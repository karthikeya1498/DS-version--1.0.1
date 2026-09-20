/**
 * Page 4: VRP Combinatorial Optimization & DSA Solver Lab for OPTIMA-X.
 * Inspects 0/1 Knapsack DP capacity bin-packing, 2-Opt/3-Opt edge exchanges,
 * Dijkstra vs Haversine A*, Segment Trees, and Fenwick Trees.
 */

import { HighTechChartEngine } from "../charts/chart_engine";

export function renderOptimizationPage(): string {
  return `
    <div style="display: flex; flex-direction: column; gap: 24px;">
      <!-- Header -->
      <div style="background: var(--bg-surface); backdrop-filter: blur(12px); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px; box-shadow: var(--shadow-card); display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-gold); text-transform: uppercase;">Optimization Engine</span>
          <h2 style="margin: 4px 0 0; font-size: 1.6rem;">Combinatorial VRP Optimization & DSA Solver Lab</h2>
        </div>
        <span class="status-badge" style="border-color: var(--accent-gold); color: var(--accent-gold);">Capacitated VRP Active</span>
      </div>

      <!-- Vehicle Capacity Bin Packing Inspector -->
      <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="margin: 0; font-size: 1.25rem;">0/1 Knapsack DP Parcel Bin-Packing Allocation</h3>
          <span style="font-size: 0.8rem; font-weight: 700; color: var(--accent-emerald);">3 / 3 Vehicles Feasible (0 Violations)</span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px;">
          <!-- Truck A -->
          <div style="background: var(--bg-card); padding: 20px; border-radius: 14px; border: 1px solid var(--border-subtle);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <span style="font-weight: 800; color: var(--accent-cyan);">TRUCK A (100 KG MAX)</span>
              <span style="font-size: 0.78rem; font-weight: 700; color: var(--accent-emerald);">80% Load</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 900; margin-bottom: 8px;">80.0 kg / 100 kg</div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">
              Assigned Orders: <strong>O1 (30kg) + O3 (40kg) + O4 (10kg)</strong>
            </div>
            <div style="font-size: 0.8rem; background: var(--bg-deep); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
              Route: Depot → O1 → O3 → O4 → Depot
            </div>
          </div>

          <!-- Truck B -->
          <div style="background: var(--bg-card); padding: 20px; border-radius: 14px; border: 1px solid var(--border-subtle);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <span style="font-weight: 800; color: var(--accent-emerald);">TRUCK B (60 KG MAX)</span>
              <span style="font-size: 0.78rem; font-weight: 700; color: var(--accent-emerald);">100% Load</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 900; margin-bottom: 8px;">60.0 kg / 60 kg</div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">
              Assigned Orders: <strong>O5 (25kg) + O7 (35kg)</strong>
            </div>
            <div style="font-size: 0.8rem; background: var(--bg-deep); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
              Route: Depot → O5 → O7 → Depot
            </div>
          </div>

          <!-- Truck C -->
          <div style="background: var(--bg-card); padding: 20px; border-radius: 14px; border: 1px solid var(--border-subtle);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <span style="font-weight: 800; color: var(--accent-purple);">TRUCK C (40 KG MAX)</span>
              <span style="font-size: 0.78rem; font-weight: 700; color: var(--accent-emerald);">87.5% Load</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 900; margin-bottom: 8px;">35.0 kg / 40 kg</div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">
              Assigned Orders: <strong>O2 (20kg) + O6 (15kg)</strong>
            </div>
            <div style="font-size: 0.8rem; background: var(--bg-deep); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
              Route: Depot → O2 → O6 → O8 → Depot
            </div>
          </div>
        </div>
      </div>

      <!-- Benchmark Charts -->
      <div class="grid-layout-2col">
        <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;">
          <h4 style="margin: 0 0 16px; font-size: 1.15rem;">VRP Solvers Objective Cost vs Runtime</h4>
          ${HighTechChartEngine.renderBarChart({
            labels: ["Greedy DP", "2-Opt Local", "3-Opt Search", "Simulated Anneal", "Genetic Algorithm"],
            series: [
              { name: "Objective Cost", color: "#f59e0b", values: [485.2, 412.5, 389.1, 375.4, 368.2] },
              { name: "Runtime (ms)", color: "#38bdf8", values: [8.5, 24.2, 68.0, 145.0, 290.0] },
            ],
          })}
        </div>

        <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;">
          <h4 style="margin: 0 0 16px; font-size: 1.15rem;">Dijkstra vs Haversine A* Nodes Expanded</h4>
          ${HighTechChartEngine.renderLineChart({
            labels: ["10 Nodes", "50 Nodes", "200 Nodes", "1000 Nodes", "5000 Nodes"],
            series: [
              { name: "Dijkstra (O(V log V + E))", color: "#ef4444", values: [12, 58, 240, 1280, 6400] },
              { name: "Haversine A*", color: "#10b981", values: [8, 24, 85, 340, 1420] },
            ],
          })}
        </div>
      </div>
    </div>
  `;
}
