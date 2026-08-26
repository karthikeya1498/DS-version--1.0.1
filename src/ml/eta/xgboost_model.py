"""Optional-model-compatible ETA forecaster with a dependency-free fallback."""


class EtaForecaster:
    def fit(self, features, target):
        self.mean = sum(target) / max(1, len(target))
        return self

    def predict(self, features):
        return [self.mean] * len(features)
