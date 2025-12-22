import { initTRPC, TRPCError } from '@trpc/server';
import { z } from 'zod';
import { db } from './db';
import { logs } from './schema';
import type { AuthPayload } from './auth';

// Context type for tRPC
export interface Context {
  user: AuthPayload | null;
}

const t = initTRPC.context<Context>().create();

// Public procedure (no auth required)
const publicProcedure = t.procedure;

// Protected procedure (auth required)
const protectedProcedure = t.procedure.use(async ({ ctx, next }) => {
  if (!ctx.user) {
    throw new TRPCError({ 
      code: 'UNAUTHORIZED',
      message: 'Debes iniciar sesión para realizar esta acción',
    });
  }
  return next({
    ctx: {
      user: ctx.user,
    },
  });
});

export const appRouter = t.router({
  // Public: Anyone can read logs
  getLogs: publicProcedure.query(async () => {
    return await db.query.logs.findMany({
      orderBy: (logs, { desc }) => [desc(logs.createdAt)],
    });
  }),
  
  // Protected: Only authenticated users can add logs
  addLog: protectedProcedure
    .input(z.object({ message: z.string().min(1) }))
    .mutation(async ({ input, ctx }) => {
      const result = await db.insert(logs).values({
        message: `[${ctx.user.preferred_username || 'anon'}] ${input.message}`,
      }).returning();
      return result[0];
    }),
});

export type AppRouter = typeof appRouter;
