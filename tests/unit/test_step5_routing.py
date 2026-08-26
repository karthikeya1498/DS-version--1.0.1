import itertools

from src.dsa.trees.fenwick_tree import FenwickTree
from src.dsa.trees.segment_tree import SegmentTree
from src.optimization.routing.three_opt import improve as three_opt
from src.optimization.routing.two_opt import improve as two_opt


def test_fenwick_and_segment_tree():
    tree = FenwickTree(4)
    [tree.add(i, i + 1) for i in range(4)]
    assert tree.range_sum(1, 4) == 9
    segment = SegmentTree([1, 5, 2, 3])
    assert segment.query_max(1, 3) == 5
    segment.update(2, 8)
    assert segment.query_max(1, 3) == 8


def test_two_and_three_opt_never_worsen_route():
    matrix = {
        ("a", "b"): 5,
        ("b", "c"): 5,
        ("c", "d"): 5,
        ("a", "c"): 1,
        ("c", "b"): 1,
        ("b", "d"): 1,
    }

    def cost(route):
        return sum(matrix.get((a, b), matrix.get((b, a), 10)) for a, b in itertools.pairwise(route))

    route = ["a", "b", "c", "d"]
    assert two_opt(route, cost)[1] <= cost(route)
    assert three_opt(route, cost)[1] <= cost(route)
