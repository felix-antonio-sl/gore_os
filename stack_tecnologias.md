# Stack Tecnológico GORE OS

> **Versión:** 1.0  
> **Última actualización:** Diciembre 2025  
> **Paradigma:** Ingeniería Composicional (Functorial Pipeline)

---

## 1. Stack Canónico

| Capa            | Tecnología            | Rol Categórico                        | Versión |
| --------------- | --------------------- | ------------------------------------- | ------- |
| **Runtime**     | Bun                   | VM JavaScript de alto rendimiento     | ^1.1    |
| **HTTP**        | Hono                  | Middleware composable `(ctx) → ctx'`  | ^4.0    |
| **Effects**     | Effect-TS             | Monad Stack `Effect<A, E, R>`         | ^3.0    |
| **API**         | tRPC v11              | Functor `S → API` (Type-Safe RPC)     | ^11.0   |
| **FSM**         | XState v5             | Coalgebra `c: Estado → F(Estado)`     | ^5.0    |
| **ORM**         | Drizzle               | Adjunción `ORM⊣Reflect`, schema-first | ^0.30   |
| **Validation**  | Zod                   | Subobject Classifier Ω (Schemas)      | ^3.23   |
| **Database**    | PostgreSQL + PostGIS  | Persistencia geo-referenciada         | ^16/3.4 |
| **Frontend**    | React + Vite          | Interfaz de Capacidad Humana          | ^18/^5  |
| **Auth**        | Keycloak / ClaveÚnica | Identity Provider (SSO, RBAC)         | ^24     |
| **Container**   | Docker + Compose      | Orquestación local/producción         | ^24/^2  |
| **Queue/Cache** | Redis                 | Message Broker + Cache                | ^7      |
| **Monorepo**    | Turborepo             | Composición de paquetes como funtores | ^2      |
| **Quality**     | Vitest + Biome        | Tests + Linting                       | latest  |

---

## 2. Arquitectura de Integración

### 2.1. Patrón Composicional: Frontera/Núcleo/Puente

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA COMPOSICIONAL                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FRONTERA (I/O)              PUENTE               NÚCLEO (Puro)            │
│   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐           │
│   │   Zod        │       │   tRPC       │       │  Effect-TS   │           │
│   │   Schemas    │──────►│   Handler    │──────►│   Programs   │           │
│   └──────────────┘       └──────────────┘       └──────────────┘           │
│         ▲                       │                       │                   │
│         │                       ▼                       ▼                   │
│   React/Forms             Effect.runPromise        Drizzle ORM             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Regla de Oro:**
- **Zod** valida en la frontera (tRPC inputs, React Hook Form)
- **Effect-TS** maneja lógica de dominio (errores tipados, dependencias)
- Los handlers actúan como adaptadores que ejecutan programas Effect

```typescript
// Patrón Canónico
t.procedure
  .input(ZodSchema)                           // Frontera: Zod valida
  .mutation(({ input }) => 
    Effect.runPromise(DomainLogic(input))     // Núcleo: Effect ejecuta
  )
```

### 2.2. Decisiones de Exclusión

| Tecnología        | Razón de Exclusión                                                  |
| ----------------- | ------------------------------------------------------------------- |
| **MongoDB/NoSQL** | Pierde morfismos (FKs). Modelo GORE es relacional (~4500 morfismos) |
| **GraphQL**       | Over-engineering para sistema interno. tRPC ofrece mejor DX         |
| **Prisma**        | Query engine opaco. Drizzle preserva adjunción verificable          |
| **Express**       | Legacy. Hono es más rápido y composicional                          |

---

## 3. Reglas de Desarrollo

| Regla                    | Descripción                                                 |
| ------------------------ | ----------------------------------------------------------- |
| **Schema First**         | Drizzle schema es la fuente de verdad para tipos            |
| **Validate at Boundary** | Zod valida en entrada de tRPC, no en dominio interno        |
| **Pure Core**            | `packages/core` no tiene I/O. Solo tipos y lógica pura      |
| **No Raw SQL**           | Todo query pasa por Drizzle (preserva adjunción)            |
| **FSM Explícita**        | Estados de entidades viven en XState, no en flags booleanos |

---

## 4. Frontend (Enfoque Híbrido)

| Enfoque        | Tecnología          | Uso Recomendado                            |
| -------------- | ------------------- | ------------------------------------------ |
| **Hypermedia** | HTMX + Alpine       | Módulos CRUD simples, formularios lineales |
| **SPA**        | React + tRPC Client | Dashboards interactivos, flujos complejos  |

**Recomendación:** Híbrido. HTMX para módulos administrativos simples, React para dashboards (CORE, AR, GR).

---

## 5. Infraestructura

### 5.1. Topología de Producción

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

### 5.2. Servicios Docker

| Servicio   | Imagen                         | Propósito           |
| ---------- | ------------------------------ | ------------------- |
| `postgres` | `postgis/postgis:16-3.4`       | Base de datos + geo |
| `redis`    | `redis:7-alpine`               | Queue + Cache       |
| `keycloak` | `quay.io/keycloak/keycloak:24` | Identity Provider   |
| `api`      | Build local                    | Backend Hono + tRPC |
| `web`      | Build local                    | Frontend React/Vite |
| `worker`   | Build local                    | Jobs async          |
| `caddy`    | `caddy:2-alpine`               | Reverse proxy + TLS |

### 5.3. Observabilidad (Opcional)

| Servicio         | Propósito           |
| ---------------- | ------------------- |
| `prometheus`     | Métricas            |
| `grafana`        | Dashboards          |
| `loki`           | Agregación de logs  |
| `otel-collector` | Traces distribuidos |
| `minio`          | Object storage S3   |

---

## 6. Operaciones

### 6.1. Persistencia y Backups

| Componente     | Estrategia                               |
| -------------- | ---------------------------------------- |
| **PostgreSQL** | `pg_dump` diario + WAL archiving         |
| **Redis**      | RDB snapshots (si durabilidad requerida) |
| **Keycloak**   | Export de realm + backup de DB           |
| **Documentos** | S3/MinIO con replicación                 |

### 6.2. Seguridad

| Control  | Implementación                  |
| -------- | ------------------------------- |
| SSH      | Solo llaves, sin password       |
| Firewall | UFW: 22, 80, 443                |
| Fail2ban | Activo para SSH                 |
| Updates  | Unattended-upgrades habilitado  |
| Secrets  | Variables de entorno, no en git |

### 6.3. CI/CD (GitHub Actions)

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and Push
        run: |
          docker build -t ghcr.io/gore-nuble/api:${{ github.sha }} ./apps/api
          docker push ghcr.io/gore-nuble/api:${{ github.sha }}
          
      - name: Deploy
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

## Apéndice: Glosario

| Tecnología     | Descripción                         | Rol en GORE OS                         |
| -------------- | ----------------------------------- | -------------------------------------- |
| **Bun**        | Runtime JS/TS con tooling integrado | Ejecutar monorepo, scripts, dev server |
| **Hono**       | Framework HTTP minimalista          | Capa HTTP del backend                  |
| **tRPC v11**   | RPC type-safe                       | API end-to-end tipada                  |
| **Effect-TS**  | Modelo de efectos funcional         | Invariantes, errores tipados           |
| **Zod**        | Schemas + validación runtime        | Validar en boundaries                  |
| **Drizzle**    | ORM schema-first                    | Adjunción ORM⊣Reflect                  |
| **XState v5**  | State machines formales             | Coalgebras de lifecycle                |
| **PostgreSQL** | RDBMS transaccional                 | Integridad, auditoría                  |
| **PostGIS**    | Extensión geo                       | Dominio territorial                    |
| **Redis**      | Cache + Queue                       | Workers async                          |
| **Keycloak**   | Identity Provider                   | SSO, RBAC, ClaveÚnica                  |
| **Pino**       | Logger estructurado                 | Observabilidad                         |

---

*Documento parte de GORE_OS*
