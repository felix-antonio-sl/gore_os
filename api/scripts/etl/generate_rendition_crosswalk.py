"""
Generate/refresh manual crosswalk for rendition linkage.

Output:
  /app/data/etl/crosswalk/rendition_agreement_crosswalk.csv (default in container)

This script is non-destructive: existing manual fields are preserved by legacy code.
"""

import argparse
import csv
from pathlib import Path

from sqlalchemy import text

from scripts.etl.common import get_session, close_engine, run_async, log, normalize_text

RENDITION_SOURCES = ("RENDICIONES 2024.csv", "RENDICIONES FNDR Y ADNC.csv")
DEFAULT_OUT = Path("/app/data/etl/crosswalk/rendition_agreement_crosswalk.csv")

FIELDS = [
    "legacy_codigo",
    "agreement_number",
    "agreement_id",
    "renderer_org_id",
    "renderer_name",
    "status",
    "confidence",
    "notes",
    "document_count",
    "sample_document_code",
    "sample_source",
    "sample_institucion",
    "auto_candidate_count",
]


def normalize_code(raw: str) -> str:
    import re

    return re.sub(r"[^A-Za-z0-9]", "", (raw or "").upper())


def load_existing(path: Path) -> dict[str, dict]:
    existing: dict[str, dict] = {}
    if not path.exists():
        return existing

    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            legacy = (row.get("legacy_codigo") or "").strip()
            key = normalize_code(legacy)
            if not key:
                continue
            existing[key] = row
    return existing


async def generate_crosswalk(out_path: Path):
    db = await get_session()
    try:
        docs = (
            await db.execute(
                text(
                    """
                    SELECT code, metadata
                    FROM core.document
                    WHERE deleted_at IS NULL
                      AND metadata->>'_etl_source' = ANY(:sources)
                    """
                ),
                {"sources": list(RENDITION_SOURCES)},
            )
        ).mappings().all()

        agreements = (
            await db.execute(
                text(
                    """
                    SELECT agreement_number
                    FROM core.agreement
                    WHERE deleted_at IS NULL
                      AND agreement_number IS NOT NULL
                    """
                )
            )
        ).mappings().all()
        agreement_norms = {normalize_code(a["agreement_number"]) for a in agreements}

        grouped: dict[str, dict] = {}
        for d in docs:
            meta = d["metadata"] or {}
            legacy = (meta.get("codigo") or "").strip()
            if not legacy:
                continue
            key = normalize_code(legacy)
            if not key:
                continue

            bucket = grouped.setdefault(
                key,
                {
                    "legacy_codigo": legacy,
                    "document_count": 0,
                    "sample_document_code": d["code"],
                    "sample_source": meta.get("_etl_source", ""),
                    "sample_institucion": (meta.get("institucion") or "")[:200],
                },
            )
            bucket["document_count"] += 1

        existing = load_existing(out_path)

        rows_out: list[dict] = []
        for key in sorted(grouped):
            g = grouped[key]
            ex = existing.get(key, {})

            auto_candidates = 1 if key in agreement_norms else 0

            row = {
                "legacy_codigo": g["legacy_codigo"],
                "agreement_number": (ex.get("agreement_number") or "").strip(),
                "agreement_id": (ex.get("agreement_id") or "").strip(),
                "renderer_org_id": (ex.get("renderer_org_id") or "").strip(),
                "renderer_name": (ex.get("renderer_name") or g["sample_institucion"]).strip(),
                "status": (ex.get("status") or "pending").strip().lower(),
                "confidence": (ex.get("confidence") or "").strip(),
                "notes": (ex.get("notes") or "").strip(),
                "document_count": str(g["document_count"]),
                "sample_document_code": g["sample_document_code"],
                "sample_source": g["sample_source"],
                "sample_institucion": g["sample_institucion"],
                "auto_candidate_count": str(auto_candidates),
            }
            rows_out.append(row)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows_out)

        approved = sum(1 for r in rows_out if normalize_text(r["status"]) == "approved")
        auto_matchable = sum(1 for r in rows_out if r["auto_candidate_count"] == "1")

        log.info(f"Crosswalk written: {out_path}")
        log.info(f"Rows: {len(rows_out)} | approved: {approved} | auto_candidate_count=1: {auto_matchable}")

    finally:
        await db.close()
        await close_engine()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate/refresh rendition-agreement crosswalk from staged documents."
    )
    parser.add_argument(
        "--out",
        type=str,
        default=str(DEFAULT_OUT),
        help=f"Output CSV path (default: {DEFAULT_OUT})",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    out = Path(args.out)

    async def _run():
        await generate_crosswalk(out)

    run_async(_run())


if __name__ == "__main__":
    main()
