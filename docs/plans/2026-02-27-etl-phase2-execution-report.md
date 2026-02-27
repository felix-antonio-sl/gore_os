# ETL Phase 2 — Execution Report (2026-02-27)

## Scope Executed
Loaded PARTES documents from these 6 CSV sources into `core.document`:
- `RECIBIDOS.csv`
- `OFICIOS.csv`
- `MEMOS.csv`
- `CARTAS.csv`
- `MEMOS INTERNOS.csv`
- `OFICIOS INTERNOS.csv`

## Implemented Artifacts
- `model/model_goreos/sql/goreos_seed_etl_phase2.sql`
- `api/scripts/etl/common.py` (`read_csv(..., skip_rows=0)`)
- `api/scripts/etl/load_documents.py`

## Database Verification

### 1) `document_channel` seed
```sql
SELECT code, label
FROM ref.category
WHERE scheme = 'document_channel'
ORDER BY code;
```
Result: 4 rows (`DOCDIGITAL`, `EMAIL`, `OTRO`, `PAPEL`).

### 2) Loaded rows by source
```sql
SELECT metadata->>'_etl_source' AS source, COUNT(*)
FROM core.document
WHERE deleted_at IS NULL
GROUP BY 1 ORDER BY 2 DESC;
```
- `RECIBIDOS.csv`: 5858
- `OFICIOS.csv`: 1898
- `MEMOS.csv`: 1236
- `MEMOS INTERNOS.csv`: 9
- `CARTAS.csv`: 5
- `OFICIOS INTERNOS.csv`: 2

Total loaded in Phase 2 scope: **9008**.

### 3) Type distribution
```sql
SELECT c.code, c.label, COUNT(*)
FROM core.document d
JOIN ref.category c ON c.id = d.document_type_id
WHERE d.deleted_at IS NULL
GROUP BY c.code, c.label
ORDER BY 3 DESC;
```
Top categories:
- `OTRO`: 8403
- `RENDICION`: 364
- `RESOLUCION`: 119

### 4) `storage_url` coverage
```sql
SELECT COUNT(*) AS total,
       COUNT(storage_url) AS with_url,
       ROUND(100.0 * COUNT(storage_url) / COUNT(*), 1) AS pct_with_url
FROM core.document
WHERE deleted_at IS NULL;
```
- `total`: 9008
- `with_url`: 3137
- `pct_with_url`: 34.8

## Idempotency Verification
Re-ran full loader:
- `Inserted: 0`
- `Skipped: 9008`
- `Errors: 0`

This confirms `ON CONFLICT (code) DO NOTHING` behavior is stable.

## Why Total Is 9008 (and not ~10.5k)
The Phase 2 plan estimate used line-level expectations. Actual loader behavior is record-based (`csv.DictReader`) with:
- malformed first-row handling (`skip_rows`) for specific files,
- quoted multi-line fields,
- explicit filtering of fully empty rows.

Under these rules, parseable non-empty records for the 6 in-scope files equal exactly **9008**, matching DB counts.

## Out-of-Scope Files (Phase 2B candidates)
Found in source directory but not loaded in this phase:
- `RENDICIONES 2024.csv` (2335 non-empty)
- `RESOLUCIONES EXENTAS.csv` (1258 non-empty)
- `RESOLUCIONES AFECTAS.csv` (163 non-empty)
- `RENDICIONES FNDR Y ADNC.csv` (0 non-empty)

These should be addressed in a dedicated Phase 2B plan.
