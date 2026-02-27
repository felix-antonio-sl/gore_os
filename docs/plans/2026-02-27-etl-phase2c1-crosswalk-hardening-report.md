# ETL Phase 2C.1 — Rendition Crosswalk Hardening Report (2026-02-27)

## Objective
Harden rendition linkage so `core.rendition` inserts occur only with explicit, validated crosswalk evidence.

## Delivered
- Added crosswalk generator:
  - `api/scripts/etl/generate_rendition_crosswalk.py`
  - Default output: `/app/data/etl/crosswalk/rendition_agreement_crosswalk.csv`
  - Preserves manual fields (`agreement_*`, `renderer_*`, `status`, `confidence`, `notes`) by normalized `legacy_codigo`.
- Extended transactional loader:
  - `api/scripts/etl/load_admin_acts.py`
  - New flags:
    - `--rendition-crosswalk`
    - `--allow-fallback-direct-match` (off by default)
  - Crosswalk validation for `approved` rows:
    - duplicate `legacy_codigo` detection
    - `agreement_id` existence
    - `agreement_number` existence
    - `agreement_id`/`agreement_number` consistency
  - Strict behavior: with `--insert-renditions-if-linked`, missing/invalid crosswalk now aborts with non-zero exit.
- Added staging support:
  - `scripts/stage_etl_data.sh crosswalk`
  - Copies canonical source:
    - `docs/legacy/etl/sources/partes/crosswalk/rendition_agreement_crosswalk.csv`
    - -> `api/data/etl/crosswalk/rendition_agreement_crosswalk.csv`
- Updated staging docs:
  - `api/data/README.md`
  - `docs/ETL_DATA_BOUNDARY.md`

## Validation
- `./scripts/stage_etl_data.sh crosswalk` -> staged OK.
- `docker compose exec api python -m scripts.etl.generate_rendition_crosswalk --out /app/data/etl/crosswalk/rendition_agreement_crosswalk.csv`
  - `Rows: 1935 | approved: 0 | auto_candidate_count=1: 0`
- Strict dry-run with staged crosswalk:
  - `docker compose exec api python -m scripts.etl.load_admin_acts --dry-run --limit 100 --insert-renditions-if-linked`
  - Result: `errors=0`, `renditions_linked=0`, `renditions_unresolved=100`.
- Strict dry-run with missing crosswalk:
  - `docker compose exec api python -m scripts.etl.load_admin_acts --dry-run --limit 10 --insert-renditions-if-linked --rendition-crosswalk /app/data/etl/crosswalk/does_not_exist.csv`
  - Result: explicit crosswalk errors + process exits with code `1`.
- Live run with staged crosswalk:
  - `docker compose exec api python -m scripts.etl.load_admin_acts --insert-renditions-if-linked`
  - Result: `inserted=0`, `skipped=5213`, `errors=0`.

## Current Data Status
- Canonical crosswalk exists in repo with `1935` legacy codes.
- No rows are currently `approved`, so live rendition inserts remain intentionally `0`.
