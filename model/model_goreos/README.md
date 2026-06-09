# Modelo de Datos GORE_OS

> Para arquitectura completa, comandos y convenciones: ver [../../CLAUDE.md](../../CLAUDE.md)

**Estado**: Ejecutable y auditado
**PostgreSQL**: 16+
**Tablas**: 121 en 4 schemas (meta, ref, core, txn)
**Schemes**: 105 vocabularios controlados (Category Pattern)
**CHECK constraints**: 98 + 19 triggers de transición + 6 triggers de timing
**Univocidad categorial**: 100% (0 FK→ref.category sin protección)

---

## Schemas

| Schema | Tablas | Propósito |
|--------|--------|-----------|
| `meta` | 5 | Átomos fundamentales (Role, Process, Entity, Story, Story-Entity) |
| `ref` | 3 | Vocabularios controlados: `ref.category(scheme, code, label)` + `ref.actor` + `ref.operational_commitment_type` |
| `core` | 80+ | Entidades de negocio (IPR, agreements, budget, work items, etc.) |
| `txn` | 20+ | Event sourcing particionado |

## Entidad Central: IPR

**Intervención Pública Regional** — polimórfica (8 tipos: INFRAESTRUCTURA, EQUIPAMIENTO, CONSERVACION, TRANSFERENCIA, SUBSIDIO, ESTUDIO, PROGRAMA_SOCIAL, PROGRAMA_8PCT).

- 32 estados + fase derivada (STATUS_PHASE_FIBER)
- Nature-aware: PROYECTO vs PROGRAMA bifurcan flujos
- 16 tabs satélite (compromisos, problemas, alertas, convenios, CDPs, avances, partes, territorio, hitos, resoluciones, evaluación, parentesco, admisibilidad, modificaciones, cierre, ex-post)

## Category Pattern

Cada FK → exactamente UN scheme de `ref.category`. Verificar schemes existentes antes de crear:

```sql
SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;
```

## Archivos SQL

| Archivo | Propósito |
|---------|-----------|
| `sql/goreos_ddl.sql` | Estructura completa (schemas, tablas, funciones, particiones) |
| `sql/goreos_seed.sql` | Vocabularios controlados (105 schemes) |
| `sql/goreos_seed_territory.sql` | Territorio Región de Ñuble (3 provincias, 21 comunas) |
| `sql/goreos_triggers.sql` | Triggers de negocio |
| `sql/goreos_indexes.sql` | Índices de optimización |
| `sql/goreos_seed_realistic.sql` | Seed realista (~2,200 registros, prefijo DEMO-R-) |
| `sql/goreos_seed_demo_ciclo2.sql` | Seed demo (~50 registros, prefijo DEMO-) |
| `sql/goreos_migration_*.sql` | Migraciones incrementales |
| `sql/goreos_rollback_*.sql` | Rollbacks correspondientes |

**Importante**: No aplicar `goreos_ddl.sql` a DB fresca. Usar `pg_dump --schema-only` desde `goreos_model`.

## Documentación del Modelo

| Documento | Contenido |
|-----------|-----------|
| [docs/GOREOS_ERD_v3.md](docs/GOREOS_ERD_v3.md) | Diagramas ER + diccionario de datos completo |
| [docs/GOREOS_CONCEPTUAL_MODEL.md](docs/GOREOS_CONCEPTUAL_MODEL.md) | Modelo conceptual de negocio |
| [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md) | Decisiones de diseño (ENUM vs Category, JSONB, indexing, particionamiento) |
| [docs/GOREOS_NORMALIZATION_ANALYSIS.md](docs/GOREOS_NORMALIZATION_ANALYSIS.md) | Análisis de normalización (50 tablas) |

## Principios de Diseño

1. **Story-First**: 820 historias → 141 entidades → 121 tablas → módulos
2. **Categorical Univocity**: Cada FK a ref.category usa exactamente 1 scheme
3. **Auditoría universal**: `created_at/by_id`, `updated_at/by_id`, `deleted_at/by_id` en todas las entidades
4. **Soft delete**: `WHERE deleted_at IS NULL` (no triggers DB)
5. **Integridad semántica**: CHECK constraints + triggers de transición enforced a nivel DB
6. **UUID universal**: PK UUID en todas las entidades
7. **Advisory locks**: `pg_advisory_xact_lock(hashtext('entity_code'))` antes de `SELECT MAX(...)`
