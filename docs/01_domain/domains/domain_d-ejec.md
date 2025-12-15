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

**Tipos de Convenio:**

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| MANDATO | GORE encarga ejecución a otro órgano | MOP ejecuta obra vial |
| TRANSFERENCIA | GORE transfiere recursos a ejecutor | Municipio ejecuta multicancha |
| COLABORACIÓN | Ejecución conjunta con aportes de ambos | GORE+CORFO programa fomento |
| MARCO | Convenio paraguas para múltiples iniciativas | Marco con universidad para estudios |
| PROGRAMACIÓN | Convenio plurianual con Ministerio | CP de infraestructura con MOP |

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

| Tiempo | Costo | Alcance | Riesgo |
|--------|-------|---------|--------|
| % avance vs plan | Presupuesto vs ejecución | Cambios de especificación | Identificación y mitigación |
| Hitos cumplidos | Desvío % | EP estados | Matriz riesgos |

**Semáforo de Proyecto:**

- 🟢 VERDE: Conforme a plan (±5%)
- 🟡 AMARILLO: Desviación menor (5-15%)
- 🔴 ROJO: Desviación crítica (>15%) o riesgo alto
- ⚫ NEGRO: Proyecto detenido/suspendido

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

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `HitoConvenio` | id, convenio_id, descripcion, fecha_compromiso, fecha_real, estado | → Convenio (D-NORM) |
| `EstadoPago` | id, convenio_id, numero, monto, fecha_solicitud, fecha_aprobacion, estado | → Convenio (D-NORM) |
| `Riesgo` | id, convenio_id, descripcion, probabilidad, impacto, mitigacion, estado | → Convenio (D-NORM) |

---

## Notas de Diseño

- La entidad `Convenio` (SSOT) se define en **D-NORM** como acto administrativo formal
- D-EJEC gestiona la *ejecución operativa* del convenio (hitos, pagos, riesgos)
- La entidad `Ejecutor` se unifica con `Actor` (D-COORD). El rol de ejecutor se representa mediante `actor_id`
- El rating y ficha 360° del ejecutor se gestionan en **D-FIN** (Módulo Gestión de Ejecutores)

---

## Referencias Cruzadas

| Dominio | Relación |
|---------|----------|
| **D-NORM** | Convenio (SSOT del acto administrativo) |
| **D-FIN** | IPR, Transferencias, Rating Ejecutores |
| **D-COORD** | Actor (entidad base) |

---

*Documento parte de GORE_OS v3.1*
