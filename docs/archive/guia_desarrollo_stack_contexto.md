# Guía práctica de desarrollo — `gore_os` (stack canónico + contexto TDE)

Este documento es una guía **operativa** para desarrollar correctamente `gore_os` usando el stack canónico (Bun + Hono + tRPC + Zod + Drizzle + Postgres/PostGIS + Redis + Keycloak + React/Vite + Docker Compose), considerando el contexto de **Transformación Digital del Estado (TDE)**.

Ver también:

- `docs/development_guide.md` (estándares composicionales, invariantes, checklist pre-merge)
- `docs/diseno_gore_os.md` (especificación del sistema, estructura del repo, docker-compose)
- `docs/analisis_stack.md` (rol de cada tecnología + sección TDE de componentes del stack)

---

## 1) Principios operativos (lo que guía decisiones de implementación)

- **Docker-first**
  - Desarrollo y producción deben usar el mismo conjunto de servicios (mismo contrato de red, variables y dependencias).

- **Pipeline composicional**
  - Ontología/Modelo → Schema DB → Tipos/Validación → API → UI → Operación.
  - Evitar “saltarse capas” (por ejemplo, exponer payloads sin Zod, o queries sin repositorio).

- **TDE como requisito transversal**
  - DS9 (autenticación), DS10 (expediente/documentos), DS8 (notificaciones), DS12 (interoperabilidad), DS7 (seguridad) y RAT (datos personales) deben traducirse a:
    - estructuras persistentes
    - trazabilidad (logs/audit)
    - tests verificables

---

## 2) Setup local (mínimo viable)

- **Prerequisitos**
  - Docker + Docker Compose v2
  - Bun 1.x
  - Git

- **Arranque recomendado**
  - Levantar servicios base:
    - Postgres/PostGIS
    - Redis
    - Keycloak
  - Aplicar migraciones
  - Levantar `api` y `web`

- **Regla de oro**
  - Si algo depende de infraestructura (DB/Redis/Keycloak), debe estar definido en `docker-compose.yml`.

---

## 3) Estructura de implementación (dónde va cada cosa)

- **Dominio puro** (`packages/core`)
  - **Qué va aquí**:
    - tipos de dominio
    - Zod schemas
    - invariantes
    - FSM (XState) cuando aplique
  - **Qué no va aquí**:
    - I/O (DB, HTTP, SDKs)

- **Persistencia** (`packages/db`)
  - **Qué va aquí**:
    - Drizzle schema + migraciones
    - repositories (queries tipadas)
  - **Regla**:
    - los repositorios no deben “hacer negocio”; solo acceso a datos.

- **API** (`apps/api`)
  - **Qué va aquí**:
    - routers tRPC
    - services (orquestación, side-effects)
    - middlewares (auth, logging, tracing)

- **Workers** (recomendado como app/paquete separado)
  - **Qué va aquí**:
    - notificaciones DS8
    - interoperabilidad DS12
    - sincronizaciones SIGFE/MDSF/SISREC
  - **Regla**:
    - todo worker debe ser idempotente y reintentable.

- **UI** (`apps/web`)
  - **Qué va aquí**:
    - vistas, formularios, dashboards
    - consumo de tRPC

---

## 4) Ciclo de desarrollo recomendado (dev loop)

- **1. Partir desde una story + requisito TDE asociado**
  - Identifica si la historia toca:
    - autenticación (DS9)
    - expediente/documentos (DS10)
    - notificaciones (DS8)
    - interoperabilidad (DS12)
    - seguridad/auditoría (DS7)
    - datos personales (RAT)

- **2. Modelar contrato de dominio primero**
  - Define `z.object(...)` canónico.
  - Define invariantes (idealmente como funciones puras o `Effect`).

- **3. Persistencia (schema + migration)**
  - Agrega tablas/constraints.
  - Migra de forma **compatible hacia atrás** cuando sea posible.

- **4. API (tRPC)**
  - `.input(...)` siempre validado.
  - Define errores tipados y consistentes.

- **5. UI**
  - Consume procedimientos (no duplicar lógica de dominio en UI).

- **6. Verificación**
  - tests (Vitest)
  - `typecheck`
  - `lint`

---

## 5) Disciplina de datos (DB) y migraciones

- **Reglas mínimas**
  - No aplicar cambios manuales en DB (solo migrations).
  - Preferir constraints en DB (UNIQUE/FK/CHECK) para invariantes estructurales.
  - Usar timestamps en **UTC** (importante para DS10/DS12).

- **Documentos/expediente (DS10)**
  - Mantener:
    - `IUIe` (identificador único institucional) con restricción de unicidad.
    - trazabilidad mínima de operaciones sobre expediente/documentos.

---

## 6) Asincronía (Redis/Workers) — DS8 y DS12

- **Cuándo usar async**
  - Envío/consulta de notificaciones (DS8)
  - Interoperabilidad con PISEE y terceros (DS12)
  - Procesos batch (verificaciones diarias, sincronizaciones)

- **Reglas de implementación**
  - **Idempotencia**: re-ejecutar no debe duplicar efectos.
  - **Outbox/registro**: persistir intención/evento antes de enviar.
  - **Reintentos**: backoff + máximo de intentos + dead-letter.
  - **Correlación**: cada job debe llevar `correlation_id` y quedar trazable.

---

## 7) Identidad y seguridad (Keycloak + DS7/DS9)

- **Keycloak**
  - Definir:
    - realms
    - clients
    - roles (por módulo/capacidad)

- **Enforcement en API**
  - `publicProcedure` solo cuando sea explícitamente público.
  - `protectedProcedure` para todo lo autenticado.
  - Autorización por rol/atributos (RBAC/ABAC) en middleware o en cada procedimiento.

- **Logging seguro**
  - No loggear secretos ni datos personales innecesarios.
  - Sanitizar payloads.

---

## 8) Observabilidad (para auditoría DS7 y trazabilidad DS10/DS12)

- **Logging estructurado**
  - Cada operación debe registrar:
    - `morfismo`
    - `actor`
    - `duracion_ms`
    - `resultado` (ok/error)
    - `correlation_id`

- **Recomendado**
  - OpenTelemetry (traces)
  - Prometheus (métricas)
  - Grafana (dashboards)
  - Loki (logs)

---

## 9) Checklist TDE mínimo por feature (Definition of Done)

- **DS9 (Auth)**
  - flujo OIDC correcto, roles definidos, enforcement en API.

- **DS10 (Expediente/Documentos)**
  - `IUIe` y trazabilidad mínima persisten.
  - timestamps en UTC.

- **DS8 (Notificaciones)**
  - constancia persistida (código tx, estado, fecha/hora).
  - proceso async con reintentos.

- **DS12 (Interoperabilidad)**
  - registro de transacción interoperable con clasificación de datos.

- **DS7 (Seguridad)**
  - logs/audit para acciones críticas.
  - controles de acceso verificados.

- **RAT (datos personales)**
  - si se introduce tratamiento nuevo, queda registrado/actualizado.

---

## 10) Reglas de PR (mínimo)

- **Antes de abrir PR**
  - `lint` / `typecheck` / `test` pasan.
  - no hay credenciales en commits.
  - si afecta DS8/DS10/DS12, incluye evidencia (tests, logs, migraciones, tablas).

---

# Estado

- Este documento es un **playbook** de implementación; no reemplaza `development_guide.md`.
