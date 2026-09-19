/**
 * High-Tech HTML5 Canvas Road Graph Engine for OPTIMA-X Phase 1.
 * Renders spatial network nodes, edges, Haversine A* paths, Dijkstra frontiers, and dispatch vectors.
 */

export interface GraphNode {
  id: string;
  x: number;
  y: number;
  label?: string;
}

export interface GraphEdge {
  from: string;
  to: string;
  weight: number;
  speed?: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  highlightPath?: string[];
}

export class RoadGraphVisualizer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private data: GraphData;
  private animFrameId: number | null = null;
  private pulseOffset: number = 0;

  constructor(canvas: HTMLCanvasElement, data: GraphData) {
    this.canvas = canvas;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Could not get 2D rendering context from canvas.");
    this.ctx = ctx;
    this.data = data;
    this.resizeCanvas();
    window.addEventListener("resize", () => this.resizeCanvas());
  }

  public setData(data: GraphData): void {
    this.data = data;
    this.render();
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

  public startAnimation(): void {
    const animate = () => {
      this.pulseOffset = (this.pulseOffset + 0.05) % 1;
      this.render();
      this.animFrameId = requestAnimationFrame(animate);
    };
    if (!this.animFrameId) {
      animate();
    }
  }

  public stopAnimation(): void {
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
  }

  public render(): void {
    const width = this.canvas.clientWidth;
    const height = this.canvas.clientHeight;
    this.ctx.clearRect(0, 0, width, height);

    if (this.data.nodes.length === 0) return;

    // Determine spatial bounding box
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const node of this.data.nodes) {
      if (node.x < minX) minX = node.x;
      if (node.x > maxX) maxX = node.x;
      if (node.y < minY) minY = node.y;
      if (node.y > maxY) maxY = node.y;
    }

    const padding = 50;
    const scaleX = maxX === minX ? 1 : (width - padding * 2) / (maxX - minX);
    const scaleY = maxY === minY ? 1 : (height - padding * 2) / (maxY - minY);

    const project = (x: number, y: number) => ({
      px: padding + (x - minX) * scaleX,
      py: height - (padding + (y - minY) * scaleY),
    });

    const nodePosMap = new Map<string, { px: number; py: number }>();
    for (const node of this.data.nodes) {
      nodePosMap.set(node.id, project(node.x, node.y));
    }

    // 1. Draw Edges
    for (const edge of this.data.edges) {
      const u = nodePosMap.get(edge.from);
      const v = nodePosMap.get(edge.to);
      if (u && v) {
        this.ctx.beginPath();
        this.ctx.moveTo(u.px, u.py);
        this.ctx.lineTo(v.px, v.py);
        this.ctx.strokeStyle = "rgba(56, 189, 248, 0.25)";
        this.ctx.lineWidth = 1.5;
        this.ctx.stroke();
      }
    }

    // 2. Draw Highlight Path (Shortest Path route overlay)
    if (this.data.highlightPath && this.data.highlightPath.length > 1) {
      this.ctx.beginPath();
      const firstPos = nodePosMap.get(this.data.highlightPath[0]);
      if (firstPos) {
        this.ctx.moveTo(firstPos.px, firstPos.py);
        for (let i = 1; i < this.data.highlightPath.length; i++) {
          const pos = nodePosMap.get(this.data.highlightPath[i]);
          if (pos) this.ctx.lineTo(pos.px, pos.py);
        }
      }
      this.ctx.strokeStyle = "#10b981";
      this.ctx.lineWidth = 4;
      this.ctx.shadowColor = "#10b981";
      this.ctx.shadowBlur = 12;
      this.ctx.stroke();
      this.ctx.shadowBlur = 0; // reset glow

      // Render animated pulse vector on shortest path
      if (this.data.highlightPath.length > 1) {
        const segIdx = Math.floor(this.pulseOffset * (this.data.highlightPath.length - 1));
        const segProgress = (this.pulseOffset * (this.data.highlightPath.length - 1)) % 1;
        const u = nodePosMap.get(this.data.highlightPath[segIdx]);
        const v = nodePosMap.get(this.data.highlightPath[segIdx + 1]);
        if (u && v) {
          const px = u.px + (v.px - u.px) * segProgress;
          const py = u.py + (v.py - u.py) * segProgress;
          this.ctx.beginPath();
          this.ctx.arc(px, py, 6, 0, Math.PI * 2);
          this.ctx.fillStyle = "#38bdf8";
          this.ctx.shadowColor = "#38bdf8";
          this.ctx.shadowBlur = 16;
          this.ctx.fill();
          this.ctx.shadowBlur = 0;
        }
      }
    }

    // 3. Draw Nodes
    for (const node of this.data.nodes) {
      const pos = nodePosMap.get(node.id);
      if (!pos) continue;

      const isPathNode = this.data.highlightPath?.includes(node.id);

      this.ctx.beginPath();
      this.ctx.arc(pos.px, pos.py, isPathNode ? 7 : 5, 0, Math.PI * 2);
      this.ctx.fillStyle = isPathNode ? "#10b981" : "#38bdf8";
      this.ctx.shadowColor = isPathNode ? "#10b981" : "#38bdf8";
      this.ctx.shadowBlur = isPathNode ? 14 : 6;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;

      // Label
      this.ctx.fillStyle = "#94a3b8";
      this.ctx.font = "10px Inter, sans-serif";
      this.ctx.fillText(node.label || node.id, pos.px + 9, pos.py + 3);
    }
  }
}
