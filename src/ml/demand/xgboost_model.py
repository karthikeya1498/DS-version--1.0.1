"""Optional-model-compatible tabular demand forecaster with a dependency-free fallback."""
class DemandForecaster:
    def fit(self, features, target):
        self.mean = sum(target) / max(1, len(target)); self.feature_count = len(features[0]) if features else 0; return self
    def predict(self, features): return [self.mean] * len(features)
