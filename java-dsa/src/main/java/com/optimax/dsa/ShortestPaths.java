package com.optimax.dsa;

/**
 * Author: Karthikeya
 */

import java.util.*;

/**
 * Reference shortest-path algorithms for comparable routing experiments.
 *
 * @author Karthikeya
 */
public final class ShortestPaths {
    private ShortestPaths() {}
    public record Path(List<String> nodes, double cost, int visited) {}
    private record Entry(String node, double priority) {}

    /** Dijkstra gives the non-negative-weight optimum in O((V+E) log V). */
    public static Path dijkstra(RoadGraph graph, String start, String goal) {
        return search(graph, start, goal, node -> 0.0);
    }

    /** A* remains optimal when the supplied heuristic is admissible and consistent. */
    public static Path aStar(RoadGraph graph, String start, String goal, Map<String, Double> heuristic) {
        return search(graph, start, goal, node -> heuristic.getOrDefault(node, 0.0));
    }

    private static Path search(RoadGraph graph, String start, String goal, java.util.function.ToDoubleFunction<String> heuristic) {
        Map<String, Double> distance = new HashMap<>(); Map<String, String> previous = new HashMap<>();
        PriorityQueue<Entry> queue = new PriorityQueue<>(Comparator.comparingDouble(Entry::priority));
        distance.put(start, 0.0); queue.add(new Entry(start, heuristic.applyAsDouble(start))); int visited = 0;
        while (!queue.isEmpty()) {
            Entry current = queue.poll(); double known = distance.getOrDefault(current.node(), Double.POSITIVE_INFINITY);
            if (current.priority() - heuristic.applyAsDouble(current.node()) > known + 1e-12) continue;
            visited++; if (current.node().equals(goal)) return reconstruct(previous, distance.get(goal), start, goal, visited);
            for (RoadGraph.Edge edge : graph.neighbors(current.node())) {
                double candidate = known + edge.weight();
                if (candidate < distance.getOrDefault(edge.to(), Double.POSITIVE_INFINITY)) {
                    distance.put(edge.to(), candidate); previous.put(edge.to(), current.node());
                    queue.add(new Entry(edge.to(), candidate + heuristic.applyAsDouble(edge.to())));
                }
            }
        }
        return null;
    }

    private static Path reconstruct(Map<String, String> previous, double cost, String start, String goal, int visited) {
        LinkedList<String> path = new LinkedList<>(); for (String node = goal; node != null; node = previous.get(node)) path.addFirst(node);
        if (!path.getFirst().equals(start)) return null; return new Path(List.copyOf(path), cost, visited);
    }
}
