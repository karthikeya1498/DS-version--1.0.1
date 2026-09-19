/**
 * OPTIMA-X Home Landing Page & Phase Overview.
 * Features 10 interactive hover-up feature cards that elevate on mouse hover.
 */

export interface PhaseCardConfig {
  phase: string;
  title: string;
  icon: string;
  description: string;
  backingEngine: string;
  tabKey: string;
}

export const PHASE_CARDS: PhaseCardConfig[] = [
  {
    phase: "Phase 01",
    title: "Road Graph & Discrete Ingestion",
    icon: "🗺️",
    description: "Spatial road graph parser (OSM/Overpass), Min-Heap priority queues, Dijkstra, Segment & Fenwick Trees.",
    backingEngine: "Adjacency-List RoadGraph + Priority Queue",
    tabKey: "graph",
  },
  {
    phase: "Phase 02",
    title: "ML Demand & ETA Forecasting",
    icon: "📈",
    description: "XGBoost Regressor, Neural MLP, temporal LSTM/GRU, and calibrated late-risk prediction ($P(\\text{late})$).",
    backingEngine: "XGBoost + Platt/Isotonic ECE Calibration",
    tabKey: "forecast",
  },
  {
    phase: "Phase 03",
    title: "Combinatorial VRP Optimization",
    icon: "🧩",
    description: "0/1 Knapsack DP capacity packing, 2-Opt/3-Opt local search, Simulated Annealing, GA, and Google OR-Tools.",
    backingEngine: "Knapsack DP + Local Edge Exchanges",
    tabKey: "optimization",
  },
  {
    phase: "Phase 04",
    title: "Sequential PPO Reinforcement Learning",
    icon: "🤖",
    description: "Gym-compatible LogisticsEnv, PPO Actor-Critic policy, tabular Q-Learning, and Deep Q-Networks (DQN).",
    backingEngine: "PPO Policy + Multi-Agent Dispatch State",
    tabKey: "rl",
  },
  {
    phase: "Phase 05",
    title: "Grounded Decision Intelligence",
    icon: "🛡️",
    description: "Allowlisted tool registry, natural language query parser, counterfactual scenarios, and decision traces.",
    backingEngine: "Guarded Assistant + Structured Evidence",
    tabKey: "assistant",
  },
  {
    phase: "Phase 06",
    title: "Real-Time Telemetry & Control Room",
    icon: "⚡",
    description: "FastAPI REST API, JWT tenant security, live WebSocket re-optimization stream, and interactive dispatch.",
    backingEngine: "FastAPI + WebSocket Broadcast",
    tabKey: "telemetry",
  },
  {
    phase: "Phase 07",
    title: "Research Decision Sensitivity Lab",
    icon: "🔬",
    description: "Controlled prediction noise experiments (±5%, ±15%, ±30%) evaluating ML accuracy vs downstream VRP costs.",
    backingEngine: "Sensitivity Perturbation Engine",
    tabKey: "sensitivity",
  },
  {
    phase: "Phase 08",
    title: "DSA High-Performance Core",
    icon: "⚡",
    description: "Admissible Haversine A*, Segment Tree range speed queries, Binary Indexed Fenwick prefix demand.",
    backingEngine: "Custom C++/Java/Python DSA Layer",
    tabKey: "graph",
  },
  {
    phase: "Phase 09",
    title: "SQL Persistence & Lineage Engine",
    icon: "🗄️",
    description: "SQLAlchemy ORM repository schema, SQLite & PostgreSQL persistence, full decision lineage audit trail.",
    backingEngine: "SQLAlchemy ORM + PostgreSQL DDL",
    tabKey: "telemetry",
  },
  {
    phase: "Phase 10",
    title: "Production Engineering & Guardrails",
    icon: "🔒",
    description: "Strict CORS policies, JWT authentication middleware, tenant rate-limiting, and comprehensive pytest suite.",
    backingEngine: "Production Guardrails & Pytest Harness",
    tabKey: "telemetry",
  },
];

export function renderHomePage(onSelectTab: (tabKey: string) => void): string {
  const cardsHtml = PHASE_CARDS.map(
    (card) => `
    <div class="hover-card" data-tab="${card.tabKey}">
      <div class="card-header">
        <span class="card-phase">${card.phase}</span>
        <div class="card-icon">${card.icon}</div>
      </div>
      <h3 class="card-title">${card.title}</h3>
      <p class="card-desc">${card.description}</p>
      <div class="card-footer">
        <span>${card.backingEngine}</span>
        <span class="card-action">Explore Module →</span>
      </div>
    </div>
  `
  ).join("");

  return `
    <section class="hero-section">
      <span class="hero-eyebrow">OPTIMA-X / ADAPTIVE LOGISTICS ENGINE</span>
      <h1 class="hero-title">Next-Generation Urban Logistics & Decision Intelligence</h1>
      <p class="hero-subtitle">
        Unifying Data Structures & Algorithms, Machine Learning, Combinatorial VRP Optimization, 
        Sequential Reinforcement Learning, and Real-Time WebSocket Telemetry into a state-of-the-art platform.
      </p>

      <div class="metrics-row">
        <div class="metric-box">
          <div class="metric-label">Road Network</div>
          <div class="metric-value">1,482</div>
          <div class="metric-sub">Nodes & Edges</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">Forecasting MAE</div>
          <div class="metric-value">1.42</div>
          <div class="metric-sub">XGBoost & LSTM</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">Routing Speedup</div>
          <div class="metric-value">3.8×</div>
          <div class="metric-sub">Haversine A* vs Dijkstra</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">RL Policy Return</div>
          <div class="metric-value">+0.39</div>
          <div class="metric-sub">PPO Advantage</div>
        </div>
      </div>

      <div class="cards-grid">
        ${cardsHtml}
      </div>
    </section>
  `;
}

export function bindHomePageEvents(onSelectTab: (tabKey: string) => void): void {
  document.querySelectorAll<HTMLElement>(".hover-card").forEach((card) => {
    card.addEventListener("click", () => {
      const tab = card.getAttribute("data-tab");
      if (tab) onSelectTab(tab);
    });
  });
}
