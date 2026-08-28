"""Integration coverage for authenticated batch traffic ingestion.

Author: Karthikeya
"""

from fastapi.testclient import TestClient

from api.main import app
from src.realtime.traffic_stream import traffic_stream
from src.security.auth import create_token


def _updates(count: int) -> list[dict]:
    """Build deterministic zone updates for contract-level integration tests."""
    return [
        {
            "zone_id": f"zone-{index}",
            "multiplier": 1.0 + index / 10,
            "affected_vehicle_ids": [f"vehicle-{index}"],
        }
        for index in range(count)
    ]


def test_batch_traffic_update_publishes_every_event(monkeypatch):
    """Verify one authenticated request fans out every bounded update."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    token = create_token("batch-user", "batch-tenant")
    received: list[dict] = []
    original_publish = traffic_stream.publish

    async def capture(event_type: str, payload: dict):
        received.append({"event_type": event_type, "payload": payload})
        await original_publish(event_type, payload)

    monkeypatch.setattr(traffic_stream, "publish", capture)
    response = TestClient(app).post(
        "/api/v1/traffic/updates/batch",
        headers={"Authorization": f"Bearer {token}"},
        json={"updates": _updates(25)},
    )
    assert response.status_code == 200
    assert response.json() == {
        "accepted": 25,
        "tenant_id": "batch-tenant",
        "event_type": "route_reoptimization",
    }
    assert len(received) == 25
    assert {item["payload"]["zone_id"] for item in received} == {f"zone-{i}" for i in range(25)}


def test_batch_traffic_update_accepts_exact_maximum_batch(monkeypatch):
    """Verify the documented 100-update upper bound is inclusive."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    token = create_token("batch-user", "batch-max")
    response = TestClient(app).post(
        "/api/v1/traffic/updates/batch",
        headers={"Authorization": f"Bearer {token}"},
        json={"updates": _updates(100)},
    )
    assert response.status_code == 200
    assert response.json()["accepted"] == 100


def test_batch_traffic_update_rejects_empty_and_oversized_payloads(monkeypatch):
    """Verify the API enforces the one-to-one-hundred update contract."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    token = create_token("batch-user", "batch-validation")
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/api/v1/traffic/updates/batch", headers=headers, json={"updates": []}).status_code == 422
    assert client.post("/api/v1/traffic/updates/batch", headers=headers, json={"updates": _updates(101)}).status_code == 422


def test_rate_limit_429_exposes_retry_headers(monkeypatch):
    """Verify clients receive actionable headers when a tenant exhausts its bucket."""
    import src.security.rate_limit as rate_limit_module

    monkeypatch.setattr(rate_limit_module, "limiter", rate_limit_module.TenantRateLimiter(limit=1))
    token = create_token("limited-user", "limited-tenant")
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"zone_id": "zone-limited", "multiplier": 1.2}
    assert client.post("/api/v1/traffic/updates", headers=headers, json=payload).status_code == 200
    response = client.post("/api/v1/traffic/updates", headers=headers, json=payload)
    assert response.status_code == 429
    assert response.headers["x-ratelimit-limit"] == "1"
    assert response.headers["x-ratelimit-remaining"] == "0"
    assert response.headers["retry-after"] == "60"
