# ETL Data Boundary

## Purpose
Keep repository code and canonical source data separated from runtime staging copies.

## Rules
- Canonical ETL sources live in `docs/archive/legacy-model-tel/etl/sources/`.
- Runtime staging data lives in `api/data/` and is local-only (ignored by git).
- ETL scripts read from `/app/data/etl/...` inside the API container.
- Before running ETL, stage required sources with `./scripts/stage_etl_data.sh`.

## Standard Workflow
1. Stage data locally:
   ```bash
   ./scripts/stage_etl_data.sh partes_full
   ./scripts/stage_etl_data.sh funcionarios
   ./scripts/stage_etl_data.sh contacts
   ./scripts/stage_etl_data.sh crosswalk
   ```
2. Run ETL dry-run:
   ```bash
   docker compose exec api python -m scripts.etl.load_documents --dry-run
   ```
3. Run live ETL when dry-run is clean.

## Scope Notes
- Phase 2 documents loader (`load_documents.py`) uses 6 PARTES files.
- Phase 2B documents extension adds 4 PARTES files (`RENDICIONES*`, `RESOLUCIONES*`).
- Person enrichment (`enrich_persons.py`) uses NOMINA + TransparenciaActiva + listado integrated.
- Email enrichment (`enrich_person_emails.py`) uses contacts CSV staged under `/app/data/etl/contacts/`.
- Rendition linkage for Phase 2C.1 uses crosswalk staged at `/app/data/etl/crosswalk/rendition_agreement_crosswalk.csv`.
