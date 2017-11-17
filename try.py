# get: 'price open dayr yclose vol oi'
# change: 'open close' 'price_range'
# stats: 'changept dayr changepc vol oi thinness' 'avg med std pct' 'abs '
# volR_rt:


import numpy as np
import pandas as pd
from scipy import stats

data = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,130,89]

df = pd.DataFrame(data)

print(df)

def percentile(col):
    #here col is not string but the actual panda column
    perc = stats.percentileofscore(col, 3.1)
    return perc

print(percentile(df[0]))
