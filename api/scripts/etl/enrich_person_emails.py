"""
ETL Phase 1c — Enrich core.person.email from contacts CSV.

Functor H: C_CONTACTS -> C_DB(core.person.email)
  Object mapping: contact row -> person.email attribute
  Identity preservation: person identity remains anchored by existing core.person rows
  Safety: update only when email is empty (unless --allow-overwrite)

Usage:
  docker compose exec api python -m scripts.etl.enrich_person_emails --dry-run
  docker compose exec api python -m scripts.etl.enrich_person_emails --verbose
  docker compose exec api python -m scripts.etl.enrich_person_emails --domain goredenuble.cl
"""

import json
import re
import sys
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
    read_csv,
    run_async,
    setup_logging,
)

ETL_DATA_DIR = Path("/app/data/etl/contacts")
DEFAULT_CONTACTS_FILE = "contacts_2026-02-26.csv"

_PARTICLES = {"de", "del", "la", "las", "los", "el", "y", "e"}


def _tokenize(raw: str) -> set[str]:
    tokens = set(normalize_text(raw).split())
    return {t for t in tokens if t and t not in _PARTICLES}


def _normalize_email(raw: str) -> str:
    return (raw or "").strip().lower()


def _email_tokens(email: str) -> tuple[set[str], set[str]]:
    local = email.split("@", 1)[0]
    parts = [p for p in re.split(r"[._\-]+", normalize_text(local)) if p]
    if len(parts) >= 2:
        return {parts[0]}, {parts[-1]}
    if len(parts) == 1:
        return {parts[0]}, set()
    return set(), set()


def _build_people_index(person_cache: dict[str, dict]) -> dict[str, dict]:
    people: dict[str, dict] = {}
    for person in person_cache.values():
        pid = str(person["id"])
        if pid in people:
            continue

        names = person.get("names", "") or ""
        paternal = person.get("paternal_surname", "") or ""
        maternal = person.get("maternal_surname", "") or ""

        name_tokens = _tokenize(names)
        surname_tokens = _tokenize(f"{paternal} {maternal}")
        all_tokens = name_tokens | surname_tokens

        people[pid] = {
            "id": pid,
            "names": names,
            "paternal_surname": paternal,
            "maternal_surname": maternal,
            "email": person.get("email", "") or "",
            "name_tokens": name_tokens,
            "surname_tokens": surname_tokens,
            "all_tokens": all_tokens,
        }

    return people


def _match_contact(
    first_name: str,
    middle_name: str,
    last_name: str,
    email: str,
    people: dict[str, dict],
    infer_from_email: bool = True,
) -> tuple[dict | None, str]:
    first_tokens = _tokenize(f"{first_name} {middle_name}")
    last_tokens = _tokenize(last_name)

    if not first_tokens and not last_tokens and infer_from_email:
        first_tokens, last_tokens = _email_tokens(email)

    if not first_tokens and not last_tokens:
        return None, "no_name_tokens"

    scored: list[tuple[int, str, dict]] = []

    for pid, person in people.items():
        surname_overlap = len(last_tokens & person["surname_tokens"]) if last_tokens else 0
        name_overlap = len(first_tokens & person["name_tokens"]) if first_tokens else 0

        if last_tokens and surname_overlap == 0:
            continue
        if first_tokens and name_overlap == 0:
            continue
        if not first_tokens and surname_overlap < 2:
            continue

        all_overlap = len((first_tokens | last_tokens) & person["all_tokens"])
        score = (surname_overlap * 3) + (name_overlap * 2) + all_overlap
        if score > 0:
            scored.append((score, pid, person))

    if not scored:
        return None, "no_match"

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0]
    top = [row for row in scored if row[0] == top_score]

    if len(top) > 1:
        return None, "ambiguous"

    return top[0][2], "matched"


async def enrich_person_emails(
    contacts_path: Path,
    dry_run: bool = False,
    limit: int = 0,
    domain: str = "goredenuble.cl",
    allow_overwrite: bool = False,
    infer_from_email: bool = True,
) -> ETLStats:
    stats = ETLStats()

    if not contacts_path.exists():
        stats.errors.append(f"Contacts file not found: {contacts_path}")
        return stats

    try:
        rows = read_csv(contacts_path)
    except (FileNotFoundError, ValueError) as e:
        stats.errors.append(str(e))
        return stats

    db = await get_session()

    try:
        person_cache = await build_person_cache(db)
        people = _build_people_index(person_cache)

        dedup_by_email: dict[str, dict] = {}
        duplicate_rows = 0

        for row in rows:
            email = _normalize_email(row.get("E-mail 1 - Value", ""))
            if not email:
                continue

            if domain:
                suffix = f"@{domain.lower()}"
                if not email.endswith(suffix):
                    continue

            candidate = {
                "first_name": row.get("First Name", "").strip(),
                "middle_name": row.get("Middle Name", "").strip(),
                "last_name": row.get("Last Name", "").strip(),
                "email": email,
            }
            token_count = len(_tokenize(
                f"{candidate['first_name']} {candidate['middle_name']} {candidate['last_name']}"
            ))
            candidate["token_count"] = token_count

            prev = dedup_by_email.get(email)
            if prev is None or token_count > prev["token_count"]:
                dedup_by_email[email] = candidate
            elif prev is not None:
                duplicate_rows += 1

        contacts = list(dedup_by_email.values())
        if limit > 0:
            contacts = contacts[:limit]

        log.info(f"Contacts loaded: {len(rows)} rows, {len(dedup_by_email)} unique emails")
        log.info(f"Filtered domain: {domain or '*'}")
        if duplicate_rows:
            log.info(f"Deduplicated duplicate contact rows: {duplicate_rows}")

        row_num = 0
        unmatched = 0
        ambiguous = 0

        for contact in contacts:
            row_num += 1
            email = contact["email"]

            person, reason = _match_contact(
                contact["first_name"],
                contact["middle_name"],
                contact["last_name"],
                email,
                people,
                infer_from_email=infer_from_email,
            )

            if not person:
                if reason == "ambiguous":
                    ambiguous += 1
                    stats.errors.append(f"Ambiguous match for {email}")
                else:
                    unmatched += 1
                    stats.skipped += 1
                continue

            existing_email = _normalize_email(person.get("email", ""))
            if existing_email and not allow_overwrite:
                if existing_email == email:
                    stats.skipped += 1
                else:
                    stats.errors.append(
                        f"Email conflict for {person['names']} {person['paternal_surname']}: "
                        f"DB={existing_email}, contact={email}"
                    )
                continue

            meta_patch = {
                "email_source": contacts_path.name,
                "email_etl_phase": "1c",
            }

            if dry_run:
                log.info(
                    f"[DRY-RUN] SET email {email} -> "
                    f"{person['names']} {person['paternal_surname']} "
                    f"(id={person['id'][:8]}...)"
                )
            else:
                await db.execute(
                    text("""
                        UPDATE core.person
                        SET email = :email,
                            metadata = COALESCE(metadata, '{}'::jsonb) || CAST(:meta AS jsonb),
                            updated_at = NOW()
                        WHERE id = :pid
                    """),
                    {
                        "email": email,
                        "meta": json.dumps(meta_patch, ensure_ascii=False),
                        "pid": person["id"],
                    },
                )
                person["email"] = email

            stats.updated += 1
            await batch_commit(db, row_num, dry_run)

        if not dry_run:
            await db.commit()
            log.info("Email enrichment commit done")

        log.info(
            f"Matching diagnostics: updated={stats.updated}, skipped={stats.skipped}, "
            f"unmatched={unmatched}, ambiguous={ambiguous}, errors={len(stats.errors)}"
        )

    finally:
        await db.close()
        await close_engine()

    return stats


def main():
    parser = base_argparser("ETL Phase 1c: Enrich core.person.email from contacts CSV")
    parser.add_argument(
        "--contacts",
        type=str,
        default=str(ETL_DATA_DIR / DEFAULT_CONTACTS_FILE),
        help=f"Path to contacts CSV (default: {ETL_DATA_DIR / DEFAULT_CONTACTS_FILE})",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="goredenuble.cl",
        help="Only process emails ending with this domain (empty string = no filter)",
    )
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="Allow overwriting existing core.person.email values",
    )
    parser.add_argument(
        "--no-infer-from-email",
        action="store_true",
        help="Disable fallback token inference from email local-part",
    )
    args = parser.parse_args()

    if args.verbose:
        setup_logging(verbose=True)

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    log.info(f"=== ETL Phase 1c: enrich_person_emails [{mode}] ===")

    async def _run():
        stats = await enrich_person_emails(
            contacts_path=Path(args.contacts),
            dry_run=args.dry_run,
            limit=args.limit,
            domain=args.domain,
            allow_overwrite=args.allow_overwrite,
            infer_from_email=not args.no_infer_from_email,
        )
        stats.log_summary("enrich_person_emails")
        if stats.total_processed > 0:
            error_rate = len(stats.errors) / stats.total_processed
            if error_rate > 0.15:
                log.warning(f"Error rate {error_rate:.1%} > 15%")
                sys.exit(1)

    run_async(_run())


if __name__ == "__main__":
    main()
