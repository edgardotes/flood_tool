from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime, timezone


def write_site_status_json(
    output_json: str | Path,
    site_id: str,
    site_name: str,
    canton: str,
    lat: float,
    lon: float,
    scenario_result: dict,
    scenario_image_path: str,
    source: str = "ICON MeteoSwiss",
) -> None:
    """
    Write a website-ready JSON file for one site in multi-site format.
    """
    output_json = Path(output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "updated_utc": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "sites": [
            {
                "id": site_id,
                "name": site_name,
                "canton": canton,
                "lat": float(lat),
                "lon": float(lon),
                "selected_scenario": scenario_result["selected_scenario"],
                "alert_level": scenario_result["alert_level"],
                "message": scenario_result["message"],
                "decision_metrics": {
                    "domain_p90_6h": float(scenario_result["decision_metrics"]["domain_p90_6h"]),
                    "domain_mean_6h": float(scenario_result["decision_metrics"]["domain_mean_6h"]),
                },
                "hazard_image": scenario_image_path,
            }
        ],
    }

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)