BEGIN;

-- ============================================================
-- Migration: Admissibility Sub-states (PRE_ADMISIBLE)
-- Date: 2026-03-09
-- Description: Adds PRE_ADMISIBLE state between EN_REVISION and
--   ADMISIBLE, plus parametric checklist tables per track.
-- ============================================================

-- 1. Shift sort_order to make room for PRE_ADMISIBLE at position 3
UPDATE ref.category
SET sort_order = sort_order + 1
WHERE scheme = 'ipr_state'
  AND sort_order >= 3
  AND code != 'PRE_ADMISIBLE';

-- 2. New ipr_state: PRE_ADMISIBLE
INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES ('ipr_state', 'PRE_ADMISIBLE', 'Pre-admisible',
        'Verificación de admisibilidad en curso', 3)
ON CONFLICT (scheme, code) DO NOTHING;

-- 3. Update valid_transitions: EN_REVISION now goes to PRE_ADMISIBLE (not ADMISIBLE)
UPDATE ref.category
SET valid_transitions = '["PRE_ADMISIBLE", "INADMISIBLE"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_REVISION';

-- PRE_ADMISIBLE can advance to ADMISIBLE or reject to INADMISIBLE
UPDATE ref.category
SET valid_transitions = '["ADMISIBLE", "INADMISIBLE"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'PRE_ADMISIBLE';

-- 4. Parametric table: checklist items per financing track
CREATE TABLE IF NOT EXISTS core.admissibility_item (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  financing_track_id UUID NOT NULL REFERENCES core.financing_track(id),
  code VARCHAR(50) NOT NULL,
  label TEXT NOT NULL,
  description TEXT,
  responsible_role VARCHAR(50) NOT NULL,
  sort_order INT DEFAULT 0,
  is_required BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ,
  CONSTRAINT uq_admissibility_item_track_code UNIQUE(financing_track_id, code)
);

-- 5. Operational table: verification checks per IPR
CREATE TABLE IF NOT EXISTS core.admissibility_check (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ipr_id UUID NOT NULL REFERENCES core.ipr(id),
  item_id UUID NOT NULL REFERENCES core.admissibility_item(id),
  verified_by_id UUID NOT NULL REFERENCES core."user"(id),
  verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT uq_admissibility_check_ipr_item UNIQUE(ipr_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_admissibility_check_ipr
  ON core.admissibility_check(ipr_id);

-- 6. Self-register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_admissibility.sql', 'manual', 'admissibility_substates')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
