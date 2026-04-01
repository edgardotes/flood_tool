from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
import xarray as xr


def compute_dem_domain_metrics(
    forecast_path: str | Path,
    dem_file: str | Path,
    window_hours: int = 6,
    precip_var: str = "precipitation_amount",
) -> tuple[pd.DataFrame, dict]:
    """
    Compute ensemble precipitation metrics over the DEM domain for a given forecast window.

    Parameters
    ----------
    forecast_path : str or Path
        Path to the ICON forecast NetCDF file.
    dem_file : str or Path
        Path to the DEM raster used to define the local model domain.
    window_hours : int
        Forecast accumulation window in hours.
    precip_var : str
        Name of the precipitation variable in the forecast dataset.

    Returns
    -------
    df_dem : pandas.DataFrame
        Metrics per realization over the DEM domain.
    summary : dict
        Ensemble summary metrics used later for scenario selection.
    """
    forecast_path = Path(forecast_path)
    dem_file = Path(dem_file)

    ds = xr.open_dataset(forecast_path)
    da = ds[precip_var]

    if "forecast_reference_time" in da.dims:
        da = da.isel(forecast_reference_time=0)

    required_dims = {"lead_time", "realization", "y", "x"}
    missing = required_dims - set(da.dims)
    if missing:
        raise ValueError(f"Missing expected dimensions: {missing}")

    da = da.transpose("lead_time", "realization", "y", "x")

    lead_time_hours = da["lead_time"] / np.timedelta64(1, "h")
    lead_mask = (lead_time_hours > 0) & (lead_time_hours <= window_hours)
    da_window = da.sel(lead_time=da["lead_time"][lead_mask])

    if da_window.sizes["lead_time"] == 0:
        raise ValueError(f"No lead times found in the +1h to +{window_hours}h window.")

    da_window_acc = da_window.sum(dim="lead_time")

    with rasterio.open(dem_file) as src:
        dem_left, dem_bottom, dem_right, dem_top = src.bounds

    x_ascending = bool(da_window_acc.x.values[0] < da_window_acc.x.values[-1])
    y_ascending = bool(da_window_acc.y.values[0] < da_window_acc.y.values[-1])

    x_slice = slice(dem_left, dem_right) if x_ascending else slice(dem_right, dem_left)
    y_slice = slice(dem_bottom, dem_top) if y_ascending else slice(dem_top, dem_bottom)

    da_dem = da_window_acc.sel(x=x_slice, y=y_slice)

    if da_dem.sizes["x"] == 0 or da_dem.sizes["y"] == 0:
        raise ValueError("DEM spatial subset is empty. Check DEM bounds vs forecast coordinates.")

    rows = []

    for ens in da_dem["realization"].values:
        arr = da_dem.sel(realization=ens).values
        arr = arr[np.isfinite(arr)]

        if len(arr) == 0:
            domain_sum = np.nan
            domain_mean = np.nan
            domain_p80 = np.nan
            domain_p90 = np.nan
            domain_p99_9 = np.nan
            domain_max = np.nan
            n_pixels = 0
        else:
            domain_sum = float(np.sum(arr))
            domain_mean = float(np.mean(arr))
            domain_p80 = float(np.percentile(arr, 80))
            domain_p90 = float(np.percentile(arr, 90))
            domain_p99_9 = float(np.percentile(arr, 99.9))
            domain_max = float(np.max(arr))
            n_pixels = int(len(arr))

        rows.append({
            "realization": int(ens),
            "n_pixels_dem_domain": n_pixels,
            f"domain_sum_{window_hours}h": domain_sum,
            f"domain_mean_{window_hours}h": domain_mean,
            f"domain_p80_{window_hours}h": domain_p80,
            f"domain_p90_{window_hours}h": domain_p90,
            f"domain_p99_9_{window_hours}h": domain_p99_9,
            f"domain_max_{window_hours}h": domain_max,
        })

    df_dem = pd.DataFrame(rows)

    mean_col = f"domain_mean_{window_hours}h"
    p90_col = f"domain_p90_{window_hours}h"

    summary = {
        "window_hours": window_hours,
        "metric_mean_name": mean_col,
        "metric_p90_name": p90_col,
        "ensemble_mean_of_domain_mean": float(df_dem[mean_col].mean()),
        "ensemble_median_of_domain_mean": float(df_dem[mean_col].median()),
        "ensemble_mean_of_domain_p90": float(df_dem[p90_col].mean()),
        "ensemble_median_of_domain_p90": float(df_dem[p90_col].median()),
        "n_ensembles": int(len(df_dem)),
    }

    ds.close()
    return df_dem, summary
