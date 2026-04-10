"""
Flood Tool – Scenario Selection Module

Description:
    Selects the most appropriate flood scenario based on thresholds and inputs.

Authors:
    Edgar Dolores-Tesillos

Contributors:
    ChatGPT (assistance)

Created:
    2026

License:
    MIT License
"""

from evaluate_sites import compute_dem_domain_metrics
from select_scenario import select_scenario
from sites_config import SITES

from pathlib import Path
import json
from datetime import datetime, timezone

FORECAST_PATH = "/Users/edolores/Documents/UBERN/Collaborations/Gaby/Data/new/ICON-CH1-EPS_liestal_bl_2024_2024-06-25T15Z.nc"
WINDOW_HOURS = 6

all_sites_status = []

for site in SITES:
    print(f"\nProcessing {site['id']}")

    df_dem, summary = compute_dem_domain_metrics(
        forecast_path=FORECAST_PATH,
        dem_file=site["dem_file"],
        window_hours=WINDOW_HOURS,
    )

    scenario_result = select_scenario(site["id"], summary)

    print(
        f"{site['id']}: scenario={scenario_result['selected_scenario']}, "
        f"p90={scenario_result['decision_metrics']['domain_p90_6h']:.2f}, "
        f"mean={scenario_result['decision_metrics']['domain_mean_6h']:.2f}"
    )

    selected_scenario = scenario_result["selected_scenario"]

    hazard_image = (
        None
        if selected_scenario == "green"
        else f"./scenarios/{site['id']}/{selected_scenario}.png"
    )

    site_status = {
        "id": site["id"],
        "name": site["name"],
        "canton": site["canton"],
        "lat": site["lat"],
        "lon": site["lon"],
        "selected_scenario": selected_scenario,
        "alert_level": scenario_result["alert_level"],
        "message": scenario_result["message"],
        "decision_metrics": scenario_result["decision_metrics"],
        "hazard_image": hazard_image,
    }

    all_sites_status.append(site_status)

# ---------------------------------------------------
# WRITE ONE COMBINED latest.json
# ---------------------------------------------------

output_json = Path("/Users/edolores/Documents/UBERN/Collaborations/Gaby/flood_tool/docs/api/latest.json")

payload = {
    "updated_utc": datetime.now(timezone.utc).isoformat(),
    "source": "ICON MeteoSwiss",
    "sites": all_sites_status
}

output_json.parent.mkdir(parents=True, exist_ok=True)

with output_json.open("w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)

print("\nSaved latest.json with all sites")
