# Step 4: Traffic-Aware Routing

Step 4 adds dynamic traffic-aware weights without changing the graph algorithm contracts. `TrafficAwareGraph` captures immutable base weights and applies a `TrafficState` multiplier to each edge according to its target node zone. Calling `reset()` restores the original weights, which allows repeated scenario experiments on the same graph.

`GraphDispatchRouter` evaluates every vehicle that satisfies availability and capacity constraints, computes a Dijkstra or A* route from the vehicle’s current location to the order destination, and selects the lowest-cost feasible route with vehicle ID as a deterministic tie-breaker. The returned `DispatchRoute` records the vehicle, order, path, travel cost, and algorithm used.

This layer is intentionally a routing baseline rather than a full VRP solver. It provides the interface needed by later assignment, local-search, and metaheuristic components.
