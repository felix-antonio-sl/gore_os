// GORE_OS Drizzle Schema - Domain: D-NORM
// Auto-generated: 2025-12-23T07:04:05.105224
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// estado,
export const normaudiencialobby = pgTable('norm_audiencia_lobby', {
  id_audiencia: uuid('id_audiencia').primaryKey().defaultRandom(),
  fecha_solicitud: timestamp('fecha_solicitud').notNull(),
  fecha_audiencia: timestamp('fecha_audiencia'),
  solicitante_nombre: text('solicitante_nombre').notNull(),
});
