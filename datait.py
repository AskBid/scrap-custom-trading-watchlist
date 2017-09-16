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
    return ("{:20,.2f}".format(digit)).replace(' ','')

def writePer(digit):
    if digit == '-':
        return '-'
    string = str(digit).split('.')
    if string[1].count('0') > 1:
        return ("{:.3%}".format(digit))
    return ("{:.1%}".format(digit))


class Calc_dataframe():

    def __init__(self, file_name, date_offset):

        self.file_name = file_name
        self.date_offset = date_offset
        self.dayDataFrame = self.readFile() #all calculation are done on this not on self.price for instance as that it is a string only given as information
        self.price = self.getPrice()
        self.dayr = self.getDayR()
        self.day52r = self.get52wR()

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

        x = self.date_offset

        if x == 0:
            dayDataFrame = pd.DataFrame(newlinelist, index = labelRows, columns = labelCol)
        else:
            dayDataFrame = pd.DataFrame(newlinelist[:-x], index = labelRows[:-x], columns = labelCol)


        return dayDataFrame

    def getPrice(self):
        day = self.dayDataFrame
        price = day['price'][-1]
        return writePrice(price)

    def getOpen(self):
        day = self.dayDataFrame
        open_ = day['open'][-1]
        return self.writeVal(open_)

    def getYClose(self):
        day = self.dayDataFrame
        close = day['yclose'][-1]
        return self.writeVal(close)

    def get52wR(self):
        day = self.dayDataFrame
        day52r = day['52h'][-1] - day['52l'][-1]
        return day52r

    def getDayR(self):
        day = self.dayDataFrame
        self.dayDataFrame['dayr'] = day['dayh'] - day['dayl'] #we actually add a column to the day dataframe
        return self.writeVal(self.dayDataFrame['dayr'][-1])

    def getDayR_avg(self):
        day = self.dayDataFrame
        dayr_avg = day['dayr'].sum() / day['dayr'].size
        return self.writeVal(dayr_avg)

    def getPerChange(self, start_type, prc_or_R): #start_type defines if the starting price to calculate the move of the day is yesterday 'close' price or todays 'open' price
        day = self.dayDataFrame
        self.dayDataFrame['delta'] = day['price'] - day[start_type]
        day = self.dayDataFrame
        if prc_or_R == 'price':
            self.dayDataFrame['change'] = day['delta'] / day[start_type]
            return writePer(self.dayDataFrame['change'][-1])
        if prc_or_R == '52r':
            self.dayDataFrame['change'] = day['delta'] / self.day52r
            return writePer(self.dayDataFrame['change'][-1])
        return '-err'

    def writeVal(self, digit):
        if digit == '-':
            return '-'
        price = self.price.split('.')
        if len(price) == 1:
            digit = round(digit)
            return ("{:,}".format(digit))
        if len(price[0]) == 1:
            return ("{:20,.4f}".format(digit))
        return ("{:20,.2f}".format(digit)).replace(' ','')


if __name__ == '__main__':
    calc= Calc_dataframe('RUSSEL.i', 3)
    calc.getPerChange('open','price')
    print(calc.dayDataFrame)
    calc.getPerChange('open','52r')
    print(calc.dayDataFrame)
    print('price = ' + calc.price)
    print('open = {}'.format(calc.getOpen()))
    print('yclose = {}'.format(calc.getYClose()))
    print('dayR = {}'.format(calc.dayr))
    print('52r = {}'.format(calc.day52r))
    print('dayR_avg = {}'.format(calc.getDayR_avg()))
