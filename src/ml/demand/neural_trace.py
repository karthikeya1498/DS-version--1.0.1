"""Inspectable neural-network inference traces for the OPTIMA-X dashboard.

Author: Karthikeya
"""
from __future__ import annotations

from typing import Any

import numpy as np

from src.ml.demand.neural_models import MLPDemandForecaster


def _as_float_matrix(value: Any) -> list[list[float]]:
    return np.asarray(value, dtype=np.float32).round(6).tolist()


def build_demo_trace(features: list[float], *, seed: int = 42) -> dict[str, Any]:
    """Fit a deterministic MLP and return an inspectable single-example trace.

    The fitting data is deliberately small and deterministic. In production callers can
    replace this helper with a registry-loaded model while retaining the same wire format.
    """
    if not features:
        raise ValueError("features must contain at least one value")
    if len(features) > 12:
        raise ValueError("features must contain at most twelve values")
    x = np.asarray(features, dtype=np.float32)
    if not np.isfinite(x).all():
        raise ValueError("features must contain finite numbers")
    training = np.vstack([x * 0.5 + offset for offset in (-2.0, -1.0, 0.0, 1.0, 2.0)]).astype(np.float32)
    target = (training @ np.linspace(0.4, 1.0, x.size, dtype=np.float32)) + 10.0
    model = MLPDemandForecaster(hidden_sizes=(8, 4), epochs=45, random_state=seed).fit(training, target)
    assert model.model is not None
    assert model.feature_scaler is not None
    assert model.target_scaler is not None

    torch = __import__("torch")
    scaled = model.feature_scaler.transform(x.reshape(1, -1))
    tensor = torch.from_numpy(scaled)
    activations: list[np.ndarray] = [scaled]
    weights: list[dict[str, Any]] = []
    current = tensor
    linear_index = 0
    model.model.eval()
    with torch.no_grad():
        for layer in model.model:
            current = layer(current)
            if layer.__class__.__name__ == "Linear":
                weights.append({
                    "layer": linear_index,
                    "weight": _as_float_matrix(layer.weight.detach().cpu().numpy()),
                    "bias": layer.bias.detach().cpu().numpy().round(6).tolist(),
                })
                activations.append(current.detach().cpu().numpy())
                linear_index += 1
    prediction = model.target_scaler.inverse(current.detach().cpu().numpy()).reshape(-1).tolist()[0]
    return {
        "model": "mlp",
        "seed": seed,
        "feature_vector": [float(v) for v in x.tolist()],
        "scaled_input": _as_float_matrix(scaled)[0],
        "layers": [
            {"name": "input", "units": len(features), "activation": _as_float_matrix(activations[0])[0]},
            *[
                {"name": f"hidden_{index}", "units": len(values[0]), "activation": _as_float_matrix(values)[0]}
                for index, values in enumerate(activations[1:-1], start=1)
            ],
            {"name": "output", "units": 1, "activation": _as_float_matrix(activations[-1])[0]},
        ],
        "weights": weights,
        "prediction": float(prediction),
        "target": "demand_units",
    }


__all__ = ["build_demo_trace"]
