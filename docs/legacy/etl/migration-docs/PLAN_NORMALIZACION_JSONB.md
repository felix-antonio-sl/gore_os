# Plan de Normalización de Campos JSONB - GORE_OS

**Fecha**: 2026-01-30
**Versión**: 1.0
**Estado**: Propuesta inicial

---

## Resumen Ejecutivo

Este documento presenta un plan completo de normalización para todos los campos JSONB (`metadata` y `data`) en el sistema GORE_OS. El objetivo es extraer datos estructurados que actualmente están almacenados en formato JSON y moverlos a columnas y tablas relacionales normalizadas.

### Contexto
- **Normalización completada**: `core.ipr` Programas 8% (4 campos normalizados)
- **Tablas prioritarias**: 6 tablas con 16,222 registros totales
- **Campos JSONB identificados**: 50+ keys únicas distribuidas en las tablas

### Beneficios de la normalización
1. Integridad referencial vía FKs
2. Consultas SQL más eficientes
3. Validación de datos en tiempo de inserción
4. Reducción de redundancia y errores
5. Mejor soporte para reportes y análisis

---

## Priorización de Tablas

| Tabla | Registros | Criticidad | Prioridad | Keys JSONB |
|-------|-----------|------------|-----------|------------|
| `core.budget_commitment` | 4,609 | Alta | 1 | 5 |
| `txn.event` | 4,040 | Alta | 2 | 25+ |
| `core.ipr` | 3,621 | Alta | 3 | 15 |
| `core.organization` | 3,308 | Media | 4 | 13 |
| `core.agreement` | 533 | Media | 5 | 13 |
| `core.person` | 111 | Baja | 6 | 5 |

---

## FASE 1: core.budget_commitment (PRIORIDAD 1)

### Estado Actual
**Registros**: 4,609
**Keys en metadata**: 5

```sql
SELECT jsonb_object_keys(metadata) as key, COUNT(*)
FROM core.budget_commitment
GROUP BY key ORDER BY count DESC;
```

| Key | Count | Tipo de dato |
|-----|-------|--------------|
| source | 4,609 | Auditoría |
| bip | 3,701 | FK a IPR |
| codigo_original | 908 | Auditoría |
| fiscal_year | 908 | Columna directa |
| fondo | 908 | FK a ref.category |

### Análisis de Normalización

#### 1.1. `fiscal_year` → Nueva columna
**Acción**: Crear columna `fiscal_year INTEGER`

```sql
-- DDL
ALTER TABLE core.budget_commitment
ADD COLUMN fiscal_year INTEGER;

-- Migración
UPDATE core.budget_commitment
SET fiscal_year = (metadata->>'fiscal_year')::INTEGER
WHERE metadata->>'fiscal_year' IS NOT NULL;

-- Índice
CREATE INDEX idx_budget_commitment_fiscal_year
ON core.budget_commitment(fiscal_year);

-- Limpieza
UPDATE core.budget_commitment
SET metadata = metadata - 'fiscal_year';
```

**Justificación**: Campo crítico para consultas de presupuesto por año fiscal. Debe ser columna indexable.

#### 1.2. `fondo` → FK a ref.category
**Acción**: Crear FK `fund_id UUID REFERENCES ref.category(id)`

**Valores actuales**: No hay valores (COUNT = 0)
**Decisión**: Preparar columna para futuro uso

```sql
-- DDL
ALTER TABLE core.budget_commitment
ADD COLUMN fund_id UUID REFERENCES ref.category(id);

-- Índice
CREATE INDEX idx_budget_commitment_fund
ON core.budget_commitment(fund_id);
```

**Nota**: Verificar si este campo debe poblarse desde `txn.event.data->>'fondo'`

#### 1.3. `bip` → Verificar relación con IPR
**Acción**: Analizar si este código BIP debe reforzar FK a `core.ipr`

**Análisis requerido**:
```sql
-- Verificar consistencia
SELECT
    bc.id,
    bc.metadata->>'bip' as bip_metadata,
    i.codigo_bip,
    bc.ipr_id
FROM core.budget_commitment bc
LEFT JOIN core.ipr i ON bc.ipr_id = i.id
WHERE bc.metadata->>'bip' IS NOT NULL
LIMIT 100;
```

**Decisión pendiente**: Determinar si `bip` es redundante (ya tenemos `ipr_id`) o si hay casos donde difieren.

#### 1.4. `source` y `codigo_original` → Mantener en metadata
**Acción**: Ninguna (campos de auditoría)

**Justificación**: Estos campos son para trazabilidad de migración ETL, no son datos de negocio operacionales.

### Resultado esperado FASE 1
- ✅ Nueva columna: `fiscal_year`
- ✅ Nueva columna: `fund_id` (FK a ref.category)
- ✅ Análisis de consistencia `bip` vs `ipr_id`
- ✅ Reducción de keys en metadata de 5 a 3

---

## FASE 2: txn.event (PRIORIDAD 2)

### Estado Actual
**Registros**: 4,040 (tabla particionada)
**Keys en data**: 25+ (campo `data` en vez de `metadata`)

```sql
SELECT jsonb_object_keys(data) as key, COUNT(*)
FROM txn.event
GROUP BY key ORDER BY count DESC LIMIT 20;
```

| Key | Count | Análisis |
|-----|-------|----------|
| legacy_id | 2,373 | Auditoría → Mantener |
| columna_fuente | 2,373 | Auditoría → Mantener |
| tipo_evento_name | 2,373 | ⚠️ Redundante con event_type_id |
| tipo_evento_id | 2,373 | ⚠️ Redundante con event_type_id |
| source | 2,373 | Auditoría → Mantener |
| numero_documento | 1,788 | FK a Document |
| monto_transferido | 1,667 | Nueva tabla: event_magnitude |
| fondo | 1,667 | FK a ref.category |
| tipologia | 1,667 | FK a ref.category |
| estado_ejecucion | 1,667 | FK a ref.category |
| estado_normalizado | 1,667 | FK a ref.category |
| comuna | 1,667 | FK a Territory |
| provincia | 1,667 | FK a Territory |

### Análisis de Normalización

#### 2.1. Redundancias con event_type_id
**Problema**: `tipo_evento_name` y `tipo_evento_id` están almacenados en `data` pero la tabla ya tiene columna `event_type_id`.

```sql
-- Verificar consistencia
SELECT
    event_type_id,
    data->>'tipo_evento_id' as data_type_id,
    data->>'tipo_evento_name' as data_type_name,
    COUNT(*)
FROM txn.event
WHERE data->>'tipo_evento_id' IS NOT NULL
GROUP BY 1,2,3;
```

**Acción**: Limpiar después de validar consistencia
```sql
-- Limpieza post-validación
UPDATE txn.event
SET data = data - 'tipo_evento_id' - 'tipo_evento_name'
WHERE data ? 'tipo_evento_id';
```

#### 2.2. Fondos y Tipologías → ref.category

**Valores de `fondo`**:
```
SEGURIDAD                                        (538)
DEPORTE                                          (313)
ADULTO_MAYOR                                     (219)
SOCIAL                                           (176)
CULTURA                                          (154)
EQUIDAD_GENERO                                   (115)
```

**Valores de `tipologia`**:
```
SEGURIDAD         (538)
DEPORTE           (313)
ADULTO MAYOR      (220)
SOCIAL            (176)
CULTURA           (154)
EQUIDAD DE GÉNERO (115)
```

**Análisis**: Parece que `fondo` y `tipologia` contienen datos similares. Investigar si son el mismo concepto.

**Acción propuesta**:
```sql
-- Crear scheme en ref.category si no existe
INSERT INTO ref.category (scheme, code, label, description)
SELECT
    'event_fund_type' as scheme,
    REPLACE(LOWER(data->>'fondo'), ' ', '_') as code,
    data->>'fondo' as label,
    'Tipo de fondo asociado al evento (migrado desde txn.event.data)' as description
FROM txn.event
WHERE data->>'fondo' IS NOT NULL
GROUP BY data->>'fondo'
ON CONFLICT DO NOTHING;

-- Agregar columnas FK
ALTER TABLE txn.event
ADD COLUMN fund_type_id UUID REFERENCES ref.category(id),
ADD COLUMN event_category_id UUID REFERENCES ref.category(id);

-- Migrar datos
UPDATE txn.event e
SET fund_type_id = c.id
FROM ref.category c
WHERE c.scheme = 'event_fund_type'
  AND c.label = e.data->>'fondo';

-- Índices
CREATE INDEX idx_event_fund_type ON txn.event(fund_type_id);
CREATE INDEX idx_event_category ON txn.event(event_category_id);

-- Limpieza
UPDATE txn.event
SET data = data - 'fondo' - 'tipologia'
WHERE data ? 'fondo';
```

#### 2.3. Estados → ref.category

**Estados de ejecución** (valores actuales):
```
RENDIDA            (1,255)
NAN                (277)
TERMINADA          (59)
NO RENDIDA         (54)
PENDIENTE REVISIÓN (12)
NO TRANSFERIDA     (10)
```

**Estados normalizados** (valores actuales):
```
COMPLETADO (1,314)
PENDIENTE  (331)
EN_PROCESO (12)
CANCELADO  (10)
```

**Acción propuesta**:
```sql
-- Crear scheme execution_state
INSERT INTO ref.category (scheme, code, label)
VALUES
    ('execution_state', 'COMPLETADO', 'Completado'),
    ('execution_state', 'PENDIENTE', 'Pendiente'),
    ('execution_state', 'EN_PROCESO', 'En proceso'),
    ('execution_state', 'CANCELADO', 'Cancelado');

-- Agregar columna FK
ALTER TABLE txn.event
ADD COLUMN execution_state_id UUID REFERENCES ref.category(id);

-- Migrar datos usando estado_normalizado
UPDATE txn.event e
SET execution_state_id = c.id
FROM ref.category c
WHERE c.scheme = 'execution_state'
  AND c.code = e.data->>'estado_normalizado';

-- Índice
CREATE INDEX idx_event_execution_state ON txn.event(execution_state_id);

-- Limpieza
UPDATE txn.event
SET data = data - 'estado_ejecucion' - 'estado_normalizado'
WHERE data ? 'estado_normalizado';
```

#### 2.4. Territorio (provincia/comuna) → Junction table

**Acción**: Crear tabla `txn.event_territory` similar a `core.ipr_territory`

```sql
-- DDL
CREATE TABLE IF NOT EXISTS txn.event_territory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL,
    territory_id UUID NOT NULL REFERENCES core.territory(id),
    territory_type VARCHAR(20) NOT NULL CHECK (territory_type IN ('PROVINCIA', 'COMUNA')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (event_id) REFERENCES txn.event(id) ON DELETE CASCADE,
    UNIQUE (event_id, territory_id, territory_type)
);

CREATE INDEX idx_event_territory_event ON txn.event_territory(event_id);
CREATE INDEX idx_event_territory_territory ON txn.event_territory(territory_id);

-- Migración (requiere mapeo previo de nombres a core.territory.id)
-- Ver script de migración en FASE 2.4
```

**Nota**: Requiere normalización previa de nombres de territorio en `core.territory`.

#### 2.5. Montos → Nueva tabla txn.event_magnitude

**Observación**: Ya existe tabla `txn.magnitude` particionada. Verificar si `data->>'monto_transferido'` debe migrar allí.

```sql
-- Verificar esquema actual
\d txn.magnitude

-- Si es apropiado, migrar:
INSERT INTO txn.magnitude (
    event_id,
    magnitude_type_id,
    amount,
    recorded_at
)
SELECT
    e.id,
    (SELECT id FROM ref.category WHERE scheme = 'magnitude_type' AND code = 'TRANSFERENCIA'),
    (e.data->>'monto_transferido')::NUMERIC,
    e.occurred_at
FROM txn.event e
WHERE e.data->>'monto_transferido' IS NOT NULL
  AND e.data->>'monto_transferido' ~ '^[0-9]+\.?[0-9]*$';

-- Limpieza
UPDATE txn.event
SET data = data - 'monto_transferido'
WHERE data ? 'monto_transferido';
```

#### 2.6. Documentos → FK a core.document

**Acción**: Si `numero_documento` referencia documentos formales, crear FK.

```sql
-- Análisis previo
SELECT
    data->>'numero_documento' as num_doc,
    COUNT(*)
FROM txn.event
WHERE data->>'numero_documento' IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC
LIMIT 20;

-- Si los números coinciden con core.document:
ALTER TABLE txn.event
ADD COLUMN document_id UUID REFERENCES core.document(id);

-- Migración (requiere mapeo)
UPDATE txn.event e
SET document_id = d.id
FROM core.document d
WHERE d.document_number = e.data->>'numero_documento';

-- Índice
CREATE INDEX idx_event_document ON txn.event(document_id);

-- Limpieza
UPDATE txn.event
SET data = data - 'numero_documento'
WHERE document_id IS NOT NULL;
```

#### 2.7. Campos de auditoría → Mantener

Los siguientes campos permanecen en `data`:
- `legacy_id`
- `columna_fuente`
- `source`
- `observaciones`
- Otros campos de trazabilidad

### Resultado esperado FASE 2
- ✅ Eliminación de redundancias con `event_type_id`
- ✅ Nuevas columnas FK: `fund_type_id`, `execution_state_id`, `event_category_id`
- ✅ Nueva tabla: `txn.event_territory`
- ✅ Migración de montos a `txn.magnitude`
- ✅ FK opcional: `document_id`
- ✅ Reducción de keys en data de 25+ a ~10 (solo auditoría)

---

## FASE 3: core.ipr (PRIORIDAD 3)

### Estado Actual
**Registros**: 3,621
**Keys en metadata**: 15

| Key | Count | Estado |
|-----|-------|--------|
| source | 3,621 | Mantener (auditoría) |
| fuente_principal | 1,973 | ⚠️ Analizar |
| legacy_id | 1,973 | Mantener (auditoría) |
| codigo_normalizado | 1,973 | Mantener (auditoría) |
| **provincia** | **1,965** | ✅ **NORMALIZADO** (ipr_territory) |
| origen | 1,965 | Analizar |
| **comuna** | **1,965** | ✅ **NORMALIZADO** (ipr_territory) |
| cod_unico_idis | 1,933 | Nueva columna |
| tipologia_original | 1,924 | Mapear a ipr_type_id |
| etapa_original | 1,758 | Mapear a mcd_phase_id |
| event_id_original | 1,648 | FK a txn.event |
| unidad_tecnica | 670 | FK a core.organization |
| codigo_convenios | 438 | Analizar |

**Nota**: Provincia y comuna ya fueron normalizados a `core.ipr_territory` en migración previa.

### Análisis de Normalización

#### 3.1. `cod_unico_idis` → Nueva columna
**Acción**: Crear columna `codigo_idis VARCHAR(50)`

```sql
-- DDL
ALTER TABLE core.ipr
ADD COLUMN codigo_idis VARCHAR(50);

-- Índice único
CREATE UNIQUE INDEX idx_ipr_codigo_idis
ON core.ipr(codigo_idis)
WHERE codigo_idis IS NOT NULL;

-- Migración
UPDATE core.ipr
SET codigo_idis = metadata->>'cod_unico_idis'
WHERE metadata->>'cod_unico_idis' IS NOT NULL;

-- Limpieza
UPDATE core.ipr
SET metadata = metadata - 'cod_unico_idis';
```

**Justificación**: Código único de IDIS es identificador externo crítico, debe ser columna para validación y búsqueda.

#### 3.2. `tipologia_original` → Enriquecer ipr_type_id

**Valores actuales**:
```
FRIL               (663)
C-33               (413)
MIDESO             (381)
GLOSA 5.1          (141)
TRANSFERENCIAS     (67)
```

**Acción**: Verificar si estos valores están mapeados en `ref.category scheme='ipr_type'`

```sql
-- Análisis de mapeo
SELECT
    i.metadata->>'tipologia_original' as tipologia,
    c.code,
    c.label,
    COUNT(*)
FROM core.ipr i
LEFT JOIN ref.category c ON i.ipr_type_id = c.id
WHERE i.metadata->>'tipologia_original' IS NOT NULL
GROUP BY 1,2,3
ORDER BY 4 DESC;

-- Si hay valores sin mapear, crear en ref.category
INSERT INTO ref.category (scheme, code, label, description)
SELECT
    'ipr_type' as scheme,
    REPLACE(UPPER(metadata->>'tipologia_original'), ' ', '_') as code,
    metadata->>'tipologia_original' as label,
    'Tipo de IPR (tipología original IDIS)' as description
FROM core.ipr
WHERE metadata->>'tipologia_original' IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM ref.category
      WHERE scheme = 'ipr_type'
      AND label = metadata->>'tipologia_original'
  )
GROUP BY metadata->>'tipologia_original';

-- Actualizar ipr_type_id si está NULL
UPDATE core.ipr i
SET ipr_type_id = c.id
FROM ref.category c
WHERE c.scheme = 'ipr_type'
  AND c.label = i.metadata->>'tipologia_original'
  AND i.ipr_type_id IS NULL;

-- Limpieza (solo si todos los valores están mapeados)
UPDATE core.ipr
SET metadata = metadata - 'tipologia_original'
WHERE ipr_type_id IS NOT NULL;
```

#### 3.3. `etapa_original` → Enriquecer mcd_phase_id

**Valores actuales**:
```
EJECUCIÓN       (1,616)
DISEÑO          (141)
PREFACTIBILIDAD (1)
```

**Acción**: Similar a tipologia_original, mapear a `ref.category scheme='mcd_phase'`

```sql
-- Crear categorías si no existen
INSERT INTO ref.category (scheme, code, label, sort_order)
VALUES
    ('mcd_phase', 'EJECUCION', 'Ejecución', 3),
    ('mcd_phase', 'DISENO', 'Diseño', 2),
    ('mcd_phase', 'PREFACTIBILIDAD', 'Prefactibilidad', 1)
ON CONFLICT (scheme, code) DO NOTHING;

-- Actualizar mcd_phase_id
UPDATE core.ipr i
SET mcd_phase_id = c.id
FROM ref.category c
WHERE c.scheme = 'mcd_phase'
  AND UPPER(REPLACE(c.label, 'ó', 'o')) = UPPER(REPLACE(i.metadata->>'etapa_original', 'ó', 'o'))
  AND i.mcd_phase_id IS NULL;

-- Limpieza
UPDATE core.ipr
SET metadata = metadata - 'etapa_original'
WHERE mcd_phase_id IS NOT NULL;
```

#### 3.4. `event_id_original` → FK a txn.event

**Acción**: Crear FK opcional a `txn.event`

```sql
-- DDL
ALTER TABLE core.ipr
ADD COLUMN origin_event_id UUID REFERENCES txn.event(id);

-- Migración (requiere mapeo de legacy_id)
UPDATE core.ipr i
SET origin_event_id = e.id
FROM txn.event e
WHERE e.data->>'legacy_id' = i.metadata->>'event_id_original';

-- Índice
CREATE INDEX idx_ipr_origin_event ON core.ipr(origin_event_id);

-- Limpieza
UPDATE core.ipr
SET metadata = metadata - 'event_id_original'
WHERE origin_event_id IS NOT NULL;
```

#### 3.5. `unidad_tecnica` → FK a core.organization

**Análisis requerido**: Verificar si los nombres en metadata coinciden con `core.organization.name`

```sql
-- Análisis
SELECT
    metadata->>'unidad_tecnica' as unidad,
    COUNT(*)
FROM core.ipr
WHERE metadata->>'unidad_tecnica' IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC;

-- Si hay match, crear columna
ALTER TABLE core.ipr
ADD COLUMN technical_unit_id UUID REFERENCES core.organization(id);

-- Migración (requiere normalización de nombres)
UPDATE core.ipr i
SET technical_unit_id = o.id
FROM core.organization o
WHERE UPPER(TRIM(o.name)) = UPPER(TRIM(i.metadata->>'unidad_tecnica'));

-- Índice
CREATE INDEX idx_ipr_technical_unit ON core.ipr(technical_unit_id);

-- Limpieza
UPDATE core.ipr
SET metadata = metadata - 'unidad_tecnica'
WHERE technical_unit_id IS NOT NULL;
```

#### 3.6. `fuente_principal` → Analizar redundancia

**Valores**: IDIS (1,933), 250 (39), CONVENIOS (1)

**Análisis**: Verificar si esto se superpone con `funding_source_id` (ya normalizado).

```sql
-- Comparar
SELECT
    metadata->>'fuente_principal' as fuente_metadata,
    c.label as funding_source,
    COUNT(*)
FROM core.ipr i
LEFT JOIN ref.category c ON i.funding_source_id = c.id
WHERE metadata->>'fuente_principal' IS NOT NULL
GROUP BY 1,2;
```

**Decisión**: Si son diferentes conceptos (fuente de datos vs fuente de financiamiento), crear columna `data_source VARCHAR(50)`. Si son redundantes, limpiar.

#### 3.7. `origen` y `codigo_convenios` → Analizar

**Pendiente**: Requiere análisis de valores únicos y semántica de negocio.

### Resultado esperado FASE 3
- ✅ Nueva columna: `codigo_idis`
- ✅ Enriquecimiento de `ipr_type_id` y `mcd_phase_id`
- ✅ Nueva columna FK: `origin_event_id`, `technical_unit_id`
- ✅ Análisis de `fuente_principal`, `origen`, `codigo_convenios`
- ✅ Reducción de keys en metadata de 15 a ~6

---

## FASE 4: core.organization (PRIORIDAD 4)

### Estado Actual
**Registros**: 3,308
**Keys en metadata**: 13

| Key | Count | Análisis |
|-----|-------|----------|
| source | 3,283 | Mantener (auditoría) |
| legacy_id | 1,659 | Mantener (auditoría) |
| tipo | 1,624 | ⚠️ Redundante con org_type_id? |
| **tipo_institucion** | **1,612** | **→ org_type_id** |
| nombre_nlp | 1,612 | Mantener (procesamiento NLP) |
| fuente_original | 1,612 | Mantener (auditoría) |
| **rut** | **1,612** | **→ Nueva columna** |
| nombre_original | 1,612 | Mantener (auditoría) |
| merged_at | 32 | Mantener (auditoría merge) |
| original_name | 32 | Mantener (auditoría merge) |
| merged_into | 32 | Mantener (auditoría merge) |
| aliases | 24 | Nueva tabla org_alias |

### Análisis de Normalización

#### 4.1. `rut` → Nueva columna

**Acción**: Crear columna `rut VARCHAR(12)` con índice único

```sql
-- DDL
ALTER TABLE core.organization
ADD COLUMN rut VARCHAR(12);

-- Índice único
CREATE UNIQUE INDEX idx_organization_rut
ON core.organization(rut)
WHERE rut IS NOT NULL;

-- Migración
UPDATE core.organization
SET rut = metadata->>'rut'
WHERE metadata->>'rut' IS NOT NULL;

-- Limpieza
UPDATE core.organization
SET metadata = metadata - 'rut';
```

**Justificación**: RUT es identificador único fiscal en Chile, debe ser columna indexable para búsquedas y validación.

#### 4.2. `tipo_institucion` → Enriquecer org_type_id

**Valores actuales**:
```
OSC              (1,339)
OTROS            (238)
MUNICIPALIDAD    (15)
SERVICIO_PUBLICO (10)
UNIVERSIDAD      (7)
EMPRESA          (2)
GORE             (1)
```

**Acción**: Mapear a `ref.category scheme='org_type'`

```sql
-- Crear categorías si no existen
INSERT INTO ref.category (scheme, code, label, description)
VALUES
    ('org_type', 'OSC', 'Organización de la Sociedad Civil', NULL),
    ('org_type', 'OTROS', 'Otros', NULL),
    ('org_type', 'MUNICIPALIDAD', 'Municipalidad', NULL),
    ('org_type', 'SERVICIO_PUBLICO', 'Servicio Público', NULL),
    ('org_type', 'UNIVERSIDAD', 'Universidad', NULL),
    ('org_type', 'EMPRESA', 'Empresa', NULL),
    ('org_type', 'GORE', 'Gobierno Regional', NULL)
ON CONFLICT (scheme, code) DO NOTHING;

-- Actualizar org_type_id
UPDATE core.organization o
SET org_type_id = c.id
FROM ref.category c
WHERE c.scheme = 'org_type'
  AND c.code = o.metadata->>'tipo_institucion'
  AND o.org_type_id IS NULL;

-- Limpieza
UPDATE core.organization
SET metadata = metadata - 'tipo_institucion' - 'tipo'
WHERE org_type_id IS NOT NULL;
```

#### 4.3. `aliases` → Nueva tabla core.organization_alias

**Acción**: Crear tabla para gestionar nombres alternativos

```sql
-- DDL
CREATE TABLE IF NOT EXISTS core.organization_alias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES core.organization(id) ON DELETE CASCADE,
    alias_name TEXT NOT NULL,
    alias_type VARCHAR(50) DEFAULT 'GENERAL',
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core."user"(id),
    UNIQUE (organization_id, alias_name)
);

CREATE INDEX idx_org_alias_organization ON core.organization_alias(organization_id);
CREATE INDEX idx_org_alias_name ON core.organization_alias(alias_name);

-- Migración
INSERT INTO core.organization_alias (organization_id, alias_name, alias_type)
SELECT
    o.id,
    jsonb_array_elements_text(o.metadata->'aliases') as alias_name,
    'LEGACY_ALIAS'
FROM core.organization o
WHERE o.metadata ? 'aliases'
  AND jsonb_typeof(o.metadata->'aliases') = 'array'
ON CONFLICT (organization_id, alias_name) DO NOTHING;

-- Limpieza
UPDATE core.organization
SET metadata = metadata - 'aliases'
WHERE metadata ? 'aliases';
```

**Justificación**: Los alias son datos estructurados que deben ser consultables (búsqueda de organizaciones por nombres alternativos).

#### 4.4. Campos de auditoría y merge → Mantener

Los siguientes campos permanecen en metadata:
- `source`, `legacy_id`, `fuente_original`
- `nombre_original`, `nombre_nlp` (útiles para NLP/búsqueda)
- `merged_at`, `original_name`, `merged_into` (trazabilidad de merges)

### Resultado esperado FASE 4
- ✅ Nueva columna: `rut` (unique)
- ✅ Enriquecimiento de `org_type_id`
- ✅ Nueva tabla: `core.organization_alias`
- ✅ Reducción de keys en metadata de 13 a ~8

---

## FASE 5: core.agreement (PRIORIDAD 5)

### Estado Actual
**Registros**: 533
**Keys en metadata**: 13

| Key | Count | Análisis |
|-----|-------|----------|
| source | 533 | Mantener (auditoría) |
| origen_hoja | 533 | Mantener (auditoría) |
| territorio_id | 533 | ⚠️ Verificar uso |
| tipo_registro | 533 | Mantener (auditoría) |
| fila_origen | 533 | Mantener (auditoría) |
| legacy_id | 533 | Mantener (auditoría) |
| clasificador_id | 533 | ⚠️ Verificar uso |
| periodo_id | 533 | ⚠️ Verificar uso |
| **estado_convenio_raw** | **532** | **→ state_id** |
| **referente_tecnico** | **389** | **→ FK a core.person** |
| estado_cgr_raw | 129 | → Nueva columna |
| estado_cgr_norm | 129 | → cgr_state_id FK |
| estado_operacional | 17 | Analizar |

### Análisis de Normalización

#### 5.1. `estado_convenio_raw` → Enriquecer state_id

**Valores actuales**:
```
FIRMADO               (457)
SIN CONVENIO          (51)
ENCOMENDADO DIT       (7)
NO SE FIRMO           (6)
ENVIADO AL SERVICIO   (6)
```

**Acción**: Mapear a `ref.category scheme='agreement_state'`

```sql
-- Crear categorías
INSERT INTO ref.category (scheme, code, label, sort_order)
VALUES
    ('agreement_state', 'FIRMADO', 'Firmado', 1),
    ('agreement_state', 'SIN_CONVENIO', 'Sin convenio', 2),
    ('agreement_state', 'ENCOMENDADO_DIT', 'Encomendado DIT', 3),
    ('agreement_state', 'NO_FIRMADO', 'No se firmó', 4),
    ('agreement_state', 'ENVIADO_SERVICIO', 'Enviado al servicio', 5)
ON CONFLICT (scheme, code) DO NOTHING;

-- Actualizar state_id
UPDATE core.agreement a
SET state_id = c.id
FROM ref.category c
WHERE c.scheme = 'agreement_state'
  AND (
      (a.metadata->>'estado_convenio_raw' = 'FIRMADO' AND c.code = 'FIRMADO') OR
      (a.metadata->>'estado_convenio_raw' = 'SIN CONVENIO' AND c.code = 'SIN_CONVENIO') OR
      (a.metadata->>'estado_convenio_raw' = 'ENCOMENDADO DIT' AND c.code = 'ENCOMENDADO_DIT') OR
      (a.metadata->>'estado_convenio_raw' = 'NO SE FIRMO' AND c.code = 'NO_FIRMADO') OR
      (a.metadata->>'estado_convenio_raw' = 'ENVIADO AL SERVICIO' AND c.code = 'ENVIADO_SERVICIO')
  )
  AND a.state_id IS NULL;

-- Limpieza
UPDATE core.agreement
SET metadata = metadata - 'estado_convenio_raw'
WHERE state_id IS NOT NULL;
```

#### 5.2. `referente_tecnico` → FK a core.person

**Acción**: Crear columna FK `technical_referent_id`

```sql
-- DDL
ALTER TABLE core.agreement
ADD COLUMN technical_referent_id UUID REFERENCES core.person(id);

-- Migración (requiere normalización de nombres)
UPDATE core.agreement a
SET technical_referent_id = p.id
FROM core.person p
WHERE UPPER(TRIM(p.names || ' ' || p.paternal_surname || ' ' || COALESCE(p.maternal_surname, '')))
    = UPPER(TRIM(a.metadata->>'referente_tecnico'));

-- Índice
CREATE INDEX idx_agreement_technical_referent
ON core.agreement(technical_referent_id);

-- Limpieza
UPDATE core.agreement
SET metadata = metadata - 'referente_tecnico'
WHERE technical_referent_id IS NOT NULL;
```

**Nota**: Si hay nombres que no coinciden, crear registros en `core.person` o mantener en metadata.

#### 5.3. `estado_cgr_norm` → FK a ref.category

**Acción**: Mapear a `ref.category scheme='cgr_outcome'`

```sql
-- Análisis de valores únicos
SELECT
    metadata->>'estado_cgr_norm' as estado,
    COUNT(*)
FROM core.agreement
WHERE metadata->>'estado_cgr_norm' IS NOT NULL
GROUP BY 1;

-- Crear categorías basado en valores
-- (Pendiente: ver valores reales)

-- Agregar columna
ALTER TABLE core.agreement
ADD COLUMN cgr_state_id UUID REFERENCES ref.category(id);

-- Migración y limpieza similar a 5.1
```

#### 5.4. IDs de lookup → Verificar uso

**Campos**:
- `territorio_id`
- `clasificador_id`
- `periodo_id`

**Acción**: Analizar si estos IDs referencian tablas existentes

```sql
-- Verificar territorio_id
SELECT
    a.metadata->>'territorio_id' as territorio_uuid,
    t.name,
    COUNT(*)
FROM core.agreement a
LEFT JOIN core.territory t ON t.id::text = a.metadata->>'territorio_id'
GROUP BY 1,2
LIMIT 20;

-- Si hay match:
ALTER TABLE core.agreement
ADD COLUMN territory_id UUID REFERENCES core.territory(id);

UPDATE core.agreement
SET territory_id = (metadata->>'territorio_id')::UUID
WHERE metadata->>'territorio_id' IS NOT NULL;

-- Similar para clasificador_id y periodo_id
```

#### 5.5. Campos de auditoría → Mantener

- `source`, `legacy_id`, `origen_hoja`, `fila_origen`, `tipo_registro`

### Resultado esperado FASE 5
- ✅ Enriquecimiento de `state_id`
- ✅ Nueva columna FK: `technical_referent_id`, `cgr_state_id`
- ✅ Posibles columnas FK: `territory_id`, `clasificador_id`, `periodo_id`
- ✅ Reducción de keys en metadata de 13 a ~6

---

## FASE 6: core.person (PRIORIDAD 6)

### Estado Actual
**Registros**: 111
**Keys en metadata**: 5

| Key | Count | Análisis |
|-----|-------|----------|
| calificacion | 110 | Nueva tabla person_qualification |
| **estamento** | **110** | **→ FK a ref.category** |
| legacy_id | 110 | Mantener (auditoría) |
| cargo_ultimo | 110 | Nueva columna |
| source | 110 | Mantener (auditoría) |

### Análisis de Normalización

#### 6.1. `estamento` → FK a ref.category

**Valores actuales**:
```
Profesional           (79)
Honorarios            (10)
Directivo             (7)
Administrativo        (6)
Técnico               (4)
Auxiliar              (3)
Autoridad de Gobierno (1)
```

**Acción**: Crear scheme `employee_category`

```sql
-- Crear categorías
INSERT INTO ref.category (scheme, code, label, sort_order)
VALUES
    ('employee_category', 'PROFESIONAL', 'Profesional', 1),
    ('employee_category', 'DIRECTIVO', 'Directivo', 2),
    ('employee_category', 'TECNICO', 'Técnico', 3),
    ('employee_category', 'ADMINISTRATIVO', 'Administrativo', 4),
    ('employee_category', 'AUXILIAR', 'Auxiliar', 5),
    ('employee_category', 'HONORARIOS', 'Honorarios', 6),
    ('employee_category', 'AUTORIDAD', 'Autoridad de Gobierno', 7)
ON CONFLICT (scheme, code) DO NOTHING;

-- Agregar columna
ALTER TABLE core.person
ADD COLUMN employee_category_id UUID REFERENCES ref.category(id);

-- Migración
UPDATE core.person p
SET employee_category_id = c.id
FROM ref.category c
WHERE c.scheme = 'employee_category'
  AND c.label = p.metadata->>'estamento';

-- Índice
CREATE INDEX idx_person_employee_category
ON core.person(employee_category_id);

-- Limpieza
UPDATE core.person
SET metadata = metadata - 'estamento';
```

#### 6.2. `cargo_ultimo` → Nueva columna

**Acción**: Crear columna `last_position TEXT`

```sql
-- DDL
ALTER TABLE core.person
ADD COLUMN last_position TEXT;

-- Migración
UPDATE core.person
SET last_position = metadata->>'cargo_ultimo'
WHERE metadata->>'cargo_ultimo' IS NOT NULL;

-- Limpieza
UPDATE core.person
SET metadata = metadata - 'cargo_ultimo';
```

#### 6.3. `calificacion` → Nueva tabla core.person_qualification

**Valores actuales**: 57 calificaciones únicas (Ingeniero Comercial, Abogado, etc.)

**Opción A**: Nueva columna `qualification TEXT`
```sql
ALTER TABLE core.person ADD COLUMN qualification TEXT;
```

**Opción B**: Tabla normalizada (recomendado para análisis)
```sql
-- DDL
CREATE TABLE IF NOT EXISTS core.person_qualification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES core.person(id) ON DELETE CASCADE,
    qualification_type_id UUID REFERENCES ref.category(id), -- scheme='qualification_type'
    qualification_name TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT true,
    obtained_date DATE,
    institution TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_person_qual_person ON core.person_qualification(person_id);
CREATE INDEX idx_person_qual_type ON core.person_qualification(qualification_type_id);

-- Migración
INSERT INTO core.person_qualification (person_id, qualification_name, is_primary)
SELECT
    id,
    metadata->>'calificacion',
    true
FROM core.person
WHERE metadata->>'calificacion' IS NOT NULL;

-- Limpieza
UPDATE core.person
SET metadata = metadata - 'calificacion';
```

**Recomendación**: Usar Opción B si se planea gestionar múltiples calificaciones por persona en el futuro.

### Resultado esperado FASE 6
- ✅ Nueva columna FK: `employee_category_id`
- ✅ Nueva columna: `last_position`
- ✅ Nueva tabla: `core.person_qualification` (o columna simple)
- ✅ Reducción de keys en metadata de 5 a 2 (solo auditoría)

---

## Resumen de Cambios Propuestos

### Nuevas Columnas

| Tabla | Columnas Nuevas | Tipo |
|-------|-----------------|------|
| `core.budget_commitment` | `fiscal_year`, `fund_id` | INT, UUID FK |
| `txn.event` | `fund_type_id`, `event_category_id`, `execution_state_id`, `document_id` | UUID FKs |
| `core.ipr` | `codigo_idis`, `origin_event_id`, `technical_unit_id` | VARCHAR, UUID FKs |
| `core.organization` | `rut` | VARCHAR(12) |
| `core.agreement` | `technical_referent_id`, `cgr_state_id`, `territory_id` | UUID FKs |
| `core.person` | `employee_category_id`, `last_position` | UUID FK, TEXT |

### Nuevas Tablas

| Tabla | Propósito | Referencias |
|-------|-----------|-------------|
| `txn.event_territory` | Relación many-to-many: event ↔ territory | `txn.event`, `core.territory` |
| `core.organization_alias` | Nombres alternativos de organizaciones | `core.organization` |
| `core.person_qualification` | Calificaciones profesionales | `core.person` |

### Nuevos Schemes en ref.category

| Scheme | Valores | Usado en |
|--------|---------|----------|
| `event_fund_type` | SEGURIDAD, DEPORTE, ADULTO_MAYOR, etc. | `txn.event.fund_type_id` |
| `execution_state` | COMPLETADO, PENDIENTE, EN_PROCESO, CANCELADO | `txn.event.execution_state_id` |
| `employee_category` | PROFESIONAL, DIRECTIVO, TECNICO, etc. | `core.person.employee_category_id` |
| `agreement_state` | FIRMADO, SIN_CONVENIO, etc. | `core.agreement.state_id` |

### Impacto en Metadata

| Tabla | Keys Antes | Keys Después | Reducción |
|-------|------------|--------------|-----------|
| `core.budget_commitment` | 5 | 3 | -40% |
| `txn.event` | 25+ | ~10 | -60% |
| `core.ipr` | 15 | ~6 | -60% |
| `core.organization` | 13 | ~8 | -38% |
| `core.agreement` | 13 | ~6 | -54% |
| `core.person` | 5 | 2 | -60% |
| **TOTAL** | **76+** | **~35** | **-54%** |

---

## Orden de Ejecución Recomendado

### Semana 1: Preparación
1. Crear nuevos schemes en `ref.category`
2. Validar datos y resolver inconsistencias
3. Crear scripts de migración con rollback

### Semana 2: FASE 1 + FASE 6 (bajo riesgo)
4. `core.budget_commitment` (fiscal_year, fund_id)
5. `core.person` (employee_category_id, last_position, qualifications)

### Semana 3: FASE 4 (medio riesgo)
6. `core.organization` (rut, org_type_id, aliases)

### Semana 4: FASE 5 (medio riesgo)
7. `core.agreement` (state_id, technical_referent_id, cgr_state_id)

### Semana 5: FASE 3 (alto impacto)
8. `core.ipr` (codigo_idis, ipr_type_id, mcd_phase_id, etc.)

### Semana 6: FASE 2 (alto riesgo - particionada)
9. `txn.event` (fund_type_id, execution_state_id, event_territory)
10. Migración de montos a `txn.magnitude`

### Semana 7: Validación y limpieza
11. Verificar integridad referencial
12. Ejecutar limpieza final de metadata
13. Actualizar documentación y ERD

---

## Validaciones Post-Normalización

### Integridad Referencial
```sql
-- Verificar FKs huérfanas
SELECT 'core.ipr.funding_source_id' as fk, COUNT(*)
FROM core.ipr
WHERE funding_source_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM ref.category WHERE id = funding_source_id)
UNION ALL
SELECT 'txn.event.fund_type_id', COUNT(*)
FROM txn.event
WHERE fund_type_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM ref.category WHERE id = fund_type_id);
-- Repetir para cada FK
```

### Completitud de Migración
```sql
-- Verificar que metadata solo tenga campos de auditoría
SELECT
    'core.ipr' as tabla,
    jsonb_object_keys(metadata) as key,
    COUNT(*)
FROM core.ipr
WHERE jsonb_object_keys(metadata) NOT IN ('source', 'legacy_id', 'codigo_normalizado', 'fuente_original', 'origen', 'codigo_convenios')
GROUP BY 1,2;
-- Repetir para cada tabla
```

### Auditoría de Pérdida de Datos
```sql
-- Comparar conteos antes/después
SELECT
    'ANTES' as momento,
    COUNT(*) as registros,
    COUNT(metadata->>'fiscal_year') as fiscal_year_en_metadata
FROM core.budget_commitment_backup
UNION ALL
SELECT
    'DESPUES',
    COUNT(*),
    COUNT(fiscal_year) as fiscal_year_en_columna
FROM core.budget_commitment;
```

---

## Riesgos y Mitigaciones

### Riesgo 1: Pérdida de datos en migración
**Mitigación**:
- Backup de tablas antes de cada fase
- Validación de conteos pre/post
- Scripts de rollback probados

### Riesgo 2: Inconsistencias en mapeo a ref.category
**Mitigación**:
- Crear categorías faltantes antes de migración
- Validar 100% de match antes de limpieza
- Mantener valores originales en metadata hasta validación final

### Riesgo 3: Performance en tablas particionadas (txn.event)
**Mitigación**:
- Ejecutar migración por partición
- Crear índices después de migración
- Monitorear uso de disco

### Riesgo 4: FKs a tablas no normalizadas (ej: core.person)
**Mitigación**:
- Normalizar core.person ANTES de crear FKs desde otras tablas
- Crear personas faltantes desde metadata
- Permitir NULL en FKs opcionales

---

## Checklist de Implementación

### Por cada FASE:

- [ ] Crear backup de tabla
```sql
CREATE TABLE tabla_backup AS SELECT * FROM tabla;
```

- [ ] Crear schemes en ref.category (si aplica)
```sql
INSERT INTO ref.category ...;
```

- [ ] Crear columnas nuevas
```sql
ALTER TABLE tabla ADD COLUMN ...;
```

- [ ] Migrar datos de metadata a columnas
```sql
UPDATE tabla SET columna = metadata->>'key';
```

- [ ] Crear índices
```sql
CREATE INDEX idx_tabla_columna ON tabla(columna);
```

- [ ] Validar integridad
```sql
-- Scripts de validación
```

- [ ] Limpiar metadata
```sql
UPDATE tabla SET metadata = metadata - 'key';
```

- [ ] Actualizar documentación
```bash
# Actualizar GOREOS_ERD_v3.md con nuevas columnas
```

- [ ] Actualizar loaders ETL
```python
# Modificar scripts en etl/migration/loaders/
```

- [ ] Ejecutar tests
```bash
pytest tests/test_tabla.py
```

- [ ] Commit cambios
```bash
git add . && git commit -m "feat(normalize): FASE X - tabla"
```

---

## Scripts de Soporte

### Script 1: Generar ALTER TABLE para todas las columnas
```bash
# Ubicación: etl/migration/scripts/generate_alter_tables.py
python etl/migration/scripts/generate_alter_tables.py \
    --table core.ipr \
    --phase 3 \
    --output /tmp/alter_tables_fase3.sql
```

### Script 2: Validar consistencia metadata vs columnas
```bash
# Ubicación: etl/migration/scripts/validate_normalization.py
python etl/migration/scripts/validate_normalization.py \
    --table core.organization \
    --check rut,org_type_id
```

### Script 3: Generar categorías desde valores únicos
```bash
# Ubicación: etl/migration/scripts/generate_categories.py
python etl/migration/scripts/generate_categories.py \
    --table txn.event \
    --field data->>'fondo' \
    --scheme event_fund_type
```

---

## Métricas de Éxito

### Objetivo 1: Reducción de uso de JSONB
- Meta: Reducir keys en metadata en ≥50% por tabla
- Medición: Comparar conteo de keys antes/después

### Objetivo 2: Integridad referencial
- Meta: 100% de FKs válidas
- Medición: Query de validación sin resultados

### Objetivo 3: Performance
- Meta: No degradar tiempos de consulta
- Medición: Benchmark de queries críticas antes/después

### Objetivo 4: Completitud
- Meta: 0 datos perdidos en migración
- Medición: Conteo de registros y suma de valores numéricos

---

## Próximos Pasos

1. **Revisión**: Revisar este plan con equipo de desarrollo y negocio
2. **Aprobación**: Validar priorización y alcance
3. **Preparación**: Crear scripts de migración y validación
4. **Piloto**: Ejecutar FASE 1 en ambiente de desarrollo
5. **Iteración**: Ajustar plan basado en aprendizajes
6. **Rollout**: Ejecutar fases 2-6 según cronograma

---

## Referencias

- [LECCIONES_APRENDIDAS.md](/Users/felixsanhueza/Developer/goreos/etl/migration/LECCIONES_APRENDIDAS.md)
- [PRE_LOADER_CHECKLIST.md](/Users/felixsanhueza/Developer/goreos/etl/migration/PRE_LOADER_CHECKLIST.md)
- [GOREOS_ERD_v3.md](/Users/felixsanhueza/Developer/goreos/model/model_goreos/docs/GOREOS_ERD_v3.md)
- [Patron Category](https://github.com/tuneando-code/GOREOS/wiki/Category-Pattern)

---

**Documento mantenido por**: Equipo de Desarrollo GORE_OS
**Última actualización**: 2026-01-30
**Versión**: 1.0
