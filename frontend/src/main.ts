/**
 * OPTIMA-X operations dashboard entry point.
 *
 * Author: Karthikeya
 * The dashboard is intentionally dependency-light so it can run alongside the
 * FastAPI service during local development and remain easy to deploy.
 */

import './style.css';

type SimulationMetrics = {
  total_orders: number;
  delivered_orders: number;
  total_cost: number;
};

type SimulationResponse = {
  metrics: SimulationMetrics;
  [key: string]: unknown;
};

const API_URL = 'http://localhost:8000/api/v1/simulation/run';
const app = document.querySelector<HTMLDivElement>('#app');

if (!app) {
  throw new Error('OPTIMA-X dashboard mount element was not found.');
}

app.innerHTML = `
  <main class="shell">
    <header class="hero">
      <div>
        <p class="eyebrow">OPTIMA-X / PHASE 5</p>
        <h1>Adaptive logistics intelligence.</h1>
        <p class="lede">Forecast demand, dispatch vehicles, and inspect reproducible decisions from one operational view.</p>
      </div>
      <div class="status-pill"><span class="status-dot"></span>System ready</div>
    </header>
    <section class="metric-grid" aria-label="Scenario metrics">
      <article class="metric-card"><span>Total orders</span><strong id="orders">—</strong><small>generated in scenario</small></article>
      <article class="metric-card"><span>Delivered</span><strong id="served">—</strong><small>completed deliveries</small></article>
      <article class="metric-card"><span>Baseline cost</span><strong id="cost">—</strong><small>routing objective</small></article>
    </section>
    <section class="workspace">
      <div class="panel panel-primary">
        <div class="panel-heading"><div><p class="panel-kicker">CONTROL ROOM</p><h2>Run a seeded scenario</h2></div><span class="seed-label">seed 42</span></div>
        <p>Execute the same two-hour scenario used by the integration test suite and compare the returned decision record.</p>
        <button id="run" type="button">Run scenario <span aria-hidden="true">↗</span></button>
      </div>
      <div class="panel output-panel"><div class="panel-heading"><div><p class="panel-kicker">DECISION TRACE</p><h2>Latest response</h2></div><span id="request-state" class="request-state">Idle</span></div><pre id="output" aria-live="polite">Ready for a reproducible run.</pre></div>
    </section>
    <footer><span>Python orchestration</span><span>•</span><span>Java DSA</span><span>•</span><span>SQL persistence</span></footer>
  </main>`;

const runButton = document.querySelector<HTMLButtonElement>('#run');
const output = document.querySelector<HTMLElement>('#output');
const requestState = document.querySelector<HTMLElement>('#request-state');
const orders = document.querySelector<HTMLElement>('#orders');
const served = document.querySelector<HTMLElement>('#served');
const cost = document.querySelector<HTMLElement>('#cost');

const setState = (state: string): void => {
  if (requestState) requestState.textContent = state;
};

const renderMetrics = (metrics: SimulationMetrics): void => {
  if (orders) orders.textContent = String(metrics.total_orders);
  if (served) served.textContent = String(metrics.delivered_orders);
  if (cost) cost.textContent = metrics.total_cost.toFixed(2);
};

const runScenario = async (): Promise<void> => {
  if (!runButton || !output) return;
  runButton.disabled = true;
  setState('Running');
  output.textContent = 'Requesting simulation metrics…';

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ seed: 42, duration_hours: 2, zones: 3, vehicles: 4, orders_per_hour: 3 }),
    });
    if (!response.ok) throw new Error(`API returned HTTP ${response.status}`);
    const data = (await response.json()) as SimulationResponse;
    renderMetrics(data.metrics);
    output.textContent = JSON.stringify(data, null, 2);
    setState('Complete');
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown request failure';
    output.textContent = `${message}\n\nStart the FastAPI service on localhost:8000 and run again.`;
    setState('Unavailable');
  } finally {
    runButton.disabled = false;
  }
};

runButton?.addEventListener('click', () => void runScenario());
