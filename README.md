# GORE OS

> Sistema Operativo del Gobierno Regional de Ñuble

**Stack**: Bun + Hono + Effect + tRPC + Drizzle + XState  
**Paradigma**: Ingeniería Composicional (Functorial Pipeline)

---

## Quick Start

```bash
# 1. Clonar e instalar
git clone git@github.com:gore-nuble/gore-os.git
cd gore-os
bun install

# 2. Levantar servicios
docker compose up -d

# 3. Aplicar migraciones
bun db:migrate

# 4. Desarrollo
bun dev
```

## Estructura del Proyecto

```
gore-os/
├── apps/                    # Aplicaciones
│   ├── api/                 # Backend (Hono + tRPC + Effect)
│   └── web/                 # Frontend (React + Vite)
├── packages/                # Paquetes compartidos
│   ├── db/                  # Drizzle schemas + migraciones
│   ├── core/                # Lógica de dominio pura
│   └── ui/                  # Componentes React compartidos
├── docs/                    # Documentación
│   ├── blueprint/           # Dominios y visión del sistema
│   ├── user-stories/        # Historias de usuario por dominio
│   └── architecture/        # Stack y arquitectura técnica
└── .agent/workflows/        # Workflows de desarrollo
```

## Servicios Locales

| Servicio   | URL                   | Credenciales      |
| ---------- | --------------------- | ----------------- |
| API        | http://localhost:3000 | -                 |
| Frontend   | http://localhost:5173 | -                 |
| Keycloak   | http://localhost:8080 | admin/admin       |
| PostgreSQL | localhost:5432        | postgres/postgres |
| Redis      | localhost:6379        | -                 |

## Comandos

```bash
bun dev              # Desarrollo (todos los servicios)
bun build            # Build de producción
bun test             # Tests
bun lint             # Linting (Biome)
bun db:generate      # Generar migración Drizzle
bun db:migrate       # Aplicar migraciones
bun db:studio        # Drizzle Studio
```

## Documentación

- [Stack Tecnológico](docs/architecture/stack.md)
- [Blueprint del Sistema](docs/blueprint/vision_general.md)
- [Reglas de Desarrollo](AGENTS.md)

## Workflows

- `/setup-desarrollo` — Configurar entorno local
- `/nuevo-modulo-backend` — Crear módulo Hono + tRPC + Effect
- `/nueva-entidad-dominio` — Crear entidad Drizzle + XState

---

*Gobierno Regional de Ñuble © 2025*
