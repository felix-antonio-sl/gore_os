# GORE_OS — User Archetypes & Journeys v1.0

> Fuentes: SSOT Bundle v1.5, 818 User Stories, Manual Operacional DGI, Plan Potenciamiento DGI
> Fecha: 2026-03-14

---

## 1. Arquetipos de Usuario

### 1.1 Ejecutor

**Roles**: ENCARGADO, ANALISTA, RTF, ASESOR_JURIDICO

**Pregunta central**: "Que tengo que hacer hoy?"

**Contexto**: Son los usuarios mas frecuentes del sistema. Entran a diario, necesitan un inbox claro de tareas pendientes, y salen cuando completaron su trabajo. No les interesa el panorama institucional — quieren resolver SU cola de trabajo.

| Sub-perfil | Foco | Frecuencia | Presion temporal |
|-----------|------|-----------|-----------------|
| ENCARGADO | Compromisos, problemas, alertas de SU IPR | Diaria | Alta (deadlines, SLAs) |
| ANALISTA | Formulacion IPR F0-F3, satelites, CDPs | Diaria | Media (ciclos de evaluacion) |
| RTF | Revision rendiciones EN_REVISION_RTF | Diaria | Alta (SLA 7 dias) |
| ASESOR_JURIDICO | V.B. legalidad actos y convenios | Semanal | Media (depende de flujo) |

**Motivacion**: Cumplir con sus tareas asignadas sin errores, dentro de plazos.
**Frustracion**: No saber que tienen pendiente. Buscar informacion que deberia estar a la vista. Pasos innecesarios.

---

### 1.2 Supervisor

**Roles**: JEFE_DIVISION, JEFE_DEPARTAMENTO, JEFE_UNIDAD

**Pregunta central**: "Como va mi equipo/division?"

**Contexto**: No ejecutan tareas directamente, sino que delegan, monitorean y escalan. Necesitan vision agregada de su division: cuantas IPRs, que compromisos estan atrasados, que alertas requieren atencion. Toman decisiones de reasignacion y priorizacion.

| Accion clave | Frecuencia |
|-------------|-----------|
| Revisar dashboard divisional | Diaria |
| Delegar compromiso a ENCARGADO | Semanal |
| V.B. acto administrativo | Eventual |
| Escalar problema a ADMIN_REGIONAL | Eventual |

**Motivacion**: Que su division no tenga sorpresas. Control sin micromanagement.
**Frustracion**: Tener que entrar a cada IPR para saber su estado. No poder ver la carga de trabajo de su equipo de un vistazo.

---

### 1.3 Estratega

**Roles**: ADMIN_REGIONAL, GOBERNADOR, ADMIN_SISTEMA

**Pregunta central**: "Como va la institucion?"

**Contexto**: Ven el panorama completo. No entran al detalle de IPRs individuales salvo crisis. Necesitan KPIs agregados, semaforos institucionales, y alertas criticas que requieren su decision. El ADMIN_SISTEMA ademas configura parametros del sistema.

| Accion clave | Frecuencia |
|-------------|-----------|
| Revisar Centro de Comando | Diaria (AR), Semanal (GOB) |
| Firmar acto administrativo | Eventual |
| Aprobar decision estrategica | Semanal |
| Configurar parametros (ADMIN_SISTEMA) | Mensual |

**Motivacion**: Vision institucional clara para tomar decisiones informadas.
**Frustracion**: Informacion fragmentada. Tener que preguntar "como vamos" en vez de verlo.

---

### 1.4 Especialista DGI

**Roles**: ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD

**Pregunta central**: "Que indicadores/procesos necesitan atencion?"

**Contexto**: Trabajan en paralelo a la operativa. No gestionan IPRs directamente — observan, miden, mejoran. Cada especialista tiene un dominio distinto y ritmo de trabajo diferente.

| Sub-perfil | Dominio | Ritmo |
|-----------|---------|-------|
| ESP_CONTROL_GESTION | Indicadores, dashboards, alertas, reportes | Diario (dashboards), Semanal (reportes), Mensual (informe completo) |
| ESP_PROCESOS | BPMN, DMAIC, pain points, oportunidades | Ciclos de 2-4 semanas por proceso |
| ESP_TD | Compliance TDE, Comite TD, Knowledge Base | Semanal (monitoring), Mensual (comite) |

**Motivacion**: Generar valor institucional medible. Demostrar impacto de DGI.
**Frustracion**: Que las divisiones no adopten mejoras propuestas. Datos desactualizados.

---

### 1.5 Coordinador DGI

**Rol**: JEFE_DGI

**Pregunta central**: "Que decisiones/escalamientos hay pendientes?"

**Contexto**: Coordina el equipo DGI (3 especialistas), reporta semanalmente al AR, gestiona escalamientos, y es el puente entre la operativa y la capa de gestion institucional.

| Accion clave | Frecuencia |
|-------------|-----------|
| Standup con equipo DGI | Lunes |
| Reunion coordinacion con AR | Martes |
| Checkpoint iniciativas DMAIC | Miercoles |
| 1-on-1 con jefes de division (rotativo) | Jueves |
| Reporte ejecutivo a AR | Viernes |

**Motivacion**: Que DGI sea visto como util, no como burocracia.
**Frustracion**: Escalamientos sin resolver. Falta de datos para justificar recomendaciones.

---

## 2. Journey Maps

### J1: Ejecutor — "Mi dia de trabajo" (ENCARGADO)

**Trigger**: Inicio de jornada laboral. El ENCARGADO necesita saber que hacer hoy.

```
Login
  |
  v
Centro de Comando (Dashboard)
  |-- AttentionStrip: items urgentes (alertas CRITICO, compromisos vencidos)
  |-- MyProgress module: mis compromisos pendientes
  |
  v
[Click en compromiso urgente]
  |
  v
/ipr/{id}?tab=compromisos  (deep link directo al tab)
  |-- Ver detalle del compromiso
  |-- Actualizar progreso (EN_PROGRESO, notas)
  |-- Si completado: marcar COMPLETADO
  |
  v
[Volver al dashboard]
  |-- Siguiente item pendiente
  |-- Repetir hasta vaciar cola
  |
  v
[Si hay alerta activa]
  |
  v
/ipr/{id}?tab=alertas
  |-- Leer alerta
  |-- Crear problema si amerita
  |-- O resolver directamente
  |
  v
Fin de jornada: cola vacia
```

**Resultado esperado**: El ENCARGADO vacio su inbox de trabajo.
**Metrica de exito**: Tiempo desde login hasta primera accion < 10 segundos.
**Frecuencia**: Diaria.

**UI implications**:
- Dashboard debe mostrar items ordenados por urgencia (ya implementado via priority = SEV*5+TEMP)
- Deep links a tabs especificos (ya implementado via `?tab=compromisos`)
- El compromiso debe poder actualizarse SIN navegar fuera del contexto IPR

---

### J2: Ejecutor — "Formular IPR" (ANALISTA)

**Trigger**: Necesidad de inversion identificada. El ANALISTA inicia formulacion.

```
/ipr/nuevo
  |-- Tipo IPR, nombre, codigo BIP, fuente, mecanismo
  |
  v
[Submit] --> Redirect a /ipr/{id}?tab=partes
  |
  v
Fase F0: Completar satelites
  |-- Tab Partes: agregar POSTULANTE, EJECUTOR, FORMULADOR
  |-- Tab Territorio: asignar comunas + tipo impacto
  |-- Tab Hitos: crear hitos planificados
  |
  v
[Cuando satelites minimos listos]
  |
  v
Avanzar Estado: INGRESADO --> EN_REVISION (F0 --> F1)
  |-- TransitionPanel muestra gates:
  |   - mechanism_required: OK/FALTA
  |   - fril_max_per_comuna: OK/FALTA (si FRIL)
  |
  v
F1: Admisibilidad
  |-- Tab Admisibilidad: verificar items uno a uno
  |-- PRE_ADMISIBLE --> ADMISIBLE (gate: todos items verificados)
  |
  v
F2: Evaluacion Tecnica
  |-- Tab Evaluaciones: asignar evaluador, registrar resultado
  |-- Esperar dictamen externo (MDSF, ANID, etc.)
  |
  v
Resultado evaluacion registrado --> Avanzar a F3
```

**Resultado esperado**: IPR formulada, evaluada, lista para priorizacion.
**Metrica de exito**: Tiempo F0-->F2 < 90 dias (depende de evaluador externo).
**Frecuencia**: ANALISTA maneja ~5-10 IPRs concurrentes.

**UI implications**:
- Post-creacion redirige a tab Partes (ya implementado H1)
- TransitionPanel muestra gates ANTES de seleccionar (ya implementado C39c)
- Tab Admisibilidad debe mostrar claramente items pendientes vs verificados
- Tab Evaluaciones necesita workflow claro: asignar -> esperar -> registrar resultado

---

### J3: Ejecutor — "Revisar rendicion" (RTF)

**Trigger**: Rendicion llega a estado EN_REVISION_RTF. RTF tiene SLA de 7 dias.

```
Login
  |
  v
/datos?tab=rendiciones  (auto-filtro EN_REVISION_RTF para RTF, H12)
  |-- Lista de rendiciones pendientes de revision
  |-- Ordenadas por antiguedad (SLA clock)
  |
  v
[Click en rendicion]
  |-- Ver detalle: montos, documentos, observaciones previas
  |-- Decision: VISAR o OBSERVAR
  |
  v
[Si VISAR]: estado --> VISADA_RTF
  |-- Rendicion pasa a EN_REVISION_UCR (SLA 2 dias)
  |
[Si OBSERVAR]: estado --> OBSERVADA
  |-- Rendicion vuelve al ejecutor (SLA 15 dias para subsanar)
  |
  v
[Volver a lista, siguiente rendicion]
```

**Resultado esperado**: Rendiciones revisadas dentro del SLA de 7 dias.
**Metrica de exito**: 0 rendiciones vencidas (>7d en EN_REVISION_RTF).
**Frecuencia**: Diaria durante periodos de rendicion (post-dia 15 de cada mes).

**UI implications**:
- Auto-filtro por estado ya implementado (H12)
- La lista necesita indicador visual de "dias en estado" (SLA clock)
- Decision VISAR/OBSERVAR debe ser 1-click, no multi-paso

---

### J4: Ejecutor — "V.B. legalidad" (ASESOR_JURIDICO)

**Trigger**: Acto administrativo o convenio llega a estado EN_REVISION (juridica).

```
Login
  |
  v
Centro de Comando
  |-- ModuleJuridico: actos y convenios pendientes de V.B.
  |
  v
[Click en acto pendiente]
  |
  v
/actos/{id}
  |-- Ver documento, firmantes, antecedentes
  |-- Decision: VISAR (avanzar) o DEVOLVER (observaciones)
  |
  v
[Si hay convenio pendiente]
  |
  v
/convenios/{id}
  |-- Ver clausulas, cuotas, contraparte
  |-- V.B. legalidad
  |
  v
[Volver a dashboard, siguiente pendiente]
```

**Resultado esperado**: Actos/convenios con V.B. juridico oportunamente.
**Frecuencia**: Semanal (depende del flujo institucional).

**UI implications**:
- ModuleJuridico ya implementado (H13, C39)
- El widget debe mostrar CONTEO + lista con links directos
- La accion de visar debe estar visible en la vista de detalle sin scroll

---

### J5: Supervisor — "Estado de mi division" (JEFE_DIVISION)

**Trigger**: Inicio de jornada o reunion de equipo.

```
Login
  |
  v
Centro de Comando
  |-- MyTeam module: carga de trabajo por miembro
  |-- AttentionStrip: alertas criticas de MI division
  |
  v
/ipr?division={mi_division}  (auto-filtro H9)
  |-- Lista de IPRs de mi division
  |-- Fase, estado, responsable, deadline
  |-- Ordenadas por riesgo/urgencia
  |
  v
[Click en IPR problematica]
  |
  v
/ipr/{id}
  |-- PhaseStepper: en que fase esta, cuanto lleva
  |-- TransitionPanel: puede avanzar? que falta?
  |-- Tabs: compromisos atrasados, problemas abiertos
  |
  v
[Delegar accion]
  |-- Crear compromiso para ENCARGADO
  |-- O escalar a ADMIN_REGIONAL
  |
  v
/ipr/cartera  (vision divisional agregada, H14)
  |-- Cards por division con semaforo salud
  |-- Distribucion por fase
```

**Resultado esperado**: JEFE sabe el estado de su division sin preguntar.
**Frecuencia**: Diaria (quick check), Semanal (revision profunda).

**UI implications**:
- Auto-filtro por division ya implementado (H9)
- Cartera Divisional ya implementada (H14)
- MyTeam module necesita mostrar carga POR PERSONA (quien tiene mas pendientes)
- La vista de lista IPR necesita indicadores de riesgo inline (ProgressCell, DeadlineCell ya existen)

---

### J6: Supervisor — "Crisis/Alerta" (JEFE_DIVISION)

**Trigger**: Alerta CRITICO o ALTO aparece en AttentionStrip.

```
Centro de Comando
  |-- AttentionStrip: "3 alertas criticas"
  |
  v
[Click en alerta]
  |
  v
/ipr/{id}?tab=alertas
  |-- Detalle de la alerta: tipo, severidad, fecha
  |
  v
[Evaluar situacion]
  |-- Crear problema (Tab Problemas)
  |-- Convocar reunion de crisis
  |-- Escalar a ADMIN_REGIONAL
  |
  v
[Si reunion de crisis]
  |
  v
/reuniones/nueva
  |-- Tipo: Crisis
  |-- Participantes: ENCARGADO + especialistas relevantes
  |-- Acuerdos -> se convierten en compromisos
  |
  v
[Post-reunion]
  |-- Compromisos creados automaticamente
  |-- Seguimiento via dashboard
```

**Resultado esperado**: Crisis contenida, acciones asignadas, seguimiento activo.
**Frecuencia**: Eventual (esperemos que rara).

---

### J7: Estratega — "Panorama institucional" (ADMIN_REGIONAL)

**Trigger**: Reunion con Gobernador, o revision semanal.

```
Login
  |
  v
Centro de Comando
  |-- KPIs institucionales (semaforo 5 dimensiones)
  |-- AttentionStrip: escalamientos pendientes
  |-- Action items: decisiones que requieren mi firma
  |
  v
/centro-de-mando  (Centro de Mando estrategico)
  |-- 6 KPIs: escalamientos, alertas, riesgos, decisiones, reuniones, SLA
  |-- Timeline institucional
  |
  v
[Si hay escalamiento]
  |
  v
/escalamiento/{id}
  |-- Detalle: nivel, problema, opciones, recomendacion DGI
  |-- Decidir: resolver, escalar a Gobernador, devolver
  |
  v
[Firma de actos]
  |
  v
/actos (filtro: pendientes de firma)
  |-- Revisar V.B. previos (juridico, control, jefatura)
  |-- Firmar (FEA)
```

**Resultado esperado**: AR tiene vision completa, toma decisiones informadas.
**Frecuencia**: Diaria (quick scan), Semanal (revision profunda con DGI).

---

### J8: Especialista DGI — "Monitoreo diario" (ESP_CONTROL_GESTION)

**Trigger**: Inicio de jornada. Dashboard de indicadores.

```
Login
  |
  v
Centro de Comando (DgiTeam module NO aplica — es para JEFE_DGI)
  |-- Ver mis action items pendientes
  |
  v
/datos?tab=indicadores
  |-- Indicadores VIGENTES con valores actuales
  |-- Semaforo por dimension (5 dimensiones)
  |-- Filtrar por dimension que necesita atencion
  |
  v
[Si indicador en ROJO]
  |-- Drill-down: ver tendencia, causas
  |-- Crear alerta si amerita
  |-- Documentar en reporte semanal
  |
  v
/datos?tab=rendiciones
  |-- Rendiciones vencidas (SLA breaches)
  |-- Escalations pendientes
  |
  v
/informes
  |-- Editar reporte semanal (6 secciones auto-pobladas)
  |-- Agregar observaciones manuales
  |-- Publicar cuando completo
```

**Resultado esperado**: Indicadores monitoreados, alertas generadas, reporte semanal listo.
**Frecuencia**: Diaria (dashboards), Semanal (reportes).

---

### J9: Especialista DGI — "Mejora de proceso" (ESP_PROCESOS)

**Trigger**: Oportunidad de mejora identificada (bottleneck, pain point, solicitud de division).

```
/procesos
  |-- Catalogo de procesos documentados
  |-- Estado de cada proceso (6-state FSM)
  |
  v
[Crear nuevo proceso o seleccionar existente]
  |
  v
/procesos/{id}
  |-- Hero: nombre, division, estado, criticidad
  |-- FSM stepper: DISENO -> LEVANTAMIENTO -> ANALISIS -> MEJORA -> IMPLEMENTACION -> COMPLETADO
  |-- 5 tabs: Actores, Reglas, Metricas, Pain Points, Oportunidades
  |
  v
[Levantar proceso]
  |-- Tab Actores: registrar roles involucrados
  |-- Tab Reglas: documentar reglas de negocio
  |-- Tab Metricas: baseline (tiempos, volumenes)
  |-- Tab Pain Points: problemas identificados
  |
  v
[Analizar oportunidades]
  |-- Tab Oportunidades: impacto/esfuerzo, priorizar
  |-- Bridge: Oportunidad -> Iniciativa de Mejora
  |
  v
/tablero  (Kanban de iniciativas)
  |-- Crear iniciativa DMAIC desde oportunidad
  |-- Mover por columnas: BACKLOG -> EN_DISENO -> EN_IMPLEMENTACION -> EN_VERIFICACION -> COMPLETADO
  |-- WIP limits: EN_CURSO max 5, REVISION max 2
  |
  v
/tablero/{id}  (Detalle DMAIC)
  |-- 5-phase stepper: DEFINE -> MEASURE -> ANALYZE -> IMPROVE -> VERIFY
  |-- Contenido por fase (formularios contextuales)
  |-- Lean metrics: throughput, lead time, cycle time
```

**Resultado esperado**: Proceso documentado, oportunidades priorizadas, mejora implementada.
**Frecuencia**: Ciclos de 2-4 semanas por proceso.

---

### J10: Coordinador DGI — "Semana de coordinacion" (JEFE_DGI)

**Trigger**: Ritmo semanal fijo.

```
LUNES AM: Standup equipo DGI
  /tablero -- revisar Kanban, redistribuir carga
  /datos?tab=indicadores -- alertas nuevas

MARTES 10:00: Reunion con AR
  /coordinacion -- prep AR decisions
  /escalamiento -- escalamientos abiertos
  /centro-de-mando -- panorama para AR

MIERCOLES AM: Checkpoint DMAIC
  /tablero -- avance iniciativas, WIP check
  /procesos/progreso -- dashboard de procesos

JUEVES PM: 1-on-1 con jefe de division (rotativo)
  /ipr/cartera -- cartera de la division
  /coordinacion/divisiones -- matriz de interaccion

VIERNES AM: Reporte ejecutivo
  /informes -- editar reporte semanal para AR
  /calendario -- proxima semana
```

**Resultado esperado**: Equipo coordinado, AR informado, divisiones alineadas.
**Frecuencia**: Semanal (ritmo fijo).

---

## 3. Matriz Arquetipo-Pagina

Paginas del sistema y su relevancia por arquetipo:

| Pagina | Ejecutor | Supervisor | Estratega | Esp. DGI | Coord. DGI |
|--------|:--------:|:----------:|:---------:|:--------:|:----------:|
| Centro de Comando (dashboard) | ALTA | ALTA | ALTA | MEDIA | ALTA |
| /ipr (lista) | ALTA | ALTA | BAJA | BAJA | MEDIA |
| /ipr/{id} (detalle) | ALTA | ALTA | BAJA | BAJA | BAJA |
| /ipr/cartera | BAJA | ALTA | ALTA | MEDIA | ALTA |
| /ipr/nuevo | ALTA (ANALISTA) | BAJA | BAJA | — | — |
| /compromisos | ALTA | MEDIA | BAJA | — | — |
| /problemas | MEDIA | MEDIA | BAJA | — | — |
| /alertas | MEDIA | ALTA | ALTA | MEDIA | MEDIA |
| /presupuesto | MEDIA (ANALISTA) | MEDIA | ALTA | BAJA | BAJA |
| /convenios | MEDIA | MEDIA | MEDIA | BAJA | BAJA |
| /actos | BAJA | MEDIA | ALTA | — | — |
| /reuniones | MEDIA | MEDIA | MEDIA | — | MEDIA |
| /riesgos | BAJA | MEDIA | ALTA | MEDIA | MEDIA |
| /admin/* | — | — | ALTA (ADMIN_SISTEMA) | — | — |
| /datos (indicadores) | — | — | — | ALTA (CG) | MEDIA |
| /datos (rendiciones) | ALTA (RTF) | — | — | MEDIA (CG) | BAJA |
| /tablero (kanban) | — | — | — | ALTA (PROC) | ALTA |
| /procesos | — | — | — | ALTA (PROC) | MEDIA |
| /cuellos-de-botella | — | — | — | ALTA (CG) | MEDIA |
| /servicios | — | — | — | MEDIA | MEDIA |
| /coordinacion | — | — | — | BAJA | ALTA |
| /escalamiento | — | — | MEDIA | — | ALTA |
| /centro-de-mando | — | — | ALTA | — | ALTA |
| /calendario | — | — | — | MEDIA | ALTA |
| /comite-td | — | — | — | ALTA (TD) | MEDIA |
| /informes | — | — | — | ALTA (CG) | ALTA |

---

## 4. Principios UX derivados de los Journeys

### P1: Inbox-First, Not Browse-First

El Ejecutor (80% del uso) NO navega — ejecuta tareas de una cola. El dashboard debe ser un **inbox de trabajo**, no un panorama.

**Implicacion**: Centro de Comando + AttentionStrip + deep links es correcto. Los items de accion deben tener 1-click para llegar al punto de accion.

### P2: Nivel de Agregacion = Rol

Cada rol necesita un nivel de agregacion distinto:
- Ejecutor: MIS items (1 persona)
- Supervisor: MI DIVISION (8-15 personas)
- Estratega: TODA LA INSTITUCION (6 divisiones)
- DGI: TRANSVERSAL (observa sin controlar)

**Implicacion**: Las vistas de lista deben pre-filtrarse por el scope del rol. No mostrar "toda la institucion" a un ENCARGADO.

### P3: La Transicion es el Momento de Verdad

El momento critico en el IPR es la **transicion de fase**. Ahi es donde el usuario necesita saber:
1. Puedo avanzar? (gates)
2. Que pasa si avanzo? (effects)
3. Que me falta? (blocking gates con detalle)

**Implicacion**: TransitionPanel es el componente mas importante del detalle IPR. Debe ser claro, prominente, y autosuficiente.

### P4: El Supervisor No Ejecuta — Delega

JEFE_DIVISION no actualiza compromisos. Crea compromisos para que ENCARGADO los ejecute. Necesita ver ESTADO AGREGADO, no detalle granular.

**Implicacion**: La vista de lista con ProgressCell/DeadlineCell es mas util para el Supervisor que el detalle de cada item.

### P5: DGI Observa, No Controla

DGI no tiene FK directos a IPRs. Observa via metricas, indicadores y reportes. Sus acciones son: medir, analizar, recomendar, escalar.

**Implicacion**: Los cockpits DGI deben ser dashboards de lectura + herramientas de analisis, no formularios de CRUD.

### P6: Frecuencia Determina Prominencia

| Frecuencia | Prominencia UI |
|-----------|---------------|
| Diaria | Primer nivel (dashboard, sidebar, 1 click) |
| Semanal | Segundo nivel (pagina dedicada, 2 clicks) |
| Mensual | Tercer nivel (seccion dentro de pagina, 3 clicks) |
| Eventual | Accesible pero no prominente |

### P7: El Error Mas Comun No Es Tecnico — Es De Contexto

El usuario no se equivoca en que boton presionar. Se equivoca en **que deberia estar haciendo ahora**. El sistema debe responder "que hago?" antes de "como lo hago?".

**Implicacion**: Priorizar orientacion contextual (que hacer) sobre funcionalidad (como hacerlo).

---

## 5. Gaps UX Identificados

Journeys que el sistema actual NO resuelve bien:

| Gap | Journey | Problema | Impacto |
|-----|---------|----------|---------|
| G1 | J1 (Ejecutor inbox) | MyProgress muestra items pero sin SLA clock ni deadline visual | Alto — ENCARGADO no sabe que vence primero |
| G2 | J2 (Formular IPR) | No hay guia de "que satelites necesito para MI track" | Medio — ANALISTA completa satelites por prueba y error |
| G3 | J3 (RTF rendicion) | Lista de rendiciones no muestra dias-en-estado | Alto — RTF no ve cuales estan por vencer su SLA |
| G4 | J5 (Division oversight) | MyTeam no muestra carga POR PERSONA | Alto — JEFE no sabe quien esta sobrecargado |
| G5 | J6 (Crisis) | No hay workflow guiado alerta -> problema -> reunion -> compromiso | Medio — Flujo manual con saltos entre paginas |
| G6 | J7 (Panorama) | Centro de Mando tiene KPIs pero no drill-down a divisiones | Medio — AR tiene que navegar aparte a /ipr/cartera |
| G7 | J8 (CG monitoreo) | No hay vista de "indicadores que empeoraron esta semana" | Medio — CG revisa uno por uno sin prioridad |
| G8 | J1-J4 | Ningun journey tiene "done state" claro | Alto — Usuario no sabe cuando termino su trabajo del dia |

---

## 6. User Stories Operativas Priorizadas (P0, por Arquetipo)

### Ejecutor P0

| ID | Como... | Quiero... | Para... |
|----|---------|-----------|---------|
| US-EJEC-EO-002 | ENCARGADO | Registrar avance parcial de compromiso | Documentar progreso incremental |
| US-EJEC-EO-003 | ENCARGADO | Solicitar validacion de compromiso completado | Que mi JEFE lo verifique |
| US-EJEC-EO-007 | ENCARGADO | Recibir alertas de compromisos por vencer | No dejar pasar deadlines |
| US-ANAL-INV-001-01 | ANALISTA | Formulario de evaluacion con campos validados | Formular IPR sin errores |
| US-ANALPRES-001-01 | ANALISTA | Emitir CDP con validacion automatica de saldo | Evitar sobrecomprometer presupuesto |

### Supervisor P0

| ID | Como... | Quiero... | Para... |
|----|---------|-----------|---------|
| US-EJEC-JD-002 | JEFE_DIVISION | Delegar compromisos a mi equipo | Distribuir trabajo equitativamente |
| US-EJEC-JD-005 | JEFE_DIVISION | Filtrar y monitorear compromisos de mi division | Saber que esta atrasado |
| US-EJEC-JD-006 | JEFE_DIVISION | Validar cierre de compromisos | Verificar calidad del trabajo |
| US-EJEC-AR-009 | JEFE_DIVISION | Monitorear obstaculos y escalar externamente | Desbloquear IPRs estancadas |
| US-GEST-PB-001 | JEFE_DIVISION | Playbook de recuperacion cuando salud < 60 | Saber que hacer en crisis |

### Estratega P0

| ID | Como... | Quiero... | Para... |
|----|---------|-----------|---------|
| US-CORE-002-01 | ADMIN_REGIONAL | Ver estado de ejecucion de IPRs aprobadas por CORE | Reportar al Gobernador |
| US-GOB-001-02 | ADMIN_REGIONAL | Auto-alertas en desviaciones criticas | No enterarme tarde |
| US-GEST-SCG-001 | ADMIN_REGIONAL | Plan operativo anual por division | Alinear metas institucionales |

---

## Historial

| Version | Fecha | Cambios |
|---------|-------|---------|
| v1.0 | 2026-03-14 | Creacion inicial: 5 arquetipos, 10 journeys, matriz, principios, gaps |
