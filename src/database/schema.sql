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
CREATE TABLE IF NOT EXISTS traffic (
    observed_at TIMESTAMPTZ NOT NULL,
    zone_id TEXT NOT NULL,
    multiplier DOUBLE PRECISION NOT NULL CHECK (multiplier > 0),
    PRIMARY KEY (observed_at, zone_id)
);
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
