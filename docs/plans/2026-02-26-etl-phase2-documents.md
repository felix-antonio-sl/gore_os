# ETL Phase 2 — PARTES → core.document Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Load ~10,500 institutional documents from 6 PARTES CSV files into `core.document`.

**Architecture:** Each CSV source has a `SourceConfig` dataclass (prefix, header_row, column mapping). A shared `load_source()` coroutine applies the mapping and inserts via `ON CONFLICT(code) DO NOTHING`. `common.py` provides all DB/CSV utilities already.

**Tech Stack:** Python 3.11, asyncpg via SQLAlchemy async, `common.py` utilities already in `api/scripts/etl/`.

---

## Critical CSV Structural Quirks

Before writing any code, internalize these:

| Source | Quirk |
|--------|-------|
| RECIBIDOS | Row 0 = "ENROCADO" garbage. Row 1 = real headers. Data from row 2. |
| OFICIOS INTERNOS | Row 0 = "}" garbage. Row 1 = real headers. Data from row 2. |
| MEMOS | Column 0 has no header name (empty string). Skip it. |
| MEMOS INTERNOS | Column 0 has no header name (empty string). Skip it. |
| OFICIOS | Rows 1-2 are empty (blank separator). Skip empty rows in data. |
| CARTAS | Row 0 is empty. Data from row 1. |

The existing `read_csv()` in `common.py` reads via `csv.DictReader` using auto-detected delimiter/encoding. For files with garbage first rows, we need a `skip_rows` parameter.

---

## Task 1: Seed document_channel scheme

**Files:**
- Create: `model/model_goreos/sql/goreos_seed_etl_phase2.sql`

**Step 1: Write the SQL seed file**

```sql
-- model/model_goreos/sql/goreos_seed_etl_phase2.sql
-- Phase 2 ETL seed: document_channel scheme
-- Idempotent: ON CONFLICT DO NOTHING

INSERT INTO ref.category (scheme, code, label) VALUES
  ('document_channel', 'EMAIL',      'Email'),
  ('document_channel', 'PAPEL',      'Papel físico'),
  ('document_channel', 'DOCDIGITAL', 'Documento digital'),
  ('document_channel', 'OTRO',       'Otro')
ON CONFLICT (scheme, code) DO NOTHING;
```

**Step 2: Apply to production DB**

```bash
docker exec -i goreos_db psql -U goreos -d goreos_model \
  < model/model_goreos/sql/goreos_seed_etl_phase2.sql
```

Expected output:
```
INSERT 0 4
```

**Step 3: Verify**

```bash
docker exec goreos_db psql -U goreos -d goreos_model \
  -c "SELECT code, label FROM ref.category WHERE scheme = 'document_channel' ORDER BY code;"
```

Expected: 4 rows (DOCDIGITAL, EMAIL, OTRO, PAPEL).

**Step 4: Commit**

```bash
git add model/model_goreos/sql/goreos_seed_etl_phase2.sql
git commit -m "feat(etl): seed document_channel scheme for Phase 2"
```

---

## Task 2: Extend common.py with skip_rows support

The existing `read_csv()` always uses row 0 as header. We need to handle CSVs where row 0 is garbage.

**Files:**
- Modify: `api/scripts/etl/common.py` — add `skip_rows` param to `read_csv()`

**Step 1: Add skip_rows parameter**

Find the `read_csv()` function (around line 102). Add `skip_rows: int = 0` param and apply it:

```python
def read_csv(path: str | Path, encoding: str | None = None,
             delimiter: str | None = None,
             skip_rows: int = 0) -> list[dict]:
    """Read CSV with auto-detection of encoding and delimiter.

    skip_rows: number of rows to skip BEFORE the header row.
    Use for files with garbage first rows (e.g., RECIBIDOS.csv row 0 = 'ENROCADO').
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    encodings = [encoding] if encoding else _ENCODINGS
    delimiters = [delimiter] if delimiter else _DELIMITERS

    best_cols = 0
    best_enc = ""
    best_delim = ""

    for enc in encodings:
        try:
            with open(path, encoding=enc, newline="") as f:
                # Skip garbage rows for column detection
                for _ in range(skip_rows):
                    f.readline()
                sample = f.read(4096)
        except UnicodeDecodeError:
            continue

        for delim in delimiters:
            try:
                import io
                reader = csv.reader(io.StringIO(sample), delimiter=delim, quotechar='"')
                header = next(reader)
                ncols = len([h for h in header if h.strip()])
                if ncols > best_cols:
                    best_cols = ncols
                    best_enc = enc
                    best_delim = delim
            except (csv.Error, StopIteration):
                continue

    if best_cols < 3:
        raise ValueError(f"Could not read {path} with any encoding/delimiter combination")

    with open(path, encoding=best_enc, newline="") as f:
        # Skip garbage rows before header
        for _ in range(skip_rows):
            f.readline()
        reader = csv.DictReader(f, delimiter=best_delim, quotechar='"')
        rows = []
        for row in reader:
            cleaned = {}
            for k, v in row.items():
                key = k.strip().strip('"') if k else ""
                val = v.strip().strip('"') if v else ""
                if key:
                    cleaned[key] = val
            if any(cleaned.values()):  # Skip completely empty rows
                rows.append(cleaned)

    log.debug(f"Read {len(rows)} rows from {path.name} [{best_enc}, delim='{best_delim}', {best_cols} cols]")
    return rows
```

**Step 2: Copy updated script to container**

```bash
docker cp api/scripts goreos_api:/app/scripts
```

**Step 3: Quick smoke test**

```bash
docker compose exec api python3 -c "
from scripts.etl.common import read_csv
# RECIBIDOS has garbage row 0
rows = read_csv('/app/data/etl/partes/RECIBIDOS.csv', skip_rows=1)
print(f'RECIBIDOS: {len(rows)} rows, keys: {list(rows[0].keys())[:5]}')
"
```

Expected: `RECIBIDOS: ~7178 rows, keys: ['C', 'VIA RECEPCIÓN', 'NÚMERO DOCUMENTO', ...]`

**Step 4: Commit**

```bash
git add api/scripts/etl/common.py
git commit -m "feat(etl): add skip_rows param to read_csv for malformed headers"
```

---

## Task 3: Copy PARTES CSVs to container

**Step 1: Create data directory**

```bash
docker exec goreos_api mkdir -p /app/data/etl/partes
```

**Step 2: Copy all source files**

```bash
for f in "RECIBIDOS.csv" "OFICIOS.csv" "MEMOS.csv" "CARTAS.csv" \
         "MEMOS INTERNOS.csv" "OFICIOS INTERNOS.csv"; do
  docker cp "docs/legacy/etl/sources/partes/originales/$f" \
    goreos_api:"/app/data/etl/partes/$f"
done
echo "Done"
```

**Step 3: Verify**

```bash
docker exec goreos_api ls -la /app/data/etl/partes/
```

Expected: 6 CSV files listed.

---

## Task 4: Write load_documents.py

**Files:**
- Create: `api/scripts/etl/load_documents.py`

**Step 1: Write the full script**

```python
"""
ETL Phase 2 — Load PARTES CSVs → core.document.

Functor F: C_PARTES → C_DB(core.document)
  Objects: 6 CSV sources (RECIBIDOS, OFICIOS, MEMOS, CARTAS, MEMOS INTERNOS, OFICIOS INTERNOS)
  Morphisms: column mappings per source → core.document columns
  Idempotence: ON CONFLICT (code) DO NOTHING

Tension A1[Evento ↔ Entidad]: Documents are institutional records (entities),
not events. Each row maps 1:1 to one core.document. No colimit needed.

Usage:
  docker compose exec api python -m scripts.etl.load_documents --dry-run
  docker compose exec api python -m scripts.etl.load_documents
  docker compose exec api python -m scripts.etl.load_documents --source RECIBIDOS
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from sqlalchemy import text

from scripts.etl.common import (
    base_argparser,
    setup_logging,
    read_csv,
    parse_date,
    normalize_text,
    resolve_category,
    get_session,
    close_engine,
    batch_commit,
    ETLStats,
    run_async,
    log,
)

ETL_DATA_DIR = Path("/app/data/etl/partes")

# ---------------------------------------------------------------------------
# document_type mapping: normalized raw tipo → ref.category code
# ---------------------------------------------------------------------------

TYPE_MAP: dict[str, str] = {
    "oficio":              "OTRO",
    "oficio circular":     "OTRO",
    "oficio ord":          "OTRO",
    "ordinario":           "OTRO",
    "memo":                "OTRO",
    "memo interno":        "OTRO",
    "memorando":           "OTRO",
    "carta":               "OTRO",
    "resolucion":          "RESOLUCION",
    "resolucion exenta":   "RESOLUCION",
    "resolucion afecta":   "RESOLUCION",
    "convenio":            "CONVENIO",
    "factura":             "FACTURA",
    "boleta":              "BOLETA_GARANTIA",
    "orden de compra":     "ORDEN_COMPRA",
    "certificado":         "CERTIFICADO",
    "decreto":             "DECRETO",
    "informe":             "INFORME_TECNICO",
    "plano":               "PLANO",
    "rendicion":           "RENDICION",
}

CHANNEL_MAP: dict[str, str] = {
    "email":       "EMAIL",
    "e-mail":      "EMAIL",
    "mail":        "EMAIL",
    "papel":       "PAPEL",
    "fisico":      "PAPEL",
    "físico":      "PAPEL",
    "docdigital":  "DOCDIGITAL",
    "doc digital": "DOCDIGITAL",
    "digital":     "DOCDIGITAL",
}


def map_type(raw: str) -> str:
    """Map raw tipo string → document_type code. Default: OTRO."""
    return TYPE_MAP.get(normalize_text(raw), "OTRO")


def map_channel(raw: str) -> str:
    """Map raw canal string → document_channel code. Default: OTRO."""
    return CHANNEL_MAP.get(normalize_text(raw), "OTRO")


def clean_id(raw: str) -> str:
    """Strip float suffix from numeric IDs: '610.0' → '610'."""
    raw = raw.strip()
    if raw.endswith(".0"):
        raw = raw[:-2]
    return raw


def make_code(prefix: str, id_val: str, seen: set) -> str:
    """Build unique code: PREFIX-ID. Suffix -2, -3... for duplicates."""
    base = f"{prefix}-{clean_id(id_val)}" if id_val else f"{prefix}-SINID"
    code = base
    n = 2
    while code in seen:
        code = f"{base}-{n}"
        n += 1
    seen.add(code)
    return code


# ---------------------------------------------------------------------------
# Source configurations
# ---------------------------------------------------------------------------

@dataclass
class SourceConfig:
    name: str           # human label (also --source filter value)
    filename: str       # CSV filename in ETL_DATA_DIR
    prefix: str         # code prefix: REC, OFI, MEM, etc.
    skip_rows: int = 0  # rows to skip before header (for garbage first rows)
    id_col: str = ""    # column name for correlativo/folio
    name_col: str = "MATERIA"
    type_col: str = ""  # column with TIPO DE DOCUMENTO (empty = default_type)
    default_type: str = "OTRO"
    url_col: str = ""
    # metadata extractors: list of (meta_key, csv_col)
    meta_cols: list[tuple[str, str]] = field(default_factory=list)
    # optional channel column
    channel_col: str = ""


SOURCES: list[SourceConfig] = [
    SourceConfig(
        name="RECIBIDOS",
        filename="RECIBIDOS.csv",
        prefix="REC",
        skip_rows=1,          # row 0 = "ENROCADO" garbage
        id_col="C",
        name_col="MATERIA",
        type_col="TIPO DE DOCUMENTO",
        url_col="",           # RECIBIDOS has no storage URL column
        channel_col="VIA RECEPCIÓN",
        meta_cols=[
            ("via_recepcion",    "VIA RECEPCIÓN"),
            ("numero_documento", "NÚMERO DOCUMENTO"),
            ("fecha_documento",  "FECHA DOCUMENTO"),
            ("fecha_recepcion",  "FECHA RECEPCIÓN"),
            ("fecha_entrega",    "FECHA DE ENTREGA"),
            ("remitente",        "REMITENTE"),
            ("destinatario",     "DESTINATARIO"),
            ("via_distribucion", "VIA DISTRIBUCIÓN"),
            ("derivado_a",       "DERIVADO A: (DIVISIÓN)"),
            ("adjunto",          "ADJUNTO"),
            ("observaciones",    "Observación"),
        ],
    ),
    SourceConfig(
        name="OFICIOS",
        filename="OFICIOS.csv",
        prefix="OFI",
        skip_rows=0,
        id_col="f",
        name_col="MATERIA",
        type_col="TIPO DE DCTO",
        url_col="LINK AL DOCUMENTO",
        channel_col="DISTRIBUCIÓN",
        meta_cols=[
            ("solicita",         "SOLICITA"),
            ("numero_documento", "N° DCTO"),
            ("fecha_documento",  "FECHA DCTO"),
            ("fecha_recepcion",  "FECHA RECEPCIÓN"),
            ("fecha_entrega",    "FECHA ENTREGA"),
            ("remitente",        "REMITENTE"),
            ("destinatario",     "DESTINATARIO"),
            ("derivado_a",       "DERIVADO A: (DIVISIÓN)"),
        ],
    ),
    SourceConfig(
        name="MEMOS",
        filename="MEMOS.csv",
        prefix="MEM",
        skip_rows=0,
        id_col="FOLIO",
        name_col="MATERIA",
        type_col="",
        default_type="OTRO",
        url_col="LINK AL DOCUMENTO",
        channel_col="VÍA DESPACHO",
        meta_cols=[
            ("responsable",     "RESPONSABLE"),
            ("de_unidad",       "DE"),
            ("para",            "PARA:"),
            ("fecha_documento", "FECHA DOCTO"),
            ("fecha_entrega",   "FECHA ENTREGA"),
            ("firma",           "FIRMA"),
            ("observaciones",   "OBSERVACIONES"),
        ],
    ),
    SourceConfig(
        name="CARTAS",
        filename="CARTAS.csv",
        prefix="CAR",
        skip_rows=0,
        id_col="NUMERO DOCUMENTO",
        name_col="MATERIA",
        type_col="",
        default_type="OTRO",
        url_col="LINK AL DOCUMENTO",
        channel_col="DISTRIBUCIÓN",
        meta_cols=[
            ("solicita",        "SOLICITA"),
            ("fecha_documento", "FECHA DCTO"),
            ("fecha_recepcion", "FECHA RECEPCIÓN"),
            ("fecha_entrega",   "FECHA ENTREGA"),
            ("remitente",       "REMITENTE"),
            ("destinatario",    "DESTINATARIO"),
            ("derivado_a",      "DERIVADO A: (DIVISIÓN)"),
        ],
    ),
    SourceConfig(
        name="MEMOS_INTERNOS",
        filename="MEMOS INTERNOS.csv",
        prefix="MEI",
        skip_rows=0,
        id_col="FOLIO",
        name_col="MATERIA",
        type_col="",
        default_type="OTRO",
        url_col="LINK AL DOCUMENTO",
        channel_col="",
        meta_cols=[
            ("solicita",        "SOLICITA"),
            ("division",        "DIVISIÓN"),
            ("dirigido_a",      "DIRIGIDO A:"),
            ("fecha_documento", "FECHA DOCTO"),
            ("firma",           "FIRMA"),
            ("observaciones",   "OBSERVACIONES"),
        ],
    ),
    SourceConfig(
        name="OFICIOS_INTERNOS",
        filename="OFICIOS INTERNOS.csv",
        prefix="OFI-INT",
        skip_rows=1,          # row 0 = "}" garbage
        id_col="NÚMERO DOCUMENTO",
        name_col="MATERIA",
        type_col="TIPO DE DOCUMENTO",
        url_col="",
        channel_col="DISTRIBUCIÓN",
        meta_cols=[
            ("fecha_documento",  "FECHA DOCUMENTO"),
            ("fecha_recepcion",  "FECHA RECEPCIÓN"),
            ("fecha_entrega",    "FECHA ENTREGA"),
            ("remitente",        "REMITENTE"),
            ("destinatario",     "DESTINATARIO"),
            ("derivado_a",       "DERIVADO A: (DIVISIÓN)"),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Core loader
# ---------------------------------------------------------------------------

async def load_source(
    db,
    cfg: SourceConfig,
    data_dir: Path,
    dry_run: bool = False,
    limit: int = 0,
) -> ETLStats:
    """Load one CSV source into core.document.

    Morphism: SourceConfig × CSV_row → core.document INSERT params.
    """
    stats = ETLStats()
    filepath = data_dir / cfg.filename

    try:
        rows = read_csv(filepath, skip_rows=cfg.skip_rows)
    except (FileNotFoundError, ValueError) as e:
        log.warning(f"[{cfg.name}] Cannot read: {e}")
        stats.errors.append(str(e))
        return stats

    log.info(f"[{cfg.name}] Loaded {len(rows)} rows from {cfg.filename}")

    if limit > 0:
        rows = rows[:limit]

    # Resolve document_type codes once (cached)
    type_cache: dict[str, str | None] = {}

    async def get_type_id(raw_tipo: str) -> str | None:
        code = map_type(raw_tipo) if raw_tipo else cfg.default_type
        if code not in type_cache:
            type_cache[code] = await resolve_category(db, "document_type", code)
        return type_cache[code]

    seen_codes: set[str] = set()
    row_num = 0

    for row in rows:
        row_num += 1

        # Skip completely empty rows
        if not any(v for v in row.values()):
            stats.skipped += 1
            continue

        try:
            # Build code (idempotency key)
            id_raw = row.get(cfg.id_col, "").strip() if cfg.id_col else ""
            code = make_code(cfg.prefix, id_raw or str(row_num), seen_codes)

            # Build name (NOT NULL constraint)
            name = row.get(cfg.name_col, "").strip()
            if not name:
                name = "(Sin materia)"

            # Resolve document_type_id
            raw_tipo = row.get(cfg.type_col, "").strip() if cfg.type_col else ""
            type_id = await get_type_id(raw_tipo)

            # Build storage_url
            url = row.get(cfg.url_col, "").strip() if cfg.url_col else None
            if url and not url.startswith("http"):
                url = None  # reject non-URLs

            # Build metadata JSONB
            meta: dict[str, str] = {}
            for meta_key, csv_col in cfg.meta_cols:
                val = row.get(csv_col, "").strip()
                if val:
                    meta[meta_key] = val

            # Add canonical tipo_original
            if raw_tipo:
                meta["tipo_original"] = raw_tipo

            # Add channel normalized
            if cfg.channel_col:
                ch_raw = row.get(cfg.channel_col, "").strip()
                if ch_raw:
                    meta["canal_raw"] = ch_raw
                    meta["canal"] = map_channel(ch_raw)

            meta["_etl_source"] = cfg.filename

            if dry_run:
                log.info(
                    f"[DRY-RUN][{cfg.name}] INSERT code={code} name={name[:50]!r}"
                    f" type={raw_tipo or cfg.default_type}"
                )
                stats.inserted += 1
                continue

            await db.execute(
                text("""
                    INSERT INTO core.document
                        (code, name, document_type_id, storage_url, metadata)
                    VALUES
                        (:code, :name, :type_id, :url, CAST(:meta AS jsonb))
                    ON CONFLICT (code) DO NOTHING
                """),
                {
                    "code":    code,
                    "name":    name[:500],  # truncate safety
                    "type_id": type_id,
                    "url":     url,
                    "meta":    json.dumps(meta, ensure_ascii=False),
                },
            )
            stats.inserted += 1

        except Exception as e:
            stats.errors.append(f"[{cfg.name}] Row {row_num}: {e}")
            log.error(f"[{cfg.name}] Row {row_num} error: {e}")

        await batch_commit(db, row_num, dry_run)

    return stats


async def load_documents(
    data_dir: Path,
    source_filter: str | None = None,
    dry_run: bool = False,
    limit: int = 0,
) -> ETLStats:
    """Run all source loaders, aggregate stats."""
    total = ETLStats()
    db = await get_session()

    try:
        sources = [s for s in SOURCES if not source_filter or s.name == source_filter.upper()]
        if not sources:
            log.error(f"Unknown source: {source_filter}. Valid: {[s.name for s in SOURCES]}")
            return total

        for cfg in sources:
            stats = await load_source(db, cfg, data_dir, dry_run, limit)
            total.inserted += stats.inserted
            total.updated  += stats.updated
            total.skipped  += stats.skipped
            total.errors   += stats.errors
            stats.log_summary(cfg.name)

        if not dry_run:
            await db.commit()
            log.info("Final commit done")

    finally:
        await db.close()
        await close_engine()

    return total


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = base_argparser("ETL Phase 2: Load PARTES CSVs → core.document")
    parser.add_argument("--data-dir", type=str, default=str(ETL_DATA_DIR))
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help=f"Process only this source. One of: {[s.name for s in SOURCES]}",
    )
    args = parser.parse_args()

    if args.verbose:
        setup_logging(verbose=True)

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log.info(f"=== ETL Phase 2: load_documents [{mode}] ===")

    async def _run():
        stats = await load_documents(
            data_dir=Path(args.data_dir),
            source_filter=args.source,
            dry_run=args.dry_run,
            limit=args.limit,
        )
        stats.log_summary("TOTAL load_documents")
        if stats.total_processed > 0:
            rate = len(stats.errors) / stats.total_processed
            if rate > 0.10:
                log.warning(f"Error rate {rate:.1%} > 10%")
                sys.exit(1)

    run_async(_run())


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add api/scripts/etl/load_documents.py
git commit -m "feat(etl): add load_documents.py — Phase 2 PARTES → core.document"
```

---

## Task 5: Dry-run test — each source individually

**Step 1: Copy scripts to container**

```bash
docker cp api/scripts goreos_api:/app/scripts
```

**Step 2: Test RECIBIDOS (largest source)**

```bash
docker compose exec api python -m scripts.etl.load_documents \
  --source RECIBIDOS --dry-run --limit 5 --verbose 2>&1
```

Expected: 5 lines like `[DRY-RUN][RECIBIDOS] INSERT code=REC-... name=...`

**Step 3: Test MEMOS**

```bash
docker compose exec api python -m scripts.etl.load_documents \
  --source MEMOS --dry-run --limit 5 --verbose 2>&1
```

Expected: 5 DRY-RUN lines with `MEM-01236` style codes.

**Step 4: Full dry-run all sources**

```bash
docker compose exec api python -m scripts.etl.load_documents --dry-run 2>&1
```

Expected summary:
```
TOTAL load_documents Summary:
  Inserted: ~10500
  Errors:   <100
```

---

## Task 6: Live run + verification

**Step 1: Full live run**

```bash
docker compose exec api python -m scripts.etl.load_documents 2>&1
```

**Step 2: Verify counts by source**

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT metadata->>'_etl_source' AS source, COUNT(*)
FROM core.document WHERE deleted_at IS NULL
GROUP BY 1 ORDER BY 2 DESC;
"
```

Expected:
```
    source     | count
---------------+-------
 RECIBIDOS.csv | ~7178
 OFICIOS.csv   | ~2035
 MEMOS.csv     | ~1290
 ...
```

**Step 3: Verify document_type distribution**

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT c.code, c.label, COUNT(*)
FROM core.document d
JOIN ref.category c ON c.id = d.document_type_id
WHERE d.deleted_at IS NULL
GROUP BY c.code, c.label ORDER BY 3 DESC;
"
```

**Step 4: Verify storage_url coverage**

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT COUNT(*) AS total,
       COUNT(storage_url) AS with_url,
       ROUND(100.0 * COUNT(storage_url) / COUNT(*), 1) AS pct_with_url
FROM core.document WHERE deleted_at IS NULL;
"
```

**Step 5: Test idempotency (re-run)**

```bash
docker compose exec api python -m scripts.etl.load_documents 2>&1 | grep -E "Inserted|Skipped"
```

Expected: `Inserted: 0`, `Skipped: ~10500` (all ON CONFLICT skipped).

**Step 6: Commit**

```bash
git add .
git commit -m "feat(etl): complete Phase 2 — PARTES → core.document (~10.5K docs loaded)"
```

---

## Verification Queries Reference

```sql
-- Full stats
SELECT COUNT(*) AS total,
       COUNT(storage_url) AS with_url,
       COUNT(document_type_id) AS with_type
FROM core.document WHERE deleted_at IS NULL;

-- Sample records
SELECT code, name, storage_url,
       metadata->>'tipo_original' AS tipo,
       metadata->>'_etl_source' AS fuente
FROM core.document
WHERE deleted_at IS NULL
ORDER BY created_at DESC LIMIT 10;
```
