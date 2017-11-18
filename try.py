# get: 'price open dayr yclose vol oi'
# change: 'open close' 'price_range'
# stats: 'changept dayr changepc vol oi thinness' 'avg med std pct' 'abs '
# volR_rt:

#
# import numpy as np
# import pandas as pd
# from scipy import stats
#
# data = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,130,89]
#
# df = pd.DataFrame(data)
#
# print(df)
#
# def percentile(col):
#     #here col is not string but the actual panda column
#     perc = stats.percentileofscore(col, 3.1)
#     return perc
#
# print(percentile(df[0]))


ls = '''pct_0 = 'rgba(254, 255, 75,'
pct_1 = ('rgba(240, 255, 73,', 'rgba(255, 243, 75,')
pct_2 = ('rgba(188, 232, 36,', 'rgba(255, 101, 41,')
pct_3 = ('rgba(81, 189, 54,', 'rgba(255, 191, 39,')
pct_4 = ('rgba(37, 139, 63,', 'rgba(239, 45, 23,')
pct_5 = ('rgba(0, 255, 234,', 'rgba(234, 0, 255,')
'''
pct_0 = 'rgba(0.9961, 1.0000, 0.2941,'
pct_1 = ('rgba(0.9412, 1.0000, 0.2863,', 'rgba(1.0000, 0.9529, 0.2941,')
pct_2 = ('rgba(0.7373, 0.9098, 0.1412,', 'rgba(1.0000, 0.3961, 0.1608,')
pct_3 = ('rgba(0.3176, 0.7412, 0.2118,', 'rgba(1.0000, 0.7490, 0.1529,')
pct_4 = ('rgba(0.1451, 0.5451, 0.2471,', 'rgba(20.1529, 0.1765, 0.0902,')
pct_5 = ('rgba(0, 1.0000, 0.9176,', 'rgba(0.9176, 0, 1.0000,')


def isnumber(x):
    try:
        int(x)
        return True
    except:
        return False
num = ''
num_list = []
for char in ls:

    if isnumber(char):
        num = num + char
    else:
        if len(num) < 2:
            num = ''
        else:
            num_list.append(num)
            num = ''

d = {}

for i in num_list:
    value = "{0:.4f}".format(int(i)/255)
    d[str(i)] = value

for key, value in d.items():
    print(key + ' - ' + value)

print(ls)

for key, value in d.items():
    ls = ls.replace(key+',', key + 'ciccio,')

print(ls)

for key, value in d.items():
    ls = ls.replace(key + 'ciccio', value)

print(ls)
