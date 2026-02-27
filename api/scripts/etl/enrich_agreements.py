"""
ETL Phase 3 — Enrich core.agreement from CONVENIOS CSVs.

Functor F₃: C_CSV(CONVENIOS) → C_DB(core.agreement) [UPDATE enrichment]
  - CGR outcome: ESTADO CONVENIO EN CGR → cgr_outcome_id
  - Technical referent: REFERENTE TECNICO → technical_referent_id
  - Signed date: FECHA FIRMA DE CONVENIO → signed_at
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
    resolve_ipr_by_bip,
    resolve_person_by_name,
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

# ---------------------------------------------------------------------------
# CGR outcome mapping
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Agreement state mapping
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Referent name parser
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main enrichment function
# ---------------------------------------------------------------------------

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

            codigo = ""
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
                cgr_raw = (csv_row.get("ESTADO CONVENIO EN CGR") or "").strip()
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
                                csv_row.get("REFERENTE TECNICO") or
                                csv_row.get("REFERENTE TECNICO ") or "").strip()
                if referent_raw and not agreement["technical_referent_id"]:
                    parsed = parse_referent_name(referent_raw)
                    if parsed:
                        person = await resolve_person_by_name(db, parsed)
                        if person:
                            updates["technical_referent_id"] = person["id"]
                    meta_updates["referent_raw"] = referent_raw

                # CGR toma de razón date → metadata
                cgr_date_raw = (csv_row.get("FECHA TOMA DE RAZON DE CGR") or "").strip()
                if cgr_date_raw:
                    cgr_date = parse_date(cgr_date_raw)
                    if cgr_date:
                        meta_updates["cgr_toma_razon_date"] = cgr_date.isoformat()

                # Resolution data → metadata
                for key in ("Nº RES INCORPORA/ CERT CORE", "Nº RES CREA ASIGNACIÓN",
                            "Nº RES APRUEBA CONVENIO", "TIPO DE RESOLUCIÓN",
                            "Nº OFICIO ENVIA CONVENIO", "Nº RES REFERENTE TECNICO",
                            "Nº RES  Y FECHA APRUEBA CONVENIO", "RES REFERENTE TECNICO"):
                    val = (csv_row.get(key) or "").strip()
                    if val:
                        safe_key = normalize_text(key).replace(" ", "_").replace("/", "_")[:40]
                        meta_updates[safe_key] = val

                # Amount (MONTO FNDR M$) → metadata
                monto_raw = (csv_row.get("MONTO FNDR M$") or
                             csv_row.get(" MONTO FNDR M$ ") or
                             csv_row.get(" MONTO FNDR M$") or "").strip()
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

                    # Merge metadata via jsonb concat
                    set_parts.append(
                        "metadata = COALESCE(metadata, '{}'::jsonb) || CAST(:meta AS jsonb)"
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

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
