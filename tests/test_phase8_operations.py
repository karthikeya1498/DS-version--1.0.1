"""Phase 8 operational-intelligence tests.

Author: Karthikeya
"""
from fastapi.testclient import TestClient
import pytest

from api.main import app
from src.observability.metrics import MetricsRegistry


def test_metrics_registry_aggregates_requests_and_latency() -> None:
    registry = MetricsRegistry()
    registry.observe("/api/v1/health", 4.0)
    registry.observe("/api/v1/health", 6.0, error=True)
    snapshot = registry.snapshot()["/api/v1/health"]
    assert snapshot == {"requests": 2, "errors": 1, "latency_ms_total": 10.0, "average_latency_ms": 5.0}


def test_metrics_registry_rejects_negative_latency() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        MetricsRegistry().observe("/health", -1.0)


def test_readiness_exposes_phase8_and_all_prior_contracts() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/operations/readiness")
    assert response.status_code == 200
    payload = response.json()
    assert payload["phase"] == 8
    assert len(payload["contracts"]) == 8
    assert payload["contracts"][-1] == "OperationalIntelligence"
    assert payload["persistence"]["engine"] == "PostgreSQL 16"


def test_request_metrics_are_visible_after_health_request() -> None:
    client = TestClient(app)
    assert client.get("/api/v1/health").status_code == 200
    payload = client.get("/api/v1/operations/metrics").json()
    health_metrics = payload["metrics"]["/api/v1/health"]
    assert health_metrics["requests"] >= 1
    assert health_metrics["average_latency_ms"] >= 0
