import time
import datetime as dt
from pandas.tseries.offsets import BDay


s = '2017-09-22'
d = dt.datetime.strptime(s, '%Y-%m-%d') - dt.timedelta(days=6)
c = dt.datetime.strptime(s, '%Y-%m-%d') - BDay(6)
d = dt.datetime.today() - dt.timedelta(days=6)
c = dt.datetime.today() - BDay(6)
print(d.strftime('%Y-%m-%d'))
print(c.strftime('%Y-%m-%d'))
