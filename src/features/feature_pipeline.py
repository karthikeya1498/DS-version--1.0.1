"""Reusable leakage-safe feature engineering for demand forecasting."""
from __future__ import annotations

import pandas as pd

DEFAULT_LAGS = (1, 2, 24)
DEFAULT_WINDOWS = (3, 6, 24)

def build_demand_features(frame: pd.DataFrame, timestamp_col: str = 'timestamp', target_col: str = 'demand', group_col: str | None = 'zone', horizon: int = 1, lags: tuple[int, ...] = DEFAULT_LAGS, windows: tuple[int, ...] = DEFAULT_WINDOWS) -> pd.DataFrame:
    if timestamp_col not in frame or target_col not in frame: raise ValueError(f'required columns: {timestamp_col}, {target_col}')
    result = frame.copy(); result[timestamp_col] = pd.to_datetime(result[timestamp_col], utc=True); result = result.sort_values([group_col, timestamp_col] if group_col and group_col in result else [timestamp_col]).reset_index(drop=True)
    grouped = result.groupby(group_col, sort=False)[target_col] if group_col and group_col in result else result[target_col]
    for lag in lags: result[f'lag_{lag}'] = grouped.shift(lag)
    for window in windows:
        prior = grouped.shift(1)
        result[f'rolling_mean_{window}'] = prior.rolling(window, min_periods=window).mean().reset_index(level=0, drop=True) if group_col and group_col in result else prior.rolling(window, min_periods=window).mean()
    result['hour'] = result[timestamp_col].dt.hour; result['day_of_week'] = result[timestamp_col].dt.dayofweek; result['day_of_month'] = result[timestamp_col].dt.day; result['weekend'] = (result['day_of_week'] >= 5).astype(int)
    result['target'] = grouped.shift(-horizon) if group_col and group_col in result else result[target_col].shift(-horizon)
    return result.dropna().reset_index(drop=True)

def chronological_split(frame: pd.DataFrame, train_fraction: float = .8, validation_fraction: float = 0.0) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not 0 < train_fraction < 1: raise ValueError('train_fraction must be between 0 and 1')
    n = len(frame); train_end = int(n * train_fraction); valid_end = int(n * (train_fraction + validation_fraction)); return frame.iloc[:train_end].copy(), frame.iloc[train_end:valid_end].copy(), frame.iloc[valid_end:].copy()

def build_features(records):
    return [{**row, 'demand_squared': float(row.get('demand_units', 0)) ** 2, 'priority_weight': float(row.get('priority', 1))} for row in records]
