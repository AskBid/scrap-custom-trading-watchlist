import sys
from os import listdir
from math import isnan, log10

import ast #reads array strings as array

import numpy as np
import pandas as pd

from scrapit import getDataFormat
from drawit import drawBar

def isnumber(x):
    try:
        float(x)
        return True
    except:
        return False

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

        dayDataFrame = dayDataFrame[dayDataFrame.applymap(isnumber)] #makes sure that if there is a bad recording that gets NaN in dataframe so it does not affect calculation

        return dayDataFrame

    def getPrice(self):
        day = self.dayDataFrame
        price = day['price'].values[-1]
        return writePrice(price)

    def getOpen(self):
        day = self.dayDataFrame
        open_ = day['open'].values[-1]
        return writePrice(open_, self.price)

    def getYClose(self):
        day = self.dayDataFrame
        close = day['yclose'].values[-1]
        return writePrice(close, self.price)

    def drawBar(self, path, width):
        day = self.dayDataFrame
        low52 = day['52l'].values[-1]
        drawBar(width,
                low52,
                self.day52r,
                day['open'].values[-1],
                day['dayr'].values[-1],
                path)
        return '{} bar has been drawn'.format(path)

    def get52wR(self):
        day = self.dayDataFrame
        day52r = day['52h'].values[-1] - day['52l'].values[-1]
        return day52r

    def getDayR(self):
        day = self.dayDataFrame
        self.dayDataFrame['dayr'] = day['dayh'] - day['dayl'] #we actually add a column to the day dataframe
        return writePrice(self.dayDataFrame['dayr'].values[-1], self.price)

    def getDayR_avg(self):
        day = self.dayDataFrame
        dayr_avg = day['dayr'].sum() / day['dayr'].dropna(axis=0).size
        return writePrice(dayr_avg, self.price)

    def getPerChange(self, start_type, prc_or_R): #start_type defines if the starting price to calculate the move of the day is yesterday 'close' price or todays 'open' price
        day = self.dayDataFrame
        self.dayDataFrame['delta'] = day['price'] - day[start_type]
        day = self.dayDataFrame
        if prc_or_R == 'price':
            self.dayDataFrame['change'] = day['delta'] / day[start_type]
            return writePercent(self.dayDataFrame['change'].values[-1])
        if prc_or_R == 'range':
            self.dayDataFrame['change'] = day['delta'] / self.day52r
            return writePercent(self.dayDataFrame['change'].values[-1])
        return '-err'

    def getPerChange_avg(self):
        day = self.dayDataFrame
        dayr_avg = day['change'].sum() / day['change'].dropna(axis=0).size
        return writePercent(dayr_avg)

    def getVolume(self):
        day = self.dayDataFrame
        vol = day['vol'].values[-1]
        return writeVolume(vol)

    def getVolume_avg(self):
        day = self.dayDataFrame
        try:
            vol_avg = day['vol'].sum() / day['vol'].dropna(axis=0).size
        except:
            return '-'
        return writeVolume(vol_avg)

    def getVolR_rt(self):
        day = self.dayDataFrame
        # self.dayDataFrame['thickness'] = (day['vol'] / day['dayr'])
        try:
            self.dayDataFrame['thinness'] = (day['dayr'] / day['vol'])*1000000
        except:
            return '-'
        return writeVolume(self.dayDataFrame['thinness'].values[-1])

    def getVolR_rt_avg(self):
        day = self.dayDataFrame
        try:
            VolR_rt_avg = day['thinness'].sum() / day['thinness'].dropna(axis=0).size
        except:
            return '-'
        return writeVolume(VolR_rt_avg)

def writePrice(num, price = None):
    if num == '-' or isnan(num):
        return '-'

    if price == None:
        price = str(num).split('.')
    else:
        price = price.split('.')

    if len(price) == 1:
        num = round(num)
        return ("{:,}".format(num).replace(' ',''))
    if len(price[0].replace(' ','')) == 1:
        return ("{:20,.4f}".format(num).replace(' ',''))
    return ("{:20,.2f}".format(num)).replace(' ','')

def writePercent(num):
    if num == '-':
        return '-'
    string = str(num).split('.')
    # if string[1].count('0') > 1:
    return ("{:.2%}".format(num))
    # return ("{:.1%}".format(num))

def writeVolume(num):
    i_offset = 15 # change this if you extend the symbols!!! (you copied this code)
    prec = 3
    fmt = '.{p}g'.format(p=prec)
    symbols = ['Y', 'T', 'G', 'M', 'k', '', 'm', 'u', 'n']

    if num == '-' or isnan(num):
        return '-'

    e = log10(abs(num))
    if e >= i_offset + 3:
        return '{:{fmt}}'.format(num, fmt=fmt)
    for i, sym in enumerate(symbols):
        e_thresh = i_offset - 3 * i
        if e >= e_thresh:
            return '{:{fmt}}{sym}'.format(num/10.**e_thresh, fmt=fmt, sym=sym)
    return '{:{fmt}}'.format(num, fmt=fmt)

def writeNum(num):
    if num == '-' or isnan(num):
        return '-'
    string = str(num)
    if len(string[0]) > 1:
        return ("{:20,.0f}".format(num)).replace(' ','')
    return ("{:20,.2f}".format(num)).replace(' ','')

if __name__ == '__main__':
    calc = Calc_dataframe('DAX.F',0)
    print('prc chgPc =  {}'.format(calc.getPerChange('open','price')))
    print('avg "=       {}'.format(calc.getPerChange_avg()))

    print('rng chgPc =  {}'.format(calc.getPerChange('open','range')))
    print('avg "=       {}'.format(calc.getPerChange_avg()))

    print('price =      ' + calc.price)
    print('open =       {}'.format(calc.getOpen()))
    print('yclose =     {}'.format(calc.getYClose()))
    print('dayR =       {}'.format(calc.dayr))
    print('dayR_avg =   {}'.format(calc.getDayR_avg()))
    print('52r =        {}'.format(calc.day52r))

    print('VOLUME =     {}'.format(calc.getVolume()))
    print('VOLUME AVG = {}'.format(calc.getVolume_avg()))
    print('Vol/rng =    {}'.format(calc.getVolR_rt()))
    print('Vol/rng =    {}'.format(calc.getVolR_rt_avg()))

    print(calc.dayDataFrame)
