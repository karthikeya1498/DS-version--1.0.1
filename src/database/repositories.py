"""SQLAlchemy and in-memory repositories for OPTIMA-X persistence."""
from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy.orm import Session

from src.database.models import (
    DecisionTraceModel,
    ExperimentRecord,
    OptimizationPlanModel,
    OrderModel,
    SimulationRunModel,
    VehicleModel,
)


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, order: OrderModel) -> OrderModel:
        self.session.merge(order)
        self.session.commit()
        return order

    def get(self, order_id: str) -> OrderModel | None:
        return self.session.query(OrderModel).filter_by(order_id=order_id).first()

    def list(self) -> list[OrderModel]:
        return self.session.query(OrderModel).all()


class VehicleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, vehicle: VehicleModel) -> VehicleModel:
        self.session.merge(vehicle)
        self.session.commit()
        return vehicle

    def get(self, vehicle_id: str) -> VehicleModel | None:
        return self.session.query(VehicleModel).filter_by(vehicle_id=vehicle_id).first()

    def list(self) -> list[VehicleModel]:
        return self.session.query(VehicleModel).all()


class OptimizationPlanRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, plan: OptimizationPlanModel) -> OptimizationPlanModel:
        self.session.merge(plan)
        self.session.commit()
        return plan

    def get(self, plan_id: str) -> OptimizationPlanModel | None:
        return self.session.query(OptimizationPlanModel).filter_by(plan_id=plan_id).first()

    def list(self) -> list[OptimizationPlanModel]:
        return self.session.query(OptimizationPlanModel).all()


class ExperimentRepository:
    """In-memory experiment repository for local experiment tracking."""

    def __init__(self) -> None:
        self._records: dict[str, ExperimentRecord] = {}

    def save(self, record: ExperimentRecord) -> ExperimentRecord:
        self._records[record.experiment_id] = record
        return record

    def get(self, experiment_id: str) -> ExperimentRecord | None:
        return self._records.get(experiment_id)

    def list(self) -> list[ExperimentRecord]:
        return list(self._records.values())
