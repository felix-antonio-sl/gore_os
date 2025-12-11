# 📋 User Stories Consolidadas — GORE OS

> **Sistema Operativo Cognitivo Regional**
> **Versión:** 1.0.0 | **Fecha:** 2025-12-11
> **Fuentes:** `uso_viajes.md`, `trazabilidad_gore_4_0.md`, `user_journeys.md`, `user_stories_granulares_para_titi.md`, `vision_gore_os.md`
> **Fuentes:** `uso_viajes.md`, `users.md`, `trazabilidad_gore_4_0.md`, `user_journeys.md`, `user_stories_granulares_para_titi.md`, `vision_gore_os.md`, `onto_categorica_v4.yaml`
> **Modelo de Datos:** `onto_categorica_v4.yaml`

---

## Resumen Ejecutivo

| Métrica                  | Cantidad |
| ------------------------ | -------- |
| **Total User Stories**   | **220**  |
| **Módulos GORE OS**      | **19**   |
| **Roles/Perfiles**       | **52+**  |
| **Prioridad Crítica**    | 110      |
| **Prioridad Alta**       | 94       |
| **Journeys Soportados**  | 35+      |
| **Fuentes Consolidadas** | 8        |

> **Fuentes:** `uso_viajes.md`, `users.md`, `trazabilidad_gore_4_0.md`, `user_journeys.md`, `user_stories_granulares_para_titi.md`, `vision_gore_os.md`, `onto_categorica_v3.yaml`, `onto_categorica_v4.yaml`

---

## 1. MÓDULO IPR — Gestión de Inversión Pública Regional

**Dominio Ontológico:** `gore_inversion`, `gore_evaluacion`
**Función GORE 4.0:** Financiar + Ejecutar
**Journeys:** J01, J05, J06, JX01-JX05

### 1.1 Formulador Externo (FE)

| ID             | User Story                                                                                                                                                                                                | AC                                                                                                                                                                           | Prioridad   | Entidad Ontológica                  |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ----------------------------------- |
| **FE-IPR-001** | Como **Formulador Externo**, quiero consultar un árbol de decisión interactivo para determinar la vía de financiamiento correcta (SNI/FRIL/FRPD/8%/Glosa06), para postular correctamente desde el inicio. | Dado un conjunto de respuestas sobre naturaleza IPR, ejecutor, monto y sector; Cuando completo el wizard; Entonces recibo recomendación de track con requisitos específicos. | **Crítica** | `codigo_track`                      |
| **FE-IPR-002** | Como **Formulador Externo**, quiero ver la lista de documentos obligatorios según el mecanismo seleccionado, para preparar una postulación completa.                                                      | Dado un track seleccionado; Cuando accedo a requisitos; Entonces veo checklist específico por mecanismo con ejemplos.                                                        | **Crítica** | `gore_documental.documento`         |
| **FE-IPR-003** | Como **Formulador Externo**, quiero cargar mi postulación IPR con todos los antecedentes digitalizados, para formalizar el ingreso al GORE.                                                               | Dado formulario completo + documentos adjuntos; Cuando envío postulación; Entonces recibo número de ingreso y estado "RECIBIDA".                                             | **Crítica** | `gore_inversion.iniciativa`         |
| **FE-IPR-004** | Como **Formulador Externo**, quiero recibir notificación inmediata cuando mi IPR tenga observaciones de admisibilidad, para subsanar dentro del plazo legal (60 días).                                    | Dado IPR con estado FI/OT; Cuando GORE registra observaciones; Entonces recibo email + notificación push con detalle y plazo.                                                | **Crítica** | `gore_evaluacion.resultado_rate`    |
| **FE-IPR-005** | Como **Formulador Externo**, quiero subsanar observaciones directamente en el sistema adjuntando nuevos documentos, para no recurrir a trámite presencial.                                                | Dado IPR observada; Cuando subo documentos corregidos; Entonces estado cambia a "SUBSANACIÓN ENVIADA" y GORE es notificado.                                                  | **Alta**    | `gore_documental.version_documento` |
| **FE-IPR-006** | Como **Formulador Externo**, quiero consultar el estado de mi postulación en tiempo real, para conocer en qué fase del ciclo se encuentra.                                                                | Dado código IPR; Cuando consulto estado; Entonces veo timeline visual con fase actual y fechas estimadas.                                                                    | **Crítica** | `gore_fsm.instancia_fsm`            |
| **FE-IPR-007** | Como **Formulador Externo**, quiero ver mi historial de postulaciones con estadísticas de éxito, para mejorar futuras formulaciones.                                                                      | Dado mi identificación (RUT entidad); Cuando accedo a historial; Entonces veo lista con tasa de admisibilidad y observaciones frecuentes.                                    | **Media**   | `gore_actores.entidad`              |

| **FE-IPR-009** | Como **Formulador Externo**, quiero descargar el convenio de transferencia para revisión y firma, para formalizar la ejecución del proyecto.                                                              | Dado IPR aprobada por CORE; Cuando convenio está generado; Entonces puedo descargarlo en PDF y ver estado de firmas.                                                         | **Alta**    | `gore_financiero.convenio`          |
| **FE-IPR-010** | Como **Formulador Externo**, quiero reportar avance de ejecución mensual con % físico y financiero, para cumplir obligaciones de seguimiento.                                                             | Dado IPR en ejecución; Cuando ingreso informe; Entonces RTF es notificado y avance se refleja en dashboard GORE.                                                             | **Crítica** | `gore_ejecucion.avance_obra`        |

### 1.2 Analista DIPIR (AD)

| ID             | User Story                                                                                                                                             | AC                                                                                                                                   | Prioridad   | Entidad Ontológica                 |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ | ----------- | ---------------------------------- |
| **AD-IPR-001** | Como **Analista DIPIR**, quiero ver un dashboard de cartera IPR con estados consolidados por fase del ciclo, para gestionar mi carga de trabajo.       | Dado mi asignación; Cuando accedo a dashboard; Entonces veo contadores por estado (Ingresada, Pre-admisible, En MDSF, Con RS, etc.). | **Crítica** | `gore_inversion.iniciativa`        |
| **AD-IPR-002** | Como **Analista DIPIR**, quiero ver una bandeja de postulaciones nuevas ordenadas por fecha, para procesarlas en orden de llegada.                     | Dado rol Analista; Cuando accedo a bandeja; Entonces veo IPR sin asignar con filtros por fecha, mecanismo, municipio.                | **Crítica** | `gore_workflow.tarea`              |
| **AD-IPR-003** | Como **Analista DIPIR**, quiero completar un checklist de admisibilidad específico por mecanismo, para documentar mi revisión formal.                  | Dado IPR asignada + mecanismo; Cuando proceso admisibilidad; Entonces veo checklist dinámico según track (SNI, FRIL, Glosa06, etc.). | **Crítica** | `gore_evaluacion.evaluacion_gore`  |
| **AD-IPR-004** | Como **Analista DIPIR**, quiero registrar el resultado de admisibilidad (ADMISIBLE/CON OBS/INADMISIBLE) con fundamento, para formalizar la decisión.   | Dado checklist completado; Cuando registro resultado; Entonces estado IPR cambia y UF es notificado automáticamente.                 | **Crítica** | `gore_fsm.transicion`              |
| **AD-IPR-005** | Como **Analista DIPIR**, quiero enviar IPR a MDSF para evaluación técnica-económica registrando "Informar Postulación" en BIP, para iniciar track SNI. | Dado IPR admisible tipo SNI; Cuando ejecuto envío; Entonces se registra en BIP y estado cambia a "EN EVALUACIÓN MDSF".               | **Crítica** | `gore_integracion.sincronizacion`  |
| **AD-IPR-006** | Como **Analista DIPIR**, quiero monitorear estados RATE de MDSF (RS/FI/OT/AD) en tiempo real, para gestionar tiempos de evaluación.                    | Dado cartera en MDSF; Cuando consulto; Entonces veo semáforo de estados con días transcurridos y alertas de vencimiento.             | **Crítica** | `gore_evaluacion.resultado_rate`   |
| **AD-IPR-007** | Como **Analista DIPIR**, quiero recibir alerta automática cuando una IPR lleva >30 días sin movimiento en MDSF, para gestionar proactivamente.         | Dado IPR en MDSF >30 días sin cambio; Cuando se detecta; Entonces recibo alerta para seguimiento con SEREMI MDSF.                    | **Alta**    | `gore_ejecucion.alerta_ipr`        |
| **AD-IPR-008** | Como **Analista DIPIR**, quiero registrar observaciones FI/OT recibidas y comunicarlas automáticamente a la UF, para iniciar proceso de subsanación.   | Dado RATE con FI/OT; Cuando registro observaciones; Entonces UF recibe notificación con detalle y plazo (60 días).                   | **Crítica** | `gore_documental.documento`        |
| **AD-IPR-009** | Como **Analista DIPIR**, quiero ver la cartera de IPR con RS disponible para presentar a CORE, para preparar sesiones de inversión.                    | Dado período de sesión CORE; Cuando filtro cartera; Entonces veo IPR con aprobación técnica listas para votación.                    | **Crítica** | `gore_gobernanza.sesion_core`      |
| **AD-IPR-010** | Como **Analista DIPIR**, quiero generar automáticamente la carpeta CORE con oficios y fichas técnicas, para reducir trabajo manual de preparación.     | Dado cartera seleccionada para CORE; Cuando ejecuto generación; Entonces obtengo PDF consolidado con oficio + fichas + anexos.       | **Alta**    | `gore_documental.expediente`       |
| **AD-IPR-011** | Como **Analista DIPIR**, quiero registrar un problema/nudo detectado en una IPR en ejecución, para documentar bloqueos y coordinar solución.           | Dado IPR con problema; Cuando registro nudo; Entonces selecciono tipo, impacto, responsable y creo compromiso asociado.              | **Crítica** | `gore_ejecucion.problema_ipr`      |
| **AD-IPR-012** | Como **Analista DIPIR**, quiero ver semáforos de ejecución (verde/amarillo/rojo) para mi cartera, para priorizar seguimiento en IPR con desviaciones.  | Dado cartera asignada; Cuando veo dashboard; Entonces semáforos reflejan % avance físico vs financiero vs tiempo.                    | **Crítica** | `gore_ejecucion.alerta_ipr`        |
| **AD-IPR-013** | Como **Analista DIPIR**, quiero tramitar modificaciones de IPR (aumento costo, plazo, cambio ejecutor), para formalizar cambios en ejecución.          | Dado solicitud de modificación; Cuando proceso; Entonces sistema determina si requiere nueva RS y/o aprobación CORE.                 | **Alta**    | `gore_inversion.iniciativa`        |
| **AD-IPR-014** | Como **Analista DIPIR**, quiero validar cierre técnico de IPR verificando recepción definitiva y cierre BIP, para cerrar ciclo formalmente.            | Dado IPR terminada; Cuando proceso cierre; Entonces verifico acta recepción, saldos, y actualizo estado a "CERRADA".                 | **Alta**    | `gore_fsm.transicion`              |
| **AD-IPR-015** | Como **Analista DIPIR**, quiero exportar reportes de cartera para CGR/DIPRES, para cumplir obligaciones de reporte externo.                            | Dado parámetros de reporte; Cuando ejecuto exportación; Entonces obtengo Excel/PDF con formato requerido por organismo.              | **Media**   | `gore_integracion.sistema_externo` |

### 1.3 Jefatura DIPIR (JD-DIPIR)

| ID               | User Story                                                                                                                           | AC                                                                                                                      | Prioridad   | Entidad Ontológica                        |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ----------- | ----------------------------------------- |
| **JD-DIPIR-001** | Como **Jefe DIPIR**, quiero ver un dashboard ejecutivo de cartera con KPIs agregados, para reportar al Gobernador.                   | Dado rol Jefatura; Cuando accedo; Entonces veo: total IPR, monto cartera, % ejecución, problemas críticos.              | **Crítica** | `gore_indicadores.indicador`              |
| **JD-DIPIR-002** | Como **Jefe DIPIR**, quiero ver la distribución de carga de trabajo por analista, para balancear asignaciones.                       | Dado equipo DIPIR; Cuando consulto; Entonces veo IPR asignadas por analista con métricas de tiempos.                    | **Alta**    | `gore_actores.persona`                    |
| **JD-DIPIR-003** | Como **Jefe DIPIR**, quiero ver tiempos promedio de tramitación por fase del ciclo, para identificar cuellos de botella.             | Dado período analizado; Cuando consulto; Entonces veo días promedio en cada fase con comparativo histórico.             | **Alta**    | `gore_eventos.evento`                     |
| **JD-DIPIR-004** | Como **Jefe DIPIR**, quiero ver problemas críticos escalados que requieren mi intervención, para resolverlos oportunamente.          | Dado problemas con nivel CRÍTICO o escalados; Cuando accedo; Entonces veo lista priorizada con contexto para decisión.  | **Crítica** | `gore_ejecucion.problema_ipr`             |
| **JD-DIPIR-005** | Como **Jefe DIPIR**, quiero preparar propuesta de priorización de cartera para el Gobernador, para solicitar decisión ejecutiva.     | Dado cartera con RS/RF; Cuando preparo propuesta; Entonces genero ranking con criterios (ERD, urgencia, monto, comuna). | **Crítica** | `gore_planificacion.objetivo_estrategico` |
| **JD-DIPIR-006** | Como **Jefe DIPIR**, quiero generar informes de gestión para el Administrador Regional, para reportar avance divisional.             | Dado período; Cuando genero informe; Entonces obtengo documento con KPIs, logros, problemas y próximos pasos.           | **Alta**    | `gore_documental.documento`               |
| **JD-DIPIR-007** | Como **Jefe DIPIR**, quiero participar en el CDR con información consolidada de postulaciones, para filtrar pertinencia estratégica. | Dado sesión CDR; Cuando preparo; Entonces tengo tabla de IPR con alineamiento ERD y recomendación.                      | **Crítica** | `gore_gobernanza.acuerdo_core`            |

---

## 2. MÓDULO PRESUPUESTO — Gestión Financiera

**Dominio Ontológico:** `gore_presupuesto`, `gore_financiero`
**Función GORE 4.0:** Financiar
**Journeys:** J18, JX07

### 2.1 Profesional DAF (PD)

| ID              | User Story                                                                                                                                                  | AC                                                                                                                                    | Prioridad   | Entidad Ontológica                                |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------- |
| **PD-PPTO-001** | Como **Profesional DAF**, quiero emitir CDP con validación automática de disponibilidad presupuestaria, para garantizar respaldo financiero.                | Dado solicitud de CDP; Cuando proceso; Entonces sistema verifica saldo asignación y emite o rechaza con fundamento.                   | **Crítica** | `gore_presupuesto.cdp`                            |
| **PD-PPTO-002** | Como **Profesional DAF**, quiero ver el estado de afectación por iniciativa (preafectación → compromiso → devengo → pago), para controlar ciclo financiero. | Dado código IPR; Cuando consulto; Entonces veo pipeline financiero con montos en cada estado.                                         | **Crítica** | `gore_presupuesto.movimiento_presupuestario`      |
| **PD-PPTO-003** | Como **Profesional DAF**, quiero programar pagos según reglas de devengo por tipo de receptor, para cumplir normativa CGR.                                  | Dado convenio y tipo receptor (municipal, servicio, privado); Cuando programo; Entonces sistema aplica regla devengo correspondiente. | **Crítica** | `gore_financiero.cuota_transferencia`             |
| **PD-PPTO-004** | Como **Profesional DAF**, quiero recibir alerta de glosas cuando un movimiento potencialmente las infrinja, para prevenir observaciones CGR.                | Dado movimiento presupuestario; Cuando viola Glosa 03/04/06; Entonces recibo alerta con explicación y alternativas.                   | **Crítica** | `gore_normativo.glosa`                            |
| **PD-PPTO-005** | Como **Profesional DAF**, quiero tramitar modificaciones presupuestarias con asistente que determine tipo de acto requerido, para simplificar proceso.      | Dado necesidad de modificación; Cuando ingreso parámetros; Entonces sistema indica: Resolución/Decreto, visaciones, TdR.              | **Alta**    | `gore_presupuesto.tipo_movimiento_presupuestario` |
| **PD-PPTO-006** | Como **Profesional DAF**, quiero ver proyección de ejecución mensual vs programa de caja DIPRES, para anticipar desfases.                                   | Dado mes/año; Cuando consulto; Entonces veo gráfico comparativo con alertas de desviación >5%.                                        | **Alta**    | `gore_indicadores.medicion`                       |
| **PD-PPTO-007** | Como **Profesional DAF**, quiero calcular deuda flotante al cierre anual, para tramitar incorporación en presupuesto siguiente.                             | Dado cierre ejercicio; Cuando ejecuto cálculo; Entonces obtengo monto deuda flotante por programa/subtítulo.                          | **Alta**    | `gore_presupuesto.asignacion`                     |
| **PD-PPTO-008** | Como **Profesional DAF**, quiero sincronizar movimientos con SIGFE, para mantener consistencia entre sistemas.                                              | Dado período procesado; Cuando sincronizo; Entonces se valida consistencia y se reportan diferencias.                                 | **Crítica** | `gore_integracion.sincronizacion`                 |

### 2.2 Jefatura DAF (JD-DAF)

| ID             | User Story                                                                                                                          | AC                                                                                                                    | Prioridad   | Entidad Ontológica                           |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ----------- | -------------------------------------------- |
| **JD-DAF-001** | Como **Jefe DAF**, quiero ver dashboard de ejecución presupuestaria mensual por subtítulo/programa, para reportar al Gobernador.    | Dado mes; Cuando consulto; Entonces veo % ejecución con semáforo y comparativo año anterior.                          | **Crítica** | `gore_indicadores.indicador`                 |
| **JD-DAF-002** | Como **Jefe DAF**, quiero ver ejecutores con rendiciones vencidas, para aplicar bloqueo de nuevas transferencias (Art. 18 Res. 30). | Dado fecha actual; Cuando consulto; Entonces veo lista de ejecutores con días de vencimiento y monto bloqueado.       | **Crítica** | `gore_financiero.rendicion`                  |
| **JD-DAF-003** | Como **Jefe DAF**, quiero aprobar informes de rendición con FEA después de revisión RTF, para cerrar ciclo de rendición.            | Dado informe revisado por RTF; Cuando apruebo; Entonces firmo con FEA y UCR puede contabilizar en SIGFE.              | **Crítica** | `gore_documental.firma`                      |
| **JD-DAF-004** | Como **Jefe DAF**, quiero ver proyección de deuda flotante durante el año, para gestionar compromisos oportunamente.                | Dado punto del año; Cuando consulto; Entonces veo proyección de deuda flotante y su impacto en presupuesto siguiente. | **Alta**    | `gore_presupuesto.movimiento_presupuestario` |

---

## 3. MÓDULO CONVENIOS Y TRANSFERENCIAS

**Dominio Ontológico:** `gore_financiero`, `gore_documental`
**Función GORE 4.0:** Financiar + Ejecutar
**Journeys:** J07, JX04

### 3.1 Profesional DAF Convenios (PD-CONV)

| ID              | User Story                                                                                                                                   | AC                                                                                                                 | Prioridad   | Entidad Ontológica                    |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ----------- | ------------------------------------- |
| **PD-CONV-001** | Como **Profesional DAF**, quiero generar convenios de transferencia desde plantillas según tipo de ejecutor, para estandarizar documentos.   | Dado IPR aprobada + tipo ejecutor; Cuando genero; Entonces obtengo borrador con cláusulas apropiadas pre-llenadas. | **Crítica** | `gore_financiero.convenio`            |
| **PD-CONV-002** | Como **Profesional DAF**, quiero ver lista de convenios por estado (elaboración, visación, TdR, vigente, terminado), para gestionar cartera. | Dado rol DAF; Cuando consulto; Entonces veo convenios con filtros por estado, fecha vencimiento, ejecutor.         | **Crítica** | `estado_convenio`                     |
| **PD-CONV-003** | Como **Profesional DAF**, quiero recibir alerta de convenios próximos a vencer (30/15/7 días), para gestionar prórrogas o cierres.           | Dado convenio con fecha término cercana; Cuando se detecta; Entonces recibo alerta con acciones sugeridas.         | **Alta**    | `gore_ejecucion.alerta_ipr`           |
| **PD-CONV-004** | Como **Profesional DAF**, quiero registrar cuotas de transferencia programadas según calendario del convenio, para programar pagos.          | Dado convenio vigente; Cuando registro cuotas; Entonces quedan programadas con fechas y condiciones de liberación. | **Crítica** | `gore_financiero.cuota_transferencia` |
| **PD-CONV-005** | Como **Profesional DAF**, quiero controlar garantías de fiel cumplimiento con alertas de vencimiento, para gestionar renovaciones.           | Dado garantía asociada a convenio; Cuando próxima a vencer; Entonces recibo alerta y puedo registrar renovación.   | **Alta**    | `gore_financiero.garantia`            |

### 3.2 Referente Técnico-Financiero (RTF)

| ID          | User Story                                                                                                                          | AC                                                                                                            | Prioridad   | Entidad Ontológica                    |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------- |
| **RTF-001** | Como **RTF**, quiero crear proyectos/programas en SISREC y registrar transferencias, para habilitar rendición del ejecutor.         | Dado convenio formalizado; Cuando registro en SISREC; Entonces ejecutor puede iniciar rendiciones.            | **Crítica** | `gore_integracion.sistema_externo`    |
| **RTF-002** | Como **RTF**, quiero revisar rendiciones recibidas en SISREC verificando respaldos técnicos y financieros, para aprobar o devolver. | Dado informe de rendición; Cuando reviso; Entonces apruebo/observo cada transacción con fundamento.           | **Crítica** | `gore_financiero.rendicion`           |
| **RTF-003** | Como **RTF**, quiero generar informe de aprobación para firma de Jefe DAF, para avanzar en ciclo de rendición.                      | Dado rendición aprobada por mí; Cuando genero informe; Entonces pasa a bandeja de Jefe DAF para FEA.          | **Crítica** | `gore_documental.documento`           |
| **RTF-004** | Como **RTF**, quiero coordinar con ejecutores la regularización de observaciones, para desbloquear rendiciones trabadas.            | Dado rendición observada >15 días; Cuando gestiono; Entonces registro comunicaciones y fechas de seguimiento. | **Alta**    | `gore_ejecucion.compromiso_operativo` |

### 3.3 Unidad Control Rendiciones (UCR)

| ID          | User Story                                                                                                                            | AC                                                                                                                | Prioridad   | Entidad Ontológica                |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ----------- | --------------------------------- |
| **UCR-001** | Como **Profesional UCR**, quiero contabilizar rendiciones aprobadas en SIGFE, para cerrar ciclo financiero.                           | Dado informe aprobado con FEA; Cuando contabilizo; Entonces registro en SIGFE y archivo expediente.               | **Crítica** | `gore_integracion.sincronizacion` |
| **UCR-002** | Como **Profesional UCR**, quiero ver dashboard de rendiciones pendientes por ejecutor con días de antigüedad, para priorizar gestión. | Dado rol UCR; Cuando consulto; Entonces veo ranking de ejecutores por mora con semáforo.                          | **Alta**    | `gore_indicadores.indicador`      |
| **UCR-003** | Como **Profesional UCR**, quiero generar alerta a ejecutores con rendición vencida, para activar bloqueo según Art. 18.               | Dado ejecutor con rendición exigible pendiente; Cuando se detecta; Entonces se notifica y activa flag de bloqueo. | **Crítica** | `gore_ejecucion.alerta_ipr`       |

---

## 4. MÓDULO EJECUCIÓN Y CRISIS

**Dominio Ontológico:** `gore_ejecucion`
**Función GORE 4.0:** Ejecutar
**Journeys:** J05, J06

### 4.1 Supervisor de Proyecto (SUP)

| ID          | User Story                                                                                                                           | AC                                                                                                                      | Prioridad   | Entidad Ontológica                |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ----------- | --------------------------------- |
| **SUP-001** | Como **Supervisor**, quiero crear carpeta de seguimiento al asumir un proyecto, para centralizar información del ciclo de ejecución. | Dado IPR asignada; Cuando creo carpeta; Entonces tengo espacio estructurado para visitas, informes, EP, comunicaciones. | **Alta**    | `gore_expediente.expediente`      |
| **SUP-002** | Como **Supervisor**, quiero registrar visitas de terreno con evidencia fotográfica y observaciones, para documentar supervisión.     | Dado visita realizada; Cuando registro; Entonces adjunto fotos, notas y actualizo % avance estimado.                    | **Crítica** | `gore_ejecucion.avance_obra`      |
| **SUP-003** | Como **Supervisor**, quiero revisar y validar informes de avance de la Unidad Técnica, para aprobar continuidad.                     | Dado informe de UT; Cuando reviso; Entonces apruebo/observo y actualizo estado en BIP.                                  | **Crítica** | `gore_integracion.sincronizacion` |
| **SUP-004** | Como **Supervisor**, quiero gestionar estados de pago validando avance físico correspondiente, para autorizar liberación de cuotas.  | Dado EP presentado; Cuando valido; Entonces autorizo pago si avance corresponde a monto solicitado.                     | **Crítica** | `gore_ejecucion.estado_pago`      |
| **SUP-005** | Como **Supervisor**, quiero alertar a Jefatura sobre desviaciones relevantes (costo, plazo, calidad), para escalar oportunamente.    | Dado desviación >10% en cualquier dimensión; Cuando detecto; Entonces genero alerta formal con recomendación.           | **Crítica** | `gore_ejecucion.alerta_ipr`       |
| **SUP-006** | Como **Supervisor**, quiero validar acta de recepción provisoria y definitiva, para cerrar ciclo de ejecución.                       | Dado obra terminada; Cuando valido recepción; Entonces autorizo procesamiento de último pago y cierre.                  | **Alta**    | `gore_documental.documento`       |

### 4.2 Administrador Regional (AR)

| ID         | User Story                                                                                                                                                                                                               | AC                                                                                                                       | Prioridad   | Entidad Ontológica                    |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ | ----------- | ------------------------------------- |
| **AR-001** | Como **Administrador Regional**, quiero ver dashboard ejecutivo con número total de IPR activas, problemas abiertos, compromisos vencidos y alertas críticas, para tener visibilidad inmediata del estado de la cartera. | Dado rol AR; Cuando accedo; Entonces veo resumen ejecutivo con métricas clave y tendencias.                              | **Crítica** | `gore_indicadores.indicador`          |
| **AR-002** | Como **Administrador Regional**, quiero ver lista filtrada de proyectos con nivel de alerta "CRÍTICO", para enfocar recursos en los casos más graves.                                                                    | Dado alertas activas; Cuando filtro críticos; Entonces veo lista con detalle de problema, responsable, días antigüedad.  | **Crítica** | `gore_ejecucion.alerta_ipr`           |
| **AR-003** | Como **Administrador Regional**, quiero ver compromisos vencidos agrupados por división, para estructurar reunión semanal.                                                                                               | Dado compromisos vencidos; Cuando agrupo; Entonces veo ranking de divisiones por mora con responsables.                  | **Crítica** | `gore_ejecucion.compromiso_operativo` |
| **AR-004** | Como **Administrador Regional**, quiero crear un compromiso asignado a un responsable con fecha límite durante la reunión, para formalizar acuerdos.                                                                     | Dado reunión de coordinación; Cuando creo compromiso; Entonces queda registrado con responsable, plazo, IPR vinculada.   | **Crítica** | `gore_ejecucion.compromiso_operativo` |
| **AR-005** | Como **Administrador Regional**, quiero ver historial de compromisos de una IPR, para entender contexto de gestión.                                                                                                      | Dado código IPR; Cuando consulto; Entonces veo timeline de compromisos con estados y comentarios.                        | **Alta**    | `gore_eventos.evento`                 |
| **AR-006** | Como **Administrador Regional**, quiero verificar compromisos completados y marcarlos como "Verificado" o rechazarlos, para cerrar ciclo de seguimiento.                                                                 | Dado compromiso en estado "Completado"; Cuando verifico; Entonces cierro o devuelvo a "Pendiente" con comentario.        | **Crítica** | `gore_fsm.transicion`                 |
| **AR-007** | Como **Administrador Regional**, quiero registrar un problema detectado durante entrevista con responsable, para documentar hallazgos.                                                                                   | Dado entrevista; Cuando registro problema; Entonces selecciono tipo, impacto, y creo compromiso de seguimiento.          | **Alta**    | `gore_ejecucion.problema_ipr`         |
| **AR-008** | Como **Administrador Regional**, quiero generar resumen semanal con métricas de cumplimiento, para informar al Gobernador.                                                                                               | Dado período semanal; Cuando genero; Entonces obtengo PDF con tasa cumplimiento, problemas resueltos/nuevos, tendencias. | **Alta**    | `gore_documental.documento`           |
| **AR-009** | Como **Administrador Regional**, quiero ver ranking de divisiones por tasa de cumplimiento de compromisos, para identificar áreas de mejora.                                                                             | Dado período; Cuando consulto; Entonces veo ranking con métricas comparativas entre divisiones.                          | **Alta**    | `gore_indicadores.indicador`          |

### 4.3 Jefe de División (JD)

| ID         | User Story                                                                                                                                        | AC                                                                                                             | Prioridad   | Entidad Ontológica                    |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------- |
| **JD-001** | Como **Jefe de División**, quiero ver total de IPR asignadas a mi división, problemas abiertos y compromisos pendientes, para conocer mi alcance. | Dado mi división; Cuando accedo; Entonces veo métricas agregadas de mi área de responsabilidad.                | **Crítica** | `gore_actores.division`               |
| **JD-002** | Como **Jefe de División**, quiero ver lista de encargados de mi división con sus métricas de compromisos, para evaluar cargas de trabajo.         | Dado mi equipo; Cuando consulto; Entonces veo compromisos pendientes/vencidos por persona con semáforo.        | **Alta**    | `gore_actores.persona`                |
| **JD-003** | Como **Jefe de División**, quiero crear un compromiso y asignarlo a un encargado de mi división con prioridad, para distribuir tareas.            | Dado necesidad de acción; Cuando creo compromiso; Entonces asigno a persona, establezco plazo y prioridad.     | **Crítica** | `gore_ejecucion.compromiso_operativo` |
| **JD-004** | Como **Jefe de División**, quiero reasignar un compromiso de un encargado a otro, para balancear cargas.                                          | Dado compromiso existente; Cuando reasigno; Entonces se notifica a ambos y se registra en historial.           | **Media**   | `gore_workflow.asignacion_tarea`      |
| **JD-005** | Como **Jefe de División**, quiero registrar un problema en una IPR de mi división, para documentar bloqueos detectados.                           | Dado IPR con problema; Cuando registro; Entonces clasifico tipo, propongo solución y creo compromiso asociado. | **Crítica** | `gore_ejecucion.problema_ipr`         |
| **JD-006** | Como **Jefe de División**, quiero cerrar un problema registrando la solución aplicada, para mantener trazabilidad.                                | Dado problema resuelto; Cuando cierro; Entonces documento solución, impacto final y lección aprendida.         | **Alta**    | `gore_fsm.transicion`                 |
| **JD-007** | Como **Jefe de División**, quiero ver IPR compartidas con otras divisiones y compromisos cruzados, para coordinar acciones conjuntas.             | Dado IPR interdivisional; Cuando consulto; Entonces veo responsables de cada división y compromisos asociados. | **Media**   | `gore_actores.division`               |

### 4.4 Encargado Operativo (EO)

| ID         | User Story                                                                                                                                             | AC                                                                                                          | Prioridad   | Entidad Ontológica                    |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------- |
| **EO-001** | Como **Encargado Operativo**, quiero ver mi lista de compromisos ordenada por fecha límite con vencidos destacados, para priorizar trabajo.            | Dado mis compromisos; Cuando accedo; Entonces veo lista ordenada con semáforo y días restantes/vencidos.    | **Crítica** | `gore_ejecucion.compromiso_operativo` |
| **EO-002** | Como **Encargado Operativo**, quiero cambiar estado de mi compromiso a "En progreso" y agregar comentarios de avance parcial, para documentar gestión. | Dado compromiso asignado; Cuando actualizo; Entonces queda registrado el avance con timestamp.              | **Alta**    | `gore_fsm.transicion`                 |
| **EO-003** | Como **Encargado Operativo**, quiero marcar mi compromiso como "Completado" con comentario de cierre obligatorio, para enviarlo a verificación.        | Dado compromiso terminado; Cuando completo; Entonces pasa a bandeja de verificación del Jefe/AR.            | **Crítica** | `gore_fsm.transicion`                 |
| **EO-004** | Como **Encargado Operativo**, quiero ver la lista de IPR que tengo asignadas con indicadores de alerta, para identificar las que requieren atención.   | Dado mis IPR; Cuando consulto; Entonces veo cartera con semáforo y último avance reportado.                 | **Alta**    | `gore_inversion.iniciativa`           |
| **EO-005** | Como **Encargado Operativo**, quiero registrar informe de avance para una IPR con % físico, % financiero y descripción, para actualizar estado.        | Dado IPR en ejecución; Cuando ingreso informe; Entonces RTF es notificado y datos se reflejan en dashboard. | **Crítica** | `gore_ejecucion.avance_obra`          |
| **EO-006** | Como **Encargado Operativo**, quiero registrar un problema detectado en una de mis IPR, para alertar sobre bloqueos.                                   | Dado problema detectado; Cuando registro; Entonces queda vinculado a IPR y visible para Jefatura.           | **Alta**    | `gore_ejecucion.problema_ipr`         |
| **EO-007** | Como **Encargado Operativo**, quiero ver la ficha completa de una IPR con convenios, cuotas, problemas e historial, para tener contexto completo.      | Dado código IPR; Cuando consulto ficha; Entonces veo todos los datos asociados en vista integrada.          | **Alta**    | `gore_inversion.iniciativa`           |

---

## 5. MÓDULO CORE — Gobernanza y Fiscalización

**Dominio Ontológico:** `gore_gobernanza`
**Función GORE 4.0:** Coordinar
**Journeys:** J13

### 5.1 Consejero Regional (CR)

| ID         | User Story                                                                                                                                                | AC                                                                                                                         | Prioridad   | Entidad Ontológica             |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------ |
| **CR-001** | Como **Consejero Regional**, quiero recibir carpeta digital de cartera para votación con anticipación, para analizarla antes de sesión.                   | Dado sesión CORE programada; Cuando se publica carpeta; Entonces recibo notificación con link a documentos digitales.      | **Crítica** | `gore_gobernanza.sesion_core`  |
| **CR-002** | Como **Consejero Regional**, quiero ver fichas resumen ejecutivo por IPR con indicadores clave, para entender cada proyecto sin leer expediente completo. | Dado cartera CORE; Cuando consulto IPR; Entonces veo ficha 1-página con: monto, ejecutor, beneficiarios, alineamiento ERD. | **Crítica** | `gore_documental.documento`    |
| **CR-003** | Como **Consejero Regional**, quiero ver los proyectos de mi provincia/circunscripción destacados, para fiscalizar impacto en mi territorio.               | Dado mi circunscripción; Cuando filtro; Entonces veo cartera territorial con mapa y estadísticas por comuna.               | **Crítica** | `gore_territorial.comuna`      |
| **CR-004** | Como **Consejero Regional**, quiero ver mapa territorial de inversiones con capas por sector y estado, para visualizar distribución espacial.             | Dado cartera regional; Cuando accedo a mapa; Entonces veo puntos geolocalizados con filtros dinámicos.                     | **Alta**    | `gore_territorial.provincia`   |
| **CR-005** | Como **Consejero Regional**, quiero ver dashboard de ejecución regional con comparativo entre comunas, para fiscalizar equidad territorial.               | Dado período; Cuando consulto; Entonces veo % ejecución por comuna con semáforo y ranking.                                 | **Crítica** | `gore_indicadores.indicador`   |
| **CR-006** | Como **Consejero Regional**, quiero ver histórico de mis votaciones y los acuerdos CORE, para mantener registro de mis decisiones.                        | Dado mi perfil; Cuando consulto historial; Entonces veo votaciones por sesión con resultado y texto del acuerdo.           | **Media**   | `gore_gobernanza.votacion`     |
| **CR-007** | Como **Consejero Regional**, quiero verificar cumplimiento de acuerdos CORE anteriores, para fiscalizar ejecución de decisiones.                          | Dado acuerdo CORE; Cuando consulto; Entonces veo estado de cumplimiento con evidencia.                                     | **Alta**    | `gore_gobernanza.acuerdo_core` |
| **CR-008** | Como **Consejero Regional**, quiero buscar cualquier IPR por código o nombre, para consultar información ad-hoc.                                          | Dado criterio de búsqueda; Cuando busco; Entonces obtengo resultados con link a ficha completa.                            | **Alta**    | `gore_inversion.iniciativa`    |
| **CR-009** | Como **Consejero Regional**, quiero acceder al portal de transparencia (Glosa 16), para verificar publicación de cartera y acuerdos.                      | Dado rol CORE; Cuando accedo; Entonces veo información publicada según obligación legal.                                   | **Alta**    | `gore_normativo.norma`         |
| **CR-010** | Como **Consejero Regional**, quiero exportar información a PDF/Excel, para preparar intervenciones en sesión.                                             | Dado cualquier vista; Cuando exporto; Entonces obtengo documento en formato seleccionado.                                  | **Media**   | `gore_documental.documento`    |

### 5.2 Gobernador Regional (GR)

| ID         | User Story                                                                                                                                                               | AC                                                                                                              | Prioridad   | Entidad Ontológica                    |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------- |
| **GR-001** | Como **Gobernador Regional**, quiero ver dashboard ejecutivo integrado con KPIs de ERD, ejecución presupuestaria y alertas críticas, para tomar decisiones estratégicas. | Dado mi rol; Cuando accedo; Entonces veo panel unificado con métricas clave de las 5 funciones GORE.            | **Crítica** | `gore_indicadores.indicador`          |
| **GR-002** | Como **Gobernador Regional**, quiero recibir alertas tempranas de desviaciones críticas, para intervenir oportunamente.                                                  | Dado evento crítico; Cuando ocurre; Entonces recibo notificación push con contexto y sugerencia de acción.      | **Crítica** | `gore_ejecucion.alerta_ipr`           |
| **GR-003** | Como **Gobernador Regional**, quiero simular impacto de políticas públicas en indicadores territoriales, para fundamentar decisiones.                                    | Dado escenario hipotético; Cuando ejecuto simulación; Entonces veo proyección de impacto en KPIs.               | **Media**   | `gore_indicadores.meta`               |
| **GR-004** | Como **Gobernador Regional**, quiero comparar indicadores entre comunas para priorización de inversiones, para asegurar equidad territorial.                             | Dado conjunto de comunas; Cuando comparo; Entonces veo ranking con brechas destacadas.                          | **Crítica** | `gore_territorial.brecha_territorial` |
| **GR-005** | Como **Gobernador Regional**, quiero firmar resoluciones y decretos con FEA, para formalizar actos administrativos de manera digital.                                    | Dado acto preparado; Cuando firmo; Entonces queda registrado con FEA y pasa a siguiente etapa (DIPRES/CGR).     | **Crítica** | `gore_documental.firma`               |
| **GR-006** | Como **Gobernador Regional**, quiero registrar mis audiencias, viajes y donativos (Ley de Lobby), para cumplir obligación legal.                                         | Dado evento de lobby; Cuando registro; Entonces queda en sistema para publicación en portal de transparencia.   | **Crítica** | `gore_normativo.norma`                |
| **GR-007** | Como **Gobernador Regional**, quiero ver estado de IPR críticas y escalamientos en War Room, para sesiones de crisis.                                                    | Dado situación crítica; Cuando accedo War Room; Entonces veo IPR críticas con contexto para decisión ejecutiva. | **Crítica** | `gore_ejecucion.problema_ipr`         |

---

## 6. MÓDULO ADMINISTRACIÓN DEL SISTEMA

**Dominio Ontológico:** `gore_seguridad`, `gore_actores`
**Función GORE 4.0:** Transversal

### 6.1 Administrador del Sistema (AS)

| ID         | User Story                                                                                                                                             | AC                                                                                                                          | Prioridad   | Entidad Ontológica                 |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- | ----------- | ---------------------------------- |
| **AS-001** | Como **Administrador del Sistema**, quiero crear y editar divisiones con nombre, descripción y jefe asignado, para reflejar estructura organizacional. | Dado necesidad de organización; Cuando gestiono división; Entonces queda registrada con jerarca asignado.                   | **Alta**    | `gore_actores.division`            |
| **AS-002** | Como **Administrador del Sistema**, quiero crear usuarios con nombre, email, división y rol, para dar acceso al sistema.                               | Dado nuevo funcionario; Cuando creo usuario; Entonces queda habilitado con permisos según rol.                              | **Crítica** | `gore_actores.persona`             |
| **AS-003** | Como **Administrador del Sistema**, quiero cambiar rol o división de un usuario, para reflejar cambios organizacionales.                               | Dado usuario existente; Cuando modifico; Entonces se actualizan permisos y pertenencia automáticamente.                     | **Alta**    | `gore_seguridad.permiso`           |
| **AS-004** | Como **Administrador del Sistema**, quiero desactivar usuarios sin eliminarlos, para mantener historial de auditoría.                                  | Dado usuario inactivo; Cuando desactivo; Entonces pierde acceso pero se mantiene registro histórico.                        | **Alta**    | `gore_actores.persona`             |
| **AS-005** | Como **Administrador del Sistema**, quiero importar IPR masivamente desde Excel, para carga inicial o migraciones.                                     | Dado archivo Excel; Cuando importo; Entonces sistema valida, reporta errores y carga registros correctos.                   | **Alta**    | `gore_inversion.iniciativa`        |
| **AS-006** | Como **Administrador del Sistema**, quiero configurar reglas de alerta con condiciones y nivel de criticidad, para automatizar detección de problemas. | Dado patrón a detectar; Cuando configuro regla; Entonces sistema genera alertas automáticamente cuando se cumple condición. | **Alta**    | `gore_ejecucion.tipo_alerta_ipr`   |
| **AS-007** | Como **Administrador del Sistema**, quiero ver logs de actividad del sistema filtrados por usuario y fecha, para auditar operaciones.                  | Dado criterios de filtro; Cuando consulto logs; Entonces veo actividad con detalle de usuario, acción, timestamp.           | **Alta**    | `gore_seguridad.log_auditoria`     |
| **AS-008** | Como **Administrador del Sistema**, quiero ver estado de backups y ejecutar backup manual, para asegurar recuperación ante desastres.                  | Dado necesidad de respaldo; Cuando ejecuto backup; Entonces se genera punto de restauración verificable.                    | **Media**   | `gore_integracion.sistema_externo` |

---

## 7. MÓDULO TERRITORIAL Y PLANIFICACIÓN

**Dominio Ontológico:** `gore_territorial`, `gore_planificacion`, `gore_indicadores`
**Función GORE 4.0:** Planificar
**Journeys:** J23, JX09

### 7.1 Profesional DIPLADE

| ID           | User Story                                                                                                                           | AC                                                                                                                    | Prioridad   | Entidad Ontológica                             |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- | ----------- | ---------------------------------------------- |
| **DIPL-001** | Como **Profesional DIPLADE**, quiero ver brechas territoriales por comuna e indicador, para fundamentar priorización de inversiones. | Dado indicador y territorio; Cuando consulto; Entonces veo brecha vs meta regional con visualización geoespacial.     | **Alta**    | `gore_territorial.brecha_territorial`          |
| **DIPL-002** | Como **Profesional DIPLADE**, quiero evaluar alineamiento de IPR postuladas con objetivos ERD, para filtrar pertinencia estratégica. | Dado IPR postulada; Cuando evalúo; Entonces veo mapeo a lineamientos ERD con score de alineamiento.                   | **Crítica** | `gore_planificacion.objetivo_estrategico`      |
| **DIPL-003** | Como **Profesional DIPLADE**, quiero monitorear avance de metas de indicadores ERD, para reportar en cuenta pública.                 | Dado período; Cuando consulto; Entonces veo cumplimiento de metas con tendencia y proyección.                         | **Alta**    | `gore_indicadores.meta`                        |
| **DIPL-004** | Como **Profesional DIPLADE**, quiero gestionar proceso ARI/PROPIR en Chileindica, para coordinar inversión pública regional.         | Dado ciclo ARI; Cuando proceso; Entonces tengo herramientas para convocar, revisar y aprobar iniciativas sectoriales. | **Alta**    | `gore_planificacion.instrumento_planificacion` |

### 7.2 Gobernanza Autónoma (L2)

| ID               | User Story                                                                                                                                | AC                                                                                                         | Prioridad | Entidad Ontológica                    |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | --------- | ------------------------------------- |
| **GORE-AUTO-01** | Como **Gobernador Regional**, quiero definir una Política Regional propia (fuera de marcos nacionales), para ejercer autonomía normativa. | Dado necesidad regional; Cuando promulgo política; Entonces se crea instrumento normativo regional.        | **Alta**  | `L2.Norma.Politica_Regional`          |
| **GORE-AUTO-02** | Como **Profesional DIPLADE**, quiero crear instrumentos de planificación específicos (no estándar), para abordar realidades locales.      | Dado aprobación CORE; Cuando configuro instrumento; Entonces sistema permite seguimiento de metas propias. | **Alta**  | `L3.Planificacion.Instrumento_Propio` |

---

## 8. MÓDULO CIES — Centro Integrado de Emergencia y Seguridad

**Dominio Ontológico:** `gore_seguridad`, `gore_territorial`
**Función GORE 4.0:** Ejecutar + Coordinar
**Journeys:** J20

| ID              | User Story                                                                                                                                    | AC                                                                                                              | Prioridad   | Entidad Ontológica                 |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ----------- | ---------------------------------- |
| **CIES-OP-01**  | Como **Operador CIES**, quiero monitorear cámaras en tiempo real y detectar incidentes, para clasificarlos y activar protocolos.              | Dado feed de cámaras; Cuando detecto anomalía; Entonces clasifico por prioridad y activo protocolo.             | **Crítica** | `gore_seguridad.incidente`         |
| **CIES-OP-02**  | Como **Operador CIES**, quiero seguir trayectorias de vehículos/personas en tiempo real, para rastrear sospechosos.                           | Dado incidente activo; Cuando sigo trayectoria; Entonces veo mapa con movimientos y puedo alertar unidades.     | **Alta**    | `gore_territorial.geolocalizacion` |
| **CIES-SUP-01** | Como **Supervisor CIES**, quiero asumir gestión de incidentes críticos y coordinar con enlaces externos, para escalar respuesta.              | Dado incidente crítico; Cuando asumo; Entonces tengo herramientas de coordinación con Carabineros/PDI/Bomberos. | **Crítica** | `gore_seguridad.incidente`         |
| **CIES-SUP-02** | Como **Supervisor CIES**, quiero activar planes de contingencia ante fallas o desastres, para mantener continuidad.                           | Dado evento mayor; Cuando activo contingencia; Entonces se ejecutan protocolos predefinidos.                    | **Alta**    | `gore_seguridad.protocolo`         |
| **CIES-ENL-01** | Como **Enlace CIES (Carabineros/PDI/Bomberos)**, quiero recibir alertas del CIES y coordinar respuesta en terreno, para actuar oportunamente. | Dado alerta CIES; Cuando recibo; Entonces veo contexto y puedo confirmar respuesta.                             | **Crítica** | `gore_integracion.sistema_externo` |

---

## 9. MÓDULO IDE — Infraestructura de Datos Geoespaciales

**Dominio Ontológico:** `gore_geoespacial`, `gore_territorial`
**Función GORE 4.0:** Planificar
**Journeys:** J21

| ID          | User Story                                                                                                                          | AC                                                                                    | Prioridad | Entidad Ontológica                 |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | --------- | ---------------------------------- |
| **IDE-01**  | Como **Coordinador IDE Regional**, quiero definir política de información geoespacial del GORE, para orientar inversiones en datos. | Dado rol IDE; Cuando defino política; Entonces queda documentada y socializada.       | **Alta**  | `gore_normativo.politica`          |
| **IDE-02**  | Como **Coordinador IDE Regional**, quiero coordinar con IDE Chile la federación de catálogos (CSW), para interoperar nacionalmente. | Dado catálogo local; Cuando federo; Entonces capas aparecen en IDE Chile.             | **Alta**  | `gore_integracion.sistema_externo` |
| **UGIT-01** | Como **Profesional UGIT**, quiero modelar datos y catálogo de objetos según ISO 19110, para estandarizar capas.                     | Dado capa nueva; Cuando modelo; Entonces cumple estándar ISO.                         | **Alta**  | `gore_geoespacial.capa`            |
| **UGIT-02** | Como **Profesional UGIT**, quiero crear metadatos ISO 19115-1 (Perfil Chileno), para documentar capas.                              | Dado capa modelada; Cuando documento; Entonces tiene metadatos completos.             | **Alta**  | `gore_geoespacial.metadato`        |
| **UGIT-03** | Como **Profesional UGIT**, quiero publicar servicios WMS/WFS/WCS en Geonodo, para disponibilizar datos.                             | Dado capa documentada; Cuando publico; Entonces está disponible vía API estándar OGC. | **Alta**  | `gore_integracion.api`             |
| **PFS-01**  | Como **Punto Focal Sectorial (Geo)**, quiero validar contenido temático de capas de mi área, para asegurar calidad.                 | Dado capa sectorial; Cuando valido; Entonces certifico calidad temática.              | **Alta**  | `gore_geoespacial.calidad`         |

---

## 10. MÓDULO TIC — Gobernanza y Transformación Digital

**Dominio Ontológico:** `gore_tic`, `gore_seguridad`
**Función GORE 4.0:** Coordinar + Normar
**Journeys:** J22, JX08

| ID            | User Story                                                                                                               | AC                                                                                            | Prioridad   | Entidad Ontológica           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- | ----------- | ---------------------------- |
| **CTD-01**    | Como **Coordinador TDE**, quiero monitorear avance de implementación TDE, para cumplir plazos legales.                   | Dado plan TDE; Cuando consulto; Entonces veo % avance por componente.                         | **Alta**    | `gore_indicadores.indicador` |
| **CTD-02**    | Como **Coordinador TDE**, quiero gestionar interoperabilidad con otros órganos, para integrar servicios.                 | Dado necesidad de integración; Cuando gestiono; Entonces registro acuerdos en Red Estado.     | **Alta**    | `gore_integracion.acuerdo`   |
| **DPO-01**    | Como **Encargado Protección de Datos**, quiero gestionar solicitudes de derechos ARCO, para cumplir Ley 21.719.          | Dado solicitud ARCO; Cuando proceso; Entonces respondo en plazo legal.                        | **Alta**    | `gore_normativo.norma`       |
| **DPO-02**    | Como **Encargado Protección de Datos**, quiero evaluar impacto de privacidad en nuevos proyectos, para prevenir riesgos. | Dado proyecto nuevo; Cuando evalúo; Entonces emito informe de impacto.                        | **Alta**    | `gore_seguridad.riesgo`      |
| **CISO-01**   | Como **Oficial de Seguridad**, quiero monitorear estado de seguridad de sistemas, para detectar vulnerabilidades.        | Dado panel de seguridad; Cuando consulto; Entonces veo alertas y estado de cumplimiento NIST. | **Alta**    | `gore_seguridad.incidente`   |
| **CISO-02**   | Como **Oficial de Seguridad**, quiero gestionar incidentes de ciberseguridad, para contener amenazas.                    | Dado incidente detectado; Cuando gestiono; Entonces activo protocolo y registro acciones.     | **Crítica** | `gore_seguridad.incidente`   |
| **PMOTIC-01** | Como **PMO TIC**, quiero mantener inventario de proyectos TIC con indicadores, para gobernar portafolio.                 | Dado portafolio TIC; Cuando consulto; Entonces veo estado, riesgos y dependencias.            | **Alta**    | `gore_indicadores.indicador` |
| **JPTIC-01**  | Como **Jefe de Proyecto TIC**, quiero gestionar equipo, cronograma y presupuesto, para ejecutar proyecto.                | Dado proyecto asignado; Cuando gestiono; Entonces tengo herramientas PM estándar.             | **Alta**    | `gore_workflow.proyecto`     |

---

## 11. MÓDULO CUMPLIMIENTO — Transparencia, Lobby y Probidad

**Dominio Ontológico:** `gore_normativo`, `gore_documental`
**Función GORE 4.0:** Normar
**Journeys:** J08, J11

| ID            | User Story                                                                                                                    | AC                                                                                            | Prioridad   | Entidad Ontológica          |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ----------- | --------------------------- |
| **TRANSP-01** | Como **Encargado de Transparencia**, quiero verificar actualización mensual de transparencia activa, para cumplir Ley 20.285. | Dado checklist TA; Cuando verifico; Entonces confirmo publicación de 27 antecedentes.         | **Alta**    | `gore_normativo.norma`      |
| **TRANSP-02** | Como **Encargado de Transparencia**, quiero gestionar solicitudes de acceso a información, para responder en plazo.           | Dado solicitud; Cuando gestiono; Entonces respondo en 20+10 días hábiles.                     | **Crítica** | `gore_documental.solicitud` |
| **LOBBY-01**  | Como **Encargado de Lobby**, quiero verificar registros de audiencias de autoridades, para cumplir Ley 20.730.                | Dado período; Cuando verifico; Entonces confirmo registros en leylobby.gob.cl.                | **Alta**    | `gore_normativo.norma`      |
| **LOBBY-02**  | Como **Encargado de Lobby**, quiero coordinar designación de sujetos pasivos, para mantener registro actualizado.             | Dado cambio organizacional; Cuando actualizo; Entonces lista de sujetos pasivos está vigente. | **Media**   | `gore_actores.persona`      |

---

## 12. MÓDULO MUNICIPAL — Actores de Ejecución Local

**Dominio Ontológico:** `gore_actores`, `gore_inversion`
**Función GORE 4.0:** Ejecutar
**Journeys:** J05, J06, J14

| ID         | User Story                                                                                                                           | AC                                                                                                      | Prioridad   | Entidad Ontológica           |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- | ----------- | ---------------------------- |
| **UF-01**  | Como **Unidad Formuladora Municipal**, quiero consultar guías y requisitos por mecanismo, para preparar postulación correcta.        | Dado mecanismo seleccionado; Cuando consulto; Entonces veo documentación requerida.                     | **Alta**    | `gore_documental.plantilla`  |
| **UF-02**  | Como **Unidad Formuladora Municipal**, quiero determinar vía de financiamiento usando árbol de decisión, para elegir track correcto. | Dado características de proyecto; Cuando uso wizard; Entonces obtengo recomendación fundamentada.       | **Crítica** | `codigo_track`               |
| **UF-03**  | Como **Unidad Formuladora Municipal**, quiero verificar elegibilidad FRIL antes de postular, para evitar inadmisibilidad.            | Dado proyecto; Cuando verifico; Entonces conozco si califica FRIL y qué requisitos específicos aplican. | **Alta**    | `gore_normativo.restriccion` |
| **UTR-01** | Como **Unidad Técnica Receptora**, quiero coordinar reunión de inicio con GORE, para clarificar roles y plazos.                      | Dado convenio firmado; Cuando solicito reunión; Entonces se coordina con supervisor GORE.               | **Alta**    | `gore_workflow.reunion`      |
| **UTR-02** | Como **Unidad Técnica Receptora**, quiero reportar avance periódico a Supervisor GORE, para cumplir obligaciones de seguimiento.     | Dado hito cumplido; Cuando reporto; Entonces supervisor es notificado y puede validar.                  | **Crítica** | `gore_ejecucion.avance_obra` |
| **UTR-03** | Como **Unidad Técnica Receptora**, quiero presentar rendición final en SISREC, para cerrar ciclo financiero.                         | Dado proyecto terminado; Cuando rindo; Entonces RTF recibe y puede aprobar.                             | **Crítica** | `gore_financiero.rendicion`  |

---

## 13. MÓDULO GOBIERNO CENTRAL — Actores de Control y Evaluación

**Dominio Ontológico:** `gore_integracion`, `gore_evaluacion`
**Función GORE 4.0:** Financiar + Normar
**Journeys:** JX01, JX03

| ID            | User Story                                                                                                            | AC                                                                                    | Prioridad   | Entidad Ontológica                |
| ------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ----------- | --------------------------------- |
| **MDSF-01**   | Como **Analista MDSF Regional**, quiero recibir postulación de IDI del GORE, para evaluar técnica y económicamente.   | Dado IPR enviada por GORE; Cuando recibo; Entonces inicia plazo de evaluación.        | **Crítica** | `gore_evaluacion.evaluacion_mdsf` |
| **MDSF-02**   | Como **Analista MDSF Regional**, quiero emitir RATE (RS/FI/OT/AD), para comunicar resultado de evaluación.            | Dado análisis completado; Cuando emito RATE; Entonces GORE es notificado.             | **Crítica** | `gore_evaluacion.resultado_rate`  |
| **DIPSES-01** | Como **Analista DIPRES/SES**, quiero evaluar Formulario de Diseño MML de PPR Glosa 06, para emitir RF.                | Dado formulario recibido; Cuando evalúo; Entonces emito RF o solicito correcciones.   | **Crítica** | `gore_evaluacion.evaluacion_mdsf` |
| **CGR-01**    | Como **Auditor CGR**, quiero verificar rendiciones en SISREC, para fiscalizar uso de fondos.                          | Dado acceso a SISREC; Cuando verifico; Entonces puedo detectar anomalías.             | **Crítica** | `gore_financiero.rendicion`       |
| **CGR-02**    | Como **Auditor CGR**, quiero fiscalizar oportunidad e integridad de DIP, para verificar probidad.                     | Dado acceso a sistema DIP; Cuando fiscalizo; Entonces puedo detectar incumplimientos. | **Alta**    | `gore_normativo.norma`            |
| **CPLT-01**   | Como **Fiscal CPLT**, quiero requerir información al GORE para resolver amparo, para garantizar acceso a información. | Dado amparo presentado; Cuando requiero; Entonces GORE debe responder en plazo.       | **Alta**    | `gore_documental.solicitud`       |
| **TCP-01**    | Como **Ministro TCP**, quiero requerir expediente de licitación impugnada, para resolver reclamación.                 | Dado reclamo presentado; Cuando requiero; Entonces GORE entrega antecedentes.         | **Alta**    | `gore_documental.expediente`      |

---

## 14. MÓDULO SECTORIAL — Actores RIS Específicos

**Dominio Ontológico:** `gore_evaluacion`, `gore_normativo`
**Función GORE 4.0:** Planificar
**Journeys:** JX01

| ID             | User Story                                                                                                                  | AC                                                                                                  | Prioridad | Entidad Ontológica                     |
| -------------- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | --------- | -------------------------------------- |
| **IND-01**     | Como **Profesional IND**, quiero revisar proyectos de infraestructura deportiva, para validar coherencia con políticas IND. | Dado proyecto deportivo; Cuando reviso; Entonces emito pronunciamiento técnico.                     | **Alta**  | `gore_evaluacion.evaluacion_sectorial` |
| **CMN-01**     | Como **Profesional CMN**, quiero revisar proyectos en inmuebles patrimoniales, para autorizar intervenciones.               | Dado proyecto en zona patrimonial; Cuando reviso; Entonces emito autorización o denegación fundada. | **Alta**  | `gore_evaluacion.evaluacion_sectorial` |
| **CULTURA-01** | Como **Profesional MINCAP**, quiero revisar iniciativas culturales FNDR, para verificar alineamiento sectorial.             | Dado proyecto cultural; Cuando reviso; Entonces valido coherencia con política cultural.            | **Media** | `gore_evaluacion.evaluacion_sectorial` |

---

## 15. MÓDULO L0 PERSONAS — Gestión del Capital Humano

**Dominio Ontológico:** `L0_Homeostasis.Gestion_Personas`
**Función GORE 4.0:** Transversal (Homeostasis organizacional)
**Journeys:** Ciclo de vida funcionario

### 15.1 Profesional GDP — Gestión de Personas

| ID             | User Story                                                                                                                                          | AC                                                                                                                 | Prioridad   | Entidad Ontológica                            |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ----------- | --------------------------------------------- |
| **GDP-AUS-01** | Como **Profesional GDP**, quiero gestionar solicitudes de feriado legal verificando saldo en cuenta corriente, para autorizar vacaciones.           | Dado solicitud de funcionario; Cuando verifico saldo; Entonces apruebo/rechazo con fundamento y actualizo cuenta.  | **Alta**    | `L0.Ausentismo.feriado_legal`                 |
| **GDP-AUS-02** | Como **Profesional GDP**, quiero registrar licencias médicas electrónicas (IMED/Medipass) y su resolución COMPIN/ISAPRE, para controlar ausentismo. | Dado licencia presentada; Cuando registro; Entonces estado funcionario cambia y se contabiliza.                    | **Crítica** | `L0.Ausentismo.licencia_medica`               |
| **GDP-AUS-03** | Como **Profesional GDP**, quiero gestionar permisos administrativos verificando máximo 6 días/año, para controlar saldo.                            | Dado solicitud permiso; Cuando verifico saldo; Entonces apruebo si hay disponibilidad.                             | **Alta**    | `L0.Ausentismo.permiso_administrativo`        |
| **GDP-AUS-04** | Como **Profesional GDP**, quiero tramitar comisiones de servicio y cometidos funcionales con resolución exenta, para formalizar ausencias.          | Dado requerimiento; Cuando tramito; Entonces genero resolución y calculo viático si corresponde.                   | **Alta**    | `L0.Ausentismo.comision_servicio`             |
| **GDP-AUS-05** | Como **Profesional GDP**, quiero registrar accidentes de trabajo (DIAT) y coordinar atención Mutual, para cumplir protocolo SSO.                    | Dado accidente notificado; Cuando registro; Entonces genero DIAT y derivo a Mutual.                                | **Crítica** | `L0.Ausentismo.accidente_trabajo`             |
| **GDP-REM-01** | Como **Profesional GDP**, quiero calcular liquidaciones mensuales aplicando Escala Única de Sueldos y asignaciones, para procesar remuneraciones.   | Dado período; Cuando proceso; Entonces genero liquidaciones con haberes, descuentos y líquido.                     | **Crítica** | `L0.Remuneraciones.Liquidacion`               |
| **GDP-REM-02** | Como **Profesional GDP**, quiero generar planilla Previred con cotizaciones previsionales, para cumplir obligación legal.                           | Dado liquidaciones aprobadas; Cuando genero; Entonces obtengo archivo para carga en Previred.                      | **Crítica** | `L0.Remuneraciones.integracion`               |
| **GDP-REM-03** | Como **Profesional GDP**, quiero emitir certificados de renta para Operación Renta, para entregar a funcionarios en marzo.                          | Dado año tributario; Cuando genero; Entonces cada funcionario tiene su certificado disponible.                     | **Alta**    | `L0.Remuneraciones.certificado_rentas`        |
| **GDP-REM-04** | Como **Profesional GDP**, quiero gestionar horas extraordinarias con Formularios N°1 y N°2, para reconocer tiempo compensado.                       | Dado autorización y ejecución; Cuando registro; Entonces acumulo tiempo compensado.                                | **Alta**    | `L0.Control_Asistencia.horas_extraordinarias` |
| **GDP-CAL-01** | Como **Profesional GDP**, quiero gestionar proceso de calificación anual coordinando precalificaciones y Junta Calificadora, para cumplir ciclo.    | Dado período calificatorio; Cuando coordino; Entonces se completa proceso sept-nov.                                | **Alta**    | `L0.Calificaciones`                           |
| **GDP-CAL-02** | Como **Jefe Directo**, quiero precalificar funcionarios de mi área evaluando factores de desempeño, para alimentar Junta.                           | Dado funcionario asignado; Cuando precalifico; Entonces registro notas por subfactor con comentarios.              | **Crítica** | `L0.Calificaciones.precalificacion`           |
| **GDP-CAL-03** | Como **Profesional GDP**, quiero registrar anotaciones de mérito/demérito en hoja de vida, para documentar desempeño.                               | Dado evento relevante; Cuando registro anotación; Entonces queda en hoja de vida para calificación.                | **Alta**    | `L0.Calificaciones.anotaciones`               |
| **GDP-SEL-01** | Como **Profesional GDP**, quiero gestionar concursos públicos para cargos vacantes, para proveer dotación.                                          | Dado cargo vacante; Cuando proceso concurso; Entonces ejecuto fases: bases, postulación, evaluación, nombramiento. | **Alta**    | `L0.Desarrollo_Personas.Seleccion`            |
| **GDP-SEL-02** | Como **Profesional GDP**, quiero ejecutar programa de inducción para funcionarios nuevos, para integrarlos a la institución.                        | Dado nuevo ingreso; Cuando activo inducción; Entonces se ejecutan fases: bienvenida, informativa, cargo.           | **Alta**    | `L0.Desarrollo_Personas.Induccion`            |
| **GDP-CAP-01** | Como **Profesional GDP**, quiero gestionar Plan Anual de Capacitación registrando cursos y certificados, para desarrollar competencias.             | Dado plan aprobado; Cuando gestiono; Entonces funcionarios acceden a capacitaciones y registro certificados.       | **Alta**    | `L0.Desarrollo_Personas.Capacitacion`         |

### 15.2 Funcionario GORE

| ID              | User Story                                                                                                                              | AC                                                                                          | Prioridad | Entidad Ontológica                     |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | --------- | -------------------------------------- |
| **FUNC-AUS-01** | Como **Funcionario GORE**, quiero solicitar feriado legal electrónicamente verificando mi saldo disponible, para planificar vacaciones. | Dado mi cuenta corriente; Cuando solicito; Entonces veo saldo y envío solicitud a jefatura. | **Alta**  | `L0.Ausentismo.feriado_legal`          |
| **FUNC-AUS-02** | Como **Funcionario GORE**, quiero solicitar permiso administrativo electrónicamente, para gestionar ausencias cortas.                   | Dado saldo permisos; Cuando solicito; Entonces jefatura recibe para autorización.           | **Alta**  | `L0.Ausentismo.permiso_administrativo` |
| **FUNC-REM-01** | Como **Funcionario GORE**, quiero ver mi liquidación de sueldo mensual, para conocer mis haberes y descuentos.                          | Dado mes pagado; Cuando consulto; Entonces veo detalle de liquidación.                      | **Alta**  | `L0.Remuneraciones.Liquidacion`        |
| **FUNC-CAP-01** | Como **Funcionario GORE**, quiero inscribirme en cursos del Plan de Capacitación, para desarrollar mis competencias.                    | Dado catálogo de cursos; Cuando me inscribo; Entonces queda registrada mi participación.    | **Media** | `L0.Desarrollo_Personas.Capacitacion`  |

---

## 16. MÓDULO L0 ACTIVOS — Gestión de Bienes y Servicios

**Dominio Ontológico:** `L0_Homeostasis.Gestion_Activos_Servicios`
**Función GORE 4.0:** Transversal (Homeostasis organizacional)
**Journeys:** Ciclo de compras, Inventario, Activo fijo

### 16.1 Profesional Abastecimiento (ABS)

| ID             | User Story                                                                                                                                                  | AC                                                                                                   | Prioridad   | Entidad Ontológica                 |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ----------- | ---------------------------------- |
| **ABS-COM-01** | Como **Profesional Abastecimiento**, quiero mantener Plan Anual de Compras alineado con presupuesto, para planificar adquisiciones.                         | Dado presupuesto aprobado; Cuando configuro plan; Entonces tengo calendario de compras.              | **Alta**    | `L0.Ciclo_Compras.planificado`     |
| **ABS-COM-02** | Como **Profesional Abastecimiento**, quiero tramitar solicitudes de compra verificando CDP, para iniciar proceso de adquisición.                            | Dado requerimiento de unidad; Cuando verifico CDP; Entonces paso a proceso licitación/trato directo. | **Crítica** | `L0.Ciclo_Compras.requerido`       |
| **ABS-COM-03** | Como **Profesional Abastecimiento**, quiero publicar licitaciones en Mercado Público con bases técnicas, para ejecutar compra pública.                      | Dado proceso aprobado; Cuando publico; Entonces proveedores pueden ofertar.                          | **Crítica** | `L0.Ciclo_Compras.en_proceso`      |
| **ABS-COM-04** | Como **Profesional Abastecimiento**, quiero evaluar ofertas y adjudicar según criterios técnico-económicos, para seleccionar proveedor.                     | Dado ofertas recibidas; Cuando evalúo; Entonces adjudico al mejor evaluado.                          | **Crítica** | `L0.Ciclo_Compras.adjudicado`      |
| **ABS-COM-05** | Como **Profesional Abastecimiento**, quiero emitir órdenes de compra en Mercado Público, para comprometer gasto.                                            | Dado adjudicación; Cuando emito OC; Entonces proveedor puede entregar.                               | **Crítica** | `L0.Ciclo_Compras.comprometido`    |
| **ABS-COM-06** | Como **Profesional Abastecimiento**, quiero gestionar contratos con hoja de vida, garantías y alertas de vencimiento, para controlar ejecución contractual. | Dado contrato vigente; Cuando gestiono; Entonces tengo control de hitos, garantías y renovaciones.   | **Alta**    | `L0.Ciclo_Compras.Contratos`       |
| **ABS-BOD-01** | Como **Encargado de Bodega**, quiero registrar ingresos de productos por orden de compra, para mantener stock actualizado.                                  | Dado producto recepcionado; Cuando registro; Entonces stock aumenta y se genera documento ingreso.   | **Alta**    | `L0.Bodegas.ingreso`               |
| **ABS-BOD-02** | Como **Encargado de Bodega**, quiero despachar solicitudes de consumo de unidades, para abastecer áreas.                                                    | Dado solicitud aprobada; Cuando despacho; Entonces stock disminuye y receptor firma conformidad.     | **Alta**    | `L0.Bodegas.egreso`                |
| **ABS-BOD-03** | Como **Encargado de Bodega**, quiero realizar toma de inventario físico, para conciliar con sistema.                                                        | Dado planificación inventario; Cuando ejecuto conteo; Entonces genero ajustes por diferencia.        | **Alta**    | `L0.Bodegas.Toma_Inventario`       |
| **ABS-AF-01**  | Como **Profesional Control Patrimonial**, quiero dar alta a bienes con codificación y asignación de responsable, para control patrimonial.                  | Dado bien recepcionado; Cuando doy alta; Entonces inicia depreciación y queda asignado.              | **Crítica** | `L0.Activo_Fijo.alta`              |
| **ABS-AF-02**  | Como **Profesional Control Patrimonial**, quiero tramitar traslados de bienes entre unidades, para mantener ubicación actualizada.                          | Dado solicitud traslado; Cuando proceso; Entonces cambio ubicación y responsable con acta.           | **Alta**    | `L0.Activo_Fijo.traslado`          |
| **ABS-AF-03**  | Como **Profesional Control Patrimonial**, quiero tramitar baja de bienes por obsolescencia/deterioro/pérdida, para depurar inventario.                      | Dado bien inutilizable; Cuando tramito baja; Entonces genero resolución y actualizo inventario.      | **Alta**    | `L0.Activo_Fijo.baja`              |
| **ABS-AF-04**  | Como **Profesional Control Patrimonial**, quiero ejecutar inventario físico anual de activo fijo, para conciliar patrimonio.                                | Dado período anual; Cuando ejecuto inventario; Entonces genero informe con diferencias.              | **Crítica** | `L0.Activo_Fijo.Inventario_Fisico` |
| **ABS-MAN-01** | Como **Profesional Servicios Generales**, quiero gestionar órdenes de trabajo para mantención preventiva/correctiva, para preservar activos.                | Dado activo con necesidad; Cuando genero OT; Entonces se asigna técnico y ejecuta mantención.        | **Alta**    | `L0.Mantenimiento.Orden_Trabajo`   |
| **ABS-FLO-01** | Como **Encargado de Flota**, quiero gestionar solicitudes de uso de vehículos institucionales, para asignar pool vehicular.                                 | Dado solicitud de unidad; Cuando evalúo; Entonces asigno vehículo y conductor.                       | **Alta**    | `L0.Flota_Vehicular.solicitud_uso` |
| **ABS-FLO-02** | Como **Encargado de Flota**, quiero controlar kilometraje, combustible y mantenciones de cada vehículo, para gestionar flota.                               | Dado vehículo asignado; Cuando registro uso; Entonces tengo bitácora actualizada.                    | **Alta**    | `L0.Flota_Vehicular.control`       |

---

## 17. MÓDULO L0 BIENESTAR — Gestión de Beneficios Funcionarios

**Dominio Ontológico:** `L0_Homeostasis.Gestion_Bienestar`
**Función GORE 4.0:** Transversal (Homeostasis organizacional)
**Journeys:** Afiliación, Beneficios, Préstamos

### 17.1 Profesional Bienestar (BIEN)

| ID              | User Story                                                                                                                                                    | AC                                                                                                     | Prioridad   | Entidad Ontológica                    |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ----------- | ------------------------------------- |
| **BIEN-AF-01**  | Como **Profesional Bienestar**, quiero gestionar afiliaciones de funcionarios al Servicio de Bienestar, para habilitar beneficios.                            | Dado funcionario activo; Cuando afilio; Entonces queda como socio con descuento cuota mensual.         | **Alta**    | `L0.Bienestar.Afiliacion`             |
| **BIEN-AF-02**  | Como **Profesional Bienestar**, quiero gestionar grupo familiar de socios (cónyuge, hijos, padres), para extender beneficios.                                 | Dado socio activo; Cuando registro cargas; Entonces grupo familiar accede a beneficios.                | **Alta**    | `L0.Bienestar.Grupo_Familiar`         |
| **BIEN-BON-01** | Como **Profesional Bienestar**, quiero procesar solicitudes de bonificación médica verificando tope anual, para reembolsar gastos de salud.                   | Dado gasto médico documentado; Cuando proceso; Entonces calculo bonificación y liquido pago.           | **Crítica** | `L0.Bienestar.Bonificaciones_Medicas` |
| **BIEN-SUB-01** | Como **Profesional Bienestar**, quiero tramitar subsidios por eventos (natalidad, matrimonio, fallecimiento, escolaridad), para apoyar a socios.              | Dado evento documentado; Cuando tramito; Entonces entrego subsidio según política.                     | **Alta**    | `L0.Bienestar.Subsidios`              |
| **BIEN-PRE-01** | Como **Profesional Bienestar**, quiero evaluar y otorgar préstamos verificando capacidad de endeudamiento, para financiar necesidades de socios.              | Dado solicitud de préstamo; Cuando evalúo; Entonces apruebo/rechazo y genero pagaré si corresponde.    | **Crítica** | `L0.Bienestar.Prestamos`              |
| **BIEN-PRE-02** | Como **Profesional Bienestar**, quiero gestionar descuento de cuotas de préstamos en planilla de remuneraciones, para recuperar créditos.                     | Dado préstamo vigente; Cuando proceso mes; Entonces descuento cuota automáticamente.                   | **Alta**    | `L0.Bienestar.Prestamos.descuento`    |
| **BIEN-CON-01** | Como **Profesional Bienestar**, quiero administrar convenios con terceros (comercio, educación, salud), para ofrecer beneficios a socios.                     | Dado convenio suscrito; Cuando administro; Entonces socios pueden inscribirse y descontar en planilla. | **Alta**    | `L0.Bienestar.Convenios_Terceros`     |
| **BIEN-SSO-01** | Como **Profesional Bienestar**, quiero coordinar con Mutual de Seguridad la gestión de accidentes laborales/trayecto, para atender funcionarios accidentados. | Dado accidente notificado; Cuando coordino; Entonces funcionario es atendido y se gestiona subsidio.   | **Crítica** | `L0.Bienestar.SSO.Mutual`             |
| **BIEN-SSO-02** | Como **Profesional Bienestar**, quiero apoyar al CPHS en investigación de accidentes y propuestas de prevención, para mejorar SSO.                            | Dado accidente ocurrido; Cuando investigo con CPHS; Entonces genero informe con recomendaciones.       | **Alta**    | `L0.Bienestar.SSO.CPHS`               |

### 17.2 Socio Bienestar (Funcionario)

| ID             | User Story                                                                                                                           | AC                                                                                         | Prioridad | Entidad Ontológica                    |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | --------- | ------------------------------------- |
| **SOC-BON-01** | Como **Socio Bienestar**, quiero solicitar bonificación médica electrónicamente adjuntando boletas/facturas, para obtener reembolso. | Dado gasto de salud; Cuando solicito; Entonces Bienestar procesa y paga.                   | **Alta**  | `L0.Bienestar.Bonificaciones_Medicas` |
| **SOC-PRE-01** | Como **Socio Bienestar**, quiero solicitar préstamo verificando mi capacidad de endeudamiento, para financiar necesidad.             | Dado mi saldo y capacidad; Cuando solicito; Entonces veo condiciones y presento solicitud. | **Alta**  | `L0.Bienestar.Prestamos`              |
| **SOC-CTA-01** | Como **Socio Bienestar**, quiero ver mi cuenta corriente con beneficios otorgados y préstamos vigentes, para conocer mi situación.   | Dado mi perfil; Cuando consulto; Entonces veo historial y saldos.                          | **Alta**  | `L0.Bienestar.Cuenta_Corriente_Socio` |

---

---

## 18. MÓDULO L4 COMPETENCIAS — Gestión de Transferencias
**Dominio Ontológico:** `L4_Competencias`, `gore_gobernanza`
**Función GORE 4.0:** Normar + Planificar
**Journeys:** J10 Transferencia Competencias

### 18.1 Autoridades y Planificación

| ID               | User Story                                                                                                                                              | AC                                                                                                            | Prioridad   | Entidad Ontológica                 |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ----------- | ---------------------------------- |
| **GORE-COMP-01** | Como **Gobernador Regional**, quiero invocar la solicitud de transferencia de una competencia (Art. 114 CPR), para aumentar autonomía regional.         | Dado estudio justificativo; Cuando firmo solicitud; Entonces se envía oficio a Presidencia y SUBDERE.         | **Crítica** | `L4.Competencia.Solicitud`         |
| **GORE-COMP-02** | Como **Consejero Regional**, quiero aprobar por mayoría absoluta la solicitud de competencia, para cumplir requisito legal de origen.                   | Dado propuesta de Gobernador; Cuando voto favorablemente; Entonces se certifica el acuerdo para el oficio.    | **Crítica** | `gore_gobernanza.acuerdo_core`     |
| **GORE-COMP-03** | Como **Profesional DIPLADE**, quiero elaborar el informe de capacidad financiera y administrativa, para justificar la aptitud del GORE.                 | Dado análisis interno; Cuando documento; Entonces genero anexo técnico requerido por Comité Interministerial. | **Alta**    | `L4.Competencia.Informe_Capacidad` |
| **GORE-COMP-04** | Como **Jefe DIPLADE**, quiero monitorear el estado de la solicitud en el Comité Interministerial (6 meses plazo), para gestionar lobby si es necesario. | Dado solicitud enviada; Cuando consulto estado; Entonces veo días transcurridos y etapa en nivel central.     | **Alta**    | `L4.Competencia.Transferencia`     |

---

## 19. MÓDULO Lω EVOLUCIÓN — Gestión del Cambio
**Dominio Ontológico:** `Lomega_Evolucion`, `gore_tic`
**Función GORE 4.0:** Transversal (Meta-Bucle)
**Journeys:** J23 Planificación GORE 4.0

### 19.1 Gestión del Cambio y Deuda Técnica

| ID              | User Story                                                                                                                                 | AC                                                                                                           | Prioridad   | Entidad Ontológica      |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ | ----------- | ----------------------- |
| **GORE-EVO-01** | Como **Administrador del Sistema**, quiero registrar una nueva versión del esquema ontológico (v4.x), para controlar evolución del modelo. | Dado cambio semántico; Cuando registro versión; Entonces el sistema versiona las entidades afectadas.        | **Alta**    | `Lomega.Version_Schema` |
| **GORE-EVO-02** | Como **Encargado TDE**, quiero visualizar métricas de Deuda Técnica Categórica, para planificar refactorizaciones del sistema.             | Dado dashboard de evolución; Cuando consulto; Entonces veo score de deuda técnica y áreas críticas.          | **Media**   | `Lomega.Deuda_Tecnica`  |
| **GORE-EVO-03** | Como **Administrador del Sistema**, quiero gestionar migraciones de datos entre versiones del esquema, para asegurar integridad.           | Dado actualización de modelo; Cuando ejecuto migración; Entonces datos antiguos se adaptan al nuevo esquema. | **Crítica** | `Lomega.Migracion`      |

---

## 20. MATRIZ AMPLIADA DE TRAZABILIDAD

### 18.1 User Stories × Módulos GORE OS (Ampliada)

| Módulo           | Stories | Críticas | Altas  | Medias |
| ---------------- | ------- | -------- | ------ | ------ |
| IPR              | 32      | 22       | 8      | 2      |
| Presupuesto      | 12      | 8        | 4      | 0      |
| Convenios        | 12      | 8        | 4      | 0      |
| Ejecución/Crisis | 35      | 24       | 9      | 2      |
| CORE/Gobernanza  | 17      | 10       | 5      | 2      |
| Administración   | 8       | 1        | 6      | 1      |
| Territorial      | 4       | 1        | 3      | 0      |
| CIES             | 5       | 3        | 2      | 0      |
| IDE/GIS          | 6       | 0        | 6      | 0      |
| TIC/TDE          | 8       | 1        | 7      | 0      |
| Cumplimiento     | 4       | 1        | 2      | 1      |
| Municipal        | 6       | 3        | 3      | 0      |
| Gob. Central     | 7       | 4        | 3      | 0      |
| Sectorial        | 3       | 0        | 2      | 1      |
| **L0 Personas**  | **19**  | **6**    | **12** | **1**  |
| **L0 Activos**   | **16**  | **6**    | **10** | **0**  |
| **L0 Bienestar** | **12**  | **4**    | **8**  | **0**  |
| **L4 Comp.**     | **4**   | **2**    | **2**  | **0**  |
| **Lω Evol.**     | **3**   | **1**    | **1**  | **1**  |
| **TOTAL**        | **220** | **110**  | **94** | **12** |

### 15.2 Journeys Críticos Cubiertos

| Journey   | Nombre                       | Módulos                     |
| --------- | ---------------------------- | --------------------------- |
| J01-J07   | Ciclo IPR Completo           | IPR, Presupuesto, Convenios |
| J08       | Solicitud Acceso Información | Cumplimiento                |
| J11       | Probidad y DIP               | Cumplimiento                |
| J13       | Sesiones CORE                | Gobernanza                  |
| J14       | Postulación FRIL             | IPR, Municipal              |
| J18       | Ciclo Presupuestario         | Presupuesto                 |
| J19       | Rendiciones SISREC           | Convenios                   |
| J20       | Respuesta Incidente CIES     | CIES                        |
| J21       | Publicación Capa Geoespacial | IDE/GIS                     |
| J22       | Inversión TIC EVALTIC        | TIC                         |
| J23       | Planificación GORE 4.0       | Territorial                 |
| JX01-JX09 | Journeys Expandidos          | Multi-módulo                |

---

## 16. MATRIZ DE USUARIOS DEL GEMELO DIGITAL

### Esfera 1: Núcleo GORE (~250 usuarios)

| Rol                     | Cantidad | Criticidad | Módulos                |
| ----------------------- | -------- | ---------- | ---------------------- |
| Gobernador Regional     | 1        | Crítica    | CORE, IPR              |
| Consejeros Regionales   | 16       | Alta       | CORE                   |
| Administrador Regional  | 1        | Alta       | Ejecución              |
| Jefes de División       | 8        | Alta       | Todos                  |
| Analistas DIPIR         | ~15      | Crítica    | IPR                    |
| Supervisores Proyecto   | ~10      | Crítica    | Ejecución              |
| Profesionales DAF       | ~15      | Alta       | Presupuesto, Convenios |
| UCR                     | ~5       | Alta       | Convenios              |
| Control Interno         | ~5       | Alta       | Todos                  |
| CDR                     | ~10      | Alta       | IPR                    |
| Operadores CIES         | ~12      | Crítica    | CIES                   |
| Equipo UGIT             | ~5       | Alta       | IDE/GIS                |
| PMO TIC                 | ~3       | Alta       | TIC                    |
| Encargados Cumplimiento | ~4       | Alta       | Cumplimiento           |

### Esfera 2: Ecosistema Gubernamental (~200 usuarios)

| Actor                 | Cantidad | Criticidad | Módulos              |
| --------------------- | -------- | ---------- | -------------------- |
| MDSF Regional         | ~3       | Crítica    | IPR                  |
| DIPRES/SES            | ~5       | Alta       | IPR, Presupuesto     |
| CGR                   | ~5       | Crítica    | Todos                |
| Municipalidades (UF)  | ~42      | Crítica    | Municipal, IPR       |
| Municipalidades (UTR) | ~42      | Crítica    | Municipal, Ejecución |
| SEREMI                | ~20      | Media      | Territorial          |
| CPLT                  | ~3       | Alta       | Cumplimiento         |
| IND/CMN/MINCAP        | ~9       | Alta       | Sectorial            |

### Esfera 3: Ecosistema Regional (~506,000 usuarios)

| Actor      | Cantidad | Criticidad | Módulos       |
| ---------- | -------- | ---------- | ------------- |
| Ciudadanía | ~500,000 | Alta       | Transparencia |
| OSC        | ~1,000   | Media      | Municipal     |
| Empresas   | ~7,000   | Media      | IPR           |
| Academia   | ~500     | Media      | IDE/GIS       |

---

> **Nota Metodológica:** Este documento consolida user stories derivadas de 7 fuentes documentales, alineadas con la ontología categórica GORE Ñuble v4.1 y la visión GORE OS. Cada story fue diseñada para ser atómica, testeable y trazable a entidades del modelo de datos.

---

*Documento generado: 2025-12-11*
*Proyecto: GORE_OS — Sistema Operativo Cognitivo Regional*
*Agente: Ingeniero Software Composicional*

