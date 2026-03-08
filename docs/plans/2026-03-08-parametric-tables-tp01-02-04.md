# TP-01/02/04 Parametric Tables Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the 3 remaining parametric tables: TP-01 evaluator routing query, TP-02 Subvención 8% fund distribution with per-institution ceilings, and TP-04 FRIL 12-category taxonomy with exemptions. All with admin CRUD.

**Architecture:** Two DDL migrations (TP-02 creates 2 tables, TP-04 creates 1 table). TP-01 adds a single query endpoint to existing `admin.py`. All admin endpoints follow the existing pattern: `_require_admin(user)` + raw SQL via `text()`. TP-04 refactors one gate function to read exemptions from DB instead of hardcoded tuple.

**Tech Stack:** FastAPI + SQLAlchemy raw SQL, Pydantic v2, PostgreSQL, pytest + httpx async tests.

---

## Context

**Design document:** `docs/plans/2026-03-08-parametric-tables-tp01-02-04-design.md`

**Existing admin pattern** (`api/app/routers/admin.py`):
- `_require_admin(user)` helper checks `role_code == "ADMIN_SISTEMA"`
- GET returns `[dict(r) for r in result.mappings().all()]` or uses `response_model`
- POST uses `status_code=201`, catches `IntegrityError` → 409
- PATCH uses field allowlist + dynamic SET clause
- Schemas in `api/app/schemas/` (e.g., `threshold.py`, `admin.py`)

**Existing admin CRUD sections:**
- Usuarios (lines 40-285), Divisiones (286-482), Financing Tracks (484-614), Thresholds (616-730), SNI Levels (732-850)

**Critical traps:**
- `CurrentUser` — no `Depends()` as default, use `_require_admin(user)` inline
- Python param ordering: `user: CurrentUser` before `db: AsyncSession = Depends(get_db)`
- `CAST(:param AS jsonb)` for asyncpg (never `::jsonb`)
- After new files: `docker compose restart api`
- `core.ipr` has `financing_track_id` FK (nullable) — set by admin or ETL

---

### Task 1: DDL Migration — TP-02 + TP-04 Tables

**Files:**
- Create: `model/model_goreos/sql/goreos_migration_tp02_tp04.sql`
- Create: `model/model_goreos/sql/goreos_rollback_tp02_tp04.sql`

**Step 1: Write the migration SQL**

Create `model/model_goreos/sql/goreos_migration_tp02_tp04.sql`:

```sql
-- TP-02: Subvención 8% Fund Distribution (7 funds + ceilings)
-- TP-04: FRIL Category Taxonomy (12 categories)
BEGIN;

-- ============================================================
-- TP-02: core.subv8_fund (7 thematic funds)
-- ============================================================
CREATE TABLE IF NOT EXISTS core.subv8_fund (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code          VARCHAR(32) NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    budget_regular NUMERIC,
    budget_special NUMERIC,
    budget_total  NUMERIC,
    is_exclusive  BOOLEAN NOT NULL DEFAULT false,
    sort_order    INT NOT NULL DEFAULT 0,
    is_active     BOOLEAN NOT NULL DEFAULT true,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO core.subv8_fund (code, name, budget_regular, budget_special, budget_total, is_exclusive, sort_order)
VALUES
    ('CULTURA',        'Fondo de Cultura',                330000000, 270000000, 600000000,  false, 1),
    ('SOCIAL',         'Fondo Social e Inclusión',        500000000, NULL,      500000000,  false, 2),
    ('GENERO',         'Fondo de Equidad de Género',      400000000, NULL,      400000000,  false, 3),
    ('DEPORTE',        'Fondo de Deporte',                800000000, 200000000, 1000000000, false, 4),
    ('ADULTO_MAYOR',   'Fondo para Personas Mayores',     400000000, NULL,      400000000,  true,  5),
    ('MEDIO_AMBIENTE', 'Fondo de Medio Ambiente',         400000000, NULL,      400000000,  false, 6),
    ('SEGURIDAD',      'Fondo de Seguridad Ciudadana',   1550000000, NULL,     1550000000,  false, 7)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- TP-02: core.subv8_fund_ceiling (project ceilings per fund × institution type)
-- ============================================================
CREATE TABLE IF NOT EXISTS core.subv8_fund_ceiling (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fund_id          UUID NOT NULL REFERENCES core.subv8_fund(id),
    institution_type VARCHAR(64) NOT NULL,
    area             VARCHAR(64),
    max_amount       NUMERIC NOT NULL CHECK (max_amount > 0),
    notes            TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (fund_id, institution_type, COALESCE(area, ''))
);

CREATE INDEX IF NOT EXISTS idx_subv8_fund_ceiling_fund
    ON core.subv8_fund_ceiling(fund_id);

-- Seed ceilings (representative subset — admin can add more via CRUD)
INSERT INTO core.subv8_fund_ceiling (fund_id, institution_type, area, max_amount, notes)
SELECT f.id, v.institution_type, v.area, v.max_amount, v.notes
FROM core.subv8_fund f
JOIN (VALUES
    ('CULTURA',        'CORPORACION',              'general',              5000000,   NULL),
    ('CULTURA',        'ORG_CULTURAL',             'general',              3500000,   NULL),
    ('CULTURA',        'ORG_COMUNITARIA',          'general',              2500000,   'Juntas de vecinos, clubes'),
    ('CULTURA',        'PRODUCTORA',               'cine',                60000000,   'Producción cinematográfica'),
    ('CULTURA',        'PRODUCTORA',               'festival',            20000000,   'Festivales cine/música/teatro'),
    ('CULTURA',        'PRODUCTORA',               'libro',               10000000,   'Creación literaria'),
    ('SOCIAL',         'CORPORACION',              'general',              5500000,   NULL),
    ('SOCIAL',         'ORG_TERRITORIAL',          'general',              3500000,   NULL),
    ('SOCIAL',         'RESIDENCIA_MEJOR_NINEZ',   'exclusivo',           10000000,   'Residencias Mejor Niñez'),
    ('GENERO',         'ORG_TERRITORIAL',          'general',              3500000,   NULL),
    ('GENERO',         'CORPORACION',              'autonomia_mujer',      6500000,   NULL),
    ('DEPORTE',        'ASOCIACION_REGIONAL',      'general',             10000000,   NULL),
    ('DEPORTE',        'ASOCIACION_COMUNAL',       'general',              6000000,   NULL),
    ('DEPORTE',        'UNIVERSIDAD',              'general',              4000000,   NULL),
    ('DEPORTE',        'CLUB_DEPORTIVO',           'general',              1800000,   NULL),
    ('DEPORTE',        'CORPORACION',              'organizacion_promocion', 30000000, NULL),
    ('ADULTO_MAYOR',   'ALL',                      'general',              2500000,   'Tope unificado para todas las áreas'),
    ('MEDIO_AMBIENTE', 'CORPORACION',              'general',              6500000,   NULL),
    ('MEDIO_AMBIENTE', 'ORG_TERRITORIAL',          'general',              3500000,   NULL),
    ('MEDIO_AMBIENTE', 'COMITE_APR',               'paneles_solares',      6000000,   NULL),
    ('MEDIO_AMBIENTE', 'CORPORACION',              'sendero_sustentable', 25000000,   NULL),
    ('SEGURIDAD',      'ORG_TERRITORIAL',          'general',              5500000,   NULL)
) AS v(fund_code, institution_type, area, max_amount, notes) ON f.code = v.fund_code
ON CONFLICT DO NOTHING;

-- ============================================================
-- TP-04: core.fril_category (12 FRIL project categories)
-- ============================================================
CREATE TABLE IF NOT EXISTS core.fril_category (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code                      VARCHAR(3) NOT NULL UNIQUE,
    name                      TEXT NOT NULL,
    group_code                VARCHAR(1) NOT NULL CHECK (group_code IN ('A', 'B', 'C', 'D')),
    group_name                TEXT NOT NULL,
    description               TEXT,
    examples                  TEXT,
    max_utm                   NUMERIC(12,2) NOT NULL DEFAULT 4545,
    is_exempt_commune_limit   BOOLEAN NOT NULL DEFAULT false,
    is_active                 BOOLEAN NOT NULL DEFAULT true,
    sort_order                INT NOT NULL DEFAULT 0,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO core.fril_category (code, name, group_code, group_name, description, examples, max_utm, is_exempt_commune_limit, sort_order)
VALUES
    ('A1', 'Integración Rural',    'A', 'Desarrollo Territorial', 'Infraestructura de servicios básicos y conectividad para zonas alejadas', 'Sistemas APR, electrificación rural, telecomunicaciones', 4545, false, 1),
    ('A2', 'Acceso al Agua',       'A', 'Desarrollo Territorial', 'Sistemas de agua potable, alcantarillado y drenaje',                     'Sistemas APR, impulsión, tratamiento, distribución, alcantarillado', 4545, true, 2),
    ('A3', 'Vial',                 'A', 'Desarrollo Territorial', 'Infraestructura vial y de conectividad terrestre',                       'Aceras, baches, calles, caminos, cunetas, veredas, supresor de polvo', 4545, true, 3),
    ('B1', 'Edificación Pública',  'B', 'Servicios',              'Construcción y mejoramiento de edificios públicos',                       'Postas, centros de salud, escuelas, patios cubiertos, cuarteles de bomberos', 4545, false, 4),
    ('B2', 'Gestión de Riesgos',   'B', 'Servicios',              'Obras de mitigación y prevención de riesgos naturales',                  'Muros de contención, drenajes, cortafuegos, desbroce', 4545, false, 5),
    ('B3', 'Seguridad',            'B', 'Servicios',              'Infraestructura de seguridad ciudadana',                                 'Luminarias, televigilancia, cierres perimetrales, refugios peatonales', 4545, false, 6),
    ('C1', 'Inclusión',            'C', 'Desarrollo Social y Económico', 'Infraestructura para inclusión social',                           'Infraestructura inclusiva, centros de terapia, centros de adulto mayor', 4545, false, 7),
    ('C2', 'Género',               'C', 'Desarrollo Social y Económico', 'Infraestructura con enfoque de género',                           'Centros de acogida, casas de protección', 4545, false, 8),
    ('C3', 'Turismo',              'C', 'Desarrollo Social y Económico', 'Infraestructura turística y patrimonial',                          'Pórticos, senderos turísticos, bordes costeros, miradores, señalética', 4545, false, 9),
    ('D1', 'Deportes',             'D', 'Medio Ambiente',         'Infraestructura deportiva y recreativa',                                  'Canchas, multicanchas, estadios, piscinas, pistas de trote, plazas activas', 4545, false, 10),
    ('D2', 'Áreas Verdes',         'D', 'Medio Ambiente',         'Espacios verdes y de esparcimiento',                                     'Paseos peatonales, plazas, parques, juegos de agua', 4545, false, 11),
    ('D3', 'Sustentabilidad',      'D', 'Medio Ambiente',         'Proyectos de sustentabilidad ambiental',                                 'Paneles solares, energía eólica, riego eficiente, reciclaje, compostaje', 4545, false, 12)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- Self-register migration
-- ============================================================
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_tp02_tp04.sql', 'manual', 'tp02_tp04_self_register')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
```

**Step 2: Write the rollback SQL**

Create `model/model_goreos/sql/goreos_rollback_tp02_tp04.sql`:

```sql
BEGIN;
DROP INDEX IF EXISTS core.idx_subv8_fund_ceiling_fund;
DROP TABLE IF EXISTS core.subv8_fund_ceiling;
DROP TABLE IF EXISTS core.subv8_fund;
DROP TABLE IF EXISTS core.fril_category;
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_tp02_tp04.sql';
COMMIT;
```

**Step 3: Apply migration to both databases**

Run:
```bash
./scripts/run_migrations.sh goreos_db goreos_model
./scripts/run_migrations.sh goreos_db goreos_test
```

**Step 4: Verify**

Run:
```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT code, name, budget_total, is_exclusive FROM core.subv8_fund ORDER BY sort_order;"
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT COUNT(*) FROM core.subv8_fund_ceiling;"
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT code, name, group_code, is_exempt_commune_limit FROM core.fril_category ORDER BY sort_order;"
```
Expected: 7 funds, ~22 ceilings, 12 categories.

**Step 5: Commit**

```bash
git add model/model_goreos/sql/goreos_migration_tp02_tp04.sql model/model_goreos/sql/goreos_rollback_tp02_tp04.sql
git commit -m "feat(parametric): DDL migration — TP-02 subv8_fund + ceilings, TP-04 fril_category"
```

---

### Task 2: Pydantic Schemas

**Files:**
- Create: `api/app/schemas/parametric.py`

**Step 1: Create schema file**

```python
from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime


# ============================================================
# TP-02: Subvención 8% Funds
# ============================================================

class Subv8FundItem(BaseModel):
    id: UUID
    code: str
    name: str
    budget_regular: Decimal | None = None
    budget_special: Decimal | None = None
    budget_total: Decimal | None = None
    is_exclusive: bool
    sort_order: int
    is_active: bool


class Subv8FundCreate(BaseModel):
    code: str
    name: str
    budget_regular: Decimal | None = None
    budget_special: Decimal | None = None
    budget_total: Decimal | None = None
    is_exclusive: bool = False
    sort_order: int = 0


class Subv8FundUpdate(BaseModel):
    name: str | None = None
    budget_regular: Decimal | None = None
    budget_special: Decimal | None = None
    budget_total: Decimal | None = None
    is_exclusive: bool | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class Subv8CeilingItem(BaseModel):
    id: UUID
    fund_id: UUID
    fund_code: str | None = None
    fund_name: str | None = None
    institution_type: str
    area: str | None = None
    max_amount: Decimal
    notes: str | None = None


class Subv8CeilingCreate(BaseModel):
    institution_type: str
    area: str | None = None
    max_amount: Decimal
    notes: str | None = None


class Subv8CeilingUpdate(BaseModel):
    institution_type: str | None = None
    area: str | None = None
    max_amount: Decimal | None = None
    notes: str | None = None


# ============================================================
# TP-04: FRIL Categories
# ============================================================

class FrilCategoryItem(BaseModel):
    id: UUID
    code: str
    name: str
    group_code: str
    group_name: str
    description: str | None = None
    examples: str | None = None
    max_utm: Decimal
    is_exempt_commune_limit: bool
    is_active: bool
    sort_order: int


class FrilCategoryCreate(BaseModel):
    code: str
    name: str
    group_code: str
    group_name: str
    description: str | None = None
    examples: str | None = None
    max_utm: Decimal = Decimal("4545")
    is_exempt_commune_limit: bool = False
    sort_order: int = 0


class FrilCategoryUpdate(BaseModel):
    name: str | None = None
    group_code: str | None = None
    group_name: str | None = None
    description: str | None = None
    examples: str | None = None
    max_utm: Decimal | None = None
    is_exempt_commune_limit: bool | None = None
    is_active: bool | None = None
    sort_order: int | None = None
```

**Step 2: Commit**

```bash
git add api/app/schemas/parametric.py
git commit -m "feat(parametric): Pydantic schemas — subv8 funds/ceilings, fril categories"
```

---

### Task 3: Admin CRUD Endpoints — TP-02 Subv8 Funds + Ceilings (8 endpoints)

**Files:**
- Modify: `api/app/routers/admin.py` (add after SNI levels section, ~line 850)

**Step 1: Add imports at top of admin.py**

Add to the existing imports:

```python
from app.schemas.parametric import (
    Subv8FundItem, Subv8FundCreate, Subv8FundUpdate,
    Subv8CeilingItem, Subv8CeilingCreate, Subv8CeilingUpdate,
    FrilCategoryItem, FrilCategoryCreate, FrilCategoryUpdate,
)
```

**Step 2: Add TP-02 endpoints after SNI levels section**

Append after the last SNI level endpoint:

```python
# ===========================================================================
# SUBV8 FUNDS — TP-02 (Subvención 8% Fund Distribution)
# ===========================================================================

_SUBV8_FUND_FIELDS = {
    "name", "budget_regular", "budget_special", "budget_total",
    "is_exclusive", "sort_order", "is_active",
}


@router.get("/subv8-funds", response_model=list[Subv8FundItem])
async def list_subv8_funds(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT id, code, name, budget_regular, budget_special, budget_total,
                   is_exclusive, sort_order, is_active
            FROM core.subv8_fund
            ORDER BY sort_order
        """)
    )
    return [Subv8FundItem(**dict(r)) for r in result.mappings().all()]


@router.post("/subv8-funds", status_code=status.HTTP_201_CREATED)
async def create_subv8_fund(
    data: Subv8FundCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    try:
        result = await db.execute(
            text("""
                INSERT INTO core.subv8_fund (
                    code, name, budget_regular, budget_special, budget_total,
                    is_exclusive, sort_order
                ) VALUES (
                    :code, :name, :budget_regular, :budget_special, :budget_total,
                    :is_exclusive, :sort_order
                )
                RETURNING id
            """),
            data.model_dump(),
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"]), "code": data.code}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un fondo con ese código")


@router.patch("/subv8-funds/{fund_id}")
async def update_subv8_fund(
    fund_id: UUID,
    data: Subv8FundUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    existing = await db.execute(
        text("SELECT id FROM core.subv8_fund WHERE id = :id"),
        {"id": str(fund_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Fondo no encontrado")

    updates = data.model_dump(exclude_none=True)
    if not updates:
        return {"message": "Sin cambios"}
    for key in updates:
        if key not in _SUBV8_FUND_FIELDS:
            raise HTTPException(status_code=422, detail=f"Campo no permitido: {key}")

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(fund_id)
    await db.execute(
        text(f"UPDATE core.subv8_fund SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    await db.commit()
    return {"message": "Fondo actualizado"}


# ---------------------------------------------------------------------------
# SUBV8 FUND CEILINGS — per-institution project caps
# ---------------------------------------------------------------------------

@router.get("/subv8-funds/{fund_id}/ceilings", response_model=list[Subv8CeilingItem])
async def list_subv8_fund_ceilings(
    fund_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    exists = (await db.execute(
        text("SELECT 1 FROM core.subv8_fund WHERE id = :id"),
        {"id": str(fund_id)},
    )).scalar()
    if not exists:
        raise HTTPException(status_code=404, detail="Fondo no encontrado")

    result = await db.execute(
        text("""
            SELECT c.id, c.fund_id, f.code AS fund_code, f.name AS fund_name,
                   c.institution_type, c.area, c.max_amount, c.notes
            FROM core.subv8_fund_ceiling c
            JOIN core.subv8_fund f ON f.id = c.fund_id
            WHERE c.fund_id = :fid
            ORDER BY c.institution_type, c.area
        """),
        {"fid": str(fund_id)},
    )
    return [Subv8CeilingItem(**dict(r)) for r in result.mappings().all()]


@router.post("/subv8-funds/{fund_id}/ceilings", status_code=status.HTTP_201_CREATED)
async def create_subv8_ceiling(
    fund_id: UUID,
    data: Subv8CeilingCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    exists = (await db.execute(
        text("SELECT 1 FROM core.subv8_fund WHERE id = :id"),
        {"id": str(fund_id)},
    )).scalar()
    if not exists:
        raise HTTPException(status_code=404, detail="Fondo no encontrado")

    try:
        result = await db.execute(
            text("""
                INSERT INTO core.subv8_fund_ceiling (fund_id, institution_type, area, max_amount, notes)
                VALUES (:fund_id, :institution_type, :area, :max_amount, :notes)
                RETURNING id
            """),
            {"fund_id": str(fund_id), **data.model_dump()},
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"])}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un tope para esa combinación fondo/tipo/área")


@router.get("/subv8-fund-ceilings", response_model=list[Subv8CeilingItem])
async def list_all_ceilings(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT c.id, c.fund_id, f.code AS fund_code, f.name AS fund_name,
                   c.institution_type, c.area, c.max_amount, c.notes
            FROM core.subv8_fund_ceiling c
            JOIN core.subv8_fund f ON f.id = c.fund_id
            ORDER BY f.sort_order, c.institution_type, c.area
        """)
    )
    return [Subv8CeilingItem(**dict(r)) for r in result.mappings().all()]


@router.patch("/subv8-fund-ceilings/{ceiling_id}")
async def update_subv8_ceiling(
    ceiling_id: UUID,
    data: Subv8CeilingUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    existing = await db.execute(
        text("SELECT id FROM core.subv8_fund_ceiling WHERE id = :id"),
        {"id": str(ceiling_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Tope no encontrado")

    updates = data.model_dump(exclude_none=True)
    if not updates:
        return {"message": "Sin cambios"}

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(ceiling_id)
    await db.execute(
        text(f"UPDATE core.subv8_fund_ceiling SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    await db.commit()
    return {"message": "Tope actualizado"}


@router.delete("/subv8-fund-ceilings/{ceiling_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subv8_ceiling(
    ceiling_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("DELETE FROM core.subv8_fund_ceiling WHERE id = :id RETURNING id"),
        {"id": str(ceiling_id)},
    )
    if not result.first():
        raise HTTPException(status_code=404, detail="Tope no encontrado")
    await db.commit()
```

**Step 3: Commit**

```bash
git add api/app/routers/admin.py
git commit -m "feat(parametric): TP-02 admin CRUD — subv8 funds + ceilings (8 endpoints)"
```

---

### Task 4: Admin CRUD Endpoints — TP-04 FRIL Categories (3 endpoints)

**Files:**
- Modify: `api/app/routers/admin.py` (add after subv8 section)

**Step 1: Add FRIL category endpoints**

```python
# ===========================================================================
# FRIL CATEGORIES — TP-04 (FRIL Category Taxonomy)
# ===========================================================================

_FRIL_CATEGORY_FIELDS = {
    "name", "group_code", "group_name", "description", "examples",
    "max_utm", "is_exempt_commune_limit", "is_active", "sort_order",
}


@router.get("/fril-categories", response_model=list[FrilCategoryItem])
async def list_fril_categories(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT id, code, name, group_code, group_name, description, examples,
                   max_utm, is_exempt_commune_limit, is_active, sort_order
            FROM core.fril_category
            ORDER BY sort_order
        """)
    )
    return [FrilCategoryItem(**dict(r)) for r in result.mappings().all()]


@router.post("/fril-categories", status_code=status.HTTP_201_CREATED)
async def create_fril_category(
    data: FrilCategoryCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    try:
        result = await db.execute(
            text("""
                INSERT INTO core.fril_category (
                    code, name, group_code, group_name, description, examples,
                    max_utm, is_exempt_commune_limit, sort_order
                ) VALUES (
                    :code, :name, :group_code, :group_name, :description, :examples,
                    :max_utm, :is_exempt_commune_limit, :sort_order
                )
                RETURNING id
            """),
            data.model_dump(),
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"]), "code": data.code}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese código")


@router.patch("/fril-categories/{category_id}")
async def update_fril_category(
    category_id: UUID,
    data: FrilCategoryUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    existing = await db.execute(
        text("SELECT id FROM core.fril_category WHERE id = :id"),
        {"id": str(category_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Categoría FRIL no encontrada")

    updates = data.model_dump(exclude_none=True)
    if not updates:
        return {"message": "Sin cambios"}
    for key in updates:
        if key not in _FRIL_CATEGORY_FIELDS:
            raise HTTPException(status_code=422, detail=f"Campo no permitido: {key}")

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(category_id)
    await db.execute(
        text(f"UPDATE core.fril_category SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    await db.commit()
    return {"message": "Categoría FRIL actualizada"}
```

**Step 2: Commit**

```bash
git add api/app/routers/admin.py
git commit -m "feat(parametric): TP-04 admin CRUD — fril categories (3 endpoints)"
```

---

### Task 5: TP-01 Evaluator Routing Endpoint + TP-04 Gate Refactor

**Files:**
- Modify: `api/app/routers/admin.py` (add routing endpoint)
- Modify: `api/app/routers/ipr.py` (refactor `_check_fril_max_per_comuna`)

**Step 1: Add TP-01 routing endpoint in admin.py**

Add after financing-tracks PATCH endpoint (~line 614):

```python
# ---------------------------------------------------------------------------
# GET /api/admin/financing-tracks/routing — TP-01 evaluator routing query
# ---------------------------------------------------------------------------

@router.get("/financing-tracks/routing")
async def get_evaluator_routing(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    ipr_id: UUID | None = None,
):
    """Given an IPR, returns its financing track evaluator info. Informational only."""
    _require_admin(user)
    if not ipr_id:
        raise HTTPException(status_code=422, detail="ipr_id requerido")

    row = (await db.execute(
        text("""
            SELECT ft.code AS track_code, ft.label AS track_label,
                   ft.evaluator_code, ft.evaluator_label,
                   ft.favorable_products, ft.sla_days, ft.rs_validity_years
            FROM core.ipr i
            JOIN core.financing_track ft ON ft.id = i.financing_track_id
            WHERE i.id = :ipr_id AND i.deleted_at IS NULL AND ft.is_active = true
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="IPR no encontrado o sin track de financiamiento asignado",
        )
    return dict(row)
```

**IMPORTANT:** This endpoint route `/financing-tracks/routing` MUST be registered BEFORE `/financing-tracks/{track_id}` in the router to avoid FastAPI capturing "routing" as a UUID. If the existing PATCH is at `/financing-tracks/{track_id}`, place this GET before it.

**Step 2: Refactor `_check_fril_max_per_comuna` in ipr.py**

Replace the hardcoded exemption check (around line 470-472 in `ipr.py`):

```python
    # OLD: if ipr_row["fril_category"] in ("A2", "A3"):
    # NEW: Check exemption from DB
    fril_cat = ipr_row["fril_category"]
    if fril_cat:
        exempt = (await db.execute(
            text("""
                SELECT is_exempt_commune_limit FROM core.fril_category
                WHERE code = :code AND is_active = true
            """),
            {"code": fril_cat},
        )).scalar()
        if exempt:
            return None
```

**Step 3: Commit**

```bash
git add api/app/routers/admin.py api/app/routers/ipr.py
git commit -m "feat(parametric): TP-01 routing endpoint + TP-04 gate refactor (DB exemptions)"
```

---

### Task 6: Integration Tests (~13 tests)

**Files:**
- Create: `api/tests/test_parametric.py`
- Modify: `api/tests/conftest.py` (cleanup)
- Modify: `scripts/setup_test_db.sh` (add migration)

**Step 1: Update setup_test_db.sh**

Add before the "Copy core parametric tables" block:

```bash
# Apply TP-02/TP-04 migration (subv8 funds + FRIL categories seed)
docker exec -i goreos_db psql -U goreos -d goreos_test < model/model_goreos/sql/goreos_migration_tp02_tp04.sql
```

**Step 2: Update conftest.py cleanup**

Add to the `cleanup_test_artifacts` fixture:

```python
    # Clean parametric test data
    await db.execute(text("DELETE FROM core.subv8_fund_ceiling WHERE notes LIKE 'TEST-%'"))
    await db.execute(text("DELETE FROM core.subv8_fund WHERE code LIKE 'TEST-%'"))
    await db.execute(text("DELETE FROM core.fril_category WHERE code LIKE 'T%' AND LENGTH(code) > 3"))
```

**Step 3: Create test file**

Create `api/tests/test_parametric.py`:

```python
"""Tests for parametric tables TP-01, TP-02, TP-04.

Covers:
- TP-02: Subv8 fund CRUD + ceiling CRUD
- TP-04: FRIL category CRUD + gate refactor
- TP-01: Evaluator routing query
"""
import pytest
from sqlalchemy import text
from tests.conftest import auth


# ---------------------------------------------------------------------------
# TP-02: Subv8 Funds
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_subv8_funds(client, admin_token):
    """GET /admin/subv8-funds returns 7 seeded funds."""
    resp = await client.get("/api/admin/subv8-funds", headers=auth(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 7
    codes = [f["code"] for f in data]
    assert "CULTURA" in codes
    assert "ADULTO_MAYOR" in codes


@pytest.mark.asyncio
async def test_create_subv8_fund(client, admin_token):
    """POST /admin/subv8-funds creates a fund."""
    resp = await client.post("/api/admin/subv8-funds", json={
        "code": "TEST-FONDO",
        "name": "Fondo de prueba",
        "budget_total": 100000,
        "sort_order": 99,
    }, headers=auth(admin_token))
    assert resp.status_code == 201
    assert resp.json()["code"] == "TEST-FONDO"


@pytest.mark.asyncio
async def test_create_subv8_fund_duplicate_409(client, admin_token):
    """POST with duplicate code returns 409."""
    await client.post("/api/admin/subv8-funds", json={
        "code": "TEST-DUP", "name": "Dup1", "sort_order": 98,
    }, headers=auth(admin_token))
    resp = await client.post("/api/admin/subv8-funds", json={
        "code": "TEST-DUP", "name": "Dup2", "sort_order": 97,
    }, headers=auth(admin_token))
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_update_subv8_fund(client, admin_token):
    """PATCH /admin/subv8-funds/{id} updates a fund."""
    create = await client.post("/api/admin/subv8-funds", json={
        "code": "TEST-UPD", "name": "Before", "sort_order": 96,
    }, headers=auth(admin_token))
    fund_id = create.json()["id"]
    resp = await client.patch(f"/api/admin/subv8-funds/{fund_id}", json={
        "name": "After",
    }, headers=auth(admin_token))
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# TP-02: Subv8 Ceilings
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_ceilings_for_fund(client, admin_token, db):
    """GET /admin/subv8-funds/{id}/ceilings returns ceilings."""
    fund = (await db.execute(
        text("SELECT id FROM core.subv8_fund WHERE code = 'CULTURA'")
    )).scalar()
    resp = await client.get(
        f"/api/admin/subv8-funds/{fund}/ceilings", headers=auth(admin_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["fund_code"] == "CULTURA"


@pytest.mark.asyncio
async def test_create_and_delete_ceiling(client, admin_token, db):
    """POST + DELETE ceiling lifecycle."""
    fund = (await db.execute(
        text("SELECT id FROM core.subv8_fund WHERE code = 'SEGURIDAD'")
    )).scalar()
    # Create
    resp = await client.post(
        f"/api/admin/subv8-funds/{fund}/ceilings", json={
            "institution_type": "TEST_INST",
            "area": "test_area",
            "max_amount": 999999,
            "notes": "TEST-ceiling",
        }, headers=auth(admin_token),
    )
    assert resp.status_code == 201
    ceiling_id = resp.json()["id"]
    # Delete
    del_resp = await client.delete(
        f"/api/admin/subv8-fund-ceilings/{ceiling_id}", headers=auth(admin_token),
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_list_all_ceilings(client, admin_token):
    """GET /admin/subv8-fund-ceilings returns all ceilings flat."""
    resp = await client.get(
        "/api/admin/subv8-fund-ceilings", headers=auth(admin_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 10


# ---------------------------------------------------------------------------
# TP-04: FRIL Categories
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_fril_categories(client, admin_token):
    """GET /admin/fril-categories returns 12 categories."""
    resp = await client.get("/api/admin/fril-categories", headers=auth(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 12
    # A2 and A3 are exempt
    a2 = next(c for c in data if c["code"] == "A2")
    assert a2["is_exempt_commune_limit"] is True
    b1 = next(c for c in data if c["code"] == "B1")
    assert b1["is_exempt_commune_limit"] is False


@pytest.mark.asyncio
async def test_create_fril_category(client, admin_token):
    """POST /admin/fril-categories creates a category."""
    resp = await client.post("/api/admin/fril-categories", json={
        "code": "T1", "name": "Test Category", "group_code": "A",
        "group_name": "Test Group", "max_utm": 1000, "sort_order": 99,
    }, headers=auth(admin_token))
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_update_fril_category(client, admin_token, db):
    """PATCH /admin/fril-categories/{id} updates exemption flag."""
    cat = (await db.execute(
        text("SELECT id FROM core.fril_category WHERE code = 'B1'")
    )).scalar()
    resp = await client.patch(f"/api/admin/fril-categories/{cat}", json={
        "is_exempt_commune_limit": True,
    }, headers=auth(admin_token))
    assert resp.status_code == 200
    # Revert
    await client.patch(f"/api/admin/fril-categories/{cat}", json={
        "is_exempt_commune_limit": False,
    }, headers=auth(admin_token))


# ---------------------------------------------------------------------------
# TP-01: Evaluator Routing
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_routing_no_ipr_422(client, admin_token):
    """GET /admin/financing-tracks/routing without ipr_id returns 422."""
    resp = await client.get(
        "/api/admin/financing-tracks/routing", headers=auth(admin_token),
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_routing_no_track_404(client, admin_token, db):
    """GET /admin/financing-tracks/routing for IPR without track returns 404."""
    ipr = (await db.execute(
        text("SELECT id FROM core.ipr WHERE financing_track_id IS NULL LIMIT 1")
    )).scalar()
    if not ipr:
        pytest.skip("No IPR without track in test DB")
    resp = await client.get(
        f"/api/admin/financing-tracks/routing?ipr_id={ipr}",
        headers=auth(admin_token),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_non_admin_403(client, dgi_token):
    """Non-admin gets 403 on all parametric endpoints."""
    resp = await client.get("/api/admin/subv8-funds", headers=auth(dgi_token))
    assert resp.status_code == 403
```

**Step 4: Run tests**

```bash
docker compose restart api
docker compose exec api pytest tests/test_parametric.py -v
```
Expected: 13/13 PASS

**Step 5: Run full suite**

```bash
docker compose exec api pytest -v 2>&1 | tail -10
```
Expected: ~369 total (356 + 13), 0 failures

**Step 6: Commit**

```bash
git add api/tests/test_parametric.py api/tests/conftest.py scripts/setup_test_db.sh
git commit -m "test(parametric): 13 integration tests — subv8 funds/ceilings, fril categories, routing"
```

---

### Task 7: Documentation + Memory

**Files:**
- Modify: `CLAUDE.md` (coverage, rules, gaps)
- Modify: memory files

**Step 1: Update CLAUDE.md**

- Coverage: `~160 endpoints`, `369 tests`, `30 modules`, `90 tables`
- Add rule 54: **Parametric tables TP-02/04**: `core.subv8_fund` (7 funds) + `core.subv8_fund_ceiling` (~22 ceilings per institution type). `core.fril_category` (12 categories A1-D3, `is_exempt_commune_limit` for A2/A3). Admin CRUD in `/api/admin/`. `_check_fril_max_per_comuna()` reads exemptions from DB.
- Update Open gaps: remove TP-02/04 references, update TP status to 6/6 DONE

**Step 2: Update memory**

- MEMORY.md: metrics, ciclo entry, gaps
- traps_and_patterns.md: new DB schema entries for subv8_fund, subv8_fund_ceiling, fril_category

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: TP-01/02/04 parametric tables complete — 6/6 TPs done"
```

---

## Verification Checklist

1. `docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT COUNT(*) FROM core.subv8_fund;"` → 7
2. `docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT COUNT(*) FROM core.subv8_fund_ceiling;"` → ~22
3. `docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT COUNT(*) FROM core.fril_category;"` → 12
4. `docker compose exec api pytest tests/test_parametric.py -v` → 13/13 PASS
5. `docker compose exec api pytest tests/test_track_enforcement.py -v` → all pass (gate refactor regression check)
6. `docker compose exec api pytest -v` → all pass
