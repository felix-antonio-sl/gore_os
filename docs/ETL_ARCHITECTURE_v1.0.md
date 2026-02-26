# ETL Architecture — Legacy CSV Integration

**Version**: 1.0
**Date**: 2026-02-26
**Status**: Design (no implementation yet)

## Overview

8 legacy CSV domains (14K+ documents, 270 agreements, 120 FRIL initiatives, 500 budget modifications, 2K+ staff records) need to flow into 7 DDL tables that are either empty or partially populated post-JSONB normalization.

## Source Inventory

| Domain | Source Path | Files | Records | Target Tables |
|--------|-----------|-------|---------|---------------|
| PARTES | `etl/sources/partes/originales/` | 10 CSVs | ~12,795 | core.document, core.resolution |
| CONVENIOS | `etl/sources/convenios/originales/` | 3 CSVs | ~544 | core.agreement (enrich) |
| FRIL | `etl/sources/fril/originales/` | 7 CSVs | ~120 | core.ipr_territory, core.ipr_milestone |
| MODIFICACIONES | `etl/sources/modificaciones/originales/` | 19 CSVs | ~500 lines | txn.event (BUDGET_MOD) |
| IDIS | `etl/sources/idis/originales/` | 6 CSVs | ~2,600 | core.ipr_party, core.ipr_territory |
| FUNCIONARIOS | `etl/sources/funcionarios/` | 1 CSV | ~2,000 | core.person (enrich) |
| PROGS | `etl/sources/progs/originales/` | 20 CSVs | ~3,000 | core.budget_program (enrich), core.rendition |
| 250 | `etl/sources/250/` | 2 CSVs | ~650 | TBD |

## Target Table State (Post-Normalization)

| Table | Current Records | Source for New Data |
|-------|----------------|---------------------|
| core.ipr_party | 6,447 | IDIS (ejecutor, postulante, UT) |
| core.ipr_territory | 3,570 | FRIL (comunas), IDIS (comunas) |
| core.ipr_milestone | 0 | FRIL (stage dates), DIPIR harvest |
| core.document | 0 | PARTES (recibidos, oficios, memos) |
| core.resolution | 0 | PARTES (res. exentas/afectas), CONVENIOS |
| core.rendition | 0 | PARTES (rendiciones), PROGS |
| core.risk | 0 | Division harvest (no CSV source) |

## ETL Architecture

### Runtime Environment

```
docker compose exec api python -m scripts.etl.<module> [--dry-run] [--limit N]
```

Scripts run inside the API container for network access to `goreos_db`. Each script is standalone with shared utilities.

### Directory Structure

```
api/scripts/etl/
  common.py          # DB connection, logging, dry-run, CSV reader
  load_documents.py  # PARTES -> core.document
  load_resolutions.py # PARTES -> core.resolution + core.administrative_act
  load_renditions.py  # PARTES + PROGS -> core.rendition
  enrich_agreements.py # CONVENIOS -> core.agreement (update existing)
  load_fril.py        # FRIL -> core.ipr_territory + core.ipr_milestone
  load_modifications.py # MODIFICACIONES -> txn.event
  enrich_persons.py   # FUNCIONARIOS -> core.person (update existing)
  load_idis.py        # IDIS -> core.ipr_party + core.ipr_territory
```

### Shared Module: `common.py`

```python
# Key functions:
async def get_db_session() -> AsyncSession
def read_csv(path: str, encoding='utf-8') -> list[dict]
def normalize_rut(rut: str) -> str  # XX.XXX.XXX-X format
def parse_date(s: str) -> date | None  # handles DD-MM-YYYY and YYYY-MM-DD
def parse_amount(s: str) -> Decimal | None  # strips $, dots, handles M$
async def resolve_org_by_rut(db, rut: str) -> UUID | None
async def resolve_org_by_name(db, name: str) -> UUID | None
async def resolve_ipr_by_bip(db, codigo_bip: str) -> UUID | None
async def resolve_territory_by_name(db, name: str) -> UUID | None
async def resolve_category(db, scheme: str, code: str) -> UUID | None
def log_stats(inserted: int, updated: int, skipped: int, errors: list)
```

### Common Patterns

1. **Dry-run first**: `--dry-run` logs what would happen without DB writes
2. **Idempotent**: Uses ON CONFLICT DO NOTHING or checks before insert
3. **FK resolution via subquery**: Never hardcode UUIDs, always resolve by code/name
4. **Batch processing**: Commits every 100 rows
5. **Error accumulation**: Collects errors, logs summary, doesn't abort on single row failure

## ETL Pipelines by Priority

### P1: PARTES -> core.document (5,858 + 1,898 + 1,236 = ~9,000 records)

**Source files**: RECIBIDOS.csv, OFICIOS.csv, MEMOS.csv

**Mapping**:
| CSV Column | Target Column | Transform |
|-----------|--------------|-----------|
| C (correlativo) | code | `DOC-REC-{C}`, `DOC-OFI-{C}`, `DOC-MEM-{C}` |
| MATERIA | name | Direct |
| TIPO DOC | document_type_id | Resolve via ref.category(`document_type`) |
| FECHA DOC | metadata.document_date | parse_date() |
| FECHA INGRESO | created_at | parse_date() |
| ORIGEN / DESTINATARIO | metadata.origin / metadata.recipient | Direct |
| DERIVADO A | metadata.routed_to | Direct |
| Link | storage_url | Direct (Google Drive link) |

**New scheme needed**: `document_type` with codes:
OFICIO_RECIBIDO, OFICIO_DESPACHADO, MEMO_INTERNO, CARTA, RESOLUCION_EXENTA, RESOLUCION_AFECTA, RENDICION, CERTIFICADO

### P2: PARTES -> core.resolution (~1,421 records)

**Source files**: RESOLUCIONES EXENTAS.csv, RESOLUCIONES AFECTAS.csv

**Mapping**:
| CSV Column | Target Column |
|-----------|--------------|
| N (numero) | resolution_number (in administrative_act) |
| FECHA | resolution_date |
| MATERIA | subject |
| TIPO | resolution_type_id → EXENTA or AFECTA |
| REF BIP (if present) | ipr_id via resolve_ipr_by_bip() |

**Dependencies**: Requires `core.administrative_act` INSERT first, then `core.resolution` with FK.

### P3: CONVENIOS enrichment (~544 records)

**Source files**: CONVENIOS 2023 y 2024.csv, CONVENIOS 2025.csv

**Strategy**: UPDATE existing `core.agreement` records (matched by agreement_number or codigo_bip). Don't create new agreements — only enrich metadata.

**Enrichment fields**:
- `cgr_outcome_id`: from RES. CGR column
- `technical_referent_id`: from REFERENTE TECNICO (resolve person by name)
- Resolution links: create `core.resolution` records linked to agreement
- CGR dates: `toma_razon_at` from FECHA TOMA RAZON

### P4: FRIL -> ipr_territory + ipr_milestone (~120 records)

**Source files**: 6 FRIL CSVs (31 + Fril groups)

**Territory mapping**: COMUNA column -> resolve_territory_by_name() -> insert into ipr_territory with impact_type=UBICACION

**Milestone mapping** (from CSV stage columns):
| Stage | milestone_type code |
|-------|-------------------|
| Adj. (Adjudicacion) | ADJUDICACION |
| Lic. (Licitacion) | LICITACION |
| Con. (Contratacion) | INICIO_OBRA |
| Para. (Paralizado) | (skip — not a milestone) |

### P5: MODIFICACIONES -> txn.event (~500 records)

**Source files**: 19 modification CSVs (cleaned version preferred)

**Strategy**: Each budget modification line becomes a `txn.event` with:
- event_type_id: resolve category `event_type` code `BUDGET_MODIFICATION`
- subject_type: `core.budget_program`
- subject_id: resolve by SUBT/ITEM/ASIG combination
- data JSONB: `{amount_pre, amount_post, amount_delta, modification_number}`

### P6: FUNCIONARIOS -> core.person enrichment (~2,000 records)

**Source file**: listado_funcionarios_integrado_remediado.csv

**Strategy**: UPDATE existing `core.person` records matched by RUT. Add:
- email (from institutional email column)
- phone
- estamento_id (resolve from ref.category)

**Note**: Currently 111/111 persons have no email. This is critical for notifications.

### P7: IDIS -> ipr_party + ipr_territory (best-effort)

**Source file**: ANALISIS.csv (most reliable of the IDIS files)

**Caution**: CONSOLIDADO and MASTER have severe data corruption (2,432–9,521 formula errors). Only use ANALISIS or the cleaned version.

**Party mapping**: COD. UNICO -> resolve IPR -> extract EJECUTOR, POSTULANTE, UT -> insert ipr_party

**Territory mapping**: COMUNA column -> resolve territory -> insert ipr_territory

## New Category Schemes Required

| Scheme | Codes | For Table |
|--------|-------|-----------|
| `document_type` | 8 codes (see P1) | core.document |
| `rendition_state` | PENDIENTE, EN_REVISION, APROBADA, RECHAZADA, OBSERVADA | core.rendition |
| `event_type` | BUDGET_MODIFICATION (+ existing) | txn.event |

**Insert script**: Create `goreos_seed_etl_schemes.sql` with category inserts before running ETL.

## Execution Order

```
Phase 0: Insert new category schemes (document_type, rendition_state)
Phase 1: FUNCIONARIOS enrichment (enables person FK resolution for later phases)
Phase 2: PARTES documents + resolutions (independent, high volume)
Phase 3: CONVENIOS enrichment (depends on resolutions from Phase 2)
Phase 4: FRIL territories + milestones (independent)
Phase 5: MODIFICACIONES events (independent)
Phase 6: IDIS party + territory enrichment (best-effort, after Phase 4)
Phase 7: RENDICIONES (depends on agreements from Phase 3)
```

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| IDIS data corruption | ANALISIS still has 140 errors | Use cleaned version, skip error rows |
| Duplicate organizations | Multiple name variants for same org | Fuzzy match + manual review list |
| Missing BIP codes | Some CSVs reference IPRs not in DB | Log skipped rows, don't fail |
| Date format inconsistency | Mix of DD-MM-YYYY and YYYY-MM-DD | parse_date() handles both |
| Large transaction size | 9K+ document inserts | Batch commits every 100 rows |
| Salary data in FUNCIONARIOS | Contains sensitive financial info | Only extract name/email/RUT/division |

## Verification Queries (Post-ETL)

```sql
-- Document counts by type
SELECT c.code AS doc_type, COUNT(*)
FROM core.document d
JOIN ref.category c ON c.id = d.document_type_id
GROUP BY c.code ORDER BY COUNT(*) DESC;

-- Resolutions with IPR links
SELECT COUNT(*) AS total, COUNT(ipr_id) AS linked
FROM core.resolution;

-- Person email coverage
SELECT COUNT(*) AS total,
       COUNT(email) AS with_email,
       ROUND(100.0 * COUNT(email) / COUNT(*), 1) AS pct
FROM core.person;

-- Territory coverage per IPR
SELECT COUNT(DISTINCT ipr_id) AS iprs_with_territory,
       (SELECT COUNT(*) FROM core.ipr WHERE deleted_at IS NULL) AS total_iprs
FROM core.ipr_territory WHERE deleted_at IS NULL;

-- Milestone coverage
SELECT c.code, COUNT(*)
FROM core.ipr_milestone im
JOIN ref.category c ON c.id = im.milestone_type_id
WHERE im.deleted_at IS NULL
GROUP BY c.code ORDER BY COUNT(*) DESC;
```
