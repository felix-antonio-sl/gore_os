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

# Alias mapping for known misspellings
TERRITORY_ALIASES = {
    "TREHUACO": "Treguaco",
}

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

        bip = ""
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
                    comuna_resolved = TERRITORY_ALIASES.get(comuna.upper(), comuna)
                    territory_id = await resolve_territory_by_name(db, comuna_resolved)
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

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
