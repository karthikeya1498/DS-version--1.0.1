"""Probability calibration, Brier score, Expected Calibration Error (ECE), and reliability curves."""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def brier_score(y_true: Sequence[int], y_prob: Sequence[float]) -> float:
    """Compute mean squared error between true binary outcomes and predicted probabilities."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_prob, dtype=float)
    return float(np.mean((y_p - y_t) ** 2))


def expected_calibration_error(
    y_true: Sequence[int],
    y_prob: Sequence[float],
    n_bins: int = 10,
) -> float:
    """
    Compute Expected Calibration Error (ECE):
    ECE = sum_{b=1}^B (|B_m| / N) * |acc(B_m) - conf(B_m)|
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.clip(np.asarray(y_prob, dtype=float), 0.0, 1.0)
    n = len(y_t)
    if n == 0:
        return 0.0

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        bin_lower, bin_upper = bins[i], bins[i + 1]
        in_bin = (y_p >= bin_lower) & (y_p < bin_upper if i < n_bins - 1 else y_p <= bin_upper)
        bin_count = np.sum(in_bin)
        if bin_count > 0:
            bin_acc = np.mean(y_t[in_bin])
            bin_conf = np.mean(y_p[in_bin])
            ece += (bin_count / n) * abs(bin_acc - bin_conf)

    return float(ece)


def reliability_curve(
    y_true: Sequence[int],
    y_prob: Sequence[float],
    n_bins: int = 10,
) -> tuple[list[float], list[float], list[int]]:
    """
    Compute empirical accuracy vs predicted confidence coordinates for a reliability diagram.
    Returns: (mean_predicted_probabilities, empirical_fraction_positives, bin_counts)
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.clip(np.asarray(y_prob, dtype=float), 0.0, 1.0)
    bins = np.linspace(0.0, 1.0, n_bins + 1)

    mean_probs: list[float] = []
    fraction_positives: list[float] = []
    counts: list[int] = []

    for i in range(n_bins):
        bin_lower, bin_upper = bins[i], bins[i + 1]
        in_bin = (y_p >= bin_lower) & (y_p < bin_upper if i < n_bins - 1 else y_p <= bin_upper)
        bin_count = int(np.sum(in_bin))
        counts.append(bin_count)
        if bin_count > 0:
            mean_probs.append(float(np.mean(y_p[in_bin])))
            fraction_positives.append(float(np.mean(y_t[in_bin])))
        else:
            mean_probs.append(float((bin_lower + bin_upper) / 2.0))
            fraction_positives.append(0.0)

    return mean_probs, fraction_positives, counts


class PlattScaler:
    """Logistic Sigmoid probability calibration (Platt scaling)."""

    def __init__(self) -> None:
        self.a: float = 1.0
        self.b: float = 0.0
        self.fitted = False

    def fit(self, uncalibrated_scores: Sequence[float], y_true: Sequence[int]) -> PlattScaler:
        from sklearn.linear_model import LogisticRegression
        X = np.asarray(uncalibrated_scores, dtype=float).reshape(-1, 1)
        y = np.asarray(y_true, dtype=int)
        lr = LogisticRegression(C=1.0, solver="lbfgs")
        lr.fit(X, y)
        self.a = float(lr.coef_[0][0])
        self.b = float(lr.intercept_[0])
        self.fitted = True
        return self

    def predict_proba(self, uncalibrated_scores: Sequence[float]) -> list[float]:
        X = np.asarray(uncalibrated_scores, dtype=float)
        logits = self.a * X + self.b
        probs = 1.0 / (1.0 + np.exp(-np.clip(logits, -15.0, 15.0)))
        return [float(p) for p in probs]
