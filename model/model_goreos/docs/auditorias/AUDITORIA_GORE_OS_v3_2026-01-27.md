# REPORTE DE AUDITORÍA EXHAUSTIVA

## Modelo de Datos GORE_OS v3.0

**Fecha**: 2026-01-27
**Auditor**: Experto en diseño de modelos y bases de datos
**Directorio auditado**: `/Users/felixsanhueza/Developer/goreos/model/model_goreos/`

---

## RESUMEN EJECUTIVO

### ALERTA CRÍTICA

> **El modelo NO ES EJECUTABLE tal como está** por errores de PL/pgSQL y por inconsistencias entre DDL/seed/triggers. Existen rupturas funcionales que bloquean la operación básica.

### Estadísticas de Hallazgos

| Severidad                         | Cantidad | Estado                           |
| --------------------------------- | -------- | -------------------------------- |
| **CRÍTICO** (bloquea ejecución)   | 8        | Requiere corrección inmediata    |
| **ALTO** (consistencia/semántica) | 7        | Requiere decisión arquitectónica |
| **MEDIO** (optimización)          | 6        | Puede diferirse                  |
| **Total**                         | **21**   |                                  |

---

## PARTE I: HALLAZGOS CRÍTICOS (Bloquean Ejecución)

### CRIT-001: Error PL/pgSQL en fn_update_timestamp()

| Atributo       | Valor                                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------- |
| **Ubicación**  | `goreos_ddl.sql:1473`                                                                          |
| **Error**      | Usa `NEW.updated_at = now();`                                                                  |
| **Corrección** | Cambiar a `NEW.updated_at := now();`                                                           |
| **Impacto**    | En versiones estrictas de PostgreSQL, el operador `=` no es válido para asignación en PL/pgSQL |
| **Estado**     | **CONFIRMADO** (parcial - depende de versión PostgreSQL)                                       |

```sql
-- ACTUAL (línea 1473)
NEW.updated_at = now();

-- CORRECTO
NEW.updated_at := now();
```

---

### CRIT-002: Bloque DO con EXECUTE multi-sentencia

| Atributo       | Valor                                                        |
| -------------- | ------------------------------------------------------------ |
| **Ubicación**  | `goreos_ddl.sql:1515-1520`                                   |
| **Error**      | EXECUTE con DROP TRIGGER + CREATE TRIGGER en una sola cadena |
| **Corrección** | Separar en dos EXECUTE o usar DO bloques anidados            |
| **Impacto**    | Puede fallar en algunas versiones de PostgreSQL              |
| **Estado**     | **CONFIRMADO** (parcial - funciona en versiones modernas)    |

```sql
-- ACTUAL (líneas 1515-1520)
EXECUTE format('
    DROP TRIGGER IF EXISTS trg_%s_updated_at ON %I.%I;
    CREATE TRIGGER trg_%s_updated_at
    BEFORE UPDATE ON %I.%I
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();
', tbl_name, tbl_schema, tbl_name, tbl_name, tbl_schema, tbl_name);

-- CORRECTO: Separar en dos EXECUTE
EXECUTE format('DROP TRIGGER IF EXISTS trg_%s_updated_at ON %I.%I',
    tbl_name, tbl_schema, tbl_name);
EXECUTE format('CREATE TRIGGER trg_%s_updated_at
    BEFORE UPDATE ON %I.%I
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp()',
    tbl_name, tbl_schema, tbl_name);
```

---

### CRIT-003: fn_work_item_history() usa OLD.* en INSERT

| Atributo       | Valor                                                                  |
| -------------- | ---------------------------------------------------------------------- |
| **Ubicación**  | `goreos_triggers.sql:183-186`                                          |
| **Error**      | Accede a `OLD.status_id` y `OLD.assignee_id` cuando `TG_OP = 'INSERT'` |
| **Corrección** | Usar condicional para evitar acceso a OLD en INSERT                    |
| **Impacto**    | **Runtime error**: OLD no existe en operaciones INSERT                 |
| **Estado**     | **CONFIRMADO**                                                         |

```sql
-- ACTUAL (líneas 183-186)
INSERT INTO core.work_item_history (...) VALUES (
    NEW.id,
    v_event_type_id,
    OLD.status_id,      -- ERROR: OLD no existe en INSERT
    NEW.status_id,
    OLD.assignee_id,    -- ERROR: OLD no existe en INSERT
    NEW.assignee_id,
    ...
);

-- CORRECTO: Usar NULL para INSERT
INSERT INTO core.work_item_history (...) VALUES (
    NEW.id,
    v_event_type_id,
    CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE OLD.status_id END,
    NEW.status_id,
    CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE OLD.assignee_id END,
    NEW.assignee_id,
    ...
);
```

---

### CRIT-004: INSTEAD OF DELETE en tablas (comentado)

| Atributo       | Valor                                                    |
| -------------- | -------------------------------------------------------- |
| **Ubicación**  | `goreos_triggers.sql:340-350`                            |
| **Error**      | `INSTEAD OF DELETE ON core.ipr` - solo válido para VIEWs |
| **Corrección** | Usar `BEFORE DELETE` o crear VIEW intermedia             |
| **Impacto**    | Error de sintaxis si se descomenta                       |
| **Estado**     | **CONFIRMADO** (actualmente comentado, no bloquea)       |

```sql
-- ACTUAL (comentado, líneas 340-350)
/*
CREATE TRIGGER trg_ipr_soft_delete
    INSTEAD OF DELETE ON core.ipr  -- ERROR: solo para VIEWs
    FOR EACH ROW EXECUTE FUNCTION fn_soft_delete();
*/

-- CORRECTO: Usar BEFORE DELETE
CREATE TRIGGER trg_ipr_soft_delete
    BEFORE DELETE ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_soft_delete();
```

---

### CRIT-005: Inconsistencia semántica actor_id vs user_id

| Atributo       | Valor                                                                                |
| -------------- | ------------------------------------------------------------------------------------ |
| **Ubicación**  | DDL:1362 vs Triggers:27,48                                                           |
| **Error**      | `txn.event.actor_id` referencia `ref.actor(id)` pero triggers guardan `core.user.id` |
| **Corrección** | Decisión arquitectónica requerida (ver opciones)                                     |
| **Impacto**    | **FK inválida** - se guarda UUID de user en columna que espera actor                 |
| **Estado**     | **CONFIRMADO**                                                                       |

**Conflicto**:

```sql
-- DDL (línea 1362)
actor_id UUID REFERENCES ref.actor(id),

-- Triggers (línea 27)
v_actor_id := current_setting('app.current_user_id', true)::UUID;

-- Triggers (línea 48) - Guarda user_id en actor_id
INSERT INTO txn.event (..., actor_id, ...) VALUES (..., v_actor_id, ...);
```

**Opciones de corrección**:

1. Cambiar FK a `REFERENCES core.user(id)` y agregar `actor_ref_id` opcional
2. Mantener FK a `ref.actor` y cambiar sesión a `app.current_actor_id`
3. Crear mapeo 1:1 `ref.actor` ↔ `core.user` y resolver en triggers

---

### CRIT-006: Seeds territorio con INTEGER en lugar de UUID

| Atributo       | Valor                                                  |
| -------------- | ------------------------------------------------------ |
| **Ubicación**  | `goreos_seed_territory.sql:22-28`                      |
| **Error**      | Declara `v_region_type_id INTEGER` cuando PKs son UUID |
| **Corrección** | Cambiar a `UUID`                                       |
| **Impacto**    | **Falla por incompatibilidad de tipos**                |
| **Estado**     | **CONFIRMADO**                                         |

```sql
-- ACTUAL (líneas 22-28)
DECLARE
    v_region_type_id INTEGER;      -- ERROR: debe ser UUID
    v_provincia_type_id INTEGER;   -- ERROR
    v_comuna_type_id INTEGER;      -- ERROR
    v_region_id INTEGER;           -- ERROR
    ...

-- CORRECTO
DECLARE
    v_region_type_id UUID;
    v_provincia_type_id UUID;
    v_comuna_type_id UUID;
    v_region_id UUID;
    ...
```

---

### CRIT-007: Seeds agentes violan constraint HAIC

| Atributo       | Valor                                               |
| -------------- | --------------------------------------------------- |
| **Ubicación**  | `goreos_seed_agents.sql:110-158` vs DDL:87          |
| **Error**      | Roles ALGORITHMIC sin `human_accountable_id`        |
| **Corrección** | Agregar `human_accountable_id` a roles algorítmicos |
| **Impacto**    | **Viola CHECK constraint**                          |
| **Estado**     | **CONFIRMADO**                                      |

```sql
-- DDL (línea 87)
CONSTRAINT chk_human_accountable CHECK (
    agent_type = 'HUMAN' OR human_accountable_id IS NOT NULL
)

-- ACTUAL (seed líneas 110-120) - Sin human_accountable_id
INSERT INTO meta.role (code, name, agent_type, ...) VALUES
('ROLE_ORQUESTADOR', 'Rol Orquestador', 'ALGORITHMIC', ...);
-- ERROR: agent_type='ALGORITHMIC' requiere human_accountable_id NOT NULL

-- CORRECTO: Agregar human_accountable_id
INSERT INTO meta.role (code, name, agent_type, human_accountable_id, ...) VALUES
('ROLE_ORQUESTADOR', 'Rol Orquestador', 'ALGORITHMIC',
 (SELECT id FROM meta.role WHERE code = 'ADMIN_SISTEMA'), ...);
```

---

### CRIT-008: ENUM ipr_nature con 2 valores pero seed define 5

| Atributo       | Valor                                                           |
| -------------- | --------------------------------------------------------------- |
| **Ubicación**  | DDL:51 vs Seed:31-36                                            |
| **Error**      | `ipr_nature_enum` tiene 2 valores pero seed inserta 5 en scheme |
| **Corrección** | Expandir ENUM o eliminar valores extras del seed                |
| **Impacto**    | **Inconsistencia entre ENUM y taxonomía**                       |
| **Estado**     | **CONFIRMADO**                                                  |

```sql
-- DDL (línea 51)
CREATE TYPE ipr_nature_enum AS ENUM ('PROYECTO', 'PROGRAMA');

-- Seed (líneas 31-36) - Define 5 valores en scheme
INSERT INTO ref.category (scheme, code, ...) VALUES
('ipr_nature', 'PROYECTO', ...),
('ipr_nature', 'PROGRAMA', ...),
('ipr_nature', 'PROGRAMA_INVERSION', ...),  -- NO EN ENUM
('ipr_nature', 'ESTUDIO_BASICO', ...),      -- NO EN ENUM
('ipr_nature', 'ANF', ...);                  -- NO EN ENUM
```

**Opciones**:

1. Expandir ENUM: `CREATE TYPE ipr_nature_enum AS ENUM ('PROYECTO', 'PROGRAMA', 'PROGRAMA_INVERSION', 'ESTUDIO_BASICO', 'ANF');`
2. Eliminar ENUM y usar FK a `ref.category(id)` con scheme='ipr_nature'

---

## PARTE II: HALLAZGOS ALTOS (Consistencia/Semántica)

### HIGH-001: Nomenclatura inconsistente scheme mechanism

| Atributo      | Valor                                                                  |
| ------------- | ---------------------------------------------------------------------- |
| **Ubicación** | Seed:137-148 vs DDL:574                                                |
| **Problema**  | Seed usa `mechanism_type` con códigos `MEC_*`, DDL sugiere `mechanism` |
| **Impacto**   | Confusión en nomenclatura, funciona correctamente                      |
| **Estado**    | **PARCIALMENTE CONFIRMADO**                                            |

---

### HIGH-002: ipr_state con parent_code sin padre existente

| Atributo      | Valor                                                                   |
| ------------- | ----------------------------------------------------------------------- |
| **Ubicación** | Seed:72                                                                 |
| **Problema**  | `parent_code='PROYECTO'` referencia scheme `ipr_nature`, no `ipr_state` |
| **Impacto**   | Jerarquía de categorías inconsistente                                   |
| **Estado**    | **CONFIRMADO**                                                          |

---

### HIGH-003: Capacidades de ref.category sin uso

| Atributo      | Valor                                                                   |
| ------------- | ----------------------------------------------------------------------- |
| **Ubicación** | DDL:188-200                                                             |
| **Problema**  | `parent_id`, `phase_id`, `valid_transitions` definidos pero no poblados |
| **Impacto**   | Funcionalidades de state machine inutilizadas                           |
| **Estado**    | **CONFIRMADO**                                                          |

---

### HIGH-004: Índices redundantes con UNIQUE constraints

| Atributo                | Valor                                                                                               |
| ----------------------- | --------------------------------------------------------------------------------------------------- |
| **Ubicación**           | indexes:48,75,164; DDL:345,370                                                                      |
| **Índices redundantes** | `idx_actor_code`, `idx_ipr_bip`, `idx_budget_commitment_number`, `idx_person_rut`, `idx_user_email` |
| **Impacto**             | Espacio de almacenamiento y overhead de mantenimiento                                               |
| **Estado**              | **CONFIRMADO**                                                                                      |

---

### HIGH-005: idx_workitem_blocked mal diseñado

| Atributo       | Valor                                                                 |
| -------------- | --------------------------------------------------------------------- |
| **Ubicación**  | indexes:113-114                                                       |
| **Problema**   | Indexa `updated_at` con filtro `WHERE blocked_by_item_id IS NOT NULL` |
| **Corrección** | Indexar `blocked_by_item_id` o compuesto                              |
| **Estado**     | **CONFIRMADO**                                                        |

```sql
-- ACTUAL
CREATE INDEX idx_workitem_blocked ON core.work_item(updated_at)
    WHERE blocked_by_item_id IS NOT NULL;

-- CORRECTO
CREATE INDEX idx_workitem_blocked ON core.work_item(blocked_by_item_id)
    WHERE blocked_by_item_id IS NOT NULL;
```

---

### HIGH-006: core.user.person_id no es UNIQUE

| Atributo      | Valor                                             |
| ------------- | ------------------------------------------------- |
| **Ubicación** | DDL:352                                           |
| **Problema**  | Permite múltiples usuarios para una misma persona |
| **Impacto**   | Decisión de negocio - confirmar si es intencional |
| **Estado**    | **CONFIRMADO** - Requiere decisión                |

---

### HIGH-007: fn_generate_code() no es thread-safe

| Atributo      | Valor                               |
| ------------- | ----------------------------------- |
| **Ubicación** | triggers:267-288                    |
| **Problema**  | `SELECT MAX(...) + 1` no es atómico |
| **Impacto**   | Riesgo de colisión en concurrencia  |
| **Estado**    | **CONFIRMADO**                      |

```sql
-- ACTUAL (no seguro)
SELECT COALESCE(MAX(CAST(SUBSTRING(code FROM '[0-9]+$') AS INTEGER)), 0) + 1
FROM table WHERE code LIKE prefix;

-- CORRECTO: Usar secuencia o FOR UPDATE
SELECT ... FOR UPDATE;
-- O crear secuencia dedicada
```

---

## PARTE III: HALLAZGOS MEDIOS (Optimización)

### MED-001: Índices deleted_at poco útiles

| Atributo       | Valor                                                                   |
| -------------- | ----------------------------------------------------------------------- |
| **Ubicación**  | DDL:214,265,316,346,371,599,1275                                        |
| **Problema**   | `INDEX ON (deleted_at) WHERE deleted_at IS NULL` indexa valor constante |
| **Corrección** | Indexar claves de acceso reales con predicado                           |
| **Estado**     | **CONFIRMADO**                                                          |

---

### MED-002: Índices redundantes respecto a UNIQUE implícito

| Atributo      | Valor                                         |
| ------------- | --------------------------------------------- |
| **Ubicación** | DDL:345,370                                   |
| **Índices**   | `idx_person_rut`, `idx_user_email`            |
| **Problema**  | PostgreSQL crea índice automático para UNIQUE |
| **Estado**    | **CONFIRMADO**                                |

---

### MED-003: current_amount sin trigger de mantenimiento

| Atributo       | Valor                                          |
| -------------- | ---------------------------------------------- |
| **Ubicación**  | DDL:493 (`core.budget_program.current_amount`) |
| **Problema**   | Campo calculado sin mecanismo de actualización |
| **Corrección** | Crear trigger o calcular en consulta           |
| **Estado**     | **CONFIRMADO**                                 |

---

### MED-004: meta.story_entity sin campos de auditoría completos

| Atributo       | Valor                                                   |
| -------------- | ------------------------------------------------------- |
| **Ubicación**  | DDL:165-178                                             |
| **Problema**   | Falta `created_by_id`, `updated_by_id`, `deleted_by_id` |
| **Corrección** | Agregar campos y FKs a core.user                        |
| **Estado**     | **CONFIRMADO**                                          |

---

### MED-005: Precisión NUMERIC inconsistente

| Atributo        | Valor                                                       |
| --------------- | ----------------------------------------------------------- |
| **Ubicación**   | Múltiples líneas DDL                                        |
| **Variaciones** | NUMERIC(18,2), (15,2), (12,2), (18,4), (5,2), (6,2)         |
| **Problema**    | Inconsistencia especialmente en porcentajes: (5,2) vs (6,2) |
| **Estado**      | **CONFIRMADO**                                              |

| Precisión     | Uso               | Tablas                                          |
| ------------- | ----------------- | ----------------------------------------------- |
| NUMERIC(18,2) | Montos monetarios | budget_program, budget_commitment, agreement    |
| NUMERIC(15,2) | Montos medianos   | agreement_installment                           |
| NUMERIC(12,2) | Superficies       | territory.area_km2                              |
| NUMERIC(18,4) | Indicadores       | territorial_indicator.numeric_value             |
| NUMERIC(5,2)  | Porcentajes       | cofinanciamiento_anf, gasto_admin_max, progress |
| NUMERIC(6,2)  | Porcentajes       | puntaje_evaluacion (inconsistente)              |

---

### MED-006: Campos candidatos a ENUM

| Atributo      | Valor                                                                                               |
| ------------- | --------------------------------------------------------------------------------------------------- |
| **Ubicación** | DDL meta.*                                                                                          |
| **Campos**    | `meta.process.layer`, `meta.role.cognition_level`, `meta.role.delegation_mode`, `meta.story.status` |
| **Problema**  | Valores fijos que podrían beneficiarse de ENUM                                                      |
| **Estado**    | **CONFIRMADO** - Evaluar conveniencia                                                               |

---

## PARTE IV: RECOMENDACIONES PRIORIZADAS

### Prioridad 1: Hacer Ejecutable el Baseline (BLOQUEANTE)

1. **CRIT-001**: Corregir `=` → `:=` en `fn_update_timestamp()`
2. **CRIT-002**: Separar sentencias en bloque DO
3. **CRIT-003**: Corregir `fn_work_item_history()` para no usar OLD en INSERT
4. **CRIT-006**: Cambiar INTEGER → UUID en seed territorial
5. **CRIT-007**: Agregar `human_accountable_id` a roles algorítmicos

### Prioridad 2: Decisiones Arquitectónicas (ALTA)

1. **CRIT-005**: Resolver conflicto `actor_id` vs `user_id` en `txn.event`
2. **CRIT-008**: Decidir ENUM expandido vs FK a category para `ipr_nature`
3. **HIGH-006**: Confirmar si múltiples usuarios por persona es intencional

### Prioridad 3: Optimización (MEDIA)

1. **HIGH-004/MED-001/MED-002**: Eliminar índices redundantes
2. **HIGH-005**: Corregir `idx_workitem_blocked`
3. **HIGH-007**: Hacer `fn_generate_code()` thread-safe
4. **HIGH-003**: Poblar `valid_transitions` si se usará state machine

### Prioridad 4: Completitud (BAJA)

1. **MED-003**: Crear trigger para `current_amount`
2. **MED-004**: Completar auditoría en `meta.story_entity`
3. **MED-005**: Estandarizar precisión NUMERIC para porcentajes

---

## PARTE V: ORDEN DE EJECUCIÓN POST-FIX

```
1. goreos_ddl.sql          # Estructuras base (corregir fn_update_timestamp)
2. goreos_seed.sql         # Vocabularios controlados
3. goreos_seed_agents.sql  # Agentes (corregir human_accountable_id)
4. goreos_seed_territory.sql # Territorio (corregir tipos UUID)
5. goreos_triggers.sql     # Lógica de negocio (corregir fn_work_item_history)
6. goreos_indexes.sql      # Optimización (eliminar redundantes)
```

---

## PARTE VI: SMOKE TESTS POST-FIX

| Test   | Descripción                        | Verificación                                                  |
| ------ | ---------------------------------- | ------------------------------------------------------------- |
| ST-001 | Insertar `core.work_item`          | Verificar 1 fila en `core.work_item_history`                  |
| ST-002 | Actualizar cualquier tabla         | Verificar `updated_at` se actualiza                           |
| ST-003 | Insertar `txn.event` fuera de 2026 | Verificar cae en partición default                            |
| ST-004 | Verificar FKs de auditoría         | `created_by_id`/`updated_by_id`/`deleted_by_id` → `core.user` |
| ST-005 | Insertar rol ALGORITHMIC           | Verificar requiere `human_accountable_id`                     |
| ST-006 | Insertar territorio                | Verificar tipos UUID funcionan                                |

---

## PARTE VII: CRITERIOS DE ÉXITO

| Criterio                     | Actual | Objetivo |
| ---------------------------- | ------ | -------- |
| Hallazgos CRÍTICOS           | 8      | 0        |
| Hallazgos ALTOS sin decisión | 7      | 0        |
| Hallazgos MEDIOS aceptados   | 6      | < 10     |
| Smoke tests pasando          | 0%     | 100%     |
| Modelo ejecutable            | NO     | SÍ       |

---

## ANEXO: RESUMEN DE ARCHIVOS AUDITADOS

| Archivo                     | Tamaño               | Hallazgos                                                                                                |
| --------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------- |
| `goreos_ddl.sql`            | 66.4 KB, 1537 líneas | CRIT-001, CRIT-002, CRIT-005 (parcial), CRIT-008 (parcial), HIGH-003, MED-001, MED-002, MED-004, MED-005 |
| `goreos_indexes.sql`        | 14.0 KB, 286 líneas  | HIGH-004, HIGH-005                                                                                       |
| `goreos_triggers.sql`       | 13.1 KB, 388 líneas  | CRIT-003, CRIT-004, CRIT-005 (parcial), HIGH-007                                                         |
| `goreos_seed.sql`           | 42.6 KB              | CRIT-008 (parcial), HIGH-001, HIGH-002, HIGH-003                                                         |
| `goreos_seed_agents.sql`    | 6.7 KB               | CRIT-007                                                                                                 |
| `goreos_seed_territory.sql` | 13.0 KB              | CRIT-006                                                                                                 |

---

**Fin del Reporte de Auditoría**
