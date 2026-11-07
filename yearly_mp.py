

import os
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

# ---------- Paths ----------

nc_path = r"C:\Users\MUSKAN KUMARI SINGH\Downloads\major project\clipped data\2026_coastal_karnataka_clipped.nc"
out_dir = r"C:\Users\MUSKAN KUMARI SINGH\Downloads\major project\OUTPUTS_CLIPPED"

os.makedirs(out_dir, exist_ok=True)   # creates the folder if missing
print("Saving outputs to:", out_dir)

# ---------- Load data ----------
ds = xr.open_dataset(nc_path)
time_name = "valid_time" if "valid_time" in ds.coords else "time"

# Temperature in Celsius
temp_c = ds["t2m"] - 273.15

# Combine expver if present (mixed ERA5/ERA5T)
if "expver" in temp_c.dims:
    temp_c = temp_c.mean("expver")

# ---------- Average over all latitudes and longitudes ----------
spatial_dims = [d for d in ["latitude", "longitude"] if d in temp_c.dims]
if spatial_dims:
    if "latitude" in temp_c.dims:
        weights = np.cos(np.deg2rad(temp_c["latitude"]))
        temp_avg = temp_c.weighted(weights).mean(dim=spatial_dims)
    else:
        temp_avg = temp_c.mean(dim=spatial_dims)
else:
    temp_avg = temp_c

# ---------- Monthly mean ----------
monthly = temp_avg.resample({time_name: "1MS"}).mean()

years = sorted(set(monthly[time_name].dt.year.values))
month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
print("Years found:", years)

# ---------- One graph per year ----------
for yr in years:
    m = monthly.sel({time_name: str(yr)})
    plt.figure(figsize=(9, 4))
    plt.plot(m[time_name].dt.month.values, m.values, marker="o")
    plt.xticks(range(1, 13), month_labels)
    plt.title(f"Monthly mean temperature (spatial average) - {yr}")
    plt.xlabel("Month")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    plt.tight_layout()
    path = os.path.join(out_dir, f"monthly_temp_{yr}.png")
    plt.savefig(path, dpi=150)
    print("Saved:", path)
    plt.show()
    plt.close()

# ---------- Comparison graph ----------
plt.figure(figsize=(9, 4))
for yr in years:
    m = monthly.sel({time_name: str(yr)})
    plt.plot(m[time_name].dt.month.values, m.values, marker="o", label=str(yr))
plt.xticks(range(1, 13), month_labels)
plt.title("Monthly mean temperature - year comparison")
plt.xlabel("Month")
plt.ylabel("Temperature (°C)")
plt.legend()
plt.grid(True)
plt.tight_layout()
path = os.path.join(out_dir, "monthly_temp_comparison.png")
plt.savefig(path, dpi=150)
print("Saved:", path)
plt.show()
plt.close()

# ---------- Save CSV ----------
out = monthly.to_dataframe(name="t2m_celsius").reset_index()
out["year"] = out[time_name].dt.year
out["month"] = out[time_name].dt.month
csv_path = os.path.join(out_dir, "monthly_mean_temperature.csv")
out.to_csv(csv_path, index=False)
print("Saved:", csv_path)

print("\nFiles in output folder:", os.listdir(out_dir))
