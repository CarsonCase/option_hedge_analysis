#Values used in ojects.py
#Values used in Stocks Object
default_TKR = "SPY"
default_start_date = "2000-01-01"
#Values used in Options Object
default_exp_date = "2020-06-25"
default_max_spread = .15
default_min_volume = 10
#Values for stocks being evaluated
    #this will eventually be replaced by the develop combos module
bull = "HD"
bear = "LOW"
#Values used in predict Stock Change Module
Xfactor = 1.5             #n^x    for weighted time average
#Exit conditions
req_profit = .1
bail_price = -.1
#Values used in the statistical analysis of odds. If you can call it that
max_z_score = 6
z_score_iterations = 10000
