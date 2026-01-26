-- ============================================================================
-- GORE_OS v2.0 - SEED DATA
-- ============================================================================
-- Archivo: goreos_seed.sql
-- Descripción: Datos iniciales para ref.category (75+ schemes) y ref.actor
-- Generado: 2026-01-26
-- Fuentes: planclaude.md, especificaciones.md, goreNubleOntology.ttl,
--          goreNubleReferenceData.ttl, tdeCore.ttl, omega_gore_nuble_mermaid.md
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
-- scheme='ipr_state' ↔ gnub:IPRState (28 estados operativos)
-- scheme='mechanism_type' ↔ gnub:FinancingMechanism (7 tracks)
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
('ipr_type', 'PROGRAMA_SOCIAL', 'Programa Social', 'Programas sociales operativos', 7)
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

-- ESTADOS IPR OPERATIVOS (28 estados - gnub:IPRState subclasses)
-- Fuente: goreNubleOntology.ttl:768-805
INSERT INTO ref.category (scheme, code, label, description, parent_code, sort_order) VALUES
-- Estados Universales (gnub:UniversalIPRState)
('ipr_state', 'INGRESADO', 'Ingresado', 'Iniciativa ingresada al sistema', NULL, 1),
('ipr_state', 'EN_REVISION', 'En Revisión', 'Revisión de admisibilidad', NULL, 2),
('ipr_state', 'ADMISIBLE', 'Admisible', 'Cumple requisitos formales', NULL, 3),
('ipr_state', 'INADMISIBLE', 'Inadmisible', 'No cumple requisitos formales', NULL, 4),
('ipr_state', 'EN_EVALUACION', 'En Evaluación', 'En proceso de evaluación técnica', NULL, 5),
('ipr_state', 'CDP_EMITIDO', 'CDP Emitido', 'Certificado de disponibilidad presupuestaria emitido', NULL, 6),
('ipr_state', 'EN_FORMALIZACION', 'En Formalización', 'Preparando convenio/contrato', NULL, 7),
('ipr_state', 'FORMALIZADO', 'Formalizado', 'Convenio/contrato firmado', NULL, 8),
('ipr_state', 'EN_EJECUCION', 'En Ejecución', 'Ejecución física y financiera activa', NULL, 9),
('ipr_state', 'SUSPENDIDO', 'Suspendido', 'Ejecución suspendida temporalmente', NULL, 10),
('ipr_state', 'EN_RENDICION', 'En Rendición', 'Proceso de rendición de cuentas', NULL, 11),
('ipr_state', 'CERRADO', 'Cerrado', 'Iniciativa cerrada administrativamente', NULL, 12),
('ipr_state', 'ANULADO', 'Anulado', 'Iniciativa anulada', NULL, 13),
-- Estados Proyecto (gnub:ProjectIPRState)
('ipr_state', 'RS', 'RS', 'Rate of Social Return - Tasa Social calculada', 'PROYECTO', 20),
('ipr_state', 'FI', 'FI', 'Favorable Incondicional', 'PROYECTO', 21),
('ipr_state', 'FC', 'FC', 'Favorable Condicional', 'PROYECTO', 22),
('ipr_state', 'OT', 'OT', 'Objetado Técnicamente', 'PROYECTO', 23),
('ipr_state', 'AD', 'AD', 'Autorización de Diseño', 'PROYECTO', 24),
('ipr_state', 'EN_LICITACION', 'En Licitación', 'Proceso de licitación activo', 'PROYECTO', 25),
('ipr_state', 'ADJUDICADO', 'Adjudicado', 'Contrato adjudicado', 'PROYECTO', 26),
('ipr_state', 'EN_OBRA', 'En Obra', 'Ejecución física de obra', 'PROYECTO', 27),
('ipr_state', 'RECEPCION_PROVISORIA', 'Recepción Provisoria', 'Obra con recepción provisoria', 'PROYECTO', 28),
('ipr_state', 'RECEPCION_DEFINITIVA', 'Recepción Definitiva', 'Obra con recepción definitiva', 'PROYECTO', 29),
-- Estados Programa (gnub:ProgramIPRState)
('ipr_state', 'RF', 'RF', 'Recomendación Favorable', 'PROGRAMA', 30),
('ipr_state', 'ITF', 'ITF', 'Informe Técnico Favorable', 'PROGRAMA', 31),
('ipr_state', 'AT', 'AT', 'Aprobación Técnica', 'PROGRAMA', 32)
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
('funding_source', 'DONACION', 'Donación', 'Donaciones y aportes externos', 6)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- MECANISMOS DE FINANCIAMIENTO - 7 TRACKS (omega:659-724)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('mechanism_type', 'MEC_SNI', 'Track A: SNI General', '>15k UTM, MDSF evalúa, producto RS', 1),
('mechanism_type', 'MEC_C33', 'Track B: Circular 33', 'C33, conservación/ANF, producto AD', 2),
('mechanism_type', 'MEC_FRIL', 'Track C: FRIL', '<4.545 UTM, GORE evalúa, producto AT', 3),
('mechanism_type', 'MEC_GLOSA06', 'Track D1: Glosa 06', 'Ejecución Directa, DIPRES/SES, producto RF', 4),
('mechanism_type', 'MEC_TRANSFER', 'Track D2: Transferencias', 'Transferencias, Comité GORE, producto ITF', 5),
('mechanism_type', 'MEC_SUBV8', 'Track E1: Subvención 8%', '8% concursable, Comisión, producto Puntaje', 6),
('mechanism_type', 'MEC_FRPD', 'Track E2: FRPD Royalty', 'Royalty I+D+i, ANID/CORFO, producto Elegibilidad', 7)
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
('event_type', 'CIERRE', 'Cierre', 'Evento de cierre', 12)
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
('act_type', 'INFORME', 'Informe', 'Informe técnico o administrativo', 5)
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
('act_state', 'TRAMITADO', 'Tramitado', 5),
('act_state', 'TOMADO_RAZON', 'Toma de Razón', 6),
('act_state', 'RECHAZADO_CGR', 'Rechazado CGR', 7),
('act_state', 'ANULADO', 'Anulado', 8)
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

-- RESULTADO CGR
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('cgr_outcome', 'TOMA_RAZON', 'Toma de Razón', 'CGR aprueba', 1),
('cgr_outcome', 'CURSA_OBS', 'Cursa con Observaciones', 'CGR aprueba con observaciones', 2),
('cgr_outcome', 'REPRESENTA', 'Representa', 'CGR rechaza', 3),
('cgr_outcome', 'RETIRO', 'Retiro', 'GORE retira para corrección', 4),
('cgr_outcome', 'EXENTO', 'Exento', 'No requiere toma de razón', 5)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
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
('org_type', 'EMPRESA', 'Empresa', 'Entidad privada', 10)
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
('agreement_state', 'VIGENTE', 'Vigente', 6),
('agreement_state', 'EN_MODIFICACION', 'En Modificación', 7),
('agreement_state', 'VENCIDO', 'Vencido', 8),
('agreement_state', 'TERMINADO', 'Terminado', 9),
('agreement_state', 'RESCILIADO', 'Resciliado', 10)
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

-- ============================================================================
--    SCHEMA: ref.category - SCHEMES ESPECIFICACIONES.MD (NUEVOS)
-- ============================================================================

-- ROLES DEL SISTEMA (RF-001, RF-002)
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('system_role', 'ADMIN_SISTEMA', 'Administrador del Sistema', 'Configura sistema, usuarios, importa datos', 1),
('system_role', 'ADMIN_REGIONAL', 'Administrador Regional', 'Visión 360°, coordina divisiones, gestiona crisis', 2),
('system_role', 'JEFE_DIVISION', 'Jefe de División', 'Supervisa división, verifica trabajo, asigna', 3),
('system_role', 'ENCARGADO', 'Encargado', 'Ejecuta trabajo, actualiza avances, reporta problemas', 4)
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
--    FIN SEED DATA
-- ============================================================================
-- Total schemes: 75+
-- Total categories: ~350
-- Total actors: 23
-- Total commitment types: 10
-- ============================================================================
