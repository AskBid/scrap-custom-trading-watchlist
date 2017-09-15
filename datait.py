import sys
from os import listdir

import ast #reads array strings as array

import numpy as np
import pandas as pd

from scrapit import getDataFormat

def writePrice(digit):
    if digit == '-':
        return '-'

    string = str(digit).split('.')

    if len(string) == 1:
        return ("{:,}".format(digit))
    if len(string[0]) == 1:
        return ("{:20,.4f}".format(digit))
    # round(digit[1], 2)

    return ("{:20,.2f}".format(digit))

def writeRange(digit):

    return ("{:20,.2f}".format(digit))

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

        #make panda DataFrames
        labelCol = list(getDataFormat().keys())
        labelCol.pop(0)
        labelCol.pop(-1)

        labelRows = []

        #from list of list with strings to list of lists with float,int
        newlinelist = []

        for line in linelist:
            newline = []
            labelRows.append(line[0].split(' ')[0]) #modify here to decide how the rows label (date) format is
            for i in range(1,10):
                try:
                    if '.' in line[i]:
                        newline.append(float(line[i]))
                    else:
                        newline.append(int(line[i]))
                except:
                    newline.append('-')
            newlinelist.append(newline)

        dayslist = pd.DataFrame(newlinelist, index = labelRows, columns = labelCol)

        return dayslist



    def getPrice(self):
        day = self.dayslist
        price = day['price'].values[-1]
        return writePrice(price)

    def getOpen(self):
        day = self.dayslist
        open_ = day['open'].values[-1]
        return writePrice(open_)

    def getYClose(self):
        day = self.dayslist
        close = day['yclose'].values[-1]
        return writePrice(close)

    def getDayR(self):
        day = self.dayslist
        dayR = day['dayh'].values[-1] - day['dayl'].values[-1]
        return writeRange(dayR)

    def getDayR_avg(self):
        day = self.dayslist
        print(day['dayh'])
        print(day['dayl'])
        dayR_series = day['dayh'] - day['dayl']
        return writeRange(dayR_series.sum() / dayR_series.size)


if __name__ == '__main__':
    calc= Calc_Vals('SPY.i')
    print(calc.dayslist)
    print('price = ' + calc.getPrice())
    print('open = ' + calc.getOpen())
    print('yclose = ' + calc.getYClose())
    print('dayR = ' + calc.getDayR())
    print(calc.getDayR_avg())


# def getDataFormat():
#     dataFormat = {
#         "Date": "",
#         "Price": "",
#         "yClose": "",
#         "Open": "",
#         "DayH": "",
#         "DayL": "",
#         "52H": "",
#         "52L": "",
#         "Vol": "",
#         "Oi": "",
#         "Ticker": ""}

# ['2017-09-08 16:30 Fri', '2461.00', '2461.00', '2464.75', '2465.75', '2455.25', '2486.25', '2061.00', '1500000', '719665', 'ESZ7']
# "Date": "0",              Price 1    Close 2    Open 3     DayH 4     DayL 5     52H 6      52L 7      Volume 8  OpenInt 9  Ticker 10
