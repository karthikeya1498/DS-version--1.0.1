"""Evidence-first explanations sourced only from validated decision records."""
from __future__ import annotations

from dataclasses import dataclass

from src.decision.contracts import DecisionRecord


@dataclass(frozen=True)
class EvidenceBundle:
    decision_id: str
    decision: str
    evidence: tuple[str, ...]
    alternatives: tuple[str, ...]
    uncertainty: tuple[str, ...]

def build_evidence(record: DecisionRecord) -> EvidenceBundle:
    selected = next((candidate for candidate in record.candidates if candidate.action == record.selected_action), None)
    evidence = [f"scenario={record.scenario_id}", f"solver_version={record.solver_version}"]
    evidence.extend(f"{key}={value}" for key, value in record.objective_metrics.items())
    if selected: evidence.append(f"selected_objective={selected.objective}")
    alternatives = tuple(f"{candidate.action}: {'feasible' if candidate.feasible else 'rejected'}" + (f" ({candidate.rejection_reason})" if candidate.rejection_reason else '') for candidate in record.candidates if candidate.action != record.selected_action)
    uncertainty = tuple(f"{key}={value}" for key, value in (record.prediction_bundle.uncertainty.items() if record.prediction_bundle else []))
    return EvidenceBundle(record.decision_id, record.selected_action, tuple(evidence), alternatives, uncertainty)

def explain_record(record: DecisionRecord) -> dict[str, object]:
    bundle = build_evidence(record)
    return {'decision': bundle.decision, 'evidence': bundle.evidence, 'alternatives': bundle.alternatives, 'uncertainty': bundle.uncertainty, 'grounded': True, 'decision_id': bundle.decision_id}

def explain_result(result):
    return {'strategy': result.strategy, 'summary': f'Served {result.served_orders} orders and left {result.unserved_orders} unserved.', 'total_cost': result.total_cost, 'routes': [{'vehicle_id': r.vehicle_id, 'order_ids': r.order_ids, 'distance_km': r.distance_km, 'feasible': r.feasible} for r in result.routes]}
