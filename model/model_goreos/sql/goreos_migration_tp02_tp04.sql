-- TP-02: Subvención 8% Fund Distribution (7 funds + ceilings)
-- TP-04: FRIL Category Taxonomy (12 categories)
-- Creates core.subv8_fund, core.subv8_fund_ceiling, core.fril_category

BEGIN;

-- ============================================================
-- TP-02: core.subv8_fund (7 thematic funds)
-- ============================================================
CREATE TABLE IF NOT EXISTS core.subv8_fund (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code          VARCHAR(32) NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    budget_regular NUMERIC,
    budget_special NUMERIC,
    budget_total  NUMERIC,
    is_exclusive  BOOLEAN NOT NULL DEFAULT false,
    sort_order    INT NOT NULL DEFAULT 0,
    is_active     BOOLEAN NOT NULL DEFAULT true,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE core.subv8_fund IS 'TP-02: Subvención 8% thematic funds with budget ceilings';

INSERT INTO core.subv8_fund (code, name, budget_regular, budget_special, budget_total, is_exclusive, sort_order)
VALUES
    ('CULTURA',        'Fondo de Cultura',                330000000, 270000000, 600000000,  false, 1),
    ('SOCIAL',         'Fondo Social e Inclusión',        500000000, NULL,      500000000,  false, 2),
    ('GENERO',         'Fondo de Equidad de Género',      400000000, NULL,      400000000,  false, 3),
    ('DEPORTE',        'Fondo de Deporte',                800000000, 200000000, 1000000000, false, 4),
    ('ADULTO_MAYOR',   'Fondo para Personas Mayores',     400000000, NULL,      400000000,  true,  5),
    ('MEDIO_AMBIENTE', 'Fondo de Medio Ambiente',         400000000, NULL,      400000000,  false, 6),
    ('SEGURIDAD',      'Fondo de Seguridad Ciudadana',   1550000000, NULL,     1550000000,  false, 7)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- TP-02: core.subv8_fund_ceiling (project ceilings per fund × institution type)
-- ============================================================
CREATE TABLE IF NOT EXISTS core.subv8_fund_ceiling (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fund_id          UUID NOT NULL REFERENCES core.subv8_fund(id),
    institution_type VARCHAR(64) NOT NULL,
    area             VARCHAR(64),
    max_amount       NUMERIC NOT NULL CHECK (max_amount > 0),
    notes            TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Functional unique: one ceiling per (fund, institution_type, area) — COALESCE handles NULL area
CREATE UNIQUE INDEX IF NOT EXISTS uq_subv8_ceiling_fund_type_area
    ON core.subv8_fund_ceiling(fund_id, institution_type, COALESCE(area, ''));

CREATE INDEX IF NOT EXISTS idx_subv8_fund_ceiling_fund
    ON core.subv8_fund_ceiling(fund_id);

COMMENT ON TABLE core.subv8_fund_ceiling IS 'TP-02: Max project amount per fund × institution type × area';

-- Seed ceilings (representative subset — admin can add more via CRUD)
INSERT INTO core.subv8_fund_ceiling (fund_id, institution_type, area, max_amount, notes)
SELECT f.id, v.institution_type, v.area, v.max_amount, v.notes
FROM core.subv8_fund f
JOIN (VALUES
    ('CULTURA',        'CORPORACION',              'general',              5000000,   NULL::TEXT),
    ('CULTURA',        'ORG_CULTURAL',             'general',              3500000,   NULL),
    ('CULTURA',        'ORG_COMUNITARIA',          'general',              2500000,   'Juntas de vecinos, clubes'),
    ('CULTURA',        'PRODUCTORA',               'cine',                60000000,   'Producción cinematográfica'),
    ('CULTURA',        'PRODUCTORA',               'festival',            20000000,   'Festivales cine/música/teatro'),
    ('CULTURA',        'PRODUCTORA',               'libro',               10000000,   'Creación literaria'),
    ('SOCIAL',         'CORPORACION',              'general',              5500000,   NULL),
    ('SOCIAL',         'ORG_TERRITORIAL',          'general',              3500000,   NULL),
    ('SOCIAL',         'RESIDENCIA_MEJOR_NINEZ',   'exclusivo',           10000000,   'Residencias Mejor Niñez'),
    ('GENERO',         'ORG_TERRITORIAL',          'general',              3500000,   NULL),
    ('GENERO',         'CORPORACION',              'autonomia_mujer',      6500000,   NULL),
    ('DEPORTE',        'ASOCIACION_REGIONAL',      'general',             10000000,   NULL),
    ('DEPORTE',        'ASOCIACION_COMUNAL',       'general',              6000000,   NULL),
    ('DEPORTE',        'UNIVERSIDAD',              'general',              4000000,   NULL),
    ('DEPORTE',        'CLUB_DEPORTIVO',           'general',              1800000,   NULL),
    ('DEPORTE',        'CORPORACION',              'organizacion_promocion', 30000000, NULL),
    ('ADULTO_MAYOR',   'ALL',                      'general',              2500000,   'Tope unificado para todas las áreas'),
    ('MEDIO_AMBIENTE', 'CORPORACION',              'general',              6500000,   NULL),
    ('MEDIO_AMBIENTE', 'ORG_TERRITORIAL',          'general',              3500000,   NULL),
    ('MEDIO_AMBIENTE', 'COMITE_APR',               'paneles_solares',      6000000,   NULL),
    ('MEDIO_AMBIENTE', 'CORPORACION',              'sendero_sustentable', 25000000,   NULL),
    ('SEGURIDAD',      'ORG_TERRITORIAL',          'general',              5500000,   NULL)
) AS v(fund_code, institution_type, area, max_amount, notes) ON f.code = v.fund_code
ON CONFLICT DO NOTHING;

-- ============================================================
-- TP-04: core.fril_category (12 FRIL project categories)
-- ============================================================
CREATE TABLE IF NOT EXISTS core.fril_category (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code                      VARCHAR(3) NOT NULL UNIQUE,
    name                      TEXT NOT NULL,
    group_code                VARCHAR(1) NOT NULL CHECK (group_code IN ('A', 'B', 'C', 'D')),
    group_name                TEXT NOT NULL,
    description               TEXT,
    examples                  TEXT,
    max_utm                   NUMERIC(12,2) NOT NULL DEFAULT 4545,
    is_exempt_commune_limit   BOOLEAN NOT NULL DEFAULT false,
    is_active                 BOOLEAN NOT NULL DEFAULT true,
    sort_order                INT NOT NULL DEFAULT 0,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE core.fril_category IS 'TP-04: FRIL project categories (12 types in 4 groups A-D)';

INSERT INTO core.fril_category (code, name, group_code, group_name, description, examples, max_utm, is_exempt_commune_limit, sort_order)
VALUES
    ('A1', 'Integración Rural',    'A', 'Desarrollo Territorial', 'Infraestructura de servicios básicos y conectividad para zonas alejadas', 'Sistemas APR, electrificación rural, telecomunicaciones', 4545, false, 1),
    ('A2', 'Acceso al Agua',       'A', 'Desarrollo Territorial', 'Sistemas de agua potable, alcantarillado y drenaje',                     'Sistemas APR, impulsión, tratamiento, distribución, alcantarillado', 4545, true, 2),
    ('A3', 'Vial',                 'A', 'Desarrollo Territorial', 'Infraestructura vial y de conectividad terrestre',                       'Aceras, baches, calles, caminos, cunetas, veredas, supresor de polvo', 4545, true, 3),
    ('B1', 'Edificación Pública',  'B', 'Servicios',              'Construcción y mejoramiento de edificios públicos',                       'Postas, centros de salud, escuelas, patios cubiertos, cuarteles de bomberos', 4545, false, 4),
    ('B2', 'Gestión de Riesgos',   'B', 'Servicios',              'Obras de mitigación y prevención de riesgos naturales',                  'Muros de contención, drenajes, cortafuegos, desbroce', 4545, false, 5),
    ('B3', 'Seguridad',            'B', 'Servicios',              'Infraestructura de seguridad ciudadana',                                 'Luminarias, televigilancia, cierres perimetrales, refugios peatonales', 4545, false, 6),
    ('C1', 'Inclusión',            'C', 'Desarrollo Social y Económico', 'Infraestructura para inclusión social',                           'Infraestructura inclusiva, centros de terapia, centros de adulto mayor', 4545, false, 7),
    ('C2', 'Género',               'C', 'Desarrollo Social y Económico', 'Infraestructura con enfoque de género',                           'Centros de acogida, casas de protección', 4545, false, 8),
    ('C3', 'Turismo',              'C', 'Desarrollo Social y Económico', 'Infraestructura turística y patrimonial',                          'Pórticos, senderos turísticos, bordes costeros, miradores, señalética', 4545, false, 9),
    ('D1', 'Deportes',             'D', 'Medio Ambiente',         'Infraestructura deportiva y recreativa',                                  'Canchas, multicanchas, estadios, piscinas, pistas de trote, plazas activas', 4545, false, 10),
    ('D2', 'Áreas Verdes',         'D', 'Medio Ambiente',         'Espacios verdes y de esparcimiento',                                     'Paseos peatonales, plazas, parques, juegos de agua', 4545, false, 11),
    ('D3', 'Sustentabilidad',      'D', 'Medio Ambiente',         'Proyectos de sustentabilidad ambiental',                                 'Paneles solares, energía eólica, riego eficiente, reciclaje, compostaje', 4545, false, 12)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- Self-register migration
-- ============================================================
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_tp02_tp04.sql', 'manual', 'tp02_tp04_self_register')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
