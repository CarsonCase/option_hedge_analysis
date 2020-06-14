#=====================================================================================
#Analize Combos Module
#Purpose:
#To use the Options object to generate a series of valid options,
#then use the Combo object's functions to analize each combo for req change and percent change.
#This will probably be revisited later once we predict stock change. Then an algo score can be given to each of the combos
#in relation to it's probability to be profitable. Then we can sort combos by that algo score. (Find profit probability module)
#
#NOTE: I would like to include PEGratio as well as ROIC but yfinance doesn't really support these things very well
#.info["pegRatio"] is not exactly accurate(HD was double what it really is) and ROIC is just impossible without modifying a base.py
#Maybe fix these later when tweaking the algorithm. For now it's a little detail that seems less than necessary
#
#06-07-20
#-Carson Case
#=====================================================================================
import objects
import config
import predictStockChange as psc 

def printCombo(c):
    print("========================TRADE====================")
    print(c.serialize())
    print("PROBABILITY: "+str(c.BEprobability()))
    print("ODDS(gain,loss): "+str(c.odds))
    print("************************BULL************************")
    c.bull.print()
    print("************************BEAR************************")
    c.bear.print()

def oddsDifference(c):
    o = c.odds
    return o[0]-o[1]

def getBestTrade(bullTKR, bearTKR):
    #Get the stocks we're evaluating
    bull = objects.Options(bullTKR)
    bear = objects.Options(bearTKR)

    bull.update_valid_options()
    bear.update_valid_options()

    #add relevant stocks to an array of combos
    relevantCombos = []

    for i,bullC in enumerate(bull.valid_calls):
        for j,bearC in enumerate(bear.valid_puts):
            c = objects.Combo(bullC,bearC)
            if(c.isValid()):
                relevantCombos.append(c)

    #sort options by odds
    relevantCombos.sort(reverse=True, key=oddsDifference)

    return(relevantCombos[0])

printCombo(getBestTrade("HD","LOW"))
printCombo(getBestTrade("LOW","HD"))

