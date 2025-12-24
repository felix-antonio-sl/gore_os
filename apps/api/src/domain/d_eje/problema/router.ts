import { z } from 'zod';
import { eq, desc, and, lt, isNull, sql } from 'drizzle-orm';
import { db } from '../../../db';
import { ejeproblema } from '../../../db/schema/eje';
import { finipr } from '../../../db/schema/fin';
import { t, protectedProcedure, publicProcedure } from '../../../trpc-init';

// Schemas
const createProblemaSchema = z.object({
  iprId: z.string().uuid(),
  convenioId: z.string().uuid().optional(),
  tipo: z.enum(['TECNICO', 'FINANCIERO', 'ADMINISTRATIVO', 'LEGAL', 'OTRO']),
  impacto: z.enum(['BAJO', 'MEDIO', 'ALTO', 'CRITICO']),
  descripcion: z.string().min(10),
  solucionPropuesta: z.string().optional(),
});

const updateProblemaSchema = z.object({
  id: z.string().uuid(),
  estado: z.enum(['ABIERTO', 'EN_GESTION', 'RESUELTO', 'CERRADO']).optional(),
  solucionPropuesta: z.string().optional(),
  fechaResolucion: z.string().datetime().optional(),
});

export const problemaRouter = t.router({
  // List all problems with IPR info
  list: publicProcedure
    .query(async () => {
      const results = await db
        .select({
          id_problema: ejeproblema.id_problema,
          ipr_id: ejeproblema.ipr_id,
          ipr_nombre: finipr.nombre,
          ipr_codigo: finipr.codigo_bip,
          convenio_id: ejeproblema.convenio_id,
          tipo: ejeproblema.tipo,
          impacto: ejeproblema.impacto,
          descripcion: ejeproblema.descripcion,
          estado: ejeproblema.estado,
          fecha_registro: ejeproblema.fecha_registro,
          solucion_propuesta: ejeproblema.solucion_propuesta,
        })
        .from(ejeproblema)
        .leftJoin(finipr, eq(ejeproblema.ipr_id, finipr.id_ipr))
        .orderBy(desc(ejeproblema.fecha_registro));
      return results;
    }),

  // Get problems for specific IPR
  getByIPR: publicProcedure
    .input(z.object({ iprId: z.string().uuid() }))
    .query(async ({ input }) => {
      const results = await db
        .select()
        .from(ejeproblema)
        .where(eq(ejeproblema.ipr_id, input.iprId))
        .orderBy(desc(ejeproblema.fecha_registro));
      return results;
    }),

  // Get open problems (for dashboard)
  getAbiertos: publicProcedure
    .query(async () => {
      const results = await db
        .select({
          id_problema: ejeproblema.id_problema,
          ipr_id: ejeproblema.ipr_id,
          ipr_nombre: finipr.nombre,
          tipo: ejeproblema.tipo,
          impacto: ejeproblema.impacto,
          descripcion: ejeproblema.descripcion,
          fecha_registro: ejeproblema.fecha_registro,
        })
        .from(ejeproblema)
        .leftJoin(finipr, eq(ejeproblema.ipr_id, finipr.id_ipr))
        .where(eq(ejeproblema.estado, 'ABIERTO'))
        .orderBy(desc(ejeproblema.fecha_registro));
      return results;
    }),

  // Create new problem
  create: protectedProcedure
    .input(createProblemaSchema)
    .mutation(async ({ input, ctx }) => {
      const [inserted] = await db.insert(ejeproblema).values({
        ipr_id: input.iprId,
        convenio_id: input.convenioId || null,
        tipo: input.tipo,
        impacto: input.impacto,
        descripcion: input.descripcion,
        estado: 'ABIERTO',
        solucion_propuesta: input.solucionPropuesta || null,
        fecha_registro: new Date().toISOString(),
        // detectado_por_id: ctx.user?.sub, // TODO: link to user
      }).returning();
      
      return inserted;
    }),

  // Update problem
  update: protectedProcedure
    .input(updateProblemaSchema)
    .mutation(async ({ input }) => {
      const updateData: Record<string, unknown> = {};
      if (input.estado) updateData.estado = input.estado;
      if (input.solucionPropuesta) updateData.solucion_propuesta = input.solucionPropuesta;
      if (input.fechaResolucion) updateData.fecha_resolucion = input.fechaResolucion;

      const [updated] = await db
        .update(ejeproblema)
        .set(updateData)
        .where(eq(ejeproblema.id_problema, input.id))
        .returning();
      
      return updated;
    }),

  // Stats for dashboard
  getStats: publicProcedure
    .query(async () => {
      const total = await db.select({ count: sql<number>`count(*)` }).from(ejeproblema);
      const abiertos = await db.select({ count: sql<number>`count(*)` }).from(ejeproblema).where(eq(ejeproblema.estado, 'ABIERTO'));
      const criticos = await db.select({ count: sql<number>`count(*)` }).from(ejeproblema).where(and(eq(ejeproblema.estado, 'ABIERTO'), eq(ejeproblema.impacto, 'CRITICO')));
      
      return {
        total: total[0]?.count || 0,
        abiertos: abiertos[0]?.count || 0,
        criticos: criticos[0]?.count || 0,
      };
    }),
});
