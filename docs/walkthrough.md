# Walkthrough: Model-First ETL Migration

## Overview
We have successfully implemented the "Model-First" migration infrastructure and Dockerized the entire GORE_OS stack. This ensures that cleaned legacy data is loaded directly into the canonical PostgreSQL schema within a reproducible environment.

## 1. Schema Generation (Model → Database)

Instead of manually creating tables, we generated Drizzle ORM schemas directly from the canonical YAML entity definitions.

**Script:** `gore_os/model/entities/scripts/generate_drizzle_schema.py`
**Output:** `gore_os/src/db/schema/*.ts`

| Domain    | Entities | Key Tables                                   |
| --------- | -------- | -------------------------------------------- |
| **D-ORG** | 16       | `org_funcionario`, `org_division`            |
| **D-FIN** | 31       | `fin_ipr`, `fin_modificacion_presupuestaria` |
| **D-EJE** | 13       | `eje_convenio`                               |
| **Total** | **141**  | **ALL Canonical Entities**                   |

## 2. Migration Executor (ETL → Canonical)

We created a robust executor script that reads cleaned CSVs, transforms data according to the mapping specifications, and inserts it into the canonical tables.

**Script:** `gore_os/etl/scripts/migrate_to_model.py`

### Validation Results (Dry-Run)
The script was validated against the cleaned data sources:

| Source           | Target Table                      | Rows Prepared | Status       |
| ---------------- | --------------------------------- | ------------- | ------------ |
| `funcionarios`   | `org_funcionario`                 | 110           | ✅ Ready      |
| `idis` (SNI)     | `fin_ipr`                         | 1,721         | ✅ Ready      |
| `modificaciones` | `fin_modificacion_presupuestaria` | 54            | ✅ Ready      |
| **Total**        |                                   | **1,885**     | **Verified** |

## 3. Docker Deployment (New!)

Run the entire stack (App + DB + ETL) with a single command.

### Step 1: Start the Stack
```bash
docker-compose up -d --build
```
This starts:
- `db`: PostgreSQL + PostGIS
- `api`: Bun API
- `web`: Frontend
- `etl`: Python Environment (with `etl/` and `model/` mounted)

### Step 2: Create Tables (Schema Push)
Run this from your host (if you have Node installed) or inside the API container:
```bash
# Option A: From Host
bunx drizzle-kit push

# Option B: From Container
docker exec -it gore_api bunx drizzle-kit push
```

### Step 3: Run Migration
Execute the Python migration script inside the ETL container:
```bash
docker exec -it gore_etl python3 etl/scripts/migrate_to_model.py
```
*Wait for "✅ Migration completed successfully"*

### Step 4: Verify
Check that the data is available in the database:
```bash
docker exec -it gore_db psql -U gore -d gore_os -c "SELECT count(*) FROM fin_ipr;"
```

## 4. Key Decisions & Architecture
- **Canonical Target:** We bypassed staging tables (`mleg_*`) and targeted canonical tables (`fin_ipr`) directly for higher efficiency.
- **Auto-Generated Schemas:** Guaranteed 100% alignment between YAML models and DB tables.
- **Dockerized ETL:** The ETL process runs in an isolated Python container connected to the same network as the database, ensuring zero dependency conflicts.
