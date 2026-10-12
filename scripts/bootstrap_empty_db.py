#!/usr/bin/env python3
"""Initialize an explicitly selected empty database from canonical catalogs.

Requires prior authorization and a verified private backup. No credentials,
people, organizations, indicators, demo cases or migration records are loaded.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def prepare_sql(repo: Path) -> tuple[str, dict]:
    sql_dir = repo / "model/model_goreos/sql"
    names = ("goreos_ddl.sql", "goreos_seed.sql", "goreos_seed_territory.sql")
    sources = {name: (sql_dir / name).read_text() for name in names}
    territory = re.search(r"DO \$\$.*?END \$\$;", sources[names[2]], re.DOTALL)
    if territory is None:
        raise ValueError("Canonical territory catalog block is absent")
    catalog = territory.group(0)
    if set(re.findall(r"INSERT INTO ([\w.]+)", catalog)) != {"core.territory"}:
        raise ValueError("Territory block contains an unexpected destination")
    catalog, columns = re.subn(r", area_km2, population(?=\))", "", catalog)
    catalog, values = re.subn(
        r", [0-9]+(?:\.[0-9]+)?, [0-9]+(?=\))", "", catalog
    )
    if columns != 25 or values != 25:
        raise ValueError("Expected exactly 25 canonical territories")
    destinations = set(re.findall(r"INSERT INTO ([\w.]+)", sources[names[1]]))
    if destinations != {"ref.category", "ref.actor", "ref.operational_commitment_type"}:
        raise ValueError("Reference seed contains an unexpected destination")
    guard = """
SELECT pg_advisory_xact_lock(hashtextextended('gore-os-empty-bootstrap', 0));
DO $$ BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_namespace
        WHERE nspname IN ('core', 'meta', 'ref', 'txn')
    ) OR EXISTS (
        SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r', 'p')
          AND n.nspname NOT IN ('pg_catalog', 'information_schema')
          AND n.nspname NOT LIKE 'pg_%'
    ) THEN
        RAISE EXCEPTION 'Bootstrap requires an empty database; existing state is preserved';
    END IF;
END $$;
"""
    sql = guard + sources[names[0]] + "\n" + sources[names[1]] + "\n" + catalog
    receipt = {
        "sources": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in sources.items()},
        "prepared_sql_sha256": hashlib.sha256(sql.encode()).hexdigest(),
        "territory_count": 25,
        "excluded": [
            "territorial statistics and indicators", "organization definitions",
            "user/core-member seeds", "realistic/demo/ETL seeds", "migration history",
        ],
    }
    return sql, receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    sql, receipt = prepare_sql(Path(__file__).resolve().parents[1])
    if not args.prepare_only:
        result = subprocess.run(
            ["docker", "exec", "-i", args.container, "psql", "-X",
             "--set=ON_ERROR_STOP=1", "--single-transaction",
             "-U", args.user, "-d", args.database, "-f", "-"],
            input=sql, text=True, capture_output=True,
        )
        if result.returncode:
            raise SystemExit("Bootstrap refused or failed; transaction rolled back. No rows or SQL log emitted.")
    print(json.dumps({"status": "PREPARED" if args.prepare_only else "APPLIED", **receipt}))


if __name__ == "__main__":
    main()
