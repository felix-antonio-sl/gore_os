-- =============================================================================
-- GORE_OS Wave 5 — Rollback CORE Governance
-- =============================================================================

BEGIN;

-- 1. Drop vote table
DROP TABLE IF EXISTS core.session_vote;

-- 2. Remove category schemes
DELETE FROM ref.category WHERE scheme = 'vote_option';
DELETE FROM ref.category WHERE scheme = 'quorum_type';
DELETE FROM ref.category WHERE scheme = 'session_type';

COMMIT;

DO $$ BEGIN
    RAISE NOTICE 'Wave 5 rollback: core.session_vote + 3 schemes removed';
END $$;
