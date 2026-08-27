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

## Hyperparameter sweep and loss-curve review

A reproducible nine-case sweep was run with learning rates **0.005, 0.02, and 0.05** crossed with horizons **12, 24, and 48**, using 40 training episodes and 12 unseen evaluation episodes per case. The full matrix is stored in `data/processed/phase4/ppo_sweep/results.json`, with rankings in `analysis.md` and visual diagnostics in `policy_loss_curves.png` and `value_loss_curves.png`.

| Learning rate | Horizon | PPO return | Baseline return | Delta versus baseline | Return SD |
|---:|---:|---:|---:|---:|---:|
| 0.005 | 12 | -1148.959 | -1264.433 | **+115.474** | 96.804 |
| 0.020 | 12 | -1148.959 | -1264.433 | **+115.474** | 96.804 |
| 0.050 | 12 | -1269.307 | -1264.433 | -4.873 | 94.920 |
| 0.020 | 24 | -2514.967 | -2511.367 | -3.600 | 163.832 |
| 0.050 | 24 | -2514.967 | -2511.367 | -3.600 | 163.832 |
| 0.005 | 24 | -2521.158 | -2511.367 | -9.791 | 163.836 |
| 0.050 | 48 | -4621.328 | -5076.067 | **+454.739** | 211.171 |
| 0.005 | 48 | -5083.267 | -5076.067 | -7.200 | 209.039 |
| 0.020 | 48 | -5083.267 | -5076.067 | -7.200 | 209.039 |

Higher return is better because the reward is the negative of operational cost. The best short-horizon result was obtained at horizon 12, where both 0.005 and 0.02 achieved the same measured return. The best absolute baseline-relative delta was the 0.05/horizon-48 case, although it also had the highest policy-loss variability and should be confirmed with additional seeds before selection.

The policy-loss plot is centered near zero after early episodes, but remains noisy. Higher learning rates produce larger excursions, particularly at horizon 48. The value-loss curves remain close to the clipping ceiling around 100 with intermittent drops, so they do not show smooth monotonic convergence. These loss curves are therefore diagnostic signals; the selection criterion remains business return, variability, and the comparison with the identical baseline.

## Multi-seed validation of the selected configuration

The sweep-selected configuration, learning rate **0.005** and horizon **12**, was rerun across seeds **7, 21, 42, 84, and 123**. Each seed used 60 training episodes and 20 unseen evaluation episodes. The all-defer baseline was evaluated on the same scenario seeds for every run.

| Metric | PPO | All-defer baseline |
|---|---:|---:|
| Mean return across seeds | -1220.914 | -1240.700 |
| Standard deviation across seeds | 83.317 | 31.168 |
| Mean PPO advantage | **+19.786** | — |
| Standard deviation of advantage | 53.440 | — |
| PPO wins | **1 of 5 seeds** | 4 of 5 |

The aggregate mean is positive for PPO because higher return is better, but the result is not robust: PPO beat the baseline in only one of five seeds, and the advantage variability is larger than the mean advantage. Consequently, the configuration should remain a research candidate rather than a production default. The result reinforces the need for multi-seed evaluation and motivates the next improvements: better action masking, a graph-backed state/action representation, a stronger policy/value function, and hybrid fallback to Phase 3 optimization.

The machine-readable results are stored in `data/processed/phase4/ppo_multiseed/summary.json` and `runs.json`. The validator is reproducible with `python3 scripts/run_ppo_multiseed.py`.

## Limitations

This Phase 4 increment intentionally uses a compact reference environment and a linear PPO policy rather than claiming production-scale RL. The current environment is a research harness for sequential decision evaluation. Future work can add a graph-backed observation encoder, stronger action masking, multi-agent centralized training, richer route-level actions, PyTorch policy networks, checkpointing, and evaluation against the Phase 3 solver on unseen demand patterns.
