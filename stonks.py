import yfinance as yf
import sys
from option import option
import config
#========================FUNCTIONS==============================

def makeList(is_call, option_list, min_volume):
    valid_list = []
    for i in option_list.index:
        if(option_list.at[i,"volume"] > min_volume):
            o = option(is_call, option_list.at[i,"strike"], option_list.at[i,"lastPrice"], option_list.at[i,"volume"])
            valid_list.append(o)
    return valid_list

def print_options(option_list, name, is_call):
    if(is_call):
        print("Valid %s Calls"% name)
    else:
        print("Valid %s Puts"% name)
    for o in option_list:
        print("strike: %s\tPrice: %s"% (o.strike, o.price))

def getOptionById(id, call_list, put_list):
    for c in call_list:
        if(c.id == int(id)):
            c.print()
    for p in put_list:
        if(p.id == int(id)):
            p.print()
#========================END FUNCTIONS==========================
def main(argv):

    #Get the lists as pandas dataFrames
    BULL = yf.Ticker(config.bull)                
    BEAR = yf.Ticker(config.bear)
    call_list = BULL.option_chain(config.date).calls
    put_list = BEAR.option_chain(config.date).puts

    #calculate some variables
    bull_price = BULL.info["dayLow"]
    bear_price = BEAR.info["dayLow"]


    #option_lists for the options we will look at
    valid_calls = makeList(config.calls, call_list, config.min_volume)
    valid_puts = makeList(config.puts, put_list, config.min_volume)


    #print data here for debugging and all that
    #print("%s PRICE: %f" %(bull,bull_price))
    #print("%s PRICE: %f" %(bear,bear_price))
    #print_options(valid_calls,bull,calls)
    #print_options(valid_puts, bear, puts)

    #build csv
    fp = open(config.output_file,"a")

    #loop through each of each so analize each combination
    for i,vc in enumerate(valid_calls):
        did_write = False
        for j,vp in enumerate(valid_puts):
            #calculations...
            total_cost = vc.price+vp.price
            req_change_in_bull_price = (total_cost + vc.strike)-bull_price
            req_change_in_bear_price = (vp.strike - total_cost)-bear_price
            #add to csv
            if(req_change_in_bull_price<=config.desired_climb and req_change_in_bear_price >= config.desired_insurance):
                fp.write(str(req_change_in_bull_price)[:5]+"["+str(req_change_in_bear_price)[:5]+"]+("+str(vc.id)+"/"+str(vp.id)+"),")
                did_write=True
        if(did_write):
            fp.write("\n")
    fp.close()
    print("Output in "+config.output_file)
    while(True):
        userIn = input("Enter the Id of an option you'd like to know more about. If you wish to end the program press CTRL-C\n")
        getOptionById(userIn, valid_calls, valid_puts)
if __name__ == "__main__":
   main(sys.argv[1:])