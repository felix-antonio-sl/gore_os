# Auditoría Categorial — GORE_OS v3.0 (`model/model_goreos`)

**Fecha**: 2026-01-27  
**Auditor**: Arquitecto Categórico (Teoría de Categorías aplicada a dominios de datos)  
**Directorio auditado**: `model/model_goreos/`  
**Artefactos**: `goreos_ddl.sql`, `goreos_indexes.sql`, `goreos_triggers.sql`, `goreos_seed*.sql`, documentación en `docs/`.

---

## 0) Clasificación DIK y modo de auditoría

- **INFORMATION (dominante)**: esquema relacional, seeds, índices, triggers como especificación ejecutable.
- **KNOWLEDGE (embebido)**: invariantes declaradas (auditoría, HAIC), patrones (Category/Magnitude/Event), trazabilidad ontológica.
- **Modo**:
  - **STATIC**: estructura, referencias, completitud, calidad.
  - **TEMPORAL**: particionamiento, cadena de versión/mantenibilidad.
  - **BEHAVIORAL**: triggers, validación de transiciones, auditoría/event sourcing.

---

## 1) Métricas (hechos observables)

- **Tablas lógicas**: 50; **tablas físicas**: 68 (18 particiones). Ver `model/model_goreos/goreos_ddl.sql:1417`.
- **Schemas**: `meta` (5), `ref` (3), `core` (40), `txn` (2 particionadas).
- **FKs a `ref.category(id)`**: 70 (alto acoplamiento intencional al *Category Pattern*). Ver `model/model_goreos/goreos_ddl.sql:237`.
- **Referencias polimórficas** por par (`subject_type`, `subject_id`): `core.alert`, `core.risk`, `txn.event`, `txn.magnitude`. Ver `model/model_goreos/goreos_ddl.sql:1357`.

---

## 2) Fixes aplicados durante esta auditoría (2026-01-27)

- **Seed territorial corregido (UUID vs INTEGER)**: `model/model_goreos/goreos_seed_territory.sql:169`.
- **Jerarquía de categorías materializada (parent_code → parent_id)**: `model/model_goreos/goreos_seed.sql:914`.
- **Semántica de transiciones corregida** (incluye `[]` como terminal y evita validar si no cambia estado): `model/model_goreos/goreos_triggers.sql:107`.
- **Docs alineadas a DDL** (txn.magnitude `as_of_date`, campos de auditoría en txn, etc.): `model/model_goreos/docs/GOREOS_ERD_v3.md:502`.
- **Conceptual actualizado a fases MCD reales (F0–F5)**: `model/model_goreos/docs/GOREOS_CONCEPTUAL_MODEL.md:92`.

---

## 3) Hallazgos por dimensión (severidad + patrón)

### 3.1 STATIC — Estructura

**HIGH — STR-001 (BROKEN-DIAGRAM): Doble codificación de jerarquía en `ref.category` sin invariante**

- **Síntoma**: `ref.category` modela jerarquía con `parent_id` *y* `parent_code`, pero no hay regla que garantice conmutatividad (consistencia) entre ambos.
- **Evidencia**: columna dual `model/model_goreos/goreos_ddl.sql:237` + resolución agregada en seed `model/model_goreos/goreos_seed.sql:914`.
- **Impacto**: deriva silenciosa (actualizaciones manuales rompen navegación jerárquica).
- **Recomendación**:
  1) Declarar **canónico** `parent_id` y tratar `parent_code` como derivado (o eliminarlo en vNext), o  
  2) Añadir trigger/constraint de sincronización (si ambos existen, deben coincidir).

**MEDIUM — STR-002 (REQUIRES_ACYCLIC): jerarquías sin garantía de aciclicidad**

- **Zonas**: `ref.category.parent_id`, `core.organization.parent_id`, `core.territory.parent_id`.
- **Impacto**: ciclos rompen cierres transitivos, reportes y agregaciones (árbol deja de ser árbol).
- **Recomendación**: prevención de ciclos por trigger (DFS/CTE) o adoptar **closure table** / `ltree` para jerarquías críticas.

**LOW — STR-003 (AD-HOC-CONSTRUCTION): “metadata JSONB” sin contrato mínimo**

- **Síntoma**: `metadata JSONB` en casi todas las tablas, pero sin `CHECK (jsonb_typeof(metadata)='object')`.
- **Impacto**: degradación de calidad (arrays/strings accidentales), índices GIN menos predecibles.
- **Recomendación**: check constraint mínima + convención de claves (p.ej. `source`, `confidence`, `external_ids`).

---

### 3.2 STATIC — Referencialidad / Integridad semántica

**HIGH — REF-001 (NON-FUNCTORIAL): FKs a `ref.category` sin restricción por `scheme`**

- **Síntoma**: columnas como `mcd_phase_id`, `mechanism_id`, `system_role_id`, `event_type_id`, etc. referencian `ref.category(id)` pero no fuerzan pertenecer al `scheme` correcto.
- **Evidencia**: ejemplo `core.ipr` (`mcd_phase_id`, `status_id`, `mechanism_id`) en `model/model_goreos/goreos_ddl.sql:618`; helper existe pero no se usa: `model/model_goreos/goreos_ddl.sql:1545`.
- **Impacto**: integridad referencial ≠ integridad semántica (se pueden insertar combinaciones inválidas sin error).
- **Recomendación** (en orden de costo/beneficio):
  1) Triggers ligeros por tabla/columna (validate scheme) usando `fn_validate_category_scheme(...)`.
  2) Vistas tipadas por scheme + FKs a vistas (patrón “typed category”).
  3) Desnormalizar en tablas ref específicas si el dominio lo justifica (cuando el scheme se estabiliza).

**HIGH — REF-002 (AD-HOC COPRODUCT / DANGLING-REF): referencias polimórficas (`subject_type`, `subject_id`)**

- **Dónde**: `core.alert`, `core.risk`, `txn.event`, `txn.magnitude`. Ver `model/model_goreos/goreos_ddl.sql:1357`.
- **Impacto**: no hay FK posible → riesgo de `subject_id` huérfano, `subject_type` inválido, y “joins” manuales.
- **Recomendación**:
  - Opción A (mínima): restringir `subject_type` a un catálogo (p.ej. `meta.entity.code`) y validar existencia por trigger.
  - Opción B (robusta): introducir un **registro global de entidades** (p.ej. `core.subject`) y referenciar por `subject_pk`.

**MEDIUM — REF-003 (VERSION-MISMATCH): event/magnitude con PK compuesto no reflejado como invariante en docs**

- **Hecho**: por particionamiento, PK incluye clave de partición (`(id, occurred_at)` / `(id, as_of_date)`).
- **Evidencia**: `model/model_goreos/goreos_ddl.sql:1417` y `model/model_goreos/goreos_ddl.sql:1476`.
- **Riesgo**: consumidores asumen “id único global” y fallan al modelar integraciones/ETL.
- **Recomendación**: documentar explícitamente el *invariante* (“id único por partición”) o migrar a PK global vía secuencia/UUID + UNIQUE por partición.

**LOW — REF-004 (QUALITY): ausencia de `ON DELETE`/`ON UPDATE` explícitos en FKs “de negocio”**

- **Impacto**: las reglas quedan implícitas (NO ACTION) y el comportamiento ante borrados/archivos (soft delete) se vuelve dependiente de aplicación.
- **Recomendación**: declarar explícitamente en relaciones críticas (RESTRICT/CASCADE/SET NULL) o documentar la política por schema.

---

### 3.3 STATIC — Completitud (invariantes “declaradas” vs “enforced”)

**HIGH — CPL-001 (MISSING-PROC): transiciones de estado modeladas pero no aplicadas**

- **Hecho**: se siembran `valid_transitions` (`model/model_goreos/goreos_seed.sql:753`) y existe función trigger `fn_validate_state_transition()` (`model/model_goreos/goreos_triggers.sql:107`), pero **no hay triggers activos** que la ejecuten.
- **Impacto**: el grafo de estados es *documentación*, no regla; deriva de proceso sin alerta.
- **Recomendación**: activar triggers `BEFORE UPDATE OF status_id` en tablas con `status_id` (p.ej. `core.ipr`, `core.budget_commitment`, `core.session_agreement`, `core.electronic_file`, `core.risk`).

**HIGH — CPL-002 (MISSING-PROC): auditoría/event sourcing disponible pero deshabilitado**

- **Hecho**: `fn_audit_to_event()` existe, pero triggers están comentados como “opcionales”. Ver `model/model_goreos/goreos_triggers.sql:384`.
- **Impacto**: se pierde trazabilidad automática; el sistema se vuelve “best effort” a nivel aplicación.
- **Recomendación**: separar en archivo `goreos_triggers_optional.sql` o usar *feature flags* DB (schema `cfg`) para activar por ambiente.

**MEDIUM — CPL-003 (MISSING-PROC): soft delete inconsistente**

- **Hecho**: columnas `deleted_at/deleted_by_id` están en casi todas las tablas, pero triggers de soft delete están comentados. Ver `model/model_goreos/goreos_triggers.sql:405`.
- **Impacto**: “soft delete” queda como convención (cada consumidor decide).
- **Recomendación**: definir política única: (A) soft delete en DB (triggers + vistas *_active), o (B) soft delete solo en app (y documentar).

**LOW — CPL-004 (QUALITY): auditoría `*_by_id` sin auto-populación**

- **Hecho**: existe `set_current_user()`/`get_current_user()`; no hay triggers que rellenen `created_by_id/updated_by_id`. Ver `model/model_goreos/goreos_triggers.sql:429`.
- **Recomendación**: triggers genéricos por schema para poblar `*_by_id` desde `app.current_user_id` (con fallback seguro).

---

### 3.4 STATIC — Calidad (nombres, coherencia, performance)

**HIGH — QLT-001 (EXECUTABILITY RISK): índice por año sobre `TIMESTAMPTZ` puede fallar según versión/config**

- **Evidencia**: `idx_ipr_year` usa `EXTRACT(YEAR FROM created_at)` en `model/model_goreos/goreos_indexes.sql:63`.
- **Riesgo**: expresiones sobre `timestamptz` pueden no ser **IMMUTABLE** (dependen de timezone), lo que rompe `CREATE INDEX` en PostgreSQL.
- **Recomendación**: cambiar a una expresión explícita e inmutable (p.ej. `created_at AT TIME ZONE 'UTC'`) o indexar por rango de fechas (más típico).

**MEDIUM — QLT-002 (BROKEN-DIAGRAM): docs no declaran “nivel” (conceptual vs físico) como contrato**

- **Síntoma**: ERD/Conceptual mezclan simplificaciones (omiten campos de auditoría/PK compuestos) con afirmaciones técnicas.
- **Recomendación**: en cada doc, fijar explícitamente “**nivel**” (Business/Logical/Physical) y “**fuente de verdad**” (DDL vs doc).

**MEDIUM — QLT-003 (PERF): ausencia de verificación sistemática de índices para FKs**

- **Síntoma**: hay archivo de índices dedicado, pero no hay “checklist” que garantice que cada FK caliente tenga índice (especialmente en tablas grandes como `core.work_item`, `txn.*`).
- **Recomendación**: script de auditoría SQL (`pg_catalog`) que liste FKs sin índice y los CQs que los motivan.

**LOW — QLT-004 (CONSISTENCY): checks de no-negatividad incompletos**

- **Hecho**: existe `chk_budget_commitment_amount` (`model/model_goreos/goreos_ddl.sql:589`), pero no está extendido a otros montos (`agreement`, cuotas, etc.).
- **Recomendación**: estandarizar constraints `amount >= 0` / `percentage BETWEEN 0 AND 100` donde aplique.

---

## 4) TEMPORAL — Evolución y operación

**HIGH — TMP-001 (TECH_DEBT): particiones “año fijo” (2026) + default**

- **Hecho**: particiones creadas solo para 2026 + partición default. Ver `model/model_goreos/goreos_ddl.sql:1447` y `model/model_goreos/goreos_ddl.sql:1498`.
- **Impacto**: a partir de 2027, crecimiento cae en `*_default` → degrada rendimiento y mantenimiento.
- **Recomendación**: job anual (o función `create_partitions(year)`) que cree particiones futuras + índices.

**MEDIUM — TMP-002 (VERSION_CHAIN): DDL monolítico vs migraciones incrementales**

- **Síntoma**: `DROP TYPE ... CASCADE` y recreación total sirven para “rebuild”, no para evolución.
- **Recomendación**: adoptar cadena de migraciones (Flyway/Liquibase/SQL-migrations) + reglas “no destructivas” por defecto.

**LOW — TMP-003 (CATALOG): falta artefacto “changelog” del modelo**

- **Recomendación**: `docs/CHANGELOG_MODEL.md` con invariantes añadidas/rotas por versión.

---

## 5) BEHAVIORAL — Triggers y preservación de invariantes

**HIGH — BEH-001 (INTERFACE_CONFORMANCE): invariantes críticas están “opt-in”**

- **Ejemplos**: auditoría a evento, soft delete, validación de transiciones.
- **Impacto**: el comportamiento real depende del orden/archivo ejecutado y de si se descomentó.
- **Recomendación**: separar “core invariants” (siempre ON) de “features” (opt-in) con mecanismo explícito de activación.

**MEDIUM — BEH-002 (QUALITY): dependencia tácita de `app.current_user_id`**

- **Hecho**: funciones asumen `current_setting('app.current_user_id', true)::UUID`. Ver `model/model_goreos/goreos_triggers.sql:18`.
- **Riesgo**: si se setea mal (string no-UUID) rompe en runtime.
- **Recomendación**: capa defensiva (try/catch o validación) + guía de integración para apps.

**LOW — BEH-003 (OBSERVABILITY): falta “smoke test” ejecutable (SQL)**

- **Recomendación**: script `docs/SMOKE_TESTS.sql` que ejecute ST-001..ST-008 en una BD vacía.

---

## 6) Backlog recomendado (priorizado)

- **P0 (integridad inmediata)**: activar y probar (en ambiente dev) triggers de transiciones + esquema tipado de `ref.category` (REF-001/CPL-001).
- **P1 (trazabilidad y seguridad de proceso)**: decidir política soft delete + auditoría a `txn.event` (CPL-002/CPL-003).
- **P2 (operación)**: automatizar particiones + auditoría de índices/FKs (TMP-001/QLT-003).
- **P3 (modelo categorial)**: formalizar “coproducto” de sujetos (subject registry) para `txn.*` y `core.alert/risk` (REF-002).

---

**Fin de auditoría categorial (v3.0)**  
*Nota*: Este reporte complementa `docs/AUDITORIA_GORE_OS_v3_2026-01-27.md` con foco en invariantes y preservación estructural.
