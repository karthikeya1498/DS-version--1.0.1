"""Forecast and classification metrics."""
from __future__ import annotations

from typing import Sequence

import numpy as np


def mae(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """Mean Absolute Error."""
    a = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    return float(np.mean(np.abs(a - p))) if len(a) else 0.0


def rmse(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """Root Mean Squared Error."""
    a = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    return float(np.sqrt(np.mean((a - p) ** 2))) if len(a) else 0.0


def mape(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """Mean Absolute Percentage Error."""
    a = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    denom = np.maximum(1e-6, np.abs(a))
    return float(np.mean(np.abs((a - p) / denom))) * 100.0 if len(a) else 0.0


def smape(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """Symmetric Mean Absolute Percentage Error."""
    a = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    denom = np.maximum(1e-6, np.abs(a) + np.abs(p))
    return float(np.mean(2.0 * np.abs(a - p) / denom)) * 100.0 if len(a) else 0.0


def r2(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """Coefficient of determination R^2."""
    a = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    ss_tot = np.sum((a - np.mean(a)) ** 2)
    ss_res = np.sum((a - p) ** 2)
    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    return float(1.0 - (ss_res / ss_tot))
