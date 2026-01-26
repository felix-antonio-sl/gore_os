-- =============================================================================
-- GORE_OS DDL v2.0 - Modelo de Datos Institucional
-- =============================================================================
-- GENERADO POR: Arquitecto-GORE (KODA-CARTOGRAPHER + Ontologista Gist)
-- FECHA: 2026-01-26
-- TOTAL TABLAS: 49
-- ARQUITECTURA: 4 schemas (meta, ref, core, txn)
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
-- =============================================================================

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
    id VARCHAR(32) PRIMARY KEY,
    name TEXT NOT NULL,
    agent_type VARCHAR(16) NOT NULL,
    cognition_level VARCHAR(4),
    human_accountable_id VARCHAR(32) REFERENCES meta.role(id),
    delegation_mode VARCHAR(4),
    ontology_uri TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT chk_human_accountable CHECK (agent_type = 'HUMAN' OR human_accountable_id IS NOT NULL)
);
COMMENT ON TABLE meta.role IS 'Rol con soporte HAIC - capacidad de ejecutar transformacion';
COMMENT ON COLUMN meta.role.agent_type IS 'HUMAN|AI|ALGORITHMIC|MACHINE|MIXED (Sustrato)';
COMMENT ON COLUMN meta.role.cognition_level IS 'C0|C1|C2|C3 (Nivel de decision ORKO)';
COMMENT ON COLUMN meta.role.delegation_mode IS 'M1-M6 (modo de delegacion ORKO)';

-- TABLA: meta.process
-- EXISTE PORQUE: Atomo fundamental (MANIFESTO.md)
-- ALINEAMIENTO: goreos:Process
CREATE TABLE meta.process (
    id VARCHAR(32) PRIMARY KEY,
    name TEXT NOT NULL,
    layer VARCHAR(16),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE meta.process IS 'Proceso - perspectiva dinamica del sistema';
COMMENT ON COLUMN meta.process.layer IS 'STRATEGIC|TACTICAL|OPERATIONAL';

-- TABLA: meta.entity
-- EXISTE PORQUE: Atomo fundamental (MANIFESTO.md)
-- ALINEAMIENTO: goreos:Entity
CREATE TABLE meta.entity (
    id VARCHAR(32) PRIMARY KEY,
    name TEXT NOT NULL,
    ontology_uri TEXT,
    domain VARCHAR(16),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE meta.entity IS 'Entidad del dominio - estructura de informacion';

-- TABLA: meta.story
-- EXISTE PORQUE: Atomo fundamental (MANIFESTO.md) - origen absoluto
-- ALINEAMIENTO: goreos:Story
CREATE TABLE meta.story (
    id VARCHAR(32) PRIMARY KEY,
    name TEXT NOT NULL,
    as_a TEXT NOT NULL,
    i_want TEXT NOT NULL,
    so_that TEXT NOT NULL,
    role_id VARCHAR(32) REFERENCES meta.role(id),
    process_id VARCHAR(32) REFERENCES meta.process(id),
    domain VARCHAR(16),
    priority VARCHAR(4),
    status VARCHAR(16) DEFAULT 'ENRICHED',
    user_description TEXT,
    aspect_id INTEGER,
    scope_id INTEGER,
    extra_tags TEXT[],
    acceptance_criteria TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE meta.story IS 'Historia de usuario - atomo fundamental, origen de todo requerimiento';

-- TABLA: meta.story_entity
-- Relacion N:M Story <-> Entity
CREATE TABLE meta.story_entity (
    story_id VARCHAR(32) REFERENCES meta.story(id),
    entity_id VARCHAR(32) REFERENCES meta.entity(id),
    status VARCHAR(16),
    PRIMARY KEY (story_id, entity_id)
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
    id SERIAL PRIMARY KEY,
    scheme VARCHAR(32) NOT NULL,
    code VARCHAR(32) NOT NULL,
    label TEXT NOT NULL,
    label_en TEXT,
    description TEXT,
    parent_id INTEGER REFERENCES ref.category(id),
    sort_order INTEGER,
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(scheme, code)
);
CREATE INDEX idx_category_scheme ON ref.category(scheme);
COMMENT ON TABLE ref.category IS 'Patron Category (Gist 14.0) - 75+ schemes de taxonomias flexibles';

-- TABLA: ref.actor
-- EXISTE PORQUE: dipir_ssot_koda.yaml - 23 actores unicos
-- ALINEAMIENTO: BPMN actors
CREATE TABLE ref.actor (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    full_name TEXT,
    emoji VARCHAR(8),
    style VARCHAR(32),
    is_internal BOOLEAN DEFAULT TRUE,
    notes TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE ref.actor IS 'Actores en flujos de proceso DIPIR (23 actores)';

-- TABLA: ref.operational_commitment_type
-- EXISTE PORQUE: casos_uso.md - Catalogo de tipos de compromiso
-- ALINEAMIENTO: gore_ejecucion.tipo_compromiso_operativo (para_titi)
CREATE TABLE ref.operational_commitment_type (
    id SERIAL PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    requires_ipr_link BOOLEAN DEFAULT TRUE,
    default_days INTEGER DEFAULT 7,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE ref.operational_commitment_type IS 'Tipos de compromiso operativo para gestion';

-- =============================================================================
-- CAPA 2: CORE (39 tablas)
-- Entidades de negocio del GORE
-- =============================================================================

-- -----------------------------------------------------------------------------
-- ORGANIZACION Y PERSONAS
-- -----------------------------------------------------------------------------

-- TABLA: core.organization
-- EXISTE PORQUE: CQ-001 a CQ-028 (Estructura Organizacional)
-- ALINEAMIENTO: gnub:Division, gnub:Department, gist:Organization
CREATE TABLE core.organization (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    short_name VARCHAR(32),
    org_type_id INTEGER REFERENCES ref.category(id),
    parent_id INTEGER REFERENCES core.organization(id),
    valid_from DATE,
    valid_to DATE,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.organization IS 'Organizacion - Division, Departamento, Unidad';

-- TABLA: core.person
-- EXISTE PORQUE: ENT-ORG-FUNCIONARIO - 39 menciones
-- ALINEAMIENTO: gist:Person
CREATE TABLE core.person (
    id SERIAL PRIMARY KEY,
    rut VARCHAR(12) UNIQUE,
    names TEXT NOT NULL,
    paternal_surname TEXT NOT NULL,
    maternal_surname TEXT,
    email VARCHAR(255),
    phone VARCHAR(20),
    person_type_id INTEGER REFERENCES ref.category(id),
    organization_id INTEGER REFERENCES core.organization(id),
    role_id VARCHAR(32) REFERENCES meta.role(id),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_person_rut ON core.person(rut);
COMMENT ON TABLE core.person IS 'Persona natural - funcionario, ciudadano, proveedor';

-- TABLA: core.user (NUEVO - especificaciones.md)
-- EXISTE PORQUE: RF-001, RF-002 (Autenticacion y gestion de usuarios)
-- ALINEAMIENTO: gist:Person + extension auth
-- SEMANTICA: Usuario con credenciales, distinto de Person (datos personales)
CREATE TABLE core.user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id INTEGER NOT NULL REFERENCES core.person(id),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    system_role_id INTEGER NOT NULL REFERENCES ref.category(id),
    division_id INTEGER REFERENCES core.organization(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMPTZ,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.user IS 'Usuario del sistema con credenciales de autenticacion';
COMMENT ON COLUMN core.user.system_role_id IS 'scheme=system_role: ADMIN_SISTEMA|ADMIN_REGIONAL|JEFE_DIVISION|ENCARGADO';

-- -----------------------------------------------------------------------------
-- TERRITORIO
-- -----------------------------------------------------------------------------

-- TABLA: core.territory
-- EXISTE PORQUE: ENT-LOC-REGION, ENT-LOC-COMUNA
-- ALINEAMIENTO: gnub:Territory, gist:GeoRegion
CREATE TABLE core.territory (
    id SERIAL PRIMARY KEY,
    code VARCHAR(16) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    territory_type_id INTEGER REFERENCES ref.category(id) NOT NULL,
    parent_id INTEGER REFERENCES core.territory(id),
    population INTEGER,
    area_km2 NUMERIC(12,2),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.territory IS 'Unidad territorial (Region, Provincia, Comuna)';

-- TABLA: core.territorial_indicator
-- EXISTE PORQUE: ENT-LOC-INDICADOR_TERRITORIAL - 12 menciones
-- ALINEAMIENTO: gnub:TerritorialIndicator
CREATE TABLE core.territorial_indicator (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    indicator_type_id INTEGER REFERENCES ref.category(id),
    territory_id INTEGER REFERENCES core.territory(id),
    fiscal_year INTEGER,
    numeric_value NUMERIC(18,4),
    unit_id INTEGER REFERENCES ref.category(id),
    source TEXT,
    measured_at DATE,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.territorial_indicator IS 'Indicador socioeconomico o de gestion territorial';

-- -----------------------------------------------------------------------------
-- PLANIFICACION
-- -----------------------------------------------------------------------------

-- TABLA: core.planning_instrument
-- EXISTE PORQUE: Funcion Motora 1 (PLANIFICAR)
-- ALINEAMIENTO: gnub:PlanningInstrument, gist:Specification
CREATE TABLE core.planning_instrument (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    instrument_type_id INTEGER REFERENCES ref.category(id),
    valid_from DATE,
    valid_to DATE,
    approved_by INTEGER REFERENCES core.organization(id),
    parent_instrument_id INTEGER REFERENCES core.planning_instrument(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.planning_instrument IS 'Instrumento de planificacion (ERD, PROT, ARI)';

-- -----------------------------------------------------------------------------
-- FINANZAS Y PRESUPUESTO
-- -----------------------------------------------------------------------------

-- TABLA: core.budget_program
-- EXISTE PORQUE: ENT-FIN-PROGRAMA-PPR - 26 menciones
-- ALINEAMIENTO: gnub:BudgetProgram
CREATE TABLE core.budget_program (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    program_type_id INTEGER REFERENCES ref.category(id),
    subtitle_id INTEGER REFERENCES ref.category(id),
    initial_amount NUMERIC(18,2) NOT NULL,
    current_amount NUMERIC(18,2),
    committed_amount NUMERIC(18,2) DEFAULT 0,
    accrued_amount NUMERIC(18,2) DEFAULT 0,
    paid_amount NUMERIC(18,2) DEFAULT 0,
    owner_division_id INTEGER REFERENCES core.organization(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(code, fiscal_year)
);
CREATE INDEX idx_budget_program_year ON core.budget_program(fiscal_year);
COMMENT ON TABLE core.budget_program IS 'Programa de Presupuesto Publico Regional (PPR)';

-- TABLA: core.fund_program
-- EXISTE PORQUE: ENT-EJEC-PROGRAMA-FONDO - 8 menciones
-- ALINEAMIENTO: gnub:FundProgram
CREATE TABLE core.fund_program (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    fund_source_id INTEGER REFERENCES ref.category(id) NOT NULL,
    fiscal_year INTEGER NOT NULL,
    total_amount NUMERIC(18,2) NOT NULL,
    state_id INTEGER REFERENCES ref.category(id),
    call_open_date DATE,
    call_close_date DATE,
    resolution_id INTEGER,
    budget_program_id INTEGER REFERENCES core.budget_program(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.fund_program IS 'Programa especifico financiado por un fondo';

-- TABLA: core.budget_commitment
-- EXISTE PORQUE: ENT-FIN-CDP - 13 menciones
-- ALINEAMIENTO: gnub:BudgetaryCommitment rdfs:subClassOf gist:Commitment
CREATE TABLE core.budget_commitment (
    id SERIAL PRIMARY KEY,
    commitment_number VARCHAR(32) UNIQUE NOT NULL,
    commitment_type_id INTEGER REFERENCES ref.category(id),
    budget_program_id INTEGER REFERENCES core.budget_program(id) NOT NULL,
    ipr_id INTEGER,
    agreement_id INTEGER,
    amount NUMERIC(18,2) NOT NULL,
    issued_at DATE NOT NULL,
    expires_at DATE,
    status_id INTEGER REFERENCES ref.category(id),
    resolution_id INTEGER,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.budget_commitment IS 'Compromiso presupuestario (CDP, Compromiso, Devengado)';

-- -----------------------------------------------------------------------------
-- IPR - INICIATIVAS DE INVERSION PUBLICA REGIONAL
-- -----------------------------------------------------------------------------

-- TABLA: core.ipr
-- EXISTE PORQUE: CQ-029 a CQ-060, 113 historias D-EJEC, omega_gore_nuble_mermaid.md
-- ALINEAMIENTO: gnub:IPR rdfs:subClassOf gist:Project
-- SEMANTICA: IPR es una Transformacion Territorial (Axioma A1: S1 -> S2)
CREATE TABLE core.ipr (
    id SERIAL PRIMARY KEY,
    codigo_bip VARCHAR(20) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    ipr_nature_id INTEGER REFERENCES ref.category(id) NOT NULL,
    ipr_type_id INTEGER REFERENCES ref.category(id),
    mcd_phase_id INTEGER REFERENCES ref.category(id),
    status_id INTEGER REFERENCES ref.category(id),
    budget_subtitle_id INTEGER REFERENCES ref.category(id),
    funding_source_id INTEGER REFERENCES ref.category(id),
    mechanism_id INTEGER REFERENCES ref.category(id),
    crea_activo BOOLEAN DEFAULT TRUE,
    formulator_id INTEGER REFERENCES core.organization(id),
    executor_id INTEGER REFERENCES core.organization(id),
    sponsor_division_id INTEGER REFERENCES core.organization(id),
    max_execution_months INTEGER,
    intended_outcome TEXT,
    resolution_type_id INTEGER REFERENCES ref.category(id),
    requires_cgr BOOLEAN DEFAULT FALSE,
    requires_dipres BOOLEAN DEFAULT FALSE,
    -- Campos operativos (especificaciones.md)
    has_open_problems BOOLEAN DEFAULT false,
    alert_level_id INTEGER REFERENCES ref.category(id),
    assignee_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.ipr IS 'Iniciativa de Inversion Publica Regional - transformacion territorial';
COMMENT ON COLUMN core.ipr.ipr_nature_id IS 'scheme=ipr_nature: PROYECTO|PROGRAMA';
COMMENT ON COLUMN core.ipr.mcd_phase_id IS 'scheme=mcd_phase: F0|F1|F2|F3|F4|F5 (6 fases MCD)';
COMMENT ON COLUMN core.ipr.mechanism_id IS 'scheme=mechanism: SNI|C33|FRIL|GLOSA06|TRANSFER|SUBV8|FRPD (DUAL: postulacion+evaluacion)';

-- TABLA: core.ipr_mechanism
-- EXISTE PORQUE: omega_gore_nuble_mermaid.md - Mecanismos especificos
-- ALINEAMIENTO: Poly-IPR patterns (Polimorfismo por mecanismo)
CREATE TABLE core.ipr_mechanism (
    id SERIAL PRIMARY KEY,
    ipr_id INTEGER REFERENCES core.ipr(id) NOT NULL UNIQUE,
    mechanism_type_id INTEGER REFERENCES ref.category(id) NOT NULL,
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
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.ipr_mechanism IS 'Atributos especificos por mecanismo de evaluacion (7 tracks)';

-- -----------------------------------------------------------------------------
-- ACTOS ADMINISTRATIVOS Y NORMATIVA
-- -----------------------------------------------------------------------------

-- TABLA: core.administrative_act
-- EXISTE PORQUE: ENT-NORM-ACTO-ADMINISTRATIVO
-- ALINEAMIENTO: gnub:AdministrativeAct rdfs:subClassOf gist:Agreement
CREATE TABLE core.administrative_act (
    id SERIAL PRIMARY KEY,
    act_number VARCHAR(32) NOT NULL,
    act_type_id INTEGER REFERENCES ref.category(id) NOT NULL,
    subject TEXT NOT NULL,
    issuer_id INTEGER REFERENCES core.organization(id),
    signer_id VARCHAR(32) REFERENCES meta.role(id),
    issued_at DATE NOT NULL,
    effective_from DATE,
    effective_to DATE,
    state_id INTEGER REFERENCES ref.category(id),
    requires_cgr BOOLEAN DEFAULT FALSE,
    cgr_outcome_id INTEGER REFERENCES ref.category(id),
    cgr_submitted_at DATE,
    cgr_resolved_at DATE,
    parent_act_id INTEGER REFERENCES core.administrative_act(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_admin_act_type ON core.administrative_act(act_type_id);
CREATE INDEX idx_admin_act_state ON core.administrative_act(state_id);
COMMENT ON TABLE core.administrative_act IS 'Acto administrativo - manifestacion de voluntad con efectos juridicos';

-- TABLA: core.resolution
-- EXISTE PORQUE: ENT-NORM-RESOLUCION - 9 menciones
-- ALINEAMIENTO: gnub:Resolution rdfs:subClassOf gnub:AdministrativeAct
CREATE TABLE core.resolution (
    id SERIAL PRIMARY KEY,
    administrative_act_id INTEGER REFERENCES core.administrative_act(id) NOT NULL UNIQUE,
    resolution_type_id INTEGER REFERENCES ref.category(id) NOT NULL,
    resolution_subtype_id INTEGER REFERENCES ref.category(id),
    ipr_id INTEGER REFERENCES core.ipr(id),
    agreement_id INTEGER,
    budget_amount NUMERIC(18,2),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_resolution_ipr ON core.resolution(ipr_id);
COMMENT ON TABLE core.resolution IS 'Resolucion - EXENTA, AFECTA o CONJUNTA';

-- TABLA: core.administrative_procedure
-- EXISTE PORQUE: ENT-NORM-PROCESO - 13 menciones
-- ALINEAMIENTO: gnub:AdministrativeProcedure, gist:Event
CREATE TABLE core.administrative_procedure (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    procedure_type_id INTEGER REFERENCES ref.category(id) NOT NULL,
    name TEXT NOT NULL,
    state_id INTEGER REFERENCES ref.category(id),
    initiated_at DATE NOT NULL,
    resolved_at DATE,
    initiator_id INTEGER REFERENCES core.organization(id),
    responsible_id VARCHAR(32) REFERENCES meta.role(id),
    resolution_id INTEGER REFERENCES core.resolution(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.administrative_procedure IS 'Procedimiento administrativo - secuencia de tramites';

-- TABLA: core.legal_document
-- EXISTE PORQUE: Funcion Motora 5 (NORMAR)
-- ALINEAMIENTO: gnub:LegalDocument, gist:Content
CREATE TABLE core.legal_document (
    id SERIAL PRIMARY KEY,
    code VARCHAR(64) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    doc_type_id INTEGER REFERENCES ref.category(id),
    publication_date DATE,
    source_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.legal_document IS 'Documento legal (Ley, DFL, Reglamento)';

-- TABLA: core.legal_mandate
-- EXISTE PORQUE: gnub:LegalMandate - obligaciones normativas
-- ALINEAMIENTO: gnub:LegalMandate, gist:Requirement
CREATE TABLE core.legal_mandate (
    id SERIAL PRIMARY KEY,
    legal_document_id INTEGER REFERENCES core.legal_document(id) NOT NULL,
    article_reference VARCHAR(32),
    mandate_text TEXT NOT NULL,
    applies_to_id INTEGER REFERENCES ref.category(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.legal_mandate IS 'Mandato legal - constraint institucional derivado de norma';

-- -----------------------------------------------------------------------------
-- CONVENIOS Y RENDICIONES
-- -----------------------------------------------------------------------------

-- TABLA: core.agreement
-- EXISTE PORQUE: CQ-141 a CQ-160 (Convenios)
-- ALINEAMIENTO: gnub:GOREAgreement rdfs:subClassOf gist:Contract
CREATE TABLE core.agreement (
    id SERIAL PRIMARY KEY,
    agreement_number VARCHAR(32),
    agreement_type_id INTEGER REFERENCES ref.category(id),
    state_id INTEGER REFERENCES ref.category(id),
    ipr_id INTEGER REFERENCES core.ipr(id),
    giver_id INTEGER REFERENCES core.organization(id),
    receiver_id INTEGER REFERENCES core.organization(id),
    total_amount NUMERIC(18,2),
    signed_at DATE,
    valid_from DATE,
    valid_to DATE,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.agreement IS 'Convenio GORE - transferencia, mandato, colaboracion';

-- TABLA: core.agreement_installment (NUEVO - especificaciones.md)
-- EXISTE PORQUE: RF-012 (Convenios con cuotas y estado de pago)
-- ALINEAMIENTO: gist:ScheduledEvent
-- SEMANTICA: Cuota de pago programada de un convenio
CREATE TABLE core.agreement_installment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_id INTEGER NOT NULL REFERENCES core.agreement(id),
    installment_number INTEGER NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    due_date DATE NOT NULL,
    payment_status_id INTEGER NOT NULL REFERENCES ref.category(id),
    paid_at TIMESTAMPTZ,
    paid_amount NUMERIC(15,2),
    payment_reference VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(agreement_id, installment_number)
);
COMMENT ON TABLE core.agreement_installment IS 'Cuota de pago programada de un convenio';
COMMENT ON COLUMN core.agreement_installment.payment_status_id IS 'scheme=payment_status: PENDIENTE|EN_PROCESO|PAGADO|DIFERIDO';

-- TABLA: core.rendition
-- EXISTE PORQUE: CQ-183 a CQ-200 (Rendicion)
-- ALINEAMIENTO: gnub:Rendition
CREATE TABLE core.rendition (
    id SERIAL PRIMARY KEY,
    agreement_id INTEGER REFERENCES core.agreement(id) NOT NULL,
    renderer_id INTEGER REFERENCES core.organization(id) NOT NULL,
    state_id INTEGER REFERENCES ref.category(id),
    period_start DATE,
    period_end DATE,
    submitted_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.rendition IS 'Rendicion de cuentas de un convenio';

-- -----------------------------------------------------------------------------
-- GOBERNANZA Y COMITES
-- -----------------------------------------------------------------------------

-- TABLA: core.committee
-- EXISTE PORQUE: ENT-CONV-COMITE - 11 menciones
-- ALINEAMIENTO: gnub:Committee
CREATE TABLE core.committee (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    committee_type_id INTEGER REFERENCES ref.category(id),
    parent_org_id INTEGER REFERENCES core.organization(id),
    is_permanent BOOLEAN DEFAULT TRUE,
    legal_basis TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.committee IS 'Organo colegiado de decision (CORE, Comite Inversiones)';

-- TABLA: core.committee_member
-- EXISTE PORQUE: Composicion de comites
CREATE TABLE core.committee_member (
    id SERIAL PRIMARY KEY,
    committee_id INTEGER REFERENCES core.committee(id) NOT NULL,
    person_id INTEGER REFERENCES core.person(id),
    role_in_committee_id INTEGER REFERENCES ref.category(id),
    start_date DATE NOT NULL,
    end_date DATE,
    is_voting_member BOOLEAN DEFAULT TRUE
);
COMMENT ON TABLE core.committee_member IS 'Membresia en comite';

-- TABLA: core.session
-- EXISTE PORQUE: ENT-CONV-SESION - 8 menciones
-- ALINEAMIENTO: gnub:Session
CREATE TABLE core.session (
    id SERIAL PRIMARY KEY,
    committee_id INTEGER REFERENCES core.committee(id) NOT NULL,
    session_number INTEGER NOT NULL,
    session_type_id INTEGER REFERENCES ref.category(id),
    scheduled_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    quorum_reached BOOLEAN,
    location TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(committee_id, session_number, DATE(scheduled_at))
);
COMMENT ON TABLE core.session IS 'Sesion de un comite u organo colegiado';

-- TABLA: core.minute
-- EXISTE PORQUE: ENT-CONV-ACTA - 11 menciones
-- ALINEAMIENTO: gnub:Minute
CREATE TABLE core.minute (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES core.session(id) NOT NULL UNIQUE,
    minute_number VARCHAR(32) NOT NULL,
    approved_at DATE,
    content TEXT,
    resolution_id INTEGER REFERENCES core.resolution(id),
    signed_by_id INTEGER REFERENCES core.person(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.minute IS 'Acta de sesion con acuerdos tomados';

-- TABLA: core.session_agreement
-- EXISTE PORQUE: ENT-CONV-ACUERDO - 7 menciones
-- ALINEAMIENTO: gnub:SessionAgreement
CREATE TABLE core.session_agreement (
    id SERIAL PRIMARY KEY,
    minute_id INTEGER REFERENCES core.minute(id) NOT NULL,
    agreement_number INTEGER NOT NULL,
    subject TEXT NOT NULL,
    decision TEXT NOT NULL,
    responsible_id INTEGER REFERENCES core.person(id),
    due_date DATE,
    status_id INTEGER REFERENCES ref.category(id),
    ipr_id INTEGER REFERENCES core.ipr(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.session_agreement IS 'Acuerdo especifico tomado en una sesion';

-- -----------------------------------------------------------------------------
-- INVENTARIO Y VEHICULOS
-- -----------------------------------------------------------------------------

-- TABLA: core.inventory_item
-- EXISTE PORQUE: ENT-ORG-INVENTARIO - 10 menciones
-- ALINEAMIENTO: gnub:InventoryItem
CREATE TABLE core.inventory_item (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    item_type_id INTEGER REFERENCES ref.category(id),
    location_id INTEGER REFERENCES core.organization(id),
    responsible_id INTEGER REFERENCES core.person(id),
    acquisition_date DATE,
    acquisition_value NUMERIC(18,2),
    current_status_id INTEGER REFERENCES ref.category(id),
    ipr_origin_id INTEGER REFERENCES core.ipr(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.inventory_item IS 'Bien mueble o activo del GORE';

-- TABLA: core.vehicle
-- EXISTE PORQUE: ENT-ORG-VEHICULO - 6 menciones
-- ALINEAMIENTO: gnub:Vehicle
CREATE TABLE core.vehicle (
    id SERIAL PRIMARY KEY,
    inventory_item_id INTEGER REFERENCES core.inventory_item(id) UNIQUE,
    plate VARCHAR(10) UNIQUE NOT NULL,
    brand VARCHAR(64),
    model VARCHAR(64),
    year INTEGER,
    vehicle_type_id INTEGER REFERENCES ref.category(id),
    fuel_type_id INTEGER REFERENCES ref.category(id),
    assigned_division_id INTEGER REFERENCES core.organization(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.vehicle IS 'Vehiculo institucional';

-- -----------------------------------------------------------------------------
-- DIGITAL Y TRAMITES
-- -----------------------------------------------------------------------------

-- TABLA: core.digital_platform
-- EXISTE PORQUE: ENT-DIG-PLATAFORMA - 17 menciones
-- ALINEAMIENTO: gnub:DigitalPlatform, tde:PlataformaDigital
CREATE TABLE core.digital_platform (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    platform_type_id INTEGER REFERENCES ref.category(id),
    url TEXT,
    owner_id INTEGER REFERENCES core.organization(id),
    is_external BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.digital_platform IS 'Sistema o plataforma digital (SIGFE, BIP, Portal)';

-- TABLA: core.procedure
-- EXISTE PORQUE: ENT-DIG-TRAMITE - 17 menciones
-- ALINEAMIENTO: tde:Tramite
CREATE TABLE core.procedure (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    procedure_type_id INTEGER REFERENCES ref.category(id),
    responsible_division_id INTEGER REFERENCES core.organization(id),
    platform_id INTEGER REFERENCES core.digital_platform(id),
    max_days INTEGER,
    is_online BOOLEAN DEFAULT FALSE,
    legal_basis TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.procedure IS 'Tramite o servicio ofrecido al ciudadano';

-- TABLA: core.electronic_file
-- EXISTE PORQUE: ENT-DIG-EXPEDIENTE - 9 menciones
-- ALINEAMIENTO: tde:ExpedienteElectronico
CREATE TABLE core.electronic_file (
    id SERIAL PRIMARY KEY,
    file_number VARCHAR(32) UNIQUE NOT NULL,
    procedure_id INTEGER REFERENCES core.procedure(id),
    requester_id INTEGER REFERENCES core.person(id),
    subject TEXT NOT NULL,
    status_id INTEGER REFERENCES ref.category(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolution_id INTEGER REFERENCES core.resolution(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.electronic_file IS 'Expediente electronico de un tramite';

-- TABLA: core.document
-- EXISTE PORQUE: ENT-SYS-DOCUMENTO - 14 menciones
-- ALINEAMIENTO: gist:FormattedContent
CREATE TABLE core.document (
    id SERIAL PRIMARY KEY,
    code VARCHAR(64) UNIQUE,
    name TEXT NOT NULL,
    document_type_id INTEGER REFERENCES ref.category(id),
    file_id INTEGER REFERENCES core.electronic_file(id),
    ipr_id INTEGER REFERENCES core.ipr(id),
    agreement_id INTEGER REFERENCES core.agreement(id),
    created_by_id INTEGER REFERENCES core.person(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    storage_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.document IS 'Documento digital o fisico en el sistema';

-- -----------------------------------------------------------------------------
-- CONTROL DE GESTION Y PRODUCTIVIDAD
-- -----------------------------------------------------------------------------

-- TABLA: core.ipr_problem
-- EXISTE PORQUE: casos_uso.md - "Nudos Criticos"
-- ALINEAMIENTO: gore_ejecucion.problema_ipr (para_titi)
CREATE TABLE core.ipr_problem (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE,
    ipr_id INTEGER REFERENCES core.ipr(id) NOT NULL,
    agreement_id INTEGER REFERENCES core.agreement(id),
    problem_type_id INTEGER REFERENCES ref.category(id) NOT NULL,
    impact_id INTEGER REFERENCES ref.category(id),
    description TEXT NOT NULL,
    impact_description TEXT,
    detected_by_id INTEGER REFERENCES core.person(id),
    detected_by_user_id UUID,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    state_id INTEGER REFERENCES ref.category(id) NOT NULL,
    proposed_solution TEXT,
    solution_applied TEXT,
    resolved_by_id INTEGER REFERENCES core.person(id),
    resolved_by_user_id UUID,
    resolved_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_ipr_problem_state ON core.ipr_problem(state_id);
CREATE INDEX idx_ipr_problem_ipr ON core.ipr_problem(ipr_id);
COMMENT ON TABLE core.ipr_problem IS 'Problema/nudo detectado en una IPR que bloquea avance';

-- TABLA: core.operational_commitment
-- EXISTE PORQUE: casos_uso.md - "Compromisos Operativos"
-- ALINEAMIENTO: gore_ejecucion.compromiso_operativo (para_titi)
CREATE TABLE core.operational_commitment (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES core.session(id),
    problem_id INTEGER REFERENCES core.ipr_problem(id),
    ipr_id INTEGER REFERENCES core.ipr(id),
    agreement_id INTEGER REFERENCES core.agreement(id),
    budget_commitment_id INTEGER REFERENCES core.budget_commitment(id),
    commitment_type_id INTEGER REFERENCES ref.operational_commitment_type(id) NOT NULL,
    description TEXT NOT NULL,
    responsible_id INTEGER REFERENCES core.person(id) NOT NULL,
    division_id INTEGER REFERENCES core.organization(id),
    due_date DATE NOT NULL,
    priority_id INTEGER REFERENCES ref.category(id),
    state_id INTEGER REFERENCES ref.category(id) NOT NULL,
    observations TEXT,
    completed_at TIMESTAMPTZ,
    verified_by_id INTEGER REFERENCES core.person(id),
    verified_at TIMESTAMPTZ,
    created_by_id INTEGER REFERENCES core.person(id) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_commitment_responsible ON core.operational_commitment(responsible_id);
CREATE INDEX idx_commitment_state ON core.operational_commitment(state_id);
CREATE INDEX idx_commitment_due ON core.operational_commitment(due_date);
COMMENT ON TABLE core.operational_commitment IS 'Tarea asignada a un responsable con plazo y seguimiento';

-- TABLA: core.commitment_history
-- EXISTE PORQUE: Event sourcing - trazabilidad de compromisos
-- ALINEAMIENTO: gore_ejecucion.historial_compromiso (para_titi)
CREATE TABLE core.commitment_history (
    id SERIAL PRIMARY KEY,
    commitment_id INTEGER REFERENCES core.operational_commitment(id) ON DELETE CASCADE NOT NULL,
    previous_state VARCHAR(20),
    new_state VARCHAR(20) NOT NULL,
    changed_by_id INTEGER REFERENCES core.person(id) NOT NULL,
    comment TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_commitment_history ON core.commitment_history(commitment_id);
COMMENT ON TABLE core.commitment_history IS 'Historial de cambios de estado de compromisos';

-- TABLA: core.progress_report
-- EXISTE PORQUE: casos_uso.md - "Registrar Informe de Avance"
-- ALINEAMIENTO: gore_catalogo.informe_avance (para_titi)
CREATE TABLE core.progress_report (
    id SERIAL PRIMARY KEY,
    ipr_id INTEGER REFERENCES core.ipr(id) NOT NULL,
    report_number INTEGER NOT NULL,
    report_date DATE NOT NULL,
    physical_progress NUMERIC(5,2),
    financial_progress NUMERIC(5,2),
    description TEXT,
    issues_detected TEXT,
    reported_by_id INTEGER REFERENCES core.person(id) NOT NULL,
    attachment_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(ipr_id, report_number)
);
CREATE INDEX idx_progress_report_ipr ON core.progress_report(ipr_id);
COMMENT ON TABLE core.progress_report IS 'Reporte periodico de avance fisico/financiero de IPR';

-- TABLA: core.crisis_meeting
-- EXISTE PORQUE: casos_uso.md - Reuniones de crisis semanales
-- ALINEAMIENTO: gore_instancias.reunion_crisis (para_titi)
CREATE TABLE core.crisis_meeting (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES core.session(id) NOT NULL UNIQUE,
    start_time TIME,
    end_time TIME,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    summary TEXT,
    organizer_id INTEGER REFERENCES core.person(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.crisis_meeting IS 'Especializacion de session para gestion de crisis IPR';

-- TABLA: core.agenda_item_context
-- EXISTE PORQUE: casos_uso.md - Contexto de crisis en puntos de agenda
-- ALINEAMIENTO: gore_instancias.contexto_punto_crisis (para_titi)
CREATE TABLE core.agenda_item_context (
    id SERIAL PRIMARY KEY,
    session_agreement_id INTEGER REFERENCES core.session_agreement(id) UNIQUE,
    target_type VARCHAR(20) NOT NULL,
    target_id INTEGER NOT NULL,
    ipr_id INTEGER REFERENCES core.ipr(id),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_agenda_context_ipr ON core.agenda_item_context(ipr_id);
COMMENT ON TABLE core.agenda_item_context IS 'Vincula punto de agenda con IPR/problema/alerta';

-- -----------------------------------------------------------------------------
-- TRABAJO UNIFICADO (NUEVO - especificaciones.md)
-- -----------------------------------------------------------------------------

-- TABLA: core.work_item
-- EXISTE PORQUE: RF-020 a RF-030 (Modulo de Trabajo Unificado)
-- ALINEAMIENTO: gist:Task rdfs:subClassOf gist:Event
-- SEMANTICA: Unidad de trabajo asignable, con estado y jerarquia
CREATE TABLE core.work_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES core.work_item(id),
    assignee_id UUID NOT NULL REFERENCES core.user(id),
    division_id INTEGER NOT NULL REFERENCES core.organization(id),
    status_id INTEGER NOT NULL REFERENCES ref.category(id),
    priority_id INTEGER REFERENCES ref.category(id),
    origin_id INTEGER REFERENCES ref.category(id),
    due_date DATE,
    -- Vinculaciones a entidades formales
    ipr_id INTEGER REFERENCES core.ipr(id),
    agreement_id INTEGER REFERENCES core.agreement(id),
    resolution_id INTEGER REFERENCES core.resolution(id),
    problem_id INTEGER REFERENCES core.ipr_problem(id),
    -- Contexto proceso DIPIR
    process_ref VARCHAR(100),
    -- Bloqueo
    blocked_by_item_id UUID REFERENCES core.work_item(id),
    blocked_reason TEXT,
    -- Verificacion
    verified_by_id UUID REFERENCES core.user(id),
    verified_at TIMESTAMPTZ,
    -- Timestamps
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID NOT NULL REFERENCES core.user(id),
    tags TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_work_item_assignee ON core.work_item(assignee_id);
CREATE INDEX idx_work_item_status ON core.work_item(status_id);
CREATE INDEX idx_work_item_due ON core.work_item(due_date);
CREATE INDEX idx_work_item_ipr ON core.work_item(ipr_id);
COMMENT ON TABLE core.work_item IS 'Item de trabajo unificado - atomo de gestion operativa';
COMMENT ON COLUMN core.work_item.code IS 'Codigo unico: IT-YYYY-NNNNN';
COMMENT ON COLUMN core.work_item.status_id IS 'scheme=work_item_status: PENDIENTE|EN_PROGRESO|BLOQUEADO|COMPLETADO|VERIFICADO|CANCELADO';

-- TABLA: core.work_item_history
-- EXISTE PORQUE: RF-030 (Historial de Item)
-- ALINEAMIENTO: gist:Event (registro de cambio de estado)
-- SEMANTICA: Auditoria de cambios en work_item
CREATE TABLE core.work_item_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_item_id UUID NOT NULL REFERENCES core.work_item(id),
    event_type_id INTEGER NOT NULL REFERENCES ref.category(id),
    previous_status_id INTEGER REFERENCES ref.category(id),
    new_status_id INTEGER REFERENCES ref.category(id),
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
COMMENT ON COLUMN core.work_item_history.event_type_id IS 'scheme=work_item_event: CREATED|STATUS_CHANGE|REASSIGNED|BLOCKED|UNBLOCKED|VERIFIED|COMMENT';

-- -----------------------------------------------------------------------------
-- ALERTAS Y RIESGOS
-- -----------------------------------------------------------------------------

-- TABLA: core.alert
-- EXISTE PORQUE: ENT-SAL-ALERTA - 39 menciones
-- ALINEAMIENTO: gnub:Alert
CREATE TABLE core.alert (
    id SERIAL PRIMARY KEY,
    alert_type_id INTEGER REFERENCES ref.category(id) NOT NULL,
    severity_id INTEGER REFERENCES ref.category(id),
    subject_type VARCHAR(32) NOT NULL,
    subject_id INTEGER NOT NULL,
    -- Campos polimorficos (especificaciones.md)
    target_type VARCHAR(30),
    target_id UUID,
    message TEXT NOT NULL,
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by_id INTEGER REFERENCES core.person(id),
    -- Campos atencion (especificaciones.md)
    attended_by_id UUID,
    attended_at TIMESTAMPTZ,
    action_taken TEXT,
    resolved_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_alert_subject ON core.alert(subject_type, subject_id);
CREATE INDEX idx_alert_severity ON core.alert(severity_id, triggered_at);
COMMENT ON TABLE core.alert IS 'Alerta del sistema nervioso digital (SDA: Sense)';
COMMENT ON COLUMN core.alert.target_type IS 'IPR|CONVENIO|RESOLUCION|ITEM|PROBLEMA';

-- TABLA: core.risk
-- EXISTE PORQUE: ENT-SAL-RIESGO - 16 menciones
-- ALINEAMIENTO: gnub:Risk
CREATE TABLE core.risk (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    risk_type_id INTEGER REFERENCES ref.category(id),
    probability_id INTEGER REFERENCES ref.category(id),
    impact_id INTEGER REFERENCES ref.category(id),
    subject_type VARCHAR(32) NOT NULL,
    subject_id INTEGER NOT NULL,
    mitigation_plan TEXT,
    status_id INTEGER REFERENCES ref.category(id),
    identified_at DATE,
    metadata JSONB DEFAULT '{}'::jsonb
);
COMMENT ON TABLE core.risk IS 'Riesgo identificado en un proceso o IPR';

-- =============================================================================
-- CAPA 3: TRANSACTIONAL (2 tablas)
-- Eventos y mediciones - Event Sourcing
-- =============================================================================

-- TABLA: txn.event
-- EXISTE PORQUE: dipir:VisacionEvent, gnub:BudgetaryTransaction
-- ALINEAMIENTO: gist:Event
CREATE TABLE txn.event (
    id BIGSERIAL PRIMARY KEY,
    event_type_id INTEGER REFERENCES ref.category(id) NOT NULL,
    subject_type VARCHAR(32) NOT NULL,
    subject_id INTEGER NOT NULL,
    actor_id INTEGER,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX idx_event_subject ON txn.event(subject_type, subject_id);
CREATE INDEX idx_event_type ON txn.event(event_type_id);
CREATE INDEX idx_event_occurred ON txn.event(occurred_at);
COMMENT ON TABLE txn.event IS 'Evento del sistema - Event Sourcing';
COMMENT ON COLUMN txn.event.event_type_id IS 'scheme=event_type: CDP|COMPROMISO|DEVENGO|PAGO|VISACION|STATE_TRANSITION|etc.';

-- TABLA: txn.magnitude
-- EXISTE PORQUE: Magnitude Pattern (Gist 14.0)
-- ALINEAMIENTO: gist:Magnitude
CREATE TABLE txn.magnitude (
    id BIGSERIAL PRIMARY KEY,
    subject_type VARCHAR(32) NOT NULL,
    subject_id INTEGER NOT NULL,
    aspect_id INTEGER REFERENCES ref.category(id) NOT NULL,
    numeric_value NUMERIC(18,2),
    unit_id INTEGER REFERENCES ref.category(id),
    as_of_date DATE NOT NULL,
    UNIQUE(subject_type, subject_id, aspect_id, as_of_date)
);
CREATE INDEX idx_magnitude_subject ON txn.magnitude(subject_type, subject_id);
COMMENT ON TABLE txn.magnitude IS 'Magnitude Pattern (Gist 14.0) - mediciones con unidad y aspecto';
COMMENT ON COLUMN txn.magnitude.aspect_id IS 'scheme=aspect: BUDGETED_AMOUNT|CURRENT_BUDGET|PRE_COMMITTED|COMMITTED|ACCRUED|PAID|AVAILABLE_BALANCE|etc.';

-- =============================================================================
-- FOREIGN KEYS DIFERIDAS (referencias circulares)
-- =============================================================================

-- FK diferidas para core.ipr
ALTER TABLE core.ipr ADD CONSTRAINT fk_ipr_assignee
    FOREIGN KEY (assignee_id) REFERENCES core.user(id);

-- FK diferidas para core.fund_program
ALTER TABLE core.fund_program ADD CONSTRAINT fk_fund_program_resolution
    FOREIGN KEY (resolution_id) REFERENCES core.resolution(id);

-- FK diferidas para core.budget_commitment
ALTER TABLE core.budget_commitment ADD CONSTRAINT fk_budget_commitment_ipr
    FOREIGN KEY (ipr_id) REFERENCES core.ipr(id);
ALTER TABLE core.budget_commitment ADD CONSTRAINT fk_budget_commitment_agreement
    FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);
ALTER TABLE core.budget_commitment ADD CONSTRAINT fk_budget_commitment_resolution
    FOREIGN KEY (resolution_id) REFERENCES core.resolution(id);

-- FK diferidas para core.resolution
ALTER TABLE core.resolution ADD CONSTRAINT fk_resolution_agreement
    FOREIGN KEY (agreement_id) REFERENCES core.agreement(id);

-- FK diferidas para core.ipr_problem
ALTER TABLE core.ipr_problem ADD CONSTRAINT fk_ipr_problem_detected_by_user
    FOREIGN KEY (detected_by_user_id) REFERENCES core.user(id);
ALTER TABLE core.ipr_problem ADD CONSTRAINT fk_ipr_problem_resolved_by_user
    FOREIGN KEY (resolved_by_user_id) REFERENCES core.user(id);

-- FK diferidas para core.alert
ALTER TABLE core.alert ADD CONSTRAINT fk_alert_attended_by
    FOREIGN KEY (attended_by_id) REFERENCES core.user(id);

-- =============================================================================
-- VISTA PARA MAPPING ONTOLOGICO (gist:Assignment)
-- =============================================================================

CREATE VIEW core.v_work_item_assignment AS
SELECT
    h.id AS assignment_id,
    h.work_item_id AS task_id,
    h.new_assignee_id AS person_id,
    h.occurred_at AS start_datetime,
    LEAD(h.occurred_at) OVER (PARTITION BY h.work_item_id ORDER BY h.occurred_at) AS end_datetime
FROM core.work_item_history h
WHERE h.event_type_id IN (
    SELECT id FROM ref.category
    WHERE scheme = 'work_item_event' AND code IN ('CREATED', 'REASSIGNED')
);
COMMENT ON VIEW core.v_work_item_assignment IS 'Vista para exportar asignaciones como gist:Assignment';

-- =============================================================================
-- FIN DDL
-- =============================================================================
-- Total: 49 tablas
-- Meta: 5 | Ref: 3 | Core: 39 | Txn: 2
-- =============================================================================
