/**
 * Page 2: 3D Spatial Logistics World & Live Dynamic Traffic Adaptation Engine for OPTIMA-X.
 * Interactive spatial canvas rendering node vertices, pickup orders (O1-O8), animated vehicles,
 * and live Traffic Surge Injections (+137%) triggering dynamic A* route recalculations.
 */

import { LogisticsWorld3D } from "../charts/logistics_world_3d";

export function renderWorldPage(isSurgeActive: boolean): string {
  const routeDiffHtml = isSurgeActive
    ? `
    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 14px; padding: 20px; margin-top: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="font-size: 0.8rem; font-weight: 800; color: var(--accent-crimson); text-transform: uppercase;">⚠️ TRAFFIC SURGE EVENT INJECTED</span>
        <span class="status-badge" style="border-color: var(--accent-crimson); color: var(--accent-crimson);">Road B-D +137%</span>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div style="background: var(--bg-deep); padding: 14px; border-radius: 10px; border: 1px solid var(--border-subtle);">
          <div style="font-size: 0.75rem; color: var(--text-subtle); font-weight: 700;">OLD CORRIDOR (BLOCKED BY TRAFFIC)</div>
          <div style="font-size: 1rem; font-weight: 800; color: var(--accent-crimson); margin: 4px 0;">Depot → Node B → Node D → Node E</div>
          <div style="font-size: 0.82rem; color: var(--text-muted);">ETA: <strong style="color: var(--accent-crimson);">27 min</strong> · Late Risk: <strong>61%</strong></div>
        </div>

        <div style="background: var(--bg-deep); padding: 14px; border-radius: 10px; border: 1px solid var(--border-subtle);">
          <div style="font-size: 0.75rem; color: var(--text-subtle); font-weight: 700;">OPTIMA-X REROUTED PATH (ACTIVE)</div>
          <div style="font-size: 1rem; font-weight: 800; color: var(--accent-emerald); margin: 4px 0;">Depot → Node B → Node C → Node E</div>
          <div style="font-size: 0.82rem; color: var(--text-muted);">ETA: <strong style="color: var(--accent-emerald);">21 min (Saved 6 mins)</strong> · Late Risk: <strong>18%</strong></div>
        </div>
      </div>
    </div>
  `
    : `
    <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 14px; padding: 20px; margin-top: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 0.78rem; font-weight: 800; color: var(--accent-cyan); text-transform: uppercase;">Corridor Flow Status</span>
          <h4 style="margin: 4px 0 0; font-size: 1.1rem;">Normal Traffic Baseline (1.0x Multiplier)</h4>
        </div>
        <span class="status-badge"><span class="dot live"></span>Optimal Corridor Flow</span>
      </div>
    </div>
  `;

  return `
    <div style="display: flex; flex-direction: column; gap: 24px;">
      <!-- Header Bar -->
      <div style="background: var(--bg-surface); backdrop-filter: blur(12px); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px; box-shadow: var(--shadow-card); display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-cyan); text-transform: uppercase;">Spatial Environment</span>
          <h2 style="margin: 4px 0 0; font-size: 1.6rem;">3D Spatial Logistics World & Live Rerouting</h2>
        </div>

        <div style="display: flex; gap: 12px;">
          <button id="btn-world-surge" class="btn-danger">INJECT TRAFFIC SURGE (+137%) ⚠️</button>
          <button id="btn-world-reset" class="btn-secondary">RESET CORRIDOR FLOW 🔄</button>
        </div>
      </div>

      <!-- Spatial Canvas -->
      <div class="canvas-container" style="height: 580px;">
        <div class="canvas-overlay-hud">
          <span class="dot live"></span>
          <span>Spatial World Canvas · ${isSurgeActive ? "⚠️ TRAFFIC SURGE DETECTED ON ROAD B-D (+137%)" : "Normal Corridor Flow"}</span>
        </div>
        <canvas id="spatial-world-canvas" class="world-canvas"></canvas>
      </div>

      <!-- Route Diff Inspector -->
      ${routeDiffHtml}
    </div>
  `;
}

export function initWorldPageCanvas(
  isSurgeActive: boolean,
  onSurgeToggle: (active: boolean) => void
): LogisticsWorld3D | null {
  const canvas = document.querySelector<HTMLCanvasElement>("#spatial-world-canvas");
  if (!canvas) return null;

  const viz = new LogisticsWorld3D(canvas);
  if (isSurgeActive) viz.triggerTrafficEvent();
  viz.startAnimation();

  document.querySelector("#btn-world-surge")?.addEventListener("click", () => {
    viz.triggerTrafficEvent();
    onSurgeToggle(true);
  });

  document.querySelector("#btn-world-reset")?.addEventListener("click", () => {
    viz.resetSimulation();
    onSurgeToggle(false);
  });

  return viz;
}
