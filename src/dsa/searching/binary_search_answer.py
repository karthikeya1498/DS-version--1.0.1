"""Binary search for the minimum integer satisfying a monotonic predicate."""


def minimum_feasible(low: int, high: int, feasible):
    if low > high:
        raise ValueError("low must not exceed high")
    answer = None
    while low <= high:
        middle = (low + high) // 2
        if feasible(middle):
            answer = middle
            high = middle - 1
        else:
            low = middle + 1
    return answer
