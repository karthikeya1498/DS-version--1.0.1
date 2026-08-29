# Multi-Seed Downstream Decision Sensitivity

**Author:** Karthikeya  
**Dataset:** UCI Bike Sharing hourly demand  
**Optimizer:** fixed `Phase3Solver` with Greedy assignment and A* routing  
**Seeds:** 7, 42, 99, 123, 2026

## Experimental design

The benchmark expands the prediction-to-decision study across three fleet capacities, three route-cost profiles, three prediction models, and three prediction treatments. The same chronological data split, five-order operational scenario, objective weights, optimizer, and random-seed policy are retained across comparisons.

| Factor | Levels |
|---|---|
| Model | XGBoost, MLP, LSTM |
| Prediction treatment | Clean, stochastic Gaussian noise at 10%, targeted +20% error on the highest-priority order |
| Vehicle capacity | 5, 10, 20 units per vehicle |
| Route profile | Balanced, north-biased cost, south-biased cost |
| Seeds | 7, 42, 99, 123, 2026 |

The full run generated **405 paired observations** and **81 five-seed aggregate groups**. Each aggregate reports mean, population standard deviation, minimum, maximum, mean served orders, mean unserved orders, and mean lateness.

## Executed command

```bash
python3 scripts/run_multiseed_decision_sensitivity.py \
  --epochs 12 \
  --window 24 \
  --output data/processed/phase7_multiseed_sensitivity.json
```

## Results

The current scenario produced stable downstream outcomes across model seeds and treatments: every aggregate had zero observed cross-seed decision-cost standard deviation. Route-cost alternatives did affect the absolute cost. The balanced profile produced a mean cost of 327.25, the north-biased profile 326.875, and the south-biased profile 327.625. The fleet-capacity levels did not change service in this specific scenario: the system served 2 orders and left 3 unserved at capacities 5, 10, and 20.

Measured lateness remained zero and all selected routes were feasible. The result indicates that this scenario is still dominated by the assignment/capacity boundary. The sensitivity runner is functioning, but the operational design does not yet expose enough near-tie decisions for neural-model errors to alter the chosen plan.

## Interpretation

The absence of seed-driven cost variation is a valid result, not a reason to manufacture variance. It means the current route geometry and order-load construction create a robust decision basin. The route profile factor is visible in the cost, while model and treatment factors remain below the assignment threshold.

The next experiment should create a larger paired scenario panel with vehicle capacities near total demand, multiple vehicles with nearly equal route costs, deadline-sensitive ETA/late-risk features, and varied priority distributions. It should report paired deltas against the clean XGBoost baseline, assignment-change frequency, bootstrap confidence intervals, and the proportion of scenarios in which the model with the best prediction score also has the best operational outcome.

The raw machine-readable result is `data/processed/phase7_multiseed_sensitivity.json`, and the reproducible runner is `scripts/run_multiseed_decision_sensitivity.py`.
