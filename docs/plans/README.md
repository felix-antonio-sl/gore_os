# Implementation Plans — GORE_OS

> Updated: 2026-06-09. All plans reviewed against codebase.

## Domain: SISREC / Renditions

| File | Type | Description | Status |
|------|------|-------------|--------|
| [2026-03-08-sisrec-8phase.md](2026-03-08-sisrec-8phase.md) | Plan | SISREC 8-phase CGR cycle | ✅ Implemented |
| [2026-03-08-sisrec-8phase-design.md](2026-03-08-sisrec-8phase-design.md) | Design | FSM design for 8-phase SISREC | ✅ Implemented |

## Domain: Budget & Finance

| File | Type | Description | Status |
|------|------|-------------|--------|
| [2026-03-08-budget-classifier-level5.md](2026-03-08-budget-classifier-level5.md) | Plan | Budget classifier Level 5 (DIPRES) | ✅ Implemented |
| [2026-03-08-budget-classifier-level5-design.md](2026-03-08-budget-classifier-level5-design.md) | Design | Classification hierarchy | ✅ Implemented |
| [2026-03-08-budget-cycle-timeline.md](2026-03-08-budget-cycle-timeline.md) | Plan | Budget cycle milestones (17 rows) | ✅ Implemented |
| [2026-03-09-budget-classifier-complete-design.md](2026-03-09-budget-classifier-complete-design.md) | Design | Complete budget classifier | ✅ Implemented |

## Domain: Parametric Tables

| File | Type | Description | Status |
|------|------|-------------|--------|
| [2026-03-08-parametric-tables-tp01-02-04.md](2026-03-08-parametric-tables-tp01-02-04.md) | Plan | Routing, funds, taxonomy tables | ✅ Implemented |
| [2026-03-08-parametric-tables-tp01-02-04-design.md](2026-03-08-parametric-tables-tp01-02-04-design.md) | Design | Parametric table architecture | ✅ Implemented |

## Domain: IPR Lifecycle & Rules

| File | Type | Description | Status |
|------|------|-------------|--------|
| [2026-03-08-parentesco-8pct.md](2026-03-08-parentesco-8pct.md) | Plan | Kinship declaration for SUBV8 | ✅ Implemented |
| [2026-03-08-parentesco-8pct-design.md](2026-03-08-parentesco-8pct-design.md) | Design | Kinship gate at F1→F2 | ✅ Implemented |
| [2026-03-09-admissibility-substates.md](2026-03-09-admissibility-substates.md) | Plan | PRE_ADMISIBLE gate | ✅ Implemented |
| [2026-03-09-admissibility-substates-design.md](2026-03-09-admissibility-substates-design.md) | Design | Admissibility check + C33 cert | ✅ Implemented |
| [2026-03-09-c33-technical-certification.md](2026-03-09-c33-technical-certification.md) | Plan | C33 conservation certification | ✅ Implemented |
| [2026-03-09-c33-technical-certification-design.md](2026-03-09-c33-technical-certification-design.md) | Design | C33 as blocking gate | ✅ Implemented |

## Domain: UX/UI

| File | Type | Description | Status |
|------|------|-------------|--------|
| [2026-03-10-wave2-polish.md](2026-03-10-wave2-polish.md) | Plan | Wave 2 UI polish | ✅ Implemented |
| [2026-03-10-wave2-polish-design.md](2026-03-10-wave2-polish-design.md) | Design | Wave 2 design decisions | ✅ Implemented |
| [2026-03-10-wave3-motion.md](2026-03-10-wave3-motion.md) | Plan | Wave 3 motion/animation | ✅ Implemented |
| [2026-03-10-wave3-motion-design.md](2026-03-10-wave3-motion-design.md) | Design | Wave 3 motion system | ✅ Implemented |
| [2026-03-10-ux-remediation-wave4-design.md](2026-03-10-ux-remediation-wave4-design.md) | Design | Wave 4 accessibility | ✅ Implemented |
| [2026-03-10-ux-wave4a-quickwins.md](2026-03-10-ux-wave4a-quickwins.md) | Plan | Wave 4a UX quick wins | ✅ Implemented |
| [2026-03-10-ux-wave4c-alto-funcional.md](2026-03-10-ux-wave4c-alto-funcional.md) | Plan | Wave 4c ALTO functional | ✅ Implemented |
| [2026-03-10-ux-wave5a-quickwins.md](2026-03-10-ux-wave5a-quickwins.md) | Plan | Wave 5a quick wins | ✅ Implemented |
| [2026-03-10-ux-wave5b-medium.md](2026-03-10-ux-wave5b-medium.md) | Plan | Wave 5b medium improvements | ✅ Implemented |

## Status Legend

| Icon | Meaning |
|------|---------|
| ✅ | Implemented — matching code exists in the repo (DB tables, API endpoints, UI components, tests) |
| 🔲 | Pending — plan exists but no matching code yet |
| ⛔ | Obsolete — plan targets removed/abandoned features |

All 23 plans in this directory are **implemented**. Design documents (`-design.md`) are superseded by the shipped code but retained for decision traceability.