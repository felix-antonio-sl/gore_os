"""
ETL Phase 2C — Project document layer into transactional legal entities.

Functor K: C_DB(core.document) -> C_DB(core.administrative_act, core.resolution, core.rendition)
  - Resolution documents (EXENTA/AFECTA) -> administrative_act + resolution
  - Rendition documents -> optional rendition creation only when agreement linkage is resolvable

Safety:
  - Idempotent by metadata.document_code
  - Uses CAST(:param AS jsonb) for asyncpg compatibility

Usage:
  docker compose exec api python -m scripts.etl.load_admin_acts --dry-run
  docker compose exec api python -m scripts.etl.load_admin_acts
  docker compose exec api python -m scripts.etl.load_admin_acts --insert-renditions-if-linked
"""

import json
import re
import sys
import csv
from datetime import datetime, time, timezone
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
    parse_date,
    resolve_category,
    resolve_org_by_name,
    run_async,
    setup_logging,
)

RESOLUTION_SOURCES = ("RESOLUCIONES AFECTAS.csv", "RESOLUCIONES EXENTAS.csv")
RENDITION_SOURCES = ("RENDICIONES 2024.csv", "RENDICIONES FNDR Y ADNC.csv")
DEFAULT_CROSSWALK_PATH = Path("/app/data/etl/crosswalk/rendition_agreement_crosswalk.csv")


def normalize_code(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", (raw or "").upper())


async def load_crosswalk(
    db,
    crosswalk_path: Path | None,
    require_file: bool = False,
) -> tuple[dict[str, dict], list[str], bool]:
    """Load and validate rendition crosswalk keyed by normalized legacy code."""
    errors: list[str] = []
    mapping: dict[str, dict] = {}

    if not crosswalk_path:
        return mapping, errors, False
    if not crosswalk_path.exists():
        if require_file:
            errors.append(f"Crosswalk file not found: {crosswalk_path}")
        else:
            log.warning(f"Crosswalk not found, continuing without crosswalk: {crosswalk_path}")
        return mapping, errors, False

    with open(crosswalk_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            legacy_raw = (row.get("legacy_codigo") or "").strip()
            if not legacy_raw:
                continue
            norm_legacy = normalize_code(legacy_raw)
            if not norm_legacy:
                continue

            if norm_legacy in mapping:
                errors.append(f"Crosswalk duplicate legacy_codigo at row {i}: {legacy_raw}")
                continue

            mapping[norm_legacy] = {
                "legacy_codigo": legacy_raw,
                "agreement_number": (row.get("agreement_number") or "").strip(),
                "agreement_id": (row.get("agreement_id") or "").strip(),
                "renderer_org_id": (row.get("renderer_org_id") or "").strip(),
                "renderer_name": (row.get("renderer_name") or "").strip(),
                "status": normalize_text(row.get("status") or "pending"),
                "confidence": (row.get("confidence") or "").strip(),
                "notes": (row.get("notes") or "").strip(),
            }

    if not mapping:
        return mapping, errors, True

    agreements = (
        await db.execute(
            text(
                """
                SELECT id, agreement_number
                FROM core.agreement
                WHERE deleted_at IS NULL
                """
            )
        )
    ).mappings().all()
    by_id = {str(a["id"]): str(a["id"]) for a in agreements}
    by_number = {normalize_code(a["agreement_number"]): str(a["id"]) for a in agreements if a["agreement_number"]}

    for norm_legacy, cw in mapping.items():
        if cw["status"] not in ("approved", "pending", "rejected"):
            errors.append(f"Crosswalk {cw['legacy_codigo']}: invalid status '{cw['status']}'")

        if cw["status"] != "approved":
            continue

        aid = cw["agreement_id"]
        anum = cw["agreement_number"]
        resolved_by_number = by_number.get(normalize_code(anum)) if anum else None

        if aid and aid not in by_id:
            errors.append(f"Crosswalk {cw['legacy_codigo']}: agreement_id not found '{aid}'")
            continue

        if anum and not resolved_by_number:
            errors.append(f"Crosswalk {cw['legacy_codigo']}: agreement_number not found '{anum}'")
            continue

        if aid and resolved_by_number and aid != resolved_by_number:
            errors.append(
                f"Crosswalk {cw['legacy_codigo']}: agreement_id/number mismatch "
                f"({aid} vs {resolved_by_number})"
            )
            continue

        cw["resolved_agreement_id"] = aid or resolved_by_number
        if not cw["resolved_agreement_id"]:
            errors.append(f"Crosswalk {cw['legacy_codigo']}: approved row missing agreement reference")

    return mapping, errors, True


def map_resolution_type(subject: str) -> str:
    s = normalize_text(subject)
    if any(k in s for k in ("modifica", "modifiqu", "modifiquese", "modificase")):
        return "MODIFICATORIA"
    if "deroga" in s:
        return "DEROGATORIA"
    if any(k in s for k in ("designa", "nombra", "nombramiento")):
        return "DESIGNACION"
    if "delega" in s:
        return "DELEGACION"
    if "sancion" in s:
        return "SANCIONATORIA"
    return "APROBATORIA"


def map_act_state(raw_state: str) -> str:
    s = normalize_text(raw_state)
    if "tramite" in s:
        return "TRAMITADO"
    if "revision" in s:
        return "EN_REVISION"
    if "visado" in s:
        return "VISADO"
    if "anulad" in s:
        return "ANULADO"
    if "rechaz" in s:
        return "RECHAZADO_CGR"
    return "FIRMADO"


def parse_doc_date(meta: dict, fallback_iso: str | None = None):
    for key in ("fecha_docto", "fecha_dcto", "fecha_documento"):
        if key in meta:
            parsed = parse_date(meta.get(key, ""))
            if parsed:
                return parsed
    if fallback_iso:
        try:
            return parse_date(fallback_iso[:10])
        except Exception:
            return None
    return None


async def resolve_issuer_org_id(db, issuer_code: str | None) -> str | None:
    if issuer_code:
        row = (
            await db.execute(
                text(
                    """
                    SELECT id
                    FROM core.organization
                    WHERE deleted_at IS NULL
                      AND code = :code
                    LIMIT 1
                    """
                ),
                {"code": issuer_code},
            )
        ).mappings().first()
        if row:
            return str(row["id"])

    row = (
        await db.execute(
            text(
                """
                SELECT id
                FROM core.organization
                WHERE deleted_at IS NULL
                  AND name ILIKE '%Gobierno Regional de Ñuble%'
                LIMIT 1
                """
            )
        )
    ).mappings().first()
    return str(row["id"]) if row else None


async def load_resolution_entities(
    db,
    dry_run: bool,
    limit: int,
    issuer_org_code: str | None,
) -> tuple[int, int, int, list[str]]:
    inserted_acts = 0
    inserted_resolutions = 0
    skipped = 0
    errors: list[str] = []

    issuer_id = await resolve_issuer_org_id(db, issuer_org_code)
    if not issuer_id:
        errors.append("Cannot resolve issuer organization (GORE)")
        return inserted_acts, inserted_resolutions, skipped, errors

    act_type_id = await resolve_category(db, "act_type", "RESOLUCION")
    if not act_type_id:
        errors.append("Category not found: act_type/RESOLUCION")
        return inserted_acts, inserted_resolutions, skipped, errors

    q = text(
        """
        SELECT id, code, name, storage_url, created_at, metadata
        FROM core.document
        WHERE deleted_at IS NULL
          AND metadata->>'_etl_source' = ANY(:sources)
        ORDER BY code
        """
    )
    rows = (await db.execute(q, {"sources": list(RESOLUTION_SOURCES)})).mappings().all()
    if limit > 0:
        rows = rows[:limit]

    row_num = 0
    for doc in rows:
        row_num += 1
        code = doc["code"]
        meta = doc["metadata"] or {}

        try:
            existing_act = (
                await db.execute(
                    text(
                        """
                        SELECT id
                        FROM core.administrative_act
                        WHERE deleted_at IS NULL
                          AND metadata->>'document_code' = :doc_code
                        LIMIT 1
                        """
                    ),
                    {"doc_code": code},
                )
            ).mappings().first()

            act_id = None
            if existing_act:
                act_id = str(existing_act["id"])
                skipped += 1
            else:
                act_number = (meta.get("folio") or code.split("-", 1)[-1] or code)[:32]
                issued = parse_doc_date(meta, str(doc.get("created_at") or ""))
                issued_at = (
                    datetime.combine(issued, time.min, tzinfo=timezone.utc)
                    if issued
                    else doc["created_at"]
                )
                state_code = map_act_state(meta.get("estado", ""))
                state_id = await resolve_category(db, "act_state", state_code)

                act_meta = {
                    "document_id": str(doc["id"]),
                    "document_code": code,
                    "document_source": meta.get("_etl_source"),
                    "tipo_resolucion": meta.get("tipo_resolucion"),
                    "solicita": meta.get("solicita"),
                    "firma_raw": meta.get("firma"),
                    "estado_raw": meta.get("estado"),
                    "storage_url": doc.get("storage_url"),
                    "_etl_phase": "2c",
                }

                if dry_run:
                    log.info(
                        f"[DRY-RUN][RES_ACT] INSERT act_number={act_number} code={code} "
                        f"state={state_code}"
                    )
                    inserted_acts += 1
                    act_id = f"dry-run-{code}"
                else:
                    res = await db.execute(
                        text(
                            """
                            INSERT INTO core.administrative_act
                                (act_number, act_type_id, subject, issuer_id, issued_at, state_id, metadata)
                            VALUES
                                (:act_number, :act_type_id, :subject, :issuer_id, :issued_at, :state_id, CAST(:meta AS jsonb))
                            RETURNING id
                            """
                        ),
                        {
                            "act_number": act_number,
                            "act_type_id": act_type_id,
                            "subject": (doc["name"] or "(Sin materia)")[:2000],
                            "issuer_id": issuer_id,
                            "issued_at": issued_at,
                            "state_id": state_id,
                            "meta": json.dumps(act_meta, ensure_ascii=False),
                        },
                    )
                    act_id = str(res.scalar_one())
                    inserted_acts += 1

            if not act_id:
                errors.append(f"Resolution doc {code}: cannot resolve act_id")
                continue

            if not dry_run:
                existing_res = (
                    await db.execute(
                        text(
                            """
                            SELECT id
                            FROM core.resolution
                            WHERE administrative_act_id = :act_id
                            LIMIT 1
                            """
                        ),
                        {"act_id": act_id},
                    )
                ).mappings().first()
                if existing_res:
                    skipped += 1
                    await batch_commit(db, row_num, dry_run)
                    continue

            rtype_code = map_resolution_type(doc["name"] or "")
            rtype_id = await resolve_category(db, "resolution_type", rtype_code)
            if not rtype_id:
                errors.append(f"Resolution doc {code}: category not found resolution_type/{rtype_code}")
                continue

            res_meta = {
                "document_id": str(doc["id"]),
                "document_code": code,
                "document_source": meta.get("_etl_source"),
                "resolution_type_inferred": rtype_code,
                "tipo_resolucion_raw": meta.get("tipo_resolucion"),
                "_etl_phase": "2c",
            }

            if dry_run:
                log.info(
                    f"[DRY-RUN][RESOLUTION] INSERT doc={code} type={rtype_code}"
                )
                inserted_resolutions += 1
            else:
                await db.execute(
                    text(
                        """
                        INSERT INTO core.resolution
                            (administrative_act_id, resolution_type_id, metadata)
                        VALUES
                            (:act_id, :rtype_id, CAST(:meta AS jsonb))
                        """
                    ),
                    {
                        "act_id": act_id,
                        "rtype_id": rtype_id,
                        "meta": json.dumps(res_meta, ensure_ascii=False),
                    },
                )
                inserted_resolutions += 1

            await batch_commit(db, row_num, dry_run)

        except Exception as e:
            errors.append(f"Resolution doc {code}: {e}")

    return inserted_acts, inserted_resolutions, skipped, errors


async def load_renditions_if_linked(
    db,
    dry_run: bool,
    limit: int,
    insert_if_linked: bool,
    crosswalk_path: Path | None,
    allow_fallback_direct_match: bool,
) -> tuple[int, int, int, int, list[str]]:
    """Insert renditions only when linkage is explicit and deterministic."""
    inserted = 0
    linked = 0
    unresolved = 0
    skipped = 0
    errors: list[str] = []

    rendition_state_id = await resolve_category(db, "rendition_state", "PENDIENTE")

    agreements = (
        await db.execute(
            text(
                """
                SELECT id, agreement_number
                FROM core.agreement
                WHERE deleted_at IS NULL
                  AND agreement_number IS NOT NULL
                """
            )
        )
    ).mappings().all()
    agreement_by_norm = {normalize_code(a["agreement_number"]): str(a["id"]) for a in agreements}

    crosswalk, cw_errors, crosswalk_loaded = await load_crosswalk(
        db,
        crosswalk_path,
        require_file=insert_if_linked,
    )
    errors.extend(cw_errors)
    if insert_if_linked and (not crosswalk_loaded or cw_errors):
        errors.append("Rendition insertion aborted: crosswalk file is missing or invalid.")
        return inserted, linked, unresolved, skipped, errors

    q = text(
        """
        SELECT id, code, name, created_at, metadata
        FROM core.document
        WHERE deleted_at IS NULL
          AND metadata->>'_etl_source' = ANY(:sources)
        ORDER BY code
        """
    )
    docs = (await db.execute(q, {"sources": list(RENDITION_SOURCES)})).mappings().all()
    if limit > 0:
        docs = docs[:limit]

    row_num = 0
    for doc in docs:
        row_num += 1
        code = doc["code"]
        meta = doc["metadata"] or {}

        try:
            existing = (
                await db.execute(
                    text(
                        """
                        SELECT id
                        FROM core.rendition
                        WHERE metadata->>'document_code' = :doc_code
                          AND deleted_at IS NULL
                        LIMIT 1
                        """
                    ),
                    {"doc_code": code},
                )
            ).mappings().first()
            if existing:
                skipped += 1
                continue

            legacy_code = (meta.get("codigo") or "").strip()
            norm_legacy = normalize_code(legacy_code)
            agreement_id = None
            renderer_id = None

            cw = crosswalk.get(norm_legacy) if norm_legacy else None
            if cw and cw.get("status") == "approved":
                agreement_id = cw.get("resolved_agreement_id")

                renderer_org_id = cw.get("renderer_org_id") or ""
                if renderer_org_id:
                    exists_renderer = (
                        await db.execute(
                            text(
                                """
                                SELECT id
                                FROM core.organization
                                WHERE deleted_at IS NULL
                                  AND id = :id
                                LIMIT 1
                                """
                            ),
                            {"id": renderer_org_id},
                        )
                    ).mappings().first()
                    if exists_renderer:
                        renderer_id = str(exists_renderer["id"])

                if not renderer_id and cw.get("renderer_name"):
                    renderer_id = await resolve_org_by_name(db, cw["renderer_name"])

            if not agreement_id and allow_fallback_direct_match and legacy_code:
                agreement_id = agreement_by_norm.get(norm_legacy)

            org_name = (meta.get("institucion") or doc.get("name") or "").strip()
            if not renderer_id:
                renderer_id = await resolve_org_by_name(db, org_name) if org_name else None

            if not agreement_id or not renderer_id:
                unresolved += 1
                continue

            linked += 1
            if not insert_if_linked:
                continue

            rend_meta = {
                "document_id": str(doc["id"]),
                "document_code": code,
                "document_source": meta.get("_etl_source"),
                "legacy_codigo": legacy_code,
                "crosswalk_status": (cw or {}).get("status"),
                "renderer_name_raw": org_name,
                "_etl_phase": "2c",
            }

            submitted_date = parse_doc_date(meta, str(doc.get("created_at") or ""))
            submitted_at = (
                datetime.combine(submitted_date, time.min, tzinfo=timezone.utc)
                if submitted_date
                else doc["created_at"]
            )

            if dry_run:
                log.info(
                    f"[DRY-RUN][RENDITION] INSERT doc={code} agreement={agreement_id[:8]}..."
                )
            else:
                await db.execute(
                    text(
                        """
                        INSERT INTO core.rendition
                            (agreement_id, renderer_id, state_id, submitted_at, metadata)
                        VALUES
                            (:agreement_id, :renderer_id, :state_id, :submitted_at, CAST(:meta AS jsonb))
                        """
                    ),
                    {
                        "agreement_id": agreement_id,
                        "renderer_id": renderer_id,
                        "state_id": rendition_state_id,
                        "submitted_at": submitted_at,
                        "meta": json.dumps(rend_meta, ensure_ascii=False),
                    },
                )
                inserted += 1

            await batch_commit(db, row_num, dry_run)

        except Exception as e:
            errors.append(f"Rendition doc {code}: {e}")

    return inserted, linked, unresolved, skipped, errors


async def run_phase_2c(
    dry_run: bool,
    limit: int,
    issuer_org_code: str | None,
    insert_renditions_if_linked: bool,
    rendition_crosswalk: Path | None,
    allow_fallback_direct_match: bool,
) -> ETLStats:
    stats = ETLStats()
    db = await get_session()

    try:
        act_ins, res_ins, skipped_res, err_res = await load_resolution_entities(
            db=db,
            dry_run=dry_run,
            limit=limit,
            issuer_org_code=issuer_org_code,
        )

        ren_ins, ren_linked, ren_unresolved, ren_skipped, err_ren = await load_renditions_if_linked(
            db=db,
            dry_run=dry_run,
            limit=limit,
            insert_if_linked=insert_renditions_if_linked,
            crosswalk_path=rendition_crosswalk,
            allow_fallback_direct_match=allow_fallback_direct_match,
        )

        stats.inserted = act_ins + res_ins + ren_ins
        stats.skipped = skipped_res + ren_skipped + ren_unresolved
        stats.errors = err_res + err_ren

        log.info(
            "Phase 2C diagnostics: "
            f"acts_inserted={act_ins}, resolutions_inserted={res_ins}, "
            f"renditions_inserted={ren_ins}, renditions_linked={ren_linked}, "
            f"renditions_unresolved={ren_unresolved}, skipped={stats.skipped}, errors={len(stats.errors)}"
        )

        if not dry_run:
            await db.commit()
            log.info("Phase 2C commit done")

    finally:
        await db.close()
        await close_engine()

    return stats


def main():
    parser = base_argparser(
        "ETL Phase 2C: Project document layer to administrative_act/resolution/rendition"
    )
    parser.add_argument(
        "--issuer-org-code",
        type=str,
        default="GORE-NUBLE",
        help="Organization code to use as issuer for administrative acts",
    )
    parser.add_argument(
        "--insert-renditions-if-linked",
        action="store_true",
        help="Insert into core.rendition only for linkable rows (default is audit-only).",
    )
    parser.add_argument(
        "--rendition-crosswalk",
        type=str,
        default=str(DEFAULT_CROSSWALK_PATH),
        help=f"CSV crosswalk path for rendition linkage (default: {DEFAULT_CROSSWALK_PATH})",
    )
    parser.add_argument(
        "--allow-fallback-direct-match",
        action="store_true",
        help="Allow fallback by direct normalized legacy_codigo == agreement_number (off by default).",
    )
    args = parser.parse_args()

    if args.verbose:
        setup_logging(verbose=True)

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log.info(f"=== ETL Phase 2C: load_admin_acts [{mode}] ===")

    async def _run():
        stats = await run_phase_2c(
            dry_run=args.dry_run,
            limit=args.limit,
            issuer_org_code=args.issuer_org_code,
            insert_renditions_if_linked=args.insert_renditions_if_linked,
            rendition_crosswalk=Path(args.rendition_crosswalk) if args.rendition_crosswalk else None,
            allow_fallback_direct_match=args.allow_fallback_direct_match,
        )
        stats.log_summary("Phase 2C")
        if args.insert_renditions_if_linked and any("crosswalk" in e.lower() for e in stats.errors):
            log.error("Strict rendition mode failed due to crosswalk validation errors.")
            sys.exit(1)
        if stats.total_processed > 0:
            error_rate = len(stats.errors) / stats.total_processed
            if error_rate > 0.10:
                log.warning(f"Error rate {error_rate:.1%} > 10%")
                sys.exit(1)

    run_async(_run())


if __name__ == "__main__":
    main()
