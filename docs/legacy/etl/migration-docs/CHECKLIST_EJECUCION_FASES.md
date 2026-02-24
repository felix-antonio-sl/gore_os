# Checklist de Ejecución por Fase - Normalización JSONB

**Propósito**: Guía paso a paso para ejecutar cada fase de normalización de forma segura y validada.

**Uso**: Copiar la sección de la fase correspondiente y marcar cada paso conforme se complete.

---

## Preparación General (Semana 1)

### Pre-requisitos

- [ ] Plan de normalización revisado y aprobado por equipo
- [ ] Recursos asignados (desarrollador, DBA, QA)
- [ ] Ambiente de prueba configurado con datos de producción
- [ ] Backup completo de base de datos
- [ ] Ventana de mantenimiento programada (si aplica)

### Scripts y herramientas

- [ ] Script de validación ejecutado: `validate_jsonb_normalization.sql`
- [ ] Generador de SQL probado: `generate_migration_sql.py --list-phases`
- [ ] Git branch creada: `feature/normalize-jsonb-phase-X`
- [ ] Issue en GitHub creado para la fase

### Schemes en ref.category

Crear schemes faltantes antes de iniciar migraciones:

- [ ] `event_fund_type` (para FASE 2)
- [ ] `execution_state` (para FASE 2)
- [ ] `employee_category` (para FASE 6)

```sql
-- Ejecutar en ambiente de desarrollo primero
-- Ver sección de cada fase para DDL específico
```

---

## FASE 1: core.budget_commitment

**Tabla**: `core.budget_commitment`
**Registros**: 4,609
**Riesgo**: Bajo
**Tiempo estimado**: 2 horas

### 1. Preparación

- [ ] Revisar estado actual:
  ```bash
  docker exec goreos_db psql -U goreos -d goreos_model \
    -c "SELECT jsonb_object_keys(metadata) as key, COUNT(*) FROM core.budget_commitment GROUP BY key ORDER BY count DESC;"
  ```

- [ ] Generar script SQL:
  ```bash
  python etl/migration/scripts/generate_migration_sql.py --phase 1 --output migration_fase1.sql
  ```

- [ ] Revisar script generado: `migration_fase1.sql`

- [ ] Crear backup manual (adicional al automático):
  ```sql
  CREATE TABLE core.budget_commitment_manual_backup AS
  SELECT * FROM core.budget_commitment;
  ```

### 2. Análisis de datos

- [ ] Verificar valores de `fiscal_year`:
  ```sql
  SELECT metadata->>'fiscal_year' as year, COUNT(*)
  FROM core.budget_commitment
  WHERE metadata->>'fiscal_year' IS NOT NULL
  GROUP BY year ORDER BY year DESC;
  ```

- [ ] Verificar valores de `fondo` (debería estar vacío):
  ```sql
  SELECT metadata->>'fondo', COUNT(*)
  FROM core.budget_commitment
  WHERE metadata->>'fondo' IS NOT NULL
  GROUP BY 1;
  ```

- [ ] Analizar relación `bip` vs `ipr_id`:
  ```sql
  SELECT
    CASE
      WHEN bc.ipr_id IS NULL THEN 'SIN IPR_ID'
      WHEN bc.metadata->>'bip' IS NULL THEN 'SIN BIP EN METADATA'
      WHEN bc.metadata->>'bip' = i.codigo_bip THEN 'COINCIDE'
      ELSE 'DIFIERE'
    END as estado,
    COUNT(*)
  FROM core.budget_commitment bc
  LEFT JOIN core.ipr i ON bc.ipr_id = i.id
  GROUP BY 1;
  ```

### 3. Ejecución en DEV

- [ ] Ejecutar en ambiente de desarrollo:
  ```bash
  docker exec goreos_db psql -U goreos -d goreos_model -f migration_fase1.sql
  ```

- [ ] Revisar resultados de validaciones automáticas

- [ ] Verificar integridad referencial:
  ```sql
  -- No debería retornar resultados
  SELECT * FROM core.budget_commitment
  WHERE fund_id IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM ref.category WHERE id = fund_id);
  ```

- [ ] Ajustar script si es necesario y repetir

### 4. Ejecución en PROD

- [ ] Programar ventana de mantenimiento (si aplica)
- [ ] Notificar a usuarios sobre mantenimiento
- [ ] Crear backup de producción
- [ ] Ejecutar script en producción
- [ ] Validar resultados
- [ ] Hacer COMMIT (cambiar en script de ROLLBACK a COMMIT)

### 5. Post-ejecución

- [ ] Ejecutar validaciones adicionales:
  ```sql
  -- Comparar conteos
  SELECT
    (SELECT COUNT(*) FROM core.budget_commitment_backup_20260130) as antes,
    (SELECT COUNT(*) FROM core.budget_commitment) as despues;

  -- Verificar migración de fiscal_year
  SELECT
    COUNT(*) FILTER (WHERE fiscal_year IS NOT NULL) as migrados,
    COUNT(*) FILTER (WHERE metadata->>'fiscal_year' IS NOT NULL) as en_metadata
  FROM core.budget_commitment;
  ```

- [ ] Actualizar ERD (agregar columnas nuevas)
- [ ] Actualizar loader ETL: `etl/migration/loaders/budget_commitment_loader.py`
- [ ] Ejecutar tests: `pytest tests/test_budget_commitment.py`
- [ ] Documentar en LECCIONES_APRENDIDAS.md
- [ ] Commit y push:
  ```bash
  git add .
  git commit -m "feat(normalize): FASE 1 - core.budget_commitment (fiscal_year, fund_id)"
  git push origin feature/normalize-jsonb-phase-1
  ```
- [ ] Crear PR y solicitar revisión
- [ ] Mergear a master después de aprobación

---

## FASE 2: txn.event

**Tabla**: `txn.event` (particionada)
**Registros**: 4,040
**Riesgo**: Alto
**Tiempo estimado**: 1 día

### 1. Preparación

- [ ] Revisar estado actual de particiones:
  ```sql
  SELECT tablename, pg_size_pretty(pg_total_relation_size('txn.'||tablename))
  FROM pg_tables
  WHERE schemaname = 'txn' AND tablename LIKE 'event_%'
  ORDER BY tablename;
  ```

- [ ] Crear schemes en ref.category:
  ```sql
  -- event_fund_type
  INSERT INTO ref.category (scheme, code, label, description)
  SELECT
    'event_fund_type',
    REPLACE(LOWER(data->>'fondo'), ' ', '_'),
    data->>'fondo',
    'Tipo de fondo (migrado desde txn.event.data)'
  FROM txn.event
  WHERE data->>'fondo' IS NOT NULL
  GROUP BY data->>'fondo'
  ON CONFLICT DO NOTHING;

  -- execution_state
  INSERT INTO ref.category (scheme, code, label)
  VALUES
    ('execution_state', 'COMPLETADO', 'Completado'),
    ('execution_state', 'PENDIENTE', 'Pendiente'),
    ('execution_state', 'EN_PROCESO', 'En proceso'),
    ('execution_state', 'CANCELADO', 'Cancelado')
  ON CONFLICT DO NOTHING;
  ```

- [ ] Generar script SQL:
  ```bash
  python etl/migration/scripts/generate_migration_sql.py --phase 2 --output migration_fase2.sql
  ```

- [ ] Revisar script generado y ajustar para tablas particionadas

### 2. Análisis de datos

- [ ] Verificar redundancia de tipo_evento:
  ```sql
  SELECT
    event_type_id IS NOT NULL as tiene_fk,
    data->>'tipo_evento_id' IS NOT NULL as tiene_en_data,
    COUNT(*)
  FROM txn.event
  GROUP BY 1,2;
  ```

- [ ] Analizar valores de fondo y tipología:
  ```sql
  SELECT
    data->>'fondo' as fondo,
    data->>'tipologia' as tipologia,
    COUNT(*)
  FROM txn.event
  WHERE data->>'fondo' IS NOT NULL OR data->>'tipologia' IS NOT NULL
  GROUP BY 1,2
  ORDER BY 3 DESC
  LIMIT 20;
  ```

- [ ] Verificar montos válidos:
  ```sql
  SELECT
    COUNT(*) as total,
    COUNT(CASE WHEN data->>'monto_transferido' ~ '^[0-9]+\.?[0-9]*$' THEN 1 END) as validos,
    COUNT(CASE WHEN data->>'monto_transferido' !~ '^[0-9]+\.?[0-9]*$' THEN 1 END) as invalidos
  FROM txn.event
  WHERE data->>'monto_transferido' IS NOT NULL;
  ```

### 3. Ejecución en DEV

- [ ] Crear tabla `txn.event_territory`:
  ```sql
  CREATE TABLE IF NOT EXISTS txn.event_territory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL,
    territory_id UUID NOT NULL REFERENCES core.territory(id),
    territory_type VARCHAR(20) NOT NULL CHECK (territory_type IN ('PROVINCIA', 'COMUNA')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (event_id, territory_id, territory_type)
  );
  ```

- [ ] Ejecutar migración por partición (ejemplo para event_2026_01):
  ```sql
  BEGIN;

  -- Agregar columnas a tabla padre (se heredan a particiones)
  ALTER TABLE txn.event
  ADD COLUMN IF NOT EXISTS fund_type_id UUID REFERENCES ref.category(id),
  ADD COLUMN IF NOT EXISTS execution_state_id UUID REFERENCES ref.category(id);

  -- Migrar datos por partición
  UPDATE txn.event_2026_01 e
  SET fund_type_id = c.id
  FROM ref.category c
  WHERE c.scheme = 'event_fund_type' AND c.label = e.data->>'fondo';

  -- Validar
  SELECT COUNT(*) as migrados FROM txn.event_2026_01 WHERE fund_type_id IS NOT NULL;

  COMMIT;
  ```

- [ ] Repetir para todas las particiones activas

### 4. Ejecución en PROD

- [ ] Ejecutar en ventana de mantenimiento
- [ ] Monitorear uso de CPU/memoria durante migración
- [ ] Ejecutar por lotes si es necesario

### 5. Post-ejecución

- [ ] Crear índices en particiones:
  ```sql
  CREATE INDEX idx_event_fund_type ON txn.event(fund_type_id);
  CREATE INDEX idx_event_execution_state ON txn.event(execution_state_id);
  ```

- [ ] Validar integridad en todas las particiones
- [ ] Actualizar documentación
- [ ] Commit y PR

---

## FASE 3: core.ipr

**Tabla**: `core.ipr`
**Registros**: 3,621
**Riesgo**: Medio (tabla crítica)
**Tiempo estimado**: 4 horas

### 1. Preparación

- [ ] Generar script SQL:
  ```bash
  python etl/migration/scripts/generate_migration_sql.py --phase 3 --output migration_fase3.sql
  ```

- [ ] Crear schemes faltantes en ref.category:
  ```sql
  -- Tipologías
  INSERT INTO ref.category (scheme, code, label)
  SELECT
    'ipr_type',
    REPLACE(UPPER(metadata->>'tipologia_original'), ' ', '_'),
    metadata->>'tipologia_original'
  FROM core.ipr
  WHERE metadata->>'tipologia_original' IS NOT NULL
    AND NOT EXISTS (
      SELECT 1 FROM ref.category
      WHERE scheme = 'ipr_type' AND label = metadata->>'tipologia_original'
    )
  GROUP BY metadata->>'tipologia_original';

  -- Etapas
  INSERT INTO ref.category (scheme, code, label)
  VALUES
    ('mcd_phase', 'EJECUCION', 'Ejecución'),
    ('mcd_phase', 'DISENO', 'Diseño'),
    ('mcd_phase', 'PREFACTIBILIDAD', 'Prefactibilidad')
  ON CONFLICT DO NOTHING;
  ```

### 2. Análisis de datos

- [ ] Verificar códigos IDIS únicos:
  ```sql
  SELECT
    COUNT(*) as total,
    COUNT(DISTINCT metadata->>'cod_unico_idis') as unicos
  FROM core.ipr
  WHERE metadata->>'cod_unico_idis' IS NOT NULL;
  ```

- [ ] Analizar `fuente_principal` vs `funding_source_id`:
  ```sql
  SELECT
    metadata->>'fuente_principal' as fuente_metadata,
    c.label as funding_source,
    COUNT(*)
  FROM core.ipr i
  LEFT JOIN ref.category c ON i.funding_source_id = c.id
  GROUP BY 1,2
  ORDER BY 3 DESC;
  ```

### 3. Ejecución

- [ ] Ejecutar migración en DEV
- [ ] Validar que `codigo_idis` sea único
- [ ] Enriquecer `ipr_type_id` y `mcd_phase_id`
- [ ] Ejecutar en PROD
- [ ] Validar integridad

### 4. Post-ejecución

- [ ] Actualizar loader: `etl/migration/loaders/ipr_loader.py`
- [ ] Ejecutar tests
- [ ] Commit y PR

---

## FASE 4: core.organization

**Tabla**: `core.organization`
**Registros**: 3,308
**Riesgo**: Bajo
**Tiempo estimado**: 3 horas

### 1. Preparación

- [ ] Generar script SQL:
  ```bash
  python etl/migration/scripts/generate_migration_sql.py --phase 4 --output migration_fase4.sql
  ```

- [ ] Crear tabla `core.organization_alias`

### 2. Análisis de datos

- [ ] Verificar RUTs únicos y formato:
  ```sql
  SELECT
    COUNT(*) as total,
    COUNT(DISTINCT metadata->>'rut') as unicos,
    COUNT(CASE WHEN metadata->>'rut' ~ '^[0-9]{1,2}\.[0-9]{3}\.[0-9]{3}-[0-9K]$' THEN 1 END) as formato_valido
  FROM core.organization
  WHERE metadata->>'rut' IS NOT NULL;
  ```

- [ ] Analizar aliases:
  ```sql
  SELECT
    COUNT(*) as orgs_con_aliases,
    SUM(jsonb_array_length(metadata->'aliases')) as total_aliases
  FROM core.organization
  WHERE metadata ? 'aliases';
  ```

### 3. Ejecución

- [ ] Ejecutar migración
- [ ] Migrar aliases a tabla relacional:
  ```sql
  INSERT INTO core.organization_alias (organization_id, alias_name, alias_type)
  SELECT
    o.id,
    jsonb_array_elements_text(o.metadata->'aliases'),
    'LEGACY_ALIAS'
  FROM core.organization o
  WHERE o.metadata ? 'aliases';
  ```

### 4. Post-ejecución

- [ ] Validar RUTs únicos
- [ ] Verificar aliases migrados
- [ ] Commit y PR

---

## FASE 5: core.agreement

**Tabla**: `core.agreement`
**Registros**: 533
**Riesgo**: Medio
**Tiempo estimado**: 3 horas

### 1. Preparación

- [ ] Generar script SQL:
  ```bash
  python etl/migration/scripts/generate_migration_sql.py --phase 5 --output migration_fase5.sql
  ```

- [ ] Normalizar referentes técnicos en `core.person` si es necesario

### 2. Análisis de datos

- [ ] Analizar referentes técnicos:
  ```sql
  SELECT
    metadata->>'referente_tecnico' as referente,
    COUNT(*)
  FROM core.agreement
  WHERE metadata->>'referente_tecnico' IS NOT NULL
  GROUP BY 1
  ORDER BY 2 DESC;
  ```

- [ ] Verificar estados CGR:
  ```sql
  SELECT
    metadata->>'estado_cgr_raw',
    metadata->>'estado_cgr_norm',
    COUNT(*)
  FROM core.agreement
  WHERE metadata->>'estado_cgr_raw' IS NOT NULL
  GROUP BY 1,2;
  ```

### 3. Ejecución

- [ ] Ejecutar migración
- [ ] Mapear referentes técnicos a `core.person`
- [ ] Enriquecer `state_id` con estados de metadata

### 4. Post-ejecución

- [ ] Validar FKs a `core.person`
- [ ] Commit y PR

---

## FASE 6: core.person

**Tabla**: `core.person`
**Registros**: 111
**Riesgo**: Bajo
**Tiempo estimado**: 2 horas

### 1. Preparación

- [ ] Generar script SQL:
  ```bash
  python etl/migration/scripts/generate_migration_sql.py --phase 6 --output migration_fase6.sql
  ```

- [ ] Crear scheme `employee_category`:
  ```sql
  INSERT INTO ref.category (scheme, code, label, sort_order)
  VALUES
    ('employee_category', 'PROFESIONAL', 'Profesional', 1),
    ('employee_category', 'DIRECTIVO', 'Directivo', 2),
    ('employee_category', 'TECNICO', 'Técnico', 3),
    ('employee_category', 'ADMINISTRATIVO', 'Administrativo', 4),
    ('employee_category', 'AUXILIAR', 'Auxiliar', 5),
    ('employee_category', 'HONORARIOS', 'Honorarios', 6),
    ('employee_category', 'AUTORIDAD', 'Autoridad de Gobierno', 7)
  ON CONFLICT DO NOTHING;
  ```

- [ ] Crear tabla `core.person_qualification`

### 2. Análisis de datos

- [ ] Analizar estamentos:
  ```sql
  SELECT metadata->>'estamento', COUNT(*)
  FROM core.person
  WHERE metadata->>'estamento' IS NOT NULL
  GROUP BY 1;
  ```

- [ ] Analizar calificaciones únicas:
  ```sql
  SELECT COUNT(DISTINCT metadata->>'calificacion')
  FROM core.person
  WHERE metadata->>'calificacion' IS NOT NULL;
  ```

### 3. Ejecución

- [ ] Ejecutar migración
- [ ] Migrar calificaciones a tabla relacional:
  ```sql
  INSERT INTO core.person_qualification (person_id, qualification_name, is_primary)
  SELECT id, metadata->>'calificacion', true
  FROM core.person
  WHERE metadata->>'calificacion' IS NOT NULL;
  ```

### 4. Post-ejecución

- [ ] Validar calificaciones migradas
- [ ] Commit y PR

---

## Validación Final (Semana 7)

### Integridad referencial

- [ ] Ejecutar validación de FKs huérfanas:
  ```sql
  -- Ver sección 9 de validate_jsonb_normalization.sql
  ```

### Completitud de migración

- [ ] Verificar que metadata solo contenga campos de auditoría:
  ```sql
  SELECT
    'core.ipr' as tabla,
    jsonb_object_keys(metadata) as key,
    COUNT(*)
  FROM core.ipr
  WHERE jsonb_object_keys(metadata) NOT IN ('source', 'legacy_id', 'codigo_normalizado')
  GROUP BY 1,2
  HAVING COUNT(*) > 0;
  ```

### Performance

- [ ] Ejecutar benchmark de queries críticas
- [ ] Comparar tiempos pre/post normalización
- [ ] Ajustar índices si es necesario

### Documentación

- [ ] Actualizar ERD completo (v3.2)
- [ ] Actualizar GOREOS_ERD_v3.md
- [ ] Documentar nuevos schemes en ref.category
- [ ] Actualizar LECCIONES_APRENDIDAS.md
- [ ] Crear guía de consultas optimizadas

### Limpieza

- [ ] Eliminar tablas de backup antiguas (después de 30 días)
- [ ] Consolidar branches de Git
- [ ] Cerrar issues de GitHub

---

## Rollback

Si algo sale mal durante cualquier fase:

### Rollback inmediato (dentro de transacción)

```sql
ROLLBACK;
```

### Rollback después de COMMIT

```sql
-- Restaurar desde backup
DROP TABLE core.TABLA_NAME;
ALTER TABLE core.TABLA_NAME_backup_YYYYMMDD RENAME TO TABLA_NAME;

-- Recrear índices y constraints
-- (ver DDL original)
```

### Notificación

- [ ] Notificar al equipo sobre rollback
- [ ] Documentar causa del problema
- [ ] Crear post-mortem
- [ ] Ajustar plan y repetir

---

**Nota**: Este checklist es una guía. Ajustar según necesidades específicas de cada fase.
