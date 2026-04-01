from pathlib import Path
import pandas as pd

from evaluate_sites import compute_dem_domain_metrics
from select_scenario import select_morges_scenario
from write_status import write_site_status_json


# ---------------------------------------------------
# INPUTS
# ---------------------------------------------------
forecast_path = "/Users/edolores/Documents/UBERN/Collaborations/Gaby/Data/new/ICON-CH1-EPS_liestal_bl_2024_2024-06-25T15Z.nc"
dem_file = "/Users/edolores/Documents/UBERN/Collaborations/Gaby/Data/new/Morges_2m_CP.dem"

window_hours = 6
site_id = "morges"
site_name = "Camping de Morges"
canton = "VD"
lat = 46.511
lon = 6.498

out_csv = f"/Users/edolores/Documents/UBERN/Collaborations/Gaby/Data/new/{site_id}_dem_metrics_{window_hours}h_per_ensemble.csv"
#out_json = "/Users/edolores/Documents/UBERN/Collaborations/Gaby/Data/new/morges_status.json"
out_json = "/Users/edolores/Documents/UBERN/Collaborations/Gaby/flood_tool/docs/api/latest.json"


# ---------------------------------------------------
# COMPUTE METRICS
# ---------------------------------------------------
df_dem, summary = compute_dem_domain_metrics(
    forecast_path=forecast_path,
    dem_file=dem_file,
    window_hours=window_hours,
    precip_var="precipitation_amount",
)

pd.set_option("display.float_format", "{:.6f}".format)

print("\nPer-ensemble metrics:")
print(df_dem)

print("\nSummary:")
for key, value in summary.items():
    print(f"{key}: {value}")

df_dem.to_csv(out_csv, index=False)
print(f"\nSaved ensemble metrics CSV to:\n{out_csv}")


# ---------------------------------------------------
# SELECT SCENARIO
# ---------------------------------------------------
scenario_result = select_morges_scenario(summary)

print("\nSelected scenario:")
for key, value in scenario_result.items():
    print(f"{key}: {value}")


# ---------------------------------------------------
# WRITE WEBSITE JSON
# ---------------------------------------------------
selected_scenario = scenario_result["selected_scenario"]
scenario_image_path = f"./scenarios/{site_id}/{selected_scenario}.png"

write_site_status_json(
    output_json=out_json,
    site_id=site_id,
    site_name=site_name,
    canton=canton,
    lat=lat,
    lon=lon,
    scenario_result=scenario_result,
    scenario_image_path=scenario_image_path,
    source="ICON MeteoSwiss",
)

print(f"\nSaved website-style status JSON to:\n{out_json}")
