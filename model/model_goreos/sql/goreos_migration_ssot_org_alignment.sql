-- ============================================================================
-- Migration: SSOT Organizational Alignment
-- Date: 2026-03-15
-- Purpose: Align organization codes, types, and roles with SSOT canonical
--          definitions (ssot-organica.md, kb_gn_002_organigrama.md).
--
-- Changes:
--   1. Add missing org_types (STAFF_UNIT, ADVISORY_BODY, etc.)
--   2. Rename DIFOT → DIFOI, DIDERSO → DIDESO
--   3. Reparent DIDECO FKs → DGI, soft-delete DIDECO
--   4. Reclassify DGI as STAFF_UNIT
--   5. Fix DIPIR name, GABINETE name
--   6. Collapse ENCARGADO role (soft-delete, remap users to ANALISTA)
--   7. Add missing system_roles to ref.category
-- ============================================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. Ensure org_types exist
-- ═══════════════════════════════════════════════════════════════════════════
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('org_type', 'STAFF_UNIT', 'Unidad de Staff', 'Dependencia directa del Gobernador/a o Administrador/a Regional', 11),
('org_type', 'ADVISORY_BODY', 'Cuerpo Asesor', 'Órgano colegiado de asesoría', 12),
('org_type', 'ORG_COMUNITARIA', 'Organización Comunitaria', 'Organización de la sociedad civil', 13),
('org_type', 'COMUNITARIA', 'Comunidad', 'Comunidad territorial', 14)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. Ensure all 15 system_roles exist (ENCARGADO handled in step 6)
-- ═══════════════════════════════════════════════════════════════════════════
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('system_role', 'GOBERNADOR', 'Gobernador Regional', 'Autoridad ejecutiva máxima. Firma actos, preside CORE', 0),
('system_role', 'CONSEJERO_REGIONAL', 'Consejero Regional', 'Miembro del Consejo Regional, vota IPRs >7K UTM', 9),
('system_role', 'SECRETARIO_EJECUTIVO', 'Secretario Ejecutivo', 'Secretaría Ejecutiva del CORE', 10),
('system_role', 'JEFE_DEPARTAMENTO', 'Jefe de Departamento', 'Supervisa departamento dentro de una división', 11),
('system_role', 'JEFE_UNIDAD', 'Jefe de Unidad', 'Supervisa unidad operativa', 12),
('system_role', 'ANALISTA', 'Analista', 'Formula IPR F0-F3, evalúa admisibilidad, registra evaluaciones', 13),
('system_role', 'RTF', 'Referente Técnico-Financiero', 'Analista Otorgante SISREC, revisa rendiciones 7d SLA', 14),
('system_role', 'ASESOR_JURIDICO', 'Asesor Jurídico', 'V.B. legalidad de actos administrativos y convenios', 15)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. Rename DIFOT → DIFOI (if DIFOI doesn't already exist)
-- ═══════════════════════════════════════════════════════════════════════════
DO $$
DECLARE
    v_difoi_exists BOOLEAN;
    v_difot_id UUID;
    v_difoi_id UUID;
BEGIN
    SELECT EXISTS(SELECT 1 FROM core.organization WHERE code = 'DIFOI' AND deleted_at IS NULL) INTO v_difoi_exists;
    SELECT id INTO v_difot_id FROM core.organization WHERE code = 'DIFOT' AND deleted_at IS NULL;

    IF v_difot_id IS NOT NULL THEN
        IF v_difoi_exists THEN
            -- Both exist: merge FKs from DIFOT → DIFOI, soft-delete DIFOT
            SELECT id INTO v_difoi_id FROM core.organization WHERE code = 'DIFOI' AND deleted_at IS NULL;
            UPDATE core."user" SET division_id = v_difoi_id WHERE division_id = v_difot_id;
            UPDATE core.ipr SET sponsor_division_id = v_difoi_id WHERE sponsor_division_id = v_difot_id;
            UPDATE core.budget_program SET owner_division_id = v_difoi_id WHERE owner_division_id = v_difot_id;
            UPDATE core.agreement SET giver_id = v_difoi_id WHERE giver_id = v_difot_id;
            UPDATE core.agreement SET receiver_id = v_difoi_id WHERE receiver_id = v_difot_id;
            UPDATE core.ipr_party SET organization_id = v_difoi_id WHERE organization_id = v_difot_id;
            -- core.risk has no division_id — scoped via subject_id→ipr
            UPDATE core.organization SET deleted_at = NOW() WHERE id = v_difot_id;
            RAISE NOTICE 'DIFOT merged into DIFOI, soft-deleted';
        ELSE
            -- Only DIFOT exists: rename
            UPDATE core.organization SET code = 'DIFOI', name = 'División de Fomento e Industria' WHERE id = v_difot_id;
            RAISE NOTICE 'DIFOT renamed to DIFOI';
        END IF;
    END IF;
END $$;

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. Rename DIDERSO → DIDESO (same pattern)
-- ═══════════════════════════════════════════════════════════════════════════
DO $$
DECLARE
    v_dideso_exists BOOLEAN;
    v_diderso_id UUID;
    v_dideso_id UUID;
BEGIN
    SELECT EXISTS(SELECT 1 FROM core.organization WHERE code = 'DIDESO' AND deleted_at IS NULL) INTO v_dideso_exists;
    SELECT id INTO v_diderso_id FROM core.organization WHERE code = 'DIDERSO' AND deleted_at IS NULL;

    IF v_diderso_id IS NOT NULL THEN
        IF v_dideso_exists THEN
            SELECT id INTO v_dideso_id FROM core.organization WHERE code = 'DIDESO' AND deleted_at IS NULL;
            UPDATE core."user" SET division_id = v_dideso_id WHERE division_id = v_diderso_id;
            UPDATE core.ipr SET sponsor_division_id = v_dideso_id WHERE sponsor_division_id = v_diderso_id;
            UPDATE core.budget_program SET owner_division_id = v_dideso_id WHERE owner_division_id = v_diderso_id;
            UPDATE core.agreement SET giver_id = v_dideso_id WHERE giver_id = v_diderso_id;
            UPDATE core.agreement SET receiver_id = v_dideso_id WHERE receiver_id = v_diderso_id;
            UPDATE core.ipr_party SET organization_id = v_dideso_id WHERE organization_id = v_diderso_id;
            -- core.risk has no division_id — scoped via subject_id→ipr
            UPDATE core.organization SET deleted_at = NOW() WHERE id = v_diderso_id;
            RAISE NOTICE 'DIDERSO merged into DIDESO, soft-deleted';
        ELSE
            UPDATE core.organization SET code = 'DIDESO', name = 'División de Desarrollo Social y Humano' WHERE id = v_diderso_id;
            RAISE NOTICE 'DIDERSO renamed to DIDESO';
        END IF;
    END IF;
END $$;

-- ═══════════════════════════════════════════════════════════════════════════
-- 5. Reparent DIDECO FKs → DGI, soft-delete DIDECO
-- ═══════════════════════════════════════════════════════════════════════════
DO $$
DECLARE
    v_dideco_id UUID;
    v_dgi_id UUID;
BEGIN
    SELECT id INTO v_dideco_id FROM core.organization WHERE code = 'DIDECO' AND deleted_at IS NULL;
    SELECT id INTO v_dgi_id FROM core.organization WHERE code = 'DGI' AND deleted_at IS NULL;

    IF v_dideco_id IS NOT NULL AND v_dgi_id IS NOT NULL THEN
        UPDATE core."user" SET division_id = v_dgi_id WHERE division_id = v_dideco_id;
        UPDATE core.ipr SET sponsor_division_id = v_dgi_id WHERE sponsor_division_id = v_dideco_id;
        UPDATE core.budget_program SET owner_division_id = v_dgi_id WHERE owner_division_id = v_dideco_id;
        UPDATE core.agreement SET giver_id = v_dgi_id WHERE giver_id = v_dideco_id;
        UPDATE core.agreement SET receiver_id = v_dgi_id WHERE receiver_id = v_dideco_id;
        UPDATE core.ipr_party SET organization_id = v_dgi_id WHERE organization_id = v_dideco_id;
        -- core.risk has no division_id — scoped via subject_id→ipr
        UPDATE core.committee SET parent_org_id = v_dgi_id WHERE parent_org_id = v_dideco_id;
        UPDATE core.organization SET deleted_at = NOW() WHERE id = v_dideco_id;
        RAISE NOTICE 'DIDECO FKs reparented to DGI, DIDECO soft-deleted';
    END IF;
END $$;

-- ═══════════════════════════════════════════════════════════════════════════
-- 6. Reclassify DGI as STAFF_UNIT (was DEPARTAMENTO from confrontacion)
-- ═══════════════════════════════════════════════════════════════════════════
UPDATE core.organization
SET org_type_id = (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'STAFF_UNIT'),
    name = 'Depto. de Gestión Institucional'
WHERE code = 'DGI' AND deleted_at IS NULL;

-- Also fix DIJ and GABINETE types (guard — may already be correct)
UPDATE core.organization
SET org_type_id = (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'STAFF_UNIT'),
    name = 'Depto. Jurídico'
WHERE code = 'DIJ' AND deleted_at IS NULL
  AND org_type_id != (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'STAFF_UNIT');

UPDATE core.organization
SET org_type_id = (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'STAFF_UNIT'),
    name = 'Gabinete y Participación Social'
WHERE code = 'GABINETE' AND deleted_at IS NULL
  AND org_type_id != (SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'STAFF_UNIT');

-- ═══════════════════════════════════════════════════════════════════════════
-- 7. Fix DIPIR name
-- ═══════════════════════════════════════════════════════════════════════════
UPDATE core.organization
SET name = 'División de Presupuesto e Inversión Regional'
WHERE code = 'DIPIR' AND deleted_at IS NULL;

-- ═══════════════════════════════════════════════════════════════════════════
-- 8. Collapse ENCARGADO role
-- ═══════════════════════════════════════════════════════════════════════════
-- Remap ENCARGADO users → ANALISTA
UPDATE core."user"
SET system_role_id = (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'ANALISTA')
WHERE system_role_id = (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'ENCARGADO');

-- Mark ENCARGADO as deprecated (ref.category has no is_active — use description + sort_order)
-- Cannot DELETE due to referential integrity (historical user records may reference it)
UPDATE ref.category
SET description = 'DEPRECATED — collapsed into ANALISTA. Encargado is a dynamic assignment, not a system role.',
    sort_order = 99
WHERE scheme = 'system_role' AND code = 'ENCARGADO';

-- ═══════════════════════════════════════════════════════════════════════════
-- 9. Record migration
-- ═══════════════════════════════════════════════════════════════════════════
INSERT INTO core.schema_migration (filename, applied_at, checksum, applied_by)
VALUES ('goreos_migration_ssot_org_alignment.sql', NOW(), md5('ssot-org-alignment-v1'), 'claude')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
