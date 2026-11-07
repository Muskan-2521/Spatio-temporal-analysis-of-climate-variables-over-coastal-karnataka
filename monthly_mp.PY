
import os
import calendar
import xarray as xr
import matplotlib.pyplot as plt

# 1. Open ERA5 clipped NetCDF file
nc_path = r"C:\Users\MUSKAN KUMARI SINGH\Downloads\major project\clipped data\2026_coastal_karnataka_clipped.nc"

ds = xr.open_dataset(nc_path,engine="netcdf4")

# 2. Identify time coordinate
time_dim = "valid_time" if "valid_time" in ds.coords else "time"

# 3. Print available dates
print("Available time range:")
print(ds[time_dim].values)

print("Number of timestamps:", ds.sizes[time_dim])

# 4. Convert temperature from Kelvin to Celsius
temp = ds["t2m"] - 273.15

# 5. Calculate spatial average across latitude and longitude
spatial_mean = temp.mean(
    dim=["latitude", "longitude"],
    skipna=True
)

# 6. Calculate daily average temperature
daily_mean = spatial_mean.resample(
    {time_dim: "1D"}
).mean()

# 7. Create output folder
output_folder = os.path.join(
    os.path.expanduser("~"),
    "Documents",
    "ERA5_Temperature_Graphs_2026_clipped"
)

os.makedirs(output_folder, exist_ok=True)

# 8. Identify available years
years = sorted(
    set(daily_mean[time_dim].dt.year.values.tolist())
)

print("Years found:", years)

# 9. Generate monthly graphs for every year
for year in years:

    for month in range(1, 13):

        # Select data for a particular year and month
        month_data = daily_mean.where(
            (daily_mean[time_dim].dt.year == year) &
            (daily_mean[time_dim].dt.month == month),
            drop=True
        )

        plt.figure(figsize=(12, 6))

        if month_data.size > 0:

            # Extract daily temperature values
            values = month_data.values

            # Calculate monthly maximum and minimum
            monthly_max = float(month_data.max(skipna=True).values)
            monthly_min = float(month_data.min(skipna=True).values)

            # Find dates of maximum and minimum
            max_index = int(month_data.argmax(dim=time_dim).values)
            min_index = int(month_data.argmin(dim=time_dim).values)

            max_date = month_data[time_dim].values[max_index]
            min_date = month_data[time_dim].values[min_index]

            # Plot daily spatial average temperature
            plt.plot(
                month_data[time_dim].values,
                values,
                marker="o",
                markersize=4,
                linewidth=1.5,
                color="blue",
                label="Daily spatial average"
            )

            # Plot maximum temperature line
            plt.axhline(
                y=monthly_max,
                color="red",
                linestyle="--",
                linewidth=1.5,
                label=f"Monthly Maximum: {monthly_max:.2f} °C"
            )

            # Plot minimum temperature line
            plt.axhline(
                y=monthly_min,
                color="green",
                linestyle="--",
                linewidth=1.5,
                label=f"Monthly Minimum: {monthly_min:.2f} °C"
            )

            # Highlight maximum and minimum points
            plt.scatter(
                max_date,
                monthly_max,
                color="red",
                s=70,
                zorder=5
            )

            plt.scatter(
                min_date,
                monthly_min,
                color="green",
                s=70,
                zorder=5
            )

            # Label maximum temperature value
            plt.annotate(
                f"MAX: {monthly_max:.2f} °C",
                xy=(max_date, monthly_max),
                xytext=(10, 10),
                textcoords="offset points",
                color="red",
                fontweight="bold"
            )

            # Label minimum temperature value
            plt.annotate(
                f"MIN: {monthly_min:.2f} °C",
                xy=(min_date, monthly_min),
                xytext=(10, -18),
                textcoords="offset points",
                color="green",
                fontweight="bold"
            )

            plt.legend(loc="best")

        else:

            plt.text(
                0.5, 0.5,
                "No data available for this month",
                ha="center",
                va="center",
                transform=plt.gca().transAxes
            )

        # 10. Graph formatting
        plt.title(
            f"Daily Average Temperature with Monthly Maximum "
            f"and Minimum - {calendar.month_name[month]} {year}"
        )

        plt.xlabel("Date")
        plt.ylabel("Temperature (°C)")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # 11. Save graph
        file_name = (
            f"{year}_{month:02d}_"
            f"{calendar.month_name[month]}.png"
        )

        output_path = os.path.join(
            output_folder,
            file_name
        )

        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print("Saved:", output_path)

# 12. Close dataset
ds.close()

print("\nAll monthly graphs generated successfully!")
print("Graphs saved in:", output_folder)
