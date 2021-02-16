import pymongo as pm
import matplotlib
import pandas as pd
import pprint
import pytz
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, datetime, timezone
# Initialize MongoDB Client
client = pm.MongoClient('bigdatadb.polito.it', ssl=True,
                        authSource='carsharing', tlsAllowInvalidCertificates=True)
db = client['carsharing']  # Choose the DB to use
db.authenticate('ictts', 'Ictts16!')  # authentication

Bookings_collection = db['PermanentBookings']  # Booking Collection for Car2go to use
Parkings_collection = db['PermanentParkings']  # Parking Collection for Car2go to use
cities = ["Torino", "Madrid", "New York City"]  # Define cities to study

startUnixTime_datetime = (datetime(2017, 10, 1, tzinfo=None))  # Start studying date
endUnixTime_datetime = (datetime(2017, 11, 1, tzinfo=None))  # End studying date

# Instantiate timezone
eu = pytz.timezone('Europe/Rome')
est = pytz.timezone('America/New_York')

# Localize in Torino/Madrid
startUnixTime_datetimeEU = eu.localize(startUnixTime_datetime)
startUnixTimeEU = startUnixTime_datetimeEU.timestamp()
endUnixTime_datetimeEU = eu.localize(endUnixTime_datetime)
endUnixTimeEU = endUnixTime_datetimeEU.timestamp()

# Localize in NYC
startUnixTime_datetimeNY = est.localize(startUnixTime_datetime)
startUnixTimeNY = startUnixTime_datetimeNY.timestamp()
endUnixTime_datetimeNY = est.localize(endUnixTime_datetime)
endUnixTimeNY = endUnixTime_datetimeNY.timestamp()

print("Select the city you are interested in: \n")
city = input()
if city == "Madrid" or city == "Torino":
    startUnixTime = startUnixTimeEU
    endUnixTime = endUnixTimeEU
else:
    startUnixTime = startUnixTimeNY
    endUnixTime = endUnixTimeNY

resB = Bookings_collection.aggregate([{
    "$match":
        {
            "city": city,
            "init_time": {
                "$gte": startUnixTime,
                "$lt": endUnixTime
            },
        }
},
    {
        "$project":
            {
                "_id": 0,
                "init_time": 1,
                "hourDay": {
                    "$hour": "$init_date"
                },
                "dayMonth": {
                    "$dayOfMonth": "$init_date"
                },
                "day_week": {
                    "$dayOfWeek": "$init_date"
                },
                "moved": {
                    "$ne": [
                        {"$arrayElemAt": ["$origin_destination.coordinates", 0]},
                        {"$arrayElemAt": ["$origin_destination.coordinates", 1]}
                    ]
                },
                "duration": {
                    "$ceil": {
                        "$divide": [
                            {"$subtract": ["$final_time", "$init_time"]},
                            60
                        ]
                    }
                }
            }
    },
    {
        "$match": {
            "moved": True,  # only the cars which have starting coordinates different from the final ones
            "duration": {  # only the durations higher than 3 minutes but lower than 180
                "$gte": 3,
                "$lte": 180
            }
        }
    },
    {
        "$group":
            {
                "_id": {"day": "$dayMonth", "hour": "$hourDay"
                        },
                "count": {"$sum": 1},
                "dayWeek": { "$first": "$day_week"} # returns a value from the first document for each group
            }
    },
    {
        "$sort":
            {
                "_id.day": 1,
                "_id.hour": 1
            }
    }
])

listB = list(resB)

df = pd.DataFrame(listB)

# create a dataframe for each day of the week
df1 = df.loc[df['dayWeek'] == 1]
df2 = df.loc[df['dayWeek'] == 2]
df3 = df.loc[df['dayWeek'] == 3]
df4 = df.loc[df['dayWeek'] == 4]
df5 = df.loc[df['dayWeek'] == 5]
df6 = df.loc[df['dayWeek'] == 6]
df7 = df.loc[df['dayWeek'] == 7]

def meanHour(df):
    '''
        check all data of each df:
        one list for each day of the week,
        if the number of bookings is valid, it is saved in the corrispondent list,
        then the average of each day of the week is computed in order to replace missed values with it.

        :return: mean number of bookings for df
    '''
    meanPerHour = []
    tmp = {}
    for i in range(24):
        tmp[i] = []
    for index, row in df.iterrows():
        count = row['count']
        h = row['_id']['hour']
        tmp[h].append(count)
    for i in range(len(tmp)):
        val = sum(tmp[i])/len(tmp[i])
        meanPerHour.append(val)
    return meanPerHour

meanPerHour = {} # dict: keys are the days of the week, values are the mean number of bookings
meanPerHour[1] = meanHour(df1)
meanPerHour[2] = meanHour(df2)
meanPerHour[3] = meanHour(df3)
meanPerHour[4] = meanHour(df4)
meanPerHour[5] = meanHour(df5)
meanPerHour[6] = meanHour(df6)
meanPerHour[7] = meanHour(df7)

dict = {}
previous = -1
count = 0
new = pd.DataFrame(columns=['_id','count']) # new df to fill the initial one
for index, row in df.iterrows():
    tmp = row['_id']['hour'] - previous # how many hours there are between the actual and the previous row
    while tmp > 1:
        # a missing value exists: replace it with the mean of the corresponding day of the week
        replace = meanPerHour[row['_id']['day']][row['_id']['hour']-tmp+1]
        new.loc[count] = [{'day': row['_id']['day'], 'hour': row['_id']['hour']-tmp+1}, replace]
        count += 1
        tmp -= 1
    previous = row['_id']['hour']

dfinal = df.append(new, ignore_index=True)
days = []
hours = []
for index, row in dfinal.iterrows():
    days.append(row['_id']['day'])
    hours.append(row['_id']['hour'])
dfinal['days'] = days
dfinal['hours'] = hours
dfinal.sort_values(by=['days', 'hours'], inplace=True)
dfinal.drop(columns=['dayWeek'], inplace=True)

dfinal.to_csv(city + '_prova.csv', index=False) # save the completed and sorted df into csv