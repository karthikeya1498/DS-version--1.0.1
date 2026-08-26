"""ETA baseline based on historical mean travel time."""


class MeanEta:
    def fit(self, values):
        self.value = sum(values) / max(1, len(values))
        return self

    def predict(self, count):
        return [self.value] * count
