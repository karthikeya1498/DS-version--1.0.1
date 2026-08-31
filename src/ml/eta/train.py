"""Training pipeline for ETA travel time forecasting models."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from src.features.eta_features import build_eta_features_df
from src.features.feature_pipeline import chronological_split
from src.ml.eta.baseline import MeanEta
from src.ml.eta.mlp_model import EtaMLPForecaster
from src.ml.eta.xgboost_model import EtaForecaster
from src.ml.evaluation.metrics import mae, rmse


def train_eta_models(journey_records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Train and evaluate ETA models on historical trip records."""
    df = build_eta_features_df(journey_records)
    feature_cols = [c for c in df.columns if c != "target"]

    train_df, val_df, test_df = chronological_split(df, train_fraction=0.70, validation_fraction=0.15)

    X_train, y_train = train_df[feature_cols].values, train_df["target"].values
    X_test, y_test = test_df[feature_cols].values, test_df["target"].values

    models: dict[str, Any] = {}
    metrics: dict[str, dict[str, float]] = {}

    # 1. Baseline
    mean_model = MeanEta().fit(y_train.tolist())
    mean_preds = mean_model.predict(len(y_test))
    models["mean_baseline"] = mean_model
    metrics["mean_baseline"] = {
        "mae": mae(y_test.tolist(), mean_preds),
        "rmse": rmse(y_test.tolist(), mean_preds),
    }

    # 2. XGBoost ETA
    xgb_eta = EtaForecaster(n_estimators=100, max_depth=4)
    xgb_eta.fit(X_train, y_train, feature_names=feature_cols)
    xgb_preds = xgb_eta.predict(X_test)
    models["xgboost"] = xgb_eta
    metrics["xgboost"] = {
        "mae": mae(y_test.tolist(), xgb_preds),
        "rmse": rmse(y_test.tolist(), xgb_preds),
    }

    # 3. Neural MLP ETA
    mlp_eta = EtaMLPForecaster(hidden_dims=(32, 16), epochs=70, learning_rate=0.01)
    mlp_eta.fit(X_train, y_train)
    mlp_preds = mlp_eta.predict(X_test)
    models["mlp_neural"] = mlp_eta
    metrics["mlp_neural"] = {
        "mae": mae(y_test.tolist(), mlp_preds),
        "rmse": rmse(y_test.tolist(), mlp_preds),
    }

    return {
        "models": models,
        "metrics": metrics,
        "feature_cols": feature_cols,
        "test_count": len(test_df),
    }
