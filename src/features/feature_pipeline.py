"""Small dependency-light feature pipeline for logistics records."""


def build_features(records):
    result = []
    for row in records:
        result.append(
            {
                **row,
                "demand_squared": float(row.get("demand_units", 0)) ** 2,
                "priority_weight": float(row.get("priority", 1)),
            }
        )
    return result
