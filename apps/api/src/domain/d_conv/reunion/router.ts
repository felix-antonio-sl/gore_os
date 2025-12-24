import { z } from 'zod';
import { eq, desc, and, sql } from 'drizzle-orm';
import { db } from '../../../db';
import { convsesion, convpuntotabla, convcompromiso } from '../../../db/schema/conv';
import { finipr } from '../../../db/schema/fin';
import { t, protectedProcedure, publicProcedure } from '../../../trpc-init';

// Schemas
const createSesionSchema = z.object({
  instanciaId: z.string().uuid().optional(),
  tipo: z.enum(['ORDINARIA', 'EXTRAORDINARIA', 'CRISIS']),
  fecha: z.string().datetime(),
  lugar: z.string().optional(),
  modalidad: z.enum(['PRESENCIAL', 'REMOTA', 'HIBRIDA']).default('PRESENCIAL'),
});

const createPuntoTablaSchema = z.object({
  sesionId: z.string().uuid(),
  numero: z.number().int().positive(),
  tipo: z.enum(['INFORMATIVO', 'RESOLUTIVO', 'OTROS']),
  materia: z.string().min(3),
  iprId: z.string().uuid().optional(),
  problemaId: z.string().uuid().optional(),
});

export const reunionRouter = t.router({
  // List upcoming and recent sessions
  list: publicProcedure
    .query(async () => {
      const results = await db
        .select()
        .from(convsesion)
        .orderBy(desc(convsesion.fecha))
        .limit(20);
      return results;
    }),

  // Get session by ID with puntos
  getById: publicProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ input }) => {
      const [sesion] = await db
        .select()
        .from(convsesion)
        .where(eq(convsesion.id_sesion, input.id));
      
      if (!sesion) return null;

      const puntos = await db
        .select({
          id_punto: convpuntotabla.id_punto,
          sesion_id: convpuntotabla.sesion_id,
          numero: convpuntotabla.numero,
          tipo: convpuntotabla.tipo,
          materia: convpuntotabla.materia,
        })
        .from(convpuntotabla)
        .where(eq(convpuntotabla.sesion_id, input.id))
        .orderBy(convpuntotabla.numero);

      const compromisos = await db
        .select()
        .from(convcompromiso)
        .where(eq(convcompromiso.sesion_id, input.id));

      return { ...sesion, puntos, compromisos };
    }),

  // Create new session
  create: protectedProcedure
    .input(createSesionSchema)
    .mutation(async ({ input, ctx }) => {
      // Get next session number
      const [lastSesion] = await db
        .select({ numero: sql<number>`MAX(numero)` })
        .from(convsesion);
      const nextNumero = (lastSesion?.numero || 0) + 1;

      const [inserted] = await db.insert(convsesion).values({
        instancia_id: input.instanciaId || '00000000-0000-0000-0000-000000000000',
        numero: nextNumero,
        tipo_sesion: input.tipo,
        fecha: new Date(input.fecha),
        lugar: input.lugar || 'Sala GORE',
        modalidad: input.modalidad,
        estado: 'PROGRAMADA',
        quorum_requerido: 3,
        quorum_presente: 0,
      }).returning();
      
      return inserted;
    }),

  // Start session (set EN_CURSO)
  start: protectedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .mutation(async ({ input }) => {
      const [updated] = await db
        .update(convsesion)
        .set({ estado: 'EN_CURSO' })
        .where(eq(convsesion.id_sesion, input.id))
        .returning();
      return updated;
    }),

  // End session (set FINALIZADA)
  end: protectedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .mutation(async ({ input }) => {
      const [updated] = await db
        .update(convsesion)
        .set({ estado: 'FINALIZADA' })
        .where(eq(convsesion.id_sesion, input.id))
        .returning();
      return updated;
    }),

  // Add punto to session
  addPunto: protectedProcedure
    .input(createPuntoTablaSchema)
    .mutation(async ({ input }) => {
      const [inserted] = await db.insert(convpuntotabla).values({
        sesion_id: input.sesionId,
        numero: input.numero,
        tipo: input.tipo,
        materia: input.materia,
        // TODO: Add IPR/Problema links when schema supports it
      }).returning();
      
      return inserted;
    }),

  // Session stats
  getStats: publicProcedure
    .query(async () => {
      const total = await db.select({ count: sql<number>`count(*)` }).from(convsesion);
      const enCurso = await db.select({ count: sql<number>`count(*)` }).from(convsesion).where(eq(convsesion.estado, 'EN_CURSO'));
      const programadas = await db.select({ count: sql<number>`count(*)` }).from(convsesion).where(eq(convsesion.estado, 'PROGRAMADA'));
      
      return {
        total: total[0]?.count || 0,
        enCurso: enCurso[0]?.count || 0,
        programadas: programadas[0]?.count || 0,
      };
    }),
});
