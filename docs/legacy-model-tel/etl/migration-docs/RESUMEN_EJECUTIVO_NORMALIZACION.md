# Resumen Ejecutivo: Plan de Normalización JSONB

**Fecha**: 2026-01-30
**Autor**: Equipo de Desarrollo GORE_OS
**Estado**: Propuesta para revisión

---

## Contexto

Actualmente, el sistema GORE_OS almacena datos estructurados en campos JSONB (`metadata` y `data`) que deberían estar normalizados en columnas y tablas relacionales. Esto limita la integridad referencial, dificulta las consultas y aumenta el riesgo de inconsistencias.

### Estado Actual
- **6 tablas principales** con campos JSONB
- **16,222 registros totales** afectados
- **76+ keys únicas** distribuidas en metadata/data
- **~54% de datos normalizables** identificados

### Migración Previa Exitosa
Ya completamos la normalización parcial de `core.ipr` (Programas 8%):
- `metadata->>'fondo'` → `funding_source_id` (FK)
- `metadata->>'institucion_receptora'` → `executor_id` (FK)
- `metadata->>'monto_transferido'` → `core.budget_commitment` (tabla)
- `provincia/comuna` → `core.ipr_territory` (junction table)

**Resultado**: Datos más estructurados, consultas más rápidas, integridad garantizada.

---

## Propuesta

Normalizar sistemáticamente todos los campos JSONB en **6 fases** durante **7 semanas**.

### Impacto Esperado

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Keys en JSONB | 76+ | ~35 | **-54%** |
| FKs nuevas | 0 | 15+ | +100% |
| Tablas nuevas | 0 | 3 | +100% |
| Schemes en ref.category | 38 | 41+ | +8% |

### Beneficios

1. **Integridad referencial**: Validación automática vía FKs
2. **Performance**: Índices en columnas vs búsquedas en JSONB
3. **Consultas SQL**: Joins directos vs extracciones JSON
4. **Validación**: Constraints en tiempo de inserción
5. **Documentación**: ERD actualizado refleja modelo real

---

## Fases Propuestas

### FASE 1: core.budget_commitment (Semana 2)
**Prioridad**: Alta | **Riesgo**: Bajo | **Registros**: 4,609

**Cambios**:
- Nueva columna: `fiscal_year INTEGER`
- Nueva columna FK: `fund_id → ref.category`
- Análisis de redundancia: `bip` vs `ipr_id`

**Impacto**: -40% keys en metadata (5 → 3)

---

### FASE 2: txn.event (Semana 6)
**Prioridad**: Alta | **Riesgo**: Alto (tabla particionada) | **Registros**: 4,040

**Cambios**:
- 4 columnas FK nuevas: `fund_type_id`, `event_category_id`, `execution_state_id`, `document_id`
- Nueva tabla: `txn.event_territory` (junction)
- Migración de montos a `txn.magnitude`
- Limpieza de redundancias: `tipo_evento_id/name`

**Impacto**: -60% keys en data (25+ → ~10)

---

### FASE 3: core.ipr (Semana 5)
**Prioridad**: Alta | **Riesgo**: Medio | **Registros**: 3,621

**Cambios**:
- Nueva columna: `codigo_idis VARCHAR(50)` (unique)
- 2 columnas FK: `origin_event_id`, `technical_unit_id`
- Enriquecimiento: `ipr_type_id`, `mcd_phase_id` desde metadata

**Impacto**: -60% keys en metadata (15 → ~6)

---

### FASE 4: core.organization (Semana 3)
**Prioridad**: Media | **Riesgo**: Bajo | **Registros**: 3,308

**Cambios**:
- Nueva columna: `rut VARCHAR(12)` (unique)
- Enriquecimiento: `org_type_id` desde metadata
- Nueva tabla: `core.organization_alias`

**Impacto**: -38% keys en metadata (13 → ~8)

---

### FASE 5: core.agreement (Semana 4)
**Prioridad**: Media | **Riesgo**: Medio | **Registros**: 533

**Cambios**:
- 3 columnas FK: `technical_referent_id`, `cgr_state_id`, `territory_id`
- Enriquecimiento: `state_id` desde metadata

**Impacto**: -54% keys en metadata (13 → ~6)

---

### FASE 6: core.person (Semana 2)
**Prioridad**: Baja | **Riesgo**: Bajo | **Registros**: 111

**Cambios**:
- 2 columnas: `employee_category_id` (FK), `last_position` (TEXT)
- Nueva tabla: `core.person_qualification`

**Impacto**: -60% keys en metadata (5 → 2)

---

## Cronograma

| Semana | Actividad | Fases | Esfuerzo |
|--------|-----------|-------|----------|
| 1 | Preparación: schemes, validaciones, scripts | - | 3 días |
| 2 | FASE 1 + FASE 6 (bajo riesgo) | 1, 6 | 4 días |
| 3 | FASE 4 (medio riesgo) | 4 | 3 días |
| 4 | FASE 5 (medio riesgo) | 5 | 3 días |
| 5 | FASE 3 (alto impacto) | 3 | 4 días |
| 6 | FASE 2 (alto riesgo - particionada) | 2 | 5 días |
| 7 | Validación, limpieza, documentación | - | 3 días |

**Total**: 7 semanas, ~25 días de desarrollo

---

## Riesgos y Mitigaciones

### Riesgo 1: Pérdida de datos
**Probabilidad**: Baja | **Impacto**: Crítico

**Mitigación**:
- Backup de tabla antes de cada fase
- Scripts de validación automáticos
- Rollback probado
- Ejecución en transacciones

### Riesgo 2: Degradación de performance
**Probabilidad**: Media | **Impacto**: Moderado

**Mitigación**:
- Crear índices después de migración
- Benchmark de queries críticas antes/después
- Migración por lotes en tablas grandes
- Ejecución en ventana de mantenimiento

### Riesgo 3: Inconsistencias en mapeo
**Probabilidad**: Media | **Impacto**: Moderado

**Mitigación**:
- Crear categorías faltantes antes de migración
- Validar 100% de match antes de limpieza
- Mantener valores originales en metadata hasta validación final
- Permitir NULL en FKs opcionales

### Riesgo 4: Dependencias entre tablas
**Probabilidad**: Alta | **Impacto**: Bajo

**Mitigación**:
- Normalizar `core.person` antes de crear FKs desde otras tablas
- Ejecutar fases en orden de dependencias
- Crear personas/organizaciones faltantes desde metadata

---

## Recursos Necesarios

### Herramientas Desarrolladas
1. **Script de validación SQL**: `validate_jsonb_normalization.sql`
   - Análisis de estado actual por tabla
   - Verificación de consistencia
   - Reporte de completitud

2. **Generador de SQL**: `generate_migration_sql.py`
   - Genera ALTER TABLE automáticamente
   - Crea scripts de migración por fase
   - Incluye validaciones y rollback

3. **Plan detallado**: `PLAN_NORMALIZACION_JSONB.md`
   - 6 fases documentadas
   - DDL completo por tabla
   - Checklist de implementación

### Equipo Requerido
- **1 desarrollador senior**: Ejecución de migraciones
- **1 DBA**: Revisión de performance y optimización
- **1 QA**: Validación de integridad de datos
- **Product Owner**: Validación de reglas de negocio

---

## Entregables

### Por cada fase:
1. Backup de tabla pre-migración
2. Script SQL de migración ejecutado
3. Reporte de validación (sin errores)
4. Actualización de ERD
5. Actualización de loaders ETL
6. Tests unitarios actualizados
7. Commit con tag de versión

### Final (Semana 7):
1. ERD v3.2 actualizado
2. Documentación de nuevos schemes
3. Guía de consultas optimizadas
4. Benchmark de performance
5. Lecciones aprendidas
6. Plan de rollback completo

---

## Métricas de Éxito

| Métrica | Meta | Medición |
|---------|------|----------|
| Reducción de keys JSONB | ≥50% por tabla | Comparar conteo before/after |
| Integridad referencial | 100% FKs válidas | Query de validación sin resultados |
| Pérdida de datos | 0 registros | Comparar COUNT(*) y SUM(valores) |
| Degradación de performance | <10% | Benchmark queries críticas |
| Cobertura de normalización | ≥95% datos | % de campos con valor en columna |

---

## Próximos Pasos

### Inmediatos (esta semana):
1. ✅ Revisar plan con equipo de desarrollo
2. ✅ Validar priorización con Product Owner
3. ✅ Aprobar cronograma y recursos
4. ⬜ Ejecutar script de validación en DEV
5. ⬜ Crear issues en GitHub por fase

### Semana 1 (preparación):
1. ⬜ Crear schemes faltantes en `ref.category`
2. ⬜ Generar scripts SQL con `generate_migration_sql.py`
3. ⬜ Revisar y ajustar scripts generados
4. ⬜ Crear ambiente de prueba con datos de producción
5. ⬜ Ejecutar FASE 1 en ambiente de prueba (piloto)

### Semana 2 en adelante:
- Ejecutar fases según cronograma
- Validar y documentar después de cada fase
- Ajustar plan basado en aprendizajes

---

## Aprobaciones Requeridas

| Rol | Nombre | Aprobación | Fecha |
|-----|--------|------------|-------|
| Tech Lead | | ⬜ | |
| DBA | | ⬜ | |
| Product Owner | | ⬜ | |
| Arquitecto de Software | | ⬜ | |

---

## Referencias

- [Plan completo (173 líneas)](./PLAN_NORMALIZACION_JSONB.md)
- [Script de validación SQL](./scripts/validate_jsonb_normalization.sql)
- [Generador de SQL](./scripts/generate_migration_sql.py)
- [Lecciones aprendidas ETL](./LECCIONES_APRENDIDAS.md)
- [Checklist pre-loader](./PRE_LOADER_CHECKLIST.md)

---

**Contacto**: Equipo de Desarrollo GORE_OS
**Documento vivo**: Este plan se actualizará según aprendizajes durante la implementación.
