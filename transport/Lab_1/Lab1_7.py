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

startUnixTime_datetime = (datetime(2017, 11, 1, tzinfo=None))  # Start studying date
endUnixTime_datetime = (datetime(2017, 12, 1, tzinfo=None))  # End studying date

# Instantiate timezone
eu = pytz.timezone('Europe/Rome')
est = pytz.timezone('America/New_York')

# Localize in Torino/Madrid
startUnixTime_datetime = eu.localize(startUnixTime_datetime)
startUnixTime = startUnixTime_datetime.timestamp()
endUnixTime_datetime = eu.localize(endUnixTime_datetime)
endUnixTime = endUnixTime_datetime.timestamp()

# Define query to extract database info for the walking duration
resWalk = db.PermanentBookings.aggregate([
    {
        "$match": { # filter on Time and city
            "city": "Torino",
            "init_time": { "$gte": startUnixTime, "$lte": endUnixTime },
            "walking.duration": {"$ne":-1}
            }
    },
    {
        "$project": { # extract position, time, duration
            "_id": 0,
            "city": 1,
            "walk_duration": "$walking.duration",
            "moved": { "$ne": [
                    {"$arrayElemAt": [ "$origin_destination.coordinates", 0]},
                    {"$arrayElemAt": [ "$origin_destination.coordinates", 1]}
                    ]
            },
            "duration": { "$divide": [ { "$subtract": ["$final_time", "$init_time"] }, 60 ] }
    }
    },
    {
        "$match": { # filter only actual bookings
                "moved": True, # must have moved
                "duration": {"$gte": 3,
                            "$lte": 180} # must last less than 3h
    }
    },
    {   "$project": { # get then the possible cost for this rental
            "walk_duration": {"$ceil":{"$divide":[{"$divide":["$walk_duration",60]},5]}},
            "duration": 1
            }
    },
    {
        "$match": {
            "walk_duration": {"$lte": 300/5} # Filter too long trip
        }
    },
    {
        "$group":
        {
            "_id":
            {
                "walkDuration": "$walk_duration"
            },
            "count": {"$sum":1}
        }
    },
    {
        "$sort":
        {"_id":-1}
    }
])

# Define query to extract database info for the public transport duration
resPublTransp = db.PermanentBookings.aggregate([
    {
        "$match": { # filter on Time and city
            "city": "Torino",
            "init_time": { "$gte": startUnixTime, "$lte": endUnixTime },
            "public_transport.duration": {"$ne":-1}
            }
    },
    {
        "$project": { # extract position, time, duration
            "_id": 0,
            "city": 1,
            "public_transport_duration": "$public_transport.duration",
            "moved": { "$ne": [
                    {"$arrayElemAt": [ "$origin_destination.coordinates", 0]},
                    {"$arrayElemAt": [ "$origin_destination.coordinates", 1]}
                    ]
            },
            "duration": { "$divide": [ { "$subtract": ["$final_time", "$init_time"] }, 60 ] }
    }
    },
    {
        "$match": { # filter only actual bookings
                "moved": True, # must have moved
                "duration": {"$gte": 3,
                            "$lte": 180} # must last less than 3h
    }
    },
    {   "$project": { # get then the possible cost for this rental
            "public_transport_duration": {"$ceil":{"$divide":[{"$divide":["$public_transport_duration",60]},5]}},
            "duration": 1
            }
    },
    {
        "$match": {
            "public_transport_duration": {"$lte":300} # Filter too long trip
        }
    },
    {
        "$group":
        {
            "_id":
            {
                "public_transport_duration": "$public_transport_duration"
            },
            "count": {"$sum":1}
        }
    },
    {
        "$sort":
        {"_id":-1}
    }
])

# Define query to extract database info for the alternative driving duration
resDriv = db.PermanentBookings.aggregate([
    {
        "$match": { # filter on Time and city
            "city": "Torino",
            "init_time": { "$gte": startUnixTime, "$lte": endUnixTime },
            "driving.duration": {"$ne":-1}
            }
    },
    {
        "$project": { # extract position, time, duration
            "_id": 0,
            "city": 1,
            "driving_duration": "$driving.duration",
            "moved": { "$ne": [
                    {"$arrayElemAt": [ "$origin_destination.coordinates", 0]},
                    {"$arrayElemAt": [ "$origin_destination.coordinates", 1]}
                    ]
            },
            "duration": { "$divide": [ { "$subtract": ["$final_time", "$init_time"] }, 60 ] }
    }
    },
    {
        "$match": { # filter only actual bookings
                "moved": True, # must have moved
                "duration": {"$gte": 3,
                            "$lte": 180} # must last less than 3h
    }
    },
    {   "$project": { # get then the possible cost for this rental
            "driving_duration": {"$ceil":{"$divide":[{"$divide":["$driving_duration",60]},5]}},
            "duration": 1
            }
    },
    {
        "$match": {
            "driving_duration": {"$lte":300} # Filter too long trip
        }
    },
    {
        "$group":
        {
            "_id":
            {
                "driving_duration": "$driving_duration"
            },
            "count": {"$sum":1}
        }
    },
    {
        "$sort":
        {"_id":-1}
    }
])

# Extract the data for each alternative transport mode
resPublTransp = list(resPublTransp)
resWalk = list(resWalk)
resDriv = list(resDriv)

# Plot the histograms
fig, ax = plt.subplots()
ax.bar([x['_id']['walkDuration'] * 5 - 2.5 for x in resWalk], [x['count'] for x in resWalk], color = 'g', label="Walking", width =5, alpha=0.5)
ax.bar([x['_id']['public_transport_duration'] * 5 - 2.5 for x in resPublTransp], [x['count'] for x in resPublTransp], color = 'b', label="Public Transport", width =5, alpha=0.5)
ax.bar([x['_id']['driving_duration'] * 5 - 2.5 for x in resDriv], [x['count'] for x in resDriv], color = 'y', label="Alternative driving", width =5, alpha=0.5)
plt.legend()
plt.title("Number of bookings vs alternative transport mode duration in Torino")
plt.xlabel("Duration [min]")
plt.ylabel("Number of bookings")
plt.grid(True)
plt.savefig('nBookingsAlternative.png')
plt.show()