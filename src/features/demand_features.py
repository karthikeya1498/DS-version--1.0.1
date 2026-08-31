"""Leakage-safe demand forecasting feature engineering."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


def extract_temporal_features(timestamps: pd.Series) -> pd.DataFrame:
    """Extract cyclical hour, day of week, and weekend indicators."""
    dt = pd.to_datetime(timestamps, utc=True)
    hours = dt.dt.hour
    dow = dt.dt.dayofweek
    return pd.DataFrame(
        {
            "hour": hours,
            "hour_sin": np.sin(2 * np.pi * hours / 24.0),
            "hour_cos": np.cos(2 * np.pi * hours / 24.0),
            "day_of_week": dow,
            "day_sin": np.sin(2 * np.pi * dow / 7.0),
            "day_cos": np.cos(2 * np.pi * dow / 7.0),
            "is_weekend": (dow >= 5).astype(int),
            "day_of_month": dt.dt.day,
        }
    )


def build_demand_lag_features(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    target_col: str = "demand",
    group_col: str | None = "zone",
    lags: Sequence[int] = (1, 2, 3, 24),
    rolling_windows: Sequence[int] = (3, 6, 24),
    horizon: int = 1,
) -> pd.DataFrame:
    """
    Build leak-safe lag and rolling window features for time series demand.
    Ensures rolling statistics use strictly prior values via shift(1).
    """
    if timestamp_col not in df or target_col not in df:
        raise ValueError(f"Required columns: {timestamp_col}, {target_col}")

    data = df.copy()
    data[timestamp_col] = pd.to_datetime(data[timestamp_col], utc=True)
    sort_cols = [group_col, timestamp_col] if group_col and group_col in data else [timestamp_col]
    data = data.sort_values(sort_cols).reset_index(drop=True)

    grouped = (
        data.groupby(group_col, sort=False)[target_col]
        if group_col and group_col in data
        else data[target_col]
    )

    for lag in lags:
        data[f"lag_{lag}"] = grouped.shift(lag)

    for w in rolling_windows:
        prior = grouped.shift(1)
        if group_col and group_col in data:
            data[f"rolling_mean_{w}"] = (
                prior.rolling(w, min_periods=w).mean().reset_index(level=0, drop=True)
            )
            data[f"rolling_std_{w}"] = (
                prior.rolling(w, min_periods=w).std().fillna(0.0).reset_index(level=0, drop=True)
            )
        else:
            data[f"rolling_mean_{w}"] = prior.rolling(w, min_periods=w).mean()
            data[f"rolling_std_{w}"] = prior.rolling(w, min_periods=w).std().fillna(0.0)

    temporal = extract_temporal_features(data[timestamp_col])
    for col in temporal.columns:
        data[col] = temporal[col]

    data["target"] = (
        grouped.shift(-horizon)
        if group_col and group_col in data
        else data[target_col].shift(-horizon)
    )
    return data.dropna().reset_index(drop=True)
