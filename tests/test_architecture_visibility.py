"""Tests for public implementation visibility metadata.

Author: Karthikeya
"""
from fastapi.testclient import TestClient

from api.main import app


def test_visibility_reports_java_and_postgresql_components() -> None:
    response = TestClient(app).get("/api/v1/architecture/implementation-visibility")
    assert response.status_code == 200
    payload = response.json()
    assert payload["languages"]["java"]["path"] == "java-dsa"
    assert payload["languages"]["sql"]["tables"] == 28
    assert "traffic_history" in payload["persistence"]["partitioned_tables"]
    assert payload["java_dsa"]["build"] == "mvn -q test"


def test_architecture_status_exposes_complete_phase_loop() -> None:
    response = TestClient(app).get("/api/v1/architecture/status")
    assert response.status_code == 200
    phases = response.json()
    assert [phase["phase"] for phase in phases] == list(range(1, 8))
    assert phases[0]["contract"] == "OperationalState"
    assert phases[-1]["contract"] == "BenchmarkEvidence"
