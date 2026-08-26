"""Persistence-neutral record definitions."""
from dataclasses import dataclass
from datetime import datetime
@dataclass(frozen=True)
class ExperimentRecord:
    experiment_id: str
    strategy: str
    seed: int
    created_at: datetime
    metrics: dict[str, float]
