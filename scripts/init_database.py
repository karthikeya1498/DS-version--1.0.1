"""Initialize the Phase 1 PostgreSQL schema."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.database.connection import create_engine_if_available


def initialize(schema_path: str | Path = 'src/database/schema.sql') -> bool:
    engine = create_engine_if_available()
    if engine is None: return False
    from sqlalchemy import text
    statements = [statement.strip() for statement in Path(schema_path).read_text(encoding='utf-8').split(';') if statement.strip()]
    with engine.begin() as connection:
        for statement in statements: connection.execute(text(statement))
    return True

if __name__ == '__main__': print({'database_initialized': initialize()})
