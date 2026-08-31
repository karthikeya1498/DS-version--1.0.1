"""Late-delivery risk probability classifier."""

from __future__ import annotations

from typing import Any

import numpy as np


class LateRiskClassifier:
    """
    Predicts probability P(delivery is late) in [0, 1]
    given travel slack time, distance, traffic congestion, and order priority.
    """

    def __init__(self, random_state: int = 42, **params: Any) -> None:
        self.random_state = random_state
        self.params = params
        self.model: Any = None
        self.feature_names: list[str] = []
        self.feature_count = 0

    def fit(
        self, features: Any, labels: Any, feature_names: list[str] | None = None
    ) -> LateRiskClassifier:
        x = np.asarray(features, dtype=float)
        y = np.asarray(labels, dtype=int)
        self.feature_count = x.shape[1] if x.ndim == 2 else 0
        self.feature_names = feature_names or [f"f_{i}" for i in range(self.feature_count)]

        try:
            from xgboost import XGBClassifier

            self.model = XGBClassifier(
                n_estimators=self.params.get("n_estimators", 80),
                max_depth=self.params.get("max_depth", 3),
                learning_rate=self.params.get("learning_rate", 0.05),
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=self.random_state,
                n_jobs=1,
            )
            self.model.fit(x, y)
        except ImportError:
            from sklearn.linear_model import LogisticRegression

            self.model = LogisticRegression(random_state=self.random_state, max_iter=200)
            self.model.fit(x, y)

        return self

    def predict_proba(self, features: Any) -> list[float]:
        """Return calibrated P(late) for each sample."""
        if self.model is None:
            raise RuntimeError("LateRiskClassifier must be fitted before predict_proba()")
        x = np.asarray(features, dtype=float)
        if x.ndim == 1:
            x = x.reshape(1, -1)
        proba = self.model.predict_proba(x)
        # Class 1 probability (P(late=1))
        return [float(p[1]) for p in proba]

    def predict(self, features: Any, threshold: float = 0.5) -> list[int]:
        """Binary classification decision based on threshold."""
        prob_late = self.predict_proba(features)
        return [1 if p >= threshold else 0 for p in prob_late]

    def metadata(self) -> dict[str, Any]:
        return {
            "model_type": "late_risk_classifier",
            "feature_count": self.feature_count,
            "feature_names": self.feature_names,
            "random_state": self.random_state,
        }
