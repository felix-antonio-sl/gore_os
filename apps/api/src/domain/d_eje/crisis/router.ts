import { z } from 'zod';
import { t, publicProcedure, protectedProcedure } from '../../../trpc-init';
import { db } from '../../../db';
import { problemaIpr, compromisoOperativo, alertaIpr, historialCompromiso, tipoCompromisoOperativo } from '../../../db/schema/crisis';
import { finipr } from '../../../db/schema/fin';
import { desc, eq, and, or, lt, sql } from 'drizzle-orm';

const router = t.router;

// =============================================================================
// Input Schemas
// =============================================================================

const CreateProblemaInput = z.object({
  iniciativa_id: z.string().uuid(),
  convenio_id: z.string().uuid().optional(),
  tipo: z.enum(['TECNICO', 'FINANCIERO', 'ADMINISTRATIVO', 'LEGAL', 'COORDINACION', 'EXTERNO']),
  impacto: z.enum(['BLOQUEA_PAGO', 'RETRASA_OBRA', 'RETRASA_CONVENIO', 'RIESGO_RENDICION', 'OTRO']),
  descripcion: z.string().min(10),
  impacto_descripcion: z.string().optional(),
  solucion_propuesta: z.string().optional(),
});

const CreateCompromisoInput = z.object({
  iniciativa_id: z.string().uuid().optional(),
  convenio_id: z.string().uuid().optional(),
  problema_id: z.string().uuid().optional(),
  instancia_id: z.string().uuid().optional(),
  tipo_id: z.string().uuid(),
  descripcion: z.string().min(5),
  responsable_id: z.string().uuid(),
  fecha_limite: z.string(), // ISO date string
  prioridad: z.enum(['BAJA', 'MEDIA', 'ALTA', 'URGENTE']).default('MEDIA'),
});

// =============================================================================
// Crisis Router
// =============================================================================

export const crisisRouter = router({
  // ---------------------------------------------------------------------------
  // STATS - Dashboard statistics with IPR portfolio data
  // ---------------------------------------------------------------------------
  stats: publicProcedure.query(async () => {
    const today = new Date().toISOString().split('T')[0];
    
    // Count problems by state
    const problemasAbiertos = await db
      .select({ count: sql<number>`count(*)` })
      .from(problemaIpr)
      .where(or(eq(problemaIpr.estado, 'ABIERTO'), eq(problemaIpr.estado, 'EN_GESTION')));
    
    // Count commitments by state
    const compromisosPendientes = await db
      .select({ count: sql<number>`count(*)` })
      .from(compromisoOperativo)
      .where(or(eq(compromisoOperativo.estado, 'PENDIENTE'), eq(compromisoOperativo.estado, 'EN_PROGRESO')));
    
    // Count overdue commitments
    const compromisosVencidos = await db
      .select({ count: sql<number>`count(*)` })
      .from(compromisoOperativo)
      .where(and(
        or(eq(compromisoOperativo.estado, 'PENDIENTE'), eq(compromisoOperativo.estado, 'EN_PROGRESO')),
        lt(compromisoOperativo.fecha_limite, today)
      ));
    
    // Count active alerts
    const alertasActivas = await db
      .select({ count: sql<number>`count(*)` })
      .from(alertaIpr)
      .where(eq(alertaIpr.activa, true));

    // IPR Portfolio stats
    const iprPortfolio = await db
      .select({ 
        total: sql<number>`count(*)`,
        monto_total: sql<number>`sum(monto_total)`,
        en_ejecucion: sql<number>`count(*) filter (where etapa_actual = 'EJECUCIÓN')`,
        en_formulacion: sql<number>`count(*) filter (where etapa_actual = 'FORMULACIÓN' or etapa_actual = 'FORMULACION')`,
      })
      .from(finipr);

    return {
      problemas_abiertos: Number(problemasAbiertos[0]?.count || 0),
      compromisos_pendientes: Number(compromisosPendientes[0]?.count || 0),
      compromisos_vencidos: Number(compromisosVencidos[0]?.count || 0),
      alertas_activas: Number(alertasActivas[0]?.count || 0),
      // IPR Portfolio
      ipr_total: Number(iprPortfolio[0]?.total || 0),
      ipr_monto_total: Number(iprPortfolio[0]?.monto_total || 0),
      ipr_en_ejecucion: Number(iprPortfolio[0]?.en_ejecucion || 0),
      ipr_en_formulacion: Number(iprPortfolio[0]?.en_formulacion || 0),
    };
  }),

  // ---------------------------------------------------------------------------
  // PROBLEMAS - Issue management
  // ---------------------------------------------------------------------------
  problema: router({
    list: publicProcedure.query(async () => {
      return await db.select().from(problemaIpr).orderBy(desc(problemaIpr.detectado_en));
    }),

    create: protectedProcedure
      .input(CreateProblemaInput)
      .mutation(async ({ input, ctx }) => {
        const [created] = await db.insert(problemaIpr).values({
          ...input,
          detectado_por_id: ctx.user.id,
        }).returning();
        return created;
      }),

    resolve: protectedProcedure
      .input(z.object({
        id: z.string().uuid(),
        solucion_aplicada: z.string().min(5),
      }))
      .mutation(async ({ input, ctx }) => {
        const [updated] = await db.update(problemaIpr)
          .set({
            estado: 'RESUELTO',
            solucion_aplicada: input.solucion_aplicada,
            resuelto_por_id: ctx.user.id,
            resuelto_en: new Date(),
            updated_at: new Date(),
          })
          .where(eq(problemaIpr.id, input.id))
          .returning();
        return updated;
      }),
  }),

  // ---------------------------------------------------------------------------
  // COMPROMISOS - Commitment management
  // ---------------------------------------------------------------------------
  compromiso: router({
    list: publicProcedure
      .input(z.object({
        estado: z.enum(['PENDIENTE', 'EN_PROGRESO', 'COMPLETADO', 'VERIFICADO', 'CANCELADO']).optional(),
      }).optional())
      .query(async ({ input }) => {
        if (input?.estado) {
          return await db.select().from(compromisoOperativo)
            .where(eq(compromisoOperativo.estado, input.estado))
            .orderBy(compromisoOperativo.fecha_limite);
        }
        return await db.select().from(compromisoOperativo).orderBy(compromisoOperativo.fecha_limite);
      }),

    create: protectedProcedure
      .input(CreateCompromisoInput)
      .mutation(async ({ input, ctx }) => {
        const [created] = await db.insert(compromisoOperativo).values({
          ...input,
          creado_por_id: ctx.user.id,
        }).returning();
        
        // Record history
        await db.insert(historialCompromiso).values({
          compromiso_id: created.id,
          estado_anterior: null,
          estado_nuevo: 'PENDIENTE',
          usuario_id: ctx.user.id,
          comentario: 'Compromiso creado',
        });
        
        return created;
      }),

    complete: protectedProcedure
      .input(z.object({
        id: z.string().uuid(),
        observaciones: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // Get current state
        const [current] = await db.select().from(compromisoOperativo).where(eq(compromisoOperativo.id, input.id));
        
        const [updated] = await db.update(compromisoOperativo)
          .set({
            estado: 'COMPLETADO',
            observaciones: input.observaciones,
            completado_en: new Date(),
            updated_at: new Date(),
          })
          .where(eq(compromisoOperativo.id, input.id))
          .returning();
        
        // Record history
        await db.insert(historialCompromiso).values({
          compromiso_id: input.id,
          estado_anterior: current?.estado || null,
          estado_nuevo: 'COMPLETADO',
          usuario_id: ctx.user.id,
          comentario: input.observaciones || 'Marcado como completado',
        });
        
        return updated;
      }),

    verify: protectedProcedure
      .input(z.object({
        id: z.string().uuid(),
        comentario: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const [current] = await db.select().from(compromisoOperativo).where(eq(compromisoOperativo.id, input.id));
        
        const [updated] = await db.update(compromisoOperativo)
          .set({
            estado: 'VERIFICADO',
            verificado_por_id: ctx.user.id,
            verificado_en: new Date(),
            updated_at: new Date(),
          })
          .where(eq(compromisoOperativo.id, input.id))
          .returning();
        
        // Record history
        await db.insert(historialCompromiso).values({
          compromiso_id: input.id,
          estado_anterior: current?.estado || null,
          estado_nuevo: 'VERIFICADO',
          usuario_id: ctx.user.id,
          comentario: input.comentario || 'Verificado',
        });
        
        return updated;
      }),

    tipos: publicProcedure.query(async () => {
      return await db.select().from(tipoCompromisoOperativo).where(eq(tipoCompromisoOperativo.activo, true));
    }),
  }),

  // ---------------------------------------------------------------------------
  // ALERTAS - Alert management
  // ---------------------------------------------------------------------------
  alerta: router({
    list: publicProcedure
      .input(z.object({
        activas: z.boolean().default(true),
        nivel: z.enum(['INFO', 'ATENCION', 'ALTO', 'CRITICO']).optional(),
      }).optional())
      .query(async ({ input }) => {
        const filters = [];
        if (input?.activas !== undefined) {
          filters.push(eq(alertaIpr.activa, input.activas));
        }
        if (input?.nivel) {
          filters.push(eq(alertaIpr.nivel, input.nivel));
        }
        
        if (filters.length > 0) {
          return await db.select().from(alertaIpr)
            .where(and(...filters))
            .orderBy(desc(alertaIpr.generada_en));
        }
        return await db.select().from(alertaIpr).orderBy(desc(alertaIpr.generada_en));
      }),

    attend: protectedProcedure
      .input(z.object({
        id: z.string().uuid(),
        accion_tomada: z.string().min(5),
      }))
      .mutation(async ({ input, ctx }) => {
        const [updated] = await db.update(alertaIpr)
          .set({
            activa: false,
            atendida_por_id: ctx.user.id,
            atendida_en: new Date(),
            accion_tomada: input.accion_tomada,
          })
          .where(eq(alertaIpr.id, input.id))
          .returning();
        return updated;
      }),
  }),
});
