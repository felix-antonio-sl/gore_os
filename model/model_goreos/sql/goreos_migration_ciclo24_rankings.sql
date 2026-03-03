-- Ciclo 24 Wave 3: Evaluation rankings persistence (HΩ-13)

ALTER TABLE core.evaluation_assignment
    ADD COLUMN IF NOT EXISTS rank_position INTEGER;

ALTER TABLE core.evaluation_assignment
    ADD COLUMN IF NOT EXISTS rank_total INTEGER;

ALTER TABLE core.evaluation_assignment
    ADD COLUMN IF NOT EXISTS convocatoria_code VARCHAR(32);

CREATE INDEX IF NOT EXISTS idx_eval_convocatoria
    ON core.evaluation_assignment(convocatoria_code)
    WHERE convocatoria_code IS NOT NULL;
