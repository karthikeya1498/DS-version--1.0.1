# OPTIMA-X Java DSA module

**Author: Karthikeya**

This module makes the interview-oriented data structures explicit in Java, as required by the OPTIMA-X architecture. It contains a weighted road graph, Dijkstra and A* shortest paths, a binary min-heap wrapper, union-find with path compression and union by rank, and 0/1 knapsack dynamic programming.

Python remains the primary language for data engineering, ML, simulation, optimization orchestration, RL, LLM tooling, and APIs. The Java module is deliberately isolated behind value-oriented records and deterministic command-line/benchmark contracts. It can be invoked independently by Maven and can later exchange graph or benchmark records through JSON without coupling Java classes to Python internals.

Run the tests with:

```bash
mvn -B -f java-dsa/pom.xml test
```

Run the benchmark after compilation with:

```bash
mvn -B -f java-dsa/pom.xml package
java -cp java-dsa/target/classes com.optimax.dsa.Benchmark
```

The benchmark reports shortest-path cost parity and visited-node counts. It does not claim that one algorithm is universally faster.
