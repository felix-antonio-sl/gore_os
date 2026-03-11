# Nuevos Roles para Ciclo de Vida IPR — Plan de Implementación

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar 3 nuevos roles de sistema (ANALISTA, RTF, ASESOR_JURIDICO) con permisos granulares para cubrir 100% del ciclo de vida IPR en GORE_OS.

**Architecture:** Los 3 roles se insertan en `ref.category` scheme `system_role` (patrón existente). Se actualizan los conjuntos de roles en `security.py` (backend) y `types/index.ts` (frontend). Se modifican `_require_roles()` en routers clave. Se crean 4 usuarios de test y 3 fixtures de token. Un nuevo módulo de tests valida que los nuevos roles acceden/rechazan los endpoints correctos.

**Tech Stack:** PostgreSQL (migration SQL), FastAPI (routers), pytest + httpx (tests), SQLAlchemy async, TypeScript (frontend types)

**Prerequisitos:** Migration debe aplicarse a `goreos_model` ANTES de reconstruir `goreos_test` (el test DB copia `ref.category` via `COPY FROM`).

---

## Chunk 1: Base de datos y roles

### Task 1: Migration SQL — 3 nuevos roles + 4 usuarios de test

**Files:**
- Create: `model/model_goreos/sql/goreos_migration_new_roles.sql`
- Create: `model/model_goreos/sql/goreos_rollback_new_roles.sql`

- [ ] **Step 1: Escribir migration SQL**

```sql
-- ============================================================================
-- GORE_OS — Migración: 3 nuevos roles para ciclo de vida IPR
-- ============================================================================
-- ANALISTA (13): Formula IPR, admisibilidad, evaluación (F0-F3)
-- RTF (14): Referente Técnico-Financiero, revisión SISREC (F5)
-- ASESOR_JURIDICO (15): V.B. legalidad actos y convenios (F4)
--
-- Prerequisito: Ejecutar contra goreos_model
--   docker exec -i goreos_db psql -U goreos -d goreos_model < goreos_migration_new_roles.sql
--
-- Rollback: goreos_rollback_new_roles.sql
-- ============================================================================

BEGIN;

-- ── Op 1: 3 nuevos system_role ──────────────────────────────────────────────

INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES
  ('system_role', 'ANALISTA', 'Analista',
   'Formula IPR, ejecuta admisibilidad, registra evaluaciones, carga documentos.', 13),
  ('system_role', 'RTF', 'Referente Técnico-Financiero',
   'Revisa rendiciones SISREC, observa/aprueba, controla SLAs.', 14),
  ('system_role', 'ASESOR_JURIDICO', 'Asesor Jurídico',
   'V.B. legalidad de actos administrativos y convenios.', 15)
ON CONFLICT (scheme, code) DO NOTHING;

-- ── Op 2: Personas para usuarios de test ────────────────────────────────────

INSERT INTO core.person (id, names, paternal_surname, email, is_active)
VALUES
  ('a0000001-0000-0000-0000-000000000010', 'Felipe', 'Morales', 'analista.dipir@goreos.cl', true),
  ('a0000001-0000-0000-0000-000000000011', 'Claudia', 'Sepúlveda', 'analista.diplade@goreos.cl', true),
  ('a0000001-0000-0000-0000-000000000012', 'Diego', 'Fuentes', 'rtf.daf@goreos.cl', true),
  ('a0000001-0000-0000-0000-000000000013', 'Valentina', 'Bravo', 'juridico@goreos.cl', true)
ON CONFLICT (id) DO NOTHING;

-- ── Op 3: Usuarios de test ──────────────────────────────────────────────────

DO $$
DECLARE
    v_analista UUID;
    v_rtf UUID;
    v_juridico UUID;
    v_dipir UUID;
    v_diplade UUID;
    v_daf UUID;
    v_hash TEXT := '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe';
BEGIN
    SELECT id INTO v_analista FROM ref.category WHERE scheme='system_role' AND code='ANALISTA';
    SELECT id INTO v_rtf FROM ref.category WHERE scheme='system_role' AND code='RTF';
    SELECT id INTO v_juridico FROM ref.category WHERE scheme='system_role' AND code='ASESOR_JURIDICO';

    SELECT id INTO v_dipir FROM core.organization WHERE code='DIPIR';
    SELECT id INTO v_diplade FROM core.organization WHERE code='DIPLADE';
    SELECT id INTO v_daf FROM core.organization WHERE code='DAF';

    -- Analista DIPIR
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000010', 'analista.dipir@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000010', v_analista, v_dipir, true)
    ON CONFLICT (id) DO NOTHING;

    -- Analista DIPLADE
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000011', 'analista.diplade@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000011', v_analista, v_diplade, true)
    ON CONFLICT (id) DO NOTHING;

    -- RTF DAF
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000012', 'rtf.daf@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000012', v_rtf, v_daf, true)
    ON CONFLICT (id) DO NOTHING;

    -- Asesor Jurídico (sin división — staff unit)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000013', 'juridico@goreos.cl', v_hash,
            'a0000001-0000-0000-0000-000000000013', v_juridico, true)
    ON CONFLICT (id) DO NOTHING;

    RAISE NOTICE 'New roles + test users seeded: 3 roles, 4 users';
END $$;

-- ── Op 4: Registrar migración ───────────────────────────────────────────────

INSERT INTO core.schema_migration (version, description)
VALUES ('roles_ipr_lifecycle', '3 new system roles: ANALISTA, RTF, ASESOR_JURIDICO + 4 test users')
ON CONFLICT (version) DO NOTHING;

COMMIT;
```

- [ ] **Step 2: Escribir rollback SQL**

```sql
-- Rollback: goreos_rollback_new_roles.sql
BEGIN;

DELETE FROM core."user" WHERE email IN (
    'analista.dipir@goreos.cl', 'analista.diplade@goreos.cl',
    'rtf.daf@goreos.cl', 'juridico@goreos.cl'
);
DELETE FROM core.person WHERE id IN (
    'a0000001-0000-0000-0000-000000000010',
    'a0000001-0000-0000-0000-000000000011',
    'a0000001-0000-0000-0000-000000000012',
    'a0000001-0000-0000-0000-000000000013'
);
DELETE FROM ref.category WHERE scheme = 'system_role'
    AND code IN ('ANALISTA', 'RTF', 'ASESOR_JURIDICO');
DELETE FROM core.schema_migration WHERE version = 'roles_ipr_lifecycle';

COMMIT;
```

- [ ] **Step 3: Aplicar migration a goreos_model**

Run: `docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_migration_new_roles.sql`
Expected: `NOTICE: New roles + test users seeded: 3 roles, 4 users`

- [ ] **Step 4: Commit**

```bash
git add model/model_goreos/sql/goreos_migration_new_roles.sql model/model_goreos/sql/goreos_rollback_new_roles.sql
git commit -m "feat(db): add ANALISTA, RTF, ASESOR_JURIDICO roles + test users"
```

### Task 2: Actualizar goreos_seed_users.sql con los 4 nuevos usuarios

**Files:**
- Modify: `model/model_goreos/sql/goreos_seed_users.sql`

- [ ] **Step 1: Agregar personas al INSERT de core.person**

Reemplazar la última línea del INSERT de `core.person` (línea 15, la del consejero que termina en `;`) por:

```sql
('a0000001-0000-0000-0000-000000000009','Luis','Henríquez','consejero@goreos.cl',true),
('a0000001-0000-0000-0000-000000000010','Felipe','Morales','analista.dipir@goreos.cl',true),
('a0000001-0000-0000-0000-000000000011','Claudia','Sepúlveda','analista.diplade@goreos.cl',true),
('a0000001-0000-0000-0000-000000000012','Diego','Fuentes','rtf.daf@goreos.cl',true),
('a0000001-0000-0000-0000-000000000013','Valentina','Bravo','juridico@goreos.cl',true);
```

- [ ] **Step 2: Agregar variables de roles nuevos al DECLARE**

Después de `v_consejero UUID;` (línea 29), agregar:

```sql
    v_analista UUID;
    v_rtf UUID;
    v_juridico UUID;
    v_dipir UUID;
    v_diplade UUID;
```

Nota: `v_daf` ya existe en línea 30.

- [ ] **Step 3: Agregar lookups de roles nuevos al BEGIN**

Después del SELECT para consejero (línea 44), agregar:

```sql
    SELECT id INTO v_analista FROM ref.category WHERE scheme='system_role' AND code='ANALISTA';
    SELECT id INTO v_rtf FROM ref.category WHERE scheme='system_role' AND code='RTF';
    SELECT id INTO v_juridico FROM ref.category WHERE scheme='system_role' AND code='ASESOR_JURIDICO';
    SELECT id INTO v_dipir FROM core.organization WHERE code='DIPIR';
    SELECT id INTO v_diplade FROM core.organization WHERE code='DIPLADE';
```

- [ ] **Step 4: Agregar INSERTs de usuarios**

Después del INSERT del Consejero Regional (línea 88), agregar:

```sql
    -- Analista DIPIR
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000010','analista.dipir@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000010',v_analista,v_dipir,true);

    -- Analista DIPLADE
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000011','analista.diplade@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000011',v_analista,v_diplade,true);

    -- RTF DAF
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, division_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000012','rtf.daf@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000012',v_rtf,v_daf,true);

    -- Asesor Jurídico (sin división)
    INSERT INTO core."user" (id, email, password_hash, person_id, system_role_id, is_active)
    VALUES ('b0000001-0000-0000-0000-000000000013','juridico@goreos.cl',v_hash,'a0000001-0000-0000-0000-000000000013',v_juridico,true);
```

- [ ] **Step 5: Actualizar RAISE NOTICE**

Cambiar `'Test users seeded: 10 users'` → `'Test users seeded: 14 users'`

- [ ] **Step 6: Commit**

```bash
git add model/model_goreos/sql/goreos_seed_users.sql
git commit -m "feat(db): add ANALISTA, RTF, ASESOR_JURIDICO test users to seed"
```

---

## Chunk 2: Backend — Conjuntos de roles y fixtures

### Task 3: Actualizar security.py con los 3 nuevos roles

**Files:**
- Modify: `api/app/core/security.py:8-18`

- [ ] **Step 1: Actualizar OPERATIONAL_ROLES (líneas 8-12)**

```python
OPERATIONAL_ROLES = {
    "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "ENCARGADO",
    "GOBERNADOR", "CONSEJERO_REGIONAL", "SECRETARIO_EJECUTIVO",
    "JEFE_DEPARTAMENTO", "JEFE_UNIDAD",
    "ANALISTA", "RTF", "ASESOR_JURIDICO",
}
```

- [ ] **Step 2: Actualizar WRITE_OPERATIONAL_ROLES (líneas 13-16)**

```python
WRITE_OPERATIONAL_ROLES = {
    "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "ENCARGADO",
    "GOBERNADOR", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD",
    "ANALISTA", "RTF", "ASESOR_JURIDICO",
}
```

- [ ] **Step 3: Verificar ALL_ROLES**

Línea 18: `ALL_ROLES = OPERATIONAL_ROLES | DGI_ROLES` — sin cambio (unión dinámica).

- [ ] **Step 4: Commit**

```bash
git add api/app/core/security.py
git commit -m "feat(auth): add ANALISTA, RTF, ASESOR_JURIDICO to role sets"
```

### Task 4: Agregar token fixtures en conftest.py

**Files:**
- Modify: `api/tests/conftest.py`

- [ ] **Step 1: Agregar 3 nuevos token fixtures**

Insertar después de `consejero_token` (línea 177), antes del bloque "Auth header helpers" (línea 180):

```python
@pytest_asyncio.fixture
async def analista_token(db):
    uid = await _get_user_id(db, "analista.dipir@goreos.cl")
    return create_access_token({"sub": uid, "role": "ANALISTA"})


@pytest_asyncio.fixture
async def rtf_token(db):
    uid = await _get_user_id(db, "rtf.daf@goreos.cl")
    return create_access_token({"sub": uid, "role": "RTF"})


@pytest_asyncio.fixture
async def juridico_token(db):
    uid = await _get_user_id(db, "juridico@goreos.cl")
    return create_access_token({"sub": uid, "role": "ASESOR_JURIDICO"})
```

- [ ] **Step 2: Agregar nuevos usuarios al catalog fixture**

En el fixture `catalog` (línea 244), agregar emails al loop:

```python
    for email in [
        "admin@goreos.cl", "regional@goreos.cl",
        "jefe.daf@goreos.cl", "encargado.daf@goreos.cl",
        "jefe.dgi@goreos.cl",
        "analista.dipir@goreos.cl", "rtf.daf@goreos.cl", "juridico@goreos.cl",
    ]:
```

- [ ] **Step 3: Agregar cleanup obligatorio para tests de nuevos roles**

En el fixture `cleanup_test_artifacts` (después de las líneas de cleanup existentes, antes del `await db.commit()`), agregar:

```python
    # New roles test cleanup (renditions created by RTF tests, then IPRs)
    await db.execute(text("""
        DELETE FROM core.rendition WHERE ipr_id IN (
            SELECT id FROM core.ipr WHERE codigo_bip LIKE 'ROLE-%'
        )
    """))
    await db.execute(text("DELETE FROM core.ipr WHERE codigo_bip LIKE 'ROLE-%'"))
```

- [ ] **Step 4: Commit**

```bash
git add api/tests/conftest.py
git commit -m "feat(tests): add token fixtures for ANALISTA, RTF, ASESOR_JURIDICO"
```

---

## Chunk 3: Backend — Actualizar permisos en routers

### Task 5: Actualizar permisos en ipr.py — ANALISTA

**Files:**
- Modify: `api/app/routers/ipr.py`

- [ ] **Step 1: Actualizar _CREATE_ROLES (línea ~31)**

Cambiar:
```python
_CREATE_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"}
```
Por:
```python
_CREATE_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA"}
```

- [ ] **Step 2: Actualizar _ASSIGN_ROLES (línea ~33)**

Cambiar:
```python
_ASSIGN_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "GOBERNADOR", "JEFE_DEPARTAMENTO"}
```
Por:
```python
_ASSIGN_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "GOBERNADOR", "JEFE_DEPARTAMENTO", "ANALISTA"}
```

- [ ] **Step 3: Actualizar partes, territorio, hitos y evaluaciones**

Buscar todas las llamadas `_require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL")` en los endpoints de satélites y cambiar a:

```python
_require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "ANALISTA")
```

Aplica en estos endpoints (verificar líneas exactas con grep):
- POST `/{ipr_id}/partes`
- DELETE `/{ipr_id}/partes/{party_id}`
- POST `/{ipr_id}/territorio`
- DELETE `/{ipr_id}/territorio/{terr_id}`
- POST `/{ipr_id}/hitos`
- PATCH `/{ipr_id}/hitos/{hito_id}`
- DELETE `/{ipr_id}/hitos/{hito_id}`
- POST `/{ipr_id}/evaluaciones`: cambiar a `"ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "ANALISTA"`

**No cambiar:** parentesco (ADMIN_SISTEMA + ADMIN_REGIONAL — sensibilidad probidad), certificación técnica (roles ya correctos).

- [ ] **Step 4: Verificar comportamiento PATCH IPR para ANALISTA**

En el PATCH IPR (líneas ~2071-2076), el código restringe campos solo para JEFE_DIVISION y JEFE_DEPARTAMENTO:
```python
if role in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO"):
    updates = {k: v for k, v in updates.items() if k == "assignee_id"}
```

ANALISTA **no** está en este check restrictivo, así que tiene acceso a todos los campos del allowlist — esto es correcto: ANALISTA es quien formula y edita datos de la IPR en F0-F3.

- [ ] **Step 5: Commit**

```bash
git add api/app/routers/ipr.py
git commit -m "feat(ipr): add ANALISTA role to IPR creation and satellite management"
```

### Task 6: Actualizar permisos en presupuesto.py — ANALISTA

**Files:**
- Modify: `api/app/routers/presupuesto.py:29`

- [ ] **Step 1: Actualizar ADMIN_ROLES**

Cambiar:
```python
ADMIN_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"}
```
Por:
```python
ADMIN_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA"}
```

Esto da a ANALISTA acceso a: crear CDPs, ver CDPs por IPR, gestionar ciclo presupuestario.

- [ ] **Step 2: Commit**

```bash
git add api/app/routers/presupuesto.py
git commit -m "feat(presupuesto): add ANALISTA to budget admin roles"
```

### Task 7: Verificar actos.py, convenios.py, rendiciones — cobertura automática

**Files:**
- Verify (no modificar): `api/app/routers/actos.py`, `api/app/routers/convenios.py`, `api/app/routers/compromisos.py`, `api/app/routers/problemas.py`, `api/app/routers/alertas.py`

- [ ] **Step 1: Verificar cobertura automática via WRITE_OPERATIONAL_ROLES**

Estos routers usan `WRITE_OPERATIONAL_ROLES` para escritura. Dado que los 3 nuevos roles ya están en ese conjunto (Task 3), automáticamente obtienen:

| Router | Endpoint | Nuevo acceso |
|--------|----------|--------------|
| actos.py | POST/PATCH `/api/actos` | ASESOR_JURIDICO, ANALISTA, RTF |
| convenios.py | POST/PATCH `/api/convenios`, cuotas | ASESOR_JURIDICO, ANALISTA, RTF |
| compromisos.py | PATCH compromisos | ANALISTA, RTF (PATCH usa WRITE_OP) |
| problemas.py | POST/PATCH problemas | ANALISTA, RTF |
| alertas.py | POST atender | ANALISTA, RTF |
| dgi_data.py | Rendiciones CRUD (via _RENDICION_WRITE_ROLES) | RTF |

**Nota sobre compromisos.py:** `POST /api/compromisos` usa `_require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION")` — los 3 nuevos roles **no** pueden crear compromisos. Esto es correcto: crear compromisos es función de gestión, no de análisis.

No se necesitan cambios en estos archivos.

### Task 7b: Autorizar RTF en transiciones SISREC de rendición

**Context (H-04 Auditoría Categórica):** `_RENDICION_TRANSITION_ROLES` en `dgi_data.py:1788-1797` usa `DGI_ROLES` para las transiciones de revisión RTF (visar, observar). RTF es rol operativo, no DGI, así que queda bloqueado de su función ontológica core. La SSOT define al RTF como "Analista Otorgante — revisa/aprueba/observa". Sin este cambio, RTF puede crear/editar rendiciones pero NO ejecutar las transiciones que justifican su existencia.

**Files:**
- Modify: `api/app/routers/dgi_data.py:1788-1797`

- [ ] **Step 1: Actualizar `_RENDICION_TRANSITION_ROLES`**

Cambiar (líneas 1788-1797):
```python
_RENDICION_TRANSITION_ROLES: dict[tuple[str, str], set[str]] = {
    ("PENDIENTE", "EN_REVISION_RTF"):       _RENDICION_WRITE_ROLES,
    ("EN_REVISION_RTF", "OBSERVADA"):       DGI_ROLES,
    ("EN_REVISION_RTF", "VISADA_RTF"):      DGI_ROLES,
    ("VISADA_RTF", "EN_REVISION_UCR"):      DGI_ROLES,
    ("EN_REVISION_UCR", "OBSERVADA"):       DGI_ROLES,
    ("EN_REVISION_UCR", "APROBADA"):        DGI_ROLES,
    ("EN_REVISION_UCR", "RECHAZADA"):       DGI_ROLES,
    ("OBSERVADA", "EN_REVISION_RTF"):       _RENDICION_WRITE_ROLES,
}
```

Por:
```python
# RTF can review in EN_REVISION_RTF phase (visar/observar) — ontological RTF role
_RTF_REVIEW_ROLES = DGI_ROLES | {"RTF"}

_RENDICION_TRANSITION_ROLES: dict[tuple[str, str], set[str]] = {
    ("PENDIENTE", "EN_REVISION_RTF"):       _RENDICION_WRITE_ROLES,
    ("EN_REVISION_RTF", "OBSERVADA"):       _RTF_REVIEW_ROLES,
    ("EN_REVISION_RTF", "VISADA_RTF"):      _RTF_REVIEW_ROLES,
    ("VISADA_RTF", "EN_REVISION_UCR"):      DGI_ROLES,
    ("EN_REVISION_UCR", "OBSERVADA"):       DGI_ROLES,
    ("EN_REVISION_UCR", "APROBADA"):        DGI_ROLES,
    ("EN_REVISION_UCR", "RECHAZADA"):       DGI_ROLES,
    ("OBSERVADA", "EN_REVISION_RTF"):       _RENDICION_WRITE_ROLES,
}
```

**Semántica**: RTF puede visar y observar en la fase que lleva su nombre (EN_REVISION_RTF). Las fases posteriores (UCR, aprobación, rechazo) siguen siendo exclusivas de DGI — son competencia del Jefe DAF y UCR, no del RTF.

- [ ] **Step 2: Commit**

```bash
git add api/app/routers/dgi_data.py
git commit -m "feat(rendiciones): authorize RTF role in SISREC review transitions"
```

---

## Chunk 4: Frontend — Types y Sidebar

### Task 8: Actualizar RoleCode TypeScript type y arrays de roles

**Files:**
- Modify: `web/src/types/index.ts:19-61`

- [ ] **Step 1: Actualizar RoleCode type (líneas 19-32)**

Cambiar:
```typescript
export type RoleCode =
  | "ADMIN_SISTEMA"
  | "ADMIN_REGIONAL"
  | "JEFE_DIVISION"
  | "ENCARGADO"
  | "GOBERNADOR"
  | "CONSEJERO_REGIONAL"
  | "SECRETARIO_EJECUTIVO"
  | "JEFE_DEPARTAMENTO"
  | "JEFE_UNIDAD"
  | "JEFE_DGI"
  | "ESP_CONTROL_GESTION"
  | "ESP_PROCESOS"
  | "ESP_TD";
```
Por:
```typescript
export type RoleCode =
  | "ADMIN_SISTEMA"
  | "ADMIN_REGIONAL"
  | "JEFE_DIVISION"
  | "ENCARGADO"
  | "GOBERNADOR"
  | "CONSEJERO_REGIONAL"
  | "SECRETARIO_EJECUTIVO"
  | "JEFE_DEPARTAMENTO"
  | "JEFE_UNIDAD"
  | "ANALISTA"
  | "RTF"
  | "ASESOR_JURIDICO"
  | "JEFE_DGI"
  | "ESP_CONTROL_GESTION"
  | "ESP_PROCESOS"
  | "ESP_TD";
```

- [ ] **Step 2: Actualizar OPERATIONAL_ROLES array (líneas 34-44)**

Agregar antes del cierre `];`:
```typescript
  "ANALISTA",
  "RTF",
  "ASESOR_JURIDICO",
```

- [ ] **Step 3: Actualizar WRITE_OPERATIONAL_ROLES array (líneas 46-54)**

Agregar antes del cierre `];`:
```typescript
  "ANALISTA",
  "RTF",
  "ASESOR_JURIDICO",
```

- [ ] **Step 4: Commit**

```bash
git add web/src/types/index.ts
git commit -m "feat(ui): add ANALISTA, RTF, ASESOR_JURIDICO to TypeScript role types"
```

### Task 9: Verificar sidebar y population detection

**Files:**
- Verify: `web/src/components/sidebar.tsx`, `web/src/lib/auth.tsx`

- [ ] **Step 1: Verificar population detection**

La población se determina en el backend (`auth.py`) con la lógica: si `role_code in DGI_ROLES` → `"dgi"`, else → `"operativa"`. Los 3 nuevos roles **no** están en `DGI_ROLES`, así que automáticamente son `"operativa"`.

- [ ] **Step 2: Verificar sidebar**

El sidebar muestra `operationalNav` para población operativa. Los 3 nuevos roles verán los mismos 10 ítems de navegación operativa. No necesitan ítems propios.

No se necesitan cambios en sidebar.tsx ni auth.tsx.

- [ ] **Step 3: Verificar build frontend**

Run: `cd web && npx next build`
Expected: Build exitoso sin errores de tipo

- [ ] **Step 4: Commit (si hubo cambios)**

Solo si se necesitaron cambios adicionales.

---

## Chunk 5: Tests

### Task 10: Reconstruir test DB y verificar tests existentes

**Prerequisito:** Task 1 Step 3 (migration aplicada a goreos_model) debe haberse completado.

- [ ] **Step 1: Reconstruir goreos_test con los nuevos usuarios**

Run: `./scripts/setup_test_db.sh`
Expected: Success, incluyendo nuevos test users

- [ ] **Step 2: Ejecutar suite completa de tests**

Run: `docker compose exec api pytest -v --tb=short`
Expected: 484+ pass (tests existentes no deben romperse — los nuevos roles solo amplían permisos)

### Task 11: Escribir tests para los nuevos roles

**Files:**
- Create: `api/tests/test_new_roles.py`

- [ ] **Step 1: Escribir test file completo**

```python
"""Tests for new roles: ANALISTA, RTF, ASESOR_JURIDICO.

Validates that each new role can access its intended endpoints
and is correctly blocked from unauthorized endpoints.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import auth


# ─────────────────────────────────────────────────────────────────────────────
# ANALISTA — F0-F3: Create IPR, manage satellites, create CDPs
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_analista_can_list_ipr(client: AsyncClient, analista_token: str):
    resp = await client.get("/api/ipr", params={"page": 1, "page_size": 1}, headers=auth(analista_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analista_can_create_ipr(client: AsyncClient, analista_token: str, db):
    """ANALISTA should be able to create an IPR (F0 Postulación)."""
    from sqlalchemy import text

    # Get required catalog IDs
    ipr_type = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_type' LIMIT 1")
    )
    ipr_type_id = str(ipr_type.scalar())

    ipr_status = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_status' AND code = 'PRE_ADMISIBLE'")
    )
    status_id = str(ipr_status.scalar())

    resp = await client.post("/api/ipr", json={
        "codigo_bip": "ROLE-TEST-001",
        "name": "Test IPR from ANALISTA",
        "ipr_type_id": ipr_type_id,
        "status_id": status_id,
    }, headers=auth(analista_token))
    assert resp.status_code == 201, resp.text


@pytest.mark.asyncio
async def test_analista_can_list_compromisos(client: AsyncClient, analista_token: str):
    """ANALISTA can list operational commitments."""
    resp = await client.get("/api/compromisos", headers=auth(analista_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analista_cannot_create_compromiso(client: AsyncClient, analista_token: str, catalog: dict):
    """ANALISTA should NOT create commitments (requires JEFE_DIVISION+)."""
    resp = await client.post("/api/compromisos", json={
        "title": "Test commitment",
        "description": "Test",
        "commitment_type_id": catalog["commitment_type_id"],
    }, headers=auth(analista_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_analista_cannot_access_admin(client: AsyncClient, analista_token: str):
    """ANALISTA should NOT access admin endpoints."""
    resp = await client.get("/api/admin/usuarios", headers=auth(analista_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_analista_cannot_access_dgi(client: AsyncClient, analista_token: str):
    """ANALISTA should NOT access DGI-only endpoints."""
    resp = await client.get("/api/dgi/cartera", headers=auth(analista_token))
    assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# RTF — F5: Review rendiciones SISREC
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rtf_can_list_rendiciones(client: AsyncClient, rtf_token: str):
    """RTF should access rendiciones list."""
    resp = await client.get("/api/rendiciones", headers=auth(rtf_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_rtf_can_list_problemas(client: AsyncClient, rtf_token: str):
    """RTF can list problems (via WRITE_OPERATIONAL_ROLES)."""
    resp = await client.get("/api/problemas", headers=auth(rtf_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_rtf_can_transition_rendicion_to_visada(client: AsyncClient, rtf_token: str, db):
    """RTF should be able to visar a rendición in EN_REVISION_RTF (H-04 fix)."""
    from sqlalchemy import text

    # Find a rendition in EN_REVISION_RTF state (or create one)
    state = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'EN_REVISION_RTF'")
    )
    state_rtf_id = state.scalar()
    if state_rtf_id is None:
        pytest.skip("rendition_state EN_REVISION_RTF not seeded")

    visada = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'VISADA_RTF'")
    )
    visada_id = visada.scalar()
    if visada_id is None:
        pytest.skip("rendition_state VISADA_RTF not seeded")

    # Create a rendition directly in EN_REVISION_RTF for testing
    ipr = await db.execute(text("SELECT id FROM core.ipr LIMIT 1"))
    ipr_id = ipr.scalar()
    if ipr_id is None:
        pytest.skip("No IPR in test DB")

    await db.execute(text("""
        INSERT INTO core.rendition (ipr_id, state_id, period_start, period_end, amount)
        VALUES (:ipr_id, :state_id, '2026-01-01', '2026-01-31', 1000000)
        RETURNING id
    """), {"ipr_id": str(ipr_id), "state_id": str(state_rtf_id)})
    await db.commit()

    rend = await db.execute(text(
        "SELECT id FROM core.rendition WHERE state_id = :sid ORDER BY created_at DESC LIMIT 1"
    ), {"sid": str(state_rtf_id)})
    rend_id = str(rend.scalar())

    # RTF should be able to visar (transition EN_REVISION_RTF → VISADA_RTF)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rend_id}",
        json={"state_id": str(visada_id)},
        headers=auth(rtf_token),
    )
    assert resp.status_code == 200, f"RTF should visar rendición: {resp.text}"


@pytest.mark.asyncio
async def test_rtf_cannot_approve_rendicion(client: AsyncClient, rtf_token: str, db):
    """RTF should NOT approve rendiciones (EN_REVISION_UCR → APROBADA is DGI-only)."""
    from sqlalchemy import text

    state_ucr = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'EN_REVISION_UCR'")
    )
    state_ucr_id = state_ucr.scalar()
    if state_ucr_id is None:
        pytest.skip("rendition_state EN_REVISION_UCR not seeded")

    aprobada = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'APROBADA'")
    )
    aprobada_id = aprobada.scalar()

    ipr = await db.execute(text("SELECT id FROM core.ipr LIMIT 1"))
    ipr_id = ipr.scalar()
    if ipr_id is None:
        pytest.skip("No IPR in test DB")

    await db.execute(text("""
        INSERT INTO core.rendition (ipr_id, state_id, period_start, period_end, amount)
        VALUES (:ipr_id, :state_id, '2026-02-01', '2026-02-28', 500000)
        RETURNING id
    """), {"ipr_id": str(ipr_id), "state_id": str(state_ucr_id)})
    await db.commit()

    rend = await db.execute(text(
        "SELECT id FROM core.rendition WHERE state_id = :sid ORDER BY created_at DESC LIMIT 1"
    ), {"sid": str(state_ucr_id)})
    rend_id = str(rend.scalar())

    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rend_id}",
        json={"state_id": str(aprobada_id)},
        headers=auth(rtf_token),
    )
    assert resp.status_code == 403, "RTF should NOT approve rendiciones"


@pytest.mark.asyncio
async def test_rtf_cannot_create_ipr(client: AsyncClient, rtf_token: str, db):
    """RTF should NOT be able to create IPR (not in _CREATE_ROLES)."""
    from sqlalchemy import text

    ipr_type = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_type' LIMIT 1")
    )
    ipr_type_id = str(ipr_type.scalar())

    resp = await client.post("/api/ipr", json={
        "codigo_bip": "ROLE-RTF-001",
        "name": "Test IPR from RTF",
        "ipr_type_id": ipr_type_id,
    }, headers=auth(rtf_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_rtf_cannot_access_admin(client: AsyncClient, rtf_token: str):
    """RTF should NOT access admin endpoints."""
    resp = await client.get("/api/admin/usuarios", headers=auth(rtf_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_rtf_cannot_access_dgi(client: AsyncClient, rtf_token: str):
    """RTF should NOT access DGI-only endpoints."""
    resp = await client.get("/api/dgi/cartera", headers=auth(rtf_token))
    assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# ASESOR_JURIDICO — F4: V.B. legalidad actos y convenios
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_juridico_can_list_convenios(client: AsyncClient, juridico_token: str):
    """ASESOR_JURIDICO should access convenios."""
    resp = await client.get("/api/convenios", headers=auth(juridico_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_juridico_can_list_actos(client: AsyncClient, juridico_token: str):
    """ASESOR_JURIDICO should access administrative acts list."""
    resp = await client.get("/api/actos", headers=auth(juridico_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_juridico_cannot_create_ipr(client: AsyncClient, juridico_token: str, db):
    """ASESOR_JURIDICO should NOT be able to create IPR."""
    from sqlalchemy import text

    ipr_type = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_type' LIMIT 1")
    )
    ipr_type_id = str(ipr_type.scalar())

    resp = await client.post("/api/ipr", json={
        "codigo_bip": "ROLE-JUR-001",
        "name": "Test IPR from JURIDICO",
        "ipr_type_id": ipr_type_id,
    }, headers=auth(juridico_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_juridico_cannot_access_admin(client: AsyncClient, juridico_token: str):
    """ASESOR_JURIDICO should NOT access admin endpoints."""
    resp = await client.get("/api/admin/usuarios", headers=auth(juridico_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_juridico_cannot_access_dgi(client: AsyncClient, juridico_token: str):
    """ASESOR_JURIDICO should NOT access DGI-only endpoints (uses /dgi/cartera which has guard)."""
    resp = await client.get("/api/dgi/cartera", headers=auth(juridico_token))
    assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Cross-role: login verification
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("email", [
    "analista.dipir@goreos.cl",
    "rtf.daf@goreos.cl",
    "juridico@goreos.cl",
])
async def test_new_roles_can_login(client: AsyncClient, email: str):
    """All new role users should be able to login."""
    resp = await client.post("/api/auth/login", data={
        "username": email,
        "password": "admin123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
```

- [ ] **Step 2: Ejecutar los nuevos tests**

Run: `docker compose exec api pytest tests/test_new_roles.py -v`
Expected: 18 tests pass

- [ ] **Step 3: Ejecutar suite completa**

Run: `docker compose exec api pytest -v --tb=short`
Expected: 454+ existing + 18 new = 472+ tests pass

- [ ] **Step 4: Commit**

```bash
git add api/tests/test_new_roles.py
git commit -m "test: add permission tests for ANALISTA, RTF, ASESOR_JURIDICO roles"
```

---

## Chunk 6: Documentación y cierre

### Task 12: Actualizar CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Actualizar sección de System Roles**

Buscar `**System roles** (13)` y cambiar a:
```
**System roles** (16): GOBERNADOR(0), ADMIN_SISTEMA(1), ADMIN_REGIONAL(2), JEFE_DIVISION(3), ENCARGADO(4), JEFE_DGI(5), ESP_CONTROL_GESTION(6), ESP_PROCESOS(7), ESP_TD(8), CONSEJERO_REGIONAL(9), SECRETARIO_EJECUTIVO(10), JEFE_DEPARTAMENTO(11), JEFE_UNIDAD(12), ANALISTA(13), RTF(14), ASESOR_JURIDICO(15).
```

- [ ] **Step 2: Actualizar tabla de Test Users**

Agregar al final de la tabla:
```
| analista.dipir | ANALISTA | op | DIPIR |
| analista.diplade | ANALISTA | op | DIPLADE |
| rtf.daf | RTF | op | DAF |
| juridico | ASESOR_JURIDICO | op | — |
```

- [ ] **Step 3: Actualizar conteo de tests y conftest description**

Actualizar la línea de tests al número final. Cambiar `real JWT for 5 roles` → `real JWT for 8 roles (admin, regional, jefe, encargado, dgi, analista, rtf, juridico)`.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with 3 new roles and test users"
```

### Task 13: Restart servicios y verificación final

- [ ] **Step 1: Restart API**

Run: `docker compose restart api`

- [ ] **Step 2: Verificar login con nuevos usuarios**

```bash
curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=analista.dipir@goreos.cl&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'access_token' in d else 'FAIL')"
```

Repetir para: `rtf.daf@goreos.cl`, `juridico@goreos.cl`, `analista.diplade@goreos.cl`

Expected: `OK` para los 4

- [ ] **Step 3: Ejecutar tests finales**

Run: `docker compose exec api pytest -v --tb=short`
Expected: All pass

---

## Resumen de archivos

| Acción | Archivo | Task |
|--------|---------|------|
| Create | `model/model_goreos/sql/goreos_migration_new_roles.sql` | 1 |
| Create | `model/model_goreos/sql/goreos_rollback_new_roles.sql` | 1 |
| Create | `api/tests/test_new_roles.py` | 11 |
| Modify | `model/model_goreos/sql/goreos_seed_users.sql` | 2 |
| Modify | `api/app/core/security.py` (líneas 8-18) | 3 |
| Modify | `api/tests/conftest.py` (fixtures + catalog + cleanup) | 4 |
| Modify | `api/app/routers/ipr.py` (role constants + _require_roles calls) | 5 |
| Modify | `api/app/routers/presupuesto.py` (ADMIN_ROLES) | 6 |
| Modify | `api/app/routers/dgi_data.py` (_RENDICION_TRANSITION_ROLES) | 7b |
| Modify | `web/src/types/index.ts` (RoleCode + role arrays) | 8 |
| Modify | `CLAUDE.md` (roles, test users, conteo) | 12 |

## Notas de diseño

1. **WRITE_OPERATIONAL_ROLES como puerta amplia**: Los 3 nuevos roles entran a este conjunto. Esto les da acceso a editar compromisos, crear problemas, atender alertas. Las restricciones finas se aplican en routers específicos (ej: `_CREATE_ROLES` en ipr.py excluye RTF y JURIDICO de crear IPR).

2. **No se modifica el FSM de actos/convenios**: Los permisos granulares por transición (ej: solo ASESOR_JURIDICO puede mover EN_REVISION→VISADO) son un cambio arquitectónico mayor. Este plan agrega los roles al sistema; la granularización de transiciones será un plan separado.

3. **RTF en transiciones SISREC (H-04)**: Task 7b resuelve el hallazgo H-04 de la auditoría categórica. `_RTF_REVIEW_ROLES = DGI_ROLES | {"RTF"}` se usa en las 2 transiciones de la fase EN_REVISION_RTF (visar + observar). Fases posteriores (UCR, aprobación) siguen siendo DGI-only.

4. **Population detection automática**: El backend usa `if role_code in DGI_ROLES → "dgi"`, else `"operativa"`. Los 3 nuevos roles caen en `operativa` por exclusión — sin cambios en auth.py.

5. **DIDESO→DIPLADE**: Se usa DIPLADE para el segundo analista de test porque el código `DIDESO` solo existe en producción. El seed de territorio usa `DIDERSO` que no coincide. DIPLADE existe en ambos entornos.

6. **Dashboard fallback**: Los 3 nuevos roles caerán al fallback del dashboard (vista global tipo admin_regional). Esto es aceptable para v1; un dashboard específico por rol sería mejora futura.
