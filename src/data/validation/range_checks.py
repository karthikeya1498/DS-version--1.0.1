"""Range validation for generated and imported records."""


def non_negative(value, name):
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def in_range(value, low, high, name):
    if not low <= value <= high:
        raise ValueError(f"{name} outside [{low}, {high}]")
    return value
