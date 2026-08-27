package com.optimax.dsa;

/**
 * Author: Karthikeya
 */

import static org.junit.jupiter.api.Assertions.*;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** Regression tests for the explicit Java DSA layer. @author Karthikeya */
class OptimizationStructuresTest {
    @Test void dijkstraAndAStarAgreeOnCost() {
        RoadGraph graph = new RoadGraph(); graph.addEdge("A", "B", 2); graph.addEdge("B", "C", 3); graph.addEdge("A", "C", 10);
        var dijkstra = ShortestPaths.dijkstra(graph, "A", "C"); var astar = ShortestPaths.aStar(graph, "A", "C", Map.of("A", 0.0, "B", 1.0, "C", 0.0));
        assertEquals(5.0, dijkstra.cost()); assertEquals(dijkstra.cost(), astar.cost()); assertEquals(dijkstra.nodes(), astar.nodes());
    }

    @Test void structuresPreserveTheirInvariants() {
        var heap = new OptimizationStructures.MinHeap<Integer>(Integer::compareTo); heap.offer(4); heap.offer(1); assertEquals(1, heap.poll());
        var unionFind = new OptimizationStructures.UnionFind(4); unionFind.union(0, 1); unionFind.union(1, 2); assertTrue(unionFind.connected(0, 2)); assertFalse(unionFind.connected(0, 3));
        assertEquals(7, OptimizationStructures.knapsack(new int[]{2, 3, 4}, new int[]{3, 4, 5}, 5));
    }
}
