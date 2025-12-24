// GORE_OS Drizzle Schema - Domain: D-GEO
// Auto-generated: 2025-12-23T10:39:16.560194
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// metadatos_iso19115,
export const geocapa = pgTable('geo_capa', {
  id_capa: uuid('id_capa').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
});

// capas,
export const geoservicio = pgTable('geo_servicio', {
  id_servicio: uuid('id_servicio').primaryKey().defaultRandom(),
  tipo: text('tipo').notNull(),
  url_base: text('url_base').notNull(),
  version: text('version').notNull(),
  titulo: text('titulo').notNull(),
});
