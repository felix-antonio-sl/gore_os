# Modelo Semántico GORE_OS

> Para el contrato de arquitectura y cambios: ver [../AGENTS.md](../AGENTS.md).

## Estructura

```text
model/
├── stories/          # 818 historias de usuario (YAML, fuente de verdad)
├── entities/         # 141 entidades aceptadas (YAML)
├── processes/        # 81 procesos del dominio (YAML)
├── omega/            # 12 definiciones ontológicas (YAML)
├── model_goreos/     # DDL PostgreSQL ejecutable (128 tablas, 5 schemas)
│   ├── sql/          # DDL, seeds, migraciones, triggers, indexes
│   └── docs/         # ERD, modelo conceptual, decisiones de diseño
└── GLOSARIO.yml      # 57 términos institucionales
```

## Regla de Derivación Estructural

> **A1**: Toda Entity traza a al menos una Story de origen.
> **A2**: Todo artefacto de solución habilita (no describe) Stories.
> **A3**: Los Módulos emergen de la agrupación de Stories.
> **A4**: Derivación unidireccional: Stories → Entities → Artefactos → Módulos.

## Referencia

- [MANIFESTO.md](../MANIFESTO.md) — Identidad y principios
- [AGENTS.md](../AGENTS.md) — Arquitectura y convenciones para cambios
- [model_goreos/README.md](model_goreos/README.md) — Guía del modelo PostgreSQL
- [model_goreos/docs/GOREOS_ERD_v3.md](model_goreos/docs/GOREOS_ERD_v3.md) — ERD + diccionario
