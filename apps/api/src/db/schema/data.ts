// GORE_OS Drizzle Schema - Domain: D-DATA
// Auto-generated: 2025-12-23T10:39:16.558371
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// ley_aplicable,
export const dataactivo = pgTable('data_activo', {
  id_activo: uuid('id_activo').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
});
