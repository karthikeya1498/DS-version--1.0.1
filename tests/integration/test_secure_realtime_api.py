import asyncio

import pytest
from fastapi.testclient import TestClient

from api.main import app
from src.realtime.traffic_stream import traffic_stream
from src.security.auth import create_token, decode_token
from src.security.rate_limit import TenantRateLimiter


def test_jwt_contains_tenant_claims(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    token = create_token("alice", "tenant-a")
    claims = decode_token(token)
    assert claims["sub"] == "alice"
    assert claims["tenant_id"] == "tenant-a"


def test_rate_limiter_isolated_by_tenant():
    limiter = TenantRateLimiter(limit=1, window_seconds=60)
    limiter.check("tenant-a")
    limiter.check("tenant-b")
    with pytest.raises(Exception):
        limiter.check("tenant-a")


def test_login_and_traffic_update_are_tenant_aware(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    client = TestClient(app)
    token = client.post(
        "/api/v1/auth/token",
        json={"username": "alice", "password": "test", "tenant_id": "tenant-a"},
    ).json()["access_token"]
    response = client.post(
        "/api/v1/traffic/updates",
        headers={"Authorization": f"Bearer {token}"},
        json={"zone_id": "zone-1", "multiplier": 1.4, "affected_vehicle_ids": ["v-1"]},
    )
    assert response.status_code == 200
    assert response.json()["tenant_id"] == "tenant-a"


def test_websocket_requires_jwt(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    client = TestClient(app)
    with pytest.raises(Exception), client.websocket_connect("/api/v1/ws/traffic"):
        pass
    token = create_token("alice", "tenant-a")
    with client.websocket_connect(f"/api/v1/ws/traffic?token={token}") as websocket:
        assert websocket.receive_json()["event_type"] == "connected"
        asyncio.run(traffic_stream.publish("route_reoptimization", {"tenant_id": "tenant-a", "zone_id": "zone-1", "multiplier": 1.4, "affected_vehicle_ids": ["v-1"], "action": "recompute_routes"}))
        event = websocket.receive_json()
        assert event["event_type"] == "route_reoptimization"
        assert event["payload"]["zone_id"] == "zone-1"
        assert event["payload"]["tenant_id"] == "tenant-a"
