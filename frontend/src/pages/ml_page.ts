/**
 * Page 3: ML Prediction & Neural Architecture Lab for OPTIMA-X.
 * Inspects model versions, feature importance, neural activations, ETA predictions, and ECE calibration plots.
 */

import { NeuralViewEngine } from "../charts/neural_view";
import { HighTechChartEngine } from "../charts/chart_engine";

export function renderMlPage(): string {
  return `
    <div style="display: flex; flex-direction: column; gap: 24px;">
      <!-- Header -->
      <div style="background: var(--bg-surface); backdrop-filter: blur(12px); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px; box-shadow: var(--shadow-card); display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-purple); text-transform: uppercase;">Predictive ML Engine</span>
          <h2 style="margin: 4px 0 0; font-size: 1.6rem;">ML Demand, ETA & Late-Risk Prediction Lab</h2>
        </div>

        <div style="display: flex; gap: 10px; align-items: center;">
          <label style="font-size: 0.8rem; font-weight: 700; color: var(--text-subtle);">MODEL REGISTRY:</label>
          <select id="ml-model-select" class="form-input" style="width: auto;">
            <option value="Neural MLP (64x32)">Neural MLP (64x32 Dense)</option>
            <option value="XGBoost Regressor v2.1">XGBoost Regressor v2.1</option>
            <option value="Temporal LSTM/GRU">Temporal LSTM/GRU Model</option>
          </select>
        </div>
      </div>

      <!-- Neural Topology Visualizer -->
      <div id="neural-topology-container">
        ${NeuralViewEngine.renderNeuralTopologySVG("Neural MLP (64x32 Dense)")}
      </div>

      <!-- Metrics & Calibration Grid -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;">
          <h4 style="margin: 0 0 16px; font-size: 1.15rem;">Model Error Metrics (Demand MAE & ETA RMSE)</h4>
          ${HighTechChartEngine.renderBarChart({
            labels: ["XGBoost", "Neural MLP", "Temporal LSTM"],
            series: [
              { name: "Demand MAE", color: "#38bdf8", values: [1.42, 1.68, 1.35] },
              { name: "ETA RMSE (min)", color: "#8b5cf6", values: [2.85, 3.12, 2.45] },
            ],
          })}
        </div>

        <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;">
          <h4 style="margin: 0 0 16px; font-size: 1.15rem;">Late-Risk ECE Calibration Curve</h4>
          ${HighTechChartEngine.renderLineChart({
            labels: ["0.1", "0.3", "0.5", "0.7", "0.9"],
            series: [
              { name: "Ideal Calibration", color: "#64748b", values: [0.1, 0.3, 0.5, 0.7, 0.9] },
              { name: "Uncalibrated Model", color: "#ef4444", values: [0.22, 0.48, 0.72, 0.88, 0.98] },
              { name: "Isotonic Calibrated", color: "#10b981", values: [0.11, 0.31, 0.51, 0.69, 0.91] },
            ],
          })}
          <div style="margin-top: 14px; font-size: 0.85rem; color: var(--text-muted);">
            Expected Calibration Error (ECE): <strong style="color: var(--accent-emerald);">0.0142</strong> (Isotonic Sigmoid Scaling)
          </div>
        </div>
      </div>
    </div>
  `;
}

export function bindMlPageEvents(): void {
  const select = document.querySelector<HTMLSelectElement>("#ml-model-select");
  const container = document.querySelector<HTMLElement>("#neural-topology-container");

  select?.addEventListener("change", () => {
    if (container) {
      container.innerHTML = NeuralViewEngine.renderNeuralTopologySVG(select.value);
    }
  });
}
