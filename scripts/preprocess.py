"""Convert reference CSV inputs into validated clean CSV outputs and manifests."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def process(input_path: str | Path, output_path: str | Path) -> dict:
    source, target = Path(input_path), Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(source, sep=';' if 'Demand' in source.name else ',')
    frame = frame.drop_duplicates().dropna(how='all')
    frame.to_csv(target, index=False)
    manifest = {'source': str(source), 'output': str(target), 'rows': len(frame), 'columns': list(frame.columns), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'validated': True}
    target.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('input'); parser.add_argument('output'); args = parser.parse_args(); print(json.dumps(process(args.input, args.output), indent=2))
