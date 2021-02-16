import pymongo as pm  # import MongoClient only
import matplotlib
import pandas
import pprint
import pytz
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, datetime, timezone

# Initialize MongoDB Client
client = pm.MongoClient('bigdatadb.polito.it', ssl=True,
                        authSource='carsharing', tlsAllowInvalidCertificates=True)
db = client['carsharing'] # Choose the DB to use
db.authenticate('ictts', 'Ictts16!') #authentication

Bookings_collection = db['PermanentBookings'] # Booking Collection for Car2go to use
Parkings_collection = db['PermanentParkings'] # Parking Collection for Car2go to use
cities = ["Torino", "Madrid", "New York City"] # Define cities to study

startUnixTime_datetime = (datetime(2017, 11, 1, tzinfo=None)) # Start studying date
endUnixTime_datetime = (datetime(2017, 12, 1, tzinfo=None)) # End studying date

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

# For each city under study
for city in cities:
    if city == "Madrid" or city == "Torino":
        startUnixTime = startUnixTimeEU
        endUnixTime = endUnixTimeEU
    else:
        startUnixTime = startUnixTimeNY
        endUnixTime = endUnixTimeNY

    # Define query to extract database info for each city
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
                    "_id": {"day": "$dayMonth", "hour": "$hourDay"},
                    "count": {"$sum": 1}
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
    
    resP = Parkings_collection.aggregate([{
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
                "duration": {  # only the duration that last more than 2 minutes
                    "$gte": 2
                }
            }
        },
        {
            "$group":
                {
                    "_id": {"day": "$dayMonth", "hour": "$hourDay"},
                    "count": {"$sum": 1}
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
    
    # Extract the booking data for each city
    if city == "Torino":
        listB_TO = list(resB)
        listP_TO = list(resP)
    if city == "Madrid":
        listB_MA = list(resB)
        listP_MA = list(resP)
    if city == "New York City":
        listB_NYC = list(resB)
        listP_NYC = list(resP)

# Create dict for each city in which the keys are the days and the values are the number of bookings per hour
# Torino
perDaysTO = {} 
for item in listB_TO:
    day = item["_id"]["day"]
    if day < 31:
        if (day == 1 and day not in perDaysTO.keys()) or day ==  list(perDaysTO.keys())[len(perDaysTO.keys())-1]+1:
            perDaysTO[day] = [0]*24
        else:
            while day != list(perDaysTO.keys())[len(perDaysTO.keys())-1]:
                perDaysTO[list(perDaysTO.keys())[len(perDaysTO.keys())-1]+1] = [0]*24
        hour = item["_id"]["hour"]
        perDaysTO[day][hour] = item['count']
        
# Madrid
perDaysMA = {}
for item in listB_MA:
    day = item["_id"]["day"]
    if day < 31:
        if (day == 1 and day not in perDaysMA.keys()) or day ==  list(perDaysMA.keys())[len(perDaysMA.keys())-1]+1:
            perDaysMA[day] = [0]*24
        else:
            while day != list(perDaysMA.keys())[len(perDaysMA.keys())-1]:
                perDaysMA[list(perDaysMA.keys())[len(perDaysMA.keys())-1]+1] = [0]*24
        hour = item["_id"]["hour"]
        perDaysMA[day][hour] = item['count']

# New York City
perDaysNYC = {}
for item in listB_NYC:
    day = item["_id"]["day"]
    if day < 31:
        if (day == 1 and day not in perDaysNYC.keys()) or day ==  list(perDaysNYC.keys())[len(perDaysNYC.keys())-1]+1:
            perDaysNYC[day] = [0]*24
        else:
            while day != list(perDaysNYC.keys())[len(perDaysNYC.keys())-1]:
                perDaysNYC[list(perDaysNYC.keys())[len(perDaysNYC.keys())-1]+1] = [0]*24
        hour = item["_id"]["hour"]
        perDaysNYC[day][hour] = item['count']

# Plot booked cars data, per day
fig = plt.figure(1, figsize=(20, 10))
plt.xticks(np.arange(1, len(sum(perDaysTO.values(),[])), 24), np.arange(1,31), fontsize=8)
plt.grid(True, which='both')
plt.plot(sum(perDaysTO.values(),[]), label='Torino') #in order to concatenate all the lists in only one list
plt.plot(sum(perDaysMA.values(),[]), label='Madrid')
plt.plot(sum(perDaysNYC.values(),[]), label='New York City')
plt.xlabel('Day of November')
plt.ylabel('Number of booked cars')
plt.title('Booked cars per hour during November')
plt.legend()
plt.savefig('BookedCarsAllNov.png')
plt.show()

# Parkings
# Create dict for each city in which the keys are the days and the values are the number of parkings per hour
# Torino
perDaysP_TO = {}
for item in listP_TO:
    day = item["_id"]["day"]
    if day < 31:
        if (day == 1 and day not in perDaysP_TO.keys()) or day ==  list(perDaysP_TO.keys())[len(perDaysP_TO.keys())-1]+1:
            perDaysP_TO[day] = [0]*24
        else:
            while day != list(perDaysP_TO.keys())[len(perDaysP_TO.keys())-1]:
                perDaysP_TO[list(perDaysP_TO.keys())[len(perDaysP_TO.keys())-1]+1] = [0]*24
        hour = item["_id"]["hour"]
        perDaysP_TO[day][hour] = item['count']
        
# Madrid
perDaysP_MA = {}
for item in listP_MA:
    day = item["_id"]["day"]
    if day < 31:
        if (day == 1 and day not in perDaysP_MA.keys()) or day ==  list(perDaysP_MA.keys())[len(perDaysP_MA.keys())-1]+1:
            perDaysP_MA[day] = [0]*24
        else:
            while day != list(perDaysP_MA.keys())[len(perDaysP_MA.keys())-1]:
                perDaysP_MA[list(perDaysP_MA.keys())[len(perDaysP_MA.keys())-1]+1] = [0]*24
        hour = item["_id"]["hour"]
        perDaysP_MA[day][hour] = item['count']

# New York City
perDaysP_NYC = {}
for item in listP_NYC:
    day = item["_id"]["day"]
    if day < 31:
        if (day == 1 and day not in perDaysP_NYC.keys()) or day ==  list(perDaysP_NYC.keys())[len(perDaysP_NYC.keys())-1]+1:
            perDaysP_NYC[day] = [0]*24
        else:
            while day != list(perDaysP_NYC.keys())[len(perDaysP_NYC.keys())-1]:
                perDaysP_NYC[list(perDaysP_NYC.keys())[len(perDaysP_NYC.keys())-1]+1] = [0]*24
        hour = item["_id"]["hour"]
        perDaysP_NYC[day][hour] = item['count']

# Plot parked cars data, per day
fig = plt.figure(1, figsize=(20, 10))
plt.xticks(np.arange(1, len(sum(perDaysP_TO.values(),[])), 24), np.arange(1,31), fontsize=8)
plt.grid(True, which='both')
plt.plot(sum(perDaysP_TO.values(),[]), label='Torino')
plt.plot(sum(perDaysP_MA.values(),[]), label='Madrid')
plt.plot(sum(perDaysP_NYC.values(),[]), label='New York City')
plt.xlabel('Day of November')
plt.ylabel('Number of parked cars')
plt.title('Parked cars per hour during November')
plt.legend()
plt.savefig('ParkedCarsAllNov.png')
plt.show()