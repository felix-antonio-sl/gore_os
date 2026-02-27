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

# Alias mapping for known misspellings in FRIL CSVs
TERRITORY_ALIASES = {
    "TREHUACO": "Treguaco",
}


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
                          csv_row.get(" Código ") or csv_row.get("Código ") or
                          csv_row.get(" Código") or "").strip()
                comuna = (csv_row.get("Comuna") or csv_row.get(" Comuna ") or
                          csv_row.get("Comuna ") or csv_row.get(" Comuna") or "").strip()

                if not codigo or not comuna:
                    stats.skipped += 1
                    continue

                # Normalize territory name aliases
                comuna_resolved = TERRITORY_ALIASES.get(comuna.upper(), comuna)

                ipr_id = await resolve_ipr_by_bip(db, codigo)
                if not ipr_id:
                    stats.skipped += 1
                    continue

                territory_id = await resolve_territory_by_name(db, comuna_resolved)
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
                    "estado_iniciativa": (csv_row.get("Estado Iniciativa") or
                                          csv_row.get(" Estado Iniciativa ") or "").strip(),
                    "sub_estado": (csv_row.get("Sub-Estado Iniciativa") or
                                   csv_row.get(" Sub-Estado Iniciativa ") or "").strip(),
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
