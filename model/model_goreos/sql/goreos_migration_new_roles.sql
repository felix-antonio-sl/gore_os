-- ============================================================================
-- GORE_OS — Migración: 3 nuevos roles para ciclo de vida IPR
-- ============================================================================
-- ANALISTA (13): Formula IPR, admisibilidad, evaluación (F0-F3)
-- RTF (14): Referente Técnico-Financiero, revisión SISREC (F5)
-- ASESOR_JURIDICO (15): V.B. legalidad actos y convenios (F4)
--
-- Prerequisito: Ejecutar contra goreos_model
--   docker exec -i goreos_db psql -U goreos -d goreos_model < goreos_migration_new_roles.sql
--
-- Rollback: goreos_rollback_new_roles.sql
-- ============================================================================

BEGIN;

-- ── Op 1: 3 nuevos system_role ──────────────────────────────────────────────

INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES
  ('system_role', 'ANALISTA', 'Analista',
   'Formula IPR, ejecuta admisibilidad, registra evaluaciones, carga documentos.', 13),
  ('system_role', 'RTF', 'Referente Técnico-Financiero',
   'Revisa rendiciones SISREC, observa/aprueba, controla SLAs.', 14),
  ('system_role', 'ASESOR_JURIDICO', 'Asesor Jurídico',
   'V.B. legalidad de actos administrativos y convenios.', 15)
ON CONFLICT (scheme, code) DO NOTHING;

-- ── Op 2: Personas para usuarios de test ────────────────────────────────────

INSERT INTO core.person (id, names, paternal_surname, email, is_active)
VALUES
  ('a0000001-0000-0000-0000-000000000010', 'Felipe', 'Morales', 'analista.dipir@goreos.cl', true),
  ('a0000001-0000-0000-0000-000000000011', 'Claudia', 'Sepúlveda', 'analista.diplade@goreos.cl', true),
  ('a0000001-0000-0000-0000-000000000012', 'Diego', 'Fuentes', 'rtf.daf@goreos.cl', true),
  ('a0000001-0000-0000-0000-000000000013', 'Valentina', 'Bravo', 'juridico@goreos.cl', true)
ON CONFLICT (id) DO NOTHING;

-- ── Op 3: Usuarios de test ──────────────────────────────────────────────────

DO $$
DECLARE
    v_analista UUID;
    v_rtf UUID;
    v_juridico UUID;
    v_dipir UUID;
    v_diplade UUID;
    v_daf UUID;
    v_hash TEXT := '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe';
BEGIN
    SELECT id INTO v_analista FROM ref.category WHERE scheme='system_role' AND code='ANALISTA';
    SELECT id INTO v_rtf FROM ref.category WHERE scheme='system_role' AND code='RTF';
    SELECT id INTO v_juridico FROM ref.category WHERE scheme='system_role' AND code='ASESOR_JURIDICO';

    SELECT id INTO v_dipir FROM core.organization WHERE code='DIPIR';
    SELECT id INTO v_diplade FROM core.organization WHERE code='DIPLADE';
    SELECT id INTO v_daf FROM core.organization WHERE code='DAF';

    -- Analista DIPIR
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000010', 'analista.dipir@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000010', v_analista, v_dipir, true)
    ON CONFLICT (id) DO NOTHING;

    -- Analista DIPLADE
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000011', 'analista.diplade@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000011', v_analista, v_diplade, true)
    ON CONFLICT (id) DO NOTHING;

    -- RTF DAF
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000012', 'rtf.daf@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000012', v_rtf, v_daf, true)
    ON CONFLICT (id) DO NOTHING;

    -- Asesor Jurídico (sin división — staff unit)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000013', 'juridico@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000013', v_juridico, true)
    ON CONFLICT (id) DO NOTHING;

    RAISE NOTICE 'New roles + test users seeded: 3 roles, 4 users';
END $$;

-- ── Op 4: Registrar migración ───────────────────────────────────────────────

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_new_roles.sql', 'claude-code')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
