# Normalización JSONB V3 - Fase MEDIA (Campos 1-3)
## Scripts SQL Generados

**Fecha de Generación**: 2026-01-30
**Agente**: arquitecto-gore (CM-ARTIFACT-GENERATOR)
**Estado**: LISTO PARA EJECUTAR (Verificado)

---

## Archivos Generados

### 1. Script Principal de Migración
**Archivo**: `etl/migration/sql/normalize_jsonb_v3_fase_media_1-3.sql`

**Descripción**: Script SQL completo con 3 fases transaccionales que normaliza campos JSONB de PRIORIDAD MEDIA.

**Características**:
- ✅ Transacciones atómicas por fase (BEGIN/COMMIT por fase)
- ✅ Backups temporales automáticos por fase
- ✅ Verificaciones pre y post-migración
- ✅ Cálculo de tasas de éxito (threshold ≥95%)
- ✅ Manejo de scheme cgr_outcome existente
- ✅ Categorical Univocity validation
- ✅ Audit trail preservation (mantiene JSONB original)
- ✅ Ontological alignment (tde:Cargo, tde:CalificacionProfesional, tde:EstadoCGR)

**Tamaño**: 650+ líneas de SQL/PL-pgSQL

---

### 2. Script de Verificación Pre-Ejecución
**Archivo**: `etl/migration/sql/verify_normalize_jsonb_v3_fase_media_1-3.sql`

**Descripción**: Valida prerrequisitos y analiza datos fuente antes de ejecutar migración.

**Verificaciones incluidas**:
- ✅ Existencia de tablas/schemes conflictivos
- ✅ Análisis de distribución de datos fuente
- ✅ Preview de mapeo calificacion → professional_qualification
- ✅ Verificación de función fn_validate_category_scheme
- ✅ Espacio en disco disponible
- ✅ Integridad referencial actual

**Uso**:
```bash
docker exec -i goreos_db psql -U goreos -d goreos_model \
    < etl/migration/sql/verify_normalize_jsonb_v3_fase_media_1-3.sql
```

**Resultado esperado**: "LISTO PARA EJECUTAR" sin WARNINGS críticos

---

### 3. Guía de Ejecución y Documentación
**Archivo**: `etl/migration/NORMALIZACION_V3_FASE_MEDIA_1-3_GUIA.md`

**Descripción**: Documentación completa con:
- ✅ Resumen ejecutivo de normalizaciones
- ✅ Alineamiento ontológico (Gist 14.0, TDE, GNUB)
- ✅ Estructura detallada del script por fase
- ✅ Procedimientos de ejecución (test + producción)
- ✅ Verificaciones post-ejecución
- ✅ Procedimientos de rollback
- ✅ Impacto en aplicaciones (consultas a actualizar)
- ✅ Scripts de vistas simplificadas

**Tamaño**: 400+ líneas Markdown

---

## Normalizaciones Implementadas

### FASE 1: cargo_ultimo → core.position
| Aspecto | Detalle |
|---------|---------|
| **Campo Fuente** | `core.person.metadata->>'cargo_ultimo'` |
| **Destino** | `core.position` (tabla nueva) + `person.position_id` |
| **Registros** | 110 personas con cargo |
| **Valores Únicos** | 87 cargos únicos |
| **Ontología** | `tde:Cargo` |
| **Tasa Esperada** | 100% |

**Estructura creada**:
- Tabla `core.position` con campos: id, code, name, organization_id, level
- Columna `person.position_id` (FK → core.position)
- 4 índices (org, active, code, metadata)
- Trigger `trg_position_updated_at`

---

### FASE 2: calificacion → professional_qualification
| Aspecto | Detalle |
|---------|---------|
| **Campo Fuente** | `core.person.metadata->>'calificacion'` |
| **Destino** | `ref.category` scheme=`professional_qualification` + `person.qualification_id` |
| **Registros** | 110 personas con calificación |
| **Valores Únicos** | 57 calificaciones únicas → 17 categorías normalizadas |
| **Ontología** | `tde:CalificacionProfesional` |
| **Tasa Esperada** | 95-100% |

**Categorías normalizadas** (17):
- INGENIERO_COMERCIAL, INGENIERO_CIVIL, INGENIERO_INDUSTRIAL, INGENIERO_CONSTRUCTOR
- INGENIERO_OTROS, ARQUITECTO, ABOGADO, CONTADOR
- ADMINISTRADOR_PUBLICO, TRABAJADOR_SOCIAL, PERIODISTA
- PROFESIONAL_SALUD, PROFESIONAL_EDUCACION
- TECNICO, LICENCIA_MEDIA, SECRETARIA, OTROS

**Mapeo inteligente**: Utiliza `CASE WHEN` + `UPPER()` + `LIKE` para clasificación fuzzy automática

**Constraint**: `chk_qualification_scheme` valida Categorical Univocity

---

### FASE 3: estado_cgr_norm → cgr_outcome
| Aspecto | Detalle |
|---------|---------|
| **Campo Fuente** | `core.agreement.metadata->>'estado_cgr_norm'` |
| **Destino** | `ref.category` scheme=`cgr_outcome` + `agreement.cgr_outcome_id` |
| **Registros** | 129 agreements con estado CGR |
| **Valores Únicos** | 4 estados únicos |
| **Ontología** | `tde:EstadoCGR`, `gnub:ResolutionOutcome` |
| **Tasa Esperada** | 100% |

**Categorías** (4 requeridas, scheme pre-existente con 5):
- TOMADO_DE_RAZON (86 agreements) - Aprobado sin observaciones
- TR_CON_ALCANCES (37 agreements) - Aprobado con observaciones
- REPRESENTADO (5 agreements) - Rechazado por CGR
- EN_CGR (1 agreement) - En proceso de revisión

**Nota**: El scheme `cgr_outcome` ya existe en el modelo con 5 categorías (incluye TOMA_RAZON, REPRESENTA, CURSA_OBS, EXENTO, RETIRO). El script agrega las categorías faltantes si no existen.

**Constraint**: `chk_cgr_outcome_scheme` valida Categorical Univocity

---

## Procedimiento de Ejecución

### Paso 1: Backup de Base de Datos
```bash
# Backup comprimido con timestamp
docker exec goreos_db pg_dump -U goreos -d goreos_model | \
    gzip > backups/goreos_model_pre_normalizacion_media_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Paso 2: Verificación Pre-Ejecución
```bash
docker exec -i goreos_db psql -U goreos -d goreos_model \
    < etl/migration/sql/verify_normalize_jsonb_v3_fase_media_1-3.sql
```

**Criterios de aprobación**:
- ✅ core.position NO debe existir
- ✅ scheme professional_qualification NO debe existir
- ⚠️ scheme cgr_outcome PUEDE existir (se completará)
- ✅ Función fn_validate_category_scheme debe existir
- ✅ Sin WARNINGS críticos

### Paso 3: Ejecución en Test (Recomendado)
```bash
# 1. Clonar producción a test
docker exec goreos_db psql -U goreos -d postgres -c "
DROP DATABASE IF EXISTS goreos_model_test;
CREATE DATABASE goreos_model_test;"

docker exec goreos_db bash -c "
pg_dump -U goreos -d goreos_model | psql -U goreos -d goreos_model_test"

# 2. Ejecutar en test
docker exec -i goreos_db psql -U goreos -d goreos_model_test \
    < etl/migration/sql/normalize_jsonb_v3_fase_media_1-3.sql

# 3. Verificar resultados
# Ver sección "Verificaciones Post-Ejecución" en GUIA.md
```

### Paso 4: Ejecución en Producción
```bash
docker exec -i goreos_db psql -U goreos -d goreos_model \
    < etl/migration/sql/normalize_jsonb_v3_fase_media_1-3.sql
```

**Tiempo estimado**: 2-5 minutos (dependiendo de hardware)

### Paso 5: Verificaciones Post-Ejecución

#### 5.1 Categorical Univocity
```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT
    'qualification_id' AS campo,
    COUNT(DISTINCT c.scheme) AS schemes
FROM core.person p
JOIN ref.category c ON c.id = p.qualification_id
UNION ALL
SELECT 'cgr_outcome_id', COUNT(DISTINCT c.scheme)
FROM core.agreement a
JOIN ref.category c ON c.id = a.cgr_outcome_id;
"
```
**Esperado**: schemes = 1 para ambas columnas

#### 5.2 Tasas de Migración
```bash
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT
    'cargo_ultimo → position_id' AS migracion,
    COUNT(*) FILTER (WHERE metadata->>'cargo_ultimo' IS NOT NULL) AS total,
    COUNT(*) FILTER (WHERE position_id IS NOT NULL) AS migrados,
    ROUND(COUNT(*) FILTER (WHERE position_id IS NOT NULL)::NUMERIC /
          NULLIF(COUNT(*) FILTER (WHERE metadata->>'cargo_ultimo' IS NOT NULL), 0) * 100, 2) AS pct
FROM core.person
UNION ALL
SELECT 'calificacion → qualification_id',
       COUNT(*) FILTER (WHERE metadata->>'calificacion' IS NOT NULL),
       COUNT(*) FILTER (WHERE qualification_id IS NOT NULL),
       ROUND(COUNT(*) FILTER (WHERE qualification_id IS NOT NULL)::NUMERIC /
             NULLIF(COUNT(*) FILTER (WHERE metadata->>'calificacion' IS NOT NULL), 0) * 100, 2)
FROM core.person
UNION ALL
SELECT 'estado_cgr_norm → cgr_outcome_id',
       COUNT(*) FILTER (WHERE metadata->>'estado_cgr_norm' IS NOT NULL),
       COUNT(*) FILTER (WHERE cgr_outcome_id IS NOT NULL),
       ROUND(COUNT(*) FILTER (WHERE cgr_outcome_id IS NOT NULL)::NUMERIC /
             NULLIF(COUNT(*) FILTER (WHERE metadata->>'estado_cgr_norm' IS NOT NULL), 0) * 100, 2)
FROM core.agreement;
"
```
**Esperado**: pct ≥ 95% para todas las migraciones

---

## Rollback

### Opción 1: Restaurar Backup Completo (Recomendado)
```bash
# Restaurar desde backup comprimido
gunzip -c backups/goreos_model_pre_normalizacion_media_*.sql.gz | \
    docker exec -i goreos_db psql -U goreos -d goreos_model
```

### Opción 2: Rollback Manual por Fase
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
-- NOTA: NO eliminar scheme cgr_outcome si pre-existía
```

---

## Impacto en Aplicaciones

### Consultas a Actualizar

**Antes (JSONB)**:
```sql
SELECT * FROM core.person WHERE metadata->>'cargo_ultimo' LIKE '%PROFESIONAL%';
SELECT * FROM core.person WHERE metadata->>'calificacion' LIKE '%INGENIERO%';
SELECT * FROM core.agreement WHERE metadata->>'estado_cgr_norm' = 'TOMADO_DE_RAZON';
```

**Después (Relacional)**:
```sql
SELECT p.* FROM core.person p
JOIN core.position pos ON p.position_id = pos.id
WHERE pos.name LIKE '%PROFESIONAL%';

SELECT p.* FROM core.person p
JOIN ref.category c ON p.qualification_id = c.id
WHERE c.scheme = 'professional_qualification'
AND (c.code LIKE '%INGENIERO%' OR c.label LIKE '%INGENIERO%');

SELECT a.* FROM core.agreement a
JOIN ref.category c ON a.cgr_outcome_id = c.id
WHERE c.scheme = 'cgr_outcome' AND c.code = 'TOMADO_DE_RAZON';
```

### Vistas Recomendadas

Ver sección "Vistas a Crear" en `NORMALIZACION_V3_FASE_MEDIA_1-3_GUIA.md`.

---

## Métricas de Éxito

| Métrica | Threshold | Verificación |
|---------|-----------|--------------|
| Categorical Univocity | schemes = 1 | Query en sección 5.1 |
| Tasa migración cargo_ultimo | ≥ 95% | Query en sección 5.2 |
| Tasa migración calificacion | ≥ 95% | Query en sección 5.2 |
| Tasa migración estado_cgr_norm | 100% | Query en sección 5.2 |
| Sin errores FK | 0 violaciones | Review logs de ejecución |
| Sin duplicados natural key | 0 duplicados | Garantizado por UNIQUE constraints |

---

## Estado de Verificación

**Última verificación**: 2026-01-30

### Resultados Pre-Verificación:
✅ **core.position**: NO existe - OK
✅ **scheme professional_qualification**: NO existe - OK
⚠️ **scheme cgr_outcome**: EXISTE (5 categorías) - SE COMPLETARA
✅ **Función fn_validate_category_scheme**: EXISTE - OK
✅ **Espacio en disco**: 98 MB disponible - OK
✅ **Personas con metadata**: 111
✅ **Cargos únicos**: 87
✅ **Calificaciones únicas**: 57 → 17 categorías
✅ **Agreements con estado CGR**: 129
✅ **Estados CGR únicos**: 4

**Estado**: ✅ LISTO PARA EJECUTAR

---

## Próximos Pasos

1. ✅ **Scripts generados y verificados**
2. ⏳ **Crear backup de producción**
3. ⏳ **Ejecutar en ambiente de test**
4. ⏳ **Validar tasas de migración ≥95%**
5. ⏳ **Ejecutar en producción**
6. ⏳ **Actualizar consultas en apps (migration_viewer, flask_app)**
7. ⏳ **Crear vistas simplificadas**
8. ⏳ **Actualizar ERD y Data Dictionary**
9. ⏳ **Continuar con FASE MEDIA (campos 4-6)** si se requiere

---

## Referencias

- **Auditoría Categorial v3.0**: `docs/AUDITORIA_CATEGORIAL_v3.0.md`
- **Guía de Ejecución Detallada**: `etl/migration/NORMALIZACION_V3_FASE_MEDIA_1-3_GUIA.md`
- **Plan Normalización v2.0**: `docs/PLAN_NORMALIZACION_JSONB_v2.0.md`
- **Glosario Terminológico**: `docs/glosario_terminologico.md`
- **Lecciones Aprendidas**: `etl/migration/LECCIONES_APRENDIDAS.md`

---

**Generado por**: arquitecto-gore (CM-ARTIFACT-GENERATOR)
**Fecha**: 2026-01-30
**Versión**: 1.0
