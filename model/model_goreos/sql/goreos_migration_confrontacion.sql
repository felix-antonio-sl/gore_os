-- ============================================================================
-- GORE_OS — Migración Categórica de Datos: Alineación con Informe de Confrontación
-- ============================================================================
--
-- Endofuntor Σ_f : C → C — Solo enriquece instancias (ABox), no toca estructura (TBox).
-- 7 operaciones atómicas. Todas idempotentes (ON CONFLICT / WHERE guards).
--
-- Prerequisito: Ejecutar contra goreos_model
--   docker exec -i goreos_db psql -U goreos -d goreos_model < goreos_migration_confrontacion.sql
--
-- Rollback: goreos_rollback_confrontacion.sql
-- ============================================================================

BEGIN;

-- ────────────────────────────────────────────────────────────────────────────
-- Op 1: Expandir Cat_{org_type} — 2 nuevos objetos en la fibra
-- ────────────────────────────────────────────────────────────────────────────
-- Agrega STAFF_UNIT y ADVISORY_BODY para discriminar unidades asesoras
-- del tipo DIVISION (que actualmente absorbe 25 de 31 orgs internas).

INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES
  ('org_type', 'STAFF_UNIT', 'Unidad de Staff',
   'gnub:StaffUnit — Unidad asesora/apoyo directo a autoridad (Gobernador o AR)', 11),
  ('org_type', 'ADVISORY_BODY', 'Órgano Asesor',
   'gnub:AdvisoryBody — Órgano colegiado asesor/consultivo (CORE, COSOC, CTCI)', 12)
ON CONFLICT (scheme, code) DO NOTHING;


-- ────────────────────────────────────────────────────────────────────────────
-- Op 2: Reclasificar fibras en Org — UPDATEs de org_type_id
-- ────────────────────────────────────────────────────────────────────────────
-- Cambia solo el clasificador org_type_id. No renombra code ni name.

-- STAFF_UNIT (6 orgs: gabinete, comunicaciones, auditoría, jurídica, ñuble-250, CIES)
UPDATE core.organization SET org_type_id = (
  SELECT id FROM ref.category WHERE scheme='org_type' AND code='STAFF_UNIT'
) WHERE code IN ('GABINETE','COMUNICACIONES','AUDITORIA','DIJ','NUBLE-250','CIES')
  AND deleted_at IS NULL;

-- ADVISORY_BODY (1 org: CORE — Consejo Regional)
UPDATE core.organization SET org_type_id = (
  SELECT id FROM ref.category WHERE scheme='org_type' AND code='ADVISORY_BODY'
) WHERE code = 'CORE' AND deleted_at IS NULL;

-- DEPARTAMENTO (5 orgs)
UPDATE core.organization SET org_type_id = (
  SELECT id FROM ref.category WHERE scheme='org_type' AND code='DEPARTAMENTO'
) WHERE code IN ('FINANZAS','INVERSIONES','PRESUPUESTO','PERSONAS','PREINVERSION')
  AND deleted_at IS NULL;

-- UNIDAD (4 orgs)
UPDATE core.organization SET org_type_id = (
  SELECT id FROM ref.category WHERE scheme='org_type' AND code='UNIDAD'
) WHERE code IN ('UCR','OFICINA-PARTES','INFORMATICA','SERVICIOS-GENERALES')
  AND deleted_at IS NULL;

-- Las 6 divisiones reales quedan como DIVISION: DAF, DIPIR, DIPLADE, DIDESO, DIFOI, DIT
-- (+ DIDECO/DGI que ya tiene su clasificación como StaffUnit)


-- ────────────────────────────────────────────────────────────────────────────
-- Op 3: Refijar endofuntor parent_id — Profundidad 1 → 3
-- ────────────────────────────────────────────────────────────────────────────
-- Crea la cadena jerárquica GORE → DIVISION → DEPARTAMENTO → UNIDAD

-- Nivel 2: Departamentos bajo sus Divisiones
UPDATE core.organization SET parent_id = (SELECT id FROM core.organization WHERE code='DAF')
WHERE code IN ('FINANZAS','PERSONAS','OFICINA-PARTES') AND deleted_at IS NULL;

UPDATE core.organization SET parent_id = (SELECT id FROM core.organization WHERE code='DIPIR')
WHERE code IN ('INVERSIONES','PRESUPUESTO') AND deleted_at IS NULL;

UPDATE core.organization SET parent_id = (SELECT id FROM core.organization WHERE code='DIPLADE')
WHERE code = 'PREINVERSION' AND deleted_at IS NULL;

-- Nivel 3: Unidades bajo Departamentos
UPDATE core.organization SET parent_id = (SELECT id FROM core.organization WHERE code='FINANZAS')
WHERE code IN ('UCR') AND deleted_at IS NULL;


-- ────────────────────────────────────────────────────────────────────────────
-- Op 4: INSERTs — ~8 nuevos objetos en Org (Organigrama 2026)
-- ────────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
  v_staff UUID; v_advisory UUID; v_depto UUID; v_unidad UUID;
  v_gore UUID; v_finanzas UUID;
BEGIN
  SELECT id INTO v_staff FROM ref.category WHERE scheme='org_type' AND code='STAFF_UNIT';
  SELECT id INTO v_advisory FROM ref.category WHERE scheme='org_type' AND code='ADVISORY_BODY';
  SELECT id INTO v_depto FROM ref.category WHERE scheme='org_type' AND code='DEPARTAMENTO';
  SELECT id INTO v_unidad FROM ref.category WHERE scheme='org_type' AND code='UNIDAD';
  SELECT id INTO v_gore FROM core.organization WHERE code='GORE-NUBLE';
  SELECT id INTO v_finanzas FROM core.organization WHERE code='FINANZAS';

  INSERT INTO core.organization (code, name, org_type_id, parent_id)
  VALUES
    ('URAI', 'Unidad de Relaciones y Asuntos Internacionales', v_staff, v_gore),
    ('COSOC', 'Consejo de la Sociedad Civil', v_advisory, v_gore),
    ('CTCI', 'Comité de Ciencia, Tecnología e Innovación', v_advisory, v_gore),
    ('DGI', 'Departamento de Gestión Institucional', v_depto, v_gore),
    ('TESORERIA', 'Unidad de Tesorería', v_unidad, v_finanzas),
    ('CONTABILIDAD', 'Unidad de Contabilidad y Finanzas', v_unidad, v_finanzas),
    ('ADQUISICIONES', 'Unidad de Adquisiciones', v_unidad, v_finanzas),
    ('OPERACIONES', 'Unidad de Operaciones', v_unidad, v_finanzas)
  ON CONFLICT (code) DO NOTHING;
END $$;


-- ────────────────────────────────────────────────────────────────────────────
-- Op 5: Expandir coalgebra δ_{agreement_state} — 3 nuevos estados
-- ────────────────────────────────────────────────────────────────────────────
-- Inserta estados intermedios obligatorios del flujo normativo:
--   EN_REV_JUR → EN_REV_FIN → VISADO → FIRMADO_GORE
--   FIRMADO_CONTRAPARTE → TDR_PENDIENTE → VIGENTE

INSERT INTO ref.category (scheme, code, label, description, sort_order, valid_transitions)
VALUES
  ('agreement_state', 'EN_REVISION_FINANCIERA', 'En Revisión Financiera',
   'DAF valida cláusulas financieras y disponibilidad presupuestaria', 4,
   '["VISADO_INTERNO","EN_REVISION_JURIDICA"]'::jsonb),
  ('agreement_state', 'VISADO_INTERNO', 'Visado Interno',
   'AR visa el acto (obligatorio >1.000 UTM)', 5,
   '["FIRMADO_GORE","EN_REVISION_FINANCIERA"]'::jsonb),
  ('agreement_state', 'TDR_PENDIENTE', 'TdR Pendiente',
   'Toma de Razón CGR pendiente (obligatorio >2.500 UTM)', 9,
   '["VIGENTE"]'::jsonb)
ON CONFLICT (scheme, code) DO NOTHING;

-- Reconfigurar δ para estados existentes cuyas transiciones cambian
UPDATE ref.category SET valid_transitions = '["EN_REVISION_FINANCIERA","EN_NEGOCIACION"]'::jsonb
WHERE scheme='agreement_state' AND code='EN_REVISION_JURIDICA';

UPDATE ref.category SET valid_transitions = '["VIGENTE","TDR_PENDIENTE"]'::jsonb
WHERE scheme='agreement_state' AND code='FIRMADO_CONTRAPARTE';

-- Re-numerar sort_order para orden correcto (1-13)
UPDATE ref.category SET sort_order = CASE code
  WHEN 'BORRADOR' THEN 1
  WHEN 'EN_NEGOCIACION' THEN 2
  WHEN 'EN_REVISION_JURIDICA' THEN 3
  WHEN 'EN_REVISION_FINANCIERA' THEN 4
  WHEN 'VISADO_INTERNO' THEN 5
  WHEN 'FIRMADO_GORE' THEN 6
  WHEN 'FIRMADO_CONTRAPARTE' THEN 7
  WHEN 'VIGENTE' THEN 8
  WHEN 'TDR_PENDIENTE' THEN 9
  WHEN 'EN_MODIFICACION' THEN 10
  WHEN 'VENCIDO' THEN 11
  WHEN 'TERMINADO' THEN 12
  WHEN 'RESCILIADO' THEN 13
END WHERE scheme='agreement_state';


-- ────────────────────────────────────────────────────────────────────────────
-- Op 6: Expandir Cat_{system_role} — 5 nuevos objetos
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES
  ('system_role', 'GOBERNADOR', 'Gobernador Regional',
   'Máxima autoridad ejecutiva. Firma actos, preside CORE, propone presupuesto.', 0),
  ('system_role', 'CONSEJERO_REGIONAL', 'Consejero Regional',
   'Miembro CORE (16). Funciones normativas, resolutivas, fiscalizadoras.', 9),
  ('system_role', 'SECRETARIO_EJECUTIVO', 'Secretario Ejecutivo CORE',
   'Ministro de fe CORE. Acuerdos, actas, certificados.', 10),
  ('system_role', 'JEFE_DEPARTAMENTO', 'Jefe de Departamento',
   'Nivel intermedio cadena de mando. Supervisa departamento.', 11),
  ('system_role', 'JEFE_UNIDAD', 'Jefe de Unidad',
   'Nivel operativo cadena de mando. Ejecuta en unidad.', 12)
ON CONFLICT (scheme, code) DO NOTHING;


-- ────────────────────────────────────────────────────────────────────────────
-- Op 7: Soft-delete duplicados legacy — Limpieza de fibra
-- ────────────────────────────────────────────────────────────────────────────
-- Duplicados ORG_GORE-* (sin parent_id, sin FKs activas) + ORG-85ea3272 (GORE duplicado)

DO $$
DECLARE
  v_dup RECORD;
  v_canonical_code TEXT;
BEGIN
  FOR v_dup IN
    SELECT id, code
    FROM core.organization
    WHERE code LIKE 'ORG_GORE-%' AND deleted_at IS NULL
  LOOP
    -- Derivar código canónico: ORG_GORE-DIDESO→DIDERSO, ORG_GORE-DIFOI→DIFOT, resto directo
    v_canonical_code := REPLACE(v_dup.code, 'ORG_GORE-', '');
    v_canonical_code := CASE v_canonical_code
      WHEN 'DIDESO' THEN 'DIDERSO'
      WHEN 'DIFOI' THEN 'DIFOT'
      ELSE v_canonical_code
    END;

    -- Reasignar user.division_id si apunta al duplicado (safety net)
    UPDATE core."user" SET division_id = (
      SELECT id FROM core.organization WHERE code = v_canonical_code AND deleted_at IS NULL LIMIT 1
    ) WHERE division_id = v_dup.id;

    -- Reasignar ipr.sponsor_division_id si apunta al duplicado
    UPDATE core.ipr SET sponsor_division_id = (
      SELECT id FROM core.organization WHERE code = v_canonical_code AND deleted_at IS NULL LIMIT 1
    ) WHERE sponsor_division_id = v_dup.id;

    -- Soft-delete
    UPDATE core.organization SET deleted_at = NOW() WHERE id = v_dup.id;
  END LOOP;
END $$;

-- Soft-delete GORE duplicado (ORG-85ea3272)
UPDATE core.organization SET deleted_at = NOW()
WHERE code = 'ORG-85ea3272' AND deleted_at IS NULL;


-- ────────────────────────────────────────────────────────────────────────────
-- Verificación inline (RAISE NOTICE)
-- ────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
  v_org_types INT; v_roles INT; v_states INT; v_depth INT; v_active_orgs INT;
BEGIN
  SELECT COUNT(DISTINCT c.code) INTO v_org_types
  FROM core.organization o JOIN ref.category c ON o.org_type_id = c.id
  WHERE o.deleted_at IS NULL;

  SELECT COUNT(*) INTO v_roles FROM ref.category WHERE scheme='system_role' AND deleted_at IS NULL;
  SELECT COUNT(*) INTO v_states FROM ref.category WHERE scheme='agreement_state' AND deleted_at IS NULL;
  SELECT COUNT(*) INTO v_active_orgs FROM core.organization WHERE deleted_at IS NULL;

  WITH RECURSIVE tree AS (
    SELECT id, 0 as depth FROM core.organization WHERE parent_id IS NULL AND deleted_at IS NULL
    UNION ALL
    SELECT o.id, t.depth+1 FROM core.organization o JOIN tree t ON o.parent_id = t.id WHERE o.deleted_at IS NULL
  ) SELECT MAX(depth) INTO v_depth FROM tree;

  RAISE NOTICE '── Verificación Σ_f ──────────────────────────';
  RAISE NOTICE 'Tipos org distintos en uso: % (esperado: ≥6)', v_org_types;
  RAISE NOTICE 'Roles del sistema:          % (esperado: 13)', v_roles;
  RAISE NOTICE 'Estados de convenio:        % (esperado: 13)', v_states;
  RAISE NOTICE 'Profundidad org:            % (esperado: 3)', v_depth;
  RAISE NOTICE 'Orgs activas:               % (esperado: ~33)', v_active_orgs;
  RAISE NOTICE '──────────────────────────────────────────────';
END $$;

COMMIT;
