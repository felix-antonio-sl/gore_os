-- Seed CORE committee members for test DB
-- Creates the Consejo Regional committee + 16 voting members
-- Uses the existing consejero person + 15 synthetic test persons

DO $$
DECLARE
    v_committee_id UUID;
    v_committee_type_id UUID;
    v_consejero_person_id UUID := 'a0000001-0000-0000-0000-000000000009';
    v_person_id UUID;
    i INT;
BEGIN
    -- Get or create committee_type CORE
    SELECT id INTO v_committee_type_id
    FROM ref.category WHERE scheme = 'committee_type' AND code = 'CORE';

    -- Create CONSEJO-REGIONAL committee
    INSERT INTO core.committee (code, name, committee_type_id, is_permanent)
    VALUES ('CONSEJO-REGIONAL', 'Consejo Regional de Ñuble', v_committee_type_id, TRUE)
    ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
    RETURNING id INTO v_committee_id;

    -- Member 1: the real consejero test user
    INSERT INTO core.committee_member (
        committee_id, person_id, is_voting_member, start_date
    ) VALUES (
        v_committee_id, v_consejero_person_id, TRUE, '2024-01-01'
    ) ON CONFLICT DO NOTHING;

    -- Members 2-16: synthetic test persons
    FOR i IN 2..16 LOOP
        -- Create synthetic person
        INSERT INTO core.person (
            id, names, paternal_surname, email, is_active
        ) VALUES (
            ('c0000001-0000-0000-0000-0000000000' || LPAD(i::text, 2, '0'))::uuid,
            'Consejero' || i,
            'Testperson' || i,
            'consejero' || i || '@test.cl',
            true
        ) ON CONFLICT (id) DO NOTHING
        RETURNING id INTO v_person_id;

        -- If person already existed, get its id
        IF v_person_id IS NULL THEN
            v_person_id := ('c0000001-0000-0000-0000-0000000000' || LPAD(i::text, 2, '0'))::uuid;
        END IF;

        INSERT INTO core.committee_member (
            committee_id, person_id, is_voting_member, start_date
        ) VALUES (
            v_committee_id, v_person_id, TRUE, '2024-01-01'
        ) ON CONFLICT DO NOTHING;
    END LOOP;

    RAISE NOTICE 'CORE members seeded: 16 voting members in CONSEJO-REGIONAL';
END $$;
