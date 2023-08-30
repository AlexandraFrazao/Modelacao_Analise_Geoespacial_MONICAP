import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
import matplotlib.pyplot as plt
import contextily as ctx

# Read the shapefile
shapefile_path = 'shapefiles/pt_10km.shp'
grid_data = gpd.read_file(shapefile_path)



# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

# Reproject the land_data to match the CRS of grid_data
grid_data = grid_data.to_crs(sea_data.crs)

# Perform spatial overlay to extract polygons not intersecting with land #how='intersection'
#non_land_polygons = gpd.overlay(grid_data, sea_data, how='intersection', keep_geom_type = False)
non_land_polygons = gpd.sjoin(grid_data, sea_data, how='inner', predicate = 'within')

# Define the extent of the grid
min_x, min_y, max_x, max_y = grid_data.total_bounds

# Create a plot
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the grid cells with thin lines and no color filling
non_land_polygons.plot(ax=ax, edgecolor='black', linewidth=0.5, facecolor='none')

# Add basemap using Contextily
ctx.add_basemap(ax, crs=grid_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)



# Set the plot extent
ax.set_xlim(min_x, max_x)
ax.set_ylim(min_y, max_y)

# Display the plot
plt.show()





# Read the shapefile
shapefile_path = 'shapefiles/pt_10km.shp'
grid_data = gpd.read_file(shapefile_path)

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

# Reproject the grid_data to match the CRS of sea_data
grid_data = grid_data.to_crs(sea_data.crs)

# Perform spatial overlay to extract polygons not intersecting with land
non_land_polygons = gpd.sjoin(grid_data, sea_data, how='inner', predicate='within')

# Define the extent of the grid
min_x, min_y, max_x, max_y = grid_data.total_bounds

# Define the bounding box for the Algarve region
min_latitude = min_y
max_latitude = 37.458
min_longitude = -12.858
max_longitude = max_x
algarve_bbox = Polygon([(min_longitude, min_latitude),
                        (max_longitude, min_latitude),
                        (max_longitude, max_latitude),
                        (min_longitude, max_latitude)])

# Filter the non_land_polygons to include only those within the Algarve region
algarve_polygons = non_land_polygons[non_land_polygons.geometry.within(algarve_bbox)]

# Create a plot
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the grid cells with thin lines and no color filling
non_land_polygons.plot(ax=ax, edgecolor='black', linewidth=0.5, facecolor='none')

# Plot the Algarve polygons with a different color
algarve_polygons.plot(ax=ax, edgecolor='green', linewidth=1, facecolor='red', alpha=0.7)

sea_data.plot(ax=ax, facecolor='none')

# Add basemap using Contextily
ctx.add_basemap(ax, crs=grid_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Set the plot extent
ax.set_xlim(min_x, max_x)
ax.set_ylim(min_y, max_y)

# Display the plot
plt.show()


# Save the Algarve polygons as a shapefile
algarve_polygons.to_file(r'shapefiles\algarve_polygons.shp')






# Read the shapefile
shapefile_path = 'shapefiles/pt_1km.shp'
grid_data = gpd.read_file(shapefile_path)

# Read the shapefile for the Portuguese sea
sea_path = 'shapefiles/eez.shp'
sea_data = gpd.read_file(sea_path)

# Reproject the grid_data to match the CRS of sea_data
grid_data = grid_data.to_crs(sea_data.crs)

# Perform spatial overlay to extract polygons not intersecting with land
non_land_polygons = gpd.sjoin(grid_data, sea_data, how='inner', predicate='within')

# Define the extent of the grid
min_x, min_y, max_x, max_y = grid_data.total_bounds

# Define the bounding box for the Algarve region
min_latitude = min_y
max_latitude = 37.458
min_longitude = -12.858
max_longitude = max_x
algarve_bbox = Polygon([(min_longitude, min_latitude),
                        (max_longitude, min_latitude),
                        (max_longitude, max_latitude),
                        (min_longitude, max_latitude)])

# Filter the non_land_polygons to include only those within the Algarve region
algarve_polygons = non_land_polygons[non_land_polygons.geometry.within(algarve_bbox)]

# Create a plot
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the grid cells with thin lines and no color filling
non_land_polygons.plot(ax=ax, edgecolor='black', linewidth=0.5, facecolor='none')

# Plot the Algarve polygons with a different color
algarve_polygons.plot(ax=ax, edgecolor='green', linewidth=1, facecolor='red', alpha=0.7)

sea_data.plot(ax=ax, facecolor='none')

# Add basemap using Contextily
ctx.add_basemap(ax, crs=grid_data.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Set the plot extent
ax.set_xlim(min_x, max_x)
ax.set_ylim(min_y, max_y)

# Display the plot
plt.show()


# Save the Algarve polygons as a shapefile
algarve_polygons.to_file(r'shapefiles\algarve_polygons_1km.shp')