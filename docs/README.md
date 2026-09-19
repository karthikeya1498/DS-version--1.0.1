# OPTIMA-X Documentation

**Author: Karthikeya**

The repository root is intentionally reserved for executable project files, configuration, and the main README. Long-form planning and evidence belong under this directory so the GitHub landing page stays readable.

## Directory map

| Directory | Contents |
|---|---|
| [`architecture/`](architecture/) | System boundaries, PostgreSQL schema, migrations, security, and phase contracts |
| [`research/`](research/) | Datasets, benchmark methods, quantitative findings, model validation, and phase research |
| [`reports/`](reports/) | Long-form project reports, including the complete DOCX deliverable |
| [`reviews/`](reviews/) | Performance, security, frontend, and implementation review notes |
| [`interview/`](interview/) | Recruiter and technical-interview preparation material |

## Documentation hygiene

New `.docx`, `.pdf`, and long-form planning files should be placed in `reports/`, `architecture/`, or `research/` rather than the repository root. The root should contain only the README, license, contribution guidance, runtime manifests, container files, and top-level application entry points.

The quantitative claims presented on the repository landing page are sourced from [`research/benchmark_and_forecasting_report.md`](research/benchmark_and_forecasting_report.md). When new metrics are added, include the dataset, split strategy, seed, metric definition, and artifact path so the claim remains reproducible.
