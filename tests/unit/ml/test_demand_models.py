"""Unit tests for demand forecasting models: XGBoost, MLP, LSTM, and training pipeline."""

import numpy as np
import pandas as pd

from src.ml.demand.lstm_model import LSTMForecaster
from src.ml.demand.mlp_model import MLPForecaster
from src.ml.demand.train import train_demand_models
from src.ml.demand.xgboost_model import DemandForecaster


def test_xgboost_demand_forecaster():
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1, (100, 5))
    # Target is linear combination + noise
    y = X[:, 0] * 3.0 + X[:, 1] * 1.5 + rng.normal(0, 0.2, 100)

    model = DemandForecaster(n_estimators=50, max_depth=3)
    model.fit(X, y)
    preds = model.predict(X[:5])

    assert len(preds) == 5
    assert model.metadata()["backend"] == "xgboost"
    assert model.metadata()["fallback_used"] is False


def test_mlp_demand_forecaster_and_activations():
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1, (100, 4))
    y = np.sum(X, axis=1) + 2.0

    mlp = MLPForecaster(hidden_dims=(16, 8), epochs=50, learning_rate=0.02)
    mlp.fit(X, y)
    preds = mlp.predict(X[:3])
    assert len(preds) == 3

    # Test activation extraction for neural visualizer
    acts = mlp.get_layer_activations(X[0])
    # input (4) -> hidden1 (16) -> hidden2 (8) -> output (1) = 4 layers
    assert len(acts) == 4
    assert len(acts[0]) == 4
    assert len(acts[1]) == 16
    assert len(acts[2]) == 8
    assert len(acts[3]) == 1


def test_lstm_temporal_forecaster():
    # Sine wave time series
    t = np.linspace(0, 50, 150)
    series = np.sin(t) + 2.0

    lstm = LSTMForecaster(hidden_dim=12, sequence_length=8, epochs=40)
    lstm.fit(series)

    recent = series[-8:]
    next_val = lstm.predict(recent)
    assert len(next_val) == 1
    assert isinstance(next_val[0], float)
    assert lstm.metadata()["model_type"] == "lstm_recurrent_forecaster"


def test_train_demand_models_pipeline():
    base_time = pd.date_range("2026-01-01", periods=100, freq="h", tz="UTC")
    df = pd.DataFrame(
        {
            "timestamp": base_time,
            "zone": "zone_A",
            "demand": [float(10 + (i % 24) + (i % 5)) for i in range(100)],
        }
    )

    result = train_demand_models(df)
    assert "models" in result
    assert "metrics" in result
    assert "xgboost" in result["metrics"]
    assert "mlp_neural" in result["metrics"]
    assert result["metrics"]["xgboost"]["mae"] >= 0.0
