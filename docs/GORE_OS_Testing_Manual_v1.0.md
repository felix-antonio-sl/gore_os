# GORE_OS — Plan de Pruebas Manual / Visual

**Fecha**: 2026-03-22 | **Version**: 1.0 | **Sesion**: C59
**Entorno**: `http://localhost:3000` (web) / `http://localhost:8000` (API)
**Credenciales**: Password `admin123` para todos. Dominio `@goreos.cl`.

## Prerequisitos

- `docker compose up -d api web` saludable
- Seed realista cargado (`goreos_seed_realistic.sql`, prefijo `DEMO-R-`)
- `curl http://localhost:8000/api/health` → OK
- `curl -I http://localhost:3000` → 307 → `/login`

---

## GRUPO 1: ADMINISTRADORES

### 1. admin@goreos.cl — ADMIN_SISTEMA (operativa, sin division)

**Dashboard**: Saludo con nombre. KPIs ejecutivos 5 dimensiones + semaforo + breakdown divisiones. AttentionStrip.

**Sidebar**: Inicio · Comando (Centro de Mando, Riesgos) · Gestion IPR (IPR, Cartera Divisional, Compromisos, Problemas, Alertas) · Finanzas (Presupuesto, Ciclo Ppto., Convenios) · Institucional (Actos, Reuniones, Sesiones CORE, Servicios) · **Administracion** (8 items)

**Journey (J16 Mantenimiento + J7 Panorama)**:

1. Login → `/dashboard` → Verificar saludo personal + KPIs ejecutivos + semaforo + AttentionStrip
2. `/admin/usuarios` → DataTable usuarios → Boton "Nuevo Usuario" → Formulario (nombre, email, rol 15 opciones, division) → Cancelar
3. `/admin/divisiones` → Listado 6 divisiones + 3 staff units
4. `/admin/umbrales` → Tabla `financial_threshold` (10 filas) → Editar UTM_VALUE → Verificar save
5. `/admin/niveles-sni` → 4 niveles SNI configurables
6. `/admin/salud-datos` → Barras progreso 5 entidades
7. `/admin/financing-tracks` → Tracks con barras distribucion F0-F5
8. `/admin/slas` → Dashboard 12 SLAs con semaforo (verde≥90%, amarillo≥70%, rojo)
9. `/admin/auditoria` → Tabla txn.event + 5 filtros + JSON expandible + CSV export
10. `/centro-de-mando` → 6 KPIs + timeline
11. `/ipr` → TODAS las IPRs (sin scope division) → Filtros: Estado, Tipo, Mecanismo, Division, Sector
12. `/compromisos` → CompromisosListView (DataTable generico)
13. `/convenios` → Seccion "Proximos a vencer"
14. `/riesgos` → TODOS los riesgos (sin scope)

**Checks de rol**:
- Unico con seccion "Administracion" en sidebar
- Puede CRUD usuarios
- Sin filtro de division
- `/admin/*` accesible

---

### 2. regional@goreos.cl — ADMIN_REGIONAL (operativa, sin division)

**Dashboard**: KPIs ejecutivos 5 dimensiones + semaforo + breakdown divisiones. AttentionStrip.

**Sidebar**: Inicio · Comando (Centro de Mando, Riesgos) · Gestion IPR (IPR, Cartera Divisional, Compromisos, Problemas, Alertas) · Finanzas · Institucional · ~~Administracion~~

**Journey (J7 Panorama institucional)**:

1. Login → `/dashboard` → Saludo + KPIs + semaforo + breakdown divisiones
2. `/centro-de-mando` → 6 KPIs + timeline → Drill-down funcional
3. `/actos` → **PendingQueue VISADO** arriba del DataTable → Click acto → Drawer V.B. → Cambiar a FIRMADO
4. `/escalamiento` → Lista escalamientos → Click → FSM stepper 4 niveles
5. `/ipr` → TODAS las IPRs (scope institucional)
6. `/ipr/cartera` → Portfolio divisional semaforo ROJO/AMARILLO/VERDE
7. `/compromisos` → CompromisosListView
8. `/riesgos` → TODOS los riesgos
9. `/convenios` → "Proximos a vencer"
10. `/core-sessions` → Puede gestionar sesiones CORE

**Checks de rol**:
- PendingQueue VISADO en `/actos`
- Puede firmar actos (VISADO → FIRMADO)
- Sin Administracion en sidebar
- `/admin/usuarios` → acceso denegado

---

## GRUPO 2: EJECUTIVOS

### 3. gobernador@goreos.cl — GOBERNADOR (operativa, sin division)

**Dashboard**: KPIs ejecutivos. AttentionStrip con items "pendientes de firma". ModuleKpis semaforo.

**Sidebar**: Inicio · Comando · Gestion IPR (con Cartera Divisional) · Finanzas · Institucional

**Journey (J11 Cola de firma + J12 Presidir CORE)**:

1. Login → `/dashboard` → AttentionStrip items firma prominentes + KPIs + semaforo
2. `/actos` → PendingQueue VISADO → Stepper visual → Click acto → Drawer V.B. → FIRMADO → Siguiente en cola
3. `/core-sessions` → Card "Proxima sesion" (fecha+temas+quorum) → Click → Detalle sesion
4. Sesion PROGRAMADA: "Iniciar Sesion" → EN_CURSO → Votacion tiempo real → Quorum (simple 9/16, calificada 11/16)
5. "Finalizar Sesion" → Acuerdos registrados → IPRs >7K UTM avanzan F3→F4
6. `/centro-de-mando` → 6 KPIs + timeline
7. `/ipr` → Vista completa sin scope division

**Checks de rol**:
- PendingQueue VISADO prioritaria
- Puede firmar actos + iniciar/finalizar sesiones CORE
- Sin Administracion

---

### 4. secretario.core@goreos.cl — SECRETARIO_EJECUTIVO (operativa, sin division)

**Dashboard**: KPIs ejecutivos. AttentionStrip.

**Sidebar**: Inicio · Gestion IPR (sin Cartera Divisional) · Finanzas · Institucional · ~~Comando~~

**Journey (J14 Preparar CORE)**:

1. Login → `/dashboard` → Saludo + KPIs + AttentionStrip
2. `/core-sessions` → Card "Proxima sesion" → Guia "Preparar agenda" cuando vacia
3. `/core-sessions/nueva` → Crear sesion → Temas → Quorum por tema → Guardar
4. Sesion existente: agregar/editar temas agenda
5. Dia sesion: Iniciar → Gestionar → Finalizar + acta
6. `/actos` → NO PendingQueue (no es firmante)

**Checks de rol**:
- Card "Proxima sesion" visible
- Guia preparacion cuando agenda vacia
- NO puede firmar actos
- NO ve Centro de Mando en sidebar

---

## GRUPO 3: JEFES DE DIVISION

### 5-10. jefe.{daf,dideso,difoi,dipir,diplade,dit}@goreos.cl — JEFE_DIVISION (operativa, c/u en su division)

**Dashboard**: Saludo. **ModuleMyTeam** (avatares equipo division, barras carga, drill-down). KPIs division. AttentionStrip.

**Sidebar**: Inicio · Gestion IPR (sin Cartera Divisional) · Finanzas · Institucional · Mi Trabajo (Mi Division)

**Journey (J5 Estado division + J6 Crisis)**:

1. Login → `/dashboard` → ModuleMyTeam con equipo de SU division + KPIs division
2. Click persona en ModuleMyTeam → `/compromisos?responsible_id={id}` → Compromisos filtrados
3. `/compromisos` → **CompromisosTeamView**: KPIs + personas expandibles + "Verificar" inline
4. Expandir persona → Compromisos → "Verificar" en COMPLETADO → Cambia a VERIFICADO
5. `/ipr` → **Auto-scope**: division pre-seleccionada → Strip "{N} IPRs en tu division" → Solo IPRs de SU division
6. `/mi-division` → Pagina de division
7. AttentionStrip alerta CRITICO → Click → `/ipr/{id}?tab=alertas` → Crear problema o reunion crisis
8. `/servicios` → Catalogo DGI visible (cross-population) → Puede solicitar servicio

**Checks por division**:

| Usuario | Division | Foco esperado |
|---------|----------|--------------|
| jefe.daf | DAF | Finanzas, CDPs |
| jefe.dideso | DIDESO | Programas sociales, SUBSIDIO |
| jefe.difoi | DIFOI | Fomento, PROGRAMA_8PCT |
| jefe.dipir | DIPIR | Inversion (mayor volumen IPRs) |
| jefe.diplade | DIPLADE | Planificacion territorial |
| jefe.dit | DIT | Infraestructura, gate ITO |

**Checks de rol (todos)**:
- ModuleMyTeam (no ModuleMyWork)
- CompromisosTeamView (no WorkView)
- Auto-scope a su division en `/ipr`
- "Mi Division" en sidebar
- NO Cartera Divisional, NO Comando, NO Administracion

---

## GRUPO 4: MANDOS MEDIOS

### 11. jefe.finanzas@goreos.cl — JEFE_DEPARTAMENTO (operativa, DAF)

**Dashboard**: ModuleMyTeam DAF. KPIs division. AttentionStrip.

**Sidebar**: Inicio · Gestion IPR · Finanzas · Institucional · Mi Trabajo (**Mi Division + Aprobaciones**)

**Journey (J15 Aprobar CDPs y rendiciones)**:

1. Login → `/dashboard` → ModuleMyTeam DAF + KPIs + AttentionStrip
2. `/aprobaciones` → 3 secciones: rendiciones VISADA_RTF + CDPs PENDIENTE + cuotas PENDIENTE (scoped sponsor_division_id)
3. `/datos?dominio=rendiciones&state=VISADA_RTF` → Aprobar/rechazar rendicion
4. `/presupuesto` → Programas DAF → Emision CDP
5. `/convenios/{id}` → Cuotas (Art. 18: rendiciones previas) → Bulk cuotas
6. `/compromisos` → **CompromisosTeamView** (isJefe)
7. `/ipr` → Auto-scope DAF

**Checks de rol**:
- **"Aprobaciones" en sidebar** (unico para JEFE_DEPARTAMENTO)
- CompromisosTeamView
- "Mi Division" en sidebar
- Puede aprobar rendiciones post-RTF y CDPs

---

### 12. jefe.ucr@goreos.cl — JEFE_UNIDAD (operativa, DAF)

**Dashboard**: ModuleMyTeam. KPIs division. AttentionStrip.

**Sidebar**: Inicio · Gestion IPR · Finanzas · Institucional · Mi Trabajo (**Mis Compromisos**)

**Journey**:

1. Login → `/dashboard` → ModuleMyTeam UCR/DAF + KPIs
2. `/compromisos` → **CompromisosListView** (JEFE_UNIDAD NO esta en isJefe)
3. `/mis-compromisos` → Enlace sidebar funciona
4. `/ipr` → Scope DAF
5. `/servicios` → Catalogo + crear solicitud

**Checks de rol**:
- "Mis Compromisos" en sidebar (NO "Mi Division", NO "Aprobaciones")
- CompromisosListView (no TeamView — posible inconsistencia UX con ModuleMyTeam en dashboard)
- ModuleMyTeam en dashboard (TEAM_ROLES)

---

## GRUPO 5: OPERADORES

### 13-16. analista.{dipir,diplade}@goreos.cl, profesional.{dit,dideso}@goreos.cl — ANALISTA (operativa)

**Dashboard**: Saludo. **ModuleMyWork** (task list por IPR, urgentes auto-expand). **ModuleFormulacion** (pipeline F0→F2 con checklists). KPIs personales. AttentionStrip.

**Sidebar**: Inicio · Gestion IPR · Finanzas · Institucional · Mi Trabajo (**Mis Compromisos**)

**Journey (J2 Formular IPR + J1 Mi dia)**:

1. Login → `/dashboard` → ModuleMyWork + ModuleFormulacion + KPIs personales
2. ModuleFormulacion → Checklists: F0 (mecanismo/partes/territorio/hitos), F1 (admisibilidad), F2 (eval) → `suggested_action` + `suggested_tab`
3. Click item ModuleMyWork → Deep link `/ipr/{id}?tab=compromisos`
4. `/ipr/nuevo` → Crear IPR: Tipo + Mecanismo → Guardar → **Redirect a `/ipr/{id}?tab=partes`**
5. IPR nueva → F0 satelites: tab Partes (orgs con roles), tab Territorio (impactos), tab Hitos (fechas planificadas)
6. TransitionPanel → Gates F1 (rojo = falta algo)
7. `/compromisos` → **CompromisosWorkView** (personal scope, agrupado por IPR)
8. `/servicios` → Catalogo DGI → Crear solicitud

**Checks por usuario**:

| Usuario | Division | Foco |
|---------|----------|------|
| analista.dipir | DIPIR | Inversion, mayor volumen |
| analista.diplade | DIPLADE | Planificacion |
| profesional.dit | DIT | Infraestructura |
| profesional.dideso | DIDESO | Social (PROGRAMA_SOCIAL, SUBSIDIO) |

**Checks de rol (todos)**:
- **ModuleMyWork + ModuleFormulacion** (unico rol con 2 modulos)
- CompromisosWorkView (personal scope)
- Puede crear IPR
- Post-create redirect a tab partes
- "Mis Compromisos" en sidebar

---

### 17. rtf.daf@goreos.cl — RTF (operativa, DAF)

**Dashboard**: KPIs personales. AttentionStrip con rendiciones. Sin modulo dedicado.

**Sidebar**: Inicio · Gestion IPR · Finanzas · Institucional · Mi Trabajo (**Mis Compromisos + Mis Rendiciones**)

**Journey (J3 Revisar rendicion)**:

1. Login → `/dashboard` → KPIs personales + AttentionStrip rendiciones
2. **"Mis Rendiciones"** en sidebar → `/datos?dominio=rendiciones&state=EN_REVISION_RTF` → Pre-filtrado
3. Columna SLA visible (progreso %, resaltado >80% consumido, SLA=7d habiles)
4. Click rendicion → Revisar → VISAR (→VISADA_RTF) o OBSERVAR (→OBSERVADA, 15d subsanar)
5. `/compromisos` → CompromisosWorkView (personal scope)
6. `/convenios` → Chain financiera Art. 18 visible

**Checks de rol**:
- **"Mis Rendiciones" en sidebar** (unico para RTF)
- Pre-filtrado EN_REVISION_RTF
- Columna SLA con progreso temporal
- Puede visar/observar rendiciones
- CompromisosWorkView

---

### 18. juridico@goreos.cl — ASESOR_JURIDICO (operativa, sin division)

**Dashboard**: **ModuleJuridico** (cola V.B. actos + convenios). KPIs personales. AttentionStrip.

**Sidebar**: Inicio · Gestion IPR · Finanzas · Institucional · Mi Trabajo (**Mis Compromisos + Pendientes V.B.**)

**Journey (J4 Visacion juridica)**:

1. Login → `/dashboard` → ModuleJuridico (items pendientes V.B.) + KPIs + AttentionStrip
2. Click item ModuleJuridico → `/actos/{id}` o `/convenios/{id}`
3. `/actos` → **PendingQueue EN_REVISION** (cola V.B. juridico, diferente del VISADO de GOBERNADOR)
4. Click acto EN_REVISION → Drawer → VISAR o DEVOLVER
5. `/convenios` → **Auto-filtro EN_REVISION_JURIDICA**
6. **"Pendientes V.B."** en sidebar → `/actos?estado=EN_REVISION`
7. `/compromisos` → CompromisosWorkView (personal scope)
8. `/ipr` → Sin scope division (transversal)

**Checks de rol**:
- **ModuleJuridico** en dashboard (unico)
- PendingQueue EN_REVISION (no VISADO)
- Auto-filtro EN_REVISION_JURIDICA en convenios
- **"Pendientes V.B." en sidebar** (unico)
- Sin division — datos transversales
- Gate juridico obligatorio: ningun acto avanza sin V.B.

---

## GRUPO 6: CONSEJEROS

### 19-20. consejero{1,2}@goreos.cl — CONSEJERO_REGIONAL (operativa, sin division)

**Dashboard**: KPIs ejecutivos. AttentionStrip.

**Sidebar**: Inicio · Gestion IPR (sin Cartera Divisional) · Finanzas · Institucional · ~~Comando~~ · ~~Mi Trabajo~~ · ~~Administracion~~

**Journey (J13 Votar en CORE)**:

1. Login → `/dashboard` → KPIs ejecutivos + semaforo
2. `/core-sessions` → Card "Proxima sesion" (fecha+temas+quorum)
3. Sesion EN_CURSO → TopicCard con botones: A FAVOR / EN CONTRA / ABSTENCION
4. Conteo tiempo real → Resultado (APROBADO/RECHAZADO/PENDIENTE)
5. Quorum: simple 9/16, calificada 11/16
6. `/ipr` → Vista lectura, scope institucional
7. `/compromisos` → CompromisosListView

**Check doble consejero**: Login consejero2 en misma sesion → Voto independiente → Conteo se suma (2 votos).

**Checks de rol**:
- Card "Proxima sesion" visible
- Puede votar (NO iniciar/finalizar sesiones)
- Sin Comando, Mi Trabajo, Administracion

---

## GRUPO 7: DGI

### 21. jefe.dgi@goreos.cl — JEFE_DGI (dgi, DGI)

**Dashboard**: **ModuleDgiTeam** (estado equipo). **KPIs DGI** (alertas, escalamientos, riesgos, iniciativas, solicitudes). AttentionStrip.

**Sidebar DGI**: Home · Monitoreo (Centro de Mando, Cartera, **Cartera Divisional**, Alertas, Rendiciones, Riesgos) · Mejora Continua (Tablero, Procesos, Progreso, Cuellos Botella) · Coordinacion (Coordinacion, Escalamiento, Servicios, Comite TD, Calendario) · Analisis (Datos, Informes)

**Journey (J10 Coordinacion semanal — usa TODAS las paginas DGI)**:

1. Login → `/dashboard` → ModuleDgiTeam + KPIs DGI + AttentionStrip
2. `/centro-de-mando` → 6 KPIs + timeline
3. `/cartera` → Portfolio IPR health VERDE/AMARILLO/ROJO
4. `/ipr/cartera` → Portfolio divisional
5. `/tablero` → Kanban: drag-and-drop + WIP limits (EN_CURSO:5, REVISION:2)
6. `/coordinacion` → AR prep + decisions → `/coordinacion/divisiones` → Interaction matrix
7. `/procesos/progreso` → Dashboard progreso DMAIC
8. `/informes` → 4 tipos reporte + edicion atomica JSONB
9. `/escalamiento` → Lista → Click → FSM stepper 4 niveles
10. `/servicios` → Catalogo DGI + gestionar (CRUD) + solicitudes
11. `/comite-td` → Sesiones COMITE-TD (sin votacion)
12. `/calendario` → UNION ALL 5 fuentes + filtros fecha/tipo
13. `/datos?tab=indicadores` → Lifecycle transitions (JEFE_DGI puede transicionar)
14. `/riesgos` → Vista riesgos
15. `/alertas` → Vista alertas

**Checks de rol**:
- Sidebar DGI (NO operativa)
- Unico DGI con Cartera Divisional
- Puede gestionar servicios, escalamientos, transicionar indicadores
- Usa TODAS las paginas DGI

---

### 22. control.gestion@goreos.cl — ESP_CONTROL_GESTION (dgi, DGI)

**Dashboard**: ModuleDgiTeam. KPIs DGI. AttentionStrip.

**Sidebar DGI**: Home · Monitoreo (sin Cartera Divisional) · Mejora Continua · Coordinacion · Analisis

**Journey (J8 Monitoreo diario)**:

1. Login → `/dashboard` → ModuleDgiTeam + KPIs DGI
2. `/datos?tab=indicadores` → Solo VIGENTE → Filtrar 5 dimensiones → Drill-down ROJO
3. Manual value entry (registrar valor indicador)
4. `/datos?tab=rendiciones` → SLA progress + state filter + vencidas
5. `/informes` → Reporte semanal (JSONB atomico)
6. `/cartera` → IPR health
7. `/cuellos-de-botella` → Scan cards + investigations
8. `/centro-de-mando` → 6 KPIs

**Checks de rol**:
- Foco control: indicadores + rendiciones
- NO puede transicionar lifecycle indicadores (solo JEFE_DGI)
- Sin Cartera Divisional

---

### 23. procesos@goreos.cl — ESP_PROCESOS (dgi, DGI)

**Dashboard**: ModuleDgiTeam. KPIs DGI. AttentionStrip.

**Sidebar DGI**: Home · Monitoreo (sin Cartera Divisional) · Mejora Continua · Coordinacion · Analisis

**Journey (J9 Mejora procesos)**:

1. Login → `/dashboard` → ModuleDgiTeam + KPIs DGI
2. `/procesos` → FilterBar + DataTable 7 cols + Crear proceso
3. `/procesos/{id}` → Hero + FSM 6-state + 5 tabs (actores, reglas, metricas, dolores, oportunidades)
4. Tab Oportunidades → Bridge Process→Opportunity→Initiative → "Crear Iniciativa"
5. `/tablero` → Kanban @dnd-kit: drag-and-drop + WIP limits (toast exceso)
6. `/tablero/{id}` → DMAIC 5-phase (DEFINE→MEASURE→ANALYZE→IMPROVE→**VERIFY**) + lean-metrics
7. `/procesos/progreso` → Dashboard progreso
8. `/cuellos-de-botella` → 3 scans + investigations → Click → 6-state FSM + textareas

**Checks de rol**:
- Puede CRUD procesos + satelites
- WIP limits enforced con toast
- DMAIC forward-only, 5ta fase = VERIFY (no CONTROL)
- Bridge Process→Opportunity→Initiative funcional

---

### 24. td@goreos.cl — ESP_TD (dgi, DGI)

**Dashboard**: ModuleDgiTeam. KPIs DGI. AttentionStrip.

**Sidebar DGI**: Home · Monitoreo (sin Cartera Divisional) · Mejora Continua · Coordinacion · Analisis

**Journey (ESP_TD Transformacion Digital)**:

1. Login → `/dashboard` → ModuleDgiTeam + KPIs DGI
2. `/cuellos-de-botella` → 3 detection queries → Scan → Resultados
3. `/cuellos-de-botella/{id}` → Gestionar investigacion (6-state FSM)
4. `/datos?tab=indicadores` → Indicadores TDE (velocidad, lean, Ley 21.180)
5. `/tablero` → Kanban iniciativas TD
6. `/comite-td` → Sesiones COMITE-TD (temas+acuerdos, sin votacion)
7. `/calendario` → Calendario 5 fuentes
8. `/servicios` → Catalogo DGI
9. `/centro-de-mando` → 6 KPIs

**Checks de rol**:
- Foco TD: cuellos botella, metricas lean
- Comite TD: sin votacion (diferente de CORE)

---

## PRUEBAS TRANSVERSALES

### T1. Action Items sin errores (TODOS los 25 usuarios)

Login → `/dashboard` → Verificar:
- Action-items carga sin error (no "Cargando..." permanente)
- Saludo muestra nombre correcto
- AttentionStrip renderiza (puede estar vacia)
- Fecha en es-CL

### T2. Sidebar correcta por poblacion

- **Operativa** (usuarios 1-20): Inicio, [Comando], Gestion IPR, Finanzas, Institucional, [Mi Trabajo], [Administracion]
- **DGI** (usuarios 21-24): Home, Monitoreo, Mejora Continua, Coordinacion, Analisis
- Sin mezcla entre poblaciones

### T3. Cross-population: Servicios DGI

TODOS los usuarios: `/servicios` → Catalogo visible → Puede crear solicitud. Solo DGI gestiona CRUD catalogo.

### T4. Proteccion rutas Admin

Usuarios 2-24: `/admin/usuarios` → Acceso denegado. `/admin/slas` → Denegado. `/admin/auditoria` → Denegado.

### T5. Labels humanizados

- `/ipr` → Tipo en espanol (no PROGRAMA_SOCIAL). Mecanismo (no TRANSFER). Fase (no F4 raw).
- `/actos` → Estado en espanol (no TOMADO_RAZON). StatusBadge con colores.
- Ningun codigo raw o acronimo ingles en UI.

### T6. IPR Detail 360

Con cualquier usuario operativo en `/ipr/{id}`:
- IprHeroCard + IprPhaseStepper (elapsed time: verde ≤30d, ambar ≤90d, rojo >90d)
- 18 tabs en 4 grupos: Operacion(5), Finanzas(4), Requisitos(4), Ciclo(4) + Resumen
- TransitionPanel con gates + feedforward effects
- StatusBadge colores basados en fase
- Actor actual badge (rol posicional, nunca nombre persona)

### T7. Compromisos vista por rol

| Vista | Roles |
|-------|-------|
| **CompromisosWorkView** | ANALISTA(4), RTF, ASESOR_JURIDICO |
| **CompromisosTeamView** | JEFE_DIVISION(6), JEFE_DEPARTAMENTO |
| **CompromisosListView** | ADMIN_SISTEMA, ADMIN_REGIONAL, GOBERNADOR, SECRETARIO, CONSEJERO(2), JEFE_UNIDAD |
| N/A | DGI(4) — no usan `/compromisos` |

### T8. Logout y sesion

3 usuarios representativos (admin, analista.dipir, jefe.dgi):
1. Login → Token en localStorage (`goreos_token`)
2. Navegacion normal → API calls con Bearer
3. Logout → Redirect `/login` + token removido
4. `/dashboard` sin login → Redirect `/login`
5. Credenciales invalidas → Mensaje error limpio
6. 5 intentos fallidos → Lockout 15 min (HTTP 429)

---

## MATRIZ JOURNEYS x USUARIOS

| Journey | Usuarios principales | Secundarios |
|---------|---------------------|-------------|
| J1 Mi dia | analista.dipir | analista.diplade, profesional.dit, profesional.dideso |
| J2 Formular IPR | analista.dipir, analista.diplade | profesional.dit, profesional.dideso |
| J3 Revisar rendicion | rtf.daf | — |
| J4 Visacion juridica | juridico | — |
| J5 Estado division | jefe.daf, jefe.dipir | jefe.dideso, jefe.difoi, jefe.diplade, jefe.dit |
| J6 Crisis | jefe.daf | jefe.dit |
| J7 Panorama institucional | regional | admin, gobernador |
| J8 Monitoreo CG | control.gestion | — |
| J9 Mejora procesos | procesos | — |
| J10 Coordinacion DGI | jefe.dgi | — |
| J11 Cola firma | gobernador | regional |
| J12 Presidir CORE | gobernador | — |
| J13 Votar CORE | consejero1 | consejero2 |
| J14 Preparar CORE | secretario.core | — |
| J15 Aprobar CDPs | jefe.finanzas | jefe.ucr (parcial) |
| J16 Mantenimiento | admin | — |
| IPR 360 (transversal) | Todos operativos (20) | — |

---

## RESUMEN

| Grupo | Usuarios | Pasos/usuario | Total |
|-------|:--------:|:-------------:|:-----:|
| Administradores | 2 | ~14 | ~28 |
| Ejecutivos | 2 | ~8 | ~16 |
| Jefes Division | 6 | ~8 | ~48 |
| Mandos Medios | 2 | ~8 | ~16 |
| Operadores | 6 | ~9 | ~54 |
| Consejeros | 2 | ~5 | ~10 |
| DGI | 4 | ~12 | ~48 |
| Transversales | 25 | ~8 | ~200 |
| **TOTAL** | **25** | | **~420** |

**Prioridad de ejecucion**:
1. T1 action-items todos (regresion critica)
2. Un usuario por arquetipo: admin, gobernador, analista.dipir, juridico, jefe.dgi
3. Jefes division (verificar scope correcto)
4. Consejeros (votacion CORE)
5. Resto DGI (cockpits)
6. T4 proteccion rutas admin
7. T5-T8 transversales

---

## HALLAZGO: Inconsistencia JEFE_UNIDAD

`JEFE_UNIDAD` obtiene `ModuleMyTeam` en dashboard (esta en TEAM_ROLES) pero `CompromisosListView` en `/compromisos` (no esta en `isJefe`). Evaluar si es intencional o gap.
