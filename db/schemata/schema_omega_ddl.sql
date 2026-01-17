-- =============================================================================
-- GORE_OS: Deep Semantic Omega v2.6.0 DDL
-- Fecha: 2026-01-05
-- Autor: Arquitecto-GORE
-- Descripción: Esquema relacional para el modelo integrado de datos GORE Ñuble.
--             Soporta jerarquía ontológica IPR -> IDI/PPR y trazabilidad financiera.
-- =============================================================================

-- =============================================================================
-- 0. STAGING (Bronze Layer) - Lossless Raw Data
-- =============================================================================
-- Tablas sin constraints fuertes, todos los campos TEXT para máxima tolerancia.

CREATE SCHEMA IF NOT EXISTS stg;

-- Fuente: IDIS (Iniciativas BIP - IDIs)
CREATE TABLE IF NOT EXISTS stg.stg_idis_raw (
    filename TEXT,
    row_number INT,
    codigo_unico TEXT,
    ano_presupuestario TEXT,
    bip TEXT,
    dv TEXT,
    nombre_iniciativa TEXT,
    subt TEXT,
    item TEXT,
    asig TEXT,
    monto_vigente TEXT,
    estado_actual TEXT,
    fecha_estado_actual TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuente: PROGS (Subvención 8% y Programas)
CREATE TABLE IF NOT EXISTS stg.stg_progs_raw (
    filename TEXT,
    row_number INT,
    codigo_iniciativa TEXT,
    fondo_origen TEXT, -- Ej. "SOCIAL", "DEPORTE"
    rut_institucion TEXT,
    nombre_institucion TEXT,
    comuna TEXT,
    monto_transferido TEXT,
    rendido_fecha TEXT,
    saldo_pendiente TEXT,
    observaciones TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuente: FRIL (FRIL y 31)
CREATE TABLE IF NOT EXISTS stg.stg_fril_raw (
    filename TEXT,
    source_sheet TEXT, -- "31" vs "Fril"
    etapa_sheet TEXT,  -- "Avan. y Adj.", "Lic. y Con."
    codigo TEXT,
    nombre_iniciativa TEXT,
    comuna TEXT,
    unidad_tecnica TEXT,
    estado_iniciativa TEXT,
    sub_estado TEXT,
    saldo_2026 TEXT,
    saldo_2027 TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuente: CONVENIOS
CREATE TABLE IF NOT EXISTS stg.stg_convenios_raw (
    filename TEXT,
    periodo TEXT,
    codigo TEXT,
    sub TEXT, 
    item TEXT,
    asig TEXT,
    nombre_iniciativa TEXT,
    monto TEXT,
    fecha_firma_convenio TEXT,
    nro_res_aprueba TEXT,
    fecha_res_aprueba TEXT,
    estado_convenio TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuente: NUBLE 250 (Cartera Estratégica)
CREATE TABLE IF NOT EXISTS stg.stg_nuble250_raw (
    filename TEXT,
    row_number INT,
    trazo_primario TEXT,
    nombre_iniciativa TEXT,
    division TEXT,
    codigo_bip TEXT,
    comuna TEXT,
    estado_actual TEXT,
    etapa_postulacion TEXT,
    fuente_financiera TEXT,
    monto_estimado TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuente: FUNCIONARIOS (Dotación)
CREATE TABLE IF NOT EXISTS stg.stg_funcionarios_raw (
    filename TEXT,
    row_number INT,
    rut TEXT,
    nombre_completo TEXT,
    estamento TEXT,
    grado TEXT,
    calidad_juridica TEXT,
    unidad_asignada TEXT,
    fecha_ingreso TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuente: MODIFICACIONES (Decretos Presupuestarios)
CREATE TABLE IF NOT EXISTS stg.stg_modificaciones_raw (
    filename TEXT,
    row_number INT,
    nro_decreto TEXT,
    fecha_tramite TEXT,
    moneda TEXT,
    subt TEXT,
    item TEXT,
    asig TEXT,
    denominacion TEXT,
    incremento TEXT,
    disminucion TEXT,
    glosa TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fuente: PARTES (Gestión Documental)
CREATE TABLE IF NOT EXISTS stg.stg_partes_raw (
    filename TEXT,
    row_number INT,
    nro_ingreso TEXT,
    fecha_ingreso TEXT,
    proveniencia TEXT,
    materia TEXT,
    codigo_bip_ref TEXT, -- Extraído o explícito
    observaciones TEXT,
    derivado_a TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 1. CORE INTEGRATED (Silver Layer) - 3NF / Semantic Omega
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS gn;

-- -----------------------------------------------------------------------------
-- 1.1 Entidades de Referencia (Taxonomías Omega)
-- -----------------------------------------------------------------------------

-- DIM_MECANISMO: Implementa gnub:FundingMechanism
-- Define las reglas de juego (Estrategia)
CREATE TABLE gn.gn_ref_mecanismo (
    mecanismo_id VARCHAR(50) PRIMARY KEY, -- 'SNI', 'FRIL', 'C33', '8_PCT', ...
    nombre_mecanismo VARCHAR(100) NOT NULL,
    clase_ipr_admitida VARCHAR(20) CHECK (clase_ipr_admitida IN ('IDI', 'PPR', 'AMBOS')),
    subtitulo_presupuestario CHAR(2) NOT NULL, -- '31', '33', '24'
    requiere_sni BOOLEAN DEFAULT FALSE,
    umbral_utm_max DECIMAL(10,2), -- NULL si no aplica tope
    es_concursable BOOLEAN DEFAULT FALSE
);

-- DIM_FASE: Implementa gnub:IPRPhase
CREATE TABLE gn.gn_ref_fase (
    fase_cod VARCHAR(10) PRIMARY KEY, -- 'F0', 'F1', ...
    nombre_fase VARCHAR(50) NOT NULL,
    descripcion_omega TEXT
);

-- -----------------------------------------------------------------------------
-- 1.2 Entidades Maestras (Dimensiones Conformadas)
-- -----------------------------------------------------------------------------

-- DIM_INSTITUCION: Implementa gnub:ExternalOrganization
CREATE TABLE gn.gn_maestra_institucion (
    institucion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rut_normalizado VARCHAR(20) UNIQUE, -- Format: 12345678-9
    razon_social VARCHAR(255) NOT NULL,
    tipo_institucion VARCHAR(50), -- 'MUNICIPIO', 'OSC', 'SERVICIO_PUBLICO'
    comuna_nombre VARCHAR(100), -- Ref. a Geografía (simplificado por ahora)
    es_vigente BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DIM_FUNCIONARIO: Implementa gnub:GovernmentPerson
CREATE TABLE gn.gn_maestra_funcionario (
    funcionario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rut_normalizado VARCHAR(20) UNIQUE,
    nombre_completo VARCHAR(255),
    estamento VARCHAR(50),
    unidad_organica VARCHAR(100), -- Ref. a futura DIM_UNIDAD
    es_vigente BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DIM_IPR: Superclase Abstracta (gnub:IPR)
-- Centraliza la identidad de todas las intervenciones
CREATE TABLE gn.gn_maestra_ipr (
    ipr_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identidad
    codigo_unico VARCHAR(50) UNIQUE NOT NULL, -- Natural Key (BIP o Interno)
    codigo_bip VARCHAR(20), -- Puede ser NULL para 8%
    nombre_oficial TEXT NOT NULL,
    
    -- Polimorfismo (Subclases)
    clase_ipr VARCHAR(20) NOT NULL CHECK (clase_ipr IN ('IDI', 'PPR', 'ESTUDIO')),
    
    -- Estrategia (Mecanismo)
    mecanismo_id VARCHAR(50) REFERENCES gn.gn_ref_mecanismo(mecanismo_id),
    
    -- Clasificación Presupuestaria
    subt_presupuestario VARCHAR(2),
    item_presupuestario VARCHAR(2), 
    asig_presupuestaria VARCHAR(3),
    
    -- Estado
    fase_actual_cod VARCHAR(10) REFERENCES gn.gn_ref_fase(fase_cod),
    estado_ciclo_vida VARCHAR(50), -- Snapshot del estado actual
    
    -- Relaciones
    unidad_tecnica_id UUID REFERENCES gn.gn_maestra_institucion(institucion_id), -- Quién ejecuta
    
    -- Metadata
    source_system VARCHAR(20), -- 'IDIS', 'PROGS', 'FRIL'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DIM_COMPONENTE_PROGRAMA: Implementa gnub:ProgramComponent
-- Solo aplica cuando clase_ipr = 'PPR'
CREATE TABLE gn.gn_maestra_ipr_componente (
    componente_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID NOT NULL REFERENCES gn.gn_maestra_ipr(ipr_id),
    nombre_componente VARCHAR(255) NOT NULL,
    presupuesto_asignado DECIMAL(18,0) DEFAULT 0,
    CONSTRAINT fk_solo_programas CHECK (true) -- Idealmente trigger para validar clase_ipr='PPR'
);

-- -----------------------------------------------------------------------------
-- 1.3 Entidades Transaccionales (Hechos)
-- -----------------------------------------------------------------------------

-- FACT_MOVIMIENTO_FINANCIERO
-- Trazabilidad de cada peso (Transferencias, Marcos, Rendiciones)
CREATE TABLE gn.gn_fact_movimiento_financiero (
    movimiento_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID NOT NULL REFERENCES gn.gn_maestra_ipr(ipr_id),
    
    fecha_movimiento DATE NOT NULL,
    anio_presupuestario INT NOT NULL,
    
    tipo_movimiento VARCHAR(50) NOT NULL, 
    -- 'MARCO_INICIAL', 'MODIFICACION_MARCO', 'TRANSFERENCIA', 'RENDICION_APROBADA', 'REINTEGRO'
    
    monto_pesos DECIMAL(18,0) NOT NULL,
    
    -- Documento de respaldo
    documento_ref VARCHAR(100), -- N° Resolución, ID Sigfe, etc.
    observaciones TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FACT_HITO_ESTADO
-- Eventos del ciclo de vida (Workflow)
CREATE TABLE gn.gn_fact_hito_estado (
    hito_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID NOT NULL REFERENCES gn.gn_maestra_ipr(ipr_id),
    
    fecha_hito DATE NOT NULL,
    tipo_hito VARCHAR(50) NOT NULL, 
    -- 'RS_OBTENIDO', 'CONVENIO_FIRMADO', 'TOMA_RAZON', 'INICIO_OBRA'
    
    estado_resultante VARCHAR(50),
    documento_respaldo_id UUID, -- FK a tabla de documentos (si se implementa full)
    
    observaciones TEXT
);

-- =============================================================================
-- 2. INDICES & CONSTRAINTS (Performance & Integrity)
-- =============================================================================

CREATE INDEX idx_ipr_codigo ON gn.gn_maestra_ipr(codigo_unico);
CREATE INDEX idx_ipr_mecanismo ON gn.gn_maestra_ipr(mecanismo_id);
CREATE INDEX idx_mov_ipr_fecha ON gn.gn_fact_movimiento_financiero(ipr_id, fecha_movimiento);
CREATE INDEX idx_inst_rut ON gn.gn_maestra_institucion(rut_normalizado);

-- =============================================================================
-- 3. SEED DATA (Datos de Referencia Omega)
-- =============================================================================

INSERT INTO gn.gn_ref_fase (fase_cod, nombre_fase) VALUES
('F0', 'Postulación'),
('F1', 'Admisibilidad'),
('F2', 'Evaluación'),
('F3', 'Priorización'),
('F4', 'Formalización'),
('F5', 'Ejecución'),
('F6', 'Cierre');

INSERT INTO gn.gn_ref_mecanismo (mecanismo_id, nombre_mecanismo, clase_ipr_admitida, subtitulo_presupuestario, requiere_sni, umbral_utm_max, es_concursable) VALUES
('SNI_TRADICIONAL', 'Sistema Nacional de Inversiones', 'IDI', '31', TRUE, NULL, FALSE),
('FRIL', 'Fondo Regional de Iniciativa Local', 'IDI', '33', FALSE, 4545, TRUE), -- Concursable por bolsa comunal
('C33', 'Circular 33 - Expedito', 'IDI', '31', FALSE, NULL, FALSE), -- 'AMBOS' hipoteticamente si incluye ANF
('G06_DIRECTA', 'Glosa 06 Ejecución Directa', 'PPR', '24', FALSE, NULL, FALSE),
('8_PCT', 'Subvención 8% FNDR', 'PPR', '24', FALSE, 500, TRUE), -- Tope variable según linea
('FRPD', 'Fondo Regional Productividad', 'AMBOS', '33', FALSE, NULL, TRUE),
('CONVENIO', 'Convenios de Transferencia', 'IDI', '33', FALSE, NULL, FALSE);
