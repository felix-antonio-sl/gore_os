import { z } from 'zod';
import { eq, desc, and, sql } from 'drizzle-orm';
import { db } from '../../../db';
import { salalerta } from '../../../db/schema/sal';
import { finipr } from '../../../db/schema/fin';
import { t, protectedProcedure, publicProcedure } from '../../../trpc-init';

// Schemas
const createAlertaSchema = z.object({
  iprId: z.string().uuid().optional(),
  convenioId: z.string().uuid().optional(),
  tipo: z.enum(['VENCIMIENTO', 'CUOTA_PENDIENTE', 'OBRA_SIN_PAGO', 'COMPROMISO_VENCIDO', 'RENDICION', 'OTRO']),
  nivel: z.enum(['INFO', 'ATENCION', 'ALTO', 'CRITICO']),
  mensaje: z.string(),
  reglaOrigen: z.string().optional(),
});

export const alertaRouter = t.router({
  // List active alerts
  list: publicProcedure
    .query(async () => {
      const results = await db
        .select({
          id_alerta: salalerta.id_alerta,
          ipr_id: salalerta.ipr_id,
          ipr_nombre: finipr.nombre,
          ipr_codigo: finipr.codigo_bip,
          convenio_id: salalerta.convenio_id,
          tipo: salalerta.tipo,
          nivel: salalerta.nivel,
          mensaje: salalerta.mensaje,
          activa: salalerta.activa,
          fecha_generacion: salalerta.fecha_generacion,
        })
        .from(salalerta)
        .leftJoin(finipr, eq(salalerta.ipr_id, finipr.id_ipr))
        .where(eq(salalerta.activa, true))
        .orderBy(desc(salalerta.fecha_generacion));
      return results;
    }),

  // Get critical alerts for dashboard
  getCriticas: publicProcedure
    .query(async () => {
      const results = await db
        .select({
          id_alerta: salalerta.id_alerta,
          ipr_id: salalerta.ipr_id,
          ipr_nombre: finipr.nombre,
          tipo: salalerta.tipo,
          nivel: salalerta.nivel,
          mensaje: salalerta.mensaje,
        })
        .from(salalerta)
        .leftJoin(finipr, eq(salalerta.ipr_id, finipr.id_ipr))
        .where(and(
          eq(salalerta.activa, true),
          eq(salalerta.nivel, 'CRITICO')
        ))
        .orderBy(desc(salalerta.fecha_generacion));
      return results;
    }),

  // Get alerts by IPR
  getByIPR: publicProcedure
    .input(z.object({ iprId: z.string().uuid() }))
    .query(async ({ input }) => {
      const results = await db
        .select()
        .from(salalerta)
        .where(eq(salalerta.ipr_id, input.iprId))
        .orderBy(desc(salalerta.fecha_generacion));
      return results;
    }),

  // Create alert (manual or from rule engine)
  create: protectedProcedure
    .input(createAlertaSchema)
    .mutation(async ({ input }) => {
      const [inserted] = await db.insert(salalerta).values({
        ipr_id: input.iprId || null,
        convenio_id: input.convenioId || null,
        tipo: input.tipo,
        nivel: input.nivel,
        mensaje: input.mensaje,
        regla_origen: input.reglaOrigen || 'MANUAL',
        activa: true,
        fecha_generacion: new Date().toISOString(),
      }).returning();
      
      return inserted;
    }),

  // Dismiss alert
  dismiss: protectedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .mutation(async ({ input, ctx }) => {
      const [updated] = await db
        .update(salalerta)
        .set({
          activa: false,
          atendida_por_id: ctx.user?.sub || null,
          fecha_atencion: new Date().toISOString(),
        })
        .where(eq(salalerta.id_alerta, input.id))
        .returning();
      
      return updated;
    }),

  // Stats for dashboard
  getStats: publicProcedure
    .query(async () => {
      const activas = await db.select({ count: sql<number>`count(*)` }).from(salalerta).where(eq(salalerta.activa, true));
      const criticas = await db.select({ count: sql<number>`count(*)` }).from(salalerta).where(and(eq(salalerta.activa, true), eq(salalerta.nivel, 'CRITICO')));
      
      return {
        activas: activas[0]?.count || 0,
        criticas: criticas[0]?.count || 0,
      };
    }),
});
