"""Database connection, engine factory, and schema initialization."""
from __future__ import annotations

import os
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.database.models import Base

DEFAULT_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///optima_x.db")


def get_engine(db_url: str = DEFAULT_DATABASE_URL) -> Engine:
    """Create SQLAlchemy engine with appropriate connection pooling."""
    is_sqlite = db_url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    return create_engine(db_url, connect_args=connect_args)


def init_db(engine: Engine | None = None) -> None:
    """Create all database tables if they do not exist."""
    eng = engine or get_engine()
    Base.metadata.create_all(bind=eng)


def get_session(engine: Engine | None = None) -> Session:
    """Obtain a new database session."""
    eng = engine or get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    return SessionLocal()
