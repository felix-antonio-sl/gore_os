# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in this repository.

## Project Overview

GORE_OS is an institutional operating system for the Regional Government of Ñuble (GORE), Chile: an integrated model of data, processes, and organizational capabilities to digitalize operations and enable intelligence-driven decision-making.

**Core philosophy (Story-First + Radical Minimalism)**

- Everything derives from User Stories (819+ validated)
- Strict derivation: **Stories → Entities → Artifacts → Modules**
- No code without a corresponding story

## Current Status (2026-01-29)

- **Database model**: v3.1 complete (**63 tables**, **4 schemas**, **78+ category schemes**)
- **ETL stage 1**: complete (**470 scripts**, **~32K** normalized records, star schema **15 dims + 8 facts**, **23 CSV** outputs)
- **ETL → PostgreSQL migration**: **FASE 1–7 complete**, **43,256** records migrated (see verification queries below)
- **Apps**: Streamlit tooling operational; Flask app pending

### Migration Summary (FASE 1–7)

| FASE | Target(s)                 | Records       | Success        |
| ---- | ------------------------- | ------------- | -------------- |
| 1    | `core.person`             | 111           | 100%           |
| 1    | `core.organization`       | 1,668         | 100%           |
| 2    | `core.ipr`                | 1,973 / 1,974 | 99.9%          |
| 3    | `core.agreement`          | 533           | 100%           |
| 4    | `core.budget_program`     | 25,753        | 100%           |
| 5    | `txn.event` (documentos)  | 2,373         | 100%           |
| 5    | `core.budget_commitment`  | 3,701         | 100%           |
| 6    | `txn.magnitude`           | 3,496         | 100%           |
| 6    | `txn.event` (rendiciones) | 1,667         | 100%           |
| 7    | `core.ipr_territory`      | 1,965         | 95.9% coverage |
| 7    | `core.person_org_link`    | 110           | 100%           |

---

## Quick Start (Docker PostgreSQL)

```bash
docker-compose up -d postgres
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT version();"
```

### Verify migrations (already complete)

```bash
# FASE 1 (counts by metadata.source; totals may differ from table totals/seed data)
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT 'core.person' AS table, COUNT(*) AS migrated
FROM core.person
WHERE metadata->>'source' = 'dim_funcionario'
UNION ALL
SELECT 'core.organization', COUNT(*)
FROM core.organization
WHERE metadata->>'source' = 'dim_institucion_unificada';"
# Expected: person=110, organization=1612

# FASE 2-7 (logical rows)
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT 'core.ipr' AS table, COUNT(*) AS rows FROM core.ipr WHERE deleted_at IS NULL
UNION ALL SELECT 'core.agreement', COUNT(*) FROM core.agreement WHERE deleted_at IS NULL
UNION ALL SELECT 'core.budget_program', COUNT(*) FROM core.budget_program WHERE deleted_at IS NULL
UNION ALL SELECT 'core.budget_commitment', COUNT(*) FROM core.budget_commitment WHERE deleted_at IS NULL
UNION ALL SELECT 'core.ipr_territory', COUNT(*) FROM core.ipr_territory WHERE deleted_at IS NULL
UNION ALL SELECT 'txn.event', COUNT(*) FROM txn.event
UNION ALL SELECT 'txn.magnitude', COUNT(*) FROM txn.magnitude;"
# Expected: ipr=1,973, agreement=533, budget_program=25,753, budget_commitment=3,701,
#           ipr_territory=1,965, event=4,040, magnitude=3,496
```

---

## Architectural Foundation (CRITICAL)

**The heart of GORE_OS is the PostgreSQL data model in `model/model_goreos/`.**

Why the model is the base:

1. **Executable**: DDL + seeds + triggers in `model/model_goreos/sql/` (4 semantic schemas: `meta`, `ref`, `core`, `txn`)
2. **Derived from stories**: 100% traceable to the 819 stories (Story-First)
3. **Audited**: see `model/model_goreos/docs/auditorias/AUDITORIA_CONSOLIDADA_v3_2026-01-27.md`
4. **Category pattern**: `ref.category` (75+ schemes) instead of ENUMs; transitions via JSONB + triggers
5. **Event sourcing hybrid**: `txn.event` + history tables (partitioning month/quarter)
6. **ETL-ready**: `/etl` pipeline produced normalized legacy datasets that feed the model

### 4-Schema semantic structure

| Schema | Tables | Purpose                                                       |
| ------ | ------ | ------------------------------------------------------------- |
| `meta` | 5      | Role/Process/Entity/Story atoms + mapping                     |
| `ref`  | 3      | Controlled vocabularies (Category, Actor, Commitment Types)   |
| `core` | 40+    | Business entities (IPR, Agreements, Budget, Work Items, etc.) |
| `txn`  | 2+     | Event sourcing (Event, Magnitude) - partitioned               |

### Data pipeline

```
etl/sources/ → etl/scripts/ → etl/normalized/ → model/model_goreos (PostgreSQL) → apps/
```

### Model references

- `model/model_goreos/README.md` (install/verify/troubleshoot)
- `model/model_goreos/docs/GOREOS_ERD_v3.md` (ERD + data dictionary)
- `model/model_goreos/docs/DESIGN_DECISIONS.md` (design rationale)
- `architecture/decisions/ADR-003-modelo-como-base.md` (ADR)

---

## Tech Stack

- Backend: Python 3.11+, Flask 3.0.3, SQLAlchemy 2.0.30
- Frontend: Jinja2 + HTMX 2.0.0 + Alpine.js 3.x + Tailwind CSS 3.4.0
- DB: PostgreSQL 16 + PostGIS
- Auth: Flask-Login + ClaveÚnica
- Infra: Docker/Compose, Gunicorn, Nginx
- Jobs: Celery + Redis
- ETL: Pandas 2.0+, DuckDB 0.9.2, NetworkX

---

## Domain Model (quick)

Central abstract entity: **IPR (Intervención Pública Regional)** (polymorphic)

- Types: PROYECTO (capital) vs PROGRAMA (current)
- Funding: FNDR, FRIL, FRPD, ISAR
- Evaluation: SNI, C33, FRIL, Glosa 06, 8% FNDR, Transfers

Critical entities:

- EstadoPago (EEPP): REVISION → OBSERVADO → APROBADO → PAGADO
- ResolucionModificatoria (budget/timeframe amendments)
- Funcionario (ANALISTA, JEFE, VISADOR)
- Unidad (DIPIR, DAF, JURIDICA)
- WorkItem (unified work atom: stories/commitments/problems/alerts)

Core processes:

- PAYMENT_CYCLE (7-step financial execution)
- AMENDMENT_CYCLE (4-step budget modification + CGR notification)
- Sense-Decide-Act (SDA) operational loop

---

## Database Setup (from scratch)

**Run the 8 SQL files in strict order** from `model/model_goreos/sql/`:

```bash
createdb -U postgres goreos
cd model/model_goreos/sql
for f in goreos_ddl.sql goreos_seed.sql goreos_seed_agents.sql goreos_seed_territory.sql \
         goreos_triggers.sql goreos_triggers_remediation.sql goreos_indexes.sql \
         goreos_remediation_ontological.sql; do
  psql -U postgres -d goreos -f "$f"
done
```

Install checks (Docker):

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
  SELECT schemaname, COUNT(*) AS tables
  FROM pg_tables
  WHERE schemaname IN ('meta','ref','core','txn')
  GROUP BY schemaname
  ORDER BY schemaname;"

docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT COUNT(DISTINCT scheme) FROM ref.category;"
```

---

## Directory Structure (high level)

```
architecture/    # ADRs, C1-C4 docs, standards, diagrams
model/           # stories/ roles/ entities/ processes/ + model_goreos/ (DDL + docs)
etl/             # sources/ scripts/ normalized/ + migration/
apps/            # streamlit_tooling/ and flask_app/
catalog/         # KODA federated catalog
```

---

## ETL

### Stage 1 (legacy → normalized): complete

- 470 scripts executed
- 23 CSV outputs in `etl/normalized/`
- ~32,000 records cleaned/validated; Kimball star schema (15 dims + 8 facts)

Key scripts (`etl/scripts/`):

- Profiling: `profile_all.py`, `profile_funcionarios.py`
- Normalization: `normalize_convenios.py`, `normalize_fril.py`, `normalize_progs.py`, `normalize_250.py`
- Enrichment/unification: `enrich_ipr_type.py`, `enrich_institution_type.py`, `semantic_unify_institutions.py`
- Linking/graph: `link_entities.py`, `generate_relationship_matrix.py`
- Migration assessment: `compatibility_assessment.py`

### Normalized outputs (selected)

```
etl/normalized/dimensions/: dim_funcionario (110), dim_institucion_unificada (1,613), dim_iniciativa_unificada (2,049), dim_convenio_ad_hoc (34), dim_territorio (44)
etl/normalized/facts/: fact_linea_presupuestaria (25,754), fact_convenio (533), fact_evento_documental (2,373), fact_ejecucion_mensual (3,496)
etl/normalized/metadata/: institution_id_mapping (150 UUIDs), modificaciones_errors (23)
etl/normalized/relationships/: relationship_matrix (26,045), cross_domain_matches (6,618)
```

### Migration framework (`etl/migration/`)

- Pattern: **LoaderBase** (Load → Transform → Validate → Resolve FKs → Insert/Update)
- Plan: `~/.claude/plans/warm-munching-prism.md`
- Components:
  - `etl/migration/utils/db.py` (SQLAlchemy pool)
  - `etl/migration/utils/validators.py` (schema validators)
  - `etl/migration/utils/resolvers.py` (FK lookup + caching; includes `get_system_user_id()`)
  - `etl/migration/utils/deduplication.py`

Environment setup:

```bash
cd etl
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Migration env/config (defaults match `docker-compose.yml`):

- DB: `localhost:5433`, db `goreos_model`, user `goreos`, pass `goreos_2026`
- Prefer `.env` (see `.env.example`)

Migration quality scores (from `etl/docs/COMPATIBILITY_ASSESSMENT_FRAMEWORK.md`):

| Source              | Score  | Target                      | Key challenge                     |
| ------------------- | ------ | --------------------------- | --------------------------------- |
| `dim_funcionario`   | 85/100 | `core.person` + `core.user` | none                              |
| `dim_institucion`   | 75/100 | `core.organization`         | 5.4% missing RUT                  |
| `dim_iniciativa`    | 67/100 | `core.ipr`                  | complex state mapping (31 states) |
| `fact_convenio`     | 71/100 | `core.agreement`            | LOOKUP_OR_CREATE orgs             |
| `fact_linea_presup` | 47/100 | `core.budget_program`       | reconstruct deltas                |

---

## ETL Loader Rules (CRITICAL)

Mandatory reading before touching `etl/migration/loaders/`:

1. `etl/migration/LECCIONES_APRENDIDAS.md`
2. `etl/migration/PRE_LOADER_CHECKLIST.md`
3. `etl/docs/COMPATIBILITY_ASSESSMENT_FRAMEWORK.md`

### Hard rules

1) **SQLAlchemy 2.0**: wrap SQL with `text()`.

```python
from sqlalchemy import text
session.execute(text("SELECT 1 FROM core.person WHERE id=:id"), {"id": person_id})
```

2) **Verify schema first** (never assume field names):

```bash
PGPASSWORD=goreos_2026 psql -h localhost -p 5433 -U goreos -d goreos_model -c "\d TABLE_NAME"
```

Common mismatches: `core.person.rut` (not `tax_id`), `names` (not `first_name`), `paternal_surname` (not `last_name`); RUT is often nullable; many JSONB fields.

3) **Each loader must override**: `get_natural_key()`, `get_natural_key_from_dict()`, `check_exists()`; and `pre_insert()` if JSONB.

4) **JSONB**: store JSON strings, not Python dicts.

```python
import json
row["metadata"] = json.dumps(row["metadata"]) if isinstance(row.get("metadata"), dict) else row.get("metadata")
```

JSONB tables: `core.person.metadata`, `core.organization.metadata`, `core.ipr.metadata`, `txn.event.payload`.

5) **System user** (`get_system_user_id()`): must have `password_hash`, `system_role_id` (scheme=`system_role`, code=`ADMIN_SISTEMA`), `person_id` (FK to `core.person`).

6) **Update validators first**: edit `etl/migration/utils/validators.py` for correct fields/NOT NULL/format/ranges *before* writing the loader.

Known issue: if you hit **"bind parameter required"** on update, override `update_record()` to use the same WHERE clause as `check_exists()` (see `etl/migration/LECCIONES_APRENDIDAS.md` §10).

### Execution workflow (per loader)

Schema discovery → validator update → resolvers → loader → dry run → 10-row subset → SQL verification → full run → post-validation.

Success criteria: success ≥95%, FK integrity 100%, no duplicate natural keys, warnings ≤5%, errors ≤1%.

Checklist (compact):

```
[schema] \d table; NOT NULL/UNIQUE/FK/JSONB documented
[validators] implemented + routed
[resolvers] lookup_* cached; all SQL uses text()
[loader] natural_key + exists + JSONB pre_insert + created_by_id
[tests] dry_run → subset(10) → verify queries → full
```

---

## Common Loader Patterns

Caching FK lookups:

```python
_fk_cache = {}
cache_key = f"entity:{key}"
```

Mapping legacy values to `ref.category`:

```python
code = mapping.get(str(value).upper(), "DEFAULT_CODE")
category_id = lookup_category("scheme_name", code)
```

---

## Ontology & Compliance

- **ORKO**: 5 axioms (Transformation, Capacity, Information, Constraint, Intentionality) + 5 primitives (Capacity, Flow, Information, Boundary, Purpose); HAIC constraint: AI agents require `human_accountable_id`.
- **KODA**: federation pattern; agents seeded in `model/model_goreos/sql/goreos_seed_agents.sql`.
- **TDE compliance**: ClaveÚnica, DocDigital, PISEE, SIAPER/CGR, SIGFE/DIPRES, MercadoPúblico; Once-Only + Digital Default.

---

## Semantic Model (Stories → Entities)

```
model/stories/*.yml (819 stories) → model/entities/aceptadas/*.yml (139 entities) → model/model_goreos/sql/goreos_ddl.sql → Flask blueprints (when implemented)
```

Story example:

```yaml
id: ST-FIN-001
title: "Aprobar Estado de Pago"
actor: Jefe de Inversiones
goal: "Validar avance físico/financiero de proyecto"
related_entities: [EstadoPago, IPR, Funcionario]
```

Entity example:

```yaml
id: ENT-FIN-EEPP
name: EstadoPago
origin_stories: [ST-FIN-001, ST-FIN-002, ST-FIN-003]
```

---

## Key Docs (start here)

- `INDEX.md` (repo navigation)
- `MANIFESTO.md` (identity + genesis)
- `architecture/Omega_GORE_OS_Definition_v3.0.0.md` (system spec)
- `architecture/stack.md` and `architecture/standards/` (stack + standards + anti-patterns)
- `docs/technical/` (planclaude, gestion, especificaciones)
- `etl/README.md` and `etl/docs/` (migration matrix + assessment framework)

---

## DB Connection (dev)

- Host `localhost`, port `5433`, db `goreos_model`, user `goreos`, pass `goreos_2026`
- Connection string: `postgresql://goreos:goreos_2026@localhost:5433/goreos_model`
- Prefer `docker exec goreos_db psql -U goreos -d goreos_model` for local work
- Never commit `.env` (already in `.gitignore`)
- Dev-only credentials; use secrets management in production

If `goreos_model` does not exist inside the container:

```bash
docker exec goreos_db createdb -U goreos goreos_model
```

Troubleshooting quick commands:

```bash
docker-compose up -d postgres
docker ps | rg goreos_db || docker ps | grep goreos_db
docker logs goreos_db
docker exec goreos_db psql -U goreos -l
```

Common migration issue (“Category not found”): list schemes/codes before mapping.

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;"
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT code,label FROM ref.category WHERE scheme='ACTUAL_SCHEME_NAME' ORDER BY code;"
```

---

## Recent Changes (2026-01-29 remediation)

New category schemes in `ref.category`:

| Scheme               | Values | Purpose                                                                                                                                  |
| -------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `resolution_subtype` | 6      | APRUEBA_CONVENIO, MODIFICA_CONVENIO, APRUEBA_PAGO, MODIFICA_PRESUPUESTO, TERMINO_ANTICIPADO, PRORROGA                                    |
| `document_type`      | 12     | CONVENIO, RESOLUCION, DECRETO, ESTADO_PAGO, CERTIFICADO, BOLETA_GARANTIA, INFORME_TECNICO, RENDICION, FACTURA, ORDEN_COMPRA, PLANO, OTRO |
| `role_in_committee`  | 5      | PRESIDENTE, SECRETARIO, VOCAL, ASESOR, INVITADO                                                                                          |

Remediation:

- Fixed malformed RUT in `dim_institucion_unificada.csv`
- Removed 6 `.tmp` files from facts (10,048 lines)
- Removed obsolete backups (`resolvers_broken_backup.py`, `resolvers.py.broken`)
- Updated `.gitignore` with ETL patterns (`*.duckdb`, `*.tmp`, `venv/`, `migration_logs/`)

FASE 2 diagnostics (`etl/migration/DIAGNOSTICO_SOLAPAMIENTO_FUENTES.md`):

- +39 BIPs from “cartera 250” merged into `dim_iniciativa_unificada.csv`
- 34 ad-hoc conventions split to `dim_convenio_ad_hoc.csv` (CVC-AD-XX)
- 3 duplicated BIPs handled (variants in metadata)

IPR distribution:

| Tipo            | Cantidad |
| --------------- | -------- |
| INFRAESTRUCTURA | 1,179    |
| EQUIPAMIENTO    | 413      |
| TRANSFERENCIA   | 292      |
| PROGRAMA_SOCIAL | 57       |
| CONSERVACION    | 22       |
| ESTUDIO         | 10       |

| Fuente    | Registros |
| --------- | --------- |
| IDIS      | 1,933     |
| 250       | 39        |
| CONVENIOS | 1         |

FASE 3–6 highlights:

- FASE 3 (AgreementLoader): 533 agreements; 499 linked to IPR (93.6%); receiver 533/533 (100%)
- FASE 4 (BudgetProgramLoader): 25,753 lines (2019–2025); 10,061 lines >0 (39%); total budget ~4.9B CLP; link via `metadata->>'iniciativa_id'`
- FASE 5 (EventLoader): 2,373 document events; 100% event→agreement FK integrity
- FASE 5 (BudgetCommitment): 3,701 links; coverage 14.4% of budget_program; 98% of IPRs (1,933/1,973) have ≥1 commitment
- FASE 6A (MagnitudeLoader): 3,496 rows; 2019–2025 (78 months); total ~436M CLP
- FASE 6B (RendicionLoader): 1,667 unique codes from 2,401 rows; stored as `txn.event` payload JSONB; total transferred ~1,377M CLP

Budget distribution by year:

| Fiscal Year | Lines | Amount (MM CLP) |
| ----------- | ----- | --------------- |
| 2019        | 5,418 | 2,085           |
| 2020        | 3,972 | 1,484           |
| 2021        | 3,586 | 1,041           |
| 2022        | 3,848 | 211             |
| 2023        | 5,669 | 33              |
| 2024        | 2,637 | 11              |
| 2025        | 623   | 0               |

Budget commitments by year:

| Fiscal Year | Commitments | Amount (MM CLP) |
| ----------- | ----------- | --------------- |
| 2019        | 787         | 304             |
| 2020        | 568         | 212             |
| 2021        | 514         | 149             |
| 2022        | 556         | 39              |
| 2023        | 811         | 4.7             |
| 2024        | 376         | 1.7             |
| 2025        | 89          | -               |

FK integrity (FASE 1–5):

| Relation                   | Linked | Unlinked | %     |
| -------------------------- | ------ | -------- | ----- |
| agreement → ipr            | 499    | 34       | 93.6% |
| agreement → receiver       | 533    | 0        | 100%  |
| event → subject            | 2,373  | 0        | 100%  |
| budget_commitment → ipr    | 3,701  | 0        | 100%  |
| budget_commitment → budget | 3,701  | 0        | 100%  |

Rendiciones by fund:

| Fund           | Records | Primary State |
| -------------- | ------- | ------------- |
| SEGURIDAD      | 514     | COMPLETADO    |
| DEPORTE        | 282     | COMPLETADO    |
| ADULTO_MAYOR   | 219     | PENDIENTE     |
| SOCIAL         | 163     | COMPLETADO    |
| CULTURA        | 152     | COMPLETADO    |
| EQUIDAD_GENERO | 110     | COMPLETADO    |

**Last updated**: 2026-01-29
