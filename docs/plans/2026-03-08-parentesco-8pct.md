# HΩ-02 Parentesco 8% Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement kinship disqualification (parentesco) for SUBV8 mechanism — sworn declarations by evaluators/legal reps validated against GORE authorities, with F1→F2 blocking gate.

**Architecture:** New table `core.kinship_declaration` stores per-IPR sworn declarations from persons. A gate function `_check_kinship_declarations()` in `ipr.py` blocks F1→F2 for SUBV8 IPRs missing declarations or with declared conflicts. New catalog endpoint for person search by RUT/name. Frontend tab component in IPR detail.

**Tech Stack:** FastAPI, SQLAlchemy async (raw SQL), Pydantic v2, Next.js 16 (App Router), shadcn/ui, TypeScript

**Design doc:** `docs/plans/2026-03-08-parentesco-8pct-design.md`

---

## Context for implementer

**GORE_OS codebase conventions (MUST follow):**

- Raw SQL via `text()` — no ORM models. Queries: `db.execute(text("..."), params).mappings()`
- `CurrentUser` is `Annotated[dict, Depends(get_current_user)]`. Access user fields: `user["id"]`, `user["role_code"]`
- Role restriction: use `_require_roles(user, ...)` inline helper (NOT `require_roles()` from deps.py)
- Person columns: `names`, `paternal_surname` (NOT `nombre`, `apellido_paterno`)
- PATCH allowlist: field names in Pydantic update models must match DB columns exactly
- `asyncpg` type cast: use `CAST(:param AS uuid)` (NOT `:param::uuid`)
- Gate functions return `dict | None` — `None` means "silent pass" (not applicable), `dict` with `met: bool` for applicable gates
- SUBV8 gate pattern: first check if mechanism is SUBV8, return None if not
- Cleanup test artifacts: add DELETE to `conftest.py::cleanup_test_artifacts`
- After adding new Python files: `docker compose restart api`
- Test command: `docker compose exec api pytest tests/test_parentesco.py -v`
- IPR test helper: `_create_test_ipr(db, status_code, phase_code, mechanism_code, monto)` in test file — creates IPR with `codigo_bip` starting with prefix (auto UUID-based). Cleanup via conftest deleting by prefix.

**Authority roles (5):** GOBERNADOR, CONSEJERO_REGIONAL, SECRETARIO_EJECUTIVO, ADMIN_REGIONAL, JEFE_DIVISION

---

### Task 1: DDL Migration — `core.kinship_declaration` table

**Files:**
- Create: `model/model_goreos/sql/goreos_migration_parentesco.sql`
- Modify: `scripts/run_migrations.sh` (add migration to list)

**Step 1: Write the migration SQL**

Create `model/model_goreos/sql/goreos_migration_parentesco.sql`:

```sql
-- HΩ-02: Kinship declaration table for parentesco validation
BEGIN;

CREATE TABLE IF NOT EXISTS core.kinship_declaration (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id               UUID NOT NULL REFERENCES core.ipr(id),
    person_id            UUID NOT NULL REFERENCES core.person(id),
    declaration_type     VARCHAR(32) NOT NULL
                         CHECK (declaration_type IN ('EVALUADOR', 'REPRESENTANTE_LEGAL', 'PERSONAL_CONTRATADO')),
    declares_no_conflict BOOLEAN NOT NULL,
    related_authority_id UUID REFERENCES core.person(id),
    relationship_type    VARCHAR(16)
                         CHECK (relationship_type IS NULL OR relationship_type IN ('CONSANGUINIDAD', 'AFINIDAD')),
    relationship_degree  INT CHECK (relationship_degree IS NULL OR relationship_degree BETWEEN 1 AND 4),
    declared_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    validated_by_id      UUID REFERENCES core."user"(id),
    validated_at         TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at           TIMESTAMPTZ,
    CONSTRAINT uq_kinship_decl UNIQUE (ipr_id, person_id, declaration_type)
);

CREATE INDEX IF NOT EXISTS idx_kinship_declaration_ipr ON core.kinship_declaration(ipr_id);

-- Self-register
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_parentesco.sql', 'manual', 'parentesco_ho02')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
```

**Step 2: Add to migration runner**

In `scripts/run_migrations.sh`, add `goreos_migration_parentesco.sql` to the `MIGRATIONS` array.

**Step 3: Apply migration to both databases**

Run:
```bash
docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_migration_parentesco.sql
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_migration_parentesco.sql
```

Expected: `BEGIN` / `CREATE TABLE` / `CREATE INDEX` / `INSERT` / `COMMIT` — no errors.

**Step 4: Verify table exists**

Run:
```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "\d core.kinship_declaration"
```

Expected: Table description showing all columns.

**Step 5: Commit**

```bash
git add model/model_goreos/sql/goreos_migration_parentesco.sql scripts/run_migrations.sh
git commit -m "feat(parentesco): DDL migration — kinship_declaration table (HΩ-02)"
```

---

### Task 2: Pydantic schemas + catalog endpoint for person search

**Files:**
- Create: `api/app/schemas/kinship.py`
- Modify: `api/app/routers/catalogs.py` (add person search endpoint)

**Step 1: Create Pydantic schemas**

Create `api/app/schemas/kinship.py`:

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class KinshipDeclarationCreate(BaseModel):
    person_id: UUID
    declaration_type: str  # EVALUADOR | REPRESENTANTE_LEGAL | PERSONAL_CONTRATADO
    declares_no_conflict: bool
    related_authority_id: UUID | None = None
    relationship_type: str | None = None  # CONSANGUINIDAD | AFINIDAD
    relationship_degree: int | None = None  # 1-4


class KinshipDeclarationItem(BaseModel):
    id: UUID
    ipr_id: UUID
    person_id: UUID
    person_name: str
    person_rut: str | None
    declaration_type: str
    declares_no_conflict: bool
    related_authority_id: UUID | None
    related_authority_name: str | None = None
    relationship_type: str | None
    relationship_degree: int | None
    declared_at: datetime
    validated_by_id: UUID | None
    validated_at: datetime | None


class KinshipDeclarationValidate(BaseModel):
    validated: bool
```

**Step 2: Add person search to catalogs router**

Add to the end of `api/app/routers/catalogs.py`:

```python
@router.get("/persons")
async def get_persons_list(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    search: str | None = None,
):
    """Search persons by RUT, name, or surname. Used for kinship declarations."""
    query = """
        SELECT p.id, p.rut, p.names, p.paternal_surname, p.maternal_surname,
               o.name AS organization_name
        FROM core.person p
        LEFT JOIN core.organization o ON p.organization_id = o.id
        WHERE p.is_active = true
    """
    params: dict = {}
    if search:
        query += " AND (p.rut ILIKE :s OR p.names ILIKE :s OR p.paternal_surname ILIKE :s)"
        params["s"] = f"%{search}%"
    query += " ORDER BY p.paternal_surname, p.names LIMIT 50"
    result = await db.execute(text(query), params)
    return [dict(r) for r in result.mappings().all()]
```

**Step 3: Commit**

```bash
git add api/app/schemas/kinship.py api/app/routers/catalogs.py
git commit -m "feat(parentesco): Pydantic schemas + person catalog endpoint"
```

---

### Task 3: CRUD endpoints for kinship declarations

**Files:**
- Modify: `api/app/routers/ipr.py` (add 4 endpoints at end of file, before closing)

**Step 1: Add imports at top of `ipr.py`**

Add to the existing imports section (line 12-18 area):

```python
from app.schemas.kinship import KinshipDeclarationCreate, KinshipDeclarationItem, KinshipDeclarationValidate
```

**Step 2: Add CRUD endpoints at end of `ipr.py`**

Add these 4 endpoints BEFORE the last line of the file. Place them after the existing evaluaciones endpoints. Use the same pattern as other child-entity endpoints (`/api/ipr/{id}/partes`, `/api/ipr/{id}/evaluaciones`, etc.):

```python
# ---------------------------------------------------------------------------
# HΩ-02: Kinship declarations (parentesco)
# ---------------------------------------------------------------------------

_KINSHIP_WRITE_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL"}

@router.get("/{ipr_id}/parentesco", response_model=list[KinshipDeclarationItem])
async def list_kinship_declarations(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all kinship declarations for an IPR."""
    result = await db.execute(
        text("""
            SELECT kd.id, kd.ipr_id, kd.person_id,
                   (p.names || ' ' || p.paternal_surname) AS person_name,
                   p.rut AS person_rut,
                   kd.declaration_type, kd.declares_no_conflict,
                   kd.related_authority_id,
                   CASE WHEN kd.related_authority_id IS NOT NULL
                        THEN (SELECT pa.names || ' ' || pa.paternal_surname
                              FROM core.person pa WHERE pa.id = kd.related_authority_id)
                   END AS related_authority_name,
                   kd.relationship_type, kd.relationship_degree,
                   kd.declared_at, kd.validated_by_id, kd.validated_at
            FROM core.kinship_declaration kd
            JOIN core.person p ON p.id = kd.person_id
            WHERE kd.ipr_id = :ipr_id AND kd.deleted_at IS NULL
            ORDER BY kd.declared_at DESC
        """),
        {"ipr_id": str(ipr_id)},
    )
    return [dict(r) for r in result.mappings().all()]


@router.post("/{ipr_id}/parentesco", response_model=KinshipDeclarationItem, status_code=201)
async def create_kinship_declaration(
    ipr_id: UUID,
    body: KinshipDeclarationCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a kinship declaration for an IPR."""
    _require_roles(user, *_KINSHIP_WRITE_ROLES)

    # Validate declaration_type
    if body.declaration_type not in ("EVALUADOR", "REPRESENTANTE_LEGAL", "PERSONAL_CONTRATADO"):
        raise HTTPException(status_code=422, detail="declaration_type inválido")

    # If declares conflict, require authority details
    if not body.declares_no_conflict:
        if not body.related_authority_id or not body.relationship_type or body.relationship_degree is None:
            raise HTTPException(
                status_code=422,
                detail="Si declara conflicto, debe indicar autoridad relacionada, tipo y grado de parentesco",
            )

    # Verify person exists
    person = (await db.execute(
        text("SELECT id FROM core.person WHERE id = CAST(:pid AS uuid) AND is_active = true"),
        {"pid": str(body.person_id)},
    )).mappings().first()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    # Verify related authority is actually a GORE authority (if provided)
    if body.related_authority_id:
        authority_check = (await db.execute(
            text("""
                SELECT u.id FROM core."user" u
                JOIN ref.category r ON u.system_role_id = r.id
                WHERE u.person_id = CAST(:pid AS uuid) AND u.is_active = true
                  AND r.code IN ('GOBERNADOR', 'CONSEJERO_REGIONAL', 'SECRETARIO_EJECUTIVO',
                                 'ADMIN_REGIONAL', 'JEFE_DIVISION')
            """),
            {"pid": str(body.related_authority_id)},
        )).mappings().first()
        if not authority_check:
            raise HTTPException(
                status_code=422,
                detail="La persona indicada como autoridad no tiene un rol de autoridad GORE",
            )

    try:
        row = (await db.execute(
            text("""
                INSERT INTO core.kinship_declaration (
                    ipr_id, person_id, declaration_type, declares_no_conflict,
                    related_authority_id, relationship_type, relationship_degree
                ) VALUES (
                    CAST(:ipr_id AS uuid), CAST(:person_id AS uuid), :declaration_type,
                    :declares_no_conflict, CAST(:related_authority_id AS uuid),
                    :relationship_type, :relationship_degree
                )
                RETURNING id, declared_at, created_at
            """),
            {
                "ipr_id": str(ipr_id),
                "person_id": str(body.person_id),
                "declaration_type": body.declaration_type,
                "declares_no_conflict": body.declares_no_conflict,
                "related_authority_id": str(body.related_authority_id) if body.related_authority_id else None,
                "relationship_type": body.relationship_type,
                "relationship_degree": body.relationship_degree,
            },
        )).mappings().first()
        await db.commit()
    except Exception as exc:
        await db.rollback()
        if "uq_kinship_decl" in str(exc):
            raise HTTPException(
                status_code=409,
                detail="Ya existe una declaración de esta persona con este tipo para este IPR",
            )
        raise

    # Re-fetch full item
    return await _get_kinship_declaration(row["id"], db)


@router.patch("/{ipr_id}/parentesco/{decl_id}", response_model=KinshipDeclarationItem)
async def validate_kinship_declaration(
    ipr_id: UUID,
    decl_id: UUID,
    body: KinshipDeclarationValidate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Validate (or invalidate) a kinship declaration. Admin only."""
    _require_roles(user, "ADMIN_SISTEMA")

    existing = (await db.execute(
        text("""
            SELECT id FROM core.kinship_declaration
            WHERE id = CAST(:id AS uuid) AND ipr_id = CAST(:ipr_id AS uuid) AND deleted_at IS NULL
        """),
        {"id": str(decl_id), "ipr_id": str(ipr_id)},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=404, detail="Declaración no encontrada")

    if body.validated:
        await db.execute(
            text("""
                UPDATE core.kinship_declaration
                SET validated_by_id = CAST(:uid AS uuid), validated_at = now(), updated_at = now()
                WHERE id = CAST(:id AS uuid)
            """),
            {"id": str(decl_id), "uid": str(user["id"])},
        )
    else:
        await db.execute(
            text("""
                UPDATE core.kinship_declaration
                SET validated_by_id = NULL, validated_at = NULL, updated_at = now()
                WHERE id = CAST(:id AS uuid)
            """),
            {"id": str(decl_id)},
        )
    await db.commit()
    return await _get_kinship_declaration(decl_id, db)


@router.delete("/{ipr_id}/parentesco/{decl_id}", status_code=204)
async def delete_kinship_declaration(
    ipr_id: UUID,
    decl_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a kinship declaration. Admin only."""
    _require_roles(user, "ADMIN_SISTEMA")
    result = await db.execute(
        text("""
            UPDATE core.kinship_declaration SET deleted_at = now(), updated_at = now()
            WHERE id = CAST(:id AS uuid) AND ipr_id = CAST(:ipr_id AS uuid) AND deleted_at IS NULL
        """),
        {"id": str(decl_id), "ipr_id": str(ipr_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Declaración no encontrada")
    await db.commit()


async def _get_kinship_declaration(decl_id, db: AsyncSession) -> dict:
    """Fetch a single kinship declaration with joined person names."""
    row = (await db.execute(
        text("""
            SELECT kd.id, kd.ipr_id, kd.person_id,
                   (p.names || ' ' || p.paternal_surname) AS person_name,
                   p.rut AS person_rut,
                   kd.declaration_type, kd.declares_no_conflict,
                   kd.related_authority_id,
                   CASE WHEN kd.related_authority_id IS NOT NULL
                        THEN (SELECT pa.names || ' ' || pa.paternal_surname
                              FROM core.person pa WHERE pa.id = kd.related_authority_id)
                   END AS related_authority_name,
                   kd.relationship_type, kd.relationship_degree,
                   kd.declared_at, kd.validated_by_id, kd.validated_at
            FROM core.kinship_declaration kd
            JOIN core.person p ON p.id = kd.person_id
            WHERE kd.id = CAST(:id AS uuid) AND kd.deleted_at IS NULL
        """),
        {"id": str(decl_id)},
    )).mappings().first()
    return dict(row)
```

**Step 3: Restart API and verify**

Run:
```bash
docker compose restart api
```

Verify endpoints appear in Swagger:
```bash
curl -s http://localhost:8000/api/docs | grep -c parentesco
```

**Step 4: Commit**

```bash
git add api/app/routers/ipr.py
git commit -m "feat(parentesco): 4 CRUD endpoints — list, create, validate, delete"
```

---

### Task 4: Gate function `_check_kinship_declarations()`

**Files:**
- Modify: `api/app/routers/ipr.py` (add gate function + wire into F1→F2)

**Step 1: Add gate function**

Add this function in `ipr.py` AFTER `_check_morosos_sisrec` (around line 1177) and BEFORE `_evaluate_phase_gates`:

```python
async def _check_kinship_declarations(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-02: SUBV8 requires kinship declarations from evaluators/legal reps."""
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or row["mechanism_code"] != "SUBV8":
        return None

    # Check declarations exist and none declare conflict
    decls = (await db.execute(
        text("""
            SELECT declares_no_conflict
            FROM core.kinship_declaration
            WHERE ipr_id = :id AND deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().all()

    if not decls:
        return {
            "name": "kinship_declarations",
            "met": False,
            "detail": (
                "SUBV8: requiere al menos una declaración jurada de parentesco. "
                "Registre las declaraciones de evaluadores y/o representantes legales "
                "en la pestaña Parentesco del IPR."
            ),
        }

    conflicts = [d for d in decls if not d["declares_no_conflict"]]
    if conflicts:
        return {
            "name": "kinship_declarations",
            "met": False,
            "detail": (
                f"SUBV8: {len(conflicts)} declaración(es) de parentesco declara(n) conflicto "
                f"con autoridades GORE. Inhabilidad por consanguinidad/afinidad."
            ),
        }

    return None  # All declarations are clean — silent pass
```

**Step 2: Wire gate into F1→F2 transition**

In `_evaluate_phase_gates()`, inside the `elif transition == "F1->F2":` block (around line 1204-1241), add at the end of that block (after the glosa06 executor check):

```python
        # HΩ-02: Kinship declarations for SUBV8
        kinship_gate = await _check_kinship_declarations(ipr_id, db)
        if kinship_gate is not None:
            gates.append(kinship_gate)
```

**Step 3: Commit**

```bash
git add api/app/routers/ipr.py
git commit -m "feat(parentesco): gate function _check_kinship_declarations at F1→F2"
```

---

### Task 5: Integration tests

**Files:**
- Create: `api/tests/test_parentesco.py`
- Modify: `api/tests/conftest.py` (cleanup)

**Step 1: Add cleanup to conftest.py**

In `conftest.py::cleanup_test_artifacts`, add BEFORE the IPR deletion line (`DELETE FROM core.ipr WHERE codigo_bip LIKE ...`):

```python
    await db.execute(
        text("""
            DELETE FROM core.kinship_declaration
            WHERE ipr_id IN (
                SELECT id FROM core.ipr WHERE codigo_bip LIKE 'KIN-%'
            )
        """)
    )
    await db.execute(text("DELETE FROM core.ipr WHERE codigo_bip LIKE 'KIN-%'"))
```

**Step 2: Create test file**

Create `api/tests/test_parentesco.py`:

```python
"""
Tests for HΩ-02: Kinship declarations (parentesco) for SUBV8.

10 tests:
- CRUD: list, create, create_conflict, duplicate_409, validate, delete
- Gate: blocks_missing, blocks_conflict, passes_clean, not_for_sni
"""
import json
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_category_id(db: AsyncSession, scheme: str, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :scheme AND code = :code"),
        {"scheme": scheme, "code": code},
    )).mappings().first()
    assert row, f"{scheme}/{code} not found"
    return str(row["id"])


async def _create_test_ipr(
    db: AsyncSession,
    status_code: str = "EN_REVISION",
    phase_code: str = "F1",
    mechanism_code: str | None = None,
    monto: float | None = None,
) -> str:
    """Create minimal IPR for parentesco tests."""
    bip = f"KIN-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_category_id(db, "ipr_state", status_code)
    phase_id = await _get_category_id(db, "mcd_phase", phase_code)
    mechanism_id = None
    if mechanism_code:
        mechanism_id = await _get_category_id(db, "mechanism", mechanism_code)

    meta = {}
    if monto is not None:
        meta["monto_total"] = str(monto)

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                mechanism_id, metadata, created_at, updated_at
            ) VALUES (
                :bip, 'Test Parentesco IPR', 'PROYECTO',
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                CAST(:mechanism_id AS uuid),
                CAST(:metadata AS jsonb), NOW(), NOW()
            )
            RETURNING id
        """),
        {
            "bip": bip, "status_id": status_id, "phase_id": phase_id,
            "mechanism_id": mechanism_id,
            "metadata": json.dumps(meta),
        },
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def _get_test_person_id(db: AsyncSession) -> str:
    """Get any active person from DB."""
    row = (await db.execute(
        text("SELECT id FROM core.person WHERE is_active = true LIMIT 1")
    )).mappings().first()
    assert row, "No active person found in goreos_test"
    return str(row["id"])


async def _get_authority_person_id(db: AsyncSession) -> str:
    """Get person_id of a user with authority role."""
    row = (await db.execute(
        text("""
            SELECT u.person_id FROM core."user" u
            JOIN ref.category r ON u.system_role_id = r.id
            WHERE u.is_active = true
              AND r.code IN ('GOBERNADOR', 'CONSEJERO_REGIONAL', 'SECRETARIO_EJECUTIVO',
                             'ADMIN_REGIONAL', 'JEFE_DIVISION')
            LIMIT 1
        """)
    )).mappings().first()
    assert row, "No authority user found in goreos_test"
    return str(row["person_id"])


def _find_gate(transitions: list[dict], target_phase: str, gate_name: str) -> dict | None:
    """Find a specific gate in transitions response."""
    for t in transitions:
        if t.get("target_phase") == target_phase:
            for g in t.get("gates", []):
                if g["name"] == gate_name:
                    return g
    return None


# ---------------------------------------------------------------------------
# CRUD Tests (6)
# ---------------------------------------------------------------------------

async def test_list_empty(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Listing declarations on an IPR with none returns empty list."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    resp = await client.get(f"/api/ipr/{ipr_id}/parentesco", headers=auth(admin_token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_no_conflict(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Create a declaration with no conflict."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    person_id = await _get_test_person_id(db)

    resp = await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={
            "person_id": person_id,
            "declaration_type": "EVALUADOR",
            "declares_no_conflict": True,
        },
        headers=auth(admin_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["declares_no_conflict"] is True
    assert data["person_id"] == person_id
    assert data["declaration_type"] == "EVALUADOR"


async def test_create_with_conflict(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Create a declaration declaring conflict with authority."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    person_id = await _get_test_person_id(db)
    authority_id = await _get_authority_person_id(db)

    resp = await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={
            "person_id": person_id,
            "declaration_type": "EVALUADOR",
            "declares_no_conflict": False,
            "related_authority_id": authority_id,
            "relationship_type": "CONSANGUINIDAD",
            "relationship_degree": 2,
        },
        headers=auth(admin_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["declares_no_conflict"] is False
    assert data["relationship_degree"] == 2
    assert data["related_authority_name"] is not None


async def test_duplicate_409(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Duplicate (same person + type + IPR) returns 409."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    person_id = await _get_test_person_id(db)

    body = {
        "person_id": person_id,
        "declaration_type": "EVALUADOR",
        "declares_no_conflict": True,
    }
    resp1 = await client.post(f"/api/ipr/{ipr_id}/parentesco", json=body, headers=auth(admin_token))
    assert resp1.status_code == 201

    resp2 = await client.post(f"/api/ipr/{ipr_id}/parentesco", json=body, headers=auth(admin_token))
    assert resp2.status_code == 409


async def test_validate_declaration(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Admin can validate a declaration."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    person_id = await _get_test_person_id(db)

    create_resp = await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={"person_id": person_id, "declaration_type": "EVALUADOR", "declares_no_conflict": True},
        headers=auth(admin_token),
    )
    decl_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/ipr/{ipr_id}/parentesco/{decl_id}",
        json={"validated": True},
        headers=auth(admin_token),
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["validated_at"] is not None


async def test_delete_declaration(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Admin can soft-delete a declaration."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    person_id = await _get_test_person_id(db)

    create_resp = await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={"person_id": person_id, "declaration_type": "EVALUADOR", "declares_no_conflict": True},
        headers=auth(admin_token),
    )
    decl_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/ipr/{ipr_id}/parentesco/{decl_id}",
        headers=auth(admin_token),
    )
    assert del_resp.status_code == 204

    # Verify gone from list
    list_resp = await client.get(f"/api/ipr/{ipr_id}/parentesco", headers=auth(admin_token))
    assert len(list_resp.json()) == 0


# ---------------------------------------------------------------------------
# Gate Tests (4)
# ---------------------------------------------------------------------------

async def test_gate_blocks_missing_declarations(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR at F1 with no declarations should block F1→F2."""
    ipr_id = await _create_test_ipr(db, "ADMISIBLE", "F1", "SUBV8", monto=50_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "kinship_declarations")
    assert gate is not None
    assert gate["met"] is False
    assert "declaración jurada" in gate["detail"].lower()


async def test_gate_blocks_conflict(
    client: AsyncClient, admin_token: str, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR with a conflict declaration should block F1→F2."""
    ipr_id = await _create_test_ipr(db, "ADMISIBLE", "F1", "SUBV8", monto=50_000_000)
    person_id = await _get_test_person_id(db)
    authority_id = await _get_authority_person_id(db)

    await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={
            "person_id": person_id,
            "declaration_type": "EVALUADOR",
            "declares_no_conflict": False,
            "related_authority_id": authority_id,
            "relationship_type": "CONSANGUINIDAD",
            "relationship_degree": 3,
        },
        headers=auth(admin_token),
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "kinship_declarations")
    assert gate is not None
    assert gate["met"] is False
    assert "conflicto" in gate["detail"].lower()


async def test_gate_passes_clean(
    client: AsyncClient, admin_token: str, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR with clean declarations should pass (gate absent = silent pass)."""
    ipr_id = await _create_test_ipr(db, "ADMISIBLE", "F1", "SUBV8", monto=50_000_000)
    person_id = await _get_test_person_id(db)

    await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={"person_id": person_id, "declaration_type": "EVALUADOR", "declares_no_conflict": True},
        headers=auth(admin_token),
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "kinship_declarations")
    assert gate is None, "Clean declarations should result in silent pass (no gate shown)"


async def test_gate_not_for_sni(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Non-SUBV8 mechanism (SNI) should not show kinship gate."""
    ipr_id = await _create_test_ipr(db, "ADMISIBLE", "F1", "SNI", monto=200_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "kinship_declarations")
    assert gate is None, "Kinship gate should not appear for non-SUBV8 mechanisms"
```

**Step 3: Run tests**

Run:
```bash
docker compose exec api pytest tests/test_parentesco.py -v
```

Expected: 10 passed.

**Step 4: Run full suite to verify no regressions**

Run:
```bash
docker compose exec api pytest -v --tb=short 2>&1 | tail -20
```

Expected: All existing tests still pass.

**Step 5: Commit**

```bash
git add api/tests/test_parentesco.py api/tests/conftest.py
git commit -m "test(parentesco): 10 integration tests — CRUD + gate validation"
```

---

### Task 6: Frontend tab component

**Files:**
- Create: `web/src/app/(app)/ipr/components/tab-parentesco.tsx`
- Modify: `web/src/app/(app)/ipr/[id]/page.tsx` (add tab + import)
- Modify: `web/src/types/index.ts` (add TypeScript interface)

**Step 1: Add TypeScript interface**

Add to `web/src/types/index.ts`:

```typescript
export interface KinshipDeclaration {
  id: string;
  ipr_id: string;
  person_id: string;
  person_name: string;
  person_rut: string | null;
  declaration_type: string;
  declares_no_conflict: boolean;
  related_authority_id: string | null;
  related_authority_name: string | null;
  relationship_type: string | null;
  relationship_degree: number | null;
  declared_at: string;
  validated_by_id: string | null;
  validated_at: string | null;
}

export interface PersonRef {
  id: string;
  rut: string | null;
  names: string;
  paternal_surname: string;
  maternal_surname: string | null;
  organization_name: string | null;
}
```

**Step 2: Create tab component**

Create `web/src/app/(app)/ipr/components/tab-parentesco.tsx`:

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ComboboxAsync } from "@/components/combobox-async";
import { Plus, CheckCircle2, XCircle, ShieldCheck, Trash2 } from "lucide-react";
import { formatDate } from "@/lib/format";
import { toast } from "sonner";
import type { KinshipDeclaration, PersonRef } from "@/types";

interface TabParentescoProps {
  iprId: string;
  canManage: boolean;
}

const DECLARATION_TYPES = [
  { value: "EVALUADOR", label: "Evaluador" },
  { value: "REPRESENTANTE_LEGAL", label: "Representante Legal" },
  { value: "PERSONAL_CONTRATADO", label: "Personal Contratado" },
];

const RELATIONSHIP_TYPES = [
  { value: "CONSANGUINIDAD", label: "Consanguinidad" },
  { value: "AFINIDAD", label: "Afinidad" },
];

export function TabParentesco({ iprId, canManage }: TabParentescoProps) {
  const [declarations, setDeclarations] = useState<KinshipDeclaration[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [personId, setPersonId] = useState("");
  const [declType, setDeclType] = useState("");
  const [noConflict, setNoConflict] = useState(true);
  const [authorityId, setAuthorityId] = useState("");
  const [relType, setRelType] = useState("");
  const [relDegree, setRelDegree] = useState("");

  const loadDeclarations = useCallback(() => {
    setLoading(true);
    api
      .get<KinshipDeclaration[]>(`/api/ipr/${iprId}/parentesco`)
      .then(setDeclarations)
      .catch(() => setDeclarations([]))
      .finally(() => setLoading(false));
  }, [iprId]);

  useEffect(() => {
    loadDeclarations();
  }, [loadDeclarations]);

  const searchPersons = async (query: string) => {
    const results = await api.get<PersonRef[]>(
      `/api/catalogs/persons?search=${encodeURIComponent(query)}`
    );
    return results.map((p) => ({
      value: p.id,
      label: `${p.paternal_surname}, ${p.names}${p.rut ? ` (${p.rut})` : ""}`,
    }));
  };

  const searchAuthorities = async (query: string) => {
    const results = await api.get<PersonRef[]>(
      `/api/catalogs/persons?search=${encodeURIComponent(query)}`
    );
    return results.map((p) => ({
      value: p.id,
      label: `${p.paternal_surname}, ${p.names}${p.rut ? ` (${p.rut})` : ""}`,
    }));
  };

  const resetForm = () => {
    setPersonId("");
    setDeclType("");
    setNoConflict(true);
    setAuthorityId("");
    setRelType("");
    setRelDegree("");
    setError(null);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const body: Record<string, unknown> = {
        person_id: personId,
        declaration_type: declType,
        declares_no_conflict: noConflict,
      };
      if (!noConflict) {
        body.related_authority_id = authorityId;
        body.relationship_type = relType;
        body.relationship_degree = parseInt(relDegree);
      }
      await api.post(`/api/ipr/${iprId}/parentesco`, body);
      setShowForm(false);
      resetForm();
      loadDeclarations();
      toast.success("Declaración registrada");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error al crear declaración";
      setError(msg);
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleValidate = async (declId: string) => {
    try {
      await api.patch(`/api/ipr/${iprId}/parentesco/${declId}`, { validated: true });
      loadDeclarations();
      toast.success("Declaración validada");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al validar");
    }
  };

  const handleDelete = async (declId: string) => {
    try {
      await api.delete(`/api/ipr/${iprId}/parentesco/${declId}`);
      loadDeclarations();
      toast.success("Declaración eliminada");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al eliminar");
    }
  };

  if (loading) return <p className="text-sm text-muted-foreground">Cargando...</p>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">
          Declaraciones de Parentesco ({declarations.length})
        </h3>
        {canManage && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => { setShowForm(!showForm); resetForm(); }}
          >
            <Plus className="h-4 w-4 mr-1" /> Nueva Declaración
          </Button>
        )}
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="border rounded-lg p-4 space-y-3 bg-muted/30">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium">Persona declarante</label>
              <ComboboxAsync
                value={personId}
                onChange={setPersonId}
                searchFn={searchPersons}
                placeholder="Buscar por RUT o nombre..."
              />
            </div>
            <div>
              <label className="text-xs font-medium">Tipo de declaración</label>
              <Select value={declType} onValueChange={setDeclType}>
                <SelectTrigger><SelectValue placeholder="Seleccione..." /></SelectTrigger>
                <SelectContent>
                  {DECLARATION_TYPES.map((t) => (
                    <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <label className="text-xs font-medium">¿Declara ausencia de conflicto?</label>
            <Select
              value={noConflict ? "true" : "false"}
              onValueChange={(v) => setNoConflict(v === "true")}
            >
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="true">Sí — Sin conflicto de parentesco</SelectItem>
                <SelectItem value="false">No — Declara parentesco con autoridad</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {!noConflict && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 border-t pt-3">
              <div>
                <label className="text-xs font-medium">Autoridad relacionada</label>
                <ComboboxAsync
                  value={authorityId}
                  onChange={setAuthorityId}
                  searchFn={searchAuthorities}
                  placeholder="Buscar autoridad..."
                />
              </div>
              <div>
                <label className="text-xs font-medium">Tipo de parentesco</label>
                <Select value={relType} onValueChange={setRelType}>
                  <SelectTrigger><SelectValue placeholder="Seleccione..." /></SelectTrigger>
                  <SelectContent>
                    {RELATIONSHIP_TYPES.map((t) => (
                      <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs font-medium">Grado (1-4)</label>
                <Select value={relDegree} onValueChange={setRelDegree}>
                  <SelectTrigger><SelectValue placeholder="Grado" /></SelectTrigger>
                  <SelectContent>
                    {[1, 2, 3, 4].map((d) => (
                      <SelectItem key={d} value={String(d)}>{d}°</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={submitting || !personId || !declType}>
              {submitting ? "Guardando..." : "Guardar"}
            </Button>
            <Button type="button" size="sm" variant="ghost" onClick={() => setShowForm(false)}>
              Cancelar
            </Button>
          </div>
        </form>
      )}

      {declarations.length === 0 && !showForm && (
        <p className="text-sm text-muted-foreground">No hay declaraciones registradas.</p>
      )}

      <div className="space-y-2">
        {declarations.map((d) => (
          <div key={d.id} className="border rounded-lg p-3 flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                {d.declares_no_conflict ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <XCircle className="h-4 w-4 text-red-600" />
                )}
                <span className="font-medium text-sm">{d.person_name}</span>
                {d.person_rut && (
                  <span className="text-xs text-muted-foreground">({d.person_rut})</span>
                )}
                <Badge variant="outline" className="text-xs">
                  {d.declaration_type}
                </Badge>
              </div>
              {!d.declares_no_conflict && d.related_authority_name && (
                <p className="text-xs text-red-600 ml-6">
                  Parentesco {d.relationship_type?.toLowerCase()} {d.relationship_degree}° con{" "}
                  {d.related_authority_name}
                </p>
              )}
              <p className="text-xs text-muted-foreground ml-6">
                Declarado: {formatDate(d.declared_at)}
                {d.validated_at && (
                  <span className="text-green-600 ml-2">
                    · Validado: {formatDate(d.validated_at)}
                  </span>
                )}
              </p>
            </div>
            {canManage && (
              <div className="flex gap-1">
                {!d.validated_at && (
                  <Button size="sm" variant="ghost" onClick={() => handleValidate(d.id)} title="Validar">
                    <ShieldCheck className="h-4 w-4" />
                  </Button>
                )}
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-red-600"
                  onClick={() => handleDelete(d.id)}
                  title="Eliminar"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Step 3: Add tab to IPR detail page**

In `web/src/app/(app)/ipr/[id]/page.tsx`:

Add import (with the other tab imports, around line 36):
```typescript
import { TabParentesco } from "../components/tab-parentesco";
```

Add TabsTrigger after "evaluaciones" (around line 512):
```tsx
          <TabsTrigger value="parentesco">Parentesco</TabsTrigger>
```

Add TabsContent after "evaluaciones" TabsContent (around line 557):
```tsx
        <TabsContent value="parentesco" className="mt-4">
          <TabParentesco iprId={id} canManage={!!canManageChildren} />
        </TabsContent>
```

**Step 4: Verify frontend builds**

Run:
```bash
cd web && npx next build 2>&1 | tail -10
```

Expected: Build succeeds with no errors.

**Step 5: Commit**

```bash
git add web/src/app/(app)/ipr/components/tab-parentesco.tsx web/src/app/(app)/ipr/[id]/page.tsx web/src/types/index.ts
git commit -m "feat(parentesco): frontend tab component — declarations CRUD + person search"
```

---

### Task 7: Update CLAUDE.md + memory

**Files:**
- Modify: `CLAUDE.md` (update metrics, add rule)
- Modify: memory files

**Step 1: Update CLAUDE.md coverage metrics**

Update the coverage line in CLAUDE.md to reflect 14/15 HΩ implemented and the new test count. Add a note about the parentesco feature.

**Step 2: Add CLAUDE.md rule 52**

Add rule:
```
52. **Kinship declarations (HΩ-02)**: `core.kinship_declaration` table with UNIQUE(ipr_id, person_id, declaration_type). CRUD via `/api/ipr/{id}/parentesco`. Gate `_check_kinship_declarations()` at F1→F2 for SUBV8 only — blocks if no declarations or if any declares conflict. Authority roles: GOBERNADOR, CONSEJERO_REGIONAL, SECRETARIO_EJECUTIVO, ADMIN_REGIONAL, JEFE_DIVISION. Declarations reference `core.person` via FK (not inline text).
```

**Step 3: Update HΩ-02 status from ABIERTO to CERRADO in audit doc**

Update `docs/GORE_OS_Audit_v3.0.md` HΩ-02 row.

**Step 4: Commit**

```bash
git add CLAUDE.md docs/GORE_OS_Audit_v3.0.md
git commit -m "docs: CLAUDE.md rule 52 + HΩ-02 closed (14/15 HΩ)"
```

---

## Summary

| Task | Description | Files | Tests |
|------|-------------|-------|-------|
| 1 | DDL migration | 1 new SQL + migration runner | — |
| 2 | Pydantic schemas + person catalog | 1 new schema + 1 modified router | — |
| 3 | 4 CRUD endpoints | 1 modified router (ipr.py) | — |
| 4 | Gate function F1→F2 | 1 modified router (ipr.py) | — |
| 5 | 10 integration tests | 1 new test file + conftest | 10 tests |
| 6 | Frontend tab component | 1 new component + 2 modified files | — |
| 7 | Docs + memory | CLAUDE.md + audit doc | — |

**Total new tests:** 10
**Total new endpoints:** 5 (4 parentesco CRUD + 1 person catalog)
**New DB table:** 1 (`core.kinship_declaration`)
