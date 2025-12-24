import { z } from 'zod';
import { eq, desc } from 'drizzle-orm';
import { db } from '../../../db';
import { finipr } from '../../../db/schema/fin';
import { loccomuna } from '../../../db/schema/loc';
import { t, protectedProcedure, publicProcedure } from '../../../trpc-init';

// Input Validation Schemas
const createIPRSchema = z.object({
  nombre: z.string().min(5),
  codigoBip: z.string().optional(), // Puede ser null/undefined al inicio
  fondoId: z.string(),
  viaEvaluacionId: z.string().optional(),
  montoTotal: z.number().int().nonnegative(),
  comunaId: z.string().uuid(),
  // Defaults handled in logic usually, but here specific inputs
  estadoCiclo: z.enum(['IDEA', 'PERFIL', 'DISEÑO', 'EJECUCION', 'CIERRE']).default('IDEA'),
  etapaActual: z.enum(['PREINVERSION', 'SOLICITUD_RS', 'LICITACION', 'CONTRATO', 'RECEPCION']).default('PREINVERSION'),
  fechaPostulacion: z.string().datetime(), // ISO String
});

export const iprRouter = t.router({
  create: protectedProcedure
    .input(createIPRSchema)
    .mutation(async ({ input, ctx }) => {
      // Logic: Insert into DB
      // TODO: In a real scenario, use Effect to map Domain Entity -> DB Row
      // Here we map directly to legacy table columns
      
      const [inserted] = await db.insert(finipr).values({
        codigo_bip: input.codigoBip || 'PENDIENTE', // DB constraint is NOT NULL, so fallback
        nombre: input.nombre,
        descripcion: input.nombre, // Reusing name as desc for now
        tipo: 'IPR', // Default type
        mecanismo_id: '2247ba9e-8854-5ae8-8ed8-072115492ad9', // TODO: Resolve real mechanism ID (FNDR default?)
        monto_total: input.montoTotal.toString(),
        comuna_id: input.comunaId,
        estado_ciclo: input.estadoCiclo,
        etapa_actual: input.etapaActual,
        fecha_rs: input.fechaPostulacion, // Mapping postulation date to RS date for legacy compat (fallback)
        // Additional legacy fields defaults
      }).returning();
      
      return inserted;
    }),

  list: publicProcedure
    .query(async () => {
      // JOIN con loc_comuna para obtener nombre
      const results = await db
        .select({
          id_ipr: finipr.id_ipr,
          codigo_bip: finipr.codigo_bip,
          nombre: finipr.nombre,
          monto_total: finipr.monto_total,
          comuna_id: finipr.comuna_id,
          comuna_nombre: loccomuna.nombre,
          estado_ciclo: finipr.estado_ciclo,
          etapa_actual: finipr.etapa_actual,
          fecha_rs: finipr.fecha_rs,
        })
        .from(finipr)
        .leftJoin(loccomuna, eq(finipr.comuna_id, loccomuna.id_comuna))
        .orderBy(desc(finipr.fecha_rs));
      return results;
    }),

  getById: publicProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ input }) => {
      const [result] = await db.select().from(finipr).where(eq(finipr.id_ipr, input.id));
      return result;
    }),
});
