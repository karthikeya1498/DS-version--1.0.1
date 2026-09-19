/**
 * High-Performance 3D/Spatial Canvas Logistics World for OPTIMA-X.
 * Renders spatial road networks, delivery nodes, smooth continuous vehicle motion with easing,
 * and live dynamic rerouting on Traffic Event Injections.
 */

export interface WorldNode {
  id: string;
  label: string;
  x: number;
  y: number;
}

export interface OrderItem {
  id: string;
  weight: number;
  customer: string;
  nodeId: string;
  delivered: boolean;
}

export interface VehicleAgent {
  id: string;
  label: string;
  capacity: number;
  currentLoad: number;
  route: string[];
  currentSegIdx: number;
  segProgress: number; // 0.0 to 1.0
  direction: 1 | -1;   // 1 = Forward, -1 = Return
  color: string;
}

export class LogisticsWorld3D {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private animFrameId: number | null = null;
  private isTrafficSurge: boolean = false;
  private pulsePhase: number = 0;

  public nodes: Map<string, WorldNode> = new Map([
    ["depot", { id: "depot", label: "Central Depot (Hub A)", x: 0, y: 0 }],
    ["node_b", { id: "node_b", label: "North Zone B", x: -2.5, y: 2.8 }],
    ["node_c", { id: "node_c", label: "East Hub C", x: 1.2, y: 4.2 }],
    ["node_d", { id: "node_d", label: "South Corridor D", x: 3.2, y: 1.8 }],
    ["node_e", { id: "node_e", label: "West Terminal E", x: 4.2, y: -2.2 }],
  ]);

  public orders: OrderItem[] = [
    { id: "O1", weight: 30, customer: "Customer A", nodeId: "node_b", delivered: false },
    { id: "O2", weight: 20, customer: "Customer B", nodeId: "node_c", delivered: false },
    { id: "O3", weight: 40, customer: "Customer C", nodeId: "node_d", delivered: false },
    { id: "O4", weight: 10, customer: "Customer D", nodeId: "node_e", delivered: false },
  ];

  public vehicles: VehicleAgent[] = [
    {
      id: "truck_a",
      label: "Fleet A (100kg)",
      capacity: 100,
      currentLoad: 80,
      route: ["depot", "node_b", "node_d", "node_e"],
      currentSegIdx: 0,
      segProgress: 0.0,
      direction: 1,
      color: "#0ea5e9",
    },
    {
      id: "truck_b",
      label: "Fleet B (60kg)",
      capacity: 60,
      currentLoad: 60,
      route: ["depot", "node_c", "node_e"],
      currentSegIdx: 0,
      segProgress: 0.35,
      direction: 1,
      color: "#10b981",
    },
    {
      id: "truck_c",
      label: "Fleet C (40kg)",
      capacity: 40,
      currentLoad: 35,
      route: ["depot", "node_b", "node_c", "node_e"],
      currentSegIdx: 1,
      segProgress: 0.7,
      direction: -1,
      color: "#6366f1",
    },
  ];

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Could not get 2D rendering context.");
    this.ctx = ctx;
    this.resizeCanvas();
    window.addEventListener("resize", () => this.resizeCanvas());
  }

  private resizeCanvas(): void {
    const parent = this.canvas.parentElement;
    if (parent) {
      this.canvas.width = parent.clientWidth * window.devicePixelRatio;
      this.canvas.height = parent.clientHeight * window.devicePixelRatio;
      this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }
    this.render();
  }

  public triggerTrafficEvent(): void {
    this.isTrafficSurge = true;
    const truckA = this.vehicles.find((v) => v.id === "truck_a");
    if (truckA) {
      truckA.route = ["depot", "node_b", "node_c", "node_e"];
    }
  }

  public resetSimulation(): void {
    this.isTrafficSurge = false;
    const truckA = this.vehicles.find((v) => v.id === "truck_a");
    if (truckA) {
      truckA.route = ["depot", "node_b", "node_d", "node_e"];
    }
  }

  public startAnimation(): void {
    const animate = () => {
      this.pulsePhase += 0.03;
      this.updateVehiclePositions();
      this.render();
      this.animFrameId = requestAnimationFrame(animate);
    };
    if (!this.animFrameId) animate();
  }

  public stopAnimation(): void {
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
  }

  private updateVehiclePositions(): void {
    for (const v of this.vehicles) {
      const speed = 0.005; // Smooth realistic cruising speed
      v.segProgress += speed * v.direction;

      if (v.direction === 1 && v.segProgress >= 1.0) {
        v.segProgress = 0.0;
        if (v.currentSegIdx < v.route.length - 2) {
          v.currentSegIdx++;
        } else {
          // Reached route end node: Reverse direction smoothly to return to depot
          v.direction = -1;
          v.segProgress = 1.0;
        }
      } else if (v.direction === -1 && v.segProgress <= 0.0) {
        v.segProgress = 1.0;
        if (v.currentSegIdx > 0) {
          v.currentSegIdx--;
        } else {
          // Returned to depot: Reverse direction smoothly to start next delivery loop
          v.direction = 1;
          v.segProgress = 0.0;
        }
      }
    }
  }

  private render(): void {
    const width = this.canvas.clientWidth;
    const height = this.canvas.clientHeight;
    this.ctx.clearRect(0, 0, width, height);

    const padding = 70;
    const project = (x: number, y: number) => ({
      px: padding + ((x + 4) / 10) * (width - padding * 2),
      py: height - (padding + ((y + 4) / 10) * (height - padding * 2)),
    });

    // 1. Draw Network Road Edges
    const edges: [string, string][] = [
      ["depot", "node_b"],
      ["node_b", "node_c"],
      ["node_b", "node_d"],
      ["node_c", "node_e"],
      ["node_d", "node_e"],
    ];

    for (const [uId, vId] of edges) {
      const u = this.nodes.get(uId);
      const v = this.nodes.get(vId);
      if (u && v) {
        const p1 = project(u.x, u.y);
        const p2 = project(v.x, v.y);

        const isSurgeEdge =
          this.isTrafficSurge &&
          ((uId === "node_b" && vId === "node_d") || (uId === "node_d" && vId === "node_b"));

        this.ctx.beginPath();
        this.ctx.moveTo(p1.px, p1.py);
        this.ctx.lineTo(p2.px, p2.py);
        this.ctx.strokeStyle = isSurgeEdge ? "#e11d48" : "rgba(14, 165, 233, 0.25)";
        this.ctx.lineWidth = isSurgeEdge ? 4 : 2;
        if (isSurgeEdge) {
          this.ctx.shadowColor = "#e11d48";
          this.ctx.shadowBlur = 12;
        }
        this.ctx.stroke();
        this.ctx.shadowBlur = 0;
      }
    }

    // 2. Draw Smooth Animated Vehicles along Route Segments
    for (const v of this.vehicles) {
      if (v.route.length > 1 && v.currentSegIdx >= 0 && v.currentSegIdx < v.route.length - 1) {
        const uId = v.route[v.currentSegIdx];
        const vId = v.route[v.currentSegIdx + 1];
        const u = this.nodes.get(uId);
        const nodeV = this.nodes.get(vId);
        if (u && nodeV) {
          const p1 = project(u.x, u.y);
          const p2 = project(nodeV.x, nodeV.y);

          // Smooth interpolation
          const t = Math.max(0, Math.min(1, v.segProgress));
          const vx = p1.px + (p2.px - p1.px) * t;
          const vy = p1.py + (p2.py - p1.py) * t;

          // Draw Glowing Vehicle Circle
          this.ctx.beginPath();
          this.ctx.arc(vx, vy, 8, 0, Math.PI * 2);
          this.ctx.fillStyle = v.color;
          this.ctx.shadowColor = v.color;
          this.ctx.shadowBlur = 14;
          this.ctx.fill();
          this.ctx.shadowBlur = 0;

          // Vehicle Label Text
          this.ctx.fillStyle = "var(--text-main)";
          this.ctx.font = "bold 11px Plus Jakarta Sans, sans-serif";
          this.ctx.fillText(v.label, vx + 12, vy + 4);
        }
      }
    }

    // 3. Draw Nodes & Hubs
    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    for (const [id, node] of this.nodes) {
      const p = project(node.x, node.y);

      // Pulse ring for Central Depot
      if (id === "depot") {
        const pulseR = 12 + Math.sin(this.pulsePhase) * 3;
        this.ctx.beginPath();
        this.ctx.arc(p.px, p.py, pulseR, 0, Math.PI * 2);
        this.ctx.strokeStyle = "rgba(217, 119, 6, 0.4)";
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
      }

      this.ctx.beginPath();
      this.ctx.arc(p.px, p.py, id === "depot" ? 10 : 6, 0, Math.PI * 2);
      this.ctx.fillStyle = id === "depot" ? "#d97706" : "#10b981";
      this.ctx.shadowColor = id === "depot" ? "#d97706" : "#10b981";
      this.ctx.shadowBlur = 10;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;

      this.ctx.fillStyle = isLight ? "#0f172a" : "#f8fafc";
      this.ctx.font = "bold 12px Plus Jakarta Sans, sans-serif";
      this.ctx.fillText(node.label, p.px + 12, p.py - 6);
    }
  }
}
