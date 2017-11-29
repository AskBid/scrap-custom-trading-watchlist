import sys
from os import listdir, system, path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt, QSize
import datait
from random import *
import time
import datetime
from pandas.tseries.offsets import BDay #to make operation betwen dates where only BusinessDays are considered
from PyQt5.QtCore import QDate
from drawit import drawCandle, draw52RangeBar
# import mergeit
import ec2it
from math import isnan
import htmit
import webbrowser

today = time.strftime('%Y-%m-%d')
print(today)
# width, height = 800, 600

def prev_weekday(adate):
    print(adate)
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= datetime.timedelta(days=1)
    return adate

today = prev_weekday(datetime.datetime.strptime(today, '%Y-%m-%d')).strftime("%Y-%m-%d")
print(today)
