-- ==============================================================================
-- NORMALIZACIÓN JSONB v3.0 - FASE 4: EVENTOS
-- ==============================================================================
-- ARQUITECTO-GORE v0.1.0
-- Fecha: 2026-01-30
-- Motor: CM-ARTIFACT-GENERATOR
-- Fundamento: docs/AUDITORIA_CATEGORIAL_v3.0.md
--
-- ACCIONES:
--   1. Crear scheme magnitude_aspect con TRANSFER_AMOUNT
--   2. Crear scheme currency con CLP (si no existe)
--   3. Migrar monto_transferido → txn.magnitude (953 eventos, 677 valores únicos)
--   4. Corregir 3 eventos con subject_type='rendicion_8pct' anómalo
--   5. Marcar campos migrados en event.data (preservar audit trail)
--
-- ALINEAMIENTO ONTOLÓGICO:
--   - gist:Magnitude pattern (valor numérico + aspect + unit + fecha)
--   - gnub:MontoTransferido → Magnitude aspect
--   - tde:CLP → Currency unit
--
-- TABLAS AFECTADAS:
--   - txn.event (PARTICIONADA por occurred_at) - UPDATE subject_type
--   - txn.magnitude (PARTICIONADA por as_of_date) - INSERT nuevos registros
--   - ref.category - INSERT schemes (magnitude_aspect, currency)
--
-- NOTA: txn.magnitude tiene partición default para fechas < 2026-01-01
-- ==============================================================================

\set ON_ERROR_STOP on
\timing on

-- ==============================================================================
-- CONFIGURACIÓN Y HEADER
-- ==============================================================================

DO $$ BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '======================================================================';
    RAISE NOTICE '  NORMALIZACIÓN JSONB v3.0 - FASE 4: EVENTOS                        ';
    RAISE NOTICE '  Arquitecto-GORE | Patrón gist:Magnitude                           ';
    RAISE NOTICE '======================================================================';
    RAISE NOTICE '';
END $$;

-- Crear función helper para reportes (si no existe)
CREATE OR REPLACE FUNCTION report_phase(phase_name TEXT, status TEXT) RETURNS void AS $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '--------------------------------------------------------------------';
    RAISE NOTICE 'FASE: % - %', phase_name, status;
    RAISE NOTICE '--------------------------------------------------------------------';
    RAISE NOTICE '';
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- PRE-EJECUCIÓN: VALIDACIONES DE SEGURIDAD
-- ==============================================================================

SELECT report_phase('PRE-EJECUCIÓN', 'Validaciones de Seguridad');

-- Validar que txn.event existe y está particionada
DO $$
DECLARE
    is_partitioned BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM pg_partitioned_table
        WHERE partrelid = 'txn.event'::regclass
    ) INTO is_partitioned;

    IF NOT is_partitioned THEN
        RAISE EXCEPTION 'txn.event NO está particionada. Verificar DDL.';
    END IF;
    RAISE NOTICE '  txn.event está particionada';
END $$;

-- Validar que txn.magnitude existe y está particionada
DO $$
DECLARE
    is_partitioned BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM pg_partitioned_table
        WHERE partrelid = 'txn.magnitude'::regclass
    ) INTO is_partitioned;

    IF NOT is_partitioned THEN
        RAISE EXCEPTION 'txn.magnitude NO está particionada. Verificar DDL.';
    END IF;
    RAISE NOTICE '  txn.magnitude está particionada';
END $$;

-- Conteos PRE-MIGRACIÓN
DO $$
DECLARE
    event_total INTEGER;
    event_with_monto INTEGER;
    event_anomalous INTEGER;
    magnitude_total INTEGER;
BEGIN
    SELECT COUNT(*) INTO event_total FROM txn.event;
    SELECT COUNT(*) INTO event_with_monto
    FROM txn.event
    WHERE data ? 'monto_transferido'
      AND (data->>'monto_transferido')::numeric > 0;
    SELECT COUNT(*) INTO event_anomalous
    FROM txn.event
    WHERE subject_type = 'rendicion_8pct';
    SELECT COUNT(*) INTO magnitude_total FROM txn.magnitude;

    RAISE NOTICE '';
    RAISE NOTICE '  === CONTEOS PRE-MIGRACIÓN ===';
    RAISE NOTICE '  txn.event total:              %', event_total;
    RAISE NOTICE '  txn.event con monto_transferido (>0): %', event_with_monto;
    RAISE NOTICE '  txn.event con subject_type anómalo: %', event_anomalous;
    RAISE NOTICE '  txn.magnitude total:          %', magnitude_total;
    RAISE NOTICE '';
END $$;

-- ==============================================================================
-- BACKUP: Snapshot de eventos afectados
-- ==============================================================================

SELECT report_phase('BACKUP', 'Snapshot Eventos Pre-Migración');

DROP TABLE IF EXISTS temp_event_backup_fase4;

CREATE TEMP TABLE temp_event_backup_fase4 AS
SELECT
    id,
    event_type_id,
    subject_type,
    subject_id,
    occurred_at,
    data,
    now() AS backup_at
FROM txn.event
WHERE (data ? 'monto_transferido' AND (data->>'monto_transferido')::numeric > 0)
   OR subject_type = 'rendicion_8pct';

DO $$
DECLARE
    backup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO backup_count FROM temp_event_backup_fase4;
    RAISE NOTICE '  Backup creado: % eventos en temp_event_backup_fase4', backup_count;
    RAISE NOTICE '  Para rollback: SELECT * FROM temp_event_backup_fase4;';
END $$;

-- ==============================================================================
-- FASE 4.1: CREAR SCHEME magnitude_aspect
-- ==============================================================================

BEGIN;

SELECT report_phase('4.1', 'Crear Scheme magnitude_aspect');

-- Verificar si ya existe
DO $$
DECLARE
    existing_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO existing_count
    FROM ref.category
    WHERE scheme = 'magnitude_aspect';

    IF existing_count > 0 THEN
        RAISE NOTICE '  Scheme magnitude_aspect ya existe (% valores)', existing_count;
    ELSE
        RAISE NOTICE '  Scheme magnitude_aspect no existe, creando...';
    END IF;
END $$;

-- Crear scheme magnitude_aspect con TRANSFER_AMOUNT
-- Ontología: gist:Magnitude aspect - representa el tipo de medición
INSERT INTO ref.category (scheme, code, label, label_en, description, sort_order, metadata)
VALUES
    ('magnitude_aspect', 'TRANSFER_AMOUNT', 'Monto Transferido', 'Transfer Amount',
     'Monto de transferencia efectiva a institucion receptora (gist:Magnitude pattern)',
     1, jsonb_build_object(
         'gist_class', 'Magnitude',
         'gnub_class', 'MontoTransferido',
         'unit_scheme', 'currency',
         'created_from', 'AUDITORIA_CATEGORIAL_v3.0'
     )),
    ('magnitude_aspect', 'BUDGET_AMOUNT', 'Monto Presupuestado', 'Budget Amount',
     'Monto presupuestado para una iniciativa',
     2, jsonb_build_object(
         'gist_class', 'Magnitude',
         'gnub_class', 'MontoPresupuestado',
         'unit_scheme', 'currency'
     )),
    ('magnitude_aspect', 'COMMITTED_AMOUNT', 'Monto Comprometido', 'Committed Amount',
     'Monto comprometido via compromiso presupuestario',
     3, jsonb_build_object(
         'gist_class', 'Magnitude',
         'gnub_class', 'MontoComprometido',
         'unit_scheme', 'currency'
     )),
    ('magnitude_aspect', 'EXECUTED_AMOUNT', 'Monto Ejecutado', 'Executed Amount',
     'Monto efectivamente ejecutado/pagado',
     4, jsonb_build_object(
         'gist_class', 'Magnitude',
         'gnub_class', 'MontoEjecutado',
         'unit_scheme', 'currency'
     ))
ON CONFLICT (scheme, code) DO NOTHING;

DO $$
DECLARE
    created_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO created_count
    FROM ref.category
    WHERE scheme = 'magnitude_aspect';
    RAISE NOTICE '  Scheme magnitude_aspect: % valores disponibles', created_count;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 4.2: CREAR SCHEME currency
-- ==============================================================================

BEGIN;

SELECT report_phase('4.2', 'Crear Scheme currency');

-- Verificar si ya existe
DO $$
DECLARE
    existing_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO existing_count
    FROM ref.category
    WHERE scheme = 'currency';

    IF existing_count > 0 THEN
        RAISE NOTICE '  Scheme currency ya existe (% valores)', existing_count;
    ELSE
        RAISE NOTICE '  Scheme currency no existe, creando...';
    END IF;
END $$;

-- Crear scheme currency
-- Ontología: ISO 4217 currency codes
INSERT INTO ref.category (scheme, code, label, label_en, description, sort_order, metadata)
VALUES
    ('currency', 'CLP', 'Peso Chileno', 'Chilean Peso',
     'Moneda oficial de Chile (ISO 4217: CLP)',
     1, jsonb_build_object(
         'iso_4217', 'CLP',
         'numeric_code', 152,
         'symbol', '$',
         'decimal_places', 0
     )),
    ('currency', 'UF', 'Unidad de Fomento', 'Unidad de Fomento',
     'Unidad de cuenta indexada a inflacion chilena',
     2, jsonb_build_object(
         'iso_4217', 'CLF',
         'numeric_code', 990,
         'symbol', 'UF',
         'decimal_places', 4
     )),
    ('currency', 'USD', 'Dolar Estadounidense', 'US Dollar',
     'Moneda oficial de Estados Unidos (ISO 4217: USD)',
     3, jsonb_build_object(
         'iso_4217', 'USD',
         'numeric_code', 840,
         'symbol', 'US$',
         'decimal_places', 2
     ))
ON CONFLICT (scheme, code) DO NOTHING;

DO $$
DECLARE
    created_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO created_count
    FROM ref.category
    WHERE scheme = 'currency';
    RAISE NOTICE '  Scheme currency: % valores disponibles', created_count;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 4.3: MIGRAR monto_transferido → txn.magnitude
-- ==============================================================================

BEGIN;

SELECT report_phase('4.3', 'Migrar monto_transferido a txn.magnitude');

-- 4.3.1 Verificar prerequisitos
DO $$
DECLARE
    v_aspect_id UUID;
    v_unit_id UUID;
BEGIN
    SELECT id INTO v_aspect_id
    FROM ref.category
    WHERE scheme = 'magnitude_aspect' AND code = 'TRANSFER_AMOUNT';

    IF v_aspect_id IS NULL THEN
        RAISE EXCEPTION 'TRANSFER_AMOUNT aspect no existe. Ejecutar Fase 4.1 primero.';
    END IF;
    RAISE NOTICE '  TRANSFER_AMOUNT aspect_id: %', v_aspect_id;

    SELECT id INTO v_unit_id
    FROM ref.category
    WHERE scheme = 'currency' AND code = 'CLP';

    IF v_unit_id IS NULL THEN
        RAISE EXCEPTION 'CLP currency no existe. Ejecutar Fase 4.2 primero.';
    END IF;
    RAISE NOTICE '  CLP unit_id: %', v_unit_id;
END $$;

-- 4.3.2 Migrar datos a txn.magnitude
-- NOTA: txn.magnitude tiene UNIQUE(subject_type, subject_id, aspect_id, as_of_date)
-- Para eventos múltiples del mismo IPR en misma fecha, usar ON CONFLICT DO UPDATE
DO $$
DECLARE
    inserted_count INTEGER;
    v_aspect_id UUID;
    v_unit_id UUID;
BEGIN
    -- Obtener IDs de referencia
    SELECT id INTO v_aspect_id
    FROM ref.category
    WHERE scheme = 'magnitude_aspect' AND code = 'TRANSFER_AMOUNT';

    SELECT id INTO v_unit_id
    FROM ref.category
    WHERE scheme = 'currency' AND code = 'CLP';

    -- Insertar magnitudes desde eventos
    -- Usar subject_id del evento (que es el IPR id)
    -- as_of_date viene de occurred_at del evento
    WITH inserted AS (
        INSERT INTO txn.magnitude (
            subject_type,
            subject_id,
            aspect_id,
            numeric_value,
            unit_id,
            as_of_date
        )
        SELECT DISTINCT ON (
            CASE WHEN e.subject_type = 'rendicion_8pct' THEN 'ipr' ELSE e.subject_type END,
            e.subject_id,
            e.occurred_at::date
        )
            CASE WHEN e.subject_type = 'rendicion_8pct' THEN 'ipr' ELSE e.subject_type END,
            e.subject_id,
            v_aspect_id,
            (e.data->>'monto_transferido')::numeric,
            v_unit_id,
            e.occurred_at::date
        FROM txn.event e
        WHERE e.data ? 'monto_transferido'
          AND (e.data->>'monto_transferido')::numeric > 0
        ORDER BY
            CASE WHEN e.subject_type = 'rendicion_8pct' THEN 'ipr' ELSE e.subject_type END,
            e.subject_id,
            e.occurred_at::date,
            (e.data->>'monto_transferido')::numeric DESC  -- Tomar el mayor si hay duplicados
        ON CONFLICT (subject_type, subject_id, aspect_id, as_of_date)
        DO UPDATE SET
            numeric_value = GREATEST(txn.magnitude.numeric_value, EXCLUDED.numeric_value),
            created_at = now()
        RETURNING id
    )
    SELECT COUNT(*) INTO inserted_count FROM inserted;

    RAISE NOTICE '  % registros insertados/actualizados en txn.magnitude', inserted_count;
END $$;

-- 4.3.3 Verificar migración
DO $$
DECLARE
    source_count INTEGER;
    target_count INTEGER;
    v_aspect_id UUID;
BEGIN
    SELECT COUNT(*) INTO source_count
    FROM txn.event
    WHERE data ? 'monto_transferido'
      AND (data->>'monto_transferido')::numeric > 0;

    SELECT id INTO v_aspect_id
    FROM ref.category
    WHERE scheme = 'magnitude_aspect' AND code = 'TRANSFER_AMOUNT';

    SELECT COUNT(*) INTO target_count
    FROM txn.magnitude
    WHERE aspect_id = v_aspect_id;

    RAISE NOTICE '';
    RAISE NOTICE '  === VERIFICACIÓN MIGRACIÓN ===';
    RAISE NOTICE '  Eventos fuente con monto > 0: %', source_count;
    RAISE NOTICE '  Magnitudes creadas (TRANSFER_AMOUNT): %', target_count;
    RAISE NOTICE '  NOTA: Diferencia es normal por deduplicación (mismo IPR+fecha)';
    RAISE NOTICE '';
END $$;

COMMIT;

-- ==============================================================================
-- FASE 4.4: CORREGIR EVENTOS CON subject_type ANÓMALO
-- ==============================================================================

BEGIN;

SELECT report_phase('4.4', 'Corregir subject_type Anómalo');

-- 4.4.1 Mostrar eventos afectados
DO $$
DECLARE
    anomalous_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO anomalous_count
    FROM txn.event
    WHERE subject_type = 'rendicion_8pct';

    RAISE NOTICE '  Eventos con subject_type=rendicion_8pct: %', anomalous_count;
END $$;

-- 4.4.2 Corregir subject_type
-- Los eventos de 'rendicion_8pct' deberían ser 'ipr' (el subject_id referencia un IPR)
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    WITH updated AS (
        UPDATE txn.event
        SET subject_type = 'ipr'
        WHERE subject_type = 'rendicion_8pct'
        RETURNING id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;

    IF updated_count > 0 THEN
        RAISE NOTICE '  % eventos corregidos: subject_type rendicion_8pct -> ipr', updated_count;
    ELSE
        RAISE NOTICE '  0 eventos necesitaban correccion (ya corregidos)';
    END IF;
END $$;

-- 4.4.3 Verificar corrección
DO $$
DECLARE
    remaining INTEGER;
BEGIN
    SELECT COUNT(*) INTO remaining
    FROM txn.event
    WHERE subject_type = 'rendicion_8pct';

    IF remaining > 0 THEN
        RAISE WARNING '  ADVERTENCIA: Aun quedan % eventos con subject_type anomalo', remaining;
    ELSE
        RAISE NOTICE '  Verificacion: 0 eventos con subject_type anomalo';
    END IF;
END $$;

COMMIT;

-- ==============================================================================
-- FASE 4.5: MARCAR CAMPOS MIGRADOS EN event.data (AUDIT TRAIL)
-- ==============================================================================

BEGIN;

SELECT report_phase('4.5', 'Marcar Campos Migrados (Audit Trail)');

-- 4.5.1 Añadir marca de normalización a eventos migrados
-- NO eliminamos monto_transferido, solo añadimos metadata de normalización
DO $$
DECLARE
    marked_count INTEGER;
BEGIN
    WITH marked AS (
        UPDATE txn.event
        SET data = data || jsonb_build_object(
            'normalized_to_magnitude', true,
            'normalized_at', now()::text,
            'normalized_version', 'v3.0',
            'normalized_fields', ARRAY['monto_transferido']::text[]
        )
        WHERE data ? 'monto_transferido'
          AND (data->>'monto_transferido')::numeric > 0
          AND NOT (data ? 'normalized_to_magnitude')
        RETURNING id
    )
    SELECT COUNT(*) INTO marked_count FROM marked;

    RAISE NOTICE '  % eventos marcados como normalizados', marked_count;
    RAISE NOTICE '  NOTA: monto_transferido PRESERVADO en event.data como audit trail';
END $$;

-- 4.5.2 Documentar campos que pueden ser removidos post-validación
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '  === CAMPOS CANDIDATOS A LIMPIEZA FUTURA ===';
    RAISE NOTICE '  Estos campos YA existen en txn.magnitude (redundantes):';
    RAISE NOTICE '    - monto_transferido (ahora en magnitude.numeric_value)';
    RAISE NOTICE '';
    RAISE NOTICE '  Para eliminar DESPUES de validacion completa:';
    RAISE NOTICE '    UPDATE txn.event';
    RAISE NOTICE '    SET data = data - ''monto_transferido''';
    RAISE NOTICE '    WHERE data ? ''normalized_to_magnitude'';';
    RAISE NOTICE '';
END $$;

COMMIT;

-- ==============================================================================
-- POST-EJECUCIÓN: VERIFICACIONES FINALES
-- ==============================================================================

SELECT report_phase('POST-EJECUCIÓN', 'Verificaciones Finales');

-- Verificación 1: Conteos POST-MIGRACIÓN
DO $$
DECLARE
    event_total INTEGER;
    event_normalized INTEGER;
    event_anomalous INTEGER;
    magnitude_total INTEGER;
    magnitude_transfer INTEGER;
    v_aspect_id UUID;
BEGIN
    SELECT COUNT(*) INTO event_total FROM txn.event;
    SELECT COUNT(*) INTO event_normalized
    FROM txn.event
    WHERE data ? 'normalized_to_magnitude';
    SELECT COUNT(*) INTO event_anomalous
    FROM txn.event
    WHERE subject_type = 'rendicion_8pct';
    SELECT COUNT(*) INTO magnitude_total FROM txn.magnitude;

    SELECT id INTO v_aspect_id
    FROM ref.category
    WHERE scheme = 'magnitude_aspect' AND code = 'TRANSFER_AMOUNT';

    SELECT COUNT(*) INTO magnitude_transfer
    FROM txn.magnitude
    WHERE aspect_id = v_aspect_id;

    RAISE NOTICE '';
    RAISE NOTICE '  === CONTEOS POST-MIGRACIÓN ===';
    RAISE NOTICE '  txn.event total:              %', event_total;
    RAISE NOTICE '  txn.event normalizados:       %', event_normalized;
    RAISE NOTICE '  txn.event anomalos (deben ser 0): %', event_anomalous;
    RAISE NOTICE '  txn.magnitude total:          %', magnitude_total;
    RAISE NOTICE '  txn.magnitude TRANSFER_AMOUNT: %', magnitude_transfer;
    RAISE NOTICE '';
END $$;

-- Verificación 2: Schemes creados
DO $$
DECLARE
    aspect_count INTEGER;
    currency_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO aspect_count
    FROM ref.category
    WHERE scheme = 'magnitude_aspect';
    SELECT COUNT(*) INTO currency_count
    FROM ref.category
    WHERE scheme = 'currency';

    RAISE NOTICE '  === SCHEMES CREADOS ===';
    RAISE NOTICE '  magnitude_aspect: % valores', aspect_count;
    RAISE NOTICE '  currency: % valores', currency_count;
    RAISE NOTICE '';
END $$;

-- Verificación 3: Distribución por fecha en magnitude
DO $$
BEGIN
    RAISE NOTICE '  === DISTRIBUCIÓN POR AÑO (txn.magnitude TRANSFER_AMOUNT) ===';
END $$;

SELECT
    EXTRACT(YEAR FROM m.as_of_date)::integer AS year,
    COUNT(*) AS magnitudes,
    TO_CHAR(SUM(m.numeric_value), 'FM$999,999,999,999') AS total_monto
FROM txn.magnitude m
JOIN ref.category c ON m.aspect_id = c.id
WHERE c.scheme = 'magnitude_aspect' AND c.code = 'TRANSFER_AMOUNT'
GROUP BY EXTRACT(YEAR FROM m.as_of_date)
ORDER BY year;

-- Verificación 4: Integridad de subject_id
DO $$
DECLARE
    orphan_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO orphan_count
    FROM txn.magnitude m
    JOIN ref.category c ON m.aspect_id = c.id
    WHERE c.scheme = 'magnitude_aspect'
      AND c.code = 'TRANSFER_AMOUNT'
      AND m.subject_type = 'ipr'
      AND NOT EXISTS (
          SELECT 1 FROM core.ipr i WHERE i.id = m.subject_id
      );

    IF orphan_count = 0 THEN
        RAISE NOTICE '';
        RAISE NOTICE '  PASS: Todas las magnitudes referencian IPRs válidos';
    ELSE
        RAISE WARNING '';
        RAISE WARNING '  ADVERTENCIA: % magnitudes referencian IPRs inexistentes', orphan_count;
    END IF;
END $$;

-- ==============================================================================
-- REPORTE FINAL
-- ==============================================================================

DO $$ BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '======================================================================';
    RAISE NOTICE '  FASE 4 COMPLETADA: EVENTOS                                        ';
    RAISE NOTICE '======================================================================';
    RAISE NOTICE '';
    RAISE NOTICE '  Patrón aplicado: gist:Magnitude';
    RAISE NOTICE '  Ontología: gnub:MontoTransferido -> magnitude_aspect.TRANSFER_AMOUNT';
    RAISE NOTICE '  Versión: v3.0';
    RAISE NOTICE '';
    RAISE NOTICE '  Acciones ejecutadas:';
    RAISE NOTICE '    1. Scheme magnitude_aspect creado (4 valores)';
    RAISE NOTICE '    2. Scheme currency creado (3 valores: CLP, UF, USD)';
    RAISE NOTICE '    3. monto_transferido migrado a txn.magnitude';
    RAISE NOTICE '    4. subject_type anomalo corregido (rendicion_8pct -> ipr)';
    RAISE NOTICE '    5. Eventos marcados con normalized_to_magnitude flag';
    RAISE NOTICE '';
    RAISE NOTICE '  Backup disponible: temp_event_backup_fase4';
    RAISE NOTICE '';
    RAISE NOTICE '  Próximos pasos:';
    RAISE NOTICE '    1. Validar queries de aplicacion con txn.magnitude';
    RAISE NOTICE '    2. Opcional: Limpiar monto_transferido de event.data';
    RAISE NOTICE '    3. Documentar en ERD (model/model_goreos/docs/GOREOS_ERD_v3.md)';
    RAISE NOTICE '';
END $$;

-- Limpiar función helper
DROP FUNCTION IF EXISTS report_phase(TEXT, TEXT);

-- ==============================================================================
-- FIN FASE 4 - EVENTOS
-- ==============================================================================
