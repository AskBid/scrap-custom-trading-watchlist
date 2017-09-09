import sys
from os import listdir
import ast

class Calc_Vals():

    def __init__(self, file_name):

        self.file_name = file_name + '.csv'
        self.linelist = []

        #from list of strings to list of lists
        with open('data/data_20-22/{}'.format(self.file_name)) as f:
    	    self.linelist = f.readlines()
        for i,day in enumerate(self.linelist):
            self.linelist[i] = ast.literal_eval(day)

        self.price = self.getLastPrc()
        self.open = self.getOpenPrc()

    def getLastPrc(self):
        last_day = self.linelist[-1]

        return last_day[1]

    def getOpenPrc(self):
        last_day = self.linelist[-1]

        return last_day[3]



if __name__ == '__main__':
    calc= Calc_Vals('USDCHF.S')

#
# "Date": "0",
# "Price": "1",
# "Close": "2",
# "Open": "3",
# "DayH": "4",
# "DayL": "5",
# "52H": "6",
# "52L": "7",
# "Volume": "8",
# "OpenInterest": "9",
# "Ticker": "10",
