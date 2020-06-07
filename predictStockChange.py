#===============================================================================
#Predict Stock Change Module
#Purpose:
#To analize historical data and get a statistically reasonable prediction
#for the stock change.
#Also find the probability of a crash and how bad a crash is on average when it happens
#
#06-07-20
#-Carson Case
#===============================================================================

import objects
import config
import math
import numpy

#**************************
#FUNCTIONS
#**************************

# I stole this from stack overflow....
def weighted_avg_and_sd(values, x):
    #create weights
    weights = []
    for i in range(0,len(values)):
        weights.append(pow((i+1),x))
    """
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    """
    average = numpy.average(values, weights=weights)
    # Fast and numerically precise:
    variance = numpy.average((values-average)**2, weights=weights)
    return (average, math.sqrt(variance))

#Fills the bull and bear data lists
def fill_daily_percent_change(obj, arr):
    for i in range(0,len(obj.history)):
        Open = obj.history["Open"][i]
        Close = obj.history["Close"][i]
        arr.append((Close-Open)/Close) 

#**************************
#END OF FUNCTIONS
#**************************
bull = objects.Stock(config.bull)
bear = objects.Stock(config.bear)

#Percent daily change for bear and bull
bullData = []
bearData = []
fill_daily_percent_change(bull,bullData)
fill_daily_percent_change(bear,bearData)

#Mean and SD are respectivly stored in a tuple:
bull_daily_growth = weighted_avg_and_sd(bullData,config.Xfactor)
bear_daily_growth = weighted_avg_and_sd(bearData,config.Xfactor)

print("BULL DAILY GROWTH(MEAN,SD): "+str(bull_daily_growth))
print("BEAR DAILY GROWTH(MEAN,SD): "+str(bear_daily_growth))

#Crash Analysis:
#Define a crash as -> total decrease over a period of half the option length
#if this happens define it as a crash and create crash object (also keep track of the number of x day periods. X being half option length)
#For each crash find total percent decrease in the crash and note it's time score so we cand use the same weighted average here
#Finaly find the weighted probabilty of a crash and what the average/sd is of the crash percent change
#later use those values to find if our insurance put on the bear is likely to be useful and how much risk it mitigates

#FOR LATER
#The probability of profit as of right now would be the probability bull grows to req_bull_growth + probability of bear crash to insurance
#This relies on exit strategy of break even only for contracts at expire which is default right now. This will eventually change to a dynamic value.