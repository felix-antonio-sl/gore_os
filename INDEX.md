# GORE_OS — Mapa del Repositorio

> **v3.2.0** | **Story-First & Minimalismo Radical** | Fuente de verdad: [CLAUDE.md](CLAUDE.md)

---

## Por donde empezar

| Audiencia | Documento | Contenido |
|-----------|-----------|-----------|
| Todos | [CLAUDE.md](CLAUDE.md) | Arquitectura, comandos, convenciones, reglas, modelo de datos |
| Todos | [MANIFESTO.md](MANIFESTO.md) | Identidad, génesis, filosofía Story-First, 5 funciones motoras |
| Nuevos devs | [docs/ONBOARDING.md](docs/ONBOARDING.md) | Setup local, patrones clave, flujo de nueva feature |
| Modeladores | [model/model_goreos/docs/GOREOS_ERD_v3.md](model/model_goreos/docs/GOREOS_ERD_v3.md) | ERD + diccionario de datos (121 tablas, 4 schemas) |
| Modeladores | [model/GLOSARIO.yml](model/GLOSARIO.yml) | Glosario autoritativo (244 términos) |
| Testers | [docs/GORE_OS_Testing_Ciclo3.md](docs/GORE_OS_Testing_Ciclo3.md) | Guía de testing integral (ciclos 1-6 + SISREC + paramétricas) |

---

## Estructura del Repositorio

```
goreos/
├── model/                         # Modelo semántico (corazón del sistema)
│   ├── stories/                   # 820 historias de usuario (YAML)
│   ├── entities/aceptadas/        # 141 entidades validadas (YAML)
│   ├── processes/                 # 92 procesos del dominio (YAML)
│   ├── omega/                     # 12 definiciones ontológicas (YAML)
│   ├── model_goreos/              # DDL PostgreSQL ejecutable
│   │   ├── sql/                   # DDL, seeds, migraciones, triggers
│   │   └── docs/                  # ERD, modelo conceptual, decisiones de diseño
│   └── GLOSARIO.yml               # 244 términos institucionales
├── api/                           # Backend FastAPI (:8000)
│   ├── app/routers/               # 29 routers, ~299 endpoints
│   ├── app/schemas/               # Pydantic v2
│   ├── app/core/                  # deps, security, scope, audit, config
│   ├── tests/                     # 730 tests de integración (55 módulos)
│   └── scripts/etl/               # 6 scripts ETL
├── web/                           # Frontend Next.js 16 (:3000)
│   └── src/                       # app/, components/, lib/, types/, hooks/
├── docs/
│   ├── adr/                       # 8 Architecture Decision Records
│   ├── plans/                     # 23 planes de implementación + diseños
│   ├── superpowers/               # 11 planes avanzados + 5 specs
│   ├── archive/                   # Material histórico (feb2026, legacy-model-tel)
│   └── *.md                       # Specs, auditorías, auditorías UX, journeys
├── scripts/                       # Scripts operativos (migraciones, test DB, ETL)
├── CLAUDE.md                      # Fuente de verdad documental (SSOT)
├── INDEX.md                       # Este archivo
├── MANIFESTO.md                   # Identidad y génesis del proyecto
└── docker-compose.yml
```

---

## Decisiones de Arquitectura

Todas las ADRs vigentes están en [`docs/adr/`](docs/adr/):

| ADR | Tema | Estado |
|-----|------|--------|
| [ADR-001](docs/adr/ADR-001-meta-schema.md) | Retención del schema meta | Accepted |
| [ADR-002](docs/adr/ADR-002-raw-sql.md) | Raw SQL via text() (sin ORM) | Accepted |
| [ADR-003](docs/adr/ADR-003-advisory-locks.md) | Advisory locks para generadores secuenciales | Accepted |
| [ADR-004](docs/adr/ADR-004-category-pattern.md) | Category Pattern (univocidad categorial) | Accepted |
| [ADR-005](docs/adr/ADR-005-test-strategy.md) | Tests contra PostgreSQL real (sin mocks) | Accepted |
| [ADR-006](docs/adr/ADR-006-jwt-cookie-migration.md) | Migración JWT → cookies | Proposed |
| [ADR-007](docs/adr/ADR-007-categorical-univocity.md) | Univocidad categorial en todos los schemas | Accepted |
| [ADR-008](docs/adr/008-create-pattern-drawer-vs-page.md) | Drawer vs página /nuevo | Accepted |

---

## Especificaciones y Auditorías

| Documento | Contenido |
|-----------|-----------|
| [GORE_OS_Specification_v1.0.md](docs/GORE_OS_Specification_v1.0.md) | Especificación funcional y técnica completa |
| [GORE_OS_Audit_v3.0.md](docs/GORE_OS_Audit_v3.0.md) | Auditoría institucional (4 fuentes de verdad) |
| [GORE_OS_Role_Surface_Spec_v1.0.md](docs/GORE_OS_Role_Surface_Spec_v1.0.md) | Mapeo rol→superficie (15 roles, 38 rutas) |
| [GORE_OS_User_Journeys_v3.0.md](docs/GORE_OS_User_Journeys_v3.0.md) | 8 arquetipos, 17 journeys, 8 principios UX |
| [GORE_OS_User_Action_Trees_v1.0.md](docs/GORE_OS_User_Action_Trees_v1.0.md) | Árboles de acción por usuario (24 usuarios, 304 endpoints) |
| [AUDITORIA_CATEGORIAL_v3.0.md](docs/AUDITORIA_CATEGORIAL_v3.0.md) | Auditoría categorial exhaustiva |
| [PLAN_NORMALIZACION_JSONB_v2.0.md](docs/PLAN_NORMALIZACION_JSONB_v2.0.md) | Plan de normalización JSONB→relacional |
| [ETL_ARCHITECTURE_v1.0.md](docs/ETL_ARCHITECTURE_v1.0.md) | Arquitectura ETL para datos legacy |

---

## Principios Fundamentales

### Story-First
> **"Si no hay Historia, no existe el requerimiento."**

Derivación unidireccional: **Stories → Entities → Artefactos → Módulos**

### Las 5 Funciones Motoras
1. **PLANIFICAR** — ERD, PROT, ARI
2. **FINANCIAR** — FNDR, FRIL, fondos regionales
3. **EJECUTAR** — Convenios, obras, programas
4. **COORDINAR** — Municipios, servicios, gabinete
5. **NORMAR** — Resoluciones, reglamentos

---

## Estado del Modelo de Datos

**121 tablas** en 4 schemas semánticos:

| Schema | Tablas | Propósito |
|--------|--------|-----------|
| `meta` | 5 | Átomos: Role, Process, Entity, Story |
| `ref` | 3 | Vocabularios controlados (105 schemes) |
| `core` | 80+ | Entidades de negocio |
| `txn` | 20+ | Event sourcing (particionado) |

- **100% univocidad categorial**: 98 CHECK constraints + 19 triggers de transición
- **820 user stories** validadas como fuente de verdad
- **DDL ejecutable**: `model/model_goreos/sql/`

---

*Para arquitectura, comandos, convenciones y reglas: ver [CLAUDE.md](CLAUDE.md)*
