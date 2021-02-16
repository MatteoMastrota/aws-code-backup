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

# We train over one week
timesteps = 24*7
train = [df["count"][r] for r in range(timesteps)]
test = [df["count"][r+timesteps] for r in range(timesteps)]


# evaluate an ARIMA model for a given order (p,d,q)
def evaluate_arima_model(train, test, arima_order, method="expanding window"):
    #Check on inputs
    if method != "expanding window" and method != "sliding window":
        print("You choose",method)
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
    mpe = np.mean(np.divide(np.subtract(test,predictions),test))*100
    mape = np.mean(np.abs(np.divide(np.subtract(test,predictions),test)))*100
    #plt.figure()
    #plt.plot(predictions,label="Prediction")
    #plt.plot(test,label="Real Values")
    #plt.legend()
    #plt.show()
    return rmse,mpe,mape

	
rmse,mpe,mape= evaluate_arima_model(train, test, arimaOrder)
print("RMSE: ",rmse)
print("MPE: ",mpe)
print("MAPE: ",mape)

##############################################################################################
############### Tuning Parameters ############################################################

p_tuning= [1,2,3,4,5]
q_tuning= [1,2,3,4,5]
d=1

def fill_matrix(matrix,value,x,y):
    matrix[x-1][y-1]=value
    
matrixMPE =np.ones((len(p_tuning),len(q_tuning)))
matrixRMSE = np.ones((len(p_tuning),len(q_tuning)))

for p in p_tuning:
    for q in q_tuning:
        tr
            arimaOrder = (p,d,q)
            rmse,mpe,mape= evaluate_arima_model(train, test, arimaOrder)
            fill_matrix(matrixMPE,mpe,p,q)
            fill_matrix(matrixRMSE,rmse,p,q)
        
#plt.imshow(a, cmap='hot', interpolation='nearest')        
# f, ax = plt.subplots(figsize=(9, 9))

# sns.heatmap(heatmap_df, linewidths=.5, square=True, cmap='inferno_r',
#             ax=ax)
# plt.title('Number of Cars per Grid', fontsize=14)
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')
# plt.savefig('plots/heatmap.jpg', dpi=300)
# plt.show()
