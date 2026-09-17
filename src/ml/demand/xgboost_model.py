"""Demand forecasting model with native XGBoost and deterministic fallback."""
from __future__ import annotations

import numpy as np


class DemandForecaster:
    def __init__(self, random_state: int = 42, **params): self.random_state, self.params, self.model = random_state, params, None
    def fit(self, features, target):
        x = np.asarray(features, dtype=float); y = np.asarray(target, dtype=float); self.feature_count = x.shape[1] if x.ndim == 2 else 0; self.mean = float(y.mean()) if len(y) else 0.0
        try:
            from xgboost import XGBRegressor
            self.model = XGBRegressor(n_estimators=self.params.get('n_estimators', 200), max_depth=self.params.get('max_depth', 6), learning_rate=self.params.get('learning_rate', .05), subsample=.9, colsample_bytree=.9, objective='reg:squarederror', random_state=self.random_state, n_jobs=1)
            self.model.fit(x, y)
        except ImportError: self.model = None
        return self
    def predict(self, features):
        x = np.asarray(features, dtype=float)
        return self.model.predict(x).tolist() if self.model is not None else [self.mean] * len(x)
    def metadata(self) -> dict: return {'model': 'xgboost' if self.model is not None else 'mean_fallback', 'feature_count': self.feature_count, 'random_state': self.random_state, 'params': self.params}
