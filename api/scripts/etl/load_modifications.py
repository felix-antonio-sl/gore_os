"""
ETL Phase 5 — Load budget modifications into txn.event.

Functor F₅: C_CSV(MODIFICACIONES) → C_DB(txn.event) [INSERT]
  - Each modification line → txn.event with event_type=MODIFICACION
  - Subject: core.budget_program (matched by SUBT/ITEM/ASIG)
  - Data: amounts before/after/delta, denominación

CSV structure quirk: each file has 6+ garbage header rows (institutional
header, title, blanks). Real data starts after the SUBT/ITEM/ASIG row.
Columns are positional — col[2]=SUBT, col[3]=ITEM, col[4]=ASIG,
col[5]=DENOMINACION, col[6-9]=four amount columns.

Usage:
  docker compose exec api python -m scripts.etl.load_modifications --dry-run
  docker compose exec api python -m scripts.etl.load_modifications
"""

import csv
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
    run_async,
    setup_logging,
)

MOD_DIR = Path("/app/data/etl/modificaciones")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ENCODINGS = ["utf-8-sig", "latin-1", "cp1252"]


def extract_mod_number(filename: str) -> str:
    """Extract modification number from filename. E.g., 'MODIFICACIÓN N°10.csv' → '10'."""
    # Check special cases first (before generic regex)
    if "REBAJA 5%" in filename:
        return "REBAJA_5PCT"
    if "REBAJA FUNC" in filename:
        m2 = re.search(r"[Nn][°º]?\s*(\d+)", filename)
        return f"REBAJA_FUNC_{m2.group(1)}" if m2 else "REBAJA_FUNC"
    if "SIN EFECTO" in filename.upper():
        m3 = re.search(r"[Nn][°º]?\s*(\d+)", filename)
        return f"{m3.group(1)}_SIN_EFECTO" if m3 else filename.replace(".csv", "").strip()
    if "SIC" in filename.upper():
        m4 = re.search(r"[Nn][°º]?\s*(\d+)", filename)
        return f"{m4.group(1)}_SIC" if m4 else filename.replace(".csv", "").strip()
    m = re.search(r"[Nn][°º]?\s*(\d+)", filename)
    if m:
        return m.group(1)
    return filename.replace(".csv", "").strip()


def parse_mod_csv(path: Path) -> list[dict]:
    """Read modification CSV with positional column parsing.

    Skips institutional header rows until finding SUBT/ITEM pattern,
    then extracts hierarchical budget lines with amounts.
    """
    # Find working encoding
    raw_rows = []
    for enc in _ENCODINGS:
        try:
            with open(path, encoding=enc, newline="") as f:
                reader = csv.reader(f)
                raw_rows = list(reader)
            break
        except UnicodeDecodeError:
            continue

    if not raw_rows:
        return []

    # Find header row (contains SUBT)
    header_idx = -1
    for i, row in enumerate(raw_rows):
        combined = " ".join(str(c) for c in row).upper()
        if "SUBT" in combined:
            header_idx = i
            break

    if header_idx < 0:
        log.warning(f"No SUBT header found in {path.name}")
        return []

    # Parse data rows after header
    data_rows = []
    current_subt = ""
    current_item = ""

    for row in raw_rows[header_idx + 1:]:
        if len(row) < 7:
            continue

        # Positional: col[2]=SUBT, col[3]=ITEM, col[4]=ASIG, col[5]=DENOM
        subt_raw = row[2].strip() if len(row) > 2 else ""
        item_raw = row[3].strip() if len(row) > 3 else ""
        asig_raw = row[4].strip() if len(row) > 4 else ""
        denom = row[5].strip() if len(row) > 5 else ""

        # Track hierarchical context
        if subt_raw:
            current_subt = subt_raw
            current_item = ""
        if item_raw:
            current_item = item_raw

        # Skip pure total/summary rows (GASTOS at top, or empty structure rows)
        if not subt_raw and not item_raw and not asig_raw:
            continue

        # Extract amounts from remaining columns (positions 6+)
        amounts = []
        for col in row[6:]:
            val = str(col or "").strip()
            if val:
                amt = parse_amount(val)
                if amt is not None:
                    amounts.append(float(amt))

        if not amounts:
            continue

        data_rows.append({
            "subt": current_subt if not subt_raw else subt_raw,
            "item": current_item if not item_raw else item_raw,
            "asig": asig_raw,
            "denominacion": denom,
            "amounts": amounts,
        })

    return data_rows


# ---------------------------------------------------------------------------
# Main loader
# ---------------------------------------------------------------------------

async def load_modifications(
    db,
    dry_run: bool,
    limit: int,
) -> ETLStats:
    stats = ETLStats()
    errors: list[str] = []

    mod_type_id = await resolve_category_cached(db, "event_type", "MODIFICACION")
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

                subject_type = "core.budget_program"
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


async def resolve_category_cached(db, scheme: str, code: str) -> str | None:
    """Resolve category — thin wrapper around common.resolve_category."""
    from scripts.etl.common import resolve_category
    return await resolve_category(db, scheme, code)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

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
