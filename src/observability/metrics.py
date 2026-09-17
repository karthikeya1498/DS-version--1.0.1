"""Process-local metrics primitives for Phase 8 operational intelligence.

Author: Karthikeya
"""
from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class RouteMetric:
    requests: int = 0
    errors: int = 0
    latency_ms_total: float = 0.0

    @property
    def average_latency_ms(self) -> float:
        return self.latency_ms_total / self.requests if self.requests else 0.0


@dataclass
class MetricsRegistry:
    _routes: dict[str, RouteMetric] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock, repr=False)

    def observe(self, route: str, latency_ms: float, error: bool = False) -> None:
        if latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")
        with self._lock:
            metric = self._routes.setdefault(route, RouteMetric())
            metric.requests += 1
            metric.errors += int(error)
            metric.latency_ms_total += latency_ms

    def snapshot(self) -> dict[str, dict[str, float | int]]:
        with self._lock:
            return {
                route: {
                    "requests": metric.requests,
                    "errors": metric.errors,
                    "latency_ms_total": round(metric.latency_ms_total, 3),
                    "average_latency_ms": round(metric.average_latency_ms, 3),
                }
                for route, metric in sorted(self._routes.items())
            }


metrics_registry = MetricsRegistry()

__all__ = ["MetricsRegistry", "RouteMetric", "metrics_registry"]
