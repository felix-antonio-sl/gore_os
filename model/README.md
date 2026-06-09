# Modelo Semántico GORE_OS

> Para arquitectura, comandos y convenciones: ver [../CLAUDE.md](../CLAUDE.md)

## Estructura

```text
model/
├── stories/          # 820 historias de usuario (YAML, fuente de verdad)
├── entities/         # 141 entidades aceptadas (YAML)
├── processes/        # 92 procesos del dominio (YAML)
├── omega/            # 12 definiciones ontológicas (YAML)
├── model_goreos/     # DDL PostgreSQL ejecutable (121 tablas, 4 schemas)
│   ├── sql/          # DDL, seeds, migraciones, triggers, indexes
│   └── docs/         # ERD, modelo conceptual, decisiones de diseño
└── GLOSARIO.yml      # 244 términos institucionales
```

## Regla de Derivación Estructural

> **A1**: Toda Entity traza a al menos una Story de origen.
> **A2**: Todo artefacto de solución habilita (no describe) Stories.
> **A3**: Los Módulos emergen de la agrupación de Stories.
> **A4**: Derivación unidireccional: Stories → Entities → Artefactos → Módulos.

## Referencia

- [MANIFESTO.md](../MANIFESTO.md) — Identidad y principios
- [CLAUDE.md](../CLAUDE.md) — Arquitectura y convenciones completas
- [model_goreos/README.md](model_goreos/README.md) — Guía del modelo PostgreSQL
- [model_goreos/docs/GOREOS_ERD_v3.md](model_goreos/docs/GOREOS_ERD_v3.md) — ERD + diccionario
