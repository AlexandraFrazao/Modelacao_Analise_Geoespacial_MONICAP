import geopandas as gpd
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
import contextily as ctx
import pandas as pd
import numpy as np
from matplotlib.cm import ScalarMappable
import seaborn as sns

month = '02'

df = pd.read_csv(f'MONICAP\Monthly\MONICAP_2022_{month}.csv')

df.drop(columns='Unnamed: 0', inplace=True)

df.drop_duplicates(inplace=True)

df.dropna(subset=['Gear'], inplace=True)

df = df[df.speed<5]


# Read the shapefile
shapefile_path = 'shapefiles/algarve_polygons.shp'
algarve_polygons = gpd.read_file(shapefile_path)

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)


# Create a plot
fig, ax = plt.subplots(figsize=(10, 10))


# Define the extent of the grid
min_x, min_y, max_x, max_y = algarve_polygons.total_bounds



# Plot the Algarve polygons with a different color
algarve_polygons.plot(ax=ax, edgecolor='green', linewidth=1, facecolor='red', alpha=0.7)

sea_data.plot(ax=ax, facecolor='none')

merged_algarve = algarve_polygons.unary_union

# Create a GeoDataFrame from lat and lon columns
geometry = [Point(lon, lat) for lon, lat in zip(df['lon'], df['lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=sea_data.crs)

# Filter the GeoDataFrame for the Algarve region
algarve_gdf = gdf[gdf.geometry.within(merged_algarve)]

# Print the resulting GeoDataFrame
print(algarve_gdf)

# Plot the boundary
gpd.GeoSeries(merged_algarve).plot(ax=ax, color='none', linewidth=1, facecolor='none')

# Add basemap using Contextily
ctx.add_basemap(ax, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Set the plot extent
ax.set_xlim(min_x-1, max_x+1)
ax.set_ylim(min_y-1, max_y+1)

# Display the plot
#plt.show()




# Iterate over each square in algarve_polygons
for i, square in enumerate(algarve_polygons.geometry):
    # Select points inside the current square
    points_inside_square = gdf[gdf.geometry.within(square)]
    
    # Calculate the mean LOA value for the selected points
    mean_loa = np.mean(points_inside_square['LOA'])

    #Count the signals sent inside square
    count = len(points_inside_square['LOA'])

    #Count the ships that went to that spot
    boat_count = len(points_inside_square.CFR.unique())
    
    # Handle NaN values
    if np.isnan(mean_loa):
        mean_loa = 0
    
    # Assign the mean LOA value to the 'mean_loa' column of the current square
    algarve_polygons.loc[i, 'mean_loa'] = mean_loa
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

    # Add the time_diff's for point in square
    boat_hours = points_inside_square.time_diff.sum()
    algarve_polygons.loc[i, 'boat_hours'] = np.round(boat_hours)
    if points_inside_square.empty:
        algarve_polygons.loc[i, 'mean_loa_per_hour'] = 0
        algarve_polygons.loc[i, 'hour_boat_meter'] = 0
    else:
        mean_loa_per_hour = (points_inside_square.LOA*points_inside_square.time_diff)
        algarve_polygons.loc[i, 'mean_loa_per_hour'] = mean_loa_per_hour.sum()/boat_hours
        algarve_polygons.loc[i, 'hour_boat_meter'] = mean_loa_per_hour.sum()/100

algarve_polygons['centroid'] = algarve_polygons.geometry.centroid


##########################################################################
##########################################################################
##########################################################################
algarve_polygons['boat_hours'] = algarve_polygons['boat_hours']


cmap='coolwarm'

import matplotlib.gridspec as gridspec

cmap = 'coolwarm'

fig = plt.figure(figsize=(15, 15))
gs = gridspec.GridSpec(2, 4, width_ratios=[0.05, 1, 1, 0.05], height_ratios=[1, 1])

cbar_ax = plt.subplot(gs[0])
ax1 = plt.subplot(gs[1])
ax2 = plt.subplot(gs[2])
cbar_ax2 = plt.subplot(gs[3])
cbar_ax3 = plt.subplot(gs[4])
ax3 = plt.subplot(gs[5])
ax4 = plt.subplot(gs[6])
cbar_ax4 = plt.subplot(gs[7])

padding = 0.5
ax1.set_xlim(min_x - padding, max_x + padding)
ax1.set_ylim(min_y - padding, max_y + padding)
ax2.set_xlim(min_x - padding, max_x + padding)
ax2.set_ylim(min_y - padding, max_y + padding)
ax3.set_xlim(min_x - padding, max_x + padding)
ax3.set_ylim(min_y - padding, max_y + padding)
ax4.set_xlim(min_x - padding, max_x + padding)
ax4.set_ylim(min_y - padding, max_y + padding)

algarve_polygons.plot(ax=ax1, column='hour_boat_meter', cmap=cmap, linewidth=1, edgecolor='black')
algarve_polygons.plot(ax=ax1, color='none', linewidth=0.2, edgecolor='black')
sm = ScalarMappable(cmap=cmap)
sm.set_array(algarve_polygons['hour_boat_meter'])

sns.kdeplot(
    ax=ax2,
    x=algarve_polygons['centroid'].x,
    y=algarve_polygons['centroid'].y,
    levels=np.linspace(0.01, 1, 100),
    weights=algarve_polygons['boat_count'],
    fill=True,
    cmap=cmap,
    alpha=0.5
)

algarve_polygons.plot(ax=ax3, column='boat_hours', cmap=cmap, linewidth=1, edgecolor='black')
algarve_polygons.plot(ax=ax3, color='none', linewidth=0.2, edgecolor='black')

algarve_polygons.plot(ax=ax4, column='gear_number', cmap=cmap, linewidth=1, edgecolor='black')
algarve_polygons.plot(ax=ax4, color='none', linewidth=0.2, edgecolor='black')

ctx.add_basemap(ax1, crs=algarve_polygons.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
ctx.add_basemap(ax2, crs=algarve_polygons.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
ctx.add_basemap(ax3, crs=algarve_polygons.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
ctx.add_basemap(ax4, crs=algarve_polygons.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

ax1.set_title('Choropleth Map of Hours of Fishing per Square Kilometer')
ax2.set_title('Kernel Density Estimation of Number of Boats')
ax3.set_title('Choropleth Map of Hours of Fishing')
ax4.set_title('Choropleth Map of Number of Gears Used')

sm2 = ScalarMappable(cmap=cmap)
sm2.set_array(algarve_polygons['boat_count'])
sm3 = ScalarMappable(cmap=cmap)
sm3.set_array(algarve_polygons['boat_hours'])
sm4 = ScalarMappable(cmap=cmap)
sm4.set_array(algarve_polygons['gear_number'])

cbar = plt.colorbar(sm, cax=cbar_ax, orientation='vertical', aspect=10, pad=0.2)
cbar.ax.yaxis.set_ticks_position('left')
cbar.set_label('Hour_Boat_Meter per km^2')

cbar2 = plt.colorbar(sm2, cax=cbar_ax2, orientation='vertical', aspect=10, pad=0.2)
cbar2.ax.yaxis.set_ticks_position('left')
cbar2.set_label('Boat Count')

cbar3 = plt.colorbar(sm3, cax=cbar_ax3, orientation='vertical', aspect=10, pad=0.2)
cbar3.ax.yaxis.set_ticks_position('left')
cbar3.set_label('Boat Hours')

cbar4 = plt.colorbar(sm4, cax=cbar_ax4, orientation='vertical', aspect=10, pad=0.2)
cbar4.ax.yaxis.set_ticks_position('left')
cbar4.set_label('Number of Gears')

plt.tight_layout()
plt.show()
