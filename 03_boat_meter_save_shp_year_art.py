import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import contextily as ctx
import pandas as pd
import numpy as np

# Define the output directory for saving the plots
output_dir = 'saved_shapefiles'

# Read the shapefile
shapefile_path = 'shapefiles/algarve_polygons.shp'
algarve_polygons = gpd.read_file(shapefile_path)

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

df_all = pd.DataFrame()

# Iterate over each month
for month in range(1, 13):
    # Format the month value with leading zeros
    month_str = f'{month:02d}'
    print(month_str)

    df = pd.read_csv(f'MONICAP\Monthly\MONICAP_2021_{month_str}.csv')

    df_all = df_all.append(df, ignore_index=True)



df_all.drop(columns='Unnamed: 0', inplace=True)

df_all.drop_duplicates(inplace=True)

df_all.dropna(subset=['Gear'], inplace=True)

art_level = {'NK':1, 'GND':5 , 'DRH':5 , 'LTL':5, 'LLD' :5 , 'PS':9 , 'FPO':6 , 'OTB':9, 'GNS':6, 'LLS':5, 'LHP':4, 'DRB':7, 'GTR':8, 'SB':8, 'PTB':9, 'LNB':9}

df_all['art_level'] = [art_level[gear] for gear in df_all.Gear]

list_all = df_all.CFR.unique()

df_all = df_all[df_all.speed<5]

# Add 'month' and 'year' columns
df_all['month'] = df_all['GDH'].str.split('/').str[1].astype(int)
df_all['year'] = df_all['GDH'].str.split('/').str[2].str.split().str[0].astype(int)

list_slow = df_all.CFR.unique()

left_over = list(set(list_all) - set(list_slow))

# Create a GeoDataFrame from lat and lon columns
geometry = [Point(lon, lat) for lon, lat in zip(df_all['lon'], df_all['lat'])]
gdf = gpd.GeoDataFrame(df_all, geometry=geometry, crs=sea_data.crs)
# Iterate over each square in algarve_polygons
for i, square in enumerate(algarve_polygons.geometry):
    # Select points inside the current square
    points_inside_square = gdf[gdf.geometry.within(square)]

    mean_loa = np.mean(points_inside_square['LOA'])
    
    # Calculate the mean LOA value for the selected points
    mean_art_level = np.mean(points_inside_square['art_level'])
    #Count the signals sent inside square
    count = len(points_inside_square['art_level'])
    #Count the ships that went to that spot
    boat_count = len(points_inside_square.CFR.unique())
    
    # Handle NaN values
    if np.isnan(mean_loa):
        mean_loa = 0
    
    # Assign the mean LOA value to the 'mean_loa' column of the current square
    algarve_polygons.loc[i, 'mean_art_level'] = mean_art_level
    algarve_polygons.loc[i, 'count'] = count
    algarve_polygons.loc[i, 'boat_count'] = boat_count
    algarve_polygons.loc[i, 'time_diff'] = ''
    algarve_polygons.loc[i, 'gear_number'] = len(points_inside_square.Gear.unique())
    # Group points by ship and day
    grouped_points = points_inside_square.groupby(['CFR', 'day'])
    # Create time_diff column
    points_inside_square['time_diff'] = 0
    # Iterate over each group
    for (ship, day), group in grouped_points:
        # Sort the group by GDH (datetime) and reset the index
        group['hour'] = [pd.to_datetime(time_g) for time_g in group.GDH]
        group = group.sort_values('hour').reset_index(drop=True)
        # Calculate the time difference between consecutive points
        time_diff = group['hour'].diff().fillna(pd.Timedelta(seconds=1))
        # Convert time difference to hours rounded to the nearest hour
        time_diff_hours = time_diff.apply(lambda x: round(x.total_seconds() / 3600,2))
        # Adjust time spent values to be at least 1 hour
        for j in range(len(time_diff_hours)):
            if time_diff_hours[j]> 1:
                time_diff_hours[j] = 0.5
            elif time_diff_hours[j] <= 0:
                time_diff_hours[j] = 0.5
        # Assign the time spent for each ship on the current day
        points_inside_square.loc[
            (points_inside_square['CFR'] == ship) &
            (points_inside_square['day'] == day),
            'time_diff'
        ] = time_diff_hours.tolist()
        art_level = group['art_level']
    # Add the time_diff's for point in square
    boat_hours = points_inside_square.time_diff.sum()
    algarve_polygons.loc[i, 'boat_hours'] = np.round(boat_hours)
    if points_inside_square.empty:
        algarve_polygons.loc[i, 'level_hour_boat_meter'] = 0
        algarve_polygons.loc[i, 'mean_art_level_per_hour'] = 0
        algarve_polygons.loc[i, 'hour_boat_meter'] = 0
    else:
        boat_meter = (points_inside_square.LOA*points_inside_square.time_diff)
        art_level_hour_boat_meter = (boat_meter*points_inside_square.art_level)
        algarve_polygons.loc[i, 'mean_art_level_per_hour'] = (art_level_hour_boat_meter).sum()/boat_hours
        algarve_polygons.loc[i, 'art_level_hour_boat_meter'] = art_level_hour_boat_meter.sum()/100
        algarve_polygons.loc[i, 'hour_boat_meter'] = boat_meter.sum()/100
    if i % 10 == 0:
        print(i)
algarve_polygons['centroid'] = algarve_polygons.geometry.centroid

# Convert centroid column to string representation of coordinates
algarve_polygons['centroid'] = algarve_polygons['centroid'].apply(lambda p: p.wkt)
# Save the Algarve polygons as a shapefile
algarve_polygons.to_file(f'{output_dir}/algarve_polygons_2021.shp')