# GORE_OS — Cobertura de User Stories DGI v1.0

> **Relación**: Este documento es un snapshot de cobertura (C60) del catálogo de 185 historias DGI. Para el detalle completo de cada historia (descripción, prioridad, fuente), ver [DGI_USER_STORIES_v1.0.md](DGI_USER_STORIES_v1.0.md) (C58).

> **Snapshot C60 (parcialmente desactualizado).** Varias páginas DGI marcadas 'NUEVO/no construido' (cuellos-de-botella, escalamiento, servicios, calendario, coordinación) YA EXISTEN — la cobertura efectiva es mayor que la aquí reportada. Residual válido: /stakeholders, /nps, /plan-trabajo siguen sin construir.

Fecha: 2026-03-22 | Sesion: C60

## Resumen

| Dominio | Total | IMPL | PARCIAL | NUEVO | EXTERNO |
|---------|:-----:|:----:|:-------:|:-----:|:-------:|
| D-DGI-CG — Control de Gestion | 38 | 12 | 8 | 16 | 2 |
| D-DGI-MP — Modernizacion Procesos | 32 | 2 | 3 | 27 | 0 |
| D-DGI-TD — Transformacion Digital | 35 | 3 | 5 | 20 | 7 |
| D-DGI-KC — Gestion Conocimiento | 28 | 0 | 2 | 26 | 0 |
| D-DGI-CI — Coordinacion Institucional | 22 | 3 | 4 | 15 | 0 |
| D-DGI-POT — Potenciamiento | 30 | 4 | 3 | 23 | 0 |
| **TOTAL** | **185** | **24** | **25** | **127** | **9** |

**Cobertura efectiva**: 24 implementadas + 25 parciales = **49/185 (26.5%)**

### Por Rol

| Rol | Total | IMPL | PARCIAL | NUEVO | EXTERNO |
|-----|:-----:|:----:|:-------:|:-----:|:-------:|
| ESP_CONTROL_GESTION | 32 | 10 | 7 | 13 | 2 |
| ESP_PROCESOS | 40 | 4 | 4 | 32 | 0 |
| ESP_TD | 48 | 1 | 6 | 34 | 7 |
| JEFE_DGI | 52 | 8 | 5 | 39 | 0 |
| ADMIN_REGIONAL | 4 | 1 | 1 | 1 | 1 |
| JEFE_DIVISION | 5 | 0 | 1 | 4 | 0 |
| Cross-role (varios) | 4 | 0 | 1 | 3 | 0 |

---

## Stories por Rol

### JEFE_DGI

| Story ID | Descripcion | Estado | P | Paginas involucradas |
|----------|------------|:------:|:-:|---------------------|
| D-DGI-CG-006 | Aprobar creacion/modificacion de indicadores | NUEVO | P2 | /datos (nuevo workflow) |
| D-DGI-CG-015 | Ver estado del equipo DGI (ultima actividad) | IMPL | — | /dashboard (cockpit) |
| D-DGI-CG-023 | Resumen cuellos de botella activos | NUEVO | P2 | /cuellos-de-botella |
| D-DGI-CG-026 | Revisar y aprobar informes antes de enviar | IMPL | — | /informes/[id] |
| D-DGI-CG-030 | Exportar informe como PDF institucional | NUEVO | P2 | /informes/[id] (nuevo boton) |
| D-DGI-CG-035 | Panel productividad DGI (productos por tipo) | NUEVO | P2 | /dashboard (nueva seccion) |
| D-DGI-CG-038 | Items de decision pendientes con acciones | IMPL | — | /dashboard (cockpit) |
| D-DGI-MP-010 | Procesos levantados vs identificados por division | NUEVO | P2 | /procesos/progreso |
| D-DGI-MP-028 | Resumen proyectos DMAIC por fase con tiempos | NUEVO | P2 | /procesos/progreso |
| D-DGI-TD-007 | Reportar avance TDE al Comite TD | NUEVO | P1 | /comite-td (nueva seccion) |
| D-DGI-KC-008 | Panel estado KB (vigentes, en revision) | PARCIAL | P1 | /dashboard (cockpit TD, hardcoded) |
| D-DGI-KC-013 | Metricas disciplina 5S de KB | NUEVO | P3 | Pagina nueva /kb/salud |
| D-DGI-KC-023 | Resumen capacitaciones realizadas | NUEVO | P2 | Pagina nueva /capacitaciones |
| D-DGI-KC-026 | Estado adopcion de cambios implementados | NUEVO | P3 | Pagina nueva /cambios |
| D-DGI-CI-001 | Preparar reunion semanal con AR | PARCIAL | P1 | /coordinacion |
| D-DGI-CI-002 | Registrar decisiones de reunion AR | NUEVO | P1 | /coordinacion |
| D-DGI-CI-003 | Seguimiento decisiones AR con semaforo | NUEVO | P1 | /coordinacion |
| D-DGI-CI-004 | Escalar temas a AR via Informe Ejecutivo | PARCIAL | P1 | /coordinacion + /informes |
| D-DGI-CI-005 | Matriz interacciones con divisiones | NUEVO | P2 | /coordinacion/divisiones |
| D-DGI-CI-008 | Registrar interacciones con Juridica | NUEVO | P2 | /coordinacion/divisiones |
| D-DGI-CI-010 | Acuerdos pendientes con divisiones | NUEVO | P2 | /coordinacion/divisiones |
| D-DGI-CI-012 | Escalamiento nivel 2 (bloqueo proyecto) | NUEVO | P1 | /escalamiento |
| D-DGI-CI-013 | Escalamiento nivel 3 (conflicto divisiones) | NUEVO | P2 | /escalamiento |
| D-DGI-CI-014 | Escalamiento nivel 4 (decision estrategica) | NUEVO | P2 | /escalamiento |
| D-DGI-CI-015 | Ver escalamientos activos con semaforo | NUEVO | P1 | /escalamiento |
| D-DGI-CI-017 | Participar como informante en Comite Coord Regional | NUEVO | P3 | /core-sessions (solo lectura) |
| D-DGI-CI-019 | Calendario consolidado reuniones DGI | NUEVO | P2 | /calendario |
| D-DGI-CI-020 | Publicar catalogo servicios DGI | NUEVO | P1 | /servicios |
| D-DGI-CI-022 | Feedback post-entrega de servicio | NUEVO | P2 | /servicios/[id] |
| D-DGI-POT-001 | Estructura DGI como Building Blocks Meyer | NUEVO | P3 | Pagina nueva /dgi/estructura |
| D-DGI-POT-002 | Matriz RACI sin superposiciones | NUEVO | P3 | Pagina nueva /dgi/estructura |
| D-DGI-POT-003 | Relacion cliente-proveedor con divisiones | NUEVO | P2 | /servicios (dashboard) |
| D-DGI-POT-004 | Mapa stakeholders con poder e interes | NUEVO | P1 | Pagina nueva /stakeholders |
| D-DGI-POT-005 | Estado ADKAR por stakeholder e iniciativa | NUEVO | P2 | /stakeholders/[id] |
| D-DGI-POT-006 | Tacticas de influencia por stakeholder | NUEVO | P3 | /stakeholders/[id] |
| D-DGI-POT-007 | Detectar resistencias al cambio | NUEVO | P2 | Pagina nueva /cambios |
| D-DGI-POT-008 | Identificar campeones por division | NUEVO | P2 | /stakeholders |
| D-DGI-POT-009 | NPS interno DGI (encuesta trimestral) | NUEVO | P1 | Pagina nueva /nps |
| D-DGI-POT-010 | Tasa adopcion voluntaria por division | NUEVO | P2 | /servicios (dashboard) |
| D-DGI-POT-011 | Tiempo promedio respuesta a solicitudes | NUEVO | P2 | /servicios (dashboard) |
| D-DGI-POT-012 | Proyectos completados sin escalamiento | NUEVO | P2 | /tablero (metricas) |
| D-DGI-POT-013 | Red de embajadores por division | NUEVO | P3 | /stakeholders |
| D-DGI-POT-015 | WIP limits por columna Kanban | IMPL | — | /tablero |
| D-DGI-POT-016 | Metricas Lean (throughput, lead/cycle time) | NUEVO | P1 | /tablero (lean panel) |
| D-DGI-POT-017 | CFD (Cumulative Flow Diagram) | NUEVO | P2 | /tablero (grafico) |
| D-DGI-POT-019 | Definir SLAs por producto DGI | NUEVO | P1 | /servicios/[id] (SLAs) |
| D-DGI-POT-020 | Monitorear cumplimiento SLAs | NUEVO | P1 | /servicios (SLA dashboard) |
| D-DGI-POT-022 | Plan de trabajo con prioridades | NUEVO | P1 | Pagina nueva /plan-trabajo |
| D-DGI-POT-023 | Priorizar iniciativas con scoring | NUEVO | P2 | /tablero (ranking) |
| D-DGI-POT-024 | Comunicar plan al equipo | NUEVO | P2 | /plan-trabajo |
| D-DGI-POT-025 | Registrar conflictos entre divisiones | NUEVO | P2 | /escalamiento (nuevo tipo) |
| D-DGI-POT-026 | Comunicar exitos y valor generado | NUEVO | P3 | Template comunicacion |

### ESP_CONTROL_GESTION

| Story ID | Descripcion | Estado | P | Paginas involucradas |
|----------|------------|:------:|:-:|---------------------|
| D-DGI-CG-001 | Ficha indicador con formula, umbrales, frecuencia | PARCIAL | P1 | /datos (CRUD parcial, faltan campos) |
| D-DGI-CG-002 | Editar umbrales de indicador existente | PARCIAL | P1 | /datos (PATCH existe) |
| D-DGI-CG-003 | Vincular indicador a objetivo estrategico | NUEVO | P2 | /datos (nuevo FK) |
| D-DGI-CG-004 | Fuente de datos y responsable por indicador | NUEVO | P2 | /datos (nuevos campos) |
| D-DGI-CG-005 | Catalogo indicadores con estado vigente/deprecado | PARCIAL | P1 | /datos (falta lifecycle completo) |
| D-DGI-CG-007 | Calculo automatico 4 indicadores reales | IMPL | — | /datos (refresh endpoint) |
| D-DGI-CG-008 | Indicador TDE desde inventario real | PARCIAL | P1 | /datos (hardcoded parcial) |
| D-DGI-CG-009 | Registro manual valor indicador | NUEVO | P2 | /datos (endpoint existe pero sin UI) |
| D-DGI-CG-010 | Comparar valor actual con periodos anteriores | IMPL | — | /datos (history endpoint) |
| D-DGI-CG-011 | Alerta cuando indicador bajo umbral 2 periodos | NUEVO | P1 | /datos (logica en refresh) |
| D-DGI-CG-012 | Validar calidad datos antes de calcular | NUEVO | P2 | /datos (flag verificacion) |
| D-DGI-CG-018 | Dashboard ejecutivo desglose comparativo divisiones | PARCIAL | P1 | /dashboard (sparklines parcial) |
| D-DGI-CG-019 | Detectar acumulacion trabajo pendiente por division | PARCIAL | P1 | /cuellos-de-botella (scan parcial) |
| D-DGI-CG-020 | Detectar incrementos tiempos de ciclo | NUEVO | P1 | /cuellos-de-botella (nuevo scan) |
| D-DGI-CG-021 | Investigacion cuello de botella (6 estados) | NUEVO | P2 | /cuellos-de-botella/[id] |
| D-DGI-CG-022 | Desviaciones presupuestarias por programa | PARCIAL | P1 | /cuellos-de-botella (scan parcial) |
| D-DGI-CG-024 | Informe estado situacional semanal 6 secciones | IMPL | — | /informes |
| D-DGI-CG-025 | Informe mensual con graficos tendencia | IMPL | — | /informes |
| D-DGI-CG-027 | Informe Flash urgente | IMPL | — | /informes |
| D-DGI-CG-028 | Informe Tematico por comite | IMPL | — | /informes |
| D-DGI-CG-029 | Recomendaciones con decisiones en informe | PARCIAL | P2 | /informes/[id] (seccion parcial) |
| D-DGI-CG-031 | Historial informes enviados | IMPL | — | /informes |
| D-DGI-CG-032 | Dashboard ejecutivo actualizado diariamente | IMPL | — | /dashboard |
| D-DGI-CG-033 | Alertas de desviacion continuas | IMPL | — | /alertas |
| D-DGI-CG-034 | Metricas verificadas a divisiones | PARCIAL | P2 | /datos (flag verificacion falta) |
| D-DGI-CG-036 | Resumen semanal por email | EXTERNO | P3 | Requiere email service |
| D-DGI-CG-037 | Reglas de alerta configurables | NUEVO | P1 | Pagina nueva /admin/alert-rules |
| D-DGI-CI-006 | Interacciones con DAF | NUEVO | P2 | /coordinacion/divisiones |
| D-DGI-CI-007 | Interacciones con DIPIR | NUEVO | P2 | /coordinacion/divisiones |
| D-DGI-CI-011 | Escalamiento nivel 1 (incidente operativo) | NUEVO | P1 | /escalamiento |
| D-DGI-CG-013 | Dashboard ejecutivo KPIs y alertas (AR) | IMPL | — | /dashboard |
| D-DGI-CG-016 | Dashboards tematicos por comite (AR) | NUEVO | P2 | /dashboard (filtro tematico) |

### ESP_PROCESOS

| Story ID | Descripcion | Estado | P | Paginas involucradas |
|----------|------------|:------:|:-:|---------------------|
| D-DGI-MP-001 | Registrar proceso institucional (CRUD) | NUEVO | P1 | /procesos |
| D-DGI-MP-002 | Asociar modelo BPMN a proceso | PARCIAL | P1 | /procesos/[id] (BPMN existe parcial) |
| D-DGI-MP-003 | Roles y sistemas por proceso | NUEVO | P2 | /procesos/[id] (tab-actors) |
| D-DGI-MP-004 | Reglas de negocio por proceso | NUEVO | P2 | /procesos/[id] (tab-rules) |
| D-DGI-MP-005 | Metricas actuales de proceso (linea base) | NUEVO | P1 | /procesos/[id] (tab-metrics) |
| D-DGI-MP-006 | Puntos de dolor en proceso | NUEVO | P2 | /procesos/[id] (tab-pain-points) |
| D-DGI-MP-007 | Sesiones de levantamiento programadas | NUEVO | P3 | Pagina nueva /sesiones-levantamiento |
| D-DGI-MP-008 | Validar modelo BPMN con participantes | NUEVO | P2 | /procesos/[id] (workflow) |
| D-DGI-MP-009 | Catalogo procesos con estado y fecha | PARCIAL | P1 | /procesos |
| D-DGI-MP-011 | Oportunidades de mejora con dimension | NUEVO | P1 | /procesos/[id] (tab-opportunities) |
| D-DGI-MP-012 | Matriz impacto/esfuerzo 3x3 | NUEVO | P2 | /procesos/progreso (matriz) |
| D-DGI-MP-013 | Convertir oportunidad en iniciativa DGI | NUEVO | P1 | /procesos/[id] (boton) |
| D-DGI-MP-014 | Analisis causa raiz (5 Porques, Ishikawa) | NUEVO | P2 | /cuellos-de-botella/[id] |
| D-DGI-MP-015 | Validacion oportunidades por JEFE_DIVISION | NUEVO | P2 | /procesos/[id] (workflow) |
| D-DGI-MP-016 | Modelo TO-BE de proceso mejorado | NUEVO | P2 | /procesos/[id] (BPMN versionado) |
| D-DGI-MP-017 | Plan de piloto de mejora | NUEVO | P2 | /tablero/[id] (seccion piloto) |
| D-DGI-MP-018 | Comparar metricas antes/despues | NUEVO | P2 | /procesos/[id] (tab-metrics comparar) |
| D-DGI-MP-019 | Lecciones aprendidas al cerrar mejora | NUEVO | P3 | /tablero/[id] (campo en DMAIC) |
| D-DGI-MP-020 | Tipo automatizacion implementada | NUEVO | P3 | /tablero (enum en iniciativa) |
| D-DGI-MP-021 | Kanban con fases DMAIC | IMPL | — | /tablero |
| D-DGI-MP-022 | Fase DMAIC actual de iniciativa | IMPL | — | /tablero/[id] |
| D-DGI-MP-023 | Charter DMAIC (Define) | NUEVO | P1 | /tablero/[id] (seccion Define) |
| D-DGI-MP-024 | Linea base DMAIC (Measure) | NUEVO | P2 | /tablero/[id] (seccion Measure) |
| D-DGI-MP-025 | Analisis causa raiz DMAIC (Analyze) | NUEVO | P2 | /tablero/[id] (seccion Analyze) |
| D-DGI-MP-026 | Solucion y piloto DMAIC (Improve) | NUEVO | P2 | /tablero/[id] (seccion Improve) |
| D-DGI-MP-027 | Controles y transferencia DMAIC (Control) | NUEVO | P2 | /tablero/[id] (seccion Control) |
| D-DGI-MP-029 | Value Stream Map por proceso | NUEVO | P3 | /procesos/[id] (VSM upload) |
| D-DGI-MP-030 | Tiempos de ciclo por etapa en VSM | NUEVO | P3 | /procesos/[id] (JSON VSM) |
| D-DGI-MP-031 | Especificaciones automatizacion como entregable | NUEVO | P3 | /tablero (tipo artefacto) |
| D-DGI-MP-032 | Carga de trabajo personal ESP_PROCESOS | PARCIAL | P2 | /dashboard (parcial via action-items) |
| D-DGI-CI-018 | Mesas de trabajo tematicas | NUEVO | P2 | Pagina nueva /mesas-trabajo |
| D-DGI-POT-014 | Kanban flujo trabajo equipo DGI | IMPL | — | /tablero |
| D-DGI-POT-018 | Aging de items en columnas Kanban | NUEVO | P2 | /tablero (badge dias) |
| D-DGI-POT-027 | Proyecto piloto DMAIC visacion actos | NUEVO | P2 | /tablero/[id] (caso especifico) |
| D-DGI-POT-028 | Tiempos ciclo por etapa visacion | IMPL | — | /actos (resumen endpoint) |
| D-DGI-POT-029 | Etapas con mayor tiempo espera visacion | IMPL | — | /actos (analisis) |
| D-DGI-POT-030 | Alertas SLA por etapa visacion | PARCIAL | P1 | /admin/slas (parcial) |

### ESP_TD

| Story ID | Descripcion | Estado | P | Paginas involucradas |
|----------|------------|:------:|:-:|---------------------|
| D-DGI-TD-001 | Inventario procesos con nivel digitalizacion | NUEVO | P0 | Pagina nueva /tde/inventario |
| D-DGI-TD-002 | Brechas estado actual vs requisitos TDE | NUEVO | P1 | /tde/inventario (gap analysis) |
| D-DGI-TD-003 | Roadmap cumplimiento TDE con hitos | NUEVO | P1 | Pagina nueva /tde/roadmap |
| D-DGI-TD-004 | Checklist cumplimiento TDE por proceso | NUEVO | P1 | /tde/inventario (6 items) |
| D-DGI-TD-005 | Cockpit TDE con barras progreso reales | PARCIAL | P0 | /dashboard (cockpit TD, barras hardcoded) |
| D-DGI-TD-006 | Evidencia cumplimiento por proceso | NUEVO | P2 | /tde/inventario (upload) |
| D-DGI-TD-008 | Preparar agenda sesion Comite TD | PARCIAL | P1 | /comite-td |
| D-DGI-TD-009 | Actas Comite TD con acuerdos | NUEVO | P1 | /comite-td (acuerdos) |
| D-DGI-TD-010 | Seguimiento acuerdos Comite TD | NUEVO | P1 | /comite-td (vista acuerdos) |
| D-DGI-TD-011 | Avance TDE en cada sesion Comite | NUEVO | P2 | /comite-td (seccion auto) |
| D-DGI-TD-012 | Proponer iniciativas al Comite TD | NUEVO | P2 | /comite-td (tipo agenda) |
| D-DGI-TD-013 | Evaluar factibilidad tecnica | NUEVO | P3 | /comite-td (formulario) |
| D-DGI-TD-014 | Escalar impedimentos desde Comite a AR | NUEVO | P2 | /comite-td + /escalamiento |
| D-DGI-TD-015 | Inventario sistemas del GORE | NUEVO | P1 | Pagina nueva /tde/sistemas |
| D-DGI-TD-016 | Requisitos funcionales por sistema | NUEVO | P2 | /tde/sistemas/[id] |
| D-DGI-TD-017 | Reglas negocio en sistemas | NUEVO | P3 | /tde/sistemas/[id] |
| D-DGI-TD-018 | Incidentes de negocio en sistemas | NUEVO | P2 | /tde/sistemas/[id] |
| D-DGI-TD-019 | Estadisticas KB con datos reales | PARCIAL | P1 | /dashboard (cockpit TD, hardcoded) |
| D-DGI-TD-020 | Inventario conjuntos de datos criticos | NUEVO | P1 | Pagina nueva /tde/datasets |
| D-DGI-TD-021 | Fuente autoritativa de cada dato | NUEVO | P2 | /tde/datasets (campo) |
| D-DGI-TD-022 | Estandares calidad por dataset | NUEVO | P2 | /tde/datasets (reglas) |
| D-DGI-TD-023 | Necesidades integracion entre sistemas | NUEVO | P2 | /tde/sistemas (mapa) |
| D-DGI-TD-024 | Integrar datos desde SIGFE | EXTERNO | P1 | Conector externo |
| D-DGI-TD-025 | Integrar datos desde BIP | EXTERNO | P1 | Conector externo |
| D-DGI-TD-026 | Integrar datos desde PISEE | EXTERNO | P1 | Conector externo |
| D-DGI-TD-027 | Integrar datos desde CGR | EXTERNO | P1 | Conector externo |
| D-DGI-TD-028 | Alertas normativas reales plazos TDE | PARCIAL | P1 | /dashboard (cockpit TD) |
| D-DGI-TD-029 | Cumplimiento Resolucion 22/2023 | NUEVO | P2 | /tde/inventario (checklist) |
| D-DGI-TD-030 | Tracking cumplimiento PMG | NUEVO | P2 | Pagina nueva /tde/pmg |
| D-DGI-TD-031 | Artefactos conocimiento como producto | NUEVO | P3 | /tablero (tipo artefacto) |
| D-DGI-TD-032 | Agentes IA como producto DGI | NUEVO | P3 | Pagina nueva /kb/agentes |
| D-DGI-TD-033 | Integraciones como producto DGI | NUEVO | P3 | /tde/sistemas (inventario) |
| D-DGI-TD-034 | Autenticacion con ClaveUnica | EXTERNO | P1 | Login (OAuth2) |
| D-DGI-TD-035 | Velocidad avance TDE con datos reales | PARCIAL | P1 | /dashboard (cockpit TD, hardcoded) |
| D-DGI-CI-009 | Interacciones con Unidad Operaciones | NUEVO | P2 | /coordinacion/divisiones |
| D-DGI-CI-016 | Gestionar sesiones Comite TD | PARCIAL | P1 | /comite-td |
| D-DGI-KC-001 | Registrar artefacto KB con metadatos | NUEVO | P1 | Pagina nueva /kb |
| D-DGI-KC-002 | Clasificar por taxonomia institucional | NUEVO | P2 | /kb (categorias) |
| D-DGI-KC-003 | Vincular artefactos relacionados | NUEVO | P2 | /kb/[id] (relaciones) |
| D-DGI-KC-004 | Enviar artefacto a validacion por experto | NUEVO | P2 | /kb/[id] (workflow) |
| D-DGI-KC-005 | Revisar vigencia y deprecar obsoletos | NUEVO | P2 | /kb (filtro vencimiento) |
| D-DGI-KC-006 | Alertas por cambio normativo en KB | NUEVO | P3 | /kb (notificaciones) |
| D-DGI-KC-007 | Estadisticas uso KB | NUEVO | P2 | /kb (dashboard) |
| D-DGI-KC-009 | Auditar artefactos por utilidad (Seiri) | NUEVO | P2 | /kb (clasificacion) |
| D-DGI-KC-010 | Validar URN y taxonomia (Seiton) | NUEVO | P3 | /kb (validacion) |
| D-DGI-KC-011 | Revision periodica vigencia (Seiso) | NUEVO | P3 | /kb (job programado) |
| D-DGI-KC-012 | Plantillas estandar por tipo (Seiketsu) | NUEVO | P3 | /kb (templates) |
| D-DGI-KC-014 | Registrar agente IA institucional | NUEVO | P1 | Pagina nueva /kb/agentes |
| D-DGI-KC-015 | Monitorear interacciones agente IA | NUEVO | P2 | /kb/agentes/[id] |
| D-DGI-KC-016 | Ciclo vida agente IA (FSM) | NUEVO | P2 | /kb/agentes/[id] (workflow) |
| D-DGI-KC-017 | Dueno funcional + respuestas auditables | NUEVO | P2 | /kb/agentes/[id] |
| D-DGI-KC-018 | Evaluar efectividad agente IA | NUEVO | P3 | /kb/agentes/[id] (metricas) |
| D-DGI-KC-019 | Planificar capacitacion | NUEVO | P1 | Pagina nueva /capacitaciones |
| D-DGI-KC-020 | Registrar asistencia y evaluacion | NUEVO | P2 | /capacitaciones/[id] |
| D-DGI-KC-021 | Proceso de cambio 5 fases | NUEVO | P2 | Pagina nueva /cambios |
| D-DGI-KC-022 | Registrar resistencias al cambio | NUEVO | P2 | /cambios/[id] |
| D-DGI-KC-024 | Comunicar beneficios por stakeholder | NUEVO | P3 | /cambios (template) |
| D-DGI-KC-025 | Materiales apoyo post-capacitacion | NUEVO | P3 | /capacitaciones/[id] |
| D-DGI-KC-027 | Lecciones aprendidas por cambio | NUEVO | P3 | /cambios/[id] |
| D-DGI-KC-028 | Transparencia IA vs persona | PARCIAL | P2 | Global (badge) |

### ADMIN_REGIONAL

| Story ID | Descripcion | Estado | P | Paginas involucradas |
|----------|------------|:------:|:-:|---------------------|
| D-DGI-CG-013 | Dashboard ejecutivo KPIs y alertas | IMPL | — | /dashboard |
| D-DGI-CG-016 | Dashboards tematicos por comite | NUEVO | P2 | /dashboard (filtro) |
| D-DGI-CG-018 | Dashboard desglose comparativo divisiones | PARCIAL | P1 | /dashboard (sparklines) |
| D-DGI-CG-036 | Resumen semanal por email | EXTERNO | P3 | Email service |

### JEFE_DIVISION

| Story ID | Descripcion | Estado | P | Paginas involucradas |
|----------|------------|:------:|:-:|---------------------|
| D-DGI-CG-014 | Dashboard indicadores de mi division | IMPL | — | /dashboard |
| D-DGI-MP-015 | Validar oportunidades mejora para mi division | NUEVO | P2 | /procesos/[id] (aprobacion) |
| D-DGI-CI-021 | Solicitar servicio DGI formalmente | NUEVO | P1 | /servicios/solicitar |
| D-DGI-POT-021 | Ver SLAs comprometidos por DGI para mi division | NUEVO | P2 | /servicios (vista division) |
| D-DGI-CG-017 | Configurar indicadores por dashboard (cross) | NUEVO | P3 | /admin/dashboard-config |

---

## Stories de Alto Valor No Implementadas

### P0 — Criticas (1 story)

| Story ID | Rol | Descripcion | Impacto |
|----------|-----|------------|---------|
| D-DGI-TD-001 | ESP_TD | Inventario procesos con nivel digitalizacion | **Desbloquea TD-002..007 + cockpit TD real**. Sin esto, barras TDE son hardcoded. |

### P1 — Alto Valor (33 stories)

#### JEFE_DGI (10)

| Story ID | Descripcion | Justificacion |
|----------|------------|---------------|
| D-DGI-CI-002 | Registrar decisiones reunion AR | Sin trazabilidad de decisiones. Endpoint AR prep existe pero no persiste. |
| D-DGI-CI-003 | Seguimiento decisiones AR | Complemento directo de CI-002. |
| D-DGI-CI-015 | Ver escalamientos activos | Backend existe (dgi_escalation.py) pero frontend /escalamiento incompleto. |
| D-DGI-CI-020 | Catalogo servicios DGI publicado | Backend existe (dgi_services.py) pero catalogo sin contenido real. |
| D-DGI-TD-007 | Reportar avance TDE al Comite | Depende de TD-001 (inventario). |
| D-DGI-POT-004 | Mapa stakeholders | Sin gestion politica/social del DGI. Fundamento de toda la capa POT. |
| D-DGI-POT-009 | NPS interno DGI | Sin metricas de percepcion. |
| D-DGI-POT-016 | Metricas Lean (throughput, lead time) | Backend lean-metrics existe pero no surfaceado prominentemente. |
| D-DGI-POT-019 | Definir SLAs por producto | Backend SLA existe pero sin productos DGI definidos. |
| D-DGI-POT-022 | Plan de trabajo con prioridades | Sin planificacion formal del equipo DGI. |

#### ESP_CONTROL_GESTION (4)

| Story ID | Descripcion | Justificacion |
|----------|------------|---------------|
| D-DGI-CG-011 | Alerta indicador bajo umbral 2 periodos | Deteccion automatica, alto impacto con bajo esfuerzo. |
| D-DGI-CG-020 | Detectar incrementos tiempos de ciclo | Nuevo scan para cuellos de botella. Backend bottleneck parcial. |
| D-DGI-CG-037 | Reglas alerta configurables | Generaliza CG-011 a cualquier indicador. |
| D-DGI-CI-011 | Escalamiento nivel 1 | Backend existe, frontend falta para ESP_CG. |

#### ESP_PROCESOS (4)

| Story ID | Descripcion | Justificacion |
|----------|------------|---------------|
| D-DGI-MP-001 | CRUD proceso institucional | Backend dgi_processes.py existe con 22 endpoints. Frontend /procesos parcial. |
| D-DGI-MP-005 | Metricas actuales proceso (linea base) | Backend process_metric existe. Frontend tab pendiente. |
| D-DGI-MP-011 | Oportunidades de mejora | Backend improvement_opportunity existe. Frontend tab pendiente. |
| D-DGI-MP-013 | Convertir oportunidad en iniciativa | Bridge Opportunity->Initiative existe en backend. UI falta. |
| D-DGI-MP-023 | Charter DMAIC (Define) | DMAIC backend existe con jsonb_set. UI formulario estructurado falta. |

#### ESP_TD (8)

| Story ID | Descripcion | Justificacion |
|----------|------------|---------------|
| D-DGI-TD-002 | Brechas digitalizacion vs TDE | Gap analysis despues de TD-001. |
| D-DGI-TD-003 | Roadmap cumplimiento TDE | Planificacion de hitos. |
| D-DGI-TD-004 | Checklist 6 items TDE por proceso | Granularidad cumplimiento. |
| D-DGI-TD-015 | Inventario sistemas GORE | Sin gestion de plataformas. |
| D-DGI-TD-020 | Inventario datasets criticos | Sin gestion datos como activo. |
| D-DGI-KC-001 | Catalogo artefactos KB | Sin Knowledge Base real (todo hardcoded). |
| D-DGI-KC-014 | Inventario agentes IA | Sin governance de IA. |
| D-DGI-KC-019 | Planificar capacitaciones | Sin gestion de formacion. |

#### JEFE_DIVISION (1)

| Story ID | Descripcion | Justificacion |
|----------|------------|---------------|
| D-DGI-CI-021 | Solicitar servicio DGI | Backend service_request existe. UI /servicios/solicitar existe parcial. |

---

## Stories Podables (bajo valor o redundantes)

### Redundantes con implementacion existente (pueden descartarse)

| Story ID | Descripcion | Razon |
|----------|------------|-------|
| D-DGI-CG-009 | Registro manual valor indicador | Endpoint `/indicators/{id}/value` ya existe. Solo falta UI menor. |
| D-DGI-CG-032 | Dashboard ejecutivo actualizado diariamente | Redundante con CG-013 (ya implementado). |
| D-DGI-CG-033 | Alertas desviacion continuas | Ya cubierto por sistema de alertas existente. |
| D-DGI-MP-009 | Catalogo procesos con estado | Ya cubierto parcialmente por /procesos + dgi_processes.py. |
| D-DGI-CI-016 | Gestionar sesiones Comite TD | Ya cubierto por dgi_td_sessions.py + /comite-td. |

### Bajo valor operacional (P3 descartables)

| Story ID | Descripcion | Razon |
|----------|------------|-------|
| D-DGI-CG-017 | Configurar indicadores por dashboard | Over-engineering: pocos dashboards, configuracion manual suficiente. |
| D-DGI-MP-007 | Sesiones levantamiento programadas | Gestion de agenda no critica, calendario existente cubre. |
| D-DGI-MP-019 | Lecciones aprendidas al cerrar | Campo de texto, no requiere tabla nueva. |
| D-DGI-MP-020 | Tipo automatizacion como enum | Clasificacion menor, no impacta operacion. |
| D-DGI-MP-029 | Value Stream Map por proceso | Herramienta especializada, upload de imagen suficiente. |
| D-DGI-MP-030 | Tiempos ciclo por etapa VSM (JSON) | Complejidad alta, valor marginal sobre MP-005. |
| D-DGI-MP-031 | Especificaciones automatizacion | Documento, no requiere entidad propia. |
| D-DGI-TD-013 | Evaluar factibilidad tecnica | Formulario ad-hoc, no requiere tabla. |
| D-DGI-TD-017 | Reglas negocio en sistemas | Muy granular, documento Confluence suficiente. |
| D-DGI-TD-031 | Artefactos conocimiento como producto | Tipo de entidad, no requiere tabla. |
| D-DGI-TD-032 | Agentes IA como producto | Duplica KC-014. |
| D-DGI-TD-033 | Integraciones como producto | Duplica TD-023. |
| D-DGI-KC-006 | Alertas cambio normativo en KB | Requiere deteccion automatica, complejidad alta. |
| D-DGI-KC-010 | Validar URN y taxonomia (Seiton) | Validacion basica, no justifica feature. |
| D-DGI-KC-011 | Revision periodica vigencia (Seiso) | Job programado, puede ser manual. |
| D-DGI-KC-012 | Plantillas estandar (Seiketsu) | Templates estaticos, no requiere sistema. |
| D-DGI-KC-018 | Evaluar efectividad agente IA | Metricas derivables sin tabla nueva. |
| D-DGI-KC-024 | Comunicar beneficios por stakeholder | Template de comunicacion, no requiere sistema. |
| D-DGI-KC-025 | Materiales apoyo post-capacitacion | Links simples, no requiere entidad. |
| D-DGI-KC-027 | Lecciones aprendidas por cambio | Campo de texto, no justifica tabla. |
| D-DGI-POT-001 | Building Blocks Meyer como pagina | Visualizacion organigrama, no operacional. |
| D-DGI-POT-002 | Matriz RACI sin superposiciones | Estatica, documento suficiente. |
| D-DGI-POT-006 | Tacticas influencia por stakeholder | Conceptual, no operacional. |
| D-DGI-POT-013 | Red de embajadores por division | Flag booleano, no requiere pagina. |
| D-DGI-POT-026 | Comunicar exitos valor DGI | Template email, no requiere sistema. |
| D-DGI-CI-017 | Participar Comite Coord Regional | Solo lectura en core-sessions existente. |

**Total podables: 31 stories** (5 redundantes + 26 bajo valor)

Si se descartan, el backlog se reduce de 185 a **154 stories** y la cobertura sube de 26.5% a **31.8%**.

---

## Resumen de Paginas Nuevas Requeridas

| Pagina | Stories que atiende | Prioridad |
|--------|:-------------------:|:---------:|
| /tde/inventario | TD-001..006, TD-029 | P0 |
| /tde/roadmap | TD-003 | P1 |
| /tde/sistemas | TD-015..018, TD-023 | P1 |
| /tde/datasets | TD-020..022 | P1 |
| /tde/pmg | TD-030 | P2 |
| /kb | KC-001..007, KC-009..012 | P1 |
| /kb/agentes | KC-014..018, TD-032 | P1 |
| /capacitaciones | KC-019..020, KC-023, KC-025 | P1 |
| /cambios | KC-021..022, KC-027, POT-007 | P2 |
| /stakeholders | POT-004..008, POT-013 | P1 |
| /nps | POT-009 | P1 |
| /plan-trabajo | POT-022..024 | P1 |
| /admin/alert-rules | CG-037 | P1 |
| /dgi/estructura | POT-001..002 | P3 |

**Total: 14 paginas nuevas** (10 P1, 2 P2, 1 P0, 1 P3)

---

## Mapa Backend: Stories con Infraestructura Existente

Stories donde el backend ya tiene endpoints pero la cobertura frontend es incompleta o nula:

| Story ID | Backend existente | Frontend gap |
|----------|------------------|--------------|
| D-DGI-CG-009 | `POST /indicators/{id}/value` | Falta UI formulario valor manual |
| D-DGI-CG-019 | `GET /dgi/bottleneck/scan` | Parcial, falta scan acumulacion |
| D-DGI-CG-022 | `GET /dgi/bottleneck/scan` | Parcial, falta scan presupuesto |
| D-DGI-MP-001 | `POST /dgi/processes` | Frontend existe pero incompleto |
| D-DGI-MP-003 | `POST /processes/{id}/actors` | Frontend tab-actors existe |
| D-DGI-MP-004 | `POST /processes/{id}/rules` | Frontend tab-rules existe |
| D-DGI-MP-005 | `POST /processes/{id}/metrics` | Frontend tab-metrics existe |
| D-DGI-MP-006 | `POST /processes/{id}/pain-points` | Frontend tab-pain-points existe |
| D-DGI-MP-011 | `POST /processes/{id}/opportunities` | Frontend tab-opportunities existe |
| D-DGI-MP-013 | Opportunity->Initiative bridge | Falta boton "Crear Iniciativa" |
| D-DGI-MP-018 | `GET /processes/{id}/metrics/comparison` | Falta toggle "Comparar" UI |
| D-DGI-CI-002 | `POST /coordination/ar/decisions` | Frontend /coordinacion parcial |
| D-DGI-CI-011 | `POST /dgi/escalation` | Frontend /escalamiento parcial |
| D-DGI-CI-015 | `GET /dgi/escalation/active` | Frontend /escalamiento parcial |
| D-DGI-CI-020 | `GET /dgi/services` | Frontend /servicios existe |
| D-DGI-CI-021 | `POST /dgi/services/requests` | Frontend /servicios/solicitar existe |
| D-DGI-POT-016 | `GET /dgi/initiatives/lean-metrics` | Frontend parcial |
| D-DGI-POT-019 | `POST /dgi/services/{id}/slas` | Frontend /servicios/[id] parcial |

**18 stories con backend listo** — solo requieren completar/conectar frontend.
