# Full Architecture v1

OPTIMA-X is now a runnable modular monolith with a stable vertical slice from synthetic data to API response. The primary contract path is `SimulationConfig -> ScenarioGenerator -> EventEngine -> GraphDispatchRouter -> HybridSolver -> OptimizationResult -> API/Explanation`.

Optional research components use dependency-light fallback implementations so the base project remains executable in a clean environment. PyTorch, XGBoost, OR-Tools, MLflow, PostgreSQL, and the frontend can be enabled as the corresponding experiment work matures; the contracts do not require those optional dependencies for local validation.

The implementation intentionally separates **baseline behavior** from future research improvements. A baseline is deterministic, observable, and testable; future model-specific or metaheuristic modules should be benchmarked against it rather than silently replacing it.
