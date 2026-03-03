# GORE_OS — Especificacion Funcional y Tecnica v1.0

> Documento generado: 2026-02-25
> Ultima revision: Ciclo 12 (Post-Wave 5: CORE Governance + Doc Sync)

---

## 1. Vision General del Sistema

**GORE_OS** es un sistema operativo institucional para el Gobierno Regional de Nuble (GORE), Chile. Reemplaza flujos basados en Excel con una plataforma web integrada que gestiona la cartera de inversiones publicas regionales, compromisos operacionales, presupuesto, convenios y gobernanza institucional.

### 1.1 Poblaciones de Usuario

El sistema sirve a dos poblaciones distintas sobre una base de datos compartida:

| Poblacion | Roles | Funcion Principal |
|-----------|-------|-------------------|
| **Operativa** | ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, ENCARGADO | Gestion de crisis IPR: compromisos, problemas, alertas, presupuesto, convenios, reuniones |
| **DGI** (Departamento de Gestion Institucional) | JEFE_DGI, ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD | Monitoreo de indicadores, tablero Kanban de iniciativas, informes auto-poblados, exploracion de datos |

Un unico login detecta el rol del usuario y lo enruta a su sidebar y dashboard correspondiente.

### 1.2 Stack Tecnologico

| Capa | Tecnologia | Version |
|------|-----------|---------|
| Frontend | Next.js (App Router, Turbopack) + TypeScript + TailwindCSS v4 | 16 |
| Componentes UI | shadcn/ui (Radix UI) + lucide-react | latest |
| Backend | FastAPI + uvicorn (hot-reload) | 0.100+ |
| ORM/DB Driver | SQLAlchemy async + asyncpg (raw SQL, sin modelos ORM) | 2.x |
| Base de datos | PostgreSQL | 16 |
| Autenticacion | JWT (python-jose) + bcrypt, OAuth2PasswordBearer | — |
| Contenedores | Docker Compose | — |

### 1.3 Arquitectura de Red

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────────────┐
│  Next.js 16   │────▶│  FastAPI      │────▶│  PostgreSQL 16            │
│  :3000        │     │  :8000       │     │  goreos_db                │
│  (web/)       │     │  (api/)      │     │  red: visor_model_default │
└──────────────┘     └──────────────┘     └──────────────────────────┘
```

La base de datos vive en la red Docker externa `visor_model_default`, compartida con otros proyectos del GORE.

---

## 2. Autenticacion y Autorizacion

### 2.1 Flujo de Autenticacion

1. `POST /api/auth/login` recibe `username` (email) + `password` (form-urlencoded)
2. Valida contra `core.user.password_hash` (bcrypt)
3. Verifica `is_active = true`
4. Determina `population` ("operativa" o "dgi") segun `system_role_id`
5. Genera JWT con 480 minutos de expiracion
6. Retorna `{access_token, user: {id, email, nombre, apellido_paterno, role_code, role_label, population, division_id, division_name}}`

### 2.2 Manejo de Token (Frontend)

- Token almacenado en `localStorage.goreos_token`
- Usuario almacenado en `localStorage.goreos_user` (JSON)
- `ApiClient` singleton adjunta `Authorization: Bearer {token}` automaticamente
- En HTTP 401, limpia token y redirige a `/login`
- Errores de API: `ApiClient.fetch()` extrae `.detail` del JSON de error de FastAPI automaticamente

### 2.3 Matriz de Roles y Permisos

| Capacidad | ADMIN_SISTEMA | ADMIN_REGIONAL | JEFE_DIVISION | ENCARGADO | JEFE_DGI | ESP_CG | ESP_PROC | ESP_TD |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Ver dashboard operativo | ✓ | ✓ | ✓ | ✓ | — | — | — | — |
| Ver cockpit DGI | — | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Crear IPR | ✓ | ✓ | — | — | — | — | — | — |
| Editar IPR | ✓ | ✓ | parcial | — | — | — | — | — |
| Crear compromisos | ✓ | ✓ | ✓ | — | — | — | — | — |
| Completar compromisos | ✓ | ✓ | — | solo propios | — | — | — | — |
| Verificar compromisos | ✓ | ✓ | division propia | — | — | — | — | — |
| Devolver compromisos | ✓ | ✓ | ✓ | — | — | — | — | — |
| Crear problemas | ✓ | ✓ | ✓ | ✓ | — | — | — | — |
| Resolver/cerrar problemas | ✓ | ✓ | ✓ | ✓ | — | — | — | — |
| Atender alertas | ✓ | ✓ | ✓ | ✓ | — | — | — | — |
| Crear presupuesto | ✓ | ✓ | — | — | — | — | — | — |
| Editar presupuesto | ✓ | ✓ | division propia | — | — | — | — | — |
| Crear convenios | ✓ | ✓ | ✓ | ✓ | — | — | — | — |
| Crear reuniones | ✓ | ✓ | ✓ | — | — | — | — | — |
| Iniciar/finalizar reuniones | ✓ | ✓ | ✓ | — | — | — | — | — |
| Administrar usuarios | ✓ | — | — | — | — | — | — | — |
| Administrar divisiones | ✓ | — | — | — | — | — | — | — |
| Gestionar iniciativas DGI | — | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Crear informes DGI | — | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Refrescar indicadores DGI | — | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Explorar datos (DGI Explorer) | — | — | — | — | ✓ | ✓ | ✓ | ✓ |

### 2.4 Usuarios de Prueba

Todas las contrasenas: `admin123`

| Email | Rol | Poblacion |
|-------|-----|-----------|
| admin@goreos.cl | ADMIN_SISTEMA | operativa |
| regional@goreos.cl | ADMIN_REGIONAL | operativa |
| jefe.daf@goreos.cl | JEFE_DIVISION | operativa |
| encargado.daf@goreos.cl | ENCARGADO | operativa |
| jefe.dgi@goreos.cl | JEFE_DGI | dgi |
| control.gestion@goreos.cl | ESP_CONTROL_GESTION | dgi |
| procesos@goreos.cl | ESP_PROCESOS | dgi |
| td@goreos.cl | ESP_TD | dgi |

---

## 3. Modulos Funcionales — Poblacion Operativa

### 3.1 Dashboard (Panel de Control)

**Ruta**: `/dashboard`
**Endpoints**: `GET /api/dashboard`, `GET /api/dashboard/chart-data`, `GET /api/dashboard/ejecutivo`, `GET /api/dashboard/mi-division`, `GET /api/dashboard/mis-compromisos`

El dashboard es **role-aware**: un unico endpoint despacha a implementaciones distintas segun el rol del usuario.

#### Vista ADMIN_REGIONAL / ADMIN_SISTEMA

- **KPIs** (4 tarjetas): IPRs criticas, compromisos vencidos, ejecucion presupuestaria global, convenios por vencer
- **Graficos** (3, via Recharts):
  - Ejecucion presupuestaria por division (BarChart, top 10)
  - Compromisos por estado (Donut: PENDIENTE, EN_PROGRESO, COMPLETADO, VERIFICADO, CANCELADO, VENCIDO)
  - Alertas por severidad (Donut: CRITICO, ALTO, ATENCION, INFO)
- **Tablas**: Compromisos recientes (top 15, priorizando vencidos), alertas sin atender

#### Dashboard Ejecutivo (ADMIN)

- Todo lo anterior + desglose por division: vencidos, total compromisos, problemas abiertos, ejecucion presupuestaria %

#### Vista JEFE_DIVISION — Mi Division

- **KPIs**: Vencidos, por verificar, problemas abiertos, ejecucion presupuestaria de la division
- **Carga del equipo**: Tarjetas por integrante con badges (vencidos, pendientes, en progreso, completados)
- **Tabla**: Compromisos vencidos de la division

#### Vista ENCARGADO — Mis Compromisos

- **KPIs**: Personales (vencidos, esta semana, total pendientes, completados)
- **Agrupacion**: Vencidos (rojo), esta semana (ambar), pendientes (azul) — cada grupo con DataTable

---

### 3.2 IPR (Intervenciones Publicas Regionales)

**Ruta**: `/ipr`, `/ipr/[id]`, `/ipr/nuevo`
**Endpoints**: `GET /api/ipr` (paginado), `GET /api/ipr/{id}`, `POST /api/ipr`, `PATCH /api/ipr/{id}`, `POST /api/ipr/{id}/avances`, `GET /api/ipr/{id}/avances`

#### Entidad Central

La IPR es la entidad central del sistema. Poliformica con 5 naturalezas (PROYECTO, PROGRAMA, PROGRAMA_INVERSION, ESTUDIO_BASICO, ANF) y 8 tipos (INFRAESTRUCTURA, EQUIPAMIENTO, CONSERVACION, TRANSFERENCIA, SUBSIDIO, ESTUDIO, PROGRAMA_SOCIAL, PROGRAMA_8PCT).

**3,622+ registros** en la base de datos real.

#### Lista (Pagina Principal)

- Filtros: tipo IPR, estado, sector, nivel alerta, busqueda libre
- Columnas: nivel alerta (punto color), codigo BIP, nombre, tipo (badge), estado (StatusBadge), presupuesto total (CLP compacto)
- Filtrado por rol: ENCARGADO solo ve IPRs asignadas, JEFE_DIVISION solo su division, admins ven todo
- Ordenamiento: nivel alerta DESC, luego codigo BIP

#### Detalle (Pagina con Tabs)

10 pestanas con informacion relacionada (las primeras 5 principales):
1. **Compromisos**: DataTable filtrada por `ipr_id`
2. **Problemas**: DataTable filtrada por `ipr_id`
3. **Alertas**: AlertCard list filtrada por `subject_type=core.ipr`
4. **Convenios**: Lista de convenios vinculados con cuotas
5. **Avances**: Reportes de progreso con formulario inline para registrar nuevo avance

**Acciones en drawer**:
- Asignar encargado (`PATCH` con `assignee_id`)
- Editar nombre (`PATCH`)
- Registrar avance (`POST /api/ipr/{id}/avances` con report_date, physical_progress%, financial_progress%, descripcion)

#### Creacion

Formulario: codigo BIP (auto-genera si vacio, formato IPR-00001), nombre*, tipo IPR, estado inicial, division patrocinante (~31 opciones), descripcion.

---

### 3.3 Compromisos Operacionales

**Ruta**: `/compromisos`, `/compromisos/nuevo`
**Endpoints**: `GET /api/compromisos` (paginado), `GET /api/compromisos/{id}`, `POST /api/compromisos`, `POST /api/compromisos/{id}/completar`, `POST /api/compromisos/{id}/verificar`, `POST /api/compromisos/{id}/devolver`

#### Maquina de Estados

```
PENDIENTE → EN_PROGRESO → COMPLETADO → VERIFICADO
                              ↓
                         EN_PROGRESO (devolucion)

Estado terminal: CANCELADO (desde cualquier estado)
```

#### Lista

- Filtros: estado (6), division, responsable, IPR, solo vencidos, solo mios
- Columnas: urgencia (TemporalIndicator: dias restantes, color rojo/naranja/verde), descripcion, codigo BIP, responsable, fecha limite, estado
- Ordenamiento: vencidos primero (no terminados con fecha pasada), luego por fecha limite ASC
- Click fila → DrawerPanel con detalle + acciones + historial de cambios (timeline)

#### Acciones de Estado (en Drawer)

- **Completar**: Solo responsable o admins. Requiere observaciones. Establece `completed_at = NOW()`
- **Verificar**: Solo JEFE_DIVISION (su division) o admins. Solo desde COMPLETADO. Establece `verified_by_id`, `verified_at`
- **Devolver**: Solo JEFE_DIVISION/admins. Solo desde COMPLETADO. Vuelve a EN_PROGRESO. Requiere motivo
- Cada accion genera registro en `commitment_history`

#### Creacion

Formulario: tipo compromiso (Select con 10 tipos, cada uno con `default_days`), descripcion*, responsable* (Select de usuarios), fecha limite* (auto-calculada desde `default_days`), IPR asociada (ComboboxAsync con busqueda server-side), observaciones.

**10 tipos de compromiso**: Hito Contractual, Entrega de Informe, Rendicion, Revision Tecnica, Visita a Terreno, Sesion de Comite, Plazo CGR, Plazo Convenio, Pago, Otro.

---

### 3.4 Problemas

**Ruta**: `/problemas`, `/problemas/nuevo`
**Endpoints**: `GET /api/problemas` (paginado), `GET /api/problemas/{id}`, `POST /api/problemas`, `PATCH /api/problemas/{id}`

#### Maquina de Estados

```
ABIERTO → EN_GESTION → RESUELTO
                    ↘ CERRADO_SIN_RESOLVER
```

#### Lista y Detalle

- Filtros: estado, tipo problema, busqueda
- Columnas: dias abierto, codigo BIP, descripcion, tipo (badge), impacto (badge color), estado
- Drawer con acciones: Pasar a En Gestion, Resolver (con solucion aplicada), Cerrar sin Resolver

#### Creacion

Formulario: IPR asociada* (ComboboxAsync), tipo problema* (Select: TECNICO, FINANCIERO, ADMINISTRATIVO, LEGAL, COORDINACION, EXTERNO), impacto, descripcion*, descripcion del impacto, solucion propuesta.

**6 tipos de impacto**: BLOQUEA_PAGO, RETRASA_OBRA, RETRASA_CONVENIO, RIESGO_RENDICION, INCUMPLIMIENTO_PLAZO, OTRO.

---

### 3.5 Alertas

**Ruta**: `/alertas`
**Endpoints**: `GET /api/alertas` (paginado), `POST /api/alertas/{id}/atender`

#### Modelo

Alertas generadas por el sistema con 4 niveles de severidad: CRITICO (rojo), ALTO (naranja), ATENCION (ambar), INFO (azul).

**12 tipos de alerta**: cuota vencida, cuota proxima, convenio por vencer, convenio vencido, trabajo vencido, trabajo bloqueado largo, problema sin gestion, rendicion pendiente, obra sin pago, plazo legal, CDP por vencer, presupuesto bajo.

#### Lista

- Filtros: severidad, tipo alerta, toggle "Solo Activas" (por defecto ON)
- Renderizadas como AlertCard (borde izquierdo coloreado, icono severidad, mensaje, metadata)
- Filtrado por rol: ENCARGADO ve alertas de sus IPRs/compromisos, JEFE_DIVISION de su division, admins todo

#### Atender Alerta

- `POST /api/alertas/{id}/atender` con `action_taken` (texto)
- Establece `attended_by_id`, `attended_at`
- No se puede atender si ya tiene `resolved_at`

#### Notificaciones en Header

- Bell icon con popover que muestra 5 alertas mas recientes
- Auto-refresh cada 60 segundos
- Badge con conteo total (max "99+")

---

### 3.6 Presupuesto

**Ruta**: `/presupuesto`
**Endpoints**: `GET /api/presupuesto` (paginado), `GET /api/presupuesto/{id}`, `POST /api/presupuesto`, `PATCH /api/presupuesto/{id}`, `GET /api/presupuesto/resumen`

#### Modelo

Programa presupuestario por ano fiscal con 5 etapas de ejecucion: inicial → vigente → comprometido → devengado → pagado. Ejecucion % = pagado/vigente.

#### Lista

- Filtros: ano fiscal (2024-2026), subtitulo (21-35), busqueda
- Columnas: codigo, nombre, division, subtitulo, monto inicial (CLP compacto), ejecucion % (barra color: verde >=70%, ambar >=40%, rojo <40%)
- JEFE_DIVISION solo ve programas de su division

#### Detalle (en Drawer)

- Header con codigo, nombre, ano, division
- Barra de ejecucion con porcentaje
- Montos editables (inline): inicial, vigente, comprometido, devengado, pagado
- Clasificacion presupuestaria: subtitulo, item, asignacion
- Tabla de arrastres por ano fiscal
- Tabla de CDPs vinculados (numero compromiso, estado, fechas, monto, IPR)

#### Resumen Agregado

`GET /api/presupuesto/resumen?group_by=division|subtitle` — agrega montos y programa_count por division o subtitulo.

---

### 3.7 Convenios

**Ruta**: `/convenios`
**Endpoints**: `GET /api/convenios` (paginado), `GET /api/convenios/{id}`, `POST /api/convenios`, `PATCH /api/convenios/{id}`, `GET/POST /api/convenios/{id}/cuotas`, `PATCH /api/convenios/{id}/cuotas/{cuota_id}`

#### Maquina de Estados

```
BORRADOR → EN_NEGOCIACION → EN_REVISION_JURIDICA → FIRMADO_GORE → FIRMADO_CONTRAPARTE → VIGENTE
                                                                                           ↓
                                                                          EN_MODIFICACION / VENCIDO / TERMINADO / RESCILIADO
```

**6 tipos**: MANDATO, TRANSFERENCIA, COLABORACION, PROGRAMACION, MARCO, EJECUCION

#### Lista

- Filtros: estado (10), tipo convenio (6)
- Columnas: numero convenio, tipo (badge), codigo BIP, receptor, monto total (CLP), dias para vencimiento (TemporalIndicator), estado
- Ordenamiento: estados activos primero, luego fecha vencimiento ASC

#### Detalle (en Drawer)

- Formulario editable: estado, monto total, fecha vencimiento, resultado CGR
- Partes: otorgante, receptor, referente tecnico
- Cuotas: tabla con numero, estado pago (badge color), monto, fecha vencimiento, datos de pago
- Crear/editar cuotas inline

---

### 3.8 Reuniones de Crisis

**Ruta**: `/reuniones`, `/reuniones/[id]`, `/reuniones/nueva`
**Endpoints**: `GET /api/reuniones` (paginado), `POST /api/reuniones`, `GET /api/reuniones/{id}`, `GET /api/reuniones/{id}/preparar`, `POST /api/reuniones/{id}/temas`, `POST /api/reuniones/{id}/temas/{id}/revisar`, `POST /api/reuniones/{id}/iniciar`, `POST /api/reuniones/{id}/finalizar`

#### Ciclo de Vida

```
PROGRAMADA → EN_CURSO → FINALIZADA
```

#### Lista

- Filtro: estado (tabs: Todas, PROGRAMADA, EN_CURSO, FINALIZADA)
- Columnas: numero sesion, fecha programada, estado (badge animado si EN_CURSO), resumen, organizador, cantidad de temas

#### Creacion

- Crea automaticamente: comite de crisis (COMITE-CRISIS), sesion numerada, acta con numero auto-generado (ACT-N)
- Campos: fecha/hora, ubicacion, resumen

#### Detalle

- Header con metadata de sesion
- **Auto-sugerencias** (`GET /preparar`): alertas criticas sin resolver, compromisos vencidos, problemas abiertos >7 dias
- Agregar temas manualmente: asunto, responsable (usuario), fecha limite, IPR vinculada
- Revisar temas: decision (texto), estado
- Acciones: Iniciar sesion, Finalizar sesion (con resumen opcional)

---

### 3.9 Sesiones CORE Ordinarias y Votacion

**Ruta**: `/core-sessions`, `/core-sessions/[id]`, `/core-sessions/nueva`
**Endpoints**: `POST /api/core-sessions`, `GET /api/core-sessions`, `GET /api/core-sessions/{id}`, `POST /api/core-sessions/{id}/iniciar`, `POST /api/core-sessions/{id}/finalizar`, `POST /api/core-sessions/{id}/temas`, `POST /api/core-sessions/{id}/temas/{tid}/votar`, `GET /api/core-sessions/{id}/temas/{tid}/votos`, `GET /api/core-sessions/{id}/miembros`

#### Maquina de Estados

```
PROGRAMADA → EN_CURSO → FINALIZADA
```

#### Modelo de Votacion

- **Comite**: CONSEJO-REGIONAL (auto-creado en primer uso), 16 miembros
- **Tipos de sesion**: ORDINARIA, EXTRAORDINARIA
- **Opciones de voto**: A_FAVOR, EN_CONTRA, ABSTENCION
- **Quorum**: SIMPLE (9/16 votos a favor), CALIFICADA (11/16 votos a favor)
- **Tabla DDL**: `core.session_vote` (Wave 5 migration)

#### Lista

- Filtro: estado (tabs: Todas, PROGRAMADA, EN_CURSO, FINALIZADA)
- Columnas: numero sesion, tipo (ORDINARIA/EXTRAORDINARIA), fecha programada, estado (badge), cantidad de temas, temas aprobados

#### Detalle y Votacion

- Header con metadata de sesion + tipo quorum
- Temas de agenda: cada tema vinculado a una IPR (BIP clickeable)
- Panel de votacion: botones A_FAVOR / EN_CONTRA / ABSTENCION por tema
- Resultado: aprobado (verde), rechazado (rojo), pendiente (gris) segun quorum
- Detalle de votos: lista de votantes con su voto

#### Creacion

- Campos: tipo sesion, tipo quorum, fecha/hora programada, descripcion
- Crea automaticamente: sesion numerada en comite CONSEJO-REGIONAL

#### Gate F3→F4 (IPR Lifecycle)

IPRs con monto total >7.000 UTM (~$471M CLP) requieren aprobacion del CORE para avanzar de fase F3 a F4. El endpoint `GET /api/ipr/{id}/transiciones` verifica la existencia de un tema de sesion CORE aprobado.

---

### 3.10 Administracion

**Ruta**: `/admin/usuarios`, `/admin/usuarios/nuevo`, `/admin/divisiones`
**Endpoints**: `GET/POST/PATCH /api/admin/usuarios`, `POST /api/admin/usuarios/{id}/toggle-activo`, `POST /api/admin/usuarios/{id}/reset-password`, `GET/POST/PATCH /api/admin/divisiones`

Exclusivo para ADMIN_SISTEMA.

#### Gestion de Usuarios

- Lista paginada con filtros: busqueda, rol, activo/inactivo
- Crear usuario: nombres, apellidos, email, RUT, telefono, contrasena, rol, division
- Editar: nombres, apellidos, email, telefono, rol, division
- Toggle activo/inactivo
- Reset de contrasena

#### Gestion de Divisiones

- Lista de organizaciones tipo DIVISION/GORE (~31)
- Crear division: codigo, nombre
- Editar: codigo, nombre

---

## 4. Modulos Funcionales — Poblacion DGI

### 4.1 Cockpit DGI (Dashboard por Rol)

**Ruta**: `/dashboard` (cuando `population = "dgi"`)
**Endpoint**: `GET /api/dgi/cockpit` (retorna forma diferente segun rol)

#### JEFE_DGI — Vista Ejecutiva

- **Semaforo institucional**: 5 dimensiones (PRESUPUESTO, CARTERA_IPR, CONVENIOS, TDE, RIESGOS) con senal peor caso (ROJO > AMARILLO > VERDE)
- **Decisiones pendientes**: Conteo de alertas CRITICO sin `action_taken`
- **Estado del equipo**: ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD con actividades
- **Alertas criticas**: Top 3 alertas CRITICO sin resolver
- **Informe actual**: Estado del informe BORRADOR de la semana

#### ESP_CONTROL_GESTION — Monitoreo

- **Fuentes de datos**: Tabla con division, fuente, estado (ACTUALIZADO/ATRASADO/SIN_DATOS), dias de atraso
- **Indicadores en alerta**: Indicadores con senal ROJO o AMARILLO
- **Tendencias**: Todos los indicadores ordenados por dimension
- **Cola de trabajo**: Tareas dinamicas generadas segun estado de fuentes e indicadores (prioridad ALTA/MEDIA/BAJA)

#### ESP_PROCESOS — Iniciativas

- **Iniciativas activas**: Lista ordenada por estado
- **Modelos BPMN**: Lista de modelos de procesos
- **Agenda del dia**: Actividades programadas
- **Estadisticas portafolio**: activas, completadas, objetivo (5)

#### ESP_TD — Transformacion Digital

- **Barras de cumplimiento**: Indicadores de dimension TDE
- **Velocidad**: actual vs requerida, meses restantes
- **Decretos**: Checklist DS7-DS12 con estado
- **Base de conocimiento**: Estadisticas (pendientes publicacion, actualizados, total)
- **Comite DGI**: Proxima sesion
- **Alertas normativas**: Plazos de decretos

---

### 4.2 Tablero Kanban de Iniciativas

**Ruta**: `/tablero`
**Endpoints**: `GET /api/dgi/initiatives`, `POST /api/dgi/initiatives`, `PATCH /api/dgi/initiatives/{id}`, `POST /api/dgi/initiatives/{id}/move`

#### Columnas con Limites WIP

| Columna | Limite WIP (Backend) |
|---------|---------------------|
| BACKLOG | Sin limite |
| EN_CURSO | 5 |
| REVISION | 2 |
| COMPLETADO | Sin limite |

- Si se alcanza el limite: `HTTP 409 CONFLICT` con mensaje descriptivo
- El frontend muestra banner amarillo con el error

#### Tarjetas Kanban

Cada tarjeta muestra: nombre, barra de progreso (0-100%), nombre del responsable. Flechas izquierda/derecha para mover entre columnas.

#### Dialogo Crear/Editar

Campos: nombre*, descripcion, responsable (Select de usuarios con "Sin asignar"), fecha objetivo, dias totales. Al editar, pre-carga `responsible_id` del registro existente.

#### Respuesta InitiativeItem

Incluye `responsible_id` (UUID) y `responsible_name` (string) para permitir pre-seleccion del responsable en formularios de edicion. Auto-genera codigo `INI-NNNN`.

---

### 4.3 Indicadores Institucionales (Semaforo)

**Endpoints**: `GET /api/dgi/data/indicators`, `POST /api/dgi/data/indicators/refresh`

#### 5 Dimensiones

| Dimension | Calculo | Verde | Amarillo | Rojo |
|-----------|---------|-------|----------|------|
| PRESUPUESTO | pagado/vigente del ano fiscal | ≥70% | ≥40% | <40% |
| CARTERA_IPR | % IPRs con alerta CRITICO | <5% | <15% | ≥15% |
| CONVENIOS | % convenios vencidos | <5% | <20% | ≥20% |
| TDE | Estatico (sin fuente de datos real) | — | — | — |
| RIESGOS | alertas sin resolver + problemas abiertos | <5 | <15 | ≥15 |

- `POST /api/dgi/data/indicators/refresh`: Idempotente, recalcula 4/5 dimensiones desde agregados reales de la BD
- Cada indicador tiene: valor actual, valor meta, unidad, senal, tendencia (up/down/flat)

---

### 4.4 Informes DGI

**Ruta**: `/informes`, `/informes/[id]`
**Endpoints**: `GET /api/dgi/reports`, `POST /api/dgi/reports`, `GET /api/dgi/reports/{id}/content`, `PATCH /api/dgi/reports/{id}`, `GET /api/dgi/reports/{id}/export`

#### Tipos de Informe

FLASH, SEMANAL, MENSUAL, TEMATICO

#### 6 Secciones Auto-Pobladas

Cada seccion se regenera en cada `GET` desde datos reales de la BD:

1. **Resumen ejecutivo**: Semaforo + KPIs (cartera IPR, ejecucion, alertas, compromisos vencidos)
2. **Tabla de indicadores**: Valor actual/meta/senal/tendencia por dimension
3. **Alertas institucionales**: Agrupadas por severidad con top mensajes CRITICO
4. **Avance DGI**: Conteo de iniciativas por estado con top 3 nombres
5. **Decisiones pendientes**: Alertas criticas requiriendo decision (top 10)
6. **Prioridades**: Compromisos vencidos + convenios por vencer (top 5 cada uno)

#### Edicion de Secciones

- Las ediciones del usuario se almacenan atomicamente en `metadata` JSONB via `jsonb_set` (no read-modify-write)
- Si hay edicion: retorna contenido del usuario + `last_edited_at`
- Si no hay edicion: retorna contenido auto-generado + `auto_populated = true`
- Estado: BORRADOR → ENVIADO → ARCHIVADO

---

### 4.5 Explorador de Datos (DGI Explorer)

**Ruta**: `/datos`
**Endpoints**: Multiples endpoints en `/api/dgi/data/`

Interfaz de 3 columnas (sidebar de dominios, tabla principal, panel de detalle):

#### 9 Dominios Explorables

| Dominio | Endpoint | Paginado |
|---------|----------|----------|
| IPR | `GET /api/ipr` | Si |
| Indicadores | `GET /api/dgi/data/indicators` | No (array) |
| Presupuesto | `GET /api/presupuesto` | Si |
| Convenios | `GET /api/convenios` | Si |
| Organizaciones | `GET /api/dgi/data/organizaciones` | Si |
| Personas | `GET /api/dgi/data/personas` | Si |
| Territorio | `GET /api/dgi/data/territorio` | Si |
| Eventos | `GET /api/dgi/data/eventos` | Si (requiere rango de fechas para partition pruning) |
| Rendiciones | `GET /api/dgi/data/rendiciones` | Si |

- Cada dominio tiene filtros especificos, columnas configurables, panel de detalle
- Boton "Exportar CSV" disponible en todos los dominios

---

## 5. Funcionalidades Transversales

### 5.1 Busqueda Global (Cmd+K)

**Endpoint**: `GET /api/search?q=...&limit=5`

CommandDialog estilo palette que busca en 4 entidades simultaneamente via `UNION ALL`:
- IPR: por codigo_bip y nombre
- Compromisos: por codigo y descripcion
- Problemas: por codigo y descripcion
- Personas: por nombres y apellido paterno

Resultados agrupados por tipo con iconos y navegacion directa.

### 5.2 Componentes UI Reutilizables

#### Componentes de Dominio (20)

| Componente | Proposito | Uso |
|-----------|-----------|-----|
| `AppShell` | Wrapper de layout autenticado | Layout principal |
| `Sidebar` | Navegacion condicional operativa/DGI | Layout principal |
| `Header` | Barra superior con usuario + notificaciones | Layout principal |
| `GlobalSearch` | Palette ⌘K de busqueda multi-entidad | Transversal |
| `DataTable` | Tabla paginada generica | Todas las listas |
| `FilterBar` | Barra de filtros + busqueda | Todas las listas |
| `DrawerPanel` | Panel lateral deslizable | Detalles + acciones |
| `StatusBadge` | Badge de estado con colores predefinidos | Estados de entidades |
| `TemporalIndicator` | Indicador de dias restantes con urgencia | Compromisos, convenios |
| `ProgressBarIndicator` | Barra de progreso visual | Presupuesto, avances |
| `AlertCard` | Tarjeta de alerta con borde color | Alertas |
| `KpiCard` | Tarjeta KPI con valor grande | Dashboards |
| `KanbanCard` | Tarjeta de iniciativa con progreso | Tablero DGI |
| `SemaforoCard` | Indicador semaforo (dimension DGI) | Cockpit DGI |
| `ComboboxAsync` | Select buscable con busqueda server-side | IPR (3,622+ registros) |
| `TimelineHistory` | Timeline vertical de eventos | Historial compromisos |
| `CockpitJefeDgi` | Vista ejecutiva DGI | Dashboard DGI (JEFE_DGI) |
| `CockpitControlGestion` | Vista monitoreo DGI | Dashboard DGI (ESP_CG) |
| `CockpitProcesos` | Vista iniciativas DGI | Dashboard DGI (ESP_PROC) |
| `CockpitTd` | Vista transformacion digital | Dashboard DGI (ESP_TD) |

#### Primitivos UI (shadcn/ui — 16)

`Avatar`, `Badge`, `Button`, `Card`, `Command`, `Dialog`, `DropdownMenu`, `Input`, `Popover`, `ScrollArea`, `Select`, `Separator`, `Sheet`, `Table`, `Tabs`, `Tooltip`

### 5.3 Graficos (Recharts)

4 componentes de graficos:
1. `ExecutionBarChart`: Ejecucion presupuestaria por division (BarChart)
2. `CommitmentDonut`: Compromisos por estado (PieChart)
3. `AlertsBySeverity`: Alertas por severidad (PieChart)
4. `SemaforoGauge`: Gauge semi-circular para senal DGI

### 5.4 Exportacion CSV

Funcion `exportCSV(columns, data, filename)` disponible en tablas del explorador DGI. Genera archivo `.csv` y lo descarga.

---

## 6. Modelo de Datos

### 6.1 Esquemas de Base de Datos

**79 tablas distribuidas en 4 esquemas**:

| Esquema | Tablas | Proposito |
|---------|--------|-----------|
| `meta` | 5 | Atomos fundamentales: Role, Process, Entity, Story, StoryEntity |
| `ref` | 3 | Vocabularios controlados: Category (Gist 14.0 pattern), Actor (BPMN), OperationalCommitmentType |
| `core` | 50 | Entidades de negocio: organizacion, personas, IPR, presupuesto, convenios, alertas, gobernanza, DGI |
| `txn` | 2 logicas (20 fisicas) | Event sourcing: Event (particionado por mes), Magnitude (particionado por trimestre) |

### 6.2 Patron Categorial (ref.category)

Pilar central del modelo: `ref.category(scheme, code, label)` implementa **Univocidad Categorial** — cada columna FK apunta a exactamente 1 scheme. Nunca mezclar dimensiones.

**93+ schemes** incluyendo: `ipr_type`, `ipr_state`, `budget_subtitle`, `agreement_type`, `agreement_state`, `problem_type`, `commitment_state`, `alert_level`, `system_role`, `org_type`, todos los schemes DGI, y governance schemes (session_type, vote_option, quorum_type).

### 6.3 Entidades Principales

#### Organizacion y Personal
- `core.organization` (3,320 registros, ~31 de tipo DIVISION/GORE)
- `core.person` (columnas: `names`, `paternal_surname`, NOT `nombre`/`apellido_paterno`)
- `core.user` (FK: `system_role_id`, NOT `role_id`. Tiene `is_active`)
- `core.position` (cargos, vinculados a organizacion)
- `core.territory` (regiones, provincias, comunas)

#### IPR y Control Operacional
- `core.ipr` (3,622+ registros, entidad central)
- `core.operational_commitment` (codigo auto-generado OC-NNNNN)
- `core.commitment_history` (auditoria de cambios de estado)
- `core.ipr_problem` (codigo auto-generado PR-NNNNN)
- `core.alert` (12 tipos, 4 niveles, `subject_type` almacenado como 'core.ipr')
- `core.progress_report` (`report_number` auto-incrementado por IPR)

#### Presupuesto y Finanzas
- `core.budget_program` (5 etapas de ejecucion, UNIQUE code+fiscal_year)
- `core.budget_carryover` (arrastres por ano)
- `core.budget_commitment` (CDPs vinculados a IPR/convenios)

#### Convenios y Rendiciones
- `core.agreement` (10 estados con transiciones definidas en `valid_transitions` JSONB)
- `core.agreement_installment` (calendario de pagos)
- `core.rendition` (rendiciones de cuentas)

#### Gobernanza
- `core.committee`, `core.session`, `core.minute`, `core.session_agreement`
- `core.crisis_meeting` (especializacion de session, usa comite auto-creado COMITE-CRISIS)
- `core.session_vote` (votos individuales por tema de agenda, Wave 5)
- `core.agenda_item_context` (vincula temas de reunion a IPRs)

#### DGI
- `core.dgi_indicator` (5 dimensiones, senal VERDE/AMARILLO/ROJO)
- `core.dgi_initiative` (Kanban con WIP limits, fases DMAIC opcionales)
- `core.dgi_report` (informes con 6 secciones auto-pobladas, ediciones en JSONB)
- `core.dgi_bpmn_model` (modelos de procesos)
- `core.dgi_data_source_status` (estado de fuentes de datos)

### 6.4 Event Sourcing (txn)

- `txn.event`: Particionado por mes (12 particiones 2026). Registra 16 tipos de evento con payload JSONB.
- `txn.magnitude`: Particionado por trimestre. Patron Magnitude de Gist 14.0 para mediciones temporales.

### 6.5 Auditoria

Todas las tablas incluyen columnas de auditoria: `created_at`, `updated_at`, `created_by_id`, `updated_by_id`, `deleted_at`, `deleted_by_id`. Trigger `fn_update_timestamp()` actualiza `updated_at` automaticamente.

---

## 7. API — Catalogo Completo de Endpoints

### 7.1 Autenticacion

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/api/auth/login` | Login con email/password, retorna JWT |

### 7.2 IPR

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/ipr` | Lista paginada con filtros |
| GET | `/api/ipr/{id}` | Detalle con conteos de entidades relacionadas |
| POST | `/api/ipr` | Crear IPR |
| PATCH | `/api/ipr/{id}` | Actualizar campos permitidos |
| POST | `/api/ipr/{id}/avances` | Registrar avance fisico/financiero |
| GET | `/api/ipr/{id}/avances` | Listar avances |

### 7.3 Compromisos

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/compromisos` | Lista paginada con filtros |
| GET | `/api/compromisos/{id}` | Detalle con historial |
| POST | `/api/compromisos` | Crear compromiso |
| POST | `/api/compromisos/{id}/completar` | Marcar como completado |
| POST | `/api/compromisos/{id}/verificar` | Verificar compromiso |
| POST | `/api/compromisos/{id}/devolver` | Devolver para rehacer |

### 7.4 Problemas

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/problemas` | Lista paginada con filtros |
| GET | `/api/problemas/{id}` | Detalle |
| POST | `/api/problemas` | Crear problema |
| PATCH | `/api/problemas/{id}` | Actualizar (solucion, estado) |

### 7.5 Alertas

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/alertas` | Lista paginada con filtros |
| POST | `/api/alertas/{id}/atender` | Atender alerta |

### 7.6 Dashboard

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/dashboard` | Dashboard base (role-aware) |
| GET | `/api/dashboard/ejecutivo` | Vista ejecutiva con desglose por division |
| GET | `/api/dashboard/mi-division` | Dashboard de division (JEFE_DIVISION) |
| GET | `/api/dashboard/mis-compromisos` | Compromisos personales (ENCARGADO) |
| GET | `/api/dashboard/chart-data` | Datos para 3 graficos |

### 7.7 Catalogos

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/catalogs/categories/{scheme}` | Categorias por scheme |
| GET | `/api/catalogs/commitment-types` | Tipos de compromiso operacional |
| GET | `/api/catalogs/users` | Lista de usuarios (filtrable por division) |
| GET | `/api/catalogs/iprs` | Busqueda de IPR server-side (limit 200) |
| GET | `/api/catalogs/divisions` | Divisiones (~31, filtrado por org_type) |

### 7.8 Presupuesto

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/presupuesto` | Lista paginada |
| GET | `/api/presupuesto/{id}` | Detalle con arrastres y CDPs |
| POST | `/api/presupuesto` | Crear programa |
| PATCH | `/api/presupuesto/{id}` | Actualizar montos |
| GET | `/api/presupuesto/resumen` | Resumen agregado por division/subtitulo |

### 7.9 Convenios

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/convenios` | Lista paginada |
| GET | `/api/convenios/{id}` | Detalle con cuotas |
| POST | `/api/convenios` | Crear convenio |
| PATCH | `/api/convenios/{id}` | Actualizar |
| GET | `/api/convenios/{id}/cuotas` | Listar cuotas |
| POST | `/api/convenios/{id}/cuotas` | Agregar cuota |
| PATCH | `/api/convenios/{id}/cuotas/{cuota_id}` | Actualizar cuota |

### 7.10 Reuniones

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/reuniones` | Lista paginada |
| POST | `/api/reuniones` | Crear reunion |
| GET | `/api/reuniones/{id}` | Detalle con temas |
| GET | `/api/reuniones/{id}/preparar` | Auto-sugerencias |
| POST | `/api/reuniones/{id}/temas` | Agregar tema |
| POST | `/api/reuniones/{id}/temas/{id}/revisar` | Revisar tema |
| POST | `/api/reuniones/{id}/iniciar` | Iniciar sesion |
| POST | `/api/reuniones/{id}/finalizar` | Finalizar sesion |

### 7.11 Administracion

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/admin/usuarios` | Lista paginada |
| GET | `/api/admin/usuarios/{id}` | Detalle |
| POST | `/api/admin/usuarios` | Crear usuario |
| PATCH | `/api/admin/usuarios/{id}` | Actualizar |
| POST | `/api/admin/usuarios/{id}/toggle-activo` | Activar/desactivar |
| POST | `/api/admin/usuarios/{id}/reset-password` | Resetear contrasena |
| GET | `/api/admin/divisiones` | Lista |
| POST | `/api/admin/divisiones` | Crear |
| PATCH | `/api/admin/divisiones/{id}` | Actualizar |

### 7.12 DGI — Cockpit

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/dgi/cockpit` | Cockpit role-aware (4 formas de respuesta) |

### 7.13 DGI — Iniciativas

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/dgi/initiatives` | Lista (array plano, no paginado) |
| POST | `/api/dgi/initiatives` | Crear |
| PATCH | `/api/dgi/initiatives/{id}` | Actualizar |
| POST | `/api/dgi/initiatives/{id}/move` | Mover en Kanban (con WIP limit) |

### 7.14 DGI — Datos

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/dgi/data/indicators` | Lista indicadores |
| GET | `/api/dgi/data/indicators/{id}` | Indicador individual |
| POST | `/api/dgi/data/indicators/refresh` | Recomputar desde datos reales |
| GET | `/api/dgi/data/sources` | Estado de fuentes de datos |
| GET | `/api/dgi/data/organizaciones` | Explorador organizaciones |
| GET | `/api/dgi/data/personas` | Explorador personas |
| GET | `/api/dgi/data/territorio` | Explorador territorio |
| GET | `/api/dgi/data/eventos` | Explorador eventos (requiere rango fecha) |
| GET | `/api/dgi/data/rendiciones` | Explorador rendiciones |
| POST | `/api/dgi/data/rendiciones` | Crear rendicion (SISREC MVP) |
| GET | `/api/dgi/data/rendiciones/{id}` | Detalle rendicion |

### 7.15 DGI — Informes

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/dgi/reports` | Lista (array plano) |
| POST | `/api/dgi/reports` | Crear informe |
| GET | `/api/dgi/reports/{id}/content` | Contenido con 6 secciones auto-pobladas |
| PATCH | `/api/dgi/reports/{id}` | Editar seccion (JSONB atomico) |
| GET | `/api/dgi/reports/{id}/export` | Exportar JSON estructurado |

### 7.16 Sesiones CORE

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/api/core-sessions` | Crear sesion CORE |
| GET | `/api/core-sessions` | Listar sesiones paginadas |
| GET | `/api/core-sessions/{id}` | Detalle con temas + votos |
| POST | `/api/core-sessions/{id}/iniciar` | Iniciar sesion (PROGRAMADA → EN_CURSO) |
| POST | `/api/core-sessions/{id}/finalizar` | Finalizar sesion (EN_CURSO → FINALIZADA) |
| POST | `/api/core-sessions/{id}/temas` | Agregar tema de agenda |
| POST | `/api/core-sessions/{id}/temas/{tid}/votar` | Registrar voto |
| GET | `/api/core-sessions/{id}/temas/{tid}/votos` | Detalle de votos por tema |
| GET | `/api/core-sessions/{id}/miembros` | Lista miembros + asistencia |

### 7.17 Busqueda

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/search` | Busqueda global multi-entidad |

### 7.18 Sistema

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/health` | Health check |

**Total: ~113 endpoints en 18 routers + health check.**

---

## 8. Rutas del Frontend

### 8.1 Poblacion Operativa

| Ruta | Componente | Descripcion |
|------|-----------|-------------|
| `/` | RootPage | Redirect a `/login` o `/dashboard` segun estado de sesion |
| `/login` | LoginPage | Formulario de autenticacion |
| `/dashboard` | DashboardPage | Panel de control (role-aware) |
| `/ipr` | IprListPage | Lista paginada de IPRs |
| `/ipr/[id]` | IprDetailPage | Detalle con 10 tabs |
| `/ipr/nuevo` | NuevaIprPage | Formulario de creacion |
| `/compromisos` | CompromisosPage | Lista con drawer de acciones |
| `/compromisos/nuevo` | NuevoCompromisoPage | Formulario con ComboboxAsync |
| `/problemas` | ProblemasPage | Lista con drawer de acciones |
| `/problemas/nuevo` | NuevoProblemaPage | Formulario con ComboboxAsync |
| `/alertas` | AlertasPage | Lista con AlertCards |
| `/presupuesto` | PresupuestoPage | Lista con drawer editable |
| `/convenios` | ConveniosPage | Lista con drawer + cuotas |
| `/reuniones` | ReunionesPage | Lista de reuniones crisis |
| `/reuniones/[id]` | ReunionDetailPage | Detalle con temas + acciones |
| `/reuniones/nueva` | NuevaReunionPage | Formulario de creacion |
| `/mi-division` | MiDivisionPage | Dashboard division (JEFE_DIVISION) |
| `/mis-compromisos` | MisCompromisosPage | Vista agrupada (ENCARGADO) |
| `/admin/usuarios` | UsuariosPage | CRUD usuarios (ADMIN_SISTEMA) |
| `/admin/usuarios/nuevo` | NuevoUsuarioPage | Formulario creacion |
| `/admin/divisiones` | DivisionesPage | CRUD divisiones (ADMIN_SISTEMA) |
| `/core-sessions` | CoreSessionsPage | Lista sesiones CORE |
| `/core-sessions/[id]` | CoreSessionDetailPage | Detalle + votacion |
| `/core-sessions/nueva` | NuevaCoreSessionPage | Crear sesion CORE |

### 8.2 Poblacion DGI

| Ruta | Componente | Descripcion |
|------|-----------|-------------|
| `/login` | LoginPage | Formulario de autenticacion |
| `/dashboard` | DashboardPage → Cockpit* | Cockpit role-specific |
| `/alertas` | AlertasPage | Compartida con operativa |
| `/tablero` | TableroPage | Kanban de iniciativas |
| `/datos` | DatosPage | Explorador multi-dominio (9 dominios) |
| `/informes` | InformesPage | Lista + editor inline de secciones |
| `/informes/[id]` | InformeDetailPage | Vista completa del informe |

---

## 9. Convenios de Paginacion y Respuesta

### 9.1 Endpoints Paginados (Operativa)

```json
{
  "items": [...],
  "total": 1234,
  "page": 1,
  "page_size": 20,
  "total_pages": 62
}
```

### 9.2 Endpoints Lista (DGI)

Retornan arrays planos (sin wrapper de paginacion):
```json
[
  { "id": "...", "name": "...", ... },
  { "id": "...", "name": "...", ... }
]
```

Excepcion: endpoints de `/api/dgi/data/*` (explorador) SI son paginados.

---

## 10. Datos Demo

Estrategia de datos demo con prefijo `DEMO-` para identificacion clara:

- `goreos_seed_demo_ciclo2.sql`: Carga datos demo (budget programs, agreements, CDPs)
- `goreos_unseed_demo_ciclo2.sql`: Elimina SOLO registros DEMO-*, datos reales intactos
- FKs a datos reales usan subqueries (no UUIDs hardcodeados)
- 6 programas presupuestarios demo (DEMO-BP-001..006)
- 4 convenios demo (DEMO-AGR-001..004)
- 8 CDPs demo (DEMO-CDP-001..008)

---

## 11. Resumen Cuantitativo

| Metrica | Valor |
|---------|-------|
| Endpoints API totales | ~113 |
| Routers backend | 18 (+health) |
| Paginas frontend | 31 |
| Componentes reutilizables | 24 |
| Componentes de graficos | 4 |
| Tablas en BD | 79 (59 logicas + 20 particiones txn) |
| Esquemas ref.category | 93+ |
| Tests de integracion | 155 (154 pass + 1 skip) across 17 modules |
| Roles de sistema | 8 |
| Tipos de IPR | 8 |
| Naturalezas IPR | 5 |
| Estados de convenio | 10 |
| Tipos de alerta | 12 |
| Niveles de severidad | 4 |
| Dimensiones DGI | 5 |
| Tipos de informe DGI | 4 |
| Secciones auto-pobladas por informe | 6 |
| Dominios en explorador DGI | 9 |
| Tipos de compromiso operacional | 10 |
| Tipos de problema | 6 |
| Tipos de evento (txn) | 16 |
