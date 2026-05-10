
import pandas as pd
from random import randrange
import numpy as np
import math
import geopy
from geopy import distance
from geopy.distance import geodesic
from geopy.distance import great_circle 
import time

def donut_geomask(band_range, orig_point):
    """
    The solution below is based on:
    https://stackoverflow.com/questions/24427828/calculate-point-based-on-distance-and-direction

    This computes a destination (geomasked) point based on random bearing and distance 
        from origin point.

    Parameters:
    band_range (list of two tuples): first tuple is range of min distance 
        and second tuple is range of max distance in meters
    orig_point (tuple): Tuple of latitude and latitude of origin point

    Returns:
    geomask_dict: dictionary containing:
        destination latitude
        destination longitude
        bearing (in degrees)
        distance (in kilometers)
    """
    # get start time
    tick = time.perf_counter()

    # get random number between 0 and 360 and store as bearing
    bearing = randrange(0, 360)

    # get random number between lower_value and upper_value in meters 
    #    and store as distance in kilometers 
    lower, upper = band_range
    min_distance = randrange(lower[0],lower[1])
    max_distance = randrange(upper[0],upper[1])
    distance_kilometers = (randrange(min_distance, max_distance)) / 1000

    # convert orig_point to Shapely Point (lat, lon)
    origin = geopy.Point(orig_point)

    # create a geopy distance object (measurement unit in kilometers)
    d = distance.distance(kilometers=distance_kilometers)

    # store destination point of distance object in destination point
    destination = d.destination(origin, bearing)

    # get end time
    tock = time.perf_counter()
    elapsed_time = tock-tick

    # create return dictionary
    return_dictionary = {'latitude':destination.latitude,'longitude':destination.longitude,\
            'bearing':bearing, 'distance':distance_kilometers, 'elapsed_time':elapsed_time,\
             'final_band_range':(min_distance, max_distance)}

    return return_dictionary
    
def random_donuts_records(range_max, max_random):
    """    
    This returns a random list of numbers to use for randomly selecting which
    record to draw a donut for, to decrease the visual noise in a folium map
    of geomasked points (and amplify cognition of how donut geomasking works.

    Parameters:
    range_max (int): max number of records in dataframe to be displayed in folium 
    max_random (int): number of random donuts to display

    Returns:
    random_record_list (list): list of random records to display donuts for
    """
    total_rows = range_max
    random_record_list = []
    track_list = []
    counter = 1
    max_records = max_random
    for i in range(0, total_rows):
        random_number = randrange (0, total_rows)
        if random_number in track_list:
            continue
        else:
            random_record_list.append(random_number)
        track_list.append(random_number)
        counter = counter + 1
        if counter > max_records:
            break
    return random_record_list
    
def distance_between_points(orig, dest):
    """    
    This returns a dictionary of distance values in kilometers using geodesic 
        and great circle methods. The Vincenty distance method will be 
        deprecated from geopy soon (v2), so it was excluded from this class
        function.

    Parameters:
    orig (tuple): pair of floats representing lat, lon values of origin point 
    dest (tuple): pair of floats representing lat, lon values of destination point
        (computed after geomasking)

    Returns:
    return_dict (dict): dictionary of values representing distance computation using
        geodesic and great_circle methods of geopy. Distance values are in km and m.
    """
    geod_km = geodesic(orig, dest).km
    geod_m = geod_km*1000
    #geod_mi = geodesic(orig, dest).miles
    gcircle_km = great_circle(orig, dest).km
    gcircle_m = gcircle_km*1000
    #gcircle_mi = great_circle(orig, dest).miles
    return_dict = {'geodesic_km': geod_km, 'great_circle_km': gcircle_km,\
                  'geodesic_m':geod_m, 'great_circle_m': gcircle_m}
    return return_dict

def weighted_mean_center(weights, lats, lons):
    """    
    This computes the weighted mean center given a list each of weights, latitude and longitude.

    Parameters:
    weights (list of ints or floats): weighting factor for points 
        (see product_lat and product_lon below)
    lats (list of floats): list of latitudes
    lons (list of floats): list of longitudes

    Returns:
    mean_center_dictionary (dict): dictionary containing:
        mean center latitude
        mean center longitude
    """
    # create data frame from dictionary of lists
    
    df = pd.DataFrame({'weight':weights, 'lat':lats, 'lon':lons})

    # add weighted lat and lon columns
    df['product_lat'] = df['lat'] * df['weight']
    df['product_lon'] = df['lon'] * df['weight']

    # compute for mean lat and lon
    mean_lon = np.sum(df['product_lon'])/np.sum(df['weight'])
    mean_lat = np.sum(df['product_lat'])/np.sum(df['weight'])

    # create return dictionary
    mean_center_dictionary = {'latitude':mean_lat, 'longitude':mean_lon}

    return mean_center_dictionary
