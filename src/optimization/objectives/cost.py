"""Objective decomposition for routing decisions."""
def total_cost(distance, lateness=0.0, fuel=0.0, unserved=0.0, vehicle_usage=0.0, weights=None):
    w = weights or {'distance': 1.0, 'lateness': 5.0, 'fuel': 1.5, 'unserved': 20.0, 'vehicle_usage': 2.0}
    return w['distance']*distance + w['lateness']*lateness + w['fuel']*fuel + w['unserved']*unserved + w['vehicle_usage']*vehicle_usage
