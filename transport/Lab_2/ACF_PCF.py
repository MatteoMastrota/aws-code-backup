from pandas import read_csv
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from datetime import datetime,timedelta
import warnings

warnings.filterwarnings("ignore")


def resetIndex(df,startdate):
    # We need the index to be a datetime
    idx=[]
    for index,row in df.iterrows():
        date = datetime(startdate.year,startdate.month,int(row["days"]),int(row["hours"]),0,0)
        idx.append(date)
    df["datetime"] = idx
    df.set_index(df["datetime"],inplace=True)
    print(df)

startdate = datetime(2017, 10, 1, tzinfo=None)
df = read_csv('Torino.csv', header=0, index_col=0, squeeze=False)

X = df["count"]#series.values

# ACF, APCF per trovare p e q
#plt.figure(figsize=(15, 5))
#pd.plotting.autocorrelation_plot(X)
#plt.title('ACF')
#plt.show()
plt.figure(figsize=(15, 5))
plot_acf(df['count'].diff().dropna(), lags=100, markersize=0)
#plt.savefig('ACF.png')
plt.show()

plt.figure(figsize=(15, 5))
plot_pacf(df['count'].diff().dropna(), lags=100, markersize=0)
#plt.savefig('PACF.png')
plt.show()

# ARIMA model fit
p = 2
q = 2
d = 1
arimaOrder = (p,d,q)
resetIndex(df,startdate)

# We train over one week
timesteps = 24*7
train = [df["count"][r] for r in range(timesteps)]
test = [df["count"][r+timesteps] for r in range(timesteps)]



# evaluate an ARIMA model for a given order (p,d,q)
def evaluate_arima_model(train, test, arima_order, method="expanding window"):
    #Check on inputs
    if method != "expanding window" or method != "sliding window":
        print("Invalid value for method, the system will use expanding window")
        method="expanding window"
        
    history = [x for x in train]
    # make predictions
    predictions = list()
    for t in range(len(test)):
        model = ARIMA(history, order=arima_order)
        model_fit = model.fit()
        yhat = model_fit.forecast()[0]
        predictions.append(yhat)
        history.append(test[t])
        
        if method == "sliding window":
            history=history[1:] # sliding
		    
    # calculate out of sample error
    rmse = np.sqrt(mean_squared_error(test, predictions))
    return rmse

	
	
evaluate_arima_model(train, test,arimaOrder)
#You current index, as printed, is string index. You should convert it to DatetimeIndex and pass a frequency by to_period:
