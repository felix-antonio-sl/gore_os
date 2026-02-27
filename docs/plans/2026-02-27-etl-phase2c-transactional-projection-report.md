# ETL Phase 2C — Transactional Projection Report (2026-02-27)

## Objective
Project Phase 2B document records into transactional legal entities while preserving identity by document code.

Projection executed:
- `core.document` (sources: `RESOLUCIONES AFECTAS.csv`, `RESOLUCIONES EXENTAS.csv`)
  -> `core.administrative_act`
  -> `core.resolution`
- Renditions were audited for linkability to `core.agreement`.

## Implementation
Script added:
- `api/scripts/etl/load_admin_acts.py`

Idempotency strategy:
- administrative act key: `metadata.document_code = core.document.code`
- resolution key: `UNIQUE(administrative_act_id)`
- rendition key (when used): `metadata.document_code`

## Execution Results
### Resolutions -> transactional entities
- `core.administrative_act`: `1421` rows inserted
- `core.resolution`: `1421` rows inserted
- Source split:
  - `RESOLUCIONES EXENTAS.csv`: `1258`
  - `RESOLUCIONES AFECTAS.csv`: `163`

### Inferred resolution type distribution
- `APROBATORIA`: `1220`
- `MODIFICATORIA`: `139`
- `DESIGNACION`: `61`
- `DELEGACION`: `1`

### Renditions linkability audit
- Rendition documents analyzed: `2371`
- Agreements with number: `537`
- Direct normalized code matches (`legacy codigo` vs `agreement_number`): `0`
- Result: no safe linkage available, so `core.rendition` insertions remained `0`.

## Idempotency Check
Re-run results:
- `Inserted: 0`
- `Skipped: 5213`
- `Errors: 0`

## Notes
- This projection intentionally avoids fabricating `agreement_id` for renditions.
- A future Phase 2C.1 should define a deterministic crosswalk between legacy rendition codes (`2301...`) and `core.agreement` identities.
