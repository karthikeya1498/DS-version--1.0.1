"""Reusable leakage-safe feature engineering pipeline."""

from __future__ import annotations

import pandas as pd

from src.features.demand_features import build_demand_lag_features

DEFAULT_LAGS = (1, 2, 24)
DEFAULT_WINDOWS = (3, 6, 24)


def build_demand_features(
    frame: pd.DataFrame,
    timestamp_col: str = "timestamp",
    target_col: str = "demand",
    group_col: str | None = "zone",
    horizon: int = 1,
    lags: tuple[int, ...] = DEFAULT_LAGS,
    windows: tuple[int, ...] = DEFAULT_WINDOWS,
) -> pd.DataFrame:
    """
    Build demand forecasting features with rolling means, calendar variables, and chronological lags.
    """
    return build_demand_lag_features(
        frame,
        timestamp_col=timestamp_col,
        target_col=target_col,
        group_col=group_col,
        lags=lags,
        rolling_windows=windows,
        horizon=horizon,
    )


def chronological_split(
    frame: pd.DataFrame,
    train_fraction: float = 0.8,
    validation_fraction: float = 0.0,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split time series frame chronologically without lookahead bias.
    """
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")
    if validation_fraction < 0 or (train_fraction + validation_fraction) > 1.0:
        raise ValueError("Invalid validation_fraction")

    n = len(frame)
    train_end = int(n * train_fraction)
    valid_end = int(n * (train_fraction + validation_fraction))
    return (
        frame.iloc[:train_end].copy(),
        frame.iloc[train_end:valid_end].copy(),
        frame.iloc[valid_end:].copy(),
    )


def build_features(records: list[dict]) -> list[dict]:
    """Compatibility feature transformer for operational scenario records."""
    return [
        {
            **row,
            "demand_squared": float(row.get("demand_units", 0)) ** 2,
            "priority_weight": float(row.get("priority", 1)),
        }
        for row in records
    ]
