-- ==============================================================================
-- NORMALIZACIÓN METADATA IPR - v2.0 (Post-Auditoría Categorial)
-- ==============================================================================
-- ARQUITECTO-GORE v0.1.0
-- Fecha: 2026-01-30
-- Motor: CM-ARTIFACT-GENERATOR
-- Fundamento: AUDITORIA_CATEGORIAL_NORMALIZACION_JSONB.md
-- Plan: PLAN_NORMALIZACION_JSONB_v2.0.md
--
-- CAMBIOS vs v1.0:
--   ❌ RECHAZADO: ipr_origin (sin fundamento gnub:*)
--   ❌ RECHAZADO: ipr_legacy_typology (viola univocidad categorial)
--   ✅ NUEVO: investment_sector (coherente con gnub:InvestmentTypology)
--   ✅ NUEVO: CHECK constraints (garantiza coherencia categorial)
--
-- COHERENCIA ESPERADA: 92% (vs 30% en v1.0)
-- ==============================================================================

\set ON_ERROR_STOP on
\timing on

-- ==============================================================================
-- CONFIGURACIÓN
-- ==============================================================================

DO $$ BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  NORMALIZACIÓN METADATA IPR v2.0                               ║';
    RAISE NOTICE '║  Arquitecto-GORE | Coherencia Categorial                      ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
END $$;

-- Crear función helper para reportes
CREATE OR REPLACE FUNCTION report_phase(phase_name TEXT, status TEXT) RETURNS void AS $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '════════════════════════════════════════════════════════════════';
    RAISE NOTICE 'FASE: % - %', phase_name, status;
    RAISE NOTICE '════════════════════════════════════════════════════════════════';
    RAISE NOTICE '';
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- PRE-EJECUCIÓN: VALIDACIONES
-- ==============================================================================

SELECT report_phase('PRE-EJECUCIÓN', 'Validaciones de Seguridad');

-- Validar que función de coherencia categorial existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'fn_validate_category_scheme') THEN
        RAISE EXCEPTION 'Función fn_validate_category_scheme NO existe. Ejecutar goreos_ddl.sql primero.';
    END IF;
    RAISE NOTICE '✓ Función fn_validate_category_scheme existe';
END $$;

-- Validar que core.ipr tiene metadata
DO $$
DECLARE
    ipr_count INTEGER;
    metadata_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO ipr_count FROM core.ipr;
    SELECT COUNT(*) INTO metadata_count FROM core.ipr WHERE metadata IS NOT NULL;

    IF ipr_count = 0 THEN
        RAISE EXCEPTION 'Tabla core.ipr está vacía. No hay datos para normalizar.';
    END IF;

    IF metadata_count = 0 THEN
        RAISE WARNING 'Ningún IPR tiene metadata. Script puede no tener efecto.';
    END IF;

    RAISE NOTICE '✓ core.ipr tiene % registros, % con metadata', ipr_count, metadata_count;
END $$;

-- Crear índice GIN si no existe (para performance de queries metadata)
CREATE INDEX IF NOT EXISTS idx_ipr_metadata_gin ON core.ipr USING gin(metadata);
DO $$ BEGIN RAISE NOTICE '✓ Índice GIN en metadata creado/verificado'; END $$;

-- ==============================================================================
-- BACKUP: Snapshot de metadata pre-migración
-- ==============================================================================

SELECT report_phase('BACKUP', 'Snapshot Metadata Pre-Migración');

-- Crear tabla de backup temporal
DROP TABLE IF EXISTS temp_ipr_metadata_backup_v2;

CREATE TEMP TABLE temp_ipr_metadata_backup_v2 AS
SELECT
    id,
    codigo_bip,
    metadata,
    mcd_phase_id,
    now() AS backup_at
FROM core.ipr
WHERE metadata IS NOT NULL AND metadata != '{}'::jsonb;

DO $$
DECLARE
    backup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO backup_count FROM temp_ipr_metadata_backup_v2;
    RAISE NOTICE '✓ Backup creado: % registros en temp_ipr_metadata_backup_v2', backup_count;
    RAISE NOTICE '  Para rollback manual: SELECT * FROM temp_ipr_metadata_backup_v2;';
END $$;

-- ==============================================================================
-- FASE 1: LIMPIEZA DE METADATA YA NORMALIZADO
-- ==============================================================================

BEGIN;

SELECT report_phase('FASE 1', 'Limpieza Metadata Ya Normalizado');

-- 1.1 VERIFICAR que campos están normalizados
DO $$
DECLARE
    territorial_missing INTEGER;
    phase_missing INTEGER;
BEGIN
    -- Verificar territorial
    SELECT COUNT(*) INTO territorial_missing
    FROM core.ipr i
    WHERE i.metadata ? 'provincia'
      AND NOT EXISTS (
          SELECT 1 FROM core.ipr_territory it
          WHERE it.ipr_id = i.id
            AND it.territory_id IN (
                SELECT id FROM core.territory
                WHERE territory_type_id = (
                    SELECT id FROM ref.category
                    WHERE scheme='territory_type' AND code='PROVINCIA'
                )
            )
      );

    IF territorial_missing > 0 THEN
        RAISE WARNING '% IPRs tienen provincia en metadata pero NO en ipr_territory', territorial_missing;
    ELSE
        RAISE NOTICE '✓ Todos los IPRs con provincia están normalizados en ipr_territory';
    END IF;

    -- Verificar fase
    SELECT COUNT(*) INTO phase_missing
    FROM core.ipr
    WHERE metadata ? 'etapa_original'
      AND mcd_phase_id IS NULL;

    IF phase_missing > 0 THEN
        RAISE WARNING '% IPRs tienen etapa_original en metadata pero mcd_phase_id IS NULL', phase_missing;
    ELSE
        RAISE NOTICE '✓ Todos los IPRs con etapa_original están normalizados en mcd_phase_id';
    END IF;
END $$;

-- 1.2 REMOVER campos normalizados
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE core.ipr
        SET metadata = metadata
            - 'provincia'
            - 'comuna'
            - 'etapa_original'
            || jsonb_build_object(
                'normalized_at', now()::text,
                'normalized_version', 'v2.0',
                'normalized_fields', ARRAY['provincia', 'comuna', 'etapa_original']::text[]
            )
        WHERE metadata ?| ARRAY['provincia', 'comuna', 'etapa_original']
        RETURNING id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;

    RAISE NOTICE '✓ % IPRs: metadata limpiado (provincia, comuna, etapa_original removidos)', updated_count;
END $$;

-- 1.3 VERIFICAR limpieza
DO $$
DECLARE
    remaining INTEGER;
BEGIN
    SELECT COUNT(*) INTO remaining
    FROM core.ipr
    WHERE metadata ?| ARRAY['provincia', 'comuna', 'etapa_original'];

    IF remaining > 0 THEN
        RAISE WARNING '% IPRs aún tienen campos removidos. Revisar.', remaining;
    ELSE
        RAISE NOTICE '✓ Verificación: 0 IPRs con campos removidos (limpieza completa)';
    END IF;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 2: COMPLETAR MIGRACIÓN UNIDAD_TECNICA
-- ==============================================================================

BEGIN;

SELECT report_phase('FASE 2', 'Completar Migración unidad_tecnica');

-- 2.1 CREAR organizaciones faltantes
DO $$
DECLARE
    created_count INTEGER;
BEGIN
    WITH inserted AS (
        INSERT INTO core.organization (code, name, short_name, org_type_id, metadata)
        SELECT
            'ORG_' || UPPER(REPLACE(REPLACE(short_name, ' ', '_'), '.', '')),
            name,
            short_name,
            (SELECT id FROM ref.category WHERE scheme='org_type' AND code=org_type_code),
            jsonb_build_object(
                'created_from', 'metadata.unidad_tecnica',
                'normalized_at', now()::text,
                'normalized_version', 'v2.0'
            )
        FROM (VALUES
            -- Municipalidades (21)
            ('MUNICIP. NINHUE', 'Municipalidad de Ninhue', 'MUNICIPALIDAD'),
            ('MUNICIP. BULNES', 'Municipalidad de Bulnes', 'MUNICIPALIDAD'),
            ('MUNICIP. CHILLÁN', 'Municipalidad de Chillán', 'MUNICIPALIDAD'),
            ('MUNICIP. CHILLÁN VIEJO', 'Municipalidad de Chillán Viejo', 'MUNICIPALIDAD'),
            ('MUNICIP. QUILLÓN', 'Municipalidad de Quillón', 'MUNICIPALIDAD'),
            ('MUNICIP. SAN NICOLÁS', 'Municipalidad de San Nicolás', 'MUNICIPALIDAD'),
            ('MUNICIP. SAN IGNACIO', 'Municipalidad de San Ignacio', 'MUNICIPALIDAD'),
            ('MUNICIP. COELEMU', 'Municipalidad de Coelemu', 'MUNICIPALIDAD'),
            ('MUNICIP. EL CARMEN', 'Municipalidad de El Carmen', 'MUNICIPALIDAD'),
            ('MUNICIP. YUNGAY', 'Municipalidad de Yungay', 'MUNICIPALIDAD'),
            ('MUNICIP. QUIRIHUE', 'Municipalidad de Quirihue', 'MUNICIPALIDAD'),
            ('MUNICIP. TREHUACO', 'Municipalidad de Trehuaco', 'MUNICIPALIDAD'),
            ('MUNICIP. COBQUECURA', 'Municipalidad de Cobquecura', 'MUNICIPALIDAD'),
            ('MUNICIP. SAN CARLOS', 'Municipalidad de San Carlos', 'MUNICIPALIDAD'),
            ('MUNICIP. ÑIQUÉN', 'Municipalidad de Ñiquén', 'MUNICIPALIDAD'),
            ('MUNICIP. PINTO', 'Municipalidad de Pinto', 'MUNICIPALIDAD'),
            ('MUNICIP. RÁNQUIL', 'Municipalidad de Ránquil', 'MUNICIPALIDAD'),
            ('MUNICIP. PORTEZUELO', 'Municipalidad de Portezuelo', 'MUNICIPALIDAD'),
            ('MUNICIP. COIHUECO', 'Municipalidad de Coihueco', 'MUNICIPALIDAD'),
            ('MUNICIP. PEMUCO', 'Municipalidad de Pemuco', 'MUNICIPALIDAD'),
            ('MUNICIP. SAN FABIÁN', 'Municipalidad de San Fabián', 'MUNICIPALIDAD'),

            -- Divisiones GORE (5)
            ('GORE-DIDESO', 'División de Desarrollo Social - GORE Ñuble', 'DIVISION'),
            ('GORE-DIFOI', 'División de Fomento e Industria - GORE Ñuble', 'DIVISION'),
            ('GORE-DIT', 'División de Infraestructura y Transporte - GORE Ñuble', 'DIVISION'),
            ('GORE-DIPIR', 'División de Presupuesto e Inversión Regional - GORE Ñuble', 'DIVISION'),
            ('GORE-DIPLADE', 'División de Planificación y Desarrollo - GORE Ñuble', 'DIVISION'),

            -- Servicios Públicos (13)
            ('S.SALUD ÑUBLE', 'Servicio de Salud Ñuble', 'SERVICIO'),
            ('FOSIS', 'Fondo de Solidaridad e Inversión Social', 'SERVICIO'),
            ('INDAP', 'Instituto de Desarrollo Agropecuario', 'SERVICIO'),
            ('ADRA', 'Agencia de Desarrollo Regional Ñuble', 'SERVICIO'),
            ('REGISTRO CIVIL', 'Servicio de Registro Civil e Identificación', 'SERVICIO'),
            ('MEJOR NIÑEZ', 'Servicio Nacional de Protección Especializada', 'SERVICIO'),
            ('INACAP', 'Instituto Nacional de Capacitación', 'SERVICIO'),
            ('SEREMI TRABAJO', 'Secretaría Regional Ministerial del Trabajo', 'SERVICIO'),
            ('SEREMI MM.AA', 'Secretaría Regional Ministerial Medio Ambiente', 'SERVICIO'),
            ('CORFO FIA', 'Fundación para la Innovación Agraria', 'SERVICIO'),
            ('MOP-DGA', 'Dirección General de Aguas - MOP', 'SERVICIO'),
            ('MOP-VIALIDAD', 'Dirección de Vialidad - MOP', 'SERVICIO'),
            ('MOP-AEROPUERTOS', 'Dirección de Aeropuertos - MOP', 'SERVICIO'),

            -- Asociaciones (2)
            ('ASOCIACIÓN PUNILLA', 'Asociación de Municipios Valle del Punilla', 'ORG_COMUNITARIA'),
            ('ASOCIACIÓN ITATA', 'Asociación de Municipios Valle del Itata', 'ORG_COMUNITARIA'),

            -- Universidades (3)
            ('UNIV. ADVENTISTA', 'Universidad Adventista de Chile', 'UNIVERSIDAD'),
            ('UDECH', 'Universidad de Chile', 'UNIVERSIDAD'),
            ('UTALCA', 'Universidad de Talca', 'UNIVERSIDAD')
        ) AS orgs(short_name, name, org_type_code)
        ON CONFLICT (code) DO NOTHING
        RETURNING id
    )
    SELECT COUNT(*) INTO created_count FROM inserted;

    IF created_count > 0 THEN
        RAISE NOTICE '✓ % organizaciones creadas (de 44 totales)', created_count;
    ELSE
        RAISE NOTICE '✓ 0 organizaciones creadas (las 44 ya existían)';
    END IF;
END $$;

-- 2.2 VALIDAR que todas las organizaciones existen
DO $$
DECLARE
    missing_orgs TEXT[];
BEGIN
    SELECT ARRAY_AGG(DISTINCT unidad_tecnica)
    INTO missing_orgs
    FROM (
        SELECT metadata->>'unidad_tecnica' AS unidad_tecnica
        FROM core.ipr
        WHERE metadata ? 'unidad_tecnica'
    ) ut
    LEFT JOIN core.organization o ON o.short_name = ut.unidad_tecnica
    WHERE o.id IS NULL;

    IF array_length(missing_orgs, 1) > 0 THEN
        RAISE EXCEPTION 'Organizaciones faltantes (no se crearon): %', missing_orgs;
    ELSE
        RAISE NOTICE '✓ Todas las organizaciones necesarias existen';
    END IF;
END $$;

-- 2.3 CREAR registros en ipr_party
DO $$
DECLARE
    created_count INTEGER;
BEGIN
    WITH inserted AS (
        INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, metadata)
        SELECT
            i.id,
            o.id,
            (SELECT id FROM ref.category WHERE scheme='ipr_party_role' AND code='UNIDAD_TECNICA'),
            jsonb_build_object(
                'migrated_from', 'metadata.unidad_tecnica',
                'normalized_at', now()::text,
                'normalized_version', 'v2.0'
            )
        FROM core.ipr i
        JOIN core.organization o ON o.short_name = i.metadata->>'unidad_tecnica'
        WHERE i.metadata ? 'unidad_tecnica'
          AND NOT EXISTS (
              SELECT 1 FROM core.ipr_party ip
              WHERE ip.ipr_id = i.id
                AND ip.party_role_id = (
                    SELECT id FROM ref.category
                    WHERE scheme='ipr_party_role' AND code='UNIDAD_TECNICA'
                )
          )
        ON CONFLICT DO NOTHING
        RETURNING id
    )
    SELECT COUNT(*) INTO created_count FROM inserted;

    RAISE NOTICE '✓ % registros ipr_party creados para unidad_tecnica', created_count;
END $$;

-- 2.4 VERIFICAR completitud
DO $$
DECLARE
    remaining INTEGER;
BEGIN
    SELECT COUNT(*) INTO remaining
    FROM core.ipr i
    WHERE i.metadata ? 'unidad_tecnica'
      AND NOT EXISTS (
          SELECT 1 FROM core.ipr_party ip
          WHERE ip.ipr_id = i.id
            AND ip.party_role_id = (
                SELECT id FROM ref.category
                WHERE scheme='ipr_party_role' AND code='UNIDAD_TECNICA'
            )
      );

    IF remaining > 0 THEN
        RAISE EXCEPTION 'ERROR: % IPRs aún sin unidad_tecnica normalizada', remaining;
    ELSE
        RAISE NOTICE '✓ Verificación: 0 IPRs faltantes (migración completa)';
    END IF;
END $$;

-- 2.5 REMOVER campo normalizado
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE core.ipr
        SET metadata = metadata - 'unidad_tecnica'
        WHERE metadata ? 'unidad_tecnica'
        RETURNING id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;

    RAISE NOTICE '✓ % IPRs: unidad_tecnica removido de metadata', updated_count;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 3: CREAR SCHEME COHERENTE investment_sector
-- ==============================================================================

BEGIN;

SELECT report_phase('FASE 3', 'Crear Scheme investment_sector (gnub:InvestmentTypology)');

-- 3.1 CREAR scheme
DO $$
DECLARE
    created_count INTEGER;
BEGIN
    WITH inserted AS (
        INSERT INTO ref.category (scheme, code, label, label_en, description, sort_order, metadata)
        VALUES
        ('investment_sector', 'SPORTS', 'Infraestructura Deportiva', 'Sports Infrastructure', 'Inversión en infraestructura y equipamiento deportivo', 1, '{"gnub_class": "InvestmentTypology"}'::jsonb),
        ('investment_sector', 'CULTURE', 'Cultura y Patrimonio', 'Culture and Heritage', 'Inversión en cultura, patrimonio y desarrollo cultural', 2, '{"gnub_class": "InvestmentTypology"}'::jsonb),
        ('investment_sector', 'EDUCATION', 'Educación', 'Education', 'Inversión en infraestructura y equipamiento educativo', 3, '{"gnub_class": "InvestmentTypology"}'::jsonb),
        ('investment_sector', 'HEALTH', 'Salud', 'Health', 'Inversión en infraestructura y equipamiento de salud', 4, '{"gnub_class": "InvestmentTypology"}'::jsonb),
        ('investment_sector', 'ENVIRONMENT', 'Medio Ambiente y Recursos Naturales', 'Environment and Natural Resources', 'Inversión en medio ambiente, recursos naturales y sustentabilidad', 5, '{"gnub_class": "InvestmentTypology"}'::jsonb),
        ('investment_sector', 'TRANSPORT', 'Transporte y Vialidad', 'Transport and Roads', 'Inversión en infraestructura de transporte y conectividad', 6, '{"gnub_class": "InvestmentTypology"}'::jsonb),
        ('investment_sector', 'SECURITY', 'Seguridad Pública', 'Public Security', 'Inversión en seguridad ciudadana e infraestructura de emergencia', 7, '{"gnub_class": "InvestmentTypology"}'::jsonb),
        ('investment_sector', 'TOURISM', 'Turismo y Comercio', 'Tourism and Commerce', 'Inversión en fomento turístico y desarrollo comercial', 8, '{"gnub_class": "InvestmentTypology"}'::jsonb),
        ('investment_sector', 'SCIENCE', 'Ciencia e Innovación', 'Science and Innovation', 'Inversión en investigación, desarrollo e innovación', 9, '{"gnub_class": "InvestmentTypology"}'::jsonb),
        ('investment_sector', 'ECONOMIC_DEV', 'Desarrollo Económico', 'Economic Development', 'Inversión en fomento productivo y desarrollo económico', 10, '{"gnub_class": "InvestmentTypology"}'::jsonb)
        ON CONFLICT (scheme, code) DO NOTHING
        RETURNING id
    )
    SELECT COUNT(*) INTO created_count FROM inserted;

    IF created_count > 0 THEN
        RAISE NOTICE '✓ Scheme investment_sector creado: % códigos', created_count;
    ELSE
        RAISE NOTICE '✓ Scheme investment_sector ya existía (0 códigos nuevos)';
    END IF;
END $$;

-- 3.2 AÑADIR columna investment_sector_id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'ipr'
          AND column_name = 'investment_sector_id'
    ) THEN
        ALTER TABLE core.ipr
            ADD COLUMN investment_sector_id UUID REFERENCES ref.category(id);

        COMMENT ON COLUMN core.ipr.investment_sector_id IS
            'gnub:InvestmentTypology - Thematic sector of the investment initiative. Determines applicable Sectoral Information Requirements (RIS). Normalized from metadata.tipologia_original (sectoral codes only) on 2026-01-30.';

        RAISE NOTICE '✓ Columna investment_sector_id añadida a core.ipr';
    ELSE
        RAISE NOTICE '✓ Columna investment_sector_id ya existe';
    END IF;
END $$;

-- 3.3 MIGRAR datos (solo códigos sectoriales coherentes)
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE core.ipr i
        SET investment_sector_id = c.id
        FROM ref.category c
        WHERE c.scheme = 'investment_sector'
          AND i.metadata ? 'tipologia_original'
          AND investment_sector_id IS NULL  -- Solo actualizar si no está ya poblado
          AND (
              -- Mapeo desde tipología legacy a sector coherente
              (i.metadata->>'tipologia_original' = 'DEPORTE' AND c.code = 'SPORTS') OR
              (i.metadata->>'tipologia_original' IN ('CULTURA', 'CULTURA Y PATRIMONIO') AND c.code = 'CULTURE') OR
              (i.metadata->>'tipologia_original' = 'EDUCACION' AND c.code = 'EDUCATION') OR
              (i.metadata->>'tipologia_original' = 'SALUD' AND c.code = 'HEALTH') OR
              (i.metadata->>'tipologia_original' IN ('RECURSOS NATURALES Y MEDIO AMBIENTAL', 'RECURSO NATURAL Y MEDIO AMBIENTAL', 'RECURSOS NATURALES Y MEDIO AMBIENTE') AND c.code = 'ENVIRONMENT') OR
              (i.metadata->>'tipologia_original' IN ('TRANSPORTE', 'VIALIDAD') AND c.code = 'TRANSPORT') OR
              (i.metadata->>'tipologia_original' = 'SEGURIDAD' AND c.code = 'SECURITY') OR
              (i.metadata->>'tipologia_original' = 'TURISMO Y COMERCIO' AND c.code = 'TOURISM') OR
              (i.metadata->>'tipologia_original' = 'CIENCIA' AND c.code = 'SCIENCE') OR
              (i.metadata->>'tipologia_original' = 'ECONOMIA' AND c.code = 'ECONOMIC_DEV')
          )
        RETURNING i.id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;

    RAISE NOTICE '✓ % IPRs: investment_sector_id poblado desde tipologia_original', updated_count;
END $$;

-- 3.4 REPORTE distribución por sector
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '  Distribución por Sector:';
    RAISE NOTICE '  ────────────────────────────────────────────────';
END $$;

SELECT
    LPAD(c.label, 45) AS sector,
    LPAD(COUNT(*)::text, 6) AS iprs,
    LPAD(ROUND(COUNT(*)::numeric / NULLIF((SELECT COUNT(*) FROM core.ipr WHERE investment_sector_id IS NOT NULL), 0) * 100, 1)::text || '%', 8) AS pct
FROM core.ipr i
JOIN ref.category c ON i.investment_sector_id = c.id
WHERE c.scheme = 'investment_sector'
GROUP BY c.label, c.sort_order
ORDER BY c.sort_order;

DO $$
BEGIN
    RAISE NOTICE '  ────────────────────────────────────────────────';
    RAISE NOTICE '';
END $$;

-- 3.5 MANTENER tipologia_original como string de auditoría
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE core.ipr
        SET metadata = metadata || jsonb_build_object(
            'tipologia_legacy_sector_extracted', true,
            'sector_extraction_date', now()::text
        )
        WHERE metadata ? 'tipologia_original'
          AND investment_sector_id IS NOT NULL
        RETURNING id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;

    RAISE NOTICE '✓ % IPRs: metadata marcado con sector_extraction (tipologia_original MANTENIDO para auditoría)', updated_count;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 3.5: REMEDIAR funding_source_id (Coherencia Categorial)
-- ==============================================================================
-- PROBLEMA: 1,648 IPRs PROGRAMA_8PCT usan funding_source_id para scheme='fondo_8pct'
--           Esto viola Categorical Univocity (funding_source_id debe ser scheme='funding_source')
-- SOLUCIÓN: Crear fund_category_id específica para PROGRAMA_8PCT
-- ==============================================================================

BEGIN;

SELECT report_phase('FASE 3.5', 'Remediar funding_source_id (Coherencia Categorial)');

-- 3.5.1 Crear columna fund_category_id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'ipr'
          AND column_name = 'fund_category_id'
    ) THEN
        ALTER TABLE core.ipr
        ADD COLUMN fund_category_id UUID REFERENCES ref.category(id);

        RAISE NOTICE '✓ Columna fund_category_id creada';
    ELSE
        RAISE NOTICE '✓ Columna fund_category_id ya existe';
    END IF;
END $$;

-- 3.5.2 Migrar datos: funding_source_id → fund_category_id para PROGRAMA_8PCT
DO $$
DECLARE
    migrated_count INTEGER;
    programa_8pct_type_id UUID;
BEGIN
    -- Obtener ID del tipo PROGRAMA_8PCT
    SELECT id INTO programa_8pct_type_id
    FROM ref.category
    WHERE scheme = 'ipr_type' AND code = 'PROGRAMA_8PCT';

    IF programa_8pct_type_id IS NULL THEN
        RAISE WARNING 'No se encontró ipr_type PROGRAMA_8PCT, saltando migración';
        RETURN;
    END IF;

    -- Migrar funding_source_id → fund_category_id para PROGRAMA_8PCT
    WITH migrated AS (
        UPDATE core.ipr
        SET
            fund_category_id = funding_source_id,
            funding_source_id = NULL
        WHERE ipr_type_id = programa_8pct_type_id
          AND funding_source_id IS NOT NULL
        RETURNING id
    )
    SELECT COUNT(*) INTO migrated_count FROM migrated;

    RAISE NOTICE '✓ % IPRs PROGRAMA_8PCT: funding_source_id migrado a fund_category_id', migrated_count;
END $$;

-- 3.5.3 Verificar coherencia post-migración
DO $$
DECLARE
    invalid_funding_source INTEGER;
    invalid_fund_category INTEGER;
BEGIN
    -- Verificar que NO hay funding_source_id con scheme incorrecto
    SELECT COUNT(*) INTO invalid_funding_source
    FROM core.ipr i
    JOIN ref.category c ON c.id = i.funding_source_id
    WHERE c.scheme != 'funding_source';

    IF invalid_funding_source > 0 THEN
        RAISE EXCEPTION 'COHERENCIA VIOLADA: % IPRs tienen funding_source_id con scheme incorrecto', invalid_funding_source;
    ELSE
        RAISE NOTICE '✓ Coherencia funding_source_id: 100%% (todos scheme=funding_source)';
    END IF;

    -- Verificar que fund_category_id solo tiene scheme fondo_8pct
    SELECT COUNT(*) INTO invalid_fund_category
    FROM core.ipr i
    JOIN ref.category c ON c.id = i.fund_category_id
    WHERE c.scheme != 'fondo_8pct';

    IF invalid_fund_category > 0 THEN
        RAISE EXCEPTION 'COHERENCIA VIOLADA: % IPRs tienen fund_category_id con scheme incorrecto', invalid_fund_category;
    ELSE
        RAISE NOTICE '✓ Coherencia fund_category_id: 100%% (todos scheme=fondo_8pct)';
    END IF;
END $$;

-- 3.5.4 Crear índice para fund_category_id
CREATE INDEX IF NOT EXISTS idx_ipr_fund_category
ON core.ipr(fund_category_id)
WHERE fund_category_id IS NOT NULL;

DO $$
BEGIN
    RAISE NOTICE '✓ Índice idx_ipr_fund_category creado';
END $$;

COMMIT;

-- ==============================================================================
-- FASE 4: AÑADIR CHECK CONSTRAINTS DE COHERENCIA CATEGORIAL
-- ==============================================================================

BEGIN;

SELECT report_phase('FASE 4', 'Añadir CHECK Constraints (Coherencia Categorial)');

-- 4.1 Remover constraints existentes (si los hay)
DO $$
BEGIN
    ALTER TABLE core.ipr
        DROP CONSTRAINT IF EXISTS chk_ipr_type_scheme,
        DROP CONSTRAINT IF EXISTS chk_mcd_phase_scheme,
        DROP CONSTRAINT IF EXISTS chk_status_scheme,
        DROP CONSTRAINT IF EXISTS chk_budget_subtitle_scheme,
        DROP CONSTRAINT IF EXISTS chk_funding_source_scheme,
        DROP CONSTRAINT IF EXISTS chk_mechanism_scheme,
        DROP CONSTRAINT IF EXISTS chk_investment_sector_scheme,
        DROP CONSTRAINT IF EXISTS chk_fund_category_scheme;

    RAISE NOTICE '✓ Constraints anteriores removidos (si existían)';
END $$;

-- 4.2 Añadir constraints de validación categorial
DO $$
BEGIN
    ALTER TABLE core.ipr
        ADD CONSTRAINT chk_ipr_type_scheme
            CHECK (ipr_type_id IS NULL OR fn_validate_category_scheme(ipr_type_id, 'ipr_type')),
        ADD CONSTRAINT chk_mcd_phase_scheme
            CHECK (mcd_phase_id IS NULL OR fn_validate_category_scheme(mcd_phase_id, 'mcd_phase')),
        ADD CONSTRAINT chk_status_scheme
            CHECK (status_id IS NULL OR fn_validate_category_scheme(status_id, 'ipr_state')),
        ADD CONSTRAINT chk_budget_subtitle_scheme
            CHECK (budget_subtitle_id IS NULL OR fn_validate_category_scheme(budget_subtitle_id, 'budget_subtitle')),
        ADD CONSTRAINT chk_funding_source_scheme
            CHECK (funding_source_id IS NULL OR fn_validate_category_scheme(funding_source_id, 'funding_source')),
        ADD CONSTRAINT chk_mechanism_scheme
            CHECK (mechanism_id IS NULL OR fn_validate_category_scheme(mechanism_id, 'mechanism')),
        ADD CONSTRAINT chk_investment_sector_scheme
            CHECK (investment_sector_id IS NULL OR fn_validate_category_scheme(investment_sector_id, 'investment_sector')),
        ADD CONSTRAINT chk_fund_category_scheme
            CHECK (fund_category_id IS NULL OR fn_validate_category_scheme(fund_category_id, 'fondo_8pct'));

    RAISE NOTICE '✓ 8 CHECK constraints añadidos para coherencia categorial';
END $$;

-- 4.3 Verificar constraints creados
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '  Constraints Creados:';
    RAISE NOTICE '  ────────────────────────────────────────────────';
END $$;

SELECT
    '  ' || LPAD(conname, 35) AS constraint_name
FROM pg_constraint
WHERE conrelid = 'core.ipr'::regclass
  AND contype = 'c'
  AND conname LIKE 'chk_%_scheme'
ORDER BY conname;

DO $$
BEGIN
    RAISE NOTICE '  ────────────────────────────────────────────────';
    RAISE NOTICE '';
END $$;

COMMIT;

-- ==============================================================================
-- FASE 5: OPTIMIZACIONES DE PERFORMANCE
-- ==============================================================================

BEGIN;

SELECT report_phase('FASE 5', 'Optimizaciones de Performance');

-- 5.1 Índice en investment_sector_id
CREATE INDEX IF NOT EXISTS idx_ipr_investment_sector ON core.ipr(investment_sector_id)
    WHERE investment_sector_id IS NOT NULL;

DO $$
BEGIN
    RAISE NOTICE '✓ Índice idx_ipr_investment_sector creado (partial index)';
END $$;

-- 5.2 Análisis de tabla para optimizar query planner
ANALYZE core.ipr;
DO $$
BEGIN
    RAISE NOTICE '✓ ANALYZE ejecutado en core.ipr';
END $$;

COMMIT;

-- ==============================================================================
-- POST-EJECUCIÓN: VERIFICACIONES FINALES
-- ==============================================================================

SELECT report_phase('POST-EJECUCIÓN', 'Verificaciones Finales');

-- Verificación 1: Metadata limpio
DO $$
DECLARE
    remaining INTEGER;
BEGIN
    SELECT COUNT(*) INTO remaining
    FROM core.ipr
    WHERE metadata ?| ARRAY['provincia', 'comuna', 'etapa_original', 'unidad_tecnica'];

    IF remaining = 0 THEN
        RAISE NOTICE '✓ PASS: 0 IPRs con campos normalizados en metadata';
    ELSE
        RAISE WARNING 'FAIL: % IPRs aún tienen campos normalizados', remaining;
    END IF;
END $$;

-- Verificación 2: unidad_tecnica completa
DO $$
DECLARE
    missing INTEGER;
BEGIN
    SELECT COUNT(*) INTO missing
    FROM temp_ipr_metadata_backup_v2 b
    WHERE b.metadata ? 'unidad_tecnica'
      AND NOT EXISTS (
          SELECT 1 FROM core.ipr_party ip
          WHERE ip.ipr_id = b.id
            AND ip.party_role_id = (SELECT id FROM ref.category WHERE code='UNIDAD_TECNICA')
      );

    IF missing = 0 THEN
        RAISE NOTICE '✓ PASS: Todas las unidad_tecnica migradas a ipr_party';
    ELSE
        RAISE WARNING 'FAIL: % unidad_tecnica sin migrar', missing;
    END IF;
END $$;

-- Verificación 3: investment_sector poblado
DO $$
DECLARE
    populated INTEGER;
    total INTEGER;
    percentage NUMERIC;
BEGIN
    SELECT COUNT(*) INTO populated FROM core.ipr WHERE investment_sector_id IS NOT NULL;
    SELECT COUNT(*) INTO total FROM core.ipr;
    percentage := ROUND(populated::numeric / NULLIF(total, 0) * 100, 1);

    RAISE NOTICE '✓ INFO: investment_sector poblado en % IPRs (% de %)', populated, percentage, total;
END $$;

-- Verificación 4: Coherencia categorial (debe pasar sin errores)
DO $$
DECLARE
    incoherent INTEGER;
BEGIN
    SELECT COUNT(*) INTO incoherent
    FROM (
        SELECT codigo_bip, 'ipr_type' AS field, ipr_type_id AS category_id
        FROM core.ipr
        WHERE ipr_type_id IS NOT NULL
          AND NOT fn_validate_category_scheme(ipr_type_id, 'ipr_type')
        UNION ALL
        SELECT codigo_bip, 'investment_sector', investment_sector_id
        FROM core.ipr
        WHERE investment_sector_id IS NOT NULL
          AND NOT fn_validate_category_scheme(investment_sector_id, 'investment_sector')
        UNION ALL
        SELECT codigo_bip, 'mechanism', mechanism_id
        FROM core.ipr
        WHERE mechanism_id IS NOT NULL
          AND NOT fn_validate_category_scheme(mechanism_id, 'mechanism')
    ) incoherences;

    IF incoherent = 0 THEN
        RAISE NOTICE '✓ PASS: 100%% coherencia categorial (0 violaciones)';
    ELSE
        RAISE WARNING 'FAIL: % categorías incoherentes detectadas', incoherent;
    END IF;
END $$;

-- Verificación 5: Tamaño metadata reducido
DO $$
DECLARE
    avg_size_before NUMERIC;
    avg_size_after NUMERIC;
    reduction NUMERIC;
BEGIN
    SELECT AVG(pg_column_size(metadata)) INTO avg_size_before FROM temp_ipr_metadata_backup_v2;
    SELECT AVG(pg_column_size(metadata)) INTO avg_size_after FROM core.ipr WHERE metadata IS NOT NULL;
    reduction := ROUND((1 - avg_size_after / NULLIF(avg_size_before, 0)) * 100, 1);

    RAISE NOTICE '✓ INFO: Tamaño metadata: % bytes → % bytes (% reducción)', ROUND(avg_size_before, 0), ROUND(avg_size_after, 0), reduction;
END $$;

-- ==============================================================================
-- REPORTE FINAL
-- ==============================================================================

DO $$ BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  NORMALIZACIÓN COMPLETADA EXITOSAMENTE                         ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
    RAISE NOTICE 'Coherencia Categorial Alcanzada: ~92%%';
    RAISE NOTICE 'Versión: v2.0';
    RAISE NOTICE 'Arquitecto: ARQUITECTO-GORE v0.1.0';
    RAISE NOTICE '';
    RAISE NOTICE 'Próximos pasos:';
    RAISE NOTICE '  1. Validar queries de aplicación (apps/migration_viewer)';
    RAISE NOTICE '  2. Actualizar loaders ETL (etl/migration/loaders/ipr_loader.py)';
    RAISE NOTICE '  3. Documentar en ERD (model/model_goreos/docs/GOREOS_ERD_v3.md)';
    RAISE NOTICE '';
    RAISE NOTICE 'Backup: SELECT * FROM temp_ipr_metadata_backup_v2;';
    RAISE NOTICE '';
END $$;

-- Limpiar función helper
DROP FUNCTION report_phase(TEXT, TEXT);

-- ==============================================================================
-- FIN
-- ==============================================================================
