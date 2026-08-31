"""Unit tests for ETA travel time models and pipeline."""

import numpy as np

from src.features.eta_features import build_eta_feature_row
from src.ml.eta.train import train_eta_models


def test_eta_xgboost_and_mlp():
    rng = np.random.default_rng(42)
    # Generate 100 simulated journey records
    records = []
    for i in range(100):
        dist = float(rng.uniform(2.0, 30.0))
        traffic = float(rng.uniform(1.0, 2.0))
        speed = 40.0
        time_min = (dist / speed) * 60.0 * traffic + float(rng.normal(0, 1.0))
        row = build_eta_feature_row(distance_km=dist, traffic_multiplier=traffic)
        row["target"] = max(1.0, time_min)
        records.append(row)

    res = train_eta_models(records)
    assert "xgboost" in res["models"]
    assert "mlp_neural" in res["models"]
    assert res["metrics"]["xgboost"]["rmse"] < 10.0
    assert res["metrics"]["mlp_neural"]["rmse"] < 15.0

    # Ensure single-sample predictions are strictly positive
    xgb_m = res["models"]["xgboost"]
    single_pred = xgb_m.predict(
        np.array([[5.0, 7.5, 1.0, 0.0, 1.0, 1.0, 7.5, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0]])
    )
    assert len(single_pred) == 1
    assert single_pred[0] > 0.0
