"""Forecast and classification metrics."""


def mae(actual, predicted):
    return sum(abs(a - p) for a, p in zip(actual, predicted)) / max(1, len(actual))


def rmse(actual, predicted):
    return (sum((a - p) ** 2 for a, p in zip(actual, predicted)) / max(1, len(actual))) ** 0.5


def smape(actual, predicted):
    return sum(
        2 * abs(a - p) / max(1e-9, abs(a) + abs(p)) for a, p in zip(actual, predicted)
    ) / max(1, len(actual))
