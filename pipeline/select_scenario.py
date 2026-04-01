from __future__ import annotations
from site_thresholds import SITE_THRESHOLDS

# ============================================================
# SITE-SPECIFIC THRESHOLDS
# Edit these values after calibration with historical cases
# and your precomputed flood scenarios.
# ============================================================

def _validate_site(site_id: str) -> dict:
    if site_id not in SITE_THRESHOLDS:
        available = ", ".join(sorted(SITE_THRESHOLDS))
        raise ValueError(
            f"Unknown site_id '{site_id}'. Available site_ids: {available}"
        )
    return SITE_THRESHOLDS[site_id]


def _extract_metrics(summary: dict) -> tuple[float, float]:
    """
    Use ensemble medians as operational decision metrics.
    """
    try:
        p90 = float(summary["ensemble_median_of_domain_p90"])
        mean = float(summary["ensemble_median_of_domain_mean"])
    except KeyError as exc:
        raise KeyError(
            f"Missing expected key in summary: {exc}. "
            "Expected keys: 'ensemble_median_of_domain_p90' and "
            "'ensemble_median_of_domain_mean'."
        ) from exc

    return p90, mean


def select_scenario(site_id: str, summary: dict) -> dict:
    """
    Select a flood scenario for a given site using:
      - domain_p90_6h
      - domain_mean_6h

    Strategy:
      - RED requires both metrics to be high.
      - ORANGE requires either both metrics moderately high,
        or a very strong p90 together with at least yellow-level mean.
      - YELLOW requires either both metrics at yellow level,
        or p90 already at orange level.
      - Otherwise GREEN.
    """
    config = _validate_site(site_id)
    p90, mean = _extract_metrics(summary)

    t_y = config["yellow"]
    t_o = config["orange"]
    t_r = config["red"]
    messages = config["messages"]

    if p90 >= t_r["domain_p90_6h"] and mean >= t_r["domain_mean_6h"]:
        scenario = "red"

    elif (
        (p90 >= t_o["domain_p90_6h"] and mean >= t_o["domain_mean_6h"])
        or
        (p90 >= t_r["domain_p90_6h"] and mean >= t_y["domain_mean_6h"])
    ):
        scenario = "orange"

    elif (
        (p90 >= t_y["domain_p90_6h"] and mean >= t_y["domain_mean_6h"])
        or
        (p90 >= t_o["domain_p90_6h"])
    ):
        scenario = "yellow"

    else:
        scenario = "green"

#    print(
#    f"{site['id']}: scenario={scenario_result['selected_scenario']}, "
#    f"p90={scenario_result['decision_metrics']['domain_p90_6h']:.2f}, "
#    f"mean={scenario_result['decision_metrics']['domain_mean_6h']:.2f}"
#    )

    return {
        "selected_scenario": scenario,
        "alert_level": scenario,
        "message": messages[scenario],
        "decision_metrics": {
            "domain_p90_6h": p90,
            "domain_mean_6h": mean,
        },
        "thresholds_used": {
            "yellow": t_y,
            "orange": t_o,
            "red": t_r,
        },
    }
