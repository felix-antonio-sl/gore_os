import { pgTable, text, timestamp, uuid, integer, decimal } from 'drizzle-orm/pg-core';

export const convenios = pgTable('d_fin_convenios', {
  id: uuid('id').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  ministerio: text('ministerio').notNull(),
  regionId: uuid('region_id').notNull(),
  montoTotal: decimal('monto_total', { precision: 18, scale: 0 }).notNull(),
  fechaFirma: timestamp('fecha_firma').notNull(),
  vigenciaAnios: integer('vigencia_anios').notNull(),
  // Enum simulado con check constraint en DB real, aquí como text simple por ahora
  estado: text('estado').default('BORRADOR').notNull(), 
  
  // Auditoría
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});
