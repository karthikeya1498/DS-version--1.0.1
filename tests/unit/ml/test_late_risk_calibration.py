"""Unit tests for LateRiskClassifier, Platt Scaling, Brier Score, and Expected Calibration Error (ECE)."""
import numpy as np
import pytest

from src.ml.evaluation.calibration import PlattScaler, brier_score, expected_calibration_error, reliability_curve
from src.ml.late_risk.classifier import LateRiskClassifier
from src.ml.late_risk.train import train_late_risk_model


def test_late_risk_classifier_and_probabilities():
    rng = np.random.default_rng(42)
    X = []
    y = []
    for _ in range(120):
        slack = float(rng.uniform(-15.0, 30.0))
        traffic = float(rng.uniform(1.0, 2.5))
        # High traffic + negative slack -> almost certainly late
        late_prob = 1.0 / (1.0 + np.exp(slack / 5.0 - traffic))
        label = 1 if rng.uniform() < late_prob else 0
        X.append([slack, 20.0, 20.0 + slack, 10.0, traffic, 1.0])
        y.append(label)

    clf = LateRiskClassifier(n_estimators=40, max_depth=2)
    clf.fit(X, y)

    probas = clf.predict_proba(X[:10])
    assert len(probas) == 10
    assert all(0.0 <= p <= 1.0 for p in probas)

    preds = clf.predict(X[:10], threshold=0.5)
    assert len(preds) == 10
    assert all(p in {0, 1} for p in preds)


def test_brier_score_and_ece():
    y_true = [0, 0, 1, 1, 0, 1, 1, 0, 0, 1]
    # Well-calibrated probabilities
    y_prob = [0.1, 0.2, 0.8, 0.9, 0.15, 0.85, 0.75, 0.1, 0.05, 0.95]

    bs = brier_score(y_true, y_prob)
    assert 0.0 <= bs <= 0.1  # Low Brier error

    ece = expected_calibration_error(y_true, y_prob, n_bins=5)
    assert 0.0 <= ece <= 0.2

    mean_p, frac_pos, counts = reliability_curve(y_true, y_prob, n_bins=5)
    assert len(mean_p) == 5
    assert len(frac_pos) == 5
    assert sum(counts) == len(y_true)


def test_platt_scaler():
    # Raw uncalibrated decision scores
    scores = [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
    y_true = [0, 0, 0, 0, 1, 1, 1]

    scaler = PlattScaler()
    scaler.fit(scores, y_true)
    calibrated = scaler.predict_proba(scores)

    assert len(calibrated) == len(scores)
    # Monotonicity check
    assert all(x <= y for x, y in zip(calibrated[:-1], calibrated[1:]))
