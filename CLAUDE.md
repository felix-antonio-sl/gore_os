# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GORE_OS is an institutional operating system for the Regional Government of Ñuble (GORE), Chile: data model, processes, and organizational capabilities to digitalize operations and enable intelligence-driven decision-making.

**Core philosophy**: Story-First + Radical Minimalism
- Everything derives from User Stories (820+ validated)
- Derivation chain: **Stories → Entities → Artifacts → Modules**

## Current Status

- **Database**: v3.2 (71 tables, 4 schemas, 78+ category schemes)
- **Data**: ~53K records (3,621 IPRs, 3,308+ Organizations, 4,609 Budget Commitments, 4,040 Events)
- **ETL migration**: Complete (7 phases executed, code archived in `docs/legacy/etl/`)
- **Metadata normalization v3.0**: COMPLETED (13 critical + 16 medium normalizations)
- **Categorical Univocity**: 100% (CHECK constraints active)
- **Stack transition**: Legacy (Flask+Streamlit) archived. New stack: Next.js + FastAPI + MCP + PostgreSQL + pgvector

## Quick Start

```bash
# Start PostgreSQL
docker compose up -d postgres

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
| `core` | Business entities (IPR, Agreements, Budget, etc.) | 54 |
| `txn`  | Event sourcing (Event, Magnitude) - partitioned | 5 |

### Key references

- `model/model_goreos/docs/GOREOS_ERD_v3.md` (ERD + data dictionary)
- `model/model_goreos/docs/DESIGN_DECISIONS.md` (design rationale)
- `architecture/decisions/ADR-003-modelo-como-base.md` (ADR)

## Tech Stack (Transition)

**Legacy (archived)**: Python 3.11+, Flask, Streamlit, HTMX, Alpine.js
**New stack (in progress)**: Next.js, FastAPI, MCP Servers, PostgreSQL 16 + pgvector, LLM Agents

The PostgreSQL data model (71 tables, 78+ category schemes) and 820 user stories are the core assets that persist across the stack transition.

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

Connection parameters are defined in `.env` (see `.env.example`):

```bash
# Preferred method
docker exec goreos_db psql -U goreos -d goreos_model

# Or use env vars
source .env && PGPASSWORD=$DB_PASSWORD psql -h localhost -p ${DB_PORT:-5432} -U $DB_USER -d $DB_NAME
```

## Category Pattern & Ontological Alignment

Uses `ref.category` (78+ schemes) following **Gist 14.0 Category Pattern** with strict ontological alignment and **Categorical Univocity** enforcement.

### Core Ontologies

- **Gist 14.0**: Base ontology (Category, Magnitude, Event patterns)
- **GORE Ñuble Ontology**: 199 terms (gnub:*) - see `model/GLOSARIO.yml`
- **TDE (Transformación Digital del Estado)**: 19 core terms (tde:*)
- **Mappings**: Documented in DDL lines 21-37 (`model/model_goreos/sql/goreos_ddl.sql`)

### Key Schemes

- `ipr_type`: INFRAESTRUCTURA, PROGRAMA_8PCT, etc. (7 codes)
- `ipr_party_role`: MANDANTE, EJECUTOR, BENEFICIARIO, UNIDAD_TECNICA
- `funding_source`: FNDR, FRIL, FRPD, etc. (funding mechanisms for non-8% IPRs)
- `fondo_8pct`: DEPORTE, CULTURA, SEGURIDAD, ADULTO_MAYOR, etc. (10 codes, via `fund_category_id` for PROGRAMA_8PCT)
- `investment_sector`: SPORTS, CULTURE, EDUCATION, HEALTH, etc. (10 codes)
- `mechanism`: SNI, FRIL, SUBV8, etc. (financing mechanisms)
- `org_type`: MUNICIPALIDAD, SERVICIO, DIVISION, UNIVERSIDAD, ORG_COMUNITARIA, etc.
- `budget_subtitle`: 24, 31, 33 (budget classification)
- `rendition_state`: COMPLETADO, PENDIENTE, EN_PROCESO (generic, NOT fund-specific)

### Critical Rules for Creating New Schemes

**BEFORE creating a new scheme, verify against categorical audit principles:**

1. DO NOT create schemes with only 1 value (use boolean/timestamp instead)
2. DO NOT create entity-specific schemes (e.g., `rendicion_8pct_state` - use generic `rendition_state`)
3. DO NOT duplicate existing schemes (check `ipr_party_role` before creating `org_funding_role`)
4. DO NOT mix ontological dimensions (funding sources != mechanisms != sectors)
5. DO NOT violate Categorical Univocity (each FK column → exactly 1 scheme)
6. DO align with Gist/GNUB/TDE ontologies (check `model/GLOSARIO.yml`)
7. DO use existing relational patterns (M:N junction tables over denormalized schemes)
8. DO separate dimensions into different columns (funding_source_id != fund_category_id)

**Categorical Univocity Principle**: Each FK column must point to exactly ONE ref.category scheme.

### Query Schemes

```bash
# List all schemes
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;"

# View scheme values
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT code,label FROM ref.category WHERE scheme='SCHEME_NAME';"
```

## Directory Structure

```
goreos/
├── model/                     # THE HEART - Stories + Entities + DDL
│   ├── stories/               # 820 user stories (INTOCABLE)
│   ├── entities/aceptadas/    # 141 accepted entities
│   ├── processes/             # 92 processes
│   ├── model_goreos/
│   │   ├── sql/               # DDL, indexes, seed, triggers
│   │   └── docs/              # ERD, Design Decisions
│   ├── omega/                 # Ontological definitions
│   └── GLOSARIO.yml           # 244 ontological terms
├── architecture/
│   ├── decisions/             # ADR-002, ADR-003
│   ├── Omega_GORE_OS_Definition_v3.0.0.md
│   └── legacy/                # Old stack docs (frozen)
├── docs/
│   ├── AUDITORIA_CATEGORIAL_v3.0.md
│   ├── PLAN_NORMALIZACION_JSONB_v2.0.md
│   └── legacy/                # ETL sources, migration SQL, old docs
├── docker-compose.yml
├── .env.example
├── CLAUDE.md
├── INDEX.md
├── MANIFESTO.md
└── README.md
```

## Key Docs

### Essential Reading

- `INDEX.md` - repo navigation
- `MANIFESTO.md` - identity + genesis
- `architecture/Omega_GORE_OS_Definition_v3.0.0.md` - system spec
- `model/GLOSARIO.yml` - 244 ontological terms (Gist 14.0 + GNUB + TDE)

### Data Architecture

- `model/model_goreos/docs/GOREOS_ERD_v3.md` - ERD + data dictionary
- `model/model_goreos/docs/DESIGN_DECISIONS.md` - design rationale
- `model/model_goreos/sql/goreos_ddl.sql` - DDL with ontological mappings (lines 21-37)

### Audits & Normalization

- `docs/AUDITORIA_CATEGORIAL_v3.0.md` - v3.0 comprehensive JSONB audit
- `docs/PLAN_NORMALIZACION_JSONB_v2.0.md` - v2.0 normalization plan
- `docs/AUDITORIA_CATEGORIAL_NORMALIZACION_JSONB.md` - v1.0 categorical audit

### Legacy (archived, read-only reference)

- `docs/legacy/etl/migration-docs/` - ETL migration lessons, checklists, reports
- `docs/legacy/etl/migration-sql/` - Normalization SQL scripts (v1-v3)
- `docs/legacy/etl/sources/` - Original data sources (CSVs)
- `architecture/legacy/` - Old stack architecture docs

## Semantic Model

```
model/stories/*.yml → model/entities/aceptadas/*.yml → model/model_goreos/sql/goreos_ddl.sql
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

# Check categorical coherence
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

# Verify categorical univocity post-v3.0
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT
    'estamento_id' AS columna,
    COUNT(DISTINCT c.scheme) AS schemes
FROM core.person p
JOIN ref.category c ON c.id = p.estamento_id
WHERE p.estamento_id IS NOT NULL
UNION ALL
SELECT 'item_id', COUNT(DISTINCT c.scheme)
FROM core.budget_program bp
JOIN ref.category c ON c.id = bp.item_id
WHERE bp.item_id IS NOT NULL;
"

# Verify EJECUTOR integrity
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT
    COUNT(*) as total_iprs_con_executor,
    COUNT(ip.id) as total_ipr_party_ejecutor
FROM core.ipr i
LEFT JOIN core.ipr_party ip ON i.id = ip.ipr_id
    AND ip.party_role_id = (SELECT id FROM ref.category WHERE code='EJECUTOR')
WHERE i.executor_id IS NOT NULL AND i.deleted_at IS NULL;
"
```

## Compliance & Governance

### Ontological Compliance

- **Gist 14.0**: Strict adherence to Category, Magnitude, Event patterns
- **GNUB (GORE Ñuble)**: 199 classes mapped to PostgreSQL schema
- **TDE (Transformación Digital del Estado)**: 19 core classes for digital government
- **ORKO**: Ontology with HAIC constraint (AI agents require `human_accountable_id`)

### Data Quality Gates

Before any schema change or new category scheme:

1. **Categorical Audit**: Check alignment with Gist/GNUB/TDE ontologies
2. **Redundancy Check**: Verify no existing scheme covers the need
3. **Pattern Validation**: Ensure proper use of Category/Magnitude/Junction patterns
4. **Univocity Validation**: Confirm each FK column points to exactly 1 scheme
5. **User Story Traceability**: Confirm requirement derives from validated story

**Audit Tools**:
- Use arquitecto-gore agent role for categorical audits
- Check coherence with: `fn_validate_category_scheme(uuid, varchar)` function
- Verify univocity: Query `COUNT(DISTINCT c.scheme)` for each FK column

---

**Last updated**: 2026-02-24 (Radical cleanup for LLM agent stack transition)
