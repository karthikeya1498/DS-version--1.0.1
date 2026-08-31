# Container Deployment and Reusable Skill Validation

## Containerized service

The routing and forecasting engine is packaged as a FastAPI microservice. The Dockerfile uses Python 3.11, installs the declared dependencies, runs as non-root user `appuser`, exposes port 8000, and defines a health check. Docker Compose starts the API as `optima-api` and PostgreSQL as a health-gated dependency.

The REST surface includes health, simulation, optimization demo, demand forecasting, ETA prediction, routing strategies, decision explanation, and experiment status endpoints. Local in-process API smoke tests pass. The current sandbox does not have the Docker CLI installed, so an actual image build and Compose startup could not be executed here; the deployment files are ready for a Docker-enabled host.

## New logistics dataset

The reusable workflow was tested against the UCI **Daily Demand Forecasting Orders** dataset. UCI describes it as a 60-day real database from a Brazilian logistics company with 12 predictive attributes and a daily total-orders target [1]. The data is stored at `data/raw/logistics/Daily_Demand_Forecasting_Orders.csv`.

The logistics adapter uses a chronological split after constructing one-day and seven-day lags plus seven-day and fourteen-day prior rolling means. The resulting evaluation contains 46 rows after history warm-up, with 36 training rows and 10 test rows.

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Training mean | 48.639 | 66.188 | -0.565 |
| Gradient Boosting | 20.575 | 25.267 | 0.772 |
| XGBoost | **18.408** | **23.929** | **0.795** |

The XGBoost adapter improves MAE by approximately 62.1% relative to the training-mean baseline. Because the dataset contains only 60 observations, these values are useful as a workflow smoke test and not as a stable estimate of generalization performance.

## Reusable runner command

```bash
python /home/ubuntu/skills/optima-x-research-workflow/scripts/run_workflow.py \
  /home/ubuntu/OPTIMA-X \
  --dataset /home/ubuntu/OPTIMA-X/data/raw/logistics/Daily_Demand_Forecasting_Orders.csv \
  --skip-default-forecast
```

The runner completed graph benchmarks, obstacle benchmarks, the alternate logistics forecast adapter, and the full test suite. The skill validator reports that `optima-x-research-workflow` is valid.

### Reference

[1]: https://archive.ics.uci.edu/dataset/409/daily+demand+forecasting+orders "Daily Demand Forecasting Orders — UCI Machine Learning Repository"
