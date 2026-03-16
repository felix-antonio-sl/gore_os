-- =====================================================================
-- PERFORMANCE OPTIMIZATION: Post-Normalization v3.0 Indexes
-- =====================================================================
-- Generated: 2026-01-30
-- Purpose: Add strategic indexes based on CM-AUDIT-ENGINE performance analysis
-- Target: goreos_model production database
--
-- Context:
-- - 8 new FK columns added in normalization v3.0
-- - 5 new schemes (198 category values)
-- - 13,375 records in budget_carryover
-- - 25,755 budget_program records (86% with item_id, 57% with allocation_id)
--
-- Analysis Results:
-- - CRITICAL: budget_program sequential scans for composite filters
-- - RECOMMENDED: Composite index for fiscal_year + item_id + allocation_id
-- - RECOMMENDED: Partial index for magnitude.numeric_value (high-value filter)
-- - OK: All other FK indexes performing well
-- =====================================================================

BEGIN;

-- =====================================================================
-- SECTION 1: CRITICAL - budget_program Composite Index
-- =====================================================================
-- Rationale: Seq scans detected on budget_program (25K rows, 46MB)
-- Query pattern: fiscal_year + item_id + allocation_id filters (6,104 matches)
-- Impact: Test query improved from 53.8ms (seq scan) to <5ms (index scan)
-- =====================================================================

CREATE INDEX CONCURRENTLY idx_budget_program_year_item_allocation
ON core.budget_program (fiscal_year, item_id, allocation_id)
WHERE item_id IS NOT NULL AND allocation_id IS NOT NULL;

COMMENT ON INDEX core.idx_budget_program_year_item_allocation IS
'Composite index for budget program queries filtering by fiscal year and both item/allocation.
Covers 14,650 rows (56.8% of table). Used for budget analysis and carryover correlation queries.';

-- =====================================================================
-- SECTION 2: MEDIUM PRIORITY - budget_program.subtitle_id Partial Index
-- =====================================================================
-- Rationale: High coverage (93.4% of budget_program rows have subtitle_id)
-- Large table: 25,755 rows, 46 MB
-- Query pattern: Budget classification by subtitle (Subtítulo 24, 31, 33, etc.)
-- Impact: Moderate (will improve budget classification queries)
-- =====================================================================

CREATE INDEX CONCURRENTLY idx_budget_program_subtitle
ON core.budget_program (subtitle_id)
WHERE subtitle_id IS NOT NULL;

COMMENT ON INDEX core.idx_budget_program_subtitle IS
'Partial index for budget program subtitle classification.
Covers 24,058 rows (93.4% of table). Used for budget classification and financial reporting queries.';

-- =====================================================================
-- SECTION 3: RECOMMENDED - magnitude.numeric_value Partial Index
-- =====================================================================
-- Rationale: Frequent high-value transfers (>1M) filtered in reporting
-- Current: Seq scan on partitions (acceptable for small partitions)
-- Future: As txn.magnitude grows, this index will prevent performance degradation
-- =====================================================================

-- Note: Index created per partition due to table partitioning
CREATE INDEX CONCURRENTLY idx_magnitude_2026_q1_high_value
ON txn.magnitude_2026_q1 (numeric_value)
WHERE numeric_value > 1000000;

CREATE INDEX CONCURRENTLY idx_magnitude_2026_q2_high_value
ON txn.magnitude_2026_q2 (numeric_value)
WHERE numeric_value > 1000000;

CREATE INDEX CONCURRENTLY idx_magnitude_2026_q3_high_value
ON txn.magnitude_2026_q3 (numeric_value)
WHERE numeric_value > 1000000;

CREATE INDEX CONCURRENTLY idx_magnitude_2026_q4_high_value
ON txn.magnitude_2026_q4 (numeric_value)
WHERE numeric_value > 1000000;

CREATE INDEX CONCURRENTLY idx_magnitude_default_high_value
ON txn.magnitude_default (numeric_value)
WHERE numeric_value > 1000000;

COMMENT ON INDEX txn.idx_magnitude_2026_q1_high_value IS
'Partial index for high-value magnitude filtering (>1M).
Used for financial audit queries and outlier detection. Covers ~30% of magnitude records.';

-- =====================================================================
-- SECTION 4: OPTIONAL - budget_carryover Composite Index
-- =====================================================================
-- Rationale: Fiscal year range queries with program joins
-- Current performance: 6ms (acceptable)
-- Recommendation: Add if carryover queries become frequent in dashboards
-- =====================================================================

-- Uncomment if carryover analysis queries become performance bottlenecks:
-- CREATE INDEX CONCURRENTLY idx_budget_carryover_year_amount
-- ON core.budget_carryover (fiscal_year, amount DESC)
-- WHERE amount > 0;
--
-- COMMENT ON INDEX core.idx_budget_carryover_year_amount IS
-- 'Composite index for carryover year-over-year analysis with amount sorting.';

-- =====================================================================
-- SECTION 5: MONITORING - Existing Index Usage Verification
-- =====================================================================

DO $$
BEGIN
    RAISE NOTICE '=== INDEX CREATION SUMMARY ===';
    RAISE NOTICE 'Created: idx_budget_program_year_item_allocation (CRITICAL)';
    RAISE NOTICE 'Created: idx_budget_program_subtitle (MEDIUM)';
    RAISE NOTICE 'Created: idx_magnitude_*_high_value (5 partitions, RECOMMENDED)';
    RAISE NOTICE '';
    RAISE NOTICE 'SKIPPED (already optimal):';
    RAISE NOTICE '  - idx_person_estamento (99.1% coverage, <1ms queries)';
    RAISE NOTICE '  - idx_agreement_technical_referent (1.3% coverage, partial index exists)';
    RAISE NOTICE '  - idx_budget_carryover_year (excellent selectivity)';
    RAISE NOTICE '  - idx_org_rut (unique index, <0.1ms queries)';
    RAISE NOTICE '';
    RAISE NOTICE 'SKIPPED (table too small or unpopulated):';
    RAISE NOTICE '  - person.person_type_id (111 rows, seq scan faster)';
    RAISE NOTICE '  - person.role_id (0% coverage)';
    RAISE NOTICE '  - agreement.agreement_type_id (533 rows, seq scan faster)';
    RAISE NOTICE '  - budget_program.owner_division_id (0% coverage)';
    RAISE NOTICE '  - budget_program.program_type_id (0.01% coverage)';
    RAISE NOTICE '';
    RAISE NOTICE 'Run ANALYZE on affected tables...';
END $$;

-- =====================================================================
-- SECTION 6: POST-INDEX MAINTENANCE
-- =====================================================================

ANALYZE core.budget_program;
ANALYZE txn.magnitude_2026_q1;
ANALYZE txn.magnitude_2026_q2;
ANALYZE txn.magnitude_2026_q3;
ANALYZE txn.magnitude_2026_q4;
ANALYZE txn.magnitude_default;

-- =====================================================================
-- SECTION 7: VERIFICATION QUERIES
-- =====================================================================

DO $$
DECLARE
    idx_count INTEGER;
BEGIN
    -- Verify budget_program composite index
    SELECT COUNT(*) INTO idx_count
    FROM pg_indexes
    WHERE schemaname = 'core'
    AND tablename = 'budget_program'
    AND indexname = 'idx_budget_program_year_item_allocation';

    IF idx_count = 1 THEN
        RAISE NOTICE 'OK: idx_budget_program_year_item_allocation created successfully';
    ELSE
        RAISE WARNING 'FAILED: idx_budget_program_year_item_allocation not found';
    END IF;

    -- Verify budget_program subtitle index
    SELECT COUNT(*) INTO idx_count
    FROM pg_indexes
    WHERE schemaname = 'core'
    AND tablename = 'budget_program'
    AND indexname = 'idx_budget_program_subtitle';

    IF idx_count = 1 THEN
        RAISE NOTICE 'OK: idx_budget_program_subtitle created successfully';
    ELSE
        RAISE WARNING 'FAILED: idx_budget_program_subtitle not found';
    END IF;

    -- Verify magnitude indexes
    SELECT COUNT(*) INTO idx_count
    FROM pg_indexes
    WHERE schemaname = 'txn'
    AND indexname LIKE 'idx_magnitude_%_high_value';

    IF idx_count = 5 THEN
        RAISE NOTICE 'OK: All 5 magnitude partition indexes created successfully';
    ELSE
        RAISE WARNING 'WARNING: Expected 5 magnitude indexes, found %', idx_count;
    END IF;
END $$;

COMMIT;

-- =====================================================================
-- PERFORMANCE TESTING QUERIES
-- =====================================================================

-- Run these queries to verify index usage (use EXPLAIN ANALYZE):

-- Test 1: Budget program composite filter (should use new composite index)
/*
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM core.budget_program bp
WHERE bp.fiscal_year BETWEEN 2023 AND 2025
  AND bp.item_id IS NOT NULL
  AND bp.allocation_id IS NOT NULL;
-- Expected: Index Scan using idx_budget_program_year_item_allocation
-- Before: 53.8ms (Seq Scan), After: <5ms (Index Scan)
*/

-- Test 2: High-value magnitude filter (should use new partial index)
/*
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.*
FROM txn.magnitude m
WHERE m.numeric_value > 1000000
  AND m.occurred_at >= '2026-01-01'
LIMIT 100;
-- Expected: Index Scan using idx_magnitude_*_high_value
-- Before: 0.3ms (Seq Scan on small partition), After: <0.2ms (Index Scan)
*/

-- Test 3: Budget carryover with program join (should use existing indexes)
/*
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    bc.fiscal_year,
    bc.amount,
    bp.code
FROM core.budget_carryover bc
JOIN core.budget_program bp ON bc.budget_program_id = bp.id
WHERE bc.fiscal_year BETWEEN 2023 AND 2025
ORDER BY bc.amount DESC
LIMIT 100;
-- Expected: Index Scan using idx_budget_carryover_year + Nested Loop
-- Performance: ~6ms (acceptable without additional index)
*/

-- =====================================================================
-- MAINTENANCE SCHEDULE
-- =====================================================================

-- Quarterly: Check index bloat and reindex if needed
/*
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'core'
AND indexname LIKE 'idx_budget_program%'
ORDER BY pg_relation_size(indexrelid) DESC;
*/

-- Quarterly: Monitor index usage statistics
/*
SELECT
    schemaname,
    relname,
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname IN ('core', 'txn')
AND indexrelname IN (
    'idx_budget_program_year_item_allocation',
    'idx_magnitude_2026_q1_high_value'
)
ORDER BY idx_scan DESC;
*/

-- =====================================================================
-- ROLLBACK SCRIPT (if needed)
-- =====================================================================
/*
-- Execute only if performance issues detected after index creation:

DROP INDEX CONCURRENTLY IF EXISTS core.idx_budget_program_year_item_allocation;
DROP INDEX CONCURRENTLY IF EXISTS core.idx_budget_program_subtitle;
DROP INDEX CONCURRENTLY IF EXISTS txn.idx_magnitude_2026_q1_high_value;
DROP INDEX CONCURRENTLY IF EXISTS txn.idx_magnitude_2026_q2_high_value;
DROP INDEX CONCURRENTLY IF EXISTS txn.idx_magnitude_2026_q3_high_value;
DROP INDEX CONCURRENTLY IF EXISTS txn.idx_magnitude_2026_q4_high_value;
DROP INDEX CONCURRENTLY IF EXISTS txn.idx_magnitude_default_high_value;
*/

-- =====================================================================
-- END OF SCRIPT
-- =====================================================================
