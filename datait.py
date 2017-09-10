import sys
from os import listdir
import ast
from scrapit import getDataFormat

def writePrice(digit):
    pass

class Calc_Vals():

    def __init__(self, file_name):

        self.file_name = file_name
        self.dayslist = self.readFile()


    def readFile(self):
        with open('data/data_16-18/{}'.format(self.file_name + '.csv')) as f:
    	    linelist = f.readlines()

        #from list of strings to list of lists
        for i,day in enumerate(linelist):
            linelist[i] = ast.literal_eval(day)

        #from list of list with strings to list of lists with float,int
        newlinelist = []
        for line in linelist:
            newline = []
            newline.append(line[0].split(' ')[0])
            for i in range(1,8):
                try:
                    newline.append(float(line[i]))
                except:
                    newline.append('-')
            try:
                newline.append(int(line[8]))
            except:
                newline.append('-')
            try:
                newline.append(int(line[9]))
            except:
                newline.append('-')
            newlinelist.append(newline)

        return newlinelist

    def getPrice(self):
        day = self.dayslist[-1]
        day = round(float(day[1]), 2)
        return ("{:20,.2f}".format(day))

    def getOpen(self):
        day = self.dayslist[-1]
        return day[3]

    def getYClose(self):
        day = self.dayslist[-1]

        return day[2]

    def getDayRange(self):
        day = self.dayslist[-1]
        dayrange = float(day[4]) - float(day[5])

        return ("{:20,.2f}".format(dayrange))



if __name__ == '__main__':
    calc= Calc_Vals('USDCHF.S')


# ['2017-09-08 16:30 Fri', '2461.00', '2461.00', '2464.75', '2465.75', '2455.25', '2486.25', '2061.00', '1500000', '719665', 'ESZ7']
# "Date": "0",              Price 1    Close 2    Open 3     DayH 4     DayL 5     52H 6      52L 7      Volume 8  OpenInt 9  Ticker 10
