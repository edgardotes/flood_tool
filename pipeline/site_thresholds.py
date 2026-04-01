SITE_THRESHOLDS = {
    "morges": {
        "yellow": {"domain_p90_6h": 15.0, "domain_mean_6h": 0.0},
        "orange": {"domain_p90_6h": 25.0, "domain_mean_6h": 0.0},
        "red":    {"domain_p90_6h": 35.0, "domain_mean_6h": 0.0},
        "messages": {
            "green":  "No flooding expected.",
            "yellow": "Minor flooding is possible in the lowest parts of the site.",
            "orange": "Moderate flooding may affect low-lying sectors and access areas.",
            "red":    "Severe flooding may affect much of the Morges campsite area."
        }
    },

    "zell": {
        "yellow": {"domain_p90_6h": 0.0,  "domain_mean_6h": 0.0},
        "orange": {"domain_p90_6h": 0.0, "domain_mean_6h": 0.0},
        "red":    {"domain_p90_6h": 0.0, "domain_mean_6h": 0.0},
        "messages": {
            "green":  "No flooding expected.",
            "yellow": "Minor flooding is possible in low-lying areas of the campsite.",
            "orange": "Moderate flooding may affect internal access areas and nearby low points.",
            "red":    "Severe flooding may affect major parts of the Zell campsite area."
        }
    },

    "interlaken": {
        "yellow": {"domain_p90_6h": 10.0, "domain_mean_6h": 5.0},
        "orange": {"domain_p90_6h": 20.0, "domain_mean_6h": 9.0},
        "red":    {"domain_p90_6h": 30.0, "domain_mean_6h": 16.0},
        "messages": {
            "green":  "No flooding expected.",
            "yellow": "Minor flooding is possible in the lowest parts of the campsite.",
            "orange": "Moderate flooding may affect low-lying sectors and access areas.",
            "red":    "Severe flooding may affect much of the Interlaken campsite area."
        }
    },

    "gordevio": {
        "yellow": {"domain_p90_6h": 10.0, "domain_mean_6h": 4.5},
        "orange": {"domain_p90_6h": 40.0, "domain_mean_6h": 9.0},
        "red":    {"domain_p90_6h": 60.0, "domain_mean_6h": 17.0},
        "messages": {
            "green":  "No flooding expected.",
            "yellow": "Minor flooding is possible in the lowest parts of the campsite.",
            "orange": "Moderate flooding may affect low-lying sectors and access areas.",
            "red":    "Severe flooding may affect much of the Gordevio campsite area."
        }
    }
}
