# NORMALIZACION JSONB V3 - FASE MEDIA (CAMPOS 1-3)
## Guía de Ejecución

**Fecha**: 2026-01-30
**Script**: `etl/migration/sql/normalize_jsonb_v3_fase_media_1-3.sql`
**Referencia**: `docs/AUDITORIA_CATEGORIAL_v3.0.md` (Prioridad MEDIA)

---

## Resumen Ejecutivo

Este script normaliza 3 campos JSONB de **PRIORIDAD MEDIA** identificados en la auditoría categorial v3.0, migrándolos a estructuras relacionales:

| # | Campo Original | Destino | Registros | Valores Únicos |
|---|---------------|---------|-----------|----------------|
| 1 | `core.person.metadata->>'cargo_ultimo'` | `core.position` (tabla nueva) | 110 personas | 87 cargos |
| 2 | `core.person.metadata->>'calificacion'` | `ref.category` scheme=`professional_qualification` | 110 personas | 57 calificaciones |
| 3 | `core.agreement.metadata->>'estado_cgr_norm'` | `ref.category` scheme=`cgr_outcome` | 129 agreements | 4 estados |

---

## Alineamiento Ontológico

| Normalización | Ontología | Concepto |
|--------------|-----------|----------|
| `core.position` | `tde:Cargo` | Cargos y posiciones laborales en el sector público |
| `professional_qualification` | `tde:CalificacionProfesional` | Títulos y calificaciones profesionales |
| `cgr_outcome` | `tde:EstadoCGR`, `gnub:ResolutionOutcome` | Estados de resultado de revisión CGR |

---

## Estructura del Script

### FASE 1: Cargo Último → core.position

**Acción**:
- Crea tabla `core.position` con campos: `id`, `code`, `name`, `organization_id`, `level`
- Inserta 87 cargos únicos desde `person.metadata->>'cargo_ultimo'`
- Agrega columna `person.position_id` (FK → `core.position`)
- Migra relaciones persona-cargo

**Índices creados**:
- `idx_position_org` (organization_id)
- `idx_position_active` (id WHERE deleted_at IS NULL)
- `idx_position_code` (code)
- `idx_position_metadata` (GIN sobre metadata)
- `idx_person_position` (person.position_id)

**Resultado esperado**: 100% de personas con `cargo_ultimo` tendrán `position_id` asignado

---

### FASE 2: Calificación → professional_qualification

**Acción**:
- Crea scheme `professional_qualification` con 17 categorías normalizadas
- Agrupa 57 calificaciones únicas en categorías semánticas:
  - `INGENIERO_COMERCIAL`, `INGENIERO_CIVIL`, `INGENIERO_INDUSTRIAL`, `INGENIERO_CONSTRUCTOR`
  - `ARQUITECTO`, `ABOGADO`, `CONTADOR`, `ADMINISTRADOR_PUBLICO`
  - `TRABAJADOR_SOCIAL`, `PERIODISTA`, `PROFESIONAL_SALUD`, `PROFESIONAL_EDUCACION`
  - `TECNICO`, `LICENCIA_MEDIA`, `SECRETARIA`, `INGENIERO_OTROS`, `OTROS`
- Agrega columna `person.qualification_id` (FK → `ref.category`)
- Utiliza mapeo fuzzy con `CASE WHEN` + `LIKE` para clasificación automática

**Mapeo Inteligente**:
```sql
WHEN UPPER(calificacion) LIKE '%INGENIER%COMERCIAL%' THEN 'INGENIERO_COMERCIAL'
WHEN UPPER(calificacion) LIKE '%ARQUITECTO%' OR LIKE '%ARQUITECTA%' THEN 'ARQUITECTO'
-- ... (ver script completo)
```

**CHECK Constraint**:
```sql
ALTER TABLE core.person ADD CONSTRAINT chk_qualification_scheme
    CHECK (qualification_id IS NULL OR
           fn_validate_category_scheme(qualification_id, 'professional_qualification'));
```

**Resultado esperado**: ~95-100% de personas con `calificacion` tendrán `qualification_id` asignado

---

### FASE 3: Estado CGR → cgr_outcome

**Acción**:
- Crea scheme `cgr_outcome` con 4 categorías:
  - `TOMADO_DE_RAZON` (86 agreements) - Aprobado sin observaciones
  - `TR_CON_ALCANCES` (37 agreements) - Aprobado con observaciones
  - `REPRESENTADO` (5 agreements) - Rechazado por CGR
  - `EN_CGR` (1 agreement) - En proceso de revisión
- Agrega columna `agreement.cgr_outcome_id` (FK → `ref.category`)
- Migra 129 agreements con estado CGR

**CHECK Constraint**:
```sql
ALTER TABLE core.agreement ADD CONSTRAINT chk_cgr_outcome_scheme
    CHECK (cgr_outcome_id IS NULL OR
           fn_validate_category_scheme(cgr_outcome_id, 'cgr_outcome'));
```

**Resultado esperado**: 100% de agreements con `estado_cgr_norm` tendrán `cgr_outcome_id` asignado

---

## Verificaciones de Integridad

### Categorical Univocity

El script verifica que cada FK column apunte a **exactamente 1 scheme**:

```sql
-- Debe retornar schemes = 1
SELECT COUNT(DISTINCT c.scheme) AS schemes
FROM core.person p
JOIN ref.category c ON c.id = p.qualification_id;

-- Debe retornar schemes = 1
SELECT COUNT(DISTINCT c.scheme) AS schemes
FROM core.agreement a
JOIN ref.category c ON c.id = a.cgr_outcome_id;
```

### Backups Temporales

Cada fase crea tabla temporal de backup:
- `backup_person_fase1` (cargo_ultimo)
- `backup_person_fase2` (calificacion)
- `backup_agreement_fase3` (estado_cgr_norm)

### Tasa de Éxito

El script calcula y reporta tasa de éxito para cada migración:
```
Tasa de éxito = (registros_migrados / registros_totales) * 100
```

Umbral esperado: **≥95%**

---

## Ejecución

### Prerequisitos

1. **Verificar esquema actual**:
```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "\d core.person"
docker exec goreos_db psql -U goreos -d goreos_model -c "\d core.agreement"
```

2. **Verificar que tablas/schemes NO existan**:
```bash
# Debe retornar 'f' (false)
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT EXISTS(SELECT 1 FROM information_schema.tables
              WHERE table_schema='core' AND table_name='position');"

# Debe retornar 0
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT COUNT(*) FROM ref.category
WHERE scheme IN ('professional_qualification', 'cgr_outcome');"
```

3. **Backup completo de la base de datos**:
```bash
docker exec goreos_db pg_dump -U goreos -d goreos_model \
    -f /tmp/backup_pre_normalizacion_media_1-3.sql

# O desde host
docker exec goreos_db pg_dump -U goreos -d goreos_model | \
    gzip > backups/goreos_model_pre_normalizacion_media_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Ejecución en Producción

```bash
# Ejecutar script completo
docker exec -i goreos_db psql -U goreos -d goreos_model \
    < etl/migration/sql/normalize_jsonb_v3_fase_media_1-3.sql
```

### Ejecución en Ambiente de Test

```bash
# 1. Clonar producción a test
docker exec goreos_db psql -U goreos -d postgres -c "
DROP DATABASE IF EXISTS goreos_model_test;
CREATE DATABASE goreos_model_test;"

docker exec goreos_db bash -c "
pg_dump -U goreos -d goreos_model | psql -U goreos -d goreos_model_test"

# 2. Ejecutar script en test
docker exec -i goreos_db psql -U goreos -d goreos_model_test \
    < etl/migration/sql/normalize_jsonb_v3_fase_media_1-3.sql

# 3. Verificar resultados
docker exec goreos_db psql -U goreos -d goreos_model_test -c "
SELECT 'position' as tabla, COUNT(*) FROM core.position
UNION ALL
SELECT 'professional_qualification', COUNT(*) FROM ref.category
WHERE scheme='professional_qualification'
UNION ALL
SELECT 'cgr_outcome', COUNT(*) FROM ref.category WHERE scheme='cgr_outcome';"
```

---

## Verificaciones Post-Ejecución

### 1. Verificar Categorical Univocity

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT
    'qualification_id' AS campo,
    COUNT(DISTINCT c.scheme) AS schemes,
    STRING_AGG(DISTINCT c.scheme, ', ') AS scheme_list
FROM core.person p
JOIN ref.category c ON c.id = p.qualification_id
WHERE p.qualification_id IS NOT NULL
UNION ALL
SELECT
    'cgr_outcome_id',
    COUNT(DISTINCT c.scheme),
    STRING_AGG(DISTINCT c.scheme, ', ')
FROM core.agreement a
JOIN ref.category c ON c.id = a.cgr_outcome_id
WHERE a.cgr_outcome_id IS NOT NULL;
"
```

**Esperado**: `schemes = 1` para ambas columnas

### 2. Verificar Tasas de Migración

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT
    'cargo_ultimo → position_id' AS migracion,
    COUNT(*) FILTER (WHERE metadata->>'cargo_ultimo' IS NOT NULL) AS total_fuente,
    COUNT(*) FILTER (WHERE position_id IS NOT NULL) AS migrados,
    ROUND(COUNT(*) FILTER (WHERE position_id IS NOT NULL)::NUMERIC /
          NULLIF(COUNT(*) FILTER (WHERE metadata->>'cargo_ultimo' IS NOT NULL), 0) * 100, 2) AS pct_exito
FROM core.person
UNION ALL
SELECT
    'calificacion → qualification_id',
    COUNT(*) FILTER (WHERE metadata->>'calificacion' IS NOT NULL),
    COUNT(*) FILTER (WHERE qualification_id IS NOT NULL),
    ROUND(COUNT(*) FILTER (WHERE qualification_id IS NOT NULL)::NUMERIC /
          NULLIF(COUNT(*) FILTER (WHERE metadata->>'calificacion' IS NOT NULL), 0) * 100, 2)
FROM core.person
UNION ALL
SELECT
    'estado_cgr_norm → cgr_outcome_id',
    COUNT(*) FILTER (WHERE metadata->>'estado_cgr_norm' IS NOT NULL),
    COUNT(*) FILTER (WHERE cgr_outcome_id IS NOT NULL),
    ROUND(COUNT(*) FILTER (WHERE cgr_outcome_id IS NOT NULL)::NUMERIC /
          NULLIF(COUNT(*) FILTER (WHERE metadata->>'estado_cgr_norm' IS NOT NULL), 0) * 100, 2)
FROM core.agreement;
"
```

**Esperado**: `pct_exito ≥ 95%` para todas las migraciones

### 3. Verificar Distribuciones

```bash
# Distribución de calificaciones profesionales
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT c.code, c.label, COUNT(p.id) as total_personas
FROM ref.category c
LEFT JOIN core.person p ON p.qualification_id = c.id
WHERE c.scheme = 'professional_qualification'
GROUP BY c.id, c.code, c.label
ORDER BY total_personas DESC;
"

# Distribución de estados CGR
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT c.code, c.label, COUNT(a.id) as total_agreements
FROM ref.category c
LEFT JOIN core.agreement a ON a.cgr_outcome_id = c.id
WHERE c.scheme = 'cgr_outcome'
GROUP BY c.id, c.code, c.label
ORDER BY total_agreements DESC;
"
```

### 4. Verificar Constraints

```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conname IN ('chk_qualification_scheme', 'chk_cgr_outcome_scheme')
ORDER BY table_name, conname;
"
```

---

## Rollback

Si se detectan problemas post-ejecución:

### Opción 1: Rollback Completo (Restaurar Backup)

```bash
# Restaurar desde backup
docker exec -i goreos_db psql -U goreos -d postgres -c "
DROP DATABASE goreos_model;
CREATE DATABASE goreos_model;"

# Restaurar dump
docker exec -i goreos_db psql -U goreos -d goreos_model \
    < /tmp/backup_pre_normalizacion_media_1-3.sql

# O desde gzip
gunzip -c backups/goreos_model_pre_normalizacion_media_*.sql.gz | \
    docker exec -i goreos_db psql -U goreos -d goreos_model
```

### Opción 2: Rollback Manual por Fase

**ADVERTENCIA**: Solo usar si se conoce exactamente qué fase falló.

```sql
-- FASE 1: Revertir cargo_ultimo
ALTER TABLE core.person DROP COLUMN IF EXISTS position_id;
DROP TABLE IF EXISTS core.position CASCADE;

-- FASE 2: Revertir calificacion
ALTER TABLE core.person DROP CONSTRAINT IF EXISTS chk_qualification_scheme;
ALTER TABLE core.person DROP COLUMN IF EXISTS qualification_id;
DELETE FROM ref.category WHERE scheme = 'professional_qualification';

-- FASE 3: Revertir estado_cgr_norm
ALTER TABLE core.agreement DROP CONSTRAINT IF EXISTS chk_cgr_outcome_scheme;
ALTER TABLE core.agreement DROP COLUMN IF EXISTS cgr_outcome_id;
DELETE FROM ref.category WHERE scheme = 'cgr_outcome';
```

---

## Impacto en Aplicaciones

### Consultas que Requieren Actualización

#### Antes (usando JSONB):
```sql
-- Buscar personas por cargo
SELECT * FROM core.person
WHERE metadata->>'cargo_ultimo' LIKE '%PROFESIONAL%';

-- Buscar personas por calificación
SELECT * FROM core.person
WHERE metadata->>'calificacion' LIKE '%INGENIERO%';

-- Buscar agreements por estado CGR
SELECT * FROM core.agreement
WHERE metadata->>'estado_cgr_norm' = 'TOMADO_DE_RAZON';
```

#### Después (usando relaciones):
```sql
-- Buscar personas por cargo
SELECT p.* FROM core.person p
JOIN core.position pos ON p.position_id = pos.id
WHERE pos.name LIKE '%PROFESIONAL%';

-- Buscar personas por calificación
SELECT p.* FROM core.person p
JOIN ref.category c ON p.qualification_id = c.id
WHERE c.scheme = 'professional_qualification'
AND (c.code LIKE '%INGENIERO%' OR c.label LIKE '%INGENIERO%');

-- Buscar agreements por estado CGR
SELECT a.* FROM core.agreement a
JOIN ref.category c ON a.cgr_outcome_id = c.id
WHERE c.scheme = 'cgr_outcome' AND c.code = 'TOMADO_DE_RAZON';
```

### Vistas a Crear

```sql
-- Vista simplificada para personas con cargo y calificación
CREATE OR REPLACE VIEW core.v_person_details AS
SELECT
    p.id,
    p.rut,
    p.names,
    p.paternal_surname,
    p.maternal_surname,
    pos.name as cargo,
    pos.code as cargo_code,
    qual.label as calificacion,
    qual.code as calificacion_code,
    org.name as organizacion
FROM core.person p
LEFT JOIN core.position pos ON p.position_id = pos.id
LEFT JOIN ref.category qual ON p.qualification_id = qual.id
LEFT JOIN core.organization org ON p.organization_id = org.id
WHERE p.deleted_at IS NULL;

-- Vista para agreements con estado CGR
CREATE OR REPLACE VIEW core.v_agreement_cgr_status AS
SELECT
    a.id,
    a.agreement_number,
    cgr.code as cgr_outcome_code,
    cgr.label as cgr_outcome_label,
    cgr.metadata->>'severity' as cgr_severity,
    a.signed_at,
    a.total_amount
FROM core.agreement a
LEFT JOIN ref.category cgr ON a.cgr_outcome_id = cgr.id
WHERE a.deleted_at IS NULL;
```

---

## Audit Trail

**IMPORTANTE**: Los campos JSONB originales se **mantienen** en `metadata` para trazabilidad:

- `core.person.metadata->>'cargo_ultimo'` → disponible para auditoría
- `core.person.metadata->>'calificacion'` → disponible para auditoría
- `core.agreement.metadata->>'estado_cgr_norm'` → disponible para auditoría

**Fuente de Verdad**:
- `core.person.position_id` → `core.position`
- `core.person.qualification_id` → `ref.category` (professional_qualification)
- `core.agreement.cgr_outcome_id` → `ref.category` (cgr_outcome)

---

## Próximos Pasos

1. ✅ **Ejecutar script en ambiente de test**
2. ✅ **Verificar Categorical Univocity (schemes = 1)**
3. ✅ **Validar tasas de migración (≥95%)**
4. ⏳ **Actualizar consultas en apps (Streamlit, Flask)**
5. ⏳ **Crear vistas simplificadas para UX**
6. ⏳ **Ejecutar en producción**
7. ⏳ **Actualizar documentación (ERD, Data Dictionary)**
8. ⏳ **Continuar con FASE MEDIA (campos 4-6)** si se requiere

---

## Referencias

- **Auditoría Categorial v3.0**: `docs/AUDITORIA_CATEGORIAL_v3.0.md`
- **Plan Normalización v2.0**: `docs/PLAN_NORMALIZACION_JSONB_v2.0.md`
- **Normalization v2.0 Report**: `etl/migration/NORMALIZACION_v2.0_REPORTE_FINAL.md`
- **Glosario Terminológico**: `docs/glosario_terminologico.md`
- **Category Pattern**: `model/model_goreos/docs/DESIGN_DECISIONS.md`

---

**Autor**: arquitecto-gore
**Ejecutor**: CM-ARTIFACT-GENERATOR
**Fecha**: 2026-01-30
