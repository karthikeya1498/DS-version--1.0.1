"""Time-window constraints and arrival lateness calculation."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta

from src.simulation.models import Order


def calculate_schedule_lateness(
    orders_sequence: Sequence[Order],
    start_time: datetime,
    segment_travel_minutes: Sequence[float],
) -> tuple[float, list[datetime], list[float]]:
    """
    Simulate arrival times along an ordered sequence of order delivery stops.
    Returns: (total_lateness_minutes, arrival_times, per_stop_lateness)
    """
    current_time = start_time
    arrival_times: list[datetime] = []
    lateness_list: list[float] = []
    total_late = 0.0

    for i, order in enumerate(orders_sequence):
        travel_min = segment_travel_minutes[i] if i < len(segment_travel_minutes) else 5.0
        current_time = current_time + timedelta(minutes=travel_min)
        arrival_times.append(current_time)

        # Measure lateness beyond time window end
        if current_time > order.time_window.end:
            late_min = (current_time - order.time_window.end).total_seconds() / 60.0
        else:
            late_min = 0.0

        lateness_list.append(late_min)
        total_late += late_min

    return total_late, arrival_times, lateness_list
