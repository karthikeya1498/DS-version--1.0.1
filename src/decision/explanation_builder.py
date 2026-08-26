"""Traceable explanations generated only from structured optimization results."""


def explain_result(result):
    return {
        "strategy": result.strategy,
        "summary": f"Served {result.served_orders} orders and left {result.unserved_orders} unserved.",
        "total_cost": result.total_cost,
        "routes": [
            {
                "vehicle_id": r.vehicle_id,
                "order_ids": r.order_ids,
                "distance_km": r.distance_km,
                "feasible": r.feasible,
            }
            for r in result.routes
        ],
    }
