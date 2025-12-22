# Stack Tecnológico GORE OS

> **Versión:** 2.0  
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

Vea [categorical-view/pipeline.md](categorical-view/pipeline.md) para más detalle.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA COMPOSICIONAL                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FRONTERA (I/O)              PUENTE               NÚCLEO (Puro)            │
│   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐            │
│   │   Zod        │       │   tRPC       │       │  Effect-TS   │            │
│   │   Schemas    │──────►│   Handler    │──────►│   Programs   │            │
│   └──────────────┘       └──────────────┘       └──────────────┘            │
│         ▲                       │                       │                   │
│         │                       ▼                       ▼                   │
│   React/Forms             Effect.runPromise        Drizzle ORM              │
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

## 3. Estructura Arquitectónica C4

Para una descripción detallada, consulte los documentos en los subdirectorios:

- **[C1 Contexto](c1_context/system_context.md)**: GORE_OS en el ecosistema regional.
- **[C2 Contenedores](c2_containers/containers.md)**: Despliegue de servicios (API, Web, DB, Workers).
- **[C3 Componentes](c3_components/components.md)**: Estructura interna de la API (Módulos, Shared Kernel).

---

## 4. Reglas de Desarrollo

| Regla                    | Descripción                                                 |
| ------------------------ | ----------------------------------------------------------- |
| **Schema First**         | Drizzle schema es la fuente de verdad para tipos            |
| **Validate at Boundary** | Zod valida en entrada de tRPC, no en dominio interno        |
| **Pure Core**            | `packages/core` no tiene I/O. Solo tipos y lógica pura      |
| **No Raw SQL**           | Todo query pasa por Drizzle (preserva adjunción)            |
| **FSM Explícita**        | Estados de entidades viven en XState, no en flags booleanos |

---

## 5. Frontend (Enfoque Híbrido)

| Enfoque        | Tecnología          | Uso Recomendado                            |
| -------------- | ------------------- | ------------------------------------------ |
| **Hypermedia** | HTMX + Alpine       | Módulos CRUD simples, formularios lineales |
| **SPA**        | React + tRPC Client | Dashboards interactivos, flujos complejos  |

**Recomendación:** Híbrido. HTMX para módulos administrativos simples, React para dashboards (CORE, AR, GR).

---

## 6. Infraestructura y Operaciones

Consulte la arquitectura de contenedores y despliegue en [C2 Contenedores](c2_containers/containers.md).

### Resumen de Producción
- **Hosting**: Hetzner Cloud (Ubuntu Server)
- **Proxy**: Caddy (Auto-HTTPS)
- **CI/CD**: GitHub Actions (Build -> Docker Registry -> SSH Deploy)
- **Backups**: `pg_dump` diario a S3
- **Seguridad**: Firewall estricto, SSH keys only, Secretos en env vars

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
