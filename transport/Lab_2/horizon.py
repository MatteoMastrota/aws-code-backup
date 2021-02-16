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

np.random.seed(0)
warnings.filterwarnings("ignore")


# evaluate an ARIMA model for a given order (p,d,q)
def evaluate_arima_model(train, test, arima_order,predDict={},h=1, method="expanding window"):
    
    #Check on inputs
    if method != "expanding window" and method != "sliding window":
        print("You choose",method)
        print("Invalid value for method, the system will use expanding window")
        method="expanding window"
        
    history = [x for x in train]
    # make predictions
    for t in range(len(test)):
        #print(len(test)-t-1,"Times to go")
        model = ARIMA(history, order=arima_order)
        model_fit = model.fit()
        predDict[h].append(model_fit.forecast(steps=h)[h-1])
        history.append(test[t])
        if method == "sliding window":
            history=history[1:] # sliding
    
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

# ARIMA model fit
p = 2
q = 2
d = 1
arimaOrder = (p,d,q)
resetIndex(df,startdate)

N = 24*6
testLag=24*6

train = [df["count"][r] for r in range(N)]
test = [df["count"][r+testLag] for r in range(N)]

predDict={}
for i in range(1,25):
    predDict[i]=[]
    
for h in range(1,25):
    print("Try h=",h)
    evaluate_arima_model(train, test, arimaOrder,predDict,h)
print("FINE")
# history = [x for x in train]
# # make predictions
# for i in range(1,25):
#     model = ARIMA(history, order=arimaOrder)
#     model_fit = model.fit()
#     print(model_fit.forecast(steps=i))
df_pred = pd.DataFrame(predDict)
print(df_pred)

# x = range(len(test))
# print(x)
# plt.figure(figsize=(70,20))
# plt.plot(x[:50],test[:50])

# for i in range(1,5):
#     plt.plot(range(i,len(test)+i)[:50] , df_pred[i][:50])

mape = []
rmse = []
mpe = []
for k in predDict.keys():
    rmse.append(np.sqrt(mean_squared_error(test[k:], predDict[k][:len(predDict[k])-k])))
    mpe.append(np.mean(np.divide(np.subtract(test[k:], predDict[k][:len(predDict[k])-k]), test[k:])) * 100)
    mape.append(np.mean(np.abs(np.divide(np.subtract(test[k:], predDict[k][:len(predDict[k])-k]), test[k:]))) * 100)
print(mape)

plt.figure()
plt.plot(rmse, label='RMSE')
plt.plot(mpe, label='MPE')
plt.plot(mape, label='MAPE')
plt.legend()
plt.savefig('horizon_MA.png')
plt.show()

# history=[x for x in train]
# model = ARIMA(history, order=arimaOrder)
# model_fit = model.fit()
# gg = model_fit.predict(1,48)
# plt.figure(figsize=(30,10))
# plt.plot(range(1,49),gg)
# plt.plot(test[:48])
# plt.legend(["pred","test"])



##########################  bre    ################################
mape = []
rmse = []
mpe  = []
for k in df_pred.keys():
    rmse.append(np.sqrt(mean_squared_error(test[k:], predDict[k][:len(predDict[k])-k])))
    mpe.append(np.mean(np.divide(np.subtract(test[k:], predDict[k][:len(predDict[k])-k]), test[k:])) * 100)
    mape.append(np.mean(np.abs(np.divide(np.subtract(test[k:], predDict[k][:len(predDict[k])-k]), test[k:]))) * 100)
print(mape)

plt.figure(figsize=(10,10))
plt.plot(rmse, label='RMSE', color = 'blueviolet')
plt.plot(mpe, label='MPE', color = 'orange')
plt.plot(mape, label='MAPE', color = 'steelblue')
plt.legend()
plt.ylabel("Error", fontsize=10)
plt.xlabel("Time [hour]",fontsize=10)
plt.xticks([i for i in range(0,25)])
plt.title("Errors for Different Time Horizon Predictions, NYC",fontsize=16)
plt.savefig('horizon_NYC.png')
plt.show()
#####################