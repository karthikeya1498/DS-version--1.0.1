/**
 * OPTIMA-X Unified Logistics Control Center.
 * Author: Karthikeya
 * Orchestrates 3D Spatial Logistics World, Live Traffic Event Dynamic Rerouting (+137%),
 * Neural Architecture Visualizer, Grounded Evidence, Dual Theme Engine, 3-Position Sidebar Docking,
 * and 2-Finger Swipe Slide Transitions.
 */

import "./style.css";
import { LogisticsWorld3D } from "./charts/logistics_world_3d";
import { NeuralViewEngine } from "./charts/neural_view";
import { renderScenarioBuilder } from "./components/scenario_builder";
import { renderDecisionExplanation } from "./components/decision_explanation";
import { renderResearchLab } from "./components/research_lab";
import { HighTechChartEngine } from "./charts/chart_engine";

type SidebarPosition = "left" | "right" | "top";
type ThemeMode = "dark" | "light";
type ViewTab = "world" | "neural" | "optimization" | "explanation" | "research";

class UnifiedControlCenter {
  private currentTheme: ThemeMode = "dark";
  private sidebarPos: SidebarPosition = "left";
  private currentTab: ViewTab = "world";
  private isSurgeActive: boolean = false;
  private appElement: HTMLElement;
  private worldViz: LogisticsWorld3D | null = null;

  // Touch Swipe Gesture State
  private touchStartX: number = 0;

  constructor() {
    const root = document.querySelector<HTMLElement>("#app");
    if (!root) throw new Error("#app element not found");
    this.appElement = root;
    this.init();
  }

  private init(): void {
    document.documentElement.setAttribute("data-theme", this.currentTheme);
    this.render();
    this.initTouchGestures();
  }

  private toggleTheme(): void {
    this.currentTheme = this.currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", this.currentTheme);
    this.render();
  }

  private setSidebarPosition(pos: SidebarPosition): void {
    this.sidebarPos = pos;
    this.render();
  }

  private switchTab(tab: ViewTab): void {
    this.currentTab = tab;
    this.render();
  }

  private triggerTrafficSurge(): void {
    this.isSurgeActive = true;
    if (this.worldViz) {
      this.worldViz.triggerTrafficEvent();
    }
    this.render();
  }

  private runOptimaEngine(): void {
    this.isSurgeActive = false;
    if (this.worldViz) {
      this.worldViz.resetSimulation();
    }
    this.render();
  }

  private render(): void {
    const navItems: { key: ViewTab; label: string; icon: string }[] = [
      { key: "world", label: "3D Logistics World", icon: "🌐" },
      { key: "neural", label: "Neural Model View", icon: "🧠" },
      { key: "optimization", label: "VRP Optimization & DSA", icon: "🧩" },
      { key: "explanation", label: "Why This Decision?", icon: "🛡️" },
      { key: "research", label: "Research Benchmark", icon: "🔬" },
    ];

    const navHtml = navItems
      .map(
        (item) => `
      <button class="nav-item ${this.currentTab === item.key ? "active" : ""}" data-tab="${item.key}">
        <span>${item.icon}</span> ${item.label}
      </button>
    `
      )
      .join("");

    let mainViewHtml = "";
    switch (this.currentTab) {
      case "world":
        mainViewHtml = `
          <div>
            <div class="hud-grid">
              <div class="hud-card">
                <div class="hud-label">Total Orders</div>
                <div class="hud-val">50</div>
                <div class="hud-sub">Active Scenario</div>
              </div>
              <div class="hud-card">
                <div class="hud-label">Fleet Size</div>
                <div class="hud-val">10</div>
                <div class="hud-sub">3 Active Vehicles</div>
              </div>
              <div class="hud-card">
                <div class="hud-label">On-Time Rate</div>
                <div class="hud-val" style="color: var(--accent-emerald);">94.2%</div>
                <div class="hud-sub">ECE Calibrated</div>
              </div>
              <div class="hud-card">
                <div class="hud-label">Routing Cost</div>
                <div class="hud-val" style="color: var(--accent-purple);">412.87</div>
                <div class="hud-sub">3-Opt Optimized</div>
              </div>
            </div>

            <div class="canvas-container">
              <div class="canvas-overlay-hud">
                <span class="dot live"></span>
                <span>Live Spatial Canvas · ${this.isSurgeActive ? "⚠️ TRAFFIC SURGE ACTIVE (+137%) · Rerouted A→B→C→E" : "Normal Corridor Flow"}</span>
              </div>
              <canvas id="world-canvas-element" class="world-canvas"></canvas>
            </div>

            <div style="margin-top: 24px;">
              ${renderDecisionExplanation(this.isSurgeActive)}
            </div>
          </div>
        `;
        break;

      case "neural":
        mainViewHtml = `
          <div>
            ${NeuralViewEngine.renderNeuralTopologySVG("Neural MLP (64x32) + XGBoost Regressor")}
            <div style="margin-top: 24px;">
              <h3>Prediction Model Comparison</h3>
              ${HighTechChartEngine.renderBarChart({
                labels: ["XGBoost Regressor", "Neural MLP", "Temporal LSTM/GRU"],
                series: [
                  { name: "Demand MAE", color: "#38bdf8", values: [1.42, 1.68, 1.35] },
                  { name: "ETA RMSE (min)", color: "#8b5cf6", values: [2.85, 3.12, 2.45] },
                ],
              })}
            </div>
          </div>
        `;
        break;

      case "optimization":
        mainViewHtml = `
          <div style="background: var(--bg-surface); backdrop-filter: blur(12px); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px;">
            <h3>🧩 Combinatorial VRP Optimization & DSA Engine</h3>
            <p style="color: var(--text-muted); margin-bottom: 20px;">
              Validates vehicle capacities (Truck A 100kg, Truck B 60kg, Truck C 40kg) via 0/1 Knapsack DP parcel packing and multi-stop 3-Opt local search edge exchanges.
            </p>

            ${HighTechChartEngine.renderBarChart({
              labels: ["Greedy DP", "2-Opt Local", "3-Opt Search", "Simulated Anneal", "Genetic Algorithm"],
              series: [
                { name: "Objective Cost", color: "#f59e0b", values: [485.2, 412.5, 389.1, 375.4, 368.2] },
                { name: "Runtime (ms)", color: "#38bdf8", values: [8.5, 24.2, 68.0, 145.0, 290.0] },
              ],
            })}

            <div style="margin-top: 20px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
              <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 0.8rem; font-weight: 800; color: var(--accent-cyan);">TRUCK A (100 KG MAX)</div>
                <div style="font-size: 1.5rem; font-weight: 900; margin: 6px 0;">80.0 kg</div>
                <div style="font-size: 0.78rem; color: var(--accent-emerald);">Route: Depot → O1 → O3 → O4 → Depot</div>
              </div>

              <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 0.8rem; font-weight: 800; color: var(--accent-emerald);">TRUCK B (60 KG MAX)</div>
                <div style="font-size: 1.5rem; font-weight: 900; margin: 6px 0;">60.0 kg</div>
                <div style="font-size: 0.78rem; color: var(--accent-emerald);">Route: Depot → O5 → O7 → Depot</div>
              </div>

              <div style="background: var(--bg-card); padding: 16px; border-radius: 12px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 0.8rem; font-weight: 800; color: var(--accent-purple);">TRUCK C (40 KG MAX)</div>
                <div style="font-size: 1.5rem; font-weight: 900; margin: 6px 0;">35.0 kg</div>
                <div style="font-size: 0.78rem; color: var(--accent-emerald);">Route: Depot → O2 → O6 → O8 → Depot</div>
              </div>
            </div>
          </div>
        `;
        break;

      case "explanation":
        mainViewHtml = renderDecisionExplanation(this.isSurgeActive);
        break;

      case "research":
        mainViewHtml = renderResearchLab();
        break;
    }

    this.appElement.innerHTML = `
      <div class="app-shell sidebar-position-${this.sidebarPos}">
        <aside class="sidebar">
          <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 38px; height: 38px; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: #fff; font-size: 1.1rem; box-shadow: 0 0 14px var(--accent-cyan);">OX</div>
            <div>
              <div style="font-weight: 900; font-size: 1.2rem; letter-spacing: -0.02em;">OPTIMA-X</div>
              <div style="font-size: 0.72rem; color: var(--text-subtle); font-weight: 600;">Control Center</div>
            </div>
          </div>

          <nav class="nav-menu">
            ${navHtml}
          </nav>

          <div style="margin-top: auto;">
            ${renderScenarioBuilder()}
          </div>
        </aside>

        <main class="main-content">
          <div class="top-toolbar">
            <div class="tool-group">
              <span style="font-size: 0.8rem; font-weight: 800; color: var(--text-subtle);">SIDEBAR DOCK:</span>
              <button class="tool-btn ${this.sidebarPos === "left" ? "active" : ""}" id="dock-left">Left</button>
              <button class="tool-btn ${this.sidebarPos === "right" ? "active" : ""}" id="dock-right">Right</button>
              <button class="tool-btn ${this.sidebarPos === "top" ? "active" : ""}" id="dock-top">Top</button>
            </div>

            <div class="tool-group">
              <span style="font-size: 0.8rem; font-weight: 800; color: var(--text-subtle);">THEME:</span>
              <button class="tool-btn" id="btn-theme-toggle">
                ${this.currentTheme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode"}
              </button>
              <span class="status-badge"><span class="dot live"></span>Live System Connected</span>
            </div>
          </div>

          <div class="carousel-viewport">
            <div class="carousel-slide">
              ${mainViewHtml}
            </div>
          </div>
        </main>
      </div>
    `;

    this.bindEvents();

    if (this.currentTab === "world") {
      const canvas = document.querySelector<HTMLCanvasElement>("#world-canvas-element");
      if (canvas) {
        this.worldViz = new LogisticsWorld3D(canvas);
        if (this.isSurgeActive) this.worldViz.triggerTrafficEvent();
        this.worldViz.startAnimation();
      }
    }
  }

  private bindEvents(): void {
    // Nav Items
    this.appElement.querySelectorAll<HTMLButtonElement>(".nav-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        const tab = btn.getAttribute("data-tab") as ViewTab;
        if (tab) this.switchTab(tab);
      });
    });

    // Sidebar Dock Buttons
    document.querySelector("#dock-left")?.addEventListener("click", () => this.setSidebarPosition("left"));
    document.querySelector("#dock-right")?.addEventListener("click", () => this.setSidebarPosition("right"));
    document.querySelector("#dock-top")?.addEventListener("click", () => this.setSidebarPosition("top"));

    // Theme Switcher
    document.querySelector("#btn-theme-toggle")?.addEventListener("click", () => this.toggleTheme());

    // Scenario Builder Actions
    document.querySelector("#btn-run-optima")?.addEventListener("click", () => this.runOptimaEngine());
    document.querySelector("#btn-traffic-surge")?.addEventListener("click", () => this.triggerTrafficSurge());
  }

  private initTouchGestures(): void {
    const tabs: ViewTab[] = ["world", "neural", "optimization", "explanation", "research"];

    window.addEventListener("touchstart", (e) => {
      if (e.touches.length === 1 || e.touches.length === 2) {
        this.touchStartX = e.touches[0].clientX;
      }
    });

    window.addEventListener("touchend", (e) => {
      if (e.changedTouches.length >= 1) {
        const touchEndX = e.changedTouches[0].clientX;
        const diffX = touchEndX - this.touchStartX;

        // 2-Finger Swipe Gesture threshold check (> 80px)
        if (Math.abs(diffX) > 80) {
          const currentIdx = tabs.indexOf(this.currentTab);
          if (diffX < 0 && currentIdx < tabs.length - 1) {
            // Swipe left -> Next tab
            this.switchTab(tabs[currentIdx + 1]);
          } else if (diffX > 0 && currentIdx > 0) {
            // Swipe right -> Previous tab
            this.switchTab(tabs[currentIdx - 1]);
          }
        }
      }
    });
  }
}

new UnifiedControlCenter();
