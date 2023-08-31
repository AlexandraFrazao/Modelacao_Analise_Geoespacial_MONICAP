import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import seaborn as sns
import contextily as ctx
import numpy as np

month_str = '12'

shapefile_path = f'saved_shapefiles/algarve_polygons_2022_{month_str}.shp'
algarve_polygons = gpd.read_file(shapefile_path)
algarve_polygons['month'] = int(month_str)

#aa = algarve_polygons[algarve_polygons['boat_hours'] > 0] 

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

##########################################################################
##########################################################################
##########################################################################
cmap='coolwarm'

import matplotlib.gridspec as gridspec

cmap = 'coolwarm'

fig = plt.figure(figsize=(15, 9))
gs = gridspec.GridSpec(2, 4, width_ratios=[0.05, 1, 1, 0.05], height_ratios=[1, 1])

cbar_ax = plt.subplot(gs[0])
ax1 = plt.subplot(gs[1])
ax2 = plt.subplot(gs[2])
cbar_ax2 = plt.subplot(gs[3])
cbar_ax3 = plt.subplot(gs[4])
ax3 = plt.subplot(gs[5])
ax4 = plt.subplot(gs[6])
cbar_ax4 = plt.subplot(gs[7])


# Define the extent of the grid
min_x, min_y, max_x, max_y = algarve_polygons.total_bounds

padding = 0.5
ax1.set_xlim(min_x - padding, max_x + padding)
ax1.set_ylim(min_y - padding, max_y + padding)
ax2.set_xlim(min_x - padding, max_x + padding)
ax2.set_ylim(min_y - padding, max_y + padding)
ax3.set_xlim(min_x - padding, max_x + padding)
ax3.set_ylim(min_y - padding, max_y + padding)
ax4.set_xlim(min_x - padding, max_x + padding)
ax4.set_ylim(min_y - padding, max_y + padding)

algarve_polygons.rename(columns = {'hour_boat_':'hour_boat_meter', 'gear_numbe':'gear_number'}, inplace = True)

algarve_polygons.plot(ax=ax1, column='hour_boat_meter', cmap=cmap, linewidth=1, edgecolor='black')
algarve_polygons.plot(ax=ax1, color='none', linewidth=0.2, edgecolor='black')
sm = ScalarMappable(cmap=cmap)
sm.set_array(algarve_polygons['hour_boat_meter'])

algarve_polygons = algarve_polygons.to_crs(sea_data.crs)

sns.kdeplot(
    ax=ax2,
    x=algarve_polygons.geometry.centroid.x,
    y=algarve_polygons.geometry.centroid.y,
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


# Read the shapefile for the protected areas
protected_path = 'shapefiles/WDPA_WDOECM_Jun2023_Public_PRT_shp_2/WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)
protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe', 'Costa Sudoeste', 'Ria Formosa'])]

protected_area.plot(ax=ax1, facecolor='none', edgecolor='red')
protected_area.plot(ax=ax2, facecolor='none', edgecolor='red')
protected_area.plot(ax=ax3, facecolor='none', edgecolor='red')
protected_area.plot(ax=ax4, facecolor='none', edgecolor='red')

plt.tight_layout()
plt.show()

# List of variables/columns of interest
columns_of_interest = ['hour_boat_meter', 'boat_count', 'boat_hours', 'gear_number']

# Describe each variable
descriptions = {}
for column in columns_of_interest:
    description = algarve_polygons[column].describe()
    descriptions[column] = description
    print(f"Description for {column}:\n", description, "\n" + "-"*50)

# If you need the descriptions as a single DataFrame:
description_df = pd.concat(descriptions, axis=1)
print(description_df)







