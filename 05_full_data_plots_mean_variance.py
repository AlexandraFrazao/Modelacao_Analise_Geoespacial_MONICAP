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



# Load algarve_polygons_all from pickle
with open(r'saved_shapefiles/algarve_polygons_all.pickle', 'rb') as f:
    algarve_polygons_all = pickle.load(f)

"""  """
"""  """
"""  """

# Perform a spatial join
fiscrep_algarve = gpd.sjoin(fiscrep_geo, algarve_polygons_all, how='inner', op='intersects')

# Drop duplicate rows based on inspection ID
fiscrep_algarve.drop_duplicates(subset='Number', inplace=True)

#save this file in excel format
fiscrep_algarve.to_csv('fiscrep_algarve.csv')

#count how many gears have in this file per year
gear_counts = fiscrep_algarve.groupby('Year')['Gear'].value_counts()

#Count how many gears where considered PI
presum_fiscrep = fiscrep_algarve[fiscrep_algarve['Result'] == 'PRESUM']
gear_counts_presum = presum_fiscrep.groupby('Year')['Gear'].value_counts()
#Count the unique Name vessels PI
vessel_counts = presum_fiscrep['Name'].value_counts()


#Count the unique CFR vessels
total_unique = fiscrep_algarve['matched_CFR'].nunique()

# Contar valores únicos na coluna 'matched_CFR' com 'Result' igual a 'Legal'
legal_unique = fiscrep_algarve[fiscrep_algarve['Result'] == 'LEGAL']['matched_CFR'].nunique()

# Contar valores únicos na coluna 'matched_CFR' com 'Result' igual a 'PRESUM'
presum_unique = fiscrep_algarve[fiscrep_algarve['Result'] == 'PRESUM']['matched_CFR'].nunique()


# Calculate Spearman rank correlation
correlation = algarve_polygons_all[['boat_count', 'gear_number']].corr(method='spearman').iloc[0, 1]

# Print the correlation value
print("Spearman rank correlation:", correlation)


variable = 'boat_count'  # Specify the variable here

mean_variable = algarve_polygons_all.groupby(['CELLCODE'])[variable].mean().copy()
variance_variable = algarve_polygons_all.groupby('CELLCODE')[variable].std().copy()

# Create a new GeoDataFrame for the grid polygons with the mean and variance data
grid_data = algarve_polygons_all.dissolve(by='CELLCODE')
grid_data['boat_count_avg'] = mean_variable.copy()
grid_data['boat_count_std'] = variance_variable.copy()



variable = 'gear_number'  # Specify the variable here

mean_variable2 = algarve_polygons_all.groupby(['CELLCODE'])[variable].mean().copy()
variance_variable2 = algarve_polygons_all.groupby('CELLCODE')[variable].std().copy()

# Create a new GeoDataFrame for the grid polygons with the mean and variance data
grid_data['gear_number_avg'] = mean_variable2.copy()
grid_data['gear_number_std'] = variance_variable2.copy()





variable = 'hour_boat_meter'  # Specify the variable here

mean_variable3 = algarve_polygons_all.groupby(['CELLCODE'])[variable].mean().copy()
variance_variable3 = algarve_polygons_all.groupby('CELLCODE')[variable].std().copy()

# Create a new GeoDataFrame for the grid polygons with the mean and variance data
grid_data['hour_boat_meter_avg'] = mean_variable3.copy()
grid_data['hour_boat_meter_std'] = variance_variable3.copy()


variable = 'boat_hours'

mean_variable4 = algarve_polygons_all.groupby(['CELLCODE'])[variable].mean().copy()
variance_variable4 = algarve_polygons_all.groupby('CELLCODE')[variable].std().copy()

# Create a new GeoDataFrame for the grid polygons with the mean and variance data
grid_data['boat_hours_avg'] = mean_variable4.copy()
grid_data['boat_hours_std'] = variance_variable4.copy()


#Average and Standard Deviation to boat_count
# Plot the mean variable and variance side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

variable = 'boat_count'

mean_variable = grid_data['boat_count_avg']
variance_variable = grid_data['boat_count_std']

# Read the shapefile for the protected areas
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)

protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])] 

grid_data['boat_count_avg'].replace(0, float('nan'), inplace=True)
grid_data['boat_count_std'].replace(0, float('nan'), inplace=True)

filtered_data = grid_data[~np.isnan(grid_data['boat_count_std'])]
filtered_data = grid_data[grid_data['boat_count_avg'] > 10]
selected_columns = filtered_data[['boat_count_avg', 'boat_count_std']]

#cellcodes = filtered_data.index.tolist()
filtered_data = grid_data[(grid_data['boat_count_std'] > 6) & (grid_data['boat_count_std'] <=8)]

# Plot the mean variable
grid_data.plot(column='boat_count_avg', cmap='coolwarm', linewidth=0.8, edgecolor='none', ax=ax1, legend=False)
ax1.set_title('Average of ' + variable)
ax1.set_aspect('equal')
ctx.add_basemap(ax1, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the variance of the variable
grid_data.plot(column='boat_count_std', cmap='YlOrRd', linewidth=0.8, edgecolor='none', ax=ax2, legend=False)
ax2.set_title('Standard Deviation of ' + variable)
ax2.set_aspect('equal')
ctx.add_basemap(ax2, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the protected area on top
protected_area.to_crs(sea_data.crs).plot(ax=ax1, facecolor='none', edgecolor='red')
protected_area.to_crs(sea_data.crs).plot(ax=ax2, facecolor='none', edgecolor='red')

# Create a single colorbar for both subplots
sm1 = ScalarMappable(cmap='coolwarm')
sm1.set_array(grid_data['boat_count_avg'])
cbar1 = plt.colorbar(sm1, ax=ax1, orientation='horizontal', aspect=20, pad=0.1)
cbar1.ax.yaxis.set_ticks_position('left')
cbar1.set_label('Average number of number of unique boats per month')


# Create a single colorbar for both subplots
sm2 = ScalarMappable(cmap='YlOrRd')
sm2.set_array(grid_data['boat_count_std'])
cbar2 = plt.colorbar(sm2, ax=ax2, orientation='horizontal', aspect=20, pad=0.1)
cbar2.ax.yaxis.set_ticks_position('left')
cbar2.set_label('Standard Deviation of number of unique boats per month')

# Plot the inspections in the Algarve region
#fiscrep_algarve.plot(ax=ax1, marker='o', column='Result', cmap='coolwarm', markersize=2, alpha = 0.3)
#fiscrep_algarve.plot(ax=ax2, marker='o', column='Result', cmap='coolwarm', markersize=2, alpha = 0.3)


# Show the plots
plt.tight_layout()
plt.show()


import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.cm import ScalarMappable
import contextily as ctx
import numpy as np
import pickle

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

# Load algarve_polygons_all from pickle
with open(r'saved_shapefiles/algarve_polygons_all.pickle', 'rb') as f:
    algarve_polygons_all = pickle.load(f)

"""  """
"""  """
"""  """

variable = 'boat_count'

mean_variable = grid_data['boat_count_avg']
variance_variable = grid_data['boat_count_std']


# Plot the mean variable and variance side by side as kernel density plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Read the shapefile for the protected areas
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)

protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]
# Set the same limits for x-axis and y-axis of both subplots
xlim = (grid_data.centroid.x.min(), grid_data.centroid.x.max())
ylim = (grid_data.centroid.y.min(), grid_data.centroid.y.max())

# Plot the kernel density of the mean variable
sns.kdeplot(
    ax=ax1,
    x=grid_data.centroid.x,
    y=grid_data.centroid.y,
    levels=np.linspace(0.01, 1, 100),
    fill=True,
    weights=mean_variable,
    cmap='coolwarm',
    alpha=0.5
)
ax1.set_title('Kernel Density of the average of number of unique boats per month')
ax1.set_xlabel('Density')
ax1.set_ylabel('')

# Plot the kernel density of the variance variable
sns.kdeplot(
    ax=ax2,
    x=grid_data.centroid.x,
    y=grid_data.centroid.y,
    levels=np.linspace(0.01, 1, 100),
    weights=variance_variable,
    fill=True,
    cmap='YlOrRd',
    alpha=0.5
)
ax2.set_title('Kernel Density of the standard deviation of number of unique boats per month')
ax2.set_xlabel('Density')
ax2.set_ylabel('')

# Plot the protected area on top
protected_area.to_crs(sea_data.crs).plot(ax=ax1, facecolor='none', edgecolor='red', alpha=0.8)
protected_area.to_crs(sea_data.crs).plot(ax=ax2, facecolor='none', edgecolor='red', alpha=0.8)

# Add colorbar for the mean variable
sm1 = ScalarMappable(cmap='coolwarm')
sm1.set_array(mean_variable)
cbar1 = plt.colorbar(sm1, ax=ax1, orientation='horizontal', aspect=20, pad=0.1)
cbar1.ax.yaxis.set_ticks_position('left')
cbar1.set_label('Average number of number of unique boats per month')

# Add colorbar for the variance variable
sm2 = ScalarMappable(cmap='YlOrRd')
sm2.set_array(variance_variable)
cbar2 = plt.colorbar(sm2, ax=ax2, orientation='horizontal', aspect=20, pad=0.1)
cbar2.ax.yaxis.set_ticks_position('left')
cbar2.set_label('Standard deviation of of number of unique boats per month')

ctx.add_basemap(ax1, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
ctx.add_basemap(ax2, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Show the plots
plt.tight_layout()
plt.show()



#Average and Standard Deviation to the gear_number
# Plot the mean variable and variance side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# Read the shapefile for the protected areas
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)

protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]


mean_variable = grid_data['gear_number_avg']
variance_variable = grid_data['gear_number_std']
variable = 'gear_number'

grid_data['gear_number_avg'].replace(0, float('nan'), inplace=True)
grid_data['gear_number_std'].replace(0, float('nan'), inplace=True)


# Plot the mean variable
grid_data.plot(column='gear_number_avg', cmap='coolwarm', linewidth=0.8, edgecolor='none', ax=ax1, legend=False)
ax1.set_title('Average of ' + variable)
ax1.set_aspect('equal')
ctx.add_basemap(ax1, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the variance of the variable
grid_data.plot(column='gear_number_std', cmap='YlOrRd', linewidth=0.8, edgecolor='none', ax=ax2, legend=False)
ax2.set_title('Standard Deviation of ' + variable)
ax2.set_aspect('equal')
ctx.add_basemap(ax2, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the protected area on top
protected_area.to_crs(sea_data.crs).plot(ax=ax1, facecolor='none', edgecolor='red')
protected_area.to_crs(sea_data.crs).plot(ax=ax2, facecolor='none', edgecolor='red')

# Create a single colorbar for both subplots
sm1 = ScalarMappable(cmap='coolwarm')
sm1.set_array(grid_data['gear_number_avg'])
cbar1 = plt.colorbar(sm1, ax=ax1, orientation='horizontal', aspect=20, pad=0.1)
cbar1.ax.yaxis.set_ticks_position('left')
cbar1.set_label('Average number of gears used per month')


# Create a single colorbar for both subplots
sm2 = ScalarMappable(cmap='YlOrRd')
sm2.set_array(grid_data['gear_number_std'])
cbar2 = plt.colorbar(sm2, ax=ax2, orientation='horizontal', aspect=20, pad=0.1)
cbar2.ax.yaxis.set_ticks_position('left')
cbar2.set_label('Standard Deviation of the number of gears used per month')


# Show the plots
plt.tight_layout()
plt.show()



#Average and Standard Deviation hour_boat_meter
# Plot the mean variable and variance side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

variable = 'hour_boat_meter'

mean_variable = grid_data['hour_boat_meter_avg']
variance_variable = grid_data['hour_boat_meter_std']

grid_data['hour_boat_meter_avg'].replace(0, float('nan'), inplace=True)
grid_data['hour_boat_meter_std'].replace(0, float('nan'), inplace=True)

# Read the shapefile for the protected areas
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)

protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]

# Plot the mean variable
grid_data.plot(column='hour_boat_meter_avg', cmap='coolwarm', linewidth=0.8, edgecolor='none', ax=ax1, legend=False)
ax1.set_title('Average ' + variable)
ax1.set_aspect('equal')
ctx.add_basemap(ax1, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the variance of the variable
grid_data.plot(column='hour_boat_meter_std', cmap='YlOrRd', linewidth=0.8, edgecolor='none', ax=ax2, legend=False)
ax2.set_title('Standard Deviation of ' + variable)
ax2.set_aspect('equal')
ctx.add_basemap(ax2, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the protected area on top
protected_area.to_crs(sea_data.crs).plot(ax=ax1, facecolor='none', edgecolor='red', alpha=0.8)
protected_area.to_crs(sea_data.crs).plot(ax=ax2, facecolor='none', edgecolor='red', alpha=0.8)

# Create a single colorbar for both subplots
sm1 = ScalarMappable(cmap='coolwarm')
sm1.set_array(grid_data['hour_boat_meter_avg'])
cbar1 = plt.colorbar(sm1, ax=ax1, orientation='horizontal', aspect=20, pad=0.1)
cbar1.ax.yaxis.set_ticks_position('left')
cbar1.set_label('Average of the monthly hour_boat_meter per km^2')

# Create a single colorbar for both subplots
sm2 = ScalarMappable(cmap='YlOrRd')
sm2.set_array(grid_data['hour_boat_meter_std'])
cbar2 = plt.colorbar(sm2, ax=ax2, orientation='horizontal', aspect=20, pad=0.1)
cbar2.ax.yaxis.set_ticks_position('left')
cbar2.set_label('Standard Deviation of the monthly hour_boat_meter per km^2')

# Show the plots
plt.tight_layout()
plt.show()




import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.cm import ScalarMappable
import contextily as ctx
import numpy as np

import pickle

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

# Load algarve_polygons_all from pickle
with open(r'saved_shapefiles/algarve_polygons_all.pickle', 'rb') as f:
    algarve_polygons_all = pickle.load(f)

"""  """
"""  """
"""  """

variable = 'hour_boat_meter'

mean_variable = grid_data['hour_boat_meter_avg']
variance_variable = grid_data['hour_boat_meter_std']


# Plot the mean variable and variance side by side as kernel density plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

# Read the shapefile for the protected areas
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)

protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]
# Set the same limits for x-axis and y-axis of both subplots
xlim = (grid_data.centroid.x.min(), grid_data.centroid.x.max())
ylim = (grid_data.centroid.y.min(), grid_data.centroid.y.max())

# Plot the kernel density of the mean variable
sns.kdeplot(
    ax=ax1,
    x=grid_data.centroid.x,
    y=grid_data.centroid.y,
    levels=np.linspace(0.01, 1, 100),
    fill=True,
    weights=mean_variable,
    cmap='coolwarm',
    alpha=0.5
)
ax1.set_title('Kernel Density of the average of the monthly hour_boat_meter per km^2')
ax1.set_xlabel('Density')
ax1.set_ylabel('')

# Plot the kernel density of the variance variable
sns.kdeplot(
    ax=ax2,
    x=grid_data.centroid.x,
    y=grid_data.centroid.y,
    levels=np.linspace(0.01, 1, 100),
    weights=variance_variable,
    fill=True,
    cmap='YlOrRd',
    alpha=0.5
)
ax2.set_title('Kernel Density of the standard deviation of the monthly hour_boat_meter per km^2')
ax2.set_xlabel('Density')
ax2.set_ylabel('')

# Plot the protected area on top
protected_area.to_crs(sea_data.crs).plot(ax=ax1, facecolor='none', edgecolor='red', alpha=0.8)
protected_area.to_crs(sea_data.crs).plot(ax=ax2, facecolor='none', edgecolor='red', alpha=0.8)

# Add colorbar for the mean variable
sm1 = ScalarMappable(cmap='coolwarm')
sm1.set_array(mean_variable)
cbar1 = plt.colorbar(sm1, ax=ax1, orientation='horizontal', aspect=20, pad=0.1)
cbar1.ax.yaxis.set_ticks_position('left')
cbar1.set_label('Average number of the monthly hour_boat_meter per km^2')

# Add colorbar for the variance variable
sm2 = ScalarMappable(cmap='YlOrRd')
sm2.set_array(variance_variable)
cbar2 = plt.colorbar(sm2, ax=ax2, orientation='horizontal', aspect=20, pad=0.1)
cbar2.ax.yaxis.set_ticks_position('left')
cbar2.set_label('Standard deviation of the monthly hour_boat_meter per km^2')

ctx.add_basemap(ax1, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
ctx.add_basemap(ax2, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Show the plots
plt.tight_layout()
plt.show()





#Spearman Correlation-HB&GN
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import contextily as ctx
import pickle
import numpy as np

# Ler o shapefile para o mar Português
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

# Carregar algarve_polygons_all do pickle
with open(r'saved_shapefiles/algarve_polygons_all.pickle', 'rb') as f:
    algarve_polygons_all = pickle.load(f)

# Calcular a correlação de rank de Spearman para 'boat_count' e 'gear_number'
correlation = algarve_polygons_all.groupby('CELLCODE')[['boat_count', 'gear_number']].corr(method='spearman').iloc[0::2, -1]
group_counts = algarve_polygons_all['boat_count'].fillna(0).astype(bool).groupby(algarve_polygons_all['CELLCODE']).sum()
correlation_10 = pd.DataFrame({'spearman': correlation})
correlation_10['number'] = group_counts.values
correlation_10.loc[correlation_10['number'] < 10, 'spearman'] = np.nan

grid_data['spearman1'] = correlation_10['spearman'].values

# Merge the DataFrames using 'CELLCODE' as the key
merged_data = grid_data.merge(correlation_10, on='CELLCODE')

# Criar um gráfico
fig, ax = plt.subplots(figsize=(10, 10))
grid_data.plot(column='spearman1', cmap='coolwarm', linewidth=0.8, edgecolor='black', ax=ax)
ax.set_title('Spearman Rank Correlation - Número de embarcações e artes únicas')

# Ler o shapefile para as áreas protegidas
protected_path = 'shapefiles/WDPA_WDOECM_Jun2023_Public_PRT_shp_2/WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)
protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe', 'Costa Sudoeste', 'Ria Formosa'])]

# Traçar a área protegida por cima
protected_area.to_crs(sea_data.crs).plot(ax=ax, facecolor='none', edgecolor='red')

# Adicionar uma barra de cores para os valores de correlação
sm = ScalarMappable(cmap='coolwarm')
sm.set_array(grid_data['spearman'].dropna().values)
sm.set_clim(-1, 1)
cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', aspect=20, pad=0.1)
cbar.ax.xaxis.set_ticks_position('top')
cbar.set_label('Spearman Rank Correlation')

# Adicionar mapa base usando Contextily
ctx.add_basemap(ax, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Mostrar o gráfico
plt.show()







import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import contextily as ctx

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

# Calculate Spearman rank correlation
correlation = algarve_polygons_all.groupby('CELLCODE')[['hour_boat_meter', 'gear_number']].corr(method='spearman').iloc[0::2, -1]
group_counts = algarve_polygons_all['hour_boat_meter'].fillna(0).astype(bool).groupby(algarve_polygons_all['CELLCODE']).sum()
correlation_10 = pd.DataFrame({'spearman':correlation})
correlation_10['number'] = group_counts.values
correlation_10.loc[correlation_10['number'] < 10, 'spearman'] = np.nan

grid_data['spearman'] = correlation_10['spearman'].values

# Merge the DataFrames using 'CELLCODE' as the key
merged_data = grid_data.merge(correlation_10, on='CELLCODE')


# Create a new GeoDataFrame for the grid polygons with the correlation data
grid_data['hour_boat_meter_avg_all'] = grid_data['hour_boat_meter_avg'].apply(lambda x: x * 23)
grid_data['hour_boat_meter_avg_all'] = grid_data['hour_boat_meter_avg_all'].apply(lambda x: x if np.isnan(x) or x < 200 else 200) # 200 is quantile 0.90


grid_data['boat_count_avg'].replace(0, float('nan'), inplace=True)
grid_data['boat_count_avg'] = grid_data['boat_count_avg'].apply(lambda x: x if np.isnan(x) or x < 10 else 10) # 10 is quantile 0.90

# Plot the boat_count, hour_boat_meter, gear_number, and Spearman rank correlation
fig, axs = plt.subplots(2, 2, figsize=(15, 15))

# Read the shapefile for the protected areas
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)

protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]

# Plot the protected area on top
protected_area.to_crs(sea_data.crs).plot(ax=axs[0,0], facecolor='none', edgecolor='red')
protected_area.to_crs(sea_data.crs).plot(ax=axs[0,1], facecolor='none', edgecolor='red')
protected_area.to_crs(sea_data.crs).plot(ax=axs[1,0], facecolor='none', edgecolor='red')
protected_area.to_crs(sea_data.crs).plot(ax=axs[1,1], facecolor='none', edgecolor='red')

# Plot boat_count
grid_data.plot(column='boat_count_avg', cmap='coolwarm', linewidth=0.8, edgecolor='none', ax=axs[0, 0], legend=False, alpha=0.9)
axs[0, 0].set_title('Average of the monthly boat_count')
axs[0, 0].set_aspect('equal')
ctx.add_basemap(axs[0, 0], crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot hour_boat_meter
grid_data.plot(column='hour_boat_meter_avg_all', cmap='coolwarm', linewidth=0.8, edgecolor='none', ax=axs[0, 1], legend=False, alpha=0.9)
axs[0, 1].set_title('Sum of all hour_boat_meter per km^2')
axs[0, 1].set_aspect('equal')
ctx.add_basemap(axs[0, 1], crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot gear_number
grid_data.plot(column='gear_number_avg', cmap='coolwarm', linewidth=0.8, edgecolor='none', ax=axs[1, 0], legend=False, alpha=0.9)
axs[1, 0].set_title('Average of the monthly gear_number')
axs[1, 0].set_aspect('equal')
ctx.add_basemap(axs[1, 0], crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the Spearman rank correlation between hour_boat_meter and gear_number
grid_data.plot(column='spearman', cmap='coolwarm', vmin=-1, vmax=1, linewidth=0.3, edgecolor='black', ax=axs[1, 1], legend=False, alpha=0.9)
axs[1, 1].set_title('Spearman Rank Correlation between hour_boat_meter and gear_number')
axs[1, 1].set_aspect('equal')  # Set the aspect ratio to equal
ctx.add_basemap(axs[1, 1], crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Create a colorbar for boat_count
sm1 = ScalarMappable(cmap='coolwarm')
sm1.set_array(grid_data['boat_count_avg'])
cbar1 = plt.colorbar(sm1, ax=axs[0, 0], orientation='horizontal', aspect=15, pad=0.05)
cbar1.ax.yaxis.set_ticks_position('left')
#cbar1.set_label('Boat Count')

# Create a colorbar for hour_boat_meter
sm2 = ScalarMappable(cmap='coolwarm')
sm2.set_array(grid_data['hour_boat_meter_avg_all'])
cbar2 = plt.colorbar(sm2, ax=axs[0, 1], orientation='horizontal', aspect=15, pad=0.05)
cbar2.ax.yaxis.set_ticks_position('left')
#cbar2.set_label('Hour Boat Meter')

# Create a colorbar for gear_number
sm3 = ScalarMappable(cmap='coolwarm')
sm3.set_array(grid_data['gear_number_avg'])
cbar3 = plt.colorbar(sm3, ax=axs[1, 0], orientation='horizontal', aspect=15, pad=0.05)
cbar3.ax.yaxis.set_ticks_position('left')
#cbar3.set_label('Gear Number')

# Create a colorbar for the Spearman rank correlation
sm4 = ScalarMappable(cmap='coolwarm')
sm4.set_array(grid_data['spearman'])
sm4.set_clim(-1, 1)  # Set the color limits to -1 and 1
cbar4 = plt.colorbar(sm4, ax=axs[1, 1], orientation='horizontal', aspect=15, pad=0.05)
cbar4.ax.yaxis.set_ticks_position('left')
#cbar4.set_label('Spearman Rank Correlation')

# Modify the tick labels of the colorbar
tick_labels = cbar2.ax.get_xticklabels()
new_tick_labels = [label.get_text() if float(label.get_text()) < 200 else '>200' for label in tick_labels]
cbar2.ax.set_xticklabels(new_tick_labels)

# Modify the tick labels of the colorbar
tick_labels2 = cbar1.ax.get_xticklabels()
new_tick_labels2 = [label.get_text() if float(label.get_text()) < 10 else '>10' for label in tick_labels2]
cbar1.ax.set_xticklabels(new_tick_labels2)

axs[0, 0].axis('off')
axs[1, 0].axis('off')
axs[0, 1].axis('off')
axs[1, 1].axis('off')

# Show the plot
#plt.tight_layout()
plt.show()



#SPEARMAN CORR HBM&GN
correlation = algarve_polygons_all.groupby('CELLCODE')[['hour_boat_meter', 'gear_number']].corr(method='spearman').iloc[0::2, -1]
group_counts = algarve_polygons_all['hour_boat_meter'].fillna(0).astype(bool).groupby(algarve_polygons_all['CELLCODE']).sum()
correlation_10 = pd.DataFrame({'spearman':correlation})
correlation_10['number'] = group_counts.values
correlation_10.loc[correlation_10['number'] < 10, 'spearman'] = np.nan

# Correção: Atribuir os valores de 'spearman' ao DataFrame grid_data
grid_data['spearman'] = correlation_10['spearman'].values

# Merge the DataFrames using 'CELLCODE' as the key
merged_data = grid_data.merge(correlation_10, on='CELLCODE')
merged_data.drop(['spearman_y', 'number_y'], axis=1, inplace=True)


# Plot the filtered Spearman rank correlation between hour_boat_meter and gear_number
fig, ax = plt.subplots(figsize=(10, 10))

# Read the shapefile for the protected areas
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)

protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]

# Plot the protected area on top
protected_area.to_crs(sea_data.crs).plot(ax=ax, facecolor='none', edgecolor='red')


grid_data.plot(column='spearman', cmap='coolwarm', vmin=-1, vmax=1, linewidth=0.3, edgecolor='black', ax=ax, legend=False)
ax.set_title('Spearman Rank Correlation between hour_boat_meter and gear_number')
ax.set_aspect('equal')
ctx.add_basemap(ax, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Create a colorbar for the filtered Spearman rank correlation
sm = ScalarMappable(cmap='coolwarm')
sm.set_array(filtered_data['spearman'])
sm.set_clim(-1, 1)  # Set the color limits to -1 and 1
cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', aspect=15, pad=0.05)
cbar.ax.yaxis.set_ticks_position('left')
#cbar.set_label('Spearman Rank Correlation')

# Show the plot
plt.show()




#LESS THAN 0.5 IN SPEARMAN CORR
correlation = algarve_polygons_all.groupby('CELLCODE')[['hour_boat_meter', 'gear_number']].corr(method='spearman').iloc[0::2, -1]

group_counts = algarve_polygons_all['hour_boat_meter'].fillna(0).astype(bool).groupby(algarve_polygons_all['CELLCODE']).sum()

correlation_10 = pd.DataFrame({'spearman':correlation})

correlation_10['number'] = group_counts.values

correlation_10.loc[correlation_10['number'] < 10, 'spearman'] = np.nan

# Create a new GeoDataFrame for the grid polygons with the correlation data
# Correção: Atribuir os valores de 'spearman' ao DataFrame grid_data
grid_data['spearman'] = correlation_10['spearman'].values


# Filter the grid data for correlations less than 0.5
filtered_data = grid_data[grid_data['spearman'] < 0.5]

# Merge the DataFrames using 'CELLCODE' as the key
merged_data = filtered_data.merge(correlation_10, on='CELLCODE')

# Plot the filtered Spearman rank correlation between hour_boat_meter and gear_number
fig, ax = plt.subplots(figsize=(10, 10))

# Read the shapefile for the protected areas
protected_path = 'shapefiles\WDPA_WDOECM_Jun2023_Public_PRT_shp_2\WDPA_WDOECM_Jun2023_Public_PRT_shp-polygons.shp'
protected_area = gpd.read_file(protected_path)

protected_area = protected_area[protected_area.NAME.isin(['Banco Gorringe','Costa Sudoeste', 'Ria Formosa'])]

# Plot the protected area on top
protected_area.to_crs(sea_data.crs).plot(ax=ax, facecolor='none', edgecolor='red')


filtered_data.plot(column='spearman', cmap='coolwarm', vmin=-1, vmax=1, linewidth=0.3, edgecolor='black', ax=ax, legend=False)
ax.set_title('Spearman Rank Correlation < 0.5 between hour_boat_meter and gear_number')
ax.set_aspect('equal')
ctx.add_basemap(ax, crs=sea_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Create a colorbar for the filtered Spearman rank correlation
sm = ScalarMappable(cmap='coolwarm')
sm.set_array(filtered_data['spearman'])
sm.set_clim(-1, 1)  # Set the color limits to -1 and 1
cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', aspect=15, pad=0.05)
cbar.ax.yaxis.set_ticks_position('left')
#cbar.set_label('Spearman Rank Correlation')

# Show the plot
plt.show()







import folium

# Create a Folium Map centered on the Algarve region
m = folium.Map(location=[37.1505, -8.5790], zoom_start=9)

# Add the Algarve polygons to the map
folium.GeoJson(sea_data).add_to(m)

# Add the protected area polygons to the map
folium.GeoJson(protected_area.to_crs('EPSG:4326')).add_to(m)

grid_data2 = grid_data.reset_index()

grid_data2.drop(columns='centroid', inplace = True)

folium.Choropleth(
    geo_data=grid_data2,
    data=grid_data2,
    columns=['CELLCODE', 'hour_boat_meter_avg'],  # Replace 'hour_boat_meter_avg' with the correct column name
    fill_color='red',
    fill_opacity=0.7,
    line_opacity=0.8,
    nan_fill_color='red',
    legend_name='Average hour_boat_meter per km^2',
).add_to(m)


# Add the inspections in the Algarve region
for idx, row in fiscrep_algarve.iterrows():
    folium.CircleMarker(
        location=[row['lat_DD'], row['lon_DD']],
        radius=3,
        color='blue' if row['Result'] != 'PRESUM' else 'red',
        fill=True,
        fill_color='blue' if row['Result'] != 'PRESUM' else 'red',
        popup=fiscrep_algarve.Infrac.loc[idx],
        fill_opacity=0.3,
    ).add_to(m)
# Display the map
m.save('map2.html')





