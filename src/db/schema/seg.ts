// GORE_OS Drizzle Schema - Domain: D-SEG
// Auto-generated: 2025-12-23T07:04:05.105901
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// specs,
export const segdispositivo = pgTable('seg_dispositivo', {
  id_dispositivo: uuid('id_dispositivo').primaryKey().defaultRandom(),
});

// fuente_deteccion,
export const segincidente = pgTable('seg_incidente', {
  id_incidente: uuid('id_incidente').primaryKey().defaultRandom(),
});
