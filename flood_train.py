import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import matplotlib.pyplot as plt

# Threshold for setting depth to 0
threshold = -1000000  # Adjust this threshold as needed

# Path to your GeoTIFF files
depth_file_path = "C:/Users/leide/Downloads/Pan-European data sets of river flood probability of occurrence under present and future climate_1_all/data/River_flood_extent_2071_2100_RCP85_with_protection.tif"
#depth_file_path =  "C:/Users/leide/Downloads/floodrisks/data/Coastal_flood_extent_2071_2100_RCP45_with_protection.tif"
population_density_file_path = "C:/Users/leide/Downloads/JRC_GRID_2018/JRC_1K_POP_2018.tif"
with rasterio.open(depth_file_path) as src:
    # Read the raster data
    population_data = src.read(1)

    # Plot the population density data
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(population_data, cmap='viridis')
    ax.set_title('Raw Flood Risk RCP85 2070-2100 With Protection')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.show()

# Output file path
output_file_path = "C:/Users/leide/Downloads/floodrisks/data/simple_weights_River_flood_extent_2071_2100_RCP85_with_protection.tif"

# Open the GeoTIFF files
with rasterio.open(depth_file_path) as depth_dataset, rasterio.open(population_density_file_path) as density_dataset:
    # Read the raster data
    depth_data = depth_dataset.read(1)  # Depth data
    density_data = density_dataset.read(1)  # Population density data

    # Get nodata values
    depth_nodata = depth_dataset.nodata
    density_nodata = density_dataset.nodata

    # Replace nodata values with 0
    depth_data[np.isnan(depth_data)] = 0
    density_data[np.isnan(density_data)] = 0
    # Replace nodata values with 0
    density_data[density_data == density_nodata] = 0

    # Get metadata
    depth_metadata = depth_dataset.meta
    density_metadata = density_dataset.meta

    # Reproject depth data to match density data
    # Reproject population density data to match depth data
    density_data_resampled = np.zeros_like(depth_data)
    reproject(
        source=density_data,
        destination=density_data_resampled,
        src_transform=density_dataset.transform,
        src_crs=density_dataset.crs,
        dst_transform=depth_dataset.transform,
        dst_crs=depth_dataset.crs,
        resampling=Resampling.sum
    )

    # Now use density_data_resampled instead of density_data

    # Find the most common value in depth data
    unique_values, counts = np.unique(depth_data, return_counts=True)
    most_common_value = unique_values[np.argmax(counts)]

    # Set the most common value to 0 in depth data
    depth_data[depth_data == most_common_value] = 0

    # Apply threshold to set depths below the threshold to 0
    depth_data[depth_data < threshold] = 0
    #depth_data = np.where(depth_data > 0, 1 / depth_data, 0)

    # Multiply depth data with resampled population density data
    depth_data_with_density = depth_data * density_data_resampled

    # Convert the array to a floating-point type
    depth_data_with_density = depth_data_with_density.astype(float)

    # Write the final TIFF with geographic information
    with rasterio.open(
            output_file_path,
            'w',
            driver='GTiff',
            height=depth_data_with_density.shape[0],
            width=depth_data_with_density.shape[1],
            count=1,
            dtype=rasterio.float64,
            crs=depth_metadata['crs'],
            transform=depth_dataset.transform,  # Use the original transform
            nodata=0  # Set nodata value to 0
    ) as dst:
        dst.write(depth_data_with_density, 1)

    print(f"Output written to {output_file_path}")

# Print metadata
print("Depth Metadata:")
print(depth_metadata)

print("Population Density Metadata:")
print(density_metadata)
