import { initTRPC } from '@trpc/server';
import { z } from 'zod';
import { Schema } from "@effect/schema";
import { Effect } from "effect";
import { db } from '../../db';
import { convenios } from './schema';
import { CreateConvenioInput, Convenio } from '@gore-os/core';
import type { Context } from '../../trpc';
// import * as TrpcEffect from '@effect/rpc-trpc'; // Removed for now

// Adapter manual Effect-Schema -> Zod para tRPC input
// En un futuro usaremos @effect/rpc directamente, por ahora puenteamos
const createConvenioZod = z.object({
    nombre: z.string(),
    ministerio: z.string(),
    regionId: z.string().uuid(),
    montoTotal: z.number().int().nonnegative(),
    fechaFirma: z.string(), // tRPC viaja como string
    vigenciaAnios: z.number().int().positive()
});

const t = initTRPC.context<Context>().create();

export const convenioRouter = t.router({
    create: t.procedure
        .input(createConvenioZod)
        .mutation(async ({ input }) => {
            // 1. Convertir Input Zod -> Effect Schema Entity
            // En una app real, esto es transparente si usamos Effect RPC
            const program = Effect.gen(function* (_) {
                // Lógica de Negocio Pura
                
                // Persistencia
                const inserted = yield* _(
                    Effect.tryPromise(() => db.insert(convenios).values({
                        ...input,
                        id: crypto.randomUUID(),
                        montoTotal: input.montoTotal.toString(), // Drizzle decimal handling
                        fechaFirma: new Date(input.fechaFirma),
                        createdAt: new Date(),
                        updatedAt: new Date(),
                        estado: 'BORRADOR'
                    }).returning())
                );
                
                return inserted[0];
            });

            return Effect.runPromise(program);
        }),

    list: t.procedure.query(async () => {
        return await db.select().from(convenios);
    })
});
