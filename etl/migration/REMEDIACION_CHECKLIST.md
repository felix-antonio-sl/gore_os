# Checklist de Remediación Categorial - Normalización JSONB v2.0

**ARQUITECTO-GORE v0.1.0** | Motor: CM-AUDIT-ENGINE
**Fecha**: 2026-01-30
**Plan**: PLAN_NORMALIZACION_JSONB_v2.0.md
**Script**: normalize_ipr_metadata_v2.sql

---

## Objetivo

Garantizar **92% de coherencia ontológica** mediante verificaciones categóricas en cada fase de la normalización.

---

## Pre-Ejecución: Validaciones de Seguridad

### 1. Backup y Entorno

- [ ] **Backup PITR completo** ejecutado
  ```bash
  # Verificar último backup
  pg_basebackup -h localhost -p 5433 -U goreos -D /backups/goreos_$(date +%Y%m%d_%H%M%S)
  ```

- [ ] **WAL archiving** habilitado para rollback point-in-time
  ```sql
  SHOW archive_mode;  -- Expected: on
  SHOW wal_level;     -- Expected: replica
  ```

- [ ] **Ambiente de testing** validado (NO ejecutar en producción sin testing previo)
  ```bash
  # Verificar ambiente
  docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT current_database();"
  # Expected: goreos_model_dev (o ambiente de testing)
  ```

- [ ] **Ventana de mantenimiento** programada (20-30 minutos estimados)

### 2. Validaciones de Coherencia Pre-Migración

- [ ] **Función de validación categorial** existe
  ```sql
  SELECT proname FROM pg_proc WHERE proname = 'fn_validate_category_scheme';
  -- Expected: 1 row
  ```

- [ ] **Schemes existentes** coherentes (baseline)
  ```sql
  -- Verificar que schemes críticos existen
  SELECT scheme, COUNT(*)
  FROM ref.category
  WHERE scheme IN ('ipr_type', 'mcd_phase', 'ipr_state', 'mechanism', 'funding_source', 'ipr_party_role', 'org_type')
  GROUP BY scheme
  ORDER BY scheme;
  -- Expected: 7 rows con counts > 0
  ```

- [ ] **Índice GIN en metadata** existe o se creará
  ```sql
  SELECT indexname FROM pg_indexes WHERE tablename = 'ipr' AND indexname = 'idx_ipr_metadata_gin';
  -- If 0 rows: se creará automáticamente en script
  ```

- [ ] **Datos baseline** documentados
  ```sql
  -- Guardar para comparación post-migración
  SELECT
      COUNT(*) AS total_iprs,
      COUNT(*) FILTER (WHERE metadata IS NOT NULL) AS with_metadata,
      AVG(pg_column_size(metadata))::int AS avg_metadata_size_bytes,
      COUNT(DISTINCT jsonb_object_keys(metadata)) AS unique_keys
  FROM core.ipr;
  ```

---

## Fase 1: Limpieza de Metadata Ya Normalizado

### Verificaciones Pre-Fase

- [ ] **Territorial coverage** validado
  ```sql
  -- Debe retornar 0 (todos normalizados)
  SELECT COUNT(*) FROM core.ipr i
  WHERE i.metadata ? 'provincia'
    AND NOT EXISTS (SELECT 1 FROM core.ipr_territory it WHERE it.ipr_id = i.id);
  -- Expected: 0
  ```

- [ ] **MCD Phase coverage** validado
  ```sql
  -- Debe retornar 0 (todos normalizados)
  SELECT COUNT(*) FROM core.ipr
  WHERE metadata ? 'etapa_original' AND mcd_phase_id IS NULL;
  -- Expected: 0
  ```

### Post-Fase 1 Checks

- [ ] **Metadata limpiado** correctamente
  ```sql
  SELECT COUNT(*) FROM core.ipr WHERE metadata ?| ARRAY['provincia', 'comuna', 'etapa_original'];
  -- Expected: 0
  ```

- [ ] **Timestamp de normalización** añadido
  ```sql
  SELECT COUNT(*) FROM core.ipr WHERE metadata->>'normalized_version' = 'v2.0';
  -- Expected: > 0 (registros actualizados)
  ```

- [ ] **No se perdió información** (verificar contra backup)
  ```sql
  -- Comparar counts pre/post
  SELECT COUNT(*) FROM core.ipr;
  -- Expected: mismo count que pre-migración
  ```

**Criterio de éxito Fase 1**: ✅ 0 registros con campos removidos, 100% con timestamp

---

## Fase 2: Completar Migración unidad_tecnica

### Verificaciones Pre-Fase

- [ ] **Organizaciones a crear** identificadas (11 esperadas)
  ```sql
  -- Listar organizaciones que NO existen
  SELECT DISTINCT metadata->>'unidad_tecnica' AS unidad_faltante
  FROM core.ipr
  WHERE metadata ? 'unidad_tecnica'
    AND NOT EXISTS (
        SELECT 1 FROM core.organization o
        WHERE o.short_name = core.ipr.metadata->>'unidad_tecnica'
    );
  -- Expected: hasta 11 organizaciones
  ```

- [ ] **Scheme ipr_party_role** tiene código UNIDAD_TECNICA
  ```sql
  SELECT id FROM ref.category WHERE scheme='ipr_party_role' AND code='UNIDAD_TECNICA';
  -- Expected: 1 row
  ```

- [ ] **Scheme org_type** tiene códigos necesarios
  ```sql
  SELECT code FROM ref.category WHERE scheme='org_type'
    AND code IN ('SERVICIO_PUBLICO', 'ASOCIACION', 'INSTITUCION_EDUCACION', 'SEREMI', 'UNIVERSIDAD');
  -- Expected: 5 rows
  ```

### Post-Fase 2 Checks

- [ ] **Organizaciones creadas** exitosamente
  ```sql
  SELECT COUNT(*) FROM core.organization WHERE metadata->>'normalized_version' = 'v2.0';
  -- Expected: 11 (o menos si ya existían)
  ```

- [ ] **ipr_party records** creados
  ```sql
  SELECT COUNT(*) FROM core.ipr_party WHERE metadata->>'normalized_version' = 'v2.0';
  -- Expected: ~15 registros faltantes
  ```

- [ ] **Completitud 100%** alcanzada
  ```sql
  SELECT COUNT(*) FROM core.ipr i
  WHERE i.metadata ? 'unidad_tecnica'
    AND NOT EXISTS (
        SELECT 1 FROM core.ipr_party ip
        WHERE ip.ipr_id = i.id
          AND ip.party_role_id = (SELECT id FROM ref.category WHERE code='UNIDAD_TECNICA')
    );
  -- Expected: 0 (todos migrados)
  ```

- [ ] **Metadata campo removido**
  ```sql
  SELECT COUNT(*) FROM core.ipr WHERE metadata ? 'unidad_tecnica';
  -- Expected: 0
  ```

**Criterio de éxito Fase 2**: ✅ 0 IPRs sin unidad_tecnica normalizada, 11 orgs creadas

---

## Fase 3: Crear Scheme investment_sector

### Verificaciones Pre-Fase

- [ ] **Coherencia ontológica** validada
  ```sql
  -- Verificar que gnub:InvestmentTypology existe en glosario
  -- (verificación manual en glosario_terminologico.md línea 1693-1700)
  ```

- [ ] **Naming convention** coherente (inglés para codes)
  ```sql
  -- Script usa codes en inglés (SPORTS, CULTURE, EDUCATION...)
  -- Coherente con DDL estándar (funding_source, mcd_phase)
  ```

- [ ] **Tipologías legacy** analizadas (30 códigos → 10 sectoriales)
  ```sql
  -- Verificar distribución de tipologías legacy
  SELECT
      metadata->>'tipologia_original' AS legacy_type,
      COUNT(*) AS iprs
  FROM core.ipr
  WHERE metadata ? 'tipologia_original'
  GROUP BY metadata->>'tipologia_original'
  ORDER BY COUNT(*) DESC;
  ```

### Post-Fase 3 Checks

- [ ] **Scheme creado** con 10 códigos
  ```sql
  SELECT COUNT(*) FROM ref.category WHERE scheme = 'investment_sector';
  -- Expected: 10
  ```

- [ ] **Columna añadida** a core.ipr
  ```sql
  SELECT column_name FROM information_schema.columns
  WHERE table_schema = 'core' AND table_name = 'ipr' AND column_name = 'investment_sector_id';
  -- Expected: 1 row
  ```

- [ ] **COMMENT añadido** a columna
  ```sql
  SELECT col_description('core.ipr'::regclass, (
      SELECT ordinal_position FROM information_schema.columns
      WHERE table_schema='core' AND table_name='ipr' AND column_name='investment_sector_id'
  ));
  -- Expected: texto que mencione "gnub:InvestmentTypology"
  ```

- [ ] **Migración de datos** ejecutada
  ```sql
  SELECT COUNT(*) FROM core.ipr WHERE investment_sector_id IS NOT NULL;
  -- Expected: ~300-500 (10-15% de IPRs con tipologías sectoriales)
  ```

- [ ] **Distribución sectorial** coherente
  ```sql
  SELECT
      c.label AS sector,
      COUNT(*) AS iprs,
      ROUND(COUNT(*)::numeric / NULLIF((SELECT COUNT(*) FROM core.ipr WHERE investment_sector_id IS NOT NULL), 0) * 100, 1) AS pct
  FROM core.ipr i
  JOIN ref.category c ON i.investment_sector_id = c.id
  WHERE c.scheme = 'investment_sector'
  GROUP BY c.label
  ORDER BY COUNT(*) DESC;
  -- Verificar que distribución es razonable (no un solo sector con 100%)
  ```

- [ ] **tipologia_original** MANTENIDA en metadata (no removida)
  ```sql
  SELECT COUNT(*) FROM core.ipr WHERE metadata ? 'tipologia_original';
  -- Expected: mismo count que pre-migración (NO se remueve, es auditoría)
  ```

- [ ] **Metadata marcada** con extracción sectorial
  ```sql
  SELECT COUNT(*) FROM core.ipr
  WHERE metadata->>'tipologia_legacy_sector_extracted' = 'true';
  -- Expected: ~300-500 (IPRs con sector extraído)
  ```

**Criterio de éxito Fase 3**: ✅ 10 códigos creados, 300-500 IPRs con sector poblado, tipologia_original mantenida

---

## Fase 4: CHECK Constraints de Coherencia Categorial

### Verificaciones Pre-Fase

- [ ] **Datos existentes** coherentes (antes de añadir constraints)
  ```sql
  -- Detectar incoherencias antes de constraint (deben ser 0)
  SELECT codigo_bip, 'ipr_type' AS field
  FROM core.ipr
  WHERE ipr_type_id IS NOT NULL
    AND NOT fn_validate_category_scheme(ipr_type_id, 'ipr_type')
  UNION ALL
  SELECT codigo_bip, 'mechanism'
  FROM core.ipr
  WHERE mechanism_id IS NOT NULL
    AND NOT fn_validate_category_scheme(mechanism_id, 'mechanism');
  -- Expected: 0 rows (si hay rows, corregir datos antes de constraint)
  ```

### Post-Fase 4 Checks

- [ ] **7 CHECK constraints** creados
  ```sql
  SELECT COUNT(*) FROM pg_constraint
  WHERE conrelid = 'core.ipr'::regclass
    AND contype = 'c'
    AND conname LIKE 'chk_%_scheme';
  -- Expected: 7
  ```

- [ ] **Nombres de constraints** correctos
  ```sql
  SELECT conname FROM pg_constraint
  WHERE conrelid = 'core.ipr'::regclass
    AND contype = 'c'
    AND conname LIKE 'chk_%_scheme'
  ORDER BY conname;
  -- Expected: chk_budget_subtitle_scheme, chk_funding_source_scheme,
  --           chk_investment_sector_scheme, chk_ipr_type_scheme,
  --           chk_mcd_phase_scheme, chk_mechanism_scheme, chk_status_scheme
  ```

- [ ] **Constraints funcionan** (test de violación)
  ```sql
  -- Este INSERT debe FALLAR con constraint violation
  BEGIN;
  INSERT INTO core.ipr (codigo_bip, name, ipr_nature, ipr_type_id)
  VALUES ('TEST-CONSTRAINT', 'Test', 'PROYECTO', (SELECT id FROM ref.category WHERE scheme='org_type' LIMIT 1));
  -- Expected: ERROR constraint violation chk_ipr_type_scheme
  ROLLBACK;
  ```

**Criterio de éxito Fase 4**: ✅ 7 constraints activos, test de violación falla correctamente

---

## Fase 5: Optimizaciones de Performance

### Post-Fase 5 Checks

- [ ] **Índice GIN** creado en metadata
  ```sql
  SELECT indexname FROM pg_indexes WHERE tablename = 'ipr' AND indexname = 'idx_ipr_metadata_gin';
  -- Expected: 1 row
  ```

- [ ] **Índice partial** creado en investment_sector_id
  ```sql
  SELECT indexname, indexdef FROM pg_indexes
  WHERE tablename = 'ipr' AND indexname = 'idx_ipr_investment_sector';
  -- Expected: 1 row con "WHERE investment_sector_id IS NOT NULL"
  ```

- [ ] **ANALYZE** ejecutado
  ```sql
  SELECT last_analyze FROM pg_stat_user_tables WHERE relname = 'ipr';
  -- Expected: timestamp reciente (< 5 minutos)
  ```

**Criterio de éxito Fase 5**: ✅ 2 índices creados, estadísticas actualizadas

---

## Post-Ejecución: Verificaciones Finales

### 1. Coherencia Categorial (CRÍTICO)

- [ ] **100% coherencia** en todas las FKs de category
  ```sql
  -- Debe retornar 0 rows (ninguna incoherencia)
  SELECT codigo_bip, field, category_id, scheme_esperado, scheme_real
  FROM (
      SELECT i.codigo_bip, 'ipr_type' AS field, i.ipr_type_id AS category_id,
             'ipr_type' AS scheme_esperado, c.scheme AS scheme_real
      FROM core.ipr i
      LEFT JOIN ref.category c ON i.ipr_type_id = c.id
      WHERE i.ipr_type_id IS NOT NULL AND c.scheme != 'ipr_type'

      UNION ALL

      SELECT i.codigo_bip, 'investment_sector', i.investment_sector_id,
             'investment_sector', c.scheme
      FROM core.ipr i
      LEFT JOIN ref.category c ON i.investment_sector_id = c.id
      WHERE i.investment_sector_id IS NOT NULL AND c.scheme != 'investment_sector'

      -- Añadir más UNIONs para otros campos...
  ) incoherences;
  -- Expected: 0 rows
  ```

### 2. Integridad Referencial

- [ ] **Todas las FKs** válidas
  ```sql
  -- Verificar que no hay FKs huérfanas
  SELECT COUNT(*) FROM core.ipr i
  WHERE investment_sector_id IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM ref.category WHERE id = i.investment_sector_id);
  -- Expected: 0
  ```

### 3. Completitud de Migración

- [ ] **Metadata limpiado** (4 campos removidos)
  ```sql
  SELECT COUNT(*) FROM core.ipr
  WHERE metadata ?| ARRAY['provincia', 'comuna', 'etapa_original', 'unidad_tecnica'];
  -- Expected: 0
  ```

- [ ] **unidad_tecnica 100%** migrada
  ```sql
  SELECT COUNT(*) FROM temp_ipr_metadata_backup_v2 b
  WHERE b.metadata ? 'unidad_tecnica'
    AND NOT EXISTS (
        SELECT 1 FROM core.ipr_party ip
        WHERE ip.ipr_id = b.id
          AND ip.party_role_id = (SELECT id FROM ref.category WHERE code='UNIDAD_TECNICA')
    );
  -- Expected: 0
  ```

- [ ] **investment_sector** poblado
  ```sql
  SELECT
      COUNT(*) FILTER (WHERE investment_sector_id IS NOT NULL) AS with_sector,
      COUNT(*) AS total,
      ROUND(COUNT(*) FILTER (WHERE investment_sector_id IS NOT NULL)::numeric / COUNT(*) * 100, 1) AS percentage
  FROM core.ipr;
  -- Expected: 10-15% con sector
  ```

### 4. Reducción de Complejidad

- [ ] **Tamaño metadata reducido** (~15-20%)
  ```sql
  -- Comparar con baseline pre-migración
  SELECT
      AVG(pg_column_size(metadata))::int AS avg_size_after,
      (SELECT AVG(pg_column_size(metadata))::int FROM temp_ipr_metadata_backup_v2) AS avg_size_before,
      ROUND((1 - AVG(pg_column_size(metadata)) / (SELECT AVG(pg_column_size(metadata)) FROM temp_ipr_metadata_backup_v2)) * 100, 1) AS reduction_pct
  FROM core.ipr
  WHERE metadata IS NOT NULL;
  -- Expected: reduction_pct entre 15-25%
  ```

- [ ] **Keys en metadata reducidos** (15 → 9)
  ```sql
  SELECT
      COUNT(DISTINCT jsonb_object_keys(metadata)) AS unique_keys_after,
      (SELECT COUNT(DISTINCT jsonb_object_keys(metadata)) FROM temp_ipr_metadata_backup_v2) AS unique_keys_before
  FROM core.ipr;
  -- Expected: ~9 keys después (vs ~15 antes)
  ```

### 5. Performance de Queries

- [ ] **Query sectorial** más rápido que JSONB
  ```sql
  -- Comparar plan de ejecución
  EXPLAIN ANALYZE
  SELECT COUNT(*) FROM core.ipr i
  JOIN ref.category c ON i.investment_sector_id = c.id
  WHERE c.code IN ('SPORTS', 'CULTURE', 'EDUCATION');
  -- Expected: Index Scan en idx_ipr_investment_sector + B-tree en category
  --           (más rápido que GIN scan en metadata)
  ```

---

## Métricas de Coherencia (Target v2.0)

### Checklist de Métricas Objetivo

- [ ] **Coherencia ontológica ≥ 90%**
  ```
  Elementos con fundamento gnub:* o tde:* / Total elementos
  - investment_sector → gnub:InvestmentTypology ✓
  - CHECK constraints → coherencia categorial ✓
  - Limpieza metadata → no viola ontologías ✓
  - unidad_tecnica → gnub:hasParticipant ✓

  Score esperado: ~92%
  ```

- [ ] **Redundancia ≤ 10%**
  ```
  Campos derivables / Total campos normalizados
  - investment_sector NO es derivable ✓
  - unidad_tecnica migrada a junction table ✓
  - Campos removidos YA normalizados ✓

  Score esperado: ~8%
  ```

- [ ] **Univocidad categorial = 100%**
  ```
  Schemes con 1 dimensión / Total schemes
  - investment_sector = 1 dimensión (sectores) ✓
  - NO mezcla mechanisms, funding sources, etc. ✓

  Score esperado: 100%
  ```

- [ ] **Alineamiento TDE ≥ 85%**
  ```
  Elementos alineados con tde:* o gnub:* / Total
  - investment_sector → gnub:InvestmentTypology ✓
  - Naming convention en inglés (estándar DDL) ✓

  Score esperado: ~88%
  ```

---

## Validación de Aplicaciones

### Breaking Changes Check

- [ ] **migration_viewer** funciona sin cambios
  ```bash
  cd apps/migration_viewer
  streamlit run app.py
  # Verificar que vistas de IPR funcionan correctamente
  ```

- [ ] **Queries legacy** NO rotos
  ```sql
  -- Verificar queries que usan metadata existente
  SELECT * FROM core.ipr WHERE metadata->>'source' = 'IDIS';
  -- Expected: funciona igual (source NO fue removido)
  ```

- [ ] **Nuevas vistas** funcionan
  ```sql
  -- Vista derivada de origen (alternativa a origin_id rechazado)
  CREATE OR REPLACE VIEW core.v_ipr_origin AS
  SELECT i.id, i.codigo_bip,
      CASE WHEN ot.code = 'MUNICIPALIDAD' THEN 'MUNICIPAL' ELSE 'SECTORIAL' END AS origin
  FROM core.ipr i
  LEFT JOIN core.organization o ON i.formulator_id = o.id
  LEFT JOIN ref.category ot ON o.org_type_id = ot.id;

  SELECT COUNT(*) FROM core.v_ipr_origin;
  -- Expected: count igual a total IPRs
  ```

### ETL Loaders Check

- [ ] **ipr_loader.py** actualizado (si es necesario)
  ```python
  # Verificar que loader popula investment_sector_id
  # si viene en metadata de fuente
  ```

---

## Rollback Plan (Si es necesario)

### Condiciones para Rollback

Ejecutar rollback SI:
- ❌ Coherencia categorial < 90%
- ❌ Pérdida de datos detectada (counts no coinciden)
- ❌ Queries de aplicación rotos
- ❌ Constraints impiden operación normal

### Checklist de Rollback

- [ ] **PITR recovery point** identificado
  ```sql
  SELECT pg_current_wal_lsn();
  -- Anotar LSN pre-migración para recovery
  ```

- [ ] **Restaurar desde backup** (si rollback completo necesario)
  ```bash
  pg_restore -h localhost -p 5433 -U goreos -d goreos_model /backups/goreos_pre_normalization.dump
  ```

- [ ] **Restaurar metadata desde temp table** (rollback parcial)
  ```sql
  BEGIN;

  UPDATE core.ipr i
  SET metadata = b.metadata
  FROM temp_ipr_metadata_backup_v2 b
  WHERE i.id = b.id;

  ALTER TABLE core.ipr DROP COLUMN IF EXISTS investment_sector_id;

  DELETE FROM ref.category WHERE scheme = 'investment_sector';

  -- Remover CHECK constraints
  ALTER TABLE core.ipr
      DROP CONSTRAINT IF EXISTS chk_investment_sector_scheme,
      DROP CONSTRAINT IF EXISTS chk_ipr_type_scheme,
      -- ... resto de constraints

  COMMIT;
  ```

- [ ] **Verificar estado post-rollback**
  ```sql
  SELECT COUNT(*) FROM core.ipr;
  -- Expected: mismo count que pre-migración

  SELECT AVG(pg_column_size(metadata))::int FROM core.ipr;
  -- Expected: similar a baseline
  ```

---

## Sign-Off Final

### Criterios de Aprobación

✅ **APROBADO PARA PRODUCCIÓN** si TODOS los siguientes son TRUE:

- [ ] Coherencia ontológica ≥ 90%
- [ ] Redundancia ≤ 10%
- [ ] Univocidad categorial = 100%
- [ ] 0 violaciones de coherencia categorial
- [ ] 0 pérdida de datos (todos los counts coinciden)
- [ ] Queries de aplicación funcionan sin cambios
- [ ] Performance igual o mejor que pre-migración
- [ ] Backup PITR válido disponible
- [ ] Plan de rollback probado y documentado

### Firma de Aprobación

```
Ejecutado por: ____________________
Fecha: ____________________________
Ambiente: _________________________
Resultado: [ ] APROBADO  [ ] RECHAZADO  [ ] ROLLBACK EJECUTADO

Coherencia Alcanzada: _____ %
Issues Detectados: _________________
Acciones Correctivas: ______________

Firma ARQUITECTO-GORE: _____________
```

---

**Versión**: 2.0
**Fecha**: 2026-01-30
**Motor**: CM-AUDIT-ENGINE
**Estado**: Listo para ejecución post-testing
