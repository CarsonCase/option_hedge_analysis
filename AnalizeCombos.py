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

hd = objects.Options(config.bear)
low = objects.Options(config.bull)

hd.update_valid_options()
low.update_valid_options()
for i,bull in enumerate(low.valid_calls):
    for j,bear in enumerate(hd.valid_puts):
        c = objects.Combo(bull,bear)
        c.update()
        print(c.serialize())

