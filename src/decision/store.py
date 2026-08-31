"""Persistence-neutral decision trace store for local and test deployments."""

from __future__ import annotations

from src.decision.contracts import DecisionRecord


class DecisionStore:
    def __init__(self) -> None:
        self._records: dict[str, DecisionRecord] = {}

    def save(self, record: DecisionRecord) -> DecisionRecord:
        self._records[record.decision_id] = record
        return record

    def get(self, decision_id: str) -> DecisionRecord | None:
        return self._records.get(decision_id)

    def list(self) -> list[DecisionRecord]:
        return list(self._records.values())


store = DecisionStore()
