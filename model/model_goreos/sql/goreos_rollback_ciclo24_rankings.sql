-- Rollback Ciclo 24 Wave 3: Remove evaluation rankings columns

DROP INDEX IF EXISTS core.idx_eval_convocatoria;

ALTER TABLE core.evaluation_assignment DROP COLUMN IF EXISTS convocatoria_code;
ALTER TABLE core.evaluation_assignment DROP COLUMN IF EXISTS rank_total;
ALTER TABLE core.evaluation_assignment DROP COLUMN IF EXISTS rank_position;
