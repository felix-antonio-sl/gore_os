import { z } from 'zod';
import { eq, desc, and, lt, sql } from 'drizzle-orm';
import { db } from '../../../db';
import { convcompromiso } from '../../../db/schema/conv';
import { ejeproblema } from '../../../db/schema/eje';
import { finipr } from '../../../db/schema/fin';
import { t, protectedProcedure, publicProcedure } from '../../../trpc-init';

// Schemas
const createCompromisoSchema = z.object({
  problemaId: z.string().uuid().optional(),
  iprId: z.string().uuid().optional(),
  sesionId: z.string().uuid().optional(),
  tipo: z.enum(['GESTION', 'DOCUMENTO', 'REUNION', 'VISITA', 'TRAMITE', 'OTRO']),
  descripcion: z.string().min(5),
  responsableId: z.string().uuid(),
  fechaLimite: z.string(), // Date string
  divisionId: z.string().uuid().optional(),
});

const updateCompromisoSchema = z.object({
  id: z.string().uuid(),
  estado: z.enum(['PENDIENTE', 'EN_PROGRESO', 'COMPLETADO', 'VERIFICADO', 'CANCELADO']).optional(),
  comentario: z.string().optional(),
});

export const compromisoRouter = t.router({
  // List all compromisos with relations
  list: publicProcedure
    .query(async () => {
      const results = await db
        .select({
          id_compromiso: convcompromiso.id_compromiso,
          sesion_id: convcompromiso.sesion_id,
          problema_id: convcompromiso.problema_id,
          ipr_id: convcompromiso.ipr_id,
          ipr_nombre: finipr.nombre,
          tipo: convcompromiso.tipo_gestion,
          descripcion: convcompromiso.descripcion,
          responsable_id: convcompromiso.responsable_id,
          fecha_limite: convcompromiso.fecha_limite,
          estado: convcompromiso.estado,
          verificado: convcompromiso.verificado,
        })
        .from(convcompromiso)
        .leftJoin(finipr, eq(convcompromiso.ipr_id, finipr.id_ipr))
        .orderBy(desc(convcompromiso.fecha_limite));
      return results;
    }),

  // Get overdue compromisos (for crisis dashboard)
  getVencidos: publicProcedure
    .query(async () => {
      const today = new Date().toISOString().split('T')[0];
      const results = await db
        .select({
          id_compromiso: convcompromiso.id_compromiso,
          ipr_id: convcompromiso.ipr_id,
          ipr_nombre: finipr.nombre,
          descripcion: convcompromiso.descripcion,
          fecha_limite: convcompromiso.fecha_limite,
          responsable_id: convcompromiso.responsable_id,
        })
        .from(convcompromiso)
        .leftJoin(finipr, eq(convcompromiso.ipr_id, finipr.id_ipr))
        .where(and(
          lt(convcompromiso.fecha_limite, today),
          eq(convcompromiso.estado, 'PENDIENTE')
        ))
        .orderBy(convcompromiso.fecha_limite);
      return results;
    }),

  // Get my compromisos (for encargado view)
  myCompromisos: protectedProcedure
    .query(async ({ ctx }) => {
      // TODO: filter by ctx.user.sub when user management is complete
      const results = await db
        .select()
        .from(convcompromiso)
        .where(eq(convcompromiso.estado, 'PENDIENTE'))
        .orderBy(convcompromiso.fecha_limite);
      return results;
    }),

  // Get by IPR
  getByIPR: publicProcedure
    .input(z.object({ iprId: z.string().uuid() }))
    .query(async ({ input }) => {
      const results = await db
        .select()
        .from(convcompromiso)
        .where(eq(convcompromiso.ipr_id, input.iprId))
        .orderBy(desc(convcompromiso.fecha_limite));
      return results;
    }),

  // Create new compromiso
  create: protectedProcedure
    .input(createCompromisoSchema)
    .mutation(async ({ input, ctx }) => {
      const [inserted] = await db.insert(convcompromiso).values({
        sesion_id: input.sesionId || null,
        problema_id: input.problemaId || null,
        ipr_id: input.iprId || null,
        tipo_gestion: input.tipo,
        descripcion: input.descripcion,
        responsable_id: input.responsableId,
        fecha_limite: input.fechaLimite,
        estado: 'PENDIENTE',
        verificado: false,
        // division_id: input.divisionId,
      }).returning();
      
      return inserted;
    }),

  // Update compromiso estado
  update: protectedProcedure
    .input(updateCompromisoSchema)
    .mutation(async ({ input }) => {
      const updateData: Record<string, unknown> = {};
      if (input.estado) updateData.estado = input.estado;
      if (input.comentario) updateData.notas = input.comentario;
      if (input.estado === 'COMPLETADO') {
        updateData.fecha_cumplimiento = new Date().toISOString();
      }

      const [updated] = await db
        .update(convcompromiso)
        .set(updateData)
        .where(eq(convcompromiso.id_compromiso, input.id))
        .returning();
      
      return updated;
    }),

  // Verify compromiso (jefe action)
  verify: protectedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .mutation(async ({ input, ctx }) => {
      const [updated] = await db
        .update(convcompromiso)
        .set({
          estado: 'VERIFICADO',
          verificado: true,
          // verificado_por_id: ctx.user?.sub,
          fecha_verificacion: new Date().toISOString(),
        })
        .where(eq(convcompromiso.id_compromiso, input.id))
        .returning();
      
      return updated;
    }),

  // Stats for dashboard
  getStats: publicProcedure
    .query(async () => {
      const today = new Date().toISOString().split('T')[0];
      const total = await db.select({ count: sql<number>`count(*)` }).from(convcompromiso);
      const pendientes = await db.select({ count: sql<number>`count(*)` }).from(convcompromiso).where(eq(convcompromiso.estado, 'PENDIENTE'));
      const vencidos = await db.select({ count: sql<number>`count(*)` }).from(convcompromiso).where(and(lt(convcompromiso.fecha_limite, today), eq(convcompromiso.estado, 'PENDIENTE')));
      
      return {
        total: total[0]?.count || 0,
        pendientes: pendientes[0]?.count || 0,
        vencidos: vencidos[0]?.count || 0,
      };
    }),
});
