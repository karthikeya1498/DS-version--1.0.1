"""Tests for the Phase 2 neural forecasting models.

Author: Karthikeya
"""
from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("torch")

from src.ml.demand.neural_models import MLPDemandForecaster, TemporalDemandForecaster


def test_mlp_learns_deterministic_tabular_signal():
    features = np.arange(40, dtype=np.float32).reshape(20, 2)
    target = (features[:, 0] * 0.4 + features[:, 1] * 0.8).astype(np.float32)
    model = MLPDemandForecaster(hidden_sizes=(16, 8), epochs=150, random_state=7).fit(features, target)
    predictions = model.predict(features)
    assert len(predictions) == len(target)
    assert model.metadata()["model"] == "mlp"
    assert model.loss_history[-1] < model.loss_history[0]
    assert np.mean(np.abs(np.asarray(predictions) - target)) < 4.0


def test_temporal_lstm_and_gru_predict_from_sequence_windows():
    sequences = np.arange(72, dtype=np.float32).reshape(12, 3, 2)
    target = sequences[:, -1, 0] * 0.25 + sequences[:, -1, 1] * 0.5
    for cell in ("lstm", "gru"):
        model = TemporalDemandForecaster(cell=cell, hidden_size=8, epochs=20, random_state=11).fit(sequences, target)
        predictions = model.predict(sequences[:3])
        assert len(predictions) == 3
        assert model.metadata()["model"] == cell
        assert model.loss_history[-1] < model.loss_history[0]


def test_neural_models_reject_invalid_shapes():
    with pytest.raises(ValueError, match="two-dimensional"):
        MLPDemandForecaster(epochs=2).fit(np.ones((2, 2, 1)), [1, 2])
    with pytest.raises(ValueError, match="three-dimensional"):
        TemporalDemandForecaster(epochs=2).fit(np.ones((2, 2)), [1, 2])
