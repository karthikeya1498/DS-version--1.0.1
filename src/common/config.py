from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://optima:optima@localhost:5432/optima_x"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_yaml_config(path: str | Path = "configs/base.yaml") -> dict:
    with Path(path).open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}
