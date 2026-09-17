"""Validation for the inspectable neural trace contract.

Author: Karthikeya
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app
from src.ml.demand.neural_trace import build_demo_trace


def test_trace_contains_input_hidden_output_weights_and_prediction() -> None:
    trace = build_demo_trace([1.0, 2.0, 3.0], seed=7)
    assert trace["model"] == "mlp"
    assert len(trace["layers"]) == 4
    assert trace["layers"][0]["name"] == "input"
    assert trace["layers"][-1]["name"] == "output"
    assert len(trace["weights"]) == 3
    assert trace["weights"][0]["weight"]
    assert isinstance(trace["prediction"], float)


def test_neural_trace_endpoint_returns_real_trace() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/neural/trace", json={"features": [2, 4, 8]})
    assert response.status_code == 200
    payload = response.json()
    assert payload["feature_vector"] == [2.0, 4.0, 8.0]
    assert payload["weights"]
    assert payload["layers"][1]["activation"]


def test_neural_trace_rejects_non_finite_features() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/neural/trace", json={"features": [1, "NaN"]})
    assert response.status_code == 422
