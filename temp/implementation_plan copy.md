# Plan de Implementación: Acoplamiento Orgánico TDE ↔ D-EVOL

> **Objetivo:** Establecer un "acoplamiento fuerte" entre el piso normativo (D-TDE) y el techo estratégico (D-EVOL), asegurando que las actividades de cumplimiento alimenten automáticamente las métricas de evolución organizacional (`H_org`).

## Revisión de Usuario Requerida

> [!IMPORTANT]
> **Cambio Semántico:** D-TDE se enmarcará explícitamente como un **subconjunto** del Framework ORKO dentro del GORE. Los artefactos de cumplimiento (documentos, logs) serán tratados como Primitivos ORKO (Información/P3).

## Cambios Propuestos

### 1. D-EVOL: Profundizando el Puente (El Techo)
Mapear explícitamente los módulos D-TDE a Primitivos ORKO para calcular `H_org`.

#### [MODIFICAR] [domain_d-evol.md](file:///Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/domains/domain_d-evol.md)
- **Refinar Sección 11 (Puente TDE-ORKO):**
    - Mapear `D-TDE M2 (Servicios)` → `ORKO P1 (Capacidad)`.
    - Mapear `D-TDE M3 (Interoperabilidad)` → `ORKO P2 (Flujo)`.
    - Mapear `D-TDE M7 (Expediente)` → `ORKO P3 (Información)`.
    - Mapear `D-TDE M1/M4 (Cumplimiento/Seguridad)` → `ORKO P4 (Límite)`.
- **Actualizar Fórmula `H_org`:** Incluir explícitamente `TDEScore` como una variable en el componente de Gobernanza/Límite (P4).
- **Añadir User Story**: `US-EVOL-BRIDGE-001` para automatizar la ingesta de métricas TDE hacia D-EVOL.

### 2. D-TDE: Contextualizando el Cumplimiento (El Piso)
Añadir "Metadatos Evolutivos" para mostrar cómo el cumplimiento contribuye al sistema mayor.

#### [MODIFICAR] [domain_d-tde.md](file:///Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/domains/domain_d-tde.md)
- **Añadir Sección "Contribución a Evolución (ORKO)":**
    - Explicar que satisfacer los mandatos D-TDE "desbloquea" los niveles L2 (Integrado) y L3 (Automatizado) en la escala de madurez D-EVOL.
    - Etiquetar Módulos con su Primitivo ORKO correspondiente (ej: `M7 Expediente [Habilita P3: Información]`).

## Plan de Verificación

### Verificación Manual
- Verificar que cada User Story de Prioridad "Crítica" en D-TDE se mapee a un factor de riesgo en D-EVOL.
- Confirmar que la fórmula `H_org` pueda aceptar matemáticamente los inputs de TDE.
