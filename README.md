# GORE_OS Monorepo

> **Architecture:** Bun + Turborepo + Docker  
> **Approach:** Container-First Development

## Estructura

```text
gore_os/
├── apps/
│   ├── api/            # Backend (Hono) [To Be Created]
│   └── web/            # Frontend (React/Vite) [To Be Created]
├── packages/
│   ├── core/           # Shared Logic & Schemas
│   └── ui/             # Design System (React + Tailwind)
├── docker-compose.yml  # Infraestructura Local (DB + Auth)
├── package.json        # Workspace Root
└── turbo.json          # Pipeline Construction
```

## Quick Start

### 1. Prerrequisitos
- [Docker & Docker Compose](https://www.docker.com/)
- [Bun](https://bun.sh/) (`curl -fsSL https://bun.sh/install | bash`)

### 2. Infraestructura
Levantar servicios base (PostgreSQL + Keycloak):
```bash
docker-compose up -d
```

### 3. Desarrollo
Instalar dependencias y correr en modo dev (cuando existan las apps):
```bash
bun install
bun run dev
```

## Docker Strategy
Este proyecto utiliza una estrategia **Container-First**.
- El entorno local replica producción usando contenedores.
- `apps/*` tendrán sus propios `Dockerfile` para builds multicapa.
- La base de datos y autenticación son siempre externas al código, gestionadas por `docker-compose`.
