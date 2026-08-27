"""Typed observation contract for sequential multi-agent logistics control."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LogisticsState:
    time_step: int
    pending_demand: np.ndarray
    vehicle_positions: np.ndarray
    vehicle_capacity: np.ndarray
    traffic: np.ndarray

    def vector(self) -> np.ndarray:
        return np.concatenate((self.pending_demand, self.vehicle_positions, self.vehicle_capacity, self.traffic)).astype(np.float32)

    @property
    def observation_dim(self) -> int:
        return int(self.vector().size)
