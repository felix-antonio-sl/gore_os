# GORE_OS Database Schemas

## Current Version: v3.0

El DDL ejecutable **canónico** se encuentra en:

```
/model/model_goreos/sql/
```

Este directorio contiene los archivos SQL que definen la estructura completa de la base de datos.

---

## Archivos Principales

| Archivo | Propósito |
|---------|-----------|
| `goreos_ddl.sql` | DDL completo del modelo v3.0 (schemas, tablas, funciones, ENUMs) |
| `goreos_seed.sql` | Datos semilla principales (75+ schemes, 350+ categorías) |
| `goreos_seed_agents.sql` | Agentes KODA con constraint HAIC |
| `goreos_seed_territory.sql` | Territorio Región de Ñuble (3 provincias, 21 comunas) |
| `goreos_triggers.sql` | Triggers de negocio (core, siempre activo) |
| `goreos_triggers_remediation.sql` | Triggers de remediación categorial |
| `goreos_indexes.sql` | Índices de optimización |
| `goreos_remediation_ontological.sql` | Remediación ontológica v3.1 (relaciones N:M) |

---

## Instalación desde Cero

**Orden crítico** (no omitir ni reordenar):

```bash
# 0. Crear base de datos
createdb -U postgres goreos

# 1-8. Ejecutar DDL en orden estricto
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

---

## Verificación de Instalación

```bash
# Contar tablas por schema (esperado: meta=5, ref=3, core=40+, txn=2+)
psql -U postgres -d goreos -c "
    SELECT schemaname, COUNT(*) AS tables
    FROM pg_tables
    WHERE schemaname IN ('meta', 'ref', 'core', 'txn')
    GROUP BY schemaname
    ORDER BY schemaname;
"

# Verificar seed data (debe retornar 75+)
psql -U postgres -d goreos -c "SELECT COUNT(DISTINCT scheme) FROM ref.category;"
```

---

## Arquitectura de 4 Schemas

| Schema | Tablas | Propósito |
|--------|--------|-----------|
| `meta` | 5 | Átomos fundamentales (Role, Process, Entity, Story, Story-Entity) |
| `ref` | 3 | Vocabularios controlados (Category pattern con 75+ schemes) |
| `core` | 40+ | Entidades de negocio (IPR, Agreements, Budget, Work Items, etc.) |
| `txn` | 2+ | Event Sourcing (Event, Magnitude) - Particionadas |

---

## Documentación Completa

Para documentación detallada del modelo:

- **[model/model_goreos/README.md](../model/model_goreos/README.md)** - Guía completa de instalación y troubleshooting
- **[model/model_goreos/docs/GOREOS_ERD_v3.md](../model/model_goreos/docs/GOREOS_ERD_v3.md)** - ERD completo + Data Dictionary
- **[model/model_goreos/docs/DESIGN_DECISIONS.md](../model/model_goreos/docs/DESIGN_DECISIONS.md)** - Decisiones de diseño explicadas

---

## Migraciones

Para futuras migraciones, seguir patron:

```
db/migrations/
├── v3.0_to_v3.1/
│   ├── 001_add_column_foo.sql
│   └── 002_create_index_bar.sql
└── v3.1_to_v3.2/
    └── ...
```

**Actualmente**: No hay directorio de migraciones. DDL v3.0 es la versión base.

---

Última actualización: 2026-01-29
