import { z } from 'zod';
import { db } from './db';
import { logs } from './schema';
import { convenioRouter } from './domain/d_fin/router';
import { iprRouter } from './domain/d_fin/ipr/router';
import { crisisRouter } from './domain/d_eje/crisis/router';
import { problemaRouter } from './domain/d_eje/problema/router';
import { compromisoRouter } from './domain/d_conv/compromiso/router';
import { alertaRouter } from './domain/d_sal/alerta/router';
import { reunionRouter } from './domain/d_conv/reunion/router';
import { t, publicProcedure, protectedProcedure } from './trpc-init';

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
    
  // Domain Routers
  convenio: convenioRouter,
  ipr: iprRouter,
  crisis: crisisRouter,
  
  // M2 Crisis Management
  problema: problemaRouter,
  compromiso: compromisoRouter,
  alerta: alertaRouter,
  
  // M3 Reuniones
  reunion: reunionRouter,
});

export type AppRouter = typeof appRouter;

