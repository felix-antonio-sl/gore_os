-- Critical indexes identified in C59 audit
-- document table (12,800 rows, 868 seq_scans vs 3 idx_scans)
CREATE INDEX IF NOT EXISTS idx_document_ipr_id ON core.document (ipr_id) WHERE ipr_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_document_agreement_id ON core.document (agreement_id) WHERE agreement_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_document_type_id ON core.document (document_type_id);

-- budget_program table (25,767 rows, largest table)
CREATE INDEX IF NOT EXISTS idx_budget_program_division ON core.budget_program (owner_division_id) WHERE owner_division_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_budget_program_fiscal_year ON core.budget_program (fiscal_year, owner_division_id);

-- rendition table (1,295 rows)
CREATE INDEX IF NOT EXISTS idx_rendition_state ON core.rendition (state_id) WHERE deleted_at IS NULL;

-- Remove duplicate GIN index on ipr.metadata (keep jsonb_path_ops)
DROP INDEX IF EXISTS core.idx_ipr_metadata_gin;

-- Record migration
INSERT INTO core.schema_migration (filename, applied_at, checksum, applied_by)
VALUES ('goreos_migration_critical_indexes.sql', NOW(), 'c59-audit-indexes', 'claude-c59')
ON CONFLICT (filename) DO NOTHING;
