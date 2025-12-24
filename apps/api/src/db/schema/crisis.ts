// =============================================================================
// apps/api/src/db/schema/crisis.ts — Crisis Management Tables (Drizzle ORM)
// Replicated from para_titi/app/models/crisis.py
// =============================================================================

import { pgTable, pgSchema, uuid, text, boolean, integer, timestamp, date, jsonb } from 'drizzle-orm/pg-core';

// Schema references
const goreEjecucion = pgSchema('gore_ejecucion');

// =============================================================================
// ENUMS (as text with constraints - Drizzle doesn't auto-create PG enums)
// =============================================================================

// tipo_problema_ipr: TECNICO, FINANCIERO, ADMINISTRATIVO, LEGAL, COORDINACION, EXTERNO
// impacto_problema_ipr: BLOQUEA_PAGO, RETRASA_OBRA, RETRASA_CONVENIO, RIESGO_RENDICION, OTRO
// estado_problema_ipr: ABIERTO, EN_GESTION, RESUELTO, CERRADO_SIN_RESOLVER
// prioridad_compromiso: BAJA, MEDIA, ALTA, URGENTE
// estado_compromiso: PENDIENTE, EN_PROGRESO, COMPLETADO, VERIFICADO, CANCELADO
// nivel_alerta_ipr: INFO, ATENCION, ALTO, CRITICO

// =============================================================================
// tipo_compromiso_operativo — Catalog of commitment types
// =============================================================================
export const tipoCompromisoOperativo = goreEjecucion.table('tipo_compromiso_operativo', {
  id: uuid('id').primaryKey().defaultRandom(),
  codigo: text('codigo').notNull().unique(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion'),
  requiere_vinculo_ipr: boolean('requiere_vinculo_ipr').default(true),
  dias_default: integer('dias_default').default(7),
  activo: boolean('activo').default(true),
  created_at: timestamp('created_at').defaultNow(),
});

// =============================================================================
// problema_ipr — Issues/problems detected in IPRs
// =============================================================================
export const problemaIpr = goreEjecucion.table('problema_ipr', {
  id: uuid('id').primaryKey().defaultRandom(),
  iniciativa_id: uuid('iniciativa_id').notNull(), // FK to gore_inversion.iniciativa
  convenio_id: uuid('convenio_id'), // FK to gore_financiero.convenio
  tipo: text('tipo').notNull(), // ENUM: TECNICO, FINANCIERO, etc.
  impacto: text('impacto').notNull(), // ENUM: BLOQUEA_PAGO, etc.
  descripcion: text('descripcion').notNull(),
  impacto_descripcion: text('impacto_descripcion'),
  detectado_por_id: uuid('detectado_por_id').notNull(), // FK to usuario
  detectado_en: timestamp('detectado_en').defaultNow(),
  estado: text('estado').default('ABIERTO'), // ENUM
  solucion_propuesta: text('solucion_propuesta'),
  solucion_aplicada: text('solucion_aplicada'),
  resuelto_por_id: uuid('resuelto_por_id'), // FK to usuario
  resuelto_en: timestamp('resuelto_en'),
  created_at: timestamp('created_at').defaultNow(),
  updated_at: timestamp('updated_at').defaultNow(),
});

// =============================================================================
// compromiso_operativo — Operational commitments
// =============================================================================
export const compromisoOperativo = goreEjecucion.table('compromiso_operativo', {
  id: uuid('id').primaryKey().defaultRandom(),
  
  // Origin links
  instancia_id: uuid('instancia_id'), // FK to instancia_colectiva
  problema_id: uuid('problema_id'), // FK to problema_ipr
  
  // IPR links (derived by trigger)
  cuota_id: uuid('cuota_id'), // FK to cuota
  convenio_id: uuid('convenio_id'), // FK to convenio
  iniciativa_id: uuid('iniciativa_id'), // FK to iniciativa
  
  // Type and description
  tipo_id: uuid('tipo_id').notNull(), // FK to tipo_compromiso_operativo
  descripcion: text('descripcion').notNull(),
  
  // Assignment
  responsable_id: uuid('responsable_id').notNull(), // FK to usuario
  division_id: uuid('division_id'), // FK to division
  
  // Deadlines and state
  fecha_limite: date('fecha_limite').notNull(),
  prioridad: text('prioridad').default('MEDIA'), // BAJA, MEDIA, ALTA, URGENTE
  estado: text('estado').default('PENDIENTE'), // PENDIENTE, EN_PROGRESO, COMPLETADO, VERIFICADO, CANCELADO
  observaciones: text('observaciones'),
  completado_en: timestamp('completado_en'),
  
  // Verification
  verificado_por_id: uuid('verificado_por_id'), // FK to usuario
  verificado_en: timestamp('verificado_en'),
  
  // Audit
  creado_por_id: uuid('creado_por_id').notNull(), // FK to usuario
  created_at: timestamp('created_at').defaultNow(),
  updated_at: timestamp('updated_at').defaultNow(),
});

// =============================================================================
// historial_compromiso — Event sourcing for commitment state changes
// =============================================================================
export const historialCompromiso = goreEjecucion.table('historial_compromiso', {
  id: uuid('id').primaryKey().defaultRandom(),
  compromiso_id: uuid('compromiso_id').notNull(), // FK to compromiso_operativo
  estado_anterior: text('estado_anterior'),
  estado_nuevo: text('estado_nuevo').notNull(),
  usuario_id: uuid('usuario_id').notNull(), // FK to usuario
  comentario: text('comentario'),
  created_at: timestamp('created_at').defaultNow(),
});

// =============================================================================
// alerta_ipr — Automatic alerts
// =============================================================================
export const alertaIpr = goreEjecucion.table('alerta_ipr', {
  id: uuid('id').primaryKey().defaultRandom(),
  target_tipo: text('target_tipo').notNull(), // INICIATIVA, CONVENIO, CUOTA, COMPROMISO, PROBLEMA
  target_id: uuid('target_id').notNull(),
  iniciativa_id: uuid('iniciativa_id').notNull(), // FK to iniciativa
  tipo: text('tipo').notNull(), // Alert type (OBRA_TERMINADA_SIN_PAGO, CUOTA_VENCIDA, etc.)
  nivel: text('nivel').notNull(), // INFO, ATENCION, ALTO, CRITICO
  mensaje: text('mensaje').notNull(),
  datos_contexto: jsonb('datos_contexto'), // JSON context data
  activa: boolean('activa').default(true),
  atendida_por_id: uuid('atendida_por_id'), // FK to usuario
  atendida_en: timestamp('atendida_en'),
  accion_tomada: text('accion_tomada'),
  generada_en: timestamp('generada_en').defaultNow(),
  created_at: timestamp('created_at').defaultNow(),
});
