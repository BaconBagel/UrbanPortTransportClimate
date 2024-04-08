import rasterio
from rasterio.plot import show
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rasterio import mask

# Pah to the output GeoTIFF file
output_file_path =  "C:/Users/leide/Downloads/floodrisks/data/final_output_pop-only_Ocean_flood_extent_2071_2100_RCP85_with_protection.tif"


population_density_file_path = "C:/Users/leide/Downloads/JRC_GRID_2018/JRC_1K_POP_2018.tif"
# Path to the shapefile
municipality_shapefile_path = "C:/Users/leide/Downloads/GISfileswk1/municipalities2017.shp"

# Read the municipality shapefile
municipalities = gpd.read_file(municipality_shapefile_path)

# Open the output GeoTIFF file
with rasterio.open(output_file_path) as src:
    # Read the raster data
    data = src.read(1)
    # Get the coordinate reference system
    crs = src.crs
    # Get the bounds of the raster data
    bounds = src.bounds

    # Print bounds of raster data
    print("Bounds of Raster Data:")
    print("Minimum Longitude:", bounds.left)
    print("Minimum Latitude:", bounds.bottom)
    print("Maximum Longitude:", bounds.right)
    print("Maximum Latitude:", bounds.top)

    # Reproject the municipality boundaries to match the CRS of the raster data
    municipalities = municipalities.to_crs(crs)

    # Get the bounds of the original municipality boundaries
    original_bounds = municipalities.total_bounds

    # Mask the raster data outside the shapefile boundaries
    masked_data, _ = rasterio.mask.mask(src, municipalities.geometry, crop=True)

    # Define the threshold for the pixel values to be considered
    threshold = 0
    masked_data[masked_data < threshold] = np.nan

    # Initialize list to store aggregated values
    aggregated_values = []

    # Iterate over each municipality
    for index, municipality in municipalities.iterrows():
        geom = municipality.geometry
        municipality_masked_data, _ = rasterio.mask.mask(src, [geom], crop=True)
        municipality_masked_data[municipality_masked_data < threshold] = 0
        aggregated_value = np.nansum(municipality_masked_data)
        aggregated_values.append(aggregated_value)

    # Create a DataFrame with municipality names and their corresponding aggregated values
    aggregated_values_df = pd.DataFrame(
        {"Municipality_Name": municipalities["GM_NAAM"], "Sum_Pixel_Values": aggregated_values, "Population": municipalities["AANT_INW"]}
    )

    # Calculate the pixel value per capita
    aggregated_values_df["Pixel_Value_Per_Capita"] = aggregated_values_df["Sum_Pixel_Values"]/municipalities["AANT_INW"]

    # Save the DataFrame to a CSV file
    aggregated_values_df.to_csv("unweighted_River_flood_extent_2071_2100_RCP85_with_protection.csv", index=False)

    # Plot 1: Raster data with municipality boundaries as mask
    plt.figure(figsize=(12, 8))
    plt.gca().set_facecolor('white')
    max_value = np.nanmax(masked_data)
    show(masked_data, transform=src.transform,
         extent=(original_bounds[0], original_bounds[2], original_bounds[1], original_bounds[3]),
         cmap='hsv', vmin=-1, vmax=max_value)
    municipalities.plot(ax=plt.gca(), facecolor='none', edgecolor='red')
    dummy_image = plt.imshow(np.squeeze(masked_data), cmap='hsv')
    plt.colorbar(dummy_image, label='Processed Pixel Values')
    plt.title('Flood Masked Population')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

    # Plot 2: Raster data with municipality boundaries filled with pixel value per capita
    plt.figure(figsize=(12, 8))
    plt.gca().set_facecolor('white')
    municipalities = municipalities.merge(aggregated_values_df, left_on='GM_NAAM', right_on='Municipality_Name')
    municipalities.plot(column='Pixel_Value_Per_Capita', ax=plt.gca(), cmap='viridis', edgecolor='black', linewidth=0.5, legend=True)
    plt.title('Coastal 1000y Flood Risk Area Probabilities * Population - Standardised: RCP85 - 2070-2100 - Protected ')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()