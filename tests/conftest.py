"""Shared test environment isolation.

Author: Karthikeya
"""

import pytest

pytest_plugins = ["tests.integration.db_fixtures"]


@pytest.fixture(autouse=True)
def isolate_application_environment(monkeypatch):
    """Use safe deterministic development settings unless a test overrides them."""
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("AUTH_REQUIRED", "false")
    monkeypatch.setenv("JWT_SECRET", "test-secret-for-isolated-suite")
