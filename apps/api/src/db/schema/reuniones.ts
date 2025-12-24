// =============================================================================
// apps/api/src/db/schema/reuniones.ts — Meetings/Reuniones Tables (Drizzle ORM)
// Replicated from para_titi/app/models/reuniones.py
// =============================================================================

import { pgTable, pgSchema, uuid, text, boolean, integer, timestamp, date, time, jsonb } from 'drizzle-orm/pg-core';

const goreInstancias = pgSchema('gore_instancias');

// =============================================================================
// instancia_colectiva — Collective instances (meetings, sessions)
// =============================================================================
export const instanciaColectiva = goreInstancias.table('instancia_colectiva', {
  id: uuid('id').primaryKey().defaultRandom(),
  tipo: text('tipo').notNull(), // REUNION_JEFATURA, SESION_CORE, COMITE_TECNICO, etc.
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion'),
  fecha: date('fecha').notNull(),
  hora_inicio: time('hora_inicio'),
  hora_fin: time('hora_fin'),
  lugar: text('lugar'),
  modalidad: text('modalidad').default('PRESENCIAL'), // PRESENCIAL, VIRTUAL, HIBRIDO
  estado: text('estado').default('PROGRAMADA'), // PROGRAMADA, EN_CURSO, FINALIZADA, CANCELADA
  
  // Organization
  convocada_por_id: uuid('convocada_por_id').notNull(), // FK to usuario
  division_id: uuid('division_id'), // FK to division
  
  // Metadata
  link_virtual: text('link_virtual'),
  notas: text('notas'),
  
  // Audit
  created_at: timestamp('created_at').defaultNow(),
  updated_at: timestamp('updated_at').defaultNow(),
});

// =============================================================================
// tema_reunion — Agenda items for meetings
// =============================================================================
export const temaReunion = goreInstancias.table('tema_reunion', {
  id: uuid('id').primaryKey().defaultRandom(),
  instancia_id: uuid('instancia_id').notNull(), // FK to instancia_colectiva
  orden: integer('orden').default(1),
  titulo: text('titulo').notNull(),
  descripcion: text('descripcion'),
  duracion_estimada: integer('duracion_estimada'), // minutes
  responsable_id: uuid('responsable_id'), // FK to usuario
  estado: text('estado').default('PENDIENTE'), // PENDIENTE, TRATADO, POSPUESTO
  created_at: timestamp('created_at').defaultNow(),
});

// =============================================================================
// acuerdo — Agreements from meetings (can become compromisos)
// =============================================================================
export const acuerdo = goreInstancias.table('acuerdo', {
  id: uuid('id').primaryKey().defaultRandom(),
  instancia_id: uuid('instancia_id').notNull(), // FK to instancia_colectiva
  tema_id: uuid('tema_id'), // FK to tema_reunion
  
  // Content
  descripcion: text('descripcion').notNull(),
  tipo: text('tipo').default('ACUERDO'), // ACUERDO, TAREA, SOLICITUD, INFORMATIVO
  
  // Assignment
  responsable_id: uuid('responsable_id'), // FK to usuario
  fecha_limite: date('fecha_limite'),
  prioridad: text('prioridad').default('MEDIA'),
  
  // Status
  estado: text('estado').default('PENDIENTE'), // PENDIENTE, EN_PROGRESO, COMPLETADO, CANCELADO
  completado_en: timestamp('completado_en'),
  
  // IPR links (optional)
  iniciativa_id: uuid('iniciativa_id'), // FK to iniciativa
  compromiso_id: uuid('compromiso_id'), // FK if converted to compromiso_operativo
  
  // Audit
  created_at: timestamp('created_at').defaultNow(),
  updated_at: timestamp('updated_at').defaultNow(),
});

// =============================================================================
// minuta_reunion — Meeting minutes
// =============================================================================
export const minutaReunion = goreInstancias.table('minuta_reunion', {
  id: uuid('id').primaryKey().defaultRandom(),
  instancia_id: uuid('instancia_id').notNull().unique(), // FK to instancia_colectiva (one per meeting)
  contenido: text('contenido'), // Markdown/Rich text
  asistentes: jsonb('asistentes'), // Array of user IDs
  ausentes_justificados: jsonb('ausentes_justificados'),
  estado: text('estado').default('BORRADOR'), // BORRADOR, PUBLICADA, APROBADA
  publicada_en: timestamp('publicada_en'),
  aprobada_por_id: uuid('aprobada_por_id'), // FK to usuario
  created_at: timestamp('created_at').defaultNow(),
  updated_at: timestamp('updated_at').defaultNow(),
});
