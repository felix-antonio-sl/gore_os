# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GORE_OS is an institutional operating system for the Regional Government of Ñuble (GORE), Chile: data model, processes, and organizational capabilities to digitalize operations and enable intelligence-driven decision-making.

**Core philosophy**: Story-First + Radical Minimalism
- Everything derives from User Stories (819+ validated)
- Derivation chain: **Stories → Entities → Artifacts → Modules**

## Current Status

- **Database**: v3.1 complete (63 tables, 4 schemas, 78+ category schemes)
- **ETL migration**: FASE 1–7 complete (~46K records migrated)
- **Apps**: Streamlit tooling operational; Flask app pending

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
- Types: PROYECTO (capital) vs PROGRAMA (current)
- Funding: FNDR, FRIL, FRPD, ISAR

Critical entities: EstadoPago, Agreement, BudgetProgram, WorkItem

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

## Category Pattern

Uses `ref.category` (78+ schemes) instead of ENUMs. Query available schemes:

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

## Compliance

- **ORKO**: Ontology with HAIC constraint (AI agents require `human_accountable_id`)
- **TDE**: ClaveÚnica, DocDigital, PISEE, Once-Only + Digital Default

---

**Last updated**: 2026-01-30
