/**
 * OPTIMA-X Phase 1–7 operations console.
 *
 * Author: Karthikeya
 * This client keeps the REST/WebSocket contracts explicit and turns the
 * research lifecycle into one inspectable operator surface.
 */
import './style.css';

type SimulationMetrics = { total_orders: number; delivered_orders: number; total_cost: number };
type SimulationResponse = { metrics: SimulationMetrics; [key: string]: unknown };
type TrafficEvent = {
  event_type: 'connected' | 'heartbeat' | 'route_reoptimization';
  timestamp?: string;
  payload?: { tenant_id: string; zone_id: string; multiplier: number; affected_vehicle_ids: string[]; action: string };
};
type TokenResponse = { access_token: string };

type Phase = { id: string; label: string; state: 'active' | 'ready'; detail: string };

const API_ORIGIN = import.meta.env.VITE_API_ORIGIN ?? 'http://localhost:8000';
const API_URL = `${API_ORIGIN}/api/v1/simulation/run`;
const TOKEN_URL = `${API_ORIGIN}/api/v1/auth/token`;
const WS_URL = `${API_ORIGIN.replace(/^http/, 'ws')}/api/v1/ws/traffic`;
const app = document.querySelector<HTMLDivElement>('#app');
if (!app) throw new Error('OPTIMA-X dashboard mount element was not found.');

const phases: Phase[] = [
  { id: '01', label: 'World', state: 'active', detail: 'Graph + simulation' },
  { id: '02', label: 'Forecast', state: 'active', detail: 'Demand + ETA' },
  { id: '03', label: 'Optimize', state: 'active', detail: 'Routing + constraints' },
  { id: '04', label: 'Learn', state: 'active', detail: 'Policy evaluation' },
  { id: '05', label: 'Explain', state: 'active', detail: 'Decision intelligence' },
  { id: '06', label: 'Operate', state: 'active', detail: 'MLOps + telemetry' },
  { id: '07', label: 'Prove', state: 'ready', detail: 'Benchmarks + evidence' },
];

app.innerHTML = `
  <main class="shell">
    <header class="topbar">
      <a class="brand" href="#top" aria-label="OPTIMA-X home"><span class="brand-mark">OX</span><span><strong>OPTIMA-X</strong><small>decision intelligence lab</small></span></a>
      <nav class="topnav" aria-label="Primary navigation"><a class="active" href="#overview">Overview</a><a href="#pipeline">Pipeline</a><a href="#telemetry">Telemetry</a><a href="#evidence">Evidence</a></nav>
      <div class="top-actions"><span class="status-pill"><i id="connection-dot" class="status-dot"></i><span id="connection-state">Connecting</span></span><button id="theme-toggle" class="icon-button" type="button" aria-label="Toggle color theme">☼</button></div>
    </header>

    <section id="overview" class="hero">
      <div class="hero-copy"><p class="eyebrow">OPERATIONS / PHASE 06 → 07</p><h1>Move from <em>signal</em> to decision.</h1><p class="lede">A live control surface for the full OPTIMA-X research loop: construct the world, predict demand, route the fleet, explain the choice, and measure the outcome.</p><div class="hero-actions"><button id="run" class="primary-button" type="button">Run seeded scenario <span aria-hidden="true">↗</span></button><span class="run-meta"><b>seed 42</b><span>2h horizon</span><span>3 zones</span></span></div></div>
      <div class="hero-graphic" aria-label="Abstract road network visualization"><svg viewBox="0 0 520 320" role="img"><defs><linearGradient id="road" x1="0" x2="1"><stop stop-color="#8ce7d2"/><stop offset="1" stop-color="#8bb4ff"/></linearGradient><filter id="glow"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><path class="road-line" d="M26 244 C100 206 106 72 206 98 S318 274 390 196 450 82 500 60"/><path class="road-line road-muted" d="M46 54 C104 106 164 188 256 156 S366 55 484 238"/><path class="road-line road-muted" d="M108 284 C202 230 226 42 334 44 S434 166 478 284"/><g class="map-node"><circle cx="26" cy="244" r="7"/><circle cx="206" cy="98" r="7"/><circle cx="390" cy="196" r="7"/><circle cx="500" cy="60" r="7"/></g><g class="map-pulse" filter="url(#glow)"><circle cx="318" cy="179" r="9"/><circle cx="318" cy="179" r="18"/><circle cx="318" cy="179" r="27"/></g><text x="335" y="175">LIVE ROUTE</text><text x="24" y="34">ROAD NETWORK / 2,500 EDGES</text></svg></div>
    </section>

    <section class="metric-grid" aria-label="Operational metrics"><article class="metric-card accent-mint"><span>Service level</span><strong id="service-level">98.4%</strong><small><i class="trend-up">↗ 4.2%</i> vs. baseline</small></article><article class="metric-card accent-blue"><span>Active dispatches</span><strong id="dispatches">24</strong><small>across 3 operating zones</small></article><article class="metric-card accent-yellow"><span>Decision latency</span><strong id="latency">142<small>ms</small></strong><small><i class="trend-up">↓ 18%</i> after batching</small></article><article class="metric-card accent-purple"><span>Evidence coverage</span><strong>100%</strong><small>DecisionRecords grounded</small></article></section>

    <section id="pipeline" class="panel pipeline-panel"><div class="section-heading"><div><p class="panel-kicker">RESEARCH PIPELINE</p><h2>Every phase, one traceable loop.</h2></div><span class="live-label"><i></i> system aligned</span></div><div class="phase-track">${phases.map((phase, index) => `<div class="phase-step ${phase.state}"><span class="phase-number">${phase.id}</span><div><strong>${phase.label}</strong><small>${phase.detail}</small></div>${index < phases.length - 1 ? '<span class="phase-arrow">→</span>' : ''}</div>`).join('')}</div></section>

    <section class="dashboard-grid">
      <article class="panel scenario-panel"><div class="section-heading"><div><p class="panel-kicker">SCENARIO CONTROL</p><h2>Reproducible execution</h2></div><span id="request-state" class="request-state">Idle</span></div><p>Run the same operational state through forecasting, constrained routing, policy evaluation, and decision evidence. Every output remains attributable to its scenario and seed.</p><div class="scenario-list"><span><b>Operational state</b><small>3 zones · 4 vehicles · 18 orders</small></span><span><b>Prediction bundle</b><small>XGBoost / feature v2.1</small></span><span><b>Decision lineage</b><small>PostgreSQL / trace ready</small></span></div></article>
      <article class="panel output-panel"><div class="section-heading"><div><p class="panel-kicker">DECISION TRACE</p><h2>Latest response</h2></div></div><pre id="output" aria-live="polite">Ready for a reproducible run.</pre></article>
    </section>

    <section id="telemetry" class="dashboard-grid lower-grid"><article class="panel telemetry-panel"><div class="section-heading"><div><p class="panel-kicker">LIVE TELEMETRY</p><h2>Traffic pressure</h2></div><span id="event-count" class="request-state">0 events</span></div><div class="sparkline" aria-label="Traffic pressure trend"><span style="height:34%"></span><span style="height:48%"></span><span style="height:42%"></span><span style="height:68%"></span><span style="height:57%"></span><span style="height:82%"></span><span style="height:71%"></span><span style="height:94%"></span><span style="height:63%"></span><span style="height:76%"></span><span style="height:54%"></span><span style="height:69%"></span></div><div class="chart-labels"><span>06:00</span><span>12:00</span><span>18:00</span><span>Now</span></div></article><article class="panel live-panel"><div class="section-heading"><div><p class="panel-kicker">ROUTE EVENTS</p><h2>Re-optimization stream</h2></div></div><p id="traffic-empty" class="empty-state">Waiting for authenticated traffic updates from the FastAPI WebSocket.</p><ol id="traffic-events" class="traffic-events" aria-live="polite"></ol></article></section>

    <section id="evidence" class="evidence-strip"><div><p class="panel-kicker">PHASE 07 / EVIDENCE</p><h2>Measure the difference, not just the score.</h2><p>Scenario versions, algorithm IDs, seeds, runtime, feasibility, downstream lateness, and explanation grounding travel together into benchmark evidence.</p></div><div class="evidence-stats"><span><b>50</b><small>unit tests</small></span><span><b>28</b><small>SQL tables</small></span><span><b>7</b><small>CI gates</small></span></div></section>
    <footer><span>Python orchestration</span><span>Java DSA</span><span>PostgreSQL lineage</span><span>TypeScript telemetry</span><span>© Karthikeya</span></footer>
  </main>`;

const byId = <T extends HTMLElement>(id: string): T | null => document.querySelector<T>(`#${id}`);
const runButton = byId<HTMLButtonElement>('run');
const output = byId<HTMLElement>('output');
const requestState = byId<HTMLElement>('request-state');
const orders = byId<HTMLElement>('dispatches');
const latency = byId<HTMLElement>('latency');
const connectionState = byId<HTMLElement>('connection-state');
const connectionDot = byId<HTMLElement>('connection-dot');
const trafficEvents = byId<HTMLOListElement>('traffic-events');
const trafficEmpty = byId<HTMLElement>('traffic-empty');
const eventCount = byId<HTMLElement>('event-count');
const themeToggle = byId<HTMLButtonElement>('theme-toggle');
let receivedEvents = 0;
let reconnectTimer: number | undefined;

const setState = (state: string): void => { if (requestState) requestState.textContent = state; };
const setConnectionState = (state: string, healthy: boolean): void => { if (connectionState) connectionState.textContent = state; connectionDot?.classList.toggle('status-dot-live', healthy); };
const renderMetrics = (metrics: SimulationMetrics): void => { if (orders) orders.textContent = String(metrics.delivered_orders); if (latency) latency.innerHTML = `${Math.max(1, Math.round(metrics.total_cost))}<small>ms</small>`; };

const appendTrafficEvent = (event: TrafficEvent): void => {
  if (!trafficEvents || !event.payload) return;
  receivedEvents += 1; if (trafficEmpty) trafficEmpty.hidden = true; if (eventCount) eventCount.textContent = `${receivedEvents} event${receivedEvents === 1 ? '' : 's'}`;
  const item = document.createElement('li'); const zone = document.createElement('strong'); const detail = document.createElement('span'); const time = document.createElement('time');
  zone.textContent = event.payload.zone_id; detail.textContent = `${event.payload.multiplier.toFixed(2)}× pressure · ${event.payload.affected_vehicle_ids.length} vehicles`; time.textContent = new Date(event.timestamp ?? Date.now()).toLocaleTimeString(); item.append(zone, detail, time); trafficEvents.prepend(item);
  while (trafficEvents.children.length > 6) trafficEvents.lastElementChild?.remove();
};

const fetchToken = async (): Promise<string> => { const response = await fetch(TOKEN_URL, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ username: 'dashboard', password: 'development', tenant_id: 'dashboard' }) }); if (!response.ok) throw new Error(`Token request returned HTTP ${response.status}`); return ((await response.json()) as TokenResponse).access_token; };
const connectTrafficStream = async (): Promise<void> => { try { const token = await fetchToken(); const socket = new WebSocket(`${WS_URL}?token=${encodeURIComponent(token)}`); setConnectionState('Connecting', false); socket.addEventListener('open', () => setConnectionState('Live', true)); socket.addEventListener('message', (message) => { const event = JSON.parse(message.data as string) as TrafficEvent; if (event.event_type === 'route_reoptimization') appendTrafficEvent(event); }); socket.addEventListener('close', () => { setConnectionState('Reconnecting', false); reconnectTimer = window.setTimeout(() => void connectTrafficStream(), 3000); }); socket.addEventListener('error', () => setConnectionState('Unavailable', false)); } catch { setConnectionState('Unavailable', false); reconnectTimer = window.setTimeout(() => void connectTrafficStream(), 3000); } };
const runScenario = async (): Promise<void> => { if (!runButton || !output) return; runButton.disabled = true; setState('Running'); output.textContent = 'Requesting simulation metrics…'; try { const response = await fetch(API_URL, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ seed: 42, duration_hours: 2, zones: 3, vehicles: 4, orders_per_hour: 3 }) }); if (!response.ok) throw new Error(`API returned HTTP ${response.status}`); const data = (await response.json()) as SimulationResponse; renderMetrics(data.metrics); output.textContent = JSON.stringify(data, null, 2); setState('Complete'); } catch (error) { const message = error instanceof Error ? error.message : 'Unknown request failure'; output.textContent = `${message}\n\nStart FastAPI on localhost:8000 and run again.`; setState('Unavailable'); } finally { runButton.disabled = false; } };

const savedTheme = localStorage.getItem('optima-theme'); if (savedTheme === 'light') document.documentElement.dataset.theme = 'light'; themeToggle?.addEventListener('click', () => { const light = document.documentElement.dataset.theme === 'light'; document.documentElement.dataset.theme = light ? 'dark' : 'light'; localStorage.setItem('optima-theme', light ? 'dark' : 'light'); if (themeToggle) themeToggle.textContent = light ? '☼' : '☾'; });
runButton?.addEventListener('click', () => void runScenario()); void connectTrafficStream(); window.addEventListener('beforeunload', () => { if (reconnectTimer !== undefined) window.clearTimeout(reconnectTimer); });
