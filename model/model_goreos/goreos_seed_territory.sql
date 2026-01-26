-- ============================================================================
-- GORE_OS v2.0 - SEED DATA TERRITORIAL
-- ============================================================================
-- Archivo: goreos_seed_territory.sql
-- Descripción: Datos territoriales Región de Ñuble (código 16)
-- Generado: 2026-01-26
-- Fuente: División Político-Administrativa de Chile (INE)
-- ============================================================================

-- ============================================================================
--    REGIÓN DE ÑUBLE (código CUT: 16)
-- ============================================================================
-- La Región de Ñuble fue creada el 5 de septiembre de 2018 (Ley 21.033)
-- Capital regional: Chillán
-- Superficie: 13.178,5 km²
-- Población estimada: ~511.551 habitantes (Censo 2017)
-- ============================================================================

-- Obtener IDs de categorías de territorio
DO $$
DECLARE
    v_region_type_id INTEGER;
    v_provincia_type_id INTEGER;
    v_comuna_type_id INTEGER;
    v_region_id INTEGER;
    v_prov_diguillin_id INTEGER;
    v_prov_itata_id INTEGER;
    v_prov_punilla_id INTEGER;
BEGIN
    -- Obtener tipos de territorio
    SELECT id INTO v_region_type_id FROM ref.category WHERE scheme = 'territory_type' AND code = 'REGION';
    SELECT id INTO v_provincia_type_id FROM ref.category WHERE scheme = 'territory_type' AND code = 'PROVINCIA';
    SELECT id INTO v_comuna_type_id FROM ref.category WHERE scheme = 'territory_type' AND code = 'COMUNA';

    -- ========================================================================
    -- REGIÓN
    -- ========================================================================
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16', 'Región de Ñuble', v_region_type_id, NULL, 13178.5, 511551)
    RETURNING id INTO v_region_id;

    -- ========================================================================
    -- PROVINCIAS (3)
    -- ========================================================================

    -- Provincia de Diguillín
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('161', 'Diguillín', v_provincia_type_id, v_region_id, 4568.4, 310826)
    RETURNING id INTO v_prov_diguillin_id;

    -- Provincia de Itata
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('162', 'Itata', v_provincia_type_id, v_region_id, 2644.5, 52082)
    RETURNING id INTO v_prov_itata_id;

    -- Provincia de Punilla
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('163', 'Punilla', v_provincia_type_id, v_region_id, 5965.6, 148643)
    RETURNING id INTO v_prov_punilla_id;

    -- ========================================================================
    -- COMUNAS PROVINCIA DE DIGUILLÍN (9 comunas)
    -- ========================================================================

    -- Chillán (capital regional)
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16101', 'Chillán', v_comuna_type_id, v_prov_diguillin_id, 511.2, 184739);

    -- Bulnes
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16102', 'Bulnes', v_comuna_type_id, v_prov_diguillin_id, 423.5, 21307);

    -- Chillán Viejo
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16103', 'Chillán Viejo', v_comuna_type_id, v_prov_diguillin_id, 292.3, 35684);

    -- El Carmen
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16104', 'El Carmen', v_comuna_type_id, v_prov_diguillin_id, 666.8, 12364);

    -- Pemuco
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16105', 'Pemuco', v_comuna_type_id, v_prov_diguillin_id, 561.8, 8275);

    -- Pinto
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16106', 'Pinto', v_comuna_type_id, v_prov_diguillin_id, 1164.1, 11426);

    -- Quillón
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16107', 'Quillón', v_comuna_type_id, v_prov_diguillin_id, 401.5, 16263);

    -- San Ignacio
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16108', 'San Ignacio', v_comuna_type_id, v_prov_diguillin_id, 359.9, 14946);

    -- Yungay
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16109', 'Yungay', v_comuna_type_id, v_prov_diguillin_id, 823.6, 17822);

    -- ========================================================================
    -- COMUNAS PROVINCIA DE ITATA (7 comunas)
    -- ========================================================================

    -- Quirihue (capital provincial)
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16201', 'Quirihue', v_comuna_type_id, v_prov_itata_id, 589.4, 11806);

    -- Cobquecura
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16202', 'Cobquecura', v_comuna_type_id, v_prov_itata_id, 569.8, 5169);

    -- Coelemu
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16203', 'Coelemu', v_comuna_type_id, v_prov_itata_id, 324.5, 16623);

    -- Ninhue
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16204', 'Ninhue', v_comuna_type_id, v_prov_itata_id, 401.5, 5282);

    -- Portezuelo
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16205', 'Portezuelo', v_comuna_type_id, v_prov_itata_id, 287.2, 5102);

    -- Ránquil
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16206', 'Ránquil', v_comuna_type_id, v_prov_itata_id, 249.1, 5679);

    -- Treguaco
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16207', 'Treguaco', v_comuna_type_id, v_prov_itata_id, 223.0, 4776);

    -- ========================================================================
    -- COMUNAS PROVINCIA DE PUNILLA (5 comunas)
    -- ========================================================================

    -- San Carlos (capital provincial)
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16301', 'San Carlos', v_comuna_type_id, v_prov_punilla_id, 874.5, 54841);

    -- Coihueco
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16302', 'Coihueco', v_comuna_type_id, v_prov_punilla_id, 1782.8, 26037);

    -- Ñiquén
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16303', 'Ñiquén', v_comuna_type_id, v_prov_punilla_id, 496.6, 11221);

    -- San Fabián
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16304', 'San Fabián', v_comuna_type_id, v_prov_punilla_id, 1510.2, 3688);

    -- San Nicolás
    INSERT INTO core.territory (code, name, territory_type_id, parent_id, area_km2, population)
    VALUES ('16305', 'San Nicolás', v_comuna_type_id, v_prov_punilla_id, 575.3, 11282);

    RAISE NOTICE 'Territorio Ñuble insertado: 1 región, 3 provincias, 21 comunas';

END $$;

-- ============================================================================
-- INDICADORES TERRITORIALES BASE (ejemplos)
-- ============================================================================
-- Estos indicadores pueden ser actualizados con datos reales del INE, SINIM, etc.

DO $$
DECLARE
    v_demo_type_id INTEGER;
    v_eco_type_id INTEGER;
    v_social_type_id INTEGER;
    v_region_id INTEGER;
BEGIN
    -- Obtener tipos de indicador
    SELECT id INTO v_demo_type_id FROM ref.category WHERE scheme = 'indicator_type' AND code = 'DEMOGRAFICO';
    SELECT id INTO v_eco_type_id FROM ref.category WHERE scheme = 'indicator_type' AND code = 'ECONOMICO';
    SELECT id INTO v_social_type_id FROM ref.category WHERE scheme = 'indicator_type' AND code = 'SOCIAL';

    -- Obtener ID de la región
    SELECT id INTO v_region_id FROM core.territory WHERE code = '16';

    -- Indicadores demográficos región
    -- NOTA: DDL usa code (NOT NULL), numeric_value, fiscal_year (no value/unit/year)
    INSERT INTO core.territorial_indicator (code, territory_id, indicator_type_id, name, numeric_value, fiscal_year, source)
    VALUES
        ('IND-16-DEMO-001', v_region_id, v_demo_type_id, 'Población Total', 511551, 2017, 'INE Censo 2017'),
        ('IND-16-DEMO-002', v_region_id, v_demo_type_id, 'Densidad Poblacional', 38.8, 2017, 'INE Censo 2017'),
        ('IND-16-DEMO-003', v_region_id, v_demo_type_id, 'Índice de Masculinidad', 98.2, 2017, 'INE Censo 2017'),
        ('IND-16-DEMO-004', v_region_id, v_demo_type_id, 'Población Urbana', 71.5, 2017, 'INE Censo 2017'),
        ('IND-16-DEMO-005', v_region_id, v_demo_type_id, 'Población Rural', 28.5, 2017, 'INE Censo 2017');

    -- Indicadores económicos región
    INSERT INTO core.territorial_indicator (code, territory_id, indicator_type_id, name, numeric_value, fiscal_year, source)
    VALUES
        ('IND-16-ECO-001', v_region_id, v_eco_type_id, 'PIB Regional', 2850000, 2022, 'Banco Central'),
        ('IND-16-ECO-002', v_region_id, v_eco_type_id, 'Participación PIB Nacional', 1.2, 2022, 'Banco Central'),
        ('IND-16-ECO-003', v_region_id, v_eco_type_id, 'Tasa de Desempleo', 7.8, 2023, 'INE'),
        ('IND-16-ECO-004', v_region_id, v_eco_type_id, 'Ingreso Promedio Hogar', 850000, 2022, 'CASEN');

    -- Indicadores sociales región
    INSERT INTO core.territorial_indicator (code, territory_id, indicator_type_id, name, numeric_value, fiscal_year, source)
    VALUES
        ('IND-16-SOC-001', v_region_id, v_social_type_id, 'Tasa de Pobreza', 12.3, 2022, 'CASEN'),
        ('IND-16-SOC-002', v_region_id, v_social_type_id, 'Índice de Desarrollo Humano', 0.78, 2021, 'PNUD'),
        ('IND-16-SOC-003', v_region_id, v_social_type_id, 'Cobertura Agua Potable', 98.5, 2022, 'SISS'),
        ('IND-16-SOC-004', v_region_id, v_social_type_id, 'Cobertura Alcantarillado', 92.1, 2022, 'SISS');

    RAISE NOTICE 'Indicadores territoriales base insertados';

END $$;

-- ============================================================================
-- ORGANIZACIONES BASE GORE ÑUBLE
-- ============================================================================

DO $$
DECLARE
    v_gore_type_id INTEGER;
    v_division_type_id INTEGER;
    v_gore_id INTEGER;
BEGIN
    -- Obtener tipos de organización
    SELECT id INTO v_gore_type_id FROM ref.category WHERE scheme = 'org_type' AND code = 'GORE';
    SELECT id INTO v_division_type_id FROM ref.category WHERE scheme = 'org_type' AND code = 'DIVISION';

    -- GORE Ñuble
    -- NOTA: DDL de core.organization no tiene territory_id ni is_active
    INSERT INTO core.organization (code, name, org_type_id, parent_id)
    VALUES ('GORE-NUBLE', 'Gobierno Regional de Ñuble', v_gore_type_id, NULL)
    RETURNING id INTO v_gore_id;

    -- Divisiones del GORE
    INSERT INTO core.organization (code, name, org_type_id, parent_id) VALUES
        ('DIPIR', 'División de Planificación e Inversión Regional', v_division_type_id, v_gore_id),
        ('DAF', 'División de Administración y Finanzas', v_division_type_id, v_gore_id),
        ('DIFOT', 'División de Fomento e Industria', v_division_type_id, v_gore_id),
        ('DIDERSO', 'División de Desarrollo Social y Humano', v_division_type_id, v_gore_id),
        ('DIIAP', 'División de Infraestructura y Arquitectura Pública', v_division_type_id, v_gore_id),
        ('DIJ', 'División Jurídica', v_division_type_id, v_gore_id),
        ('DIDECO', 'División de Control de Gestión', v_division_type_id, v_gore_id),
        ('GABINETE', 'Gabinete del Gobernador', v_division_type_id, v_gore_id);

    RAISE NOTICE 'Organizaciones GORE Ñuble insertadas: 1 GORE, 8 divisiones';

END $$;

-- ============================================================================
-- FIN SEED DATA TERRITORIAL
-- ============================================================================
-- Total territorios: 25 (1 región + 3 provincias + 21 comunas)
-- Total indicadores: 13 (base regional)
-- Total organizaciones: 9 (1 GORE + 8 divisiones)
-- ============================================================================
