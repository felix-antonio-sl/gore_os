-- Migration: Relax core.rendition FK constraints — coproduct Agreement + IPR
-- Date: 2026-02-27
-- Purpose: Allow renditions linked to IPR (via codigo_bip) without requiring agreement_id.
--          99.75% of renditions are SUBDERE→ONG transfers linked to IPRs, not bilateral agreements.
--
-- Reversible: YES (see goreos_rollback_rendition_coproduct.sql)
-- Idempotent: YES (IF NOT EXISTS / DROP NOT NULL are no-ops if already applied)

BEGIN;

-- 1. Relax agreement_id NOT NULL
ALTER TABLE core.rendition ALTER COLUMN agreement_id DROP NOT NULL;

-- 2. Relax renderer_id NOT NULL (1,770 of 2,030 renderers don't exist in core.organization)
ALTER TABLE core.rendition ALTER COLUMN renderer_id DROP NOT NULL;

-- 3. Add ipr_id FK (the new coproduct leg)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core' AND table_name = 'rendition' AND column_name = 'ipr_id'
    ) THEN
        ALTER TABLE core.rendition ADD COLUMN ipr_id uuid REFERENCES core.ipr(id);
    END IF;
END $$;

-- 4. Index for ipr-linked renditions
CREATE INDEX IF NOT EXISTS idx_rendition_ipr ON core.rendition(ipr_id) WHERE ipr_id IS NOT NULL;

-- 5. Constraint: at least one business link must exist (agreement OR ipr)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_rendition_link' AND conrelid = 'core.rendition'::regclass
    ) THEN
        ALTER TABLE core.rendition ADD CONSTRAINT chk_rendition_link
            CHECK (agreement_id IS NOT NULL OR ipr_id IS NOT NULL);
    END IF;
END $$;

COMMIT;
