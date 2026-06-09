# GORE_OS — Developer Onboarding

> Para referencia completa (arquitectura, modelo, reglas): ver [../CLAUDE.md](../CLAUDE.md)

## Arquitectura

```
┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│   Next.js 16          │────▶│   FastAPI             │────▶│   PostgreSQL 16      │
│   :3000  (web/)       │     │   :8000  (api/)       │     │   goreos_db          │
│   App Router + TS     │     │   SQLAlchemy async    │     │   121 tablas, 4 schemas│
└──────────────────────┘     └──────────────────────┘     └──────────────────────┘
```

Dos poblaciones comparten la misma DB:
- **Operativa** (ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, ANALISTA, RTF, ASESOR_JURIDICO): IPRs, compromisos, problemas, alertas, presupuesto, convenios, actos administrativos.
- **DGI** (JEFE_DGI, ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD): indicadores, iniciativas de mejora, reportes.

Login único → detección de rol → routing a sidebar/dashboard.

---

## Setup Local en 5 Minutos

```bash
# 1. Levantar servicios (asume goreos_db corriendo en red visor_model_default)
docker compose up -d api web

# 2. Verificar
curl http://localhost:8000/api/health     # → {"status": "ok"}
curl -I http://localhost:3000             # → 307 redirect a /login

# 3. Explorar API
open http://localhost:8000/api/docs

# 4. Login con usuarios de prueba (ver CLAUDE.md §Test Users)
# Todas las passwords: admin123
```

### Usuarios de prueba rápidos

| Email | Rol | Población |
|-------|-----|-----------|
| `admin@goreos.cl` | ADMIN_SISTEMA | operativa |
| `regional@goreos.cl` | ADMIN_REGIONAL | operativa |
| `jefe.daf@goreos.cl` | JEFE_DIVISION | operativa |
| `analista.dipir@goreos.cl` | ANALISTA | operativa |
| `jefe.dgi@goreos.cl` | JEFE_DGI | dgi |
| `control.gestion@goreos.cl` | ESP_CONTROL_GESTION | dgi |

---

## Patrones Clave

### 1. Raw SQL — sin ORM
Todas las queries usan SQLAlchemy `text()` directamente. Ver [ADR-002](adr/ADR-002-raw-sql.md).

```python
rows = await db.execute(
    text("SELECT id, name FROM core.ipr WHERE deleted_at IS NULL LIMIT :lim"),
    {"lim": 10},
)
items = rows.mappings().all()
```

### 2. Vocabularios controlados — ref.category
Todos los FK apuntan a `ref.category(scheme, code, label)`. El `scheme` identifica el vocabulario. Nunca mezclar schemes en un mismo FK (Univocidad Categorial). Ver [ADR-004](adr/ADR-004-category-pattern.md).

### 3. Restricción de roles
Usar `_require_roles(user, ...)` dentro del body del endpoint. **No** usar como default parameter (conflicto con `CurrentUser`).

### 4. Formato en frontend
Todo formato de fecha/moneda usa `import { formatDate, formatCLP } from "@/lib/format"`. Nunca definir funciones locales de formato.

### 5. Selects de datasets grandes
`core.ipr` tiene 3,600+ filas, `core.organization` 3,300+. Nunca cargar en un `<Select>`. Usar `ComboboxAsync` con búsqueda server-side.

---

## Cómo Agregar una Nueva Feature

1. **Schema** — Agregar/modificar tablas en `model/model_goreos/sql/` como migración (`goreos_migration_waveN_feature.sql`). Crear rollback.
2. **Pydantic schemas** — Crear `api/app/schemas/feature.py` con modelos request/response.
3. **Router** — Crear `api/app/routers/feature.py`. Registrarlo en `api/app/main.py`.
4. **Test** — Crear `api/tests/test_feature.py`. Reconstruir test DB si cambió schema.
5. **Tipos frontend** — Agregar interfaces TypeScript a `web/src/types/index.ts`.
6. **Página/componente** — Crear bajo `web/src/app/(app)/feature/`. Usar `ApiClient` de `web/src/lib/api.ts`.
7. **Sidebar** — Agregar nav item a `web/src/components/sidebar.tsx` si aplica.

Después de cambios backend: `docker compose restart api`.

---

## Migraciones

```bash
./scripts/run_migrations.sh model/model_goreos/sql/goreos_migration_waveN_feature.sql
./scripts/run_migrations.sh model/model_goreos/sql/goreos_rollback_waveN_feature.sql
./scripts/setup_test_db.sh    # Reconstruir test DB tras cambios de schema
```

---

## Testing

```bash
./scripts/setup_test_db.sh                                          # Setup test DB
docker compose exec api pytest -v                                   # Suite completa
docker compose exec api pytest tests/test_compromisos.py -v         # Un módulo
docker compose exec api pytest tests/test_auth.py::test_login_success -v  # Un test
```

**730 tests de integración (55 módulos)** contra PostgreSQL real (`goreos_test`). Sin mocks. Ver [ADR-005](adr/ADR-005-test-strategy.md).
