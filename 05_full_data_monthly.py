import pandas as pd
import geopandas as gpd

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']  # Update with the desired months

# Create an empty DataFrame to store the data for all months
algarve_polygons_all = pd.DataFrame()

for month_str in months:
    shapefile_path = f'saved_shapefiles/algarve_polygons_2021_{month_str}.shp'
    algarve_polygons = gpd.read_file(shapefile_path)
    algarve_polygons['month'] = int(month_str)
    algarve_polygons['year'] = 2021
    algarve_polygons.rename(columns={'hour_boat_': 'hour_boat_meter', 'gear_numbe': 'gear_number', 'mean_loa_p': 'mean_loa_per_hour'}, inplace=True)
    algarve_polygons_all = algarve_polygons_all.append(algarve_polygons, ignore_index=True)

months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11']  # Update with the desired months

for month_str in months:
    shapefile_path = f'saved_shapefiles/algarve_polygons_2022_{month_str}.shp'
    algarve_polygons = gpd.read_file(shapefile_path)
    algarve_polygons['month'] = int(month_str)
    algarve_polygons['year'] = 2022
    algarve_polygons.rename(columns={'hour_boat_': 'hour_boat_meter', 'gear_numbe': 'gear_number', 'mean_loa_p': 'mean_loa_per_hour'}, inplace=True)
    algarve_polygons_all = algarve_polygons_all.append(algarve_polygons, ignore_index=True)

algarve_polygons_all = algarve_polygons_all.to_crs(sea_data.crs)

algarve_polygons_all['centroid'] = algarve_polygons_all.geometry.to_crs(sea_data.crs).centroid

import pickle

# Save algarve_polygons_all as pickle
with open(r'saved_shapefiles/algarve_polygons_all.pickle', 'wb') as f:
    pickle.dump(algarve_polygons_all, f)



import pandas as pd
import geopandas as gpd
import pickle

def load_and_process_data(year, months):
    algarve_polygons_year = pd.DataFrame()
    for month_str in months:
        shapefile_path = f'saved_shapefiles/algarve_polygons_{year}_{month_str}.shp'
        algarve_polygons = gpd.read_file(shapefile_path)
        algarve_polygons['month'] = int(month_str)
        algarve_polygons['year'] = year
        algarve_polygons.rename(columns={'hour_boat_': 'hour_boat_meter', 'gear_numbe': 'gear_number', 'mean_loa_p': 'mean_loa_per_hour'}, inplace=True)
        algarve_polygons_year = algarve_polygons_year.append(algarve_polygons, ignore_index=True)
    return algarve_polygons_year

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

months_2021 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
months_2022 = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11']

algarve_polygons_2021 = load_and_process_data(2021, months_2021)
algarve_polygons_2022 = load_and_process_data(2022, months_2022)

algarve_polygons_all = pd.concat([algarve_polygons_2021, algarve_polygons_2022], ignore_index=True)
algarve_polygons_all = algarve_polygons_all.to_crs(sea_data.crs)
algarve_polygons_all['centroid'] = algarve_polygons_all.geometry.to_crs(sea_data.crs).centroid

#Resumo das variáveis por mês e ano
# Lista de colunas de interesse
cols_of_interest = [
    'mean_loa', 'count', 'boat_count', 'time_diff', 'gear_number', 
    'boat_hours', 'mean_loa_per_hour', 'hour_boat_meter'
]

# Agrupamento por mês e ano e descrição das colunas de interesse
grouped_description = algarve_polygons_all.groupby(['year', 'month'])[cols_of_interest].describe()

# Salvar o resultado em um arquivo CSV (opcional)
grouped_description.to_csv('grouped_description.csv')

# Printa o resultado
print(grouped_description)


