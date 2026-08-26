"""Core domain models for the reproducible logistics simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

UTC = UTC


class OrderStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    UNAVAILABLE = "unavailable"


class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFF_DUTY = "off_duty"


class EventType(str, Enum):
    ORDER_CREATED = "order_created"
    VEHICLE_DISPATCHED = "vehicle_dispatched"
    ORDER_DELIVERED = "order_delivered"
    TRAFFIC_UPDATED = "traffic_updated"
    VEHICLE_RETURNED = "vehicle_returned"


@dataclass(frozen=True, slots=True)
class Location:
    """A node in the abstract road network."""

    node_id: str
    zone_id: str
    latitude: float = 0.0
    longitude: float = 0.0

    def __post_init__(self) -> None:
        if not self.node_id.strip() or not self.zone_id.strip():
            raise ValueError("node_id and zone_id must be non-empty")
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")


@dataclass(frozen=True, slots=True)
class TimeWindow:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("time-window datetimes must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("time-window end must be after start")

    def contains(self, timestamp: datetime) -> bool:
        return self.start <= timestamp <= self.end


@dataclass(slots=True)
class Order:
    order_id: str
    origin: Location
    destination: Location
    demand_units: int
    created_at: datetime
    time_window: TimeWindow
    priority: int = 1
    status: OrderStatus = OrderStatus.PENDING
    assigned_vehicle_id: str | None = None
    delivered_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.order_id.strip():
            raise ValueError("order_id must be non-empty")
        if self.demand_units <= 0:
            raise ValueError("demand_units must be positive")
        if self.priority < 1:
            raise ValueError("priority must be at least 1")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

    @property
    def is_late(self) -> bool:
        return self.delivered_at is not None and self.delivered_at > self.time_window.end


@dataclass(slots=True)
class Vehicle:
    vehicle_id: str
    home_base: Location
    capacity_units: int
    available_from: datetime
    available_until: datetime
    status: VehicleStatus = VehicleStatus.AVAILABLE
    current_location: Location | None = None
    load_units: int = 0
    completed_orders: int = 0

    def __post_init__(self) -> None:
        if not self.vehicle_id.strip():
            raise ValueError("vehicle_id must be non-empty")
        if self.capacity_units <= 0:
            raise ValueError("capacity_units must be positive")
        if self.available_from.tzinfo is None or self.available_until.tzinfo is None:
            raise ValueError("vehicle availability datetimes must be timezone-aware")
        if self.available_until <= self.available_from:
            raise ValueError("available_until must be after available_from")
        if self.current_location is None:
            self.current_location = self.home_base

    def can_accept(self, demand_units: int, timestamp: datetime) -> bool:
        return (
            demand_units > 0
            and self.status == VehicleStatus.AVAILABLE
            and self.load_units + demand_units <= self.capacity_units
            and self.available_from <= timestamp <= self.available_until
        )


@dataclass(frozen=True, slots=True)
class TrafficState:
    timestamp: datetime
    zone_multipliers: dict[str, float]

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("traffic timestamp must be timezone-aware")
        if any(value <= 0 for value in self.zone_multipliers.values()):
            raise ValueError("traffic multipliers must be positive")

    def multiplier_for(self, zone_id: str) -> float:
        return self.zone_multipliers.get(zone_id, 1.0)


@dataclass(order=True, frozen=True, slots=True)
class SimulationEvent:
    timestamp: datetime
    sequence: int
    event_type: EventType = field(compare=False)
    entity_id: str = field(compare=False)
    payload: dict[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("event timestamp must be timezone-aware")


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    seed: int = 42
    start_time: datetime = datetime(2026, 1, 1, tzinfo=UTC)
    duration: timedelta = timedelta(hours=8)
    zones: int = 5
    vehicles: int = 10
    orders_per_hour: int = 20
    max_order_demand: int = 5
    traffic_update_minutes: int = 15

    def __post_init__(self) -> None:
        if self.start_time.tzinfo is None:
            raise ValueError("start_time must be timezone-aware")
        if self.duration.total_seconds() <= 0:
            raise ValueError("duration must be positive")
        if min(self.zones, self.vehicles, self.orders_per_hour, self.max_order_demand) <= 0:
            raise ValueError("simulation sizes must be positive")
        if self.traffic_update_minutes <= 0:
            raise ValueError("traffic_update_minutes must be positive")


@dataclass(frozen=True, slots=True)
class SimulationMetrics:
    total_orders: int
    delivered_orders: int
    late_deliveries: int
    unserved_orders: int
    total_distance_km: float
    total_cost: float


@dataclass(slots=True)
class SimulationResult:
    seed: int
    start_time: datetime
    end_time: datetime
    orders: list[Order]
    vehicles: list[Vehicle]
    events: list[SimulationEvent]
    traffic_history: list[TrafficState]
    metrics: SimulationMetrics

    def to_summary(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "metrics": {
                "total_orders": self.metrics.total_orders,
                "delivered_orders": self.metrics.delivered_orders,
                "late_deliveries": self.metrics.late_deliveries,
                "unserved_orders": self.metrics.unserved_orders,
                "total_distance_km": round(self.metrics.total_distance_km, 3),
                "total_cost": round(self.metrics.total_cost, 3),
            },
        }


def utc_now() -> datetime:
    """Return an aware UTC timestamp for callers creating ad hoc entities."""
    return datetime.now(UTC)
