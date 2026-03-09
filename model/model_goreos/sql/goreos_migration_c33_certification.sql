-- goreos_migration_c33_certification.sql
-- Adds categoria_c33 scheme to ref.category for C33 technical certification routing

BEGIN;

-- Seed categoria_c33 scheme with certifier org routing metadata
INSERT INTO ref.category (scheme, code, label, description, metadata)
VALUES
  ('categoria_c33', 'EDIFICACION', 'Edificación', 'Proyectos de edificación — certificación SERVIU', '{"certifier_org_code": "SERVIU"}'),
  ('categoria_c33', 'VIALIDAD', 'Vialidad', 'Proyectos viales — certificación MOP', '{"certifier_org_code": "MOP"}')
ON CONFLICT (scheme, code) DO NOTHING;

-- Self-register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_c33_certification.sql', 'manual', 'c33_certification_self_register')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
