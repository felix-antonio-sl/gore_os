-- Test users for GORE_OS integration tests
-- Depends on: goreos_seed.sql, goreos_seed_territory.sql

-- Persons
INSERT INTO core.person (id, names, paternal_surname, email, is_active) VALUES
('90bc3d7d-48aa-4949-8a1d-9893e4bf6c6e','Sistema','GOREOS',NULL,true),
('a0000001-0000-0000-0000-000000000001','María','González','admin@goreos.cl',true),
('a0000001-0000-0000-0000-000000000002','Carlos','Muñoz','regional@goreos.cl',true),
('a0000001-0000-0000-0000-000000000003','José','Pérez','jefe.daf@goreos.cl',true),
('a0000001-0000-0000-0000-000000000004','Ana','Silva','encargado.daf@goreos.cl',true),
('a0000001-0000-0000-0000-000000000005','Carmen','Rojas','jefe.dgi@goreos.cl',true),
('a0000001-0000-0000-0000-000000000006','Pedro','López','control.gestion@goreos.cl',true),
('a0000001-0000-0000-0000-000000000007','Paola','Leiva','procesos@goreos.cl',true),
('a0000001-0000-0000-0000-000000000008','Roberto','Torres','td@goreos.cl',true);

-- Users (password: admin123 for all)
-- Uses subqueries to resolve division/role IDs from seeded data
DO $$
DECLARE
    v_admin_sistema UUID;
    v_admin_regional UUID;
    v_jefe_division UUID;
    v_encargado UUID;
    v_jefe_dgi UUID;
    v_esp_control UUID;
    v_esp_procesos UUID;
    v_esp_td UUID;
    v_daf UUID;
    v_dgi UUID;
    v_hash TEXT := '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe';
    v_sys_hash TEXT := '$2b$12$KIXxKv.lQ8PvH8y1N3N3auqVZ8y9Z4K5Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3';
BEGIN
    -- Roles
    SELECT id INTO v_admin_sistema FROM ref.category WHERE scheme='system_role' AND code='ADMIN_SISTEMA';
    SELECT id INTO v_admin_regional FROM ref.category WHERE scheme='system_role' AND code='ADMIN_REGIONAL';
    SELECT id INTO v_jefe_division FROM ref.category WHERE scheme='system_role' AND code='JEFE_DIVISION';
    SELECT id INTO v_encargado FROM ref.category WHERE scheme='system_role' AND code='ENCARGADO';
    SELECT id INTO v_jefe_dgi FROM ref.category WHERE scheme='system_role' AND code='JEFE_DGI';
    SELECT id INTO v_esp_control FROM ref.category WHERE scheme='system_role' AND code='ESP_CONTROL_GESTION';
    SELECT id INTO v_esp_procesos FROM ref.category WHERE scheme='system_role' AND code='ESP_PROCESOS';
    SELECT id INTO v_esp_td FROM ref.category WHERE scheme='system_role' AND code='ESP_TD';

    -- Divisions
    SELECT id INTO v_daf FROM core.organization WHERE code='DAF';
    SELECT id INTO v_dgi FROM core.organization WHERE code='DIDECO';

    -- System user
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('5a979abe-12e3-4700-9216-c6945a8f6ce6','system@goreos.cl',v_sys_hash,'90bc3d7d-48aa-4949-8a1d-9893e4bf6c6e',v_admin_sistema,true);

    -- Admin
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000001','admin@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000001',v_admin_sistema,true);

    -- Regional
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000002','regional@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000002',v_admin_regional,true);

    -- Jefe DAF
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000003','jefe.daf@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000003',v_jefe_division,v_daf,true);

    -- Encargado DAF
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000004','encargado.daf@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000004',v_encargado,v_daf,true);

    -- Jefe DGI
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000005','jefe.dgi@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000005',v_jefe_dgi,v_dgi,true);

    -- ESP Control Gestion
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000006','control.gestion@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000006',v_esp_control,v_dgi,true);

    -- ESP Procesos
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000007','procesos@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000007',v_esp_procesos,v_dgi,true);

    -- ESP TD
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000008','td@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000008',v_esp_td,v_dgi,true);

    RAISE NOTICE 'Test users seeded: 9 users';
END $$;
