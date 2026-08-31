"""XGBoost trip travel time (ETA) forecaster."""

from __future__ import annotations

from typing import Any

import numpy as np


class EtaForecaster:
    """Trip travel time (ETA in minutes) estimator using XGBoost."""

    def __init__(self, random_state: int = 42, **params: Any) -> None:
        self.random_state = random_state
        self.params = params
        self.model: Any = None
        self.feature_names: list[str] = []
        self.feature_count = 0

    def fit(
        self, features: Any, target: Any, feature_names: list[str] | None = None
    ) -> EtaForecaster:
        x = np.asarray(features, dtype=float)
        y = np.asarray(target, dtype=float)
        self.feature_count = x.shape[1] if x.ndim == 2 else 0
        self.feature_names = feature_names or [f"f_{i}" for i in range(self.feature_count)]

        try:
            from xgboost import XGBRegressor
        except ImportError as err:
            raise ImportError("xgboost is required for EtaForecaster") from err

        n_estimators = self.params.get("n_estimators", 120)
        max_depth = self.params.get("max_depth", 4)
        learning_rate = self.params.get("learning_rate", 0.05)

        self.model = XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="reg:squarederror",
            random_state=self.random_state,
            n_jobs=1,
        )
        self.model.fit(x, y)
        return self

    def predict(self, features: Any) -> list[float]:
        if self.model is None:
            raise RuntimeError("EtaForecaster must be fitted before predict()")
        x = np.asarray(features, dtype=float)
        if x.ndim == 1:
            x = x.reshape(1, -1)
        preds = self.model.predict(x)
        # Travel time must always be positive
        return [float(max(0.5, p)) for p in preds]

    def metadata(self) -> dict[str, Any]:
        return {
            "model_type": "xgboost_eta_forecaster",
            "backend": "xgboost",
            "feature_count": self.feature_count,
            "feature_names": self.feature_names,
            "params": self.params,
        }
