# OPTIMA-X Phase 5: Decision Intelligence

## Purpose

Phase 5 turns the Phase 1–4 computational pipeline into an auditable decision-intelligence system. Programmatic components remain the source of truth for forecasts, routes, constraints, rewards, and metrics. The assistant interprets validated tool responses and cannot mutate operational state.

## Connected evidence flow

`OperationalState → PredictionBundle → OptimizationResult → RLDecision → DecisionRecord → EvidenceBundle → validated tool response → explanation or counterfactual.`

The new canonical contracts are in `src/decision/contracts.py`. Decision records retain the scenario, state reference, dataset version, model versions, solver version, RL policy version, selected action, objective metrics, candidates, and code commit.

## Evidence-first explainability

`build_evidence` constructs a structured `EvidenceBundle` from a `DecisionRecord`. `explain_record` returns four explicit sections: decision, evidence, alternatives, and uncertainty. Numeric values are copied from trusted records; no model-generated number is accepted as operational truth.

## Controlled orchestration

`ToolRegistry` exposes an allowlist of read-only or analytical tools. Requests are validated using Pydantic schemas and guardrails reject unknown tools, mutation-shaped arguments, and excessive call depth. Scenario modifications are validated and returned as isolated computations with `baseline_mutated=False`. The assistant supports both structured tool requests and simple natural-language demand/traffic scenario requests.

## API surface

The Phase 5 API now includes:

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/decisions/record` | Store a local auditable decision record |
| `GET /api/v1/decisions/{id}` | Retrieve a decision trace |
| `POST /api/v1/decisions/explain` | Build an evidence-grounded explanation |
| `POST /api/v1/decisions/compare` | Compare stored candidates |
| `POST /api/v1/scenarios/simulate` | Validate an isolated what-if modification |
| `POST /api/v1/assistant/query` | Execute a structured or natural-language analytical request |

PostgreSQL DDL adds decision records, candidates, traces, tool calls, explanations, and scenario modifications while preserving the local in-memory repository for tests and lightweight deployments.

## Evaluation

The fixed Phase 5 evaluation harness measured schema-valid rate, tool success rate, grounded-response rate, and natural-language scenario parsing. The current deterministic evaluation achieved **100%** on all four checks across three known-answer tool cases plus a demand/traffic scenario query. This validates orchestration safety and contract behavior, not the quality of a future external LLM model.

## PPO stabilization result

The Phase 4 environment now defaults to reward scaling and clipping (`reward_scale=50`, `reward_clip=10`) while retaining raw component semantics when custom weights are supplied. Under the paired five-seed evaluation, the mean PPO advantage became **+0.391**, standard deviation **1.057**, and win rate remained **20%**. Reward scaling reduced numerical scale but did not solve policy-selection instability; the next improvement should be a higher-capacity actor–critic with paired fixed scenarios and a Phase 3 optimization fallback.
