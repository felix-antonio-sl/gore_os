# Guía de Ingeniería Composicional — GORE OS

## 2. Stack Tecnológico

### 2.1. Decisiones y Justificación Categórica

| Capa           | Tecnología       | Justificación Categórica                          |
| -------------- | ---------------- | ------------------------------------------------- |
| **Runtime**    | Bun 1.x          | TypeScript nativo, tipos preservados en runtime   |
| **Framework**  | Hono             | Middlewares composicionales `(ctx) → ctx'`        |
| **API**        | tRPC v11         | Funtores tipados `Input → Output` end-to-end      |
| **Validación** | Zod              | Clasificador Ω: `χ: X → Bool` con inferencia      |
| **ORM**        | Drizzle          | Adjunción `ORM⊣Reflect` verificable, schema-first |
| **FSM**        | XState v5        | Coalgebras `c: Estado → F(Estado)` formales       |
| **DB**         | PostgreSQL 16    | Preserva límites finitos (JOINs, FKs, UNIQUE)     |
| **Geo**        | PostGIS 3.4      | Topos de Sheaves para L9 Territorial              |
| **Cache**      | Redis (opcional) | Colímites materializados                          |
| **Monorepo**   | Turborepo        | Composición de paquetes como funtores             |

### 2.2. Decisiones de NO Usar

| Tecnología        | Razón de Exclusión                                                            |
| ----------------- | ----------------------------------------------------------------------------- |
| **MongoDB/NoSQL** | Pierde morfismos (FKs). Modelo GORE es altamente relacional (~4500 morfismos) |
| **GraphQL**       | Over-engineering para sistema interno. N+1 problems. tRPC ofrece mejor DX     |
| **Prisma**        | Query engine opaco. Drizzle es más transparente y preserva adjunción          |
| **Express**       | Legacy. Hono es más rápido y composicional                                    |

### 2.4. Frontend (Opción Híbrida)

El frontend puede ser:

**Opción A: HTMX + Alpine (Hypermedia-driven)**

- Servidor renderiza HTML, HTMX sincroniza parciales
- Ideal para formularios y flujos lineales
- Menor complejidad de estado en cliente

**Opción B: React + tRPC Client (SPA)**

- Type-safety completa client-server
- Ideal para dashboards interactivos
- React Query para cache y optimistic updates

**Recomendación**: Híbrido. HTMX para módulos CRUD simples, React para dashboards complejos (CORE, AR, GR).

### 2.5. Infraestructura

| Componente     | Tecnología               | Propósito                     |
| -------------- | ------------------------ | ----------------------------- |
| **Containers** | Docker Compose v2        | Desarrollo local + producción |
| **DB Dev**     | `postgis/postgis:16-3.4` | Base de datos + geo           |
| **Cache**      | Redis 7 Alpine           | Queue + Cache                 |
| **Auth**       | Keycloak 24              | Identity Provider (SSO)       |
| **Quality**    | Vitest + Biome           | Tests + Linting               |
| **CI/CD**      | GitHub Actions           | Automatización                |
| **Deploy**     | Docker Swarm / K8s       | Producción (TBD)              |

### 3.3. Reglas de Oro

| Regla                    | Descripción                                                 |
| ------------------------ | ----------------------------------------------------------- |
| **Schema First**         | Drizzle schema es la fuente de verdad para tipos            |
| **Validate at Boundary** | Zod valida en entrada de tRPC, no en dominio interno        |
| **Pure Core**            | `packages/core` no tiene I/O. Solo tipos y lógica pura      |
| **No Raw SQL**           | Todo query pasa por Drizzle (preserva adjunción)            |
| **FSM Explícita**        | Estados de entidades viven en XState, no en flags booleanos |

## 11. Operaciones y Despliegue

### 11.1. Topología de Producción (Single-Host)

```
┌─────────────────────────────────────────────────────────────┐
│                    Hetzner Ubuntu Server                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐                                                │
│  │  Caddy  │ ◄── TLS (Let's Encrypt)                        │
│  │ (proxy) │                                                 │
│  └────┬────┘                                                │
│       │                                                      │
│  ┌────┴────────────────────────────────────────────────┐    │
│  │              Docker Network (internal)               │    │
│  │  ┌─────┐  ┌─────┐  ┌────────┐  ┌─────┐  ┌───────┐  │    │
│  │  │ api │  │ web │  │keycloak│  │redis│  │postgres│  │    │
│  │  └─────┘  └─────┘  └────────┘  └─────┘  └───────┘  │    │
│  └──────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 11.2. Servicios Docker Requeridos

| Servicio   | Imagen                         | Propósito             |
| ---------- | ------------------------------ | --------------------- |
| `postgres` | `postgis/postgis:16-3.4`       | Base de datos + geo   |
| `redis`    | `redis:7-alpine`               | Queue + Cache         |
| `keycloak` | `quay.io/keycloak/keycloak:24` | Identity Provider     |
| `api`      | Build local                    | Backend Hono + tRPC   |
| `web`      | Build local                    | Frontend React/Vite   |
| `worker`   | Build local                    | Jobs async (DS8/DS12) |
| `caddy`    | `caddy:2-alpine`               | Reverse proxy + TLS   |

### 11.3. Servicios Recomendados (Observabilidad)

| Servicio         | Propósito                           |
| ---------------- | ----------------------------------- |
| `prometheus`     | Métricas                            |
| `grafana`        | Dashboards                          |
| `loki`           | Agregación de logs                  |
| `otel-collector` | Traces distribuidos                 |
| `minio`          | Object storage S3 (documentos DS10) |

### 11.4. Persistencia y Backups

| Componente     | Estrategia                               |
| -------------- | ---------------------------------------- |
| **PostgreSQL** | `pg_dump` diario + WAL archiving         |
| **Redis**      | RDB snapshots (si durabilidad requerida) |
| **Keycloak**   | Export de realm + backup de DB           |
| **Documentos** | S3/MinIO con replicación                 |

### 11.5. Seguridad Operativa

| Control  | Implementación                  |
| -------- | ------------------------------- |
| SSH      | Solo llaves, sin password       |
| Firewall | UFW: 22, 80, 443                |
| Fail2ban | Activo para SSH                 |
| Updates  | Unattended-upgrades habilitado  |
| Secrets  | Variables de entorno, no en git |

### 11.6. CI/CD (GitHub Actions → Hetzner)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and Push Images
        run: |
          docker build -t ghcr.io/gore-nuble/api:${{ github.sha }} ./apps/api
          docker push ghcr.io/gore-nuble/api:${{ github.sha }}
          
      - name: Deploy to Hetzner
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.HETZNER_HOST }}
          username: deploy
          key: ${{ secrets.HETZNER_SSH_KEY }}
          script: |
            cd /opt/gore-os
            docker compose -f docker-compose.prod.yml pull
            docker compose -f docker-compose.prod.yml up -d
```

---

## Apéndice A: Glosario de Tecnologías

| Tecnología         | Qué es                              | Rol en GORE OS                         |
| ------------------ | ----------------------------------- | -------------------------------------- |
| **Bun**            | Runtime JS/TS con tooling integrado | Ejecutar monorepo, scripts, dev server |
| **Hono**           | Framework HTTP minimalista          | Capa HTTP del backend                  |
| **tRPC v11**       | RPC type-safe                       | API end-to-end tipada                  |
| **Effect-TS**      | Modelo de efectos funcional         | Invariantes, errores tipados           |
| **Zod**            | Schemas + validación runtime        | Validar en boundaries                  |
| **Drizzle**        | ORM schema-first                    | Adjunción ORM⊣Reflect                  |
| **XState v5**      | State machines formales             | Coalgebras de lifecycle                |
| **PostgreSQL 16**  | RDBMS transaccional                 | Integridad, auditoría                  |
| **PostGIS 3.4**    | Extensión geo                       | Dominio territorial                    |
| **Redis 7**        | Cache + Queue                       | Workers async                          |
| **Keycloak 24**    | Identity Provider                   | SSO, RBAC, ClaveÚnica                  |
| **Turborepo**      | Monorepo build system               | Coordinación de paquetes               |
| **Vitest**         | Test runner                         | Tests unitarios/integración            |
| **Biome**          | Linter + Formatter                  | Calidad de código                      |
| **Pino**           | Logger estructurado                 | Observabilidad                         |
| **Docker Compose** | Orquestación local/prod             | Paridad dev/prod                       |
