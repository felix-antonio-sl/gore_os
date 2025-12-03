# GORE OS: Sistema Operativo Cognitivo Regional
 
**Versión:** 2.0.0  
**Fecha:** 2025-12-03  
**Basado en:**
- Modelo de datos IS-GORE v4.1 (21 dominios, 121 entidades)
- `kb_gn_018_gestion_prpto_koda.yml` (Ciclo presupuestario)
- `kb_gn_019_gestion_ipr_koda.yml` (Gestión IPR end-to-end)
- `kb_gn_020_gestion_rendiciones_koda.yml` (Gestión de rendiciones)
- `kb_gn_011_selector_ipr_koda.yml` (Selector de vías de financiamiento)
- `kb_gn_900_gore_ideal_koda.yml` (Visión GORE 4.0)

---

## 1. Propósito

GORE OS es la **capa cognitiva** sobre el modelo de datos IS-GORE v4.1. Su función es:

1. **Integrar** los 21 dominios del modelo en una vista unificada del territorio y la cartera de IPR.
2. **Automatizar** decisiones operativas repetitivas (clasificación, alertas, asignación).
3. **Predecir** riesgos de ejecución, rendición y presupuesto antes de que escalen.
4. **Asistir** a cada rol con información contextualizada y acciones sugeridas.

---

## 2. Anclaje en el Modelo de Datos

### 2.1 Dominios del Modelo IS-GORE v4.1

| Schema             | Propósito                         | Entidades Clave                                     |
|--------------------|-----------------------------------|-----------------------------------------------------|
| `gore_inversion`   | Cartera de IPR (IDI + PPR)        | `iniciativa`, `etapa_ipr`, `track_evaluacion`      |
| `gore_presupuesto` | Ciclo presupuestario              | `asignacion`, `movimiento_presupuestario`, `cdp`   |
| `gore_financiero`  | Convenios y cuotas                | `convenio`, `cuota_transferencia`, `garantia`      |
| `gore_ejecucion`   | Seguimiento físico y crisis       | `avance_obra`, `estado_pago`, `problema_ipr`, `compromiso_operativo`, `alerta_ipr` |
| `gore_evaluacion`  | Análisis técnico-económico        | `evaluacion_mdsf`, `evaluacion_gore`, `resultado_rate` |
| `gore_documental`  | Expedientes y documentos          | `documento`, `version_documento`, `firma`          |
| `gore_actores`     | Actores del ecosistema            | `entidad`, `persona`, `rol`, `division`            |
| `gore_territorial` | Geografía y brechas territoriales | `comuna`, `provincia`, `brecha_territorial`        |
| `gore_gobernanza`  | CORE y sesiones                   | `sesion_core`, `acuerdo_core`, `votacion`          |
| `gore_fsm`         | Máquinas de estado                | `estado`, `transicion`, `instancia_fsm`            |
| `gore_workflow`    | Flujos de trabajo                 | `tarea`, `asignacion_tarea`, `deadline`            |
| `gore_indicadores` | Indicadores y metas               | `indicador`, `meta`, `medicion`                    |
| `gore_riesgos`     | Gestión de riesgos                | `riesgo`, `mitigacion`, `evento_riesgo`            |
| `gore_eventos`     | Bitácora de eventos               | `evento`, `correlacion_evento`                     |
| `gore_expediente`  | Trazabilidad documental           | `expediente`, `hito_expediente`                    |
| `gore_normativo`   | Marco legal y glosas              | `norma`, `glosa`, `restriccion`                    |
| `gore_integracion` | Integraciones externas            | `sistema_externo`, `sincronizacion`                |
| `gore_lenses`      | Mapeos y transformaciones         | `lens`, `campo_mapeo`                              |
| `gore_seguridad`   | Permisos y auditoría              | `permiso`, `log_auditoria`                         |
| `gore_privacidad`  | Protección de datos               | `consentimiento`, `anonimizacion`                  |
| `gore_planificacion` | ERD/PROT/ARI y planificación    | `instrumento_planificacion`, `objetivo_estrategico`|

### 2.2 Tipos de Dominio (ENUMs Clave)

```sql
-- Ciclo de vida de problemas
gore_ejecucion.estado_problema_ipr: ABIERTO | EN_GESTION | RESUELTO | CERRADO_SIN_RESOLVER
gore_ejecucion.impacto_problema_ipr: BLOQUEA_PAGO | RETRASA_OBRA | RETRASA_CONVENIO | RIESGO_RENDICION | AFECTA_IMAGEN | OTRO

-- Alertas automáticas
gore_ejecucion.tipo_alerta_ipr: OBRA_TERMINADA_SIN_PAGO | CUOTA_VENCIDA | CONVENIO_POR_VENCER | RENDICION_VENCIDA | COMPROMISO_VENCIDO | PROBLEMA_PROLONGADO | AVANCE_DETENIDO | INCONSISTENCIA_DETECTADA
gore_ejecucion.nivel_alerta_ipr: NORMAL | INFO | ATENCION | ALTO | CRITICO

-- Tracks de evaluación
public.codigo_track: SNI_COMPLETO | SNI_SIMPLIFICADO | GLOSA06_BIFASICO | CONCURSO_FRPD | CONCURSO_8 | EXENTO_FRIL | CIRCULAR_33 | OTRO

-- Estados de convenio
public.estado_convenio: ELABORACION | EN_VISACION | EN_TDR | VIGENTE | EN_PRORROGA | TERMINADO | LIQUIDADO | RESCILIADO
```

---

## 3. Módulos Funcionales por Dominio Operativo

### 3.1 Módulo IPR (Intervenciones Públicas Regionales)

**Base de datos:** `gore_inversion`, `gore_evaluacion`

| Funcionalidad                        | Proceso KODA                    | Capacidad GORE OS                                                 |
|--------------------------------------|----------------------------------|-------------------------------------------------------------------|
| Clasificación automática de IPR      | `GN-IPR-FASE1-INGRESO`          | Detectar si es IDI o PPR y track probable (SNI, FRIL, Glosa06, etc.) |
| Admisibilidad documental             | `GN-IPR-F1-ADMISIBILIDAD-FORMAL`| Checklist automático de requisitos por mecanismo                  |
| Pertinencia estratégica              | `GN-IPR-F1-PERTINENCIA-CDR`     | Score de alineación con ERD y prioridades regionales              |
| Seguimiento de evaluación            | `GN-IPR-FASE2-EVAL`             | Alertas de plazos MDSF y tracking de RATE (RS/FI/OT/AD)           |

**Usuarios:**
- Formulador externo: asistente para selección de vía y checklist de antecedentes.
- Analista DIPIR: cartera en evaluación, alertas de FI/OT, seguimiento BIP.
- Jefatura DIPIR: vista agregada de cartera con RS disponible para CORE.

### 3.2 Módulo Presupuesto

**Base de datos:** `gore_presupuesto`, `gore_financiero`

| Funcionalidad                  | Proceso KODA                           | Capacidad GORE OS                                                   |
|--------------------------------|-----------------------------------------|---------------------------------------------------------------------|
| Programación de ejecución      | `GORE-FIN-EJEC-PROGRAMACION-01`        | Proyección de flujo de caja mensual, alertas de desfase vs. programa DIPRES |
| Control de afectación          | `GORE-FIN-CONCEPTOS-CLAS-AFECT-01`     | Visibilidad de preafectación → afectación → compromiso → devengo → pago |
| Modificaciones presupuestarias | `GORE-FIN-MOD-TIPOS-ACTOS-01`          | Asistente para determinar tipo de acto requerido                     |
| Alertas de glosas              | `GORE-FIN-MOD-LIMITES-GLOSAS-01`       | Detección automática de violaciones a Glosa 03, 04, 06               |

**Usuarios:**
- Profesional DAF: control de disponibilidad, emisión de CDP, programación de pagos.
- Jefatura DAF: dashboard de ejecución mensual y proyección de deuda flotante.
- Profesional DIPIR: coordinación para modificaciones de inversión.

### 3.3 Módulo Convenios y Transferencias

**Base de datos:** `gore_financiero`, `gore_documental`

| Funcionalidad            | Proceso KODA                    | Capacidad GORE OS                                              |
|--------------------------|----------------------------------|----------------------------------------------------------------|
| Seguimiento de convenios | `GN-IPR-FASE4-GESTION-PPT`      | Estados de convenio y alertas de vencimiento                   |
| Control de cuotas        | `GN-IPR-F4-FORMALIZACION-DEVENGO` | Programación de transferencias y reglas de devengo por receptor |
| Gestión de garantías     | —                                | Alertas de vencimiento y renovaciones de garantías             |

**Usuarios:**
- Profesional de convenios (DAF): lista de convenios por estado, TDR pendientes.
- RTF: seguimiento de convenios y hitos asociados.

### 3.4 Módulo Ejecución y Crisis

**Base de datos:** `gore_ejecucion`

| Funcionalidad              | Proceso / Entidad      | Capacidad GORE OS                                                |
|----------------------------|------------------------|------------------------------------------------------------------|
| Registro de problemas IPR  | `problema_ipr`         | Modelo estructurado de nudos (TECNICO, FINANCIERO, LEGAL, etc.)  |
| Gestión de compromisos     | `compromiso_operativo` | Asignación, seguimiento y verificación de compromisos operativos |
| Sistema de alertas         | `alerta_ipr`           | Generación automática de alertas según reglas de negocio         |
| Escalamiento de criticidad | `nivel_alerta_ipr`     | Escalamiento INFO → ATENCION → ALTO → CRITICO                    |

**Usuarios:**
- Analista DIPIR: registro de problemas y creación de compromisos.
- Jefatura divisional: dashboard de problemas abiertos y compromisos vencidos.
- Gobernador/a: War Room con IPR críticas y escalamientos.

### 3.5 Módulo Rendiciones

**Base de datos:** `gore_financiero`, `gore_integracion` (SISREC)

| Funcionalidad                | Proceso KODA                               | Capacidad GORE OS                                              |
|------------------------------|---------------------------------------------|-----------------------------------------------------------------|
| Seguimiento de rendiciones   | `STS-KB-GN-RENDICION-PROCESO-CON-SISREC-01` | Sincronización con SISREC y alertas de rendiciones pendientes  |
| Control de plazos y vetos    | Res. 30/2015 CGR Art. 18                    | Bloqueo de nuevas transferencias si hay rendiciones vencidas   |
| Revisión técnica y financiera| `STS-KB-GN-RENDICION-ACTOR-RTF-01`          | Checklist estructurado por RTF y estados de aprobación         |

**Usuarios:**
- RTF: lista de rendiciones por revisar, observaciones pendientes.
- U.C.R. (DAF): contabilización SIGFE y archivo de expedientes.
- Jefatura DAF: dashboard de rendiciones vencidas por ejecutor.

### 3.6 Módulo CORE

**Base de datos:** `gore_gobernanza`

| Funcionalidad              | Capacidad GORE OS                                             |
|----------------------------|----------------------------------------------------------------|
| Preparación de carteras    | Generación automática de carpetas CORE con fichas IDI/PPR     |
| Seguimiento de acuerdos    | Trazabilidad de IPR aprobadas → financiamiento → ejecución    |
| Transparencia y reporte    | Publicación automática de acuerdos y cartera financiada       |

**Usuarios:**
- Secretario/a Ejecutivo CORE: preparación de sesiones y certificados.
- Consejero/a Regional: acceso a información de cartera con trazabilidad.

---

## 4. Arquitectura de Capas

```text
┌─────────────────────────────────────────────────────────────────┐
│                    COCKPITS (Por Rol)                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │Formulador│ │ Analista │ │ Jefatura │ │Gobernador│           │
│  │  Externo │ │  DIPIR   │ │ DAF/DIPIR│ │ /CORE    │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA COGNITIVA (GORE OS)                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌─────────────┐  │
│  │Clasificador│ │ Detector   │ │ Alertas    │ │ Predictor   │  │
│  │  de IPR    │ │ Anomalías  │ │ Automáticas│ │ de Riesgo   │  │
│  └────────────┘ └────────────┘ └────────────┘ └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    MODELO DE DATOS IS-GORE v4.1                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │inversion│ │presupsto│ │financiro│ │ejecucion│ │ ...x21  │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRACIONES EXTERNAS                       │
│  ┌─────┐ ┌─────┐ ┌──────┐ ┌───────┐ ┌────────┐                 │
│  │ BIP │ │SIGFE│ │SISREC│ │ChileIn│ │MercadoP│                 │
│  └─────┘ └─────┘ └──────┘ └───────┘ └────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Usuarios y Necesidades Prioritarias

### 5.1 Matriz de Usuarios vs. Necesidades

| Usuario               | Necesidad Principal                                                | Módulo GORE OS              | Prioridad |
|-----------------------|--------------------------------------------------------------------|-----------------------------|-----------|
| Formulador Externo    | Saber qué vía usar y qué documentos presentar                     | IPR / Selector              | Alta      |
| Analista DIPIR        | Ver estado de cartera, detectar FI/OT, registrar problemas        | IPR / Ejecución             | Crítica   |
| Jefatura DIPIR        | Priorizar cartera para CORE, ver riesgos de ejecución             | IPR / CORE                  | Crítica   |
| Profesional DAF       | Controlar disponibilidad, programar pagos, emitir CDP             | Presupuesto                 | Crítica   |
| Jefatura DAF          | Ver ejecución mensual, proyectar deuda flotante                   | Presupuesto                 | Alta      |
| Referente Téc.-Fin.   | Seguir convenios y rendiciones asignadas                          | Convenios / Rendiciones     | Alta      |
| Unidad Control Rend.  | Controlar rendiciones pendientes y contabilización                | Rendiciones                 | Alta      |
| Consejero Regional    | Acceder a información de cartera antes de sesiones                | CORE                        | Media     |
| Gobernador/a Regional | Ver IPR críticas, escalamientos y KPIs de ejecución territorial   | Ejecución / War Room        | Alta      |

### 5.2 Instancias de Uso Prioritarias (MVP)

1. **Alerta de Convenio por Vencer** → notificación automática a RTF y Jefatura DIPIR.
2. **Alerta de Rendición Vencida** → bloqueo de nuevas transferencias al ejecutor hasta regularización.
3. **Dashboard de Cartera RS** → vista de IPR listas para presentar a CORE.
4. **Clasificador de IPR** → sugerencia automática de track (SNI, FRIL, Glosa 06, FRPD, etc.).
5. **Registro estructurado de Problema IPR** → formulario que enlaza impacto, actor responsable y compromiso asociado.

---

## 6. Próximos Artefactos

1. **Especificación de reglas de alerta** para cada `tipo_alerta_ipr` y `nivel_alerta_ipr`.
2. **Diseño de cockpits** por rol, con wireframes ligados a entidades del modelo de datos.
3. **Mapeo de integraciones** BIP ↔ `gore_inversion`, SISREC ↔ `gore_financiero`, SIGFE ↔ `gore_presupuesto`.
4. **FSM detallada para IPR** en `gore_fsm` (estados y transiciones principales del ciclo).
5. **Matriz de trazabilidad GORE 4.0 ↔ módulos GORE OS**, apoyada por el modelo de datos y procesos KODA.

> **GORE OS no inventa datos: orquesta, alerta y predice sobre los 21 dominios del modelo IS-GORE v4.1, usando la semántica operativa de los artefactos KODA.**
