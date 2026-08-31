"""Neural MLP model for ETA trip duration forecasting."""

from __future__ import annotations

from typing import Any

from src.ml.demand.mlp_model import MLPForecaster


class EtaMLPForecaster(MLPForecaster):
    """Neural ETA regressor ensuring non-negative travel times."""

    def predict(self, X: Any) -> list[float]:
        raw_preds = super().predict(X)
        return [float(max(0.5, p)) for p in raw_preds]
