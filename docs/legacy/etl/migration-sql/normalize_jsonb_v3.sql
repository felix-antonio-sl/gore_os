-- ==============================================================================
-- NORMALIZACIÓN JSONB v3.0 - FASE 1: INTEGRIDAD RELACIONAL
-- ==============================================================================
-- ARQUITECTO-GORE v0.1.0
-- Fecha: 2026-01-30
-- Motor: CM-ARTIFACT-GENERATOR
-- Fundamento: docs/AUDITORIA_CATEGORIAL_v3.0.md
--
-- FASE 1 - Integridad Relacional:
--   1. Normalizar RUT en organization (tde:RUT, gnub:IdentificadorTributario)
--   2. Sincronizar EJECUTOR en ipr_party (gnub:hasExecutor)
--   3. Agregar agreement_id FK en ipr_party (gnub:hasAgreement)
--
-- REGISTROS AFECTADOS:
--   - organization.rut: 1,524 registros
--   - ipr_party EJECUTOR sync: 1,646 registros
--   - ipr_party.agreement_id: 476 registros
--
-- PRE-REQUISITOS:
--   - Ejecutar en goreos_model_test primero (ver sección TEST ENVIRONMENT)
--   - Verificar que fn_validate_category_scheme existe
--   - Backup completo de la base de datos
-- ==============================================================================

\set ON_ERROR_STOP on
\timing on

-- ==============================================================================
-- CONFIGURACIÓN
-- ==============================================================================

DO $$ BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '  NORMALIZACIÓN JSONB v3.0 - FASE 1: INTEGRIDAD RELACIONAL             ';
    RAISE NOTICE '  Arquitecto-GORE | Alineación Ontológica                              ';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Ontologías de referencia:';
    RAISE NOTICE '  - tde:RUT (Transformación Digital del Estado)';
    RAISE NOTICE '  - gnub:IdentificadorTributario (GORE Ñuble Ontology)';
    RAISE NOTICE '  - gnub:hasExecutor (relación IPR-Organization)';
    RAISE NOTICE '  - gnub:hasAgreement (relación Party-Agreement)';
    RAISE NOTICE '';
END $$;

-- Crear función helper para reportes (si no existe)
CREATE OR REPLACE FUNCTION report_phase_v3(phase_name TEXT, status TEXT) RETURNS void AS $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '────────────────────────────────────────────────────────────────────────';
    RAISE NOTICE 'FASE: % - %', phase_name, status;
    RAISE NOTICE '────────────────────────────────────────────────────────────────────────';
    RAISE NOTICE '';
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- PRE-EJECUCIÓN: VALIDACIONES DE SEGURIDAD
-- ==============================================================================

SELECT report_phase_v3('PRE-EJECUCIÓN', 'Validaciones de Seguridad');

-- Verificar que fn_validate_category_scheme existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'fn_validate_category_scheme') THEN
        RAISE EXCEPTION 'Función fn_validate_category_scheme NO existe. Ejecutar goreos_ddl.sql primero.';
    END IF;
    RAISE NOTICE '✓ Función fn_validate_category_scheme existe';
END $$;

-- Verificar schema de tablas target
DO $$
BEGIN
    -- Verificar core.organization
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'core' AND table_name = 'organization'
    ) THEN
        RAISE EXCEPTION 'Tabla core.organization NO existe';
    END IF;
    RAISE NOTICE '✓ Tabla core.organization existe';

    -- Verificar core.ipr_party
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'core' AND table_name = 'ipr_party'
    ) THEN
        RAISE EXCEPTION 'Tabla core.ipr_party NO existe';
    END IF;
    RAISE NOTICE '✓ Tabla core.ipr_party existe';

    -- Verificar core.agreement
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'core' AND table_name = 'agreement'
    ) THEN
        RAISE EXCEPTION 'Tabla core.agreement NO existe';
    END IF;
    RAISE NOTICE '✓ Tabla core.agreement existe';
END $$;

-- Verificar rol EJECUTOR en ref.category
DO $$
DECLARE
    ejecutor_id UUID;
BEGIN
    SELECT id INTO ejecutor_id
    FROM ref.category
    WHERE scheme = 'ipr_party_role' AND code = 'EJECUTOR';

    IF ejecutor_id IS NULL THEN
        RAISE EXCEPTION 'Rol EJECUTOR no encontrado en ref.category (scheme=ipr_party_role)';
    END IF;
    RAISE NOTICE '✓ Rol EJECUTOR existe: %', ejecutor_id;
END $$;

-- Conteos pre-migración
DO $$
DECLARE
    org_count INTEGER;
    rut_count INTEGER;
    ipr_count INTEGER;
    executor_missing INTEGER;
    agreement_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO org_count FROM core.organization WHERE deleted_at IS NULL;
    SELECT COUNT(*) INTO rut_count FROM core.organization WHERE metadata->>'rut' IS NOT NULL;
    SELECT COUNT(*) INTO ipr_count FROM core.ipr WHERE executor_id IS NOT NULL AND deleted_at IS NULL;

    SELECT COUNT(*) INTO executor_missing
    FROM core.ipr i
    WHERE i.executor_id IS NOT NULL
      AND i.deleted_at IS NULL
      AND NOT EXISTS (
        SELECT 1 FROM core.ipr_party ip
        JOIN ref.category c ON ip.party_role_id = c.id
        WHERE ip.ipr_id = i.id AND c.code = 'EJECUTOR' AND c.scheme = 'ipr_party_role'
      );

    SELECT COUNT(*) INTO agreement_count
    FROM core.ipr_party WHERE metadata->>'agreement_id' IS NOT NULL;

    RAISE NOTICE '';
    RAISE NOTICE 'Estado Pre-Migración:';
    RAISE NOTICE '  - Organizaciones activas: %', org_count;
    RAISE NOTICE '  - Organizaciones con RUT en metadata: %', rut_count;
    RAISE NOTICE '  - IPRs con executor_id: %', ipr_count;
    RAISE NOTICE '  - IPRs sin EJECUTOR en ipr_party: %', executor_missing;
    RAISE NOTICE '  - ipr_party con agreement_id en metadata: %', agreement_count;
    RAISE NOTICE '';
END $$;

-- ==============================================================================
-- ACCIÓN 1: NORMALIZAR RUT EN ORGANIZATION
-- ==============================================================================
-- Ontología: tde:RUT, gnub:IdentificadorTributario
-- Registros afectados: 1,524
--
-- ROLLBACK:
--   ALTER TABLE core.organization DROP COLUMN IF EXISTS rut CASCADE;
--   DROP INDEX IF EXISTS idx_org_rut;
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('ACCIÓN 1', 'Normalizar RUT en organization (tde:RUT)');

-- 1.1 Crear backup de metadata antes de modificar
DROP TABLE IF EXISTS temp_organization_backup_v3;

CREATE TEMP TABLE temp_organization_backup_v3 AS
SELECT
    id,
    code,
    name,
    metadata,
    now() AS backup_at
FROM core.organization
WHERE metadata->>'rut' IS NOT NULL;

DO $$
DECLARE
    backup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO backup_count FROM temp_organization_backup_v3;
    RAISE NOTICE '✓ Backup creado: % organizaciones en temp_organization_backup_v3', backup_count;
END $$;

-- 1.2 Verificar que columna rut NO existe
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'organization'
          AND column_name = 'rut'
    ) THEN
        RAISE NOTICE '⚠ Columna rut ya existe en core.organization - saltando creación';
    ELSE
        -- Agregar columna rut
        ALTER TABLE core.organization ADD COLUMN rut VARCHAR(12);

        COMMENT ON COLUMN core.organization.rut IS
            'tde:RUT, gnub:IdentificadorTributario - Rol Único Tributario. Identificador único de personas jurídicas en Chile (SII). Formato: XX.XXX.XXX-X. Normalizado desde metadata.rut el 2026-01-30.';

        RAISE NOTICE '✓ Columna rut añadida a core.organization';
    END IF;
END $$;

-- 1.3 Crear índice único parcial (si no existe)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'core'
          AND tablename = 'organization'
          AND indexname = 'idx_org_rut'
    ) THEN
        CREATE UNIQUE INDEX idx_org_rut ON core.organization(rut) WHERE rut IS NOT NULL;
        RAISE NOTICE '✓ Índice único idx_org_rut creado';
    ELSE
        RAISE NOTICE '⚠ Índice idx_org_rut ya existe';
    END IF;
END $$;

-- 1.4 Agregar CHECK constraint para formato RUT chileno
-- Formato válido: X.XXX.XXX-X o XX.XXX.XXX-X (con puntos y guión, dígito verificador puede ser K)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_rut_format'
          AND conrelid = 'core.organization'::regclass
    ) THEN
        ALTER TABLE core.organization ADD CONSTRAINT chk_rut_format
            CHECK (rut IS NULL OR rut ~ '^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$');
        RAISE NOTICE '✓ CHECK constraint chk_rut_format añadido';
    ELSE
        RAISE NOTICE '⚠ CHECK constraint chk_rut_format ya existe';
    END IF;
EXCEPTION
    WHEN check_violation THEN
        RAISE EXCEPTION 'Datos existentes violarían el formato RUT. Revisar metadata antes de continuar.';
END $$;

-- 1.5 Verificar formato de RUTs en metadata antes de migrar
DO $$
DECLARE
    invalid_ruts INTEGER;
    sample_invalid TEXT;
BEGIN
    SELECT COUNT(*), STRING_AGG(metadata->>'rut', ', ' ORDER BY metadata->>'rut')
    INTO invalid_ruts, sample_invalid
    FROM (
        SELECT metadata
        FROM core.organization
        WHERE metadata->>'rut' IS NOT NULL
          AND NOT (metadata->>'rut' ~ '^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$')
        LIMIT 5
    ) sub;

    IF invalid_ruts > 0 THEN
        RAISE WARNING '⚠ % RUTs con formato inválido encontrados. Ejemplos: %', invalid_ruts, sample_invalid;
        RAISE WARNING '  Estos RUTs NO serán migrados. Corregir formato manualmente si es necesario.';
    ELSE
        RAISE NOTICE '✓ Todos los RUTs en metadata tienen formato válido';
    END IF;
END $$;

-- 1.6 Migrar datos: metadata->>'rut' → columna rut
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE core.organization
        SET rut = metadata->>'rut'
        WHERE metadata->>'rut' IS NOT NULL
          AND rut IS NULL  -- Solo si no está ya poblado
          AND (metadata->>'rut' ~ '^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$')  -- Solo formato válido
        RETURNING id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;

    RAISE NOTICE '✓ % organizaciones: rut poblado desde metadata', updated_count;
END $$;

-- 1.7 Marcar metadata como normalizado (NO eliminar rut de metadata para audit trail)
DO $$
DECLARE
    marked_count INTEGER;
BEGIN
    WITH marked AS (
        UPDATE core.organization
        SET metadata = metadata || jsonb_build_object(
            'rut_normalized_at', now()::text,
            'rut_normalized_version', 'v3.0'
        )
        WHERE rut IS NOT NULL
          AND metadata->>'rut' IS NOT NULL
          AND NOT (metadata ? 'rut_normalized_at')
        RETURNING id
    )
    SELECT COUNT(*) INTO marked_count FROM marked;

    RAISE NOTICE '✓ % organizaciones: metadata marcado con rut_normalized_at', marked_count;
END $$;

-- 1.8 Verificación post-migración
DO $$
DECLARE
    total_rut_metadata INTEGER;
    total_rut_column INTEGER;
    missing INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_rut_metadata
    FROM core.organization
    WHERE metadata->>'rut' IS NOT NULL;

    SELECT COUNT(*) INTO total_rut_column
    FROM core.organization
    WHERE rut IS NOT NULL;

    missing := total_rut_metadata - total_rut_column;

    RAISE NOTICE '';
    RAISE NOTICE 'Verificación ACCIÓN 1 - RUT:';
    RAISE NOTICE '  - RUTs en metadata: %', total_rut_metadata;
    RAISE NOTICE '  - RUTs en columna: %', total_rut_column;
    RAISE NOTICE '  - Diferencia: % (RUTs con formato inválido no migrados)', missing;

    IF total_rut_column >= total_rut_metadata * 0.99 THEN
        RAISE NOTICE '✓ PASS: ≥99%% de RUTs migrados exitosamente';
    ELSE
        RAISE WARNING 'WARN: <99%% de RUTs migrados. Revisar formato de datos.';
    END IF;
END $$;

COMMIT;

-- ==============================================================================
-- ACCIÓN 2: SINCRONIZAR EJECUTOR EN IPR_PARTY
-- ==============================================================================
-- Ontología: gnub:hasExecutor
-- Registros afectados: 1,646
--
-- PROBLEMA: ipr.executor_id tiene datos pero ipr_party no tiene registros EJECUTOR
-- SOLUCIÓN: Crear registros en ipr_party para cada IPR con executor_id
--
-- ROLLBACK:
--   DELETE FROM core.ipr_party
--   WHERE metadata->>'source' = 'SYNC_FROM_IPR_EXECUTOR_ID';
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('ACCIÓN 2', 'Sincronizar EJECUTOR en ipr_party (gnub:hasExecutor)');

-- 2.1 Crear backup de ipr_party antes de insertar
DROP TABLE IF EXISTS temp_ipr_party_backup_v3;

CREATE TEMP TABLE temp_ipr_party_backup_v3 AS
SELECT
    id,
    ipr_id,
    organization_id,
    party_role_id,
    is_primary,
    metadata,
    now() AS backup_at
FROM core.ipr_party
WHERE deleted_at IS NULL;

DO $$
DECLARE
    backup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO backup_count FROM temp_ipr_party_backup_v3;
    RAISE NOTICE '✓ Backup creado: % registros ipr_party en temp_ipr_party_backup_v3', backup_count;
END $$;

-- 2.2 Verificar conteo antes de insertar
DO $$
DECLARE
    to_sync INTEGER;
BEGIN
    SELECT COUNT(*) INTO to_sync
    FROM core.ipr i
    WHERE i.executor_id IS NOT NULL
      AND i.deleted_at IS NULL
      AND NOT EXISTS (
        SELECT 1 FROM core.ipr_party ip
        JOIN ref.category c ON ip.party_role_id = c.id
        WHERE ip.ipr_id = i.id
          AND c.code = 'EJECUTOR'
          AND c.scheme = 'ipr_party_role'
          AND ip.deleted_at IS NULL
      );

    RAISE NOTICE '✓ IPRs a sincronizar (executor_id → ipr_party): %', to_sync;
END $$;

-- 2.3 Insertar registros EJECUTOR en ipr_party
DO $$
DECLARE
    inserted_count INTEGER;
    ejecutor_role_id UUID;
BEGIN
    -- Obtener ID del rol EJECUTOR
    SELECT id INTO ejecutor_role_id
    FROM ref.category
    WHERE scheme = 'ipr_party_role' AND code = 'EJECUTOR';

    WITH inserted AS (
        INSERT INTO core.ipr_party (
            ipr_id,
            organization_id,
            party_role_id,
            is_primary,
            metadata
        )
        SELECT
            i.id,
            i.executor_id,
            ejecutor_role_id,
            TRUE,  -- EJECUTOR es siempre primary para su IPR
            jsonb_build_object(
                'source', 'SYNC_FROM_IPR_EXECUTOR_ID',
                'synced_at', now()::text,
                'sync_version', 'v3.0',
                'ontology_alignment', 'gnub:hasExecutor'
            )
        FROM core.ipr i
        WHERE i.executor_id IS NOT NULL
          AND i.deleted_at IS NULL
          AND NOT EXISTS (
            SELECT 1 FROM core.ipr_party ip
            JOIN ref.category c ON ip.party_role_id = c.id
            WHERE ip.ipr_id = i.id
              AND c.code = 'EJECUTOR'
              AND c.scheme = 'ipr_party_role'
              AND ip.deleted_at IS NULL
          )
        ON CONFLICT (ipr_id, organization_id, party_role_id) DO NOTHING
        RETURNING id
    )
    SELECT COUNT(*) INTO inserted_count FROM inserted;

    RAISE NOTICE '✓ % registros EJECUTOR insertados en ipr_party', inserted_count;
END $$;

-- 2.4 Verificación post-inserción
DO $$
DECLARE
    iprs_with_executor INTEGER;
    iprs_with_party_ejecutor INTEGER;
    missing INTEGER;
BEGIN
    SELECT COUNT(*) INTO iprs_with_executor
    FROM core.ipr
    WHERE executor_id IS NOT NULL AND deleted_at IS NULL;

    SELECT COUNT(DISTINCT i.id) INTO iprs_with_party_ejecutor
    FROM core.ipr i
    JOIN core.ipr_party ip ON ip.ipr_id = i.id
    JOIN ref.category c ON ip.party_role_id = c.id
    WHERE i.executor_id IS NOT NULL
      AND i.deleted_at IS NULL
      AND ip.deleted_at IS NULL
      AND c.code = 'EJECUTOR'
      AND c.scheme = 'ipr_party_role';

    missing := iprs_with_executor - iprs_with_party_ejecutor;

    RAISE NOTICE '';
    RAISE NOTICE 'Verificación ACCIÓN 2 - EJECUTOR sync:';
    RAISE NOTICE '  - IPRs con executor_id: %', iprs_with_executor;
    RAISE NOTICE '  - IPRs con EJECUTOR en ipr_party: %', iprs_with_party_ejecutor;
    RAISE NOTICE '  - Faltantes: %', missing;

    IF missing = 0 THEN
        RAISE NOTICE '✓ PASS: 100%% de EJECUTOR sincronizados';
    ELSE
        RAISE WARNING 'WARN: % IPRs aún sin EJECUTOR en ipr_party. Posible constraint violation.', missing;
    END IF;
END $$;

-- 2.5 Verificar integridad: executor_id == organization_id para rol EJECUTOR
DO $$
DECLARE
    mismatches INTEGER;
BEGIN
    SELECT COUNT(*) INTO mismatches
    FROM core.ipr i
    JOIN core.ipr_party ip ON ip.ipr_id = i.id
    JOIN ref.category c ON ip.party_role_id = c.id
    WHERE c.code = 'EJECUTOR'
      AND c.scheme = 'ipr_party_role'
      AND i.deleted_at IS NULL
      AND ip.deleted_at IS NULL
      AND i.executor_id != ip.organization_id;

    IF mismatches > 0 THEN
        RAISE WARNING '⚠ % IPRs tienen executor_id diferente de ipr_party.organization_id para EJECUTOR', mismatches;
    ELSE
        RAISE NOTICE '✓ Integridad verificada: executor_id == ipr_party.organization_id para todos los EJECUTOR';
    END IF;
END $$;

COMMIT;

-- ==============================================================================
-- ACCIÓN 3: AGREGAR agreement_id FK EN IPR_PARTY
-- ==============================================================================
-- Ontología: gnub:hasAgreement
-- Registros afectados: 476
--
-- PROBLEMA: ipr_party tiene agreement_id en metadata sin FK formal
-- SOLUCIÓN: Crear columna agreement_id con FK a core.agreement
--
-- ROLLBACK:
--   ALTER TABLE core.ipr_party DROP COLUMN IF EXISTS agreement_id CASCADE;
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('ACCIÓN 3', 'Agregar agreement_id FK en ipr_party (gnub:hasAgreement)');

-- 3.1 Verificar que columna agreement_id NO existe
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'ipr_party'
          AND column_name = 'agreement_id'
    ) THEN
        RAISE NOTICE '⚠ Columna agreement_id ya existe en core.ipr_party - saltando creación';
    ELSE
        -- Agregar columna agreement_id
        ALTER TABLE core.ipr_party ADD COLUMN agreement_id UUID REFERENCES core.agreement(id);

        COMMENT ON COLUMN core.ipr_party.agreement_id IS
            'gnub:hasAgreement - Convenio o mandato que formaliza la participación de la organización en el IPR. Normalizado desde metadata.agreement_id el 2026-01-30.';

        RAISE NOTICE '✓ Columna agreement_id añadida a core.ipr_party';
    END IF;
END $$;

-- 3.2 Verificar datos antes de migrar
DO $$
DECLARE
    total_in_metadata INTEGER;
    valid_uuids INTEGER;
    invalid_uuids INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_in_metadata
    FROM core.ipr_party
    WHERE metadata->>'agreement_id' IS NOT NULL;

    SELECT COUNT(*) INTO valid_uuids
    FROM core.ipr_party ip
    JOIN core.agreement a ON a.id = (ip.metadata->>'agreement_id')::uuid
    WHERE ip.metadata->>'agreement_id' IS NOT NULL;

    invalid_uuids := total_in_metadata - valid_uuids;

    RAISE NOTICE '✓ ipr_party con agreement_id en metadata: %', total_in_metadata;
    RAISE NOTICE '  - UUIDs válidos (existen en core.agreement): %', valid_uuids;
    RAISE NOTICE '  - UUIDs inválidos/huérfanos: %', invalid_uuids;

    IF invalid_uuids > 0 THEN
        RAISE WARNING '⚠ % agreement_id en metadata no tienen agreement correspondiente', invalid_uuids;
    END IF;
END $$;

-- 3.3 Crear índice para agreement_id (si no existe)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'core'
          AND tablename = 'ipr_party'
          AND indexname = 'idx_ipr_party_agreement'
    ) THEN
        CREATE INDEX idx_ipr_party_agreement ON core.ipr_party(agreement_id)
            WHERE agreement_id IS NOT NULL;
        RAISE NOTICE '✓ Índice idx_ipr_party_agreement creado';
    ELSE
        RAISE NOTICE '⚠ Índice idx_ipr_party_agreement ya existe';
    END IF;
END $$;

-- 3.4 Migrar datos: metadata->>'agreement_id' → columna agreement_id
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE core.ipr_party ip
        SET agreement_id = (ip.metadata->>'agreement_id')::uuid
        FROM core.agreement a
        WHERE ip.metadata->>'agreement_id' IS NOT NULL
          AND ip.agreement_id IS NULL  -- Solo si no está ya poblado
          AND a.id = (ip.metadata->>'agreement_id')::uuid  -- Solo si el agreement existe
        RETURNING ip.id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;

    RAISE NOTICE '✓ % registros ipr_party: agreement_id poblado desde metadata', updated_count;
END $$;

-- 3.5 Marcar metadata como normalizado
DO $$
DECLARE
    marked_count INTEGER;
BEGIN
    WITH marked AS (
        UPDATE core.ipr_party
        SET metadata = metadata || jsonb_build_object(
            'agreement_id_normalized_at', now()::text,
            'agreement_id_normalized_version', 'v3.0'
        )
        WHERE agreement_id IS NOT NULL
          AND metadata->>'agreement_id' IS NOT NULL
          AND NOT (metadata ? 'agreement_id_normalized_at')
        RETURNING id
    )
    SELECT COUNT(*) INTO marked_count FROM marked;

    RAISE NOTICE '✓ % registros ipr_party: metadata marcado con agreement_id_normalized_at', marked_count;
END $$;

-- 3.6 Verificación post-migración
DO $$
DECLARE
    total_metadata INTEGER;
    total_column INTEGER;
    coverage NUMERIC;
BEGIN
    SELECT COUNT(*) INTO total_metadata
    FROM core.ipr_party
    WHERE metadata->>'agreement_id' IS NOT NULL;

    SELECT COUNT(*) INTO total_column
    FROM core.ipr_party
    WHERE agreement_id IS NOT NULL;

    coverage := ROUND(total_column::numeric / NULLIF(total_metadata, 0) * 100, 1);

    RAISE NOTICE '';
    RAISE NOTICE 'Verificación ACCIÓN 3 - agreement_id:';
    RAISE NOTICE '  - agreement_id en metadata: %', total_metadata;
    RAISE NOTICE '  - agreement_id en columna: %', total_column;
    RAISE NOTICE '  - Cobertura: %%', coverage;

    IF coverage >= 95 THEN
        RAISE NOTICE '✓ PASS: ≥95%% de agreement_id migrados';
    ELSE
        RAISE WARNING 'WARN: <95%% cobertura. Revisar agreements huérfanos.';
    END IF;
END $$;

COMMIT;

-- ==============================================================================
-- POST-EJECUCIÓN: VERIFICACIONES FINALES
-- ==============================================================================

SELECT report_phase_v3('POST-EJECUCIÓN', 'Verificaciones Finales');

-- Reporte consolidado
DO $$
DECLARE
    org_rut_count INTEGER;
    party_ejecutor_count INTEGER;
    party_agreement_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO org_rut_count
    FROM core.organization WHERE rut IS NOT NULL;

    SELECT COUNT(*) INTO party_ejecutor_count
    FROM core.ipr_party ip
    JOIN ref.category c ON ip.party_role_id = c.id
    WHERE c.code = 'EJECUTOR'
      AND c.scheme = 'ipr_party_role'
      AND ip.deleted_at IS NULL;

    SELECT COUNT(*) INTO party_agreement_count
    FROM core.ipr_party WHERE agreement_id IS NOT NULL;

    RAISE NOTICE '';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '  RESUMEN FASE 1 - INTEGRIDAD RELACIONAL                               ';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '';
    RAISE NOTICE '  ACCIÓN 1 - RUT normalizado:';
    RAISE NOTICE '    - Organizaciones con rut: %', org_rut_count;
    RAISE NOTICE '    - Ontología: tde:RUT, gnub:IdentificadorTributario';
    RAISE NOTICE '';
    RAISE NOTICE '  ACCIÓN 2 - EJECUTOR sincronizado:';
    RAISE NOTICE '    - Registros EJECUTOR en ipr_party: %', party_ejecutor_count;
    RAISE NOTICE '    - Ontología: gnub:hasExecutor';
    RAISE NOTICE '';
    RAISE NOTICE '  ACCIÓN 3 - agreement_id normalizado:';
    RAISE NOTICE '    - ipr_party con agreement_id FK: %', party_agreement_count;
    RAISE NOTICE '    - Ontología: gnub:hasAgreement';
    RAISE NOTICE '';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '';
END $$;

-- Análisis de tablas modificadas para query planner
ANALYZE core.organization;
ANALYZE core.ipr_party;

DO $$
BEGIN
    RAISE NOTICE '✓ ANALYZE ejecutado en core.organization y core.ipr_party';
END $$;

-- ==============================================================================
-- INSTRUCCIONES DE ROLLBACK
-- ==============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '────────────────────────────────────────────────────────────────────────';
    RAISE NOTICE 'INSTRUCCIONES DE ROLLBACK (si es necesario):';
    RAISE NOTICE '────────────────────────────────────────────────────────────────────────';
    RAISE NOTICE '';
    RAISE NOTICE '-- ROLLBACK ACCIÓN 1 (RUT):';
    RAISE NOTICE '   UPDATE core.organization SET rut = NULL;';
    RAISE NOTICE '   ALTER TABLE core.organization DROP CONSTRAINT IF EXISTS chk_rut_format;';
    RAISE NOTICE '   DROP INDEX IF EXISTS idx_org_rut;';
    RAISE NOTICE '   ALTER TABLE core.organization DROP COLUMN IF EXISTS rut;';
    RAISE NOTICE '';
    RAISE NOTICE '-- ROLLBACK ACCIÓN 2 (EJECUTOR sync):';
    RAISE NOTICE '   DELETE FROM core.ipr_party';
    RAISE NOTICE '   WHERE metadata->>''source'' = ''SYNC_FROM_IPR_EXECUTOR_ID'';';
    RAISE NOTICE '';
    RAISE NOTICE '-- ROLLBACK ACCIÓN 3 (agreement_id):';
    RAISE NOTICE '   UPDATE core.ipr_party SET agreement_id = NULL;';
    RAISE NOTICE '   DROP INDEX IF EXISTS idx_ipr_party_agreement;';
    RAISE NOTICE '   ALTER TABLE core.ipr_party DROP COLUMN IF EXISTS agreement_id;';
    RAISE NOTICE '';
    RAISE NOTICE '-- RESTAURAR DESDE BACKUP (tablas temp):';
    RAISE NOTICE '   SELECT * FROM temp_organization_backup_v3;';
    RAISE NOTICE '   SELECT * FROM temp_ipr_party_backup_v3;';
    RAISE NOTICE '';
    RAISE NOTICE '────────────────────────────────────────────────────────────────────────';
END $$;

-- ==============================================================================
-- REPORTE FINAL
-- ==============================================================================

DO $$ BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '  NORMALIZACIÓN JSONB v3.0 - FASE 1 COMPLETADA                          ';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Versión: v3.0 - Fase 1';
    RAISE NOTICE 'Arquitecto: ARQUITECTO-GORE v0.1.0';
    RAISE NOTICE 'Fecha ejecución: %', now();
    RAISE NOTICE '';
    RAISE NOTICE 'Próximos pasos:';
    RAISE NOTICE '  1. Verificar queries de aplicación (apps/migration_viewer)';
    RAISE NOTICE '  2. Ejecutar tests de integridad referencial';
    RAISE NOTICE '  3. Continuar con Fase 2 (Personas): estamento, technical_referent';
    RAISE NOTICE '';
    RAISE NOTICE 'Documentación:';
    RAISE NOTICE '  - docs/AUDITORIA_CATEGORIAL_v3.0.md';
    RAISE NOTICE '  - etl/migration/sql/normalize_jsonb_v3.sql';
    RAISE NOTICE '';
END $$;

-- Limpiar función helper
DROP FUNCTION IF EXISTS report_phase_v3(TEXT, TEXT);

-- ==============================================================================
-- FIN FASE 1
-- ==============================================================================
