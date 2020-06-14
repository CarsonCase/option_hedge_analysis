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
    #Eventually replace this with a KERNAL DENSITY FUNCTION. God that is a terrifying thought
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
            if(self.__is_spread_valid(bid,ask) and self.__is_volume_valid(self.calls.at[i,"volume"])):
                c = Contract(self,True,i)
                self.valid_calls.append(c)
        #PUTS
        for i in range(len(self.puts.index)):
            bid = self.puts.at[i,"bid"]
            ask = self.puts.at[i,"ask"]
            if(self.__is_spread_valid(bid,ask) and self.__is_volume_valid(self.puts.at[i,"volume"])):
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

    #Private Method to return if an option is valid based on spread
    def __is_spread_valid(self,bid,ask):
        if(ask==0):
            return False
        elif((ask-bid)/ask < config.default_max_spread):
            return True
        else:
            return False

    def __is_volume_valid(self,volume):
        if(volume >= config.default_min_volume):
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

    #Converts a zscore to the actual value of price at expire that coresponds to that z score
    def get_est_price(self,z):
        x = self.daysToExpire*(z*self.opts.sd + self.opts.mean)
        return (x+1)*self.opts.bid

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
        #get odds (saved because we use a lot I think)
        self.odds = self.getOdds()
        #Exit Condiutions. May change over time to be more dynamic for each trade
        self.exit_max = config.req_profit
        self.exit_bail =- config.bail_price

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
        return(bull_p, bear_p)
    
    #Returns odds for loss and gain in regards to probability
    def getOdds(self):
        #NOTE: This assumes that they mirror one another. And therefore must carry one another. This does not account for probability that
        #one stock goes down and the other goes up. That is fairly rare and when it happens does not happen consistently to a very large degree.
        #HOPEFULLY this means that is statistically insignificant. Man I am a terrible statistican
        bull_z = self.bull.get_z_score(self.bull.req_percentEXP)
        bear_z = self.bear.get_z_score(self.bear.req_percentEXP)
        #print(str(bull_z)+":"+str(bear_z))
        loss = (statistics.NormalDist().cdf(bull_z) * self.bull.data.ask) + ((1-statistics.NormalDist().cdf(bear_z))*self.bear.data.ask)
        gain = 0

        #Get an array of z scores to interpret for bull
        bull_zs = numpy.linspace(bull_z,config.max_z_score,config.z_score_iterations)
        #And edit gain odds as the probability of a z score * the profit it would give

        for i in range(0,len(bull_zs)-1):
            p = bull_zs[i]
            profit = self.bull.get_est_price(p) - (self.bull.data.strike + self.total_cost)
            P = (1-statistics.NormalDist().cdf(p)) - (1-statistics.NormalDist().cdf(bull_zs[i+1]))
            gain += profit*P

        #Do the same for bear (I know this is wet. Ah well. I can fix it later if I want)
        bear_zs = numpy.linspace(bear_z,config.max_z_score*-1,config.z_score_iterations)

        for i in range(0,len(bear_zs)-1):
            p=bear_zs[i]
            profit = self.bear.data.strike - (self.bear.get_est_price(p) + self.total_cost)
            P = statistics.NormalDist().cdf(p) - statistics.NormalDist().cdf(bear_zs[i+1])
            gain += profit * P
            
        return(gain,loss)

    #Returns true if odds are positive and false if not
    def isValid(self):
        if self.odds[0]>self.odds[1]:
            return True
        else: 
            return False 
