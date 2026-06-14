# C33 Technical Certification Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add SERVIU/MOP technical certification workflow for C33 IPRs with blocking gate at F1→F2, 3 endpoints, and frontend section.

**Architecture:** Parametric `categoria_c33` scheme in `ref.category` with `certifier_org_code` metadata drives auto-routing. All certification data stored in `core.ipr.metadata` JSONB (consistent with existing `_check_c33_conservation()` pattern). Blocking gate `_check_c33_technical_certification()` at F1→F2. 3 endpoints (GET status, POST solicitar, PATCH resolver) with role-escalated permissions.

**Tech Stack:** FastAPI + SQLAlchemy async (raw SQL), PostgreSQL JSONB, Next.js/React frontend.

**Design doc:** `docs/plans/2026-03-09-c33-technical-certification-design.md`

**Important codebase notes:**
- C33 fields (`categoria_c33`, `informe_tecnico_favorable`) exist as DDL columns in `core.ipr_mechanism` (lines 767-805 of DDL) but NO router code uses that table. The existing C33 gate reads `core.ipr.metadata` JSONB. We follow the metadata pattern.
- `_require_roles(user, *roles)` is at `ipr.py:1507-1509` — raises 403 if `user["role_code"]` not in roles.
- `_evaluate_phase_gates()` F1→F2 block is at `ipr.py:1294-1337`. C33 conservation gate is called at line ~1314.
- `jsonb_set()` pattern for atomic metadata updates: see `dgi_reports.py:414-427`.
- Test helper `_create_test_ipr()` in `test_track_rules.py:33-77` supports `metadata` dict parameter.
- All endpoints use `db.execute(text("..."), params).mappings()` pattern — NO ORM.
- Use `CAST(:param AS uuid)` not `::uuid` with asyncpg.

---

### Task 1: Migration — `categoria_c33` Scheme Seed

**Files:**
- Create: `model/model_goreos/sql/goreos_migration_c33_certification.sql`
- Create: `model/model_goreos/sql/goreos_rollback_c33_certification.sql`

**Step 1: Write the migration**

```sql
-- goreos_migration_c33_certification.sql
-- Adds categoria_c33 scheme to ref.category for C33 technical certification routing

BEGIN;

-- Seed categoria_c33 scheme with certifier org routing metadata
INSERT INTO ref.category (scheme, code, label, description, metadata)
VALUES
  ('categoria_c33', 'EDIFICACION', 'Edificación', 'Proyectos de edificación — certificación SERVIU', '{"certifier_org_code": "SERVIU"}'),
  ('categoria_c33', 'VIALIDAD', 'Vialidad', 'Proyectos viales — certificación MOP', '{"certifier_org_code": "MOP"}')
ON CONFLICT (scheme, code) DO NOTHING;

-- Self-register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_c33_certification.sql', 'manual', 'c33_certification_self_register')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
```

**Step 2: Write the rollback**

```sql
-- goreos_rollback_c33_certification.sql
BEGIN;

DELETE FROM ref.category WHERE scheme = 'categoria_c33';
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_c33_certification.sql';

COMMIT;
```

**Step 3: Apply migration to both databases**

Run:
```bash
docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_migration_c33_certification.sql
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_migration_c33_certification.sql
```

Expected: `INSERT 0 2` (or `INSERT 0 0` if already applied)

**Step 4: Verify**

Run:
```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT code, label, metadata FROM ref.category WHERE scheme = 'categoria_c33' ORDER BY code;"
```

Expected: 2 rows — EDIFICACION with SERVIU, VIALIDAD with MOP.

**Step 5: Commit**

```bash
git add model/model_goreos/sql/goreos_migration_c33_certification.sql model/model_goreos/sql/goreos_rollback_c33_certification.sql
git commit -m "feat(c33): DDL migration — categoria_c33 scheme with SERVIU/MOP routing"
```

---

### Task 2: Gate Function + Tests (TDD)

**Files:**
- Modify: `api/app/routers/ipr.py` (gate function + registration in F1→F2)
- Create: `api/tests/test_c33_certification.py`

**Step 1: Write the failing tests**

Create `api/tests/test_c33_certification.py`:

```python
"""Tests for C33 technical certification workflow."""
import uuid
import json
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth


async def _get_category_id(db: AsyncSession, scheme: str, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :scheme AND code = :code"),
        {"scheme": scheme, "code": code},
    )).scalar()
    assert row, f"{scheme}/{code} not found"
    return str(row)


async def _create_c33_ipr(
    db: AsyncSession,
    status_code: str = "ADMISIBLE",
    phase_code: str = "F1",
    categoria: str | None = None,
    informe: bool | None = None,
    cert_metadata: dict | None = None,
) -> str:
    """Create a C33 IPR with optional certification metadata."""
    bip = f"C33-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_category_id(db, "ipr_state", status_code)
    phase_id = await _get_category_id(db, "mcd_phase", phase_code)
    mechanism_id = await _get_category_id(db, "mechanism", "C33")

    meta = cert_metadata or {}
    if categoria:
        meta["categoria_c33"] = categoria
    if informe is not None:
        meta["informe_tecnico_favorable"] = informe
    meta_json = json.dumps(meta)

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                mechanism_id, metadata, created_at, updated_at
            ) VALUES (
                :bip, 'Test C33 IPR', 'PROYECTO',
                :status_id, :phase_id,
                CAST(:mechanism_id AS uuid),
                CAST(:metadata AS jsonb), NOW(), NOW()
            )
            RETURNING id
        """),
        {
            "bip": bip, "status_id": status_id, "phase_id": phase_id,
            "mechanism_id": mechanism_id, "metadata": meta_json,
        },
    )).mappings().first()
    await db.commit()
    return str(row["id"])


# ── Gate tests ──

async def test_c33_gate_blocks_no_categoria(client: AsyncClient, regional_token: str, db: AsyncSession):
    """F1→F2: blocks C33 IPR without categoria_c33."""
    ipr_id = await _create_c33_ipr(db, "ADMISIBLE", "F1")
    target_id = await _get_category_id(db, "ipr_state", "EN_EVALUACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "categoría C33" in resp.json()["detail"].lower() or "categoria" in resp.json()["detail"].lower()


async def test_c33_gate_blocks_no_certification(client: AsyncClient, regional_token: str, db: AsyncSession):
    """F1→F2: blocks C33 IPR with categoria but no certification result."""
    ipr_id = await _create_c33_ipr(db, "ADMISIBLE", "F1", categoria="EDIFICACION")
    target_id = await _get_category_id(db, "ipr_state", "EN_EVALUACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "certificación" in resp.json()["detail"].lower() or "SERVIU" in resp.json()["detail"]


async def test_c33_gate_blocks_unfavorable(client: AsyncClient, regional_token: str, db: AsyncSession):
    """F1→F2: blocks C33 IPR with unfavorable certification."""
    ipr_id = await _create_c33_ipr(db, "ADMISIBLE", "F1", categoria="VIALIDAD", informe=False)
    target_id = await _get_category_id(db, "ipr_state", "EN_EVALUACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "desfavorable" in resp.json()["detail"].lower()


async def test_c33_gate_passes_favorable(client: AsyncClient, regional_token: str, db: AsyncSession):
    """F1→F2: allows C33 IPR with favorable certification."""
    ipr_id = await _create_c33_ipr(db, "ADMISIBLE", "F1", categoria="EDIFICACION", informe=True)
    target_id = await _get_category_id(db, "ipr_state", "EN_EVALUACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
```

**Step 2: Run tests to verify they fail**

Run: `docker compose exec api pytest tests/test_c33_certification.py -v --tb=short`
Expected: 4 FAIL (gate function doesn't exist yet)

**Step 3: Implement the gate function**

Add to `api/app/routers/ipr.py`, after `_check_c33_conservation()` (after line 741):

```python
async def _check_c33_technical_certification(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """C33 technical certification gate (blocking, F1→F2).

    Routes to SERVIU (edificación) or MOP (vialidad) based on categoria_c33.
    Blocks if certification is missing or unfavorable.
    """
    ipr_row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code,
                   i.metadata->>'categoria_c33' AS categoria_c33,
                   i.metadata->>'informe_tecnico_favorable' AS informe
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()

    if not ipr_row or ipr_row["mechanism_code"] != "C33":
        return None

    categoria = ipr_row["categoria_c33"]
    informe = ipr_row["informe"]

    # Look up certifier org from categoria_c33 scheme
    certifier = None
    if categoria:
        cert_row = (await db.execute(
            text("""
                SELECT metadata->>'certifier_org_code' AS certifier
                FROM ref.category
                WHERE scheme = 'categoria_c33' AND code = :code AND deleted_at IS NULL
            """),
            {"code": categoria},
        )).mappings().first()
        certifier = cert_row["certifier"] if cert_row else None

    if not categoria:
        return {
            "name": "c33_technical_certification",
            "met": False,
            "detail": "Asignar categoría C33 (EDIFICACION/VIALIDAD) antes de continuar",
        }

    if informe is None:
        org_label = certifier or "organismo certificador"
        return {
            "name": "c33_technical_certification",
            "met": False,
            "detail": f"Certificación técnica pendiente — solicitar a {org_label}",
        }

    # metadata stores booleans as strings
    is_favorable = informe == "true" or informe is True
    if not is_favorable:
        org_label = certifier or "organismo certificador"
        return {
            "name": "c33_technical_certification",
            "met": False,
            "detail": f"Certificación técnica desfavorable de {org_label}",
        }

    return {
        "name": "c33_technical_certification",
        "met": True,
        "detail": f"Certificación técnica favorable de {certifier or 'organismo'}",
    }
```

Register in `_evaluate_phase_gates()` F1→F2 block (after the `_check_c33_conservation` call, around line 1316):

```python
    # C33 technical certification (blocking)
    c33_cert = await _check_c33_technical_certification(ipr_id, db)
    if c33_cert is not None:
        gates.append(c33_cert)
```

**Step 4: Run tests to verify they pass**

Run: `docker compose exec api pytest tests/test_c33_certification.py -v --tb=short`
Expected: 4 PASS

**Step 5: Commit**

```bash
git add api/app/routers/ipr.py api/tests/test_c33_certification.py
git commit -m "feat(c33): blocking gate _check_c33_technical_certification at F1→F2"
```

---

### Task 3: 3 Endpoints + Tests (TDD)

**Files:**
- Modify: `api/app/routers/ipr.py` (3 endpoints at end of file)
- Modify: `api/tests/test_c33_certification.py` (6 new tests)

**Step 1: Write the failing tests**

Append to `api/tests/test_c33_certification.py`:

```python
# ── GET status endpoint ──

async def test_get_certification_status_empty(client: AsyncClient, regional_token: str, db: AsyncSession):
    """GET returns empty status for IPR without certification."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="EDIFICACION")
    resp = await client.get(
        f"/api/ipr/{ipr_id}/certificacion-tecnica",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["categoria_c33"] == "EDIFICACION"
    assert data["certifier_org"] == "SERVIU"
    assert data["requested"] is False
    assert data["resolved"] is False


# ── POST solicitar endpoint ──

async def test_solicitar_certification(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """JEFE_DIVISION can request certification."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="EDIFICACION")
    resp = await client.post(
        f"/api/ipr/{ipr_id}/certificacion-tecnica/solicitar",
        json={},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["certifier_org"] == "SERVIU"
    assert data["requested_at"] is not None


async def test_solicitar_no_categoria(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """POST solicitar fails if categoria_c33 not assigned."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1")
    resp = await client.post(
        f"/api/ipr/{ipr_id}/certificacion-tecnica/solicitar",
        json={},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 409


async def test_solicitar_wrong_role(client: AsyncClient, encargado_token: str, db: AsyncSession):
    """ENCARGADO cannot request certification."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="EDIFICACION")
    resp = await client.post(
        f"/api/ipr/{ipr_id}/certificacion-tecnica/solicitar",
        json={},
        headers=auth(encargado_token),
    )
    assert resp.status_code == 403


# ── PATCH resolver endpoint ──

async def test_resolver_favorable(client: AsyncClient, jefe_token: str, regional_token: str, db: AsyncSession):
    """ADMIN_REGIONAL can register favorable result."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="VIALIDAD")
    # First request
    await client.post(
        f"/api/ipr/{ipr_id}/certificacion-tecnica/solicitar",
        json={},
        headers=auth(jefe_token),
    )
    # Then resolve
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/certificacion-tecnica",
        json={"favorable": True, "document_reference": "ORD. 123/2026"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["informe_tecnico_favorable"] is True


async def test_resolver_without_request(client: AsyncClient, regional_token: str, db: AsyncSession):
    """Cannot resolve without prior request."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="EDIFICACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/certificacion-tecnica",
        json={"favorable": True},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409


async def test_resolver_wrong_role(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """JEFE_DIVISION cannot resolve certification."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="EDIFICACION")
    await client.post(
        f"/api/ipr/{ipr_id}/certificacion-tecnica/solicitar",
        json={},
        headers=auth(jefe_token),
    )
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/certificacion-tecnica",
        json={"favorable": True},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 403
```

**Step 2: Run tests to verify they fail**

Run: `docker compose exec api pytest tests/test_c33_certification.py::test_get_certification_status_empty -v --tb=short`
Expected: FAIL (endpoint doesn't exist)

**Step 3: Implement the 3 endpoints**

Add to `api/app/routers/ipr.py` at the end of the file (before the final line), after the admissibility endpoints:

```python
# ---------------------------------------------------------------------------
# C33 Technical Certification
# ---------------------------------------------------------------------------

_CERT_REQUEST_ROLES = {"JEFE_DIVISION", "ADMIN_REGIONAL", "ADMIN_SISTEMA", "JEFE_DGI", "GOBERNADOR"}
_CERT_RESOLVE_ROLES = {"ADMIN_REGIONAL", "ADMIN_SISTEMA"}


@router.get("/{ipr_id}/certificacion-tecnica")
async def get_certification_status(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get C33 technical certification status for an IPR."""
    row = (await db.execute(text("""
        SELECT m.code AS mechanism_code,
               i.metadata->>'categoria_c33' AS categoria_c33,
               i.metadata->>'informe_tecnico_favorable' AS informe,
               i.metadata->>'cert_requested_at' AS requested_at,
               i.metadata->>'cert_requested_by_name' AS requested_by,
               i.metadata->>'cert_certifier_org' AS certifier_org,
               i.metadata->>'cert_resolved_at' AS resolved_at,
               i.metadata->>'cert_resolved_by_name' AS resolved_by,
               i.metadata->>'cert_document_reference' AS document_reference,
               i.metadata->>'cert_notes' AS notes
        FROM core.ipr i
        LEFT JOIN ref.category m ON m.id = i.mechanism_id
        WHERE i.id = CAST(:id AS uuid) AND i.deleted_at IS NULL
    """), {"id": str(ipr_id)})).mappings().first()

    if not row:
        raise HTTPException(404, "IPR no encontrado")
    if row["mechanism_code"] != "C33":
        raise HTTPException(409, "Este IPR no es del track C33")

    categoria = row["categoria_c33"]
    # Look up certifier from scheme if categoria assigned
    certifier = row["certifier_org"]
    if categoria and not certifier:
        cert_row = (await db.execute(text("""
            SELECT metadata->>'certifier_org_code' AS certifier
            FROM ref.category
            WHERE scheme = 'categoria_c33' AND code = :code AND deleted_at IS NULL
        """), {"code": categoria})).mappings().first()
        certifier = cert_row["certifier"] if cert_row else None

    informe_raw = row["informe"]
    informe_val = None
    if informe_raw is not None:
        informe_val = informe_raw == "true" or informe_raw is True

    return {
        "categoria_c33": categoria,
        "certifier_org": certifier,
        "requested": row["requested_at"] is not None,
        "requested_at": row["requested_at"],
        "requested_by": row["requested_by"],
        "resolved": informe_raw is not None,
        "informe_tecnico_favorable": informe_val,
        "resolved_at": row["resolved_at"],
        "resolved_by": row["resolved_by"],
        "document_reference": row["document_reference"],
        "notes": row["notes"],
    }


@router.post("/{ipr_id}/certificacion-tecnica/solicitar")
async def solicitar_certification(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Request C33 technical certification from SERVIU/MOP."""
    _require_roles(user, *_CERT_REQUEST_ROLES)

    row = (await db.execute(text("""
        SELECT m.code AS mechanism_code,
               i.metadata->>'categoria_c33' AS categoria_c33,
               i.metadata->>'cert_requested_at' AS already_requested,
               i.metadata->>'informe_tecnico_favorable' AS already_resolved
        FROM core.ipr i
        LEFT JOIN ref.category m ON m.id = i.mechanism_id
        WHERE i.id = CAST(:id AS uuid) AND i.deleted_at IS NULL
    """), {"id": str(ipr_id)})).mappings().first()

    if not row:
        raise HTTPException(404, "IPR no encontrado")
    if row["mechanism_code"] != "C33":
        raise HTTPException(409, "Este IPR no es del track C33")
    if not row["categoria_c33"]:
        raise HTTPException(409, "Asignar categoría C33 antes de solicitar certificación")
    if row["already_resolved"] is not None:
        raise HTTPException(409, "Certificación ya tiene resultado registrado")

    # Look up certifier org
    cert_row = (await db.execute(text("""
        SELECT metadata->>'certifier_org_code' AS certifier
        FROM ref.category
        WHERE scheme = 'categoria_c33' AND code = :code AND deleted_at IS NULL
    """), {"code": row["categoria_c33"]})).mappings().first()
    certifier = cert_row["certifier"] if cert_row else "Organismo"

    # Build person name
    person_row = (await db.execute(text("""
        SELECT p.names, p.paternal_surname
        FROM core."user" u JOIN core.person p ON p.id = u.person_id
        WHERE u.id = CAST(:uid AS uuid)
    """), {"uid": user["id"]})).mappings().first()
    requester_name = f"{person_row['names']} {person_row['paternal_surname']}" if person_row else "Unknown"

    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()

    await db.execute(text("""
        UPDATE core.ipr
        SET metadata = jsonb_set(
                jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            COALESCE(metadata, '{}'),
                            '{cert_requested_at}', CAST(:ts AS jsonb)
                        ),
                        '{cert_requested_by_id}', CAST(:uid AS jsonb)
                    ),
                    '{cert_requested_by_name}', CAST(:uname AS jsonb)
                ),
                '{cert_certifier_org}', CAST(:org AS jsonb)
            ),
            updated_at = NOW()
        WHERE id = CAST(:id AS uuid)
    """), {
        "id": str(ipr_id),
        "ts": json.dumps(now_iso),
        "uid": json.dumps(user["id"]),
        "uname": json.dumps(requester_name),
        "org": json.dumps(certifier),
    })
    await db.commit()

    return {
        "message": f"Certificación técnica solicitada a {certifier}",
        "certifier_org": certifier,
        "requested_at": now_iso,
        "requested_by": requester_name,
    }


@router.patch("/{ipr_id}/certificacion-tecnica")
async def resolver_certification(
    ipr_id: UUID,
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Register C33 technical certification result."""
    _require_roles(user, *_CERT_RESOLVE_ROLES)

    row = (await db.execute(text("""
        SELECT m.code AS mechanism_code,
               i.metadata->>'cert_requested_at' AS requested,
               i.metadata->>'informe_tecnico_favorable' AS already_resolved
        FROM core.ipr i
        LEFT JOIN ref.category m ON m.id = i.mechanism_id
        WHERE i.id = CAST(:id AS uuid) AND i.deleted_at IS NULL
    """), {"id": str(ipr_id)})).mappings().first()

    if not row:
        raise HTTPException(404, "IPR no encontrado")
    if row["mechanism_code"] != "C33":
        raise HTTPException(409, "Este IPR no es del track C33")
    if not row["requested"]:
        raise HTTPException(409, "No existe solicitud de certificación previa")
    if row["already_resolved"] is not None:
        raise HTTPException(409, "Certificación ya tiene resultado registrado")

    favorable = data.get("favorable")
    if favorable is None:
        raise HTTPException(422, "Campo 'favorable' es requerido (true/false)")

    # Build resolver name
    person_row = (await db.execute(text("""
        SELECT p.names, p.paternal_surname
        FROM core."user" u JOIN core.person p ON p.id = u.person_id
        WHERE u.id = CAST(:uid AS uuid)
    """), {"uid": user["id"]})).mappings().first()
    resolver_name = f"{person_row['names']} {person_row['paternal_surname']}" if person_row else "Unknown"

    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()

    doc_ref = data.get("document_reference", "")
    notes = data.get("notes", "")

    await db.execute(text("""
        UPDATE core.ipr
        SET metadata = jsonb_set(
                jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                COALESCE(metadata, '{}'),
                                '{informe_tecnico_favorable}', CAST(:favorable AS jsonb)
                            ),
                            '{cert_resolved_at}', CAST(:ts AS jsonb)
                        ),
                        '{cert_resolved_by_id}', CAST(:uid AS jsonb)
                    ),
                    '{cert_resolved_by_name}', CAST(:uname AS jsonb)
                ),
                '{cert_document_reference}', CAST(:doc AS jsonb)
            ),
            updated_at = NOW()
        WHERE id = CAST(:id AS uuid)
    """), {
        "id": str(ipr_id),
        "favorable": json.dumps(favorable),
        "ts": json.dumps(now_iso),
        "uid": json.dumps(user["id"]),
        "uname": json.dumps(resolver_name),
        "doc": json.dumps(doc_ref),
    })

    if notes:
        await db.execute(text("""
            UPDATE core.ipr
            SET metadata = jsonb_set(COALESCE(metadata, '{}'), '{cert_notes}', CAST(:notes AS jsonb))
            WHERE id = CAST(:id AS uuid)
        """), {"id": str(ipr_id), "notes": json.dumps(notes)})

    await db.commit()

    return {
        "message": "Resultado de certificación registrado",
        "informe_tecnico_favorable": favorable,
        "resolved_at": now_iso,
        "resolved_by": resolver_name,
        "document_reference": doc_ref,
    }
```

**Important:** Add `import json` at the top of `ipr.py` if not already present.

**Step 4: Run all tests**

Run: `docker compose exec api pytest tests/test_c33_certification.py -v --tb=short`
Expected: 11 PASS (4 gate + 7 endpoint tests)

**Step 5: Run full suite to check for regressions**

Run: `docker compose exec api pytest -v --tb=short | tail -5`
Expected: All pass, no regressions

**Step 6: Commit**

```bash
git add api/app/routers/ipr.py api/tests/test_c33_certification.py
git commit -m "feat(c33): 3 certification endpoints (GET/POST/PATCH) + 7 tests"
```

---

### Task 4: Frontend — Certification Section in Evaluation Tab

**Files:**
- Create: `web/src/app/(app)/ipr/components/c33-certification-section.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-evaluaciones.tsx` (import + render section)

**Step 1: Create the C33 certification section component**

Create `web/src/app/(app)/ipr/components/c33-certification-section.tsx`:

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/lib/auth";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { toast } from "sonner";

interface CertificationStatus {
  categoria_c33: string | null;
  certifier_org: string | null;
  requested: boolean;
  requested_at: string | null;
  requested_by: string | null;
  resolved: boolean;
  informe_tecnico_favorable: boolean | null;
  resolved_at: string | null;
  resolved_by: string | null;
  document_reference: string | null;
  notes: string | null;
}

const REQUEST_ROLES = ["JEFE_DIVISION", "ADMIN_REGIONAL", "ADMIN_SISTEMA", "JEFE_DGI", "GOBERNADOR"];
const RESOLVE_ROLES = ["ADMIN_REGIONAL", "ADMIN_SISTEMA"];

export function C33CertificationSection({ iprId }: { iprId: string }) {
  const { user } = useAuth();
  const [status, setStatus] = useState<CertificationStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [showResolveForm, setShowResolveForm] = useState(false);
  const [docRef, setDocRef] = useState("");
  const [notes, setNotes] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await api.get<CertificationStatus>(`/api/ipr/${iprId}/certificacion-tecnica`);
      setStatus(data);
    } catch {
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }, [iprId]);

  useEffect(() => { load(); }, [load]);

  if (loading) return <div className="text-sm text-muted-foreground">Cargando certificación...</div>;
  if (!status) return null;

  const canRequest = user && REQUEST_ROLES.includes(user.role_code);
  const canResolve = user && RESOLVE_ROLES.includes(user.role_code);

  const handleSolicitar = async () => {
    try {
      await api.post(`/api/ipr/${iprId}/certificacion-tecnica/solicitar`, {});
      toast.success("Certificación solicitada");
      load();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Error al solicitar");
    }
  };

  const handleResolver = async (favorable: boolean) => {
    try {
      await api.patch(`/api/ipr/${iprId}/certificacion-tecnica`, {
        favorable,
        document_reference: docRef,
        notes,
      });
      toast.success(favorable ? "Certificación favorable registrada" : "Certificación desfavorable registrada");
      setShowResolveForm(false);
      load();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Error al registrar resultado");
    }
  };

  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="font-medium">Certificación Técnica C33</h4>
        {status.resolved ? (
          status.informe_tecnico_favorable ? (
            <Badge variant="default" className="bg-green-600">Favorable</Badge>
          ) : (
            <Badge variant="destructive">Desfavorable</Badge>
          )
        ) : status.requested ? (
          <Badge variant="secondary">Solicitada a {status.certifier_org}</Badge>
        ) : (
          <Badge variant="outline">Sin solicitar</Badge>
        )}
      </div>

      {status.categoria_c33 && (
        <div className="text-sm text-muted-foreground">
          Categoría: <span className="font-medium">{status.categoria_c33}</span>
          {status.certifier_org && <> — Certificador: <span className="font-medium">{status.certifier_org}</span></>}
        </div>
      )}

      {status.requested && (
        <div className="text-sm">
          Solicitada por {status.requested_by} el {status.requested_at ? formatDateTime(status.requested_at) : "—"}
        </div>
      )}

      {status.resolved && (
        <div className="text-sm space-y-1">
          <div>Resuelta por {status.resolved_by} el {status.resolved_at ? formatDateTime(status.resolved_at) : "—"}</div>
          {status.document_reference && <div>Referencia: {status.document_reference}</div>}
          {status.notes && <div>Notas: {status.notes}</div>}
        </div>
      )}

      {!status.requested && !status.resolved && canRequest && status.categoria_c33 && (
        <Button size="sm" onClick={handleSolicitar}>
          Solicitar Certificación a {status.certifier_org}
        </Button>
      )}

      {status.requested && !status.resolved && canResolve && (
        <>
          {!showResolveForm ? (
            <Button size="sm" variant="outline" onClick={() => setShowResolveForm(true)}>
              Registrar Resultado
            </Button>
          ) : (
            <div className="space-y-2 border-t pt-2">
              <Input
                placeholder="Referencia documento (ej: ORD. N° 123/2026)"
                value={docRef}
                onChange={(e) => setDocRef(e.target.value)}
              />
              <Textarea
                placeholder="Notas (opcional)"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
              />
              <div className="flex gap-2">
                <Button size="sm" onClick={() => handleResolver(true)}>Favorable</Button>
                <Button size="sm" variant="destructive" onClick={() => handleResolver(false)}>Desfavorable</Button>
                <Button size="sm" variant="ghost" onClick={() => setShowResolveForm(false)}>Cancelar</Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
```

**Step 2: Integrate into evaluation tab**

Modify `web/src/app/(app)/ipr/components/tab-evaluaciones.tsx`:

At the top, add import:
```tsx
import { C33CertificationSection } from "./c33-certification-section";
```

In the component, accept `mechanismCode` prop. Inside the render, before the evaluations list, add:
```tsx
{mechanismCode === "C33" && <C33CertificationSection iprId={iprId} />}
```

The parent `ipr/[id]/page.tsx` must pass `mechanismCode` to the evaluation tab. Check if the IPR detail fetch already includes the mechanism code — if not, add it to the query.

**Step 3: Verify frontend builds**

Run: `cd web && npx next build`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add web/src/app/(app)/ipr/components/c33-certification-section.tsx web/src/app/(app)/ipr/components/tab-evaluaciones.tsx
git commit -m "feat(frontend): C33 certification section in evaluation tab"
```

---

### Task 5: CLAUDE.md + Docs Update

**Files:**
- Modify: `CLAUDE.md` (test counts, endpoint counts, gate count, C33 rule)
- Modify: `api/tests/conftest.py` (cleanup for C33 test IPRs)

**Step 1: Update conftest.py cleanup**

Add to the cleanup section in `conftest.py` (around line 73-83):

```python
# Clean up C33 certification test data
await session.execute(text("DELETE FROM core.ipr WHERE codigo_bip LIKE 'C33-%' AND deleted_at IS NULL"))
```

**Step 2: Update CLAUDE.md**

Updates needed:
- Testing section: update test count (+11 → 393 total) and add `test_c33_certification (11)` to module list
- Coverage section: update endpoint count (+3), gate function count (+1 = 22)
- Add note in Track enforcement section about C33 technical certification gate

**Step 3: Run full test suite**

Run: `docker compose exec api pytest -v --tb=short | tail -5`
Expected: All pass

**Step 4: Commit**

```bash
git add CLAUDE.md api/tests/conftest.py
git commit -m "docs(CLAUDE.md): add C33 certification coverage — 22 gates, ~169 endpoints"
```
