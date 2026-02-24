-- ============================================================================
-- VERIFICACION RAPIDA: NORMALIZACION JSONB V3 - FASE MEDIA (CAMPOS 1-3)
-- ============================================================================
-- Script de verificación PRE-EJECUCION para validar condiciones
-- Ejecutar ANTES de normalize_jsonb_v3_fase_media_1-3.sql
--
-- USO: docker exec -i goreos_db psql -U goreos -d goreos_model < verify_normalize_jsonb_v3_fase_media_1-3.sql
-- ============================================================================

\echo ''
\echo '============================================================================'
\echo 'VERIFICACION PRE-MIGRACION: NORMALIZACION JSONB V3 - FASE MEDIA (CAMPOS 1-3)'
\echo '============================================================================'
\echo ''

-- Configuración
SET client_min_messages = NOTICE;

-- ============================================================================
-- 1. VERIFICAR QUE TABLAS/SCHEMES NO EXISTAN (Prerequisito)
-- ============================================================================

\echo '1. Verificando que tablas y schemes NO existan...'

DO $$
DECLARE
    v_position_exists BOOLEAN;
    v_prof_qual_exists BOOLEAN;
    v_cgr_outcome_exists BOOLEAN;
BEGIN
    -- Verificar tabla position
    SELECT EXISTS(SELECT 1 FROM information_schema.tables
                  WHERE table_schema = 'core' AND table_name = 'position')
    INTO v_position_exists;

    -- Verificar scheme professional_qualification
    SELECT EXISTS(SELECT 1 FROM ref.category WHERE scheme = 'professional_qualification')
    INTO v_prof_qual_exists;

    -- Verificar scheme cgr_outcome
    SELECT EXISTS(SELECT 1 FROM ref.category WHERE scheme = 'cgr_outcome')
    INTO v_cgr_outcome_exists;

    RAISE NOTICE '';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'PREREQUISITOS: TABLAS Y SCHEMES';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'core.position existe: %', CASE WHEN v_position_exists THEN 'SI - ABORTAR' ELSE 'NO - OK' END;
    RAISE NOTICE 'scheme professional_qualification existe: %', CASE WHEN v_prof_qual_exists THEN 'SI - ABORTAR' ELSE 'NO - OK' END;
    RAISE NOTICE 'scheme cgr_outcome existe: %', CASE WHEN v_cgr_outcome_exists THEN 'SI - SE COMPLETARA' ELSE 'NO - SE CREARA' END;
    RAISE NOTICE '====================================================================';
    RAISE NOTICE '';

    IF v_position_exists OR v_prof_qual_exists THEN
        RAISE WARNING 'ADVERTENCIA: Una o más estructuras críticas ya existen. La migración ABORTARA.';
    ELSE
        RAISE NOTICE 'ESTADO: OK - Verificaciones críticas pasaron';
        IF v_cgr_outcome_exists THEN
            RAISE NOTICE 'NOTA: El scheme cgr_outcome existe, se agregaran categorias faltantes.';
        END IF;
    END IF;
END $$;

-- ============================================================================
-- 2. ANALIZAR DATOS FUENTE
-- ============================================================================

\echo ''
\echo '2. Analizando datos fuente...'
\echo ''

-- 2.1 Analizar cargo_ultimo
\echo '2.1 Campo: core.person.metadata->>"cargo_ultimo"'

SELECT
    COUNT(*) as total_personas,
    COUNT(*) FILTER (WHERE metadata->>'cargo_ultimo' IS NOT NULL) as con_cargo,
    COUNT(DISTINCT metadata->>'cargo_ultimo') as cargos_unicos
FROM core.person;

\echo ''
\echo 'Top 10 cargos más frecuentes:'
SELECT
    metadata->>'cargo_ultimo' as cargo,
    COUNT(*) as personas
FROM core.person
WHERE metadata->>'cargo_ultimo' IS NOT NULL
GROUP BY cargo
ORDER BY personas DESC
LIMIT 10;

-- 2.2 Analizar calificacion
\echo ''
\echo '2.2 Campo: core.person.metadata->>"calificacion"'

SELECT
    COUNT(*) as total_personas,
    COUNT(*) FILTER (WHERE metadata->>'calificacion' IS NOT NULL) as con_calificacion,
    COUNT(DISTINCT metadata->>'calificacion') as calificaciones_unicas
FROM core.person;

\echo ''
\echo 'Top 15 calificaciones más frecuentes:'
SELECT
    metadata->>'calificacion' as calificacion,
    COUNT(*) as personas
FROM core.person
WHERE metadata->>'calificacion' IS NOT NULL
GROUP BY calificacion
ORDER BY personas DESC
LIMIT 15;

-- 2.3 Analizar estado_cgr_norm
\echo ''
\echo '2.3 Campo: core.agreement.metadata->>"estado_cgr_norm"'

SELECT
    COUNT(*) as total_agreements,
    COUNT(*) FILTER (WHERE metadata->>'estado_cgr_norm' IS NOT NULL) as con_estado_cgr,
    COUNT(DISTINCT metadata->>'estado_cgr_norm') as estados_unicos
FROM core.agreement;

\echo ''
\echo 'Distribución de estados CGR:'
SELECT
    metadata->>'estado_cgr_norm' as estado_cgr,
    COUNT(*) as agreements
FROM core.agreement
WHERE metadata->>'estado_cgr_norm' IS NOT NULL
GROUP BY estado_cgr
ORDER BY agreements DESC;

-- ============================================================================
-- 3. VERIFICAR FUNCIÓN DE VALIDACIÓN
-- ============================================================================

\echo ''
\echo '3. Verificando función fn_validate_category_scheme...'

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'fn_validate_category_scheme') THEN
        RAISE EXCEPTION 'Función fn_validate_category_scheme NO existe. Abortar migración.';
    ELSE
        RAISE NOTICE 'Función fn_validate_category_scheme: EXISTE - OK';
    END IF;
END $$;

-- ============================================================================
-- 4. VERIFICAR ESPACIO EN DISCO
-- ============================================================================

\echo ''
\echo '4. Verificando espacio en disco...'

SELECT
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'goreos_model';

-- ============================================================================
-- 5. VERIFICAR INTEGRIDAD REFERENCIAL ACTUAL
-- ============================================================================

\echo ''
\echo '5. Verificando integridad referencial actual...'

-- Verificar personas sin organización (afecta position.organization_id)
SELECT
    COUNT(*) as personas_sin_org,
    ROUND(COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM core.person) * 100, 2) as pct
FROM core.person
WHERE organization_id IS NULL;

-- Verificar agreements con metadata completo
SELECT
    COUNT(*) as agreements_total,
    COUNT(*) FILTER (WHERE metadata IS NOT NULL) as con_metadata,
    COUNT(*) FILTER (WHERE metadata = '{}'::jsonb) as metadata_vacio
FROM core.agreement;

-- ============================================================================
-- 6. PREVIEW DE MAPEO: calificacion → professional_qualification
-- ============================================================================

\echo ''
\echo '6. Preview de mapeo: calificacion → professional_qualification'
\echo ''

WITH mapping_preview AS (
    SELECT
        metadata->>'calificacion' as original,
        CASE
            WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIER%COMERCIAL%' THEN 'INGENIERO_COMERCIAL'
            WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIERO CIVIL%'
                 AND NOT UPPER(metadata->>'calificacion') LIKE '%INDUSTRIAL%' THEN 'INGENIERO_CIVIL'
            WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIERO%INDUSTRIAL%' THEN 'INGENIERO_INDUSTRIAL'
            WHEN UPPER(metadata->>'calificacion') LIKE '%CONSTRUCTOR%' THEN 'INGENIERO_CONSTRUCTOR'
            WHEN UPPER(metadata->>'calificacion') LIKE '%ARQUITECTO%' THEN 'ARQUITECTO'
            WHEN UPPER(metadata->>'calificacion') LIKE '%ABOGAD%' THEN 'ABOGADO'
            WHEN UPPER(metadata->>'calificacion') LIKE '%CONTADOR%' THEN 'CONTADOR'
            WHEN UPPER(metadata->>'calificacion') LIKE '%ADMINISTRA%PUBLIC%' THEN 'ADMINISTRADOR_PUBLICO'
            WHEN UPPER(metadata->>'calificacion') LIKE '%TRABAJADOR%SOCIAL%' THEN 'TRABAJADOR_SOCIAL'
            WHEN UPPER(metadata->>'calificacion') LIKE '%PERIODISTA%' THEN 'PERIODISTA'
            WHEN UPPER(metadata->>'calificacion') LIKE '%TECNICO%' THEN 'TECNICO'
            WHEN UPPER(metadata->>'calificacion') LIKE '%LICENCIA%MEDIA%' THEN 'LICENCIA_MEDIA'
            WHEN UPPER(metadata->>'calificacion') LIKE '%SECRETARIA%' THEN 'SECRETARIA'
            WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIER%' THEN 'INGENIERO_OTROS'
            ELSE 'OTROS'
        END as mapped_code
    FROM core.person
    WHERE metadata->>'calificacion' IS NOT NULL
)
SELECT
    mapped_code,
    COUNT(*) as total_personas,
    COUNT(DISTINCT original) as calificaciones_originales
FROM mapping_preview
GROUP BY mapped_code
ORDER BY total_personas DESC;

\echo ''
\echo 'Ejemplos de mapeo por categoría:'
WITH mapping_preview AS (
    SELECT
        metadata->>'calificacion' as original,
        CASE
            WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIER%COMERCIAL%' THEN 'INGENIERO_COMERCIAL'
            WHEN UPPER(metadata->>'calificacion') LIKE '%ARQUITECTO%' THEN 'ARQUITECTO'
            WHEN UPPER(metadata->>'calificacion') LIKE '%ABOGAD%' THEN 'ABOGADO'
            WHEN UPPER(metadata->>'calificacion') LIKE '%CONTADOR%' THEN 'CONTADOR'
            ELSE 'OTROS'
        END as mapped_code
    FROM core.person
    WHERE metadata->>'calificacion' IS NOT NULL
)
SELECT
    mapped_code,
    STRING_AGG(DISTINCT original, ', ' ORDER BY original) as ejemplos
FROM (
    SELECT mapped_code, original,
           ROW_NUMBER() OVER (PARTITION BY mapped_code ORDER BY original) as rn
    FROM mapping_preview
) t
WHERE rn <= 3
GROUP BY mapped_code
ORDER BY mapped_code;

-- ============================================================================
-- 7. RESUMEN FINAL
-- ============================================================================

\echo ''
\echo '============================================================================'
\echo 'RESUMEN DE VERIFICACION'
\echo '============================================================================'

DO $$
DECLARE
    v_person_count INTEGER;
    v_cargo_count INTEGER;
    v_calificacion_count INTEGER;
    v_agreement_count INTEGER;
    v_cgr_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_person_count FROM core.person WHERE metadata IS NOT NULL;
    SELECT COUNT(DISTINCT metadata->>'cargo_ultimo') INTO v_cargo_count
        FROM core.person WHERE metadata->>'cargo_ultimo' IS NOT NULL;
    SELECT COUNT(DISTINCT metadata->>'calificacion') INTO v_calificacion_count
        FROM core.person WHERE metadata->>'calificacion' IS NOT NULL;
    SELECT COUNT(*) INTO v_agreement_count
        FROM core.agreement WHERE metadata->>'estado_cgr_norm' IS NOT NULL;
    SELECT COUNT(DISTINCT metadata->>'estado_cgr_norm') INTO v_cgr_count
        FROM core.agreement WHERE metadata->>'estado_cgr_norm' IS NOT NULL;

    RAISE NOTICE '';
    RAISE NOTICE 'DATOS A MIGRAR:';
    RAISE NOTICE '  FASE 1 - cargo_ultimo:';
    RAISE NOTICE '    - Personas con metadata: %', v_person_count;
    RAISE NOTICE '    - Cargos únicos a crear: %', v_cargo_count;
    RAISE NOTICE '';
    RAISE NOTICE '  FASE 2 - calificacion:';
    RAISE NOTICE '    - Personas con calificación: %', (SELECT COUNT(*) FROM core.person WHERE metadata->>'calificacion' IS NOT NULL);
    RAISE NOTICE '    - Calificaciones únicas: %', v_calificacion_count;
    RAISE NOTICE '    - Categorías a crear: 17';
    RAISE NOTICE '';
    RAISE NOTICE '  FASE 3 - estado_cgr_norm:';
    RAISE NOTICE '    - Agreements con estado CGR: %', v_agreement_count;
    RAISE NOTICE '    - Estados únicos: %', v_cgr_count;
    RAISE NOTICE '    - Categorías a crear: 4';
    RAISE NOTICE '';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'LISTO PARA EJECUTAR: normalize_jsonb_v3_fase_media_1-3.sql';
    RAISE NOTICE '====================================================================';
END $$;

\echo ''
\echo 'FIN DE VERIFICACION'
\echo ''
