# Modelo de Datos GORE_OS

> Para el contrato de arquitectura y cambios: ver [../../AGENTS.md](../../AGENTS.md).

**Estado**: Ejecutable y auditado
**PostgreSQL**: 16+
**Tablas**: 128 en 5 schemas (core, txn, public, meta, ref)
**Schemes**: 105 vocabularios controlados (Category Pattern)
**CHECK constraints**: 178 (incluye `fn_validate_category_scheme`) + triggers de transición/timing (89 totales)
**Univocidad categorial**: 100% (0 FK→ref.category sin protección)

---

## Schemas

| Schema | Tablas | Propósito |
|--------|--------|-----------|
| `meta` | 5 | Átomos fundamentales (Role, Process, Entity, Story, Story-Entity) |
| `ref` | 3 | Vocabularios controlados: `ref.category(scheme, code, label)` + `ref.actor` + `ref.operational_commitment_type` |
| `core` | 89 | Entidades de negocio (IPR, agreements, budget, work items, etc.) |
| `txn` | 20 | Event sourcing particionado (`event` + `magnitude`, 18 particiones) |
| `public` | 11 | Capa de modelado Story-First (`dim_*`, `fact_user_story`, `bridge_*`) |

## Entidad Central: IPR

**Intervención Pública Regional** — polimórfica (8 tipos: INFRAESTRUCTURA, EQUIPAMIENTO, CONSERVACION, TRANSFERENCIA, SUBSIDIO, ESTUDIO, PROGRAMA_SOCIAL, PROGRAMA_8PCT).

- 32 estados + fase derivada (STATUS_PHASE_FIBER)
- Nature-aware: PROYECTO vs PROGRAMA bifurcan flujos
- 18 tabs (Resumen + 17 satélites: compromisos, problemas, hitos, avances, alertas, CDPs, convenios, rendiciones, resoluciones, partes, territorio, evaluación, parentesco, admisibilidad, modificaciones, cierre, ex-post)

## Category Pattern

Cada FK → exactamente UN scheme de `ref.category`. Verificar schemes existentes antes de crear:

```sql
SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;
```

## Archivos SQL

| Archivo | Propósito |
|---------|-----------|
| `sql/goreos_ddl.sql` | Baseline canónico y ejecutable en DB fresca (schemas, tablas, funciones, particiones) |
| `sql/goreos_ddl_production.sql` | Snapshot anterior sin owners; excluido del bootstrap automático |
| `sql/goreos_seed.sql` | Vocabularios controlados (105 schemes) |
| `sql/goreos_seed_territory.sql` | Territorio Región de Ñuble (3 provincias, 21 comunas) |
| `sql/goreos_triggers.sql` | Triggers de negocio |
| `sql/goreos_indexes.sql` | Índices de optimización |
| `sql/goreos_seed_realistic.sql` | Seed realista (~2,200 registros, prefijo DEMO-R-) |
| `sql/goreos_seed_demo_ciclo2.sql` | Seed demo (~50 registros, prefijo DEMO-) |
| `sql/goreos_migration_*.sql` | Migraciones incrementales |
| `sql/goreos_rollback_*.sql` | Rollbacks correspondientes |

**Bootstrap fresco**: aplicar, en este orden, `goreos_ddl.sql`, `goreos_seed.sql`
y `goreos_seed_territory.sql`. Las migraciones, rollbacks, identidades y seeds demo
quedan fuera del arranque automático. Verificar el circuito con
`./scripts/verify_fresh_db.sh` desde la raíz del repositorio.

**Instalación existente**: nombrar explícitamente las migraciones y su orden. El
runner aplica todo el lote pendiente en una transacción, registra su checksum y
rechaza la ejecución implícita de todos los archivos:

```bash
./scripts/run_migrations.sh \
  --container goreos_db \
  --database goreos_model \
  goreos_migration_primera.sql \
  goreos_migration_segunda.sql
```

Lote ordenado de la refactorización de autoridad transaccional:

```bash
./scripts/run_migrations.sh \
  goreos_migration_act_state_cross_cutting.sql \
  goreos_migration_rendition_escalation_uniqueness.sql \
  goreos_migration_bottleneck_fsm.sql \
  goreos_migration_indicator_catalogs_fsm.sql \
  goreos_migration_process_catalogs_fsm.sql \
  goreos_migration_opportunity_fsm.sql \
  goreos_migration_service_request_active_guard.sql \
  goreos_migration_report_catalogs_fsm.sql \
  goreos_migration_dmaic_catalog_fsm.sql \
  goreos_migration_session_lifecycle_authority.sql \
  goreos_migration_evaluation_result_authority.sql \
  goreos_migration_session_agreement_status_authority.sql \
  goreos_migration_budget_cycle_completion_authority.sql
```

## Documentación del Modelo

| Documento | Contenido |
|-----------|-----------|
| [docs/GOREOS_ERD_v3.md](docs/GOREOS_ERD_v3.md) | Diagramas ER + diccionario de datos completo |
| [docs/GOREOS_CONCEPTUAL_MODEL.md](docs/GOREOS_CONCEPTUAL_MODEL.md) | Modelo conceptual de negocio |
| [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md) | Decisiones de diseño (ENUM vs Category, JSONB, indexing, particionamiento) |
| [docs/GOREOS_NORMALIZATION_ANALYSIS.md](docs/GOREOS_NORMALIZATION_ANALYSIS.md) | Análisis de normalización (50 tablas) |

## Principios de Diseño

1. **Story-First**: 818 historias → 141 entidades → 128 tablas → módulos
2. **Categorical Univocity**: Cada FK a ref.category usa exactamente 1 scheme
3. **Auditoría universal**: `created_at/by_id`, `updated_at/by_id`, `deleted_at/by_id` en todas las entidades
4. **Soft delete**: `WHERE deleted_at IS NULL` (no triggers DB)
5. **Integridad semántica**: CHECK constraints + triggers de transición enforced a nivel DB
6. **UUID universal**: PK UUID en todas las entidades
7. **Advisory locks**: `pg_advisory_xact_lock(hashtext('entity_code'))` antes de `SELECT MAX(...)`
