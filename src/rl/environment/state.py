"""Typed observation contract and domain state encoder for multi-agent logistics control."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from src.simulation.models import Order, OrderStatus, Vehicle


@dataclass(frozen=True)
class LogisticsState:
    time_step: int
    pending_demand: np.ndarray
    vehicle_positions: np.ndarray
    vehicle_capacity: np.ndarray
    traffic: np.ndarray

    def vector(self) -> np.ndarray:
        return np.concatenate(
            (self.pending_demand, self.vehicle_positions, self.vehicle_capacity, self.traffic)
        ).astype(np.float32)

    @property
    def observation_dim(self) -> int:
        return int(self.vector().size)

    @classmethod
    def from_domain_entities(
        cls,
        time_step: int,
        orders: Sequence[Order],
        vehicles: Sequence[Vehicle],
        zone_ids: Sequence[str] = ("zone_0", "zone_1", "zone_2"),
        traffic_multipliers: dict[str, float] | None = None,
    ) -> LogisticsState:
        """Encode live domain orders, vehicles, and traffic into a normalized RL observation."""
        zone_to_idx = {z: i for i, z in enumerate(zone_ids)}
        pending = np.zeros(len(zone_ids), dtype=np.float32)

        for o in orders:
            if o.status in {OrderStatus.PENDING, OrderStatus.ASSIGNED}:
                idx = zone_to_idx.get(o.destination.zone_id, 0)
                pending[idx] += float(o.demand_units)

        v_pos = np.zeros(len(vehicles), dtype=np.float32)
        v_cap = np.zeros(len(vehicles), dtype=np.float32)

        for i, v in enumerate(vehicles):
            z_idx = zone_to_idx.get(v.current_location.zone_id, 0)
            v_pos[i] = float(z_idx)
            spare_cap = max(0, v.capacity_units - v.load_units)
            v_cap[i] = float(spare_cap / max(1, v.capacity_units))

        traffic_vec = np.ones(len(zone_ids), dtype=np.float32)
        if traffic_multipliers:
            for z, mult in traffic_multipliers.items():
                if z in zone_to_idx:
                    traffic_vec[zone_to_idx[z]] = float(mult)

        return cls(
            time_step=time_step,
            pending_demand=pending,
            vehicle_positions=v_pos,
            vehicle_capacity=v_cap,
            traffic=traffic_vec,
        )
