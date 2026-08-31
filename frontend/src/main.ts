/**
 * OPTIMA-X operations dashboard entry point.
 *
 * Author: Karthikeya
 * The dashboard is dependency-light and uses the FastAPI REST and WebSocket
 * contracts directly so local operations remain easy to reproduce.
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

type TrafficEvent = {
  event_type: 'connected' | 'heartbeat' | 'route_reoptimization';
  timestamp?: string;
  tenant_id?: string;
  payload?: {
    tenant_id: string;
    zone_id: string;
    multiplier: number;
    affected_vehicle_ids: string[];
    action: string;
  };
};

type TokenResponse = { access_token: string };

const API_ORIGIN = import.meta.env.VITE_API_ORIGIN ?? 'http://localhost:8000';
const API_URL = `${API_ORIGIN}/api/v1/simulation/run`;
const TOKEN_URL = `${API_ORIGIN}/api/v1/auth/token`;
const WS_URL = `${API_ORIGIN.replace(/^http/, 'ws')}/api/v1/ws/traffic`;
const app = document.querySelector<HTMLDivElement>('#app');

if (!app) throw new Error('OPTIMA-X dashboard mount element was not found.');

app.innerHTML = `
  <main class="shell">
    <header class="hero">
      <div>
        <p class="eyebrow">OPTIMA-X / PHASE 5</p>
        <h1>Adaptive logistics intelligence.</h1>
        <p class="lede">Forecast demand, dispatch vehicles, and inspect reproducible decisions from one operational view.</p>
      </div>
      <div class="status-pill"><span id="connection-dot" class="status-dot"></span><span id="connection-state">Connecting</span></div>
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
    <section class="panel live-panel"><div class="panel-heading"><div><p class="panel-kicker">LIVE TRAFFIC STREAM</p><h2>Route re-optimization events</h2></div><span id="event-count" class="request-state">0 events</span></div><p id="traffic-empty" class="empty-state">Waiting for traffic updates from the FastAPI WebSocket.</p><ol id="traffic-events" class="traffic-events" aria-live="polite"></ol></section>
    <footer><span>Python orchestration</span><span>Java DSA</span><span>SQL persistence</span><span>Live WebSocket telemetry</span></footer>
  </main>`;

const runButton = document.querySelector<HTMLButtonElement>('#run');
const output = document.querySelector<HTMLElement>('#output');
const requestState = document.querySelector<HTMLElement>('#request-state');
const orders = document.querySelector<HTMLElement>('#orders');
const served = document.querySelector<HTMLElement>('#served');
const cost = document.querySelector<HTMLElement>('#cost');
const connectionState = document.querySelector<HTMLElement>('#connection-state');
const connectionDot = document.querySelector<HTMLElement>('#connection-dot');
const trafficEvents = document.querySelector<HTMLOListElement>('#traffic-events');
const trafficEmpty = document.querySelector<HTMLElement>('#traffic-empty');
const eventCount = document.querySelector<HTMLElement>('#event-count');
let receivedEvents = 0;
let reconnectTimer: number | undefined;

const setState = (state: string): void => {
  if (requestState) requestState.textContent = state;
};

const setConnectionState = (state: string, healthy: boolean): void => {
  if (connectionState) connectionState.textContent = state;
  connectionDot?.classList.toggle('status-dot-live', healthy);
};

const renderMetrics = (metrics: SimulationMetrics): void => {
  if (orders) orders.textContent = String(metrics.total_orders);
  if (served) served.textContent = String(metrics.delivered_orders);
  if (cost) cost.textContent = metrics.total_cost.toFixed(2);
};

const appendTrafficEvent = (event: TrafficEvent): void => {
  if (!trafficEvents || !event.payload) return;
  receivedEvents += 1;
  if (trafficEmpty) trafficEmpty.hidden = true;
  if (eventCount) eventCount.textContent = `${receivedEvents} event${receivedEvents === 1 ? '' : 's'}`;
  const item = document.createElement('li');
  const affectedVehicles = event.payload.affected_vehicle_ids.join(', ') || 'none';
  item.innerHTML = `<strong>${event.payload.zone_id}</strong><span>${event.payload.multiplier.toFixed(2)}× traffic multiplier · vehicles ${affectedVehicles}</span><time>${new Date(event.timestamp ?? Date.now()).toLocaleTimeString()}</time>`;
  trafficEvents.prepend(item);
  while (trafficEvents.children.length > 8) trafficEvents.lastElementChild?.remove();
};

const fetchToken = async (): Promise<string> => {
  const response = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ username: 'dashboard', password: 'development', tenant_id: 'dashboard' }),
  });
  if (!response.ok) throw new Error(`Token request returned HTTP ${response.status}`);
  return ((await response.json()) as TokenResponse).access_token;
};

const connectTrafficStream = async (): Promise<void> => {
  try {
    const token = await fetchToken();
    const socket = new WebSocket(`${WS_URL}?token=${encodeURIComponent(token)}`);
    setConnectionState('Connecting', false);
    socket.addEventListener('open', () => setConnectionState('Live', true));
    socket.addEventListener('message', (message) => {
      const event = JSON.parse(message.data as string) as TrafficEvent;
      if (event.event_type === 'route_reoptimization') appendTrafficEvent(event);
    });
    socket.addEventListener('close', () => {
      setConnectionState('Reconnecting', false);
      reconnectTimer = window.setTimeout(() => void connectTrafficStream(), 3000);
    });
    socket.addEventListener('error', () => setConnectionState('Unavailable', false));
  } catch {
    setConnectionState('Unavailable', false);
    reconnectTimer = window.setTimeout(() => void connectTrafficStream(), 3000);
  }
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
void connectTrafficStream();

window.addEventListener('beforeunload', () => {
  if (reconnectTimer !== undefined) window.clearTimeout(reconnectTimer);
});
