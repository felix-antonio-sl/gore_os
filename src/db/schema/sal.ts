// GORE_OS Drizzle Schema - Domain: D-SAL
// Auto-generated: 2025-12-23T07:04:05.105617
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// regla_origen,
export const salalerta = pgTable('sal_alerta', {
  id_alerta: uuid('id_alerta').primaryKey().defaultRandom(),
  tipo: text('tipo').notNull(),
  severidad: text('severidad').notNull(),
  origen: text('origen').notNull(),
  mensaje: text('mensaje').notNull(),
  fecha: timestamp('fecha').notNull(),
  atendida: boolean('atendida').notNull(),
  ipr_id: uuid('ipr_id'),
  convenio_id: uuid('convenio_id'),
});

// Aprendizaje Institucional
export const salaprendizaje = pgTable('sal_aprendizaje', {
  id_aprendizaje: uuid('id_aprendizaje').primaryKey().defaultRandom(),
  intervencion_id: uuid('intervencion_id').notNull(),
  tipo: text('tipo').notNull(),
  descripcion: text('descripcion').notNull(),
  fecha: date('fecha').notNull(),
  aplicable_a: text('aplicable_a').notNull(),
});

// Dimensión de Salud
export const saldimension = pgTable('sal_dimension', {
  id_dimension: uuid('id_dimension').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
  peso: numeric('peso', { precision: 15, scale: 2 }).notNull(),
  activa: boolean('activa').notNull(),
});

// Equipo de Intervención
export const salequipointervencion = pgTable('sal_equipo_intervencion', {
  id_equipo: uuid('id_equipo').primaryKey().defaultRandom(),
  intervencion_id: uuid('intervencion_id').notNull(),
  nombre_equipo: text('nombre_equipo').notNull(),
  lider_id: uuid('lider_id'),
  fecha_conformacion: date('fecha_conformacion').notNull(),
  estado: text('estado').notNull(),
  miembros: jsonb('miembros').notNull(),
  recursos_asignados: jsonb('recursos_asignados'),
});

// H_gore
export const salhgore = pgTable('sal_h_gore', {
  id_hgore: uuid('id_hgore').primaryKey().defaultRandom(),
  region_id: uuid('region_id').notNull(),
  periodo_id: uuid('periodo_id').notNull(),
  puntaje_global: numeric('puntaje_global', { precision: 15, scale: 2 }).notNull(),
  estado: text('estado').notNull(),
});

// Indicador POA
export const salindicadorpoa = pgTable('sal_indicador_poa', {
  id_indicador: uuid('id_indicador').primaryKey().defaultRandom(),
  poa_id: uuid('poa_id').notNull(),
  nombre: text('nombre').notNull(),
  meta: numeric('meta', { precision: 15, scale: 2 }).notNull(),
  actual: numeric('actual', { precision: 15, scale: 2 }).notNull(),
  ponderacion: numeric('ponderacion', { precision: 15, scale: 2 }).notNull(),
});

// Intervención FENIX
export const salintervencion = pgTable('sal_intervencion', {
  id_intervencion: uuid('id_intervencion').primaryKey().defaultRandom(),
  alerta_id: uuid('alerta_id').notNull(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
  responsable_id: uuid('responsable_id').notNull(),
  fecha_inicio: date('fecha_inicio').notNull(),
  fecha_termino: date('fecha_termino'),
  estado: text('estado').notNull(),
});

// Key Result
export const salkeyresult = pgTable('sal_key_result', {
  id_kr: uuid('id_kr').primaryKey().defaultRandom(),
  okr_id: uuid('okr_id').notNull(),
  descripcion: text('descripcion').notNull(),
  meta: numeric('meta', { precision: 15, scale: 2 }).notNull(),
  actual: numeric('actual', { precision: 15, scale: 2 }).notNull(),
  unidad: text('unidad').notNull(),
});

// OKR
export const salokr = pgTable('sal_okr', {
  id_okr: uuid('id_okr').primaryKey().defaultRandom(),
  objetivo: text('objetivo').notNull(),
  periodo_id: uuid('periodo_id').notNull(),
  responsable_id: uuid('responsable_id').notNull(),
  estado: text('estado').notNull(),
});

// Plan de Acción
export const salplanaccion = pgTable('sal_plan_accion', {
  id_plan: uuid('id_plan').primaryKey().defaultRandom(),
  intervencion_id: uuid('intervencion_id').notNull(),
  nombre: text('nombre').notNull(),
  objetivo: text('objetivo').notNull(),
  acciones: text('acciones').notNull(),
  estado: text('estado').notNull(),
});

// ejecuciones,
export const salplaybook = pgTable('sal_playbook', {
  id_playbook: uuid('id_playbook').primaryKey().defaultRandom(),
  poa_id: uuid('poa_id').notNull(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
  trigger: text('trigger').notNull(),
  pasos: text('pasos').notNull(),
  activo: boolean('activo').notNull(),
});

// Plan Operativo Anual
export const salpoa = pgTable('sal_poa', {
  id_poa: uuid('id_poa').primaryKey().defaultRandom(),
  division_id: uuid('division_id').notNull(),
  periodo_id: uuid('periodo_id').notNull(),
  estado: text('estado').notNull(),
});

// Puntaje
export const salpuntaje = pgTable('sal_puntaje', {
  id_puntaje: uuid('id_puntaje').primaryKey().defaultRandom(),
  hgore_id: uuid('hgore_id').notNull(),
  dimension_id: uuid('dimension_id').notNull(),
  valor: numeric('valor', { precision: 15, scale: 2 }).notNull(),
  fecha_calculo: date('fecha_calculo').notNull(),
});

// Riesgo
export const salriesgo = pgTable('sal_riesgo', {
  id_riesgo: uuid('id_riesgo').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
  probabilidad: text('probabilidad').notNull(),
  impacto: text('impacto').notNull(),
  mitigacion: text('mitigacion').notNull(),
  responsable_id: uuid('responsable_id').notNull(),
  estado: text('estado').notNull(),
});

// Umbral
export const salumbral = pgTable('sal_umbral', {
  id_umbral: uuid('id_umbral').primaryKey().defaultRandom(),
  dimension_id: uuid('dimension_id').notNull(),
  nivel: text('nivel').notNull(),
  valor_min: numeric('valor_min', { precision: 15, scale: 2 }).notNull(),
  valor_max: numeric('valor_max', { precision: 15, scale: 2 }).notNull(),
  color: text('color').notNull(),
});
