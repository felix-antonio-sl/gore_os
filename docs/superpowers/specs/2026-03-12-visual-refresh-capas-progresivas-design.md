# Visual Refresh — Capas Progresivas

**Date**: 2026-03-12
**Status**: Approved
**Scope**: Pure frontend (Capas 2-3) + 1 backend endpoint (Capa 1)

## Context

GORE_OS tiene 55 páginas, 16 roles, 2 poblaciones. Tras completar la refactorización estructural (6 fases: sidebar semántico, breadcrumbs, PageGuard, URL tabs, dashboard decomposition, drawer unification), quedan **5 tensiones visuales/UX** que degradan la experiencia sin tocar la funcionalidad:

| ID | Tensión | Severidad |
|----|---------|-----------|
| T-A | Monotonía de listas — 15+ páginas visualmente idénticas | MEDIO |
| T-B | Cockpits sin identidad — 4 cockpits DGI sin diferenciación visual | MEDIO |
| T-C | Densidad de datos — tablas con poco soporte visual (solo badges) | MEDIO |
| T-D | Detail pages sin jerarquía — hero+stepper+tabs mecánicamente repetidos | BAJO |
| T-E | Sin experiencia de primer uso — usuario nuevo sin guía de qué hacer | ALTO |

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Visual direction | Centro de Comando Personal | Orientado a acción, personalizado por rol, contextual al día |
| Backend approach | Light backend (1 endpoint) | Colímite computado server-side — resuelve broken diagrams de owner/deadline |
| Dashboard layout | Unificado + módulos condicionales | Misma estructura base, bloques condicionales por arquetipo |
| Execution strategy | Capas progresivas (3 oleadas) | Impacto incremental, validable, deployable por capa |
| ENCARGADO role | Arquetipo ejecutor (inbox de trabajo) | Toda persona con tarea asignada sujeta a control de cumplimiento |

## Categorical Analysis

### ActionItem as Coproduct

The `action-items` endpoint constructs a coproduct (UNION ALL) of 6 heterogeneous sources:

```
Obj: {Commitment, Alert, ARDecision, Escalation, SLABreach, Risk}
η_i : Source_i → ActionItem
```

### Tension: Urgente ↔ Importante (A2: Temporal)

Initial design collapsed temporal urgency and severity into a single `urgency` field — a premature coequalizer. Resolved by modeling as a **product** `Temporal × Severity` with a derived total order:

- `temporal`: VENCIDO | HOY | ESTA_SEMANA | FUTURO | null (deadline-based, null for items without deadlines)
- `severity`: CRITICO | ALTO | MEDIO | BAJO (always defined, derived per source)
- `priority`: int (computed total order, 0 = maximum urgency)

### Broken Diagrams Resolved

1. **Alert → owner**: Alerts have no assignee. Resolved via derived morphism through subject FK (`subject_type → entity → assignee_id`)
2. **Alert → deadline**: Alerts have no deadline. Resolved by making `deadline` and `temporal` nullable
3. **Risk → owner**: Risks have no assignee. Scoping by role (filter), not by assignment

### Priority Computation

```python
def compute_priority(temporal: str | None, severity: str) -> int:
    SEV = {"CRITICO": 0, "ALTO": 1, "MEDIO": 2, "BAJO": 3}
    TEMP = {"VENCIDO": 0, "HOY": 1, "ESTA_SEMANA": 2, "FUTURO": 3, None: 4}
    return SEV.get(severity, 3) * 5 + TEMP.get(temporal, 4)
```

### Severity Mapping per Source

| Source | severity | Derivation |
|--------|----------|-----------|
| Commitment | from days_remaining | ALTO if overdue, MEDIO if ≤7d, BAJO if >7d |
| Alert | direct field (scheme `alert_level`) | CRITICO/ALTO/ATENCION→MEDIO/INFO→BAJO |
| ARDecision | from days_remaining | ALTO if due_date ≤3d, MEDIO otherwise |
| Escalation | from level | NIVEL_3-4→CRITICO, NIVEL_2→ALTO, NIVEL_1→MEDIO |
| SLA breach | always CRITICO | by definition (already past SLA) |
| Risk | from probability | MUY_ALTA→CRITICO, ALTA→ALTO |

## Architecture

### Capa 1: Comando (T-B, T-E)

#### Backend: `GET /api/dashboard/action-items`

```python
class ActionItem(BaseModel):
    id: str
    category: str                    # COMPROMISO|ALERTA|DECISION|ESCALAMIENTO|SLA|RIESGO
    title: str
    subtitle: str | None
    deadline: date | None
    days_remaining: int | None
    temporal: str | None             # VENCIDO|HOY|ESTA_SEMANA|FUTURO
    severity: str                    # CRITICO|ALTO|MEDIO|BAJO
    priority: int                    # total order (0 = max urgency)
    action_label: str                # "Completar"|"Decidir"|"Gestionar"|"Ver"
    action_route: str                # see action_route table below

class ActionItemsResponse(BaseModel):
    greeting_name: str               # user["nombre"].split()[0] — first token of nombre
    today: date
    summary: str                     # "Tienes 2 tareas vencidas"
    items: list[ActionItem]          # ORDER BY priority ASC
    counts: dict[str, int]           # by severity
```

**Note**: `greeting_name` is derived from `user["nombre"].split()[0]` — the user dict from `deps.py` exposes `nombre` (not `names`).

**Scoping by role**:

| Role | Sees | Does not see |
|------|------|-------------|
| ENCARGADO, ANALISTA, RTF, ASESOR_JURIDICO | Own commitments, alerts on own IPRs | AR decisions, escalations |
| JEFE_DIVISION, JEFE_DEPARTAMENTO, JEFE_UNIDAD | Division commitments, division alerts, level 1-2 escalations | AR decisions (unless delegated) |
| ADMIN_REGIONAL, GOBERNADOR, ADMIN_SISTEMA, SECRETARIO_EJECUTIVO, CONSEJERO_REGIONAL | All: global overdue commitments, CRITICO alerts, AR decisions, escalations, SLA, risks | — |
| JEFE_DGI | AR decisions, escalations, SLA breaches, high risks, CRITICO alerts | Operational commitments |
| ESP_* | SLA on their services, alerts on their indicators | AR decisions, escalations |

**`action_route` per category**:

| Category | action_route | action_label | Notes |
|----------|-------------|--------------|-------|
| COMPROMISO | `/compromisos` | Completar | List page — user finds their commitment |
| ALERTA | `/ipr/{subject_id}?tab=alertas` | Ver | Navigate to IPR alertas tab (most alerts are IPR-scoped) |
| DECISION | `/coordinacion` | Decidir | List page — AR decisions tab |
| ESCALAMIENTO | `/escalamiento/{id}` | Gestionar | Detail page exists |
| SLA | `/servicios/{service_id}` | Ver | Detail page — SLA tab |
| RIESGO | `/riesgos/{id}` | Gestionar | Detail page exists |

**`page.tsx` routing change**: Replace population-based branch with unified Centro de Comando for ALL roles:

```tsx
// BEFORE: population-based
if (user.population === "dgi") return <DgiCockpitRouter role={user.role_code} />;
return <OperationalDashboard user={user} />;

// AFTER: unified
return <CommandCenter user={user} />;
// DgiCockpitRouter remains accessible via sidebar "Monitoreo" section
// OperationalDashboard kept as deprecated fallback (remove in future)
```

#### Frontend: Centro de Comando Personal

```
dashboard/
├── page.tsx                          # orchestrator (modified)
├── components/
│   ├── command-center.tsx            # NEW — unified layout
│   ├── attention-strip.tsx           # NEW — urgent action-item cards
│   ├── module-my-progress.tsx        # NEW — ENCARGADO progress bar
│   ├── module-my-team.tsx            # NEW — JEFE_DIVISION team view
│   ├── module-dgi-team.tsx           # NEW — JEFE_DGI team status
│   ├── module-kpis.tsx              # NEW — compact KPIs + semáforo
│   ├── operational-dashboard.tsx     # existing (kept, deprecated path)
│   ├── dgi-cockpit-router.tsx        # existing (kept, accessed via sidebar)
│   └── cockpit-*.tsx                 # existing (unchanged)
```

**Layout structure**:
1. Contextual greeting (name + date + summary from action-items)
2. Attention strip (urgent action-items, max ~5, with action buttons)
3. Conditional module (Mi Progreso / Mi Equipo / Equipo DGI / Indicadores / Panorama)
4. Compact KPIs + semáforo

**Module assignment**:

| Module | Roles | Data source |
|--------|-------|-------------|
| Mi Progreso | ENCARGADO, ANALISTA, RTF, ASESOR_JURIDICO | `GET /api/dashboard/mis-compromisos` |
| Mi Equipo | JEFE_DIVISION, JEFE_DEPARTAMENTO, JEFE_UNIDAD | `GET /api/dashboard/mi-division` |
| Equipo DGI | JEFE_DGI | `GET /api/dgi/cockpit` → team_status |
| Indicadores | ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD | `GET /api/dgi/cockpit` → trends/work_queue |
| Panorama | ADMIN_REGIONAL, GOBERNADOR, ADMIN_SISTEMA, SECRETARIO_EJECUTIVO, CONSEJERO_REGIONAL | `GET /api/dashboard/ejecutivo` → divisions + semaforo |

**`module-kpis.tsx`**: Presentational wrapper, not a separate module. Receives data as props from `command-center.tsx` which already fetches the appropriate module data source. Renders 2-4 compact KPI cards + semáforo dots. Data varies by module: Mi Progreso → completion %, Mi Equipo → team load, Panorama → execution + alertas count. No independent API call.

**Existing cockpits**: DGI cockpits remain accessible via sidebar (Monitoreo section) as specialized deep-dive views. The Centro de Comando provides the unified entry point.

### Capa 2: Densidad Visual + Detail Template (T-C, T-D)

#### 2A: Table enrichment components

| Component | Purpose | Lines est. |
|-----------|---------|:----------:|
| `progress-cell.tsx` | Horizontal progress bar inline (% execution) | ~30 |
| `deadline-cell.tsx` | Deadline text + automatic semáforo color | ~35 |
| `trend-indicator.tsx` | Arrow ↑↓→ with color for trends | ~25 |

Usage: Replace plain `<span>` in DataTable columns for presupuesto, compromisos, convenios, escalamientos.

#### 2B: Detail page template

```tsx
// components/detail-page-layout.tsx (~100 lines)
interface DetailPageLayoutProps {
  breadcrumbLabel?: string;
  heroContent: ReactNode;
  stepper?: {
    phases: { code: string; label: string }[];
    currentPhase: string;
    phaseColors?: Record<string, string>;
  };
  transitionPanel?: ReactNode;
  children: ReactNode;
}
```

Opt-in wrapper for detail pages. Existing pages migrate incrementally. New pages adopt by default. **Note**: The `stepper` is display-only (no click navigation) — FSM interaction remains in each page's own `transitionPanel` slot. This mirrors the existing IPR stepper pattern (`ipr-phase-stepper.tsx`).

### Capa 3: Identidad por Dominio (T-A)

#### Domain color accents

| Domain | Accent color | Icon | Pages |
|--------|-------------|------|-------|
| IPR / Cartera | Indigo (`#4f46e5`) | FileStack | ipr, cartera |
| Compromisos / Problemas | Amber (`#d97706`) | ListChecks | compromisos, problemas |
| Finanzas | Emerald (`#059669`) | DollarSign | presupuesto, ciclo, convenios, rendiciones |
| Institucional | Violet (`#7c3aed`) | Building2 | actos, reuniones, core-sessions |
| Riesgos / Crisis | Rose (`#e11d48`) | ShieldAlert | riesgos, centro-de-mando, escalamiento |
| DGI Análisis | Cyan (`#0891b2`) | BarChart3 | datos, informes, tablero, procesos |
| Servicios | Teal (`#0d9488`) | Headphones | servicios, solicitar |

#### Implementation

Extend `PageHeader` with optional `accentColor` prop (Tailwind color name, e.g. `"indigo"`, `"amber"`) → renders 3px left border (`border-l-{color}-500`) + tinted section icon (`text-{color}-600`). Uses Tailwind classes (not raw hex) for dark mode compatibility with existing OKLCH system. ~5 lines in PageHeader + ~1 line per list page (15 pages).

#### Contextual empty states

Replace generic "No hay datos" with domain-specific descriptions in EmptyState components (~15 string changes).

## File Summary

### New files (10)

| # | File | Layer | Lines est. |
|---|------|:-----:|:----------:|
| 1 | `dashboard/components/command-center.tsx` | L1 | ~120 |
| 2 | `dashboard/components/attention-strip.tsx` | L1 | ~80 |
| 3 | `dashboard/components/module-my-progress.tsx` | L1 | ~60 |
| 4 | `dashboard/components/module-my-team.tsx` | L1 | ~80 |
| 5 | `dashboard/components/module-dgi-team.tsx` | L1 | ~60 |
| 6 | `dashboard/components/module-kpis.tsx` | L1 | ~70 |
| 7 | `components/progress-cell.tsx` | L2 | ~30 |
| 8 | `components/deadline-cell.tsx` | L2 | ~35 |
| 9 | `components/trend-indicator.tsx` | L2 | ~25 |
| 10 | `components/detail-page-layout.tsx` | L2 | ~100 |

### Modified files (~29)

| Layer | Files | Type of change |
|:-----:|:-----:|----------------|
| L1 | 4 | dashboard.py (+endpoint), schemas (+models), types/index.ts (+interfaces), page.tsx (orchestrator) |
| L2 | 9 | 6 list pages (use ProgressCell/DeadlineCell) + 3 detail pages (adopt DetailPageLayout). List pages: presupuesto, compromisos, convenios, escalamiento, riesgos, rendiciones |
| L3 | 16 | page-header.tsx (+accentColor) + 15 list pages (+accentColor prop + empty state text). **Overlap**: 6 L2 list pages also receive L3 accentColor — apply both in same commit to avoid double-touch |

### Totals

| Layer | New lines | Modified lines | Backend |
|:-----:|:---------:|:--------------:|:-------:|
| L1 | ~590 | ~165 | 1 endpoint (~120 LOC) |
| L2 | ~340 | ~150 | 0 |
| L3 | ~10 | ~45 | 0 |
| **Total** | **~940** | **~360** | **1 endpoint** |

## Dependency Graph

```
Capa 1 (Comando)      ← independent, do first (highest impact)
    │
    ├── Capa 2 (Densidad)  ← can use module-kpis patterns from L1
    │
    └── Capa 3 (Identidad) ← independent, can parallel with L2
```

## Verification

After all 3 layers:

1. **Build**: `cd web && npx next build` — 0 TypeScript errors
2. **API tests**: `docker compose exec api pytest -v` — all pass (only 1 new endpoint, existing unchanged)
3. **Visual smoke test** by archetype:
   - `encargado.daf@goreos.cl` → Centro de Comando with "Mi Progreso" module, attention strip with own commitments
   - `jefe.daf@goreos.cl` → Centro de Comando with "Mi Equipo" module showing team load
   - `regional@goreos.cl` → Centro de Comando with "Panorama" module, all action-items visible
   - `jefe.dgi@goreos.cl` → Centro de Comando with "Equipo DGI" module, AR decisions in attention strip
   - `control.gestion@goreos.cl` → Centro de Comando with "Indicadores" module
4. **Responsive**: Centro de Comando usable on 375px viewport (modules stack vertically)
5. **Domain accents**: Each list page shows distinct color accent in PageHeader (L3)
6. **Table enrichment**: Progress bars visible in presupuesto, deadline colors in compromisos (L2)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full notification system (DB persistence, read/unread, push) | Over-construction — materialized colimit introduces drift |
| Onboarding wizard / tutorial | Requires UX research on actual user flows |
| Dark mode adjustments for domain accents | Handled by existing OKLCH palette, adjust if needed |
| Mobile-specific dashboard layout | Current responsive grid sufficient for MVP |
| Real-time updates (WebSocket) | Infrastructure scope, not UX refresh |
