-- =============================================================================
-- GORE_OS v3.0 - SEED DATA: Agentes Algorítmicos (KODA)
-- =============================================================================
-- Archivo: goreos_seed_agents.sql
-- Descripción: Datos iniciales para agentes algorítmicos en ref.actor
-- Generado: 2026-01-26
-- Dependencias: goreos_ddl_v3.sql, goreos_seed.sql (debe ejecutarse después)
-- =============================================================================

-- =============================================================================
-- AGENTES ALGORÍTMICOS (KODA Framework)
-- =============================================================================
-- Estos actores representan agentes de IA/automatización que participan
-- en procesos del GORE. Cada uno tiene una definición YAML asociada.
-- =============================================================================

INSERT INTO ref.actor (
    code, name, full_name, agent_type,
    agent_definition_uri, agent_version,
    is_internal, sort_order, notes
) VALUES
-- Orquestador Genérico
(
    'ORQUESTADOR_GENERICO',
    'Orquestador',
    'Agente Orquestador Genérico KODA',
    'ALGORITHMIC',
    'koda://orquestador-generico/v0.1.0',
    'v0.1.0',
    TRUE,
    100,
    'Coordinador multi-agente de segundo orden. Gestiona colaboraciones entre especialistas. Protocolos: SECUENCIAL, PARALELO, DINAMICO, CONSENSO.'
),
-- Ingeniero GOREOS
(
    'INGENIERO_GOREOS',
    'Ingeniero GOREOS',
    'Agente Ingeniero GORE_OS',
    'ALGORITHMIC',
    'koda://ingeniero-goreos/v0.1.0',
    'v0.1.0',
    TRUE,
    101,
    'Ingeniero de software especializado en GORE_OS. Pipeline Dominio→Blueprint→Sistema→Código. Stack: Python 3.11+, Flask, SQLAlchemy, HTMX, PostgreSQL.'
),
-- Ontologista Gist
(
    'ONTOLOGISTA_GIST',
    'Ontologista',
    'Agente Ontologista Gist 14.0',
    'ALGORITHMIC',
    'koda://ontologista-gist/v0.1.0',
    'v0.1.0',
    TRUE,
    102,
    'Ontólogo especializado en Gist 14.0. Pensador dialéctico-generativo. Navega tensiones ontológicas como adjunciones (L⊣R). ~100 clases/propiedades core.'
),
-- Arquitecto Categórico
(
    'ARQUITECTO_CATEGORICO',
    'Arq. Categórico',
    'Agente Arquitecto Categórico',
    'ALGORITHMIC',
    'koda://arquitecto-categorico/v0.1.0',
    'v0.1.0',
    TRUE,
    103,
    'Arquitecto de datos basado en Teoría de Categorías. Genera: SQL, GraphQL, JSON Schema, OpenAPI. Modelo DIK: DATA, INFORMATION, KNOWLEDGE.'
),
-- Auditor de Código
(
    'AUDITOR_CODIGO',
    'Auditor',
    'Agente Auditor de Código y Modelos',
    'ALGORITHMIC',
    'koda://auditor-codigo/v0.1.0',
    'v0.1.0',
    TRUE,
    104,
    'Auditor de calidad de código y modelos. Detecta anti-patrones, inconsistencias y vulnerabilidades. Genera reportes de auditoría.'
),
-- Cartógrafo de Dominio
(
    'CARTOGRAFO_DOMINIO',
    'Cartógrafo',
    'Agente Cartógrafo de Dominio',
    'ALGORITHMIC',
    'koda://cartografo-dominio/v0.1.0',
    'v0.1.0',
    TRUE,
    105,
    'Explora y mapea dominios de conocimiento. Genera ontologías, diagramas de entidad-relación y documentación técnica.'
)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    full_name = EXCLUDED.full_name,
    agent_type = EXCLUDED.agent_type,
    agent_definition_uri = EXCLUDED.agent_definition_uri,
    agent_version = EXCLUDED.agent_version,
    is_internal = EXCLUDED.is_internal,
    sort_order = EXCLUDED.sort_order,
    notes = EXCLUDED.notes;

-- =============================================================================
-- ROLES META PARA AGENTES ALGORÍTMICOS
-- =============================================================================
-- Cada agente algorítmico tiene un rol asociado en meta.role
-- =============================================================================

INSERT INTO meta.role (
    code, name, agent_type, cognition_level, delegation_mode, ontology_uri
) VALUES
(
    'ROLE_ORQUESTADOR',
    'Rol Orquestador Multi-Agente',
    'ALGORITHMIC',
    'C3',  -- Nivel más alto: decide sobre otros agentes
    'M6',  -- Delegación completa
    'koda://roles/orquestador'
),
(
    'ROLE_INGENIERO',
    'Rol Ingeniero de Software',
    'ALGORITHMIC',
    'C2',  -- Decisiones técnicas
    'M4',  -- Delegación supervisada
    'koda://roles/ingeniero'
),
(
    'ROLE_ONTOLOGISTA',
    'Rol Especialista Ontológico',
    'ALGORITHMIC',
    'C2',
    'M4',
    'koda://roles/ontologista'
),
(
    'ROLE_ARQUITECTO',
    'Rol Arquitecto de Datos',
    'ALGORITHMIC',
    'C2',
    'M4',
    'koda://roles/arquitecto'
),
(
    'ROLE_AUDITOR',
    'Rol Auditor de Calidad',
    'ALGORITHMIC',
    'C1',  -- Ejecución de reglas
    'M3',
    'koda://roles/auditor'
)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    agent_type = EXCLUDED.agent_type,
    cognition_level = EXCLUDED.cognition_level,
    delegation_mode = EXCLUDED.delegation_mode,
    ontology_uri = EXCLUDED.ontology_uri;

-- =============================================================================
-- TIPOS DE EVENTO PARA AGENTES
-- =============================================================================

INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('event_type', 'AGENT_INVOKED', 'Agente Invocado', 'Un agente algorítmico fue invocado', 50),
('event_type', 'AGENT_COMPLETED', 'Agente Completado', 'Un agente algorítmico completó su tarea', 51),
('event_type', 'AGENT_ERROR', 'Error de Agente', 'Un agente algorítmico reportó un error', 52),
('event_type', 'DEBATE_STARTED', 'Debate Iniciado', 'Se inició un debate multiagente', 53),
('event_type', 'DEBATE_CONCLUDED', 'Debate Concluido', 'Se concluyó un debate multiagente', 54),
('event_type', 'CONSENSUS_REACHED', 'Consenso Alcanzado', 'Los agentes alcanzaron consenso', 55)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- =============================================================================
-- VERIFICACIÓN
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM ref.actor WHERE agent_type = 'ALGORITHMIC';
    RAISE NOTICE 'Agentes algorítmicos insertados: %', v_count;

    SELECT COUNT(*) INTO v_count FROM meta.role WHERE agent_type = 'ALGORITHMIC';
    RAISE NOTICE 'Roles algorítmicos insertados: %', v_count;
END $$;

-- =============================================================================
-- FIN SEED AGENTES
-- =============================================================================
