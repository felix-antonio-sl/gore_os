#!/usr/bin/env python3
"""Restore a private GORE custom dump into an explicitly selected empty target.

The caller prepares PostgreSQL, roles and a template0 database in isolation.
Catalog data precedes core CHECK functions that query ref.category. Every
archive entry and constraint is retained; restoration is one transaction.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from uuid import uuid4


def run(command: list[str], payload: bytes | None = None) -> bytes:
    result = subprocess.run(command, input=payload, capture_output=True)
    if result.returncode:
        raise SystemExit("Restore refused or failed; no rows or private SQL diagnostic emitted.")
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--archive", required=True, type=Path)
    args = parser.parse_args()
    client = ["docker", "exec", "-i", args.container]
    state = run(client + ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-U", args.user,
                          "-d", args.database, "-At"], b"""
SELECT (SELECT count(*) FROM pg_namespace WHERE nspname IN ('core','meta','ref','txn'))
     + (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE c.relkind IN ('r','p') AND n.nspname NOT IN ('pg_catalog','information_schema')
          AND n.nspname NOT LIKE 'pg_%');
""")
    if state.strip() != b"0":
        raise SystemExit("Restore requires an empty target; existing state is preserved.")
    toc = run(client + ["pg_restore", "--list"], args.archive.read_bytes()).decode()
    lines = toc.splitlines()
    references = [line for line in lines if " TABLE DATA ref " in line]
    if not any(" TABLE DATA ref category " in line for line in references):
        raise SystemExit("The archive does not contain the required GORE reference catalog.")
    start = next(i for i, line in enumerate(lines) if " TABLE DATA " in line)
    ordered = lines[:start] + references + [line for line in lines[start:] if line not in references]
    if Counter(ordered) != Counter(lines):
        raise SystemExit("Restore ordering changed the archive inventory.")
    target = "/tmp/gore-restore-" + uuid4().hex
    run(["docker", "exec", args.container, "mkdir", "-m", "700", target])
    try:
        with TemporaryDirectory(prefix="gore-restore-") as temporary:
            listing = Path(temporary) / "restore.list"
            listing.write_text("\n".join(ordered) + "\n")
            run(["docker", "cp", str(listing), args.container + ":" + target + "/restore.list"])
        # Custom archives need seekable input when their data order changes.
        run(["docker", "cp", str(args.archive.resolve()), args.container + ":" + target + "/database.dump"])
        run(["docker", "exec", args.container, "chmod", "600", target + "/database.dump", target + "/restore.list"])
        run(["docker", "exec", args.container, "pg_restore", "--exit-on-error",
             "--single-transaction", "--use-list=" + target + "/restore.list",
             "-U", args.user, "-d", args.database, target + "/database.dump"])
    finally:
        subprocess.run(["docker", "exec", args.container, "rm", "-rf", target], capture_output=True)
    print(json.dumps({"status": "RESTORED", "reference_data_entries_reordered": len(references),
                      "all_archive_entries_preserved": True, "constraints_kept": True,
                      "single_transaction": True, "seekable_private_archive": True}))


if __name__ == "__main__":
    main()
