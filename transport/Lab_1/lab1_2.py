import pymongo as pm  # import MongoClient only
import matplotlib
import pandas
import pprint
import numpy as np
import pytz
import matplotlib.pyplot as plt
from datetime import date, datetime, timezone

# Instantiate mongodb client
client = pm.MongoClient('bigdatadb.polito.it', ssl=True,
                        authSource='carsharing', tlsAllowInvalidCertificates=True)
db = client['carsharing']  # Choose the DB to use
# , mechanism='MONGODB-CR') #authentication
db.authenticate('ictts', 'Ictts16!')

cities = ['Torino','New York City', 'Madrid'] # Define cities to study
Bookings_collection = db['PermanentBookings']  # Booking Collection for Car2go to use
Parkings_collection = db['PermanentParkings'] # Parking Collection for Car2go to use

startUnixTime_datetime = (datetime(2017, 11, 1, tzinfo=None))
endUnixTime_datetime = (datetime(2017, 12, 1, tzinfo=None))

# Instantiate timezone
eu= pytz.timezone('Europe/Rome')
est=pytz.timezone('America/New_York')

# Localize in Torino/Madrid
startUnixTime_datetimeEU = eu.localize(startUnixTime_datetime)
startUnixTimeEU = startUnixTime_datetimeEU.timestamp()
endUnixTime_datetimeEU = eu.localize(endUnixTime_datetime)
endUnixTimeEU = endUnixTime_datetimeEU.timestamp()

#Localize in NYC
startUnixTime_datetimeNY = est.localize(startUnixTime_datetime)
startUnixTimeNY = startUnixTime_datetimeNY.timestamp()
endUnixTime_datetimeNY = est.localize(endUnixTime_datetime)
endUnixTimeNY = endUnixTime_datetimeNY.timestamp()

# Define pipeline to extract database info
pipeline_Torino = [{"$match":
                    {
                        "city": "Torino",
                        "init_time": {"$gte": startUnixTimeEU, "$lte": endUnixTimeEU},
                        # "final_time": {
                            # "$gte": startUnixTime, "$lte": endUnixTime}
                    }
                    },
                   {"$project":
                    {
                        "city": "$city",
                        "hour": {"$hour":"$init_date"}
                    }
                    },
                   {"$group":
                    {

                        "_id": {"city": "$city", "hour": "$hour"},
                        "count": {"$sum": 1}
                    }
                    },
                   {"$sort":
                    {"_id": 1}
                    }
                   ]

pipeline_Madrid = [{"$match":
                    {
                        "city": "Madrid",
                        "init_time": {"$gte": startUnixTimeEU, "$lte": endUnixTimeEU},
                        # "final_time": {
                            # "$gte": startUnixTime, "$lte": endUnixTime}
                    }
                    },
                   {"$project":
                    {
                        "city": "$city",
                        "hour": {"$hour":"$init_date"}
                    }
                    },
                   {"$group":
                    {

                        "_id": {"city": "$city", "hour": "$hour"},
                        "count": {"$sum": 1}
                    }
                    },
                   {"$sort":
                    {"_id": 1}
                    }
                   ]

pipeline_NYC = [
                    {"$match":
                    {
                        "city": "New York City",
                        "init_time": {"$gte": startUnixTimeNY, "$lte": endUnixTimeNY},
                        # "final_time": {
                            # "$gte": startUnixTime, "$lte": endUnixTime}
                    }
                    },
                   {"$project":
                    {
                        "city": "$city",
                        "hour": {"$hour":"$init_date"}
                    }
                    },
                   {"$group":
                    {

                        "_id": {"city": "$city", "hour": "$hour"},
                        "count": {"$sum": 1}
                    }
                    },
                   {"$sort":
                    {"_id": 1}
                    }
                   ]

# Extract booking data
book_res_NY =list(Bookings_collection.aggregate(pipeline_NYC))
book_res_TO = list(Bookings_collection.aggregate(pipeline_Torino))
book_res_MA = list(Bookings_collection.aggregate(pipeline_Madrid))

#Extract parking data
park_res_TO = list(Parkings_collection.aggregate(pipeline_Torino))
park_res_NY =list(Parkings_collection.aggregate(pipeline_NYC))
park_res_MA = list(Parkings_collection.aggregate(pipeline_Madrid))


# Plot booking for each city per hour of the day
fig,ax=plt.subplots()
ax.bar([x["_id"]["hour"]+0 for x in book_res_TO],[y["count"] for y in book_res_TO], color = 'b',label="Torino", width = 0.25)
ax.bar([x["_id"]["hour"]-0.25 for x in book_res_NY],[y["count"] for y in book_res_NY], color = 'y',label="New York City", width = 0.25)
ax.bar([x["_id"]["hour"]+0.25 for x in book_res_MA],[y["count"] for y in book_res_MA], color = 'r',label="Madrid", width = 0.25)
ax.legend(labels=['Torino', 'New York City','Madrid'])
ax.set_ylabel('Bookings')
ax.set_xlabel('Hour')
ax.set_title('Booking per hour vs time of day')
ax.set_xticks(list([x["_id"]["hour"] for x in book_res_TO]))
ax.set_xticklabels([x["_id"]["hour"] for x in book_res_TO])
ax.set_yticks(np.arange(0, max([y["count"] for y in book_res_MA]), 1000))

plt.show()

# Plot parking for each city per hour of the day
fig,ax=plt.subplots()
ax.bar([x["_id"]["hour"]+0 for x in park_res_TO],[y["count"] for y in park_res_TO], color = 'b',label="Torino", width = 0.25)
ax.bar([x["_id"]["hour"]-0.25 for x in park_res_NY],[y["count"] for y in park_res_NY], color = 'y',label="New York City", width = 0.25)
ax.bar([x["_id"]["hour"]+0.25 for x in park_res_MA],[y["count"] for y in park_res_MA], color = 'r',label="Madrid", width = 0.25)
ax.legend(labels=['Torino', 'New York City','Madrid'])
ax.set_ylabel('Parking')
ax.set_xlabel('Hour')
ax.set_title('Parking per hour vs time of day')
ax.set_xticks(list([x["_id"]["hour"] for x in park_res_TO]))
ax.set_xticklabels([x["_id"]["hour"] for x in park_res_TO])
ax.set_yticks(np.arange(0, max([y["count"] for y in park_res_NY]), 1000))

plt.show()

# FILTER
resMA = list(Bookings_collection.aggregate([{
                "$match":
                    {
                        "city": "Madrid",
                        "init_time": {
                                        "$gte": startUnixTimeEU,
                                        "$lt": endUnixTimeEU
                                     },
                    }
            },
            {
                "$project":
                    {
                        "_id": 0,
                        "init_time" : 1,
                        "hourDay": {
                                    "$hour": "$init_date"
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
                        "_id": {"hour": "$hourDay"},
                        "count": {"$sum": 1}
                    }
            },
            {
                "$sort":
                        {
                            "_id": 1
                        }
            }
           ]))
resNY = list(Bookings_collection.aggregate([{
                "$match":
                    {
                        "city": "New York City",
                        "init_time": {
                                        "$gte": startUnixTimeNY,
                                        "$lt": endUnixTimeNY
                                     },
                    }
            },
            {
                "$project":
                    {
                        "_id": 0,
                        "init_time" : 1,
                        "hourDay": {
                                    "$hour": "$init_date"
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
                        "_id": {"hour": "$hourDay"},
                        "count": {"$sum": 1}
                    }
            },
            {
                "$sort":
                        {
                            "_id": 1
                        }
            }
           ]))
resTO = list(Bookings_collection.aggregate([{
                "$match":
                    {
                        "city": "Torino",
                        "init_time": {
                                        "$gte": startUnixTimeEU,
                                        "$lt": endUnixTimeEU
                                     },
                    }
            },
            {
                "$project":
                    {
                        "_id": 0,
                        "init_time" : 1,
                        "hourDay": {
                                    "$hour": "$init_date"
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
                        "_id": {"hour": "$hourDay"},
                        "count": {"$sum": 1}
                    }
            },
            {
                "$sort":
                        {
                            "_id": 1
                        }
            }
           ]))
           
fig,ax=plt.subplots()
ax.bar([x["_id"]["hour"]+0 for x in resTO],[y["count"] for y in resTO], color = 'b',label="Torino", width = 0.25)
ax.bar([x["_id"]["hour"]-0.25 for x in resNY],[y["count"] for y in resNY], color = 'y',label="New York City", width = 0.25)
ax.bar([x["_id"]["hour"]+0.25 for x in resMA],[y["count"] for y in resMA], color = 'r',label="Madrid", width = 0.25)
ax.legend(labels=['Torino', 'New York City','Madrid'])
ax.set_ylabel('Bookings')
ax.set_xlabel('Hour')
ax.set_title('Booking per hour vs time of day (filtered)')
ax.set_xticks(list([x["_id"]["hour"] for x in book_res_TO]))
ax.set_xticklabels([x["_id"]["hour"] for x in book_res_TO])
ax.set_yticks(np.arange(0, max([y["count"] for y in book_res_MA]), 1000))

plt.show()