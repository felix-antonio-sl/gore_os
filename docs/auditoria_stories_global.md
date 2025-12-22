# Auditoría Categórica Exhaustiva: User Stories
> **Fecha:** 2025-12-22
> **Agente:** Ingeniero de Software Composicional
> **Scope:** `model/atoms/stories`

## 1. Resumen Ejecutivo (Estado del Morfismo)

Se ha realizado una auditoría exhaustiva de los **686 átomos** de tipo `Story` presentes en el repositorio, bajo la lente de la Teoría de Categorías aplicada a la Ingeniería de Software (Functorial Data Model).

El estado actual revela una **incompletitud crítica** en el morfismo de reificación (`R -> Code`), ya que si bien la intencionalidad (`i_want`, `so_that`) está presente, la condición de satisfacción verificable (`acceptance_criteria`) es inexistente en la totalidad del corpus.

### Métricas Clave

| Dimensión Categórica | Métrica   | Estado | Diagnóstico                                               |
| -------------------- | --------- | ------ | --------------------------------------------------------- |
| **Total Objetos R**  | **686**   | ✅      | Corpus robusto de intenciones.                            |
| **Dominio (D)**      | **100%**  | ✅      | Todos los objetos mapeados a un Dominio.                  |
| **Rol (U)**          | **100%**  | ✅      | Todos los objetos mapeados a un Rol (Morfismo `used_by`). |
| **Capacidad (C)**    | **85.6%** | ⚠️      | **99 historias huérfanas** (Morfismo `enabled_by` nulo).  |
| **Criterio (AC)**    | **0.0%**  | ❌      | **CRÍTICO: Ninguna historia es testable maquinalmente.**  |

## 2. Hallazgos Detallados

### 2.1. El Vacío del Criterio de Aceptación (Gap R->Code)
> **Severidad:** CRÍTICA (Bloqueante para Desarrollo)

Ninguna de las 686 historias posee la sección `acceptance_criteria`. En términos composicionales, esto significa que **no existe una función de verdad** para determinar si una implementación satisface la historia. El sistema es "especificable" pero no "verificable".

**Ejemplo de Patología:**
```yaml
id: US-ABAST-001-01
i_want: un módulo de gestión del Plan de Compras integrado con Mercado Público
so_that: pueda hacer seguimiento de las adquisiciones programadas
acceptance_criteria: [] # IMPLÍCITO/VACÍO
```
*Sin criterios explícitos (Given/When/Then verificables), el desarrollo depende de interpretación subjetiva, rompiendo la trazabilidad categórica.*

### 2.2. Orfandad Categórica (Gap R->C)
> **Severidad:** ALTA (Riesgo de Coherencia Arquitectónica)

99 historias de usuario no declaran `capability_id`. Esto implica que existen requerimientos (R) que no están sostenidos por ninguna capacidad del sistema (S), o bien, que la capacidad no ha sido explicita.

**Distribución de Orfandad (Top 5):**
1. **D-FIN:** Subdominios específicos (presupuesto, rendiciones).
2. **D-BACK:** Roles administrativos sin capacidad clara.
3. **D-EJEC:** Historias de terreno.

### 2.3. Distribución de Complejidad (Prioridad)
El backlog está fuertemente cargado hacia la alta prioridad:
- **P0 + P1:** ~89% del total.
- **P2:** ~10%
- **P3:** <1%

Esto sugiere una **tensión de priorización (Praxis B1)**: si "todo es urgente", nada lo es. Se recomienda aplicar un functor de re-priorización basado en dependencias estructurales.

## 3. Plan de Remediación Categórica

Para transicionar de un "Listado de Deseos" a una "Especificación Ejecutable", propongo el siguiente plan de acción:

### Fase 1: Inyección de Verificabilidad (R -> Code)
Generar, mediante inferencia lógica basada en `i_want` + `so_that`, una lista de **3 a 5 Criterios de Aceptación (Gherkin-style)** para cada historia.

**Transformación Propuesta:**
```yaml
acceptance_criteria:
  - "GIVEN un Plan de Compras creado"
  - "WHEN agrego un item desde Catálogo Mercado Público"
  - "THEN el item queda vinculado con su ID y precio referencial"
```

### Fase 2: Validación de la Satisfacción
Activar el agente `koda-tester` (Test Engineer) para validar que los criterios generados son:
1.  **Atómicos:** Testean una sola condición.
2.  **Deterministas:** No dependen de estado volátil no controlado.
3.  **Composicionales:** Reutilizan fixtures definidos en el dominio.

### Fase 3: Conexión de Capacidades (R -> C)
Ejecutar un proceso de "Healing" para las 99 historias huérfanas, asignándoles el `capability_id` más probable basado en su dominio y rol, o creando capacidades "Placeholder" si es necesario para mantener la integridad referencial.

---
**Recomendación Inmediata:** Autorizar la **Fase 1** (Inyección de ACs) para las historias de **D-FIN (Rendiciones)** como piloto, dada su criticidad financiera.
