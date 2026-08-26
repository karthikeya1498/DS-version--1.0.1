"""Bounded 3-opt route improvement using deterministic segment reversals."""
def improve(route, cost):
    best, best_cost = list(route), cost(route)
    n = len(best)
    for i in range(1, n - 3):
        for j in range(i + 1, n - 2):
            for k in range(j + 1, n):
                candidates = [best[:i] + best[i:j][::-1] + best[j:k] + best[k:], best[:i] + best[i:j] + best[j:k][::-1] + best[k:], best[:i] + best[i:j][::-1] + best[j:k][::-1] + best[k:]]
                for candidate in candidates:
                    value = cost(candidate)
                    if value < best_cost: best, best_cost = candidate, value
    return best, best_cost
