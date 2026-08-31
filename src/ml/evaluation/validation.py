"""Time-series validation, bootstrap confidence intervals, and error slice analysis."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
import pandas as pd
from scipy import stats

from src.ml.evaluation.metrics import mae, rmse


def rolling_origin_cv(
    series: Sequence[float],
    min_train_size: int,
    step_size: int = 1,
    horizon: int = 1,
) -> list[tuple[list[float], list[float]]]:
    """
    Generate rolling-origin (expanding window) splits for time series evaluation.
    Guarantees no future lookahead.
    """
    data = list(series)
    n = len(data)
    splits = []
    curr = min_train_size
    while curr + horizon <= n:
        train = data[:curr]
        test = data[curr : curr + horizon]
        splits.append((train, test))
        curr += step_size
    return splits


def bootstrap_metric_ci(
    y_true: Sequence[float],
    y_pred: Sequence[float],
    metric_fn: Callable[[list[float], list[float]], float] = mae,
    n_bootstraps: int = 400,
    confidence_level: float = 0.95,
    random_state: int = 42,
) -> tuple[float, float, float]:
    """
    Compute metric point estimate and bootstrap confidence interval [lower, upper].
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    n = len(y_t)
    if n == 0:
        return 0.0, 0.0, 0.0

    point_est = metric_fn(y_t.tolist(), y_p.tolist())
    rng = np.random.default_rng(random_state)
    boot_scores = []

    for _ in range(n_bootstraps):
        idx = rng.choice(n, size=n, replace=True)
        boot_scores.append(metric_fn(y_t[idx].tolist(), y_p[idx].tolist()))

    alpha = (1.0 - confidence_level) / 2.0
    lower = float(np.percentile(boot_scores, 100.0 * alpha))
    upper = float(np.percentile(boot_scores, 100.0 * (1.0 - alpha)))
    return float(point_est), lower, upper


def paired_model_comparison(
    errors_model_a: Sequence[float],
    errors_model_b: Sequence[float],
) -> dict[str, float]:
    """
    Perform paired t-test and Wilcoxon signed-rank test to determine if
    difference in model prediction errors is statistically significant.
    """
    err_a = np.asarray(errors_model_a, dtype=float)
    err_b = np.asarray(errors_model_b, dtype=float)
    diff = err_a - err_b

    # Paired Student's t-test
    t_stat, p_val_t = stats.ttest_rel(err_a, err_b)
    # Wilcoxon signed-rank test (non-parametric)
    try:
        w_stat, p_val_w = stats.wilcoxon(err_a, err_b)
    except Exception:
        w_stat, p_val_w = 0.0, 1.0

    return {
        "mean_error_diff": float(np.mean(diff)),
        "t_statistic": float(t_stat),
        "t_test_p_value": float(p_val_t),
        "wilcoxon_statistic": float(w_stat),
        "wilcoxon_p_value": float(p_val_w),
        "statistically_significant": float(1.0 if p_val_t < 0.05 else 0.0),
    }


def analyze_error_slices(
    df: pd.DataFrame,
    slice_col: str,
    y_true_col: str = "actual",
    y_pred_col: str = "predicted",
) -> pd.DataFrame:
    """Analyze model error across categorical or discretized slices."""
    records = []
    for slice_val, group in df.groupby(slice_col):
        y_t = group[y_true_col].tolist()
        y_p = group[y_pred_col].tolist()
        records.append(
            {
                slice_col: slice_val,
                "sample_count": len(group),
                "mae": mae(y_t, y_p),
                "rmse": rmse(y_t, y_p),
                "mean_bias": float(np.mean(np.asarray(y_p) - np.asarray(y_t))),
            }
        )
    return pd.DataFrame(records)
