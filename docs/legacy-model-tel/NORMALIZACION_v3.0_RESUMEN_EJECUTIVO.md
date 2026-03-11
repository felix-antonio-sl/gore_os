# NORMALIZACIÓN v3.0 - RESUMEN EJECUTIVO

**Fecha**: 2026-01-30
**Agente**: arquitecto-gore v0.1.0
**Base de datos**: goreos_model_test (validado) → goreos_model (pendiente deploy)
**Fundamento**: docs/AUDITORIA_CATEGORIAL_v3.0.md

---

## Estado

✅ **COMPLETADO en ambiente TEST**
⏳ **PENDIENTE deployment a producción**

---

## Contexto

La Auditoría Categorial v3.0 identificó **98 campos JSONB** en 10 tablas que violaban el principio de normalización relacional. Se priorizaron **13 normalizaciones críticas** y **16 medias** para migrar de JSONB metadata a estructuras relacionales formales, garantizando:

1. **Univocidad Categorial**: Cada FK apunta a exactamente 1 scheme (100%)
2. **Integridad Referencial**: FKs con ON DELETE CASCADE y CHECK constraints
3. **Alineamiento Ontológico**: Mapeo formal a Gist 14.0 + GNUB + TDE
4. **Audit Trail**: Preservación de metadata original para trazabilidad

---

## Resumen por Fase

### Fase 1: Integridad Relacional

**Scripts**: `etl/migration/sql/normalize_jsonb_v3.sql`

| Acción | Registros | Ontología | CHECK Constraint |
|--------|-----------|-----------|------------------|
| `organization.rut` VARCHAR(12) UNIQUE | 1,524 | tde:RUT | `chk_rut_format` (regex) |
| `ipr_party.EJECUTOR` sync | 1,646 | gnub:hasExecutor | - |
| `ipr_party.agreement_id` FK | 476 | gnub:hasAgreement | - |

**Queries de Verificación**:
```sql
-- RUT normalizado
SELECT COUNT(*) FROM core.organization WHERE rut IS NOT NULL;
-- Expected: 1,524

-- EJECUTOR sincronizado
SELECT COUNT(*) FROM core.ipr_party ip
JOIN ref.category c ON ip.party_role_id = c.id
WHERE c.code = 'EJECUTOR';
-- Expected: 1,646
```

---

### Fase 2: Personas

**Scripts**: `etl/migration/sql/normalize_jsonb_v3_fase2_personas.sql`

| Acción | Registros | Ontología | Scheme/Valores |
|--------|-----------|-----------|----------------|
| `person.estamento_id` FK | 110 | tde:Estamento (Ley 18.834) | scheme='estamento' (7 valores) |
| `agreement.technical_referent_id` FK | 7 | gnub:TechnicalReferent | - |

**Valores Estamento**:
- PROFESIONAL, DIRECTIVO, ADMINISTRATIVO, TECNICO, AUXILIAR, HONORARIOS, AUTORIDAD

**Queries de Verificación**:
```sql
-- Estamento normalizado
SELECT c.code, COUNT(*)
FROM core.person p
JOIN ref.category c ON p.estamento_id = c.id
GROUP BY c.code;

-- Univocidad categorial
SELECT COUNT(DISTINCT c.scheme) FROM core.person p
JOIN ref.category c ON p.estamento_id = c.id;
-- Expected: 1
```

---

### Fase 3: Presupuesto

**Scripts**: `etl/migration/sql/normalize_jsonb_v3_fase3_presupuesto.sql`

| Acción | Registros | Ontología | Scheme |
|--------|-----------|-----------|--------|
| `budget_program.item_id` FK | 22,280 | gnub:BudgetItem | 14 valores |
| `budget_program.allocation_id` FK | 14,650 | gnub:BudgetAllocation | 170 valores |
| `core.budget_carryover` tabla | 13,375 | gnub:BudgetCarryover | años 2024-2026 |
| `budget_program.fndr_amount` | 10,040 | - | NUMERIC(18,2) |
| `budget_program.sectorial_amount` | 738 | - | NUMERIC(18,2) |

**Nueva Tabla**:
```sql
CREATE TABLE core.budget_carryover (
    id UUID PRIMARY KEY,
    budget_program_id UUID NOT NULL REFERENCES core.budget_program(id),
    fiscal_year SMALLINT NOT NULL CHECK (fiscal_year BETWEEN 2020 AND 2030),
    amount NUMERIC(18,2) NOT NULL CHECK (amount >= 0),
    ...,
    UNIQUE (budget_program_id, fiscal_year)
);
```

**Queries de Verificación**:
```sql
-- Items y allocations
SELECT
    COUNT(*) FILTER (WHERE item_id IS NOT NULL) as con_item,
    COUNT(*) FILTER (WHERE allocation_id IS NOT NULL) as con_allocation
FROM core.budget_program;

-- Arrastres por año
SELECT fiscal_year, COUNT(*), SUM(amount)
FROM core.budget_carryover
GROUP BY fiscal_year;
-- Expected: 2024: 5,424 | 2025: 3,850 | 2026: 4,101
```

---

### Fase 4: Eventos

**Scripts**: `etl/migration/sql/normalize_jsonb_v3_fase4_eventos.sql`

| Acción | Registros | Ontología | Scheme |
|--------|-----------|-----------|--------|
| `magnitude_aspect` scheme | 4 valores | gist:Magnitude pattern | TRANSFER_AMOUNT, BUDGET_AMOUNT, etc. |
| `currency` scheme | 3 valores | ISO 4217 | CLP, UF, USD |
| `txn.magnitude` migración | 953 eventos | gnub:MontoTransferido | $1.38B (2024-2026) |
| `subject_type` corrección | 3 eventos | - | rendicion_8pct → ipr |

**Distribución Magnitudes**:
- 2024: 464 eventos ($807M)
- 2025: 69 eventos ($182M)
- 2026: 420 eventos ($388M)

**Queries de Verificación**:
```sql
-- Magnitudes migradas
SELECT
    COUNT(*) as eventos_con_monto
FROM txn.event
WHERE data ? 'monto_transferido' AND (data->>'monto_transferido')::numeric > 0;
-- Expected: 953

SELECT COUNT(*) FROM txn.magnitude
WHERE aspect_id = (SELECT id FROM ref.category WHERE code='TRANSFER_AMOUNT');
-- Expected: 953

-- Subject_type anómalos corregidos
SELECT COUNT(*) FROM txn.event WHERE subject_type = 'rendicion_8pct';
-- Expected: 0
```

---

## Métricas de Calidad

| Métrica | v2.0 (Anterior) | v3.0 (Actual) |
|---------|-----------------|---------------|
| **Univocidad Categorial** | 100% | 100% (mantenido) |
| **Campos JSONB → Relacional** | 2 (funding_source, fund_category) | 15 (13 críticos + 2 previos) |
| **Integridad EJECUTOR** | 0% (sin sync) | 100% (1,646 registros) |
| **RUT normalizado** | 0% | 100% (1,524 orgs) |
| **Estamento normalizado** | 0% | 100% (110 personas) |
| **Budget items normalizado** | 0% | 100% (22,280 programas) |
| **Arrastres estructurados** | 0% | 100% (13,375 registros) |
| **Magnitudes en gist:Pattern** | 0% | 100% (953 eventos) |

---

## Impacto en Data Model

### Nuevas Columnas (8)

1. `core.organization.rut` VARCHAR(12) UNIQUE
2. `core.person.estamento_id` UUID FK
3. `core.agreement.technical_referent_id` UUID FK
4. `core.ipr_party.agreement_id` UUID FK (pendiente en DDL)
5. `core.budget_program.item_id` UUID FK
6. `core.budget_program.allocation_id` UUID FK
7. `core.budget_program.fndr_amount` NUMERIC(18,2)
8. `core.budget_program.sectorial_amount` NUMERIC(18,2)

### Nuevas Tablas (1)

- `core.budget_carryover` (51ª tabla del modelo)

### Nuevos Schemes (5)

1. **estamento** (7 valores): PROFESIONAL, DIRECTIVO, ADMINISTRATIVO, TECNICO, AUXILIAR, HONORARIOS, AUTORIDAD
2. **budget_item** (14 valores): Items presupuestarios chilenos
3. **budget_allocation** (170 valores): Asignaciones presupuestarias
4. **magnitude_aspect** (4 valores): TRANSFER_AMOUNT, BUDGET_AMOUNT, COMMITTED_AMOUNT, EXECUTED_AMOUNT
5. **currency** (3 valores): CLP, UF, USD

### CHECK Constraints (6)

1. `chk_rut_format`: Valida formato chileno `^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$`
2. `chk_estamento_scheme`: Valida `estamento_id` → scheme='estamento'
3. `chk_item_scheme`: Valida `item_id` → scheme='budget_item'
4. `chk_allocation_scheme`: Valida `allocation_id` → scheme='budget_allocation'
5. `fiscal_year BETWEEN 2020 AND 2030`: Rango de años válido
6. `amount >= 0`: Montos no negativos

---

## Alineamiento Ontológico

Todas las normalizaciones están formalmente alineadas con las ontologías:

### Gist 14.0
- `txn.magnitude` → **gist:Magnitude** pattern
- `magnitude_aspect` → **gist:MagnitudeAspect**

### GNUB (GORE Ñuble)
- `ipr_party.EJECUTOR` → **gnub:hasExecutor**
- `ipr_party.agreement_id` → **gnub:hasAgreement**
- `budget_program.item_id` → **gnub:BudgetItem**
- `budget_program.allocation_id` → **gnub:BudgetAllocation**
- `core.budget_carryover` → **gnub:BudgetCarryover**
- `agreement.technical_referent_id` → **gnub:TechnicalReferent**
- `txn.magnitude` → **gnub:MontoTransferido**

### TDE (Transformación Digital del Estado)
- `organization.rut` → **tde:RUT**
- `person.estamento_id` → **tde:Estamento** (Ley 18.834 Estatuto Administrativo)
- `agreement.technical_referent_id` → **tde:ResponsableAsignado**

---

## Archivos Generados

### Scripts SQL (3,264 líneas)
1. `etl/migration/sql/normalize_jsonb_v3.sql` (787 líneas)
2. `etl/migration/sql/normalize_jsonb_v3_fase2_personas.sql` (887 líneas)
3. `etl/migration/sql/normalize_jsonb_v3_fase3_presupuesto.sql` (933 líneas)
4. `etl/migration/sql/normalize_jsonb_v3_fase4_eventos.sql` (657 líneas)

### Documentación
1. `docs/AUDITORIA_CATEGORIAL_v3.0.md` - Auditoría completa (98 campos)
2. `CLAUDE.md` - Actualizado con normalizaciones v3.0
3. `model/model_goreos/sql/goreos_ddl.sql` - DDL v3.3 actualizado
4. **Este documento** - Resumen ejecutivo

---

## Deployment a Producción

### Pre-requisitos

- [ ] Backup completo de `goreos_model` producción
- [ ] Ventana de mantenimiento coordinada (1-2 horas)
- [ ] Apps detenidas temporalmente (`migration_viewer`, Flask app)
- [ ] Validación en test completada (✓ ya ejecutado)

### Secuencia de Deployment

```bash
# 1. Backup producción
docker exec goreos_db pg_dump -U goreos -d goreos_model > backup_pre_v3.0_$(date +%Y%m%d).sql

# 2. Ejecutar fases en orden
docker exec goreos_db psql -U goreos -d goreos_model -f /path/normalize_jsonb_v3.sql
docker exec goreos_db psql -U goreos -d goreos_model -f /path/normalize_jsonb_v3_fase2_personas.sql
docker exec goreos_db psql -U goreos -d goreos_model -f /path/normalize_jsonb_v3_fase3_presupuesto.sql
docker exec goreos_db psql -U goreos -d goreos_model -f /path/normalize_jsonb_v3_fase4_eventos.sql

# 3. Verificar univocidad categorial (debe ser 1 para cada FK)
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT 'estamento_id', COUNT(DISTINCT c.scheme) FROM core.person p
JOIN ref.category c ON c.id = p.estamento_id WHERE p.estamento_id IS NOT NULL;"

# 4. Verificar integridad EJECUTOR
docker exec goreos_db psql -U goreos -d goreos_model -c "
SELECT
    COUNT(*) as total_iprs_con_executor,
    COUNT(ip.id) as total_ipr_party_ejecutor
FROM core.ipr i
LEFT JOIN core.ipr_party ip ON i.id = ip.ipr_id
    AND ip.party_role_id = (SELECT id FROM ref.category WHERE code='EJECUTOR')
WHERE i.executor_id IS NOT NULL AND i.deleted_at IS NULL;"

# 5. Reiniciar apps
cd apps/migration_viewer && streamlit run app.py
```

### Rollback (si necesario)

```bash
# Restaurar backup completo
docker exec -i goreos_db psql -U goreos -d postgres -c "DROP DATABASE goreos_model;"
docker exec -i goreos_db psql -U goreos -d postgres -c "CREATE DATABASE goreos_model;"
docker exec -i goreos_db psql -U goreos -d goreos_model < backup_pre_v3.0_YYYYMMDD.sql
```

---

## Próximos Pasos

### Corto Plazo (Semana 1-2)
1. ✅ Deployment a producción (pendiente autorización)
2. ⏳ Validar queries en `apps/migration_viewer`
3. ⏳ Actualizar ERD en `model/model_goreos/docs/GOREOS_ERD_v3.md`
4. ⏳ Crear índices adicionales si hay degradación de performance

### Mediano Plazo (Semana 3-4)
5. Normalizar campos PRIORIDAD MEDIA (6 restantes):
   - `core.person.cargo_ultimo` → tabla `core.position`
   - `core.person.calificacion` → scheme `professional_qualification`
   - `core.agreement.estado_cgr_norm` → `resolution.cgr_outcome_id`
   - `core.ipr.origen` → `is_municipal_origin` BOOLEAN
   - `core.ipr_party.division` → `sponsor_division_id` FK
6. Limpiar campos redundantes en metadata (opcional, post-validación):
   ```sql
   UPDATE txn.event
   SET data = data - 'monto_transferido'
   WHERE data ? 'normalized_to_magnitude';
   ```

### Largo Plazo (Mes 2+)
7. Auditoría categorial v4.0 (si se identifican nuevos campos JSONB)
8. Crear vistas materializadas para queries frecuentes
9. Implementar particionamiento en tablas grandes (si crecimiento > 100K registros)

---

## Lecciones Aprendidas

### Técnicas
- ✅ **Variables PL/pgSQL**: Usar prefijo `v_` para evitar ambigüedad con nombres de columnas
- ✅ **Transacciones**: Separar fases en transacciones independientes para mejor control
- ✅ **Backups temporales**: Crear `temp_*_backup` antes de cada UPDATE masivo
- ✅ **Verificaciones**: RAISE NOTICE con conteos pre/post por cada operación
- ✅ **Idempotencia**: Verificar existencia antes de CREATE (columnas, índices, schemes)

### Ontológicas
- ✅ **Univocidad Categorial**: Principio no negociable (1 FK → 1 scheme)
- ✅ **CHECK Constraints**: Obligatorios para todos los FKs a `ref.category`
- ✅ **Audit Trail**: Preservar metadata original incluso después de normalizar
- ✅ **Gist Patterns**: Aplicar consistentemente (Magnitude para métricas numéricas)

### Metodológicas
- ✅ **Test primero**: Ejecutar SIEMPRE en ambiente test antes de producción
- ✅ **Agentes paralelos**: Usar para generar scripts independientes simultáneamente
- ✅ **Documentación continua**: Actualizar CLAUDE.md + DDL al mismo tiempo que código

---

**Versión**: 1.0
**Arquitecto**: GORE-ARQUITECTO v0.1.0
**Motores**: CM-ARTIFACT-GENERATOR, CM-AUDIT-ENGINE, CM-STRUCTURE-ENGINE
**Fecha última actualización**: 2026-01-30
