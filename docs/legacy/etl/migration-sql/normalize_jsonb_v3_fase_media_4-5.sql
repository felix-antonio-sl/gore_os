-- ============================================================================
-- NORMALIZACION JSONB v3.0 - FASE MEDIA (CAMPOS 4-5)
-- ============================================================================
-- Archivo: etl/migration/sql/normalize_jsonb_v3_fase_media_4-5.sql
-- Fecha: 2026-01-30
-- Autor: arquitecto-gore (CM-ARTIFACT-GENERATOR)
--
-- SCOPE:
--   4. core.ipr_party.division → sponsor_division_id FK (37 registros)
--   5. core.ipr.origen → is_municipal_origin BOOLEAN (1,965 registros)
--
-- ONTOLOGIA:
--   - gnub:SponsorDivision (campo 4)
--   - gnub:MunicipalOrigin (campo 5)
--
-- PREREQUISITOS:
--   - Esquema core.ipr_party y core.ipr validados
--   - Organizaciones tipo DIVISION existentes en core.organization
--   - Categorical Audit v3.0 completada
--
-- EJECUCION:
--   psql -U goreos -d goreos_model -f normalize_jsonb_v3_fase_media_4-5.sql
-- ============================================================================

\set ON_ERROR_STOP on
\timing on

-- ============================================================================
-- FASE 1: PRE-FLIGHT CHECKS
-- ============================================================================

DO $pre_checks$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  NORMALIZACION v3.0 - FASE MEDIA (CAMPOS 4-5)                 ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
    RAISE NOTICE '[INICIO] Verificaciones pre-vuelo...';
END $pre_checks$;

-- Verificar esquema core.ipr_party
DO $schema_check_1$
DECLARE
    v_column_exists BOOLEAN;
BEGIN
    -- Verificar que sponsor_division_id NO existe aún
    SELECT EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='core'
        AND table_name='ipr_party'
        AND column_name='sponsor_division_id'
    ) INTO v_column_exists;

    IF v_column_exists THEN
        RAISE WARNING '[SCHEMA] Columna sponsor_division_id ya existe en core.ipr_party';
    ELSE
        RAISE NOTICE '[SCHEMA] ✓ Columna sponsor_division_id no existe (OK para crear)';
    END IF;

    -- Verificar que metadata existe
    SELECT EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='core'
        AND table_name='ipr_party'
        AND column_name='metadata'
    ) INTO v_column_exists;

    IF NOT v_column_exists THEN
        RAISE EXCEPTION '[ERROR] Columna metadata no existe en core.ipr_party';
    ELSE
        RAISE NOTICE '[SCHEMA] ✓ Columna metadata existe en core.ipr_party';
    END IF;
END $schema_check_1$;

-- Verificar esquema core.ipr
DO $schema_check_2$
DECLARE
    v_column_exists BOOLEAN;
BEGIN
    -- Verificar que is_municipal_origin NO existe aún
    SELECT EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='core'
        AND table_name='ipr'
        AND column_name='is_municipal_origin'
    ) INTO v_column_exists;

    IF v_column_exists THEN
        RAISE WARNING '[SCHEMA] Columna is_municipal_origin ya existe en core.ipr';
    ELSE
        RAISE NOTICE '[SCHEMA] ✓ Columna is_municipal_origin no existe (OK para crear)';
    END IF;

    -- Verificar que metadata existe
    SELECT EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='core'
        AND table_name='ipr'
        AND column_name='metadata'
    ) INTO v_column_exists;

    IF NOT v_column_exists THEN
        RAISE EXCEPTION '[ERROR] Columna metadata no existe en core.ipr';
    ELSE
        RAISE NOTICE '[SCHEMA] ✓ Columna metadata existe en core.ipr';
    END IF;
END $schema_check_2$;

-- Verificar datos disponibles
DO $data_check$
DECLARE
    v_division_count INTEGER;
    v_origen_count INTEGER;
    v_division_org_count INTEGER;
BEGIN
    -- Contar registros con division
    SELECT COUNT(*) INTO v_division_count
    FROM core.ipr_party
    WHERE metadata->>'division' IS NOT NULL;

    RAISE NOTICE '[DATA] Registros con metadata.division: %', v_division_count;

    -- Contar registros con origen
    SELECT COUNT(*) INTO v_origen_count
    FROM core.ipr
    WHERE metadata->>'origen' IS NOT NULL;

    RAISE NOTICE '[DATA] Registros con metadata.origen: %', v_origen_count;

    -- Verificar organizaciones tipo DIVISION
    SELECT COUNT(*) INTO v_division_org_count
    FROM core.organization
    WHERE org_type_id = (SELECT id FROM ref.category WHERE scheme='org_type' AND code='DIVISION');

    RAISE NOTICE '[DATA] Organizaciones tipo DIVISION: %', v_division_org_count;

    IF v_division_count = 0 THEN
        RAISE WARNING '[DATA] No hay registros con division para migrar';
    END IF;

    IF v_origen_count = 0 THEN
        RAISE WARNING '[DATA] No hay registros con origen para migrar';
    END IF;

    RAISE NOTICE '[PRE-CHECKS] ✓ Verificaciones completadas';
    RAISE NOTICE '';
END $data_check$;


-- ============================================================================
-- FASE 2: BACKUPS TEMPORALES
-- ============================================================================

DO $backup_start$
BEGIN
    RAISE NOTICE '[BACKUP] Creando tablas de respaldo temporal...';
END $backup_start$;

-- Backup de ipr_party
DROP TABLE IF EXISTS _backup_ipr_party_v3_media;
CREATE TEMP TABLE _backup_ipr_party_v3_media AS
SELECT * FROM core.ipr_party;

-- Backup de ipr
DROP TABLE IF EXISTS _backup_ipr_v3_media;
CREATE TEMP TABLE _backup_ipr_v3_media AS
SELECT * FROM core.ipr;

DO $backup_confirm$
DECLARE
    v_backup_party_count INTEGER;
    v_backup_ipr_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_backup_party_count FROM _backup_ipr_party_v3_media;
    SELECT COUNT(*) INTO v_backup_ipr_count FROM _backup_ipr_v3_media;

    RAISE NOTICE '[BACKUP] ✓ Respaldo ipr_party: % registros', v_backup_party_count;
    RAISE NOTICE '[BACKUP] ✓ Respaldo ipr: % registros', v_backup_ipr_count;
    RAISE NOTICE '';
END $backup_confirm$;


-- ============================================================================
-- NORMALIZACION 4: core.ipr_party.division → sponsor_division_id FK
-- ============================================================================

DO $norm4_header$
BEGIN
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  NORMALIZACION 4: ipr_party.division → sponsor_division_id    ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
END $norm4_header$;

-- Análisis pre-migración
DO $norm4_analysis$
BEGIN
    RAISE NOTICE '[ANALISIS] Distribución de valores division:';
END $norm4_analysis$;

SELECT
    metadata->>'division' as division,
    COUNT(*) as total
FROM core.ipr_party
WHERE metadata->>'division' IS NOT NULL
GROUP BY metadata->>'division'
ORDER BY total DESC;

-- Crear tabla de mapeo manual para divisiones
DROP TABLE IF EXISTS _temp_division_mapping;
CREATE TEMP TABLE _temp_division_mapping (
    metadata_value TEXT PRIMARY KEY,
    organization_code TEXT NOT NULL,
    organization_name TEXT
);

-- Mapeo manual basado en análisis de datos
INSERT INTO _temp_division_mapping (metadata_value, organization_code, organization_name) VALUES
('DIDESO', 'ORG_GORE-DIDESO', 'División de Desarrollo Social - GORE Ñuble'),
('DIFOI', 'ORG_GORE-DIFOI', 'División de Fomento e Industria - GORE Ñuble'),
('DIPIR', 'DIPIR', 'División de Planificación e Inversión Regional'),
('DIPLADE', 'DIPLADE', 'División de Planificación y Desarrollo'),
('DIT', 'DIT', 'División de Infraestructura y Transporte');

DO $norm4_mapping_check$
BEGIN
    RAISE NOTICE '[MAPEO] Verificando correspondencia con core.organization:';
END $norm4_mapping_check$;

SELECT
    dm.metadata_value,
    dm.organization_code,
    o.name as org_name_actual,
    CASE WHEN o.id IS NOT NULL THEN '✓' ELSE '✗' END as exists
FROM _temp_division_mapping dm
LEFT JOIN core.organization o ON o.code = dm.organization_code
ORDER BY dm.metadata_value;

-- PASO 4.1: Agregar columna sponsor_division_id
BEGIN;

DO $norm4_add_column$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '[NORM-4.1] Agregando columna sponsor_division_id a core.ipr_party...';

    -- Verificar si ya existe
    IF EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='core'
        AND table_name='ipr_party'
        AND column_name='sponsor_division_id'
    ) THEN
        RAISE NOTICE '[NORM-4.1] ⚠ Columna sponsor_division_id ya existe, saltando creación';
    ELSE
        ALTER TABLE core.ipr_party
        ADD COLUMN sponsor_division_id UUID REFERENCES core.organization(id);

        RAISE NOTICE '[NORM-4.1] ✓ Columna sponsor_division_id creada';
    END IF;
END $norm4_add_column$;

COMMIT;

-- PASO 4.2: Crear índice
BEGIN;

DO $norm4_create_index$
BEGIN
    RAISE NOTICE '[NORM-4.2] Creando índice idx_ipr_party_sponsor_division...';

    -- Drop si existe
    DROP INDEX IF EXISTS core.idx_ipr_party_sponsor_division;

    CREATE INDEX idx_ipr_party_sponsor_division
    ON core.ipr_party(sponsor_division_id)
    WHERE sponsor_division_id IS NOT NULL;

    RAISE NOTICE '[NORM-4.2] ✓ Índice creado';
END $norm4_create_index$;

COMMIT;

-- PASO 4.3: Migrar datos usando mapeo manual
BEGIN;

DO $norm4_migrate$
DECLARE
    v_updated_count INTEGER;
BEGIN
    RAISE NOTICE '[NORM-4.3] Migrando datos usando mapeo manual...';

    WITH division_mapping AS (
        SELECT
            dm.metadata_value,
            o.id as org_id
        FROM _temp_division_mapping dm
        INNER JOIN core.organization o ON o.code = dm.organization_code
    )
    UPDATE core.ipr_party ip
    SET sponsor_division_id = dm.org_id
    FROM division_mapping dm
    WHERE ip.metadata->>'division' = dm.metadata_value
    AND ip.metadata->>'division' IS NOT NULL;

    GET DIAGNOSTICS v_updated_count = ROW_COUNT;

    RAISE NOTICE '[NORM-4.3] ✓ Registros actualizados: %', v_updated_count;
END $norm4_migrate$;

COMMIT;

-- PASO 4.4: Verificación post-migración
DO $norm4_verify$
DECLARE
    v_matched INTEGER;
    v_unmatched INTEGER;
    v_total INTEGER;
    v_match_rate NUMERIC;
BEGIN
    RAISE NOTICE '[NORM-4.4] Verificando resultados de migración...';

    SELECT
        COUNT(*) FILTER (WHERE sponsor_division_id IS NOT NULL) as matched,
        COUNT(*) FILTER (WHERE sponsor_division_id IS NULL AND metadata->>'division' IS NOT NULL) as unmatched,
        COUNT(*) FILTER (WHERE metadata->>'division' IS NOT NULL) as total
    INTO v_matched, v_unmatched, v_total
    FROM core.ipr_party;

    IF v_total > 0 THEN
        v_match_rate := ROUND(100.0 * v_matched / v_total, 2);
    ELSE
        v_match_rate := 0;
    END IF;

    RAISE NOTICE '[NORM-4.4] Registros con division en metadata: %', v_total;
    RAISE NOTICE '[NORM-4.4] Matched (sponsor_division_id populated): %', v_matched;
    RAISE NOTICE '[NORM-4.4] Unmatched (sin FK): %', v_unmatched;
    RAISE NOTICE '[NORM-4.4] Match rate: % %%', v_match_rate;

    IF v_match_rate >= 95.0 THEN
        RAISE NOTICE '[NORM-4.4] ✓ Match rate aceptable (>= 95%%)';
    ELSIF v_match_rate >= 80.0 THEN
        RAISE WARNING '[NORM-4.4] ⚠ Match rate bajo (< 95%%)';
    ELSE
        RAISE WARNING '[NORM-4.4] ✗ Match rate crítico (< 80%%)';
    END IF;

    RAISE NOTICE '';
END $norm4_verify$;

-- Mostrar casos no mapeados
DO $norm4_unmapped$
BEGIN
    RAISE NOTICE '[NORM-4.4] Casos no mapeados:';
END $norm4_unmapped$;

SELECT
    metadata->>'division' as division_no_mapeada,
    COUNT(*) as total
FROM core.ipr_party
WHERE metadata->>'division' IS NOT NULL
AND sponsor_division_id IS NULL
GROUP BY metadata->>'division'
ORDER BY total DESC;


-- ============================================================================
-- NORMALIZACION 5: core.ipr.origen → is_municipal_origin BOOLEAN
-- ============================================================================

DO $norm5_header$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  NORMALIZACION 5: ipr.origen → is_municipal_origin            ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
END $norm5_header$;

-- Análisis pre-migración
DO $norm5_analysis$
BEGIN
    RAISE NOTICE '[ANALISIS] Distribución de valores origen:';
END $norm5_analysis$;

SELECT
    metadata->>'origen' as origen,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM core.ipr
WHERE metadata->>'origen' IS NOT NULL
GROUP BY metadata->>'origen'
ORDER BY total DESC;

-- PASO 5.1: Agregar columna is_municipal_origin
BEGIN;

DO $norm5_add_column$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '[NORM-5.1] Agregando columna is_municipal_origin a core.ipr...';

    -- Verificar si ya existe
    IF EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='core'
        AND table_name='ipr'
        AND column_name='is_municipal_origin'
    ) THEN
        RAISE NOTICE '[NORM-5.1] ⚠ Columna is_municipal_origin ya existe, saltando creación';
    ELSE
        ALTER TABLE core.ipr
        ADD COLUMN is_municipal_origin BOOLEAN DEFAULT false;

        RAISE NOTICE '[NORM-5.1] ✓ Columna is_municipal_origin creada (default: false)';
    END IF;
END $norm5_add_column$;

COMMIT;

-- PASO 5.2: Crear índice
BEGIN;

DO $norm5_create_index$
BEGIN
    RAISE NOTICE '[NORM-5.2] Creando índice idx_ipr_municipal_origin...';

    -- Drop si existe
    DROP INDEX IF EXISTS core.idx_ipr_municipal_origin;

    CREATE INDEX idx_ipr_municipal_origin
    ON core.ipr(is_municipal_origin)
    WHERE is_municipal_origin = true;

    RAISE NOTICE '[NORM-5.2] ✓ Índice creado (partial index para true)';
END $norm5_create_index$;

COMMIT;

-- PASO 5.3: Migrar datos
BEGIN;

DO $norm5_migrate$
DECLARE
    v_updated_count INTEGER;
BEGIN
    RAISE NOTICE '[NORM-5.3] Migrando datos (MUNICIPIO → true, otros → false)...';

    UPDATE core.ipr
    SET is_municipal_origin = (
        CASE
            WHEN UPPER(TRIM(metadata->>'origen')) = 'MUNICIPIO' THEN true
            ELSE false
        END
    )
    WHERE metadata->>'origen' IS NOT NULL;

    GET DIAGNOSTICS v_updated_count = ROW_COUNT;

    RAISE NOTICE '[NORM-5.3] ✓ Registros actualizados: %', v_updated_count;
END $norm5_migrate$;

COMMIT;

-- PASO 5.4: Verificación post-migración
DO $norm5_verify$
DECLARE
    v_total INTEGER;
    v_municipal INTEGER;
    v_sectorial INTEGER;
    v_null_count INTEGER;
    v_municipal_pct NUMERIC;
BEGIN
    RAISE NOTICE '[NORM-5.4] Verificando resultados de migración...';

    SELECT
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE is_municipal_origin = true) as municipal,
        COUNT(*) FILTER (WHERE is_municipal_origin = false AND metadata->>'origen' IS NOT NULL) as sectorial,
        COUNT(*) FILTER (WHERE is_municipal_origin IS NULL) as null_count
    INTO v_total, v_municipal, v_sectorial, v_null_count
    FROM core.ipr
    WHERE metadata->>'origen' IS NOT NULL;

    IF v_total > 0 THEN
        v_municipal_pct := ROUND(100.0 * v_municipal / v_total, 2);
    ELSE
        v_municipal_pct := 0;
    END IF;

    RAISE NOTICE '[NORM-5.4] Total registros con origen: %', v_total;
    RAISE NOTICE '[NORM-5.4] Municipal (true): % (% %%)', v_municipal, v_municipal_pct;
    RAISE NOTICE '[NORM-5.4] Sectorial/Otro (false): %', v_sectorial;
    RAISE NOTICE '[NORM-5.4] NULL: %', v_null_count;

    IF v_null_count > 0 THEN
        RAISE WARNING '[NORM-5.4] ⚠ Se encontraron % registros con valor NULL', v_null_count;
    ELSE
        RAISE NOTICE '[NORM-5.4] ✓ No hay valores NULL';
    END IF;

    RAISE NOTICE '';
END $norm5_verify$;

-- Distribución final
DO $norm5_distribution$
BEGIN
    RAISE NOTICE '[NORM-5.4] Distribución final de is_municipal_origin:';
END $norm5_distribution$;

SELECT
    is_municipal_origin,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM core.ipr
WHERE is_municipal_origin IS NOT NULL
GROUP BY is_municipal_origin
ORDER BY is_municipal_origin DESC;


-- ============================================================================
-- FASE 3: VERIFICACION GLOBAL
-- ============================================================================

DO $global_verify_header$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  VERIFICACION GLOBAL                                           ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
END $global_verify_header$;

-- Verificar integridad referencial
DO $verify_fk$
DECLARE
    v_orphan_divisions INTEGER;
BEGIN
    RAISE NOTICE '[FK-CHECK] Verificando integridad referencial...';

    -- Verificar sponsor_division_id órfanos
    SELECT COUNT(*) INTO v_orphan_divisions
    FROM core.ipr_party ip
    LEFT JOIN core.organization o ON ip.sponsor_division_id = o.id
    WHERE ip.sponsor_division_id IS NOT NULL
    AND o.id IS NULL;

    IF v_orphan_divisions > 0 THEN
        RAISE WARNING '[FK-CHECK] ✗ Se encontraron % FK órfanos en sponsor_division_id', v_orphan_divisions;
    ELSE
        RAISE NOTICE '[FK-CHECK] ✓ No hay FK órfanos en sponsor_division_id';
    END IF;
END $verify_fk$;

-- Verificar índices creados
DO $verify_indexes$
DECLARE
    v_idx_party_exists BOOLEAN;
    v_idx_ipr_exists BOOLEAN;
BEGIN
    RAISE NOTICE '[INDEX-CHECK] Verificando índices...';

    SELECT EXISTS(
        SELECT 1 FROM pg_indexes
        WHERE schemaname='core'
        AND tablename='ipr_party'
        AND indexname='idx_ipr_party_sponsor_division'
    ) INTO v_idx_party_exists;

    SELECT EXISTS(
        SELECT 1 FROM pg_indexes
        WHERE schemaname='core'
        AND tablename='ipr'
        AND indexname='idx_ipr_municipal_origin'
    ) INTO v_idx_ipr_exists;

    IF v_idx_party_exists THEN
        RAISE NOTICE '[INDEX-CHECK] ✓ Índice idx_ipr_party_sponsor_division existe';
    ELSE
        RAISE WARNING '[INDEX-CHECK] ✗ Índice idx_ipr_party_sponsor_division no existe';
    END IF;

    IF v_idx_ipr_exists THEN
        RAISE NOTICE '[INDEX-CHECK] ✓ Índice idx_ipr_municipal_origin existe';
    ELSE
        RAISE WARNING '[INDEX-CHECK] ✗ Índice idx_ipr_municipal_origin no existe';
    END IF;
END $verify_indexes$;

-- Resumen final
DO $final_summary$
DECLARE
    v_norm4_populated INTEGER;
    v_norm4_total INTEGER;
    v_norm5_true INTEGER;
    v_norm5_false INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  RESUMEN FINAL                                                 ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';

    -- Norm 4 stats
    SELECT
        COUNT(*) FILTER (WHERE sponsor_division_id IS NOT NULL),
        COUNT(*) FILTER (WHERE metadata->>'division' IS NOT NULL)
    INTO v_norm4_populated, v_norm4_total
    FROM core.ipr_party;

    -- Norm 5 stats
    SELECT
        COUNT(*) FILTER (WHERE is_municipal_origin = true),
        COUNT(*) FILTER (WHERE is_municipal_origin = false)
    INTO v_norm5_true, v_norm5_false
    FROM core.ipr
    WHERE is_municipal_origin IS NOT NULL;

    RAISE NOTICE '[NORM-4] sponsor_division_id: %/% registros migrados', v_norm4_populated, v_norm4_total;
    RAISE NOTICE '[NORM-5] is_municipal_origin: % municipales, % sectoriales', v_norm5_true, v_norm5_false;
    RAISE NOTICE '';
    RAISE NOTICE '✓ NORMALIZACION v3.0 FASE MEDIA (CAMPOS 4-5) COMPLETADA';
    RAISE NOTICE '';
END $final_summary$;

-- ============================================================================
-- NOTAS FINALES
-- ============================================================================

DO $final_notes$
BEGIN
    RAISE NOTICE '════════════════════════════════════════════════════════════════';
    RAISE NOTICE 'NOTAS FINALES:';
    RAISE NOTICE '';
    RAISE NOTICE '1. Backups temporales disponibles:';
    RAISE NOTICE '   - _backup_ipr_party_v3_media';
    RAISE NOTICE '   - _backup_ipr_v3_media';
    RAISE NOTICE '';
    RAISE NOTICE '2. Nuevas columnas creadas:';
    RAISE NOTICE '   - core.ipr_party.sponsor_division_id UUID FK';
    RAISE NOTICE '   - core.ipr.is_municipal_origin BOOLEAN';
    RAISE NOTICE '';
    RAISE NOTICE '3. Índices creados:';
    RAISE NOTICE '   - idx_ipr_party_sponsor_division (partial)';
    RAISE NOTICE '   - idx_ipr_municipal_origin (partial)';
    RAISE NOTICE '';
    RAISE NOTICE '4. Mapeo manual usado para divisiones:';
    RAISE NOTICE '   - DIDESO → ORG_GORE-DIDESO';
    RAISE NOTICE '   - DIFOI → ORG_GORE-DIFOI';
    RAISE NOTICE '   - DIPIR → DIPIR';
    RAISE NOTICE '   - DIPLADE → DIPLADE';
    RAISE NOTICE '   - DIT → DIT';
    RAISE NOTICE '';
    RAISE NOTICE '5. Siguiente paso:';
    RAISE NOTICE '   - Ejecutar normalize_jsonb_v3_fase_critica_1-3.sql';
    RAISE NOTICE '';
    RAISE NOTICE '════════════════════════════════════════════════════════════════';
END $final_notes$;

\timing off
