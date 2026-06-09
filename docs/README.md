# GORE_OS — Documentation Index

> **SSOT**: [CLAUDE.md](../CLAUDE.md) is the source of truth for architecture, data model, rules, and conventions.
> This index organizes all secondary documentation by purpose and currency.

---

## Entry Points

| Doc | Audience | Purpose |
|-----|----------|---------|
| [CLAUDE.md](../CLAUDE.md) | Developers, Agents | Architecture, data model, rules, commands, conventions |
| [INDEX.md](../INDEX.md) | All | navigable repo map, ADR index, model status |
| [MANIFESTO.md](../MANIFESTO.md) | All | project identity, philosophy, 5 motor functions |
| [ONBOARDING.md](ONBOARDING.md) | New developers | setup, patterns, how to add a feature |

## Specifications & Audits

These documents capture institutional knowledge. **CLAUDE.md supersedes specifications** — if conflicts exist, CLAUDE.md wins.

| Document | Date | Status | Content |
|----------|------|--------|---------|
| [GORE_OS_Audit_v3.0.md](GORE_OS_Audit_v3.0.md) | 2026-03-08 | **Current** | Institutional audit: 4-source triangulation, 472 CQs, coverage ~55% |
| [GORE_OS_Audit_C59.md](GORE_OS_Audit_C59.md) | 2026-03-22 | **Current** | Session C59 live audit: 121 findings (10 critical) with concrete fixes |
| [GORE_OS_Audit_Detail_v1.0.md](GORE_OS_Audit_Detail_v1.0.md) | 2026-02-27 | Superseded by v3.0 | Per-story coverage detail; lower-level version of audit v3.0 |
| [GORE_OS_UX_Audit_v2.0.md](GORE_OS_UX_Audit_v2.0.md) | 2026-03 | **Current** | UX audit: 54/55 findings closed (98%) |
| [AUDITORIA_CATEGORIAL_v3.0.md](AUDITORIA_CATEGORIAL_v3.0.md) | 2026-01-30 | **Completed** | JSONB categorical audit: 13 critical, 16 medium normalizations identified |
| [AUDITORIA_RELACIONAL_v1.0.md](AUDITORIA_RELACIONAL_v1.0.md) | 2026-01-30 | **Current reference** | Relational audit: 183 FKs, hub analysis, 5 graphs, critical chains |
| [GORE_OS_Specification_v1.0.md](GORE_OS_Specification_v1.0.md) | 2026-02-25 | Superseded by CLAUDE.md | Original functional/technical spec — CLAUDE.md is now more current |

## Domain & UX Specs

| Document | Content |
|----------|---------|
| [GORE_OS_User_Journeys_v3.0.md](GORE_OS_User_Journeys_v3.0.md) | 8 archetypes, 17 journeys, 8 UX principles |
| [GORE_OS_User_Action_Trees_v1.0.md](GORE_OS_User_Action_Trees_v1.0.md) | 24 users, 304 endpoints, per-role action trees |
| [GORE_OS_Role_Surface_Spec_v1.0.md](GORE_OS_Role_Surface_Spec_v1.0.md) | 15 roles → 38 routes + IDOR scoping |
| [DGI_USER_STORIES_v1.0.md](DGI_USER_STORIES_v1.0.md) | 185 DGI user stories with implementation status |
| [GORE_OS_Story_Coverage_v1.0.md](GORE_OS_Story_Coverage_v1.0.md) | Cross-reference: DGI stories vs implementation (26.5% effective coverage) |

## Testing

| Document | Content |
|----------|---------|
| [GORE_OS_Testing_Ciclo3.md](GORE_OS_Testing_Ciclo3.md) | **Primary testing guide** (v8.0): full suite, SISREC, parametric tables, HΩ-02, budget |
| [GORE_OS_Testing_Manual_v1.0.md](GORE_OS_Testing_Manual_v1.0.md) | Session C59 visual/manual test plan (per-role walkthroughs) |

## ETL & Data Pipeline

| Document | Content |
|----------|---------|
| [ETL_ARCHITECTURE_v1.0.md](ETL_ARCHITECTURE_v1.0.md) | ETL architecture for 8 legacy CSV domains (design, not yet implemented) |
| [ETL_DATA_BOUNDARY.md](ETL_DATA_BOUNDARY.md) | Separation rules: canonical sources vs runtime staging |

## Normalization (Historical)

These documents record the JSONB-to-relational normalization that is now **complete** (100% categorical univocity, 98 CHECK constraints). Kept for traceability.

| Document | Content |
|----------|---------|
| [PLAN_NORMALIZACION_JSONB_v2.0.md](PLAN_NORMALIZACION_JSONB_v2.0.md) | v2.0 normalization plan (post-audit corrections) — **completed** |
| [AUDITORIA_CATEGORIAL_NORMALIZACION_JSONB.md](AUDITORIA_CATEGORIAL_NORMALIZACION_JSONB.md) | Audit of v1 plan (rejected) → led to v2.0 |

## Architecture Decisions (ADRs)

| ADR | Topic | Status |
|-----|-------|--------|
| [ADR-001](adr/ADR-001-meta-schema.md) | Meta schema retention | Accepted |
| [ADR-002](adr/ADR-002-raw-sql.md) | Raw SQL via text() (no ORM) | Accepted |
| [ADR-003](adr/ADR-003-advisory-locks.md) | Advisory locks for code generators | Accepted |
| [ADR-004](adr/ADR-004-category-pattern.md) | Category Pattern (ref.category) | Accepted |
| [ADR-005](adr/ADR-005-test-strategy.md) | Integration tests against real PostgreSQL | Accepted |
| [ADR-006](adr/ADR-006-jwt-cookie-migration.md) | JWT → Cookie migration | **Deferred** |
| [ADR-007](adr/ADR-007-categorical-univocity.md) | 100% categorical univocity enforcement | Accepted |
| [ADR-008](adr/008-create-pattern-drawer-vs-page.md) | Drawer vs page for /nuevo | Accepted |

## Feature Specs

| Document | Content |
|----------|---------|
| [SPEC_Bug_Capture_System_v1.0.md](SPEC_Bug_Capture_System_v1.0.md) | In-app bug capture system (FAB + drawer, dev-only) |

## Implementation Plans

See [plans/README.md](plans/README.md) for indexed list with implementation status (all 23 plans: implemented).

## Superpowers (Advanced Features)

See [superpowers/README.md](superpowers/README.md) for indexed list with implementation status (5/6 implemented, 1 obsolete — targets external repo).

## Archived Material

Historical documents preserved for traceability. Not operational.

| Path | Content |
|------|---------|
| [archive/planning-feb2026/](archive/planning-feb2026/) | Feb 2026 ETL phases, backend test plans, early UI design |
| [archive/legacy-model-tel/](archive/legacy-model-tel/) | Legacy ETL sources, normalization v2/v3 docs, relational navigator |

## Model Documentation

| Document | Content |
|----------|---------|
| [../model/model_goreos/docs/GOREOS_ERD_v3.md](../model/model_goreos/docs/GOREOS_ERD_v3.md) | ERD + data dictionary (52 tables, 4 schemas) |
| [../model/model_goreos/docs/GOREOS_CONCEPTUAL_MODEL.md](../model/model_goreos/docs/GOREOS_CONCEPTUAL_MODEL.md) | Business-level conceptual model (6 domain areas) |
| [../model/model_goreos/docs/DESIGN_DECISIONS.md](../model/model_goreos/docs/DESIGN_DECISIONS.md) | DB design decisions: ENUM vs category, JSONB, partitioning |
| [../model/model_goreos/docs/GOREOS_NORMALIZATION_ANALYSIS.md](../model/model_goreos/docs/GOREOS_NORMALIZATION_ANALYSIS.md) | Normal form verification (1NF-BCNF) |
| [../model/GLOSARIO.yml](../model/GLOSARIO.yml) | 244 institutional terms |