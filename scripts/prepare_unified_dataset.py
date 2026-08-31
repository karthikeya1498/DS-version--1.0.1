"""Prepare unified, auditable Phase 1 data products from downloaded sources."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed/unified'

def prepare_tlc() -> dict:
    source = ROOT / 'data/raw/traffic/yellow_tripdata_2024-01.parquet'; frame = pd.read_parquet(source)
    frame['timestamp'] = pd.to_datetime(frame['tpep_pickup_datetime'], utc=True); frame['zone_id'] = frame['PULocationID'].astype(str); frame['travel_time_min'] = (pd.to_datetime(frame['tpep_dropoff_datetime'], utc=True) - frame['timestamp']).dt.total_seconds() / 60
    traffic = frame.loc[(frame['travel_time_min'] > 0) & (frame['trip_distance'] >= 0), ['timestamp', 'zone_id', 'travel_time_min', 'trip_distance']].copy(); traffic['hour'] = traffic['timestamp'].dt.floor('h'); traffic = traffic.groupby(['hour', 'zone_id'], as_index=False).agg(travel_time_min=('travel_time_min', 'median'), trip_distance_km=('trip_distance', 'median'), trips=('zone_id', 'size')); traffic['speed_proxy_kmh'] = traffic['trip_distance_km'] / (traffic['travel_time_min'] / 60).clip(lower=.01); traffic.to_csv(OUT / 'traffic_hourly.csv', index=False)
    demand = traffic[['hour', 'zone_id', 'trips']].rename(columns={'hour': 'timestamp', 'trips': 'demand'}); demand.to_csv(OUT / 'demand_hourly_from_tlc.csv', index=False)
    return {'source': str(source.relative_to(ROOT)), 'source_rows': len(frame), 'traffic_rows': len(traffic), 'demand_rows': len(demand)}

def prepare_noaa() -> dict:
    source = ROOT / 'data/raw/weather/USW00094728.csv.gz'; names = ['station', 'date', 'element', 'value', 'mflag', 'qflag', 'sflag', 'obstime']; frame = pd.read_csv(source, compression='gzip', names=names, dtype={'value': 'float64'}, low_memory=False); frame = frame[frame['qflag'].isna()].copy(); pivot = frame.pivot_table(index=['station', 'date'], columns='element', values='value', aggfunc='first').reset_index(); pivot['date'] = pd.to_datetime(pivot['date'], format='%Y%m%d', utc=True); rename = {'TMAX': 'tmax_c_tenths', 'TMIN': 'tmin_c_tenths', 'PRCP': 'precipitation_mm_tenths'}; pivot = pivot.rename(columns=rename); pivot.to_csv(OUT / 'weather_daily.csv', index=False); return {'source': str(source.relative_to(ROOT)), 'rows': len(pivot), 'columns': list(pivot.columns)}

def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True); result = {'traffic_demand': prepare_tlc(), 'weather': prepare_noaa()}; (OUT / 'manifest.json').write_text(json.dumps(result, indent=2), encoding='utf-8'); return result

if __name__ == '__main__': print(json.dumps(main(), indent=2))
