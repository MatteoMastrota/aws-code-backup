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
    plt.figure()
    plt.plot(predictions,label="Prediction")
    plt.plot(test,label="Real Values")
    plt.legend()
    plt.show()
    return rmse,mpe,mape

