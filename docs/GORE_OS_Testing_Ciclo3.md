# GORE_OS — Documento de Testeo Ciclo 3

**Fecha**: 2026-02-25
**Version**: 3.0 (Ciclo 1 + Ciclo 2 + Ciclo 3)
**Objetivo**: Guia completa para testeo funcional de GORE_OS tras la migracion de funcionalidad desde para_titi.

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

### 2.1 Funcionalidad Completada (Ciclo 1 + 2 + 3)

| Modulo | Estado | Ciclo | Descripcion |
|--------|--------|-------|-------------|
| Login/Auth | Completo | C1 | JWT + 8 roles (4 op + 4 DGI) |
| Dashboard operativo | Completo | C1+C3 | Role-aware con KPIs, desglose por division para ejecutivos |
| IPR lista + detalle | Completo | C1 | Paginado, filtros, tabs compromisos/problemas/alertas/convenios |
| IPR crear | **Nuevo C3** | C3 | Form completo con auto-generacion de codigo BIP |
| IPR asignar responsable | **Nuevo C3** | C3 | Boton en detalle IPR para roles admin |
| IPR registrar avance | **Nuevo C3** | C3 | Tab Avances en detalle IPR + form progress_report |
| Compromisos lista | Completo | C1 | Paginado, filtros, drawer con historial + acciones |
| Compromisos crear | **Nuevo C3** | C3 | Form con tipo, responsable, fecha, IPR asociada |
| Compromisos acciones | Completo | C1 | Completar, verificar, devolver con historial |
| Problemas lista | Completo | C1 | Paginado, filtros por estado y tipo |
| Problemas crear | **Nuevo C3** | C3 | Form con IPR, tipo, impacto, descripcion |
| Problemas resolver/cerrar | **Nuevo C3** | C3 | Drawer con acciones: En Gestion, Resolver, Cerrar |
| Alertas | Completo | C1 | Lista con severidad, atencion |
| Presupuesto | Completo | C2 | CRUD programas, resumen, CDPs |
| Convenios | Completo | C2 | CRUD convenios + cuotas |
| Mi Division | **Nuevo C3** | C3 | Dashboard JEFE con carga por persona |
| Mis Compromisos | **Nuevo C3** | C3 | Vista personal agrupada (vencidos/semana/pendientes) |
| Dashboard ejecutivo | **Nuevo C3** | C3 | Desglose por division con metricas comparativas |
| Admin usuarios | **Nuevo C3** | C3 | CRUD completo + toggle activo + reset password |
| Admin divisiones | **Nuevo C3** | C3 | CRUD con conteo de usuarios |
| Reuniones de crisis | **Nuevo C3** | C3 | Modulo completo: crear, preparar, conducir, finalizar |
| DGI Cockpits | Completo | C2 | 4 cockpits por rol DGI |
| DGI Indicadores | Completo | C2 | Semaforo 5 dimensiones, refresh desde BD real |
| DGI Iniciativas | Completo | C2 | Kanban con WIP limits |
| DGI Informes | Completo | C2 | 4 tipos, 6 secciones auto-populadas |

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
| Verificar compromiso | Si | Si | Si (propia div) | No |
| Admin usuarios | Si | No | No | No |
| Admin divisiones | Si | No | No | No |
| Mi Division | No | No | Si | No |
| Mis Compromisos | No | No | No | Si |
| Dashboard ejecutivo | Si | Si | No | No |
| Crear reunion | Si | Si | Si | No |

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

---

## 5. Endpoints API — Referencia Rapida

### 5.1 Autenticacion
```
POST /api/auth/login          Login (form-urlencoded: username, password)
```

### 5.2 IPR
```
GET    /api/ipr                Lista paginada, filtros: ipr_type, status, sector, search
GET    /api/ipr/{id}           Detalle con conteos
POST   /api/ipr                Crear IPR (ADMIN_SISTEMA, ADMIN_REGIONAL)
PATCH  /api/ipr/{id}           Asignar responsable
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
```

### 5.7 Presupuesto
```
GET    /api/presupuesto/resumen  Resumen agrupado
GET    /api/presupuesto          Lista programas
GET    /api/presupuesto/{id}     Detalle con CDPs
POST   /api/presupuesto          Crear programa
PATCH  /api/presupuesto/{id}     Actualizar montos
```

### 5.8 Convenios
```
GET    /api/convenios               Lista
GET    /api/convenios/{id}          Detalle con cuotas
POST   /api/convenios               Crear
PATCH  /api/convenios/{id}          Actualizar
GET    /api/convenios/{id}/cuotas   Listar cuotas
POST   /api/convenios/{id}/cuotas   Agregar cuota
PATCH  /api/convenios/{id}/cuotas/{cid}  Actualizar cuota
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
GET    /api/dgi/initiatives                Iniciativas
POST   /api/dgi/data/indicators/refresh    Recalcular indicadores
GET    /api/dgi/reports                    Informes
```

---

## 6. Hoja de Ruta

### 6.1 Completado

| Ciclo | Alcance | Estado |
|-------|---------|--------|
| Ciclo 1 | Base operativa: Login, Dashboard, IPR (read-only), Compromisos CRUD, Problemas lista, Alertas | Completado |
| Ciclo 2 | Presupuesto, Convenios, DGI (cockpits, indicadores, iniciativas, informes) | Completado |
| Ciclo 3 | Migracion para_titi: forms CRUD, IPR escritura, admin, dashboards, reuniones | Completado |

### 6.2 Pendiente / Proximos Ciclos

| Item | Prioridad | Descripcion |
|------|-----------|-------------|
| Tests automatizados | Alta | Unit tests backend (pytest), integration tests API, E2E frontend |
| Notificaciones | Media | Notificaciones en-app y/o email para alertas, compromisos vencidos |
| Exportar a Excel/PDF | Media | Exportar listas y reportes a formatos descargables |
| Auditoria de acciones | Media | Log de acciones de usuario (quien hizo que, cuando) |
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
