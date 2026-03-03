# ADR-004: Categorical Univocity — ref.category(scheme, code, label)

**Status**: Accepted
**Date**: 2026-03-03
**Deciders**: GORE_OS development team

## Context

The GORE_OS domain model requires dozens of controlled vocabularies: alert severities, agreement states, budget subtitles, problem types, system roles, and more. A naive approach allocates one lookup table per vocabulary, producing dozens of small tables with identical structure. This creates table proliferation, schema noise, and repetitive JOIN boilerplate.

## Decision

Use a single polymorphic reference table `ref.category(scheme, code, label, sort_order)` with a `scheme` discriminator column. Every FK column in the domain points to exactly ONE scheme. This is the **Categorical Univocity** rule: one FK column → one scheme.

## Current scale

95+ schemes including: `alert_type`, `alert_severity`, `agreement_state` (13 codes), `agreement_type`, `budget_subtitle`, `dgi_initiative_status`, `dgi_report_type`, `evaluator_type`, `ipr_party_role`, `payment_status`, `problem_type`, `session_type`, `system_role`, `vote_option`, and more.

## Consequences

- **No table proliferation**: Adding a new vocabulary requires only inserting rows into `ref.category`, not creating a new table.
- **Uniform query pattern**: `JOIN ref.category c ON c.id = entity.fk_col WHERE c.scheme = 'scheme_name'` is consistent across all FK lookups.
- **No cross-scheme contamination**: The FK points to only one scheme by design. A `CHECK` constraint plus the `fn_validate_category_scheme` trigger enforces this at the DB level.
- **DGI schemes are production-only**: Schemes like `dgi_initiative_status` are NOT in the seed SQL; they exist in `goreos_model` and are copied to `goreos_test` via `pg_dump COPY`. Never seed them manually in test scripts.
- **Adding new schemes**: Insert into `ref.category` in production first, then the test DB picks them up via `setup_test_db.sh`.
