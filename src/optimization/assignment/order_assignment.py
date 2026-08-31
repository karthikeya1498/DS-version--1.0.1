"""Capacity-aware multi-order clustering and bundle formation."""
from __future__ import annotations

from typing import Sequence

from src.dsa.dynamic_programming.knapsack import knapsack
from src.simulation.models import Order, Vehicle


def cluster_orders_by_capacity(
    orders: Sequence[Order],
    vehicles: Sequence[Vehicle],
) -> tuple[dict[str, list[Order]], list[Order]]:
    """
    Assign multiple orders to vehicle bundles respecting each vehicle's capacity.
    Orders are sorted by priority and urgency (deadline end), then assigned
    to vehicles using capacity-constrained bin-packing.
    
    Returns:
        (assigned_bundles_by_vehicle_id, unassigned_orders)
    """
    if not orders or not vehicles:
        return {}, list(orders)

    # Sort orders by priority (high to low) and deadline (urgent first)
    sorted_orders = sorted(
        orders,
        key=lambda o: (-o.priority, o.time_window.end.timestamp(), o.created_at.timestamp()),
    )

    available_vehicles = [v for v in vehicles if v.capacity_units > 0]
    bundles: dict[str, list[Order]] = {v.vehicle_id: [] for v in available_vehicles}
    vehicle_capacities = {v.vehicle_id: v.capacity_units for v in available_vehicles}
    vehicle_loads = {v.vehicle_id: 0 for v in available_vehicles}

    unassigned: list[Order] = []

    for order in sorted_orders:
        assigned = False
        # Find best feasible vehicle with enough remaining capacity
        # Preference: vehicle with matching zone/closest location or highest available capacity
        candidate_vehicles = [
            v for v in available_vehicles
            if vehicle_loads[v.vehicle_id] + order.demand_units <= vehicle_capacities[v.vehicle_id]
        ]

        if candidate_vehicles:
            # Sort candidate vehicles to pack efficiently (first-fit / best-fit)
            # Prefer vehicle that already has orders in the same zone, or has lowest spare capacity (best fit)
            best_vehicle = min(
                candidate_vehicles,
                key=lambda v: (
                    0 if bundles[v.vehicle_id] and bundles[v.vehicle_id][-1].destination.zone_id == order.destination.zone_id else 1,
                    vehicle_capacities[v.vehicle_id] - vehicle_loads[v.vehicle_id],
                ),
            )
            bundles[best_vehicle.vehicle_id].append(order)
            vehicle_loads[best_vehicle.vehicle_id] += order.demand_units
            assigned = True

        if not assigned:
            unassigned.append(order)

    # Filter out vehicles with no assigned orders
    active_bundles = {v_id: ords for v_id, ords in bundles.items() if len(ords) > 0}
    return active_bundles, unassigned
