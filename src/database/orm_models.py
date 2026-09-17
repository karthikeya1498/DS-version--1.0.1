"""SQLAlchemy 2.x mappings for the canonical OPTIMA-X ``optima`` schema.

Author: Karthikeya
The models mirror ``src/database/optima_schema.sql``.  JSONB is intentionally
used only for variable-shaped payloads; identifiers, timestamps, statuses, and
performance-critical predicates remain typed columns.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, ClassVar
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import CHAR, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

SCHEMA = "optima"
UUIDType = PGUUID(as_uuid=True)


class Base(DeclarativeBase):
    """Declarative metadata root for OPTIMA-X PostgreSQL models."""


class OptimaEntity:
    __table_args__: ClassVar = {"schema": SCHEMA}


class Tenant(OptimaEntity, Base):
    __tablename__ = "tenant"
    tenant_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scenarios: Mapped[list[Scenario]] = relationship(back_populates="tenant")
    vehicles: Mapped[list[Vehicle]] = relationship(back_populates="tenant")
    orders: Mapped[list[LogisticsOrder]] = relationship(back_populates="tenant")


class DatasetVersion(OptimaEntity, Base):
    __tablename__ = "dataset_version"
    dataset_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(Text, nullable=False)
    source_uri: Mapped[str | None] = mapped_column(Text)
    content_sha256: Mapped[str | None] = mapped_column(CHAR(64))
    schema_version: Mapped[str] = mapped_column(Text, nullable=False)
    row_count: Mapped[int | None] = mapped_column(BigInteger)
    manifest: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", "version", name="uq_dataset_tenant_name_version"),
        {"schema": SCHEMA},
    )


class Scenario(OptimaEntity, Base):
    __tablename__ = "scenario"
    scenario_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE"), nullable=False
    )
    dataset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.dataset_version.dataset_id", ondelete="SET NULL")
    )
    scenario_key: Mapped[str] = mapped_column(Text, nullable=False)
    seed: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="created")
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tenant: Mapped[Tenant] = relationship(back_populates="scenarios")
    orders: Mapped[list[LogisticsOrder]] = relationship(back_populates="scenario")
    optimization_runs: Mapped[list[OptimizationRun]] = relationship(back_populates="scenario")
    __table_args__ = (
        UniqueConstraint("tenant_id", "scenario_key", name="uq_scenario_tenant_key"),
        {"schema": SCHEMA},
    )


class Location(OptimaEntity, Base):
    __tablename__ = "location"
    location_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE"), nullable=False
    )
    external_key: Mapped[str | None] = mapped_column(Text)
    zone_id: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )


class RoadNode(OptimaEntity, Base):
    __tablename__ = "road_node"
    node_id: Mapped[str] = mapped_column(Text, primary_key=True)
    dataset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.dataset_version.dataset_id", ondelete="SET NULL")
    )
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    outgoing_edges: Mapped[list[RoadEdge]] = relationship(
        foreign_keys="RoadEdge.source_node_id", back_populates="source_node"
    )
    incoming_edges: Mapped[list[RoadEdge]] = relationship(
        foreign_keys="RoadEdge.target_node_id", back_populates="target_node"
    )


class RoadEdge(OptimaEntity, Base):
    __tablename__ = "road_edge"
    edge_id: Mapped[str] = mapped_column(Text, primary_key=True)
    dataset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.dataset_version.dataset_id", ondelete="SET NULL")
    )
    source_node_id: Mapped[str] = mapped_column(
        ForeignKey(f"{SCHEMA}.road_node.node_id"), nullable=False
    )
    target_node_id: Mapped[str] = mapped_column(
        ForeignKey(f"{SCHEMA}.road_node.node_id"), nullable=False
    )
    distance_km: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    base_travel_time_sec: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    base_cost: Mapped[Decimal] = mapped_column(Numeric(14, 5), nullable=False)
    geometry: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    source_node: Mapped[RoadNode] = relationship(
        foreign_keys=[source_node_id], back_populates="outgoing_edges"
    )
    target_node: Mapped[RoadNode] = relationship(
        foreign_keys=[target_node_id], back_populates="incoming_edges"
    )
    __table_args__ = (
        UniqueConstraint(
            "dataset_id", "source_node_id", "target_node_id", name="uq_edge_dataset_source_target"
        ),
        {"schema": SCHEMA},
    )


class Vehicle(OptimaEntity, Base):
    __tablename__ = "vehicle"
    vehicle_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE"), nullable=False
    )
    external_key: Mapped[str] = mapped_column(Text, nullable=False)
    capacity_units: Mapped[int] = mapped_column(Integer, nullable=False)
    home_location_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.location.location_id")
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, default="available")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    tenant: Mapped[Tenant] = relationship(back_populates="vehicles")
    __table_args__ = (
        UniqueConstraint("tenant_id", "external_key", name="uq_vehicle_tenant_key"),
        {"schema": SCHEMA},
    )


class VehicleShift(OptimaEntity, Base):
    __tablename__ = "vehicle_shift"
    shift_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    vehicle_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.vehicle.vehicle_id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="CASCADE"), nullable=False
    )
    available_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    available_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    start_location_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.location.location_id")
    )
    end_location_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.location.location_id")
    )


class LogisticsOrder(OptimaEntity, Base):
    __tablename__ = "logistics_order"
    order_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="CASCADE"), nullable=False
    )
    external_key: Mapped[str] = mapped_column(Text, nullable=False)
    pickup_location_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.location.location_id"), nullable=False
    )
    delivery_location_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.location.location_id"), nullable=False
    )
    demand_units: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    tenant: Mapped[Tenant] = relationship(back_populates="orders")
    scenario: Mapped[Scenario] = relationship(back_populates="orders")
    __table_args__ = (
        UniqueConstraint("tenant_id", "external_key", name="uq_order_tenant_key"),
        {"schema": SCHEMA},
    )


class TrafficHistory(OptimaEntity, Base):
    __tablename__ = "traffic_history"
    traffic_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="SET NULL")
    )
    zone_id: Mapped[str] = mapped_column(Text, nullable=False)
    edge_id: Mapped[str | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.road_edge.edge_id", ondelete="SET NULL")
    )
    multiplier: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    speed_kph: Mapped[Decimal | None] = mapped_column(Numeric(8, 3))
    congestion_level: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    source: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    __table_args__ = (
        Index("ix_traffic_tenant_zone_time", "tenant_id", "zone_id", "observed_at", postgresql_include=("multiplier", "speed_kph", "congestion_level")),
        Index("ix_traffic_edge_time", "edge_id", "observed_at"),
        Index("ix_traffic_scenario_time", "scenario_id", "observed_at"),
        {"schema": SCHEMA, "postgresql_partition_by": "RANGE (observed_at)"},
    )


class WeatherObservation(OptimaEntity, Base):
    __tablename__ = "weather_observation"
    weather_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    dataset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.dataset_version.dataset_id", ondelete="SET NULL")
    )
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    station_id: Mapped[str] = mapped_column(Text, nullable=False)
    zone_id: Mapped[str | None] = mapped_column(Text)
    condition: Mapped[str | None] = mapped_column(Text)
    temperature_c: Mapped[Decimal | None] = mapped_column(Numeric(7, 3))
    precipitation_mm: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    features: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    __table_args__ = (
        UniqueConstraint("station_id", "observed_at", name="uq_weather_station_time"),
        {"schema": SCHEMA},
    )


class ModelVersion(OptimaEntity, Base):
    __tablename__ = "model_version"
    model_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE")
    )
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    model_type: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(Text, nullable=False)
    feature_version: Mapped[str] = mapped_column(Text, nullable=False)
    artifact_uri: Mapped[str | None] = mapped_column(Text)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    __table_args__ = (
        UniqueConstraint("tenant_id", "model_name", "version", name="uq_model_tenant_name_version"),
        {"schema": SCHEMA},
    )


class DemandPrediction(OptimaEntity, Base):
    __tablename__ = "demand_prediction"
    prediction_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="SET NULL")
    )
    model_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.model_version.model_id"), nullable=False
    )
    zone_id: Mapped[str] = mapped_column(Text, nullable=False)
    forecast_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    horizon_steps: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_units: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    lower_bound: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    upper_bound: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    feature_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    __table_args__ = (
        UniqueConstraint(
            "model_id",
            "zone_id",
            "forecast_for",
            "generated_at",
            name="uq_demand_prediction_identity",
        ),
        {"schema": SCHEMA},
    )


class ETAPrediction(OptimaEntity, Base):
    __tablename__ = "eta_prediction"
    eta_prediction_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="SET NULL")
    )
    model_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.model_version.model_id"), nullable=False
    )
    order_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.logistics_order.order_id", ondelete="SET NULL")
    )
    edge_id: Mapped[str | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.road_edge.edge_id", ondelete="SET NULL")
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    predicted_seconds: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    late_probability: Mapped[Decimal | None] = mapped_column(Numeric(8, 6))
    feature_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class OptimizationRun(OptimaEntity, Base):
    __tablename__ = "optimization_run"
    optimization_run_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="CASCADE"), nullable=False
    )
    algorithm: Mapped[str] = mapped_column(Text, nullable=False)
    solver_version: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(Text, nullable=False)
    objective_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    total_distance_km: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    total_lateness_sec: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    feasible: Mapped[bool | None] = mapped_column(Boolean)
    diagnostics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    scenario: Mapped[Scenario] = relationship(back_populates="optimization_runs")


class RouteAssignment(OptimaEntity, Base):
    __tablename__ = "route_assignment"
    assignment_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    optimization_run_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.optimization_run.optimization_run_id", ondelete="CASCADE"),
        nullable=False,
    )
    vehicle_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.vehicle.vehicle_id"), nullable=False
    )
    route_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    objective_contribution: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    __table_args__ = (
        UniqueConstraint("optimization_run_id", "vehicle_id", name="uq_assignment_run_vehicle"),
        UniqueConstraint("optimization_run_id", "route_rank", name="uq_assignment_run_rank"),
        {"schema": SCHEMA},
    )


class RouteStop(OptimaEntity, Base):
    __tablename__ = "route_stop"
    stop_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    assignment_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.route_assignment.assignment_id", ondelete="CASCADE"), nullable=False
    )
    order_id: Mapped[UUID | None] = mapped_column(ForeignKey(f"{SCHEMA}.logistics_order.order_id"))
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    location_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.location.location_id"), nullable=False
    )
    planned_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        UniqueConstraint("assignment_id", "sequence_no", name="uq_stop_assignment_sequence"),
        {"schema": SCHEMA},
    )


class RLExperiment(OptimaEntity, Base):
    __tablename__ = "rl_experiment"
    experiment_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    algorithm: Mapped[str] = mapped_column(Text, nullable=False, default="ppo")
    policy_model_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.model_version.model_id")
    )
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RLEpisode(OptimaEntity, Base):
    __tablename__ = "rl_episode"
    episode_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    experiment_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.rl_experiment.experiment_id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="CASCADE"), nullable=False
    )
    seed: Mapped[int] = mapped_column(BigInteger, nullable=False)
    episode_no: Mapped[int] = mapped_column(Integer, nullable=False)
    total_reward: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    win: Mapped[bool | None] = mapped_column(Boolean)
    runtime_ms: Mapped[Decimal | None] = mapped_column(Numeric(18, 3))
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    __table_args__ = (
        UniqueConstraint(
            "experiment_id", "seed", "episode_no", name="uq_episode_experiment_seed_no"
        ),
        {"schema": SCHEMA},
    )


class RLStep(OptimaEntity, Base):
    __tablename__ = "rl_step"
    step_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    episode_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.rl_episode.episode_id", ondelete="CASCADE"), nullable=False
    )
    step_no: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    action: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    reward: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    next_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    __table_args__ = (
        UniqueConstraint("episode_id", "step_no", name="uq_step_episode_no"),
        {"schema": SCHEMA},
    )


class DecisionRecord(OptimaEntity, Base):
    __tablename__ = "decision_record"
    decision_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="RESTRICT"), nullable=False
    )
    optimization_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.optimization_run.optimization_run_id", ondelete="SET NULL")
    )
    episode_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.rl_episode.episode_id", ondelete="SET NULL")
    )
    demand_model_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.model_version.model_id", ondelete="SET NULL")
    )
    eta_model_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.model_version.model_id", ondelete="SET NULL")
    )
    policy_model_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.model_version.model_id", ondelete="SET NULL")
    )
    algorithm: Mapped[str] = mapped_column(Text, nullable=False)
    selected_action: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    objective_metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    uncertainty: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    code_commit: Mapped[str | None] = mapped_column(CHAR(40))
    state_reference: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="proposed")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    candidates: Mapped[list[DecisionCandidate]] = relationship(
        back_populates="decision", cascade="all, delete-orphan"
    )
    traces: Mapped[list[DecisionTrace]] = relationship(
        back_populates="decision", cascade="all, delete-orphan"
    )
    evidence: Mapped[list[EvidenceItem]] = relationship(
        back_populates="decision", cascade="all, delete-orphan"
    )
    __table_args__ = (
        Index("ix_decision_tenant_scenario_time", "tenant_id", "scenario_id", "created_at"),
        Index("ix_decision_tenant_status_time", "tenant_id", "status", "created_at"),
        Index("ix_decision_optimization", "optimization_run_id", postgresql_where=(optimization_run_id.is_not(None))),
        Index("ix_decision_episode", "episode_id", postgresql_where=(episode_id.is_not(None))),
        {"schema": SCHEMA},
    )


class DecisionCandidate(OptimaEntity, Base):
    __tablename__ = "decision_candidate"
    candidate_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.decision_record.decision_id", ondelete="CASCADE"), nullable=False
    )
    rank: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    action: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    objective_metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    feasible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    decision: Mapped[DecisionRecord] = relationship(back_populates="candidates")
    __table_args__ = (
        UniqueConstraint("decision_id", "rank", name="uq_candidate_decision_rank"),
        {"schema": SCHEMA},
    )


class DecisionTrace(OptimaEntity, Base):
    __tablename__ = "decision_trace"
    trace_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.decision_record.decision_id", ondelete="CASCADE"), nullable=False
    )
    parent_trace_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.decision_trace.trace_id", ondelete="SET NULL")
    )
    component: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    latency_ms: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    decision: Mapped[DecisionRecord] = relationship(back_populates="traces")


class EvidenceItem(OptimaEntity, Base):
    __tablename__ = "evidence_item"
    evidence_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    decision_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.decision_record.decision_id", ondelete="CASCADE"), nullable=False
    )
    evidence_type: Mapped[str] = mapped_column(Text, nullable=False)
    source_table: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[str] = mapped_column(Text, nullable=False)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decision: Mapped[DecisionRecord] = relationship(back_populates="evidence")


class ToolCall(OptimaEntity, Base):
    __tablename__ = "tool_call"
    tool_call_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    decision_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.decision_record.decision_id", ondelete="CASCADE")
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE"), nullable=False
    )
    tool_name: Mapped[str] = mapped_column(Text, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    success: Mapped[bool | None] = mapped_column(Boolean)
    arguments: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    response: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


class ScenarioModification(OptimaEntity, Base):
    __tablename__ = "scenario_modification"
    modification_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    decision_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.decision_record.decision_id", ondelete="SET NULL")
    )
    base_scenario_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="CASCADE"), nullable=False
    )
    derived_scenario_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="CASCADE"), nullable=False
    )
    requested_by: Mapped[str] = mapped_column(Text, nullable=False)
    changes: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    baseline_mutated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SystemEvent(OptimaEntity, Base):
    __tablename__ = "system_event"
    event_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.tenant.tenant_id", ondelete="CASCADE")
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    component: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(UUIDType)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class BenchmarkRun(OptimaEntity, Base):
    __tablename__ = "benchmark_run"
    benchmark_id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    experiment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.rl_experiment.experiment_id", ondelete="SET NULL")
    )
    scenario_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.scenario.scenario_id", ondelete="SET NULL")
    )
    algorithm_version: Mapped[str] = mapped_column(Text, nullable=False)
    seed: Mapped[int | None] = mapped_column(BigInteger)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    runtime_ms: Mapped[Decimal | None] = mapped_column(Numeric(18, 3))
    objective_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    lateness_sec: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    feasible: Mapped[bool | None] = mapped_column(Boolean)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


__all__ = [
    name
    for name in globals()
    if not name.startswith("_") and name not in {"Any", "UUID", "Decimal", "datetime"}
]
