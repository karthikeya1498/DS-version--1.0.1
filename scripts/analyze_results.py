"""Create benchmark and forecasting analysis artifacts."""
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
bench = pd.read_csv(ROOT / "data/processed/graph_benchmark.csv")
forecast = json.loads((ROOT / "data/processed/forecast_metrics.json").read_text())
wide = bench.pivot(index="grid_side", columns="algorithm", values=["runtime_ms_mean", "visited_nodes_mean", "path_cost"])
summary = []
for side in sorted(bench.grid_side.unique()):
    row = bench[bench.grid_side == side].set_index("algorithm")
    summary.append({"grid_side": int(side), "nodes": int(row.iloc[0].nodes), "dijkstra_ms": float(row.loc["dijkstra", "runtime_ms_mean"]), "astar_ms": float(row.loc["astar", "runtime_ms_mean"]), "astar_runtime_ratio": float(row.loc["astar", "runtime_ms_mean"] / row.loc["dijkstra", "runtime_ms_mean"]), "dijkstra_visited": float(row.loc["dijkstra", "visited_nodes_mean"]), "astar_visited": float(row.loc["astar", "visited_nodes_mean"]), "astar_visited_ratio": float(row.loc["astar", "visited_nodes_mean"] / row.loc["dijkstra", "visited_nodes_mean"]), "same_cost": bool(abs(row.loc["astar", "path_cost"] - row.loc["dijkstra", "path_cost"]) < 1e-9)})
Path(ROOT / "data/processed/benchmark_analysis.json").write_text(json.dumps(summary, indent=2))
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for algorithm, group in bench.groupby("algorithm"):
    axes[0].plot(group.nodes, group.runtime_ms_mean, marker="o", label=algorithm)
    axes[1].plot(group.nodes, group.visited_nodes_mean, marker="o", label=algorithm)
axes[0].set(xlabel="Nodes", ylabel="Mean runtime (ms)", title="Runtime scaling")
axes[1].set(xlabel="Nodes", ylabel="Mean visited nodes", title="Search expansion")
for ax in axes: ax.grid(alpha=.25); ax.legend()
fig.tight_layout(); fig.savefig(ROOT / "data/processed/graph_benchmark.png", dpi=160); plt.close(fig)
models = pd.DataFrame(forecast["models"]).T.reset_index(names="model")
fig, ax = plt.subplots(figsize=(8, 4.5)); ax.bar(models.model, models.mae, color=["#94a3b8", "#38bdf8", "#22c55e", "#f59e0b"][:len(models)]); ax.set_ylabel("MAE"); ax.set_title("UCI Bike Sharing demand forecast MAE"); ax.tick_params(axis="x", rotation=20); fig.tight_layout(); fig.savefig(ROOT / "data/processed/forecast_mae.png", dpi=160); plt.close(fig)
print(json.dumps({"benchmark": summary, "forecast": forecast}, indent=2))
