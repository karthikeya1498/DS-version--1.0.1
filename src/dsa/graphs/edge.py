"""Directed weighted road-network edge model."""
from dataclasses import dataclass
@dataclass(frozen=True, slots=True)
class Edge:
    source: str
    target: str
    weight: float
    def __post_init__(self):
        if not self.source.strip() or not self.target.strip(): raise ValueError('edge endpoints must be non-empty')
        if self.weight < 0: raise ValueError('edge weight must be non-negative')
