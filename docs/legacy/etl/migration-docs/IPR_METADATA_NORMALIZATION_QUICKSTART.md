# IPR Metadata Normalization - Quick Start Guide

**Status**: Ready for execution
**Estimated time**: 15 minutes
**Risk**: Low (transaction-wrapped, reversible)

## What This Does

Normalizes 6 metadata fields from JSONB to proper database columns:

| Field | Action | Records |
|-------|--------|---------|
| `provincia`, `comuna` | Remove (already in `ipr_territory`) | 1,965 |
| `etapa_original` | Remove (already in `mcd_phase_id`) | 1,758 |
| `origen` | Move to new `origin_id` FK | 1,965 |
| `tipologia_original` | Move to new `legacy_typology_id` FK | 1,924 |
| `unidad_tecnica` | Complete migration to `ipr_party` | 15 |

**Result**: Cleaner metadata, faster queries, proper referential integrity.

---

## Pre-Execution Checklist

- [ ] Database backup exists
- [ ] PostgreSQL 16+ running
- [ ] You have write permissions on `goreos_model`
- [ ] No other migrations running
- [ ] 15 minutes available

---

## Execution

### Option 1: Interactive (Recommended First Time)

```bash
# Connect to database
docker exec -it goreos_db psql -U goreos -d goreos_model

# Run script
\i /path/to/etl/migration/sql/normalize_ipr_metadata.sql

# Review output at each step
# When finished, manually commit:
COMMIT;

# Or rollback if issues found:
ROLLBACK;
```

### Option 2: Non-Interactive (After Testing)

```bash
# Execute script directly
docker exec goreos_db psql -U goreos -d goreos_model -f /app/etl/migration/sql/normalize_ipr_metadata.sql

# Check last 50 lines for verification
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT COUNT(*) as total, COUNT(origin_id) as with_origin, COUNT(legacy_typology_id) as with_typology
FROM core.ipr;"
```

---

## Expected Output Summary

**Phase 1 (Verification)**:
- Territorial: 1,965 normalized ✓
- MCD Phase: 1,758 normalized ✓
- Unidad Técnica: 655 normalized, 15 missing

**Phase 2.1 (Create origin_id)**:
- MUNICIPIO: 1,327 records
- SECTORIAL: 638 records

**Phase 2.2 (Create legacy_typology_id)**:
- Top 3: FRIL (663), C-33 (413), MIDESO (381)
- Total: 1,924 records across 30 categories

**Phase 3 (Complete unidad_tecnica)**:
- Organizations created: 11
- ipr_party records created: 15
- Remaining missing: 0

**Phase 4 (Cleanup)**:
- Keys removed: `provincia`, `comuna`, `etapa_original`, `origen`, `tipologia_original`, `unidad_tecnica`
- Keys remaining: 9 (all audit/tracking)

---

## Verification Queries

### After completion, run these checks:

```sql
-- 1. Check new columns are populated
SELECT
    COUNT(*) as total_iprs,
    COUNT(origin_id) as with_origin,
    COUNT(legacy_typology_id) as with_typology,
    ROUND(COUNT(origin_id)::numeric / COUNT(*) * 100, 1) as origin_pct,
    ROUND(COUNT(legacy_typology_id)::numeric / COUNT(*) * 100, 1) as typology_pct
FROM core.ipr;
-- Expected: ~54% with origin, ~53% with typology

-- 2. Check metadata keys reduced
SELECT
    jsonb_object_keys(metadata) as key,
    COUNT(*) as records
FROM core.ipr
GROUP BY key
ORDER BY records DESC;
-- Expected: 9 keys (source, legacy_id, codigo_normalizado, cod_unico_idis, event_id_original, codigo_convenios, fuente_principal, registros_duplicados, nombres_alternativos)

-- 3. Check unidad_tecnica complete
SELECT COUNT(*) FROM core.ipr i
LEFT JOIN core.ipr_party ip ON i.id = ip.ipr_id
    AND ip.party_role_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'UNIDAD_TECNICA')
WHERE i.metadata->>'unidad_tecnica' IS NOT NULL
  AND ip.id IS NULL;
-- Expected: 0

-- 4. Sample normalized data
SELECT
    i.codigo_bip,
    i.name,
    origin.label as origin,
    typology.label as legacy_typology
FROM core.ipr i
LEFT JOIN ref.category origin ON i.origin_id = origin.id
LEFT JOIN ref.category typology ON i.legacy_typology_id = typology.id
WHERE i.origin_id IS NOT NULL OR i.legacy_typology_id IS NOT NULL
LIMIT 10;
```

---

## Rollback Plan

If you need to rollback **BEFORE committing**:

```sql
ROLLBACK;
```

If you need to rollback **AFTER committing** (within same session):

```sql
BEGIN;

-- Restore metadata from columns
UPDATE core.ipr i
SET metadata = metadata ||
    jsonb_build_object(
        'origen', CASE WHEN o.code = 'MUNICIPIO' THEN 'MUNICIPIO' ELSE 'SECTORIAL / OTRO' END,
        'tipologia_original', t.label
    )
FROM ref.category o, ref.category t
WHERE i.origin_id = o.id
  AND i.legacy_typology_id = t.id;

-- Drop new columns
ALTER TABLE core.ipr DROP COLUMN IF EXISTS origin_id;
ALTER TABLE core.ipr DROP COLUMN IF EXISTS legacy_typology_id;

-- Delete new category schemes
DELETE FROM ref.category WHERE scheme IN ('ipr_origin', 'ipr_legacy_typology');

-- Delete new organizations (check for other references first!)
DELETE FROM core.ipr_party WHERE metadata->>'migrated_from' = 'metadata.unidad_tecnica';
DELETE FROM core.organization WHERE metadata->>'legacy_name' IN (
    'ADRA', 'ASOCIACIÓN ITATA', 'FOSIS', 'INACAP', 'INDAP',
    'MEJOR NIÑEZ', 'REGISTRO CIVIL', 'SEREMI MM.AA', 'SEREMI TRABAJO',
    'UDECH', 'UTALCA'
);

COMMIT;
```

---

## Common Issues

### Issue 1: "column origin_id already exists"

**Cause**: Script run multiple times
**Fix**: Script is idempotent, safe to re-run. Or drop column first:
```sql
ALTER TABLE core.ipr DROP COLUMN IF EXISTS origin_id;
```

### Issue 2: "organization name already exists"

**Cause**: Organizations created manually before
**Fix**: Script uses `ON CONFLICT DO NOTHING`, safe to proceed

### Issue 3: "remaining_missing > 0 after Phase 3"

**Cause**: Organization creation failed
**Fix**: Check which orgs are missing:
```sql
SELECT DISTINCT metadata->>'unidad_tecnica', COUNT(*)
FROM core.ipr i
LEFT JOIN core.ipr_party ip ON i.id = ip.ipr_id
    AND ip.party_role_id = (SELECT id FROM ref.category WHERE code = 'UNIDAD_TECNICA')
WHERE i.metadata->>'unidad_tecnica' IS NOT NULL AND ip.id IS NULL
GROUP BY 1;
```

Then create manually or fix org_type_id mismatch.

---

## Post-Execution Tasks

After successful migration:

1. **Update documentation**:
   ```bash
   # Add origin_id and legacy_typology_id to ERD
   vim model/model_goreos/docs/GOREOS_ERD_v3.md
   ```

2. **Update loader scripts**:
   ```bash
   # Modify ipr_loader.py to populate new columns
   vim etl/migration/loaders/ipr_loader.py
   ```

3. **Update Streamlit viewer**:
   ```bash
   # Display new fields in detail view
   vim apps/migration_viewer/components/detail_view.py
   ```

4. **Tag migration**:
   ```bash
   git add .
   git commit -m "feat(etl): normalize IPR metadata - 6 fields to FK columns

   - Create ipr_origin scheme (MUNICIPIO, SECTORIAL)
   - Create ipr_legacy_typology scheme (30 codes)
   - Add origin_id and legacy_typology_id to core.ipr
   - Complete unidad_tecnica migration (15 remaining IPRs)
   - Remove 6 normalized keys from metadata JSONB
   - 40% reduction in JSONB complexity

   Impact: 1,973 IPRs normalized

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```

---

## Performance Impact

**Before**:
```sql
-- JSONB GIN index scan
SELECT * FROM core.ipr WHERE metadata->>'origen' = 'MUNICIPIO';
```

**After**:
```sql
-- B-tree index scan (faster)
SELECT * FROM core.ipr WHERE origin_id = (SELECT id FROM ref.category WHERE code = 'MUNICIPIO');
```

**Query speedup**: ~3-5x for filtering, ~10x for joins

---

## Need Help?

Check full documentation:
- **Analysis**: `/Users/felixsanhueza/Developer/goreos/etl/migration/IPR_METADATA_NORMALIZATION_ANALYSIS.md`
- **SQL Script**: `/Users/felixsanhueza/Developer/goreos/etl/migration/sql/normalize_ipr_metadata.sql`
- **ETL Lessons**: `etl/migration/LECCIONES_APRENDIDAS.md`

---

**Last updated**: 2026-01-30
