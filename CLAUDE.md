# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GORE_OS is an institutional operating system for the Regional Government of Ñuble (GORE), Chile: data model, processes, and organizational capabilities to digitalize operations and enable intelligence-driven decision-making.

**Core philosophy**: Story-First + Radical Minimalism
- Everything derives from User Stories (819+ validated)
- Derivation chain: **Stories → Entities → Artifacts → Modules**

## Current Status

- **Database**: v3.2 (63 tables, 4 schemas, 78+ category schemes)
- **Data**: ~53K records (3,621 IPRs, 3,308+ Organizations, 4,609 Budget Commitments, 4,040 Events)
- **ETL migration**: Complete (7 phases: IDIS, Agreements, Budget, Events, Organizations, Programas 8%)
- **Metadata normalization v2.0**: ✓ TESTED in dev | ⏳ PENDING production deployment
  - Coherencia categorial: 100% (Categorical Univocity achieved)
  - New columns: `investment_sector_id`, `fund_category_id`
  - See `etl/migration/NORMALIZACION_v2.0_REPORTE_FINAL.md`
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

| Schema | Purpose | Tables |
|--------|---------|--------|
| `meta` | Role/Process/Entity/Story atoms | 10 |
| `ref`  | Controlled vocabularies (Category pattern, 78+ schemes) | 2 |
| `core` | Business entities (IPR, Agreements, Budget, etc.) | 46 |
| `txn`  | Event sourcing (Event, Magnitude) - partitioned | 5 |

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
- Funding mechanisms: FNDR, FRIL, FRPD, ISAR (via `funding_source_id`)
- Fund categories (8% FNDR): DEPORTE, CULTURA, SEGURIDAD, ADULTO_MAYOR, etc. (via `fund_category_id`, PROGRAMA_8PCT only)
- Investment sectors: SPORTS, CULTURE, EDUCATION, HEALTH, etc. (via `investment_sector_id`)
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

## Category Pattern & Ontological Alignment

Uses `ref.category` (78+ schemes) following **Gist 14.0 Category Pattern** with strict ontological alignment and **Categorical Univocity** enforcement.

### Core Ontologies

- **Gist 14.0**: Base ontology (Category, Magnitude, Event patterns)
- **GORE Ñuble Ontology**: 199 terms (gnub:*) - see `docs/glosario_terminologico.md`
- **TDE (Transformación Digital del Estado)**: 19 core terms (tde:*)
- **Mappings**: Documented in DDL lines 21-37 (`model/model_goreos/sql/goreos_ddl.sql`)

### Key Schemes

- `ipr_type`: INFRAESTRUCTURA, PROGRAMA_8PCT, etc. (7 codes)
- `ipr_party_role`: MANDANTE, EJECUTOR, BENEFICIARIO, UNIDAD_TECNICA (use this, NOT org_funding_role)
- `funding_source`: FNDR, FRIL, FRPD, etc. (funding mechanisms for non-8% IPRs)
- `fondo_8pct`: DEPORTE, CULTURA, SEGURIDAD, ADULTO_MAYOR, etc. (10 codes, via `fund_category_id` for PROGRAMA_8PCT)
- `investment_sector`: SPORTS, CULTURE, EDUCATION, HEALTH, etc. (10 codes, sectorial classification)
- `mechanism`: SNI, FRIL, SUBV8, etc. (financing mechanisms)
- `org_type`: MUNICIPALIDAD, SERVICIO, DIVISION, UNIVERSIDAD, ORG_COMUNITARIA, etc.
- `budget_subtitle`: 24, 31, 33 (budget classification)
- `rendition_state`: COMPLETADO, PENDIENTE, EN_PROCESO (generic, NOT fund-specific)

### Critical Rules for Creating New Schemes

**BEFORE creating a new scheme, verify against categorical audit principles:**

1. ❌ **DO NOT create schemes with only 1 value** (use boolean/timestamp instead)
2. ❌ **DO NOT create entity-specific schemes** (e.g., `rendicion_8pct_state` - use generic `rendition_state`)
3. ❌ **DO NOT duplicate existing schemes** (check `ipr_party_role` before creating `org_funding_role`)
4. ❌ **DO NOT mix ontological dimensions** (funding sources ≠ mechanisms ≠ sectors)
5. ❌ **DO NOT violate Categorical Univocity** (each FK column → exactly 1 scheme)
6. ✅ **DO align with Gist/GNUB/TDE ontologies** (check glosario_terminologico.md)
7. ✅ **DO use existing relational patterns** (M:N junction tables over denormalized schemes)
8. ✅ **DO separate dimensions into different columns** (funding_source_id ≠ fund_category_id)

**Example violations from categorical audits:**
- `ipr_legacy_typology`: REJECTED (v1.0) - mixed 5 ontological dimensions
- `org_funding_role`: REJECTED (v1.0) - duplicates `ipr_party_role`
- `funding_source_id` accepting 2 schemes: FIXED (v2.0) - separated into `funding_source_id` + `fund_category_id`

**Categorical Univocity Principle**: Each FK column must point to exactly ONE ref.category scheme.
- ✓ CORRECT: `funding_source_id` → scheme='funding_source' only
- ✓ CORRECT: `fund_category_id` → scheme='fondo_8pct' only
- ✗ VIOLATION: Single FK pointing to multiple schemes

**See full audits**:
- `docs/AUDITORIA_CATEGORIAL_NORMALIZACION_JSONB.md` (v1.0 audit)
- `etl/migration/NORMALIZACION_v2.0_REPORTE_FINAL.md` (v2.0 remediation)

### Query Schemes

```bash
# List all schemes
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;"

# View scheme values
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT code,label FROM ref.category WHERE scheme='SCHEME_NAME';"

# Check if scheme exists before creating
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT COUNT(*) FROM ref.category WHERE scheme='proposed_scheme_name';"
```

## Directory Structure

```
architecture/    # ADRs, C1-C4 docs, standards
model/           # stories/ entities/ processes/ + model_goreos/ (DDL)
etl/             # sources/ scripts/ normalized/ migration/
apps/            # streamlit_tooling/ flask_app/
```

## Key Docs

### Essential Reading

- `INDEX.md` - repo navigation
- `MANIFESTO.md` - identity + genesis
- `architecture/Omega_GORE_OS_Definition_v3.0.0.md` - system spec
- `docs/glosario_terminologico.md` - 244 ontological terms (Gist 14.0 + GNUB + TDE)

### Data Architecture

- `model/model_goreos/docs/GOREOS_ERD_v3.md` - ERD + data dictionary
- `model/model_goreos/docs/DESIGN_DECISIONS.md` - design rationale
- `model/model_goreos/sql/goreos_ddl.sql` - DDL with ontological mappings (lines 21-37)

### ETL & Migration

- `etl/migration/LECCIONES_APRENDIDAS.md` - migration lessons learned
- `etl/migration/PRE_LOADER_CHECKLIST.md` - pre-loader checklist
- `etl/docs/COMPATIBILITY_ASSESSMENT_FRAMEWORK.md` - migration methodology

### Normalization & Audits

- `etl/migration/NORMALIZACION_v2.0_REPORTE_FINAL.md` - **LATEST**: v2.0 normalization complete report (100% categorical coherence achieved)
- `etl/migration/IPR_NEW_COLUMNS_DATA_DICT_v2.md` - Data dictionary for new columns (investment_sector_id, fund_category_id)
- `docs/PLAN_NORMALIZACION_JSONB_v2.0.md` - v2.0 normalization plan (corrected after categorical audit)
- `etl/migration/sql/normalize_ipr_metadata_v2.sql` - Production-ready normalization script (tested in dev)
- `docs/AUDITORIA_CATEGORIAL_NORMALIZACION_JSONB.md` - v1.0 categorical audit (rejected plan)
- `etl/migration/IPR_METADATA_NORMALIZATION_ANALYSIS.md` - IPR metadata field-by-field analysis

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

# Check categorical coherence (post-normalization v2.0)
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT
    'funding_source_id' AS campo,
    COUNT(*) AS iprs,
    COUNT(DISTINCT c.scheme) AS schemes,
    STRING_AGG(DISTINCT c.scheme, ', ') AS scheme_list
FROM core.ipr i
JOIN ref.category c ON c.id = i.funding_source_id
WHERE i.funding_source_id IS NOT NULL
UNION ALL
SELECT
    'fund_category_id',
    COUNT(*),
    COUNT(DISTINCT c.scheme),
    STRING_AGG(DISTINCT c.scheme, ', ')
FROM core.ipr i
JOIN ref.category c ON c.id = i.fund_category_id
WHERE i.fund_category_id IS NOT NULL;
"
# Expected: schemes = 1 for both (Categorical Univocity)

# Check PROGRAMA_8PCT coherence
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT
    COUNT(*) FILTER (WHERE funding_source_id IS NOT NULL) as has_funding_source,
    COUNT(*) FILTER (WHERE fund_category_id IS NOT NULL) as has_fund_category
FROM core.ipr
WHERE ipr_type_id = (SELECT id FROM ref.category WHERE code='PROGRAMA_8PCT');
"
# Expected: has_funding_source = 0, has_fund_category > 0

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

## Compliance & Governance

### Ontological Compliance

- **Gist 14.0**: Strict adherence to Category, Magnitude, Event patterns
- **GNUB (GORE Ñuble)**: 199 classes mapped to PostgreSQL schema (gnub:IPR, gnub:BudgetaryCommitment, etc.)
- **TDE (Transformación Digital del Estado)**: 19 core classes for digital government
- **ORKO**: Ontology with HAIC constraint (AI agents require `human_accountable_id`)

### Digital Government Standards

- **TDE Core**: ClaveÚnica, DocDigital, PISEE, Once-Only + Digital Default
- **DS N°10**: Electronic file management (expedientes electrónicos)
- **MGDE (Marco de Gestión de Datos del Estado)**: Data governance framework

### Data Quality Gates

Before any schema change or new category scheme:

1. ✅ **Categorical Audit**: Check alignment with Gist/GNUB/TDE ontologies
2. ✅ **Redundancy Check**: Verify no existing scheme covers the need
3. ✅ **Pattern Validation**: Ensure proper use of Category/Magnitude/Junction patterns
4. ✅ **Univocity Validation**: Confirm each FK column points to exactly 1 scheme
5. ✅ **User Story Traceability**: Confirm requirement derives from validated story

**Audit Tools**:
- Use arquitecto-gore agent role for categorical audits
- Check coherence with: `fn_validate_category_scheme(uuid, varchar)` function
- Verify univocity: Query `COUNT(DISTINCT c.scheme)` for each FK column

**Methodology**: See `etl/migration/NORMALIZACION_v2.0_REPORTE_FINAL.md` for v2.0 approach

## Metadata Normalization Workflow (Tested v2.0)

When normalizing JSONB metadata to relational columns:

### 1. Pre-Migration Analysis
```bash
# Identify JSONB keys to normalize
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT jsonb_object_keys(metadata) as key, COUNT(*) as occurrences
FROM core.ipr
WHERE metadata IS NOT NULL
GROUP BY key
ORDER BY occurrences DESC;"
```

### 2. Categorical Audit (CRITICAL)
- Use arquitecto-gore agent for ontological alignment check
- Verify against Gist/GNUB/TDE ontologies (`docs/glosario_terminologico.md`)
- Check for Categorical Univocity violations
- Document rejected schemes with rationale

### 3. Schema Verification
```bash
# Always verify actual schema before writing migration
docker exec goreos_db psql -U goreos -d goreos_model -c "\d core.TARGET_TABLE"
```

### 4. Test Environment Setup
```bash
# Clone production to test database
docker exec goreos_db psql -U goreos -d postgres -c "
DROP DATABASE IF EXISTS goreos_model_test;
CREATE DATABASE goreos_model_test;"

docker exec goreos_db bash -c "
pg_dump -U goreos -d goreos_model | psql -U goreos -d goreos_model_test"
```

### 5. Migration Script Structure
```sql
-- Use transaction blocks per phase
BEGIN;
  -- Phase operations
  -- Verification queries
COMMIT;

-- Use DO $$ blocks for PL/pgSQL
DO $$
BEGIN
  RAISE NOTICE 'Status message';
END $$;

-- Always create backup
CREATE TEMP TABLE backup_table AS SELECT * FROM target_table;
```

### 6. Post-Migration Verification
```bash
# Verify categorical coherence (must be 100%)
docker exec goreos_db psql -U goreos -d goreos_model_test -c "
SELECT
    column_name,
    COUNT(DISTINCT c.scheme) as schemes
FROM core.ipr i
JOIN ref.category c ON c.id = i.column_name
GROUP BY column_name;"
# Expected: schemes = 1 for all FK columns
```

### 7. CHECK Constraints
```sql
-- Add CHECK constraints for referential integrity
ALTER TABLE core.ipr
    ADD CONSTRAINT chk_column_scheme
    CHECK (column_id IS NULL OR
           fn_validate_category_scheme(column_id, 'scheme_name'));
```

**Reference Implementation**: See `etl/migration/sql/normalize_ipr_metadata_v2.sql`

---

**Last updated**: 2026-01-30 (Normalization v2.0 Complete)
