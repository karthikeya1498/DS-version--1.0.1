/**
 * High-Performance 3D/Spatial Canvas Logistics World for OPTIMA-X.
 * Renders spatial road networks, pickup orders O1-O8, vehicle movement along routes,
 * and live dynamic rerouting on Traffic Event Injections (+137%).
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
  color: string;
}

export class LogisticsWorld3D {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private animFrameId: number | null = null;
  private isTrafficSurge: boolean = false;
  private trafficSurgeEdge: [string, string] = ["node_b", "node_d"];

  public nodes: Map<string, WorldNode> = new Map([
    ["depot", { id: "depot", label: "Central Depot (A)", x: 0, y: 0 }],
    ["node_b", { id: "node_b", label: "Node B", x: -2, y: 3 }],
    ["node_c", { id: "node_c", label: "Node C (Alternative)", x: 1, y: 5 }],
    ["node_d", { id: "node_d", label: "Node D (Traffic Zone)", x: 3, y: 2 }],
    ["node_e", { id: "node_e", label: "Node E (Destination)", x: 4, y: -2 }],
  ]);

  public orders: OrderItem[] = [
    { id: "O1", weight: 30, customer: "Customer A", nodeId: "node_b", delivered: false },
    { id: "O2", weight: 20, customer: "Customer B", nodeId: "node_c", delivered: false },
    { id: "O3", weight: 40, customer: "Customer C", nodeId: "node_d", delivered: false },
    { id: "O4", weight: 10, customer: "Customer D", nodeId: "node_e", delivered: false },
    { id: "O5", weight: 25, customer: "Customer E", nodeId: "node_b", delivered: false },
  ];

  public vehicles: VehicleAgent[] = [
    {
      id: "truck_a",
      label: "Truck A (100kg)",
      capacity: 100,
      currentLoad: 80,
      route: ["depot", "node_b", "node_d", "node_e"],
      currentSegIdx: 0,
      segProgress: 0.0,
      color: "#38bdf8",
    },
    {
      id: "truck_b",
      label: "Truck B (60kg)",
      capacity: 60,
      currentLoad: 60,
      route: ["depot", "node_c", "node_e"],
      currentSegIdx: 0,
      segProgress: 0.2,
      color: "#10b981",
    },
    {
      id: "truck_c",
      label: "Truck C (40kg)",
      capacity: 40,
      currentLoad: 35,
      route: ["depot", "node_b", "node_e"],
      currentSegIdx: 0,
      segProgress: 0.5,
      color: "#8b5cf6",
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
    // Reroute Truck A from Depot -> B -> D -> E to Depot -> B -> C -> E (Avoiding B-D traffic surge)
    const truckA = this.vehicles.find((v) => v.id === "truck_a");
    if (truckA) {
      truckA.route = ["depot", "node_b", "node_c", "node_e"];
      truckA.currentSegIdx = 1; // Reroute live at Node B toward Node C!
      truckA.segProgress = 0.0;
    }
  }

  public resetSimulation(): void {
    this.isTrafficSurge = false;
    const truckA = this.vehicles.find((v) => v.id === "truck_a");
    if (truckA) {
      truckA.route = ["depot", "node_b", "node_d", "node_e"];
      truckA.currentSegIdx = 0;
      truckA.segProgress = 0.0;
    }
  }

  public startAnimation(): void {
    const animate = () => {
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
      v.segProgress += 0.008;
      if (v.segProgress >= 1.0) {
        v.segProgress = 0.0;
        v.currentSegIdx = (v.currentSegIdx + 1) % (v.route.length - 1);
      }
    }
  }

  private render(): void {
    const width = this.canvas.clientWidth;
    const height = this.canvas.clientHeight;
    this.ctx.clearRect(0, 0, width, height);

    const padding = 60;
    const project = (x: number, y: number) => ({
      px: padding + ((x + 4) / 10) * (width - padding * 2),
      py: height - (padding + ((y + 4) / 10) * (height - padding * 2)),
    });

    // 1. Draw Edges
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
        this.ctx.strokeStyle = isSurgeEdge ? "#ef4444" : "rgba(56, 189, 248, 0.3)";
        this.ctx.lineWidth = isSurgeEdge ? 4 : 2;
        if (isSurgeEdge) {
          this.ctx.shadowColor = "#ef4444";
          this.ctx.shadowBlur = 12;
        }
        this.ctx.stroke();
        this.ctx.shadowBlur = 0;
      }
    }

    // 2. Draw Vehicle Routes & Animated Vehicles
    for (const v of this.vehicles) {
      if (v.route.length > 1) {
        const uId = v.route[v.currentSegIdx];
        const vId = v.route[v.currentSegIdx + 1];
        const u = this.nodes.get(uId);
        const nodeV = this.nodes.get(vId);
        if (u && nodeV) {
          const p1 = project(u.x, u.y);
          const p2 = project(nodeV.x, nodeV.y);

          const vx = p1.px + (p2.px - p1.px) * v.segProgress;
          const vy = p1.py + (p2.py - p1.py) * v.segProgress;

          // Draw Vehicle Circle
          this.ctx.beginPath();
          this.ctx.arc(vx, vy, 10, 0, Math.PI * 2);
          this.ctx.fillStyle = v.color;
          this.ctx.shadowColor = v.color;
          this.ctx.shadowBlur = 16;
          this.ctx.fill();
          this.ctx.shadowBlur = 0;

          // Vehicle Label
          this.ctx.fillStyle = "#ffffff";
          this.ctx.font = "bold 11px Inter, sans-serif";
          this.ctx.fillText(`FLEET ${v.id.toUpperCase()}`, vx + 14, vy + 4);
        }
      }
    }

    // 3. Draw Nodes & Orders
    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    for (const [id, node] of this.nodes) {
      const p = project(node.x, node.y);

      this.ctx.beginPath();
      this.ctx.arc(p.px, p.py, id === "depot" ? 12 : 7, 0, Math.PI * 2);
      this.ctx.fillStyle = id === "depot" ? "#f59e0b" : "#10b981";
      this.ctx.shadowColor = id === "depot" ? "#f59e0b" : "#10b981";
      this.ctx.shadowBlur = 10;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;

      this.ctx.fillStyle = isLight ? "#0f172a" : "#f8fafc";
      this.ctx.font = "bold 12px Inter, sans-serif";
      this.ctx.fillText(node.label, p.px + 12, p.py - 6);
    }
  }
}
