// GORE_OS Drizzle Schema - Domain: D-SYS
// Auto-generated: 2025-12-23T10:39:16.563488
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// Acto Administrativo
export const sysacto = pgTable('sys_acto', {
  id_acto: uuid('id_acto').primaryKey().defaultRandom(),
  tipo_acto: text('tipo_acto').notNull(),
  materia: text('materia').notNull(),
  autoridad_id: uuid('autoridad_id').notNull(),
  fecha_dictacion: date('fecha_dictacion').notNull(),
  requiere_toma_razon: boolean('requiere_toma_razon').notNull(),
  estado_tramitacion: text('estado_tramitacion').notNull(),
});

// Actor
export const sysactor = pgTable('sys_actor', {
  id_actor: uuid('id_actor').primaryKey().defaultRandom(),
  tipo_actor: text('tipo_actor').notNull(),
  identificador: text('identificador').notNull(),
  nombre: text('nombre').notNull(),
  activo: boolean('activo').default(true),
});

// estado,
export const sysconvenio = pgTable('sys_convenio', {
  id_convenio: uuid('id_convenio').primaryKey().defaultRandom(),
});

// metadata_legacy,
export const sysdocumento = pgTable('sys_documento', {
  id_documento: uuid('id_documento').primaryKey().defaultRandom(),
  tipo_documento: text('tipo_documento').notNull(),
  numero: text('numero').notNull(),
  fecha_emision: date('fecha_emision').notNull(),
  emisor_id: uuid('emisor_id').notNull(),
  hash_contenido: text('hash_contenido').notNull(),
  estado: text('estado').notNull(),
  folio: text('folio'),
  correlativo: text('correlativo'),
  materia: text('materia'),
  remitente: text('remitente'),
  destinatario: text('destinatario'),
  canal_recepcion_id: uuid('canal_recepcion_id'),
  canal_despacho_id: uuid('canal_despacho_id'),
  tiene_adjunto: boolean('tiene_adjunto'),
});

// Evento
export const sysevento = pgTable('sys_evento', {
  id_evento: uuid('id_evento').primaryKey().defaultRandom(),
  tipo_evento: text('tipo_evento').notNull(),
  fecha_evento: timestamp('fecha_evento').notNull(),
  actor_id: uuid('actor_id'),
  entidad_tipo: text('entidad_tipo'),
  entidad_id: uuid('entidad_id'),
  observacion: text('observacion'),
});

// Identificador Legacy
export const sysidentificadorlegacy = pgTable('sys_identificador_legacy', {
  id_identificador: uuid('id_identificador').primaryKey().defaultRandom(),
  entidad_tipo: text('entidad_tipo').notNull(),
  entidad_id: uuid('entidad_id').notNull(),
  sistema_origen: text('sistema_origen').notNull(),
  codigo_legacy: text('codigo_legacy').notNull(),
  codigo_tipo: text('codigo_tipo').notNull(),
  hoja_origen: text('hoja_origen'),
  fila_origen: integer('fila_origen'),
  hash_fila: text('hash_fila'),
});

// Período
export const sysperiodo = pgTable('sys_periodo', {
  id_periodo: uuid('id_periodo').primaryKey().defaultRandom(),
  anio: integer('anio').notNull(),
  tipo: text('tipo').notNull(),
  fecha_inicio: date('fecha_inicio').notNull(),
  fecha_fin: date('fecha_fin').notNull(),
});
