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
import datetime

#**************************
#FUNCTIONS (moved most to objects)
#**************************

#A neat idea. But I don't think I will use it. Not sure if I will later. Seems like I can just use the probability
#to find probability of decrease
#Preforms the Crash Analysis
'''
def crash_analysis(obj):
    obj.update_options()
    opt_len = (str_to_date(obj.exp_date) - datetime.date.today()).days      #time to expiration
    crash_count = 0
    period_count = 0
    average_severity = 0
    for i in range(0,len(obj.history),opt_len):
        total_change = 0
        # I'm not going to round or whatever. At least not now. Just cut off the last few days that don't fit within the itteration
        if(i+opt_len > len(obj.history)):
            break
        for j in range(i,i+opt_len):
            total_change += obj.percent_change(j)
        #crash is defined as a total decrease over the period of time that our option lasts in history
        if total_change < 0:
            crash_count+=1
            average_severity += total_change
        period_count += 1
    return(crash_count,period_count,average_severity/crash_count)
    '''

#**************************
#END OF FUNCTIONS
#**************************
'''
bull = objects.Options(config.bull)
bear = objects.Options(config.bear)

#Percent daily change for bear and bull

#Mean and SD are respectivly stored in a tuple:
bull_daily_growth = bull.weighted_avg_and_sd()
bear_daily_growth = bear.weighted_avg_and_sd()            

#PRINT STUFF
print("BULL DAILY GROWTH(MEAN,SD): "+str(bull_daily_growth))
print("BEAR DAILY GROWTH(MEAN,SD): "+str(bear_daily_growth))
'''