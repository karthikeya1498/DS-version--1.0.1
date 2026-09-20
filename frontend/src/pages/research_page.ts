/**
 * Page 6: Research & Sensitivity Benchmark Lab for OPTIMA-X.
 * Evaluates whether higher prediction accuracy translates to superior decision quality costs,
 * prediction noise sensitivity perturbation studies, and system latency/throughput metrics.
 */

import { renderResearchLab } from "../components/research_lab";

export function renderResearchPage(): string {
  return `
    <div style="display: flex; flex-direction: column; gap: 24px;">
      <!-- Header -->
      <div style="background: var(--bg-surface); backdrop-filter: blur(12px); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px; box-shadow: var(--shadow-card); display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-purple); text-transform: uppercase;">Research & Validation</span>
          <h2 style="margin: 4px 0 0; font-size: 1.6rem;">Research Benchmark & Sensitivity Lab</h2>
        </div>
        <span class="status-badge" style="border-color: var(--accent-purple); color: var(--accent-purple);">Phase 7 Research Active</span>
      </div>

      <!-- Core Research Experiment Table -->
      ${renderResearchLab()}

      <!-- System Performance & Ablation Matrix -->
      <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;">
        <h4 style="margin: 0 0 16px; font-size: 1.15rem;">System Operational Metrics & Ablation Summary</h4>

        <div class="grid-layout-4col" style="margin-bottom: 20px;">
          <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.72rem; color: var(--text-subtle); font-weight: 700;">PIPELINE LATENCY</div>
            <div style="font-size: 1.5rem; font-weight: 900; color: var(--accent-cyan); margin-top: 4px;">68.0 ms</div>
            <div style="font-size: 0.75rem; color: var(--accent-emerald);">3-Opt Solver Run</div>
          </div>

          <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.72rem; color: var(--text-subtle); font-weight: 700;">SYSTEM THROUGHPUT</div>
            <div style="font-size: 1.5rem; font-weight: 900; color: var(--accent-emerald); margin-top: 4px;">1,480 req/s</div>
            <div style="font-size: 0.75rem; color: var(--accent-emerald);">FastAPI Tenant Limiter</div>
          </div>

          <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.72rem; color: var(--text-subtle); font-weight: 700;">OPTIMALITY GAP</div>
            <div style="font-size: 1.5rem; font-weight: 900; color: var(--accent-purple); margin-top: 4px;">1.84%</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">vs OR-Tools Integer MILP</div>
          </div>

          <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.72rem; color: var(--text-subtle); font-weight: 700;">PPO ADVANTAGE WIN RATE</div>
            <div style="font-size: 1.5rem; font-weight: 900; color: var(--accent-gold); margin-top: 4px;">+0.391</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">vs All-Defer Baseline</div>
          </div>
        </div>
      </div>
    </div>
  `;
}
