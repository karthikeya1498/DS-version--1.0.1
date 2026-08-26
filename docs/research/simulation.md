# Step 2: Reproducible Logistics Simulator

The simulator is a deterministic discrete-event model for controlled logistics experiments. A `SimulationConfig` defines the seed, time horizon, fleet size, zone count, demand rate, and traffic update interval. `ScenarioGenerator` derives independent random streams for demand, traffic, and fleet generation so that changes in one subsystem do not silently reorder randomness in the others.

The core entities are `Location`, `TimeWindow`, `Order`, `Vehicle`, `TrafficState`, `SimulationEvent`, `SimulationMetrics`, and `SimulationResult`. Domain invariants reject invalid coordinates, naive timestamps, non-positive capacity or demand, and malformed time windows before simulation begins.

The first dispatch policy is intentionally simple and transparent: each newly created order is assigned to the available vehicle with the lowest current load that has enough capacity. Travel distance is calculated from the abstract coordinate system, and delivery time is derived deterministically from that distance. This baseline is not intended to compete with the future optimizer; it provides a reproducible control policy for later experiments.

The event engine uses a stable priority queue ordered by event timestamp and insertion sequence. Order creation, delivery, and traffic-update events are recorded in the result, enabling later benchmarking, replay, and explanation features. The result exposes delivered, late, and unserved counts together with distance and a baseline cost decomposition.

## Example

```python
from datetime import timedelta
from src.simulation.models import SimulationConfig
from src.simulation.simulator import LogisticsSimulator

config = SimulationConfig(seed=42, duration=timedelta(hours=2))
result = LogisticsSimulator(config).run()
print(result.to_summary())
```

The reproducibility contract is that two runs with equal configurations produce equal summaries, order statuses, traffic history, and event sequences. Future optimization and reinforcement-learning components should consume this simulator rather than introduce separate uncontrolled random behavior.
"} gestalt?} ]} UNKNOWN?} 
