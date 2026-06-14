# GORE_OS — Mapa del Repositorio

> **v3.2.0** | **Story-First & Minimalismo Radical** | Fuente de verdad: [CLAUDE.md](CLAUDE.md)

---

## Por dónde empezar

| Audiencia | Documento | Contenido |
|-----------|-----------|-----------|
| Todos | [CLAUDE.md](CLAUDE.md) | Arquitectura, comandos, convenciones, reglas, modelo de datos (SSOT) |
| Todos | [MANIFESTO.md](MANIFESTO.md) | Identidad, génesis, filosofía Story-First, 5 funciones motoras |
| Nuevos devs | [docs/ONBOARDING.md](docs/ONBOARDING.md) | Setup local, patrones clave, flujo de nueva feature |
| Exploradores | [docs/README.md](docs/README.md) | Catálogo de toda la documentación secundaria (con estado/vigencia) |
| Modeladores | [model/model_goreos/docs/GOREOS_ERD_v3.md](model/model_goreos/docs/GOREOS_ERD_v3.md) | ERD + diccionario de datos (parcial: modelo base) |
| Modeladores | [model/GLOSARIO.yml](model/GLOSARIO.yml) | Glosario autoritativo (57 términos) |

---

## Estructura del Repositorio

```
goreos/
├── model/                         # Modelo semántico (corazón del sistema)
│   ├── stories/                   # 818 historias de usuario (YAML)
│   ├── entities/aceptadas/        # 141 entidades validadas (YAML)
│   ├── processes/                 # 81 procesos del dominio (YAML)
│   ├── omega/                     # 12 definiciones ontológicas (YAML)
│   ├── model_goreos/              # DDL PostgreSQL ejecutable
│   │   ├── sql/                   # DDL, seeds, migraciones, triggers
│   │   └── docs/                  # ERD, modelo conceptual, decisiones de diseño
│   └── GLOSARIO.yml               # 57 términos institucionales
├── api/                           # Backend FastAPI (:8000)
│   ├── app/routers/               # 29 routers, 304 endpoints
│   ├── app/schemas/               # Pydantic v2
│   ├── app/core/                  # deps, security, scope, audit, config
│   ├── tests/                     # ~730 tests de integración (54 módulos)
│   └── scripts/etl/               # 8 loaders/enrichers + helpers
├── web/                           # Frontend Next.js 16 (:3000)
│   └── src/                       # app/, components/, lib/, types/, hooks/
├── docs/
│   ├── README.md                  # Catálogo de documentación (empieza aquí)
│   ├── adr/                       # 8 Architecture Decision Records
│   ├── archive/                   # Material histórico (planes implementados, auditorías cerradas, normalización, legacy)
│   └── *.md                       # Specs y referencias vigentes (ver docs/README.md)
├── scripts/                       # Scripts operativos (migraciones, test DB, ETL)
├── CLAUDE.md                      # Fuente de verdad documental (SSOT)
├── INDEX.md                       # Este archivo (mapa del repo)
└── MANIFESTO.md                   # Identidad y génesis del proyecto
```

---

## Decisiones de Arquitectura

Las 8 ADRs vigentes están catalogadas con su estado en **[docs/README.md › Decisiones de arquitectura](docs/README.md#decisiones-de-arquitectura-adrs)** (ADR-006 *Deferred*, el resto *Accepted*). Los archivos viven en [`docs/adr/`](docs/adr/).

---

## Estado del Modelo de Datos

**128 tablas físicas** en 5 schemas:

| Schema | Tablas | Propósito |
|--------|--------|-----------|
| `core`   | 89 | Entidades de negocio |
| `txn`    | 20 | Event sourcing (`event` + `magnitude`, 18 particiones) |
| `public` | 11 | Capa de modelado Story-First (`dim_*`, `fact_user_story`, `bridge_*`) |
| `meta`   | 5  | Átomos: Role, Process, Entity, Story |
| `ref`    | 3  | Vocabularios controlados (105 schemes) |

- **100% univocidad categorial**: 159 CHECK constraints (`fn_validate_category_scheme`) + triggers de transición
- **818 user stories** validadas como fuente de verdad
- **DDL ejecutable**: `model/model_goreos/sql/`

---

*Para arquitectura, comandos, convenciones y reglas: ver [CLAUDE.md](CLAUDE.md)*
*Para el catálogo completo de documentación: ver [docs/README.md](docs/README.md)*
