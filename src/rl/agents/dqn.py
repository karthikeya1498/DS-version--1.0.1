"""Deep Q-Network (DQN) agent with experience replay and target network."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from random import Random
from typing import Any, Sequence

import numpy as np


@dataclass(frozen=True)
class DQNConfig:
    learning_rate: float = 0.005
    discount: float = 0.99
    epsilon_start: float = 1.0
    epsilon_end: float = 0.05
    epsilon_decay: float = 0.98
    buffer_size: int = 2000
    batch_size: int = 32
    target_update_interval: int = 5
    hidden_dim: int = 32
    seed: int = 42


class DQNAgent:
    """
    Deep Q-Network (DQN) agent with linear/neural approximation,
    experience replay memory, and target network stabilization.
    """

    def __init__(
        self,
        observation_dim: int,
        action_count: int,
        config: DQNConfig = DQNConfig(),
    ) -> None:
        if observation_dim <= 0 or action_count <= 0:
            raise ValueError("Dimensions must be positive")
        self.observation_dim = observation_dim
        self.action_count = action_count
        self.config = config
        self.rng = Random(config.seed)
        self.np_rng = np.random.default_rng(config.seed)

        self.epsilon = config.epsilon_start
        self.memory: deque[tuple[np.ndarray, int, float, np.ndarray, bool]] = deque(
            maxlen=config.buffer_size
        )

        # Q-Network weights (input -> hidden -> actions)
        h = config.hidden_dim
        std1 = np.sqrt(2.0 / observation_dim)
        std2 = np.sqrt(2.0 / h)

        self.W1 = self.np_rng.normal(0.0, std1, (observation_dim, h))
        self.b1 = np.zeros((1, h))
        self.W2 = self.np_rng.normal(0.0, std2, (h, action_count))
        self.b2 = np.zeros((1, action_count))

        # Target network weights
        self.target_W1 = np.copy(self.W1)
        self.target_b1 = np.copy(self.b1)
        self.target_W2 = np.copy(self.W2)
        self.target_b2 = np.copy(self.b2)

        self.step_counter = 0

    def _forward(self, obs: np.ndarray, target: bool = False) -> np.ndarray:
        W1 = self.target_W1 if target else self.W1
        b1 = self.target_b1 if target else self.b1
        W2 = self.target_W2 if target else self.W2
        b2 = self.target_b2 if target else self.b2

        x = np.asarray(obs, dtype=float)
        if x.ndim == 1:
            x = x.reshape(1, -1)
        # Scale observation features
        x_norm = np.tanh(x / 10.0)
        h_act = np.maximum(0.0, x_norm @ W1 + b1)
        q_vals = h_act @ W2 + b2
        return q_vals

    def act(self, observation: np.ndarray, deterministic: bool = False) -> int:
        """Select action via epsilon-greedy policy."""
        if not deterministic and self.rng.random() < self.epsilon:
            return self.rng.randint(0, self.action_count - 1)
        q_vals = self._forward(observation, target=False)
        return int(np.argmax(q_vals[0]))

    def remember(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ) -> None:
        """Store experience transition in replay buffer."""
        self.memory.append((
            np.asarray(state, dtype=float),
            int(action),
            float(reward),
            np.asarray(next_state, dtype=float),
            bool(done),
        ))

    def train_step(self) -> float:
        """Sample mini-batch from replay buffer and perform Q-learning update."""
        if len(self.memory) < self.config.batch_size:
            return 0.0

        batch = self.rng.sample(list(self.memory), self.config.batch_size)
        states = np.array([t[0] for t in batch])
        actions = np.array([t[1] for t in batch])
        rewards = np.array([t[2] for t in batch])
        next_states = np.array([t[3] for t in batch])
        dones = np.array([t[4] for t in batch])

        # Compute Q(s, a)
        x_norm = np.tanh(states / 10.0)
        h_act = np.maximum(0.0, x_norm @ self.W1 + self.b1)
        q_current = h_act @ self.W2 + self.b2

        # Compute target Q values: r + gamma * max_a' Q_target(s', a')
        q_next_target = self._forward(next_states, target=True)
        max_q_next = np.max(q_next_target, axis=1)

        targets = np.copy(q_current)
        for i in range(len(batch)):
            if dones[i]:
                targets[i, actions[i]] = rewards[i]
            else:
                targets[i, actions[i]] = rewards[i] + self.config.discount * max_q_next[i]

        # Backpropagation
        loss_grad = 2.0 * (q_current - targets) / len(batch)
        dW2 = h_act.T @ loss_grad
        db2 = np.sum(loss_grad, axis=0, keepdims=True)

        dh = loss_grad @ self.W2.T
        dh[h_act <= 0.0] = 0.0

        dW1 = x_norm.T @ dh
        db1 = np.sum(dh, axis=0, keepdims=True)

        # SGD gradient update
        lr = self.config.learning_rate
        self.W1 -= lr * np.clip(dW1, -1.0, 1.0)
        self.b1 -= lr * np.clip(db1, -1.0, 1.0)
        self.W2 -= lr * np.clip(dW2, -1.0, 1.0)
        self.b2 -= lr * np.clip(db2, -1.0, 1.0)

        # Decay exploration rate
        self.epsilon = max(self.config.epsilon_end, self.epsilon * self.config.epsilon_decay)
        self.step_counter += 1

        # Periodic target network sync
        if self.step_counter % self.config.target_update_interval == 0:
            self.target_W1 = np.copy(self.W1)
            self.target_b1 = np.copy(self.b1)
            self.target_W2 = np.copy(self.W2)
            self.target_b2 = np.copy(self.b2)

        return float(np.mean((q_current - targets) ** 2))
