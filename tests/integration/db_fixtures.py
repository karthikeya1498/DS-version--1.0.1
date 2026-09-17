"""Shared PostgreSQL integration fixture.

Author: Karthikeya
The fixture prefers OPTIMA_TEST_DATABASE_URL for CI service containers and
otherwise starts a disposable PostgreSQL 16 Testcontainers instance.
"""
from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from alembic import command


def _migration_config(url: str) -> Config:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    return config


@pytest.fixture(scope="session")
def postgres_engine() -> Iterator[Engine]:
    """Yield a migrated PostgreSQL database, skipping when Docker is unavailable."""
    container = None
    url = os.getenv("OPTIMA_TEST_DATABASE_URL")
    if not url:
        try:
            from testcontainers.postgres import PostgresContainer
        except ImportError:
            pytest.skip("testcontainers is not installed")
        try:
            container = PostgresContainer("postgres:16-alpine")
            container.start()
            url = container.get_connection_url().replace("postgresql+psycopg2", "postgresql+psycopg")
        except Exception as exc:  # pragma: no cover - depends on host Docker runtime
            if container is not None:
                container.stop()
            pytest.skip(f"PostgreSQL test container unavailable: {exc}")
    engine = create_engine(url, pool_pre_ping=True)
    try:
        os.environ["DATABASE_URL"] = url
        command.upgrade(_migration_config(url), "head")
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(text("DROP SCHEMA IF EXISTS optima CASCADE"))
            connection.execute(text("DROP SCHEMA IF EXISTS archive CASCADE"))
        engine.dispose()
        if container is not None:
            container.stop()
