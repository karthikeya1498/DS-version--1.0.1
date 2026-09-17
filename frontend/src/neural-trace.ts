/** Real neural activation visualization for OPTIMA-X.
 * Author: Karthikeya
 */
export type NeuralLayer = { name: string; units: number; activation: number[] };
export type NeuralTrace = {
  feature_vector: number[];
  scaled_input: number[];
  layers: NeuralLayer[];
  weights: Array<{ layer: number; weight: number[][]; bias: number[] }>;
  prediction: number;
  target: string;
};

const valueColor = (value: number): string => value >= 0 ? 'var(--mint)' : 'var(--purple)';
const format = (value: number): string => value.toFixed(3);

export const renderNeuralTrace = (host: HTMLElement, trace: NeuralTrace): void => {
  host.replaceChildren();
  const graph = document.createElement('div');
  graph.className = 'neural-graph';
  trace.layers.forEach((layer, layerIndex) => {
    const column = document.createElement('div');
    column.className = 'neural-layer';
    const title = document.createElement('strong');
    title.textContent = layer.name.replace('_', ' ');
    column.append(title);
    const units = document.createElement('div');
    units.className = 'neural-units';
    layer.activation.forEach((activation, unitIndex) => {
      const unit = document.createElement('span');
      unit.className = 'neural-unit';
      unit.style.setProperty('--activation', String(Math.min(1, Math.abs(activation) / 2)));
      unit.style.background = valueColor(activation);
      unit.title = `${layer.name}[${unitIndex}] = ${format(activation)}`;
      unit.textContent = unitIndex < 8 ? format(activation) : '…';
      unit.style.animationDelay = `${(layerIndex * 90) + unitIndex * 25}ms`;
      units.append(unit);
    });
    column.append(units);
    graph.append(column);
  });
  const footer = document.createElement('div');
  footer.className = 'neural-result';
  footer.innerHTML = `<span>features <b>${trace.feature_vector.map(format).join(' · ')}</b></span><span>prediction <b>${format(trace.prediction)} ${trace.target}</b></span>`;
  host.append(graph, footer);
};
