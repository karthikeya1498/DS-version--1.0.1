"""Deterministic ranking of feasible decision candidates."""
from __future__ import annotations

from src.decision.contracts import CandidateEvidence


def rank_candidates(candidates: list[CandidateEvidence]) -> list[CandidateEvidence]:
    return sorted(candidates, key=lambda candidate: (not candidate.feasible, candidate.objective, candidate.candidate_id))

def select_candidate(candidates: list[CandidateEvidence]) -> CandidateEvidence | None:
    ranked = rank_candidates(candidates)
    return ranked[0] if ranked and ranked[0].feasible else None
