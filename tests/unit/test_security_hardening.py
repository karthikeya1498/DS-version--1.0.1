"""Security regression tests for production authentication defaults.

Author: Karthikeya
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from src.security.auth import AuthConfigurationError, _secret
from src.security.rate_limit import TenantRateLimiter


def test_production_requires_jwt_secret(monkeypatch):
    """Production must not silently use the development JWT secret."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(AuthConfigurationError):
        _secret()


def test_production_requires_a_long_jwt_secret(monkeypatch):
    """Production rejects secrets too short for the configured HMAC boundary."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "short-secret")
    with pytest.raises(AuthConfigurationError):
        _secret()


def test_production_disables_development_token_endpoint(monkeypatch):
    """The development credential endpoint cannot mint tokens in production."""
    monkeypatch.setenv("APP_ENV", "production")
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "user", "password": "password", "tenant_id": "tenant"},
    )
    assert response.status_code == 503


def test_production_rate_limiter_defaults_to_fail_closed(monkeypatch):
    """Redis failures must not silently disable throttling in production."""
    monkeypatch.setenv("APP_ENV", "production")
    limiter = TenantRateLimiter(redis_url=None)
    assert limiter.fail_open is False
