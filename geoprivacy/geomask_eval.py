
import pandas as pd
from geoprivacy.donut_geomask import donut_geomask, distance_between_points, weighted_mean_center,\
    random_donuts_records
from geoprivacy.data_geomask import data_geomask
import time

def eval_wmc(df, iterations, band_range):
    """    
    This returns an evaluation dataframe containing performance measures from running
        several iterations of cholera_geomask(), weighted_mean_center() and 
        distance_betwen_points() on original and geomasked points. 
        
    Parameters:
        1. df (Pandas dataframe): Cholera dataframe containing deaths, lat and lon values
        2. iterations (int): Number of iterations to run cholera_geomask() and weighted_mean_center()
        3. band_range (tuple of integer tuples): Tuple of tuples of format ((low1, low2), (high1, high2)). 
            (low1, low2): tuple of integers (meters) representing randomization range for inner donut radius.
            (high1, high2) tuple of integers (meters) representing randomization range for outer donut radius.
    
    Returns:
        eval_df (dataframe): Evaluation dataframe with the following record structure:
            record = {'iteration':iteration, \
                      'geodesic_dist': d1['geodesic'], \
                      'great_circle_dist':d1['great_circle']}
    """    
    eval_df = pd.DataFrame()
    df1 = df
    for iteration in range(0,iterations):
        df2 = data_geomask(df=df1, band_range=band_range, reidentify=False)
        deaths = list(df2['DEATHS'])
        lats = list(df2['LAT'])
        lons = list(df2['LON'])
        gmlats = list(df2['gmLAT'])
        gmlons = list(df2['gmLON'])
        distance = df2['gmDISTANCE'].mean()
        mean_center = weighted_mean_center(weights=deaths, lats=lats, lons=lons)
        gm_mean_center = weighted_mean_center(weights=deaths, lats=gmlats, lons=gmlons)
        orig_lat = mean_center['latitude']
        orig_lon = mean_center['longitude']
        dest_lat = gm_mean_center['latitude']
        dest_lon = gm_mean_center['longitude']
        d1 = distance_between_points(orig=(orig_lat, orig_lon), dest=(dest_lat, dest_lon))
        record = {'iteration':iteration, \
                  'geodesic_dist': d1['geodesic_km'], \
                  'great_circle_dist':d1['great_circle_km'],
                  'distance': distance}
        eval_df = pd.concat([eval_df, pd.DataFrame([record])], ignore_index=True)
        eval_df['iteration'] = eval_df['iteration'].astype(int)
        print(record)
    return eval_df

def eval_reidentify(df, iterations, band_range, tries_range, min_distance_risk_range):
    """    
    This returns an evaluation dataframe containing performance measures from running
        several iterations of cholera_geomask() with reidentification of geomasked points. 
        
    Parameters:
        1. df (Pandas dataframe): Cholera dataframe containing deaths, lat and lon values
        2. iterations (int): Number of interations to run cholera_geomask() with reidentification (reverse geomask)
        3. band_range (tuple of integer tuples): Tuple of tuples of format ((low1, low2), (high1, high2)). 
            (low1, low2): tuple of integers (meters) representing randomization range for inner donut radius.
            (high1, high2) tuple of integers (meters) representing randomization range for outer donut radius.
        4. tries (int): Number of reidentification tries to implement
        5. min_distance_risk: Distance in meters between original and reverse geomasked points, 
            less than which reidentification is considered true
    
    Returns:
        eval_df (dataframe): Evaluation dataframe with the following record structure:

            record = {'iteration':iteration, \
                      'id_rate': id_rate, 
                      'id_runs': id_runs,
                      'id_tries': id_tries,
                      'lo_band': lo_band,
                      'hi_band': hi_band,
                      'band_width': band_width,
                      'min_distance_risk': min_distance_risk,
                      'hilo_ratio': hilo_ratio,
                      'effort': effort,
                      'process_record_time': elapsed_time2,
                      'geodesic_dist': d1['geodesic_km'], \
                      'great_circle_dist':d1['great_circle_km'],
                      'distance': distance}

    """    
    # get start time
    tick1 = time.perf_counter()
    
    eval_df = pd.DataFrame()
    df1 = df
    df2_list = []
    for iteration in range(0, iterations):
        for tries in range(tries_range[0], tries_range[1]):
            for min_distance_risk in range(min_distance_risk_range[0],min_distance_risk_range[1]):
                # get start time
                tick2 = time.perf_counter()
                df2 = data_geomask(df=df1, band_range=band_range, \
                                      reidentify=True, tries=tries, min_distance_risk=min_distance_risk)
                df2_list.append(df2)
                true_id = len(df2[df2['gmIDstatus']==True])
                false_id = len(df2[df2['gmIDstatus']==False])
                id_rate = (true_id * 100) / false_id
                id_runs = df2['gmIDruns'].mean()
                id_tries = df2['gmIDtries'].mean()
                lo_band = df2['gmBANDlo'].mean()
                hi_band = df2['gmBANDhi'].mean()
                hilo_ratio = hi_band / lo_band
                band_width = hi_band - lo_band
                total = len(df2)
                df2_true = df2[df2['gmIDstatus']==True]
                effort = (1.0 if len(df2_true)==0 else df2_true['gmIDeffort'].mean())
                # weighted mean center
                deaths = list(df2['DEATHS'])
                lats = list(df2['LAT'])
                lons = list(df2['LON'])
                gmlats = list(df2['gmLAT'])
                gmlons = list(df2['gmLON'])
                distance = df2['gmDISTANCE'].mean()
                mean_center = weighted_mean_center(weights=deaths, lats=lats, lons=lons)
                gm_mean_center = weighted_mean_center(weights=deaths, lats=gmlats, lons=gmlons)
                orig_lat = mean_center['latitude']
                orig_lon = mean_center['longitude']
                dest_lat = gm_mean_center['latitude']
                dest_lon = gm_mean_center['longitude']
                d1 = distance_between_points(orig=(orig_lat, orig_lon), dest=(dest_lat, dest_lon))
                tock2 = time.perf_counter()
                elapsed_time2 = tock2-tick2
                record = {'iteration':iteration, \
                          'id_rate': id_rate, 
                          'id_runs': id_runs,
                          'id_tries': id_tries,
                          'lo_band': lo_band,
                          'hi_band': hi_band,
                          'band_width': band_width,
                          'min_distance_risk': min_distance_risk,
                          'hilo_ratio': hilo_ratio,
                          'effort': effort,
                          'process_record_time': elapsed_time2,
                          'geodesic_dist': d1['geodesic_km'], \
                          'great_circle_dist':d1['great_circle_km'],
                          'distance': distance}
                eval_df = pd.concat([eval_df, pd.DataFrame([record])], ignore_index=True)
                print(record)
    eval_df['iteration'] = eval_df['iteration'].astype(int)
    df3 = pd.concat(df2_list)
    # get end time
    tock1 = time.perf_counter()
    elapsed_time1 = tock1-tick1

    return_dict = {'eval': eval_df, 'gm_df': df3, 'elapsed_time': elapsed_time1}
    return return_dict
