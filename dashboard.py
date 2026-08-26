"""Streamlit dashboard for graph, dispatch, and demand-forecast operations."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title='OPTIMA-X Operations', layout='wide')
st.title('OPTIMA-X Operations Dashboard')
st.caption('Road-network routing, live dispatch state, and XGBoost demand forecasting')
root = Path(__file__).parent
forecast_path = root / 'data/processed/forecast_metrics_lagged.json'
bench_path = root / 'data/processed/graph_benchmark.csv'
col1, col2, col3 = st.columns(3)
if forecast_path.exists():
    metrics = json.loads(forecast_path.read_text())['models']
    best = metrics.get('xgboost', metrics.get('random_forest', {}))
    col1.metric('XGBoost MAE', f"{best.get('mae', 0):.2f}")
    col2.metric('XGBoost RMSE', f"{best.get('rmse', 0):.2f}")
    col3.metric('XGBoost R²', f"{best.get('r2', 0):.3f}")
left, right = st.columns(2)
with left:
    st.subheader('Road network graph')
    graph = nx.grid_2d_graph(6, 6)
    pos = {(x, y): (x, y) for x, y in graph.nodes}
    fig, ax = plt.subplots(figsize=(6, 5)); nx.draw(graph, pos, ax=ax, node_size=35, width=.7, node_color='#38bdf8'); st.pyplot(fig, clear_figure=True)
with right:
    st.subheader('Demand forecast models')
    if forecast_path.exists():
        frame = pd.DataFrame(metrics).T.reset_index(names='model')
        st.bar_chart(frame.set_index('model')[['mae', 'rmse']])
    else: st.info('Run the forecasting pipeline to populate metrics.')
st.subheader('Routing benchmark')
if bench_path.exists():
    benchmark = pd.read_csv(bench_path)
    st.line_chart(benchmark.pivot(index='nodes', columns='algorithm', values='runtime_ms_mean'))
else: st.info('Run the graph benchmark to populate routing results.')
if st.button('Refresh data'): st.rerun()
