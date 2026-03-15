# IPR Detail Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign IPR detail page from vertical stack (~460px chrome) to compact sticky header (~48px) + sidebar navigation + tab Resumen. Net result: −110 lines, 400px less chrome.

**Architecture:** Sticky header replaces HeroCard. Sidebar replaces horizontal TabsList. New tab "Resumen" absorbs PhaseStepper, TransitionPanel, TrackCard, HistorySection. Conditional rendering replaces Radix Tabs wrapper.

**Tech Stack:** Next.js 16, TypeScript, TailwindCSS v4, shadcn/ui, lucide-react

**Spec:** `docs/superpowers/specs/2026-03-15-ipr-detail-redesign-design.md`

---

## Task 1: Create IprStickyHeader

**Files:**
- Create: `web/src/app/(app)/ipr/components/ipr-sticky-header.tsx`

- [ ] **Step 1: Create component**

```tsx
"use client";

import { useRouter } from "next/navigation";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ArrowLeft, MoreVertical, Pencil, UserPlus } from "lucide-react";
import { cn } from "@/lib/utils";
import { mechanismColors, mcdPhaseColors } from "./ipr-constants";
import type { IprDetail } from "./ipr-constants";

interface IprStickyHeaderProps {
  ipr: IprDetail;
  canEdit: boolean;
  canAssign: boolean;
  onEdit: () => void;
  onAssign: () => void;
}

const TERMINAL_STATES = ["CERRADO", "ANULADO", "TERMINADO_ANTICIPADAMENTE", "INADMISIBLE"];

export function IprStickyHeader({ ipr, canEdit, canAssign, onEdit, onAssign }: IprStickyHeaderProps) {
  const router = useRouter();
  const isTerminal = TERMINAL_STATES.includes(ipr.status ?? "");
  const hasActions = !isTerminal && (canEdit || canAssign);

  return (
    <header className="sticky top-0 z-30 bg-background/95 backdrop-blur border-b px-4 py-2">
      <div className="flex items-center gap-3 min-w-0">
        <Button variant="ghost" size="icon" className="size-8 shrink-0" onClick={() => router.back()}>
          <ArrowLeft className="size-4" />
        </Button>

        <span className="font-mono text-xs text-muted-foreground shrink-0">{ipr.codigo_bip}</span>
        <span className="text-xs text-muted-foreground shrink-0">·</span>
        <span className="text-sm font-medium truncate min-w-0">{ipr.name}</span>

        <div className="flex items-center gap-1.5 shrink-0 ml-auto">
          {ipr.mechanism && (
            <Badge variant="outline" className={cn("text-[10px] px-1.5 py-0", mechanismColors[ipr.mechanism])}>
              {ipr.mechanism}
            </Badge>
          )}
          {ipr.status && <StatusBadge status={ipr.status} size="sm" />}
          {ipr.mcd_phase && (
            <Badge variant="outline" className={cn("text-[10px] px-1.5 py-0", mcdPhaseColors[ipr.mcd_phase])}>
              {ipr.mcd_phase}
            </Badge>
          )}
          {hasActions && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="size-7">
                  <MoreVertical className="size-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {canEdit && (
                  <DropdownMenuItem onClick={onEdit}>
                    <Pencil className="size-3.5 mr-2" /> Editar
                  </DropdownMenuItem>
                )}
                {canAssign && (
                  <DropdownMenuItem onClick={onAssign}>
                    <UserPlus className="size-3.5 mr-2" /> Asignar Responsable
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>

      {/* Second line: executor + responsible */}
      <div className="flex items-center gap-4 ml-11 text-xs text-muted-foreground">
        {ipr.executor_name && <span>Ejecutor: <span className="text-foreground">{ipr.executor_name}</span></span>}
        {ipr.formulator_name && <span>Responsable: <span className="text-foreground">{ipr.formulator_name}</span></span>}
      </div>
    </header>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add web/src/app/(app)/ipr/components/ipr-sticky-header.tsx
git commit -m "feat(ui): create IprStickyHeader — compact identity bar replacing HeroCard"
```

---

## Task 2: Create IprSidebarNav

**Files:**
- Create: `web/src/app/(app)/ipr/components/ipr-sidebar-nav.tsx`
- Modify: `web/src/app/(app)/ipr/components/ipr-constants.ts` (add "resumen")

- [ ] **Step 1: Update constants — add resumen to groups and labels**

In `ipr-constants.ts`, prepend resumen:

```typescript
export const ALL_TABS = [
  { key: "resumen", label: "Resumen", group: null },
  ...TAB_GROUPS.flatMap(g => g.tabs.map(t => ({ key: t, label: TAB_LABELS[t] ?? t, group: g.label }))),
];
```

Add to TAB_LABELS:
```typescript
resumen: "Resumen",
```

- [ ] **Step 2: Create sidebar component**

```tsx
"use client";

import { cn } from "@/lib/utils";
import { TAB_GROUPS, TAB_LABELS } from "./ipr-constants";

interface IprSidebarNavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function IprSidebarNav({ activeTab, onTabChange }: IprSidebarNavProps) {
  return (
    <nav className="py-3 px-2 space-y-1">
      {/* Resumen — always first */}
      <button
        onClick={() => onTabChange("resumen")}
        className={cn(
          "w-full text-left text-sm px-3 py-1.5 rounded-md transition-colors",
          activeTab === "resumen"
            ? "bg-accent font-medium text-foreground"
            : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
        )}
      >
        Resumen
      </button>

      {TAB_GROUPS.map((group) => (
        <div key={group.label} className="pt-2">
          <p className="px-3 text-[10px] font-medium text-muted-foreground/60 uppercase tracking-wider mb-1">
            {group.label}
          </p>
          {group.tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => onTabChange(tab)}
              className={cn(
                "w-full text-left text-sm px-3 py-1.5 rounded-md transition-colors",
                activeTab === tab
                  ? "bg-accent font-medium text-foreground"
                  : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
              )}
            >
              {TAB_LABELS[tab] ?? tab}
            </button>
          ))}
        </div>
      ))}
    </nav>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add web/src/app/(app)/ipr/components/ipr-sidebar-nav.tsx web/src/app/(app)/ipr/components/ipr-constants.ts
git commit -m "feat(ui): create IprSidebarNav — vertical tab navigation with groups"
```

---

## Task 3: Create TabResumen

**Files:**
- Create: `web/src/app/(app)/ipr/components/tab-resumen.tsx`

- [ ] **Step 1: Create component**

Composes existing components (PhaseStepper, TransitionPanel, TrackCard, HistorySection) into a single view with extended metadata.

```tsx
"use client";

import { IprPhaseStepper } from "./ipr-phase-stepper";
import { IprTransitionPanel } from "./ipr-transition-panel";
import { IprHistorySection } from "./ipr-history-section";
import { TrackCard } from "./track-card";
import { formatDate, formatCurrency } from "@/lib/format";
import type { IprDetail } from "./ipr-constants";
import type { IprTransition, TrackInfo, HistoryEntry } from "@/types";

interface TabResumenProps {
  ipr: IprDetail;
  transitions: IprTransition[] | null;
  transLoading: boolean;
  trackInfo: TrackInfo | null;
  history: HistoryEntry[];
  canTransition: boolean;
  selectedTransition: string;
  onSelectTransition: (v: string) => void;
  onTransition: () => void;
  transSubmitting: boolean;
  transError: string | null;
  currentPhase?: string;
}

export function TabResumen({
  ipr, transitions, transLoading, trackInfo, history,
  canTransition, selectedTransition, onSelectTransition,
  onTransition, transSubmitting, transError, currentPhase,
}: TabResumenProps) {
  return (
    <div className="space-y-4">
      {/* Phase stepper */}
      {ipr.mcd_phase && (
        <IprPhaseStepper
          currentPhase={ipr.mcd_phase}
          currentPhaseLabel={ipr.mcd_phase_label}
          phaseEnteredAt={ipr.phase_entered_at}
        />
      )}

      {/* Transition panel */}
      {canTransition && (
        <IprTransitionPanel
          transitions={transitions ?? []}
          loading={transLoading}
          selectedTransition={selectedTransition}
          onSelectTransition={onSelectTransition}
          submitting={transSubmitting}
          onTransition={onTransition}
          error={transError}
          currentPhase={currentPhase}
        />
      )}

      {/* Track card */}
      {trackInfo && trackInfo.mechanism && (
        <TrackCard track={trackInfo} />
      )}

      {/* History */}
      {history.length > 0 && <IprHistorySection history={history} />}

      {/* Extended metadata */}
      <div className="rounded-xl border bg-card p-4">
        <h3 className="text-sm font-medium mb-3">Información General</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
          {ipr.description && (
            <div className="col-span-full">
              <span className="text-muted-foreground text-xs">Descripción</span>
              <p className="mt-0.5">{ipr.description}</p>
            </div>
          )}
          {ipr.total_budget != null && ipr.total_budget > 0 && (
            <div>
              <span className="text-muted-foreground text-xs">Presupuesto total</span>
              <p className="font-medium tabular-nums">{formatCurrency(ipr.total_budget)}</p>
            </div>
          )}
          {ipr.investment_sector && (
            <div>
              <span className="text-muted-foreground text-xs">Sector</span>
              <p>{ipr.investment_sector}</p>
            </div>
          )}
          {ipr.funding_source && (
            <div>
              <span className="text-muted-foreground text-xs">Fuente</span>
              <p>{ipr.fund_category_label || ipr.funding_source}</p>
            </div>
          )}
          {ipr.start_date && (
            <div>
              <span className="text-muted-foreground text-xs">Inicio</span>
              <p>{formatDate(ipr.start_date)}</p>
            </div>
          )}
          {ipr.end_date && (
            <div>
              <span className="text-muted-foreground text-xs">Término</span>
              <p>{formatDate(ipr.end_date)}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add web/src/app/(app)/ipr/components/tab-resumen.tsx
git commit -m "feat(ui): create TabResumen — absorbs stepper, transitions, track, history, metadata"
```

---

## Task 4: Rewrite page layout + delete HeroCard

**Files:**
- Rewrite: `web/src/app/(app)/ipr/[id]/page.tsx`
- Delete: `web/src/app/(app)/ipr/components/ipr-hero-card.tsx`

- [ ] **Step 1: Rewrite page.tsx**

Replace the vertical stack layout with the new 2-panel layout:

Key changes:
- Remove Breadcrumb (sticky header has back button)
- Remove IprHeroCard import → use IprStickyHeader
- Remove TabsList/TabsTrigger/TabsContent → use conditional rendering
- Add IprSidebarNav
- Add TabResumen
- Layout: `flex flex-col h-[calc(100vh-...)]` with `flex flex-1 overflow-hidden`
- Use `useTabParam("tab", "resumen")` — default to resumen
- Mobile: `<Select>` dropdown instead of sidebar

The page.tsx should drop from ~440 lines to ~300 lines because the tab rendering becomes simple conditional blocks and the header/sidebar are extracted.

- [ ] **Step 2: Delete ipr-hero-card.tsx**

```bash
git rm web/src/app/(app)/ipr/components/ipr-hero-card.tsx
```

- [ ] **Step 3: Build + test**

```bash
cd web && npx next build
docker compose exec api pytest tests/test_dashboard.py tests/test_formulacion.py tests/test_ipr_readiness.py -v --tb=short
```

Expected: Build clean, all tests pass.

- [ ] **Step 4: Commit**

```bash
git add web/src/app/(app)/ipr/[id]/page.tsx
git rm web/src/app/(app)/ipr/components/ipr-hero-card.tsx
git commit -m "feat(ux): IPR detail redesign — sticky header + sidebar nav + tab resumen

Replaces vertical stack layout (~460px chrome) with:
- IprStickyHeader: compact ~48px identity bar
- IprSidebarNav: vertical navigation, 18 items in 5 groups
- TabResumen: absorbs PhaseStepper, TransitionPanel, TrackCard, History

HeroCard eliminated. Radix Tabs replaced with conditional rendering.
Deep links (?tab=X) preserved. Default tab: resumen.
Mobile: sidebar becomes Select dropdown."
```

---

## Summary

| Task | Component | Action | Lines |
|------|-----------|--------|-------|
| 1 | IprStickyHeader | CREATE | ~80 |
| 2 | IprSidebarNav + constants | CREATE | ~60 |
| 3 | TabResumen | CREATE | ~100 |
| 4 | page.tsx rewrite + HeroCard delete | REWRITE + DELETE | ~300 new, ~440+120 deleted |

**Total: ~540 new, ~560 deleted = −20 lines net. 4 commits.**

**Test as:**
- Any user → `/ipr/{id}` → should see sticky header + sidebar + Resumen tab
- Deep link → `/ipr/{id}?tab=compromisos` → should open Compromisos directly
- Mobile → sidebar hidden, Select dropdown visible
- Terminal state (CERRADO) → no action buttons in header menu
