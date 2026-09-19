/**
 * OPTIMA-X Research-Grade Multi-Page Control Platform.
 * Author: Karthikeya
 * Orchestrates Scenario Execution Stepper, 3D Spatial Logistics World,
 * Neural Topology Lab, VRP Solvers, Decision Lineage Explorer, and Research Benchmarks.
 */

import "./style.css";
import { OptimaApiClient, SimulationResult } from "./services/api_client";
import { renderScenarioPage, bindScenarioPageEvents } from "./pages/scenario_page";
import { renderWorldPage, initWorldPageCanvas } from "./pages/world_page";
import { renderMlPage, bindMlPageEvents } from "./pages/ml_page";
import { renderOptimizationPage } from "./pages/optimization_page";
import { renderDecisionPage } from "./pages/decision_page";
import { renderResearchPage } from "./pages/research_page";
import { LogisticsWorld3D } from "./charts/logistics_world_3d";

import logoUrl from "./assets/logo.jpg";

type SidebarPosition = "left" | "right" | "top";
type ThemeMode = "dark" | "light";
type PageTab = "scenario" | "world" | "ml" | "optimization" | "decision" | "research";

class OptimaMultiPageApp {
  private apiClient: OptimaApiClient;
  private currentTheme: ThemeMode = "dark";
  private sidebarPos: SidebarPosition = "left";
  private activePage: PageTab = "scenario";
  private latestResult: SimulationResult | null = null;
  private isSurgeActive: boolean = false;
  private appElement: HTMLElement;
  private worldViz: LogisticsWorld3D | null = null;

  constructor() {
    const root = document.querySelector<HTMLElement>("#app");
    if (!root) throw new Error("#app element not found");
    this.appElement = root;
    this.apiClient = new OptimaApiClient();
    this.init();
  }

  private init(): void {
    document.documentElement.setAttribute("data-theme", this.currentTheme);
    this.render();
  }

  private toggleTheme(): void {
    this.currentTheme = this.currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", this.currentTheme);
    this.render();
  }

  private setSidebarPos(pos: SidebarPosition): void {
    this.sidebarPos = pos;
    this.render();
  }

  private switchPage(page: PageTab): void {
    this.activePage = page;
    this.render();
  }

  private render(): void {
    const pages: { key: PageTab; label: string; icon: string }[] = [
      { key: "scenario", label: "Scenario & Execution", icon: "⚡" },
      { key: "world", label: "3D Logistics World", icon: "🌐" },
      { key: "ml", label: "ML Prediction Lab", icon: "🧠" },
      { key: "optimization", label: "VRP & DSA Lab", icon: "🧩" },
      { key: "decision", label: "Decision Audit Trace", icon: "🛡️" },
      { key: "research", label: "Research Benchmark", icon: "🔬" },
    ];

    const navHtml = pages
      .map(
        (p) => `
      <button class="nav-item ${this.activePage === p.key ? "active" : ""}" data-page="${p.key}">
        <span>${p.icon}</span> ${p.label}
      </button>
    `
      )
      .join("");

    let pageContentHtml = "";
    switch (this.activePage) {
      case "scenario":
        pageContentHtml = renderScenarioPage(this.latestResult);
        break;
      case "world":
        pageContentHtml = renderWorldPage(this.isSurgeActive);
        break;
      case "ml":
        pageContentHtml = renderMlPage();
        break;
      case "optimization":
        pageContentHtml = renderOptimizationPage();
        break;
      case "decision":
        pageContentHtml = renderDecisionPage();
        break;
      case "research":
        pageContentHtml = renderResearchPage();
        break;
    }

    this.appElement.innerHTML = `
      <div class="app-shell sidebar-position-${this.sidebarPos}">
        <aside class="sidebar">
          <div style="display: flex; align-items: center; gap: 12px;">
            <img src="${logoUrl}" alt="OPTIMA-X Logo" class="brand-logo" style="width: 42px; height: 42px; border-radius: 10px; object-fit: cover; border: 1.5px solid var(--accent-cyan); box-shadow: 0 0 12px var(--accent-cyan);" />
            <div>
              <div style="font-weight: 900; font-size: 1.25rem; letter-spacing: -0.02em;">OPTIMA-X</div>
              <div style="font-size: 0.72rem; color: var(--text-subtle); font-weight: 600;">Multi-Page Platform</div>
            </div>
          </div>

          <nav class="nav-menu">
            ${navHtml}
          </nav>

          <div style="margin-top: auto; padding: 16px; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-subtle); font-size: 0.8rem; color: var(--text-muted);">
            <div>Tenant: <strong>Dashboard Admin</strong></div>
            <div style="margin-top: 4px;">Backend: <strong style="color: var(--accent-emerald);">http://localhost:8000</strong></div>
          </div>
        </aside>

        <main class="main-content">
          <div class="top-toolbar">
            <div class="tool-group">
              <span style="font-size: 0.8rem; font-weight: 800; color: var(--text-subtle);">SIDEBAR DOCK:</span>
              <button class="tool-btn ${this.sidebarPos === "left" ? "active" : ""}" id="dock-left" title="Dock Left">⇇ Left</button>
              <button class="tool-btn ${this.sidebarPos === "right" ? "active" : ""}" id="dock-right" title="Dock Right">⇉ Right</button>
              <button class="tool-btn ${this.sidebarPos === "top" ? "active" : ""}" id="dock-top" title="Dock Top">⇈ Top</button>
            </div>

            <div class="tool-group">
              <span style="font-size: 0.8rem; font-weight: 800; color: var(--text-subtle);">THEME:</span>
              <button class="tool-btn" id="btn-theme-toggle">
                ${this.currentTheme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode"}
              </button>
              <span class="status-badge"><span class="dot live"></span>FastAPI Live</span>
            </div>
          </div>

          <div class="carousel-viewport">
            ${pageContentHtml}
          </div>
        </main>
      </div>
    `;

    this.bindEvents();

    if (this.activePage === "scenario") {
      bindScenarioPageEvents(
        this.apiClient,
        (res) => {
          this.latestResult = res;
          this.render();
        },
        () => this.switchPage("world")
      );
    } else if (this.activePage === "world") {
      this.worldViz = initWorldPageCanvas(this.isSurgeActive, (active) => {
        this.isSurgeActive = active;
        this.render();
      });
    } else if (this.activePage === "ml") {
      bindMlPageEvents();
    }
  }

  private bindEvents(): void {
    // Nav Items
    this.appElement.querySelectorAll<HTMLButtonElement>(".nav-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        const page = btn.getAttribute("data-page") as PageTab;
        if (page) this.switchPage(page);
      });
    });

    // Sidebar Docking Buttons
    document.querySelector("#dock-left")?.addEventListener("click", () => this.setSidebarPos("left"));
    document.querySelector("#dock-right")?.addEventListener("click", () => this.setSidebarPos("right"));
    document.querySelector("#dock-top")?.addEventListener("click", () => this.setSidebarPos("top"));

    // Theme Switcher
    document.querySelector("#btn-theme-toggle")?.addEventListener("click", () => this.toggleTheme());
  }
}

new OptimaMultiPageApp();
