import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import contextily as ctx
import numpy as np
from shapely.geometry import Point
import pickle

fiscrep = pd.read_csv('final_fiscrep.csv')

fiscrep.drop_duplicates(inplace=True)


fiscrep = fiscrep[fiscrep.Year>2020]

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)



# Create a geometry column using lat_DD and lon_DD
geometry = [Point(lon, lat) for lon, lat in zip(fiscrep['lon_DD'], fiscrep['lat_DD'])]

# Create a GeoDataFrame
fiscrep_geo = gpd.GeoDataFrame(fiscrep, geometry=geometry, crs=sea_data.crs)


output_dir = 'saved_shapefiles'

# Create an empty GeoDataFrame to store the data for all shapefiles
algarve_polygons_all_art = gpd.GeoDataFrame()

# Read the shapefiles
algarve_polygons_2021 = gpd.read_file(f'{output_dir}/algarve_polygons_2021.shp')
algarve_polygons_2022 = gpd.read_file(f'{output_dir}/algarve_polygons_2022.shp')


# Append the shapefiles
algarve_polygons_all_art = algarve_polygons_2021.append(algarve_polygons_2022, ignore_index=True)

# Rename the columns
algarve_polygons_all_art.rename(columns={'mean_art_1': 'mean_art_level_per_hour', 'level_hour': 'level_hour_boat_meter', 'art_level_': 'art_level_hour_boat_meter', 'hour_boat_': 'hour_boat_meter', 'gear_numbe': 'gear_number','mean_art_l': 'mean_art_level'}, inplace=True)

# Save the appended shapefile as a pickle file
algarve_polygons_all_art.to_pickle(f'{output_dir}/algarve_polygons_all_art.pickle')


# Perform a spatial join
fiscrep_algarve = gpd.sjoin(fiscrep_geo, algarve_polygons_all_art , how='inner', op='intersects')




variable = 'mean_art_level_per_hour'  # Specify the variable here

mean_variable = algarve_polygons_all_art.groupby(['CELLCODE'])[variable].mean().copy()
variance_variable = algarve_polygons_all_art.groupby('CELLCODE')[variable].std().copy()

# Create a new GeoDataFrame for the grid polygons with the mean and variance data
grid_data = algarve_polygons_all_art.dissolve(by='CELLCODE')
grid_data['mean_art_level_per_hour_avg'] = mean_variable.copy()
grid_data['mean_art_level_per_hour_std'] = variance_variable.copy()

variable = 'art_level_hour_boat_meter'  # Specify the variable here

mean_variable2 = algarve_polygons_all_art.groupby(['CELLCODE'])[variable].mean().copy()
variance_variable2 = algarve_polygons_all_art.groupby('CELLCODE')[variable].std().copy()

# Create a new GeoDataFrame for the grid polygons with the mean and variance data
grid_data['art_level_hour_boat_meter_avg'] = mean_variable2.copy()
grid_data['art_level_hour_boat_meter_std'] = variance_variable2.copy()



variable = 'hour_boat_meter'  # Specify the variable here

mean_variable3 = algarve_polygons_all_art.groupby(['CELLCODE'])[variable].mean().copy()
variance_variable3 = algarve_polygons_all_art.groupby('CELLCODE')[variable].std().copy()

# Create a new GeoDataFrame for the grid polygons with the mean and variance data
grid_data['hour_boat_meter_avg'] = mean_variable3.copy()
grid_data['hour_boat_meter_std'] = variance_variable3.copy()



variable = 'mean_art_level'  # Specify the variable here

mean_variable4 = algarve_polygons_all_art.groupby(['CELLCODE'])[variable].mean().copy()
variance_variable4 = algarve_polygons_all_art.groupby('CELLCODE')[variable].std().copy()

# Create a new GeoDataFrame for the grid polygons with the mean and variance data
grid_data['mean_art_level_avg'] = mean_variable4.copy()
grid_data['mean_art_level_std'] = variance_variable4.copy()



import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
from matplotlib.cm import ScalarMappable

# Assuming you have already defined 'sea_data' and 'grid_data'

# Average and Standard Deviation to mean_art_level
mean_variable = grid_data['mean_art_level_avg']
variance_variable = grid_data['mean_art_level_std']
variable = 'mean_art_level'

# Replace zeros with NaN to avoid distortion in the plots
grid_data['mean_art_level_avg'].replace(0, float('nan'), inplace=True)
grid_data['mean_art_level_std'].replace(0, float('nan'), inplace=True)

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

filtered_data = grid_data[~np.isnan(grid_data['mean_art_level_avg'])]

filtered_data = grid_data[(grid_data['mean_art_level_avg'] > 5) & (grid_data['mean_art_level_avg'] < 9)]

# Plot the mean variable
grid_data.plot(column='mean_art_level_avg', cmap='coolwarm', linewidth=0.8, edgecolor='none', ax=ax1, legend=False)
ax1.set_title('Average of ' + variable)
ax1.set_aspect('equal')
ctx.add_basemap(ax1, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the variance of the variable
grid_data.plot(column='mean_art_level_std', cmap='YlOrRd', linewidth=0.8, edgecolor='none', ax=ax2, legend=False)
ax2.set_title('Standard Deviation of ' + variable)
ax2.set_aspect('equal')
ctx.add_basemap(ax2, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Get the common x and y limits and set them to both axes
xlim = (min(ax1.get_xlim()[0], ax2.get_xlim()[0]), max(ax1.get_xlim()[1], ax2.get_xlim()[1]))
ylim = (min(ax1.get_ylim()[0], ax2.get_ylim()[0]), max(ax1.get_ylim()[1], ax2.get_ylim()[1]))

ax1.set_xlim(xlim)
ax1.set_ylim(ylim)
ax2.set_xlim(xlim)
ax2.set_ylim(ylim)

# Plot the protected area on top
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)
protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]
protected_area.to_crs(sea_data.crs).plot(ax=ax1, facecolor='none', edgecolor='red')
protected_area.to_crs(sea_data.crs).plot(ax=ax2, facecolor='none', edgecolor='red')

# Create a single colorbar for both subplots
sm1 = ScalarMappable(cmap='coolwarm')
sm1.set_array(grid_data['mean_art_level_avg'])
cbar1 = plt.colorbar(sm1, ax=ax1, orientation='horizontal', aspect=20, pad=0.1)
cbar1.ax.yaxis.set_ticks_position('left')
cbar1.set_label('Average number of ' + variable)

# Create a single colorbar for both subplots
sm2 = ScalarMappable(cmap='YlOrRd')
sm2.set_array(grid_data['mean_art_level_std'])
cbar2 = plt.colorbar(sm2, ax=ax2, orientation='horizontal', aspect=20, pad=0.1)
cbar2.ax.yaxis.set_ticks_position('left')
cbar2.set_label('Standard Deviation of ' + variable)

# Show the plots
plt.tight_layout()
plt.show()



import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
from matplotlib.cm import ScalarMappable

# Assuming you have already defined 'sea_data' and 'grid_data'

# Average and Standard Deviation to mean_art_level
mean_variable = grid_data['mean_art_level_avg']
variance_variable = grid_data['mean_art_level_std']
variable = 'mean_art_level'

# Replace zeros with NaN to avoid distortion in the plots
grid_data['mean_art_level_avg'].replace(0, float('nan'), inplace=True)
grid_data['mean_art_level_std'].replace(0, float('nan'), inplace=True)

filtered_data = grid_data[grid_data['mean_art_level_avg'] >= 9]


# Plotting
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# Plot the mean variable on ax1
grid_data.plot(column='mean_art_level_avg', cmap='coolwarm', linewidth=0.8, edgecolor='none', ax=ax1, legend=False)
ax1.set_title('Average of ' + variable)
ax1.set_aspect('equal')

# Plot the variance of the variable on ax2
grid_data.plot(column='mean_art_level_std', cmap='YlOrRd', linewidth=0.8, edgecolor='none', ax=ax2, legend=False)
ax2.set_title('Standard Deviation of ' + variable)
ax2.set_aspect('equal')

# Plot the protected areas on top
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)
protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]
protected_area.plot(ax=ax1, facecolor='none', edgecolor='red')
protected_area.plot(ax=ax2, facecolor='none', edgecolor='red')

# Add basemap
ctx.add_basemap(ax1, crs=grid_data.crs, source=ctx.providers.OpenStreetMap.Mapnik)
ctx.add_basemap(ax2, crs=grid_data.crs, source=ctx.providers.OpenStreetMap.Mapnik)

# Colorbars
sm1 = ScalarMappable(cmap='coolwarm')
sm1.set_array(grid_data['mean_art_level_avg'])
cbar1 = plt.colorbar(sm1, ax=ax1, orientation='horizontal', aspect=20, pad=0.1)
cbar1.ax.yaxis.set_ticks_position('left')
cbar1.set_label('Average number of ' + variable)

sm2 = ScalarMappable(cmap='YlOrRd')
sm2.set_array(grid_data['mean_art_level_std'])
cbar2 = plt.colorbar(sm2, ax=ax2, orientation='horizontal', aspect=20, pad=0.1)
cbar2.ax.yaxis.set_ticks_position('left')
cbar2.set_label('Standard Deviation of ' + variable)

plt.tight_layout()
plt.show()



#Average and Standard Deviation to mean_art_level_per_hour
# Plot the mean variable and variance side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# Read the shapefile for the protected areas
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)

protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]


mean_variable = grid_data['mean_art_level_per_hour_avg']
variance_variable = grid_data['mean_art_level_per_hour_std']
variable = 'mean_art_level_per_hour'

grid_data['mean_art_level_per_hour_avg'].replace(0, float('nan'), inplace=True)
grid_data['mean_art_level_per_hour_std'].replace(0, float('nan'), inplace=True)

filtered_data = grid_data[grid_data['art_level_hour_boat_meter_avg'] >=2000]
filtered_data = grid_data[(grid_data['mean_art_level_per_hour_avg'] >= 1000 ) & (grid_data['mean_art_level_per_hour_avg'] < 2000)]


cellcodes = filtered_data.index.tolist()

list1 = ['10kmE228N170', '10kmE229N171', '10kmE229N172', '10kmE230N173', '10kmE231N173', '10kmE235N178']

# Describe specific columns in the filtered_data
columns_to_describe = ['mean_art_level_per_hour_avg', 'mean_art_level_per_hour_std']
description_specific = filtered_data[columns_to_describe].describe()

# Print the description for specific columns
print(description_specific)



# Plot the mean variable
grid_data.plot(column='mean_art_level_per_hour_avg', cmap='coolwarm', linewidth=0.8, edgecolor='none', ax=ax1, legend=False)
ax1.set_title('Average of ' + variable)
ax1.set_aspect('equal')
ctx.add_basemap(ax1, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the variance of the variable
grid_data.plot(column='mean_art_level_per_hour_std', cmap='YlOrRd', linewidth=0.8, edgecolor='none', ax=ax2, legend=False)
ax2.set_title('Standard Deviation of ' + variable)
ax2.set_aspect('equal')
ctx.add_basemap(ax2, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the protected area on top
protected_area.to_crs(sea_data.crs).plot(ax=ax1, facecolor='none', edgecolor='red')
protected_area.to_crs(sea_data.crs).plot(ax=ax2, facecolor='none', edgecolor='red')

# Create a single colorbar for both subplots
sm1 = ScalarMappable(cmap='coolwarm')
sm1.set_array(grid_data['mean_art_level_per_hour_avg'])
cbar1 = plt.colorbar(sm1, ax=ax1, orientation='horizontal', aspect=20, pad=0.1)
cbar1.ax.yaxis.set_ticks_position('left')
cbar1.set_label('Average number of ' + variable)


# Create a single colorbar for both subplots
sm2 = ScalarMappable(cmap='YlOrRd')
sm2.set_array(grid_data['mean_art_level_per_hour_std'])
cbar2 = plt.colorbar(sm2, ax=ax2, orientation='horizontal', aspect=20, pad=0.1)
cbar2.ax.yaxis.set_ticks_position('left')
cbar2.set_label('Standard Deviation of ' + variable)

# Show the plots
plt.tight_layout()
plt.show()




#Average and Standard Deviation to art_level_hour_boat_meter
# Plot the mean variable and variance side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# Read the shapefile for the protected areas
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)

protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]


mean_variable = grid_data['art_level_hour_boat_meter_avg']
variance_variable = grid_data['art_level_hour_boat_meter_std']
variable = 'art_level_hour_boat_meter'

grid_data['art_level_hour_boat_meter_avg'].replace(0, float('nan'), inplace=True)
grid_data['art_level_hour_boat_meter_std'].replace(0, float('nan'), inplace=True)

# Plot the mean variable
grid_data.plot(column='art_level_hour_boat_meter_avg', cmap='coolwarm', linewidth=0.8, edgecolor='none', ax=ax1, legend=False)
ax1.set_title('Average of ' + variable)
ax1.set_aspect('equal')
ctx.add_basemap(ax1, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the variance of the variable
grid_data.plot(column='art_level_hour_boat_meter_std', cmap='YlOrRd', linewidth=0.8, edgecolor='none', ax=ax2, legend=False)
ax2.set_title('Standard Deviation of ' + variable)
ax2.set_aspect('equal')
ctx.add_basemap(ax2, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the protected area on top
protected_area.to_crs(sea_data.crs).plot(ax=ax1, facecolor='none', edgecolor='red')
protected_area.to_crs(sea_data.crs).plot(ax=ax2, facecolor='none', edgecolor='red')

# Create a single colorbar for both subplots
sm1 = ScalarMappable(cmap='coolwarm')
sm1.set_array(grid_data['art_level_hour_boat_meter_avg'])
cbar1 = plt.colorbar(sm1, ax=ax1, orientation='horizontal', aspect=20, pad=0.1)
cbar1.ax.yaxis.set_ticks_position('left')
cbar1.set_label('Average number of ' + variable)


# Create a single colorbar for both subplots
sm2 = ScalarMappable(cmap='YlOrRd')
sm2.set_array(grid_data['art_level_hour_boat_meter_std'])
cbar2 = plt.colorbar(sm2, ax=ax2, orientation='horizontal', aspect=20, pad=0.1)
cbar2.ax.yaxis.set_ticks_position('left')
cbar2.set_label('Standard Deviation of ' + variable)

# Show the plots
plt.tight_layout()
plt.show()

