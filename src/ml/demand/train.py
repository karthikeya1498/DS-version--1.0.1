"""Demand model training pipeline comparing XGBoost, MLP, LSTM, and Seasonal Baseline."""
from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from src.features.demand_features import build_demand_lag_features
from src.features.feature_pipeline import chronological_split
from src.ml.demand.baseline import SeasonalMean
from src.ml.demand.lstm_model import LSTMForecaster
from src.ml.demand.mlp_model import MLPForecaster
from src.ml.demand.xgboost_model import DemandForecaster
from src.ml.evaluation.metrics import mae, rmse


def train_demand_models(
    raw_df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    target_col: str = "demand",
    group_col: str | None = "zone",
) -> dict[str, Any]:
    """
    Train and evaluate demand forecasting models on chronologically split data.
    Returns comparison metrics table and fitted model artifacts.
    """
    # 1. Feature Engineering
    features_df = build_demand_lag_features(
        raw_df, timestamp_col=timestamp_col, target_col=target_col, group_col=group_col
    )
    feature_cols = [c for c in features_df.columns if c not in {timestamp_col, target_col, group_col, "target"}]

    # 2. Chronological Split (Train: 70%, Val: 15%, Test: 15%)
    train_df, val_df, test_df = chronological_split(features_df, train_fraction=0.70, validation_fraction=0.15)

    X_train, y_train = train_df[feature_cols].values, train_df["target"].values
    X_val, y_val = val_df[feature_cols].values, val_df["target"].values
    X_test, y_test = test_df[feature_cols].values, test_df["target"].values

    models: dict[str, Any] = {}
    metrics: dict[str, dict[str, float]] = {}

    # Model 1: Baseline
    base_model = SeasonalMean().fit(y_train.tolist())
    base_preds = base_model.predict(len(y_test))
    models["seasonal_mean"] = base_model
    metrics["seasonal_mean"] = {
        "mae": mae(y_test.tolist(), base_preds),
        "rmse": rmse(y_test.tolist(), base_preds),
    }

    # Model 2: XGBoost
    xgb_model = DemandForecaster(n_estimators=100, max_depth=4, learning_rate=0.08)
    xgb_model.fit(X_train, y_train, feature_names=feature_cols)
    xgb_preds = xgb_model.predict(X_test)
    models["xgboost"] = xgb_model
    metrics["xgboost"] = {
        "mae": mae(y_test.tolist(), xgb_preds),
        "rmse": rmse(y_test.tolist(), xgb_preds),
    }

    # Model 3: MLP Neural Forecaster
    mlp_model = MLPForecaster(hidden_dims=(32, 16), epochs=80, learning_rate=0.01)
    mlp_model.fit(X_train, y_train)
    mlp_preds = mlp_model.predict(X_test)
    models["mlp_neural"] = mlp_model
    metrics["mlp_neural"] = {
        "mae": mae(y_test.tolist(), mlp_preds),
        "rmse": rmse(y_test.tolist(), mlp_preds),
    }

    # Model 4: LSTM Forecaster
    lstm_model = LSTMForecaster(hidden_dim=16, sequence_length=6, epochs=60)
    raw_series = raw_df[target_col].values
    split_idx = int(len(raw_series) * 0.7)
    lstm_model.fit(raw_series[:split_idx])
    models["lstm_temporal"] = lstm_model

    return {
        "models": models,
        "metrics": metrics,
        "feature_cols": feature_cols,
        "test_records_count": len(test_df),
    }
