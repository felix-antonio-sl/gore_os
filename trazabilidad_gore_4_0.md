# Trazabilidad: Funciones GORE 4.0 → Módulos GORE OS

**Versión:** 1.0.0  
**Fecha:** 2025-12-03  
**Basado en:** `kb_gn_900_gore_ideal_koda.yml` + modelo IS-GORE v4.1 + artefactos KODA de gestión (`kb_gn_018`, `kb_gn_019`, `kb_gn_020`, `kb_gn_011`) + `vision_gore_os.md`

---

## 0. Propósito del Documento

Este artefacto define la **trazabilidad explícita** entre las cinco funciones motoras del GORE 4.0:

- Planificar  
- Financiar  
- Ejecutar  
- Coordinar  
- Normar  

y los componentes de **GORE OS**:

- Módulos funcionales (IPR, Presupuesto, Convenios, Ejecución/Crisis, Rendiciones, CORE).  
- Capas cognitivas (Sensing, Clasificador, Alertas, Predictor).  
- Dominios y entidades del modelo IS-GORE v4.1.  
- Artefactos KODA que definen semántica y procesos.  
- Usuarios y casos de uso prioritarios.

La intención es que cada decisión de diseño/implementación de GORE OS pueda rastrearse hacia una necesidad institucional del GORE 4.0, pasando **siempre** por el modelo de datos y los artefactos KODA.

---

## 1. Planificar → GORE OS

### 1.1 Resumen de la función en GORE Ideal / GORE 4.0

Referencia: `Motor_Cinco_Funciones → Planificar`, `Funcion_Planificar_4_0`.

- **Misión:** posicionar al GORE como **arquitecto del territorio inteligente** mediante planificación basada en datos y simulaciones.  
- **Capacidades clave:**
  - Gemelo Digital del territorio (`Gemelo Digital del territorio`).
  - ERD y PROT como capas lógicas vinculantes para cada iniciativa.  
  - Centro de inteligencia territorial con datos en tiempo real.  
  - Uso de convenios/ARI como herramientas de simulación y co-diseño con el nivel central.  
  - Participación ciudadana aumentada por IA.

### 1.2 Mapa de trazabilidad (Planificar → GORE OS)

| Capacidad GORE 4.0 | Módulos / Capas GORE OS | Dominios / entidades IS-GORE v4.1 | Artefactos KODA | Usuarios / casos de uso |
|--------------------|-------------------------|-----------------------------------|------------------|-------------------------|
| Gemelo Digital del territorio | Capa **Sensing** (Gemelo Digital Regional) | `gore_territorial` (unidades territoriales, brechas), `gore_indicadores` (KPIs), `gore_eventos` (eventos de ciclo de vida) | `Funcion_Planificar_4_0` (Dimensiones: Gemelo Digital, Centro de inteligencia territorial) | DIPLADE, Gobernador/a, equipo de planificación: análisis de brechas y escenarios territoriales. |
| ERD/PROT como capas lógicas vinculantes | Módulo **IPR** + Capa Sensing | `gore_planificacion.instrumento_planificacion`, `gore_planificacion.objetivo_estrategico`, `gore_inversion.iniciativa` | `Funcion_Planificar_4_0` (ERD y PROT como capas lógicas vinculantes) + `kb_gn_019` (gestión IPR) | DIPLADE y DIPIR: chequeo automático de alineamiento de iniciativas con ERD/PROT. |
| Centro de inteligencia territorial | Capa **Reasoning** (Predictor de riesgo, analítica de portafolio) | `gore_territorial`, `gore_indicadores`, `gore_riesgos`, `gore_eventos` | `Funcion_Planificar_4_0` (Centro de inteligencia territorial) | Gobernador/a y Jefaturas: tablero de planificación con proyecciones de impacto territorial. |
| ARI y convenios como herramientas de co-diseño | Módulo **Presupuesto** + Módulo **Convenios/CORE** | `gore_planificacion` (ARI), dominios financieros que usan `public.estado_convenio`, `public.estado_cuota` | `Funcion_Planificar_4_0` (Convenios y ARI como herramientas de co-diseño) + `kb_gn_018` | Gobernador/a, DIPIR, DAF, CORE: negociación ARI/FNDR con el nivel central apoyada en simulaciones. |
| Participación ciudadana aumentada por IA | Cockpits abiertos + Capa Reasoning | `gore_indicadores` (metas públicas), `gore_eventos` (participación), `gore_documental` (actas, consultas) | `Funcion_Planificar_4_0` (Participación ciudadana aumentada por IA) | Ciudadanía, CORE, Gobernador/a: consulta de planes e indicadores con explicaciones generadas por IA. |

### 1.3 Entidades y enums clave (Planificar)

- `gore_planificacion.instrumento_planificacion` (ERD, PROT, ARI y otros).  
- `gore_planificacion.objetivo_estrategico`.  
- Entidades territoriales en `gore_territorial`.  
- Indicadores y metas (`gore_indicadores`).

---

## 2. Financiar → GORE OS

### 2.1 Resumen de la función en GORE Ideal / GORE 4.0

Referencia: `Motor_Cinco_Funciones → Financiar`, `Funcion_Financiar_4_0`, `Limites_Funcion_Financiar`.

- **Misión:** transformar al GORE en una **banca de desarrollo regional inteligente** que maximiza el impacto de cada peso público.  
- **Capacidades clave:**
  - Financiamiento estratégico y catalítico alineado con la ERD.  
  - Portafolio diversificado de instrumentos (FNDR, FRPD, ISAR, etc.).  
  - Trazabilidad total y controles externos (MDSF, DIPRES, CGR, CORE).  
  - Ventanilla única digital con asistencia de IA para proponentes.

### 2.2 Mapa de trazabilidad (Financiar → GORE OS)

| Capacidad GORE 4.0 | Módulos / Capas GORE OS | Dominios / entidades IS-GORE v4.1 | Artefactos KODA | Usuarios / casos de uso |
|--------------------|-------------------------|-----------------------------------|------------------|-------------------------|
| Financiamiento estratégico según ERD | Módulo **IPR** + Módulo **Presupuesto** | `gore_inversion.iniciativa`, dominios presupuestarios que usan `gore_presupuesto.tipo_movimiento_presupuestario` | `Funcion_Financiar_4_0` (Financiamiento estratégico y catalítico) + `kb_gn_019` (ciclo IPR) + `kb_gn_018` (ciclo presupuestario) | Gobernador/a, DIPIR, DAF, CORE: priorización de cartera IPR según impacto y alineamiento. |
| Portafolio diversificado de fondos (FNDR, FRPD, ISAR) | Módulo **Presupuesto** | `gore_presupuesto` (estructuras de asignación y movimientos por programa/fondo) | `Funcion_Financiar_4_0` (Portafolio diversificado) + `Limites_Funcion_Financiar` | DAF, DIPIR: diseño de combinaciones de fondos y seguimiento de topes/eligibilidad. |
| Control técnico MDSF (RS) | Módulo **IPR** (evaluación) | Tablas de evaluación que usan `public.entidad_evaluadora`, `public.estado_bip` | `Limites_Funcion_Financiar` (control técnico MDSF) + `kb_gn_019` | DIPIR: asegurar RS previa a financiamiento; seguimiento de estado BIP. |
| Control presupuestario DIPRES y CORE | Módulo **Presupuesto** + Módulo **CORE** | Dominios presupuestarios (`gore_presupuesto`) y de gobernanza (`gore_gobernanza`) | `Limites_Funcion_Financiar` (control DIPRES, CORE y umbral 7.000 UTM) + `kb_gn_018` | DAF, Gobernador/a, CORE: visibilidad de arquitectura programática, modificaciones y acuerdos. |
| Trazabilidad de transferencias y cuotas | Módulo **Convenios y Transferencias** | Dominios financieros que usan `public.estado_convenio`, `public.estado_cuota`, `public.estado_estado_pago` | `kb_gn_019` (formalización y devengos) + `kb_gn_020` (rendiciones) | DAF, RTF, ejecutores: programación de pagos y control de estados de convenios/cuotas. |
| Ventanilla única digital para proponentes | Cockpit **Formulador Externo** + Capa Reasoning | `gore_inversion.iniciativa`, `gore_documental` (antecedentes), `gore_workflow` (tareas) | `Funcion_Financiar_4_0` (ventanilla única con IA) + `kb_gn_011` (selector IPR) | Proponentes externos, municipios y servicios: apoyo en selección de vía y armado de expediente. |

### 2.3 Entidades y enums clave (Financiar)

- `gore_inversion.iniciativa`.  
- Enum `public.codigo_track` (SNI_COMPLETO, SNI_SIMPLIFICADO, GLOSA06_BIFASICO, CONCURSO_FRPD, CONCURSO_8, EXENTO_FRIL, CIRCULAR_33, OTRO).  
- Enum `public.entidad_evaluadora`.  
- Enum `public.estado_convenio`, `public.estado_cuota`, `public.estado_estado_pago`.  
- Enum `gore_presupuesto.tipo_movimiento_presupuestario`.

---

## 3. Ejecutar → GORE OS

### 3.1 Resumen de la función en GORE Ideal / GORE 4.0

Referencia: `Motor_Cinco_Funciones → Ejecutar`, `Funcion_Ejecutar_4_0`, `Limites_Funcion_Ejecutar`.

- **Misión:** consolidar al GORE como **orquestador de la ejecución 4.0**, garantizando calidad y oportunidad más que "hacer directamente las obras".  
- **Capacidades clave:**
  - PMO Regional como torre de control de convenios y obras.  
  - Programas habilitantes (capacidad institucional, digitalización, soporte a ejecutores).  
  - Unidades de desbloqueo de cuellos de botella, aumentadas por IA.

### 3.2 Mapa de trazabilidad (Ejecutar → GORE OS)

| Capacidad GORE 4.0 | Módulos / Capas GORE OS | Dominios / entidades IS-GORE v4.1 | Artefactos KODA | Usuarios / casos de uso |
|--------------------|-------------------------|-----------------------------------|------------------|-------------------------|
| PMO Regional como torre de control | Módulo **Ejecución y Crisis** + Cockpits ejecutivos | `gore_ejecucion` (avance de iniciativas, estados de pago, problemas, compromisos, alertas) | `Funcion_Ejecutar_4_0` (PMO Regional) + `kb_gn_019` (fase de ejecución) | DIPIR, DAF, Gobernador/a, Jefaturas divisionales: monitoreo de avance físico/financiero y riesgos. |
| Detección temprana de riesgos en ejecución | Capa **Reasoning** (Detector de anomalías, Predictor de riesgo) | `gore_ejecucion` + `gore_riesgos` + `gore_eventos` | `Funcion_Ejecutar_4_0` (torre de control predictiva) | Unidad de seguimiento, DIPIR, PMO regional: predicción de retrasos, sobrecostos, riesgo de rendición. |
| Unidades de desbloqueo (problemas y cuellos de botella) | Módulo **Ejecución y Crisis** (Problemas, Compromisos) | Tablas de crisis definidas en la extensión v4.1: `gore_ejecucion.problema_ipr`, `gore_ejecucion.compromiso_operativo`, `gore_ejecucion.alerta_ipr`, enums `estado_problema_ipr`, `impacto_problema_ipr`, `prioridad_compromiso` | `Funcion_Ejecutar_4_0` (Unidades de desbloqueo) + doc `extension_crisis_v4_1` | Analista DIPIR, Jefatura divisional, encargados operativos: registro y gestión de problemas y compromisos. |
| Programas habilitantes y soporte a ejecutores | Módulo **Rendiciones** + Cockpit para ejecutores | Dominios financieros y de integración con SISREC (`public.estado_expediente_sisrec`) + `gore_documental` (expedientes) | `Funcion_Ejecutar_4_0` (programas habilitantes) + `kb_gn_020` (gestión de rendiciones) | Ejecutores (municipios, servicios), RTF, U.C.R.: reducción de fricción en ciclo de ejecución y rendición. |

### 3.3 Entidades y enums clave (Ejecutar)

- `gore_inversion.iniciativa` (ampliada con campos de alerta/nivel riesgo según `extension_crisis_v4_1`).  
- `gore_ejecucion.problema_ipr`, enum `gore_ejecucion.tipo_problema_ipr`, `gore_ejecucion.estado_problema_ipr`, `gore_ejecucion.impacto_problema_ipr`.  
- `gore_ejecucion.compromiso_operativo`, enum `gore_ejecucion.estado_compromiso`, `gore_ejecucion.prioridad_compromiso`.  
- `gore_ejecucion.alerta_ipr`, enum `gore_ejecucion.tipo_alerta_ipr`, `gore_ejecucion.nivel_alerta_ipr`.  
- Enum `public.estado_expediente_sisrec`.

---

## 4. Coordinar → GORE OS

### 4.1 Resumen de la función en GORE Ideal / GORE 4.0

Referencia: `Motor_Cinco_Funciones → Coordinar`, `Funcion_Coordinar_4_0`, `Limites_Funcion_Coordinar`.

- **Misión:** convertir al GORE en una **plataforma de gobernanza como servicio (GaaP)**, habilitando colaboración descentralizada entre actores públicos y privados.  
- **Capacidades clave:**
  - Co-diseño vertical con el nivel central usando datos y simulaciones.  
  - Sincronización horizontal del aparato público regional.  
  - Empoderamiento territorial de los municipios.  
  - Articulación ampliada mediante APIs y datos abiertos.

### 4.2 Mapa de trazabilidad (Coordinar → GORE OS)

| Capacidad GORE 4.0 | Módulos / Capas GORE OS | Dominios / entidades IS-GORE v4.1 | Artefactos KODA | Usuarios / casos de uso |
|--------------------|-------------------------|-----------------------------------|------------------|-------------------------|
| Co-diseño vertical con nivel central | Módulo **CORE** + Capa Sensing/Reasoning | `gore_gobernanza.sesion_core`, `gore_gobernanza.acuerdo_core`, `gore_planificacion` (ARI), dominios presupuestarios | `Funcion_Coordinar_4_0` (co-diseño vertical) + `kb_gn_018` (ARI) | Gobernador/a, CORE, DIPRES, ministerios sectoriales: negociación basada en evidencia y simulaciones. |
| Sincronización horizontal del aparato público | Capa **Integraciones** + modelo unificado IS-GORE v4.1 | `gore_integracion.sistema_externo`, `gore_integracion.sincronizacion`, 21 dominios integrados | `Funcion_Coordinar_4_0` (sincronización horizontal) + `Limites_Funcion_Coordinar` | Gobernador/a, SEREMI, DPR, directores regionales: uso de una "fuente única de verdad" para coordinar agendas. |
| Empoderamiento territorial de municipios | Cockpits territoriales + servicios de datos/IA | `gore_territorial`, `gore_indicadores`, `gore_eventos` (vistas por comuna) | `Funcion_Coordinar_4_0` (empoderamiento territorial) | Alcaldes, equipos municipales de SECPLAN: acceso a analítica territorial e instrumentos de planificación regional. |
| Articulación vía APIs y datos abiertos | Capa **Integraciones** + catálogo de datos | `gore_lenses` (mapeos), `gore_integracion`, dominios expuestos como datasets | `Funcion_Coordinar_4_0` (APIs y datos abiertos) | Academia, sector privado, sociedad civil: construcción de soluciones sobre datos regionales. |

### 4.3 Entidades y enums clave (Coordinar)

- `gore_gobernanza.sesion_core`, `gore_gobernanza.acuerdo_core`.  
- `gore_integracion.sistema_externo`, `gore_integracion.sincronizacion` (modelan vínculos con BIP, SIGFE, SISREC, etc.).  
- Entidades territoriales y de indicadores para vistas comunales y provinciales.

---

## 5. Normar → GORE OS

### 5.1 Resumen de la función en GORE Ideal / GORE 4.0

Referencia: `Motor_Cinco_Funciones → Normar`, `Funcion_Normar_4_0`, `Limites_Funcion_Normar`.

- **Misión:** usar la potestad reglamentaria como palanca **habilitante y basada en evidencia** para acelerar el desarrollo territorial.  
- **Capacidades clave:**
  - Regulación basada en misiones y estándares (calidad, sostenibilidad, interoperabilidad de datos).  
  - Proceso normativo dinámico y co-diseñado.  
  - Simplificación de procedimientos y sandboxes regulatorios.

### 5.2 Mapa de trazabilidad (Normar → GORE OS)

| Capacidad GORE 4.0 | Módulos / Capas GORE OS | Dominios / entidades IS-GORE v4.1 | Artefactos KODA | Usuarios / casos de uso |
|--------------------|-------------------------|-----------------------------------|------------------|-------------------------|
| Regulación basada en misiones y estándares | Capa **Normativa** de GORE OS + Módulo Presupuesto/IPR | `gore_normativo.norma`, `gore_normativo.glosa`, restricciones asociadas a fondos e instrumentos | `Funcion_Normar_4_0` (regulación basada en misiones) + `Limites_Funcion_Normar` + `kb_gn_018` (glosas y límites) | Gobernador/a, CORE, División Jurídica/Secretaría General, DAF, DIPIR: diseño de reglamentos que aterrizan la ERD en requisitos operativos. |
| Control de glosas y límites normativos en financiamiento | Motor de **Alertas de Glosas** | `gore_normativo.glosa`, dominios presupuestarios vinculados a cada glosa, enum `gore_presupuesto.tipo_movimiento_presupuestario` | `Limites_Funcion_Financiar` (topes, elegibilidad) + `kb_gn_018` | DAF, DIPIR: prevención de actos que vulneren glosas o topes legales en tiempo real. |
| Proceso normativo dinámico y co-diseñado | Gestión documental y de workflow | `gore_documental.documento` (borradores, versiones, firmas), `public.estado_documento`, `gore_workflow.tarea` | `Funcion_Normar_4_0` (proceso normativo dinámico) + `Limites_Funcion_Normar` | Gobernador/a, CORE, unidades técnicas, ciudadanía (consultas públicas): trazabilidad de reglamentos desde borrador a publicación. |
| Sandboxes regulatorios y experimentación | Capa Sensing/Reasoning + Normativa | Combinación de datos de ejecución (`gore_ejecucion`, `gore_indicadores`) con normas y pilotos etiquetados en `gore_normativo` | `Funcion_Normar_4_0` (sandboxes regulatorios) | GORE + servicios sectoriales + actores privados: diseño y seguimiento de pilotos regulados territorialmente. |

### 5.3 Entidades y enums clave (Normar)

- `gore_normativo.norma`, `gore_normativo.glosa`, `gore_normativo.restriccion`.  
- `gore_documental.documento`, enum `public.estado_documento`.  
- Enum `gore_presupuesto.tipo_movimiento_presupuestario` para expresar restricciones sobre movimientos.

---

## 6. Matriz resumen por función

### 6.1 Vista compacta

| Función GORE 4.0 | Módulos GORE OS principales | Dominios IS-GORE dominantes | Artefactos KODA clave | Prioridad MVP |
|------------------|----------------------------|-----------------------------|------------------------|---------------|
| **Planificar**   | Sensing (Gemelo Digital), IPR, CORE | `gore_planificacion`, `gore_territorial`, `gore_indicadores`, `gore_inversion` | `Funcion_Planificar_4_0`, `kb_gn_019` | Media |
| **Financiar**    | IPR, Presupuesto, Convenios/Transferencias | `gore_inversion`, `gore_presupuesto`, dominios que usan `estado_convenio`/`estado_cuota` | `Funcion_Financiar_4_0`, `kb_gn_018`, `kb_gn_011`, `Limites_Funcion_Financiar` | **Crítica** |
| **Ejecutar**     | Ejecución y Crisis, Rendiciones | `gore_ejecucion`, dominios financieros y de integración (SISREC) | `Funcion_Ejecutar_4_0`, `kb_gn_019`, `kb_gn_020`, `extension_crisis_v4_1` | **Crítica** |
| **Coordinar**    | CORE, Integraciones, Cockpits Territoriales | `gore_gobernanza`, `gore_integracion`, `gore_territorial` | `Funcion_Coordinar_4_0`, `Limites_Funcion_Coordinar` | Alta |
| **Normar**       | Capa Normativa, Alertas de Glosas, Documental/Workflow | `gore_normativo`, `gore_documental`, `gore_presupuesto` | `Funcion_Normar_4_0`, `Limites_Funcion_Normar`, `kb_gn_018` | Media |

### 6.2 Lectura rápida por rol

- **Gobernador/a Regional**  
  - Planificar: acceso a Gemelo Digital y tableros de inteligencia territorial.  
  - Financiar: priorización de cartera FNDR/FRPD/ISAR con soporte algorítmico.  
  - Ejecutar: vista tipo PMO regional de convenios e IPR críticos.  
  - Coordinar: panel de coordinación multi-actor (CORE, SEREMI, municipios).  
  - Normar: apoyo al diseño y seguimiento de reglamentos regionales.

- **CORE**  
  - Planificar: visualización de alineamiento de iniciativas con ERD/PROT.  
  - Financiar: trazabilidad entre acuerdos CORE y ejecución presupuestaria.  
  - Coordinar/Normar: seguimiento de acuerdos y normas aprobadas.

- **DIPIR / DIPLADE**  
  - Planificar: evaluación de pertinencia y priorización de cartera IPR.  
  - Financiar: interacción con presupuesto e instrumentos de financiamiento.  
  - Ejecutar: seguimiento operativo de ejecución de iniciativas.

- **DAF / Unidad de Presupuesto**  
  - Financiar: programación y control de ejecución presupuestaria.  
  - Ejecutar: gestión de devengos, pagos y su vínculo con rendiciones.  
  - Normar: cumplimiento de glosas y límites normativos.

- **RTF / U.C.R. / Ejecutores**  
- Ejecutar: soporte en convenios y control de ejecución.  
- Rendiciones: seguimiento del estado de expedientes SISREC y bloqueos asociados.  
- Coordinar: interacción estructurada con GORE OS vía cockpits y flujos.
 
---

## 7. Trazas finas: Vínculos específicos KODA → GORE OS

Esta sección detalla vínculos más finos entre artefactos KODA específicos y las capacidades de GORE OS, para que los equipos puedan ir directamente a la fuente normativa/procesal cuando diseñen reglas, pantallas o servicios.

### 7.1 Normar ↔ Glosas y límites presupuestarios

**Fuente KODA principal:** `kb_gn_018_gestion_prpto_koda.yml` → `GORE-FIN-MOD-LIMITES-GLOSAS-01`.

| Elemento KODA / Glosa | Restricción sustantiva | Capacidad GORE OS | Dominio / entidad IS-GORE |
|------------------------|------------------------|-------------------|----------------------------|
| Glosa 03 (uso de inversión en transferencias) | Prohíbe usar inversión para préstamos, gasto en personal o bienes/servicios de consumo de entidades receptoras. | Motor de **Alertas de Glosas** que bloquea o marca movimientos que intentan financiar Subt. 21 o 22 con recursos de inversión. | `gore_normativo.glosa` (Glosa 03), `gore_presupuesto.movimiento_presupuestario` (campo subtítulo/ítem), `gore_documental.documento` (acto asociado). |
| Glosa 04 (traspasos entre subtítulos) | Permite traspasos entre subtítulos de inversión, excluyendo explícitamente al Subt. 22 como receptor. | Regla de validación en interfaz de **modificaciones presupuestarias** que impide destino Subt. 22 cuando origen es inversión. | `gore_normativo.glosa`, `gore_presupuesto.movimiento_presupuestario` (origen/destino), reglas de negocio de módulo Presupuesto. |
| Glosa 01 Ley de Reajuste | Habilita excepcionalmente uso de inversión para gasto en personal cuando otra ley lo mandate. | Excepción parametrizable en el motor de reglas; permite determinados movimientos que normalmente serían bloqueados. | `gore_normativo.glosa`, `gore_presupuesto.movimiento_presupuestario`, `gore_documental.documento` (acto que invoca la glosa). |
| Glosa 06 (programas directos) | Permite hasta 5% para gastos de administración del GORE y hasta 5% para honorarios de la entidad receptora. | Cálculo automático del 5% permitido en cockpits de diseño de programas y alertas si se excede. | `gore_normativo.glosa`, `gore_presupuesto.asignacion` y movimientos vinculados a programas Glosa 06. |

**Implicación:** la capa Normativa de GORE OS no es abstracta; se parametriza directamente con glosas concretas y alimenta reglas en el módulo Presupuesto y en el motor de alertas.

### 7.2 Coordinar ↔ ARI, PROPIR y Convenios de Programación

**Fuente KODA principal:** `kb_gn_018_gestion_prpto_koda.yml` → `Coordinacion_ARI_PROPIR`, `GORE-FIN-FORM-ROL-DIPIR-01`, `GORE-FIN-FORM-COORDINACION-01`.

| Elemento KODA | Qué describe | Capacidad GORE OS | Dominios / entidades |
|---------------|-------------|-------------------|----------------------|
| `Coordinacion_ARI_PROPIR` (ARI/PROPIR) | Proceso de coordinación regional del gasto público (Chileindica, SEREMI, servicios, municipios). | Cockpit de **Coordinación de Gasto Público** que muestra ARI y PROPIR como capas en el Gemelo Digital y genera alertas por desalineamiento ERD/PROPIR. | `gore_planificacion.instrumento_planificacion` (ARI, PROPIR), `gore_territorial`, `gore_gobernanza.sesion_core` (instancias de validación). |
| Rol Gobernador/DIPLADE en ARI/PROPIR | Gobernador conduce el proceso; DIPLADE lidera Secretaría Ejecutiva. | Flujo de trabajo y permisos en el módulo CORE/Planificación: quién convoca, aprueba, registra acuerdos; actas trazables. | `gore_actores.persona` (roles), `gore_gobernanza.sesion_core`, `gore_workflow.tarea`. |
| Informe trimestral PROPIR al CORE, publicación Glosa 16 | Exigencia de reportar ejecución y cartera al CORE y ciudadanía. | Automatización de informes PROPIR y tablero público de transparencia (salida del módulo CORE + Sensing). | `gore_gobernanza.acuerdo_core`, `gore_indicadores`, `gore_expediente`, `gore_eventos` (publicación). |
| Convenios de Programación y transferencias consolidables | Co-diseño de inversiones con ministerios y servicios. | Integración con sistemas sectoriales vía capa de **Integraciones** y modelado explícito de convenios maestro entre GORE y otros organismos. | `gore_financiero.convenio` (tipo CONVENIO_PROGRAMACION), `gore_integracion.sistema_externo`, `gore_integracion.sincronizacion`. |

**Implicación:** la función Coordinar se materializa en GORE OS como flujos ARI/PROPIR/Convenios de Programación trazables y visualizables territorialmente, no solo como documentos aislados.

### 7.3 Financiar ↔ Tracks de evaluación y controles MDSF/DIPRES/CGR

**Fuentes KODA:**
- `kb_gn_019_gestion_ipr_koda.yml` → `GN-IPR-FASE1-INGRESO`, `GN-IPR-F1-PERTINENCIA-CDR`, `GN-IPR-F1-ADMISIBILIDAD-FORMAL`, estados de financiamiento.  
- `kb_gn_011_selector_ipr_koda.yml` (selector de vías de financiamiento).  
- `kb_gn_018_gestion_prpto_koda.yml` → secciones de control MDSF/DIPRES/CGR.

| Elemento KODA / Concepto | Qué fija | Capacidad GORE OS | Dominios / entidades |
|--------------------------|---------|-------------------|----------------------|
| `GN-IPR-FASE1-INGRESO` (Recepción, CDR, admisibilidad) | Secuencia de pasos desde postulación hasta estado "Lista para Fase 2". | Motor de estados IPR en módulo **IPR**, con UI que refleja exactamente estos pasos y estados. | `gore_inversion.iniciativa` + `gore_fsm` (máquina de estados), `public.codigo_track`. |
| `GN-IPR-F1-PERTINENCIA-CDR` | Uso del CDR como filtro estratégico inicial. | Vista de **Cartera CDR** en cockpit DIPLADE/DIPIR, con estados `PRE-ADMISIBLE CDR` y `NO PRE-ADMISIBLE CDR`. | `gore_inversion.iniciativa` (campo estado_estratégico), `gore_gobernanza.sesion_core` (cuando se eleva). |
| Estados de financiamiento IPR (GN-IPR-GLOS-ESTADOS-FINANCIAMIENTO) | Cadena: PARA REVISIÓN TÉCNICA → EN CARTERA PRE-ADMISIBLE → ... → CONVENIO FORMALIZADO. | Mapeo 1:1 a estados en módulo IPR/Presupuesto/Convenios, usados para filtros y alertas. | `gore_fsm.instancia_fsm` para ciclo de financiamiento; vínculos a `gore_financiero.convenio`. |
| Selector de tracks (kb_gn_011) | Reglas para elegir SNI_COMPLETO, FRIL, Glosa 06, FRPD, etc. | Clasificador de IPR (asistente de financiamiento) que consume atributos de la IPR y recomienda track. | Enum `public.codigo_track`, `gore_inversion.iniciativa` (campos de tipología), módulo IPR. |
| Controles MDSF/DIPRES/CGR (Limites_Funcion_Financiar, GORE-FIN-EJEC-DEVENGO-01, control legalidad) | Obligación de RS/RF/AD, visación DIPRES y Toma de Razón CGR. | Checklists automáticos en módulo Presupuesto/Convenios que impiden avanzar si falta RS/RF/AD o actos no han pasado por DIPRES/CGR. | `gore_evaluacion` (RS/RF/AD), `gore_financiero.convenio`, `gore_documental.documento` (estado_documento con hitos de Toma de Razón). |

**Implicación:** la función Financiar se operacionaliza como una cadena de estados y validaciones automáticas que reflejan exactamente lo descrito en los KODA, minimizando discrecionalidad ad-hoc en la UI.

### 7.4 Ejecutar ↔ Reglas de devengo y rendiciones

**Fuentes KODA:**
- `kb_gn_018_gestion_prpto_koda.yml` → `GORE-FIN-EJEC-DEVENGO-01` (Regla_Devengo_Por_Tipo_Transferencia).  
- `kb_gn_020_gestion_rendiciones_koda.yml` → procesos SISREC y modalidades de rendición.  
- `kb_gn_019_gestion_ipr_koda.yml` → fase de ejecución y seguimiento físico.

| Elemento KODA / Regla | Qué define | Capacidad GORE OS | Dominios / entidades |
|-----------------------|-----------|-------------------|----------------------|
| `GORE-FIN-EJEC-DEVENGO-01` (reglas de devengo) | Momento de devengo según tipo de transferencia (extrapresupuestaria, consolidable, privada). | Motor de **reglas de devengo** en módulo Presupuesto que calcula ejecución devengada en base a tipo de receptor y estado de rendición/convenio. | `gore_financiero.cuota_transferencia`, `gore_financiero.rendicion`, enums de tipo de transferencia y `public.estado_expediente_sisrec`. |
| Rendiciones en SISREC (kb_gn_020) | Flujo de envío, revisión, observaciones, cierre; estados SISREC. | Integración con SISREC en módulo Rendiciones y alertas: `Rendición vencida`, `Rendición observada prolongada`, bloqueo de nuevas transferencias. | `gore_integracion.sistema_externo` (SISREC), `gore_financiero.rendicion`, enum `public.estado_expediente_sisrec`, `gore_ejecucion.alerta_ipr` (tipo RENDICION_VENCIDA). |
| Vínculo ejecución física–financiera (kb_gn_019 + kb_gn_018) | DIPIR debe cruzar avance físico de obras con ejecución presupuestaria. | Tableros de **PMO Regional** que cruzan porcentaje de avance físico (obra) con porcentaje de devengo/pago y disparan alertas de desalineamiento. | `gore_ejecucion.avance_obra`, `gore_financiero.estado_pago`, `gore_inversion.iniciativa`. |
| Control interno y externo (Control_CGR, Seguimiento_DIPRES) | Roles de Unidad de Control, CGR, DIPRES en control previo/posterior. | Módulo de **auditoría y trazabilidad** que permite navegar desde una observación CGR/DIPRES al movimiento, convenio y IPR asociada. | `gore_seguridad.log_auditoria`, `gore_documental.documento`, `gore_presupuesto.movimiento_presupuestario`, `gore_financiero.convenio`. |

**Implicación:** la función Ejecutar en GORE OS no solo muestra "avance"; incorpora la lógica de devengo y de rendición para que la ejecución físico-financiera sea coherente con la normativa CGR/DIPRES.

> Este documento debe evolucionar junto con el modelo de datos y los artefactos KODA. Cada nuevo módulo o cambio de esquema en IS-GORE v4.1 (o v5.0, etc.) debe actualizar su traza hacia al menos una de las cinco funciones GORE 4.0.
