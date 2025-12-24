import { initTRPC, TRPCError } from '@trpc/server';
import type { AuthPayload } from './auth';

// Context type for tRPC
export interface Context {
  user: AuthPayload | null;
}

export const t = initTRPC.context<Context>().create();

// Public procedure (no auth required)
export const publicProcedure = t.procedure;

// Protected procedure (auth required)
export const protectedProcedure = t.procedure.use(async ({ ctx, next }) => {
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
