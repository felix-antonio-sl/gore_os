-- Rollback: Wave C Migration
BEGIN;

DROP TRIGGER IF EXISTS trg_initiative_timing ON core.dgi_initiative;
DROP FUNCTION IF EXISTS core.trg_initiative_timing_fn();

ALTER TABLE core.dgi_initiative
  DROP COLUMN IF EXISTS started_at,
  DROP COLUMN IF EXISTS completed_at;

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_wave_c.sql';

COMMIT;
