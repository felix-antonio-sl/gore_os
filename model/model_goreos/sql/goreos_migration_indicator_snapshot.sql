-- Migration: DGI indicator snapshot for time series tracking
-- Captures historical values on each refresh.

CREATE TABLE IF NOT EXISTS core.dgi_indicator_snapshot (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_id UUID REFERENCES core.dgi_indicator(id) ON DELETE CASCADE NOT NULL,
    value NUMERIC(18,4),
    signal_id UUID REFERENCES ref.category(id),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_indicator_snapshot_lookup
    ON core.dgi_indicator_snapshot(indicator_id, recorded_at);
