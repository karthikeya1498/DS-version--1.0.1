# Step 3: Road Network and Graph Algorithms

Step 3 introduces a weighted adjacency-list road graph. `Node` stores a stable identifier and optional geographic coordinates. `Edge` stores a directed non-negative travel cost. `RoadGraph.add_edge(..., bidirectional=True)` creates the paired reverse edge used for ordinary two-way roads.

`PriorityQueue` is a stable minimum queue. A monotonically increasing insertion sequence makes equal-priority items deterministic, which is important for reproducible experiments and benchmark comparisons.

`dijkstra.shortest_path` computes the lowest-cost route for non-negative edge weights and returns a `PathResult` containing the node sequence, total cost, and number of expanded nodes. `astar.shortest_path` uses the coordinate-based Euclidean heuristic while returning the same result contract. Both algorithms return `None` when the goal is unreachable and raise `KeyError` for unknown nodes.

The graph layer deliberately remains independent of the simulator. Later steps can construct graph nodes from simulation locations and update edge weights from traffic states without coupling shortest-path code to order or vehicle state.
