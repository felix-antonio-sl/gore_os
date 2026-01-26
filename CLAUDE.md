# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GORE_OS is an institutional operating system for the Regional Government of Ñuble (GORE), Chile. It is an integrated model of data, processes, and organizational capabilities designed to digitalize and enable intelligence-driven decision-making for regional government operations.

**Core Philosophy: Story-First & Radical Minimalism**
- Everything derives from User Stories (819+ validated stories)
- Strictly unidirectional derivation: **Stories → Entities → Artifacts → Modules**
- No code exists without a corresponding story

## Technology Stack

- **Backend:** Python 3.11+, Flask 3.0.3 (Application Factory pattern), SQLAlchemy 2.0.30
- **Frontend:** Server-Side Rendering with Jinja2, HTMX 2.0.0, Alpine.js 3.x, Tailwind CSS 3.4.0
- **Database:** PostgreSQL 16 + PostGIS (geospatial for regional planning)
- **Authentication:** Flask-Login integrated with ClaveÚnica (Chilean national identity)
- **Infrastructure:** Docker + Docker Compose, Gunicorn WSGI, Nginx reverse proxy
- **Background Jobs:** Celery with Redis broker
- **ETL:** Pandas, DuckDB, NetworkX

## Architecture

### C2 Container Architecture
- **Nginx** → TLS termination, routing, static files
- **Flask App (Gunicorn)** → SSR with Jinja2, HTMX interactivity, business logic
- **Celery Worker/Beat** → Background processing and scheduling
- **PostgreSQL + PostGIS** → Relational DB with geospatial support
- **Redis** → Message broker and session cache

### C3 Flask Blueprints (Bounded Contexts)
- **BP-FIN** (Finances) → Budget, income/expense, financial conciliation
- **BP-EJEC** (Execution) → Works supervision, municipal agreements, PMO
- **BP-TERR** (Territorial) → Digital Twin, maps, gap analysis
- **BP-NORM** (Normative) → Administrative acts, electronic expedients, digital signature
- **BP-BACK** (Backoffice) → HR, procurement
- **BP-AUTH** → Authentication

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
│   └── omega/             # Omega system models
├── etl/                   # ETL pipeline for legacy data migration
│   ├── sources/           # Legacy data (convenios, FRIL, IDIS, etc.)
│   ├── scripts/           # ~30 Python transformation scripts
│   └── normalized/        # Cleaned & validated output
├── db/                    # Database schemas and migrations
└── catalog/               # KODA federated catalog
```

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

### Core Processes
- **PAYMENT_CYCLE:** 7-step financial execution flow
- **AMENDMENT_CYCLE:** 4-step budget modification with CGR notification

## Ontological Foundation

The project uses two semantic frameworks:

**ORKO (Organizational Knowledge Ontology):**
- 5 Axioms: Transformation, Capacity, Information, Constraint, Intentionality
- 5 Primitives: Capacity, Flow, Information, Boundary, Purpose

**KODA (Knowledge Design Architecture):**
- Federation pattern for distributed knowledge across projects

## Key Documentation Files

- `MANIFESTO.md` - Political genesis and identity, 5 Motor Functions
- `architecture/Omega_GORE_OS_Definition_v3.0.0.md` - System specification v3.0
- `planclaude.md` - Master data model specification
- `gestion.md` - Operational data model
- `especificaciones.md` - Detailed specifications
- `entity_diagram.mmd` - Mermaid class diagram of polymorphic IPR model

## Working with the Codebase

### ETL Development
ETL scripts are in `/etl/scripts/` using Pandas and DuckDB. Install dependencies:
```bash
cd etl && pip install -r requirements.txt
```

### Domain Model
- Stories are YAML files in `model/stories/` - these are the source of truth
- Entities derive from stories and live in `model/entities/aceptadas/`
- The glossary (`model/GLOSARIO.yml`) defines authoritative terminology

### TDE Compliance
GORE_OS integrates with Chilean national digital transformation systems:
- ClaveÚnica (authentication), DocDigital, PISEE, SIAPER/CGR, SIGFE/DIPRES, MercadoPúblico
- Follows Once-Only Principle: consume data via PISEE before asking citizens
- Digital Default: all outgoing documents are digital (XML/PDF signed)
