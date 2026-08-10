-- =============================================================================
-- GORE_OS — Demo Data Ciclo 2
-- =============================================================================
-- SEPARACION REAL/DEMO:
--   - Todos los registros de este archivo tienen códigos con prefijo DEMO-
--   - Los catálogos estructurales viven en goreos_seed.sql
--   - Para limpiar estos datos: ejecutar goreos_unseed_demo_ciclo2.sql
-- =============================================================================

BEGIN;

-- =============================================================================
-- DATOS DEMO (removibles con goreos_unseed_demo_ciclo2.sql)
-- Todos los registros demo tienen código/número con prefijo DEMO-
-- FKs a organizaciones e IPRs usan subqueries para portabilidad
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 2.1 PROGRAMAS PRESUPUESTARIOS DEMO (6 registros)
-- -----------------------------------------------------------------------------
-- DAF — Subtítulo 31, FNDR, ejecución alta (80%)
INSERT INTO core.budget_program (
    code, name, fiscal_year,
    program_type_id, subtitle_id, item_id, allocation_id, owner_division_id,
    initial_amount, current_amount, committed_amount, accrued_amount, paid_amount,
    fndr_amount, sectorial_amount, created_at, updated_at
) VALUES (
    'DEMO-BP-001',
    'Programa Inversión Regional DAF — FNDR 2026',
    2026,
    (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_INVERSION' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='31' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='INV_REAL' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='FNDR_INFRAESTRUCTURA' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DAF' LIMIT 1),
    2000000000.00, 1800000000.00, 1200000000.00, 900000000.00, 1440000000.00,
    1800000000.00, 0.00,
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- DAF — Subtítulo 22, Propios, ejecución media-alta (70%)
INSERT INTO core.budget_program (
    code, name, fiscal_year,
    program_type_id, subtitle_id, item_id, allocation_id, owner_division_id,
    initial_amount, current_amount, committed_amount, accrued_amount, paid_amount,
    created_at, updated_at
) VALUES (
    'DEMO-BP-002',
    'Funcionamiento Administración DAF 2026',
    2026,
    (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_FUNCIONAMIENTO' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='22' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='BIENES_SERVICIOS' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='PROPIOS_OPERACION' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DAF' LIMIT 1),
    800000000.00, 750000000.00, 600000000.00, 580000000.00, 525000000.00,
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- DIPIR — Subtítulo 31, FNDR, ejecución media-baja (40%)
INSERT INTO core.budget_program (
    code, name, fiscal_year,
    program_type_id, subtitle_id, item_id, allocation_id, owner_division_id,
    initial_amount, current_amount, committed_amount, accrued_amount, paid_amount,
    fndr_amount, created_at, updated_at
) VALUES (
    'DEMO-BP-003',
    'Cartera Proyectos DIPIR — FNDR 2026',
    2026,
    (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_INVERSION' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='31' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='INV_REAL' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='FNDR_INFRAESTRUCTURA' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DIPIR' LIMIT 1),
    5000000000.00, 4800000000.00, 2000000000.00, 1200000000.00, 1920000000.00,
    4800000000.00,
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- DIPIR — Subtítulo 33, Sectorial, ejecución baja (30%)
INSERT INTO core.budget_program (
    code, name, fiscal_year,
    program_type_id, subtitle_id, item_id, allocation_id, owner_division_id,
    initial_amount, current_amount, committed_amount, accrued_amount, paid_amount,
    sectorial_amount, created_at, updated_at
) VALUES (
    'DEMO-BP-004',
    'Transferencias Capital DIPIR — Sectorial 2026',
    2026,
    (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_TRANSFERENCIA' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='33' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='TRANSF_CAPITAL' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='SECT_MOP' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DIPIR' LIMIT 1),
    1500000000.00, 1400000000.00, 1000000000.00, 800000000.00, 420000000.00,
    1400000000.00,
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- DIFOI — Subtítulo 24, FNDR 8%, ejecución alta (80%)
INSERT INTO core.budget_program (
    code, name, fiscal_year,
    program_type_id, subtitle_id, item_id, allocation_id, owner_division_id,
    initial_amount, current_amount, committed_amount, accrued_amount, paid_amount,
    fndr_amount, created_at, updated_at
) VALUES (
    'DEMO-BP-005',
    'Transferencias Corrientes Fomento — FNDR 8% 2026',
    2026,
    (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_PROGRAMA' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='24' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='TRANSFERENCIAS_CTES' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='FNDR_8PCT' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DIFOI' LIMIT 1),
    600000000.00, 580000000.00, 400000000.00, 350000000.00, 464000000.00,
    580000000.00,
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- DIT — Subtítulo 31, FNDR, ejecución media (50%)
INSERT INTO core.budget_program (
    code, name, fiscal_year,
    program_type_id, subtitle_id, item_id, allocation_id, owner_division_id,
    initial_amount, current_amount, committed_amount, accrued_amount, paid_amount,
    fndr_amount, created_at, updated_at
) VALUES (
    'DEMO-BP-006',
    'Obras Públicas DIT — FNDR 2026',
    2026,
    (SELECT id FROM ref.category WHERE scheme='program_type' AND code='PPR_INVERSION' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_subtitle' AND code='31' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_item' AND code='INV_REAL' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='budget_allocation' AND code='FNDR_INFRAESTRUCTURA' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DIT' LIMIT 1),
    3200000000.00, 3000000000.00, 1800000000.00, 1000000000.00, 1500000000.00,
    3000000000.00,
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2.2 ARRASTRES PRESUPUESTARIOS DEMO (3 registros — saldos de 2025)
-- -----------------------------------------------------------------------------
INSERT INTO core.budget_carryover (
    budget_program_id, fiscal_year, amount, created_at, updated_at
) VALUES
(
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-003' LIMIT 1),
    2025, 450000000.00, NOW(), NOW()
),
(
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-004' LIMIT 1),
    2025, 280000000.00, NOW(), NOW()
),
(
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-006' LIMIT 1),
    2025, 620000000.00, NOW(), NOW()
)
ON CONFLICT DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2.3 COMPROMISOS PRESUPUESTARIOS DEMO / CDPs (8 registros)
-- -----------------------------------------------------------------------------
-- CDP-001: DEMO-BP-001 vinculado a IPR real
INSERT INTO core.budget_commitment (
    commitment_number, budget_program_id, ipr_id,
    amount, issued_at, expires_at,
    status_id, created_at, updated_at
) VALUES (
    'DEMO-CDP-001',
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-001' LIMIT 1),
    (SELECT id FROM core.ipr WHERE codigo_bip='2401SC0028' LIMIT 1),
    350000000.00, '2026-01-15', '2026-12-31',
    (SELECT id FROM ref.category WHERE scheme='budget_commitment_status' AND code='VIGENTE' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- CDP-002
INSERT INTO core.budget_commitment (
    commitment_number, budget_program_id, ipr_id,
    amount, issued_at, expires_at,
    status_id, created_at, updated_at
) VALUES (
    'DEMO-CDP-002',
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-001' LIMIT 1),
    (SELECT id FROM core.ipr WHERE codigo_bip='2401SC0180' LIMIT 1),
    280000000.00, '2026-02-01', '2026-11-30',
    (SELECT id FROM ref.category WHERE scheme='budget_commitment_status' AND code='VIGENTE' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- CDP-003
INSERT INTO core.budget_commitment (
    commitment_number, budget_program_id,
    amount, issued_at, expires_at,
    status_id, created_at, updated_at
) VALUES (
    'DEMO-CDP-003',
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-003' LIMIT 1),
    600000000.00, '2026-01-20', '2026-12-31',
    (SELECT id FROM ref.category WHERE scheme='budget_commitment_status' AND code='EJECUTADO' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- CDP-004
INSERT INTO core.budget_commitment (
    commitment_number, budget_program_id, ipr_id,
    amount, issued_at, expires_at,
    status_id, created_at, updated_at
) VALUES (
    'DEMO-CDP-004',
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-003' LIMIT 1),
    (SELECT id FROM core.ipr WHERE codigo_bip='2401D0003' LIMIT 1),
    520000000.00, '2026-02-10', '2026-12-31',
    (SELECT id FROM ref.category WHERE scheme='budget_commitment_status' AND code='VIGENTE' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- CDP-005
INSERT INTO core.budget_commitment (
    commitment_number, budget_program_id,
    amount, issued_at, expires_at,
    status_id, created_at, updated_at
) VALUES (
    'DEMO-CDP-005',
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-004' LIMIT 1),
    380000000.00, '2026-01-10', '2026-06-30',
    (SELECT id FROM ref.category WHERE scheme='budget_commitment_status' AND code='VIGENTE' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- CDP-006 (vencido)
INSERT INTO core.budget_commitment (
    commitment_number, budget_program_id,
    amount, issued_at, expires_at,
    status_id, created_at, updated_at
) VALUES (
    'DEMO-CDP-006',
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-004' LIMIT 1),
    120000000.00, '2025-10-01', '2025-12-31',
    (SELECT id FROM ref.category WHERE scheme='budget_commitment_status' AND code='VENCIDO' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- CDP-007
INSERT INTO core.budget_commitment (
    commitment_number, budget_program_id,
    amount, issued_at, expires_at,
    status_id, created_at, updated_at
) VALUES (
    'DEMO-CDP-007',
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-005' LIMIT 1),
    180000000.00, '2026-02-05', '2026-09-30',
    (SELECT id FROM ref.category WHERE scheme='budget_commitment_status' AND code='VIGENTE' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- CDP-008
INSERT INTO core.budget_commitment (
    commitment_number, budget_program_id, ipr_id,
    amount, issued_at, expires_at,
    status_id, created_at, updated_at
) VALUES (
    'DEMO-CDP-008',
    (SELECT id FROM core.budget_program WHERE code='DEMO-BP-006' LIMIT 1),
    (SELECT id FROM core.ipr WHERE codigo_bip='2401D0160' LIMIT 1),
    720000000.00, '2026-01-25', '2026-12-31',
    (SELECT id FROM ref.category WHERE scheme='budget_commitment_status' AND code='VIGENTE' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2.4 CONVENIOS DEMO (4 registros)
-- -----------------------------------------------------------------------------
-- AGR-001: VIGENTE, MANDATO, IPR real 2401SC0028
INSERT INTO core.agreement (
    agreement_number, agreement_type_id, state_id,
    ipr_id, giver_id, receiver_id,
    total_amount, signed_at, valid_from, valid_to,
    created_at, updated_at
) VALUES (
    'DEMO-AGR-001',
    (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE' LIMIT 1),
    (SELECT id FROM core.ipr WHERE codigo_bip='2401SC0028' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DIPIR' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DAF' LIMIT 1),
    500000000.00,
    '2025-06-01', '2025-06-01', '2027-05-31',
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- AGR-002: VIGENTE, TRANSFERENCIA, vence en ~60 días (por vencer pronto)
INSERT INTO core.agreement (
    agreement_number, agreement_type_id, state_id,
    ipr_id, giver_id, receiver_id,
    total_amount, signed_at, valid_from, valid_to,
    created_at, updated_at
) VALUES (
    'DEMO-AGR-002',
    (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='TRANSFERENCIA' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE' LIMIT 1),
    (SELECT id FROM core.ipr WHERE codigo_bip='2401SC0180' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DIPIR' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DIFOI' LIMIT 1),
    350000000.00,
    '2024-04-15', '2024-04-15',
    (CURRENT_DATE + INTERVAL '28 days')::timestamptz,
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- AGR-003: EN_MODIFICACION, COLABORACION
INSERT INTO core.agreement (
    agreement_number, agreement_type_id, state_id,
    ipr_id, giver_id, receiver_id,
    total_amount, signed_at, valid_from, valid_to,
    created_at, updated_at
) VALUES (
    'DEMO-AGR-003',
    (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='COLABORACION' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='EN_MODIFICACION' LIMIT 1),
    (SELECT id FROM core.ipr WHERE codigo_bip='2401D0003' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DIT' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DIJ' LIMIT 1),
    200000000.00,
    '2025-01-10', '2025-01-10', '2026-06-30',
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- AGR-004: VENCIDO, MANDATO, expirado en 2025
INSERT INTO core.agreement (
    agreement_number, agreement_type_id, state_id,
    ipr_id, giver_id, receiver_id,
    total_amount, signed_at, valid_from, valid_to,
    created_at, updated_at
) VALUES (
    'DEMO-AGR-004',
    (SELECT id FROM ref.category WHERE scheme='agreement_type' AND code='MANDATO' LIMIT 1),
    (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VENCIDO' LIMIT 1),
    (SELECT id FROM core.ipr WHERE codigo_bip='2401D0160' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DIPLADE' LIMIT 1),
    (SELECT id FROM core.organization WHERE code='DGI' LIMIT 1),
    800000000.00,
    '2024-02-01', '2024-02-01', '2025-01-31',
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2.5 CUOTAS DE CONVENIOS DEMO (10 registros)
-- -----------------------------------------------------------------------------
-- Cuotas AGR-001 (3 cuotas — 2 pagadas, 1 pendiente)
INSERT INTO core.agreement_installment (
    agreement_id, installment_number, amount, due_date,
    payment_status_id, paid_at, paid_amount, payment_reference,
    created_at, updated_at
) VALUES (
    (SELECT id FROM core.agreement WHERE agreement_number='DEMO-AGR-001' LIMIT 1),
    1, 166666666.67, '2025-12-31',
    (SELECT id FROM ref.category WHERE scheme='payment_status' AND code='PAGADO' LIMIT 1),
    '2025-12-28', 166666666.67, 'TRF-2025-12-001',
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

INSERT INTO core.agreement_installment (
    agreement_id, installment_number, amount, due_date,
    payment_status_id, paid_at, paid_amount, payment_reference,
    created_at, updated_at
) VALUES (
    (SELECT id FROM core.agreement WHERE agreement_number='DEMO-AGR-001' LIMIT 1),
    2, 166666666.67, '2026-06-30',
    (SELECT id FROM ref.category WHERE scheme='payment_status' AND code='PAGADO' LIMIT 1),
    '2026-06-25', 166666666.67, 'TRF-2026-06-001',
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

INSERT INTO core.agreement_installment (
    agreement_id, installment_number, amount, due_date,
    payment_status_id, created_at, updated_at
) VALUES (
    (SELECT id FROM core.agreement WHERE agreement_number='DEMO-AGR-001' LIMIT 1),
    3, 166666666.66, '2026-12-31',
    (SELECT id FROM ref.category WHERE scheme='payment_status' AND code='PENDIENTE' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- Cuotas AGR-002 (3 cuotas — 1 pagada, 1 en proceso, 1 pendiente)
INSERT INTO core.agreement_installment (
    agreement_id, installment_number, amount, due_date,
    payment_status_id, paid_at, paid_amount, payment_reference,
    created_at, updated_at
) VALUES (
    (SELECT id FROM core.agreement WHERE agreement_number='DEMO-AGR-002' LIMIT 1),
    1, 116666666.67, '2024-08-31',
    (SELECT id FROM ref.category WHERE scheme='payment_status' AND code='PAGADO' LIMIT 1),
    '2024-08-28', 116666666.67, 'TRF-2024-08-002',
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

INSERT INTO core.agreement_installment (
    agreement_id, installment_number, amount, due_date,
    payment_status_id, created_at, updated_at
) VALUES (
    (SELECT id FROM core.agreement WHERE agreement_number='DEMO-AGR-002' LIMIT 1),
    2, 116666666.67, '2025-04-30',
    (SELECT id FROM ref.category WHERE scheme='payment_status' AND code='EN_PROCESO' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

INSERT INTO core.agreement_installment (
    agreement_id, installment_number, amount, due_date,
    payment_status_id, created_at, updated_at
) VALUES (
    (SELECT id FROM core.agreement WHERE agreement_number='DEMO-AGR-002' LIMIT 1),
    3, 116666666.66, (CURRENT_DATE + INTERVAL '28 days')::date,
    (SELECT id FROM ref.category WHERE scheme='payment_status' AND code='PENDIENTE' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- Cuotas AGR-003 (2 cuotas — ambas pendientes)
INSERT INTO core.agreement_installment (
    agreement_id, installment_number, amount, due_date,
    payment_status_id, created_at, updated_at
) VALUES (
    (SELECT id FROM core.agreement WHERE agreement_number='DEMO-AGR-003' LIMIT 1),
    1, 100000000.00, '2026-03-31',
    (SELECT id FROM ref.category WHERE scheme='payment_status' AND code='PENDIENTE' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

INSERT INTO core.agreement_installment (
    agreement_id, installment_number, amount, due_date,
    payment_status_id, created_at, updated_at
) VALUES (
    (SELECT id FROM core.agreement WHERE agreement_number='DEMO-AGR-003' LIMIT 1),
    2, 100000000.00, '2026-06-30',
    (SELECT id FROM ref.category WHERE scheme='payment_status' AND code='PENDIENTE' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

-- Cuotas AGR-004 (2 cuotas — ambas vencidas/rechazadas)
INSERT INTO core.agreement_installment (
    agreement_id, installment_number, amount, due_date,
    payment_status_id, paid_at, paid_amount, payment_reference,
    created_at, updated_at
) VALUES (
    (SELECT id FROM core.agreement WHERE agreement_number='DEMO-AGR-004' LIMIT 1),
    1, 400000000.00, '2024-07-31',
    (SELECT id FROM ref.category WHERE scheme='payment_status' AND code='PAGADO' LIMIT 1),
    '2024-07-29', 400000000.00, 'TRF-2024-07-004',
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

INSERT INTO core.agreement_installment (
    agreement_id, installment_number, amount, due_date,
    payment_status_id, created_at, updated_at
) VALUES (
    (SELECT id FROM core.agreement WHERE agreement_number='DEMO-AGR-004' LIMIT 1),
    2, 400000000.00, '2025-01-15',
    (SELECT id FROM ref.category WHERE scheme='payment_status' AND code='DIFERIDO' LIMIT 1),
    NOW(), NOW()
) ON CONFLICT DO NOTHING;

COMMIT;

-- =============================================================================
-- VERIFICACION (ejecutar manualmente):
-- SELECT code, name, fiscal_year,
--        ROUND(paid_amount / NULLIF(current_amount,0) * 100, 1) AS ejecucion_pct
-- FROM core.budget_program WHERE code LIKE 'DEMO-%' ORDER BY code;
--
-- SELECT agreement_number, total_amount, valid_to,
--        EXTRACT(DAY FROM valid_to - CURRENT_DATE) AS dias_restantes
-- FROM core.agreement WHERE agreement_number LIKE 'DEMO-%' ORDER BY agreement_number;
-- =============================================================================
