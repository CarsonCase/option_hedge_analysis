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
    def __init__(self,opt=Options(),isCall = True, index=0):
        self.isCall = isCall
        self.index = index
        self.opts = opt                             #The options object contract came from
        self.data=opt.get_data_frame(isCall,index)
        self.algoScore = 0

    # needs to update all its underlying data then get a new dataframe
    def update(self):
        self.opts.update_valid_options()
        self.data = self.opts.get_data_frame(self.isCall,self.index)

    def print(self):
        print(self.data)

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
    def update(self):
        #Get the strike prices
        self.bull_strike = self.bull.data.strike
        self.bear_strike = self.bear.data.strike
        #Get the cost of the contracts
        self.bull_cost = self.bull.data.ask
        self.bear_cost = self.bear.data.ask
        self.total_cost = self.bull_cost + self.bear_cost
        #Get the required prices for underlying at expiration for profit
        self.req_bullEXP = self.total_cost + self.bull_strike
        self.req_bearEXP = self.bear_strike - self.total_cost
        #Get the required changes of underlying price
        self.req_bull_changeEXP = self.req_bullEXP - self.bull.opts.bid
        self.req_bear_changeEXP = self.req_bearEXP - self.bear.opts.bid          #Should be negative

    def print_req_change(self):
        print(self.bull.opts.bid)
        print("REQ BULL CHANGE: "+str(self.req_bull_changeEXP)+"\tREQ BEAR CHANGE: "+str(self.req_bear_changeEXP))

#This will be removed
#It was used for debugging but will also be the basis for the combo analysis module that comes next!
'''
hd = Options("HD")
low = Options("LOW")

hd.update_valid_options()
low.update_valid_options()
for i,bull in enumerate(low.valid_calls):
    for j,bear in enumerate(hd.valid_puts):
        c = Combo(bull,bear)
        c.update()
        print(str(i)+","+str(j))
        c.print_req_change()

'''




