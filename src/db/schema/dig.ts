// GORE_OS Drizzle Schema - Domain: D-DIG
// Auto-generated: 2025-12-23T07:04:05.102623
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// Activo de Datos
export const digactivodatos = pgTable('dig_activo_datos', {
  id_activo: uuid('id_activo').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
  tipo: text('tipo').notNull(),
  clasificacion: text('clasificacion').notNull(),
  custodio_id: uuid('custodio_id').notNull(),
});

// Auditoría CGR
export const digauditoriacgr = pgTable('dig_auditoria_cgr', {
  id_auditoria: uuid('id_auditoria').primaryKey().defaultRandom(),
  numero: text('numero').notNull(),
  tipo: text('tipo').notNull(),
  materia: text('materia').notNull(),
  fecha_inicio: date('fecha_inicio').notNull(),
  fecha_informe: date('fecha_informe'),
  hallazgos: integer('hallazgos').notNull(),
  estado: text('estado').notNull(),
});

// Canal
export const digcanal = pgTable('dig_canal', {
  id_canal: uuid('id_canal').primaryKey().defaultRandom(),
  codigo: text('codigo').notNull(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion'),
  activo: boolean('activo').notNull(),
});

// Consentimiento
export const digconsentimiento = pgTable('dig_consentimiento', {
  id_consentimiento: uuid('id_consentimiento').primaryKey().defaultRandom(),
  titular_id: uuid('titular_id').notNull(),
  finalidad: text('finalidad').notNull(),
  fecha_otorgamiento: timestamp('fecha_otorgamiento').notNull(),
  fecha_revocacion: timestamp('fecha_revocacion'),
  vigente: boolean('vigente').notNull(),
});

// Enlace Externo
export const digenlace = pgTable('dig_enlace', {
  id_enlace: uuid('id_enlace').primaryKey().defaultRandom(),
  documento_id: uuid('documento_id').notNull(),
  url: text('url').notNull(),
  tipo_repositorio: text('tipo_repositorio').notNull(),
  fecha_verificacion: timestamp('fecha_verificacion'),
  estado: text('estado').notNull(),
});

// Evento de Documento
export const digeventodocumento = pgTable('dig_evento_documento', {
  documento_id: uuid('documento_id').notNull(),
  tipo_workflow: text('tipo_workflow').notNull(),
  division_destino_id: uuid('division_destino_id'),
  canal_id: uuid('canal_id'),
  respuesta_flag: boolean('respuesta_flag'),
  plazo_dias: integer('plazo_dias'),
  plazo_fecha: date('plazo_fecha'),
  instruccion: text('instruccion'),
});

// Expediente Electrónico
export const digexpediente = pgTable('dig_expediente', {
  id_expediente: uuid('id_expediente').primaryKey().defaultRandom(),
  numero: text('numero').notNull(),
  materia: text('materia').notNull(),
  fecha_creacion: timestamp('fecha_creacion').notNull(),
  estado: text('estado').notNull(),
  reservado: boolean('reservado').notNull(),
});

// Firma Electrónica
export const digfirma = pgTable('dig_firma', {
  id_firma: uuid('id_firma').primaryKey().defaultRandom(),
  documento_id: uuid('documento_id').notNull(),
  firmante_id: uuid('firmante_id').notNull(),
  tipo: text('tipo').notNull(),
  fecha: timestamp('fecha').notNull(),
  certificado: text('certificado').notNull(),
  valida: boolean('valida').notNull(),
});

// Folio
export const digfolio = pgTable('dig_folio', {
  id_folio: uuid('id_folio').primaryKey().defaultRandom(),
  expediente_id: uuid('expediente_id').notNull(),
  numero: integer('numero').notNull(),
  tipo_documento: text('tipo_documento').notNull(),
  fecha_incorporacion: timestamp('fecha_incorporacion').notNull(),
  hash: text('hash').notNull(),
});

// Incidente de Seguridad
export const digincidenteseguridad = pgTable('dig_incidente_seguridad', {
  id_incidente: uuid('id_incidente').primaryKey().defaultRandom(),
  activo_afectado_id: uuid('activo_afectado_id').notNull(),
  tipo: text('tipo').notNull(),
  severidad: text('severidad').notNull(),
  fecha_deteccion: timestamp('fecha_deteccion').notNull(),
  descripcion: text('descripcion').notNull(),
  estado: text('estado').notNull(),
  resolucion: text('resolucion').notNull(),
});

// Nodo de Interoperabilidad
export const dignodointerop = pgTable('dig_nodo_interop', {
  id_nodo: uuid('id_nodo').primaryKey().defaultRandom(),
  division_propietaria_id: uuid('division_propietaria_id').notNull(),
  nombre: text('nombre').notNull(),
  institucion: text('institucion').notNull(),
  url_endpoint: text('url_endpoint').notNull(),
  protocolo: text('protocolo').notNull(),
  estado: text('estado').notNull(),
});

// Notificación Electrónica
export const dignotificacion = pgTable('dig_notificacion', {
  id_notificacion: uuid('id_notificacion').primaryKey().defaultRandom(),
  documento_id: uuid('documento_id').notNull(),
  destinatario_id: uuid('destinatario_id').notNull(),
  canal: text('canal').notNull(),
  fecha_envio: timestamp('fecha_envio').notNull(),
  fecha_lectura: timestamp('fecha_lectura'),
  estado: text('estado').notNull(),
});

// Plataforma
export const digplataforma = pgTable('dig_plataforma', {
  id_plataforma: uuid('id_plataforma').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  tipo: text('tipo').notNull(),
  url: text('url').notNull(),
  responsable_id: uuid('responsable_id').notNull(),
  estado: text('estado').notNull(),
});

// Servicio de Interoperabilidad
export const digserviciointerop = pgTable('dig_servicio_interop', {
  id_servicio: uuid('id_servicio').primaryKey().defaultRandom(),
  nodo_id: uuid('nodo_id').notNull(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
  tipo: text('tipo').notNull(),
  activo: boolean('activo').notNull(),
});

// Solicitud ARCO
export const digsolicitudarco = pgTable('dig_solicitud_arco', {
  id_solicitud: uuid('id_solicitud').primaryKey().defaultRandom(),
  tipo: text('tipo').notNull(),
  solicitante_id: uuid('solicitante_id').notNull(),
  fecha_solicitud: timestamp('fecha_solicitud').notNull(),
  fecha_respuesta: timestamp('fecha_respuesta'),
  estado: text('estado').notNull(),
});

// estado,
export const digsolicitudtransparencia = pgTable('dig_solicitud_transparencia', {
  id_solicitud: uuid('id_solicitud').primaryKey().defaultRandom(),
  numero_folio: text('numero_folio').notNull(),
  fecha_ingreso: timestamp('fecha_ingreso').notNull(),
  solicitante_nombre: text('solicitante_nombre').notNull(),
  solicitante_rut: text('solicitante_rut'),
  solicitante_email: text('solicitante_email').notNull(),
});

// Toma de Razón
export const digtomarazon = pgTable('dig_toma_razon', {
  id_toma_razon: uuid('id_toma_razon').primaryKey().defaultRandom(),
  acto_id: uuid('acto_id').notNull(),
  fecha_ingreso: date('fecha_ingreso').notNull(),
  fecha_pronunciamiento: date('fecha_pronunciamiento'),
  resultado: text('resultado').notNull(),
  observaciones: text('observaciones').notNull(),
});

// Trámite
export const digtramite = pgTable('dig_tramite', {
  id_tramite: uuid('id_tramite').primaryKey().defaultRandom(),
  expediente_id: uuid('expediente_id').notNull(),
  tipo: text('tipo').notNull(),
  solicitante_id: uuid('solicitante_id').notNull(),
  fecha_inicio: timestamp('fecha_inicio').notNull(),
  fecha_termino: timestamp('fecha_termino'),
  estado: text('estado').notNull(),
});
