# ETL Data Boundary

## Purpose
Keep repository code and canonical source data separated from runtime staging copies.

## Rules
- Canonical ETL sources live in `docs/legacy/etl/sources/`.
- Runtime staging data lives in `api/data/` and is local-only (ignored by git).
- ETL scripts read from `/app/data/etl/...` inside the API container.
- Before running ETL, stage required sources with `./scripts/stage_etl_data.sh`.

## Standard Workflow
1. Stage data locally:
   ```bash
   ./scripts/stage_etl_data.sh all
   ```
2. Run ETL dry-run:
   ```bash
   docker compose exec api python -m scripts.etl.load_documents --dry-run
   ```
3. Run live ETL when dry-run is clean.

## Scope Notes
- Phase 2 documents loader (`load_documents.py`) uses 6 PARTES files.
- Person enrichment (`enrich_persons.py`) uses NOMINA + TransparenciaActiva + listado integrated.
- Additional PARTES files (`RENDICIONES*`, `RESOLUCIONES*`) remain out of Phase 2 scope.
