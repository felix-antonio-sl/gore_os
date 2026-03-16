# ETL Phase 2 — PARTES → core.document

**Date**: 2026-02-26
**Status**: Approved
**Author**: Arquitecto Categórico v3.0.0

## Categorical Framing

Functor `F: C_PARTES → C_DB(core.document)` with 6 source objects (CSV files) and 1 target object (core.document table). Morphisms are column mappings; composition is FK resolution via ref.category cache.

Tension resolved: **A1[Evento ↔ Entidad]** → documents are institutional records (entities), not events. Each CSV row maps 1:1 to a core.document record. Idempotence via `ON CONFLICT(code) DO NOTHING`.

## Scope

**In scope — Phase 2:**
- `load_documents.py`: 6 PARTES CSV sources → `core.document` (~10,528 rows)
- `goreos_seed_etl_phase2.sql`: seed `document_channel` scheme (4 codes)

**Out of scope — Phase 3 (separate):**
- `load_resolutions.py`: RESOLUCIONES EXENTAS + AFECTAS → `core.administrative_act` + `core.resolution`
- RENDICIONES → `core.rendition` (Phase 7)

## Phase 0: Seed document_channel

New scheme needed (not in ref.category):

```sql
INSERT INTO ref.category (scheme, code, label) VALUES
  ('document_channel', 'EMAIL',      'Email'),
  ('document_channel', 'PAPEL',      'Papel físico'),
  ('document_channel', 'DOCDIGITAL', 'Documento digital'),
  ('document_channel', 'OTRO',       'Otro')
ON CONFLICT (scheme, code) DO NOTHING;
```

Note: `document_type` scheme already exists with 12 codes — no changes needed.

## Source Inventory

| File | Prefix | ID Column | ~Rows | Key columns |
|------|--------|-----------|-------|-------------|
| RECIBIDOS.csv | `REC` | `C` | 7,180 | VIA RECEPCIÓN, TIPO DE DOCUMENTO, FECHA DOCUMENTO, FECHA RECEPCIÓN, REMITENTE, DESTINATARIO, MATERIA, DERIVADO A |
| OFICIOS.csv | `OFI` | `f` | 2,038 | TIPO DE DCTO, FECHA DCTO, REMITENTE, DESTINATARIO, MATERIA, LINK AL DOCUMENTO |
| MEMOS.csv | `MEM` | `FOLIO` | 1,292 | DE, PARA, MATERIA, FIRMA, VÍA DESPACHO, LINK AL DOCUMENTO |
| CARTAS.csv | `CAR` | `NUMERO DOCUMENTO` | 6 | FECHA DCTO, REMITENTE, DESTINATARIO, MATERIA, LINK AL DOCUMENTO |
| MEMOS INTERNOS.csv | `MEI` | `FOLIO` | 9 | DIVISIÓN, FOLIO, MATERIA, FIRMA, LINK AL DOCUMENTO |
| OFICIOS INTERNOS.csv | `OFI-INT` | row_number | 3 | NÚMERO DOCUMENTO, MATERIA, REMITENTE, DESTINATARIO |

## Target Schema: core.document

```
id UUID PK
code VARCHAR(64) UNIQUE          ← {PREFIX}-{ID}, idempotency key
name TEXT NOT NULL               ← MATERIA
document_type_id UUID FK         ← ref.category(scheme='document_type')
storage_url TEXT                 ← LINK AL DOCUMENTO
metadata JSONB                   ← all remaining fields
created_at / updated_at / deleted_at
```

## Column Mapping

### code (idempotency key)
```
{PREFIX}-{ID_value}
If ID is empty or duplicate within source: {PREFIX}-{row_number}
Examples: REC-1234, OFI-610, MEM-01236, CAR-00004
```

### document_type_id
Normalize raw tipo → document_type code via TYPE_MAP:

```python
TYPE_MAP = {
    "oficio":          "OTRO",
    "oficio circular": "OTRO",
    "memo":            "OTRO",
    "memo interno":    "OTRO",
    "carta":           "OTRO",
    "resolucion":      "RESOLUCION",
    "convenio":        "CONVENIO",
    "factura":         "FACTURA",
    "orden de compra": "ORDEN_COMPRA",
    # default:         "OTRO"
}
```

### metadata JSONB (all sources)
```json
{
  "tipo_original": "OFICIO",
  "remitente": "...",
  "destinatario": "...",
  "fecha_documento": "2024-01-15",
  "fecha_recepcion": "2024-01-15",
  "fecha_entrega": "2024-01-20",
  "via": "EMAIL",
  "derivado_a": "DAF",
  "solicita": "acv",
  "firma": "GONZALO SEPÚLVEDA",
  "observaciones": "...",
  "_etl_source": "RECIBIDOS.csv",
  "_etl_date": "2026-02-26"
}
```

## Data Quality Handling

| Issue | Strategy |
|-------|----------|
| Duplicate C in RECIBIDOS (~30) | suffix: REC-1234 → REC-1234-2, REC-1234-3 |
| Date anomalies (year 2044, 2054) | parse_date() returns None, store raw in metadata |
| Empty MATERIA | Use "(Sin materia)" as placeholder for NOT NULL constraint |
| Channel variants (EMAIL/E-MAIL) | normalize_text() collapses to canonical form |
| Numeric ID as float (610.0) | strip .0 before building code |

## CLI Interface

```bash
# Full run (all 6 sources)
docker compose exec api python -m scripts.etl.load_documents --dry-run
docker compose exec api python -m scripts.etl.load_documents

# Single source
docker compose exec api python -m scripts.etl.load_documents --source RECIBIDOS

# Standard flags (inherited from common.py)
--dry-run    # log without writing
--limit N    # first N rows only
--verbose    # debug logging
--data-dir   # override CSV directory
```

## Idempotence

`INSERT INTO core.document (...) ON CONFLICT (code) DO NOTHING`

Re-running produces 0 inserts (all skipped), 0 errors. Safe for repeated execution.

## Verification Queries (Post-ETL)

```sql
-- Count by source
SELECT metadata->>'_etl_source' AS source, COUNT(*)
FROM core.document WHERE deleted_at IS NULL
GROUP BY 1 ORDER BY 2 DESC;

-- Count by document type
SELECT c.code, c.label, COUNT(*)
FROM core.document d
JOIN ref.category c ON c.id = d.document_type_id
WHERE d.deleted_at IS NULL
GROUP BY c.code, c.label ORDER BY 3 DESC;

-- Storage URL coverage
SELECT COUNT(*) AS total,
       COUNT(storage_url) AS with_url,
       ROUND(100.0 * COUNT(storage_url) / COUNT(*), 1) AS pct
FROM core.document WHERE deleted_at IS NULL;
```
