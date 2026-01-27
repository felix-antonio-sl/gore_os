-- =============================================================================
-- GORE_OS v3.1 - REMEDIACIÓN ONTOLÓGICA
-- =============================================================================
-- Archivo: goreos_remediation_ontological.sql
-- Descripción: Correcciones categóricas identificadas en auditoría ontológica
-- Fecha: 2026-01-27
-- Dependencias: goreos_ddl.sql, goreos_seed.sql
-- Referencia: /Users/felixsanhueza/.claude/plans/majestic-napping-naur.md
-- =============================================================================
-- Principios aplicados:
-- 1. N:M sobre FK simples (cuando ontología permite múltiples valores)
-- 2. Patrón gist:hasParty (partes con roles categorizados)
-- 3. Event Sourcing (mutaciones como eventos, no entidades)
-- 4. Category Pattern (taxonomías via ref.category)
-- =============================================================================

-- =============================================================================
-- OO-001: RELACIÓN N:M IPR↔TERRITORY (gnub:isLocatedIn)
-- =============================================================================
-- Cardinalidad: Un proyecto puede impactar múltiples comunas
-- Patrón: gist:isLocatedIn con tipo de impacto

-- Scheme para tipos de impacto territorial
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('territory_impact', 'UBICACION', 'Ubicación Física', 'Territorio donde se ejecuta físicamente la IPR', 1),
('territory_impact', 'IMPACTO_DIRECTO', 'Impacto Directo', 'Comunas directamente beneficiadas por la IPR', 2),
('territory_impact', 'IMPACTO_INDIRECTO', 'Impacto Indirecto', 'Comunas con efecto spillover de la IPR', 3),
('territory_impact', 'ZONA_INFLUENCIA', 'Zona de Influencia', 'Territorio de usuarios potenciales', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- Tabla de relación N:M
CREATE TABLE IF NOT EXISTS core.ipr_territory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID NOT NULL REFERENCES core.ipr(id) ON DELETE CASCADE,
    territory_id UUID NOT NULL REFERENCES core.territory(id),
    impact_type_id UUID NOT NULL REFERENCES ref.category(id),
    is_primary BOOLEAN DEFAULT FALSE,
    notes TEXT,
    -- Auditoría estándar GORE_OS
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    -- Constraint: una IPR solo puede tener un tipo de impacto por territorio
    CONSTRAINT uq_ipr_territory_impact UNIQUE (ipr_id, territory_id, impact_type_id)
);

COMMENT ON TABLE core.ipr_territory IS
'OO-001: Relación N:M IPR↔Territory siguiendo gnub:isLocatedIn con tipo de impacto';

COMMENT ON COLUMN core.ipr_territory.is_primary IS
'Territorio principal de la IPR (para queries rápidas)';

-- Índices
CREATE INDEX IF NOT EXISTS idx_ipr_territory_ipr ON core.ipr_territory(ipr_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_ipr_territory_territory ON core.ipr_territory(territory_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_ipr_territory_impact ON core.ipr_territory(impact_type_id);
CREATE INDEX IF NOT EXISTS idx_ipr_territory_primary ON core.ipr_territory(ipr_id) WHERE is_primary = TRUE AND deleted_at IS NULL;

-- =============================================================================
-- OO-002: TABLA IPR_MILESTONE (gnub:ProjectMilestone)
-- =============================================================================
-- Patrón: gist:ScheduledEvent con Goal
-- Características: planned_date vs actual_date, deviation_days calculado

-- Scheme para tipos de hito
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('milestone_type', 'INICIO_OBRA', 'Inicio de Obras', 'Acta de inicio de construcción', 1),
('milestone_type', 'AVANCE_25', 'Avance 25%', 'Hito de avance físico 25%', 2),
('milestone_type', 'AVANCE_50', 'Avance 50%', 'Hito de avance físico 50%', 3),
('milestone_type', 'AVANCE_75', 'Avance 75%', 'Hito de avance físico 75%', 4),
('milestone_type', 'RECEPCION_PROV', 'Recepción Provisoria', 'Acta de recepción provisoria de obras', 5),
('milestone_type', 'RECEPCION_DEF', 'Recepción Definitiva', 'Acta de recepción definitiva', 6),
('milestone_type', 'CIERRE_ADMIN', 'Cierre Administrativo', 'Cierre administrativo y contable', 7),
('milestone_type', 'ENTREGA_DISENO', 'Entrega de Diseño', 'Entrega de diseño o estudio', 8),
('milestone_type', 'INFORME_FINAL', 'Informe Final', 'Entrega de informe final', 9),
('milestone_type', 'APROBACION_CDP', 'Aprobación CDP', 'Emisión de Certificado de Disponibilidad Presupuestaria', 10),
('milestone_type', 'FIRMA_CONVENIO', 'Firma de Convenio', 'Suscripción del convenio de transferencia', 11),
('milestone_type', 'LICITACION', 'Publicación Licitación', 'Publicación en MercadoPúblico', 12),
('milestone_type', 'ADJUDICACION', 'Adjudicación', 'Resolución de adjudicación', 13)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- Tabla de hitos
CREATE TABLE IF NOT EXISTS core.ipr_milestone (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID NOT NULL REFERENCES core.ipr(id) ON DELETE CASCADE,
    milestone_type_id UUID NOT NULL REFERENCES ref.category(id),
    code VARCHAR(20),
    description TEXT,
    planned_date DATE NOT NULL,
    actual_date DATE,
    -- Columna calculada: desviación en días (positivo = atraso, negativo = adelanto)
    deviation_days INTEGER GENERATED ALWAYS AS (
        CASE WHEN actual_date IS NOT NULL
             THEN actual_date - planned_date
             ELSE NULL
        END
    ) STORED,
    completed_by_id UUID REFERENCES core.user(id),
    verification_notes TEXT,
    evidence_document_id UUID, -- FK a core.document cuando exista
    -- Auditoría estándar GORE_OS
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb
);

COMMENT ON TABLE core.ipr_milestone IS
'OO-002: Hitos de proyecto (gnub:ProjectMilestone) con fechas planificadas vs reales';

COMMENT ON COLUMN core.ipr_milestone.deviation_days IS
'Desviación calculada: actual - planned. Positivo = atraso, Negativo = adelanto';

-- Índices
CREATE INDEX IF NOT EXISTS idx_milestone_ipr ON core.ipr_milestone(ipr_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_milestone_type ON core.ipr_milestone(milestone_type_id);
CREATE INDEX IF NOT EXISTS idx_milestone_planned ON core.ipr_milestone(planned_date);
CREATE INDEX IF NOT EXISTS idx_milestone_actual ON core.ipr_milestone(actual_date) WHERE actual_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_milestone_deviation ON core.ipr_milestone(deviation_days) WHERE deviation_days IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_milestone_pending ON core.ipr_milestone(ipr_id, planned_date)
    WHERE actual_date IS NULL AND deleted_at IS NULL;

-- =============================================================================
-- OO-003: TABLA IPR_PARTY (gist:hasParty)
-- =============================================================================
-- Patrón: Partes de Agreement con roles categorizados
-- Reemplaza: executor_id, formulator_id, applicant_id (FKs simples)

-- Scheme para roles de parte
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('ipr_party_role', 'POSTULANTE', 'Postulante', 'Organización que postula la iniciativa (gnub:hasApplicant)', 1),
('ipr_party_role', 'FORMULADOR', 'Formulador', 'Organización que formula técnicamente la IPR', 2),
('ipr_party_role', 'EJECUTOR', 'Ejecutor', 'Organización que ejecuta técnica y financieramente (gnub:hasExecutor)', 3),
('ipr_party_role', 'COFINANCIADOR', 'Cofinanciador', 'Organización que aporta recursos adicionales', 4),
('ipr_party_role', 'UNIDAD_TECNICA', 'Unidad Técnica', 'MOP, SERVIU u otro servicio que supervisa ejecución', 5),
('ipr_party_role', 'FISCALIZADOR', 'Fiscalizador', 'Organización que fiscaliza el proyecto', 6),
('ipr_party_role', 'BENEFICIARIO', 'Beneficiario Institucional', 'Organización beneficiaria directa', 7),
('ipr_party_role', 'MANDANTE', 'Mandante', 'GORE como mandante en convenio mandato', 8),
('ipr_party_role', 'MANDATARIO', 'Mandatario', 'Organización que recibe el mandato de ejecución', 9)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- Tabla de partes
CREATE TABLE IF NOT EXISTS core.ipr_party (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID NOT NULL REFERENCES core.ipr(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES core.organization(id),
    party_role_id UUID NOT NULL REFERENCES ref.category(id),
    is_primary BOOLEAN DEFAULT FALSE,
    valid_from DATE,
    valid_to DATE,
    responsibility_description TEXT,
    contact_person TEXT,
    contact_email VARCHAR(255),
    -- Auditoría estándar GORE_OS
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core.user(id),
    updated_by_id UUID REFERENCES core.user(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core.user(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    -- Constraint: una organización solo puede tener un rol por IPR (salvo que termine y reinicie)
    CONSTRAINT uq_ipr_party_role UNIQUE (ipr_id, organization_id, party_role_id)
);

COMMENT ON TABLE core.ipr_party IS
'OO-003: Partes de IPR siguiendo gist:hasParty con roles categorizados (N:M)';

COMMENT ON COLUMN core.ipr_party.is_primary IS
'Parte principal para este rol (cuando hay múltiples ejecutores, uno es el principal)';

-- Índices
CREATE INDEX IF NOT EXISTS idx_ipr_party_ipr ON core.ipr_party(ipr_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_ipr_party_org ON core.ipr_party(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_ipr_party_role ON core.ipr_party(party_role_id);
CREATE INDEX IF NOT EXISTS idx_ipr_party_primary ON core.ipr_party(ipr_id, party_role_id)
    WHERE is_primary = TRUE AND deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_ipr_party_active ON core.ipr_party(ipr_id)
    WHERE (valid_to IS NULL OR valid_to >= CURRENT_DATE) AND deleted_at IS NULL;

-- Vistas de compatibilidad para código existente
CREATE OR REPLACE VIEW core.vw_ipr_executor AS
SELECT p.ipr_id, p.organization_id AS executor_id, o.name AS executor_name
FROM core.ipr_party p
JOIN ref.category c ON c.id = p.party_role_id
JOIN core.organization o ON o.id = p.organization_id
WHERE c.scheme = 'ipr_party_role'
  AND c.code = 'EJECUTOR'
  AND p.is_primary = TRUE
  AND p.deleted_at IS NULL;

COMMENT ON VIEW core.vw_ipr_executor IS
'Vista de compatibilidad: Ejecutor principal de cada IPR';

CREATE OR REPLACE VIEW core.vw_ipr_applicant AS
SELECT p.ipr_id, p.organization_id AS applicant_id, o.name AS applicant_name
FROM core.ipr_party p
JOIN ref.category c ON c.id = p.party_role_id
JOIN core.organization o ON o.id = p.organization_id
WHERE c.scheme = 'ipr_party_role'
  AND c.code = 'POSTULANTE'
  AND p.is_primary = TRUE
  AND p.deleted_at IS NULL;

COMMENT ON VIEW core.vw_ipr_applicant IS
'Vista de compatibilidad: Postulante principal de cada IPR';

CREATE OR REPLACE VIEW core.vw_ipr_formulator AS
SELECT p.ipr_id, p.organization_id AS formulator_id, o.name AS formulator_name
FROM core.ipr_party p
JOIN ref.category c ON c.id = p.party_role_id
JOIN core.organization o ON o.id = p.organization_id
WHERE c.scheme = 'ipr_party_role'
  AND c.code = 'FORMULADOR'
  AND p.is_primary = TRUE
  AND p.deleted_at IS NULL;

COMMENT ON VIEW core.vw_ipr_formulator IS
'Vista de compatibilidad: Formulador principal de cada IPR';

-- Vista consolidada de todas las partes
CREATE OR REPLACE VIEW core.vw_ipr_parties AS
SELECT
    p.ipr_id,
    i.codigo_bip,
    p.organization_id,
    o.name AS organization_name,
    c.code AS role_code,
    c.label AS role_label,
    p.is_primary,
    p.valid_from,
    p.valid_to,
    p.responsibility_description
FROM core.ipr_party p
JOIN core.ipr i ON i.id = p.ipr_id
JOIN core.organization o ON o.id = p.organization_id
JOIN ref.category c ON c.id = p.party_role_id
WHERE p.deleted_at IS NULL
  AND c.scheme = 'ipr_party_role';

COMMENT ON VIEW core.vw_ipr_parties IS
'Vista consolidada de todas las partes de cada IPR con sus roles';

-- =============================================================================
-- OO-008: TABLA INSTALLMENT_MILESTONE (gnub:triggersPayment)
-- =============================================================================
-- Patrón: Relación N:M cuota↔hito
-- Semántica: Hitos que gatillan pagos de cuotas

CREATE TABLE IF NOT EXISTS core.installment_milestone (
    installment_id UUID NOT NULL REFERENCES core.agreement_installment(id) ON DELETE CASCADE,
    milestone_id UUID NOT NULL REFERENCES core.ipr_milestone(id) ON DELETE CASCADE,
    is_required BOOLEAN DEFAULT TRUE,
    notes TEXT,
    PRIMARY KEY (installment_id, milestone_id)
);

COMMENT ON TABLE core.installment_milestone IS
'OO-008: Relación N:M cuota↔hito siguiendo gnub:triggersPayment';

COMMENT ON COLUMN core.installment_milestone.is_required IS
'Si TRUE, el hito es requisito para liberar el pago de la cuota';

-- Índices
CREATE INDEX IF NOT EXISTS idx_inst_milestone_inst ON core.installment_milestone(installment_id);
CREATE INDEX IF NOT EXISTS idx_inst_milestone_mile ON core.installment_milestone(milestone_id);
CREATE INDEX IF NOT EXISTS idx_inst_milestone_required ON core.installment_milestone(installment_id)
    WHERE is_required = TRUE;

-- =============================================================================
-- OO-006: ASPECTOS PLANIFICADOS (gnub:PlannedProgressAspect)
-- =============================================================================

INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('aspect', 'PLANNED_PHYSICAL_PROGRESS', 'Avance Físico Planificado',
 'gnub:PlannedProgressAspect - Porcentaje de avance según cronograma original', 15),
('aspect', 'PLANNED_FINANCIAL_PROGRESS', 'Avance Financiero Planificado',
 'Ejecución financiera planificada según flujo de caja proyectado', 16),
('aspect', 'PHYSICAL_DEVIATION', 'Desviación Física',
 'Diferencia entre avance real y planificado (puntos porcentuales)', 17),
('aspect', 'FINANCIAL_DEVIATION', 'Desviación Financiera',
 'Diferencia entre ejecución real y planificada (puntos porcentuales)', 18)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- =============================================================================
-- TRIGGERS DE VALIDACIÓN DE SCHEME
-- =============================================================================

-- Validación scheme para ipr_territory
CREATE OR REPLACE FUNCTION fn_validate_ipr_territory_schemes()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.impact_type_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.impact_type_id, 'territory_impact') THEN
            RAISE EXCEPTION 'impact_type_id debe pertenecer al scheme "territory_impact"';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ipr_territory_validate_schemes ON core.ipr_territory;
CREATE TRIGGER trg_ipr_territory_validate_schemes
    BEFORE INSERT OR UPDATE ON core.ipr_territory
    FOR EACH ROW EXECUTE FUNCTION fn_validate_ipr_territory_schemes();

-- Validación scheme para ipr_milestone
CREATE OR REPLACE FUNCTION fn_validate_ipr_milestone_schemes()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.milestone_type_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.milestone_type_id, 'milestone_type') THEN
            RAISE EXCEPTION 'milestone_type_id debe pertenecer al scheme "milestone_type"';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ipr_milestone_validate_schemes ON core.ipr_milestone;
CREATE TRIGGER trg_ipr_milestone_validate_schemes
    BEFORE INSERT OR UPDATE ON core.ipr_milestone
    FOR EACH ROW EXECUTE FUNCTION fn_validate_ipr_milestone_schemes();

-- Validación scheme para ipr_party
CREATE OR REPLACE FUNCTION fn_validate_ipr_party_schemes()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.party_role_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.party_role_id, 'ipr_party_role') THEN
            RAISE EXCEPTION 'party_role_id debe pertenecer al scheme "ipr_party_role"';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ipr_party_validate_schemes ON core.ipr_party;
CREATE TRIGGER trg_ipr_party_validate_schemes
    BEFORE INSERT OR UPDATE ON core.ipr_party
    FOR EACH ROW EXECUTE FUNCTION fn_validate_ipr_party_schemes();

-- =============================================================================
-- TRIGGER: Asegurar solo un is_primary=TRUE por (ipr_id, party_role_id)
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_ensure_single_primary_party()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_primary = TRUE THEN
        -- Desmarcar otros primarios del mismo rol
        UPDATE core.ipr_party
        SET is_primary = FALSE, updated_at = now()
        WHERE ipr_id = NEW.ipr_id
          AND party_role_id = NEW.party_role_id
          AND id != NEW.id
          AND is_primary = TRUE
          AND deleted_at IS NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ipr_party_single_primary ON core.ipr_party;
CREATE TRIGGER trg_ipr_party_single_primary
    BEFORE INSERT OR UPDATE OF is_primary ON core.ipr_party
    FOR EACH ROW
    WHEN (NEW.is_primary = TRUE)
    EXECUTE FUNCTION fn_ensure_single_primary_party();

-- =============================================================================
-- TRIGGER: Asegurar solo un is_primary=TRUE por ipr_id en ipr_territory
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_ensure_single_primary_territory()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_primary = TRUE THEN
        -- Desmarcar otros primarios
        UPDATE core.ipr_territory
        SET is_primary = FALSE, updated_at = now()
        WHERE ipr_id = NEW.ipr_id
          AND id != NEW.id
          AND is_primary = TRUE
          AND deleted_at IS NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ipr_territory_single_primary ON core.ipr_territory;
CREATE TRIGGER trg_ipr_territory_single_primary
    BEFORE INSERT OR UPDATE OF is_primary ON core.ipr_territory
    FOR EACH ROW
    WHEN (NEW.is_primary = TRUE)
    EXECUTE FUNCTION fn_ensure_single_primary_territory();

-- =============================================================================
-- VISTA: Modificaciones presupuestarias (sobre txn.event)
-- =============================================================================
-- OO-007: budget_modification ya es correcto como Event
-- Esta vista facilita queries sobre modificaciones

CREATE OR REPLACE VIEW core.vw_budget_modification AS
SELECT
    e.id,
    e.subject_id AS ipr_id,
    e.occurred_at,
    (e.data->>'modification_type') AS modification_type,
    (e.data->>'amount_before')::NUMERIC AS amount_before,
    (e.data->>'amount_after')::NUMERIC AS amount_after,
    (e.data->>'amount_delta')::NUMERIC AS amount_delta,
    (e.data->>'resolution_number') AS resolution_number,
    (e.data->>'justification') AS justification,
    e.created_by_id,
    e.created_at
FROM txn.event e
JOIN ref.category c ON c.id = e.event_type_id
WHERE c.scheme = 'event_type'
  AND c.code = 'BUDGET_MODIFICATION';

COMMENT ON VIEW core.vw_budget_modification IS
'OO-007: Vista sobre txn.event para modificaciones presupuestarias (categóricamente correcto como Event)';

-- Insertar event_type si no existe
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('event_type', 'BUDGET_MODIFICATION', 'Modificación Presupuestaria',
 'Evento de modificación presupuestaria (suplemento, reasignación, rebaja)', 20)
ON CONFLICT (scheme, code) DO NOTHING;

-- =============================================================================
-- FIN REMEDIACIÓN ONTOLÓGICA v3.1
-- =============================================================================
-- Tablas creadas: 4 (ipr_territory, ipr_milestone, ipr_party, installment_milestone)
-- Schemes agregados: 4 (territory_impact, milestone_type, ipr_party_role, +aspectos)
-- Vistas creadas: 5 (vw_ipr_executor, vw_ipr_applicant, vw_ipr_formulator, vw_ipr_parties, vw_budget_modification)
-- Triggers: 5 (3 validación scheme, 2 single primary)
-- =============================================================================

DO $$ BEGIN RAISE NOTICE 'GORE_OS Remediación Ontológica v3.1 aplicada correctamente'; END $$;
