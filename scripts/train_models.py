
"""Train and evaluate the demand forecasting subsystem on UCI Bike Sharing data."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
try:
    from xgboost import XGBRegressor
except ImportError:
    XGBRegressor = None
from src.ml.demand.baseline import SeasonalMean

BASE_FEATURES = ['season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed']
LAG_FEATURES = ['demand_lag_1', 'demand_lag_24', 'demand_rolling_24_mean', 'demand_rolling_168_mean']
FEATURES = BASE_FEATURES + LAG_FEATURES

def load_hourly(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, parse_dates=['dteday'])
    frame['timestamp'] = frame['dteday'] + pd.to_timedelta(frame['hr'], unit='h')
    frame = frame.sort_values('timestamp').reset_index(drop=True)
    # Shift before rolling so the target at time t is never included in its own features.
    frame['demand_lag_1'] = frame['cnt'].shift(1)
    frame['demand_lag_24'] = frame['cnt'].shift(24)
    frame['demand_rolling_24_mean'] = frame['cnt'].shift(1).rolling(24, min_periods=24).mean()
    frame['demand_rolling_168_mean'] = frame['cnt'].shift(1).rolling(168, min_periods=168).mean()
    return frame.dropna(subset=FEATURES).reset_index(drop=True)

def evaluate(path='data/raw/mobility/hour.csv', output='data/processed/forecast_metrics.json'):
    frame = load_hourly(path)
    split = int(len(frame) * 0.8)
    train, test = frame.iloc[:split], frame.iloc[split:]
    x_train, x_test = train[FEATURES], test[FEATURES]
    y_train, y_test = train['cnt'], test['cnt']
    models = {'gradient_boosting': GradientBoostingRegressor(random_state=42, n_estimators=200, max_depth=3, learning_rate=.05), 'random_forest': RandomForestRegressor(random_state=42, n_estimators=100, n_jobs=-1, max_depth=16)}
    if XGBRegressor is not None:
        models['xgboost'] = XGBRegressor(n_estimators=300, max_depth=6, learning_rate=.05, subsample=.9, colsample_bytree=.9, objective='reg:squarederror', random_state=42, n_jobs=2)
    results = {'dataset': 'UCI Bike Sharing hourly', 'rows': len(frame), 'features': FEATURES, 'split': {'train': len(train), 'test': len(test)}, 'models': {}}
    baseline = SeasonalMean().fit(y_train.tolist()).predict(len(y_test))
    results['models']['seasonal_mean'] = {'mae': mean_absolute_error(y_test, baseline), 'rmse': mean_squared_error(y_test, baseline) ** .5, 'r2': r2_score(y_test, baseline)}
    for name, model in models.items():
        model.fit(x_train, y_train); predictions = model.predict(x_test)
        results['models'][name] = {'mae': mean_absolute_error(y_test, predictions), 'rmse': mean_squared_error(y_test, predictions) ** .5, 'r2': r2_score(y_test, predictions)}
    target = Path(output); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(results, indent=2), encoding='utf-8')
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--data', default='data/raw/mobility/hour.csv'); parser.add_argument('--output', default='data/processed/forecast_metrics.json'); args = parser.parse_args()
    print(json.dumps(evaluate(args.data, args.output), indent=2))
