# ADR-001: Validación del Stack Tecnológico GORE_OS

> **Estado:** Aceptado
> **Fecha:** 22-Diciembre-2025
> **Contexto:** Validación exhaustiva de las elecciones tecnológicas para GORE_OS (v3.0) frente al estado del arte 2024-2025 y cumplimiento TDE.

## 1. Contexto y Problema

GORE_OS es un sistema crítico de gestión gubernamental que requiere:

1. **Alta Seguridad y Auditoría** (Marco NIST, Ley 21.180).
2. **Rendimiento en Recursos** (EVALTIC, Cloud First).
3. **Correctitud Matemática** (Paradigma Functorial, ~4500 relaciones).
4. **Desarrollo Ágil** (Equipo interno pequeño, Monorepo TypeScript).

Necesitamos confirmar si el stack `Bun + Hono + Effect-TS + tRPC + Drizzle` es la mejor elección o si existen alternativas superiores (Node.js, Express, Prisma, GraphQL).

## 2. Decisiones

### 2.1. Runtime: Bun

- **Decisión**: Mantener Bun v1.x.
- **Alternativas**: Node.js v22 (LTS), Deno v2.
- **Justificación**:
  - **Performance**: 3x más rápido en cold start y HTTP que Node.js, crucial para costos Cloud.
  - **DX**: Tooling unificado (test runner, bundler, package manager) reduce la complejidad del CI/CD.
  - **Mitigación de Riesgos**: Aunque es menos maduro que Node, para un sistema autocontenido en contenedores Docker, los riesgos de compatibilidad son controlables.

### 2.2. HTTP Framework: Hono

- **Decisión**: Utilizar Hono v4.
- **Alternativas**: Express, Fastify.
- **Justificación**:
  - **Performance**: ~37k req/sec vs ~10k de Express.
  - **Peso**: <14KB, ideal para contenedores ligeros.
  - **Ecosistema**: Compatibilidad nativa con Bun y estándares Web (Request/Response). Fastify es excelente pero añade complejidad innecesaria para nuestro caso de uso (API interna).

### 2.3. Dominio y Efectos: Effect-TS

- **Decisión**: Adoptar Effect-TS como backbone lógico.
- **Alternativas**: fp-ts, neverthrow, Try/Catch nativo.
- **Justificación**:
  - **Type Safety**: El tipo `Effect<A, E, R>` es el único que garantiza trazabilidad total de errores y dependencias en tiempo de compilación.
  - **Concurrencia**: Manejo de fibras superior a Promesas nativas para orquestación compleja.
  - **Obsolescencia**: `fp-ts` está en modo mantenimiento; Effect es el estándar moderno.

### 2.4. Capa de API: tRPC v11

- **Decisión**: Usar tRPC para comunicación Cliente-Servidor.
- **Alternativas**: GraphQL, REST (OpenAPI).
- **Justificación**:
  - **Sincronización**: Al estar en un Monorepo TypeScript, tRPC ofrece garantías de tipo end-to-end sin generación de código (codegen).
  - **Eficiencia**: Evita el over-fetching de REST y la complejidad de cacheo de GraphQL.
  - **Nota**: Si se requiere exponer API pública a terceros, se usará `trpc-openapi` para generar endpoints REST automáticamente.

### 2.5. Persistencia: Drizzle ORM + PostgreSQL

- **Decisión**: Drizzle ORM sobre PostgreSQL con PostGIS.
- **Alternativas**: Prisma, TypeORM, Kysely.
- **Justificación**:
  - **Control SQL**: Drizzle permite consultas SQL-like predecibles, evitando el "caja negra" del Query Engine de Prisma.
  - **GIS**: Soporte nativo y ligero para tipos geométricos de PostGIS, esencial para el módulo D-TERR.
  - **Performance**: Menor overhead en runtime que Prisma.

## 3. Consecuencias

### Positivas

- **Velocidad de Desarrollo**: El stack es altamente cohesivo (TypeScript en todo el stack).
- **Seguridad**: El tipado fuerte reduce a casi cero los errores de runtime (null ptrs, type mismatches).
- **Eficiencia Operativa**: Menor consumo de RAM/CPU en producción gracias a Bun/Hono.

### Negativas / Riesgos

- **Curva de Aprendizaje**: Effect-TS requiere un cambio de mentalidad (programación funcional pura) para nuevos desarrolladores.
- **Ecosistema Bun**: Posibles edge-cases con librerías de Node muy antiguas (aunque la compatibilidad es alta hoy en día).

## 4. Estado de Cumplimiento TDE

| Tecnología | Cumplimiento             | Nota                          |
| :--------- | :----------------------- | :---------------------------- |
| **Auth**   | ✅ ClaveÚnica/OIDC        | Cumple DS N°9.                |
| **Logs**   | ✅ Estructurados (NIST)   | Effect Logger + Pino.         |
| **Datos**  | ✅ Integridad Referencial | PostgreSQL Schema First.      |
| **Infra**  | ✅ Cloud First            | Docker + Servicios Stateless. |

---
*Autor: Arquitecto GORE_OS*
