from __future__ import annotations


# ------------------------------------------------------------------
# MORGES THRESHOLDS
# Edit these values after validation against historical cases.
# ------------------------------------------------------------------
MORGES_THRESHOLDS = {
    "yellow": {
        "domain_p90_6h": 15.0,
        "domain_mean_6h": 0.0,
    },
    "orange": {
        "domain_p90_6h": 25.0,
        "domain_mean_6h": 0.0,
    },
    "red": {
        "domain_p90_6h": 35.0,
        "domain_mean_6h": 0.0,
    },
}


def select_morges_scenario(summary: dict) -> dict:
    """
    Select a flood scenario for Morges using both domain_p90_6h and domain_mean_6h.

    Strategy:
    - Use ensemble medians as the operational decision metrics.
    - Require both metrics to be high for RED.
    - Allow ORANGE if p90 is high, or if both metrics are moderately high.
    - Allow YELLOW for lower but relevant signals.

    Returns
    -------
    dict
        Selected scenario and diagnostic metrics.
    """
    p90 = summary["ensemble_median_of_domain_p90"]
    mean = summary["ensemble_median_of_domain_mean"]

    t_y = MORGES_THRESHOLDS["yellow"]
    t_o = MORGES_THRESHOLDS["orange"]
    t_r = MORGES_THRESHOLDS["red"]

    # RED: both widespread and intense rainfall signal
    if p90 >= t_r["domain_p90_6h"] and mean >= t_r["domain_mean_6h"]:
        scenario = "red"
        alert_level = "red"
        message = "Severe flooding may affect much of the Morges campsite area."

    # ORANGE: high p90, or both metrics clearly elevated
    elif (
        p90 >= t_o["domain_p90_6h"] and mean >= t_o["domain_mean_6h"]
    ) or (
        p90 >= t_r["domain_p90_6h"] and mean >= t_y["domain_mean_6h"]
    ):
        scenario = "orange"
        alert_level = "orange"
        message = "Moderate flooding may affect low-lying sectors and access areas."

    # YELLOW: some relevant rainfall signal
    elif (
        p90 >= t_y["domain_p90_6h"] and mean >= t_y["domain_mean_6h"]
    ) or (
        p90 >= t_o["domain_p90_6h"]
    ):
        scenario = "yellow"
        alert_level = "yellow"
        message = "Minor flooding is possible in the lowest parts of the site."

    else:
        scenario = "green"
        alert_level = "green"
        message = "No flooding expected."

    return {
        "selected_scenario": scenario,
        "alert_level": alert_level,
        "message": message,
        "decision_metrics": {
            "domain_p90_6h": p90,
            "domain_mean_6h": mean,
        },
    }
