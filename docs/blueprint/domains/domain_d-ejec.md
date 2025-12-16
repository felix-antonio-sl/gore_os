# D-EJEC: Dominio de Ejecución

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Núcleo (Dimensión Táctica)  
> **Función GORE:** EJECUTAR  

---

## Propósito

Gestionar la materialización de las iniciativas a través de convenios y seguimiento de obras.

---

## Módulos

### 1. Convenios

> **Nota de Diseño:** La entidad `Convenio` (SSOT) se define en **D-NORM** como acto administrativo formal. D-EJEC gestiona la *ejecución operativa* del convenio (hitos, pagos, riesgos). La tabla de tipos se replica aquí para referencia operativa.

**Tipos de Convenio:** (→ Ver D-NORM para definición formal)

| Tipo          | Descripción                                  | Ejemplo                             |
| ------------- | -------------------------------------------- | ----------------------------------- |
| MANDATO       | GORE encarga ejecución a otro órgano         | MOP ejecuta obra vial               |
| TRANSFERENCIA | GORE transfiere recursos a ejecutor          | Municipio ejecuta multicancha       |
| COLABORACIÓN  | Ejecución conjunta con aportes de ambos      | GORE+CORFO programa fomento         |
| MARCO         | Convenio paraguas para múltiples iniciativas | Marco con universidad para estudios |
| PROGRAMACIÓN  | Convenio plurianual con Ministerio           | CP de infraestructura con MOP       |

**Ciclo de Vida del Convenio:**

```
ELABORACIÓN → REVISIÓN JURÍDICA → FIRMA → EJECUCIÓN → LIQUIDACIÓN
     │              │              │          │            │
     ▼              ▼              ▼          ▼            ▼
  Borrador      V°B° UJ       Decreto    Transferenc.  Acta cierre
  técnico                     aprueba    + monitoreo
```

**Estados del Convenio:**

- BORRADOR → EN_REVISION_JURIDICA → PARA_FIRMA → VIGENTE
- PRORROGA_SOLICITADA, ADDENDUM_EN_PROCESO
- TERMINADO → LIQUIDADO
- CADUCADO

**Alertas con Escalamiento FÉNIX:**

| Condición                                     | Alerta      | Activación FÉNIX      |
| --------------------------------------------- | ----------- | --------------------- |
| Convenio a <30 días de vencimiento sin cierre | Prioritaria | Nivel I (automático)  |
| Convenio en riesgo de caducidad               | Crítica     | Nivel II (evaluación) |

**Funcionalidades:**

- Catálogo de convenios con filtros
- Alertas de vencimiento de plazo
- Gestión de addendum y prórrogas
- Hitos de ejecución y % avance
- Control de garantías (boletas)
- Generación automática de decretos

### 2. PMO Regional

**Torre de Control de Proyectos**

**Dimensiones de Monitoreo:**

| Tiempo           | Costo                    | Alcance                   | Riesgo                      |
| ---------------- | ------------------------ | ------------------------- | --------------------------- |
| % avance vs plan | Presupuesto vs ejecución | Cambios de especificación | Identificación y mitigación |
| Hitos cumplidos  | Desvío %                 | EP estados                | Matriz riesgos              |

**Semáforo de Proyecto:**

| Semáforo   | Condición                               | Acción                       |
| ---------- | --------------------------------------- | ---------------------------- |
| 🟢 VERDE    | Conforme a plan (±5%)                   | Monitoreo normal             |
| 🟡 AMARILLO | Desviación menor (5-15%)                | Seguimiento reforzado        |
| 🔴 ROJO     | Desviación crítica (>15%) o riesgo alto | Candidato FÉNIX Nivel II-III |
| ⚫ NEGRO    | Proyecto detenido/suspendido            | Activación FÉNIX Nivel I-II  |

**Funcionalidades:**

- Dashboard ejecutivo con semáforos
- Drill-down a detalle de proyecto
- Alertas proactivas de desvío
- Informes automáticos para Gabinete
- Gestión de riesgos y mitigaciones
- Estados de pago y avance físico

---

## Entidades de Datos

*Ejecución de Convenios (aspectos operativos):*

| Entidad                | Atributos Clave                                                                                          | Relaciones                                       |
| ---------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `HitoConvenio`         | id, convenio_id, descripcion, fecha_compromiso, fecha_real, estado                                       | → Convenio (D-NORM)                              |
| `EstadoPago`           | id, convenio_id, numero, monto, fecha_solicitud, fecha_aprobacion, estado                                | → Convenio (D-NORM)                              |
| `Riesgo`               | id, convenio_id, descripcion, probabilidad, impacto, mitigacion, estado                                  | → Convenio (D-NORM)                              |
| `VisitaTerreno`        | id, convenio_id, fecha, inspector, hallazgos, fotografias[], estado_verificado, firma_inspector          | → Convenio (D-NORM), → D-TERR                    |
| `ActaRecepcion`        | id, convenio_id, tipo (PARCIAL/DEFINITIVA), fecha, observaciones, conformidad, firmantes[], documentos[] | → Convenio (D-NORM), → D-NORM.ActoAdministrativo |
| `ModificacionConvenio` | id, convenio_id, tipo (ADDENDUM/PRORROGA/CAMBIO_MONTO), justificacion, acto_aprobatorio_id, fecha        | → Convenio (D-NORM)                              |
| `InformeAvance`        | id, convenio_id, periodo, avance_fisico_%, avance_financiero_%, observaciones, documentos_respaldo[]     | → Convenio (D-NORM)                              |
| `GarantiaConvenio`     | id, convenio_id, tipo (BOLETA/POLIZA), numero, entidad_emisora, monto, fecha_vencimiento, estado         | → Convenio (D-NORM)                              |

---

## Notas de Diseño

- La entidad `Convenio` (SSOT) se define en **D-NORM** como acto administrativo formal
- D-EJEC gestiona la *ejecución operativa* del convenio (hitos, pagos, riesgos)
- La entidad `Ejecutor` se unifica con `Actor` (D-COORD). El rol de ejecutor se representa mediante `actor_id`
- El rating y ficha 360° del ejecutor se gestionan en **D-FIN** (Módulo Gestión de Ejecutores)

---

## Referencias Cruzadas

| Dominio            | Relación                                            |
| ------------------ | --------------------------------------------------- |
| **D-PLAN**         | IPR priorizadas en ARI se ejecutan vía convenios    |
| **D-NORM**         | Convenio (SSOT del acto administrativo)             |
| **D-FIN**          | IPR, Transferencias, Rating Ejecutores              |
| **D-COORD**        | Actor (entidad base)                                |
| **D-TERR**         | Localización geoespacial de obras en ejecución      |
| **D-GESTION**      | Indicadores de ejecución de convenios para H_gore   |
| **D-SEG**          | PMO para proyectos de seguridad en ejecución        |
| **D-EVOL**         | Automatización de alertas de convenios              |
| **D-GINT (FÉNIX)** | Convenios en riesgo activan intervención Nivel I-II |

---

*Documento parte de GORE_OS v4.1*
