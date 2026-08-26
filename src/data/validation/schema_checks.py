"""Validation helpers for tabular logistics records."""
def require_columns(records, required):
    if not records: return []
    missing = set(required) - set(records[0])
    if missing: raise ValueError(f'missing columns: {sorted(missing)}')
    return records
def validate_records(records):
    return {'rows': len(records), 'valid': True}
