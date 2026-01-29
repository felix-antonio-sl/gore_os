# Auditoría del Modelo de Datos `model/model_goreos` (GORE_OS v3.0)

Fecha: 2026-01-27  
Auditor: Experto en diseño de modelos y bases de datos

## Alcance
Directorio auditado: `model/model_goreos/`

Archivos:
- `goreos_ddl.sql`
- `goreos_indexes.sql`
- `goreos_seed.sql`
- `goreos_seed_agents.sql`
- `goreos_seed_territory.sql`
- `goreos_triggers.sql`

Objetivo:
- Auditoría exhaustiva por archivo y auditoría cruzada (consistencia lógica y formal).
- Identificar bloqueos de ejecución, incoherencias de modelado y riesgos operativos/performance.

## Resumen ejecutivo (crítico)
- El modelo **no es ejecutable tal como está** por errores de PL/pgSQL y por inconsistencias entre DDL/seed/triggers.
- Hay **rupturas funcionales** que bloquean operación básica:
  - Trigger universal de `updated_at` (DDL) con error de sintaxis PL/pgSQL y uso de `EXECUTE` multi-sentencia.
  - `fn_work_item_history()` usa `OLD.*` en `INSERT` (runtime error).
  - Seeds de agentes y territorio fallan por constraints/tipos (HAIC y UUID vs INTEGER).

## Hallazgos por archivo

### 1) `model/model_goreos/goreos_ddl.sql`
#### Crítico (bloquea ejecución)
- `fn_update_timestamp()` usa `NEW.updated_at = now();` (operador incorrecto en PL/pgSQL; debería ser `:=`).
  - Referencia: `model/model_goreos/goreos_ddl.sql:1470`
- El bloque `DO $$ ... $$;` para crear triggers de `updated_at` hace un solo `EXECUTE format(' ... DROP TRIGGER; CREATE TRIGGER; ... ')`.
  - En PostgreSQL, `EXECUTE` normalmente no admite múltiples sentencias en una sola cadena, por lo que este bloque puede fallar.
  - Referencia: `model/model_goreos/goreos_ddl.sql:1504`

#### Alto (consistencia/semántica)
- `txn.event.actor_id` referencia `ref.actor(id)` pero el contexto de sesión (`app.current_user_id`) modela usuario (`core.user`) en triggers.
  - Esto genera choque directo con `goreos_triggers.sql` (ver auditoría cruzada).
  - Referencia: `model/model_goreos/goreos_ddl.sql:1357`
- `ref.category` soporta jerarquías y reglas (`parent_id`, `phase_id`, `valid_transitions`) pero los seeds no las poblan: capacidades quedan sin uso o incoherentes.
  - Referencia: `model/model_goreos/goreos_ddl.sql:188`

#### Medio (performance/índices)
- Índices `... ON (deleted_at) WHERE deleted_at IS NULL` tienden a ser poco útiles (indexan un valor constante). Se recomienda indexar claves de acceso reales + predicado.
  - Referencias: `model/model_goreos/goreos_ddl.sql:214`, `:265`, `:316`, `:346`, `:371`, `:599`, `:1275`
- Índices redundantes respecto a `UNIQUE` (Postgres crea índice implícito para `UNIQUE`).
  - Ejemplos: `core.user(email)`, `core.person(rut)`
  - Referencias: `model/model_goreos/goreos_ddl.sql:345`, `:370`

#### Diseño (observaciones)
- `core.user.person_id` no es `UNIQUE` → permite múltiples usuarios para una misma persona (decisión de negocio a confirmar).
  - Referencia: `model/model_goreos/goreos_ddl.sql:350`
- `ipr_nature_enum` sólo permite `('PROYECTO','PROGRAMA')`, pero el seed define más naturalezas (ver `goreos_seed.sql`).
  - Referencia: `model/model_goreos/goreos_ddl.sql:51`

---

### 2) `model/model_goreos/goreos_indexes.sql`
#### Alto
- Índices redundantes respecto a `UNIQUE` ya definido en DDL:
  - `ref.actor(code)` (`code` ya es `UNIQUE` en DDL).
  - `core.ipr(codigo_bip)` (`codigo_bip` ya es `UNIQUE` en DDL).
  - `core.budget_commitment(commitment_number)` (`commitment_number` ya es `UNIQUE` en DDL).
  - Referencias: `model/model_goreos/goreos_indexes.sql:48`, `:75`, `:164`

#### Medio
- `idx_workitem_blocked` indexa `updated_at` filtrando `blocked_by_item_id IS NOT NULL`; suele ser mejor indexar el propio `blocked_by_item_id` o un compuesto `(blocked_by_item_id, updated_at)`.
  - Referencia: `model/model_goreos/goreos_indexes.sql:112`

---

### 3) `model/model_goreos/goreos_triggers.sql`
#### Crítico
- `fn_work_item_history()` inserta `OLD.status_id` y `OLD.assignee_id` incluso en `TG_OP='INSERT'` (en INSERT `OLD` no existe).
  - Referencias: `model/model_goreos/goreos_triggers.sql:142`, `:172`

#### Crítico (inconsistencia de IDs)
- `fn_audit_to_event()` toma `app.current_user_id` (usuario) y lo guarda como:
  - `txn.event.actor_id` (pero en DDL `actor_id` referencia `ref.actor`).
  - `txn.event.created_by_id` (en DDL `created_by_id` referencia `core.user`).
  - Resultado: FK inválida/semántica inconsistente.
  - Referencias: `model/model_goreos/goreos_triggers.sql:14`, `:48` y `model/model_goreos/goreos_ddl.sql:1357`

#### Alto
- Triggers de soft delete opcionales definidos como `INSTEAD OF DELETE ON core.ipr/core.agreement`: en PostgreSQL `INSTEAD OF` es para `VIEW`, no para tablas.
  - Referencias: `model/model_goreos/goreos_triggers.sql:340`
- `fn_generate_code()` no es seguro en concurrencia (riesgo de colisión) y el manejo de `p_table_name` no contempla `schema.table` robustamente.
  - Referencia: `model/model_goreos/goreos_triggers.sql:242`

---

### 4) `model/model_goreos/goreos_seed.sql`
#### Alto (inconsistencias con DDL)
- Seed define `ipr_nature` con 5 valores (incluye `PROGRAMA_INVERSION`, `ESTUDIO_BASICO`, `ANF`), pero la columna real `core.ipr.ipr_nature` es ENUM con 2 valores.
  - Referencias: `model/model_goreos/goreos_seed.sql:31` vs `model/model_goreos/goreos_ddl.sql:51` y `:568`
- Seed usa scheme `mechanism_type` (`MEC_*`), mientras el comentario del DDL sugiere `scheme=mechanism` con códigos `SNI|C33|...`.
  - Referencias: `model/model_goreos/goreos_seed.sql:138` vs `model/model_goreos/goreos_ddl.sql:603`

#### Alto (jerarquías incompletas)
- `ipr_state` usa `parent_code='PROYECTO'` pero no existe categoría padre en ese `scheme`, y `parent_id` no se puebla.
  - Referencia: `model/model_goreos/goreos_seed.sql:72`

---

### 5) `model/model_goreos/goreos_seed_agents.sql`
#### Crítico
- Inserta roles `meta.role` con `agent_type='ALGORITHMIC'` sin `human_accountable_id`, pero DDL exige `human_accountable_id IS NOT NULL` para cualquier `agent_type != 'HUMAN'`.
  - Referencias: `model/model_goreos/goreos_seed_agents.sql:110` vs `model/model_goreos/goreos_ddl.sql:70`

---

### 6) `model/model_goreos/goreos_seed_territory.sql`
#### Crítico
- Declara variables `INTEGER` para IDs que en DDL son `UUID` (`ref.category.id`, `core.territory.id`, etc.) → falla por tipos.
  - Referencia: `model/model_goreos/goreos_seed_territory.sql:21`
- No es idempotente (no usa `ON CONFLICT`) → segunda ejecución romperá por `UNIQUE` (`core.territory.code`, `core.organization.code`).

## Auditoría cruzada (consistencia global)
### Identidad actor/usuario en eventos
Conflicto actual:
- DDL: `txn.event.actor_id -> ref.actor(id)` (`model/model_goreos/goreos_ddl.sql:1362`)
- Triggers: `actor_id := current_setting('app.current_user_id')::UUID` (`model/model_goreos/goreos_triggers.sql:27`) → semánticamente apunta a `core.user(id)`.

Opciones recomendadas (decisión de arquitectura):
1) Cambiar `txn.event.actor_id` a FK a `core.user(id)`; y si se necesita `ref.actor`, agregar un `actor_ref_id` opcional.
2) Mantener `actor_id -> ref.actor`, pero cambiar contexto de sesión a `app.current_actor_id` y agregar `created_by_id -> core.user`.
3) Modelar mapeo 1:1 `ref.actor` ↔ `core.user/core.person` y resolver en triggers.

### Taxonomías vs ENUMs
Conflicto actual:
- `core.ipr.ipr_nature` es ENUM restringido (`model/model_goreos/goreos_ddl.sql:51`, `:568`)
- Seed define `ref.category scheme='ipr_nature'` con más valores (`model/model_goreos/goreos_seed.sql:31`)

Recomendación:
- O bien expandir `ipr_nature_enum` para reflejar la taxonomía real, o bien eliminar el ENUM y usar FK a `ref.category(id)` (validado por scheme).

### Jerarquías de categorías (parent_id/phase_id/valid_transitions)
El DDL provee columnas ricas (`model/model_goreos/goreos_ddl.sql:188`) pero el seed:
- usa `parent_code` sin asegurar existencia de padre
- no resuelve `parent_id`, no asigna `phase_id`, no setea `valid_transitions`

Recomendación:
- Poblar jerarquía por `parent_id` (derivando desde `scheme+code`), y definir `valid_transitions` si se va a usar `fn_validate_state_transition()`.

## Recomendaciones priorizadas
1) **Hacer ejecutable el baseline**
   - Corregir PL/pgSQL en `fn_update_timestamp()` y el `DO` de triggers `updated_at`.
   - Corregir `fn_work_item_history()` para no leer `OLD.*` en INSERT.
   - Ajustar seed de agentes para cumplir HAIC (`human_accountable_id`).
   - Ajustar seed territorial para UUID + idempotencia.
2) **Cerrar decisiones de modelado**
   - Unificar `actor` vs `user` en `txn.event`.
   - Unificar `ipr_nature` y `mechanism` (ENUM vs `ref.category`).
3) **Optimizar índices**
   - Eliminar índices redundantes a `UNIQUE`.
   - Revisar índices de `deleted_at` y reemplazarlos por índices de acceso con predicados.

## Checklist de validación (post-fix)
Orden recomendado:
1. `goreos_ddl.sql`
2. `goreos_seed.sql`
3. `goreos_seed_agents.sql`
4. `goreos_seed_territory.sql`
5. `goreos_triggers.sql`
6. `goreos_indexes.sql`

Smoke tests:
- Insertar `core.work_item` y verificar 1 fila en `core.work_item_history`.
- Actualizar cualquier tabla con `updated_at` y verificar que se setea automáticamente.
- Insertar `txn.event` con `occurred_at` fuera de 2026 y verificar que cae en `txn.event_default`.
- Verificar integridad referencial de `created_by_id/updated_by_id/deleted_by_id` a `core.user`.

