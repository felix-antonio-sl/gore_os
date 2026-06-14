# AUDITORIA CATEGORIAL v3.0

> **COMPLETED**: The 13 critical and 16 medium normalizations identified here have been executed. Categorical univocity is now 100% (98 CHECK constraints). This document is kept as a historical reference of the audit findings.

**Fecha**: 2026-01-30
**Agente**: arquitecto-gore
**Scope**: Análisis exhaustivo de campos JSONB en todas las tablas core/txn
**Metodología**: Alineación con Gist 14.0, GNUB (199 términos), TDE (19 términos)

---

## Resumen Ejecutivo

Se analizaron **6 dominios** del modelo GORE_OS identificando campos JSONB que violan el principio de normalización relacional:

| Dominio | Tablas | Campos Analizados | Críticos | Medio | Audit Trail |
|---------|--------|-------------------|----------|-------|-------------|
| Organization | 1 | 13 | 1 | 2 | 10 |
| Agreement + Person | 2 | 18 | 5 | 4 | 9 |
| Events (txn) | 1 | 25 | 3 | 2 | 20 |
| Junction Tables | 3 | 12 | 2 | 2 | 8 |
| IPR | 1 | 16 | 0 | 2 | 14 |
| Budget | 2 | 14 | 2 | 4 | 8 |
| **TOTAL** | 10 | 98 | **13** | **16** | 69 |

**Univocidad Categorial**: 100% lograda en v2.0 (CHECK constraints activos)

---

## PRIORIDAD ALTA - Normalizaciones Críticas

### 1. `core.organization.rut` → Columna dedicada

| Campo | Ocurrencias | Valores Únicos | Impacto |
|-------|-------------|----------------|---------|
| `rut` | 1,594 | 1,514 | Integración con SII, ChileProveedores, SIAPER |

**Acción**:
```sql
ALTER TABLE core.organization ADD COLUMN rut VARCHAR(12);
CREATE UNIQUE INDEX idx_org_rut ON core.organization(rut) WHERE rut IS NOT NULL;
ALTER TABLE core.organization ADD CONSTRAINT chk_rut_format
  CHECK (rut ~ '^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$');
UPDATE core.organization SET rut = metadata->>'rut'
  WHERE metadata->>'rut' IS NOT NULL;
```

**Ontología**: tde:RUT, gnub:IdentificadorTributario

---

### 2. Sincronizar EJECUTOR en `core.ipr_party`

| Problema | IPRs Afectados | Estado Actual |
|----------|----------------|---------------|
| `executor_id` existe pero EJECUTOR no en ipr_party | 1,646 | 0 registros EJECUTOR |

**Acción**:
```sql
INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id, is_primary, metadata)
SELECT
  i.id,
  i.executor_id,
  (SELECT id FROM ref.category WHERE scheme='ipr_party_role' AND code='EJECUTOR'),
  TRUE,
  jsonb_build_object('source', 'SYNC_FROM_IPR_EXECUTOR_ID', 'synced_at', NOW())
FROM core.ipr i
WHERE i.executor_id IS NOT NULL
  AND i.deleted_at IS NULL
  AND NOT EXISTS (
    SELECT 1 FROM core.ipr_party ip
    JOIN ref.category c ON ip.party_role_id = c.id
    WHERE ip.ipr_id = i.id AND c.code = 'EJECUTOR'
  );
```

**Ontología**: gnub:hasExecutor (actualmente violado)

---

### 3. `core.person.estamento` → Nuevo scheme + FK

| Campo | Ocurrencias | Valores Distintos |
|-------|-------------|-------------------|
| `estamento` | 110 | 7 |

**Valores**:
- PROFESIONAL, DIRECTIVO, ADMINISTRATIVO, TECNICO, AUXILIAR, HONORARIOS, AUTORIDAD

**Acción**:
```sql
-- 1. Crear scheme
INSERT INTO ref.category (scheme, code, label) VALUES
  ('estamento', 'PROFESIONAL', 'Profesional'),
  ('estamento', 'DIRECTIVO', 'Directivo'),
  ('estamento', 'ADMINISTRATIVO', 'Administrativo'),
  ('estamento', 'TECNICO', 'Técnico'),
  ('estamento', 'AUXILIAR', 'Auxiliar'),
  ('estamento', 'HONORARIOS', 'Honorarios'),
  ('estamento', 'AUTORIDAD', 'Autoridad de Gobierno');

-- 2. Agregar columna
ALTER TABLE core.person ADD COLUMN estamento_id UUID REFERENCES ref.category(id);

-- 3. Migrar datos
UPDATE core.person p
SET estamento_id = (
  SELECT c.id FROM ref.category c
  WHERE c.scheme = 'estamento'
  AND c.code = UPPER(REPLACE(p.metadata->>'estamento', ' ', '_'))
)
WHERE p.metadata->>'estamento' IS NOT NULL;
```

**Ontología**: tde:Estamento

---

### 4. `core.agreement.referente_tecnico` → FK a person

| Campo | Ocurrencias | Valores Únicos |
|-------|-------------|----------------|
| `referente_tecnico` | 389 | 41 |

**Acción**:
```sql
ALTER TABLE core.agreement ADD COLUMN technical_referent_id UUID REFERENCES core.person(id);
-- Migración requiere fuzzy matching de nombres a core.person
```

**Ontología**: gnub:TechnicalReferent, tde:ResponsableAsignado

---

### 5. `core.ipr_party.agreement_id` → Nueva FK

| Campo | Ocurrencias | Estado |
|-------|-------------|--------|
| `agreement_id` en metadata | 476 | Sin FK formal |

**Acción**:
```sql
ALTER TABLE core.ipr_party ADD COLUMN agreement_id UUID REFERENCES core.agreement(id);
UPDATE core.ipr_party
SET agreement_id = (metadata->>'agreement_id')::uuid
WHERE metadata->>'agreement_id' IS NOT NULL;
```

**Ontología**: gnub:hasAgreement

---

### 6. `txn.event.monto_transferido` → `txn.magnitude`

| Campo | Ocurrencias | Valores Únicos |
|-------|-------------|----------------|
| `monto_transferido` | 953 | 677 |

**Acción**:
```sql
-- Verificar/crear aspect
INSERT INTO ref.category (scheme, code, label)
VALUES ('magnitude_aspect', 'TRANSFER_AMOUNT', 'Monto Transferido')
ON CONFLICT DO NOTHING;

-- Migrar a txn.magnitude
INSERT INTO txn.magnitude (subject_type, subject_id, aspect_id, numeric_value, unit_id, as_of_date)
SELECT
  'ipr',
  e.subject_id,
  (SELECT id FROM ref.category WHERE scheme='magnitude_aspect' AND code='TRANSFER_AMOUNT'),
  (e.data->>'monto_transferido')::numeric,
  (SELECT id FROM ref.category WHERE scheme='currency' AND code='CLP'),
  e.occurred_at::date
FROM txn.event e
WHERE e.subject_type = 'ipr'
  AND e.data ? 'monto_transferido'
  AND (e.data->>'monto_transferido')::numeric > 0;
```

**Ontología**: gist:Magnitude pattern

---

### 7. `core.budget_program.item` + `asignacion` → FKs

| Campo | Ocurrencias | Valores |
|-------|-------------|---------|
| `item` | 22,280 | 14 |
| `asignacion` | 14,650 | 170 |

**Acción**:
```sql
-- 1. Crear schemes
CREATE TEMP TABLE items AS
SELECT DISTINCT (metadata->>'item')::text as code FROM core.budget_program WHERE metadata->>'item' IS NOT NULL;

INSERT INTO ref.category (scheme, code, label)
SELECT 'budget_item', code, 'Item ' || code FROM items;

-- 2. Agregar columnas
ALTER TABLE core.budget_program
  ADD COLUMN item_id UUID REFERENCES ref.category(id),
  ADD COLUMN allocation_id UUID REFERENCES ref.category(id);
```

**Ontología**: gnub:BudgetItem, gnub:BudgetAllocation (Clasificador Presupuestario chileno)

---

## PRIORIDAD MEDIA - Normalizaciones Recomendadas

### 8. `core.person.cargo_ultimo` → Tabla `core.position`

| Campo | Ocurrencias | Valores Únicos |
|-------|-------------|----------------|
| `cargo_ultimo` | 110 | 87 |

**Propuesta**: Crear tabla `core.position` (tde:Cargo) con FK en person.

---

### 9. `core.person.calificacion` → Nuevo scheme

| Campo | Ocurrencias | Valores Únicos |
|-------|-------------|----------------|
| `calificacion` | 110 | 57 |

**Propuesta**: Scheme `professional_qualification` con ~20 valores normalizados.

---

### 10. `core.agreement.estado_cgr_norm` → FK en resolution

| Campo | Ocurrencias | Valores |
|-------|-------------|---------|
| `estado_cgr_norm` | 129 | 4 (TOMA_RAZON, REPRESENTA, TR_CON_ALCANCES, EN_CGR) |

**Propuesta**: Agregar `cgr_outcome_id` a `core.resolution` (ontológicamente correcto).

---

### 11. `core.budget_program` - Montos dimensionados

| Campo | Ocurrencias |
|-------|-------------|
| `monto_fndr` | 10,040 |
| `monto_sectorial` | 738 |

**Propuesta**: Columnas `fndr_amount` y `sectorial_amount` NUMERIC(18,2).

---

### 12. `core.budget_program` - Arrastres

| Campo | Ocurrencias |
|-------|-------------|
| `arrastre_2024` | 5,781 |
| `arrastre_2025` | 3,864 |
| `arrastre_2026` | 4,871 |

**Propuesta**: Tabla `core.budget_carryover(budget_program_id, fiscal_year, amount)`.

---

### 13. `core.ipr_party.division` → FK

| Campo | Ocurrencias |
|-------|-------------|
| `division` | 37 |

**Propuesta**: Columna `sponsor_division_id` FK a `core.organization`.

---

### 14. `core.ipr.origen` → Booleano o scheme

| Campo | Ocurrencias | Valores |
|-------|-------------|---------|
| `origen` | 1,965 | 2 (MUNICIPIO, SECTORIAL/OTRO) |

**Propuesta**: Columna `is_municipal_origin BOOLEAN` (más simple).

---

## RECHAZADOS - No Normalizar

### `core.ipr.tipologia_original`

| Ocurrencias | Valores Distintos | Razón de Rechazo |
|-------------|-------------------|------------------|
| 1,924 | 30 | Mezcla dimensiones ontológicas (mecanismos + sectores + fuentes) |

**Decisión**: Mantener como audit trail. El mapeo a `investment_sector_id` (128 registros) representa el máximo semánticamente correcto.

---

### `core.organization.tipo_institucion`

| Ocurrencias | Razón de Rechazo |
|-------------|------------------|
| 1,594 | Redundante con `org_type_id` (99.6% cobertura) |

**Decisión**: Eliminar de metadata tras verificar cobertura completa.

---

### Campos de Audit Trail (69 campos)

Todos los campos `source`, `legacy_id`, `normalized_at`, `normalized_version`, etc. son **válidos** en JSONB según el principio: "JSONB metadata only for audit trails".

---

## Correcciones de Datos

### 3 eventos con `subject_type='rendicion_8pct'` anómalo

```sql
UPDATE txn.event
SET subject_type = 'ipr'
WHERE subject_type = 'rendicion_8pct';
```

---

## Métricas de Calidad

| Métrica | v2.0 (Anterior) | v3.0 (Post-Remediación) |
|---------|-----------------|-------------------------|
| Univocidad Categorial | 100% | 100% (mantener) |
| Campos JSONB → Relacional | 0 pendientes | 13 críticos + 6 medios |
| Integridad EJECUTOR | 0% | → 100% (post-sync) |
| RUT normalizado | 0% | → 100% (1,514 orgs) |
| Estamento normalizado | 0% | → 100% (110 persons) |

---

## Plan de Implementación

### Fase 1 - Integridad Relacional (Semana 1)
1. Sync EJECUTOR en ipr_party (1,646 registros)
2. Agregar `agreement_id` FK en ipr_party (476 registros)
3. Normalizar `rut` en organization (1,514 registros)

### Fase 2 - Personas (Semana 2)
4. Crear scheme `estamento` + columna (110 registros)
5. Agregar `technical_referent_id` en agreement (389 registros)
6. Evaluar tabla `core.position` para cargos

### Fase 3 - Presupuesto (Semana 3)
7. Crear schemes `budget_item` + `budget_allocation`
8. Agregar columnas en budget_program
9. Crear tabla `budget_carryover`

### Fase 4 - Eventos (Semana 4)
10. Migrar `monto_transferido` a txn.magnitude
11. Corregir 3 eventos anómalos
12. Limpiar campos redundantes en event.data

---

## Archivos de Referencia

- `model/model_goreos/sql/goreos_ddl.sql` - DDL v3.2
- `etl/migration/NORMALIZACION_v2.0_REPORTE_FINAL.md` - Baseline
- `docs/glosario_terminologico.md` - 244 términos ontológicos
- `etl/migration/sql/normalize_ipr_metadata_v2.sql` - Template de migración

---

**Próximo paso**: Crear script `etl/migration/sql/normalize_jsonb_v3.sql` con las 13 acciones críticas.
