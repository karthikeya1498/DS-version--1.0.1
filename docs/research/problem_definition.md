# OPTIMA-X Phase 1: Problem Definition

## Purpose

OPTIMA-X studies **dynamic urban delivery and resource allocation**. The system receives a road network, orders, vehicles, traffic conditions, weather context, and historical demand, then produces operational decisions that assign orders to vehicles and select feasible routes.

The Phase 1 objective is not to claim an optimal production system. It is to build a deterministic and auditable logistics world in which later forecasting, optimization, and reinforcement-learning methods can be compared under the same scenarios.

## Decision maker and controllable actions

The OPTIMA-X engine is the decision maker. At each decision time it may choose vehicle assignment, route selection, order priority, and resource activation. Phase 1 implements transparent baseline policies and records enough state to reproduce their outcomes.

| Category | Phase 1 representation |
|---|---|
| Observations | Orders, traffic, weather context, vehicle state, road graph, historical demand |
| Decisions | Vehicle assignment, route, order priority, activation of available vehicles |
| Operational outcomes | Travel distance, travel time, late deliveries, unserved orders, utilization, cost |
| Hard constraints | Vehicle capacity, time windows, vehicle availability, route existence, shift limits |

## Mathematical formulation

Let the road network be a directed weighted graph:

$$G=(V,E)$$

where $V$ is the set of road-network nodes and $E$ is the set of road segments. Each edge $(u,v) \in E$ stores distance, base travel time, dynamic travel time, and operational cost.

Let $K=\{1,\ldots,m\}$ be the fleet and $O=\{1,\ldots,n\}$ be the set of orders. Each order $i$ has origin $p_i$, destination $d_i$, demand $q_i$, creation time $c_i$, and delivery window $[a_i,b_i]$. Each vehicle $k$ has capacity $Q_k$, current node $s_k$, availability interval, and current load $l_k$.

The binary assignment variable is:

$$x_{ik}=\begin{cases}1 & \text{if order }i\text{ is assigned to vehicle }k\\0 & \text{otherwise.}\end{cases}$$

A route $r_k$ is a sequence of graph nodes beginning at the vehicle's current node and containing the destinations of its assigned orders. A route is feasible only when every consecutive pair has a graph path, cumulative assigned demand does not exceed capacity, and delivery times respect vehicle availability and order windows.

The Phase 1 scalar objective is:

$$J=\alpha C_{distance}+\beta C_{fuel}+\gamma C_{late}+\delta C_{unserved}+\epsilon C_{activation}$$

where distance and fuel costs are operational costs, late cost penalizes missed delivery windows, unserved cost penalizes orders without a feasible assignment, and activation cost penalizes bringing additional vehicles into service. The coefficients are configuration values, not hard-coded claims about a particular carrier.

The assignment constraints include:

$$\sum_{k\in K}x_{ik}\leq 1 \quad \forall i\in O$$

$$\sum_{i\in O}q_i x_{ik}\leq Q_k \quad \forall k\in K$$

$$x_{ik}=0 \quad \text{when vehicle }k\text{ is unavailable or no feasible route exists.}$$

## Research questions

Phase 1 establishes the following questions for later experiments:

1. Can the same seeded scenario be replayed with identical orders, traffic, routes, and outcomes?
2. How do Dijkstra and A* compare on the same road graph under runtime, explored nodes, and path cost?
3. How does traffic variation alter route selection and downstream delivery outcomes?
4. How do vehicle shortages, demand peaks, and distribution shifts affect service level and total cost?
5. Can the simulation expose a stable baseline against which prediction-aware and optimization-aware decisions can be evaluated?

## Phase boundaries

Phase 1 deliberately excludes neural forecasting, reinforcement learning, LLM explanations, and production-grade autonomous dispatch. It includes data contracts, validation, graph construction, deterministic simulation, baseline algorithms, PostgreSQL-ready persistence boundaries, and reproducible acceptance tests.

## Reproducibility contract

Every scenario must carry a seed, scenario identifier, configuration snapshot, and source-data manifest. Randomness must be derived from named deterministic streams so that changing traffic generation does not silently change fleet or demand generation. A complete run must be serializable to JSON or tabular artifacts and must report whether data validation, graph construction, and simulation completed successfully.
