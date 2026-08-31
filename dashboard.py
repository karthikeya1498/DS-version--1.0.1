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
    load_osm_edges,
    load_phase1_status,
    load_phase3_comparison,
    load_phase3_sensitivity,
    load_rl_evaluation,
    vehicle_dispatch_rows,
)

st.set_page_config(page_title="OPTIMA-X Operations", page_icon="O", layout="wide")
st.title("OPTIMA-X Operations Dashboard")
st.caption("Reproducible road-network routing, vehicle dispatch, and demand intelligence")


@st.cache_data(show_spinner=False)
def simulation_snapshot(seed: int, hours: int, vehicles: int, orders_per_hour: int) -> dict:
    return run(seed=seed, duration_hours=hours, vehicles=vehicles, orders_per_hour=orders_per_hour)


with st.sidebar:
    st.header("Scenario controls")
    seed = st.number_input("Seed", min_value=0, value=42, step=1)
    hours = st.slider("Duration (hours)", 1, 24, 8)
    vehicles = st.slider("Vehicles", 1, 100, 10)
    orders_per_hour = st.slider("Orders per hour", 1, 100, 20)
    if st.button("Refresh artifacts"):
        st.cache_data.clear()
        st.rerun()

status = load_phase1_status(ROOT)
snapshot = simulation_snapshot(int(seed), hours, vehicles, orders_per_hour)
metrics = snapshot.get("metrics", {})
cols = st.columns(5)
for col, (label, key) in zip(
    cols,
    [
        ("Orders", "total_orders"),
        ("Delivered", "delivered_orders"),
        ("Late", "late_deliveries"),
        ("Unserved", "unserved_orders"),
        ("Cost", "total_cost"),
    ],
):
    col.metric(label, metrics.get(key, 0))

network_tab, dispatch_tab, forecast_tab, benchmark_tab, optimization_tab, rl_tab = st.tabs(
    [
        "Road network",
        "Live dispatches",
        "Demand forecast",
        "Algorithm benchmark",
        "Phase 3 optimization",
        "Phase 4 RL",
    ]
)
with network_tab:
    st.subheader("Road-network graph")
    fig, ax = plt.subplots(figsize=(9, 5))
    edges = load_osm_edges(ROOT)
    n = max(3, int(status.get("nodes", snapshot.get("nodes", 5))))
    if not edges.empty:
        for row in edges.itertuples(index=False):
            ax.plot([row.x0, row.x1], [row.y0, row.y1], color="#38bdf8", linewidth=0.45, alpha=0.3)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
    else:
        xs = list(range(n))
        ys = [(index * 2) % max(3, n // 2 + 1) for index in xs]
        ax.plot(xs, ys, color="#38bdf8", linewidth=1.5, alpha=0.65)
        ax.scatter(xs, ys, s=45, color="#0f766e", zorder=3)
        ax.set_xlabel("Node sequence")
        ax.set_ylabel("Road-network coordinate")
    ax.grid(alpha=0.2)
    st.pyplot(fig, clear_figure=True)
    st.info(
        f"Graph built: {status.get('graph_built', True)} | Nodes: {status.get('nodes', n)} | Edges: {status.get('edges', 'available through graph builder')}"
    )
with dispatch_tab:
    st.subheader("Live vehicle dispatch state")
    st.dataframe(vehicle_dispatch_rows(snapshot), use_container_width=True, hide_index=True)
    st.dataframe(dispatch_rows(snapshot), use_container_width=True, hide_index=True)
    st.caption(
        "The live WebSocket stream is exposed by the FastAPI service at `/api/v1/ws/traffic?token=<JWT>`."
    )
with forecast_tab:
    st.subheader("XGBoost demand forecast metrics")
    forecast = load_forecast_metrics(ROOT)
    if not forecast.empty and {"mae", "rmse"}.issubset(forecast.columns):
        st.bar_chart(forecast.set_index("model")[["mae", "rmse"]])
    else:
        st.info("Run scripts/train_unified_demand.py to populate unified forecast artifacts.")
with benchmark_tab:
    st.subheader("Dijkstra versus A*")
    benchmark = load_benchmark(ROOT)
    if not benchmark.empty and {"nodes", "algorithm", "runtime_ms_mean"}.issubset(
        benchmark.columns
    ):
        st.line_chart(benchmark.pivot(index="nodes", columns="algorithm", values="runtime_ms_mean"))
    else:
        st.info("Run benchmarks/graph_benchmark.py to populate routing artifacts.")
with optimization_tab:
    st.subheader("Phase 3 optimization lab")
    comparison = load_phase3_comparison(ROOT)
    sensitivity = load_phase3_sensitivity(ROOT)
    if not comparison.empty:
        st.dataframe(
            comparison.drop(columns=["route"], errors="ignore"),
            use_container_width=True,
            hide_index=True,
        )
        st.bar_chart(comparison.set_index("algorithm")[["objective", "runtime_ms"]])
    else:
        st.info("Run scripts/run_phase3_experiments.py to populate optimization artifacts.")
    if not sensitivity.empty:
        st.caption("Prediction error propagated through the same optimizer")
        st.line_chart(sensitivity.set_index("forecast_error")[["decision_cost"]])
with rl_tab:
    st.subheader("Phase 4 sequential reinforcement learning")
    rl = load_rl_evaluation(ROOT)
    if rl:
        st.json(
            {
                "algorithm": rl.get("algorithm"),
                "episodes": rl.get("episodes"),
                "ppo_mean_return": rl.get("ppo_mean_return"),
                "baseline_mean_return": rl.get("baseline_mean_return"),
            }
        )
        st.caption(
            "PPO is evaluated against the fixed all-defer baseline on unseen seeded scenarios."
        )
    else:
        st.info("Run scripts/run_phase4_experiments.py to populate RL artifacts.")

st.divider()
st.caption(
    f"Scenario {snapshot.get('scenario_id', 'S042')} | Seed {seed} | Simulation {snapshot.get('simulation', 'SUCCESS')}"
)
