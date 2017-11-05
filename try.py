#libs required
from scipy import stats
import pandas as pd
import numpy as np

#generate ramdom data with same seed (to be reproducible)
np.random.seed(seed=1)
df = pd.DataFrame(np.random.uniform(0,1,(10)), columns=['a'])

#quantile function
x = df.quantile(0.5)[0]

#inverse of quantile
stats.percentileofscore(df['a'],x)
