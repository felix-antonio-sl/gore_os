-- =============================================================================
-- GORE_OS: Silver Layer Transformations
-- Descripción: Poblamiento de tablas Core (gn.*) desde Staging (stg.*)
-- Engine: DuckDB / PostgreSQL Compatible
-- =============================================================================

BEGIN TRANSACTION;

-- -----------------------------------------------------------------------------
-- 1. Normalización de Instituciones
-- -----------------------------------------------------------------------------
-- Estrategia: "Best Effort" deduplication basada en RUT.
-- Se asume que el RUT es la verdad, se limpia formato.

INSERT INTO gn.gn_maestra_institucion (rut_normalizado, razon_social, tipo_institucion)
SELECT DISTINCT
    upper(replace(rut_institucion, '.', '')) as rut_clean,
    upper(trim(nombre_institucion)) as nombre_clean,
    CASE 
        WHEN nombre_institucion ILIKE '%MUNICIP%' THEN 'MUNICIPIO'
        WHEN nombre_institucion ILIKE '%FUNDACION%' OR nombre_institucion ILIKE '%CORPORACION%' THEN 'OSC'
        ELSE 'OTRO'
    END as tipo
FROM stg.stg_progs_raw
WHERE rut_institucion IS NOT NULL
ON CONFLICT (rut_normalizado) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2. Maestra de Funcionarios
-- -----------------------------------------------------------------------------
INSERT INTO gn.gn_maestra_funcionario (rut_normalizado, nombre_completo, estamento, unidad_organica)
SELECT DISTINCT
    upper(replace(rut, '.', '')) as rut_clean,
    upper(trim(nombre_completo)),
    upper(trim(estamento)),
    upper(trim(unidad_asignada))
FROM stg.stg_funcionarios_raw
WHERE rut IS NOT NULL
ON CONFLICT (rut_normalizado) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 3. Unificación de IPRs (Identity Resolution)
-- -----------------------------------------------------------------------------

-- 3.1 Carga de IDIs (Proyectos BIP) -> Clase 'IDI'
INSERT INTO gn.gn_maestra_ipr (
    codigo_unico, 
    codigo_bip, 
    nombre_oficial, 
    clase_ipr, 
    mecanismo_id, 
    subt_presupuestario,
    estado_ciclo_vida,
    source_system
)
SELECT 
    codigo_unico,
    codigo_unico as codigo_bip,
    nombre_iniciativa,
    'IDI' as clase_ipr,
    CASE 
        WHEN subt = '33' THEN 'FRIL'
        ELSE 'SNI_TRADICIONAL'
    END as mecanismo_id,
    subt,
    estado_actual,
    'IDIS'
FROM stg.stg_idis_raw
ON CONFLICT (codigo_unico) DO UPDATE SET 
    nombre_oficial = EXCLUDED.nombre_oficial,
    last_updated = now();

-- 3.2 Carga de Programas (PPR) -> Clase 'PPR'
INSERT INTO gn.gn_maestra_ipr (
    codigo_unico, 
    nombre_oficial, 
    clase_ipr, 
    mecanismo_id, 
    subt_presupuestario,
    source_system
)
SELECT DISTINCT
    codigo_iniciativa,
    'PROGRAMA ' || fondo_origen || ' - ' || nombre_institucion,
    'PPR' as clase_ipr,
    CASE 
        WHEN codigo_iniciativa LIKE '24%' THEN '8_PCT'
        ELSE 'G06_DIRECTA'
    END,
    '24',
    'PROGS'
FROM stg.stg_progs_raw
WHERE codigo_iniciativa IS NOT NULL
ON CONFLICT (codigo_unico) DO NOTHING;

-- 3.3 Carga de Cartera Estratégica (Ñuble 250)
INSERT INTO gn.gn_maestra_ipr (
    codigo_unico, 
    codigo_bip,
    nombre_oficial, 
    clase_ipr, 
    mecanismo_id, 
    estado_ciclo_vida,
    source_system
)
SELECT DISTINCT
    COALESCE(NULLIF(codigo_bip, 'Sin información'), 'N250-' || row_number) as codigo_unico,
    NULLIF(codigo_bip, 'Sin información') as codigo_bip,
    nombre_iniciativa,
    CASE 
        WHEN codigo_bip IS NOT NULL AND codigo_bip != 'Sin información' THEN 'IDI'
        ELSE 'ESTUDIO' 
    END,
    'FRPD' as mecanismo_id,
    estado_actual,
    'NUBLE_250'
FROM stg.stg_nuble250_raw
WHERE nombre_iniciativa IS NOT NULL
ON CONFLICT (codigo_unico) DO UPDATE SET
    mecanismo_id = 'FRPD',
    last_updated = now();

-- 3.4 Carga de FRIL -> Clase 'IDI'
INSERT INTO gn.gn_maestra_ipr (
    codigo_unico, 
    codigo_bip,
    nombre_oficial, 
    clase_ipr, 
    mecanismo_id, 
    subt_presupuestario,
    estado_ciclo_vida,
    source_system
)
SELECT DISTINCT
    codigo as codigo_unico,
    codigo as codigo_bip,
    nombre_iniciativa,
    'IDI' as clase_ipr,
    'FRIL' as mecanismo_id,
    '33' as subt_presupuestario,
    estado_iniciativa,
    'FRIL'
FROM stg.stg_fril_raw
WHERE codigo IS NOT NULL AND nombre_iniciativa IS NOT NULL
ON CONFLICT (codigo_unico) DO UPDATE SET
    last_updated = now();

-- 3.5 Carga de CONVENIOS -> Clase 'IDI'
INSERT INTO gn.gn_maestra_ipr (
    codigo_unico, 
    codigo_bip,
    nombre_oficial, 
    clase_ipr, 
    mecanismo_id, 
    subt_presupuestario,
    estado_ciclo_vida,
    source_system
)
SELECT DISTINCT
    COALESCE(codigo, 'CONV-' || filename || '-' || row_number() OVER ()) as codigo_unico,
    codigo as codigo_bip,
    nombre_iniciativa,
    'IDI' as clase_ipr,
    'CONVENIO' as mecanismo_id,
    CONCAT_WS('.', sub, item, asig) as subt_presupuestario,
    estado_convenio,
    'CONVENIOS'
FROM stg.stg_convenios_raw
WHERE nombre_iniciativa IS NOT NULL
ON CONFLICT (codigo_unico) DO UPDATE SET
    last_updated = now();

-- -----------------------------------------------------------------------------
-- 4. Movimientos Financieros
-- -----------------------------------------------------------------------------

-- 4.1 Marcos Vigentes
INSERT INTO gn.gn_fact_movimiento_financiero (ipr_id, fecha_movimiento, anio_presupuestario, tipo_movimiento, monto_pesos)
SELECT m.ipr_id, CURRENT_DATE, CAST(r.ano_presupuestario AS INT), 'MARCO_VIGENTE', 
    CASE WHEN regexp_replace(r.monto_vigente, '[^0-9-]', '', 'g') IN ('-', '') THEN 0 
    ELSE CAST(regexp_replace(r.monto_vigente, '[^0-9-]', '', 'g') AS DECIMAL) END
FROM stg.stg_idis_raw r JOIN gn.gn_maestra_ipr m ON r.codigo_unico = m.codigo_unico;

-- 4.2 Transferencias Corrientes
INSERT INTO gn.gn_fact_movimiento_financiero (ipr_id, fecha_movimiento, anio_presupuestario, tipo_movimiento, monto_pesos)
SELECT m.ipr_id, CURRENT_DATE, 2025, 'TRANSFERENCIA', 
    CASE WHEN regexp_replace(r.monto_transferido, '[^0-9-]', '', 'g') IN ('-', '') THEN 0 
    ELSE CAST(regexp_replace(r.monto_transferido, '[^0-9-]', '', 'g') AS DECIMAL) END
FROM stg.stg_progs_raw r JOIN gn.gn_maestra_ipr m ON r.codigo_iniciativa = m.codigo_unico
WHERE r.monto_transferido IS NOT NULL;

-- 4.3 FRIL Saldo Programado
INSERT INTO gn.gn_fact_movimiento_financiero (ipr_id, fecha_movimiento, anio_presupuestario, tipo_movimiento, monto_pesos)
SELECT m.ipr_id, CURRENT_DATE, 2026, 'SALDO_PROGRAMADO', 
    CASE WHEN regexp_replace(r.saldo_2026, '[^0-9-]', '', 'g') IN ('-', '') THEN 0 
    ELSE CAST(regexp_replace(r.saldo_2026, '[^0-9-]', '', 'g') AS DECIMAL) END
FROM stg.stg_fril_raw r JOIN gn.gn_maestra_ipr m ON r.codigo = m.codigo_unico
WHERE r.saldo_2026 IS NOT NULL;

-- 4.4 Convenios Monto FNDR
INSERT INTO gn.gn_fact_movimiento_financiero (ipr_id, fecha_movimiento, anio_presupuestario, tipo_movimiento, monto_pesos)
SELECT m.ipr_id, COALESCE(TRY_CAST(r.fecha_firma_convenio AS DATE), CURRENT_DATE), 2025, 'ASIGNACION_FNDR', 
    CASE WHEN regexp_replace(r.monto, '[^0-9-]', '', 'g') IN ('-', '') THEN 0 
    ELSE CAST(regexp_replace(r.monto, '[^0-9-]', '', 'g') AS DECIMAL) END
FROM stg.stg_convenios_raw r JOIN gn.gn_maestra_ipr m ON r.codigo = m.codigo_unico
WHERE r.monto IS NOT NULL;

-- 4.3 Modificaciones Presupuestarias (Decretos)
-- Intento de cruce heurístico por N° Decreto o Glosa (Complejo sin IPR explícita, se carga genérico)
-- Nota: En producción esto requiere inferencia de IPR desde la glosa.
-- Aquí solo cargamos aquellos que logren cruzar por algún ID hipotético (a implementar en refinamiento).

-- -----------------------------------------------------------------------------
-- 5. Gestión Documental (Partes)
-- -----------------------------------------------------------------------------
-- Crear hitos basados en ingresos de partes referenciando BIPs
INSERT INTO gn.gn_fact_hito_estado (ipr_id, fecha_hito, tipo_hito, observaciones)
SELECT 
    m.ipr_id,
    TRY_CAST(p.fecha_ingreso AS DATE), -- Requiere limpieza de fechas en staging
    'INGRESO_DOCUMENTO_PARTES',
    p.materia
FROM stg.stg_partes_raw p
JOIN gn.gn_maestra_ipr m ON p.codigo_bip_ref = m.codigo_bip -- Cruce explícito si existe columna
WHERE p.codigo_bip_ref IS NOT NULL;

COMMIT;
