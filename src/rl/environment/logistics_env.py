"""Small Gym-like logistics environment without a hard Gym dependency."""
class LogisticsEnv:
    def __init__(self, demand=5): self.demand = demand; self.reset()
    def reset(self, seed=None): self.remaining = self.demand; self.time = 0; return self.state()
    def state(self): return (self.remaining, self.time)
    def step(self, action):
        served = min(max(0, int(action)), self.remaining); self.remaining -= served; self.time += 1
        reward = float(served) - (2.0 if served == 0 and self.remaining else 0.0)
        return self.state(), reward, self.remaining == 0 or self.time >= 10, {'served': served}
