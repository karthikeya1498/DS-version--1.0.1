"""Minimal, reproducible PPO implementation for the Phase 4 environment."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PPOConfig:
    learning_rate: float = 0.02
    discount: float = 0.99
    gae_lambda: float = 0.95
    clip_ratio: float = 0.2
    epochs: int = 4
    seed: int = 42

@dataclass(frozen=True)
class TrainingMetrics:
    episodes: int
    returns: tuple[float, ...]
    mean_return: float
    final_return: float

class PPOAgent:
    """Linear policy/value PPO reference implementation without a framework dependency."""
    def __init__(self, observation_dim: int, action_count: int, config: PPOConfig = PPOConfig()):
        if min(observation_dim, action_count) <= 0: raise ValueError('dimensions must be positive')
        self.observation_dim, self.action_count, self.config = observation_dim, action_count, config
        self.rng = np.random.default_rng(config.seed)
        self.policy = self.rng.normal(0, .01, (observation_dim, action_count))
        self.value = np.zeros(observation_dim, dtype=np.float64)

    def _features(self, observation: np.ndarray) -> np.ndarray:
        return np.tanh(np.asarray(observation, dtype=np.float64) / 10.0)

    def _probs(self, observation: np.ndarray) -> np.ndarray:
        logits = self._features(observation) @ self.policy
        logits -= logits.max()
        values = np.exp(logits)
        return values / values.sum()

    def act(self, observation: np.ndarray, deterministic: bool = False) -> tuple[int, float, float]:
        probs = self._probs(observation)
        action = int(np.argmax(probs)) if deterministic else int(self.rng.choice(self.action_count, p=probs))
        return action, float(np.log(max(probs[action], 1e-12))), float(self._features(observation) @ self.value)

    def update(self, observations: np.ndarray, actions: np.ndarray, old_log_probs: np.ndarray, advantages: np.ndarray, returns: np.ndarray) -> dict[str, float]:
        observations = np.asarray(observations, dtype=np.float64)
        actions = np.asarray(actions, dtype=int)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        policy_loss, value_loss = 0.0, 0.0
        for _ in range(self.config.epochs):
            for observation, action, old_log_prob, advantage, target in zip(observations, actions, old_log_probs, advantages, returns):
                probs = self._probs(observation)
                ratio = np.exp(np.log(max(probs[action], 1e-12)) - old_log_prob)
                clipped_ratio = np.clip(ratio, 1 - self.config.clip_ratio, 1 + self.config.clip_ratio)
                surrogate = min(ratio * advantage, clipped_ratio * advantage)
                features = self._features(observation)
                gradient = (np.eye(self.action_count)[action] - probs) * min(ratio, 1 + self.config.clip_ratio) * advantage
                self.policy += self.config.learning_rate * np.clip(np.outer(features, gradient), -1.0, 1.0)
                estimate = features @ self.value
                error = float(np.clip(target - estimate, -10.0, 10.0))
                self.value += self.config.learning_rate * error * features
                policy_loss -= surrogate
                value_loss += error * error
        count = max(1, len(observations) * self.config.epochs)
        return {'policy_loss': float(policy_loss / count), 'value_loss': float(value_loss / count)}

    def train(self, env, episodes: int = 100) -> TrainingMetrics:
        returns = []
        for _ in range(episodes):
            observation = env.reset()
            observations, actions, log_probs, rewards, values = [], [], [], [], []
            done = False
            while not done:
                action, log_prob, value = self.act(observation)
                joint_actions = np.zeros(env.agents, dtype=int)
                joint_actions[0] = action
                next_observation, reward, done, _ = env.step(joint_actions)
                observations.append(observation); actions.append(action); log_probs.append(log_prob); rewards.append(reward); values.append(value)
                observation = next_observation
            advantages, gae, next_value = [], 0.0, 0.0
            for reward, value in zip(reversed(rewards), reversed(values)):
                delta = reward + self.config.discount * next_value - value
                gae = delta + self.config.discount * self.config.gae_lambda * gae
                advantages.append(gae); next_value = value
            advantages = np.asarray(list(reversed(advantages)))
            targets = advantages + np.asarray(values)
            self.update(np.asarray(observations), np.asarray(actions), np.asarray(log_probs), advantages, targets)
            returns.append(float(sum(rewards)))
        return TrainingMetrics(episodes, tuple(returns), float(np.mean(returns)) if returns else 0.0, float(returns[-1]) if returns else 0.0)
