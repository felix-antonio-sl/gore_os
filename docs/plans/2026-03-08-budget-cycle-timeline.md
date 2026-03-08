# HΩ-15 Budget Cycle Timeline (TP-05) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the TP-05 parametric table for the annual budget cycle timeline (T-1→T→T+1) with 17 milestones, operational tracking per fiscal year, CRUD endpoints, and a frontend timeline view — closing audit finding HΩ-15.

**Architecture:** New `core.budget_cycle_milestone` table holds the 17 standard milestones (parametric seed data). New `core.budget_cycle_tracking` table records per-fiscal-year completion status for each milestone. Backend: 5 new endpoints on the existing presupuesto router. Frontend: timeline component in the presupuesto page.

**Tech Stack:** FastAPI + raw SQL (text()), Pydantic v2 schemas, Next.js 16 + shadcn/ui, PostgreSQL 16.

---

## Task 1: DDL Migration — Create tables + seed 17 milestones

**Files:**
- Create: `model/model_goreos/sql/goreos_migration_budget_cycle.sql`

**Step 1: Write the migration SQL**

```sql
-- Budget Cycle Timeline (TP-05) — HΩ-15
-- Creates parametric milestone table + operational tracking table
-- Seeds 17 standard milestones from Omega GORE Ñuble spec
BEGIN;

-- TP-05: Parametric milestone definitions
CREATE TABLE IF NOT EXISTS core.budget_cycle_milestone (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phase VARCHAR(4) NOT NULL CHECK (phase IN ('T-1', 'T', 'T+1')),
    quarter VARCHAR(4) CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    ordinal SMALLINT NOT NULL UNIQUE CHECK (ordinal BETWEEN 1 AND 30),
    month_label VARCHAR(32) NOT NULL,
    name TEXT NOT NULL,
    responsible TEXT NOT NULL,
    deliverable TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Operational tracking: one row per milestone per fiscal year
CREATE TABLE IF NOT EXISTS core.budget_cycle_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    milestone_id UUID NOT NULL REFERENCES core.budget_cycle_milestone(id),
    fiscal_year SMALLINT NOT NULL CHECK (fiscal_year BETWEEN 2020 AND 2040),
    status VARCHAR(16) NOT NULL DEFAULT 'PENDIENTE'
        CHECK (status IN ('PENDIENTE', 'EN_CURSO', 'COMPLETADO', 'OMITIDO')),
    planned_date DATE,
    completed_at TIMESTAMPTZ,
    completed_by_id UUID REFERENCES core."user"(id),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (milestone_id, fiscal_year)
);

CREATE INDEX idx_bct_fiscal_year ON core.budget_cycle_tracking(fiscal_year);

-- Seed 17 standard milestones (Omega GORE Ñuble v2.6.0)
INSERT INTO core.budget_cycle_milestone (phase, quarter, ordinal, month_label, name, responsible, deliverable) VALUES
-- T-1: FORMULACIÓN (Jul-Dic año anterior)
('T-1', NULL,  1, 'Jul-Ago', 'DIPRES emite instrucciones presupuestarias',          'DIPRES',      'Circular instrucciones'),
('T-1', NULL,  2, 'Sep',     'Gobernador presenta proyecto presupuesto al CORE',     'Gobernador',  'Proyecto de presupuesto'),
('T-1', NULL,  3, 'Oct-Nov', 'CORE analiza y aprueba presupuesto',                   'CORE',        'Acuerdo aprobación'),
('T-1', NULL,  4, 'Dic',     'Ley de Presupuestos promulgada',                       'Congreso',    'Ley publicada en DO'),
-- T: EJECUCIÓN Q1 (Ene-Mar)
('T',   'Q1',  5, 'Ene',     'Decreto inicial de presupuesto',                       'Gobernador',  'Decreto promulgado'),
('T',   'Q1',  6, 'Feb-Mar', 'Primera distribución FNDR',                            'DIPIR',       'Resolución distribución'),
-- T: EJECUCIÓN Q2 (Abr-Jun)
('T',   'Q2',  7, 'Abr',     'Informe trimestral al CORE',                           'DIPIR/DAF',   'Informe Q1'),
('T',   'Q2',  8, 'May-Jun', 'Evaluación ejecución primer semestre',                 'DIPIR/DAF',   'Informe evaluación'),
-- T: EJECUCIÓN Q3 (Jul-Sep)
('T',   'Q3',  9, 'Jul',     'Informe semestral',                                    'DIPIR/DAF',   'Informe semestral'),
('T',   'Q3', 10, 'Ago',     'Solicitud de modificaciones presupuestarias',           'DIPIR',       'Propuesta modificación'),
('T',   'Q3', 11, 'Sep',     'CORE aprueba ajustes',                                 'CORE',        'Acuerdo ajustes'),
-- T: EJECUCIÓN Q4 (Oct-Dic)
('T',   'Q4', 12, 'Oct',     'Aceleración ejecución',                                'DIPIR/DAF',   'Plan aceleración'),
('T',   'Q4', 13, 'Nov',     'Última distribución recursos',                         'DIPIR',       'Resolución distribución'),
('T',   'Q4', 14, 'Dic',     'Cierre ejercicio presupuestario',                      'DAF',         'Acta cierre'),
-- T+1: EVALUACIÓN (Ene-Jun año siguiente)
('T+1', NULL, 15, 'Ene-Mar', 'Rendición de cuentas',                                 'DAF/UCR',     'Informe rendición'),
('T+1', NULL, 16, 'Abr',     'Cuenta Pública Gobernador',                            'Gobernador',  'Cuenta pública'),
('T+1', NULL, 17, 'May-Jun', 'Auditoría CGR',                                        'CGR',         'Informe auditoría')
ON CONFLICT DO NOTHING;

-- Self-register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_budget_cycle.sql', 'manual', 'budget_cycle')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
```

**Step 2: Apply migration to both databases**

Run:
```bash
docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_migration_budget_cycle.sql
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_migration_budget_cycle.sql
```

Expected: Both succeed with `COMMIT`. Verify:
```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT ordinal, phase, name FROM core.budget_cycle_milestone ORDER BY ordinal;"
```
Expected: 17 rows.

**Step 3: Commit**

```bash
git add model/model_goreos/sql/goreos_migration_budget_cycle.sql
git commit -m "feat(budget-cycle): DDL migration — TP-05 milestone table + 17 seed milestones"
```

---

## Task 2: Pydantic schemas for budget cycle

**Files:**
- Modify: `api/app/schemas/presupuesto.py` — add 4 new schemas at bottom

**Step 1: Add schemas**

Append to `api/app/schemas/presupuesto.py`:

```python
class BudgetCycleMilestoneItem(BaseModel):
    id: UUID
    phase: str
    quarter: Optional[str] = None
    ordinal: int
    month_label: str
    name: str
    responsible: str
    deliverable: Optional[str] = None


class BudgetCycleTrackingItem(BaseModel):
    id: UUID
    milestone_id: UUID
    ordinal: int
    phase: str
    quarter: Optional[str] = None
    month_label: str
    name: str
    responsible: str
    deliverable: Optional[str] = None
    fiscal_year: int
    status: str
    planned_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    completed_by_name: Optional[str] = None
    notes: Optional[str] = None


class BudgetCycleTrackingUpdate(BaseModel):
    status: Optional[str] = None
    planned_date: Optional[date] = None
    notes: Optional[str] = None


class BudgetCycleSummary(BaseModel):
    fiscal_year: int
    total_milestones: int
    completed: int
    en_curso: int
    pendiente: int
    omitido: int
    completion_pct: float
```

**Step 2: Commit**

```bash
git add api/app/schemas/presupuesto.py
git commit -m "feat(budget-cycle): Pydantic schemas for cycle milestones and tracking"
```

---

## Task 3: Backend endpoints — 5 new routes

**Files:**
- Modify: `api/app/routers/presupuesto.py` — add 5 endpoints at bottom (before glosa functions)
- Modify: `api/app/schemas/presupuesto.py` — import in router

**Step 1: Write the failing tests**

Add to `api/tests/test_presupuesto.py`:

```python
# --- Budget Cycle Timeline Tests ---

async def test_list_milestones(client, regional_token):
    """GET /api/presupuesto/ciclo/hitos returns 17 seed milestones."""
    resp = await client.get("/api/presupuesto/ciclo/hitos", headers=auth(regional_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 17
    assert data[0]["ordinal"] == 1
    assert data[0]["phase"] == "T-1"
    assert data[-1]["ordinal"] == 17


async def test_initialize_cycle(client, regional_token):
    """POST /api/presupuesto/ciclo/2026 creates tracking rows for all 17 milestones."""
    resp = await client.post("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["fiscal_year"] == 2026
    assert data["total_milestones"] == 17
    assert data["completed"] == 0
    assert data["pendiente"] == 17


async def test_initialize_cycle_idempotent(client, regional_token):
    """POST /api/presupuesto/ciclo/2027 is idempotent (second call returns same data)."""
    resp1 = await client.post("/api/presupuesto/ciclo/2027", headers=auth(regional_token))
    assert resp1.status_code == 201
    resp2 = await client.post("/api/presupuesto/ciclo/2027", headers=auth(regional_token))
    assert resp2.status_code == 200
    assert resp2.json()["total_milestones"] == 17


async def test_get_cycle_timeline(client, regional_token):
    """GET /api/presupuesto/ciclo/2026 returns timeline with all milestones."""
    # Ensure cycle exists
    await client.post("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    resp = await client.get("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 17
    assert data[0]["status"] == "PENDIENTE"
    assert data[0]["phase"] == "T-1"


async def test_update_milestone_status(client, regional_token):
    """PATCH milestone tracking to mark as COMPLETADO."""
    await client.post("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    timeline = (await client.get("/api/presupuesto/ciclo/2026", headers=auth(regional_token))).json()
    first_id = timeline[0]["id"]

    resp = await client.patch(
        f"/api/presupuesto/ciclo/tracking/{first_id}",
        json={"status": "COMPLETADO"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETADO"
    assert resp.json()["completed_at"] is not None


async def test_update_milestone_invalid_status(client, regional_token):
    """PATCH with invalid status returns 422."""
    await client.post("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    timeline = (await client.get("/api/presupuesto/ciclo/2026", headers=auth(regional_token))).json()
    first_id = timeline[0]["id"]

    resp = await client.patch(
        f"/api/presupuesto/ciclo/tracking/{first_id}",
        json={"status": "INVALIDO"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 422


async def test_encargado_cannot_modify_cycle(client, encargado_token):
    """ENCARGADO cannot initialize or modify cycle."""
    resp = await client.post("/api/presupuesto/ciclo/2026", headers=auth(encargado_token))
    assert resp.status_code == 403


async def test_cycle_summary(client, regional_token):
    """GET /api/presupuesto/ciclo/2026/resumen returns completion stats."""
    await client.post("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    resp = await client.get("/api/presupuesto/ciclo/2026/resumen", headers=auth(regional_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["fiscal_year"] == 2026
    assert data["total_milestones"] == 17
    assert data["completion_pct"] == 0.0
```

**Step 2: Run tests to verify they fail**

Run: `docker compose exec api pytest tests/test_presupuesto.py::test_list_milestones -v`
Expected: FAIL (404 — route not found)

**Step 3: Implement 5 endpoints in presupuesto.py**

Add these imports to the top of `presupuesto.py`:

```python
from app.schemas.presupuesto import (
    # ... existing imports ...
    BudgetCycleMilestoneItem,
    BudgetCycleTrackingItem,
    BudgetCycleTrackingUpdate,
    BudgetCycleSummary,
)
```

Add these 5 endpoints BEFORE the `check_glosa_rules` function (to avoid path conflicts with `/{presupuesto_id}`). They all use prefix `/ciclo/` which won't conflict:

```python
# ---------------------------------------------------------------------------
# Budget Cycle Timeline (TP-05 / HΩ-15)
# ---------------------------------------------------------------------------

_VALID_CYCLE_STATUSES = {"PENDIENTE", "EN_CURSO", "COMPLETADO", "OMITIDO"}


@router.get("/ciclo/hitos", response_model=list[BudgetCycleMilestoneItem])
async def list_cycle_milestones(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all 17 standard budget cycle milestones (parametric TP-05)."""
    result = await db.execute(
        text("""
            SELECT id, phase, quarter, ordinal, month_label, name, responsible, deliverable
            FROM core.budget_cycle_milestone
            ORDER BY ordinal
        """)
    )
    return [BudgetCycleMilestoneItem(**dict(r)) for r in result.mappings().all()]


@router.post("/ciclo/{fiscal_year}", status_code=201)
async def initialize_cycle(
    fiscal_year: int,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Initialize tracking rows for all milestones in a fiscal year. Idempotent."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR")

    if fiscal_year < 2020 or fiscal_year > 2040:
        raise HTTPException(status_code=422, detail="Año fiscal fuera de rango (2020-2040)")

    # Check if already initialized
    existing = (await db.execute(
        text("SELECT COUNT(*) FROM core.budget_cycle_tracking WHERE fiscal_year = :fy"),
        {"fy": fiscal_year},
    )).scalar()

    if existing and existing > 0:
        # Already initialized — return summary with 200
        return await _cycle_summary(db, fiscal_year, status_code=200)

    # Insert tracking row for each milestone
    await db.execute(
        text("""
            INSERT INTO core.budget_cycle_tracking (milestone_id, fiscal_year)
            SELECT id, :fy FROM core.budget_cycle_milestone
            ORDER BY ordinal
            ON CONFLICT (milestone_id, fiscal_year) DO NOTHING
        """),
        {"fy": fiscal_year},
    )
    await db.commit()

    return await _cycle_summary(db, fiscal_year)


@router.get("/ciclo/{fiscal_year}", response_model=list[BudgetCycleTrackingItem])
async def get_cycle_timeline(
    fiscal_year: int,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get the full timeline for a fiscal year with tracking status."""
    result = await db.execute(
        text("""
            SELECT t.id, t.milestone_id, m.ordinal, m.phase, m.quarter,
                   m.month_label, m.name, m.responsible, m.deliverable,
                   t.fiscal_year, t.status, t.planned_date, t.completed_at,
                   t.notes,
                   CASE WHEN p.id IS NOT NULL
                        THEN p.names || ' ' || p.paternal_surname
                        ELSE NULL END AS completed_by_name
            FROM core.budget_cycle_tracking t
            JOIN core.budget_cycle_milestone m ON m.id = t.milestone_id
            LEFT JOIN core."user" u ON u.id = t.completed_by_id
            LEFT JOIN core.person p ON p.id = u.person_id
            WHERE t.fiscal_year = :fy
            ORDER BY m.ordinal
        """),
        {"fy": fiscal_year},
    )
    rows = result.mappings().all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"Ciclo {fiscal_year} no inicializado")
    return [BudgetCycleTrackingItem(**dict(r)) for r in rows]


@router.get("/ciclo/{fiscal_year}/resumen", response_model=BudgetCycleSummary)
async def get_cycle_summary(
    fiscal_year: int,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get completion summary for a fiscal year cycle."""
    return await _cycle_summary(db, fiscal_year)


@router.patch("/ciclo/tracking/{tracking_id}")
async def update_cycle_tracking(
    tracking_id: UUID,
    body: BudgetCycleTrackingUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update a milestone tracking entry (status, planned_date, notes)."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION")

    # Validate status if provided
    if body.status and body.status not in _VALID_CYCLE_STATUSES:
        raise HTTPException(status_code=422, detail=f"Status inválido. Valores: {_VALID_CYCLE_STATUSES}")

    # Build dynamic SET clause
    sets = []
    params: dict = {"tid": str(tracking_id)}

    if body.status is not None:
        sets.append("status = :status")
        params["status"] = body.status
        if body.status == "COMPLETADO":
            sets.append("completed_at = NOW()")
            sets.append("completed_by_id = :uid")
            params["uid"] = user["sub"]
        elif body.status in ("PENDIENTE", "EN_CURSO"):
            sets.append("completed_at = NULL")
            sets.append("completed_by_id = NULL")

    if body.planned_date is not None:
        sets.append("planned_date = :planned_date")
        params["planned_date"] = body.planned_date

    if body.notes is not None:
        sets.append("notes = :notes")
        params["notes"] = body.notes

    if not sets:
        raise HTTPException(status_code=422, detail="Sin campos para actualizar")

    sets.append("updated_at = NOW()")
    set_clause = ", ".join(sets)

    result = await db.execute(
        text(f"""
            UPDATE core.budget_cycle_tracking SET {set_clause}
            WHERE id = :tid
            RETURNING id, milestone_id, fiscal_year, status, planned_date,
                      completed_at, notes
        """),
        params,
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Tracking entry not found")

    await db.commit()
    return dict(row)


async def _cycle_summary(db: AsyncSession, fiscal_year: int, status_code: int = 201) -> dict:
    """Build cycle summary response."""
    result = await db.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status = 'COMPLETADO') AS completed,
                COUNT(*) FILTER (WHERE status = 'EN_CURSO') AS en_curso,
                COUNT(*) FILTER (WHERE status = 'PENDIENTE') AS pendiente,
                COUNT(*) FILTER (WHERE status = 'OMITIDO') AS omitido
            FROM core.budget_cycle_tracking
            WHERE fiscal_year = :fy
        """),
        {"fy": fiscal_year},
    )
    row = result.mappings().first()
    if not row or row["total"] == 0:
        raise HTTPException(status_code=404, detail=f"Ciclo {fiscal_year} no inicializado")

    total = row["total"]
    completed = row["completed"]
    return {
        "fiscal_year": fiscal_year,
        "total_milestones": total,
        "completed": completed,
        "en_curso": row["en_curso"],
        "pendiente": row["pendiente"],
        "omitido": row["omitido"],
        "completion_pct": round(completed / total * 100, 1) if total > 0 else 0.0,
    }
```

**Step 4: Handle route ordering**

The `/ciclo/hitos`, `/ciclo/{fiscal_year}`, `/ciclo/{fiscal_year}/resumen`, and `/ciclo/tracking/{tracking_id}` routes all start with `/ciclo/` so they won't conflict with `/{presupuesto_id}` which expects a UUID. But they MUST be registered BEFORE `/{presupuesto_id}` in the router file. Place them after the `POST /` (create) endpoint and before `GET /{presupuesto_id}`.

Also: the `initialize_cycle` POST returns 201 on first call but should return 200 on subsequent calls. The `_cycle_summary` helper handles this — but the `@router.post` decorator sets `status_code=201`. For idempotent behavior, use `from starlette.responses import JSONResponse` to return 200 on existing cycles:

```python
from fastapi.responses import JSONResponse

# In initialize_cycle, replace the idempotent return:
if existing and existing > 0:
    summary = await _cycle_summary(db, fiscal_year)
    return JSONResponse(content=summary, status_code=200)
```

**Step 5: Run tests to verify they pass**

Run: `docker compose exec api pytest tests/test_presupuesto.py -v`
Expected: All 18 tests pass (10 existing + 8 new).

**Step 6: Commit**

```bash
git add api/app/routers/presupuesto.py api/app/schemas/presupuesto.py api/tests/test_presupuesto.py
git commit -m "feat(budget-cycle): 5 endpoints + 8 tests — cycle milestones, tracking, summary"
```

---

## Task 4: Frontend — Timeline component in presupuesto page

**Files:**
- Create: `web/src/app/(app)/presupuesto/ciclo/page.tsx` — dedicated cycle timeline page
- Modify: `web/src/components/sidebar.tsx` — add "Ciclo Presupuestario" nav item under Presupuesto (optional, can also be a tab)

**Step 1: Create the cycle timeline page**

The page should:
1. Show a year selector (default: current year)
2. Display the 17 milestones as a vertical timeline grouped by phase (T-1, T, T+1)
3. Each milestone shows: ordinal, name, month, responsible, status badge, completion date
4. Admin/Regional users see an "Inicializar" button if cycle not yet created
5. Admin/Regional/Jefe users can click a milestone to update its status

Use these UI patterns from the existing codebase:
- `Badge` from shadcn for status (PENDIENTE=gray, EN_CURSO=blue, COMPLETADO=green, OMITIDO=yellow)
- `Card` for each phase group
- `Select` for year picker
- `Button` for initialize action
- `Dialog` for status update (Select status + optional notes + date picker)
- `formatDate` from `@/lib/format` for dates
- `ApiClient` from `@/lib/api` for API calls

**File**: `web/src/app/(app)/presupuesto/ciclo/page.tsx`

```tsx
"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/lib/auth";
import api from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { ArrowLeft, CheckCircle2, Clock, Circle, SkipForward } from "lucide-react";
import { useRouter } from "next/navigation";
import { formatDate } from "@/lib/format";

interface TrackingItem {
  id: string;
  milestone_id: string;
  ordinal: number;
  phase: string;
  quarter: string | null;
  month_label: string;
  name: string;
  responsible: string;
  deliverable: string | null;
  fiscal_year: number;
  status: string;
  planned_date: string | null;
  completed_at: string | null;
  completed_by_name: string | null;
  notes: string | null;
}

interface CycleSummary {
  fiscal_year: number;
  total_milestones: number;
  completed: number;
  en_curso: number;
  pendiente: number;
  omitido: number;
  completion_pct: number;
}

const PHASE_LABELS: Record<string, string> = {
  "T-1": "T-1: Formulación (Año Anterior)",
  T: "T: Ejecución (Año Fiscal)",
  "T+1": "T+1: Evaluación (Año Siguiente)",
};

const STATUS_CONFIG: Record<
  string,
  { label: string; variant: "default" | "secondary" | "outline" | "destructive"; icon: typeof Circle }
> = {
  PENDIENTE: { label: "Pendiente", variant: "secondary", icon: Circle },
  EN_CURSO: { label: "En Curso", variant: "default", icon: Clock },
  COMPLETADO: { label: "Completado", variant: "outline", icon: CheckCircle2 },
  OMITIDO: { label: "Omitido", variant: "destructive", icon: SkipForward },
};

const currentYear = new Date().getFullYear();
const yearOptions = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i);

export default function CicloPresupuestarioPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [year, setYear] = useState(currentYear.toString());
  const [timeline, setTimeline] = useState<TrackingItem[]>([]);
  const [summary, setSummary] = useState<CycleSummary | null>(null);
  const [notInitialized, setNotInitialized] = useState(false);
  const [loading, setLoading] = useState(true);
  const [editItem, setEditItem] = useState<TrackingItem | null>(null);
  const [editStatus, setEditStatus] = useState("");
  const [editNotes, setEditNotes] = useState("");

  const canEdit = ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION"].includes(
    user?.role_code ?? ""
  );
  const canInitialize = ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"].includes(
    user?.role_code ?? ""
  );

  const loadCycle = useCallback(async () => {
    setLoading(true);
    setNotInitialized(false);
    try {
      const data = await api.get<TrackingItem[]>(`/api/presupuesto/ciclo/${year}`);
      setTimeline(data);
      const sum = await api.get<CycleSummary>(`/api/presupuesto/ciclo/${year}/resumen`);
      setSummary(sum);
    } catch {
      setTimeline([]);
      setSummary(null);
      setNotInitialized(true);
    } finally {
      setLoading(false);
    }
  }, [year]);

  useEffect(() => {
    loadCycle();
  }, [loadCycle]);

  const handleInitialize = async () => {
    try {
      await api.post(`/api/presupuesto/ciclo/${year}`, {});
      await loadCycle();
    } catch (err) {
      console.error(err);
    }
  };

  const handleEdit = (item: TrackingItem) => {
    setEditItem(item);
    setEditStatus(item.status);
    setEditNotes(item.notes ?? "");
  };

  const handleSave = async () => {
    if (!editItem) return;
    try {
      await api.patch(`/api/presupuesto/ciclo/tracking/${editItem.id}`, {
        status: editStatus,
        notes: editNotes || null,
      });
      setEditItem(null);
      await loadCycle();
    } catch (err) {
      console.error(err);
    }
  };

  const phases = ["T-1", "T", "T+1"];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/presupuesto")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-2xl font-bold">Ciclo Presupuestario</h1>
        <Select value={year} onValueChange={setYear}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {yearOptions.map((y) => (
              <SelectItem key={y} value={y.toString()}>
                {y}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {summary && (
          <Badge variant="outline" className="ml-auto text-sm">
            {summary.completion_pct}% completado ({summary.completed}/{summary.total_milestones})
          </Badge>
        )}
      </div>

      {loading && <p className="text-muted-foreground">Cargando...</p>}

      {notInitialized && !loading && (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground mb-4">
              El ciclo presupuestario {year} no ha sido inicializado.
            </p>
            {canInitialize && (
              <Button onClick={handleInitialize}>Inicializar Ciclo {year}</Button>
            )}
          </CardContent>
        </Card>
      )}

      {!loading &&
        !notInitialized &&
        phases.map((phase) => {
          const items = timeline.filter((t) => t.phase === phase);
          if (items.length === 0) return null;
          return (
            <Card key={phase}>
              <CardHeader>
                <CardTitle className="text-lg">{PHASE_LABELS[phase]}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {items.map((item) => {
                    const cfg = STATUS_CONFIG[item.status] ?? STATUS_CONFIG.PENDIENTE;
                    const Icon = cfg.icon;
                    return (
                      <div
                        key={item.id}
                        className={`flex items-start gap-3 p-3 rounded-lg border ${
                          canEdit ? "cursor-pointer hover:bg-accent" : ""
                        }`}
                        onClick={() => canEdit && handleEdit(item)}
                      >
                        <Icon className="h-5 w-5 mt-0.5 shrink-0 text-muted-foreground" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-sm">
                              {item.ordinal}. {item.name}
                            </span>
                            <Badge variant={cfg.variant} className="text-xs">
                              {cfg.label}
                            </Badge>
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {item.month_label} · {item.responsible}
                            {item.deliverable && ` · ${item.deliverable}`}
                          </div>
                          {item.completed_at && (
                            <div className="text-xs text-muted-foreground mt-1">
                              Completado: {formatDate(item.completed_at)}
                              {item.completed_by_name && ` por ${item.completed_by_name}`}
                            </div>
                          )}
                          {item.notes && (
                            <div className="text-xs mt-1 text-muted-foreground italic">
                              {item.notes}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          );
        })}

      <Dialog open={!!editItem} onOpenChange={() => setEditItem(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editItem?.ordinal}. {editItem?.name}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Estado</label>
              <Select value={editStatus} onValueChange={setEditStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
                    <SelectItem key={key} value={key}>
                      {cfg.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Notas</label>
              <Textarea
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                placeholder="Observaciones opcionales..."
                rows={3}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setEditItem(null)}>
                Cancelar
              </Button>
              <Button onClick={handleSave}>Guardar</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
```

**Step 2: Add nav link in sidebar**

In `web/src/components/sidebar.tsx`, add a nav item in `operationalNav` after "Presupuesto":

Find the Presupuesto entry and add below it:
```tsx
{ name: "Ciclo Ppto.", href: "/presupuesto/ciclo", icon: CalendarDays },
```

Import `CalendarDays` from `lucide-react`.

**Step 3: Verify build**

Run: `cd web && npx next build`
Expected: 0 TypeScript errors, 0 build errors.

**Step 4: Commit**

```bash
git add web/src/app/\(app\)/presupuesto/ciclo/page.tsx web/src/components/sidebar.tsx
git commit -m "feat(budget-cycle): frontend timeline page + sidebar nav"
```

---

## Task 5: Integration verification + cleanup

**Step 1: Run full test suite**

Run: `docker compose exec api pytest -v`
Expected: 334+ tests (326 existing + 8 new), all pass.

**Step 2: Run frontend build**

Run: `cd web && npx next build`
Expected: 0 errors.

**Step 3: Restart API and manual test**

```bash
docker compose restart api
```

Manual verification:
1. Login as `regional@goreos.cl` → Sidebar → "Ciclo Ppto."
2. Click "Inicializar Ciclo 2026" → 17 milestones appear
3. Click milestone 1 → change to "COMPLETADO" → save
4. Badge shows "5.9% completado (1/17)"
5. Change year to 2027 → shows "not initialized"

**Step 4: Update CLAUDE.md**

Add rule 50 (or next available number):
```
50. **Budget Cycle Timeline (TP-05)**: `core.budget_cycle_milestone` (17 seed rows) + `core.budget_cycle_tracking` (per fiscal year). 5 endpoints: `GET /ciclo/hitos`, `POST /ciclo/{year}` (initialize, idempotent), `GET /ciclo/{year}` (timeline), `GET /ciclo/{year}/resumen` (summary), `PATCH /ciclo/tracking/{id}` (update status). Statuses: PENDIENTE, EN_CURSO, COMPLETADO, OMITIDO. Frontend: `/presupuesto/ciclo` page with phase-grouped timeline.
```

**Step 5: Final commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md — budget cycle timeline TP-05 (HΩ-15)"
```

---

## Summary

| Task | Files | Tests | Description |
|------|-------|-------|-------------|
| 1 | 1 new SQL | 0 | DDL migration + 17 seed milestones |
| 2 | 1 modified | 0 | Pydantic schemas (4 new classes) |
| 3 | 3 modified | 8 new | 5 endpoints + 8 tests |
| 4 | 1 new + 1 modified | 0 | Frontend timeline page + sidebar |
| 5 | 1 modified | 0 | Verification + CLAUDE.md update |

**Totals**: 2 new files + 4 modified, 5 new endpoints, 8 new tests, 4 commits.
