# Checklist de Ejecución: Normalización JSONB V3 - Fase MEDIA (Campos 1-3)

**Fecha**: 2026-01-30
**Script**: `etl/migration/sql/normalize_jsonb_v3_fase_media_1-3.sql`
**Estado Inicial**: ✅ LISTO PARA EJECUTAR (Verificado)

---

## Pre-Ejecución

### 1. Backup
- [ ] Crear backup de base de datos producción
  ```bash
  docker exec goreos_db pg_dump -U goreos -d goreos_model | \
      gzip > backups/goreos_model_pre_normalizacion_media_$(date +%Y%m%d_%H%M%S).sql.gz
  ```
- [ ] Verificar tamaño del backup (debe ser ~98 MB comprimido)
- [ ] Guardar backup en ubicación segura (local + nube/backup remoto)

### 2. Verificación de Prerrequisitos
- [ ] Ejecutar script de verificación:
  ```bash
  docker exec -i goreos_db psql -U goreos -d goreos_model \
      < etl/migration/sql/verify_normalize_jsonb_v3_fase_media_1-3.sql
  ```
- [ ] Confirmar resultado: "LISTO PARA EJECUTAR"
- [ ] Verificar que NO hay WARNINGS críticos
- [ ] Confirmar datos esperados:
  - [ ] 110 personas con cargo_ultimo
  - [ ] 87 cargos únicos
  - [ ] 110 personas con calificacion
  - [ ] 57 calificaciones únicas
  - [ ] 129 agreements con estado_cgr_norm
  - [ ] 4 estados CGR únicos

### 3. Notificaciones
- [ ] Notificar a usuarios sobre ventana de mantenimiento (si aplica)
- [ ] Coordinar con equipo de desarrollo/ops
- [ ] Tener a mano procedimiento de rollback

---

## Ejecución en Ambiente de Test

### 4. Preparar Ambiente de Test
- [ ] Clonar base de datos de producción a test:
  ```bash
  docker exec goreos_db psql -U goreos -d postgres -c "
  DROP DATABASE IF EXISTS goreos_model_test;
  CREATE DATABASE goreos_model_test;"

  docker exec goreos_db bash -c "
  pg_dump -U goreos -d goreos_model | psql -U goreos -d goreos_model_test"
  ```
- [ ] Verificar clonación exitosa (tablas, registros, schemes)

### 5. Ejecutar Migración en Test
- [ ] Ejecutar script de normalización en test:
  ```bash
  docker exec -i goreos_db psql -U goreos -d goreos_model_test \
      < etl/migration/sql/normalize_jsonb_v3_fase_media_1-3.sql
  ```
- [ ] Revisar output completo (sin errores PostgreSQL)
- [ ] Anotar tiempo de ejecución: _______ minutos

### 6. Validar Resultados en Test

#### 6.1 Verificar Categorical Univocity
- [ ] Ejecutar query:
  ```bash
  docker exec goreos_db psql -U goreos -d goreos_model_test -c "
  SELECT 'qualification_id' AS campo, COUNT(DISTINCT c.scheme) AS schemes
  FROM core.person p JOIN ref.category c ON c.id = p.qualification_id
  UNION ALL
  SELECT 'cgr_outcome_id', COUNT(DISTINCT c.scheme)
  FROM core.agreement a JOIN ref.category c ON c.id = a.cgr_outcome_id;"
  ```
- [ ] Confirmar: schemes = 1 para ambas columnas ✅

#### 6.2 Verificar Tasas de Migración
- [ ] Ejecutar query de tasas (ver sección 5.2 en README)
- [ ] Confirmar tasas:
  - [ ] cargo_ultimo → position_id: _____ % (≥95%)
  - [ ] calificacion → qualification_id: _____ % (≥95%)
  - [ ] estado_cgr_norm → cgr_outcome_id: _____ % (100%)

#### 6.3 Verificar Estructuras Creadas
- [ ] Tabla core.position creada: _____ registros
- [ ] Scheme professional_qualification: _____ categorías (esperado: 17)
- [ ] Scheme cgr_outcome actualizado: _____ categorías (esperado: ≥4)

#### 6.4 Verificar Constraints e Índices
- [ ] Verificar constraints:
  ```bash
  docker exec goreos_db psql -U goreos -d goreos_model_test -c "
  SELECT conname, conrelid::regclass
  FROM pg_constraint
  WHERE conname IN ('chk_qualification_scheme', 'chk_cgr_outcome_scheme');"
  ```
- [ ] Confirmar 2 constraints creados ✅

#### 6.5 Smoke Test de Consultas
- [ ] Ejecutar consultas de ejemplo (ver sección "Impacto en Aplicaciones" en README)
- [ ] Confirmar que consultas relacionales funcionan correctamente

### 7. Decisión Go/No-Go para Producción
- [ ] Todos los checks anteriores ✅
- [ ] Equipo aprueba migración a producción
- [ ] Rollback plan documentado y entendido

---

## Ejecución en Producción

### 8. Ejecutar Migración en Producción
- [ ] Confirmar backup de producción existe y es válido
- [ ] Poner aplicaciones en modo mantenimiento (si aplica)
- [ ] Ejecutar script:
  ```bash
  docker exec -i goreos_db psql -U goreos -d goreos_model \
      < etl/migration/sql/normalize_jsonb_v3_fase_media_1-3.sql | tee logs/normalizacion_v3_media_1-3_$(date +%Y%m%d_%H%M%S).log
  ```
- [ ] Revisar output en tiempo real (sin errores)
- [ ] Anotar tiempo de ejecución: _______ minutos

### 9. Validar Resultados en Producción

#### 9.1 Categorical Univocity
- [ ] Ejecutar query de univocidad (mismo que en test)
- [ ] Confirmar: schemes = 1 ✅

#### 9.2 Tasas de Migración
- [ ] Ejecutar query de tasas
- [ ] Confirmar tasas ≥95% (100% para CGR)

#### 9.3 Verificar Integridad Referencial
- [ ] No hay violaciones FK
- [ ] No hay NULL inesperados en FK columns

### 10. Smoke Tests en Producción
- [ ] Ejecutar consultas de ejemplo
- [ ] Verificar aplicaciones (migration_viewer)
- [ ] Confirmar datos visibles y correctos en UI

---

## Post-Ejecución

### 11. Actualizar Aplicaciones
- [ ] Actualizar consultas en migration_viewer (si usa campos JSONB migrados)
- [ ] Actualizar consultas en Flask app (si aplica)
- [ ] Crear vistas simplificadas (v_person_details, v_agreement_cgr_status)

### 12. Documentación
- [ ] Actualizar ERD con nuevas estructuras:
  - [ ] Tabla core.position
  - [ ] Columna person.position_id
  - [ ] Columna person.qualification_id
  - [ ] Columna agreement.cgr_outcome_id
- [ ] Actualizar Data Dictionary con nuevos campos
- [ ] Documentar en CLAUDE.md (actualizar sección "Current Status")

### 13. Monitoreo Post-Migración
- [ ] Revisar logs de aplicaciones (primeras 24-48h)
- [ ] Monitorear performance de consultas (verificar índices efectivos)
- [ ] Solicitar feedback de usuarios

### 14. Limpieza (Opcional, post-validación)
- [ ] Después de 7-14 días de validación exitosa, considerar:
  - [ ] Eliminar backups temporales en tablas TEMP (se autoeliminan)
  - [ ] Archivar logs de migración
- [ ] Mantener JSONB original en metadata (NO eliminar, es audit trail)

---

## Rollback (Si es necesario)

### Opción A: Rollback Completo desde Backup
- [ ] Detener aplicaciones
- [ ] Restaurar backup:
  ```bash
  gunzip -c backups/goreos_model_pre_normalizacion_media_*.sql.gz | \
      docker exec -i goreos_db psql -U goreos -d goreos_model
  ```
- [ ] Verificar restauración exitosa
- [ ] Reiniciar aplicaciones
- [ ] Notificar a usuarios

### Opción B: Rollback Manual (Solo si se conoce fase específica fallida)
- [ ] Ejecutar comandos DROP/DELETE según fase (ver README sección Rollback)
- [ ] Verificar integridad post-rollback

---

## Métricas Finales (Completar post-ejecución)

### Tiempos
- Backup: _______ minutos
- Ejecución test: _______ minutos
- Ejecución producción: _______ minutos
- Tiempo total ventana: _______ minutos

### Tasas de Éxito
- cargo_ultimo → position_id: _______ %
- calificacion → qualification_id: _______ %
- estado_cgr_norm → cgr_outcome_id: _______ %

### Structures Created
- core.position registros: _______
- professional_qualification categorías: _______
- cgr_outcome categorías actualizadas: _______

### Issues Encontrados
- [ ] Ninguno ✅
- [ ] Describir issues: _________________________________

---

## Firma de Aprobación

### Pre-Ejecución
- **Verificación completada por**: _________________ Fecha: _______
- **Backup validado por**: _________________ Fecha: _______

### Test
- **Migración test exitosa**: _________________ Fecha: _______
- **Validaciones test OK**: _________________ Fecha: _______

### Producción
- **Aprobación Go para Prod**: _________________ Fecha: _______
- **Migración prod exitosa**: _________________ Fecha: _______
- **Validaciones prod OK**: _________________ Fecha: _______

### Post-Ejecución
- **Aplicaciones actualizadas**: _________________ Fecha: _______
- **Documentación actualizada**: _________________ Fecha: _______
- **Sign-off final**: _________________ Fecha: _______

---

## Notas Adicionales

_Espacio para notas, observaciones, o lecciones aprendidas durante la ejecución:_

---

**Versión**: 1.0
**Última actualización**: 2026-01-30
