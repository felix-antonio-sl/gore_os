# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GORE_OS is an institutional operating system for the Regional Government of Ñuble (GORE), Chile. It is an integrated model of data, processes, and organizational capabilities designed to digitalize and enable intelligence-driven decision-making for regional government operations.

**Core Philosophy: Story-First & Radical Minimalism**
- Everything derives from User Stories (819+ validated stories)
- Strictly unidirectional derivation: **Stories → Entities → Artifacts → Modules**
- No code exists without a corresponding story

**Current Project Status (2026-01-29)**:
- 🗄️ **Database Model**: v3.1 Complete (63 tables, 4 schemas, 78+ category schemes)
- 📊 **ETL Pipeline**: Stage 1 Complete (470 scripts, 32K records normalized)
- ✅ **Migration FASE 1**: Complete - PersonLoader (110/110) + OrganizationLoader (1,612/1,613) = 1,722 records
- 🔄 **Next**: FASE 2 - IPRLoader (2,010 initiatives from dim_iniciativa_unificada.csv)
- 💻 **Applications**: Streamlit tooling operational, Flask app pending

---

## 🚀 Quick Start

```bash
# 1. Start PostgreSQL
docker-compose up -d postgres

# 2. Verify connection
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT version();"

# 3. Verify FASE 1 migration (already complete)
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT 'core.person' as table, COUNT(*) as migrated FROM core.person WHERE metadata->>'source' = 'dim_funcionario'
UNION ALL
SELECT 'core.organization', COUNT(*) FROM core.organization WHERE metadata->>'source' = 'dim_institucion_unificada';"
-- Expected: person=110, organization=1612

# 4. Next: FASE 2 - IPRLoader
cd etl/migration
python loaders/phase2_ipr_loader.py  # 2,010 initiatives pending
```

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

**Docker Setup (Recommended):**

```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Verify container is running
docker ps | grep goreos_db

# Container exposes port 5433 (not 5432) to host
# Connection: localhost:5433/goreos_model (user: goreos, password: goreos_2026)
```

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
docker exec goreos_db psql -U goreos -d goreos_model -c "
    SELECT schemaname, COUNT(*) AS tables
    FROM pg_tables
    WHERE schemaname IN ('meta', 'ref', 'core', 'txn')
    GROUP BY schemaname
    ORDER BY schemaname;"

# Verify seed data loaded (should return 78+ category schemes after remediation)
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT COUNT(DISTINCT scheme) FROM ref.category;"

# Verify FASE 1 migration data
docker exec goreos_db psql -U goreos -d goreos_model -c "
    SELECT 'persons' as entity, COUNT(*) FROM core.person WHERE deleted_at IS NULL
    UNION ALL
    SELECT 'organizations', COUNT(*) FROM core.organization WHERE deleted_at IS NULL;"
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

### ETL Pipeline Architecture

The ETL pipeline has **two main stages**:

```
Source → Normalized (100% COMPLETE)
  ↓ 470 Python scripts executed
  ↓ 23 CSV files in /etl/normalized/
  ↓ ~32,000 records cleaned and validated
  ↓ Star schema (15 dimensions + 8 facts)

Normalized → PostgreSQL (IN PROGRESS)
  ↓ Migration framework in /etl/migration/
  ↓ 6 phases over 8 weeks
  ↓ Target: core.person, core.ipr, core.agreement, etc.
```

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

### ETL Output Structure (Kimball Star Schema)

```
etl/normalized/
├── dimensions/                    # 15 dimension tables
│   ├── dim_funcionario.csv        # 110 funcionarios (quality: EXCELLENT)
│   ├── dim_institucion_unificada.csv  # 1,613 orgs (5.4% missing RUT)
│   ├── dim_iniciativa_unificada.csv   # 2,010 initiatives
│   └── dim_territorio.csv         # 44 geographic entities
├── facts/                         # 8 fact tables
│   ├── fact_linea_presupuestaria.csv  # 25,754 budget lines (core)
│   ├── fact_convenio.csv          # 533 agreements
│   ├── fact_evento_documental.csv # 2,373 document events
│   └── fact_ejecucion_mensual.csv # 3,496 monthly executions
├── metadata/
│   ├── institution_id_mapping.csv # 150 canonical institution UUIDs
│   └── modificaciones_errors.csv  # 23 known errors (#REF!)
└── relationships/
    ├── relationship_matrix.csv    # 26,045 pairs with strength scores
    └── cross_domain_matches.csv   # 6,618 validated matches (confidence ≥0.9)
```

### ETL Migration to PostgreSQL

The migration framework is in `etl/migration/` and follows a **6-phase LoaderBase pattern**:

```bash
# Setup migration environment
cd etl/migration
pip install -r requirements.txt

# Configure connection
# Edit /goreos/.env with PostgreSQL credentials:
# DB_NAME=goreos_model
# DB_USER=goreos
# DB_PASSWORD=goreos_2026
# DB_HOST=localhost
# DB_PORT=5433

# Test connection
python utils/db.py

# Analyze normalized data quality
python analyze_dimensions.py  # Analyze 15 dimension files
python analyze_facts.py        # Analyze 8 fact files

# Run migration (6 phases)
# Phase 1: Persons and Organizations
python -c "from loaders.phase1_person_loader import PersonLoader; PersonLoader().run()"
python -c "from loaders.phase1_org_loader import OrganizationLoader; OrganizationLoader().run()"

# Phase 2-6: IPR, Agreements, Documents, Budget, Events
# (See plan at ~/.claude/plans/warm-munching-prism.md)
```

### Migration Architecture Components

- **`utils/db.py`**: PostgreSQL connection pool with SQLAlchemy
- **`utils/validators.py`**: Schema validators for 8 target tables (RUT, email, dates, ranges)
- **`utils/resolvers.py`**: FK resolution with caching (12+ lookup functions)
- **`utils/deduplication.py`**: 4 dedup strategies (keep_first, keep_last, keep_newest, merge)
- **`loaders/base.py`**: Abstract LoaderBase class implementing Load→Transform→Validate→Resolve FKs→Insert/Update pipeline
- **`analyze_dimensions.py`**: Quality analysis tool for dimension tables
- **`analyze_facts.py`**: Quality analysis tool for fact tables

### Migration Quality Scores

Based on `etl/docs/COMPATIBILITY_ASSESSMENT_FRAMEWORK.md`:

| Source | Score | Target Table | Key Challenge |
|--------|-------|--------------|---------------|
| dim_funcionario | 85/100 | core.person + core.user | None (excellent quality) |
| dim_institucion | 75/100 | core.organization | 5.4% missing RUT |
| dim_iniciativa | 67/100 | core.ipr | Complex state mapping (31 states) |
| fact_convenio | 71/100 | core.agreement | LOOKUP_OR_CREATE orgs |
| fact_linea_presup | 47/100 | core.budget_program | Reconstruct deltas |

---

## ETL Migration Guidelines (CRITICAL)

**⚠️ MANDATORY READING**: When implementing any ETL loader in `/etl/migration/loaders/`, you MUST follow these guidelines. These rules are derived from 7 critical errors discovered during PersonLoader implementation (110/110 records migrated successfully after 7 iterations).

### 📚 Required Documentation (Read Before Coding)

1. **`/etl/migration/LECCIONES_APRENDIDAS.md`** (32 pages)
   - Complete analysis of 7 critical errors and their solutions
   - Patterns that worked well (hooks, caching, robust parsing)
   - Post-execution validation queries
   - Specific precautions for each upcoming loader

2. **`/etl/migration/PRE_LOADER_CHECKLIST.md`** (80-minute workflow)
   - Step-by-step implementation guide
   - Complete loader template with all overrides
   - Pre-execution tests (dry run → subset → full)
   - Success criteria (≥95% success rate, 100% FK integrity)

### 🔴 Critical Rules (DO NOT SKIP)

#### 1. SQLAlchemy 2.0 - text() Wrapper Obligatory

```python
# ❌ WRONG
session.execute("SELECT * FROM core.person WHERE id = :id", {'id': person_id})

# ✅ CORRECT
from sqlalchemy import text
session.execute(text("SELECT * FROM core.person WHERE id = :id"), {'id': person_id})
```

**Apply to**: All SQL queries in loaders, resolvers, validators

#### 2. Schema Verification First (Never Assume Field Names)

```bash
# ALWAYS verify schema before implementing loader
PGPASSWORD=goreos_2026 psql -h localhost -p 5433 -U goreos -d goreos -c "\d TABLE_NAME"

# Or read DDL directly
cat /Users/felixsanhueza/Developer/goreos/model/model_goreos/sql/goreos_ddl.sql
```

**Common Mismatches**:
- core.person: `rut` (NOT tax_id), `names` (NOT first_name), `paternal_surname` (NOT last_name)
- RUT is NULLABLE in most tables
- Many tables have JSONB fields that require special handling

#### 3. Override Pattern (Mandatory for Each Loader)

Every loader MUST override these methods:

```python
class MyLoader(LoaderBase):

    def get_natural_key(self, row: pd.Series) -> str:
        """Extract natural key from source CSV"""
        return str(row['NATURAL_KEY_FIELD'])

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """Extract natural key from transformed dict"""
        return str(row.get('TARGET_KEY_FIELD', ''))

    def check_exists(self, session, natural_key: str) -> bool:
        """Check if record exists - MUST use correct field for this table"""
        if not natural_key:
            return False
        result = session.execute(
            text("SELECT 1 FROM schema.table WHERE unique_field = :key AND deleted_at IS NULL LIMIT 1"),
            {'key': natural_key}
        ).fetchone()
        return result is not None

    # ONLY if table has JSONB fields
    def pre_insert(self, row: Dict) -> Dict:
        """Convert dict to JSON string for JSONB fields"""
        row = row.copy()
        if 'metadata' in row and isinstance(row['metadata'], dict):
            row['metadata'] = json.dumps(row['metadata'])
        return row
```

#### 4. JSONB Type Adaptation

PostgreSQL JSONB fields require JSON strings, not Python dicts:

```python
# ❌ WRONG - will fail with "can't adapt type 'dict'"
row = {'metadata': {'key': 'value'}}

# ✅ CORRECT
import json
row = {'metadata': json.dumps({'key': 'value'})}
```

**Tables with JSONB**: core.person.metadata, core.organization.metadata, core.ipr.metadata, txn.event.payload

#### 5. System User Required Fields

When using `get_system_user_id()`, the system user MUST have:
- `password_hash` (TEXT NOT NULL) - use dummy bcrypt hash
- `system_role_id` (UUID NOT NULL FK → ref.category where scheme='system_role' and code='ADMIN_SISTEMA')
- `person_id` (UUID NOT NULL FK → core.person)

**Already implemented in**: `/etl/migration/utils/resolvers.py`

#### 6. Validator Updates (Before Each Loader)

Update `/etl/migration/utils/validators.py` with correct field names and validation logic BEFORE implementing loader.

```python
def _validate_TABLE(row: Dict) -> List[str]:
    errors = []

    # Validate NOT NULL fields
    if 'required_field' not in row or not row['required_field']:
        errors.append("Missing required_field (required)")

    # Validate formats (RUT, email, UUID)
    if row.get('rut') and not validate_rut(row['rut']):
        errors.append(f"Invalid RUT: {row['rut']}")

    # Validate ranges
    if 'progress' in row and not (0 <= row['progress'] <= 1):
        errors.append(f"progress out of range: {row['progress']}")

    return errors
```

### 🚀 Execution Workflow (80 minutes per loader)

1. **Schema Discovery** (10 min) - Verify DDL, document NOT NULL, UNIQUE, JSONB fields
2. **Validator Update** (5 min) - Update validators.py with correct schema
3. **Resolver Functions** (10 min) - Implement lookup_* functions with caching
4. **Loader Implementation** (30 min) - Use template from PRE_LOADER_CHECKLIST.md
5. **Dry Run Test** (5 min) - Test with dry_run=True
6. **Subset Test** (5 min) - Test with 10 real records
7. **PostgreSQL Verification** (5 min) - Query to verify data
8. **Full Execution** (5 min) - Migrate all records
9. **Post-Validation** (5 min) - FK integrity, duplicates, ranges

### ✅ Success Criteria (Mandatory)

- ✅ Success rate ≥ 95%
- ✅ FK integrity = 100% (no orphan records)
- ✅ No duplicate natural keys
- ✅ Warnings ≤ 5%
- ✅ Errors ≤ 1%

### 🔍 Pre-Implementation Checklist (Copy-Paste This)

```
Schema Verification:
[ ] Read DDL with \d table_name
[ ] Document NOT NULL fields
[ ] Document UNIQUE fields
[ ] Identify JSONB fields
[ ] Identify FK relationships

Validator:
[ ] Create/update _validate_TABLE() function
[ ] Use correct field names from DDL
[ ] Validate NOT NULL, formats, ranges
[ ] Add to validate_row() router

Resolver:
[ ] Implement lookup_*() functions for FKs
[ ] Add caching (_fk_cache dict)
[ ] Use text() wrapper in all queries

Loader:
[ ] Import text from sqlalchemy
[ ] Import json if JSONB fields exist
[ ] Override get_natural_key()
[ ] Override get_natural_key_from_dict()
[ ] Override check_exists()
[ ] Override pre_insert() if JSONB
[ ] Implement transform_row() with all mappings
[ ] Include created_by_id in all records

Testing:
[ ] Dry run passes (no DB writes)
[ ] Subset (10 rows) passes
[ ] PostgreSQL verification queries pass
[ ] Full run achieves ≥95% success
```

### 📊 Current Migration Status

- ✅ **FASE 1 - PersonLoader**: 110/110 records (100% success) - COMPLETED
- ✅ **FASE 1 - OrganizationLoader**: 1,612/1,613 records (99.9% success) - COMPLETED
- 🔄 **FASE 2 - IPRLoader**: 2,010 records - NEXT
- ⏳ **FASE 3 - AgreementLoader**: 533 convenios - Pending
- ⏳ **FASE 4 - DocumentLoader**: ~500 documents - Pending
- ⏳ **FASE 5 - BudgetProgramLoader**: 25,754 budget lines - Pending
- ⏳ **FASE 6 - EventLoader**: ~5,000 events - Pending

**FASE 1 Total**: 1,722 records migrated (99.95% success rate)

### 🎯 Quick Reference - Common Patterns

**Caching FK Lookups**:
```python
_fk_cache: Dict[str, UUID] = {}

def lookup_entity(key: str) -> Optional[UUID]:
    cache_key = f"entity:{key}"
    if cache_key in _fk_cache:
        return _fk_cache[cache_key]
    # ... query DB ...
    _fk_cache[cache_key] = result
    return result
```

**Mapping Legacy Values to ref.category**:
```python
def _resolve_type(self, legacy_value: str):
    mapping = {
        'LEGACY_A': 'CATEGORY_CODE_A',
        'LEGACY_B': 'CATEGORY_CODE_B',
    }
    code = mapping.get(legacy_value.upper(), 'DEFAULT_CODE')
    return lookup_category('scheme_name', code)
```

**Parsing Complex Fields**:
```python
def _parse_field(self, value: str) -> tuple:
    if ',' not in value:
        return (value, 'DEFAULT', None)  # Fallback

    part1, part2 = value.split(',', 1)
    # ... parsing logic with edge cases ...
    return (parsed1, parsed2, parsed3)
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
- `etl/docs/COMPATIBILITY_ASSESSMENT_FRAMEWORK.md` - Migration methodology (8 sources with compatibility scores 43-85/100)
- Migration plan: `~/.claude/plans/warm-munching-prism.md` - 8-week, 6-phase migration plan with LoaderBase architecture

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

---

## Database Credentials & Configuration

### PostgreSQL Connection Details

**Development Database** (Docker container):
- **Host**: localhost
- **Port**: 5433 (NOT 5432 - mapped from container's 5432)
- **Database**: goreos_model
- **User**: goreos
- **Password**: goreos_2026
- **Connection String**: `postgresql://goreos:goreos_2026@localhost:5433/goreos_model`

### Connection Commands

```bash
# psql connection (via docker exec - recommended)
docker exec goreos_db psql -U goreos -d goreos_model

# psql connection (direct)
PGPASSWORD=goreos_2026 psql -h localhost -p 5433 -U goreos -d goreos_model

# SQLAlchemy connection (Python)
DATABASE_URL = "postgresql://goreos:goreos_2026@localhost:5433/goreos_model"

# Docker container management
docker-compose up -d postgres          # Start PostgreSQL container
docker-compose down                    # Stop all containers
docker-compose ps                      # Check container status
docker logs goreos_db                  # View PostgreSQL logs
```

### Docker Compose Configuration

Located at `/Users/felixsanhueza/Developer/goreos/docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgis/postgis:16-3.4
    container_name: goreos_db
    environment:
      POSTGRES_DB: goreos
      POSTGRES_USER: goreos
      POSTGRES_PASSWORD: goreos_2026
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=es_CL.UTF-8"
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    command: postgres -c shared_preload_libraries='pg_stat_statements' -c pg_stat_statements.track=all
```

### Environment Variables (.env)

Create `/Users/felixsanhueza/Developer/goreos/.env`:

```bash
# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5433
DB_NAME=goreos_model
DB_USER=goreos
DB_PASSWORD=goreos_2026

# SQLAlchemy
DATABASE_URL=postgresql://goreos:goreos_2026@localhost:5433/goreos_model

# Migration Settings
NORMALIZED_DIR=/Users/felixsanhueza/Developer/goreos/etl/normalized
DRY_RUN=false
BATCH_SIZE=1000

# Flask Configuration (when implemented)
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
```

### ETL Migration Connection

Located at `/Users/felixsanhueza/Developer/goreos/etl/migration/config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Database (defaults match docker-compose setup)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5433))  # Docker maps 5433:5432
DB_NAME = os.getenv('DB_NAME', 'goreos_model')  # Actual database name
DB_USER = os.getenv('DB_USER', 'goreos')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'goreos_2026')

# Migration
NORMALIZED_DIR = os.path.join(os.path.dirname(__file__), '..', 'normalized')
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 1000))
```

### Verification Commands

```bash
# Test PostgreSQL connection
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT version();"

# Verify database exists
docker exec goreos_db psql -U goreos -l

# Count tables by schema
docker exec goreos_db psql -U goreos -d goreos_model -c "
    SELECT schemaname, COUNT(*) AS tables
    FROM pg_tables
    WHERE schemaname IN ('meta', 'ref', 'core', 'txn')
    GROUP BY schemaname;"

# Test ETL migration connection (Python)
cd /Users/felixsanhueza/Developer/goreos/etl/migration
python -c "from utils.db import test_connection; test_connection()"
```

### Troubleshooting

**"Connection refused"**:
```bash
# Check container is running
docker ps | grep goreos_db

# If not running, start it
docker-compose up -d postgres

# Check logs
docker logs goreos_db
```

**"Password authentication failed"**:
```bash
# Use docker exec instead (avoids password issues)
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT 1;"

# Or use connection string with password
psql postgresql://goreos:goreos_2026@localhost:5433/goreos_model
```

**"Database does not exist"**:
```bash
# Create database (if goreos_model doesn't exist)
docker exec goreos_db createdb -U goreos goreos_model

# Then install schema (8 DDL files)
cd /Users/felixsanhueza/Developer/goreos/model/model_goreos/sql
for f in goreos_ddl.sql goreos_seed.sql goreos_seed_agents.sql goreos_seed_territory.sql \
         goreos_triggers.sql goreos_triggers_remediation.sql goreos_indexes.sql \
         goreos_remediation_ontological.sql; do
    docker exec -i goreos_db psql -U goreos -d goreos_model < $f
done
```

### Security Notes

- **Development only**: These credentials are for local development
- **Production**: Use environment variables, secrets management (AWS Secrets Manager, HashiCorp Vault)
- **Never commit**: Add `.env` to `.gitignore`
- **Docker volume**: Database persists in `postgres_data` volume even after container restart

---

## 🔧 Common Issues & Solutions

### "Database does not exist"
```bash
# Check actual database name
docker exec goreos_db psql -U goreos -l

# The database is called "goreos_model", not "goreos"
# Update config.py: DB_NAME = 'goreos_model'
```

### "Category not found" warnings during migration
```bash
# Always verify scheme names BEFORE mapping
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;"

# Then verify codes for specific scheme
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT code, label FROM ref.category
WHERE scheme = 'ACTUAL_SCHEME_NAME'
ORDER BY code;"
```

### "bind parameter required" during update
- **Cause**: LoaderBase.update_record() uses generic WHERE clause
- **Solution**: Override update_record() with same WHERE as check_exists()
- **See**: `/etl/migration/LECCIONES_APRENDIDAS.md` §10

### Migration appears to have duplicates
```bash
# Filter by metadata.source to exclude seed data
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT COUNT(*) FROM core.organization
WHERE metadata->>'source' = 'dim_institucion_unificada';"
```

### "can't adapt type 'dict'" when inserting
- **Cause**: PostgreSQL JSONB requires JSON string, not Python dict
- **Solution**: Implement pre_insert() to convert with json.dumps()
- **See**: `/etl/migration/LECCIONES_APRENDIDAS.md` §5

---

## 📚 Essential Reading

**Before ANY ETL work**:
1. `/etl/migration/LECCIONES_APRENDIDAS.md` - 13 problems + solutions from FASE 1
2. `/etl/migration/PRE_LOADER_CHECKLIST.md` - 80-min workflow for each loader
3. `/etl/docs/COMPATIBILITY_ASSESSMENT_FRAMEWORK.md` - Migration methodology

**Database Documentation**:
1. `/model/model_goreos/README.md` - Installation & verification
2. `/model/model_goreos/docs/GOREOS_ERD_v3.md` - Complete ERD + Data Dictionary
3. `/model/model_goreos/docs/DESIGN_DECISIONS.md` - Architectural decisions

**Architecture**:
1. `/architecture/Omega_GORE_OS_Definition_v3.0.0.md` - System specification
2. `/architecture/standards/stack-tecnico-propuesto.md` - Complete tech stack

---

**Last Updated**: 2026-01-29
**Document Version**: 2.3 (FASE 1 complete, credentials fixed, schemes added)

---

## 📋 Recent Changes (2026-01-29 Remediation)

### New Category Schemes Added to ref.category

| Scheme | Values | Purpose |
|--------|--------|---------|
| `resolution_subtype` | 6 | APRUEBA_CONVENIO, MODIFICA_CONVENIO, APRUEBA_PAGO, MODIFICA_PRESUPUESTO, TERMINO_ANTICIPADO, PRORROGA |
| `document_type` | 12 | CONVENIO, RESOLUCION, DECRETO, ESTADO_PAGO, CERTIFICADO, BOLETA_GARANTIA, INFORME_TECNICO, RENDICION, FACTURA, ORDEN_COMPRA, PLANO, OTRO |
| `role_in_committee` | 5 | PRESIDENTE, SECRETARIO, VOCAL, ASESOR, INVITADO |

### Remediation Completed
- Fixed malformed RUT in dim_institucion_unificada.csv
- Removed 6 .tmp files from facts/ (10,048 lines)
- Removed obsolete backup files (resolvers_broken_backup.py, resolvers.py.broken)
- Updated .gitignore with ETL patterns (*.duckdb, *.tmp, venv/, migration_logs/)
