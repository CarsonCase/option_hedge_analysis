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
    def update_options(self,exp_date=config.default_exp_date):
        self.option_chain = self.yfObject.option_chain(exp_date)
        self.calls = self.option_chain.calls
        self.puts = self.option_chain.puts
    #A quick note about valid calls
    #valid_calls is a list of indexes for valid calls in the call object. Saves some memory and complexity that way
    #A follow up note. Nevermind. We are going to create a contract object and make this an array of those contracts
    def update_valid_options(self):
        self.valid_calls = []
        self.valid_puts = []
        #This is super wet code. Shhh don't tell anyone. It's before lunch and I am hungry
        for i in range(len(self.calls.index)):
            bid = self.calls.at[i,"bid"]
            ask = self.calls.at[i,"ask"]
            if(self.__is_spread_valid(bid,ask)):
                c = Contract(self.calls.loc[i])
                self.valid_calls.append(c)
        for i in range(len(self.puts.index)):
            bid = self.puts.at[i,"bid"]
            ask = self.puts.at[i,"ask"]
            if(self.__is_spread_valid(bid,ask)):
                p = Contract(self.puts.loc[i])
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

    #Private Method to return if an option is valid
    def __is_spread_valid(self,bid,ask):
        if((ask-bid)/ask < config.default_max_spread):
            print((ask-bid)/ask)
            return True
        else:
            return False
            
#Contract
#Stores the information for a single option contract
class Contract:
    def __init__(self,dataFrame):
        self.data=dataFrame
        self.algoScore = 0

    def print(self):
        print(self.data)

    #A lot more is going to be added here I am sure once we get to analysis
    #This is where each individual contract's calculated scores and probabilities and whatnot
    #Will be stored