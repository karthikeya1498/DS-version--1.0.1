"""Tests for advanced DSA integration bridges in logistics operations."""

from src.dsa.dsa_integration import (
    CapacityKnapsackSelector,
    CumulativeDemandMonitor,
    NetworkConnectivityEngine,
    TrafficSpeedRangeQuery,
)
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node


def test_segment_tree_traffic_range_query():
    # 24 hourly speed readings along an expressway
    hourly_speeds = [
        60.0,
        65.0,
        70.0,
        55.0,
        40.0,
        30.0,
        25.0,
        20.0,
        35.0,
        50.0,
        55.0,
        60.0,
        58.0,
        55.0,
        50.0,
        45.0,
        30.0,
        22.0,
        25.0,
        38.0,
        48.0,
        55.0,
        60.0,
        62.0,
    ]

    speed_query = TrafficSpeedRangeQuery(hourly_speeds, aggregation="min")

    # Morning rush hour query (hours 6 to 9) -> minimum speed should be 20.0
    assert speed_query.query_interval(6, 9) == 20.0

    # Update traffic incident at hour 2
    speed_query.update_speed(2, 15.0)
    assert speed_query.query_interval(0, 3) == 15.0


def test_fenwick_tree_cumulative_demand_monitor():
    # Monitor 10 time intervals
    demand_monitor = CumulativeDemandMonitor(size=10)

    # Add order arrivals
    demand_monitor.record_order_demand(0, 5.0)
    demand_monitor.record_order_demand(1, 10.0)
    demand_monitor.record_order_demand(2, 8.0)
    demand_monitor.record_order_demand(3, 12.0)

    # Prefix cumulative demand
    assert demand_monitor.cumulative_demand(1) == 15.0
    assert demand_monitor.cumulative_demand(3) == 35.0

    # Range demand [1, 3] = 10 + 8 + 12 = 30
    assert demand_monitor.range_demand(1, 3) == 30.0


def test_union_find_network_connectivity():
    g = RoadGraph()
    # Island 1: A <-> B <-> C
    g.add_node(Node("A", 0, 0))
    g.add_node(Node("B", 0, 1))
    g.add_node(Node("C", 0, 2))
    g.add_edge(Edge("A", "B", 1.0), bidirectional=True)
    g.add_edge(Edge("B", "C", 1.0), bidirectional=True)

    # Island 2: X <-> Y
    g.add_node(Node("X", 10, 10))
    g.add_node(Node("Y", 10, 11))
    g.add_edge(Edge("X", "Y", 1.0), bidirectional=True)

    connectivity = NetworkConnectivityEngine(g)
    assert connectivity.are_connected("A", "C") is True
    assert connectivity.are_connected("A", "X") is False
    assert connectivity.connected_component_count() == 2


def test_capacity_knapsack_order_selection():
    # (order_id, weight_units, priority_value)
    orders = [
        ("ord_1", 2, 50.0),
        ("ord_2", 3, 70.0),
        ("ord_3", 5, 120.0),
        ("ord_4", 4, 80.0),
    ]
    # Vehicle capacity = 7 units
    selected_ids, total_val = CapacityKnapsackSelector.select_orders(orders, capacity=7)

    # Optimal choice: ord_1 (wt 2, val 50) + ord_3 (wt 5, val 120) = wt 7, val 170
    assert total_val == 170.0
    assert set(selected_ids) == {"ord_1", "ord_3"}
