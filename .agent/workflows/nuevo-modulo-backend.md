---
description: Crear nuevo módulo backend con Hono + tRPC + Effect
---

# Workflow: Nuevo Módulo Backend

Este workflow guía la creación de un nuevo módulo siguiendo el patrón composicional Frontera/Núcleo/Puente.

## Pre-requisitos

- Monorepo inicializado con Turborepo
- `packages/core` existe con tipos de dominio
- PostgreSQL + Drizzle configurado

---

## Pasos

### 1. Crear estructura del módulo

// turbo
```bash
mkdir -p apps/api/src/modules/{nombre}
touch apps/api/src/modules/{nombre}/router.ts
touch apps/api/src/modules/{nombre}/service.ts
touch apps/api/src/modules/{nombre}/schemas.ts
```

### 2. Definir schemas Zod (Frontera)

```typescript
// apps/api/src/modules/{nombre}/schemas.ts
import { z } from 'zod'

export const CreateInputSchema = z.object({
  // Campos del input
})

export const OutputSchema = z.object({
  // Campos del output
})

export type CreateInput = z.infer<typeof CreateInputSchema>
```

### 3. Crear servicio Effect (Núcleo)

```typescript
// apps/api/src/modules/{nombre}/service.ts
import { Effect, Layer } from 'effect'
import { db } from '@/db'
import type { CreateInput } from './schemas'

export class NombreService extends Effect.Tag('NombreService')<
  NombreService,
  {
    create: (input: CreateInput) => Effect.Effect<Result, DomainError>
  }
>() {}

export const NombreServiceLive = Layer.succeed(NombreService, {
  create: (input) =>
    Effect.tryPromise({
      try: () => db.insert(table).values(input).returning(),
      catch: (e) => new DatabaseError({ cause: e })
    })
})
```

### 4. Crear router tRPC (Puente)

```typescript
// apps/api/src/modules/{nombre}/router.ts
import { router, publicProcedure } from '@/trpc'
import { Effect } from 'effect'
import { CreateInputSchema } from './schemas'
import { NombreService, NombreServiceLive } from './service'

export const nombreRouter = router({
  create: publicProcedure
    .input(CreateInputSchema)
    .mutation(async ({ input }) => {
      const program = Effect.gen(function* () {
        const service = yield* NombreService
        return yield* service.create(input)
      })
      
      return Effect.runPromise(
        program.pipe(Effect.provide(NombreServiceLive))
      )
    })
})
```

### 5. Registrar en router principal

```typescript
// apps/api/src/router.ts
import { nombreRouter } from './modules/{nombre}/router'

export const appRouter = router({
  // ... otros routers
  nombre: nombreRouter
})
```

### 6. Crear tests

// turbo
```bash
touch apps/api/src/modules/{nombre}/service.test.ts
```

```typescript
// apps/api/src/modules/{nombre}/service.test.ts
import { describe, it, expect } from 'vitest'
import { Effect } from 'effect'

describe('NombreService', () => {
  it('should create entity', async () => {
    // Arrange
    const input = { /* test data */ }
    
    // Act
    const result = await Effect.runPromise(
      service.create(input).pipe(Effect.provide(TestLayer))
    )
    
    // Assert
    expect(result).toBeDefined()
  })
})
```

### 7. Verificar

// turbo
```bash
cd apps/api && bun test src/modules/{nombre}
```

---

## Checklist Final

- [ ] Schema Zod definido en frontera
- [ ] Service Effect en núcleo (sin I/O directo)
- [ ] Router tRPC como puente
- [ ] Tests unitarios pasando
- [ ] Router registrado en appRouter
