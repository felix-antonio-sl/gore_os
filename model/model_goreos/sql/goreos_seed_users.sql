-- =============================================================================
-- GORE_OS Test Users — SSOT-aligned, consolidated
-- Depends on: goreos_seed.sql (system_role codes), goreos_seed_territory.sql (org codes)
-- 25 users: 1 system + 24 regular. Password: admin123 for all.
-- Roles: 15 system_roles (ENCARGADO collapsed — is assignment, not role)
-- Orgs: 6 divisions (SSOT canonical) + DGI (StaffUnit)
-- =============================================================================

-- Persons (25)
INSERT INTO core.person (id, names, paternal_surname, email, is_active) VALUES
('90bc3d7d-48aa-4949-8a1d-9893e4bf6c6e', 'Sistema',   'GOREOS',     NULL, true),
('a0000001-0000-0000-0000-000000000001', 'María',      'González',   'admin@goreos.cl', true),
('a0000001-0000-0000-0000-000000000002', 'Carlos',     'Muñoz',      'regional@goreos.cl', true),
('a0000001-0000-0000-0000-000000000003', 'Patricio',   'Reyes',      'gobernador@goreos.cl', true),
('a0000001-0000-0000-0000-000000000004', 'Isabel',     'Fuentes',    'secretario.core@goreos.cl', true),
('a0000001-0000-0000-0000-000000000005', 'José',       'Pérez',      'jefe.daf@goreos.cl', true),
('a0000001-0000-0000-0000-000000000006', 'Laura',      'Campos',     'jefe.dideso@goreos.cl', true),
('a0000001-0000-0000-0000-000000000007', 'Andrés',     'Vega',       'jefe.difoi@goreos.cl', true),
('a0000001-0000-0000-0000-000000000008', 'Marcela',    'Soto',       'jefe.dipir@goreos.cl', true),
('a0000001-0000-0000-0000-000000000009', 'Tomás',      'Araya',      'jefe.diplade@goreos.cl', true),
('a0000001-0000-0000-0000-000000000010', 'Carolina',   'Rivas',      'jefe.dit@goreos.cl', true),
('a0000001-0000-0000-0000-000000000011', 'Ricardo',    'Mora',       'jefe.finanzas@goreos.cl', true),
('a0000001-0000-0000-0000-000000000012', 'Soledad',    'Parra',      'jefe.ucr@goreos.cl', true),
('a0000001-0000-0000-0000-000000000013', 'Felipe',     'Morales',    'analista.dipir@goreos.cl', true),
('a0000001-0000-0000-0000-000000000014', 'Claudia',    'Sepúlveda',  'analista.diplade@goreos.cl', true),
('a0000001-0000-0000-0000-000000000015', 'Diego',      'Fuentes',    'rtf.daf@goreos.cl', true),
('a0000001-0000-0000-0000-000000000016', 'Valentina',  'Bravo',      'juridico@goreos.cl', true),
('a0000001-0000-0000-0000-000000000017', 'Luis',       'Henríquez',  'consejero1@goreos.cl', true),
('a0000001-0000-0000-0000-000000000018', 'Rosa',       'Olivares',   'consejero2@goreos.cl', true),
('a0000001-0000-0000-0000-000000000019', 'Carmen',     'Rojas',      'jefe.dgi@goreos.cl', true),
('a0000001-0000-0000-0000-000000000020', 'Pedro',      'López',      'control.gestion@goreos.cl', true),
('a0000001-0000-0000-0000-000000000021', 'Paola',      'Leiva',      'procesos@goreos.cl', true),
('a0000001-0000-0000-0000-000000000022', 'Roberto',    'Torres',     'td@goreos.cl', true),
('a0000001-0000-0000-0000-000000000023', 'Camila',     'Soto',       'profesional.dit@goreos.cl', true),
('a0000001-0000-0000-0000-000000000024', 'Andrés',     'Vega',       'profesional.dideso@goreos.cl', true)
ON CONFLICT (id) DO NOTHING;

-- Users (25) — password: admin123 for all
DO $$
DECLARE
    -- Roles (15 system_roles)
    v_admin_sistema UUID;
    v_admin_regional UUID;
    v_gobernador UUID;
    v_secretario UUID;
    v_jefe_division UUID;
    v_jefe_departamento UUID;
    v_jefe_unidad UUID;
    v_jefe_dgi UUID;
    v_esp_control UUID;
    v_esp_procesos UUID;
    v_esp_td UUID;
    v_consejero UUID;
    v_analista UUID;
    v_rtf UUID;
    v_juridico UUID;
    -- Divisions (6 SSOT canonical + DGI)
    v_daf UUID;
    v_dideso UUID;
    v_difoi UUID;
    v_dipir UUID;
    v_diplade UUID;
    v_dit UUID;
    v_dgi UUID;
    -- Password hash (admin123)
    v_hash TEXT := '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe';
    v_sys_hash TEXT := '$2b$12$KIXxKv.lQ8PvH8y1N3N3auqVZ8y9Z4K5Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3';
BEGIN
    -- Resolve roles
    SELECT id INTO v_admin_sistema FROM ref.category WHERE scheme='system_role' AND code='ADMIN_SISTEMA';
    SELECT id INTO v_admin_regional FROM ref.category WHERE scheme='system_role' AND code='ADMIN_REGIONAL';
    SELECT id INTO v_gobernador FROM ref.category WHERE scheme='system_role' AND code='GOBERNADOR';
    SELECT id INTO v_secretario FROM ref.category WHERE scheme='system_role' AND code='SECRETARIO_EJECUTIVO';
    SELECT id INTO v_jefe_division FROM ref.category WHERE scheme='system_role' AND code='JEFE_DIVISION';
    SELECT id INTO v_jefe_departamento FROM ref.category WHERE scheme='system_role' AND code='JEFE_DEPARTAMENTO';
    SELECT id INTO v_jefe_unidad FROM ref.category WHERE scheme='system_role' AND code='JEFE_UNIDAD';
    SELECT id INTO v_jefe_dgi FROM ref.category WHERE scheme='system_role' AND code='JEFE_DGI';
    SELECT id INTO v_esp_control FROM ref.category WHERE scheme='system_role' AND code='ESP_CONTROL_GESTION';
    SELECT id INTO v_esp_procesos FROM ref.category WHERE scheme='system_role' AND code='ESP_PROCESOS';
    SELECT id INTO v_esp_td FROM ref.category WHERE scheme='system_role' AND code='ESP_TD';
    SELECT id INTO v_consejero FROM ref.category WHERE scheme='system_role' AND code='CONSEJERO_REGIONAL';
    SELECT id INTO v_analista FROM ref.category WHERE scheme='system_role' AND code='ANALISTA';
    SELECT id INTO v_rtf FROM ref.category WHERE scheme='system_role' AND code='RTF';
    SELECT id INTO v_juridico FROM ref.category WHERE scheme='system_role' AND code='ASESOR_JURIDICO';

    -- Resolve divisions (SSOT canonical codes)
    SELECT id INTO v_daf FROM core.organization WHERE code='DAF';
    SELECT id INTO v_dideso FROM core.organization WHERE code='DIDESO';
    SELECT id INTO v_difoi FROM core.organization WHERE code='DIFOI';
    SELECT id INTO v_dipir FROM core.organization WHERE code='DIPIR';
    SELECT id INTO v_diplade FROM core.organization WHERE code='DIPLADE';
    SELECT id INTO v_dit FROM core.organization WHERE code='DIT';
    SELECT id INTO v_dgi FROM core.organization WHERE code='DGI';

    -- #0 System
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('5a979abe-12e3-4700-9216-c6945a8f6ce6', 'system@goreos.cl', v_sys_hash,
            '90bc3d7d-48aa-4949-8a1d-9893e4bf6c6e', v_admin_sistema, true)
    ON CONFLICT (email) DO NOTHING;

    -- #1 Admin Sistema
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000001', 'admin@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000001', v_admin_sistema, true)
    ON CONFLICT (email) DO NOTHING;

    -- #2 Admin Regional
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000002', 'regional@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000002', v_admin_regional, true)
    ON CONFLICT (email) DO NOTHING;

    -- #3 Gobernador
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000003', 'gobernador@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000003', v_gobernador, true)
    ON CONFLICT (email) DO NOTHING;

    -- #4 Secretario Ejecutivo CORE
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000004', 'secretario.core@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000004', v_secretario, true)
    ON CONFLICT (email) DO NOTHING;

    -- #5 Jefe DAF
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000005', 'jefe.daf@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000005', v_jefe_division, v_daf, true)
    ON CONFLICT (email) DO NOTHING;

    -- #6 Jefe DIDESO
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000006', 'jefe.dideso@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000006', v_jefe_division, v_dideso, true)
    ON CONFLICT (email) DO NOTHING;

    -- #7 Jefe DIFOI
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000007', 'jefe.difoi@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000007', v_jefe_division, v_difoi, true)
    ON CONFLICT (email) DO NOTHING;

    -- #8 Jefe DIPIR
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000008', 'jefe.dipir@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000008', v_jefe_division, v_dipir, true)
    ON CONFLICT (email) DO NOTHING;

    -- #9 Jefe DIPLADE
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000009', 'jefe.diplade@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000009', v_jefe_division, v_diplade, true)
    ON CONFLICT (email) DO NOTHING;

    -- #10 Jefe DIT
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000010', 'jefe.dit@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000010', v_jefe_division, v_dit, true)
    ON CONFLICT (email) DO NOTHING;

    -- #11 Jefe Depto. Finanzas (DAF)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000011', 'jefe.finanzas@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000011', v_jefe_departamento, v_daf, true)
    ON CONFLICT (email) DO NOTHING;

    -- #12 Jefe UCR (DAF)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000012', 'jefe.ucr@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000012', v_jefe_unidad, v_daf, true)
    ON CONFLICT (email) DO NOTHING;

    -- #13 Analista DIPIR (Depto. Análisis y Evaluación — formula IPR F0-F2)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000013', 'analista.dipir@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000013', v_analista, v_dipir, true)
    ON CONFLICT (email) DO NOTHING;

    -- #14 Analista DIPLADE (Depto. Planificación — formula IPR F0-F2)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000014', 'analista.diplade@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000014', v_analista, v_diplade, true)
    ON CONFLICT (email) DO NOTHING;

    -- #15 RTF DAF (Analista Otorgante SISREC — revisa rendiciones)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000015', 'rtf.daf@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000015', v_rtf, v_daf, true)
    ON CONFLICT (email) DO NOTHING;

    -- #16 Asesor Jurídico (Depto. Jurídico — V.B. actos y convenios)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000016', 'juridico@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000016', v_juridico, true)
    ON CONFLICT (email) DO NOTHING;

    -- #17 Consejero Regional 1 (CORE — vota IPRs >7K UTM)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000017', 'consejero1@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000017', v_consejero, true)
    ON CONFLICT (email) DO NOTHING;

    -- #18 Consejero Regional 2 (CORE — quórum 9/16 simple, 11/16 calificada)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000018', 'consejero2@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000018', v_consejero, true)
    ON CONFLICT (email) DO NOTHING;

    -- #19 Jefe DGI (Director DGI — coordinación institucional)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000019', 'jefe.dgi@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000019', v_jefe_dgi, v_dgi, true)
    ON CONFLICT (email) DO NOTHING;

    -- #20 ESP Control Gestión (DGI — indicadores, cartera IPR)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000020', 'control.gestion@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000020', v_esp_control, v_dgi, true)
    ON CONFLICT (email) DO NOTHING;

    -- #21 ESP Procesos (DGI — BPMN, DMAIC, catálogo)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000021', 'procesos@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000021', v_esp_procesos, v_dgi, true)
    ON CONFLICT (email) DO NOTHING;

    -- #22 ESP Transformación Digital (DGI — Ley 21.180, métricas Lean)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000022', 'td@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000022', v_esp_td, v_dgi, true)
    ON CONFLICT (email) DO NOTHING;

    -- #23 Profesional DIT (Depto. Ejecución y Supervisión — supervisa obras F4)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000023', 'profesional.dit@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000023', v_analista, v_dit, true)
    ON CONFLICT (email) DO NOTHING;

    -- #24 Profesional DIDESO (Depto. Fondos Concursables — programas sociales)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000024', 'profesional.dideso@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000024', v_analista, v_dideso, true)
    ON CONFLICT (email) DO NOTHING;

    RAISE NOTICE 'Test users seeded: 25 users (1 system + 24 regular), 15 roles, SSOT-aligned';
END $$;
