"""Naive demand forecasting baselines."""


class SeasonalMean:
    def fit(self, values):
        self.value = sum(values) / max(1, len(values))
        return self

    def predict(self, horizon):
        return [self.value] * horizon


class PreviousValue:
    def fit(self, values):
        self.value = values[-1] if values else 0.0
        return self

    def predict(self, horizon):
        return [self.value] * horizon
