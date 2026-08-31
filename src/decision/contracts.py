"""Canonical contracts linking the five OPTIMA-X phases."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class PredictionBundle:
    timestamp: datetime
    demand_forecasts: dict[str, float]
    eta_predictions: dict[str, float]
    late_probabilities: dict[str, float]
    uncertainty: dict[str, float] = field(default_factory=dict)
    model_versions: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RLDecision:
    policy_version: str
    state_reference: str
    action: str
    masked_actions: tuple[str, ...]
    reward: float
    diagnostics: dict[str, float] = field(default_factory=dict)
    next_state_reference: str = ""


@dataclass(frozen=True)
class CandidateEvidence:
    candidate_id: str
    action: str
    feasible: bool
    objective: float
    rejection_reason: str = ""
    metrics: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    scenario_id: str
    state_reference: str
    dataset_version: str
    model_versions: dict[str, str]
    solver_version: str
    rl_policy_version: str
    selected_action: str
    objective_metrics: dict[str, float]
    candidates: tuple[CandidateEvidence, ...] = ()
    prediction_bundle: PredictionBundle | None = None
    rl_decision: RLDecision | None = None
    code_commit: str = ""
    experiment_id: str = ""
    explanation_evidence: tuple[str, ...] = ()
