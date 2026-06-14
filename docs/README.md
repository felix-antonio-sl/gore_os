# GORE_OS — Índice de Documentación

> **SSOT**: [CLAUDE.md](../CLAUDE.md) es la fuente de verdad de arquitectura, modelo de datos, reglas y convenciones.
> Este índice cataloga la documentación secundaria **vigente**. Ante cualquier conflicto, **CLAUDE.md prevalece**.

---

## Puntos de entrada

| Doc | Audiencia | Propósito |
|-----|-----------|-----------|
| [CLAUDE.md](../CLAUDE.md) | Devs, agentes | Arquitectura, modelo de datos, reglas, comandos, convenciones |
| [INDEX.md](../INDEX.md) | Todos | Mapa del repositorio: árbol de directorios + estado del modelo |
| [MANIFESTO.md](../MANIFESTO.md) | Todos | Identidad, filosofía Story-First, 5 funciones motoras |
| [ONBOARDING.md](ONBOARDING.md) | Nuevos devs | Setup local, patrones clave, flujo de nueva feature |

## Dominio y requisitos (vigente)

| Documento | Contenido |
|-----------|-----------|
| [GORE_OS_User_Journeys_v3.0.md](GORE_OS_User_Journeys_v3.0.md) | 8 arquetipos, 16 journeys + IPR 360 transversal, 8 principios UX |
| [GORE_OS_User_Action_Trees_v1.0.md](GORE_OS_User_Action_Trees_v1.0.md) | 24 usuarios × rutas → árboles de acción (lectura/escritura/destructiva) + endpoints + scoping IDOR |
| [GORE_OS_Role_Surface_Spec_v1.0.md](GORE_OS_Role_Surface_Spec_v1.0.md) | Matriz 15 roles × páginas + recomendaciones de poda R1-R7 (implementadas) |
| [DGI_USER_STORIES_v1.0.md](DGI_USER_STORIES_v1.0.md) | 185 historias de usuario DGI (backlog de requisitos) |
| [GORE_OS_Story_Coverage_v1.0.md](GORE_OS_Story_Coverage_v1.0.md) | Cobertura historia DGI→página (snapshot C60 — parcialmente desactualizado: varias páginas marcadas "NUEVO" ya existen) |
| [AUDITORIA_RELACIONAL_v1.0.md](AUDITORIA_RELACIONAL_v1.0.md) | Mapa relacional: hubs de FKs, cadenas de navegación, queries reutilizables (cifras de cabecera = baseline 2026-01-30) |

## Auditoría institucional

| Documento | Fecha | Contenido |
|-----------|-------|-----------|
| [GORE_OS_Audit_v3.0.md](GORE_OS_Audit_v3.0.md) | 2026-03-08 | Scorecard CQ (472 CQs, 15 HΩ), cobertura ontológica, gap analysis. **Snapshot fechado** — los conteos de infraestructura están congelados; el estado vigente vive en CLAUDE.md. |

## Testing

| Documento | Contenido |
|-----------|-----------|
| [GORE_OS_Testing_Ciclo3.md](GORE_OS_Testing_Ciclo3.md) | Guía de testing primaria: suite completa, SISREC, tablas paramétricas, presupuesto |
| [GORE_OS_Testing_Manual_v1.0.md](GORE_OS_Testing_Manual_v1.0.md) | Plan de pruebas manual/visual por rol (sesión C59) |

## ETL y pipeline de datos

| Documento | Contenido |
|-----------|-----------|
| [ETL_DATA_BOUNDARY.md](ETL_DATA_BOUNDARY.md) | **Operativo**: frontera fuentes canónicas vs staging runtime, workflow `stage_etl_data.sh` |
| [ETL_ARCHITECTURE_v1.0.md](ETL_ARCHITECTURE_v1.0.md) | Diseño ETL original (8 dominios) — **implementado** en `api/scripts/etl/` (8 loaders; el roster final divergió del diseño) |

## Specs de features

| Documento | Contenido |
|-----------|-----------|
| [SPEC_Bug_Capture_System_v1.0.md](SPEC_Bug_Capture_System_v1.0.md) | Captura de bugs in-app (FAB + drawer, solo dev) — implementado |

## Decisiones de arquitectura (ADRs)

> Tabla canónica de ADRs. INDEX.md referencia esta tabla en lugar de duplicarla.

| ADR | Tema | Estado |
|-----|------|--------|
| [ADR-001](adr/ADR-001-meta-schema.md) | Retención del schema `meta` | Accepted |
| [ADR-002](adr/ADR-002-raw-sql.md) | Raw SQL via `text()` (sin ORM) | Accepted |
| [ADR-003](adr/ADR-003-advisory-locks.md) | Advisory locks para generadores de código | Accepted |
| [ADR-004](adr/ADR-004-category-pattern.md) | Category Pattern (`ref.category`) | Accepted |
| [ADR-005](adr/ADR-005-test-strategy.md) | Tests de integración contra PostgreSQL real | Accepted |
| [ADR-006](adr/ADR-006-jwt-cookie-migration.md) | Migración JWT → cookies | **Deferred** |
| [ADR-007](adr/ADR-007-categorical-univocity.md) | Univocidad categorial 100% | Accepted |
| [ADR-008](adr/008-create-pattern-drawer-vs-page.md) | Drawer vs página para `/nuevo` | Accepted |

## Documentación de modelo

| Documento | Contenido |
|-----------|-----------|
| [../model/model_goreos/docs/GOREOS_ERD_v3.md](../model/model_goreos/docs/GOREOS_ERD_v3.md) | ERD + diccionario de datos — **parcial**: documenta 42/89 tablas core (modelo base v3.0); el schema vigente está en `goreos_ddl.sql` |
| [../model/model_goreos/docs/GOREOS_CONCEPTUAL_MODEL.md](../model/model_goreos/docs/GOREOS_CONCEPTUAL_MODEL.md) | Modelo conceptual de negocio (6 áreas de dominio) |
| [../model/model_goreos/docs/DESIGN_DECISIONS.md](../model/model_goreos/docs/DESIGN_DECISIONS.md) | Razonamiento de diseño DB: ENUM vs category, JSONB, particionamiento (el "por qué" de las reglas) |
| [../model/model_goreos/docs/GOREOS_NORMALIZATION_ANALYSIS.md](../model/model_goreos/docs/GOREOS_NORMALIZATION_ANALYSIS.md) | Verificación de formas normales (retrospectivo, baseline v3.0) |
| [../model/GLOSARIO.yml](../model/GLOSARIO.yml) | 57 términos institucionales |

## Material archivado (no operativo)

Conservado solo por trazabilidad. Ver [archive/README.md](archive/README.md).

| Carpeta | Contenido |
|---------|-----------|
| [archive/plans-implemented/](archive/plans-implemented/) | Planes implementados (`docs/plans/` + `docs/superpowers/`) — diseño superado por el código |
| [archive/audits-closed/](archive/audits-closed/) | Auditorías cerradas: Specification v1.0, Audit C59 (remediada), Audit Detail v1.0, UX Audit v2.0, mockups |
| [archive/normalization-completed/](archive/normalization-completed/) | Normalización JSONB→relacional, completada (159 CHECK, 100% univocidad) |
| [archive/planning-feb2026/](archive/planning-feb2026/) | Fases ETL feb-2026, planes de test backend, diseño UI temprano |
| [archive/legacy-model-tel/](archive/legacy-model-tel/) | Fuentes ETL legacy, reportes de normalización v2/v3, navegador relacional |
