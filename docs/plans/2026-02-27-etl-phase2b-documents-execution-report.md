# ETL Phase 2B — Execution Report (2026-02-27)

## Scope Executed
Extended `load_documents.py` to ingest 4 additional PARTES sources into `core.document`:
- `RENDICIONES 2024.csv`
- `RENDICIONES FNDR Y ADNC.csv`
- `RESOLUCIONES AFECTAS.csv`
- `RESOLUCIONES EXENTAS.csv`

## Technical Changes
- Added new source configs in `api/scripts/etl/load_documents.py`:
  - `RENDICIONES_2024`
  - `RENDICIONES_FNDR_ADNC`
  - `RESOLUCIONES_AFECTAS`
  - `RESOLUCIONES_EXENTAS`
- Added custom parser `read_rendiciones_fndr_adnc()` for dual-block CSV layout.
- Preserved idempotency by `code` + `ON CONFLICT (code) DO NOTHING`.
- Extended staging script modes:
  - `partes2b`
  - `partes_full`

## Live Load Results (Phase 2B)
- `RENDICIONES_2024`: inserted `2334`
- `RENDICIONES_FNDR_ADNC`: inserted `37`
- `RESOLUCIONES_AFECTAS`: inserted `163`
- `RESOLUCIONES_EXENTAS`: inserted `1258`

**Total Phase 2B inserted:** `3792`

## Global Document Totals After Phase 2B
`core.document` by `_etl_source`:
- `RECIBIDOS.csv`: 5858
- `RENDICIONES 2024.csv`: 2334
- `OFICIOS.csv`: 1898
- `RESOLUCIONES EXENTAS.csv`: 1258
- `MEMOS.csv`: 1236
- `RESOLUCIONES AFECTAS.csv`: 163
- `RENDICIONES FNDR Y ADNC.csv`: 37
- `MEMOS INTERNOS.csv`: 9
- `CARTAS.csv`: 5
- `OFICIOS INTERNOS.csv`: 2

**Total `core.document`: `12800`**

## Type Distribution Impact
After Phase 2B:
- `RENDICION`: `2735`
- `RESOLUCION`: `1540`

## Idempotency Verification
Re-ran each Phase 2B source:
- `Inserted: 0`
- `Skipped: N` (full source cardinality)
- `Errors: 0`

## Notes
- This phase intentionally maps these records to `core.document` (documental layer), not `core.rendition` / `core.resolution` transactional entities.
- `RENDICIONES FNDR Y ADNC.csv` requires custom parsing due dual FNDR/ADNC blocks in one row.
