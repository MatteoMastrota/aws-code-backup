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

	 
rmse,mpe,mape = evaluate_arima_model(train, test, arimaOrder)
print("RMSE: ",rmse)
print("MPE: ",mpe)
print("MAPE: ",mape)

##############################################################################################
############### Tuning Parameters ############################################################

p_tuning= [1,2,3,4,5]
q_tuning= [1,2,3,4,5]
d=1

def fill_matrix(matrix,value,x,y):
    matrix[x][y]=value
    
matrixMPE =np.ones((len(p_tuning),len(q_tuning)))
matrixRMSE = np.ones((len(p_tuning),len(q_tuning)))


# for p in p_tuning:
#     for q in q_tuning:
#         try:
#             arimaOrder = (p,d,q)
#             rmse,mpe,mape= evaluate_arima_model(train, test, arimaOrder)
#         except:
#             rmse,mpe,mape=(None,None,None)
#         fill_matrix(matrixMPE,mpe,p-1,q-1)
#         fill_matrix(matrixRMSE,rmse,p-1,q-1)
        
#plt.imshow(a, cmap='hot', interpolation='nearest')        
# f, ax = plt.subplots(figsize=(9, 9))

# sns.heatmap(heatmap_df, linewidths=.5, square=True, cmap='inferno_r',
#             ax=ax)
# plt.title('Number of Cars per Grid', fontsize=14)
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')
# plt.savefig('plots/heatmap.jpg', dpi=300)
# plt.show()


############################################################
# Change N and training strategy:
training_strategy = ["expanding window","sliding window"]
N = 24*3
timestep=24
EndN = 24*21
testLag = 24*7
# Select best model
p=2
q=2
d=1

arimaOrder = (p,d,q)

#{N:{s1:val,s2:val},N1:{}}
resultsRMSE = {}
resultsMPE = {}
resultsMAPE = {}
while N < EndN:
    strategyRMSE={}
    strategyMPE={}
    strategyMAPE={}
    for s in training_strategy:
        train = [df["count"][r] for r in range(N)]
        test = [df["count"][r+testLag] for r in range(N)]
        try:
            rmse,mpe,mape= evaluate_arima_model(train, test, arimaOrder, s)
        except:
            rmse,mpe,mape=(None,None,None)
        strategyRMSE[s]=rmse
        strategyMPE[s]=mpe
        strategyMAPE[s]=mape
        
    resultsRMSE[N]=strategyRMSE
    resultsMPE[N]=strategyMPE
    resultsMAPE[N]=strategyMAPE
    N += 24*1
    
df_RMSE = pd.DataFrame(resultsRMSE)
df_MPE = pd.DataFrame(resultsMPE)
df_MAPE = pd.DataFrame(resultsMAPE)
#df.to_csv('df_result.csv', index=False)
print("Dataframe")
print(df_MAPE)

df_MAPE.loc["expanding window"].plot(figsize=(10,10),marker='+')
df_MAPE.loc["sliding window"].plot(figsize=(10,10),marker='*')
plt.legend(["expanding","sliding"])
plt.title('Expanding vs Sliding window MAPE changing N', fontsize=12)
plt.ylabel('MAPE', fontsize=8)
plt.xlabel('Time [hour]', fontsize=8)
plt.xticks(df_MAPE.transpose().index,rotation=45)
plt.savefig("sliding_expanding_NYC.png",dpi=300)






######################
#FIrst model
plt.figure(figsize=(15,10)) 
plt.plot(predictions,label="Prediction") 
plt.plot(test,label="Real Values") 
plt.legend()
plt.xlabel("Hours")
plt.ylabel("Number of Rentals", rotation=90)
plt.title("Prediction vs Test, Optimal Model, NYC",fontsize=18) 
plt.savefig('Pred_NYC.png', dpi=300) 


######
df_MAPE.loc["expanding window"].plot(figsize=(10,10),marker='+')
df_MAPE.loc["sliding window"].plot(figsize=(10,10),marker='*')
plt.legend(["Expanding window","Sliding window"])
plt.title('Expanding vs Sliding window MAPE changing N', fontsize=16)
plt.ylabel('MAPE', fontsize=10)
plt.xlabel('Time [hour]', fontsize=10)
plt.xticks(df_MAPE.transpose().index,rotation=45)
plt.savefig("sliding_expanding_NYC_2.png",dpi=300)



####
plt.figure(figsize=(15,10)) 
plt.plot(predictions,label="Prediction") 
plt.plot(test,label="Real Values") 
plt.legend()
plt.xlabel("Time [hour]", fontsize=10)
plt.ylabel("Number of Rentals", rotation=90, fontsize=10)
plt.title("Prediction vs Test, Optimal Model, NYC",fontsize=16) 
plt.savefig('Pred_NYC.png', dpi=300) 