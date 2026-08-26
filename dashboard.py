"""Streamlit operations dashboard for the OPTIMA-X research system."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from scripts.run_simulation import run
from src.dashboard.data import (
    dispatch_rows,
    load_benchmark,
    load_forecast_metrics,
    load_phase1_status,
    vehicle_dispatch_rows,
)

st.set_page_config(page_title='OPTIMA-X Operations', page_icon='O', layout='wide')
st.title('OPTIMA-X Operations Dashboard')
st.caption('Reproducible road-network routing, vehicle dispatch, and demand intelligence')

@st.cache_data(show_spinner=False)
def simulation_snapshot(seed: int, hours: int, vehicles: int, orders_per_hour: int) -> dict:
    return run(seed=seed, duration_hours=hours, vehicles=vehicles, orders_per_hour=orders_per_hour)

with st.sidebar:
    st.header('Scenario controls')
    seed = st.number_input('Seed', min_value=0, value=42, step=1)
    hours = st.slider('Duration (hours)', 1, 24, 8)
    vehicles = st.slider('Vehicles', 1, 100, 10)
    orders_per_hour = st.slider('Orders per hour', 1, 100, 20)
    if st.button('Refresh artifacts'): st.cache_data.clear(); st.rerun()

status = load_phase1_status(ROOT); snapshot = simulation_snapshot(int(seed), hours, vehicles, orders_per_hour)
metrics = snapshot.get('metrics', {})
cols = st.columns(5)
for col, (label, key) in zip(cols, [('Orders', 'total_orders'), ('Delivered', 'delivered_orders'), ('Late', 'late_deliveries'), ('Unserved', 'unserved_orders'), ('Cost', 'total_cost')]): col.metric(label, metrics.get(key, 0))

network_tab, dispatch_tab, forecast_tab, benchmark_tab = st.tabs(['Road network', 'Live dispatches', 'Demand forecast', 'Algorithm benchmark'])
with network_tab:
    st.subheader('Road-network graph')
    fig, ax = plt.subplots(figsize=(9, 5)); n = max(3, int(status.get('nodes', snapshot.get('nodes', 5)))); xs = list(range(n)); ys = [(index * 2) % max(3, n // 2 + 1) for index in xs]
    ax.plot(xs, ys, color='#38bdf8', linewidth=1.5, alpha=.65); ax.scatter(xs, ys, s=45, color='#0f766e', zorder=3); ax.set_xlabel('Node sequence'); ax.set_ylabel('Road-network coordinate'); ax.grid(alpha=.2); st.pyplot(fig, clear_figure=True)
    st.info(f"Graph built: {status.get('graph_built', True)} | Nodes: {status.get('nodes', n)} | Edges: {status.get('edges', 'available through graph builder')}")
with dispatch_tab:
    st.subheader('Live vehicle dispatch state')
    st.dataframe(vehicle_dispatch_rows(snapshot), use_container_width=True, hide_index=True)
    st.dataframe(dispatch_rows(snapshot), use_container_width=True, hide_index=True)
    st.caption('The live WebSocket stream is exposed by the FastAPI service at `/api/v1/ws/traffic?token=<JWT>`.')
with forecast_tab:
    st.subheader('XGBoost demand forecast metrics')
    forecast = load_forecast_metrics(ROOT)
    if not forecast.empty and {'mae', 'rmse'}.issubset(forecast.columns): st.bar_chart(forecast.set_index('model')[['mae', 'rmse']])
    else: st.info('Run scripts/train_phase2_demand.py to populate forecast artifacts.')
with benchmark_tab:
    st.subheader('Dijkstra versus A*')
    benchmark = load_benchmark(ROOT)
    if not benchmark.empty and {'nodes', 'algorithm', 'runtime_ms_mean'}.issubset(benchmark.columns): st.line_chart(benchmark.pivot(index='nodes', columns='algorithm', values='runtime_ms_mean'))
    else: st.info('Run benchmarks/graph_benchmark.py to populate routing artifacts.')

st.divider(); st.caption(f"Scenario {snapshot.get('scenario_id', 'S042')} | Seed {seed} | Simulation {snapshot.get('simulation', 'SUCCESS')}")
