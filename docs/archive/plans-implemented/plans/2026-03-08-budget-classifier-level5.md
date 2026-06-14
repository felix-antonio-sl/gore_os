# Budget Classifier Level 5 (Programa DIPRES) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add the 5th DIPRES budget classification level (Programa presupuestario) as a `ref.category` scheme with admin CRUD, API filter, and frontend column.

**Architecture:** New `budget_program_code` scheme in `ref.category` (no dedicated table). FK column `program_code_id` on `core.budget_program`. Admin CRUD operates on `ref.category` rows filtered by scheme. Presupuesto list endpoint gets a new filter param + JOIN + response field. Frontend shows column in table and label in detail drawer.

**Tech Stack:** FastAPI + SQLAlchemy raw SQL, Pydantic v2 schemas, Next.js 16 + TypeScript + shadcn/ui

---

### Task 1: DDL Migration

**Files:**
- Create: `model/model_goreos/sql/goreos_migration_budget_program_code.sql`
- Create: `model/model_goreos/sql/goreos_rollback_budget_program_code.sql`
- Modify: `scripts/run_migrations.sh`

**Step 1: Write migration SQL**

```sql
-- goreos_migration_budget_program_code.sql
-- Adds program_code_id FK to core.budget_program (DIPRES Level 5)

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'core' AND table_name = 'budget_program' AND column_name = 'program_code_id'
  ) THEN
    ALTER TABLE core.budget_program
      ADD COLUMN program_code_id UUID REFERENCES ref.category(id);
  END IF;
END $$;

-- Register migration
INSERT INTO core.schema_migration (name, description)
VALUES ('budget_program_code', 'Add program_code_id FK to budget_program (DIPRES Level 5)')
ON CONFLICT (name) DO NOTHING;
```

**Step 2: Write rollback SQL**

```sql
-- goreos_rollback_budget_program_code.sql
ALTER TABLE core.budget_program DROP COLUMN IF EXISTS program_code_id;
DELETE FROM core.schema_migration WHERE name = 'budget_program_code';
```

**Step 3: Register in run_migrations.sh**

Add `budget_program_code` to the migration list array in `scripts/run_migrations.sh`.

**Step 4: Apply migration**

Run: `docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_migration_budget_program_code.sql`
Expected: `DO` + `INSERT 0 1` (or `INSERT 0 0` if idempotent re-run)

**Step 5: Commit**

```bash
git add model/model_goreos/sql/goreos_migration_budget_program_code.sql model/model_goreos/sql/goreos_rollback_budget_program_code.sql scripts/run_migrations.sh
git commit -m "feat(ddl): add program_code_id to budget_program (DIPRES Level 5)"
```

---

### Task 2: Admin CRUD Endpoints + Tests

**Files:**
- Modify: `api/app/routers/admin.py` (add 3 endpoints after sni-levels block, ~line 900)
- Modify: `api/tests/test_presupuesto.py` (add 3 admin CRUD tests)
- Modify: `api/tests/conftest.py` (add cleanup for budget_program_code scheme)

**Step 1: Write the failing tests**

Add to `api/tests/test_presupuesto.py`:

```python
# --- Admin CRUD: budget-program-codes ---

async def test_admin_create_program_code(client, admin_token):
    """Admin can create a budget program code."""
    resp = await client.post(
        "/api/admin/budget-program-codes",
        json={"code": "TEST-P01", "label": "Test Programa 01", "sort_order": 1},
        headers=auth(admin_token),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["code"] == "TEST-P01"
    assert "id" in data


async def test_admin_list_program_codes(client, admin_token):
    """Admin can list budget program codes."""
    # Create one first
    await client.post(
        "/api/admin/budget-program-codes",
        json={"code": "TEST-P02", "label": "Test Programa 02", "sort_order": 2},
        headers=auth(admin_token),
    )
    resp = await client.get("/api/admin/budget-program-codes", headers=auth(admin_token))
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    codes = [i["code"] for i in items]
    assert "TEST-P02" in codes


async def test_admin_update_program_code(client, admin_token):
    """Admin can update a budget program code label."""
    create_resp = await client.post(
        "/api/admin/budget-program-codes",
        json={"code": "TEST-P03", "label": "Original", "sort_order": 3},
        headers=auth(admin_token),
    )
    pid = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/admin/budget-program-codes/{pid}",
        json={"label": "Actualizado"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 200

    # Verify
    items = (await client.get("/api/admin/budget-program-codes", headers=auth(admin_token))).json()
    match = [i for i in items if i["id"] == pid]
    assert match[0]["label"] == "Actualizado"
```

**Step 2: Run tests to verify they fail**

Run: `docker compose exec api pytest tests/test_presupuesto.py::test_admin_create_program_code -v`
Expected: FAIL with `404 Not Found` (endpoint doesn't exist yet)

**Step 3: Add cleanup to conftest.py**

In `api/tests/conftest.py`, in the `cleanup_test_artifacts` function, add:

```python
await db.execute(text("DELETE FROM ref.category WHERE scheme = 'budget_program_code' AND code LIKE 'TEST-%'"))
```

**Step 4: Implement admin CRUD in admin.py**

Add after the sni-levels PATCH block (~line 900 in `admin.py`):

```python
# ---------------------------------------------------------------------------
# Budget Program Codes (DIPRES Level 5) — CRUD on ref.category scheme
# ---------------------------------------------------------------------------

_PROGRAM_CODE_FIELDS = {"label", "sort_order", "is_active"}


@router.get("/budget-program-codes")
async def list_budget_program_codes(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT id, code, label, sort_order, is_active, created_at, updated_at
            FROM ref.category
            WHERE scheme = 'budget_program_code'
            ORDER BY sort_order, code
        """)
    )
    return [dict(r) for r in result.mappings().all()]


@router.post("/budget-program-codes", status_code=status.HTTP_201_CREATED)
async def create_budget_program_code(
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    required = {"code", "label"}
    missing = required - set(data.keys())
    if missing:
        raise HTTPException(status_code=422, detail=f"Campos requeridos faltantes: {missing}")

    try:
        result = await db.execute(
            text("""
                INSERT INTO ref.category (scheme, code, label, sort_order, is_active, created_by_id)
                VALUES ('budget_program_code', :code, :label, :sort_order, true, :user_id)
                RETURNING id, code
            """),
            {
                "code": data["code"],
                "label": data["label"],
                "sort_order": data.get("sort_order", 0),
                "user_id": str(user["id"]),
            },
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"]), "code": row["code"]}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un código de programa con ese code")


@router.patch("/budget-program-codes/{code_id}")
async def update_budget_program_code(
    code_id: UUID,
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    existing = await db.execute(
        text("SELECT id FROM ref.category WHERE id = :id AND scheme = 'budget_program_code'"),
        {"id": str(code_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Código de programa no encontrado")

    updates = {k: v for k, v in data.items() if k in _PROGRAM_CODE_FIELDS}
    if not updates:
        return {"message": "Sin cambios"}

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(code_id)
    await db.execute(
        text(f"UPDATE ref.category SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    await db.commit()
    return {"message": "Actualizado"}
```

**Step 5: Run tests to verify they pass**

Run: `docker compose exec api pytest tests/test_presupuesto.py::test_admin_create_program_code tests/test_presupuesto.py::test_admin_list_program_codes tests/test_presupuesto.py::test_admin_update_program_code -v`
Expected: 3 PASS

**Step 6: Commit**

```bash
git add api/app/routers/admin.py api/tests/test_presupuesto.py api/tests/conftest.py
git commit -m "feat(admin): budget-program-codes CRUD (DIPRES Level 5) + 3 tests"
```

---

### Task 3: Presupuesto API — Filter, Schema, JOIN

**Files:**
- Modify: `api/app/schemas/presupuesto.py:25-65` (add `program_code_label` to ListItem/Detail, `program_code_id` to Create)
- Modify: `api/app/routers/presupuesto.py:398-514` (add JOIN, filter param, SELECT column, response field)
- Modify: `api/app/routers/presupuesto.py:912-945` (add program_code_id to INSERT)
- Modify: `api/app/routers/presupuesto.py:970` (add program_code_id to PATCH allowlist)
- Modify: `api/tests/test_presupuesto.py` (add 2 tests: filter + create with program_code_id)

**Step 1: Write failing tests**

Add to `api/tests/test_presupuesto.py`:

```python
async def test_filter_by_program_code(client, admin_token, regional_token, catalog):
    """Filter budget programs by program_code."""
    # Create a program code
    pc_resp = await client.post(
        "/api/admin/budget-program-codes",
        json={"code": "TEST-FILTER-PC", "label": "Filtro Test"},
        headers=auth(admin_token),
    )
    pc_id = pc_resp.json()["id"]

    # Create budget program with that code
    await _create_budget(client, regional_token, catalog, program_code_id=pc_id)

    # Filter by code
    resp = await client.get(
        "/api/presupuesto?program_code=TEST-FILTER-PC",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1
    assert all(i.get("program_code_label") == "Filtro Test" for i in items)


async def test_create_with_program_code(client, admin_token, regional_token, catalog):
    """Create budget program with program_code_id."""
    pc_resp = await client.post(
        "/api/admin/budget-program-codes",
        json={"code": "TEST-CREATE-PC", "label": "Create Test"},
        headers=auth(admin_token),
    )
    pc_id = pc_resp.json()["id"]

    data = await _create_budget(client, regional_token, catalog, program_code_id=pc_id)

    detail = await client.get(f"/api/presupuesto/{data['id']}", headers=auth(regional_token))
    body = detail.json()
    assert body.get("program_code_label") == "Create Test"
```

**Step 2: Run tests to verify they fail**

Run: `docker compose exec api pytest tests/test_presupuesto.py::test_filter_by_program_code -v`
Expected: FAIL

**Step 3: Update Pydantic schemas**

In `api/app/schemas/presupuesto.py`:

- `PresupuestoListItem` (line 25): add `program_code_label: Optional[str] = None` after `allocation_label`
- `PresupuestoCreate` (line 54): add `program_code_id: Optional[UUID] = None` after `allocation_id`
- `PresupuestoUpdate` (line 74): add `program_code_id: Optional[UUID] = None`

**Step 4: Update presupuesto router**

In `api/app/routers/presupuesto.py`:

1. **List endpoint** (line 398): Add param `program_code: str | None = None` after `program_type`
2. **Filter block** (after line 443): Add:
   ```python
   if program_code:
       conditions.append("pc.code = :program_code")
       params["program_code"] = program_code
   ```
3. **JOIN** (line 457): Add:
   ```sql
   LEFT JOIN ref.category pc ON pc.id = bp.program_code_id
   ```
4. **SELECT** (line 480): Add:
   ```sql
   pc.label AS program_code_label,
   ```
5. **Response mapping** (line 504): Add:
   ```python
   program_code_label=r["program_code_label"],
   ```
6. **Create INSERT** (line 914-927): Add `program_code_id` to column list and VALUES
7. **Create params** (line 936): Add:
   ```python
   "program_code_id": str(body.program_code_id) if body.program_code_id else None,
   ```
8. **PATCH allowlist** (line 970): Add `"program_code_id"` to `UPDATABLE_COLUMNS`

Also update the detail endpoint's SQL query to include the `pc` JOIN and `pc.label AS program_code_label`.

**Step 5: Run tests to verify they pass**

Run: `docker compose exec api pytest tests/test_presupuesto.py -v`
Expected: ALL PASS (18 existing + 5 new = 23)

**Step 6: Commit**

```bash
git add api/app/schemas/presupuesto.py api/app/routers/presupuesto.py api/tests/test_presupuesto.py
git commit -m "feat(presupuesto): program_code filter + schema + JOIN (DIPRES Level 5)"
```

---

### Task 4: Frontend — Column + Detail Label

**Files:**
- Modify: `web/src/types/index.ts:172-216` (add `program_code_label` to PresupuestoListItem)
- Modify: `web/src/app/(app)/presupuesto/page.tsx:20-30` (add to CSV_COLUMNS)
- Modify: `web/src/app/(app)/presupuesto/page.tsx:248-262` (add column in table after subtitle_label)
- Modify: `web/src/app/(app)/presupuesto/page.tsx:428-438` (add label in detail drawer)

**Step 1: Add TypeScript type**

In `web/src/types/index.ts`, add to `PresupuestoListItem` interface (after `allocation_label`):

```typescript
program_code_label: string | null;
```

**Step 2: Add CSV column**

In `web/src/app/(app)/presupuesto/page.tsx`, add to `CSV_COLUMNS` array (line 23, after program_type_label):

```typescript
{ key: "program_code_label", label: "Programa DIPRES" },
```

**Step 3: Add table column**

In the columns array (~line 255, after the subtitle_label column), add:

```typescript
{
  key: "program_code_label",
  label: "Programa",
  render: (v: unknown) => (
    <span className="text-xs text-muted-foreground">{String(v ?? "-")}</span>
  ),
},
```

**Step 4: Add detail drawer label**

In the detail classification section (~line 431, after subtitle_label):

```tsx
{detail.program_code_label && (
  <p><span className="text-muted-foreground">Programa: </span>{detail.program_code_label}</p>
)}
```

**Step 5: Verify frontend builds**

Run: `cd web && npx next build`
Expected: Build succeeds with no type errors

**Step 6: Commit**

```bash
git add web/src/types/index.ts web/src/app/(app)/presupuesto/page.tsx
git commit -m "feat(ui): show Programa DIPRES column in presupuesto table + detail"
```

---

### Task 5: Test DB Setup + Documentation

**Files:**
- Modify: `scripts/setup_test_db.sh` (apply migration to test DB)
- Modify: `CLAUDE.md` (update classifier level count + endpoint count)

**Step 1: Update test DB setup**

In `scripts/setup_test_db.sh`, add the migration to the list of applied migrations:

```bash
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_migration_budget_program_code.sql
```

**Step 2: Update CLAUDE.md**

- Rule 43: Change "4/6 levels" to "5/6 levels" and add `budget_program_code` scheme
- Admin endpoints count: 30 → 33
- Total endpoints: ~160 → ~163
- Test count: update if changed

**Step 3: Run full test suite**

Run: `docker compose exec api pytest -v`
Expected: ALL PASS (existing + 5 new)

**Step 4: Restart API container**

Run: `docker compose restart api`

**Step 5: Commit**

```bash
git add scripts/setup_test_db.sh CLAUDE.md
git commit -m "docs: budget classifier 5/6 levels, update endpoint counts"
```
