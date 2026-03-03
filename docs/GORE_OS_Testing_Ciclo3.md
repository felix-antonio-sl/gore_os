# GORE_OS — Documento de Testeo

**Fecha**: 2026-03-03
**Version**: 7.0 (Ciclo 1-6 + Tests + Confrontacion + Ciclo 19 SISREC)
**Objetivo**: Guia completa para testeo funcional de GORE_OS incluyendo el workflow multi-rol SISREC del Ciclo 19.

---

## 1. Acceso al Sistema

### 1.1 URLs de Servicio

| Servicio | URL |
|----------|-----|
| Frontend (Web) | http://localhost:3000 |
| API (Backend) | http://localhost:8000 |
| Swagger/Docs | http://localhost:8000/api/docs |
| Health Check | http://localhost:8000/api/health |

### 1.2 Iniciar Servicios

```bash
# Iniciar API + Web (BD ya corriendo en red visor_model_default)
docker compose up -d api web

# Verificar
curl http://localhost:8000/api/health     # {"status": "ok"}
curl -I http://localhost:3000             # 307 redirect to /login

# Cargar datos demo (opcional, prefijo DEMO-)
docker exec -i goreos_db psql -U goreos -d goreos_model \
  < model/model_goreos/sql/goreos_seed_demo_ciclo2.sql
```

### 1.3 Credenciales de Prueba

**Password para todos los usuarios**: `admin123`

#### Usuarios Operativos

| Email | Rol | Poblacion | Acceso Especial |
|-------|-----|-----------|-----------------|
| `admin@goreos.cl` | ADMIN_SISTEMA | operativa | Admin usuarios/divisiones, acceso total |
| `regional@goreos.cl` | ADMIN_REGIONAL | operativa | Dashboard ejecutivo, acceso global |
| `jefe.daf@goreos.cl` | JEFE_DIVISION | operativa | Mi Division, verificar compromisos de su div |
| `encargado.daf@goreos.cl` | ENCARGADO | operativa | Mis Compromisos, completar compromisos propios |

#### Usuarios DGI

| Email | Rol | Poblacion | Cockpit Especializado |
|-------|-----|-----------|----------------------|
| `jefe.dgi@goreos.cl` | JEFE_DGI | dgi | Semaforo 5 dimensiones, equipo, alertas criticas |
| `control.gestion@goreos.cl` | ESP_CONTROL_GESTION | dgi | Fuentes datos, indicadores alerta, cola trabajo |
| `procesos@goreos.cl` | ESP_PROCESOS | dgi | Iniciativas, modelos BPMN, agenda |
| `td@goreos.cl` | ESP_TD | dgi | Cumplimiento, decretos, velocidad |

---

## 2. Estado del Desarrollo

### 2.1 Funcionalidad Completada (Ciclo 1 + 2 + 3 + 4)

| Modulo | Estado | Ciclo | Descripcion |
|--------|--------|-------|-------------|
| Login/Auth | Completo | C1 | JWT + 8 roles (4 op + 4 DGI) |
| Dashboard operativo | Completo | C1+C3+C4 | Role-aware con KPIs, desglose por division, charts recharts |
| IPR lista + detalle | Completo | C1+C6 | Paginado, filtros (incl. assignee_id), 6 tabs: compromisos/problemas/alertas/convenios/CDPs/avances |
| IPR crear | Completo | C3 | Form completo con auto-generacion de codigo BIP |
| IPR editar | **Nuevo C4** | C4 | Edicion inline nombre/descripcion/tipo/estado (roles admin) |
| IPR asignar responsable | Completo | C3 | Boton en detalle IPR para roles admin |
| IPR registrar avance | Completo | C3 | Tab Avances en detalle IPR + form progress_report |
| Compromisos lista | Completo | C1 | Paginado, filtros, drawer con historial + acciones |
| Compromisos crear | Completo | C3 | Form con tipo, responsable, fecha, IPR asociada |
| Compromisos acciones | Completo | C1 | Completar, verificar, devolver con historial |
| Problemas lista | Completo | C1 | Paginado, filtros por estado y tipo |
| Problemas crear | Completo | C3 | Form con IPR, tipo, impacto, descripcion |
| Problemas resolver/cerrar | Completo | C3 | Drawer con acciones: En Gestion, Resolver, Cerrar |
| Alertas | Completo | C1 | Lista con severidad, atencion |
| Presupuesto | Completo | C2+C4+C6 | CRUD programas, resumen, CDPs, edicion montos inline, filtro division frontend |
| Convenios | Completo | C2+C4+C6 | CRUD convenios + cuotas inline (crear/registrar pago), edicion estado/monto/fecha, filtro orphan |
| Mi Division | Completo | C3 | Dashboard JEFE con carga por persona |
| Mis Compromisos | Completo | C3 | Vista personal agrupada (vencidos/semana/pendientes) |
| Dashboard ejecutivo | Completo | C3 | Desglose por division con metricas comparativas |
| Admin usuarios | Completo | C3 | CRUD completo + toggle activo + reset password |
| Admin divisiones | Completo | C3 | CRUD con conteo de usuarios |
| Reuniones de crisis | Completo | C3 | Modulo completo: crear, preparar, conducir, finalizar |
| Busqueda global | **Nuevo C4** | C4 | Dialog ⌘K con resultados agrupados por tipo de entidad |
| Notificaciones bell | **Nuevo C4** | C4 | Popover con alertas activas recientes y badge contador |
| CSV Export | **Nuevo C4** | C4 | Exportar datos desde DGI Explorer a CSV |
| Dashboard charts | **Nuevo C4** | C4 | 3 charts recharts: ejecucion presupuestaria, compromisos, alertas |
| DGI gauges | **Nuevo C4** | C4 | Gauges semaforo en cockpit DGI con iconos visuales |
| DGI Cockpits | Completo | C2 | 4 cockpits por rol DGI |
| DGI Indicadores | Completo | C2 | Semaforo 5 dimensiones, refresh desde BD real |
| DGI Iniciativas | Completo | C2+C6 | Kanban con WIP limits, paginacion opcional |
| DGI Informes | Completo | C2 | 4 tipos, 6 secciones auto-populadas |
| Navegacion bidireccional | **Nuevo C6** | C6 | Links clickeables entre entidades satelite e IPR en 6 paginas |
| Timeline problemas | **Nuevo C6** | C6 | Historial visual de estados en drawer de problemas |
| SISREC Workflow | **Nuevo C19** | C19 | Rendiciones multi-rol: 8 estados, RTF→UCR, audit trail, SLA |
| StatusBadge rendiciones | **Nuevo C19** | C19 | 6 badges para estados SISREC (RTF, UCR, observada, aprobada, rechazada) |
| SLA rendiciones | **Nuevo C19** | C19 | Indicador de vencimiento + endpoint `/rendiciones/vencidas` |
| Art. 18 CGR fix | **Nuevo C19** | C19 | Bloqueo de pago extendido a paid_amount/paid_at |

### 2.5 Resumen de Nuevas Funcionalidades Ciclo 19 (SISREC Multi-Role Workflow)

| # | Feature | Descripcion | Wave |
|---|---------|-------------|------|
| S1 | State machine multi-rol | 8 estados: PENDIENTE → EN_REVISION_RTF → VISADA_RTF → EN_REVISION_UCR → APROBADA/RECHAZADA + OBSERVADA loop | A+B |
| S2 | Autorizacion por transicion | Cada transicion tiene roles permitidos: operativa inicia/reenvia, DGI visa/aprueba/rechaza | B |
| S3 | Audit trail | `core.rendition_history` + trigger + comment por transicion | A+B |
| S4 | SLA detection | 7 dias RTF, 2 dias UCR. Campo `is_overdue` + `days_in_state` computados. Endpoint `/vencidas` | B |
| S5 | Amount field | Campo `amount` (monto rendido) en crear y editar rendicion | A+B+C |
| S6 | Art. 18 CGR extension | PATCH cuotas ahora verifica rendiciones pendientes tambien en paid_amount/paid_at | B |
| S7 | StatusBadge 6 cases | EN_REVISION_RTF (amber), VISADA_RTF (blue), EN_REVISION_UCR (indigo), OBSERVADA (orange), APROBADA (green), RECHAZADA (red) | C |
| S8 | History timeline | TimelineHistory reutilizado en drawer de rendiciones con historial de transiciones | C |
| S9 | Comment textarea | Textarea para comentario opcional en cada transicion de estado | C |
| S10 | 18 integration tests | State machine, role restrictions, history, SLA, amount en `test_sisrec.py` | D |

### 2.2 Resumen de Nuevas Funcionalidades Ciclo 3

| # | Gap | Descripcion | Wave |
|---|-----|-------------|------|
| G1 | Form crear compromiso | `/compromisos/nuevo` | W1 |
| G2 | Form crear problema | `/problemas/nuevo` | W1 |
| G3 | Resolver/cerrar problema | Botones en drawer de problemas | W1 |
| G4 | Crear IPR | `/ipr/nuevo` + `POST /api/ipr` | W2 |
| G5 | Asignar responsable IPR | Boton en detalle IPR + `PATCH /api/ipr/{id}` | W2 |
| G6 | Registrar avance IPR | Tab Avances + `POST /api/ipr/{id}/avances` | W2 |
| G7 | Historial avance IPR | `GET /api/ipr/{id}/avances` en tab | W2 |
| G8 | Admin usuarios CRUD | `/admin/usuarios` + router completo | W3 |
| G9 | Admin divisiones CRUD | `/admin/divisiones` + endpoints | W3 |
| G10 | Mi Division | `/mi-division` + `GET /api/dashboard/mi-division` | W4 |
| G11 | Mis Compromisos | `/mis-compromisos` + `GET /api/dashboard/mis-compromisos` | W4 |
| G12 | Reuniones de crisis | Modulo completo: `/reuniones` + 8 endpoints API | W5 |
| G13 | Dashboard ejecutivo | `/api/dashboard/ejecutivo` con desglose divisiones | W4 |

### 2.3 Resumen de Nuevas Funcionalidades Ciclo 4

| # | Feature | Descripcion | Tipo |
|---|---------|-------------|------|
| F1 | CSV Export | Exportar datos desde DGI Explorer a archivo CSV | UX |
| F2 | Notificaciones Bell | Badge con contador + popover alertas activas en header | UX |
| F3 | Busqueda global ⌘K | Dialog de busqueda con resultados agrupados (IPR, compromisos, problemas) | UX |
| F4 | Dashboard Charts | 3 charts recharts: ejecucion presupuestaria (bar), compromisos por estado (donut), alertas por severidad (horizontal bar) | Charts |
| F5 | DGI Gauges | Iconos semaforo visuales en cockpit Jefe DGI | Charts |
| F6 | IPR Edit | Edicion de nombre, descripcion, tipo, estado para ADMIN_SISTEMA y ADMIN_REGIONAL | CRUD |
| F7 | Presupuesto Edit | Edicion inline de montos (inicial, vigente, comprometido, devengado, pagado) | CRUD |
| F8 | Convenios Edit | Edicion de estado, monto, fecha termino en drawer de convenio | CRUD |

### 2.4 Resumen de Nuevas Funcionalidades Ciclo 6 (Auditoria Ontologica)

| # | Feature | Descripcion | Tier |
|---|---------|-------------|------|
| R1 | Navegacion bidireccional | Links clickeables IPR ↔ satelites en 6 drawers/paginas | TIER 1 |
| R2 | AlertCard multi-subject | AlertCard navega a IPR, compromiso, problema o convenio segun subject_type | TIER 1 |
| R3 | Reunion topics BIP link | Badge BIP en temas de reunion es clickeable hacia IPR detail | TIER 1 |
| R4 | Filtro assignee_id en IPR | `GET /api/ipr?assignee_id=X` filtra por usuario asignado | TIER 2 |
| R5 | Filtro orphan en convenios | `GET /api/convenios?orphan=true` devuelve convenios sin IPR vinculado | TIER 2 |
| R6 | Paginacion DGI initiatives | `GET /api/dgi/initiatives?page=1&page_size=N` paginacion opcional | TIER 2 |
| R7 | Cuotas crear inline | Formulario inline en drawer convenio para crear cuota | TIER 3 |
| R8 | Cuotas registrar pago | Formulario inline por cuota para registrar pago con monto y referencia | TIER 3 |
| R9 | Filtro division presupuesto | Select division en FilterBar de presupuesto (carga desde catalogs) | TIER 3 |
| R10 | Tab CDPs en IPR detail | Nuevo tab CDPs en IPR detail + endpoint `GET /api/presupuesto/cdps-por-ipr/{id}` | TIER 3 |
| R11 | Timeline problemas | Historial visual de estados (detectado → en gestion → resuelto/cerrado) en drawer | TIER 3 |

---

## 3. Navegacion por Rol

### 3.1 Barra Lateral — Usuarios Operativos

**Todos los roles operativos ven**:
- Inicio (Dashboard)
- IPR
- Compromisos
- Problemas
- Alertas
- Presupuesto
- Convenios
- Reuniones

**Adicional segun rol**:
- **JEFE_DIVISION**: + Mi Division
- **ENCARGADO**: + Mis Compromisos
- **ADMIN_SISTEMA**: + Usuarios, + Divisiones

### 3.2 Barra Lateral — Usuarios DGI

- Home (Cockpit DGI)
- Alertas
- Tablero (Kanban)
- Datos (Indicadores)
- Informes

---

## 4. Casos de Prueba

### 4.1 Wave 1 — Forms CRUD

#### TC-01: Crear Compromiso
1. Login como `regional@goreos.cl` (ADMIN_REGIONAL)
2. Ir a `/compromisos`
3. Verificar que aparece boton "Nuevo Compromiso" en el header
4. Click en "Nuevo Compromiso" → navega a `/compromisos/nuevo`
5. Completar formulario:
   - Tipo: seleccionar de dropdown
   - Descripcion: "Compromiso de prueba Ciclo 3"
   - Responsable: seleccionar usuario
   - Fecha limite: fecha futura
   - IPR asociada: seleccionar una (opcional)
   - Observaciones: texto libre (opcional)
6. Click "Crear Compromiso"
7. **Esperado**: Redirect a `/compromisos`, nuevo compromiso visible en lista
8. **Verificar**: Login como `encargado.daf@goreos.cl` → NO debe ver boton "Nuevo Compromiso"

#### TC-02: Crear Problema
1. Login como `regional@goreos.cl`
2. Ir a `/problemas` → click "Nuevo Problema" → `/problemas/nuevo`
3. Completar:
   - IPR asociada: seleccionar (requerido)
   - Tipo: TECNICO / FINANCIERO / etc.
   - Impacto: ALTO / MEDIO / BAJO (opcional)
   - Descripcion: "Problema de prueba"
   - Descripcion impacto (opcional)
   - Solucion propuesta (opcional)
4. Click "Crear Problema"
5. **Esperado**: Redirect a `/problemas`, nuevo problema con estado ABIERTO

#### TC-03: Resolver Problema
1. Login como `regional@goreos.cl`
2. Ir a `/problemas` → click en un problema ABIERTO
3. **Esperado**: Drawer se abre con detalle completo (descripcion, tipo, impacto, detectado por, fecha)
4. Click "Pasar a En Gestion" → estado cambia a EN_GESTION
5. Reabrir drawer → escribir solucion aplicada → click "Resolver"
6. **Esperado**: Problema pasa a RESUELTO, muestra resuelto_por y fecha

#### TC-04: Cerrar Problema Sin Resolver
1. Con un problema en estado ABIERTO o EN_GESTION
2. En el drawer, escribir motivo → click "Cerrar sin Resolver"
3. **Esperado**: Estado cambia a CERRADO_SIN_RESOLVER

---

### 4.2 Wave 2 — IPR Escritura

#### TC-05: Crear IPR
1. Login como `admin@goreos.cl` (ADMIN_SISTEMA)
2. Ir a `/ipr` → verificar boton "Nueva IPR"
3. Click → `/ipr/nuevo`
4. Completar:
   - Codigo BIP: dejar vacio (auto-genera) o ingresar "99999999"
   - Nombre: "IPR de prueba Ciclo 3"
   - Tipo: INFRAESTRUCTURA
   - Estado: EN_EJECUCION
   - Division: seleccionar
   - Descripcion: texto libre
5. Click "Crear IPR"
6. **Esperado**: Redirect a `/ipr`, nueva IPR visible
7. **Verificar**: Login como `encargado.daf@goreos.cl` → NO debe ver boton "Nueva IPR"

#### TC-06: Asignar Responsable IPR
1. Login como `regional@goreos.cl`
2. Ir a `/ipr/{id}` (detalle de cualquier IPR)
3. Verificar boton "Asignar Responsable" en header
4. Click → drawer con select de usuarios
5. Seleccionar usuario → guardar
6. **Esperado**: Responsable asignado exitosamente

#### TC-07: Registrar Avance IPR
1. En detalle IPR, click tab "Avances"
2. Click "Registrar Avance"
3. Completar:
   - Fecha reporte: hoy
   - Avance fisico: 45 (0-100)
   - Avance financiero: 60 (0-100)
   - Descripcion: "Avance al primer trimestre"
   - Problemas detectados: (opcional)
4. Guardar
5. **Esperado**: Avance aparece en tabla con numero correlativo
6. Repetir → avance #2 con valores distintos
7. **Esperado**: Tabla muestra ambos avances ordenados por numero

---

### 4.3 Wave 3 — Administracion

#### TC-08: CRUD Usuarios
1. Login como `admin@goreos.cl`
2. Ir a `/admin/usuarios`
3. **Verificar**: Lista de usuarios con nombre, email, rol, division, estado
4. Click "Nuevo Usuario" → `/admin/usuarios/nuevo`
5. Completar:
   - Nombres: "Test"
   - Apellido paterno: "Ciclo3"
   - Email: "test.ciclo3@goreos.cl"
   - Password: "test123"
   - Rol: ENCARGADO
   - Division: seleccionar
6. Crear → volver a lista → verificar que aparece
7. Click en usuario → drawer con detalle
8. Editar nombre → guardar → verificar cambio
9. Click "Desactivar" → badge cambia a inactivo
10. Click "Activar" → badge cambia a activo
11. Click "Reset Contrasena" → ingresar nueva → guardar

#### TC-09: CRUD Divisiones
1. Login como `admin@goreos.cl`
2. Ir a `/admin/divisiones`
3. **Verificar**: Tabla con codigo, nombre, tipo, conteo usuarios, estado
4. Crear nueva division: codigo "TEST", nombre "Division Test"
5. Click en division → editar nombre → guardar
6. **Verificar**: Solo ADMIN_SISTEMA puede acceder (otros roles no ven menu)

---

### 4.4 Wave 4 — Dashboards Mejorados

#### TC-10: Mi Division (JEFE_DIVISION)
1. Login como `jefe.daf@goreos.cl`
2. Verificar que aparece "Mi Division" en sidebar
3. Click → `/mi-division`
4. **Esperado**:
   - 4 KPIs: Vencidos, Pendientes, Por Verificar, Activos
   - Seccion "Carga por Persona": tabla con badges por cada miembro del equipo
   - Seccion "Compromisos Vencidos": lista de compromisos pasados de fecha
5. **Verificar**: Login como `encargado.daf@goreos.cl` → NO ve "Mi Division" en sidebar

#### TC-11: Mis Compromisos (ENCARGADO)
1. Login como `encargado.daf@goreos.cl`
2. Verificar que aparece "Mis Compromisos" en sidebar
3. Click → `/mis-compromisos`
4. **Esperado**:
   - 4 KPIs: Vencidos, Pendientes, En Progreso, Completados (este mes)
   - Grupos: "Vencidos" (rojo), "Esta Semana" (ambar), "Pendientes" (azul)
   - Cada grupo muestra tabla con urgencia, descripcion, BIP, estado
5. **Verificar**: Login como `jefe.daf@goreos.cl` → NO ve "Mis Compromisos"

#### TC-12: Dashboard Ejecutivo (ADMIN_REGIONAL)
1. Login como `regional@goreos.cl`
2. Ir a `/dashboard`
3. **Esperado**: Ademas de KPIs y alertas normales, aparece seccion "Desglose por Division"
4. **Verificar**: Cada division muestra:
   - Nombre
   - Compromisos vencidos (badge rojo si > 0)
   - Total compromisos
   - Problemas abiertos (badge naranja si > 0)
   - Ejecucion presupuestaria (%) con color segun nivel

---

### 4.5 Wave 5 — Reuniones de Crisis

#### TC-13: Crear Reunion
1. Login como `jefe.daf@goreos.cl`
2. Ir a `/reuniones` → verificar boton "Nueva Reunion"
3. Click → `/reuniones/nueva`
4. Completar:
   - Fecha y hora: proxima semana
   - Ubicacion: "Sala de reuniones GORE"
   - Motivo: "Revision de avance trimestral"
5. Crear → redirect a detalle de reunion

#### TC-14: Preparar Reunion (Auto-sugerencias)
1. En detalle reunion (estado PROGRAMADA)
2. Click "Obtener Sugerencias" en seccion Preparar
3. **Esperado**: El sistema muestra sugerencias automaticas:
   - Alertas criticas sin resolver
   - Compromisos vencidos mas antiguos
   - Problemas abiertos > 7 dias
4. Click "Agregar" en una sugerencia → se agrega como tema

#### TC-15: Agregar Temas Manualmente
1. En seccion Temas, completar formulario:
   - Asunto: "Revision presupuesto DAF"
   - IPR asociada (opcional)
   - Responsable (opcional)
   - Fecha limite (opcional)
2. Click "Agregar Tema"
3. **Esperado**: Tema aparece en la lista

#### TC-16: Conducir Reunion
1. Click "Iniciar Reunion" → estado cambia a EN_CURSO
2. Para cada tema, click "Revisar":
   - Escribir decision/notas
   - Guardar → tema marcado como TRATADO
3. Al terminar todos los temas, click "Finalizar Reunion"
4. Escribir resumen general (opcional)
5. Confirmar → estado cambia a FINALIZADA

#### TC-17: Ver Reunion Finalizada
1. Abrir reunion FINALIZADA
2. **Esperado**: Vista de solo lectura con:
   - Informacion de la reunion (fecha, ubicacion, organizador)
   - Resumen
   - Lista de temas con decisiones tomadas

---

### 4.6 Pruebas Transversales

#### TC-18: Verificacion de Permisos por Rol
| Funcionalidad | ADMIN_SISTEMA | ADMIN_REGIONAL | JEFE_DIVISION | ENCARGADO |
|---------------|:---:|:---:|:---:|:---:|
| Crear compromiso | Si | Si | Si | No |
| Crear problema | Si | Si | Si | Si |
| Crear IPR | Si | Si | No | No |
| Editar IPR | Si | Si | No | No |
| Verificar compromiso | Si | Si | Si (propia div) | No |
| Admin usuarios | Si | No | No | No |
| Admin divisiones | Si | No | No | No |
| Mi Division | No | No | Si | No |
| Mis Compromisos | No | No | No | Si |
| Dashboard ejecutivo | Si | Si | No | No |
| Crear reunion | Si | Si | Si | No |
| Busqueda global ⌘K | Si | Si | Si | Si |
| Ver notificaciones bell | Si | Si | Si | Si |

#### TC-19: Navegacion Sidebar
1. Login con cada usuario de prueba
2. Verificar que la barra lateral muestra exactamente las opciones correctas segun rol
3. Verificar que los links DGI no aparecen para operativos y viceversa

#### TC-20: Ciclo Completo de Crisis
1. Login ADMIN_REGIONAL → crear IPR → asignar responsable
2. Login ENCARGADO → crear compromiso vinculado a IPR
3. Login ADMIN_REGIONAL → crear problema en IPR
4. Login JEFE_DIVISION → crear reunion → preparar (ver sugerencias del paso 2-3)
5. Conducir reunion → agregar temas → revisar → finalizar
6. Verificar que compromisos creados en la reunion aparecen en la lista general

### 4.7 Wave 6 — UX Polish + Charts + CRUD (Ciclo 4)

#### TC-21: CSV Export desde DGI Explorer
1. Login como `jefe.dgi@goreos.cl` (JEFE_DGI)
2. Ir a `/datos` → seleccionar dominio "IPR"
3. Esperar que cargue la tabla de datos
4. Click boton "Exportar CSV" en el header de la tabla
5. **Esperado**: Se descarga un archivo `.csv` con los datos de la tabla
6. **Verificar**: Abrir el CSV — debe contener las columnas y filas visibles en la tabla

#### TC-22: Notificaciones Bell — Badge + Popover
1. Login como `regional@goreos.cl`
2. Verificar en el header: icono campana visible junto al avatar
3. Si hay alertas activas: badge rojo con numero visible sobre la campana
4. Click en la campana
5. **Esperado**: Popover se abre mostrando:
   - Titulo "Alertas activas" con conteo
   - Lista de hasta 5 alertas recientes con severidad (icono color), mensaje y fecha
   - Link "Ver todas las alertas →" al pie
6. Click en "Ver todas las alertas →"
7. **Esperado**: Navega a `/alertas`

#### TC-23: Busqueda Global ⌘K — Query + Resultados
1. Login como `regional@goreos.cl`
2. Click en boton "Buscar ⌘K" en el header (o presionar ⌘K / Ctrl+K)
3. **Esperado**: Dialog de busqueda se abre con input y placeholder "Buscar IPR, compromisos, problemas, personas..."
4. Escribir "DAF" (minimo 2 caracteres)
5. **Esperado**: Resultados agrupados por tipo:
   - **IPR**: NORMALIZACION ESCUELA DAFNE ZAPATA ROZAS (30387725)
   - **Compromisos**: Entrega informe tecnico avance semestral DAF (OC-0001)
   - **Problemas**: Facturas pendientes de visacion contable DAF... (PR-00002)
6. Escribir 1 solo caracter → muestra "Escribe al menos 2 caracteres para buscar"
7. **Verificar**: Buscar termino sin resultados → muestra "Sin resultados para ..."

#### TC-24: Busqueda Global ⌘K — Navegacion a Entidad
1. Con el dialog de busqueda abierto y resultados visibles (TC-23)
2. Click en un resultado de tipo IPR
3. **Esperado**: Dialog se cierra y navega a `/ipr/{id}` del IPR seleccionado
4. Volver a abrir ⌘K → click en resultado de compromiso
5. **Esperado**: Navega a `/compromisos?id={id}`
6. **Verificar**: Presionar Escape cierra el dialog sin navegar

#### TC-25: Dashboard Charts — Operativo (3 Charts Recharts)
1. Login como `regional@goreos.cl` (ADMIN_REGIONAL)
2. Ir a `/dashboard`
3. **Esperado**: Debajo de los KPIs, 3 charts visibles:
   - **Ejecucion Presupuestaria**: Bar chart vertical por division (% ejecucion)
   - **Compromisos por Estado**: Donut chart con leyenda (EN_PROGRESO, PENDIENTE, VENCIDO, VERIFICADO)
   - **Alertas por Severidad**: Horizontal bar chart (Critico, Alto, Atencion)
4. **Verificar**: Charts muestran datos reales (no vacios ni placeholders)
5. **Verificar**: Los datos coinciden con `GET /api/dashboard/chart-data`

#### TC-26: Dashboard Charts — DGI Gauges (Semaforo)
1. Login como `jefe.dgi@goreos.cl` (JEFE_DGI)
2. Ir a `/dashboard`
3. **Esperado**: Cockpit Jefe DGI con:
   - 5 tarjetas de semaforo institucional (PRESUPUESTO, CARTERA_IPR, CONVENIOS, TDE, RIESGOS)
   - Cada tarjeta con signal de color (verde=OK, amarillo=Atencion, rojo=Critico)
   - Iconos gauge visuales debajo de las tarjetas por cada dimension
4. **Verificar**: Sidebar muestra nav DGI (Home, Alertas, Tablero, Datos, Informes)
5. **Verificar**: Badge "DGI" visible junto a GORE_OS en el header

#### TC-27: IPR Edit (ADMIN_REGIONAL puede editar)
1. Login como `regional@goreos.cl` (ADMIN_REGIONAL)
2. Ir a `/ipr` → click en cualquier IPR para ver detalle
3. **Esperado**: Boton "Editar" visible en la seccion de detalle (junto a "Asignar Responsable")
4. Click "Editar" → se abre formulario de edicion
5. Cambiar nombre de la IPR → guardar
6. **Esperado**: Nombre actualizado exitosamente
7. **Verificar**: Login como `admin@goreos.cl` → tambien debe ver boton "Editar"

#### TC-28: IPR Edit — Role Gating (ENCARGADO no puede)
1. Login como `encargado.daf@goreos.cl` (ENCARGADO)
2. Ir a `/ipr/{id}` (detalle de cualquier IPR)
3. **Esperado**: Boton "Editar" NO visible. Solo vista de lectura.
4. **Verificar API**: `PATCH /api/ipr/{id}` con token ENCARGADO retorna 403 "Sin permisos suficientes"

#### TC-29: Presupuesto Edit Montos
1. Login como `regional@goreos.cl` (ADMIN_REGIONAL)
2. Ir a `/presupuesto` → click en un programa presupuestario
3. En el drawer de detalle, buscar boton "Editar Montos"
4. Click → inputs editables para: inicial, vigente, comprometido, devengado, pagado
5. Cambiar un monto → click "Guardar"
6. **Esperado**: Montos actualizados, drawer se refresca con valores nuevos
7. **Verificar API**: `PATCH /api/presupuesto/{id}` retorna 200

#### TC-30: Convenios Edit (Estado + Monto + Fecha)
1. Login como `regional@goreos.cl` (ADMIN_REGIONAL)
2. Ir a `/convenios` → click en un convenio
3. En el drawer de detalle, buscar boton "Editar"
4. Click → formulario con campos editables: estado, monto, fecha termino
5. Cambiar estado del convenio → click "Guardar"
6. **Esperado**: Badge de estado actualizado en el drawer
7. **Verificar**: Cerrar y reabrir drawer → valores persisten

### 4.8 Wave 7 — Auditoria Ontologica: Navegacion + Filtros + CRUD (Ciclo 6)

#### TC-31: Navegacion Bidireccional — Compromiso → IPR
1. Login como `regional@goreos.cl`
2. Ir a `/compromisos` → click en un compromiso con IPR asociada
3. En el drawer, buscar la linea "IPR: XXXXXXXX"
4. **Esperado**: El codigo BIP es un link azul clickeable
5. Click en el BIP
6. **Esperado**: Drawer se cierra, navega a `/ipr/{id}` del IPR asociado
7. **Verificar**: La pagina de detalle IPR carga correctamente con los 6 tabs

#### TC-32: Navegacion Bidireccional — Problema → IPR
1. Login como `regional@goreos.cl`
2. Ir a `/problemas` → click en un problema
3. En el drawer, buscar la linea "IPR: XXXXXXXX"
4. **Esperado**: BIP es link azul clickeable
5. Click → navega a `/ipr/{id}`

#### TC-33: Navegacion Bidireccional — Convenio → IPR
1. Ir a `/convenios` → click en un convenio con IPR asociada
2. En el drawer, buscar "IPR: XXXXXXXX — Nombre"
3. **Esperado**: BIP es link azul clickeable
4. Click → navega a `/ipr/{id}`

#### TC-34: Navegacion Bidireccional — Presupuesto CDP → IPR
1. Ir a `/presupuesto` → click en un programa con CDPs
2. En el drawer, seccion CDPs, buscar "IPR: XXXXXXXX"
3. **Esperado**: BIP es link azul clickeable
4. Click → navega a `/ipr/{id}`

#### TC-35: Navegacion Bidireccional — Reunion Topic → IPR
1. Ir a `/reuniones/{id}` (detalle de reunion con temas que tienen IPR)
2. En la lista de temas, buscar badge "BIP: XXXXXXXX"
3. **Esperado**: Badge BIP es link azul clickeable
4. Click → navega a `/ipr/{id}`

#### TC-36: AlertCard Multi-Subject en IPR Detail
1. Ir a `/ipr/{id}` → click tab "Alertas"
2. **Esperado**: Cada AlertCard tiene boton "Ver"
3. Click "Ver" en una alerta de tipo IPR
4. **Esperado**: Navega a `/ipr/{subject_id}`
5. **Verificar**: Si hay alertas de tipo compromiso/problema → navega a `/compromisos` o `/problemas`

#### TC-37: IPR Detail — Tab CDPs
1. Ir a `/ipr/{id}` (IPR con CDPs vinculados)
2. Click tab "CDPs"
3. **Esperado**: Tab muestra lista de CDPs con:
   - Numero de compromiso presupuestario (font-mono)
   - Badge de estado
   - Fecha emision → vencimiento
   - Monto (font-mono)
4. **Verificar**: Si IPR no tiene CDPs → mensaje "No hay CDPs vinculados a este IPR."
5. **Verificar API**: `GET /api/presupuesto/cdps-por-ipr/{ipr_id}` retorna array de BudgetCommitmentItem

#### TC-38: Filtro Division en Presupuesto
1. Login como `regional@goreos.cl`
2. Ir a `/presupuesto`
3. **Esperado**: FilterBar muestra 3 selects: Ano, Subtitulo, Division
4. Seleccionar una division
5. **Esperado**: Tabla se filtra mostrando solo programas de esa division
6. **Verificar**: Badge de filtro activo muestra "Division: {nombre}"
7. Click "Limpiar" → todos los filtros se resetean

#### TC-39: Filtro Orphan en Convenios (API)
1. `GET /api/convenios?orphan=true`
2. **Esperado**: Todos los convenios retornados tienen `ipr_id: null`
3. `GET /api/convenios?orphan=true&page_size=5`
4. **Esperado**: Respuesta paginada con max 5 items, todos sin IPR

#### TC-40: Filtro Assignee en IPR (API)
1. Obtener user_id de un usuario con IPRs asignadas
2. `GET /api/ipr?assignee_id={user_id}`
3. **Esperado**: Solo IPRs donde el assignee es ese usuario
4. `GET /api/ipr?assignee_id=00000000-0000-0000-0000-000000000000`
5. **Esperado**: `total: 0` (UUID inexistente)

#### TC-41: Paginacion DGI Initiatives (API)
1. Login como `jefe.dgi@goreos.cl`
2. `GET /api/dgi/initiatives?page=1&page_size=3`
3. **Esperado**: Respuesta con `{items, total, page, page_size, total_pages}`
4. `GET /api/dgi/initiatives` (sin params)
5. **Esperado**: Array plano (retrocompatible, no paginado)

#### TC-42: Crear Cuota Inline en Convenio
1. Login como `regional@goreos.cl`
2. Ir a `/convenios` → click en un convenio
3. En seccion "Cuotas", click boton "+Cuota"
4. **Esperado**: Form inline con campos Monto y Fecha
5. Completar: Monto=5000000, Fecha=proximo mes → click "Crear"
6. **Esperado**: Nueva cuota aparece en la lista con estado PENDIENTE
7. **Verificar**: Numero de cuota se auto-incrementa

#### TC-43: Registrar Pago de Cuota
1. Con un convenio que tiene cuotas PENDIENTE (TC-42)
2. En una cuota pendiente, click "Registrar Pago"
3. **Esperado**: Form inline con Monto pagado y Referencia
4. Completar: Monto=5000000, Ref="TRF-2026-001" → click "Confirmar"
5. **Esperado**: Cuota cambia a estado PAGADO con fecha y referencia
6. **Verificar**: Contador pagadas se actualiza (ej: "2/3 pagadas")

#### TC-44: Timeline de Estados en Problema
1. Login como `regional@goreos.cl`
2. Ir a `/problemas` → click en un problema
3. En el drawer, buscar seccion "Historial"
4. **Esperado**: Timeline visual con:
   - Punto azul: "Detectado — ABIERTO" con fecha y nombre del detector
   - Punto ambar: "EN_GESTION" (si aplica)
   - Punto verde/rojo: "Resuelto"/"Cerrado sin resolver" con fecha y nombre (si aplica)
5. **Verificar**: Problema en estado ABIERTO solo muestra el primer punto
6. **Verificar**: Problema RESUELTO muestra los 3 puntos completos

### 4.9 Ciclo 19 — SISREC Multi-Role Workflow

#### TC-45: Crear Rendicion con Monto
1. Login como `regional@goreos.cl` (ADMIN_REGIONAL)
2. Ir a `/datos` → seleccionar dominio "Rendiciones"
3. Click "Nueva Rendicion"
4. Completar:
   - IPR: buscar y seleccionar una IPR
   - Ejecutor: buscar organizacion (opcional)
   - Periodo inicio/fin: fechas
   - Monto rendido: 5000000
5. Click "Registrar"
6. **Esperado**: Rendicion aparece en lista con estado PENDIENTE y monto $5.000.000

#### TC-46: Flujo Completo — Happy Path (PENDIENTE → APROBADA)
1. Login como `regional@goreos.cl` → crear rendicion (TC-45)
2. Abrir la rendicion en el panel lateral
3. Click "Enviar a Revision RTF"
4. **Esperado**: Estado cambia a EN_REVISION_RTF (badge amber)
5. Login como `jefe.dgi@goreos.cl` (JEFE_DGI)
6. Abrir la misma rendicion
7. Escribir comentario: "Documentacion completa" → click "Visar RTF"
8. **Esperado**: Estado cambia a VISADA_RTF (badge blue)
9. Click "Enviar a UCR"
10. **Esperado**: Estado cambia a EN_REVISION_UCR (badge indigo)
11. Click "Aprobar"
12. **Esperado**: Estado cambia a APROBADA (badge verde con check). No hay mas acciones disponibles.

#### TC-47: Loop de Observacion (RTF → OBSERVADA → RTF)
1. Login como `regional@goreos.cl` → crear rendicion → enviar a revision RTF
2. Login como `jefe.dgi@goreos.cl`
3. Escribir "Falta boleta N°123" → click "Observar"
4. **Esperado**: Estado OBSERVADA (badge orange)
5. Login como `regional@goreos.cl`
6. **Esperado**: Boton "Re-enviar a Revision RTF" visible
7. Click "Re-enviar a Revision RTF"
8. **Esperado**: Estado vuelve a EN_REVISION_RTF

#### TC-48: Restriccion de Rol — Operativa NO puede visar
1. Login como `regional@goreos.cl`
2. Crear rendicion y enviarla a revision RTF
3. Intentar "Visar RTF" desde el mismo usuario
4. **Esperado**: Boton NO visible (solo DGI ve acciones de visa/aprobacion)
5. **Verificar API**: `PATCH /api/dgi/data/rendiciones/{id}` con state_id de VISADA_RTF → HTTP 403

#### TC-49: Historial de Transiciones
1. Ejecutar flujo completo (TC-46)
2. Abrir rendicion aprobada en panel lateral
3. Buscar seccion "Historial"
4. **Esperado**: Timeline con 4+ entradas:
   - PENDIENTE → EN_REVISION_RTF
   - EN_REVISION_RTF → VISADA_RTF (con comment "Documentacion completa")
   - VISADA_RTF → EN_REVISION_UCR
   - EN_REVISION_UCR → APROBADA
5. **Verificar**: Cada entrada muestra fecha, nombre del usuario, y comment (si hay)

#### TC-50: SLA Vencida
1. Crear rendicion via API y transicionar a EN_REVISION_RTF
2. Esperar 7+ dias (o modificar `updated_at` en DB para simular)
3. Ir a `/datos` → "Rendiciones"
4. **Esperado**: Badge rojo "Vencida (Xd)" junto al estado
5. **Verificar API**: `GET /api/dgi/data/rendiciones/vencidas` incluye la rendicion

#### TC-51: Art. 18 CGR — Bloqueo de Pago por Rendicion Pendiente
1. Crear un convenio con cuota e IPR vinculada
2. Crear una rendicion vinculada al mismo convenio/IPR en estado PENDIENTE
3. Intentar registrar pago en la cuota (paid_amount o paid_at)
4. **Esperado**: HTTP 409 "Art. 18 Res. 30 CGR: Existen N rendicion(es) pendiente(s)..."
5. Aprobar la rendicion (flujo completo)
6. Reintentar registrar pago
7. **Esperado**: Pago se registra correctamente

#### TC-52: Rechazo en UCR
1. Crear rendicion → enviar a RTF → visar RTF → enviar a UCR
2. Login como DGI → escribir "No cumple normativa" → click "Rechazar"
3. **Esperado**: Estado RECHAZADA (badge rojo con X). No hay mas acciones. Estado terminal.

---

## 5. Endpoints API — Referencia Rapida

### 5.1 Autenticacion
```
POST /api/auth/login          Login (form-urlencoded: username, password)
```

### 5.2 IPR
```
GET    /api/ipr                Lista paginada, filtros: ipr_type, status, sector, search, assignee_id
GET    /api/ipr/{id}           Detalle con conteos
POST   /api/ipr                Crear IPR (ADMIN_SISTEMA, ADMIN_REGIONAL)
PATCH  /api/ipr/{id}           Editar IPR (nombre, descripcion, tipo, estado, assignee)
POST   /api/ipr/{id}/avances   Registrar avance (progress_report)
GET    /api/ipr/{id}/avances   Listar avances
```

### 5.3 Compromisos
```
GET    /api/compromisos              Lista paginada
GET    /api/compromisos/{id}         Detalle con historial
POST   /api/compromisos              Crear
POST   /api/compromisos/{id}/completar   Marcar completado
POST   /api/compromisos/{id}/verificar   Verificar
POST   /api/compromisos/{id}/devolver    Devolver
```

### 5.4 Problemas
```
GET    /api/problemas            Lista paginada
GET    /api/problemas/{id}       Detalle
POST   /api/problemas            Crear
PATCH  /api/problemas/{id}       Actualizar (estado, solucion)
```

### 5.5 Alertas
```
GET    /api/alertas              Lista paginada
POST   /api/alertas/{id}/atender Atender alerta
```

### 5.6 Dashboard
```
GET    /api/dashboard                   Dashboard role-aware
GET    /api/dashboard/mi-division       Stats equipo (JEFE_DIVISION)
GET    /api/dashboard/mis-compromisos   Compromisos agrupados (ENCARGADO)
GET    /api/dashboard/ejecutivo         Dashboard con desglose divisiones
GET    /api/dashboard/chart-data        Datos para charts (commitments_by_state, alerts_by_severity, budget_by_division)
```

### 5.6b Busqueda Global (Nuevo C4)
```
GET    /api/search?q={query}&limit={n}  Busqueda cross-entity (IPR, compromisos, problemas). Min 2 chars.
```

### 5.7 Presupuesto
```
GET    /api/presupuesto/resumen              Resumen agrupado
GET    /api/presupuesto/cdps-por-ipr/{id}    CDPs vinculados a un IPR (Nuevo C6)
GET    /api/presupuesto                      Lista programas (filtros: fiscal_year, division_id, subtitle)
GET    /api/presupuesto/{id}                 Detalle con CDPs
POST   /api/presupuesto                      Crear programa
PATCH  /api/presupuesto/{id}                 Actualizar montos
```

### 5.8 Convenios
```
GET    /api/convenios               Lista (filtros: state, agreement_type, ipr_id, orphan, search, date_from/to)
GET    /api/convenios/{id}          Detalle con cuotas + historial
POST   /api/convenios               Crear
PATCH  /api/convenios/{id}          Actualizar (estado, monto, fecha, CGR)
GET    /api/convenios/{id}/transiciones  Estados destino validos
GET    /api/convenios/{id}/cuotas   Listar cuotas
POST   /api/convenios/{id}/cuotas   Agregar cuota (UI inline en drawer)
PATCH  /api/convenios/{id}/cuotas/{cid}  Actualizar cuota / registrar pago
```

### 5.9 Reuniones
```
GET    /api/reuniones                         Lista paginada
POST   /api/reuniones                         Crear reunion
GET    /api/reuniones/{id}                    Detalle con temas
GET    /api/reuniones/{id}/preparar           Auto-sugerencias
POST   /api/reuniones/{id}/temas             Agregar tema
POST   /api/reuniones/{id}/temas/{tid}/revisar  Revisar tema
POST   /api/reuniones/{id}/iniciar           Iniciar reunion
POST   /api/reuniones/{id}/finalizar         Finalizar reunion
```

### 5.10 Administracion
```
GET    /api/admin/usuarios                  Lista usuarios
GET    /api/admin/usuarios/{id}             Detalle usuario
POST   /api/admin/usuarios                  Crear usuario
PATCH  /api/admin/usuarios/{id}             Editar usuario
POST   /api/admin/usuarios/{id}/toggle-activo  Toggle activo
POST   /api/admin/usuarios/{id}/reset-password Reset password
GET    /api/admin/divisiones                Lista divisiones
POST   /api/admin/divisiones                Crear division
PATCH  /api/admin/divisiones/{id}           Editar division
```

### 5.11 Catalogos
```
GET    /api/catalogs/categories/{scheme}   Categorias por esquema
GET    /api/catalogs/commitment-types      Tipos de compromiso
GET    /api/catalogs/users                 Usuarios activos
GET    /api/catalogs/iprs                  IPRs (para selects)
GET    /api/catalogs/divisions             Divisiones activas
```

### 5.12 DGI
```
GET    /api/dgi/cockpit                    Cockpit por rol DGI
GET    /api/dgi/initiatives                Iniciativas (filtros: status, responsible_id, page, page_size)
POST   /api/dgi/initiatives                Crear iniciativa
PATCH  /api/dgi/initiatives/{id}           Actualizar iniciativa
POST   /api/dgi/initiatives/{id}/move      Mover en Kanban (WIP limits)
POST   /api/dgi/data/indicators/refresh    Recalcular indicadores
GET    /api/dgi/reports                    Informes
```

### 5.13 Rendiciones SISREC (Nuevo C19)
```
GET    /api/dgi/data/rendiciones                  Lista paginada (filtros: state, search)
GET    /api/dgi/data/rendiciones/vencidas          Rendiciones que superan SLA (7d RTF, 2d UCR)
GET    /api/dgi/data/rendiciones/{id}              Detalle con historial de transiciones
POST   /api/dgi/data/rendiciones                   Crear rendicion (ipr_id requerido, amount opcional)
PATCH  /api/dgi/data/rendiciones/{id}              Transicionar estado / actualizar campos
```

**Campos PATCH**: `state_id` (transicion), `amount`, `period_start`, `period_end`, `submitted_at`, `comment` (en body, se guarda en historial).

**Transiciones por rol**: ver seccion 7 "Rendicion (SISREC Multi-Role)".

**Campos computados en respuesta**: `is_overdue` (bool), `days_in_state` (float), `history` (en detail).

---

## 6. Hoja de Ruta

### 6.1 Completado

| Ciclo | Alcance | Estado |
|-------|---------|--------|
| Ciclo 1 | Base operativa: Login, Dashboard, IPR (read-only), Compromisos CRUD, Problemas lista, Alertas | Completado |
| Ciclo 2 | Presupuesto, Convenios, DGI (cockpits, indicadores, iniciativas, informes) | Completado |
| Ciclo 3 | Migracion para_titi: forms CRUD, IPR escritura, admin, dashboards, reuniones | Completado |
| Ciclo 4 | UX Polish (CSV export, Bell notif, ⌘K search), Charts (recharts dashboard, DGI gauges), CRUD (IPR/Presupuesto/Convenios edit) | Completado |
| Ciclo 5 | ComboboxAsync, Initiative CRUD, divisions filter, spec v1.0 | Completado |
| Tests  | 71 integration tests (8 modulos), test DB setup, security readonly suite | Completado |
| Confrontacion | Migracion datos: org_type(+2), jerarquia 3 niveles, agreement_state(+3), roles(+5) | Completado |
| Ciclo 6 | Auditoria ontologica: navegacion bidireccional (7), filtros API (3), CRUD completions (4) | Completado |
| Ciclo 19 | SISREC multi-role: 8-state machine RTF→UCR, audit trail, SLA, Art. 18 fix, 18 tests | Completado |

### 6.2 Pendiente / Proximos Ciclos

| Item | Prioridad | Descripcion |
|------|-----------|-------------|
| Tests automatizados | ~~Alta~~ | ~~71 tests backend completados~~ — Pendiente: E2E frontend |
| Exportar a PDF | Media | Exportar reportes e informes DGI a PDF |
| Auditoria de acciones | Media | Log de acciones de usuario (quien hizo que, cuando) |
| Notificaciones email | Media | Notificaciones por email para alertas criticas y compromisos vencidos |
| DGI dimension TDE | Baja | Fuente de datos real para dimension Transformacion Digital |
| Integracion SIGFE | Baja | Conexion con sistema financiero del Estado |
| App movil (PWA) | Baja | Acceso desde dispositivos moviles |

---

## 7. Maquinas de Estado

### Compromiso Operativo
```
PENDIENTE → EN_PROGRESO → COMPLETADO → VERIFICADO
                                ↓
                         (devolver) → EN_PROGRESO

Estados terminales: VERIFICADO, CANCELADO
```

### Problema IPR
```
ABIERTO → EN_GESTION → RESUELTO
   ↓
CERRADO_SIN_RESOLVER
```

### Convenio
```
BORRADOR → FIRMADO_GORE → FIRMADO_CONTRAPARTE → VIGENTE → VENCIDO
                    ↓                               ↓
              EN_MODIFICACION                   TERMINADO
```

### Reunion de Crisis
```
PROGRAMADA → EN_CURSO → FINALIZADA
(creada)     (iniciar)   (finalizar)
```

### Rendicion (SISREC Multi-Role)
```
PENDIENTE ──→ EN_REVISION_RTF ──→ VISADA_RTF ──→ EN_REVISION_UCR ──→ APROBADA
 (any)         (DGI)↓               (DGI)          (DGI)↓    ↘
               OBSERVADA ←──────────────────────── OBSERVADA   RECHAZADA
                 ↓ (any)
               EN_REVISION_RTF (loop)
```

**Roles por transicion**:
| Transicion | Roles permitidos |
|-----------|-----------------|
| PENDIENTE → EN_REVISION_RTF | Operativa + DGI (cualquiera) |
| EN_REVISION_RTF → VISADA_RTF | Solo DGI |
| EN_REVISION_RTF → OBSERVADA | Solo DGI |
| VISADA_RTF → EN_REVISION_UCR | Solo DGI |
| EN_REVISION_UCR → APROBADA | Solo DGI |
| EN_REVISION_UCR → RECHAZADA | Solo DGI |
| EN_REVISION_UCR → OBSERVADA | Solo DGI |
| OBSERVADA → EN_REVISION_RTF | Operativa + DGI (reenvio) |

**SLA**: EN_REVISION_RTF = 7 dias, EN_REVISION_UCR = 2 dias.

---

## 8. Esquemas de Categoria (ref.category)

Esquemas frecuentes para pruebas:

| Scheme | Valores | Uso |
|--------|---------|-----|
| `commitment_state` | PENDIENTE, EN_PROGRESO, COMPLETADO, VERIFICADO, CANCELADO | Estado compromisos |
| `problem_state` | ABIERTO, EN_GESTION, RESUELTO, CERRADO_SIN_RESOLVER | Estado problemas |
| `problem_type` | TECNICO, FINANCIERO, LEGAL, ADMINISTRATIVO, AMBIENTAL, SOCIAL | Tipo problema |
| `impact` | ALTO, MEDIO, BAJO | Nivel impacto |
| `ipr_type` | INFRAESTRUCTURA, EQUIPAMIENTO, TRANSFERENCIA, PROGRAMA_SOCIAL, PROGRAMA_8PCT, CONSERVACION, ESTUDIO | Tipo IPR |
| `ipr_state` | EN_FORMULACION, EN_EJECUCION, TERMINADO, CERRADO | Estado IPR |
| `alert_level` | CRITICO, ALTO, ATENCION, INFO | Severidad alerta |
| `system_role` | ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, ENCARGADO, JEFE_DGI, ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD | Roles del sistema |
| `rendition_state` | PENDIENTE, EN_REVISION_RTF, VISADA_RTF, EN_REVISION_UCR, OBSERVADA, APROBADA, RECHAZADA (+EN_REVISION legacy) | Estado rendiciones SISREC |

---

## 9. Datos Demo

Los datos demo utilizan el prefijo `DEMO-` para identificacion:

```bash
# Cargar datos demo
docker exec -i goreos_db psql -U goreos -d goreos_model \
  < model/model_goreos/sql/goreos_seed_demo_ciclo2.sql

# Limpiar datos demo (solo DEMO-, datos reales intactos)
docker exec -i goreos_db psql -U goreos -d goreos_model \
  < model/model_goreos/sql/goreos_unseed_demo_ciclo2.sql

# Refrescar indicadores DGI
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=jefe.dgi@goreos.cl&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/dgi/data/indicators/refresh
```

| Tipo Demo | Codigos | Descripcion |
|-----------|---------|-------------|
| Programas presupuestarios | DEMO-BP-001..006 | 3 divisiones, ejecucion 30%-80% |
| Convenios | DEMO-AGR-001..004 | 2 VIGENTE, 1 EN_MODIFICACION, 1 VENCIDO |
| CDPs | DEMO-CDP-001..008 | Vinculados a IPRs reales |
