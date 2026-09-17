"""Validate a JSON-lines operational dataset."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.data.validation.quality_engine import validate_operational_records


def validate(path: str | Path) -> dict:
    records = [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]
    result = validate_operational_records(records)
    if not result['valid']: raise ValueError(json.dumps(result))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('path'); args = parser.parse_args(); print(json.dumps(validate(args.path), indent=2))
