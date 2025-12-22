# Arquitectura Categórica y Pipeline Functorial

## Visión General

GORE_OS no es solo un conjunto de servicios; es la materialización de una teoría matemática. La arquitectura implementa un **Pipeline Functorial** que transforma necesidades humanas en código ejecutable preservando la estructura y la intención original.

## El Pipeline Functorial

El proceso de construcción de software se modela como una composición de funtores entre categorías específicas.

$$ \mathcal{C}_{Req} \xrightarrow{\mathcal{F}_{Impl}} \mathcal{C}_{Arch} \xrightarrow{\mathcal{F}_{Code}} \mathcal{C}_{Runtime} $$

### 1. Categoría de Requisitos ($\mathcal{C}_{Req}$)
- **Objetos**: Roles, Stories, Capabilities.
- **Morfismos**: `contributes_to`, `actor_of`.
- **Artefactos**: Archivos en `model/atoms/stories`, `model/atoms/roles`.

### 2. Categoría de Arquitectura ($\mathcal{C}_{Arch}$)
- **Objetos**: Módulos, Contenedores, Componentes.
- **Morfismos**: `depends_on`, `composes`.
- **Artefactos**: Diagramas C4, Definiciones YAML de Módulos.
- **Funtor $\mathcal{F}_{Impl}$**: Transforma una Capacidad (conjunto de historias) en un Módulo Arquitectónico.

### 3. Categoría de Código ($\mathcal{C}_{Code}$)
- **Objetos**: Tipos (Types/Interfaces), Clases.
- **Morfismos**: Funciones puras, Métodos.
- **Artefactos**: Código fuente TypeScript (Zod schemas, tRPC routers).
- **Funtor $\mathcal{F}_{Code}$**: Transforma un Módulo en un Router tRPC y sus esquemas asociados.

## Mapeo de Conceptos

| Concepto Categórico          | Concepto Arquitectónico | Implementación Tecnológica |
| ---------------------------- | ----------------------- | -------------------------- |
| **Objeto**                   | Entidad / DTO           | Zod Schema / TS Type       |
| **Morfismo**                 | Función de Negocio      | Effect-TS Function         |
| **Funtor**                   | Transformación de Capa  | tRPC Procedure / Adapter   |
| **Producto** ($A \times B$)  | Agregación              | Objetos JS / Records       |
| **Coproducto** ($A + B$)     | Variación / Estado      | Discriminated Unions       |
| **Coálgebra** ($S \to F(S)$) | Máquina de Estados      | XState Machine             |

## Invariantes Estructurales

Para que el sistema sea correcto por construcción, mantenemos ciertos invariantes:

1.  **Preservación de Trazabilidad**: Todo componente de código debe ser rastreable hasta una User Story y un Rol.
    - *Implementación*: Decoradores o metadatos en los routers tRPC que referencian los IDs de las Stories.

2.  **Validación en Frontera (Adjunción)**: La validación de tipos no ocurre "dentro" de la lógica pura, sino en la frontera.
    - *Implementación*: Zod actúa como el *parser* que convierte datos no estructurados (`unknown`) en tipos del dominio (`DomainType`).

3.  **Manejo de Efectos (Mónadas)**: Los efectos secundarios (DB, API calls) están encapsulados.
    - *Implementación*: Uso de `Effect<Success, Error, Context>` para explicitar dependencias y fallos posibles.
