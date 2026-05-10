#!/usr/bin/env python3

import pandas as pd
from random import randrange
import numpy as np
import math
import geopy
from geopy import distance
from geopy.distance import geodesic
from geopy.distance import great_circle 
import time
class GeomaskedPoint:
    
    def __init__():
        pass
    
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