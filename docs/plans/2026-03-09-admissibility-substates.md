# Admissibility Sub-states Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add track-specific admissibility checklist with PRE_ADMISIBLE sub-state to IPR F1 phase.

**Architecture:** New `PRE_ADMISIBLE` state in `ipr_state` scheme. Two new tables: `admissibility_item` (parametric, per track) and `admissibility_check` (operational, per IPR). Admin CRUD for items, IPR-scoped verification endpoints. Gate `checklist_complete` blocks PRE_ADMISIBLE→ADMISIBLE until all required items verified.

**Tech Stack:** FastAPI + raw SQL (text()), PostgreSQL, Next.js + shadcn/ui tabs.

**Design doc:** `docs/plans/2026-03-09-admissibility-substates-design.md`

---

## Critical Context

### State Machine (current → target)

**Current F1:**
```
INGRESADO (F0) → EN_REVISION (F1) → ADMISIBLE (F1) | INADMISIBLE (F1)
ADMISIBLE (F1) → EN_EVALUACION (F2)
```

**Target F1:**
```
INGRESADO (F0) → EN_REVISION (F1) → PRE_ADMISIBLE (F1) | INADMISIBLE (F1)
PRE_ADMISIBLE (F1) → ADMISIBLE (F1) | INADMISIBLE (F1)
ADMISIBLE (F1) → EN_EVALUACION (F2)
```

### Key: Same-phase transitions have NO automatic gates

The gate engine `_evaluate_phase_gates()` (ipr.py:1243) only fires on **phase boundary crosses** (F0→F1, F1→F2, etc.). All F1 states (EN_REVISION, PRE_ADMISIBLE, ADMISIBLE, INADMISIBLE) share phase F1. Therefore:
- EN_REVISION → PRE_ADMISIBLE: **no automatic gate** (just status change)
- PRE_ADMISIBLE → ADMISIBLE: needs **custom gate logic** added to PATCH endpoint
- The 7 existing F1→F2 gates fire at ADMISIBLE → EN_EVALUACION (unchanged)

### Pattern references

- **Admin CRUD pattern**: `admin.py` financing-tracks endpoints (~line 1000+). Uses `_require_admin()`, allowlist dict, raw SQL.
- **IPR tab pattern**: `web/src/app/(app)/ipr/components/tab-parentesco.tsx`. Self-contained with own fetch/state.
- **Migration pattern**: `goreos_migration_parentesco.sql`. BEGIN; CREATE TABLE IF NOT EXISTS; self-register; COMMIT.
- **Test pattern**: `conftest.py` cleanup at lines 38-84, tokens at 121-148, catalog at 170-257.
- **STATUS_PHASE_FIBER**: `ipr.py:38-57` — dict mapping status codes to F0-F5.

---

## Task 1: DDL Migration

**Files:**
- Create: `model/model_goreos/sql/goreos_migration_admissibility.sql`
- Create: `model/model_goreos/sql/goreos_rollback_admissibility.sql`

**Step 1: Write the migration**

```sql
-- goreos_migration_admissibility.sql
-- Adds PRE_ADMISIBLE state + admissibility checklist tables

BEGIN;

-- 1. New ipr_state: PRE_ADMISIBLE
INSERT INTO ref.category (scheme, code, label, description, scope, sort_order)
VALUES ('ipr_state', 'PRE_ADMISIBLE', 'Pre-admisible', 'Verificación de admisibilidad en curso', 'UNIVERSAL', 3)
ON CONFLICT (scheme, code) DO NOTHING;

-- 2. Update valid_transitions
-- EN_REVISION: was ["ADMISIBLE","INADMISIBLE"] → now ["PRE_ADMISIBLE","INADMISIBLE"]
UPDATE ref.category
SET valid_transitions = '["PRE_ADMISIBLE", "INADMISIBLE"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_REVISION';

-- PRE_ADMISIBLE: can go to ADMISIBLE or INADMISIBLE
UPDATE ref.category
SET valid_transitions = '["ADMISIBLE", "INADMISIBLE"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'PRE_ADMISIBLE';

-- ADMISIBLE: unchanged (→ EN_EVALUACION)
-- INADMISIBLE: unchanged (→ INGRESADO)

-- 3. Parametric table: checklist items per track
CREATE TABLE IF NOT EXISTS core.admissibility_item (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  financing_track_id UUID NOT NULL REFERENCES core.financing_track(id),
  code VARCHAR(50) NOT NULL,
  label TEXT NOT NULL,
  description TEXT,
  responsible_role VARCHAR(50) NOT NULL,
  sort_order INT DEFAULT 0,
  is_required BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ,
  CONSTRAINT uq_admissibility_item_track_code UNIQUE(financing_track_id, code)
);

-- 4. Operational table: verification checks per IPR
CREATE TABLE IF NOT EXISTS core.admissibility_check (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ipr_id UUID NOT NULL REFERENCES core.ipr(id),
  item_id UUID NOT NULL REFERENCES core.admissibility_item(id),
  verified_by_id UUID NOT NULL REFERENCES core."user"(id),
  verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT uq_admissibility_check_ipr_item UNIQUE(ipr_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_admissibility_check_ipr
  ON core.admissibility_check(ipr_id);

-- 5. Self-register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_admissibility.sql', 'manual', 'admissibility_substates')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
```

**Step 2: Write the rollback**

```sql
-- goreos_rollback_admissibility.sql
BEGIN;

DROP TABLE IF EXISTS core.admissibility_check;
DROP TABLE IF EXISTS core.admissibility_item;

-- Restore original transitions
UPDATE ref.category
SET valid_transitions = '["ADMISIBLE", "INADMISIBLE"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_REVISION';

DELETE FROM ref.category
WHERE scheme = 'ipr_state' AND code = 'PRE_ADMISIBLE';

DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_admissibility.sql';

COMMIT;
```

**Step 3: Run the migration**

```bash
# Production DB
docker exec -i goreos_db psql -U goreos -d goreos_model \
  < model/model_goreos/sql/goreos_migration_admissibility.sql

# Test DB
docker exec -i goreos_db psql -U goreos -d goreos_test \
  < model/model_goreos/sql/goreos_migration_admissibility.sql
```

**Step 4: Verify**

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c \
  "SELECT code, label, valid_transitions FROM ref.category WHERE scheme='ipr_state' AND code IN ('EN_REVISION','PRE_ADMISIBLE','ADMISIBLE') ORDER BY sort_order;"

docker exec goreos_db psql -U goreos -d goreos_model -c \
  "SELECT table_name FROM information_schema.tables WHERE table_schema='core' AND table_name LIKE 'admissibility%';"
```

Expected: 3 states with correct transitions, 2 new tables.

**Step 5: Commit**

```bash
git add model/model_goreos/sql/goreos_migration_admissibility.sql \
        model/model_goreos/sql/goreos_rollback_admissibility.sql
git commit -m "feat(ddl): admissibility sub-states — PRE_ADMISIBLE + checklist tables"
```

---

## Task 2: Admin CRUD for Admissibility Items

**Files:**
- Modify: `api/app/routers/admin.py` (add 3 endpoints at end, ~line 1388)
- Modify: `api/tests/conftest.py` (add cleanup)
- Create: `api/tests/test_admissibility.py`

**Step 1: Write the failing tests**

Create `api/tests/test_admissibility.py`:

```python
"""Tests for admissibility sub-states (PRE_ADMISIBLE checklist)."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

def auth(token: str):
    return {"Authorization": f"Bearer {token}"}


# ---------- helpers ----------

async def _get_track_id(client, token):
    """Get first financing track ID."""
    resp = await client.get("/api/admin/financing-tracks", headers=auth(token))
    assert resp.status_code == 200
    items = resp.json()["items"] if "items" in resp.json() else resp.json()
    assert len(items) > 0, "Need at least one financing track"
    return items[0]["id"]


# ---------- admin CRUD ----------

async def test_admin_create_admissibility_item(client: AsyncClient, admin_token: str):
    track_id = await _get_track_id(client, admin_token)
    resp = await client.post(
        "/api/admin/admissibility-items",
        json={
            "financing_track_id": track_id,
            "code": "TEST-DOC-LEGAL",
            "label": "Documentación legal completa",
            "responsible_role": "JEFE_DIVISION",
            "sort_order": 1,
            "is_required": True,
        },
        headers=auth(admin_token),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["code"] == "TEST-DOC-LEGAL"
    assert data["responsible_role"] == "JEFE_DIVISION"


async def test_admin_list_admissibility_items(client: AsyncClient, admin_token: str):
    track_id = await _get_track_id(client, admin_token)
    # Create one first
    await client.post(
        "/api/admin/admissibility-items",
        json={
            "financing_track_id": track_id,
            "code": "TEST-LIST-ITEM",
            "label": "Test item for listing",
            "responsible_role": "ADMIN_REGIONAL",
        },
        headers=auth(admin_token),
    )
    resp = await client.get(
        f"/api/admin/admissibility-items?track_id={track_id}",
        headers=auth(admin_token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert any(i["code"] == "TEST-LIST-ITEM" for i in items)


async def test_admin_update_admissibility_item(client: AsyncClient, admin_token: str):
    track_id = await _get_track_id(client, admin_token)
    create = await client.post(
        "/api/admin/admissibility-items",
        json={
            "financing_track_id": track_id,
            "code": "TEST-UPD-ITEM",
            "label": "Original label",
            "responsible_role": "JEFE_DIVISION",
        },
        headers=auth(admin_token),
    )
    item_id = create.json()["id"]
    resp = await client.patch(
        f"/api/admin/admissibility-items/{item_id}",
        json={"label": "Updated label", "is_required": False},
        headers=auth(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["label"] == "Updated label"
```

**Step 2: Run tests to verify they fail**

```bash
docker compose exec api pytest tests/test_admissibility.py -v
```

Expected: FAIL (404 — endpoints don't exist yet)

**Step 3: Add cleanup to conftest.py**

In `api/tests/conftest.py`, inside the `cleanup_test_artifacts` fixture (around line 38-84), add:

```python
    # Admissibility cleanup
    await db.execute(text(
        "DELETE FROM core.admissibility_check WHERE item_id IN "
        "(SELECT id FROM core.admissibility_item WHERE code LIKE 'TEST-%')"
    ))
    await db.execute(text(
        "DELETE FROM core.admissibility_item WHERE code LIKE 'TEST-%'"
    ))
```

**Step 4: Implement admin endpoints in `admin.py`**

Add at the end of `api/app/routers/admin.py` (~line 1388):

```python
# ── Admissibility items CRUD ─────────────────────────────────

_ADMISSIBILITY_ITEM_FIELDS = {"label", "description", "responsible_role", "sort_order", "is_required"}


@router.get("/admissibility-items")
async def list_admissibility_items(
    track_id: UUID | None = None,
    user: CurrentUser = ...,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    sql = """
        SELECT ai.id, ai.financing_track_id, ai.code, ai.label, ai.description,
               ai.responsible_role, ai.sort_order, ai.is_required,
               ft.code AS track_code
        FROM core.admissibility_item ai
        JOIN core.financing_track ft ON ft.id = ai.financing_track_id
        WHERE ai.deleted_at IS NULL
    """
    params: dict = {}
    if track_id:
        sql += " AND ai.financing_track_id = :track_id"
        params["track_id"] = str(track_id)
    sql += " ORDER BY ai.sort_order, ai.code"
    rows = (await db.execute(text(sql), params)).mappings().all()
    return [dict(r) for r in rows]


@router.post("/admissibility-items", status_code=201)
async def create_admissibility_item(
    data: dict,
    user: CurrentUser = ...,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    required = {"financing_track_id", "code", "label", "responsible_role"}
    missing = required - data.keys()
    if missing:
        raise HTTPException(400, f"Campos requeridos: {missing}")
    try:
        row = (await db.execute(
            text("""
                INSERT INTO core.admissibility_item
                  (financing_track_id, code, label, description, responsible_role, sort_order, is_required)
                VALUES (:financing_track_id, :code, :label, :description, :responsible_role, :sort_order, :is_required)
                RETURNING id, financing_track_id, code, label, description, responsible_role, sort_order, is_required
            """),
            {
                "financing_track_id": str(data["financing_track_id"]),
                "code": data["code"],
                "label": data["label"],
                "description": data.get("description"),
                "responsible_role": data["responsible_role"],
                "sort_order": data.get("sort_order", 0),
                "is_required": data.get("is_required", True),
            },
        )).mappings().first()
        await db.commit()
        return dict(row)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Ya existe un ítem con ese código para este track")


@router.patch("/admissibility-items/{item_id}")
async def update_admissibility_item(
    item_id: UUID,
    data: dict,
    user: CurrentUser = ...,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    existing = await db.execute(
        text("SELECT id FROM core.admissibility_item WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(item_id)},
    )
    if not existing.first():
        raise HTTPException(404, "Ítem de admisibilidad no encontrado")
    updates = {k: v for k, v in data.items() if k in _ADMISSIBILITY_ITEM_FIELDS}
    if not updates:
        return {"message": "Sin cambios"}
    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(item_id)
    row = (await db.execute(
        text(f"""
            UPDATE core.admissibility_item SET {set_clause}, updated_at = NOW()
            WHERE id = :id
            RETURNING id, financing_track_id, code, label, description, responsible_role, sort_order, is_required
        """),
        updates,
    )).mappings().first()
    await db.commit()
    return dict(row)
```

**Step 5: Run tests**

```bash
docker compose restart api
docker compose exec api pytest tests/test_admissibility.py -v
```

Expected: 3 passed

**Step 6: Commit**

```bash
git add api/app/routers/admin.py api/tests/test_admissibility.py api/tests/conftest.py
git commit -m "feat(admin): admissibility items CRUD — 3 endpoints + 3 tests"
```

---

## Task 3: IPR Checklist Endpoints

**Files:**
- Modify: `api/app/routers/ipr.py` (add 3 endpoints)
- Modify: `api/tests/test_admissibility.py` (add 4 tests)

**Step 1: Write the failing tests**

Add to `api/tests/test_admissibility.py`:

```python
# ---------- helpers for IPR checklist ----------

async def _create_ipr_in_pre_admisible(client, token, catalog, db):
    """Create an IPR and advance it to PRE_ADMISIBLE."""
    from sqlalchemy import text as sa_text

    # Get PRE_ADMISIBLE status ID
    row = (await db.execute(sa_text(
        "SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='PRE_ADMISIBLE'"
    ))).first()
    pre_admisible_id = str(row[0])

    # Create IPR directly in PRE_ADMISIBLE (shortcut for test)
    row = (await db.execute(sa_text("""
        INSERT INTO core.ipr (codigo_bip, nombre, ipr_nature, status_id, fiscal_year)
        VALUES (:code, 'Test Admissibility IPR', 'PROYECTO', :status_id, 2026)
        RETURNING id
    """), {"code": f"ADM-TEST-{__import__('uuid').uuid4().hex[:6]}", "status_id": pre_admisible_id})).first()
    await db.commit()
    return str(row[0])


async def _create_item_and_get_id(client, admin_token, track_id, code, role="JEFE_DIVISION"):
    resp = await client.post(
        "/api/admin/admissibility-items",
        json={
            "financing_track_id": track_id,
            "code": code,
            "label": f"Test item {code}",
            "responsible_role": role,
        },
        headers=auth(admin_token),
    )
    assert resp.status_code in (201, 409), resp.text
    if resp.status_code == 201:
        return resp.json()["id"]
    # Already exists — fetch it
    items = await client.get(
        f"/api/admin/admissibility-items?track_id={track_id}",
        headers=auth(admin_token),
    )
    return next(i["id"] for i in items.json() if i["code"] == code)


# ---------- checklist endpoints ----------

async def test_get_checklist(client: AsyncClient, admin_token: str, jefe_token: str, db):
    track_id = await _get_track_id(client, admin_token)
    item_id = await _create_item_and_get_id(client, admin_token, track_id, "TEST-CHK-GET")
    ipr_id = await _create_ipr_in_pre_admisible(client, admin_token, None, db)

    # Assign track to IPR
    from sqlalchemy import text as sa_text
    await db.execute(sa_text(
        "UPDATE core.ipr SET mechanism_id = (SELECT id FROM core.financing_track LIMIT 1) WHERE id = :id"
    ), {"id": ipr_id})
    await db.commit()

    resp = await client.get(
        f"/api/ipr/{ipr_id}/admisibilidad",
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total_items"] >= 1


async def test_verify_item_correct_role(client: AsyncClient, admin_token: str, jefe_token: str, db):
    track_id = await _get_track_id(client, admin_token)
    item_id = await _create_item_and_get_id(client, admin_token, track_id, "TEST-CHK-VER", "JEFE_DIVISION")
    ipr_id = await _create_ipr_in_pre_admisible(client, admin_token, None, db)

    from sqlalchemy import text as sa_text
    await db.execute(sa_text(
        "UPDATE core.ipr SET mechanism_id = (SELECT id FROM core.financing_track LIMIT 1) WHERE id = :id"
    ), {"id": ipr_id})
    await db.commit()

    resp = await client.post(
        f"/api/ipr/{ipr_id}/admisibilidad/{item_id}/verificar",
        json={"notes": "Verificado OK"},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200, resp.text


async def test_verify_item_wrong_role(client: AsyncClient, admin_token: str, encargado_token: str, db):
    track_id = await _get_track_id(client, admin_token)
    item_id = await _create_item_and_get_id(client, admin_token, track_id, "TEST-CHK-ROLE", "JEFE_DIVISION")
    ipr_id = await _create_ipr_in_pre_admisible(client, admin_token, None, db)

    from sqlalchemy import text as sa_text
    await db.execute(sa_text(
        "UPDATE core.ipr SET mechanism_id = (SELECT id FROM core.financing_track LIMIT 1) WHERE id = :id"
    ), {"id": ipr_id})
    await db.commit()

    resp = await client.post(
        f"/api/ipr/{ipr_id}/admisibilidad/{item_id}/verificar",
        json={},
        headers=auth(encargado_token),
    )
    assert resp.status_code == 403


async def test_unverify_item(client: AsyncClient, admin_token: str, jefe_token: str, db):
    track_id = await _get_track_id(client, admin_token)
    item_id = await _create_item_and_get_id(client, admin_token, track_id, "TEST-CHK-UNVER", "JEFE_DIVISION")
    ipr_id = await _create_ipr_in_pre_admisible(client, admin_token, None, db)

    from sqlalchemy import text as sa_text
    await db.execute(sa_text(
        "UPDATE core.ipr SET mechanism_id = (SELECT id FROM core.financing_track LIMIT 1) WHERE id = :id"
    ), {"id": ipr_id})
    await db.commit()

    # Verify first
    await client.post(
        f"/api/ipr/{ipr_id}/admisibilidad/{item_id}/verificar",
        json={},
        headers=auth(jefe_token),
    )
    # Unverify
    resp = await client.delete(
        f"/api/ipr/{ipr_id}/admisibilidad/{item_id}/verificar",
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200
```

**Step 2: Run tests to verify they fail**

```bash
docker compose exec api pytest tests/test_admissibility.py::test_get_checklist -v
```

Expected: FAIL (404 — endpoints don't exist)

**Step 3: Implement checklist endpoints in `ipr.py`**

Add 3 endpoints to `api/app/routers/ipr.py`. Place them BEFORE the `/{ipr_id}` PATCH endpoint (around line 1935) to avoid path conflicts:

```python
# ── Admissibility checklist endpoints ─────────────────────────

@router.get("/{ipr_id}/admisibilidad")
async def get_admissibility_checklist(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get checklist for IPR: items from its track + verification status."""
    # Get IPR's track
    ipr = (await db.execute(text("""
        SELECT i.id, i.mechanism_id, ft.code AS track_code
        FROM core.ipr i
        LEFT JOIN core.financing_track ft ON ft.id = i.mechanism_id
        WHERE i.id = :ipr_id
    """), {"ipr_id": str(ipr_id)})).mappings().first()
    if not ipr:
        raise HTTPException(404, "IPR no encontrado")
    if not ipr["mechanism_id"]:
        return {"track_code": None, "total_items": 0, "verified_count": 0, "pending_count": 0, "items": []}

    rows = (await db.execute(text("""
        SELECT ai.id AS item_id, ai.code, ai.label, ai.description,
               ai.responsible_role, ai.is_required, ai.sort_order,
               ac.verified_at, ac.notes,
               COALESCE(p.names || ' ' || p.paternal_surname, '') AS verified_by
        FROM core.admissibility_item ai
        LEFT JOIN core.admissibility_check ac ON ac.item_id = ai.id AND ac.ipr_id = :ipr_id
        LEFT JOIN core."user" u ON u.id = ac.verified_by_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE ai.financing_track_id = :track_id AND ai.deleted_at IS NULL
        ORDER BY ai.sort_order, ai.code
    """), {"ipr_id": str(ipr_id), "track_id": str(ipr["mechanism_id"])})).mappings().all()

    items = []
    verified_count = 0
    for r in rows:
        verified = r["verified_at"] is not None
        if verified:
            verified_count += 1
        items.append({
            "item_id": str(r["item_id"]),
            "code": r["code"],
            "label": r["label"],
            "description": r["description"],
            "responsible_role": r["responsible_role"],
            "is_required": r["is_required"],
            "verified": verified,
            "verified_by": r["verified_by"] if verified else None,
            "verified_at": r["verified_at"].isoformat() if verified else None,
            "notes": r["notes"],
        })

    total = len(items)
    required_pending = sum(1 for i in items if i["is_required"] and not i["verified"])
    return {
        "track_code": ipr["track_code"],
        "total_items": total,
        "verified_count": verified_count,
        "pending_count": required_pending,
        "items": items,
    }


@router.post("/{ipr_id}/admisibilidad/{item_id}/verificar")
async def verify_admissibility_item(
    ipr_id: UUID,
    item_id: UUID,
    data: dict | None = None,
    user: CurrentUser = ...,
    db: AsyncSession = Depends(get_db),
):
    """Mark a checklist item as verified. Role-restricted."""
    if data is None:
        data = {}
    # Fetch item to check responsible_role
    item = (await db.execute(text(
        "SELECT id, responsible_role FROM core.admissibility_item WHERE id = :id AND deleted_at IS NULL"
    ), {"id": str(item_id)})).mappings().first()
    if not item:
        raise HTTPException(404, "Ítem de admisibilidad no encontrado")

    user_role = user.get("role", "")
    if user_role != "ADMIN_SISTEMA" and user_role != item["responsible_role"]:
        raise HTTPException(403, f"Solo {item['responsible_role']} puede verificar este ítem")

    try:
        row = (await db.execute(text("""
            INSERT INTO core.admissibility_check (ipr_id, item_id, verified_by_id, notes)
            VALUES (:ipr_id, :item_id, :user_id, :notes)
            RETURNING id, verified_at
        """), {
            "ipr_id": str(ipr_id),
            "item_id": str(item_id),
            "user_id": user["id"],
            "notes": data.get("notes"),
        })).mappings().first()
        await db.commit()
        return {"message": "Ítem verificado", "verified_at": row["verified_at"].isoformat()}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Este ítem ya fue verificado para este IPR")


@router.delete("/{ipr_id}/admisibilidad/{item_id}/verificar")
async def unverify_admissibility_item(
    ipr_id: UUID,
    item_id: UUID,
    user: CurrentUser = ...,
    db: AsyncSession = Depends(get_db),
):
    """Unmark a checklist item verification."""
    # Check role
    item = (await db.execute(text(
        "SELECT responsible_role FROM core.admissibility_item WHERE id = :id AND deleted_at IS NULL"
    ), {"id": str(item_id)})).mappings().first()
    if not item:
        raise HTTPException(404, "Ítem no encontrado")

    user_role = user.get("role", "")
    if user_role != "ADMIN_SISTEMA" and user_role != item["responsible_role"]:
        raise HTTPException(403, f"Solo {item['responsible_role']} puede desmarcar este ítem")

    result = await db.execute(text(
        "DELETE FROM core.admissibility_check WHERE ipr_id = :ipr_id AND item_id = :item_id"
    ), {"ipr_id": str(ipr_id), "item_id": str(item_id)})
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(404, "Verificación no encontrada")
    return {"message": "Verificación desmarcada"}
```

**Important**: Add `from sqlalchemy.exc import IntegrityError` to imports at top of `ipr.py` if not already present.

**Step 4: Run tests**

```bash
docker compose restart api
docker compose exec api pytest tests/test_admissibility.py -v
```

Expected: 7 passed (3 admin + 4 checklist)

**Step 5: Commit**

```bash
git add api/app/routers/ipr.py api/tests/test_admissibility.py
git commit -m "feat(ipr): admissibility checklist — 3 endpoints + 4 tests"
```

---

## Task 4: Gate Logic — checklist_complete

**Files:**
- Modify: `api/app/routers/ipr.py` (PATCH endpoint + STATUS_PHASE_FIBER)
- Modify: `api/tests/test_admissibility.py` (add 3 gate tests)

**Step 1: Write the failing tests**

Add to `api/tests/test_admissibility.py`:

```python
# ---------- gate tests ----------

async def test_transition_to_pre_admisible(client: AsyncClient, admin_token: str, regional_token: str, catalog, db):
    """EN_REVISION → PRE_ADMISIBLE should work (no gate beyond valid_transitions)."""
    from sqlalchemy import text as sa_text

    en_revision_id = str((await db.execute(sa_text(
        "SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='EN_REVISION'"
    ))).scalar())
    pre_admisible_id = str((await db.execute(sa_text(
        "SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='PRE_ADMISIBLE'"
    ))).scalar())

    # Create IPR in EN_REVISION with mechanism
    ipr = (await db.execute(sa_text("""
        INSERT INTO core.ipr (codigo_bip, nombre, ipr_nature, status_id, fiscal_year,
                               mechanism_id)
        VALUES (:code, 'Gate test IPR', 'PROYECTO', :status_id, 2026,
                (SELECT id FROM core.financing_track LIMIT 1))
        RETURNING id
    """), {"code": f"ADM-GATE-{__import__('uuid').uuid4().hex[:6]}", "status_id": en_revision_id})).first()
    await db.commit()

    resp = await client.patch(
        f"/api/ipr/{ipr[0]}",
        json={"status_id": pre_admisible_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200, resp.text


async def test_transition_admisible_blocked_incomplete(client: AsyncClient, admin_token: str, regional_token: str, db):
    """PRE_ADMISIBLE → ADMISIBLE blocked when required checklist items are not verified."""
    from sqlalchemy import text as sa_text

    track_id = await _get_track_id(client, admin_token)
    # Create a required item
    await _create_item_and_get_id(client, admin_token, track_id, "TEST-GATE-REQ", "JEFE_DIVISION")

    pre_admisible_id = str((await db.execute(sa_text(
        "SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='PRE_ADMISIBLE'"
    ))).scalar())
    admisible_id = str((await db.execute(sa_text(
        "SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='ADMISIBLE'"
    ))).scalar())

    ipr = (await db.execute(sa_text("""
        INSERT INTO core.ipr (codigo_bip, nombre, ipr_nature, status_id, fiscal_year,
                               mechanism_id)
        VALUES (:code, 'Gate blocked IPR', 'PROYECTO', :status_id, 2026,
                (SELECT id FROM core.financing_track LIMIT 1))
        RETURNING id
    """), {"code": f"ADM-BLK-{__import__('uuid').uuid4().hex[:6]}", "status_id": pre_admisible_id})).first()
    await db.commit()

    resp = await client.patch(
        f"/api/ipr/{ipr[0]}",
        json={"status_id": admisible_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409, resp.text
    assert "checklist" in resp.json()["detail"].lower() or "pendiente" in resp.json()["detail"].lower()


async def test_transition_admisible_allowed_complete(client: AsyncClient, admin_token: str, jefe_token: str, regional_token: str, db):
    """PRE_ADMISIBLE → ADMISIBLE allowed when all required items are verified."""
    from sqlalchemy import text as sa_text

    track_id = await _get_track_id(client, admin_token)
    item_id = await _create_item_and_get_id(client, admin_token, track_id, "TEST-GATE-PASS", "JEFE_DIVISION")

    pre_admisible_id = str((await db.execute(sa_text(
        "SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='PRE_ADMISIBLE'"
    ))).scalar())
    admisible_id = str((await db.execute(sa_text(
        "SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='ADMISIBLE'"
    ))).scalar())

    ipr = (await db.execute(sa_text("""
        INSERT INTO core.ipr (codigo_bip, nombre, ipr_nature, status_id, fiscal_year,
                               mechanism_id)
        VALUES (:code, 'Gate pass IPR', 'PROYECTO', :status_id, 2026,
                (SELECT id FROM core.financing_track LIMIT 1))
        RETURNING id
    """), {"code": f"ADM-PASS-{__import__('uuid').uuid4().hex[:6]}", "status_id": pre_admisible_id})).first()
    await db.commit()
    ipr_id = str(ipr[0])

    # Verify the required item
    await client.post(
        f"/api/ipr/{ipr_id}/admisibilidad/{item_id}/verificar",
        json={},
        headers=auth(jefe_token),
    )

    # Now transition should work
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": admisible_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200, resp.text
```

**Step 2: Run tests to verify they fail**

```bash
docker compose exec api pytest tests/test_admissibility.py::test_transition_admisible_blocked_incomplete -v
```

Expected: FAIL (transition succeeds when it should block)

**Step 3: Implement gate logic**

In `api/app/routers/ipr.py`:

**3a. Update STATUS_PHASE_FIBER (line ~42)**:

Add `"PRE_ADMISIBLE": "F1",` after `"EN_REVISION": "F1",`

**3b. Add checklist gate function** (before `_evaluate_phase_gates`, around line 1240):

```python
async def _check_admissibility_checklist(ipr_id: str, db) -> dict:
    """Check if all required admissibility items are verified for this IPR."""
    row = (await db.execute(text("""
        SELECT COUNT(*) FILTER (WHERE ac.id IS NULL AND ai.is_required) AS pending,
               COUNT(*) AS total
        FROM core.admissibility_item ai
        LEFT JOIN core.admissibility_check ac ON ac.item_id = ai.id AND ac.ipr_id = :ipr_id
        WHERE ai.financing_track_id = (SELECT mechanism_id FROM core.ipr WHERE id = :ipr_id)
          AND ai.deleted_at IS NULL
    """), {"ipr_id": ipr_id})).first()

    pending = row[0] if row else 0
    total = row[1] if row else 0
    if total == 0:
        return {"name": "checklist_complete", "met": True, "detail": "Sin ítems de admisibilidad configurados para este track"}
    if pending > 0:
        return {"name": "checklist_complete", "met": False, "detail": f"Checklist incompleto: {pending} ítem(s) requerido(s) pendiente(s) de verificación"}
    return {"name": "checklist_complete", "met": True, "detail": f"Checklist completo: {total} ítem(s) verificados"}
```

**3c. Add gate check in PATCH endpoint** (around line 1995, inside the `update_ipr` function):

Find the section after phase gate evaluation and before the actual UPDATE. Add a check for PRE_ADMISIBLE → ADMISIBLE:

```python
    # Custom gate: PRE_ADMISIBLE → ADMISIBLE (same-phase, not caught by _evaluate_phase_gates)
    if current_code == "PRE_ADMISIBLE" and target_code == "ADMISIBLE":
        gate = await _check_admissibility_checklist(str(ipr_id), db)
        if not gate["met"]:
            raise HTTPException(409, gate["detail"])
```

**Step 4: Run tests**

```bash
docker compose restart api
docker compose exec api pytest tests/test_admissibility.py -v
```

Expected: 10 passed (3 admin + 4 checklist + 3 gates)

**Step 5: Commit**

```bash
git add api/app/routers/ipr.py api/tests/test_admissibility.py
git commit -m "feat(ipr): admissibility gate — checklist_complete blocks PRE_ADMISIBLE→ADMISIBLE"
```

---

## Task 5: Frontend — Tab Admisibilidad

**Files:**
- Create: `web/src/app/(app)/ipr/components/tab-admisibilidad.tsx`
- Modify: `web/src/app/(app)/ipr/[id]/page.tsx` (add tab #13)

**Step 1: Create tab component**

Create `web/src/app/(app)/ipr/components/tab-admisibilidad.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, Circle, Shield } from "lucide-react";
import { formatDateTime } from "@/lib/format";
import { useAuth } from "@/lib/auth";

interface ChecklistItem {
  item_id: string;
  code: string;
  label: string;
  description: string | null;
  responsible_role: string;
  is_required: boolean;
  verified: boolean;
  verified_by: string | null;
  verified_at: string | null;
  notes: string | null;
}

interface ChecklistResponse {
  track_code: string | null;
  total_items: number;
  verified_count: number;
  pending_count: number;
  items: ChecklistItem[];
}

interface Props {
  iprId: string;
  canManage: boolean;
}

export function TabAdmisibilidad({ iprId, canManage }: Props) {
  const { user } = useAuth();
  const [data, setData] = useState<ChecklistResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const res = await api.get<ChecklistResponse>(`/api/ipr/${iprId}/admisibilidad`);
      setData(res);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [iprId]);

  const handleVerify = async (itemId: string) => {
    try {
      await api.post(`/api/ipr/${iprId}/admisibilidad/${itemId}/verificar`, {});
      load();
    } catch (err) {
      const { toast } = await import("sonner");
      toast.error(err instanceof Error ? err.message : "Error al verificar");
    }
  };

  const handleUnverify = async (itemId: string) => {
    try {
      await api.delete(`/api/ipr/${iprId}/admisibilidad/${itemId}/verificar`);
      load();
    } catch (err) {
      const { toast } = await import("sonner");
      toast.error(err instanceof Error ? err.message : "Error al desmarcar");
    }
  };

  if (loading) return <div className="text-sm text-muted-foreground">Cargando checklist...</div>;
  if (!data || data.total_items === 0) {
    return <div className="text-sm text-muted-foreground">No hay ítems de admisibilidad configurados para este track.</div>;
  }

  const pct = data.total_items > 0 ? Math.round((data.verified_count / data.total_items) * 100) : 0;
  const userRole = user?.system_role || "";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Checklist de Admisibilidad
          </CardTitle>
          <Badge variant="outline">{data.track_code}</Badge>
        </div>
        <div className="space-y-2 pt-2">
          <div className="flex justify-between text-sm">
            <span>{data.verified_count}/{data.total_items} verificados</span>
            <span>{pct}%</span>
          </div>
          <Progress value={pct} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {data.items.map((item) => {
            const canVerify = canManage && (userRole === "ADMIN_SISTEMA" || userRole === item.responsible_role);
            return (
              <div key={item.item_id} className="flex items-start gap-3 rounded-lg border p-3">
                {item.verified ? (
                  <CheckCircle2 className="mt-0.5 h-5 w-5 text-green-600 shrink-0" />
                ) : (
                  <Circle className="mt-0.5 h-5 w-5 text-muted-foreground shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{item.label}</span>
                    {item.is_required && <Badge variant="destructive" className="text-[10px]">Requerido</Badge>}
                  </div>
                  {item.description && (
                    <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
                  )}
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="secondary" className="text-[10px]">{item.responsible_role}</Badge>
                    {item.verified && item.verified_by && (
                      <span className="text-xs text-muted-foreground">
                        {item.verified_by} — {formatDateTime(item.verified_at!)}
                      </span>
                    )}
                  </div>
                </div>
                {canVerify && !item.verified && (
                  <Button size="sm" variant="outline" onClick={() => handleVerify(item.item_id)}>
                    Verificar
                  </Button>
                )}
                {canVerify && item.verified && (
                  <Button size="sm" variant="ghost" className="text-muted-foreground" onClick={() => handleUnverify(item.item_id)}>
                    Desmarcar
                  </Button>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
```

**Step 2: Register tab in IPR detail page**

In `web/src/app/(app)/ipr/[id]/page.tsx`:

**2a. Add import** (after the last tab import, around line 37):
```tsx
import { TabAdmisibilidad } from "../components/tab-admisibilidad";
```

**2b. Add TabsTrigger** (after "parentesco" trigger, around line 514):
```tsx
<TabsTrigger value="admisibilidad">Admisibilidad</TabsTrigger>
```

**2c. Add TabsContent** (after parentesco TabsContent):
```tsx
<TabsContent value="admisibilidad" className="mt-4">
  <TabAdmisibilidad iprId={id} canManage={!!canManageChildren} />
</TabsContent>
```

**Step 3: Build and verify**

```bash
cd web && npx next build
```

Expected: Build succeeds with no errors.

**Step 4: Commit**

```bash
git add web/src/app/\(app\)/ipr/components/tab-admisibilidad.tsx \
        web/src/app/\(app\)/ipr/\[id\]/page.tsx
git commit -m "feat(frontend): admissibility tab — checklist with role-gated verification"
```

---

## Task 6: Documentation Update

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update CLAUDE.md**

- Update admin endpoint count (21 → 24) and add `admissibility-items` to admin description
- Update Rule 15 to include `admissibility-items` CRUD
- Add new rule about admissibility checklist pattern
- Update coverage line (endpoint count, test count)
- Update IPR detail tabs (12 → 13)

**Step 2: Run full test suite**

```bash
docker compose exec api pytest -v
```

Expected: All tests pass (374 + ~10 new = ~384)

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(CLAUDE.md): add admissibility sub-states coverage"
```

---

## Summary

| Task | Deliverable | Tests |
|------|------------|:-----:|
| 1 | DDL: 2 tables + PRE_ADMISIBLE state + transitions | 0 (manual verify) |
| 2 | Admin CRUD: 3 endpoints | 3 |
| 3 | IPR checklist: 3 endpoints | 4 |
| 4 | Gate: checklist_complete + STATUS_PHASE_FIBER | 3 |
| 5 | Frontend: tab-admisibilidad.tsx | 0 (build verify) |
| 6 | CLAUDE.md update | 0 (full suite) |
| **Total** | **6 endpoints + 1 gate + 1 tab + 2 tables** | **10** |
