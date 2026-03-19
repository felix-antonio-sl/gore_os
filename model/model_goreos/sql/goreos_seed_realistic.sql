-- =============================================================================
-- GORE_OS — Seed Realista Completo (~830 registros)
-- =============================================================================
-- Simula un GORE de Ñuble operando en ciclo presupuestario 2026.
-- Coexiste con demo seeds existentes (ciclo2, wave_b, wave_e).
-- Rangos de códigos no superpuestos: DEMO-R* (realistic prefix).
--
-- Convenciones:
--   - Prefijo DEMO-R en todos los códigos generados
--   - FKs vía subquery: (SELECT id FROM ... WHERE ... LIMIT 1)
--   - Fechas relativas: CURRENT_DATE - INTERVAL 'N days'
--   - ON CONFLICT DO NOTHING para idempotencia
--   - FSM: INSERT directo con estado destino (triggers solo validan UPDATE)
--
-- Para cargar:
--   docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_seed_realistic.sql
--
-- Para revertir:
--   docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_unseed_realistic.sql
-- =============================================================================

BEGIN;

-- =============================================================================
-- TIER 1: PERSONAS Y ORGANIZACIONES EXTERNAS (~45 registros)
-- =============================================================================

-- 1.1 Personas externas (15) — contactos de municipalidades, servicios, empresas
INSERT INTO core.person (names, paternal_surname, maternal_surname, email, is_active)
VALUES
    ('Hernán',    'Arriagada',  'Muñoz',     'harriagada@munichillan.cl',   true),
    ('Patricia',  'Cifuentes',  'Lagos',     'pcifuentes@munisancarlos.cl', true),
    ('Miguel',    'Orellana',   'Díaz',      'morellana@muniquirihue.cl',   true),
    ('Francisca', 'Bustamante', 'Vergara',   'fbustamante@municoihueco.cl', true),
    ('Roberto',   'Sanhueza',   'Martínez',  'rsanhueza@munibulnes.cl',     true),
    ('Carmen',    'Valenzuela', 'Pizarro',   'cvalenzuela@serviu-nuble.cl', true),
    ('Eduardo',   'Figueroa',   'Cáceres',   'efigueroa@mop-nuble.cl',     true),
    ('Daniela',   'Contreras',  'Fuentes',   'dcontreras@sernatur-nuble.cl',true),
    ('Julio',     'Espinoza',   'Riquelme',  'jespinoza@ubb.cl',           true),
    ('Marisol',   'Navarrete',  'Gatica',    'mnavarrete@uadventista.cl',   true),
    ('Gonzalo',   'Riquelme',   'Astorga',   'griquelme@constructoraitata.cl', true),
    ('Lorena',    'Zúñiga',     'Sepúlveda', 'lzuniga@ingnuble.cl',        true),
    ('Alejandro', 'Medina',     'Farías',    'amedina@fundacionnuble.cl',   true),
    ('Susana',    'Paredes',    'Guajardo',  'sparedes@mdsf.gob.cl',       true),
    ('Ramón',     'Castillo',   'Villalobos','rcastillo@mop-eval.cl',      true)
ON CONFLICT DO NOTHING;

-- 1.2 Organizaciones externas (15) — DEMO-R* prefix en code
-- Municipalidades (7)
INSERT INTO core.organization (code, name, short_name, org_type_id) VALUES
    ('DEMO-R-MUNI-CHILLAN',     'Ilustre Municipalidad de Chillán',      'Muni Chillán',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='MUNICIPALIDAD')),
    ('DEMO-R-MUNI-SANCARLOS',   'Ilustre Municipalidad de San Carlos',   'Muni San Carlos',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='MUNICIPALIDAD')),
    ('DEMO-R-MUNI-QUIRIHUE',    'Ilustre Municipalidad de Quirihue',     'Muni Quirihue',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='MUNICIPALIDAD')),
    ('DEMO-R-MUNI-COIHUECO',    'Ilustre Municipalidad de Coihueco',     'Muni Coihueco',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='MUNICIPALIDAD')),
    ('DEMO-R-MUNI-BULNES',      'Ilustre Municipalidad de Bulnes',       'Muni Bulnes',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='MUNICIPALIDAD')),
    ('DEMO-R-MUNI-PINTO',       'Ilustre Municipalidad de Pinto',        'Muni Pinto',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='MUNICIPALIDAD')),
    ('DEMO-R-MUNI-COELEMU',     'Ilustre Municipalidad de Coelemu',      'Muni Coelemu',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='MUNICIPALIDAD'))
ON CONFLICT (code) DO NOTHING;

-- Servicios públicos (3)
INSERT INTO core.organization (code, name, short_name, org_type_id) VALUES
    ('DEMO-R-SERVIU-NUBLE',     'SERVIU Ñuble',                          'SERVIU',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='SERVICIO')),
    ('DEMO-R-MOP-NUBLE',        'Dirección de Obras Hidráulicas MOP',    'MOP DOH',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='SERVICIO')),
    ('DEMO-R-SERNATUR-NUBLE',   'SERNATUR Ñuble',                        'SERNATUR',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='SERVICIO'))
ON CONFLICT (code) DO NOTHING;

-- Universidades (2)
INSERT INTO core.organization (code, name, short_name, org_type_id) VALUES
    ('DEMO-R-UBB',              'Universidad del Bío-Bío',               'UBB',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='UNIVERSIDAD')),
    ('DEMO-R-UADVENTISTA',      'Universidad Adventista de Chile',       'UNACH',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='UNIVERSIDAD'))
ON CONFLICT (code) DO NOTHING;

-- Empresas (2)
INSERT INTO core.organization (code, name, short_name, org_type_id) VALUES
    ('DEMO-R-CONST-ITATA',      'Constructora Itata SpA',                'Const. Itata',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='EMPRESA')),
    ('DEMO-R-ING-NUBLE',        'Ingeniería Ñuble Ltda.',                'Ing. Ñuble',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='EMPRESA'))
ON CONFLICT (code) DO NOTHING;

-- ONG (1)
INSERT INTO core.organization (code, name, short_name, org_type_id) VALUES
    ('DEMO-R-FUND-NUBLE',       'Fundación para el Desarrollo de Ñuble', 'Fund. Ñuble',
     (SELECT id FROM ref.category WHERE scheme='org_type' AND code='ONG'))
ON CONFLICT (code) DO NOTHING;


-- =============================================================================
-- TIER 2: IPRs (~35 registros)
-- =============================================================================
-- Distribuye los 7 mecanismos × fases F0-F5 + 32 estados.
-- ipr_nature es un ENUM (PROYECTO|PROGRAMA|PROGRAMA_INVERSION|ESTUDIO_BASICO|ANF)
-- mcd_phase_id se incluye pero el API lo deriva de status — aquí lo insertamos consistente.
-- phase_entered_at simula tiempos reales de permanencia en fase.

-- === SNI (8 IPRs) ===
-- SNI-F0: INGRESADO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SNI-001', 'Construcción Centro de Salud Familiar Chillán Viejo', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='INGRESADO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F0'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPIR'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='HEALTH'),
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '5 days',
 '{"monto_total": 4500000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SNI-F1a: EN_REVISION
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SNI-002', 'Mejoramiento Estadio Municipal San Carlos', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_REVISION'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F1'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPIR'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='SPORTS'),
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '15 days',
 '{"monto_total": 1800000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SNI-F1b: PRE_ADMISIBLE
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SNI-003', 'Construcción Puente Peatonal Río Itata', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='PRE_ADMISIBLE'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F1'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='TRANSPORT'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '35 days',
 '{"monto_total": 2200000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SNI-F2a: EN_EVALUACION
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SNI-004', 'Habilitación Centro Cultural Quirihue', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_EVALUACION'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F2'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPIR'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='CULTURE'),
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '45 days',
 '{"monto_total": 950000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SNI-F2b: RS (Recomendación Satisfactoria)
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SNI-005', 'Reposición Liceo Bicentenario San Fabián', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='RS'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F2'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='SECTORIAL'),
 (SELECT id FROM core.organization WHERE code='DIPIR'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='EDUCATION'),
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '60 days',
 '{"monto_total": 3200000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SNI-F3: CDP_EMITIDO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SNI-006', 'Construcción Piscina Temperada Coihueco', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='CDP_EMITIDO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F3'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='SPORTS'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '10 days',
 '{"monto_total": 1600000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SNI-F4: EN_OBRA
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SNI-007', 'Pavimentación Acceso Norte Chillán', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_OBRA'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='TRANSPORT'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '120 days',
 '{"monto_total": 5800000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SNI-F5: CERRADO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SNI-008', 'Construcción Multicancha Techada Yungay', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='CERRADO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F5'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPIR'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='SPORTS'),
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '30 days',
 '{"monto_total": 890000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- === FRIL (6 IPRs) ===
-- FRIL-F0: INGRESADO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-FRIL-001', 'Reposición Sede Social Junta de Vecinos Pinto', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='INGRESADO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F0'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRIL'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPIR'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='CULTURE'),
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '3 days',
 '{"monto_total": 120000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- FRIL-F1: ADMISIBLE
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-FRIL-002', 'Mejoramiento Plaza de Armas Coelemu', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='ADMISIBLE'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F1'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRIL'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPIR'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='CULTURE'),
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '20 days',
 '{"monto_total": 85000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- FRIL-F2: FI (Falta de Información)
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-FRIL-003', 'Construcción Vereda Acceso Hospital Bulnes', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='FI'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F2'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRIL'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='HEALTH'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '50 days',
 '{"monto_total": 65000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- FRIL-F3: CDP_EMITIDO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-FRIL-004', 'Iluminación Cancha Sintética Ñiquén', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='EQUIPAMIENTO'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='CDP_EMITIDO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F3'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRIL'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPIR'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='SPORTS'),
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '8 days',
 '{"monto_total": 45000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- FRIL-F4: EN_EJECUCION
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-FRIL-005', 'Reposición Techado Feria Libre San Nicolás', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_EJECUCION'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRIL'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIFOI'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='ECONOMIC_DEV'),
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '90 days',
 '{"monto_total": 110000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- FRIL-F5: EN_RENDICION
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-FRIL-006', 'Mejoramiento Multicancha Pemuco', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_RENDICION'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F5'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRIL'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPIR'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='SPORTS'),
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '25 days',
 '{"monto_total": 78000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- === C33 (4 IPRs) ===
-- C33-F1: INADMISIBLE
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-C33-001', 'Conservación Puente Río Diguillín', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='CONSERVACION'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='INADMISIBLE'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F1'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='C33'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='TRANSPORT'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '40 days',
 '{"monto_total": 680000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- C33-F2: FC (Falta de Capacidad)
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-C33-002', 'Conservación Camino Rural Cobquecura-Quirihue', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='CONSERVACION'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='FC'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F2'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='C33'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='TRANSPORT'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '55 days',
 '{"monto_total": 420000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- C33-F4: RECEPCION_PROVISORIA
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-C33-003', 'Conservación Edificio Consistorial Ninhue', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='CONSERVACION'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='RECEPCION_PROVISORIA'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='C33'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='CULTURE'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '15 days',
 '{"monto_total": 350000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- C33-F5: RENDICION_APROBADA
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-C33-004', 'Conservación Red Vial Portezuelo-Ránquil', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='CONSERVACION'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='RENDICION_APROBADA'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F5'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='C33'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='TRANSPORT'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '20 days',
 '{"monto_total": 290000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- === SUBV8 (5 IPRs — naturaleza PROGRAMA) ===
-- SUBV8-F0: INGRESADO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SUBV8-001', 'Programa Apícola Comunas Rurales Ñuble', 'PROGRAMA',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='PROGRAMA_SOCIAL'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='INGRESADO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F0'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SUBV8'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIFOI'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='ECONOMIC_DEV'),
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '7 days',
 '{"monto_total": 250000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SUBV8-F2: OT (Observación Técnica)
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SUBV8-002', 'Programa Fortalecimiento PYMES Turísticas Itata', 'PROGRAMA',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='PROGRAMA_SOCIAL'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='OT'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F2'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SUBV8'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIFOI'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='TOURISM'),
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '65 days',
 '{"monto_total": 180000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SUBV8-F3: CDP_EMITIDO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SUBV8-003', 'Programa Capacitación Digital Adultos Mayores', 'PROGRAMA',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='PROGRAMA_SOCIAL'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='CDP_EMITIDO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F3'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SUBV8'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIDESO'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='EDUCATION'),
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '12 days',
 '{"monto_total": 95000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SUBV8-F4: FORMALIZADO (PROGRAMA no bifurca a licitación/obra)
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SUBV8-004', 'Programa Huertos Familiares Punilla', 'PROGRAMA',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='PROGRAMA_SOCIAL'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='FORMALIZADO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SUBV8'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIDESO'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='ENVIRONMENT'),
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '100 days',
 '{"monto_total": 75000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- SUBV8-F5: EN_CIERRE_ADMINISTRATIVO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-SUBV8-005', 'Programa Deportivo Escolar Diguillín', 'PROGRAMA',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='PROGRAMA_SOCIAL'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_CIERRE_ADMINISTRATIVO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F5'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SUBV8'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIDESO'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='SPORTS'),
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '18 days',
 '{"monto_total": 60000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- === TRANSFER (4 IPRs — PROGRAMA) ===
-- TRANSFER-F2: AD (Aprobado con Deficiencias)
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-TRF-001', 'Transferencia Fomento Productivo Vitivinícola Itata', 'PROGRAMA',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='TRANSFERENCIA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='AD'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F2'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='TRANSFER'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIFOI'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='ECONOMIC_DEV'),
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '70 days',
 '{"monto_total": 320000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- TRANSFER-F3: CDP_EMITIDO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-TRF-002', 'Transferencia Investigación Acuícola UBB', 'PROGRAMA',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='TRANSFERENCIA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='CDP_EMITIDO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F3'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='TRANSFER'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FIC'),
 (SELECT id FROM core.organization WHERE code='DIFOI'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='SCIENCE'),
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '14 days',
 '{"monto_total": 450000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- TRANSFER-F4: EN_EJECUCION
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-TRF-003', 'Transferencia Programa Turismo Aventura Punilla', 'PROGRAMA',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='TRANSFERENCIA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_EJECUCION'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='TRANSFER'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIFOI'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='TOURISM'),
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '85 days',
 '{"monto_total": 280000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- TRANSFER-F5: TERMINADO_ANTICIPADAMENTE
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-TRF-004', 'Transferencia Capacitación Silvoagropecuaria', 'PROGRAMA',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='TRANSFERENCIA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='TERMINADO_ANTICIPADAMENTE'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F5'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='TRANSFER'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIFOI'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='ENVIRONMENT'),
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '10 days',
 '{"monto_total": 190000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- === GLOSA06 (4 IPRs) ===
-- GLOSA06-F1: EN_REVISION
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-G06-001', 'Estudio Plan Regulador Comunal Chillán', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='ESTUDIO'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_REVISION'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F1'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='GLOSA06'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPLADE'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='ENVIRONMENT'),
 (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '22 days',
 '{"monto_total": 380000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- GLOSA06-F2: RF (Recomendación Favorable)
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-G06-002', 'Estudio Factibilidad Tren Chillán-Concepción', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='ESTUDIO'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='RF'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F2'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='GLOSA06'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='SECTORIAL'),
 (SELECT id FROM core.organization WHERE code='DIPLADE'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='TRANSPORT'),
 (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '80 days',
 '{"monto_total": 520000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- GLOSA06-F4: EN_FORMALIZACION
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-G06-003', 'Estudio Diagnóstico Residuos Sólidos Ñuble', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='ESTUDIO'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_FORMALIZACION'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='GLOSA06'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPLADE'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='ENVIRONMENT'),
 (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '30 days',
 '{"monto_total": 150000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- GLOSA06-F5: CERRADO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-G06-004', 'Estudio Zonificación Borde Costero Itata', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='ESTUDIO'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='CERRADO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F5'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='GLOSA06'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIPLADE'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='ENVIRONMENT'),
 (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '45 days',
 '{"monto_total": 210000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- === FRPD (4 IPRs) ===
-- FRPD-F0: INGRESADO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-FRPD-001', 'Equipamiento Laboratorio Informática Escuelas Rurales', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='EQUIPAMIENTO'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='INGRESADO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F0'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRPD'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIDESO'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='EDUCATION'),
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '2 days',
 '{"monto_total": 160000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- FRPD-F2: ITF (Informe Técnico Favorable)
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-FRPD-002', 'Adquisición Ambulancias SAMU Ñuble', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='EQUIPAMIENTO'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='ITF'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F2'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRPD'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='SECTORIAL'),
 (SELECT id FROM core.organization WHERE code='DIDESO'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='HEALTH'),
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '58 days',
 '{"monto_total": 480000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- FRPD-F4: EN_LICITACION
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-FRPD-003', 'Equipamiento Seguridad Ciudadana Chillán', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='EQUIPAMIENTO'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_LICITACION'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRPD'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DAF'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='SECURITY'),
 (SELECT id FROM core."user" WHERE email='jefe.daf@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '28 days',
 '{"monto_total": 380000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.daf@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- FRPD-F4: ADJUDICADO + ANULADO cross-cutting
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-FRPD-004', 'Equipamiento Tecnológico Bibliotecas Públicas', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='EQUIPAMIENTO'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='ANULADO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F2'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRPD'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIDESO'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='EDUCATION'),
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '60 days',
 '{"monto_total": 220000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- === Estados faltantes: SUSPENDIDO, RECEPCION_DEFINITIVA, ADJUDICADO, CONTRATO_FIRMADO, AT ===
-- Extra: SUSPENDIDO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-EXT-001', 'Construcción Centro Comunitario Treguaco (Suspendido)', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='SUSPENDIDO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='CULTURE'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '45 days',
 '{"monto_total": 720000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- Extra: RECEPCION_DEFINITIVA
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-EXT-002', 'Mejoramiento Ruta Turística Valle del Itata', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='RECEPCION_DEFINITIVA'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='FRIL'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='TOURISM'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '10 days',
 '{"monto_total": 95000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- Extra: ADJUDICADO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-EXT-003', 'Construcción Parque Urbano Ribera Chillán', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='ADJUDICADO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='ENVIRONMENT'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '18 days',
 '{"monto_total": 2800000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- Extra: CONTRATO_FIRMADO
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-EXT-004', 'Mejoramiento Agua Potable Rural San Ignacio', 'PROYECTO',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='INFRAESTRUCTURA'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='CONTRATO_FIRMADO'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SNI'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='SECTORIAL'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='HEALTH'),
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '6 days',
 '{"monto_total": 1400000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;

-- Extra: AT (Aprobación Técnica)
INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id, mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id, assignee_id, phase_entered_at, metadata, created_by_id) VALUES
('DEMO-R-EXT-005', 'Subsidio Habitacional Emergencia El Carmen', 'PROGRAMA',
 (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code='SUBSIDIO'),
 (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='AT'),
 (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F2'),
 (SELECT id FROM ref.category WHERE scheme='mechanism' AND code='SUBV8'),
 (SELECT id FROM ref.category WHERE scheme='funding_source' AND code='FNDR'),
 (SELECT id FROM core.organization WHERE code='DIDESO'),
 (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code='HEALTH'),
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'),
 CURRENT_TIMESTAMP - INTERVAL '42 days',
 '{"monto_total": 340000000}'::jsonb,
 (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'))
ON CONFLICT (codigo_bip) DO NOTHING;


-- =============================================================================
-- TIER 2B: IPRs ADICIONALES (~70 registros via DO block)
-- =============================================================================
-- Genera 70 IPRs más para llegar a 110 total.
-- Nombres realistas de proyectos Región de Ñuble.
-- Distribución: ~10 F0, ~12 F1, ~15 F2, ~8 F3, ~18 F4, ~7 F5.

DO $$
DECLARE
    v_codes TEXT[];
    v_names TEXT[];
    v_natures TEXT[];
    v_types TEXT[];
    v_states TEXT[];
    v_phases TEXT[];
    v_mechs TEXT[];
    v_sources TEXT[];
    v_divs TEXT[];
    v_sectors TEXT[];
    v_users TEXT[];
    v_amounts NUMERIC[];
    v_days INTEGER[];
    v_i INTEGER;
BEGIN
    -- === Parallel arrays: 70 IPRs ===
    v_codes := ARRAY[
        -- SNI extras (17)
        'DEMO-R-SNI-101','DEMO-R-SNI-102','DEMO-R-SNI-103','DEMO-R-SNI-104','DEMO-R-SNI-105',
        'DEMO-R-SNI-106','DEMO-R-SNI-107','DEMO-R-SNI-108','DEMO-R-SNI-109','DEMO-R-SNI-110',
        'DEMO-R-SNI-111','DEMO-R-SNI-112','DEMO-R-SNI-113','DEMO-R-SNI-114','DEMO-R-SNI-115',
        'DEMO-R-SNI-116','DEMO-R-SNI-117',
        -- FRIL extras (13)
        'DEMO-R-FRIL-101','DEMO-R-FRIL-102','DEMO-R-FRIL-103','DEMO-R-FRIL-104','DEMO-R-FRIL-105',
        'DEMO-R-FRIL-106','DEMO-R-FRIL-107','DEMO-R-FRIL-108','DEMO-R-FRIL-109','DEMO-R-FRIL-110',
        'DEMO-R-FRIL-111','DEMO-R-FRIL-112','DEMO-R-FRIL-113',
        -- C33 extras (11)
        'DEMO-R-C33-101','DEMO-R-C33-102','DEMO-R-C33-103','DEMO-R-C33-104','DEMO-R-C33-105',
        'DEMO-R-C33-106','DEMO-R-C33-107','DEMO-R-C33-108','DEMO-R-C33-109','DEMO-R-C33-110',
        'DEMO-R-C33-111',
        -- SUBV8 extras (10)
        'DEMO-R-SUBV8-101','DEMO-R-SUBV8-102','DEMO-R-SUBV8-103','DEMO-R-SUBV8-104','DEMO-R-SUBV8-105',
        'DEMO-R-SUBV8-106','DEMO-R-SUBV8-107','DEMO-R-SUBV8-108','DEMO-R-SUBV8-109','DEMO-R-SUBV8-110',
        -- TRANSFER extras (8)
        'DEMO-R-TRF-101','DEMO-R-TRF-102','DEMO-R-TRF-103','DEMO-R-TRF-104',
        'DEMO-R-TRF-105','DEMO-R-TRF-106','DEMO-R-TRF-107','DEMO-R-TRF-108',
        -- GLOSA06 extras (6)
        'DEMO-R-G06-101','DEMO-R-G06-102','DEMO-R-G06-103','DEMO-R-G06-104','DEMO-R-G06-105','DEMO-R-G06-106',
        -- FRPD extras (5)
        'DEMO-R-FRPD-101','DEMO-R-FRPD-102','DEMO-R-FRPD-103','DEMO-R-FRPD-104','DEMO-R-FRPD-105'
    ];

    v_names := ARRAY[
        -- SNI (17)
        'Ampliación Hospital San Carlos','Construcción Gimnasio Municipal Coelemu','Mejoramiento Red APR El Carmen',
        'Reposición Escuela Rural Pemuco','Centro Día Adulto Mayor Chillán','Ampliación CESFAM Quillón',
        'Mejoramiento Estadio Municipal Quirihue','Paseo Peatonal Costanera Chillán','Reposición Cuartel Bomberos Yungay',
        'Sede Comunitaria San Ignacio','Mejoramiento Parque Municipal Coihueco','Ampliación Liceo Técnico San Carlos',
        'Puente Vehicular Río Ñuble','Mejoramiento Terminal Rodoviario Chillán','Reposición Red Alcantarillado Bulnes',
        'Centro Cultural Ninhue','Mejoramiento Acceso Sur San Fabián',
        -- FRIL (13)
        'Reposición Luminarias LED Chillán Viejo','Mejoramiento Cancha Futbolito Pinto','Cierre Perimetral Escuela Cobquecura',
        'Reposición Juegos Infantiles Plaza Ránquil','Vereda Calle Principal Treguaco','Área Verde Portezuelo',
        'Techado Cancha Municipal El Carmen','Sede JV Villa Los Héroes Chillán','Paradero Buses Pemuco Centro',
        'Reposición Baños Públicos Feria Quillón','Iluminación Parque Central Bulnes','Estacionamiento Municipal Coelemu',
        'Reposición Mobiliario Urbano Plaza Yungay',
        -- C33 (11)
        'Conservación Ruta Q-50 Ñiquén-San Carlos','Conservación Puente Río Chillán Sur','Conservación Camino Cobquecura Alto',
        'Conservación Edificio Municipal Treguaco','Conservación Red Vial Rural Coihueco','Conservación Puente San Fabián',
        'Conservación Costanera Río Chillán Tr.2','Conservación Camino San Ignacio-Pemuco','Conservación Edificio GORE Ala Norte',
        'Conservación Aceras Centro Histórico Chillán','Conservación Ruta Panorámica Itata',
        -- SUBV8 (10)
        'Programa Emprendedoras Rurales Ñuble','Programa Deporte Escolar Punilla','Programa Ferias Costumbristas Itata',
        'Programa Alfabetización Digital Adultos','Programa Rescate Patrimonio Artesanal','Programa Reciclaje Comunitario Diguillín',
        'Programa Alimentación Saludable Escuelas','Programa Turismo Rural Comunitario','Programa Capacitación Oficios Jóvenes',
        'Programa Inclusión Deportiva PcD',
        -- TRANSFER (8)
        'Transferencia Innovación Agrícola UBB','Transferencia Energías Renovables Ñuble','Transferencia Acuicultura Cobquecura',
        'Transferencia Conservación Bosque Nativo','Transferencia Gastronomía Regional','Transferencia Formación TIC Municipios',
        'Transferencia Innovación Vitivinícola 2.0','Transferencia Observatorio Territorial',
        -- GLOSA06 (6)
        'Estudio Impacto Ambiental Ruta Costera','Estudio Plan Movilidad Urbana Chillán','Estudio Catastro Patrimonio Arquitectónico',
        'Estudio Riego Tecnificado Valle Itata','Estudio Masterplan Parque Industrial','Estudio Red Ciclovías Chillán',
        -- FRPD (5)
        'Equipamiento Cámaras Seguridad Comunal','Adquisición Vehículos Emergencia GORE','Equipamiento Cocinas Escuelas Rurales',
        'Adquisición Equipos Topográficos DIT','Equipamiento Bibliotecas Digitales Comunales'
    ];

    v_natures := ARRAY[
        -- SNI: all PROYECTO
        'PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO',
        'PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO',
        -- FRIL: all PROYECTO
        'PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO',
        'PROYECTO','PROYECTO','PROYECTO','PROYECTO',
        -- C33: all PROYECTO
        'PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO',
        'PROYECTO','PROYECTO',
        -- SUBV8: all PROGRAMA
        'PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA',
        -- TRANSFER: all PROGRAMA
        'PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA','PROGRAMA',
        -- GLOSA06: all PROYECTO
        'PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO',
        -- FRPD: all PROYECTO
        'PROYECTO','PROYECTO','PROYECTO','PROYECTO','PROYECTO'
    ];

    v_types := ARRAY[
        -- SNI
        'INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA',
        'INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA',
        'INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA',
        -- FRIL
        'EQUIPAMIENTO','INFRAESTRUCTURA','INFRAESTRUCTURA','EQUIPAMIENTO','INFRAESTRUCTURA','INFRAESTRUCTURA',
        'INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA','INFRAESTRUCTURA','EQUIPAMIENTO','INFRAESTRUCTURA','EQUIPAMIENTO',
        -- C33
        'CONSERVACION','CONSERVACION','CONSERVACION','CONSERVACION','CONSERVACION','CONSERVACION',
        'CONSERVACION','CONSERVACION','CONSERVACION','CONSERVACION','CONSERVACION',
        -- SUBV8
        'PROGRAMA_SOCIAL','PROGRAMA_SOCIAL','PROGRAMA_SOCIAL','PROGRAMA_SOCIAL','PROGRAMA_SOCIAL',
        'PROGRAMA_SOCIAL','PROGRAMA_SOCIAL','PROGRAMA_SOCIAL','PROGRAMA_SOCIAL','PROGRAMA_SOCIAL',
        -- TRANSFER
        'TRANSFERENCIA','TRANSFERENCIA','TRANSFERENCIA','TRANSFERENCIA','TRANSFERENCIA','TRANSFERENCIA','TRANSFERENCIA','TRANSFERENCIA',
        -- GLOSA06
        'ESTUDIO','ESTUDIO','ESTUDIO','ESTUDIO','ESTUDIO','ESTUDIO',
        -- FRPD
        'EQUIPAMIENTO','EQUIPAMIENTO','EQUIPAMIENTO','EQUIPAMIENTO','EQUIPAMIENTO'
    ];

    -- States distributed across all phases:
    -- F0(10), F1(12), F2(15), F3(8), F4(18), F5(7)
    v_states := ARRAY[
        -- SNI: F0(3), F1(2), F2(3), F3(2), F4(5), F5(2)
        'INGRESADO','INGRESADO','INGRESADO','EN_REVISION','ADMISIBLE',
        'EN_EVALUACION','RS','AD','CDP_EMITIDO','CDP_EMITIDO',
        'EN_FORMALIZACION','FORMALIZADO','EN_EJECUCION','EN_OBRA','EN_OBRA',
        'RECEPCION_DEFINITIVA','EN_RENDICION',
        -- FRIL: F0(2), F1(2), F2(2), F3(1), F4(4), F5(2)
        'INGRESADO','INGRESADO','EN_REVISION','PRE_ADMISIBLE',
        'EN_EVALUACION','FC','CDP_EMITIDO',
        'EN_EJECUCION','EN_EJECUCION','EN_EJECUCION','RECEPCION_PROVISORIA',
        'CERRADO','EN_CIERRE_ADMINISTRATIVO',
        -- C33: F0(1), F1(2), F2(2), F3(1), F4(3), F5(2)
        'INGRESADO','EN_REVISION','ADMISIBLE','EN_EVALUACION','RS',
        'CDP_EMITIDO','EN_EJECUCION','EN_OBRA','RECEPCION_PROVISORIA',
        'EN_RENDICION','RENDICION_APROBADA',
        -- SUBV8: F1(2), F2(2), F3(1), F4(3), F5(2)
        'EN_REVISION','ADMISIBLE','EN_EVALUACION','OT','CDP_EMITIDO',
        'FORMALIZADO','FORMALIZADO','EN_EJECUCION','EN_CIERRE_ADMINISTRATIVO','CERRADO',
        -- TRANSFER: F1(1), F2(2), F3(1), F4(3), F5(1)
        'ADMISIBLE','EN_EVALUACION','RF','CDP_EMITIDO',
        'EN_FORMALIZACION','FORMALIZADO','EN_EJECUCION','TERMINADO_ANTICIPADAMENTE',
        -- GLOSA06: F0(1), F1(1), F2(2), F4(1), F5(1)
        'INGRESADO','EN_REVISION','EN_EVALUACION','ITF','EN_EJECUCION','CERRADO',
        -- FRPD: F0(1), F2(1), F3(1), F4(1), F5(1)
        'INGRESADO','AT','CDP_EMITIDO','ADJUDICADO','EN_RENDICION'
    ];

    v_phases := ARRAY[
        -- SNI
        'F0','F0','F0','F1','F1','F2','F2','F2','F3','F3','F4','F4','F4','F4','F4','F4','F5',
        -- FRIL
        'F0','F0','F1','F1','F2','F2','F3','F4','F4','F4','F4','F5','F5',
        -- C33
        'F0','F1','F1','F2','F2','F3','F4','F4','F4','F5','F5',
        -- SUBV8
        'F1','F1','F2','F2','F3','F4','F4','F4','F5','F5',
        -- TRANSFER
        'F1','F2','F2','F3','F4','F4','F4','F5',
        -- GLOSA06
        'F0','F1','F2','F2','F4','F5',
        -- FRPD
        'F0','F2','F3','F4','F5'
    ];

    v_mechs := ARRAY[
        'SNI','SNI','SNI','SNI','SNI','SNI','SNI','SNI','SNI','SNI','SNI','SNI','SNI','SNI','SNI','SNI','SNI',
        'FRIL','FRIL','FRIL','FRIL','FRIL','FRIL','FRIL','FRIL','FRIL','FRIL','FRIL','FRIL','FRIL',
        'C33','C33','C33','C33','C33','C33','C33','C33','C33','C33','C33',
        'SUBV8','SUBV8','SUBV8','SUBV8','SUBV8','SUBV8','SUBV8','SUBV8','SUBV8','SUBV8',
        'TRANSFER','TRANSFER','TRANSFER','TRANSFER','TRANSFER','TRANSFER','TRANSFER','TRANSFER',
        'GLOSA06','GLOSA06','GLOSA06','GLOSA06','GLOSA06','GLOSA06',
        'FRPD','FRPD','FRPD','FRPD','FRPD'
    ];

    v_sources := ARRAY[
        'FNDR','SECTORIAL','FNDR','FNDR','FNDR','SECTORIAL','FNDR','FNDR','FNDR','FNDR',
        'FNDR','FNDR','SECTORIAL','FNDR','FNDR','FNDR','FNDR',
        'FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR',
        'FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR',
        'FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR','FNDR',
        'FIC','FNDR','FNDR','FNDR','FNDR','FNDR','FIC','FNDR',
        'FNDR','FNDR','FNDR','FNDR','FNDR','FNDR',
        'FNDR','FNDR','FNDR','SECTORIAL','FNDR'
    ];

    v_divs := ARRAY[
        'DIT','DIT','DIT','DIPIR','DIDESO','DIDESO','DIT','DIT','DIPIR','DIPIR',
        'DIT','DIPIR','DIT','DIT','DIT','DIPIR','DIPIR',
        'DIPIR','DIPIR','DIPIR','DIPIR','DIPIR','DIPIR','DIPIR','DIPIR','DIPIR','DIPIR','DIPIR','DIPIR','DIPIR',
        'DIT','DIT','DIT','DIT','DIT','DIT','DIT','DIT','DIT','DIT','DIT',
        'DIDESO','DIDESO','DIFOI','DIDESO','DIDESO','DIDESO','DIDESO','DIFOI','DIDESO','DIDESO',
        'DIFOI','DIFOI','DIFOI','DIFOI','DIFOI','DIFOI','DIFOI','DIPLADE',
        'DIPLADE','DIPLADE','DIPLADE','DIPLADE','DIPLADE','DIPLADE',
        'DAF','DAF','DIDESO','DIT','DIDESO'
    ];

    v_sectors := ARRAY[
        'HEALTH','SPORTS','HEALTH','EDUCATION','HEALTH','HEALTH','SPORTS','CULTURE','SECURITY','CULTURE',
        'ENVIRONMENT','EDUCATION','TRANSPORT','TRANSPORT','HEALTH','CULTURE','TRANSPORT',
        'CULTURE','SPORTS','EDUCATION','CULTURE','TRANSPORT','ENVIRONMENT','SPORTS','CULTURE','TRANSPORT',
        'HEALTH','SPORTS','TRANSPORT','SPORTS',
        'TRANSPORT','TRANSPORT','TRANSPORT','CULTURE','TRANSPORT','TRANSPORT','TRANSPORT','TRANSPORT','CULTURE',
        'CULTURE','TOURISM',
        'ECONOMIC_DEV','SPORTS','TOURISM','EDUCATION','CULTURE','ENVIRONMENT','HEALTH','TOURISM','EDUCATION','SPORTS',
        'SCIENCE','ENVIRONMENT','SCIENCE','ENVIRONMENT','TOURISM','EDUCATION','ECONOMIC_DEV','ENVIRONMENT',
        'ENVIRONMENT','TRANSPORT','CULTURE','ENVIRONMENT','ECONOMIC_DEV','TRANSPORT',
        'SECURITY','SECURITY','EDUCATION','SCIENCE','EDUCATION'
    ];

    v_users := ARRAY[
        'jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','analista.dipir@goreos.cl','jefe.dideso@goreos.cl',
        'jefe.dideso@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','analista.dipir@goreos.cl','analista.dipir@goreos.cl',
        'jefe.dit@goreos.cl','analista.dipir@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl',
        'analista.dipir@goreos.cl','analista.dipir@goreos.cl',
        'analista.dipir@goreos.cl','analista.dipir@goreos.cl','analista.dipir@goreos.cl','analista.dipir@goreos.cl',
        'analista.dipir@goreos.cl','analista.dipir@goreos.cl','analista.dipir@goreos.cl','analista.dipir@goreos.cl',
        'analista.dipir@goreos.cl','analista.dipir@goreos.cl','analista.dipir@goreos.cl','analista.dipir@goreos.cl','analista.dipir@goreos.cl',
        'jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl',
        'jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl',
        'jefe.dideso@goreos.cl','jefe.dideso@goreos.cl','jefe.difoi@goreos.cl','jefe.dideso@goreos.cl','jefe.dideso@goreos.cl',
        'jefe.dideso@goreos.cl','jefe.dideso@goreos.cl','jefe.difoi@goreos.cl','jefe.dideso@goreos.cl','jefe.dideso@goreos.cl',
        'jefe.difoi@goreos.cl','jefe.difoi@goreos.cl','jefe.difoi@goreos.cl','jefe.difoi@goreos.cl','jefe.difoi@goreos.cl',
        'jefe.difoi@goreos.cl','jefe.difoi@goreos.cl','analista.diplade@goreos.cl',
        'analista.diplade@goreos.cl','analista.diplade@goreos.cl','analista.diplade@goreos.cl','analista.diplade@goreos.cl',
        'analista.diplade@goreos.cl','analista.diplade@goreos.cl',
        'jefe.daf@goreos.cl','jefe.daf@goreos.cl','jefe.dideso@goreos.cl','jefe.dit@goreos.cl','jefe.dideso@goreos.cl'
    ];

    v_amounts := ARRAY[
        3200000000,1500000000,850000000,420000000,1200000000,680000000,780000000,2100000000,350000000,
        280000000,1800000000,950000000,4200000000,3800000000,2600000000,450000000,1100000000,
        95000000,75000000,55000000,42000000,68000000,38000000,88000000,72000000,58000000,
        48000000,65000000,82000000,52000000,
        520000000,380000000,290000000,180000000,450000000,310000000,680000000,240000000,350000000,420000000,280000000,
        180000000,120000000,95000000,150000000,85000000,65000000,110000000,140000000,200000000,160000000,
        380000000,220000000,290000000,180000000,250000000,120000000,420000000,350000000,
        480000000,320000000,280000000,190000000,550000000,210000000,
        250000000,180000000,95000000,320000000,140000000
    ];

    v_days := ARRAY[
        3,5,8,18,25,48,55,22,12,9,35,40,95,130,110,20,28,
        2,4,12,30,42,52,10,75,85,65,15,22,45,
        6,15,20,50,58,8,100,115,18,25,35,
        14,22,45,62,10,105,95,80,20,38,
        25,48,68,12,32,98,88,15,
        4,16,46,56,92,42,
        3,55,9,22,30
    ];

    FOR v_i IN 1..array_length(v_codes, 1) LOOP
        INSERT INTO core.ipr (
            codigo_bip, name, ipr_nature, ipr_type_id, status_id, mcd_phase_id,
            mechanism_id, funding_source_id, sponsor_division_id, investment_sector_id,
            assignee_id, phase_entered_at, metadata, created_by_id
        ) VALUES (
            v_codes[v_i], v_names[v_i], v_natures[v_i]::ipr_nature_enum,
            (SELECT id FROM ref.category WHERE scheme='ipr_type' AND code=v_types[v_i]),
            (SELECT id FROM ref.category WHERE scheme='ipr_state' AND code=v_states[v_i]),
            (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code=v_phases[v_i]),
            (SELECT id FROM ref.category WHERE scheme='mechanism' AND code=v_mechs[v_i]),
            (SELECT id FROM ref.category WHERE scheme='funding_source' AND code=v_sources[v_i]),
            (SELECT id FROM core.organization WHERE code=v_divs[v_i]),
            (SELECT id FROM ref.category WHERE scheme='investment_sector' AND code=v_sectors[v_i]),
            (SELECT id FROM core."user" WHERE email=v_users[v_i]),
            CURRENT_TIMESTAMP - (v_days[v_i] || ' days')::interval,
            jsonb_build_object('monto_total', v_amounts[v_i]),
            (SELECT id FROM core."user" WHERE email=v_users[v_i])
        ) ON CONFLICT (codigo_bip) DO NOTHING;
    END LOOP;

    RAISE NOTICE 'Inserted % additional IPRs', array_length(v_codes, 1);
END $$;


-- =============================================================================
-- TIER 3: SATÉLITES IPR (ENRIQUECIDOS — PHASE-AWARE)
-- =============================================================================
-- TODOS los IPRs reciben satélites ricos según su fase:
-- F0: 3 parties, 2 territories, 1-2 milestones
-- F1: 4 parties, 2 territories, 2-3 milestones
-- F2: 4 parties, 3 territories, 3-5 milestones, 1 evaluation
-- F3: 5 parties, 3 territories, 4-6 milestones, 1-2 evaluations
-- F4: 6-8 parties (ITO/mandatario/fiscalizador), 4 territories, 6-13 milestones, 2 evals, 2-4 reports
-- F5: 7-10 parties, 4 territories, 10-13 milestones (all completed), 2 evals, 3-5 reports
-- 6 "IPRs héroe" con cadenas artesanales completas:
--   H1: DEMO-R-SNI-007 (EN_OBRA, Pavimentación Chillán) — obra activa con ITO
--   H2: DEMO-R-SNI-008 (CERRADO, Multicancha Yungay) — ciclo completo
--   H3: DEMO-R-FRIL-005 (EN_EJECUCION, Techado Feria) — ejecución media
--   H4: DEMO-R-TRF-003 (EN_EJECUCION, Turismo Punilla) — programa transferencia
--   H5: DEMO-R-SUBV8-004 (FORMALIZADO, Huertos Punilla) — programa social
--   H6: DEMO-R-EXT-003 (ADJUDICADO, Parque Urbano) — recién adjudicado
-- Resto: satélites genéricos via DO blocks.

-- =============================================================================
-- 3.1 IPR_PARTY — genéricos + héroe enrichment
-- =============================================================================
DO $$
DECLARE
    v_ipr RECORD;
    v_postulante UUID; v_ejecutor UUID; v_ut UUID; v_ito UUID;
    v_formulador UUID; v_fiscalizador UUID; v_mandante UUID; v_mandatario UUID;
    v_beneficiario UUID; v_cofinanciador UUID; v_supervisor UUID;
    v_munis TEXT[] := ARRAY['DEMO-R-MUNI-CHILLAN','DEMO-R-MUNI-SANCARLOS','DEMO-R-MUNI-QUIRIHUE','DEMO-R-MUNI-COIHUECO','DEMO-R-MUNI-BULNES','DEMO-R-MUNI-PINTO','DEMO-R-MUNI-COELEMU'];
    v_idx INTEGER := 0;
BEGIN
    SELECT id INTO v_postulante FROM ref.category WHERE scheme='ipr_party_role' AND code='POSTULANTE';
    SELECT id INTO v_ejecutor FROM ref.category WHERE scheme='ipr_party_role' AND code='EJECUTOR';
    SELECT id INTO v_ut FROM ref.category WHERE scheme='ipr_party_role' AND code='UNIDAD_TECNICA';
    SELECT id INTO v_ito FROM ref.category WHERE scheme='ipr_party_role' AND code='ITO';
    SELECT id INTO v_formulador FROM ref.category WHERE scheme='ipr_party_role' AND code='FORMULADOR';
    SELECT id INTO v_fiscalizador FROM ref.category WHERE scheme='ipr_party_role' AND code='FISCALIZADOR';
    SELECT id INTO v_mandante FROM ref.category WHERE scheme='ipr_party_role' AND code='MANDANTE';
    SELECT id INTO v_mandatario FROM ref.category WHERE scheme='ipr_party_role' AND code='MANDATARIO';
    SELECT id INTO v_beneficiario FROM ref.category WHERE scheme='ipr_party_role' AND code='BENEFICIARIO';
    SELECT id INTO v_cofinanciador FROM ref.category WHERE scheme='ipr_party_role' AND code='COFINANCIADOR';
    SELECT id INTO v_supervisor FROM ref.category WHERE scheme='ipr_party_role' AND code='SUPERVISOR_GORE';

    FOR v_ipr IN SELECT id, codigo_bip, sponsor_division_id FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%' ORDER BY codigo_bip LOOP
        v_idx := v_idx + 1;

        -- === BASE: todos los IPRs tienen POSTULANTE + EJECUTOR + UNIDAD_TECNICA ===
        INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person, contact_email)
        VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code = v_munis[1 + (v_idx % 7)]),
                v_postulante, true, 'Contacto Municipal ' || v_idx, 'contacto' || v_idx || '@municipio.cl')
        ON CONFLICT DO NOTHING;

        INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
        VALUES (v_ipr.id, v_ipr.sponsor_division_id, v_ejecutor, false, 'Encargado Ejecución')
        ON CONFLICT DO NOTHING;

        IF v_idx % 3 = 0 THEN
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code = 'DEMO-R-SERVIU-NUBLE'), v_ut, false, 'Profesional SERVIU')
            ON CONFLICT DO NOTHING;
        ELSE
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, v_ipr.sponsor_division_id, v_ut, false, 'Prof. Unidad Técnica')
            ON CONFLICT DO NOTHING;
        END IF;

        -- === HÉROE H1: SNI-007 (EN_OBRA) — cadena completa de obra ===
        IF v_ipr.codigo_bip = 'DEMO-R-SNI-007' THEN
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person, contact_email)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-ING-NUBLE'), v_ito, false, 'Ing. Gonzalo Riquelme A.', 'griquelme@ingnuble.cl')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person, contact_email)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-CONST-ITATA'), v_mandatario, false, 'Gerente Técnico Const. Itata', 'gerencia@constructoraitata.cl')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-SERVIU-NUBLE'), v_fiscalizador, false, 'Fiscalizador SERVIU Regional')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='GORE-NUBLE'), v_mandante, false, 'GORE Ñuble — Mandante')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, v_ipr.sponsor_division_id, v_supervisor, false, 'Supervisor DIT')
            ON CONFLICT DO NOTHING;
        END IF;

        -- === HÉROE H2: SNI-008 (CERRADO) — ciclo completo ===
        IF v_ipr.codigo_bip = 'DEMO-R-SNI-008' THEN
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-ING-NUBLE'), v_ito, false, 'ITO asignado (obra finalizada)')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-BULNES'), v_beneficiario, false, 'Comunidad Yungay — beneficiaria directa')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='GORE-NUBLE'), v_mandante, false, 'GORE Ñuble — Mandante')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-SERVIU-NUBLE'), v_mandatario, false, 'SERVIU Ñuble — Mandatario')
            ON CONFLICT DO NOTHING;
        END IF;

        -- === HÉROE H4: TRF-003 (EN_EJECUCION programa) ===
        IF v_ipr.codigo_bip = 'DEMO-R-TRF-003' THEN
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person, contact_email)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-SERNATUR-NUBLE'), v_mandatario, false, 'Dir. Regional SERNATUR', 'dcontreras@sernatur-nuble.cl')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-SANCARLOS'), v_beneficiario, false, 'Cámara de Turismo Punilla')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-UBB'), v_cofinanciador, false, 'Facultad Ciencias Empresariales UBB')
            ON CONFLICT DO NOTHING;
        END IF;

        -- === HÉROE H6: EXT-003 (ADJUDICADO parque) ===
        IF v_ipr.codigo_bip = 'DEMO-R-EXT-003' THEN
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-CONST-ITATA'), v_mandatario, false, 'Constructora Itata — adjudicatario')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-CHILLAN'), v_beneficiario, false, 'Vecinos sector Ribera Norte')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='GORE-NUBLE'), v_mandante, false, 'GORE Ñuble — Mandante')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-MOP-NUBLE'), v_fiscalizador, false, 'MOP DOH — fiscalización hidráulica')
            ON CONFLICT DO NOTHING;
        END IF;

        -- === HÉROE H5: SUBV8-004 (FORMALIZADO programa social) ===
        IF v_ipr.codigo_bip = 'DEMO-R-SUBV8-004' THEN
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-FUND-NUBLE'), v_mandatario, false, 'Fundación Ñuble — ejecutor técnico')
            ON CONFLICT DO NOTHING;
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, contact_person)
            VALUES (v_ipr.id, (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-COIHUECO'), v_beneficiario, false, 'Familias beneficiarias comunas rurales')
            ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;
END $$;

-- =============================================================================
-- 3.2 IPR_TERRITORY — genéricos + héroe con zonas de influencia
-- =============================================================================
DO $$
DECLARE
    v_ipr RECORD;
    v_comunas TEXT[] := ARRAY['16101','16102','16103','16104','16105','16106','16107','16201','16202','16203','16204','16205','16206','16207','16301','16302','16303','16304','16305'];
    v_ubicacion UUID; v_impacto_d UUID; v_impacto_i UUID; v_zona UUID;
    v_idx INTEGER := 0;
BEGIN
    SELECT id INTO v_ubicacion FROM ref.category WHERE scheme='territory_impact' AND code='UBICACION';
    SELECT id INTO v_impacto_d FROM ref.category WHERE scheme='territory_impact' AND code='IMPACTO_DIRECTO';
    SELECT id INTO v_impacto_i FROM ref.category WHERE scheme='territory_impact' AND code='IMPACTO_INDIRECTO';
    SELECT id INTO v_zona FROM ref.category WHERE scheme='territory_impact' AND code='ZONA_INFLUENCIA';

    FOR v_ipr IN SELECT id, codigo_bip FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%' ORDER BY codigo_bip LOOP
        v_idx := v_idx + 1;

        -- Ubicación principal
        INSERT INTO core.ipr_territory (ipr_id, territory_id, impact_type_id, is_primary)
        VALUES (v_ipr.id, (SELECT id FROM core.territory WHERE code = v_comunas[1 + (v_idx % 19)]), v_ubicacion, true)
        ON CONFLICT DO NOTHING;

        -- Impacto directo
        INSERT INTO core.ipr_territory (ipr_id, territory_id, impact_type_id, is_primary)
        VALUES (v_ipr.id, (SELECT id FROM core.territory WHERE code = v_comunas[1 + ((v_idx + 5) % 19)]), v_impacto_d, false)
        ON CONFLICT DO NOTHING;

        -- === HÉROES: +2 territorios adicionales (impacto indirecto + zona influencia) ===
        IF v_ipr.codigo_bip IN ('DEMO-R-SNI-007','DEMO-R-SNI-008','DEMO-R-TRF-003','DEMO-R-SUBV8-004','DEMO-R-EXT-003','DEMO-R-FRIL-005') THEN
            INSERT INTO core.ipr_territory (ipr_id, territory_id, impact_type_id, is_primary, notes)
            VALUES (v_ipr.id, (SELECT id FROM core.territory WHERE code = v_comunas[1 + ((v_idx + 10) % 19)]), v_impacto_i, false, 'Impacto indirecto por conectividad')
            ON CONFLICT DO NOTHING;

            INSERT INTO core.ipr_territory (ipr_id, territory_id, impact_type_id, is_primary, notes)
            VALUES (v_ipr.id, (SELECT id FROM core.territory WHERE code = '16'), v_zona, false, 'Zona de influencia regional')
            ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;
END $$;

-- =============================================================================
-- 3.3 IPR_MILESTONE — HÉROES con cadenas completas de 13 tipos, resto genérico
-- =============================================================================
-- Héroes: hitos artesanales con actual_date según avance real
-- Genéricos: 3 hitos base

-- H1: DEMO-R-SNI-007 (EN_OBRA) — 10 hitos, 6 completados
INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='ENTREGA_DISENO'), 'Entrega diseño definitivo SERVIU', CURRENT_DATE - INTERVAL '200 days', CURRENT_DATE - INTERVAL '195 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='APROBACION_CDP'), 'CDP aprobado por DAF', CURRENT_DATE - INTERVAL '170 days', CURRENT_DATE - INTERVAL '168 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='FIRMA_CONVENIO'), 'Firma convenio mandato SERVIU', CURRENT_DATE - INTERVAL '150 days', CURRENT_DATE - INTERVAL '145 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='LICITACION'), 'Publicación bases licitación', CURRENT_DATE - INTERVAL '140 days', CURRENT_DATE - INTERVAL '138 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='ADJUDICACION'), 'Adjudicación a Constructora Itata SpA', CURRENT_DATE - INTERVAL '125 days', CURRENT_DATE - INTERVAL '122 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='INICIO_OBRA'), 'Inicio de obras en terreno', CURRENT_DATE - INTERVAL '120 days', CURRENT_DATE - INTERVAL '118 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_25'), 'Avance 25% — fundaciones y trazado', CURRENT_DATE - INTERVAL '80 days', CURRENT_DATE - INTERVAL '75 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_50'), 'Avance 50% — carpeta y drenaje', CURRENT_DATE - INTERVAL '40 days', NULL),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_75'), 'Avance 75% — pavimentación y señalética', CURRENT_DATE + INTERVAL '20 days', NULL),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='RECEPCION_PROV'), 'Recepción provisoria obra', CURRENT_DATE + INTERVAL '60 days', NULL),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='RECEPCION_DEF'), 'Recepción definitiva', CURRENT_DATE + INTERVAL '120 days', NULL),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='INFORME_FINAL'), 'Informe final DIT al CORE', CURRENT_DATE + INTERVAL '140 days', NULL),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='CIERRE_ADMIN'), 'Cierre administrativo DIPIR', CURRENT_DATE + INTERVAL '180 days', NULL)
ON CONFLICT DO NOTHING;

-- H2: DEMO-R-SNI-008 (CERRADO) — 11 hitos, TODOS completados
INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='ENTREGA_DISENO'), 'Diseño estructural aprobado', CURRENT_DATE - INTERVAL '300 days', CURRENT_DATE - INTERVAL '298 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='APROBACION_CDP'), 'CDP aprobado DIPIR', CURRENT_DATE - INTERVAL '280 days', CURRENT_DATE - INTERVAL '275 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='FIRMA_CONVENIO'), 'Convenio transferencia Muni Bulnes', CURRENT_DATE - INTERVAL '270 days', CURRENT_DATE - INTERVAL '265 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='LICITACION'), 'Bases de licitación publicadas', CURRENT_DATE - INTERVAL '260 days', CURRENT_DATE - INTERVAL '258 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='ADJUDICACION'), 'Adjudicación constructora', CURRENT_DATE - INTERVAL '240 days', CURRENT_DATE - INTERVAL '235 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='INICIO_OBRA'), 'Acta de inicio de obra', CURRENT_DATE - INTERVAL '230 days', CURRENT_DATE - INTERVAL '228 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_25'), 'Hito 25% — radier y estructura', CURRENT_DATE - INTERVAL '180 days', CURRENT_DATE - INTERVAL '176 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_50'), 'Hito 50% — techado y cerramiento', CURRENT_DATE - INTERVAL '130 days', CURRENT_DATE - INTERVAL '125 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_75'), 'Hito 75% — terminaciones', CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE - INTERVAL '88 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='RECEPCION_PROV'), 'Recepción provisoria municipal', CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '58 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='RECEPCION_DEF'), 'Recepción definitiva', CURRENT_DATE - INTERVAL '40 days', CURRENT_DATE - INTERVAL '38 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='INFORME_FINAL'), 'Informe final al CORE', CURRENT_DATE - INTERVAL '35 days', CURRENT_DATE - INTERVAL '33 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='CIERRE_ADMIN'), 'Cierre administrativo — acta firmada', CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '30 days')
ON CONFLICT DO NOTHING;

-- H3: DEMO-R-FRIL-005 (EN_EJECUCION) — 8 hitos, 5 completados
INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='APROBACION_CDP'), 'CDP FRIL aprobado', CURRENT_DATE - INTERVAL '110 days', CURRENT_DATE - INTERVAL '108 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='FIRMA_CONVENIO'), 'Convenio Muni San Nicolás firmado', CURRENT_DATE - INTERVAL '100 days', CURRENT_DATE - INTERVAL '98 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='LICITACION'), 'Trato directo publicado', CURRENT_DATE - INTERVAL '95 days', CURRENT_DATE - INTERVAL '93 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='ADJUDICACION'), 'Adjudicación proveedor', CURRENT_DATE - INTERVAL '92 days', CURRENT_DATE - INTERVAL '90 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='INICIO_OBRA'), 'Inicio obras en feria', CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE - INTERVAL '88 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_25'), 'Retiro estructura antigua', CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '55 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_50'), 'Instalación nuevo techado 50%', CURRENT_DATE - INTERVAL '30 days', NULL),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='RECEPCION_PROV'), 'Recepción provisoria feria', CURRENT_DATE + INTERVAL '30 days', NULL)
ON CONFLICT DO NOTHING;

-- H4: DEMO-R-TRF-003 (EN_EJECUCION programa) — 6 hitos
INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='FIRMA_CONVENIO'), 'Convenio SERNATUR firmado', CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE - INTERVAL '85 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='APROBACION_CDP'), 'CDP programa turismo aprobado', CURRENT_DATE - INTERVAL '85 days', CURRENT_DATE - INTERVAL '82 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='INICIO_OBRA'), 'Inicio actividades en terreno', CURRENT_DATE - INTERVAL '70 days', CURRENT_DATE - INTERVAL '68 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_25'), 'Capacitación 25% operadores turísticos', CURRENT_DATE - INTERVAL '40 days', CURRENT_DATE - INTERVAL '38 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_50'), 'Avance 50% — señalética instalada', CURRENT_DATE + INTERVAL '10 days', NULL),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='INFORME_FINAL'), 'Informe final programa turismo', CURRENT_DATE + INTERVAL '90 days', NULL)
ON CONFLICT DO NOTHING;

-- H5: DEMO-R-SUBV8-004 (FORMALIZADO) — 5 hitos, 2 completados
INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-004'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='APROBACION_CDP'), 'CDP programa huertos aprobado', CURRENT_DATE - INTERVAL '105 days', CURRENT_DATE - INTERVAL '102 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-004'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='FIRMA_CONVENIO'), 'Convenio Muni Coihueco', CURRENT_DATE - INTERVAL '100 days', CURRENT_DATE - INTERVAL '100 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-004'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='INICIO_OBRA'), 'Inicio programa en comunas', CURRENT_DATE - INTERVAL '80 days', NULL),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-004'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_50'), 'Entrega 50% kits huertos', CURRENT_DATE + INTERVAL '30 days', NULL),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-004'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='INFORME_FINAL'), 'Informe final DIDESO', CURRENT_DATE + INTERVAL '120 days', NULL)
ON CONFLICT DO NOTHING;

-- H6: DEMO-R-EXT-003 (ADJUDICADO) — 7 hitos, 5 completados
INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='ENTREGA_DISENO'), 'Diseño paisajístico aprobado', CURRENT_DATE - INTERVAL '90 days', CURRENT_DATE - INTERVAL '88 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='APROBACION_CDP'), 'CDP parque urbano aprobado', CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '58 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='FIRMA_CONVENIO'), 'Convenio mandato Const. Itata', CURRENT_DATE - INTERVAL '40 days', CURRENT_DATE - INTERVAL '38 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='LICITACION'), 'Licitación pública publicada', CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '28 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='ADJUDICACION'), 'Adjudicación Constructora Itata', CURRENT_DATE - INTERVAL '18 days', CURRENT_DATE - INTERVAL '18 days'),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='INICIO_OBRA'), 'Inicio obras planificado', CURRENT_DATE + INTERVAL '15 days', NULL),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM ref.category WHERE scheme='milestone_type' AND code='RECEPCION_DEF'), 'Recepción definitiva', CURRENT_DATE + INTERVAL '270 days', NULL)
ON CONFLICT DO NOTHING;

-- Phase-aware milestones para TODOS los demás IPRs (no héroes)
-- F0-F1: 2-3 hitos planificados
-- F2: 4 hitos (diseño+CDP completados, convenio+licitación planificados)
-- F3: 5 hitos (diseño→CDP completados, convenio+licitación+inicio planificados)
-- F4: 7-10 hitos (cadena parcialmente completada según sub-estado)
-- F5: 8-11 hitos (todos completados)
DO $$
DECLARE
    v_ipr RECORD;
    v_mt RECORD;
    v_heroes TEXT[] := ARRAY['DEMO-R-SNI-007','DEMO-R-SNI-008','DEMO-R-FRIL-005','DEMO-R-TRF-003','DEMO-R-SUBV8-004','DEMO-R-EXT-003'];
    v_phase_num INTEGER;
    v_idx INTEGER := 0;
    v_base_offset INTEGER;
    -- Milestone type IDs
    v_diseno UUID; v_cdp UUID; v_convenio UUID; v_licit UUID; v_adjud UUID;
    v_inicio UUID; v_a25 UUID; v_a50 UUID; v_a75 UUID;
    v_rprov UUID; v_rdef UUID; v_informe UUID; v_cierre UUID;
BEGIN
    SELECT id INTO v_diseno FROM ref.category WHERE scheme='milestone_type' AND code='ENTREGA_DISENO';
    SELECT id INTO v_cdp FROM ref.category WHERE scheme='milestone_type' AND code='APROBACION_CDP';
    SELECT id INTO v_convenio FROM ref.category WHERE scheme='milestone_type' AND code='FIRMA_CONVENIO';
    SELECT id INTO v_licit FROM ref.category WHERE scheme='milestone_type' AND code='LICITACION';
    SELECT id INTO v_adjud FROM ref.category WHERE scheme='milestone_type' AND code='ADJUDICACION';
    SELECT id INTO v_inicio FROM ref.category WHERE scheme='milestone_type' AND code='INICIO_OBRA';
    SELECT id INTO v_a25 FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_25';
    SELECT id INTO v_a50 FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_50';
    SELECT id INTO v_a75 FROM ref.category WHERE scheme='milestone_type' AND code='AVANCE_75';
    SELECT id INTO v_rprov FROM ref.category WHERE scheme='milestone_type' AND code='RECEPCION_PROV';
    SELECT id INTO v_rdef FROM ref.category WHERE scheme='milestone_type' AND code='RECEPCION_DEF';
    SELECT id INTO v_informe FROM ref.category WHERE scheme='milestone_type' AND code='INFORME_FINAL';
    SELECT id INTO v_cierre FROM ref.category WHERE scheme='milestone_type' AND code='CIERRE_ADMIN';

    FOR v_ipr IN
        SELECT i.id, i.codigo_bip, p.code as phase_code, s.code as status_code
        FROM core.ipr i
        JOIN ref.category p ON i.mcd_phase_id = p.id
        JOIN ref.category s ON i.status_id = s.id
        WHERE i.codigo_bip LIKE 'DEMO-R-%' AND i.codigo_bip != ALL(v_heroes)
        ORDER BY i.codigo_bip
    LOOP
        v_idx := v_idx + 1;
        v_base_offset := v_idx * 2; -- stagger dates per IPR
        v_phase_num := CASE v_ipr.phase_code WHEN 'F0' THEN 0 WHEN 'F1' THEN 1 WHEN 'F2' THEN 2 WHEN 'F3' THEN 3 WHEN 'F4' THEN 4 WHEN 'F5' THEN 5 END;

        -- === DISEÑO (F0+ planned, F2+ completed) ===
        IF v_phase_num >= 0 THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_diseno, 'Entrega diseño / formulación',
                    CURRENT_DATE - INTERVAL '180 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_phase_num >= 2 THEN CURRENT_DATE - INTERVAL '175 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === CDP (F1+ planned, F3+ completed) ===
        IF v_phase_num >= 1 THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_cdp, 'Aprobación CDP',
                    CURRENT_DATE - INTERVAL '150 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_phase_num >= 3 THEN CURRENT_DATE - INTERVAL '148 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === CONVENIO (F2+ planned, F3+ completed) ===
        IF v_phase_num >= 2 THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_convenio, 'Firma de convenio',
                    CURRENT_DATE - INTERVAL '130 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_phase_num >= 3 THEN CURRENT_DATE - INTERVAL '128 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === LICITACIÓN (F2+ planned, F4+ completed) ===
        IF v_phase_num >= 2 THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_licit, 'Publicación licitación / trato directo',
                    CURRENT_DATE - INTERVAL '120 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_phase_num >= 4 THEN CURRENT_DATE - INTERVAL '118 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === ADJUDICACIÓN (F3+ planned, F4+ completed) ===
        IF v_phase_num >= 3 THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_adjud, 'Adjudicación',
                    CURRENT_DATE - INTERVAL '110 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_phase_num >= 4 THEN CURRENT_DATE - INTERVAL '108 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === INICIO OBRA (F3+ planned, F4+ completed) ===
        IF v_phase_num >= 3 THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_inicio, 'Inicio de ejecución',
                    CURRENT_DATE - INTERVAL '100 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_phase_num >= 4 AND v_ipr.status_code NOT IN ('EN_FORMALIZACION','EN_LICITACION') THEN CURRENT_DATE - INTERVAL '98 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === AVANCE 25% (F4+ planned, completed for mid-F4+) ===
        IF v_phase_num >= 4 THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_a25, 'Avance 25%',
                    CURRENT_DATE - INTERVAL '70 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_ipr.status_code IN ('EN_OBRA','RECEPCION_PROVISORIA','RECEPCION_DEFINITIVA','EN_EJECUCION') OR v_phase_num = 5
                         THEN CURRENT_DATE - INTERVAL '65 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === AVANCE 50% (F4 mid+ planned, completed for late-F4/F5) ===
        IF v_phase_num >= 4 THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_a50, 'Avance 50%',
                    CURRENT_DATE - INTERVAL '40 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_ipr.status_code IN ('RECEPCION_PROVISORIA','RECEPCION_DEFINITIVA') OR v_phase_num = 5
                         THEN CURRENT_DATE - INTERVAL '35 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === AVANCE 75% (F4 mid+ planned, completed for recepción/F5) ===
        IF v_phase_num >= 4 AND v_ipr.status_code NOT IN ('EN_FORMALIZACION','EN_LICITACION','ADJUDICADO','CONTRATO_FIRMADO') THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_a75, 'Avance 75%',
                    CURRENT_DATE + INTERVAL '10 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_ipr.status_code IN ('RECEPCION_PROVISORIA','RECEPCION_DEFINITIVA') OR v_phase_num = 5
                         THEN CURRENT_DATE - INTERVAL '10 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === RECEPCION PROVISORIA (F4 late+, completed for F5) ===
        IF v_phase_num >= 4 AND v_ipr.status_code NOT IN ('EN_FORMALIZACION','FORMALIZADO','EN_LICITACION','ADJUDICADO','CONTRATO_FIRMADO') THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_rprov, 'Recepción provisoria',
                    CURRENT_DATE + INTERVAL '40 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_ipr.status_code IN ('RECEPCION_DEFINITIVA') OR v_phase_num = 5
                         THEN CURRENT_DATE - INTERVAL '5 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === RECEPCION DEFINITIVA (F4 late+, completed for F5) ===
        IF v_phase_num >= 4 AND v_ipr.status_code NOT IN ('EN_FORMALIZACION','FORMALIZADO','EN_LICITACION','ADJUDICADO','CONTRATO_FIRMADO','EN_EJECUCION','EN_OBRA') THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_rdef, 'Recepción definitiva',
                    CURRENT_DATE + INTERVAL '60 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_phase_num = 5 THEN CURRENT_DATE - INTERVAL '3 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === INFORME FINAL (F4+, completed for F5) ===
        IF v_phase_num >= 4 THEN
            INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
            VALUES (v_ipr.id, v_informe, 'Informe final',
                    CURRENT_DATE + INTERVAL '80 days' + (v_base_offset * INTERVAL '1 day'),
                    CASE WHEN v_phase_num = 5 THEN CURRENT_DATE - INTERVAL '2 days' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === CIERRE ADMIN (always planned, completed for CERRADO) ===
        INSERT INTO core.ipr_milestone (ipr_id, milestone_type_id, description, planned_date, actual_date)
        VALUES (v_ipr.id, v_cierre, 'Cierre administrativo',
                CURRENT_DATE + INTERVAL '120 days' + (v_base_offset * INTERVAL '1 day'),
                CASE WHEN v_ipr.status_code IN ('CERRADO','EN_CIERRE_ADMINISTRATIVO') THEN CURRENT_DATE - INTERVAL '1 day' + (v_base_offset * INTERVAL '1 day') ELSE NULL END)
        ON CONFLICT DO NOTHING;
    END LOOP;
END $$;

-- =============================================================================
-- 3.4 EVALUATION_ASSIGNMENT — héroes con evaluaciones múltiples, resto genérico
-- =============================================================================
-- H1: SNI-007 — 2 evaluaciones (MDSF + GORE_COMITE)
INSERT INTO core.evaluation_assignment (ipr_id, evaluator_type_id, evaluator_name, assigned_at, completed_at, result_id, numeric_score, rank_position, rank_total, observations, created_by_id) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='evaluator_type' AND code='MDSF'), 'Evaluador MDSF Central — Div. Inversiones', CURRENT_TIMESTAMP - INTERVAL '200 days', CURRENT_TIMESTAMP - INTERVAL '180 days', (SELECT id FROM ref.category WHERE scheme='evaluation_result' AND code='RS'), 88.50, 3, 12, 'Proyecto estratégico para conectividad urbana. Diseño cumple normativa MOP. Recomendado para financiamiento.', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='evaluator_type' AND code='GORE_COMITE'), 'Comité Evaluador Regional GORE', CURRENT_TIMESTAMP - INTERVAL '190 days', CURRENT_TIMESTAMP - INTERVAL '175 days', (SELECT id FROM ref.category WHERE scheme='evaluation_result' AND code='RS'), 91.00, 1, 8, 'Prioridad regional alta. Complementa Plan Regulador vigente. Aprobado por unanimidad.', (SELECT id FROM core."user" WHERE email='jefe.dipir@goreos.cl'))
ON CONFLICT DO NOTHING;

-- H2: SNI-008 — 2 evaluaciones (cerrado, scores altos)
INSERT INTO core.evaluation_assignment (ipr_id, evaluator_type_id, evaluator_name, assigned_at, completed_at, result_id, numeric_score, rank_position, rank_total, observations, created_by_id) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='evaluator_type' AND code='MDSF'), 'Evaluador MDSF Regional Ñuble', CURRENT_TIMESTAMP - INTERVAL '320 days', CURRENT_TIMESTAMP - INTERVAL '300 days', (SELECT id FROM ref.category WHERE scheme='evaluation_result' AND code='RS'), 82.30, 5, 15, 'Proyecto deportivo con alto impacto comunal. Costos dentro de rango FRIL.', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='evaluator_type' AND code='GORE_DIDESO'), 'Evaluación social DIDESO', CURRENT_TIMESTAMP - INTERVAL '310 days', CURRENT_TIMESTAMP - INTERVAL '295 days', (SELECT id FROM ref.category WHERE scheme='evaluation_result' AND code='RS'), 85.00, NULL, NULL, 'Impacto social positivo en población joven de Yungay.', (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'))
ON CONFLICT DO NOTHING;

-- H6: EXT-003 — evaluación reciente + CORE approval
INSERT INTO core.evaluation_assignment (ipr_id, evaluator_type_id, evaluator_name, assigned_at, completed_at, result_id, numeric_score, rank_position, rank_total, convocatoria_code, observations, created_by_id) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM ref.category WHERE scheme='evaluator_type' AND code='MDSF'), 'Evaluador MDSF Central — Proyectos Urbanos', CURRENT_TIMESTAMP - INTERVAL '90 days', CURRENT_TIMESTAMP - INTERVAL '70 days', (SELECT id FROM ref.category WHERE scheme='evaluation_result' AND code='RS'), 93.20, 1, 6, 'CONV-2026-001', 'Proyecto emblemático. Máximo puntaje en dimensión ambiental. Requiere aprobación CORE (>7K UTM).', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT DO NOTHING;

-- Genéricos: resto de IPRs F2+
DO $$
DECLARE
    v_ipr RECORD; v_eval_type UUID; v_result_rs UUID; v_result_fi UUID; v_result_ot UUID;
    v_heroes TEXT[] := ARRAY['DEMO-R-SNI-007','DEMO-R-SNI-008','DEMO-R-EXT-003'];
    v_idx INTEGER := 0;
BEGIN
    SELECT id INTO v_eval_type FROM ref.category WHERE scheme='evaluator_type' AND code='MDSF';
    SELECT id INTO v_result_rs FROM ref.category WHERE scheme='evaluation_result' AND code='RS';
    SELECT id INTO v_result_fi FROM ref.category WHERE scheme='evaluation_result' AND code='FI';
    SELECT id INTO v_result_ot FROM ref.category WHERE scheme='evaluation_result' AND code='OT';

    FOR v_ipr IN
        SELECT i.id, i.codigo_bip, c.code as status_code FROM core.ipr i
        JOIN ref.category c ON i.status_id = c.id
        WHERE i.codigo_bip LIKE 'DEMO-R-%' AND i.codigo_bip != ALL(v_heroes)
          AND c.code NOT IN ('INGRESADO','EN_REVISION','PRE_ADMISIBLE','ADMISIBLE','INADMISIBLE')
        ORDER BY i.codigo_bip
    LOOP
        v_idx := v_idx + 1;
        INSERT INTO core.evaluation_assignment (ipr_id, evaluator_type_id, evaluator_name, assigned_at, result_id, numeric_score, observations, created_by_id)
        VALUES (v_ipr.id, v_eval_type,
            CASE WHEN v_idx % 3 = 0 THEN 'Evaluador MDSF Regional' ELSE 'Evaluador MDSF Central' END,
            CURRENT_TIMESTAMP - INTERVAL '30 days',
            CASE WHEN v_ipr.status_code = 'FI' THEN v_result_fi
                 WHEN v_ipr.status_code IN ('OT','AT') THEN v_result_ot
                 ELSE v_result_rs END,
            CASE WHEN v_idx % 2 = 0 THEN 85.50 ELSE 72.30 END,
            'Evaluación técnica — ' || v_ipr.codigo_bip,
            (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
        ON CONFLICT DO NOTHING;
    END LOOP;
END $$;

-- =============================================================================
-- 3.5 PROGRESS_REPORT — héroes con series temporales, resto genérico
-- =============================================================================
-- H1: SNI-007 — 4 informes mostrando progresión de obra
INSERT INTO core.progress_report (ipr_id, report_number, report_date, physical_progress, financial_progress, description, issues_detected, reported_by_id) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), 1, CURRENT_DATE - INTERVAL '90 days', 12.0, 8.5, 'Inicio de obras. Trazado completado, excavaciones en curso. Equipo de 15 personas en terreno. Sin problemas.', NULL, (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), 2, CURRENT_DATE - INTERVAL '60 days', 28.0, 22.0, 'Avance en fundaciones y subbase. Se detectó problema de drenaje en sector norte (PRB-001). ITO realizó 3 visitas.', 'Falla en sistema de drenaje sector norte — requiere rediseño parcial. Retraso estimado 15 días.', (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), 3, CURRENT_DATE - INTERVAL '30 days', 42.0, 35.0, 'Rediseño drenaje aprobado por SERVIU. Carpeta asfáltica iniciada en tramo sur. 2 estados de pago procesados.', 'Retraso acumulado de 10 días por rediseño. Plan de recuperación activo.', (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), 4, CURRENT_DATE - INTERVAL '5 days', 48.0, 40.0, 'Carpeta asfáltica 60% completada. Solicitud de modificación presupuestaria ingresada (MOD-001). Próxima visita ITO programada.', 'Incremento de costos materiales 12% — modificación en trámite.', (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT DO NOTHING;

-- H2: SNI-008 — 5 informes (ciclo completo cerrado)
INSERT INTO core.progress_report (ipr_id, report_number, report_date, physical_progress, financial_progress, description, reported_by_id) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), 1, CURRENT_DATE - INTERVAL '200 days', 15.0, 10.0, 'Radier completado. Estructura metálica en proceso de montaje. Sin novedades.', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), 2, CURRENT_DATE - INTERVAL '160 days', 35.0, 28.0, 'Estructura completa. Techado en instalación. Visita ITO satisfactoria.', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), 3, CURRENT_DATE - INTERVAL '120 days', 58.0, 50.0, 'Cerramiento perimetral completado. Instalaciones eléctricas al 80%. Se detectó defecto menor en soldadura (resuelto in situ).', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), 4, CURRENT_DATE - INTERVAL '70 days', 85.0, 78.0, 'Terminaciones interiores y exteriores al 90%. Pintura y señalética. Programación de recepción provisoria con municipio.', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), 5, CURRENT_DATE - INTERVAL '35 days', 100.0, 98.5, 'Obra 100% completada. Recepción definitiva firmada. Informe final entregado al CORE. Cierre administrativo en proceso.', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'))
ON CONFLICT DO NOTHING;

-- H3: FRIL-005 — 2 informes
INSERT INTO core.progress_report (ipr_id, report_number, report_date, physical_progress, financial_progress, description, issues_detected, reported_by_id) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), 1, CURRENT_DATE - INTERVAL '55 days', 20.0, 15.0, 'Desmontaje estructura antigua completado. Nuevo trazado de pilares marcado. Equipo de 8 personas.', NULL, (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), 2, CURRENT_DATE - INTERVAL '20 days', 40.0, 32.0, 'Pilares instalados. Estructura metálica al 60%. Lluvia retrasó 5 días. Solicitud extensión plazo ingresada (MOD-002).', 'Alza 12% en costo materiales — evaluar modificación presupuestaria.', (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT DO NOTHING;

-- H4: TRF-003 — 2 informes
INSERT INTO core.progress_report (ipr_id, report_number, report_date, physical_progress, financial_progress, description, issues_detected, reported_by_id) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), 1, CURRENT_DATE - INTERVAL '40 days', 25.0, 20.0, 'Capacitación operadores turísticos Fase 1 completada (8 comunas). Señalética en proceso de fabricación.', 'SERNATUR no ha designado contraparte técnica regional (PRB-004).', (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), 2, CURRENT_DATE - INTERVAL '10 days', 38.0, 30.0, 'Señalética 30% instalada en rutas principales. Actividades de terreno retrasadas por falta de contraparte SERNATUR.', 'Problema de coordinación persiste — escalamiento N2 activado.', (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT DO NOTHING;

-- Phase-aware progress reports: F4 early(1-2), F4 mid(2-3), F4 late/F5(3-4)
DO $$
DECLARE
    v_ipr RECORD; v_idx INTEGER := 0;
    v_heroes TEXT[] := ARRAY['DEMO-R-SNI-007','DEMO-R-SNI-008','DEMO-R-FRIL-005','DEMO-R-TRF-003'];
    v_reporter UUID;
    v_n_reports INTEGER;
    v_r INTEGER;
    v_phys NUMERIC; v_fin NUMERIC;
BEGIN
    SELECT id INTO v_reporter FROM core."user" WHERE email='jefe.dit@goreos.cl';
    FOR v_ipr IN
        SELECT i.id, i.assignee_id, s.code as status_code, p.code as phase_code
        FROM core.ipr i
        JOIN ref.category s ON i.status_id = s.id
        JOIN ref.category p ON i.mcd_phase_id = p.id
        WHERE i.codigo_bip LIKE 'DEMO-R-%' AND i.codigo_bip != ALL(v_heroes)
          AND s.code IN ('EN_EJECUCION','EN_OBRA','RECEPCION_PROVISORIA','RECEPCION_DEFINITIVA','SUSPENDIDO',
                         'EN_RENDICION','RENDICION_APROBADA','EN_CIERRE_ADMINISTRATIVO','CERRADO','FORMALIZADO',
                         'CONTRATO_FIRMADO','ADJUDICADO')
        ORDER BY i.codigo_bip
    LOOP
        v_idx := v_idx + 1;

        -- Number of reports based on how far into execution
        v_n_reports := CASE
            WHEN v_ipr.status_code IN ('FORMALIZADO','ADJUDICADO','CONTRATO_FIRMADO') THEN 1
            WHEN v_ipr.status_code IN ('EN_EJECUCION','EN_OBRA','SUSPENDIDO') THEN 2 + (v_idx % 2)  -- 2 or 3
            WHEN v_ipr.status_code IN ('RECEPCION_PROVISORIA','RECEPCION_DEFINITIVA') THEN 3
            WHEN v_ipr.phase_code = 'F5' THEN 3 + (v_idx % 2) -- 3 or 4
            ELSE 2
        END;

        FOR v_r IN 1..v_n_reports LOOP
            v_phys := LEAST((v_r::numeric / v_n_reports) * CASE
                WHEN v_ipr.phase_code = 'F5' THEN 100
                WHEN v_ipr.status_code IN ('RECEPCION_PROVISORIA','RECEPCION_DEFINITIVA') THEN 95
                WHEN v_ipr.status_code IN ('EN_OBRA','EN_EJECUCION') THEN 60
                ELSE 30
            END, 100.0);
            v_fin := v_phys * 0.85;

            INSERT INTO core.progress_report (ipr_id, report_number, report_date, physical_progress, financial_progress, description, reported_by_id)
            VALUES (v_ipr.id, v_r,
                    CURRENT_DATE - ((v_n_reports - v_r + 1) * 25 * INTERVAL '1 day'),
                    ROUND(v_phys, 1), ROUND(v_fin, 1),
                    'Informe de avance N°' || v_r || ' — ' ||
                    CASE v_r
                        WHEN 1 THEN 'Inicio de actividades y movilización de recursos'
                        WHEN 2 THEN 'Avance intermedio, sin observaciones mayores'
                        WHEN 3 THEN 'Avance significativo, hitos contractuales en cumplimiento'
                        ELSE 'Informe final de avance — ejecución en fase de cierre'
                    END,
                    COALESCE(v_ipr.assignee_id, v_reporter))
            ON CONFLICT DO NOTHING;
        END LOOP;
    END LOOP;
END $$;


-- =============================================================================
-- TIER 3B: CONVENIOS Y CDPs PARA IPRs NUEVOS (F3+)
-- =============================================================================
-- Genera un convenio VIGENTE + 2-3 cuotas + 1 CDP para cada IPR F3+ que no sea héroe original.
-- Esto conecta la cadena: IPR ← CDP + Convenio ← Cuotas ← Rendiciones.

DO $$
DECLARE
    v_ipr RECORD;
    v_agr_num INTEGER := 200; -- Start at 200 to avoid collision with DEMO-R-AGR-001..018
    v_cdp_num INTEGER := 100; -- Start at 100 to avoid collision with DEMO-R-CDP-001..020
    v_vigente UUID; v_borrador UUID; v_mandato UUID; v_transferencia UUID;
    v_pendiente UUID; v_pagado UUID; v_cdp_vigente UUID;
    v_munis TEXT[] := ARRAY['DEMO-R-MUNI-CHILLAN','DEMO-R-MUNI-SANCARLOS','DEMO-R-MUNI-QUIRIHUE','DEMO-R-MUNI-COIHUECO','DEMO-R-MUNI-BULNES','DEMO-R-MUNI-PINTO','DEMO-R-MUNI-COELEMU'];
    v_servs TEXT[] := ARRAY['DEMO-R-SERVIU-NUBLE','DEMO-R-MOP-NUBLE','DEMO-R-SERNATUR-NUBLE','DEMO-R-UBB','DEMO-R-CONST-ITATA','DEMO-R-ING-NUBLE','DEMO-R-FUND-NUBLE'];
    v_agr_id UUID;
    v_bp_id UUID;
    v_cuota NUMERIC;
    v_idx INTEGER := 0;
BEGIN
    SELECT id INTO v_vigente FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE';
    SELECT id INTO v_borrador FROM ref.category WHERE scheme='agreement_state' AND code='BORRADOR';
    SELECT id INTO v_mandato FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO';
    SELECT id INTO v_transferencia FROM ref.category WHERE scheme='agreement_type' AND code='TRANSFERENCIA';
    SELECT id INTO v_pendiente FROM ref.category WHERE scheme='payment_status' AND code='PENDIENTE';
    SELECT id INTO v_pagado FROM ref.category WHERE scheme='payment_status' AND code='PAGADO';
    SELECT id INTO v_cdp_vigente FROM ref.category WHERE scheme='budget_commitment_status' AND code='VIGENTE';

    -- Get a budget program to link CDPs to (use ciclo2 BP that already exists, or any)
    SELECT id INTO v_bp_id FROM core.budget_program WHERE code LIKE 'DEMO-BP-%' ORDER BY code LIMIT 1;
    IF v_bp_id IS NULL THEN
        SELECT id INTO v_bp_id FROM core.budget_program WHERE deleted_at IS NULL ORDER BY code LIMIT 1;
    END IF;

    FOR v_ipr IN
        SELECT i.id, i.codigo_bip, i.sponsor_division_id, p.code as phase_code, i.metadata
        FROM core.ipr i
        JOIN ref.category p ON i.mcd_phase_id = p.id
        WHERE i.codigo_bip LIKE 'DEMO-R-%-1%' -- Only the new batch (101+)
          AND p.code IN ('F3','F4','F5')
        ORDER BY i.codigo_bip
    LOOP
        v_idx := v_idx + 1;
        v_agr_num := v_agr_num + 1;
        v_cdp_num := v_cdp_num + 1;

        -- === CONVENIO ===
        INSERT INTO core.agreement (
            agreement_number, agreement_type_id, state_id, ipr_id, giver_id, receiver_id,
            total_amount, signed_at, valid_from, valid_to
        ) VALUES (
            'DEMO-R-AGR-' || LPAD(v_agr_num::text, 3, '0'),
            CASE WHEN v_idx % 2 = 0 THEN v_mandato ELSE v_transferencia END,
            CASE WHEN v_ipr.phase_code = 'F3' THEN v_borrador ELSE v_vigente END,
            v_ipr.id,
            v_ipr.sponsor_division_id,
            (SELECT id FROM core.organization WHERE code = v_servs[1 + (v_idx % 7)]),
            COALESCE((v_ipr.metadata->>'monto_total')::numeric, 500000000),
            CASE WHEN v_ipr.phase_code != 'F3' THEN CURRENT_TIMESTAMP - (v_idx * 10 * INTERVAL '1 day') ELSE NULL END,
            CASE WHEN v_ipr.phase_code != 'F3' THEN CURRENT_TIMESTAMP - (v_idx * 10 * INTERVAL '1 day') ELSE NULL END,
            CASE WHEN v_ipr.phase_code != 'F3' THEN CURRENT_TIMESTAMP + INTERVAL '365 days' ELSE NULL END
        ) ON CONFLICT DO NOTHING
        RETURNING id INTO v_agr_id;

        -- === CUOTAS (3 per convenio) ===
        IF v_agr_id IS NOT NULL THEN
            v_cuota := ROUND(COALESCE((v_ipr.metadata->>'monto_total')::numeric, 500000000) / 3, 2);

            -- Cuota 1: pagada si F4+
            INSERT INTO core.agreement_installment (agreement_id, installment_number, amount, due_date, payment_status_id, paid_at, paid_amount)
            VALUES (v_agr_id, 1, v_cuota,
                    CURRENT_DATE - INTERVAL '60 days' + (v_idx * INTERVAL '3 days'),
                    CASE WHEN v_ipr.phase_code IN ('F4','F5') THEN v_pagado ELSE v_pendiente END,
                    CASE WHEN v_ipr.phase_code IN ('F4','F5') THEN CURRENT_TIMESTAMP - INTERVAL '55 days' ELSE NULL END,
                    CASE WHEN v_ipr.phase_code IN ('F4','F5') THEN v_cuota ELSE NULL END)
            ON CONFLICT DO NOTHING;

            -- Cuota 2: pendiente
            INSERT INTO core.agreement_installment (agreement_id, installment_number, amount, due_date, payment_status_id)
            VALUES (v_agr_id, 2, v_cuota, CURRENT_DATE + INTERVAL '30 days' + (v_idx * INTERVAL '5 days'), v_pendiente)
            ON CONFLICT DO NOTHING;

            -- Cuota 3: pendiente
            INSERT INTO core.agreement_installment (agreement_id, installment_number, amount, due_date, payment_status_id)
            VALUES (v_agr_id, 3, v_cuota, CURRENT_DATE + INTERVAL '90 days' + (v_idx * INTERVAL '5 days'), v_pendiente)
            ON CONFLICT DO NOTHING;
        END IF;

        -- === CDP ===
        IF v_bp_id IS NOT NULL THEN
            INSERT INTO core.budget_commitment (
                commitment_number, budget_program_id, ipr_id, amount, issued_at, expires_at, status_id
            ) VALUES (
                'DEMO-R-CDP-' || LPAD(v_cdp_num::text, 3, '0'),
                v_bp_id, v_ipr.id,
                COALESCE((v_ipr.metadata->>'monto_total')::numeric, 500000000),
                CURRENT_DATE - (v_idx * 5 * INTERVAL '1 day'),
                '2026-12-31', v_cdp_vigente
            ) ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;

    RAISE NOTICE 'Generated % agreements + CDPs for new F3+ IPRs', v_idx;
END $$;


-- =============================================================================
-- TIER 4: CADENA FINANCIERA (~110 registros originales)
-- =============================================================================

-- 4.1 BUDGET_PROGRAMS (12) — ya existen 6 en ciclo2, estos son adicionales
INSERT INTO core.budget_program (code, name, fiscal_year, program_type_id, subtitle_id, item_id, allocation_id, owner_division_id, initial_amount, current_amount, committed_amount, accrued_amount, paid_amount, fndr_amount) VALUES
('DEMO-R-BP-001', 'Inversión FNDR DIPLADE 2026', 2026,
 (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_INVERSION'),
 (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='31'),
 (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='INV_REAL'),
 (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='FNDR_ESTUDIO'),
 (SELECT id FROM core.organization WHERE code='DIPLADE'),
 1200000000, 1100000000, 700000000, 500000000, 440000000, 1100000000),
('DEMO-R-BP-002', 'Programa Social DIDESO 2026', 2026,
 (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_PROGRAMA'),
 (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='24'),
 (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='TRANSFERENCIAS_CTES'),
 (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='FNDR_PROGRAMA_SOCIAL'),
 (SELECT id FROM core.organization WHERE code='DIDESO'),
 900000000, 850000000, 600000000, 400000000, 340000000, 850000000),
('DEMO-R-BP-003', 'Inversión FNDR DIT 2026', 2026,
 (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_INVERSION'),
 (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='31'),
 (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='INV_REAL'),
 (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='FNDR_INFRAESTRUCTURA'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 4500000000, 4200000000, 3000000000, 2100000000, 2520000000, 4200000000),
('DEMO-R-BP-004', 'Fomento Productivo DIFOI 2026', 2026,
 (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_TRANSFERENCIA'),
 (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='33'),
 (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='TRANSF_CAPITAL'),
 (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='FNDR_8PCT'),
 (SELECT id FROM core.organization WHERE code='DIFOI'),
 700000000, 680000000, 450000000, 300000000, 272000000, 680000000),
('DEMO-R-BP-005', 'Sectorial MOP DIT 2026', 2026,
 (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_INVERSION'),
 (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='31'),
 (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='INV_REAL'),
 (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='SECT_MOP'),
 (SELECT id FROM core.organization WHERE code='DIT'),
 2000000000, 1900000000, 1400000000, 1000000000, 950000000, 0),
('DEMO-R-BP-006', 'Innovación FIC DIFOI 2026', 2026,
 (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_TRANSFERENCIA'),
 (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='33'),
 (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='TRANSF_CAPITAL'),
 (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='FIC_INNOVACION'),
 (SELECT id FROM core.organization WHERE code='DIFOI'),
 500000000, 480000000, 350000000, 200000000, 192000000, 0)
ON CONFLICT DO NOTHING;

-- 4.2 BUDGET_CARRYOVER (4)
INSERT INTO core.budget_carryover (budget_program_id, fiscal_year, amount)
VALUES
((SELECT id FROM core.budget_program WHERE code='DEMO-R-BP-003'), 2025, 380000000),
((SELECT id FROM core.budget_program WHERE code='DEMO-R-BP-005'), 2025, 520000000),
((SELECT id FROM core.budget_program WHERE code='DEMO-R-BP-001'), 2025, 150000000),
((SELECT id FROM core.budget_program WHERE code='DEMO-R-BP-004'), 2025, 90000000)
ON CONFLICT DO NOTHING;

-- 4.3 BUDGET_COMMITMENT / CDPs (20)
DO $$
DECLARE
    v_iprs TEXT[] := ARRAY['DEMO-R-SNI-006','DEMO-R-SNI-007','DEMO-R-FRIL-004','DEMO-R-FRIL-005','DEMO-R-SUBV8-003','DEMO-R-SUBV8-004','DEMO-R-TRF-002','DEMO-R-TRF-003','DEMO-R-G06-003','DEMO-R-FRPD-003','DEMO-R-EXT-001','DEMO-R-EXT-002','DEMO-R-EXT-003','DEMO-R-EXT-004','DEMO-R-C33-003','DEMO-R-C33-004','DEMO-R-SNI-005','DEMO-R-G06-002','DEMO-R-SNI-008','DEMO-R-FRIL-006'];
    v_bps TEXT[] := ARRAY['DEMO-R-BP-003','DEMO-R-BP-003','DEMO-R-BP-003','DEMO-R-BP-004','DEMO-R-BP-002','DEMO-R-BP-002','DEMO-R-BP-006','DEMO-R-BP-004','DEMO-R-BP-001','DEMO-R-BP-003','DEMO-R-BP-003','DEMO-R-BP-003','DEMO-R-BP-003','DEMO-R-BP-005','DEMO-R-BP-003','DEMO-R-BP-003','DEMO-R-BP-003','DEMO-R-BP-001','DEMO-R-BP-003','DEMO-R-BP-003'];
    v_amounts NUMERIC[] := ARRAY[160000000,580000000,45000000,110000000,95000000,75000000,450000000,280000000,150000000,380000000,720000000,95000000,2800000000,1400000000,350000000,290000000,320000000,520000000,890000000,78000000];
    v_statuses TEXT[] := ARRAY['VIGENTE','VIGENTE','VIGENTE','VIGENTE','VIGENTE','EJECUTADO','VIGENTE','VIGENTE','VIGENTE','VIGENTE','VIGENTE','EJECUTADO','VIGENTE','VIGENTE','EJECUTADO','EJECUTADO','VIGENTE','VIGENTE','EJECUTADO','VIGENTE'];
    v_i INTEGER;
BEGIN
    FOR v_i IN 1..20 LOOP
        INSERT INTO core.budget_commitment (
            commitment_number, budget_program_id, ipr_id, amount, issued_at, expires_at, status_id
        ) VALUES (
            'DEMO-R-CDP-' || LPAD(v_i::text, 3, '0'),
            (SELECT id FROM core.budget_program WHERE code = v_bps[v_i] LIMIT 1),
            (SELECT id FROM core.ipr WHERE codigo_bip = v_iprs[v_i] LIMIT 1),
            v_amounts[v_i],
            CURRENT_DATE - INTERVAL '60 days' + (v_i * INTERVAL '2 days'),
            '2026-12-31',
            (SELECT id FROM ref.category WHERE scheme='budget_commitment_status' AND code=v_statuses[v_i])
        ) ON CONFLICT DO NOTHING;
    END LOOP;
END $$;

-- 4.4 AGREEMENTS (18) — cubriendo los 10 estados conocidos
INSERT INTO core.agreement (agreement_number, agreement_type_id, state_id, ipr_id, giver_id, receiver_id, total_amount, signed_at, valid_from, valid_to) VALUES
('DEMO-R-AGR-001', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='BORRADOR'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-004'), (SELECT id FROM core.organization WHERE code='DIPIR'), (SELECT id FROM core.organization WHERE code='DEMO-R-SERVIU-NUBLE'), 950000000, NULL, NULL, NULL),
('DEMO-R-AGR-002', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='TRANSFERENCIA'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='EN_NEGOCIACION'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-002'), (SELECT id FROM core.organization WHERE code='DIFOI'), (SELECT id FROM core.organization WHERE code='DEMO-R-FUND-NUBLE'), 180000000, NULL, NULL, NULL),
('DEMO-R-AGR-003', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='EN_REVISION_JURIDICA'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-006'), (SELECT id FROM core.organization WHERE code='DIT'), (SELECT id FROM core.organization WHERE code='DEMO-R-MOP-NUBLE'), 1600000000, NULL, NULL, NULL),
('DEMO-R-AGR-004', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='COLABORACION'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='FIRMADO_GORE'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-002'), (SELECT id FROM core.organization WHERE code='DIFOI'), (SELECT id FROM core.organization WHERE code='DEMO-R-UBB'), 450000000, CURRENT_TIMESTAMP - INTERVAL '20 days', CURRENT_TIMESTAMP - INTERVAL '20 days', NULL),
('DEMO-R-AGR-005', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='FIRMADO_CONTRAPARTE'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM core.organization WHERE code='DIT'), (SELECT id FROM core.organization WHERE code='DEMO-R-CONST-ITATA'), 2800000000, CURRENT_TIMESTAMP - INTERVAL '15 days', CURRENT_TIMESTAMP - INTERVAL '15 days', NULL),
('DEMO-R-AGR-006', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM core.organization WHERE code='DIT'), (SELECT id FROM core.organization WHERE code='DEMO-R-SERVIU-NUBLE'), 5800000000, CURRENT_TIMESTAMP - INTERVAL '120 days', CURRENT_TIMESTAMP - INTERVAL '120 days', CURRENT_TIMESTAMP + INTERVAL '365 days'),
('DEMO-R-AGR-007', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='TRANSFERENCIA'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), (SELECT id FROM core.organization WHERE code='DIFOI'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-SANCARLOS'), 110000000, CURRENT_TIMESTAMP - INTERVAL '90 days', CURRENT_TIMESTAMP - INTERVAL '90 days', CURRENT_TIMESTAMP + INTERVAL '180 days'),
('DEMO-R-AGR-008', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), (SELECT id FROM core.organization WHERE code='DIFOI'), (SELECT id FROM core.organization WHERE code='DEMO-R-SERNATUR-NUBLE'), 280000000, CURRENT_TIMESTAMP - INTERVAL '85 days', CURRENT_TIMESTAMP - INTERVAL '85 days', CURRENT_TIMESTAMP + INTERVAL '200 days'),
('DEMO-R-AGR-009', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='COLABORACION'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-004'), (SELECT id FROM core.organization WHERE code='DIDESO'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-COIHUECO'), 75000000, CURRENT_TIMESTAMP - INTERVAL '100 days', CURRENT_TIMESTAMP - INTERVAL '100 days', CURRENT_TIMESTAMP + INTERVAL '150 days'),
('DEMO-R-AGR-010', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='TRANSFERENCIA'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-G06-003'), (SELECT id FROM core.organization WHERE code='DIPLADE'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-CHILLAN'), 150000000, CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP + INTERVAL '300 days'),
-- Próximos a vencer (≤90d)
('DEMO-R-AGR-011', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-C33-003'), (SELECT id FROM core.organization WHERE code='DIT'), (SELECT id FROM core.organization WHERE code='DEMO-R-MOP-NUBLE'), 350000000, CURRENT_TIMESTAMP - INTERVAL '330 days', CURRENT_TIMESTAMP - INTERVAL '330 days', CURRENT_TIMESTAMP + INTERVAL '35 days'),
('DEMO-R-AGR-012', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='EN_MODIFICACION'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-001'), (SELECT id FROM core.organization WHERE code='DIT'), (SELECT id FROM core.organization WHERE code='DEMO-R-CONST-ITATA'), 720000000, CURRENT_TIMESTAMP - INTERVAL '200 days', CURRENT_TIMESTAMP - INTERVAL '200 days', CURRENT_TIMESTAMP + INTERVAL '60 days'),
-- Terminados
('DEMO-R-AGR-013', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VENCIDO'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-G06-004'), (SELECT id FROM core.organization WHERE code='DIPLADE'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-QUIRIHUE'), 210000000, '2024-06-01', '2024-06-01', '2025-12-31'),
('DEMO-R-AGR-014', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='TRANSFERENCIA'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='TERMINADO'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM core.organization WHERE code='DIPIR'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-BULNES'), 890000000, '2024-03-01', '2024-03-01', '2025-09-30'),
('DEMO-R-AGR-015', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='COLABORACION'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='RESCILIADO'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-004'), (SELECT id FROM core.organization WHERE code='DIFOI'), (SELECT id FROM core.organization WHERE code='DEMO-R-UADVENTISTA'), 190000000, '2024-09-01', '2024-09-01', '2026-08-31'),
-- Extras para volumen
('DEMO-R-AGR-016', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='EJECUCION'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-004'), (SELECT id FROM core.organization WHERE code='DIT'), (SELECT id FROM core.organization WHERE code='DEMO-R-SERVIU-NUBLE'), 1400000000, CURRENT_TIMESTAMP - INTERVAL '6 days', CURRENT_TIMESTAMP - INTERVAL '6 days', CURRENT_TIMESTAMP + INTERVAL '400 days'),
('DEMO-R-AGR-017', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='PROGRAMACION'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE'), (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRPD-002'), (SELECT id FROM core.organization WHERE code='DIDESO'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-PINTO'), 480000000, CURRENT_TIMESTAMP - INTERVAL '58 days', CURRENT_TIMESTAMP - INTERVAL '58 days', CURRENT_TIMESTAMP + INTERVAL '250 days'),
('DEMO-R-AGR-018', (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MARCO'), (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE'), NULL, (SELECT id FROM core.organization WHERE code='GORE-NUBLE'), (SELECT id FROM core.organization WHERE code='DEMO-R-UBB'), 1500000000, CURRENT_TIMESTAMP - INTERVAL '180 days', CURRENT_TIMESTAMP - INTERVAL '180 days', CURRENT_TIMESTAMP + INTERVAL '540 days')
ON CONFLICT DO NOTHING;

-- 4.5 AGREEMENT_INSTALLMENT (~40) — 2-3 cuotas por convenio vigente
DO $$
DECLARE
    v_agr RECORD;
    v_pendiente UUID;
    v_pagado UUID;
    v_en_proceso UUID;
    v_cuota_monto NUMERIC;
    v_idx INTEGER := 0;
BEGIN
    SELECT id INTO v_pendiente FROM ref.category WHERE scheme='payment_status' AND code='PENDIENTE';
    SELECT id INTO v_pagado FROM ref.category WHERE scheme='payment_status' AND code='PAGADO';
    SELECT id INTO v_en_proceso FROM ref.category WHERE scheme='payment_status' AND code='EN_PROCESO';

    FOR v_agr IN SELECT id, total_amount, agreement_number FROM core.agreement WHERE agreement_number LIKE 'DEMO-R-AGR-%' AND total_amount IS NOT NULL ORDER BY agreement_number LOOP
        v_idx := v_idx + 1;
        v_cuota_monto := ROUND(v_agr.total_amount / 3, 2);

        -- Cuota 1: pagada
        INSERT INTO core.agreement_installment (agreement_id, installment_number, amount, due_date, payment_status_id, paid_at, paid_amount)
        VALUES (v_agr.id, 1, v_cuota_monto, CURRENT_DATE - INTERVAL '60 days' + (v_idx * INTERVAL '5 days'), v_pagado, CURRENT_TIMESTAMP - INTERVAL '65 days', v_cuota_monto)
        ON CONFLICT DO NOTHING;

        -- Cuota 2: en proceso o pendiente
        INSERT INTO core.agreement_installment (agreement_id, installment_number, amount, due_date, payment_status_id)
        VALUES (v_agr.id, 2, v_cuota_monto, CURRENT_DATE + (v_idx * INTERVAL '10 days'),
                CASE WHEN v_idx % 3 = 0 THEN v_en_proceso ELSE v_pendiente END)
        ON CONFLICT DO NOTHING;

        -- Cuota 3: pendiente
        INSERT INTO core.agreement_installment (agreement_id, installment_number, amount, due_date, payment_status_id)
        VALUES (v_agr.id, 3, v_agr.total_amount - (2 * v_cuota_monto), CURRENT_DATE + INTERVAL '90 days' + (v_idx * INTERVAL '10 days'), v_pendiente)
        ON CONFLICT DO NOTHING;
    END LOOP;
END $$;

-- 4.6 RENDITIONS (15) — cubriendo estados SISREC
INSERT INTO core.rendition (agreement_id, renderer_id, state_id, period_start, period_end, submitted_at, created_by_id) VALUES
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-006'), (SELECT id FROM core.organization WHERE code='DEMO-R-SERVIU-NUBLE'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='PENDIENTE'), '2026-01-01', '2026-03-31', NULL, (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-006'), (SELECT id FROM core.organization WHERE code='DEMO-R-SERVIU-NUBLE'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='EN_REVISION_RTF'), '2025-10-01', '2025-12-31', CURRENT_TIMESTAMP - INTERVAL '15 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-007'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-SANCARLOS'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='VISADA_RTF'), '2025-10-01', '2025-12-31', CURRENT_TIMESTAMP - INTERVAL '20 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-008'), (SELECT id FROM core.organization WHERE code='DEMO-R-SERNATUR-NUBLE'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='EN_REVISION_UCR'), '2025-07-01', '2025-09-30', CURRENT_TIMESTAMP - INTERVAL '30 days', (SELECT id FROM core."user" WHERE email='jefe.ucr@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-009'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-COIHUECO'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='OBSERVADA'), '2025-07-01', '2025-09-30', CURRENT_TIMESTAMP - INTERVAL '45 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-010'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-CHILLAN'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='APROBADA'), '2025-04-01', '2025-06-30', CURRENT_TIMESTAMP - INTERVAL '60 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-011'), (SELECT id FROM core.organization WHERE code='DEMO-R-MOP-NUBLE'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='RECHAZADA'), '2025-01-01', '2025-03-31', CURRENT_TIMESTAMP - INTERVAL '90 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-014'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-BULNES'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='APROBADA'), '2024-10-01', '2024-12-31', CURRENT_TIMESTAMP - INTERVAL '120 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-016'), (SELECT id FROM core.organization WHERE code='DEMO-R-SERVIU-NUBLE'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='PENDIENTE'), '2026-01-01', '2026-03-31', NULL, (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-017'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-PINTO'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='EN_REVISION'), '2025-10-01', '2025-12-31', CURRENT_TIMESTAMP - INTERVAL '10 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
-- Extras para volumen
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-006'), (SELECT id FROM core.organization WHERE code='DEMO-R-SERVIU-NUBLE'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='APROBADA'), '2025-07-01', '2025-09-30', CURRENT_TIMESTAMP - INTERVAL '80 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-007'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-SANCARLOS'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='APROBADA'), '2025-07-01', '2025-09-30', CURRENT_TIMESTAMP - INTERVAL '70 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-008'), (SELECT id FROM core.organization WHERE code='DEMO-R-SERNATUR-NUBLE'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='APROBADA'), '2025-04-01', '2025-06-30', CURRENT_TIMESTAMP - INTERVAL '100 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-009'), (SELECT id FROM core.organization WHERE code='DEMO-R-MUNI-COIHUECO'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='APROBADA'), '2025-04-01', '2025-06-30', CURRENT_TIMESTAMP - INTERVAL '90 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-018'), (SELECT id FROM core.organization WHERE code='DEMO-R-UBB'), (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='EN_REVISION_RTF'), '2025-10-01', '2025-12-31', CURRENT_TIMESTAMP - INTERVAL '12 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl'))
ON CONFLICT DO NOTHING;


-- =============================================================================
-- TIER 4C: COMPROMISOS Y PROBLEMAS PARA IPRs NUEVOS (F4+)
-- =============================================================================
-- 2 compromisos por IPR F4+, 1 problema por cada 3 IPRs F4+.

DO $$
DECLARE
    v_ipr RECORD;
    v_ct_id UUID;
    v_ct_visita UUID;
    v_pendiente UUID; v_en_progreso UUID; v_completado UUID;
    v_abierto UUID; v_en_gestion UUID;
    v_pt_tecnico UUID; v_pt_financiero UUID; v_pt_coordinacion UUID;
    v_com_num INTEGER := 100;
    v_prb_num INTEGER := 100;
    v_idx INTEGER := 0;
    v_descs_1 TEXT[] := ARRAY['Verificar estado de obras en terreno','Coordinar próxima visita ITO','Gestionar estado de pago mensual','Preparar informe trimestral para división','Validar cumplimiento hitos contractuales','Revisar documentación rendición parcial','Coordinar con municipio agenda de actividades','Gestionar permisos ambientales pendientes'];
    v_descs_2 TEXT[] := ARRAY['Completar registro fotográfico avance','Enviar nota técnica a evaluador','Preparar documentación para auditoría','Actualizar cronograma de ejecución','Coordinar capacitación equipo local','Gestionar ampliación de plazo','Revisar calidad de materiales recibidos','Tramitar certificado de avance parcial'];
BEGIN
    SELECT id INTO v_ct_id FROM ref.operational_commitment_type WHERE code = 'HITO_CONTRATO' LIMIT 1;
    SELECT id INTO v_ct_visita FROM ref.operational_commitment_type WHERE code = 'VISITA_TERRENO' LIMIT 1;
    SELECT id INTO v_pendiente FROM ref.category WHERE scheme='commitment_state' AND code='PENDIENTE';
    SELECT id INTO v_en_progreso FROM ref.category WHERE scheme='commitment_state' AND code='EN_PROGRESO';
    SELECT id INTO v_completado FROM ref.category WHERE scheme='commitment_state' AND code='COMPLETADO';
    SELECT id INTO v_abierto FROM ref.category WHERE scheme='problem_state' AND code='ABIERTO';
    SELECT id INTO v_en_gestion FROM ref.category WHERE scheme='problem_state' AND code='EN_GESTION';
    SELECT id INTO v_pt_tecnico FROM ref.category WHERE scheme='problem_type' AND code='TECNICO';
    SELECT id INTO v_pt_financiero FROM ref.category WHERE scheme='problem_type' AND code='FINANCIERO';
    SELECT id INTO v_pt_coordinacion FROM ref.category WHERE scheme='problem_type' AND code='COORDINACION';

    FOR v_ipr IN
        SELECT i.id, i.codigo_bip, i.assignee_id, i.sponsor_division_id, s.code as status_code
        FROM core.ipr i
        JOIN ref.category s ON i.status_id = s.id
        JOIN ref.category p ON i.mcd_phase_id = p.id
        WHERE i.codigo_bip LIKE 'DEMO-R-%-1%' -- New batch only
          AND p.code IN ('F4','F5')
        ORDER BY i.codigo_bip
    LOOP
        v_idx := v_idx + 1;
        v_com_num := v_com_num + 1;

        -- Compromiso 1: PENDIENTE o EN_PROGRESO
        INSERT INTO core.operational_commitment (
            code, ipr_id, commitment_type_id, description, responsible_id, division_id, due_date, state_id, created_by_id
        ) VALUES (
            'DEMO-R-COM-' || LPAD(v_com_num::text, 3, '0'),
            v_ipr.id, v_ct_id,
            v_descs_1[1 + (v_idx % 8)],
            v_ipr.assignee_id,
            v_ipr.sponsor_division_id,
            CURRENT_DATE + ((v_idx % 15) * INTERVAL '2 days'),
            CASE WHEN v_idx % 3 = 0 THEN v_en_progreso ELSE v_pendiente END,
            v_ipr.assignee_id
        ) ON CONFLICT (code) DO NOTHING;

        v_com_num := v_com_num + 1;

        -- Compromiso 2: EN_PROGRESO o COMPLETADO
        INSERT INTO core.operational_commitment (
            code, ipr_id, commitment_type_id, description, responsible_id, division_id, due_date, state_id,
            completed_at, created_by_id
        ) VALUES (
            'DEMO-R-COM-' || LPAD(v_com_num::text, 3, '0'),
            v_ipr.id, v_ct_visita,
            v_descs_2[1 + (v_idx % 8)],
            v_ipr.assignee_id,
            v_ipr.sponsor_division_id,
            CURRENT_DATE + ((v_idx % 10) * INTERVAL '3 days'),
            CASE WHEN v_idx % 4 = 0 THEN v_completado ELSE v_en_progreso END,
            CASE WHEN v_idx % 4 = 0 THEN CURRENT_TIMESTAMP - INTERVAL '5 days' ELSE NULL END,
            v_ipr.assignee_id
        ) ON CONFLICT (code) DO NOTHING;

        -- Problema: 1 cada 3 IPRs
        IF v_idx % 3 = 0 THEN
            v_prb_num := v_prb_num + 1;
            INSERT INTO core.ipr_problem (
                code, ipr_id, problem_type_id, description, state_id, detected_by_id, impact_description, created_by_id
            ) VALUES (
                'DEMO-R-PRB-' || LPAD(v_prb_num::text, 3, '0'),
                v_ipr.id,
                CASE v_idx % 3 WHEN 0 THEN v_pt_tecnico WHEN 1 THEN v_pt_financiero ELSE v_pt_coordinacion END,
                'Problema detectado en ejecución de ' || v_ipr.codigo_bip,
                CASE WHEN v_idx % 2 = 0 THEN v_abierto ELSE v_en_gestion END,
                v_ipr.assignee_id,
                'Impacto en plazo de ejecución',
                v_ipr.assignee_id
            ) ON CONFLICT (code) DO NOTHING;
        END IF;
    END LOOP;

    RAISE NOTICE 'Generated % commitments + problems for new F4+ IPRs', v_com_num - 100;
END $$;


-- =============================================================================
-- TIER 5: NORMATIVO + OPERACIONAL (~75 registros originales)
-- =============================================================================

-- 5.1 ADMINISTRATIVE_ACT (18) — cubriendo los 8 estados del FSM de 7 pasos
-- signer_id FK→meta.role (NOT core.person)
INSERT INTO core.administrative_act (act_number, act_type_id, subject, issuer_id, issued_at, state_id, requires_cgr) VALUES
('DEMO-R-RES-001', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='RESOLUCION'), 'Aprueba convenio SERVIU para Pavimentación Acceso Norte', (SELECT id FROM core.organization WHERE code='DIT'), CURRENT_TIMESTAMP - INTERVAL '5 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='BORRADOR'), false),
('DEMO-R-RES-002', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='RESOLUCION'), 'Aprueba bases licitación Parque Urbano Ribera Chillán', (SELECT id FROM core.organization WHERE code='DIT'), CURRENT_TIMESTAMP - INTERVAL '10 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='EN_REVISION'), false),
('DEMO-R-RES-003', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='RESOLUCION'), 'Autoriza transferencia programa turismo Punilla', (SELECT id FROM core.organization WHERE code='DIFOI'), CURRENT_TIMESTAMP - INTERVAL '15 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='VISADO'), false),
('DEMO-R-DEC-001', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='DECRETO'), 'Decreto aprobación CDP Centro de Salud Chillán Viejo', (SELECT id FROM core.organization WHERE code='DIPIR'), CURRENT_TIMESTAMP - INTERVAL '20 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='FIRMADO'), true),
('DEMO-R-DEC-002', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='DECRETO'), 'Decreto modificación presupuestaria programa DIDESO', (SELECT id FROM core.organization WHERE code='DIDESO'), CURRENT_TIMESTAMP - INTERVAL '30 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='TRAMITADO'), true),
('DEMO-R-DEC-003', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='DECRETO'), 'Decreto asignación FNDR multicancha Yungay', (SELECT id FROM core.organization WHERE code='DIPIR'), CURRENT_TIMESTAMP - INTERVAL '60 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='TOMADO_RAZON'), true),
('DEMO-R-RES-004', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='RESOLUCION'), 'Aprueba programa apícola comunas rurales', (SELECT id FROM core.organization WHERE code='DIFOI'), CURRENT_TIMESTAMP - INTERVAL '90 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='TOMADO_RAZON'), false),
('DEMO-R-RES-005', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='RESOLUCION'), 'Aprueba estudio plan regulador Chillán', (SELECT id FROM core.organization WHERE code='DIPLADE'), CURRENT_TIMESTAMP - INTERVAL '40 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='RECHAZADO_CGR'), true),
('DEMO-R-RES-006', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='RESOLUCION'), 'Aprueba contrato constructora (anulado)', (SELECT id FROM core.organization WHERE code='DIT'), CURRENT_TIMESTAMP - INTERVAL '120 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='ANULADO'), false),
-- Más para volumen
('DEMO-R-OFI-001', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='OFICIO'), 'Oficio a Contraloría Regional — rendición trimestral', (SELECT id FROM core.organization WHERE code='DAF'), CURRENT_TIMESTAMP - INTERVAL '25 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='FIRMADO'), false),
('DEMO-R-OFI-002', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='OFICIO'), 'Oficio requerimiento información SERVIU', (SELECT id FROM core.organization WHERE code='DIT'), CURRENT_TIMESTAMP - INTERVAL '8 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='BORRADOR'), false),
('DEMO-R-RES-007', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='RESOLUCION'), 'Aprueba bases licitación equipamiento seguridad', (SELECT id FROM core.organization WHERE code='DAF'), CURRENT_TIMESTAMP - INTERVAL '28 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='VISADO'), false),
('DEMO-R-DEC-004', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='DECRETO'), 'Decreto convenio marco UBB', (SELECT id FROM core.organization WHERE code='DIPLADE'), CURRENT_TIMESTAMP - INTERVAL '180 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='TOMADO_RAZON'), true),
('DEMO-R-RES-008', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='RESOLUCION'), 'Aprueba adquisición ambulancias SAMU', (SELECT id FROM core.organization WHERE code='DIDESO'), CURRENT_TIMESTAMP - INTERVAL '58 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='TRAMITADO'), false),
('DEMO-R-RES-009', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='RESOLUCION'), 'Cierre administrativo multicancha techada Yungay', (SELECT id FROM core.organization WHERE code='DIPIR'), CURRENT_TIMESTAMP - INTERVAL '35 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='FIRMADO'), false),
('DEMO-R-CER-001', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='CERTIFICADO'), 'Certificado disponibilidad presupuestaria FNDR Q2', (SELECT id FROM core.organization WHERE code='DAF'), CURRENT_TIMESTAMP - INTERVAL '12 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='FIRMADO'), false),
('DEMO-R-INF-001', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='INFORME'), 'Informe técnico evaluación FRIL Pemuco', (SELECT id FROM core.organization WHERE code='DIPIR'), CURRENT_TIMESTAMP - INTERVAL '22 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='VISADO'), false),
('DEMO-R-INF-002', (SELECT id FROM ref.category WHERE scheme='act_type' AND code='INFORME'), 'Informe estado avance obras DIT Q1 2026', (SELECT id FROM core.organization WHERE code='DIT'), CURRENT_TIMESTAMP - INTERVAL '45 days', (SELECT id FROM ref.category WHERE scheme='act_state' AND code='TOMADO_RAZON'), false)
ON CONFLICT DO NOTHING;

-- 5.2 OPERATIONAL_COMMITMENT (25) — 4 estados + VENCIDO
DO $$
DECLARE
    v_iprs TEXT[] := ARRAY['DEMO-R-SNI-007','DEMO-R-SNI-007','DEMO-R-FRIL-005','DEMO-R-FRIL-005','DEMO-R-SUBV8-004','DEMO-R-SUBV8-004','DEMO-R-TRF-003','DEMO-R-TRF-003','DEMO-R-G06-003','DEMO-R-EXT-001','DEMO-R-EXT-002','DEMO-R-EXT-003','DEMO-R-EXT-004','DEMO-R-C33-003','DEMO-R-SNI-006','DEMO-R-SNI-005','DEMO-R-FRPD-003','DEMO-R-FRIL-006','DEMO-R-G06-002','DEMO-R-FRPD-002','DEMO-R-SNI-008','DEMO-R-SNI-008','DEMO-R-C33-004','DEMO-R-G06-004','DEMO-R-TRF-004'];
    v_states TEXT[] := ARRAY['PENDIENTE','EN_PROGRESO','PENDIENTE','EN_PROGRESO','EN_PROGRESO','COMPLETADO','PENDIENTE','EN_PROGRESO','PENDIENTE','EN_PROGRESO','EN_PROGRESO','PENDIENTE','EN_PROGRESO','COMPLETADO','PENDIENTE','EN_PROGRESO','PENDIENTE','VENCIDO','COMPLETADO','COMPLETADO','VERIFICADO','VERIFICADO','VERIFICADO','VERIFICADO','VENCIDO'];
    v_descs TEXT[] := ARRAY['Verificar estado de obras pavimentación','Coordinar inspección terreno con ITO','Gestionar permisos municipales para techado','Validar especificaciones técnicas feria','Realizar visita de seguimiento a beneficiarios','Entregar informe final programa huertos','Coordinar agenda reunión con SERNATUR','Gestionar viáticos equipo terreno','Preparar documentación CDP DIPLADE','Evaluar alternativas de reanudación obra','Preparar acta recepción definitiva','Revisar documentación licitación parque','Confirmar cumplimiento cláusulas contrato','Completar registro fotográfico recepción','Preparar documentación CDP piscina','Coordinar con evaluador MDSF','Revisar bases de licitación equipamiento','Enviar rendición trimestral (atrasada)','Cerrar informe técnico estudio tren','Verificar entregas parciales ambulancias','Archivar documentación cierre proyecto','Registrar lecciones aprendidas','Firmar acta de cierre rendición','Archivar expediente estudio zonificación','Gestionar resciliación con universidad'];
    v_users TEXT[] := ARRAY['jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.difoi@goreos.cl','jefe.difoi@goreos.cl','jefe.dideso@goreos.cl','jefe.dideso@goreos.cl','jefe.difoi@goreos.cl','jefe.difoi@goreos.cl','analista.diplade@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.daf@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','jefe.dit@goreos.cl','analista.dipir@goreos.cl','jefe.daf@goreos.cl','rtf.daf@goreos.cl','analista.diplade@goreos.cl','jefe.dideso@goreos.cl','analista.dipir@goreos.cl','analista.dipir@goreos.cl','jefe.dit@goreos.cl','analista.diplade@goreos.cl','jefe.difoi@goreos.cl'];
    v_ct_id UUID;
    v_i INTEGER;
BEGIN
    -- Use first commitment type found
    SELECT id INTO v_ct_id FROM ref.operational_commitment_type LIMIT 1;

    FOR v_i IN 1..25 LOOP
        INSERT INTO core.operational_commitment (
            code, ipr_id, commitment_type_id, description, responsible_id, division_id, due_date, state_id,
            completed_at, verified_by_id, verified_at, created_by_id
        ) VALUES (
            'DEMO-R-COM-' || LPAD(v_i::text, 3, '0'),
            (SELECT id FROM core.ipr WHERE codigo_bip = v_iprs[v_i] LIMIT 1),
            v_ct_id,
            v_descs[v_i],
            (SELECT id FROM core."user" WHERE email = v_users[v_i]),
            (SELECT division_id FROM core."user" WHERE email = v_users[v_i]),
            CASE
                WHEN v_states[v_i] = 'VENCIDO' THEN CURRENT_DATE - INTERVAL '10 days'
                WHEN v_states[v_i] IN ('COMPLETADO','VERIFICADO') THEN CURRENT_DATE - INTERVAL '5 days'
                ELSE CURRENT_DATE + (v_i * INTERVAL '3 days')
            END,
            (SELECT id FROM ref.category WHERE scheme='commitment_state' AND code=v_states[v_i]),
            CASE WHEN v_states[v_i] IN ('COMPLETADO','VERIFICADO') THEN CURRENT_TIMESTAMP - INTERVAL '7 days' ELSE NULL END,
            CASE WHEN v_states[v_i] = 'VERIFICADO' THEN (SELECT id FROM core."user" WHERE email='jefe.dipir@goreos.cl') ELSE NULL END,
            CASE WHEN v_states[v_i] = 'VERIFICADO' THEN CURRENT_TIMESTAMP - INTERVAL '3 days' ELSE NULL END,
            (SELECT id FROM core."user" WHERE email='admin@goreos.cl')
        ) ON CONFLICT (code) DO NOTHING;
    END LOOP;
END $$;

-- 5.3 IPR_PROBLEM (12) — 4 estados
INSERT INTO core.ipr_problem (code, ipr_id, problem_type_id, description, state_id, detected_by_id, impact_description, created_by_id) VALUES
('DEMO-R-PRB-001', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='TECNICO'), 'Falla en sistema de drenaje durante excavación — requiere rediseño parcial', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='ABIERTO'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), 'Retraso estimado 15 días en frente norte', (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl')),
('DEMO-R-PRB-002', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='FINANCIERO'), 'Incremento 12% en costo de materiales post-licitación', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='ABIERTO'), (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'), 'Posible déficit presupuestario de M$13', (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl')),
('DEMO-R-PRB-003', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-001'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='LEGAL'), 'Terreno en litigio impide inicio de obra — recurso pendiente en tribunal', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='ABIERTO'), (SELECT id FROM core."user" WHERE email='juridico@goreos.cl'), 'Obra paralizada indefinidamente', (SELECT id FROM core."user" WHERE email='juridico@goreos.cl')),
('DEMO-R-PRB-004', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='COORDINACION'), 'SERNATUR no ha designado contraparte técnica regional', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='ABIERTO'), (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'), 'Actividades de terreno no pueden iniciar', (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl')),
('DEMO-R-PRB-005', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-004'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='ADMINISTRATIVO'), 'Retraso en emisión de certificado fitosanitario SAG', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='EN_GESTION'), (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'), 'Programa no puede comprar insumos', (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl')),
('DEMO-R-PRB-006', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='TECNICO'), 'Modificación de diseño requerida por SERVIU — nuevo cruce peatonal', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='EN_GESTION'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), 'Rediseño parcial en ejecución', (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl')),
('DEMO-R-PRB-007', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='FINANCIERO'), 'Ajuste presupuestario por variación UTM', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='EN_GESTION'), (SELECT id FROM core."user" WHERE email='jefe.daf@goreos.cl'), 'Requiere modificación de CDP', (SELECT id FROM core."user" WHERE email='jefe.daf@goreos.cl')),
('DEMO-R-PRB-008', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-C33-003'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='EXTERNO'), 'Proveedor de materiales en quiebra — buscar alternativas', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='EN_GESTION'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), 'Posible retraso 30 días', (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl')),
('DEMO-R-PRB-009', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='TECNICO'), 'Defecto menor detectado en recepción — subsanado por constructora', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='RESUELTO'), (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'), 'Sin impacto en plazo', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl')),
('DEMO-R-PRB-010', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-G06-004'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='ADMINISTRATIVO'), 'Retraso en envío de informe final al MDSF — resuelto', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='RESUELTO'), (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl'), 'Informe entregado 5 días tarde', (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl')),
('DEMO-R-PRB-011', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-006'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='FINANCIERO'), 'Discrepancia menor en rendición — aclarada por UCR', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='RESUELTO'), (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl'), 'Rendición regularizada', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
('DEMO-R-PRB-012', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-004'), (SELECT id FROM ref.category WHERE scheme='problem_type' AND code='COORDINACION'), 'Contraparte no participó en actividades — incumplimiento convenio', (SELECT id FROM ref.category WHERE scheme='problem_state' AND code='CERRADO_SIN_RESOLVER'), (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'), 'Motivó resciliación del convenio', (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT (code) DO NOTHING;


-- =============================================================================
-- TIER 5B: CADENAS IPR ↔ CONVENIO ↔ RESOLUCIÓN ↔ CDP
-- =============================================================================
-- Conecta las entidades que estaban desvinculadas:
-- 1. resolution: puente entre administrative_act ↔ ipr ↔ agreement
-- 2. budget_commitment.resolution_id: CDP vinculado a resolución
-- 3. ipr_closure.closure_act_id: cierre vinculado a acto administrativo
-- 4. renditions: rendiciones para convenios F4+ nuevos

-- 5B.1 RESOLUCIONES — vinculan actos administrativos con IPRs y convenios
DO $$
DECLARE
    v_aprobatoria UUID; v_modificatoria UUID;
    v_sub_convenio UUID; v_sub_pago UUID; v_sub_modifica UUID;
    v_admin UUID;
BEGIN
    SELECT id INTO v_aprobatoria FROM ref.category WHERE scheme='resolution_type' AND code='APROBATORIA';
    SELECT id INTO v_modificatoria FROM ref.category WHERE scheme='resolution_type' AND code='MODIFICATORIA';
    SELECT id INTO v_sub_convenio FROM ref.category WHERE scheme='resolution_subtype' AND code='APRUEBA_CONVENIO';
    SELECT id INTO v_sub_pago FROM ref.category WHERE scheme='resolution_subtype' AND code='APRUEBA_PAGO';
    SELECT id INTO v_sub_modifica FROM ref.category WHERE scheme='resolution_subtype' AND code='MODIFICA_PRESUPUESTO';
    SELECT id INTO v_admin FROM core."user" WHERE email='admin@goreos.cl';

    -- RES-001: Resolución aprueba convenio SNI-007 ↔ AGR-006 (SERVIU pavimentación)
    INSERT INTO core.resolution (administrative_act_id, resolution_type_id, resolution_subtype_id, ipr_id, agreement_id, budget_amount, created_by_id)
    SELECT
        (SELECT id FROM core.administrative_act WHERE act_number='DEMO-R-RES-004'),
        v_aprobatoria, v_sub_convenio,
        (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'),
        (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-006'),
        5800000000, v_admin
    WHERE EXISTS (SELECT 1 FROM core.administrative_act WHERE act_number='DEMO-R-RES-004')
    ON CONFLICT DO NOTHING;

    -- RES-002: Resolución aprueba convenio EXT-003 ↔ AGR-005 (Constructora parque)
    INSERT INTO core.resolution (administrative_act_id, resolution_type_id, resolution_subtype_id, ipr_id, agreement_id, budget_amount, created_by_id)
    SELECT
        (SELECT id FROM core.administrative_act WHERE act_number='DEMO-R-RES-003'),
        v_aprobatoria, v_sub_convenio,
        (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'),
        (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-005'),
        2800000000, v_admin
    WHERE EXISTS (SELECT 1 FROM core.administrative_act WHERE act_number='DEMO-R-RES-003')
    ON CONFLICT DO NOTHING;

    -- RES-003: Resolución aprueba pago cuota convenio FRIL-005
    INSERT INTO core.resolution (administrative_act_id, resolution_type_id, resolution_subtype_id, ipr_id, agreement_id, budget_amount, created_by_id)
    SELECT
        (SELECT id FROM core.administrative_act WHERE act_number='DEMO-R-RES-007'),
        v_aprobatoria, v_sub_pago,
        (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'),
        (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-007'),
        36666666, v_admin
    WHERE EXISTS (SELECT 1 FROM core.administrative_act WHERE act_number='DEMO-R-RES-007')
    ON CONFLICT DO NOTHING;

    -- RES-004: Decreto aprueba CDP SNI-006 (piscina Coihueco)
    INSERT INTO core.resolution (administrative_act_id, resolution_type_id, resolution_subtype_id, ipr_id, budget_amount, created_by_id)
    SELECT
        (SELECT id FROM core.administrative_act WHERE act_number='DEMO-R-DEC-001'),
        v_aprobatoria, v_sub_pago,
        (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-006'),
        1600000000, v_admin
    WHERE EXISTS (SELECT 1 FROM core.administrative_act WHERE act_number='DEMO-R-DEC-001')
    ON CONFLICT DO NOTHING;

    -- RES-005: Decreto modifica presupuesto programa DIDESO
    INSERT INTO core.resolution (administrative_act_id, resolution_type_id, resolution_subtype_id, ipr_id, budget_amount, created_by_id)
    SELECT
        (SELECT id FROM core.administrative_act WHERE act_number='DEMO-R-DEC-002'),
        v_modificatoria, v_sub_modifica,
        (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-003'),
        95000000, v_admin
    WHERE EXISTS (SELECT 1 FROM core.administrative_act WHERE act_number='DEMO-R-DEC-002')
    ON CONFLICT DO NOTHING;

    -- RES-006: Decreto asignación FNDR multicancha Yungay (cerrado)
    INSERT INTO core.resolution (administrative_act_id, resolution_type_id, resolution_subtype_id, ipr_id, agreement_id, budget_amount, created_by_id)
    SELECT
        (SELECT id FROM core.administrative_act WHERE act_number='DEMO-R-DEC-003'),
        v_aprobatoria, v_sub_convenio,
        (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'),
        (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-014'),
        890000000, v_admin
    WHERE EXISTS (SELECT 1 FROM core.administrative_act WHERE act_number='DEMO-R-DEC-003')
    ON CONFLICT DO NOTHING;

    -- RES-007: Decreto convenio marco UBB
    INSERT INTO core.resolution (administrative_act_id, resolution_type_id, resolution_subtype_id, agreement_id, budget_amount, created_by_id)
    SELECT
        (SELECT id FROM core.administrative_act WHERE act_number='DEMO-R-DEC-004'),
        v_aprobatoria, v_sub_convenio,
        (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-018'),
        1500000000, v_admin
    WHERE EXISTS (SELECT 1 FROM core.administrative_act WHERE act_number='DEMO-R-DEC-004')
    ON CONFLICT DO NOTHING;

    -- RES-008: Resolución aprueba convenio TRF-003 ↔ AGR-008 (SERNATUR turismo)
    INSERT INTO core.resolution (administrative_act_id, resolution_type_id, resolution_subtype_id, ipr_id, agreement_id, budget_amount, created_by_id)
    SELECT
        (SELECT id FROM core.administrative_act WHERE act_number='DEMO-R-RES-004'),
        v_aprobatoria, v_sub_convenio,
        (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'),
        (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-008'),
        280000000, v_admin
    WHERE EXISTS (SELECT 1 FROM core.administrative_act WHERE act_number='DEMO-R-RES-004')
    ON CONFLICT DO NOTHING;

    -- RES-009: Resolución cierre multicancha Yungay
    INSERT INTO core.resolution (administrative_act_id, resolution_type_id, ipr_id, created_by_id)
    SELECT
        (SELECT id FROM core.administrative_act WHERE act_number='DEMO-R-RES-009'),
        v_aprobatoria,
        (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'),
        v_admin
    WHERE EXISTS (SELECT 1 FROM core.administrative_act WHERE act_number='DEMO-R-RES-009')
    ON CONFLICT DO NOTHING;

    -- RES-010: Resolución aprueba ambulancias SAMU
    INSERT INTO core.resolution (administrative_act_id, resolution_type_id, resolution_subtype_id, ipr_id, budget_amount, created_by_id)
    SELECT
        (SELECT id FROM core.administrative_act WHERE act_number='DEMO-R-RES-008'),
        v_aprobatoria, v_sub_pago,
        (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRPD-002'),
        480000000, v_admin
    WHERE EXISTS (SELECT 1 FROM core.administrative_act WHERE act_number='DEMO-R-RES-008')
    ON CONFLICT DO NOTHING;
END $$;

-- 5B.2 CDP ↔ RESOLUCIÓN — vincular CDPs originales a resoluciones
DO $$
DECLARE
    v_res_id UUID;
BEGIN
    -- CDP-001 (SNI-006 piscina) → resolución del decreto DEC-001
    SELECT r.id INTO v_res_id FROM core.resolution r
    JOIN core.administrative_act a ON r.administrative_act_id = a.id
    WHERE a.act_number = 'DEMO-R-DEC-001' LIMIT 1;

    IF v_res_id IS NOT NULL THEN
        UPDATE core.budget_commitment SET resolution_id = v_res_id
        WHERE commitment_number = 'DEMO-R-CDP-001' AND resolution_id IS NULL;
    END IF;

    -- CDP-019 (SNI-008 cerrado) → resolución del decreto DEC-003
    SELECT r.id INTO v_res_id FROM core.resolution r
    JOIN core.administrative_act a ON r.administrative_act_id = a.id
    WHERE a.act_number = 'DEMO-R-DEC-003'
    AND r.ipr_id = (SELECT id FROM core.ipr WHERE codigo_bip = 'DEMO-R-SNI-008')
    LIMIT 1;

    IF v_res_id IS NOT NULL THEN
        UPDATE core.budget_commitment SET resolution_id = v_res_id
        WHERE commitment_number = 'DEMO-R-CDP-019' AND resolution_id IS NULL;
    END IF;
END $$;

-- 5B.3 CIERRE ↔ ACTO: moved to TIER 10.2b (after ipr_closure INSERT)

-- 5B.4 RENDICIONES PARA CONVENIOS NUEVOS (F4+)
-- Genera 1-2 rendiciones por convenio F4+ nuevo que no tenga rendiciones
DO $$
DECLARE
    v_agr RECORD;
    v_pendiente UUID; v_en_revision UUID; v_aprobada UUID; v_observada UUID;
    v_states UUID[];
    v_idx INTEGER := 0;
    v_reporter UUID;
BEGIN
    SELECT id INTO v_pendiente FROM ref.category WHERE scheme='rendition_state' AND code='PENDIENTE';
    SELECT id INTO v_en_revision FROM ref.category WHERE scheme='rendition_state' AND code='EN_REVISION_RTF';
    SELECT id INTO v_aprobada FROM ref.category WHERE scheme='rendition_state' AND code='APROBADA';
    SELECT id INTO v_observada FROM ref.category WHERE scheme='rendition_state' AND code='OBSERVADA';
    SELECT id INTO v_reporter FROM core."user" WHERE email='rtf.daf@goreos.cl';

    v_states := ARRAY[v_pendiente, v_en_revision, v_aprobada, v_observada, v_pendiente, v_en_revision];

    FOR v_agr IN
        SELECT a.id, a.agreement_number, a.receiver_id
        FROM core.agreement a
        JOIN ref.category s ON a.state_id = s.id
        WHERE a.agreement_number LIKE 'DEMO-R-AGR-2%' -- New batch (200+)
          AND s.code = 'VIGENTE'
          AND NOT EXISTS (SELECT 1 FROM core.rendition r WHERE r.agreement_id = a.id)
        ORDER BY a.agreement_number
    LOOP
        v_idx := v_idx + 1;

        -- Rendición trimestre anterior
        INSERT INTO core.rendition (agreement_id, renderer_id, state_id, period_start, period_end, submitted_at, created_by_id)
        VALUES (v_agr.id, v_agr.receiver_id,
                v_states[1 + ((v_idx - 1) % 6)],
                '2025-10-01', '2025-12-31',
                CASE WHEN v_idx % 3 != 0 THEN CURRENT_TIMESTAMP - (v_idx * 3 * INTERVAL '1 day') ELSE NULL END,
                v_reporter)
        ON CONFLICT DO NOTHING;

        -- Rendición trimestre actual (solo para algunos)
        IF v_idx % 2 = 0 THEN
            INSERT INTO core.rendition (agreement_id, renderer_id, state_id, period_start, period_end, submitted_at, created_by_id)
            VALUES (v_agr.id, v_agr.receiver_id, v_pendiente,
                    '2026-01-01', '2026-03-31', NULL, v_reporter)
            ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;

    RAISE NOTICE 'Generated renditions for % new agreements', v_idx;
END $$;


-- =============================================================================
-- TIER 6: DGI CORE (~70 registros)
-- =============================================================================

-- 6.1 DGI_INDICATOR (15) — 5 dimensiones × 3, señales variadas
INSERT INTO core.dgi_indicator (code, name, dimension_id, description, current_value, target_value, unit, signal_id, trend, division_id, lifecycle_status_id, source_type, frequency, created_by_id) VALUES
('DEMO-R-IND-P01', 'Ejecución Presupuestaria FNDR', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='PRESUPUESTO'), 'Porcentaje de ejecución presupuestaria FNDR acumulada', 62.5, 80.0, '%', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='AMARILLO'), 'up', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'MENSUAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-P02', 'Ejecución Presupuestaria Sectorial', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='PRESUPUESTO'), 'Porcentaje de ejecución presupuesto sectorial', 78.3, 75.0, '%', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='VERDE'), 'up', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'MENSUAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-P03', 'CDPs Vigentes vs Presupuesto', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='PRESUPUESTO'), 'Ratio CDPs vigentes sobre presupuesto disponible', 45.2, 60.0, '%', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='ROJO'), 'down', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'SEMANAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-C01', 'IPRs en Formulación (F0-F2)', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='CARTERA_IPR'), 'Número de IPRs activos en fases de formulación', 15, 20, 'unidades', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='AMARILLO'), 'flat', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'SEMANAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-C02', 'IPRs en Ejecución (F4)', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='CARTERA_IPR'), 'Número de IPRs en fase de ejecución', 12, 15, 'unidades', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='VERDE'), 'up', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'SEMANAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-C03', 'Tasa de Cierre IPR', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='CARTERA_IPR'), 'IPRs cerrados en últimos 12 meses vs total ejecutados', 35.0, 50.0, '%', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='ROJO'), 'flat', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'MENSUAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-V01', 'Convenios Vigentes', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='CONVENIOS'), 'Total convenios en estado vigente', 8, 10, 'unidades', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='VERDE'), 'up', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'SEMANAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-V02', 'Rendiciones Pendientes', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='CONVENIOS'), 'Rendiciones en estado pendiente o en revisión', 5, 3, 'unidades', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='ROJO'), 'up', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'SEMANAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-V03', 'Tasa Cumplimiento SLA Rendiciones', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='CONVENIOS'), 'Rendiciones revisadas dentro del SLA', 72.0, 90.0, '%', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='AMARILLO'), 'down', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'MENSUAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-T01', 'Documentos con Firma Electrónica', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='TDE'), 'Porcentaje de actos administrativos con FEA', 45.0, 80.0, '%', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='ROJO'), 'up', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'MANUAL', 'MENSUAL', (SELECT id FROM core."user" WHERE email='td@goreos.cl')),
('DEMO-R-IND-T02', 'Trámites Digitalizados', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='TDE'), 'Porcentaje de trámites disponibles en línea', 30.0, 60.0, '%', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='ROJO'), 'up', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'MANUAL', 'TRIMESTRAL', (SELECT id FROM core."user" WHERE email='td@goreos.cl')),
('DEMO-R-IND-T03', 'Uptime Plataformas Digitales', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='TDE'), 'Disponibilidad mensual de plataformas institucionales', 99.2, 99.5, '%', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='VERDE'), 'flat', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'MENSUAL', (SELECT id FROM core."user" WHERE email='td@goreos.cl')),
('DEMO-R-IND-R01', 'Riesgos Abiertos', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='RIESGOS'), 'Riesgos en estado abierto (no mitigados/cerrados)', 8, 5, 'unidades', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='AMARILLO'), 'up', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'SEMANAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-R02', 'Alertas Críticas Activas', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='RIESGOS'), 'Alertas con severidad CRITICO sin resolver', 3, 0, 'unidades', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='ROJO'), 'flat', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'DIARIA', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-IND-R03', 'Escalamientos Activos', (SELECT id FROM ref.category WHERE scheme='dgi_indicator_dimension' AND code='RIESGOS'), 'Escalamientos no resueltos', 2, 1, 'unidades', (SELECT id FROM ref.category WHERE scheme='dgi_signal' AND code='AMARILLO'), 'down', NULL, (SELECT id FROM ref.category WHERE scheme='dgi_indicator_lifecycle' AND code='VIGENTE'), 'AUTO', 'SEMANAL', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 6.2 DGI_PROCESS (5) — 6-state FSM
INSERT INTO core.dgi_process (code, name, description, scope, division_id, owner_id, status_id, criticality, created_by_id) VALUES
('DEMO-R-PROC-001', 'Formulación y Evaluación IPR', 'Proceso de formulación, admisibilidad y evaluación técnico-económica de iniciativas de inversión', 'F0 a F2 completo', (SELECT id FROM core.organization WHERE code='DIPIR'), (SELECT id FROM core."user" WHERE email='jefe.dipir@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_process_status' AND code='VALIDADO'), 'ALTA', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl')),
('DEMO-R-PROC-002', 'Gestión de Convenios', 'Ciclo completo de convenios: negociación, firma, ejecución, rendición', 'Convenios GORE con entidades externas', (SELECT id FROM core.organization WHERE code='DAF'), (SELECT id FROM core."user" WHERE email='jefe.daf@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_process_status' AND code='MODELADO'), 'ALTA', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl')),
('DEMO-R-PROC-003', 'Rendición de Cuentas SISREC', 'Proceso de rendición ante Contraloría General', 'Rendiciones trimestrales CGR', (SELECT id FROM core.organization WHERE code='DAF'), (SELECT id FROM core."user" WHERE email='jefe.ucr@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_process_status' AND code='EN_LEVANTAMIENTO'), 'ALTA', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl')),
('DEMO-R-PROC-004', 'Tramitación Actos Administrativos', 'Generación, revisión, firma y toma de razón de actos administrativos', 'Resoluciones y decretos GORE', (SELECT id FROM core.organization WHERE code='DIJ'), (SELECT id FROM core."user" WHERE email='juridico@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_process_status' AND code='PUBLICADO'), 'MEDIA', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl')),
('DEMO-R-PROC-005', 'Supervisión de Obras F4', 'Supervisión técnica de obras en ejecución incluyendo ITO', 'Obras F4 con contrato vigente', (SELECT id FROM core.organization WHERE code='DIT'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_process_status' AND code='IDENTIFICADO'), 'ALTA', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 6.3 DGI_PROCESS satellites
-- Process Actors (10)
INSERT INTO core.dgi_process_actor (process_id, actor_type, actor_name, lane_label, description) VALUES
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-001'), 'ROL', 'Analista DIPIR', 'Formulación', 'Formula y revisa IPR F0-F2'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-001'), 'SISTEMA', 'GORE_OS', 'Sistema', 'Gestiona flujo y validaciones'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-002'), 'ROL', 'Jefe DAF', 'Gestión', 'Aprueba y supervisa convenios'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-002'), 'ROL', 'Asesor Jurídico', 'Revisión Legal', 'Revisa cláusulas y V.B.'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-003'), 'ROL', 'RTF', 'Revisión', 'Revisa rendiciones trimestrales'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-003'), 'ROL', 'Jefe UCR', 'Aprobación', 'Visa y aprueba rendiciones'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-004'), 'ROL', 'Gobernador', 'Firma', 'Firma decretos y resoluciones'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-004'), 'DIVISION', 'DIJ', 'Tramitación', 'Tramita ante Contraloría'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-005'), 'ROL', 'ITO', 'Inspección', 'Inspección técnica en terreno'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-005'), 'ROL', 'Profesional DIT', 'Supervisión', 'Supervisión técnica GORE')
ON CONFLICT DO NOTHING;

-- Process Metrics (8)
INSERT INTO core.dgi_process_metric (process_id, name, value, unit, measured_at, measurement_type, source) VALUES
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-001'), 'Tiempo promedio F0→F2', 45, 'días', CURRENT_DATE - INTERVAL '15 days', 'BASELINE', 'GORE_OS analytics'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-001'), 'Tasa de admisibilidad', 78.5, '%', CURRENT_DATE - INTERVAL '15 days', 'BASELINE', 'GORE_OS analytics'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-002'), 'Tiempo firma convenio', 32, 'días', CURRENT_DATE - INTERVAL '10 days', 'BASELINE', 'GORE_OS analytics'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-002'), 'Convenios vigentes', 8, 'unidades', CURRENT_DATE - INTERVAL '10 days', 'PERIODICA', 'GORE_OS analytics'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-003'), 'SLA cumplimiento rendiciones', 72, '%', CURRENT_DATE - INTERVAL '5 days', 'BASELINE', 'GORE_OS analytics'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-003'), 'Rendiciones pendientes', 5, 'unidades', CURRENT_DATE - INTERVAL '5 days', 'PERIODICA', 'GORE_OS analytics'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-004'), 'Tiempo tramitación promedio', 18, 'días', CURRENT_DATE - INTERVAL '20 days', 'BASELINE', 'GORE_OS analytics'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-005'), 'Visitas terreno por mes', 12, 'unidades', CURRENT_DATE - INTERVAL '7 days', 'PERIODICA', 'GORE_OS analytics')
ON CONFLICT DO NOTHING;

-- Process Rules (5)
INSERT INTO core.dgi_process_rule (process_id, code, description, rule_type) VALUES
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-001'), 'R-001', 'IPR requiere admisibilidad antes de evaluación', 'VALIDACION'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-002'), 'R-002', 'V.B. jurídico obligatorio antes de firma', 'RESTRICCION'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-003'), 'R-003', 'Rendición trimestral dentro de SLA 7 días', 'RESTRICCION'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-004'), 'R-004', 'Decretos >7K UTM requieren toma de razón CGR', 'DECISION'),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-005'), 'R-005', 'PROYECTO EN_LICITACION requiere ITO para avanzar a ADJUDICADO', 'VALIDACION')
ON CONFLICT DO NOTHING;

-- Process Pain Points (5)
INSERT INTO core.dgi_process_pain_point (process_id, description, impact, bpmn_stage, reported_by_id) VALUES
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-001'), 'Demora excesiva en respuesta de evaluadores MDSF', 'ALTO', 'Evaluación técnica', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl')),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-002'), 'Idas y vueltas en revisión jurídica de cláusulas', 'MEDIO', 'Revisión legal', (SELECT id FROM core."user" WHERE email='jefe.daf@goreos.cl')),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-003'), 'Información incompleta de ejecutores en rendiciones', 'ALTO', 'Recepción documentos', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-004'), 'Cuello de botella en firma del Gobernador', 'ALTO', 'Firma autoridad', (SELECT id FROM core."user" WHERE email='juridico@goreos.cl')),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-005'), 'Difícil coordinar agenda ITO con constructora', 'MEDIO', 'Programación visitas', (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 6.4 DGI_INITIATIVE (10) — Kanban: BACKLOG(2), EN_CURSO(3), REVISION(2), COMPLETADO(2), CANCELADO(1)
-- WIP limits: EN_CURSO:5, REVISION:2 — we stay within limits
INSERT INTO core.dgi_initiative (code, name, description, responsible_id, status_id, division_id, start_date, target_date, progress, sort_order, created_by_id) VALUES
('DEMO-R-INI-001', 'Automatizar notificaciones SLA rendiciones', 'Bot de alertas automáticas cuando rendición supera SLA', (SELECT id FROM core."user" WHERE email='td@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_initiative_status' AND code='BACKLOG'), (SELECT id FROM core.organization WHERE code='DGI'), NULL, CURRENT_DATE + INTERVAL '60 days', 0, 1, (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-INI-002', 'Dashboard ejecución presupuestaria por división', 'Visualización en tiempo real de ejecución por programa', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_initiative_status' AND code='BACKLOG'), (SELECT id FROM core.organization WHERE code='DGI'), NULL, CURRENT_DATE + INTERVAL '45 days', 0, 2, (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-INI-003', 'Reducir tiempo formulación F0-F2', 'Estandarizar checklist y templates de formulación', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_initiative_status' AND code='EN_CURSO'), (SELECT id FROM core.organization WHERE code='DGI'), CURRENT_DATE - INTERVAL '20 days', CURRENT_DATE + INTERVAL '30 days', 35.0, 1, (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-INI-004', 'Digitalizar proceso de firma electrónica actos', 'Implementar FEA en cadena completa de actos administrativos', (SELECT id FROM core."user" WHERE email='td@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_initiative_status' AND code='EN_CURSO'), (SELECT id FROM core.organization WHERE code='DGI'), CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE + INTERVAL '60 days', 45.0, 2, (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-INI-005', 'Mejorar SLA revisión rendiciones RTF', 'Optimizar flujo RTF→UCR reduciendo observaciones', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_initiative_status' AND code='EN_CURSO'), (SELECT id FROM core.organization WHERE code='DGI'), CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE + INTERVAL '45 days', 25.0, 3, (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-INI-006', 'Protocolo gestión de riesgos operacionales', 'Documentar y estandarizar proceso de identificación y mitigación', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_initiative_status' AND code='REVISION'), (SELECT id FROM core.organization WHERE code='DGI'), CURRENT_DATE - INTERVAL '40 days', CURRENT_DATE + INTERVAL '10 days', 80.0, 1, (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-INI-007', 'Estandarizar informes de gestión mensual', 'Template unificado para informes CG a la AR', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_initiative_status' AND code='REVISION'), (SELECT id FROM core.organization WHERE code='DGI'), CURRENT_DATE - INTERVAL '35 days', CURRENT_DATE + INTERVAL '5 days', 90.0, 2, (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-INI-008', 'Mapeo procesos DIDESO (subsidios)', 'Levantamiento AS-IS del proceso de subsidios sociales', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_initiative_status' AND code='COMPLETADO'), (SELECT id FROM core.organization WHERE code='DGI'), CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '10 days', 100.0, 1, (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-INI-009', 'Capacitación GORE_OS para analistas', 'Taller de uso del sistema para nuevos analistas DIPIR/DIPLADE', (SELECT id FROM core."user" WHERE email='td@goreos.cl'), (SELECT id FROM ref.category WHERE scheme='dgi_initiative_status' AND code='COMPLETADO'), (SELECT id FROM core.organization WHERE code='DGI'), CURRENT_DATE - INTERVAL '45 days', CURRENT_DATE - INTERVAL '15 days', 100.0, 2, (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 6.5 DGI_IMPROVEMENT_OPPORTUNITY (5)
INSERT INTO core.dgi_improvement_opportunity (process_id, initiative_id, dimension, description, impact, effort, status, created_by_id) VALUES
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-001'), (SELECT id FROM core.dgi_initiative WHERE code='DEMO-R-INI-003'), 'ESPERAS', 'Eliminar tiempo muerto entre admisibilidad y evaluación', 'ALTO', 'MEDIO', 'EN_EJECUCION', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl')),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-002'), NULL, 'DUPLICACION', 'Reducir revisiones jurídicas redundantes', 'MEDIO', 'BAJO', 'VALIDADA', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl')),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-003'), (SELECT id FROM core.dgi_initiative WHERE code='DEMO-R-INI-005'), 'ERRORES', 'Reducir tasa de observaciones en rendiciones', 'ALTO', 'ALTO', 'EN_EJECUCION', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl')),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-004'), (SELECT id FROM core.dgi_initiative WHERE code='DEMO-R-INI-004'), 'AUTOMATIZACION', 'Implementar firma electrónica end-to-end', 'ALTO', 'ALTO', 'EN_EJECUCION', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl')),
((SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-005'), NULL, 'MOVIMIENTOS', 'Reducir desplazamientos ITO con inspección remota', 'MEDIO', 'MEDIO', 'PROPUESTA', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 6.6 DGI_BOTTLENECK_INVESTIGATION (3)
INSERT INTO core.dgi_bottleneck_investigation (code, status_id, division_id, process_id, detection_type, detection_value, detection_threshold, problem, created_by_id) VALUES
('DEMO-R-BN-001', (SELECT id FROM ref.category WHERE scheme='dgi_bottleneck_status' AND code='VERIFICADO'), (SELECT id FROM core.organization WHERE code='DAF'), (SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-003'), 'CYCLE_TIME', 18.5, 7.0, 'Tiempo de revisión RTF supera SLA en 164%', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-BN-002', (SELECT id FROM ref.category WHERE scheme='dgi_bottleneck_status' AND code='ANALIZADO'), (SELECT id FROM core.organization WHERE code='DIJ'), (SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-004'), 'ACCUMULATION', 12, 5, 'Cola de actos esperando firma supera umbral', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-BN-003', (SELECT id FROM ref.category WHERE scheme='dgi_bottleneck_status' AND code='DETECTADO'), (SELECT id FROM core.organization WHERE code='DIPIR'), (SELECT id FROM core.dgi_process WHERE code='DEMO-R-PROC-001'), 'CYCLE_TIME', 52, 30, 'Evaluación MDSF demora más del doble del objetivo', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 6.7 DGI_REPORT (4)
INSERT INTO core.dgi_report (code, report_type_id, status_id, title, period_start, period_end, recipient, generated_by_id, created_by_id) VALUES
('DEMO-R-RPT-001', (SELECT id FROM ref.category WHERE scheme='dgi_report_type' AND code='FLASH'), (SELECT id FROM ref.category WHERE scheme='dgi_report_status' AND code='ENVIADO'), 'Flash: Ejecución presupuestaria supera 60%', CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE, 'Gobernador Regional', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-RPT-002', (SELECT id FROM ref.category WHERE scheme='dgi_report_type' AND code='SEMANAL'), (SELECT id FROM ref.category WHERE scheme='dgi_report_status' AND code='APROBADO'), 'Informe Semanal Gestión S11-2026', CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '7 days', 'Autoridad Regional', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-RPT-003', (SELECT id FROM ref.category WHERE scheme='dgi_report_type' AND code='MENSUAL'), (SELECT id FROM ref.category WHERE scheme='dgi_report_status' AND code='EN_REVISION'), 'Informe Mensual Febrero 2026', '2026-02-01', '2026-02-28', 'Consejo Regional', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-RPT-004', (SELECT id FROM ref.category WHERE scheme='dgi_report_type' AND code='TEMATICO'), (SELECT id FROM ref.category WHERE scheme='dgi_report_status' AND code='BORRADOR'), 'Análisis Brechas Inversión Territorial Ñuble', '2025-01-01', '2025-12-31', 'DIPLADE + CORE', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 6.8 DGI_DECREE (4)
INSERT INTO core.dgi_decree (code, name, description, status_id, deadline) VALUES
('DEMO-R-DS7', 'DS 7 — Transparencia Activa', 'Decreto Supremo 7: información pública en portal institucional', (SELECT id FROM ref.category WHERE scheme='dgi_decree_status' AND code='VIGENTE'), '2026-12-31'),
('DEMO-R-DS8', 'DS 8 — Participación Ciudadana', 'Decreto Supremo 8: mecanismos de participación ciudadana', (SELECT id FROM ref.category WHERE scheme='dgi_decree_status' AND code='PARCIAL'), '2026-06-30'),
('DEMO-R-DS10', 'DS 10 — Gestión Documental', 'Decreto Supremo 10: estándares de gestión documental electrónica', (SELECT id FROM ref.category WHERE scheme='dgi_decree_status' AND code='PENDIENTE'), '2027-03-31'),
('DEMO-R-DS12', 'DS 12 — Interoperabilidad', 'Decreto Supremo 12: interoperabilidad entre servicios del Estado', (SELECT id FROM ref.category WHERE scheme='dgi_decree_status' AND code='PENDIENTE'), '2027-06-30')
ON CONFLICT DO NOTHING;


-- =============================================================================
-- TIER 7: DGI COORDINACIÓN (~40 registros)
-- =============================================================================

-- 7.1 DGI_AR_DECISION (6)
INSERT INTO core.dgi_ar_decision (description, decision_type_id, status_id, due_date, context, responsible_id, created_by_id) VALUES
('DEMO-R-DEC-A01: Priorizar cartera FRIL comunas con mayor brecha', (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_type' AND code='PRIORIDAD'), (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_status' AND code='PENDIENTE'), CURRENT_DATE + INTERVAL '21 days', 'Análisis DGI muestra desigualdad territorial en asignación FRIL', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'), (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-DEC-A02: Reasignar profesionales DIT a obras con retraso', (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_type' AND code='RECURSO'), (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_status' AND code='EN_EJECUCION'), CURRENT_DATE + INTERVAL '10 days', '3 obras con retraso >30 días requieren refuerzo técnico', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-DEC-A03: Escalar incumplimiento SLA rendiciones DIDESO', (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_type' AND code='ESCALAMIENTO'), (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_status' AND code='PENDIENTE'), CURRENT_DATE + INTERVAL '5 days', 'DIDESO tiene 3 rendiciones vencidas consecutivas', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'), (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-DEC-A04: Definir estrategia digitalización trámites 2026', (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_type' AND code='ESTRATEGIA'), (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_status' AND code='COMPLETADA'), CURRENT_DATE - INTERVAL '15 days', 'Ley 21.180 exige avance significativo durante 2026', (SELECT id FROM core."user" WHERE email='td@goreos.cl'), (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-DEC-A05: Ajustar umbrales evaluación SNI', (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_type' AND code='ESTRATEGIA'), (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_status' AND code='EN_EJECUCION'), CURRENT_DATE + INTERVAL '30 days', 'Tasa de rechazo SNI ha subido a 35% — revisar umbrales', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-DEC-A06: Reforzar coordinación GORE-municipios FRIL', (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_type' AND code='RECURSO'), (SELECT id FROM ref.category WHERE scheme='dgi_ar_decision_status' AND code='COMPLETADA'), CURRENT_DATE - INTERVAL '20 days', 'Municipios tienen dificultad para completar formulación FRIL', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'), (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 7.2 DGI_ESCALATION (6)
INSERT INTO core.dgi_escalation (code, level_id, status_id, situation, impact, recommendation, deadline, created_by_id) VALUES
('DEMO-R-ESC-101', (SELECT id FROM ref.category WHERE scheme='dgi_escalation_level' AND code='NIVEL_1'), (SELECT id FROM ref.category WHERE scheme='dgi_escalation_status' AND code='ABIERTO'), 'DAF no entrega información presupuestaria para informe mensual', 'Imposible generar informe de gestión a tiempo', 'Reunión bilateral con Jefe DAF', CURRENT_TIMESTAMP + INTERVAL '7 days', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-ESC-102', (SELECT id FROM ref.category WHERE scheme='dgi_escalation_level' AND code='NIVEL_2'), (SELECT id FROM ref.category WHERE scheme='dgi_escalation_status' AND code='EN_GESTION'), 'DIDESO incumple SLA rendiciones por tercer trimestre consecutivo', 'Riesgo de observación CGR y bloqueo de pagos', 'Notificación formal a Jefe DIDESO con copia a Secretario', CURRENT_TIMESTAMP + INTERVAL '3 days', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-ESC-103', (SELECT id FROM ref.category WHERE scheme='dgi_escalation_level' AND code='NIVEL_3'), (SELECT id FROM ref.category WHERE scheme='dgi_escalation_status' AND code='RESUELTO'), 'Bloqueo de firma decreto por diferencia de criterio jurídico', 'Proyecto SNI >7K UTM detenido 45 días', 'Intervención directa del Gobernador', CURRENT_TIMESTAMP - INTERVAL '10 days', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-ESC-104', (SELECT id FROM ref.category WHERE scheme='dgi_escalation_level' AND code='NIVEL_1'), (SELECT id FROM ref.category WHERE scheme='dgi_escalation_status' AND code='CERRADO'), 'Retraso en designación de evaluador MDSF', 'IPR C33 en espera de evaluación 30 días', 'Oficio a SEREMI MDSF', CURRENT_TIMESTAMP - INTERVAL '30 days', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-ESC-105', (SELECT id FROM ref.category WHERE scheme='dgi_escalation_level' AND code='NIVEL_2'), (SELECT id FROM ref.category WHERE scheme='dgi_escalation_status' AND code='ABIERTO'), 'Constructora no cumple hitos contractuales obra Chillán', 'Retraso acumulado 20% en pavimentación acceso norte', 'Carta certificada con apercibimiento de multas', CURRENT_TIMESTAMP + INTERVAL '14 days', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-ESC-106', (SELECT id FROM ref.category WHERE scheme='dgi_escalation_level' AND code='NIVEL_4'), (SELECT id FROM ref.category WHERE scheme='dgi_escalation_status' AND code='EN_GESTION'), 'Crisis de liquidez en ejecutor SUBV8 — riesgo de pérdida de fondos', 'Programa huertos Punilla con M$75 comprometidos', 'Escalamiento a SUBDERE + medida cautelar', CURRENT_TIMESTAMP + INTERVAL '2 days', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 7.3 DGI_SERVICE (4) + REQUESTS (10) + SLAs (5) + INTERACTIONS (6) — ya existen en wave_b demo
-- Usamos ON CONFLICT para coexistir. Aquí solo agregamos solicitudes adicionales si los servicios wave_b existen.
-- Si no existen (no se cargó wave_b), estos INSERT simplemente fallan silentemente.
INSERT INTO core.dgi_service_request (code, service_id, requester_id, status_id, description, urgency, created_by_id)
SELECT 'DEMO-R-REQ-001', s.id,
       (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'),
       (SELECT id FROM ref.category WHERE scheme='dgi_request_status' AND code='RECIBIDA'),
       'Solicito informe de avance cartera obras DIT Q1 2026', 'ALTA',
       (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl')
FROM core.dgi_service s WHERE s.code = 'DEMO-SVC-CG-001'
AND NOT EXISTS (SELECT 1 FROM core.dgi_service_request WHERE code='DEMO-R-REQ-001');

INSERT INTO core.dgi_service_request (code, service_id, requester_id, status_id, description, urgency, assigned_to_id, started_at, created_by_id)
SELECT 'DEMO-R-REQ-002', s.id,
       (SELECT id FROM core."user" WHERE email='jefe.dipir@goreos.cl'),
       (SELECT id FROM ref.category WHERE scheme='dgi_request_status' AND code='EN_EJECUCION'),
       'Levantamiento proceso evaluación IPR DIPIR', 'NORMAL',
       (SELECT id FROM core."user" WHERE email='procesos@goreos.cl'),
       NOW() - INTERVAL '8 days',
       (SELECT id FROM core."user" WHERE email='jefe.dipir@goreos.cl')
FROM core.dgi_service s WHERE s.code = 'DEMO-SVC-MP-001'
AND NOT EXISTS (SELECT 1 FROM core.dgi_service_request WHERE code='DEMO-R-REQ-002');

-- 7.4 DGI_DIVISION_INTERACTION (6)
INSERT INTO core.dgi_division_interaction (division_id, interaction_type_id, interaction_date, participants, topics, agreements, next_date, notes, created_by_id) VALUES
((SELECT id FROM core.organization WHERE code='DIPIR'), (SELECT id FROM ref.category WHERE scheme='dgi_interaction_type' AND code='CARTERA'), CURRENT_DATE - INTERVAL '3 days', '[{"name":"Jefe DIPIR","role":"Jefe División"},{"name":"CG DGI","role":"ESP_CONTROL_GESTION"}]'::jsonb, '["Revisión estado cartera IPR F0-F2","Brechas de evaluación pendiente"]'::jsonb, '[]'::jsonb, CURRENT_DATE + INTERVAL '14 days', 'DIPIR prioriza resolución de IPRs FI', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
((SELECT id FROM core.organization WHERE code='DIT'), (SELECT id FROM ref.category WHERE scheme='dgi_interaction_type' AND code='PROCESO'), CURRENT_DATE - INTERVAL '7 days', '[{"name":"Jefe DIT","role":"Jefe División"},{"name":"Procesos DGI","role":"ESP_PROCESOS"}]'::jsonb, '["Levantamiento proceso supervisión obras","Definición de KPIs F4"]'::jsonb, '[]'::jsonb, CURRENT_DATE + INTERVAL '21 days', 'DIT acepta participar en piloto BPMN', (SELECT id FROM core."user" WHERE email='procesos@goreos.cl')),
((SELECT id FROM core.organization WHERE code='DAF'), (SELECT id FROM ref.category WHERE scheme='dgi_interaction_type' AND code='PRESUPUESTO'), CURRENT_DATE - INTERVAL '12 days', '[{"name":"Jefe DAF","role":"Jefe División"},{"name":"CG DGI","role":"ESP_CONTROL_GESTION"}]'::jsonb, '["Ejecución presupuestaria Q1","Proyección cierre año"]'::jsonb, '[]'::jsonb, CURRENT_DATE + INTERVAL '15 days', 'DAF proyecta ejecución del 85% al cierre', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
((SELECT id FROM core.organization WHERE code='DIDESO'), (SELECT id FROM ref.category WHERE scheme='dgi_interaction_type' AND code='JURIDICO'), CURRENT_DATE - INTERVAL '18 days', '[{"name":"Prof. DIDESO","role":"Analista"},{"name":"Jefe DGI","role":"JEFE_DGI"}]'::jsonb, '["Estado rendiciones vencidas","Plan de regularización"]'::jsonb, '[]'::jsonb, CURRENT_DATE + INTERVAL '7 days', 'DIDESO presenta plan de regularización en 30 días', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
((SELECT id FROM core.organization WHERE code='DIFOI'), (SELECT id FROM ref.category WHERE scheme='dgi_interaction_type' AND code='TECNOLOGIA'), CURRENT_DATE - INTERVAL '5 days', '[{"name":"Jefe DIFOI","role":"Jefe División"},{"name":"TD DGI","role":"ESP_TD"}]'::jsonb, '["Adopción GORE_OS para fomento","Capacitación equipo"]'::jsonb, '[]'::jsonb, CURRENT_DATE + INTERVAL '20 days', 'DIFOI solicita capacitación en módulo convenios', (SELECT id FROM core."user" WHERE email='td@goreos.cl')),
((SELECT id FROM core.organization WHERE code='DIPLADE'), (SELECT id FROM ref.category WHERE scheme='dgi_interaction_type' AND code='GENERAL'), CURRENT_DATE - INTERVAL '25 days', '[{"name":"Jefe DIPLADE","role":"Jefe División"},{"name":"Jefe DGI","role":"JEFE_DGI"}]'::jsonb, '["Alineamiento ERD con cartera IPR","Indicadores territoriales"]'::jsonb, '[]'::jsonb, CURRENT_DATE + INTERVAL '30 days', 'Se acuerda vincular indicadores ERD con tablero DGI', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'))
ON CONFLICT DO NOTHING;


-- =============================================================================
-- TIER 8: GOBERNANZA (~35 registros)
-- =============================================================================

-- 8.1 COMMITTEES (3) — ON CONFLICT para coexistir con auto-created
INSERT INTO core.committee (code, name, committee_type_id, is_permanent, legal_basis) VALUES
('CONSEJO-REGIONAL', 'Consejo Regional de Ñuble', (SELECT id FROM ref.category WHERE scheme='committee_type' AND code='CORE'), true, 'Ley 19.175 Orgánica Constitucional'),
('COMITE-CRISIS', 'Comité de Crisis GORE Ñuble', (SELECT id FROM ref.category WHERE scheme='committee_type' AND code='COMITE_TECNICO'), true, 'Resolución Interna GORE'),
('COMITE-TD', 'Comité de Transformación Digital', (SELECT id FROM ref.category WHERE scheme='committee_type' AND code='COMITE_TECNICO'), true, 'Ley 21.180')
ON CONFLICT (code) DO NOTHING;

-- 8.2 COMMITTEE_MEMBER (10) — consejeros + secretario + gobernador
DO $$
DECLARE
    v_core_id UUID;
    v_crisis_id UUID;
    v_td_id UUID;
    v_consejero1_person UUID;
    v_consejero2_person UUID;
    v_secretario_person UUID;
    v_gobernador_person UUID;
    v_jefe_dgi_person UUID;
    v_td_person UUID;
BEGIN
    SELECT id INTO v_core_id FROM core.committee WHERE code='CONSEJO-REGIONAL';
    SELECT id INTO v_crisis_id FROM core.committee WHERE code='COMITE-CRISIS';
    SELECT id INTO v_td_id FROM core.committee WHERE code='COMITE-TD';

    SELECT person_id INTO v_consejero1_person FROM core."user" WHERE email='consejero1@goreos.cl';
    SELECT person_id INTO v_consejero2_person FROM core."user" WHERE email='consejero2@goreos.cl';
    SELECT person_id INTO v_secretario_person FROM core."user" WHERE email='secretario.core@goreos.cl';
    SELECT person_id INTO v_gobernador_person FROM core."user" WHERE email='gobernador@goreos.cl';
    SELECT person_id INTO v_jefe_dgi_person FROM core."user" WHERE email='jefe.dgi@goreos.cl';
    SELECT person_id INTO v_td_person FROM core."user" WHERE email='td@goreos.cl';

    -- CORE members
    INSERT INTO core.committee_member (committee_id, person_id, start_date, is_voting_member) VALUES
    (v_core_id, v_consejero1_person, '2025-01-01', true),
    (v_core_id, v_consejero2_person, '2025-01-01', true),
    (v_core_id, v_secretario_person, '2025-01-01', false),
    (v_core_id, v_gobernador_person, '2025-01-01', false)
    ON CONFLICT DO NOTHING;

    -- Crisis members
    INSERT INTO core.committee_member (committee_id, person_id, start_date, is_voting_member) VALUES
    (v_crisis_id, v_gobernador_person, '2025-01-01', false),
    (v_crisis_id, v_secretario_person, '2025-01-01', false),
    (v_crisis_id, v_jefe_dgi_person, '2025-01-01', false)
    ON CONFLICT DO NOTHING;

    -- TD members
    INSERT INTO core.committee_member (committee_id, person_id, start_date, is_voting_member) VALUES
    (v_td_id, v_jefe_dgi_person, '2025-01-01', false),
    (v_td_id, v_td_person, '2025-01-01', false)
    ON CONFLICT DO NOTHING;
END $$;

-- 8.3 SESSIONS (6) + MINUTES (6) + SESSION_AGREEMENTS (12)
DO $$
DECLARE
    v_core_id UUID;
    v_crisis_id UUID;
    v_td_id UUID;
    v_session_id UUID;
    v_minute_id UUID;
    v_session_type_ord UUID;
    v_session_type_ext UUID;
    v_session_type_crisis UUID;
    v_gobernador_person UUID;
    v_secretario_person UUID;
BEGIN
    SELECT id INTO v_core_id FROM core.committee WHERE code='CONSEJO-REGIONAL';
    SELECT id INTO v_crisis_id FROM core.committee WHERE code='COMITE-CRISIS';
    SELECT id INTO v_td_id FROM core.committee WHERE code='COMITE-TD';
    SELECT id INTO v_session_type_ord FROM ref.category WHERE scheme='session_type' AND code='ORDINARIA';
    SELECT id INTO v_session_type_ext FROM ref.category WHERE scheme='session_type' AND code='EXTRAORDINARIA';
    SELECT id INTO v_session_type_crisis FROM ref.category WHERE scheme='session_type' AND code='CRISIS';
    SELECT person_id INTO v_gobernador_person FROM core."user" WHERE email='gobernador@goreos.cl';
    SELECT person_id INTO v_secretario_person FROM core."user" WHERE email='secretario.core@goreos.cl';

    -- CORE Session 1: Ordinaria completada
    INSERT INTO core.session (committee_id, session_number, session_type_id, scheduled_at, started_at, ended_at, quorum_reached, location)
    VALUES (v_core_id, 901, v_session_type_ord, CURRENT_TIMESTAMP - INTERVAL '45 days', CURRENT_TIMESTAMP - INTERVAL '45 days', CURRENT_TIMESTAMP - INTERVAL '45 days' + INTERVAL '3 hours', true, 'Sala del Consejo Regional')
    RETURNING id INTO v_session_id;

    INSERT INTO core.minute (session_id, minute_number, approved_at, content, signed_by_id)
    VALUES (v_session_id, 'DEMO-R-ACTA-901', (CURRENT_DATE - INTERVAL '40 days')::date, 'Acta sesión ordinaria N°901. Aprobación cartera FNDR 2026.', v_gobernador_person)
    RETURNING id INTO v_minute_id;

    INSERT INTO core.session_agreement (minute_id, agreement_number, subject, decision, due_date) VALUES
    (v_minute_id, 1, 'Aprobación cartera FNDR infraestructura DIT', 'Se aprueba por unanimidad la cartera FNDR infraestructura propuesta', CURRENT_DATE + INTERVAL '90 days'),
    (v_minute_id, 2, 'Solicitud informe ejecución presupuestaria', 'Se solicita a DAF informe detallado de ejecución presupuestaria Q1', CURRENT_DATE + INTERVAL '30 days');

    -- CORE Session 2: Extraordinaria completada
    INSERT INTO core.session (committee_id, session_number, session_type_id, scheduled_at, started_at, ended_at, quorum_reached, location)
    VALUES (v_core_id, 902, v_session_type_ext, CURRENT_TIMESTAMP - INTERVAL '20 days', CURRENT_TIMESTAMP - INTERVAL '20 days', CURRENT_TIMESTAMP - INTERVAL '20 days' + INTERVAL '2 hours', true, 'Sala del Consejo Regional')
    RETURNING id INTO v_session_id;

    INSERT INTO core.minute (session_id, minute_number, approved_at, content, signed_by_id)
    VALUES (v_session_id, 'DEMO-R-ACTA-902', (CURRENT_DATE - INTERVAL '15 days')::date, 'Acta sesión extraordinaria N°902. Aprobación proyecto SNI Parque Urbano.', v_gobernador_person)
    RETURNING id INTO v_minute_id;

    INSERT INTO core.session_agreement (minute_id, agreement_number, subject, decision, due_date) VALUES
    (v_minute_id, 1, 'Aprobación proyecto Parque Urbano Ribera Chillán', 'Se aprueba el proyecto SNI por quórum calificado (>7K UTM)', CURRENT_DATE + INTERVAL '60 days'),
    (v_minute_id, 2, 'Requerimiento de informe ambiental', 'Se solicita informe de impacto ambiental complementario', CURRENT_DATE + INTERVAL '45 days');

    -- CORE Session 3: Próxima (programada)
    INSERT INTO core.session (committee_id, session_number, session_type_id, scheduled_at, location)
    VALUES (v_core_id, 903, v_session_type_ord, CURRENT_TIMESTAMP + INTERVAL '15 days', 'Sala del Consejo Regional')
    RETURNING id INTO v_session_id;

    INSERT INTO core.minute (session_id, minute_number, content)
    VALUES (v_session_id, 'DEMO-R-ACTA-903', 'Tabla: 1) Aprobación acta anterior 2) Informe ejecución presupuestaria 3) Aprobación FRIL Ñiquén')
    RETURNING id INTO v_minute_id;

    INSERT INTO core.session_agreement (minute_id, agreement_number, subject, decision) VALUES
    (v_minute_id, 1, 'Pendiente: aprobación FRIL Ñiquén', 'Por definir');

    -- Crisis Session 1: Completada
    INSERT INTO core.session (committee_id, session_number, session_type_id, scheduled_at, started_at, ended_at, quorum_reached, location)
    VALUES (v_crisis_id, 801, v_session_type_crisis, CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP - INTERVAL '30 days' + INTERVAL '1 hour', true, 'Gabinete del Gobernador')
    RETURNING id INTO v_session_id;

    INSERT INTO core.crisis_meeting (session_id, summary, organizer_id, started_at, finished_at)
    VALUES (v_session_id, 'Reunión de crisis por bloqueo de firma decreto SNI. Se resuelve intervención directa del Gobernador.',
            (SELECT id FROM core."user" WHERE email='secretario.core@goreos.cl'),
            CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP - INTERVAL '30 days' + INTERVAL '1 hour');

    INSERT INTO core.minute (session_id, minute_number, approved_at, content, signed_by_id)
    VALUES (v_session_id, 'DEMO-R-ACTA-CR-801', (CURRENT_DATE - INTERVAL '28 days')::date, 'Acta reunión de crisis. Se resolvió el bloqueo de firma.', v_secretario_person)
    RETURNING id INTO v_minute_id;

    INSERT INTO core.session_agreement (minute_id, agreement_number, subject, decision, due_date) VALUES
    (v_minute_id, 1, 'Resolución bloqueo firma decreto', 'Gobernador instruye firma inmediata previa V.B. jurídico especial', CURRENT_DATE - INTERVAL '25 days'),
    (v_minute_id, 2, 'Protocolo urgencia futura', 'DGI elaborará protocolo de escalamiento rápido', CURRENT_DATE + INTERVAL '30 days');

    -- Crisis Session 2: Programada
    INSERT INTO core.session (committee_id, session_number, session_type_id, scheduled_at, location)
    VALUES (v_crisis_id, 802, v_session_type_crisis, CURRENT_TIMESTAMP + INTERVAL '3 days', 'Gabinete del Gobernador')
    RETURNING id INTO v_session_id;

    INSERT INTO core.crisis_meeting (session_id, summary, organizer_id)
    VALUES (v_session_id, 'Reunión crisis por liquidez ejecutor SUBV8 — programa Huertos Punilla en riesgo.',
            (SELECT id FROM core."user" WHERE email='secretario.core@goreos.cl'));

    INSERT INTO core.minute (session_id, minute_number, content)
    VALUES (v_session_id, 'DEMO-R-ACTA-CR-802', 'Tabla: 1) Situación ejecutor 2) Medidas cautelares 3) Alternativas de continuidad')
    RETURNING id INTO v_minute_id;

    INSERT INTO core.session_agreement (minute_id, agreement_number, subject, decision) VALUES
    (v_minute_id, 1, 'Evaluación situación ejecutor', 'Por definir');

    -- TD Session 1: Completada
    INSERT INTO core.session (committee_id, session_number, session_type_id, scheduled_at, started_at, ended_at, location)
    VALUES (v_td_id, 701, v_session_type_ord, CURRENT_TIMESTAMP - INTERVAL '14 days', CURRENT_TIMESTAMP - INTERVAL '14 days', CURRENT_TIMESTAMP - INTERVAL '14 days' + INTERVAL '90 minutes', 'Sala DGI')
    RETURNING id INTO v_session_id;

    INSERT INTO core.minute (session_id, minute_number, approved_at, content)
    VALUES (v_session_id, 'DEMO-R-ACTA-TD-701', (CURRENT_DATE - INTERVAL '10 days')::date, 'Revisión avance Ley 21.180. Estado FEA: 45% actos. Próximos pasos: DS10.')
    RETURNING id INTO v_minute_id;

    INSERT INTO core.session_agreement (minute_id, agreement_number, subject, decision, due_date) VALUES
    (v_minute_id, 1, 'Calendario implementación DS10', 'TD elaborará cronograma de cumplimiento DS10', CURRENT_DATE + INTERVAL '20 days'),
    (v_minute_id, 2, 'Capacitación FEA divisiones', 'Programar taller FEA para DIFOI y DIDESO', CURRENT_DATE + INTERVAL '15 days');

END $$;


-- =============================================================================
-- TIER 9: RIESGOS + ALERTAS (~37 registros)
-- =============================================================================

-- 9.1 RISK (12) — 6 estados, 5 probabilidades
INSERT INTO core.risk (code, name, risk_type_id, probability_id, impact_id, status_id, subject_type, subject_id, mitigation_plan, identified_at, created_by_id) VALUES
('DEMO-R-RSK-0101', 'Déficit ejecución FNDR cierre año', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='FINANCIERO'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='ALTA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='BLOQUEA_PAGO'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='IDENTIFICADO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-006' LIMIT 1), NULL, CURRENT_DATE - INTERVAL '5 days', (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl')),
('DEMO-R-RSK-0102', 'Retraso obras pavimentación por lluvias', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='OPERACIONAL'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='MUY_ALTA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='RETRASA_OBRA'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='EN_EVALUACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007' LIMIT 1), 'Evaluar suspensión temporal hasta abril', CURRENT_DATE - INTERVAL '10 days', (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl')),
('DEMO-R-RSK-0103', 'Incumplimiento Ley 21.180 plazos', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='LEGAL'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='MEDIA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='INCUMPLIMIENTO_PLAZO'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='EN_MITIGACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-G06-003' LIMIT 1), 'Plan acelerado de digitalización FEA — meta 80% a dic 2026', CURRENT_DATE - INTERVAL '20 days', (SELECT id FROM core."user" WHERE email='td@goreos.cl')),
('DEMO-R-RSK-0104', 'Quiebre ejecutor programa SUBV8', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='FINANCIERO'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='ALTA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='RIESGO_RENDICION'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='EN_EVALUACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-004' LIMIT 1), 'Evaluar resciliación y recuperación de fondos', CURRENT_DATE - INTERVAL '3 days', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-RSK-0105', 'Vulnerabilidad ciberseguridad plataformas', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='TECNICO'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='BAJA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='OTRO'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='MITIGADO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRPD-001' LIMIT 1), 'Auditoría de seguridad completada, parches aplicados', CURRENT_DATE - INTERVAL '40 days', (SELECT id FROM core."user" WHERE email='td@goreos.cl')),
('DEMO-R-RSK-0106', 'Conflicto comunidad local obra Treguaco', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='REPUTACIONAL'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='MEDIA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='RETRASA_OBRA'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='ACEPTADO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-001' LIMIT 1), 'Riesgo aceptado — mediación en curso con dirigentes', CURRENT_DATE - INTERVAL '30 days', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl')),
('DEMO-R-RSK-0107', 'Brecha presupuestaria materiales FRIL', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='FINANCIERO'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='MEDIA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='BLOQUEA_PAGO'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='CERRADO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005' LIMIT 1), 'Modificación presupuestaria aprobada', CURRENT_DATE - INTERVAL '50 days', (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl')),
('DEMO-R-RSK-0108', 'Demora respuesta evaluador MDSF', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='OPERACIONAL'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='ALTA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='INCUMPLIMIENTO_PLAZO'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='EN_MITIGACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-004' LIMIT 1), 'Oficio recordatorio enviado a SEREMI MDSF', CURRENT_DATE - INTERVAL '15 days', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl')),
('DEMO-R-RSK-0109', 'Observación CGR en rendición convenio', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='LEGAL'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='MUY_BAJA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='RIESGO_RENDICION'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='IDENTIFICADO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-C33-003' LIMIT 1), NULL, CURRENT_DATE - INTERVAL '2 days', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl')),
('DEMO-R-RSK-0110', 'Rotación personal clave DIT', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='OPERACIONAL'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='MEDIA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='RETRASA_CONVENIO'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='IDENTIFICADO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-002' LIMIT 1), NULL, CURRENT_DATE - INTERVAL '8 days', (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl')),
('DEMO-R-RSK-0111', 'Impugnación licitación equipamiento seguridad', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='LEGAL'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='BAJA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='INCUMPLIMIENTO_PLAZO'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='EN_EVALUACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRPD-003' LIMIT 1), 'Asesoría jurídica evaluando recurso', CURRENT_DATE - INTERVAL '12 days', (SELECT id FROM core."user" WHERE email='juridico@goreos.cl')),
('DEMO-R-RSK-0112', 'Incendio forestal zona obras San Fabián', (SELECT id FROM ref.category WHERE scheme='risk_type' AND code='OPERACIONAL'), (SELECT id FROM ref.category WHERE scheme='risk_probability' AND code='MUY_BAJA'), (SELECT id FROM ref.category WHERE scheme='problem_impact' AND code='RETRASA_OBRA'), (SELECT id FROM ref.category WHERE scheme='risk_status' AND code='CERRADO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-005' LIMIT 1), 'Zona no afectada, obras continuaron normalmente', CURRENT_DATE - INTERVAL '60 days', (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'))
ON CONFLICT (code) DO NOTHING;

-- 9.2 ALERTS (25) — 13 alert_types, 4 severidades
INSERT INTO core.alert (alert_type_id, severity_id, subject_type, subject_id, message, triggered_at, created_by_id) VALUES
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='CUOTA_VENCIDA'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='CRITICO'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-013'), 'Cuota vencida convenio DEMO-R-AGR-013 — pago diferido hace 60 días', CURRENT_TIMESTAMP - INTERVAL '5 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='CUOTA_PROXIMA'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ATENCION'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-011'), 'Cuota próxima a vencer convenio DEMO-R-AGR-011 — 35 días restantes', CURRENT_TIMESTAMP - INTERVAL '2 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='CONVENIO_POR_VENCER'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ALTO'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-011'), 'Convenio DEMO-R-AGR-011 vence en 35 días', CURRENT_TIMESTAMP - INTERVAL '1 day', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='CONVENIO_POR_VENCER'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ATENCION'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-012'), 'Convenio DEMO-R-AGR-012 vence en 60 días', CURRENT_TIMESTAMP - INTERVAL '3 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='CONVENIO_VENCIDO'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='CRITICO'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-013'), 'Convenio DEMO-R-AGR-013 VENCIDO desde diciembre 2025', CURRENT_TIMESTAMP - INTERVAL '30 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='TRABAJO_VENCIDO'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ALTO'), 'core.operational_commitment', (SELECT id FROM core.operational_commitment WHERE code='DEMO-R-COM-018'), 'Compromiso DEMO-R-COM-018 vencido — rendición trimestral atrasada', CURRENT_TIMESTAMP - INTERVAL '10 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='TRABAJO_VENCIDO'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ALTO'), 'core.operational_commitment', (SELECT id FROM core.operational_commitment WHERE code='DEMO-R-COM-025'), 'Compromiso DEMO-R-COM-025 vencido — gestión resciliación atrasada', CURRENT_TIMESTAMP - INTERVAL '8 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='TRABAJO_BLOQUEADO_LARGO'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ATENCION'), 'core.operational_commitment', (SELECT id FROM core.operational_commitment WHERE code='DEMO-R-COM-001'), 'Compromiso DEMO-R-COM-001 pendiente hace >15 días', CURRENT_TIMESTAMP - INTERVAL '2 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='PROBLEMA_SIN_GESTION'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ALTO'), 'core.ipr_problem', (SELECT id FROM core.ipr_problem WHERE code='DEMO-R-PRB-003'), 'Problema legal DEMO-R-PRB-003 abierto >30 días sin gestión', CURRENT_TIMESTAMP - INTERVAL '5 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='RENDICION_PENDIENTE'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='CRITICO'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-009'), 'Rendición trimestral DEMO-R-AGR-009 observada hace 45 días', CURRENT_TIMESTAMP - INTERVAL '7 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='OBRA_SIN_PAGO'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ALTO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), 'Obra DEMO-R-SNI-007 sin estado de pago hace 60 días', CURRENT_TIMESTAMP - INTERVAL '4 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='PLAZO_LEGAL'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='CRITICO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-006'), 'Plazo legal CGR decreto DEMO-R-DEC-002 vence en 5 días', CURRENT_TIMESTAMP - INTERVAL '1 day', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='CDP_POR_VENCER'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ATENCION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-004'), 'CDP DEMO-R-CDP-003 asociado a FRIL-004 vence en 90 días', CURRENT_TIMESTAMP - INTERVAL '3 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='PRESUPUESTO_BAJO'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ALTO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-001'), 'Programa DEMO-R-BP-004 con ejecución bajo 40% al Q1', CURRENT_TIMESTAMP - INTERVAL '6 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
-- Alertas atendidas/resueltas para variedad
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='CUOTA_VENCIDA'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ALTO'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-014'), 'Cuota atrasada convenio DEMO-R-AGR-014 — resuelta', CURRENT_TIMESTAMP - INTERVAL '20 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='PROBLEMA_SIN_GESTION'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ATENCION'), 'core.ipr_problem', (SELECT id FROM core.ipr_problem WHERE code='DEMO-R-PRB-005'), 'Problema administrativo DEMO-R-PRB-005 ahora en gestión', CURRENT_TIMESTAMP - INTERVAL '12 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='RENDICION_PENDIENTE'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ATENCION'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-010'), 'Rendición DEMO-R-AGR-010 aprobada', CURRENT_TIMESTAMP - INTERVAL '25 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='CONVENIO_POR_VENCER'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='INFO'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-016'), 'Convenio DEMO-R-AGR-016 con 400 días de vigencia restante', CURRENT_TIMESTAMP - INTERVAL '1 day', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
-- Alertas por riesgo alto/muy_alto (auto-alert)
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='PRESUPUESTO_BAJO'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='CRITICO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-001'), 'Riesgo ALTA: Déficit ejecución FNDR — requiere atención inmediata', CURRENT_TIMESTAMP - INTERVAL '5 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='TRABAJO_BLOQUEADO_LARGO'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ALTO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-004'), 'IPR DEMO-R-SNI-004 en evaluación >45 días sin avance', CURRENT_TIMESTAMP - INTERVAL '3 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
-- Más para completar 25
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='OBRA_SIN_PAGO'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ATENCION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), 'FRIL-005 sin EP hace 30 días', CURRENT_TIMESTAMP - INTERVAL '8 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='CUOTA_PROXIMA'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='INFO'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-006'), 'Próxima cuota convenio DEMO-R-AGR-006 en 30 días', CURRENT_TIMESTAMP - INTERVAL '1 day', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='PLAZO_LEGAL'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ALTO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-G06-001'), 'Vencimiento plazo admisibilidad estudio DEMO-R-G06-001', CURRENT_TIMESTAMP - INTERVAL '2 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='CDP_POR_VENCER'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ATENCION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-002'), 'CDP asociado a transferencia UBB vence fin de año', CURRENT_TIMESTAMP - INTERVAL '4 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl')),
((SELECT id FROM ref.category WHERE scheme='alert_type' AND code='PRESUPUESTO_BAJO'), (SELECT id FROM ref.category WHERE scheme='alert_level' AND code='ATENCION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-003'), 'Programa DIDESO con ejecución 40% — necesita acelerar', CURRENT_TIMESTAMP - INTERVAL '6 days', (SELECT id FROM core."user" WHERE email='admin@goreos.cl'))
ON CONFLICT DO NOTHING;


-- =============================================================================
-- TIER 10: CICLO DE VIDA AVANZADO (~7 registros)
-- =============================================================================

-- 10.1 IPR_MODIFICATION (4) — 4 estados FSM
INSERT INTO core.ipr_modification (ipr_id, code, modification_type_id, status_id, description, justification, field_changed, old_value, new_value, amount_delta, requested_by_id) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), 'DEMO-R-MOD-001', (SELECT id FROM ref.category WHERE scheme='modification_type' AND code='PRESUPUESTO'), (SELECT id FROM ref.category WHERE scheme='modification_status' AND code='SOLICITADA'), 'Incremento presupuestario por alza de materiales', 'IPC acumulado 8.5% desde licitación', 'metadata.monto_total', '5800000000', '6200000000', 400000000, (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-005'), 'DEMO-R-MOD-002', (SELECT id FROM ref.category WHERE scheme='modification_type' AND code='PLAZO'), (SELECT id FROM ref.category WHERE scheme='modification_status' AND code='EN_REVISION'), 'Extensión de plazo 30 días por lluvia', 'Informe meteorológico adjunto', 'max_execution_months', '6', '7', NULL, (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-004'), 'DEMO-R-MOD-003', (SELECT id FROM ref.category WHERE scheme='modification_type' AND code='ALCANCE'), (SELECT id FROM ref.category WHERE scheme='modification_status' AND code='APROBADA'), 'Ampliar cobertura a 3 comunas adicionales', 'Demanda excede oferta en comunas originales', 'intended_outcome', 'Cobertura 5 comunas', 'Cobertura 8 comunas', NULL, (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-003'), 'DEMO-R-MOD-004', (SELECT id FROM ref.category WHERE scheme='modification_type' AND code='EJECUTOR'), (SELECT id FROM ref.category WHERE scheme='modification_status' AND code='RECHAZADA'), 'Cambio de ejecutor por incumplimiento', 'Ejecutor original no cuenta con equipo técnico suficiente', 'executor_id', 'SERNATUR', 'Municipalidad Chillán', NULL, (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 10.2 IPR_CLOSURE (2) — UNIQUE per IPR, vinculado a CERRADO
INSERT INTO core.ipr_closure (ipr_id, closure_date, closure_report, physical_completion, financial_completion, final_amount, signed_by_id, signed_at, created_by_id) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), CURRENT_DATE - INTERVAL '30 days', 'Cierre administrativo multicancha techada Yungay. Obra ejecutada al 100%, sin observaciones pendientes.', 100.00, 98.50, 876000000, (SELECT id FROM core."user" WHERE email='jefe.dipir@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '28 days', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl')),
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-G06-004'), CURRENT_DATE - INTERVAL '45 days', 'Cierre estudio zonificación borde costero Itata. Productos entregados al MDSF y aprobados.', 100.00, 100.00, 210000000, (SELECT id FROM core."user" WHERE email='jefe.diplade@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '43 days', (SELECT id FROM core."user" WHERE email='analista.diplade@goreos.cl'))
ON CONFLICT DO NOTHING;

-- 10.2b: Vincular cierres con actos administrativos
UPDATE core.ipr_closure SET closure_act_id = (
    SELECT id FROM core.administrative_act WHERE act_number = 'DEMO-R-RES-009'
)
WHERE ipr_id = (SELECT id FROM core.ipr WHERE codigo_bip = 'DEMO-R-SNI-008')
  AND closure_act_id IS NULL;

-- 10.3 IPR_EXPOST_EVALUATION (1) — post-CERRADO, 4 dimensiones
INSERT INTO core.ipr_expost_evaluation (ipr_id, evaluation_date, evaluator_id, evaluation_type_id, impact_score, sustainability_score, efficiency_score, effectiveness_score, overall_rating_id, findings, recommendations, lessons_learned) VALUES
((SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), CURRENT_DATE - INTERVAL '15 days',
 (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'),
 (SELECT id FROM ref.category WHERE scheme='expost_eval_type' AND code='SIMPLIFICADA'),
 85.00, 78.00, 92.00, 88.00,
 (SELECT id FROM ref.category WHERE scheme='expost_rating' AND code='SATISFACTORIO'),
 'Obra cumplió objetivos de cobertura deportiva. Uso comunitario efectivo.',
 'Considerar mantenimiento preventivo anual. Evaluar ampliación gradería.',
 'Modelo de cogestión municipal-GORE funciona bien para instalaciones deportivas.')
ON CONFLICT DO NOTHING;


-- =============================================================================
-- TIER 11: AUDIT TRAIL (~40 registros)
-- =============================================================================

-- txn.event: 40 eventos distribuidos en los últimos 30 días
INSERT INTO txn.event (event_type_id, subject_type, subject_id, actor_id, occurred_at, data) VALUES
-- LOGIN events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='LOGIN'), 'core.user', (SELECT id FROM core."user" WHERE email='admin@goreos.cl'), (SELECT id FROM core."user" WHERE email='admin@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '1 day', '{"ip": "10.0.1.50"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='LOGIN'), 'core.user', (SELECT id FROM core."user" WHERE email='jefe.dipir@goreos.cl'), (SELECT id FROM core."user" WHERE email='jefe.dipir@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '1 day', '{"ip": "10.0.2.15"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='LOGIN'), 'core.user', (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'), (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '2 days', '{"ip": "10.0.3.22"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='LOGIN'), 'core.user', (SELECT id FROM core."user" WHERE email='gobernador@goreos.cl'), (SELECT id FROM core."user" WHERE email='gobernador@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '3 days', '{"ip": "10.0.1.1"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='LOGIN_FAILED'), 'core.user', (SELECT id FROM core."user" WHERE email='admin@goreos.cl'), NULL, CURRENT_TIMESTAMP - INTERVAL '5 days', '{"ip": "192.168.1.100", "reason": "invalid_password"}'::jsonb),
-- CREACION events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='CREACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-001'), (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '5 days', '{"codigo_bip": "DEMO-R-SNI-001"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='CREACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-001'), (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '3 days', '{"codigo_bip": "DEMO-R-FRIL-001"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='CREACION'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-006'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '120 days', '{"agreement_number": "DEMO-R-AGR-006"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='CREACION'), 'core.risk', (SELECT id FROM core.risk WHERE code='DEMO-R-RSK-0101'), (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '5 days', '{"risk_code": "DEMO-R-RSK-0101"}'::jsonb),
-- STATE_TRANSITION events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='STATE_TRANSITION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '120 days', '{"from": "FORMALIZADO", "to": "EN_OBRA"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='STATE_TRANSITION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '30 days', '{"from": "EN_RENDICION", "to": "CERRADO"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='STATE_TRANSITION'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-006'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '120 days', '{"from": "FIRMADO_CONTRAPARTE", "to": "VIGENTE"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='STATE_TRANSITION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-TRF-004'), (SELECT id FROM core."user" WHERE email='jefe.difoi@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '10 days', '{"from": "EN_EJECUCION", "to": "TERMINADO_ANTICIPADAMENTE"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='STATE_TRANSITION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRPD-004'), (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '60 days', '{"from": "EN_EVALUACION", "to": "ANULADO"}'::jsonb),
-- CDP / COMPROMISO events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='CDP'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-006'), (SELECT id FROM core."user" WHERE email='jefe.daf@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '10 days', '{"cdp": "DEMO-R-CDP-001", "amount": 160000000}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='PAGO'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-006'), (SELECT id FROM core."user" WHERE email='jefe.daf@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '65 days', '{"installment": 1, "amount": 1933333333}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='COMPROMISO'), 'core.operational_commitment', (SELECT id FROM core.operational_commitment WHERE code='DEMO-R-COM-001' LIMIT 1), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '8 days', '{"action": "created"}'::jsonb),
-- ALERT events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='ALERT_CREATED'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM core."user" WHERE email='admin@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '4 days', '{"alert_type": "OBRA_SIN_PAGO", "severity": "ALTO"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='ALERT_ATTENDED'), 'core.agreement', (SELECT id FROM core.agreement WHERE agreement_number='DEMO-R-AGR-014'), (SELECT id FROM core."user" WHERE email='jefe.daf@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '18 days', '{"action": "resolved"}'::jsonb),
-- RISK events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='RISK_CREATED'), 'core.risk', (SELECT id FROM core.risk WHERE code='DEMO-R-RSK-0102'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '10 days', '{"risk_code": "DEMO-R-RSK-0102", "probability": "MUY_ALTA"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='RISK_STATUS_CHANGE'), 'core.risk', (SELECT id FROM core.risk WHERE code='DEMO-R-RSK-0105'), (SELECT id FROM core."user" WHERE email='td@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '38 days', '{"from": "EN_MITIGACION", "to": "MITIGADO"}'::jsonb),
-- ESCALATION events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='ESCALATION_CREATED'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '14 days', '{"escalation_code": "DEMO-R-ESC-105", "level": "NIVEL_2"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='ESCALATION_STATUS_CHANGE'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-005'), (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '10 days', '{"from": "EN_GESTION", "to": "RESUELTO"}'::jsonb),
-- DECISION events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='DECISION_CREATED'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRIL-001'), (SELECT id FROM core."user" WHERE email='jefe.dgi@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '21 days', '{"decision": "DEMO-R-DEC-A01"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='DECISION_STATUS_CHANGE'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-G06-003'), (SELECT id FROM core."user" WHERE email='td@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '15 days', '{"from": "PENDIENTE", "to": "COMPLETADA"}'::jsonb),
-- MEETING events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='MEETING_STARTED'), 'core.committee', (SELECT id FROM core.committee WHERE code='CONSEJO-REGIONAL'), (SELECT id FROM core."user" WHERE email='secretario.core@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '20 days', '{"session_number": 902}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='MEETING_ENDED'), 'core.committee', (SELECT id FROM core.committee WHERE code='CONSEJO-REGIONAL'), (SELECT id FROM core."user" WHERE email='secretario.core@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '20 days' + INTERVAL '2 hours', '{"session_number": 902, "agreements": 2}'::jsonb),
-- APROBACION events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='APROBACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-003'), (SELECT id FROM core."user" WHERE email='gobernador@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '20 days', '{"type": "CORE_approval", "session": 902}'::jsonb),
-- MODIFICACION events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='MODIFICACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '8 days', '{"modification": "DEMO-R-MOD-001", "type": "PRESUPUESTO"}'::jsonb),
-- ACCESO events
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='ACCESO'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-007'), (SELECT id FROM core."user" WHERE email='control.gestion@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '2 days', '{"action": "view_detail"}'::jsonb),
-- Additional variety
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='CIERRE'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-008'), (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '30 days', '{"closure_type": "normal"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='ASIGNACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SNI-004'), (SELECT id FROM core."user" WHERE email='jefe.dipir@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '45 days', '{"assigned_to": "analista.dipir@goreos.cl"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='PASSWORD_CHANGED'), 'core.user', (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'), (SELECT id FROM core."user" WHERE email='analista.dipir@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '25 days', '{}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='STATE_TRANSITION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-EXT-004'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '6 days', '{"from": "ADJUDICADO", "to": "CONTRATO_FIRMADO"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='STATE_TRANSITION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-C33-004'), (SELECT id FROM core."user" WHERE email='jefe.dit@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '20 days', '{"from": "EN_RENDICION", "to": "RENDICION_APROBADA"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='CREACION'), 'core.operational_commitment', (SELECT id FROM core.operational_commitment WHERE code='DEMO-R-COM-005' LIMIT 1), (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '15 days', '{"code": "DEMO-R-COM-005"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='ACTUALIZACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-SUBV8-004'), (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '12 days', '{"field": "metadata.monto_total"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='LOGIN'), 'core.user', (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl'), (SELECT id FROM core."user" WHERE email='rtf.daf@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '1 day', '{"ip": "10.0.4.10"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='LOGIN'), 'core.user', (SELECT id FROM core."user" WHERE email='juridico@goreos.cl'), (SELECT id FROM core."user" WHERE email='juridico@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '2 days', '{"ip": "10.0.4.20"}'::jsonb),
((SELECT id FROM ref.category WHERE scheme='event_type' AND code='CREACION'), 'core.ipr', (SELECT id FROM core.ipr WHERE codigo_bip='DEMO-R-FRPD-001'), (SELECT id FROM core."user" WHERE email='jefe.dideso@goreos.cl'), CURRENT_TIMESTAMP - INTERVAL '2 days', '{"codigo_bip": "DEMO-R-FRPD-001"}'::jsonb)
ON CONFLICT DO NOTHING;


COMMIT;

-- =============================================================================
-- VERIFICACIÓN (ejecutar manualmente):
-- =============================================================================
-- SELECT 'IPRs' AS entity, COUNT(*) FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Parties', COUNT(*) FROM core.ipr_party ip JOIN core.ipr i ON ip.ipr_id=i.id WHERE i.codigo_bip LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Territories', COUNT(*) FROM core.ipr_territory it JOIN core.ipr i ON it.ipr_id=i.id WHERE i.codigo_bip LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Milestones', COUNT(*) FROM core.ipr_milestone im JOIN core.ipr i ON im.ipr_id=i.id WHERE i.codigo_bip LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Evaluations', COUNT(*) FROM core.evaluation_assignment ea JOIN core.ipr i ON ea.ipr_id=i.id WHERE i.codigo_bip LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Progress', COUNT(*) FROM core.progress_report pr JOIN core.ipr i ON pr.ipr_id=i.id WHERE i.codigo_bip LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Budget Progs', COUNT(*) FROM core.budget_program WHERE code LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'CDPs', COUNT(*) FROM core.budget_commitment WHERE commitment_number LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Agreements', COUNT(*) FROM core.agreement WHERE agreement_number LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Installments', COUNT(*) FROM core.agreement_installment ai JOIN core.agreement a ON ai.agreement_id=a.id WHERE a.agreement_number LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Renditions', COUNT(*) FROM core.rendition r JOIN core.agreement a ON r.agreement_id=a.id WHERE a.agreement_number LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Admin Acts', COUNT(*) FROM core.administrative_act WHERE act_number LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Commitments', COUNT(*) FROM core.operational_commitment WHERE code LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Problems', COUNT(*) FROM core.ipr_problem WHERE code LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'DGI Indicators', COUNT(*) FROM core.dgi_indicator WHERE code LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'DGI Processes', COUNT(*) FROM core.dgi_process WHERE code LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'DGI Initiatives', COUNT(*) FROM core.dgi_initiative WHERE code LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Risks', COUNT(*) FROM core.risk WHERE code LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Alerts', COUNT(*) FROM core.alert WHERE message LIKE 'DEMO-R-%' OR message LIKE '%DEMO-R-%'
-- UNION ALL SELECT 'Modifications', COUNT(*) FROM core.ipr_modification WHERE code LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Closures', COUNT(*) FROM core.ipr_closure ic JOIN core.ipr i ON ic.ipr_id=i.id WHERE i.codigo_bip LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'ExPost', COUNT(*) FROM core.ipr_expost_evaluation ep JOIN core.ipr i ON ep.ipr_id=i.id WHERE i.codigo_bip LIKE 'DEMO-R-%';
