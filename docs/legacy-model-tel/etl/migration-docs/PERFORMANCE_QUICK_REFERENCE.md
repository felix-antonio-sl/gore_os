# Performance Optimization Quick Reference

**Post-Normalization v3.0** | **2026-01-30**

---

## 🚀 One-Liner Execution

```bash
docker exec goreos_db psql -U goreos -d goreos_model -f /Users/felixsanhueza/Developer/goreos/etl/migration/sql/optimize_indexes_post_normalization_v3.sql
```

**Duration**: ~10 minutes | **Disk**: +3 MB | **Downtime**: 0 (CONCURRENTLY)

---

## 📊 Critical Metrics (Before → After)

| Query | Before | After | Improvement |
|-------|--------|-------|-------------|
| Budget composite filter | 53.9ms | <5ms | **90%** |
| Budget subtitle filter | ~15ms | <3ms | **80%** |
| High-value magnitude | 0.31ms | <0.2ms | **35%** |

---

## 🎯 Indexes Created (7 total)

### CRITICAL Priority
- `idx_budget_program_year_item_allocation` (1.5 MB)
  - Covers: fiscal_year + item_id + allocation_id filters
  - Impact: Daily budget dashboards

### MEDIUM Priority
- `idx_budget_program_subtitle` (1 MB)
  - Covers: 93.4% of budget_program (24K rows)
  - Impact: Budget classification queries

### RECOMMENDED Priority
- `idx_magnitude_*_high_value` (5 partitions, 500 KB)
  - Covers: numeric_value > 1M (30% of magnitude)
  - Impact: Future-proofing for audit queries

---

## ✅ Pre-Flight Checklist

- [ ] Verify 20% free disk space (`df -h`)
- [ ] Backup database (`pg_dump`)
- [ ] Execute during off-peak hours (recommended: 22:00-06:00)
- [ ] Monitor `pg_stat_activity` during execution

---

## 🔍 Verification Queries

```sql
-- 1. Check indexes created
SELECT indexname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
WHERE indexrelname IN (
    'idx_budget_program_year_item_allocation',
    'idx_budget_program_subtitle',
    'idx_magnitude_2026_q1_high_value'
);

-- 2. Test performance improvement
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM core.budget_program
WHERE fiscal_year BETWEEN 2023 AND 2025
  AND item_id IS NOT NULL
  AND allocation_id IS NOT NULL;
-- Expected: Index Scan, <5ms execution

-- 3. Check index usage (run after 24h)
SELECT
    indexrelname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
WHERE indexrelname LIKE 'idx_budget_program%'
ORDER BY idx_scan DESC;
```

---

## 🔄 Rollback (if needed)

```sql
DROP INDEX CONCURRENTLY IF EXISTS core.idx_budget_program_year_item_allocation;
DROP INDEX CONCURRENTLY IF EXISTS core.idx_budget_program_subtitle;
DROP INDEX CONCURRENTLY IF EXISTS txn.idx_magnitude_2026_q1_high_value;
DROP INDEX CONCURRENTLY IF EXISTS txn.idx_magnitude_2026_q2_high_value;
DROP INDEX CONCURRENTLY IF EXISTS txn.idx_magnitude_2026_q3_high_value;
DROP INDEX CONCURRENTLY IF EXISTS txn.idx_magnitude_2026_q4_high_value;
DROP INDEX CONCURRENTLY IF EXISTS txn.idx_magnitude_default_high_value;
```

**Recovery time**: <2 minutes (no downtime)

---

## 📝 Maintenance Schedule

### Daily (Automated)
- Monitor slow query log

### Weekly
- Check index usage: `SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;`

### Monthly
- `ANALYZE core.budget_program;`

### Quarterly
- Check index bloat
- Review new query patterns
- Consider REINDEX if bloat >30%

---

## 🚨 Troubleshooting

### Issue: "Index creation hanging"
**Cause**: Conflicting locks
**Solution**: Check `pg_locks`, kill blocking queries, retry

### Issue: "Disk space full"
**Cause**: Insufficient space for index creation
**Solution**: Free 5 GB, retry with CONCURRENTLY

### Issue: "Query still slow after index"
**Cause**: PostgreSQL not using new index (stale statistics)
**Solution**: `ANALYZE core.budget_program;` then `SET enable_seqscan = OFF;` (test only)

---

## 📚 Documentation

- **Full Report**: `PERFORMANCE_AUDIT_v3.0_REPORT.md` (23 KB, 11 sections)
- **Summary**: `PERFORMANCE_AUDIT_v3.0_SUMMARY.md` (6 KB, executive summary)
- **SQL Script**: `sql/optimize_indexes_post_normalization_v3.sql` (11 KB, production-ready)

---

## 🔗 Related Files

- Normalization Report: `NORMALIZACION_v2.0_REPORTE_FINAL.md`
- Categorical Audit: `../../docs/AUDITORIA_CATEGORIAL_v3.0.md`
- Data Dictionary: `IPR_NEW_COLUMNS_DATA_DICT_v2.md`

---

**Agent**: arquitecto-gore (CM-AUDIT-ENGINE)
**Mode**: PERFORMANCE
**Status**: ✅ READY FOR PRODUCTION
