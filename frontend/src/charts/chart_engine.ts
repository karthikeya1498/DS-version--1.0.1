/**
 * High-Tech SVG Chart Engine for OPTIMA-X Phase 2-7 Visualizations.
 * Supports line charts, multi-series bar charts, and ECE calibration curves.
 */

export interface SeriesData {
  name: string;
  color: string;
  values: number[];
}

export interface ChartOptions {
  labels: string[];
  series: SeriesData[];
  title?: string;
  yAxisLabel?: string;
}

export class HighTechChartEngine {
  /**
   * Renders a glowing dark-mode multi-series line chart SVG.
   */
  public static renderLineChart(options: ChartOptions): string {
    const width = 600;
    const height = 300;
    const padding = 50;
    const chartW = width - padding * 2;
    const chartH = height - padding * 2;

    const allValues = options.series.flatMap((s) => s.values);
    const minVal = Math.min(0, ...allValues);
    const maxVal = Math.max(1, ...allValues);

    const getX = (idx: number) =>
      padding + (idx / Math.max(1, options.labels.length - 1)) * chartW;
    const getY = (val: number) =>
      height - padding - ((val - minVal) / Math.max(0.0001, maxVal - minVal)) * chartH;

    let svgLines = "";
    let svgLegend = "";

    options.series.forEach((s, sIdx) => {
      let pathD = "";
      s.values.forEach((v, vIdx) => {
        const x = getX(vIdx);
        const y = getY(v);
        pathD += (vIdx === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
      });

      svgLines += `
        <path d="${pathD}" fill="none" stroke="${s.color}" stroke-width="3" 
              style="filter: drop-shadow(0px 0px 8px ${s.color}aa);" />
      `;

      s.values.forEach((v, vIdx) => {
        const x = getX(vIdx);
        const y = getY(v);
        svgLines += `
          <circle cx="${x}" cy="${y}" r="4" fill="${s.color}" 
                  style="filter: drop-shadow(0px 0px 6px ${s.color});" />
        `;
      });

      svgLegend += `
        <g transform="translate(${padding + sIdx * 140}, 20)">
          <rect width="12" height="12" rx="3" fill="${s.color}" />
          <text x="18" y="10" fill="#94a3b8" font-size="11" font-family="Inter, sans-serif" font-weight="600">${s.name}</text>
        </g>
      `;
    });

    // Grid lines & labels
    let gridSvg = "";
    options.labels.forEach((label, idx) => {
      const x = getX(idx);
      gridSvg += `
        <line x1="${x}" y1="${padding}" x2="${x}" y2="${height - padding}" stroke="rgba(255,255,255,0.06)" stroke-dasharray="4" />
        <text x="${x}" y="${height - padding + 18}" fill="#64748b" font-size="10" text-anchor="middle" font-family="Inter, sans-serif">${label}</text>
      `;
    });

    return `
      <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: auto; background: rgba(9,13,22,0.6); border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
        ${svgLegend}
        ${gridSvg}
        ${svgLines}
      </svg>
    `;
  }

  /**
   * Renders a sleek multi-series bar chart SVG.
   */
  public static renderBarChart(options: ChartOptions): string {
    const width = 600;
    const height = 300;
    const padding = 50;
    const chartW = width - padding * 2;
    const chartH = height - padding * 2;

    const allValues = options.series.flatMap((s) => s.values);
    const maxVal = Math.max(1, ...allValues);

    const groupWidth = chartW / options.labels.length;
    const barWidth = Math.min(30, (groupWidth * 0.7) / options.series.length);

    let barsSvg = "";
    let legendSvg = "";

    options.series.forEach((s, sIdx) => {
      s.values.forEach((v, vIdx) => {
        const groupX = padding + vIdx * groupWidth;
        const barX = groupX + (groupWidth - barWidth * options.series.length) / 2 + sIdx * barWidth;
        const barH = (v / maxVal) * chartH;
        const barY = height - padding - barH;

        barsSvg += `
          <rect x="${barX}" y="${barY}" width="${barWidth - 4}" height="${barH}" rx="4" 
                fill="${s.color}" style="filter: drop-shadow(0px 0px 8px ${s.color}66);" />
          <text x="${barX + (barWidth - 4) / 2}" y="${barY - 6}" fill="#f8fafc" font-size="9" 
                font-family="Inter, sans-serif" text-anchor="middle" font-weight="700">${v.toFixed(1)}</text>
        `;
      });

      legendSvg += `
        <g transform="translate(${padding + sIdx * 120}, 20)">
          <rect width="12" height="12" rx="3" fill="${s.color}" />
          <text x="18" y="10" fill="#94a3b8" font-size="11" font-family="Inter, sans-serif" font-weight="600">${s.name}</text>
        </g>
      `;
    });

    // Labels
    let labelsSvg = "";
    options.labels.forEach((label, idx) => {
      const groupX = padding + idx * groupWidth + groupWidth / 2;
      labelsSvg += `
        <text x="${groupX}" y="${height - padding + 20}" fill="#64748b" font-size="11" 
              font-family="Inter, sans-serif" text-anchor="middle" font-weight="600">${label}</text>
      `;
    });

    return `
      <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: auto; background: rgba(9,13,22,0.6); border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
        ${legendSvg}
        ${barsSvg}
        ${labelsSvg}
      </svg>
    `;
  }
}
