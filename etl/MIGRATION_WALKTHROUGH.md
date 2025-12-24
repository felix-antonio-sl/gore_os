# Walkthrough: Model-First ETL Migration

## Overview
We have successfully implemented the "Model-First" migration infrastructure. This ensures that cleaned legacy data is loaded directly into the canonical GORE_OS PostgreSQL schema, creating a robust foundation for the system.

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

## 3. How to Execute

To finalize the migration, follow these steps with database access:

### Step 1: Create Database Tables
```bash
# Apply generated schemas to PostgreSQL
cd gore_os
bunx drizzle-kit push
```

### Step 2: Run Migration
```bash
# Execute the data load
export DATABASE_URL="postgresql://user:pass@localhost:5432/goreos"
python3 etl/scripts/migrate_to_model.py
```

## 4. Key Decisions & Architecture
- **Canonical Target:** We bypassed staging tables (`mleg_*`) and targeted canonical tables (`fin_ipr`) directly for higher efficiency.
- **Auto-Generated Schemas:** Guaranteed 100% alignment between YAML models and DB tables.
- **Python Executor:** Chosen for robust CSV handling and transformation capabilities (e.g., Chilean currency parsing).
