"""Cross-phase architecture status contract for the OPTIMA-X console.

Author: Karthikeya
The endpoint is intentionally metadata-only: it reports the declared phase
contracts and persistence boundaries without exposing tenant data.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/architecture", tags=["architecture"])


class PhaseStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    phase: int
    name: str
    contract: str
    persistence: str
    status: str


PHASES = [
    PhaseStatus(phase=1, name="World", contract="OperationalState", persistence="scenario, graph, orders, fleet, traffic", status="active"),
    PhaseStatus(phase=2, name="Forecast", contract="PredictionBundle", persistence="model_version, demand_prediction, eta_prediction", status="active"),
    PhaseStatus(phase=3, name="Optimize", contract="OptimizationResult", persistence="optimization_run, route_assignment, route_stop", status="active"),
    PhaseStatus(phase=4, name="Learn", contract="PolicyOutcome", persistence="rl_experiment, rl_episode, rl_step", status="active"),
    PhaseStatus(phase=5, name="Explain", contract="DecisionRecord", persistence="decision lineage and evidence", status="active"),
    PhaseStatus(phase=6, name="Operate", contract="RuntimeTelemetry", persistence="system_event, traffic history", status="active"),
    PhaseStatus(phase=7, name="Prove", contract="BenchmarkEvidence", persistence="benchmark_run and research artifacts", status="ready"),
]


@router.get("/status", response_model=list[PhaseStatus])
def architecture_status() -> list[PhaseStatus]:
    """Return the public, non-tenant-specific Phase 1–7 connectivity contract."""
    return PHASES
