-- OPTIMA-X Phase 1 operational schema
CREATE TABLE IF NOT EXISTS nodes (
    node_id TEXT PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS edges (
    edge_id BIGSERIAL PRIMARY KEY,
    source_node_id TEXT NOT NULL REFERENCES nodes(node_id),
    target_node_id TEXT NOT NULL REFERENCES nodes(node_id),
    distance_km DOUBLE PRECISION NOT NULL CHECK (distance_km >= 0),
    travel_time_min DOUBLE PRECISION NOT NULL CHECK (travel_time_min > 0),
    cost DOUBLE PRECISION NOT NULL CHECK (cost >= 0),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (source_node_id, target_node_id)
);
CREATE INDEX IF NOT EXISTS edges_source_idx ON edges(source_node_id);
CREATE INDEX IF NOT EXISTS edges_target_idx ON edges(target_node_id);
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id TEXT PRIMARY KEY,
    capacity_units INTEGER NOT NULL CHECK (capacity_units > 0),
    current_node_id TEXT NOT NULL REFERENCES nodes(node_id),
    available_from TIMESTAMPTZ NOT NULL,
    available_until TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'available',
    CHECK (available_until > available_from)
);
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    pickup_node_id TEXT NOT NULL REFERENCES nodes(node_id),
    destination_node_id TEXT NOT NULL REFERENCES nodes(node_id),
    demand_units INTEGER NOT NULL CHECK (demand_units > 0),
    priority INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    CHECK (window_end > window_start)
);
CREATE INDEX IF NOT EXISTS orders_created_idx ON orders(created_at);
CREATE INDEX IF NOT EXISTS orders_status_window_idx ON orders(status, window_start, window_end);
CREATE TABLE IF NOT EXISTS traffic (
    observed_at TIMESTAMPTZ NOT NULL,
    zone_id TEXT NOT NULL,
    multiplier DOUBLE PRECISION NOT NULL CHECK (multiplier > 0),
    PRIMARY KEY (observed_at, zone_id)
);
CREATE INDEX IF NOT EXISTS traffic_zone_observed_idx ON traffic(zone_id, observed_at DESC);
CREATE TABLE IF NOT EXISTS weather (
    observed_at TIMESTAMPTZ NOT NULL,
    zone_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    temperature_c DOUBLE PRECISION,
    precipitation_mm DOUBLE PRECISION CHECK (precipitation_mm IS NULL OR precipitation_mm >= 0),
    PRIMARY KEY (observed_at, zone_id)
);
CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id TEXT PRIMARY KEY,
    seed BIGINT NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS decision_records (
    decision_id TEXT PRIMARY KEY,
    scenario_id TEXT NOT NULL REFERENCES scenarios(scenario_id),
    state_reference TEXT NOT NULL,
    dataset_version TEXT NOT NULL,
    model_versions JSONB NOT NULL DEFAULT '{}'::jsonb,
    solver_version TEXT NOT NULL,
    rl_policy_version TEXT NOT NULL DEFAULT '',
    selected_action TEXT NOT NULL,
    objective_metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    code_commit TEXT NOT NULL DEFAULT '',
    experiment_id TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS decision_records_scenario_created_idx
    ON decision_records(scenario_id, created_at DESC);

CREATE TABLE IF NOT EXISTS decision_candidates (
    candidate_id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL REFERENCES decision_records(decision_id),
    action TEXT NOT NULL,
    feasible BOOLEAN NOT NULL,
    objective DOUBLE PRECISION NOT NULL,
    rejection_reason TEXT NOT NULL DEFAULT '',
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS decision_traces_decision_created_idx
    ON decision_traces(decision_id, created_at DESC);

CREATE TABLE IF NOT EXISTS decision_traces (
    trace_id BIGSERIAL PRIMARY KEY,
    decision_id TEXT NOT NULL REFERENCES decision_records(decision_id),
    trace JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS tool_calls (
    tool_call_id BIGSERIAL PRIMARY KEY,
    decision_id TEXT,
    tool_name TEXT NOT NULL,
    arguments JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB NOT NULL DEFAULT '{}'::jsonb,
    grounded BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS explanations (
    explanation_id BIGSERIAL PRIMARY KEY,
    decision_id TEXT NOT NULL REFERENCES decision_records(decision_id),
    prompt_version TEXT NOT NULL,
    model_version TEXT NOT NULL DEFAULT '',
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS scenario_modifications (
    modification_id BIGSERIAL PRIMARY KEY,
    scenario_id TEXT NOT NULL REFERENCES scenarios(scenario_id),
    demand_multiplier DOUBLE PRECISION NOT NULL CHECK (demand_multiplier >= 0),
    traffic_multiplier DOUBLE PRECISION NOT NULL CHECK (traffic_multiplier >= 0),
    unavailable_vehicle_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    lateness_weight DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
