-- Schema para US Model GORE_OS
-- Basado exclusivamente en User Stories YAML
-- Generado por Arquitecto Categórico v1.4.0

-- ══════════════════════════════════════════════════════════════════════════════
-- DDL: TABLAS DIMENSIONALES
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE dim_role (
    id VARCHAR(50) PRIMARY KEY,
    label TEXT,
    agent_type VARCHAR(20) DEFAULT 'HUMAN',
    description TEXT
);

CREATE TABLE dim_entity (
    id VARCHAR(50) PRIMARY KEY,
    domain VARCHAR(20)
);

CREATE TABLE dim_process (
    id VARCHAR(50) PRIMARY KEY
);

CREATE TABLE dim_extra_tag (
    tag_value VARCHAR(100) PRIMARY KEY
);

-- ══════════════════════════════════════════════════════════════════════════════
-- DDL: TABLAS DE HECHOS Y RELACIONES
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE fact_user_story (
    id VARCHAR(50) PRIMARY KEY,
    urn TEXT,
    name TEXT,
    as_a TEXT,
    i_want TEXT,
    so_that TEXT,
    status VARCHAR(20),
    role_id VARCHAR(50) REFERENCES dim_role(id),
    process_id VARCHAR(50) REFERENCES dim_process(id),
    domain VARCHAR(50),
    aspect VARCHAR(50),
    priority VARCHAR(10),
    scope VARCHAR(20)
);

CREATE TABLE acceptance_criteria (
    id SERIAL PRIMARY KEY,
    us_id VARCHAR(50) REFERENCES fact_user_story(id) ON DELETE CASCADE,
    description TEXT
);

-- Relaciones N:M
CREATE TABLE bridge_us_entity (
    us_id VARCHAR(50) REFERENCES fact_user_story(id) ON DELETE CASCADE,
    entity_id VARCHAR(50) REFERENCES dim_entity(id) ON DELETE CASCADE,
    PRIMARY KEY (us_id, entity_id)
);

CREATE TABLE bridge_us_extra_tag (
    us_id VARCHAR(50) REFERENCES fact_user_story(id) ON DELETE CASCADE,
    tag_value VARCHAR(100) REFERENCES dim_extra_tag(tag_value) ON DELETE CASCADE,
    PRIMARY KEY (us_id, tag_value)
);

-- ══════════════════════════════════════════════════════════════════════════════
-- DML: INSERCIÓN DE EJEMPLO (Data extraída)
-- ══════════════════════════════════════════════════════════════════════════════

INSERT INTO dim_role (id, label) VALUES 
('ROL-FIN-ANALISTA-TES', 'Analista de Tesorería'),
('ROL-GESTION-PRES', 'Gestión Presupuestaria');

INSERT INTO dim_entity (id, domain) VALUES 
('ENT-CONV-ACTA', 'CONV'),
('ENT-FIN-IPR-PAGO', 'FIN');

INSERT INTO dim_process (id) VALUES 
('PROC-FIN-PAGO-PROVEEDORES'),
('PROC-PLAN-FORMULACION-ARI');

-- [Los datos de las 818 US se insertan a continuación...]
