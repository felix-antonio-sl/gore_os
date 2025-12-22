# GORE_OS

Sistema de Gestión Integral para Gobiernos Regionales - Ontología Categórica v3.0

## Estructura del Repositorio

```
gore_os/
├── ontology/             # Especificación formal (Norma Superior)
├── model/                # Modelo categórico
│   ├── atoms/            # Roles, Stories, Capabilities, Modules, Processes, Entities
│   ├── profunctors/      # Relaciones N:M centralizadas
│   ├── compositions/     # Dominios (Σ-Lifts)
│   └── catalog/          # Catálogo maestro
├── architecture/         # Arquitectura C4 + ADRs
├── etl/                  # Pipelines de migración (sources, sinks, transforms)
├── tools/                # Scripts de validación y composición
├── schemas/              # JSON Schemas
├── docs/                 # Guías, procesos BPMN, diseño
└── archive/              # Artefactos históricos
```

## Ontología

La ontología v3.0 define el sistema como una **Categoría de Grothendieck** con tres subcategorías:
- **$\mathcal{G}_{Req}$**: Requisitos (Roles, Stories, Capabilities)
- **$\mathcal{G}_{Impl}$**: Implementación (Modules, Processes, Entities)
- **$\mathcal{G}_{Ops}$**: Operación (Services, Events)

Ver: [ontology/ontologia_categorica_goreos.md](ontology/ontologia_categorica_goreos.md)

## Herramientas

| Script                                 | Descripción                        |
| -------------------------------------- | ---------------------------------- |
| `tools/validation/verify_ontology.py`  | Verifica conformidad con ontología |
| `tools/composition/compose_domains.py` | Genera dominios como Σ-Lifts       |

## Licencia

Propiedad de Gobierno Regional. Uso interno.
