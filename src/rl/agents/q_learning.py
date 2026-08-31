"""Tabular Q-learning baseline."""


class QLearningAgent:
    def __init__(self, actions=(0, 1), alpha=0.1, gamma=0.95):
        self.actions = tuple(actions)
        self.alpha = alpha
        self.gamma = gamma
        self.q = {}

    def value(self, state, action):
        return self.q.get((state, action), 0.0)

    def best_action(self, state):
        return max(self.actions, key=lambda a: (self.value(state, a), -a))

    def update(self, state, action, reward, next_state):
        target = reward + self.gamma * max(self.value(next_state, a) for a in self.actions)
        self.q[(state, action)] = self.value(state, action) + self.alpha * (
            target - self.value(state, action)
        )
