package com.optimax.dsa;

/**
 * Author: Karthikeya
 */

import java.util.Map;

/**
 * Small deterministic benchmark used by CI and interview demonstrations.
 * It reports cost parity before comparing performance, avoiding unsupported
 * claims about which algorithm is universally faster.
 *
 * @author Karthikeya
 */
public final class Benchmark {
    private Benchmark() {}

    /** Build a line graph and print comparable shortest-path diagnostics. */
    public static void main(String[] args) {
        RoadGraph graph = new RoadGraph();
        for (int index = 0; index < 100; index++) graph.addEdge("n" + index, "n" + (index + 1), 1.0);
        var dijkstra = ShortestPaths.dijkstra(graph, "n0", "n100");
        var astar = ShortestPaths.aStar(graph, "n0", "n100", Map.of());
        System.out.printf("dijkstra_cost=%.3f astar_cost=%.3f dijkstra_visited=%d astar_visited=%d%n", dijkstra.cost(), astar.cost(), dijkstra.visited(), astar.visited());
    }
}
