# ÍNDICE DE PROGRESO: NORMALIZACIÓN JSONB v3.0

**Actualizado**: 2026-01-30
**Basado en**: Auditoría Categorial v3.0 (`docs/AUDITORIA_CATEGORIAL_v3.0.md`)

---

## ESTADO GENERAL

| Fase | Prioridad | Campos | Estado | Script | Reporte |
|------|-----------|--------|--------|--------|---------|
| **Fase CRÍTICA** | CRITICAL | 1-3 | ⏳ PENDIENTE | `normalize_jsonb_v3_fase_critica_1-3.sql` | - |
| **Fase MEDIA** | MEDIUM | 4-5 | ✅ COMPLETADO | `normalize_jsonb_v3_fase_media_4-5.sql` | `NORMALIZACION_v3_FASE_MEDIA_REPORTE.md` |
| **Fase BAJA** | LOW | 6-16 | ⏳ PENDIENTE | - | - |

**Total campos a normalizar**: 16
**Completados**: 2 (12.5%)
**Pendientes**: 14 (87.5%)

---

## FASE CRÍTICA (PRIORIDAD: CRITICAL) - 3 campos

### 1. core.organization.rut → rut VARCHAR(12) + CHECK

**Estado**: ⏳ PENDIENTE
**Registros**: 3,308
**Tipo**: JSONB string → VARCHAR(12) normalizado
**Ontología**: tde:Rut (Transformación Digital del Estado)

**Impacto**:
- CRÍTICO: Integridad referencial (RUT es natural key alternativo)
- CRÍTICO: Detección de duplicados
- ALTO: Queries de búsqueda por RUT

**Acción**:
```sql
-- 1. Agregar columna rut VARCHAR(12)
-- 2. Normalizar formato (eliminar puntos/guiones)
-- 3. Validar dígito verificador
-- 4. Crear índice único
-- 5. Agregar CHECK constraint para formato
```

---

### 2. core.person.estamento → estamento_id FK

**Estado**: ⏳ PENDIENTE
**Registros**: 1,208
**Tipo**: JSONB string → UUID FK a ref.category
**Ontología**: gnub:Estamento

**Impacto**:
- CRÍTICO: Clasificación de personal (DIRECTIVO, PROFESIONAL, ADMINISTRATIVO, etc.)
- ALTO: Reportes de dotación
- ALTO: Análisis de recursos humanos

**Prerequisitos**:
1. Crear scheme `estamento` en ref.category
2. Poblar valores desde metadata actual
3. Mapear a códigos normalizados

**Acción**:
```sql
-- 1. Analizar valores únicos en metadata->>'estamento'
-- 2. Crear scheme 'estamento' en ref.category
-- 3. Agregar columna estamento_id UUID FK
-- 4. Migrar datos con mapeo normalizado
-- 5. Agregar CHECK constraint scheme validation
```

---

### 3. core.ipr EJECUTOR sync (metadata vs ipr_party) - 880+ registros

**Estado**: ⏳ PENDIENTE
**Tipo**: Sincronización metadata->>'institucion_receptora' vs ipr_party.organization_id (role=EJECUTOR)
**Ontología**: gnub:Executor (ya existe como ipr.executor_id)

**Impacto**:
- CRÍTICO: Inconsistencia entre metadata y estructura relacional
- CRÍTICO: Queries de ejecutor pueden retornar resultados contradictorios
- ALTO: Reportes de ejecución

**Situación actual**:
- `core.ipr.executor_id` FK existe pero subutilizado
- `metadata->>'institucion_receptora'` contiene ejecutor en JSONB
- `core.ipr_party` con role=EJECUTOR es fuente de verdad relacional

**Acción**:
```sql
-- 1. Identificar IPRs con metadata->>'institucion_receptora'
-- 2. Sincronizar con ipr_party (role=EJECUTOR)
-- 3. Poblar ipr.executor_id desde ipr_party
-- 4. Resolver conflictos (múltiples ejecutores)
-- 5. Limpiar metadata JSONB
```

---

## FASE MEDIA (PRIORIDAD: MEDIUM) - 2 campos

### ✅ 4. core.ipr_party.division → sponsor_division_id FK

**Estado**: ✅ COMPLETADO (2026-01-30)
**Registros migrados**: 37/37 (100%)
**Tipo**: JSONB string → UUID FK a core.organization
**Ontología**: gnub:SponsorDivision

**Resultado**:
- Match rate: 100%
- FK órfanos: 0
- Índice: `idx_ipr_party_sponsor_division` (partial)

**Distribución**:
- DIDESO: 13 (35.1%)
- DIT: 8 (21.6%)
- DIFOI: 8 (21.6%)
- DIPIR: 5 (13.5%)
- DIPLADE: 3 (8.1%)

---

### ✅ 5. core.ipr.origen → is_municipal_origin BOOLEAN

**Estado**: ✅ COMPLETADO (2026-01-30)
**Registros migrados**: 1,965/1,965 (100%)
**Tipo**: JSONB string → BOOLEAN (default false)
**Ontología**: gnub:MunicipalOrigin

**Resultado**:
- Municipal (true): 1,327 (67.53%)
- Sectorial/Otro (false): 638 (32.47%)
- Índice: `idx_ipr_municipal_origin` (partial)

**Decisión de diseño**: BOOLEAN en lugar de FK scheme (solo 2 valores, principio de parsimonia)

---

## FASE BAJA (PRIORIDAD: LOW) - 11 campos

### 6. core.budget_commitment.cuenta_contable → accounting_account VARCHAR

**Estado**: ⏳ PENDIENTE
**Registros**: ~4,609
**Tipo**: JSONB string → VARCHAR(20)
**Ontología**: tde:AccountingAccount

---

### 7. core.budget_commitment.numero_compromiso → commitment_number VARCHAR

**Estado**: ⏳ PENDIENTE
**Registros**: ~4,609
**Tipo**: JSONB string → VARCHAR(50)
**Ontología**: gnub:CommitmentNumber

---

### 8. core.budget_commitment.fecha_compromiso → commitment_date DATE

**Estado**: ⏳ PENDIENTE
**Registros**: ~4,609
**Tipo**: JSONB string → DATE
**Ontología**: gnub:CommitmentDate

---

### 9. core.ipr.provincia (text array) → ipr_territory M:N

**Estado**: ⏳ PENDIENTE
**Registros**: ~1,500
**Tipo**: JSONB array → core.ipr_territory (ya existe)
**Ontología**: gnub:Province (via core.territory)

**Nota**: Tabla junction `ipr_territory` ya existe, solo requiere poblar desde metadata JSONB

---

### 10. core.ipr.comuna (text array) → ipr_territory M:N

**Estado**: ⏳ PENDIENTE
**Registros**: ~2,800
**Tipo**: JSONB array → core.ipr_territory
**Ontología**: gnub:Commune (via core.territory)

---

### 11. core.event.numero_resolucion → resolution_number VARCHAR

**Estado**: ⏳ PENDIENTE
**Registros**: ~1,200
**Tipo**: JSONB string → VARCHAR(100)
**Ontología**: gnub:ResolutionNumber

---

### 12. core.event.fecha_resolucion → resolution_date DATE

**Estado**: ⏳ PENDIENTE
**Registros**: ~1,200
**Tipo**: JSONB string → DATE
**Ontología**: gnub:ResolutionDate

---

### 13. core.agreement.numero_convenio → agreement_number VARCHAR

**Estado**: ⏳ PENDIENTE
**Registros**: ~800
**Tipo**: JSONB string → VARCHAR(50)
**Ontología**: gnub:AgreementNumber

---

### 14. core.agreement.fecha_firma → signature_date DATE

**Estado**: ⏳ PENDIENTE
**Registros**: ~800
**Tipo**: JSONB string → DATE
**Ontología**: gnub:SignatureDate

---

### 15. core.ipr.codigo_sni → sni_code VARCHAR

**Estado**: ⏳ PENDIENTE
**Registros**: ~1,800
**Tipo**: JSONB string → VARCHAR(20)
**Ontología**: gnub:SniCode

---

### 16. core.ipr.ano_postulacion → application_year INTEGER

**Estado**: ⏳ PENDIENTE
**Registros**: ~2,000
**Tipo**: JSONB string/number → INTEGER
**Ontología**: gnub:ApplicationYear

---

## MÉTRICAS DE PROGRESO

### Por Prioridad

| Prioridad | Total | Completados | Pendientes | % Completado |
|-----------|-------|-------------|------------|--------------|
| CRITICAL | 3 | 0 | 3 | 0% |
| MEDIUM | 2 | 2 | 0 | 100% |
| LOW | 11 | 0 | 11 | 0% |
| **TOTAL** | **16** | **2** | **14** | **12.5%** |

### Por Tabla

| Tabla | Normalizaciones | Completadas | Pendientes |
|-------|-----------------|-------------|------------|
| core.organization | 1 | 0 | 1 |
| core.person | 1 | 0 | 1 |
| core.ipr | 6 | 1 | 5 |
| core.ipr_party | 1 | 1 | 0 |
| core.budget_commitment | 3 | 0 | 3 |
| core.event | 2 | 0 | 2 |
| core.agreement | 2 | 0 | 2 |

---

## PRÓXIMOS PASOS

### 1. Fase CRÍTICA (INMEDIATO)

**Prioridad**: CRITICAL
**Script**: `normalize_jsonb_v3_fase_critica_1-3.sql`
**Estimado**: 2-3 horas desarrollo + testing

**Orden sugerido**:
1. `core.person.estamento` (más simple, requiere scheme creation)
2. `core.organization.rut` (validación compleja de dígito verificador)
3. `core.ipr` EJECUTOR sync (requiere análisis de conflictos)

### 2. Fase BAJA - Budget Commitments (MEDIO PLAZO)

**Prioridad**: LOW (pero alto volumen)
**Campos**: 6-8 (cuenta_contable, numero_compromiso, fecha_compromiso)
**Registros**: ~4,609
**Impacto**: Trazabilidad financiera

### 3. Fase BAJA - Territorial (MEDIO PLAZO)

**Prioridad**: LOW
**Campos**: 9-10 (provincia, comuna arrays)
**Registros**: ~4,300 combined
**Nota**: Tabla `ipr_territory` ya existe, solo poblar

### 4. Fase BAJA - Resto (LARGO PLAZO)

**Campos**: 11-16
**Estimado**: 1-2 semanas (puede ejecutarse en paralelo con otras tareas)

---

## CONVENCIONES DE NOMENCLATURA

### Scripts SQL

Patrón: `normalize_jsonb_v3_fase_{prioridad}_{campos}.sql`

Ejemplos:
- `normalize_jsonb_v3_fase_critica_1-3.sql`
- `normalize_jsonb_v3_fase_media_4-5.sql`
- `normalize_jsonb_v3_fase_baja_6-8.sql`

### Reportes

Patrón: `NORMALIZACION_v3_FASE_{PRIORIDAD}_REPORTE.md`

Ejemplos:
- `NORMALIZACION_v3_FASE_CRITICA_REPORTE.md`
- `NORMALIZACION_v3_FASE_MEDIA_REPORTE.md`

### Índices

Patrón: `idx_{tabla}_{columna}[_{condicion}]`

Ejemplos:
- `idx_ipr_party_sponsor_division` (partial WHERE sponsor_division_id IS NOT NULL)
- `idx_ipr_municipal_origin` (partial WHERE is_municipal_origin = true)
- `idx_organization_rut` (unique)

---

## REFERENCIAS

### Documentación Base

- `docs/AUDITORIA_CATEGORIAL_v3.0.md` - Auditoría completa de 98 campos JSONB
- `etl/migration/LECCIONES_APRENDIDAS.md` - Lecciones de migraciones previas
- `etl/migration/PRE_LOADER_CHECKLIST.md` - Checklist pre-normalización

### Normalizaciones Previas

- `etl/migration/NORMALIZACION_v2.0_REPORTE_FINAL.md` - v2.0 (investment_sector_id, fund_category_id)
- `etl/migration/sql/normalize_ipr_metadata_v2.sql` - Script v2.0 producción

### Ontologías

- `docs/glosario_terminologico.md` - 244 términos (Gist 14.0 + GNUB + TDE)
- `model/model_goreos/sql/goreos_ddl.sql` - Mapeos ontológicos (líneas 21-37)

---

**Última actualización**: 2026-01-30
**Responsable**: arquitecto-gore
**Estado del sistema**: ESTABLE (post Fase MEDIA)
