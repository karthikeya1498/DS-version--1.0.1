package com.optimax.dsa;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;
import org.junit.jupiter.api.Test;

/** Author: Karthikeya. Cross-checks Java routing against the canonical graph contract. */
class ShortestPathsTest {
    @Test
    void dijkstraAndAdmissibleAStarHaveEqualCost() {
        RoadGraph graph = new RoadGraph();
        graph.addEdge("a", "b", 1.0);
        graph.addEdge("b", "c", 2.0);
        graph.addEdge("a", "c", 5.0);
        var dijkstra = ShortestPaths.dijkstra(graph, "a", "c");
        var aStar = ShortestPaths.aStar(graph, "a", "c", Map.of("a", 3.0, "b", 2.0, "c", 0.0));
        assertNotNull(dijkstra);
        assertNotNull(aStar);
        assertEquals(dijkstra.cost(), aStar.cost(), 1e-9);
        assertEquals(java.util.List.of("a", "b", "c"), aStar.nodes());
    }

    @Test
    void negativeEdgesAreRejectedBeforeSearch() {
        RoadGraph graph = new RoadGraph();
        assertThrows(IllegalArgumentException.class, () -> graph.addEdge("a", "b", -1.0));
    }
}
