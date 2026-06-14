# UX Journey Inbox — Enfoque B Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close 6 UX gaps (G1, G8, G3, A1, G4, G6) for Ejecutor + Supervisor archetypes, covering 95% of daily system usage.

**Architecture:** Pure frontend changes — all data already exists in backend endpoints. No new API endpoints needed. 6 component modifications across dashboard and list pages.

**Tech Stack:** Next.js 16, TypeScript, TailwindCSS v4, shadcn/ui, lucide-react. Design system in CLAUDE.md rules 34-37.

**Branch:** `feat/ux-journey-inbox`

**Mockup:** `docs/mockups/ux-journey-inbox.html` (approved)

**Journeys reference:** `docs/GORE_OS_User_Journeys_v1.0.md`

---

## Chunk 1: Dashboard Inbox (G1 + G8)

### Task 1: G8 — Done State in AttentionStrip

**Files:**
- Modify: `web/src/app/(app)/dashboard/components/attention-strip.tsx`

Currently returns `null` when `items.length === 0`. Users don't know if they're caught up or if the system failed.

- [ ] **Step 1: Add done state rendering**

In `attention-strip.tsx`, replace the early return `if (items.length === 0) return null;` with a positive "Al día" card:

```tsx
if (items.length === 0) {
  return (
    <div className="flex items-center gap-3 p-4 rounded-lg bg-green-50 border border-green-200 dark:bg-green-950/30 dark:border-green-800 animate-in fade-in duration-200">
      <div className="size-10 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center shrink-0">
        <CheckCircle2 className="size-5 text-green-600" />
      </div>
      <div>
        <p className="text-sm font-medium text-green-800 dark:text-green-200">Al día</p>
        <p className="text-xs text-green-600 dark:text-green-400">No tienes tareas pendientes.</p>
      </div>
    </div>
  );
}
```

Add `CheckCircle2` to the lucide-react imports.

- [ ] **Step 2: Verify in browser**

Login as `encargado.daf@goreos.cl`. If no action items exist, the green "Al día" card should render instead of blank space.

- [ ] **Step 3: Commit**

```bash
git add web/src/app/(app)/dashboard/components/attention-strip.tsx
git commit -m "feat(ux): G8 done state — show 'Al día' when inbox empty"
```

---

### Task 2: G1 — ModuleMyProgress Inbox with Deadlines

**Files:**
- Modify: `web/src/app/(app)/dashboard/components/module-my-progress.tsx`

Currently shows only a progress bar + KPI counts. The API `GET /api/dashboard/mis-compromisos` already returns `groups[].items[]` with full commitment data including `days_remaining`. We just need to render the items.

- [ ] **Step 1: Rewrite ModuleMyProgress**

Replace the entire component with an inbox-style list. Key design decisions:
- Show items from `groups` ordered by urgency (Vencidos first, Esta Semana, then Pendientes)
- Each item shows: title (truncated), days_remaining with temporal color, click to navigate
- Max 6 items visible, "+N más" footer
- Keep the progress bar at top for at-a-glance status
- Use `useRouter` for navigation to `action_route` or `/compromisos`

```tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { MisCompromisosResponse } from "@/types";

export function ModuleMyProgress() {
  const router = useRouter();
  const [data, setData] = useState<MisCompromisosResponse | null>(null);

  useEffect(() => {
    api.get<MisCompromisosResponse>("/api/dashboard/mis-compromisos")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <div className="h-4 w-24 bg-muted animate-pulse rounded mb-3" />
        <div className="h-2 w-full bg-muted animate-pulse rounded-full mb-3" />
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-8 bg-muted animate-pulse rounded" />
          ))}
        </div>
      </div>
    );
  }

  const total = data.kpis.reduce((sum, k) => sum + k.value, 0);
  const completados = data.kpis.find(k => k.label.toLowerCase().includes("completad"))?.value ?? 0;
  const pct = total > 0 ? Math.round((completados / total) * 100) : 0;

  // Flatten groups into a single sorted list (vencidos first, then esta_semana, then pendientes)
  const allItems = data.groups.flatMap(g => g.items);
  const maxVisible = 6;
  const visible = allItems.slice(0, maxVisible);
  const remaining = allItems.length - maxVisible;

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold">Mi Trabajo</h3>
        <span className="text-xs text-muted-foreground tabular-nums">{completados}/{total}</span>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 rounded-full bg-muted mb-3">
        <div
          className="h-full rounded-full bg-green-500 transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Item list */}
      {visible.length > 0 ? (
        <div className="space-y-1">
          {visible.map((item) => {
            const dr = item.days_remaining ?? 999;
            const isOverdue = dr < 0;
            const isToday = dr === 0;
            const isUrgent = dr > 0 && dr <= 7;

            return (
              <div
                key={item.id}
                onClick={() => {
                  if (item.ipr_id) router.push(`/ipr/${item.ipr_id}?tab=compromisos`);
                  else router.push("/compromisos");
                }}
                className={cn(
                  "flex items-center gap-2 px-2 py-1.5 rounded-md text-xs cursor-pointer transition-colors",
                  isOverdue && "bg-red-50 hover:bg-red-100 dark:bg-red-950/30 dark:hover:bg-red-950/50",
                  isToday && "bg-amber-50 hover:bg-amber-100 dark:bg-amber-950/30",
                  isUrgent && "hover:bg-amber-50 dark:hover:bg-amber-950/20",
                  !isOverdue && !isToday && !isUrgent && "hover:bg-muted/50"
                )}
              >
                <span className={cn(
                  "size-1.5 rounded-full shrink-0",
                  isOverdue ? "bg-red-500" : isToday ? "bg-amber-500" : isUrgent ? "bg-blue-400" : "bg-gray-300"
                )} />
                <span className={cn(
                  "flex-1 truncate",
                  isOverdue ? "font-medium text-foreground" : "text-muted-foreground"
                )}>
                  {item.description}
                </span>
                <span className={cn(
                  "tabular-nums shrink-0 font-medium",
                  isOverdue ? "text-red-600" : isToday ? "text-amber-600" : isUrgent ? "text-blue-600" : "text-muted-foreground"
                )}>
                  {isOverdue ? `${dr}d` : isToday ? "hoy" : `${dr}d`}
                </span>
              </div>
            );
          })}
          {remaining > 0 && (
            <button
              onClick={() => router.push("/compromisos?solo_mios=true")}
              className="w-full text-xs text-muted-foreground hover:text-foreground py-1 text-center"
            >
              +{remaining} más
            </button>
          )}
        </div>
      ) : (
        <p className="text-xs text-muted-foreground py-2">Sin compromisos pendientes.</p>
      )}
    </div>
  );
}
```

Note: The `DashboardCommitment` type (used in `groups[].items[]`) has `id`, `description`, `ipr_codigo_bip`, `ipr_id`, `responsible_name`, `due_date`, `state`, `days_remaining`. We navigate to the IPR's compromisos tab if `ipr_id` exists.

- [ ] **Step 2: Verify `DashboardCommitment` type has `ipr_id`**

Check `web/src/types/index.ts` for the `DashboardCommitment` or `CompromisoListItem` interface. If `ipr_id` is missing, add it. The backend `_ai_commitments()` in `dashboard.py` already includes `oc.ipr_id::text AS ipr_id` in its SELECT.

- [ ] **Step 3: Test in browser**

Login as `encargado.daf@goreos.cl`. The "Mi Trabajo" module should show:
- Progress bar with completion percentage
- List of items with colored dots and days-remaining
- Red background for overdue items
- Click navigates to `/ipr/{id}?tab=compromisos`

- [ ] **Step 4: Commit**

```bash
git add web/src/app/(app)/dashboard/components/module-my-progress.tsx
git commit -m "feat(ux): G1 inbox — ModuleMyProgress shows items with deadlines"
```

---

## Chunk 2: List Page Enhancements (A1 + G3)

### Task 3: A1 — Enhanced DeadlineCell with relative time

**Files:**
- Modify: `web/src/components/deadline-cell.tsx`

Currently shows badge with "Xd vencido" / "Hoy" / "Xd". Change to more natural language: "hace X días" / "hoy" / "en X días".

- [ ] **Step 1: Update DeadlineCell text format**

Change the badge/label text rendering:
- Overdue: `"hace {abs(days)}d"` instead of `"{days}d vencido"`
- Today: `"hoy"` (keep as-is)
- ≤7 days: `"en {days}d"` instead of `"{days}d"`
- >7 days: show date only (no badge)

Also add the original date as a secondary line below the relative text for context.

- [ ] **Step 2: Verify in compromisos list**

Navigate to `/compromisos`. The "Vence" column should show "hace 3d" (red) or "en 5d" (gray) with the actual date below.

- [ ] **Step 3: Commit**

```bash
git add web/src/components/deadline-cell.tsx
git commit -m "feat(ux): A1 deadline cell — relative time format 'hace Xd' / 'en Xd'"
```

---

### Task 4: G3 — Rendiciones SLA row highlighting

**Files:**
- Modify: `web/src/app/(app)/datos/domains/rendiciones.tsx`

The SLA column already exists with progress bar. Enhancement: highlight urgent rows (>80% SLA consumed) with background color, and sort by SLA urgency by default when RTF is viewing.

- [ ] **Step 1: Add row className logic**

In the rendiciones domain config, add `rowClassName` function (if supported by DataTable) or enhance the SLA column render to make the urgency more visually prominent:

- If SLA ratio ≥ 0.85: add `className="bg-red-50"` to the row
- If SLA ratio ≥ 0.7: add `className="bg-amber-50/50"`

Check if DataTable supports `rowClassName` prop. If not, enhance the SLA cell render to use a wider visual indicator (e.g., full-width background in the cell).

- [ ] **Step 2: Verify as RTF user**

Login as `rtf.daf@goreos.cl`, navigate to `/datos` (auto-filtered to rendiciones EN_REVISION_RTF). Urgent renditions should have red/amber row highlighting.

- [ ] **Step 3: Commit**

```bash
git add web/src/app/(app)/datos/domains/rendiciones.tsx
git commit -m "feat(ux): G3 rendiciones — SLA urgency row highlighting"
```

---

## Chunk 3: Supervisor Enhancements (G4 + G6)

### Task 5: G4 — Enhanced MyTeam with avatars, load bar, drill-down

**Files:**
- Modify: `web/src/app/(app)/dashboard/components/module-my-team.tsx`

Current: plain text list with vencidos/activos counts. Enhancement: avatar initials, relative load bar, click to drill-down to that person's commitments, red highlighting for overloaded members.

- [ ] **Step 1: Rewrite ModuleMyTeam**

```tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { MiDivisionResponse } from "@/types";

export function ModuleMyTeam() {
  const router = useRouter();
  const [data, setData] = useState<MiDivisionResponse | null>(null);

  useEffect(() => {
    api.get<MiDivisionResponse>("/api/dashboard/mi-division")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <div className="h-4 w-20 bg-muted animate-pulse rounded mb-3" />
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-10 w-full bg-muted animate-pulse rounded mb-2" />
        ))}
      </div>
    );
  }

  const maxLoad = Math.max(...data.team.map(m => m.total), 1);

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Mi Equipo</h3>
        <button
          onClick={() => router.push("/compromisos")}
          className="text-xs text-indigo-600 hover:underline"
        >
          Ver todos
        </button>
      </div>
      <div className="space-y-1.5">
        {data.team.slice(0, 5).map((m) => {
          const hasOverdue = m.vencidos > 0;
          const activos = m.pendientes + m.en_progreso;
          const loadPct = Math.round((m.total / maxLoad) * 100);
          const initials = m.name.split(" ").map(w => w[0]).slice(0, 2).join("").toUpperCase();

          return (
            <div
              key={m.user_id}
              onClick={() => router.push(`/compromisos?responsible_id=${m.user_id}`)}
              className={cn(
                "flex items-center gap-2.5 p-2 rounded-md cursor-pointer transition-colors text-xs",
                hasOverdue
                  ? "bg-red-50 hover:bg-red-100 dark:bg-red-950/20 dark:hover:bg-red-950/40"
                  : "hover:bg-muted/50"
              )}
            >
              {/* Avatar */}
              <div className={cn(
                "size-7 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0",
                hasOverdue
                  ? "bg-red-200 text-red-700 dark:bg-red-900 dark:text-red-300"
                  : activos > 0
                    ? "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300"
                    : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
              )}>
                {initials}
              </div>

              {/* Name */}
              <span className="flex-1 truncate font-medium">{m.name}</span>

              {/* Stats */}
              <div className="flex items-center gap-2 shrink-0">
                {hasOverdue && (
                  <span className="px-1.5 py-0.5 rounded bg-red-600 text-white text-[10px] font-bold">
                    {m.vencidos}
                  </span>
                )}
                <span className="text-muted-foreground">{activos} activos</span>
              </div>

              {/* Load bar */}
              <div className="w-14 h-1.5 rounded-full bg-muted overflow-hidden shrink-0">
                <div
                  className={cn(
                    "h-full rounded-full transition-all",
                    hasOverdue ? "bg-red-500" : loadPct > 70 ? "bg-amber-400" : "bg-green-400"
                  )}
                  style={{ width: `${loadPct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
      {data.team.length > 5 && (
        <p className="text-xs text-muted-foreground mt-2 text-center">
          +{data.team.length - 5} más
        </p>
      )}
    </div>
  );
}
```

Note: The drill-down navigates to `/compromisos?responsible_id={user_id}`. If the compromisos page doesn't support this filter, we need to add it (check in Task 5 Step 2).

- [ ] **Step 2: Verify compromisos page supports `responsible_id` filter**

Check if `/compromisos/page.tsx` reads `responsible_id` from searchParams and passes it to the API. If not, add it:
- Read `responsible_id` from `useSearchParams()`
- Pass to `GET /api/compromisos?responsible_id={id}`
- The backend `compromisos.py` likely already supports this param

- [ ] **Step 3: Test as JEFE_DIVISION**

Login as `jefe.daf@goreos.cl`. The "Mi Equipo" module should show team members with avatars, load bars, and red highlighting for those with overdue items. Click a person to navigate to their commitments.

- [ ] **Step 4: Commit**

```bash
git add web/src/app/(app)/dashboard/components/module-my-team.tsx
git commit -m "feat(ux): G4 MyTeam — avatars, load bars, drill-down per person"
```

---

### Task 6: G6 — Division breakdown in Centro de Mando

**Files:**
- Modify: `web/src/app/(app)/dashboard/components/command-center.tsx`
- Modify: `web/src/app/(app)/dashboard/components/module-kpis.tsx`

The `DashboardExecutivoResponse` already includes `divisions: DivisionBreakdown[]` with `division_name, vencidos, total_compromisos, problemas_abiertos, ejecucion_pct`. We need to render this data below the KPIs for PANORAMA_ROLES.

- [ ] **Step 1: Pass divisions data to ModuleKpis**

In `command-center.tsx`:
- Add `divisions` state: `const [divisions, setDivisions] = useState<DivisionBreakdown[]>([])`
- In the ejecutivo fetch, capture divisions: `setDivisions(d.divisions ?? [])`
- Pass to ModuleKpis: `<ModuleKpis kpis={kpis} semaforo={semaforo} divisions={divisions} />`

- [ ] **Step 2: Render division breakdown in ModuleKpis**

In `module-kpis.tsx`, add a `divisions` optional prop. When present, render a compact list below the semáforo:

```tsx
{divisions && divisions.length > 0 && (
  <div className="border-t pt-2 mt-1">
    <div className="flex items-center justify-between mb-1.5">
      <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Por división</p>
      <button
        onClick={() => router.push("/ipr/cartera")}
        className="text-[10px] text-indigo-600 hover:underline"
      >
        Cartera Divisional
      </button>
    </div>
    <div className="space-y-1">
      {divisions.slice(0, 6).map((d) => {
        const hasIssues = d.vencidos > 0;
        return (
          <div
            key={d.division_name}
            onClick={() => router.push(`/ipr?division=${encodeURIComponent(d.division_name)}`)}
            className="flex items-center gap-2 text-xs cursor-pointer hover:bg-muted/50 rounded px-1 py-0.5"
          >
            <span className={cn(
              "size-1.5 rounded-full",
              hasIssues ? "bg-red-500" : d.problemas_abiertos > 3 ? "bg-amber-500" : "bg-green-500"
            )} />
            <span className="flex-1 truncate">{d.division_name}</span>
            {d.vencidos > 0 && (
              <span className="text-red-600 font-medium tabular-nums">{d.vencidos} vencidos</span>
            )}
            <span className="text-muted-foreground tabular-nums">{d.total_compromisos} comp.</span>
          </div>
        );
      })}
    </div>
  </div>
)}
```

Import `useRouter` and `cn` in module-kpis.tsx. Add `DivisionBreakdown` to the types import.

- [ ] **Step 3: Verify type exists**

Check `web/src/types/index.ts` for `DivisionBreakdown`. If missing, add:

```typescript
export interface DivisionBreakdown {
  division_name: string;
  vencidos: number;
  total_compromisos: number;
  problemas_abiertos: number;
  ejecucion_pct: number;
}
```

- [ ] **Step 4: Test as ADMIN_REGIONAL**

Login as `regional@goreos.cl`. Below the KPIs and semáforo, a "Por división" section should appear with each division's health indicators. Click a division to navigate to filtered IPR list.

- [ ] **Step 5: Commit**

```bash
git add web/src/app/(app)/dashboard/components/command-center.tsx \
       web/src/app/(app)/dashboard/components/module-kpis.tsx \
       web/src/types/index.ts
git commit -m "feat(ux): G6 division breakdown in Centro de Mando for executives"
```

---

## Chunk 4: Verification & Cleanup

### Task 7: Build verification + full test suite

- [ ] **Step 1: Frontend build**

```bash
cd web && npx next build
```

Expected: 0 errors, 56 pages.

- [ ] **Step 2: Backend tests**

```bash
docker compose exec api pytest -v --tb=short
```

Expected: 610 passed, 3 skipped.

- [ ] **Step 3: Verify no unused imports**

```bash
cd web && npx eslint src/ --quiet 2>&1 | head -20
```

Expected: no NEW errors from our changes.

- [ ] **Step 4: Final commit if any cleanup needed**

```bash
git add -A && git commit -m "chore: cleanup after UX journey inbox implementation"
```

---

## Summary

| Task | Gap | Component | Type | Estimated |
|------|-----|-----------|------|-----------|
| 1 | G8 | AttentionStrip | 10 lines added | 5 min |
| 2 | G1 | ModuleMyProgress | Full rewrite (~80 lines) | 15 min |
| 3 | A1 | DeadlineCell | Text format change | 10 min |
| 4 | G3 | Rendiciones | Row highlighting | 10 min |
| 5 | G4 | ModuleMyTeam | Full rewrite (~80 lines) | 15 min |
| 6 | G6 | ModuleKpis + CommandCenter | ~40 lines added | 15 min |
| 7 | — | Verification | Build + tests | 10 min |

**Total: ~6 files modified, ~300 lines changed, 7 commits.**
