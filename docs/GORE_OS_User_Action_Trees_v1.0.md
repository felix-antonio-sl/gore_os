# GORE_OS — Arboles de Acciones por Usuario v1.0

**Fecha**: 2026-03-23 | **Sesion**: C61
**Fuentes**: sidebar.tsx (ROLE_SECTIONS), 60 page.tsx, 29 routers (304 endpoints), security.py, scope.py, types/index.ts
**Cobertura**: 24 usuarios de prueba, 15 roles, 38 rutas navegables, 304 endpoints API

---

## Convenciones

```
📍  Pagina/Vista navegable (ruta en browser)
  🔍  Accion de lectura: consultar, filtrar, buscar, drill-down, exportar
  ✏️  Accion de escritura: crear, editar, transicionar estado, aprobar
  🗑️  Accion destructiva: eliminar, anular, soft-delete
  ⚡  Accion automatica: sistema ejecuta sin intervencion del usuario
  🔒  Accion bloqueada para este rol
  [D]  Drawer: formulario lateral inline (no pagina separada)
  [T]  Tab dentro de una pagina (Radix Tabs, sincronizado con ?tab=URL)
  →   Navegacion a otra vista
  ↳   Sub-accion dentro de un contexto padre
```

**Scoping IDOR** (3 niveles):
- `GLOBAL`: Sin restriccion. Ve todo el sistema.
- `DIVISION`: Solo entidades donde `sponsor_division_id` = division del usuario.
- `PERSONAL`: Solo entidades donde `assignee_id` o `formulator_id` = usuario actual.

**Poblaciones**:
- `Operativa`: 11 roles — gestion IPR, presupuesto, convenios, actos, governance.
- `DGI`: 4 roles — monitoreo, mejora continua, coordinacion, analisis.

---

## Tabla de Usuarios

| # | Email | Rol | Poblacion | Division | Scope |
|---|-------|-----|-----------|----------|-------|
| 1 | admin@goreos.cl | ADMIN_SISTEMA | Operativa | — | GLOBAL |
| 2 | regional@goreos.cl | ADMIN_REGIONAL | Operativa | — | GLOBAL |
| 3 | gobernador@goreos.cl | GOBERNADOR | Operativa | — | GLOBAL |
| 4 | consejero1@goreos.cl | CONSEJERO_REGIONAL | Operativa | — | GLOBAL |
| 5 | consejero2@goreos.cl | CONSEJERO_REGIONAL | Operativa | — | GLOBAL |
| 6 | secretario.core@goreos.cl | SECRETARIO_EJECUTIVO | Operativa | — | GLOBAL |
| 7 | jefe.daf@goreos.cl | JEFE_DIVISION | Operativa | DAF | DIVISION |
| 8 | jefe.dideso@goreos.cl | JEFE_DIVISION | Operativa | DIDESO | DIVISION |
| 9 | jefe.difoi@goreos.cl | JEFE_DIVISION | Operativa | DIFOI | DIVISION |
| 10 | jefe.dipir@goreos.cl | JEFE_DIVISION | Operativa | DIPIR | DIVISION |
| 11 | jefe.diplade@goreos.cl | JEFE_DIVISION | Operativa | DIPLADE | DIVISION |
| 12 | jefe.dit@goreos.cl | JEFE_DIVISION | Operativa | DIT | DIVISION |
| 13 | jefe.finanzas@goreos.cl | JEFE_DEPARTAMENTO | Operativa | DAF | DIVISION |
| 14 | jefe.ucr@goreos.cl | JEFE_UNIDAD | Operativa | DAF | DIVISION |
| 15 | analista.dipir@goreos.cl | ANALISTA | Operativa | DIPIR | PERSONAL |
| 16 | analista.diplade@goreos.cl | ANALISTA | Operativa | DIPLADE | PERSONAL |
| 17 | profesional.dit@goreos.cl | ANALISTA | Operativa | DIT | PERSONAL |
| 18 | profesional.dideso@goreos.cl | ANALISTA | Operativa | DIDESO | PERSONAL |
| 19 | rtf.daf@goreos.cl | RTF | Operativa | DAF | PERSONAL |
| 20 | juridico@goreos.cl | ASESOR_JURIDICO | Operativa | — | PERSONAL |
| 21 | jefe.dgi@goreos.cl | JEFE_DGI | DGI | DGI | GLOBAL |
| 22 | control.gestion@goreos.cl | ESP_CONTROL_GESTION | DGI | DGI | GLOBAL |
| 23 | procesos@goreos.cl | ESP_PROCESOS | DGI | DGI | GLOBAL |
| 24 | td@goreos.cl | ESP_TD | DGI | DGI | GLOBAL |

Contrasena universal: `admin123`

---

# POBLACION OPERATIVA

---

## 1. ADMIN_SISTEMA — admin@goreos.cl

**Scope**: GLOBAL | **Division**: Ninguna (transversal) | **Sidebar sections**: Comando, Gestion IPR, Finanzas, Institucional, Admin

Este es el unico rol con acceso al modulo `/admin`. Tiene visibilidad y escritura total sobre todas las entidades del sistema sin restriccion de division.

### Flujo de Acceso

```
/login
  ✏️ Ingresar email (admin@goreos.cl) + contrasena (admin123)
  ⚡ Backend: POST /api/auth/login → JWT (iss=goreos-api, aud=goreos-web, exp=8h)
  ⚡ Frontend: localStorage.goreos_token = JWT, localStorage.goreos_user = {user}
  ⚡ Deteccion poblacion=operativa, role=ADMIN_SISTEMA → redirect /dashboard
```

### Dashboard

```
📍 /dashboard
  ⚡ Routing automatico → CommandCenter (Centro de Comando unificado)
  🔍 Saludo contextual: "Buenos dias, Administrador"
  🔍 AttentionStrip: items urgentes priorizados (prioridad = SEV*5 + TEMP)
    ↳ Fuentes: compromisos vencidos, alertas criticas, decisiones AR, escalamientos, SLA incumplidos, riesgos abiertos
    ↳ Click item → navega a entidad origen (IPR, compromiso, alerta, etc.)
  🔍 KPI Strip: 4 tarjetas semaforo
    ↳ Compromisos vencidos (rojo si >10)
    ↳ Alertas criticas activas
    ↳ IPRs sin actividad >7d
    ↳ SLA incumplidos
  🔍 ModuleMyTeam: vista equipo global (todas las divisiones)
    ↳ Avatares por division
    ↳ Drill-down: click division → /compromisos?division=X
    ↳ Progreso compromisos por miembro
```

### Comando

```
📍 /centro-de-mando
  🔍 6 KPIs paralelos (queries concurrentes):
    ↳ Escalamientos activos: count + drill-down → /escalamiento
    ↳ Alertas criticas: count CRITICO + ALTO → /alertas?severity=CRITICO
    ↳ Riesgos abiertos: count IDENTIFICADO+EN_EVALUACION+EN_MITIGACION → /riesgos
    ↳ Decisiones pendientes: count PENDIENTE → /coordinacion
    ↳ Reuniones proximas: count <=7d → /reuniones
    ↳ SLA incumplidos: count breaches → /admin?tab=monitoreo
  🔍 Timeline unificada (UNION ALL 5 fuentes, ordenada cronologicamente)
    ↳ Cada evento: icono tipo, severidad semaforo, titulo, timestamp
    ↳ Click → navega a entidad

📍 /riesgos
  🔍 FilterBar:
    ↳ Tabs estado: TODOS | IDENTIFICADO | EN_EVALUACION | EN_MITIGACION | MITIGADO | ACEPTADO | CERRADO
    ↳ Busqueda texto libre (debounce 300ms)
  🔍 DataTable 7 columnas:
    ↳ Codigo (RSK-NNNN, advisory-locked), Nombre, Tipo, Probabilidad, Impacto, Estado, Mitigacion
  🔍 Toggle vista → Matriz de riesgo 3x3 (Probabilidad x Impacto con colores)
  ✏️ Crear riesgo [D]:
    ↳ Campos: nombre, tipo, probabilidad (BAJA/MEDIA/ALTA/MUY_ALTA), impacto (BAJO/MEDIO/ALTO/MUY_ALTO)
    ↳ IPR vinculado (ComboboxAsync, busqueda servidor)
    ↳ Plan mitigacion (textarea)
    ↳ POST /api/risk → auto-genera RSK-NNNN (advisory-locked)
    ⚡ Si probabilidad ALTA o MUY_ALTA → auto-crea alerta en core.alert
  ✏️ Transicionar estado (FSM 6-state):
    ↳ IDENTIFICADO → EN_EVALUACION | ACEPTADO
    ↳ EN_EVALUACION → EN_MITIGACION | ACEPTADO | CERRADO
    ↳ EN_MITIGACION → MITIGADO | CERRADO
    ↳ MITIGADO → CERRADO
    ↳ ACEPTADO → CERRADO
    ↳ CERRADO → (terminal)
  ✏️ Editar mitigacion, responsable
  🗑️ Eliminar riesgo (soft-delete, ConfirmDialog)
  🔍 CSV export

📍 /riesgos/{id}
  🔍 Detalle completo: record, posicion matriz, historial mitigacion, IPRs vinculados
  ✏️ Editar campos
  ✏️ Transicionar estado (mismos paths que lista)
  🔍 Timeline de cambios
```

### Gestion IPR

```
📍 /ipr
  🔍 FilterBar:
    ↳ Busqueda texto (debounce 300ms, busca en codigo_bip + nombre)
    ↳ Filtro estado: 32 opciones agrupadas por fase ("F0 · INGRESADO", "F1 · EN_REVISION", etc.)
    ↳ Filtro division: Select (9 divisiones)
    ↳ Filtro fase: F0|F1|F2|F3|F4|F5
    ↳ "Mas filtros" toggle → Sector, Mecanismo, Alerta (nivel)
  🔍 DataTable 8 columnas:
    ↳ BIP (codigo unico), Nombre, Tipo (8: INFRAESTRUCTURA, EQUIPAMIENTO, etc.)
    ↳ Estado (StatusBadge 32 colores por fase), Sector, Actor (rol + accion)
    ↳ Dias (semaforo: verde ≤30d, ambar ≤90d, rojo >90d desde phase_entered_at)
    ↳ Ejecucion % (ProgressCell verde/ambar/rojo)
  🔍 Paginacion: page + page_size, total_pages
  ✏️ Boton "Nuevo IPR" → /ipr/nuevo
  🔍 Click fila → /ipr/{id}
  🔍 CSV export (descarga todos los registros filtrados)

📍 /ipr/nuevo
  ✏️ Formulario creacion IPR (F0 INGRESADO):
    ↳ Tipo inversion: Select (8 opciones: INFRAESTRUCTURA, EQUIPAMIENTO, CONSERVACION, TRANSFERENCIA, SUBSIDIO, ESTUDIO, PROGRAMA_SOCIAL, PROGRAMA_8PCT)
    ↳ Division patrocinadora: Select (9 divisiones)
    ↳ Nombre proyecto: Input texto
    ↳ Sector inversion: Select (ref.category scheme=investment_sector)
    ↳ Mecanismo financiamiento: Select (ref.category scheme=mechanism)
    ↳ Formulador: ComboboxAsync (busqueda personas)
    ↳ Asesor juridico: ComboboxAsync (opcional)
  ✏️ POST /api/ipr → crea IPR en estado INGRESADO (F0)
  ⚡ Redirect → /ipr/{id}?tab=partes (para completar formulacion)
  ⚡ record_event: IPR_CREATED

📍 /ipr/{id} — Detalle IPR (18 tabs en 4 grupos)
  🔍 IprHeroCard:
    ↳ Codigo BIP, nombre, tipo inversion, division patrocinadora
    ↳ Fase actual (badge F0-F5), estado actual (StatusBadge 32 estados)
    ↳ Track de financiamiento (si asignado)
    ↳ Actor actual: rol + accion sugerida ("Analista DIPIR — Completar formulacion")
  🔍 IprPhaseStepper:
    ↳ 6 fases F0→F5 como steps visuales
    ↳ Fase activa resaltada
    ↳ Dias transcurridos por fase (semaforo verde/ambar/rojo)
  🔍 TrackCard (si track asignado):
    ↳ Requisitos del track: umbrales UTM, reglas glosa, certificaciones
    ↳ Labels humanizados ("Dictamen requerido", "Requisitos", etc.)
    ↳ Gates con indicador semaforo (gates evaluados desde /readiness)
  ✏️ IprTransitionPanel:
    ↳ Estados destino permitidos (desde STATUS_PHASE_FIBER + valid_transitions)
    ↳ Evaluacion de gates en tiempo real (GET /api/ipr/{id}/readiness):
      ↳ Gates totales vs gates cumplidos
      ↳ Lista de gates bloqueantes (rojo) y cumplidos (verde)
    ↳ Feedforward effects: que pasa si avanzo (ej: "Al pasar a CDP_EMITIDO se bloquea edicion de partes")
    ↳ Boton "Avanzar a [estado]" → ConfirmDialog → PATCH /api/ipr/{id} {status_id: nuevo}
    ⚡ DB trigger valida transicion (valid_transitions JSONB)
    ⚡ record_event: IPR_STATUS_CHANGED
    ⚡ Auto-notificacion: create_notification al responsable
  🔍 IprHistorySection:
    ↳ Timeline de transiciones desde txn.event (GET /api/ipr/{id}/historial)
    ↳ Cada evento: fecha, estado anterior → nuevo, actor, duracion en fase

  [T] Grupo "Operacion"

    📍 tab-resumen [T]
      🔍 Resumen ejecutivo del IPR
      🔍 Actor actual card (rol, division abreviada, accion sugerida)
      🔍 ReadinessCard:
        ↳ Conteos satelites inline: Compromisos(N), Problemas(N), Alertas(N), Convenios(N), CDPs(N), Avances(N), Partes(N), Territorio(N), Hitos(N/M)
        ↳ Gate evaluation desde /readiness (gates_passed/gates_total)

    📍 tab-compromisos [T]
      🔍 Lista compromisos vinculados al IPR
        ↳ Columnas: tipo, responsable, estado, vencimiento, dias
        ↳ DeadlineCell: rojo vencido, ambar ≤7d, verde futuro
      ✏️ Crear compromiso [D]:
        ↳ Tipo compromiso: Select (ref.category scheme=operational_commitment_type)
        ↳ Responsable: ComboboxAsync (personas)
        ↳ Fecha vencimiento: DatePicker
        ↳ Descripcion: Textarea
        ↳ POST /api/compromisos → estado inicial PENDIENTE
        ⚡ record_event: COMPROMISO_CREATED
        ⚡ create_notification al responsable
      ✏️ Completar compromiso:
        ↳ Boton "Completar" → POST /api/compromisos/{id}/complete
        ↳ Transicion: PENDIENTE → COMPLETADO (o EN_PROGRESO → COMPLETADO)
        ⚡ record_event: COMPROMISO_COMPLETED
        ⚡ create_notification al jefe de division
      ✏️ Verificar compromiso:
        ↳ Boton "Verificar" (solo JEFE_DIVISION+ visible)
        ↳ POST /api/compromisos/{id}/verify
        ↳ Transicion: COMPLETADO → VERIFICADO
        ⚡ record_event: COMPROMISO_VERIFIED
        ⚡ create_notification al responsable
      🗑️ Eliminar compromiso (soft-delete, ConfirmDialog)
      🔍 Click codigo_bip → navega a IPR padre

    📍 tab-problemas [T]
      🔍 Lista problemas del IPR
        ↳ Columnas: tipo, impacto, estado, detectado, responsable
      ✏️ Crear problema [D]:
        ↳ Tipo: Select (TECNICO, FINANCIERO, LEGAL, AMBIENTAL, SOCIAL, INSTITUCIONAL, OTRO)
        ↳ Impacto: Select (BAJO, MEDIO, ALTO, CRITICO)
        ↳ Descripcion: Textarea
        ↳ Responsable resolucion: ComboboxAsync
        ↳ POST /api/problemas → estado inicial ABIERTO
        ⚡ record_event
      ✏️ Transicionar estado:
        ↳ ABIERTO → EN_GESTION (asignar responsable)
        ↳ EN_GESTION → RESUELTO | CERRADO_SIN_RESOLVER
        ↳ RESUELTO → (terminal)
        ↳ CERRADO_SIN_RESOLVER → (terminal)
      🗑️ Eliminar problema (soft-delete)

    📍 tab-alertas [T]
      🔍 Lista alertas vinculadas al IPR (solo lectura)
        ↳ Severidad badge: CRITICO (rojo), ALTO (naranja), ATENCION (ambar), INFO (gris)
        ↳ Mensaje, subject_type (core.ipr, core.operational_commitment, etc.)
        ↳ Timestamp, estado (activa/resuelta)
      🔍 Click subject → navega a entidad origen

    📍 tab-convenios [T]
      🔍 Convenios vinculados al IPR
        ↳ Columnas: numero, tipo, contraparte, estado, monto (formatCLP), vigencia
      ✏️ Vincular convenio existente [D]
      🔍 Click convenio → drawer detalle con cuotas y rendiciones

  [T] Grupo "Finanzas"

    📍 tab-rendiciones [T]
      🔍 Rendiciones SISREC del IPR
        ↳ Columnas: ID (8 chars), convenio, estado (8 fases), fase, SLA clock
        ↳ SLA display: dias en fase actual vs SLA permitido
      🔍 Filtro por estado rendicion
      🔍 Click rendicion → drawer detalle

    📍 tab-cdps [T]
      🔍 CDPs presupuestarios del IPR
        ↳ Columnas: codigo CDP-YYYY-NNNN, monto, estado, fecha
      ✏️ Crear CDP [D]:
        ↳ Monto: Input numerico (validacion: monto ≤ vigente - comprometido)
        ↳ POST /api/presupuesto/cdps → auto-genera CDP-YYYY-NNNN (advisory-locked)
        ⚡ record_event: CDP_CREATED
      🗑️ Eliminar CDP (ConfirmDialog)

    📍 tab-avances [T]
      🔍 Reportes de progreso del IPR (cronologico)
        ↳ Columnas: N° reporte (auto-incremented), periodo, % fisico, % financiero, fecha
      ✏️ Crear avance [D]:
        ↳ Periodo: Input texto
        ↳ Avance fisico %: Input numerico
        ↳ Avance financiero %: Input numerico
        ↳ Observaciones: Textarea
        ↳ POST /api/ipr/{id}/avances → auto-numera report_number
        ⚡ record_event

    📍 tab-presupuesto [T]
      🔍 Vista ejecucion presupuestaria del IPR
        ↳ Cadena: inicial → vigente → comprometido → devengado → pagado
        ↳ ProgressCell por nivel de ejecucion

  [T] Grupo "Requisitos"

    📍 tab-partes [T]
      🔍 Partes interesadas del IPR (9 roles posibles)
        ↳ Columnas: organizacion, rol (BENEFICIARIO, EJECUTOR, SUPERVISOR, FINANCIADOR, ITO, etc.), contacto
      ✏️ Agregar parte [D]:
        ↳ Organizacion: ComboboxAsync (3,375 organizaciones, busqueda servidor)
        ↳ Rol: Select (ref.category scheme=ipr_party_role, 9 opciones)
        ↳ Contacto: Input texto
        ↳ Convenio vinculado: ComboboxAsync (opcional)
        ↳ POST /api/ipr/{id}/partes
        ↳ UNIQUE constraint: uq_ipr_party_role (org + rol por IPR)
      🗑️ Eliminar parte (ConfirmDialog)
      🔍 ITO card: indicador verde (ITO asignado) o ambar ("Sin ITO asignado" + boton agregar)

    📍 tab-territorio [T]
      🔍 Territorio impactado por el IPR
        ↳ Columnas: comuna/departamento, tipo impacto
      ✏️ Agregar territorio [D]:
        ↳ Comuna: Select (25 territorios, sin busqueda)
        ↳ Tipo impacto: Select (DIRECTO, INDIRECTO, COBERTURA, INFLUENCIA)
        ↳ POST /api/ipr/{id}/territorio
        ↳ UNIQUE constraint: uq_ipr_territory_impact
      🗑️ Eliminar territorio

    📍 tab-hitos [T]
      🔍 Hitos del proyecto (13 tipos posibles)
        ↳ Columnas: tipo, fecha planificada, fecha real, desviacion (dias, GENERATED)
      ✏️ Crear hito [D]:
        ↳ Tipo: Select (13 tipos: diseno, licitacion, adjudicacion, contrato, inicio_obra, termino_obra, recepcion_provisoria, recepcion_definitiva, liquidacion, rendicion, cierre, etc.)
        ↳ Fecha planificada: DatePicker
        ↳ POST /api/ipr/{id}/hitos
      ✏️ Registrar fecha real:
        ↳ DatePicker → PATCH
        ↳ ⚡ Auto-calculo deviation_days = actual_date - planned_date (column GENERATED)

    📍 tab-evaluaciones [T]
      🔍 Evaluaciones asignadas al IPR
        ↳ Columnas: tipo evaluador, resultado, puntaje, fecha
      ✏️ Registrar resultado evaluacion:
        ↳ Resultado: Select (RS=Rec.Satisfactoria, FI=Favorablemente Informado, FC=Fav.Condicionado, OT=Objetado Tecnicamente, AD=Admisible, RF=Rec.Favorable, ITF=Inf.Tec.Favorable, AT=Aprobado Tec.)
        ↳ Puntaje: Input numerico NUMERIC(5,2)
        ↳ PATCH /api/ipr/{id}/evaluaciones/{eval_id}
        ⚡ Labels humanizados via _EVAL_LABELS (nunca codigos raw en UI)

  [T] Grupo "Ciclo"

    📍 tab-resoluciones [T]
      🔍 Actos administrativos vinculados al IPR (solo lectura)
        ↳ Via ipr_party + agreements → resolutions
        ↳ Click resolucion → /actos/{id}

    📍 tab-parentesco [T]
      🔍 Arbol IPR padre/hijo
      ✏️ Crear relacion parentesco:
        ↳ IPR hijo: ComboboxAsync
        ↳ Tipo relacion: Select
        ↳ POST /api/ipr/{id}/parentesco

    📍 tab-admisibilidad [T]
      🔍 Checks de admisibilidad (mecanismo-especificos)
        ↳ Lista checks: verificado (si/no), descripcion, tipo
      ✏️ Marcar check como verificado:
        ↳ PATCH /api/ipr/{id}/admisibilidad/{check_id} → verified=true
        ↳ Gate F1→F2: TODOS los checks deben estar verificados
      🔍 Kinship gate: para SUBV8 en F1→F2 (declaracion parentesco requerida)

    📍 tab-modificaciones [T]
      🔍 Modificaciones al IPR (MOD-YYYY-NNNN)
        ↳ Columnas: codigo, tipo, estado, fecha, solicitante
        ↳ Mini-stepper FSM: SOLICITADA→EN_REVISION→APROBADA|RECHAZADA
      ✏️ Crear modificacion [D]:
        ↳ Tipo: Select
        ↳ Justificacion: Textarea
        ↳ POST → auto-genera MOD-YYYY-NNNN
      ✏️ Aprobar/Rechazar:
        ↳ PATCH → EN_REVISION→APROBADA o EN_REVISION→RECHAZADA

    📍 tab-cierre [T]
      🔍 Acta de cierre del IPR (UNIQUE — max 1 por IPR)
      ✏️ Crear acta de cierre:
        ↳ Observaciones: Textarea
        ↳ POST /api/ipr/{id}/cierre
      ✏️ Firmar cierre:
        ↳ Gate: solo si IPR en F5 (EN_RENDICION o posterior)
        ↳ PATCH → signed=true

    📍 tab-evaluacion-expost [T]
      🔍 Evaluacion ex-post (solo para IPR en estado CERRADO)
      ✏️ Registrar evaluacion 4 dimensiones:
        ↳ Pertinencia: score 1-5
        ↳ Eficiencia: score 1-5
        ↳ Eficacia: score 1-5
        ↳ Sostenibilidad: score 1-5
        ↳ Wizard 4 pasos con contextual prompts
```

### Cartera y Portfolios

```
📍 /ipr/cartera
  🔍 Health signals por division:
    ↳ ROJO: alertas criticas o >30% compromisos vencidos
    ↳ AMARILLO: >5 problemas abiertos
    ↳ VERDE: sin senales de riesgo
  🔍 DataTable por division: nombre, IPRs activos, health, alerts, problems
  🔍 Drill-down: click division → lista IPRs filtrada
  🔍 CSV export
```

### Compromisos

```
📍 /compromisos
  🔍 CompromisosListView (vista global para ADMIN_SISTEMA):
    ↳ FilterBar: busqueda, IPR (ComboboxAsync), responsable, estado, division
    ↳ DataTable 7 cols: BIP, nombre, responsable, estado, vencimiento, dias, actor
    ↳ DeadlineCell: rojo vencido, ambar ≤7d, verde futuro
  ✏️ Crear compromiso [D] (mismos campos que tab-compromisos)
  ✏️ Completar inline (boton por fila)
  ✏️ Verificar inline (boton por fila)
  🗑️ Eliminar (ConfirmDialog)
  🔍 CSV export
```

### Problemas

```
📍 /problemas
  🔍 FilterBar: busqueda, IPR, tipo (7), impacto (4), estado (4)
  🔍 DataTable 6 cols: codigo, IPR (click → /ipr/{id}), tipo, impacto, estado, detectado
  ✏️ Crear problema [D] (mismos campos que tab-problemas)
  ✏️ Transicionar estado inline
  🗑️ Eliminar (ConfirmDialog)
  🔍 CSV export
```

### Alertas

```
📍 /alertas
  🔍 Filtro severidad: CRITICO | ALTO | ATENCION | INFO
  🔍 Filtro tipo alerta: ref.category scheme=alert_type (13 codigos)
  🔍 Filtro rango fechas
  🔍 AlertCard UI por alerta:
    ↳ Severidad badge (color), mensaje, subject link
    ↳ Timestamp, estado (activa/resuelta)
    ↳ Click subject → navega a entidad (IPR, compromiso, rendicion, etc.)
  🔍 CSV export
```

### Presupuesto

```
📍 /presupuesto
  🔍 FilterBar: division, subtitulo (21/22/24/29/31/33), ano fiscal
  🔍 DataTable 10 cols:
    ↳ Division, programa, tipo, DIPRES code, item
    ↳ Asignacion, Ppto.Inicial, Ppto.Vigente, Comprometido
    ↳ % Ejecucion (ProgressCell: verde ≥70%, ambar ≥40%, rojo <40%)
  ✏️ Crear programa [D]:
    ↳ Division: Select (9)
    ↳ Subtitulo: Select (presupuestario)
    ↳ Item: Input
    ↳ Monto inicial: Input numerico
    ↳ Ano fiscal: Select
    ↳ POST /api/presupuesto
    ⚡ record_event: BUDGET_CREATED
  🔍 Click fila → drawer detalle con cadena ejecucion
  ✏️ Editar programa: PATCH /api/presupuesto/{id}
  🔍 CSV export

📍 /presupuesto/ciclo
  🔍 Ciclos fiscales por ano
  ✏️ Inicializar ciclo:
    ↳ POST /api/presupuesto/ciclo/{year}/initialize
    ↳ Advisory-locked (pg_advisory_xact_lock)
    ⚡ record_event: BUDGET_CYCLE_INITIALIZED
  🔍 Hitos del ciclo (17 budget_cycle_milestone entries)
```

### Convenios

```
📍 /convenios
  🔍 FilterBar: busqueda, estado (14 opciones), tipo, contraparte, vencimiento (≤30/60/90d)
  🔍 KPI strip: total convenios, vigentes, vencidos, cuotas pendientes, monto total
  🔍 Seccion "Proximos a vencer": convenios VIGENTE con ≤90d a vencimiento
  🔍 DataTable 7 cols:
    ↳ Numero, tipo, estado (StatusBadge 14 estados), contraparte
    ↳ Monto (formatCLP), vigencia hasta (DeadlineCell semaforo), cuotas (count)
  ✏️ Crear convenio [D]:
    ↳ Tipo: Select
    ↳ Contraparte: ComboboxAsync (organizaciones)
    ↳ Monto total: Input numerico
    ↳ Periodo vigencia: DatePicker from/to
    ↳ IPR vinculado: ComboboxAsync (opcional)
    ↳ POST /api/convenios
    ⚡ record_event: AGREEMENT_CREATED
  ✏️ Transicionar estado (FSM 14-state):
    ↳ BORRADOR → EN_NEGOCIACION | CANCELADO
    ↳ EN_NEGOCIACION → EN_REVISION_JURIDICA | BORRADOR
    ↳ EN_REVISION_JURIDICA → FIRMADO_GORE | EN_NEGOCIACION
    ↳ FIRMADO_GORE → FIRMADO_CONTRAPARTE
    ↳ FIRMADO_CONTRAPARTE → VIGENTE | TDR_PENDIENTE
    ↳ TDR_PENDIENTE → FORMALIZADO
    ↳ FORMALIZADO → VIGENTE
    ↳ VIGENTE → EN_MODIFICACION | VENCIDO | TERMINADO | RESCILIADO
    ↳ EN_MODIFICACION → VIGENTE
    ↳ VENCIDO, TERMINADO, RESCILIADO, CANCELADO → (terminal)
  ✏️ Agregar cuota [D]:
    ↳ Numero cuota: Input
    ↳ Monto: Input numerico
    ↳ Fecha vencimiento: DatePicker
    ↳ Estado pago: Select (PENDIENTE)
    ↳ POST /api/convenios/{id}/cuotas
  ✏️ Cuotas bulk: POST /api/cuotas/bulk (multiples cuotas en una operacion)
  ✏️ Marcar cuota PAGADA: PATCH payment_status_id
  🔍 Filtro huerfano: ?orphan=true (convenios sin IPR)
  🔍 CSV export
```

### Actos Administrativos

```
📍 /actos
  🔍 FilterBar: busqueda, estado (9), tipo (DECRETO/RESOLUCION/DECRETO_ALCALDICIO/OFICIO/CERTIFICADO/INFORME)
  🔍 PendingQueue: actos en estado VISADO (cola de firma para GOBERNADOR/AR)
  🔍 DataTable 7 cols: N° acto, tipo, materia, estado (StatusBadge), emisor, fecha, resolucion
  ✏️ Crear acto [D]:
    ↳ Tipo: Select (6 tipos)
    ↳ Materia/asunto: Input texto
    ↳ Emisor: ComboboxAsync
    ↳ Fecha emision: DatePicker
    ↳ Firmante: Select (signer_id → meta.role, no core.person)
    ↳ IPR/Convenio vinculado: ComboboxAsync (opcional)
    ↳ POST /api/actos
    ⚡ record_event: ACTO_CREATED
  ✏️ Transicionar estado (FSM 9-state):
    ↳ BORRADOR → EN_REVISION
    ↳ EN_REVISION → VISADO | BORRADOR
    ↳ VISADO → FIRMADO
    ↳ FIRMADO → ENVIADO_CGR
    ↳ ENVIADO_CGR → TOMADO_RAZON | RECHAZADO_CGR | OBSERVADO | ANULADO
    ↳ OBSERVADO → ENVIADO_CGR (reenviar) | ANULADO
    ↳ TOMADO_RAZON, RECHAZADO_CGR, ANULADO → (terminal)
  🔍 KPI strip: resumen (pending_firma, en_revision, by_state, by_type)
  🔍 CSV export
```

### Reuniones y Governance

```
📍 /reuniones
  🔍 FilterBar: estado (PROGRAMADA/EN_CURSO/FINALIZADA), tipo (Ordinaria/Extraordinaria)
  🔍 DataTable: comite, fecha, estado, temas, quorum
  ✏️ Crear reunion [D]:
    ↳ Comite: Select (auto-crea COMITE-CRISIS si no existe)
    ↳ Fecha: DateTimePicker
    ↳ Temas: Textarea
    ↳ POST /api/reuniones
    ⚡ record_event
  ✏️ Marcar EN_CURSO (valida quorum si aplica)
  ✏️ Finalizar (genera acta/minuta)
  ✏️ Registrar acuerdos

📍 /core-sessions
  🔍 Sesiones del CONSEJO-REGIONAL
  🔍 DataTable: fecha, estado, temas, presentes, quorum
  ✏️ Crear sesion [D]:
    ↳ Tipo: Ordinaria/Extraordinaria
    ↳ Fecha: DateTimePicker
    ↳ Temas (IPRs >7K UTM que requieren aprobacion CORE)
    ↳ POST /api/core-sessions
  🔍 Click → /core-sessions/{id} (detalle con voting table)

📍 /servicios
  🔍 Catalogo servicios DGI (cross-population, visible para todos)
    ↳ 4 areas: CG, MP, TD, KC
    ↳ DataTable: nombre, area, SLA dias, descripcion
  ✏️ Solicitar servicio [D]:
    ↳ Servicio: Select del catalogo
    ↳ Descripcion solicitud: Textarea
    ↳ Prioridad: Select
    ↳ POST /api/dgi/services/requests
```

### Admin (Exclusivo ADMIN_SISTEMA)

```
📍 /admin (5 tabs)

  [T] Usuarios
    🔍 Lista 24 usuarios activos
      ↳ DataTable: email, nombre, rol, division, estado, ultimo login
    ✏️ Crear usuario [D]:
      ↳ Email: Input (validacion regex)
      ↳ Nombre: Input
      ↳ Apellido paterno: Input
      ↳ Rol: Select (15 system_roles)
      ↳ Division: Select (condicional, solo si rol requiere division)
      ↳ Contrasena: Input (min 8 chars, strength indicator)
      ↳ POST /api/admin/usuarios
      ⚡ record_event: USER_CREATED
    ✏️ Editar usuario [D]:
      ↳ PATCH /api/admin/usuarios/{id} (allowlist validado)
    ✏️ Reset contrasena:
      ↳ POST /api/admin/usuarios/{id}/reset-password
      ↳ Min 8 chars, bcrypt hash inmediato
    🗑️ Soft-delete usuario (deleted_at = NOW())

  [T] Divisiones
    🔍 Lista organizaciones tipo DIVISION (9 entries)
    ✏️ Crear division [D]: codigo, nombre, parent_id (jerarquia)
    ✏️ Editar division [D]
    🗑️ Eliminar (soft-delete)

  [T] Configuracion
    🔍 Financing tracks: lista tracks con umbrales JSONB
    ✏️ CRUD financing tracks: nombre, mecanismo, thresholds (UTM, glosa%)
    🔍 Financial thresholds: 10 filas (4 UTM + 5 glosa% + UTM_VALUE)
    ✏️ Editar umbrales
    🔍 Niveles SNI: 4 niveles (Basico/Intermedio/Avanzado/Especializado)
    ✏️ Editar niveles SNI
    🔍 Categorias FRIL: 12 categorias (A2/A3 exentas)
    ✏️ CRUD categorias FRIL
    🔍 Fondos SUBV8: 7 fondos + ~22 topes (UNIQUE funcional via COALESCE)
    ✏️ CRUD fondos y topes
    🔍 Budget cycle milestones: 17 hitos
    ✏️ Editar hitos
    🔍 Rendition phases: 8 fases con SLA days
    ✏️ Editar SLA por fase

  [T] Monitoreo
    🔍 Data quality:
      ↳ 5 entidades con metricas de completitud (%)
      ↳ IPR: % con ejecutor, % con BIP, % con presupuesto
      ↳ Convenio: % con info CGR, % con cuotas
      ↳ Persona: % con email, % con telefono
      ↳ Organizacion: % con tipo, % con RUT
      ↳ Documento: 7 metricas
      ↳ ProgressBar por metrica
    🔍 SLA Dashboard:
      ↳ 12/12 SLAs monitoreados con semaforo
      ↳ verde ≥90%, amarillo ≥70%, rojo <70%
      ↳ Fuentes: admisibilidad (>30d), convenio pago (>90d), 4 fases rendicion, track-phase, etc.
      ↳ Drill-down: click SLA → lista entidades incumplidas

  [T] Auditoria
    🔍 txn.event paginado:
      ↳ 13 event_types: LOGIN, LOGIN_FAILED, PASSWORD_CHANGED, IPR_CREATED, IPR_STATUS_CHANGED, COMPROMISO_CREATED, COMPROMISO_COMPLETED, COMPROMISO_VERIFIED, AGREEMENT_CREATED, ACTO_CREATED, BUDGET_CREATED, ESCALATION_CREATED, MODIFICACION, ELIMINACION
      ↳ 5 filtros: entidad, event_type, usuario, rango fechas, accion
      ↳ Metadata de filtros en response
    🔍 JSON expandible por evento (detalle completo del cambio)
    🔍 CSV export (descarga todos los eventos filtrados)
```

---

## 2. ADMIN_REGIONAL — regional@goreos.cl

**Scope**: GLOBAL | **Division**: Ninguna | **Sidebar sections**: Comando, Gestion IPR, Finanzas, Institucional

Identico a ADMIN_SISTEMA excepto:

```
🔒 /admin — NO tiene acceso al modulo de administracion
🔒 CRUD usuarios, divisiones, configuracion, auditoria — bloqueado
```

### Arbol completo

```
📍 /dashboard → AttentionStrip + KPIs + ModuleMyTeam (global)
📍 /centro-de-mando → 6 KPIs + timeline (acceso completo)
📍 /riesgos → CRUD completo (crear, transicionar, editar, eliminar)
📍 /riesgos/{id} → Detalle + transiciones
📍 /ipr → Lista global sin restriccion + crear
📍 /ipr/nuevo → Crear IPR
📍 /ipr/{id} → 18 tabs completos (CRUD todos los satelites + transicionar estado)
📍 /ipr/cartera → Health signals por division
📍 /compromisos → CompromisosListView global + crear + completar + verificar
📍 /problemas → CRUD completo
📍 /alertas → Vista global
📍 /presupuesto → CRUD programas + CDPs
📍 /presupuesto/ciclo → Inicializar ciclo
📍 /convenios → CRUD completo + cuotas + 14-state FSM
📍 /actos → CRUD + PendingQueue (actos VISADO) + todas las transiciones
📍 /reuniones → CRUD reuniones
📍 /core-sessions → Crear sesion + gestionar
📍 /servicios → Catalogo + solicitar servicio
```

---

## 3. GOBERNADOR — gobernador@goreos.cl

**Scope**: GLOBAL | **Division**: Ninguna | **Sidebar sections**: Comando, Gestion IPR, Finanzas, Institucional (todos defaultOpen)

### Caracteristica exclusiva: Firma de actos (VISADO→FIRMADO)

```
📍 /dashboard → AttentionStrip + ModuleExecutivo (KPIs estrategicos)
  🔍 KPI enfocado en vision macro: IPRs por fase, presupuesto ejecucion global

📍 /centro-de-mando → 6 KPIs + timeline (vision ejecutiva)
📍 /riesgos → CRUD completo

📍 /ipr → Lista global completa
📍 /ipr/nuevo → Crear IPR
📍 /ipr/{id} → 18 tabs (CRUD completo)
📍 /ipr/cartera → Health signals todas las divisiones

📍 /compromisos → Vista global + crear + completar + verificar
📍 /problemas → CRUD completo
📍 /alertas → Vista global
📍 /presupuesto → CRUD programas
📍 /presupuesto/ciclo → Vista ciclos

📍 /convenios → CRUD completo + cuotas + transiciones

📍 /actos ⭐ ACCION EXCLUSIVA:
  🔍 PendingQueue prominente: actos en VISADO esperando firma
  ✏️ Firmar acto: VISADO → FIRMADO (click boton "Firmar")
    ↳ ConfirmDialog: "¿Confirma la firma de este acto?"
    ↳ PATCH /api/actos/{id} → state_id = FIRMADO
    ⚡ record_event: ACTO_STATE_CHANGED
  ✏️ Enviar a CGR: FIRMADO → ENVIADO_CGR
  ✏️ Crear acto [D]
  ✏️ Todas las transiciones de estado

📍 /reuniones → CRUD + presidir reuniones
📍 /core-sessions → Presidir sesiones CORE
📍 /servicios → Catalogo + solicitar

🔒 /admin — No tiene acceso
```

---

## 4-5. CONSEJERO_REGIONAL — consejero1@goreos.cl, consejero2@goreos.cl

**Scope**: GLOBAL | **Division**: Ninguna | **Sidebar sections**: Gestion IPR, Finanzas, Institucional

### Caracteristica exclusiva: Votar en sesiones CORE (Art. 36 LOC)

```
📍 /dashboard → AttentionStrip + KPIs (vista resumen)

📍 /ipr → Lista global (SOLO LECTURA, sin boton crear)
📍 /ipr/{id} → 18 tabs (SOLO LECTURA — sin crear/editar/eliminar en satelites)
  🔍 Puede ver todos los tabs: resumen, compromisos, problemas, alertas, etc.
  🔒 No puede crear compromisos, problemas, partes, territorio, hitos
  🔒 No puede transicionar estado IPR

📍 /compromisos → Vista lectura global (sin crear/completar/verificar)
📍 /problemas → Vista lectura (sin crear/transicionar)
📍 /alertas → Vista lectura
📍 /presupuesto → Vista lectura (sin crear programas)
📍 /presupuesto/ciclo → Vista lectura
📍 /convenios → Vista lectura + KPI strip (sin crear/transicionar)
📍 /actos → Vista lectura (sin PendingQueue, sin transiciones)

📍 /reuniones → Vista lectura

📍 /core-sessions ⭐ ACCION EXCLUSIVA:
  🔍 "Proxima sesion" card:
    ↳ Fecha proxima sesion
    ↳ Temas a tratar (IPRs >7K UTM)
    ↳ Quorum actual (N/16 presentes)
  🔍 DataTable sesiones: fecha, estado, temas, presentes
  🔍 Click → /core-sessions/{id}

📍 /core-sessions/{id} ⭐ ACCION EXCLUSIVA:
  🔍 Detalle sesion: temas, asistencia, acuerdos
  ✏️ Votar por cada IPR en agenda:
    ↳ [✓ Aprueba] o [✗ Rechaza] por IPR
    ↳ Comentarios opcionales
    ↳ POST /api/core-sessions/{id}/vote
    ↳ Quorum requerido:
      ↳ SIMPLE (general): 9/16 consejeros
      ↳ CALIFICADA (>7K UTM): 11/16 consejeros
    ⚡ record_event: VOTE_CAST
  🔍 Resultado votacion en tiempo real
  🔍 Acta/minuta (post-finalizacion)

📍 /servicios → Catalogo + solicitar

🔒 /centro-de-mando, /riesgos — No visible en sidebar
🔒 /admin — No tiene acceso
🔒 Crear/editar en IPR, compromisos, actos, convenios — Bloqueado
```

---

## 6. SECRETARIO_EJECUTIVO — secretario.core@goreos.cl

**Scope**: GLOBAL | **Division**: Ninguna | **Sidebar sections**: Institucional (defaultOpen)

### Caracteristica exclusiva: Gestionar reuniones y sesiones CORE (preparacion, actas, quorum)

```
📍 /dashboard → AttentionStrip + KPIs (vista limitada)

📍 /actos → Vista lectura
📍 /reuniones ⭐:
  🔍 Lista reuniones por comite
  ✏️ Crear reunion [D]: comite, fecha, temas
  ✏️ Marcar EN_CURSO (con validacion quorum)
  ✏️ Finalizar reunion (genera acta automatica)
  ✏️ Registrar acuerdos de la sesion

📍 /core-sessions ⭐:
  🔍 "Proxima sesion" card + guia preparacion (si agenda vacia → prompt "Preparar agenda")
  ✏️ Crear sesion CORE [D]:
    ↳ Tipo: Ordinaria/Extraordinaria
    ↳ Fecha: DateTimePicker
    ↳ Temas: IPRs >7K UTM que necesitan aprobacion
  ✏️ Registrar asistencia (check-in consejeros)
  ✏️ Registrar votos como secretario (en nombre de los consejeros)
  ✏️ Generar acta oficial

📍 /servicios → Catalogo + solicitar

🔒 /centro-de-mando, /riesgos — No visible
🔒 /ipr, /ipr/nuevo — No visible en sidebar (puede acceder por URL, solo lectura)
🔒 /compromisos, /problemas, /presupuesto, /convenios — No visible en sidebar
🔒 /admin — No tiene acceso
🔒 Crear/editar IPR, compromisos, actos, convenios — Bloqueado
```

---

## 7-12. JEFE_DIVISION — jefe.daf@goreos.cl, jefe.dideso@goreos.cl, jefe.difoi@goreos.cl, jefe.dipir@goreos.cl, jefe.diplade@goreos.cl, jefe.dit@goreos.cl

**Scope**: DIVISION (sponsor_division_id) | **Sidebar sections**: Gestion IPR (defaultOpen), Finanzas (defaultOpen), Institucional

Cada jefe ve SOLO los IPRs y entidades satelite de su division. Se documenta el arbol generico; la unica diferencia entre los 6 jefes es el filtro de division aplicado.

### Caracteristica exclusiva: Verificar compromisos (COMPLETADO→VERIFICADO), auto-scope division

```
📍 /dashboard → ModuleMyTeam (equipo de la division)
  🔍 Avatares equipo: miembros de la division (analistas, RTF, etc.)
  🔍 Drill-down: click miembro → /compromisos?responsible_id=X
  🔍 Progreso compromisos por miembro del equipo
  🔍 KPIs division: IPRs activos, compromisos vencidos, alertas

📍 /ipr ⭐ (auto-scoped a division):
  ⚡ Auto-filtro: division = mi division (via router.replace con ref guard)
  🔍 Context strip: "{N} IPRs en tu division"
  🔍 FilterBar: busqueda, estado, sector, mecanismo (pre-filtrado por division)
  ✏️ Crear IPR (pre-fill division = mi division)
  🔍 Click fila → /ipr/{id}
  🔒 IPRs fuera de su division → HTTP 403 "Sin acceso a este IPR"

📍 /ipr/nuevo → Crear IPR (division pre-seleccionada)

📍 /ipr/{id} → 18 tabs completos (SOLO para IPRs de su division)
  ✏️ Transicionar estado IPR
  ✏️ CRUD completo en todos los satelites:
    ↳ Compromisos: crear, completar, verificar ⭐
    ↳ Problemas: crear, transicionar
    ↳ CDPs: crear, eliminar
    ↳ Avances: crear
    ↳ Partes: agregar, eliminar
    ↳ Territorio: agregar, eliminar
    ↳ Hitos: crear, registrar fecha real
    ↳ Evaluaciones: registrar resultado
    ↳ Modificaciones: crear, aprobar/rechazar
    ↳ Cierre: crear, firmar
    ↳ Ex-post: registrar 4 dimensiones

📍 /compromisos ⭐ → CompromisosTeamView:
  🔍 KPI strip: total, pendientes, completados, verificados, vencidos
  🔍 Lista equipo expandible (click → compromisos del miembro)
  ✏️ Verificar inline: boton "Verificar" por compromiso COMPLETADO
    ↳ POST /api/compromisos/{id}/verify → COMPLETADO→VERIFICADO
    ⚡ record_event + create_notification
  ✏️ Crear compromiso [D]
  ✏️ Completar compromiso inline

📍 /problemas → CRUD (scoped a division)
📍 /alertas → Vista lectura (scoped)
📍 /presupuesto → Programas de su division
📍 /presupuesto/ciclo → Vista ciclo
📍 /convenios → Convenios de su division + transiciones + cuotas
📍 /actos → Vista + crear actos
📍 /reuniones → Vista + crear reuniones
📍 /core-sessions → Vista lectura
📍 /servicios → Catalogo + solicitar

🔒 /centro-de-mando — No visible en sidebar
🔒 /riesgos — No visible (solo DGI/admin)
🔒 /admin — No tiene acceso
🔒 /ipr/cartera — No visible (solo ADMIN/AR/GOB/JEFE_DGI)
🔒 IPRs de otras divisiones → HTTP 403
```

### Ejemplo especifico por division

| Usuario | Division | IPRs visibles | Presupuesto visible |
|---------|----------|---------------|---------------------|
| jefe.daf@goreos.cl | DAF | sponsor_division_id = DAF | Programas DAF |
| jefe.dideso@goreos.cl | DIDESO | sponsor_division_id = DIDESO | Programas DIDESO |
| jefe.difoi@goreos.cl | DIFOI | sponsor_division_id = DIFOI | Programas DIFOI |
| jefe.dipir@goreos.cl | DIPIR | sponsor_division_id = DIPIR | Programas DIPIR |
| jefe.diplade@goreos.cl | DIPLADE | sponsor_division_id = DIPLADE | Programas DIPLADE |
| jefe.dit@goreos.cl | DIT | sponsor_division_id = DIT | Programas DIT |

---

## 13. JEFE_DEPARTAMENTO — jefe.finanzas@goreos.cl

**Scope**: DIVISION (DAF) | **Sidebar sections**: Gestion IPR (defaultOpen), Finanzas (defaultOpen), Institucional, Mi Trabajo (defaultOpen)

### Caracteristica exclusiva: Pagina /aprobaciones (rendiciones + CDPs + cuotas pendientes)

```
📍 /dashboard → ModuleMyTeam (equipo departamento DAF)

📍 /ipr → Scoped a division DAF
📍 /ipr/{id} → 18 tabs (CRUD completo dentro de scope DAF)
📍 /compromisos → CompromisosTeamView + verificar
📍 /problemas → CRUD (scoped DAF)
📍 /alertas → Vista lectura
📍 /presupuesto → Programas DAF (crear, editar)
📍 /presupuesto/ciclo → Vista ciclo
📍 /convenios → Convenios DAF + transiciones + cuotas
📍 /actos → Vista + crear
📍 /reuniones → Vista + crear
📍 /core-sessions → Vista lectura
📍 /servicios → Catalogo + solicitar

📍 /aprobaciones ⭐ EXCLUSIVO JEFE_DEPARTAMENTO:
  🔍 3 secciones colapsables con count badges:

  Seccion 1: Rendiciones VISADA_RTF
    🔍 Lista rendiciones en estado VISADA_RTF (pendientes aprobacion jefe)
      ↳ Columnas: ID rendicion, convenio, monto, dias en fase
    ✏️ Aprobar: transicionar a EN_REVISION_UCR (confirma validez financiera)
    ✏️ Rechazar: devolver con observacion
    ✏️ Posponer: marcar para revision posterior

  Seccion 2: CDPs PENDIENTE
    🔍 Lista CDPs en estado PENDIENTE (pendientes autorizacion presupuestaria)
      ↳ Columnas: codigo CDP, IPR, monto, solicitante
    ✏️ Autorizar CDP (confirma disponibilidad presupuestaria)
    ✏️ Rechazar CDP

  Seccion 3: Cuotas PENDIENTE
    🔍 Lista cuotas de convenio en estado PENDIENTE (pendientes pago)
      ↳ Columnas: convenio, N° cuota, monto, vencimiento
    ✏️ Marcar PAGADO
    ✏️ Marcar EN_PROCESO
    ✏️ Diferir

  🔍 Count badges por seccion (ej: "Rendiciones (3)")

🔒 /centro-de-mando, /riesgos — No visible
🔒 /admin — No tiene acceso
🔒 IPRs fuera de DAF → HTTP 403
```

---

## 14. JEFE_UNIDAD — jefe.ucr@goreos.cl

**Scope**: DIVISION (DAF) | **Sidebar sections**: Gestion IPR (defaultOpen), Finanzas, Institucional, Mi Trabajo (defaultOpen)

```
📍 /dashboard → ModuleMyTeam

📍 /ipr → Scoped a division DAF
📍 /ipr/{id} → 18 tabs (CRUD dentro de scope)
📍 /compromisos → CompromisosTeamView

📍 /mis-compromisos ⭐:
  🔍 Mis tareas personales (Todoist-style):
    ↳ Agrupadas por IPR (collapsible sections)
    ↳ Items de 9 fuentes action-items
    ↳ Auto-expand secciones urgentes
    ↳ Click item → /ipr/{id}?tab=X
  ✏️ Completar tarea inline

📍 /problemas → CRUD (scoped)
📍 /alertas → Vista lectura
📍 /presupuesto → Programas DAF
📍 /convenios → Convenios DAF
📍 /actos → Vista + crear
📍 /reuniones → Vista
📍 /core-sessions → Vista lectura
📍 /servicios → Catalogo + solicitar

🔒 /centro-de-mando, /riesgos, /admin, /aprobaciones
```

---

## 15-18. ANALISTA — analista.dipir@goreos.cl, analista.diplade@goreos.cl, profesional.dit@goreos.cl, profesional.dideso@goreos.cl

**Scope**: PERSONAL (assignee_id / formulator_id) | **Sidebar sections**: Gestion IPR (defaultOpen), Finanzas, Institucional, Mi Trabajo (defaultOpen)

### Caracteristica exclusiva: ModuleMyWork (task list) + Formular IPR F0→F2

```
📍 /dashboard ⭐ → ModuleMyWork (Todoist-style):
  🔍 IPRs asignados agrupados + colapsables
  🔍 Items de 9 fuentes action-items (solo mis IPRs)
  🔍 Auto-expand secciones urgentes (deadline ≤3d)
  🔍 Click item → /ipr/{id}?tab=X (navega al tab relevante)
  🔍 Accion sugerida por item: "Completar partes", "Registrar avance", etc.

📍 /ipr (PERSONAL scope — solo mis IPRs):
  🔍 Lista solo IPRs donde soy assignee_id o formulator_id
  ✏️ Crear IPR → /ipr/nuevo (formulador = yo automaticamente)
  🔒 IPRs de otros → HTTP 403

📍 /ipr/nuevo → Crear IPR
  ✏️ Formulario: tipo, division, nombre, sector, mecanismo
  ⚡ formulator_id = mi user_id (automatico)
  ✏️ POST → redirect /ipr/{id}?tab=partes

📍 /ipr/{id} ⭐ (solo mis IPRs) → ModuleFormulacion:
  🔍 Pipeline F0→F2 con checklist por fase:
    F0 INGRESADO:
      ↳ [_] Mecanismo definido
      ↳ [_] Partes agregadas (≥1 beneficiario + ≥1 ejecutor)
      ↳ [_] Territorio definido (≥1 comuna)
      ↳ [_] Hitos creados (≥2)
    F1 EN_REVISION/PRE_ADMISIBLE:
      ↳ [_] Admisibilidad: X checks por verificar, Y verificados
    F2 EN_EVALUACION:
      ↳ [_] Evaluacion asignada
      ↳ [_] Resultado registrado (RS/FI/FC/etc.)
  🔍 suggested_action: "Agregar partes interesadas" (basado en checklist incompleto)
  🔍 suggested_tab: "partes" (navega automaticamente al tab sugerido)

  ✏️ CRUD en satelites de mis IPRs:
    ↳ Compromisos: crear, completar
    ↳ Problemas: crear, transicionar
    ↳ CDPs: crear, eliminar
    ↳ Avances: crear
    ↳ Partes: agregar, eliminar
    ↳ Territorio: agregar, eliminar
    ↳ Hitos: crear, registrar fecha real
    ↳ Evaluaciones: registrar resultado
  🔒 Transicionar estado IPR → bloqueado (solo JEFE+ puede avanzar de fase)
  🔒 Verificar compromisos → bloqueado (solo JEFE+)
  🔒 Aprobar/rechazar modificaciones → bloqueado

📍 /compromisos ⭐ → CompromisosWorkView:
  🔍 Mis compromisos grouped by IPR (collapsible):
    ↳ Seccion por IPR: titulo IPR, count tareas pendientes
    ↳ Dentro: lista compromisos con estado, vencimiento, accion
  ✏️ Completar compromiso (PENDIENTE→COMPLETADO)
  🔒 Verificar → bloqueado

📍 /mis-compromisos ⭐ → Mis tareas personales
  🔍 Todoist-style grouped by IPR
  ✏️ Completar inline

📍 /problemas → Crear + editar (solo en mis IPRs)
📍 /alertas → Vista lectura (solo alertas de mis IPRs)
📍 /presupuesto → Vista lectura
📍 /convenios → Vista lectura (mis IPRs)
📍 /actos → Vista lectura (empty state: "No tienes actos asignados")
📍 /reuniones → Vista lectura
📍 /core-sessions → Vista lectura
📍 /servicios → Catalogo + solicitar

🔒 /centro-de-mando, /riesgos, /admin, /aprobaciones
🔒 IPRs de otros → HTTP 403
🔒 Transicionar estado IPR, verificar compromisos, aprobar modificaciones
```

### Scope por usuario especifico

| Usuario | Division | IPRs visibles |
|---------|----------|---------------|
| analista.dipir | DIPIR | Solo donde assignee=yo OR formulator=yo |
| analista.diplade | DIPLADE | Solo donde assignee=yo OR formulator=yo |
| profesional.dit | DIT | Solo donde assignee=yo OR formulator=yo |
| profesional.dideso | DIDESO | Solo donde assignee=yo OR formulator=yo |

---

## 19. RTF — rtf.daf@goreos.cl

**Scope**: PERSONAL | **Division**: DAF | **Sidebar sections**: Gestion IPR, Finanzas, Institucional, Mi Trabajo (defaultOpen)

### Caracteristica exclusiva: Visar/Observar rendiciones SISREC (EN_REVISION_RTF)

```
📍 /dashboard → ModuleMyWork (tareas personales)

📍 /ipr → Solo IPRs donde soy assignee/formulator
📍 /ipr/{id} → 18 tabs (dentro de scope):
  📍 tab-rendiciones ⭐:
    🔍 Rendiciones del IPR con SLA clock
    ✏️ Visar rendicion: EN_REVISION_RTF → VISADA_RTF
      ↳ Confirma revision tecnica/financiera de la rendicion
      ↳ PATCH /api/dgi/data/rendiciones/{id} → state_id = VISADA_RTF
      ↳ SLA: 7 dias para revision RTF
    ✏️ Observar rendicion: EN_REVISION_RTF → OBSERVADA
      ↳ Devuelve rendicion con observaciones
      ↳ Textarea: observaciones obligatorias
      ↳ PATCH → state_id = OBSERVADA
    🔍 SLA clock: dias en EN_REVISION_RTF vs 7d limite
    🔍 Semaforo: verde <5d, ambar <7d, rojo >7d

📍 /mis-rendiciones ⭐ (Sidebar "Mi Trabajo"):
  → Navega a /datos?dominio=rendiciones&state=EN_REVISION_RTF
  🔍 Auto-filtro: rendiciones en EN_REVISION_RTF
  🔍 DataTable: ID, convenio, monto, dias en fase, SLA status
  ✏️ Visar inline
  ✏️ Observar inline

📍 /compromisos → CompromisosWorkView (mis tareas)
  ✏️ Completar compromisos
  🔒 Verificar → bloqueado

📍 /problemas → Crear (mis IPRs)
📍 /alertas → Vista lectura
📍 /presupuesto → Vista lectura
📍 /convenios → Vista lectura
📍 /actos → Vista lectura
📍 /reuniones → Vista lectura
📍 /servicios → Catalogo + solicitar

🔒 /centro-de-mando, /riesgos, /admin, /aprobaciones
🔒 Transicionar estado IPR → bloqueado
🔒 IPRs de otros → HTTP 403
```

---

## 20. ASESOR_JURIDICO — juridico@goreos.cl

**Scope**: PERSONAL | **Division**: Ninguna | **Sidebar sections**: Gestion IPR, Finanzas, Institucional (defaultOpen), Mi Trabajo (defaultOpen)

### Caracteristica exclusiva: V.B. juridico en actos (EN_REVISION→VISADO) y convenios

```
📍 /dashboard → KPIs + ModuleJuridico:
  🔍 Pendientes V.B.: count actos en EN_REVISION
  🔍 Convenios en revision juridica: count en EN_REVISION_JURIDICA
  🔍 Drill-down a cada cola

📍 /actos ⭐:
  ⚡ Auto-filtro → EN_REVISION (pendientes visacion juridica)
  🔍 PendingQueue: actos EN_REVISION (prominente)
  ✏️ Visar acto: EN_REVISION → VISADO (V.B. legalidad)
    ↳ Confirma revision juridica del acto
    ↳ PATCH /api/actos/{id} → state_id = VISADO
    ⚡ record_event: ACTO_STATE_CHANGED
  ✏️ Devolver a borrador: EN_REVISION → BORRADOR (con observaciones)
  ✏️ Crear acto [D]
  🔍 KPI strip: resumen estados

📍 /pendientes-vb ⭐ (Sidebar "Mi Trabajo"):
  → Navega a /actos?estado=EN_REVISION
  🔍 Cola de visacion juridica: actos esperando V.B.
  ✏️ Visar / Devolver inline

📍 /convenios ⭐:
  ⚡ Auto-filtro → EN_REVISION_JURIDICA
  ✏️ Visar convenio juridicamente: EN_REVISION_JURIDICA → FIRMADO_GORE
  ✏️ Devolver: EN_REVISION_JURIDICA → EN_NEGOCIACION (con observaciones)
  ✏️ Crear convenio [D]
  ✏️ Transicionar estado

📍 /ipr → Solo IPRs donde soy asesor (PERSONAL scope)
📍 /ipr/{id} → 18 tabs:
  📍 tab-admisibilidad: verificar checks (V.B. juridico para admisibilidad)
  ✏️ CRUD en satelites de mis IPRs

📍 /compromisos → CompromisosWorkView (mis tareas)
📍 /problemas → CRUD (mis IPRs)
📍 /alertas → Vista lectura
📍 /presupuesto → Vista lectura
📍 /reuniones → Vista lectura
📍 /core-sessions → Vista lectura
📍 /servicios → Catalogo + solicitar

🔒 /centro-de-mando, /riesgos, /admin, /aprobaciones
🔒 IPRs de otros → HTTP 403
```

---

# POBLACION DGI

---

## 21. JEFE_DGI — jefe.dgi@goreos.cl

**Scope**: GLOBAL | **Division**: DGI | **Sidebar sections**: Monitoreo (defaultOpen), Mejora Continua (defaultOpen), Coordinacion (defaultOpen), Analisis (defaultOpen)

Este es el rol mas amplio de la poblacion DGI. Acceso total a todas las funcionalidades DGI incluyendo gestion de servicios, lifecycle de indicadores, y comite TD.

### Dashboard

```
📍 /dashboard → DGI Cockpit (CockpitJefeDGI):
  🔍 4 modulos especializados:
    ↳ Escalamientos activos: count + nivel + deadline + drill-down
    ↳ SLA cumplimiento: % global + por fase rendicion
    ↳ Cartera IPR: health signal agregado + drill-down
    ↳ Indicadores DGI: VIGENTE count + senales criticas
  🔍 KPI strip DGI
  🔍 Click modulo → navega a pagina correspondiente
```

### Monitoreo

```
📍 /centro-de-mando
  🔍 6 KPIs paralelos + timeline (vista DGI)

📍 /cartera ⭐ (Cartera IPR — salud portafolio):
  🔍 Health signals por IPR:
    ↳ ROJO: alertas criticas o >30% compromisos vencidos
    ↳ AMARILLO: >5 problemas abiertos
    ↳ VERDE: sin senales
  🔍 DataTable 12 cols:
    ↳ Senal, BIP, nombre, mecanismo, fase
    ↳ Avance fisico%, avance financiero%
    ↳ Convenios (count), cuotas vencidas, alertas, problemas, compromisos vencidos
  🔍 Tab "Cuotas vencidas": cuotas PENDIENTE con deadline pasado
  🔍 Filtro: division, mecanismo, senal
  🔍 CSV export (IPRs + cuotas)

📍 /ipr/cartera → Cartera divisional (health por division)

📍 /alertas → Vista global DGI

📍 /datos?dominio=rendiciones → Rendiciones SISREC:
  🔍 Todas las rendiciones (sin auto-filtro, a diferencia de RTF)
  🔍 DataTable: ID, convenio, estado (8 fases), monto, dias en fase, SLA
  🔍 Dashboard SLA cumplimiento por fase
  🔍 Filtro estado, fase, convenio

📍 /riesgos → CRUD completo (crear, transicionar, editar, eliminar)
📍 /riesgos/{id} → Detalle + transiciones
```

### Mejora Continua

```
📍 /tablero ⭐ (Kanban DGI Initiatives):
  🔍 4 columnas WIP-managed:
    ↳ BACKLOG (sin limite)
    ↳ EN_CURSO (WIP limit: 5)
    ↳ REVISION (WIP limit: 2)
    ↳ COMPLETADO (sin limite)
  🔍 KanbanCard por iniciativa:
    ↳ Titulo, asignado, prioridad badge
    ↳ DMAIC phase badge (DEFINE/MEASURE/ANALYZE/IMPROVE/VERIFY)
    ↳ Aging badge (dias desde creacion, ambar >15d, rojo >30d)
  ✏️ Crear iniciativa [D]:
    ↳ Nombre: Input
    ↳ Descripcion: Textarea
    ↳ Asignado: Select (miembros DGI)
    ↳ Prioridad: Select (ALTA/MEDIA/BAJA)
    ↳ POST /api/dgi/initiatives → estado BACKLOG
    ⚡ Auto-genera codigo INI-NNNN (advisory-locked)
  ✏️ Drag-and-drop (@dnd-kit/sortable):
    ↳ Vertical: reordenar dentro de columna
    ↳ Horizontal: mover entre columnas
    ↳ Validacion WIP: si EN_CURSO ya tiene 5, toast error "WIP limit alcanzado"
    ↳ POST /api/dgi/initiatives/reorder (bulk sort_order update)
  ✏️ Mover iniciativa: POST /api/dgi/initiatives/{id}/move → nuevo status_id
  🗑️ Eliminar iniciativa (soft-delete, ConfirmDialog)
  🔍 Click card → /tablero/{id}

📍 /tablero/{id} ⭐ (DMAIC 5 fases):
  🔍 Stepper 5 fases: DEFINE → MEASURE → ANALYZE → IMPROVE → VERIFY
    ↳ Fase activa resaltada, fases completadas con check
    ↳ Fases futuras en gris (no editables)
  ✏️ Editar contenido por fase (textareas phase-gated):
    ↳ DEFINE: definicion problema, objetivo, alcance, equipo
    ↳ MEASURE: metricas baseline, datos recopilados, metodo medicion
    ↳ ANALYZE: analisis causa raiz, diagrama, hallazgos
    ↳ IMPROVE: solucion propuesta, plan implementacion, resultados esperados
    ↳ VERIFY: resultados obtenidos, comparacion before/after, lecciones
    ↳ PATCH → atomic jsonb_set en metadata JSONB
  ✏️ Avanzar fase (forward-only):
    ↳ POST /api/dgi/initiatives/{id}/dmaic/transition → next phase
    ↳ Gate validation (informational, no blocking)
    ⚡ trg_initiative_timing trigger actualiza started_at/completed_at
  🔍 LeanMetricsPanel (collapsible KPIs):
    ↳ Throughput: initiatives completadas/mes
    ↳ Lead time: promedio dias BACKLOG→COMPLETADO
    ↳ Cycle time: promedio dias EN_CURSO→COMPLETADO
    ↳ WIP: count EN_CURSO + REVISION
    ↳ Aging: dias promedio en columna actual
  🔍 Comparacion before/after: metricas antes y despues de implementacion
  🔍 Matriz impacto/esfuerzo 3x3: posicion de la iniciativa

📍 /procesos ⭐ (Catalogo de procesos):
  🔍 FilterBar: estado (6), criticidad (ALTO/MEDIO/BAJO), busqueda
  🔍 DataTable 6 cols: codigo (auto-locked), nombre, division, estado, criticidad, creado
  ✏️ Crear proceso [D]:
    ↳ Nombre: Input
    ↳ Division: Select
    ↳ Descripcion: Textarea
    ↳ Alcance: Textarea
    ↳ Criticidad: Select (ALTO/MEDIO/BAJO)
    ↳ POST /api/dgi/processes → estado IDENTIFICADO, auto-genera codigo
  ✏️ Transicionar FSM 6-state:
    ↳ IDENTIFICADO → EN_LEVANTAMIENTO
    ↳ EN_LEVANTAMIENTO → MODELADO
    ↳ MODELADO → VALIDADO
    ↳ VALIDADO → PUBLICADO
    ↳ PUBLICADO → SUSPENDIDO (o reverse)
    ↳ SUSPENDIDO → EN_LEVANTAMIENTO
  🗑️ Eliminar proceso (soft-delete)
  🔍 Click → /procesos/{id}

📍 /procesos/{id} (Detalle proceso — 6 tabs):
  🔍 Hero card: nombre, estado, criticidad, division, creador
  ✏️ Editar proceso (drawer)
  ✏️ Transicionar estado (botones inline)

  [T] tab-actores:
    🔍 Lista actores del proceso
    ✏️ Agregar actor [D]: tipo (ROL/SISTEMA/DIVISION), nombre, responsabilidad
    🗑️ Eliminar actor

  [T] tab-reglas:
    🔍 Reglas del proceso
    ✏️ Agregar regla [D]: codigo, descripcion, tipo
    ↳ 409 duplicate handling (codigo unico)
    🗑️ Eliminar regla

  [T] tab-metricas:
    🔍 Metricas del proceso (6 campos)
    ✏️ Agregar metrica [D]: nombre, formula, unidad, baseline, target, frecuencia
    ✏️ Toggle "Comparar": before/after metricas
    🗑️ Eliminar metrica

  [T] tab-puntos-dolor:
    🔍 Pain points del proceso (con colores de impacto)
    ✏️ Agregar pain point [D]: descripcion, impacto (ALTO/MEDIO/BAJO), area afectada
    🗑️ Eliminar pain point

  [T] tab-oportunidades:
    🔍 Oportunidades de mejora (bridge Process → Opportunity → Initiative MP-013)
    ✏️ Crear oportunidad [D]: descripcion, impacto, esfuerzo
    ✏️ Toggle "Matriz": vista impacto/esfuerzo 3x3
    🔍 Link a iniciativa DGI (si existe)
    🗑️ Eliminar oportunidad

  [T] tab-documentos:
    🔍 Documentos BPMN del proceso
    ✏️ Agregar referencia documento

📍 /procesos/progreso (Dashboard progreso):
  🔍 Distribucion por estado (barras)
  🔍 Distribucion por criticidad
  🔍 KPI strip
  🔍 Drill-down a proceso individual

📍 /cuellos-de-botella ⭐:
  🔍 3 tipos de scan cards:
    ↳ ACUMULACION: procesos con colas crecientes
    ↳ CICLO_TIEMPO: procesos donde cycle time > SLA
    ↳ PRESUPUESTO: procesos con presupuesto sub-ejecutado
  ✏️ Ejecutar escaneo: POST /api/dgi/bottleneck/detect
    ↳ Retorna hallazgos con severidad
  🔍 Investigaciones DataTable:
    ↳ Columnas: codigo (auto-gen), tipo, severidad, estado, proceso
  ✏️ Crear investigacion desde hallazgo [D]:
    ↳ Pre-fill tipo y proceso del hallazgo
    ↳ POST /api/dgi/bottleneck/investigations
  🔍 Click → /cuellos-de-botella/{id}

📍 /cuellos-de-botella/{id}:
  🔍 6-phase stepper: DETECTADO→VERIFICADO→ANALIZADO→PROPUESTO→IMPLEMENTADO→CERRADO
  ✏️ Campos por fase (textareas gated):
    ↳ DETECTADO: descripcion, evidencia
    ↳ VERIFICADO: confirmacion, datos adicionales
    ↳ ANALIZADO: causa raiz, analisis
    ↳ PROPUESTO: solucion propuesta, plan
    ↳ IMPLEMENTADO: resultados, evidencia
    ↳ CERRADO: conclusiones, lecciones
  ✏️ Avanzar fase (linear forward-only)
```

### Coordinacion

```
📍 /coordinacion ⭐:
  [T] Decisiones AR:
    🔍 Lista decisiones AR (tipo: PRIORIDAD/RECURSO/ESCALAMIENTO/ESTRATEGIA)
    🔍 Estado: PENDIENTE | EN_EJECUCION | COMPLETADA
    ✏️ Crear decision [D]: tipo, impacto, recomendacion, source_session_id (bridge crisis)
    ✏️ Transicionar estado
    🗑️ Eliminar decision

  [T] Divisiones:
    🔍 Matriz interaccion (7 divisiones x 5 tipos):
      ↳ Tipos: PRESUPUESTO, CARTERA, JURIDICO, TECNOLOGIA, PROCESO
      ↳ Heatmap: dias desde ultima interaccion (verde <7d, ambar <30d, rojo >30d)
    ✏️ Actualizar interaccion [D]: tipo, notas, fecha

📍 /escalamiento ⭐ (Protocolo 4 niveles):
  🔍 Tabs estado: TODOS | ABIERTO | EN_GESTION | RESUELTO | CERRADO
  🔍 DataTable 6 cols: codigo ESC-YYYY-NNNN, situacion, nivel, estado, vencimiento, impacto
  🔍 DeadlineCell: SLA por nivel (N1=1x, N1.5=1.5x, N2=2x del SLA base)
  ✏️ Crear escalamiento [D]:
    ↳ Nivel: Select (NIVEL_1, NIVEL_2, NIVEL_3, NIVEL_4)
    ↳ Situacion: Textarea
    ↳ Impacto: Textarea
    ↳ Recomendacion: Textarea
    ↳ Subject type/id: entidad afectada (opcional)
    ↳ POST /api/dgi/escalation
    ⚡ Auto-genera ESC-YYYY-NNNN (advisory-locked)
    ⚡ Auto-crea alerta (CRITICO si N3/N4, ALTO si N1/N2)
    ⚡ Auto-notificacion a JEFE_DGI
  ✏️ Transicionar: ABIERTO → EN_GESTION → RESUELTO → CERRADO
  🗑️ Eliminar escalamiento
  🔍 Click → /escalamiento/{id}
  🔍 CSV export

📍 /escalamiento/{id}:
  🔍 Detalle completo: situacion, impacto, nivel, deadline, alerta vinculada
  🔍 Linear state progress: ABIERTO → EN_GESTION → RESUELTO → CERRADO
  🔍 SLA indicator (timeline con deadline)
  ✏️ Transicionar estado
  ✏️ Editar campos

📍 /servicios ⭐ (Gestion catalogo — exclusivo JEFE_DGI):
  🔍 Catalogo servicios DGI
  ✏️ Crear servicio [D]:
    ↳ Nombre: Input
    ↳ Area: Select (CG/MP/TD/KC)
    ↳ SLA dias: Input numerico
    ↳ Descripcion: Textarea
    ↳ POST /api/dgi/services
  ✏️ Editar servicio [D]: PATCH
  🗑️ Eliminar servicio (soft-delete)
  🔍 Dashboard SLA requests:
    ↳ Requests por estado, % cumplimiento SLA, tiempo promedio resolucion
  ✏️ Gestionar solicitudes:
    ↳ Asignar miembro DGI
    ↳ Cambiar estado (PENDIENTE → EN_PROGRESO → COMPLETADA | RECHAZADA)

📍 /comite-td ⭐ (Comite Transformacion Digital):
  🔍 Lista sesiones TD (COMITE-TD, sin voting/quorum)
  ✏️ Crear sesion [D]: fecha, temas
  ✏️ Agregar tema inline
  ✏️ Agregar acuerdo inline
  🔍 Detalle inline expandible (click fila)

📍 /calendario (5 fuentes unificadas):
  🔍 Eventos de: sesiones, interacciones, decisiones, escalamientos, SLA
  🔍 Filtro tipo (tabs): TODOS | SESSION | INTERACTION | DECISION | ESCALATION | SLA
  🔍 Filtro rango fechas (default: hoy ± 30d)
  🔍 Agrupado por fecha
  🔍 Cada evento: badge categoria, severidad semaforo, titulo, link drill-down
```

### Analisis

```
📍 /datos ⭐ (Portal datos — 9 dominios):
  🔍 Sidebar dominios: IPR, Indicadores, Presupuesto, Convenios, Organizaciones, Personas, Territorio, Eventos, Rendiciones
  🔍 DataTable dinamico por dominio seleccionado
  🔍 Drawer detalle por entidad
  ✏️ Crear indicador [D]:
    ↳ Nombre: Input
    ↳ Dimension: Select (5 dimensiones DGI)
    ↳ Senal: Select (ref.category scheme=dgi_signal)
    ↳ Frecuencia: Select (MENSUAL/TRIMESTRAL/SEMESTRAL/ANUAL)
    ↳ Formula: Textarea
    ↳ Fuente: Input
    ↳ POST /api/dgi/data/indicators → lifecycle BORRADOR
  ✏️ Lifecycle transition indicador (exclusivo JEFE_DGI):
    ↳ BORRADOR → VIGENTE → DEPRECADO → ARCHIVADO (+ PROPUESTO path)
    ↳ POST /api/dgi/data/indicators/{id}/lifecycle-transition
  ✏️ Registrar valor manual:
    ↳ POST /api/dgi/data/indicators/{id}/manual-value
    ↳ Valor + periodo + observacion
  🔍 Refresh indicadores VIGENTE:
    ↳ POST /api/dgi/data/indicators/refresh (idempotente)
    ↳ Scoped a lifecycle=VIGENTE
  🔍 CSV export

📍 /informes ⭐ (Reportes DGI):
  🔍 Tabs tipo: TODOS | FLASH | SEMANAL | MENSUAL | TEMATICO
  🔍 DataTable: titulo, tipo, estado (BORRADOR/PUBLICADO/ARCHIVADO), periodo, creado
  ✏️ Crear informe [D]:
    ↳ Tipo: Select (4 tipos)
    ↳ Titulo: Input
    ↳ Periodo: Input
    ↳ POST /api/dgi/reports → estado BORRADOR
  ✏️ Editar secciones (atomic jsonb_set):
    ↳ Cada seccion: titulo, contenido (auto-populated flag), last_edited_at
    ↳ FLASH: resumen KPI
    ↳ SEMANAL: actividades semana
    ↳ MENSUAL: tendencias mes
    ↳ TEMATICO: analisis custom
  ✏️ Publicar: BORRADOR → PUBLICADO
  ✏️ Archivar: PUBLICADO → ARCHIVADO
  🔍 Click → /informes/{id}

📍 /informes/{id}:
  🔍 ScrollArea con secciones del reporte
  ✏️ Edit mode toggle: textareas inline con "Guardar"
  🔍 Auto-populated indicator en secciones con datos del sistema
```

---

## 22. ESP_CONTROL_GESTION — control.gestion@goreos.cl

**Scope**: GLOBAL | **Division**: DGI | **Sidebar sections**: Monitoreo (defaultOpen), Mejora Continua, Coordinacion, Analisis (defaultOpen)

Identico a JEFE_DGI excepto las siguientes restricciones:

```
🔒 Crear servicio en catalogo (solo JEFE_DGI)
🔒 Lifecycle transition indicadores (solo JEFE_DGI puede cambiar BORRADOR→VIGENTE→DEPRECADO)
🔒 /comite-td — No visible en sidebar (solo JEFE_DGI + ESP_TD)
```

### Arbol diferencial

```
📍 /dashboard → CockpitControlGestion:
  🔍 KPIs: bottleneck summary, SLA compliance, cartera health
  🔍 Agenda derivada de alertas + rendiciones

📍 /centro-de-mando, /cartera, /ipr/cartera, /alertas, /riesgos → Identico a JEFE_DGI
📍 /datos?dominio=rendiciones → Rendiciones SLA monitoring

📍 /tablero → Kanban completo (crear, drag-drop, DMAIC)
📍 /tablero/{id} → DMAIC 5 fases
📍 /procesos → CRUD completo procesos
📍 /procesos/{id} → 6 tabs CRUD
📍 /procesos/progreso → Dashboard
📍 /cuellos-de-botella → Escaneo + investigaciones CRUD

📍 /coordinacion → AR decisions + divisiones matrix
📍 /escalamiento ⭐ → CRUD escalamientos (puede crear nivel 1-4)
📍 /escalamiento/{id} → Detalle + transiciones
📍 /servicios → Catalogo (LECTURA) + solicitar + gestionar requests DGI
  🔒 Crear/eliminar servicio en catalogo
📍 /calendario → Vista unificada 5 fuentes

📍 /datos → 9 dominios
  ✏️ Crear indicador [D]
  ✏️ Registrar valor manual
  🔒 Lifecycle transition indicadores
📍 /informes → CRUD reportes (crear, editar, publicar, archivar)
📍 /informes/{id} → Detalle + edit mode
```

---

## 23. ESP_PROCESOS — procesos@goreos.cl

**Scope**: GLOBAL | **Division**: DGI | **Sidebar sections**: Monitoreo (defaultOpen), Mejora Continua (defaultOpen), Coordinacion, Analisis

Enfocado en mejora continua y procesos. Restricciones adicionales sobre JEFE_DGI:

```
🔒 /comite-td — No visible
🔒 Crear/editar servicios en catalogo
🔒 Lifecycle transition indicadores
🔒 Crear escalamientos (solo JEFE_DGI + ESP_CONTROL_GESTION)
🔒 Crear/editar informes (solo JEFE_DGI + ESP_CONTROL_GESTION)
```

### Arbol completo

```
📍 /dashboard → CockpitProcesos:
  🔍 Agenda desde comites + BPMN
  🔍 Work queue con deadlines

📍 /centro-de-mando → KPIs (lectura)
📍 /cartera → Health signals (lectura)
📍 /ipr/cartera → Cartera divisional (lectura)
📍 /alertas → Vista DGI (lectura)
📍 /riesgos → CRUD completo
📍 /datos?dominio=rendiciones → Rendiciones (lectura)

📍 /tablero ⭐ → Kanban completo (crear, drag-drop, reordenar)
📍 /tablero/{id} ⭐ → DMAIC 5 fases (editar, avanzar)
📍 /procesos ⭐ → CRUD completo procesos (crear, transicionar, eliminar)
📍 /procesos/{id} ⭐ → 6 tabs CRUD completo
📍 /procesos/progreso ⭐ → Dashboard
📍 /cuellos-de-botella ⭐ → Escaneo + investigaciones CRUD

📍 /coordinacion → Vista lectura (AR decisions + divisiones)
📍 /escalamiento → Vista lectura (sin crear/editar)
📍 /servicios → Catalogo lectura + solicitar
📍 /calendario → Vista unificada

📍 /datos → Lectura dominios
📍 /informes → Vista lectura (sin crear/editar)
```

---

## 24. ESP_TD — td@goreos.cl

**Scope**: GLOBAL | **Division**: DGI | **Sidebar sections**: Monitoreo, Mejora Continua (defaultOpen), Coordinacion, Analisis

Enfocado en transformacion digital y tecnologia. Restricciones:

```
🔒 Crear/editar servicios en catalogo
🔒 Lifecycle transition indicadores
🔒 Crear escalamientos
🔒 Crear/editar informes
```

### Caracteristica exclusiva: Comite TD + Decretos DS7-DS12

```
📍 /dashboard → CockpitTD:
  🔍 3 cards velocidad TDE:
    ↳ Velocidad actual (derivada de indicadores TDE)
    ↳ Velocidad target
    ↳ Tendencia (up/down/stable)
  🔍 Ley 21.180 deadline: dias restantes + progress
  🔍 Decretos pendientes: DS7-DS12 con estado

📍 /centro-de-mando → KPIs (lectura)
📍 /cartera → Health signals (lectura)
📍 /ipr/cartera → Cartera divisional (lectura)
📍 /alertas → Vista DGI (lectura)
📍 /riesgos → CRUD completo

📍 /tablero → Kanban completo (crear, drag-drop, DMAIC)
📍 /tablero/{id} → DMAIC 5 fases
📍 /procesos → CRUD procesos
📍 /procesos/{id} → 6 tabs
📍 /procesos/progreso → Dashboard
📍 /cuellos-de-botella → Escaneo + investigaciones

📍 /comite-td ⭐ (Exclusivo con JEFE_DGI):
  🔍 Lista sesiones TD
  ✏️ Crear sesion TD [D]: fecha, temas
  ✏️ Agregar tema inline
  ✏️ Agregar acuerdo inline
  🔍 Detalle inline expandible
  🔍 Sin voting ni quorum (a diferencia de CORE sessions)

📍 /coordinacion → Vista lectura
📍 /escalamiento → Vista lectura
📍 /servicios → Catalogo lectura + solicitar
📍 /calendario → Vista unificada

📍 /datos ⭐ → 9 dominios + decretos:
  🔍 Lectura todos los dominios
  ✏️ PATCH decretos (DS7-DS12, Ley 21.180):
    ↳ Actualizar estado decreto
    ↳ Registrar fecha cumplimiento
    ↳ Atomic jsonb_set en metadata

📍 /informes → Vista lectura
```

---

# FUNCIONALIDAD CROSS-POPULATION

## Servicios DGI (visible para TODOS)

```
Todos los 24 usuarios pueden:
📍 /servicios → Ver catalogo de servicios DGI
  🔍 Lista: nombre, area (CG/MP/TD/KC), SLA dias, descripcion
  ✏️ Solicitar servicio [D]:
    ↳ Servicio: Select del catalogo
    ↳ Descripcion: Textarea
    ↳ Prioridad: Select (ALTA/MEDIA/BAJA)
    ↳ POST /api/dgi/services/requests
    ↳ Asignado automaticamente al equipo DGI

Solo JEFE_DGI puede:
  ✏️ Crear/editar/eliminar servicios del catalogo
  ✏️ Gestionar solicitudes (asignar, cambiar estado)
```

## Notificaciones (todos los usuarios)

```
Todos los 24 usuarios tienen:
🔔 Bell icon (header derecho):
  🔍 Dropdown con notificaciones no leidas
  🔍 Polling cada 60 segundos
  🔍 7 categorias: compromiso, alerta, ipr, rendicion, escalamiento, riesgo, servicio
  🔍 Timestamps relativos (formatRelativeTime es-CL)
  ✏️ Mark as read (click notificacion)
  ✏️ Mark all as read

10 puntos de auto-generacion:
  ⚡ Compromiso creado → notifica responsable
  ⚡ Compromiso completado → notifica jefe division
  ⚡ Compromiso verificado → notifica responsable
  ⚡ IPR transicion estado → notifica responsable
  ⚡ SLA batch rendicion → notifica RTF/jefe relevante
  ⚡ SLA batch convenio → notifica responsable convenio
  ⚡ SLA batch track-phase → notifica formulador
  ⚡ SLA batch admisibilidad → notifica formulador
  ⚡ Riesgo ALTA/MUY_ALTA → notifica jefe DGI
  ⚡ Escalamiento creado → notifica jefe DGI
```

## Busqueda Global (todos los usuarios, Cmd+K)

```
Todos los 24 usuarios tienen:
⌘K Global Search:
  🔍 Busqueda cross-entity: IPR (codigo_bip + nombre), compromisos, convenios
  🔍 Resultados agrupados por tipo
  🔍 Click resultado → navega a detalle
  🔍 IDOR-scoped: solo muestra resultados dentro del scope del usuario
```

---

# DEV TOOLING (solo en devMode)

```
Solo cuando localStorage.goreos_dev_mode === "true" (activado via /dev login):

📍 /dev (Quick Login):
  🔍 24 cards de usuarios agrupados en 5 arquetipos:
    ↳ Ejecutores: analistas, RTF, juridico
    ↳ Supervisores: jefes division/departamento/unidad
    ↳ Estrategas: gobernador, admin regional, consejeros, secretario
    ↳ DGI: jefe DGI, especialistas CG/MP/TD
    ↳ Sistema: admin sistema
  ✏️ Click card → auto-login (POST /api/auth/login → redirect /dashboard)
  ⚡ Activa goreos_dev_mode en localStorage

📍 /dev/testing (Checklist + Bugs):
  [T] Checklist:
    🔍 17 journeys, categorias, progress % por rol
    🔍 Grupos de tareas colapsables
    ✏️ Check/uncheck tarea (persiste a api/dev-data/test-checklist-state.json)
    🔍 Barra progreso global

  [T] Bugs:
    🔍 KPI strip: total, abiertos, cerrados
    🔍 Cards expandibles por bug: titulo, pasos, contexto, screenshot
    🔍 Export JSON

  FAB 🐛 (boton flotante z-50, siempre visible en devMode):
    ✏️ Click → DrawerPanel bug report:
      ↳ Auto-context: usuario, rol, URL actual, viewport, checklist item activo
      ↳ Titulo: Input
      ↳ Pasos para reproducir: Textarea
      ↳ Screenshot: paste (⌘V) o upload archivo
      ↳ POST /api/dev/bugs → persiste a api/dev-data/test-bugs.json (mounted volume)

⚡ devMode se limpia en login normal (no-dev)
⚡ Sidebar link "Testing" visible solo en devMode
```

---

# MATRIZ RESUMEN

## Acciones por Rol

| Rol | Rutas | Lectura | Escritura | Destructiva | Exclusividad |
|-----|:-----:|:-------:|:---------:|:-----------:|--------------|
| ADMIN_SISTEMA | 38 | ~90 | ~85 | ~25 | /admin (5 tabs), CRUD users/config |
| ADMIN_REGIONAL | 35 | ~85 | ~75 | ~20 | Centro de Mando full |
| GOBERNADOR | 35 | ~80 | ~60 | ~15 | Firma actos (VISADO→FIRMADO) |
| CONSEJERO_REGIONAL (x2) | 25 | ~50 | ~5 | 0 | Votar en CORE (quorum) |
| SECRETARIO_EJECUTIVO | 15 | ~20 | ~15 | ~3 | Gestionar reuniones + actas |
| JEFE_DIVISION (x6) | 30 | ~70 | ~65 | ~18 | Verificar compromisos, scope division |
| JEFE_DEPARTAMENTO | 32 | ~72 | ~67 | ~18 | /aprobaciones (rendiciones+CDPs+cuotas) |
| JEFE_UNIDAD | 28 | ~60 | ~55 | ~15 | Mis compromisos |
| ANALISTA (x4) | 25 | ~45 | ~40 | ~10 | ModuleMyWork, formular F0→F2 |
| RTF | 22 | ~40 | ~15 | ~5 | Visar/Observar SISREC |
| ASESOR_JURIDICO | 24 | ~45 | ~25 | ~8 | V.B. juridico actos+convenios |
| JEFE_DGI | 35 | ~90 | ~85 | ~25 | Full DGI + servicios + lifecycle indicadores |
| ESP_CONTROL_GESTION | 30 | ~75 | ~60 | ~15 | Bottleneck + SLA + escalamientos |
| ESP_PROCESOS | 28 | ~65 | ~55 | ~12 | Procesos DMAIC, cuellos botella |
| ESP_TD | 25 | ~55 | ~40 | ~10 | Comite TD, decretos DS7-DS12 |

## Scope IDOR por Rol

| Scope | Roles | IPRs visibles | Mecanismo |
|-------|-------|---------------|-----------|
| GLOBAL | ADMIN_SISTEMA, ADMIN_REGIONAL, GOBERNADOR, SECRETARIO_EJECUTIVO, CONSEJERO_REGIONAL, JEFE_DGI, ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD | Todos (3,732) | Sin query adicional |
| DIVISION | JEFE_DIVISION (x6), JEFE_DEPARTAMENTO, JEFE_UNIDAD | Solo su division | WHERE sponsor_division_id = :div_id |
| PERSONAL | ANALISTA (x4), RTF, ASESOR_JURIDICO | Solo asignados | WHERE assignee_id = :uid OR formulator_id = :uid |

## FSMs del Sistema

| Entidad | Estados | Terminal | Trigger DB | Router |
|---------|:-------:|:--------:|:----------:|--------|
| IPR (ipr_state) | 32 | CERRADO, ANULADO | trg_ipr_state_transition | ipr.py |
| Convenio (agreement_state) | 14 | VENCIDO, TERMINADO, RESCILIADO, CANCELADO | trg_agreement_state_transition | convenios.py |
| Acto (act_state) | 9 | TOMADO_RAZON, RECHAZADO_CGR, ANULADO | trg_act_state_transition | actos.py |
| Rendicion (rendition_state) | 8 | APROBADA, RECHAZADA | trg_rendition_state_transition | dgi_data.py |
| Compromiso (commitment_state) | 5 | VERIFICADO, CANCELADO | trg_commitment_state_transition | compromisos.py |
| Problema (problem_state) | 4 | RESUELTO, CERRADO_SIN_RESOLVER | trg_problem_state_transition | problemas.py |
| Riesgo (risk_status) | 6 | CERRADO | trg_risk_status_transition | risk.py |
| DGI Iniciativa (dgi_initiative_status) | 4 | COMPLETADO | trg_dgi_initiative_status_transition | dgi_initiatives.py |
| DGI Proceso (dgi_process_status) | 6 | PUBLICADO/SUSPENDIDO | trg_dgi_process_status | dgi_processes.py |
| Modificacion IPR (modification_status) | 3 | APROBADA, RECHAZADA | trg_modification_state_transition | ipr.py |
| Escalamiento (dgi_escalation_status) | 4 | CERRADO | trg_escalation_state_transition | dgi_escalation.py |
| Servicio request | 4 | COMPLETADA, RECHAZADA | trg_request_state_transition | dgi_services.py |
| Pago cuota (payment_status) | 4 | PAGADO, RECHAZADO | trg_installment_payment_transition | convenios.py |

---

*Generado: 2026-03-23 | Sesion C61 | 24 usuarios, 15 roles, 38 rutas, 304 endpoints, 13 FSMs*
