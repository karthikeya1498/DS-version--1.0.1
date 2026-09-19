/**
 * Neural Model Topology & Architecture Visualizer for OPTIMA-X.
 * Renders high-precision SVG diagrams for Neural MLP, ExtraTrees, XGBoost, and Random Forest architectures.
 * Uses dynamic CSS variables for theme compatibility and generous 980px viewBox padding to eliminate label clipping.
 */

export class NeuralViewEngine {
  public static renderNeuralTopologySVG(selectedModel: string = "ExtraTrees Regressor"): string {
    const width = 980;
    const height = 340;

    const inputs = ["Distance", "Traffic", "Weather", "Vehicle Load", "Hour of Day", "Demand"];
    const outputs = ["Predicted ETA (min)", "Late Probability P(late)"];

    const xInput = 210;
    const xHidden1 = 430;
    const xHidden2 = 620;
    const xOutput = 810;

    const getInputY = (i: number) => 40 + i * 46;
    const getHidden1Y = (i: number) => 50 + i * 52;
    const getHidden2Y = (i: number) => 70 + i * 56;
    const getOutputY = (i: number) => 100 + i * 90;

    let h1Nodes = ["H1_1", "H1_2", "H1_3", "H1_4", "H1_5"];
    let h2Nodes = ["H2_1", "H2_2", "H2_3", "H2_4"];
    let h1Color = "#8b5cf6";
    let h2Color = "#38bdf8";

    if (selectedModel.includes("ExtraTrees")) {
      h1Nodes = ["Tree_1 (Split)", "Tree_2 (Split)", "Tree_3 (Split)", "Tree_4 (Split)", "Tree_5 (Split)"];
      h2Nodes = ["Leaf_Agg_1", "Leaf_Agg_2", "Leaf_Agg_3", "Leaf_Agg_4"];
      h1Color = "#10b981";
      h2Color = "#38bdf8";
    } else if (selectedModel.includes("XGBoost")) {
      h1Nodes = ["Gradient_1", "Gradient_2", "Gradient_3", "Gradient_4", "Gradient_5"];
      h2Nodes = ["Residual_Boost_1", "Residual_Boost_2", "Residual_Boost_3", "Residual_Boost_4"];
      h1Color = "#38bdf8";
      h2Color = "#f59e0b";
    } else if (selectedModel.includes("Random Forest")) {
      h1Nodes = ["Bootstrap_1", "Bootstrap_2", "Bootstrap_3", "Bootstrap_4", "Bootstrap_5"];
      h2Nodes = ["Forest_Vote_1", "Forest_Vote_2", "Forest_Vote_3", "Forest_Vote_4"];
      h1Color = "#f59e0b";
      h2Color = "#a855f7";
    }

    let linesSvg = "";

    // Connect Inputs to Hidden 1
    inputs.forEach((_, iIdx) => {
      h1Nodes.forEach((_, hIdx) => {
        linesSvg += `<line x1="${xInput}" y1="${getInputY(iIdx)}" x2="${xHidden1}" y2="${getHidden1Y(hIdx)}" stroke="var(--border-glow)" stroke-width="1.3" opacity="0.6" />`;
      });
    });

    // Connect Hidden 1 to Hidden 2
    h1Nodes.forEach((_, h1Idx) => {
      h2Nodes.forEach((_, h2Idx) => {
        linesSvg += `<line x1="${xHidden1}" y1="${getHidden1Y(h1Idx)}" x2="${xHidden2}" y2="${getHidden2Y(h2Idx)}" stroke="var(--accent-purple)" stroke-width="1.3" opacity="0.5" />`;
      });
    });

    // Connect Hidden 2 to Output
    h2Nodes.forEach((_, h2Idx) => {
      outputs.forEach((_, oIdx) => {
        linesSvg += `<line x1="${xHidden2}" y1="${getHidden2Y(h2Idx)}" x2="${xOutput}" y2="${getOutputY(oIdx)}" stroke="var(--accent-emerald)" stroke-width="2.0" opacity="0.7" />`;
      });
    });

    let nodesSvg = "";

    // Inputs (Left align text with generous 192px padding)
    inputs.forEach((label, i) => {
      const y = getInputY(i);
      nodesSvg += `
        <circle cx="${xInput}" cy="${y}" r="9" fill="var(--accent-cyan)" />
        <text x="${xInput - 18}" y="${y + 5}" fill="var(--text-main)" font-size="13" font-weight="800" text-anchor="end">${label}</text>
      `;
    });

    // Hidden 1
    h1Nodes.forEach((label, i) => {
      const y = getHidden1Y(i);
      nodesSvg += `
        <circle cx="${xHidden1}" cy="${y}" r="8" fill="${h1Color}" />
        <text x="${xHidden1}" y="${y - 12}" fill="var(--text-subtle)" font-size="9" font-weight="700" text-anchor="middle">${label}</text>
      `;
    });

    // Hidden 2
    h2Nodes.forEach((label, i) => {
      const y = getHidden2Y(i);
      nodesSvg += `
        <circle cx="${xHidden2}" cy="${y}" r="8" fill="${h2Color}" />
        <text x="${xHidden2}" y="${y - 12}" fill="var(--text-subtle)" font-size="9" font-weight="700" text-anchor="middle">${label}</text>
      `;
    });

    // Outputs (Right align text with 152px padding to right margin)
    outputs.forEach((label, i) => {
      const y = getOutputY(i);
      nodesSvg += `
        <circle cx="${xOutput}" cy="${y}" r="11" fill="var(--accent-emerald)" />
        <text x="${xOutput + 20}" y="${y + 5}" fill="var(--text-main)" font-size="14" font-weight="900">${label}</text>
      `;
    });

    return `
      <div style="background: var(--bg-surface); border: 1.5px solid var(--border-subtle); border-radius: 20px; padding: 24px;" class="ox-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <div>
            <span style="font-size: 0.82rem; font-weight: 800; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 0.05em;">ACTIVE MODEL ARCHITECTURE</span>
            <h4 style="margin: 4px 0 0; font-size: 1.35rem; font-weight: 900; color: var(--text-main);">${selectedModel}</h4>
          </div>
          <span class="status-badge" style="border-color: var(--accent-emerald); color: var(--accent-emerald);"><span class="dot live"></span>Isotonic ECE Calibrated</span>
        </div>

        <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: auto; overflow: visible;">
          ${linesSvg}
          ${nodesSvg}
        </svg>

        <div style="display: flex; justify-content: space-between; margin-top: 18px; font-size: 0.88rem; color: var(--text-muted); border-top: 1.5px solid var(--border-subtle); padding-top: 12px; font-weight: 700;">
          <span>Input Features: <strong>18 Lagged & Rolling Features</strong></span>
          <span>Architecture: <strong>${selectedModel}</strong></span>
          <span>Output: <strong>ETA Forecast + Calibrated Late Risk</strong></span>
        </div>
      </div>
    `;
  }
}
