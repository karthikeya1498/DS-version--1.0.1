"""Neural ETA forecasters built on the shared Phase 2 architectures.

Author: Karthikeya
ETA and demand use the same supervised numerical contract; keeping these
aliases under `ml.eta` makes model ownership explicit without duplicating the
training implementation.
"""
from __future__ import annotations

from src.ml.demand.neural_models import MLPDemandForecaster, TemporalDemandForecaster


class MLPETAForecaster(MLPDemandForecaster):
    """MLP ETA regressor with the shared normalization and persistence logic."""

    def metadata(self) -> dict[str, object]:
        return {**super().metadata(), "target": "eta_minutes", "model": "mlp_eta"}


class TemporalETAForecaster(TemporalDemandForecaster):
    """LSTM/GRU ETA regressor for travel-time feature sequences."""

    def metadata(self) -> dict[str, object]:
        return {**super().metadata(), "target": "eta_minutes", "model": f"{self.cell}_eta"}
