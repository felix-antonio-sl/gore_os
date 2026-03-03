BEGIN;
CREATE TABLE IF NOT EXISTS core.schema_migration (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    checksum VARCHAR(64),
    applied_by VARCHAR(128)
);
-- Register retroactively all existing migrations
INSERT INTO core.schema_migration (filename, applied_by) VALUES
    ('goreos_migration_confrontacion.sql', 'retroactive'),
    ('goreos_migration_wave1_trigger_fix.sql', 'retroactive'),
    ('goreos_migration_rendition_coproduct.sql', 'retroactive'),
    ('goreos_migration_wave5_core_voting.sql', 'retroactive'),
    ('goreos_migration_wave6_act_history.sql', 'retroactive'),
    ('goreos_migration_wave7_evaluation.sql', 'retroactive'),
    ('goreos_migration_wave8_financing_track.sql', 'retroactive'),
    ('goreos_migration_wave9_tracking.sql', 'retroactive')
ON CONFLICT (filename) DO NOTHING;
COMMIT;
