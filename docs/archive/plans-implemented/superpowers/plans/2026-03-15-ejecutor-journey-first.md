# Ejecutor Journey-First Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the generic ModuleMyProgress with two journey-specific modules: ModuleMyWork (ENCARGADO task list grouped by IPR) and ModuleFormulacion (ANALISTA F0-F2 pipeline with satellite checklists).

**Architecture:** Dashboard CommandCenter routes ENCARGADO to ModuleMyWork and ANALISTA to ModuleFormulacion. ModuleMyWork groups existing action-items by ipr_id (client-side). ModuleFormulacion uses a new backend endpoint. RTF + ASESOR_JURIDICO keep the existing ModuleMyProgress behavior (flat list) to avoid regression.

**Tech Stack:** Next.js 16, TypeScript, TailwindCSS v4, FastAPI, SQLAlchemy async, PostgreSQL

**Spec:** `docs/superpowers/specs/2026-03-15-ejecutor-journey-first-design.md`

---

## Chunk 1: Backend — ipr_id in ActionItem + mis-formulaciones endpoint

### Task 1: Add ipr_id to ActionItem schema

**Files:**
- Modify: `api/app/schemas/dashboard.py`
- Modify: `api/app/routers/dashboard.py` (3 source functions)
- Modify: `web/src/types/index.ts`

- [ ] **Step 1: Add ipr_id to ActionItem Pydantic model**

In `api/app/schemas/dashboard.py`, add `ipr_id: str | None = None` to ActionItem:

```python
class ActionItem(BaseModel):
    id: str
    category: str
    title: str
    subtitle: str | None = None
    deadline: date | None = None
    days_remaining: int | None = None
    temporal: str | None = None
    severity: str
    priority: int
    action_label: str
    action_route: str
    ipr_id: str | None = None
    ipr_codigo_bip: str | None = None
```

- [ ] **Step 2: Pass ipr_id in _ai_commitments()**

In `dashboard.py` `_ai_commitments()`, the SQL already selects `oc.ipr_id::text AS ipr_id` and `ipr.codigo_bip AS ipr_codigo_bip` (lines 149-151). Add these to the ActionItem constructor (around line 183):

```python
items.append(ActionItem(
    id=r["id"],
    category="COMPROMISO",
    # ... existing fields ...
    action_route=f"/ipr/{r['ipr_id']}?tab=compromisos" if r.get("ipr_id") else "/compromisos",
    ipr_id=r.get("ipr_id"),
    ipr_codigo_bip=r.get("ipr_codigo_bip"),
))
```

- [ ] **Step 3: Pass ipr_id in _ai_alerts()**

In `_ai_alerts()`, the SQL selects `a.subject_id`. When `subject_type = 'core.ipr'`, pass it as ipr_id:

```python
ipr_id = str(r["subject_id"]) if r["subject_type"] == "core.ipr" else None
items.append(ActionItem(
    # ... existing fields ...
    ipr_id=ipr_id,
))
```

- [ ] **Step 4: Pass ipr_id in _ai_ipr_stale()**

Already has `i.id::text` — pass it:

```python
items.append(ActionItem(
    # ... existing fields ...
    ipr_id=r["id"],
    ipr_codigo_bip=r["codigo_bip"],
))
```

- [ ] **Step 5: Add ipr_id to frontend TypeScript type**

In `web/src/types/index.ts`, add to ActionItem interface:

```typescript
export interface ActionItem {
  // ... existing fields ...
  action_route: string;
  ipr_id?: string | null;
  ipr_codigo_bip?: string | null;
}
```

- [ ] **Step 6: Run tests + commit**

```bash
docker compose restart api
docker compose exec api pytest tests/test_dashboard.py -v --tb=short
```

Expected: 6 passed. Then:

```bash
git add api/app/schemas/dashboard.py api/app/routers/dashboard.py web/src/types/index.ts
git commit -m "feat(api): add ipr_id to ActionItem for client-side grouping"
```

---

### Task 2: Create mis-formulaciones endpoint

**Files:**
- Modify: `api/app/routers/ipr.py`
- Modify: `api/app/schemas/ipr.py`
- Create: `api/tests/test_formulacion.py`

- [ ] **Step 1: Add Pydantic schemas**

In `api/app/schemas/ipr.py`, add:

```python
class FormulacionIPR(BaseModel):
    id: str
    codigo_bip: str
    name: str
    phase: str
    days_in_phase: int
    has_mechanism: bool
    partes_count: int
    territorio_count: int
    hitos_count: int
    evaluaciones_count: int
    admisibilidad_total: int
    admisibilidad_verified: int
    eval_assigned: bool
    eval_result: str | None = None
    suggested_action: str
    suggested_tab: str

class MisFormulacionesResponse(BaseModel):
    total: int
    by_phase: dict[str, list[FormulacionIPR]]
```

- [ ] **Step 2: Add endpoint to ipr.py**

Place BEFORE `/{ipr_id}` routes (route ordering rule). Add after the `cartera-por-division` endpoint:

```python
@router.get("/mis-formulaciones")
async def get_mis_formulaciones(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """IPRs assigned to current user in F0-F2 with satellite completeness."""
    from app.schemas.ipr import FormulacionIPR, MisFormulacionesResponse

    user_id = str(user["id"])

    sql = text("""
        WITH ipr_base AS (
            SELECT i.id, i.codigo_bip, i.name,
                   mcd.code AS phase,
                   COALESCE(EXTRACT(DAY FROM NOW() - i.phase_entered_at)::int, 0) AS days_in_phase,
                   i.mechanism_id IS NOT NULL AS has_mechanism,
                   (SELECT COUNT(*) FROM core.ipr_party WHERE ipr_id = i.id AND deleted_at IS NULL) AS partes_count,
                   (SELECT COUNT(*) FROM core.ipr_territory WHERE ipr_id = i.id AND deleted_at IS NULL) AS territorio_count,
                   (SELECT COUNT(*) FROM core.ipr_milestone WHERE ipr_id = i.id AND deleted_at IS NULL) AS hitos_count,
                   (SELECT COUNT(*) FROM core.evaluation_assignment WHERE ipr_id = i.id AND deleted_at IS NULL) AS evaluaciones_count,
                   (SELECT COUNT(*) FROM core.evaluation_assignment WHERE ipr_id = i.id AND deleted_at IS NULL AND result_id IS NOT NULL) AS eval_with_result,
                   (SELECT COUNT(*) FROM core.admissibility_check WHERE ipr_id = i.id) AS admisibilidad_total,
                   (SELECT COUNT(*) FROM core.admissibility_check WHERE ipr_id = i.id AND verified_at IS NOT NULL) AS admisibilidad_verified
            FROM core.ipr i
            JOIN ref.category sc ON sc.id = i.status_id
            LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
            WHERE i.assignee_id = :uid
              AND i.deleted_at IS NULL
              AND mcd.code IN ('F0', 'F1', 'F2')
              AND sc.code NOT IN ('ANULADO', 'TERMINADO_ANTICIPADAMENTE', 'INADMISIBLE')
            ORDER BY mcd.code, i.phase_entered_at ASC
        )
        SELECT * FROM ipr_base
    """)
    rows = (await db.execute(sql, {"uid": user_id})).mappings().all()

    by_phase: dict[str, list[FormulacionIPR]] = {"F0": [], "F1": [], "F2": []}
    for r in rows:
        phase = r["phase"] or "F0"
        # Compute suggested action + tab
        if phase == "F0":
            missing = []
            if not r["has_mechanism"]:
                missing.append("mecanismo")
            if r["partes_count"] == 0:
                missing.append("partes")
            if r["territorio_count"] == 0:
                missing.append("territorio")
            if r["hitos_count"] == 0:
                missing.append("hitos")
            if missing:
                action = f"Completar {', '.join(missing)} para avanzar a F1"
                tab = missing[0]  # first missing satellite
            else:
                action = "Lista para avanzar a F1"
                tab = "compromisos"
        elif phase == "F1":
            total = r["admisibilidad_total"]
            verified = r["admisibilidad_verified"]
            if total > 0 and verified < total:
                action = f"Verificar {total - verified} items de admisibilidad pendientes"
                tab = "admisibilidad"
            elif total == 0:
                action = "Sin items de admisibilidad configurados"
                tab = "admisibilidad"
            else:
                action = "Admisibilidad completa — lista para avanzar a F2"
                tab = "compromisos"
        else:  # F2
            if r["evaluaciones_count"] == 0:
                action = "Asignar evaluador según mecanismo"
                tab = "evaluaciones"
            elif r["eval_with_result"] == 0:
                action = "Esperando resultado de evaluación externa"
                tab = "evaluaciones"
            else:
                action = "Evaluación registrada — lista para avanzar a F3"
                tab = "evaluaciones"

        by_phase[phase].append(FormulacionIPR(
            id=str(r["id"]),
            codigo_bip=r["codigo_bip"] or "",
            name=r["name"] or "",
            phase=phase,
            days_in_phase=r["days_in_phase"],
            has_mechanism=r["has_mechanism"],
            partes_count=r["partes_count"],
            territorio_count=r["territorio_count"],
            hitos_count=r["hitos_count"],
            evaluaciones_count=r["evaluaciones_count"],
            admisibilidad_total=r["admisibilidad_total"],
            admisibilidad_verified=r["admisibilidad_verified"],
            eval_assigned=r["evaluaciones_count"] > 0,
            eval_result=None,  # simplified — detail is in eval tab
            suggested_action=action,
            suggested_tab=tab,
        ))

    total = sum(len(v) for v in by_phase.values())
    return MisFormulacionesResponse(total=total, by_phase=by_phase)
```

- [ ] **Step 3: Write test**

Create `api/tests/test_formulacion.py`:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_mis_formulaciones_endpoint(async_client: AsyncClient, analista_token: str):
    """Test that ANALISTA can fetch their IPRs in formulation phases."""
    resp = await async_client.get(
        "/api/ipr/mis-formulaciones",
        headers={"Authorization": f"Bearer {analista_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "by_phase" in data
    assert "F0" in data["by_phase"]
    assert "F1" in data["by_phase"]
    assert "F2" in data["by_phase"]

@pytest.mark.asyncio
async def test_mis_formulaciones_has_suggested_action(async_client: AsyncClient, analista_token: str):
    """Each IPR in response must have suggested_action and suggested_tab."""
    resp = await async_client.get(
        "/api/ipr/mis-formulaciones",
        headers={"Authorization": f"Bearer {analista_token}"},
    )
    data = resp.json()
    for phase_items in data["by_phase"].values():
        for item in phase_items:
            assert "suggested_action" in item
            assert "suggested_tab" in item
            assert item["suggested_action"]  # non-empty
```

Note: Uses `analista_token` from conftest.py (already exists for ANALISTA role).

- [ ] **Step 4: Run tests + commit**

```bash
docker compose restart api
docker compose exec api pytest tests/test_formulacion.py -v --tb=short
```

Expected: 2 passed. Then:

```bash
git add api/app/routers/ipr.py api/app/schemas/ipr.py api/tests/test_formulacion.py
git commit -m "feat(api): add GET /ipr/mis-formulaciones endpoint for ANALISTA pipeline"
```

---

## Chunk 2: Frontend — ModuleMyWork + ModuleFormulacion

### Task 3: Create ModuleMyWork (ENCARGADO)

**Files:**
- Create: `web/src/app/(app)/dashboard/components/module-my-work.tsx`

- [ ] **Step 1: Create component**

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronDown, ChevronRight, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ActionItem } from "@/types";

interface IprGroup {
  ipr_id: string | null;
  ipr_codigo_bip: string | null;
  items: ActionItem[];
  hasUrgent: boolean;
}

interface ModuleMyWorkProps {
  items: ActionItem[];
}

export function ModuleMyWork({ items }: ModuleMyWorkProps) {
  const router = useRouter();

  // Group by ipr_id
  const groupMap = new Map<string, IprGroup>();
  for (const item of items) {
    const key = item.ipr_id ?? "__general__";
    if (!groupMap.has(key)) {
      groupMap.set(key, {
        ipr_id: item.ipr_id ?? null,
        ipr_codigo_bip: item.ipr_codigo_bip ?? null,
        items: [],
        hasUrgent: false,
      });
    }
    const g = groupMap.get(key)!;
    g.items.push(item);
    if (item.temporal === "VENCIDO" || item.temporal === "HOY") {
      g.hasUrgent = true;
    }
  }
  const groups = Array.from(groupMap.values()).sort((a, b) => {
    // Urgent groups first
    if (a.hasUrgent && !b.hasUrgent) return -1;
    if (!a.hasUrgent && b.hasUrgent) return 1;
    return 0;
  });

  // Collapse state: auto-expand urgent, collapse rest
  const [collapsed, setCollapsed] = useState<Set<string>>(() => {
    const set = new Set<string>();
    for (const g of groups) {
      if (!g.hasUrgent) set.add(g.ipr_id ?? "__general__");
    }
    return set;
  });

  const toggle = (key: string) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  if (items.length === 0) return null; // AttentionStrip shows "Al día"

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Mi Trabajo</h3>
        <span className="text-xs text-muted-foreground tabular-nums">{items.length} pendientes</span>
      </div>

      <div className="space-y-2">
        {groups.map((group) => {
          const key = group.ipr_id ?? "__general__";
          const isCollapsed = collapsed.has(key);
          return (
            <div key={key}>
              <button
                onClick={() => toggle(key)}
                className="w-full flex items-center gap-2 text-xs py-1 hover:bg-muted/50 rounded px-1 -mx-1"
              >
                {isCollapsed ? (
                  <ChevronRight className="size-3.5 text-muted-foreground shrink-0" />
                ) : (
                  <ChevronDown className="size-3.5 text-muted-foreground shrink-0" />
                )}
                <span className="font-mono text-muted-foreground">
                  {group.ipr_codigo_bip ?? "General"}
                </span>
                {group.hasUrgent && (
                  <span className="size-1.5 rounded-full bg-red-500 shrink-0" />
                )}
                <span className="text-muted-foreground ml-auto tabular-nums">
                  {group.items.length}
                </span>
              </button>

              {!isCollapsed && (
                <div className="ml-5 space-y-0.5 mt-0.5">
                  {group.items.map((item) => {
                    const dr = item.days_remaining;
                    const isOverdue = dr != null && dr < 0;
                    const isToday = dr === 0;
                    const isUrgent = dr != null && dr > 0 && dr <= 7;

                    return (
                      <div
                        key={`${item.category}-${item.id}`}
                        onClick={() => router.push(item.action_route)}
                        className={cn(
                          "flex items-center gap-2 px-2 py-1.5 rounded text-xs cursor-pointer transition-colors",
                          isOverdue && "bg-red-50 hover:bg-red-100 dark:bg-red-950/30",
                          isToday && "bg-amber-50 hover:bg-amber-100 dark:bg-amber-950/30",
                          !isOverdue && !isToday && "hover:bg-muted/50"
                        )}
                      >
                        <span className={cn(
                          "size-1.5 rounded-full shrink-0",
                          isOverdue ? "bg-red-500" : isToday ? "bg-amber-500" : isUrgent ? "bg-blue-400" : "bg-gray-300"
                        )} />
                        <span className={cn(
                          "flex-1 truncate",
                          isOverdue ? "font-medium" : "text-muted-foreground"
                        )}>
                          {item.title}
                        </span>
                        {dr != null && (
                          <span className={cn(
                            "tabular-nums shrink-0 text-[11px]",
                            isOverdue ? "text-red-600 font-medium" : isToday ? "text-amber-600" : "text-muted-foreground"
                          )}>
                            {isOverdue ? `${dr}d` : isToday ? "hoy" : `${dr}d`}
                          </span>
                        )}
                        <ArrowRight className="size-3 text-muted-foreground/50 shrink-0" />
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

Key design decisions:
- Receives `items` as props (fetched by CommandCenter, not self-fetching — avoids duplicate API call since action-items is already fetched for AttentionStrip)
- Groups client-side by `ipr_id`
- Auto-expands groups with urgent items, collapses others
- Returns null when empty (AttentionStrip "Al día" card handles empty state)

- [ ] **Step 2: Build check**

```bash
cd web && npx next build 2>&1 | grep -E "(error|Error|✓)" | head -5
```

Expected: Compiled successfully (component not yet imported).

- [ ] **Step 3: Commit**

```bash
git add web/src/app/(app)/dashboard/components/module-my-work.tsx
git commit -m "feat(ui): create ModuleMyWork — task list grouped by IPR for ENCARGADO"
```

---

### Task 4: Create ModuleFormulacion (ANALISTA)

**Files:**
- Create: `web/src/app/(app)/dashboard/components/module-formulacion.tsx`
- Modify: `web/src/types/index.ts`

- [ ] **Step 1: Add TypeScript types**

In `web/src/types/index.ts`, add before the `// Historial` section:

```typescript
// ---------------------------------------------------------------------------
// ANALISTA Formulation Pipeline
// ---------------------------------------------------------------------------
export interface FormulacionIPR {
  id: string;
  codigo_bip: string;
  name: string;
  phase: string;
  days_in_phase: number;
  has_mechanism: boolean;
  partes_count: number;
  territorio_count: number;
  hitos_count: number;
  evaluaciones_count: number;
  admisibilidad_total: number;
  admisibilidad_verified: number;
  eval_assigned: boolean;
  eval_result: string | null;
  suggested_action: string;
  suggested_tab: string;
}

export interface MisFormulacionesResponse {
  total: number;
  by_phase: Record<string, FormulacionIPR[]>;
}
```

- [ ] **Step 2: Create component**

```tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { MisFormulacionesResponse, FormulacionIPR } from "@/types";

const PHASE_LABELS: Record<string, string> = {
  F0: "Formulación",
  F1: "Admisibilidad",
  F2: "Evaluación",
};

const PHASE_COLORS: Record<string, string> = {
  F0: "bg-slate-100 text-slate-700",
  F1: "bg-blue-100 text-blue-700",
  F2: "bg-cyan-100 text-cyan-700",
};

function SatCheck({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span className="inline-flex items-center gap-1 text-[11px]">
      {ok ? (
        <CheckCircle2 className="size-3 text-green-600 shrink-0" />
      ) : (
        <Circle className="size-3 text-muted-foreground shrink-0" />
      )}
      <span className={ok ? "text-foreground" : "text-muted-foreground"}>{label}</span>
    </span>
  );
}

function FormulacionCard({ ipr }: { ipr: FormulacionIPR }) {
  const router = useRouter();
  const daysColor =
    ipr.days_in_phase <= 30 ? "text-green-600" :
    ipr.days_in_phase <= 90 ? "text-amber-600" : "text-red-600";

  return (
    <div
      onClick={() => router.push(`/ipr/${ipr.id}?tab=${ipr.suggested_tab}`)}
      className="rounded-lg border bg-card p-3 cursor-pointer hover:bg-accent/50 transition-colors"
    >
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-2 min-w-0">
          <span className="font-mono text-xs text-muted-foreground">{ipr.codigo_bip}</span>
          <span className="text-xs font-medium truncate">{ipr.name}</span>
        </div>
        <span className={cn("text-[10px] tabular-nums shrink-0", daysColor)}>
          {ipr.days_in_phase}d
        </span>
      </div>

      {/* Phase-contextual checklist */}
      {ipr.phase === "F0" && (
        <div className="flex flex-wrap gap-x-3 gap-y-0.5 mb-1.5">
          <SatCheck ok={ipr.has_mechanism} label="Mecanismo" />
          <SatCheck ok={ipr.partes_count > 0} label={`Partes (${ipr.partes_count})`} />
          <SatCheck ok={ipr.territorio_count > 0} label={`Territorio (${ipr.territorio_count})`} />
          <SatCheck ok={ipr.hitos_count > 0} label={`Hitos (${ipr.hitos_count})`} />
        </div>
      )}
      {ipr.phase === "F1" && ipr.admisibilidad_total > 0 && (
        <div className="mb-1.5">
          <div className="flex items-center gap-2 text-[11px]">
            <span className="text-muted-foreground">Admisibilidad:</span>
            <span className={cn(
              "font-medium tabular-nums",
              ipr.admisibilidad_verified === ipr.admisibilidad_total ? "text-green-600" : "text-amber-600"
            )}>
              {ipr.admisibilidad_verified}/{ipr.admisibilidad_total}
            </span>
          </div>
        </div>
      )}
      {ipr.phase === "F2" && (
        <div className="flex items-center gap-2 text-[11px] mb-1.5">
          <SatCheck ok={ipr.eval_assigned} label="Evaluación asignada" />
          {ipr.eval_result && <SatCheck ok={true} label={ipr.eval_result} />}
        </div>
      )}

      {/* Suggested action */}
      <div className="flex items-center gap-1.5 text-[11px] text-indigo-600 dark:text-indigo-400">
        <ArrowRight className="size-3 shrink-0" />
        <span>{ipr.suggested_action}</span>
      </div>
    </div>
  );
}

export function ModuleFormulacion() {
  const [data, setData] = useState<MisFormulacionesResponse | null>(null);

  useEffect(() => {
    api.get<MisFormulacionesResponse>("/api/ipr/mis-formulaciones")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <div className="h-4 w-40 bg-muted animate-pulse rounded mb-3" />
        <div className="space-y-2">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="h-20 bg-muted animate-pulse rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (data.total === 0) {
    return (
      <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
        <h3 className="text-sm font-semibold mb-2">Mis IPRs en Formulación</h3>
        <p className="text-xs text-muted-foreground">Sin IPRs asignadas en formulación.</p>
      </div>
    );
  }

  const phases = ["F0", "F1", "F2"].filter(p => (data.by_phase[p]?.length ?? 0) > 0);

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Mis IPRs en Formulación</h3>
        <span className="text-xs text-muted-foreground tabular-nums">{data.total} activas</span>
      </div>

      <div className="space-y-3">
        {phases.map((phase) => (
          <div key={phase}>
            <div className="flex items-center gap-2 mb-1.5">
              <Badge className={cn("text-[10px] px-1.5 py-0", PHASE_COLORS[phase])}>
                {phase}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {PHASE_LABELS[phase]}
              </span>
              <span className="text-[10px] text-muted-foreground tabular-nums">
                ({data.by_phase[phase].length})
              </span>
            </div>
            <div className="space-y-1.5">
              {data.by_phase[phase].map((ipr) => (
                <FormulacionCard key={ipr.id} ipr={ipr} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Build check**

```bash
cd web && npx next build 2>&1 | grep -E "(error|Error|✓)" | head -5
```

- [ ] **Step 4: Commit**

```bash
git add web/src/app/(app)/dashboard/components/module-formulacion.tsx web/src/types/index.ts
git commit -m "feat(ui): create ModuleFormulacion — F0-F2 pipeline with checklists for ANALISTA"
```

---

## Chunk 3: Integration — wire up CommandCenter + cleanup

### Task 5: Wire modules in CommandCenter + remove ModuleMyProgress

**Files:**
- Modify: `web/src/app/(app)/dashboard/components/command-center.tsx`
- Delete: `web/src/app/(app)/dashboard/components/module-my-progress.tsx`

- [ ] **Step 1: Update CommandCenter imports and routing**

Replace ModuleMyProgress import with new modules. Update conditional rendering:

```tsx
// Replace this import:
// import { ModuleMyProgress } from "./module-my-progress";
// With:
import { ModuleMyWork } from "./module-my-work";
import { ModuleFormulacion } from "./module-formulacion";
```

Update PROGRESS_ROLES to exclude ENCARGADO and ANALISTA (they get dedicated modules). RTF and ASESOR_JURIDICO keep using KPIs only (no separate module — they have ModuleJuridico for ASESOR and action-items for RTF):

```tsx
// Remove PROGRESS_ROLES constant entirely (no longer used for module routing)
// Keep it only for KPI fetching
const KPI_ROLES: RoleCode[] = ["ENCARGADO", "ANALISTA", "RTF", "ASESOR_JURIDICO"];
```

Update the conditional module section (around line 93-98):

```tsx
{/* 3. Conditional module */}
{role === "ENCARGADO" && actionData && <ModuleMyWork items={actionData.items} />}
{role === "ANALISTA" && <ModuleFormulacion />}
{role && TEAM_ROLES.includes(role) && <ModuleMyTeam />}
{role && DGI_TEAM_ROLES.includes(role) && <ModuleDgiTeam />}
{role === "ASESOR_JURIDICO" && <ModuleJuridico />}
```

Update KPI fetching to use KPI_ROLES instead of PROGRESS_ROLES:

```tsx
} else if (KPI_ROLES.includes(role)) {
    api.get<{ kpis: KPICardData[] }>("/api/dashboard/mis-compromisos")
      .then((d) => setKpis(d.kpis))
      .catch(() => {});
}
```

- [ ] **Step 2: Delete ModuleMyProgress**

```bash
rm web/src/app/(app)/dashboard/components/module-my-progress.tsx
```

- [ ] **Step 3: Build + verify**

```bash
cd web && npx next build 2>&1 | grep -E "(error|Error|✓)" | head -5
```

Expected: Compiled successfully, 56 pages.

- [ ] **Step 4: Run all tests**

```bash
docker compose exec api pytest tests/test_dashboard.py tests/test_formulacion.py -v --tb=short
```

Expected: 8 passed (6 dashboard + 2 formulacion).

- [ ] **Step 5: Commit**

```bash
git add web/src/app/(app)/dashboard/components/command-center.tsx
git rm web/src/app/(app)/dashboard/components/module-my-progress.tsx
git commit -m "feat(ux): wire ENCARGADO→ModuleMyWork, ANALISTA→ModuleFormulacion, remove ModuleMyProgress"
```

---

## Summary

| Task | Component | Type | Lines |
|------|-----------|------|-------|
| 1 | ActionItem + ipr_id | Backend schema | ~15 |
| 2 | mis-formulaciones endpoint | Backend endpoint | ~100 |
| 3 | ModuleMyWork | Frontend component | ~130 |
| 4 | ModuleFormulacion | Frontend component | ~140 |
| 5 | CommandCenter wiring + cleanup | Integration | ~10 + deletion |

**Total: ~400 lines new, ~110 deleted. 5 commits. 1 new endpoint, 2 new components, 1 removed.**

**Test as:**
- `encargado.daf@goreos.cl` → should see "Mi Trabajo" grouped by IPR
- `analista.dipir@goreos.cl` → should see "Mis IPRs en Formulación" pipeline
- `jefe.daf@goreos.cl` → should still see "Mi Equipo" (unchanged)
- `regional@goreos.cl` → should still see KPIs + division breakdown (unchanged)
