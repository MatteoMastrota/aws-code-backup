import pymongo as pm  # import MongoClient only
import matplotlib
import pandas
import pprint
import pytz
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, datetime, timezone

def plotCDF(list_eval,totals,labels,title=0,xlabel=0,show=False):
    '''
    Take list value and plot CDF for collectionType:
        list_eval: list on which calculate CDF
        totals: total count of element
        labels: label of the plot
        title: title to add to figure when plotting
        show(Bool): show the plot 
    '''
    
    durata = []
    count = []
    counter = 0  # book_res_TO[0]['count']
    
    #Compute CDF 
    for x in list_eval:
        durata.append(x['_id']['duration'])
        count.append((x['count'] / totals + counter))
        counter = count[-1] #always take last element
        
    plt.plot(durata, count,label = labels)
    # print(labels+ ": "+ str(totals))
    #If show =True then show what has been plotted so far
    if show:
        plt.title("Cumulative Distribution Function for "+title)
        plt.xscale('log') # Use log scale
        plt.xlabel(xlabel)
        plt.ylabel("CDF")
        plt.legend()
        plt.show()

# Initialize MongoDB Client
client = pm.MongoClient('bigdatadb.polito.it', ssl=True,
                        authSource='carsharing', tlsAllowInvalidCertificates=True)
db = client['carsharing']  # Choose the DB to use
# , mechanism='MONGODB-CR') #authentication
db.authenticate('ictts', 'Ictts16!')

cities = ['Torino','New York City', 'Madrid'] # Define cities to study
Bookings_collection = db['PermanentBookings']  # Booking Collection for Car2go to use
Parkings_collection = db['PermanentParkings'] # Parking Collection for Car2go to use

startUnixTime_datetime = (datetime(2017, 11, 1, tzinfo=None)) # start studying date
endUnixTime_datetime = (datetime(2017, 12, 1, tzinfo=None)) # end studying date

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
                        "duration": {"$floor": {"$divide": [
                            {"$subtract": ["$final_time", "$init_time"]}, 60]}}
                    }
                    },
                   {"$group":
                    {

                        "_id": {"city": "$city", "duration": "$duration"},
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
                        "duration": {"$floor": {"$divide": [
                            {"$subtract": ["$final_time", "$init_time"]}, 60]}}
                    }
                    },
                   {"$group":
                    {

                        "_id": {"city": "$city", "duration": "$duration"},
                        "count": {"$sum": 1}
                    }
                    },
                   {"$sort":
                    {"_id": 1}
                    }
                   ]

pipeline_NewYork = [{"$match":
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
                        "duration": {"$floor": {"$divide": [
                            {"$subtract": ["$final_time", "$init_time"]}, 60]}}
                    }
                    },
                   {"$group":
                    {

                        "_id": {"city": "$city", "duration": "$duration"},
                        "count": {"$sum": 1}
                    }
                    },
                   {"$sort":
                    {"_id": 1}
                    }
                   ]

countPerCity_Pipeline=[{"$match":
        {
            "$or": [{'city':"Torino"},{"city":"Madrid"}],
            "init_time": {"$gte": startUnixTimeEU, "$lte": endUnixTimeEU},
            # "final_time": {
                # "$gte": startUnixTime, "$lte": endUnixTime}
        }},
        {
            "$group":
            {
                "_id":"$city",
                "count":{"$sum":1}
            }
        }
]

countNYC_Pipeline=[{"$match":
        {
            "city":"New York City",
            "init_time": {"$gte": startUnixTimeNY, "$lte": endUnixTimeNY},
            # "final_time": {
                # "$gte": startUnixTime, "$lte": endUnixTime}
        }},
        {
            "$group":
            {
                "_id":"$city",
                "count":{"$sum":1}
            }
        }
]

# Extract booking data
book_res_TO = list(Bookings_collection.aggregate(pipeline_Torino))
book_res_NY =list(Bookings_collection.aggregate(pipeline_NewYork))
book_res_MA = list(Bookings_collection.aggregate(pipeline_Madrid))
#Extract total counts of records per city
tot_booking = list(Bookings_collection.aggregate(countPerCity_Pipeline))
tot_bookingNY= list(Bookings_collection.aggregate(countNYC_Pipeline))

# Create dict to associate count to city
book_count={}
for c in tot_booking:
    book_count[c['_id']] = c['count'] #Create dict {torino:64312}
for c in tot_bookingNY:
    book_count[c['_id']] = c['count'] #Create dict 
    
#Extract parking data
park_res_TO = list(Parkings_collection.aggregate(pipeline_Torino))
park_res_NY =list(Parkings_collection.aggregate(pipeline_NewYork))
park_res_MA = list(Parkings_collection.aggregate(pipeline_Madrid))
tot_parking = list(Parkings_collection.aggregate(countPerCity_Pipeline))
tot_parkingNY=list(Parkings_collection.aggregate(countNYC_Pipeline))

# Create dict to associate count to city
park_count={}
for c in tot_parking:
    park_count[c['_id']] = c['count'] #Create dict {torino:63452}
for c in tot_parkingNY:
    park_count[c['_id']] = c['count'] #Create dict 

# Plot CDF bookings

plotCDF(book_res_TO, book_count['Torino'],'Torino')
plotCDF(book_res_MA, book_count['Madrid'],'Madrid')
plotCDF(book_res_NY, book_count['New York City'],'New York City',title="booking",xlabel="min[log]",show=True)

# Plot CDF parkings
plotCDF(park_res_MA, park_count['Madrid'],'Madrid')
plotCDF(park_res_TO, park_count['Torino'],'Torino')
plotCDF(park_res_NY, park_count['New York City'],'New York City',title="parking",xlabel="min[log]",show=True)

#####################################################################################################################################

# We take a single city to study

def groupbyDay(city,startUnixTime,endUnixTime):
    '''
    Function that plot the cdf for each weekday for the given city and time period
    '''
    
    
    # Create query to extract data for given city and time period
    pipeline = [{"$match":
                        {
                            "city": city,
                            "init_time": {"$gte": startUnixTime, "$lte": endUnixTime},
                            # "final_time": {
                                # "$gte": startUnixTime, "$lte": endUnixTime}
                        }
                        },
                       {"$project":
                        {
                            "city": "$city",
                            "dayOfWeek": { "$dayOfWeek": "$init_date" },
                            "duration": {"$floor": {"$divide": [
                                {"$subtract": ["$final_time", "$init_time"]}, 60]}}
                        }
                        },
                       {"$group":
                        {

                            "_id": {"city": "$city", "dayOfWeek":"$dayOfWeek","duration": "$duration"},
                            "count": {"$sum": 1}
                        }
                        },
                       {"$sort":
                        {"_id": 1}
                        }
                       ]
    countPerCityDay_Pipeline=[{"$match":
        {
            'city':city,
            "init_time": {"$gte": startUnixTime, "$lte": endUnixTime},
            # "final_time": {
                # "$gte": startUnixTime, "$lte": endUnixTime}
        }},
        {"$project":
                        {
                            "city": "$city",
                            "dayOfWeek": { "$dayOfWeek": "$init_date" }
                        }
        },
        {
            "$group":
            {
                "_id":"$dayOfWeek",
                "count":{"$sum":1}
            }
        },
        {
            "$sort":
            {
                "_id":1
                }
                }
    ]
    #Query the database
    day_park = list(Parkings_collection.aggregate(pipeline))
    day_book = list(Bookings_collection.aggregate(pipeline))
    
    count_park = list(Parkings_collection.aggregate(countPerCityDay_Pipeline))
    count_book = list(Bookings_collection.aggregate(countPerCityDay_Pipeline))

    # Create dictionary associating day-index to Day
    days = {1: 'Sunday',2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
    sliceDays = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
    # Plot parking
    for x in day_park:
        sliceDays[x["_id"]["dayOfWeek"]].append({"_id": x["_id"],"count":x["count"]})
    # plot park
    for key in days.keys():
        if key!=7:
            plotCDF(sliceDays[key],count_park[key-1]["count"],days[key])
        elif key==7:
            plotCDF(sliceDays[key],count_park[key-1]["count"],days[key],title="parking",xlabel="min[log]",show=True)
    
    # Re-initiate Slice Days        
    sliceDays = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
    # Plot booking
    for x in day_book:
        sliceDays[x["_id"]["dayOfWeek"]].append({"_id": x["_id"],"count":x["count"]})
    # plot park
    for key in days.keys():
        if key!=7:
            plotCDF(sliceDays[key],count_book[key-1]["count"],days[key])
        elif key==7:
            plotCDF(sliceDays[key],count_book[key-1]["count"],days[key],title="booking",xlabel="min[log]",show=True)
        
                   
                   
# We select Madrid as case study
city = "Madrid"
groupbyDay(city,startUnixTimeEU,endUnixTimeEU)
