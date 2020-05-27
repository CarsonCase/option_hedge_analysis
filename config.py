#bools for readability. Please don't change this unless you want to cause problems
calls = True
puts = False


date = "2020-06-04"             #Date of options expiration
bull = "LOW"                    #Ticker Symbol of predicted bullish Stock
bear = "HD"                     #Ticker Symbol of predicted bearish Stock
min_volume = 30                #Minumum volume of options we're willing to buy   
desired_insurance = -10        #a max of -$ needed to profit off of hedged put (Make negative as the puts require a decrease in value to proffit)
desired_climb = 10              #a min # of $ needed to profit off of call 
output_file = "output.csv"      #output file. Must be of type csv. Open with a spreadsheet editor