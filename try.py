#libs required
from scipy import stats
import pandas as pd
import numpy as np

#generate ramdom data with same seed (to be reproducible)
np.random.seed(seed=10)
df = pd.DataFrame(np.random.uniform(0,0.5,(10)), columns=['a'])

print(df)

#quantile function
x = df.quantile(1)[0]

x = 0.5
#inverse of quantile
percentile = stats.percentileofscore(df['a'],x)
percentile = percentile / 100

print("the percentile of the value '{}' is '{}'".format(x,percentile))
