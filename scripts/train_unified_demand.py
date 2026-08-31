"""Train demand forecasting on the unified TLC demand plus NOAA weather product."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd

from src.features.feature_pipeline import build_demand_features, chronological_split
from src.ml.demand.xgboost_model import DemandForecaster
from src.ml.evaluation.metrics import mae, rmse, smape


def train(output_path: str | Path = 'data/processed/unified_demand_metrics.json') -> dict:
    root = Path(__file__).resolve().parents[1]; demand = pd.read_csv(root / 'data/processed/unified/demand_hourly_from_tlc.csv', parse_dates=['timestamp']); weather = pd.read_csv(root / 'data/processed/unified/weather_daily.csv', parse_dates=['date']); demand['timestamp'] = pd.to_datetime(demand['timestamp'], utc=True); demand['demand'] = demand['demand'].astype(float); weather['date'] = pd.to_datetime(weather['date'], utc=True).dt.floor('D'); demand['weather_date'] = demand['timestamp'].dt.floor('D'); weather_cols = [column for column in ['tmax_c_tenths', 'tmin_c_tenths', 'precipitation_mm_tenths'] if column in weather]; demand = demand.merge(weather[['date', *weather_cols]], left_on='weather_date', right_on='date', how='left').drop(columns=['date', 'weather_date']); demand[weather_cols] = demand[weather_cols].fillna(0)
    features = build_demand_features(demand[['timestamp', 'zone_id', 'demand', *weather_cols]].rename(columns={'zone_id': 'zone'}), group_col='zone'); train_frame, _, test_frame = chronological_split(features, .8, 0); excluded = {'timestamp', 'zone', 'demand', 'target'}; columns = [column for column in features.columns if column not in excluded]; model = DemandForecaster().fit(train_frame[columns], train_frame['target']); prediction = model.predict(test_frame[columns]); actual = test_frame['target'].to_numpy(); result = {'dataset': 'data/processed/unified/demand_hourly_from_tlc.csv', 'weather_dataset': 'data/processed/unified/weather_daily.csv', 'rows': len(features), 'train_rows': len(train_frame), 'test_rows': len(test_frame), 'features': columns, 'model': model.metadata(), 'metrics': {'mae': mae(actual, prediction), 'rmse': rmse(actual, prediction), 'smape': smape(actual, prediction)}}; path = root / output_path; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(result, indent=2), encoding='utf-8'); return result

if __name__ == '__main__': print(json.dumps(train(), indent=2))
