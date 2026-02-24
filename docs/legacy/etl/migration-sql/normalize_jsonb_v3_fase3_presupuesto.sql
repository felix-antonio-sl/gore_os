-- ==============================================================================
-- NORMALIZACION JSONB v3.0 - FASE 3: PRESUPUESTO
-- ==============================================================================
-- ARQUITECTO-GORE v0.1.0
-- Fecha: 2026-01-30
-- Motor: CM-ARTIFACT-GENERATOR
-- Fundamento: docs/AUDITORIA_CATEGORIAL_v3.0.md (Secciones 7, 11, 12)
-- Template: etl/migration/sql/normalize_ipr_metadata_v2.sql
--
-- ACCIONES EN ESTA FASE:
--   1. Crear scheme budget_item (14 valores)
--   2. Crear scheme budget_allocation (170 valores)
--   3. Agregar columnas item_id, allocation_id en budget_program
--   4. Crear tabla budget_carryover (arrastres anuales)
--   5. Agregar columnas fndr_amount, sectorial_amount (prioridad media)
--   6. Migrar datos desde metadata
--   7. Agregar CHECK constraints
--
-- ONTOLOGIA:
--   gnub:BudgetItem - Item del Clasificador Presupuestario chileno
--   gnub:BudgetAllocation - Asignacion del Clasificador Presupuestario
--   gnub:BudgetCarryover - Arrastre presupuestario anual
--
-- PREREQUISITOS:
--   - fn_validate_category_scheme debe existir
--   - core.budget_program debe tener datos
--
-- COHERENCIA ESPERADA: 100% (univocidad categorial)
-- ==============================================================================

\set ON_ERROR_STOP on
\timing on

-- ==============================================================================
-- CONFIGURACION
-- ==============================================================================

DO $$ BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '  NORMALIZACION JSONB v3.0 - FASE 3: PRESUPUESTO                      ';
    RAISE NOTICE '  Arquitecto-GORE | Coherencia Categorial | Clasificador Presupuestario';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '';
END $$;

-- Crear funcion helper para reportes
CREATE OR REPLACE FUNCTION report_phase(phase_name TEXT, status TEXT) RETURNS void AS $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '------------------------------------------------------------------------';
    RAISE NOTICE 'FASE: % - %', phase_name, status;
    RAISE NOTICE '------------------------------------------------------------------------';
    RAISE NOTICE '';
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- PRE-EJECUCION: VALIDACIONES
-- ==============================================================================

SELECT report_phase('PRE-EJECUCION', 'Validaciones de Seguridad');

-- Validar que funcion de coherencia categorial existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'fn_validate_category_scheme') THEN
        RAISE EXCEPTION 'Funcion fn_validate_category_scheme NO existe. Ejecutar goreos_ddl.sql primero.';
    END IF;
    RAISE NOTICE '[OK] Funcion fn_validate_category_scheme existe';
END $$;

-- Validar que core.budget_program tiene datos
DO $$
DECLARE
    bp_count INTEGER;
    metadata_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO bp_count FROM core.budget_program;
    SELECT COUNT(*) INTO metadata_count FROM core.budget_program WHERE metadata IS NOT NULL AND metadata != '{}'::jsonb;

    IF bp_count = 0 THEN
        RAISE EXCEPTION 'Tabla core.budget_program esta vacia. No hay datos para normalizar.';
    END IF;

    IF metadata_count = 0 THEN
        RAISE WARNING 'Ningun budget_program tiene metadata. Script puede no tener efecto.';
    END IF;

    RAISE NOTICE '[OK] core.budget_program tiene % registros, % con metadata', bp_count, metadata_count;
END $$;

-- Verificar campos objetivo existen en metadata
DO $$
DECLARE
    item_count INTEGER;
    asig_count INTEGER;
    arr24_count INTEGER;
    arr25_count INTEGER;
    arr26_count INTEGER;
    fndr_count INTEGER;
    sect_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO item_count FROM core.budget_program WHERE metadata ? 'item';
    SELECT COUNT(*) INTO asig_count FROM core.budget_program WHERE metadata ? 'asignacion';
    SELECT COUNT(*) INTO arr24_count FROM core.budget_program WHERE metadata ? 'arrastre_2024';
    SELECT COUNT(*) INTO arr25_count FROM core.budget_program WHERE metadata ? 'arrastre_2025';
    SELECT COUNT(*) INTO arr26_count FROM core.budget_program WHERE metadata ? 'arrastre_2026';
    SELECT COUNT(*) INTO fndr_count FROM core.budget_program WHERE metadata ? 'monto_fndr';
    SELECT COUNT(*) INTO sect_count FROM core.budget_program WHERE metadata ? 'monto_sectorial';

    RAISE NOTICE '[INFO] Campos a normalizar:';
    RAISE NOTICE '       - item: % registros', item_count;
    RAISE NOTICE '       - asignacion: % registros', asig_count;
    RAISE NOTICE '       - arrastre_2024: % registros', arr24_count;
    RAISE NOTICE '       - arrastre_2025: % registros', arr25_count;
    RAISE NOTICE '       - arrastre_2026: % registros', arr26_count;
    RAISE NOTICE '       - monto_fndr: % registros', fndr_count;
    RAISE NOTICE '       - monto_sectorial: % registros', sect_count;
END $$;

-- ==============================================================================
-- BACKUP: Snapshot de metadata pre-migracion
-- ==============================================================================

SELECT report_phase('BACKUP', 'Snapshot Metadata Pre-Migracion');

DROP TABLE IF EXISTS temp_budget_program_backup_v3;

CREATE TEMP TABLE temp_budget_program_backup_v3 AS
SELECT
    id,
    code,
    fiscal_year,
    metadata,
    now() AS backup_at
FROM core.budget_program
WHERE metadata IS NOT NULL AND metadata != '{}'::jsonb;

DO $$
DECLARE
    backup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO backup_count FROM temp_budget_program_backup_v3;
    RAISE NOTICE '[OK] Backup creado: % registros en temp_budget_program_backup_v3', backup_count;
    RAISE NOTICE '     Para rollback: SELECT * FROM temp_budget_program_backup_v3;';
END $$;

-- ==============================================================================
-- FASE 3.1: CREAR SCHEME budget_item (gnub:BudgetItem)
-- ==============================================================================

BEGIN;

SELECT report_phase('3.1', 'Crear Scheme budget_item (gnub:BudgetItem)');

-- Extraer items unicos del metadata
DO $$
DECLARE
    item_values TEXT[];
    created_count INTEGER;
BEGIN
    -- Obtener valores unicos
    SELECT ARRAY_AGG(DISTINCT metadata->>'item' ORDER BY metadata->>'item')
    INTO item_values
    FROM core.budget_program
    WHERE metadata->>'item' IS NOT NULL;

    RAISE NOTICE '[INFO] Items unicos encontrados: %', array_length(item_values, 1);
    RAISE NOTICE '[INFO] Valores: %', item_values;
END $$;

-- Insertar scheme budget_item
-- gnub:BudgetItem - Item del Clasificador Presupuestario chileno (Ley de Presupuestos)
WITH item_source AS (
    SELECT DISTINCT (metadata->>'item')::text AS code
    FROM core.budget_program
    WHERE metadata->>'item' IS NOT NULL
),
inserted AS (
    INSERT INTO ref.category (scheme, code, label, label_en, description, sort_order, metadata)
    SELECT
        'budget_item',
        code,
        CASE
            WHEN code = '0' THEN 'Sin Item Asignado'
            WHEN code = '1' THEN 'Item 01 - Gastos en Personal'
            WHEN code = '2' THEN 'Item 02 - Bienes y Servicios de Consumo'
            WHEN code = '3' THEN 'Item 03 - Transferencias Corrientes'
            WHEN code = '4' THEN 'Item 04 - Intereses de Deuda'
            WHEN code = '5' THEN 'Item 05 - Otros Gastos Corrientes'
            WHEN code = '6' THEN 'Item 06 - Adquisicion Activos No Financieros'
            WHEN code = '7' THEN 'Item 07 - Inversiones'
            WHEN code = '9' THEN 'Item 09 - Adquisicion Activos Financieros'
            WHEN code = '99' THEN 'Item 99 - Saldo Final de Caja'
            WHEN code LIKE '%/%' THEN 'Items Multiples (' || code || ')'
            ELSE 'Item ' || code
        END,
        CASE
            WHEN code = '0' THEN 'No Item Assigned'
            WHEN code = '1' THEN 'Item 01 - Personnel Expenses'
            WHEN code = '2' THEN 'Item 02 - Goods and Consumption Services'
            WHEN code = '3' THEN 'Item 03 - Current Transfers'
            WHEN code = '4' THEN 'Item 04 - Debt Interest'
            WHEN code = '5' THEN 'Item 05 - Other Current Expenses'
            WHEN code = '6' THEN 'Item 06 - Non-Financial Assets Acquisition'
            WHEN code = '7' THEN 'Item 07 - Investments'
            WHEN code = '9' THEN 'Item 09 - Financial Assets Acquisition'
            WHEN code = '99' THEN 'Item 99 - Final Cash Balance'
            ELSE 'Item ' || code
        END,
        'Item del Clasificador Presupuestario Publico - Ley de Presupuestos Chile',
        CASE
            WHEN code ~ '^\d+$' THEN code::integer
            ELSE 999
        END,
        jsonb_build_object(
            'gnub_class', 'BudgetItem',
            'source', 'Clasificador Presupuestario DIPRES',
            'created_by', 'normalize_jsonb_v3_fase3'
        )
    FROM item_source
    ON CONFLICT (scheme, code) DO NOTHING
    RETURNING id
)
SELECT COUNT(*) AS created FROM inserted;

DO $$
DECLARE
    scheme_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO scheme_count
    FROM ref.category WHERE scheme = 'budget_item';

    RAISE NOTICE '[OK] Scheme budget_item: % codigos en ref.category', scheme_count;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 3.2: CREAR SCHEME budget_allocation (gnub:BudgetAllocation)
-- ==============================================================================

BEGIN;

SELECT report_phase('3.2', 'Crear Scheme budget_allocation (gnub:BudgetAllocation)');

-- Contar valores unicos
DO $$
DECLARE
    alloc_count INTEGER;
BEGIN
    SELECT COUNT(DISTINCT metadata->>'asignacion') INTO alloc_count
    FROM core.budget_program
    WHERE metadata->>'asignacion' IS NOT NULL;

    RAISE NOTICE '[INFO] Asignaciones unicas encontradas: %', alloc_count;
END $$;

-- Insertar scheme budget_allocation
-- gnub:BudgetAllocation - Asignacion del Clasificador Presupuestario
WITH alloc_source AS (
    SELECT DISTINCT (metadata->>'asignacion')::text AS code
    FROM core.budget_program
    WHERE metadata->>'asignacion' IS NOT NULL
),
inserted AS (
    INSERT INTO ref.category (scheme, code, label, label_en, description, sort_order, metadata)
    SELECT
        'budget_allocation',
        code,
        CASE
            WHEN code = '0' THEN 'Sin Asignacion'
            WHEN code = '125' THEN 'Asignacion 125 - FNDR'
            WHEN code = '100' THEN 'Asignacion 100 - Subsidios'
            WHEN code = '200' THEN 'Asignacion 200 - Transferencias a Entidades Publicas'
            WHEN code = '300' THEN 'Asignacion 300 - Transferencias a Entidades Privadas'
            WHEN code = '490' THEN 'Asignacion 490 - Otros'
            WHEN code = '999' THEN 'Asignacion 999 - No Clasificado'
            WHEN code LIKE '%/%' THEN 'Asignaciones Multiples (' || code || ')'
            ELSE 'Asignacion ' || code
        END,
        'Allocation ' || code,
        'Asignacion del Clasificador Presupuestario Publico - Ley de Presupuestos Chile',
        CASE
            WHEN code ~ '^\d+$' THEN code::integer
            ELSE 9999
        END,
        jsonb_build_object(
            'gnub_class', 'BudgetAllocation',
            'source', 'Clasificador Presupuestario DIPRES',
            'created_by', 'normalize_jsonb_v3_fase3'
        )
    FROM alloc_source
    ON CONFLICT (scheme, code) DO NOTHING
    RETURNING id
)
SELECT COUNT(*) AS created FROM inserted;

DO $$
DECLARE
    scheme_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO scheme_count
    FROM ref.category WHERE scheme = 'budget_allocation';

    RAISE NOTICE '[OK] Scheme budget_allocation: % codigos en ref.category', scheme_count;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 3.3: AGREGAR COLUMNAS item_id Y allocation_id EN budget_program
-- ==============================================================================

BEGIN;

SELECT report_phase('3.3', 'Agregar Columnas item_id y allocation_id');

-- Agregar columna item_id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'budget_program'
          AND column_name = 'item_id'
    ) THEN
        ALTER TABLE core.budget_program
            ADD COLUMN item_id UUID REFERENCES ref.category(id);

        COMMENT ON COLUMN core.budget_program.item_id IS
            'gnub:BudgetItem - Item del Clasificador Presupuestario Publico (Ley de Presupuestos Chile). Normalizado desde metadata.item en 2026-01-30.';

        RAISE NOTICE '[OK] Columna item_id agregada a core.budget_program';
    ELSE
        RAISE NOTICE '[SKIP] Columna item_id ya existe';
    END IF;
END $$;

-- Agregar columna allocation_id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'budget_program'
          AND column_name = 'allocation_id'
    ) THEN
        ALTER TABLE core.budget_program
            ADD COLUMN allocation_id UUID REFERENCES ref.category(id);

        COMMENT ON COLUMN core.budget_program.allocation_id IS
            'gnub:BudgetAllocation - Asignacion del Clasificador Presupuestario Publico. Normalizado desde metadata.asignacion en 2026-01-30.';

        RAISE NOTICE '[OK] Columna allocation_id agregada a core.budget_program';
    ELSE
        RAISE NOTICE '[SKIP] Columna allocation_id ya existe';
    END IF;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 3.4: MIGRAR DATOS item Y asignacion
-- ==============================================================================

BEGIN;

SELECT report_phase('3.4', 'Migrar Datos item y asignacion');

-- Conteo pre-migracion
DO $$
DECLARE
    pre_item INTEGER;
    pre_alloc INTEGER;
BEGIN
    SELECT COUNT(*) INTO pre_item FROM core.budget_program WHERE item_id IS NOT NULL;
    SELECT COUNT(*) INTO pre_alloc FROM core.budget_program WHERE allocation_id IS NOT NULL;

    RAISE NOTICE '[PRE] item_id poblados: %, allocation_id poblados: %', pre_item, pre_alloc;
END $$;

-- Migrar item_id
WITH updated AS (
    UPDATE core.budget_program bp
    SET item_id = c.id
    FROM ref.category c
    WHERE c.scheme = 'budget_item'
      AND c.code = bp.metadata->>'item'
      AND bp.metadata->>'item' IS NOT NULL
      AND bp.item_id IS NULL
    RETURNING bp.id
)
SELECT COUNT(*) AS migrated_items FROM updated;

-- Migrar allocation_id
WITH updated AS (
    UPDATE core.budget_program bp
    SET allocation_id = c.id
    FROM ref.category c
    WHERE c.scheme = 'budget_allocation'
      AND c.code = bp.metadata->>'asignacion'
      AND bp.metadata->>'asignacion' IS NOT NULL
      AND bp.allocation_id IS NULL
    RETURNING bp.id
)
SELECT COUNT(*) AS migrated_allocations FROM updated;

-- Conteo post-migracion
DO $$
DECLARE
    post_item INTEGER;
    post_alloc INTEGER;
    expected_item INTEGER;
    expected_alloc INTEGER;
BEGIN
    SELECT COUNT(*) INTO post_item FROM core.budget_program WHERE item_id IS NOT NULL;
    SELECT COUNT(*) INTO post_alloc FROM core.budget_program WHERE allocation_id IS NOT NULL;
    SELECT COUNT(*) INTO expected_item FROM core.budget_program WHERE metadata->>'item' IS NOT NULL;
    SELECT COUNT(*) INTO expected_alloc FROM core.budget_program WHERE metadata->>'asignacion' IS NOT NULL;

    RAISE NOTICE '[POST] item_id poblados: % (esperado: %)', post_item, expected_item;
    RAISE NOTICE '[POST] allocation_id poblados: % (esperado: %)', post_alloc, expected_alloc;

    IF post_item < expected_item THEN
        RAISE WARNING '[WARN] Algunos items no migraron. Verificar valores faltantes.';
    END IF;

    IF post_alloc < expected_alloc THEN
        RAISE WARNING '[WARN] Algunas asignaciones no migraron. Verificar valores faltantes.';
    END IF;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 3.5: CREAR TABLA budget_carryover (gnub:BudgetCarryover)
-- ==============================================================================

BEGIN;

SELECT report_phase('3.5', 'Crear Tabla budget_carryover');

-- Crear tabla si no existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'core'
          AND table_name = 'budget_carryover'
    ) THEN
        CREATE TABLE core.budget_carryover (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            budget_program_id UUID NOT NULL REFERENCES core.budget_program(id) ON DELETE CASCADE,
            fiscal_year SMALLINT NOT NULL,
            amount NUMERIC(18,2) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            created_by_id UUID REFERENCES core."user"(id),
            metadata JSONB DEFAULT '{}'::jsonb,
            CONSTRAINT budget_carryover_unique_year UNIQUE (budget_program_id, fiscal_year),
            CONSTRAINT chk_fiscal_year_range CHECK (fiscal_year BETWEEN 2000 AND 2100),
            CONSTRAINT chk_amount_positive CHECK (amount >= 0)
        );

        -- Comentario de tabla
        COMMENT ON TABLE core.budget_carryover IS
            'gnub:BudgetCarryover - Arrastres presupuestarios anuales por programa. Modelo time-series para tracking de saldos arrastrados entre ejercicios fiscales.';

        COMMENT ON COLUMN core.budget_carryover.budget_program_id IS
            'FK al programa presupuestario origen del arrastre';
        COMMENT ON COLUMN core.budget_carryover.fiscal_year IS
            'Anio fiscal destino del arrastre (ej: 2024 = arrastre hacia 2024)';
        COMMENT ON COLUMN core.budget_carryover.amount IS
            'Monto arrastrado en CLP';

        -- Indice para queries por anio
        CREATE INDEX idx_budget_carryover_year
            ON core.budget_carryover(fiscal_year);

        -- Indice para queries por programa
        CREATE INDEX idx_budget_carryover_program
            ON core.budget_carryover(budget_program_id);

        -- Trigger para updated_at
        CREATE TRIGGER trg_budget_carryover_updated_at
            BEFORE UPDATE ON core.budget_carryover
            FOR EACH ROW
            EXECUTE FUNCTION fn_update_timestamp();

        RAISE NOTICE '[OK] Tabla core.budget_carryover creada con indices y constraints';
    ELSE
        RAISE NOTICE '[SKIP] Tabla core.budget_carryover ya existe';
    END IF;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 3.6: MIGRAR DATOS DE ARRASTRES
-- ==============================================================================

BEGIN;

SELECT report_phase('3.6', 'Migrar Datos de Arrastres');

-- Contar registros pre-migracion
DO $$
DECLARE
    pre_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO pre_count FROM core.budget_carryover;
    RAISE NOTICE '[PRE] Registros en budget_carryover: %', pre_count;
END $$;

-- Migrar arrastre_2024
INSERT INTO core.budget_carryover (budget_program_id, fiscal_year, amount, metadata)
SELECT
    id,
    2024,
    COALESCE((metadata->>'arrastre_2024')::numeric, 0),
    jsonb_build_object(
        'source', 'MIGRATION_V3',
        'migrated_from', 'metadata.arrastre_2024',
        'migrated_at', now()::text
    )
FROM core.budget_program
WHERE metadata->>'arrastre_2024' IS NOT NULL
  AND (metadata->>'arrastre_2024')::numeric > 0
ON CONFLICT (budget_program_id, fiscal_year) DO NOTHING;

DO $$
DECLARE
    cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO cnt FROM core.budget_carryover WHERE fiscal_year = 2024;
    RAISE NOTICE '[OK] Arrastres 2024 migrados: %', cnt;
END $$;

-- Migrar arrastre_2025
INSERT INTO core.budget_carryover (budget_program_id, fiscal_year, amount, metadata)
SELECT
    id,
    2025,
    COALESCE((metadata->>'arrastre_2025')::numeric, 0),
    jsonb_build_object(
        'source', 'MIGRATION_V3',
        'migrated_from', 'metadata.arrastre_2025',
        'migrated_at', now()::text
    )
FROM core.budget_program
WHERE metadata->>'arrastre_2025' IS NOT NULL
  AND (metadata->>'arrastre_2025')::numeric > 0
ON CONFLICT (budget_program_id, fiscal_year) DO NOTHING;

DO $$
DECLARE
    cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO cnt FROM core.budget_carryover WHERE fiscal_year = 2025;
    RAISE NOTICE '[OK] Arrastres 2025 migrados: %', cnt;
END $$;

-- Migrar arrastre_2026
INSERT INTO core.budget_carryover (budget_program_id, fiscal_year, amount, metadata)
SELECT
    id,
    2026,
    COALESCE((metadata->>'arrastre_2026')::numeric, 0),
    jsonb_build_object(
        'source', 'MIGRATION_V3',
        'migrated_from', 'metadata.arrastre_2026',
        'migrated_at', now()::text
    )
FROM core.budget_program
WHERE metadata->>'arrastre_2026' IS NOT NULL
  AND (metadata->>'arrastre_2026')::numeric > 0
ON CONFLICT (budget_program_id, fiscal_year) DO NOTHING;

DO $$
DECLARE
    cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO cnt FROM core.budget_carryover WHERE fiscal_year = 2026;
    RAISE NOTICE '[OK] Arrastres 2026 migrados: %', cnt;
END $$;

-- Reporte consolidado
DO $$
DECLARE
    total_carryovers INTEGER;
    total_amount NUMERIC;
BEGIN
    SELECT COUNT(*), COALESCE(SUM(amount), 0)
    INTO total_carryovers, total_amount
    FROM core.budget_carryover;

    RAISE NOTICE '';
    RAISE NOTICE '[RESUMEN] budget_carryover:';
    RAISE NOTICE '          Total registros: %', total_carryovers;
    RAISE NOTICE '          Total monto: $%', TO_CHAR(total_amount, 'FM999,999,999,999');
END $$;

COMMIT;

-- ==============================================================================
-- FASE 3.7: AGREGAR COLUMNAS fndr_amount Y sectorial_amount
-- ==============================================================================

BEGIN;

SELECT report_phase('3.7', 'Agregar Columnas fndr_amount y sectorial_amount');

-- Agregar fndr_amount
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'budget_program'
          AND column_name = 'fndr_amount'
    ) THEN
        ALTER TABLE core.budget_program
            ADD COLUMN fndr_amount NUMERIC(18,2);

        COMMENT ON COLUMN core.budget_program.fndr_amount IS
            'Monto FNDR (Fondo Nacional de Desarrollo Regional) asignado al programa. Normalizado desde metadata.monto_fndr en 2026-01-30.';

        RAISE NOTICE '[OK] Columna fndr_amount agregada';
    ELSE
        RAISE NOTICE '[SKIP] Columna fndr_amount ya existe';
    END IF;
END $$;

-- Agregar sectorial_amount
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'core'
          AND table_name = 'budget_program'
          AND column_name = 'sectorial_amount'
    ) THEN
        ALTER TABLE core.budget_program
            ADD COLUMN sectorial_amount NUMERIC(18,2);

        COMMENT ON COLUMN core.budget_program.sectorial_amount IS
            'Monto de origen sectorial (ministerial) asignado al programa. Normalizado desde metadata.monto_sectorial en 2026-01-30.';

        RAISE NOTICE '[OK] Columna sectorial_amount agregada';
    ELSE
        RAISE NOTICE '[SKIP] Columna sectorial_amount ya existe';
    END IF;
END $$;

-- Migrar fndr_amount
WITH updated AS (
    UPDATE core.budget_program
    SET fndr_amount = (metadata->>'monto_fndr')::numeric
    WHERE metadata->>'monto_fndr' IS NOT NULL
      AND fndr_amount IS NULL
    RETURNING id
)
SELECT COUNT(*) AS migrated_fndr FROM updated;

-- Migrar sectorial_amount
WITH updated AS (
    UPDATE core.budget_program
    SET sectorial_amount = (metadata->>'monto_sectorial')::numeric
    WHERE metadata->>'monto_sectorial' IS NOT NULL
      AND sectorial_amount IS NULL
    RETURNING id
)
SELECT COUNT(*) AS migrated_sectorial FROM updated;

DO $$
DECLARE
    fndr_count INTEGER;
    sect_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO fndr_count FROM core.budget_program WHERE fndr_amount IS NOT NULL;
    SELECT COUNT(*) INTO sect_count FROM core.budget_program WHERE sectorial_amount IS NOT NULL;

    RAISE NOTICE '[POST] fndr_amount poblados: %', fndr_count;
    RAISE NOTICE '[POST] sectorial_amount poblados: %', sect_count;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 3.8: CHECK CONSTRAINTS PARA COHERENCIA CATEGORIAL
-- ==============================================================================

BEGIN;

SELECT report_phase('3.8', 'Agregar CHECK Constraints');

-- Remover constraints existentes si los hay
DO $$
BEGIN
    ALTER TABLE core.budget_program
        DROP CONSTRAINT IF EXISTS chk_item_scheme,
        DROP CONSTRAINT IF EXISTS chk_allocation_scheme;

    RAISE NOTICE '[OK] Constraints anteriores removidos (si existian)';
EXCEPTION WHEN undefined_object THEN
    RAISE NOTICE '[OK] No habia constraints previos';
END $$;

-- Agregar CHECK constraint para item_id
DO $$
BEGIN
    ALTER TABLE core.budget_program
        ADD CONSTRAINT chk_item_scheme
            CHECK (item_id IS NULL OR fn_validate_category_scheme(item_id, 'budget_item'));

    RAISE NOTICE '[OK] CHECK constraint chk_item_scheme agregado';
END $$;

-- Agregar CHECK constraint para allocation_id
DO $$
BEGIN
    ALTER TABLE core.budget_program
        ADD CONSTRAINT chk_allocation_scheme
            CHECK (allocation_id IS NULL OR fn_validate_category_scheme(allocation_id, 'budget_allocation'));

    RAISE NOTICE '[OK] CHECK constraint chk_allocation_scheme agregado';
END $$;

-- Listar constraints creados
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '[INFO] Constraints creados en core.budget_program:';
END $$;

SELECT '       - ' || conname AS constraint_name
FROM pg_constraint
WHERE conrelid = 'core.budget_program'::regclass
  AND contype = 'c'
  AND conname LIKE 'chk_%'
ORDER BY conname;

COMMIT;

-- ==============================================================================
-- FASE 3.9: INDICES DE PERFORMANCE
-- ==============================================================================

BEGIN;

SELECT report_phase('3.9', 'Crear Indices de Performance');

-- Indice en item_id
CREATE INDEX IF NOT EXISTS idx_budget_program_item
    ON core.budget_program(item_id)
    WHERE item_id IS NOT NULL;

-- Indice en allocation_id
CREATE INDEX IF NOT EXISTS idx_budget_program_allocation
    ON core.budget_program(allocation_id)
    WHERE allocation_id IS NOT NULL;

-- Indice GIN en metadata (si no existe)
CREATE INDEX IF NOT EXISTS idx_budget_program_metadata_gin
    ON core.budget_program USING gin(metadata);

DO $$
BEGIN
    RAISE NOTICE '[OK] Indices creados: idx_budget_program_item, idx_budget_program_allocation';
END $$;

-- ANALYZE para actualizar estadisticas
ANALYZE core.budget_program;
ANALYZE core.budget_carryover;

DO $$
BEGIN
    RAISE NOTICE '[OK] ANALYZE ejecutado en budget_program y budget_carryover';
END $$;

COMMIT;

-- ==============================================================================
-- VERIFICACIONES FINALES
-- ==============================================================================

SELECT report_phase('VERIFICACIONES', 'Validaciones Post-Migracion');

-- Verificacion 1: Coherencia categorial item_id
DO $$
DECLARE
    incoherent INTEGER;
BEGIN
    SELECT COUNT(*) INTO incoherent
    FROM core.budget_program bp
    JOIN ref.category c ON c.id = bp.item_id
    WHERE c.scheme != 'budget_item';

    IF incoherent = 0 THEN
        RAISE NOTICE '[PASS] Coherencia item_id: 100%% (todos scheme=budget_item)';
    ELSE
        RAISE WARNING '[FAIL] % registros con item_id incoherente', incoherent;
    END IF;
END $$;

-- Verificacion 2: Coherencia categorial allocation_id
DO $$
DECLARE
    incoherent INTEGER;
BEGIN
    SELECT COUNT(*) INTO incoherent
    FROM core.budget_program bp
    JOIN ref.category c ON c.id = bp.allocation_id
    WHERE c.scheme != 'budget_allocation';

    IF incoherent = 0 THEN
        RAISE NOTICE '[PASS] Coherencia allocation_id: 100%% (todos scheme=budget_allocation)';
    ELSE
        RAISE WARNING '[FAIL] % registros con allocation_id incoherente', incoherent;
    END IF;
END $$;

-- Verificacion 3: Migracion completa item
DO $$
DECLARE
    in_metadata INTEGER;
    in_column INTEGER;
BEGIN
    SELECT COUNT(*) INTO in_metadata FROM core.budget_program WHERE metadata->>'item' IS NOT NULL;
    SELECT COUNT(*) INTO in_column FROM core.budget_program WHERE item_id IS NOT NULL;

    IF in_column >= in_metadata THEN
        RAISE NOTICE '[PASS] Migracion item completa: % de % (100%%)', in_column, in_metadata;
    ELSE
        RAISE WARNING '[WARN] Migracion item incompleta: % de %', in_column, in_metadata;
    END IF;
END $$;

-- Verificacion 4: Migracion completa allocation
DO $$
DECLARE
    in_metadata INTEGER;
    in_column INTEGER;
BEGIN
    SELECT COUNT(*) INTO in_metadata FROM core.budget_program WHERE metadata->>'asignacion' IS NOT NULL;
    SELECT COUNT(*) INTO in_column FROM core.budget_program WHERE allocation_id IS NOT NULL;

    IF in_column >= in_metadata THEN
        RAISE NOTICE '[PASS] Migracion allocation completa: % de % (100%%)', in_column, in_metadata;
    ELSE
        RAISE WARNING '[WARN] Migracion allocation incompleta: % de %', in_column, in_metadata;
    END IF;
END $$;

-- Verificacion 5: Arrastres migrados
DO $$
DECLARE
    expected_2024 INTEGER;
    expected_2025 INTEGER;
    expected_2026 INTEGER;
    actual_2024 INTEGER;
    actual_2025 INTEGER;
    actual_2026 INTEGER;
BEGIN
    SELECT COUNT(*) INTO expected_2024 FROM core.budget_program WHERE metadata->>'arrastre_2024' IS NOT NULL AND (metadata->>'arrastre_2024')::numeric > 0;
    SELECT COUNT(*) INTO expected_2025 FROM core.budget_program WHERE metadata->>'arrastre_2025' IS NOT NULL AND (metadata->>'arrastre_2025')::numeric > 0;
    SELECT COUNT(*) INTO expected_2026 FROM core.budget_program WHERE metadata->>'arrastre_2026' IS NOT NULL AND (metadata->>'arrastre_2026')::numeric > 0;

    SELECT COUNT(*) INTO actual_2024 FROM core.budget_carryover WHERE fiscal_year = 2024;
    SELECT COUNT(*) INTO actual_2025 FROM core.budget_carryover WHERE fiscal_year = 2025;
    SELECT COUNT(*) INTO actual_2026 FROM core.budget_carryover WHERE fiscal_year = 2026;

    RAISE NOTICE '[INFO] Arrastres migrados:';
    RAISE NOTICE '       2024: % de % (%.1f%%)', actual_2024, expected_2024, (actual_2024::numeric / NULLIF(expected_2024, 0) * 100);
    RAISE NOTICE '       2025: % de % (%.1f%%)', actual_2025, expected_2025, (actual_2025::numeric / NULLIF(expected_2025, 0) * 100);
    RAISE NOTICE '       2026: % de % (%.1f%%)', actual_2026, expected_2026, (actual_2026::numeric / NULLIF(expected_2026, 0) * 100);
END $$;

-- Verificacion 6: Montos FNDR/Sectorial
DO $$
DECLARE
    fndr_count INTEGER;
    sect_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO fndr_count FROM core.budget_program WHERE fndr_amount IS NOT NULL AND fndr_amount > 0;
    SELECT COUNT(*) INTO sect_count FROM core.budget_program WHERE sectorial_amount IS NOT NULL AND sectorial_amount > 0;

    RAISE NOTICE '[INFO] Montos dimensionados:';
    RAISE NOTICE '       fndr_amount poblados: %', fndr_count;
    RAISE NOTICE '       sectorial_amount poblados: %', sect_count;
END $$;

-- ==============================================================================
-- REPORTE FINAL
-- ==============================================================================

DO $$ BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '  FASE 3 - PRESUPUESTO: COMPLETADA                                     ';
    RAISE NOTICE '========================================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'RESUMEN:';
    RAISE NOTICE '  - Schemes creados: budget_item (14 valores), budget_allocation (170 valores)';
    RAISE NOTICE '  - Columnas agregadas: item_id, allocation_id, fndr_amount, sectorial_amount';
    RAISE NOTICE '  - Tabla creada: core.budget_carryover';
    RAISE NOTICE '  - CHECK constraints: chk_item_scheme, chk_allocation_scheme';
    RAISE NOTICE '';
    RAISE NOTICE 'COHERENCIA CATEGORIAL: 100%% (Univocidad garantizada por constraints)';
    RAISE NOTICE '';
    RAISE NOTICE 'ONTOLOGIA:';
    RAISE NOTICE '  - gnub:BudgetItem -> ref.category(scheme=budget_item)';
    RAISE NOTICE '  - gnub:BudgetAllocation -> ref.category(scheme=budget_allocation)';
    RAISE NOTICE '  - gnub:BudgetCarryover -> core.budget_carryover';
    RAISE NOTICE '';
    RAISE NOTICE 'BACKUP: SELECT * FROM temp_budget_program_backup_v3;';
    RAISE NOTICE '';
    RAISE NOTICE 'PROXIMOS PASOS:';
    RAISE NOTICE '  1. Ejecutar en ambiente de TEST: psql -d goreos_model_test -f normalize_jsonb_v3_fase3_presupuesto.sql';
    RAISE NOTICE '  2. Validar queries de aplicacion';
    RAISE NOTICE '  3. Limpiar campos de metadata post-validacion (script separado)';
    RAISE NOTICE '  4. Documentar en ERD: model/model_goreos/docs/GOREOS_ERD_v3.md';
    RAISE NOTICE '';
END $$;

-- Limpiar funcion helper
DROP FUNCTION IF EXISTS report_phase(TEXT, TEXT);

-- ==============================================================================
-- FIN FASE 3 - PRESUPUESTO
-- ==============================================================================
