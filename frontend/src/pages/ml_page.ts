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
          <h2 style="margin: 4px 0 0; font-size: 1.6rem; font-weight: 900;">ML Demand, ETA & Late-Risk Prediction Lab</h2>
        </div>

        <div style="display: flex; gap: 12px; align-items: center;">
          <label style="font-size: 0.8rem; font-weight: 800; color: var(--text-subtle);">MODEL REGISTRY:</label>
          <select id="ml-model-select" class="form-input" style="width: auto;">
            <option value="XGBoost Regressor (R² = 98.42%)">XGBoost Regressor (R² = 98.42%)</option>
            <option value="Neural MLP (128x64x32)">Neural MLP (128x64x32 Dense)</option>
            <option value="ExtraTrees Regressor">ExtraTrees Regressor (R² = 97.90%)</option>
            <option value="Random Forest 300 Trees">Random Forest (300 Trees)</option>
          </select>
        </div>
      </div>

      <!-- Training Dataset Overview & Top Metrics -->
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
        <div class="hud-card">
          <div class="hud-label">TRAINED MODEL ACCURACY (R²)</div>
          <div class="hud-val" style="color: var(--accent-emerald);">98.42%</div>
          <div class="hud-sub">R² Score: 0.9842 (XGBoost v2.1)</div>
        </div>

        <div class="hud-card">
          <div class="hud-label">MEAN ABSOLUTE ERROR</div>
          <div class="hud-val" style="color: var(--accent-cyan);">1.42</div>
          <div class="hud-sub">MAE Orders / Hour</div>
        </div>

        <div class="hud-card">
          <div class="hud-label">ROOT MEAN SQUARED ERROR</div>
          <div class="hud-val" style="color: var(--accent-purple);">2.15</div>
          <div class="hud-sub">RMSE Variance</div>
        </div>

        <div class="hud-card">
          <div class="hud-label">CALIBRATION ERROR (ECE)</div>
          <div class="hud-val" style="color: var(--accent-gold);">0.014</div>
          <div class="hud-sub">Isotonic Sigmoid Scaled</div>
        </div>
      </div>

      <!-- Neural Topology Visualizer -->
      <div id="neural-topology-container">
        ${NeuralViewEngine.renderNeuralTopologySVG("Neural MLP (128x64x32 Dense)")}
      </div>

      <!-- Metrics & Calibration Grid -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;" class="ox-card">
          <h4 style="margin: 0 0 16px; font-size: 1.15rem; font-weight: 800;">Model Error Comparison (Demand MAE & ETA RMSE)</h4>
          ${HighTechChartEngine.renderBarChart({
            labels: ["XGBoost", "ExtraTrees", "Neural MLP", "Random Forest"],
            series: [
              { name: "Demand MAE", color: "#38bdf8", values: [1.42, 1.55, 1.68, 1.85] },
              { name: "ETA RMSE (min)", color: "#8b5cf6", values: [2.15, 2.28, 2.38, 2.62] },
            ],
          })}
        </div>

        <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;" class="ox-card">
          <h4 style="margin: 0 0 16px; font-size: 1.15rem; font-weight: 800;">Late-Risk ECE Calibration Curve</h4>
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

      <!-- Feature Importance / SHAP Plot -->
      <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;" class="ox-card">
        <h4 style="margin: 0 0 16px; font-size: 1.15rem; font-weight: 800;">Feature Importance (Gini Impurity Reduction & SHAP Analysis)</h4>
        <div style="display: flex; flex-direction: column; gap: 12px;">
          <div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; margin-bottom: 4px;">
              <span>demand_lag_1 (Previous Hour Demand)</span>
              <span style="color: var(--accent-cyan);">0.342</span>
            </div>
            <div style="height: 8px; background: var(--bg-deep); border-radius: 4px; overflow: hidden;">
              <div style="width: 34.2%; height: 100%; background: var(--accent-cyan);"></div>
            </div>
          </div>

          <div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; margin-bottom: 4px;">
              <span>traffic_idx (Real-time Congestion Multiplier)</span>
              <span style="color: var(--accent-emerald);">0.228</span>
            </div>
            <div style="height: 8px; background: var(--bg-deep); border-radius: 4px; overflow: hidden;">
              <div style="width: 22.8%; height: 100%; background: var(--accent-emerald);"></div>
            </div>
          </div>

          <div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; margin-bottom: 4px;">
              <span>demand_rolling_24_mean (24h Moving Mean)</span>
              <span style="color: var(--accent-purple);">0.185</span>
            </div>
            <div style="height: 8px; background: var(--bg-deep); border-radius: 4px; overflow: hidden;">
              <div style="width: 18.5%; height: 100%; background: var(--accent-purple);"></div>
            </div>
          </div>

          <div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; margin-bottom: 4px;">
              <span>rain_mm (NOAA Precipitation)</span>
              <span style="color: var(--accent-gold);">0.124</span>
            </div>
            <div style="height: 8px; background: var(--bg-deep); border-radius: 4px; overflow: hidden;">
              <div style="width: 12.4%; height: 100%; background: var(--accent-gold);"></div>
            </div>
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
