# REPORTE DE EJECUCIÓN: NORMALIZACIÓN v3.0 FASE MEDIA (CAMPOS 4-5)

**Fecha**: 2026-01-30
**Ejecutor**: arquitecto-gore (CM-ARTIFACT-GENERATOR)
**Script**: `etl/migration/sql/normalize_jsonb_v3_fase_media_4-5.sql`
**Estado**: ✅ COMPLETADO

---

## RESUMEN EJECUTIVO

Se completó exitosamente la normalización de 2 campos JSONB de prioridad MEDIA en las tablas `core.ipr_party` y `core.ipr`, migrando un total de **2,002 registros** a estructura relacional.

### Métricas Globales

| Métrica | Valor |
|---------|-------|
| **Campos normalizados** | 2 |
| **Tablas afectadas** | 2 (ipr_party, ipr) |
| **Registros migrados** | 2,002 |
| **Match rate promedio** | 100% |
| **Tiempo de ejecución** | ~600ms |
| **Integridad referencial** | ✓ 100% (0 FK órfanos) |

---

## NORMALIZACIONES EJECUTADAS

### Normalización 4: `core.ipr_party.division → sponsor_division_id`

**Ontología**: `gnub:SponsorDivision`
**Tipo**: UUID FK a `core.organization`
**Índice**: `idx_ipr_party_sponsor_division` (partial WHERE sponsor_division_id IS NOT NULL)

#### Resultados

| Métrica | Valor |
|---------|-------|
| Registros con metadata.division | 37 |
| Registros migrados (sponsor_division_id populated) | 37 |
| Match rate | **100%** |
| Casos sin mapeo | 0 |

#### Mapeo Manual Aplicado

Debido a inconsistencias en nomenclatura de divisiones entre metadata JSONB y `core.organization`, se utilizó un mapeo manual:

| metadata.division | organization.code | organization.name |
|-------------------|-------------------|-------------------|
| DIDESO | ORG_GORE-DIDESO | División de Desarrollo Social - GORE Ñuble |
| DIFOI | ORG_GORE-DIFOI | División de Fomento e Industria - GORE Ñuble |
| DIPIR | DIPIR | División de Planificación e Inversión Regional |
| DIPLADE | DIPLADE | División de Planificación y Desarrollo |
| DIT | DIT | División de Infraestructura y Transporte |

#### Distribución de Divisiones Patrocinadoras

| División | IPR Parties |
|----------|-------------|
| División de Desarrollo Social - GORE Ñuble | 13 (35.1%) |
| División de Infraestructura y Transporte | 8 (21.6%) |
| División de Fomento e Industria - GORE Ñuble | 8 (21.6%) |
| División de Planificación e Inversión Regional | 5 (13.5%) |
| División de Planificación y Desarrollo | 3 (8.1%) |

**Total**: 37 ipr_party records

---

### Normalización 5: `core.ipr.origen → is_municipal_origin`

**Ontología**: `gnub:MunicipalOrigin`
**Tipo**: BOOLEAN (DEFAULT false)
**Índice**: `idx_ipr_municipal_origin` (partial WHERE is_municipal_origin = true)

#### Resultados

| Métrica | Valor |
|---------|-------|
| Registros con metadata.origen | 1,965 |
| Registros migrados (is_municipal_origin populated) | 1,965 |
| Match rate | **100%** |
| Valores NULL | 0 |

#### Lógica de Migración

```sql
CASE
    WHEN UPPER(TRIM(metadata->>'origen')) = 'MUNICIPIO' THEN true
    ELSE false
END
```

- **MUNICIPIO** → `true`
- **SECTORIAL / OTRO** → `false`

#### Distribución de Origen

| Origen | Total IPRs | Porcentaje |
|--------|-----------|------------|
| Municipal (true) | 1,327 | 67.53% |
| Sectorial/Otro (false) | 638 | 32.47% |

**Total con metadata.origen**: 1,965 IPRs
**Total IPRs en BD**: 3,621

**Nota**: 1,656 IPRs (45.76%) no tienen valor en `metadata->>'origen'` y mantienen el default `false`.

---

## CAMBIOS DE ESQUEMA

### Tabla `core.ipr_party`

```sql
-- Nueva columna
ALTER TABLE core.ipr_party
ADD COLUMN sponsor_division_id UUID REFERENCES core.organization(id);

-- Nuevo índice
CREATE INDEX idx_ipr_party_sponsor_division
ON core.ipr_party(sponsor_division_id)
WHERE sponsor_division_id IS NOT NULL;
```

**Impacto**:
- 37 registros con FK poblada (0.57% de 6,447 total ipr_party records)
- FK apunta a organizaciones tipo `DIVISION` en `core.organization`

### Tabla `core.ipr`

```sql
-- Nueva columna
ALTER TABLE core.ipr
ADD COLUMN is_municipal_origin BOOLEAN DEFAULT false;

-- Nuevo índice
CREATE INDEX idx_ipr_municipal_origin
ON core.ipr(is_municipal_origin)
WHERE is_municipal_origin = true;
```

**Impacto**:
- 1,327 IPRs marcados como `true` (36.65% de 3,621 total)
- 2,294 IPRs marcados como `false` (63.35%)
- Índice parcial optimiza queries sobre IPRs de origen municipal

---

## VERIFICACIONES DE INTEGRIDAD

### Integridad Referencial (FK)

```sql
✓ sponsor_division_id: 0 FK órfanos
  - Todas las 37 FKs apuntan a registros válidos en core.organization
  - Todas las organizaciones tienen org_type_id = DIVISION
```

### Verificación de Índices

```sql
✓ idx_ipr_party_sponsor_division: CREADO (partial index)
✓ idx_ipr_municipal_origin: CREADO (partial index)
```

### Coherencia de Datos

| Verificación | Estado |
|-------------|--------|
| sponsor_division_id sin NULL indeseados | ✓ |
| is_municipal_origin solo true/false | ✓ |
| Mapeo 1:1 metadata → FK | ✓ 100% |
| Valores inconsistentes | 0 |

---

## LECCIONES APRENDIDAS

### 1. Mapeo Manual vs Fuzzy Matching

**Situación**: Las divisiones en `metadata->>'division'` usan nomenclatura abreviada (DIDESO, DIFOI), mientras que `core.organization` usa nombres completos.

**Solución aplicada**: Mapeo manual explícito en tabla temporal `_temp_division_mapping`.

**Ventaja**:
- 100% de precisión
- 0 falsos positivos
- Trazabilidad completa

**Desventaja**:
- No escalable a nuevas divisiones
- Requiere mantenimiento manual

**Recomendación**: Considerar estandarización de nomenclatura de divisiones en futuros loaders.

### 2. Boolean con Default vs Esquema Categorial

**Situación**: `metadata->>'origen'` tenía solo 2 valores (MUNICIPIO vs SECTORIAL/OTRO).

**Decisión**: Usar BOOLEAN en lugar de FK a `ref.category` scheme.

**Justificación** (siguiendo Auditoría Categorial v3.0):
- ❌ Crear scheme con 2 valores viola principio de parsimonia
- ✓ BOOLEAN es más eficiente (1 byte vs 16 bytes UUID)
- ✓ Índice parcial optimiza queries frecuentes (IPRs municipales)
- ✓ Semántica clara: `is_municipal_origin = true` es más legible que FK lookup

**Resultado**: Coherencia ontológica mantenida sin overhead categorial.

### 3. Partial Indexes para Optimización

**Patrón aplicado**:
```sql
CREATE INDEX idx_name ON table(column) WHERE column IS NOT NULL;
CREATE INDEX idx_name ON table(column) WHERE column = true;
```

**Ventaja**:
- Reduce tamaño de índice (~60-90% según selectividad)
- Mejora rendimiento de queries frecuentes
- Menor costo de mantenimiento (INSERT/UPDATE)

**Aplicado en**:
- `idx_ipr_party_sponsor_division` (37 entradas vs 6,447 total)
- `idx_ipr_municipal_origin` (1,327 entradas vs 3,621 total)

---

## BACKUPS Y ROLLBACK

### Backups Temporales Creados

```sql
_backup_ipr_party_v3_media (6,447 registros)
_backup_ipr_v3_media (3,621 registros)
```

**Ubicación**: Tablas temporales en sesión actual
**Disponibilidad**: Hasta fin de sesión psql

### Procedimiento de Rollback

Si se requiere revertir cambios:

```sql
-- 1. Restaurar datos (sponsor_division_id quedará NULL)
BEGIN;
  UPDATE core.ipr_party ip
  SET sponsor_division_id = NULL
  WHERE sponsor_division_id IS NOT NULL;

  UPDATE core.ipr i
  SET is_municipal_origin = false;
COMMIT;

-- 2. Eliminar columnas (opcional)
ALTER TABLE core.ipr_party DROP COLUMN sponsor_division_id;
ALTER TABLE core.ipr DROP COLUMN is_municipal_origin;

-- 3. Eliminar índices
DROP INDEX core.idx_ipr_party_sponsor_division;
DROP INDEX core.idx_ipr_municipal_origin;
```

**Nota**: metadata JSONB original NO fue modificado, por lo que siempre es posible re-ejecutar migración.

---

## PRÓXIMOS PASOS

### Fase Crítica (Campos 1-3)

**Script siguiente**: `etl/migration/sql/normalize_jsonb_v3_fase_critica_1-3.sql`

**Normalizaciones críticas pendientes**:

1. **core.organization.rut** (3,308 registros)
   - Normalización: JSONB → VARCHAR(12) + CHECK constraint
   - Impacto: Integridad referencial, duplicados

2. **core.person.estamento** (1,208 registros)
   - Normalización: JSONB → estamento_id FK
   - Requiere: Scheme `estamento` en ref.category

3. **core.ipr.executor** (880+ registros)
   - Normalización: JSONB → executor_id FK (ya existe en schema)
   - Sincronización: metadata vs FK en ipr_party

### Validación Post-Normalización

Después de completar todas las fases:

```sql
-- 1. Verificar coherencia categorial
SELECT table_name, column_name, COUNT(DISTINCT scheme)
FROM (analytical query sobre todas las FKs a ref.category)
GROUP BY table_name, column_name
HAVING COUNT(DISTINCT scheme) > 1; -- Debe retornar 0 rows

-- 2. Auditoría de metadata remanente
SELECT
    table_schema,
    table_name,
    jsonb_object_keys(metadata) as remaining_keys,
    COUNT(*) as occurrences
FROM (UNION de todas las tablas con metadata)
GROUP BY table_schema, table_name, remaining_keys
ORDER BY occurrences DESC;

-- 3. Verificar índices parciales
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE indexdef LIKE '%WHERE%'
AND schemaname = 'core';
```

---

## ANEXO: QUERIES DE VERIFICACIÓN

### Verificar sponsor_division_id

```sql
-- Distribución por división
SELECT
    o.code,
    o.name,
    COUNT(*) as ipr_parties
FROM core.ipr_party ip
JOIN core.organization o ON ip.sponsor_division_id = o.id
GROUP BY o.code, o.name
ORDER BY ipr_parties DESC;

-- Verificar FK integrity
SELECT COUNT(*) as orphan_fks
FROM core.ipr_party ip
LEFT JOIN core.organization o ON ip.sponsor_division_id = o.id
WHERE ip.sponsor_division_id IS NOT NULL
AND o.id IS NULL;
-- Expected: 0
```

### Verificar is_municipal_origin

```sql
-- Distribución origen municipal vs sectorial
SELECT
    is_municipal_origin,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as pct
FROM core.ipr
GROUP BY is_municipal_origin;

-- Comparar con metadata original (debe coincidir 100%)
SELECT
    metadata->>'origen' as origen_metadata,
    is_municipal_origin,
    COUNT(*) as total
FROM core.ipr
WHERE metadata->>'origen' IS NOT NULL
GROUP BY metadata->>'origen', is_municipal_origin
ORDER BY origen_metadata, is_municipal_origin;
-- Expected: MUNICIPIO → true, SECTORIAL/OTRO → false
```

### Verificar índices parciales

```sql
-- Tamaño de índices
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
FROM pg_indexes
WHERE schemaname = 'core'
AND indexname IN ('idx_ipr_party_sponsor_division', 'idx_ipr_municipal_origin')
ORDER BY tablename, indexname;
```

---

## CONCLUSIONES

✅ **Normalización v3.0 Fase MEDIA completada con éxito**

- **100% match rate** en ambas normalizaciones
- **0 errores** de integridad referencial
- **2 nuevas columnas** relacionales optimizadas con índices parciales
- **Mapeo manual documentado** para sponsor_division_id
- **Decisión justificada** de usar BOOLEAN para is_municipal_origin

**Impacto**:
- Mejora en queries de origen municipal (índice parcial)
- Trazabilidad de divisiones patrocinadoras
- Reducción de dependencia en metadata JSONB
- Coherencia ontológica mantenida (gnub:SponsorDivision, gnub:MunicipalOrigin)

**Estado del sistema**: ESTABLE, listo para Fase CRITICA.

---

**Generado**: 2026-01-30
**Revisor**: arquitecto-gore
**Próxima acción**: Ejecutar `normalize_jsonb_v3_fase_critica_1-3.sql`
