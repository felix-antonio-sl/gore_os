// GORE_OS Drizzle Schema - Domain: D-EJE
// Auto-generated: 2025-12-23T10:39:16.559200
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// Acta de Recepción
export const ejeactarecepcion = pgTable('eje_acta_recepcion', {
  id_acta: uuid('id_acta').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  tipo: text('tipo').notNull(),
  fecha: date('fecha').notNull(),
  observaciones: text('observaciones').notNull(),
  conforme: boolean('conforme').notNull(),
});

// georeferencia,
export const ejebitacoraobra = pgTable('eje_bitacora_obra', {
  id_bitacora: uuid('id_bitacora').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  fecha_registro: timestamp('fecha_registro').notNull(),
});

// nivel_alerta,
export const ejeconvenio = pgTable('eje_convenio', {
  id_convenio_eje: uuid('id_convenio_eje').primaryKey().defaultRandom(),
});

// estado,
export const ejecuota = pgTable('eje_cuota', {
  id_cuota: uuid('id_cuota').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  numero: integer('numero').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  es_anticipo: boolean('es_anticipo').default(false),
  fecha_programada: date('fecha_programada').notNull(),
});

// Ejecutor
export const ejeejecutor = pgTable('eje_ejecutor', {
  id_ejecutor: uuid('id_ejecutor').primaryKey().defaultRandom(),
  rut: text('rut').notNull(),
  razon_social: text('razon_social').notNull(),
  tipo: text('tipo').notNull(),
  direccion: text('direccion').notNull(),
  representante_legal: text('representante_legal').notNull(),
  calificacion: numeric('calificacion', { precision: 15, scale: 2 }).notNull(),
  estado: text('estado').notNull(),
  correo: text('correo'),
  correo_2: text('correo_2'),
  telefono: text('telefono'),
});

// Estado de Pago
export const ejeestadopago = pgTable('eje_estado_pago', {
  id_ep: uuid('id_ep').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  numero: integer('numero').notNull(),
  monto_solicitado: numeric('monto_solicitado', { precision: 15, scale: 2 }).notNull(),
  monto_aprobado: numeric('monto_aprobado', { precision: 15, scale: 2 }).notNull(),
  fecha_presentacion: date('fecha_presentacion').notNull(),
  fecha_aprobacion: date('fecha_aprobacion'),
  estado: text('estado').notNull(),
});

// Evaluación Ex-Post
export const ejeevaluacionexpost = pgTable('eje_evaluacion_expost', {
  id_evaluacion: uuid('id_evaluacion').primaryKey().defaultRandom(),
  ipr_id: uuid('ipr_id').notNull(),
  fecha: date('fecha').notNull(),
  metodologia: text('metodologia').notNull(),
  resultado: text('resultado').notNull(),
  recomendaciones: text('recomendaciones').notNull(),
});

// Garantía de Convenio
export const ejegarantia = pgTable('eje_garantia', {
  id_garantia: uuid('id_garantia').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  tipo: text('tipo').notNull(),
  numero: text('numero').notNull(),
  institucion: text('institucion').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  fecha_vencimiento: date('fecha_vencimiento').notNull(),
  estado: text('estado').notNull(),
});

// Hito de Convenio
export const ejehito = pgTable('eje_hito', {
  id_hito: uuid('id_hito').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  numero: integer('numero').notNull(),
  descripcion: text('descripcion').notNull(),
  fecha_programada: date('fecha_programada').notNull(),
  fecha_real: date('fecha_real'),
  monto_asociado: numeric('monto_asociado', { precision: 15, scale: 2 }).notNull(),
  estado: text('estado').notNull(),
});

// Informe de Avance
export const ejeinformeavance = pgTable('eje_informe_avance', {
  id_informe: uuid('id_informe').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  periodo: text('periodo').notNull(),
  avance_fisico: numeric('avance_fisico', { precision: 15, scale: 2 }).notNull(),
  avance_financiero: numeric('avance_financiero', { precision: 15, scale: 2 }).notNull(),
  observaciones: text('observaciones').notNull(),
  fecha: date('fecha').notNull(),
});

// Liquidación de Convenio
export const ejeliquidacion = pgTable('eje_liquidacion', {
  id_liquidacion: uuid('id_liquidacion').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  monto_transferido: numeric('monto_transferido', { precision: 15, scale: 2 }).notNull(),
  monto_rendido: numeric('monto_rendido', { precision: 15, scale: 2 }).notNull(),
  saldo: numeric('saldo', { precision: 15, scale: 2 }).notNull(),
  fecha: date('fecha').notNull(),
  estado: text('estado').notNull(),
});

// Problema de Ejecución
export const ejeproblema = pgTable('eje_problema', {
  id_problema: uuid('id_problema').primaryKey().defaultRandom(),
  ipr_id: uuid('ipr_id').notNull(),
  convenio_id: uuid('convenio_id'),
  tipo: text('tipo').notNull(), // TECNICO|FINANCIERO|ADMINISTRATIVO|LEGAL|OTRO
  impacto: text('impacto').notNull(), // BAJO|MEDIO|ALTO|CRITICO
  descripcion: text('descripcion').notNull(),
  estado: text('estado').notNull().default('ABIERTO'), // ABIERTO|EN_GESTION|RESUELTO|CERRADO
  solucion_propuesta: text('solucion_propuesta'),
  fecha_registro: timestamp('fecha_registro').notNull().defaultNow(),
  fecha_resolucion: timestamp('fecha_resolucion'),
  detectado_por_id: uuid('detectado_por_id'),
  resuelto_por_id: uuid('resuelto_por_id'),
});

// Visita a Terreno
export const ejevisitaterreno = pgTable('eje_visita_terreno', {
  id_visita: uuid('id_visita').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  fecha: date('fecha').notNull(),
  inspector_id: uuid('inspector_id').notNull(),
  objetivo: text('objetivo').notNull(),
  observaciones: text('observaciones').notNull(),
  avance_fisico: numeric('avance_fisico', { precision: 15, scale: 2 }).notNull(),
});
