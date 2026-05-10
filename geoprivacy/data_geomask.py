import pandas as pd
import time
from geoprivacy.donut_geomask import donut_geomask, distance_between_points

#pd.set_option('precision', 6)

def data_geomask(df, band_range, reidentify=False, tries=1, min_distance_risk=20):
    """    
    This returns an extended dataframe based on the original. It adds analytic columns
        used for computing performance evaluations and reidentification. 
        Note: The function can be adapted for other dataframes.
    
    Parameters:
    df (Pandas dataframe): Cholera dataframe containing deaths, lat and lon values
    band_range (tuple of integer tuples): Tuple of tuples of format ((low1, low2), (high1, high2)). 
        (low1, low2): tuple of integers (meters) representing randomization range for inner donut radius.
        (high1, high2) tuple of integers (meters) representing randomization range for outer donut radius.
    reidentify (bool): Boolean representing use (or not) of reidentification algorithm. True=use
        reidentification, False=do not use reidentification.
    tries (integer): Number of tries to do for reidentification, defaults to 1
    min_distance_risk (integer): Distance in meters between original point and geomasked point as the 
        threshold to use for reidentification status. 
            reidentified=true if distance_between_points(origin, geomasked) <= min_distance_risk
            reidentified=false if distance_between_points(origin, geomasked) > min_distance_risk
    
    Returns:
    gm_df (dataframe): Modified copy of the original dataframe with the added and computed analytic columns
    
    """    
    gm_df = df

    # add columns to the deaths_df for 
    gm_df['gmLAT'] = 0.0
    gm_df['gmLON'] = 0.0
    gm_df['gmBEARING'] = 0.0
    gm_df['gmDISTANCE'] = 0.0
    gm_df['gmPERF_noID'] = 0.0
    gm_df['gmBANDlo'] = 0
    gm_df['gmBANDhi'] = 0
    if reidentify == True:
        gm_df['gmIDstatus'] = False
        gm_df['gmIDruns'] = 0
        gm_df['gmPERF_wID'] = 0.0
        gm_df['gmIDlat'] = 0.0
        gm_df['gmIDlon'] = 0.0
        gm_df['gmIDrate'] = 0.0
        tick = time.perf_counter()
    # loop through deaths_df and create geomasked_deaths_df
    for index, row in df.iterrows(): 

        # get random number between 500 and 1000 and store as distance
        band_range = band_range

        #set the point to geomask
        orig_point = (row['LAT'],row['LON'])

        gm_data = donut_geomask(band_range=band_range, orig_point=orig_point)

        #add the geomasked measures to the deaths_df
        gm_df.at[index,'gmLAT'] = gm_data['latitude']
        gm_df.at[index,'gmLON'] = gm_data['longitude']
        gm_df.at[index,'gmBEARING'] = gm_data['bearing']
        gm_df.at[index,'gmDISTANCE'] = gm_data['distance']
        gm_df.at[index,'gmPERF_noID'] = gm_data['elapsed_time']
        final_band_range = gm_data['final_band_range']
        gm_df.at[index,'gmBANDlo'] = final_band_range[0]
        gm_df.at[index,'gmBANDhi'] = final_band_range[1]
        gm_df.at[index,'gmIDtries'] = tries
        
        if reidentify == True:
            orig_point2 = (gm_data['latitude'], gm_data['longitude'])
            min_range = (min_distance_risk/1000 if min_distance_risk > 0 else final_band_range[0]/1000) 
            for i in range(0,tries):
                gm_data2 = donut_geomask(band_range=band_range, orig_point=orig_point2)
                p1 = orig_point
                p2 = (gm_data2['latitude'], gm_data2['longitude'])
                d1 = distance_between_points(orig=p1, dest=p2)
                if d1['geodesic_km'] < min_range:
                    gm_df.at[index, 'gmIDstatus'] = True
                    gm_df.at[index, 'gmIDlat'] = gm_data2['latitude']
                    gm_df.at[index, 'gmIDlon'] = gm_data2['longitude']
                    break
            # get end time
            tock = time.perf_counter()
            elapsed_time = tock-tick
            gm_df.at[index, 'gmIDruns'] = i+1 # actual runs needed to reidentify
            gm_df['gmIDtries'] = tries
            gm_df.at[index,'gmPERF_wID'] = elapsed_time
            gm_df['gmIDeffort'] = gm_df['gmIDruns'] / gm_df['gmIDtries']
    return gm_df
