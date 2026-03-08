-- HΩ-02: Kinship declaration table for parentesco validation
BEGIN;

CREATE TABLE IF NOT EXISTS core.kinship_declaration (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id               UUID NOT NULL REFERENCES core.ipr(id),
    person_id            UUID NOT NULL REFERENCES core.person(id),
    declaration_type     VARCHAR(32) NOT NULL
                         CHECK (declaration_type IN ('EVALUADOR', 'REPRESENTANTE_LEGAL', 'PERSONAL_CONTRATADO')),
    declares_no_conflict BOOLEAN NOT NULL,
    related_authority_id UUID REFERENCES core.person(id),
    relationship_type    VARCHAR(16)
                         CHECK (relationship_type IS NULL OR relationship_type IN ('CONSANGUINIDAD', 'AFINIDAD')),
    relationship_degree  INT CHECK (relationship_degree IS NULL OR relationship_degree BETWEEN 1 AND 4),
    declared_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    validated_by_id      UUID REFERENCES core."user"(id),
    validated_at         TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at           TIMESTAMPTZ,
    CONSTRAINT uq_kinship_decl UNIQUE (ipr_id, person_id, declaration_type)
);

CREATE INDEX IF NOT EXISTS idx_kinship_declaration_ipr ON core.kinship_declaration(ipr_id);

-- Self-register
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_parentesco.sql', 'manual', 'parentesco_ho02')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
