/**
 * OPTIMA-X Executive-Grade Control Platform.
 * Author: Karthikeya
 * Clean Navigation Shell with uniform typography, 2-finger slide/swipe gesture dashboard transitions,
 * graphical indicator overlay, and downloadable scenario report integration.
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

const PAGES_ORDER: { key: PageTab; label: string }[] = [
  { key: "scenario", label: "Scenario & Execution" },
  { key: "world", label: "3D Logistics World" },
  { key: "ml", label: "ML Prediction Lab" },
  { key: "optimization", label: "VRP & DSA Lab" },
  { key: "decision", label: "Decision Audit Trace" },
  { key: "research", label: "Research Benchmark" },
];

class OptimaMultiPageApp {
  private apiClient: OptimaApiClient;
  private currentTheme: ThemeMode = "dark";
  private sidebarPos: SidebarPos = "top";
  private activePage: PageTab = "scenario";
  private latestResult: SimulationResult | null = null;
  private isSurgeActive: boolean = false;
  private appElement: HTMLElement;
  private worldViz: LogisticsWorld3D | null = null;

  // Gesture Slider tracking
  private gestureCooldown: boolean = false;
  private touchStartX: number = 0;
  private touchStartY: number = 0;
  private slideDirection: "next" | "prev" | "none" = "none";

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
    this.setupGestureListeners();
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

  private switchPage(page: PageTab, dir: "next" | "prev" = "next"): void {
    if (this.activePage === page) return;
    this.slideDirection = dir;
    this.activePage = page;
    this.render();
  }

  private navigateRelative(delta: number): void {
    const idx = PAGES_ORDER.findIndex((p) => p.key === this.activePage);
    if (idx === -1) return;
    const newIdx = idx + delta;
    if (newIdx >= 0 && newIdx < PAGES_ORDER.length) {
      const targetPage = PAGES_ORDER[newIdx].key;
      const dir = delta > 0 ? "next" : "prev";
      this.switchPage(targetPage, dir);
    }
  }

  private setupGestureListeners(): void {
    // 2-finger Trackpad Horizontal Wheel gesture listener
    window.addEventListener(
      "wheel",
      (evt: WheelEvent) => {
        if (Math.abs(evt.deltaX) > 35 && Math.abs(evt.deltaX) > Math.abs(evt.deltaY) * 1.5) {
          if (this.gestureCooldown) return;
          this.gestureCooldown = true;
          setTimeout(() => (this.gestureCooldown = false), 500);

          if (evt.deltaX > 0) {
            this.navigateRelative(1);
          } else {
            this.navigateRelative(-1);
          }
        }
      },
      { passive: true }
    );

    // Touch Swipe gesture listeners
    window.addEventListener(
      "touchstart",
      (evt: TouchEvent) => {
        if (evt.touches.length > 0) {
          this.touchStartX = evt.touches[0].clientX;
          this.touchStartY = evt.touches[0].clientY;
        }
      },
      { passive: true }
    );

    window.addEventListener(
      "touchend",
      (evt: TouchEvent) => {
        if (evt.changedTouches.length > 0) {
          const deltaX = evt.changedTouches[0].clientX - this.touchStartX;
          const deltaY = evt.changedTouches[0].clientY - this.touchStartY;

          if (Math.abs(deltaX) > 60 && Math.abs(deltaX) > Math.abs(deltaY) * 1.5) {
            if (this.gestureCooldown) return;
            this.gestureCooldown = true;
            setTimeout(() => (this.gestureCooldown = false), 500);

            if (deltaX < 0) {
              this.navigateRelative(1);
            } else {
              this.navigateRelative(-1);
            }
          }
        }
      },
      { passive: true }
    );
  }

  private render(): void {
    const navHtml = PAGES_ORDER.map(
      (p) => `
      <button class="nav-item ${this.activePage === p.key ? "active" : ""}" data-page="${p.key}">
        ${p.label}
      </button>
    `
    ).join("");

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

    const objClass = this.slideDirection === "next" ? "slide-next" : this.slideDirection === "prev" ? "slide-prev" : "";

    this.appElement.innerHTML = `
      <div class="app-shell sidebar-position-${this.sidebarPos}">
        <aside class="sidebar">
          <div style="display: flex; align-items: center; gap: 14px;">
            <img src="${logoUrl}" alt="OPTIMA-X Logo" class="brand-logo" style="width: 42px; height: 42px; border-radius: 10px; object-fit: cover; border: 1.5px solid var(--accent-cyan); box-shadow: 0 0 14px rgba(14, 165, 233, 0.35);" />
            <div>
              <div style="font-weight: 900; font-size: 1.3rem; letter-spacing: -0.02em; color: var(--text-main);">OPTIMA-X</div>
            </div>
          </div>

          <nav class="nav-menu">
            ${navHtml}
          </nav>
        </aside>

        <main class="main-content">
          <div class="top-toolbar">
            <div class="tool-group">
              <button class="tool-btn ${this.sidebarPos === "left" ? "active" : ""}" id="btn-pos-left" title="Dock Left">⇇ Left</button>
              <button class="tool-btn ${this.sidebarPos === "right" ? "active" : ""}" id="btn-pos-right" title="Dock Right">⇉ Right</button>
              <button class="tool-btn ${this.sidebarPos === "top" ? "active" : ""}" id="btn-pos-top" title="Dock Top">⇈ Top</button>
            </div>

            <div class="tool-group">
              <button class="tool-btn" id="btn-theme-toggle">
                ${this.currentTheme === "dark" ? "Light Mode" : "Dark Mode"}
              </button>
            </div>
          </div>

          <div class="carousel-viewport ${objClass}">
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
        () => this.switchPage("world", "next"),
        this.latestResult
      );
    } else if (this.activePage === "world") {
      this.worldViz = initWorldPageCanvas(this.isSurgeActive, (active) => {
        this.isSurgeActive = active;
        this.render();
      });
    } else if (this.activePage === "ml") {
      bindMlPageEvents();
    }

    this.slideDirection = "none";
  }

  private bindEvents(): void {
    // Nav Items
    this.appElement.querySelectorAll<HTMLButtonElement>(".nav-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        const page = btn.getAttribute("data-page") as PageTab;
        if (page) {
          const currentIdx = PAGES_ORDER.findIndex((p) => p.key === this.activePage);
          const targetIdx = PAGES_ORDER.findIndex((p) => p.key === page);
          const dir = targetIdx >= currentIdx ? "next" : "prev";
          this.switchPage(page, dir);
        }
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
