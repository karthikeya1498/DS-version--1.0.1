"""Optional SQLAlchemy connection factory; SQLite is convenient for local experiments."""
from src.common.config import get_settings
def database_url(): return get_settings().database_url

def create_engine_if_available(url=None):
    try:
        from sqlalchemy import create_engine
        return create_engine(url or database_url(), pool_pre_ping=True)
    except ImportError:
        return None
