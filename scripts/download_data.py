"""Download legally redistributable Phase 1 reference datasets."""
from __future__ import annotations

import argparse
from pathlib import Path
from urllib.request import urlretrieve

DATASETS = {
    'bike_hour': ('https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip', 'data/raw/mobility/bike_sharing.zip'),
    'logistics_daily': ('https://archive.ics.uci.edu/static/public/409/daily+demand+forecasting+orders.zip', 'data/raw/logistics/daily_demand.zip'),
}

def download(name: str, root: str | Path = '.') -> Path:
    if name not in DATASETS: raise ValueError(f'unknown dataset: {name}')
    url, relative = DATASETS[name]; target = Path(root) / relative; target.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, target)
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--root', default='.'); parser.add_argument('--dataset', choices=[*DATASETS, 'all'], default='all'); args = parser.parse_args()
    for name in DATASETS if args.dataset == 'all' else [args.dataset]: print(download(name, args.root))
