"""Download official public datasets with bounded, HTTPS-only requests.

Author: Karthikeya
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DATASETS = {
    "bike_hour": (
        "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip",
        "data/raw/mobility/bike_sharing.zip",
    ),
    "logistics_daily": (
        "https://archive.ics.uci.edu/static/public/409/daily+demand+forecasting+orders.zip",
        "data/raw/logistics/daily_demand.zip",
    ),
}
_ALLOWED_HOSTS = {urlparse(url).hostname for url, _ in DATASETS.values()}
_MAX_DOWNLOAD_BYTES = 2_000_000_000


def download(name: str, root: str | Path = ".") -> Path:
    """Download one allowlisted dataset without exceeding the size bound."""
    if name not in DATASETS:
        raise ValueError(f"unknown dataset: {name}")
    url, relative = DATASETS[name]
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in _ALLOWED_HOSTS:
        raise ValueError(f"unsupported dataset URL: {url}")
    target = Path(root) / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(
        Request(url, headers={"User-Agent": "OPTIMA-X research downloader/1.0"}), timeout=120
    ) as response:  # nosec B310
        content_length = int(response.headers.get("Content-Length", 0))
        if content_length > _MAX_DOWNLOAD_BYTES:
            raise ValueError(f"dataset exceeds {_MAX_DOWNLOAD_BYTES} bytes")
        data = response.read(_MAX_DOWNLOAD_BYTES + 1)
        if len(data) > _MAX_DOWNLOAD_BYTES:
            raise ValueError(f"dataset exceeds {_MAX_DOWNLOAD_BYTES} bytes")
        target.write_bytes(data)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--dataset", choices=[*DATASETS, "all"], default="all")
    args = parser.parse_args()
    for name in DATASETS if args.dataset == "all" else [args.dataset]:
        print(download(name, args.root))
