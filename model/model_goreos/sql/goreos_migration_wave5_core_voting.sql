-- =============================================================================
-- GORE_OS Wave 5 — CORE Governance: Sesiones + Votación
-- =============================================================================
-- Agrega tabla de votos individuales por consejero (core.session_vote) y
-- 3 category schemes: session_type, vote_option, quorum_type.
-- Usa infraestructura DDL existente: committee, committee_member, session,
-- session_agreement, minute.
-- =============================================================================

BEGIN;

-- 1. Tabla de votos individuales por consejero
CREATE TABLE IF NOT EXISTS core.session_vote (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_agreement_id UUID NOT NULL REFERENCES core.session_agreement(id),
    voter_id UUID NOT NULL REFERENCES core.committee_member(id),
    vote_option_id UUID NOT NULL REFERENCES ref.category(id),
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_agreement_id, voter_id)
);

CREATE INDEX IF NOT EXISTS idx_session_vote_agreement
    ON core.session_vote(session_agreement_id);

CREATE INDEX IF NOT EXISTS idx_session_vote_voter
    ON core.session_vote(voter_id);

-- 2. Category schemes

-- session_type: tipos de sesión del consejo
INSERT INTO ref.category (scheme, code, label, sort_order) VALUES
    ('session_type', 'ORDINARIA', 'Sesión Ordinaria', 1),
    ('session_type', 'EXTRAORDINARIA', 'Sesión Extraordinaria', 2),
    ('session_type', 'CRISIS', 'Sesión de Crisis', 3)
ON CONFLICT (scheme, code) DO NOTHING;

-- vote_option: opciones de voto
INSERT INTO ref.category (scheme, code, label, sort_order) VALUES
    ('vote_option', 'A_FAVOR', 'A Favor', 1),
    ('vote_option', 'EN_CONTRA', 'En Contra', 2),
    ('vote_option', 'ABSTENCION', 'Abstención', 3)
ON CONFLICT (scheme, code) DO NOTHING;

-- quorum_type: tipo de mayoría requerida
INSERT INTO ref.category (scheme, code, label, sort_order) VALUES
    ('quorum_type', 'SIMPLE', 'Mayoría Simple (9/16)', 1),
    ('quorum_type', 'CALIFICADA', 'Mayoría Calificada (11/16)', 2)
ON CONFLICT (scheme, code) DO NOTHING;

COMMIT;

DO $$ BEGIN
    RAISE NOTICE 'Wave 5: core.session_vote + 3 schemes (session_type, vote_option, quorum_type) created';
END $$;
