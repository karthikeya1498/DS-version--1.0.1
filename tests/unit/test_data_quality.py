from datetime import UTC, datetime, timedelta

from src.data.validation.quality_engine import validate_operational_records


def test_quality_engine_accepts_valid_records():
    now = datetime.now(UTC)
    result = validate_operational_records([{'order_id': 'o1', 'distance_km': 2.0, 'capacity_units': 4, 'latitude': 10.0, 'longitude': 20.0, 'created_at': now, 'delivered_at': now + timedelta(minutes=5)}])
    assert result['valid'] is True
    assert result['errors'] == []


def test_quality_engine_reports_duplicate_and_invalid_values():
    result = validate_operational_records([{'order_id': 'o1', 'distance_km': -1, 'latitude': 100}, {'order_id': 'o1', 'actual_eta': -3}])
    assert result['valid'] is False
    assert any('duplicate' in error for error in result['errors'])
    assert any('distance_km' in error for error in result['errors'])
    assert any('latitude' in error for error in result['errors'])
    assert any('actual_eta' in error for error in result['errors'])


def test_quality_engine_reports_temporal_error():
    now = datetime.now(UTC)
    result = validate_operational_records([{'order_id': 'o1', 'created_at': now, 'delivered_at': now - timedelta(seconds=1)}])
    assert result['valid'] is False
    assert 'delivered_at precedes created_at' in result['errors'][0]
