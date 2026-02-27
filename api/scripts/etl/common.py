"""
ETL Common Module — Shared utilities for all ETL pipelines.

Categorical framing:
  F: C_CSV → C_DB  (functor from source to target category)
  FK resolution = morphism composition via cached lookups
  Batch commit = colimit over transaction chunks

Usage:
  docker compose exec api python -m scripts.etl.<module> [--dry-run] [--limit N]
"""

import argparse
import asyncio
import csv
import logging
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(verbose: bool = False) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("etl")


log = setup_logging()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def base_argparser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--dry-run", action="store_true", help="Log actions without writing to DB")
    p.add_argument("--limit", type=int, default=0, help="Process only first N rows (0=all)")
    p.add_argument("--verbose", action="store_true", help="Debug-level logging")
    return p


# ---------------------------------------------------------------------------
# Database — reuses API Settings for connection string
# ---------------------------------------------------------------------------

_engine = None
_session_factory = None


def _get_database_url() -> str:
    """Build DB URL from environment or defaults (same as api/app/core/config.py)."""
    import os
    user = os.getenv("DB_USER", "goreos")
    password = os.getenv("DB_PASSWORD", "goreos_2026")
    host = os.getenv("DB_HOST", "goreos_db")  # container network name
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "goreos_model")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


async def get_session() -> AsyncSession:
    global _engine, _session_factory
    if _engine is None:
        url = _get_database_url()
        _engine = create_async_engine(url, echo=False, pool_pre_ping=True)
        _session_factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _session_factory()


async def close_engine():
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None


# ---------------------------------------------------------------------------
# CSV Reader — auto-detects encoding and delimiter
# ---------------------------------------------------------------------------

_ENCODINGS = ["utf-8-sig", "latin-1", "cp1252"]
_DELIMITERS = [",", ";"]


def read_csv(path: str | Path, encoding: str | None = None,
             delimiter: str | None = None,
             skip_rows: int = 0) -> list[dict]:
    """Read CSV with auto-detection of encoding and delimiter.

    Returns list of dicts with stripped keys and values.
    Handles BOM (utf-8-sig) and latin-1 Chilean CSVs.

    Delimiter detection: tries both ',' and ';', picks whichever produces
    more columns in the header (greedy heuristic). This avoids false matches
    when a field name contains embedded commas.

    skip_rows: number of rows to skip BEFORE the header row.
    Use for files with garbage first rows.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    encodings = [encoding] if encoding else _ENCODINGS
    delimiters = [delimiter] if delimiter else _DELIMITERS

    best_result: list[dict] | None = None
    best_cols = 0
    best_enc = ""
    best_delim = ""

    for enc in encodings:
        try:
            with open(path, encoding=enc, newline="") as f:
                for _ in range(skip_rows):
                    f.readline()
                sample = f.read(4096)
        except UnicodeDecodeError:
            continue

        for delim in delimiters:
            try:
                # Count columns using csv.reader on the header (respects quoting)
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

    # Now read the full file with the best encoding+delimiter
    with open(path, encoding=best_enc, newline="") as f:
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
            if any(cleaned.values()):
                rows.append(cleaned)

    log.debug(f"Read {len(rows)} rows from {path.name} [{best_enc}, delim='{best_delim}', {best_cols} cols]")
    return rows


# ---------------------------------------------------------------------------
# Name Parser — CSV "Apellido1 Apellido2, Nombres" → structured
# ---------------------------------------------------------------------------

@dataclass
class ParsedName:
    names: str
    paternal_surname: str
    maternal_surname: str = ""

    @property
    def full_display(self) -> str:
        parts = [self.names, self.paternal_surname]
        if self.maternal_surname:
            parts.append(self.maternal_surname)
        return " ".join(parts)


def parse_fullname(raw: str) -> ParsedName:
    """Parse 'Apellido1 Apellido2, Nombres' into structured components.

    Morphism: String → ParsedName (deterministic, total on well-formed input).
    Examples:
        'Aburto Contreras, Abraham Aníbal' → ParsedName(names='Abraham Aníbal', paternal='Aburto', maternal='Contreras')
        'González, María'                  → ParsedName(names='María', paternal='González', maternal='')
    """
    raw = raw.strip()
    if "," not in raw:
        # Fallback: assume "Nombre Apellido"
        parts = raw.split()
        if len(parts) >= 2:
            return ParsedName(names=" ".join(parts[:-1]), paternal_surname=parts[-1])
        return ParsedName(names=raw, paternal_surname="")

    apellidos_part, nombres_part = raw.split(",", 1)
    apellidos = apellidos_part.strip().split()
    nombres = nombres_part.strip()

    paternal = apellidos[0] if apellidos else ""
    maternal = " ".join(apellidos[1:]) if len(apellidos) > 1 else ""

    return ParsedName(names=nombres, paternal_surname=paternal, maternal_surname=maternal)


# ---------------------------------------------------------------------------
# Text normalization — for fuzzy matching
# ---------------------------------------------------------------------------

def normalize_text(s: str) -> str:
    """Normalize for comparison: lowercase, strip accents, collapse whitespace."""
    s = s.strip().lower()
    # Decompose unicode, strip combining marks (accents)
    nfkd = unicodedata.normalize("NFKD", s)
    stripped = "".join(c for c in nfkd if not unicodedata.category(c).startswith("M"))
    return re.sub(r"\s+", " ", stripped)


# ---------------------------------------------------------------------------
# Date / Amount / RUT parsers
# ---------------------------------------------------------------------------

def parse_date(s: str) -> date | None:
    """Parse date from DD-MM-YYYY, DD/MM/YYYY, or YYYY-MM-DD formats."""
    if not s or not s.strip():
        return None
    s = s.strip()
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(s: str) -> Decimal | None:
    """Parse Chilean currency: '$ 1.827.026', '$1827026', '1.827.026'.

    Morphism: String → Decimal (partial — returns None on unparseable).
    """
    if not s or not s.strip():
        return None
    s = s.strip()
    # Remove $ sign and whitespace
    s = s.replace("$", "").strip()
    # Remove thousand separators (dots) but keep decimal comma
    # Chilean format: 1.827.026 (dots are thousands)
    if "," in s and "." in s:
        # e.g., "1.827.026,50" → "1827026.50"
        s = s.replace(".", "").replace(",", ".")
    elif "." in s:
        # Could be thousands or decimal — if multiple dots, they're thousands
        if s.count(".") > 1:
            s = s.replace(".", "")
        # Single dot with >2 digits after → thousands separator
        elif "." in s:
            after_dot = s.split(".")[-1]
            if len(after_dot) == 3:
                s = s.replace(".", "")
    s = s.replace(",", ".")
    # Remove any remaining non-numeric chars except . and -
    s = re.sub(r"[^\d.\-]", "", s)
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def normalize_rut(rut: str) -> str | None:
    """Normalize RUT to XX.XXX.XXX-V format. Returns None if invalid."""
    if not rut or not rut.strip():
        return None
    # Strip everything except digits and K/k
    cleaned = re.sub(r"[^0-9kK]", "", rut.strip())
    if len(cleaned) < 2:
        return None
    body = cleaned[:-1]
    dv = cleaned[-1].upper()
    # Format with dots
    body_int = int(body)
    formatted = f"{body_int:,}".replace(",", ".")
    return f"{formatted}-{dv}"


# ---------------------------------------------------------------------------
# FK Resolvers — cached morphism composition
# ---------------------------------------------------------------------------

# In-memory cache: scheme → {code → uuid}
_category_cache: dict[str, dict[str, str]] = {}


async def resolve_category(db: AsyncSession, scheme: str, code: str) -> str | None:
    """Resolve ref.category(scheme, code) → UUID string. Cached per scheme."""
    if scheme not in _category_cache:
        result = await db.execute(
            text("SELECT id, code FROM ref.category WHERE scheme = :scheme"),
            {"scheme": scheme},
        )
        _category_cache[scheme] = {row["code"]: str(row["id"]) for row in result.mappings()}
        log.debug(f"Cached {len(_category_cache[scheme])} codes for scheme '{scheme}'")

    return _category_cache[scheme].get(code)


async def resolve_category_by_label(db: AsyncSession, scheme: str, label: str) -> str | None:
    """Resolve ref.category by label (case-insensitive). Slower — use code when possible."""
    cache_key = f"{scheme}__labels"
    if cache_key not in _category_cache:
        result = await db.execute(
            text("SELECT id, label FROM ref.category WHERE scheme = :scheme"),
            {"scheme": scheme},
        )
        _category_cache[cache_key] = {}
        for row in result.mappings():
            normalized = normalize_text(row["label"])
            _category_cache[cache_key][normalized] = str(row["id"])

    return _category_cache[cache_key].get(normalize_text(label))


# Person cache: normalized(paternal + names) → {id, names, paternal_surname, ...}
_person_cache: dict[str, dict] = {}


async def build_person_cache(db: AsyncSession) -> dict[str, dict]:
    """Load all active persons into cache keyed by normalized name."""
    global _person_cache
    if _person_cache:
        return _person_cache

    result = await db.execute(text("""
        SELECT id, names, paternal_surname, maternal_surname,
               email, rut, estamento_id, metadata
        FROM core.person
        WHERE deleted_at IS NULL
    """))
    for row in result.mappings():
        key = normalize_text(f"{row['paternal_surname']} {row['names']}")
        _person_cache[key] = dict(row)
        # Also index by full name (paternal + maternal + names) for disambiguation
        if row.get("maternal_surname"):
            full_key = normalize_text(
                f"{row['paternal_surname']} {row['maternal_surname']} {row['names']}"
            )
            _person_cache[full_key] = dict(row)

    log.info(f"Person cache: {len(_person_cache)} entries from {len(set(str(v['id']) for v in _person_cache.values()))} persons")
    return _person_cache


async def resolve_person_by_name(db: AsyncSession, parsed: ParsedName) -> dict | None:
    """Match a ParsedName to an existing core.person record.

    Strategy: try exact (paternal + names), then fuzzy (paternal + maternal + names).
    """
    cache = await build_person_cache(db)

    # Try primary key: paternal + names
    key1 = normalize_text(f"{parsed.paternal_surname} {parsed.names}")
    if key1 in cache:
        return cache[key1]

    # Try full key: paternal + maternal + names
    if parsed.maternal_surname:
        key2 = normalize_text(
            f"{parsed.paternal_surname} {parsed.maternal_surname} {parsed.names}"
        )
        if key2 in cache:
            return cache[key2]

    return None


async def resolve_org_by_name(db: AsyncSession, name: str) -> str | None:
    """Resolve organization by name (case-insensitive substring match)."""
    result = await db.execute(
        text("""
            SELECT id FROM core.organization
            WHERE deleted_at IS NULL
              AND (LOWER(name) = LOWER(:name) OR LOWER(short_name) = LOWER(:name))
            LIMIT 1
        """),
        {"name": name.strip()},
    )
    row = result.mappings().first()
    return str(row["id"]) if row else None


async def resolve_ipr_by_bip(db: AsyncSession, codigo_bip: str) -> str | None:
    """Resolve IPR by codigo_bip."""
    result = await db.execute(
        text("SELECT id FROM core.ipr WHERE codigo_bip = :bip AND deleted_at IS NULL LIMIT 1"),
        {"bip": codigo_bip.strip()},
    )
    row = result.mappings().first()
    return str(row["id"]) if row else None


async def resolve_territory_by_name(db: AsyncSession, name: str) -> str | None:
    """Resolve territory by name (case-insensitive)."""
    result = await db.execute(
        text("SELECT id FROM core.territory WHERE LOWER(name) = LOWER(:name) LIMIT 1"),
        {"name": name.strip()},
    )
    row = result.mappings().first()
    return str(row["id"]) if row else None


# ---------------------------------------------------------------------------
# Stats tracking
# ---------------------------------------------------------------------------

@dataclass
class ETLStats:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_processed(self) -> int:
        return self.inserted + self.updated + self.skipped + len(self.errors)

    def log_summary(self, label: str = "ETL"):
        log.info(f"{'='*50}")
        log.info(f"{label} Summary:")
        log.info(f"  Inserted: {self.inserted}")
        log.info(f"  Updated:  {self.updated}")
        log.info(f"  Skipped:  {self.skipped}")
        log.info(f"  Errors:   {len(self.errors)}")
        log.info(f"  Total:    {self.total_processed}")
        if self.errors:
            log.info(f"  First 10 errors:")
            for err in self.errors[:10]:
                log.info(f"    - {err}")
        log.info(f"{'='*50}")


# ---------------------------------------------------------------------------
# Batch commit helper
# ---------------------------------------------------------------------------

BATCH_SIZE = 100


async def batch_commit(db: AsyncSession, row_num: int, dry_run: bool = False):
    """Commit every BATCH_SIZE rows unless dry_run."""
    if not dry_run and row_num > 0 and row_num % BATCH_SIZE == 0:
        await db.commit()
        log.debug(f"Committed batch at row {row_num}")


# ---------------------------------------------------------------------------
# Async runner
# ---------------------------------------------------------------------------

def run_async(coro):
    """Run an async coroutine from sync context (script entrypoint)."""
    asyncio.run(coro)
