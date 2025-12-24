CREATE TABLE "conv_acta" (
	"id_acta" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"sesion_id" uuid NOT NULL,
	"secretario_id" uuid NOT NULL,
	"contenido" text NOT NULL,
	"estado" text NOT NULL,
	"fecha_aprobacion" date NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_acuerdo" (
	"id_acuerdo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"sesion_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"materia" text NOT NULL,
	"descripcion" text NOT NULL,
	"tipo_votacion" text NOT NULL,
	"votos_favor" integer NOT NULL,
	"votos_contra" integer NOT NULL,
	"abstenciones" integer NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_asistencia" (
	"id_asistencia" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"sesion_id" uuid NOT NULL,
	"actor_id" uuid NOT NULL,
	"rol_en_sesion" text NOT NULL,
	"hora_ingreso" timestamp NOT NULL,
	"hora_salida" timestamp NOT NULL,
	"modalidad" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_audiencia" (
	"id_audiencia" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo" text NOT NULL,
	"solicitante_id" uuid NOT NULL,
	"autoridad_id" uuid NOT NULL,
	"fecha" timestamp NOT NULL,
	"materia" text NOT NULL,
	"registro_ley_lobby" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_cabildo" (
	"id_cabildo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"territorio_id" uuid NOT NULL,
	"fecha" date NOT NULL,
	"participantes" integer NOT NULL,
	"propuestas_recibidas" integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_comite" (
	"id_comite" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo" text NOT NULL,
	"territorio_id" uuid,
	"normativa" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_compromiso" (
	"id_compromiso" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"acuerdo_id" uuid,
	"sesion_id" uuid,
	"descripcion" text NOT NULL,
	"responsable_id" uuid NOT NULL,
	"fecha_compromiso" date NOT NULL,
	"fecha_limite" date NOT NULL,
	"prioridad" text NOT NULL,
	"estado" text NOT NULL,
	"porcentaje_avance" integer NOT NULL,
	"problema_id" uuid
);
--> statement-breakpoint
CREATE TABLE "conv_consulta_publica" (
	"id_consulta" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"comuna_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"materia" text NOT NULL,
	"fecha_inicio" date NOT NULL,
	"fecha_termino" date NOT NULL,
	"modalidad" text NOT NULL,
	"participantes" integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_convocatoria" (
	"id_convocatoria" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"sesion_id" uuid NOT NULL,
	"fecha_emision" timestamp NOT NULL,
	"tabla" text NOT NULL,
	"documentos_adjuntos" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_cuenta_publica" (
	"id_cuenta" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"anio" integer NOT NULL,
	"gobernador_id" uuid NOT NULL,
	"fecha" date NOT NULL,
	"documento_id" uuid NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_gabinete" (
	"id_gabinete" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"gobernador_id" uuid NOT NULL,
	"periodo_id" uuid NOT NULL,
	"miembros" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_instancia" (
	"id_instancia" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"tipo" text NOT NULL,
	"periodicidad" text NOT NULL,
	"convocante_id" uuid NOT NULL,
	"activa" boolean DEFAULT true
);
--> statement-breakpoint
CREATE TABLE "conv_punto_tabla" (
	"id_punto" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"sesion_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"tipo" text NOT NULL,
	"materia" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "conv_sesion" (
	"id_sesion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"instancia_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"tipo_sesion" text NOT NULL,
	"fecha" timestamp NOT NULL,
	"lugar" text NOT NULL,
	"modalidad" text NOT NULL,
	"estado" text NOT NULL,
	"quorum_requerido" integer NOT NULL,
	"quorum_presente" integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE "data_activo" (
	"id_activo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_activo_datos" (
	"id_activo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL,
	"tipo" text NOT NULL,
	"clasificacion" text NOT NULL,
	"custodio_id" uuid NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_auditoria_cgr" (
	"id_auditoria" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"numero" text NOT NULL,
	"tipo" text NOT NULL,
	"materia" text NOT NULL,
	"fecha_inicio" date NOT NULL,
	"fecha_informe" date,
	"hallazgos" integer NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_canal" (
	"id_canal" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo" text NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text,
	"activo" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_consentimiento" (
	"id_consentimiento" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"titular_id" uuid NOT NULL,
	"finalidad" text NOT NULL,
	"fecha_otorgamiento" timestamp NOT NULL,
	"fecha_revocacion" timestamp,
	"vigente" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_enlace" (
	"id_enlace" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"documento_id" uuid NOT NULL,
	"url" text NOT NULL,
	"tipo_repositorio" text NOT NULL,
	"fecha_verificacion" timestamp,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_evento_documento" (
	"documento_id" uuid NOT NULL,
	"tipo_workflow" text NOT NULL,
	"division_destino_id" uuid,
	"canal_id" uuid,
	"respuesta_flag" boolean,
	"plazo_dias" integer,
	"plazo_fecha" date,
	"instruccion" text
);
--> statement-breakpoint
CREATE TABLE "dig_expediente" (
	"id_expediente" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"numero" text NOT NULL,
	"materia" text NOT NULL,
	"fecha_creacion" timestamp NOT NULL,
	"estado" text NOT NULL,
	"reservado" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_firma" (
	"id_firma" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"documento_id" uuid NOT NULL,
	"firmante_id" uuid NOT NULL,
	"tipo" text NOT NULL,
	"fecha" timestamp NOT NULL,
	"certificado" text NOT NULL,
	"valida" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_folio" (
	"id_folio" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"expediente_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"tipo_documento" text NOT NULL,
	"fecha_incorporacion" timestamp NOT NULL,
	"hash" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_incidente_seguridad" (
	"id_incidente" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"activo_afectado_id" uuid NOT NULL,
	"tipo" text NOT NULL,
	"severidad" text NOT NULL,
	"fecha_deteccion" timestamp NOT NULL,
	"descripcion" text NOT NULL,
	"estado" text NOT NULL,
	"resolucion" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_nodo_interop" (
	"id_nodo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"division_propietaria_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"institucion" text NOT NULL,
	"url_endpoint" text NOT NULL,
	"protocolo" text NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_notificacion" (
	"id_notificacion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"documento_id" uuid NOT NULL,
	"destinatario_id" uuid NOT NULL,
	"canal" text NOT NULL,
	"fecha_envio" timestamp NOT NULL,
	"fecha_lectura" timestamp,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_plataforma" (
	"id_plataforma" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"tipo" text NOT NULL,
	"url" text NOT NULL,
	"responsable_id" uuid NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_servicio_interop" (
	"id_servicio" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nodo_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL,
	"tipo" text NOT NULL,
	"activo" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_solicitud_arco" (
	"id_solicitud" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo" text NOT NULL,
	"solicitante_id" uuid NOT NULL,
	"fecha_solicitud" timestamp NOT NULL,
	"fecha_respuesta" timestamp,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_solicitud_transparencia" (
	"id_solicitud" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"numero_folio" text NOT NULL,
	"fecha_ingreso" timestamp NOT NULL,
	"solicitante_nombre" text NOT NULL,
	"solicitante_rut" text,
	"solicitante_email" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_toma_razon" (
	"id_toma_razon" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"acto_id" uuid NOT NULL,
	"fecha_ingreso" date NOT NULL,
	"fecha_pronunciamiento" date,
	"resultado" text NOT NULL,
	"observaciones" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "dig_tramite" (
	"id_tramite" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"expediente_id" uuid NOT NULL,
	"tipo" text NOT NULL,
	"solicitante_id" uuid NOT NULL,
	"fecha_inicio" timestamp NOT NULL,
	"fecha_termino" timestamp,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_acta_recepcion" (
	"id_acta" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"tipo" text NOT NULL,
	"fecha" date NOT NULL,
	"observaciones" text NOT NULL,
	"conforme" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_bitacora_obra" (
	"id_bitacora" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"fecha_registro" timestamp NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_convenio" (
	"id_convenio_eje" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_cuota" (
	"id_cuota" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"es_anticipo" boolean DEFAULT false,
	"fecha_programada" date NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_ejecutor" (
	"id_ejecutor" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"rut" text NOT NULL,
	"razon_social" text NOT NULL,
	"tipo" text NOT NULL,
	"direccion" text NOT NULL,
	"representante_legal" text NOT NULL,
	"calificacion" numeric(15, 2) NOT NULL,
	"estado" text NOT NULL,
	"correo" text,
	"correo_2" text,
	"telefono" text
);
--> statement-breakpoint
CREATE TABLE "eje_estado_pago" (
	"id_ep" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"monto_solicitado" numeric(15, 2) NOT NULL,
	"monto_aprobado" numeric(15, 2) NOT NULL,
	"fecha_presentacion" date NOT NULL,
	"fecha_aprobacion" date,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_evaluacion_expost" (
	"id_evaluacion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"ipr_id" uuid NOT NULL,
	"fecha" date NOT NULL,
	"metodologia" text NOT NULL,
	"resultado" text NOT NULL,
	"recomendaciones" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_garantia" (
	"id_garantia" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"tipo" text NOT NULL,
	"numero" text NOT NULL,
	"institucion" text NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"fecha_vencimiento" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_hito" (
	"id_hito" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"descripcion" text NOT NULL,
	"fecha_programada" date NOT NULL,
	"fecha_real" date,
	"monto_asociado" numeric(15, 2) NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_informe_avance" (
	"id_informe" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"periodo" text NOT NULL,
	"avance_fisico" numeric(15, 2) NOT NULL,
	"avance_financiero" numeric(15, 2) NOT NULL,
	"observaciones" text NOT NULL,
	"fecha" date NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_liquidacion" (
	"id_liquidacion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"monto_transferido" numeric(15, 2) NOT NULL,
	"monto_rendido" numeric(15, 2) NOT NULL,
	"saldo" numeric(15, 2) NOT NULL,
	"fecha" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "eje_problema" (
	"id_problema" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"ipr_id" uuid NOT NULL,
	"convenio_id" uuid
);
--> statement-breakpoint
CREATE TABLE "eje_visita_terreno" (
	"id_visita" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"fecha" date NOT NULL,
	"inspector_id" uuid NOT NULL,
	"objetivo" text NOT NULL,
	"observaciones" text NOT NULL,
	"avance_fisico" numeric(15, 2) NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_ari" (
	"id_ari" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"periodo_id" uuid NOT NULL,
	"region_id" uuid NOT NULL,
	"monto_total" numeric(15, 2) NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_asignacion" (
	"id_asignacion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"presupuesto_id" uuid NOT NULL,
	"subtitulo" text NOT NULL,
	"item" text NOT NULL,
	"asignacion" text NOT NULL,
	"monto_inicial" numeric(15, 2) NOT NULL,
	"monto_vigente" numeric(15, 2) NOT NULL,
	"monto_ejecutado" numeric(15, 2) NOT NULL,
	"denominacion" text,
	"nombre_linea" text,
	"marca_cm" text
);
--> statement-breakpoint
CREATE TABLE "fin_cdp" (
	"id_cdp" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"numero" text NOT NULL,
	"asignacion_id" uuid NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"fecha_emision" date NOT NULL,
	"fecha_vencimiento" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_compromiso_presupuestario" (
	"id_compromiso" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"cdp_id" uuid NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"fecha" date NOT NULL,
	"descripcion" text NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_contrato" (
	"id_contrato" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"numero" text NOT NULL,
	"proveedor_id" uuid NOT NULL,
	"objeto" text NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"fecha_inicio" date NOT NULL,
	"fecha_termino" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_convenio_programacion" (
	"id_cp" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"ministerio" text NOT NULL,
	"region_id" uuid NOT NULL,
	"monto_total" numeric(15, 2) NOT NULL,
	"fecha_firma" date NOT NULL,
	"vigencia_anios" integer NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_devengo" (
	"id_devengo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"compromiso_id" uuid NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"fecha" date NOT NULL,
	"documento_respaldo" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_eje_estrategico" (
	"id_eje" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"erd_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_erd" (
	"id_erd" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"region_id" uuid NOT NULL,
	"periodo_inicio" integer NOT NULL,
	"periodo_termino" integer NOT NULL,
	"vision" text NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_estado_rate" (
	"codigo" text PRIMARY KEY NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL,
	"permite_financiamiento" boolean NOT NULL,
	"requiere_accion" text,
	"es_terminal" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_fondo" (
	"id_fondo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_garantia_financiera" (
	"id_garantia" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo" text NOT NULL,
	"numero" text NOT NULL,
	"institucion" text NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"fecha_emision" date NOT NULL,
	"fecha_vencimiento" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_idi" (
	"id_idi" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"comuna_id" uuid NOT NULL,
	"division_responsable_id" uuid NOT NULL,
	"codigo_bip" text NOT NULL,
	"nombre" text NOT NULL,
	"tipo" text NOT NULL,
	"etapa_sni" text NOT NULL,
	"monto_solicitado" numeric(15, 2) NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_ipr" (
	"id_ipr" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo_bip" text NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL,
	"tipo" text NOT NULL,
	"mecanismo_id" uuid NOT NULL,
	"monto_total" numeric(15, 2) NOT NULL,
	"comuna_id" uuid NOT NULL,
	"estado_ciclo" text NOT NULL,
	"etapa_actual" text NOT NULL,
	"fecha_rs" date NOT NULL,
	"vigencia" text,
	"tipologia" text,
	"origen" text,
	"fuente" text,
	"sub_estado" text,
	"rate_actual" text,
	"fecha_rate" date,
	"n_rates_emitidos" integer
);
--> statement-breakpoint
CREATE TABLE "fin_licitacion" (
	"id_licitacion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"idi_asociada_id" uuid NOT NULL,
	"codigo_mercado_publico" text NOT NULL,
	"nombre" text NOT NULL,
	"tipo" text NOT NULL,
	"monto_estimado" numeric(15, 2) NOT NULL,
	"fecha_publicacion" date NOT NULL,
	"fecha_cierre" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_linea_ari" (
	"id_linea_ari" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"ari_id" uuid NOT NULL,
	"codigo_linea" text NOT NULL,
	"nombre" text NOT NULL,
	"eje_id" uuid
);
--> statement-breakpoint
CREATE TABLE "fin_mecanismo" (
	"id_mecanismo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo" text NOT NULL,
	"nombre" text NOT NULL,
	"tipo" text NOT NULL,
	"normativa" text NOT NULL,
	"activo" boolean NOT NULL,
	"glosa" text,
	"subtitulo" integer,
	"monto_min" numeric(15, 2),
	"monto_max" numeric(15, 2),
	"requiere_rate" boolean,
	"categorias_validas" text
);
--> statement-breakpoint
CREATE TABLE "fin_medida_temporal" (
	"id_medida" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"periodo_id" uuid NOT NULL,
	"entidad_tipo" text NOT NULL,
	"entidad_id" uuid NOT NULL,
	"asignacion_id" uuid,
	"tipo_medida" text NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"unidad" text
);
--> statement-breakpoint
CREATE TABLE "fin_modificacion_presupuestaria" (
	"id_modificacion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo" text NOT NULL,
	"asignacion_origen_id" uuid NOT NULL,
	"asignacion_destino_id" uuid NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"justificacion" text NOT NULL,
	"acto_id" uuid NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_objetivo_estrategico" (
	"id_objetivo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"eje_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"indicador" text NOT NULL,
	"meta" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_orden_compra" (
	"id_oc" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"numero" text NOT NULL,
	"proveedor_id" uuid NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"fecha_emision" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_ppr" (
	"id_ppr" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo" text NOT NULL,
	"nombre" text NOT NULL,
	"objetivo" text NOT NULL,
	"poblacion_objetivo" text NOT NULL,
	"presupuesto_anual" numeric(15, 2) NOT NULL,
	"periodo_id" uuid NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_presupuesto" (
	"id_presupuesto" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"periodo_id" uuid NOT NULL,
	"ley_presupuesto" text NOT NULL,
	"monto_inicial" numeric(15, 2) NOT NULL,
	"monto_vigente" numeric(15, 2) NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_proveedor" (
	"id_proveedor" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"rut" text NOT NULL,
	"razon_social" text NOT NULL,
	"giro" text NOT NULL,
	"direccion" text NOT NULL,
	"estado_mercado_publico" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_reintegro" (
	"id_reintegro" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"rendicion_id" uuid NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"motivo" text NOT NULL,
	"fecha" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_remesa" (
	"id_remesa" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"transferencia_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"fecha" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_rendicion" (
	"id_rendicion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"monto_rendido" numeric(15, 2) NOT NULL,
	"fecha_presentacion" date NOT NULL,
	"estado" text NOT NULL,
	"correlativo" text,
	"tipo_documento_rendicion" text,
	"fecha_ingreso" date,
	"monto_reintegrado" numeric(15, 2),
	"saldo_pendiente" numeric(15, 2),
	"observado" boolean,
	"rendicion_a_tiempo" boolean,
	"recepcionado_por" text
);
--> statement-breakpoint
CREATE TABLE "fin_serie_financiera" (
	"id_serie" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_transferencia" (
	"id_transferencia" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"convenio_id" uuid NOT NULL,
	"numero_cuota" integer NOT NULL,
	"monto" numeric(15, 2) NOT NULL,
	"fecha" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "fin_via_evaluacion" (
	"id_via" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo" text NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL,
	"normativa" text NOT NULL,
	"aplica_a" text NOT NULL,
	"subtitulo_tipico" integer
);
--> statement-breakpoint
CREATE TABLE "plan_brecha_erd" (
	"id_brecha" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"erd_id" uuid NOT NULL
);
--> statement-breakpoint
CREATE TABLE "geo_capa" (
	"id_capa" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "geo_servicio" (
	"id_servicio" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo" text NOT NULL,
	"url_base" text NOT NULL,
	"version" text NOT NULL,
	"titulo" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "gov_acuerdo_core" (
	"id_acuerdo_core" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"sesion_core_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"materia" text NOT NULL,
	"asunto" text NOT NULL,
	"votos_favor" integer NOT NULL,
	"votos_contra" integer NOT NULL,
	"abstenciones" integer NOT NULL,
	"resultado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "gov_comision" (
	"id_comision" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"core_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"tipo" text NOT NULL,
	"materia" text NOT NULL,
	"presidente_id" uuid NOT NULL,
	"miembros" text NOT NULL,
	"activa" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "gov_comite_coordinacion" (
	"id_comite" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo" text NOT NULL,
	"nombre" text NOT NULL,
	"acto_creacion" text,
	"fecha_creacion" date,
	"presidente_id" uuid,
	"secretario_id" uuid,
	"periodicidad" text,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "gov_consejero" (
	"id_consejero" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"persona_id" uuid NOT NULL,
	"circunscripcion_id" uuid NOT NULL,
	"periodo_inicio" date NOT NULL,
	"periodo_termino" date NOT NULL,
	"partido_politico" text NOT NULL,
	"comisiones" text NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "gov_core" (
	"id_core" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"region_id" uuid NOT NULL,
	"periodo_id" uuid NOT NULL,
	"presidente_id" uuid NOT NULL,
	"vicepresidente_id" uuid NOT NULL,
	"numero_consejeros" integer NOT NULL,
	"quorum_sesion" integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE "gov_gobernador" (
	"id_gobernador" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"persona_id" uuid NOT NULL,
	"region_id" uuid NOT NULL,
	"periodo_inicio" date NOT NULL,
	"periodo_termino" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "gov_sesion_core" (
	"id_sesion_core" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"core_id" uuid NOT NULL,
	"numero" integer NOT NULL,
	"tipo" text NOT NULL,
	"fecha" timestamp NOT NULL,
	"tabla" text NOT NULL,
	"quorum_presente" integer NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "gov_tabla_sesion" (
	"id_tabla" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"sesion_core_id" uuid NOT NULL,
	"numero_punto" integer NOT NULL,
	"materia" text NOT NULL,
	"descripcion" text NOT NULL,
	"estado" text NOT NULL,
	"acuerdo_id" uuid
);
--> statement-breakpoint
CREATE TABLE "gov_transferencia_competencia" (
	"id_transferencia" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"division_receptora_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"ministerio_origen" text NOT NULL,
	"decreto_transferencia" text NOT NULL,
	"fecha_transferencia" date NOT NULL,
	"recursos_asociados" numeric(15, 2) NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "gov_votacion" (
	"id_votacion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"acuerdo_core_id" uuid NOT NULL,
	"consejero_id" uuid NOT NULL,
	"voto" text NOT NULL,
	"fundamento" text
);
--> statement-breakpoint
CREATE TABLE "loc_capa_geoespacial" (
	"id_capa" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"region_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"tipo" text NOT NULL,
	"formato" text NOT NULL,
	"url_servicio" text NOT NULL,
	"srid" integer DEFAULT '4326'
);
--> statement-breakpoint
CREATE TABLE "loc_circunscripcion" (
	"id_circunscripcion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"region_id" uuid NOT NULL,
	"numero_consejeros" integer NOT NULL,
	"comunas" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "loc_comuna" (
	"id_comuna" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo_ine" text NOT NULL,
	"nombre" text NOT NULL,
	"provincia_id" uuid NOT NULL,
	"superficie_km2" numeric(15, 2) NOT NULL,
	"poblacion" integer NOT NULL,
	"tipologia" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "loc_indicador_territorial" (
	"id_indicador" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"dimension" text NOT NULL,
	"valor" numeric(15, 2) NOT NULL,
	"territorio_id" uuid NOT NULL,
	"periodo_id" uuid NOT NULL
);
--> statement-breakpoint
CREATE TABLE "loc_ipt" (
	"id_ipt" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo" text NOT NULL,
	"nombre" text NOT NULL,
	"territorio_id" uuid,
	"region_id" uuid,
	"fecha_aprobacion" date,
	"fecha_vigencia" date
);
--> statement-breakpoint
CREATE TABLE "loc_localidad" (
	"id_localidad" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"comuna_id" uuid NOT NULL,
	"tipo" text NOT NULL,
	"latitud" numeric(15, 2) NOT NULL,
	"longitud" numeric(15, 2) NOT NULL
);
--> statement-breakpoint
CREATE TABLE "loc_prot" (
	"id_prot" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"region_id" uuid NOT NULL,
	"fecha_aprobacion" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "loc_provincia" (
	"id_provincia" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo_ine" text NOT NULL,
	"nombre" text NOT NULL,
	"region_id" uuid NOT NULL
);
--> statement-breakpoint
CREATE TABLE "loc_region" (
	"id_region" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo_ine" text NOT NULL,
	"nombre" text NOT NULL,
	"capital" text NOT NULL,
	"superficie_km2" numeric(15, 2) NOT NULL,
	"poblacion" integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE "loc_zona_geografica" (
	"id_zona" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"tipo" text NOT NULL,
	"region_id" uuid NOT NULL
);
--> statement-breakpoint
CREATE TABLE "loc_zona_riesgo" (
	"id_zona_riesgo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo_riesgo" text NOT NULL,
	"nivel" text NOT NULL,
	"comuna_id" uuid NOT NULL,
	"geometria" text NOT NULL,
	"capa_id" uuid
);
--> statement-breakpoint
CREATE TABLE "norm_audiencia_lobby" (
	"id_audiencia" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"fecha_solicitud" timestamp NOT NULL,
	"fecha_audiencia" timestamp,
	"solicitante_nombre" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_activo" (
	"id_activo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo_inventario" text NOT NULL,
	"descripcion" text NOT NULL,
	"tipo" text NOT NULL,
	"valor_adquisicion" numeric(15, 2) NOT NULL,
	"fecha_adquisicion" date NOT NULL,
	"vida_util_anios" integer NOT NULL,
	"responsable_id" uuid NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_asistencia" (
	"id_asistencia" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"funcionario_id" uuid NOT NULL,
	"fecha" date NOT NULL,
	"hora_entrada" text NOT NULL,
	"hora_salida" text NOT NULL,
	"tipo" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_capacidad" (
	"id_capacidad" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"division_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"tipo" text NOT NULL,
	"nivel_requerido" text NOT NULL,
	"descripcion" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_cargo" (
	"id_cargo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo" text NOT NULL,
	"nombre" text NOT NULL,
	"division_id" uuid NOT NULL,
	"estamento" text NOT NULL,
	"grado_min" integer NOT NULL,
	"grado_max" integer NOT NULL,
	"jefatura" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_cometido" (
	"id_cometido" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"funcionario_id" uuid NOT NULL,
	"destino" text NOT NULL,
	"motivo" text NOT NULL,
	"fecha_inicio" date NOT NULL,
	"fecha_termino" date NOT NULL,
	"viatico" numeric(15, 2) NOT NULL,
	"resolucion" text NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_contrato_honorario" (
	"id_contrato" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"funcionario_id" uuid NOT NULL,
	"numero_contrato" text NOT NULL,
	"objeto" text NOT NULL,
	"monto_bruto" numeric(15, 2) NOT NULL,
	"fecha_inicio" date NOT NULL,
	"fecha_termino" date NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_declaracion_jurada" (
	"id_declaracion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"funcionario_id" uuid NOT NULL,
	"tipo" text NOT NULL,
	"fecha_presentacion" date NOT NULL,
	"periodo_id" uuid NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_division" (
	"id_division" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"codigo" text NOT NULL,
	"nombre" text NOT NULL,
	"sigla" text NOT NULL,
	"tipo" text NOT NULL,
	"division_padre_id" uuid,
	"jefe_id" uuid NOT NULL,
	"nivel_jerarquico" integer NOT NULL,
	"activa" boolean DEFAULT true
);
--> statement-breakpoint
CREATE TABLE "org_dotacion" (
	"id_dotacion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"periodo_id" uuid NOT NULL,
	"calidad_juridica" text NOT NULL,
	"estamento" text NOT NULL,
	"cupos_autorizados" integer NOT NULL,
	"cupos_ocupados" integer NOT NULL,
	"presupuesto_asignado" numeric(15, 2) NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_funcionario" (
	"id_funcionario" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"rut" text NOT NULL,
	"nombres" text NOT NULL,
	"apellido_paterno" text NOT NULL,
	"apellido_materno" text NOT NULL,
	"email_institucional" text NOT NULL,
	"cargo_id" uuid NOT NULL,
	"division_id" uuid NOT NULL,
	"fecha_ingreso" date NOT NULL,
	"calidad_juridica" text NOT NULL,
	"grado" integer NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_inventario" (
	"id_inventario" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"fecha" date NOT NULL,
	"tipo" text NOT NULL,
	"responsable_id" uuid NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_permiso" (
	"id_permiso" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"funcionario_id" uuid NOT NULL,
	"tipo" text NOT NULL,
	"fecha_inicio" date NOT NULL,
	"fecha_termino" date NOT NULL,
	"horas" numeric(15, 2) NOT NULL,
	"motivo" text NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_remuneracion" (
	"id_remuneracion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"funcionario_id" uuid NOT NULL,
	"periodo_id" uuid NOT NULL,
	"sueldo_base" numeric(15, 2) NOT NULL,
	"asignaciones" numeric(15, 2) NOT NULL,
	"descuentos" numeric(15, 2) NOT NULL,
	"liquido" numeric(15, 2) NOT NULL,
	"fecha_pago" date NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_rol" (
	"id_rol" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"plataforma_id" uuid NOT NULL,
	"codigo" text NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL,
	"permisos" text NOT NULL,
	"activo" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_sumario" (
	"id_sumario" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"numero" text NOT NULL,
	"funcionario_id" uuid NOT NULL,
	"fiscal_id" uuid NOT NULL,
	"hechos" text NOT NULL,
	"fecha_inicio" date NOT NULL,
	"sancion" text NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "org_vehiculo" (
	"id_vehiculo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"patente" text NOT NULL,
	"tipo" text NOT NULL,
	"marca" text NOT NULL,
	"modelo" text NOT NULL,
	"anio" integer NOT NULL,
	"kilometraje" integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_alerta" (
	"id_alerta" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo" text NOT NULL,
	"severidad" text NOT NULL,
	"origen" text NOT NULL,
	"mensaje" text NOT NULL,
	"fecha" timestamp NOT NULL,
	"atendida" boolean NOT NULL,
	"ipr_id" uuid,
	"convenio_id" uuid
);
--> statement-breakpoint
CREATE TABLE "sal_aprendizaje" (
	"id_aprendizaje" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"intervencion_id" uuid NOT NULL,
	"tipo" text NOT NULL,
	"descripcion" text NOT NULL,
	"fecha" date NOT NULL,
	"aplicable_a" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_dimension" (
	"id_dimension" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL,
	"peso" numeric(15, 2) NOT NULL,
	"activa" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_equipo_intervencion" (
	"id_equipo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"intervencion_id" uuid NOT NULL,
	"nombre_equipo" text NOT NULL,
	"lider_id" uuid,
	"fecha_conformacion" date NOT NULL,
	"estado" text NOT NULL,
	"miembros" jsonb NOT NULL,
	"recursos_asignados" jsonb
);
--> statement-breakpoint
CREATE TABLE "sal_h_gore" (
	"id_hgore" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"region_id" uuid NOT NULL,
	"periodo_id" uuid NOT NULL,
	"puntaje_global" numeric(15, 2) NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_indicador_poa" (
	"id_indicador" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"poa_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"meta" numeric(15, 2) NOT NULL,
	"actual" numeric(15, 2) NOT NULL,
	"ponderacion" numeric(15, 2) NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_intervencion" (
	"id_intervencion" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"alerta_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL,
	"responsable_id" uuid NOT NULL,
	"fecha_inicio" date NOT NULL,
	"fecha_termino" date,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_key_result" (
	"id_kr" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"okr_id" uuid NOT NULL,
	"descripcion" text NOT NULL,
	"meta" numeric(15, 2) NOT NULL,
	"actual" numeric(15, 2) NOT NULL,
	"unidad" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_okr" (
	"id_okr" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"objetivo" text NOT NULL,
	"periodo_id" uuid NOT NULL,
	"responsable_id" uuid NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_plan_accion" (
	"id_plan" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"intervencion_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"objetivo" text NOT NULL,
	"acciones" text NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_playbook" (
	"id_playbook" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"poa_id" uuid NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL,
	"trigger" text NOT NULL,
	"pasos" text NOT NULL,
	"activo" boolean NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_poa" (
	"id_poa" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"division_id" uuid NOT NULL,
	"periodo_id" uuid NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_puntaje" (
	"id_puntaje" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"hgore_id" uuid NOT NULL,
	"dimension_id" uuid NOT NULL,
	"valor" numeric(15, 2) NOT NULL,
	"fecha_calculo" date NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_riesgo" (
	"id_riesgo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nombre" text NOT NULL,
	"descripcion" text NOT NULL,
	"probabilidad" text NOT NULL,
	"impacto" text NOT NULL,
	"mitigacion" text NOT NULL,
	"responsable_id" uuid NOT NULL,
	"estado" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sal_umbral" (
	"id_umbral" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"dimension_id" uuid NOT NULL,
	"nivel" text NOT NULL,
	"valor_min" numeric(15, 2) NOT NULL,
	"valor_max" numeric(15, 2) NOT NULL,
	"color" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "seg_dispositivo" (
	"id_dispositivo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "seg_incidente" (
	"id_incidente" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sys_acto" (
	"id_acto" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo_acto" text NOT NULL,
	"materia" text NOT NULL,
	"autoridad_id" uuid NOT NULL,
	"fecha_dictacion" date NOT NULL,
	"requiere_toma_razon" boolean NOT NULL,
	"estado_tramitacion" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sys_actor" (
	"id_actor" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo_actor" text NOT NULL,
	"identificador" text NOT NULL,
	"nombre" text NOT NULL,
	"activo" boolean DEFAULT true
);
--> statement-breakpoint
CREATE TABLE "sys_convenio" (
	"id_convenio" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sys_documento" (
	"id_documento" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo_documento" text NOT NULL,
	"numero" text NOT NULL,
	"fecha_emision" date NOT NULL,
	"emisor_id" uuid NOT NULL,
	"hash_contenido" text NOT NULL,
	"estado" text NOT NULL,
	"folio" text,
	"correlativo" text,
	"materia" text,
	"remitente" text,
	"destinatario" text,
	"canal_recepcion_id" uuid,
	"canal_despacho_id" uuid,
	"tiene_adjunto" boolean
);
--> statement-breakpoint
CREATE TABLE "sys_evento" (
	"id_evento" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"tipo_evento" text NOT NULL,
	"fecha_evento" timestamp NOT NULL,
	"actor_id" uuid,
	"entidad_tipo" text,
	"entidad_id" uuid,
	"observacion" text
);
--> statement-breakpoint
CREATE TABLE "sys_identificador_legacy" (
	"id_identificador" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"entidad_tipo" text NOT NULL,
	"entidad_id" uuid NOT NULL,
	"sistema_origen" text NOT NULL,
	"codigo_legacy" text NOT NULL,
	"codigo_tipo" text NOT NULL,
	"hoja_origen" text,
	"fila_origen" integer,
	"hash_fila" text
);
--> statement-breakpoint
CREATE TABLE "sys_periodo" (
	"id_periodo" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"anio" integer NOT NULL,
	"tipo" text NOT NULL,
	"fecha_inicio" date NOT NULL,
	"fecha_fin" date NOT NULL
);
