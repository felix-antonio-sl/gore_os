# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GORE_OS is an institutional operating system for the Regional Government of Ñuble (GORE), Chile. It is an integrated model of data, processes, and organizational capabilities designed to digitalize and enable intelligence-driven decision-making for regional government operations.

**Core Philosophy: Story-First & Radical Minimalism**
- Everything derives from User Stories (819+ validated stories)
- Strictly unidirectional derivation: **Stories → Entities → Artifacts → Modules**
- No code exists without a corresponding story

---

## 🏛️ FUNDAMENTO ARQUITECTÓNICO

**CRÍTICO**: El corazón de GORE_OS es el modelo de datos PostgreSQL en `/model/model_goreos`.

### Por qué el Modelo es la Base

Este modelo PostgreSQL es el activo más valioso del proyecto:

1. **Completo y Ejecutable**: 54 tablas organizadas en 4 schemas semánticos (`meta`, `ref`, `core`, `txn`)
2. **Derivado de Stories**: 100% trazable a 819 User Stories validadas (Story-First architecture)
3. **Auditado y Probado**: Ver `/model/model_goreos/docs/auditorias/AUDITORIA_CONSOLIDADA_v3_2026-01-27.md`
4. **Category Pattern**: Gist 14.0 implementado - 75+ schemes para vocabularios controlados sin DDL
5. **Event Sourcing**: Historia completa de cambios con particionamiento mensual/trimestral
6. **ETL Ready**: 470 scripts en `/etl` han migrado datos legacy que alimentan este modelo

### Instalación del Modelo (PRIMER PASO OBLIGATORIO)

**Antes de cualquier desarrollo, instalar el modelo PostgreSQL:**

```bash
# 0. Crear base de datos
createdb -U postgres goreos

# 1-8. Ejecutar DDL en orden estricto (CRÍTICO: no omitir ni reordenar)
cd model/model_goreos/sql
psql -U postgres -d goreos -f goreos_ddl.sql
psql -U postgres -d goreos -f goreos_seed.sql
psql -U postgres -d goreos -f goreos_seed_agents.sql
psql -U postgres -d goreos -f goreos_seed_territory.sql
psql -U postgres -d goreos -f goreos_triggers.sql
psql -U postgres -d goreos -f goreos_triggers_remediation.sql
psql -U postgres -d goreos -f goreos_indexes.sql
psql -U postgres -d goreos -f goreos_remediation_ontological.sql
```

### Arquitectura de 4 Schemas

| Schema | Tablas | Propósito |
|--------|--------|-----------|
| `meta` | 5 | Átomos fundamentales (Role, Process, Entity, Story, Story-Entity) |
| `ref` | 3 | Vocabularios controlados (Category, Actor, Commitment Types) |
| `core` | 40+ | Entidades de negocio (IPR, Agreements, Budget, Work Items) |
| `txn` | 2+ | Event Sourcing (Event, Magnitude) - Particionadas |

### Pipeline de Datos: ETL → PostgreSQL → Apps

```
/etl/sources/               # Datos legacy (Excel, CSV, IDIS)
      ↓
/etl/scripts/               # 470 scripts de transformación Python
      ↓
/etl/normalized/            # Datos limpios y validados
      ↓
model/model_goreos (PostgreSQL)   # Modelo canónico (LA VERDAD)
      ↓
apps/streamlit_tooling/     # Tooling interno existente
apps/flask_app/             # Aplicación productiva (a construir)
```

**Referencias clave del modelo:**
- Documentación completa: `/model/model_goreos/README.md`
- ERD + Data Dictionary: `/model/model_goreos/docs/GOREOS_ERD_v3.md`
- Decisiones de diseño: `/model/model_goreos/docs/DESIGN_DECISIONS.md`
- ADR-003: `/architecture/decisions/ADR-003-modelo-como-base.md`

---

## Technology Stack

- **Backend:** Python 3.11+, Flask 3.0.3 (Application Factory pattern), SQLAlchemy 2.0.30
- **Frontend:** Server-Side Rendering with Jinja2, HTMX 2.0.0, Alpine.js 3.x, Tailwind CSS 3.4.0
- **Database:** PostgreSQL 16 + PostGIS (geospatial for regional planning)
- **Authentication:** Flask-Login integrated with ClaveÚnica (Chilean national identity)
- **Infrastructure:** Docker + Docker Compose, Gunicorn WSGI, Nginx reverse proxy
- **Background Jobs:** Celery with Redis broker
- **ETL:** Pandas 2.0+, DuckDB 0.9.2, NetworkX

## Database Setup & Commands

### Creating the Database from Scratch

The database is defined in `model/model_goreos/sql/` with **8 SQL files** that must be executed in strict order:

```bash
# 0. Create database
createdb -U postgres goreos

# 1-8. Execute DDL files in order (CRITICAL: do not skip or reorder)
cd model/model_goreos/sql
psql -U postgres -d goreos -f goreos_ddl.sql                      # Schemas, tables, functions, ENUMs
psql -U postgres -d goreos -f goreos_seed.sql                     # 75+ schemes, 350+ categories
psql -U postgres -d goreos -f goreos_seed_agents.sql              # KODA agents with HAIC constraint
psql -U postgres -d goreos -f goreos_seed_territory.sql           # 3 provinces, 21 comunas
psql -U postgres -d goreos -f goreos_triggers.sql                 # Business logic triggers
psql -U postgres -d goreos -f goreos_triggers_remediation.sql     # Category validation triggers
psql -U postgres -d goreos -f goreos_indexes.sql                  # Performance indexes
psql -U postgres -d goreos -f goreos_remediation_ontological.sql  # N:M relations (v3.1)
```

### Verifying the Installation

```bash
# Count tables by schema (expected: meta=5, ref=3, core=40+, txn=2+)
psql -U postgres -d goreos -c "
    SELECT schemaname, COUNT(*) AS tables
    FROM pg_tables
    WHERE schemaname IN ('meta', 'ref', 'core', 'txn')
    GROUP BY schemaname
    ORDER BY schemaname;
"

# Verify triggers are active
psql -U postgres -d goreos -c "
    SELECT schemaname, tablename, COUNT(*) AS triggers
    FROM pg_trigger t
    JOIN pg_class c ON c.oid = t.tgrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname IN ('meta', 'ref', 'core', 'txn')
      AND NOT t.tgisinternal
    GROUP BY schemaname, tablename
    ORDER BY schemaname, tablename;
"

# Verify seed data loaded (should return 75+ category schemes)
psql -U postgres -d goreos -c "SELECT COUNT(DISTINCT scheme) FROM ref.category;"
```

## Database Architecture

### 4-Schema Semantic Structure

The database uses **category theory** principles with 4 schemas:

| Schema | Tables | Purpose |
|--------|--------|---------|
| `meta` | 5 | Fundamental atoms (Role, Process, Entity, Story, Story-Entity mapping) |
| `ref` | 3 | Controlled vocabularies (Category pattern with 75+ schemes) |
| `core` | 40+ | Business entities (IPR, Agreements, Budget, Work Items, etc.) |
| `txn` | 2+ | Event Sourcing (Event, Magnitude) - partitioned by month/quarter |

### Critical Design Patterns

**Category Pattern (Gist 14.0):** All taxonomies use `ref.category` instead of ENUMs. 75+ schemes including:
- `ipr_state` (31 states), `work_item_status` (6 states), `mechanism` (evaluation tracks)
- State machines enforced via `valid_transitions` JSONB + triggers

**UUID Universal:** All tables use UUID as PK (not SERIAL)

**Audit Universal:** All tables have `created_at`, `updated_at`, `deleted_at`, `created_by_id`, `updated_by_id`

**Soft Delete:** Deletion is logical (`deleted_at IS NOT NULL`), never physical

**Event Sourcing Hybrid:**
- History tables for critical entities (`core.work_item → core.work_item_history`)
- Generic events in `txn.event` (partitioned monthly)

## Domain Model

### Central Abstract Entity: IPR (Intervención Pública Regional)
Polymorphic type hierarchy with funding mechanisms:
- **Types:** PROYECTO (capital investment) vs PROGRAMA (current expenditure)
- **Funding:** FNDR, FRIL, FRPD, ISAR
- **Evaluation:** SNI, C33, FRIL, Glosa 06, 8% FNDR, Transfers

### Critical Entities
- **EstadoPago (EEPP):** Payment workflow (REVISION → OBSERVADO → APROBADO → PAGADO)
- **ResolucionModificatoria:** Budget/timeframe amendments
- **Funcionario:** Human actors with roles (ANALISTA, JEFE, VISADOR)
- **Unidad:** Organizational units (DIPIR, DAF, JURIDICA)
- **WorkItem:** Unified work management atom (stories, commitments, problems, alerts)

### Core Processes
- **PAYMENT_CYCLE:** 7-step financial execution flow
- **AMENDMENT_CYCLE:** 4-step budget modification with CGR notification
- **Sense-Decide-Act (SDA):** Real-time operational cycle for work items

## Directory Structure

```
goreos/
├── architecture/          # C1-C4 documentation, ADRs, design system
├── model/                 # THE HEART - Semantic domain model
│   ├── stories/           # 819+ YAML user stories (source of truth)
│   ├── roles/             # 410+ institutional roles
│   ├── entities/          # 139+ domain entities (aceptadas/, candidates/)
│   ├── processes/         # 84+ BPMN processes
│   ├── GLOSARIO.yml       # Authoritative terminology
│   └── model_goreos/      # Executable database (v3.1)
│       ├── sql/           # 8 DDL files (execute in order!)
│       ├── docs/          # ERD, audits, design decisions
│       └── README.md      # Installation guide
├── etl/                   # ETL pipeline for legacy data migration
│   ├── sources/           # Legacy data (convenios, FRIL, IDIS, etc.)
│   ├── scripts/           # ~30 Python transformation scripts
│   ├── normalized/        # Cleaned & validated output
│   └── requirements.txt   # pandas>=2.0.0, duckdb==0.9.2
└── catalog/               # KODA federated catalog
```

## Working with ETL Scripts

### Setup ETL Environment

```bash
cd etl
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Key ETL Scripts

All scripts are in `etl/scripts/`:

```bash
# Data profiling (quality assessment)
python scripts/profile_all.py                  # Profile all legacy sources
python scripts/profile_funcionarios.py         # Profile HR data

# Normalization (cleaning + standardization)
python scripts/normalize_convenios.py          # Convenios 2023-2025
python scripts/normalize_fril.py               # FRIL initiatives
python scripts/normalize_progs.py              # 8% FNDR programs
python scripts/normalize_250.py                # Section 250 programs

# Semantic enrichment
python scripts/enrich_ipr_type.py              # Classify IPR types
python scripts/enrich_institution_type.py      # Classify organizations
python scripts/semantic_unify_institutions.py  # Deduplicate institutions

# Entity linking
python scripts/link_entities.py               # Create FK relationships
python scripts/generate_relationship_matrix.py # Visualize entity graph

# Migration assessment
python scripts/compatibility_assessment.py     # Assess legacy → v3.0 compatibility
```

### ETL Output Structure

```
etl/normalized/
├── convenios_normalized.csv       # Cleaned convenios
├── fril_normalized.csv            # Cleaned FRIL
├── progs_normalized.csv           # Cleaned programs
└── idis_normalized.csv            # Cleaned IDIs
```

## Ontological Foundation

The project uses two semantic frameworks:

**ORKO (Organizational Knowledge Ontology):**
- 5 Axioms: Transformation, Capacity, Information, Constraint, Intentionality
- 5 Primitives: Capacity, Flow, Information, Boundary, Purpose
- Enforced via HAIC constraint: all AI agents must have `human_accountable_id`

**KODA (Knowledge Design Architecture):**
- Federation pattern for distributed knowledge across projects
- Agents defined in `model/model_goreos/sql/goreos_seed_agents.sql`

## Key Documentation Files

**Core Documents:**
- `INDEX.md` - Repository navigation guide (START HERE)
- `MANIFESTO.md` - Political genesis and identity, 5 Motor Functions
- `architecture/Omega_GORE_OS_Definition_v3.0.0.md` - System specification v3.0

**Technical Specifications:**
- `docs/technical/planclaude.md` - Master data model specification (Story-First derivation)
- `docs/technical/gestion.md` - Operational data model (WorkItem, Resolutions, Alerts)
- `docs/technical/especificaciones.md` - Detailed specifications

**Stack & Standards:**
- `architecture/stack.md` - Tech stack overview
- `architecture/standards/stack-tecnico-propuesto.md` - Complete stack with code examples, Docker Compose, requirements
- `architecture/standards/antipatrones-y-deuda-tecnica.md` - Anti-patterns guide and quality checklists

**Diagrams & Visual:**
- `architecture/diagrams/entity_diagram.mmd` - Mermaid class diagram of polymorphic IPR model

**Database Documentation:**
- `model/model_goreos/README.md` - Installation guide, verification, troubleshooting
- `model/model_goreos/docs/GOREOS_ERD_v3.md` - Full ERD + Data Dictionary
- `model/model_goreos/docs/GOREOS_CONCEPTUAL_MODEL.md` - Business semantics
- `model/model_goreos/docs/DESIGN_DECISIONS.md` - Why ENUMs vs Category, Event Sourcing, etc.
- `model/model_goreos/docs/auditorias/AUDITORIA_CONSOLIDADA_v3_2026-01-27.md` - Quality audit

**ETL Documentation:**
- `etl/README.md` - Legacy data sources, quality assessment
- `etl/docs/MIGRATION_MATRIX.md` - Entity mapping legacy → v3.0
- `etl/docs/COMPATIBILITY_ASSESSMENT_FRAMEWORK.md` - Migration methodology

## Semantic Model (Stories → Entities)

Stories are the **source of truth**. The derivation chain is:

```
model/stories/*.yml (819 stories)
    ↓
model/entities/aceptadas/*.yml (139 entities)
    ↓
model/model_goreos/sql/goreos_ddl.sql (executable DDL)
    ↓
Flask Blueprints (when implemented)
```

### Story Structure (YAML)

```yaml
id: ST-FIN-001
title: "Aprobar Estado de Pago"
actor: Jefe de Inversiones
goal: "Validar avance físico/financiero de proyecto"
acceptance_criteria:
  - Verificar documentación técnica
  - Calcular porcentaje de avance
  - Emitir aprobación o generar observación
related_entities:
  - EstadoPago
  - IPR
  - Funcionario
```

### Entity Derivation

Entities must trace to at least one story. Example:

```yaml
# model/entities/aceptadas/estado_pago.yml
id: ENT-FIN-EEPP
name: EstadoPago
origin_stories:
  - ST-FIN-001  # Aprobar EEPP
  - ST-FIN-002  # Revisar técnicamente EEPP
  - ST-FIN-003  # Pagar EEPP aprobado
```

## TDE Compliance

GORE_OS integrates with Chilean national digital transformation systems:
- ClaveÚnica (authentication), DocDigital, PISEE, SIAPER/CGR, SIGFE/DIPRES, MercadoPúblico
- Follows Once-Only Principle: consume data via PISEE before asking citizens
- Digital Default: all outgoing documents are digital (XML/PDF signed)
