// GORE_OS Drizzle Schema - Domain: D-ORG
// Auto-generated: 2025-12-23T10:39:16.561613
// DO NOT EDIT MANUALLY - Regenerate from model/entities/

import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';

// Activo Fijo
export const orgactivo = pgTable('org_activo', {
  id_activo: uuid('id_activo').primaryKey().defaultRandom(),
  codigo_inventario: text('codigo_inventario').notNull(),
  descripcion: text('descripcion').notNull(),
  tipo: text('tipo').notNull(),
  valor_adquisicion: numeric('valor_adquisicion', { precision: 15, scale: 2 }).notNull(),
  fecha_adquisicion: date('fecha_adquisicion').notNull(),
  vida_util_anios: integer('vida_util_anios').notNull(),
  responsable_id: uuid('responsable_id').notNull(),
  estado: text('estado').notNull(),
});

// Asistencia
export const orgasistencia = pgTable('org_asistencia', {
  id_asistencia: uuid('id_asistencia').primaryKey().defaultRandom(),
  funcionario_id: uuid('funcionario_id').notNull(),
  fecha: date('fecha').notNull(),
  hora_entrada: text('hora_entrada').notNull(),
  hora_salida: text('hora_salida').notNull(),
  tipo: text('tipo').notNull(),
});

// Capacidad
export const orgcapacidad = pgTable('org_capacidad', {
  id_capacidad: uuid('id_capacidad').primaryKey().defaultRandom(),
  division_id: uuid('division_id').notNull(),
  nombre: text('nombre').notNull(),
  tipo: text('tipo').notNull(),
  nivel_requerido: text('nivel_requerido').notNull(),
  descripcion: text('descripcion').notNull(),
});

// Cargo
export const orgcargo = pgTable('org_cargo', {
  id_cargo: uuid('id_cargo').primaryKey().defaultRandom(),
  codigo: text('codigo').notNull(),
  nombre: text('nombre').notNull(),
  division_id: uuid('division_id').notNull(),
  estamento: text('estamento').notNull(),
  grado_min: integer('grado_min').notNull(),
  grado_max: integer('grado_max').notNull(),
  jefatura: boolean('jefatura').notNull(),
});

// Cometido Funcionario
export const orgcometido = pgTable('org_cometido', {
  id_cometido: uuid('id_cometido').primaryKey().defaultRandom(),
  funcionario_id: uuid('funcionario_id').notNull(),
  destino: text('destino').notNull(),
  motivo: text('motivo').notNull(),
  fecha_inicio: date('fecha_inicio').notNull(),
  fecha_termino: date('fecha_termino').notNull(),
  viatico: numeric('viatico', { precision: 15, scale: 2 }).notNull(),
  resolucion: text('resolucion').notNull(),
  estado: text('estado').notNull(),
});

// Contrato a Honorarios
export const orgcontratohonorario = pgTable('org_contrato_honorario', {
  id_contrato: uuid('id_contrato').primaryKey().defaultRandom(),
  funcionario_id: uuid('funcionario_id').notNull(),
  numero_contrato: text('numero_contrato').notNull(),
  objeto: text('objeto').notNull(),
  monto_bruto: numeric('monto_bruto', { precision: 15, scale: 2 }).notNull(),
  fecha_inicio: date('fecha_inicio').notNull(),
  fecha_termino: date('fecha_termino').notNull(),
  estado: text('estado').notNull(),
});

// Declaración Jurada
export const orgdeclaracionjurada = pgTable('org_declaracion_jurada', {
  id_declaracion: uuid('id_declaracion').primaryKey().defaultRandom(),
  funcionario_id: uuid('funcionario_id').notNull(),
  tipo: text('tipo').notNull(),
  fecha_presentacion: date('fecha_presentacion').notNull(),
  periodo_id: uuid('periodo_id').notNull(),
});

// division_padre_id,
export const orgdivision = pgTable('org_division', {
  id_division: uuid('id_division').primaryKey().defaultRandom(),
  codigo: text('codigo').notNull(),
  nombre: text('nombre').notNull(),
  sigla: text('sigla').notNull(),
  tipo: text('tipo').notNull(),
});

// Dotación
export const orgdotacion = pgTable('org_dotacion', {
  id_dotacion: uuid('id_dotacion').primaryKey().defaultRandom(),
  periodo_id: uuid('periodo_id').notNull(),
  calidad_juridica: text('calidad_juridica').notNull(),
  estamento: text('estamento').notNull(),
  cupos_autorizados: integer('cupos_autorizados').notNull(),
  cupos_ocupados: integer('cupos_ocupados').notNull(),
  presupuesto_asignado: numeric('presupuesto_asignado', { precision: 15, scale: 2 }).notNull(),
});

// derecho_horas_extras,
export const orgfuncionario = pgTable('org_funcionario', {
  id_funcionario: uuid('id_funcionario').primaryKey().defaultRandom(),
  rut: text('rut').notNull(),
  nombres: text('nombres').notNull(),
  apellido_paterno: text('apellido_paterno').notNull(),
  apellido_materno: text('apellido_materno').notNull(),
  email_institucional: text('email_institucional').notNull(),
  cargo_id: uuid('cargo_id').notNull(),
  division_id: uuid('division_id').notNull(),
  fecha_ingreso: date('fecha_ingreso').notNull(),
  calidad_juridica: text('calidad_juridica').notNull(),
  grado: integer('grado').notNull(),
  estado: text('estado').notNull(),
});

// Inventario
export const orginventario = pgTable('org_inventario', {
  id_inventario: uuid('id_inventario').primaryKey().defaultRandom(),
  fecha: date('fecha').notNull(),
  tipo: text('tipo').notNull(),
  responsable_id: uuid('responsable_id').notNull(),
  estado: text('estado').notNull(),
});

// Permiso Administrativo
export const orgpermiso = pgTable('org_permiso', {
  id_permiso: uuid('id_permiso').primaryKey().defaultRandom(),
  funcionario_id: uuid('funcionario_id').notNull(),
  tipo: text('tipo').notNull(),
  fecha_inicio: date('fecha_inicio').notNull(),
  fecha_termino: date('fecha_termino').notNull(),
  horas: numeric('horas', { precision: 15, scale: 2 }).notNull(),
  motivo: text('motivo').notNull(),
  estado: text('estado').notNull(),
});

// codigos_asignacion,
export const orgremuneracion = pgTable('org_remuneracion', {
  id_remuneracion: uuid('id_remuneracion').primaryKey().defaultRandom(),
  funcionario_id: uuid('funcionario_id').notNull(),
  periodo_id: uuid('periodo_id').notNull(),
  sueldo_base: numeric('sueldo_base', { precision: 15, scale: 2 }).notNull(),
  asignaciones: numeric('asignaciones', { precision: 15, scale: 2 }).notNull(),
  descuentos: numeric('descuentos', { precision: 15, scale: 2 }).notNull(),
  liquido: numeric('liquido', { precision: 15, scale: 2 }).notNull(),
  fecha_pago: date('fecha_pago').notNull(),
});

// Rol
export const orgrol = pgTable('org_rol', {
  id_rol: uuid('id_rol').primaryKey().defaultRandom(),
  plataforma_id: uuid('plataforma_id').notNull(),
  codigo: text('codigo').notNull(),
  nombre: text('nombre').notNull(),
  descripcion: text('descripcion').notNull(),
  permisos: text('permisos').notNull(),
  activo: boolean('activo').notNull(),
});

// Sumario Administrativo
export const orgsumario = pgTable('org_sumario', {
  id_sumario: uuid('id_sumario').primaryKey().defaultRandom(),
  numero: text('numero').notNull(),
  funcionario_id: uuid('funcionario_id').notNull(),
  fiscal_id: uuid('fiscal_id').notNull(),
  hechos: text('hechos').notNull(),
  fecha_inicio: date('fecha_inicio').notNull(),
  sancion: text('sancion').notNull(),
  estado: text('estado').notNull(),
});

// Vehículo
export const orgvehiculo = pgTable('org_vehiculo', {
  id_vehiculo: uuid('id_vehiculo').primaryKey().defaultRandom(),
  patente: text('patente').notNull(),
  tipo: text('tipo').notNull(),
  marca: text('marca').notNull(),
  modelo: text('modelo').notNull(),
  anio: integer('anio').notNull(),
  kilometraje: integer('kilometraje').notNull(),
});
