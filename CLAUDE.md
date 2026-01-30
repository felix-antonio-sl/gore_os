# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GORE_OS is an institutional operating system for the Regional Government of Ñuble (GORE), Chile: data model, processes, and organizational capabilities to digitalize operations and enable intelligence-driven decision-making.

**Core philosophy**: Story-First + Radical Minimalism
- Everything derives from User Stories (819+ validated)
- Derivation chain: **Stories → Entities → Artifacts → Modules**

## Current Status

- **Database**: v3.1 complete (63 tables, 4 schemas, 56 category schemes)
- **Data**: ~53K records (3,621 IPRs, 3,308 Organizations, 4,609 Budget Commitments, 4,040 Events)
- **ETL migration**: Complete (7 phases: IDIS, Agreements, Budget, Events, Organizations, Programas 8%)
- **Apps**: Streamlit migration_viewer operational; Flask app pending

## Quick Start

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Verify connection
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT version();"

# Quick data check
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT schemaname, COUNT(*) AS tables FROM pg_tables
WHERE schemaname IN ('meta','ref','core','txn') GROUP BY schemaname;"
```

## Architecture

**The heart of GORE_OS is the PostgreSQL data model in `model/model_goreos/`.**

### 4-Schema structure

| Schema | Purpose |
|--------|---------|
| `meta` | Role/Process/Entity/Story atoms |
| `ref`  | Controlled vocabularies (Category pattern, 78+ schemes) |
| `core` | Business entities (IPR, Agreements, Budget, etc.) |
| `txn`  | Event sourcing (Event, Magnitude) - partitioned |

### Data pipeline

```
etl/sources/ → etl/scripts/ → etl/normalized/ → model/model_goreos (PostgreSQL) → apps/
```

### Key references

- `model/model_goreos/docs/GOREOS_ERD_v3.md` (ERD + data dictionary)
- `model/model_goreos/docs/DESIGN_DECISIONS.md` (design rationale)
- `architecture/decisions/ADR-003-modelo-como-base.md` (ADR)

## Tech Stack

- **Backend**: Python 3.11+, Flask 3.0.3, SQLAlchemy 2.0.30
- **Frontend**: Jinja2 + HTMX 2.0.0 + Alpine.js 3.x + Tailwind CSS 3.4.0
- **DB**: PostgreSQL 16 + PostGIS
- **ETL**: Pandas 2.0+, DuckDB 0.9.2

## Domain Model

Central entity: **IPR (Intervención Pública Regional)** - polymorphic
- Types: INFRAESTRUCTURA, EQUIPAMIENTO, TRANSFERENCIA, PROGRAMA_SOCIAL, PROGRAMA_8PCT, CONSERVACION, ESTUDIO
- Funding mechanisms: FNDR, FRIL, FRPD, ISAR, SUBV8 (8% FNDR)
- Lifecycle: Status transitions from planning → execution → closure

Critical entities:
- **Organization**: Parties involved (GORE, municipalities, private sector, community orgs)
- **BudgetProgram/BudgetCommitment**: Financial tracking ($1.37B+ committed)
- **Agreement**: Contracts and mandates (convenios, mandatos)
- **Territory**: Geographic scope (regional, provincial, communal)
- **Event**: Audit trail (payments, transfers, milestones)

## Database Connection

```
Host: localhost, Port: 5433, DB: goreos_model, User: goreos, Pass: goreos_2026
```

```bash
# Preferred method
docker exec goreos_db psql -U goreos -d goreos_model

# Or direct
PGPASSWORD=goreos_2026 psql -h localhost -p 5433 -U goreos -d goreos_model
```

## ETL Development

### Setup

```bash
cd etl
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Critical rules for loaders

**Read before writing loaders:**
1. `etl/migration/LECCIONES_APRENDIDAS.md`
2. `etl/migration/PRE_LOADER_CHECKLIST.md`

**Hard rules:**

1. **SQLAlchemy 2.0**: Always wrap SQL with `text()`:
```python
from sqlalchemy import text
session.execute(text("SELECT 1 FROM core.person WHERE id=:id"), {"id": person_id})
```

2. **Verify schema first** (never assume field names):
```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "\d core.TABLE_NAME"
```

3. **JSONB fields**: Store JSON strings, not Python dicts:
```python
import json
row["metadata"] = json.dumps(row["metadata"]) if isinstance(row.get("metadata"), dict) else row.get("metadata")
```

4. **Each loader must override**: `get_natural_key()`, `get_natural_key_from_dict()`, `check_exists()`

### Execution workflow

```
Schema discovery → validator update → resolvers → loader → dry run → 10-row subset → full run
```

Success criteria: ≥95% success, 100% FK integrity, no duplicate natural keys.

### Data Normalization Principle

**CRITICAL**: Prefer relational structures over JSONB metadata.

When migrating data, follow this hierarchy:
1. **FK relationships** (funding_source_id, executor_id) > JSONB text fields
2. **Dedicated tables** (budget_commitment) > JSONB numeric fields
3. **Junction tables** (ipr_territory, ipr_party) > JSONB denormalized data
4. **JSONB metadata** only for: audit trails (source, event_id_original), unstructured extras

Example: Programas 8% were migrated with full normalization:
- `metadata->>'fondo'` → `funding_source_id` FK to `ref.category`
- `metadata->>'institucion_receptora'` → `executor_id` FK to `core.organization`
- `metadata->>'monto_transferido'` → `core.budget_commitment.amount`
- Text fields (provincia/comuna) → `core.ipr_territory` junction table

## Category Pattern

Uses `ref.category` (56 schemes) instead of ENUMs for extensibility.

**Key schemes:**
- `ipr_type`: INFRAESTRUCTURA, PROGRAMA_8PCT, etc.
- `ipr_status`: PLANIFICACION, EN_EJECUCION, CERRADO, etc.
- `funding_mechanism`: FNDR, FRIL, SUBV8, etc.
- `fondo_8pct`: DEPORTE, CULTURA, SEGURIDAD, ADULTO_MAYOR, etc.
- `org_type`: PUBLICO, PRIVADO, COMUNITARIA, etc.
- `commitment_type`: PRESUPUESTO_INICIAL, TRANSFERENCIA_8PCT, etc.
- `party_role`: MANDANTE, EJECUTOR, BENEFICIARIO, etc.

Query available schemes:

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;"
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT code,label FROM ref.category WHERE scheme='SCHEME_NAME';"
```

## Directory Structure

```
architecture/    # ADRs, C1-C4 docs, standards
model/           # stories/ entities/ processes/ + model_goreos/ (DDL)
etl/             # sources/ scripts/ normalized/ migration/
apps/            # streamlit_tooling/ flask_app/
```

## Key Docs

- `INDEX.md` - repo navigation
- `MANIFESTO.md` - identity + genesis
- `architecture/Omega_GORE_OS_Definition_v3.0.0.md` - system spec
- `etl/docs/COMPATIBILITY_ASSESSMENT_FRAMEWORK.md` - migration methodology

## Semantic Model

```
model/stories/*.yml → model/entities/aceptadas/*.yml → model/model_goreos/sql/goreos_ddl.sql
```

## Development Commands

```bash
# Lint
ruff check .

# Format
black .

# Type check
mypy .

# Tests
pytest                        # all tests
pytest -m unit               # unit tests only
pytest -m "not slow"         # skip slow tests
pytest tests/test_foo.py -k test_name  # single test
```

## Running Apps

```bash
# Migration Viewer (Streamlit)
cd apps/migration_viewer
source .venv/bin/activate
streamlit run app.py

# Flask app (when implemented)
cd app
flask run --debug
```

## Data Integrity Checks

Critical queries for validating system integrity:

```bash
# Check IPR types distribution
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT c.code, COUNT(*) as total
FROM core.ipr i
JOIN ref.category c ON i.ipr_type_id = c.id
GROUP BY c.code ORDER BY total DESC;"

# Check orphaned records (IPRs without funding source)
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT COUNT(*) FROM core.ipr WHERE funding_source_id IS NULL;"

# Check budget vs commitments alignment
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT bp.code, bp.initial_amount, SUM(bc.amount) as committed
FROM core.budget_program bp
LEFT JOIN core.budget_commitment bc ON bc.budget_program_id = bp.id
GROUP BY bp.id, bp.code, bp.initial_amount;"

# Check territorial coverage
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT COUNT(*) as iprs_sin_territorio
FROM core.ipr i
LEFT JOIN core.ipr_territory it ON i.id = it.ipr_id
WHERE it.ipr_id IS NULL;"
```

## Compliance

- **ORKO**: Ontology with HAIC constraint (AI agents require `human_accountable_id`)
- **TDE**: ClaveÚnica, DocDigital, PISEE, Once-Only + Digital Default

---

**Last updated**: 2026-01-30
