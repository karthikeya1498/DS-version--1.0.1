package com.optimax.dsa;

import java.util.*;

/**
 * Interview-oriented data structures used by optimization benchmarks.
 *
 * @author Karthikeya
 */
public final class OptimizationStructures {
    private OptimizationStructures() {}

    /** Binary min-heap wrapper with O(log n) insertion and removal. */
    public static final class MinHeap<T> {
        private final PriorityQueue<T> queue;
        public MinHeap(Comparator<T> comparator) { queue = new PriorityQueue<>(comparator); }
        public void offer(T value) { queue.offer(value); }
        public T poll() { return queue.poll(); }
        public boolean isEmpty() { return queue.isEmpty(); }
    }

    /** Disjoint-set union with path compression and union by rank. */
    public static final class UnionFind {
        private final int[] parent; private final byte[] rank;
        public UnionFind(int size) { parent = new int[size]; rank = new byte[size]; for (int i = 0; i < size; i++) parent[i] = i; }
        public int find(int value) { if (parent[value] != value) parent[value] = find(parent[value]); return parent[value]; }
        public void union(int left, int right) { int a = find(left), b = find(right); if (a == b) return; if (rank[a] < rank[b]) parent[a] = b; else { parent[b] = a; if (rank[a] == rank[b]) rank[a]++; } }
        public boolean connected(int left, int right) { return find(left) == find(right); }
    }

    /** 0/1 knapsack; returns the maximum value under an integer capacity. */
    public static int knapsack(int[] weights, int[] values, int capacity) {
        if (weights.length != values.length || capacity < 0) throw new IllegalArgumentException("invalid knapsack inputs");
        int[] best = new int[capacity + 1];
        for (int item = 0; item < weights.length; item++) for (int remaining = capacity; remaining >= weights[item]; remaining--) best[remaining] = Math.max(best[remaining], best[remaining - weights[item]] + values[item]);
        return best[capacity];
    }
}
