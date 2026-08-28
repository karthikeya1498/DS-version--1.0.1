-- OPTIMA-X canonical PostgreSQL schema, additive to legacy schema.sql.
-- Author: Karthikeya
-- PostgreSQL 16+. All operational timestamps use timestamptz in UTC.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE SCHEMA IF NOT EXISTS optima;
SET search_path TO optima, public;

CREATE TABLE IF NOT EXISTS tenant (
    tenant_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_key text NOT NULL UNIQUE,
    display_name text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (tenant_key ~ '^[a-z0-9][a-z0-9_-]{1,62}$')
);
CREATE TABLE IF NOT EXISTS dataset_version (
    dataset_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid REFERENCES tenant ON DELETE CASCADE,
    name text NOT NULL, version text NOT NULL, source_uri text, content_sha256 char(64),
    schema_version text NOT NULL, row_count bigint CHECK (row_count IS NULL OR row_count >= 0),
    manifest jsonb NOT NULL DEFAULT '{}', created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, name, version), CHECK (content_sha256 IS NULL OR content_sha256 ~ '^[0-9a-f]{64}$')
);
CREATE TABLE IF NOT EXISTS scenario (
    scenario_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid NOT NULL REFERENCES tenant ON DELETE CASCADE,
    dataset_id uuid REFERENCES dataset_version ON DELETE SET NULL, scenario_key text NOT NULL, seed bigint NOT NULL,
    status text NOT NULL DEFAULT 'created' CHECK (status IN ('created','running','completed','failed','archived')),
    config jsonb NOT NULL DEFAULT '{}', starts_at timestamptz NOT NULL, ends_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (tenant_id, scenario_key), CHECK (ends_at IS NULL OR ends_at >= starts_at)
);
CREATE TABLE IF NOT EXISTS location (
    location_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid NOT NULL REFERENCES tenant ON DELETE CASCADE,
    external_key text, zone_id text NOT NULL, latitude numeric(9,6) NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude numeric(9,6) NOT NULL CHECK (longitude BETWEEN -180 AND 180), metadata jsonb NOT NULL DEFAULT '{}',
    UNIQUE (tenant_id, external_key)
);
CREATE TABLE IF NOT EXISTS road_node (
    node_id text PRIMARY KEY, dataset_id uuid REFERENCES dataset_version ON DELETE SET NULL,
    latitude numeric(9,6) NOT NULL CHECK (latitude BETWEEN -90 AND 90), longitude numeric(9,6) NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    metadata jsonb NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS road_edge (
    edge_id text PRIMARY KEY, dataset_id uuid REFERENCES dataset_version ON DELETE SET NULL,
    source_node_id text NOT NULL REFERENCES road_node, target_node_id text NOT NULL REFERENCES road_node,
    distance_km numeric(12,4) NOT NULL CHECK (distance_km >= 0), base_travel_time_sec numeric(12,3) NOT NULL CHECK (base_travel_time_sec > 0),
    base_cost numeric(14,5) NOT NULL CHECK (base_cost >= 0), geometry jsonb, metadata jsonb NOT NULL DEFAULT '{}',
    UNIQUE (dataset_id, source_node_id, target_node_id)
);
CREATE TABLE IF NOT EXISTS vehicle (
    vehicle_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid NOT NULL REFERENCES tenant ON DELETE CASCADE,
    external_key text NOT NULL, capacity_units integer NOT NULL CHECK (capacity_units > 0),
    home_location_id uuid REFERENCES location, status text NOT NULL DEFAULT 'available' CHECK (status IN ('available','dispatched','inactive','maintenance')),
    metadata jsonb NOT NULL DEFAULT '{}', UNIQUE (tenant_id, external_key)
);
CREATE TABLE IF NOT EXISTS vehicle_shift (
    shift_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), vehicle_id uuid NOT NULL REFERENCES vehicle ON DELETE CASCADE,
    scenario_id uuid NOT NULL REFERENCES scenario ON DELETE CASCADE, available_from timestamptz NOT NULL, available_until timestamptz NOT NULL,
    start_location_id uuid REFERENCES location, end_location_id uuid REFERENCES location, CHECK (available_until > available_from),
    EXCLUDE USING gist (vehicle_id WITH =, tstzrange(available_from, available_until, '[)') WITH &&)
);
CREATE TABLE IF NOT EXISTS logistics_order (
    order_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid NOT NULL REFERENCES tenant ON DELETE CASCADE,
    scenario_id uuid NOT NULL REFERENCES scenario ON DELETE CASCADE, external_key text NOT NULL,
    pickup_location_id uuid NOT NULL REFERENCES location, delivery_location_id uuid NOT NULL REFERENCES location,
    demand_units integer NOT NULL CHECK (demand_units > 0), priority smallint NOT NULL DEFAULT 0,
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','assigned','in_transit','delivered','cancelled','failed')),
    window_start timestamptz NOT NULL, window_end timestamptz NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), delivered_at timestamptz,
    metadata jsonb NOT NULL DEFAULT '{}', UNIQUE (tenant_id, external_key), CHECK (window_end > window_start)
);
CREATE INDEX IF NOT EXISTS ix_order_pending_window ON logistics_order (tenant_id, window_start, window_end) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS ix_order_scenario_status_time ON logistics_order (scenario_id, status, created_at DESC);

-- Phase 1/6 high-volume telemetry. Range partition by observation time; create monthly partitions in production.
CREATE TABLE IF NOT EXISTS traffic_history (
    traffic_id uuid NOT NULL DEFAULT gen_random_uuid(), tenant_id uuid NOT NULL REFERENCES tenant ON DELETE CASCADE,
    scenario_id uuid REFERENCES scenario ON DELETE SET NULL, zone_id text NOT NULL, edge_id text REFERENCES road_edge ON DELETE SET NULL,
    observed_at timestamptz NOT NULL, multiplier numeric(8,4) NOT NULL CHECK (multiplier > 0), speed_kph numeric(8,3) CHECK (speed_kph IS NULL OR speed_kph >= 0),
    congestion_level numeric(8,4) CHECK (congestion_level IS NULL OR congestion_level BETWEEN 0 AND 1), source text NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}', PRIMARY KEY (traffic_id, observed_at)
) PARTITION BY RANGE (observed_at);
CREATE TABLE IF NOT EXISTS traffic_history_default PARTITION OF traffic_history DEFAULT;
CREATE INDEX IF NOT EXISTS ix_traffic_tenant_zone_time ON traffic_history (tenant_id, zone_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS ix_traffic_edge_time ON traffic_history (edge_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS ix_traffic_scenario_time ON traffic_history (scenario_id, observed_at DESC);
CREATE TABLE IF NOT EXISTS weather_observation (
    weather_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), dataset_id uuid REFERENCES dataset_version ON DELETE SET NULL,
    observed_at timestamptz NOT NULL, station_id text NOT NULL, zone_id text, condition text, temperature_c numeric(7,3),
    precipitation_mm numeric(10,3) CHECK (precipitation_mm IS NULL OR precipitation_mm >= 0), features jsonb NOT NULL DEFAULT '{}', UNIQUE (station_id, observed_at)
);

-- Phase 2 forecasting and model lineage.
CREATE TABLE IF NOT EXISTS model_version (
    model_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid REFERENCES tenant ON DELETE CASCADE,
    model_name text NOT NULL, model_type text NOT NULL CHECK (model_type IN ('demand','eta','late_risk','policy','other')),
    version text NOT NULL, feature_version text NOT NULL, artifact_uri text, metrics jsonb NOT NULL DEFAULT '{}', created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, model_name, version)
);
CREATE TABLE IF NOT EXISTS demand_prediction (
    prediction_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid NOT NULL REFERENCES tenant ON DELETE CASCADE,
    scenario_id uuid REFERENCES scenario ON DELETE SET NULL, model_id uuid NOT NULL REFERENCES model_version,
    zone_id text NOT NULL, forecast_for timestamptz NOT NULL, generated_at timestamptz NOT NULL DEFAULT now(), horizon_steps integer NOT NULL CHECK (horizon_steps > 0),
    predicted_units numeric(14,4) NOT NULL CHECK (predicted_units >= 0), lower_bound numeric(14,4), upper_bound numeric(14,4), feature_snapshot jsonb NOT NULL DEFAULT '{}',
    UNIQUE (model_id, zone_id, forecast_for, generated_at)
);
CREATE TABLE IF NOT EXISTS eta_prediction (
    eta_prediction_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid NOT NULL REFERENCES tenant ON DELETE CASCADE,
    scenario_id uuid REFERENCES scenario ON DELETE SET NULL, model_id uuid NOT NULL REFERENCES model_version, order_id uuid REFERENCES logistics_order ON DELETE SET NULL,
    edge_id text REFERENCES road_edge ON DELETE SET NULL, generated_at timestamptz NOT NULL DEFAULT now(), predicted_seconds numeric(12,3) NOT NULL CHECK (predicted_seconds >= 0),
    late_probability numeric(8,6) CHECK (late_probability BETWEEN 0 AND 1), feature_snapshot jsonb NOT NULL DEFAULT '{}'
);

-- Phase 3 optimization and route execution.
CREATE TABLE IF NOT EXISTS optimization_run (
    optimization_run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid NOT NULL REFERENCES tenant ON DELETE CASCADE,
    scenario_id uuid NOT NULL REFERENCES scenario ON DELETE CASCADE, algorithm text NOT NULL, solver_version text,
    started_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz, status text NOT NULL CHECK (status IN ('running','completed','failed')),
    objective_value numeric(18,6), total_distance_km numeric(18,6), total_lateness_sec numeric(18,6), feasible boolean, diagnostics jsonb NOT NULL DEFAULT '{}',
    CHECK (completed_at IS NULL OR completed_at >= started_at)
);
CREATE TABLE IF NOT EXISTS route_assignment (
    assignment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), optimization_run_id uuid NOT NULL REFERENCES optimization_run ON DELETE CASCADE,
    vehicle_id uuid NOT NULL REFERENCES vehicle, route_rank integer NOT NULL CHECK (route_rank > 0), assigned_at timestamptz NOT NULL DEFAULT now(), objective_contribution numeric(18,6),
    UNIQUE (optimization_run_id, vehicle_id), UNIQUE (optimization_run_id, route_rank)
);
CREATE TABLE IF NOT EXISTS route_stop (
    stop_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), assignment_id uuid NOT NULL REFERENCES route_assignment ON DELETE CASCADE,
    order_id uuid REFERENCES logistics_order, sequence_no integer NOT NULL CHECK (sequence_no > 0), location_id uuid NOT NULL REFERENCES location,
    planned_arrival timestamptz, planned_departure timestamptz, actual_arrival timestamptz, actual_departure timestamptz, UNIQUE (assignment_id, sequence_no)
);

-- Phase 4 PPO/RL experiments, episodes, and step-level evidence.
CREATE TABLE IF NOT EXISTS rl_experiment (
    experiment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid REFERENCES tenant ON DELETE CASCADE,
    name text NOT NULL, algorithm text NOT NULL DEFAULT 'ppo', policy_model_id uuid REFERENCES model_version, config jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS rl_episode (
    episode_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), experiment_id uuid NOT NULL REFERENCES rl_experiment ON DELETE CASCADE,
    scenario_id uuid NOT NULL REFERENCES scenario ON DELETE CASCADE, seed bigint NOT NULL, episode_no integer NOT NULL CHECK (episode_no > 0),
    total_reward numeric(18,6), win boolean, runtime_ms numeric(18,3), metrics jsonb NOT NULL DEFAULT '{}', UNIQUE (experiment_id, seed, episode_no)
);
CREATE TABLE IF NOT EXISTS rl_step (
    step_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, episode_id uuid NOT NULL REFERENCES rl_episode ON DELETE CASCADE,
    step_no integer NOT NULL CHECK (step_no >= 0), state jsonb NOT NULL, action jsonb NOT NULL, reward numeric(18,6) NOT NULL, next_state jsonb, done boolean NOT NULL DEFAULT false,
    UNIQUE (episode_id, step_no)
);

-- Phase 5 decision intelligence and auditable lineage.
CREATE TABLE IF NOT EXISTS decision_record (
    decision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid NOT NULL REFERENCES tenant ON DELETE CASCADE,
    scenario_id uuid NOT NULL REFERENCES scenario ON DELETE RESTRICT, optimization_run_id uuid REFERENCES optimization_run ON DELETE SET NULL,
    episode_id uuid REFERENCES rl_episode ON DELETE SET NULL, demand_model_id uuid REFERENCES model_version ON DELETE SET NULL,
    eta_model_id uuid REFERENCES model_version ON DELETE SET NULL, policy_model_id uuid REFERENCES model_version ON DELETE SET NULL,
    algorithm text NOT NULL, selected_action jsonb NOT NULL, objective_metrics jsonb NOT NULL DEFAULT '{}', uncertainty jsonb NOT NULL DEFAULT '{}',
    code_commit char(40), state_reference text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
    status text NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed','approved','executed','rejected','superseded')), metadata jsonb NOT NULL DEFAULT '{}',
    CHECK (code_commit IS NULL OR code_commit ~ '^[0-9a-f]{40}$')
);
CREATE INDEX IF NOT EXISTS ix_decision_tenant_scenario_time ON decision_record (tenant_id, scenario_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_decision_tenant_status_time ON decision_record (tenant_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_decision_optimization ON decision_record (optimization_run_id) WHERE optimization_run_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_decision_episode ON decision_record (episode_id) WHERE episode_id IS NOT NULL;
CREATE TABLE IF NOT EXISTS decision_candidate (
    candidate_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), decision_id uuid NOT NULL REFERENCES decision_record ON DELETE CASCADE,
    rank smallint NOT NULL CHECK (rank > 0), action jsonb NOT NULL, objective_metrics jsonb NOT NULL DEFAULT '{}', feasible boolean NOT NULL, rejection_reason text,
    UNIQUE (decision_id, rank)
);
CREATE TABLE IF NOT EXISTS decision_trace (
    trace_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), decision_id uuid NOT NULL REFERENCES decision_record ON DELETE CASCADE,
    parent_trace_id uuid REFERENCES decision_trace ON DELETE SET NULL, component text NOT NULL, event_type text NOT NULL,
    occurred_at timestamptz NOT NULL DEFAULT now(), latency_ms numeric(14,3) CHECK (latency_ms IS NULL OR latency_ms >= 0), payload jsonb NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_trace_decision_time ON decision_trace (decision_id, occurred_at DESC);
CREATE TABLE IF NOT EXISTS evidence_item (
    evidence_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), decision_id uuid NOT NULL REFERENCES decision_record ON DELETE CASCADE,
    evidence_type text NOT NULL, source_table text NOT NULL, source_id text NOT NULL, claim text NOT NULL, value jsonb NOT NULL, captured_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_evidence_decision_time ON evidence_item (decision_id, captured_at DESC);
CREATE TABLE IF NOT EXISTS tool_call (
    tool_call_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), decision_id uuid REFERENCES decision_record ON DELETE CASCADE,
    tenant_id uuid NOT NULL REFERENCES tenant ON DELETE CASCADE, tool_name text NOT NULL, requested_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz,
    success boolean, arguments jsonb NOT NULL DEFAULT '{}', response jsonb, CHECK (completed_at IS NULL OR completed_at >= requested_at)
);
CREATE TABLE IF NOT EXISTS scenario_modification (
    modification_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), decision_id uuid REFERENCES decision_record ON DELETE SET NULL,
    base_scenario_id uuid NOT NULL REFERENCES scenario ON DELETE CASCADE, derived_scenario_id uuid NOT NULL REFERENCES scenario ON DELETE CASCADE,
    requested_by text NOT NULL, changes jsonb NOT NULL, baseline_mutated boolean NOT NULL DEFAULT false CHECK (baseline_mutated = false), created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (base_scenario_id <> derived_scenario_id)
);

-- Phase 6 observability and Phase 7 experiment result storage.
CREATE TABLE IF NOT EXISTS system_event (
    event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id uuid REFERENCES tenant ON DELETE CASCADE,
    event_type text NOT NULL, component text NOT NULL, occurred_at timestamptz NOT NULL DEFAULT now(), correlation_id uuid, payload jsonb NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_event_component_time ON system_event (component, occurred_at DESC);
CREATE TABLE IF NOT EXISTS benchmark_run (
    benchmark_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), experiment_id uuid REFERENCES rl_experiment ON DELETE SET NULL,
    scenario_id uuid REFERENCES scenario ON DELETE SET NULL, algorithm_version text NOT NULL, seed bigint, started_at timestamptz NOT NULL, completed_at timestamptz,
    runtime_ms numeric(18,3), objective_value numeric(18,6), lateness_sec numeric(18,6), feasible boolean, metrics jsonb NOT NULL DEFAULT '{}', CHECK (completed_at IS NULL OR completed_at >= started_at)
);
CREATE INDEX IF NOT EXISTS ix_benchmark_algorithm_scenario ON benchmark_run (algorithm_version, scenario_id);

CREATE OR REPLACE VIEW decision_lineage AS
SELECT d.decision_id, d.tenant_id, d.scenario_id, d.algorithm, d.status, d.created_at,
       d.demand_model_id, d.eta_model_id, d.policy_model_id, o.optimization_run_id, o.objective_value, o.feasible,
       count(DISTINCT c.candidate_id) AS candidate_count, count(DISTINCT t.trace_id) AS trace_count, count(DISTINCT e.evidence_id) AS evidence_count
FROM decision_record d
LEFT JOIN optimization_run o ON o.optimization_run_id = d.optimization_run_id
LEFT JOIN decision_candidate c ON c.decision_id = d.decision_id
LEFT JOIN decision_trace t ON t.decision_id = d.decision_id
LEFT JOIN evidence_item e ON e.decision_id = d.decision_id
GROUP BY d.decision_id, o.optimization_run_id, o.objective_value, o.feasible;

-- Author: Karthikeya. End canonical schema.
