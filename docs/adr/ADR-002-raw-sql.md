# ADR-002: Raw SQL via text() vs ORM Models

**Status**: Accepted
**Date**: 2026-03-03
**Deciders**: GORE_OS development team

## Context

The system interacts with a PostgreSQL database of 80 tables spread across 4 schemas (meta, ref, core, txn). Many queries involve multi-schema JOINs, raw aggregations, JSONB operations, partitioned tables, and PostgreSQL-specific features such as `pg_advisory_xact_lock`, `jsonb_set`, and generated columns. An ORM layer would require either extensive customization or would produce suboptimal queries for these patterns.

## Decision

Use raw SQL via SQLAlchemy `text()` for all database operations. No ORM model classes. All queries use `db.execute(text("..."), params).mappings()` to return dict-like row objects.

## Rationale

- **Direct PostgreSQL mapping**: Queries map 1:1 to the logical schema — no translation layer to debug.
- **No impedance mismatch**: Schema uses advanced PostgreSQL features (generated columns, partitioned tables, JSONB, advisory locks) that ORM layers handle poorly or incompletely.
- **Complex queries**: Many endpoints require multi-table JOINs across schemas with conditional filters built at runtime. Raw SQL handles this cleanly via f-string clause construction.
- **Performance clarity**: SQL is explicit and auditable — no N+1 surprises from lazy loading.
- **Pydantic for validation**: Input/output validation is done at the API boundary via Pydantic v2 schemas, not at the ORM layer.

## Consequences

- **No model layer for validation**: Column name typos surface at runtime, not compile time. Mitigated by integration tests against a real DB.
- **Manual column name management**: PATCH endpoints require an explicit `_ALLOWLIST` of permitted field names.
- **Schema evolution is manual**: Migrations are plain SQL files, not auto-generated.
- **Asyncpg type cast caveat**: Do NOT use `:param::type` syntax — asyncpg interprets `::` as a parameter boundary. Use `CAST(:param AS type)` instead.
