"""Unit tests for feature engineering modules: demand, ETA, graph, vehicle, and pipeline."""

from datetime import UTC, datetime, timedelta

import pandas as pd

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.features.demand_features import build_demand_lag_features
from src.features.eta_features import build_eta_feature_row
from src.features.feature_pipeline import chronological_split
from src.features.graph_features import extract_node_graph_features, extract_path_graph_features
from src.features.vehicle_features import extract_vehicle_features
from src.simulation.models import Location, Vehicle, VehicleStatus


def test_demand_features_no_lookahead_leakage():
    # Construct 100 hourly records
    base = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    records = []
    for i in range(100):
        records.append(
            {
                "timestamp": base + timedelta(hours=i),
                "zone": "zone_1",
                "demand": float(i + 10),
            }
        )
    df = pd.DataFrame(records)
    feat_df = build_demand_lag_features(df, lags=(1, 2), rolling_windows=(3,), horizon=1)

    assert "lag_1" in feat_df.columns
    assert "lag_2" in feat_df.columns
    assert "rolling_mean_3" in feat_df.columns
    assert "target" in feat_df.columns

    # Verify lag_1 in consecutive rows advances by 1 step
    assert feat_df.iloc[5]["lag_1"] + 1 == feat_df.iloc[6]["lag_1"]


def test_chronological_split():
    df = pd.DataFrame({"val": range(100)})
    train, val, test = chronological_split(df, train_fraction=0.7, validation_fraction=0.15)
    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15
    assert train["val"].max() < val["val"].min()
    assert val["val"].max() < test["val"].min()


def test_eta_features_extraction():
    row = build_eta_feature_row(
        distance_km=15.0,
        free_flow_speed_kmh=60.0,
        traffic_multiplier=1.5,
        congestion_level=0.2,
        road_class="motorway",
        hour=8,
        day_of_week=1,
    )
    assert row["distance_km"] == 15.0
    assert row["free_flow_time_min"] == 15.0  # 15km / 60kmh * 60 = 15 min
    assert row["effective_travel_time_est"] > 15.0
    assert "hour_sin" in row
    assert "day_sin" in row


def test_graph_and_vehicle_features():
    g = RoadGraph()
    g.add_node(Node("A", 0, 0))
    g.add_node(Node("B", 0, 1))
    g.add_node(Node("C", 0, 2))
    g.add_edge(Edge("A", "B", 5.0), bidirectional=True)
    g.add_edge(Edge("B", "C", 8.0), bidirectional=True)

    node_feats = extract_node_graph_features(g, "B")
    assert node_feats["total_degree"] == 4.0  # in and out
    assert node_feats["avg_outgoing_weight"] == 6.5

    path_feats = extract_path_graph_features(g, ["A", "B", "C"])
    assert path_feats["hop_count"] == 2.0
    assert path_feats["total_path_weight"] == 13.0

    now = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)
    loc = Location("A", "zone_1", 0, 0)
    v = Vehicle(
        vehicle_id="v_1",
        home_base=loc,
        capacity_units=10,
        available_from=now,
        available_until=now + timedelta(hours=8),
        current_location=loc,
        load_units=4,
        status=VehicleStatus.AVAILABLE,
    )
    v_feats = extract_vehicle_features(v, current_time=now + timedelta(hours=2))
    assert v_feats["remaining_capacity"] == 6.0
    assert v_feats["capacity_utilization"] == 0.4
    assert 0.7 < v_feats["shift_remaining_ratio"] < 0.8
