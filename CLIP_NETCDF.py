
import xarray as xr
import geopandas as gpd
import rioxarray
import os
os.environ["SHAPE_RESTORE_SHX"]="YES"

# ---------------------------------
# 1. File paths
# ---------------------------------

nc_path = r"C:\Users\MUSKAN KUMARI SINGH\Downloads\59a768b6d5a3d7e496ed4758cc2a97cd (1)\reanalysis-era5-single-levels-timeseries-sfc8apcuh2j.nc"

shp_path = r"C:\Users\MUSKAN KUMARI SINGH\Downloads\coastal_karnataka_redd.shp"
output_path = r"C:\Users\MUSKAN KUMARI SINGH\Downloads\major project\clipped data\2025_coastal_karnataka_clipped.nc"
# ---------------------------------
# 2. Open original NetCDF
# ---------------------------------

ds = xr.open_dataset(nc_path)

print("Original dataset:")
print(ds)


# ---------------------------------
# 3. Open coastal Karnataka boundary
# ---------------------------------




# Read coastal Karnataka shapefile
gdf = gpd.read_file(shp_path)

# Check CRS
print("Original CRS:", gdf.crs)

# Assign CRS if missing
if gdf.crs is None:
    gdf = gdf.set_crs("EPSG:4326")
else:
    gdf = gdf.to_crs("EPSG:4326")

print("Updated CRS:", gdf.crs)

print(gdf.head())


# ---------------------------------
# 4. Identify coordinate names
# ---------------------------------

if "longitude" in ds.coords:
    lon_name = "longitude"
elif "lon" in ds.coords:
    lon_name = "lon"
else:
    raise ValueError("Longitude coordinate not found")

if "latitude" in ds.coords:
    lat_name = "latitude"
elif "lat" in ds.coords:
    lat_name = "lat"
else:
    raise ValueError("Latitude coordinate not found")


# ---------------------------------
# 5. Set spatial dimensions
# ---------------------------------

ds = ds.rio.set_spatial_dims(
    x_dim=lon_name,
    y_dim=lat_name
)

ds = ds.rio.write_crs("EPSG:4326")


# ---------------------------------
# 6. Clip entire dataset
# ---------------------------------

clipped_ds = ds.rio.clip(
    gdf.geometry,
    gdf.crs,
    drop=True,
    all_touched=False
)


# ---------------------------------
# 7. Save clipped NetCDF
# ---------------------------------

clipped_ds.to_netcdf(output_path)

print("\nClipping completed successfully!")
print("Saved at:", output_path)

print("\nClipped dataset:")
print(clipped_ds)

# Close datasets
ds.close()
