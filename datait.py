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

from scipy import stats

import sqlite3

class Calc_dataframe(object):

    def __init__(self,
        file_name,
        enddate,
        sample_days,
        period_start,
        period_end):

        self.file_name = file_name
        self.enddate = enddate
        self.sample_days = sample_days + 1
        self.period_start = getTimestamp(period_start)
        self.period_end = getTimestamp(period_end)

        self.df = self.getDataFrame() #all calculation are done on this not on self.price for instance as that it is a string only given as information

        self.lastdate = self.df.index[-1][0]
        self.price = self.last('price')

        self.dayr = self.dayR()
        self.day52r = self.r52w()

    def getDataFrame(self):

        conn = sqlite3.connect("scrapData.db")

        start_date = dt.datetime.strptime(self.enddate, '%Y-%m-%d') - BDay(self.sample_days)
        start_date = start_date.strftime('%Y-%m-%d')
        start_date_str = "'" + start_date + "'"
        end_date_str = "'" + self.enddate + "'"

        df = pd.read_sql_query('''
            SELECT * FROM (
                SELECT * FROM MARKETS
                WHERE
                name = {0}
                AND date BETWEEN {1} AND {2}
                AND timestamp BETWEEN {3} AND {4}
                GROUP BY date, timestamp
                ORDER BY date(date), timestamp
                )
            GROUP BY date
            ORDER BY date(date);
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

    def func(self, func_str):
        # dispatch function from string
        func_name = func_str.split(': ')[0]
        args = func_str.split(': ')[1].split(' ')

        method = getattr(self, func_name, lambda: "nothing")

        return method(*args)

    ### :STATISTIC FUNCTION ###

    def last(self, col):
        day = self.df
        val = day[col].values[-1]

        if col in 'price open dayr yclose':
            return writePrice(val)

        elif col in 'vol oi':
            return writeVolume(val)

        return 'NaN'

    def r52w(self):
        day = self.df
        day52r = day['h52'].values[-1] - day['l52'].values[-1]
        return day52r

    def dayR(self):
        day = self.df
        self.df['dayr'] = day['dayh'] - day['dayl'] #we actually add a column to the day dataframe
        return writePrice(self.df['dayr'].values[-1], self.price)

    def change(self, start_type, prc_or_R): #start_type defines if the starting price to calculate the move of the day is yesterday 'close' price or todays 'open' price
        day = self.df
        self.df['changept'] = day['price'] - day[start_type]
        day = self.df
        if prc_or_R == 'price':
            self.df['changepc'] = day['changept'] / day[start_type]
            return writePercent(self.df['changepc'].values[-1])
        if prc_or_R == 'range':
            self.df['changepc'] = day['changept'] / self.day52r
            return writePercent(self.df['changepc'].values[-1])
        return 'NaN'

    def volR_rt(self):
        day = self.df
        # self.df['thickness'] = (day['vol'] / day['dayr'])
        try:
            self.df['thinness'] = (day['dayr'] / day['vol'])*1000000
        except:
            return '-'
        return writeVolume(self.df['thinness'].values[-1])

    def percentile(self, col):
        #here col is not string but the actual panda column
        day = self.df
        perc = stats.percentileofscore(col, col.values[-1])
        return round((perc / 100), 2)

    def stat(self, col, stat_type, absSW = None):
        #example: getStats('dayr', 'std', True)
        day = self.df

        if absSW == 'abs':
            if stat_type == 'avg':
                val = day[col].abs().mean()
            if stat_type == 'med':
                val = day[col].abs().median()
            if stat_type == 'std':
                val = day[col].abs().std()
            if stat_type == 'pct':
                val = self.percentile(day[col].abs())

        else:
            if stat_type == 'avg':
                val = day[col].mean()
            if stat_type == 'med':
                val = day[col].median()
            if stat_type == 'std':
                val = day[col].std()
            if stat_type == 'pct':
                val = self.percentile(day[col])

        if stat_type in 'pct':
            return val
        elif col in 'changept, dayr':
            return writePrice(val)
        elif col in 'changepc':
            return writePercent(val)
        elif col in 'vol, oi':
            return writeVolume(val)
        else:
            return writeNum(val)

    def getDescribe(self, col):
        day = self.df
        x = day[col].abs().describe()
        return x

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
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    today = time.strftime('%Y-%m-%d')

    calc = Calc_dataframe('ES_F',today,30,'08:00','17:10')

    print('----> ' + calc.file_name +  ' <----\n')

    print('prc chgPc =  {}'.format(calc.change('open','price')))
    print('avg "=       {}'.format(calc.stat('changepc', 'avg', 'abs')))

    print('rng chgPc =  {}'.format(calc.change('open','range')))
    print('avg "=       {}'.format(calc.stat('changepc', 'avg', 'abs')))

    print('price =      ' + calc.price)
    print('open =       {}'.format(calc.last('open')))
    print('yclose =     {}'.format(calc.last('yclose')))
    print('dayR =       {}'.format(calc.dayr))
    print('dayR_pct =   {}'.format(calc.stat('dayr', 'pct')))
    print('dayR_avg =   {}'.format(calc.stat('dayr', 'avg')))
    print('dayR_med =   {}'.format(calc.stat('dayr', 'med')))
    print('dayR_std =   {}'.format(calc.stat('dayr', 'std')))
    # print('chpt_describe = \n {}'.format(calc.getDescribe('dayr')))
    print('52r =        {}'.format(calc.day52r))

    print('VOLUME =     {}'.format(calc.last('vol')))
    print('VOLUME_avg = {}'.format(calc.stat('vol', 'avg')))
    print('VOLUME_med = {}'.format(calc.stat('vol', 'med')))
    print('VOLUME_std = {}'.format(calc.stat('vol', 'std')))
    print('Vol/rng =    {}'.format(calc.volR_rt()))
    print('Vol/rng_avg= {}'.format(calc.stat('thinness', 'avg')))

    print('\ndispatch =   {}'.format(calc.func('stat: changepc avg abs')))
    print('dispatch =   {}'.format(calc.func('last: yclose')))

    print(calc.df)
