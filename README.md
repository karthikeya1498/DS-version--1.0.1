# OPTIMA-X

OPTIMA-X is a Python-first hybrid decision and optimization engine for dynamic urban logistics. It combines data validation, machine-learning forecasts, graph algorithms, constraint-aware optimization, simulation, reinforcement learning, and explainable decisions.

## Step 1 status

This first scaffold provides the modular-monolith directory structure, configuration conventions, FastAPI health endpoint, Docker/PostgreSQL development setup, frontend placeholder, CI, and a testable package foundation. Domain algorithms will be implemented incrementally in the planned order: simulator, graph/DSA, ML, optimizer, benchmarks, API, dashboard, RL, and explanation tooling.

## Quick start

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn api.main:app --reload
```

The API documentation is available at `http://localhost:8000/docs`.
