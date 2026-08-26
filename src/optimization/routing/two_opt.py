"""2-opt route improvement for symmetric route costs."""
def improve(route, cost):
    best = list(route); best_cost = cost(best); changed = True
    while changed:
        changed = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best)):
                candidate = best[:i] + best[i:j][::-1] + best[j:]
                value = cost(candidate)
                if value < best_cost:
                    best, best_cost, changed = candidate, value, True
                    break
            if changed: break
    return best, best_cost
