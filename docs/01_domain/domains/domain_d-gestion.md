# D-GESTION: Dominio de Gestión Institucional Transversal

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Transversal  
> **Función:** Gestión por resultados y mejora continua  

---

## Propósito

Gestionar el desempeño institucional, la mejora continua y la operación transversal del GORE mediante metodologías de gestión por resultados.

---

## Módulos

### 1. OKRs Institucionales

**Estructura OKR:**

```
OBJETIVO (O)
└── "Mejorar la eficiencia en ejecución presupuestaria"
    ├── KR1: Alcanzar 95% ejecución al 31/12
    ├── KR2: Reducir mora rendiciones a <5%
    └── KR3: Cerrar 100% convenios vencidos
```

**Ciclo OKR (Trimestral):**

```
DEFINIR OKRs → EJECUTAR → REVISAR (semanal) → CERRAR y AJUSTAR
```

**Funcionalidades:**

- Definición de OKRs por división/unidad
- Vinculación OKR ↔ ERD (alineamiento estratégico)
- Tracking semanal de Key Results
- Alertas de OKRs en riesgo
- Retrospectivas trimestrales

### 2. H_GORE (Índice de Salud Institucional)

**Dimensiones H_GORE:**

| Dimensión | Indicadores |
|-----------|-------------|
| Ejecución Presup. | % ejecución, desvío vs plan, días para cierre |
| Cartera IPR | % avance, proyectos en riesgo, estancados |
| Rendiciones | % mora, días promedio revisión, rechazos |
| Convenios | % vigentes OK, vencimientos próximos |
| Cumplimiento TDE | % normas cumplidas, brechas críticas |
| Satisfacción | NPS interno, tiempos respuesta |

**Cálculo:**

```
H_gore = Σ (peso_i × indicador_normalizado_i)
Escala: 0-100 | Meta: ≥80 (zona verde)
```

**Funcionalidades:**

- Dashboard H_gore en tiempo real
- Drill-down por dimensión
- Tendencia histórica
- Alertas de degradación
- Benchmark con otros GOREs

### 3. Playbooks Operativos

**Categorías:**

- **Operativos:** Cómo ejecutar procesos recurrentes
- **De Crisis:** Qué hacer ante situaciones de emergencia
- **De Onboarding:** Guías para nuevos funcionarios
- **De Cierre:** Procedimientos de fin de período/gestión

**Estructura Playbook:**

- Objetivo y alcance
- Roles responsables
- Pasos detallados (checklist)
- Decisiones y bifurcaciones
- Documentos/sistemas involucrados
- Criterios de éxito

**Funcionalidades:**

- Catálogo de playbooks por proceso
- Ejecución guiada paso a paso
- Versionamiento y mejora continua
- Métricas de uso y efectividad

### 4. Mejora Continua

**Ciclo PDCA Institucional:**

```
PLAN → DO → CHECK → ACT → (repetir)
```

**Funcionalidades:**

- Registro de oportunidades de mejora
- Priorización y asignación de iniciativas
- Seguimiento de implementación
- Medición de impacto
- Lecciones aprendidas

---

## Entidades de Datos

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `OKR` | id, periodo, tipo (institucional/division/unidad), objetivo, estado | → KeyResult[], Division |
| `KeyResult` | id, okr_id, descripcion, meta, valor_actual, confianza | → OKR, Medicion[] |
| `H_gore` | id, fecha, valor_compuesto, dimension_scores (JSON) | → HistoricoH_gore[] |
| `Playbook` | id, codigo, nombre, categoria, version, estado | → PasoPlaybook[], Ejecucion[] |
| `PasoPlaybook` | id, playbook_id, orden, descripcion, responsable_rol, checklist | → Playbook |
| `IniciativaMejora` | id, descripcion, origen, estado, responsable_id, impacto_esperado | → Funcionario |

---

## Referencias Cruzadas

| Dominio | Relación |
|---------|----------|
| **D-PLAN** | OKRs alineados con ERD |
| **D-FIN** | Indicadores de ejecución presupuestaria |
| **D-TDE** | Indicadores de cumplimiento TDE |
| **Todos** | H_gore integra métricas de todos los dominios |

---

*Documento parte de GORE_OS v3.1*
