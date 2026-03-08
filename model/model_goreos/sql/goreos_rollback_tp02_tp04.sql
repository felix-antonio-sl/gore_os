-- Rollback: TP-02 subv8_fund + ceilings, TP-04 fril_category
BEGIN;

DROP INDEX IF EXISTS core.uq_subv8_ceiling_fund_type_area;
DROP INDEX IF EXISTS core.idx_subv8_fund_ceiling_fund;
DROP TABLE IF EXISTS core.subv8_fund_ceiling;
DROP TABLE IF EXISTS core.subv8_fund;
DROP TABLE IF EXISTS core.fril_category;

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_tp02_tp04.sql';

COMMIT;
