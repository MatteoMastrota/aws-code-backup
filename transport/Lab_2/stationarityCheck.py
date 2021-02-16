from pandas import read_csv
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import numpy as np

df = read_csv('Madrid_prova.csv', header=0, index_col=0, squeeze=False)
print(df.head())
X = df["count"]  # series.values

# rolling mean and standard deviation over one day
df['rolling_mean_day'] = X.rolling(24).mean()
df['rolling_std_day'] = X.rolling(24).std()

# rolling mean and standard deviation over one week
df['rolling_mean_week'] = X.rolling(24*7).mean()
df['rolling_std_week'] = X.rolling(24*7).std()

plt.figure()
plt.plot(X,label="Original data")
plt.plot(df['rolling_mean_day'].dropna(),label="Rolling mean day")
plt.plot(df['rolling_std_day'].dropna(),label="Rolling std day")
# plt.plot(df['rolling_mean_week'].dropna(),label="Rolling mean week")
# plt.plot(df['rolling_std_week'].dropna(),label="Rolling std week")
# considering a longer period (one week), the process can be defined stationary

plt.xticks(np.arange(1, df.shape[0], step = 24), np.arange(1, 32), fontsize=8)
plt.legend()
plt.xlabel("Time [days]")
plt.ylabel("Number of rentals")
plt.title("Rolling statistics")
#plt.savefig('stationaryStatistics_24_.png')
plt.show()

# Augmented Dickey Fuller test to check stationarity
# d = 0
result = adfuller(X)
# d = 1
#result = adfuller(np.diff(X))
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])
print('Critical Values:')
for key, value in result[4].items():
    print('\t%s: %.3f' % (key, value))
    




