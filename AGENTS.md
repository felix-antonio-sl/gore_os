# GORE OS Development Rules

> Reglas de desarrollo para el stack composicional GORE OS.

## Stack Canónico

- **Runtime**: Bun ^1.1
- **HTTP**: Hono ^4.0
- **Effects**: Effect-TS ^3.0
- **API**: tRPC v11
- **FSM**: XState v5
- **ORM**: Drizzle ^0.30
- **Validation**: Zod ^3.23
- **Database**: PostgreSQL 16 + PostGIS 3.4

## Reglas de Arquitectura

### Patrón Frontera/Núcleo/Puente

```
FRONTERA (Zod) → PUENTE (tRPC Handler) → NÚCLEO (Effect Program)
```

1. **Zod solo en frontera**: Validar inputs de tRPC y forms. Nunca en lógica de dominio.
2. **Effect en núcleo**: Toda lógica de negocio como `Effect.Effect<A, E, R>`.
3. **tRPC como puente**: Handlers ejecutan `Effect.runPromise(program)`.

### Reglas de Oro

| Regla                    | Descripción                                      |
| ------------------------ | ------------------------------------------------ |
| **Schema First**         | Drizzle schema es la fuente de verdad para tipos |
| **Validate at Boundary** | Zod valida en entrada de tRPC, no en dominio     |
| **Pure Core**            | `packages/core` no tiene I/O directo             |
| **No Raw SQL**           | Todo query pasa por Drizzle                      |
| **FSM Explícita**        | Estados en XState, no flags booleanos            |

## Convenciones de Código

### Estructura de Módulo Backend

```
apps/api/src/modules/{nombre}/
├── router.ts      # tRPC router (Puente)
├── service.ts     # Effect service (Núcleo)
├── schemas.ts     # Zod schemas (Frontera)
└── *.test.ts      # Tests
```

### Nombrado

- **Files**: kebab-case (`user-service.ts`)
- **Types/Interfaces**: PascalCase (`UserInput`)
- **Functions**: camelCase (`createUser`)
- **Enums DB**: snake_case (`estado_convenio`)

### Imports

```typescript
// 1. External
import { Effect } from 'effect'
import { z } from 'zod'

// 2. Internal packages  
import { db } from '@gore-os/db'

// 3. Local
import { UserSchema } from './schemas'
```

## Comandos Frecuentes

```bash
# Desarrollo
bun dev                    # Levantar todos los servicios
bun dev --filter=api       # Solo API

# Base de datos
bun db:generate            # Generar migración
bun db:migrate             # Aplicar migraciones
bun db:studio              # Abrir Drizzle Studio

# Tests
bun test                   # Todos los tests
bun test --filter=api      # Solo tests de API

# Calidad
bun lint                   # Biome lint
bun format                 # Biome format
bun typecheck              # TypeScript check
```

## Anti-Patterns (Evitar)

❌ Usar `any` o `unknown` sin refinamiento  
❌ Queries SQL crudos (usar Drizzle)  
❌ Flags booleanos para estado (usar XState enum)  
❌ Zod dentro de services (solo en router)  
❌ `console.log` (usar logger Pino)  
❌ Mutación de estado (preferir funciones puras)

## Workflows Disponibles

- `/nuevo-modulo-backend` - Crear módulo con Hono + tRPC + Effect
- `/nueva-entidad-dominio` - Crear entidad con Drizzle + XState
- `/setup-desarrollo` - Configurar entorno local
