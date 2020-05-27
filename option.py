#a class for an option object

class option:
    # call is a bool for if it is a call or a put
    counter = 0
    def __init__(self, call, strike, price, volume):
        self.price = price  
        self.volume = volume
        self.strike = strike
        self.call = call
        self.id = self.__class__.counter
        self.__class__.counter += 1
    def print(self):
        if(self.call):
            print("Type: Call")
        else:
            print("Type: Put")
        print("Strike: "+str(self.strike)+" Price: "+str(self.price)+" Volume: "+str(self.volume)+" ID: "+str(self.id))