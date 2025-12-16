# D-EVOL: Dominio de Evolución e Inteligencia

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Estratégica  
> **Función:** Evolución nativa del sistema operativo regional  

---

## Propósito

Gestionar la evolución nativa del sistema operativo regional hacia niveles superiores de madurez organizacional, basándose en un framework formal de transformación que va más allá del cumplimiento normativo.

> **Evolución Nativa vs. Cumplimiento:** Mientras D-TDE asegura el piso normativo (Ley 21.180), D-EVOL representa el **techo de capacidades**. La TDE es obligatoria; la evolución nativa es estratégica. GORE_OS no solo cumple, sino que **lidera** la transformación del aparato público regional.

---

## Framework de Evolución Organizacional

### Primitivos Fundamentales (P1-P5)

| Primitivo | Pregunta | Descripción |
|-----------|----------|-------------|
| **P1: CAPACIDAD** | ¿Quién ejecuta? | Humano/IA/Mixto |
| **P2: FLUJO** | ¿Cómo se transforma? | Procesos y pasos |
| **P3: INFORMACIÓN** | ¿Qué se transforma? | Entrada/salida |
| **P4: LÍMITE** | ¿Qué restringe? | Normas, recursos, plazos |
| **P5: PROPÓSITO** | ¿Para qué? | OKRs, outcomes |

### Ciclo Operacional: SDA

```
SENSE → DECIDE → ACT → (feedback loop)
Percibir   Analizar   Ejecutar
datos      priorizar  transformación
```

---

## Modelo HAIC: Colaboración Humano-IA

### Niveles de Delegación (M1-M6)

| Nivel | Nombre | Descripción |
|-------|--------|-------------|
| **M1** | MONITOREAR | Humano ejecuta, IA observa y aprende |
| **M2** | ASISTIR | Humano ejecuta, IA sugiere opciones |
| **M3** | HABILITAR | IA prepara, humano decide y ejecuta |
| **M4** | CONTROLAR | IA ejecuta, humano aprueba cada acción |
| **M5** | SUPERVISAR | IA ejecuta, humano audita por excepción |
| **M6** | EJECUTAR | IA autónoma, humano override disponible |

### Invariantes

- **∀ Capacidad IA (nivel ≥ M2): ∃ Humano accountable**
- Accountability humana obligatoria para decisiones algorítmicas
- Progresión M1→M6 solo con trajectory log y evidencia de desempeño
- Explainability requerida para niveles M3+

---

## Módulos

### 1. Niveles de Madurez

| Nivel | Nombre | Características |
|-------|--------|-----------------|
| **L0** | INICIAL | Procesos ad-hoc, sin estandarización |
| **L1** | DIGITALIZADO | Captura digital, repositorio único, trazabilidad |
| **L2** | INTEGRADO | Datos unificados, dashboards tiempo real |
| **L3** | AUTOMATIZADO | Alertas, validaciones, flujos automáticos |
| **L4** | INTELIGENTE | Decisiones asistidas por IA (M2-M4) |
| **L5** | AUTÓNOMO | Agentes IA operativos (M5-M6), optimización continua |

**GATE:** Transformación estructural requiere H_org ≥ 70

**Integración FÉNIX:** Anomalías detectadas por agentes IA o analytics pueden activar intervención (nivel variable según severidad)

### 2. Gobierno de Datos

**Pilares:** Calidad • Seguridad (Ley 21.719) • Disponibilidad • Linaje

- Catálogo de datasets con responsable (Data Steward)
- Diccionario de datos y trazabilidad de transformaciones
- Clasificación: Público / Interno / Confidencial / Sensible
- Calidad: Completitud, Exactitud, Actualidad, Consistencia

### 3. Automatizaciones

**Tipos:** Alertas • Validaciones • Cálculos • Notificaciones • Integraciones

- Nivel cognitivo: C0 (mecánico), C1 (decisional), C2 (razonamiento)
- Diseñador visual de flujos automatizados
- Métricas: tiempo ahorrado, errores evitados, throughput
- Trajectory log para progresión de autonomía

### 4. Agentes IA

> → Ver Parte IV del documento principal: Catálogo de Agentes Especializados

- Gobernanza: accountability humana, explainability, guardrails
- Ciclo de vida: Deploy → Monitor → Evaluate → Promote/Demote
- Drift detection: Alerta si rendimiento degrada

### 5. Analytics Avanzado

**Niveles:** Descriptivo → Diagnóstico → Predictivo → Prescriptivo

- Proyección ejecución presupuestaria
- Detección anomalías en rendiciones
- Predicción mora por ejecutor
- Simulación de escenarios y optimización

---

## Entidades de Datos

### Framework de Evolución

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Capacidad` | id, nombre, sustrato (humano/algorítmico/mixto), nivel_cognitivo, rol, accountable_id | → Flujo[], Delegacion[] |
| `Flujo` | id, nombre, tipo, pasos[], nivel_cognitivo, proposito_id | → Capacidad[], Informacion[] |
| `Proposito` | id, objetivo, key_results[], owner_id, padre_id | → Flujo[], KeyResult[] |
| `Limite` | id, tipo, expresion, enforcement | → Capacidad[], Flujo[] |
| `NivelMadurez` | id, proceso_id, nivel_actual (L0-L5), nivel_objetivo, fecha_evaluacion, gaps[] | → PlanEvolucion |

### Colaboración Humano-IA

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Delegacion` | id, capacidad_ia_id, humano_accountable_id, modo (M1-M6), fecha_inicio, evidencia | → Capacidad, Funcionario |
| `TrajectoryLog` | id, capacidad_id, timestamp, input, output, success, latency | → Capacidad |
| `DriftAlert` | id, capacidad_id, fecha, metrica_afectada, valor_esperado, valor_actual, severidad | → Capacidad |

### Gobierno de Datos

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Dataset` | id, nombre, descripcion, clasificacion, steward_id, frecuencia_actualizacion | → MetadatoDatos[], CertificacionCalidad[] |
| `MetadatoDatos` | id, dataset_id, campo, tipo, descripcion, sensibilidad, linaje | → Dataset |
| `Automatizacion` | id, nombre, tipo, nivel_cognitivo, trigger, estado, tiempo_ahorro | → LogEjecucion[], TrajectoryLog[] |

### Agentes IA

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Agente` | id, nombre, dominio, version, modo_delegacion, accountable_id, precision, estado | → InteraccionAgente[], TrajectoryLog[] |
| `InteraccionAgente` | id, agente_id, usuario_id, consulta, respuesta, rating, explicacion | → Agente, Funcionario |
| `ModeloML` | id, nombre, tipo, metricas, fecha_entrenamiento, drift_score | → Prediccion[], DriftAlert[] |

---

## Referencias Cruzadas

| Dominio | Relación |
|---------|----------|
| **D-PLAN** | Proyección de cumplimiento ERD |
| **D-FIN** | Analytics predictivo para IPR (ejecución, mora, riesgos) |
| **D-EJEC** | Automatización de alertas de convenios |
| **D-COORD** | Scoring predictivo de actores/ejecutores |
| **D-NORM** | Automatización de expedientes y alertas normativas |
| **D-BACK** | Predicción de necesidades de recursos |
| **D-TDE** | D-TDE es piso normativo, D-EVOL es techo estratégico |
| **D-TERR** | Analytics geoespacial avanzado |
| **D-GESTION** | H_gore integra métricas de madurez |
| **D-SEG** | Analytics predictivo de incidentes de seguridad |
| **D-GINT (FÉNIX)** | Detección automatizada de condiciones de activación |
| **Todos** | Agentes IA operan sobre todos los dominios |

---

*Documento parte de GORE_OS v4.1*
