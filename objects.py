#==================================================
#Objects File
#Purpose:
#To contain the class objects in use in stockbot
#-Stock
#-Options (child of Stock)
#-Contract
#-Combo
#More notes available above each object in the file
#
#05/31/20
#-Carson Case
#===================================================
#INCLUDES:
import yfinance as yf
import numpy
import math
import statistics
import datetime
import config

#Stock
#Purpose:
#To hold all the data for a particular ticker including historical data

class Stock:
    #Constructor
    def __init__(self,ticker=config.default_TKR,time=config.default_start_date):
        self.TKR = ticker
        self.start_date = time
        self.update()

    #Update information with data from yfinance
    def update(self):
        #basic data
        self.yfObject = yf.Ticker(self.TKR)
        self.info = self.yfObject.info
        #price data
        self.bid = self.info["bid"]
        self.ask = self.info["ask"]
        self.spread = self.ask-self.bid
        #volume
        self.volume = self.info["volume"]
        #Historical Data
        self.history = yf.download(self.TKR,self.start_date)
        #Mean and SD from historical data
        self.mean,self.sd = self.weighted_avg_and_sd()

    #Return the daily price change for a particular index in the history dataframe
    def percent_change(self,i):
        Open = self.history["Open"][i]
        Close = self.history["Close"][i]
        return((Close-Open)/Close)
    
    #Returns the weighted average and sd of the daily percentage change historically. Copied a bit from stack overflow...
    def weighted_avg_and_sd(self):
        #get values
        values = []
        for i in range(0,len(self.history)):
            values.append(self.percent_change(i))
        #create weights
        weights = []
        for i in range(0,len(values)):
            weights.append(pow((i+1),config.Xfactor))
        """
        Return the weighted average and standard deviation.

        values, weights -- Numpy ndarrays with the same shape.
        """
        average = numpy.average(values, weights=weights)
        # Fast and numerically precise:
        variance = numpy.average((values-average)**2, weights=weights)
        return (average, math.sqrt(variance))

    #obvious
    def printInfo(self):
        print(self.info)
    #FINALNOTE: More is going to be added certainly. However, this is all we need for now


#Options
#Purpose:
#To hold all the options data for a stock. The option chain, as well as determine valid options and a list of filtered valid options
class Options(Stock):
    #updates the list of all options
    #======================================================================
    #MUST BE CALLED BEFORE update_valid_options IF YOU WANT TO SET EXP DATE
    #======================================================================
    def update_options(self,exp_date=config.default_exp_date):
        #Whenever you update, update from top down
        self.update()

        self.exp_date = exp_date
        self.option_chain = self.yfObject.option_chain(self.exp_date)
        self.calls = self.option_chain.calls
        self.puts = self.option_chain.puts
    #A quick note about valid calls
    #valid_calls is a list of indexes for valid calls in the call object. Saves some memory and complexity that way
    #A follow up note. Nevermind. We are going to create a contract object and make this an array of those contracts
    def update_valid_options(self):
        #gotta update above first
        self.update_options()

        self.valid_calls = []
        self.valid_puts = []
        #This is super wet code. Shhh don't tell anyone. It's before lunch and I am hungry
        #CALLS
        for i in range(len(self.calls.index)):
            bid = self.calls.at[i,"bid"]
            ask = self.calls.at[i,"ask"]
            if(self.__is_spread_valid(bid,ask)):
                c = Contract(self,True,i)
                self.valid_calls.append(c)
        #PUTS
        for i in range(len(self.puts.index)):
            bid = self.puts.at[i,"bid"]
            ask = self.puts.at[i,"ask"]
            if(self.__is_spread_valid(bid,ask)):
                p = Contract(self,False,i)
                self.valid_puts.append(p)

    #print the valid options
    def print_valid(self):
        print("CALLS: ")
        for c in self.valid_calls:
            c.print()
        print("\n")
        print("PUTS: ")
        for p in self.valid_puts:
            p.print()

    #return the options dataframe for either calls or puts
    def get_data_frame(self,iscall,i):
        if(iscall):
            return self.calls.loc[i]
        else:
            return self.puts.loc[i]

    #Private Method to return if an option is valid
    def __is_spread_valid(self,bid,ask):
        if(ask==0):
            return False
        elif((ask-bid)/ask < config.default_max_spread):
            return True
        else:
            return False
            
#Contract
#Stores the information for a single option contract
class Contract:
    def __init__(self,opt,isCall = True, index=0):
        self.isCall = isCall
        self.index = index
        self.opts = opt                             #The options object contract came from
        self.data=opt.get_data_frame(isCall,index)
        self.algoScore = 0
        self.daysToExpire = (self.__str_to_date(self.opts.exp_date) - datetime.date.today()).days
        self.data = self.opts.get_data_frame(self.isCall,self.index)
        
    #Get data for prices and whatnot in regards to a combo
    def update_combo_data(self,combo_total_cost):
        #Get the required prices for underlying at expiration for profit
        if(self.isCall):
            self.reqEXP = combo_total_cost+self.data.strike
        else:
            self.reqEXP = self.data.strike - combo_total_cost
        #Get the required changes of underlying price
        self.req_changeEXP = self.reqEXP - self.opts.bid
        #Get the required percent changes in underlying price
        self.req_percentEXP = self.req_changeEXP / self.opts.bid

    #gets the zscore of the req percent change on historical data. 
    #MUST HAVE CALLED UPDATE_COMBO_DATA!!!
    def get_z_score(self, req_percent):
        return ((req_percent/self.daysToExpire)-self.opts.mean)/self.opts.sd

    #print data
    def print(self):
        print(self.data)

    #converts the "2020-01-01" date format we use to a datetime object
    def __str_to_date(self, date):
        return(datetime.date(int(date[:4]),int(date[5:7]), int(date[8:10])))

    #A lot more is going to be added here I am sure once we get to analysis
    #This is where each individual contract's calculated scores and probabilities and whatnot
    #Will be stored

#Combo
#Stores two Contracts, the bear and the bull
#Will later store important methods that calculate information like the analysis of the combos and exit conditions
class Combo:
    def __init__(self, bull, bear):
        self.bull = bull
        self.bear = bear
        #Get the cost of the contracts
        self.total_cost = self.bull.data.ask + self.bear.data.ask
        #Calculate required changes
        self.bull.update_combo_data(self.total_cost)
        self.bear.update_combo_data(self.total_cost)

    #return a nice string of data on the contract
    def serialize(self):
        return ("REQ BULL CHANGE: $"+str(self.bull.req_changeEXP)[:5]+"["+str(self.bull.req_percentEXP*100)[:5]+"%]"+"\tREQ BEAR CHANGE: $"+str(self.bear.req_changeEXP)[:5]+"["+str(self.bear.req_percentEXP*100)[:5]+"%]")

    #return probability of break even
    def BEprobability(self):
        #zscore of each
        bull_z = self.bull.get_z_score(self.bull.req_percentEXP)
        bear_z = self.bear.get_z_score(self.bear.req_percentEXP)
        #Probability
        #1- because we want probability it's greater than z score
        bull_p = 1 - statistics.NormalDist().cdf(bull_z)
        #no 1- because we want probability it's less than z score
        bear_p = statistics.NormalDist().cdf(bear_z)
        return(bull_p+bear_p)

    #probability of ten percent profit
    def ProfitProbability(self):
        #z scores:
        bull_z = self.bull.get_z_score(self.bull.req_percentEXP+(config.req_profit/self.bull.daysToExpire))
        bear_z = self.bear.get_z_score(self.bear.req_percentEXP+(config.req_profit/self.bear.daysToExpire))
        bull_p = 1- statistics.NormalDist().cdf(bull_z)
        bear_p = statistics.NormalDist().cdf(bear_z)
        return(bull_p+bear_p)
    
    #Returns odds for loss and gain in regards to probability
    def odds(self):
        loss = (1-self.BEprobability())*self.total_cost
        gain = self.ProfitProbability()*self.total_cost*(1+config.req_profit)
        return(gain,loss)
