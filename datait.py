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
        self.sample_days = sample_days - 1
        self.period_start = getTimestamp(period_start)
        self.period_end = getTimestamp(period_end)

        self.df = self.getDataFrame() #all calculation are done on this not on self.price for instance as that it is a string only given as information

        self.lastdate = self.df.index[-1][0]
        self.lasthour = self.df.index[-1][1]
        self.daysAmount = len(self.df.index)
        self.price = writePrice(self.df['price'][-1])

        self.dayr = self.dayR()
        self.day52r = self.r52w()

    def getDataFrame(self, path = "scrapData.db"):

        conn = sqlite3.connect(path)

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

        # try:
        df = df[df.applymap(isnumber)] #makes sure that if there is a bad recording that gets NaN in dataframe so it does not affect calculation
        # except:
        #     print('''something went wrong with the DB selection in datait.py and no value where selected''')

        return df

    def func(self, func_str):
        # dispatch function from string
        func_name = func_str.split(': ')[0]
        args = func_str.split(': ')[1].split(' ')

        method = getattr(self, func_name, lambda: "nothing")

        return method(*args)

    def color(self):
        color = '0'

        #first index positive, second index negative
        # pct_0 = 'rgba(0.9961, 1.0000, 0.2941,'
        # pct_1 = ('rgba(0.9412, 1.0000, 0.2863,', 'rgba(1.0000, 0.9529, 0.2941,')
        # pct_2 = ('rgba(0.7373, 0.9098, 0.1412,', 'rgba(1.0000, 0.3961, 0.1608,')
        # pct_3 = ('rgba(0.3176, 0.7412, 0.2118,', 'rgba(1.0000, 0.7490, 0.1529,')
        # pct_4 = ('rgba(0.1451, 0.5451, 0.2471,', 'rgba(20.1529, 0.1765, 0.0902,')
        # pct_5 = ('rgba(0, 1.0000, 0.9176,', 'rgba(0.9176, 0, 1.0000,')
        pct_0 = 'rgba(254, 255, 75'
        pct_1 = ('rgba(240, 255, 73', 'rgba(255, 243, 75')
        pct_2 = ('rgba(188, 232, 36', 'rgba(255, 101, 41')
        pct_3 = ('rgba(81, 189, 54', 'rgba(255, 191, 39')
        pct_4 = ('rgba(37, 139, 63', 'rgba(239, 45, 23')
        pct_5 = ('rgba(18, 219, 202', 'rgba(223, 95, 234')

        i = 0
        if self.df['changept'].values[-1] < 0:
            i = 1

        pc = self.percentage('changept')

        if pc <= 0.01:
            color = pct_0
        elif pc <= 0.1:
            color = pct_1[i]
        elif pc <= 0.37:
            color = pct_2[i]
        elif pc <= 0.64:
            color = pct_3[i]
        elif pc <= 0.91:
            color = pct_4[i]
        elif pc <= 1:
            color = pct_5[i]

        alpha = self.percentage('vol')
        if isnan(alpha):
            alpha = self.percentage('dayr')
        if isnan(alpha):
            alpha = 0.01
        softening_factor = 1.3
        alpha = alpha/softening_factor
        alpha = ", {0:.3f})".format(alpha)
        alphaTrueColor = ", {0:.3f})".format(1/softening_factor)

        return (str(color) + str(alpha)), (str(color) + str(alphaTrueColor))

    ### :STATISTIC FUNCTION ###

    def last(self, col, calc_chpt_start_type = None):
        day = self.df

        if col == 'changept' and calc_chpt_start_type != None:
            self.df['changept'] = day['price'] - day[calc_chpt_start_type]

        try:
            val = day[col].values[-1]
        except:
            print('''the column ({}) requested has not been claculated yet\nso we cannot give you the last value of it\nif you were asking for "changept" try adding "open" or "yclose"'''.format(col))

        if col in 'price open dayr yclose changept':
            return writePrice(val, self.price)

        elif col in 'vol oi':
            return writeVolume(val)

        elif col in 'thinness':
            return writeVolume(val)

        return np.nan

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
        return np.nan

    def dayr_vol_ratio(self):
        day = self.df
        # self.df['thickness'] = (day['vol'] / day['dayr'])
        try:
            self.df['thinness'] = (day['dayr'] / day['vol'])*1000000
        except:
            return '-'
        return writeNum(self.df['thinness'].values[-1])

    def percentile(self, col):
        #here col is not string but the actual panda column
        if isnan(col.values[-1]):
            return np.nan
        perc = stats.percentileofscore(col, col.values[-1])
        return round((perc / 100), 2)

    def percentage(self, col):
        np.seterr(invalid='ignore')
        day = self.df
        if isnan(day[col].values[-1]):
            return np.nan

        max_ = day[col].abs().max()
        last = day[col].abs().values[-1]
        try:
            pc = last / max_
        except:
            pc = np.nan
        return pc

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
            if stat_type == 'pc':
                val = self.percentage(col)

        if  stat_type in 'pct':
            return writeNum(val)
        elif col in 'changept, dayr':
            return writePrice(val, self.price)
        elif col in 'changepc, pc':
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
        return np.nan

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
        return np.nan
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
        return np.nan
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
        return np.nan
    string = str(num)
    if len(string[0]) > 1:
        return ("{:20,.0f}".format(num)).replace(' ','')
    return ("{:20,.2f}".format(num)).replace(' ','')

if __name__ == '__main__':
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # today = time.strftime('%Y-%m-%d')
    today = '2017-11-20'

    calc = Calc_dataframe('ES_F',today,60,'16:00','20:00')

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
    print('chpt_describe = \n {}'.format(calc.getDescribe('changept')))
    print('52r =        {}'.format(calc.day52r))

    print('VOLUME =     {}'.format(calc.last('vol')))
    print('VOLUME_avg = {}'.format(calc.stat('vol', 'avg')))
    print('VOLUME_med = {}'.format(calc.stat('vol', 'med')))
    print('VOLUME_std = {}'.format(calc.stat('vol', 'std')))
    print('dayr/vol =   {}'.format(calc.dayr_vol_ratio()))
    print('dayr/vol_avg={}'.format(calc.stat('thinness', 'avg')))
    print('days amount= {}'.format(calc.daysAmount))

    print('\ndispatch =   {}'.format(calc.func('stat: changepc avg abs')))
    print('\npct =   {}'.format(calc.func('stat: vol pc')))
    print('dispatch =   {}'.format(calc.func('last: price')))

    print('color: {}'.format(calc.color()))

    print(calc.df)
