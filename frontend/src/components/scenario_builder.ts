/**
 * Scenario Builder & Operational Control Component.
 * Accepts user inputs for Orders, Fleet Capacities, Traffic, Weather, and Model selection.
 */

export interface ScenarioParams {
  name: string;
  ordersCount: number;
  vehiclesCount: number;
  truckACapacity: number;
  truckBCapacity: number;
  truckCCapacity: number;
  traffic: string;
  weather: string;
  model: string;
  routing: string;
  optimization: string;
}

export function renderScenarioBuilder(): string {
  return `
    <div style="background: var(--bg-surface); backdrop-filter: blur(12px); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 24px; box-shadow: var(--shadow-card);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div>
          <span style="font-size: 0.75rem; font-weight: 800; color: var(--accent-cyan); text-transform: uppercase;">Logistics Engine</span>
          <h3 style="margin: 4px 0 0; font-size: 1.3rem;">Scenario Builder</h3>
        </div>
        <span class="status-badge"><span class="dot live"></span>Engine Ready</span>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
        <div class="form-group">
          <label class="form-label">Scenario Name</label>
          <input id="sc-name" type="text" class="form-input" value="Hyderabad Logistics Test" />
        </div>

        <div class="form-group">
          <label class="form-label">Total Orders</label>
          <input id="sc-orders" type="number" class="form-input" value="50" min="1" max="500" />
        </div>

        <div class="form-group">
          <label class="form-label">Vehicle Fleet Size</label>
          <input id="sc-vehicles" type="number" class="form-input" value="10" min="1" max="100" />
        </div>

        <div class="form-group">
          <label class="form-label">Truck A Capacity (kg)</label>
          <input id="sc-cap-a" type="number" class="form-input" value="100" />
        </div>

        <div class="form-group">
          <label class="form-label">Truck B Capacity (kg)</label>
          <input id="sc-cap-b" type="number" class="form-input" value="60" />
        </div>

        <div class="form-group">
          <label class="form-label">Truck C Capacity (kg)</label>
          <input id="sc-cap-c" type="number" class="form-input" value="40" />
        </div>

        <div class="form-group">
          <label class="form-label">Traffic Condition</label>
          <select id="sc-traffic" class="form-input">
            <option value="Normal">Normal Traffic (1.0x)</option>
            <option value="Dynamic">Dynamic Dynamic Surge (1.5x - 2.5x)</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Prediction Model</label>
          <select id="sc-model" class="form-input">
            <option value="XGBoost">XGBoost Regressor</option>
            <option value="Neural MLP">Neural MLP (64x32)</option>
            <option value="LSTM">Temporal LSTM/GRU</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Routing Algorithm</label>
          <select id="sc-routing" class="form-input">
            <option value="A*">Haversine A* (Admissible)</option>
            <option value="Dijkstra">Dijkstra Shortest Path</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">Optimization Method</label>
          <select id="sc-opt" class="form-input">
            <option value="3-Opt">0/1 Knapsack DP + 3-Opt Local</option>
            <option value="2-Opt">0/1 Knapsack DP + 2-Opt Local</option>
            <option value="Simulated Annealing">Simulated Annealing</option>
            <option value="Genetic Algorithm">Genetic Algorithm</option>
          </select>
        </div>
      </div>

      <div style="display: flex; gap: 12px; margin-top: 20px;">
        <button id="btn-run-optima" class="btn-primary" style="flex: 1;">RUN OPTIMA-X ENGINE</button>
        <button id="btn-traffic-surge" class="btn-danger" style="flex: 1;">INJECT TRAFFIC SURGE (+137%)</button>
      </div>
    </div>
  `;
}
