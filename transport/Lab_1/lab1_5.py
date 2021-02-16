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
db = client['carsharing']  # Choose the DB to use
db.authenticate('ictts', 'Ictts16!')  # authentication

Bookings_collection = db['PermanentBookings']  # Booking Collection for Car2go to use
Parkings_collection = db['PermanentParkings']  # Parking Collection for Car2go to use
cities = ["Torino", "Madrid", "New York City"]  # Define cities to study

startUnixTime_datetime = (datetime(2017, 11, 1, tzinfo=None))  # Start studying date
endUnixTime_datetime = (datetime(2017, 12, 1, tzinfo=None))  # End studying date

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

# Bookings
# Define query to extract database info for the selected city
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
                        "init_time" : 1,
                        "day": {
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
                            "moved": True,
                            "duration": {
                                            "$gte": 3,
                                            "$lte": 180
                                        }
                          }
            },
            {
                "$group":
                    {
                        "_id": {"day": "$day"},
                        "durations": {
                            "$push": "$duration"
                        },
                        "avg": {
                            "$avg": "$duration"
                        },
                        "stdev": {
                            "$stdDevPop": "$duration"
                        }
                    }
            },
            {
                "$sort":
                        {
                            "_id.day":1,
                        }
            }
           ])
# Extract the booking data for each city
listB = list(resB)

avgDaysB = []
medianDaysB = []
stdvDaysB = []
percentileDaysB = []
perDaysB = {}
prev = 0
for x in listB:
    day = x["_id"]["day"]
    if day < 31:
        if day == prev+1:
            avgDaysB.append(x['avg'])
            medianDaysB.append(np.median(x['durations']))
            stdvDaysB.append(x['stdev'])
            percentileDaysB.append(np.percentile(x['durations'], 90))
            prev +=1
        else:
            while (day != prev+1):
                avgDaysB.append(0)
                medianDaysB.append(0)
                stdvDaysB.append(0)
                percentileDaysB.append(0)
                prev += 1
            avgDaysB.append(x['avg'])
            medianDaysB.append(np.median(x['durations']))
            stdvDaysB.append(x['stdev'])
            percentileDaysB.append(np.percentile(x['durations'], 90))
            prev = day

# Parkings
# Define query to extract database info for the selected city
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
                        "init_time" : 1,
                        "day": {
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
                            "duration": {
                                            "$gte": 2
                                        }
                          }
            },
            {
                "$group":
                    {
                        "_id": {"day": "$day"},
                        "durations": {
                            "$push": "$duration"
                                     },
                        "avg": {
                                    "$avg": "$duration"
                               },
                        "stdev": {
                                    "$stdDevPop": "$duration"
                                 }
                    }
            },
            {
                "$sort":
                        {
                            "_id.day":1
                        }
            }
           ])
# Extract the parking data for each city
listP = list(resP)

avgDaysP = []
medianDaysP = []
stdvDaysP = []
percentileDaysP = []
prev = 0
for x in listP:
    day = x["_id"]["day"]
    if day < 31:
        if day == prev+1:
            avgDaysP.append(x['avg'])
            medianDaysP.append(np.median(x['durations']))
            stdvDaysP.append(x['stdev'])
            percentileDaysP.append(np.percentile(x['durations'], 90))
            prev += 1
        else:
            while(day != prev+1):
                avgDaysP.append(0)
                medianDaysP.append(0)
                stdvDaysP.append(0)
                percentileDaysP.append(0)
                prev += 1
            avgDaysP.append(x['avg'])
            medianDaysP.append(np.median(x['durations']))
            stdvDaysP.append(x['stdev'])
            percentileDaysP.append(np.percentile(x['durations'], 90))
            prev = day

# Plot statistic about booking
plt.figure(figsize=(20,10))
x = np.linspace(1,31,30)
plt.xticks(np.arange(1,31,1))
plt.plot(x, avgDaysB, label='Average', color='blue')
plt.plot(x, medianDaysB, label='Median', color='orange')
plt.plot(x, stdvDaysB, label='Standard Deviation', color='green')
plt.plot(x, percentileDaysB, label='90th percentile', color='red')
plt.title("Average, median, standard deviation, 90th percentile of the duration of the bookings \n in " + city + "per day during November")
plt.ylabel('Avg, median, stdv, 90th percentile')
plt.xlabel('Date')
plt.grid(True)
plt.legend()
#plt.savefig('Statistics_booked_Madrid_Nov.png')
plt.show()

# Plot statistic about parking
plt.figure(figsize=(20,10))
plt.xticks(np.arange(1,31,1))
plt.plot(x, avgDaysP, label='Average', color='blue')
plt.plot(x, medianDaysP, label='Median', color='orange')
plt.plot(x, stdvDaysP, label='Standard Deviation', color='green')
plt.plot(x, percentileDaysP, label='90th percentile', color='red')
plt.title("Average, median, standard deviation, 90th percentile of the duration of the parkings \n in " + city + "per day during November")
plt.ylabel('Avg, median, stdv, 90th percentile')
plt.xlabel('Date')
plt.grid(True)
plt.legend()
#plt.savefig('Statistics_parked_Madrid_Nov.png')
plt.show()