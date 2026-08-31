"""SQLAlchemy ORM models and dataclass persistence contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OrderModel(Base):
    __tablename__ = "orders"

    order_id = Column(String(64), primary_key=True)
    origin_node = Column(String(64), nullable=False)
    origin_zone = Column(String(64), nullable=False)
    dest_node = Column(String(64), nullable=False)
    dest_zone = Column(String(64), nullable=False)
    demand_units = Column(Integer, nullable=False, default=1)
    priority = Column(Integer, nullable=False, default=1)
    status = Column(String(32), nullable=False, default="pending")
    assigned_vehicle_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)


class VehicleModel(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(String(64), primary_key=True)
    home_base_node = Column(String(64), nullable=False)
    capacity_units = Column(Integer, nullable=False, default=10)
    load_units = Column(Integer, nullable=False, default=0)
    current_node = Column(String(64), nullable=False)
    current_zone = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="available")
    completed_orders = Column(Integer, nullable=False, default=0)


class SimulationRunModel(Base):
    __tablename__ = "simulation_runs"

    run_id = Column(String(64), primary_key=True)
    seed = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    total_orders = Column(Integer, nullable=False)
    delivered_orders = Column(Integer, nullable=False)
    late_deliveries = Column(Integer, nullable=False)
    unserved_orders = Column(Integer, nullable=False)
    total_distance_km = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class OptimizationPlanModel(Base):
    __tablename__ = "optimization_plans"

    plan_id = Column(String(64), primary_key=True)
    strategy = Column(String(64), nullable=False)
    total_cost = Column(Float, nullable=False)
    served_orders = Column(Integer, nullable=False)
    unserved_orders = Column(Integer, nullable=False)
    runtime_ms = Column(Float, nullable=False)
    routes_json = Column(JSON, nullable=True)
    diagnostics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class DecisionTraceModel(Base):
    __tablename__ = "decision_traces"

    trace_id = Column(String(64), primary_key=True)
    decision_type = Column(String(64), nullable=False)
    chosen_candidate = Column(String(128), nullable=False)
    feasible = Column(Boolean, nullable=False, default=True)
    objective_cost = Column(Float, nullable=False, default=0.0)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class ExperimentRecord:
    experiment_id: str
    strategy: str
    seed: int
    created_at: datetime
    metrics: dict[str, float]
