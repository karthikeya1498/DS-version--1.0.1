from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.strip() + "\n", encoding="utf-8")


files = {
    "README.md": """# OPTIMA-X

OPTIMA-X is a Python-first hybrid decision and optimization engine for dynamic urban logistics. It combines data validation, machine-learning forecasts, graph algorithms, constraint-aware optimization, simulation, reinforcement learning, and explainable decisions.

## Step 1 status

This first scaffold provides the modular-monolith directory structure, configuration conventions, FastAPI health endpoint, Docker/PostgreSQL development setup, TypeScript/HTML/CSS dashboard foundation, CI, and a testable package foundation. Domain algorithms will be implemented incrementally in the planned order: simulator, graph/DSA, ML, optimizer, benchmarks, API, dashboard, RL, and explanation tooling.

## Quick start

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn api.main:app --reload
```

The API documentation is available at `http://localhost:8000/docs`.
""",
    "LICENSE": """MIT License

Copyright (c) 2026 OPTIMA-X contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
""",
    ".gitignore": """.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
.env
*.log
.vscode/
.idea/
data/raw/*
data/interim/*
data/processed/*
data/synthetic/*
models/*
mlruns/*
!data/**/.gitkeep
!models/**/.gitkeep
!mlruns/.gitkeep
""",
    ".env.example": """APP_ENV=development
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg://optima:optima@localhost:5432/optima_x
API_HOST=0.0.0.0
API_PORT=8000
""",
    "pyproject.toml": """[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "optima-x"
version = "0.1.0"
description = "Hybrid ML, algorithms, optimization, and RL engine for dynamic decision optimization"
requires-python = ">=3.11"
dependencies = ["fastapi>=0.115", "uvicorn[standard]>=0.30", "pydantic-settings>=2.6", "pyyaml>=6.0"]

[project.optional-dependencies]
dev = ["pytest>=8.3", "pytest-asyncio>=0.24", "httpx>=0.27", "ruff>=0.8", "mypy>=1.13"]
ml = ["pandas>=2.2", "numpy>=2.1", "scikit-learn>=1.5", "xgboost>=2.1", "torch>=2.5"]
optimization = ["ortools>=9.11"]
tracking = ["mlflow>=2.18"]
database = ["sqlalchemy>=2.0", "psycopg[binary]>=3.2"]

[tool.setuptools.packages.find]
include = ["api*", "src*"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
""",
    "requirements.txt": """fastapi>=0.115
uvicorn[standard]>=0.30
pydantic-settings>=2.6
pyyaml>=6.0
pandas>=2.2
numpy>=2.1
scikit-learn>=1.5
xgboost>=2.1
ortools>=9.11
mlflow>=2.18
sqlalchemy>=2.0
psycopg[binary]>=3.2
pytest>=8.3
pytest-asyncio>=0.24
httpx>=0.27
ruff>=0.8
mypy>=1.13
""",
    "configs/base.yaml": """project:
  name: optima-x
  version: 0.1.0
simulation:
  seed: 42
  zones: 20
  vehicles: 100
  orders_per_hour: 1000
forecast:
  horizon_minutes: 60
  model: xgboost
routing:
  shortest_path: astar
  local_search: two_opt
optimization:
  timeout_seconds: 2
  alpha_distance: 1.0
  beta_lateness: 5.0
  gamma_fuel: 1.5
  delta_unserved: 20.0
  epsilon_vehicle_activation: 2.0
rl:
  algorithm: ppo
  episodes: 1000
""",
    "src/common/config.py": """from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://optima:optima@localhost:5432/optima_x"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_yaml_config(path: str | Path = "configs/base.yaml") -> dict:
    with Path(path).open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}
""",
    "src/common/logger.py": """import logging


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s %(message)s")
""",
    "api/schemas/responses.py": """from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
""",
    "api/routes/health.py": """from fastapi import APIRouter

from api.schemas.responses import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="optima-x-api", version="0.1.0")
""",
    "api/main.py": """from fastapi import FastAPI

from api.routes.health import router as health_router
from src.common.config import get_settings
from src.common.logger import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title="OPTIMA-X API", version="0.1.0", description="Decision and optimization engine API")
app.include_router(health_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "optima-x-api", "docs": "/docs"}
""",
    "tests/api/test_health.py": """from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
""",
    "Makefile": """install:
\tpip install -e '.[dev]'

run:
\tuvicorn api.main:app --reload

test:
\tpytest -q

lint:
\truff check .

format:
\truff format .
""",
    "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml requirements.txt README.md ./
RUN pip install --no-cache-dir -r requirements.txt
COPY api ./api
COPY src ./src
COPY configs ./configs
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "docker-compose.yml": """services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: optima_x
      POSTGRES_USER: optima
      POSTGRES_PASSWORD: optima
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    environment:
      DATABASE_URL: postgresql+psycopg://optima:optima@postgres:5432/optima_x
    ports:
      - "8000:8000"
    depends_on:
      - postgres

volumes:
  postgres_data:
""",
    "frontend/package.json": """{
  "name": "optima-x-frontend", "private": true, "version": "0.2.0", "type": "module", "author": "Karthikeya",
  "scripts": { "dev": "vite", "build": "tsc --noEmit && vite build", "check": "tsc --noEmit" },
  "devDependencies": { "@types/node": "^22.0.0", "typescript": "^5.7.0", "vite": "^6.0.0" }
}""",
    "frontend/tsconfig.json": """{
  "compilerOptions": { "target": "ES2022", "module": "ESNext", "moduleResolution": "Bundler", "strict": true, "noEmit": true, "skipLibCheck": true, "lib": ["ES2022", "DOM", "DOM.Iterable"] },
  "include": ["src"]
}""",
    "frontend/vite.config.js": """import { defineConfig } from 'vite';
export default defineConfig({});
""",
    "frontend/index.html": """<!doctype html>
<html lang="en">
  <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>OPTIMA-X</title></head>
  <body><div id="app">Loading OPTIMA-X dashboard…</div><script type="module" src="/src/main.ts"></script></body>
</html>
""",
    "frontend/src/main.ts": """/** OPTIMA-X TypeScript dashboard foundation. Author: Karthikeya. */
import './style.css';
const app = document.querySelector<HTMLDivElement>('#app');
if (app) app.textContent = 'OPTIMA-X dashboard foundation';
""",
    "frontend/src/style.css": """/* OPTIMA-X dashboard foundation. Author: Karthikeya. */
:root { color-scheme: dark; font-family: system-ui, sans-serif; background: #080a0f; color: #f4f7fb; }
body { margin: 0; min-width: 320px; }
""",
    "docs/research/methodology.md": """# OPTIMA-X Methodology

This document will record datasets, baselines, constraints, evaluation metrics, and the reproducibility protocol as implementation advances.
""",
    "docs/architecture/README.md": """# Architecture Documentation

The initial architecture is a modular monolith with explicit boundaries for data, features, DSA, ML, optimization, simulation, decisions, API, and frontend layers.
""",
}

for path, text in files.items():
    write(path, text)

for directory in [ROOT / "src", ROOT / "api", *[p for p in ROOT.rglob("*") if p.is_dir()]]:
    if directory.name not in {
        "frontend",
        "data",
        "configs",
        "docs",
        "experiments",
        "models",
        "mlruns",
        "notebooks",
    }:
        (directory / "__init__.py").touch(exist_ok=True)

for name in ["development.yaml", "production.yaml"]:
    write(f"configs/{name}", "# Environment-specific overrides.\n")
for name in ["demand_xgboost.yaml", "eta_xgboost.yaml", "routing_astar.yaml", "rl_ppo.yaml"]:
    write(f"configs/experiments/{name}", "# Experiment-specific configuration placeholder.\n")
for name in ["cost_minimization.yaml", "service_level.yaml"]:
    write(f"configs/objectives/{name}", "# Objective-weight configuration placeholder.\n")

print("OPTIMA-X boilerplate generated")
