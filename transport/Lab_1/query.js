//Number of documents present in each collection

db.getCollection('ActiveBookings').count()
-> 8743
    
db.getCollection('ActiveParkings').count()
-> 4790

db.getCollection('PermanentBookings').count()
-> 28180508

db.getCollection('PermanentParkings').count()
-> 28312676

db.getCollection('enjoy\_ActiveBookings').count()
-> 0

db.getCollection('enjoy\_ActiveParkings').count()
-> 0

db.getCollection('enjoy\_PermanentBookings').count()
-> 6653472

db.getCollection('enjoy_PermanentParkings').count()
-> 6689979

//Cities for which the system is collecting data
For Car2Go:
db.getCollection('PermanentBookings').distinct("city")
[Amsterdam, Austin, Berlin, Calgary, Columbus, Denver, Firenze, Frankfurt, Hamburg, Madrid, Milano, Montreal, Munchen, New York City, Portland, Rheinland, Roma, Seattle, Stuttgart, Torino, Toronto, Vancouver, Washington DC, Wien]

For Enjoy:
db.getCollection('enojy_PermanentBookings').distinct("city")
[Bologna, Catania, Firenze, Milano, Roma, Torino]

//Starting point and end of the collection
For Enjoy:
db.getCollection('enjoy_PermanentBookings').find({},{init_date:1})
.sort({init_time:1}).limit(1)
-> "init_date" : ISODate("2017-05-05T17:06:21.000Z")

db.getCollection('enjoy_PermanentBookings').find({},{init_date:1})
.sort({init_time:-1}).limit(1)
-> "init_date" : ISODate("2019-06-10T19:16:20.000Z")

For Car2Go:
db.getCollection('PermanentBookings').find({},{init_date:1})
.sort({init_time:1}).limit(1)
-> "init_date" : ISODate("2016-12-13T18:38:23.000Z")

db.getCollection('PermanentBookings').find({},{init_date:1})
.sort({init_time:-1}).limit(1)
-> "init_date" : ISODate("2018-01-31T08:11:33.000Z")

//Number of cars available in each city
var cities = ["Torino", "Madrid", "New York City"], len = cities.length

for(i=0; i<len; i++)
    {
        c=cities[i]
        cars = db.PermanentBookings.distinct("plate", {city : c})
        print("Total number of available cars in " + c + ": " + cars.length)
     }
->  Total number of available cars in Torino: 609
    Total number of available cars in Madrid: 475
    Total number of available cars in New York City: 1050

//Bookings recorded on the November 2017 in each city
import pymongo as pm  # import MongoClient only
import matplotlib
import pandas
import pprint
import pytz
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, datetime, timezone

client = pm.MongoClient('bigdatadb.polito.it', ssl=True,
                        authSource='carsharing', tlsAllowInvalidCertificates=True)
db = client['carsharing']
db.authenticate('ictts', 'Ictts16!')
Bookings_collection = db['PermanentBookings']
Parkings_collection = db['PermanentParkings']

startUnixTime_datetime = (datetime(2017, 11, 1, tzinfo=None))
endUnixTime_datetime = (datetime(2017, 12, 1, tzinfo=None))

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

cities = ["Torino", "Madrid", "New York City"]
for city in cities:
    if city == "Torino" or city == "Madrid":
        startUnixTime = startUnixTimeEU
        endUnixTime = endUnixTimeEU
    else:
        startUnixTime = startUnixTimeNY
        endUnixTime = endUnixTimeNY
    res = Bookings_collection.aggregate(
        [{
            "$match":
            {
                "city": city,
                "init_time": {"$gte": startUnixTime, "$lt": endUnixTime}
    }
    },
    {
    "$group":
    {
        "_id": "$city",
        "count": {"$sum": 1}
    }
    }
    ])

    print(list(res))
    
->  [{'_id': 'Torino', 'count': 67965}]
    [{'_id': 'Madrid', 'count': 140745}]
    [{'_id': 'New York City', 'count': 53829}]

//Number of bookings with alternative transportation modes recorded in each city
db.PermanentBookings.aggregate([
        {    
            $match: 
            {
                city: "Torino",
                $or:
                [
                    {"public_transport.duration":{$ne: -1}},
                    {"driving.duration":{$ne: -1}},
                    {"walking.duration":{$ne: -1}}
                 ]
                }
        },
         {
             $count: "alternative_transport"
         }])
    
    equivalente:
    db.getCollection('PermanentBookings').find({
                city: "Torino",
                $or:
                [
                    {"public_transport.duration":{$ne: -1}},
                    {"driving.duration":{$ne: -1}},
                    {"walking.duration":{$ne: -1}}
                 ]
             }).count()
             
-> Torino: 297539, Madrid: 0, New York City: 0.