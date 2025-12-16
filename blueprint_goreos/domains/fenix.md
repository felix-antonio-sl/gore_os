# Departamento de Gestión Institucional (FÉNIX)

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Transversal  
> **Función GORE:** Gestión de Contingencias e Intervención Institucional  

---

## 1. Propósito

Unidad especializada del GORE de Ñuble responsable de diagnosticar, intervenir y resolver situaciones críticas institucionales, gestionar procesos estancados y acelerar iniciativas estratégicas cuando las circunstancias lo requieren.

El Departamento opera como capacidad transversal, activándose ante contingencias que exceden la capacidad de respuesta de los flujos operativos normales.

---

## 2. Principios Rectores

| Principio | Descripción |
|-----------|-------------|
| **Orientación a Resultados** | Objetivos específicos, medibles y con plazos definidos |
| **Multidisciplinariedad** | Integración de especialistas de múltiples áreas según requerimiento |
| **Facultades Delegadas** | Autoridad para tomar decisiones operativas sin escalamiento innecesario |
| **Agilidad Operativa** | Ciclos de gestión abreviados respecto a procesos regulares |
| **Responsabilidad Directa** | Rendición de cuentas sobre los resultados de cada intervención |
| **Transferencia Ordenada** | Traspaso documentado a operación regular post-intervención |

---

## 3. Estructura del Equipo

### 3.1 Equipo Base (3-4 funcionarios)

| Rol | Responsabilidades |
|-----|-------------------|
| **Jefe de Intervención** | Coordinación general y toma de decisiones operativas |
| **Analista de Gestión** | Diagnóstico situacional, análisis de datos e identificación de causas |
| **Asesor Jurídico** | Evaluación de viabilidad legal y alternativas normativas |
| **Especialista en Procesos** | Diseño e implementación de soluciones operativas |

### 3.2 Especialistas de Apoyo (según intervención)

| Área | Criterio de Incorporación |
|------|---------------------------|
| D-FIN | Materias presupuestarias, rendiciones, inversión pública |
| D-EJEC | Convenios, seguimiento de obras |
| D-COORD | Gestión de actores externos |
| D-NORM | Materias jurídico-administrativas |
| D-TDE | Soluciones tecnológicas |
| D-EVOL | Automatización y analítica |

---

## 4. Categorías de Intervención

### 4.1 Nivel I: Contingencia Crítica

- Emergencias o catástrofes regionales
- Riesgo de pérdida de recursos por incumplimiento de plazos
- Conflictos críticos con ejecutores o contratistas
- Observaciones de CGR con plazo inminente

**Activación:** Inmediata | **Duración estimada:** 1-4 semanas

### 4.2 Nivel II: Gestión de Procesos Estancados

- IPR sin avance por más de 90 días
- Rendiciones en mora superior a 180 días
- Procesos administrativos detenidos
- Convenios en riesgo de caducidad

**Activación:** Programada | **Duración estimada:** 2-6 semanas

### 4.3 Nivel III: Aceleración de Iniciativas

- Proyectos prioritarios con plazos comprometidos
- Oportunidades de financiamiento con ventana limitada
- Implementación de nueva normativa
- Gestión de cierre de año presupuestario

**Activación:** Por requerimiento | **Duración estimada:** 2-8 semanas

### 4.4 Nivel IV: Mejora Institucional

- Rediseño de procesos críticos
- Implementación de nuevos módulos de gestión
- Mejoramiento de áreas con bajo desempeño
- Preparación para auditorías externas

**Activación:** Por diagnóstico | **Duración estimada:** 4-12 semanas

---

## 5. Ciclo de Intervención

```
DETECCIÓN → DIAGNÓSTICO → PLANIFICACIÓN → EJECUCIÓN → CIERRE
```

### Fases

| Fase | Duración | Actividades Principales |
|------|----------|-------------------------|
| **1. Detección** | Horas | Identificación del problema, evaluación de criticidad, decisión de activación |
| **2. Diagnóstico** | 1-3 días | Análisis de causa raíz, levantamiento de actores involucrados, evaluación de recursos |
| **3. Planificación** | 1 día | Definición de objetivo, conformación de equipo, elaboración de plan de acción |
| **4. Ejecución** | Variable | Implementación de acciones, seguimiento periódico, gestión de contingencias |
| **5. Cierre** | 1 semana | Transferencia a operación regular, documentación de aprendizajes, actualización de procedimientos |

---

## 6. Condiciones de Activación Automática

| Condición | Nivel | Acción |
|-----------|-------|--------|
| Índice H_gore < 60 sostenido por 2 semanas | IV | Notificación automática a Jefatura |
| IPR en estado ESTANCADA >90 días | II | Candidata a intervención |
| Rendición en mora >180 días | II | Escalamiento para evaluación |
| Convenio a <30 días de vencimiento sin cierre | I | Alerta prioritaria |
| Anomalía detectada por sistema | Variable | Recomendación de evaluación |

---

## 7. Entidades de Datos

### 7.1 Intervención

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| id | uuid | Identificador único |
| codigo | string | Código de intervención (ej: "INT-2024-001") |
| nivel | enum | I, II, III, IV |
| estado | enum | DETECTADA, EN_DIAGNOSTICO, PLANIFICADA, EN_EJECUCION, EN_CIERRE, CERRADA |
| criticidad | int | Escala 1-5 |
| objetivo | text | Objetivo específico y medible |
| fecha_inicio | date | Fecha de activación |
| autoriza_id | FK | Directivo que autoriza la intervención |
| responsable_id | FK | Jefe de intervención asignado |
| dominios_involucrados | array | Dominios afectados |
| indicadores_exito | json | Métricas de éxito definidas |

### 7.2 Equipo de Intervención

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| intervencion_id | FK | Referencia a Intervención |
| funcionario_id | FK | Funcionario asignado |
| rol | enum | JEFE, ANALISTA, JURIDICO, PROCESOS, APOYO |
| area_especialidad | enum | D-FIN, D-EJEC, D-NORM, etc. |
| horas_asignadas | int | Horas dedicadas a la intervención |

### 7.3 Bitácora de Intervención

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| intervencion_id | FK | Referencia a Intervención |
| fecha | datetime | Fecha y hora del registro |
| tipo | enum | DIAGNOSTICO, DECISION, ACCION, HITO, IMPEDIMENTO |
| descripcion | text | Detalle de la actividad o evento |
| responsable_id | FK | Funcionario que registra |

### 7.4 Aprendizaje Institucional

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| intervencion_id | FK | Referencia a Intervención |
| categoria | enum | PROCESO, PERSONAS, TECNOLOGIA, NORMATIVA |
| hallazgo | text | Situación identificada |
| recomendacion | text | Acción correctiva o preventiva sugerida |
| procedimiento_actualizado_id | FK | Referencia a procedimiento modificado (si aplica) |

---

## 8. Diagrama de Integración

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    DEPARTAMENTO DE GESTIÓN INSTITUCIONAL EN GORE_OS                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   OPERACIÓN REGULAR                                                                  │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│   D-PLAN → D-FIN → D-EJEC → D-COORD (flujo continuo)                                │
│                                                                                      │
│   ANTE CONTINGENCIA / PROCESO ESTANCADO / PRIORIDAD ESTRATÉGICA                     │
│   ━━━━━━━━━━━━━━━━━━━▓▓▓▓▓▓▓▓▓━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                          │                                                          │
│                          ▼                                                          │
│                   ┌──────────────┐                                                  │
│                   │   GESTIÓN    │  ◄── Activación, diagnóstico, intervención       │
│                   │INSTITUCIONAL │      y normalización de flujos                   │
│                   └──────────────┘                                                  │
│                          │                                                          │
│                          ▼                                                          │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│   Flujo normalizado / iniciativa acelerada                                          │
│                                                                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   INTEGRACIÓN CON DOMINIOS                                                           │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                              CAPA DE EVOLUCIÓN                              │   │
│   │  ┌─────────────────────────────────────────────────────────────────────┐   │   │
│   │  │  D-EVOL  │  D-GESTION  │  GESTIÓN   │  Agentes IA                   │   │   │
│   │  │          │             │  INSTIT.   │                               │   │   │
│   │  │          │   OKRs      │ (capacidad │  Automatizaciones             │   │   │
│   │  │  Madurez │   H_gore ───┼──especial) │                               │   │   │
│   │  └──────────────────────────────┼──────────────────────────────────────┘   │   │
│   └─────────────────────────────────┼───────────────────────────────────────────┘   │
│                                     │ Interviene en                                  │
│                                     ▼                                                │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │  D-FIN       │  D-EJEC        │  D-COORD       │  D-NORM       │  D-BACK    │   │
│   │  (IPR)       │  (Convenios)   │  (Actores)     │  (Normativa)  │  (Recursos)│   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Referencias Cruzadas

| Dominio | Tipo de Integración |
|---------|---------------------|
| **D-GESTION** | Procedimientos actualizados con aprendizajes institucionales |
| **D-GESTION** | Índice H_gore como indicador de activación |
| **D-FIN** | Intervención en IPR con estado problemático |
| **D-EJEC** | Gestión de convenios con riesgo de incumplimiento |
| **D-EVOL** | Detección automatizada de condiciones de activación |
| **Todos** | Capacidad de intervención transversal según requerimiento |

---

*Documento parte de GORE_OS v4.0*  
*Departamento de Gestión Institucional - GORE Ñuble*
