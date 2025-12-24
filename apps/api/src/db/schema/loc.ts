// GORE_OS Drizzle Schema - Domain: D-LOC
// Auto-generated: 2025-12-23T10:39:16.560856
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// Capa Geoespacial
export const loccapageoespacial = pgTable('loc_capa_geoespacial', {
  id_capa: uuid('id_capa').primaryKey().defaultRandom(),
  region_id: uuid('region_id').notNull(),
  nombre: text('nombre').notNull(),
  tipo: text('tipo').notNull(),
  formato: text('formato').notNull(),
  url_servicio: text('url_servicio').notNull(),
  srid: integer('srid').default('4326'),
});

// Circunscripción Provincial
export const loccircunscripcion = pgTable('loc_circunscripcion', {
  id_circunscripcion: uuid('id_circunscripcion').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  region_id: uuid('region_id').notNull(),
  numero_consejeros: integer('numero_consejeros').notNull(),
  comunas: text('comunas').notNull(),
});

// Comuna
export const loccomuna = pgTable('loc_comuna', {
  id_comuna: uuid('id_comuna').primaryKey().defaultRandom(),
  codigo_ine: text('codigo_ine').notNull(),
  nombre: text('nombre').notNull(),
  provincia_id: uuid('provincia_id').notNull(),
  superficie_km2: numeric('superficie_km2', { precision: 15, scale: 2 }).notNull(),
  poblacion: integer('poblacion').notNull(),
  tipologia: text('tipologia').notNull(),
});

// Indicador Territorial
export const locindicadorterritorial = pgTable('loc_indicador_territorial', {
  id_indicador: uuid('id_indicador').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  dimension: text('dimension').notNull(),
  valor: numeric('valor', { precision: 15, scale: 2 }).notNull(),
  territorio_id: uuid('territorio_id').notNull(),
  periodo_id: uuid('periodo_id').notNull(),
});

// estado,
export const locipt = pgTable('loc_ipt', {
  id_ipt: uuid('id_ipt').primaryKey().defaultRandom(),
  tipo: text('tipo').notNull(),
  nombre: text('nombre').notNull(),
  territorio_id: uuid('territorio_id'),
  region_id: uuid('region_id'),
  fecha_aprobacion: date('fecha_aprobacion'),
  fecha_vigencia: date('fecha_vigencia'),
});

// Localidad
export const loclocalidad = pgTable('loc_localidad', {
  id_localidad: uuid('id_localidad').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  comuna_id: uuid('comuna_id').notNull(),
  tipo: text('tipo').notNull(),
  latitud: numeric('latitud', { precision: 15, scale: 2 }).notNull(),
  longitud: numeric('longitud', { precision: 15, scale: 2 }).notNull(),
});

// Plan Regional de Ordenamiento Territorial
export const locprot = pgTable('loc_prot', {
  id_prot: uuid('id_prot').primaryKey().defaultRandom(),
  region_id: uuid('region_id').notNull(),
  fecha_aprobacion: date('fecha_aprobacion').notNull(),
  estado: text('estado').notNull(),
});

// Provincia
export const locprovincia = pgTable('loc_provincia', {
  id_provincia: uuid('id_provincia').primaryKey().defaultRandom(),
  codigo_ine: text('codigo_ine').notNull(),
  nombre: text('nombre').notNull(),
  region_id: uuid('region_id').notNull(),
});

// Región
export const locregion = pgTable('loc_region', {
  id_region: uuid('id_region').primaryKey().defaultRandom(),
  codigo_ine: text('codigo_ine').notNull(),
  nombre: text('nombre').notNull(),
  capital: text('capital').notNull(),
  superficie_km2: numeric('superficie_km2', { precision: 15, scale: 2 }).notNull(),
  poblacion: integer('poblacion').notNull(),
});

// Zona Geográfica
export const loczonageografica = pgTable('loc_zona_geografica', {
  id_zona: uuid('id_zona').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  tipo: text('tipo').notNull(),
  region_id: uuid('region_id').notNull(),
});

// severidad,
export const loczonariesgo = pgTable('loc_zona_riesgo', {
  id_zona_riesgo: uuid('id_zona_riesgo').primaryKey().defaultRandom(),
  tipo_riesgo: text('tipo_riesgo').notNull(),
  nivel: text('nivel').notNull(),
  comuna_id: uuid('comuna_id').notNull(),
  geometria: text('geometria').notNull(),
  capa_id: uuid('capa_id'),
});
