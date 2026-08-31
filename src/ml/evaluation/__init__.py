"""ML Evaluation package."""

from src.ml.evaluation.calibration import (
    PlattScaler,
    brier_score,
    expected_calibration_error,
    reliability_curve,
)
from src.ml.evaluation.metrics import mae, mape, r2, rmse
from src.ml.evaluation.validation import (
    analyze_error_slices,
    bootstrap_metric_ci,
    paired_model_comparison,
    rolling_origin_cv,
)

__all__ = [
    "PlattScaler",
    "analyze_error_slices",
    "bootstrap_metric_ci",
    "brier_score",
    "expected_calibration_error",
    "mae",
    "mape",
    "paired_model_comparison",
    "r2",
    "reliability_curve",
    "rmse",
    "rolling_origin_cv",
]
