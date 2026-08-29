"""Container-backed integration tests for ORM and history lifecycle.

Author: Karthikeya
Run with Docker or an existing PostgreSQL URL:
OPTIMA_TEST_DATABASE_URL=postgresql+psycopg://... pytest -m integration -q
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from scripts.manage_history import archive_decisions, archive_traffic, ensure_traffic_partitions
from src.database.orm_models import Base, DecisionRecord, DecisionTrace, EvidenceItem, Tenant

pytestmark = pytest.mark.integration


def _seed_tenant_and_scenario(session: Session):
    tenant = Tenant(tenant_id=uuid4(), tenant_key=f"test-{uuid4().hex[:12]}", display_name="Integration", created_at=datetime.now(UTC))
    session.add(tenant)
    session.flush()
    session.execute(
        text(
            "INSERT INTO optima.scenario "
            "(scenario_id, tenant_id, scenario_key, seed, status, config, starts_at) "
            "VALUES (:id, :tenant, :key, 7, 'created', '{}'::jsonb, :starts)"
        ),
        {"id": uuid4(), "tenant": tenant.tenant_id, "key": uuid4().hex, "starts": datetime.now(UTC)},
    )
    scenario_id = session.execute(text("SELECT scenario_id FROM optima.scenario WHERE tenant_id = :tenant"), {"tenant": tenant.tenant_id}).scalar_one()
    return tenant, scenario_id


def test_migration_exposes_all_mapped_tables(postgres_engine):
    inspector = inspect(postgres_engine)
    tables = set(inspector.get_table_names(schema="optima"))
    assert tables - {"traffic_history_default"} == {table.name for table in Base.metadata.tables.values()}
    assert len(tables) == 29  # 28 mapped tables plus the non-mapped traffic default partition.
    assert "traffic_history_default" in tables


def test_traffic_partition_creation_and_archival(postgres_engine):
    start = datetime(2024, 1, 1, tzinfo=UTC)
    created = ensure_traffic_partitions(postgres_engine, start, months=1)
    assert created == ["traffic_history_202401"]
    with postgres_engine.begin() as connection:
        tenant_id = connection.execute(text("INSERT INTO optima.tenant (tenant_key, display_name) VALUES ('traffic-test', 'Traffic') RETURNING tenant_id")).scalar_one()
        connection.execute(
            text("INSERT INTO optima.traffic_history (tenant_id, zone_id, observed_at, multiplier, source) VALUES (:tenant, 'z1', :observed, 1.4, 'test')"),
            {"tenant": tenant_id, "observed": datetime(2024, 1, 15, tzinfo=UTC)},
        )
    moved = archive_traffic(postgres_engine, datetime(2024, 2, 1, tzinfo=UTC))
    assert moved == ["traffic_history_202401"]
    with postgres_engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM optima.traffic_history")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM archive.traffic_history_202401_archived")).scalar_one() == 1


def test_decision_and_lineage_archival_is_atomic(postgres_engine):
    with Session(postgres_engine) as session:
        tenant, scenario_id = _seed_tenant_and_scenario(session)
        decision_id = uuid4()
        session.add(DecisionRecord(
            decision_id=decision_id, tenant_id=tenant.tenant_id, scenario_id=scenario_id, algorithm="astar",
            selected_action={"route": ["a", "b"]}, state_reference="state:test", created_at=datetime(2024, 1, 15, tzinfo=UTC),
        ))
        session.add(DecisionTrace(trace_id=uuid4(), decision_id=decision_id, component="routing", event_type="selected", occurred_at=datetime(2024, 1, 15, tzinfo=UTC), payload={"cost": 1.0}))
        session.add(EvidenceItem(evidence_id=uuid4(), decision_id=decision_id, evidence_type="traffic", source_table="traffic_history", source_id="t1", claim="multiplier", value={"value": 1.2}, captured_at=datetime(2024, 1, 15, tzinfo=UTC)))
        session.commit()
    archived = archive_decisions(postgres_engine, datetime(2024, 2, 1, tzinfo=UTC))
    assert archived == 1
    with postgres_engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM optima.decision_record")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM archive.decision_record")).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM archive.decision_trace")).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM archive.evidence_item")).scalar_one() == 1
