# TP-06 + HΩ-14 SISREC 8-Phase CGR Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the formal CGR Res. 30 rendition cycle with 8-phase parametric table, external phase metadata, archived_at, escalation tracking with alert generation, and enhanced ciclo endpoint. Closes HΩ-14 → 15/15 (100%).

**Architecture:** TP-06 seed-only parametric table (`core.rendition_phase`, 8 rows). External phases 1-3 tracked as JSONB metadata timestamps (not formal states). Phase 8 uses `archived_at` timestamp (APROBADA remains terminal). Escalation via `core.rendition_escalation` table + auto-generated `core.alert` entries. No automated reassignment.

**Tech Stack:** FastAPI + SQLAlchemy raw SQL, Pydantic v2, PostgreSQL, pytest + httpx async tests.

---

## Context

**Design document:** `docs/plans/2026-03-08-sisrec-8phase-design.md`

**Current state machine (6 states, 7 transitions — NOT changing):**
```python
_RENDICION_TRANSITIONS = {
    "PENDIENTE":       {"EN_REVISION_RTF"},
    "EN_REVISION_RTF": {"OBSERVADA", "VISADA_RTF"},
    "VISADA_RTF":      {"EN_REVISION_UCR"},
    "EN_REVISION_UCR": {"OBSERVADA", "APROBADA", "RECHAZADA"},
    "OBSERVADA":       {"EN_REVISION_RTF"},
}
```

**State → TP-06 phase mapping:**
| State | Phase ordinal | Phase code |
|-------|:---:|------------|
| (external) | 1 | PREPARACION_EJECUTOR |
| (external) | 2 | CERTIFICACION |
| (external) | 3 | FIRMA_ENCARGADO |
| PENDIENTE | 4 | RECEPCION_GORE |
| EN_REVISION_RTF | 5 | REVISION_RTF |
| VISADA_RTF/EN_REVISION_UCR | 6-7 | APROBACION_DAF / CONTABILIZACION_UCR |
| APROBADA + archived_at | 8 | ARCHIVO_CIERRE |

**Key files:**
- Router: `api/app/routers/dgi_data.py` (state machine at L1014-1046, ciclo at L811-903, PATCH at L1069-1170)
- Schemas: `api/app/schemas/dgi.py` (Rendicion* at L241-308)
- Tests: `api/tests/test_sisrec.py` (18 tests, helpers: `_age_rendicion`, `_create_rendicion`, `_transition`, `_get_state_id`)
- Migration pattern: `model/model_goreos/sql/goreos_migration_*.sql` (self-register in `core.schema_migration`)
- Conftest: `api/tests/conftest.py` (cleanup in `cleanup_test_artifacts`, fixtures: admin_token, dgi_token, etc.)

**Critical traps (from memory):**
- `CurrentUser` is `Annotated[dict, Depends()]` — use inline `_require_roles(user, ...)`, NOT `Depends(require_roles(...))` as default
- Python param ordering: `user: CurrentUser` (no default) BEFORE params with defaults like `Query(...)`
- Route ordering: specific routes (`/rendiciones/vencidas`, `/rendiciones/fases`) BEFORE `/{rendicion_id}`
- `COALESCE(r.phase_entered_at, r.updated_at)` — defensive fallback for pre-migration data
- After adding new Python files: `docker compose restart api`
- `asyncpg` type cast: use `CAST(:param AS jsonb)`, NOT `::jsonb`

---

### Task 1: DDL Migration — TP-06 Table + archived_at + Escalation Table

**Files:**
- Create: `model/model_goreos/sql/goreos_migration_sisrec_8phase.sql`
- Create: `model/model_goreos/sql/goreos_rollback_sisrec_8phase.sql`

**Step 1: Write the migration SQL**

Create `model/model_goreos/sql/goreos_migration_sisrec_8phase.sql`:

```sql
-- TP-06 + HΩ-14: 8-Phase CGR rendition cycle
-- Creates: core.rendition_phase (8 seed rows), core.rendition_escalation
-- Alters: core.rendition (adds archived_at)
BEGIN;

-- T1: Parametric table TP-06 — 8 CGR rendition phases (seed-only, immutable)
CREATE TABLE IF NOT EXISTS core.rendition_phase (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordinal    INT NOT NULL UNIQUE CHECK (ordinal BETWEEN 1 AND 8),
    code       VARCHAR(32) NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    responsible_role TEXT NOT NULL,
    sla_days   INT NOT NULL,
    escalation_action TEXT,
    is_internal BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- T2: Seed 8 phases
INSERT INTO core.rendition_phase (ordinal, code, name, responsible_role, sla_days, escalation_action, is_internal)
VALUES
    (1, 'PREPARACION_EJECUTOR', 'Preparación Ejecutor',           'EJECUTOR',               15, 'Notificar ejecutor',         false),
    (2, 'CERTIFICACION',        'Certificación',                   'EJECUTOR',                3, 'Notificar ejecutor',         false),
    (3, 'FIRMA_ENCARGADO',      'Firma Encargado',                 'ENCARGADO_RENDICION',     1, 'Notificar encargado',        false),
    (4, 'RECEPCION_GORE',       'Recepción GORE',                  'OFICINA_PARTES',          2, 'Notificar Of. Partes',       true),
    (5, 'REVISION_RTF',         'Revisión RTF',                    'RTF',                     7, 'Escalar a Jefe RTF',         true),
    (6, 'APROBACION_DAF',       'Aprobación DAF',                  'DAF',                     1, 'Escalar a Jefe DAF',         true),
    (7, 'CONTABILIZACION_UCR',  'Contabilización UCR',             'UCR',                     2, 'Escalar a Jefe UCR',         true),
    (8, 'ARCHIVO_CIERRE',       'Archivo y Cierre',                'ARCHIVO',                 1, 'Notificar responsable',      true)
ON CONFLICT (ordinal) DO NOTHING;

-- T3: archived_at on rendition (phase 8 — not a new state)
ALTER TABLE core.rendition ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ;

-- T4: Escalation tracking table
CREATE TABLE IF NOT EXISTS core.rendition_escalation (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rendition_id     UUID NOT NULL REFERENCES core.rendition(id),
    phase_id         UUID NOT NULL REFERENCES core.rendition_phase(id),
    escalation_level INT NOT NULL CHECK (escalation_level BETWEEN 1 AND 3),
    detected_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    alert_id         UUID REFERENCES core.alert(id),
    resolved_at      TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- T5: Index for rendition escalation lookups
CREATE INDEX IF NOT EXISTS idx_rendition_escalation_rendition
    ON core.rendition_escalation(rendition_id);

-- T6: Index for archived_at queries
CREATE INDEX IF NOT EXISTS idx_rendition_archived
    ON core.rendition(archived_at)
    WHERE archived_at IS NOT NULL AND deleted_at IS NULL;

-- T7: Self-register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_sisrec_8phase.sql', 'manual', 'sisrec_8phase_self_register')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
```

**Step 2: Write the rollback SQL**

Create `model/model_goreos/sql/goreos_rollback_sisrec_8phase.sql`:

```sql
BEGIN;
DROP INDEX IF EXISTS core.idx_rendition_escalation_rendition;
DROP INDEX IF EXISTS core.idx_rendition_archived;
DROP TABLE IF EXISTS core.rendition_escalation;
ALTER TABLE core.rendition DROP COLUMN IF EXISTS archived_at;
DROP TABLE IF EXISTS core.rendition_phase;
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_sisrec_8phase.sql';
COMMIT;
```

**Step 3: Apply migration to both databases**

Run:
```bash
./scripts/run_migrations.sh goreos_db goreos_model
./scripts/run_migrations.sh goreos_db goreos_test
```
Expected: `APPLY goreos_migration_sisrec_8phase.sql ...`

**Step 4: Verify migration**

Run:
```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT ordinal, code, sla_days, is_internal FROM core.rendition_phase ORDER BY ordinal;"
docker exec goreos_db psql -U goreos -d goreos_model -c "\d core.rendition_escalation"
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT column_name FROM information_schema.columns WHERE table_schema='core' AND table_name='rendition' AND column_name='archived_at';"
```
Expected: 8 rows in rendition_phase, escalation table exists, archived_at column exists.

**Step 5: Commit**

```bash
git add model/model_goreos/sql/goreos_migration_sisrec_8phase.sql model/model_goreos/sql/goreos_rollback_sisrec_8phase.sql
git commit -m "feat(sisrec-8phase): DDL migration — TP-06 table + archived_at + escalation"
```

---

### Task 2: Pydantic Schemas

**Files:**
- Modify: `api/app/schemas/dgi.py` (add after line ~308)

**Step 1: Add new schema classes**

Add after `RendicionPhaseEntry` class (around line 308) in `api/app/schemas/dgi.py`:

```python
class RenditionPhaseDefinition(BaseModel):
    """TP-06 parametric phase definition."""
    id: UUID
    ordinal: int
    code: str
    name: str
    responsible_role: str
    sla_days: int
    escalation_action: str | None = None
    is_internal: bool


class EscalationItem(BaseModel):
    """Rendition escalation record."""
    id: UUID
    rendition_id: UUID
    phase_id: UUID
    phase_code: str | None = None
    phase_name: str | None = None
    escalation_level: int
    detected_at: datetime
    alert_id: UUID | None = None
    resolved_at: datetime | None = None


class EscalationCheckResult(BaseModel):
    """Result of check-escalations batch operation."""
    checked: int
    new_escalations: int
    details: list[dict] = []


class CicloPhaseStatus(BaseModel):
    """Enhanced ciclo phase with TP-06 definition link."""
    ordinal: int
    code: str
    name: str
    responsible_role: str
    sla_days: int
    status: str  # completada | en_curso | pendiente | no_aplica
    entered_at: datetime | None = None
    exited_at: datetime | None = None
    duration_days: float | None = None
    is_overdue: bool = False
```

**Step 2: Update the imports at top of dgi.py if needed**

No new imports needed — `UUID`, `datetime`, `BaseModel` already imported.

**Step 3: Commit**

```bash
git add api/app/schemas/dgi.py
git commit -m "feat(sisrec-8phase): Pydantic schemas — phase definitions, escalation, enhanced ciclo"
```

---

### Task 3: New API Endpoints (4 endpoints)

**Files:**
- Modify: `api/app/routers/dgi_data.py`

**Step 1: Add schema imports**

At the top of `dgi_data.py`, update the import from `app.schemas.dgi` to include the new schemas:

```python
from app.schemas.dgi import (
    IndicatorItem, DataSourceItem,
    OrganizacionItem, PersonaItem, TerritorioItem, EventoItem,
    RendicionItem, RendicionDetail, RendicionCreate, RendicionUpdate,
    RendicionHistoryEntry, RendicionPhaseEntry,
    RenditionPhaseDefinition, EscalationItem, EscalationCheckResult,
    CicloPhaseStatus,
)
```

**Step 2: Add GET /rendiciones/fases endpoint**

Add this BEFORE the `/rendiciones/vencidas` endpoint (around line 740), to ensure route ordering:

```python
# ---------------------------------------------------------------------------
# GET /api/dgi/data/rendiciones/fases — TP-06 phase definitions
# ---------------------------------------------------------------------------

@router.get("/rendiciones/fases")
async def list_rendition_phases(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all 8 CGR rendition phase definitions (TP-06 parametric table)."""
    rows = (await db.execute(
        text("""
            SELECT id, ordinal, code, name, responsible_role,
                   sla_days, escalation_action, is_internal
            FROM core.rendition_phase
            ORDER BY ordinal
        """)
    )).mappings().all()
    return [RenditionPhaseDefinition(**dict(r)) for r in rows]
```

**Step 3: Add PATCH /rendiciones/{id}/archivar endpoint**

Add AFTER the existing GET `/rendiciones/{rendicion_id}` detail endpoint (after line ~970):

```python
# ---------------------------------------------------------------------------
# PATCH /api/dgi/data/rendiciones/{rendicion_id}/archivar
# ---------------------------------------------------------------------------

@router.patch("/rendiciones/{rendicion_id}/archivar")
async def archive_rendicion(
    rendicion_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Set archived_at on an APROBADA rendition (phase 8 closure)."""
    from app.core.security import DGI_ROLES as _DGI
    if user["role_code"] not in _DGI and user["role_code"] not in WRITE_OPERATIONAL_ROLES:
        raise HTTPException(status_code=403, detail="Rol sin permiso para archivar")

    row = (await db.execute(
        text("""
            SELECT r.id, r.archived_at, st.code AS state_code
            FROM core.rendition r
            LEFT JOIN ref.category st ON st.id = r.state_id
            WHERE r.id = :id AND r.deleted_at IS NULL
        """),
        {"id": str(rendicion_id)},
    )).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")
    if row["state_code"] != "APROBADA":
        raise HTTPException(status_code=409, detail="Solo rendiciones APROBADA pueden archivarse")
    if row["archived_at"]:
        raise HTTPException(status_code=409, detail="Rendición ya archivada")

    await db.execute(
        text("UPDATE core.rendition SET archived_at = NOW() WHERE id = :id"),
        {"id": str(rendicion_id)},
    )
    await db.commit()
    return {"archived": True, "rendicion_id": str(rendicion_id)}
```

**Step 4: Add GET /rendiciones/{id}/escalamientos endpoint**

Add after the archivar endpoint:

```python
# ---------------------------------------------------------------------------
# GET /api/dgi/data/rendiciones/{rendicion_id}/escalamientos
# ---------------------------------------------------------------------------

@router.get("/rendiciones/{rendicion_id}/escalamientos")
async def list_rendicion_escalations(
    rendicion_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List escalation records for a rendition."""
    # Verify rendition exists
    exists = (await db.execute(
        text("SELECT 1 FROM core.rendition WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(rendicion_id)},
    )).scalar()
    if not exists:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")

    rows = (await db.execute(
        text("""
            SELECT e.id, e.rendition_id, e.phase_id, e.escalation_level,
                   e.detected_at, e.alert_id, e.resolved_at,
                   rp.code AS phase_code, rp.name AS phase_name
            FROM core.rendition_escalation e
            JOIN core.rendition_phase rp ON rp.id = e.phase_id
            WHERE e.rendition_id = :rid
            ORDER BY e.detected_at DESC
        """),
        {"rid": str(rendicion_id)},
    )).mappings().all()
    return [EscalationItem(**dict(r)) for r in rows]
```

**Step 5: Add POST /rendiciones/check-escalations endpoint**

Add BEFORE the `/rendiciones/vencidas` endpoint (near `/rendiciones/fases`), to keep specific routes before `{rendicion_id}`:

```python
# ---------------------------------------------------------------------------
# POST /api/dgi/data/rendiciones/check-escalations — Batch detect overdue
# ---------------------------------------------------------------------------

_STATE_TO_PHASE_CODE: dict[str, str] = {
    "EN_REVISION_RTF": "REVISION_RTF",
    "VISADA_RTF": "APROBACION_DAF",
    "EN_REVISION_UCR": "CONTABILIZACION_UCR",
}

_ESCALATION_MULTIPLIERS = {1: 1.0, 2: 1.5, 3: 2.0}


@router.post("/rendiciones/check-escalations")
async def check_escalations(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Detect overdue renditions and create escalation + alert entries."""
    if user["role_code"] not in _RENDICION_WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Rol sin permiso")

    # Find renditions in reviewable states with time elapsed
    rows = (await db.execute(
        text("""
            SELECT r.id, st.code AS state_code,
                   EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 AS days_in_state,
                   a.agreement_number, ipr.codigo_bip
            FROM core.rendition r
            LEFT JOIN ref.category st ON st.id = r.state_id
            LEFT JOIN core.agreement a ON a.id = r.agreement_id
            LEFT JOIN core.ipr ipr ON ipr.id = r.ipr_id
            WHERE r.deleted_at IS NULL
              AND st.code IN ('EN_REVISION_RTF', 'VISADA_RTF', 'EN_REVISION_UCR')
        """)
    )).mappings().all()

    # Get phase IDs by code
    phase_rows = (await db.execute(
        text("SELECT id, code, sla_days FROM core.rendition_phase")
    )).mappings().all()
    phase_map = {p["code"]: {"id": str(p["id"]), "sla_days": p["sla_days"]} for p in phase_rows}

    # Get alert severity ID (ALTO)
    severity_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_severity' AND code = 'ALTO'")
    )).scalar()

    checked = 0
    new_escalations = 0
    details = []

    for r in rows:
        checked += 1
        phase_code = _STATE_TO_PHASE_CODE.get(r["state_code"])
        if not phase_code or phase_code not in phase_map:
            continue

        phase_info = phase_map[phase_code]
        sla = phase_info["sla_days"]
        days = float(r["days_in_state"])

        for level, multiplier in _ESCALATION_MULTIPLIERS.items():
            threshold = sla * multiplier
            if days <= threshold:
                continue

            # Check if escalation already exists at this level
            existing = (await db.execute(
                text("""
                    SELECT 1 FROM core.rendition_escalation
                    WHERE rendition_id = :rid AND phase_id = :pid
                      AND escalation_level = :level AND resolved_at IS NULL
                """),
                {"rid": str(r["id"]), "pid": phase_info["id"], "level": level},
            )).scalar()

            if existing:
                continue

            # Create alert
            alert_id = None
            if severity_id:
                alert_row = (await db.execute(
                    text("""
                        INSERT INTO core.alert (
                            title, description, severity_id, subject_type, subject_id,
                            created_at, updated_at
                        ) VALUES (
                            :title, :desc, :sev, 'core.rendition', :sid,
                            NOW(), NOW()
                        ) RETURNING id
                    """),
                    {
                        "title": f"Escalamiento N{level}: rendición vencida en {phase_code}",
                        "desc": f"Rendición {r.get('agreement_number') or str(r['id'])[:8]} "
                                f"lleva {round(days, 1)}d en {r['state_code']} (SLA: {sla}d, "
                                f"umbral N{level}: {threshold}d)",
                        "sev": str(severity_id),
                        "sid": str(r["id"]),
                    },
                )).mappings().first()
                if alert_row:
                    alert_id = str(alert_row["id"])

            # Create escalation
            await db.execute(
                text("""
                    INSERT INTO core.rendition_escalation (
                        rendition_id, phase_id, escalation_level, alert_id
                    ) VALUES (:rid, :pid, :level, :aid)
                """),
                {
                    "rid": str(r["id"]),
                    "pid": phase_info["id"],
                    "level": level,
                    "aid": alert_id,
                },
            )
            new_escalations += 1
            details.append({
                "rendition_id": str(r["id"]),
                "phase_code": phase_code,
                "level": level,
                "days_in_state": round(days, 1),
                "threshold": threshold,
            })

    await db.commit()
    return EscalationCheckResult(checked=checked, new_escalations=new_escalations, details=details)
```

**Step 6: Commit**

```bash
git add api/app/routers/dgi_data.py
git commit -m "feat(sisrec-8phase): 4 new endpoints — fases, archivar, escalamientos, check-escalations"
```

---

### Task 4: Enhanced Ciclo Endpoint

**Files:**
- Modify: `api/app/routers/dgi_data.py` (replace existing ciclo endpoint at lines 811-903)

**Step 1: Replace the ciclo endpoint with enhanced version**

Replace the existing `get_rendicion_ciclo` function (lines 814-903) with the enhanced version that maps TP-06 phases:

```python
@router.get("/rendiciones/{rendicion_id}/ciclo")
async def get_rendicion_ciclo(
    rendicion_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db),
):
    """Enhanced phase-by-phase cycle view with TP-06 phase definitions.

    Maps state history to 8 CGR phases. Internal phases (4-7) derive from
    rendition_history. External phases (1-3) from metadata timestamps.
    Phase 8 from archived_at.
    """
    row = (await db.execute(
        text("""
            SELECT r.id, r.created_at, r.archived_at, r.metadata,
                   st.code AS state_code
            FROM core.rendition r
            LEFT JOIN ref.category st ON st.id = r.state_id
            WHERE r.id = :id AND r.deleted_at IS NULL
        """),
        {"id": str(rendicion_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")

    # Load TP-06 phase definitions
    phase_defs = (await db.execute(
        text("SELECT id, ordinal, code, name, responsible_role, sla_days FROM core.rendition_phase ORDER BY ordinal")
    )).mappings().all()
    phase_by_code = {p["code"]: dict(p) for p in phase_defs}

    # Load state history
    history_rows = (await db.execute(
        text("""
            SELECT h.changed_at,
                   new_cat.code  AS new_state,
                   new_cat.label AS new_state_label
            FROM core.rendition_history h
            JOIN ref.category new_cat ON h.new_state_id = new_cat.id
            WHERE h.rendition_id = :rid
            ORDER BY h.changed_at ASC
        """),
        {"rid": str(rendicion_id)},
    )).mappings().all()

    now = datetime.now(timezone.utc)
    metadata = row["metadata"] or {}
    current_state = row["state_code"]

    # Map state → TP-06 phase code
    state_to_phase = {
        "PENDIENTE": "RECEPCION_GORE",
        "EN_REVISION_RTF": "REVISION_RTF",
        "VISADA_RTF": "APROBACION_DAF",
        "EN_REVISION_UCR": "CONTABILIZACION_UCR",
    }

    # Build phase status list (all 8 phases)
    phases: list[dict] = []

    # --- External phases (1-3): from metadata timestamps ---
    external_keys = [
        ("PREPARACION_EJECUTOR", "fase1_preparacion_at"),
        ("CERTIFICACION", "fase2_certificacion_at"),
        ("FIRMA_ENCARGADO", "fase3_firma_at"),
    ]
    for phase_code, meta_key in external_keys:
        pdef = phase_by_code.get(phase_code, {})
        ts_str = metadata.get(meta_key)
        if ts_str:
            status = "completada"
            entered = datetime.fromisoformat(ts_str) if isinstance(ts_str, str) else ts_str
            phases.append(CicloPhaseStatus(
                ordinal=pdef.get("ordinal", 0), code=phase_code, name=pdef.get("name", ""),
                responsible_role=pdef.get("responsible_role", ""), sla_days=pdef.get("sla_days", 0),
                status=status, entered_at=entered, duration_days=None, is_overdue=False,
            ).model_dump())
        else:
            # If rendition exists (submitted), external phases are implicitly completed
            # unless metadata is empty (legacy data)
            phases.append(CicloPhaseStatus(
                ordinal=pdef.get("ordinal", 0), code=phase_code, name=pdef.get("name", ""),
                responsible_role=pdef.get("responsible_role", ""), sla_days=pdef.get("sla_days", 0),
                status="no_aplica",
            ).model_dump())

    # --- Internal phases (4-7): from state history ---
    # Build a timeline of state entries
    state_entries: list[dict] = []
    if history_rows:
        # Phase 4 (RECEPCION_GORE): from created_at to first transition
        first_ts = history_rows[0]["changed_at"]
        state_entries.append({
            "state": "PENDIENTE", "entered": row["created_at"], "exited": first_ts,
        })
        for i, h in enumerate(history_rows):
            exited = history_rows[i + 1]["changed_at"] if i + 1 < len(history_rows) else None
            state_entries.append({
                "state": h["new_state"], "entered": h["changed_at"], "exited": exited,
            })
    else:
        state_entries.append({
            "state": "PENDIENTE", "entered": row["created_at"], "exited": None,
        })

    # Aggregate state entries into TP-06 phases (take first entry and last exit per phase)
    internal_phase_codes = ["RECEPCION_GORE", "REVISION_RTF", "APROBACION_DAF", "CONTABILIZACION_UCR"]
    for phase_code in internal_phase_codes:
        pdef = phase_by_code.get(phase_code, {})
        # Find matching state entries
        matching_states = [s for s in state_entries if state_to_phase.get(s["state"]) == phase_code]

        if matching_states:
            entered = matching_states[0]["entered"]
            last = matching_states[-1]
            exited = last["exited"]
            if exited:
                dur = (exited - entered).total_seconds() / 86400.0
                status = "completada"
            else:
                dur = (now - entered).total_seconds() / 86400.0
                status = "en_curso"
            sla = pdef.get("sla_days", 0)
            phases.append(CicloPhaseStatus(
                ordinal=pdef.get("ordinal", 0), code=phase_code, name=pdef.get("name", ""),
                responsible_role=pdef.get("responsible_role", ""), sla_days=sla,
                status=status, entered_at=entered, exited_at=exited,
                duration_days=round(dur, 1),
                is_overdue=sla > 0 and dur > sla,
            ).model_dump())
        else:
            # Phase not yet reached
            # Check if current state is past this phase
            current_phase_code = state_to_phase.get(current_state)
            current_ordinal = phase_by_code.get(current_phase_code, {}).get("ordinal", 0) if current_phase_code else 99
            phase_ordinal = pdef.get("ordinal", 0)
            if current_state in ("APROBADA", "RECHAZADA"):
                # Terminal state — all preceding phases are completed (no history available = skip)
                status = "completada" if phase_ordinal <= 7 else "pendiente"
            elif current_ordinal > phase_ordinal:
                status = "completada"
            else:
                status = "pendiente"
            phases.append(CicloPhaseStatus(
                ordinal=pdef.get("ordinal", 0), code=phase_code, name=pdef.get("name", ""),
                responsible_role=pdef.get("responsible_role", ""), sla_days=pdef.get("sla_days", 0),
                status=status,
            ).model_dump())

    # --- Phase 8 (ARCHIVO_CIERRE): from archived_at ---
    pdef8 = phase_by_code.get("ARCHIVO_CIERRE", {})
    if row["archived_at"]:
        phases.append(CicloPhaseStatus(
            ordinal=8, code="ARCHIVO_CIERRE", name=pdef8.get("name", "Archivo y Cierre"),
            responsible_role=pdef8.get("responsible_role", "ARCHIVO"), sla_days=pdef8.get("sla_days", 1),
            status="completada", entered_at=row["archived_at"],
        ).model_dump())
    elif current_state == "APROBADA":
        phases.append(CicloPhaseStatus(
            ordinal=8, code="ARCHIVO_CIERRE", name=pdef8.get("name", "Archivo y Cierre"),
            responsible_role=pdef8.get("responsible_role", "ARCHIVO"), sla_days=pdef8.get("sla_days", 1),
            status="en_curso",
        ).model_dump())
    else:
        phases.append(CicloPhaseStatus(
            ordinal=8, code="ARCHIVO_CIERRE", name=pdef8.get("name", "Archivo y Cierre"),
            responsible_role=pdef8.get("responsible_role", "ARCHIVO"), sla_days=pdef8.get("sla_days", 1),
            status="pendiente",
        ).model_dump())

    # Sort by ordinal
    phases.sort(key=lambda p: p["ordinal"])

    total_elapsed = (now - row["created_at"]).total_seconds() / 86400.0
    overdue_count = sum(1 for p in phases if p.get("is_overdue"))

    return {
        "rendicion_id": rendicion_id,
        "current_state": current_state,
        "total_elapsed_days": round(total_elapsed, 1),
        "cycle_target_days": _RENDICION_CYCLE_TARGET_DAYS,
        "cycle_overdue": total_elapsed > _RENDICION_CYCLE_TARGET_DAYS,
        "archived_at": row["archived_at"],
        "phases": phases,
        "overdue_count": overdue_count,
    }
```

**Step 2: Commit**

```bash
git add api/app/routers/dgi_data.py
git commit -m "feat(sisrec-8phase): enhanced ciclo endpoint with TP-06 phase mapping"
```

---

### Task 5: PATCH rendiciones — add metadata update support

**Files:**
- Modify: `api/app/routers/dgi_data.py` (RENDICION_UPDATABLE + PATCH endpoint)
- Modify: `api/app/schemas/dgi.py` (RendicionUpdate)

**Step 1: Add metadata field to RendicionUpdate schema**

In `api/app/schemas/dgi.py`, add `metadata` to `RendicionUpdate`:

```python
class RendicionUpdate(BaseModel):
    state_id: UUID | None = None
    responsible_id: UUID | None = None
    period_start: date | None = None
    period_end: date | None = None
    submitted_at: datetime | None = None
    amount: float | None = None
    comment: str | None = None
    metadata: dict | None = None  # External phase timestamps
```

**Step 2: Add metadata to RENDICION_UPDATABLE in dgi_data.py**

Change line ~1043:

```python
RENDICION_UPDATABLE = {"state_id", "responsible_id", "period_start", "period_end", "submitted_at", "amount", "metadata"}
```

**Step 3: Handle metadata serialization in PATCH endpoint**

In the PATCH endpoint, the `for col, val in updates.items()` loop needs to handle metadata as JSONB. Add a special case before the generic loop (around line 1147):

```python
    # Handle metadata as JSONB
    metadata_val = updates.pop("metadata", None)
    if metadata_val is not None:
        import json
        set_parts.append("metadata = CAST(:v_metadata AS jsonb)")
        params["v_metadata"] = json.dumps(metadata_val)

    for col, val in updates.items():
        # ... existing loop ...
```

**Step 4: Commit**

```bash
git add api/app/schemas/dgi.py api/app/routers/dgi_data.py
git commit -m "feat(sisrec-8phase): metadata update support for external phase timestamps"
```

---

### Task 6: Integration Tests (12 tests)

**Files:**
- Create: `api/tests/test_sisrec_8phase.py`
- Modify: `api/tests/conftest.py` (cleanup)

**Step 1: Write the test file**

Create `api/tests/test_sisrec_8phase.py`:

```python
"""Tests para SISREC 8-Phase CGR (TP-06 + HΩ-14).

Covers:
- TP-06 phase definitions endpoint (8 rows)
- Archive endpoint (phase 8)
- Escalation check + listing
- Enhanced ciclo with phase mapping
- Metadata external phase timestamps
"""
import uuid
import pytest
from sqlalchemy import text
from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helpers (reuse patterns from test_sisrec.py)
# ---------------------------------------------------------------------------

async def _ensure_ipr(db) -> str:
    """Get or create a test IPR."""
    r = await db.execute(text("SELECT id FROM core.ipr LIMIT 1"))
    row = r.scalar()
    if row:
        return str(row)
    code = f"T-8PH-{uuid.uuid4().hex[:8].upper()}"
    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (codigo_bip, name, ipr_nature, created_at, updated_at)
            VALUES (:code, 'Test IPR 8Phase', 'PROYECTO', NOW(), NOW())
            RETURNING id
        """),
        {"code": code},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def _get_state_id(db, code: str) -> str:
    r = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = :code"),
        {"code": code},
    )
    return str(r.scalar())


async def _create_rendicion(client, token, db, amount=None, metadata=None) -> str:
    """Create a rendicion in PENDIENTE and return its ID."""
    ipr_id = await _ensure_ipr(db)
    payload = {"ipr_id": ipr_id}
    if amount is not None:
        payload["amount"] = amount
    resp = await client.post("/api/dgi/data/rendiciones", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    rid = resp.json()["id"]
    if metadata:
        import json
        await db.execute(
            text("UPDATE core.rendition SET metadata = CAST(:m AS jsonb) WHERE id = :id"),
            {"m": json.dumps(metadata), "id": rid},
        )
        await db.commit()
    return rid


async def _transition(client, token, rid: str, target_code: str, db) -> int:
    state_id = await _get_state_id(db, target_code)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}",
        json={"state_id": state_id},
        headers=auth(token),
    )
    return resp.status_code


async def _age_rendicion(db, rid: str, interval: str) -> None:
    """Age a rendicion's phase_entered_at and updated_at."""
    await db.execute(text("ALTER TABLE core.rendition DISABLE TRIGGER trg_rendition_updated_at"))
    await db.execute(
        text(f"UPDATE core.rendition SET updated_at = NOW() - INTERVAL '{interval}', "
             f"phase_entered_at = NOW() - INTERVAL '{interval}' WHERE id = :id"),
        {"id": rid},
    )
    await db.execute(text("ALTER TABLE core.rendition ENABLE TRIGGER trg_rendition_updated_at"))
    await db.commit()


async def _drive_to_aprobada(client, token, rid, db):
    """Drive rendition through full happy path to APROBADA."""
    await _transition(client, token, rid, "EN_REVISION_RTF", db)
    await _transition(client, token, rid, "VISADA_RTF", db)
    await _transition(client, token, rid, "EN_REVISION_UCR", db)
    status = await _transition(client, token, rid, "APROBADA", db)
    assert status == 200


# ---------------------------------------------------------------------------
# Test 1: GET /rendiciones/fases — TP-06 parametric table
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_phases_returns_8(client, dgi_token):
    """TP-06 endpoint returns exactly 8 phase definitions."""
    resp = await client.get("/api/dgi/data/rendiciones/fases", headers=auth(dgi_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 8
    assert data[0]["ordinal"] == 1
    assert data[0]["code"] == "PREPARACION_EJECUTOR"
    assert data[7]["ordinal"] == 8
    assert data[7]["code"] == "ARCHIVO_CIERRE"
    # External phases not internal
    assert data[0]["is_internal"] is False
    assert data[4]["is_internal"] is True


# ---------------------------------------------------------------------------
# Test 2-4: PATCH /rendiciones/{id}/archivar
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_archive_aprobada(client, dgi_token, db):
    """Archive sets archived_at on APROBADA rendition."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _drive_to_aprobada(client, dgi_token, rid, db)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}/archivar", headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["archived"] is True


@pytest.mark.asyncio
async def test_archive_non_aprobada_409(client, dgi_token, db):
    """Cannot archive a rendition that is not APROBADA."""
    rid = await _create_rendicion(client, dgi_token, db)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}/archivar", headers=auth(dgi_token),
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_archive_twice_409(client, dgi_token, db):
    """Cannot archive a rendition that is already archived."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _drive_to_aprobada(client, dgi_token, rid, db)
    resp1 = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}/archivar", headers=auth(dgi_token),
    )
    assert resp1.status_code == 200
    resp2 = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}/archivar", headers=auth(dgi_token),
    )
    assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# Test 5-7: Escalation check + listing
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_check_escalations_creates_level1(client, dgi_token, db):
    """Aging a rendition past SLA creates a level 1 escalation."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    # Age past 7d SLA
    await _age_rendicion(db, rid, "8 days")
    resp = await client.post(
        "/api/dgi/data/rendiciones/check-escalations", headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_escalations"] >= 1


@pytest.mark.asyncio
async def test_check_escalations_idempotent(client, dgi_token, db):
    """Running check-escalations twice does not create duplicates."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _age_rendicion(db, rid, "8 days")
    resp1 = await client.post(
        "/api/dgi/data/rendiciones/check-escalations", headers=auth(dgi_token),
    )
    n1 = resp1.json()["new_escalations"]
    resp2 = await client.post(
        "/api/dgi/data/rendiciones/check-escalations", headers=auth(dgi_token),
    )
    n2 = resp2.json()["new_escalations"]
    assert n2 < n1  # Second run creates fewer (or zero) new escalations


@pytest.mark.asyncio
async def test_list_escalations(client, dgi_token, db):
    """GET escalamientos returns escalation records with phase info."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _age_rendicion(db, rid, "8 days")
    await client.post(
        "/api/dgi/data/rendiciones/check-escalations", headers=auth(dgi_token),
    )
    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rid}/escalamientos", headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["phase_code"] == "REVISION_RTF"
    assert data[0]["escalation_level"] == 1


# ---------------------------------------------------------------------------
# Test 8-10: Enhanced ciclo endpoint
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ciclo_returns_8_phases(client, dgi_token, db):
    """Enhanced ciclo returns all 8 TP-06 phases."""
    rid = await _create_rendicion(client, dgi_token, db)
    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rid}/ciclo", headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["phases"]) == 8
    assert data["phases"][0]["code"] == "PREPARACION_EJECUTOR"
    assert data["phases"][7]["code"] == "ARCHIVO_CIERRE"


@pytest.mark.asyncio
async def test_ciclo_with_metadata_shows_external(client, dgi_token, db):
    """External phases show as completada when metadata timestamps present."""
    rid = await _create_rendicion(client, dgi_token, db, metadata={
        "fase1_preparacion_at": "2026-01-15T10:00:00Z",
        "fase2_certificacion_at": "2026-01-20T10:00:00Z",
    })
    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rid}/ciclo", headers=auth(dgi_token),
    )
    data = resp.json()
    assert data["phases"][0]["status"] == "completada"
    assert data["phases"][1]["status"] == "completada"
    assert data["phases"][2]["status"] == "no_aplica"  # fase3 not set


@pytest.mark.asyncio
async def test_ciclo_archived_shows_phase8(client, dgi_token, db):
    """Archived rendition shows phase 8 as completada."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _drive_to_aprobada(client, dgi_token, rid, db)
    await client.patch(
        f"/api/dgi/data/rendiciones/{rid}/archivar", headers=auth(dgi_token),
    )
    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rid}/ciclo", headers=auth(dgi_token),
    )
    data = resp.json()
    assert data["phases"][7]["status"] == "completada"
    assert data["archived_at"] is not None


# ---------------------------------------------------------------------------
# Test 11-12: Metadata update via PATCH
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_patch_metadata_external_phases(client, dgi_token, db):
    """PATCH with metadata sets external phase timestamps."""
    rid = await _create_rendicion(client, dgi_token, db)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}",
        json={"metadata": {"fase1_preparacion_at": "2026-02-01T08:00:00Z"}},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    # Verify via detail
    detail = await client.get(
        f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token),
    )
    assert detail.json()["metadata"]["fase1_preparacion_at"] == "2026-02-01T08:00:00Z"


@pytest.mark.asyncio
async def test_escalation_level2_at_1_5x(client, dgi_token, db):
    """Aging past 1.5x SLA creates level 2 escalation."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    # 7d SLA * 1.5 = 10.5d → age to 11d
    await _age_rendicion(db, rid, "11 days")
    resp = await client.post(
        "/api/dgi/data/rendiciones/check-escalations", headers=auth(dgi_token),
    )
    data = resp.json()
    # Should create both level 1 and level 2
    levels = [d["level"] for d in data["details"] if d["rendition_id"] == rid]
    assert 1 in levels
    assert 2 in levels
```

**Step 2: Update conftest.py cleanup**

Add cleanup for escalation records and T-8PH IPRs. In `cleanup_test_artifacts` fixture:

```python
    await db.execute(text("DELETE FROM core.rendition_escalation WHERE rendition_id IN (SELECT id FROM core.rendition WHERE deleted_at IS NULL)"))
```

Actually, since escalation rows are created per-test and FK-cascade isn't set, add cleanup before existing rendition cleanup (if any). But since rendition tests don't clean up renditions (they accumulate), and escalation test data is tied to those renditions, the simplest approach is to clean escalations at start:

```python
    # Clean escalation test data
    await db.execute(text("DELETE FROM core.rendition_escalation"))
```

**Step 3: Run tests to verify they fail first (TDD red)**

Run:
```bash
docker compose exec api pytest tests/test_sisrec_8phase.py -v
```
Expected: All tests FAIL (endpoints not yet wired if running before Task 3)

**Step 4: Run tests after endpoints are wired**

Run:
```bash
docker compose exec api pytest tests/test_sisrec_8phase.py -v
```
Expected: 12/12 PASS

**Step 5: Run full suite to verify no regressions**

Run:
```bash
docker compose exec api pytest -v
```
Expected: All existing 344 tests + 12 new = 356 tests, 0 failures

**Step 6: Commit**

```bash
git add api/tests/test_sisrec_8phase.py api/tests/conftest.py
git commit -m "test(sisrec-8phase): 12 integration tests — phases, archive, escalation, ciclo"
```

---

### Task 7: Documentation + Memory Update

**Files:**
- Modify: `CLAUDE.md` (coverage metrics, new rule, HΩ status)
- Modify: `docs/GORE_OS_Audit_v3.0.md` (HΩ-14 PARCIAL → CERRADO)
- Modify: `/Users/felixsanhueza/.claude/projects/-Users-felixsanhueza-Developer-goreos/memory/MEMORY.md`
- Modify: `/Users/felixsanhueza/.claude/projects/-Users-felixsanhueza-Developer-goreos/memory/traps_and_patterns.md`

**Step 1: Update CLAUDE.md**

1. Update coverage line: `~148 endpoints`, `356 tests (352 pass + 4 skip)`, `87 tables`, `15/15 HΩ (100%)`
2. Update Open gaps: remove HΩ-14 entry, update CQ score to ~44-48%
3. Add rule 53: `**SISREC 8-Phase CGR**: TP-06 table `core.rendition_phase` (8 seed rows). External phases (1-3) as metadata timestamps. Phase 8 via `archived_at` (not new state). Escalation: `core.rendition_escalation` with 3 levels (1x, 1.5x, 2x SLA). `_STATE_TO_PHASE_CODE` maps states to TP-06 phases. `POST /rendiciones/check-escalations` batch-detects overdue.`

**Step 2: Update Audit v3.0**

- HΩ-14: PARCIAL → CERRADO in §5.4 table and §5.5 table
- Update conclusion: 15/15 cerrados (100%)

**Step 3: Update MEMORY.md**

- Update metrics table: tests, endpoints, tables, HΩ
- Add Ciclo entry for SISREC 8-Phase
- Update Open Gaps: remove HΩ-14, mark 15/15

**Step 4: Update traps_and_patterns.md**

Add under DB Schema Traps:
```
- `core.rendition_phase`: TP-06 parametric (8 seed rows). Columns: ordinal, code, name, responsible_role, sla_days, escalation_action, is_internal. Use ordinal for ordering, code for lookups.
- `core.rendition_escalation`: FK rendition_id + phase_id. escalation_level 1-3 (1x, 1.5x, 2x SLA). alert_id FK optional. resolved_at nullable.
- `core.rendition.archived_at`: Phase 8 timestamp. APROBADA remains terminal state.
```

**Step 5: Commit**

```bash
git add CLAUDE.md docs/GORE_OS_Audit_v3.0.md
git commit -m "docs: SISREC 8-Phase — HΩ-14 CERRADO, 15/15 (100%)"
```

---

## Verification Checklist

1. `docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT COUNT(*) FROM core.rendition_phase;"` → 8
2. `docker exec goreos_db psql -U goreos -d goreos_test -c "SELECT COUNT(*) FROM core.rendition_phase;"` → 8
3. `docker compose exec api pytest tests/test_sisrec_8phase.py -v` → 12/12 PASS
4. `docker compose exec api pytest tests/test_sisrec.py -v` → 18/18 PASS (no regression)
5. `docker compose exec api pytest -v` → All pass
6. `curl -s http://localhost:8000/api/dgi/data/rendiciones/fases -H "Authorization: Bearer $TOKEN" | python3 -m json.tool` → 8 phases
