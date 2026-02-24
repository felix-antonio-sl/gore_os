-- ============================================================================
-- NORMALIZACION JSONB V3 - FASE MEDIA (CAMPOS 1-3)
-- ============================================================================
-- Script de normalización para prioridad MEDIA identificadas en auditoría v3.0
--
-- NORMALIZACIONES INCLUIDAS:
-- 1. core.person.cargo_ultimo → core.position (tabla nueva)
-- 2. core.person.calificacion → ref.category scheme='professional_qualification'
-- 3. core.agreement.estado_cgr_norm → ref.category scheme='cgr_outcome'
--
-- REFERENCIA: docs/AUDITORIA_CATEGORIAL_v3.0.md
-- ONTOLOGIA: tde:Cargo, tde:CalificacionProfesional, tde:EstadoCGR, gnub:ResolutionOutcome
-- FECHA: 2026-01-30
-- ============================================================================

-- Configuración de sesión
SET client_min_messages = NOTICE;
SET search_path TO core, ref, meta, public;

\echo ''
\echo '============================================================================'
\echo 'INICIO: NORMALIZACION JSONB V3 - FASE MEDIA (CAMPOS 1-3)'
\echo '============================================================================'
\echo ''

-- ============================================================================
-- VERIFICACIONES PRE-MIGRACION
-- ============================================================================

DO $$
DECLARE
    v_person_count INTEGER;
    v_cargo_count INTEGER;
    v_calificacion_count INTEGER;
    v_agreement_count INTEGER;
    v_cgr_count INTEGER;
BEGIN
    -- Contar registros a migrar
    SELECT COUNT(*) INTO v_person_count FROM core.person WHERE metadata IS NOT NULL;
    SELECT COUNT(DISTINCT metadata->>'cargo_ultimo') INTO v_cargo_count
        FROM core.person WHERE metadata->>'cargo_ultimo' IS NOT NULL;
    SELECT COUNT(DISTINCT metadata->>'calificacion') INTO v_calificacion_count
        FROM core.person WHERE metadata->>'calificacion' IS NOT NULL;
    SELECT COUNT(*) INTO v_agreement_count
        FROM core.agreement WHERE metadata->>'estado_cgr_norm' IS NOT NULL;
    SELECT COUNT(DISTINCT metadata->>'estado_cgr_norm') INTO v_cgr_count
        FROM core.agreement WHERE metadata->>'estado_cgr_norm' IS NOT NULL;

    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'PRE-VERIFICACION: ESTADO ACTUAL';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'Personas con metadata: %', v_person_count;
    RAISE NOTICE 'Cargos únicos (cargo_ultimo): %', v_cargo_count;
    RAISE NOTICE 'Calificaciones únicas (calificacion): %', v_calificacion_count;
    RAISE NOTICE 'Agreements con estado_cgr_norm: %', v_agreement_count;
    RAISE NOTICE 'Estados CGR únicos: %', v_cgr_count;
    RAISE NOTICE '====================================================================';
END $$;

\echo ''
\echo '======================================================================'
\echo 'FASE 1: NORMALIZACION core.person.cargo_ultimo → core.position'
\echo '======================================================================'
\echo ''

-- ============================================================================
-- FASE 1: NORMALIZACION cargo_ultimo → core.position
-- ============================================================================

BEGIN;

-- Crear tabla temporal de backup
CREATE TEMP TABLE backup_person_fase1 AS
SELECT id, metadata FROM core.person WHERE metadata IS NOT NULL;

RAISE NOTICE 'Backup creado: % registros', (SELECT COUNT(*) FROM backup_person_fase1);

-- Verificar si tabla position ya existe
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'core' AND table_name = 'position') THEN
        RAISE EXCEPTION 'La tabla core.position ya existe. Abortar migración.';
    END IF;
END $$;

-- Crear tabla core.position
CREATE TABLE core.position (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    organization_id UUID REFERENCES core.organization(id),
    level SMALLINT,  -- Nivel jerárquico (1=más alto)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core."user"(id),
    updated_by_id UUID REFERENCES core."user"(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core."user"(id),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Índices para position
CREATE INDEX idx_position_org ON core.position(organization_id)
    WHERE organization_id IS NOT NULL;
CREATE INDEX idx_position_active ON core.position(id)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_position_code ON core.position(code);
CREATE INDEX idx_position_metadata ON core.position USING gin(metadata jsonb_path_ops);

-- Comentarios
COMMENT ON TABLE core.position IS 'Cargos y posiciones laborales (tde:Cargo)';
COMMENT ON COLUMN core.position.code IS 'Código único del cargo (normalizado)';
COMMENT ON COLUMN core.position.name IS 'Nombre completo del cargo';
COMMENT ON COLUMN core.position.organization_id IS 'Organización a la que pertenece el cargo';
COMMENT ON COLUMN core.position.level IS 'Nivel jerárquico (1=más alto, e.g., Director)';

-- Trigger para updated_at
CREATE TRIGGER trg_position_updated_at
    BEFORE UPDATE ON core.position
    FOR EACH ROW
    EXECUTE FUNCTION fn_update_timestamp();

RAISE NOTICE 'Tabla core.position creada exitosamente';

-- Insertar cargos únicos desde person.metadata->>'cargo_ultimo'
INSERT INTO core.position (code, name, metadata)
SELECT
    DISTINCT
    UPPER(REGEXP_REPLACE(metadata->>'cargo_ultimo', '[^a-zA-Z0-9_]', '_', 'g')) as code,
    metadata->>'cargo_ultimo' as name,
    jsonb_build_object(
        'source', 'MIGRATION_MEDIA_V3',
        'migration_date', now()::text,
        'original_field', 'person.metadata.cargo_ultimo'
    ) as metadata
FROM core.person
WHERE metadata->>'cargo_ultimo' IS NOT NULL
ON CONFLICT (code) DO NOTHING;

RAISE NOTICE 'Cargos insertados: %', (SELECT COUNT(*) FROM core.position);

-- Agregar columna position_id en person
ALTER TABLE core.person ADD COLUMN position_id UUID REFERENCES core.position(id);

-- Crear índice
CREATE INDEX idx_person_position ON core.person(position_id)
    WHERE position_id IS NOT NULL;

COMMENT ON COLUMN core.person.position_id IS 'Cargo/Posición laboral actual (FK → core.position)';

-- Migrar datos: Relacionar person con position
UPDATE core.person p
SET position_id = (
    SELECT pos.id
    FROM core.position pos
    WHERE pos.name = p.metadata->>'cargo_ultimo'
)
WHERE p.metadata->>'cargo_ultimo' IS NOT NULL;

-- Verificaciones post-migración Fase 1
DO $$
DECLARE
    v_total_cargos INTEGER;
    v_migrated INTEGER;
    v_pct NUMERIC;
BEGIN
    SELECT COUNT(*) INTO v_total_cargos
        FROM core.person WHERE metadata->>'cargo_ultimo' IS NOT NULL;
    SELECT COUNT(*) INTO v_migrated
        FROM core.person WHERE position_id IS NOT NULL;

    v_pct := CASE WHEN v_total_cargos > 0
                  THEN ROUND((v_migrated::NUMERIC / v_total_cargos * 100), 2)
                  ELSE 0 END;

    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'VERIFICACION FASE 1: cargo_ultimo → position';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'Total personas con cargo_ultimo: %', v_total_cargos;
    RAISE NOTICE 'Personas con position_id asignado: %', v_migrated;
    RAISE NOTICE 'Tasa de éxito: % %%', v_pct;
    RAISE NOTICE 'Total positions creados: %', (SELECT COUNT(*) FROM core.position);
    RAISE NOTICE '====================================================================';

    IF v_pct < 100 THEN
        RAISE WARNING 'Migración parcial: solo % %% de cargos fueron migrados', v_pct;
    END IF;
END $$;

COMMIT;

\echo ''
\echo '======================================================================'
\echo 'FASE 2: NORMALIZACION core.person.calificacion → ref.category'
\echo '======================================================================'
\echo ''

-- ============================================================================
-- FASE 2: NORMALIZACION calificacion → ref.category scheme='professional_qualification'
-- ============================================================================

BEGIN;

-- Crear tabla temporal de backup
CREATE TEMP TABLE backup_person_fase2 AS
SELECT id, metadata FROM core.person WHERE metadata->>'calificacion' IS NOT NULL;

RAISE NOTICE 'Backup Fase 2 creado: % registros', (SELECT COUNT(*) FROM backup_person_fase2);

-- Verificar que el scheme no exista ya
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM ref.category WHERE scheme = 'professional_qualification') THEN
        RAISE EXCEPTION 'El scheme professional_qualification ya existe. Abortar migración.';
    END IF;
END $$;

-- Crear scheme professional_qualification
-- Categorías normalizadas basadas en análisis de datos reales
INSERT INTO ref.category (scheme, code, label, metadata) VALUES
('professional_qualification', 'INGENIERO_COMERCIAL', 'Ingeniero Comercial',
    '{"ontology": "tde:CalificacionProfesional", "area": "ADMINISTRACION"}'),
('professional_qualification', 'INGENIERO_CIVIL', 'Ingeniero Civil',
    '{"ontology": "tde:CalificacionProfesional", "area": "INGENIERIA"}'),
('professional_qualification', 'INGENIERO_INDUSTRIAL', 'Ingeniero Industrial',
    '{"ontology": "tde:CalificacionProfesional", "area": "INGENIERIA"}'),
('professional_qualification', 'INGENIERO_CONSTRUCTOR', 'Ingeniero Constructor/Constructor Civil',
    '{"ontology": "tde:CalificacionProfesional", "area": "CONSTRUCCION"}'),
('professional_qualification', 'INGENIERO_OTROS', 'Ingeniero (Otras especialidades)',
    '{"ontology": "tde:CalificacionProfesional", "area": "INGENIERIA"}'),
('professional_qualification', 'ARQUITECTO', 'Arquitecto',
    '{"ontology": "tde:CalificacionProfesional", "area": "ARQUITECTURA"}'),
('professional_qualification', 'ABOGADO', 'Abogado',
    '{"ontology": "tde:CalificacionProfesional", "area": "JURIDICO"}'),
('professional_qualification', 'CONTADOR', 'Contador/Contador Auditor',
    '{"ontology": "tde:CalificacionProfesional", "area": "CONTABILIDAD"}'),
('professional_qualification', 'ADMINISTRADOR_PUBLICO', 'Administrador Público',
    '{"ontology": "tde:CalificacionProfesional", "area": "ADMINISTRACION"}'),
('professional_qualification', 'TRABAJADOR_SOCIAL', 'Trabajador Social/Asistente Social',
    '{"ontology": "tde:CalificacionProfesional", "area": "SOCIAL"}'),
('professional_qualification', 'PERIODISTA', 'Periodista/Comunicador',
    '{"ontology": "tde:CalificacionProfesional", "area": "COMUNICACIONES"}'),
('professional_qualification', 'PROFESIONAL_SALUD', 'Profesional de Salud',
    '{"ontology": "tde:CalificacionProfesional", "area": "SALUD"}'),
('professional_qualification', 'PROFESIONAL_EDUCACION', 'Profesional de Educación',
    '{"ontology": "tde:CalificacionProfesional", "area": "EDUCACION"}'),
('professional_qualification', 'TECNICO', 'Técnico de Nivel Superior',
    '{"ontology": "tde:CalificacionProfesional", "area": "TECNICO"}'),
('professional_qualification', 'LICENCIA_MEDIA', 'Licencia Enseñanza Media',
    '{"ontology": "tde:CalificacionProfesional", "area": "BASICO"}'),
('professional_qualification', 'SECRETARIA', 'Secretaria Ejecutiva/Administrativa',
    '{"ontology": "tde:CalificacionProfesional", "area": "ADMINISTRATIVO"}'),
('professional_qualification', 'OTROS', 'Otro',
    '{"ontology": "tde:CalificacionProfesional", "area": "OTROS"}');

RAISE NOTICE 'Scheme professional_qualification creado: % categorías',
    (SELECT COUNT(*) FROM ref.category WHERE scheme = 'professional_qualification');

-- Agregar columna qualification_id en person
ALTER TABLE core.person ADD COLUMN qualification_id UUID REFERENCES ref.category(id);

-- Agregar CHECK constraint
ALTER TABLE core.person ADD CONSTRAINT chk_qualification_scheme
    CHECK (qualification_id IS NULL OR
           fn_validate_category_scheme(qualification_id, 'professional_qualification'));

-- Crear índice
CREATE INDEX idx_person_qualification ON core.person(qualification_id)
    WHERE qualification_id IS NOT NULL;

COMMENT ON COLUMN core.person.qualification_id IS 'Calificación profesional (FK → ref.category scheme=professional_qualification)';

-- Crear tabla temporal de mapeo calificacion → categoría
CREATE TEMP TABLE qualification_mapping AS
SELECT
    metadata->>'calificacion' as original,
    CASE
        -- Ingenieros Comerciales
        WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIER%COMERCIAL%' THEN 'INGENIERO_COMERCIAL'
        WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIER%COMERICIAL%' THEN 'INGENIERO_COMERCIAL'

        -- Ingenieros Civiles
        WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIERO CIVIL%'
             AND NOT UPPER(metadata->>'calificacion') LIKE '%INDUSTRIAL%' THEN 'INGENIERO_CIVIL'
        WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIERO CIVÍL%'
             AND NOT UPPER(metadata->>'calificacion') LIKE '%INDUSTRIAL%' THEN 'INGENIERO_CIVIL'

        -- Ingenieros Industriales
        WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIERO%INDUSTRIAL%' THEN 'INGENIERO_INDUSTRIAL'
        WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIERO%INDUTRIAL%' THEN 'INGENIERO_INDUSTRIAL'
        WHEN UPPER(metadata->>'calificacion') LIKE '%CIVIL%INDUSTRIAL%' THEN 'INGENIERO_INDUSTRIAL'

        -- Constructores/Ingenieros Constructores
        WHEN UPPER(metadata->>'calificacion') LIKE '%CONSTRUCTOR%' THEN 'INGENIERO_CONSTRUCTOR'
        WHEN UPPER(metadata->>'calificacion') LIKE '%CONSTRUCCION%' THEN 'INGENIERO_CONSTRUCTOR'

        -- Otros Ingenieros
        WHEN UPPER(metadata->>'calificacion') LIKE '%INGENIERO%'
             OR UPPER(metadata->>'calificacion') LIKE '%INGENIERA%' THEN 'INGENIERO_OTROS'

        -- Arquitectos
        WHEN UPPER(metadata->>'calificacion') LIKE '%ARQUITECTO%'
             OR UPPER(metadata->>'calificacion') LIKE '%ARQUITECTA%'
             OR UPPER(metadata->>'calificacion') LIKE '%AQUITECTO%' THEN 'ARQUITECTO'

        -- Abogados
        WHEN UPPER(metadata->>'calificacion') LIKE '%ABOGAD%' THEN 'ABOGADO'

        -- Contadores
        WHEN UPPER(metadata->>'calificacion') LIKE '%CONTADOR%' THEN 'CONTADOR'

        -- Administradores Públicos
        WHEN UPPER(metadata->>'calificacion') LIKE '%ADMINISTRA%PUBLIC%'
             OR UPPER(metadata->>'calificacion') LIKE '%ADMINISTRA%MUNICIPAL%' THEN 'ADMINISTRADOR_PUBLICO'

        -- Trabajadores Sociales
        WHEN UPPER(metadata->>'calificacion') LIKE '%TRABAJADOR%SOCIAL%'
             OR UPPER(metadata->>'calificacion') LIKE '%TRABAJADORA%SOCIAL%'
             OR UPPER(metadata->>'calificacion') LIKE '%ASISTENTE%SOCIAL%' THEN 'TRABAJADOR_SOCIAL'

        -- Periodistas
        WHEN UPPER(metadata->>'calificacion') LIKE '%PERIODISTA%'
             OR UPPER(metadata->>'calificacion') LIKE '%PUBLICISTA%'
             OR UPPER(metadata->>'calificacion') LIKE '%COMUNICACION%'
             OR UPPER(metadata->>'calificacion') LIKE '%AUDIOVISUAL%'
             OR UPPER(metadata->>'calificacion') LIKE '%DISEÑADOR%GRAFICO%' THEN 'PERIODISTA'

        -- Profesionales de Salud
        WHEN UPPER(metadata->>'calificacion') LIKE '%MEDICO%'
             OR UPPER(metadata->>'calificacion') LIKE '%VETERINARIO%'
             OR UPPER(metadata->>'calificacion') LIKE '%FONOAUDIOLOG%'
             OR UPPER(metadata->>'calificacion') LIKE '%PSICOLOGO%' THEN 'PROFESIONAL_SALUD'

        -- Técnicos
        WHEN UPPER(metadata->>'calificacion') LIKE '%TECNICO%'
             OR UPPER(metadata->>'calificacion') LIKE '%TÉCNICO%' THEN 'TECNICO'

        -- Licencia Media
        WHEN UPPER(metadata->>'calificacion') LIKE '%LICENCIA%MEDIA%'
             OR UPPER(metadata->>'calificacion') LIKE '%ENSEÑANZA%MEDIA%' THEN 'LICENCIA_MEDIA'

        -- Secretarias
        WHEN UPPER(metadata->>'calificacion') LIKE '%SECRETARIA%' THEN 'SECRETARIA'

        -- Geógrafo, Sociólogo, Biólogo, etc.
        WHEN UPPER(metadata->>'calificacion') LIKE '%GEOGRAFO%'
             OR UPPER(metadata->>'calificacion') LIKE '%SOCIOLOGO%'
             OR UPPER(metadata->>'calificacion') LIKE '%BIOLOGO%' THEN 'OTROS'

        -- Default
        ELSE 'OTROS'
    END as normalized_code
FROM core.person
WHERE metadata->>'calificacion' IS NOT NULL
GROUP BY metadata->>'calificacion';

RAISE NOTICE 'Tabla de mapeo creada: % calificaciones únicas',
    (SELECT COUNT(*) FROM qualification_mapping);

-- Mostrar distribución del mapeo
DO $$
DECLARE
    rec RECORD;
BEGIN
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'DISTRIBUCION DE MAPEO: calificacion → professional_qualification';
    RAISE NOTICE '====================================================================';
    FOR rec IN
        SELECT normalized_code, COUNT(*) as total
        FROM qualification_mapping
        GROUP BY normalized_code
        ORDER BY total DESC
    LOOP
        RAISE NOTICE 'Código: % → % calificaciones originales', rec.normalized_code, rec.total;
    END LOOP;
    RAISE NOTICE '====================================================================';
END $$;

-- Migrar datos usando el mapeo
UPDATE core.person p
SET qualification_id = (
    SELECT c.id
    FROM ref.category c
    JOIN qualification_mapping qm ON c.code = qm.normalized_code
    WHERE qm.original = p.metadata->>'calificacion'
    AND c.scheme = 'professional_qualification'
)
WHERE p.metadata->>'calificacion' IS NOT NULL;

-- Verificaciones post-migración Fase 2
DO $$
DECLARE
    v_total_calificaciones INTEGER;
    v_migrated INTEGER;
    v_pct NUMERIC;
BEGIN
    SELECT COUNT(*) INTO v_total_calificaciones
        FROM core.person WHERE metadata->>'calificacion' IS NOT NULL;
    SELECT COUNT(*) INTO v_migrated
        FROM core.person WHERE qualification_id IS NOT NULL;

    v_pct := CASE WHEN v_total_calificaciones > 0
                  THEN ROUND((v_migrated::NUMERIC / v_total_calificaciones * 100), 2)
                  ELSE 0 END;

    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'VERIFICACION FASE 2: calificacion → qualification_id';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'Total personas con calificacion: %', v_total_calificaciones;
    RAISE NOTICE 'Personas con qualification_id asignado: %', v_migrated;
    RAISE NOTICE 'Tasa de éxito: % %%', v_pct;

    -- Distribución por categoría
    RAISE NOTICE '';
    RAISE NOTICE 'DISTRIBUCION POR CATEGORIA:';
    FOR rec IN
        SELECT c.code, c.label, COUNT(p.id) as total
        FROM ref.category c
        LEFT JOIN core.person p ON p.qualification_id = c.id
        WHERE c.scheme = 'professional_qualification'
        GROUP BY c.id, c.code, c.label
        ORDER BY total DESC
    LOOP
        RAISE NOTICE '  % (%): % personas', rec.label, rec.code, rec.total;
    END LOOP;
    RAISE NOTICE '====================================================================';

    IF v_pct < 100 THEN
        RAISE WARNING 'Migración parcial: solo % %% de calificaciones fueron migradas', v_pct;
    END IF;
END $$;

COMMIT;

\echo ''
\echo '======================================================================'
\echo 'FASE 3: NORMALIZACION core.agreement.estado_cgr_norm → ref.category'
\echo '======================================================================'
\echo ''

-- ============================================================================
-- FASE 3: NORMALIZACION estado_cgr_norm → ref.category scheme='cgr_outcome'
-- ============================================================================

BEGIN;

-- Crear tabla temporal de backup
CREATE TEMP TABLE backup_agreement_fase3 AS
SELECT id, metadata FROM core.agreement WHERE metadata->>'estado_cgr_norm' IS NOT NULL;

RAISE NOTICE 'Backup Fase 3 creado: % registros', (SELECT COUNT(*) FROM backup_agreement_fase3);

-- Verificar scheme cgr_outcome y agregar categorías faltantes
DO $$
DECLARE
    v_scheme_exists BOOLEAN;
    v_missing_codes TEXT[];
BEGIN
    -- Verificar si scheme existe
    SELECT EXISTS (SELECT 1 FROM ref.category WHERE scheme = 'cgr_outcome')
    INTO v_scheme_exists;

    IF v_scheme_exists THEN
        RAISE NOTICE 'Scheme cgr_outcome ya existe. Verificando categorías requeridas...';

        -- Insertar categorías faltantes (solo si no existen)
        INSERT INTO ref.category (scheme, code, label, metadata)
        SELECT * FROM (VALUES
            ('cgr_outcome', 'TOMADO_DE_RAZON', 'Tomado de Razón',
                '{"description": "Aprobado sin observaciones por CGR", "ontology": "tde:EstadoCGR", "severity": "APROBADO"}'::jsonb),
            ('cgr_outcome', 'TR_CON_ALCANCES', 'Tomado de Razón con Alcances',
                '{"description": "Aprobado con observaciones por CGR", "ontology": "tde:EstadoCGR", "severity": "APROBADO_CON_OBSERVACIONES"}'::jsonb),
            ('cgr_outcome', 'REPRESENTADO', 'Representado',
                '{"description": "Rechazado por CGR (representación)", "ontology": "tde:EstadoCGR", "severity": "RECHAZADO"}'::jsonb),
            ('cgr_outcome', 'EN_CGR', 'En CGR',
                '{"description": "En proceso de revisión en CGR", "ontology": "tde:EstadoCGR", "severity": "EN_PROCESO"}'::jsonb)
        ) AS t(scheme, code, label, metadata)
        WHERE NOT EXISTS (
            SELECT 1 FROM ref.category WHERE scheme = 'cgr_outcome' AND code = t.code
        )
        ON CONFLICT (scheme, code) DO NOTHING;

        RAISE NOTICE 'Categorías agregadas/verificadas en scheme cgr_outcome';
    ELSE
        -- Crear scheme completo desde cero
        INSERT INTO ref.category (scheme, code, label, metadata) VALUES
        ('cgr_outcome', 'TOMADO_DE_RAZON', 'Tomado de Razón',
            '{"description": "Aprobado sin observaciones por CGR", "ontology": "tde:EstadoCGR", "severity": "APROBADO"}'),
        ('cgr_outcome', 'TR_CON_ALCANCES', 'Tomado de Razón con Alcances',
            '{"description": "Aprobado con observaciones por CGR", "ontology": "tde:EstadoCGR", "severity": "APROBADO_CON_OBSERVACIONES"}'),
        ('cgr_outcome', 'REPRESENTADO', 'Representado',
            '{"description": "Rechazado por CGR (representación)", "ontology": "tde:EstadoCGR", "severity": "RECHAZADO"}'),
        ('cgr_outcome', 'EN_CGR', 'En CGR',
            '{"description": "En proceso de revisión en CGR", "ontology": "tde:EstadoCGR", "severity": "EN_PROCESO"}');

        RAISE NOTICE 'Scheme cgr_outcome creado desde cero';
    END IF;

    RAISE NOTICE 'Total categorías en scheme cgr_outcome: %',
        (SELECT COUNT(*) FROM ref.category WHERE scheme = 'cgr_outcome');
END $$;

-- Agregar columna cgr_outcome_id en agreement
-- NOTA: Dado que NO existe core.resolution.agreement_id, agregamos directamente en agreement
ALTER TABLE core.agreement ADD COLUMN cgr_outcome_id UUID REFERENCES ref.category(id);

-- Agregar CHECK constraint
ALTER TABLE core.agreement ADD CONSTRAINT chk_cgr_outcome_scheme
    CHECK (cgr_outcome_id IS NULL OR
           fn_validate_category_scheme(cgr_outcome_id, 'cgr_outcome'));

-- Crear índice
CREATE INDEX idx_agreement_cgr_outcome ON core.agreement(cgr_outcome_id)
    WHERE cgr_outcome_id IS NOT NULL;

COMMENT ON COLUMN core.agreement.cgr_outcome_id IS 'Estado resultado de revisión en CGR (FK → ref.category scheme=cgr_outcome)';

-- Migrar datos desde agreement.metadata->>'estado_cgr_norm'
UPDATE core.agreement a
SET cgr_outcome_id = (
    SELECT c.id
    FROM ref.category c
    WHERE c.scheme = 'cgr_outcome'
    AND c.code = a.metadata->>'estado_cgr_norm'
)
WHERE a.metadata->>'estado_cgr_norm' IS NOT NULL;

-- Verificaciones post-migración Fase 3
DO $$
DECLARE
    v_total_agreements INTEGER;
    v_migrated INTEGER;
    v_pct NUMERIC;
    rec RECORD;
BEGIN
    SELECT COUNT(*) INTO v_total_agreements
        FROM core.agreement WHERE metadata->>'estado_cgr_norm' IS NOT NULL;
    SELECT COUNT(*) INTO v_migrated
        FROM core.agreement WHERE cgr_outcome_id IS NOT NULL;

    v_pct := CASE WHEN v_total_agreements > 0
                  THEN ROUND((v_migrated::NUMERIC / v_total_agreements * 100), 2)
                  ELSE 0 END;

    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'VERIFICACION FASE 3: estado_cgr_norm → cgr_outcome_id';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'Total agreements con estado_cgr_norm: %', v_total_agreements;
    RAISE NOTICE 'Agreements con cgr_outcome_id asignado: %', v_migrated;
    RAISE NOTICE 'Tasa de éxito: % %%', v_pct;

    -- Distribución por estado CGR
    RAISE NOTICE '';
    RAISE NOTICE 'DISTRIBUCION POR ESTADO CGR:';
    FOR rec IN
        SELECT c.code, c.label, COUNT(a.id) as total
        FROM ref.category c
        LEFT JOIN core.agreement a ON a.cgr_outcome_id = c.id
        WHERE c.scheme = 'cgr_outcome'
        GROUP BY c.id, c.code, c.label
        ORDER BY total DESC
    LOOP
        RAISE NOTICE '  % (%): % agreements', rec.label, rec.code, rec.total;
    END LOOP;
    RAISE NOTICE '====================================================================';

    IF v_pct < 100 THEN
        RAISE WARNING 'Migración parcial: solo % %% de estados CGR fueron migrados', v_pct;
    ELSE
        RAISE NOTICE 'Migración EXITOSA: 100%% de estados CGR migrados';
    END IF;
END $$;

COMMIT;

\echo ''
\echo '======================================================================'
\echo 'VERIFICACIONES FINALES Y COHERENCIA CATEGORIAL'
\echo '======================================================================'
\echo ''

-- ============================================================================
-- VERIFICACIONES FINALES
-- ============================================================================

DO $$
DECLARE
    v_position_count INTEGER;
    v_qualification_count INTEGER;
    v_cgr_outcome_count INTEGER;
    v_person_position_count INTEGER;
    v_person_qualification_count INTEGER;
    v_agreement_cgr_count INTEGER;
BEGIN
    -- Contar categorías creadas
    SELECT COUNT(*) INTO v_position_count FROM core.position;
    SELECT COUNT(*) INTO v_qualification_count FROM ref.category WHERE scheme = 'professional_qualification';
    SELECT COUNT(*) INTO v_cgr_outcome_count FROM ref.category WHERE scheme = 'cgr_outcome';

    -- Contar asignaciones
    SELECT COUNT(*) INTO v_person_position_count FROM core.person WHERE position_id IS NOT NULL;
    SELECT COUNT(*) INTO v_person_qualification_count FROM core.person WHERE qualification_id IS NOT NULL;
    SELECT COUNT(*) INTO v_agreement_cgr_count FROM core.agreement WHERE cgr_outcome_id IS NOT NULL;

    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'RESUMEN FINAL: NORMALIZACION JSONB V3 - FASE MEDIA (CAMPOS 1-3)';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'FASE 1 - cargo_ultimo → core.position:';
    RAISE NOTICE '  - Tabla core.position creada: SI';
    RAISE NOTICE '  - Total positions: %', v_position_count;
    RAISE NOTICE '  - Personas con position_id: %', v_person_position_count;
    RAISE NOTICE '';
    RAISE NOTICE 'FASE 2 - calificacion → professional_qualification:';
    RAISE NOTICE '  - Scheme professional_qualification creado: SI';
    RAISE NOTICE '  - Total categorías: %', v_qualification_count;
    RAISE NOTICE '  - Personas con qualification_id: %', v_person_qualification_count;
    RAISE NOTICE '';
    RAISE NOTICE 'FASE 3 - estado_cgr_norm → cgr_outcome:';
    RAISE NOTICE '  - Scheme cgr_outcome creado: SI';
    RAISE NOTICE '  - Total categorías: %', v_cgr_outcome_count;
    RAISE NOTICE '  - Agreements con cgr_outcome_id: %', v_agreement_cgr_count;
    RAISE NOTICE '';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'COHERENCIA CATEGORIAL (Categorical Univocity):';
    RAISE NOTICE '====================================================================';
END $$;

-- Verificar Categorical Univocity para qualification_id
SELECT
    'qualification_id' AS campo,
    COUNT(DISTINCT c.scheme) AS schemes,
    STRING_AGG(DISTINCT c.scheme, ', ') AS scheme_list,
    COUNT(*) AS total_registros
FROM core.person p
JOIN ref.category c ON c.id = p.qualification_id
WHERE p.qualification_id IS NOT NULL;

-- Verificar Categorical Univocity para cgr_outcome_id
SELECT
    'cgr_outcome_id' AS campo,
    COUNT(DISTINCT c.scheme) AS schemes,
    STRING_AGG(DISTINCT c.scheme, ', ') AS scheme_list,
    COUNT(*) AS total_registros
FROM core.agreement a
JOIN ref.category c ON c.id = a.cgr_outcome_id
WHERE a.cgr_outcome_id IS NOT NULL;

\echo ''
\echo '======================================================================'
\echo 'NOTA: Los campos JSONB originales se mantienen en metadata para audit trail'
\echo '======================================================================'
\echo ''

DO $$
BEGIN
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'IMPORTANTE: MANTENIMIENTO DE AUDIT TRAIL';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'Los siguientes campos JSONB se MANTIENEN en metadata para trazabilidad:';
    RAISE NOTICE '  - core.person.metadata->>"cargo_ultimo"';
    RAISE NOTICE '  - core.person.metadata->>"calificacion"';
    RAISE NOTICE '  - core.agreement.metadata->>"estado_cgr_norm"';
    RAISE NOTICE '';
    RAISE NOTICE 'Los nuevos campos relacionales son la fuente de verdad:';
    RAISE NOTICE '  - core.person.position_id → core.position';
    RAISE NOTICE '  - core.person.qualification_id → ref.category (professional_qualification)';
    RAISE NOTICE '  - core.agreement.cgr_outcome_id → ref.category (cgr_outcome)';
    RAISE NOTICE '====================================================================';
END $$;

\echo ''
\echo '============================================================================'
\echo 'FIN: NORMALIZACION JSONB V3 - FASE MEDIA (CAMPOS 1-3) COMPLETADA'
\echo '============================================================================'
\echo ''
\echo 'Próximos pasos:'
\echo '1. Verificar coherencia categorial (Categorical Univocity = 100%)'
\echo '2. Actualizar vistas y consultas que usen los campos JSONB antiguos'
\echo '3. Ejecutar NORMALIZACION V3 - FASE MEDIA (CAMPOS 4-6) si se requiere'
\echo ''

-- FIN DEL SCRIPT
