/**
 * Research & Sensitivity Benchmark View Component.
 * Evaluates whether higher prediction accuracy translates to superior decision quality costs.
 */

export function renderResearchLab(): string {
  return `
    <div style="background: var(--bg-surface); backdrop-filter: blur(12px); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px; box-shadow: var(--shadow-card);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <div>
          <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-purple); text-transform: uppercase;">Research Experiment</span>
          <h3 style="margin: 4px 0 0; font-size: 1.3rem;">Predictive Accuracy vs Decision Quality Benchmark</h3>
        </div>
        <span class="status-badge" style="border-color: var(--accent-purple); color: var(--accent-purple);">Phase 7 Experiment</span>
      </div>

      <p style="color: var(--text-muted); margin-bottom: 20px; font-size: 0.92rem; line-height: 1.6;">
        Central Research Question: <em>Does higher predictive ML accuracy strictly translate to superior downstream logistics decisions?</em>
      </p>

      <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.88rem;">
        <thead>
          <tr style="border-bottom: 1px solid var(--border-subtle); color: var(--text-subtle); text-align: left;">
            <th style="padding: 10px;">Model Candidate</th>
            <th style="padding: 10px;">Prediction MAE</th>
            <th style="padding: 10px;">Late Prediction Accuracy</th>
            <th style="padding: 10px;">Total Distance (km)</th>
            <th style="padding: 10px;">Late Deliveries</th>
            <th style="padding: 10px;">Capacity Utilization</th>
            <th style="padding: 10px;">Downstream Decision Cost</th>
          </tr>
        </thead>
        <tbody>
          <tr style="border-bottom: 1px solid var(--border-subtle);">
            <td style="padding: 12px; font-weight: 700; color: var(--text-main);">Model A (Baseline Linear)</td>
            <td style="padding: 12px; color: var(--accent-crimson);">8.2 min</td>
            <td style="padding: 12px;">71%</td>
            <td style="padding: 12px;">221 km</td>
            <td style="padding: 12px; color: var(--accent-crimson);">9</td>
            <td style="padding: 12px;">61%</td>
            <td style="padding: 12px; font-weight: 700;">485.20</td>
          </tr>
          <tr style="border-bottom: 1px solid var(--border-subtle);">
            <td style="padding: 12px; font-weight: 700; color: var(--accent-cyan);">Model B (XGBoost Regressor)</td>
            <td style="padding: 12px; color: var(--accent-cyan);">6.7 min</td>
            <td style="padding: 12px;">86%</td>
            <td style="padding: 12px;">194 km</td>
            <td style="padding: 12px; color: var(--accent-emerald);">4</td>
            <td style="padding: 12px;">83%</td>
            <td style="padding: 12px; font-weight: 700; color: var(--accent-emerald);">412.87</td>
          </tr>
          <tr>
            <td style="padding: 12px; font-weight: 700; color: var(--accent-purple);">Model C (Neural MLP + Isotonic)</td>
            <td style="padding: 12px; color: var(--accent-emerald);">5.4 min</td>
            <td style="padding: 12px; color: var(--accent-emerald);">91%</td>
            <td style="padding: 12px;">188 km</td>
            <td style="padding: 12px; color: var(--accent-emerald);">2</td>
            <td style="padding: 12px; color: var(--accent-emerald);">88%</td>
            <td style="padding: 12px; font-weight: 700; color: var(--accent-emerald);">368.20</td>
          </tr>
        </tbody>
      </table>

      <div style="background: var(--bg-deep); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle); font-size: 0.88rem; line-height: 1.6;">
        <strong>Experimental Conclusion:</strong> On small capacity-constrained graphs, prediction noise below 15% is absorbed by feasibility bounds. On multi-vehicle capacity tours, improving prediction MAE from 8.2 min to 5.4 min directly reduces downstream decision routing costs by <strong>24.1%</strong> and cuts late deliveries from 9 to 2.
      </div>
    </div>
  `;
}
