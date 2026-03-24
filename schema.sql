CREATE TABLE IF NOT EXISTS briefings (
    id SERIAL PRIMARY KEY,
    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    period VARCHAR(20) NOT NULL CHECK (period IN ('morning', 'afternoon')),
    content TEXT NOT NULL,
    source_counts JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS raw_items (
    id SERIAL PRIMARY KEY,
    briefing_id INTEGER REFERENCES briefings(id) ON DELETE CASCADE,
    source VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    dedup_hash VARCHAR(64) NOT NULL UNIQUE,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscribers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    subscribed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    unsubscribe_token VARCHAR(64) NOT NULL UNIQUE,
    fail_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS delivery_log (
    id SERIAL PRIMARY KEY,
    briefing_id INTEGER REFERENCES briefings(id) ON DELETE CASCADE,
    subscriber_id INTEGER REFERENCES subscribers(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('sent', 'failed')),
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    error_msg TEXT
);

CREATE INDEX IF NOT EXISTS idx_briefings_run_at ON briefings(run_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_items_dedup ON raw_items(dedup_hash);
CREATE INDEX IF NOT EXISTS idx_delivery_log_briefing ON delivery_log(briefing_id);
CREATE INDEX IF NOT EXISTS idx_delivery_log_subscriber ON delivery_log(subscriber_id);
