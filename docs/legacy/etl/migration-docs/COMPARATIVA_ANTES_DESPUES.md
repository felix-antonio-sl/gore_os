# Comparativa Antes/Después: Normalización JSONB

**Propósito**: Visualizar el impacto de la normalización en estructura de datos y capacidades del sistema.

---

## Vista General

### Métricas Globales

| Métrica | Antes | Después | Cambio |
|---------|-------|---------|--------|
| **Keys en JSONB** | 76+ | 35 | -54% ✅ |
| **Columnas relacionales** | 89 | 104+ | +17% ✅ |
| **Foreign Keys** | 47 | 62+ | +32% ✅ |
| **Tablas normalizadas** | 0 | 3 | +3 ✅ |
| **Schemes en ref.category** | 38 | 41+ | +8% ✅ |
| **Integridad referencial** | Parcial | Total | +100% ✅ |

---

## Por Tabla

### core.budget_commitment (4,609 registros)

#### Antes
```json
{
  "id": "uuid",
  "commitment_number": "2024-001",
  "amount": 5000000,
  "ipr_id": "uuid",
  "metadata": {
    "fiscal_year": "2024",           // ⚠️ En JSON
    "fondo": "FNDR",                  // ⚠️ En JSON
    "bip": "30123456-0",              // ⚠️ Redundante?
    "codigo_original": "ABC123",      // Auditoría
    "source": "IDIS"                  // Auditoría
  }
}
```

**Problemas**:
- ❌ `fiscal_year` no indexable para consultas por año
- ❌ `fondo` sin validación de valores permitidos
- ❌ Imposible hacer JOIN directo por año fiscal

#### Después
```sql
CREATE TABLE core.budget_commitment (
  id UUID,
  commitment_number VARCHAR(32),
  amount NUMERIC(18,2),
  ipr_id UUID REFERENCES core.ipr(id),
  fiscal_year INTEGER,              -- ✅ Nueva columna
  fund_id UUID REFERENCES ref.category(id), -- ✅ FK validada
  metadata JSONB DEFAULT '{}'       -- Solo auditoría
);

-- metadata:
{
  "bip": "30123456-0",       // Temporal hasta análisis
  "codigo_original": "ABC123",
  "source": "IDIS"
}
```

**Mejoras**:
- ✅ Consultas por año fiscal: `WHERE fiscal_year = 2024` (indexado)
- ✅ Validación de fondos vía FK a ref.category
- ✅ Posibilidad de agregar CONSTRAINT CHECK en fiscal_year

**Queries optimizadas**:
```sql
-- Antes (lento)
SELECT * FROM core.budget_commitment
WHERE metadata->>'fiscal_year' = '2024';

-- Después (rápido, usa índice)
SELECT * FROM core.budget_commitment
WHERE fiscal_year = 2024;
```

---

### txn.event (4,040 registros - particionada)

#### Antes
```json
{
  "id": "uuid",
  "event_type_id": "uuid",           // ✅ Ya normalizado
  "subject_id": "uuid",
  "occurred_at": "2024-01-15",
  "data": {
    "tipo_evento_id": "uuid",        // ⚠️ REDUNDANTE con event_type_id
    "tipo_evento_name": "aprueba_convenio", // ⚠️ REDUNDANTE
    "fondo": "SEGURIDAD",            // ⚠️ Sin validación
    "tipologia": "SEGURIDAD",        // ⚠️ Duplicado de fondo?
    "estado_normalizado": "COMPLETADO", // ⚠️ En JSON
    "monto_transferido": "1500000",  // ⚠️ Debería estar en txn.magnitude
    "comuna": "CHILLÁN",             // ⚠️ Sin FK a territory
    "provincia": "DIGUILLÍN",        // ⚠️ Sin FK a territory
    "numero_documento": "RES-123",   // ⚠️ Sin FK a document
    "legacy_id": "abc-123",          // Auditoría
    "source": "PROGS"                // Auditoría
  }
}
```

**Problemas**:
- ❌ 3 campos redundantes con `event_type_id`
- ❌ Fondos y tipologías sin validación
- ❌ Estados en texto libre
- ❌ Montos desacoplados de txn.magnitude
- ❌ Territorios sin relación a core.territory

#### Después
```sql
CREATE TABLE txn.event (
  id UUID,
  event_type_id UUID REFERENCES ref.category(id), -- ✅ Ya existía
  subject_id UUID,
  occurred_at TIMESTAMPTZ,
  fund_type_id UUID REFERENCES ref.category(id),     -- ✅ Nuevo
  event_category_id UUID REFERENCES ref.category(id), -- ✅ Nuevo
  execution_state_id UUID REFERENCES ref.category(id), -- ✅ Nuevo
  document_id UUID REFERENCES core.document(id),     -- ✅ Nuevo
  data JSONB DEFAULT '{}'  -- Solo auditoría
) PARTITION BY RANGE (occurred_at);

CREATE TABLE txn.event_territory (
  id UUID PRIMARY KEY,
  event_id UUID NOT NULL,
  territory_id UUID REFERENCES core.territory(id), -- ✅ Nuevo
  territory_type VARCHAR(20) CHECK (territory_type IN ('PROVINCIA', 'COMUNA'))
);

-- data (reducido):
{
  "legacy_id": "abc-123",
  "source": "PROGS",
  "observaciones": "..."
}
```

**Mejoras**:
- ✅ Eliminación de redundancias (tipo_evento)
- ✅ Validación de fondos y estados vía ref.category
- ✅ Relación formal a territorios
- ✅ Montos migrados a txn.magnitude (tabla especializada)
- ✅ FK a documentos para trazabilidad

**Queries optimizadas**:
```sql
-- Antes (muy lento, sin índice)
SELECT * FROM txn.event
WHERE data->>'fondo' = 'SEGURIDAD'
  AND data->>'estado_normalizado' = 'COMPLETADO';

-- Después (rápido, 2 índices)
SELECT * FROM txn.event
WHERE fund_type_id = (SELECT id FROM ref.category WHERE scheme = 'event_fund_type' AND code = 'SEGURIDAD')
  AND execution_state_id = (SELECT id FROM ref.category WHERE scheme = 'execution_state' AND code = 'COMPLETADO');

-- Con JOIN para labels
SELECT
  e.id,
  ft.label as fondo,
  es.label as estado
FROM txn.event e
JOIN ref.category ft ON e.fund_type_id = ft.id
JOIN ref.category es ON e.execution_state_id = es.id
WHERE ft.code = 'SEGURIDAD'
  AND es.code = 'COMPLETADO';
```

---

### core.ipr (3,621 registros)

#### Antes
```json
{
  "id": "uuid",
  "codigo_bip": "30123456-0",
  "name": "Proyecto X",
  "funding_source_id": "uuid",       // ✅ Ya normalizado
  "executor_id": "uuid",             // ✅ Ya normalizado
  "metadata": {
    "cod_unico_idis": "1-2019",      // ⚠️ Identificador crítico en JSON
    "tipologia_original": "FRIL",    // ⚠️ Debería enriquecer ipr_type_id
    "etapa_original": "EJECUCIÓN",   // ⚠️ Debería enriquecer mcd_phase_id
    "event_id_original": "uuid-str", // ⚠️ Sin FK a txn.event
    "unidad_tecnica": "DIT",         // ⚠️ Sin FK a organization
    "provincia": "DIGUILLÍN",        // ✅ Ya normalizado (ipr_territory)
    "comuna": "CHILLÁN",             // ✅ Ya normalizado (ipr_territory)
    "source": "IDIS"                 // Auditoría
  }
}
```

#### Después
```sql
CREATE TABLE core.ipr (
  id UUID,
  codigo_bip VARCHAR(20) UNIQUE,
  codigo_idis VARCHAR(50) UNIQUE,   -- ✅ Nueva columna
  name TEXT,
  ipr_type_id UUID REFERENCES ref.category(id), -- ✅ Enriquecido
  mcd_phase_id UUID REFERENCES ref.category(id), -- ✅ Enriquecido
  funding_source_id UUID REFERENCES ref.category(id), -- ✅ Ya existía
  executor_id UUID REFERENCES core.organization(id), -- ✅ Ya existía
  origin_event_id UUID REFERENCES txn.event(id), -- ✅ Nuevo
  technical_unit_id UUID REFERENCES core.organization(id), -- ✅ Nuevo
  metadata JSONB DEFAULT '{}'
);

-- metadata (reducido):
{
  "source": "IDIS",
  "legacy_id": "...",
  "origen": "SECTORIAL",
  "codigo_normalizado": "1"
}
```

**Mejoras**:
- ✅ `codigo_idis` como columna única (identificador crítico)
- ✅ `ipr_type_id` enriquecido desde tipología original
- ✅ `mcd_phase_id` enriquecido desde etapa original
- ✅ FK a evento de origen (trazabilidad completa)
- ✅ FK a unidad técnica responsable

---

### core.organization (3,308 registros)

#### Antes
```json
{
  "id": "uuid",
  "code": "ORG-001",
  "name": "MUNICIPALIDAD DE CHILLÁN",
  "org_type_id": null,               // ⚠️ NULL pero existe en metadata
  "metadata": {
    "rut": "69.150.000-7",           // ⚠️ Identificador fiscal en JSON
    "tipo_institucion": "MUNICIPALIDAD", // ⚠️ Debería estar en org_type_id
    "tipo": "MUNICIPALIDAD",         // ⚠️ Redundante
    "aliases": [                     // ⚠️ Array en JSON
      "Muni Chillán",
      "I. Municipalidad de Chillán"
    ],
    "source": "PROGS"
  }
}
```

#### Después
```sql
CREATE TABLE core.organization (
  id UUID,
  code VARCHAR(32) UNIQUE,
  name TEXT,
  rut VARCHAR(12) UNIQUE,            -- ✅ Nueva columna
  org_type_id UUID REFERENCES ref.category(id), -- ✅ Enriquecido
  metadata JSONB DEFAULT '{}'
);

CREATE TABLE core.organization_alias (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES core.organization(id),
  alias_name TEXT NOT NULL,
  alias_type VARCHAR(50),
  UNIQUE (organization_id, alias_name)
);

-- metadata (reducido):
{
  "source": "PROGS",
  "legacy_id": "...",
  "nombre_original": "...",
  "nombre_nlp": "..."
}
```

**Mejoras**:
- ✅ RUT como columna única (búsquedas rápidas por identificador fiscal)
- ✅ `org_type_id` poblado desde metadata
- ✅ Aliases normalizados en tabla relacional (búsquedas por alias)

**Queries optimizadas**:
```sql
-- Antes (lento)
SELECT * FROM core.organization
WHERE metadata->>'rut' = '69.150.000-7';

-- Después (usa índice único)
SELECT * FROM core.organization
WHERE rut = '69.150.000-7';

-- Búsqueda por alias (NUEVO)
SELECT o.*
FROM core.organization o
JOIN core.organization_alias a ON o.id = a.organization_id
WHERE a.alias_name ILIKE '%muni chillán%';
```

---

### core.agreement (533 registros)

#### Antes
```json
{
  "id": "uuid",
  "agreement_number": "CONV-2024-001",
  "state_id": null,                  // ⚠️ NULL pero existe en metadata
  "metadata": {
    "estado_convenio_raw": "FIRMADO", // ⚠️ Debería estar en state_id
    "referente_tecnico": "JUAN PÉREZ", // ⚠️ Sin FK a person
    "estado_cgr_norm": "APROBADO",   // ⚠️ Sin FK a category
    "territorio_id": "uuid-str",     // ⚠️ UUID como string
    "source": "fact_convenio"
  }
}
```

#### Después
```sql
CREATE TABLE core.agreement (
  id UUID,
  agreement_number VARCHAR(32),
  state_id UUID REFERENCES ref.category(id),        -- ✅ Enriquecido
  technical_referent_id UUID REFERENCES core.person(id), -- ✅ Nuevo
  cgr_state_id UUID REFERENCES ref.category(id),    -- ✅ Nuevo
  territory_id UUID REFERENCES core.territory(id),  -- ✅ Nuevo
  metadata JSONB DEFAULT '{}'
);

-- metadata (reducido):
{
  "source": "fact_convenio",
  "legacy_id": "...",
  "origen_hoja": "CONVENIOS_2023_2024"
}
```

**Mejoras**:
- ✅ Estado del convenio normalizado
- ✅ Referente técnico como FK (trazabilidad)
- ✅ Estado CGR validado vía ref.category
- ✅ Territorio como FK (no string)

---

### core.person (111 registros)

#### Antes
```json
{
  "id": "uuid",
  "rut": "12.345.678-9",
  "names": "Juan",
  "paternal_surname": "Pérez",
  "metadata": {
    "estamento": "Profesional",      // ⚠️ En JSON
    "calificacion": "Ingeniero Comercial", // ⚠️ En JSON
    "cargo_ultimo": "Jefe de Proyecto", // ⚠️ En JSON
    "source": "personal_gore"
  }
}
```

#### Después
```sql
CREATE TABLE core.person (
  id UUID,
  rut VARCHAR(12) UNIQUE,
  names TEXT,
  paternal_surname TEXT,
  employee_category_id UUID REFERENCES ref.category(id), -- ✅ Nuevo
  last_position TEXT,                -- ✅ Nuevo
  metadata JSONB DEFAULT '{}'
);

CREATE TABLE core.person_qualification (
  id UUID PRIMARY KEY,
  person_id UUID REFERENCES core.person(id),
  qualification_name TEXT NOT NULL,
  is_primary BOOLEAN DEFAULT true,
  obtained_date DATE,
  institution TEXT
);

-- metadata (reducido):
{
  "source": "personal_gore",
  "legacy_id": "..."
}
```

**Mejoras**:
- ✅ Estamento validado vía ref.category
- ✅ Cargo como columna consultable
- ✅ Calificaciones en tabla relacional (permite múltiples títulos)

---

## Impacto en Consultas Comunes

### 1. Reporte de presupuesto por año

**Antes** (sin índice, lento):
```sql
SELECT
  SUM(amount) as total,
  metadata->>'fiscal_year' as year
FROM core.budget_commitment
WHERE metadata->>'fiscal_year' = '2024'
GROUP BY metadata->>'fiscal_year';
```

**Después** (con índice, 10-100x más rápido):
```sql
SELECT
  SUM(amount) as total,
  fiscal_year as year
FROM core.budget_commitment
WHERE fiscal_year = 2024
GROUP BY fiscal_year;
```

---

### 2. Eventos por fondo y estado

**Antes** (sin índice, muy lento):
```sql
SELECT
  data->>'fondo' as fondo,
  data->>'estado_normalizado' as estado,
  COUNT(*)
FROM txn.event
WHERE data->>'fondo' = 'SEGURIDAD'
  AND data->>'estado_normalizado' = 'COMPLETADO'
GROUP BY data->>'fondo', data->>'estado_normalizado';
```

**Después** (con 2 índices + JOIN, rápido):
```sql
SELECT
  ft.label as fondo,
  es.label as estado,
  COUNT(*)
FROM txn.event e
JOIN ref.category ft ON e.fund_type_id = ft.id
JOIN ref.category es ON e.execution_state_id = es.id
WHERE ft.code = 'SEGURIDAD'
  AND es.code = 'COMPLETADO'
GROUP BY ft.label, es.label;
```

---

### 3. IPRs por ejecutor y territorio

**Antes** (parcialmente normalizado):
```sql
SELECT
  o.name as ejecutor,
  metadata->>'comuna' as comuna,  -- ⚠️ Texto sin validar
  COUNT(*)
FROM core.ipr i
JOIN core.organization o ON i.executor_id = o.id
WHERE metadata->>'comuna' = 'CHILLÁN'
GROUP BY o.name, metadata->>'comuna';
```

**Después** (totalmente normalizado):
```sql
SELECT
  o.name as ejecutor,
  t.name as comuna,
  COUNT(*)
FROM core.ipr i
JOIN core.organization o ON i.executor_id = o.id
JOIN core.ipr_territory it ON i.id = it.ipr_id
JOIN core.territory t ON it.territory_id = t.id
WHERE t.code = 'CHILLAN'
  AND it.is_primary = true
GROUP BY o.name, t.name;
```

---

### 4. Organizaciones por RUT

**Antes** (sin índice):
```sql
SELECT * FROM core.organization
WHERE metadata->>'rut' = '69.150.000-7';
```

**Después** (índice único, instant):
```sql
SELECT * FROM core.organization
WHERE rut = '69.150.000-7';
```

---

### 5. Búsqueda de organizaciones por alias

**Antes** (imposible de forma eficiente):
```sql
-- No hay forma eficiente de buscar en arrays JSONB
SELECT *
FROM core.organization
WHERE metadata->'aliases' @> '"Muni Chillán"'::jsonb;
```

**Después** (índice en tabla relacional):
```sql
SELECT DISTINCT o.*
FROM core.organization o
JOIN core.organization_alias a ON o.id = a.organization_id
WHERE a.alias_name ILIKE '%muni%chillán%';
```

---

## Validaciones Habilitadas

### Antes
- ⚠️ Sin validación de valores en JSONB
- ⚠️ Valores inconsistentes posibles
- ⚠️ Typos y variaciones sin control

Ejemplo de problema:
```json
// Mismo concepto, 3 formas diferentes
{"fondo": "SEGURIDAD"}
{"fondo": "Seguridad"}
{"fondo": "seguridad"}
```

### Después
- ✅ FK a ref.category valida valores permitidos
- ✅ CHECK constraints en tipos
- ✅ UNIQUE constraints en identificadores
- ✅ NOT NULL donde corresponde

Ejemplo de validación:
```sql
-- Solo valores en ref.category son permitidos
INSERT INTO txn.event (fund_type_id, ...)
VALUES ('uuid-invalido', ...);
-- ERROR: violates foreign key constraint

-- Valor correcto
INSERT INTO txn.event (fund_type_id, ...)
VALUES (
  (SELECT id FROM ref.category WHERE scheme = 'event_fund_type' AND code = 'SEGURIDAD'),
  ...
);
-- OK
```

---

## Métricas de Performance Esperadas

| Operación | Antes | Después | Mejora |
|-----------|-------|---------|--------|
| SELECT WHERE fiscal_year = X | 50ms | 5ms | **10x** |
| SELECT WHERE fondo = X | 100ms | 10ms | **10x** |
| JOIN eventos + fondos | 200ms | 20ms | **10x** |
| Búsqueda por RUT | 30ms | 1ms | **30x** |
| Agregaciones por año | 150ms | 15ms | **10x** |
| COUNT eventos por estado | 80ms | 8ms | **10x** |

*Nota: Tiempos estimados en tabla con ~4,000 registros. Mejoras aumentan con volumen de datos.*

---

## Conclusión

### Resumen de beneficios

1. **Integridad**: De validación manual a automática vía FKs
2. **Performance**: 10-30x mejora en queries comunes
3. **Mantenibilidad**: Código SQL más limpio y legible
4. **Escalabilidad**: Índices apropiados para crecimiento futuro
5. **Trazabilidad**: Relaciones explícitas entre entidades
6. **Consultas**: Posibilidad de JOINs complejos y eficientes

### Próximos pasos

1. ✅ Aprobación del plan
2. ⬜ Ejecución por fases (7 semanas)
3. ⬜ Validación continua
4. ⬜ Documentación actualizada
5. ⬜ Capacitación al equipo en nuevas estructuras

---

**Fecha**: 2026-01-30
**Versión**: 1.0
