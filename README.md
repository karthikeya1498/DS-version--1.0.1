# OPTIMA-X: Hybrid Decision and Optimization Engine for Urban Logistics

**OPTIMA-X** is an end-to-end research-engineering prototype for dynamic, data-driven urban logistics. It unifies **Data Structures & Algorithms (DSA)**, **Machine Learning (XGBoost, MLP, LSTM/GRU)**, **Combinatorial Optimization (CVRP/TW with 2-opt/3-opt/SA/GA/OR-Tools)**, **Sequential Reinforcement Learning (PPO/DQN)**, **Evidence-Grounded Decision Intelligence**, and **SQL Persistence** into a single cohesive pipeline.

---

## 🏛️ System Architecture

```
                                  OPTIMA-X PIPELINE
                                  
  ┌───────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
  │  HISTORICAL DATA  │ ───► │  SQL DATABASE / ENGINE  │ ───► │    FEATURE PIPELINE     │
  │ Orders / Traffic  │      │   PostgreSQL / SQLite   │      │ Lags, ETA, Graph Stats  │
  └───────────────────┘      └─────────────────────────┘      └─────────────────────────┘
                                                                           │
                             ┌─────────────────────────────────────────────┘
                             ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────┐
  │                                MACHINE LEARNING LAYER                               │
  │  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────────────┐  │
  │  │  XGBoost & Neural MLP │  │  Temporal LSTM / GRU  │  │  Late-Risk Classifier   │  │
  │  │ (Demand & Travel ETA) │  │  (Multi-Step Series)  │  │  & ECE Risk Calibration │  │
  │  └───────────────────────┘  └───────────────────────┘  └─────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────────────────┘
                                             │ PredictionBundle
                                             ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────┐
  │                                 DSA & ROUTING LAYER                                 │
  │  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────────────┐  │
  │  │ Admissible A* Routing │  │  Segment Tree Speed   │  │  Fenwick Tree Cumulative│  │
  │  │  (Haversine Lower Bnd)│  │   Range Query Engine  │  │   Demand Monitoring     │  │
  │  └───────────────────────┘  └───────────────────────┘  └─────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────────────────┘
                                             │
                                             ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────┐
  │                            COMBINATORIAL OPTIMIZATION (VRP)                         │
  │  ┌────────────────────────────────────────┐  ┌───────────────────────────────────┐  │
  │  │   Capacity Bin-Packing / Knapsack DP   │  │    Multi-Stop Route Sequencing    │  │
  │  │    (Multi-Order Vehicle Bundles)       │  │ (2-Opt, 3-Opt, SA, GA, OR-Tools)  │  │
  │  └────────────────────────────────────────┘  └───────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────────────────┘
                                             │
                                             ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────┐
  │                             DECISION & EXECUTION LAYER                              │
  │  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────────────┐  │
  │  │ Sequential RL Policy  │  │ Grounded Tool Registry│  │ FastAPI Telemetry &     │  │
  │  │ (Domain-Connected PPO)│  │ & Guarded Assistant   │  │ Interactive Dashboard   │  │
  │  └───────────────────────┘  └───────────────────────┘  └─────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Implementation Status Matrix

| Module | Component | Implementation Status | Backing Engine |
| :--- | :--- | :--- | :--- |
| **Phase 1: Foundations** | Road Graph & Ingestion | **Implemented** | Adjacency-list `RoadGraph`, OSM/Overpass parser |
| | Discrete-Event Simulator | **Implemented** | Priority-queue event engine (Synthetic + Replay) |
| **Phase 2: ML & Forecasting** | Demand Forecasting | **Implemented** | XGBoost Regressor, Neural MLP, LSTM & GRU |
| | ETA Prediction | **Implemented** | Feature-engineered XGBoost & Neural MLP |
| | Late-Risk Classification | **Implemented** | Calibrated XGBoost & Logistic Classifier ($P(\text{late})$) |
| | Probability Calibration | **Implemented** | Platt Sigmoid Scaling, Isotonic Regression, ECE |
| | Evaluation & Validation | **Implemented** | Rolling-origin temporal CV, Brier score, bootstrap CI |
| | Model Artifact Registry | **Implemented** | Metadata lineage tracking & serialized model binaries |
| **Phase 3: Optimization** | Capacity Multi-Order Assignment | **Implemented** | 0/1 Knapsack DP & Capacity Bin-Packing |
| | Multi-Stop Route Sequencing | **Implemented** | 2-opt, 3-opt, Simulated Annealing, GA, OR-Tools |
| | Objective Cost Function | **Implemented** | Documented business cost configuration (`ObjectiveConfig`) |
| **Phase 4: Reinforcement Learning**| Domain Environment | **Implemented** | `LogisticsEnv` with real entity state encoding |
| | Sequential Policy | **Implemented** | PPO Actor-Critic agent, Tabular Q-Learning, DQN |
| **Phase 5: Decision Intelligence** | Grounded Assistant | **Implemented** | Allowlisted tool execution with structured evidence |
| | Persistence Layer | **Implemented** | SQLAlchemy ORM & Repository (SQLite / PostgreSQL) |
| **Phase 6: Interfaces** | FastAPI Service | **Implemented** | REST endpoints, WebSocket telemetry, JWT security |
| | Operations Dashboard | **Implemented** | Streamlit analytics & Vite/TypeScript web client |
| **Phase 7: Research Validation** | Decision Boundary Benchmark | **Implemented** | Prediction-sensitivity vs decision-quality study |

---

## 🧩 Data Structures & Algorithms (DSA) Integration

OPTIMA-X directly integrates classical and advanced computer science data structures into its operational loop:

| Data Structure / Algorithm | Source Module | Logistics Engine Purpose |
| :--- | :--- | :--- |
| **Admissible A\* Algorithm** | `src/dsa/graphs/astar.py` | Heuristic-accelerated shortest path with admissible Haversine lower bound |
| **Dijkstra's Algorithm** | `src/dsa/graphs/dijkstra.py` | Baseline optimal path verification and distance matrix computation |
| **Priority Queue (Min-Heap)** | `src/dsa/heaps/priority_queue.py` | Event loop scheduling and Dijkstra/A\* frontier expansion |
| **Segment Tree** | `src/dsa/trees/segment_tree.py` | $O(\log N)$ dynamic range queries for speed and congestion along time intervals |
| **Fenwick Tree (Binary Indexed)**| `src/dsa/trees/fenwick_tree.py` | $O(\log N)$ rolling cumulative order volume and prefix demand queries |
| **Disjoint Set (Union-Find)** | `src/dsa/union_find/union_find.py`| Road network connected component validation and bridge/island detection |
| **0/1 Knapsack Dynamic Prog.** | `src/optimization/phase3_engine.py`| Optimal parcel subset selection subject to vehicle weight/volume constraints |
| **2-Opt & 3-Opt Local Search** | `src/optimization/routing/` | Combinatorial edge-exchange operators for route tour improvement |
| **Simulated Annealing & GA** | `src/optimization/routing/` | Metaheuristics for multi-stop vehicle schedule optimization |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python $\ge$ 3.11
- Virtual environment tool (`venv` or `uv`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/karthikeya1498/DS-version--1.0.1.git
cd DS-version--1.0.1

# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 3. Run the Master Golden Path Demo
Execute the full 18-step end-to-end demonstration from data loading to decision explanation:
```bash
python scripts/run_demo.py
```

### 4. Run Test Suite
```bash
pytest tests -v
```

### 5. Launch FastAPI Service
```bash
uvicorn api.main:app --reload --port 8000
```
Interactive OpenAPI documentation will be accessible at `http://localhost:8000/docs`.

### 6. Launch Operations Dashboard
```bash
streamlit run dashboard.py
```

---

## 🔬 Phase 7 Research Focus

A central research question explored by OPTIMA-X is:
> **Does higher predictive ML accuracy strictly translate to superior downstream logistics decisions?**

Through controlled perturbation experiments around scenario decision boundaries, OPTIMA-X evaluates the sensitivity of combinatorial assignment and route costs against varying prediction errors ($\pm 5\%$, $\pm 15\%$, $\pm 30\%$).

---

## 📜 License
This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
