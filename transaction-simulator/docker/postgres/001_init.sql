CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY,
    reference VARCHAR(100) UNIQUE NOT NULL,
    account_number VARCHAR(32) NOT NULL,
    amount NUMERIC(18,2) NOT NULL,
    currency VARCHAR(8) NOT NULL,
    channel VARCHAR(32) NOT NULL,
    transaction_type VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    idempotency_key VARCHAR(128) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transaction_events (
    id SERIAL PRIMARY KEY,
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS retries (
    id SERIAL PRIMARY KEY,
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    retry_count INTEGER NOT NULL DEFAULT 0,
    next_retry_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reversals (
    id SERIAL PRIMARY KEY,
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transaction_events_tx_id ON transaction_events(transaction_id);
CREATE INDEX IF NOT EXISTS idx_retries_tx_id ON retries(transaction_id);
CREATE INDEX IF NOT EXISTS idx_reversals_tx_id ON reversals(transaction_id);
