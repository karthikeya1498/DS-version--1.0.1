"""Pure counterfactual transformations that never mutate the baseline state."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioModification:
    demand_multiplier: float = 1.0
    traffic_multiplier: float = 1.0
    unavailable_vehicle_ids: tuple[str, ...] = ()
    lateness_weight: float | None = None

def apply_modification(state: dict, modification: ScenarioModification) -> dict:
    if modification.demand_multiplier < 0 or modification.traffic_multiplier < 0: raise ValueError('multipliers must be non-negative')
    result = deepcopy(state); result['isolated'] = True; result['demand_multiplier'] = modification.demand_multiplier; result['traffic_multiplier'] = modification.traffic_multiplier
    result['unavailable_vehicle_ids'] = list(modification.unavailable_vehicle_ids)
    if 'demand' in result: result['demand'] = {key: value * modification.demand_multiplier for key, value in result['demand'].items()}
    if 'traffic' in result: result['traffic'] = {key: value * modification.traffic_multiplier for key, value in result['traffic'].items()}
    return result
