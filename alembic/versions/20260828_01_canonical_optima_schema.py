"""Install the canonical OPTIMA-X PostgreSQL schema.

Revision ID: 20260828_01
Revises:
Create Date: 2026-08-28
Author: Karthikeya

This baseline intentionally executes the reviewed canonical SQL artifact so
schema.sql and migration history have one source of truth at initial adoption.
Future revisions must use explicit Alembic operations and must not edit this
revision after it has been applied anywhere.
"""
from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "20260828_01"
down_revision = None
branch_labels = None
depends_on = None


SQL_PATH = Path(__file__).resolve().parents[2] / "src" / "database" / "optima_schema.sql"


def upgrade() -> None:
    """Install the canonical schema in one controlled migration."""
    op.get_bind().exec_driver_sql(SQL_PATH.read_text(encoding="utf-8"))


def downgrade() -> None:
    """Remove the canonical schema; use only for disposable environments."""
    op.execute("DROP SCHEMA IF EXISTS optima CASCADE")
