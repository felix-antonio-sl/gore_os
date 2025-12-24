// GORE_OS Drizzle Schema - Domain: D-FIN
// Auto-generated: 2025-12-23T07:04:05.104128
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// Anteproyecto Regional de Inversiones
export const finari = pgTable('fin_ari', {
  id_ari: uuid('id_ari').primaryKey().defaultRandom(),
  periodo_id: uuid('periodo_id').notNull(),
  region_id: uuid('region_id').notNull(),
  monto_total: numeric('monto_total', { precision: 15, scale: 2 }).notNull(),
  estado: text('estado').notNull(),
});

// Asignación Presupuestaria
export const finasignacion = pgTable('fin_asignacion', {
  id_asignacion: uuid('id_asignacion').primaryKey().defaultRandom(),
  presupuesto_id: uuid('presupuesto_id').notNull(),
  subtitulo: text('subtitulo').notNull(),
  item: text('item').notNull(),
  asignacion: text('asignacion').notNull(),
  monto_inicial: numeric('monto_inicial', { precision: 15, scale: 2 }).notNull(),
  monto_vigente: numeric('monto_vigente', { precision: 15, scale: 2 }).notNull(),
  monto_ejecutado: numeric('monto_ejecutado', { precision: 15, scale: 2 }).notNull(),
  denominacion: text('denominacion'),
  nombre_linea: text('nombre_linea'),
  marca_cm: text('marca_cm'),
});

// Certificado de Disponibilidad Presupuestaria
export const fincdp = pgTable('fin_cdp', {
  id_cdp: uuid('id_cdp').primaryKey().defaultRandom(),
  numero: text('numero').notNull(),
  asignacion_id: uuid('asignacion_id').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  fecha_emision: date('fecha_emision').notNull(),
  fecha_vencimiento: date('fecha_vencimiento').notNull(),
  estado: text('estado').notNull(),
});

// Compromiso Presupuestario
export const fincompromisopresupuestario = pgTable('fin_compromiso_presupuestario', {
  id_compromiso: uuid('id_compromiso').primaryKey().defaultRandom(),
  cdp_id: uuid('cdp_id').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  fecha: date('fecha').notNull(),
  descripcion: text('descripcion').notNull(),
  estado: text('estado').notNull(),
});

// Contrato Administrativo
export const fincontrato = pgTable('fin_contrato', {
  id_contrato: uuid('id_contrato').primaryKey().defaultRandom(),
  numero: text('numero').notNull(),
  proveedor_id: uuid('proveedor_id').notNull(),
  objeto: text('objeto').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  fecha_inicio: date('fecha_inicio').notNull(),
  fecha_termino: date('fecha_termino').notNull(),
  estado: text('estado').notNull(),
});

// hitos,
export const finconvenioprogramacion = pgTable('fin_convenio_programacion', {
  id_cp: uuid('id_cp').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  ministerio: text('ministerio').notNull(),
  region_id: uuid('region_id').notNull(),
  monto_total: numeric('monto_total', { precision: 15, scale: 2 }).notNull(),
  fecha_firma: date('fecha_firma').notNull(),
  vigencia_anios: integer('vigencia_anios').notNull(),
  estado: text('estado').notNull(),
});

// Devengo Contable
export const findevengo = pgTable('fin_devengo', {
  id_devengo: uuid('id_devengo').primaryKey().defaultRandom(),
  compromiso_id: uuid('compromiso_id').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  fecha: date('fecha').notNull(),
  documento_respaldo: text('documento_respaldo').notNull(),
});

// Eje Estratégico
export const finejeestrategico = pgTable('fin_eje_estrategico', {
  id_eje: uuid('id_eje').primaryKey().defaultRandom(),
  erd_id: uuid('erd_id').notNull(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
});

// planes_regionales,
export const finerd = pgTable('fin_erd', {
  id_erd: uuid('id_erd').primaryKey().defaultRandom(),
  region_id: uuid('region_id').notNull(),
  periodo_inicio: integer('periodo_inicio').notNull(),
  periodo_termino: integer('periodo_termino').notNull(),
  vision: text('vision').notNull(),
  estado: text('estado').notNull(),
});

// aplica_a_via,
export const finestadorate = pgTable('fin_estado_rate', {
  codigo: text('codigo').primaryKey().defaultRandom(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
  permite_financiamiento: boolean('permite_financiamiento').notNull(),
  requiere_accion: text('requiere_accion'),
  es_terminal: boolean('es_terminal').notNull(),
});

// subtitulo_principal,
export const finfondo = pgTable('fin_fondo', {
  id_fondo: uuid('id_fondo').primaryKey().defaultRandom(),
});

// Garantía Financiera
export const fingarantiafinanciera = pgTable('fin_garantia_financiera', {
  id_garantia: uuid('id_garantia').primaryKey().defaultRandom(),
  tipo: text('tipo').notNull(),
  numero: text('numero').notNull(),
  institucion: text('institucion').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  fecha_emision: date('fecha_emision').notNull(),
  fecha_vencimiento: date('fecha_vencimiento').notNull(),
  estado: text('estado').notNull(),
});

// Iniciativa de Inversión
export const finidi = pgTable('fin_idi', {
  id_idi: uuid('id_idi').primaryKey().defaultRandom(),
  comuna_id: uuid('comuna_id').notNull(),
  division_responsable_id: uuid('division_responsable_id').notNull(),
  codigo_bip: text('codigo_bip').notNull(),
  nombre: text('nombre').notNull(),
  tipo: text('tipo').notNull(),
  etapa_sni: text('etapa_sni').notNull(),
  monto_solicitado: numeric('monto_solicitado', { precision: 15, scale: 2 }).notNull(),
  estado: text('estado').notNull(),
});

// via_evaluacion_id,
export const finipr = pgTable('fin_ipr', {
  id_ipr: uuid('id_ipr').primaryKey().defaultRandom(),
  codigo_bip: text('codigo_bip').notNull(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
  tipo: text('tipo').notNull(),
  mecanismo_id: uuid('mecanismo_id').notNull(),
  monto_total: numeric('monto_total', { precision: 15, scale: 2 }).notNull(),
  comuna_id: uuid('comuna_id').notNull(),
  estado_ciclo: text('estado_ciclo').notNull(),
  etapa_actual: text('etapa_actual').notNull(),
  fecha_rs: date('fecha_rs').notNull(),
  vigencia: text('vigencia'),
  tipologia: text('tipologia'),
  origen: text('origen'),
  fuente: text('fuente'),
  sub_estado: text('sub_estado'),
  rate_actual: text('rate_actual'),
  fecha_rate: date('fecha_rate'),
  n_rates_emitidos: integer('n_rates_emitidos'),
});

// Licitación
export const finlicitacion = pgTable('fin_licitacion', {
  id_licitacion: uuid('id_licitacion').primaryKey().defaultRandom(),
  idi_asociada_id: uuid('idi_asociada_id').notNull(),
  codigo_mercado_publico: text('codigo_mercado_publico').notNull(),
  nombre: text('nombre').notNull(),
  tipo: text('tipo').notNull(),
  monto_estimado: numeric('monto_estimado', { precision: 15, scale: 2 }).notNull(),
  fecha_publicacion: date('fecha_publicacion').notNull(),
  fecha_cierre: date('fecha_cierre').notNull(),
  estado: text('estado').notNull(),
});

// estado,
export const finlineaari = pgTable('fin_linea_ari', {
  id_linea_ari: uuid('id_linea_ari').primaryKey().defaultRandom(),
  ari_id: uuid('ari_id').notNull(),
  codigo_linea: text('codigo_linea').notNull(),
  nombre: text('nombre').notNull(),
  eje_id: uuid('eje_id'),
});

// schema_metadata,
export const finmecanismo = pgTable('fin_mecanismo', {
  id_mecanismo: uuid('id_mecanismo').primaryKey().defaultRandom(),
  codigo: text('codigo').notNull(),
  nombre: text('nombre').notNull(),
  tipo: text('tipo').notNull(),
  normativa: text('normativa').notNull(),
  activo: boolean('activo').notNull(),
  glosa: text('glosa'),
  subtitulo: integer('subtitulo'),
  monto_min: numeric('monto_min', { precision: 15, scale: 2 }),
  monto_max: numeric('monto_max', { precision: 15, scale: 2 }),
  requiere_rate: boolean('requiere_rate'),
  categorias_validas: text('categorias_validas'),
});

// Medida Temporal
export const finmedidatemporal = pgTable('fin_medida_temporal', {
  id_medida: uuid('id_medida').primaryKey().defaultRandom(),
  periodo_id: uuid('periodo_id').notNull(),
  entidad_tipo: text('entidad_tipo').notNull(),
  entidad_id: uuid('entidad_id').notNull(),
  asignacion_id: uuid('asignacion_id'),
  tipo_medida: text('tipo_medida').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  unidad: text('unidad'),
});

// Modificación Presupuestaria
export const finmodificacionpresupuestaria = pgTable('fin_modificacion_presupuestaria', {
  id_modificacion: uuid('id_modificacion').primaryKey().defaultRandom(),
  tipo: text('tipo').notNull(),
  asignacion_origen_id: uuid('asignacion_origen_id').notNull(),
  asignacion_destino_id: uuid('asignacion_destino_id').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  justificacion: text('justificacion').notNull(),
  acto_id: uuid('acto_id').notNull(),
  estado: text('estado').notNull(),
});

// Objetivo Estratégico
export const finobjetivoestrategico = pgTable('fin_objetivo_estrategico', {
  id_objetivo: uuid('id_objetivo').primaryKey().defaultRandom(),
  eje_id: uuid('eje_id').notNull(),
  nombre: text('nombre').notNull(),
  indicador: text('indicador').notNull(),
  meta: text('meta').notNull(),
});

// Orden de Compra
export const finordencompra = pgTable('fin_orden_compra', {
  id_oc: uuid('id_oc').primaryKey().defaultRandom(),
  numero: text('numero').notNull(),
  proveedor_id: uuid('proveedor_id').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  fecha_emision: date('fecha_emision').notNull(),
  estado: text('estado').notNull(),
});

// Programa Público Regional
export const finppr = pgTable('fin_ppr', {
  id_ppr: uuid('id_ppr').primaryKey().defaultRandom(),
  codigo: text('codigo').notNull(),
  nombre: text('nombre').notNull(),
  objetivo: text('objetivo').notNull(),
  poblacion_objetivo: text('poblacion_objetivo').notNull(),
  presupuesto_anual: numeric('presupuesto_anual', { precision: 15, scale: 2 }).notNull(),
  periodo_id: uuid('periodo_id').notNull(),
  estado: text('estado').notNull(),
});

// Presupuesto
export const finpresupuesto = pgTable('fin_presupuesto', {
  id_presupuesto: uuid('id_presupuesto').primaryKey().defaultRandom(),
  periodo_id: uuid('periodo_id').notNull(),
  ley_presupuesto: text('ley_presupuesto').notNull(),
  monto_inicial: numeric('monto_inicial', { precision: 15, scale: 2 }).notNull(),
  monto_vigente: numeric('monto_vigente', { precision: 15, scale: 2 }).notNull(),
  estado: text('estado').notNull(),
});

// Proveedor
export const finproveedor = pgTable('fin_proveedor', {
  id_proveedor: uuid('id_proveedor').primaryKey().defaultRandom(),
  rut: text('rut').notNull(),
  razon_social: text('razon_social').notNull(),
  giro: text('giro').notNull(),
  direccion: text('direccion').notNull(),
  estado_mercado_publico: text('estado_mercado_publico').notNull(),
});

// Reintegro
export const finreintegro = pgTable('fin_reintegro', {
  id_reintegro: uuid('id_reintegro').primaryKey().defaultRandom(),
  rendicion_id: uuid('rendicion_id').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  motivo: text('motivo').notNull(),
  fecha: date('fecha').notNull(),
  estado: text('estado').notNull(),
});

// Remesa
export const finremesa = pgTable('fin_remesa', {
  id_remesa: uuid('id_remesa').primaryKey().defaultRandom(),
  transferencia_id: uuid('transferencia_id').notNull(),
  numero: integer('numero').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  fecha: date('fecha').notNull(),
  estado: text('estado').notNull(),
});

// Rendición
export const finrendicion = pgTable('fin_rendicion', {
  id_rendicion: uuid('id_rendicion').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  numero: integer('numero').notNull(),
  monto_rendido: numeric('monto_rendido', { precision: 15, scale: 2 }).notNull(),
  fecha_presentacion: date('fecha_presentacion').notNull(),
  estado: text('estado').notNull(),
  correlativo: text('correlativo'),
  tipo_documento_rendicion: text('tipo_documento_rendicion'),
  fecha_ingreso: date('fecha_ingreso'),
  monto_reintegrado: numeric('monto_reintegrado', { precision: 15, scale: 2 }),
  saldo_pendiente: numeric('saldo_pendiente', { precision: 15, scale: 2 }),
  observado: boolean('observado'),
  rendicion_a_tiempo: boolean('rendicion_a_tiempo'),
  recepcionado_por: text('recepcionado_por'),
});

// fuente,
export const finseriefinanciera = pgTable('fin_serie_financiera', {
  id_serie: uuid('id_serie').primaryKey().defaultRandom(),
});

// Transferencia
export const fintransferencia = pgTable('fin_transferencia', {
  id_transferencia: uuid('id_transferencia').primaryKey().defaultRandom(),
  convenio_id: uuid('convenio_id').notNull(),
  numero_cuota: integer('numero_cuota').notNull(),
  monto: numeric('monto', { precision: 15, scale: 2 }).notNull(),
  fecha: date('fecha').notNull(),
  estado: text('estado').notNull(),
});

// instrumento_formulacion,
export const finviaevaluacion = pgTable('fin_via_evaluacion', {
  id_via: uuid('id_via').primaryKey().defaultRandom(),
  codigo: text('codigo').notNull(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
  normativa: text('normativa').notNull(),
  aplica_a: text('aplica_a').notNull(),
  subtitulo_tipico: integer('subtitulo_tipico'),
});

// objetivo_id,
export const planbrechaerd = pgTable('plan_brecha_erd', {
  id_brecha: uuid('id_brecha').primaryKey().defaultRandom(),
  erd_id: uuid('erd_id').notNull(),
});
