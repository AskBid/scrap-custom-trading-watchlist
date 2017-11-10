import sys
from os import listdir
from math import isnan, log10
import ast #reads array strings as array

import numpy as np
import pandas as pd

import time
import datetime as dt
from pandas.tseries.offsets import BDay #to make operation betwen dates where only BusinessDays are considered

from scrapit import getTimestamp
from drawit import draw52RangeBar

import sqlite3

class Calc_dataframe():

    def __init__(self,
        file_name,
        enddate,
        sample_days,
        period_start,
        period_end):

        self.file_name = file_name
        self.enddate = enddate
        self.sample_days = sample_days
        self.period_start = getTimestamp(period_start)
        self.period_end = getTimestamp(period_end)

        self.dayDataFrame = self.getDataFrame() #all calculation are done on this not on self.price for instance as that it is a string only given as information

        self.lastdate = self.dayDataFrame.index[-1][0]
        self.price = self.getPrice()
        self.dayr = self.getDayR()
        self.dayr_std = self.getDayR_std()
        self.dayr_avg = self.getDayR_avg()
        self.day52r = self.get52wR()

    def getDataFrame(self):

        conn = sqlite3.connect("scrapData.db")

        start_date = dt.datetime.strptime(self.enddate, '%Y-%m-%d') - BDay(self.sample_days)
        start_date = start_date.strftime('%Y-%m-%d')
        start_date_str = "'" + start_date + "'"
        end_date_str = "'" + self.enddate + "'"

        df = pd.read_sql_query('''
            SELECT * FROM MARKETS
            WHERE
            name = {0}
            AND date BETWEEN {1} AND {2}
            AND timestamp BETWEEN {3} AND {4};
            '''.format(
            '"' + str(self.file_name) + '"',
            start_date_str,
            end_date_str,
            self.period_start,
            self.period_end), conn)

        df.drop('day', axis=1, inplace=True)
        df.drop('name', axis=1, inplace=True)

        df.set_index(['date', 'time'], inplace=True)

        try:
            df = df[df.applymap(isnumber)] #makes sure that if there is a bad recording that gets NaN in dataframe so it does not affect calculation
        except:
            print('''something went wrong with the DB selection in datait.py and no value where selected''')

        return df

    def drawBar2(self, path, lenght, thickness):
        day = self.dayDataFrame
        low52 = day['l52'].values[-1]
        draw52RangeBar(
                    lenght,
                    thickness,
                    low52,
                    self.day52r,
                    day['open'].values[-1],
                    day['dayr'].values[-1],
                    path)

        return '{} bar has been drawn'.format(path)

    ### :STATISTIC FUNCTION ###

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

    def get52wR(self):
        day = self.dayDataFrame
        day52r = day['h52'].values[-1] - day['l52'].values[-1]
        return day52r

    def getDayR(self):
        day = self.dayDataFrame
        self.dayDataFrame['dayr'] = day['dayh'] - day['dayl'] #we actually add a column to the day dataframe
        return writePrice(self.dayDataFrame['dayr'].values[-1], self.price)

    def getDayR_avg(self):
        day = self.dayDataFrame
        return writePrice(day['dayr'].mean())

    def getDayR_med(self):
        day = self.dayDataFrame
        return writePrice(day['dayr'].median())

    def getDayR_std(self):
        day = self.dayDataFrame
        return writePrice(day['dayr'].std())

    def get_describe(self):
        day = self.dayDataFrame
        x = day['changept'].describe()
        return x

    def getPcChange(self, start_type, prc_or_R): #start_type defines if the starting price to calculate the move of the day is yesterday 'close' price or todays 'open' price
        day = self.dayDataFrame
        self.dayDataFrame['changept'] = day['price'] - day[start_type]
        day = self.dayDataFrame
        if prc_or_R == 'price':
            self.dayDataFrame['changepc'] = day['changept'] / day[start_type]
            return writePercent(self.dayDataFrame['changepc'].values[-1])
        if prc_or_R == 'range':
            self.dayDataFrame['changepc'] = day['changept'] / self.day52r
            return writePercent(self.dayDataFrame['changepc'].values[-1])
        return '-err'

    def getPcChange_avg(self, switch_abs = None):
        if switch_abs == 'abs':
            day = self.dayDataFrame['changepc'].abs()
        else:
            day = self.dayDataFrame['changepc']
        dayr_avg = day.mean()
        return writePercent(dayr_avg)

    def getVolume(self):
        day = self.dayDataFrame
        vol = day['vol'].values[-1]
        return writeVolume(vol)

    def getVolume_avg(self):
        day = self.dayDataFrame
        return writeVolume(day['vol'].mean())

    def getVolume_med(self):
        day = self.dayDataFrame
        return writeVolume(day['vol'].median())

    def getVolume_std(self):
        day = self.dayDataFrame
        return writeVolume(day['vol'].std())

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

    ### /STATISTIC FUNCTION ###

def writePrice(num, price = None):
    if num == '-' or isnan(num):
        return 'NaN'

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
        return 'NaN'
    string = str(num).split('.')
    # if string[1].count('0') > 1:
    return ("{:.2%}".format(num))
    # return ("{:.1%}".format(num))

def writeVolume(num):
    i_offset = 15 # changepc this if you extend the symbols!!! (you copied this code)
    prec = 3
    fmt = '.{p}g'.format(p=prec)
    symbols = ['Y', 'T', 'G', 'M', 'k', '', 'm', 'u', 'n']

    if num == '-' or isnan(num):
        return 'NaN'
    if num == 0:
        return '0'

    e = log10(abs(num))
    if e >= i_offset + 3:
        return '{:{fmt}}'.format(num, fmt=fmt)
    for i, sym in enumerate(symbols):
        e_thresh = i_offset - 3 * i
        if e >= e_thresh:
            return '{:{fmt}}{sym}'.format(num/10.**e_thresh, fmt=fmt, sym=sym)
    return '{:{fmt}}'.format(num, fmt=fmt)

def isnumber(x):
    try:
        float(x)
        return True
    except:
        return False

def writeNum(num):
    if num == '-' or isnan(num):
        return 'NaN'
    string = str(num)
    if len(string[0]) > 1:
        return ("{:20,.0f}".format(num)).replace(' ','')
    return ("{:20,.2f}".format(num)).replace(' ','')

if __name__ == '__main__':
    # pd.set_option('display.height', 1000)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    today = time.strftime('%Y-%m-%d')

    calc = Calc_dataframe('ES_F',today,30,'13:00','13:10')
    print(calc.dayDataFrame)
    print('\n')

    print('----> ' + calc.file_name +  ' <----''\n')

    print('prc chgPc =  {}'.format(calc.getPcChange('open','price')))
    print('avg "=       {}'.format(calc.getPcChange_avg('abs')))

    print('rng chgPc =  {}'.format(calc.getPcChange('open','range')))
    print('avg "=       {}'.format(calc.getPcChange_avg('abs')))

    print('price =      ' + calc.price)
    print('open =       {}'.format(calc.getOpen()))
    print('yclose =     {}'.format(calc.getYClose()))
    print('dayR =       {}'.format(calc.dayr))
    print('dayR_avg =   {}'.format(calc.getDayR_avg()))
    print('dayR_med =   {}'.format(calc.getDayR_med()))
    print('dayR_std =   {}'.format(calc.getDayR_std()))
    print('chpt_describe = \n {}'.format(calc.get_describe()))
    print('52r =        {}'.format(calc.day52r))

    print('VOLUME =     {}'.format(calc.getVolume()))
    print('VOLUME AVG = {}'.format(calc.getVolume_avg()))
    print('VOLUME MED = {}'.format(calc.getVolume_med()))
    print('VOLUME STD = {}'.format(calc.getVolume_std()))
    print('Vol/rng =    {}'.format(calc.getVolR_rt()))
    print('Vol/rng AVG= {}'.format(calc.getVolR_rt_avg()))
