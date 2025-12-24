// GORE_OS Drizzle Schema - Domain: D-CONV
// Auto-generated: 2025-12-23T07:04:05.101938
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// Acta
export const convacta = pgTable('conv_acta', {
  id_acta: uuid('id_acta').primaryKey().defaultRandom(),
  sesion_id: uuid('sesion_id').notNull(),
  secretario_id: uuid('secretario_id').notNull(),
  contenido: text('contenido').notNull(),
  estado: text('estado').notNull(),
  fecha_aprobacion: date('fecha_aprobacion').notNull(),
});

// Acuerdo
export const convacuerdo = pgTable('conv_acuerdo', {
  id_acuerdo: uuid('id_acuerdo').primaryKey().defaultRandom(),
  sesion_id: uuid('sesion_id').notNull(),
  numero: integer('numero').notNull(),
  materia: text('materia').notNull(),
  descripcion: text('descripcion').notNull(),
  tipo_votacion: text('tipo_votacion').notNull(),
  votos_favor: integer('votos_favor').notNull(),
  votos_contra: integer('votos_contra').notNull(),
  abstenciones: integer('abstenciones').notNull(),
  estado: text('estado').notNull(),
});

// Asistencia
export const convasistencia = pgTable('conv_asistencia', {
  id_asistencia: uuid('id_asistencia').primaryKey().defaultRandom(),
  sesion_id: uuid('sesion_id').notNull(),
  actor_id: uuid('actor_id').notNull(),
  rol_en_sesion: text('rol_en_sesion').notNull(),
  hora_ingreso: timestamp('hora_ingreso').notNull(),
  hora_salida: timestamp('hora_salida').notNull(),
  modalidad: text('modalidad').notNull(),
});

// Audiencia
export const convaudiencia = pgTable('conv_audiencia', {
  id_audiencia: uuid('id_audiencia').primaryKey().defaultRandom(),
  tipo: text('tipo').notNull(),
  solicitante_id: uuid('solicitante_id').notNull(),
  autoridad_id: uuid('autoridad_id').notNull(),
  fecha: timestamp('fecha').notNull(),
  materia: text('materia').notNull(),
  registro_ley_lobby: boolean('registro_ley_lobby').notNull(),
});

// Cabildo Territorial
export const convcabildo = pgTable('conv_cabildo', {
  id_cabildo: uuid('id_cabildo').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  territorio_id: uuid('territorio_id').notNull(),
  fecha: date('fecha').notNull(),
  participantes: integer('participantes').notNull(),
  propuestas_recibidas: integer('propuestas_recibidas').notNull(),
});

// Comité
export const convcomite = pgTable('conv_comite', {
  id_comite: uuid('id_comite').primaryKey().defaultRandom(),
  tipo: text('tipo').notNull(),
  territorio_id: uuid('territorio_id'),
  normativa: text('normativa').notNull(),
});

// verificado_por_id,
export const convcompromiso = pgTable('conv_compromiso', {
  id_compromiso: uuid('id_compromiso').primaryKey().defaultRandom(),
  acuerdo_id: uuid('acuerdo_id'),
  sesion_id: uuid('sesion_id'),
  descripcion: text('descripcion').notNull(),
  responsable_id: uuid('responsable_id').notNull(),
  fecha_compromiso: date('fecha_compromiso').notNull(),
  fecha_limite: date('fecha_limite').notNull(),
  prioridad: text('prioridad').notNull(),
  estado: text('estado').notNull(),
  porcentaje_avance: integer('porcentaje_avance').notNull(),
  problema_id: uuid('problema_id'),
});

// Consulta Pública
export const convconsultapublica = pgTable('conv_consulta_publica', {
  id_consulta: uuid('id_consulta').primaryKey().defaultRandom(),
  comuna_id: uuid('comuna_id').notNull(),
  nombre: text('nombre').notNull(),
  materia: text('materia').notNull(),
  fecha_inicio: date('fecha_inicio').notNull(),
  fecha_termino: date('fecha_termino').notNull(),
  modalidad: text('modalidad').notNull(),
  participantes: integer('participantes').notNull(),
});

// Convocatoria
export const convconvocatoria = pgTable('conv_convocatoria', {
  id_convocatoria: uuid('id_convocatoria').primaryKey().defaultRandom(),
  sesion_id: uuid('sesion_id').notNull(),
  fecha_emision: timestamp('fecha_emision').notNull(),
  tabla: text('tabla').notNull(),
  documentos_adjuntos: text('documentos_adjuntos').notNull(),
});

// Cuenta Pública
export const convcuentapublica = pgTable('conv_cuenta_publica', {
  id_cuenta: uuid('id_cuenta').primaryKey().defaultRandom(),
  anio: integer('anio').notNull(),
  gobernador_id: uuid('gobernador_id').notNull(),
  fecha: date('fecha').notNull(),
  documento_id: uuid('documento_id').notNull(),
});

// Gabinete Regional
export const convgabinete = pgTable('conv_gabinete', {
  id_gabinete: uuid('id_gabinete').primaryKey().defaultRandom(),
  gobernador_id: uuid('gobernador_id').notNull(),
  periodo_id: uuid('periodo_id').notNull(),
  miembros: text('miembros').notNull(),
});

// Instancia de Coordinación
export const convinstancia = pgTable('conv_instancia', {
  id_instancia: uuid('id_instancia').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  tipo: text('tipo').notNull(),
  periodicidad: text('periodicidad').notNull(),
  convocante_id: uuid('convocante_id').notNull(),
  activa: boolean('activa').default(true),
});

// notas,
export const convpuntotabla = pgTable('conv_punto_tabla', {
  id_punto: uuid('id_punto').primaryKey().defaultRandom(),
  sesion_id: uuid('sesion_id').notNull(),
  numero: integer('numero').notNull(),
  tipo: text('tipo').notNull(),
  materia: text('materia').notNull(),
});

// Sesión
export const convsesion = pgTable('conv_sesion', {
  id_sesion: uuid('id_sesion').primaryKey().defaultRandom(),
  instancia_id: uuid('instancia_id').notNull(),
  numero: integer('numero').notNull(),
  tipo_sesion: text('tipo_sesion').notNull(),
  fecha: timestamp('fecha').notNull(),
  lugar: text('lugar').notNull(),
  modalidad: text('modalidad').notNull(),
  estado: text('estado').notNull(),
  quorum_requerido: integer('quorum_requerido').notNull(),
  quorum_presente: integer('quorum_presente').notNull(),
});
