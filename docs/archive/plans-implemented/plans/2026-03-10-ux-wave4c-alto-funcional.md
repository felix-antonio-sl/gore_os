# Wave 4C — ALTO Funcional Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close 3 ALTO severity UX findings (UX-011, UX-030, UX-047) to raise audit closure from 62% → 67%.

**Architecture:** UX-011 requires backend query expansion + frontend actionable list. UX-030 is frontend-only validation. UX-047 extends PATCH allowlist + schema + frontend edit form.

**Tech Stack:** FastAPI, SQLAlchemy raw SQL, Next.js, TypeScript, shadcn/ui.

---

### Task 1: UX-030 — Admin user edit form inline validation

**Files:**
- Modify: `web/src/app/(app)/admin/usuarios/page.tsx`

This is the simplest task — frontend-only, no backend changes.

**Step 1: Add validation state and helper**

After the `editSaving` state (around line 180), add:

```tsx
const [editErrors, setEditErrors] = useState<Record<string, string>>({});
```

Add a validation function before `handleSaveEdit`:

```tsx
const validateEditForm = (): Record<string, string> => {
  const errors: Record<string, string> = {};
  if (!editNames.trim()) errors.names = "Nombres es requerido";
  if (!editPaternal.trim()) errors.paternal = "Apellido paterno es requerido";
  if (!editEmail.trim()) {
    errors.email = "Email es requerido";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editEmail)) {
    errors.email = "Formato de email inválido";
  }
  return errors;
};
```

**Step 2: Add validation call in handleSaveEdit**

At the top of `handleSaveEdit` (line 195), after `if (!detail) return;`, add:

```tsx
const errors = validateEditForm();
if (Object.keys(errors).length > 0) {
  setEditErrors(errors);
  return;
}
setEditErrors({});
```

**Step 3: Add inline error messages under each required field**

For each of the 3 required fields (Nombres, Apellido paterno, Email), add an error message below the Input:

Nombres (line 472):
```tsx
<Input value={editNames} onChange={(e) => setEditNames(e.target.value)} className={editErrors.names ? "border-red-400" : ""} />
{editErrors.names && <p className="text-xs text-red-600">{editErrors.names}</p>}
```

Apellido paterno (line 476):
```tsx
<Input value={editPaternal} onChange={(e) => setEditPaternal(e.target.value)} className={editErrors.paternal ? "border-red-400" : ""} />
{editErrors.paternal && <p className="text-xs text-red-600">{editErrors.paternal}</p>}
```

Email (line 484):
```tsx
<Input value={editEmail} onChange={(e) => setEditEmail(e.target.value)} className={editErrors.email ? "border-red-400" : ""} />
{editErrors.email && <p className="text-xs text-red-600">{editErrors.email}</p>}
```

**Step 4: Clear errors when user starts editing**

Reset errors when entering edit mode. In the existing code where `setEditing(true)` is called (the "Editar" button click handler), add `setEditErrors({})`.

**Step 5: Build verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

**Step 6: Commit**

```bash
git add web/src/app/(app)/admin/usuarios/page.tsx
git commit -m "fix(ux): UX-030 add inline form validation to admin user edit"
```

---

### Task 2: UX-047 — Budget classifier PATCH post-creation

**Files:**
- Modify: `api/app/schemas/presupuesto.py` (line 76-82)
- Modify: `api/app/routers/presupuesto.py` (line 981)
- Modify: `web/src/app/(app)/presupuesto/page.tsx` (edit form, lines 380-390)

**Step 1: Add 3 classifier fields to Pydantic schema**

In `api/app/schemas/presupuesto.py`, class `PresupuestoUpdate` (line 76), add after `program_code_id`:

```python
class PresupuestoUpdate(BaseModel):
    initial_amount: Optional[Decimal] = None
    current_amount: Optional[Decimal] = None
    committed_amount: Optional[Decimal] = None
    accrued_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None
    program_code_id: Optional[UUID] = None
    subtitle_id: Optional[UUID] = None
    item_id: Optional[UUID] = None
    allocation_id: Optional[UUID] = None
```

**Step 2: Add 3 fields to backend PATCH allowlist**

In `api/app/routers/presupuesto.py` (line 981), change:

```python
UPDATABLE_COLUMNS = {"initial_amount", "current_amount", "committed_amount", "accrued_amount", "paid_amount", "program_code_id"}
```

To:

```python
UPDATABLE_COLUMNS = {"initial_amount", "current_amount", "committed_amount", "accrued_amount", "paid_amount", "program_code_id", "subtitle_id", "item_id", "allocation_id"}
```

**Step 3: Add classifier Select dropdowns to frontend edit form**

In `web/src/app/(app)/presupuesto/page.tsx`, add 3 state variables near the existing edit states (line 87):

```tsx
const [editSubtitle, setEditSubtitle] = useState("");
const [editItem, setEditItem] = useState("");
const [editAllocation, setEditAllocation] = useState("");
```

Add catalog state variables if not already present. The page already has `SUBTITLE_OPTIONS` (line 35). For items and allocations, we need to fetch from catalog or use the existing `item_id`/`allocation_id` from detail.

When entering edit mode (look for where edit state is initialized from `detail`), initialize these values from the selected budget program detail.

In the edit form (around lines 382-386), after the amount fields, add a separator and 3 Select dropdowns using existing `SUBTITLE_OPTIONS` and catalog data:

```tsx
<div className="border-t pt-2 mt-2">
  <p className="text-xs font-medium text-muted-foreground mb-2">Clasificador</p>
  <div className="flex items-center gap-2">
    <label className="text-xs text-muted-foreground w-28 shrink-0">Subtítulo</label>
    <Select value={editSubtitle} onValueChange={setEditSubtitle}>
      <SelectTrigger className="h-8 text-xs"><SelectValue placeholder="Sin cambio" /></SelectTrigger>
      <SelectContent>
        {SUBTITLE_OPTIONS.map((o) => (
          <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  </div>
</div>
```

For item and allocation, fetch the category options from `/api/catalogs/schemes/budget_item` and `/api/catalogs/schemes/budget_allocation` (or inline constants if small).

**Step 4: Include classifier fields in PATCH call**

In the `handleEditSave` function (around line 225), expand the body to include classifier UUIDs when changed:

```tsx
await api.patch(`/api/presupuesto/${selectedId}`, {
  initial_amount: editInitial ? parseFloat(editInitial) : undefined,
  current_amount: editCurrent ? parseFloat(editCurrent) : undefined,
  committed_amount: editCommitted ? parseFloat(editCommitted) : undefined,
  accrued_amount: editAccrued ? parseFloat(editAccrued) : undefined,
  paid_amount: editPaid ? parseFloat(editPaid) : undefined,
  subtitle_id: editSubtitle || undefined,
  item_id: editItem || undefined,
  allocation_id: editAllocation || undefined,
});
```

**Step 5: Import Select components**

Ensure `Select, SelectContent, SelectItem, SelectTrigger, SelectValue` are imported from `@/components/ui/select`.

**Step 6: Build verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

**Step 7: Commit**

```bash
git add api/app/schemas/presupuesto.py api/app/routers/presupuesto.py web/src/app/(app)/presupuesto/page.tsx
git commit -m "feat(ux): UX-047 enable budget classifier editing via PATCH"
```

---

### Task 3: UX-011 — Cockpit "Requieren Mi Decisión" with actionable items

**Files:**
- Modify: `api/app/routers/dgi_cockpit.py` (lines 80-91, ~228)
- Modify: `web/src/types/index.ts` (CockpitJefeDGI interface, line 369)
- Modify: `web/src/components/cockpit-jefe-dgi.tsx` (lines 100-109)

**Step 1: Expand backend query to return decision items**

In `api/app/routers/dgi_cockpit.py`, after the existing `decisions_sql` (line 81), add a new query that fetches the top 5 actionable items from 3 sources:

```python
# Decision items: top 5 actionable items across sources
decision_items_sql = text("""
    (
        SELECT 'alert' AS source, a.id, a.message AS title,
               sev.code AS severity, 'core.alert' AS subject_type
        FROM core.alert a
        JOIN ref.category sev ON sev.id = a.severity_id
        WHERE sev.code IN ('CRITICO', 'ALTO')
          AND a.resolved_at IS NULL
          AND a.action_taken IS NULL
          AND a.deleted_at IS NULL
        ORDER BY a.created_at DESC
        LIMIT 3
    )
    UNION ALL
    (
        SELECT 'rendition' AS source, r.id,
               'Rendición ' || LEFT(r.id::text, 8) || ' — ' || COALESCE(o.name, 'Sin ejecutor') AS title,
               CASE WHEN EXTRACT(EPOCH FROM NOW() - COALESCE(r.phase_entered_at, r.updated_at)) / 86400 > 7 THEN 'VENCIDA' ELSE 'PENDIENTE' END AS severity,
               'core.rendition' AS subject_type
        FROM core.rendition r
        LEFT JOIN core.organization o ON o.id = r.executor_id
        JOIN ref.category st ON st.id = r.status_id
        WHERE st.code IN ('PENDIENTE', 'EN_REVISION_RTF')
          AND r.deleted_at IS NULL
        ORDER BY r.created_at ASC
        LIMIT 2
    )
""")
decision_rows = (await db.execute(decision_items_sql)).mappings().all()
decision_items = [
    {"source": r["source"], "id": str(r["id"]), "title": r["title"], "severity": r["severity"]}
    for r in decision_rows
]
```

**Step 2: Add `decision_items` to response**

In the return dict (around line 228), add `decision_items=decision_items` alongside `decisions_pending`.

**Step 3: Update TypeScript interface**

In `web/src/types/index.ts`, update `CockpitJefeDGI` (line 369):

```typescript
export interface CockpitJefeDGI {
  semaforo: DGIDimensionSummary[];
  decisions_pending: number;
  decision_items: { source: string; id: string; title: string; severity: string }[];
  team_status: { role: string; name: string; activity: string }[];
  critical_alerts: { id: string; message: string; severity: string }[];
  report_status: { title: string; status: string; due: string } | null;
  rendition_summary: RenditionSummary | null;
}
```

**Step 4: Update frontend to show actionable items**

In `web/src/components/cockpit-jefe-dgi.tsx`, destructure `decision_items` from data (line 34).

Replace the generic message (lines 103-108) with a list of actionable items:

```tsx
{decisions_pending === 0 ? (
  <p className="text-sm text-muted-foreground italic">Sin pendientes. Todo al día.</p>
) : (
  <div className="space-y-1.5">
    {(decision_items ?? []).slice(0, 5).map((item) => (
      <div
        key={`${item.source}-${item.id}`}
        className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm hover:bg-muted/50 cursor-pointer"
        role="button"
        tabIndex={0}
        onClick={() => {
          if (item.source === "alert") router.push("/alertas");
          else if (item.source === "rendition") router.push("/rendiciones");
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            if (item.source === "alert") router.push("/alertas");
            else if (item.source === "rendition") router.push("/rendiciones");
          }
        }}
      >
        <span className={cn(
          "inline-block h-2 w-2 rounded-full shrink-0",
          item.severity === "CRITICO" || item.severity === "VENCIDA" ? "bg-red-500" : "bg-orange-500"
        )} />
        <span className="truncate flex-1">{item.title}</span>
        <Badge variant="outline" className="text-[10px] px-1.5 py-0 shrink-0">
          {item.source === "alert" ? "Alerta" : "Rendición"}
        </Badge>
      </div>
    ))}
    {decisions_pending > (decision_items ?? []).length && (
      <p className="text-xs text-muted-foreground pl-1">
        +{decisions_pending - (decision_items ?? []).length} más
      </p>
    )}
  </div>
)}
```

**Step 5: Build verify (frontend)**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

**Step 6: Restart API**

Run: `docker compose restart api`

**Step 7: Commit**

```bash
git add api/app/routers/dgi_cockpit.py web/src/types/index.ts web/src/components/cockpit-jefe-dgi.tsx
git commit -m "feat(ux): UX-011 show actionable decision items in cockpit Jefe DGI"
```

---

### Task 4: Final build + restart

**Step 1: Full build**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build`

Expected: All routes compile, 0 errors.

**Step 2: Restart containers**

Run: `cd /Users/felixsanhueza/Developer/goreos && docker compose restart api web`
