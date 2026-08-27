# OPTIMA-X Phase 4: Sequential Simulation and PPO

## Scope

Phase 4 extends the connected Phase 1–3 decision engine into a sequential control problem. The environment exposes pending demand, vehicle positions, remaining capacity, traffic state, and time through a typed `LogisticsState`. Each timestep accepts one discrete action per agent: defer, serve, reroute, or reposition.

## Architecture

| Layer | Implementation | Phase connection |
|---|---|---|
| State | `LogisticsState.vector()` | Phase 1 fleet/traffic state representation |
| Actions | `Action` enum | Sequential control contract |
| Environment | `MultiAgentLogisticsEnv` | Demand arrivals and traffic drift with seeded RNG |
| Reward | `RewardBreakdown` | Operating cost, lateness, unserved demand, priority completion |
| Policy | `PPOAgent` | PPO clipped surrogate with linear policy/value heads |
| Training | `src/rl/training/train.py` | Reproducible episode returns |
| Evaluation | `src/rl/training/evaluate.py` | PPO versus all-defer baseline on unseen seeds |
| Dashboard | Phase 4 RL tab | Displays evaluation metrics |

## PPO implementation

The agent uses a dependency-light reference implementation so the repository remains executable without requiring a deep-learning framework. It uses a clipped policy ratio, generalized advantage estimation, a learned linear value function, deterministic seeding, normalized observations, and bounded updates for numerical stability. PyTorch remains available as an optional dependency for a future higher-capacity policy implementation; it is not silently required by the base test path.

## Measured run

The standard command is `python3 scripts/run_phase4_experiments.py`. With seed 42, 100 training episodes, 20 unseen evaluation scenarios, three agents, five zones, and a 24-step horizon, the recorded metrics were:

| Metric | Value |
|---|---:|
| Training episodes | 100 |
| Training mean return | -2532.034 |
| PPO unseen-scenario mean return | -2499.300 |
| All-defer baseline mean return | -2495.700 |
| Evaluation scenarios | 20 |

The PPO reference policy did not outperform the fixed all-defer baseline in this initial fixture. That is the measured result and not evidence that PPO is ineffective generally. It indicates that reward shaping, action masking, capacity dynamics, and training scale require further research before claiming improvement.

## Reproducibility and tests

The environment is deterministic when reset with the same seed, and the test suite verifies identical transitions, action masks, reward decomposition, PPO training metrics, and deterministic inference. The complete repository validation run passed linting, compilation, and **33 tests**. Existing Phase 1 graph/simulation, Phase 2 forecasting, Phase 3 optimization, API, and Phase 4 RL tests execute together.

## Limitations

This Phase 4 increment intentionally uses a compact reference environment and a linear PPO policy rather than claiming production-scale RL. The current environment is a research harness for sequential decision evaluation. Future work can add a graph-backed observation encoder, stronger action masking, multi-agent centralized training, richer route-level actions, PyTorch policy networks, checkpointing, and evaluation against the Phase 3 solver on unseen demand patterns.
