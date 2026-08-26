"""Train an XGBoost-compatible model on UCI daily logistics demand."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
except ImportError:
    XGBRegressor = None


def load_data(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=";")
    frame.columns = [column.strip() for column in frame.columns]
    target = next(column for column in frame.columns if "Target" in column)
    frame = frame.rename(columns={target: "target"})
    frame["row_index"] = range(len(frame))
    frame["demand_lag_1"] = frame["target"].shift(1)
    frame["demand_lag_7"] = frame["target"].shift(7)
    frame["demand_rolling_7_mean"] = frame["target"].shift(1).rolling(7, min_periods=7).mean()
    frame["demand_rolling_14_mean"] = frame["target"].shift(1).rolling(14, min_periods=14).mean()
    feature_columns = [column for column in frame.columns if column != "target"]
    return frame.dropna(subset=feature_columns).reset_index(drop=True)


def evaluate(
    path="data/raw/logistics/Daily_Demand_Forecasting_Orders.csv",
    output="data/processed/logistics_forecast_metrics.json",
):
    frame = load_data(path)
    features = [column for column in frame.columns if column != "target"]
    split = int(len(frame) * 0.8)
    train, test = frame.iloc[:split], frame.iloc[split:]
    models = {
        "gradient_boosting": GradientBoostingRegressor(
            random_state=42, n_estimators=100, max_depth=2, learning_rate=0.05
        )
    }
    if XGBRegressor is not None:
        models["xgboost"] = XGBRegressor(
            n_estimators=150,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=2,
        )
    results = {
        "dataset": "UCI Daily Demand Forecasting Orders",
        "rows_after_history": len(frame),
        "features": features,
        "split": {"train": len(train), "test": len(test)},
        "models": {},
    }
    baseline = [float(train.target.mean())] * len(test)
    results["models"]["train_mean"] = {
        "mae": mean_absolute_error(test.target, baseline),
        "rmse": mean_squared_error(test.target, baseline) ** 0.5,
        "r2": r2_score(test.target, baseline),
    }
    for name, model in models.items():
        model.fit(train[features], train.target)
        prediction = model.predict(test[features])
        results["models"][name] = {
            "mae": mean_absolute_error(test.target, prediction),
            "rmse": mean_squared_error(test.target, prediction) ** 0.5,
            "r2": r2_score(test.target, prediction),
        }
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    print(json.dumps(evaluate(sys.argv[1] if len(sys.argv) > 1 else None), indent=2))
