"""Download bounded public extracts with checksummed reproducibility manifests.

Author: Karthikeya
The source map is intentionally restricted to official HTTPS hosts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "osm_manhattan": {"url": "https://overpass-api.de/api/interpreter?data=[out:json];way[highway](40.70,-74.02,40.80,-73.93);out%20geom;", "path": "data/raw/osm/manhattan_roads.json", "kind": "osm"},
    "nyc_tlc_yellow_2024_01": {"url": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet", "path": "data/raw/traffic/yellow_tripdata_2024-01.parquet", "kind": "traffic"},
    "noaa_ghcn_central_park": {"url": "https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/USW00094728.csv.gz", "path": "data/raw/weather/USW00094728.csv.gz", "kind": "weather"},
    "uci_bike_sharing": {"url": "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip", "path": "data/raw/demand/bike_sharing.zip", "kind": "demand"},
    "uci_logistics_orders": {"url": "https://archive.ics.uci.edu/static/public/409/daily+demand+forecasting+orders.zip", "path": "data/raw/orders/daily_demand.zip", "kind": "orders"},
}
_ALLOWED_HOSTS = {urlparse(source["url"]).hostname for source in SOURCES.values()}
_MAX_DOWNLOAD_BYTES = 2_000_000_000


def _validated_request(url: str) -> Request:
    """Build a request only for an allowlisted official HTTPS host."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in _ALLOWED_HOSTS:
        raise ValueError(f"unsupported dataset URL: {url}")
    return Request(url, headers={"User-Agent": "OPTIMA-X research downloader/1.0"})


def download_one(name: str, force: bool = False) -> dict:
    """Download one source, enforce a size bound, and write its manifest."""
    source = SOURCES[name]
    target = ROOT / source["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if force or not target.exists():
        with urlopen(_validated_request(source["url"]), timeout=120) as response:  # nosec B310
            content_length = int(response.headers.get("Content-Length", 0))
            if content_length > _MAX_DOWNLOAD_BYTES:
                raise ValueError(f"dataset exceeds {_MAX_DOWNLOAD_BYTES} bytes")
            data = response.read(_MAX_DOWNLOAD_BYTES + 1)
            if len(data) > _MAX_DOWNLOAD_BYTES:
                raise ValueError(f"dataset exceeds {_MAX_DOWNLOAD_BYTES} bytes")
            target.write_bytes(data)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest = {"name": name, **source, "local_path": str(target.relative_to(ROOT)), "bytes": target.stat().st_size, "sha256": digest}
    target.with_suffix(target.suffix + ".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def write_holidays(year: int = 2024) -> dict:
    """Write deterministic United States holiday metadata."""
    try:
        import holidays
        entries = [{"date": day.isoformat(), "holiday": label, "event": "federal_holiday", "expected_demand_multiplier": 0.8} for day, label in sorted(holidays.US(years=year).items())]
    except ImportError:
        entries = [{"date": f"{year}-01-01", "holiday": "New Year's Day", "event": "federal_holiday", "expected_demand_multiplier": 0.8}, {"date": f"{year}-07-04", "holiday": "Independence Day", "event": "federal_holiday", "expected_demand_multiplier": 0.8}, {"date": f"{year}-12-25", "holiday": "Christmas Day", "event": "federal_holiday", "expected_demand_multiplier": 0.8}]
    target = ROOT / "data/raw/events/us_holidays_2024.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=entries[0])
        writer.writeheader()
        writer.writerows(entries)
    manifest = {"name": "us_holidays_2024", "kind": "events", "local_path": str(target.relative_to(ROOT)), "rows": len(entries), "source": "python-holidays rules for United States federal holidays"}
    target.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main(names: list[str] | None = None, force: bool = False) -> list[dict]:
    """Download selected sources and write the aggregate manifest."""
    selected = names or list(SOURCES)
    manifests = [download_one(name, force) for name in selected]
    manifests.append(write_holidays())
    (ROOT / "data/raw/dataset_manifest.json").write_text(json.dumps({"generated_at": datetime.now(UTC).date().isoformat(), "datasets": manifests}, indent=2), encoding="utf-8")
    return manifests


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", action="append", choices=[*SOURCES, "all"])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    print(json.dumps(main(None if not args.dataset or "all" in args.dataset else args.dataset, args.force), indent=2))
