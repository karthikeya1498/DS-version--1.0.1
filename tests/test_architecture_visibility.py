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
