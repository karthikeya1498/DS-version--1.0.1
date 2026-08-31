"""Application service for route decisions."""


class DecisionEngine:
    def __init__(self, solver):
        self.solver = solver

    def decide(self, orders, vehicles):
        return self.solver.solve(orders, vehicles)
