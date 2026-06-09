# GORE_OS

**Sistema operativo institucional del Gobierno Regional de Ñuble (Chile).**

GORE_OS digitaliza, automatiza e inteligencia el GORE: gestión de inversiones públicas (IPR), compromisos operacionales, presupuesto, convenios, actos administrativos, indicadores DGI y sesiones CORE — todo en una plataforma integrada con 820 user stories como fuente de verdad.

## Quick Start

```bash
docker compose up -d api web                       # Start (requires goreos_db)
docker compose --profile standalone up -d           # With standalone PostgreSQL
curl http://localhost:8000/api/health               # Verify API
open http://localhost:3000/dev                      # Dev login (24 test users)
```

## Stack

Next.js 16 → FastAPI → PostgreSQL 16. Raw SQL (no ORM). 121 tablas. 820 user stories. Filosofía Story-First.

## Documentation Map

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | **Source of truth**: arquitectura, modelo de datos, reglas, convenciones, comandos |
| [INDEX.md](INDEX.md) | Índice navegable del repositorio |
| [MANIFESTO.md](MANIFESTO.md) | Identidad, génesis y filosofía del proyecto |
| [docs/README.md](docs/README.md) | Índice de toda la documentación técnica |

## Resources

- [Onboarding](docs/ONBOARDING.md) — Setup local, patrones clave, flujo de feature
- [ADR](docs/adr/) — 8 Architecture Decision Records
- [Model](model/model_goreos/README.md) — DDL, ERD, modelo conceptual, glosario
- [Testing](docs/GORE_OS_Testing_Ciclo3.md) — Guía de testing integral
- [Plans](docs/plans/README.md) — Planes de implementación por dominio