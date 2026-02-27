# ETL Remaining Phases — Complete Pipeline

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete all remaining ETL phases (3–6) to enrich agreements, load territories, record budget modifications, and extract IDIS data.

**Architecture:** Each phase is a standalone async script in `api/scripts/etl/` reusing `common.py` utilities. Scripts are idempotent (metadata-keyed dedup), support `--dry-run`, and run inside the API container. No DDL changes needed — all enrichment fits existing columns + metadata JSONB.

**Tech Stack:** Python 3.12, SQLAlchemy async + asyncpg, CSV parsing via `common.read_csv()`, Chilean currency via `common.parse_amount()`

---

## Phase 3: CONVENIOS Enrichment

### Context

537 agreements exist in `core.agreement`. Current gaps:
- **CGR outcome**: only 129/537 have `cgr_outcome_id` (76% missing)
- **Referente técnico**: only 7/537 have `technical_referent_id` (99% missing)
- **Signed date**: 439/537 have `signed_at` (18% missing)

CSV sources: `CONVENIOS 2023 y 2024.csv` (409 rows) + `CONVENIOS 2025.csv` (98 rows) + `MODIFICACIONES.csv` (29 rows) = 536 rows total.

**Matching strategy**: CSV `CODIGO` column contains IPR BIP codes (e.g., `40058688`). Match via: `CSV.CODIGO → core.ipr.codigo_bip → ipr.id → core.agreement WHERE ipr_id = ipr.id`.

### Task 1: Create `enrich_agreements.py` — Core script

**Files:**
- Create: `api/scripts/etl/enrich_agreements.py`

**Step 1**: Write the script skeleton with imports and constants:

```python
"""
ETL Phase 3 — Enrich core.agreement from CONVENIOS CSVs.

Functor F₃: C_CSV(CONVENIOS) → C_DB(core.agreement) [UPDATE enrichment]
  - CGR outcome: ESTADO CONVENIO EN CGR → cgr_outcome_id
  - Technical referent: REFERENTE TECNICO → technical_referent_id
  - Signed date: FECHA FIRMA DE CONVENIO → signed_at
  - State: ESTADO DE CONVENIO → state_id
  - Metadata: resolution numbers, dates, oficio data

Safety:
  - UPDATE only — never creates new agreements
  - Idempotent via metadata._etl_enriched flag
  - Uses CAST(:param AS jsonb) for asyncpg compatibility

Usage:
  docker compose exec api python -m scripts.etl.enrich_agreements --dry-run
  docker compose exec api python -m scripts.etl.enrich_agreements
"""

import json
import re
from datetime import datetime, time, timezone
from pathlib import Path

from sqlalchemy import text

from scripts.etl.common import (
    ETLStats,
    base_argparser,
    batch_commit,
    build_person_cache,
    close_engine,
    get_session,
    log,
    normalize_text,
    parse_amount,
    parse_date,
    read_csv,
    resolve_category,
    resolve_category_by_label,
    resolve_ipr_by_bip,
    resolve_person_by_name,
    resolve_org_by_name,
    run_async,
    setup_logging,
    ParsedName,
)

CONVENIO_SOURCES = {
    "CONVENIOS 2023 y 2024.csv": {"year_range": "2023-2024"},
    "CONVENIOS 2025.csv": {"year_range": "2025"},
    "MODIFICACIONES.csv": {"year_range": "mod"},
}
DATA_DIR = Path("/app/data/etl/convenios")
```

**Step 2**: Add CGR outcome mapping:

```python
CGR_MAPPING = {
    "tomado de razon": "TOMA_RAZON",
    "toma de razon": "TOMA_RAZON",
    "tomada razon": "TOMA_RAZON",
    "t.r con alcances": "TR_CON_ALCANCES",
    "toma de razon con alcances": "TR_CON_ALCANCES",
    "cursa con observaciones": "CURSA_OBS",
    "representa": "REPRESENTA",
    "retiro": "RETIRO",
    "exento": "EXENTO",
    "en cgr": "EN_CGR",
    "en contraloria": "EN_CGR",
    "enviado al servicio": "EN_CGR",
    "enviado a servicio": "EN_CGR",
    "pendiente": "EN_CGR",
    "n/a": None,
    "": None,
    "no aplica": None,
    "sin tramite cgr": None,
}


def resolve_cgr_code(raw: str) -> str | None:
    """Map raw CGR string to cgr_outcome scheme code."""
    norm = normalize_text(raw)
    for pattern, code in CGR_MAPPING.items():
        if pattern and pattern in norm:
            return code
    return None
```

**Step 3**: Add agreement state mapping:

```python
STATE_MAPPING = {
    "firmado": "FIRMADO_CONTRAPARTE",
    "vigente": "VIGENTE",
    "vencido": "VENCIDO",
    "terminado": "TERMINADO",
    "resciliado": "RESCILIADO",
    "en modificacion": "EN_MODIFICACION",
    "en negociacion": "EN_NEGOCIACION",
    "borrador": "BORRADOR",
    "en revision juridica": "EN_REVISION_JURIDICA",
    "en revision financiera": "EN_REVISION_FINANCIERA",
    "visado interno": "VISADO_INTERNO",
    "firmado gore": "FIRMADO_GORE",
    "tdr pendiente": "TDR_PENDIENTE",
}


def resolve_state_code(raw: str) -> str | None:
    norm = normalize_text(raw)
    for pattern, code in STATE_MAPPING.items():
        if pattern in norm:
            return code
    return None
```

**Step 4**: Add name parser for referente técnico:

```python
def parse_referent_name(raw: str) -> ParsedName | None:
    """Parse 'CARMEN NAVARRETE RETAMAL' → ParsedName."""
    parts = raw.strip().split()
    if len(parts) < 2:
        return None
    if len(parts) == 2:
        return ParsedName(names=parts[0], paternal_surname=parts[1], maternal_surname="")
    if len(parts) == 3:
        return ParsedName(names=parts[0], paternal_surname=parts[1], maternal_surname=parts[2])
    # 4+ parts: first N-2 are names, last 2 are surnames
    return ParsedName(
        names=" ".join(parts[:-2]),
        paternal_surname=parts[-2],
        maternal_surname=parts[-1],
    )
```

**Step 5**: Write the main enrichment function:

```python
async def enrich_agreements(
    db,
    dry_run: bool,
    limit: int,
    source_filter: str | None,
) -> ETLStats:
    stats = ETLStats()
    errors: list[str] = []

    # Pre-load IPR→Agreement lookup
    agreements_by_ipr = {}
    rows = (await db.execute(text("""
        SELECT id, ipr_id, agreement_number, cgr_outcome_id, technical_referent_id, signed_at
        FROM core.agreement
        WHERE deleted_at IS NULL AND ipr_id IS NOT NULL
    """))).mappings().all()
    for a in rows:
        agreements_by_ipr[str(a["ipr_id"])] = dict(a)
    log.info(f"Loaded {len(agreements_by_ipr)} agreements with ipr_id")

    # Build person cache for referent matching
    await build_person_cache(db)

    row_num = 0
    for source_name, source_meta in CONVENIO_SOURCES.items():
        if source_filter and source_filter != source_name:
            continue

        path = DATA_DIR / source_name
        if not path.exists():
            log.warning(f"Source not found: {path}")
            continue

        csv_rows = read_csv(str(path))
        log.info(f"Source {source_name}: {len(csv_rows)} rows")

        for csv_row in csv_rows:
            row_num += 1
            if 0 < limit <= stats.total_processed:
                break

            try:
                # Resolve IPR by BIP code
                codigo = (csv_row.get("CODIGO") or csv_row.get("Código") or "").strip()
                if not codigo:
                    stats.skipped += 1
                    continue

                ipr_id = await resolve_ipr_by_bip(db, codigo)
                if not ipr_id:
                    stats.skipped += 1
                    continue

                # Find agreement by ipr_id
                agreement = agreements_by_ipr.get(ipr_id)
                if not agreement:
                    stats.skipped += 1
                    continue

                agreement_id = str(agreement["id"])

                # Build UPDATE SET clauses
                updates = {}
                meta_updates = {
                    "_etl_source": source_name,
                    "_etl_phase": "3",
                    "_etl_enriched": True,
                    "year_range": source_meta["year_range"],
                }

                # CGR outcome
                cgr_raw = (csv_row.get("ESTADO CONVENIO EN CGR") or
                           csv_row.get("ESTADO CONVENIO EN CGR") or "").strip()
                if cgr_raw:
                    cgr_code = resolve_cgr_code(cgr_raw)
                    if cgr_code:
                        cgr_id = await resolve_category(db, "cgr_outcome", cgr_code)
                        if cgr_id and not agreement["cgr_outcome_id"]:
                            updates["cgr_outcome_id"] = cgr_id
                    meta_updates["cgr_raw"] = cgr_raw

                # Signed date
                signed_raw = (csv_row.get("FECHA FIRMA DE CONVENIO") or
                              csv_row.get("FECHA FIRMA DE CONVENIO ") or "").strip()
                if signed_raw and not agreement["signed_at"]:
                    signed_date = parse_date(signed_raw)
                    if signed_date:
                        updates["signed_at"] = datetime.combine(
                            signed_date, time.min, tzinfo=timezone.utc
                        )
                    meta_updates["signed_raw"] = signed_raw

                # Technical referent
                referent_raw = (csv_row.get("REFERENTE TECNICO O CONTRAPARTE TECNICA") or
                                csv_row.get("REFERENTE TECNICO") or "").strip()
                if referent_raw and not agreement["technical_referent_id"]:
                    parsed = parse_referent_name(referent_raw)
                    if parsed:
                        person = await resolve_person_by_name(db, parsed)
                        if person:
                            updates["technical_referent_id"] = person["id"]
                    meta_updates["referent_raw"] = referent_raw

                # CGR toma de razón date → metadata
                cgr_date_raw = (csv_row.get("FECHA TOMA DE RAZON DE CGR") or
                                csv_row.get("FECHA TOMA DE RAZON DE CGR") or "").strip()
                if cgr_date_raw:
                    cgr_date = parse_date(cgr_date_raw)
                    if cgr_date:
                        meta_updates["cgr_toma_razon_date"] = cgr_date.isoformat()

                # Resolution data → metadata
                for key in ("Nº RES INCORPORA/ CERT CORE", "Nº RES CREA ASIGNACIÓN",
                            "Nº RES APRUEBA CONVENIO", "TIPO DE RESOLUCIÓN",
                            "Nº OFICIO ENVIA CONVENIO", "Nº RES REFERENTE TECNICO",
                            "Nº RES Y FECHA APRUEBA CONVENIO", "RES REFERENTE TECNICO"):
                    val = (csv_row.get(key) or "").strip()
                    if val:
                        safe_key = normalize_text(key).replace(" ", "_").replace("/", "_")[:40]
                        meta_updates[safe_key] = val

                # Amount (MONTO FNDR M$) → metadata (don't overwrite total_amount)
                monto_raw = (csv_row.get("MONTO FNDR M$") or csv_row.get(" MONTO FNDR M$ ") or "").strip()
                if monto_raw:
                    amount = parse_amount(monto_raw)
                    if amount is not None:
                        meta_updates["monto_fndr_m"] = float(amount)

                if not updates and not meta_updates:
                    stats.skipped += 1
                    continue

                if dry_run:
                    fields = list(updates.keys())
                    log.info(f"[DRY-RUN] UPDATE agreement {agreement_id[:8]}... "
                             f"ipr={codigo} fields={fields}")
                    stats.updated += 1
                else:
                    # Build dynamic UPDATE
                    set_parts = []
                    params = {"agreement_id": agreement_id}

                    for col, val in updates.items():
                        set_parts.append(f"{col} = :{col}")
                        params[col] = val

                    # Merge metadata via jsonb_set chain
                    set_parts.append(
                        "metadata = metadata || CAST(:meta AS jsonb)"
                    )
                    params["meta"] = json.dumps(meta_updates, ensure_ascii=False)

                    set_parts.append("updated_at = now()")

                    sql = f"""
                        UPDATE core.agreement
                        SET {', '.join(set_parts)}
                        WHERE id = :agreement_id
                    """
                    await db.execute(text(sql), params)
                    stats.updated += 1

                await batch_commit(db, row_num, dry_run)

            except Exception as e:
                errors.append(f"Row {row_num} codigo={codigo}: {e}")

    stats.errors = errors
    return stats
```

**Step 6**: Write the CLI entrypoint:

```python
def main():
    parser = base_argparser("ETL Phase 3: Enrich agreements from CONVENIOS CSVs")
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Process single source file (e.g., 'CONVENIOS 2025.csv')",
    )
    args = parser.parse_args()

    if args.verbose:
        setup_logging(verbose=True)

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log.info(f"=== ETL Phase 3: enrich_agreements [{mode}] ===")

    async def _run():
        db = await get_session()
        try:
            stats = await enrich_agreements(
                db=db,
                dry_run=args.dry_run,
                limit=args.limit,
                source_filter=args.source,
            )
            if not args.dry_run:
                await db.commit()
                log.info("Phase 3 commit done")
            stats.log_summary("Phase 3 — Enrich Agreements")
        finally:
            await db.close()
            await close_engine()

    run_async(_run())


if __name__ == "__main__":
    main()
```

**Step 7**: Copy CSVs to container and run:

```bash
# Copy sources
docker cp docs/legacy/etl/sources/convenios/originales/ goreos_api:/app/data/etl/convenios/
# Flatten — CSVs end up inside originales/ subfolder
docker compose exec api bash -c "mv /app/data/etl/convenios/originales/*.csv /app/data/etl/convenios/ 2>/dev/null; rmdir /app/data/etl/convenios/originales 2>/dev/null; ls /app/data/etl/convenios/"

# Copy script
docker cp api/scripts goreos_api:/app/scripts

# Dry-run
docker compose exec api python -m scripts.etl.enrich_agreements --dry-run --verbose

# Live run
docker compose exec api python -m scripts.etl.enrich_agreements --verbose
```

**Step 8**: Verify:

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT COUNT(*) AS total,
       COUNT(cgr_outcome_id) AS with_cgr,
       COUNT(technical_referent_id) AS with_referent,
       COUNT(signed_at) AS with_signed,
       COUNT(CASE WHEN metadata->>'_etl_enriched' = 'true' THEN 1 END) AS etl_enriched
FROM core.agreement WHERE deleted_at IS NULL;
"
```

Expected: CGR from 129 → ~300+, referent from 7 → ~50+, signed from 439 → ~500+.

**Step 9**: Commit:

```bash
git add api/scripts/etl/enrich_agreements.py
git commit -m "feat(etl): enrich agreements from CONVENIOS CSVs — CGR, referent, signed date"
```

---

## Phase 4: FRIL Territory Enrichment

### Context

FRIL CSVs have 173 IPR rows with COMUNA field. These can add `ipr_territory` records (impact_type=UBICACION). There are already 3,570 territory records from normalization — this adds supplementary data for FRIL-specific IPRs.

**Note**: FRIL CSVs have NO date fields, so `ipr_milestone` (where `planned_date` is NOT NULL) CANNOT be populated from FRIL.

### Task 2: Create `load_fril.py` — Territory extraction

**Files:**
- Create: `api/scripts/etl/load_fril.py`

**Step 1**: Write the script:

```python
"""
ETL Phase 4 — Load FRIL territory data.

Functor F₄: C_CSV(FRIL) → C_DB(core.ipr_territory) [INSERT]
  - COMUNA → territory_id, impact_type=UBICACION
  - Código → ipr_id via resolve_ipr_by_bip()

Note: FRIL CSVs lack date fields, so ipr_milestone cannot be populated.

Usage:
  docker compose exec api python -m scripts.etl.load_fril --dry-run
  docker compose exec api python -m scripts.etl.load_fril
"""

import json
from pathlib import Path

from sqlalchemy import text

from scripts.etl.common import (
    ETLStats,
    base_argparser,
    batch_commit,
    close_engine,
    get_session,
    log,
    normalize_text,
    read_csv,
    resolve_category,
    resolve_ipr_by_bip,
    resolve_territory_by_name,
    run_async,
    setup_logging,
)

FRIL_DIR = Path("/app/data/etl/fril")
FRIL_FILES = [
    "31 Avan. y Adj..csv",
    "31 Lic. y Con..csv",
    "31 Para., Reeva. y Ter..csv",
    "Fril Avan. y Adj..csv",
    "Fril Lic. y Con..csv",
    "Fril Para., Reeva. y Ter..csv",
]


async def load_fril_territories(
    db,
    dry_run: bool,
    limit: int,
) -> ETLStats:
    stats = ETLStats()
    errors: list[str] = []

    ubicacion_id = await resolve_category(db, "territory_impact", "UBICACION")
    if not ubicacion_id:
        errors.append("Category not found: territory_impact/UBICACION")
        stats.errors = errors
        return stats

    seen_pairs: set[tuple[str, str]] = set()  # (ipr_id, territory_id) dedup
    row_num = 0

    for filename in FRIL_FILES:
        path = FRIL_DIR / filename
        if not path.exists():
            log.warning(f"FRIL file not found: {path}")
            continue

        csv_rows = read_csv(str(path))
        log.info(f"Source {filename}: {len(csv_rows)} rows")

        for csv_row in csv_rows:
            row_num += 1
            if 0 < limit <= stats.total_processed:
                break

            try:
                codigo = (csv_row.get("Código") or csv_row.get("Codigo") or
                          csv_row.get(" Código ") or csv_row.get("Código ") or "").strip()
                comuna = (csv_row.get("Comuna") or csv_row.get(" Comuna ") or
                          csv_row.get("Comuna ") or "").strip()

                if not codigo or not comuna:
                    stats.skipped += 1
                    continue

                ipr_id = await resolve_ipr_by_bip(db, codigo)
                if not ipr_id:
                    stats.skipped += 1
                    continue

                territory_id = await resolve_territory_by_name(db, comuna)
                if not territory_id:
                    stats.skipped += 1
                    errors.append(f"Territory not found: {comuna} (BIP={codigo})")
                    continue

                pair = (ipr_id, territory_id)
                if pair in seen_pairs:
                    stats.skipped += 1
                    continue
                seen_pairs.add(pair)

                # Check if already exists in DB
                existing = (await db.execute(text("""
                    SELECT id FROM core.ipr_territory
                    WHERE ipr_id = :ipr_id AND territory_id = :territory_id
                      AND impact_type_id = :impact_type_id AND deleted_at IS NULL
                    LIMIT 1
                """), {
                    "ipr_id": ipr_id,
                    "territory_id": territory_id,
                    "impact_type_id": ubicacion_id,
                })).mappings().first()

                if existing:
                    stats.skipped += 1
                    continue

                meta = {
                    "_etl_source": filename,
                    "_etl_phase": "4",
                    "estado_iniciativa": (csv_row.get("Estado Iniciativa") or "").strip(),
                    "sub_estado": (csv_row.get("Sub-Estado Iniciativa") or "").strip(),
                }

                if dry_run:
                    log.info(f"[DRY-RUN] INSERT ipr_territory ipr={codigo} comuna={comuna}")
                    stats.inserted += 1
                else:
                    await db.execute(text("""
                        INSERT INTO core.ipr_territory
                            (ipr_id, territory_id, impact_type_id, is_primary, metadata)
                        VALUES
                            (:ipr_id, :territory_id, :impact_type_id, false,
                             CAST(:meta AS jsonb))
                    """), {
                        "ipr_id": ipr_id,
                        "territory_id": territory_id,
                        "impact_type_id": ubicacion_id,
                        "meta": json.dumps(meta, ensure_ascii=False),
                    })
                    stats.inserted += 1

                await batch_commit(db, row_num, dry_run)

            except Exception as e:
                if "uq_ipr_territory_impact" in str(e):
                    stats.skipped += 1
                else:
                    errors.append(f"FRIL {filename} row {row_num}: {e}")

    stats.errors = errors
    return stats


def main():
    parser = base_argparser("ETL Phase 4: Load FRIL territories")
    args = parser.parse_args()
    if args.verbose:
        setup_logging(verbose=True)

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log.info(f"=== ETL Phase 4: load_fril [{mode}] ===")

    async def _run():
        db = await get_session()
        try:
            stats = await load_fril_territories(db, args.dry_run, args.limit)
            if not args.dry_run:
                await db.commit()
                log.info("Phase 4 commit done")
            stats.log_summary("Phase 4 — FRIL Territories")
        finally:
            await db.close()
            await close_engine()

    run_async(_run())


if __name__ == "__main__":
    main()
```

**Step 2**: Copy and run:

```bash
docker cp docs/legacy/etl/sources/fril/originales/ goreos_api:/app/data/etl/fril/
docker compose exec api bash -c "mv /app/data/etl/fril/originales/*.csv /app/data/etl/fril/ 2>/dev/null; ls /app/data/etl/fril/"
docker cp api/scripts goreos_api:/app/scripts
docker compose exec api python -m scripts.etl.load_fril --dry-run --verbose
docker compose exec api python -m scripts.etl.load_fril --verbose
```

**Step 3**: Verify:

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT COUNT(*) AS total,
       COUNT(CASE WHEN metadata->>'_etl_phase' = '4' THEN 1 END) AS from_fril
FROM core.ipr_territory WHERE deleted_at IS NULL;
"
```

**Step 4**: Commit:

```bash
git add api/scripts/etl/load_fril.py
git commit -m "feat(etl): load FRIL territory data into ipr_territory"
```

---

## Phase 5: Budget Modifications → txn.event

### Context

19 CSV files with ~500 budget modification lines. Each becomes a `txn.event` with `event_type=MODIFICACION`. CSVs have 6 garbage header rows, hierarchical SUBT/ITEM/ASIG structure, and Chilean currency amounts.

### Task 3: Create `load_modifications.py`

**Files:**
- Create: `api/scripts/etl/load_modifications.py`

**Step 1**: Write the script:

```python
"""
ETL Phase 5 — Load budget modifications into txn.event.

Functor F₅: C_CSV(MODIFICACIONES) → C_DB(txn.event) [INSERT]
  - Each modification line → txn.event with event_type=MODIFICACION
  - Subject: core.budget_program (matched by SUBT/ITEM/ASIG)
  - Data: amounts before/after/delta, denominación

Usage:
  docker compose exec api python -m scripts.etl.load_modifications --dry-run
  docker compose exec api python -m scripts.etl.load_modifications
"""

import json
import re
from pathlib import Path

from sqlalchemy import text

from scripts.etl.common import (
    ETLStats,
    base_argparser,
    batch_commit,
    close_engine,
    get_session,
    log,
    parse_amount,
    read_csv,
    resolve_category,
    run_async,
    setup_logging,
)

MOD_DIR = Path("/app/data/etl/modificaciones")


def extract_mod_number(filename: str) -> str:
    """Extract modification number from filename. E.g., 'MODIFICACIÓN N°10.csv' → '10'."""
    m = re.search(r"[Nn][°º]?\s*(\d+)", filename)
    if m:
        return m.group(1)
    if "REBAJA 5%" in filename:
        return "REBAJA_5PCT"
    if "REBAJA FUNC" in filename:
        m2 = re.search(r"[Nn][°º]?\s*(\d+)", filename)
        return f"REBAJA_FUNC_{m2.group(1)}" if m2 else "REBAJA_FUNC"
    return filename.replace(".csv", "").strip()


def parse_mod_csv(path: Path) -> list[dict]:
    """Read modification CSV, skipping header rows until we find SUBT/ITEM columns."""
    rows = read_csv(str(path), skip_rows=0)
    if not rows:
        return []

    # Find the actual header row by looking for SUBT pattern
    data_rows = []
    header_found = False
    amount_keys = []

    for row in rows:
        values = list(row.values())
        keys = list(row.keys())

        # Detect header row
        if not header_found:
            combined = " ".join(str(v) for v in values).upper()
            if "SUBT" in combined or "ITEM" in combined:
                header_found = True
                # Next rows are data
                continue
            continue

        # Parse data row — find SUBT/ITEM/ASIG values
        subt = ""
        item = ""
        asig = ""
        denom = ""
        amounts = []

        for k, v in row.items():
            v_str = str(v or "").strip()
            k_upper = str(k or "").upper().strip()

            if "SUBT" in k_upper:
                subt = v_str
            elif "ITEM" == k_upper or k_upper.startswith("ITEM"):
                item = v_str
            elif "ASIG" in k_upper:
                asig = v_str
            elif "DENOM" in k_upper or "NOMBRE" in k_upper:
                denom = v_str
            elif "$" in v_str or re.match(r"^[\d.,\-\s]+$", v_str) and len(v_str) > 2:
                amt = parse_amount(v_str)
                if amt is not None:
                    amounts.append(float(amt))

        if not subt and not item:
            continue  # Skip subtotal/header rows

        data_rows.append({
            "subt": subt,
            "item": item,
            "asig": asig,
            "denominacion": denom,
            "amounts": amounts,
        })

    return data_rows


async def load_modifications(
    db,
    dry_run: bool,
    limit: int,
) -> ETLStats:
    stats = ETLStats()
    errors: list[str] = []

    mod_type_id = await resolve_category(db, "event_type", "MODIFICACION")
    if not mod_type_id:
        errors.append("Category not found: event_type/MODIFICACION")
        stats.errors = errors
        return stats

    # List modification files
    if not MOD_DIR.exists():
        errors.append(f"Directory not found: {MOD_DIR}")
        stats.errors = errors
        return stats

    files = sorted(MOD_DIR.glob("*.csv"))
    log.info(f"Found {len(files)} modification files")

    row_num = 0
    for filepath in files:
        mod_number = extract_mod_number(filepath.name)
        parsed_rows = parse_mod_csv(filepath)
        log.info(f"File {filepath.name}: mod_number={mod_number}, {len(parsed_rows)} data rows")

        for prow in parsed_rows:
            row_num += 1
            if 0 < limit <= stats.total_processed:
                break

            try:
                subt = prow["subt"]
                item = prow["item"]
                asig = prow["asig"]
                denom = prow["denominacion"]
                amounts = prow["amounts"]

                if not subt:
                    stats.skipped += 1
                    continue

                # Dedup key
                dedup_key = f"MOD-{mod_number}-{subt}-{item}-{asig}"

                # Check existing
                existing = (await db.execute(text("""
                    SELECT id FROM txn.event
                    WHERE event_type_id = :type_id
                      AND data->>'dedup_key' = :dedup_key
                    LIMIT 1
                """), {
                    "type_id": mod_type_id,
                    "dedup_key": dedup_key,
                })).mappings().first()

                if existing:
                    stats.skipped += 1
                    continue

                # Try to resolve budget_program as subject
                bp_row = None
                if subt and item and asig:
                    bp_row = (await db.execute(text("""
                        SELECT bp.id
                        FROM core.budget_program bp
                        JOIN ref.category sub ON sub.id = bp.subtitle_id AND sub.code = :subt
                        WHERE bp.deleted_at IS NULL
                          AND bp.metadata->>'item_code' = :item
                        LIMIT 1
                    """), {"subt": subt, "item": item})).mappings().first()

                subject_type = "core.budget_program" if bp_row else "core.budget_program"
                subject_id = str(bp_row["id"]) if bp_row else "00000000-0000-0000-0000-000000000000"

                event_data = {
                    "dedup_key": dedup_key,
                    "modification_number": mod_number,
                    "source_file": filepath.name,
                    "subt": subt,
                    "item": item,
                    "asig": asig,
                    "denominacion": denom,
                    "_etl_phase": "5",
                }

                # Map amounts to named fields based on position
                amount_labels = [
                    "distribucion_inicial_m",
                    "ppto_vigente_anterior_m",
                    "modificacion_m",
                    "ppto_vigente_actual_m",
                ]
                for i, amt in enumerate(amounts):
                    if i < len(amount_labels):
                        event_data[amount_labels[i]] = amt

                if dry_run:
                    log.info(f"[DRY-RUN] INSERT txn.event mod={mod_number} "
                             f"subt={subt} item={item} asig={asig}")
                    stats.inserted += 1
                else:
                    await db.execute(text("""
                        INSERT INTO txn.event
                            (event_type_id, subject_type, subject_id, data)
                        VALUES
                            (:type_id, :subject_type, CAST(:subject_id AS uuid),
                             CAST(:data AS jsonb))
                    """), {
                        "type_id": mod_type_id,
                        "subject_type": subject_type,
                        "subject_id": subject_id,
                        "data": json.dumps(event_data, ensure_ascii=False),
                    })
                    stats.inserted += 1

                await batch_commit(db, row_num, dry_run)

            except Exception as e:
                errors.append(f"Mod {mod_number} row {row_num}: {e}")

    stats.errors = errors
    return stats


def main():
    parser = base_argparser("ETL Phase 5: Load budget modifications into txn.event")
    args = parser.parse_args()
    if args.verbose:
        setup_logging(verbose=True)

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log.info(f"=== ETL Phase 5: load_modifications [{mode}] ===")

    async def _run():
        db = await get_session()
        try:
            stats = await load_modifications(db, args.dry_run, args.limit)
            if not args.dry_run:
                await db.commit()
                log.info("Phase 5 commit done")
            stats.log_summary("Phase 5 — Budget Modifications")
        finally:
            await db.close()
            await close_engine()

    run_async(_run())


if __name__ == "__main__":
    main()
```

**Step 2**: Copy and run:

```bash
docker cp docs/legacy/etl/sources/modificaciones/originales/ goreos_api:/app/data/etl/modificaciones/
docker compose exec api bash -c "mv /app/data/etl/modificaciones/originales/*.csv /app/data/etl/modificaciones/ 2>/dev/null; ls /app/data/etl/modificaciones/"
docker cp api/scripts goreos_api:/app/scripts
docker compose exec api python -m scripts.etl.load_modifications --dry-run --verbose
docker compose exec api python -m scripts.etl.load_modifications --verbose
```

**Step 3**: Verify:

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT data->>'modification_number' AS mod_number, COUNT(*)
FROM txn.event
WHERE event_type_id = (SELECT id FROM ref.category WHERE scheme='event_type' AND code='MODIFICACION')
GROUP BY 1 ORDER BY 1;
"
```

**Step 4**: Commit:

```bash
git add api/scripts/etl/load_modifications.py
git commit -m "feat(etl): load budget modifications into txn.event"
```

---

## Phase 6: IDIS Territory + Party Enrichment

### Context

IDIS ANÁLISIS has 3,033 rows with 78 columns. Usable extractions:
- **COMUNA** → `ipr_territory` (UBICACION)
- **UNIDAD TÉCNICA** → `ipr_party` (UNIDAD_TECNICA role) — supplementary to existing 670
- **FORMULADOR** → `ipr_party` (FORMULADOR role) — new data
- **BENEFICIARIO** → `ipr_party` (BENEFICIARIO role) — supplementary

**Warning**: Architecture doc notes data corruption in CONSOLIDADO and MASTER files. Only use ANÁLISIS.csv.

### Task 4: Create `load_idis.py` — Territory + Party extraction

**Files:**
- Create: `api/scripts/etl/load_idis.py`

**Step 1**: Write the script:

```python
"""
ETL Phase 6 — Extract territory and party data from IDIS ANÁLISIS.

Functor F₆: C_CSV(ANÁLISIS) → C_DB(core.ipr_territory, core.ipr_party) [INSERT]
  - COMUNA → ipr_territory (UBICACION)
  - UNIDAD TÉCNICA → ipr_party (UNIDAD_TECNICA)
  - FORMULADOR → ipr_party (FORMULADOR)

Only uses ANÁLISIS.csv — other IDIS files have data corruption.

Usage:
  docker compose exec api python -m scripts.etl.load_idis --dry-run
  docker compose exec api python -m scripts.etl.load_idis
  docker compose exec api python -m scripts.etl.load_idis --territory-only
  docker compose exec api python -m scripts.etl.load_idis --party-only
"""

import json
from pathlib import Path

from sqlalchemy import text

from scripts.etl.common import (
    ETLStats,
    base_argparser,
    batch_commit,
    close_engine,
    get_session,
    log,
    read_csv,
    resolve_category,
    resolve_ipr_by_bip,
    resolve_org_by_name,
    resolve_territory_by_name,
    run_async,
    setup_logging,
)

ANALISIS_PATH = Path("/app/data/etl/idis/ANÁLISIS.csv")

# IDIS party role mappings
PARTY_EXTRACTIONS = [
    {"csv_key": "UNIDAD TÉCNICA", "role_code": "UNIDAD_TECNICA"},
    {"csv_key": "FORMULADOR", "role_code": "FORMULADOR"},
]


async def load_idis(
    db,
    dry_run: bool,
    limit: int,
    territory_only: bool,
    party_only: bool,
) -> ETLStats:
    stats = ETLStats()
    errors: list[str] = []

    if not ANALISIS_PATH.exists():
        errors.append(f"File not found: {ANALISIS_PATH}")
        stats.errors = errors
        return stats

    csv_rows = read_csv(str(ANALISIS_PATH))
    log.info(f"IDIS ANÁLISIS: {len(csv_rows)} rows")

    # Pre-resolve categories
    ubicacion_id = await resolve_category(db, "territory_impact", "UBICACION")
    party_roles = {}
    for pe in PARTY_EXTRACTIONS:
        role_id = await resolve_category(db, "ipr_party_role", pe["role_code"])
        if role_id:
            party_roles[pe["csv_key"]] = {"role_id": role_id, "role_code": pe["role_code"]}
        else:
            log.warning(f"Party role not found: {pe['role_code']}")

    seen_territories: set[tuple[str, str]] = set()
    seen_parties: set[tuple[str, str, str]] = set()
    row_num = 0

    for csv_row in csv_rows:
        row_num += 1
        if 0 < limit <= stats.total_processed:
            break

        try:
            bip = (csv_row.get("BIP") or csv_row.get("Código") or "").strip()
            if not bip:
                stats.skipped += 1
                continue

            ipr_id = await resolve_ipr_by_bip(db, bip)
            if not ipr_id:
                stats.skipped += 1
                continue

            # --- Territory ---
            if not party_only:
                comuna = (csv_row.get("COMUNA") or "").strip()
                if comuna and ubicacion_id:
                    territory_id = await resolve_territory_by_name(db, comuna)
                    if territory_id:
                        pair = (ipr_id, territory_id)
                        if pair not in seen_territories:
                            seen_territories.add(pair)

                            existing = (await db.execute(text("""
                                SELECT id FROM core.ipr_territory
                                WHERE ipr_id = :ipr_id AND territory_id = :tid
                                  AND impact_type_id = :impact AND deleted_at IS NULL
                                LIMIT 1
                            """), {
                                "ipr_id": ipr_id, "tid": territory_id,
                                "impact": ubicacion_id,
                            })).mappings().first()

                            if not existing:
                                meta = {"_etl_source": "ANÁLISIS.csv", "_etl_phase": "6"}
                                if dry_run:
                                    log.info(f"[DRY-RUN] INSERT territory bip={bip} comuna={comuna}")
                                else:
                                    await db.execute(text("""
                                        INSERT INTO core.ipr_territory
                                            (ipr_id, territory_id, impact_type_id, is_primary, metadata)
                                        VALUES (:ipr_id, :tid, :impact, false, CAST(:meta AS jsonb))
                                    """), {
                                        "ipr_id": ipr_id, "tid": territory_id,
                                        "impact": ubicacion_id,
                                        "meta": json.dumps(meta, ensure_ascii=False),
                                    })
                                stats.inserted += 1

            # --- Party roles ---
            if not territory_only:
                for csv_key, role_info in party_roles.items():
                    org_name = (csv_row.get(csv_key) or "").strip()
                    if not org_name or len(org_name) < 3:
                        continue

                    org_id = await resolve_org_by_name(db, org_name)
                    if not org_id:
                        continue

                    triple = (ipr_id, org_id, role_info["role_id"])
                    if triple in seen_parties:
                        continue
                    seen_parties.add(triple)

                    existing = (await db.execute(text("""
                        SELECT id FROM core.ipr_party
                        WHERE ipr_id = :ipr_id AND organization_id = :org_id
                          AND party_role_id = :role_id AND deleted_at IS NULL
                        LIMIT 1
                    """), {
                        "ipr_id": ipr_id, "org_id": org_id,
                        "role_id": role_info["role_id"],
                    })).mappings().first()

                    if not existing:
                        meta = {
                            "_etl_source": "ANÁLISIS.csv",
                            "_etl_phase": "6",
                            "org_name_raw": org_name,
                        }
                        if dry_run:
                            log.info(f"[DRY-RUN] INSERT party bip={bip} "
                                     f"role={role_info['role_code']} org={org_name[:30]}")
                        else:
                            await db.execute(text("""
                                INSERT INTO core.ipr_party
                                    (ipr_id, organization_id, party_role_id, metadata)
                                VALUES (:ipr_id, :org_id, :role_id, CAST(:meta AS jsonb))
                            """), {
                                "ipr_id": ipr_id, "org_id": org_id,
                                "role_id": role_info["role_id"],
                                "meta": json.dumps(meta, ensure_ascii=False),
                            })
                        stats.inserted += 1

            await batch_commit(db, row_num, dry_run)

        except Exception as e:
            if "uq_ipr_party_role" in str(e) or "uq_ipr_territory_impact" in str(e):
                stats.skipped += 1
            else:
                errors.append(f"IDIS row {row_num} bip={bip}: {e}")

    stats.errors = errors
    return stats


def main():
    parser = base_argparser("ETL Phase 6: Load IDIS ANÁLISIS territory + party data")
    parser.add_argument("--territory-only", action="store_true",
                        help="Only load territory data")
    parser.add_argument("--party-only", action="store_true",
                        help="Only load party data")
    args = parser.parse_args()
    if args.verbose:
        setup_logging(verbose=True)

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log.info(f"=== ETL Phase 6: load_idis [{mode}] ===")

    async def _run():
        db = await get_session()
        try:
            stats = await load_idis(
                db, args.dry_run, args.limit,
                territory_only=args.territory_only,
                party_only=args.party_only,
            )
            if not args.dry_run:
                await db.commit()
                log.info("Phase 6 commit done")
            stats.log_summary("Phase 6 — IDIS Territory + Party")
        finally:
            await db.close()
            await close_engine()

    run_async(_run())


if __name__ == "__main__":
    main()
```

**Step 2**: Copy and run:

```bash
docker cp docs/legacy/etl/sources/idis/originales/ANÁLISIS.csv goreos_api:/app/data/etl/idis/
docker cp api/scripts goreos_api:/app/scripts
docker compose exec api python -m scripts.etl.load_idis --dry-run --verbose --limit 100
docker compose exec api python -m scripts.etl.load_idis --verbose
```

**Step 3**: Verify:

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT 'territory' AS entity,
       COUNT(*) AS total,
       COUNT(CASE WHEN metadata->>'_etl_phase' = '6' THEN 1 END) AS from_idis
FROM core.ipr_territory WHERE deleted_at IS NULL
UNION ALL
SELECT 'party',
       COUNT(*),
       COUNT(CASE WHEN metadata->>'_etl_phase' = '6' THEN 1 END)
FROM core.ipr_party WHERE deleted_at IS NULL;
"
```

**Step 4**: Commit:

```bash
git add api/scripts/etl/load_idis.py
git commit -m "feat(etl): load IDIS territory and party data from ANÁLISIS"
```

---

## Task 5: Final — Update docs + CLAUDE.md

**Step 1**: Update CLAUDE.md ETL section with all new modules.

**Step 2**: Update MEMORY.md with results from all phases.

**Step 3**: Final commit:

```bash
git add CLAUDE.md
git commit -m "docs(etl): record completion of ETL phases 3-6"
```

---

## Key files

| File | Action | Phase |
|------|--------|-------|
| `api/scripts/etl/enrich_agreements.py` | CREATE | 3 |
| `api/scripts/etl/load_fril.py` | CREATE | 4 |
| `api/scripts/etl/load_modifications.py` | CREATE | 5 |
| `api/scripts/etl/load_idis.py` | CREATE | 6 |
| `CLAUDE.md` | MODIFY | docs |

## Execution order

```
Phase 3 → Phase 4 → Phase 5 → Phase 6 → docs
```

All phases are independent (no cross-dependencies), but Phase 3 is highest value.
