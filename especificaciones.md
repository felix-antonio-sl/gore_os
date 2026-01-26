# GOREOS - Sistema de Gestión de Trabajo Regional
## Documento de Requisitos y Especificaciones Técnicas

**Versión:** 1.0
**Fecha:** 2026-01-26
**Estado:** Borrador para revisión

---

## 1. VISIÓN Y ALCANCE

### 1.1 Propósito

GOREOS es un sistema web para la gestión unificada de trabajo en el Gobierno Regional de Ñuble. Integra la gestión de inversión pública (IPR), convenios, resoluciones, y el trabajo operativo de equipos, con un modelo simplificado que difunde las fronteras entre lo personal, lo de equipo y lo institucional.

### 1.2 Objetivos del Sistema

| Objetivo | Descripción | Métrica de Éxito |
|----------|-------------|------------------|
| **Visibilidad** | Proporcionar visión 360° del estado de la cartera de inversión | 100% de IPR con estado actualizado |
| **Coordinación** | Facilitar coordinación entre divisiones | Reducción de IPR con problemas inter-división |
| **Productividad** | Gestionar trabajo con metodología lean simplificada | Reducción de trabajo vencido |
| **Trazabilidad** | Registrar historial completo de decisiones y acciones | Auditoría completa de cambios |
| **Alertas** | Detectar problemas antes de que se vuelvan críticos | Reducción de crisis reactivas |

### 1.3 Usuarios del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESTRUCTURA DE USUARIOS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ADMIN_SISTEMA (1-2 usuarios)                                   │
│  └── Configura sistema, usuarios, importa datos                 │
│                                                                  │
│  ADMIN_REGIONAL (1-3 usuarios)                                  │
│  └── Visión 360°, coordina divisiones, gestiona crisis          │
│                                                                  │
│  JEFE_DIVISION (6-8 usuarios)                                   │
│  └── Supervisa su división, verifica trabajo, asigna            │
│                                                                  │
│  ENCARGADO (30-50 usuarios)                                     │
│  └── Ejecuta trabajo, actualiza avances, reporta problemas      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 Alcance del Sistema

**Incluido:**
- Gestión de entidades formales: IPR, Convenio, Resolución
- Gestión unificada de trabajo (ítems de trabajo)
- Registro y seguimiento de problemas
- Sistema de alertas automáticas
- Dashboards por rol
- Reportes y exportación

**Excluido (primera versión):**
- Integración con sistemas externos (BIP, SIGFE, SGDOC)
- Aplicación móvil nativa
- Notificaciones push
- Chat/mensajería interna

---

## 2. REQUISITOS FUNCIONALES

### 2.1 Módulo de Autenticación y Usuarios

#### RF-001: Inicio de Sesión
- El sistema debe permitir autenticación con email y contraseña
- Debe soportar "recordar sesión" por 30 días
- Debe bloquear cuenta tras 5 intentos fallidos
- **Prioridad:** Alta

#### RF-002: Gestión de Usuarios (ADMIN_SISTEMA)
- Crear, editar, desactivar usuarios
- Asignar rol del sistema (ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, ENCARGADO)
- Asignar división
- **Prioridad:** Alta

#### RF-003: Restablecimiento de Contraseña
- Usuario solicita restablecimiento por email
- Sistema envía link con token de 24h de validez
- **Prioridad:** Media

#### RF-004: Gestión de Divisiones (ADMIN_SISTEMA)
- Crear, editar divisiones
- Asignar jefe de división
- **Prioridad:** Alta

### 2.2 Módulo de Entidades Formales

#### RF-010: Gestión de IPR (Iniciativas de Inversión)
- Listar IPR con filtros (división, estado, instrumento, responsable)
- Ver ficha completa de IPR con:
  - Datos generales (código, nombre, instrumento, montos)
  - Estado actual (avance físico, financiero)
  - Convenios asociados
  - Resoluciones asociadas
  - Trabajo asociado (árbol de ítems)
  - Problemas asociados
  - Alertas activas
  - Historial de cambios
- Editar datos de IPR (según permisos)
- Asignar/reasignar responsable
- **Prioridad:** Alta

#### RF-011: Importación de IPR (ADMIN_SISTEMA)
- Importar desde archivo Excel
- Mapeo de columnas configurable
- Validación de datos antes de importar
- Reporte de errores de importación
- **Prioridad:** Alta

#### RF-012: Gestión de Convenios
- Listar convenios con filtros
- Ver ficha de convenio con:
  - Datos generales (número, tipo, fechas)
  - Cuotas y estado de pago
  - IPR vinculada
  - Resolución vinculada
  - Trabajo asociado
- Registrar nueva cuota
- Actualizar estado de pago
- **Prioridad:** Alta

#### RF-013: Importación de Convenios (ADMIN_SISTEMA)
- Importar desde archivo Excel
- Vincular automáticamente a IPR por código
- **Prioridad:** Alta

#### RF-014: Gestión de Resoluciones
- Crear nueva resolución
- Vincular a IPR y/o Convenio
- Estados: BORRADOR, EN_REVISION, FIRMADA, TRAMITADA, RECHAZADA
- Registrar fechas clave (elaboración, firma, tramitación)
- **Prioridad:** Media

### 2.3 Módulo de Trabajo Unificado

#### RF-020: Crear Ítem de Trabajo
- Campos obligatorios: título, responsable
- Campos opcionales: descripción, fecha límite, prioridad, padre
- Vinculación a entidad formal: IPR, Convenio, Resolución, Problema
- Herencia automática de vinculación del padre
- Contexto de proceso DIPIR (opcional)
- **Prioridad:** Alta

#### RF-021: Captura Rápida
- Crear ítem con solo título (se asigna al usuario actual)
- Opción de vincular a IPR en un clic
- **Prioridad:** Alta

#### RF-022: Flujo de Estados
- Estados: PENDIENTE → EN_PROGRESO → BLOQUEADO → COMPLETADO → VERIFICADO
- También: CANCELADO (desde cualquier estado activo)
- Transiciones permitidas:
  - PENDIENTE → EN_PROGRESO, BLOQUEADO, CANCELADO
  - EN_PROGRESO → COMPLETADO, BLOQUEADO, CANCELADO
  - BLOQUEADO → EN_PROGRESO, CANCELADO
  - COMPLETADO → VERIFICADO (solo jefe/admin)
- **Prioridad:** Alta

#### RF-023: Bloqueo de Trabajo
- Indicar motivo de bloqueo
- Opción de indicar "esperando" otro ítem de trabajo
- Desbloqueo automático cuando el ítem esperado se completa
- **Prioridad:** Media

#### RF-024: Verificación de Trabajo
- Solo JEFE_DIVISION o superior puede verificar
- Solo ítems en estado COMPLETADO pueden verificarse
- Registro de quién verificó y cuándo
- **Prioridad:** Alta

#### RF-025: Reasignación de Trabajo
- Cambiar responsable de un ítem
- Actualiza automáticamente división
- Registra en historial con comentario opcional
- **Prioridad:** Alta

#### RF-026: Jerarquía de Trabajo
- Crear sub-ítems (hijos) de un ítem padre
- Visualizar árbol de trabajo
- Métricas agregadas: total hijos, hijos completados
- **Prioridad:** Media

#### RF-027: Consulta "Mi Trabajo"
- Lista de ítems asignados al usuario actual
- Ordenados por prioridad y fecha límite
- Filtros: estado, fecha, IPR vinculada
- Indicador visual de vencidos
- **Prioridad:** Alta

#### RF-028: Consulta "Trabajo de División"
- Lista de ítems de toda la división
- Agrupado por responsable
- Solo visible para JEFE_DIVISION o superior
- **Prioridad:** Alta

#### RF-029: Consulta "Trabajo por IPR"
- Ver todo el trabajo vinculado a una IPR
- Visualización en árbol
- Métricas: total, completados, bloqueados, vencidos
- **Prioridad:** Alta

#### RF-030: Historial de Ítem
- Registro automático de cambios de estado
- Registro de reasignaciones
- Comentarios asociados a cambios
- **Prioridad:** Media

### 2.4 Módulo de Problemas

#### RF-040: Registrar Problema
- Descripción del problema
- Clasificación por tipo: TECNICO, FINANCIERO, ADMINISTRATIVO, LEGAL, COORDINACION, EXTERNO
- Clasificación por impacto: BLOQUEA_PAGO, RETRASA_OBRA, RETRASA_CONVENIO, RIESGO_RENDICION, OTRO
- Vinculación a IPR, Convenio o Resolución
- **Prioridad:** Alta

#### RF-041: Gestión de Problemas
- Estados: ABIERTO → EN_GESTION → RESUELTO / CERRADO_SIN_RESOLVER
- Registrar solución propuesta
- Registrar solución aplicada
- Crear trabajo desde problema
- **Prioridad:** Alta

#### RF-042: Consulta de Problemas
- Listar problemas abiertos
- Filtrar por división, tipo, impacto
- Ordenar por criticidad
- **Prioridad:** Alta

#### RF-043: Problema Actualiza IPR
- Al registrar/resolver problema, actualizar flag `tiene_problemas_abiertos` en IPR
- Actualizar `nivel_alerta` de IPR según impacto de problemas
- **Prioridad:** Alta

### 2.5 Módulo de Alertas

#### RF-050: Generación Automática de Alertas
- Evaluar reglas diariamente (07:00)
- Tipos de alerta:
  - CUOTA_VENCIDA: cuota de pago vencida
  - CUOTA_PROXIMA: cuota próxima a vencer (7 días)
  - CONVENIO_POR_VENCER: convenio próximo a vencer (30 días)
  - CONVENIO_VENCIDO: convenio vencido
  - TRABAJO_VENCIDO: ítem de trabajo vencido
  - TRABAJO_BLOQUEADO_LARGO: ítem bloqueado > 7 días
  - PROBLEMA_SIN_GESTION: problema abierto > 3 días sin trabajo
  - RENDICION_PENDIENTE: rendición pendiente
  - OBRA_SIN_PAGO: avance >= 95%, pago pendiente
- **Prioridad:** Alta

#### RF-051: Niveles de Alerta
- INFO: informativo, sin acción urgente
- ATENCION: requiere atención pronto
- ALTO: requiere acción esta semana
- CRITICO: requiere acción inmediata
- **Prioridad:** Alta

#### RF-052: Consulta de Alertas
- Ver alertas activas
- Filtrar por nivel, tipo, división
- Ordenar por criticidad
- **Prioridad:** Alta

#### RF-053: Atender Alerta
- Marcar alerta como atendida
- Registrar acción tomada
- Registrar quién atendió y cuándo
- **Prioridad:** Alta

### 2.6 Módulo de Dashboards

#### RF-060: Dashboard Ejecutivo (ADMIN_REGIONAL)
- Total de IPR activas
- IPR con problemas abiertos
- Problemas abiertos (total y críticos)
- Alertas críticas
- Trabajo vencido (total)
- Trabajo bloqueado (total)
- Trabajo por verificar
- Tendencias semanales:
  - Problemas nuevos vs resueltos
  - Trabajo completado
- **Prioridad:** Alta

#### RF-061: Dashboard de División (JEFE_DIVISION)
- Trabajo por estado (gráfico)
- Trabajo por responsable (con indicador de vencidos)
- Trabajo vencido de la división
- Trabajo por verificar
- Problemas de la división
- **Prioridad:** Alta

#### RF-062: Dashboard Personal (ENCARGADO)
- Conteo por estado: pendientes, en progreso, bloqueados
- Vencidos
- Completados esta semana
- Mis IPR asignadas
- **Prioridad:** Alta

### 2.7 Módulo de Reportes

#### RF-070: Exportar Informe Ejecutivo
- Resumen semanal en PDF
- Incluye: métricas, problemas críticos, trabajo destacado
- **Prioridad:** Media

#### RF-071: Exportar Lista de Trabajo
- Excel con trabajo filtrado
- Campos configurables
- **Prioridad:** Media

#### RF-072: Exportar Ficha IPR
- PDF con toda la información de una IPR
- Incluye convenios, resoluciones, trabajo, problemas
- **Prioridad:** Media

### 2.8 Módulo de Administración

#### RF-080: Configuración de Alertas (ADMIN_SISTEMA)
- Definir umbrales de alertas
- Activar/desactivar tipos de alerta
- **Prioridad:** Baja

#### RF-081: Logs del Sistema (ADMIN_SISTEMA)
- Ver registro de actividad
- Filtrar por usuario, fecha, acción
- **Prioridad:** Baja

#### RF-082: Gestión de Backups (ADMIN_SISTEMA)
- Ver estado de backups automáticos
- Descargar backup manual
- **Prioridad:** Baja

---

## 3. REQUISITOS NO FUNCIONALES

### 3.1 Rendimiento

| Requisito | Especificación |
|-----------|----------------|
| RNF-001 | Tiempo de carga de dashboard < 2 segundos |
| RNF-002 | Tiempo de respuesta de APIs < 500ms (p95) |
| RNF-003 | Soporte para 100 usuarios concurrentes |
| RNF-004 | Importación de 500 IPR < 60 segundos |

### 3.2 Disponibilidad

| Requisito | Especificación |
|-----------|----------------|
| RNF-010 | Disponibilidad 99% en horario laboral (Lun-Vie 08:00-18:00) |
| RNF-011 | Ventana de mantenimiento: domingos 00:00-06:00 |
| RNF-012 | Backup diario automático |
| RNF-013 | Retención de backups: 30 días |

### 3.3 Seguridad

| Requisito | Especificación |
|-----------|----------------|
| RNF-020 | Autenticación obligatoria para todas las funciones |
| RNF-021 | Contraseñas hasheadas con bcrypt (cost 12) |
| RNF-022 | Sesiones con JWT, expiración 24h |
| RNF-023 | HTTPS obligatorio |
| RNF-024 | Protección CSRF en formularios |
| RNF-025 | Rate limiting: 100 req/min por usuario |
| RNF-026 | Auditoría de acciones sensibles |

### 3.4 Usabilidad

| Requisito | Especificación |
|-----------|----------------|
| RNF-030 | Interfaz responsive (desktop, tablet) |
| RNF-031 | Navegadores soportados: Chrome, Firefox, Edge (últimas 2 versiones) |
| RNF-032 | Mensajes de error claros y accionables |
| RNF-033 | Confirmación antes de acciones destructivas |
| RNF-034 | Feedback visual de acciones (loading, success, error) |

### 3.5 Mantenibilidad

| Requisito | Especificación |
|-----------|----------------|
| RNF-040 | Código documentado con docstrings |
| RNF-041 | Cobertura de tests > 70% |
| RNF-042 | Logs estructurados (JSON) |
| RNF-043 | Configuración externalizada (variables de entorno) |

---

## 4. MODELO DE DATOS

### 4.1 Diagrama Entidad-Relación

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODELO DE DATOS GOREOS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  AUTENTICACIÓN                   ORGANIZACIÓN                               │
│  ┌─────────────┐                 ┌─────────────┐                            │
│  │   usuario   │────────────────▶│  division   │                            │
│  │─────────────│                 │─────────────│                            │
│  │ id          │                 │ id          │                            │
│  │ email       │                 │ nombre      │                            │
│  │ password    │                 │ jefe_id     │────┐                       │
│  │ nombre      │                 └─────────────┘    │                       │
│  │ rol_sistema │◀───────────────────────────────────┘                       │
│  │ division_id │                                                            │
│  └─────────────┘                                                            │
│         │                                                                    │
│         │ responsable_id, creado_por_id, etc.                               │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      ENTIDADES FORMALES                              │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │                                                                      │    │
│  │  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐          │    │
│  │  │ iniciativa  │◀────▶│  convenio   │◀────▶│ resolucion  │          │    │
│  │  │    (IPR)    │      │             │      │             │          │    │
│  │  │─────────────│      │─────────────│      │─────────────│          │    │
│  │  │ codigo_unico│      │ numero      │      │ numero      │          │    │
│  │  │ nombre      │      │ tipo        │      │ tipo        │          │    │
│  │  │ instrumento │      │ fecha_inicio│      │ materia     │          │    │
│  │  │ monto       │      │ fecha_termino│     │ estado      │          │    │
│  │  │ avance_fisico│     │ monto       │      │ fecha_firma │          │    │
│  │  │ nivel_alerta│      │ cuotas[]    │      │             │          │    │
│  │  └─────────────┘      └─────────────┘      └─────────────┘          │    │
│  │         │                    │                    │                  │    │
│  └─────────┴────────────────────┴────────────────────┴──────────────────┘    │
│            │                    │                    │                       │
│            ▼                    ▼                    ▼                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         TRABAJO                                      │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │                        item                                  │    │    │
│  │  │─────────────────────────────────────────────────────────────│    │    │
│  │  │ id, codigo                                                   │    │    │
│  │  │ titulo, descripcion                                          │    │    │
│  │  │ padre_id ──────────────────────────────┐ (jerarquía)        │    │    │
│  │  │ responsable_id, division_id            │                     │    │    │
│  │  │ estado (PENDIENTE/EN_PROGRESO/...)     │                     │    │    │
│  │  │ fecha_limite, prioridad                │                     │    │    │
│  │  │ iniciativa_id ─────────────────────────┼── vinculación      │    │    │
│  │  │ convenio_id ───────────────────────────┼── a entidades      │    │    │
│  │  │ resolucion_id ─────────────────────────┘   formales         │    │    │
│  │  │ problema_id ───────────────────────────── origen problema   │    │    │
│  │  └─────────────────────────────────────────────────────────────┘    │    │
│  │         │                                                            │    │
│  │         ▼                                                            │    │
│  │  ┌─────────────────┐                                                │    │
│  │  │ item_historial  │ (cambios de estado, reasignaciones)           │    │
│  │  └─────────────────┘                                                │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                       PROBLEMAS Y ALERTAS                            │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │                                                                      │    │
│  │  ┌─────────────┐                      ┌─────────────┐               │    │
│  │  │  problema   │                      │   alerta    │               │    │
│  │  │─────────────│                      │─────────────│               │    │
│  │  │ codigo      │                      │ target_tipo │               │    │
│  │  │ descripcion │                      │ target_id   │               │    │
│  │  │ tipo        │                      │ tipo        │               │    │
│  │  │ impacto     │                      │ nivel       │               │    │
│  │  │ estado      │                      │ mensaje     │               │    │
│  │  │ iniciativa_id                      │ activa      │               │    │
│  │  └─────────────┘                      └─────────────┘               │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Esquemas de Base de Datos

| Esquema | Propósito |
|---------|-----------|
| `gore_autenticacion` | Usuarios, sesiones |
| `gore_organizacion` | Divisiones, estructura |
| `gore_inversion` | IPR (iniciativas) |
| `gore_financiero` | Convenios, cuotas |
| `gore_actos` | Resoluciones |
| `gore_trabajo` | Ítems de trabajo, problemas, alertas |

### 4.3 Tablas Principales

#### 4.3.1 gore_trabajo.item

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID | PK |
| codigo | VARCHAR(20) | Código único (IT-2026-00001) |
| titulo | VARCHAR(500) | Título descriptivo |
| descripcion | TEXT | Descripción detallada |
| padre_id | UUID | FK a item (jerarquía) |
| responsable_id | UUID | FK a usuario |
| division_id | UUID | FK a division |
| estado | VARCHAR(20) | PENDIENTE/EN_PROGRESO/BLOQUEADO/COMPLETADO/VERIFICADO/CANCELADO |
| fecha_limite | DATE | Fecha límite |
| prioridad | VARCHAR(10) | URGENTE/NORMAL/BAJA |
| iniciativa_id | UUID | FK a iniciativa |
| convenio_id | UUID | FK a convenio |
| resolucion_id | UUID | FK a resolucion |
| problema_id | UUID | FK a problema |
| proceso_ref | VARCHAR(100) | Referencia a proceso DIPIR |
| origen_tipo | VARCHAR(30) | MANUAL/REUNION/PROBLEMA/ALERTA/SISTEMA |
| tags | TEXT[] | Etiquetas |
| created_at | TIMESTAMPTZ | Fecha creación |
| updated_at | TIMESTAMPTZ | Última actualización |
| completed_at | TIMESTAMPTZ | Fecha completado |

#### 4.3.2 gore_trabajo.problema

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID | PK |
| codigo | VARCHAR(20) | Código único (PR-2026-00001) |
| descripcion | TEXT | Descripción del problema |
| tipo | VARCHAR(30) | TECNICO/FINANCIERO/ADMINISTRATIVO/LEGAL/COORDINACION/EXTERNO |
| impacto | VARCHAR(30) | BLOQUEA_PAGO/RETRASA_OBRA/RETRASA_CONVENIO/RIESGO_RENDICION/OTRO |
| estado | VARCHAR(30) | ABIERTO/EN_GESTION/RESUELTO/CERRADO_SIN_RESOLVER |
| iniciativa_id | UUID | FK a iniciativa |
| convenio_id | UUID | FK a convenio |
| detectado_por_id | UUID | FK a usuario |
| solucion_aplicada | TEXT | Descripción de solución |
| resuelto_por_id | UUID | FK a usuario |
| resuelto_en | TIMESTAMPTZ | Fecha resolución |

#### 4.3.3 gore_trabajo.alerta

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | UUID | PK |
| target_tipo | VARCHAR(30) | IPR/CONVENIO/RESOLUCION/ITEM/PROBLEMA |
| target_id | UUID | ID de la entidad target |
| iniciativa_id | UUID | FK a iniciativa (para navegación) |
| tipo | VARCHAR(50) | Tipo de alerta |
| nivel | VARCHAR(20) | INFO/ATENCION/ALTO/CRITICO |
| mensaje | TEXT | Mensaje descriptivo |
| activa | BOOLEAN | Si está activa |
| atendida_por_id | UUID | FK a usuario |
| atendida_en | TIMESTAMPTZ | Fecha atención |
| accion_tomada | TEXT | Descripción de acción |

---

## 5. ESPECIFICACIÓN DE API

### 5.1 Convenciones Generales

- **Base URL:** `/api/v1`
- **Formato:** JSON
- **Autenticación:** Bearer token (JWT)
- **Paginación:** `?page=1&per_page=20`
- **Filtros:** Query parameters
- **Ordenamiento:** `?sort=campo&order=asc|desc`

### 5.2 Respuestas Estándar

**Éxito (200/201):**
```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

**Error (4xx/5xx):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "El campo 'titulo' es requerido",
    "details": [...]
  }
}
```

### 5.3 Endpoints de Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/login` | Iniciar sesión |
| POST | `/auth/logout` | Cerrar sesión |
| POST | `/auth/refresh` | Refrescar token |
| POST | `/auth/password/reset-request` | Solicitar reset |
| POST | `/auth/password/reset` | Resetear contraseña |

### 5.4 Endpoints de Trabajo

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/trabajo` | Listar ítems de trabajo |
| GET | `/trabajo/{id}` | Obtener ítem |
| POST | `/trabajo` | Crear ítem |
| PATCH | `/trabajo/{id}` | Actualizar ítem |
| POST | `/trabajo/{id}/completar` | Marcar completado |
| POST | `/trabajo/{id}/verificar` | Verificar (jefe) |
| POST | `/trabajo/{id}/bloquear` | Bloquear |
| POST | `/trabajo/{id}/desbloquear` | Desbloquear |
| POST | `/trabajo/{id}/reasignar` | Reasignar |
| GET | `/trabajo/{id}/historial` | Historial |
| GET | `/trabajo/mi-trabajo` | Mi trabajo |
| GET | `/trabajo/division/{id}` | Trabajo de división |
| GET | `/trabajo/ipr/{id}` | Trabajo de IPR |

### 5.5 Endpoints de Problemas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/problemas` | Listar problemas |
| GET | `/problemas/{id}` | Obtener problema |
| POST | `/problemas` | Registrar problema |
| PATCH | `/problemas/{id}` | Actualizar problema |
| POST | `/problemas/{id}/resolver` | Resolver |
| POST | `/problemas/{id}/crear-trabajo` | Crear trabajo |

### 5.6 Endpoints de Alertas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/alertas` | Listar alertas activas |
| POST | `/alertas/{id}/atender` | Atender alerta |

### 5.7 Endpoints de IPR

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/ipr` | Listar IPR |
| GET | `/ipr/{id}` | Obtener IPR completa |
| PATCH | `/ipr/{id}` | Actualizar IPR |
| POST | `/ipr/{id}/avance` | Registrar avance |
| GET | `/ipr/{id}/trabajo` | Trabajo de IPR |
| GET | `/ipr/{id}/problemas` | Problemas de IPR |
| GET | `/ipr/{id}/alertas` | Alertas de IPR |

### 5.8 Endpoints de Dashboards

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dashboard/ejecutivo` | Dashboard admin regional |
| GET | `/dashboard/division/{id}` | Dashboard división |
| GET | `/dashboard/personal` | Dashboard personal |

### 5.9 Endpoints de Administración

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/admin/usuarios` | Listar usuarios |
| POST | `/admin/usuarios` | Crear usuario |
| PATCH | `/admin/usuarios/{id}` | Editar usuario |
| DELETE | `/admin/usuarios/{id}` | Desactivar usuario |
| POST | `/admin/usuarios/{id}/reset-password` | Reset password |
| GET | `/admin/divisiones` | Listar divisiones |
| POST | `/admin/divisiones` | Crear división |
| PATCH | `/admin/divisiones/{id}` | Editar división |
| POST | `/admin/importar/ipr` | Importar IPR |
| POST | `/admin/importar/convenios` | Importar convenios |

---

## 6. ESPECIFICACIONES UI/UX

### 6.1 Estructura de Navegación

```
┌─────────────────────────────────────────────────────────────────┐
│  NAVEGACIÓN PRINCIPAL                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ADMIN_SISTEMA:                                                 │
│  ├── Dashboard                                                  │
│  ├── Configuración                                              │
│  │   ├── Usuarios                                               │
│  │   ├── Divisiones                                             │
│  │   ├── Importar Datos                                         │
│  │   └── Sistema                                                │
│  └── Monitoreo                                                  │
│                                                                  │
│  ADMIN_REGIONAL:                                                │
│  ├── Dashboard Ejecutivo                                        │
│  ├── IPR                                                        │
│  │   ├── Todas                                                  │
│  │   └── Con Problemas                                          │
│  ├── Trabajo                                                    │
│  │   ├── Todo                                                   │
│  │   ├── Vencido                                                │
│  │   └── Por Verificar                                          │
│  ├── Problemas                                                  │
│  ├── Alertas                                                    │
│  └── Reportes                                                   │
│                                                                  │
│  JEFE_DIVISION:                                                 │
│  ├── Dashboard División                                         │
│  ├── Mi División                                                │
│  │   ├── IPR                                                    │
│  │   ├── Trabajo                                                │
│  │   └── Equipo                                                 │
│  ├── Problemas                                                  │
│  └── Alertas                                                    │
│                                                                  │
│  ENCARGADO:                                                     │
│  ├── Mi Trabajo                                                 │
│  ├── Mis IPR                                                    │
│  └── Alertas                                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Pantallas Principales

#### 6.2.1 Dashboard Ejecutivo

```
┌─────────────────────────────────────────────────────────────────┐
│  DASHBOARD EJECUTIVO                                    [fecha] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │   127    │ │    12    │ │    8     │ │    3     │           │
│  │ IPR Total│ │c/Problemas│ │T.Vencido │ │ Críticas │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                  │
│  ALERTAS CRÍTICAS                                    [ver todas]│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ! Gimnasio Coihueco: Obra 100% terminada, pago pendiente   ││
│  │ ! Televigilancia: Convenio vence en 15 días                 ││
│  │ ! CESFAM Quirihue: Rendición vencida hace 10 días          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  PROBLEMAS CRÍTICOS                                  [ver todos]│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ PR-2026-00012 | Gimnasio Coihueco | Cuota diferida         ││
│  │ PR-2026-00015 | Televigilancia    | Proveedor retrasado    ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  TENDENCIA SEMANAL                                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ [Gráfico: Problemas nuevos vs resueltos]                    ││
│  │ [Gráfico: Trabajo completado por día]                       ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.2.2 Mi Trabajo (Encargado)

```
┌─────────────────────────────────────────────────────────────────┐
│  MI TRABAJO                              [+ Captura rápida]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Filtros: [Estado ▼] [IPR ▼] [Fecha ▼]              [Buscar...]│
│                                                                  │
│  VENCIDOS (2)                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ⚠ IT-2026-00145 | Gestionar CDP cuota 2              -3d   ││
│  │   Gimnasio Coihueco | PENDIENTE                             ││
│  │                                                              ││
│  │ ⚠ IT-2026-00132 | Preparar informe avance            -5d   ││
│  │   Estadio Bulnes | EN_PROGRESO                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ESTA SEMANA (4)                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ● IT-2026-00156 | Enviar memo a DAF                   hoy   ││
│  │   Gimnasio Coihueco | PENDIENTE                             ││
│  │                                                              ││
│  │ ● IT-2026-00162 | Visita terreno                      mié   ││
│  │   Piscina Quillón | PENDIENTE                               ││
│  │                                                              ││
│  │ ● IT-2026-00170 | Revisar rendición                   vie   ││
│  │   Centro Cultural | PENDIENTE                               ││
│  │                                                              ││
│  │ ● IT-2026-00175 | Actualizar BIP                      vie   ││
│  │   (3 proyectos) | PENDIENTE                                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.2.3 Ficha IPR

```
┌─────────────────────────────────────────────────────────────────┐
│  ← IPR | GIMNASIO MUNICIPAL COIHUECO            [Exportar PDF] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Código: 30481212 | FNDR | Responsable: Juan Pérez (DIPIR)     │
│  Estado: ⚠ CRÍTICO - Obra terminada, pago pendiente            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ TABS: [Resumen] [Convenios] [Trabajo] [Problemas] [Historial]│
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  RESUMEN                                                        │
│  ┌────────────────────┬────────────────────┐                   │
│  │ Monto Aprobado     │ $1.200.000.000     │                   │
│  │ Avance Físico      │ ████████████ 100%  │                   │
│  │ Avance Financiero  │ ████████░░░░ 65%   │                   │
│  │ Saldo Pendiente    │ $420.000.000       │                   │
│  │ Término Convenio   │ 2026-03-15         │                   │
│  └────────────────────┴────────────────────┘                   │
│                                                                  │
│  ALERTAS ACTIVAS                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ! CRÍTICO: Obra terminada (100%) con pago pendiente ($420M)││
│  │ ! ALTO: Convenio vence en 48 días                           ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  PROBLEMAS ABIERTOS (1)                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ PR-2026-00012 | FINANCIERO | Cuota diferida a 2026         ││
│  │ Impacto: BLOQUEA_PAGO | Estado: EN_GESTION                  ││
│  │ [Ver detalle] [Crear trabajo]                               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  TRABAJO ASOCIADO (5)                            [+ Nuevo]     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ⚠ IT-2026-00145 | Gestionar CDP cuota 2 | PENDIENTE  -3d   ││
│  │ ● IT-2026-00156 | Enviar memo a DAF     | PENDIENTE   hoy   ││
│  │ ✓ IT-2026-00089 | Recepcionar obra      | VERIFICADO  15d   ││
│  │ ✓ IT-2026-00075 | Tramitar estado pago  | VERIFICADO  22d   ││
│  │ ✓ IT-2026-00062 | Preparar EP cuota 1   | VERIFICADO  30d   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Componentes Reutilizables

| Componente | Descripción |
|------------|-------------|
| `ItemCard` | Tarjeta de ítem de trabajo con estado, vencimiento, vinculación |
| `AlertBadge` | Badge de alerta con nivel (color) y tipo |
| `ProblemaBadge` | Badge de problema con tipo e impacto |
| `EstadoBadge` | Badge de estado con color según valor |
| `IPRMini` | Vista compacta de IPR para referencias |
| `UserAvatar` | Avatar de usuario con nombre |
| `DateRelative` | Fecha relativa ("hace 3 días", "en 2 días") |
| `ProgressBar` | Barra de progreso con porcentaje |
| `FilterBar` | Barra de filtros configurable |
| `DataTable` | Tabla con ordenamiento y paginación |
| `Modal` | Modal para formularios y confirmaciones |
| `Toast` | Notificación temporal de acciones |

### 6.4 Paleta de Colores

| Color | Uso | Código |
|-------|-----|--------|
| Primario | Acciones principales, links | #2563EB |
| Éxito | Completado, verificado | #16A34A |
| Advertencia | Atención, próximo a vencer | #CA8A04 |
| Error | Crítico, vencido, bloqueado | #DC2626 |
| Info | Informativo | #0891B2 |
| Neutral | Texto, bordes | #6B7280 |
| Background | Fondo | #F9FAFB |

---

## 7. ARQUITECTURA TÉCNICA

### 7.1 Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| Frontend | React 18 + TypeScript |
| UI Framework | Tailwind CSS + Headless UI |
| State Management | React Query + Zustand |
| Backend | Python 3.11 + Flask |
| ORM | SQLAlchemy 2.0 |
| Base de Datos | PostgreSQL 15 |
| Cache | Redis 7 |
| Task Queue | Celery |
| Servidor Web | Gunicorn + Nginx |
| Contenedores | Docker + Docker Compose |

### 7.2 Estructura de Proyecto

```
goreos/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── stores/
│   │   └── utils/
│   ├── public/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── models/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── utils/
│   ├── migrations/
│   ├── tests/
│   └── requirements.txt
├── docker/
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   └── docker-compose.yml
└── docs/
```

### 7.3 Diagrama de Despliegue

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRODUCCIÓN                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐                                                │
│  │   Nginx     │  ← SSL, static files, reverse proxy            │
│  │   (443)     │                                                │
│  └──────┬──────┘                                                │
│         │                                                        │
│  ┌──────┴──────┐                                                │
│  │             │                                                │
│  ▼             ▼                                                │
│  ┌─────────┐   ┌─────────┐                                      │
│  │Frontend │   │ Backend │                                      │
│  │ (React) │   │ (Flask) │ ← 2 réplicas Gunicorn               │
│  └─────────┘   └────┬────┘                                      │
│                     │                                            │
│         ┌───────────┼───────────┐                               │
│         │           │           │                               │
│         ▼           ▼           ▼                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│  │PostgreSQL│ │  Redis   │ │  Celery  │                        │
│  │   (DB)   │ │ (Cache)  │ │ (Tasks)  │                        │
│  └──────────┘ └──────────┘ └──────────┘                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. PLAN DE IMPLEMENTACIÓN

### 8.1 Fases de Desarrollo

```
┌─────────────────────────────────────────────────────────────────┐
│                    FASES DE IMPLEMENTACIÓN                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FASE 1: FUNDAMENTOS                                            │
│  ─────────────────────                                          │
│  • Setup de proyecto (Docker, CI/CD)                            │
│  • Modelo de datos base                                         │
│  • Autenticación y autorización                                 │
│  • CRUD de usuarios y divisiones                                │
│  • Importación de IPR y convenios                               │
│                                                                  │
│  FASE 2: TRABAJO UNIFICADO                                      │
│  ─────────────────────────                                      │
│  • CRUD de ítems de trabajo                                     │
│  • Flujo de estados                                             │
│  • Jerarquía padre-hijo                                         │
│  • Vinculación a entidades formales                             │
│  • Vista "Mi Trabajo"                                           │
│  • Vista "Trabajo de División"                                  │
│                                                                  │
│  FASE 3: IPR Y FICHA COMPLETA                                   │
│  ─────────────────────────────                                  │
│  • Ficha IPR completa                                           │
│  • Convenios y resoluciones                                     │
│  • Vista de trabajo por IPR                                     │
│  • Registro de avance                                           │
│                                                                  │
│  FASE 4: PROBLEMAS Y ALERTAS                                    │
│  ─────────────────────────────                                  │
│  • CRUD de problemas                                            │
│  • Flujo de resolución                                          │
│  • Motor de alertas automáticas                                 │
│  • Notificaciones                                               │
│                                                                  │
│  FASE 5: DASHBOARDS Y REPORTES                                  │
│  ─────────────────────────────                                  │
│  • Dashboard ejecutivo                                          │
│  • Dashboard de división                                        │
│  • Dashboard personal                                           │
│  • Exportación de reportes                                      │
│                                                                  │
│  FASE 6: PULIDO Y DESPLIEGUE                                    │
│  ─────────────────────────────                                  │
│  • Pruebas de usuario                                           │
│  • Corrección de bugs                                           │
│  • Optimización de rendimiento                                  │
│  • Documentación                                                │
│  • Despliegue a producción                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Priorización de Requisitos

| Prioridad | Requisitos |
|-----------|------------|
| **P1 - Crítico** | RF-001, RF-002, RF-010, RF-020-027, RF-040-042, RF-060-062 |
| **P2 - Alto** | RF-003, RF-011-013, RF-028-030, RF-043, RF-050-053 |
| **P3 - Medio** | RF-004, RF-014, RF-070-072 |
| **P4 - Bajo** | RF-080-082 |

### 8.3 Criterios de Aceptación por Fase

#### Fase 1 - Fundamentos
- [ ] Usuario puede iniciar sesión
- [ ] Admin puede crear usuarios
- [ ] Admin puede crear divisiones
- [ ] Admin puede importar IPR desde Excel
- [ ] Tests de integración pasan

#### Fase 2 - Trabajo Unificado
- [ ] Usuario puede crear ítem de trabajo
- [ ] Usuario puede completar ítem
- [ ] Jefe puede verificar ítem completado
- [ ] Usuario puede ver "Mi Trabajo"
- [ ] Jefe puede ver "Trabajo de División"

#### Fase 3 - IPR y Ficha
- [ ] Usuario puede ver ficha IPR completa
- [ ] Usuario puede registrar avance
- [ ] Sistema vincula trabajo a IPR
- [ ] Sistema muestra convenios y resoluciones

#### Fase 4 - Problemas y Alertas
- [ ] Usuario puede registrar problema
- [ ] Sistema genera alertas automáticas
- [ ] Usuario puede atender alertas
- [ ] Problemas actualizan nivel de alerta de IPR

#### Fase 5 - Dashboards
- [ ] Admin Regional ve dashboard ejecutivo
- [ ] Jefe ve dashboard de división
- [ ] Encargado ve dashboard personal
- [ ] Usuario puede exportar reportes

---

## 9. MAPEO DE CASOS DE USO

### 9.1 Administrador Regional (AR)

| ID | Caso de Uso | Endpoint Principal | Pantalla |
|----|-------------|-------------------|----------|
| AR-01 | Ver dashboard ejecutivo | GET /dashboard/ejecutivo | Dashboard Ejecutivo |
| AR-02 | Revisar nudos críticos | GET /problemas?impacto=CRITICO | Lista Problemas |
| AR-03 | Preparar reunión semanal | GET /dashboard/ejecutivo + /alertas | Dashboard + Alertas |
| AR-04 | Conducir reunión | POST /trabajo (origen=REUNION) | Modal Crear Trabajo |
| AR-05 | Verificar trabajo | POST /trabajo/{id}/verificar | Ficha Trabajo |
| AR-06 | Entrevistar responsable | GET /ipr/{id} + /trabajo/usuario/{id} | Ficha IPR + Mi Trabajo |
| AR-07 | Generar informe | GET /reportes/ejecutivo/pdf | Reportes |
| AR-08 | Ver cumplimiento división | GET /dashboard/division/{id} | Dashboard División |

### 9.2 Jefe de División (JD)

| ID | Caso de Uso | Endpoint Principal | Pantalla |
|----|-------------|-------------------|----------|
| JD-01 | Ver resumen de división | GET /dashboard/division/{id} | Dashboard División |
| JD-02 | Ver estado de equipo | GET /trabajo/division/{id}?group=responsable | Trabajo División |
| JD-03 | Ver trabajo vencido | GET /trabajo/division/{id}?vencido=true | Trabajo División |
| JD-04 | Asignar trabajo | POST /trabajo + POST /trabajo/{id}/reasignar | Modal Crear/Reasignar |
| JD-05 | Verificar trabajo | POST /trabajo/{id}/verificar | Ficha Trabajo |
| JD-06 | Registrar problema | POST /problemas | Modal Crear Problema |
| JD-07 | Coordinar con otra división | POST /trabajo (otra división) | Modal Crear Trabajo |

### 9.3 Encargado Operativo (EO)

| ID | Caso de Uso | Endpoint Principal | Pantalla |
|----|-------------|-------------------|----------|
| EO-01 | Ver mis compromisos | GET /trabajo/mi-trabajo | Mi Trabajo |
| EO-02 | Ver mis IPR | GET /ipr?responsable=me | Mis IPR |
| EO-03 | Actualizar compromiso | PATCH /trabajo/{id} | Ficha Trabajo |
| EO-04 | Completar compromiso | POST /trabajo/{id}/completar | Ficha Trabajo |
| EO-05 | Registrar avance | POST /ipr/{id}/avance | Modal Avance |
| EO-06 | Registrar problema | POST /problemas | Modal Crear Problema |
| EO-07 | Ver ficha IPR | GET /ipr/{id} | Ficha IPR |
| EO-08 | Ver historial | GET /trabajo/{id}/historial | Tab Historial |

### 9.4 Administrador del Sistema (AS)

| ID | Caso de Uso | Endpoint Principal | Pantalla |
|----|-------------|-------------------|----------|
| AS-01 | Crear división | POST /admin/divisiones | Modal División |
| AS-02 | Editar división | PATCH /admin/divisiones/{id} | Modal División |
| AS-03 | Crear usuario | POST /admin/usuarios | Modal Usuario |
| AS-04 | Editar usuario | PATCH /admin/usuarios/{id} | Modal Usuario |
| AS-05 | Desactivar usuario | DELETE /admin/usuarios/{id} | Lista Usuarios |
| AS-06 | Restablecer contraseña | POST /admin/usuarios/{id}/reset-password | Lista Usuarios |
| AS-07 | Importar IPR | POST /admin/importar/ipr | Importar Datos |
| AS-08 | Importar convenios | POST /admin/importar/convenios | Importar Datos |
| AS-09 | Asignación masiva | POST /admin/ipr/asignar-masivo | Lista IPR |
| AS-10 | Configurar alertas | PATCH /admin/alertas/config | Configuración |
| AS-11 | Ver logs del sistema | GET /admin/logs | Monitoreo |
| AS-12 | Gestionar backups | GET /admin/backups | Monitoreo |

---

## 10. ANEXOS

### 10.1 Glosario

| Término | Definición |
|---------|------------|
| **IPR** | Iniciativa de Inversión Pública Regional. Proyecto de inversión financiado por el GORE. |
| **Convenio** | Acuerdo legal que formaliza la transferencia de recursos para ejecutar una IPR. |
| **Resolución** | Acto administrativo que aprueba, modifica o cierra un convenio o IPR. |
| **Ítem de Trabajo** | Unidad de trabajo asignable a un responsable, con estado y fecha límite. |
| **Problema** | Situación que afecta el flujo normal de una IPR o convenio. |
| **Alerta** | Notificación automática generada por el sistema ante condiciones predefinidas. |
| **DIPIR** | División de Inversión Pública Regional del GORE. |
| **DAF** | División de Administración y Finanzas del GORE. |
| **BIP** | Banco Integrado de Proyectos. Sistema nacional de registro de proyectos. |

### 10.2 Referencias

- Diseño conceptual: `/Users/felixsanhueza/Developer/goreos/gestion.md`
- Casos de uso detallados: `/Users/felixsanhueza/fx_felixiando/para_titi/casos_uso.md`
- Estructura GORE Ñuble: `/Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/intro/omega_gore_nuble_mermaid.md`
- Procesos DIPIR: `/Users/felixsanhueza/Developer/gorenuble/staging/procesos_dipir/dipir_ssot_koda.yaml`

---

**Fin del Documento**
