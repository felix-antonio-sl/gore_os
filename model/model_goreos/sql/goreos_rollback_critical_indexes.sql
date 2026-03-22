-- Rollback: goreos_migration_critical_indexes.sql

DROP INDEX IF EXISTS core.idx_document_ipr_id;
DROP INDEX IF EXISTS core.idx_document_agreement_id;
DROP INDEX IF EXISTS core.idx_document_type_id;

DROP INDEX IF EXISTS core.idx_budget_program_division;
DROP INDEX IF EXISTS core.idx_budget_program_fiscal_year;

DROP INDEX IF EXISTS core.idx_rendition_state;

-- Note: idx_ipr_metadata_gin is NOT restored — it was a duplicate of the jsonb_path_ops index

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_critical_indexes.sql';
