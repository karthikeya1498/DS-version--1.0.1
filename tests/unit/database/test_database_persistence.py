"""Unit tests for SQLAlchemy database persistence, models, and repositories."""
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import (
    Base,
    DecisionTraceModel,
    OptimizationPlanModel,
    OrderModel,
    SimulationRunModel,
    VehicleModel,
)
from src.database.repositories import (
    OptimizationPlanRepository,
    OrderRepository,
    VehicleRepository,
)


@pytest.fixture
def db_session():
    # In-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_order_repository_crud(db_session):
    repo = OrderRepository(db_session)
    now = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)

    order = OrderModel(
        order_id="ORD-001",
        origin_node="node-1",
        origin_zone="zone-1",
        dest_node="node-2",
        dest_zone="zone-2",
        demand_units=3,
        priority=2,
        status="pending",
        created_at=now,
    )
    repo.save(order)

    fetched = repo.get("ORD-001")
    assert fetched is not None
    assert fetched.demand_units == 3
    assert fetched.dest_zone == "zone-2"

    all_orders = repo.list()
    assert len(all_orders) == 1


def test_vehicle_and_plan_persistence(db_session):
    v_repo = VehicleRepository(db_session)
    veh = VehicleModel(
        vehicle_id="V-100",
        home_base_node="depot",
        capacity_units=15,
        load_units=5,
        current_node="depot",
        current_zone="zone-0",
        status="available",
    )
    v_repo.save(veh)
    assert v_repo.get("V-100").capacity_units == 15

    p_repo = OptimizationPlanRepository(db_session)
    plan = OptimizationPlanModel(
        plan_id="PLAN-42",
        strategy="greedy_2opt",
        total_cost=125.5,
        served_orders=10,
        unserved_orders=0,
        runtime_ms=12.4,
        routes_json={"v1": ["depot", "stop1", "stop2"]},
    )
    p_repo.save(plan)

    fetched_plan = p_repo.get("PLAN-42")
    assert fetched_plan is not None
    assert fetched_plan.strategy == "greedy_2opt"
    assert fetched_plan.routes_json["v1"] == ["depot", "stop1", "stop2"]
