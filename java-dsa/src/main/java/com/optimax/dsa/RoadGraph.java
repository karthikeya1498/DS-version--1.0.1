package com.optimax.dsa;

/**
 * Author: Karthikeya
 */

import java.util.*;

/**
 * Directed weighted road graph used by the Java DSA benchmark layer.
 *
 * @author Karthikeya
 */
public final class RoadGraph {
    /** Immutable edge record; weights represent travel cost or minutes. */
    public record Edge(String to, double weight) {}
    private final Map<String, List<Edge>> adjacency = new HashMap<>();

    /** Add a node if it is not already present. */
    public void addNode(String node) { adjacency.computeIfAbsent(node, ignored -> new ArrayList<>()); }

    /** Add a directed edge and preserve insertion order for deterministic runs. */
    public void addEdge(String from, String to, double weight) {
        if (weight < 0) throw new IllegalArgumentException("Dijkstra requires non-negative weights");
        addNode(from); addNode(to); adjacency.get(from).add(new Edge(to, weight));
    }

    /** Return a read-only adjacency view so callers cannot mutate benchmark state. */
    public List<Edge> neighbors(String node) { return Collections.unmodifiableList(adjacency.getOrDefault(node, List.of())); }
    public Set<String> nodes() { return Collections.unmodifiableSet(adjacency.keySet()); }
}
