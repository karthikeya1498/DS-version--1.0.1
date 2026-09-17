"""Condition-based error analysis for forecasting outputs."""
from __future__ import annotations

import pandas as pd


def segment_mae(frame: pd.DataFrame, actual: str = 'actual', predicted: str = 'predicted', segments: dict[str, str] | None = None) -> dict[str, float]:
    if segments is None: segments = {'all': 'True'}
    result = {}
    for name, expression in segments.items():
        subset = frame.query(expression) if expression != 'True' else frame
        result[name] = float((subset[actual] - subset[predicted]).abs().mean()) if len(subset) else float('nan')
    return result
