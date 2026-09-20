/**
 * Page 5: Decision Intelligence & Full Lineage Audit Explorer for OPTIMA-X.
 * Search any Decision ID (e.g., DEC-1042) to inspect its full causal lineage tree,
 * verifiable evidence items, constraint checks, and grounded text explanation.
 */

export function renderDecisionPage(): string {
  return `
    <div style="display: flex; flex-direction: column; gap: 24px;">
      <!-- Header -->
      <div style="background: var(--bg-surface); backdrop-filter: blur(12px); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px; box-shadow: var(--shadow-card); display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-emerald); text-transform: uppercase;">Audit Backbone</span>
          <h2 style="margin: 4px 0 0; font-size: 1.6rem;">Decision Intelligence & Full Lineage Audit Explorer</h2>
        </div>

        <div style="display: flex; gap: 10px; align-items: center;">
          <input id="decision-search-input" type="text" class="form-input" value="DEC-1042" style="width: 160px;" />
          <button id="btn-search-decision" class="btn-primary">INSPECT TRACE</button>
        </div>
      </div>

      <!-- Lineage Tree Visualizer -->
      <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;">
        <h4 style="margin: 0 0 16px; font-size: 1.15rem;">Full Causal Decision Lineage Tree</h4>

        <div class="grid-layout-4col" style="text-align: center;">
          <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.72rem; color: var(--text-subtle); font-weight: 700;">1. DECISION RECORD</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: var(--accent-emerald); margin-top: 4px;">DEC-1042</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">Vehicle Reroute Triggered</div>
          </div>

          <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.72rem; color: var(--text-subtle); font-weight: 700;">2. OPTIMIZATION RUN</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: var(--accent-cyan); margin-top: 4px;">OPT-8812</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">3-Opt + Knapsack DP</div>
          </div>

          <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.72rem; color: var(--text-subtle); font-weight: 700;">3. PREDICTION BUNDLE</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: var(--accent-purple); margin-top: 4px;">P-129, P-130</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">XGBoost ETA v2.1</div>
          </div>

          <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.72rem; color: var(--text-subtle); font-weight: 700;">4. SCENARIO MANIFEST</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: var(--accent-gold); margin-top: 4px;">SCN-2026-00982</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">50 Orders / 10 Vehicles</div>
          </div>
        </div>
      </div>

      <!-- Evidence Items Table -->
      <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;">
        <h4 style="margin: 0 0 16px; font-size: 1.15rem;">Verifiable Evidence Records (Decision #DEC-1042)</h4>

        <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem;">
          <thead>
            <tr style="border-bottom: 1px solid var(--border-subtle); color: var(--text-subtle); text-align: left;">
              <th style="padding: 10px;">Evidence Item</th>
              <th style="padding: 10px;">Source Object</th>
              <th style="padding: 10px;">Before Value</th>
              <th style="padding: 10px;">After Decision Value</th>
              <th style="padding: 10px;">Verification Status</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom: 1px solid var(--border-subtle);">
              <td style="padding: 12px; font-weight: 700;">#E01 Traffic Surge Event</td>
              <td style="padding: 12px; color: var(--accent-cyan);">Edge B-D (RoadGraph)</td>
              <td style="padding: 12px;">1.0x Traffic Factor</td>
              <td style="padding: 12px; color: var(--accent-crimson);">2.37x (+137% Surge)</td>
              <td style="padding: 12px; color: var(--accent-emerald);">✓ VERIFIED</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--border-subtle);">
              <td style="padding: 12px; font-weight: 700;">#E02 Estimated Travel Time</td>
              <td style="padding: 12px; color: var(--accent-cyan);">Prediction P-129</td>
              <td style="padding: 12px; color: var(--accent-crimson);">27 min (Blocked Route)</td>
              <td style="padding: 12px; color: var(--accent-emerald);">21 min (Saved 6 min)</td>
              <td style="padding: 12px; color: var(--accent-emerald);">✓ VERIFIED</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--border-subtle);">
              <td style="padding: 12px; font-weight: 700;">#E03 Customer Late Probability</td>
              <td style="padding: 12px; color: var(--accent-cyan);">Isotonic Classifier</td>
              <td style="padding: 12px; color: var(--accent-gold);">61% Late Risk</td>
              <td style="padding: 12px; color: var(--accent-emerald);">18% Late Risk</td>
              <td style="padding: 12px; color: var(--accent-emerald);">✓ VERIFIED</td>
            </tr>
            <tr>
              <td style="padding: 12px; font-weight: 700;">#E04 Fleet Weight Capacity</td>
              <td style="padding: 12px; color: var(--accent-cyan);">Knapsack DP Constraint</td>
              <td style="padding: 12px;">100.0 kg Limit</td>
              <td style="padding: 12px; color: var(--accent-emerald);">80.0 kg Payload (FEASIBLE)</td>
              <td style="padding: 12px; color: var(--accent-emerald);">✓ VERIFIED</td>
            </tr>
          </tbody>
        </table>

        <div style="margin-top: 20px; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 16px; font-size: 0.88rem; line-height: 1.6;">
          <strong>Evidence-Grounded AI Synthesis:</strong> Decision <code>DEC-1042</code> rerouted Truck A from path <code>Depot → B → D → E</code> to alternative corridor <code>Depot → B → C → E</code> due to a verified 137% congestion surge on segment <code>B-D</code>. This adaptation reduced predicted travel time by 6 minutes, lowered customer late delivery probability from 61% to 18%, and maintained full compliance with Truck A's 100 kg weight capacity constraint.
        </div>
      </div>
    </div>
  `;
}
