import pandas as pd
from src.features.feature_pipeline import build_demand_features, chronological_split


def test_features_use_only_prior_demand_and_create_next_target():
    frame = pd.DataFrame({'timestamp': pd.date_range('2026-01-01', periods=30, freq='h', tz='UTC'), 'zone': ['A'] * 30, 'demand': list(range(30))})
    result = build_demand_features(frame, lags=(1,), windows=(3,))
    first = result.iloc[0]
    assert first['lag_1'] == 4
    assert first['rolling_mean_3'] == 3
    assert first['target'] == 6


def test_chronological_split_preserves_order_and_lengths():
    frame = pd.DataFrame({'value': range(10)})
    train, validation, test = chronological_split(frame, .6, .2)
    assert list(train['value']) == list(range(6))
    assert list(validation['value']) == [6, 7]
    assert list(test['value']) == [8, 9]
