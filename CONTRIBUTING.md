# Contributing to OPTIMA-X

OPTIMA-X is a research-oriented logistics decision engine. Contributions should preserve reproducibility, explicit contracts, and testable behavior across simulation, routing, forecasting, optimization, and service layers.

## Development workflow

Create a focused branch for each change, run `python3 -m compileall -q api src tests benchmarks scripts`, run `pytest -q`, and include a concise explanation of the behavior changed. For forecasting work, record dataset provenance, use chronological evaluation, and document feature construction. For routing work, report path-cost parity against a reference algorithm and include deterministic seeds where randomness is involved.

## Commit standards

Use meaningful conventional commit messages such as `feat:`, `fix:`, `test:`, `docs:`, or `chore:`. Do not create empty commits or split one trivial change into artificial activity. Each commit should represent a reviewable project improvement.

## Security

Never commit credentials, JWT secrets, `.env` files, model artifacts containing private data, or raw data that is not legally redistributable. Production deployments must enable authentication, use a strong secret manager, and replace in-process rate limiting with a shared store when horizontally scaled.
