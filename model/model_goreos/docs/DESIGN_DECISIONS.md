# GORE_OS v3.0 - Decisiones de Diseño

**Fecha**: 2026-01-27
**Estado**: Living Document
**Audiencia**: Arquitectos, Desarrolladores, DBA

---

## 1. Criterio ENUM vs Category Pattern

**Hallazgo**: CAT-004 / M-005
**Tensión Ontológica**: A4_EXPRESAR (Formal ↔ Informal)

### Decisión

El modelo GORE_OS usa **simultáneamente** SQL ENUMs y Category Pattern según la siguiente matriz:

| Criterio | SQL ENUM | Category Pattern |
|----------|----------|------------------|
| **Mutabilidad** | Inmutable (requiere ALTER TYPE) | Mutable (INSERT/UPDATE sin DDL) |
| **Validación** | Compile-time (PostgreSQL) | Runtime (FK constraint) |
| **Performance** | Inline storage, sin JOIN | Requiere JOIN para obtener label |
| **Extensibilidad** | Baja (ALTER TYPE CASCADE) | Alta (gestión desde UI/API) |
| **Transiciones** | No aplicable | `valid_transitions` JSONB |
| **Jerarquía** | No soportada | `parent_id` FK |
| **Versionado** | No aplicable | `deleted_at` soft delete |

### Regla de Aplicación

**Usar SQL ENUM cuando**:
- El tipo proviene directamente de la **ontología** (gnub:*, gist:*, tde:*)
- Los valores son **estables** (cambios < 1 vez al año)
- No requiere jerarquía ni transiciones
- Ejemplos: `agent_type_enum`, `ipr_nature_enum`, `cognition_level_enum`, `process_layer_enum`

**Usar Category Pattern cuando**:
- El vocabulario es **evolutivo** (administrable por usuarios avanzados)
- Requiere **transiciones de estado** (`valid_transitions`)
- Requiere **jerarquía** (`parent_id`)
- Ejemplos: `ipr_state`, `work_item_status`, `mechanism`, `agreement_type`

### Mapeo Actual

#### SQL ENUMs (6)
```sql
-- Tipos ontológicos inmutables
agent_type_enum          → gnub:AgentType (HUMAN, AI, ALGORITHMIC, ...)
ipr_nature_enum          → gnub:IPRNature (PROYECTO, PROGRAMA, ...)
cognition_level_enum     → HAIC C0-C3
delegation_mode_enum     → HAIC M1-M6
process_layer_enum       → STRATEGIC, TACTICAL, OPERATIONAL
story_status_enum        → Story lifecycle
```

#### Category Schemes (75+)
```sql
-- Vocabularios evolutivos con semántica rica
mcd_phase               → 6 fases F0-F5
ipr_state               → 31 estados (28 con transiciones)
mechanism               → 7 tracks de evaluación
work_item_status        → 6 estados con valid_transitions
commitment_state        → 6 estados con valid_transitions
agreement_state         → 10 estados con valid_transitions
payment_status          → 5 estados con valid_transitions
...
```

### Migración ENUM → Category

Si un ENUM debe evolucionar a Category:

1. Crear scheme en `ref.category` con valores equivalentes
2. Agregar columna `*_category_id UUID REFERENCES ref.category(id)`
3. Migrar datos: `UPDATE ... SET *_category_id = (SELECT id FROM ref.category WHERE scheme='...' AND code=old_enum_value::TEXT)`
4. Deprecar columna ENUM (soft: marcar como obsoleta, hard: DROP en v+1)

---

## 2. Estrategia de Event Sourcing

**Hallazgo**: CPL-002 / CAT-006
**Tensión Ontológica**: A2_DEVENIR (Estático ↔ Dinámico)

### Decisión

**Modelo híbrido de auditoría**:

| Enfoque | Tablas | Propósito |
|---------|--------|-----------|
| **History Tables** | `work_item_history`, `commitment_history` | Auditoría granular de entidades críticas, queries directos |
| **Event Sourcing** (opcional) | `txn.event` | Trazabilidad cross-entidad, event replay, integración externa |

### Implementación

#### Core (Siempre Activo)
```sql
-- History tables con triggers activos
trg_work_item_history         → core.work_item_history
trg_commitment_history        → core.operational_commitment
```

#### Opcional (Activar por Ambiente/Tabla)
```sql
-- Event sourcing genérico (ver goreos_triggers.sql:384-402)
trg_ipr_audit                 → txn.event (comentado por defecto)
trg_agreement_audit           → txn.event (comentado por defecto)
trg_budget_commitment_audit   → txn.event (comentado por defecto)
```

### Activación de Event Sourcing

Para activar event sourcing en una tabla:

```sql
-- 1. Descomentar trigger en goreos_triggers.sql
CREATE TRIGGER trg_ipr_audit
    AFTER INSERT OR UPDATE ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_audit_to_event();

-- 2. Reiniciar aplicación para capturar cambios
```

### Criterio de Activación

**Activar event sourcing cuando**:
- Se requiere **time-travel** (reconstruir estado pasado)
- Se requiere **event replay** (reprocesar cambios)
- Se requiere **integración CDC** (Change Data Capture)
- Se requiere **auditoría forense** (compliance)

**No activar si**:
- Solo se requiere "quién/cuándo cambió" (usar `*_by_id`/`*_at`)
- Solo se requiere historial de estados (usar history table dedicada)
- Volumen transaccional > 10K/día (evaluar costo storage)

---

## 3. Política de Soft Delete

**Hallazgo**: CPL-003 / M-002
**Decisión**: CPL-003

### Decisión

**Soft delete a nivel aplicación** (no DB triggers).

### Razones

1. **Control explícito**: La aplicación decide cuándo aplicar soft vs hard delete
2. **Performance**: Evitar overhead de triggers en DELETE
3. **Flexibilidad**: Diferentes políticas por tabla/contexto
4. **Auditabilidad**: `deleted_at`/`deleted_by_id` populados por aplicación

### Implementación

#### Esquema (todas las tablas)
```sql
deleted_at TIMESTAMPTZ,
deleted_by_id UUID REFERENCES core.user(id)
```

#### Aplicación (ejemplo Python/Flask)
```python
def soft_delete(entity):
    """Soft delete: marca como eliminado sin borrar."""
    entity.deleted_at = datetime.utcnow()
    entity.deleted_by_id = g.current_user.id
    db.session.commit()

def hard_delete(entity):
    """Hard delete: borrado físico (usar con precaución)."""
    db.session.delete(entity)
    db.session.commit()
```

#### Queries (filtro estándar)
```sql
-- Siempre filtrar registros activos
SELECT * FROM core.ipr
WHERE deleted_at IS NULL;

-- Usar índices parciales para performance
CREATE INDEX idx_ipr_active ON core.ipr(id) WHERE deleted_at IS NULL;
```

### Activación de Soft Delete Automático

Si se requiere soft delete forzado (nivel DB):

```sql
-- Descomentar en goreos_triggers.sql:405-419
CREATE TRIGGER trg_ipr_soft_delete
    BEFORE DELETE ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_soft_delete();
```

---

## 4. Particionamiento de Tablas Transaccionales

**Hallazgo**: TMP-001 / CAT-009 / L-005

### Decisión

| Tabla | Estrategia | Granularidad | Razón |
|-------|------------|--------------|-------|
| `txn.event` | RANGE(occurred_at) | **Mensual** | Alta frecuencia escritura/query, retención 2 años |
| `txn.magnitude` | RANGE(as_of_date) | **Trimestral** | Baja frecuencia escritura, queries agregados por periodo |

### Asimetría Justificada

- **Eventos**: Volumen alto (10K-100K/mes), queries por fecha exacta → particiones mensuales
- **Magnitudes**: Volumen bajo (1K-10K/mes), queries por periodo fiscal → particiones trimestrales

### Mantenimiento Anual

**Crear particiones futuras**:

```sql
-- Script de mantenimiento (ejecutar Q4 de cada año)
-- Ver archivo: goreos_maintenance_partitions.sql (pendiente crear)

SELECT create_event_partitions(2027);
SELECT create_magnitude_partitions(2027);
```

### PK Compuesto

**Invariante documentado** (REF-003):

```sql
-- txn.event: PK incluye clave de partición
PRIMARY KEY (id, occurred_at)

-- txn.magnitude: PK incluye clave de partición
PRIMARY KEY (id, as_of_date)
```

**Implicación**: `id` es único **por partición**, no globalmente. Para FK desde otras tablas, usar solo `id` (PostgreSQL permite FK a subset de PK compuesto).

---

## 5. Preservación de Funtorialidad Story → WorkItem

**Hallazgo**: CAT-003 / H-002

### Decisión

Agregar `work_item.required_role_id` para preservar semántica Story-First.

### Modelo Categórico

```
meta.story ──role_id──→ meta.role
     │                      │
     F↓                     F↓
core.work_item ──required_role_id──→ meta.role
     │
     └──assignee_id──→ core.user
```

### Semántica

| Campo | Tipo | Semántica | Origen |
|-------|------|-----------|--------|
| `required_role_id` | UUID (meta.role) | **Capacidad requerida** (qué rol necesita el trabajo) | Deriva de `story.role_id` |
| `assignee_id` | UUID (core.user) | **Persona asignada** (quién ejecuta el trabajo) | Decisión operacional |

### Implementación

```sql
-- DDL (goreos_ddl.sql:1299)
required_role_id UUID REFERENCES meta.role(id),

-- Trigger de propagación automática (opcional)
CREATE OR REPLACE FUNCTION fn_propagate_story_role()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.story_id IS NOT NULL AND NEW.required_role_id IS NULL THEN
        SELECT role_id INTO NEW.required_role_id
        FROM meta.story
        WHERE id = NEW.story_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_work_item_propagate_role
    BEFORE INSERT ON core.work_item
    FOR EACH ROW EXECUTE FUNCTION fn_propagate_story_role();
```

### Validación

```sql
-- Query: ¿Hay work items asignados a usuarios sin el rol requerido?
SELECT wi.code, wi.title,
       req_role.name AS required_role,
       assigned_user.email,
       user_role.name AS user_role
FROM core.work_item wi
JOIN meta.role req_role ON req_role.id = wi.required_role_id
JOIN core.user assigned_user ON assigned_user.id = wi.assignee_id
JOIN core.user_role ur ON ur.user_id = assigned_user.id
JOIN meta.role user_role ON user_role.id = ur.role_id
WHERE req_role.code != user_role.code
  AND wi.deleted_at IS NULL;
```

---

## 6. Validación de Integridad Semántica en ref.category

**Hallazgo**: REF-001 / H-001

### Problema

Los FKs a `ref.category(id)` garantizan **integridad referencial** pero no **integridad semántica**:

```sql
-- Esto es válido referencialmente pero semánticamente incorrecto:
INSERT INTO core.ipr (mcd_phase_id, ...)
VALUES (
    (SELECT id FROM ref.category WHERE scheme='work_item_status' AND code='PENDIENTE'), -- ❌ Wrong scheme!
    ...
);
```

### Solución Aplicada

**Triggers de validación por tabla** usando `fn_validate_category_scheme()`:

```sql
-- Ejemplo: core.ipr (ver goreos_triggers_remediation.sql:112-148)
CREATE TRIGGER trg_ipr_validate_schemes
    BEFORE INSERT OR UPDATE ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_validate_ipr_schemes();
```

### Tablas Cubiertas

- `core.ipr`: 5 FKs validados (mcd_phase_id, status_id, mechanism_id, budget_subtitle_id, alert_level_id)
- `core.work_item`: 3 FKs validados (status_id, priority_id, origin_id)
- `core.agreement`: 2 FKs validados (agreement_type_id, state_id)
- `core.operational_commitment`: 1 FK validado (state_id)

### Alternativas No Implementadas

**Opción 2: Vistas tipadas** (mayor complejidad, no implementado)
```sql
CREATE VIEW ref.category_mcd_phase AS
SELECT * FROM ref.category WHERE scheme = 'mcd_phase';

ALTER TABLE core.ipr
ADD CONSTRAINT fk_ipr_phase
FOREIGN KEY (mcd_phase_id) REFERENCES ref.category_mcd_phase(id);
```

**Opción 3: Desnormalización** (solo si scheme se estabiliza completamente)
```sql
CREATE TABLE ref.mcd_phase (
    id UUID PRIMARY KEY,
    code VARCHAR(32) UNIQUE,
    label TEXT,
    ...
);
```

---

## 7. Sincronización de Jerarquías en ref.category

**Hallazgo**: STR-001 / H-005

### Problema

`ref.category` tiene **doble codificación de jerarquía**:
- `parent_id UUID` (FK canónica)
- `parent_code VARCHAR(32)` (helper para seeds)

Sin sincronización, puede haber deriva.

### Solución Aplicada

**Trigger de sincronización** (ver goreos_triggers_remediation.sql:241-266):

```sql
CREATE TRIGGER trg_category_sync_parent
    BEFORE INSERT OR UPDATE OF parent_code ON ref.category
    FOR EACH ROW EXECUTE FUNCTION fn_sync_category_parent();
```

**Comportamiento**:
- Si se setea `parent_code` → resuelve automáticamente `parent_id`
- Si no hay `parent_code` → limpia `parent_id`
- Error si `parent_code` no existe en el mismo scheme

### Deprecación Futura

En v4.0, considerar **eliminar `parent_code`** y usar solo `parent_id` (más limpio).

---

## 8. Prevención de Ciclos en Jerarquías

**Hallazgo**: STR-002 / M-001 / CAT-008

### Problema Detectado

Las jerarquías (`parent_id`) en `ref.category`, `core.organization`, `core.territory`, `core.work_item` **no tienen prevención de ciclos**.

### Solución Parcial Aplicada

**CHECK básico** para prevenir auto-referencia en `work_item`:

```sql
-- goreos_triggers_remediation.sql:286-293
ALTER TABLE core.work_item
ADD CONSTRAINT chk_work_item_no_self_parent
CHECK (parent_id IS NULL OR parent_id != id);

ADD CONSTRAINT chk_work_item_no_self_block
CHECK (blocked_by_item_id IS NULL OR blocked_by_item_id != id);
```

### Solución Completa (Pendiente)

Para prevenir **ciclos transitivos** (A→B→C→A):

**Opción 1: Trigger de validación con CTE**
```sql
CREATE FUNCTION fn_validate_hierarchy_acyclic(table_name TEXT, row_id UUID, parent_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_has_cycle BOOLEAN;
BEGIN
    EXECUTE format('
        WITH RECURSIVE hierarchy AS (
            SELECT id, parent_id, 1 AS level
            FROM %I
            WHERE id = $1
            UNION ALL
            SELECT t.id, t.parent_id, h.level + 1
            FROM %I t
            JOIN hierarchy h ON h.parent_id = t.id
            WHERE h.level < 100
        )
        SELECT EXISTS (SELECT 1 FROM hierarchy WHERE id = $2)
    ', table_name, table_name)
    INTO v_has_cycle
    USING parent_id, row_id;

    RETURN NOT v_has_cycle;
END;
$$ LANGUAGE plpgsql;
```

**Opción 2: Closure Table Pattern**
```sql
CREATE TABLE ref.category_closure (
    ancestor_id UUID REFERENCES ref.category(id),
    descendant_id UUID REFERENCES ref.category(id),
    depth INTEGER,
    PRIMARY KEY (ancestor_id, descendant_id)
);
```

**Opción 3: ltree Extension** (PostgreSQL)
```sql
ALTER TABLE ref.category ADD COLUMN path ltree;
CREATE INDEX idx_category_path_gist ON ref.category USING GIST(path);
```

**Decisión**: Implementar en v3.1 según evaluación de performance.

---

## Referencias

- Auditoría Categorial Consolidada (2026-01-27)
- GORE_OS ERD v3.0 (`docs/GOREOS_ERD_v3.md`)
- Auditoría Exhaustiva v3.0 (`docs/AUDITORIA_GORE_OS_v3_2026-01-27.md`)

---

**Última actualización**: 2026-01-27
**Próxima revisión**: v3.1 (Q2 2026)
