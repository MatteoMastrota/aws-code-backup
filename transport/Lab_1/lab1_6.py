import pymongo as pm  # import MongoClient only
import matplotlib
import pandas as pd
import geopandas
import pprint
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
import math
import jsonify
import contextily as ctx
from datetime import date, datetime, timezone
from sklearn import preprocessing

print_spacer = 150
client = pm.MongoClient('bigdatadb.polito.it', ssl=True,
                        authSource='carsharing', tlsAllowInvalidCertificates=True)
db = client['carsharing']  # Choose the DB to use
# , mechanism='MONGODB-CR') #authentication
db.authenticate('ictts', 'Ictts16!')

# https://stackoverflow.com/questions/20638006/convert-list-of-dictionaries-to-a-pandas-dataframe
# http://maps.stamen.com/terrain/#9/40.8959/-73.6002
# Bookings_collection = db['PermanentBookings']  # Collection for Car2go to use


# startUnixTime_datetime = (datetime(2017, 11, 1, tzinfo=timezone.utc))
# startUnixTime = startUnixTime_datetime.timestamp()
# endUnixTime_datetime = (datetime(2017, 11, 30, tzinfo=timezone.utc))
# endUnixTime = endUnixTime_datetime.timestamp()
# pippo = (startDate - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
# print(pippo)
# list_res = list(res)
# df = pandas.DataFrame(list_res)
# {'_id': {'city': 'Torino', 'duration': 11036.0}, 'count': 1}
# print((list_res[0]), type(list_res[0]))
"""

pipeline_OG = [{"$match":
                {
                    "$or": [{"city": "Torino"}, {"city": "New York City"}, {"city": "Madrid"}],
                    "init_time": {"$gte": startUnixTime, "$lte": endUnixTime},
                    "final_time": {
                        "$gte": startUnixTime, "$lte": endUnixTime}
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
pipeline_Torino = [{"$match":
                    {
                        "city": "Torino",
                        "init_time": {"$gte": startUnixTime, "$lte": endUnixTime},
                        "final_time": {
                            "$gte": startUnixTime, "$lte": endUnixTime}
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
res_to = Bookings_collection.aggregate(pipeline_Torino)
lista_torino = list(res_to)
tot_to = len(lista_torino)
# {'_id': {'city': 'Torino', 'duration': 0.0}, 'count': 6285}
print(lista_torino[0])
print(tot_to)

durata = []
count = []
counter = 0  # lista_torino[0]['count']
for x in lista_torino:

    durata.append(x['_id']['duration'])
    count.append((x['count'] / 63452 + counter))
    counter = count[-1]


print(durata)
print(count)
plt.plot(durata, count)
plt.show()



"""


##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################


# POINT 6
"""
Consider one city of your collection and check the position of the cars when parked,
and compute the density of cars during different hours of the day.

    a. Plot the parking position of cars in different times using google map.
    You can use the Google Fusion Tables to get the plot in minutes
    -- check https://support.google.com/fusiontables/answer/2527132?hl=en.

    b. Divide the area using a simple squared grid of approximatively 500mx500m
    and compute the density of cars in each area, and plot the results using
    a heatmap (i.e., assigning a different colour to each square to represent the densities of cars).

    c. Compute then the O-D matrix, i.e., the number of rentals starting in
    area O and ending in area D. Try to visualize the results in a meaningful way.
"""

##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################


"""
For point A
I want to get all the parked cars for a certain time and plot them on a map,
and then do this for the various times of the day. Suppose hourly grouping
When querying the db i will ask for
-coordinates of the car
-start time of parking
-parking duration

i also have to divide the time into intervals

query:
Considering the city of new york -- match operation

The coordinates are
 "coordinates" : [
                    16.34585, # longitude
                    48.22522  # latitude
                ]
longitude |   {$arrayElemAt: [ "$origin_destination.coordinates", 0]},
latitude -    {$arrayElemAt: [ "$origin_destination.coordinates", 1]}


do i have to compile all parkings for a cetain hour?
so to then see over the whole time period which hours have which densities of cars?
this means grouping by hour

"""

"""
query_6a

db.PermanentParkings.aggregate([
                                { $match:
                                    {
                                        city: "New York City",
                                        init_time: { $gte: startUnixTime, $lte: endUnixTime }
                                    }
                                },
                                { $project:
                                        {
                                            _id: 0,
                                            init_time: 1,
                                            duration: {$subtract: ["$final_time", "$init_time"] },
                                            lon: {$arrayElemAt: [ "$loc.coordinates", 0]},
                                            lat: {$arrayElemAt: [ "$loc.coordinates", 1]}
                                        }
                                },
                            ])
"""
##########################################################################################
#####################################   CODE     #########################################
##########################################################################################

# PermanentParkings_Collection = db['PermanentParkings']
# # class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
# startUnixTime_datetime = (datetime(2017, 11, 1, tzinfo=timezone.utc))
# startUnixTime = startUnixTime_datetime.timestamp()
# print("Start time", startUnixTime, startUnixTime_datetime)
# endUnixTime_datetime = (datetime(2017, 11, 2, tzinfo=timezone.utc))
# endUnixTime = endUnixTime_datetime.timestamp()
# print("End time", startUnixTime, endUnixTime_datetime)

# pipeline_6a = [
#     {"$match":
#      {
#          "city": "New York City",
#          "init_time": {"$gte": startUnixTime, "$lte": endUnixTime}
#      }

#      },
#     {"$project": {
#         "_id": 0,
#         "init_time": 1,
#         "duration": {"$subtract": ["$final_time", "$init_time"]},
#         "lon": {"$arrayElemAt": ["$loc.coordinates", 0]},
#         "lat": {"$arrayElemAt": ["$loc.coordinates", 1]}
#     }
#     }
# ]

# somepoints_nyc = PermanentParkings_Collection.aggregate(pipeline_6a)

# # https://stackoverflow.com/questions/20638006/convert-list-of-dictionaries-to-a-pandas-dataframe
# # http://maps.stamen.com/terrain/#9/40.8959/-73.6002


# df_points = pd.DataFrame(somepoints_nyc)

# """
# For the syntax problem
# """
# # https://stackoverflow.com/questions/59596835/open-street-map-pyproj-how-to-solve-syntax-issue
# geo_df = geopandas.GeoDataFrame(
#     df_points,
#     crs={'init': 'epsg:4326'},
#     # geometry=df_points['coords'].apply(Point),
#     geometry=geopandas.points_from_xy(df_points.lon, df_points.lat)
# ).to_crs(epsg=3857)

# df = geopandas.read_file(geopandas.datasets.get_path('nybb'))
# df = df.to_crs(epsg=3857)

# ax = df.plot(figsize=(10, 10), alpha=0.5, edgecolor='k')
# ctx.add_basemap(ax)
# geo_df.plot(ax=ax, color='red')

# plt.show()
##########################################################################################
# {
#         $group: { // now compute the totals, per city
#             _id: "$hour",


#             hour: { $hour: "$init_date" },
#             duration: {$subtract: ["$final_time", "$init_time"] },
#             lon: {$arrayElemAt: [ "$loc.coordinates", 0]},
#             lat: {$arrayElemAt: [ "$loc.coordinates", 1]},
#             //avg_time: {$avg: "$duration"},
#         }
#     }

##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################

"""
POINT B
QUERY FOR ALL PARKINGS IN NYC AND THEIR COORDINATES
db.PermanentParkings.aggregate([
    {
        $match:
            {
                city: "New York City",
                init_time: { $gte: startUnixTime, $lte: endUnixTime }
            }
    },

    {
        $project: {
            _id: 0,
            lon: {$arrayElemAt: [ "$loc.coordinates", 0]},
            lat: {$arrayElemAt: [ "$loc.coordinates", 1]},

        }
    },
    {
        "$group":{
            "_id": {"hour":"$hour"},
        }
    }

])
"""
####################################################################################
####################################################################################
##################################    START CODE    ################################
####################################################################################
####################################################################################


####################################################################################
####################################################################################
##################################    QUERY DB     #################################
####################################################################################
####################################################################################
# PermanentParkings_Collection = db['PermanentParkings']

# pipeline_6b = [
#     {
#         "$match":
#         {
#             "city": "New York City",
#         }
#     },
#     {
#         "$project": {
#             "_id": 0,
#             "city": "$city",
#             "hour": {"$hour": "$init_date"},
#             "day_week": {"$dayOfWeek": "$init_date"},
#             # "lat": {"$trunc": {"$arrayElemAt": ["$loc.coordinates", 1]}},
#             # "lon": {"$trunc": {"$arrayElemAt": ["$loc.coordinates", 0]}}
#             "lat": {"$arrayElemAt": ["$loc.coordinates", 1]},
#             "lon": {"$arrayElemAt": ["$loc.coordinates", 0]}


#         }
#     }
# ]

# # Query to get all parkings in NYC
# points_nyc = PermanentParkings_Collection.aggregate(pipeline_6b)
# df_points = pd.DataFrame(points_nyc)
# df_points.to_csv('df_points.csv', index=False)
####################################################################################
####################################################################################
################################    END  QUERY DB     ##############################
####################################################################################
####################################################################################


####################################################################################
####################################################################################
################################    CREATING GRID     ##############################
####################################################################################
####################################################################################
# df_points = pd.read_csv('df_points.csv')

# # After retrieving all the coordinates filter for erroneous data
# lat_min = 40.4900
# lat_max = 40.9200
# long_min = -74.2700
# long_max = -73.7100


# # DataFrame for the filtered points
# filtered_points = df_points.loc[
#     (df_points['lat'] != 0)
#     & (df_points['lon'] != 0)
#     & (lat_min < df_points['lat'])
#     & (df_points['lat'] < lat_max)
#     & (long_min < df_points['lon'])
#     & (df_points['lon'] < long_max)
# ]
# print(print_spacer * '+')
# print('Filtered points DataFrame')
# print(filtered_points.head(5))

# # Creating the GeoDataFrame for the filtered points BRENDAN
# filtered_points_gdf = geopandas.GeoDataFrame(
#     filtered_points, geometry=geopandas.points_from_xy(filtered_points.lat, filtered_points.lon))

# # print(print_spacer * '+')
# # print('Filtered points GeoDataFrame')
# # print(filtered_points_gdf.head(5))

# # CIOCIO
# # filtered_points_gdf = geopandas.GeoDataFrame(filtered_points, geometry=filtered_points.loc[:, ["lon", "lat"]]
# #                                              .apply(lambda p: Point(p[0], p[1]), axis=1))
# # filtered_points_gdf.crs = {"init": "epsg:4326"}
# # filtered_points_gdf = filtered_points_gdf.to_crs({"init": "epsg:3857"})
# # filtered_points_gdf.loc[:, "lon"] = filtered_points_gdf.geometry.apply(
# #     lambda p: p.x)
# # filtered_points_gdf.loc[:, "lat"] = filtered_points_gdf.geometry.apply(
# #     lambda p: p.y)


# # https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
# # origin = (latitude, longitude)
# # dist_NS = geodesic((lat_max, long_max), (lat_max, long_min)).meters
# # dist_WE = geodesic((lat_max, long_min), (lat_min, long_min)).meters
# # print(dist_NS, dist_WE)

# # CALCULATING NUMBER OF ROWS AND COLUMNS FOR THE GRID ON THE CITY
# long_boi = 0.0059
# lat_boi = 0.0045
# row_of_grid = int(math.ceil(abs((lat_max - lat_min)) / lat_boi))
# col_of_grid = int(math.ceil((long_max - long_min) / long_boi))

# print("cols for grid", col_of_grid, "rows for grid", row_of_grid)


# def calculate_new_lat_long(lat_init, dy_lat, long_init, dx_long):
#     """
#     Function to calculate new latitude and longitude given initial latitude and longitude
#     by adding a delta in meters.
#     new_latitude, new_longitude = calculate_new_lat_long(lat_min, long_min)
#     """
#     r_earth = 6371000.0000
#     pi = 3.1415
#     new_latitude = lat_init + (dy_lat / r_earth) * (180 / pi)
#     new_longitude = long_init + (dx_long / r_earth) * (180 / pi) / \
#         math.cos(lat_init * pi / 180)

#     lat_to_return = '{0:.4f}'.format(new_latitude)
#     long_to_return = '{0:.4f}'.format(new_longitude)

#     return float(lat_to_return), float(long_to_return)


# def find_grid_polygon(centre_lat, centre_long):
#     """
#     Function that given a latitude and longitude as centre, calculates the Square Polygon that has
#     as center the passed coordinates.
#     """
#     UL = (calculate_new_lat_long(centre_lat, 250, centre_long, -250))
#     UR = (calculate_new_lat_long(centre_lat, 250, centre_long, 250))
#     BL = (calculate_new_lat_long(centre_lat, -250, centre_long, -250))
#     BR = (calculate_new_lat_long(centre_lat, -250, centre_long, 250))
#     poll = Polygon([BL, UL, UR, BR])
#     return poll


# # CREATING GRID OF POLYGONS
# data_for_grid = []
# ids = []
# lat_centre = []
# long_centre = []
# centre_of_zones = []
# latitudes_hm = []
# longitudes_hm = []
# start_lat = lat_max  # upper left
# start_long = long_min

# for r in range(0, row_of_grid + 1):

#     # new_latitude, new_longitude = calculate_new_lat_long(
#     #     lat_max, -500 * (r), long_min, 0)
#     # if new_latitude not in latitudes_hm:
#     #     latitudes_hm.append(new_latitude)
#     # # start_lat = new_latitude
#     # # start_long = new_longitude
#     # print(new_latitude, new_longitude)

#     for c in range(0, col_of_grid + 1):
#         # if new_longitude not in longitudes_hm:
#         #     longitudes_hm.append(new_longitude)
#         new_latitude, new_longitude = calculate_new_lat_long(
#             start_lat, -500 * r, start_long, 500 * c)
#         diz = {

#             'polygon': find_grid_polygon(new_latitude, new_longitude)
#             # 'lat_centre': new_latitude,
#             # 'long_centre': new_longitude,
#             # 'n_cars': 0,
#             # 'id': str(r) + '-' + str(c)
#         }

#         data_for_grid.append(diz)
#         ids.append(str(r) + '-' + str(c))
#         centre_of_zones.append([new_latitude, new_longitude])
#         lat_centre.append(new_latitude)
#         long_centre.append(new_longitude)

# grid_df = pd.DataFrame(data=data_for_grid)

# print(print_spacer * '+')
# print('Grid DataFrame')
# print(grid_df.head(5))


# # CREATING DATAFRAME FOR LATITUDE AND LONGITUDE FOR HEATMAP
# # lat_long_df_hm = pd.DataFrame()
# # print(len(latitudes_hm), len(longitudes_hm))
# # lat_long_df_hm['lat_hm'] = latitudes_hm
# # lat_long_df_hm['long_hm'] = longitudes_hm


# # CREATING GRID GEODATAFRAME AND ADDING RELEVANT COLUMNS
# grid_df_gdf = geopandas.GeoDataFrame(geometry=grid_df['polygon'])

# grid_df_gdf["zone_id"] = ids
# grid_df_gdf['zone_centre'] = centre_of_zones
# grid_df_gdf['lat_centre'] = lat_centre
# grid_df_gdf['long_centre'] = long_centre
# # grid_df_gdf.crs = {"init": "epsg:3857"}

# print(print_spacer * '+')
# print('Grid GeoDataFrame')
# print(grid_df_gdf.head(10))

# # SAVING GRID GEODATAFRAME AS CSV
# grid_df_gdf.to_csv('grid_df_gdf.csv')

# ########################
# ## END CREATING GRID  ##
# ########################

# # SPATIALLY JOINING THE GRID AND POINTS TO FIND MATCHES
# grid_and_points_gdf = geopandas.sjoin(
#     filtered_points_gdf, grid_df_gdf, how="right", op='within')
# grid_and_points_gdf['num_cars_total'] = 1

# print(print_spacer * '+')
# print('Grid And Points GeoDataFrame')
# print(grid_and_points_gdf.head(10))
# # #      index_left           city  hour  day_week       lat  ...  zone_id                               zone_centre lat_centre long_centre  num_cars_total
# # # 1675     99882.0  New York City  16.0       2.0  40.84188  ...    17-60   [40.84355540895071, -73.91335729383731]  40.843555  -73.913357               1
# # # 1975     88719.0  New York City   3.0       4.0  40.83034  ...    20-75  [40.830065187000834, -73.82428732166294]  40.830065  -73.824287               1
# # # 2434    688547.0  New York City  15.0       6.0  40.80952  ...    25-59   [40.80758148375104, -73.91949150887747]  40.807581  -73.919492               1

# # SAVING GRID AND POINTS TO CSV
# grid_and_points_gdf.to_csv('grid_and_points_gdf.csv', index=False)

# ##################################
# # END CREATING GRID AND POINTS  ##
# ##################################

# grid_and_points_gdf = pd.read_csv('grid_and_points_gdf.csv')

# grid_and_points_gdf_grouped = grid_and_points_gdf.groupby(
#     ['lat_centre', 'long_centre'], as_index=False)['num_cars_total'].sum()
# print(print_spacer * '+')
# print('Grid And Points GeoDataFrame GROUPED')
# print(grid_and_points_gdf_grouped.head(10))
# # Grid And Points GROUPED GeoDataFrame
# #    lat_centre  long_centre  num_cars_total
# # 0   40.497306   -74.270000               1
# # 1   40.497306   -74.264087               1
# # 2   40.497306   -74.258173               1

# grid_and_points_gdf_grouped.to_csv(
#     'grid_and_points_gdf_grouped.csv', index=False)

####################################################################################
####################################################################################
################################### END GROUPING ###################################
####################################################################################
####################################################################################


####################################################################################
####################################################################################
#####################################  SEABORN  ####################################
####################################################################################
####################################################################################
heatmap_df = pd.read_csv('grid_and_points_gdf_grouped.csv')
heatmap_df['num_cars_total'] = heatmap_df['num_cars_total'] - 1
print(print_spacer * '+')
print('Heatmap DataFrame')
print(heatmap_df.head(10))
##########################################
print(print_spacer * '+')
print('Heatmap DataFrame SHAPE')
print(heatmap_df.shape)
##########################################
print(print_spacer * '+')
print('Heatmap DataFrame DTYPES')
print(heatmap_df.dtypes)
##########################################
print(print_spacer * '+')
print('Heatmap DataFrame UNIQUE')
print(heatmap_df.nunique(axis=0))
##########################################
heatmap_df.to_csv('heatmap.csv', index=False)

##########################################
heatmap_df = heatmap_df.pivot_table(values='num_cars_total', index=[
    'lat_centre'], columns=['long_centre'], aggfunc=np.sum)
heatmap_df = heatmap_df.sort_index(ascending=False)
print(print_spacer * '+')
print('Heatmap DataFrame PIVOT')
print(heatmap_df.head(10))
##########################################
print(print_spacer * '+')
print('Heatmap DataFrame SHAPE')
print(heatmap_df.shape)
heatmap_df.to_csv('pivot.csv')


sns.heatmap(heatmap_df, linewidths=.5, square=True, cmap='inferno_r')
plt.savefig('heatmap.jpg', dpi=300)
plt.show()
# #################################  SEABORN EXAMPLE 1 ##########################
# Index = ['aaa', 'bbb', 'ccc', 'ddd', 'eee']
# Cols = ['A', 'B', 'C', 'D']
# df = pd.DataFrame(abs(np.random.randn(5, 4)), index=Index, columns=Cols)
# sns.heatmap(df, annot=True)
# plt.savefig('cols.png')

# #################################  SEABORN EXAMPLE 2 ##########################

# flights = sns.load_dataset("flights")

# print(print_spacer * '+')
# print('flights DataFrame')
# print(flights.head(10))

# print(print_spacer * '+')
# print('flights DataFrame DTYPES')
# print(flights.dtypes)

# flights = flights.pivot("month", "year", "passengers")

# print(print_spacer * '+')
# print('flights DataFrame PIVOT')
# print(flights.head(10))

# # ax = sns.heatmap(flights)

####################################################################################
####################################################################################
###################################  END SEABORN  ##################################
####################################################################################
####################################################################################

####################################################################################
####################################################################################
######################### PLOTTING ZONE CENTRES POINTS ON MAP ######################
####################################################################################
####################################################################################
# READING CSV WITH DATA FOR HEATMAP LAT LON N-CARS
df_points = pd.read_csv('heatmap.csv')
#      lat_centre   long_centre      num_cars_total
# 0     40.4883     -74.2700               0
# 1     40.4883     -74.2640               0
# normalized_df = (df - df.mean()) / df.std()
# df_points['normalised_cars'] = (df_points['num_cars_total'] -
#                                 df_points['num_cars_total'].mean()) / df_points['num_cars_total'].std()

# normalized_df=(df-df.min())/(df.max()-df.min())
df_points['normalised_cars'] = ((df_points['num_cars_total'] - df_points['num_cars_total'].min()) / (
    df_points['num_cars_total'].max() - df_points['num_cars_total'].min())) * 300


geo_df = geopandas.GeoDataFrame(
    df_points,
    crs={'init': 'epsg:4326'},
    geometry=geopandas.points_from_xy(
        df_points.long_centre, df_points.lat_centre)
).to_crs(epsg=3857)

# Getting the provided NYC and Boroughs map
df = geopandas.read_file(geopandas.datasets.get_path('nybb'))
df = df.to_crs(epsg=3857)  # changhing to mercatore map

ax = df.plot(figsize=(20, 20), alpha=0.7, edgecolor='k')
ctx.add_basemap(ax)
geo_df.plot(ax=ax, color='red', markersize='normalised_cars')
plt.savefig('gridOnNYBB.png', dpi=300)

plt.show()

##################################    END CODE    ################################


##################################################################################
#################################  SEABORN TEST ##################################
# plt.figure(figsize=(9, 9))

# test_lat_lon_ncars = {'lat': [lat_max, lat_min, lat_max, lat_min, new_latitude],
#                       'lon': [long_max, long_max, long_min, long_min, new_longitude],
#                       'n_cars': [10, 20, 30, 40, 50]}
# phase_1_2 = pd.DataFrame(data=test_lat_lon_ncars)
# pivot_table = phase_1_2.pivot('lat', 'lon', 'n_cars')
# plt.xlabel('lon', size=15)
# plt.ylabel('lat', size=15)
# plt.title('n_cars', size=15)
# sns.heatmap(pivot_table, annot=True, fmt=".1f",
#             linewidths=.5, square=True, cmap='inferno_r')
# plt.show()
##################################################################################


##################################################################################
###################################  PLOTLY  #####################################
# import plotly.express as px
# df = px.data.carshare()
# print(df.head(5))
# # fig = px.density_heatmap(df, y="centroid_lat",
# #                          x="centroid_lon",z="car_hours", nbinsx=55, nbinsy=55)
# fig = px.density_mapbox(df, lat='centroid_lat', lon='centroid_lon', z='car_hours',
#                         zoom=0,
#                         mapbox_style="stamen-terrain")
# fig.show()
###################################  PLOTLY  #####################################
# import plotly.express as px

# fig = px.density_heatmap(df, y="centroid_lat",
#                          x="centroid_lon",z="car_hours", nbinsx=55, nbinsy=55)
# fig = px.density_mapbox(heatmap_df, lat='lat_centre', lon='long_centre', z='num_cars_total',
#                         zoom=0,
#                         mapbox_style="stamen-terrain")
# fig = px.imshow(heatmap_df)

# fig.show()
###################################  END PLOTLY  #################################


###################################  CIOCIOLA  ###################################

# def get_parkings_gdf(parkings):
#     gdf = gpd.GeoDataFrame(parkings, geometry=parkings.loc[:, ["longitude", "latitude"]]
#                            .apply(lambda p: Point(p[0], p[1]), axis=1))
#     gdf.crs = {"init": "epsg:4326"}
#     gdf = gdf.to_crs({"init": "epsg:3857"})
#     gdf.loc[:, "longitude"] = gdf.geometry.apply(lambda p: p.x)
#     gdf.loc[:, "latitude"] = gdf.geometry.apply(lambda p: p.y)
#     return gdf


# def get_parking_gs(parking):
#     parking.loc["geometry"] = Point(parking.longitude, parking.latitude)
#     gs = gpd.GeoSeries(parking)
#     gs.crs = {"init": "epsg:3857"}
#     return gs

# def get_city_grid(locations, bin_side_length):

#     x_min, y_min, x_max, y_max = locations.total_bounds
#     width = bin_side_length
#     height = bin_side_length
#     rows = int(np.ceil((y_max - y_min) / height))
#     cols = int(np.ceil((x_max - x_min) / width))
#     x_left = x_min
#     x_right = x_min + width
#     polygons = []
#     for i in range(cols):
#         y_top = y_max
#         y_bottom = y_max - height
#         for j in range(rows):
#             polygons.append(Polygon([(x_left, y_top),
#                                      (x_right, y_top),
#                                      (x_right, y_bottom),
#                                      (x_left, y_bottom)]))
#             y_top = y_top - height
#             y_bottom = y_bottom - height
#         x_left = x_left + width
#         x_right = x_right + width
#     grid = gpd.GeoDataFrame({"geometry": polygons})

#     grid["zone_id"] = range(len(grid))
#     grid.crs = {"init": "epsg:3857"}

#     return grid


# def apply_binning(self, bin_side_length):

#     self.bin_side_length = bin_side_length
#     self.grid = get_city_grid(self.parkings_gdf, self.bin_side_length)

#     return self.grid

# def map_points_to_city_grid(self):

#     self.bookings_origins_gdf = gpd.sjoin(self.bookings_origins_gdf,
#                                           self.grid.drop("zone_id", axis=1),
#                                           how='left',
#                                           op='within').rename({"index_right": "origin_id"}, axis=1)

#     self.bookings_destinations_gdf = gpd.sjoin(self.bookings_destinations_gdf,
#                                                self.grid.drop(
#                                                    "zone_id", axis=1),
#                                                how='left',
#                                                op='within').rename({"index_right": "destination_id"}, axis=1)

#     self.parkings_gdf = gpd.sjoin(self.parkings_gdf,
#                                   self.grid.drop("zone_id", axis=1),
#                                   how='left',
#                                   op='within').rename({"index_right": "zone_id"}, axis=1)

#     self.bookings["origin_id"] =
#         self.bookings_origins_gdf.origin_id
#         .dropna().astype(int)

#     self.bookings["destination_id"] =
#         self.bookings_destinations_gdf.destination_id
#         .dropna().astype(int)

#     self.parkings["zone_id"] =
#         self.parkings_gdf.zone_id
#         .dropna().astype(int)

#     return self.bookings_origins_gdf,
#         self.bookings_destinations_gdf,
#         self.parkings_gdf
###################################  END CIOCIOLA  ###############################

########################################################
##################### FROM MEDIUM ######################

# https://medium.com/@m_vemuri/create-a-geographic-heat-map-of-the-city-of-toronto-in-python-cd2ae0f8be55
# nyc_bb = 'nyc_shapefiles/Borough_Boundaries/geo_export_fa3dfddb-85fe-4b44-bc21-48e12f88c3b8.shp'
# regions = geopandas.read_file(nyc_bb)
# # print(regions.head(4))
# # print(regions.columns)
# regions.plot(figsize=(10, 10))
# plt.show()

##################### END MEDIUM ######################
########################################################
