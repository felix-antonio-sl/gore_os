"""
ETL Phase 2 — Load PARTES CSVs → core.document.

Functor F: C_PARTES → C_DB(core.document)
  Objects: PARTES CSV sources (Phase 2 + Phase 2B extensions)
  Morphisms: column mappings per source → core.document columns
  Idempotence: ON CONFLICT (code) DO NOTHING

Tension A1[Evento ↔ Entidad]: Documents are institutional records (entities),
not events. Each row maps 1:1 to one core.document. No colimit needed.

Usage:
  docker compose exec api python -m scripts.etl.load_documents --dry-run
  docker compose exec api python -m scripts.etl.load_documents
  docker compose exec api python -m scripts.etl.load_documents --source RECIBIDOS
"""

import csv
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
# Custom readers for malformed multi-block CSVs
# ---------------------------------------------------------------------------

def read_rendiciones_fndr_adnc(path: Path) -> list[dict]:
    """Read dual-block CSV (FNDR + ADNC/ADCD) into normalized row dicts."""
    rows: list[dict] = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        raw = list(csv.reader(f, delimiter=",", quotechar='"'))

    # Data starts at row 4; each physical row may contain up to two renditions.
    for idx, row in enumerate(raw[4:], start=5):
        if len(row) < 13:
            continue

        def add_row(
            block: str,
            code: str,
            fecha_dcto: str,
            fecha_ingreso: str,
            fecha_entrega: str,
            institucion: str,
        ):
            code = code.strip()
            if not code:
                return
            rows.append(
                {
                    "CODIGO": code,
                    "FECHA DCTO": fecha_dcto.strip(),
                    "FECHA INGRESO": fecha_ingreso.strip(),
                    "FECHA ENTREGA": fecha_entrega.strip(),
                    "NOMBRE INSTITUCIÓN": institucion.strip(),
                    "BLOQUE": block,
                    "ROW_INDEX": str(idx),
                }
            )

        add_row("FNDR", row[1], row[2], row[3], row[4], row[5])
        add_row("ADNC_ADCD", row[8], row[9], row[10], row[11], row[12])

    return rows


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
    # static metadata fields added to all rows from this source
    fixed_meta: dict[str, str] = field(default_factory=dict)
    # custom row reader for malformed CSV structures
    custom_reader: Callable[[Path], list[dict]] | None = None


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
    SourceConfig(
        name="RENDICIONES_2024",
        filename="RENDICIONES 2024.csv",
        prefix="REN24",
        skip_rows=3,  # header starts at row 3
        id_col="CÓDIGO",
        name_col="NOMBRE DE LA INICIATIVA",
        type_col="",
        default_type="RENDICION",
        url_col="",
        channel_col="",
        meta_cols=[
            ("correlativo",      "CORRELATIVO"),
            ("tipo_documento",   "TIPO DOCUMENTO"),
            ("codigo",           "CÓDIGO"),
            ("fecha_dcto",       "FECHA DCTO"),
            ("fecha_ingreso",    "FECHA INGRESO"),
            ("fecha_entrega",    "FECHA ENTREGA"),
            ("institucion",      "NOMBRE INSTITUCIÓN"),
            ("monto_rendicion",  "MONTO DE LA RENDICIÓN"),
            ("recepcionado_por", "RECEPCIONADO POR"),
            ("firma",            "FIRMA"),
        ],
    ),
    SourceConfig(
        name="RENDICIONES_FNDR_ADNC",
        filename="RENDICIONES FNDR Y ADNC.csv",
        prefix="RENX",
        id_col="CODIGO",
        name_col="NOMBRE INSTITUCIÓN",
        type_col="",
        default_type="RENDICION",
        url_col="",
        channel_col="",
        meta_cols=[
            ("codigo",        "CODIGO"),
            ("fecha_dcto",    "FECHA DCTO"),
            ("fecha_ingreso", "FECHA INGRESO"),
            ("fecha_entrega", "FECHA ENTREGA"),
            ("institucion",   "NOMBRE INSTITUCIÓN"),
            ("bloque",        "BLOQUE"),
            ("row_index",     "ROW_INDEX"),
        ],
        custom_reader=read_rendiciones_fndr_adnc,
    ),
    SourceConfig(
        name="RESOLUCIONES_AFECTAS",
        filename="RESOLUCIONES AFECTAS.csv",
        prefix="RFA",
        id_col="FOLIO",
        name_col="MATERIA",
        type_col="",
        default_type="RESOLUCION",
        url_col="LINK AL DOCUMENTO",
        channel_col="OBSERVACIONES",
        meta_cols=[
            ("solicita",      "SOLICITA"),
            ("folio",         "FOLIO"),
            ("fecha_docto",   "FECHA DOCTO"),
            ("firma",         "FIRMA"),
            ("observaciones", "OBSERVACIONES"),
            ("estado",        "ESTADO"),
        ],
        fixed_meta={"tipo_resolucion": "AFECTA"},
    ),
    SourceConfig(
        name="RESOLUCIONES_EXENTAS",
        filename="RESOLUCIONES EXENTAS.csv",
        prefix="REX",
        id_col="FOLIO",
        name_col="MATERIA",
        type_col="",
        default_type="RESOLUCION",
        url_col="LINK AL DOCUMENTO",
        channel_col="OBSERVACIONES",
        meta_cols=[
            ("solicita",      "SOLICITA"),
            ("folio",         "FOLIO"),
            ("fecha_docto",   "FECHA DOCTO"),
            ("firma",         "FIRMA"),
            ("observaciones", "OBSERVACIONES"),
        ],
        fixed_meta={"tipo_resolucion": "EXENTA"},
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
        if cfg.custom_reader:
            rows = cfg.custom_reader(filepath)
        else:
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

            if cfg.fixed_meta:
                meta.update(cfg.fixed_meta)

            meta["_etl_source"] = cfg.filename

            if dry_run:
                log.info(
                    f"[DRY-RUN][{cfg.name}] INSERT code={code} name={name[:50]!r}"
                    f" type={raw_tipo or cfg.default_type}"
                )
                stats.inserted += 1
                continue

            result = await db.execute(
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
            if result.rowcount and result.rowcount > 0:
                stats.inserted += 1
            else:
                stats.skipped += 1

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
