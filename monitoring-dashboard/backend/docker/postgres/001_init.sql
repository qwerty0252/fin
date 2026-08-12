-- PostgreSQL initialization script

-- Create tables
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(36) PRIMARY KEY,
    transaction_id VARCHAR(255) NOT NULL UNIQUE,
    reference VARCHAR(255) NOT NULL UNIQUE,
    current_state VARCHAR(50) NOT NULL DEFAULT 'INITIATED',
    amount NUMERIC(19, 2) NOT NULL,
    provider VARCHAR(255) NOT NULL,
    merchant VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transaction_id ON transactions(transaction_id);
CREATE INDEX idx_reference ON transactions(reference);
CREATE INDEX idx_current_state ON transactions(current_state);
CREATE INDEX idx_created_at ON transactions(created_at);
CREATE INDEX idx_updated_at ON transactions(updated_at);

CREATE TABLE IF NOT EXISTS transaction_events (
    id VARCHAR(36) PRIMARY KEY,
    transaction_id VARCHAR(36) NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    previous_state VARCHAR(50),
    new_state VARCHAR(50),
    payload JSONB,
    processing_time_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transaction_id_events ON transaction_events(transaction_id);
CREATE INDEX idx_event_type ON transaction_events(event_type);
CREATE INDEX idx_timestamp ON transaction_events(timestamp);

CREATE TABLE IF NOT EXISTS alerts (
    id VARCHAR(36) PRIMARY KEY,
    severity VARCHAR(50) NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_alert_type ON alerts(alert_type);
CREATE INDEX idx_status ON alerts(status);
CREATE INDEX idx_created_at_alerts ON alerts(created_at);

CREATE TABLE IF NOT EXISTS services (
    id VARCHAR(36) PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'UNKNOWN',
    last_heartbeat TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details JSONB,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metrics (
    id VARCHAR(36) PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value NUMERIC(20, 4) NOT NULL,
    labels JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metric_name ON metrics(metric_name);
CREATE INDEX idx_metric_timestamp ON metrics(timestamp);
