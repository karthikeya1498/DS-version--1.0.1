# OPTIMA-X End-to-End Architecture

**Author: Karthikeya**

OPTIMA-X is implemented as a modular monolith. The API is the application boundary, while each internal subsystem owns one responsibility and communicates through small typed contracts.

| Layer | Responsibility | Current entry points |
|---|---|---|
| Data | Record validation and feature preparation | `src/data`, `src/features` |
| Simulation | Seeded demand, traffic, fleet, and event replay | `src/simulation` |
| Graph/DSA | Weighted road graph, heaps, shortest paths, trees, search | `src/dsa` |
| ML | Baselines, metrics, and registry contract | `src/ml` |
| Optimization | Objective scoring, route feasibility, dispatch, solver orchestration | `src/optimization` |
| RL | Gym-like environment and Q-learning baseline | `src/rl` |
| Decision | Structured result and traceable explanation | `src/decision` |
| Persistence | Database URL factory and repository contracts | `src/database` |
| API | Health, simulation, and optimization endpoints | `api` |
| Frontend | TypeScript operations dashboard with HTML shell and responsive CSS | `frontend/src/main.ts`, `frontend/index.html`, `frontend/src/style.css` |

The frontend dashboard is a browser-facing TypeScript layer that calls the FastAPI application boundary. `dashboard.py` remains the separate Streamlit research and visualization view. The architecture deliberately distinguishes implemented baselines from future research extensions. OR-Tools, PyTorch, MLflow, and PostgreSQL are optional integration dependencies; the local baseline remains runnable without requiring them.
