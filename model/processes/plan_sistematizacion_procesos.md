# Plan de Sistematización de Procesos GORE_OS

Este plan detalla la estrategia para transformar los 289 procesos extraídos en un catálogo canónico y estructurado basado en el **Modelo Omega v2.6.0**.

## 1. Objetivos
*   **Limpiar y Depurar**: Eliminar duplicados, marcadores (P1, P2) y procesos fuera de alcance.
*   **Estructural (Categorización)**: Clasificar cada proceso en uno de los 12 dominios funcionales de GORE_OS.
*   **Alineación Semántica**: Mapear los procesos a las 5 funciones clave (Planificar, Financiar, Ejecutar, Coordinar, Normar).
*   **Normalización**: Establecer nombres canónicos (URNs) y descripciones breves.

## 2. Metodología

### Fase 1: Análisis y Limpieza
1. Leer `_procesos_extraidos_us.txt`.
2. Identificar y agrupar procesos por afinidad funcional.
3. Resolver sinonimias (ej: `GESTION-FLOTA` vs `GESTION-FLOTA-VEHICULAR`).
4. Descartar placeholders genéricos (`P1`, `P2`, etc.) a menos que tengan contexto específico en las US.

### Fase 2: Mapeo a Dominios GORE_OS
Utilizar los 12 dominios definidos en el perfil del agente:
*   **D-PLAN** (Planificación)
*   **D-FIN** (Finanzas)
*   **D-EJEC** (Ejecución)
*   **D-GOB** (Gobernanza)
*   **D-NORM** (Normativa/Legal)
*   **D-BACK** (Back-office/Admin)
*   **D-TDE** (Transformación Digital)
*   **D-TERR** (Territorio)
*   **D-SEG** (Seguridad/Emergencias)
*   **D-GESTION** (Gestión de Personas)
*   **D-EVOL** (Evolución/I+D)
*   **FÉNIX** (Casos críticos)

### Fase 3: Creación del Catálogo (`catalog_processes_goreos.yml`)
Crear un archivo YAML estructurado que contenga:
```yaml
processes:
  - id: PROCESO-CANONICO-ID
    name: "Nombre Amigable"
    domain: D-DOMAIN
    layer: Omega Layer (0-5)
    description: "Breve descripción funcional"
    source_us: [US-001, US-002] # Trazabilidad
```

## 3. Entregables
1.  **`catalog_processes_goreos.yml`**: El artefacto principal de conocimiento.
2.  **Reporte de Hallazgos**: Resumen de discrepancias o procesos que requieren mayor definición.

## 4. Próximos Pasos
1.  Escaneo profundo de `model/stories/` para validar contexto.
2.  Generación del borrador del catálogo.
3.  Revisión y validación final.
