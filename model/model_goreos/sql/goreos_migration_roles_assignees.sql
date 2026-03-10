-- =============================================================================
-- GORE_OS — MIGRACIÓN: ROLES Y ASSIGNEES
-- =============================================================================
-- Archivo: goreos_migration_roles_assignees.sql
-- Fecha: 2026-03-09
-- =============================================================================
-- Crea usuarios para los 5 roles sin usuarios + 6 jefes de división vacías.
-- Puebla sponsor_division_id (por track) y assignee_id (por jefe de división).
-- Todos los usuarios usan password: admin123
-- =============================================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. PERSONAS para nuevos usuarios
-- ═══════════════════════════════════════════════════════════════════════════

-- Roles institucionales
INSERT INTO core.person (id, rut, names, paternal_surname, maternal_surname)
VALUES
  (gen_random_uuid(), '11.111.111-1', 'Rodrigo', 'Mundaca', 'Cabrera'),
  (gen_random_uuid(), '11.111.112-K', 'María Elena', 'Pérez', 'Soto'),
  (gen_random_uuid(), '11.111.113-8', 'Carlos', 'González', 'Muñoz'),
  (gen_random_uuid(), '11.111.114-6', 'Ana', 'Martínez', 'Flores'),
  (gen_random_uuid(), '11.111.115-4', 'Pedro', 'López', 'Ramírez'),
  (gen_random_uuid(), '11.111.116-2', 'Claudia', 'Hernández', 'Díaz')
ON CONFLICT (rut) DO NOTHING;

-- Jefes de divisiones vacías
INSERT INTO core.person (id, rut, names, paternal_surname, maternal_surname)
VALUES
  (gen_random_uuid(), '22.222.221-1', 'Sofía', 'Araya', 'Valenzuela'),
  (gen_random_uuid(), '22.222.222-K', 'Matías', 'Campos', 'Rojas'),
  (gen_random_uuid(), '22.222.223-8', 'Valentina', 'Fuentes', 'Morales'),
  (gen_random_uuid(), '22.222.224-6', 'Sebastián', 'Riquelme', 'Vera'),
  (gen_random_uuid(), '22.222.225-4', 'Catalina', 'Saavedra', 'Contreras'),
  (gen_random_uuid(), '22.222.226-2', 'Diego', 'Núñez', 'Espinoza')
ON CONFLICT (rut) DO NOTHING;


-- ═══════════════════════════════════════════════════════════════════════════
-- 2. USUARIOS para roles faltantes
-- ═══════════════════════════════════════════════════════════════════════════

-- GOBERNADOR (1 usuario, sin división — sobre la jerarquía)
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(),
       p.id,
       'gobernador@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'GOBERNADOR'),
       NULL,
       true
FROM core.person p WHERE p.rut = '11.111.111-1'
ON CONFLICT (email) DO NOTHING;

-- SECRETARIO_EJECUTIVO (1 usuario, sin división — sirve al CORE)
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(),
       p.id,
       'secretario.core@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'SECRETARIO_EJECUTIVO'),
       NULL,
       true
FROM core.person p WHERE p.rut = '11.111.112-K'
ON CONFLICT (email) DO NOTHING;

-- CONSEJERO_REGIONAL (2 usuarios, sin división — miembros del consejo)
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(),
       p.id,
       'consejero1@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'CONSEJERO_REGIONAL'),
       NULL,
       true
FROM core.person p WHERE p.rut = '11.111.113-8'
ON CONFLICT (email) DO NOTHING;

INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(),
       p.id,
       'consejero2@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'CONSEJERO_REGIONAL'),
       NULL,
       true
FROM core.person p WHERE p.rut = '11.111.114-6'
ON CONFLICT (email) DO NOTHING;

-- JEFE_DEPARTAMENTO (1 usuario, en DAF → Depto Finanzas)
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(),
       p.id,
       'jefe.finanzas@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'JEFE_DEPARTAMENTO'),
       (SELECT id FROM core.organization WHERE code = 'DAF'),
       true
FROM core.person p WHERE p.rut = '11.111.115-4'
ON CONFLICT (email) DO NOTHING;

-- JEFE_UNIDAD (1 usuario, en DAF → UCR)
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(),
       p.id,
       'jefe.ucr@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'JEFE_UNIDAD'),
       (SELECT id FROM core.organization WHERE code = 'DAF'),
       true
FROM core.person p WHERE p.rut = '11.111.116-2'
ON CONFLICT (email) DO NOTHING;


-- ═══════════════════════════════════════════════════════════════════════════
-- 3. JEFES DE DIVISIÓN para divisiones vacías
-- ═══════════════════════════════════════════════════════════════════════════

-- DIDESO
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(), p.id, 'jefe.dideso@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'JEFE_DIVISION'),
       (SELECT id FROM core.organization WHERE code = 'DIDESO'),
       true
FROM core.person p WHERE p.rut = '22.222.221-1'
ON CONFLICT (email) DO NOTHING;

-- DIFOI
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(), p.id, 'jefe.difoi@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'JEFE_DIVISION'),
       (SELECT id FROM core.organization WHERE code = 'DIFOI'),
       true
FROM core.person p WHERE p.rut = '22.222.222-K'
ON CONFLICT (email) DO NOTHING;

-- DIIAP
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(), p.id, 'jefe.diiap@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'JEFE_DIVISION'),
       (SELECT id FROM core.organization WHERE code = 'DIIAP'),
       true
FROM core.person p WHERE p.rut = '22.222.223-8'
ON CONFLICT (email) DO NOTHING;

-- DIPIR
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(), p.id, 'jefe.dipir@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'JEFE_DIVISION'),
       (SELECT id FROM core.organization WHERE code = 'DIPIR'),
       true
FROM core.person p WHERE p.rut = '22.222.224-6'
ON CONFLICT (email) DO NOTHING;

-- DIPLADE
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(), p.id, 'jefe.diplade@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'JEFE_DIVISION'),
       (SELECT id FROM core.organization WHERE code = 'DIPLADE'),
       true
FROM core.person p WHERE p.rut = '22.222.225-4'
ON CONFLICT (email) DO NOTHING;

-- DIT
INSERT INTO core."user" (id, person_id, email, password_hash, system_role_id, division_id, is_active)
SELECT gen_random_uuid(), p.id, 'jefe.dit@goreos.cl',
       '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
       (SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = 'JEFE_DIVISION'),
       (SELECT id FROM core.organization WHERE code = 'DIT'),
       true
FROM core.person p WHERE p.rut = '22.222.226-2'
ON CONFLICT (email) DO NOTHING;


-- ═══════════════════════════════════════════════════════════════════════════
-- 4. SPONSOR_DIVISION_ID por financing track (mechanism)
-- ═══════════════════════════════════════════════════════════════════════════
-- SNI → DIPIR (inversión pública)
-- SUBV8 → DIDESO (desarrollo social)
-- TRANSFER → DAF (administración y finanzas)
-- FRPD → DIFOI (fomento productivo)
-- Sin mecanismo → DIPLADE (planificación)

UPDATE core.ipr i
SET sponsor_division_id = CASE
    WHEN m.code = 'SNI'      THEN (SELECT id FROM core.organization WHERE code = 'DIPIR')
    WHEN m.code = 'SUBV8'    THEN (SELECT id FROM core.organization WHERE code = 'DIDESO')
    WHEN m.code = 'TRANSFER' THEN (SELECT id FROM core.organization WHERE code = 'DAF')
    WHEN m.code = 'FRPD'     THEN (SELECT id FROM core.organization WHERE code = 'DIFOI')
    ELSE (SELECT id FROM core.organization WHERE code = 'DIPLADE')
END
FROM ref.category m
WHERE m.id = i.mechanism_id
  AND i.deleted_at IS NULL
  AND i.sponsor_division_id IS NULL;

-- IPRs sin mecanismo → DIPLADE
UPDATE core.ipr
SET sponsor_division_id = (SELECT id FROM core.organization WHERE code = 'DIPLADE')
WHERE mechanism_id IS NULL
  AND deleted_at IS NULL
  AND sponsor_division_id IS NULL;


-- ═══════════════════════════════════════════════════════════════════════════
-- 5. ASSIGNEE_ID por jefe de división sponsor
-- ═══════════════════════════════════════════════════════════════════════════
-- Cada IPR se asigna al JEFE_DIVISION de su sponsor_division.

UPDATE core.ipr i
SET assignee_id = u.id
FROM core."user" u
JOIN ref.category sr ON sr.id = u.system_role_id AND sr.code = 'JEFE_DIVISION'
WHERE u.division_id = i.sponsor_division_id
  AND u.is_active = true
  AND u.deleted_at IS NULL
  AND i.deleted_at IS NULL
  AND i.assignee_id IS NULL;

COMMIT;

DO $$ BEGIN
    RAISE NOTICE 'GORE_OS Migración roles_assignees aplicada: 12 personas, 12 usuarios, sponsor_division + assignee poblados';
END $$;
