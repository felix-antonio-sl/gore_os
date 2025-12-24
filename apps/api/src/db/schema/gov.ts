// GORE_OS Drizzle Schema - Domain: D-GOV
// Auto-generated: 2025-12-23T10:39:16.560470
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// Acuerdo del CORE
export const govacuerdocore = pgTable('gov_acuerdo_core', {
  id_acuerdo_core: uuid('id_acuerdo_core').primaryKey().defaultRandom(),
  sesion_core_id: uuid('sesion_core_id').notNull(),
  numero: integer('numero').notNull(),
  materia: text('materia').notNull(),
  asunto: text('asunto').notNull(),
  votos_favor: integer('votos_favor').notNull(),
  votos_contra: integer('votos_contra').notNull(),
  abstenciones: integer('abstenciones').notNull(),
  resultado: text('resultado').notNull(),
});

// Comisión del CORE
export const govcomision = pgTable('gov_comision', {
  id_comision: uuid('id_comision').primaryKey().defaultRandom(),
  core_id: uuid('core_id').notNull(),
  nombre: text('nombre').notNull(),
  tipo: text('tipo').notNull(),
  materia: text('materia').notNull(),
  presidente_id: uuid('presidente_id').notNull(),
  miembros: text('miembros').notNull(),
  activa: boolean('activa').notNull(),
});

// integrantes,
export const govcomitecoordinacion = pgTable('gov_comite_coordinacion', {
  id_comite: uuid('id_comite').primaryKey().defaultRandom(),
  tipo: text('tipo').notNull(),
  nombre: text('nombre').notNull(),
  acto_creacion: text('acto_creacion'),
  fecha_creacion: date('fecha_creacion'),
  presidente_id: uuid('presidente_id'),
  secretario_id: uuid('secretario_id'),
  periodicidad: text('periodicidad'),
  estado: text('estado').notNull(),
});

// Consejero Regional
export const govconsejero = pgTable('gov_consejero', {
  id_consejero: uuid('id_consejero').primaryKey().defaultRandom(),
  persona_id: uuid('persona_id').notNull(),
  circunscripcion_id: uuid('circunscripcion_id').notNull(),
  periodo_inicio: date('periodo_inicio').notNull(),
  periodo_termino: date('periodo_termino').notNull(),
  partido_politico: text('partido_politico').notNull(),
  comisiones: text('comisiones').notNull(),
  estado: text('estado').notNull(),
});

// Consejo Regional
export const govcore = pgTable('gov_core', {
  id_core: uuid('id_core').primaryKey().defaultRandom(),
  region_id: uuid('region_id').notNull(),
  periodo_id: uuid('periodo_id').notNull(),
  presidente_id: uuid('presidente_id').notNull(),
  vicepresidente_id: uuid('vicepresidente_id').notNull(),
  numero_consejeros: integer('numero_consejeros').notNull(),
  quorum_sesion: integer('quorum_sesion').notNull(),
});

// Gobernador Regional
export const govgobernador = pgTable('gov_gobernador', {
  id_gobernador: uuid('id_gobernador').primaryKey().defaultRandom(),
  persona_id: uuid('persona_id').notNull(),
  region_id: uuid('region_id').notNull(),
  periodo_inicio: date('periodo_inicio').notNull(),
  periodo_termino: date('periodo_termino').notNull(),
  estado: text('estado').notNull(),
});

// Sesión del CORE
export const govsesioncore = pgTable('gov_sesion_core', {
  id_sesion_core: uuid('id_sesion_core').primaryKey().defaultRandom(),
  core_id: uuid('core_id').notNull(),
  numero: integer('numero').notNull(),
  tipo: text('tipo').notNull(),
  fecha: timestamp('fecha').notNull(),
  tabla: text('tabla').notNull(),
  quorum_presente: integer('quorum_presente').notNull(),
  estado: text('estado').notNull(),
});

// Tabla de Sesión
export const govtablasesion = pgTable('gov_tabla_sesion', {
  id_tabla: uuid('id_tabla').primaryKey().defaultRandom(),
  sesion_core_id: uuid('sesion_core_id').notNull(),
  numero_punto: integer('numero_punto').notNull(),
  materia: text('materia').notNull(),
  descripcion: text('descripcion').notNull(),
  estado: text('estado').notNull(),
  acuerdo_id: uuid('acuerdo_id'),
});

// Transferencia de Competencia
export const govtransferenciacompetencia = pgTable('gov_transferencia_competencia', {
  id_transferencia: uuid('id_transferencia').primaryKey().defaultRandom(),
  division_receptora_id: uuid('division_receptora_id').notNull(),
  nombre: text('nombre').notNull(),
  ministerio_origen: text('ministerio_origen').notNull(),
  decreto_transferencia: text('decreto_transferencia').notNull(),
  fecha_transferencia: date('fecha_transferencia').notNull(),
  recursos_asociados: numeric('recursos_asociados', { precision: 15, scale: 2 }).notNull(),
  estado: text('estado').notNull(),
});

// Votación
export const govvotacion = pgTable('gov_votacion', {
  id_votacion: uuid('id_votacion').primaryKey().defaultRandom(),
  acuerdo_core_id: uuid('acuerdo_core_id').notNull(),
  consejero_id: uuid('consejero_id').notNull(),
  voto: text('voto').notNull(),
  fundamento: text('fundamento'),
});
