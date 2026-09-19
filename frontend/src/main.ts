/**
 * OPTIMA-X Executive-Grade Control Platform.
 * Author: Karthikeya
 * Clean Top Header Navigation Shell with zero emoji fluff, professional typography, and dynamic multi-page state sync.
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

type ThemeMode = "dark" | "light";
type PageTab = "scenario" | "world" | "ml" | "optimization" | "decision" | "research";
type SidebarPos = "left" | "right" | "top";

class OptimaMultiPageApp {
  private apiClient: OptimaApiClient;
  private currentTheme: ThemeMode = "dark";
  private sidebarPos: SidebarPos = "top";
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

  private setSidebarPos(pos: SidebarPos): void {
    this.sidebarPos = pos;
    this.render();
  }

  private switchPage(page: PageTab): void {
    this.activePage = page;
    this.render();
  }

  private render(): void {
    const pages: { key: PageTab; label: string }[] = [
      { key: "scenario", label: "Scenario & Execution" },
      { key: "world", label: "3D Logistics World" },
      { key: "ml", label: "ML Prediction Lab" },
      { key: "optimization", label: "VRP & DSA Lab" },
      { key: "decision", label: "Decision Audit Trace" },
      { key: "research", label: "Research Benchmark" },
    ];

    const navHtml = pages
      .map(
        (p) => `
      <button class="nav-item ${this.activePage === p.key ? "active" : ""}" data-page="${p.key}">
        ${p.label}
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
          <div style="display: flex; align-items: center; gap: 14px;">
            <img src="${logoUrl}" alt="OPTIMA-X Logo" class="brand-logo" style="width: 44px; height: 44px; border-radius: 12px; object-fit: cover; border: 1.5px solid var(--accent-cyan); box-shadow: 0 0 16px rgba(56, 189, 248, 0.45);" />
            <div>
              <div style="font-weight: 900; font-size: 1.35rem; letter-spacing: -0.02em; color: var(--text-main);">OPTIMA-X</div>
              <div style="font-size: 0.76rem; color: var(--text-subtle); font-weight: 700;">Multi-Page Platform</div>
            </div>
          </div>

          <nav class="nav-menu">
            ${navHtml}
          </nav>

          <div style="font-size: 0.78rem; color: var(--text-subtle); font-weight: 700;">
            <div>Tenant: <strong style="color: var(--text-main);">Dashboard Admin</strong></div>
            <div>Backend: <a href="http://localhost:8000" target="_blank" style="color: var(--accent-cyan); text-decoration: none;">http://localhost:8000</a></div>
          </div>
        </aside>

        <main class="main-content">
          <div class="top-toolbar">
            <div class="tool-group">
              <span style="font-size: 0.75rem; font-weight: 800; color: var(--text-subtle); text-transform: uppercase;">SIDEBAR DOCK:</span>
              <button class="tool-btn ${this.sidebarPos === "left" ? "active" : ""}" id="btn-pos-left">⇇ Left</button>
              <button class="tool-btn ${this.sidebarPos === "right" ? "active" : ""}" id="btn-pos-right">⇉ Right</button>
              <button class="tool-btn ${this.sidebarPos === "top" ? "active" : ""}" id="btn-pos-top">⇈ Top</button>
            </div>

            <div class="tool-group">
              <span style="font-size: 0.75rem; font-weight: 800; color: var(--text-subtle); text-transform: uppercase;">THEME:</span>
              <button class="tool-btn" id="btn-theme-toggle">
                ${this.currentTheme === "dark" ? "Light Mode" : "Dark Mode"}
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

    // Theme Switcher
    document.querySelector("#btn-theme-toggle")?.addEventListener("click", () => this.toggleTheme());

    // Sidebar Position Controls
    document.querySelector("#btn-pos-left")?.addEventListener("click", () => this.setSidebarPos("left"));
    document.querySelector("#btn-pos-right")?.addEventListener("click", () => this.setSidebarPos("right"));
    document.querySelector("#btn-pos-top")?.addEventListener("click", () => this.setSidebarPos("top"));
  }
}

new OptimaMultiPageApp();
