# Agent Instructions — GORE_OS

## Source of Truth

**[CLAUDE.md](CLAUDE.md)** is the canonical reference for architecture, data model, coding rules, conventions, and domain logic. Read it fully before making any changes.

## Agent Priorities

1. **Story-First**: Every code change must trace to a user story in `model/stories/`. If no story exists, create one first.
2. **Categorical Univocity**: Every FK → exactly one `ref.category` scheme. 100% CHECK coverage. See [ADR-004](docs/adr/ADR-004-category-pattern.md) and [ADR-007](docs/adr/ADR-007-categorical-univocity.md).
3. **Integration Tests**: 730 tests against real PostgreSQL. No mocks. See [ADR-005](docs/adr/ADR-005-test-strategy.md).
4. **Raw SQL**: SQLAlchemy `text()`, no ORM. See [ADR-002](docs/adr/ADR-002-raw-sql.md).

## Key References

| Need | Go to |
|------|-------|
| Architecture, DB rules, conventions | [CLAUDE.md](CLAUDE.md) |
| ERD + data dictionary (121 tables) | [model/model_goreos/docs/GOREOS_ERD_v3.md](model/model_goreos/docs/GOREOS_ERD_v3.md) |
| Glossary (244 terms) | [model/GLOSARIO.yml](model/GLOSARIO.yml) |
| Design decisions | [model/model_goreos/docs/DESIGN_DECISIONS.md](model/model_goreos/docs/DESIGN_DECISIONS.md) |
| Testing guide | [docs/GORE_OS_Testing_Ciclo3.md](docs/GORE_OS_Testing_Ciclo3.md) |
| ADRs | [docs/adr/](docs/adr/) |
| Implementation plans | [docs/plans/README.md](docs/plans/README.md) |

## Critical Rules (cheat sheet)

- Column naming: `names`, `paternal_surname` (NOT `nombre`/`apellido_paterno`). `system_role_id` (NOT `role_id`). `org_type_id` (NOT `organization_type_id`).
- `ref.category` scheme = one FK column → one scheme. Never mix.
- asyncpg: NO `:param::jsonb` → use `CAST(:param AS jsonb)`. Always `datetime.now(timezone.utc)`.
- DB trigger errors → HTTP 409 (rollback first).
- Frontend: `formatDate`/`formatCLP` from `@/lib/format` only. `ComboboxAsync` for 500+ options. `PageHeader` for all list pages.
- DDL migrations via `scripts/run_migrations.sh`, never apply `goreos_ddl.sql` directly.
- idiom: Spanish for user communication, English for code and commits.