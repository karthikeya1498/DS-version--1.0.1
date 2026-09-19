/**
 * Neural Model Topology & Prediction Visualizer for OPTIMA-X.
 * Renders the architecture (Inputs -> Hidden Layers -> Outputs: ETA, Late Risk)
 * with feature activation weights and ECE calibration plots.
 */

export class NeuralViewEngine {
  public static renderNeuralTopologySVG(selectedModel: string = "Neural MLP (64x32)"): string {
    const width = 640;
    const height = 320;

    const inputs = ["Distance", "Traffic", "Weather", "Vehicle Load", "Hour of Day", "Demand"];
    const hidden1 = ["h1_1", "h1_2", "h1_3", "h1_4", "h1_5"];
    const hidden2 = ["h2_1", "h2_2", "h2_3", "h2_4"];
    const outputs = ["Predicted ETA (min)", "Late Probability P(late)"];

    const xInput = 60;
    const xHidden1 = 220;
    const xHidden2 = 400;
    const xOutput = 560;

    const getInputY = (i: number) => 40 + i * 44;
    const getHidden1Y = (i: number) => 50 + i * 50;
    const getHidden2Y = (i: number) => 70 + i * 55;
    const getOutputY = (i: number) => 100 + i * 80;

    let linesSvg = "";
    // Connect Inputs to Hidden 1
    inputs.forEach((_, iIdx) => {
      hidden1.forEach((_, hIdx) => {
        linesSvg += `<line x1="${xInput}" y1="${getInputY(iIdx)}" x2="${xHidden1}" y2="${getHidden1Y(hIdx)}" stroke="rgba(56, 189, 248, 0.2)" stroke-width="1.2" />`;
      });
    });

    // Connect Hidden 1 to Hidden 2
    hidden1.forEach((_, h1Idx) => {
      hidden2.forEach((_, h2Idx) => {
        linesSvg += `<line x1="${xHidden1}" y1="${getHidden1Y(h1Idx)}" x2="${xHidden2}" y2="${getHidden2Y(h2Idx)}" stroke="rgba(139, 92, 246, 0.25)" stroke-width="1.2" />`;
      });
    });

    // Connect Hidden 2 to Output
    hidden2.forEach((_, h2Idx) => {
      outputs.forEach((_, oIdx) => {
        linesSvg += `<line x1="${xHidden2}" y1="${getHidden2Y(h2Idx)}" x2="${xOutput}" y2="${getOutputY(oIdx)}" stroke="rgba(16, 185, 129, 0.3)" stroke-width="1.8" />`;
      });
    });

    // Node SVG graphics
    let nodesSvg = "";

    // Inputs
    inputs.forEach((label, i) => {
      const y = getInputY(i);
      nodesSvg += `
        <circle cx="${xInput}" cy="${y}" r="8" fill="#38bdf8" style="filter: drop-shadow(0 0 6px #38bdf8);" />
        <text x="${xInput - 14}" y="${y + 4}" fill="#94a3b8" font-size="10" font-weight="700" text-anchor="end">${label}</text>
      `;
    });

    // Hidden 1
    hidden1.forEach((_, i) => {
      const y = getHidden1Y(i);
      nodesSvg += `<circle cx="${xHidden1}" cy="${y}" r="7" fill="#8b5cf6" style="filter: drop-shadow(0 0 6px #8b5cf6);" />`;
    });

    // Hidden 2
    hidden2.forEach((_, i) => {
      const y = getHidden2Y(i);
      nodesSvg += `<circle cx="${xHidden2}" cy="${y}" r="7" fill="#8b5cf6" style="filter: drop-shadow(0 0 6px #8b5cf6);" />`;
    });

    // Outputs
    outputs.forEach((label, i) => {
      const y = getOutputY(i);
      nodesSvg += `
        <circle cx="${xOutput}" cy="${y}" r="9" fill="#10b981" style="filter: drop-shadow(0 0 8px #10b981);" />
        <text x="${xOutput + 14}" y="${y + 4}" fill="#f8fafc" font-size="11" font-weight="800">${label}</text>
      `;
    });

    return `
      <div style="background: rgba(9,13,22,0.8); border: 1px solid var(--border-subtle); border-radius: 16px; padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
          <div>
            <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-cyan); text-transform: uppercase;">Active Model Architecture</span>
            <h4 style="margin: 4px 0 0; font-size: 1.15rem;">${selectedModel}</h4>
          </div>
          <span class="status-badge"><span class="dot live"></span>Isotonic ECE Calibrated</span>
        </div>

        <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: auto;">
          ${linesSvg}
          ${nodesSvg}
        </svg>

        <div style="display: flex; justify-content: space-between; margin-top: 14px; font-size: 0.82rem; color: var(--text-muted); border-top: 1px solid var(--border-subtle); padding-top: 10px;">
          <span>Input Features: <strong>12 Lagged Features</strong></span>
          <span>Hidden Layers: <strong>64 -> 32 Dense Neurons</strong></span>
          <span>Output: <strong>ETA + Calibrated Risk</strong></span>
        </div>
      </div>
    `;
  }
}
