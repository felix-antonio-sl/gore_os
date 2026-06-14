# Visual Refresh — Capas Progresivas Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Centro de Comando Personal dashboard, table enrichment components, and domain color accents across 55 pages to resolve 5 UX tensions.

**Architecture:** 3 progressive layers. Capa 1: 1 backend endpoint (`action-items` as computed coproduct of 6 sources) + 6 new frontend components (command-center orchestrator, attention strip, 4 conditional modules). Capa 2: 3 reusable table cell components + 1 detail page template. Capa 3: PageHeader accent color prop + 15 list page modifications.

**Tech Stack:** FastAPI + SQLAlchemy (raw SQL), Pydantic v2, Next.js 16 (App Router), TypeScript, TailwindCSS v4, shadcn/ui, lucide-react.

**Spec:** `docs/superpowers/specs/2026-03-12-visual-refresh-capas-progresivas-design.md`

---

## Chunk 1: Capa 1 Backend — `action-items` Endpoint

### Task 1: Pydantic Schemas for ActionItem

**Files:**
- Modify: `api/app/schemas/dashboard.py`

- [ ] **Step 1: Add ActionItem and ActionItemsResponse schemas**

Append to `api/app/schemas/dashboard.py`:

```python
from datetime import date


class ActionItem(BaseModel):
    id: str
    category: str           # COMPROMISO|ALERTA|DECISION|ESCALAMIENTO|SLA|RIESGO
    title: str
    subtitle: str | None = None
    deadline: date | None = None
    days_remaining: int | None = None
    temporal: str | None = None   # VENCIDO|HOY|ESTA_SEMANA|FUTURO
    severity: str           # CRITICO|ALTO|MEDIO|BAJO
    priority: int           # total order (0 = max urgency)
    action_label: str       # "Completar"|"Decidir"|"Gestionar"|"Ver"
    action_route: str       # e.g. "/compromisos", "/escalamiento/{id}"


class ActionItemsResponse(BaseModel):
    greeting_name: str
    today: date
    summary: str
    items: list[ActionItem]
    counts: dict[str, int]  # by severity: {"CRITICO": 2, "ALTO": 3, ...}
```

Note: `date` is already imported in this file (line 3). No duplicate import needed.

- [ ] **Step 2: Verify schemas compile**

Run: `docker compose exec api python -c "from app.schemas.dashboard import ActionItem, ActionItemsResponse; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add api/app/schemas/dashboard.py
git commit -m "feat(schemas): add ActionItem + ActionItemsResponse for action-items endpoint"
```

---

### Task 2: Backend `action-items` Endpoint

**Files:**
- Modify: `api/app/routers/dashboard.py`

**Context:**
- Existing endpoint pattern: `_dashboard_encargado()`, `_dashboard_jefe_division()`, `_dashboard_admin_regional()` — each does role-scoped raw SQL queries
- User dict from `deps.py` has keys: `id`, `nombre`, `apellido_paterno`, `role_code`, `division_id`, `population`
- All queries must include `AND deleted_at IS NULL` for soft deletes
- `OPERATIONAL_ROLES` and `DGI_ROLES` sets from `security.py`
- Existing `from app.core.security import OPERATIONAL_ROLES, DGI_ROLES` already in dashboard.py

- [ ] **Step 1: Add helper — `compute_priority` and `compute_temporal`**

Add before the existing `_dashboard_encargado()` function in `dashboard.py`:

```python
from app.schemas.dashboard import ActionItem, ActionItemsResponse


def _compute_temporal(days_remaining: int | None) -> str | None:
    """Classify temporal urgency from days_remaining."""
    if days_remaining is None:
        return None
    if days_remaining < 0:
        return "VENCIDO"
    if days_remaining == 0:
        return "HOY"
    if days_remaining <= 7:
        return "ESTA_SEMANA"
    return "FUTURO"


def _compute_priority(temporal: str | None, severity: str) -> int:
    """Total order: severity * 5 + temporal. Lower = more urgent."""
    sev = {"CRITICO": 0, "ALTO": 1, "MEDIO": 2, "BAJO": 3}
    tmp = {"VENCIDO": 0, "HOY": 1, "ESTA_SEMANA": 2, "FUTURO": 3, None: 4}
    return sev.get(severity, 3) * 5 + tmp.get(temporal, 4)


def _severity_from_alert(alert_code: str) -> str:
    """Map alert_level scheme codes to severity."""
    m = {"CRITICO": "CRITICO", "ALTO": "ALTO", "ATENCION": "MEDIO", "INFO": "BAJO"}
    return m.get(alert_code, "BAJO")


def _severity_from_escalation_level(level_code: str) -> str:
    """Map escalation level to severity."""
    m = {"NIVEL_4": "CRITICO", "NIVEL_3": "CRITICO", "NIVEL_2": "ALTO", "NIVEL_1": "MEDIO"}
    return m.get(level_code, "MEDIO")


def _severity_from_risk_probability(prob_code: str) -> str:
    """Map risk probability to severity."""
    m = {"MUY_ALTA": "CRITICO", "ALTA": "ALTO", "MEDIA": "MEDIO", "BAJA": "BAJO", "MUY_BAJA": "BAJO"}
    return m.get(prob_code, "MEDIO")
```

- [ ] **Step 2: Add source query functions**

Add 6 query functions. Each returns `list[ActionItem]`.

```python
async def _ai_commitments(db: AsyncSession, user: dict) -> list[ActionItem]:
    """Source: operational_commitment — scoped by role."""
    role = user["role_code"]

    # Build WHERE clause based on role
    if role in ("ENCARGADO", "ANALISTA", "RTF", "ASESOR_JURIDICO"):
        scope = "AND oc.responsible_id = :uid"
    elif role in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"):
        scope = """AND oc.ipr_id IN (
            SELECT i.id FROM core.ipr i WHERE i.sponsor_division_id = :div_id AND i.deleted_at IS NULL
        )"""
    else:
        # Global roles see all overdue
        scope = "AND oc.due_date < CURRENT_DATE"

    sql = text(f"""
        SELECT oc.id, oc.description, oc.due_date,
               (oc.due_date - CURRENT_DATE) AS days_remaining
        FROM core.operational_commitment oc
        JOIN ref.category sc ON oc.state_id = sc.id
        WHERE sc.code NOT IN ('COMPLETADO', 'VERIFICADO', 'CANCELADO')
          AND oc.deleted_at IS NULL
          {scope}
        ORDER BY oc.due_date ASC NULLS LAST
        LIMIT 20
    """)
    params: dict = {"uid": user["id"], "div_id": user.get("division_id")}
    rows = (await db.execute(sql, params)).mappings().all()
    items = []
    for r in rows:
        dr = r["days_remaining"]
        sev = "ALTO" if (dr is not None and dr < 0) else ("MEDIO" if (dr is not None and dr <= 7) else "BAJO")
        temp = _compute_temporal(dr)
        items.append(ActionItem(
            id=str(r["id"]), category="COMPROMISO",
            title=r["description"] or "Compromiso sin descripción",
            subtitle=None, deadline=r["due_date"], days_remaining=dr,
            temporal=temp, severity=sev, priority=_compute_priority(temp, sev),
            action_label="Completar", action_route="/compromisos",
        ))
    return items


async def _ai_alerts(db: AsyncSession, user: dict) -> list[ActionItem]:
    """Source: alert — scoped by role via subject ownership."""
    role = user["role_code"]

    if role in ("ENCARGADO", "ANALISTA", "RTF", "ASESOR_JURIDICO"):
        scope = """AND a.subject_id IN (
            SELECT i.id FROM core.ipr i WHERE i.assignee_id = :uid AND i.deleted_at IS NULL
        )"""
    elif role in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"):
        scope = """AND a.subject_id IN (
            SELECT i.id FROM core.ipr i WHERE i.sponsor_division_id = :div_id AND i.deleted_at IS NULL
        )"""
    elif role == "JEFE_DGI":
        scope = """AND al.code IN ('CRITICO')"""
    else:
        # Global roles see CRITICO only to avoid noise
        scope = """AND al.code IN ('CRITICO', 'ALTO')"""

    sql = text(f"""
        SELECT a.id, a.message, a.subject_type, a.subject_id, a.triggered_at,
               al.code AS level_code
        FROM core.alert a
        JOIN ref.category al ON a.severity_id = al.id
        WHERE a.deleted_at IS NULL
          AND a.resolved_at IS NULL
          {scope}
        ORDER BY a.triggered_at DESC
        LIMIT 10
    """)
    params: dict = {"uid": user["id"], "div_id": user.get("division_id")}
    rows = (await db.execute(sql, params)).mappings().all()
    items = []
    for r in rows:
        sev = _severity_from_alert(r["level_code"])
        # Alerts have no deadline → temporal is null
        items.append(ActionItem(
            id=str(r["id"]), category="ALERTA",
            title=r["message"], subtitle=r["subject_type"],
            deadline=None, days_remaining=None, temporal=None,
            severity=sev, priority=_compute_priority(None, sev),
            action_label="Ver",
            action_route=f"/ipr/{r['subject_id']}?tab=alertas" if r["subject_type"] == "core.ipr" else "/alertas",
        ))
    return items


async def _ai_decisions(db: AsyncSession, user: dict) -> list[ActionItem]:
    """Source: dgi_ar_decision — only for DGI + global roles."""
    role = user["role_code"]
    if role in ("ENCARGADO", "ANALISTA", "RTF", "ASESOR_JURIDICO",
                "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"):
        return []  # These roles don't see AR decisions

    sql = text("""
        SELECT d.id, d.description, d.due_date,
               (d.due_date - CURRENT_DATE) AS days_remaining,
               ts.code AS type_code
        FROM core.dgi_ar_decision d
        JOIN ref.category ss ON d.status_id = ss.id
        JOIN ref.category ts ON d.decision_type_id = ts.id
        WHERE ss.code = 'PENDIENTE'
          AND d.deleted_at IS NULL
        ORDER BY d.due_date ASC NULLS LAST
        LIMIT 10
    """)
    rows = (await db.execute(sql)).mappings().all()
    items = []
    for r in rows:
        dr = r["days_remaining"]
        sev = "ALTO" if (dr is not None and dr <= 3) else "MEDIO"
        temp = _compute_temporal(dr)
        items.append(ActionItem(
            id=str(r["id"]), category="DECISION",
            title=r["description"], subtitle=r["type_code"],
            deadline=r["due_date"], days_remaining=dr,
            temporal=temp, severity=sev, priority=_compute_priority(temp, sev),
            action_label="Decidir", action_route="/coordinacion",
        ))
    return items


async def _ai_escalations(db: AsyncSession, user: dict) -> list[ActionItem]:
    """Source: dgi_escalation — DGI + global + division (level 1-2 only)."""
    role = user["role_code"]
    if role in ("ENCARGADO", "ANALISTA", "RTF", "ASESOR_JURIDICO"):
        return []

    if role in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"):
        scope = "AND lc.code IN ('NIVEL_1', 'NIVEL_2')"
    else:
        scope = ""

    sql = text(f"""
        SELECT e.id, e.code AS ref_code, e.situation, e.deadline,
               (e.deadline - CURRENT_DATE) AS days_remaining,
               lc.code AS level_code
        FROM core.dgi_escalation e
        JOIN ref.category ss ON e.status_id = ss.id
        JOIN ref.category lc ON e.level_id = lc.id
        WHERE ss.code IN ('ABIERTO', 'EN_GESTION')
          AND e.deleted_at IS NULL
          {scope}
        ORDER BY e.deadline ASC NULLS LAST
        LIMIT 10
    """)
    rows = (await db.execute(sql)).mappings().all()
    items = []
    for r in rows:
        dr = r["days_remaining"]
        sev = _severity_from_escalation_level(r["level_code"])
        temp = _compute_temporal(dr)
        items.append(ActionItem(
            id=str(r["id"]), category="ESCALAMIENTO",
            title=r["situation"] or r["ref_code"],
            subtitle=r["level_code"], deadline=r["deadline"], days_remaining=dr,
            temporal=temp, severity=sev, priority=_compute_priority(temp, sev),
            action_label="Gestionar", action_route=f"/escalamiento/{r['id']}",
        ))
    return items


async def _ai_sla_breaches(db: AsyncSession, user: dict) -> list[ActionItem]:
    """Source: dgi_service_request past SLA — DGI + global roles."""
    role = user["role_code"]
    if role in ("ENCARGADO", "ANALISTA", "RTF", "ASESOR_JURIDICO",
                "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"):
        return []

    # ESP_* only see SLAs for their own services
    esp_scope = ""
    if role in ("ESP_CONTROL_GESTION", "ESP_PROCESOS", "ESP_TD"):
        esp_scope = "AND sr.service_id IN (SELECT s.id FROM core.dgi_service s WHERE s.deleted_at IS NULL)"

    sql = text(f"""
        SELECT sr.id, sr.code AS ref_code, s.name AS service_name,
               sla.target_days, sr.created_at::date AS request_date,
               (CURRENT_DATE - sr.created_at::date) AS days_elapsed
        FROM core.dgi_service_request sr
        JOIN core.dgi_service s ON sr.service_id = s.id
        JOIN core.dgi_sla sla ON sla.service_id = s.id
        JOIN ref.category rs ON sr.status_id = rs.id
        WHERE rs.code NOT IN ('COMPLETADA', 'RECHAZADA')
          AND (CURRENT_DATE - sr.created_at::date) > sla.target_days
          AND sr.deleted_at IS NULL
          {esp_scope}
        ORDER BY (CURRENT_DATE - sr.created_at::date) DESC
        LIMIT 10
    """)
    rows = (await db.execute(sql)).mappings().all()
    items = []
    for r in rows:
        items.append(ActionItem(
            id=str(r["id"]), category="SLA",
            title=f"SLA vencido: {r['service_name']}",
            subtitle=r["ref_code"], deadline=None, days_remaining=None,
            temporal=None, severity="CRITICO",
            priority=_compute_priority(None, "CRITICO"),
            action_label="Ver", action_route=f"/servicios/{r['id']}",
        ))
    return items


async def _ai_risks(db: AsyncSession, user: dict) -> list[ActionItem]:
    """Source: risk — ALTA/MUY_ALTA probability, DGI + global roles."""
    role = user["role_code"]
    if role in ("ENCARGADO", "ANALISTA", "RTF", "ASESOR_JURIDICO",
                "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"):
        return []

    sql = text("""
        SELECT r.id, r.code AS ref_code, r.description,
               pc.code AS prob_code
        FROM core.risk r
        JOIN ref.category ss ON r.status_id = ss.id
        JOIN ref.category pc ON r.probability_id = pc.id
        WHERE ss.code IN ('IDENTIFICADO', 'EN_EVALUACION', 'EN_MITIGACION')
          AND pc.code IN ('ALTA', 'MUY_ALTA')
          AND r.deleted_at IS NULL
        ORDER BY pc.code ASC
        LIMIT 10
    """)
    rows = (await db.execute(sql)).mappings().all()
    items = []
    for r in rows:
        sev = _severity_from_risk_probability(r["prob_code"])
        items.append(ActionItem(
            id=str(r["id"]), category="RIESGO",
            title=r["description"] or r["ref_code"],
            subtitle=r["prob_code"], deadline=None, days_remaining=None,
            temporal=None, severity=sev,
            priority=_compute_priority(None, sev),
            action_label="Gestionar", action_route=f"/riesgos/{r['id']}",
        ))
    return items
```

- [ ] **Step 3: Add the endpoint function**

```python
@router.get("/action-items", response_model=ActionItemsResponse)
async def get_action_items(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Centro de Comando Personal — unified action items for all roles."""
    # Gather items from all 6 sources (filtered by role inside each function)
    all_items: list[ActionItem] = []
    all_items.extend(await _ai_commitments(db, user))
    all_items.extend(await _ai_alerts(db, user))
    all_items.extend(await _ai_decisions(db, user))
    all_items.extend(await _ai_escalations(db, user))
    all_items.extend(await _ai_sla_breaches(db, user))
    all_items.extend(await _ai_risks(db, user))

    # Sort by priority (total order)
    all_items.sort(key=lambda x: x.priority)

    # Count by severity
    counts: dict[str, int] = {"CRITICO": 0, "ALTO": 0, "MEDIO": 0, "BAJO": 0}
    for item in all_items:
        counts[item.severity] = counts.get(item.severity, 0) + 1

    # Summary text
    vencidos = sum(1 for i in all_items if i.temporal == "VENCIDO")
    hoy = sum(1 for i in all_items if i.temporal == "HOY")
    parts = []
    if vencidos > 0:
        parts.append(f"{vencidos} tarea{'s' if vencidos != 1 else ''} vencida{'s' if vencidos != 1 else ''}")
    if hoy > 0:
        parts.append(f"{hoy} para hoy")
    summary = "Tienes " + " y ".join(parts) if parts else "Todo al día"

    # Greeting
    greeting = user.get("nombre", "").split()[0] if user.get("nombre") else "Usuario"

    return ActionItemsResponse(
        greeting_name=greeting,
        today=date.today(),
        summary=summary,
        items=all_items,
        counts=counts,
    )
```

**Important**: This endpoint must be added **before** the existing `@router.get("/dashboard/{dashboard_id}")` route if one exists, to avoid path conflicts. In the current codebase, there is no `{dashboard_id}` route, so add it after the existing `/dashboard/chart-data` endpoint.

- [ ] **Step 4: Import `date` at top of `dashboard.py`**

Add to the imports at the top of `dashboard.py`:

```python
from datetime import date
```

(Check if `datetime` is already imported — if yes, just add `date` to the import.)

- [ ] **Step 5: Verify the endpoint loads**

Run: `docker compose restart api && docker compose exec api python -c "from app.routers.dashboard import router; print('OK')"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add api/app/routers/dashboard.py
git commit -m "feat(api): add GET /dashboard/action-items endpoint — 6-source coproduct with role scoping"
```

---

### Task 3: Integration Tests for `action-items`

**Files:**
- Create: `api/tests/test_action_items.py`

**Context:**
- Test fixtures: `admin_token`, `regional_token`, `jefe_token`, `encargado_token`, `dgi_token`, `analista_token`, `rtf_token`, `juridico_token` from conftest.py
- `auth(token)` helper returns `{"Authorization": f"Bearer {token}"}`
- `catalog` fixture has `users`, `commitment_type_id`, `division_id`

- [ ] **Step 1: Write the test file**

```python
"""
Tests for GET /api/dashboard/action-items — Centro de Comando Personal.

Tests verify:
1. Response structure (all fields present)
2. Role-based scoping (different roles see different categories)
3. Priority ordering (sorted by priority ASC)
4. Summary text generation
5. Access for all role tokens
"""
import pytest
from httpx import AsyncClient
from tests.conftest import auth


@pytest.mark.asyncio
async def test_action_items_structure(client: AsyncClient, regional_token: str):
    """Response has required top-level fields."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(regional_token))
    assert resp.status_code == 200
    data = resp.json()
    assert "greeting_name" in data
    assert "today" in data
    assert "summary" in data
    assert "items" in data
    assert "counts" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["counts"], dict)
    for key in ("CRITICO", "ALTO", "MEDIO", "BAJO"):
        assert key in data["counts"]


@pytest.mark.asyncio
async def test_action_items_item_fields(client: AsyncClient, regional_token: str):
    """Each item has all required fields."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(regional_token))
    data = resp.json()
    if data["items"]:
        item = data["items"][0]
        for key in ("id", "category", "title", "severity", "priority", "action_label", "action_route"):
            assert key in item, f"Missing field: {key}"
        assert item["category"] in ("COMPROMISO", "ALERTA", "DECISION", "ESCALAMIENTO", "SLA", "RIESGO")
        assert item["severity"] in ("CRITICO", "ALTO", "MEDIO", "BAJO")


@pytest.mark.asyncio
async def test_action_items_priority_ordering(client: AsyncClient, regional_token: str):
    """Items are sorted by priority ascending (most urgent first)."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(regional_token))
    data = resp.json()
    priorities = [item["priority"] for item in data["items"]]
    assert priorities == sorted(priorities), "Items should be sorted by priority ASC"


@pytest.mark.asyncio
async def test_action_items_encargado_no_decisions(client: AsyncClient, encargado_token: str):
    """ENCARGADO should not see AR decisions or escalations."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(encargado_token))
    data = resp.json()
    categories = {item["category"] for item in data["items"]}
    assert "DECISION" not in categories, "ENCARGADO should not see AR decisions"
    assert "ESCALAMIENTO" not in categories, "ENCARGADO should not see escalations"
    assert "SLA" not in categories, "ENCARGADO should not see SLA breaches"
    assert "RIESGO" not in categories, "ENCARGADO should not see risks"


@pytest.mark.asyncio
async def test_action_items_jefe_division_no_decisions(client: AsyncClient, jefe_token: str):
    """JEFE_DIVISION should not see AR decisions."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(jefe_token))
    data = resp.json()
    categories = {item["category"] for item in data["items"]}
    assert "DECISION" not in categories


@pytest.mark.asyncio
async def test_action_items_dgi_sees_decisions(client: AsyncClient, dgi_token: str):
    """JEFE_DGI can see decisions, escalations, risks (if they exist)."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(dgi_token))
    assert resp.status_code == 200
    # Just verify access works — actual categories depend on test data


@pytest.mark.asyncio
async def test_action_items_greeting_name(client: AsyncClient, regional_token: str):
    """greeting_name is the first token of user's nombre."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(regional_token))
    data = resp.json()
    assert data["greeting_name"]
    assert " " not in data["greeting_name"], "Should be first name only"


@pytest.mark.asyncio
async def test_action_items_all_roles_accessible(
    client: AsyncClient,
    admin_token: str, regional_token: str, jefe_token: str,
    encargado_token: str, dgi_token: str,
    analista_token: str, rtf_token: str, juridico_token: str,
):
    """All 8 test role tokens can access the endpoint."""
    for token in (admin_token, regional_token, jefe_token, encargado_token,
                  dgi_token, analista_token, rtf_token, juridico_token):
        resp = await client.get("/api/dashboard/action-items", headers=auth(token))
        assert resp.status_code == 200, f"Failed for token type"


@pytest.mark.asyncio
async def test_action_items_unauthenticated(client: AsyncClient):
    """Unauthenticated requests get 401."""
    resp = await client.get("/api/dashboard/action-items")
    assert resp.status_code in (401, 403)
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `docker compose exec api pytest tests/test_action_items.py -v`
Expected: All 9 tests PASS (some may show empty items which is expected with clean test DB)

- [ ] **Step 3: Commit**

```bash
git add api/tests/test_action_items.py
git commit -m "test: add 9 integration tests for action-items endpoint"
```

---

## Chunk 2: Capa 1 Frontend — Centro de Comando Personal

### Task 4: TypeScript Interfaces

**Files:**
- Modify: `web/src/types/index.ts`

- [ ] **Step 1: Add ActionItem and ActionItemsResponse interfaces**

Append to `web/src/types/index.ts` (after the existing `TimelineEvent` interface).

**Note**: The following dashboard response types are used by existing endpoints but were never added to the TS types file. Add them now so module components can import them:

```typescript
// --- Dashboard Response Types (existing endpoints, types previously missing) ---

export interface MisCompromisosResponse {
  kpis: KPICardData[];
  groups: Array<{ label: string; count: number; items: CompromisoListItem[] }>;
}

export interface TeamMemberLoad {
  user_id: string;
  name: string;
  pendientes: number;
  en_progreso: number;
  completados: number;
  vencidos: number;
  total: number;
}

export interface MiDivisionResponse {
  kpis: KPICardData[];
  team: TeamMemberLoad[];
  commitments: CompromisoListItem[];
}

export interface DivisionBreakdown {
  division_name: string;
  vencidos: number;
  total_compromisos: number;
  problemas_abiertos: number;
  ejecucion_pct: number;
}

export interface SemaforoItem {
  dimension: string;
  label: string;
  signal: string;
  indicator_count: number;
}

export interface DashboardExecutivoResponse extends DashboardData {
  divisions: DivisionBreakdown[];
  semaforo: SemaforoItem[];
}

// --- Action Items (Centro de Comando Personal) ---

export interface ActionItem {
  id: string;
  category: "COMPROMISO" | "ALERTA" | "DECISION" | "ESCALAMIENTO" | "SLA" | "RIESGO";
  title: string;
  subtitle: string | null;
  deadline: string | null;
  days_remaining: number | null;
  temporal: "VENCIDO" | "HOY" | "ESTA_SEMANA" | "FUTURO" | null;
  severity: "CRITICO" | "ALTO" | "MEDIO" | "BAJO";
  priority: number;
  action_label: string;
  action_route: string;
}

export interface ActionItemsResponse {
  greeting_name: string;
  today: string;
  summary: string;
  items: ActionItem[];
  counts: Record<string, number>;
}
```

- [ ] **Step 2: Verify build**

Run: `cd web && npx next build`
Expected: Build succeeds, 0 TypeScript errors

- [ ] **Step 3: Commit**

```bash
git add web/src/types/index.ts
git commit -m "feat(types): add ActionItem + ActionItemsResponse interfaces"
```

---

### Task 5: Attention Strip Component

**Files:**
- Create: `web/src/app/(app)/dashboard/components/attention-strip.tsx`

**Context:**
- This component renders the top ~5 urgent action items as cards with action buttons
- Uses `ActionItem` from `@/types`
- Each card has: severity dot, temporal badge, title, subtitle, action button
- Action button navigates to `action_route` via `useRouter`

- [ ] **Step 1: Create the component**

```tsx
"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { AlertCircle, Clock, CheckCircle2, AlertTriangle } from "lucide-react";
import type { ActionItem } from "@/types";

const SEVERITY_DOT: Record<string, string> = {
  CRITICO: "bg-red-500",
  ALTO: "bg-orange-500",
  MEDIO: "bg-amber-500",
  BAJO: "bg-green-500",
};

const TEMPORAL_LABEL: Record<string, { text: string; className: string }> = {
  VENCIDO: { text: "Vencido", className: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300" },
  HOY: { text: "Hoy", className: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300" },
  ESTA_SEMANA: { text: "Esta semana", className: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300" },
  FUTURO: { text: "Próximo", className: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300" },
};

const CATEGORY_ICON: Record<string, React.ReactNode> = {
  COMPROMISO: <CheckCircle2 className="size-4" />,
  ALERTA: <AlertCircle className="size-4" />,
  DECISION: <AlertTriangle className="size-4" />,
  ESCALAMIENTO: <AlertTriangle className="size-4" />,
  SLA: <Clock className="size-4" />,
  RIESGO: <AlertCircle className="size-4" />,
};

interface AttentionStripProps {
  items: ActionItem[];
  maxItems?: number;
}

export function AttentionStrip({ items, maxItems = 5 }: AttentionStripProps) {
  const router = useRouter();

  if (items.length === 0) return null;

  const visible = items.slice(0, maxItems);

  return (
    <div className="space-y-2">
      <h2 className="text-sm font-semibold text-muted-foreground">Requiere atención</h2>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {visible.map((item) => {
          const temporal = item.temporal ? TEMPORAL_LABEL[item.temporal] : null;
          return (
            <div
              key={`${item.category}-${item.id}`}
              className="rounded-lg border bg-card p-3 shadow-sm animate-in fade-in duration-200"
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span className={`size-2 rounded-full ${SEVERITY_DOT[item.severity]}`} />
                {temporal && (
                  <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${temporal.className}`}>
                    {temporal.text}
                  </span>
                )}
                <span className="text-muted-foreground">{CATEGORY_ICON[item.category]}</span>
              </div>
              <p className="text-sm font-medium leading-tight line-clamp-2">{item.title}</p>
              {item.subtitle && (
                <p className="text-xs text-muted-foreground mt-0.5">{item.subtitle}</p>
              )}
              <div className="mt-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7 text-xs"
                  onClick={() => router.push(item.action_route)}
                >
                  {item.action_label}
                </Button>
              </div>
            </div>
          );
        })}
      </div>
      {items.length > maxItems && (
        <p className="text-xs text-muted-foreground">
          +{items.length - maxItems} más
        </p>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify build**

Run: `cd web && npx next build`
Expected: Build succeeds

- [ ] **Step 3: Commit**

```bash
git add web/src/app/\(app\)/dashboard/components/attention-strip.tsx
git commit -m "feat(ui): add AttentionStrip component for urgent action items"
```

---

### Task 6: Module Components (4 files)

**Files:**
- Create: `web/src/app/(app)/dashboard/components/module-my-progress.tsx`
- Create: `web/src/app/(app)/dashboard/components/module-my-team.tsx`
- Create: `web/src/app/(app)/dashboard/components/module-dgi-team.tsx`
- Create: `web/src/app/(app)/dashboard/components/module-kpis.tsx`

**Context:**
- Each module wraps an existing API response in a compact card format
- `module-my-progress.tsx` uses `GET /api/dashboard/mis-compromisos` (ENCARGADO)
- `module-my-team.tsx` uses `GET /api/dashboard/mi-division` (JEFE_DIVISION)
- `module-dgi-team.tsx` uses `GET /api/dgi/cockpit` (JEFE_DGI)
- `module-kpis.tsx` is a presentational wrapper — receives KPIs as props

- [ ] **Step 1: Create `module-my-progress.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { MisCompromisosResponse } from "@/types";

export function ModuleMyProgress() {
  const [data, setData] = useState<MisCompromisosResponse | null>(null);

  useEffect(() => {
    api.get<MisCompromisosResponse>("/api/dashboard/mis-compromisos")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) return <ModuleProgressSkeleton />;

  const total = data.kpis.reduce((sum, k) => sum + k.value, 0);
  const completados = data.kpis.find(k => k.label.toLowerCase().includes("completad"))?.value ?? 0;
  const pct = total > 0 ? Math.round((completados / total) * 100) : 0;

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <h3 className="text-sm font-semibold mb-3">Mi Progreso</h3>
      <div className="flex items-center gap-3 mb-2">
        <div className="flex-1">
          <div className="h-2.5 w-full rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-gradient-to-r from-green-500 to-amber-500 transition-all duration-500"
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
        <span className="text-sm font-bold tabular-nums">{pct}%</span>
      </div>
      <div className="flex gap-4 text-xs text-muted-foreground">
        {data.kpis.map((k) => (
          <span key={k.label}>
            <span className="font-semibold text-foreground">{k.value}</span> {k.sublabel || k.label}
          </span>
        ))}
      </div>
    </div>
  );
}

function ModuleProgressSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="h-4 w-24 bg-muted animate-pulse rounded mb-3" />
      <div className="h-2.5 w-full bg-muted animate-pulse rounded-full mb-2" />
      <div className="flex gap-4">
        <div className="h-3 w-16 bg-muted animate-pulse rounded" />
        <div className="h-3 w-16 bg-muted animate-pulse rounded" />
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create `module-my-team.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { MiDivisionResponse } from "@/types";

export function ModuleMyTeam() {
  const [data, setData] = useState<MiDivisionResponse | null>(null);

  useEffect(() => {
    api.get<MiDivisionResponse>("/api/dashboard/mi-division")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) return <ModuleTeamSkeleton />;

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <h3 className="text-sm font-semibold mb-3">Mi Equipo</h3>
      <div className="grid gap-2">
        {data.team.slice(0, 5).map((m) => (
          <div key={m.user_id} className="flex items-center justify-between text-sm">
            <span className="truncate max-w-[180px]">{m.name}</span>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              {m.vencidos > 0 && (
                <span className="text-red-600 font-medium">{m.vencidos} vencidos</span>
              )}
              <span>{m.pendientes + m.en_progreso} activos</span>
            </div>
          </div>
        ))}
      </div>
      {data.team.length > 5 && (
        <p className="text-xs text-muted-foreground mt-2">+{data.team.length - 5} más</p>
      )}
    </div>
  );
}

function ModuleTeamSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="h-4 w-20 bg-muted animate-pulse rounded mb-3" />
      {[...Array(3)].map((_, i) => (
        <div key={i} className="h-5 w-full bg-muted animate-pulse rounded mb-2" />
      ))}
    </div>
  );
}
```

- [ ] **Step 3: Create `module-dgi-team.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface DgiTeamData {
  team_status?: Array<{ name: string; role: string; activity: string }>;
}

export function ModuleDgiTeam() {
  const [data, setData] = useState<DgiTeamData | null>(null);

  useEffect(() => {
    api.get<DgiTeamData>("/api/dgi/cockpit")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data?.team_status) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <div className="h-4 w-24 bg-muted animate-pulse rounded mb-3" />
        <div className="h-16 bg-muted animate-pulse rounded" />
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-4 animate-in fade-in duration-200">
      <h3 className="text-sm font-semibold mb-3">Equipo DGI</h3>
      <div className="grid gap-2">
        {data.team_status.map((m) => (
          <div key={m.name} className="flex items-center justify-between text-sm">
            <span className="truncate max-w-[180px]">{m.name}</span>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="text-muted-foreground">{m.role}</span>
              <span>{m.activity}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Create `module-kpis.tsx`**

```tsx
import type { KPICardData } from "@/types";

const KPI_COLOR_MAP: Record<string, string> = {
  red: "border-l-red-500",
  orange: "border-l-orange-500",
  amber: "border-l-amber-500",
  green: "border-l-green-500",
  blue: "border-l-blue-500",
  gray: "border-l-slate-400",
};

interface ModuleKpisProps {
  kpis: KPICardData[];
  semaforo?: Array<{ dimension: string; label: string; signal: string }>;
}

export function ModuleKpis({ kpis, semaforo }: ModuleKpisProps) {
  if (kpis.length === 0 && (!semaforo || semaforo.length === 0)) return null;

  return (
    <div className="space-y-3 animate-in fade-in duration-200">
      {kpis.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          {kpis.map((k) => (
            <div
              key={k.label}
              className={`rounded-lg border border-l-4 bg-card p-3 ${KPI_COLOR_MAP[k.color] ?? "border-l-slate-400"}`}
            >
              <p className="text-lg font-bold tabular-nums">{k.value.toLocaleString("es-CL")}</p>
              <p className="text-xs text-muted-foreground">{k.sublabel || k.label}</p>
            </div>
          ))}
        </div>
      )}
      {semaforo && semaforo.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {semaforo.map((s) => {
            const dotColor = s.signal === "VERDE" ? "bg-green-500" : s.signal === "AMARILLO" ? "bg-amber-500" : "bg-red-500";
            return (
              <div key={s.dimension} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className={`size-2 rounded-full ${dotColor}`} />
                {s.label}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 5: Verify build**

Run: `cd web && npx next build`
Expected: Build succeeds, 0 TypeScript errors

- [ ] **Step 6: Commit**

```bash
git add web/src/app/\(app\)/dashboard/components/module-*.tsx
git commit -m "feat(ui): add 4 conditional module components for Centro de Comando"
```

---

### Task 7: Command Center Orchestrator

**Files:**
- Create: `web/src/app/(app)/dashboard/components/command-center.tsx`

**Context:**
- Fetches `GET /api/dashboard/action-items` for greeting + attention strip
- Selects appropriate module based on `user.role_code`
- Fetches module-specific data for KPIs (via the existing endpoints the modules themselves call)
- Layout: greeting → attention strip → module → KPIs

- [ ] **Step 1: Create the component**

```tsx
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDateLong } from "@/lib/format";
import { AttentionStrip } from "./attention-strip";
import { ModuleMyProgress } from "./module-my-progress";
import { ModuleMyTeam } from "./module-my-team";
import { ModuleDgiTeam } from "./module-dgi-team";
import { ModuleKpis } from "./module-kpis";
import type { ActionItemsResponse, RoleCode, KPICardData, DashboardExecutivoResponse } from "@/types";

// Role → module mapping
const PROGRESS_ROLES: RoleCode[] = ["ENCARGADO", "ANALISTA", "RTF", "ASESOR_JURIDICO"];
const TEAM_ROLES: RoleCode[] = ["JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"];
const DGI_TEAM_ROLES: RoleCode[] = ["JEFE_DGI"];
const INDICATOR_ROLES: RoleCode[] = ["ESP_CONTROL_GESTION", "ESP_PROCESOS", "ESP_TD"];
const PANORAMA_ROLES: RoleCode[] = [
  "ADMIN_REGIONAL", "GOBERNADOR", "ADMIN_SISTEMA", "SECRETARIO_EJECUTIVO", "CONSEJERO_REGIONAL",
];

export function CommandCenter() {
  const { user } = useAuth();
  const [actionData, setActionData] = useState<ActionItemsResponse | null>(null);
  const [kpis, setKpis] = useState<KPICardData[]>([]);
  const [semaforo, setSemaforo] = useState<Array<{ dimension: string; label: string; signal: string }>>([]);
  const [loading, setLoading] = useState(true);

  const role = user?.role_code;

  useEffect(() => {
    // Fetch action items (universal)
    api.get<ActionItemsResponse>("/api/dashboard/action-items")
      .then(setActionData)
      .catch(() => setActionData(null))
      .finally(() => setLoading(false));
  }, []);

  // Fetch KPIs + semáforo for Panorama roles
  useEffect(() => {
    if (!role) return;
    if (PANORAMA_ROLES.includes(role)) {
      api.get<DashboardExecutivoResponse>("/api/dashboard/ejecutivo")
        .then((d) => {
          setKpis(d.kpis);
          setSemaforo(d.semaforo ?? []);
        })
        .catch(() => {});
    } else if (TEAM_ROLES.includes(role)) {
      api.get<{ kpis: KPICardData[] }>("/api/dashboard/mi-division")
        .then((d) => setKpis(d.kpis))
        .catch(() => {});
    } else if (PROGRESS_ROLES.includes(role)) {
      api.get<{ kpis: KPICardData[] }>("/api/dashboard/mis-compromisos")
        .then((d) => setKpis(d.kpis))
        .catch(() => {});
    }
  }, [role]);

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-64 bg-muted animate-pulse rounded" />
        <div className="h-4 w-48 bg-muted animate-pulse rounded" />
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-28 bg-muted animate-pulse rounded-lg" />
          ))}
        </div>
        <div className="h-32 bg-muted animate-pulse rounded-lg" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 animate-in fade-in duration-300">
      {/* 1. Contextual greeting */}
      <div>
        <h1 className="text-2xl font-bold">
          Buenos días, {actionData?.greeting_name ?? "usuario"}
        </h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          {formatDateLong(new Date().toISOString())} — {actionData?.summary ?? "Cargando..."}
        </p>
      </div>

      {/* 2. Attention strip */}
      {actionData && <AttentionStrip items={actionData.items} />}

      {/* 3. Conditional module */}
      {role && PROGRESS_ROLES.includes(role) && <ModuleMyProgress />}
      {role && TEAM_ROLES.includes(role) && <ModuleMyTeam />}
      {role && DGI_TEAM_ROLES.includes(role) && <ModuleDgiTeam />}
      {/* INDICATOR_ROLES and PANORAMA_ROLES get KPIs below — no separate module */}

      {/* 4. Compact KPIs + semáforo */}
      <ModuleKpis kpis={kpis} semaforo={semaforo} />
    </div>
  );
}
```

- [ ] **Step 2: Verify build**

Run: `cd web && npx next build`
Expected: Build succeeds

- [ ] **Step 3: Commit**

```bash
git add web/src/app/\(app\)/dashboard/components/command-center.tsx
git commit -m "feat(ui): add CommandCenter orchestrator — unified dashboard entry point"
```

---

### Task 8: Wire `page.tsx` to CommandCenter

**Files:**
- Modify: `web/src/app/(app)/dashboard/page.tsx`

**Context:**
- Currently: routes `dgi` population to `DgiCockpitRouter`, operativa to `OperationalDashboard`
- After: ALL roles go to `CommandCenter`. Existing components kept for sidebar deep-dive access.

- [ ] **Step 1: Update page.tsx**

Replace the entire content of `web/src/app/(app)/dashboard/page.tsx`:

```tsx
"use client";

import { useAuth } from "@/lib/auth";
import { PageSkeleton } from "@/components/page-skeleton";
import { CommandCenter } from "./components/command-center";

export default function DashboardPage() {
  const { user, loading } = useAuth();

  if (loading) return <PageSkeleton variant="dashboard" />;
  if (!user) return null;

  return <CommandCenter />;
}
```

- [ ] **Step 2: Verify build**

Run: `cd web && npx next build`
Expected: Build succeeds, 0 TypeScript errors. The old `OperationalDashboard` and `DgiCockpitRouter` components remain in the `components/` directory (accessible via sidebar for specialized cockpit views).

- [ ] **Step 3: Verify API tests still pass**

Run: `docker compose exec api pytest tests/test_action_items.py tests/test_dashboard.py -v`
Expected: All tests pass (no backend changes in this step)

- [ ] **Step 4: Commit**

```bash
git add web/src/app/\(app\)/dashboard/page.tsx
git commit -m "feat(dashboard): wire page.tsx to CommandCenter — unified entry for all 16 roles"
```

---

## Chunk 3: Capa 2 — Densidad Visual + Detail Template

### Task 9: Progress Cell Component

**Files:**
- Create: `web/src/components/progress-cell.tsx`

- [ ] **Step 1: Create the component**

```tsx
interface ProgressCellProps {
  value: number;  // 0-100
  label?: string;
}

export function ProgressCell({ value, label }: ProgressCellProps) {
  const pct = Math.max(0, Math.min(100, value));
  const color = pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-amber-500" : "bg-red-500";

  return (
    <div className="flex items-center gap-2 min-w-[80px]">
      <div className="flex-1 h-2 rounded-full bg-muted">
        <div
          className={`h-full rounded-full ${color} transition-all`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs tabular-nums text-muted-foreground w-9 text-right">
        {label ?? `${Math.round(pct)}%`}
      </span>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add web/src/components/progress-cell.tsx
git commit -m "feat(ui): add ProgressCell — inline progress bar for DataTable columns"
```

---

### Task 10: Deadline Cell Component

**Files:**
- Create: `web/src/components/deadline-cell.tsx`

- [ ] **Step 1: Create the component**

```tsx
import { formatDate } from "@/lib/format";

interface DeadlineCellProps {
  date: string | null;
  daysRemaining?: number | null;
}

export function DeadlineCell({ date: dateStr, daysRemaining }: DeadlineCellProps) {
  if (!dateStr) return <span className="text-muted-foreground text-xs">—</span>;

  const dr = daysRemaining ?? Math.round(
    (new Date(dateStr).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  );

  const color =
    dr < 0 ? "text-red-600 dark:text-red-400" :
    dr <= 7 ? "text-amber-600 dark:text-amber-400" :
    "text-muted-foreground";

  const badge =
    dr < 0 ? `${Math.abs(dr)}d vencido` :
    dr === 0 ? "Hoy" :
    dr <= 7 ? `${dr}d` :
    null;

  return (
    <div className="flex items-center gap-1.5">
      <span className={`text-sm ${color}`}>{formatDate(dateStr)}</span>
      {badge && (
        <span className={`text-[10px] font-medium ${color}`}>({badge})</span>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add web/src/components/deadline-cell.tsx
git commit -m "feat(ui): add DeadlineCell — date + semáforo color for DataTable columns"
```

---

### Task 11: Trend Indicator Component

**Files:**
- Create: `web/src/components/trend-indicator.tsx`

- [ ] **Step 1: Create the component**

```tsx
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface TrendIndicatorProps {
  direction: "up" | "down" | "flat";
  label?: string;
}

export function TrendIndicator({ direction, label }: TrendIndicatorProps) {
  const config = {
    up: { icon: TrendingUp, color: "text-green-600 dark:text-green-400" },
    down: { icon: TrendingDown, color: "text-red-600 dark:text-red-400" },
    flat: { icon: Minus, color: "text-muted-foreground" },
  }[direction];

  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1 ${config.color}`}>
      <Icon className="size-3.5" />
      {label && <span className="text-xs">{label}</span>}
    </span>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add web/src/components/trend-indicator.tsx
git commit -m "feat(ui): add TrendIndicator — arrow + color for trend columns"
```

---

### Task 12: Detail Page Layout Component

**Files:**
- Create: `web/src/components/detail-page-layout.tsx`

**Context:**
- Opt-in wrapper that standardizes hero + stepper + transition + content structure
- Mirrors `ipr-phase-stepper.tsx` pattern: display-only stepper, FSM interaction via `transitionPanel` slot
- `breadcrumbLabel` constructs breadcrumbs from pathname via `buildBreadcrumbs`

- [ ] **Step 1: Create the component**

```tsx
import { ReactNode } from "react";
import { CheckCircle2 } from "lucide-react";
import { Breadcrumb } from "@/components/breadcrumb";
import { buildBreadcrumbs } from "@/lib/breadcrumbs";

interface DetailPageLayoutProps {
  pathname: string;
  breadcrumbLabel?: string;
  heroContent: ReactNode;
  stepper?: {
    phases: { code: string; label: string }[];
    currentPhase: string;
    phaseColors?: Record<string, string>;
  };
  transitionPanel?: ReactNode;
  children: ReactNode;
}

const DEFAULT_PHASE_COLORS: Record<string, string> = {
  past: "bg-green-500",
  active: "bg-blue-600",
  future: "bg-muted",
};

export function DetailPageLayout({
  pathname,
  breadcrumbLabel,
  heroContent,
  stepper,
  transitionPanel,
  children,
}: DetailPageLayoutProps) {
  const breadcrumbs = buildBreadcrumbs(pathname, breadcrumbLabel);

  return (
    <div className="p-6 space-y-4">
      <Breadcrumb items={breadcrumbs} />

      {/* Hero */}
      {heroContent}

      {/* Stepper (display-only) */}
      {stepper && (
        <div className="flex items-center gap-1 overflow-x-auto py-2">
          {stepper.phases.map((phase, idx) => {
            const currentIdx = stepper.phases.findIndex(p => p.code === stepper.currentPhase);
            const isPast = idx < currentIdx;
            const isActive = idx === currentIdx;
            const colors = stepper.phaseColors ?? {};

            const dotColor = isPast
              ? (colors[phase.code] ?? DEFAULT_PHASE_COLORS.past)
              : isActive
                ? (colors[phase.code] ?? DEFAULT_PHASE_COLORS.active)
                : DEFAULT_PHASE_COLORS.future;

            return (
              <div key={phase.code} className="flex items-center gap-1">
                {idx > 0 && <div className={`h-0.5 w-4 ${isPast ? "bg-green-500" : "bg-muted"}`} />}
                <div className="flex items-center gap-1.5 shrink-0">
                  {isPast ? (
                    <CheckCircle2 className="size-4 text-green-600" />
                  ) : (
                    <div className={`size-3 rounded-full ${dotColor} ${isActive ? "ring-2 ring-offset-2 ring-blue-300" : ""}`} />
                  )}
                  <span className={`text-xs whitespace-nowrap ${isActive ? "font-semibold" : "text-muted-foreground"}`}>
                    {phase.label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Transition panel slot */}
      {transitionPanel}

      {/* Content (tabs, forms, etc.) */}
      {children}
    </div>
  );
}
```

- [ ] **Step 2: Verify build**

Run: `cd web && npx next build`
Expected: Build succeeds, 0 TypeScript errors

- [ ] **Step 3: Commit**

```bash
git add web/src/components/detail-page-layout.tsx
git commit -m "feat(ui): add DetailPageLayout — opt-in wrapper for detail pages with stepper"
```

---

### Task 13: Integrate Table Enrichment into List Pages

**Files:**
- Modify: `web/src/app/(app)/presupuesto/page.tsx` (ProgressCell for execution_pct)
- Modify: `web/src/app/(app)/compromisos/page.tsx` (DeadlineCell for due_date)
- Modify: `web/src/app/(app)/convenios/page.tsx` (DeadlineCell for valid_to)
- Modify: `web/src/app/(app)/escalamiento/page.tsx` (DeadlineCell for deadline)
- Modify: `web/src/app/(app)/riesgos/page.tsx` (DeadlineCell — no deadline, skip if not applicable)
- Modify: `web/src/app/(app)/rendiciones/page.tsx` (DeadlineCell for SLA deadline)

**Pattern**: For each page, find the column definition for execution/deadline and replace the plain render function with the new component.

- [ ] **Step 1: Presupuesto — replace execution_pct column render**

In `web/src/app/(app)/presupuesto/page.tsx`:
1. Add import: `import { ProgressCell } from "@/components/progress-cell";`
2. Find the `execution_pct` column and replace its render function with:
   ```tsx
   render: (pct: number) => <ProgressCell value={pct ?? 0} />
   ```

- [ ] **Step 2: Compromisos — replace due_date column render**

In `web/src/app/(app)/compromisos/page.tsx`:
1. Add import: `import { DeadlineCell } from "@/components/deadline-cell";`
2. Find the column for `due_date` and update its render to:
   ```tsx
   render: (val: string, row: CompromisoListItem) => (
     <DeadlineCell date={val} daysRemaining={row.days_remaining} />
   )
   ```

- [ ] **Step 3: Convenios — replace valid_to or expiry column**

In `web/src/app/(app)/convenios/page.tsx`:
1. Add import: `import { DeadlineCell } from "@/components/deadline-cell";`
2. Find the expiry/validity date column and replace its render with `<DeadlineCell>`.

- [ ] **Step 4: Escalamiento — replace deadline column**

In `web/src/app/(app)/escalamiento/page.tsx`:
1. Add import: `import { DeadlineCell } from "@/components/deadline-cell";`
2. Replace deadline column render with `<DeadlineCell date={val} />`.

- [ ] **Step 5: Rendiciones — replace SLA deadline column**

In `web/src/app/(app)/rendiciones/page.tsx`:
1. Add import: `import { DeadlineCell } from "@/components/deadline-cell";`
2. Replace the SLA/due date column render with `<DeadlineCell>`.

- [ ] **Step 6: Verify build**

Run: `cd web && npx next build`
Expected: Build succeeds, 0 TypeScript errors

- [ ] **Step 7: Commit**

```bash
git add web/src/app/\(app\)/presupuesto/page.tsx web/src/app/\(app\)/compromisos/page.tsx \
  web/src/app/\(app\)/convenios/page.tsx web/src/app/\(app\)/escalamiento/page.tsx \
  web/src/app/\(app\)/rendiciones/page.tsx
git commit -m "feat(ui): integrate ProgressCell and DeadlineCell into 5 list pages"
```

---

## Chunk 4: Capa 3 — Identidad por Dominio

### Task 14: Extend PageHeader with `accentColor` Prop

**Files:**
- Modify: `web/src/components/page-header.tsx`

- [ ] **Step 1: Add accentColor prop**

Update `page-header.tsx` to support optional accent color:

```tsx
import { ReactNode } from "react";
import { Breadcrumb } from "@/components/breadcrumb";
import type { BreadcrumbItem } from "@/lib/breadcrumbs";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  breadcrumbs?: BreadcrumbItem[];
  accentColor?: string;  // Tailwind color name: "indigo", "amber", "emerald", etc.
}

const ACCENT_BORDER: Record<string, string> = {
  indigo: "border-l-indigo-500",
  amber: "border-l-amber-500",
  emerald: "border-l-emerald-500",
  violet: "border-l-violet-500",
  rose: "border-l-rose-500",
  cyan: "border-l-cyan-500",
  teal: "border-l-teal-500",
};

export function PageHeader({ title, description, actions, breadcrumbs, accentColor }: PageHeaderProps) {
  // Use mapping to avoid dynamic Tailwind class purging issues
  const borderClass = accentColor
    ? `border-l-4 ${ACCENT_BORDER[accentColor] ?? ""} pl-3`
    : "";

  return (
    <div className="animate-in fade-in duration-300">
      {breadcrumbs && <Breadcrumb items={breadcrumbs} />}
      <div className={`flex items-center justify-between ${borderClass}`}>
        <div>
          <h1 className="text-2xl font-bold">{title}</h1>
          {description && (
            <p className="text-muted-foreground text-sm mt-1">{description}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify build**

Run: `cd web && npx next build`
Expected: Build succeeds

- [ ] **Step 3: Commit**

```bash
git add web/src/components/page-header.tsx
git commit -m "feat(ui): add accentColor prop to PageHeader — domain identity via left border"
```

---

### Task 15: Apply Domain Accents to 15 List Pages + Empty States

**Files:**
- Modify: 15 list pages (add `accentColor` prop to `<PageHeader>`)
- Modify: ~10 pages (update EmptyState descriptions)

**Domain → Color Mapping** (from spec):

| Domain | accentColor | Pages |
|--------|------------|-------|
| IPR / Cartera | `"indigo"` | `ipr/page.tsx`, `cartera/page.tsx` (if DGI) |
| Compromisos / Problemas | `"amber"` | `compromisos/page.tsx`, `problemas/page.tsx` |
| Finanzas | `"emerald"` | `presupuesto/page.tsx`, `presupuesto/ciclo/page.tsx`, `convenios/page.tsx`, `rendiciones/page.tsx` |
| Institucional | `"violet"` | `actos/page.tsx`, `reuniones/page.tsx`, `core-sessions/page.tsx` |
| Riesgos / Crisis | `"rose"` | `riesgos/page.tsx`, `centro-de-mando/page.tsx`, `escalamiento/page.tsx` |
| DGI Análisis | `"cyan"` | `datos/page.tsx`, `informes/page.tsx`, `tablero/page.tsx`, `procesos/page.tsx` |
| Servicios | `"teal"` | `servicios/page.tsx` |

- [ ] **Step 1: Add accentColor to each PageHeader call**

For each page listed above, find the `<PageHeader` call and add the `accentColor` prop. Example:

```tsx
// In compromisos/page.tsx
<PageHeader
  title="Compromisos"
  description="Gestión de compromisos operativos"
  accentColor="amber"
  actions={...}
/>
```

Repeat for all 15 pages with the color from the mapping table.

- [ ] **Step 2: Update EmptyState descriptions**

In pages that use `<EmptyState title="No hay datos">`, add domain-specific `description` prop. Examples:

| Page | Updated EmptyState |
|------|-------------------|
| `compromisos` | `description="Los compromisos asignados aparecerán aquí"` |
| `problemas` | `description="Los problemas reportados aparecerán aquí"` |
| `convenios` | `description="Los convenios registrados aparecerán aquí"` |
| `presupuesto` | `description="Los programas presupuestarios aparecerán aquí"` |
| `rendiciones` | `description="Las rendiciones de cuentas aparecerán aquí"` |
| `actos` | `description="Los actos administrativos aparecerán aquí"` |
| `riesgos` | `description="Los riesgos registrados aparecerán aquí"` |
| `escalamiento` | `description="Los escalamientos activos aparecerán aquí"` |
| `servicios` | `description="El catálogo de servicios DGI aparecerá aquí"` |
| `reuniones` | `description="Las reuniones de crisis aparecerán aquí"` |

- [ ] **Step 3: Verify build**

Run: `cd web && npx next build`
Expected: Build succeeds, 0 TypeScript errors

- [ ] **Step 4: Commit**

```bash
git add web/src/app/\(app\)/*/page.tsx
git commit -m "feat(ui): apply domain color accents to 15 list pages + contextual empty states"
```

---

## Final Verification

### Task 16: End-to-End Verification

- [ ] **Step 1: Full frontend build**

Run: `cd web && npx next build`
Expected: 0 TypeScript errors, all 55+ pages compile

- [ ] **Step 2: Full API test suite**

Run: `docker compose exec api pytest -v`
Expected: All tests pass (568+ existing + 9 new action-items tests)

- [ ] **Step 3: Visual smoke test checklist**

Open browser and test each archetype:

| User | Expected |
|------|----------|
| `encargado.daf@goreos.cl` | Centro de Comando with greeting, attention strip (own commitments), "Mi Progreso" module |
| `jefe.daf@goreos.cl` | Centro de Comando with "Mi Equipo" module, team load grid |
| `regional@goreos.cl` | Centro de Comando with "Panorama" module, KPIs + semáforo, all action-items |
| `jefe.dgi@goreos.cl` | Centro de Comando with "Equipo DGI" module, AR decisions in attention strip |
| `control.gestion@goreos.cl` | Centro de Comando with KPIs (Indicadores), SLA items if any |

- [ ] **Step 4: Check domain accents**

Navigate to at least 5 list pages and verify:
- Indigo left border on `/ipr`
- Amber left border on `/compromisos`
- Emerald left border on `/presupuesto`
- Rose left border on `/riesgos`
- Violet left border on `/actos`

- [ ] **Step 5: Check table enrichment**

- `/presupuesto` → progress bars in execution column
- `/compromisos` → deadline semáforo colors (red for overdue, amber for ≤7d)

- [ ] **Step 6: Responsive check**

Resize browser to 375px width → Centro de Comando cards stack vertically, modules stack, no horizontal overflow.

---

## Summary

| Chunk | Tasks | New files | Modified files |
|:-----:|:-----:|:---------:|:--------------:|
| 1 — Backend | 1-3 | 1 test file | 2 (schemas + router) |
| 2 — Frontend L1 | 4-8 | 6 components | 2 (types + page.tsx) |
| 3 — L2 | 9-13 | 4 components | 5 list pages |
| 4 — L3 | 14-15 | 0 | 16 (page-header + 15 pages) |
| Verify | 16 | 0 | 0 |
| **Total** | **16** | **11** | **25** |
