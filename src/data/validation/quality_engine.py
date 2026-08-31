"""Composable data-quality checks for Phase 1 operational records."""

from __future__ import annotations

from collections import Counter
from datetime import datetime


def validate_operational_records(records: list[dict]) -> dict:
    errors: list[str] = []
    ids = [record.get("order_id") for record in records if record.get("order_id") is not None]
    errors.extend(f"duplicate order_id: {key}" for key, count in Counter(ids).items() if count > 1)
    for index, record in enumerate(records):
        prefix = f"row {index}"
        if record.get("distance_km") is not None and record["distance_km"] < 0:
            errors.append(f"{prefix}: distance_km must be non-negative")
        if record.get("capacity_units") is not None and record["capacity_units"] < 0:
            errors.append(f"{prefix}: capacity_units must be non-negative")
        if record.get("actual_eta") is not None and record["actual_eta"] < 0:
            errors.append(f"{prefix}: actual_eta must be non-negative")
        if record.get("latitude") is not None and not -90 <= record["latitude"] <= 90:
            errors.append(f"{prefix}: latitude out of range")
        if record.get("longitude") is not None and not -180 <= record["longitude"] <= 180:
            errors.append(f"{prefix}: longitude out of range")
        created, delivered = record.get("created_at"), record.get("delivered_at")
        if (
            isinstance(created, datetime)
            and isinstance(delivered, datetime)
            and delivered < created
        ):
            errors.append(f"{prefix}: delivered_at precedes created_at")
    return {"rows": len(records), "valid": not errors, "errors": errors}
