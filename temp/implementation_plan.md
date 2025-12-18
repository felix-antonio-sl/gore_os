# Plan de Alineación D-TDE y D-EVOL

## Objetivo
Establecer un acoplamiento orgánico entre **D-TDE (Piso Normativo)** y **D-EVOL (Techo Estratégico)** estandarizando terminología, explicitando el puente arquitectónico e integrando al agente `Digitrans`.

## Revisión de Usuario Requerida
> [!IMPORTANT]
> **Renombrado de Entidades en D-TDE**: Todas las entidades de datos en `domain_d-tde.md` serán renombradas de Español a Inglés (ej: `PoliticaDatos` → `DataPolicy`) para coincidir con el nuevo estándar GORE_OS establecido en D-EVOL.

## Cambios Propuestos

### D-TDE: Gobernanza Digital (`domain_d-tde.md`)

#### [MODIFICAR] Terminología y Entidades
- Traducir todas las Entidades de Datos al Inglés para asegurar coherencia semántica con D-EVOL.
    - `PoliticaDatos` → `DataPolicy`
    - `ActivoTI` → `ITAsset` (alineado con ISO 27001)
    - `ExpedienteElec` → `ElectronicFile`
    - `Incidente` → `Incident`
    - etc.

#### [MODIFICAR] Alineación Estratégica
- Actualizar **Propósito** y **Referencias Cruzadas** para definir explícitamente a D-TDE como el "Piso" fundacional para el "Techo" de D-EVOL.
- Vincular el Cumplimiento TDE (M1) a Primitivos ORKO (Capacidad P1, Límite P4).

#### [NUEVO] Integración Agente IA
- Agregar referencia a `Agente: Digitrans` (Asesor TDE) en la sección de Roles/Capacidades, vinculando a `agent_digitrans.yaml`.

### D-EVOL: Evolución e Inteligencia (`domain_d-evol.md`)

#### [MODIFICAR] Catálogo de Agentes
- Agregar `Digitrans` a la lista de agentes de ejemplo en Módulo 10 (Arquitectura Organizacional), categorizado explícitamente como **Asesor Experto TDE** (Modo M2/M3).

## Plan de Verificación

### Verificación Manual
- Verificar que las entidades D-TDE estén en inglés.
- Verificar que D-TDE referencia explícitamente a D-EVOL como su evolución estratégica.
- Verificar que D-EVOL reconoce a `Digitrans` como un recurso activo.
