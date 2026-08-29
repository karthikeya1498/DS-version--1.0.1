"""Neural demand forecasting models for the Phase 2 model comparison.

Author: Karthikeya

The models are deliberately small and reproducible. They consume the same
numeric feature matrices and chronological sequence windows as the existing
Phase 2 pipeline, allowing XGBoost, MLP, LSTM, and GRU to be compared without
changing the downstream prediction contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np


@dataclass(frozen=True)
class Standardizer:
    mean: np.ndarray
    scale: np.ndarray

    @classmethod
    def fit(cls, values: np.ndarray) -> Standardizer:
        mean = values.mean(axis=0)
        scale = values.std(axis=0)
        return cls(mean=mean, scale=np.where(scale < 1e-8, 1.0, scale))

    def transform(self, values: np.ndarray) -> np.ndarray:
        return (values - self.mean) / self.scale

    def inverse(self, values: np.ndarray) -> np.ndarray:
        return values * self.scale + self.mean


def _torch():
    try:
        import torch
        from torch import nn
    except ImportError as exc:  # pragma: no cover - depends on optional ML extra
        raise RuntimeError("Neural models require the optional 'ml' dependencies (torch).") from exc
    return torch, nn


def _as_matrix(values: object) -> np.ndarray:
    matrix = np.asarray(values, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] == 0:
        raise ValueError("features must be a non-empty two-dimensional array")
    return matrix


def _as_target(values: object, expected_rows: int) -> np.ndarray:
    target = np.asarray(values, dtype=np.float32).reshape(-1)
    if target.shape[0] != expected_rows:
        raise ValueError("target length must match the number of feature rows")
    return target


class MLPDemandForecaster:
    """Feed-forward neural baseline for tabular demand features."""

    def __init__(
        self,
        hidden_sizes: tuple[int, ...] = (64, 32),
        learning_rate: float = 1e-3,
        epochs: int = 80,
        random_state: int = 42,
    ) -> None:
        if not hidden_sizes or any(size < 1 for size in hidden_sizes):
            raise ValueError("hidden_sizes must contain positive widths")
        if learning_rate <= 0 or epochs < 1:
            raise ValueError("learning_rate must be positive and epochs must be >= 1")
        self.hidden_sizes = hidden_sizes
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.random_state = random_state
        self.model = None
        self.feature_scaler: Standardizer | None = None
        self.target_scaler: Standardizer | None = None
        self.loss_history: list[float] = []

    def fit(self, features: object, target: object) -> MLPDemandForecaster:
        torch, nn = _torch()
        x = _as_matrix(features)
        y = _as_target(target, x.shape[0])
        torch.manual_seed(self.random_state)
        self.feature_scaler = Standardizer.fit(x)
        self.target_scaler = Standardizer.fit(y[:, None])
        layers: list[object] = []
        input_size = x.shape[1]
        for width in self.hidden_sizes:
            layers.extend([nn.Linear(input_size, width), nn.ReLU()])
            input_size = width
        layers.append(nn.Linear(input_size, 1))
        self.model = nn.Sequential(*layers)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        loss_fn = nn.MSELoss()
        x_tensor = torch.from_numpy(self.feature_scaler.transform(x))
        y_tensor = torch.from_numpy(self.target_scaler.transform(y[:, None]))
        self.model.train()
        self.loss_history = []
        for _ in range(self.epochs):
            optimizer.zero_grad()
            loss = loss_fn(self.model(x_tensor), y_tensor)
            loss.backward()
            optimizer.step()
            self.loss_history.append(float(loss.detach().cpu()))
        return self

    def predict(self, features: object) -> list[float]:
        torch, _ = _torch()
        if self.model is None or self.feature_scaler is None or self.target_scaler is None:
            raise RuntimeError("fit must be called before predict")
        x = _as_matrix(features)
        self.model.eval()
        with torch.no_grad():
            values = self.model(torch.from_numpy(self.feature_scaler.transform(x))).cpu().numpy()
        return self.target_scaler.inverse(values).reshape(-1).astype(float).tolist()

    def metadata(self) -> dict[str, object]:
        return {"model": "mlp", "hidden_sizes": self.hidden_sizes, "learning_rate": self.learning_rate, "epochs": self.epochs, "random_state": self.random_state, "final_loss": self.loss_history[-1] if self.loss_history else None}

    def save(self, path: str | Path) -> None:
        torch, _ = _torch()
        if self.model is None or self.feature_scaler is None or self.target_scaler is None:
            raise RuntimeError("fit must be called before save")
        torch.save({"metadata": self.metadata(), "state_dict": self.model.state_dict(), "feature_mean": self.feature_scaler.mean, "feature_scale": self.feature_scaler.scale, "target_mean": self.target_scaler.mean, "target_scale": self.target_scaler.scale}, Path(path))


class TemporalDemandForecaster:
    """LSTM or GRU forecaster for leakage-safe sequence windows."""

    def __init__(
        self,
        cell: Literal["lstm", "gru"] = "lstm",
        hidden_size: int = 32,
        learning_rate: float = 1e-3,
        epochs: int = 80,
        random_state: int = 42,
    ) -> None:
        if cell not in {"lstm", "gru"} or hidden_size < 1 or learning_rate <= 0 or epochs < 1:
            raise ValueError("cell must be lstm/gru, hidden_size positive, and training settings valid")
        self.cell = cell
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.random_state = random_state
        self.model = None
        self.feature_scaler: Standardizer | None = None
        self.target_scaler: Standardizer | None = None
        self.loss_history: list[float] = []

    def fit(self, sequences: object, target: object) -> TemporalDemandForecaster:
        torch, nn = _torch()
        x = np.asarray(sequences, dtype=np.float32)
        if x.ndim != 3 or x.shape[0] == 0:
            raise ValueError("sequences must be a non-empty three-dimensional array")
        y = _as_target(target, x.shape[0])
        torch.manual_seed(self.random_state)
        flattened = x.reshape(-1, x.shape[-1])
        self.feature_scaler = Standardizer.fit(flattened)
        self.target_scaler = Standardizer.fit(y[:, None])
        cell_cls = nn.LSTM if self.cell == "lstm" else nn.GRU
        self.model = nn.Sequential(cell_cls(x.shape[-1], self.hidden_size, batch_first=True), nn.Linear(self.hidden_size, 1))
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        loss_fn = nn.MSELoss()
        x_scaled = self.feature_scaler.transform(flattened).reshape(x.shape)
        x_tensor = torch.from_numpy(x_scaled)
        y_tensor = torch.from_numpy(self.target_scaler.transform(y[:, None]))
        self.loss_history = []
        self.model.train()
        for _ in range(self.epochs):
            optimizer.zero_grad()
            recurrent, _ = self.model[0](x_tensor)
            loss = loss_fn(self.model[1](recurrent[:, -1, :]), y_tensor)
            loss.backward()
            optimizer.step()
            self.loss_history.append(float(loss.detach().cpu()))
        return self

    def predict(self, sequences: object) -> list[float]:
        torch, _ = _torch()
        if self.model is None or self.feature_scaler is None or self.target_scaler is None:
            raise RuntimeError("fit must be called before predict")
        x = np.asarray(sequences, dtype=np.float32)
        if x.ndim != 3 or x.shape[0] == 0 or x.shape[-1] != self.feature_scaler.mean.shape[0]:
            raise ValueError("sequences must match the fitted three-dimensional feature shape")
        x_scaled = self.feature_scaler.transform(x.reshape(-1, x.shape[-1])).reshape(x.shape)
        self.model.eval()
        with torch.no_grad():
            recurrent, _ = self.model[0](torch.from_numpy(x_scaled))
            values = self.model[1](recurrent[:, -1, :]).cpu().numpy()
        return self.target_scaler.inverse(values).reshape(-1).astype(float).tolist()

    def metadata(self) -> dict[str, object]:
        return {"model": self.cell, "hidden_size": self.hidden_size, "learning_rate": self.learning_rate, "epochs": self.epochs, "random_state": self.random_state, "final_loss": self.loss_history[-1] if self.loss_history else None}
