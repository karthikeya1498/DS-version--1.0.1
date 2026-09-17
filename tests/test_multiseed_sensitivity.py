"""Tests for the Phase 7 multi-seed sensitivity design.

Author: Karthikeya
"""
from __future__ import annotations

import numpy as np
import pytest

from scripts.run_multiseed_decision_sensitivity import (
    CAPACITIES,
    ROUTE_PROFILES,
    SEEDS,
    TREATMENTS,
    build_graph,
    treated_predictions,
)


def test_sensitivity_design_has_paired_factors():
    assert len(SEEDS) == 5
    assert CAPACITIES == (5, 10, 20)
    assert ROUTE_PROFILES == ("balanced", "north_bias", "south_bias")
    assert TREATMENTS == ("clean", "noise_10pct", "priority_targeted")
    assert len(SEEDS) * 3 * 3 * 3 * 3 == 405


def test_route_profiles_change_edge_costs_without_changing_topology():
    balanced = build_graph("balanced")
    north = build_graph("north_bias")
    south = build_graph("south_bias")
    assert set(balanced.nodes) == set(north.nodes) == set(south.nodes)
    assert balanced.adjacency["0"][0].weight != north.adjacency["0"][0].weight
    assert north.adjacency["6"][0].weight != south.adjacency["6"][0].weight
    with pytest.raises(ValueError, match="unsupported"):
        build_graph("unknown")


def test_noise_treatments_are_seeded_and_priority_targeted():
    predictions = np.array([10.0, 20.0, 30.0])
    actual = np.array([10.0, 20.0, 30.0])
    first = treated_predictions(predictions, actual, "noise_10pct", 42)
    second = treated_predictions(predictions, actual, "noise_10pct", 42)
    targeted = treated_predictions(predictions, actual, "priority_targeted", 42)
    assert np.array_equal(first, second)
    assert targeted[0] == 12.0
    assert np.array_equal(targeted[1:], predictions[1:])
