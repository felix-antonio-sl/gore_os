# UX Remediation Wave 4 — Design

**Date**: 2026-03-10
**Approach**: Remediation-first — close 12 open findings (8 quick wins + 3 ALTO + 1 color unification) to raise closure from 45% → 67%.

## Context

UX Audit v2.0 (2026-03-09): 55 findings total, 25 closed, 30 open. This wave targets the highest-impact subset: 8 quick wins (~2.5h), status color unification (UX-022, ~2-3h), and 3 remaining ALTO items (~5h).

## Wave 4A — Quick Wins CSS/A11y (8 items)

Atomic 1-3 line changes, no new logic or endpoints.

| ID | File | Change |
|----|------|--------|
| UX-013 | `login/page.tsx` | Replace hardcoded `text-[#031B5F]` with CSS token |
| UX-015 | `cockpit-td.tsx` | Wrap VIG/PAR/PEN badges in shadcn Tooltip with full label |
| UX-016 | `login/page.tsx` | Add email regex validation in handleSubmit |
| UX-025 | `header.tsx` | Add `role="button" tabIndex={0} onKeyDown` to alert popover items |
| UX-031 | `admin/usuarios/page.tsx` | Add `disabled={len < 8}` + helper text on reset password |
| UX-040 | `cockpit-control-gestion.tsx` | Add `hidden md:block` on sparkline containers |
| UX-041 | `cockpit-control-gestion.tsx` | Change gray badge text to `text-gray-800` for WCAG AA 4.5:1 |
| UX-048 | `presupuesto/page.tsx` | Add Tooltip explaining execution formula |

## Wave 4B — Status Color Unification (1 item)

UX-022: Centralize semantic status colors. Currently 3 independent color maps:
- `status-badge.tsx`: 16 states with hardcoded Tailwind classes
- `kpi-card.tsx`: 6 color props (red/orange/amber/green/blue/gray)
- `semaforo-card.tsx`: 3 signals (VERDE/AMARILLO/ROJO)
- `sparkline-indicator.tsx`: 3 hex signals

Create a shared `STATUS_COLORS` map in `lib/colors.ts` and migrate all 4 components.

## Wave 4C — ALTO Funcional (3 items)

| ID | File | Effort | Change |
|----|------|--------|--------|
| UX-011 | `cockpit-jefe-dgi.tsx` + backend | 1-2d | Connect "Requieren Mi Decisión" with real data (pending initiatives, overdue renditions, unreviewed reports) |
| UX-030 | `admin/usuarios/page.tsx` | 2-3h | Add inline form validation (email format, required fields, error display) |
| UX-047 | `presupuesto/page.tsx` + backend | 1d | Enable PATCH of budget classifier fields post-creation with consistency validation |

## Result

Closure: 25/55 (45%) → 37/55 (67%). Dimensions improved: Accesibilidad (Medio→Medio-Alto), Consistencia Visual (Medio→Medio-Alto), Funcionalidad (Medio-Alto→Alto).
