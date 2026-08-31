"""Select an optimization strategy by name."""


def select_solver(name, **kwargs):
    if name in {"hybrid", "graph_dispatch"}:
        from src.optimization.solver.hybrid_solver import HybridSolver

        return HybridSolver(**kwargs)
    raise ValueError(f"unknown solver: {name}")
