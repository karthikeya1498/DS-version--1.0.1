# OPTIMA-X Language Matrix

**Author: Karthikeya**

This matrix is the canonical implementation guide for the multi-language architecture. Each language has a bounded responsibility and a discoverable entry point in the repository.

| Language | Where used | Main purpose | Repository entry points |
|---|---|---|---|
| Python | Phases 1–5 | Data engineering, ML, simulation, optimization, RL, decision intelligence, APIs | `src/`, `api/`, `scripts/`, `dashboard.py` |
| Java | Core DSA and benchmark layer | Advanced DSA implementations: graphs, Dijkstra, A*, heaps, dynamic programming, DSU | `java-dsa/src/main/java/com/optimax/dsa/` |
| SQL | Phases 1–5 | PostgreSQL schema, data querying, joins, CTEs, window-function analytics | `src/database/schema.sql` |
| TypeScript | Phase 5 operations dashboard | Typed browser interaction, API calls, scenario metrics, decision traces | `frontend/src/main.ts` |
| HTML | Phase 5 operations dashboard | Accessible document shell and metadata | `frontend/index.html` |
| CSS | Phase 5 operations dashboard | Responsive visual system, layout, states, and accessibility preferences | `frontend/src/style.css` |
| YAML | Phases 1–5 | Configuration, ML/RL/optimization settings, CI/CD workflows | `configs/`, `.github/workflows/` |
| Bash / PowerShell | Phases 1–5 | Scripts, automation, Docker, and CI/CD operations | `scripts/`, `Dockerfile`, workflow commands |

The TypeScript dashboard is distinct from the Streamlit research dashboard. The former is the browser-facing operations view that calls FastAPI; the latter remains a Python-first analytical interface for research visualization. Java is similarly isolated as an explicit DSA implementation and benchmark layer while Python remains the application orchestration language.
