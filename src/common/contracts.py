"""Stable cross-layer contracts used by API and services."""
from dataclasses import dataclass, field
from datetime import datetime
@dataclass(frozen=True)
class ForecastResult:
    timestamps: tuple[datetime, ...]
    values: tuple[float, ...]
    lower: tuple[float, ...] = ()
    upper: tuple[float, ...] = ()
    model: str = 'baseline'
@dataclass(frozen=True)
class RoutePlan:
    vehicle_id: str
    order_ids: tuple[str, ...]
    node_path: tuple[str, ...]
    distance_km: float
    lateness_minutes: float = 0.0
    feasible: bool = True
    violations: tuple[str, ...] = ()
@dataclass(frozen=True)
class OptimizationResult:
    routes: tuple[RoutePlan, ...]
    total_cost: float
    served_orders: int
    unserved_orders: int
    runtime_ms: float
    strategy: str
    diagnostics: dict[str, float] = field(default_factory=dict)
