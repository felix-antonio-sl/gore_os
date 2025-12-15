# Stack de `gore_os`: qué es cada tecnología y qué rol cumple

Este documento resume el **stack canónico** descrito en `docs/development_guide.md` y `docs/diseno_gore_os.md`, y agrega el **modo de trabajo** esperado (IDE) y el **modo de operación** (servidor dedicado docker-first).

Pipeline mental (funtorial):

`Ontología YAML → Schema DB → Tipos/Validación → API → UI → Operación (Docker/CI/Obs)`

---

## 1) Runtime y ejecución

- **Bun (runtime JS/TS)**
  - **Qué es**: runtime tipo Node.js, con tooling integrado (runner, bundler, package manager).
  - **Rol en GORE OS**:
    - Ejecutar el monorepo TypeScript en desarrollo.
    - Ejecutar scripts de tooling (`dev`, `typecheck`, `lint`, `db:migrate`, etc.).

- **Node.js (workers/adapters, opcional/estratégico)**
  - **Qué es**: runtime estándar del ecosistema JS.
  - **Rol en GORE OS**:
    - Correr **workers de integración** y conectores con máxima compatibilidad de librerías (SIGFE/MDSF/SISREC/PISEE).
    - Alternativa para producción si quieres minimizar riesgo operativo asociado a runtime.

---

## 2) Backend HTTP y API tipada

- **Hono (framework HTTP)**
  - **Qué es**: framework HTTP minimalista (routing + middleware), diseñado para composición.
  - **Rol en GORE OS**:
    - Ser la capa HTTP del backend `apps/api`.
    - Encapsular cross-cutting concerns (auth, logging, CORS, rate limits, tracing).

- **tRPC v11 (API type-safe RPC)**
  - **Qué es**: framework para definir procedimientos RPC con tipos compartidos (sin contrato OpenAPI/GraphQL como primario).
  - **Rol en GORE OS**:
    - Implementar el functor **`F_API: Types → Procedures`**.
    - Garantizar type-safety end-to-end (cliente ↔ servidor), reduciendo drift y bugs de contrato.

- **Effect-TS (modelo de efectos)**
  - **Qué es**: librería para modelar computaciones con efectos como `Effect<A, E, R>`.
  - **Rol en GORE OS**:
    - Implementar invariantes como validaciones componibles (financieras, FSM, activos).
    - Tipar errores (en vez de excepciones implícitas) y estandarizar control de fallas.
    - Mejorar testeabilidad de lógica de negocio (servicios puros + “ports/adapters”).

---

## 3) Tipos y validación

- **Zod (schemas + validación)**
  - **Qué es**: schemas runtime + inferencia TypeScript.
  - **Rol en GORE OS**:
    - “Validate at boundary”: validar inputs de procedimientos tRPC y payloads externos.
    - Proveer tipos canónicos (`z.infer`) y soportar uniones discriminadas (sum types).

---

## 4) Persistencia y datos

- **PostgreSQL 16 (RDBMS)**
  - **Qué es**: base de datos relacional transaccional.
  - **Rol en GORE OS**:
    - Sostener integridad relacional (FK/UNIQUE/CHECK) para un dominio altamente relacional.
    - Base de auditoría y consistencia (transacciones, aislamiento).

- **PostGIS 3.4 (geoespacial)**
  - **Qué es**: extensión de Postgres para tipos y funciones geo.
  - **Rol en GORE OS**:
    - Habilitar todo el dominio territorial: mapas, capas, análisis espacial.

- **Drizzle (ORM / query builder schema-first)**
  - **Qué es**: ORM ligero donde el schema en TS guía queries tipadas.
  - **Rol en GORE OS**:
    - Implementar `Sch_GORE` (tablas) y mantener coherencia Schema ↔ Types ↔ Queries.
    - Ejecutar migraciones y sostener disciplina “no raw SQL” en el día a día.

---

## 5) Máquinas de estado (FSM) y lifecycle

- **XState v5 (state machines / statecharts)**
  - **Qué es**: framework para máquinas de estado explícitas.
  - **Rol en GORE OS**:
    - Modelar lifecycles críticos (IPR multi-track, convenios, rendiciones, etc.).
    - Garantizar transiciones válidas (invariantes `INV_FSM_*`).
    - Soportar auditoría de “qué cambió”, “cuándo” y “por quién”.

---

## 6) Cache, colas y asincronía

- **Redis 7 (cache / message broker ligero)**
  - **Qué es**: datastore in-memory, usado para cache y streams.
  - **Rol en GORE OS**:
    - Cache (cuando se necesite).
    - Cola/streams para procesos async:
      - notificaciones DS8
      - integraciones DS12/PISEE
      - sincronizaciones con SIGFE/MDSF/SISREC

---

## 7) Frontend

- **React 18 (UI framework)**
  - **Qué es**: librería de UI basada en componentes.
  - **Rol en GORE OS**:
    - Dashboards complejos y UIs con estado rico (CORE/AR/GR), consumiendo tRPC.

- **Vite (build tool / dev server)**
  - **Qué es**: dev server + bundler moderno.
  - **Rol en GORE OS**:
    - HMR (hot reload) en desarrollo y build optimizado en producción.

- **React Query (estrategia de client cache)**
  - **Qué es**: librería para cache/estado de datos remotos.
  - **Rol en GORE OS**:
    - Cache, invalidación y optimistic updates en dashboards.

- **HTMX + Alpine (opcional/híbrido)**
  - **Qué es**: HTMX para interacciones hypermedia; Alpine para estado liviano.
  - **Rol en GORE OS**:
    - Alternativa para módulos CRUD lineales si se decide híbrido.

---

## 8) Identidad, autenticación y cumplimiento

- **Keycloak 24 (Identity Provider / IAM)**
  - **Qué es**: IdP para OAuth2/OIDC, roles, usuarios, federación.
  - **Rol en GORE OS**:
    - Centralizar SSO y RBAC.
    - Operar como broker OIDC para integrar ClaveÚnica.
    - Evitar auth “propia” para ciudadanía (alineación DS9).

- **ClaveÚnica (OIDC)**
  - **Qué es**: sistema de identidad del Estado chileno (OIDC Authorization Code Flow).
  - **Rol en GORE OS**:
    - Autenticación ciudadana/externa conforme a DS9.

---

## 9) Monorepo y productividad

- **Turborepo (monorepo build system)**
  - **Qué es**: orquestador de builds y caching para monorepos.
  - **Rol en GORE OS**:
    - Coordinar `apps/*` y `packages/*` con pipelines reproducibles.

---

## 10) Calidad (tests, lint, formato, logging)

- **Vitest (test runner)**
  - **Qué es**: runner de tests moderno.
  - **Rol en GORE OS**:
    - Tests para invariantes, repositorios y procedimientos.

- **Biome (lint/formatter)**
  - **Qué es**: linter + formatter unificado.
  - **Rol en GORE OS**:
    - Estándar de estilo y calidad en PRs.

- **Pino (logging estructurado)**
  - **Qué es**: logger JSON de alto rendimiento.
  - **Rol en GORE OS**:
    - Logging por morfismo (operación) con actor/duración y payload sanitizado.

---

## 11) Docker-first (obligatorio)

- **Docker (contenedores)**
  - **Qué es**: empaquetado/aislamiento de procesos.
  - **Rol en GORE OS**:
    - Paridad dev/prod y despliegues reproducibles.

- **Docker Compose v2 (orquestación local y base prod)**
  - **Qué es**: definición multi-servicio con redes, volúmenes y healthchecks.
  - **Rol en GORE OS**:
    - Development local completo (DB/Redis/Keycloak/API/Web).
    - Base para producción (normalmente vía `docker-compose.prod.yml`).

---

## 12) CI/CD

- **GitHub Actions**
  - **Qué es**: CI/CD basado en workflows.
  - **Rol en GORE OS**:
    - `lint` + `typecheck` + `test` + build de imágenes.
    - Push a registry (GHCR u otro).
    - Deploy a Hetzner vía SSH (pull + restart con compose).

---

# Modo de desarrollo y trabajo (lo que faltaba)

## A) IDE: Windsurf

Windsurf es el entorno de trabajo principal. El rol práctico en el proyecto es:

- **Navegación y refactor seguro**
  - Búsquedas, lectura de flujo de datos y trazabilidad de cambios.
- **Iteración rápida**
  - Cambios chicos, ejecutables, y validados con `typecheck`/tests.
- **Disciplina composicional**
  - Respetar el pipeline: Ontología → Schema → Domain → Repo → Router → UI.

## B) IDE: “antigravidity” (necesito confirmación)

No puedo asegurar qué es “antigravidity” en tu contexto sin más detalle.

- Si te refieres a un **plugin/extensión/workflow** (por ejemplo, un conjunto de prompts/agents, un sistema de tareas o un framework interno), dime:
  - **1)** ¿dónde vive? (ruta repo / nombre paquete / URL)
  - **2)** ¿qué hace? (ej: scaffolding, lint, docs, despliegue, generación)
  - **3)** ¿cómo se invoca? (comando / UI / configuración)

Con eso puedo documentar su rol exacto (y cómo se integra a `gore_os`).

## C) Ritmo de trabajo recomendado (dev loop)

- **Definición de cambio**
  - Partir desde una Story (ej: `tic-014`) o una invariante (ej: `INV_FIN_02`).
- **Implementación functorial (orden sugerido)**
  - Ontología (si corresponde) → Drizzle schema/migration → Zod types → repos → tRPC router → UI.
- **Verificación**
  - Tests (Vitest) + typecheck + lint.
- **Observabilidad**
  - Log estructurado por morfismo (Pino) + trazas cuando aplique.

---

# Operación en servidor dedicado (Hetzner, Ubuntu) — Docker-first

## A) Objetivo

Desplegar `gore_os` como un conjunto de **servicios Docker** (API, Web, DB, Redis, Keycloak) en un **Ubuntu** dedicado (Hetzner), con:

- TLS
- backups
- actualización reproducible
- separación de secretos

## B) Topología mínima sugerida (single-host)

- **Reverse proxy**: Nginx o Caddy
  - Termina TLS (Let’s Encrypt)
  - Rutea `web` y `api`
- **Servicios internos (red privada Docker)**
  - `postgres` (PostGIS)
  - `redis`
  - `keycloak`
  - `api`
  - `web`

## C) Persistencia (volúmenes)

- `postgres`: volumen dedicado (datos)
- `keycloak`: DB propia idealmente (o volumen si usas su DB embebida en dev; en prod mejor Postgres separado)
- `redis`: volumen si se usa para streams durables

## D) Backups (mínimo viable)

- **Postgres**: `pg_dump` programado (cron en host o job container) + retención
- **Volúmenes**: snapshots/rsync hacia storage externo (ideal)
- **Keycloak realm**: export programado (o IaC del realm)

## E) Seguridad operativa (mínimo)

- Ubuntu: actualizaciones automáticas de seguridad
- Acceso: SSH con llaves (sin password), firewall (UFW), fail2ban
- Docker: secretos fuera de git; `.env` solo para dev; en prod preferir secrets/variables del host

---

# CI/CD mínimo recomendado (GitHub Actions → Hetzner)

## Flujo

- **CI** (por PR y por merge)
  - `lint` / `typecheck` / `test`
  - build de imágenes Docker
  - push a registry (por ejemplo GHCR)

- **CD** (en merge a `main`)
  - SSH al host Hetzner
  - `docker compose -f docker-compose.prod.yml pull`
  - `docker compose -f docker-compose.prod.yml up -d`
  - migraciones controladas (paso explícito, no automático por réplica)

---

# TDE (Transformación Digital del Estado) — Componentes que el stack debe incorporar

Esta sección aterriza los lineamientos TDE en **piezas concretas de stack**. El objetivo es que el cumplimiento no sea solo documental, sino **implementable y verificable**.

## A) Obligatorio (si el sistema soporta procedimientos administrativos TDE)

- **DS4 — Reglamento TD (Decreto 4)**
  - **Stack/arquitectura**:
    - Plataforma debe operar 24/7 (ingresos), y registrar actuaciones con fecha/hora.
    - Interoperabilidad para no exigir documentos/datos que ya obren en poder de otro OAE.
  - **Componentes en `gore_os`**:
    - `expediente` como bounded context transversal (base para DS8/DS10).
    - “Regla de tiempo” institucional (timestamps en UTC en DB + servicios).

- **DS9 — Norma Técnica de Autenticación (Decreto 9)**
  - **Stack/infra**:
    - **Keycloak** como IdP y broker **OIDC** (ClaveÚnica).
    - **Reverse proxy con TLS** (TLSv1.2+).
    - Medidas anti-abuso (rate limit / bloqueo / CAPTCHA) configurables.
  - **Componentes en `gore_os`**:
    - Autenticación ciudadana: prohibido implementar mecanismos “propios” fuera del marco oficial.

- **DS10 — Norma Técnica de Documentos y Expedientes Electrónicos (Decreto 10)**
  - **Stack/infra**:
    - Persistencia de **expedientes**, **documentos** y **trazabilidad mínima** (auditable).
    - Registro de fecha/hora en UTC.
  - **Componentes en `gore_os`**:
    - Generador y validador de **IUIe** (identificador único de expediente).
    - Modelo de eventos del expediente (creación, incorporación, modificación, eliminación, accesos).

- **DS8 — Norma Técnica de Notificaciones (Decreto 8)**
  - **Stack/infra**:
    - Servicio de notificaciones con persistencia de **constancia** (código tx, estados, fechas/horas).
    - Procesamiento asíncrono para reintentos/consulta de estados.
  - **Componentes en `gore_os`**:
    - Resolver DDU (casilla/email/excepción/sin DDU).
    - Enlazar notificación ↔ expediente (IUIe).
    - Regla de “notificación practicada” (3 días hábiles o lectura, según aplique en implementación).

- **DS12 — Norma Técnica de Interoperabilidad (Decreto 12)**
  - **Stack/infra**:
    - Integración mediante **nodo/adapter** (PISEE) y **registro de trazabilidad de transacciones**.
    - Gestión de acuerdos/autorizaciones para consumo (y consentimiento en datos sensibles).
  - **Componentes en `gore_os`**:
    - Worker(s) de interoperabilidad + tabla/log de transacciones interoperables (timestamp UTC, clasificación de datos, resultado).

- **DS7 — Norma Técnica de Seguridad de la Información y Ciberseguridad (Decreto 7)**
  - **Stack/infra**:
    - Política y gobernanza (CISO/responsables no externalizables) + registro de eventos.
    - Control de acceso por roles (RBAC) + auditoría de acciones.
  - **Componentes en `gore_os`**:
    - Logging estructurado por morfismo (ya definido) + trazabilidad asociada a actor.

- **Datos personales (RAT) + minimización/anonimización**
  - **Stack/infra**:
    - Registro interno de tratamientos (RAT) con versión/historial.
  - **Componentes en `gore_os`**:
    - Entidad `RAT` (data governance) y UI/admin mínima.
    - Pipeline separado para analítica (si aplica) con controles de anonimización.

## B) Recomendado (para que sea operable y demostrable)

- **Repositorio documental externo (DS10)**
  - **Dev**: MinIO (S3 compatible) en Docker.
  - **Prod**: Object storage S3 compatible.

- **Observabilidad (DS7/DS12/DS10)**
  - OpenTelemetry (traces), Prometheus (métricas), Grafana (dashboards), Loki (logs agregados).

- **Calidad Web (guía TDE de Calidad WEB)**
  - Checklist de accesibilidad/usabilidad/lenguaje claro incorporado a DoD de frontend.

## C) Servicios Docker adicionales típicos para TDE

- **`reverse-proxy`** (Caddy o Nginx) con TLS
- **`worker`** (notificaciones DS8 + interoperabilidad DS12 + jobs)
- **`minio`** (recomendado para documentos DS10 en dev)
- **`otel-collector` + `prometheus` + `grafana` + `loki`** (recomendado)

# Estado de la tarea

- **Completado**: se agregó la capa “modo de trabajo” (IDE) y “operación” (Hetzner Ubuntu docker-first) al análisis del stack.
- **Completado**: se agregó sección TDE con componentes obligatorios/recomendados para DS4/DS7/DS8/DS9/DS10/DS12 y gobierno de datos.
- **Pendiente**: confirmar qué es exactamente “antigravidity” (plugin/comando/repositorio) para documentar su rol real en el workflow.

Ver también:

- [`docs/guia_desarrollo_stack_contexto.md`](guia_desarrollo_stack_contexto.md)
