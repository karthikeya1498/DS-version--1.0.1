"""Road-network node model."""
from dataclasses import dataclass
@dataclass(frozen=True, slots=True)
class Node:
    node_id: str
    latitude: float = 0.0
    longitude: float = 0.0
    def __post_init__(self):
        if not self.node_id.strip(): raise ValueError('node_id must be non-empty')
        if not -90 <= self.latitude <= 90: raise ValueError('invalid latitude')
        if not -180 <= self.longitude <= 180: raise ValueError('invalid longitude')
