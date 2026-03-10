# ADR-007: Categorical Univocity Enforcement

**Status**: Accepted
**Date**: 2026-03-09
**Deciders**: Auditoría Categorial v6

## Context

GORE_OS uses `ref.category(scheme, code, label, metadata)` as a terminal object for 83+ controlled vocabulary schemes (~420 codes). Every FK column pointing to `ref.category` must reference exactly ONE scheme — this is the **Categorical Univocity** principle.

An audit of the DDL identified 78 FK→ref.category columns across 52 tables. Only 21 had validation (6 CHECK constraints + 15 via trigger functions). The remaining 57 columns had no enforcement, allowing cross-scheme corruption.

## Decision

1. **Add 37 CHECK constraints** via migration `goreos_migration_categorical_univocity.sql` for all columns with confirmed scheme mappings (verified against live DB).
2. **Extend `fn_validate_ipr_schemes()`** to validate 10 columns (was 5), adding `ipr_type_id`, `funding_source_id`, `investment_sector_id`, `fund_category_id`, `resolution_type_id`.
3. **Leave ~20 columns unvalidated** — orphan tables (vehicle, platform, risk, asset) and columns with unconfirmed scheme names. These are documented for future remediation.
4. **Add `"type": "informational"` field** to gate return dicts in `ipr.py` for 4 informational gates, making the blocking/informational distinction explicit in the API response.

## Rationale

- CHECK constraints are declarative — they survive trigger deletion and provide a second safety layer.
- Triggers provide richer error messages and can enforce complex multi-column rules.
- Both layers together form a defense-in-depth strategy for Categorical Univocity.
- The `fn_validate_category_scheme()` function already exists in the DDL and is battle-tested.

## Related Findings

### S-01: DDL Circular Dependencies
`goreos_ddl.sql` defines `fn_validate_category_scheme()` AFTER tables that need it in CHECK constraints, and `core.person` references `core.position` (defined later). This is a known PostgreSQL bootstrap limitation. Workaround: never apply DDL directly to fresh DB — use `pg_dump --schema-only` from production. Documented in CLAUDE.md Rule 19.

### D-01: Orphan Tables
7 tables in DDL have 0 API endpoints and 0 frontend references: `vehicle`, `digital_platform`, `risk`, `asset`, `procedure`, `financing_instrument`, `territorial_indicator`. These are placeholders for future domains (D-BACK, D-SEG, D-TERR). No action needed — they cause no harm and will be activated when their domains are implemented.

### D-03: Pydantic→TypeScript Codegen
TypeScript interfaces in `web/src/types/index.ts` are manually maintained duplicates of Pydantic schemas. A codegen pipeline (e.g., `pydantic-to-typescript` or `openapi-typescript`) would eliminate drift. This is a low-priority improvement — current drift is minimal due to integration tests catching mismatches.

## Consequences

- 37+6+7 = **50 CHECK constraints** now enforce Categorical Univocity (was 6).
- `fn_validate_ipr_schemes()` validates **10/14** IPR FK→ref.category columns.
- Orphan FK columns remain unvalidated but are harmless (no write path exists).
- Gate responses now include explicit `"type"` field for API consumers.
- Migration is idempotent (`DROP CONSTRAINT IF EXISTS` + `ADD CONSTRAINT`).
