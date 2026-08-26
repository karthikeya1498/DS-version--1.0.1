"""Traffic-state generation for reproducible simulation scenarios."""

from __future__ import annotations

import random
from datetime import timedelta

from src.simulation.models import SimulationConfig, TrafficState


class TrafficEngine:
    def __init__(self, config: SimulationConfig, rng: random.Random) -> None:
        self.config = config
        self.rng = rng

    def generate_history(self) -> list[TrafficState]:
        states: list[TrafficState] = []
        step = timedelta(minutes=self.config.traffic_update_minutes)
        timestamp = self.config.start_time
        end = self.config.start_time + self.config.duration
        while timestamp <= end:
            peak = 1.25 if timestamp.hour in {8, 9, 17, 18} else 1.0
            multipliers = {
                f"zone-{i}": round(max(0.75, peak + self.rng.uniform(-0.15, 0.15)), 3)
                for i in range(self.config.zones)
            }
            states.append(TrafficState(timestamp, multipliers))
            timestamp += step
        return states
