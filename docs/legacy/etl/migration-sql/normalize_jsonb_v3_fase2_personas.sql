-- ==============================================================================
-- NORMALIZACIÓN JSONB v3.0 - FASE 2: PERSONAS
-- ==============================================================================
-- ARQUITECTO-GORE v0.1.0
-- Fecha: 2026-01-30
-- Motor: CM-ARTIFACT-GENERATOR
-- Fundamento: AUDITORIA_CATEGORIAL_v3.0.md (Secciones 3, 4)
--
-- SCOPE:
--   1. Crear scheme 'estamento' + columna estamento_id en core.person (110 registros)
--   2. Agregar technical_referent_id en core.agreement (389 registros)
--
-- ALINEAMIENTO ONTOLÓGICO:
--   - tde:Estamento (Transformación Digital del Estado)
--   - gnub:TechnicalReferent (GORE Ñuble Ontology)
--   - tde:ResponsableAsignado (Responsable de seguimiento técnico)
--
-- PREREQUISITOS:
--   - fn_validate_category_scheme() debe existir (goreos_ddl.sql)
--   - core.person con metadata->>'estamento' poblado
--   - core.agreement con metadata->>'referente_tecnico' poblado
-- ==============================================================================

\set ON_ERROR_STOP on
\timing on

-- ==============================================================================
-- CONFIGURACIÓN
-- ==============================================================================

DO $$ BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '  NORMALIZACIÓN JSONB v3.0 - FASE 2: PERSONAS';
    RAISE NOTICE '  Arquitecto-GORE | Coherencia Categorial';
    RAISE NOTICE '  Ontología: tde:Estamento, gnub:TechnicalReferent';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '';
END $$;

-- Crear función helper para reportes
CREATE OR REPLACE FUNCTION report_phase_v3(phase_name TEXT, status TEXT) RETURNS void AS $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '------------------------------------------------------------------------';
    RAISE NOTICE 'FASE 2.%: %', phase_name, status;
    RAISE NOTICE '------------------------------------------------------------------------';
    RAISE NOTICE '';
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- PRE-EJECUCIÓN: VALIDACIONES
-- ==============================================================================

SELECT report_phase_v3('0', 'Validaciones de Seguridad');

-- Validar que función de coherencia categorial existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'fn_validate_category_scheme') THEN
        RAISE EXCEPTION 'Función fn_validate_category_scheme NO existe. Ejecutar goreos_ddl.sql primero.';
    END IF;
    RAISE NOTICE '  [OK] Función fn_validate_category_scheme existe';
END $$;

-- Validar que core.person tiene metadata con estamento
DO $$
DECLARE
    person_count INTEGER;
    estamento_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO person_count FROM core.person WHERE deleted_at IS NULL;
    SELECT COUNT(*) INTO estamento_count FROM core.person WHERE metadata->>'estamento' IS NOT NULL;

    IF person_count = 0 THEN
        RAISE EXCEPTION 'Tabla core.person está vacía.';
    END IF;

    RAISE NOTICE '  [OK] core.person: % registros, % con estamento en metadata', person_count, estamento_count;
END $$;

-- Validar que core.agreement tiene metadata con referente_tecnico
DO $$
DECLARE
    agreement_count INTEGER;
    referente_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO agreement_count FROM core.agreement WHERE deleted_at IS NULL;
    SELECT COUNT(*) INTO referente_count FROM core.agreement WHERE metadata->>'referente_tecnico' IS NOT NULL;

    RAISE NOTICE '  [OK] core.agreement: % registros, % con referente_tecnico en metadata', agreement_count, referente_count;
END $$;

-- ==============================================================================
-- BACKUP: Snapshot de datos pre-migración
-- ==============================================================================

SELECT report_phase_v3('0.5', 'Creación de Backups');

-- Backup de persons con estamento
DROP TABLE IF EXISTS temp_person_estamento_backup;
CREATE TEMP TABLE temp_person_estamento_backup AS
SELECT
    id,
    names,
    paternal_surname,
    maternal_surname,
    metadata,
    metadata->>'estamento' AS estamento_original,
    now() AS backup_at
FROM core.person
WHERE metadata->>'estamento' IS NOT NULL;

DO $$
DECLARE
    backup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO backup_count FROM temp_person_estamento_backup;
    RAISE NOTICE '  [OK] Backup persons con estamento: % registros', backup_count;
END $$;

-- Backup de agreements con referente_tecnico
DROP TABLE IF EXISTS temp_agreement_referente_backup;
CREATE TEMP TABLE temp_agreement_referente_backup AS
SELECT
    id,
    agreement_number,
    metadata,
    metadata->>'referente_tecnico' AS referente_original,
    now() AS backup_at
FROM core.agreement
WHERE metadata->>'referente_tecnico' IS NOT NULL;

DO $$
DECLARE
    backup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO backup_count FROM temp_agreement_referente_backup;
    RAISE NOTICE '  [OK] Backup agreements con referente_tecnico: % registros', backup_count;
END $$;

-- ==============================================================================
-- FASE 2.1: CREAR SCHEME 'estamento'
-- ==============================================================================
-- Ontología: tde:Estamento
-- Alineamiento: Clasificación funcionaria chilena (Ley 18.834 Estatuto Administrativo)
-- Valores: PROFESIONAL, DIRECTIVO, ADMINISTRATIVO, TECNICO, AUXILIAR, HONORARIOS, AUTORIDAD
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('1', 'Crear Scheme estamento (tde:Estamento)');

-- 2.1.1 Verificar si scheme ya existe
DO $$
DECLARE
    existing_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO existing_count
    FROM ref.category WHERE scheme = 'estamento';

    IF existing_count > 0 THEN
        RAISE NOTICE '  [INFO] Scheme estamento ya existe con % valores', existing_count;
    END IF;
END $$;

-- 2.1.2 Crear scheme con valores normalizados
DO $$
DECLARE
    created_count INTEGER;
BEGIN
    WITH inserted AS (
        INSERT INTO ref.category (scheme, code, label, label_en, description, sort_order, metadata)
        VALUES
            -- Alineamiento: Ley 18.834 Estatuto Administrativo
            ('estamento', 'PROFESIONAL', 'Profesional', 'Professional',
             'Funcionarios con título profesional (grados 4-8)', 1,
             '{"tde_class": "Estamento", "legal_basis": "Ley_18834_Art_5"}'::jsonb),
            ('estamento', 'DIRECTIVO', 'Directivo', 'Executive',
             'Cargos de exclusiva confianza y jefaturas superiores (grados 1-4)', 2,
             '{"tde_class": "Estamento", "legal_basis": "Ley_18834_Art_5"}'::jsonb),
            ('estamento', 'ADMINISTRATIVO', 'Administrativo', 'Administrative',
             'Funciones de apoyo administrativo y secretaría (grados 10-17)', 3,
             '{"tde_class": "Estamento", "legal_basis": "Ley_18834_Art_5"}'::jsonb),
            ('estamento', 'TECNICO', 'Técnico', 'Technical',
             'Funciones técnicas de nivel medio (grados 10-17)', 4,
             '{"tde_class": "Estamento", "legal_basis": "Ley_18834_Art_5"}'::jsonb),
            ('estamento', 'AUXILIAR', 'Auxiliar', 'Auxiliary',
             'Funciones de apoyo operativo (grados 18-22)', 5,
             '{"tde_class": "Estamento", "legal_basis": "Ley_18834_Art_5"}'::jsonb),
            ('estamento', 'HONORARIOS', 'Honorarios', 'Fee-based',
             'Contrato a honorarios (no aplica Estatuto Administrativo)', 6,
             '{"tde_class": "Estamento", "legal_basis": "Ley_18834_Art_11"}'::jsonb),
            ('estamento', 'AUTORIDAD', 'Autoridad de Gobierno', 'Government Authority',
             'Autoridades electas o designadas políticamente', 7,
             '{"tde_class": "Estamento", "gnub_class": "AutoridadRegional"}'::jsonb)
        ON CONFLICT (scheme, code) DO NOTHING
        RETURNING id
    )
    SELECT COUNT(*) INTO created_count FROM inserted;

    IF created_count > 0 THEN
        RAISE NOTICE '  [OK] Scheme estamento creado: % códigos', created_count;
    ELSE
        RAISE NOTICE '  [INFO] Scheme estamento: 0 códigos nuevos (ya existían)';
    END IF;
END $$;

-- 2.1.3 Verificar scheme creado
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '  Valores del Scheme estamento:';
    RAISE NOTICE '  ----------------------------------------';
END $$;

SELECT
    '    ' || LPAD(code, 15) AS codigo,
    LPAD(label, 25) AS etiqueta
FROM ref.category
WHERE scheme = 'estamento'
ORDER BY sort_order;

COMMIT;

-- ==============================================================================
-- FASE 2.2: AGREGAR COLUMNA estamento_id EN core.person
-- ==============================================================================
-- Ontología: tde:Estamento → gnub:Person.estamento
-- Constraint: CHECK que valida scheme='estamento'
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('2', 'Agregar Columna estamento_id en core.person');

-- 2.2.1 Agregar columna si no existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'person'
          AND column_name = 'estamento_id'
    ) THEN
        ALTER TABLE core.person
            ADD COLUMN estamento_id UUID REFERENCES ref.category(id);

        COMMENT ON COLUMN core.person.estamento_id IS
            'tde:Estamento - Clasificación funcionaria según Ley 18.834. '
            'Normalized from metadata.estamento on 2026-01-30. '
            'Valid values: PROFESIONAL, DIRECTIVO, ADMINISTRATIVO, TECNICO, AUXILIAR, HONORARIOS, AUTORIDAD.';

        RAISE NOTICE '  [OK] Columna estamento_id agregada a core.person';
    ELSE
        RAISE NOTICE '  [INFO] Columna estamento_id ya existe en core.person';
    END IF;
END $$;

-- 2.2.2 Crear índice parcial
CREATE INDEX IF NOT EXISTS idx_person_estamento
ON core.person(estamento_id)
WHERE estamento_id IS NOT NULL;

DO $$
BEGIN
    RAISE NOTICE '  [OK] Índice idx_person_estamento creado (partial index)';
END $$;

COMMIT;

-- ==============================================================================
-- FASE 2.3: MIGRAR DATOS estamento
-- ==============================================================================
-- Mapeo: metadata->>'estamento' (texto libre) → estamento_id (FK)
-- Normalización de variantes: 'Técnico' → 'TECNICO', 'Autoridad de Gobierno' → 'AUTORIDAD'
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('3', 'Migrar Datos metadata.estamento → estamento_id');

-- 2.3.1 Crear tabla de mapeo explícito
DROP TABLE IF EXISTS temp_estamento_mapping;
CREATE TEMP TABLE temp_estamento_mapping (
    original_value TEXT PRIMARY KEY,
    normalized_code VARCHAR(20) NOT NULL
);

INSERT INTO temp_estamento_mapping (original_value, normalized_code) VALUES
    ('Profesional', 'PROFESIONAL'),
    ('profesional', 'PROFESIONAL'),
    ('PROFESIONAL', 'PROFESIONAL'),
    ('Directivo', 'DIRECTIVO'),
    ('directivo', 'DIRECTIVO'),
    ('DIRECTIVO', 'DIRECTIVO'),
    ('Administrativo', 'ADMINISTRATIVO'),
    ('administrativo', 'ADMINISTRATIVO'),
    ('ADMINISTRATIVO', 'ADMINISTRATIVO'),
    ('Técnico', 'TECNICO'),
    ('Tecnico', 'TECNICO'),
    ('tecnico', 'TECNICO'),
    ('TECNICO', 'TECNICO'),
    ('TÉCNICO', 'TECNICO'),
    ('Auxiliar', 'AUXILIAR'),
    ('auxiliar', 'AUXILIAR'),
    ('AUXILIAR', 'AUXILIAR'),
    ('Honorarios', 'HONORARIOS'),
    ('honorarios', 'HONORARIOS'),
    ('HONORARIOS', 'HONORARIOS'),
    ('Autoridad de Gobierno', 'AUTORIDAD'),
    ('Autoridad', 'AUTORIDAD'),
    ('autoridad', 'AUTORIDAD'),
    ('AUTORIDAD', 'AUTORIDAD');

DO $$
BEGIN
    RAISE NOTICE '  [OK] Tabla de mapeo estamento creada (24 variantes → 7 códigos)';
END $$;

-- 2.3.2 Migrar datos
DO $$
DECLARE
    updated_count INTEGER;
    unmapped_count INTEGER;
BEGIN
    -- Actualizar con mapeo
    WITH updated AS (
        UPDATE core.person p
        SET estamento_id = c.id
        FROM temp_estamento_mapping m
        JOIN ref.category c ON c.scheme = 'estamento' AND c.code = m.normalized_code
        WHERE p.metadata->>'estamento' IS NOT NULL
          AND TRIM(p.metadata->>'estamento') = m.original_value
          AND p.estamento_id IS NULL
        RETURNING p.id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;

    -- Verificar unmapped
    SELECT COUNT(*) INTO unmapped_count
    FROM core.person
    WHERE metadata->>'estamento' IS NOT NULL
      AND estamento_id IS NULL;

    RAISE NOTICE '  [OK] % personas: estamento_id poblado', updated_count;

    IF unmapped_count > 0 THEN
        RAISE WARNING '  [WARN] % personas con estamento no mapeado', unmapped_count;
    END IF;
END $$;

-- 2.3.3 Reportar valores no mapeados (si los hay)
DO $$
DECLARE
    unmapped_values TEXT;
BEGIN
    SELECT STRING_AGG(DISTINCT metadata->>'estamento', ', ')
    INTO unmapped_values
    FROM core.person
    WHERE metadata->>'estamento' IS NOT NULL
      AND estamento_id IS NULL;

    IF unmapped_values IS NOT NULL THEN
        RAISE WARNING '  [WARN] Valores no mapeados: %', unmapped_values;
    ELSE
        RAISE NOTICE '  [OK] Todos los estamentos mapeados correctamente';
    END IF;
END $$;

-- 2.3.4 Reporte de distribución
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '  Distribución por Estamento:';
    RAISE NOTICE '  ----------------------------------------';
END $$;

SELECT
    '    ' || LPAD(c.label, 25) AS estamento,
    LPAD(COUNT(*)::text, 6) AS personas,
    LPAD(ROUND(COUNT(*)::numeric / NULLIF((SELECT COUNT(*) FROM core.person WHERE estamento_id IS NOT NULL), 0) * 100, 1)::text || '%', 8) AS pct
FROM core.person p
JOIN ref.category c ON p.estamento_id = c.id
WHERE c.scheme = 'estamento'
GROUP BY c.label, c.sort_order
ORDER BY c.sort_order;

COMMIT;

-- ==============================================================================
-- FASE 2.4: AGREGAR CHECK CONSTRAINT PARA estamento_id
-- ==============================================================================
-- Garantiza Univocidad Categorial: estamento_id → scheme='estamento' exclusivamente
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('4', 'Agregar CHECK Constraint (Coherencia Categorial)');

-- 2.4.1 Remover constraint si existe
DO $$
BEGIN
    ALTER TABLE core.person
        DROP CONSTRAINT IF EXISTS chk_estamento_scheme;
    RAISE NOTICE '  [INFO] Constraint anterior removido (si existía)';
END $$;

-- 2.4.2 Agregar constraint de validación
DO $$
BEGIN
    ALTER TABLE core.person
        ADD CONSTRAINT chk_estamento_scheme
            CHECK (estamento_id IS NULL OR fn_validate_category_scheme(estamento_id, 'estamento'));

    RAISE NOTICE '  [OK] CHECK constraint chk_estamento_scheme agregado';
    RAISE NOTICE '       Garantiza: estamento_id → scheme=estamento (Univocidad Categorial)';
END $$;

-- 2.4.3 Verificar constraint
DO $$
DECLARE
    constraint_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'core.person'::regclass
          AND conname = 'chk_estamento_scheme'
    ) INTO constraint_exists;

    IF constraint_exists THEN
        RAISE NOTICE '  [OK] Constraint verificado en pg_constraint';
    ELSE
        RAISE EXCEPTION 'Constraint chk_estamento_scheme NO fue creado';
    END IF;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 2.5: AGREGAR technical_referent_id EN core.agreement
-- ==============================================================================
-- Ontología: gnub:TechnicalReferent, tde:ResponsableAsignado
-- Tipo: FK a core.person
-- Migración: Fuzzy matching de nombres
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('5', 'Agregar Columna technical_referent_id en core.agreement');

-- 2.5.1 Agregar columna si no existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'agreement'
          AND column_name = 'technical_referent_id'
    ) THEN
        ALTER TABLE core.agreement
            ADD COLUMN technical_referent_id UUID REFERENCES core.person(id);

        COMMENT ON COLUMN core.agreement.technical_referent_id IS
            'gnub:TechnicalReferent, tde:ResponsableAsignado - Persona responsable del seguimiento técnico del convenio. '
            'Normalized from metadata.referente_tecnico on 2026-01-30.';

        RAISE NOTICE '  [OK] Columna technical_referent_id agregada a core.agreement';
    ELSE
        RAISE NOTICE '  [INFO] Columna technical_referent_id ya existe en core.agreement';
    END IF;
END $$;

-- 2.5.2 Crear índice
CREATE INDEX IF NOT EXISTS idx_agreement_technical_referent
ON core.agreement(technical_referent_id)
WHERE technical_referent_id IS NOT NULL;

DO $$
BEGIN
    RAISE NOTICE '  [OK] Índice idx_agreement_technical_referent creado';
END $$;

COMMIT;

-- ==============================================================================
-- FASE 2.6: CREAR TABLA DE MAPEO PARA referente_tecnico
-- ==============================================================================
-- Problema: metadata->>'referente_tecnico' contiene nombres en formato variable
-- Solución: Tabla de mapeo manual + extensión pg_trgm para fuzzy matching
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('6', 'Crear Tabla de Mapeo para referente_tecnico');

-- 2.6.1 Crear extensión pg_trgm si no existe (para fuzzy matching)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

DO $$
BEGIN
    RAISE NOTICE '  [OK] Extensión pg_trgm habilitada';
END $$;

-- 2.6.2 Crear tabla de mapeo manual
DROP TABLE IF EXISTS temp_referente_mapping;
CREATE TEMP TABLE temp_referente_mapping (
    referente_original TEXT PRIMARY KEY,
    person_id UUID,
    match_type VARCHAR(20), -- EXACT, FUZZY, MANUAL, DIVISION
    confidence NUMERIC(3,2)
);

-- 2.6.3 Poblar con matches exactos por nombre completo
INSERT INTO temp_referente_mapping (referente_original, person_id, match_type, confidence)
SELECT DISTINCT
    a.metadata->>'referente_tecnico' AS referente_original,
    p.id AS person_id,
    'EXACT' AS match_type,
    1.00 AS confidence
FROM core.agreement a
JOIN core.person p ON
    UPPER(TRIM(a.metadata->>'referente_tecnico')) =
    UPPER(TRIM(p.names || ' ' || p.paternal_surname || COALESCE(' ' || p.maternal_surname, '')))
WHERE a.metadata->>'referente_tecnico' IS NOT NULL
  AND a.metadata->>'referente_tecnico' NOT IN ('DIT', 'DIPLADE', 'DIDESOH', 'INVERSIONES')
ON CONFLICT (referente_original) DO NOTHING;

DO $$
DECLARE
    exact_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO exact_count FROM temp_referente_mapping WHERE match_type = 'EXACT';
    RAISE NOTICE '  [OK] Matches exactos encontrados: %', exact_count;
END $$;

-- 2.6.4 Agregar matches por apellido paterno + nombre
INSERT INTO temp_referente_mapping (referente_original, person_id, match_type, confidence)
SELECT DISTINCT ON (a.metadata->>'referente_tecnico')
    a.metadata->>'referente_tecnico' AS referente_original,
    p.id AS person_id,
    'FUZZY' AS match_type,
    SIMILARITY(
        UPPER(a.metadata->>'referente_tecnico'),
        UPPER(p.names || ' ' || p.paternal_surname)
    ) AS confidence
FROM core.agreement a
JOIN core.person p ON
    UPPER(a.metadata->>'referente_tecnico') LIKE '%' || UPPER(p.paternal_surname) || '%'
    AND UPPER(a.metadata->>'referente_tecnico') LIKE '%' || UPPER(SPLIT_PART(p.names, ' ', 1)) || '%'
WHERE a.metadata->>'referente_tecnico' IS NOT NULL
  AND a.metadata->>'referente_tecnico' NOT IN ('DIT', 'DIPLADE', 'DIDESOH', 'INVERSIONES')
  AND NOT EXISTS (SELECT 1 FROM temp_referente_mapping m WHERE m.referente_original = a.metadata->>'referente_tecnico')
ORDER BY a.metadata->>'referente_tecnico',
         SIMILARITY(UPPER(a.metadata->>'referente_tecnico'), UPPER(p.names || ' ' || p.paternal_surname)) DESC
ON CONFLICT (referente_original) DO NOTHING;

DO $$
DECLARE
    fuzzy_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO fuzzy_count FROM temp_referente_mapping WHERE match_type = 'FUZZY';
    RAISE NOTICE '  [OK] Matches fuzzy encontrados: %', fuzzy_count;
END $$;

-- 2.6.5 Marcar divisiones (no son personas)
INSERT INTO temp_referente_mapping (referente_original, person_id, match_type, confidence)
VALUES
    ('DIT', NULL, 'DIVISION', 0.00),
    ('DIPLADE', NULL, 'DIVISION', 0.00),
    ('DIDESOH', NULL, 'DIVISION', 0.00),
    ('INVERSIONES', NULL, 'DIVISION', 0.00),
    ('DIDESOH/GONZALO SANDOVAL', NULL, 'DIVISION', 0.00)
ON CONFLICT (referente_original) DO NOTHING;

DO $$
BEGIN
    RAISE NOTICE '  [INFO] 5 valores marcados como DIVISION (no son personas)';
END $$;

-- 2.6.6 Reporte de mapeo
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '  Resumen de Mapeo referente_tecnico:';
    RAISE NOTICE '  ----------------------------------------';
END $$;

SELECT
    '    ' || LPAD(match_type, 10) AS tipo,
    LPAD(COUNT(*)::text, 6) AS valores,
    LPAD(ROUND(AVG(confidence), 2)::text, 8) AS confianza_avg
FROM temp_referente_mapping
GROUP BY match_type
ORDER BY match_type;

-- 2.6.7 Mostrar valores sin mapear
DO $$
DECLARE
    unmapped_values TEXT;
    unmapped_count INTEGER;
BEGIN
    SELECT COUNT(DISTINCT metadata->>'referente_tecnico'),
           STRING_AGG(DISTINCT metadata->>'referente_tecnico', ', ' ORDER BY metadata->>'referente_tecnico')
    INTO unmapped_count, unmapped_values
    FROM core.agreement a
    WHERE a.metadata->>'referente_tecnico' IS NOT NULL
      AND NOT EXISTS (
          SELECT 1 FROM temp_referente_mapping m
          WHERE m.referente_original = a.metadata->>'referente_tecnico'
      );

    IF unmapped_count > 0 THEN
        RAISE WARNING '  [WARN] % valores sin mapear:', unmapped_count;
        RAISE WARNING '         %', LEFT(unmapped_values, 200);
    ELSE
        RAISE NOTICE '  [OK] Todos los valores de referente_tecnico mapeados';
    END IF;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 2.7: MIGRAR technical_referent_id
-- ==============================================================================
-- Usar tabla de mapeo para poblar technical_referent_id
-- Solo migrar matches con confidence >= 0.70
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('7', 'Migrar Datos referente_tecnico → technical_referent_id');

-- 2.7.1 Actualizar agreements con mapeo de alta confianza
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE core.agreement a
        SET technical_referent_id = m.person_id,
            metadata = a.metadata || jsonb_build_object(
                'referente_tecnico_migrated', true,
                'referente_match_type', m.match_type,
                'referente_confidence', m.confidence,
                'normalized_at', now()::text,
                'normalized_version', 'v3.0'
            )
        FROM temp_referente_mapping m
        WHERE a.metadata->>'referente_tecnico' = m.referente_original
          AND m.person_id IS NOT NULL
          AND m.confidence >= 0.70
          AND a.technical_referent_id IS NULL
        RETURNING a.id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;

    RAISE NOTICE '  [OK] % agreements: technical_referent_id poblado (confianza >= 0.70)', updated_count;
END $$;

-- 2.7.2 Marcar divisions como no-migrables
DO $$
DECLARE
    marked_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE core.agreement a
        SET metadata = a.metadata || jsonb_build_object(
                'referente_tecnico_is_division', true,
                'referente_requires_manual_review', true,
                'normalized_at', now()::text
            )
        FROM temp_referente_mapping m
        WHERE a.metadata->>'referente_tecnico' = m.referente_original
          AND m.match_type = 'DIVISION'
          AND NOT (a.metadata ? 'referente_tecnico_is_division')
        RETURNING a.id
    )
    SELECT COUNT(*) INTO marked_count FROM updated;

    RAISE NOTICE '  [INFO] % agreements marcados como referente=DIVISION (requieren revisión)', marked_count;
END $$;

-- 2.7.3 Reporte de migración
DO $$
DECLARE
    total_with_referente INTEGER;
    migrated INTEGER;
    pending INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_with_referente
    FROM core.agreement WHERE metadata->>'referente_tecnico' IS NOT NULL;

    SELECT COUNT(*) INTO migrated
    FROM core.agreement WHERE technical_referent_id IS NOT NULL;

    pending := total_with_referente - migrated;

    RAISE NOTICE '';
    RAISE NOTICE '  Resultado Migración technical_referent_id:';
    RAISE NOTICE '  ----------------------------------------';
    RAISE NOTICE '    Total con referente_tecnico:  %', total_with_referente;
    RAISE NOTICE '    Migrados (FK poblado):        %', migrated;
    RAISE NOTICE '    Pendientes (revisar manual):  %', pending;
    RAISE NOTICE '    Tasa de migración:            %', ROUND(migrated::numeric / NULLIF(total_with_referente, 0) * 100, 1) || '%';
END $$;

COMMIT;

-- ==============================================================================
-- FASE 2.8: MARCAR METADATA COMO PROCESADO
-- ==============================================================================
-- Agregar flag de migración sin eliminar campos originales (audit trail)
-- ==============================================================================

BEGIN;

SELECT report_phase_v3('8', 'Marcar Metadata como Procesado (Audit Trail)');

-- 2.8.1 Marcar estamento como procesado
DO $$
DECLARE
    marked_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE core.person
        SET metadata = metadata || jsonb_build_object(
                'estamento_migrated', true,
                'estamento_migration_date', now()::text,
                'normalized_version', 'v3.0'
            )
        WHERE metadata->>'estamento' IS NOT NULL
          AND estamento_id IS NOT NULL
          AND NOT (metadata ? 'estamento_migrated')
        RETURNING id
    )
    SELECT COUNT(*) INTO marked_count FROM updated;

    RAISE NOTICE '  [OK] % persons: metadata.estamento marcado como migrado', marked_count;
    RAISE NOTICE '       Campo original MANTENIDO como audit trail';
END $$;

COMMIT;

-- ==============================================================================
-- POST-EJECUCIÓN: VERIFICACIONES FINALES
-- ==============================================================================

SELECT report_phase_v3('9', 'Verificaciones Finales');

-- Verificación 1: Coherencia categorial estamento_id
DO $$
DECLARE
    incoherent INTEGER;
BEGIN
    SELECT COUNT(*) INTO incoherent
    FROM core.person p
    JOIN ref.category c ON p.estamento_id = c.id
    WHERE c.scheme != 'estamento';

    IF incoherent = 0 THEN
        RAISE NOTICE '  [PASS] Coherencia categorial estamento_id: 100%% (0 violaciones)';
    ELSE
        RAISE WARNING '  [FAIL] % personas con estamento_id apuntando a scheme incorrecto', incoherent;
    END IF;
END $$;

-- Verificación 2: Completitud migración estamento
DO $$
DECLARE
    original_count INTEGER;
    migrated_count INTEGER;
    pct NUMERIC;
BEGIN
    SELECT COUNT(*) INTO original_count FROM temp_person_estamento_backup;
    SELECT COUNT(*) INTO migrated_count FROM core.person WHERE estamento_id IS NOT NULL;
    pct := ROUND(migrated_count::numeric / NULLIF(original_count, 0) * 100, 1);

    IF pct >= 95 THEN
        RAISE NOTICE '  [PASS] Migración estamento: %/%% (%/%)', pct, original_count, migrated_count;
    ELSE
        RAISE WARNING '  [WARN] Migración estamento incompleta: %/%% (%/%)', pct, original_count, migrated_count;
    END IF;
END $$;

-- Verificación 3: technical_referent_id referencia válida
DO $$
DECLARE
    invalid_refs INTEGER;
BEGIN
    SELECT COUNT(*) INTO invalid_refs
    FROM core.agreement a
    WHERE a.technical_referent_id IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM core.person p WHERE p.id = a.technical_referent_id);

    IF invalid_refs = 0 THEN
        RAISE NOTICE '  [PASS] Integridad referencial technical_referent_id: 100%% válido';
    ELSE
        RAISE EXCEPTION '  [FAIL] % agreements con technical_referent_id inválido', invalid_refs;
    END IF;
END $$;

-- Verificación 4: Resumen final
DO $$
DECLARE
    total_persons INTEGER;
    persons_with_estamento INTEGER;
    total_agreements INTEGER;
    agreements_with_referent INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_persons FROM core.person WHERE deleted_at IS NULL;
    SELECT COUNT(*) INTO persons_with_estamento FROM core.person WHERE estamento_id IS NOT NULL;
    SELECT COUNT(*) INTO total_agreements FROM core.agreement WHERE deleted_at IS NULL;
    SELECT COUNT(*) INTO agreements_with_referent FROM core.agreement WHERE technical_referent_id IS NOT NULL;

    RAISE NOTICE '';
    RAISE NOTICE '  Resumen Fase 2 - Personas:';
    RAISE NOTICE '  ========================================';
    RAISE NOTICE '  core.person:';
    RAISE NOTICE '    Total:                 %', total_persons;
    RAISE NOTICE '    Con estamento_id:      %', persons_with_estamento;
    RAISE NOTICE '';
    RAISE NOTICE '  core.agreement:';
    RAISE NOTICE '    Total:                 %', total_agreements;
    RAISE NOTICE '    Con technical_referent: %', agreements_with_referent;
    RAISE NOTICE '  ========================================';
END $$;

-- ==============================================================================
-- REPORTE FINAL
-- ==============================================================================

DO $$ BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '  FASE 2 COMPLETADA EXITOSAMENTE';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Normalizaciones completadas:';
    RAISE NOTICE '  1. Scheme estamento creado (7 valores tde:Estamento)';
    RAISE NOTICE '  2. Columna estamento_id agregada a core.person';
    RAISE NOTICE '  3. CHECK constraint chk_estamento_scheme activo';
    RAISE NOTICE '  4. Columna technical_referent_id agregada a core.agreement';
    RAISE NOTICE '';
    RAISE NOTICE 'Acciones pendientes (revisión manual):';
    RAISE NOTICE '  - Revisar agreements donde referente_tecnico es DIVISION';
    RAISE NOTICE '  - Verificar matches fuzzy con confianza < 0.70';
    RAISE NOTICE '';
    RAISE NOTICE 'Backups disponibles:';
    RAISE NOTICE '  - SELECT * FROM temp_person_estamento_backup;';
    RAISE NOTICE '  - SELECT * FROM temp_agreement_referente_backup;';
    RAISE NOTICE '  - SELECT * FROM temp_referente_mapping WHERE confidence < 1.0;';
    RAISE NOTICE '';
    RAISE NOTICE 'Versión: v3.0';
    RAISE NOTICE 'Arquitecto: ARQUITECTO-GORE v0.1.0';
    RAISE NOTICE '';
END $$;

-- Limpiar función helper
DROP FUNCTION IF EXISTS report_phase_v3(TEXT, TEXT);

-- ==============================================================================
-- QUERIES DE AUDITORÍA POST-EJECUCIÓN
-- ==============================================================================
-- Ejecutar después de migración para verificar integridad:
--
-- 1. Verificar distribución estamento:
--    SELECT c.code, c.label, COUNT(p.id)
--    FROM core.person p
--    JOIN ref.category c ON p.estamento_id = c.id
--    GROUP BY c.code, c.label ORDER BY COUNT(p.id) DESC;
--
-- 2. Verificar matches fuzzy pendientes:
--    SELECT referente_original, match_type, confidence
--    FROM temp_referente_mapping
--    WHERE confidence < 0.70 AND person_id IS NOT NULL;
--
-- 3. Verificar agreements sin referente migrado:
--    SELECT agreement_number, metadata->>'referente_tecnico'
--    FROM core.agreement
--    WHERE metadata->>'referente_tecnico' IS NOT NULL
--      AND technical_referent_id IS NULL;
--
-- ==============================================================================
-- FIN FASE 2
-- ==============================================================================
