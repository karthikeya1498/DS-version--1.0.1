"""Train and evaluate the Phase 2 demand model on real hourly mobility data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.features.feature_pipeline import build_demand_features, chronological_split
from src.ml.demand.xgboost_model import DemandForecaster
from src.ml.evaluation.metrics import mae, rmse, smape


def train(input_path: str | Path = 'data/raw/mobility/hour.csv', output_path: str | Path = 'data/processed/phase2_demand_metrics.json') -> dict:
    frame = pd.read_csv(input_path); frame['timestamp'] = pd.to_datetime(frame['dteday']) + pd.to_timedelta(frame['hr'], unit='h'); frame['demand'] = frame['cnt']; frame['zone'] = 'capital_bikeshare'
    features = build_demand_features(frame[['timestamp', 'zone', 'demand']], group_col='zone'); train_frame, _, test_frame = chronological_split(features, .8, 0)
    excluded = {'timestamp', 'zone', 'demand', 'target'}; columns = [column for column in features.columns if column not in excluded]; model = DemandForecaster().fit(train_frame[columns], train_frame['target']); prediction = model.predict(test_frame[columns]); actual = test_frame['target'].to_numpy()
    result = {'dataset': str(input_path), 'rows': len(features), 'train_rows': len(train_frame), 'test_rows': len(test_frame), 'features': columns, 'model': model.metadata(), 'metrics': {'mae': mae(actual, prediction), 'rmse': rmse(actual, prediction), 'smape': smape(actual, prediction)}}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True); Path(output_path).write_text(json.dumps(result, indent=2), encoding='utf-8'); return result

if __name__ == '__main__': print(json.dumps(train(), indent=2))
