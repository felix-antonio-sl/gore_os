-- ============================================================================
-- GORE_OS SEED v3.4 - Datos Semilla (Category Schemes)
-- ============================================================================
-- Archivo: goreos_seed.sql
-- Descripción: Datos iniciales para ref.category (83+ schemes) y ref.actor
-- Última actualización: 2026-01-30
-- Fuentes: planclaude.md, especificaciones.md, goreNubleOntology.ttl,
--          goreNubleReferenceData.ttl, tdeCore.ttl, urn:gn:kb:omega-gore-nuble-mermaid
-- ============================================================================
-- Cambios v3.4:
--   +scheme professional_qualification (14 códigos)
--   +scheme cgr_outcome completado (7 códigos)
--   +scheme estamento (7 códigos)
--   +scheme magnitude_aspect (4 códigos)
--   +scheme currency (3 códigos)
-- Total schemes: 83+
-- ============================================================================
-- IDEMPOTENCIA: Este script usa ON CONFLICT para ser ejecutable múltiples veces
-- sin generar errores por duplicados. Cada INSERT actualizará registros existentes.
-- ============================================================================

-- ============================================================================
-- MAPPING ONTOLÓGICO (comentarios de trazabilidad)
-- ============================================================================
-- ref.category ↔ gist:Category (patrón taxonomía flexible)
-- ref.actor ↔ gnub:Actor (participantes proceso DIPIR)
-- scheme='mcd_phase' ↔ gnub:IPRPhase (6 fases F0-F5)
-- scheme='ipr_state' ↔ gnub:IPRState (estados operativos)
-- scheme='mechanism' ↔ gnub:FinancingMechanism (7 tracks)
-- scheme='aspect' ↔ gist:Aspect (7 aspects presupuestarios)
-- scheme='event_type' ↔ gnub:BudgetaryTransaction subclases
-- ============================================================================

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES CORE IPR
-- ============================================================================

-- NATURALEZA IPR (gnub:IPR subclasses mapping)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('ipr_nature', 'PROYECTO', 'Proyecto de Inversión', 'gnub:IPRProject - Capital (Subt 31/33)', 1),
('ipr_nature', 'PROGRAMA', 'Programa Operativo', 'gnub:OperationalProgram - Corriente (Subt 24)', 2),
('ipr_nature', 'PROGRAMA_INVERSION', 'Programa de Inversión', 'gnub:InvestmentProgram', 3),
('ipr_nature', 'ESTUDIO_BASICO', 'Estudio Básico', 'gnub:BasicStudy', 4),
('ipr_nature', 'ANF', 'Adquisición ANF', 'gnub:ANFAcquisition - C33 Activos No Financieros', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPO IPR (clasificación funcional)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('ipr_type', 'INFRAESTRUCTURA', 'Infraestructura', 'Obras de infraestructura pública', 1),
('ipr_type', 'EQUIPAMIENTO', 'Equipamiento', 'Adquisición de equipamiento', 2),
('ipr_type', 'CONSERVACION', 'Conservación', 'Conservación de infraestructura existente', 3),
('ipr_type', 'TRANSFERENCIA', 'Transferencia', 'Transferencias a entidades ejecutoras', 4),
('ipr_type', 'SUBSIDIO', 'Subsidio', 'Subsidios y aportes', 5),
('ipr_type', 'ESTUDIO', 'Estudio', 'Estudios y diseños', 6),
('ipr_type', 'PROGRAMA_SOCIAL', 'Programa Social', 'Programas sociales operativos', 7),
('ipr_type', 'PROGRAMA_8PCT', 'Programa 8%', 'Programa financiado por la subvención FNDR 8%', 8)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- FASES MCD - 6 FASES (CORRECCIÓN ONTOLÓGICA: F0-F5, NO F0-F4)
-- Fuente: goreNubleReferenceData.ttl:145-185, omega:727-835
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('mcd_phase', 'F0', 'Formulación & Ingreso', 'Postulación inicial de la iniciativa', 1),
('mcd_phase', 'F1', 'Admisibilidad', 'The Gatekeeper - verificación requisitos formales', 2),
('mcd_phase', 'F2', 'Evaluación Técnica', 'Poly-Switch - 7 Tracks de evaluación', 3),
('mcd_phase', 'F3', 'Priorización & Asignación', 'CORE - asignación presupuestaria', 4),
('mcd_phase', 'F4', 'Formalización & Ejecución', 'Convenios, contratos, ejecución física/financiera', 5),
('mcd_phase', 'F5', 'Cierre', 'Rendición final y cierre administrativo', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADOS IPR OPERATIVOS (gnub:IPRState subclasses)
-- Fuente: goreNubleOntology.ttl:768-805
-- HIGH-002 FIX: Crear categorías padre dentro del mismo scheme para jerarquía válida
INSERT INTO ref.category (scheme, code, label, description, parent_code, sort_order) VALUES
-- Categorías padre para agrupación (HIGH-002 FIX)
('ipr_state', 'UNIVERSAL', 'Estados Universales', 'gnub:UniversalIPRState - Aplican a todos los tipos de IPR', NULL, 0),
('ipr_state', 'ESTADO_PROYECTO', 'Estados Proyecto', 'gnub:ProjectIPRState - Específicos de proyectos de inversión', NULL, 19),
('ipr_state', 'ESTADO_PROGRAMA', 'Estados Programa', 'gnub:ProgramIPRState - Específicos de programas operativos', NULL, 29),
-- Estados Universales (gnub:UniversalIPRState)
('ipr_state', 'INGRESADO', 'Ingresado', 'Iniciativa ingresada al sistema', 'UNIVERSAL', 1),
('ipr_state', 'EN_REVISION', 'En Revisión', 'Revisión de admisibilidad', 'UNIVERSAL', 2),
('ipr_state', 'PRE_ADMISIBLE', 'Pre-admisible', 'Verificación de admisibilidad en curso', 'UNIVERSAL', 3),
('ipr_state', 'ADMISIBLE', 'Admisible', 'Cumple requisitos formales', 'UNIVERSAL', 4),
('ipr_state', 'INADMISIBLE', 'Inadmisible', 'No cumple requisitos formales', 'UNIVERSAL', 5),
('ipr_state', 'EN_EVALUACION', 'En Evaluación', 'En proceso de evaluación técnica', 'UNIVERSAL', 6),
('ipr_state', 'CDP_EMITIDO', 'CDP Emitido', 'Certificado de disponibilidad presupuestaria emitido', 'UNIVERSAL', 7),
('ipr_state', 'EN_FORMALIZACION', 'En Formalización', 'Preparando convenio/contrato', 'UNIVERSAL', 8),
('ipr_state', 'FORMALIZADO', 'Formalizado', 'Convenio/contrato firmado', 'UNIVERSAL', 9),
('ipr_state', 'EN_EJECUCION', 'En Ejecución', 'Ejecución física y financiera activa', 'UNIVERSAL', 10),
('ipr_state', 'SUSPENDIDO', 'Suspendido', 'Ejecución suspendida temporalmente', 'UNIVERSAL', 11),
('ipr_state', 'EN_RENDICION', 'En Rendición', 'Proceso de rendición de cuentas', 'UNIVERSAL', 12),
('ipr_state', 'CERRADO', 'Cerrado', 'Iniciativa cerrada administrativamente', 'UNIVERSAL', 13),
('ipr_state', 'ANULADO', 'Anulado', 'Iniciativa anulada', 'UNIVERSAL', 14),
-- Estados Proyecto (gnub:ProjectIPRState) - HIGH-002 FIX: parent_code ahora válido
('ipr_state', 'RS', 'RS', 'Rate of Social Return - Tasa Social calculada', 'ESTADO_PROYECTO', 20),
('ipr_state', 'FI', 'FI', 'Favorable Incondicional', 'ESTADO_PROYECTO', 21),
('ipr_state', 'FC', 'FC', 'Favorable Condicional', 'ESTADO_PROYECTO', 22),
('ipr_state', 'OT', 'OT', 'Objetado Técnicamente', 'ESTADO_PROYECTO', 23),
('ipr_state', 'AD', 'AD', 'Autorización de Diseño', 'ESTADO_PROYECTO', 24),
('ipr_state', 'EN_LICITACION', 'En Licitación', 'Proceso de licitación activo', 'ESTADO_PROYECTO', 25),
('ipr_state', 'ADJUDICADO', 'Adjudicado', 'Contrato adjudicado', 'ESTADO_PROYECTO', 26),
('ipr_state', 'EN_OBRA', 'En Obra', 'Ejecución física de obra', 'ESTADO_PROYECTO', 27),
('ipr_state', 'RECEPCION_PROVISORIA', 'Recepción Provisoria', 'Obra con recepción provisoria', 'ESTADO_PROYECTO', 28),
('ipr_state', 'RECEPCION_DEFINITIVA', 'Recepción Definitiva', 'Obra con recepción definitiva', 'ESTADO_PROYECTO', 29),
-- Estados Programa (gnub:ProgramIPRState) - HIGH-002 FIX: parent_code ahora válido
('ipr_state', 'RF', 'RF', 'Recomendación Favorable', 'ESTADO_PROGRAMA', 30),
('ipr_state', 'ITF', 'ITF', 'Informe Técnico Favorable', 'ESTADO_PROGRAMA', 31),
('ipr_state', 'AT', 'AT', 'Aprobación Técnica', 'ESTADO_PROGRAMA', 32),
-- Estados incorporados por la evolución del ciclo de vida
('ipr_state', 'TERMINADO_ANTICIPADAMENTE', 'Terminado Anticipadamente', 'IPR terminada antes de completar su ciclo', 'UNIVERSAL', 30),
('ipr_state', 'CONTRATO_FIRMADO', 'Contrato Firmado', 'Contrato firmado entre GORE y adjudicatario', 'ESTADO_PROYECTO', 33),
('ipr_state', 'RENDICION_APROBADA', 'Rendición Aprobada', 'Ciclo SISREC aprobado; pendiente cierre administrativo', 'UNIVERSAL', 36),
('ipr_state', 'EN_CIERRE_ADMINISTRATIVO', 'En Cierre Administrativo', 'Proceso de cierre formal con acta y firma de autoridad', 'UNIVERSAL', 37)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    parent_code = EXCLUDED.parent_code,
    sort_order = EXCLUDED.sort_order;

-- SUBTÍTULOS PRESUPUESTARIOS
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('budget_subtitle', '21', 'Subtítulo 21', 'Gastos en Personal', 1),
('budget_subtitle', '22', 'Subtítulo 22', 'Bienes y Servicios de Consumo', 2),
('budget_subtitle', '24', 'Subtítulo 24', 'Transferencias Corrientes', 3),
('budget_subtitle', '29', 'Subtítulo 29', 'Adquisición de Activos No Financieros', 4),
('budget_subtitle', '31', 'Subtítulo 31', 'Iniciativas de Inversión', 5),
('budget_subtitle', '33', 'Subtítulo 33', 'Transferencias de Capital', 6),
('budget_subtitle', '34', 'Subtítulo 34', 'Servicio de la Deuda', 7),
('budget_subtitle', '35', 'Subtítulo 35', 'Saldo Final de Caja', 8)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- FUENTES DE FINANCIAMIENTO
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('funding_source', 'FNDR', 'FNDR', 'Fondo Nacional de Desarrollo Regional', 1),
('funding_source', 'SECTORIAL', 'Sectorial', 'Recursos sectoriales ministeriales', 2),
('funding_source', 'PROPIOS', 'Propios', 'Recursos propios del GORE', 3),
('funding_source', 'ROYALTY', 'Royalty', 'Royalty Minero / FRPD', 4),
('funding_source', 'CREDITO', 'Crédito', 'Crédito o endeudamiento', 5),
('funding_source', 'DONACION', 'Donación', 'Donaciones y aportes externos', 6),
-- ONTO-001 FIX (Auditoría v5): Fondos faltantes vs onto_gorenuble
('funding_source', 'FIC', 'FIC', 'gnubd:_Fund_FIC - Fondo de Innovación y Competitividad', 7),
('funding_source', 'FATC', 'FATC', 'gnubd:_Fund_FATC - Fondo de Apoyo al Transporte y Conectividad', 8),
('funding_source', 'FEI', 'FEI', 'gnubd:_Fund_FEI - Fondo de Equidad Interregional', 9),
('funding_source', 'FEIRR', 'FEIRR', 'gnubd:_Fund_FEIRR - Fondo de Inversión y Reconversión Regional', 10),
('funding_source', 'ISAR', 'ISAR', 'gnubd:_Fund_ISAR - Inversiones Sectoriales de Asignación Regional', 11)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- MECANISMOS DE FINANCIAMIENTO - 7 TRACKS (omega:659-724)
-- HIGH-001 FIX: Usar scheme 'mechanism' y códigos directos (SNI, C33, etc.)
-- Alineado con documentación DDL y ontología gnub
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('mechanism', 'SNI', 'Track A: SNI General', '>15k UTM, MDSF evalúa, producto RS', 1),
('mechanism', 'C33', 'Track B: Circular 33', 'C33, conservación/ANF, producto AD', 2),
('mechanism', 'FRIL', 'Track C: FRIL', '<4.545 UTM, GORE evalúa, producto AT', 3),
('mechanism', 'GLOSA06', 'Track D1: Glosa 06', 'Ejecución Directa, DIPRES/SES, producto RF', 4),
('mechanism', 'TRANSFER', 'Track D2: Transferencias', 'Transferencias, Comité GORE, producto ITF', 5),
('mechanism', 'SUBV8', 'Track E1: Subvención 8%', '8% concursable, Comisión, producto Puntaje', 6),
('mechanism', 'FRPD', 'Track E2: FRPD Royalty', 'Royalty I+D+i, ANID/CORFO, producto Elegibilidad', 7)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- CATEGORÍAS CIRCULAR 33 Y ORGANISMO CERTIFICADOR
INSERT INTO ref.category (scheme, code, label, description, metadata, sort_order) VALUES
('categoria_c33', 'EDIFICACION', 'Edificación', 'Proyectos de edificación — certificación SERVIU', '{"certifier_org_code": "SERVIU"}', 1),
('categoria_c33', 'VIALIDAD', 'Vialidad', 'Proyectos viales — certificación MOP', '{"certifier_org_code": "MOP"}', 2)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE IMPACTO TERRITORIAL DE UNA IPR
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('territory_impact', 'UBICACION', 'Ubicación Física', 'Territorio donde se ejecuta físicamente la IPR', 1),
('territory_impact', 'IMPACTO_DIRECTO', 'Impacto Directo', 'Comunas directamente beneficiadas por la IPR', 2),
('territory_impact', 'IMPACTO_INDIRECTO', 'Impacto Indirecto', 'Comunas con efecto spillover de la IPR', 3),
('territory_impact', 'ZONA_INFLUENCIA', 'Zona de Influencia', 'Territorio de usuarios potenciales', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE HITO DEL CICLO IPR
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('milestone_type', 'INICIO_OBRA', 'Inicio de Obras', 'Acta de inicio de construcción', 1),
('milestone_type', 'AVANCE_25', 'Avance 25%', 'Hito de avance físico 25%', 2),
('milestone_type', 'AVANCE_50', 'Avance 50%', 'Hito de avance físico 50%', 3),
('milestone_type', 'AVANCE_75', 'Avance 75%', 'Hito de avance físico 75%', 4),
('milestone_type', 'RECEPCION_PROV', 'Recepción Provisoria', 'Acta de recepción provisoria de obras', 5),
('milestone_type', 'RECEPCION_DEF', 'Recepción Definitiva', 'Acta de recepción definitiva', 6),
('milestone_type', 'CIERRE_ADMIN', 'Cierre Administrativo', 'Cierre administrativo y contable', 7),
('milestone_type', 'ENTREGA_DISENO', 'Entrega de Diseño', 'Entrega de diseño o estudio', 8),
('milestone_type', 'INFORME_FINAL', 'Informe Final', 'Entrega de informe final', 9),
('milestone_type', 'APROBACION_CDP', 'Aprobación CDP', 'Emisión de Certificado de Disponibilidad Presupuestaria', 10),
('milestone_type', 'FIRMA_CONVENIO', 'Firma de Convenio', 'Suscripción del convenio de transferencia', 11),
('milestone_type', 'LICITACION', 'Publicación Licitación', 'Publicación en MercadoPúblico', 12),
('milestone_type', 'ADJUDICACION', 'Adjudicación', 'Resolución de adjudicación', 13)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ROLES DE ORGANIZACIONES PARTICIPANTES EN UNA IPR
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('ipr_party_role', 'POSTULANTE', 'Postulante', 'Organización que postula la iniciativa', 1),
('ipr_party_role', 'FORMULADOR', 'Formulador', 'Organización que formula técnicamente la IPR', 2),
('ipr_party_role', 'EJECUTOR', 'Ejecutor', 'Organización que ejecuta técnica y financieramente', 3),
('ipr_party_role', 'COFINANCIADOR', 'Cofinanciador', 'Organización que aporta recursos adicionales', 4),
('ipr_party_role', 'UNIDAD_TECNICA', 'Unidad Técnica', 'Servicio que supervisa la ejecución', 5),
('ipr_party_role', 'FISCALIZADOR', 'Fiscalizador', 'Organización que fiscaliza el proyecto', 6),
('ipr_party_role', 'BENEFICIARIO', 'Beneficiario Institucional', 'Organización beneficiaria directa', 7),
('ipr_party_role', 'MANDANTE', 'Mandante', 'GORE como mandante en convenio mandato', 8),
('ipr_party_role', 'MANDATARIO', 'Mandatario', 'Organización que recibe el mandato de ejecución', 9)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ASPECTOS PRESUPUESTARIOS - 7 ASPECTS (goreNubleOntology.ttl:376-433)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('aspect', 'BUDGETED_AMOUNT', 'Monto Presupuestado', 'gnub:BudgetedAmountAspect - Monto inicial ley', 1),
('aspect', 'CURRENT_BUDGET', 'Presupuesto Vigente', 'gnub:CurrentBudgetAspect - Presupuesto actual', 2),
('aspect', 'PRE_COMMITTED', 'Pre-Comprometido', 'gnub:PreCommittedAmountAspect - CDPs emitidos', 3),
('aspect', 'COMMITTED', 'Comprometido', 'gnub:CommittedAmountAspect - OC/Contratos', 4),
('aspect', 'ACCRUED', 'Devengado', 'gnub:AccruedAmountAspect - Devengado', 5),
('aspect', 'PAID', 'Pagado', 'gnub:PaidAmountAspect - Pagos efectuados', 6),
('aspect', 'AVAILABLE_BALANCE', 'Saldo Disponible', 'gnub:AvailableBalanceAspect - Disponible', 7),
-- MED-002: Aspects no-financieros adicionales para métricas de gestión
('aspect', 'PHYSICAL_PROGRESS', 'Avance Físico', 'Porcentaje de avance físico de obra/proyecto', 10),
('aspect', 'FINANCIAL_PROGRESS', 'Avance Financiero', 'Porcentaje de ejecución financiera', 11),
('aspect', 'BENEFICIARIES', 'Beneficiarios', 'Cantidad de beneficiarios directos', 12),
('aspect', 'JOBS_CREATED', 'Empleos Creados', 'Empleos generados por el proyecto', 13),
('aspect', 'EXECUTION_DAYS', 'Días de Ejecución', 'Días transcurridos desde inicio de ejecución', 14)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- MED-001: UNIDADES DE MEDIDA para Magnitude Pattern (gist:UnitOfMeasure)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('unit', 'CLP', 'Peso Chileno', 'Moneda nacional - peso chileno', 1),
('unit', 'UTM', 'UTM', 'Unidad Tributaria Mensual', 2),
('unit', 'UF', 'UF', 'Unidad de Fomento', 3),
('unit', 'USD', 'Dólar US', 'Dólar estadounidense', 4),
('unit', 'PERCENT', 'Porcentaje', 'Valor porcentual (0-100)', 5),
('unit', 'COUNT', 'Conteo', 'Unidades enteras/cantidad', 6),
('unit', 'DAYS', 'Días', 'Días calendario', 7),
('unit', 'MONTHS', 'Meses', 'Meses calendario', 8),
('unit', 'KM2', 'Kilómetros²', 'Superficie en kilómetros cuadrados', 9),
('unit', 'M2', 'Metros²', 'Superficie en metros cuadrados', 10),
('unit', 'ML', 'Metros lineales', 'Metros lineales de obra', 11),
('unit', 'HABITANTES', 'Habitantes', 'Cantidad de habitantes', 12)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE EVENTO (gnub:BudgetaryTransaction subclasses + operativos)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('event_type', 'CDP', 'Pre-Compromiso CDP', 'gnub:PreCommitmentEvent - Certificado disponibilidad', 1),
('event_type', 'COMPROMISO', 'Compromiso', 'gnub:CommitmentEvent - OC/Contrato', 2),
('event_type', 'DEVENGO', 'Devengo', 'gnub:AccrualEvent - Obligación devengada', 3),
('event_type', 'PAGO', 'Pago', 'gnub:PaymentEvent - Pago efectuado', 4),
('event_type', 'MODIFICACION', 'Modificación Presupuestaria', 'Ajuste presupuestario', 5),
('event_type', 'STATE_TRANSITION', 'Transición de Estado', 'gnub:IPRStateTransition', 6),
('event_type', 'CREACION', 'Creación', 'Evento de creación de entidad', 7),
('event_type', 'ACTUALIZACION', 'Actualización', 'Evento de actualización', 8),
('event_type', 'ASIGNACION', 'Asignación', 'Asignación de responsable', 9),
('event_type', 'APROBACION', 'Aprobación', 'Evento de aprobación', 10),
('event_type', 'RECHAZO', 'Rechazo', 'Evento de rechazo', 11),
('event_type', 'CIERRE', 'Cierre', 'Evento de cierre', 12),
-- TDE-002 FIX (Auditoría v5): Acciones de trazabilidad TDE (Art. 11 DS N°10)
('event_type', 'ACCESO', 'Acceso', 'tde:TipoAccionTrazabilidad - Acceso a documento/expediente', 13),
('event_type', 'ELIMINACION', 'Eliminación', 'tde:TipoAccionTrazabilidad - Eliminación lógica de documento', 14),
('event_type', 'INCORPORACION', 'Incorporación', 'tde:TipoAccionTrazabilidad - Incorporación de documento a expediente', 15),
('event_type', 'TRANSFERENCIA', 'Transferencia', 'tde:TipoAccionTrazabilidad - Transferencia de expediente entre OAE', 16)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES ACTOS ADMINISTRATIVOS
-- ============================================================================

-- TIPOS DE ACTO ADMINISTRATIVO
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('act_type', 'RESOLUCION', 'Resolución', 'gnub:Resolution - Acto resolutivo', 1),
('act_type', 'DECRETO', 'Decreto', 'gnub:Decree - Acto decreto', 2),
('act_type', 'OFICIO', 'Oficio', 'Comunicación oficial', 3),
('act_type', 'CERTIFICADO', 'Certificado', 'Certificación oficial', 4),
('act_type', 'INFORME', 'Informe', 'Informe técnico o administrativo', 5),
('act_type', 'DECRETO_ALCALDICIO', 'Decreto Alcaldicio', 'gnub:MunicipalDecree - Acto alcaldicio por mandato', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADOS DE ACTO ADMINISTRATIVO
INSERT INTO ref.category (scheme, code, label, sort_order) VALUES
('act_state', 'BORRADOR', 'Borrador', 1),
('act_state', 'EN_REVISION', 'En Revisión', 2),
('act_state', 'VISADO', 'Visado', 3),
('act_state', 'FIRMADO', 'Firmado', 4),
('act_state', 'ENVIADO_CGR', 'Enviado a CGR', 5),
('act_state', 'OBSERVADO', 'Observado por CGR', 6),
('act_state', 'TOMADO_RAZON', 'Toma de Razón', 7),
('act_state', 'RECHAZADO_CGR', 'Rechazado CGR', 8),
('act_state', 'ANULADO', 'Anulado', 9)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE RESOLUCIÓN
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('resolution_type', 'APROBATORIA', 'Aprobatoria', 'Aprueba proyecto/convenio', 1),
('resolution_type', 'MODIFICATORIA', 'Modificatoria', 'Modifica resolución anterior', 2),
('resolution_type', 'DEROGATORIA', 'Derogatoria', 'Deroga resolución anterior', 3),
('resolution_type', 'SANCIONATORIA', 'Sancionatoria', 'Aplica sanción', 4),
('resolution_type', 'DESIGNACION', 'Designación', 'Designa funcionario/comisión', 5),
('resolution_type', 'DELEGACION', 'Delegación', 'Delega facultades', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
-- SCHEME: cgr_outcome (v3.4 - completado)
-- DESCRIPCIÓN: Estados ante Contraloría General de la República (tde:EstadoCGR)
-- ============================================================================
INSERT INTO ref.category (scheme, code, label, description, metadata, sort_order) VALUES
('cgr_outcome', 'TOMA_RAZON', 'Toma de Razón', 'CGR aprueba', '{"ontology": "tde:EstadoCGR"}', 1),
('cgr_outcome', 'REPRESENTA', 'Representa', 'CGR rechaza', '{"ontology": "tde:EstadoCGR"}', 2),
('cgr_outcome', 'TR_CON_ALCANCES', 'Toma de Razón con Alcances', 'CGR aprueba con observaciones menores', '{"ontology": "tde:EstadoCGR"}', 3),
('cgr_outcome', 'EN_CGR', 'En Contraloría', 'En proceso de toma de razón', '{"ontology": "tde:EstadoCGR"}', 4),
('cgr_outcome', 'CURSA_OBS', 'Cursa con Observaciones', 'CGR aprueba con observaciones', '{"ontology": "tde:EstadoCGR"}', 5),
('cgr_outcome', 'EXENTO', 'Exento', 'No requiere toma de razón', '{"ontology": "tde:EstadoCGR"}', 6),
('cgr_outcome', 'RETIRO', 'Retiro', 'GORE retira para corrección', '{"ontology": "tde:EstadoCGR"}', 7)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES ORGANIZACIÓN
-- ============================================================================

-- TIPOS DE ORGANIZACIÓN
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('org_type', 'GORE', 'GORE', 'Gobierno Regional', 1),
('org_type', 'DIVISION', 'División', 'División funcional GORE', 2),
('org_type', 'DEPARTAMENTO', 'Departamento', 'Departamento dentro de División', 3),
('org_type', 'UNIDAD', 'Unidad', 'Unidad operativa', 4),
('org_type', 'MUNICIPALIDAD', 'Municipalidad', 'Municipalidad comunal', 5),
('org_type', 'SERVICIO', 'Servicio Público', 'Servicio público desconcentrado', 6),
('org_type', 'MINISTERIO', 'Ministerio', 'Ministerio sectorial', 7),
('org_type', 'UNIVERSIDAD', 'Universidad', 'Institución educación superior', 8),
('org_type', 'ONG', 'ONG', 'Organización sin fines de lucro', 9),
('org_type', 'EMPRESA', 'Empresa', 'Entidad privada', 10),
('org_type', 'STAFF_UNIT', 'Unidad de Staff', 'Dependencia directa del Gobernador/a o Administrador/a Regional', 11),
('org_type', 'ADVISORY_BODY', 'Cuerpo Asesor', 'Órgano colegiado de asesoría (COSOC, CTCI, CDR)', 12),
('org_type', 'ORG_COMUNITARIA', 'Organización Comunitaria', 'Organización de la sociedad civil', 13),
('org_type', 'COMUNITARIA', 'Comunidad', 'Comunidad territorial', 14)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE PERSONA
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('person_type', 'FUNCIONARIO', 'Funcionario', 'Funcionario GORE', 1),
('person_type', 'CONTRATA', 'Contrata', 'Personal a contrata', 2),
('person_type', 'HONORARIO', 'Honorarios', 'Profesional a honorarios', 3),
('person_type', 'EXTERNO', 'Externo', 'Persona externa', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE INVENTARIO
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('inventory_type', 'VEHICULO', 'Vehículo', 'Vehículo institucional', 1),
('inventory_type', 'MOBILIARIO', 'Mobiliario', 'Mobiliario de oficina', 2),
('inventory_type', 'EQUIPO_TI', 'Equipo TI', 'Equipamiento tecnológico', 3),
('inventory_type', 'MAQUINARIA', 'Maquinaria', 'Maquinaria y equipos', 4),
('inventory_type', 'INMUEBLE', 'Inmueble', 'Bien raíz', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES TERRITORIO
-- ============================================================================

-- TIPOS DE TERRITORIO
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('territory_type', 'REGION', 'Región', 'Región administrativa', 1),
('territory_type', 'PROVINCIA', 'Provincia', 'Provincia', 2),
('territory_type', 'COMUNA', 'Comuna', 'Comuna o municipio', 3),
('territory_type', 'LOCALIDAD', 'Localidad', 'Localidad o sector', 4),
('territory_type', 'ZONA', 'Zona', 'Zona de planificación', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE INDICADOR TERRITORIAL
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('indicator_type', 'DEMOGRAFICO', 'Demográfico', 'Indicadores de población', 1),
('indicator_type', 'ECONOMICO', 'Económico', 'Indicadores económicos', 2),
('indicator_type', 'SOCIAL', 'Social', 'Indicadores sociales', 3),
('indicator_type', 'AMBIENTAL', 'Ambiental', 'Indicadores ambientales', 4),
('indicator_type', 'INFRAESTRUCTURA', 'Infraestructura', 'Indicadores de infraestructura', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES CONVENIOS
-- ============================================================================

-- TIPOS DE CONVENIO (gnub:GOREAgreement subclasses)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('agreement_type', 'MANDATO', 'Mandato', 'gnub:MandateAgreement - Convenio mandato', 1),
('agreement_type', 'TRANSFERENCIA', 'Transferencia', 'gnub:TransferAgreement - Transferencia de recursos', 2),
('agreement_type', 'COLABORACION', 'Colaboración', 'Convenio de colaboración', 3),
('agreement_type', 'PROGRAMACION', 'Programación', 'Convenio de programación', 4),
('agreement_type', 'MARCO', 'Marco', 'Convenio marco', 5),
('agreement_type', 'EJECUCION', 'Ejecución', 'Convenio de ejecución directa', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADOS DE CONVENIO
INSERT INTO ref.category (scheme, code, label, sort_order) VALUES
('agreement_state', 'BORRADOR', 'Borrador', 1),
('agreement_state', 'EN_NEGOCIACION', 'En Negociación', 2),
('agreement_state', 'EN_REVISION_JURIDICA', 'En Revisión Jurídica', 3),
('agreement_state', 'FIRMADO_GORE', 'Firmado GORE', 4),
('agreement_state', 'FIRMADO_CONTRAPARTE', 'Firmado Contraparte', 5),
('agreement_state', 'FORMALIZADO', 'Formalizado', 6),
('agreement_state', 'VIGENTE', 'Vigente', 7),
('agreement_state', 'EN_MODIFICACION', 'En Modificación', 8),
('agreement_state', 'VENCIDO', 'Vencido', 9),
('agreement_state', 'TERMINADO', 'Terminado', 10),
('agreement_state', 'RESCILIADO', 'Resciliado', 11)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE COMITÉ
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('committee_type', 'CORE', 'CORE', 'Consejo Regional', 1),
('committee_type', 'COMISION', 'Comisión', 'Comisión permanente o ad-hoc', 2),
('committee_type', 'COMITE_TECNICO', 'Comité Técnico', 'Comité técnico de evaluación', 3),
('committee_type', 'MESA_TRABAJO', 'Mesa de Trabajo', 'Mesa de trabajo intersectorial', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- GOBERNANZA DE SESIONES Y VOTACIÓN
-- Catálogos estructurales requeridos por core.session y core.session_vote.
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('session_type', 'ORDINARIA', 'Sesión Ordinaria', 'Sesión ordinaria del órgano colegiado', 1),
('session_type', 'EXTRAORDINARIA', 'Sesión Extraordinaria', 'Sesión extraordinaria del órgano colegiado', 2),
('session_type', 'CRISIS', 'Sesión de Crisis', 'Sesión extraordinaria para gestión de crisis', 3),
('vote_option', 'A_FAVOR', 'A Favor', 'Voto favorable', 1),
('vote_option', 'EN_CONTRA', 'En Contra', 'Voto desfavorable', 2),
('vote_option', 'ABSTENCION', 'Abstención', 'Abstención de voto', 3),
('quorum_type', 'SIMPLE', 'Mayoría Simple (9/16)', 'Mayoría simple del CORE', 1),
('quorum_type', 'CALIFICADA', 'Mayoría Calificada (11/16)', 'Mayoría calificada del CORE', 2)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES RENDICIÓN (ONTO-003 FIX Auditoría v5)
-- ============================================================================
-- Fuente: goreNubleReferenceData.ttl + flujo SISREC RTF→UCR

-- ESTADOS DE RENDICIÓN (gnub:AccountabilityState)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('rendition_state', 'PENDIENTE', 'Pendiente', 'gnubd:_AccountabilityState_Pending - Rendición pendiente de inicio', 1),
('rendition_state', 'EN_REVISION_RTF', 'En Revisión RTF', 'Revisión técnica por Referente Técnico Financiero', 2),
('rendition_state', 'VISADA_RTF', 'Visada RTF', 'Rendición visada por RTF, pendiente de UCR', 3),
('rendition_state', 'EN_REVISION_UCR', 'En Revisión UCR', 'Revisión final por Unidad de Control de Rendiciones', 4),
('rendition_state', 'OBSERVADA', 'Observada', 'gnubd:_AccountabilityState_Observed - Con observaciones a subsanar', 5),
('rendition_state', 'APROBADA', 'Aprobada', 'gnubd:_AccountabilityState_Approved - Rendición aprobada', 6),
('rendition_state', 'APROBADA_PARCIALMENTE', 'Aprobada Parcialmente', 'Rendición con aprobación parcial - requiere complemento', 7),
('rendition_state', 'RECHAZADA', 'Rechazada', 'gnubd:_AccountabilityState_Rejected - Rendición rechazada', 8),
('rendition_state', 'EN_REVISION', 'En Revisión (legado)', 'DEPRECADO: reemplazado por EN_REVISION_RTF/EN_REVISION_UCR', 99)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES EVALUACIÓN (ONTO-004 FIX Auditoría v5)
-- ============================================================================
-- Fuente: goreNubleReferenceData.ttl - gnub:EvaluationResult (6 instancias)
-- Nota: Estos son RESULTADOS de evaluación, distintos de ESTADOS de IPR

-- RESULTADOS DE EVALUACIÓN (gnub:EvaluationResult)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('evaluation_result', 'RS', 'Rentabilidad Social', 'gnubd:_EvalResult_RS - Tasa de retorno social calculada (MDSF)', 1),
('evaluation_result', 'FI', 'Falta Información', 'gnubd:_EvalResult_FI - Subsanar documentación o antecedentes', 2),
('evaluation_result', 'OT', 'Observaciones Técnicas', 'gnubd:_EvalResult_OT - Subsanar aspectos técnicos del proyecto', 3),
('evaluation_result', 'RF', 'Recomendado Favorable', 'gnubd:_EvalResult_RF - DIPRES recomienda favorablemente (Glosa06)', 4),
('evaluation_result', 'ITF', 'Informe Técnico Favorable', 'gnubd:_EvalResult_ITF - GORE emite ITF (programas)', 5),
('evaluation_result', 'AD', 'Admisible', 'gnubd:_EvalResult_AD - Elegible para FRIL (<5k UTM)', 6),
('evaluation_result', 'ELEGIBLE', 'Elegible', 'Elegible para financiamiento FRPD/CTCI', 7),
('evaluation_result', 'NV', 'No Viable', 'Proyecto no viable técnica o financieramente', 8),
('evaluation_result', 'PUNTAJE', 'Puntaje', 'Evaluación por puntaje (ranking competitivo)', 9),
('evaluation_result', 'AT', 'Aprobación Técnica', 'Aprobación técnica sin cálculo de RS', 10)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- EVALUACIÓN EX-POST DE IPR CERRADAS
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('expost_eval_type', 'SIMPLIFICADA', 'Simplificada', 'Evaluación simplificada de resultados', 1),
('expost_eval_type', 'PROFUNDIDAD', 'En Profundidad', 'Evaluación detallada de impacto y sostenibilidad', 2),
('expost_eval_type', 'IMPACTO', 'De Impacto', 'Evaluación de impacto socioeconómico a largo plazo', 3),
('expost_rating', 'EXITOSO', 'Exitoso', 'IPR cumplió y superó objetivos planificados', 1),
('expost_rating', 'SATISFACTORIO', 'Satisfactorio', 'IPR cumplió objetivos principales', 2),
('expost_rating', 'PARCIAL', 'Parcialmente Satisfactorio', 'IPR cumplió parcialmente sus objetivos', 3),
('expost_rating', 'INSATISFACTORIO', 'Insatisfactorio', 'IPR no cumplió objetivos mínimos', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES DIGITAL
-- ============================================================================

-- TIPOS DE PLATAFORMA (tde:TipoPlataforma)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('platform_type', 'TRANSACCIONAL', 'Transaccional', 'Plataforma de trámites', 1),
('platform_type', 'INTEGRACION', 'Integración', 'Plataforma de interoperabilidad', 2),
('platform_type', 'DATOS', 'Datos', 'Plataforma de datos', 3),
('platform_type', 'IDENTIDAD', 'Identidad', 'Plataforma de identidad digital', 4),
('platform_type', 'DOCUMENTAL', 'Documental', 'Gestión documental', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE TRÁMITE (tde:TipoServicioDigital)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('procedure_type', 'SOLICITUD', 'Solicitud', 'Solicitud de servicio/beneficio', 1),
('procedure_type', 'CERTIFICADO', 'Certificado', 'Emisión de certificado', 2),
('procedure_type', 'PERMISO', 'Permiso', 'Autorización o permiso', 3),
('procedure_type', 'INSCRIPCION', 'Inscripción', 'Inscripción en registro', 4),
('procedure_type', 'RECLAMO', 'Reclamo', 'Reclamo o apelación', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADOS DE EXPEDIENTE (tde:EstadoTramite)
INSERT INTO ref.category (scheme, code, label, sort_order) VALUES
('file_status', 'INICIADO', 'Iniciado', 1),
('file_status', 'EN_TRAMITE', 'En Trámite', 2),
('file_status', 'PENDIENTE_INFO', 'Pendiente Información', 3),
('file_status', 'EN_FIRMA', 'En Firma', 4),
('file_status', 'RESUELTO', 'Resuelto', 5),
('file_status', 'ARCHIVADO', 'Archivado', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES ALERTAS Y RIESGOS
-- ============================================================================

-- TIPOS DE ALERTA (especificaciones.md RF-050)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('alert_type', 'CUOTA_VENCIDA', 'Cuota Vencida', 'Cuota de pago vencida', 1),
('alert_type', 'CUOTA_PROXIMA', 'Cuota Próxima', 'Cuota próxima a vencer (7 días)', 2),
('alert_type', 'CONVENIO_POR_VENCER', 'Convenio por Vencer', 'Convenio próximo a vencer (30 días)', 3),
('alert_type', 'CONVENIO_VENCIDO', 'Convenio Vencido', 'Convenio vencido', 4),
('alert_type', 'TRABAJO_VENCIDO', 'Trabajo Vencido', 'Ítem de trabajo vencido', 5),
('alert_type', 'TRABAJO_BLOQUEADO_LARGO', 'Trabajo Bloqueado Largo', 'Ítem bloqueado > 7 días', 6),
('alert_type', 'PROBLEMA_SIN_GESTION', 'Problema Sin Gestión', 'Problema abierto > 3 días sin trabajo', 7),
('alert_type', 'RENDICION_PENDIENTE', 'Rendición Pendiente', 'Rendición pendiente', 8),
('alert_type', 'OBRA_SIN_PAGO', 'Obra Sin Pago', 'Avance >= 95%, pago pendiente', 9),
('alert_type', 'PLAZO_LEGAL', 'Plazo Legal', 'Vencimiento de plazo legal', 10),
('alert_type', 'CDP_POR_VENCER', 'CDP por Vencer', 'CDP próximo a vencer', 11),
('alert_type', 'PRESUPUESTO_BAJO', 'Presupuesto Bajo', 'Saldo presupuestario bajo umbral', 12)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- NIVELES DE ALERTA (severidad)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('alert_level', 'INFO', 'Informativo', 'Alerta informativa', 1),
('alert_level', 'ATENCION', 'Atención', 'Requiere atención', 2),
('alert_level', 'ALTO', 'Alto', 'Alta prioridad', 3),
('alert_level', 'CRITICO', 'Crítico', 'Acción inmediata requerida', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE RIESGO
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('risk_type', 'FINANCIERO', 'Financiero', 'Riesgo financiero o presupuestario', 1),
('risk_type', 'OPERACIONAL', 'Operacional', 'Riesgo de ejecución', 2),
('risk_type', 'LEGAL', 'Legal', 'Riesgo legal o normativo', 3),
('risk_type', 'REPUTACIONAL', 'Reputacional', 'Riesgo de imagen', 4),
('risk_type', 'TECNICO', 'Técnico', 'Riesgo técnico', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- PROBABILIDAD DE RIESGO
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('risk_probability', 'MUY_BAJA', 'Muy Baja', 'Probabilidad <10%', 1),
('risk_probability', 'BAJA', 'Baja', 'Probabilidad 10-30%', 2),
('risk_probability', 'MEDIA', 'Media', 'Probabilidad 30-60%', 3),
('risk_probability', 'ALTA', 'Alta', 'Probabilidad 60-85%', 4),
('risk_probability', 'MUY_ALTA', 'Muy Alta', 'Probabilidad >85%', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADOS DE RIESGO
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('risk_status', 'IDENTIFICADO', 'Identificado', 'Riesgo detectado, pendiente evaluación', 1),
('risk_status', 'EN_EVALUACION', 'En Evaluación', 'Evaluando impacto y probabilidad', 2),
('risk_status', 'EN_MITIGACION', 'En Mitigación', 'Plan de mitigación en ejecución', 3),
('risk_status', 'MITIGADO', 'Mitigado', 'Acciones de mitigación completadas', 4),
('risk_status', 'ACEPTADO', 'Aceptado', 'Riesgo aceptado sin mitigación', 5),
('risk_status', 'CERRADO', 'Cerrado', 'Riesgo ya no aplica', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES ESPECIFICACIONES.MD (NUEVOS)
-- ============================================================================

-- ÍTEMS PRESUPUESTARIOS (clasificación DIPRES)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('budget_item', 'PERSONAL', 'Personal', 'Gastos en personal (Subtítulo 21)', 1),
('budget_item', 'BIENES_SERVICIOS', 'Bienes y Servicios', 'Bienes y servicios de consumo (Subtítulo 22)', 2),
('budget_item', 'TRANSFERENCIAS_CTES', 'Transferencias Corrientes', 'Transferencias corrientes (Subtítulo 24)', 3),
('budget_item', 'ADQUIS_ACTIVOS_NF', 'Activos No Financieros', 'Adquisición de activos no financieros (Subtítulo 29)', 4),
('budget_item', 'INV_REAL', 'Inversión Real', 'Iniciativas de inversión (Subtítulo 31)', 5),
('budget_item', 'INV_FINANCIERA', 'Inversión Financiera', 'Inversión financiera', 6),
('budget_item', 'TRANSF_CAPITAL', 'Transferencias de Capital', 'Transferencias de capital (Subtítulo 33)', 7),
('budget_item', 'DEUDA', 'Servicio de Deuda', 'Servicio de la deuda (Subtítulo 34)', 8),
('budget_item', 'SALDO_CAJA', 'Saldo de Caja', 'Saldo final de caja (Subtítulo 35)', 9),
('budget_item', 'PRESTAMOS', 'Préstamos', 'Préstamos otorgados', 10),
('budget_item', 'OTROS_GASTOS', 'Otros Gastos', 'Otros gastos varios', 11),
('budget_item', 'INTEGROS_FISCO', 'Íntegros al Fisco', 'Devoluciones al fisco', 12),
('budget_item', 'APORTES_FISCAL', 'Aportes Fiscales', 'Aportes fiscales recibidos', 13),
('budget_item', 'PROVISIONES', 'Provisiones', 'Provisiones presupuestarias', 14)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ASIGNACIONES PRESUPUESTARIAS
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('budget_allocation', 'FNDR_EQUIPAMIENTO', 'FNDR Equipamiento', 'Asignación FNDR para equipamiento', 1),
('budget_allocation', 'FNDR_INFRAESTRUCTURA', 'FNDR Infraestructura', 'Asignación FNDR para infraestructura', 2),
('budget_allocation', 'FNDR_PROGRAMA_SOCIAL', 'FNDR Programa Social', 'Asignación FNDR para programas sociales', 3),
('budget_allocation', 'FNDR_ESTUDIO', 'FNDR Estudio', 'Asignación FNDR para estudios', 4),
('budget_allocation', 'FNDR_8PCT', 'FNDR 8% Cultural/Deporte', 'Asignación FNDR Ley 8%', 5),
('budget_allocation', 'SECT_MINVU', 'Sectorial MINVU', 'Recursos sectoriales MINVU', 6),
('budget_allocation', 'SECT_MOP', 'Sectorial MOP', 'Recursos sectoriales MOP', 7),
('budget_allocation', 'SECT_EDUCACION', 'Sectorial Educación', 'Recursos sectoriales educación', 8),
('budget_allocation', 'SECT_SALUD', 'Sectorial Salud', 'Recursos sectoriales salud', 9),
('budget_allocation', 'PROPIOS_OPERACION', 'Propios Operación', 'Recursos propios operación corriente', 10),
('budget_allocation', 'PROPIOS_EMERGENCIA', 'Propios Emergencia', 'Recursos propios emergencias', 11),
('budget_allocation', 'ROYALTY_INVERSION', 'Royalty Inversión', 'Royalty destinado a inversión', 12),
('budget_allocation', 'FIC_INNOVACION', 'FIC Innovación', 'Fondo de Innovación y Competitividad', 13),
('budget_allocation', 'ISAR_ASIGNACION', 'ISAR Asignación', 'Inversiones Sectoriales de Asignación Regional', 14),
('budget_allocation', 'FEIRR_RECONVERSION', 'FEIRR Reconversión', 'Fondo de Inversión y Reconversión Regional', 15)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE PROGRAMA PRESUPUESTARIO
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('program_type', 'PPR_INVERSION', 'Programa Inversión', 'Programa presupuestario de inversión', 1),
('program_type', 'PPR_FUNCIONAMIENTO', 'Programa Funcionamiento', 'Programa presupuestario de funcionamiento', 2),
('program_type', 'PPR_TRANSFERENCIA', 'Programa Transferencia', 'Programa presupuestario de transferencias', 3),
('program_type', 'PPR_PROGRAMA', 'Programa Social/Fomento', 'Programa presupuestario social o de fomento', 4),
('program_type', 'PPR_PROVISIONES', 'Provisiones', 'Programa presupuestario de provisiones', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADOS DE COMPROMISO PRESUPUESTARIO (CDP)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('budget_commitment_status', 'EMITIDO', 'Emitido', 'CDP emitido, pendiente de validación', 1),
('budget_commitment_status', 'VIGENTE', 'Vigente', 'CDP vigente y activo', 2),
('budget_commitment_status', 'EJECUTADO', 'Ejecutado', 'CDP totalmente ejecutado', 3),
('budget_commitment_status', 'ANULADO', 'Anulado', 'CDP anulado', 4),
('budget_commitment_status', 'VENCIDO', 'Vencido', 'CDP vencido sin ejecución', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ROLES DEL SISTEMA — 15 roles alineados con SSOT organica + organigrama
-- sort_order 4 (ex-ENCARGADO) vacante deliberadamente para evitar cascada
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('system_role', 'GOBERNADOR', 'Gobernador Regional', 'Autoridad ejecutiva máxima. Firma actos, preside CORE', 0),
('system_role', 'ADMIN_SISTEMA', 'Administrador del Sistema', 'Configura sistema, usuarios, importa datos', 1),
('system_role', 'ADMIN_REGIONAL', 'Administrador Regional', 'Visión 360°, coordina divisiones, gestiona crisis', 2),
('system_role', 'JEFE_DIVISION', 'Jefe de División', 'Supervisa división, verifica trabajo, asigna', 3),
('system_role', 'JEFE_DGI', 'Jefe DGI', 'Dirige Departamento de Gestión Institucional, decide escalamientos', 5),
('system_role', 'ESP_CONTROL_GESTION', 'Especialista Control de Gestión', 'Monitorea indicadores, valida datos, genera alertas', 6),
('system_role', 'ESP_PROCESOS', 'Especialista Procesos', 'Levanta procesos BPMN, gestiona mejora continua DMAIC', 7),
('system_role', 'ESP_TD', 'Especialista Transformación Digital', 'Monitorea cumplimiento Ley 21.180, gestiona KB', 8),
('system_role', 'CONSEJERO_REGIONAL', 'Consejero Regional', 'Miembro del Consejo Regional, vota IPRs >7K UTM', 9),
('system_role', 'SECRETARIO_EJECUTIVO', 'Secretario Ejecutivo', 'Secretaría Ejecutiva del CORE, prepara agenda y actas', 10),
('system_role', 'JEFE_DEPARTAMENTO', 'Jefe de Departamento', 'Supervisa departamento dentro de una división', 11),
('system_role', 'JEFE_UNIDAD', 'Jefe de Unidad', 'Supervisa unidad operativa', 12),
('system_role', 'ANALISTA', 'Analista', 'Formula IPR F0-F3, evalúa admisibilidad, registra evaluaciones', 13),
('system_role', 'RTF', 'Referente Técnico-Financiero', 'Analista Otorgante SISREC, revisa rendiciones 7d SLA', 14),
('system_role', 'ASESOR_JURIDICO', 'Asesor Jurídico', 'V.B. legalidad de actos administrativos y convenios', 15)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADOS DE WORK_ITEM (RF-022)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('work_item_status', 'PENDIENTE', 'Pendiente', 'Trabajo por iniciar', 1),
('work_item_status', 'EN_PROGRESO', 'En Progreso', 'Trabajo en ejecución', 2),
('work_item_status', 'BLOQUEADO', 'Bloqueado', 'Trabajo detenido por dependencia o problema', 3),
('work_item_status', 'COMPLETADO', 'Completado', 'Trabajo terminado, pendiente verificación', 4),
('work_item_status', 'VERIFICADO', 'Verificado', 'Trabajo verificado por jefe/admin', 5),
('work_item_status', 'CANCELADO', 'Cancelado', 'Trabajo cancelado', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- PRIORIDAD DE WORK_ITEM
INSERT INTO ref.category (scheme, code, label, sort_order) VALUES
('work_item_priority', 'URGENTE', 'Urgente', 1),
('work_item_priority', 'ALTA', 'Alta', 2),
('work_item_priority', 'NORMAL', 'Normal', 3),
('work_item_priority', 'BAJA', 'Baja', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    sort_order = EXCLUDED.sort_order;

-- ESTADOS DE COMPROMISO OPERATIVO (HIGH-003: requerido por core.operational_commitment.state_id)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('commitment_state', 'PENDIENTE', 'Pendiente', 'Compromiso registrado, pendiente de inicio', 1),
('commitment_state', 'EN_PROGRESO', 'En Progreso', 'Compromiso en ejecución activa', 2),
('commitment_state', 'COMPLETADO', 'Completado', 'Compromiso completado, pendiente verificación', 3),
('commitment_state', 'VERIFICADO', 'Verificado', 'Compromiso verificado y cerrado', 4),
('commitment_state', 'VENCIDO', 'Vencido', 'Compromiso con plazo vencido', 5),
('commitment_state', 'CANCELADO', 'Cancelado', 'Compromiso cancelado', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADOS DE INICIATIVA DGI (Kanban sin topes WIP fijos desde C62)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_initiative_status', 'BACKLOG', 'Backlog', 'Iniciativa priorizable aún no iniciada', 1),
('dgi_initiative_status', 'EN_CURSO', 'En Curso', 'Iniciativa en ejecución', 2),
('dgi_initiative_status', 'REVISION', 'En Revisión', 'Iniciativa en revisión de resultados', 3),
('dgi_initiative_status', 'COMPLETADO', 'Completado', 'Iniciativa completada', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- CATÁLOGOS Y CICLO DE VIDA DE INDICADORES DGI
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_indicator_dimension', 'PRESUPUESTO', 'Presupuesto', 'Ejecución y gestión presupuestaria', 1),
('dgi_indicator_dimension', 'CARTERA_IPR', 'Cartera IPR', 'Estado agregado de la cartera de iniciativas', 2),
('dgi_indicator_dimension', 'CONVENIOS', 'Convenios', 'Gestión y vigencia de convenios', 3),
('dgi_indicator_dimension', 'RIESGOS', 'Riesgos', 'Alertas, problemas y riesgos operacionales', 4),
('dgi_indicator_dimension', 'TDE', 'Transformación Digital', 'Transformación digital del Estado', 5),
('dgi_signal', 'VERDE', 'Verde', 'Resultado dentro del rango esperado', 1),
('dgi_signal', 'AMARILLO', 'Amarillo', 'Resultado que requiere atención', 2),
('dgi_signal', 'ROJO', 'Rojo', 'Resultado crítico', 3)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

INSERT INTO ref.category
    (scheme, code, label, description, sort_order, valid_transitions)
VALUES
('dgi_indicator_lifecycle', 'BORRADOR', 'Borrador', 'Indicador en definición', 1, '["APROBADO"]'::jsonb),
('dgi_indicator_lifecycle', 'APROBADO', 'Aprobado', 'Indicador aprobado, aún no vigente', 2, '["VIGENTE", "BORRADOR"]'::jsonb),
('dgi_indicator_lifecycle', 'VIGENTE', 'Vigente', 'Indicador activo', 3, '["DEPRECADO", "APROBADO"]'::jsonb),
('dgi_indicator_lifecycle', 'DEPRECADO', 'Deprecado', 'Indicador retirado', 4, '[]'::jsonb)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    valid_transitions = EXCLUDED.valid_transitions;

-- CATÁLOGOS Y CICLO DE VIDA DEL MODELAMIENTO DE PROCESOS DGI
INSERT INTO ref.category
    (scheme, code, label, description, sort_order, valid_transitions)
VALUES
('dgi_process_status', 'IDENTIFICADO', 'Identificado', 'Proceso identificado', 1, '["EN_LEVANTAMIENTO", "SUSPENDIDO"]'::jsonb),
('dgi_process_status', 'EN_LEVANTAMIENTO', 'En Levantamiento', 'Proceso en levantamiento', 2, '["MODELADO", "IDENTIFICADO", "SUSPENDIDO"]'::jsonb),
('dgi_process_status', 'MODELADO', 'Modelado', 'Proceso modelado', 3, '["VALIDADO", "EN_LEVANTAMIENTO", "SUSPENDIDO"]'::jsonb),
('dgi_process_status', 'VALIDADO', 'Validado', 'Modelo validado', 4, '["PUBLICADO", "MODELADO", "SUSPENDIDO"]'::jsonb),
('dgi_process_status', 'PUBLICADO', 'Publicado', 'Proceso publicado', 5, '["SUSPENDIDO"]'::jsonb),
('dgi_process_status', 'SUSPENDIDO', 'Suspendido', 'Proceso temporalmente suspendido', 6, '["IDENTIFICADO"]'::jsonb),
('dgi_bpmn_status', 'BORRADOR', 'Borrador', 'Modelo BPMN en edición', 1, '["REVISION"]'::jsonb),
('dgi_bpmn_status', 'REVISION', 'En Revisión', 'Modelo BPMN en revisión', 2, '["BORRADOR", "VALIDADO"]'::jsonb),
('dgi_bpmn_status', 'VALIDADO', 'Validado', 'Modelo BPMN validado', 3, '["BORRADOR"]'::jsonb)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    valid_transitions = EXCLUDED.valid_transitions;

INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_bpmn_type', 'AS_IS', 'Estado Actual', 'Modelo del proceso vigente', 1),
('dgi_bpmn_type', 'TO_BE', 'Estado Futuro', 'Modelo del proceso objetivo', 2)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- CATÁLOGOS Y FLUJO DE INFORMES DGI (D-DGI-CG-024..027)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_report_type', 'FLASH', 'Flash', 'Informe urgente y conciso', 1),
('dgi_report_type', 'SEMANAL', 'Semanal', 'Informe semanal de gestión', 2),
('dgi_report_type', 'MENSUAL', 'Mensual', 'Informe mensual de gestión', 3),
('dgi_report_type', 'TEMATICO', 'Temático', 'Informe sobre una materia específica', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

INSERT INTO ref.category
    (scheme, code, label, description, sort_order, valid_transitions)
VALUES
('dgi_report_status', 'BORRADOR', 'Borrador', 'Informe en elaboración', 1, '["EN_REVISION"]'::jsonb),
('dgi_report_status', 'EN_REVISION', 'En Revisión', 'Informe en revisión por jefatura', 2, '["BORRADOR", "ENVIADO"]'::jsonb),
('dgi_report_status', 'ENVIADO', 'Enviado', 'Informe enviado a su destinatario', 3, '[]'::jsonb)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    valid_transitions = EXCLUDED.valid_transitions;

-- FASES DMAIC DE INICIATIVAS DGI
INSERT INTO ref.category
    (scheme, code, label, description, sort_order, valid_transitions)
VALUES
('dgi_dmaic_phase', 'DEFINE', 'Definir', 'Definición del problema y alcance', 1, '["MEASURE", "ANALYZE", "IMPROVE", "VERIFY"]'::jsonb),
('dgi_dmaic_phase', 'MEASURE', 'Medir', 'Medición de la línea base', 2, '["ANALYZE", "IMPROVE", "VERIFY"]'::jsonb),
('dgi_dmaic_phase', 'ANALYZE', 'Analizar', 'Análisis de causas raíz', 3, '["IMPROVE", "VERIFY"]'::jsonb),
('dgi_dmaic_phase', 'IMPROVE', 'Mejorar', 'Diseño y prueba de mejoras', 4, '["VERIFY"]'::jsonb),
('dgi_dmaic_phase', 'VERIFY', 'Verificar', 'Verificación y sostenibilidad de la mejora', 5, '[]'::jsonb)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    valid_transitions = EXCLUDED.valid_transitions;

-- ESTADOS DE INVESTIGACIÓN DE CUELLOS DE BOTELLA DGI
INSERT INTO ref.category
    (scheme, code, label, description, sort_order, valid_transitions)
VALUES
('dgi_bottleneck_status', 'DETECTADO', 'Detectado', 'Cuello de botella detectado, pendiente de verificación', 1, '["VERIFICADO", "CERRADO"]'::jsonb),
('dgi_bottleneck_status', 'VERIFICADO', 'Verificado', 'Hallazgo confirmado', 2, '["ANALIZADO", "CERRADO"]'::jsonb),
('dgi_bottleneck_status', 'ANALIZADO', 'Analizado', 'Causa raíz analizada', 3, '["PROPUESTO", "CERRADO"]'::jsonb),
('dgi_bottleneck_status', 'PROPUESTO', 'Propuesto', 'Solución propuesta', 4, '["IMPLEMENTADO", "CERRADO"]'::jsonb),
('dgi_bottleneck_status', 'IMPLEMENTADO', 'Implementado', 'Solución implementada, pendiente de cierre', 5, '["CERRADO"]'::jsonb),
('dgi_bottleneck_status', 'CERRADO', 'Cerrado', 'Investigación cerrada', 6, '[]'::jsonb)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    valid_transitions = EXCLUDED.valid_transitions;

-- CATÁLOGOS DE COORDINACIÓN DGI (Wave B)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_ar_decision_type', 'PRIORIDAD', 'Prioridad', 'Decisión de priorización', 1),
('dgi_ar_decision_type', 'RECURSO', 'Recurso', 'Asignación de recursos', 2),
('dgi_ar_decision_type', 'ESCALAMIENTO', 'Escalamiento', 'Decisión de escalamiento', 3),
('dgi_ar_decision_type', 'ESTRATEGIA', 'Estrategia', 'Decisión estratégica', 4),
('dgi_ar_decision_status', 'PENDIENTE', 'Pendiente', 'Decisión pendiente de ejecución', 1),
('dgi_ar_decision_status', 'EN_EJECUCION', 'En Ejecución', 'Decisión en proceso de implementación', 2),
('dgi_ar_decision_status', 'COMPLETADA', 'Completada', 'Decisión completada', 3),
('dgi_escalation_level', 'NIVEL_1', 'Nivel 1', 'Jefe DGI — resolución en 4h', 1),
('dgi_escalation_level', 'NIVEL_2', 'Nivel 2', 'Administrador Regional — resolución en 24h', 2),
('dgi_escalation_level', 'NIVEL_3', 'Nivel 3', 'Administrador Regional + Mesa — resolución en 48h', 3),
('dgi_escalation_level', 'NIVEL_4', 'Nivel 4', 'Gobernador — según urgencia', 4),
('dgi_escalation_status', 'ABIERTO', 'Abierto', 'Escalamiento registrado', 1),
('dgi_escalation_status', 'EN_GESTION', 'En Gestión', 'Escalamiento siendo gestionado', 2),
('dgi_escalation_status', 'RESUELTO', 'Resuelto', 'Escalamiento resuelto', 3),
('dgi_escalation_status', 'CERRADO', 'Cerrado', 'Escalamiento cerrado', 4),
('dgi_service_status', 'ACTIVO', 'Activo', 'Servicio disponible', 1),
('dgi_service_status', 'SUSPENDIDO', 'Suspendido', 'Servicio temporalmente suspendido', 2),
('dgi_service_status', 'DESCONTINUADO', 'Descontinuado', 'Servicio descontinuado', 3),
('dgi_request_status', 'RECIBIDA', 'Recibida', 'Solicitud recibida', 1),
('dgi_request_status', 'EN_EVALUACION', 'En Evaluación', 'Solicitud siendo evaluada', 2),
('dgi_request_status', 'ACEPTADA', 'Aceptada', 'Solicitud aceptada', 3),
('dgi_request_status', 'EN_EJECUCION', 'En Ejecución', 'Solicitud en ejecución', 4),
('dgi_request_status', 'COMPLETADA', 'Completada', 'Solicitud completada', 5),
('dgi_request_status', 'RECHAZADA', 'Rechazada', 'Solicitud rechazada', 6),
('dgi_interaction_type', 'PRESUPUESTO', 'Presupuesto', 'Interacción sobre temas presupuestarios', 1),
('dgi_interaction_type', 'CARTERA', 'Cartera', 'Interacción sobre cartera de proyectos', 2),
('dgi_interaction_type', 'JURIDICO', 'Jurídico', 'Interacción sobre temas jurídicos', 3),
('dgi_interaction_type', 'TECNOLOGIA', 'Tecnología', 'Interacción sobre temas tecnológicos', 4),
('dgi_interaction_type', 'PROCESO', 'Proceso', 'Interacción sobre procesos', 5),
('dgi_interaction_type', 'GENERAL', 'General', 'Interacción general', 6),
('dgi_sla_product_type', 'INFORME_FLASH', 'Informe Flash', 'Informe flash de contingencia', 1),
('dgi_sla_product_type', 'INFORME_SEMANAL', 'Informe Semanal', 'Informe semanal de gestión', 2),
('dgi_sla_product_type', 'INFORME_MENSUAL', 'Informe Mensual', 'Informe mensual de gestión', 3),
('dgi_sla_product_type', 'LEVANTAMIENTO_PROCESO', 'Levantamiento de Proceso', 'Levantamiento y modelado de proceso', 4),
('dgi_sla_product_type', 'ANALISIS_INDICADOR', 'Análisis de Indicador', 'Análisis de indicador de gestión', 5),
('dgi_sla_product_type', 'EVALUACION_CARTERA', 'Evaluación de Cartera', 'Evaluación de cartera IPR', 6),
('dgi_sla_product_type', 'SOPORTE_TD', 'Soporte TD', 'Soporte en transformación digital', 7)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ORIGEN DE WORK_ITEM
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('work_item_origin', 'MANUAL', 'Creación Manual', 'Creado manualmente por usuario', 1),
('work_item_origin', 'REUNION', 'Derivado de Reunión', 'Derivado de reunión o sesión', 2),
('work_item_origin', 'PROBLEMA', 'Derivado de Problema', 'Creado para resolver problema', 3),
('work_item_origin', 'ALERTA', 'Derivado de Alerta', 'Creado por alerta del sistema', 4),
('work_item_origin', 'SISTEMA', 'Generado por Sistema', 'Creado automáticamente', 5),
('work_item_origin', 'IMPORTACION', 'Importación', 'Importado desde fuente externa', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- EVENTOS DE WORK_ITEM (para historial)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('work_item_event', 'CREATED', 'Creado', 'Ítem creado', 1),
('work_item_event', 'STATUS_CHANGE', 'Cambio de Estado', 'Estado modificado', 2),
('work_item_event', 'REASSIGNED', 'Reasignado', 'Asignado a otro responsable', 3),
('work_item_event', 'BLOCKED', 'Bloqueado', 'Ítem bloqueado', 4),
('work_item_event', 'UNBLOCKED', 'Desbloqueado', 'Ítem desbloqueado', 5),
('work_item_event', 'VERIFIED', 'Verificado', 'Completado y verificado', 6),
('work_item_event', 'COMMENT', 'Comentario', 'Comentario agregado', 7),
('work_item_event', 'DUE_DATE_CHANGE', 'Cambio Fecha', 'Fecha límite modificada', 8),
('work_item_event', 'PRIORITY_CHANGE', 'Cambio Prioridad', 'Prioridad modificada', 9)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE PROBLEMA (RF-040)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('problem_type', 'TECNICO', 'Técnico', 'Problema técnico de ejecución', 1),
('problem_type', 'FINANCIERO', 'Financiero', 'Problema de recursos o pagos', 2),
('problem_type', 'ADMINISTRATIVO', 'Administrativo', 'Problema administrativo o documental', 3),
('problem_type', 'LEGAL', 'Legal', 'Problema legal o contractual', 4),
('problem_type', 'COORDINACION', 'Coordinación', 'Problema de coordinación inter-institucional', 5),
('problem_type', 'EXTERNO', 'Externo', 'Problema causado por factores externos', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- IMPACTO DE PROBLEMA (RF-040)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('problem_impact', 'BLOQUEA_PAGO', 'Bloquea Pago', 'Impide realizar pagos', 1),
('problem_impact', 'RETRASA_OBRA', 'Retrasa Obra', 'Retrasa ejecución física', 2),
('problem_impact', 'RETRASA_CONVENIO', 'Retrasa Convenio', 'Retrasa formalización', 3),
('problem_impact', 'RIESGO_RENDICION', 'Riesgo Rendición', 'Puede afectar rendición', 4),
('problem_impact', 'INCUMPLIMIENTO_PLAZO', 'Incumplimiento Plazo', 'Riesgo de plazo legal', 5),
('problem_impact', 'OTRO', 'Otro', 'Otro tipo de impacto', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADOS DE PROBLEMA (requerido por core.ipr_problem.state_id)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('problem_state', 'ABIERTO', 'Abierto', 'Problema detectado, sin gestión iniciada', 1),
('problem_state', 'EN_GESTION', 'En Gestión', 'Problema con acciones de resolución en curso', 2),
('problem_state', 'RESUELTO', 'Resuelto', 'Problema resuelto satisfactoriamente', 3),
('problem_state', 'CERRADO_SIN_RESOLVER', 'Cerrado Sin Resolver', 'Problema cerrado sin resolución efectiva', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADO DE PAGO (para agreement_installment)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('payment_status', 'PENDIENTE', 'Pendiente', 'Pago pendiente', 1),
('payment_status', 'EN_PROCESO', 'En Proceso', 'Pago en trámite', 2),
('payment_status', 'PAGADO', 'Pagado', 'Pago realizado', 3),
('payment_status', 'DIFERIDO', 'Diferido', 'Pago diferido', 4),
('payment_status', 'RECHAZADO', 'Rechazado', 'Pago rechazado', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES META
-- ============================================================================

-- DOMINIOS DE HISTORIA
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('story_domain', 'INVERSIONES', 'Inversiones', 'Gestión de inversiones públicas', 1),
('story_domain', 'FINANZAS', 'Finanzas', 'Gestión financiera y presupuestaria', 2),
('story_domain', 'JURIDICO', 'Jurídico', 'Gestión jurídica y normativa', 3),
('story_domain', 'TERRITORIAL', 'Territorial', 'Planificación territorial', 4),
('story_domain', 'DIGITAL', 'Digital', 'Transformación digital', 5),
('story_domain', 'CONTROL', 'Control', 'Control de gestión', 6),
('story_domain', 'ORGANIZACIONAL', 'Organizacional', 'Gestión organizacional', 7)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE ROL META (HAIC)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('role_type', 'HUMAN', 'Human', 'Rol ejercido por humano', 1),
('role_type', 'AI', 'AI', 'Rol ejercido por agente IA', 2),
('role_type', 'HYBRID', 'Hybrid', 'Rol colaborativo Human-AI', 3)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE PROCESO
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('process_type', 'CORE', 'Core', 'Proceso misional', 1),
('process_type', 'SOPORTE', 'Soporte', 'Proceso de soporte', 2),
('process_type', 'ESTRATEGICO', 'Estratégico', 'Proceso estratégico', 3)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES TDE (tdeCore.ttl)
-- ============================================================================

-- TIPOS DE NORMA (tde:TipoNorma)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('norm_type', 'LEY', 'Ley', 'Ley de la República', 1),
('norm_type', 'DFL', 'DFL', 'Decreto con Fuerza de Ley', 2),
('norm_type', 'DL', 'DL', 'Decreto Ley', 3),
('norm_type', 'DS', 'DS', 'Decreto Supremo', 4),
('norm_type', 'REGLAMENTO', 'Reglamento', 'Reglamento', 5),
('norm_type', 'INSTRUCTIVO', 'Instructivo', 'Instructivo o circular', 6),
('norm_type', 'NORMA_TECNICA', 'Norma Técnica', 'Norma técnica sectorial', 7)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ESTADO DE VIGENCIA (tde:EstadoVigencia)
INSERT INTO ref.category (scheme, code, label, sort_order) VALUES
('validity_status', 'VIGENTE', 'Vigente', 1),
('validity_status', 'DEROGADO', 'Derogado', 2),
('validity_status', 'MODIFICADO', 'Modificado', 3),
('validity_status', 'EN_TRAMITE', 'En Trámite', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    sort_order = EXCLUDED.sort_order;

-- NIVEL DE GOBIERNO (tde:NivelGobierno)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('gov_level', 'CENTRAL', 'Central', 'Gobierno central', 1),
('gov_level', 'REGIONAL', 'Regional', 'Gobierno regional', 2),
('gov_level', 'MUNICIPAL', 'Municipal', 'Gobierno municipal', 3)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- NIVEL MADUREZ MGDE (tde:NivelMadurezMGDE)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('mgde_level', 'INICIAL', 'Inicial', 'Nivel 1 - Inicial', 1),
('mgde_level', 'GESTIONADO', 'Gestionado', 'Nivel 2 - Gestionado', 2),
('mgde_level', 'DEFINIDO', 'Definido', 'Nivel 3 - Definido', 3),
('mgde_level', 'MEDIDO', 'Medido', 'Nivel 4 - Medido', 4),
('mgde_level', 'OPTIMIZADO', 'Optimizado', 'Nivel 5 - Optimizado', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ROL TDE (tde:RolTDE)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('tde_role', 'COORDINADOR_TD', 'Coordinador TD', 'Coordinador Transformación Digital', 1),
('tde_role', 'OFICIAL_DATOS', 'Oficial de Datos', 'Oficial de Datos Institucional', 2),
('tde_role', 'ENCARGADO_INTEROP', 'Encargado Interoperabilidad', 'Encargado de Interoperabilidad', 3),
('tde_role', 'GESTOR_TRAMITES', 'Gestor de Trámites', 'Gestor de Trámites Digitales', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES NORMALIZACIÓN v3.0/v3.4
-- ============================================================================

-- ============================================================================
-- SCHEME: estamento (v3.0)
-- DESCRIPCIÓN: Clasificación funcionaria chilena (tde:Estamento, Ley 18.834)
-- ============================================================================
INSERT INTO ref.category (scheme, code, label, description, metadata, sort_order) VALUES
('estamento', 'PROFESIONAL', 'Profesional', 'Estamento profesional', '{"ontology": "tde:Estamento", "ley": "18.834"}', 1),
('estamento', 'DIRECTIVO', 'Directivo', 'Estamento directivo', '{"ontology": "tde:Estamento", "ley": "18.834"}', 2),
('estamento', 'ADMINISTRATIVO', 'Administrativo', 'Estamento administrativo', '{"ontology": "tde:Estamento", "ley": "18.834"}', 3),
('estamento', 'TECNICO', 'Técnico', 'Estamento técnico', '{"ontology": "tde:Estamento", "ley": "18.834"}', 4),
('estamento', 'AUXILIAR', 'Auxiliar', 'Estamento auxiliar', '{"ontology": "tde:Estamento", "ley": "18.834"}', 5),
('estamento', 'HONORARIOS', 'Honorarios', 'Personal a honorarios', '{"ontology": "tde:Estamento", "ley": "18.834"}', 6),
('estamento', 'AUTORIDAD', 'Autoridad de Gobierno', 'Autoridades de gobierno regional', '{"ontology": "tde:Estamento"}', 7)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
-- SCHEME: professional_qualification (v3.4)
-- DESCRIPCIÓN: Calificaciones profesionales del personal (tde:CalificacionProfesional)
-- ============================================================================
INSERT INTO ref.category (scheme, code, label, description, metadata, sort_order) VALUES
('professional_qualification', 'INGENIERO', 'Ingeniero', 'Ingeniero civil o de ejecución', '{"ontology": "tde:CalificacionProfesional"}', 1),
('professional_qualification', 'ARQUITECTO', 'Arquitecto', 'Arquitecto', '{"ontology": "tde:CalificacionProfesional"}', 2),
('professional_qualification', 'ABOGADO', 'Abogado', 'Abogado', '{"ontology": "tde:CalificacionProfesional"}', 3),
('professional_qualification', 'CONTADOR', 'Contador/Auditor', 'Contador público o auditor', '{"ontology": "tde:CalificacionProfesional"}', 4),
('professional_qualification', 'ADMINISTRADOR', 'Administrador Público', 'Administrador público', '{"ontology": "tde:CalificacionProfesional"}', 5),
('professional_qualification', 'ECONOMISTA', 'Economista', 'Economista o ingeniero comercial', '{"ontology": "tde:CalificacionProfesional"}', 6),
('professional_qualification', 'TRABAJADOR_SOCIAL', 'Trabajador Social', 'Trabajador o asistente social', '{"ontology": "tde:CalificacionProfesional"}', 7),
('professional_qualification', 'PSICOLOGO', 'Psicólogo', 'Psicólogo', '{"ontology": "tde:CalificacionProfesional"}', 8),
('professional_qualification', 'PERIODISTA', 'Periodista/Comunicador', 'Periodista o comunicador social', '{"ontology": "tde:CalificacionProfesional"}', 9),
('professional_qualification', 'PROFESOR', 'Profesor/Docente', 'Profesor o docente', '{"ontology": "tde:CalificacionProfesional"}', 10),
('professional_qualification', 'GEOGRAFO', 'Geógrafo', 'Geógrafo', '{"ontology": "tde:CalificacionProfesional"}', 11),
('professional_qualification', 'TECNICO', 'Técnico', 'Técnico de nivel superior', '{"ontology": "tde:CalificacionProfesional"}', 12),
('professional_qualification', 'SECRETARIA', 'Secretaria/Administrativo', 'Secretaria o administrativo', '{"ontology": "tde:CalificacionProfesional"}', 13),
('professional_qualification', 'OTRO', 'Otra calificación', 'Otra calificación profesional', '{"ontology": "tde:CalificacionProfesional"}', 99)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
-- SCHEME: magnitude_aspect (v3.0)
-- DESCRIPCIÓN: Aspectos de magnitudes financieras (gist:MagnitudeAspect)
-- ============================================================================
INSERT INTO ref.category (scheme, code, label, description, metadata, sort_order) VALUES
('magnitude_aspect', 'TRANSFER_AMOUNT', 'Monto Transferido', 'Monto efectivamente transferido', '{"ontology": "gist:MagnitudeAspect"}', 1),
('magnitude_aspect', 'BUDGET_AMOUNT', 'Monto Presupuestado', 'Monto presupuestado inicial', '{"ontology": "gist:MagnitudeAspect"}', 2),
('magnitude_aspect', 'COMMITTED_AMOUNT', 'Monto Comprometido', 'Monto comprometido contractualmente', '{"ontology": "gist:MagnitudeAspect"}', 3),
('magnitude_aspect', 'EXECUTED_AMOUNT', 'Monto Ejecutado', 'Monto ejecutado/devengado', '{"ontology": "gist:MagnitudeAspect"}', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
-- SCHEME: currency (v3.0)
-- DESCRIPCIÓN: Monedas ISO 4217 (gist:UnitOfMeasure)
-- ============================================================================
INSERT INTO ref.category (scheme, code, label, description, metadata, sort_order) VALUES
('currency', 'CLP', 'Peso Chileno', 'Moneda nacional chilena', '{"iso_4217": "CLP", "symbol": "$", "decimals": 0}', 1),
('currency', 'UF', 'Unidad de Fomento', 'Unidad de fomento (reajustable)', '{"symbol": "UF", "decimals": 2}', 2),
('currency', 'USD', 'Dólar Estadounidense', 'Dólar de Estados Unidos', '{"iso_4217": "USD", "symbol": "US$", "decimals": 2}', 3)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.actor - ACTORES DIPIR (23 actores)
-- ============================================================================
-- Fuente: dipir_ssot_koda.yaml

INSERT INTO ref.actor (code, name, full_name, emoji, style, is_internal, sort_order) VALUES
-- Actores Internos GORE
('CT_GORE', 'CT_GORE', 'Comité Técnico GORE', '🏛️', 'fill:#4A90D9,stroke:#2E5D8C', TRUE, 1),
('ANALISTA_DIPIR', 'Analista DIPIR', 'Analista División de Planificación', '👤', 'fill:#81C784,stroke:#4CAF50', TRUE, 2),
('JEFE_DIPIR', 'Jefe DIPIR', 'Jefe División de Planificación', '👔', 'fill:#64B5F6,stroke:#1976D2', TRUE, 3),
('JEFE_PPTO', 'Jefe Presupuesto', 'Jefe Departamento Presupuesto', '💰', 'fill:#FFD54F,stroke:#F9A825', TRUE, 4),
('JEFE_JURIDICA', 'Jefe Jurídica', 'Jefe División Jurídica', '⚖️', 'fill:#CE93D8,stroke:#8E24AA', TRUE, 5),
('DAF', 'DAF', 'División de Administración y Finanzas', '📊', 'fill:#90CAF9,stroke:#1565C0', TRUE, 6),
('ADMIN_REG', 'Admin Regional', 'Administrador Regional', '🎯', 'fill:#EF9A9A,stroke:#C62828', TRUE, 7),
('JEFE_SERV', 'Jefe Servicio', 'Jefe de Servicio', '📋', 'fill:#A5D6A7,stroke:#388E3C', TRUE, 8),
('ENCARGADO_CONVENIO', 'Encargado Convenio', 'Encargado de Convenios', '📝', 'fill:#FFF59D,stroke:#FBC02D', TRUE, 9),
('TESORERIA', 'Tesorería', 'Tesorería Regional', '🏦', 'fill:#FFCC80,stroke:#EF6C00', TRUE, 10),
('SECRETARIA_EJECUTIVA', 'Secretaría Ejecutiva', 'Secretaría Ejecutiva Regional', '📧', 'fill:#B39DDB,stroke:#512DA8', TRUE, 11),
('GOBERNADOR', 'Gobernador', 'Gobernador Regional', '👑', 'fill:#FFAB91,stroke:#D84315', TRUE, 12),

-- Actores Externos
('CORE', 'CORE', 'Consejo Regional', '🏛️', 'fill:#E1BEE7,stroke:#7B1FA2', FALSE, 20),
('CGR', 'CGR', 'Contraloría General de la República', '🔍', 'fill:#FFCDD2,stroke:#B71C1C', FALSE, 21),
('DIPRES', 'DIPRES', 'Dirección de Presupuestos', '📈', 'fill:#C5CAE9,stroke:#303F9F', FALSE, 22),
('MDSF', 'MDSF', 'Ministerio de Desarrollo Social y Familia', '🏠', 'fill:#B2DFDB,stroke:#00695C', FALSE, 23),
('SUBDERE', 'SUBDERE', 'Subsecretaría de Desarrollo Regional', '🗺️', 'fill:#DCEDC8,stroke:#689F38', FALSE, 24),
('SES', 'SES', 'Servicio de Evaluación Social', '📊', 'fill:#F0F4C3,stroke:#AFB42B', FALSE, 25),
('UNIDAD_TECNICA', 'UT', 'Unidad Técnica', '🔧', 'fill:#B3E5FC,stroke:#0277BD', FALSE, 26),
('PROVEEDOR', 'Proveedor', 'Proveedor o Contratista', '🏭', 'fill:#CFD8DC,stroke:#455A64', FALSE, 27),
('ENTIDAD_EJECUTORA', 'Ejecutora', 'Entidad Ejecutora', '🏗️', 'fill:#D7CCC8,stroke:#5D4037', FALSE, 28),
('MUNICIPIO', 'Municipio', 'Municipalidad', '🏘️', 'fill:#F8BBD9,stroke:#C2185B', FALSE, 29),
('BENEFICIARIO', 'Beneficiario', 'Beneficiario Final', '👥', 'fill:#E0E0E0,stroke:#616161', FALSE, 30)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    full_name = EXCLUDED.full_name,
    emoji = EXCLUDED.emoji,
    style = EXCLUDED.style,
    is_internal = EXCLUDED.is_internal,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    SCHEMA: ref.operational_commitment_type - TIPOS COMPROMISO OPERATIVO
-- ============================================================================

INSERT INTO ref.operational_commitment_type (code, name, description, default_days, sort_order) VALUES
('HITO_CONTRATO', 'Hito Contractual', 'Hito definido en contrato de ejecución', 30, 1),
('ENTREGA_INFORME', 'Entrega de Informe', 'Entrega de informe técnico o de avance', 15, 2),
('RENDICION', 'Rendición de Cuentas', 'Rendición de recursos transferidos', 30, 3),
('REVISION_TECNICA', 'Revisión Técnica', 'Revisión técnica de avance o producto', 10, 4),
('VISITA_TERRENO', 'Visita a Terreno', 'Visita de inspección en terreno', 7, 5),
('SESION_COMITE', 'Sesión de Comité', 'Sesión de comité técnico o CORE', 1, 6),
('PLAZO_CGR', 'Plazo CGR', 'Plazo de respuesta a CGR', 15, 7),
('PLAZO_CONVENIO', 'Plazo Convenio', 'Plazo establecido en convenio', 30, 8),
('PAGO', 'Pago', 'Compromiso de pago', 30, 9),
('OTRO', 'Otro', 'Otro tipo de compromiso', 15, 10)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    default_days = EXCLUDED.default_days,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    HIGH-003 FIX: TRANSICIONES DE ESTADO VÁLIDAS
-- ============================================================================
-- Poblar valid_transitions para schemes de estado (usado por fn_validate_state_transition)
-- Formato: JSONB array con códigos de estados destino permitidos
-- ============================================================================

-- Transiciones de ipr_state (flujo principal de IPR)
UPDATE ref.category SET valid_transitions = '["EN_REVISION", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'INGRESADO';

UPDATE ref.category SET valid_transitions = '["PRE_ADMISIBLE", "INADMISIBLE"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_REVISION';

UPDATE ref.category SET valid_transitions = '["ADMISIBLE", "INADMISIBLE"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'PRE_ADMISIBLE';

UPDATE ref.category SET valid_transitions = '["EN_EVALUACION"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'ADMISIBLE';

UPDATE ref.category SET valid_transitions = '["INGRESADO", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'INADMISIBLE';

UPDATE ref.category SET valid_transitions = '["RS", "FI", "FC", "OT", "RF", "ITF", "AT", "AD", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_EVALUACION';

-- Estados Proyecto post-evaluación
UPDATE ref.category SET valid_transitions = '["CDP_EMITIDO", "OT"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'RS';

UPDATE ref.category SET valid_transitions = '["CDP_EMITIDO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'FI';

UPDATE ref.category SET valid_transitions = '["FI", "OT"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'FC';

UPDATE ref.category SET valid_transitions = '["EN_EVALUACION", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'OT';

UPDATE ref.category SET valid_transitions = '["EN_LICITACION", "CDP_EMITIDO", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'AD';

UPDATE ref.category SET valid_transitions = '["ADJUDICADO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_LICITACION';

UPDATE ref.category SET valid_transitions = '["CONTRATO_FIRMADO", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'ADJUDICADO';

UPDATE ref.category SET valid_transitions = '["EN_OBRA", "SUSPENDIDO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'CONTRATO_FIRMADO';

UPDATE ref.category SET valid_transitions = '["RECEPCION_PROVISORIA", "SUSPENDIDO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_OBRA';

UPDATE ref.category SET valid_transitions = '["RECEPCION_DEFINITIVA", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'RECEPCION_PROVISORIA';

UPDATE ref.category SET valid_transitions = '["EN_RENDICION", "CERRADO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'RECEPCION_DEFINITIVA';

-- Estados Programa post-evaluación
UPDATE ref.category SET valid_transitions = '["CDP_EMITIDO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'RF';

UPDATE ref.category SET valid_transitions = '["CDP_EMITIDO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'ITF';

UPDATE ref.category SET valid_transitions = '["CDP_EMITIDO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'AT';

-- Estados comunes post-CDP
UPDATE ref.category SET valid_transitions = '["EN_FORMALIZACION", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'CDP_EMITIDO';

UPDATE ref.category SET valid_transitions = '["FORMALIZADO", "EN_LICITACION", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_FORMALIZACION';

UPDATE ref.category SET valid_transitions = '["EN_EJECUCION", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'FORMALIZADO';

UPDATE ref.category SET valid_transitions = '["EN_RENDICION", "SUSPENDIDO", "CERRADO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_EJECUCION';

UPDATE ref.category SET valid_transitions = '["EN_EJECUCION", "EN_OBRA", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'SUSPENDIDO';

UPDATE ref.category SET valid_transitions = '["RENDICION_APROBADA", "CERRADO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_RENDICION';

UPDATE ref.category SET valid_transitions = '["EN_CIERRE_ADMINISTRATIVO", "CERRADO", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'RENDICION_APROBADA';

UPDATE ref.category SET valid_transitions = '["CERRADO", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_CIERRE_ADMINISTRATIVO';

-- Estados terminales (sin transiciones salientes)
UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'ipr_state' AND code IN ('CERRADO', 'ANULADO', 'TERMINADO_ANTICIPADAMENTE');

-- Transiciones de work_item_status
UPDATE ref.category SET valid_transitions = '["EN_PROGRESO", "CANCELADO"]'::jsonb
WHERE scheme = 'work_item_status' AND code = 'PENDIENTE';

UPDATE ref.category SET valid_transitions = '["COMPLETADO", "BLOQUEADO", "CANCELADO"]'::jsonb
WHERE scheme = 'work_item_status' AND code = 'EN_PROGRESO';

UPDATE ref.category SET valid_transitions = '["EN_PROGRESO"]'::jsonb
WHERE scheme = 'work_item_status' AND code = 'BLOQUEADO';

UPDATE ref.category SET valid_transitions = '["VERIFICADO", "EN_PROGRESO"]'::jsonb
WHERE scheme = 'work_item_status' AND code = 'COMPLETADO';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'work_item_status' AND code IN ('VERIFICADO', 'CANCELADO');

-- Transiciones de commitment_state
UPDATE ref.category SET valid_transitions = '["EN_PROGRESO", "COMPLETADO", "CANCELADO", "VENCIDO"]'::jsonb
WHERE scheme = 'commitment_state' AND code = 'PENDIENTE';

UPDATE ref.category SET valid_transitions = '["COMPLETADO", "VENCIDO", "CANCELADO"]'::jsonb
WHERE scheme = 'commitment_state' AND code = 'EN_PROGRESO';

UPDATE ref.category SET valid_transitions = '["VERIFICADO", "EN_PROGRESO"]'::jsonb
WHERE scheme = 'commitment_state' AND code = 'COMPLETADO';

UPDATE ref.category SET valid_transitions = '["EN_PROGRESO", "COMPLETADO"]'::jsonb
WHERE scheme = 'commitment_state' AND code = 'VENCIDO';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'commitment_state' AND code IN ('VERIFICADO', 'CANCELADO');

-- Transiciones de dgi_initiative_status (movimiento Kanban libre; COMPLETADO reabre a BACKLOG)
UPDATE ref.category SET valid_transitions = '["EN_CURSO", "REVISION", "COMPLETADO"]'::jsonb
WHERE scheme = 'dgi_initiative_status' AND code = 'BACKLOG';

UPDATE ref.category SET valid_transitions = '["BACKLOG", "REVISION", "COMPLETADO"]'::jsonb
WHERE scheme = 'dgi_initiative_status' AND code = 'EN_CURSO';

UPDATE ref.category SET valid_transitions = '["BACKLOG", "EN_CURSO", "COMPLETADO"]'::jsonb
WHERE scheme = 'dgi_initiative_status' AND code = 'REVISION';

UPDATE ref.category SET valid_transitions = '["BACKLOG"]'::jsonb
WHERE scheme = 'dgi_initiative_status' AND code = 'COMPLETADO';

-- Transiciones de coordinación DGI
UPDATE ref.category SET valid_transitions = '["EN_EJECUCION"]'::jsonb
WHERE scheme = 'dgi_ar_decision_status' AND code = 'PENDIENTE';

UPDATE ref.category SET valid_transitions = '["COMPLETADA"]'::jsonb
WHERE scheme = 'dgi_ar_decision_status' AND code = 'EN_EJECUCION';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'dgi_ar_decision_status' AND code = 'COMPLETADA';

UPDATE ref.category SET valid_transitions = '["EN_GESTION", "CERRADO"]'::jsonb
WHERE scheme = 'dgi_escalation_status' AND code = 'ABIERTO';

UPDATE ref.category SET valid_transitions = '["RESUELTO", "CERRADO"]'::jsonb
WHERE scheme = 'dgi_escalation_status' AND code = 'EN_GESTION';

UPDATE ref.category SET valid_transitions = '["CERRADO"]'::jsonb
WHERE scheme = 'dgi_escalation_status' AND code = 'RESUELTO';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'dgi_escalation_status' AND code = 'CERRADO';

UPDATE ref.category SET valid_transitions = '["EN_EVALUACION", "RECHAZADA"]'::jsonb
WHERE scheme = 'dgi_request_status' AND code = 'RECIBIDA';

UPDATE ref.category SET valid_transitions = '["ACEPTADA", "RECHAZADA"]'::jsonb
WHERE scheme = 'dgi_request_status' AND code = 'EN_EVALUACION';

UPDATE ref.category SET valid_transitions = '["EN_EJECUCION"]'::jsonb
WHERE scheme = 'dgi_request_status' AND code = 'ACEPTADA';

UPDATE ref.category SET valid_transitions = '["COMPLETADA"]'::jsonb
WHERE scheme = 'dgi_request_status' AND code = 'EN_EJECUCION';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'dgi_request_status' AND code IN ('COMPLETADA', 'RECHAZADA');

-- Transiciones de risk_status
UPDATE ref.category SET valid_transitions = '["EN_EVALUACION", "ACEPTADO"]'::jsonb
WHERE scheme = 'risk_status' AND code = 'IDENTIFICADO';

UPDATE ref.category SET valid_transitions = '["EN_MITIGACION", "ACEPTADO", "CERRADO"]'::jsonb
WHERE scheme = 'risk_status' AND code = 'EN_EVALUACION';

UPDATE ref.category SET valid_transitions = '["MITIGADO", "CERRADO"]'::jsonb
WHERE scheme = 'risk_status' AND code = 'EN_MITIGACION';

UPDATE ref.category SET valid_transitions = '["CERRADO"]'::jsonb
WHERE scheme = 'risk_status' AND code IN ('MITIGADO', 'ACEPTADO');

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'risk_status' AND code = 'CERRADO';

-- Transiciones de budget_commitment_status
UPDATE ref.category SET valid_transitions = '["VIGENTE", "ANULADO"]'::jsonb
WHERE scheme = 'budget_commitment_status' AND code = 'EMITIDO';

UPDATE ref.category SET valid_transitions = '["EJECUTADO", "VENCIDO", "ANULADO"]'::jsonb
WHERE scheme = 'budget_commitment_status' AND code = 'VIGENTE';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'budget_commitment_status' AND code IN ('EJECUTADO', 'ANULADO');

UPDATE ref.category SET valid_transitions = '["VIGENTE"]'::jsonb
WHERE scheme = 'budget_commitment_status' AND code = 'VENCIDO';

-- Transiciones de agreement_state
UPDATE ref.category SET valid_transitions = '["EN_NEGOCIACION", "CANCELADO"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'BORRADOR';

UPDATE ref.category SET valid_transitions = '["EN_REVISION_JURIDICA", "BORRADOR"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'EN_NEGOCIACION';

UPDATE ref.category SET valid_transitions = '["FIRMADO_GORE", "EN_NEGOCIACION"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'EN_REVISION_JURIDICA';

UPDATE ref.category SET valid_transitions = '["FIRMADO_CONTRAPARTE"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'FIRMADO_GORE';

UPDATE ref.category SET valid_transitions = '["VIGENTE", "TDR_PENDIENTE"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'FIRMADO_CONTRAPARTE';

UPDATE ref.category SET valid_transitions = '["FORMALIZADO"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'TDR_PENDIENTE';

UPDATE ref.category SET valid_transitions = '["VIGENTE"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'FORMALIZADO';

UPDATE ref.category SET valid_transitions = '["EN_MODIFICACION", "VENCIDO", "TERMINADO", "RESCILIADO"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'VIGENTE';

UPDATE ref.category SET valid_transitions = '["VIGENTE"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'EN_MODIFICACION';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'agreement_state' AND code IN ('VENCIDO', 'TERMINADO', 'RESCILIADO');

-- Transiciones de rendition_state (8-phase SISREC + APROBADA_PARCIALMENTE)
UPDATE ref.category SET valid_transitions = '["EN_REVISION_RTF"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'PENDIENTE';

UPDATE ref.category SET valid_transitions = '["OBSERVADA", "VISADA_RTF"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'EN_REVISION_RTF';

UPDATE ref.category SET valid_transitions = '["EN_REVISION_UCR"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'VISADA_RTF';

UPDATE ref.category SET valid_transitions = '["OBSERVADA", "APROBADA", "APROBADA_PARCIALMENTE", "RECHAZADA"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'EN_REVISION_UCR';

UPDATE ref.category SET valid_transitions = '["EN_REVISION_RTF"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'OBSERVADA';

UPDATE ref.category SET valid_transitions = '["EN_REVISION_RTF"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'APROBADA_PARCIALMENTE';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'rendition_state' AND code IN ('APROBADA', 'RECHAZADA');

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'EN_REVISION';

-- Transiciones de act_state. ANULADO es transversal desde todo estado no terminal.
UPDATE ref.category SET valid_transitions = '["EN_REVISION", "ANULADO"]'::jsonb
WHERE scheme = 'act_state' AND code = 'BORRADOR';

UPDATE ref.category SET valid_transitions = '["VISADO", "BORRADOR", "ANULADO"]'::jsonb
WHERE scheme = 'act_state' AND code = 'EN_REVISION';

UPDATE ref.category SET valid_transitions = '["FIRMADO", "ANULADO"]'::jsonb
WHERE scheme = 'act_state' AND code = 'VISADO';

UPDATE ref.category SET valid_transitions = '["ENVIADO_CGR", "ANULADO"]'::jsonb
WHERE scheme = 'act_state' AND code = 'FIRMADO';

UPDATE ref.category SET valid_transitions = '["TOMADO_RAZON", "RECHAZADO_CGR", "OBSERVADO", "ANULADO"]'::jsonb
WHERE scheme = 'act_state' AND code = 'ENVIADO_CGR';

UPDATE ref.category SET valid_transitions = '["ENVIADO_CGR", "ANULADO"]'::jsonb
WHERE scheme = 'act_state' AND code = 'OBSERVADO';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'act_state' AND code IN ('TOMADO_RAZON', 'RECHAZADO_CGR', 'ANULADO');

-- Transiciones de payment_status (CAT-005 FIX)
UPDATE ref.category SET valid_transitions = '["EN_PROCESO", "DIFERIDO"]'::jsonb
WHERE scheme = 'payment_status' AND code = 'PENDIENTE';

UPDATE ref.category SET valid_transitions = '["PAGADO", "RECHAZADO"]'::jsonb
WHERE scheme = 'payment_status' AND code = 'EN_PROCESO';

UPDATE ref.category SET valid_transitions = '["EN_PROCESO"]'::jsonb
WHERE scheme = 'payment_status' AND code = 'DIFERIDO';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'payment_status' AND code IN ('PAGADO', 'RECHAZADO');

-- Transiciones de file_status (CAT-005 FIX)
UPDATE ref.category SET valid_transitions = '["EN_TRAMITE"]'::jsonb
WHERE scheme = 'file_status' AND code = 'INICIADO';

UPDATE ref.category SET valid_transitions = '["PENDIENTE_INFO", "EN_FIRMA", "ARCHIVADO"]'::jsonb
WHERE scheme = 'file_status' AND code = 'EN_TRAMITE';

UPDATE ref.category SET valid_transitions = '["EN_TRAMITE"]'::jsonb
WHERE scheme = 'file_status' AND code = 'PENDIENTE_INFO';

UPDATE ref.category SET valid_transitions = '["RESUELTO"]'::jsonb
WHERE scheme = 'file_status' AND code = 'EN_FIRMA';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'file_status' AND code IN ('RESUELTO', 'ARCHIVADO');

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES REMEDIACIÓN PRE-FASE 2 (2026-01-29)
-- ============================================================================

-- SUBTIPOS DE RESOLUCIÓN (para core.resolution)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('resolution_subtype', 'APRUEBA_CONVENIO', 'Aprueba Convenio', 'Resolución que aprueba un convenio de transferencia', 1),
('resolution_subtype', 'MODIFICA_CONVENIO', 'Modifica Convenio', 'Resolución que modifica un convenio existente', 2),
('resolution_subtype', 'APRUEBA_PAGO', 'Aprueba Estado de Pago', 'Resolución que aprueba un estado de pago', 3),
('resolution_subtype', 'MODIFICA_PRESUPUESTO', 'Modificación Presupuestaria', 'Decreto de modificación presupuestaria', 4),
('resolution_subtype', 'TERMINO_ANTICIPADO', 'Término Anticipado', 'Resolución de término anticipado de convenio', 5),
('resolution_subtype', 'PRORROGA', 'Prórroga', 'Resolución de prórroga de plazos', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- TIPOS DE DOCUMENTO (para core.document)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('document_type', 'CONVENIO', 'Convenio', 'Documento de convenio de transferencia', 1),
('document_type', 'RESOLUCION', 'Resolución', 'Resolución exenta o afecta', 2),
('document_type', 'DECRETO', 'Decreto', 'Decreto alcaldicio o regional', 3),
('document_type', 'ESTADO_PAGO', 'Estado de Pago', 'Documento de estado de pago', 4),
('document_type', 'CERTIFICADO', 'Certificado', 'Certificado de avance u otro', 5),
('document_type', 'BOLETA_GARANTIA', 'Boleta de Garantía', 'Boleta de garantía bancaria', 6),
('document_type', 'INFORME_TECNICO', 'Informe Técnico', 'Informe de supervisión técnica', 7),
('document_type', 'RENDICION', 'Rendición', 'Documento de rendición de cuentas', 8),
('document_type', 'FACTURA', 'Factura', 'Factura electrónica', 9),
('document_type', 'ORDEN_COMPRA', 'Orden de Compra', 'Orden de compra MercadoPúblico', 10),
('document_type', 'PLANO', 'Plano', 'Plano técnico o arquitectónico', 11),
('document_type', 'OTRO', 'Otro', 'Otro tipo de documento', 99)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ROLES EN COMITÉ (para core.committee_member)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('role_in_committee', 'PRESIDENTE', 'Presidente', 'Presidente del comité', 1),
('role_in_committee', 'SECRETARIO', 'Secretario', 'Secretario del comité', 2),
('role_in_committee', 'VOCAL', 'Vocal', 'Miembro con voz y voto', 3),
('role_in_committee', 'ASESOR', 'Asesor', 'Asesor técnico sin voto', 4),
('role_in_committee', 'INVITADO', 'Invitado', 'Invitado sin voz ni voto', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- ============================================================================
--    RESOLUCIÓN DE JERARQUÍAS (parent_code -> parent_id)
-- ============================================================================
-- ref.category soporta jerarquía por FK (parent_id). El seed usa parent_code
-- por legibilidad; este paso materializa la relación referencial.
UPDATE ref.category AS child
SET parent_id = parent.id
FROM ref.category AS parent
WHERE child.parent_code IS NOT NULL
  AND parent.scheme = child.scheme
  AND parent.code = child.parent_code;

DO $$
DECLARE
    v_unresolved INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_unresolved
    FROM ref.category
    WHERE parent_code IS NOT NULL
      AND parent_id IS NULL;

    IF v_unresolved > 0 THEN
        RAISE NOTICE 'WARN: % categorías con parent_code sin parent_id (revisar seed)', v_unresolved;
    END IF;
END $$;

-- ============================================================================
--    FIN SEED DATA
-- ============================================================================
-- Total schemes: 83+
-- Total categories: ~385
-- Total actors: 23
-- Total commitment types: 10
-- Última actualización: 2026-01-30 (v3.4)
-- ============================================================================
