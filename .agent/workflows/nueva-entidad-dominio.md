---
description: Crear nueva entidad de dominio con Drizzle + XState
---

# Workflow: Nueva Entidad de Dominio

Este workflow guía la creación de una nueva entidad siguiendo el paradigma Schema-First con FSM explícita.

## Pre-requisitos

- Drizzle ORM configurado
- XState v5 instalado

---

## Pasos

### 1. Definir schema Drizzle

```typescript
// packages/db/src/schema/{entidad}.ts
import { pgTable, uuid, varchar, timestamp, pgEnum } from 'drizzle-orm/pg-core'

// Definir estados como enum PostgreSQL
export const estadoEnum = pgEnum('estado_{entidad}', [
  'borrador',
  'pendiente',
  'aprobado',
  'rechazado'
])

export const {entidad} = pgTable('{entidad}', {
  id: uuid('id').primaryKey().defaultRandom(),
  // ... campos
  estado: estadoEnum('estado').default('borrador').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
})

// Tipos inferidos
export type Entidad = typeof {entidad}.$inferSelect
export type NewEntidad = typeof {entidad}.$inferInsert
```

### 2. Exportar desde schema index

```typescript
// packages/db/src/schema/index.ts
export * from './{entidad}'
```

### 3. Generar migración

// turbo
```bash
cd packages/db && bun drizzle-kit generate
```

### 4. Aplicar migración

// turbo
```bash
cd packages/db && bun drizzle-kit migrate
```

### 5. Crear máquina XState (Coalgebra)

```typescript
// packages/core/src/machines/{entidad}.machine.ts
import { setup, assign } from 'xstate'
import type { Entidad } from '@gore-os/db'

type Context = {
  entity: Entidad | null
  error: string | null
}

type Events =
  | { type: 'SUBMIT' }
  | { type: 'APPROVE' }
  | { type: 'REJECT'; reason: string }
  | { type: 'RESET' }

export const {entidad}Machine = setup({
  types: {
    context: {} as Context,
    events: {} as Events
  }
}).createMachine({
  id: '{entidad}',
  initial: 'borrador',
  context: { entity: null, error: null },
  states: {
    borrador: {
      on: { SUBMIT: 'pendiente' }
    },
    pendiente: {
      on: {
        APPROVE: 'aprobado',
        REJECT: {
          target: 'rechazado',
          actions: assign({ error: ({ event }) => event.reason })
        }
      }
    },
    aprobado: { type: 'final' },
    rechazado: {
      on: { RESET: 'borrador' }
    }
  }
})
```

### 6. Crear tests de la máquina

// turbo
```bash
touch packages/core/src/machines/{entidad}.machine.test.ts
```

```typescript
import { describe, it, expect } from 'vitest'
import { createActor } from 'xstate'
import { {entidad}Machine } from './{entidad}.machine'

describe('{Entidad} Machine', () => {
  it('should transition borrador -> pendiente on SUBMIT', () => {
    const actor = createActor({entidad}Machine)
    actor.start()
    
    actor.send({ type: 'SUBMIT' })
    
    expect(actor.getSnapshot().value).toBe('pendiente')
  })
})
```

---

## Checklist Final

- [ ] Schema Drizzle definido (schema-first)
- [ ] Estados como pgEnum (no flags booleanos)
- [ ] Migración generada y aplicada
- [ ] Máquina XState creada (coalgebra)
- [ ] Tests de transiciones pasando
