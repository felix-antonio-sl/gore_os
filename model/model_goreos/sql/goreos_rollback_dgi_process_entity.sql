-- ============================================================================
-- Rollback: DGI Process as Entity
-- Reverses goreos_migration_dgi_process_entity.sql
-- ============================================================================

BEGIN;

-- 1. Restore dgi_bpmn_model columns before dropping process tables
ALTER TABLE core.dgi_bpmn_model ADD COLUMN IF NOT EXISTS process_name VARCHAR(200);
ALTER TABLE core.dgi_bpmn_model ADD COLUMN IF NOT EXISTS division_id UUID REFERENCES core.organization(id);

-- Restore process_name and division_id from dgi_process
UPDATE core.dgi_bpmn_model b
SET process_name = p.name,
    division_id = p.division_id
FROM core.dgi_process p
WHERE p.id = b.process_id;

-- Drop the FK and new columns
ALTER TABLE core.dgi_bpmn_model DROP COLUMN IF EXISTS process_id;
ALTER TABLE core.dgi_bpmn_model DROP COLUMN IF EXISTS bpmn_type_id;
DROP INDEX IF EXISTS core.idx_dgi_bpmn_model_process;

-- Make process_name NOT NULL again
UPDATE core.dgi_bpmn_model SET process_name = 'UNKNOWN' WHERE process_name IS NULL;
ALTER TABLE core.dgi_bpmn_model ALTER COLUMN process_name SET NOT NULL;

-- 2. Drop new tables (reverse dependency order)
DROP TABLE IF EXISTS core.dgi_improvement_opportunity;
DROP TABLE IF EXISTS core.dgi_process_pain_point;
DROP TABLE IF EXISTS core.dgi_process_metric;
DROP TABLE IF EXISTS core.dgi_process_rule;
DROP TABLE IF EXISTS core.dgi_process_actor;
DROP TABLE IF EXISTS core.dgi_process;

-- 3. Drop Categorical Univocity CHECKs added for debt repair
ALTER TABLE core.dgi_indicator DROP CONSTRAINT IF EXISTS chk_dgi_indicator_dimension;
ALTER TABLE core.dgi_indicator DROP CONSTRAINT IF EXISTS chk_dgi_indicator_signal;
ALTER TABLE core.dgi_initiative DROP CONSTRAINT IF EXISTS chk_dgi_initiative_status;
ALTER TABLE core.dgi_initiative DROP CONSTRAINT IF EXISTS chk_dgi_initiative_dmaic_phase;
ALTER TABLE core.dgi_bpmn_model DROP CONSTRAINT IF EXISTS chk_dgi_bpmn_model_status;
ALTER TABLE core.dgi_bpmn_model DROP CONSTRAINT IF EXISTS chk_dgi_bpmn_model_type;
ALTER TABLE core.dgi_committee_session DROP CONSTRAINT IF EXISTS chk_dgi_committee_session_status;
ALTER TABLE core.dgi_data_source_status DROP CONSTRAINT IF EXISTS chk_dgi_data_source_status;
ALTER TABLE core.dgi_report DROP CONSTRAINT IF EXISTS chk_dgi_report_type;
ALTER TABLE core.dgi_report DROP CONSTRAINT IF EXISTS chk_dgi_report_status;

-- 4. Remove new schemes
DELETE FROM ref.category WHERE scheme IN ('dgi_process_status', 'dgi_bpmn_type');

-- 5. Unregister migration
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_dgi_process_entity.sql';

COMMIT;
