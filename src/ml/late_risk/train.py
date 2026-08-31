"""Training pipeline for late-delivery risk classifier."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd

from src.features.feature_pipeline import chronological_split
from src.ml.evaluation.calibration import brier_score, expected_calibration_error
from src.ml.late_risk.classifier import LateRiskClassifier


def build_late_risk_dataset(journey_records: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """Build tabular records for late risk classification."""
    rows = []
    for r in journey_records:
        eta_min = float(r.get("predicted_eta_minutes", 20.0))
        deadline_min = float(r.get("deadline_minutes", 30.0))
        slack_min = deadline_min - eta_min
        dist_km = float(r.get("distance_km", 5.0))
        traffic_mult = float(r.get("traffic_multiplier", 1.0))
        priority = int(r.get("priority", 1))

        # Ground truth late label
        is_late = int(r.get("is_late", 1 if slack_min < 0 else 0))

        rows.append(
            {
                "slack_minutes": float(slack_min),
                "predicted_eta_minutes": float(eta_min),
                "deadline_minutes": float(deadline_min),
                "distance_km": float(dist_km),
                "traffic_multiplier": float(traffic_mult),
                "priority": float(priority),
                "target_late": is_late,
            }
        )
    return pd.DataFrame(rows)


def train_late_risk_model(journey_records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    df = build_late_risk_dataset(journey_records)
    feat_cols = [c for c in df.columns if c != "target_late"]

    train_df, val_df, test_df = chronological_split(
        df, train_fraction=0.70, validation_fraction=0.15
    )

    X_train, y_train = train_df[feat_cols].values, train_df["target_late"].values
    X_test, y_test = test_df[feat_cols].values, test_df["target_late"].values

    clf = LateRiskClassifier(n_estimators=70, max_depth=3)
    clf.fit(X_train, y_train, feature_names=feat_cols)

    test_probas = clf.predict_proba(X_test)
    test_preds = clf.predict(X_test)

    brier = brier_score(y_test, test_probas)
    ece = expected_calibration_error(y_test, test_probas, n_bins=10)
    accuracy = float(np.mean(np.asarray(test_preds) == y_test))

    return {
        "model": clf,
        "metrics": {
            "accuracy": accuracy,
            "brier_score": brier,
            "expected_calibration_error": ece,
        },
        "feature_cols": feat_cols,
        "test_count": len(test_df),
    }
