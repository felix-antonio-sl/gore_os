# GORE_OS v3.0 - Modelo de Datos

**Estado**: ✅ Ejecutable y Auditado
**Última actualización**: 2026-01-27
**PostgreSQL**: 16+ (requiere PostGIS para funcionalidad territorial futura)

---

## Descripción

Modelo de datos relacional para GORE_OS, el sistema operativo institucional del Gobierno Regional de Ñuble, Chile. Diseñado bajo principios de **Teoría de Categorías** aplicada a dominios de datos, con enfoque **Story-First** (819+ historias de usuario validadas).

### Características Principales

- **50 tablas lógicas** organizadas en 4 schemas semánticos
- **UUID universal** como PK en todas las entidades
- **Auditoría completa** (created/updated/deleted_at/by_id)
- **Category Pattern** (Gist 14.0) para vocabularios controlados (75+ schemes)
- **Event Sourcing** opcional con particionamiento mensual/trimestral
- **Soft Delete** en todas las entidades
- **Validación semántica** enforced a nivel DB
- **Máquinas de estado** con transiciones validadas

---

## Arquitectura

### Schemas

| Schema | Tablas | Propósito                                                         |
| ------ | ------ | ----------------------------------------------------------------- |
| `meta` | 5      | Átomos fundamentales (Role, Process, Entity, Story, Story-Entity) |
| `ref`  | 3      | Vocabularios controlados (Category, Actor, Commitment Types)      |
| `core` | 40     | Entidades de negocio (IPR, Agreements, Budget, Work Items, etc.)  |
| `txn`  | 2      | Event Sourcing (Event, Magnitude) - Particionadas                 |

### Entidades Centrales

**IPR (Intervención Pública Regional)**: Polimorfismo de inversiones

- Tipos: PROYECTO, PROGRAMA, PROGRAMA_INVERSION, ESTUDIO_BASICO, ANF
- Funding: FNDR, FRIL, FRPD, ISAR
- Evaluation: SNI, C33, FRIL, Glosa 06, 8% FNDR, Transferencias

**Work Item**: Átomo de gestión operativa unificado

- Origen: Stories, Commitments, Problems, Alerts
- Estados: 6 estados con transiciones validadas
- Trazabilidad: IPR, Agreement, Resolution, Commitment

**Category Pattern**: 75+ schemes de vocabularios controlados

- Estados operativos (ipr_state: 31, work_item_status: 6, ...)
- Tipos de entidades (agreement_type, mechanism, ...)
- Máquinas de estado con `valid_transitions` JSONB

---

## Instalación

### Prerrequisitos

- PostgreSQL 16+
- Usuario con privilegios `CREATE DATABASE`, `CREATE SCHEMA`
- `psql` client instalado

### Ejecución (Orden Crítico)

```bash
# 0. Crear base de datos
createdb -U postgres goreos

# 1. Estructura base (schemas, tablas, funciones, ENUMs, particiones)
psql -U postgres -d goreos -f goreos_ddl.sql

# 2. Datos semilla - Vocabularios controlados (75+ schemes, 350+ categorías)
psql -U postgres -d goreos -f goreos_seed.sql

# 3. Datos semilla - Agentes KODA con HAIC constraint
psql -U postgres -d goreos -f goreos_seed_agents.sql

# 4. Datos semilla - Territorio Región de Ñuble (3 provincias, 21 comunas)
psql -U postgres -d goreos -f goreos_seed_territory.sql

# 5. Triggers de negocio (core, siempre activo)
psql -U postgres -d goreos -f goreos_triggers.sql

# 6. Triggers de remediación categorial (validación + sincronización) ✨ NUEVO
psql -U postgres -d goreos -f goreos_triggers_remediation.sql

# 7. Índices de optimización (basados en CQs)
psql -U postgres -d goreos -f goreos_indexes.sql
```

### Verificación

```bash
# Contar tablas por schema
psql -U postgres -d goreos -c "
    SELECT schemaname, COUNT(*) AS tables
    FROM pg_tables
    WHERE schemaname IN ('meta', 'ref', 'core', 'txn')
    GROUP BY schemaname
    ORDER BY schemaname;
"
# Esperado: meta=5, ref=3, core=40, txn=2 (sin particiones) o 68 (con particiones)

# Verificar triggers activos
psql -U postgres -d goreos -c "
    SELECT schemaname, tablename, COUNT(*) AS triggers
    FROM pg_trigger t
    JOIN pg_class c ON c.oid = t.tgrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname IN ('meta', 'ref', 'core', 'txn')
      AND NOT t.tgisinternal
    GROUP BY schemaname, tablename
    HAVING COUNT(*) > 0
    ORDER BY schemaname, tablename;
"

# Ejecutar smoke tests (opcional)
psql -U postgres -d goreos -f docs/SMOKE_TESTS.sql
```

---

## Documentación

### Documentos Principales

| Documento                                            | Propósito                                                                |
| ---------------------------------------------------- | ------------------------------------------------------------------------ |
| `docs/GOREOS_ERD_v3.md`                              | Diagramas ER (Mermaid), Data Dictionary, Relaciones                      |
| `docs/AUDITORIA_CONSOLIDADA_v3_2026-01-27.md`        | Auditoría técnica + categorial integrada                                 |
| `docs/DESIGN_DECISIONS.md`                           | Decisiones de diseño explicadas (ENUM vs Category, Event Sourcing, etc.) |
| `docs/GOREOS_CONCEPTUAL_MODEL.md`                    | Modelo conceptual de negocio                                             |
| `docs/AUDITORIA_GORE_OS_v3_2026-01-27.md`            | Auditoría técnica exhaustiva (21 hallazgos)                              |
| `docs/AUDITORIA_CATEGORIAL_GORE_OS_v3_2026-01-27.md` | Auditoría categorial (preservación estructural)                          |

### Diagramas

- **ERD Completo**: 50 tablas, 4 schemas → Ver `docs/GOREOS_ERD_v3.md:20-526`
- **ERD por Dominio**: Meta, IPR, Convenios, Gobernanza, Work Items → Ver `docs/GOREOS_ERD_v3.md:530-983`

---

## Principios de Diseño

### 1. Story-First

```text
Stories (819+) → Entities (139+) → Artifacts (DDL) → Modules (Flask Blueprints)
```

Todo deriva de historias de usuario validadas. No hay código sin story correspondiente.

### 2. Category Pattern (Gist 14.0)

Taxonomías flexibles sin DDL:

- 75+ schemes (mcd_phase, ipr_state, mechanism, ...)
- 350+ categorías
- Jerarquía vía `parent_id`
- Transiciones de estado vía `valid_transitions` JSONB

### 3. Auditoría Universal

Todas las tablas tienen:

```sql
created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
created_by_id UUID REFERENCES core.user(id),
updated_by_id UUID REFERENCES core.user(id),
deleted_at TIMESTAMPTZ,
deleted_by_id UUID REFERENCES core.user(id),
metadata JSONB DEFAULT '{}'::jsonb
```

### 4. Soft Delete por Defecto

Borrado lógico en aplicación (no triggers DB):

```python
entity.deleted_at = datetime.utcnow()
entity.deleted_by_id = g.current_user.id
db.session.commit()
```

Queries siempre filtran: `WHERE deleted_at IS NULL`

### 5. Integridad Semántica Enforced

Validaciones a nivel DB:

- **Scheme validation**: FKs a `ref.category` validan scheme correcto
- **State transitions**: `valid_transitions` enforced por triggers
- **Self-reference prevention**: CHECKs básicos en jerarquías
- **Parent sync**: `parent_code` → `parent_id` automático

---

## Patrones Clave

### Category Pattern

```sql
-- Definir vocabulario
INSERT INTO ref.category (scheme, code, label) VALUES
('mechanism', 'SNI', 'Track A: SNI General'),
('mechanism', 'C33', 'Track B: Circular 33'),
('mechanism', 'FRIL', 'Track C: FRIL');

-- Usar en entidad
CREATE TABLE core.ipr (
    mechanism_id UUID REFERENCES ref.category(id),
    -- Validado por trigger: debe ser scheme='mechanism'
    ...
);
```

### Event Sourcing (Opcional)

```sql
-- Historia específica (siempre activo)
core.work_item → core.work_item_history (trigger automático)

-- Event sourcing genérico (opt-in)
core.ipr → txn.event (trigger comentado, descomentar si se requiere)
```

### Máquinas de Estado

```sql
-- Definir transiciones válidas
UPDATE ref.category SET valid_transitions = '["EN_PROGRESO", "CANCELADO"]'::jsonb
WHERE scheme = 'work_item_status' AND code = 'PENDIENTE';

-- Enforced por trigger
CREATE TRIGGER trg_work_item_state_transition
    BEFORE UPDATE OF status_id ON core.work_item
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();
```

### Funtor Story → WorkItem

Preservación de semántica Story-First:

```sql
meta.story.role_id → core.work_item.required_role_id  -- Capacidad requerida
                   → core.work_item.assignee_id        -- Usuario asignado
```

---

## Integración con Aplicación

### Contexto de Usuario

```python
# Flask: Establecer usuario al inicio del request
from goreos.db import db

@app.before_request
def set_db_user():
    if current_user.is_authenticated:
        db.session.execute(
            "SELECT set_current_user(:user_id)",
            {'user_id': current_user.id}
        )
```

```sql
-- PostgreSQL: Obtener usuario en triggers
v_user_id := get_current_user_safe();  -- Versión defensiva con validación
```

### Queries Comunes

```sql
-- IPRs en fase F4 con problemas abiertos
SELECT i.codigo_bip, i.name, p.code AS phase
FROM core.ipr i
JOIN ref.category p ON p.id = i.mcd_phase_id
WHERE p.code = 'F4'
  AND i.has_open_problems = TRUE
  AND i.deleted_at IS NULL;

-- Work items asignados a usuario X pendientes
SELECT wi.code, wi.title, wi.due_date
FROM core.work_item wi
JOIN ref.category s ON s.id = wi.status_id
WHERE wi.assignee_id = :user_id
  AND s.code = 'PENDIENTE'
  AND wi.deleted_at IS NULL
ORDER BY wi.due_date ASC NULLS LAST;

-- Transiciones válidas desde estado actual
SELECT c_new.code, c_new.label
FROM ref.category c_current
CROSS JOIN LATERAL jsonb_array_elements_text(c_current.valid_transitions) AS valid_code
JOIN ref.category c_new ON c_new.code = valid_code AND c_new.scheme = c_current.scheme
WHERE c_current.id = :current_status_id;
```

---

## Mantenimiento

### Particiones Anuales

```sql
-- Crear particiones para nuevo año (ejecutar Q4 de cada año)
-- txn.event (mensual)
DO $$
DECLARE
    v_year INTEGER := 2027;
    v_month INTEGER;
BEGIN
    FOR v_month IN 1..12 LOOP
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS txn.event_%s_%s PARTITION OF txn.event
            FOR VALUES FROM (%L) TO (%L)',
            v_year, LPAD(v_month::TEXT, 2, '0'),
            v_year || '-' || LPAD(v_month::TEXT, 2, '0') || '-01',
            (v_year + CASE WHEN v_month = 12 THEN 1 ELSE 0 END) || '-' ||
            LPAD((v_month % 12 + 1)::TEXT, 2, '0') || '-01'
        );
    END LOOP;
END $$;

-- txn.magnitude (trimestral) - Similar pero con quarters
```

### Auditoría de Índices

```sql
-- Listar FKs sin índice (potencial problema de performance)
SELECT
    tc.table_schema,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema IN ('meta', 'ref', 'core', 'txn')
  AND NOT EXISTS (
      SELECT 1 FROM pg_indexes
      WHERE schemaname = tc.table_schema
        AND tablename = tc.table_name
        AND indexdef LIKE '%' || kcu.column_name || '%'
  )
ORDER BY tc.table_schema, tc.table_name;
```

---

## Troubleshooting

### Error: "mcd_phase_id debe pertenecer al scheme 'mcd_phase'"

**Causa**: FK a `ref.category` con scheme incorrecto (integridad semántica).
**Solución**: Verificar scheme:

```sql
SELECT scheme, code, label FROM ref.category WHERE id = :category_id;
```

### Error: "Transición de estado inválida: X -> Y"

**Causa**: Transición no definida en `valid_transitions`.
**Solución**: Verificar transiciones válidas:

```sql
SELECT valid_transitions
FROM ref.category
WHERE scheme = :scheme AND code = :current_state;
```

### Warning: "app.current_user_id contiene valor no-UUID"

**Causa**: Contexto de usuario mal configurado.
**Solución**: Verificar `set_current_user()` en aplicación:

```python
# Correcto
db.session.execute("SELECT set_current_user(:user_id)", {'user_id': str(user.id)})

# Incorrecto
db.session.execute("SELECT set_current_user(:user_id)", {'user_id': user.email})
```

---

## Changelog

### v3.0 (2026-01-27)

**Estructura**:

- ✅ 50 tablas con UUID universal
- ✅ 4 schemas semánticos (meta, ref, core, txn)
- ✅ Auditoría completa en todas las entidades
- ✅ 6 ENUMs ontológicos + 75 schemes Category

**Integridad**:

- ✅ Validación de scheme en FKs a `ref.category` (16 triggers)
- ✅ Validación de transiciones de estado (7 triggers)
- ✅ Sincronización `parent_code` → `parent_id` (1 trigger)
- ✅ CHECKs anti-ciclos básicos (3 constraints)

**Semántica**:

- ✅ Funtor Story→WorkItem preservado (`required_role_id`)
- ✅ `valid_transitions` 100% pobladas (7 schemes)
- ✅ Event sourcing híbrido (history tables + txn.event)

**Documentación**:

- ✅ Decisiones de diseño explícitas (`DESIGN_DECISIONS.md`)
- ✅ Auditoría consolidada técnica + categorial
- ✅ Smoke tests definidos

### v2.0 (2026-01-26)

- Baseline inicial con auditoría exhaustiva
- 21 hallazgos corregidos

---

## Soporte

**Documentación**: Ver carpeta `docs/`
**Issues**: Reportar en repositorio del proyecto
**Contacto**: Equipo GORE Ñuble - División de Planificación

---

**Última actualización**: 2026-01-27
**Versión**: 3.0
**Estado**: ✅ Producción Ready
