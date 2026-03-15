# GORE_OS — Especificación de Usuarios y Journeys v3.1

**Versión**: 3.1
**Fecha**: 2026-03-15
**Estado**: Vigente
**Fuentes**: SSOT Bundle v1.5.0, Omega v3.0.0, DGI User Stories v1.0, User Stories (818), Procesos (81), GORE_OS codebase
**Autoridad**: Organigrama GORE 2026 > Ontología goreNubleBundle > Omega > CQs

---

## 1. Propósito

Este documento es la especificación autoritativa de los usuarios del sistema GORE_OS, sus arquetipos, journeys y principios de diseño UX. Integra:

- La estructura orgánica de GORE Ñuble (SSOT `ssot-organica.md`)
- Los 16 roles del sistema mapeados a 8 arquetipos de usuario
- Los 17 journeys individuales + 1 transversal (Ciclo IPR 360°)
- Los 8 principios de diseño UX que gobiernan decisiones de interfaz
- El estado de implementación y gaps abiertos

**Audiencia**: Desarrolladores, diseñadores UX, product owners, stakeholders GORE Ñuble.

### 1.1 Alcance y Exclusiones

Este documento cubre los journeys implementados o planificados en GORE_OS. La cobertura sobre los 16 dominios de user stories (`model/stories/`) es parcial por diseño:

| Cobertura | Dominios | Stories | Justificación |
|-----------|----------|---------|---------------|
| **Cubierto** | D-EJEC (ejecución IPR), D-FIN-IPR_CORE (finanzas IPR), D-GOB (gobernanza CORE) | ~160 | Núcleo operativo del sistema |
| **Parcial** | D-NORM (normativo — actos/convenios), D-TDE (via ESP_TD), D-GESTION (via DGI control gestión), D-FIN-EJECUTORES (rendiciones) | ~140 | Cubierto donde hay sistema; funciones externas (CGR, SIGFE) no modeladas |
| **Excluido** | D-BACK (RRHH, inventarios, flota — 105 stories) | 105 | Sin módulo RRHH en GORE_OS — requiere sistema dedicado |
| **Excluido** | D-TDE (108 stories — solo 7 via ESP_TD) | 101 | Ley 21.180, FEA, GESDOC son sistemas externos |
| **Excluido** | D-TERR (geodatos — 48 stories) | 48 | Sin módulo geoespacial — requiere GIS |
| **Excluido** | D-PLAN (planificación — 33 stories) | 33 | ARI/PROPIR, ERD, PROT son procesos no digitalizados |
| **Excluido** | D-DEV (desarrollo — 37 stories), D-OPS (operaciones — 47) | 84 | Internos al equipo de desarrollo |
| **Excluido** | D-SOC (social — 23 stories) | 23 | Participación ciudadana — sin módulo |
| **Excluido** | D-SEG (seguridad — 18 stories) | 18 | Seguridad interna — cubierto por middleware |
| **Excluido** | D-EVOL (evolución — 14 stories) | 14 | Roadmap futuro |
| **Referenciado** | FENIX (crisis — 11 stories, 2 procesos) | 11 | Referenciado en J6 como protocolo de escalación |

**Total cubierto**: ~300/818 stories (~37%). Los dominios excluidos requieren sistemas externos (ClaveÚnica, PISEE, SIGFE, CGR, GIS) o módulos no planificados (RRHH, participación ciudadana).

---

## 2. Contexto Organizacional

### 2.1 Estructura GORE Ñuble

GORE Ñuble opera con una jerarquía de 3 niveles bajo el Gobernador Regional:

```
GOBERNADOR REGIONAL
├── ADMINISTRADOR REGIONAL
│   ├── DIPLADE  — Planificación y Desarrollo Regional
│   ├── DIPIR   — Presupuesto e Inversión Regional
│   ├── DIDESO  — Desarrollo Social y Humano
│   ├── DIFOI   — Fomento e Industria
│   ├── DIT     — Infraestructura y Transportes
│   └── DAF     — Administración y Finanzas
│       ├── Depto. Presupuesto
│       ├── Depto. Finanzas
│       ├── UCR (Unidad)
│       └── Tesorería (Unidad)
├── Staff: DGI, Jurídico, Auditoría, Control, Comunicaciones, Gabinete
├── Órganos: COSOC, Comité CTCI, CDR
└── CONSEJO REGIONAL (16 consejeros electos)
    └── Secretaría Ejecutiva
```

**Reconciliaciones canónicas** (SSOT):
- DIT (no DIINF) — per OrgData.ttl `skos:altLabel`
- DIDESO (no DIDECO) — canon orgánico
- DGI es StaffUnit (no División), depende del Administrador Regional
- RS = "Recomendación Satisfactoria" (no "Rentabilidad Social")
- F0: SSOT canónico = "Postulación"; GORE_OS UI = "Formulación" (reconciliación intencional — el UI enfatiza la actividad del ANALISTA)
- F4: SSOT canónico = "Formalización"; GORE_OS agrupa "Formalización y Ejecución" (el status bifurca: PROYECTO→licitación→obra; PROGRAMA→formalizado→ejecución)

### 2.2 Poblaciones del Sistema

GORE_OS sirve a dos poblaciones sobre PostgreSQL compartido:

| Población | Roles | Dominio |
|-----------|-------|---------|
| **Operativa** | GOBERNADOR, ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, JEFE_DEPARTAMENTO, JEFE_UNIDAD, ENCARGADO, ANALISTA, RTF, ASESOR_JURIDICO, CONSEJERO_REGIONAL, SECRETARIO_EJECUTIVO | IPR, compromisos, problemas, alertas, presupuesto, convenios, actos |
| **DGI** | JEFE_DGI, ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD | Indicadores, procesos, iniciativas, reportes, cartera, coordinación |

Login único → detección de rol → routing a sidebar/dashboard apropiado.

---

## 3. Roles del Sistema

### 3.1 Tabla de Roles

| # | Código | Nombre | Población | Arquetipo | División típica |
|---|--------|--------|-----------|-----------|----------------|
| 0 | GOBERNADOR | Gobernador Regional | Operativa | Firmante + Estratega | — |
| 1 | ADMIN_SISTEMA | Administrador del Sistema | Operativa | Configurador + Estratega | — |
| 2 | ADMIN_REGIONAL | Administrador Regional | Operativa | Estratega + Firmante | — |
| 3 | JEFE_DIVISION | Jefe de División | Operativa | Supervisor | Su división |
| 4 | ENCARGADO | Encargado operativo | Operativa | Ejecutor | Su división |
| 5 | JEFE_DGI | Jefe DGI | DGI | Coordinador DGI | DGI |
| 6 | ESP_CONTROL_GESTION | Especialista Control de Gestión | DGI | Especialista DGI | DGI |
| 7 | ESP_PROCESOS | Especialista Procesos | DGI | Especialista DGI | DGI |
| 8 | ESP_TD | Especialista Transformación Digital | DGI | Especialista DGI | DGI |
| 9 | CONSEJERO_REGIONAL | Consejero Regional | Operativa | Gobernanza CORE | — |
| 10 | SECRETARIO_EJECUTIVO | Secretario Ejecutivo CORE | Operativa | Gobernanza CORE | — |
| 11 | JEFE_DEPARTAMENTO | Jefe de Departamento | Operativa | Supervisor | Su división |
| 12 | JEFE_UNIDAD | Jefe de Unidad | Operativa | Supervisor | Su división |
| 13 | ANALISTA | Analista de inversiones | Operativa | Ejecutor | Su división |
| 14 | RTF | Revisor Técnico Financiero | Operativa | Ejecutor | DAF |
| 15 | ASESOR_JURIDICO | Asesor Jurídico | Operativa | Ejecutor | — |

### 3.2 Permisos por Contexto

| Acción | Roles permitidos |
|--------|------------------|
| Crear compromisos | ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, JEFE_DEPARTAMENTO, ANALISTA, ENCARGADO |
| Verificar compromisos | JEFE_DIVISION (su división), ADMIN_REGIONAL, ADMIN_SISTEMA |
| Crear IPR | ADMIN_SISTEMA, ADMIN_REGIONAL, GOBERNADOR, ANALISTA |
| Firmar actos (VISADO→FIRMADO) | GOBERNADOR, ADMIN_REGIONAL, ADMIN_SISTEMA |
| V.B. jurídico | ASESOR_JURIDICO |
| Revisar rendiciones | RTF |
| Votar en CORE | CONSEJERO_REGIONAL |
| Gestionar sesiones CORE | ADMIN_SISTEMA, ADMIN_REGIONAL, GOBERNADOR, SECRETARIO_EJECUTIVO |
| CRUD DGI | JEFE_DGI, ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD |
| Admin sistema (usuarios, umbrales) | ADMIN_SISTEMA |

---

## 4. Arquetipos de Usuario

### 4.1 Ejecutor — "¿Qué tengo que hacer hoy?"

**Roles**: ENCARGADO, ANALISTA, RTF, ASESOR_JURIDICO
**Frecuencia**: Diaria
**Necesidad central**: Bandeja de trabajo clara, plazos visibles, acciones de 1 clic
**Métrica de éxito**: < 10 segundos desde login hasta primera acción

**Sub-perfiles**:

| Sub-perfil | Campo de acción | Presión temporal |
|------------|----------------|------------------|
| ENCARGADO | Compromisos y alertas sobre sus IPRs | Alta — plazos diarios |
| ANALISTA | Formulación IPR F0–F3, satélites | Media — ciclos semanales |
| RTF | Revisión rendiciones EN_REVISION_RTF | Alta — SLA 7 días |
| ASESOR_JURIDICO | V.B. legalidad actos y convenios | Media — cola de revisión |

**Dolores**: No saber qué está pendiente. Buscar información que debería ser visible. Pasos innecesarios.

**Implementación GORE_OS**:
- Dashboard: `ModuleMyWork` (ENCARGADO) — task list agrupada por IPR, urgentes auto-expandidos
- Dashboard: `ModuleFormulacion` (ANALISTA) — pipeline F0→F2 con checklists por fase
- Dashboard: `ModuleMyProgress` (RTF, ASESOR_JURIDICO) — barra de progreso + items
- `/compromisos`: `CompromisosWorkView` — vista de trabajo sin filtros, items propios por diseño
- `/actos`: `PendingQueue` EN_REVISION para ASESOR_JURIDICO

### 4.2 Supervisor — "¿Cómo está mi equipo/división?"

**Roles**: JEFE_DIVISION, JEFE_DEPARTAMENTO, JEFE_UNIDAD
**Frecuencia**: Diaria (check rápido), semanal (revisión profunda)
**Necesidad central**: Vista agregada de división, salud de un vistazo, no navegar IPR por IPR

**Acciones clave**: Monitorear dashboard, delegar, aprobar actos, escalar.

**Dolores**: Navegar a cada IPR para entender estado. Sin visibilidad de carga del equipo.

**Implementación GORE_OS**:
- Dashboard: `ModuleMyTeam` — avatares, barras de carga, drill-down por persona
- `/compromisos`: `CompromisosTeamView` — KPIs + equipo expandible + "Verificar" inline
- `/ipr`: Auto-scope a su división via `router.replace`, strip contextual "{N} IPRs en tu división"
- `/ipr/cartera`: Portfolio con señales de salud ROJO/AMARILLO/VERDE

### 4.3 Estratega — "¿Cómo está la institución?"

**Roles**: ADMIN_REGIONAL, GOBERNADOR, ADMIN_SISTEMA
**Frecuencia**: Diaria (AR), semanal (GOB)
**Necesidad central**: KPIs institucionales, semáforos, solo alertas críticas

**Implementación GORE_OS**:
- Dashboard: Centro de Mando unificado — action-items, AttentionStrip, KPI strip
- `/centro-de-mando`: 6 KPIs paralelos + timeline
- `/actos`: `PendingQueue` VISADO — cola de firma con stepper visual

### 4.4 Especialista DGI — "¿Qué indicadores/procesos necesitan atención?"

**Roles**: ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD
**Frecuencia**: Variable (dashboards diarios a revisiones mensuales)
**Necesidad central**: Observación paralela sin control, medición + mejora

**Sub-perfiles**:

| Sub-perfil | Foco | Herramientas |
|------------|------|-------------|
| ESP_CONTROL_GESTION | Indicadores, cartera IPR, rendiciones | Cockpit CG, filtros dimensión, SLA dashboard |
| ESP_PROCESOS | Catálogo procesos, BPMN, oportunidades mejora | Catálogo 6-state, DMAIC, dolor→oportunidad→iniciativa |
| ESP_TD | Cuellos de botella, métricas Lean, TDE | Detección automática, 3 queries, Ley 21.180 plazos |

**Principio clave (P5)**: DGI observa, no controla. No tiene FKs directos a IPRs.

### 4.5 Coordinador DGI — "¿Qué decisiones/escalamientos están pendientes?"

**Rol**: JEFE_DGI
**Frecuencia**: Diaria (standups), semanal (coordinación AR)
**Necesidad central**: Coordinación de equipo, puente entre operaciones y gobernanza

**Ritmo semanal**:
| Día | Actividad | Página |
|-----|-----------|--------|
| Lunes | Standups equipo | `/tablero` (Kanban) |
| Martes | Sync con AR | `/coordinacion` |
| Miércoles | Checkpoints DMAIC | `/procesos/progreso` |
| Jueves | 1-on-1s | `/ipr/cartera` |
| Viernes | Reporte AR | `/informes` |

### 4.6 Firmante — "¿Qué necesita mi firma hoy?"

**Roles**: GOBERNADOR, ADMIN_REGIONAL
**Frecuencia**: 2–3 sesiones/semana
**Necesidad central**: Cola de documentos pendientes de firma, contexto suficiente para decidir

**Implementación GORE_OS**:
- Dashboard: AttentionStrip con items pendientes de firma (categoría FIRMA)
- `/actos`: `PendingQueue` VISADO — actos listos para firmar, con stepper visual
- Drawer de detalle: muestra V.B. previos + contexto completo para decidir

### 4.7 Gobernanza CORE — "¿Qué voto?" / "¿Está lista la sesión?"

**Roles**: CONSEJERO_REGIONAL, SECRETARIO_EJECUTIVO
**Frecuencia**: 2–4 sesiones/mes
**Quorum**: Simple 9/16, Calificada 11/16

| Actor | Necesidad |
|-------|-----------|
| CONSEJERO | Votar informado (antecedentes previos), revisar acuerdos, fiscalizar |
| SECRETARIO | Sesión preparada, temas listos, consejeros notificados |

**Implementación GORE_OS**:
- `/core-sessions`: Card "Próxima sesión" con fecha + temas + quorum
- Guía de preparación para SECRETARIO cuando agenda vacía
- Votación en tiempo real con conteo y resultado (APROBADO/RECHAZADO/PENDIENTE)
- Gate F3→F4: IPRs > 7.000 UTM requieren aprobación CORE

### 4.8 Configurador — "¿Qué necesita mantenimiento?"

**Rol**: ADMIN_SISTEMA
**Frecuencia**: 5–15 creaciones usuario/mes, ajustes mensuales de umbrales
**Necesidad central**: CRUD usuarios, divisiones, umbrales; trazabilidad de cambios

**Módulos**: `/admin/usuarios`, `/admin/divisiones`, `/admin/financing-tracks`, `/admin/thresholds`, `/admin/sni-levels`, `/admin/budget-program-codes`, `/admin/admissibility-items`

---

## 5. Journeys de Usuario

### 5.1 Journeys del Ejecutor

#### J1: "Mi día de trabajo" (ENCARGADO)

```
Login → Centro de Comando
  → AttentionStrip (items urgentes)
  → ModuleMyWork (task list agrupada por IPR)
    → Click item → /ipr/{id}?tab=compromisos
    → Actualizar progreso → Completar
    → Volver al dashboard
```

**Página `/compromisos`** (journey-first):
- ENCARGADO ve `CompromisosWorkView`: sus items agrupados por IPR, sin toggle "solo míos"
- Grupos urgentes auto-expandidos, no-urgentes colapsados
- Acción "Completar" inline (botón ✓) sin abrir drawer
- Click en item → drawer con detalle completo + historial

**Fuente de datos**: Backend auto-scopa `responsible_id = user.id` para ENCARGADO.

**Stories**: D-EJEC | **Procesos**: PROC-EJEC-P2

#### J2: "Formular IPR" (ANALISTA)

```
/ipr/nuevo → Tipo + Mecanismo
  → Post-create redirect → /ipr/{id}?tab=partes
  → Completar satélites F0 (partes, territorio, hitos)
  → TransitionPanel muestra gates
  → Avanzar a F1 → Registrar admisibilidad
  → Avanzar a F2 → Registrar evaluación
```

**Dashboard**: `ModuleFormulacion` — pipeline F0→F2 con checklists por fase.
**Endpoint**: `GET /api/ipr/mis-formulaciones` retorna IPRs asignadas con `suggested_action` + `suggested_tab`.

**Nota reconciliación F0**: SSOT canónico = "Postulación"; GORE_OS UI = "Formulación". El ANALISTA formula la IPR con satélites (partes, territorio, hitos) antes de enviar a evaluación según track (ver tabla Track Routing en §5.10).

**Stories**: D-FIN-IPR_CORE | **Procesos**: PROC-FIN-IPR_CORE-P1 (ingreso), P2 (admisibilidad), P3 (evaluación)

#### J3: "Revisar rendición" (RTF)

```
Login → /datos?tab=rendiciones (auto-filtrado EN_REVISION_RTF)
  → Click rendición → Revisar detalles
  → Decisión: VISAR (→VISADA_RTF) o OBSERVAR (→OBSERVADA)
```

**SLA**: 7 días hábiles. Columna SLA muestra progreso; resaltado para >80% SLA consumido.

**Cadena de rendición completa** (PROC-FIN-REND-P1, 8 estados GORE_OS):

```
Ejecutor (EE)          RTF (GORE)           UCR (GORE)         Jefe DAF
    │                      │                    │                  │
    ├─ Presenta ──────► PENDIENTE               │                  │
    │                      │                    │                  │
    │                 EN_REVISION_RTF ◄── Asigna ┤                  │
    │                   (7d SLA)                │                  │
    │                      │                    │                  │
    │                      ├─ Visar ──► VISADA_RTF                 │
    │                      │              │                        │
    │                      │         EN_REVISION_UCR               │
    │                      │              │                        │
    │                      │              ├─ Aprobar ──► APROBADA ─┤─► Firma FEA
    │                      │              └─ Rechazar ─► RECHAZADA │
    │                      │                                       │
    │                      └─ Observar ─► OBSERVADA                │
    │                                       │                      │
    └──── Subsana (15d) ────────────────────┘                      │
```

**Roles SISREC**: Analista Ejecutor (crea), Ministro de Fe (certifica), Encargado Ejecutor (firma FEA, envía), Analista Otorgante/RTF (revisa), Encargado Otorgante/Jefe DAF (aprueba FEA).

**Stories**: D-FIN-EJECUTORES, D-FIN-IPR_CORE | **Procesos**: PROC-FIN-REND-P1

#### J4: "Visación jurídica" (ASESOR_JURIDICO)

```
Centro de Mando → ModuleJuridico (pending V.B.)
  → Click → /actos/{id} o /convenios/{id}
  → Decisión: VISAR o DEVOLVER
```

**Página `/actos`**: `PendingQueue` EN_REVISION arriba del DataTable.
**Página `/convenios`**: Auto-filtro a EN_REVISION_JURIDICA.

**Stories**: D-NORM | **Procesos**: PROC-NORM-P1, PROC-NORM-P2

### 5.2 Journeys del Supervisor

#### J5: "Estado de mi división" (JEFE_DIVISION)

```
Centro de Comando → ModuleMyTeam (avatares, carga)
  → /compromisos → CompromisosTeamView (KPIs + equipo expandible)
    → Expandir persona → Ver sus compromisos
    → "Verificar" inline para items COMPLETADO
  → /ipr (auto-scope a mi división)
    → Strip: "45 IPRs en tu división"
    → Filtros colapsables (avanzados tras "Más filtros")
  → /ipr/cartera → Portfolio con semáforo salud
```

**Auto-scope**: `router.replace` pre-selecciona su división en filtros IPR.

**Stories**: D-EJEC, D-FIN-IPR_CORE | **Procesos**: PROC-EJEC-P3

#### J6: "Crisis / Alerta" (JEFE_DIVISION)

```
Centro de Mando → AttentionStrip alerta CRITICO
  → /ipr/{id}?tab=alertas → Evaluar
  → Crear problema o convocar reunión de crisis
  → /reuniones/nueva → Acuerdos → Auto-convierten en compromisos
```

**Protocolo FÉNIX**: Cuando la desviación supera el 20% en obra, se activa el protocolo de crisis institucional (PROC-FENIX-P1 activación, PROC-FENIX-P2 ejecución). El escalamiento sigue 4 niveles (1×/1.5×/2× SLA) via `/escalamiento`. El Comité de Crisis (`COMITE-CRISIS`) se auto-crea y las decisiones se registran como `dgi_ar_decision` con `source_session_id` vinculando a la sesión de crisis.

**Stories**: D-EJEC, FENIX | **Procesos**: PROC-GOB-P3 (crisis), PROC-FENIX-P1, PROC-FENIX-P2

### 5.3 Journey del Estratega

#### J7: "Panorama institucional" (ADMIN_REGIONAL)

```
Centro de Mando → KPIs (5 dimensiones) + AttentionStrip escalamientos
  → /centro-de-mando (6 KPIs + timeline)
  → /escalamiento/{id} para decidir
  → /actos → PendingQueue VISADO para firmar
```

**Contexto**: El ciclo ARI/PROPIR (Mayo–Septiembre) determina la cartera priorizada anualmente (PROC-PLAN-P2).

**Stories**: D-PLAN, D-FIN-IPR_CORE, D-GOB | **Procesos**: PROC-PLAN-P2, PROC-GOB-P4

### 5.4 Journeys Especialista DGI

#### J8: "Monitoreo diario" (ESP_CONTROL_GESTION)

```
Centro de Comando → /datos?tab=indicadores (solo VIGENTE)
  → Filtrar por dimensión → Drill-down en indicadores ROJO
  → /datos?tab=rendiciones para SLA breaches
  → /informes para documentar en reporte semanal
```

#### J9: "Mejora de procesos" (ESP_PROCESOS)

```
/procesos (catálogo) → /procesos/{id} (FSM 6 estados)
  → Levantar proceso: Actores, Reglas, Métricas, Dolores
  → Tab Oportunidades → Puente a iniciativa DMAIC
  → /tablero Kanban (WIP: EN_CURSO:5, REVISION:2)
  → /tablero/{id} DMAIC stepper (DEFINE→MEASURE→ANALYZE→IMPROVE→VERIFY)
```

**Stories**: D-GESTION | **Procesos**: PROC-GESTION-P1, PROC-GESTION-P3

### 5.5 Journey Coordinador DGI

#### J10: "Coordinación semanal" (JEFE_DGI)

Ritmo semanal descrito en sección 4.5. El Coordinador es el único rol que usa TODAS las páginas DGI en un ciclo regular.

**Stories**: D-GESTION, D-GOB | **Procesos**: PROC-GOB-P4, PROC-GESTION-P2

### 5.6 Journeys del Firmante

#### J11: "Cola de firma" (GOBERNADOR)

```
Centro de Mando → AttentionStrip "pendientes de firma"
  → /actos → PendingQueue VISADO (stepper visual por acto)
  → Click → Drawer con V.B. previos + contexto
  → "Cambiar Estado" → Seleccionar FIRMADO → Confirmar
  → Siguiente en cola
```

**Stories**: D-NORM | **Procesos**: PROC-NORM-P1

#### J12: "Presidir CORE" (GOBERNADOR)

```
Pre-sesión: /core-sessions/{id} → Card con agenda + quorum
Sesión: "Iniciar Sesión" → EN_CURSO
  → Tema por tema: votación en tiempo real
  → Quorum simple (9/16) o calificada (11/16)
"Finalizar Sesión" → Acuerdos registrados
  → IPRs aprobados avanzan F3→F4 automáticamente
```

**Stories**: D-GOB | **Procesos**: PROC-GOB-P1, PROC-GOB-P2

### 5.7 Journeys de Gobernanza CORE

#### J13: "Votar en CORE" (CONSEJERO_REGIONAL)

```
/core-sessions → Card "Próxima sesión" (fecha, temas, quorum)
  → Click → /core-sessions/{id}
  → Sesión EN_CURSO → TopicCard + botones de votación
  → Conteo en tiempo real → Ver resultado
```

#### J14: "Preparar CORE" (SECRETARIO_EJECUTIVO)

```
/core-sessions/nueva → Crear sesión + tabla de temas
  → Definir quorum por tema (SIMPLE o CALIFICADA)
  → Notificar consejeros
  → Día de sesión: Iniciar → gestionar temas → Finalizar + acta
```

**Página `/core-sessions`**: Guía "Preparar agenda" cuando sesión PROGRAMADA sin temas.

**Stories (J13+J14)**: D-GOB | **Procesos**: PROC-GOB-P1

### 5.8 Journey Supervisor Financiero

#### J15: "Aprobar CDPs y rendiciones" (JEFE_DEPARTAMENTO)

```
Centro de Mando → ModuleMyTeam
  → /datos?tab=rendiciones&state=VISADA_RTF → Aprobar/rechazar
  → /presupuesto para emisión CDP
  → /convenios/{id} cuotas (Art. 18: verificar rendiciones previas)
```

**Stories**: D-FIN-IPR_CORE, D-FIN-EJECUTORES | **Procesos**: PROC-FIN-IPR_CORE-P4, PROC-FIN-REND-P1

### 5.9 Journey del Configurador

#### J16: "Día de mantenimiento" (ADMIN_SISTEMA)

```
/admin/usuarios → Crear/editar usuario + rol + división
  → /admin/divisiones (nueva división)
  → /admin/umbrales (ajustar política)
  → /admin/niveles-sni (niveles SNI)
```

**Stories**: D-OPS | **Procesos**: PROC-OPS-P1

### 5.10 Journey Transversal: Ciclo IPR 360°

**La IPR es la protagonista, no el rol.** El sistema debe responder: "Esta IPR, ¿en qué fase está y QUIÉN debe actuar ahora?"

#### Cadena de handoff por fase

| Fase | Actor principal | Gate keeper | Siguiente |
|------|----------------|-------------|-----------|
| F0 Formulación* | ANALISTA | JEFE_DIVISION | ANALISTA/evaluador |
| F1 Admisibilidad | ANALISTA verifica | JEFE_DIVISION aprueba | Evaluador externo |
| F2 Evaluación | Externo (MDSF, GORE, ANID) | ANALISTA registra | JEFE + JEFE_FINANZAS |
| F3 Priorización | JEFE_FINANZAS (CDP) | GOBERNADOR + CORE (>7K UTM) | ASESOR_JURIDICO + GOBERNADOR |
| F4 Formalización y Ejecución | ENCARGADO ejecuta | ITO/ITP supervisa | RTF (rendición) |
| F5 Cierre | RTF revisa | JEFE_DAF firma | UCR contabiliza |

*\*F0: SSOT canónico = "Postulación"; GORE_OS UI = "Formulación" (ver reconciliación en §2.1).*

**Matriz de participación**: 17 roles × 6 fases con acciones definidas por fase.

#### Track Routing (F2 Evaluación)

El mecanismo de financiamiento determina quién evalúa y qué dictamen emite. El ANALISTA registra el resultado; el sistema valida que el dictamen coincida con el track.

| Track | Mecanismo | Evaluador | Dictamen |
|-------|-----------|-----------|----------|
| A — SNI General | SNI | MDSF | RS (Recomendación Satisfactoria) |
| B — Circular 33 | C33 | MDSF/GORE | AD (Admisibilidad) |
| C — FRIL | FRIL | GORE (DIPIR) | AT (Aprobación Técnica) |
| D1 — Glosa 06 | Glosa 06 | DIPRES/SES | RF (Recomendación Favorable) |
| D2 — Transferencias | Transfer | GORE (Comité/DAE) | ITF (Informe Técnico Favorable) |
| E1 — Subvención 8% | Subv8 | GORE (Comisión) | Puntaje/Ranking |
| E2 — FRPD (Royalty) | FRPD | ANID/CORFO/GORE | Elegibilidad + RS/RF |

*Fuente: `ssot-ipr-lifecycle`, 10 códigos de resultado de evaluación.*

#### Cadena de Acto Administrativo (7 pasos)

Todo acto administrativo (decreto, resolución, oficio) sigue esta cadena antes de producir efectos jurídicos:

```
Requirente           Jurídico      Control     Jefatura    Admin Regional   Gobernador    CGR
    │                    │            │           │              │               │          │
    ├─ BORRADOR ───► EN_REVISION     │           │              │               │          │
    │                (V.B. legal)    │           │              │               │          │
    │                    ├──────► (V.B. ctrl)   │              │               │          │
    │                    │            ├────► (V.B. jefe)       │               │          │
    │                    │            │           ├─────► VISADO              │          │
    │                    │            │           │        (V.B. AR)          │          │
    │                    │            │           │              ├──────► FIRMADO (FEA)  │
    │                    │            │           │              │               ├────► TOMADO_RAZON
    │                    │            │           │              │               │     (o OBSERVADO)
    │                    │            │           │              │               │          │
    └────────────────────┴────────────┴───────────┴──────────────┴───────────────┴──────────┘
                                                                                 ANULADO (cross-cutting)
```

**Gate jurídico**: Ningún acto avanza sin V.B. de ASESOR_JURIDICO (patrón transversal #9).
**Exención TdR**: Resoluciones < 2.500 UTM están exentas de Toma de Razón CGR (Res. 7/2019).

*Fuente: `ssot-actos-admin`, 8 etapas ontológicas → 7 estados GORE_OS. Procesos: PROC-NORM-P1.*

#### SLAs Documentados

| Proceso | SLA | Responsable | Fuente |
|---------|-----|-------------|--------|
| Revisión RTF rendiciones | 7 días hábiles | Analista Otorgante (RTF) | PROC-FIN-REND-P1 |
| Devolución por observación | 1 día hábil | Jefe DAF | PROC-FIN-REND-P1 |
| Contabilización rendición | 2 días hábiles | UCR/DAF | PROC-FIN-REND-P1 |
| Resubsanación rendición observada | 15 días hábiles | Entidad Ejecutora | PROC-FIN-REND-P1 |
| Meta CGR rendición total | 14 días totales | — | CGR |
| Resoluciones exentas | 15 días hábiles | Cadena acto | PROC-NORM-P1 |
| Convenios (revisión jurídica) | 30 días hábiles | ASESOR_JURIDICO | PROC-NORM-P2 |
| Ciclo ARI/PROPIR | Mayo–Septiembre anual | DIPLADE | PROC-PLAN-P2 |
| Escalamiento nivel 1 | 1× SLA base | Responsable directo | PROC-GESTION-P2 |
| Escalamiento nivel 2 | 1.5× SLA base | JEFE_DIVISION | PROC-GESTION-P2 |
| Escalamiento nivel 3 | 2× SLA base | ADMIN_REGIONAL | PROC-GESTION-P2 |

#### Handoffs Inter-dominio

Las IPRs cruzan múltiples dominios durante su ciclo de vida. Los handoffs clave no documentados en journeys individuales:

| Origen | Destino | Trigger | Journey afectado |
|--------|---------|---------|-----------------|
| D-GESTION → FENIX | Crisis por desviación >20% | Alerta CRITICO + umbral | J6 |
| D-PLAN → D-FIN-IPR_CORE | Ciclo ARI/PROPIR prioriza cartera | Mayo cada año | J7 (Estratega) |
| D-EJEC → D-NORM | Convenio requiere acto administrativo | Gate F4 | J2, J4, J11 |
| D-FIN-IPR_CORE → D-FIN-EJECUTORES | Cuota pagada → rendición pendiente | Art. 18 | J3, J15 |
| D-TDE → todos | Ley 21.180 digitalización → FEA obligatoria | Transversal | J11 |
| D-TERR → D-PLAN | Datos territoriales informan ERD | Anual | — (sin sistema) |

#### Trazabilidad Journeys ↔ Stories ↔ Procesos

| Journey | Dominios Stories | Procesos Relacionados |
|---------|-----------------|----------------------|
| J1 ENCARGADO día | D-EJEC | PROC-EJEC-P2 (ejecución), PROC-EJEC-P3 (supervisión) |
| J2 Formular IPR | D-FIN-IPR_CORE | PROC-FIN-IPR_CORE-P1 (ingreso), P2 (admisibilidad), P3 (evaluación) |
| J3 Revisar rendición | D-FIN-EJECUTORES, D-FIN-IPR_CORE | PROC-FIN-REND-P1 |
| J4 Visación jurídica | D-NORM | PROC-NORM-P1 (resoluciones), PROC-NORM-P2 (convenios) |
| J5 Estado división | D-EJEC, D-FIN-IPR_CORE | PROC-EJEC-P3 (supervisión) |
| J6 Crisis | D-EJEC, FENIX | PROC-GOB-P3 (crisis), PROC-FENIX-P1, P2 |
| J7 Panorama institucional | D-PLAN, D-FIN-IPR_CORE | PROC-PLAN-P2 (ARI/PROPIR), PROC-GOB-P4 (agenda) |
| J8 Monitoreo CG | D-GESTION | PROC-GESTION-P1 (control) |
| J9 Mejora procesos | D-GESTION | PROC-GESTION-P3 (playbooks) |
| J10 Coordinación DGI | D-GESTION, D-GOB | PROC-GOB-P4 (agenda), PROC-GESTION-P2 (riesgos) |
| J11 Cola firma | D-NORM | PROC-NORM-P1 |
| J12 Presidir CORE | D-GOB | PROC-GOB-P1 (CORE), PROC-GOB-P2 (transferencias) |
| J13 Votar CORE | D-GOB | PROC-GOB-P1 |
| J14 Preparar CORE | D-GOB | PROC-GOB-P1 |
| J15 CDPs y rendiciones | D-FIN-IPR_CORE, D-FIN-EJECUTORES | PROC-FIN-IPR_CORE-P4 (priorización), PROC-FIN-REND-P1 |
| J16 Mantenimiento | D-OPS | PROC-OPS-P1 (identidad) |
| IPR 360° (transversal) | D-EJEC, D-FIN-IPR_CORE, D-NORM, D-GOB | PROC-FIN-IPR_CORE-P1→P7 (ciclo completo) |

---

## 6. Principios de Diseño UX

### P1: Inbox-First, No Browse-First

El Ejecutor (80% del uso) NO navega — ejecuta desde una cola. El dashboard es una **bandeja de trabajo**, no un panorama.

**Implementación**: Centro de Comando + AttentionStrip + deep links a tabs específicos. `/compromisos` muestra task list para ENCARGADO, no DataTable genérico.

### P2: Nivel de Agregación = Rol

| Arquetipo | Nivel | Alcance |
|-----------|-------|---------|
| Ejecutor | MIS items | 1 persona |
| Supervisor | MI DIVISIÓN | 8–15 personas |
| Estratega | TODA LA INSTITUCIÓN | 6 divisiones |
| DGI | TRANSVERSAL | Observa sin controlar |

**Implementación**: Auto-scope en páginas de lista. ENCARGADO ve solo sus compromisos. JEFE ve su división. ADMIN ve todo.

### P3: La Transición es el Momento de Verdad

La transición de fase en IPR es el momento crítico. El usuario necesita saber:
1. ¿Puedo avanzar? (gates)
2. ¿Qué pasa si avanzo? (efectos feedforward)
3. ¿Qué me falta? (gates bloqueantes con detalle)

**Implementación**: TransitionPanel es el componente más importante del detalle IPR.

### P4: El Supervisor No Ejecuta — Delega

JEFE_DIVISION no actualiza compromisos, los crea para ENCARGADO. Necesita ESTADO AGREGADO, no detalle granular.

**Implementación**: `CompromisosTeamView` con barras de carga y "Verificar" inline. No drill-down a formularios.

### P5: DGI Observa, No Controla

DGI no tiene FKs directos a IPRs. Observa via métricas, indicadores, reportes. Acciones: medir, analizar, recomendar, escalar.

**Implementación**: Cockpits DGI son dashboards de lectura + herramientas de análisis, no formularios CRUD.

### P6: Frecuencia Determina Prominencia

| Frecuencia | Prominencia |
|-----------|------------|
| Diaria | Primer nivel (dashboard, sidebar, 1 clic) |
| Semanal | Segundo nivel (página dedicada, 2 clics) |
| Mensual | Tercer nivel (sección dentro de página, 3 clics) |
| Eventual | Accesible pero no prominente |

### P7: El Error Más Común es Contexto, No Técnica

El usuario no hace mal clic. Entiende mal **qué debería estar haciendo ahora**. El sistema debe responder "¿qué hago?" antes que "¿cómo lo hago?".

**Implementación**: Priorizar orientación contextual sobre funcionalidad.

### P8: La IPR es la Protagonista, No el Rol

Cada fase muestra quién es el **actor actual** — el rol al que le toca. La visibilidad de "¿a quién le toca?" previene IPRs estancadas.

**Gap G15 (CRITICO)**: Aún no implementado completamente. Las IPRs se estancan sin visibilidad de quién debe actuar.

---

## 7. Implementación: Vistas Journey-First por Página

### 7.1 Dashboard — Centro de Comando

| Rol | Módulo | Contenido |
|-----|--------|-----------|
| ENCARGADO | ModuleMyWork | Task list agrupada por IPR, urgentes expandidos |
| ANALISTA | ModuleFormulacion | Pipeline F0→F2 con checklists por fase |
| RTF, ASESOR_JURIDICO | ModuleMyProgress | Barra de progreso + items pendientes |
| JEFE_DIVISION | ModuleMyTeam | Avatares, barras de carga, drill-down |
| JEFE_DGI | ModuleDgiTeam | Estado equipo DGI |
| GOBERNADOR, AR | Módulos condicionales | KPIs, panorama, firma pendientes |

### 7.2 `/compromisos` — 3 vistas por rol

| Vista | Rol | Comportamiento |
|-------|-----|---------------|
| `CompromisosWorkView` | ENCARGADO | Task list agrupada por IPR. Sin filtros — ES solo míos por diseño. "Completar" inline. |
| `CompromisosTeamView` | JEFE_DIVISION, JEFE_DEPARTAMENTO | KPIs + equipo expandible + "Verificar" inline. |
| `CompromisosListView` | Otros roles | DataTable genérico con filtros. Fix: `?responsible_id=X` drill-down desde dashboard. |

### 7.3 `/actos` — Cola de firma

| Rol | Sección agregada |
|-----|-----------------|
| GOBERNADOR, ADMIN_REGIONAL, ADMIN_SISTEMA | `PendingQueue` VISADO — actos pendientes de firma con stepper visual |
| ASESOR_JURIDICO | `PendingQueue` EN_REVISION — actos pendientes de V.B. |
| Otros | Lista estándar sin cola |

### 7.4 `/ipr` — Contexto por rol

| Cambio | Detalle |
|--------|---------|
| Filtros colapsables | Sector, Mecanismo, Alerta tras "Más filtros". Tipo, Estado, Fase, División siempre visibles. |
| Auto-scope | JEFE_DIVISION aterriza con su división pre-seleccionada (via `router.replace`). |
| Strip contextual | "{N} IPRs en tu división" o "{N} IPRs en portafolio" según rol. |

### 7.5 `/convenios` — Operaciones financieras

| Cambio | Detalle |
|--------|---------|
| Próximos a vencer | Sección arriba del DataTable: convenios VIGENTE con ≤90 días, semáforo rojo/ámbar. |
| Auto-scope | ASESOR_JURIDICO auto-aterriza en `?state=EN_REVISION_JURIDICA`. |

### 7.6 `/core-sessions` — Gobernanza CORE

| Cambio | Detalle |
|--------|---------|
| Card próxima sesión | CONSEJERO, SECRETARIO, GOBERNADOR ven card con fecha + temas + quorum. |
| Guía de preparación | SECRETARIO ve "Preparar agenda" cuando sesión PROGRAMADA sin temas. |

---

## 8. Análisis de Gaps

### 8.1 Gaps Cerrados (10/20)

| Gap | Descripción | Cierre |
|-----|------------|--------|
| G1 | Inbox ejecutor sin plazos | ModuleMyWork con colores temporales (C41) |
| G2 | Sin guía por mecanismo | Resuelto por diseño — gates guían (C44) |
| G3 | RTF sin SLA visible | Columna SLA + resaltado >80% |
| G4 | Sin visibilidad equipo división | ModuleMyTeam avatares + load bars (C41) |
| G5 | Workflow crisis fragmentado | Aceptable — proximidad de tabs mitiga (decisión diseño) |
| G6 | Sin breakdown por división | KPIs con breakdown (C41) |
| G7 | Sin filtro tendencia CG | Filtro trend en indicadores (C43) |
| G8 | Sin estado "al día" | AttentionStrip "Al día" card (C41) |
| G9 | Cola firma sin UI | PendingQueue en `/actos` + action-items FIRMA (C43 + C46) |
| G12 | Sin conteo firma dashboard | action-items categoría FIRMA en AttentionStrip (C43) |

### 8.2 Gaps Abiertos (10/20)

| Gap | Severidad | Descripción | Razón diferimiento |
|-----|-----------|------------|-------------------|
| G10 | MEDIO | Sin antecedentes en notificación CORE | Requiere infraestructura notificaciones (externa) |
| G11 | MEDIO | Sin inbox financiero dedicado | Parcial via action-items rendiciones |
| G13 | MEDIO | Sin notificación consejeros | Requiere sistema email/push (externo) |
| G14 | BAJO | Sin audit trail visible admin | Baja criticidad |
| **G15** | **CRITICO** | **Sin indicador "¿a quién le toca?" en IPR** | **Requiere DDL + UI. Gap más importante abierto.** |
| G16 | MEDIO | Sin tracking evaluación externa | Requiere modelado DDL |
| G17 | BAJO | Sin link IPR→sesión CORE | Trazabilidad gap |
| G18 | MEDIO | Sin herramientas ITO/ITP | Supervisión no en UI |
| G19 | MEDIO | Cadena financiera fragmentada | convenio→cuota→rendición separados |
| G20 | BAJO | Sin workflow guiado ex-post | Evaluación cierre necesita guía |

### 8.3 Categorías de Diferimiento

- **Requiere DDL**: G15, G16, G17, G18, G19, G20
- **Requiere sistemas externos**: G10, G13
- **Baja criticidad**: G14, G17

---

## 9. Patrones de Diseño Recurrentes

| # | Patrón | Descripción |
|---|--------|------------|
| 1 | **Role-Scoped Pre-Filtering** | Todas las listas auto-filtran por scope del usuario. Sin "ver todo, luego filtrar". |
| 2 | **Deep Links a Tabs Específicos** | Cada action-item routea a `/ipr/{id}?tab=compromisos`, etc. 1 clic al punto de trabajo. |
| 3 | **Agregación Escalonada** | Dashboard: KPIs rápidos → Lista: filas detalladas → Detalle: contexto completo. |
| 4 | **Estado Declarativo sobre Pasos** | Gates declaran qué falta. El usuario provee datos faltantes, no sigue un procedimiento. |
| 5 | **Módulo Condicional por Rol** | Dashboard no muestra "un dashboard". Muestra módulo específico al rol. |
| 6 | **Sidebar para Multi-Tab** | 17 tabs IPR usan sidebar vertical agrupado. Always visible. Mobile: `<Select>`. |
| 7 | **Cola Contextual Pre-Tabla** | Roles firmantes/revisores ven cola de pendientes SOBRE el DataTable. |
| 8 | **Auto-Scope con router.replace** | JEFE aterriza con filtro de su división. Ref guard previene re-aplicación tras clear. |
| 9 | **Gate Jurídico Obligatorio** | Ningún documento con efectos jurídicos avanza sin V.B. de ASESOR_JURIDICO. Aplica a actos administrativos (BORRADOR→EN_REVISION), convenios (→EN_REVISION_JURIDICA), y resoluciones. Implementación: `PendingQueue` EN_REVISION en `/actos`, auto-filtro en `/convenios`. Procesos: PROC-NORM-P1, PROC-NORM-P2, PROC-EJEC-P1, PROC-FIN-IPR_CORE-P4. |

---

## 10. Usuarios de Test

Todos con password `admin123`, dominio `@goreos.cl`.

| Email | Rol | Arquetipo | División |
|-------|-----|-----------|----------|
| admin | ADMIN_SISTEMA | Configurador | — |
| regional | ADMIN_REGIONAL | Estratega | — |
| gobernador | GOBERNADOR | Firmante + Estratega | — |
| secretario.core | SECRETARIO_EJECUTIVO | Gobernanza CORE | — |
| consejero1, consejero2 | CONSEJERO_REGIONAL | Gobernanza CORE | — |
| jefe.daf | JEFE_DIVISION | Supervisor | DAF |
| jefe.dipir | JEFE_DIVISION | Supervisor | DIPIR |
| jefe.diplade | JEFE_DIVISION | Supervisor | DIPLADE |
| encargado.daf | ENCARGADO | Ejecutor | DAF |
| analista.dipir | ANALISTA | Ejecutor | DIPIR |
| rtf.daf | RTF | Ejecutor | DAF |
| juridico | ASESOR_JURIDICO | Ejecutor | — |
| jefe.dgi | JEFE_DGI | Coordinador DGI | DGI |
| control.gestion | ESP_CONTROL_GESTION | Especialista DGI | DGI |
| procesos | ESP_PROCESOS | Especialista DGI | DGI |
| td | ESP_TD | Especialista DGI | DGI |

---

## 11. Verificación por Rol

Para validar el journey-first redesign:

| Test | Usuario | Verificar |
|------|---------|-----------|
| ENCARGADO ve task list | encargado.daf | `/compromisos` → CompromisosWorkView, agrupado por IPR, sin toggle manual |
| JEFE ve equipo | jefe.daf | `/compromisos` → CompromisosTeamView, KPIs + personas expandibles |
| Admin ve lista completa | admin | `/compromisos` → DataTable genérico sin cambio |
| GOBERNADOR ve cola firma | gobernador | `/actos` → PendingQueue VISADO arriba |
| ASESOR_JURIDICO ve cola V.B. | juridico | `/actos` → PendingQueue EN_REVISION + `/convenios` auto-filtro EN_REVISION_JURIDICA |
| JEFE auto-scope IPR | jefe.daf | `/ipr` → División pre-seleccionada, strip "{N} IPRs en tu división" |
| Convenios próximos a vencer | admin | `/convenios` → Sección amarilla "Próximos a vencer" si hay VIGENTE ≤90d |
| CONSEJERO ve próxima sesión | consejero1 | `/core-sessions` → Card con fecha + temas + quorum |
| Deep links funcionan | jefe.daf | Dashboard MyTeam drill-down → `/compromisos?responsible_id=X` muestra filtrado |

---

## 12. Referencias

| Documento | Ubicación |
|-----------|----------|
| SSOT Bundle v1.5.0 (15 artefactos) | `/Users/felixsanhueza/Developer/kora/KNOWLEDGE/gn/ssot/` |
| Omega v3.0.0 | `architecture/Omega_GORE_OS_Definition_v3.0.0.md` |
| User Stories (818, 16 dominios) | `model/stories/_index.yml` |
| Procesos (81, 15 dominios) | `model/processes/_index.yml` |
| DGI User Stories v1.0 | `docs/DGI_USER_STORIES_v1.0.md` |
| Ejecutor Journey-First Spec | `docs/superpowers/specs/2026-03-15-ejecutor-journey-first-design.md` |
| Visual Refresh Spec | `docs/superpowers/specs/2026-03-12-visual-refresh-capas-progresivas-design.md` |
| IPR Detail Redesign Spec | `docs/superpowers/specs/2026-03-15-ipr-detail-redesign-design.md` |
| Glosario dominio (244 términos) | `model/GLOSARIO.yml` |
| CLAUDE.md (convenciones técnicas) | `CLAUDE.md` |
