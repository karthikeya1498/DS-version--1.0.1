# Step 5: Advanced DSA and Route Construction

Step 5 adds reusable data structures and routing primitives for later optimization experiments. `FenwickTree` supports point updates and prefix sums in logarithmic time. `SegmentTree` supports range-maximum queries and point updates in logarithmic time. `minimum_feasible` provides binary search on a monotonic feasibility predicate.

Route validation is centralized in `validate_route`. It checks vehicle shift availability, cumulative capacity, the presence of every required travel segment, delivery time windows, and shift completion. It returns structured violation codes instead of silently accepting an infeasible route.

The deterministic greedy constructor repeatedly chooses the feasible candidate with the lowest next-leg travel time, then priority and order identifier as tie-breakers. `two_opt` and `three_opt` are bounded local-search operators that accept a route and cost function and never return a route with a higher cost than their input.
