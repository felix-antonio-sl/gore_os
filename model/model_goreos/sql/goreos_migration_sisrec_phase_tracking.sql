-- SISREC Wave 2: Phase tracking columns for accurate SLA measurement
-- Adds phase_entered_at (replaces updated_at for SLA) + responsible_id (reviewer assignment)
BEGIN;

-- A1: phase_entered_at — timestamp when current state was entered
-- Replaces updated_at for SLA calculations (updated_at resets on ANY update, not just transitions)
ALTER TABLE core.rendition ADD COLUMN IF NOT EXISTS phase_entered_at TIMESTAMPTZ;

-- A2: responsible_id — assigned reviewer for current phase
ALTER TABLE core.rendition ADD COLUMN IF NOT EXISTS responsible_id UUID REFERENCES core."user"(id);

-- A3: Backfill phase_entered_at from updated_at (best approximation for existing data)
UPDATE core.rendition
SET phase_entered_at = updated_at
WHERE phase_entered_at IS NULL;

-- A4: Set default for new renditions
ALTER TABLE core.rendition ALTER COLUMN phase_entered_at SET DEFAULT NOW();

-- A5: Index for responsible lookups (workload filtering)
CREATE INDEX IF NOT EXISTS idx_rendition_responsible
    ON core.rendition(responsible_id)
    WHERE responsible_id IS NOT NULL AND deleted_at IS NULL;

-- A6: Self-register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_sisrec_phase_tracking.sql', 'manual', 'sisrec_wave2_self_register')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
