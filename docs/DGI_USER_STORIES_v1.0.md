# User Stories DGI — Catálogo Exhaustivo v1.0

> **Complemento**: Para métricas de cobertura actualizadas por rol y por Story, ver [GORE_OS_Story_Coverage_v1.0.md](GORE_OS_Story_Coverage_v1.0.md) (sesión C60). Este documento es el catálogo completo de 185 stories; aquel documento añade el desglose por rol y la cobertura efectiva (26.5% implementado).

**Fecha**: 2026-03-10
**Fuentes KORA**: `urn:gn:kb:plan-potenciamiento-dgi`, `urn:gn:kb:manual-operacional-dgi`
**Cruce**: Inventario GORE_OS DGI layer (34 endpoints, 5 páginas, 4 cockpits, 398 tests)

## Convenciones

- **Formato**: `Como [ROL], quiero [ACCIÓN], para [VALOR]`
- **Estado**: Implementado / Parcial / Nuevo / Externo
- **Prioridad**: P0 (crítico), P1 (alto), P2 (medio), P3 (bajo)
- **Fuente**: MO = Manual Operacional, PP = Plan Potenciamiento, con ID de sección

---

## Resumen Ejecutivo

| Dominio | Total | Implementado | Parcial | Nuevo | Externo |
|---------|:-----:|:------------:|:-------:|:-----:|:-------:|
| D-DGI-CG — Control de Gestión | 38 | 12 | 8 | 16 | 2 |
| D-DGI-MP — Modernización Procesos | 32 | 2 | 3 | 27 | 0 |
| D-DGI-TD — Transformación Digital | 35 | 3 | 5 | 20 | 7 |
| D-DGI-KC — Gestión Conocimiento | 28 | 0 | 2 | 26 | 0 |
| D-DGI-CI — Coordinación Institucional | 22 | 3 | 4 | 15 | 0 |
| D-DGI-POT — Potenciamiento (Meyer/DMAIC/Social) | 30 | 4 | 3 | 23 | 0 |
| **TOTAL** | **185** | **24** | **25** | **127** | **9** |

---

## 1. D-DGI-CG — Control de Gestión

> Fuente: MO DGI-CG-01..04, PP POT-ARQ-02 (ServiceProvidersControl)

### 1.1 Definición y Gestión de Indicadores

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CG-001 | Como ESP_CONTROL_GESTION, quiero crear una ficha de indicador con nombre, fórmula, unidad, meta, umbrales y frecuencia, para documentar formalmente cada KPI institucional | Formulario CRUD. Campos: nombre, código, dimensión, fórmula (texto), unidad, meta, umbral_verde, umbral_amarillo, fuente_datos, frecuencia, responsable_dato. Validar unicidad de código | MO DGI-CG-01 | Parcial | P1 |
| D-DGI-CG-002 | Como ESP_CONTROL_GESTION, quiero editar los umbrales de un indicador existente, para ajustarlos según cambios en metas institucionales | PATCH con allowlist. Auditoría de cambio en historial | MO DGI-CG-01 | Parcial | P1 |
| D-DGI-CG-003 | Como ESP_CONTROL_GESTION, quiero vincular un indicador a un objetivo estratégico (ERD, Ñuble 250), para trazar la cadena de valor desde KPI a estrategia | FK opcional a tabla de objetivos estratégicos. Filtrable en listados | MO DGI-CG-01 | Nuevo | P2 |
| D-DGI-CG-004 | Como ESP_CONTROL_GESTION, quiero definir la fuente de datos de cada indicador y su responsable de provisión, para saber a quién requerir actualizaciones | Campos: fuente_sistema, responsable_provision_id (FK user), frecuencia_actualizacion | MO DGI-CG-01 | Nuevo | P2 |
| D-DGI-CG-005 | Como ESP_CONTROL_GESTION, quiero ver un catálogo de todos los indicadores con su estado (vigente/suspendido/deprecado), para gestionar el ciclo de vida de las métricas | Listado filtrable por dimensión, estado, frecuencia. Soft-delete (deprecated_at) | MO DGI-CG-01 | Parcial | P1 |
| D-DGI-CG-006 | Como JEFE_DGI, quiero aprobar la creación o modificación de indicadores antes de que entren en producción, para asegurar calidad y coherencia | Workflow: BORRADOR → APROBADO → VIGENTE. Solo JEFE_DGI puede aprobar | MO DGI-CG-01 | Nuevo | P2 |

### 1.2 Recolección y Cálculo

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CG-007 | Como ESP_CONTROL_GESTION, quiero que los indicadores PRESUPUESTO, CARTERA_IPR, CONVENIOS y RIESGOS se calculen automáticamente desde datos reales, para tener métricas siempre actualizadas | Endpoint refresh idempotente. 4 funciones de cálculo. Snapshots en historial | MO DGI-CG-01 | Implementado | — |
| D-DGI-CG-008 | Como ESP_CONTROL_GESTION, quiero que el indicador TDE se calcule desde un inventario real de procesos y su nivel de digitalización, para reemplazar el valor estático actual | Requiere tabla de inventario de procesos con campo nivel_digitalizacion. Fórmula: procesos_digitalizados / total_procesos | MO DGI-CG-01 | Parcial | P1 |
| D-DGI-CG-009 | Como ESP_CONTROL_GESTION, quiero registrar manualmente el valor de un indicador cuando no hay fuente automatizada, para cubrir métricas cualitativas o de fuentes externas | Endpoint POST /indicators/{id}/value con valor, fecha, comentario. Solo para indicadores con fuente_tipo=MANUAL | MO DGI-CG-01 | Nuevo | P2 |
| D-DGI-CG-010 | Como ESP_CONTROL_GESTION, quiero comparar el valor actual de un indicador con períodos anteriores, para identificar tendencias | Gráfico de línea temporal en detalle de indicador. Datos desde dgi_indicator_snapshot | MO DGI-CG-01 | Implementado | — |
| D-DGI-CG-011 | Como ESP_CONTROL_GESTION, quiero recibir una alerta automática cuando un indicador permanece bajo su umbral por más de 2 períodos consecutivos, para detectar problemas persistentes | Lógica en refresh: si signal=ROJO por ≥2 snapshots consecutivos → crear core.alert con severity=ALTO | MO DGI-CG-03 | Nuevo | P1 |
| D-DGI-CG-012 | Como ESP_CONTROL_GESTION, quiero validar la calidad de los datos recibidos antes de calcular un indicador, para evitar métricas basadas en datos incorrectos | Flag de calidad por fuente: VERIFICADO/NO_VERIFICADO/ERROR. Indicador con fuente ERROR no se recalcula | MO DGI-CG-01 | Nuevo | P2 |

### 1.3 Dashboards

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CG-013 | Como ADMIN_REGIONAL, quiero ver un dashboard ejecutivo con KPIs agregados y alertas críticas actualizado diariamente, para tomar decisiones informadas | Vista cockpit con semáforo 5 dimensiones, top alertas, decisiones pendientes | MO DGI-CG-02 | Implementado | — |
| D-DGI-CG-014 | Como JEFE_DIVISION, quiero ver un dashboard con indicadores específicos de mi división, para monitorear mi gestión | Dashboard filtrado por division_id del usuario. Indicadores de ejecución presupuestaria, compromisos, convenios, alertas propias | MO DGI-CG-02 | Implementado | — |
| D-DGI-CG-015 | Como JEFE_DGI, quiero ver el estado del equipo DGI (qué hace cada especialista, última actividad), para coordinar el trabajo | Panel team_status con último login, iniciativas asignadas, informes en curso | MO DGI-CG-02 | Implementado | — |
| D-DGI-CG-016 | Como ADMIN_REGIONAL, quiero ver dashboards temáticos por comité (IPR, TD, Presupuesto), para preparar reuniones con información focalizada | Endpoint con filtro temático. Reutiliza indicadores agrupados por dimensión | MO DGI-CG-02 | Nuevo | P2 |
| D-DGI-CG-017 | Como ESP_CONTROL_GESTION, quiero configurar qué indicadores aparecen en cada tipo de dashboard, para personalizar vistas por audiencia | Tabla de configuración dashboard_indicator_config(dashboard_type, indicator_id, display_order) | MO DGI-CG-02 | Nuevo | P3 |
| D-DGI-CG-018 | Como ADMIN_REGIONAL, quiero que el dashboard ejecutivo muestre indicadores de todas las divisiones con desglose comparativo, para ver desempeño relativo | Grid de divisiones con sparklines por indicador. Sort por cualquier métrica | MO DGI-CG-02 | Parcial | P1 |

### 1.4 Detección de Cuellos de Botella

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CG-019 | Como ESP_CONTROL_GESTION, quiero detectar automáticamente acumulación de trabajo pendiente por división, para anticipar cuellos de botella | Query: compromisos PENDIENTE + problemas ABIERTO agrupados por división. Alerta si count > umbral configurable | MO DGI-CG-03 | Parcial | P1 |
| D-DGI-CG-020 | Como ESP_CONTROL_GESTION, quiero detectar incrementos en tiempos de ciclo de procesos clave (visación de actos, rendiciones), para identificar degradación | Comparar promedio días_en_estado actual vs. promedio histórico. Alerta si delta > 50% | MO DGI-CG-03 | Nuevo | P1 |
| D-DGI-CG-021 | Como ESP_CONTROL_GESTION, quiero registrar una investigación de cuello de botella con problema, causa raíz, propuesta y seguimiento, para documentar el análisis | CRUD investigación: problema, verificación, análisis_causa_raíz, propuesta, comunicación, seguimiento, estado (DETECTADO→VERIFICADO→ANALIZADO→PROPUESTO→IMPLEMENTADO→CERRADO) | MO DGI-CG-03 | Nuevo | P2 |
| D-DGI-CG-022 | Como ESP_CONTROL_GESTION, quiero ver desviaciones presupuestarias significativas por programa, para alertar a las divisiones | Calcular (vigente - ejecutado) / vigente por budget_program. Alerta si ejecución < 40% al cierre Q3 | MO DGI-CG-03 | Parcial | P1 |
| D-DGI-CG-023 | Como JEFE_DGI, quiero ver un resumen de cuellos de botella activos con su estado de resolución, para reportar a AR | Vista consolidada de investigaciones en curso agrupadas por división y estado | MO DGI-CG-03 | Nuevo | P2 |

### 1.5 Informes

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CG-024 | Como ESP_CONTROL_GESTION, quiero generar un informe estado situacional semanal con 6 secciones auto-pobladas, para informar a AR | 6 secciones: resumen, indicadores, alertas, avance DGI, recomendaciones, próximo período. Auto-populado + editable | MO DGI-CG-04 | Implementado | — |
| D-DGI-CG-025 | Como ESP_CONTROL_GESTION, quiero generar un informe mensual completo con gráficos de tendencia y análisis detallado, para documentar la gestión | Tipo MENSUAL con secciones extendidas: incluye comparativa mes anterior, tendencias 6m | MO DGI-CG-04 | Implementado | — |
| D-DGI-CG-026 | Como JEFE_DGI, quiero revisar y aprobar un informe antes de enviarlo, para asegurar calidad | Workflow BORRADOR → EN_REVISION → ENVIADO. Solo JEFE_DGI cambia a ENVIADO | MO DGI-CG-04 | Implementado | — |
| D-DGI-CG-027 | Como ESP_CONTROL_GESTION, quiero generar un informe Flash (urgente) sobre una situación crítica, para informar rápidamente a AR | Tipo FLASH con sección resumen obligatoria y campo urgencia. Sin período, con timestamp | MO DGI-CG-04 | Implementado | — |
| D-DGI-CG-028 | Como ESP_CONTROL_GESTION, quiero generar un informe Temático para un comité específico, para focalizar la información | Tipo TEMATICO con campo comité/tema. Secciones filtradas por dimensión relevante | MO DGI-CG-04 | Implementado | — |
| D-DGI-CG-029 | Como ESP_CONTROL_GESTION, quiero incluir recomendaciones con decisiones requeridas en el informe, para que AR tenga opciones claras | Sección "decisiones" con items accionables: descripción, opciones, recomendación, plazo | MO DGI-CG-04 | Parcial | P2 |
| D-DGI-CG-030 | Como JEFE_DGI, quiero exportar un informe como PDF con formato institucional, para enviar por canales formales | Endpoint export con template GORE Ñuble. Incluye logos, encabezados, paginación | MO DGI-CG-04 | Nuevo | P2 |
| D-DGI-CG-031 | Como ESP_CONTROL_GESTION, quiero ver el historial de informes enviados con fecha, tipo y destinatario, para tener trazabilidad | Listado con filtros: tipo, estado, período, generado_por | MO DGI-CG-04 | Implementado | — |

### 1.6 Productos Control de Gestión (Catálogo)

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CG-032 | Como ESP_CONTROL_GESTION, quiero mantener un dashboard ejecutivo actualizado diariamente, para entregar visibilidad permanente a AR | Dashboard auto-actualizado con datos reales. KPIs agregados + alertas | PP POT-ARQ-02 | Implementado | — |
| D-DGI-CG-033 | Como ESP_CONTROL_GESTION, quiero generar alertas de desviación en forma continua, para detectar problemas proactivamente | Sistema de alertas existente + detección automática de desviaciones | PP POT-ARQ-02 | Implementado | — |
| D-DGI-CG-034 | Como ESP_CONTROL_GESTION, quiero entregar métricas calculadas y verificadas a las divisiones, para que tengan información confiable | Indicadores con flag de verificación + fuente documentada | PP POT-ARQ-02 | Parcial | P2 |
| D-DGI-CG-035 | Como JEFE_DGI, quiero ver un panel de "productividad DGI" con productos entregados por tipo y período, para medir output del equipo | Conteo de informes, alertas generadas, indicadores actualizados, iniciativas movidas — agrupados por mes | PP POT-ARQ-02 | Nuevo | P2 |
| D-DGI-CG-036 | Como ADMIN_REGIONAL, quiero recibir un resumen semanal automático por email con el estado de los indicadores clave, para estar informado sin entrar al sistema | Job programado: genera resumen + envía por email/notificación | MO DGI-CG-04 | Externo | P3 |
| D-DGI-CG-037 | Como ESP_CONTROL_GESTION, quiero definir reglas de alerta configurables (umbral, períodos, destinatarios), para personalizar la detección por indicador | Tabla alert_rule: indicator_id, threshold, periods_below, notify_roles[], severity | MO DGI-CG-03 | Nuevo | P1 |
| D-DGI-CG-038 | Como JEFE_DGI, quiero ver items de decisión pendientes con contexto y acciones posibles en mi cockpit, para priorizar qué resolver primero | Panel decision_items con alertas críticas + rendiciones vencidas + link de navegación | MO DGI-CG-04 | Implementado | — |

---

## 2. D-DGI-MP — Modernización de Procesos

> Fuente: MO DGI-MP-01..04, PP POT-ARQ-02 (EngineersProcesos), PP POT-DMAIC-01..04

### 2.1 Inventario y Levantamiento BPMN

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-MP-001 | Como ESP_PROCESOS, quiero registrar un proceso institucional con nombre, alcance, división responsable, inicio y fin, para mantener un inventario actualizado | CRUD proceso: nombre, código, descripción, alcance, division_id, actor_inicio, actor_fin, estado (IDENTIFICADO, EN_LEVANTAMIENTO, MODELADO, VALIDADO, PUBLICADO) | MO DGI-MP-01 | Nuevo | P1 |
| D-DGI-MP-002 | Como ESP_PROCESOS, quiero asociar un modelo BPMN (archivo/URL) a un proceso, para documentar el diagrama AS-IS | Upload o URL de diagrama BPMN. Tabla: bpmn_model(proceso_id, version, file_url, tipo=AS_IS/TO_BE, created_at) | MO DGI-MP-01 | Parcial | P1 |
| D-DGI-MP-003 | Como ESP_PROCESOS, quiero registrar los roles y sistemas involucrados en un proceso, para mapear actores y herramientas | Tabla proceso_actor: proceso_id, actor_type (ROL/SISTEMA/DIVISION), actor_name, lane_label | MO DGI-MP-01 | Nuevo | P2 |
| D-DGI-MP-004 | Como ESP_PROCESOS, quiero documentar las reglas de negocio de un proceso, para capturar lógica que no se ve en el diagrama | Tabla proceso_regla: proceso_id, código, descripción, tipo (VALIDACION/DECISION/CALCULO/RESTRICCION) | MO DGI-MP-01 | Nuevo | P2 |
| D-DGI-MP-005 | Como ESP_PROCESOS, quiero registrar las métricas actuales de un proceso (tiempos de ciclo, volumen mensual, tasa de error), para establecer línea base | Tabla proceso_metrica: proceso_id, nombre, valor_actual, unidad, fecha_medicion, fuente | MO DGI-MP-01 | Nuevo | P1 |
| D-DGI-MP-006 | Como ESP_PROCESOS, quiero identificar y registrar puntos de dolor en un proceso, para priorizar mejoras | Tabla proceso_pain_point: proceso_id, descripción, impacto (ALTO/MEDIO/BAJO), etapa_bpmn, reportado_por | MO DGI-MP-01 | Nuevo | P2 |
| D-DGI-MP-007 | Como ESP_PROCESOS, quiero programar sesiones de levantamiento con participantes de la división, para coordinar el trabajo de campo | Tabla sesion_levantamiento: proceso_id, fecha, participantes[], tipo (ENTREVISTA/OBSERVACION/TALLER), notas, estado | MO DGI-MP-01 | Nuevo | P3 |
| D-DGI-MP-008 | Como ESP_PROCESOS, quiero validar un modelo BPMN con los participantes antes de publicarlo, para asegurar fidelidad | Workflow: MODELADO → EN_VALIDACION → VALIDADO → PUBLICADO. Requiere aprobación de al menos 1 participante de la división | MO DGI-MP-01 | Nuevo | P2 |
| D-DGI-MP-009 | Como ESP_PROCESOS, quiero ver un catálogo de todos los procesos levantados con su estado y última actualización, para gestionar el inventario | Listado filtrable por división, estado, fecha. Incluye badge de vigencia | MO DGI-MP-01 | Parcial | P1 |
| D-DGI-MP-010 | Como JEFE_DGI, quiero ver cuántos procesos están levantados vs. identificados por división, para medir avance del inventario | Dashboard: barra de progreso por división (levantados / identificados). Meta configurable | MO DGI-MP-01 | Nuevo | P2 |

### 2.2 Análisis de Mejora

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-MP-011 | Como ESP_PROCESOS, quiero registrar oportunidades de mejora identificadas en un proceso con dimensión de análisis, para documentar hallazgos | CRUD oportunidad: proceso_id, dimensión (VALOR/DUPLICACION/ESPERAS/MOVIMIENTOS/ERRORES/AUTOMATIZACION), descripción, impacto, esfuerzo | MO DGI-MP-02 | Nuevo | P1 |
| D-DGI-MP-012 | Como ESP_PROCESOS, quiero priorizar oportunidades de mejora por impacto y esfuerzo en una matriz 3x3, para focalizar recursos | Vista matriz con ejes impacto (alto/medio/bajo) × esfuerzo (alto/medio/bajo). Quick wins (alto impacto + bajo esfuerzo) destacados | MO DGI-MP-02 | Nuevo | P2 |
| D-DGI-MP-013 | Como ESP_PROCESOS, quiero convertir una oportunidad de mejora priorizada en una iniciativa DGI, para ejecutarla en el Kanban | Botón "Crear Iniciativa" que pre-rellena nombre, descripción y vincula a oportunidad_id | MO DGI-MP-02 | Nuevo | P1 |
| D-DGI-MP-014 | Como ESP_PROCESOS, quiero registrar el análisis de causa raíz (5 Porqués, Ishikawa) de un problema en un proceso, para documentar la investigación | Campo análisis_causa_raíz en oportunidad/investigación. Soporte texto estructurado (5 niveles de porqué) | MO DGI-MP-02 | Nuevo | P2 |
| D-DGI-MP-015 | Como JEFE_DIVISION, quiero validar las oportunidades de mejora propuestas para mi división antes de que avancen, para mantener autonomía de decisión | Workflow: PROPUESTA → VALIDADA_DIVISION → EN_EJECUCION. JEFE_DIVISION aprueba o rechaza | MO DGI-MP-02 | Nuevo | P2 |

### 2.3 Implementación de Mejoras

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-MP-016 | Como ESP_PROCESOS, quiero diseñar el modelo TO-BE de un proceso mejorado, para documentar el estado futuro | Nuevo BPMN model con tipo=TO_BE vinculado al mismo proceso. Versionado | MO DGI-MP-04 | Nuevo | P2 |
| D-DGI-MP-017 | Como ESP_PROCESOS, quiero registrar el plan de piloto de una mejora (alcance, duración, métricas de éxito), para ejecutar de forma controlada | Tabla piloto: iniciativa_id, alcance_desc, fecha_inicio, fecha_fin, metricas_exito[], estado (PLANIFICADO/EN_CURSO/COMPLETADO/CANCELADO) | MO DGI-MP-04 | Nuevo | P2 |
| D-DGI-MP-018 | Como ESP_PROCESOS, quiero comparar métricas antes y después de una mejora implementada, para medir impacto real | Vista comparativa: métricas línea base vs. métricas post-implementación por proceso | MO DGI-MP-04 | Nuevo | P2 |
| D-DGI-MP-019 | Como ESP_PROCESOS, quiero documentar lecciones aprendidas al cerrar un proyecto de mejora, para alimentar el conocimiento institucional | Campo lecciones_aprendidas al cerrar iniciativa DMAIC en fase CONTROL/COMPLETADO | MO DGI-MP-04 | Nuevo | P3 |
| D-DGI-MP-020 | Como ESP_PROCESOS, quiero registrar el tipo de automatización implementada (RPA, flujo de trabajo, notificaciones, reportes, integración), para categorizar mejoras | Enum automation_type en iniciativa o mejora. Filtrable en listados | MO DGI-MP-03 | Nuevo | P3 |

### 2.4 DMAIC Framework

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-MP-021 | Como ESP_PROCESOS, quiero gestionar iniciativas DGI en un tablero Kanban con fases DMAIC, para seguir la metodología de mejora | Kanban: BACKLOG → EN_DISEÑO (D-M-A) → EN_IMPLEMENTACIÓN (I) → EN_VERIFICACIÓN (C) → COMPLETADO, con drag-and-drop y orden persistente | PP POT-DMAIC-04 | Implementado | — |
| D-DGI-MP-022 | Como ESP_PROCESOS, quiero registrar la fase DMAIC actual de una iniciativa (Define/Measure/Analyze/Improve/Control), para tracking granular | Campo dmaic_phase en iniciativa con opciones D/M/A/I/C | PP POT-DMAIC-01 | Implementado | — |
| D-DGI-MP-023 | Como ESP_PROCESOS, quiero definir un charter de proyecto DMAIC con problema, alcance, objetivos SMART, stakeholders y sponsor, para la fase Define | Formulario charter: problema_desc, alcance, objetivo_smart, stakeholders[], sponsor_id, caso_negocio | PP POT-DMAIC-01 | Nuevo | P1 |
| D-DGI-MP-024 | Como ESP_PROCESOS, quiero registrar la línea base de un proyecto DMAIC con métricas y VSM, para la fase Measure | Sección Measure en iniciativa: metricas_base[], vsm_url, sistema_medicion_validado (bool) | PP POT-DMAIC-01 | Nuevo | P2 |
| D-DGI-MP-025 | Como ESP_PROCESOS, quiero documentar el análisis de causa raíz y priorización de causas de un proyecto DMAIC, para la fase Analyze | Sección Analyze: causas_raíz[], herramienta_usada (5_PORQUES/ISHIKAWA/PARETO), cuellos_botella[], oportunidades_cuantificadas | PP POT-DMAIC-01 | Nuevo | P2 |
| D-DGI-MP-026 | Como ESP_PROCESOS, quiero documentar la solución diseñada, prototipo y resultado del piloto de un proyecto DMAIC, para la fase Improve | Sección Improve: diseño_to_be_url, prototipo_desc, piloto_resultado, capacitacion_realizada (bool) | PP POT-DMAIC-01 | Nuevo | P2 |
| D-DGI-MP-027 | Como ESP_PROCESOS, quiero documentar los controles establecidos y transferencia a operación de un proyecto DMAIC, para la fase Control | Sección Control: controles_estadisticos[], nuevo_estandar_url, alertas_configuradas[], transferido_a_operacion (bool) | PP POT-DMAIC-01 | Nuevo | P2 |
| D-DGI-MP-028 | Como JEFE_DGI, quiero ver un resumen de proyectos DMAIC por fase con tiempos promedio en cada fase, para medir throughput del equipo | Dashboard: count por fase DMAIC, promedio días en cada fase, tendencia mensual | PP POT-DMAIC-04 | Nuevo | P2 |

### 2.5 Value Stream Mapping

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-MP-029 | Como ESP_PROCESOS, quiero crear un Value Stream Map asociado a un proceso, para visualizar el flujo de valor completo | Upload/URL de VSM. Tabla vsm: proceso_id, version, file_url, tipo (ACTUAL/FUTURO), tiempos_ciclo_json | PP POT-DMAIC-01 | Nuevo | P3 |
| D-DGI-MP-030 | Como ESP_PROCESOS, quiero registrar tiempos de ciclo por etapa en un VSM, para cuantificar esperas y desperdicios | JSON estructurado: [{etapa, tiempo_proceso_min, tiempo_espera_min, valor_agregado: bool}] | PP POT-DMAIC-01 | Nuevo | P3 |

### 2.6 Productos Especialista Procesos (Catálogo)

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-MP-031 | Como ESP_PROCESOS, quiero registrar especificaciones de automatización como producto entregable, para documentar las soluciones técnicas diseñadas | Tipo de artefacto ESPECIFICACION_AUTOMATIZACION vinculado a proceso/iniciativa | PP POT-ARQ-02 | Nuevo | P3 |
| D-DGI-MP-032 | Como ESP_PROCESOS, quiero ver mi carga de trabajo actual (procesos en levantamiento, iniciativas activas, mejoras en curso), para planificar mi tiempo | Panel personal: mis procesos asignados, mis iniciativas, mis mejoras — agrupados por estado | PP POT-ARQ-02 | Parcial | P2 |

---

## 3. D-DGI-TD — Transformación Digital

> Fuente: MO DGI-TD-01..04, PP POT-ARQ-02 (EngineersTD)

### 3.1 Cumplimiento TDE (Ley 21.180)

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-TD-001 | Como ESP_TD, quiero mantener un inventario de procesos del GORE con su nivel de digitalización, para medir avance TDE | CRUD: proceso, division_id, nivel_digitalizacion (PAPEL/PARCIAL/DIGITAL/INTEROPERABLE), fecha_evaluacion, observaciones | MO DGI-TD-01 | Nuevo | P0 |
| D-DGI-TD-002 | Como ESP_TD, quiero identificar brechas entre el estado actual de digitalización y los requisitos TDE, para priorizar trabajo | Vista gap analysis: procesos con nivel < DIGITAL. Ordenados por criticidad y plazo normativo | MO DGI-TD-01 | Nuevo | P1 |
| D-DGI-TD-003 | Como ESP_TD, quiero proponer un roadmap de cumplimiento TDE con hitos y plazos, para planificar la transformación | CRUD roadmap: hito, fecha_objetivo, procesos_involucrados[], responsable_id, estado (PLANIFICADO/EN_CURSO/COMPLETADO/ATRASADO) | MO DGI-TD-01 | Nuevo | P1 |
| D-DGI-TD-004 | Como ESP_TD, quiero registrar el checklist de cumplimiento TDE por proceso (procedimiento documentado, firma electrónica, notificaciones, expediente, interoperabilidad, ClaveÚnica), para tracking granular | 6 items booleanos por proceso. Porcentaje de cumplimiento calculado | MO DGI-TD-01 | Nuevo | P1 |
| D-DGI-TD-005 | Como ESP_TD, quiero ver el estado de cumplimiento TDE en mi cockpit con barras de progreso por decreto, para monitoreo diario | Barras de progreso DS7-DS12 calculadas desde inventario real (no hardcoded) | MO DGI-TD-01 | Parcial | P0 |
| D-DGI-TD-006 | Como ESP_TD, quiero documentar evidencia de cumplimiento por proceso (resolución, acta, captura), para preparar auditorías | Tabla evidencia_tde: proceso_id, item_checklist, tipo_evidencia (RESOLUCION/ACTA/CAPTURA/INFORME), url, fecha | MO DGI-TD-01 | Nuevo | P2 |
| D-DGI-TD-007 | Como JEFE_DGI, quiero reportar el estado de avance TDE al Comité de TD, para cumplir mi rol de secretaría técnica | Vista resumen TDE: % cumplimiento global, por decreto, por división. Exportable | MO DGI-TD-01 | Nuevo | P1 |

### 3.2 Comité de Transformación Digital

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-TD-008 | Como ESP_TD, quiero preparar la tabla (agenda) de una sesión del Comité TD con temas, materiales y tiempos, para organizar la reunión | CRUD sesión comité: fecha, temas[], materiales_urls[], tiempo_estimado_min, estado (PROGRAMADA/EN_CURSO/FINALIZADA) | MO DGI-TD-02 | Parcial | P1 |
| D-DGI-TD-009 | Como ESP_TD, quiero elaborar actas del Comité TD con acuerdos, responsables y plazos, para formalizar decisiones | CRUD acta: sesion_id, acuerdos[{descripcion, responsable_id, plazo, estado}], asistentes[], observaciones | MO DGI-TD-02 | Nuevo | P1 |
| D-DGI-TD-010 | Como ESP_TD, quiero dar seguimiento a los acuerdos del Comité TD, para verificar cumplimiento | Vista acuerdos pendientes con semáforo de plazo. Filtro por sesión, responsable, estado | MO DGI-TD-02 | Nuevo | P1 |
| D-DGI-TD-011 | Como ESP_TD, quiero presentar el estado de avance TDE en cada sesión del Comité, para mantener informados a los miembros | Sección auto-populada en acta con indicadores TDE actuales | MO DGI-TD-02 | Nuevo | P2 |
| D-DGI-TD-012 | Como ESP_TD, quiero proponer iniciativas al Comité TD para decisión, para canalizar formalmente las propuestas | Tipo de agenda: PROPUESTA_INICIATIVA con campos impacto, recursos, plazo, riesgo. Decisión: APROBADA/RECHAZADA/PENDIENTE | MO DGI-TD-02 | Nuevo | P2 |
| D-DGI-TD-013 | Como ESP_TD, quiero evaluar factibilidad técnica de solicitudes al Comité, para asesorar decisiones | Formulario factibilidad: solicitud_id, complejidad, recursos_necesarios, plazo_estimado, riesgos, recomendacion | MO DGI-TD-02 | Nuevo | P3 |
| D-DGI-TD-014 | Como ESP_TD, quiero escalar impedimentos desde el Comité a AR cuando no se resuelven entre divisiones, para desbloquear proyectos | Workflow escalamiento: desde acuerdo BLOQUEADO → informe a AR con opciones | MO DGI-TD-02 | Nuevo | P2 |

### 3.3 Administración Funcional de Sistemas

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-TD-015 | Como ESP_TD, quiero mantener un inventario de sistemas del GORE con su dueño funcional y estado, para gestión de plataformas | CRUD sistema: nombre, descripción, dueño_funcional_id, estado (PRODUCCION/DESARROLLO/DEPRECADO), url, proveedor | MO DGI-TD-03 | Nuevo | P1 |
| D-DGI-TD-016 | Como ESP_TD, quiero definir requisitos funcionales para un sistema, para documentar lo que debe hacer | Tabla requisito_funcional: sistema_id, código, descripción, prioridad, estado (PENDIENTE/IMPLEMENTADO/DESCARTADO) | MO DGI-TD-03 | Nuevo | P2 |
| D-DGI-TD-017 | Como ESP_TD, quiero configurar reglas de negocio en sistemas de gestión, para que operen según normas institucionales | Registro de configuración: sistema_id, regla, valor, fecha_aplicacion, aplicado_por | MO DGI-TD-03 | Nuevo | P3 |
| D-DGI-TD-018 | Como ESP_TD, quiero registrar incidentes de negocio en sistemas (no técnicos), para tracking de problemas funcionales | CRUD incidente: sistema_id, descripción, impacto, reportado_por, estado (REPORTADO/EN_ANALISIS/RESUELTO), resolucion | MO DGI-TD-03 | Nuevo | P2 |
| D-DGI-TD-019 | Como ESP_TD, quiero ver las estadísticas de la Knowledge Base (artículos, consultas, actualizaciones) en mi cockpit con datos reales, para monitoreo | Calcular desde tablas reales: count artefactos, last_updated, consultas_periodo (requiere tracking de uso) | MO DGI-TD-03 | Parcial | P1 |

### 3.4 Interoperabilidad y Datos

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-TD-020 | Como ESP_TD, quiero mantener un inventario de conjuntos de datos críticos del GORE, para gestionar datos como activo | CRUD dataset: nombre, descripción, ubicacion, formato, dueño_datos_id, clasificacion (PUBLICO/INTERNO/CONFIDENCIAL) | MO DGI-TD-04 | Nuevo | P1 |
| D-DGI-TD-021 | Como ESP_TD, quiero definir la fuente autoritativa de cada dato, para implementar fuente única de verdad | Campo fuente_autoritativa en dataset. Flag is_master. Alertar si dato duplicado en otro sistema | MO DGI-TD-04 | Nuevo | P2 |
| D-DGI-TD-022 | Como ESP_TD, quiero definir estándares de calidad por conjunto de datos y monitorear cumplimiento, para asegurar data quality | Reglas: completitud_min%, formato_esperado, rango_valido. Monitoreo periódico con resultado (CUMPLE/NO_CUMPLE/PARCIAL) | MO DGI-TD-04 | Nuevo | P2 |
| D-DGI-TD-023 | Como ESP_TD, quiero especificar necesidades de integración entre sistemas, para planificar interoperabilidad | CRUD integracion: sistema_origen, sistema_destino, datos_intercambiados, frecuencia, protocolo (API/ARCHIVO/BD), estado | MO DGI-TD-04 | Nuevo | P2 |
| D-DGI-TD-024 | Como ESP_TD, quiero integrar datos desde SIGFE para alimentar indicadores presupuestarios, para automatizar la fuente de datos | Conector SIGFE → budget_program. Mapeo de campos. Ejecución programada | MO DGI-TD-04 | Externo | P1 |
| D-DGI-TD-025 | Como ESP_TD, quiero integrar datos desde BIP para sincronizar estado de IPRs, para fuente única de verdad en cartera | Conector BIP → core.ipr. Mapeo codigo_bip → estado. Ejecución programada | MO DGI-TD-04 | Externo | P1 |
| D-DGI-TD-026 | Como ESP_TD, quiero integrar datos desde PISEE para estado de documentos electrónicos, para cumplimiento TDE | Conector PISEE → documentos. Verificar firma electrónica, expediente | MO DGI-TD-04 | Externo | P1 |
| D-DGI-TD-027 | Como ESP_TD, quiero integrar datos desde CGR para estado de actos administrativos (toma de razón), para automatizar seguimiento | Conector CGR → administrative_act. Actualizar estado post-envío | MO DGI-TD-04 | Externo | P1 |

### 3.5 Cumplimiento Normativo

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-TD-028 | Como ESP_TD, quiero ver alertas normativas reales sobre plazos de cumplimiento TDE, para anticipar riesgos regulatorios | Reemplazar datos hardcoded en cockpit TD por alertas calculadas desde roadmap TDE + plazos normativos | MO DGI-TD-01 | Parcial | P1 |
| D-DGI-TD-029 | Como ESP_TD, quiero registrar el cumplimiento de la Resolución 22/2023 (normas técnicas de interoperabilidad), para evidencia PMG | Checklist resolución 22: items normativos con estado de cumplimiento por sistema | MO DGI-GEN-04 | Nuevo | P2 |
| D-DGI-TD-030 | Como ESP_TD, quiero trackear el cumplimiento del PMG con hitos y evidencia, para evaluación institucional | Tabla pmg_hito: compromiso, meta, indicador, evidencia_url, estado, periodo | MO DGI-GEN-04 | Nuevo | P2 |

### 3.6 Productos Especialista TD (Catálogo)

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-TD-031 | Como ESP_TD, quiero registrar artefactos de conocimiento estructurado como producto DGI, para catálogo de entregables | Tipo artefacto: CONOCIMIENTO_ESTRUCTURADO vinculado a KB | PP POT-ARQ-02 | Nuevo | P3 |
| D-DGI-TD-032 | Como ESP_TD, quiero registrar agentes IA configurados como producto DGI, para inventario de activos digitales | Tipo artefacto: AGENTE_IA con campos propósito, fuentes, estado, métricas de uso | PP POT-ARQ-02 | Nuevo | P3 |
| D-DGI-TD-033 | Como ESP_TD, quiero registrar integraciones entre sistemas implementadas como producto DGI, para inventario técnico | Tipo artefacto: INTEGRACION con sistemas origen/destino, protocolo, SLA | PP POT-ARQ-02 | Nuevo | P3 |
| D-DGI-TD-034 | Como ESP_TD, quiero autenticar usuarios con ClaveÚnica, para cumplir Ley 21.180 en trámites ciudadanos | Integración OAuth2 con ClaveÚnica. Mapeo RUT → core.user | MO DGI-TD-01 | Externo | P1 |
| D-DGI-TD-035 | Como ESP_TD, quiero ver la velocidad de avance TDE (procesos digitalizados/mes) con datos reales, para medir ritmo | Calcular desde inventario: delta procesos DIGITAL entre periodos. Reemplazar velocity hardcoded | MO DGI-TD-01 | Parcial | P1 |

---

## 4. D-DGI-KC — Gestión del Conocimiento

> Fuente: MO DGI-KC-01..03, PP POT-DMAIC-02 (5S), PP POT-ARQ-02 (EngineersTD)

### 4.1 Curación de Knowledge Base

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-KC-001 | Como ESP_TD, quiero registrar un artefacto de conocimiento con metadatos (URN, categoría, autor, vigencia), para mantener catálogo maestro | CRUD artefacto_kb: urn, titulo, descripcion, categoria, autor_id, vigencia (VIGENTE/EN_REVISION/DEPRECADO), fecha_vigencia | MO DGI-KC-01 | Nuevo | P1 |
| D-DGI-KC-002 | Como ESP_TD, quiero clasificar artefactos por taxonomía institucional, para organización consistente | Categorías: NORMATIVO, PROCEDIMENTAL, TECNICO, CAPACITACION, REFERENCIA. Sub-categorías por dominio | MO DGI-KC-01 | Nuevo | P2 |
| D-DGI-KC-003 | Como ESP_TD, quiero vincular artefactos relacionados entre sí, para navegación contextual | Tabla artefacto_relacion: artefacto_a_id, artefacto_b_id, tipo_relacion (REQUIERE/COMPLEMENTA/REEMPLAZA/VERSIONA) | MO DGI-KC-01 | Nuevo | P2 |
| D-DGI-KC-004 | Como ESP_TD, quiero enviar un artefacto a validación por un experto de dominio antes de publicar, para asegurar exactitud | Workflow: BORRADOR → EN_VALIDACION → APROBADO → PUBLICADO. Asignar validador (persona de la división experta) | MO DGI-KC-01 | Nuevo | P2 |
| D-DGI-KC-005 | Como ESP_TD, quiero revisar periódicamente la vigencia de artefactos y deprecar los obsoletos, para mantener calidad | Vista "próximos a vencer": artefactos con fecha_vigencia < 30d. Acción: renovar o deprecar | MO DGI-KC-01 | Nuevo | P2 |
| D-DGI-KC-006 | Como ESP_TD, quiero recibir alertas cuando un cambio normativo afecta artefactos de la KB, para actualización proactiva | Vincular artefacto a norma. Cuando se registra cambio normativo → alerta al curador | MO DGI-KC-01 | Nuevo | P3 |
| D-DGI-KC-007 | Como ESP_TD, quiero ver estadísticas de uso de la KB (artefactos más consultados, búsquedas sin resultado), para priorizar curación | Tracking: consultas por artefacto, búsquedas, feedback. Dashboard de uso | MO DGI-KC-01 | Nuevo | P2 |
| D-DGI-KC-008 | Como JEFE_DGI, quiero ver un panel de estado de la KB con total artefactos, vigentes, en revisión y deprecados, para monitorear salud | Resumen: counts por estado, tasa de actualización, antigüedad promedio | MO DGI-KC-01 | Parcial | P1 |

### 4.2 Sistema 5S para Conocimiento

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-KC-009 | Como ESP_TD, quiero auditar artefactos existentes clasificándolos por utilidad (necesario/ocasional/obsoleto), para Seiri (Clasificar) | Campo utilidad en artefacto. Vista de auditoría con filtro por clasificación | PP POT-DMAIC-02 | Nuevo | P2 |
| D-DGI-KC-010 | Como ESP_TD, quiero asegurar que todos los artefactos tengan URN consistente y taxonomía clara, para Seiton (Ordenar) | Validación automática de formato URN. Reporte de artefactos sin categoría | PP POT-DMAIC-02 | Nuevo | P3 |
| D-DGI-KC-011 | Como ESP_TD, quiero ejecutar una revisión periódica de vigencia de todos los artefactos, para Seiso (Limpiar) | Job programado: artefactos sin actualización en >6 meses → flag REVISAR. Dashboard de limpieza | PP POT-DMAIC-02 | Nuevo | P3 |
| D-DGI-KC-012 | Como ESP_TD, quiero aplicar plantillas estándar a todos los artefactos nuevos, para Seiketsu (Estandarizar) | Templates por tipo de artefacto. Validación de campos obligatorios según template | PP POT-DMAIC-02 | Nuevo | P3 |
| D-DGI-KC-013 | Como JEFE_DGI, quiero ver métricas de disciplina 5S (artefactos sin URN, sin categoría, vencidos), para Shitsuke (Disciplina) | Dashboard 5S: indicadores de salud de KB con semáforo | PP POT-DMAIC-02 | Nuevo | P3 |

### 4.3 Gestión de Agentes IA

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-KC-014 | Como ESP_TD, quiero registrar un agente IA institucional con propósito, alcance, fuentes y límites de actuación, para inventario | CRUD agente_ia: nombre, propósito, alcance, fuentes_kb[], limites, dueño_funcional_id, estado (DISEÑO/DESARROLLO/PRODUCCION/RETIRADO) | MO DGI-KC-02 | Nuevo | P1 |
| D-DGI-KC-015 | Como ESP_TD, quiero monitorear interacciones de un agente IA (consultas, respuestas inadecuadas), para calidad | Log de interacciones: query, response, feedback_usuario (util/no_util/inadecuado), timestamp | MO DGI-KC-02 | Nuevo | P2 |
| D-DGI-KC-016 | Como ESP_TD, quiero gestionar el ciclo de vida de un agente IA (diseño → desarrollo → despliegue → operación → evolución), para control | FSM: DISEÑO → DESARROLLO → TESTING → PRODUCCION → RETIRADO. Transiciones con validación | MO DGI-KC-02 | Nuevo | P2 |
| D-DGI-KC-017 | Como ESP_TD, quiero que todo agente IA tenga un dueño funcional y respuestas auditables, para governance | FK dueño_funcional_id obligatorio. Log de respuestas retenido 90d | MO DGI-KC-02 | Nuevo | P2 |
| D-DGI-KC-018 | Como ESP_TD, quiero evaluar la efectividad de un agente IA (tasa de respuestas útiles, reducción de consultas manuales), para justificar inversión | Métricas calculadas: util_rate = feedback_util / total, manual_reduction = consultas_pre - consultas_post | MO DGI-KC-02 | Nuevo | P3 |

### 4.4 Capacitación y Gestión del Cambio

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-KC-019 | Como ESP_TD, quiero planificar una capacitación con audiencia, objetivos, materiales y fecha, para coordinar formación | CRUD capacitacion: titulo, audiencia (roles/divisiones), objetivos[], materiales_urls[], fecha, duracion_hrs, estado | MO DGI-KC-03 | Nuevo | P1 |
| D-DGI-KC-020 | Como ESP_TD, quiero registrar asistencia y evaluación de una capacitación, para medir efectividad | Tabla asistencia: capacitacion_id, persona_id, asistio (bool), evaluacion_score (1-5), comentario | MO DGI-KC-03 | Nuevo | P2 |
| D-DGI-KC-021 | Como ESP_TD, quiero gestionar un proceso de cambio con las 5 fases (preparación, comunicación, capacitación, acompañamiento, consolidación), para tracking estructurado | CRUD cambio: nombre, descripción, division_afectada_id, fase_actual (PREPARACION/COMUNICACION/CAPACITACION/ACOMPAÑAMIENTO/CONSOLIDACION), responsable_id | MO DGI-KC-03 | Nuevo | P2 |
| D-DGI-KC-022 | Como ESP_TD, quiero identificar y registrar resistencias al cambio detectadas, para gestionarlas | Tabla resistencia: cambio_id, tipo (RACIONAL/EMOCIONAL/POLITICA), descripción, persona/grupo, estado (DETECTADA/EN_GESTION/RESUELTA) | MO DGI-KC-03 | Nuevo | P2 |
| D-DGI-KC-023 | Como JEFE_DGI, quiero ver un resumen de capacitaciones realizadas (asistencia, evaluación promedio), para reportar a AR | Dashboard: capacitaciones por período, asistencia total, NPS promedio | MO DGI-KC-03 | Nuevo | P2 |
| D-DGI-KC-024 | Como ESP_TD, quiero comunicar beneficios de un cambio a cada stakeholder según sus intereses, para facilitar adopción | Template de comunicación por rol: JEFE_DIVISION → eficiencia, ENCARGADO → facilidad, AR → cumplimiento | MO DGI-KC-03 | Nuevo | P3 |
| D-DGI-KC-025 | Como ESP_TD, quiero proveer materiales de apoyo accesibles a los usuarios durante y después de una capacitación, para reforzar aprendizaje | Sección materiales en detalle de capacitación. Links a artefactos KB relevantes | MO DGI-KC-03 | Nuevo | P3 |
| D-DGI-KC-026 | Como JEFE_DGI, quiero ver el estado de adopción de cambios implementados (% usuarios activos, frecuencia de uso), para medir consolidación | Métricas de adopción: logins post-cambio, features usadas, feedback. Por división | MO DGI-KC-03 | Nuevo | P3 |
| D-DGI-KC-027 | Como ESP_TD, quiero documentar lecciones aprendidas de cada proceso de cambio, para mejorar futuras implementaciones | Campo lecciones_aprendidas al cerrar un cambio en fase CONSOLIDACION | MO DGI-KC-03 | Nuevo | P3 |
| D-DGI-KC-028 | Como ESP_TD, quiero que los usuarios sepan claramente cuando interactúan con IA vs. persona, para transparencia | Badge "Asistente IA" visible en interfaces de agentes. Disclaimer en respuestas | MO DGI-KC-02 | Parcial | P2 |

---

## 5. D-DGI-CI — Coordinación Institucional

> Fuente: MO DGI-CI-01..04, PP POT-SOC-02 (stakeholder map)

### 5.1 Relación con AR

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CI-001 | Como JEFE_DGI, quiero preparar la reunión semanal con AR incluyendo estado de iniciativas, alertas y decisiones pendientes, para coordinación efectiva | Vista "Prep AR": auto-poblada con iniciativas activas, alertas top, decisiones sin resolver, prioridades sugeridas | MO DGI-CI-01 | Parcial | P1 |
| D-DGI-CI-002 | Como JEFE_DGI, quiero registrar decisiones tomadas en la reunión con AR, para trazabilidad | CRUD decision_ar: fecha, descripción, tipo (PRIORIDAD/RECURSO/ESCALAMIENTO/ESTRATEGIA), estado (PENDIENTE/EN_EJECUCION/COMPLETADA) | MO DGI-CI-01 | Nuevo | P1 |
| D-DGI-CI-003 | Como JEFE_DGI, quiero dar seguimiento a decisiones de AR con estado y plazo, para cumplimiento | Vista decisiones pendientes con semáforo de plazo. Alerta si vencida | MO DGI-CI-01 | Nuevo | P1 |
| D-DGI-CI-004 | Como JEFE_DGI, quiero escalar temas a AR mediante Informe Ejecutivo con opciones y recomendación, para decisiones formales | Template escalamiento: problema, impacto, opciones[], recomendación, plazo_decisión. Genera informe FLASH | MO DGI-CI-01 | Parcial | P1 |

### 5.2 Interacción con Divisiones

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CI-005 | Como JEFE_DGI, quiero ver una matriz de interacciones con divisiones (tipo, frecuencia, próxima reunión), para gestionar relaciones | Vista matriz: 7+ divisiones × tipo interacción × frecuencia × última interacción × próxima programada | MO DGI-CI-02 | Nuevo | P2 |
| D-DGI-CI-006 | Como ESP_CONTROL_GESTION, quiero registrar interacciones con la DAF (indicadores presupuestarios, rendiciones), para tracking semanal | Log interaccion: division_id, tipo, fecha, participantes[], temas[], acuerdos[], próxima_fecha | MO DGI-CI-02 | Nuevo | P2 |
| D-DGI-CI-007 | Como ESP_CONTROL_GESTION, quiero registrar interacciones con DIPIR (cartera IPR, avances), para tracking semanal | Mismo modelo de log interacción | MO DGI-CI-02 | Nuevo | P2 |
| D-DGI-CI-008 | Como JEFE_DGI, quiero registrar interacciones con Jurídica (convenios, resoluciones), para tracking quincenal | Mismo modelo de log interacción | MO DGI-CI-02 | Nuevo | P2 |
| D-DGI-CI-009 | Como ESP_TD, quiero registrar interacciones con Unidad de Operaciones (sistemas, interoperabilidad), para tracking mensual | Mismo modelo de log interacción | MO DGI-CI-02 | Nuevo | P2 |
| D-DGI-CI-010 | Como JEFE_DGI, quiero ver acuerdos pendientes con divisiones y su estado de cumplimiento, para follow-up | Filtro acuerdos: division_id, estado, vencimiento | MO DGI-CI-02 | Nuevo | P2 |

### 5.3 Protocolo de Escalamiento

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CI-011 | Como ESP_CONTROL_GESTION, quiero crear un escalamiento nivel 1 (incidente operativo) al Jefe DGI con plazo de 4 horas, para resolver rápido | CRUD escalamiento: nivel (1-4), situacion, impacto, opciones[], recomendacion, plazo, firma_responsable, estado | MO DGI-CI-03 | Nuevo | P1 |
| D-DGI-CI-012 | Como JEFE_DGI, quiero crear un escalamiento nivel 2 (bloqueo de proyecto) a AR con plazo de 24 horas, para desbloquear | Nivel 2: escala_a = AR. Información requerida completa | MO DGI-CI-03 | Nuevo | P1 |
| D-DGI-CI-013 | Como JEFE_DGI, quiero crear un escalamiento nivel 3 (conflicto entre divisiones) a AR con plazo de 48 horas, para mediación | Nivel 3: involucra múltiples divisiones. escala_a = AR | MO DGI-CI-03 | Nuevo | P2 |
| D-DGI-CI-014 | Como JEFE_DGI, quiero crear un escalamiento nivel 4 (decisión estratégica) al Gobernador vía AR, para definiciones de alto nivel | Nivel 4: escala_a = GOBERNADOR. Plazo según urgencia | MO DGI-CI-03 | Nuevo | P2 |
| D-DGI-CI-015 | Como JEFE_DGI, quiero ver todos los escalamientos activos con su nivel, plazo y estado, para priorizar resolución | Vista escalamientos filtrable por nivel, estado, plazo. Semáforo de vencimiento | MO DGI-CI-03 | Nuevo | P1 |

### 5.4 Comités

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CI-016 | Como ESP_TD, quiero gestionar sesiones del Comité de TD (preparar, ejecutar, cerrar), para secretaría técnica | Reutilizar core.session con committee COMITE-TD. Tabla + materiales + acta | MO DGI-CI-04 | Parcial | P1 |
| D-DGI-CI-017 | Como JEFE_DGI, quiero participar como informante en el Comité de Coordinación Regional, para visibilidad | Consulta de sesiones de COMITE-COORD-REGIONAL. Solo lectura para DGI | MO DGI-CI-04 | Nuevo | P3 |
| D-DGI-CI-018 | Como ESP_PROCESOS, quiero facilitar mesas de trabajo temáticas con registro de participantes y acuerdos, para articulación | CRUD mesa_trabajo: tema, participantes[], acuerdos[], fecha, estado | MO DGI-CI-04 | Nuevo | P2 |
| D-DGI-CI-019 | Como JEFE_DGI, quiero ver un calendario consolidado de todas las reuniones DGI (AR semanal, divisiones, comités), para planificación | Vista calendario: reuniones programadas por tipo, con enlaces a preparación | MO DGI-CI-01 | Nuevo | P2 |

### 5.5 Catálogo de Servicios DGI

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-CI-020 | Como JEFE_DGI, quiero publicar un catálogo de servicios DGI con productos, SLAs y cómo solicitarlos, para transparencia | Página pública interna: servicios por área (CG, MP, TD, KC), con descripción, SLA, cómo solicitar | PP POT-ARQ-03 | Nuevo | P1 |
| D-DGI-CI-021 | Como JEFE_DIVISION, quiero solicitar un servicio DGI formalmente (ej: levantamiento de proceso), para canalizar pedidos | Formulario solicitud: servicio_id, descripción_necesidad, urgencia, division_id. Estado: RECIBIDA → EN_EVALUACION → ACEPTADA → EN_EJECUCION → COMPLETADA | PP POT-ARQ-03 | Nuevo | P1 |
| D-DGI-CI-022 | Como JEFE_DGI, quiero recibir feedback estructurado post-entrega de un servicio, para mejora continua | Encuesta post-servicio: satisfacción (1-5), utilidad, sugerencias. Alimenta NPS interno | PP POT-ARQ-03 | Nuevo | P2 |

---

## 6. D-DGI-POT — Potenciamiento (Meyer / DMAIC / Social)

> Fuente: PP POT-SYN, POT-ARQ, POT-SOC, POT-CM

### 6.1 Arquitectura Organizacional (Meyer)

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-POT-001 | Como JEFE_DGI, quiero ver la estructura del DGI como Building Blocks (Engineers, Service Providers, Coordinators) con roles asignados, para claridad organizacional | Vista org chart: 4 bloques con roles asignados, productos, clientes internos | PP POT-ARQ-01 | Nuevo | P3 |
| D-DGI-POT-002 | Como JEFE_DGI, quiero verificar que cada rol DGI tenga dominios precisos sin superposiciones, para evitar conflictos | Matriz RACI visible: actividades × roles con R/A/C/I. Alertar si hay duplicación de R | PP POT-ARQ-01 | Nuevo | P3 |
| D-DGI-POT-003 | Como JEFE_DGI, quiero ver la relación cliente-proveedor del DGI con cada división (qué les entregamos, feedback recibido), para gestionar relaciones | Dashboard relacional: división → servicios solicitados → satisfacción → pendientes | PP POT-ARQ-03 | Nuevo | P2 |

### 6.2 Navegación Social

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-POT-004 | Como JEFE_DGI, quiero mantener un mapa de stakeholders con poder, interés DGI y estrategia, para gestión política | CRUD stakeholder: actor, nivel (ESTRATEGICO/TACTICO/OPERATIVO), poder (ALTO/MEDIO/BAJO), interes_dgi, estrategia, última_interacción | PP POT-SOC-02 | Nuevo | P1 |
| D-DGI-POT-005 | Como JEFE_DGI, quiero registrar el estado ADKAR de cada stakeholder por iniciativa, para tracking de adopción | Tabla adkar_tracking: stakeholder_id, iniciativa_id, awareness (1-5), desire (1-5), knowledge (1-5), ability (1-5), reinforcement (1-5), fecha_evaluacion | PP POT-SOC-03 | Nuevo | P2 |
| D-DGI-POT-006 | Como JEFE_DGI, quiero seleccionar tácticas de influencia apropiadas por stakeholder, para planificar comunicación | Catálogo de tácticas: reciprocidad, prueba social, autoridad, escasez, consistencia, simpatía. Vincular a stakeholder con notas | PP POT-SOC-04 | Nuevo | P3 |
| D-DGI-POT-007 | Como JEFE_DGI, quiero detectar y clasificar resistencias al cambio (racional, emocional, política), para respuesta diferenciada | Tipo de resistencia en registro. Protocolo sugerido por tipo (6 pasos) | PP POT-SOC-05 | Nuevo | P2 |
| D-DGI-POT-008 | Como JEFE_DGI, quiero identificar "campeones" en cada división que apoyan al DGI, para construir red de embajadores | Campo embajador (bool) en stakeholder. Meta: 1 por división. Dashboard red de embajadores | PP POT-SOC-02 | Nuevo | P2 |

### 6.3 Métricas de Éxito Social

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-POT-009 | Como JEFE_DGI, quiero medir el NPS interno del DGI (encuesta trimestral a divisiones), para evaluar percepción | Encuesta periódica: ¿Recomendarías los servicios del DGI? (0-10). Cálculo NPS. Meta >50 | PP POT-SOC-06 | Nuevo | P1 |
| D-DGI-POT-010 | Como JEFE_DGI, quiero medir la tasa de adopción voluntaria (% divisiones que solicitan servicios), para evaluar demanda | Cálculo: divisiones con ≥1 solicitud en período / total divisiones. Meta >70% | PP POT-SOC-06 | Nuevo | P2 |
| D-DGI-POT-011 | Como JEFE_DGI, quiero medir el tiempo promedio de respuesta a solicitudes, para evaluar agilidad | Cálculo: promedio(fecha_primera_respuesta - fecha_solicitud). Meta <48h | PP POT-SOC-06 | Nuevo | P2 |
| D-DGI-POT-012 | Como JEFE_DGI, quiero medir proyectos completados sin escalamiento a AR, para evaluar autonomía | Cálculo: iniciativas completadas sin escalamiento / total completadas. Meta >80% | PP POT-SOC-06 | Nuevo | P2 |
| D-DGI-POT-013 | Como JEFE_DGI, quiero medir la red de embajadores (1 por división), para evaluar penetración social | Count embajadores activos por división vs. total divisiones | PP POT-SOC-06 | Nuevo | P3 |

### 6.4 Dinámica de Producción (Lean/Kanban)

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-POT-014 | Como ESP_PROCESOS, quiero visualizar el flujo de trabajo del equipo DGI en tablero Kanban, para transparencia | Tablero Kanban con columnas BACKLOG/EN_DISEÑO/EN_IMPLEMENTACION/EN_VERIFICACION/COMPLETADO | PP POT-EF-02 | Implementado | — |
| D-DGI-POT-015 | Como JEFE_DGI, quiero ver WIP limits por columna para evitar sobrecarga, para flujo saludable | Topes fijos retirados en C62 tras prueba manual; el conteo WIP permanece como métrica informativa, sin bloqueo 409 | PP POT-DMAIC-04 | Retirado C62 | — |
| D-DGI-POT-016 | Como JEFE_DGI, quiero ver métricas Lean del equipo (throughput, lead time, cycle time), para optimizar flujo | Cálculo: throughput = iniciativas completadas/mes, lead_time = promedio(completada - creada), cycle_time = promedio(tiempo en columna). Dashboard | PP POT-EF-02 | Nuevo | P1 |
| D-DGI-POT-017 | Como JEFE_DGI, quiero ver un CFD (Cumulative Flow Diagram) de iniciativas, para detectar cuellos de botella | Gráfico de áreas apiladas: count iniciativas por estado a lo largo del tiempo | PP POT-EF-02 | Nuevo | P2 |
| D-DGI-POT-018 | Como ESP_PROCESOS, quiero ver el aging de items en cada columna Kanban (días), para detectar bloqueos | Badge con días en columna actual. Alerta si > promedio × 1.5 | PP POT-EF-02 | Nuevo | P2 |

### 6.5 SLAs por Producto

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-POT-019 | Como JEFE_DGI, quiero definir SLAs por tipo de producto DGI (ej: informe semanal = entrega viernes 18:00), para compromiso de servicio | CRUD sla: producto_tipo, descripcion, plazo_dias/hora, prioridad, aplica_a (divisiones) | PP POT-ARQ-03 | Nuevo | P1 |
| D-DGI-POT-020 | Como JEFE_DGI, quiero monitorear el cumplimiento de SLAs por producto, para gestión de calidad | Dashboard SLA: producto × cumplimiento % × promedio dias × breaches. Meta >90% | PP POT-ARQ-03 | Nuevo | P1 |
| D-DGI-POT-021 | Como JEFE_DIVISION, quiero ver los SLAs comprometidos por el DGI para mi división, para expectativas claras | Vista divisional: mis servicios contratados + SLA + estado actual | PP POT-ARQ-03 | Nuevo | P2 |

### 6.6 Plan de Trabajo y Priorización

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-POT-022 | Como JEFE_DGI, quiero crear un plan de trabajo consensuado con prioridades y recursos, para alinear equipo | CRUD plan: periodo, objetivos[], iniciativas_priorizadas[], recursos_asignados, aprobado_por_ar (bool) | PP POT-ARQ-02 | Nuevo | P1 |
| D-DGI-POT-023 | Como JEFE_DGI, quiero priorizar iniciativas con criterios explícitos (impacto, urgencia, esfuerzo, alineamiento ERD), para decisiones transparentes | Scoring: impacto(1-5) × urgencia(1-5) / esfuerzo(1-5). Bonus si alineado a ERD. Ranking automático | PP POT-ARQ-02 | Nuevo | P2 |
| D-DGI-POT-024 | Como JEFE_DGI, quiero comunicar al equipo el plan y prioridades para el próximo período, para claridad | Vista plan vigente visible para todo el equipo DGI. Notificación de cambios | PP POT-ARQ-02 | Nuevo | P2 |

### 6.7 Resolución de Conflictos y Facilitación

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-POT-025 | Como JEFE_DGI, quiero registrar conflictos entre divisiones que afectan iniciativas DGI, para gestión estructurada | CRUD conflicto: divisiones_involucradas[], iniciativa_id, descripción, estado (DETECTADO/EN_MEDIACION/RESUELTO/ESCALADO) | PP POT-ARQ-02 | Nuevo | P2 |
| D-DGI-POT-026 | Como JEFE_DGI, quiero comunicar éxitos y valor generado por el DGI a las divisiones, para legitimidad | Template comunicación: logro, impacto cuantificado, división beneficiada. Registro de comunicaciones enviadas | PP POT-SOC-01 | Nuevo | P3 |

### 6.8 Proyecto Piloto DMAIC

| ID | Historia | CA | Fuente | Estado | P |
|----|----------|----|--------|:------:|:-:|
| D-DGI-POT-027 | Como ESP_PROCESOS, quiero ejecutar un proyecto piloto DMAIC sobre el flujo de visación de actos administrativos, para demostrar la metodología | Iniciativa con charter: reducir tiempo visación 30%. Fases D-M-A-I-C completas con datos reales de actos admin | PP POT-DMAIC-03 | Nuevo | P2 |
| D-DGI-POT-028 | Como ESP_PROCESOS, quiero medir tiempos de ciclo por etapa del flujo de visación, para la fase Measure | Query: promedio días por estado en administrative_act (BORRADOR→...→TOMADO_RAZON). VSM desde datos reales | PP POT-DMAIC-03 | Implementado | — |
| D-DGI-POT-029 | Como ESP_PROCESOS, quiero identificar etapas con mayor tiempo de espera en visación, para la fase Analyze | Ranking de estados por tiempo promedio. Identificar ENVIADO_CGR y EN_REVISION como cuellos de botella | PP POT-DMAIC-03 | Implementado | — |
| D-DGI-POT-030 | Como ESP_PROCESOS, quiero configurar alertas de SLA por etapa de visación, para la fase Control | Reglas de alerta por estado: EN_REVISION >3d → alerta. ENVIADO_CGR >30d → alerta | PP POT-DMAIC-03 | Parcial | P1 |

---

## Apéndice A: Matriz de Cruce con Implementación Actual

### Endpoints DGI existentes → Stories que cubren

| Endpoint | Stories cubiertas |
|----------|-------------------|
| `GET /api/dgi/cockpit` | D-DGI-CG-013, 014, 015, 038 |
| `POST /api/dgi/data/indicators/refresh` | D-DGI-CG-007 |
| `GET /api/dgi/data/indicators` | D-DGI-CG-005, 010 |
| `GET /api/dgi/initiatives` | D-DGI-MP-021, D-DGI-POT-014 |
| `POST /api/dgi/initiatives` | D-DGI-MP-021 |
| `POST /api/dgi/initiatives/{id}/move` | D-DGI-POT-015 |
| `GET /api/dgi/reports` | D-DGI-CG-031 |
| `POST /api/dgi/reports` | D-DGI-CG-024, 025, 027, 028 |
| `GET /api/dgi/reports/{id}/content` | D-DGI-CG-024 |
| `PATCH /api/dgi/reports/{id}` | D-DGI-CG-029 |
| `POST /api/dgi/reports/{id}/status` | D-DGI-CG-026 |
| `GET /api/dgi/cartera` | D-DGI-CG-032, 033 |
| `GET /api/dgi/cartera/resumen` | D-DGI-CG-032 |
| `GET /api/dgi/data/rendiciones` | (SISREC, no DGI-specific) |
| `POST /api/dgi/data/rendiciones/check-escalations` | D-DGI-CG-011 (parcial) |

### Cockpit hardcoded → Stories que reemplazarían

| Dato hardcoded | Cockpit | Story que lo reemplaza |
|----------------|---------|------------------------|
| TDE compliance bars | ESP_TD | D-DGI-TD-005 |
| DS7-DS12 decrees checklist | ESP_TD | D-DGI-TD-004 |
| KB stats (Pendientes/Actualizados/Total) | ESP_TD | D-DGI-KC-008, D-DGI-TD-019 |
| BPMN models count | ESP_PROCESOS | D-DGI-MP-009, 010 |
| Today agenda | ESP_PROCESOS | D-DGI-CI-019 |
| Normative alerts | ESP_TD | D-DGI-TD-028 |
| Velocity (3/5) | ESP_TD | D-DGI-TD-035 |

---

## Apéndice B: Priorización Sugerida por Waves

### Wave A — Reemplazar hardcoded + Core CG (P0-P1, ~25 stories)

Objetivo: Que los 4 cockpits muestren datos 100% reales.

1. D-DGI-TD-001 (inventario TDE) → D-DGI-TD-004 (checklist) → D-DGI-TD-005 (cockpit real)
2. D-DGI-CG-001..002 (ficha indicador editable) → D-DGI-CG-008 (TDE dinámico)
3. D-DGI-MP-001, 009 (inventario procesos) → D-DGI-MP-002 (BPMN) → cockpit procesos real
4. D-DGI-KC-001, 008 (catálogo KB) → D-DGI-TD-019 (KB stats real)
5. D-DGI-CG-011 (alertas persistentes) → D-DGI-CG-037 (reglas configurables)
6. D-DGI-TD-028 (alertas normativas reales) → D-DGI-TD-035 (velocity real)

### Wave B — Coordinación + Servicios (P1, ~20 stories)

Objetivo: Formalizar relaciones DGI ↔ divisiones ↔ AR.

1. D-DGI-CI-020..022 (catálogo servicios + solicitudes + feedback)
2. D-DGI-CI-001..004 (relación AR + decisiones)
3. D-DGI-CI-011..015 (escalamientos)
4. D-DGI-POT-004 (stakeholder map)
5. D-DGI-POT-019..021 (SLAs)

### Wave C — Procesos + DMAIC (P1-P2, ~20 stories)

Objetivo: Capacidad completa de mejora de procesos.

1. D-DGI-MP-003..008 (detalle proceso: actores, reglas, métricas, pain points)
2. D-DGI-MP-011..015 (análisis mejora + priorización)
3. D-DGI-MP-023..027 (DMAIC structured)
4. D-DGI-POT-016..018 (métricas Lean)

### Wave D — KC + Cambio + Social (P2-P3, ~30 stories)

Objetivo: Gestión de conocimiento y cambio organizacional.

1. D-DGI-KC-001..008 (KB completa)
2. D-DGI-KC-014..018 (agentes IA)
3. D-DGI-KC-019..027 (capacitación + cambio)
4. D-DGI-POT-005..013 (social metrics, ADKAR, NPS)

### Wave E — Integraciones externas (Externo, 7 stories)

Requiere APIs de terceros.

1. D-DGI-TD-024 (SIGFE)
2. D-DGI-TD-025 (BIP)
3. D-DGI-TD-026 (PISEE)
4. D-DGI-TD-027 (CGR)
5. D-DGI-TD-034 (ClaveÚnica)
6. D-DGI-CG-036 (email)

---

## Apéndice C: Tablas de BD Nuevas Estimadas

| Tabla propuesta | Stories | Esquema |
|-----------------|---------|---------|
| `core.dgi_indicator_definition` | CG-001..006 | Ficha formal de indicador con workflow |
| `core.tde_process_inventory` | TD-001..007 | Inventario procesos + checklist TDE |
| `core.tde_roadmap_milestone` | TD-003 | Hitos roadmap TDE |
| `core.tde_evidence` | TD-006 | Evidencia de cumplimiento |
| `core.comite_td_session` | TD-008..014 | Sesiones + actas + acuerdos Comité TD |
| `core.process_catalog` | MP-001..010 | Inventario procesos institucionales |
| `core.process_actor` | MP-003 | Actores/sistemas por proceso |
| `core.process_rule` | MP-004 | Reglas de negocio por proceso |
| `core.process_metric` | MP-005 | Métricas base y post-mejora |
| `core.process_pain_point` | MP-006 | Puntos de dolor |
| `core.improvement_opportunity` | MP-011..015 | Oportunidades de mejora priorizadas |
| `core.dmaic_section` | MP-023..027 | Secciones D-M-A-I-C por iniciativa |
| `core.kb_artifact` | KC-001..013 | Artefactos de conocimiento |
| `core.kb_artifact_relation` | KC-003 | Relaciones entre artefactos |
| `core.ai_agent` | KC-014..018 | Inventario agentes IA |
| `core.ai_agent_interaction` | KC-015 | Log de interacciones |
| `core.training` | KC-019..020 | Capacitaciones + asistencia |
| `core.change_process` | KC-021..027 | Procesos de cambio + resistencias |
| `core.dgi_decision` | CI-002..003 | Decisiones AR |
| `core.division_interaction` | CI-005..010 | Log interacciones con divisiones |
| `core.escalation_dgi` | CI-011..015 | Escalamientos formales |
| `core.service_catalog` | CI-020 | Catálogo servicios DGI |
| `core.service_request` | CI-021..022 | Solicitudes + feedback |
| `core.stakeholder_map` | POT-004..008 | Mapa stakeholders + ADKAR |
| `core.dgi_sla` | POT-019..021 | SLAs por producto |
| `core.dgi_work_plan` | POT-022..024 | Planes de trabajo |
| `core.dgi_conflict` | POT-025 | Conflictos entre divisiones |
| `core.nps_survey` | POT-009 | Encuestas NPS |
| `core.system_inventory` | TD-015..018 | Inventario sistemas |
| `core.dataset_inventory` | TD-020..023 | Inventario datos |
| `core.alert_rule` | CG-037 | Reglas de alerta configurables |
| `core.bottleneck_investigation` | CG-021..023 | Investigaciones de cuellos de botella |

**Total nuevas tablas estimadas**: ~32

---

*Generado el 2026-03-10 desde documentos KODA del DGI GORE Ñuble.*
*Cruzado con GORE_OS rev. 2591687 (398 tests, 34 endpoints DGI, 5 páginas, 4 cockpits).*
