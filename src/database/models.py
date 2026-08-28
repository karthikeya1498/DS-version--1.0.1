"""Database model exports for OPTIMA-X.

Author: Karthikeya
The historical ``ExperimentRecord`` dataclass remains available for lightweight
in-memory tests; PostgreSQL-backed services should use the SQLAlchemy entities
exported from ``orm_models``.
"""

from dataclasses import dataclass
from datetime import datetime

from .orm_models import (
    Base,
    BenchmarkRun,
    DatasetVersion,
    DecisionCandidate,
    DecisionRecord,
    DecisionTrace,
    DemandPrediction,
    ETAPrediction,
    EvidenceItem,
    Location,
    LogisticsOrder,
    ModelVersion,
    OptimizationRun,
    RLEpisode,
    RLExperiment,
    RLStep,
    RoadEdge,
    RoadNode,
    RouteAssignment,
    RouteStop,
    Scenario,
    ScenarioModification,
    SystemEvent,
    Tenant,
    ToolCall,
    TrafficHistory,
    Vehicle,
    VehicleShift,
    WeatherObservation,
)


@dataclass(frozen=True)
class ExperimentRecord:
    """Backward-compatible in-memory experiment result contract."""

    experiment_id: str
    strategy: str
    seed: int
    created_at: datetime
    metrics: dict[str, float]


__all__ = [
    "Base",
    "BenchmarkRun",
    "DatasetVersion",
    "DecisionCandidate",
    "DecisionRecord",
    "DecisionTrace",
    "DemandPrediction",
    "ETAPrediction",
    "EvidenceItem",
    "ExperimentRecord",
    "Location",
    "LogisticsOrder",
    "ModelVersion",
    "OptimizationRun",
    "RLEpisode",
    "RLExperiment",
    "RLStep",
    "RoadEdge",
    "RoadNode",
    "RouteAssignment",
    "RouteStop",
    "Scenario",
    "ScenarioModification",
    "SystemEvent",
    "Tenant",
    "ToolCall",
    "TrafficHistory",
    "Vehicle",
    "VehicleShift",
    "WeatherObservation",
]
