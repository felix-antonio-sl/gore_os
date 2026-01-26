-- =============================================================================
-- GORE_OS DDL v3.0 - Modelo de Datos Institucional (UUID Universal)
-- =============================================================================
-- GENERADO POR: Arquitecto-GORE + Debate Multiagente (Orquestador-Genérico)
-- FECHA: 2026-01-26
-- TOTAL TABLAS: 50
-- ARQUITECTURA: 4 schemas (meta, ref, core, txn)
-- CAMBIOS v3.0:
--   - UUID universal para todas las PKs
--   - Auditoría completa (created_at, updated_at, created_by_id, updated_by_id)
--   - Soft delete (deleted_at, deleted_by_id)
--   - ref.actor extendido para agentes algorítmicos (KODA)
--   - Particionamiento en txn.event y txn.magnitude
--   - ENUM SQL para tipos fijos
-- ALINEAMIENTO: Gist 14.0, gnub:*, tde:*
-- =============================================================================

-- =============================================================================
-- MAPPING ONTOLOGICO
-- =============================================================================
-- core.ipr <-> gnub:IPR rdfs:subClassOf gist:Project
-- core.ipr (ipr_nature='PROYECTO') <-> gnub:IPRProject
-- core.ipr (ipr_nature='PROGRAMA') <-> gnub:OperationalProgram
-- core.agreement <-> gnub:GOREAgreement rdfs:subClassOf gist:Contract
-- core.resolution <-> gnub:Resolution rdfs:subClassOf gnub:AdministrativeAct
-- core.user <-> extension auth sobre gist:Person
-- core.work_item <-> gist:Task rdfs:subClassOf gist:Event
-- core.work_item_history <-> gist:Event (event sourcing)
-- core.agreement_installment <-> gist:ScheduledEvent
-- txn.event (event_type='CDP') <-> gnub:PreCommitmentEvent
-- txn.event (event_type='COMPROMISO') <-> gnub:CommitmentEvent
-- txn.event (event_type='DEVENGO') <-> gnub:AccrualEvent
-- txn.event (event_type='PAGO') <-> gnub:PaymentEvent
-- core.budget_commitment <-> gnub:BudgetaryCommitment rdfs:subClassOf gist:Commitment
-- ref.category <-> gist:Category pattern
-- ref.actor (agent_type='ALGORITHMIC') <-> koda:Agent
-- =============================================================================

-- =============================================================================
-- EXTENSIONES REQUERIDAS
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- Para gen_random_uuid()

-- =============================================================================
-- TIPOS ENUM (OPP-008)
-- =============================================================================
DROP TYPE IF EXISTS agent_type_enum CASCADE;
CREATE TYPE agent_type_enum AS ENUM ('HUMAN', 'AI', 'ALGORITHMIC', 'ORGANIZATIONAL', 'MACHINE', 'MIXED');

DROP TYPE IF EXISTS ipr_nature_enum CASCADE;
CREATE TYPE ipr_nature_enum AS ENUM ('PROYECTO', 'PROGRAMA');

-- =============================================================================
-- SCHEMAS
-- =============================================================================
CREATE SCHEMA IF NOT EXISTS meta;
CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS txn;

-- =============================================================================
-- CAPA 0: META (5 tablas)
-- Cambia solo con filosofia - Atomos fundamentales MANIFESTO.md
-- =============================================================================

-- TABLA: meta.role
-- EXISTE PORQUE: Atomo fundamental (MANIFESTO.md) + Invariante HAIC (ORKO-I5)
-- ALINEAMIENTO: goreos:Role, orko:P1_Capacidad
-- SEMANTICA: Capacidad = potencial de ejecutar transformacion (Axioma A2)
CREATE TABLE meta.role (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    agent_type agent_type_enum NOT NULL DEFAULT 'HUMAN',
    cognition_level VARCHAR(4),
    human_accountable_id UUID REFERENCES meta.role(id),
    delegation_mode VARCHAR(4),
    ontology_uri TEXT,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID,  -- Se llenará después de crear core.user
    updated_by_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT chk_human_accountable CHECK (agent_type = 'HUMAN' OR human_accountable_id IS NOT NULL)
);
COMMENT ON TABLE meta.role IS 'Rol con soporte HAIC - capacidad de ejecutar transformacion';
COMMENT ON COLUMN meta.role.agent_type IS 'HUMAN|AI|ALGORITHMIC|ORGANIZATIONAL|MACHINE|MIXED (Sustrato)';
COMMENT ON COLUMN meta.role.cognition_level IS 'C0|C1|C2|C3 (Nivel de decision ORKO)';
COMMENT ON COLUMN meta.role.delegation_mode IS 'M1-M6 (modo de delegacion ORKO)';

-- TABLA: meta.process
-- EXISTE PORQUE: Atomo fundamental (MANIFESTO.md)
-- ALINEAMIENTO: goreos:Process
CREATE TABLE meta.process (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    layer VARCHAR(16),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID,
    updated_by_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE meta.process IS 'Proceso - perspectiva dinamica del sistema';
COMMENT ON COLUMN meta.process.layer IS 'STRATEGIC|TACTICAL|OPERATIONAL';

-- TABLA: meta.entity
-- EXISTE PORQUE: Atomo fundamental (MANIFESTO.md)
-- ALINEAMIENTO: goreos:Entity
CREATE TABLE meta.entity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    ontology_uri TEXT,
    domain VARCHAR(16),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID,
    updated_by_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE meta.entity IS 'Entidad del dominio - estructura de informacion';

-- TABLA: meta.story
-- EXISTE PORQUE: Atomo fundamental (MANIFESTO.md) - origen absoluto
-- ALINEAMIENTO: goreos:Story
CREATE TABLE meta.story (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    as_a TEXT NOT NULL,
    i_want TEXT NOT NULL,
    so_that TEXT NOT NULL,
    role_id UUID REFERENCES meta.role(id),
    process_id UUID REFERENCES meta.process(id),
    domain VARCHAR(16),
    priority VARCHAR(4),
    status VARCHAR(16) DEFAULT 'ENRICHED',
    user_description TEXT,
    aspect_id UUID,
    scope_id UUID,
    extra_tags TEXT[],
    acceptance_criteria TEXT[],
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID,
    updated_by_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE meta.story IS 'Historia de usuario - atomo fundamental, origen de todo requerimiento';

-- TABLA: meta.story_entity
-- Relacion N:M Story <-> Entity
CREATE TABLE meta.story_entity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES meta.story(id) NOT NULL,
    entity_id UUID REFERENCES meta.entity(id) NOT NULL,
    status VARCHAR(16),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ,
    UNIQUE(story_id, entity_id)
);
COMMENT ON TABLE meta.story_entity IS 'Relacion N:M entre historias y entidades';

-- =============================================================================
-- CAPA 1: REFERENCE (3 tablas)
-- Vocabularios controlados - Category Pattern (Gist 14.0)
-- =============================================================================

-- TABLA: ref.category
-- EXISTE PORQUE: Category Pattern (Gist 14.0), omega_gore_nuble_mermaid.md
-- ALINEAMIENTO: gist:Category
CREATE TABLE ref.category (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme VARCHAR(32) NOT NULL,
    code VARCHAR(32) NOT NULL,
    label TEXT NOT NULL,
    label_en TEXT,
    description TEXT,
    parent_id UUID REFERENCES ref.category(id),
    parent_code VARCHAR(32),
    -- HIGH-001: Vinculacion Fase->Estado (para estados IPR que pertenecen a una fase MCD)
    phase_id UUID REFERENCES ref.category(id),
    -- MED-004: Transiciones de estado validas (para schemes de estado)
    valid_transitions JSONB,
    sort_order INTEGER,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID,
    updated_by_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(scheme, code)
);
CREATE INDEX idx_category_scheme ON ref.category(scheme);
CREATE INDEX idx_category_phase ON ref.category(phase_id) WHERE phase_id IS NOT NULL;
CREATE INDEX idx_category_deleted ON ref.category(deleted_at) WHERE deleted_at IS NULL;
COMMENT ON TABLE ref.category IS 'Patron Category (Gist 14.0) - 75+ schemes de taxonomias flexibles';
COMMENT ON COLUMN ref.category.phase_id IS 'Para scheme=ipr_state: FK a mcd_phase al que pertenece este estado';
COMMENT ON COLUMN ref.category.valid_transitions IS 'Array JSON de codigos de estado validos como destino';

-- TABLA: ref.actor (HIGH-011: Extendido para agentes algorítmicos)
-- EXISTE PORQUE: dipir_ssot_koda.yaml - 23 actores + agentes KODA
-- ALINEAMIENTO: BPMN actors + koda:Agent
CREATE TABLE ref.actor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    full_name TEXT,

    -- HIGH-011: Discriminador de tipo de actor
    agent_type agent_type_enum NOT NULL DEFAULT 'HUMAN',

    -- Solo para HUMAN
    emoji VARCHAR(8),
    style VARCHAR(100),

    -- Solo para ALGORITHMIC (agentes KODA)
    agent_definition_uri TEXT,  -- 'koda://orquestador-generico/v0.1.0'
    agent_version VARCHAR(16),

    -- Solo para ORGANIZATIONAL
    organization_id UUID,  -- Se llenará FK después de crear core.organization

    -- Común
    is_internal BOOLEAN DEFAULT TRUE,
    sort_order INTEGER,
    notes TEXT,

    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID,
    updated_by_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraint de coherencia (HIGH-011)
    CONSTRAINT chk_actor_type CHECK (
        (agent_type = 'HUMAN' AND agent_definition_uri IS NULL) OR
        (agent_type = 'ALGORITHMIC' AND agent_definition_uri IS NOT NULL) OR
        (agent_type = 'ORGANIZATIONAL') OR
        (agent_type IN ('AI', 'MACHINE', 'MIXED'))
    )
);
CREATE INDEX idx_actor_agent_type ON ref.actor(agent_type);
CREATE INDEX idx_actor_deleted ON ref.actor(deleted_at) WHERE deleted_at IS NULL;
COMMENT ON TABLE ref.actor IS 'Actores en flujos de proceso - humanos, algoritmicos, organizacionales';
COMMENT ON COLUMN ref.actor.agent_type IS 'HUMAN|AI|ALGORITHMIC|ORGANIZATIONAL|MACHINE|MIXED';
COMMENT ON COLUMN ref.actor.agent_definition_uri IS 'URI al YAML/JSON de definicion del agente (koda://...)';

-- TABLA: ref.operational_commitment_type
-- EXISTE PORQUE: casos_uso.md - Catalogo de tipos de compromiso
-- ALINEAMIENTO: gore_ejecucion.tipo_compromiso_operativo (para_titi)
CREATE TABLE ref.operational_commitment_type (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    requires_ipr_link BOOLEAN DEFAULT TRUE,
    default_days INTEGER DEFAULT 7,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID,
    updated_by_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE ref.operational_commitment_type IS 'Tipos de compromiso operativo para gestion';

-- =============================================================================
-- CAPA 2: CORE (40 tablas) - Parte 1: Organización y Personas
-- =============================================================================

-- TABLA: core.organization
CREATE TABLE core.organization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    short_name VARCHAR(32),
    org_type_id UUID REFERENCES ref.category(id),
    parent_id UUID REFERENCES core.organization(id),
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID,
    updated_by_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_organization_deleted ON core.organization(deleted_at) WHERE deleted_at IS NULL;
COMMENT ON TABLE core.organization IS 'Organizacion - Division, Departamento, Unidad';

-- FK diferida para ref.actor.organization_id
ALTER TABLE ref.actor ADD CONSTRAINT fk_actor_organization
    FOREIGN KEY (organization_id) REFERENCES core.organization(id);

-- TABLA: core.person
CREATE TABLE core.person (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rut VARCHAR(12) UNIQUE,
    names TEXT NOT NULL,
    paternal_surname TEXT NOT NULL,
    maternal_surname TEXT,
    email VARCHAR(255),
    phone VARCHAR(20),
    person_type_id UUID REFERENCES ref.category(id),
    organization_id UUID REFERENCES core.organization(id),
    role_id UUID REFERENCES meta.role(id),
    is_active BOOLEAN DEFAULT TRUE,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID,
    updated_by_id UUID,
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_person_rut ON core.person(rut);
CREATE INDEX idx_person_deleted ON core.person(deleted_at) WHERE deleted_at IS NULL;
COMMENT ON TABLE core.person IS 'Persona natural - funcionario, ciudadano, proveedor';

-- TABLA: core.user
CREATE TABLE core.user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES core.person(id),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    system_role_id UUID NOT NULL REFERENCES ref.category(id),
    division_id UUID REFERENCES core.organization(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMPTZ,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_user_email ON core.user(email);
CREATE INDEX idx_user_deleted ON core.user(deleted_at) WHERE deleted_at IS NULL;
COMMENT ON TABLE core.user IS 'Usuario del sistema con credenciales de autenticacion';
COMMENT ON COLUMN core.user.system_role_id IS 'scheme=system_role: ADMIN_SISTEMA|ADMIN_REGIONAL|JEFE_DIVISION|ENCARGADO';

-- Ahora podemos agregar FKs de auditoría a tablas anteriores
ALTER TABLE meta.role ADD CONSTRAINT fk_role_created_by FOREIGN KEY (created_by_id) REFERENCES core.user(id);
ALTER TABLE meta.role ADD CONSTRAINT fk_role_updated_by FOREIGN KEY (updated_by_id) REFERENCES core.user(id);
ALTER TABLE meta.role ADD CONSTRAINT fk_role_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core.user(id);

ALTER TABLE meta.process ADD CONSTRAINT fk_process_created_by FOREIGN KEY (created_by_id) REFERENCES core.user(id);
ALTER TABLE meta.process ADD CONSTRAINT fk_process_updated_by FOREIGN KEY (updated_by_id) REFERENCES core.user(id);
ALTER TABLE meta.process ADD CONSTRAINT fk_process_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core.user(id);

ALTER TABLE meta.entity ADD CONSTRAINT fk_entity_created_by FOREIGN KEY (created_by_id) REFERENCES core.user(id);
ALTER TABLE meta.entity ADD CONSTRAINT fk_entity_updated_by FOREIGN KEY (updated_by_id) REFERENCES core.user(id);
ALTER TABLE meta.entity ADD CONSTRAINT fk_entity_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core.user(id);

ALTER TABLE meta.story ADD CONSTRAINT fk_story_created_by FOREIGN KEY (created_by_id) REFERENCES core.user(id);
ALTER TABLE meta.story ADD CONSTRAINT fk_story_updated_by FOREIGN KEY (updated_by_id) REFERENCES core.user(id);
ALTER TABLE meta.story ADD CONSTRAINT fk_story_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core.user(id);

ALTER TABLE ref.category ADD CONSTRAINT fk_category_created_by FOREIGN KEY (created_by_id) REFERENCES core.user(id);
ALTER TABLE ref.category ADD CONSTRAINT fk_category_updated_by FOREIGN KEY (updated_by_id) REFERENCES core.user(id);
ALTER TABLE ref.category ADD CONSTRAINT fk_category_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core.user(id);

ALTER TABLE ref.actor ADD CONSTRAINT fk_actor_created_by FOREIGN KEY (created_by_id) REFERENCES core.user(id);
ALTER TABLE ref.actor ADD CONSTRAINT fk_actor_updated_by FOREIGN KEY (updated_by_id) REFERENCES core.user(id);
ALTER TABLE ref.actor ADD CONSTRAINT fk_actor_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core.user(id);

ALTER TABLE ref.operational_commitment_type ADD CONSTRAINT fk_oct_created_by FOREIGN KEY (created_by_id) REFERENCES core.user(id);
ALTER TABLE ref.operational_commitment_type ADD CONSTRAINT fk_oct_updated_by FOREIGN KEY (updated_by_id) REFERENCES core.user(id);
ALTER TABLE ref.operational_commitment_type ADD CONSTRAINT fk_oct_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core.user(id);

ALTER TABLE core.organization ADD CONSTRAINT fk_org_created_by FOREIGN KEY (created_by_id) REFERENCES core.user(id);
ALTER TABLE core.organization ADD CONSTRAINT fk_org_updated_by FOREIGN KEY (updated_by_id) REFERENCES core.user(id);
ALTER TABLE core.organization ADD CONSTRAINT fk_org_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core.user(id);

ALTER TABLE core.person ADD CONSTRAINT fk_person_created_by FOREIGN KEY (created_by_id) REFERENCES core.user(id);
ALTER TABLE core.person ADD CONSTRAINT fk_person_updated_by FOREIGN KEY (updated_by_id) REFERENCES core.user(id);
ALTER TABLE core.person ADD CONSTRAINT fk_person_deleted_by FOREIGN KEY (deleted_by_id) REFERENCES core.user(id);

-- =============================================================================
-- CAPA 2: CORE - Parte 2: Territorio
-- =============================================================================

CREATE TABLE core.territory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(16) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    territory_type_id UUID REFERENCES ref.category(id) NOT NULL,
    parent_id UUID REFERENCES core.territory(id),
    population INTEGER,
    area_km2 NUMERIC(12,2),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.territory IS 'Unidad territorial (Region, Provincia, Comuna)';

CREATE TABLE core.territorial_indicator (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    indicator_type_id UUID REFERENCES ref.category(id),
    territory_id UUID REFERENCES core.territory(id),
    fiscal_year INTEGER,
    numeric_value NUMERIC(18,4),
    unit_id UUID REFERENCES ref.category(id),
    source TEXT,
    measured_at DATE,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.territorial_indicator IS 'Indicador socioeconomico o de gestion territorial';

-- =============================================================================
-- CAPA 2: CORE - Parte 3: Planificación
-- =============================================================================

CREATE TABLE core.planning_instrument (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    instrument_type_id UUID REFERENCES ref.category(id),
    valid_from DATE,
    valid_to DATE,
    approved_by UUID REFERENCES core.organization(id),
    parent_instrument_id UUID REFERENCES core.planning_instrument(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.planning_instrument IS 'Instrumento de planificacion (ERD, PROT, ARI)';

-- =============================================================================
-- CAPA 2: CORE - Parte 4: Finanzas y Presupuesto
-- =============================================================================

CREATE TABLE core.budget_program (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) NOT NULL,
    name TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    program_type_id UUID REFERENCES ref.category(id),
    subtitle_id UUID REFERENCES ref.category(id),
    initial_amount NUMERIC(18,2) NOT NULL,
    current_amount NUMERIC(18,2),
    committed_amount NUMERIC(18,2) DEFAULT 0,
    accrued_amount NUMERIC(18,2) DEFAULT 0,
    paid_amount NUMERIC(18,2) DEFAULT 0,
    owner_division_id UUID REFERENCES core.organization(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(code, fiscal_year)
);
CREATE INDEX idx_budget_program_year ON core.budget_program(fiscal_year);
COMMENT ON TABLE core.budget_program IS 'Programa de Presupuesto Publico Regional (PPR)';

CREATE TABLE core.fund_program (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    fund_source_id UUID REFERENCES ref.category(id) NOT NULL,
    fiscal_year INTEGER NOT NULL,
    total_amount NUMERIC(18,2) NOT NULL,
    state_id UUID REFERENCES ref.category(id),
    call_open_date DATE,
    call_close_date DATE,
    resolution_id UUID,  -- FK diferida
    budget_program_id UUID REFERENCES core.budget_program(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.fund_program IS 'Programa especifico financiado por un fondo';

CREATE TABLE core.budget_commitment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commitment_number VARCHAR(32) UNIQUE NOT NULL,
    commitment_type_id UUID REFERENCES ref.category(id),
    budget_program_id UUID REFERENCES core.budget_program(id) NOT NULL,
    ipr_id UUID,  -- FK diferida
    agreement_id UUID,  -- FK diferida
    amount NUMERIC(18,2) NOT NULL,
    issued_at DATE NOT NULL,
    expires_at DATE,
    status_id UUID REFERENCES ref.category(id),
    resolution_id UUID,  -- FK diferida
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    -- OPP-005: CHECK constraint
    CONSTRAINT chk_budget_commitment_amount CHECK (amount > 0)
);
COMMENT ON TABLE core.budget_commitment IS 'Compromiso presupuestario (CDP, Compromiso, Devengado)';

-- =============================================================================
-- CAPA 2: CORE - Parte 5: IPR (Iniciativas de Inversión)
-- =============================================================================

CREATE TABLE core.ipr (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo_bip VARCHAR(20) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    -- OPP-008: Usar ENUM para ipr_nature
    ipr_nature ipr_nature_enum NOT NULL,
    ipr_type_id UUID REFERENCES ref.category(id),
    mcd_phase_id UUID REFERENCES ref.category(id),
    status_id UUID REFERENCES ref.category(id),
    budget_subtitle_id UUID REFERENCES ref.category(id),
    funding_source_id UUID REFERENCES ref.category(id),
    mechanism_id UUID REFERENCES ref.category(id),
    crea_activo BOOLEAN DEFAULT TRUE,
    formulator_id UUID REFERENCES core.organization(id),
    executor_id UUID REFERENCES core.organization(id),
    sponsor_division_id UUID REFERENCES core.organization(id),
    max_execution_months INTEGER,
    intended_outcome TEXT,
    resolution_type_id UUID REFERENCES ref.category(id),
    requires_cgr BOOLEAN DEFAULT FALSE,
    requires_dipres BOOLEAN DEFAULT FALSE,
    has_open_problems BOOLEAN DEFAULT false,
    alert_level_id UUID REFERENCES ref.category(id),
    assignee_id UUID REFERENCES core.user(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_ipr_phase ON core.ipr(mcd_phase_id);
CREATE INDEX idx_ipr_status ON core.ipr(status_id);
CREATE INDEX idx_ipr_mechanism ON core.ipr(mechanism_id);
CREATE INDEX idx_ipr_deleted ON core.ipr(deleted_at) WHERE deleted_at IS NULL;
COMMENT ON TABLE core.ipr IS 'Iniciativa de Inversion Publica Regional - transformacion territorial';
COMMENT ON COLUMN core.ipr.ipr_nature IS 'PROYECTO|PROGRAMA (ENUM)';
COMMENT ON COLUMN core.ipr.mcd_phase_id IS 'scheme=mcd_phase: F0|F1|F2|F3|F4|F5 (6 fases MCD)';
COMMENT ON COLUMN core.ipr.mechanism_id IS 'scheme=mechanism: SNI|C33|FRIL|GLOSA06|TRANSFER|SUBV8|FRPD';

-- HIGH-010: Sin mechanism_type_id redundante
CREATE TABLE core.ipr_mechanism (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID REFERENCES core.ipr(id) NOT NULL UNIQUE,
    -- Atributos SNI
    rate_mdsf VARCHAR(4),
    etapa_bip VARCHAR(16),
    sector VARCHAR(64),
    -- Atributos C33
    categoria_c33 VARCHAR(32),
    vida_util_residual INTEGER,
    informe_tecnico_favorable BOOLEAN,
    cofinanciamiento_anf NUMERIC(5,2),
    -- Atributos FRIL
    tipo_fril VARCHAR(32),
    cumple_norma_5k_utm BOOLEAN,
    res_subdere VARCHAR(32),
    plazo_licitacion_dias INTEGER,
    -- Atributos Glosa06
    fase_eval_central VARCHAR(16),
    rate_ses VARCHAR(4),
    gasto_admin_max NUMERIC(5,2),
    -- Atributos FRPD
    eje_fomento VARCHAR(64),
    nivel_trl INTEGER,
    innovacion_ctci BOOLEAN,
    -- Atributos SUBV8
    fondo_tematico VARCHAR(32),
    puntaje_evaluacion NUMERIC(6,2),
    asignacion_directa BOOLEAN,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.ipr_mechanism IS 'Atributos especificos por mecanismo (el mecanismo se obtiene de core.ipr.mechanism_id)';

-- =============================================================================
-- CONTINUACIÓN EN PARTE 2...
-- =============================================================================
-- Este archivo es muy extenso. Para continuar, se debe agregar:
-- - Actos administrativos y normativa
-- - Convenios y rendiciones
-- - Gobernanza y comités
-- - Inventario y vehículos
-- - Digital y trámites
-- - Control de gestión (problems, commitments, progress)
-- - Trabajo unificado (work_item)
-- - Alertas y riesgos
-- - Capa transaccional (txn.event, txn.magnitude) con particionamiento
-- - Triggers y funciones
-- =============================================================================

-- =============================================================================
-- CAPA 2: CORE - Parte 6: Actos Administrativos y Normativa
-- =============================================================================

CREATE TABLE core.administrative_act (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    act_number VARCHAR(32) NOT NULL,
    act_type_id UUID REFERENCES ref.category(id) NOT NULL,
    subject TEXT NOT NULL,
    issuer_id UUID REFERENCES core.organization(id),
    signer_id UUID REFERENCES meta.role(id),
    issued_at TIMESTAMPTZ NOT NULL,
    effective_from TIMESTAMPTZ,
    effective_to TIMESTAMPTZ,
    state_id UUID REFERENCES ref.category(id),
    requires_cgr BOOLEAN DEFAULT FALSE,
    cgr_outcome_id UUID REFERENCES ref.category(id),
    cgr_submitted_at DATE,
    cgr_resolved_at DATE,
    parent_act_id UUID REFERENCES core.administrative_act(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_admin_act_type ON core.administrative_act(act_type_id);
CREATE INDEX idx_admin_act_state ON core.administrative_act(state_id);
COMMENT ON TABLE core.administrative_act IS 'Acto administrativo - manifestacion de voluntad con efectos juridicos';

CREATE TABLE core.resolution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    administrative_act_id UUID REFERENCES core.administrative_act(id) NOT NULL UNIQUE,
    resolution_type_id UUID REFERENCES ref.category(id) NOT NULL,
    resolution_subtype_id UUID REFERENCES ref.category(id),
    ipr_id UUID REFERENCES core.ipr(id),
    agreement_id UUID,  -- FK diferida
    budget_amount NUMERIC(18,2),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_resolution_ipr ON core.resolution(ipr_id);
COMMENT ON TABLE core.resolution IS 'Resolucion - EXENTA, AFECTA o CONJUNTA';

-- FK diferidas para fund_program y budget_commitment
ALTER TABLE core.fund_program ADD CONSTRAINT fk_fund_program_resolution
    FOREIGN KEY (resolution_id) REFERENCES core.resolution(id);
ALTER TABLE core.budget_commitment ADD CONSTRAINT fk_budget_commitment_resolution
    FOREIGN KEY (resolution_id) REFERENCES core.resolution(id);

CREATE TABLE core.administrative_procedure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    procedure_type_id UUID REFERENCES ref.category(id) NOT NULL,
    name TEXT NOT NULL,
    state_id UUID REFERENCES ref.category(id),
    initiated_at DATE NOT NULL,
    resolved_at DATE,
    initiator_id UUID REFERENCES core.organization(id),
    responsible_id UUID REFERENCES meta.role(id),
    resolution_id UUID REFERENCES core.resolution(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.administrative_procedure IS 'Procedimiento administrativo - secuencia de tramites';

CREATE TABLE core.legal_document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(64) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    doc_type_id UUID REFERENCES ref.category(id),
    publication_date DATE,
    source_url TEXT,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.legal_document IS 'Documento legal (Ley, DFL, Reglamento)';

CREATE TABLE core.legal_mandate (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_document_id UUID REFERENCES core.legal_document(id) NOT NULL,
    article_reference VARCHAR(32),
    mandate_text TEXT NOT NULL,
    applies_to_id UUID REFERENCES ref.category(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.legal_mandate IS 'Mandato legal - constraint institucional derivado de norma';

-- =============================================================================
-- CAPA 2: CORE - Parte 7: Convenios y Rendiciones
-- =============================================================================

CREATE TABLE core.agreement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_number VARCHAR(32),
    agreement_type_id UUID REFERENCES ref.category(id),
    state_id UUID REFERENCES ref.category(id),
    ipr_id UUID REFERENCES core.ipr(id),
    giver_id UUID REFERENCES core.organization(id),
    receiver_id UUID REFERENCES core.organization(id),
    total_amount NUMERIC(18,2),
    signed_at TIMESTAMPTZ,
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_agreement_state ON core.agreement(state_id);
CREATE INDEX idx_agreement_ipr ON core.agreement(ipr_id);
COMMENT ON TABLE core.agreement IS 'Convenio GORE - transferencia, mandato, colaboracion';

-- FK diferidas
ALTER TABLE core.resolution ADD CONSTRAINT fk_resolution_agreement
    FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);
ALTER TABLE core.budget_commitment ADD CONSTRAINT fk_budget_commitment_ipr
    FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);
ALTER TABLE core.budget_commitment ADD CONSTRAINT fk_budget_commitment_agreement
    FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);

CREATE TABLE core.agreement_installment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_id UUID NOT NULL REFERENCES core.agreement(id),
    installment_number INTEGER NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    due_date DATE NOT NULL,
    payment_status_id UUID NOT NULL REFERENCES ref.category(id),
    paid_at TIMESTAMPTZ,
    paid_amount NUMERIC(15,2),
    payment_reference VARCHAR(100),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(agreement_id, installment_number)
);
COMMENT ON TABLE core.agreement_installment IS 'Cuota de pago programada de un convenio';

CREATE TABLE core.rendition (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_id UUID REFERENCES core.agreement(id) NOT NULL,
    renderer_id UUID REFERENCES core.organization(id) NOT NULL,
    state_id UUID REFERENCES ref.category(id),
    period_start DATE,
    period_end DATE,
    submitted_at TIMESTAMPTZ,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.rendition IS 'Rendicion de cuentas de un convenio';

-- =============================================================================
-- CAPA 2: CORE - Parte 8: Gobernanza y Comités
-- =============================================================================

CREATE TABLE core.committee (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    committee_type_id UUID REFERENCES ref.category(id),
    parent_org_id UUID REFERENCES core.organization(id),
    is_permanent BOOLEAN DEFAULT TRUE,
    legal_basis TEXT,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.committee IS 'Organo colegiado de decision (CORE, Comite Inversiones)';

CREATE TABLE core.committee_member (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    committee_id UUID REFERENCES core.committee(id) NOT NULL,
    person_id UUID REFERENCES core.person(id),
    role_in_committee_id UUID REFERENCES ref.category(id),
    start_date DATE NOT NULL,
    end_date DATE,
    is_voting_member BOOLEAN DEFAULT TRUE,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id)
);
COMMENT ON TABLE core.committee_member IS 'Membresia en comite';

CREATE TABLE core.session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    committee_id UUID REFERENCES core.committee(id) NOT NULL,
    session_number INTEGER NOT NULL,
    session_type_id UUID REFERENCES ref.category(id),
    scheduled_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    quorum_reached BOOLEAN,
    location TEXT,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(committee_id, session_number, DATE(scheduled_at))
);
COMMENT ON TABLE core.session IS 'Sesion de un comite u organo colegiado';

CREATE TABLE core.minute (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES core.session(id) NOT NULL UNIQUE,
    minute_number VARCHAR(32) NOT NULL,
    approved_at DATE,
    content TEXT,
    resolution_id UUID REFERENCES core.resolution(id),
    signed_by_id UUID REFERENCES core.person(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.minute IS 'Acta de sesion con acuerdos tomados';

CREATE TABLE core.session_agreement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    minute_id UUID REFERENCES core.minute(id) NOT NULL,
    agreement_number INTEGER NOT NULL,
    subject TEXT NOT NULL,
    decision TEXT NOT NULL,
    responsible_id UUID REFERENCES core.person(id),
    due_date DATE,
    status_id UUID REFERENCES ref.category(id),
    ipr_id UUID REFERENCES core.ipr(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.session_agreement IS 'Acuerdo especifico tomado en una sesion';

-- =============================================================================
-- CAPA 2: CORE - Parte 9: Inventario, Vehículos, Digital
-- =============================================================================

CREATE TABLE core.inventory_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    item_type_id UUID REFERENCES ref.category(id),
    location_id UUID REFERENCES core.organization(id),
    responsible_id UUID REFERENCES core.person(id),
    acquisition_date DATE,
    acquisition_value NUMERIC(18,2),
    current_status_id UUID REFERENCES ref.category(id),
    ipr_origin_id UUID REFERENCES core.ipr(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.inventory_item IS 'Bien mueble o activo del GORE';

CREATE TABLE core.vehicle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_item_id UUID REFERENCES core.inventory_item(id) UNIQUE,
    plate VARCHAR(10) UNIQUE NOT NULL,
    brand VARCHAR(64),
    model VARCHAR(64),
    year INTEGER,
    vehicle_type_id UUID REFERENCES ref.category(id),
    fuel_type_id UUID REFERENCES ref.category(id),
    assigned_division_id UUID REFERENCES core.organization(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.vehicle IS 'Vehiculo institucional';

CREATE TABLE core.digital_platform (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    platform_type_id UUID REFERENCES ref.category(id),
    url TEXT,
    owner_id UUID REFERENCES core.organization(id),
    is_external BOOLEAN DEFAULT FALSE,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.digital_platform IS 'Sistema o plataforma digital (SIGFE, BIP, Portal)';

CREATE TABLE core.procedure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    procedure_type_id UUID REFERENCES ref.category(id),
    responsible_division_id UUID REFERENCES core.organization(id),
    platform_id UUID REFERENCES core.digital_platform(id),
    max_days INTEGER,
    is_online BOOLEAN DEFAULT FALSE,
    legal_basis TEXT,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.procedure IS 'Tramite o servicio ofrecido al ciudadano';

CREATE TABLE core.electronic_file (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_number VARCHAR(32) UNIQUE NOT NULL,
    procedure_id UUID REFERENCES core.procedure(id),
    requester_id UUID REFERENCES core.person(id),
    subject TEXT NOT NULL,
    status_id UUID REFERENCES ref.category(id),
    resolved_at TIMESTAMPTZ,
    resolution_id UUID REFERENCES core.resolution(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.electronic_file IS 'Expediente electronico de un tramite';

CREATE TABLE core.document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(64) UNIQUE,
    name TEXT NOT NULL,
    document_type_id UUID REFERENCES ref.category(id),
    file_id UUID REFERENCES core.electronic_file(id),
    ipr_id UUID REFERENCES core.ipr(id),
    agreement_id UUID REFERENCES core.agreement(id),
    storage_url TEXT,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.document IS 'Documento digital o fisico en el sistema';

-- =============================================================================
-- CAPA 2: CORE - Parte 10: Control de Gestión
-- =============================================================================

CREATE TABLE core.ipr_problem (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE,
    ipr_id UUID REFERENCES core.ipr(id) NOT NULL,
    agreement_id UUID REFERENCES core.agreement(id),
    problem_type_id UUID REFERENCES ref.category(id) NOT NULL,
    impact_id UUID REFERENCES ref.category(id),
    description TEXT NOT NULL,
    impact_description TEXT,
    detected_by_id UUID REFERENCES core.user(id),
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    state_id UUID REFERENCES ref.category(id) NOT NULL,
    proposed_solution TEXT,
    solution_applied TEXT,
    resolved_by_id UUID REFERENCES core.user(id),
    resolved_at TIMESTAMPTZ,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_ipr_problem_state ON core.ipr_problem(state_id);
CREATE INDEX idx_ipr_problem_ipr ON core.ipr_problem(ipr_id);
COMMENT ON TABLE core.ipr_problem IS 'Problema/nudo detectado en una IPR que bloquea avance';

CREATE TABLE core.operational_commitment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE,  -- OPP-006
    session_id UUID REFERENCES core.session(id),
    problem_id UUID REFERENCES core.ipr_problem(id),
    ipr_id UUID REFERENCES core.ipr(id),
    agreement_id UUID REFERENCES core.agreement(id),
    budget_commitment_id UUID REFERENCES core.budget_commitment(id),
    commitment_type_id UUID REFERENCES ref.operational_commitment_type(id) NOT NULL,
    description TEXT NOT NULL,
    responsible_id UUID REFERENCES core.user(id) NOT NULL,
    division_id UUID REFERENCES core.organization(id),
    due_date DATE NOT NULL,
    priority_id UUID REFERENCES ref.category(id),
    state_id UUID REFERENCES ref.category(id) NOT NULL,
    observations TEXT,
    completed_at TIMESTAMPTZ,
    verified_by_id UUID REFERENCES core.user(id),
    verified_at TIMESTAMPTZ,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_commitment_responsible ON core.operational_commitment(responsible_id);
CREATE INDEX idx_commitment_state ON core.operational_commitment(state_id);
CREATE INDEX idx_commitment_due ON core.operational_commitment(due_date);
COMMENT ON TABLE core.operational_commitment IS 'Tarea asignada a un responsable con plazo y seguimiento';

CREATE TABLE core.commitment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commitment_id UUID REFERENCES core.operational_commitment(id) ON DELETE CASCADE NOT NULL,
    previous_state_id UUID REFERENCES ref.category(id),
    new_state_id UUID REFERENCES ref.category(id) NOT NULL,
    changed_by_id UUID REFERENCES core.user(id) NOT NULL,
    comment TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_commitment_history ON core.commitment_history(commitment_id);
COMMENT ON TABLE core.commitment_history IS 'Historial de cambios de estado de compromisos';

CREATE TABLE core.progress_report (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID REFERENCES core.ipr(id) NOT NULL,
    report_number INTEGER NOT NULL,
    report_date DATE NOT NULL,
    physical_progress NUMERIC(5,2),
    financial_progress NUMERIC(5,2),
    description TEXT,
    issues_detected TEXT,
    reported_by_id UUID REFERENCES core.user(id) NOT NULL,
    attachment_url TEXT,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(ipr_id, report_number),
    -- OPP-005: CHECK constraints
    CONSTRAINT chk_physical_progress CHECK (physical_progress IS NULL OR (physical_progress >= 0 AND physical_progress <= 100)),
    CONSTRAINT chk_financial_progress CHECK (financial_progress IS NULL OR (financial_progress >= 0 AND financial_progress <= 100))
);
CREATE INDEX idx_progress_report_ipr ON core.progress_report(ipr_id);
COMMENT ON TABLE core.progress_report IS 'Reporte periodico de avance fisico/financiero de IPR';

CREATE TABLE core.crisis_meeting (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES core.session(id) NOT NULL UNIQUE,
    start_time TIME,
    end_time TIME,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    summary TEXT,
    organizer_id UUID REFERENCES core.user(id),
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.crisis_meeting IS 'Especializacion de session para gestion de crisis IPR';

CREATE TABLE core.agenda_item_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_agreement_id UUID REFERENCES core.session_agreement(id) UNIQUE,
    target_type VARCHAR(20) NOT NULL,
    target_id UUID NOT NULL,
    ipr_id UUID REFERENCES core.ipr(id),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_agenda_context_ipr ON core.agenda_item_context(ipr_id);
COMMENT ON TABLE core.agenda_item_context IS 'Vincula punto de agenda con IPR/problema/alerta';

-- =============================================================================
-- CAPA 2: CORE - Parte 11: Trabajo Unificado
-- =============================================================================

CREATE TABLE core.work_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES core.work_item(id),
    assignee_id UUID NOT NULL REFERENCES core.user(id),
    division_id UUID NOT NULL REFERENCES core.organization(id),
    status_id UUID NOT NULL REFERENCES ref.category(id),
    priority_id UUID REFERENCES ref.category(id),
    origin_id UUID REFERENCES ref.category(id),
    due_date DATE,
    -- HIGH-005: Funtor Story->WorkItem
    story_id UUID REFERENCES meta.story(id),
    -- HIGH-002: FK a operational_commitment
    commitment_id UUID REFERENCES core.operational_commitment(id),
    -- Vinculaciones a entidades formales
    ipr_id UUID REFERENCES core.ipr(id),
    agreement_id UUID REFERENCES core.agreement(id),
    resolution_id UUID REFERENCES core.resolution(id),
    problem_id UUID REFERENCES core.ipr_problem(id),
    -- Contexto proceso DIPIR
    process_ref VARCHAR(100),
    -- Bloqueo
    blocked_by_item_id UUID REFERENCES core.work_item(id),
    blocked_reason TEXT,
    -- Verificacion
    verified_by_id UUID REFERENCES core.user(id),
    verified_at TIMESTAMPTZ,
    -- Timestamps operativos
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID NOT NULL REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    tags TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_work_item_assignee ON core.work_item(assignee_id);
CREATE INDEX idx_work_item_status ON core.work_item(status_id);
CREATE INDEX idx_work_item_due ON core.work_item(due_date);
CREATE INDEX idx_work_item_ipr ON core.work_item(ipr_id);
CREATE INDEX idx_work_item_commitment ON core.work_item(commitment_id);
CREATE INDEX idx_work_item_story ON core.work_item(story_id);
CREATE INDEX idx_work_item_deleted ON core.work_item(deleted_at) WHERE deleted_at IS NULL;
COMMENT ON TABLE core.work_item IS 'Item de trabajo unificado - atomo de gestion operativa';
COMMENT ON COLUMN core.work_item.commitment_id IS 'FK a operational_commitment - trazabilidad compromiso->tarea';

CREATE TABLE core.work_item_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_item_id UUID NOT NULL REFERENCES core.work_item(id),
    event_type_id UUID NOT NULL REFERENCES ref.category(id),
    previous_status_id UUID REFERENCES ref.category(id),
    new_status_id UUID REFERENCES ref.category(id),
    previous_assignee_id UUID REFERENCES core.user(id),
    new_assignee_id UUID REFERENCES core.user(id),
    comment TEXT,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    performed_by_id UUID NOT NULL REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_work_item_history_item ON core.work_item_history(work_item_id);
CREATE INDEX idx_work_item_history_date ON core.work_item_history(occurred_at);
COMMENT ON TABLE core.work_item_history IS 'Historial de cambios de estado y reasignaciones';

-- =============================================================================
-- CAPA 2: CORE - Parte 12: Alertas y Riesgos
-- =============================================================================

CREATE TABLE core.alert (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_type_id UUID REFERENCES ref.category(id) NOT NULL,
    severity_id UUID REFERENCES ref.category(id),
    subject_type VARCHAR(32) NOT NULL,
    subject_id UUID NOT NULL,
    target_type VARCHAR(30),
    target_id UUID,
    message TEXT NOT NULL,
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by_id UUID REFERENCES core.user(id),
    attended_by_id UUID REFERENCES core.user(id),
    attended_at TIMESTAMPTZ,
    action_taken TEXT,
    resolved_at TIMESTAMPTZ,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_alert_subject ON core.alert(subject_type, subject_id);
CREATE INDEX idx_alert_severity ON core.alert(severity_id, triggered_at);
COMMENT ON TABLE core.alert IS 'Alerta del sistema nervioso digital';

CREATE TABLE core.risk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    risk_type_id UUID REFERENCES ref.category(id),
    probability_id UUID REFERENCES ref.category(id),
    impact_id UUID REFERENCES ref.category(id),
    subject_type VARCHAR(32) NOT NULL,
    subject_id UUID NOT NULL,
    mitigation_plan TEXT,
    status_id UUID REFERENCES ref.category(id),
    identified_at DATE,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.risk IS 'Riesgo identificado en un proceso o IPR';

-- =============================================================================
-- CAPA 3: TRANSACTIONAL - Con Particionamiento (OPP-007)
-- =============================================================================

-- TABLA: txn.event (particionada por mes)
CREATE TABLE txn.event (
    id UUID DEFAULT gen_random_uuid(),
    event_type_id UUID REFERENCES ref.category(id) NOT NULL,
    subject_type VARCHAR(32) NOT NULL,
    subject_id UUID NOT NULL,
    actor_id UUID REFERENCES ref.actor(id),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data JSONB DEFAULT '{}'::jsonb,
    -- Auditoría
    created_by_id UUID REFERENCES core.user(id),
    PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

CREATE INDEX idx_event_subject ON txn.event(subject_type, subject_id);
CREATE INDEX idx_event_type ON txn.event(event_type_id);
CREATE INDEX idx_event_occurred ON txn.event(occurred_at);
CREATE INDEX idx_event_actor ON txn.event(actor_id);

-- OPP-006: Constraint UNIQUE para evitar duplicados
-- (No se puede crear UNIQUE global en tablas particionadas, se crea por partición)

COMMENT ON TABLE txn.event IS 'Evento del sistema - Event Sourcing (particionado por mes)';
COMMENT ON COLUMN txn.event.subject_id IS 'UUID del sujeto';
COMMENT ON COLUMN txn.event.actor_id IS 'UUID del actor (humano o algorítmico)';

-- Crear particiones para 2026
CREATE TABLE txn.event_2026_01 PARTITION OF txn.event
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE txn.event_2026_02 PARTITION OF txn.event
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE txn.event_2026_03 PARTITION OF txn.event
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
CREATE TABLE txn.event_2026_04 PARTITION OF txn.event
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');
CREATE TABLE txn.event_2026_05 PARTITION OF txn.event
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
CREATE TABLE txn.event_2026_06 PARTITION OF txn.event
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
CREATE TABLE txn.event_2026_07 PARTITION OF txn.event
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE txn.event_2026_08 PARTITION OF txn.event
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
CREATE TABLE txn.event_2026_09 PARTITION OF txn.event
    FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
CREATE TABLE txn.event_2026_10 PARTITION OF txn.event
    FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
CREATE TABLE txn.event_2026_11 PARTITION OF txn.event
    FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');
CREATE TABLE txn.event_2026_12 PARTITION OF txn.event
    FOR VALUES FROM ('2026-12-01') TO ('2027-01-01');

-- Partición default para fechas fuera de rango
CREATE TABLE txn.event_default PARTITION OF txn.event DEFAULT;

-- TABLA: txn.magnitude (particionada por fecha)
CREATE TABLE txn.magnitude (
    id UUID DEFAULT gen_random_uuid(),
    subject_type VARCHAR(32) NOT NULL,
    subject_id UUID NOT NULL,
    aspect_id UUID REFERENCES ref.category(id) NOT NULL,
    numeric_value NUMERIC(18,2),
    unit_id UUID REFERENCES ref.category(id),
    as_of_date DATE NOT NULL,
    -- Auditoría
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    PRIMARY KEY (id, as_of_date),
    UNIQUE(subject_type, subject_id, aspect_id, as_of_date)
) PARTITION BY RANGE (as_of_date);

CREATE INDEX idx_magnitude_subject ON txn.magnitude(subject_type, subject_id);
CREATE INDEX idx_magnitude_aspect ON txn.magnitude(aspect_id);
CREATE INDEX idx_magnitude_date ON txn.magnitude(as_of_date);

COMMENT ON TABLE txn.magnitude IS 'Magnitude Pattern (Gist 14.0) - particionado por fecha';

-- Particiones para 2026
CREATE TABLE txn.magnitude_2026_q1 PARTITION OF txn.magnitude
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
CREATE TABLE txn.magnitude_2026_q2 PARTITION OF txn.magnitude
    FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
CREATE TABLE txn.magnitude_2026_q3 PARTITION OF txn.magnitude
    FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');
CREATE TABLE txn.magnitude_2026_q4 PARTITION OF txn.magnitude
    FOR VALUES FROM ('2026-10-01') TO ('2027-01-01');
CREATE TABLE txn.magnitude_default PARTITION OF txn.magnitude DEFAULT;

-- =============================================================================
-- VISTA: Mapping Ontológico (gist:Assignment)
-- =============================================================================

CREATE VIEW core.v_work_item_assignment AS
SELECT
    h.id AS assignment_id,
    h.work_item_id AS task_id,
    h.new_assignee_id AS user_id,
    u.person_id AS person_id,
    h.occurred_at AS start_datetime,
    LEAD(h.occurred_at) OVER (PARTITION BY h.work_item_id ORDER BY h.occurred_at) AS end_datetime
FROM core.work_item_history h
LEFT JOIN core.user u ON h.new_assignee_id = u.id
WHERE h.event_type_id IN (
    SELECT id FROM ref.category
    WHERE scheme = 'work_item_event' AND code IN ('CREATED', 'REASSIGNED')
);
COMMENT ON VIEW core.v_work_item_assignment IS 'Vista para exportar asignaciones como gist:Assignment';

-- =============================================================================
-- FUNCIONES Y TRIGGERS (OPP-003)
-- =============================================================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION fn_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_update_timestamp() IS 'Actualiza automaticamente updated_at en UPDATE';

-- Función para validar scheme de category
CREATE OR REPLACE FUNCTION fn_validate_category_scheme(
    p_category_id UUID,
    p_expected_scheme VARCHAR(32)
) RETURNS BOOLEAN AS $$
DECLARE
    v_actual_scheme VARCHAR(32);
BEGIN
    SELECT scheme INTO v_actual_scheme
    FROM ref.category
    WHERE id = p_category_id;

    IF v_actual_scheme IS NULL THEN
        RETURN FALSE;
    END IF;

    RETURN v_actual_scheme = p_expected_scheme;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_validate_category_scheme(UUID, VARCHAR) IS
'Valida que un category_id pertenece al scheme esperado';

-- Crear triggers de updated_at para todas las tablas relevantes
DO $$
DECLARE
    tbl_name TEXT;
    tbl_schema TEXT;
BEGIN
    FOR tbl_schema, tbl_name IN
        SELECT table_schema, table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
        AND table_schema IN ('meta', 'ref', 'core')
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS trg_%s_updated_at ON %I.%I;
            CREATE TRIGGER trg_%s_updated_at
            BEFORE UPDATE ON %I.%I
            FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();
        ', tbl_name, tbl_schema, tbl_name, tbl_name, tbl_schema, tbl_name);
    END LOOP;
END;
$$;

-- =============================================================================
-- FIN DDL v3.0
-- =============================================================================
-- Total: 50 tablas
-- Meta: 5 | Ref: 3 | Core: 40 | Txn: 2 (particionadas)
-- ENUMs: agent_type_enum, ipr_nature_enum
-- Particiones: txn.event (12 mensuales + default), txn.magnitude (4 trimestrales + default)
-- Funciones: fn_update_timestamp, fn_validate_category_scheme
-- Triggers: automáticos para updated_at en todas las tablas
-- =============================================================================

DO $$ BEGIN RAISE NOTICE 'GORE_OS DDL v3.0 COMPLETADO - 50 tablas con UUID universal, auditoría completa, soft delete y particionamiento'; END $$;
