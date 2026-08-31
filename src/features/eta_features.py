"""Feature engineering for trip travel-time (ETA) estimation."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

ROAD_CLASS_WEIGHTS = {
    "motorway": 0.6,
    "trunk": 0.75,
    "primary": 1.0,
    "secondary": 1.25,
    "tertiary": 1.5,
    "residential": 1.8,
    "service": 2.0,
}


def build_eta_feature_row(
    distance_km: float,
    free_flow_speed_kmh: float = 40.0,
    traffic_multiplier: float = 1.0,
    congestion_level: float = 0.0,
    road_class: str = "primary",
    hour: int = 12,
    day_of_week: int = 2,
    weather_multiplier: float = 1.0,
    vehicle_speed_factor: float = 1.0,
    stops_count: int = 1,
) -> dict[str, float]:
    """
    Build a single standardized feature record for ETA modeling.
    """
    speed_limit = max(5.0, free_flow_speed_kmh * vehicle_speed_factor)
    free_flow_time_min = (distance_km / speed_limit) * 60.0
    effective_traffic = max(0.5, traffic_multiplier * weather_multiplier * (1.0 + congestion_level))
    estimated_travel_time_min = free_flow_time_min * effective_traffic

    rc_factor = ROAD_CLASS_WEIGHTS.get(road_class.lower(), 1.0)
    hour_rad = 2 * np.pi * (hour % 24) / 24.0
    dow_rad = 2 * np.pi * (day_of_week % 7) / 7.0

    return {
        "distance_km": float(distance_km),
        "free_flow_time_min": float(free_flow_time_min),
        "traffic_multiplier": float(traffic_multiplier),
        "congestion_level": float(congestion_level),
        "weather_multiplier": float(weather_multiplier),
        "road_class_factor": float(rc_factor),
        "effective_travel_time_est": float(estimated_travel_time_min),
        "stops_count": float(stops_count),
        "hour_sin": float(np.sin(hour_rad)),
        "hour_cos": float(np.cos(hour_rad)),
        "day_sin": float(np.sin(dow_rad)),
        "day_cos": float(np.cos(dow_rad)),
        "is_weekend": float(1.0 if day_of_week >= 5 else 0.0),
    }


def build_eta_features_df(records: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """Build a DataFrame of tabular ETA features from input journey records."""
    rows = []
    for r in records:
        row = build_eta_feature_row(
            distance_km=float(r.get("distance_km", 1.0)),
            free_flow_speed_kmh=float(r.get("free_flow_speed_kmh", 40.0)),
            traffic_multiplier=float(r.get("traffic_multiplier", 1.0)),
            congestion_level=float(r.get("congestion_level", 0.0)),
            road_class=str(r.get("road_class", "primary")),
            hour=int(r.get("hour", 12)),
            day_of_week=int(r.get("day_of_week", 2)),
            weather_multiplier=float(r.get("weather_multiplier", 1.0)),
            vehicle_speed_factor=float(r.get("vehicle_speed_factor", 1.0)),
            stops_count=int(r.get("stops_count", 1)),
        )
        if "actual_travel_time_min" in r:
            row["target"] = float(r["actual_travel_time_min"])
        elif "target" in r:
            row["target"] = float(r["target"])
        rows.append(row)
    return pd.DataFrame(rows)
