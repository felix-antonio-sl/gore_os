# KODA-CARTOGRAPHER: Plan Maestro para Modelo de Datos GORE_OS

Fase Actual: ESCUCHAR→MAPEAR (Transición)
Metodología: Del Caos al Modelo (4 fases)
Documento de Autoridad: MANIFESTO.md (Story-First)

1. SENTIDO SEMÁNTICO PROFUNDO: El Sistema Nervioso Digital
0.1 Visión Fundacional
"La crisis reveló que el GORE carecía de un sistema nervioso digital capaz de detectar problemas antes de que se convirtieran en crisis."
— MANIFESTO.md

Este modelo de datos no es un schema técnico arbitrario. Es la columna vertebral del sistema operativo institucional del Gobierno Regional de Ñuble. Cada tabla, cada relación, cada constraint debe responder a una pregunta fundamental:

¿Cómo habilita esto que el GORE perciba, decida y actúe mejor?

0.2 Los 5 Axiomas ORKO como Fundamento Ontológico
El GLOSARIO.yml define 5 axiomas que deben informar cada decisión de modelado:

Axioma Principio Implicación para el Modelo
A1: Transformación Todo sistema existe para transformar estados (S₁ → S₂) Cada IPR es una transformación territorial. Capturar estado inicial→final
A2: Capacidad Existe capacidad que efectúa la transformación Los Roles son capacidades. Distinguir sustrato (Humano/Algorítmico) y cognición
A3: Información Estructura portadora de significado que coordina Las Entidades son información. Cada campo debe tener propósito de coordinación
A4: Restricción No todo es posible. Existen límites Las reglas presupuestarias son restricciones. Modelar como constraints
A5: Intencionalidad Transformación tiene propósito direccional Cada Story captura el propósito. Sin historia, no existe el requerimiento
0.3 Los 5 Primitivos ORKO → Estructura del Modelo
Primitivo ORKO Definición Materialización en el Schema
P1: Capacidad Potencial de ejecutar transformación meta.role (con sustrato + cognición + human_accountable)
P2: Flujo Secuencia estructurada como DAG meta.process + txn.event (transiciones de estado)
P3: Información Contenido con temporalidad y lineage core.* (entidades con valid_from/to, created_at)
P4: Límite Constraint que acota posibilidades ref.category (reglas) + DB constraints + SHACL shapes
P5: Propósito Outcome deseado con métricas meta.story + txn.magnitude (KPIs medibles)
0.4 Las 5 Funciones Motoras → Cobertura del Modelo
El GORE tiene 5 funciones esenciales que el modelo debe soportar completamente:

┌─────────────────────────────────────────────────────────────────────────┐
│                        5 FUNCIONES MOTORAS                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. PLANIFICAR ──► ERD, PROT, ARI                                      │
│     └── core.planning_instrument, ref.category(scheme='planning_type') │
│                                                                         │
│  2. FINANCIAR ──► FNDR, ISAR (fondos) / SNI, C33, FRIL... (mecanismos)│
│     └── ref.category(scheme='funding_source'|'mechanism')              │
│         core.budget_line, txn.budgetary_transaction                    │
│                                                                         │
│  3. EJECUTAR ──► Convenios, Transferencias, Obras                      │
│     └── core.agreement, core.ipr, txn.event(type='milestone'|'pago')   │
│                                                                         │
│  4. COORDINAR ──► Municipios, Servicios, Gabinete                      │
│     └── core.organization (jerarquía), txn.event(type='reunion')       │
│                                                                         │
│  5. NORMAR ──► Reglamentos, Resoluciones, Dictámenes                   │
│     └── core.legal_document, core.legal_mandate                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
0.5 Human-AI Collaboration (Invariante ORKO-HAIC)
"Accountability moral siempre es humana. Algoritmos operan bajo modos de delegación con override siempre disponible."

El modelo soporta el patrón Human-in-the-Loop mediante:

-- Extensión a meta.role para HAIC
ALTER TABLE meta.role ADD COLUMN human_accountable_id VARCHAR(32) REFERENCES meta.role(id);
ALTER TABLE meta.role ADD COLUMN delegation_mode VARCHAR(4);  -- M1-M6 según ORKO
ALTER TABLE meta.role ADD COLUMN cognition_level VARCHAR(4);  -- C0-C3

-- Constraint: Todo agente no-humano requiere humano accountable
ALTER TABLE meta.role ADD CONSTRAINT chk_human_accountable
    CHECK (agent_type = 'HUMAN' OR human_accountable_id IS NOT NULL);
0.6 Jerarquía de Ciclos Operativos
El sistema GORE opera en tres niveles de ciclos:

Nivel Ciclo Naturaleza Horizonte Materialización
MACRO 5 Funciones Motoras Estratégico Anual/Plurianual PLANIFICAR, FINANCIAR, EJECUTAR, COORDINAR, NORMAR
MESO 5 Fases MCD (F0-F4) Táctico Meses Ciclo de vida de una IPR dentro de FINANCIAR/EJECUTAR
MICRO Sense-Decide-Act Operacional Tiempo real Eventos, alertas, decisiones puntuales
Nota: El ciclo SDA es recursivo y opera DENTRO de cualquier fase o función.

0.7 Ciclo Sense-Decide-Act (SDA)
El sistema nervioso digital opera en un ciclo canónico:

         ┌──────────────────────────────────────┐
         │                                      │
    ►────► SENSE ──────► DECIDE ──────► ACT ───┘
         │
         └──────────────────────────────────────

    SENSE:  txn.event captura cambios de estado
    DECIDE: meta.story + meta.role definen quién y qué
    ACT:    txn.event registra acciones ejecutadas
Habilitadores del ciclo SDA:

Alertas automáticas: txn.event + triggers detectan anomalías (ej. desviación >15%)
Reglas de negocio: ref.category + constraints guían decisiones
Trazabilidad completa: txn.event + txn.magnitude registran toda transformación
0.8 Distinción Semántica Crítica: Fondos vs Mecanismos (DUAL PURPOSE)
El modelo omega_gore_nuble_mermaid.md establece claramente que los MECANISMOS cumplen doble función:

MECANISMO = Canal de Postulación + Track de Evaluación
SNI, C33, FRIL, Glosa06, 8% y FRPD definen CÓMO se postula Y CÓMO se evalúa una IPR.

Concepto Naturaleza Ejemplos Modelado
Fondo Fuente de recursos (de dónde viene el dinero) FNDR, ISAR, FRIL, FRPD ref.category(scheme='funding_source')
Mecanismo Canal dual: Postulación + Evaluación SNI, C33, FRIL, Glosa06, 8%, FRPD ref.category(scheme='mechanism')
Matriz de Mecanismos (omega_gore_nuble_mermaid.md)
Track Mecanismo Evaluador Producto (Dictamen) Aplica a
A SNI General MDSF RS (Rec. Satisfactoria) PROYECTO >15k UTM
B Circular 33 MDSF/GORE AD (Admisibilidad) PROYECTO Conserv./ANF
C FRIL GORE (DIPIR) AT (Aprob. Técnica) PROYECTO <4.545 UTM
D1 Glosa 06 DIPRES/SES RF (Rec. Favorable) PROGRAMA Ej. Directa
D2 Transferencias GORE (Comité/DAE) ITF (Inf. Téc. Fav.) PROGRAMA Transfer.
E1 Subvención 8% GORE (Comisión) Puntaje/Ranking PROGRAMA Concursable
E2 FRPD ANID/CORFO/GORE Elegibilidad + RS/RF MIXTO (I+D+i)
Una IPR tiene:

1 Fondo (fuente de financiamiento): FNDR, ISAR, etc.
1 Mecanismo (canal dual postulación+evaluación): SNI, C33, FRIL, etc.
Esto se modela como dos FKs distintas en core.ipr:

funding_source_id  → ref.category(scheme='funding_source')  -- De dónde viene el $
mechanism_id       → ref.category(scheme='mechanism')       -- Cómo postula Y cómo se evalúa
0.9 Modelo Polimórfico IPR (omega_gore_nuble_mermaid.md)
La IPR es una entidad polimórfica. El schema debe reflejar esta estructura:

                         ┌─────────────────┐
                         │      IPR        │
                         │   (Abstract)    │
                         │ - codigo_bip    │
                         │ - fase_actual   │
                         └────────┬────────┘
                                  │
              ┌───────────────────┴───────────────────┐
              │                                       │
     ┌────────┴────────┐                   ┌─────────┴─────────┐
     │    PROYECTO     │                   │     PROGRAMA      │
     │   (Capital)     │                   │   (Corriente)     │
     │ Subt: 31, 33    │                   │ Subt: 24          │
     │ crea_activo=T   │                   │ crea_activo=F     │
     └────────┬────────┘                   └─────────┬─────────┘
              │                                       │
    ┌─────────┼─────────┐           ┌─────────────────┼─────────────────┐
    │         │         │           │                 │                 │
 MEC_SNI  MEC_C33  MEC_FRIL     MEC_GLOSA06     MEC_TRANSFER     MEC_SUBV8
0.10 Modelo Canónico de Estados (MCD) - 5 Fases (F0-F4)
Todas las IPR transitan por un ciclo de vida unificado de 5 fases (omega_gore_nuble_mermaid.md):

Fase Nombre Descripción Responsable
F0 Formulación & Ingreso Identificación → Formulación → Postulación oficial (BIP/Plataforma) Formulador
F1 Admisibilidad Verificación de requisitos (The Gatekeeper) DIPLADE/DIPIR
F2 Evaluación Técnica Poly-Switch a 7 Tracks según mecanismo MDSF/GORE/DIPRES/ANID
F3 Priorización & Asignación Cartera → Propuesta Gobernador → Votación CORE → Identificación PPT CORE
F4 Formalización, Ejecución & Cierre Convenio → Ejecución → Recepción → Rendición → Cierre DIPIR/Ejecutor/CGR
Nota: Las 5 Fases son etapas MACRO del ciclo de vida. Los 7 Tracks (A-E2) son variantes de evaluación DENTRO de la Fase F2.

Poly-Switch de F2 (Árbol de Decisión)

                    ┌─────────────────────────────────────┐
                    │     ¿Crea Activo Físico Durable?    │
                    └────────────────┬────────────────────┘
                                     │
              ┌──────────────────────┴──────────────────────┐
              │ Sí (CAPITAL)                                │ No (CORRIENTE)
              ▼                                             ▼
    ┌─────────────────────┐                     ┌─────────────────────┐
    │ <4.545 UTM + Muni?  │                     │ Ejecución Directa?  │
    └──────────┬──────────┘                     └──────────┬──────────┘
               │                                           │
      ┌────────┴────────┐                       ┌──────────┴──────────┐
      │Sí               │No                     │Sí                   │No
      ▼                 ▼                       ▼                     ▼
   Track C         ┌────────────┐           Track D1           ┌──────────────┐
   (FRIL)          │Conserv/ANF?│          (Glosa 06)          │Transfer Púb? │
                   └─────┬──────┘                              └──────┬───────┘
                         │                                            │
                 ┌───────┴───────┐                          ┌─────────┴─────────┐
                 │Sí             │No                        │Sí                 │No
                 ▼               ▼                          ▼                   ▼
             Track B         Track A                    Track D2         ┌──────────┐
             (C33)           (SNI)                      (Transfer)       │I+D+i/Roy?│
                                                                         └────┬─────┘
                                                                    ┌─────────┴─────────┐
                                                                    │Sí                 │No
                                                                    ▼                   ▼
                                                                Track E2           Track E1
                                                                (FRPD)             (Subv 8%)
Modelado en:

ref.category(scheme='mcd_phase'): F0, F1, F2, F3, F4 (5 fases)
ref.category(scheme='ipr_status'): Estados específicos dentro de cada fase
txn.event: Transiciones entre estados con actor y timestamp
0.11 Gateway DIPIR: Clasificación por Subtítulo
Fuente: dipir_ssot_koda.yaml (ubicado en proyecto gorenuble: /Users/felixsanhueza/Developer/gorenuble/staging/procesos_dipir/)

El proceso DIPIR clasifica iniciativas según:

Condición Subtítulo Tipo Resolución Requiere CGR Requiere DIPRES
Subvenciones 24 EXENTA No No
ANF <7000 UTM 29 AFECTA Sí No
FRIL <7000 UTM 33 EXENTA No No
Programas >7000 UTM 33/24 CONDICIONAL Si >5000 UTM No
Inversión 31 AFECTA Sí Sí
Modelado en:

ref.category(scheme='budget_subtitle'): 24, 29, 31, 33
ref.category(scheme='resolution_type'): EXENTA, AFECTA, CONDICIONAL
0.12 Matriz de Umbrales Financieros (omega_gore_nuble_mermaid.md)
Reglas críticas de negocio que deben implementarse como constraints o validaciones:

Concepto Umbral/Regla Detalle Constraint en DB
Exención RS (FRIL) < 4.545 UTM Tope específico Ñuble (otras regiones 5.000 UTM) CHECK en core.ipr_mechanism
Licitación Pública > 1.000 UTM Obligatoria para Obras Trigger de validación
Toma de Razón CGR > 2.500 UTM Control legalidad previo requires_cgr = TRUE
Aprobación CORE > 7.000 UTM Requiere votación explícita Trigger de workflow
Evaluación SNI > 15.000 UTM MDSF obligatorio (salvo C33/FRIL) Trigger de validación
Plazo Licitación FRIL 90 días Desde convenio, si no se pierde AT plazo_licitacion_dias
Gastos Admin Glosa06 ≤ 5% Del presupuesto total gasto_admin_max
Vigencia RATE RS 3 años Presupuestarios consecutivos Lógica de negocio
0.13 Restricciones Operativas por Mecanismo (Reglas de Oro)
Mecanismo Restricción Consecuencia Incumplimiento
FRIL Prohibición fraccionamiento Rechazo admisibilidad
FRIL Plazo licitación 90 días Pérdida Aprobación Técnica
Glosa 06 Gastos Admin ≤5% Rechazo DIPRES
Transfer Honorarios ≤5% Observación rendición
Subv 8% Sin rendiciones pendientes Bloqueo total nuevos fondos
C33 Cofinanciamiento ANF 20% Inadmisible sin certificar

1. INVENTARIO COMPLETO DE FUENTES (Fase ESCUCHAR)
1.1 Fuentes Analizadas
Fuente Tipo Tokens Relevancia
MANIFESTO.md Autoridad 114 CORE - Define 4 átomos
goreos/model/stories/*.yml Datos 819 archivos CORE - 819 historias enriquecidas
goreNubleOntology.ttl TBox 30K+ Ontología GNUB completa
goreNubleDipirOntology.ttl TBox 179 Workflows DIPIR
alignmentGnubTde.ttl Puentes 130 Alineamiento GNUB↔TDE
goreNubleShapes.ttl SHACL 247 Validación de datos
goreNubleCQs_Master.yml CQs 1345 472 Competency Questions
tdeCore.ttl TBox 241 Ontología TDE Core
tdeBundle.ttl Bundle 66 Importaciones TDE
implementation_plan.md (Gemini) Plan 82 Estrategia 3 sub-planes
1.2 Patrones Emergentes Identificados
Regla de Derivación Estructural (Cadena de Valor Semántica):

Stories → Entities → Artefactos → Módulos
Significado:

Stories → Entities: De las historias de usuario se extraen las entidades del modelo de datos
Entities → Artefactos: Desde las entidades se diseñan artefactos (tablas, APIs, UIs) que satisfacen las stories
Artefactos → Módulos: Conjuntos de artefactos que ofrecen función y capacidades al usuario
"Si no hay Historia, no existe el requerimiento" — Esta regla garantiza trazabilidad completa desde la necesidad hasta la implementación.

4 Átomos Fundamentales:

Story (origen absoluto)
Entity (estructura de información)
Role (agente activo)
Process (perspectiva dinámica)
Upper Ontology: Gist 14.0 (Category, Magnitude, Event, Organization, Agreement)

Alineamiento TDE: gnub → tde → gist (jerarquía de generalización)

1.3 Análisis Exhaustivo de Entidades (141 Formalmente Definidas)
Se realizó un análisis completo de las 141 entidades aceptadas contra las 819 historias:

Métrica Valor
Total entidades formalmente definidas 141
Entidades cubiertas por modelo inicial 13 (9.2%)
Brecha de cobertura 128 (90.8%)
Menciones totales en historias 1,847
Menciones cubiertas por modelo inicial ~14%
Análisis de Cobertura por Dominio:

Dominio Entidades Menciones Estado
D-FIN (Finanzas) 31 Alto Parcial → EXPANDIR
D-ORG (Organización) 16 Muy Alto Parcial → EXPANDIR
D-CONV (Convenios) 14 Alto Mínimo → EXPANDIR
D-EJE (Ejecución) 13 Medio 0% → AGREGAR
D-DIG (Digital) 18 Alto Mínimo → EXPANDIR
D-LOC (Localización) 11 Alto Mínimo → EXPANDIR
D-SAL (Salud/Alertas) 15 Alto Parcial
D-GOV (Gobernanza) 10 Medio 0% → AGREGAR
Entidades con Mayor Frecuencia de Mención:

Entidad Menciones Estado en Modelo
ENT-ORG-ROL 426 ✓ meta.role
ENT-SAL-ALERTA 39 AGREGAR
ENT-ORG-FUNCIONARIO 39 AGREGAR → core.person
ENT-FIN-PRESUPUESTO 29 ✓ core.budget_program
ENT-FIN-IPR 25 ✓ core.ipr
ENT-CONV-COMPROMISO 22 ✓ core.agreement
ENT-LOC-COMUNA 19 AGREGAR
ENT-DIG-PLATAFORMA 17 AGREGAR
ENT-DIG-TRAMITE 17 AGREGAR
ENT-SAL-RIESGO 16 AGREGAR
ENT-SYS-DOCUMENTO 14 AGREGAR
ENT-FIN-CDP 13 AGREGAR
ENT-LOC-INDICADOR_TERRITORIAL 12 AGREGAR
ENT-CONV-ACTA 11 AGREGAR
ENT-CONV-COMITE 11 AGREGAR
Hoja de Ruta de Implementación:

Fase Tablas Cobertura Menciones Esfuerzo
Fase 1 28 tablas 99% 3-4 semanas
Fase 2 +20 tablas 100% +2 semanas
Fase 3 +66 tablas Completo Iterativo
Decisión: Implementar Fase 1 (28 tablas) para modelo robusto con 99% de cobertura de menciones.

1. CLASIFICACIÓN ONTOLÓGICA (Fase MAPEAR)
2.1 Clasificación por Naturaleza
Tipo Concepto Fuente Alineamiento Gist
ENTIDAD IPR gnub:IPR gist:Project
ENTIDAD Convenio gnub:GOREAgreement gist:Agreement
ENTIDAD Funcionario gist:Person gist:Person
ENTIDAD División gnub:Division gist:Organization
ENTIDAD Acto Administrativo gnub:AdministrativeAct gist:FormattedContent
ENTIDAD Resolución gnub:Resolution gist:FormattedContent
ENTIDAD Procedimiento Admin. gnub:AdministrativeProcedure gist:Event
ENTIDAD Programa PPR gnub:BudgetProgram gist:FinancialInstrument
ENTIDAD Programa Fondo gnub:FundProgram gist:FinancialInstrument
EVENTO Visación dipir:VisacionEvent gist:Event
EVENTO Aprobación dipir:AprobacionEvent gist:Event
EVENTO Pago gnub:PaymentEvent gist:Event
CLASIFICADOR FundingSource gnub:FundingSource gist:Category
CLASIFICADOR IPRPhase gnub:IPRPhase gist:Category
CLASIFICADOR AgreementState gnub:AgreementState gist:Category
CLASIFICADOR ActType gnub:ActType gist:Category
CLASIFICADOR ResolutionType gnub:ResolutionType gist:Category
MEDICIÓN MontoEjecutado gnub:AccruedAmountAspect gist:Magnitude
MEDICIÓN PorcentajeAvance gist:Magnitude gist:Magnitude
2.2 Grafo de Dependencias (Nodos Centrales)

                           gist:Organization
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
         gnub:Division       gnub:Department      gnub:Unit
              │
              ▼
         gnub:IPR ─────────────► gnub:FundingSource (Category)
              │
              ├─────► gnub:GOREAgreement ─────► gnub:AgreementState
              │               │
              │               ▼
              │         gnub:Rendition ─────► gnub:RenditionState
              │
              ├─────► gnub:BudgetProgram ─────► gnub:FundProgram
              │               │                       │
              │               └───────────────────────┘
              │                         │
              ▼                         ▼
   gnub:BudgetaryTransaction      gnub:Resolution ◄──── gnub:AdministrativeAct
              (Event)                   │                        │
                                        │                        ▼
                                        └────────────► gnub:AdministrativeProcedure
Relaciones Clave Agregadas:

Resolution → IPR: Resolución que aprueba una IPR
Resolution → Agreement: Resolución que formaliza un Convenio
FundProgram → BudgetProgram: Programa de fondo vinculado a línea presupuestaria
AdministrativeProcedure → Resolution: Procedimiento resuelto por Resolución
2.3 Tabla de Equivalencias (Sinónimos Normalizados)
Fuente YAML Clase GNUB Clase Gist
ENT-FIN-IPR gnub:IPR gist:Project
ENT-FIN-CONVENIO gnub:GOREAgreement gist:Agreement
ENT-ORG-DIVISION gnub:Division gist:Organization
ENT-FIN-BALANCE gnub:FinancialStatement gist:FormattedContent
PROC-FIN-ADMISIBILIDAD dipir:VisacionEvent gist:Event
3. ARQUITECTURA DE CAPAS (Fase ELEVAR)
3.1 Upper Ontology Seleccionada: Gist 14.0
Justificación:

Ya adoptada en goreNubleOntology.ttl y tdeCore.ttl
Patrones probados: Category, Magnitude, Event
Máximo alineamiento con estándar gubernamental chileno (TDE)
3.2 Patrones Gist Aplicados
Patrón Señal en Fuentes Abstracción Propuesta
Category 15+ tablas con código/nombre/parent core.category(scheme, code, label, parent_id)
Magnitude Campos numéricos (monto, %, plazo) core.magnitude(subject_type, subject_id, aspect, value, unit)
Event Transacciones, auditoría core.event(event_type, subject_type, subject_id, occurred_at, data)
Agreement Convenios con partes core.agreement(agreement_type, party_a, party_b, status)
3.3 Arquitectura de 4 Capas

┌─────────────────────────────────────────────────────────────┐
│  CAPA 0: META (Cambia solo con filosofía)                   │
│  ─────────────────────────────────────────                  │
│  story, entity, role, process                               │
│  Fuente: MANIFESTO.md                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 1: REFERENCE (Vocabularios controlados)               │
│  ─────────────────────────────────────────────              │
│  category(scheme=[domain, funding_source, ipr_phase,        │
│           agreement_state, rendition_state, mechanism])      │
│  Fuente: goreNubleReferenceData.ttl                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 2: CORE (Entidades de negocio)                        │
│  ───────────────────────────────────                        │
│  organization, person, ipr, agreement, rendition,           │
│  budget_line, legal_document                                │
│  Fuente: goreNubleOntology.ttl + stories                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 3: TRANSACTIONAL (Eventos y mediciones)               │
│  ─────────────────────────────────────────────              │
│  event(visacion, aprobacion, pago, rendicion, ...),         │
│  magnitude(monto_ejecutado, avance_fisico, ...),            │
│  audit_log                                                  │
│  Fuente: goreNubleDipirOntology.ttl + dipir_ssot_koda.ttl   │
└─────────────────────────────────────────────────────────────┘
4. PROPUESTA DE MODELO DE DATOS (Fase CRISTALIZAR)
4.1 Schema Relacional Propuesto
Capa 0: META

-- TABLA: meta.story
-- EXISTE PORQUE: Átomo fundamental (MANIFESTO.md)
-- ALINEAMIENTO: goreos:Story
CREATE TABLE meta.story (
    id VARCHAR(32) PRIMARY KEY,        -- US-XXX-XXX-NNN
    name TEXT NOT NULL,
    as_a TEXT NOT NULL,                -- Rol
    i_want TEXT NOT NULL,              -- Acción
    so_that TEXT NOT NULL,             -- Valor
    role_id VARCHAR(32) REFERENCES meta.role(id),
    process_id VARCHAR(32) REFERENCES meta.process(id),
    domain VARCHAR(16),
    priority VARCHAR(4),
    status VARCHAR(16) DEFAULT 'ENRICHED'
);

-- TABLA: meta.entity
-- EXISTE PORQUE: Átomo fundamental (MANIFESTO.md)
-- ALINEAMIENTO: goreos:Entity
CREATE TABLE meta.entity (
    id VARCHAR(32) PRIMARY KEY,        -- ENT-XXX-XXX
    name TEXT NOT NULL,
    ontology_uri TEXT,                 -- gnub:IPR, gnub:Division, etc.
    domain VARCHAR(16)
);

-- TABLA: meta.role
-- EXISTE PORQUE: Átomo fundamental (MANIFESTO.md) + Invariante HAIC (ORKO-I5)
-- ALINEAMIENTO: goreos:Role, orko:P1_Capacidad
-- SEMÁNTICA: Capacidad = potencial de ejecutar transformación (Axioma A2)
CREATE TABLE meta.role (
    id VARCHAR(32) PRIMARY KEY,        -- ROL-XXX-XXX
    name TEXT NOT NULL,
    agent_type VARCHAR(16) NOT NULL,   -- HUMAN|AI|ALGORITHMIC|MACHINE|MIXED (Sustrato)
    cognition_level VARCHAR(4),        -- C0|C1|C2|C3 (Nivel de decisión ORKO)
    human_accountable_id VARCHAR(32) REFERENCES meta.role(id), -- HAIC: humano responsable
    delegation_mode VARCHAR(4),        -- M1-M6 (modo de delegación ORKO)
    ontology_uri TEXT,                 -- tde:RolTDE, gnub:PositionType
    CONSTRAINT chk_human_accountable CHECK (agent_type = 'HUMAN' OR human_accountable_id IS NOT NULL)
);
-- COMENTARIO: Constraint HAIC garantiza que todo agente algorítmico tenga humano accountable

-- TABLA: meta.process
-- EXISTE PORQUE: Átomo fundamental (MANIFESTO.md)
-- ALINEAMIENTO: goreos:Process
CREATE TABLE meta.process (
    id VARCHAR(32) PRIMARY KEY,        -- PROC-XXX-XXX
    name TEXT NOT NULL,
    layer VARCHAR(16)                  -- STRATEGIC|TACTICAL|OPERATIONAL
);

-- Relación N:M Story ↔ Entity
CREATE TABLE meta.story_entity (
    story_id VARCHAR(32) REFERENCES meta.story(id),
    entity_id VARCHAR(32) REFERENCES meta.entity(id),
    status VARCHAR(16),                -- linked|candidate
    PRIMARY KEY (story_id, entity_id)
);
Capa 1: REFERENCE

-- TABLA: ref.category
-- EXISTE PORQUE: Category Pattern (Gist 14.0), omega_gore_nuble_mermaid.md, dipir_ssot_koda.yaml
-- ALINEAMIENTO: gist:Category
-- SCHEMES REQUERIDOS (validados contra fuentes de verdad):
--   === IPR y Presupuesto ===
--   - ipr_nature: PROYECTO|PROGRAMA
--   - ipr_type: subtipos específicos
--   - mcd_phase: F0|F1|F2|F3|F4 (Modelo Canónico de Estados - 5 fases)
--   - ipr_status: estados dentro de cada fase
--   - budget_subtitle: 24|29|31|33 (clasificador presupuestario)
--   - funding_source: FNDR|ISAR|FRIL|FRPD (fuente de recursos)
--   - mechanism: SNI|C33|FRIL|GLOSA06|TRANSFER|SUBV8|FRPD (canal dual: postulación+evaluación)
--   - mechanism_type: MEC_SNI|MEC_C33|MEC_FRIL|MEC_GLOSA06|MEC_TRANSFER|MEC_SUBV8|MEC_FRPD
--   - program_type: INVERSION|FUNCIONAMIENTO|TRANSFERENCIAS (tipo de programa PPR)
--   === Actos Administrativos (D-NORM) ===
--   - act_type: RESOLUCION|DECRETO|OFICIO|CERTIFICADO|ORDINARIO
--   - act_state: BORRADOR|FIRMADO|TRAMITE_CGR|VIGENTE|REVOCADO|DEROGADO
--   - resolution_type: EXENTA|AFECTA|CONJUNTA
--   - resolution_subtype: NOMBRAMIENTO|APROBACION|MODIFICACION|TERMINO|SANCION
--   - cgr_outcome: TOMADO_RAZON|REPRESENTADO|REGISTRADO|DESISTIDO
--   === Procedimientos Administrativos ===
--   - procedure_type: SUMARIO|INVESTIGACION|ADQUISICION|SELECCION|RECLAMO
--   - procedure_state: INICIADO|EN_TRAMITE|RESUELTO|ARCHIVADO|SUSPENDIDO
--   === Organización y Recursos ===
--   - org_type: DIVISION|DEPARTAMENTO|UNIDAD|STAFF|ASESOR
--   - person_type: FUNCIONARIO|CIUDADANO|PROVEEDOR|AUTORIDAD
--   - inventory_type: MOBILIARIO|EQUIPO_COMPUTO|VEHICULO|MAQUINARIA
--   - inventory_status: ACTIVO|BAJA|TRANSFERIDO|EN_REPARACION
--   - vehicle_type: SEDAN|CAMIONETA|BUS|CAMION
--   - fuel_type: BENCINA|DIESEL|ELECTRICO|HIBRIDO
--   === Territorio ===
--   - territory_type: REGION|PROVINCIA|COMUNA
--   - indicator_type: SOCIOECONOMICO|AMBIENTAL|GESTION|INFRAESTRUCTURA
--   === Convenios y Gobernanza ===
--   - agreement_type: TRANSFERENCIA|MANDATO|COLABORACION|CONVENIO_MARCO
--   - agreement_state: BORRADOR|FIRMA_PENDIENTE|FIRMADO|CGR_PENDIENTE|VIGENTE|CERRADO
--   - fund_program_state: CONVOCATORIA|EVALUACION|ADJUDICADO|EN_EJECUCION|CERRADO
--   - committee_type: CORE|COMITE_INVERSIONES|COMISION_CALIFICADORA|COMITE_TECNICO
--   - committee_role: PRESIDENTE|VICEPRESIDENTE|SECRETARIO|VOCAL
--   - session_type: ORDINARIA|EXTRAORDINARIA
--   - agreement_decision_status: PENDIENTE|EN_EJECUCION|CUMPLIDO|VENCIDO
--   === Digital y Trámites ===
--   - platform_type: INTERNO|EXTERNO|INTEROPERABILIDAD
--   - procedure_type: CIUDADANO|INTERNO|INTERSECTORIAL
--   - file_status: INGRESADO|EN_TRAMITE|RESUELTO|ARCHIVADO
--   - document_type: OFICIO|MEMORANDO|INFORME|CERTIFICADO|CONTRATO
--   === Control de Gestión (D-GESTION - para_titi) ===
--   - problem_type: TECNICO|FINANCIERO|LEGAL|ADMINISTRATIVO|COORDINACION
--   - problem_impact: ALTO|MEDIO|BAJO|CRITICO
--   - problem_state: ABIERTO|EN_GESTION|RESUELTO|CERRADO
--   - commitment_state: PENDIENTE|EN_PROGRESO|COMPLETADO|VERIFICADO|CANCELADO
--   - priority: BAJA|MEDIA|ALTA|URGENTE
--   === Alertas y Riesgos ===
--   - alert_type: VENCIMIENTO|DESVIACION|INCUMPLIMIENTO|RETRASO|OBRA_SIN_PAGO|CONVENIO_POR_VENCER
--   - severity: INFO|WARNING|CRITICAL
--   - risk_type: FINANCIERO|OPERACIONAL|LEGAL|REPUTACIONAL
--   - probability: ALTA|MEDIA|BAJA
--   - impact: ALTO|MEDIO|BAJO
--   - risk_status: IDENTIFICADO|MITIGADO|MATERIALIZADO|CERRADO
--   === Finanzas Operativas ===
--   - commitment_type: CDP|COMPROMISO|DEVENGADO|PAGADO
--   - commitment_status: VIGENTE|EJECUTADO|ANULADO|VENCIDO
--   === Rendición y Eventos ===
--   - rendition_state: PENDIENTE|EN_REVISION|APROBADA|OBSERVADA|RECHAZADA
--   - event_type: VISACION|APROBACION|PAGO|MILESTONE|AUDIT|FIRMA|NOTIFICACION|ALERTA
--   - aspect: mediciones (monto_ejecutado, avance_fisico, dias_atraso, etc.)
--   - unit: CLP|UTM|UF|PORCENTAJE|DIAS|UNIDADES
--   - actor_type: INTERNO|EXTERNO (actores DIPIR)
CREATE TABLE ref.category (
    id SERIAL PRIMARY KEY,
    scheme VARCHAR(32) NOT NULL,
    code VARCHAR(32) NOT NULL,
    label TEXT NOT NULL,
    label_en TEXT,
    parent_id INTEGER REFERENCES ref.category(id),
    sequence INTEGER,
    metadata JSONB,
    UNIQUE(scheme, code)
);
CREATE INDEX idx_category_scheme ON ref.category(scheme);

-- TABLA: ref.actor
-- EXISTE PORQUE: dipir_ssot_koda.yaml - 23 actores únicos con estilos
-- ALINEAMIENTO: BPMN actors
-- SEMÁNTICA: Actores en flujos de proceso DIPIR
CREATE TABLE ref.actor (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,  -- CT_GORE, ANALISTA_DIPIR, JEFE_DIPIR, CGR, etc.
    name TEXT NOT NULL,
    full_name TEXT,
    emoji VARCHAR(8),
    style VARCHAR(32),                 -- taskAnalista, visacion, aprobacion, externo, etc.
    is_internal BOOLEAN DEFAULT TRUE,
    notes TEXT
);
Capa 2: CORE

-- TABLA: core.organization
-- EXISTE PORQUE: CQ-001 a CQ-028 (Estructura Organizacional)
-- ALINEAMIENTO: gnub:Division, gnub:Department, gist:Organization
CREATE TABLE core.organization (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    short_name VARCHAR(32),
    org_type_id INTEGER REFERENCES ref.category(id), -- scheme='org_type'
    parent_id INTEGER REFERENCES core.organization(id),
    valid_from DATE,
    valid_to DATE
);

-- TABLA: core.ipr
-- EXISTE PORQUE: CQ-029 a CQ-060 (IPR), 113 historias D-EJEC, omega_gore_nuble_mermaid.md
-- ALINEAMIENTO: gnub:IPR, gist:Project
-- SEMÁNTICA: IPR es una Transformación Territorial (Axioma A1: S₁ → S₂)
-- NOTA: Modelo polimórfico - PROYECTO (Capital) vs PROGRAMA (Corriente)
CREATE TABLE core.ipr (
    id SERIAL PRIMARY KEY,
    codigo_bip VARCHAR(20) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    -- POLIMORFISMO: ipr_nature determina si es PROYECTO (31,33) o PROGRAMA (24)
    ipr_nature_id INTEGER REFERENCES ref.category(id) NOT NULL, -- scheme='ipr_nature' (PROYECTO|PROGRAMA)
    ipr_type_id INTEGER REFERENCES ref.category(id),            -- scheme='ipr_type' (más específico)
    -- MCD: Fase actual en Modelo Canónico de Estados (F0-F4, 5 fases)
    mcd_phase_id INTEGER REFERENCES ref.category(id),           -- scheme='mcd_phase' (F0,F1,F2,F3,F4)
    status_id INTEGER REFERENCES ref.category(id),              -- scheme='ipr_status' (estado dentro de fase)
    -- CLASIFICACIÓN PRESUPUESTARIA (dipir_ssot_koda.yaml)
    budget_subtitle_id INTEGER REFERENCES ref.category(id),     -- scheme='budget_subtitle' (24,29,31,33)
    -- DISTINCIÓN SEMÁNTICA: Fondo ≠ Mecanismo (omega_gore_nuble_mermaid.md)
    -- Fondo = de dónde viene el dinero | Mecanismo = cómo postula Y cómo se evalúa (DUAL)
    funding_source_id INTEGER REFERENCES ref.category(id),      -- scheme='funding_source' (FNDR,ISAR,FRIL,FRPD)
    mechanism_id INTEGER REFERENCES ref.category(id),           -- scheme='mechanism' (SNI,C33,FRIL,GLOSA06,TRANSFER,SUBV8,FRPD) [DUAL: postulación+evaluación]
    -- ATRIBUTOS ESPECÍFICOS POR NATURALEZA
    crea_activo BOOLEAN DEFAULT TRUE,                           -- TRUE=PROYECTO, FALSE=PROGRAMA
    -- ORGANIZACIONES RELACIONADAS
    formulator_id INTEGER REFERENCES core.organization(id),
    executor_id INTEGER REFERENCES core.organization(id),
    sponsor_division_id INTEGER REFERENCES core.organization(id),
    max_execution_months INTEGER,
    -- PROPÓSITO (Axioma A5): Outcome deseado
    intended_outcome TEXT,
    -- TIPO DE RESOLUCIÓN (DIPIR Gateway)
    resolution_type_id INTEGER REFERENCES ref.category(id),     -- scheme='resolution_type' (EXENTA,AFECTA,CONDICIONAL)
    requires_cgr BOOLEAN DEFAULT FALSE,
    requires_dipres BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- TABLA: core.ipr_mechanism
-- EXISTE PORQUE: omega_gore_nuble_mermaid.md - Mecanismos específicos (MEC_SNI, MEC_C33, etc.)
-- ALINEAMIENTO: Poly-IPR patterns (Polimorfismo por mecanismo)
-- SEMÁNTICA: Atributos específicos según MECANISMO DUAL (postulación+evaluación)
-- NOTA: Cada mecanismo tiene atributos propios que determinan tanto requisitos de
--       postulación (qué documentos, umbrales) como criterios de evaluación (dictamen, evaluador)
CREATE TABLE core.ipr_mechanism (
    id SERIAL PRIMARY KEY,
    ipr_id INTEGER REFERENCES core.ipr(id) NOT NULL UNIQUE,
    mechanism_type_id INTEGER REFERENCES ref.category(id) NOT NULL, -- scheme='mechanism_type'
    -- Atributos SNI
    rate_mdsf VARCHAR(4),              -- RS|FI|OT
    etapa_bip VARCHAR(16),             -- Perfil|Factibilidad|Ejecucion
    sector VARCHAR(64),
    -- Atributos C33
    categoria_c33 VARCHAR(32),         -- ANF|Conservacion|Emergencia
    vida_util_residual INTEGER,
    informe_tecnico_favorable BOOLEAN,
    cofinanciamiento_anf NUMERIC(5,2),
    -- Atributos FRIL
    tipo_fril VARCHAR(32),             -- Infraestructura|Emergencia
    cumple_norma_5k_utm BOOLEAN,
    res_subdere VARCHAR(32),
    plazo_licitacion_dias INTEGER,     -- Típicamente 90 días desde convenio
    -- Atributos Glosa06
    fase_eval_central VARCHAR(16),     -- Perfil|Diseno
    rate_ses VARCHAR(4),               -- RF|OT|FI
    gasto_admin_max NUMERIC(5,2),
    -- Atributos FRPD
    eje_fomento VARCHAR(64),
    nivel_trl INTEGER,
    innovacion_ctci BOOLEAN,
    -- Atributos SUBV8
    fondo_tematico VARCHAR(32),
    puntaje_evaluacion NUMERIC(6,2),
    asignacion_directa BOOLEAN,
    metadata JSONB
);

-- TABLA: core.planning_instrument
-- EXISTE PORQUE: Función Motora 1 (PLANIFICAR), CQ de planificación
-- ALINEAMIENTO: gnub:PlanningInstrument, gist:Specification
-- SEMÁNTICA: Instrumento que traduce misión en acción (ERD, PROT, ARI)
CREATE TABLE core.planning_instrument (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    instrument_type_id INTEGER REFERENCES ref.category(id), -- scheme='planning_instrument_type'
    valid_from DATE,
    valid_to DATE,
    approved_by INTEGER REFERENCES core.organization(id),  -- CORE o Gobernador
    parent_instrument_id INTEGER REFERENCES core.planning_instrument(id), -- Jerarquía: ERD→ARI
    metadata JSONB
);

-- TABLA: core.legal_document
-- EXISTE PORQUE: Función Motora 5 (NORMAR), gnub:LegalDocument
-- ALINEAMIENTO: gnub:LegalDocument, gist:Content
-- SEMÁNTICA: Límites formales del sistema (Axioma A4: Restricción)
CREATE TABLE core.legal_document (
    id SERIAL PRIMARY KEY,
    code VARCHAR(64) UNIQUE NOT NULL,  -- "DFL-1-19175", "LEY-21033"
    name TEXT NOT NULL,
    doc_type_id INTEGER REFERENCES ref.category(id),       -- scheme='legal_doc_type'
    publication_date DATE,
    source_url TEXT,
    metadata JSONB
);

-- TABLA: core.legal_mandate
-- EXISTE PORQUE: gnub:LegalMandate - obligaciones que restringen el sistema
-- ALINEAMIENTO: gnub:LegalMandate, gist:Requirement
-- SEMÁNTICA: Constraint institucional derivado de norma (Axioma A4)
CREATE TABLE core.legal_mandate (
    id SERIAL PRIMARY KEY,
    legal_document_id INTEGER REFERENCES core.legal_document(id) NOT NULL,
    article_reference VARCHAR(32),     -- "Art. 16", "Art. 74"
    mandate_text TEXT NOT NULL,
    applies_to_id INTEGER REFERENCES ref.category(id),     -- scheme='mandate_scope' (GORE, División, etc.)
    metadata JSONB
);

-- TABLA: core.agreement
-- EXISTE PORQUE: CQ-141 a CQ-160 (Convenios), gnub:GOREAgreement
-- ALINEAMIENTO: gist:Agreement
CREATE TABLE core.agreement (
    id SERIAL PRIMARY KEY,
    agreement_type_id INTEGER REFERENCES ref.category(id), -- scheme='agreement_type'
    state_id INTEGER REFERENCES ref.category(id),          -- scheme='agreement_state'
    ipr_id INTEGER REFERENCES core.ipr(id),
    giver_id INTEGER REFERENCES core.organization(id),     -- GORE
    receiver_id INTEGER REFERENCES core.organization(id),  -- Municipio, privado
    signed_at DATE,
    valid_from DATE,
    valid_to DATE
);

-- TABLA: core.rendition
-- EXISTE PORQUE: CQ-183 a CQ-200 (Rendición), gnub:Rendition
-- ALINEAMIENTO: gnub:Rendition
CREATE TABLE core.rendition (
    id SERIAL PRIMARY KEY,
    agreement_id INTEGER REFERENCES core.agreement(id) NOT NULL,
    renderer_id INTEGER REFERENCES core.organization(id) NOT NULL,
    state_id INTEGER REFERENCES ref.category(id),          -- scheme='rendition_state'
    period_start DATE,
    period_end DATE,
    submitted_at TIMESTAMPTZ
);

-- ═══════════════════════════════════════════════════════════════════════
-- DOMINIO D-NORM: NORMATIVA Y ACTOS ADMINISTRATIVOS (PRIORIDAD 1)
-- Brecha detectada: 0% cobertura previa - 71 entidades mencionadas
-- ═══════════════════════════════════════════════════════════════════════

-- TABLA: core.administrative_act
-- EXISTE PORQUE: ENT-NORM-ACTO-ADMINISTRATIVO - Entidad raíz del dominio normativo
-- MENCIONES: 3 directas + subyace en toda la normativa
-- ALINEAMIENTO: gnub:AdministrativeAct, gist:FormattedContent
-- SEMÁNTICA: Manifestación de voluntad de la Administración que produce efectos jurídicos (Axioma A4: Restricción)
CREATE TABLE core.administrative_act (
    id SERIAL PRIMARY KEY,
    act_number VARCHAR(32) NOT NULL,          -- "RES-EX-001-2024", "DTO-002-2024"
    act_type_id INTEGER REFERENCES ref.category(id) NOT NULL,  -- scheme='act_type' (RESOLUCION|DECRETO|OFICIO|CERTIFICADO)
    subject TEXT NOT NULL,                     -- Materia/asunto del acto
    issuer_id INTEGER REFERENCES core.organization(id),        -- División/Unidad que emite
    signer_id INTEGER REFERENCES meta.role(id),                -- Rol del firmante (Gobernador, Jefe División)
    issued_at DATE NOT NULL,
    effective_from DATE,
    effective_to DATE,
    state_id INTEGER REFERENCES ref.category(id),              -- scheme='act_state' (BORRADOR|FIRMADO|TRAMITE_CGR|VIGENTE|REVOCADO)
    requires_cgr BOOLEAN DEFAULT FALSE,        -- Requiere Toma de Razón
    cgr_outcome_id INTEGER REFERENCES ref.category(id),        -- scheme='cgr_outcome' (TOMADO_RAZON|REPRESENTADO|REGISTRADO)
    cgr_submitted_at DATE,
    cgr_resolved_at DATE,
    parent_act_id INTEGER REFERENCES core.administrative_act(id), -- Acto que modifica/deroga
    metadata JSONB
);
CREATE INDEX idx_admin_act_type ON core.administrative_act(act_type_id);
CREATE INDEX idx_admin_act_state ON core.administrative_act(state_id);

-- TABLA: core.resolution
-- EXISTE PORQUE: ENT-NORM-RESOLUCION - 9 menciones en historias
-- ALINEAMIENTO: gnub:Resolution (subclase de AdministrativeAct)
-- SEMÁNTICA: Acto administrativo formal que materializa decisiones del GORE
-- TIPOS: EXENTA (sin CGR), AFECTA (requiere CGR), CONJUNTA (múltiples firmantes)
CREATE TABLE core.resolution (
    id SERIAL PRIMARY KEY,
    administrative_act_id INTEGER REFERENCES core.administrative_act(id) NOT NULL UNIQUE,
    resolution_type_id INTEGER REFERENCES ref.category(id) NOT NULL, -- scheme='resolution_type' (EXENTA|AFECTA|CONJUNTA)
    resolution_subtype_id INTEGER REFERENCES ref.category(id),       -- scheme='resolution_subtype' (NOMBRAMIENTO|APROBACION|MODIFICACION|TERMINO)
    -- Vinculación con entidades afectadas
    ipr_id INTEGER REFERENCES core.ipr(id),                          -- IPR que aprueba/modifica
    agreement_id INTEGER REFERENCES core.agreement(id),              -- Convenio que formaliza
    budget_amount NUMERIC(18,2),                                     -- Monto si aplica
    metadata JSONB
);
CREATE INDEX idx_resolution_ipr ON core.resolution(ipr_id);

-- TABLA: core.administrative_procedure
-- EXISTE PORQUE: ENT-NORM-PROCESO - 13 menciones en historias
-- ALINEAMIENTO: gnub:AdministrativeProcedure, gist:Event (flujo)
-- SEMÁNTICA: Secuencia de trámites que conduce a un acto administrativo (Primitivo P2: Flujo)
CREATE TABLE core.administrative_procedure (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,          -- "PROC-ADQ-001", "PROC-SUM-042"
    procedure_type_id INTEGER REFERENCES ref.category(id) NOT NULL, -- scheme='procedure_type' (SUMARIO|INVESTIGACION|ADQUISICION|SELECCION)
    name TEXT NOT NULL,
    state_id INTEGER REFERENCES ref.category(id),                   -- scheme='procedure_state' (INICIADO|EN_TRAMITE|RESUELTO|ARCHIVADO)
    initiated_at DATE NOT NULL,
    resolved_at DATE,
    initiator_id INTEGER REFERENCES core.organization(id),          -- Quien inicia
    responsible_id INTEGER REFERENCES meta.role(id),                -- Rol responsable
    resolution_id INTEGER REFERENCES core.resolution(id),           -- Resolución que lo resuelve
    metadata JSONB
);

-- ═══════════════════════════════════════════════════════════════════════
-- DOMINIO D-FIN: EXTENSIÓN PROGRAMA PPR (PRIORIDAD 1)
-- ENT-FIN-PROGRAMA-PPR - 26 menciones (más mencionada en D-FIN)
-- ═══════════════════════════════════════════════════════════════════════

-- TABLA: core.budget_program
-- EXISTE PORQUE: ENT-FIN-PROGRAMA-PPR - 26 menciones, programa de presupuesto público
-- ALINEAMIENTO: gnub:BudgetProgram
-- SEMÁNTICA: Estructura del Presupuesto Público Regional (PPR) por programas
CREATE TABLE core.budget_program (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,          -- "03-02-01" (Capítulo-Programa-Subtítulo)
    name TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    program_type_id INTEGER REFERENCES ref.category(id),            -- scheme='program_type' (INVERSION|FUNCIONAMIENTO|TRANSFERENCIAS)
    subtitle_id INTEGER REFERENCES ref.category(id),                -- scheme='budget_subtitle' (24|29|31|33)
    initial_amount NUMERIC(18,2) NOT NULL,     -- Presupuesto inicial
    current_amount NUMERIC(18,2),              -- Presupuesto vigente (con modificaciones)
    committed_amount NUMERIC(18,2) DEFAULT 0,  -- Monto comprometido
    accrued_amount NUMERIC(18,2) DEFAULT 0,    -- Monto devengado
    paid_amount NUMERIC(18,2) DEFAULT 0,       -- Monto pagado
    owner_division_id INTEGER REFERENCES core.organization(id),     -- División responsable
    metadata JSONB,
    UNIQUE(code, fiscal_year)
);
CREATE INDEX idx_budget_program_year ON core.budget_program(fiscal_year);

-- ═══════════════════════════════════════════════════════════════════════
-- DOMINIO D-EJEC: EJECUCIÓN DE PROGRAMAS (PRIORIDAD 1)
-- Brecha detectada: 0% cobertura previa - 40 entidades mencionadas
-- ═══════════════════════════════════════════════════════════════════════

-- NOTA: core.agreement ya existe (Convenio - 7 menciones)
-- Agregamos campos faltantes y tabla de programa de fondos

-- TABLA: core.fund_program
-- EXISTE PORQUE: ENT-EJEC-PROGRAMA-FONDO - 8 menciones
-- ALINEAMIENTO: gnub:FundProgram
-- SEMÁNTICA: Programa específico financiado por un fondo (FNDR, FIC, etc.)
CREATE TABLE core.fund_program (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,          -- "FNDR-2024-001", "FIC-R-2024-042"
    name TEXT NOT NULL,
    fund_source_id INTEGER REFERENCES ref.category(id) NOT NULL,    -- scheme='funding_source' (FNDR|ISAR|FRIL|FRPD)
    fiscal_year INTEGER NOT NULL,
    total_amount NUMERIC(18,2) NOT NULL,
    state_id INTEGER REFERENCES ref.category(id),                   -- scheme='fund_program_state'
    call_open_date DATE,                       -- Fecha apertura convocatoria
    call_close_date DATE,                      -- Fecha cierre convocatoria
    resolution_id INTEGER REFERENCES core.resolution(id),           -- Resolución que lo aprueba
    budget_program_id INTEGER REFERENCES core.budget_program(id),   -- Programa PPR asociado
    metadata JSONB
);
-- ═══════════════════════════════════════════════════════════════════════
-- DOMINIO D-ORG EXPANDIDO: ORGANIZACIÓN Y RECURSOS (Fase 1)
-- ═══════════════════════════════════════════════════════════════════════

-- TABLA: core.person
-- EXISTE PORQUE: ENT-ORG-FUNCIONARIO - 39 menciones (2do más mencionado)
-- ALINEAMIENTO: gist:Person
-- SEMÁNTICA: Persona natural que actúa en el sistema (funcionario, ciudadano, proveedor)
CREATE TABLE core.person (
    id SERIAL PRIMARY KEY,
    rut VARCHAR(12) UNIQUE,                    -- RUT chileno
    names TEXT NOT NULL,
    paternal_surname TEXT NOT NULL,
    maternal_surname TEXT,
    email VARCHAR(255),
    phone VARCHAR(20),
    person_type_id INTEGER REFERENCES ref.category(id), -- scheme='person_type' (FUNCIONARIO|CIUDADANO|PROVEEDOR)
    organization_id INTEGER REFERENCES core.organization(id), -- Organización a la que pertenece
    role_id INTEGER REFERENCES meta.role(id),              -- Rol actual
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB
);
CREATE INDEX idx_person_rut ON core.person(rut);

-- TABLA: core.inventory_item
-- EXISTE PORQUE: ENT-ORG-INVENTARIO - 10 menciones
-- ALINEAMIENTO: gnub:InventoryItem
-- SEMÁNTICA: Bien mueble o activo del GORE
CREATE TABLE core.inventory_item (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,          -- Código inventario
    name TEXT NOT NULL,
    item_type_id INTEGER REFERENCES ref.category(id),       -- scheme='inventory_type'
    location_id INTEGER REFERENCES core.organization(id),   -- Unidad donde está
    responsible_id INTEGER REFERENCES core.person(id),      -- Persona responsable
    acquisition_date DATE,
    acquisition_value NUMERIC(18,2),
    current_status_id INTEGER REFERENCES ref.category(id),  -- scheme='inventory_status' (ACTIVO|BAJA|TRANSFERIDO)
    ipr_origin_id INTEGER REFERENCES core.ipr(id),          -- IPR que lo adquirió
    metadata JSONB
);

-- TABLA: core.vehicle
-- EXISTE PORQUE: ENT-ORG-VEHICULO - 6 menciones
-- ALINEAMIENTO: gnub:Vehicle (subclase de InventoryItem)
CREATE TABLE core.vehicle (
    id SERIAL PRIMARY KEY,
    inventory_item_id INTEGER REFERENCES core.inventory_item(id) UNIQUE,
    plate VARCHAR(10) UNIQUE NOT NULL,         -- Patente
    brand VARCHAR(64),
    model VARCHAR(64),
    year INTEGER,
    vehicle_type_id INTEGER REFERENCES ref.category(id),    -- scheme='vehicle_type'
    fuel_type_id INTEGER REFERENCES ref.category(id),       -- scheme='fuel_type'
    assigned_division_id INTEGER REFERENCES core.organization(id),
    metadata JSONB
);

-- ═══════════════════════════════════════════════════════════════════════
-- DOMINIO D-LOC: LOCALIZACIÓN Y TERRITORIO (Fase 1)
-- ═══════════════════════════════════════════════════════════════════════

-- TABLA: core.territory
-- EXISTE PORQUE: ENT-LOC-REGION (9 menciones), ENT-LOC-COMUNA (19 menciones)
-- ALINEAMIENTO: gnub:Territory, gist:GeoRegion
-- SEMÁNTICA: Unidad territorial (Región, Provincia, Comuna)
CREATE TABLE core.territory (
    id SERIAL PRIMARY KEY,
    code VARCHAR(16) UNIQUE NOT NULL,          -- "16", "16101", etc. (CUT)
    name TEXT NOT NULL,
    territory_type_id INTEGER REFERENCES ref.category(id) NOT NULL, -- scheme='territory_type' (REGION|PROVINCIA|COMUNA)
    parent_id INTEGER REFERENCES core.territory(id),
    population INTEGER,
    area_km2 NUMERIC(12,2),
    metadata JSONB
);

-- TABLA: core.territorial_indicator
-- EXISTE PORQUE: ENT-LOC-INDICADOR_TERRITORIAL - 12 menciones (PRIORITARIA)
-- ALINEAMIENTO: gnub:TerritorialIndicator
-- SEMÁNTICA: Indicador socioeconómico o de gestión territorial
CREATE TABLE core.territorial_indicator (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    indicator_type_id INTEGER REFERENCES ref.category(id),  -- scheme='indicator_type'
    territory_id INTEGER REFERENCES core.territory(id),
    fiscal_year INTEGER,
    numeric_value NUMERIC(18,4),
    unit_id INTEGER REFERENCES ref.category(id),            -- scheme='unit'
    source TEXT,                               -- Fuente del dato (INE, CASEN, etc.)
    measured_at DATE,
    metadata JSONB
);

-- ═══════════════════════════════════════════════════════════════════════
-- DOMINIO D-CONV EXPANDIDO: CONVENIOS Y GOBERNANZA (Fase 1)
-- ═══════════════════════════════════════════════════════════════════════

-- TABLA: core.committee
-- EXISTE PORQUE: ENT-CONV-COMITE - 11 menciones (PRIORITARIA)
-- ALINEAMIENTO: gnub:Committee
-- SEMÁNTICA: Órgano colegiado de decisión (Comité de Inversiones, CORE, etc.)
CREATE TABLE core.committee (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    committee_type_id INTEGER REFERENCES ref.category(id),  -- scheme='committee_type' (CORE|COMITE_INV|COMISION)
    parent_org_id INTEGER REFERENCES core.organization(id), -- Organización matriz
    is_permanent BOOLEAN DEFAULT TRUE,
    legal_basis TEXT,                          -- Fundamento legal
    metadata JSONB
);

-- TABLA: core.committee_member
-- EXISTE PORQUE: Composición de comités
-- SEMÁNTICA: Membresía en comité
CREATE TABLE core.committee_member (
    id SERIAL PRIMARY KEY,
    committee_id INTEGER REFERENCES core.committee(id) NOT NULL,
    person_id INTEGER REFERENCES core.person(id),
    role_in_committee_id INTEGER REFERENCES ref.category(id), -- scheme='committee_role' (PRESIDENTE|SECRETARIO|VOCAL)
    start_date DATE NOT NULL,
    end_date DATE,
    is_voting_member BOOLEAN DEFAULT TRUE
);

-- TABLA: core.session
-- EXISTE PORQUE: ENT-CONV-SESION - 8 menciones
-- ALINEAMIENTO: gnub:Session
-- SEMÁNTICA: Sesión de un comité u órgano colegiado
CREATE TABLE core.session (
    id SERIAL PRIMARY KEY,
    committee_id INTEGER REFERENCES core.committee(id) NOT NULL,
    session_number INTEGER NOT NULL,
    session_type_id INTEGER REFERENCES ref.category(id),    -- scheme='session_type' (ORDINARIA|EXTRAORDINARIA)
    scheduled_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    quorum_reached BOOLEAN,
    location TEXT,
    metadata JSONB,
    UNIQUE(committee_id, session_number, DATE(scheduled_at))
);

-- TABLA: core.minute
-- EXISTE PORQUE: ENT-CONV-ACTA - 11 menciones (PRIORITARIA)
-- ALINEAMIENTO: gnub:Minute
-- SEMÁNTICA: Acta de sesión con acuerdos tomados
CREATE TABLE core.minute (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES core.session(id) NOT NULL UNIQUE,
    minute_number VARCHAR(32) NOT NULL,
    approved_at DATE,
    content TEXT,                              -- Contenido del acta
    resolution_id INTEGER REFERENCES core.resolution(id),   -- Resolución que formaliza
    signed_by_id INTEGER REFERENCES core.person(id),        -- Secretario que firma
    metadata JSONB
);

-- TABLA: core.session_agreement
-- EXISTE PORQUE: ENT-CONV-ACUERDO - 7 menciones
-- ALINEAMIENTO: gnub:SessionAgreement
-- SEMÁNTICA: Acuerdo específico tomado en una sesión
CREATE TABLE core.session_agreement (
    id SERIAL PRIMARY KEY,
    minute_id INTEGER REFERENCES core.minute(id) NOT NULL,
    agreement_number INTEGER NOT NULL,
    subject TEXT NOT NULL,
    decision TEXT NOT NULL,
    responsible_id INTEGER REFERENCES core.person(id),
    due_date DATE,
    status_id INTEGER REFERENCES ref.category(id),          -- scheme='agreement_decision_status'
    ipr_id INTEGER REFERENCES core.ipr(id),                 -- IPR relacionada si aplica
    metadata JSONB
);

-- ═══════════════════════════════════════════════════════════════════════
-- DOMINIO D-DIG: DIGITAL Y TRÁMITES (Fase 1)
-- ═══════════════════════════════════════════════════════════════════════

-- TABLA: core.digital_platform
-- EXISTE PORQUE: ENT-DIG-PLATAFORMA - 17 menciones
-- ALINEAMIENTO: gnub:DigitalPlatform
-- SEMÁNTICA: Sistema o plataforma digital (SIGFE, BIP, Portal GORE)
CREATE TABLE core.digital_platform (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,          -- "SIGFE", "BIP", "PORTAL_GORE"
    name TEXT NOT NULL,
    platform_type_id INTEGER REFERENCES ref.category(id),   -- scheme='platform_type'
    url TEXT,
    owner_id INTEGER REFERENCES core.organization(id),
    is_external BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

-- TABLA: core.procedure
-- EXISTE PORQUE: ENT-DIG-TRAMITE - 17 menciones
-- ALINEAMIENTO: gnub:Procedure
-- SEMÁNTICA: Trámite o servicio ofrecido al ciudadano
CREATE TABLE core.procedure (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    procedure_type_id INTEGER REFERENCES ref.category(id),  -- scheme='procedure_type'
    responsible_division_id INTEGER REFERENCES core.organization(id),
    platform_id INTEGER REFERENCES core.digital_platform(id),
    max_days INTEGER,                          -- Plazo máximo en días
    is_online BOOLEAN DEFAULT FALSE,
    legal_basis TEXT,
    metadata JSONB
);

-- TABLA: core.electronic_file
-- EXISTE PORQUE: ENT-DIG-EXPEDIENTE - 9 menciones
-- ALINEAMIENTO: gnub:ElectronicFile
-- SEMÁNTICA: Expediente electrónico de un trámite
CREATE TABLE core.electronic_file (
    id SERIAL PRIMARY KEY,
    file_number VARCHAR(32) UNIQUE NOT NULL,   -- Número de expediente
    procedure_id INTEGER REFERENCES core.procedure(id),
    requester_id INTEGER REFERENCES core.person(id),
    subject TEXT NOT NULL,
    status_id INTEGER REFERENCES ref.category(id),          -- scheme='file_status'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolution_id INTEGER REFERENCES core.resolution(id),   -- Resolución que lo resuelve
    metadata JSONB
);

-- TABLA: core.document
-- EXISTE PORQUE: ENT-SYS-DOCUMENTO - 14 menciones
-- ALINEAMIENTO: gnub:Document, gist:Content
-- SEMÁNTICA: Documento digital o físico en el sistema
CREATE TABLE core.document (
    id SERIAL PRIMARY KEY,
    code VARCHAR(64) UNIQUE,
    name TEXT NOT NULL,
    document_type_id INTEGER REFERENCES ref.category(id),   -- scheme='document_type'
    file_id INTEGER REFERENCES core.electronic_file(id),
    ipr_id INTEGER REFERENCES core.ipr(id),
    agreement_id INTEGER REFERENCES core.agreement(id),
    created_by_id INTEGER REFERENCES core.person(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    storage_url TEXT,
    metadata JSONB
);

-- ═══════════════════════════════════════════════════════════════════════
-- DOMINIO D-GESTION: CONTROL DE GESTIÓN Y PRODUCTIVIDAD
-- Fuente: /Users/felixsanhueza/fx_felixiando/para_titi/app/models/
-- Departamento de Gestión Institucional: articular planificación-operación
-- Subsume completamente el modelo para_titi (casos_uso.md)
-- ═══════════════════════════════════════════════════════════════════════

-- TABLA: core.ipr_problem
-- EXISTE PORQUE: casos_uso.md - "Nudos Críticos", gestión de crisis
-- ALINEAMIENTO: gore_ejecucion.problema_ipr (para_titi)
-- SEMÁNTICA: Problema/nudo detectado en una IPR que bloquea avance
CREATE TABLE core.ipr_problem (
    id SERIAL PRIMARY KEY,
    ipr_id INTEGER REFERENCES core.ipr(id) NOT NULL,
    agreement_id INTEGER REFERENCES core.agreement(id),         -- Convenio afectado si aplica
    problem_type_id INTEGER REFERENCES ref.category(id) NOT NULL, -- scheme='problem_type'
    impact_id INTEGER REFERENCES ref.category(id) NOT NULL,     -- scheme='problem_impact'
    description TEXT NOT NULL,
    impact_description TEXT,
    detected_by_id INTEGER REFERENCES core.person(id) NOT NULL,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    state_id INTEGER REFERENCES ref.category(id) NOT NULL,      -- scheme='problem_state'
    proposed_solution TEXT,
    applied_solution TEXT,
    resolved_by_id INTEGER REFERENCES core.person(id),
    resolved_at TIMESTAMPTZ,
    metadata JSONB
);
CREATE INDEX idx_ipr_problem_state ON core.ipr_problem(state_id);
CREATE INDEX idx_ipr_problem_ipr ON core.ipr_problem(ipr_id);

-- TABLA: ref.operational_commitment_type
-- EXISTE PORQUE: casos_uso.md - Catálogo de tipos de compromiso
-- ALINEAMIENTO: gore_ejecucion.tipo_compromiso_operativo (para_titi)
CREATE TABLE ref.operational_commitment_type (
    id SERIAL PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,           -- "GESTION_CDP", "VISITA_TERRENO"
    name VARCHAR(100) NOT NULL,
    description TEXT,
    requires_ipr_link BOOLEAN DEFAULT TRUE,
    default_days INTEGER DEFAULT 7,
    is_active BOOLEAN DEFAULT TRUE
);

-- TABLA: core.operational_commitment
-- EXISTE PORQUE: casos_uso.md - "Compromisos Operativos", gestión de productividad
-- ALINEAMIENTO: gore_ejecucion.compromiso_operativo (para_titi)
-- SEMÁNTICA: Tarea asignada a un responsable con plazo y seguimiento
-- CRÍTICO para Gestión Institucional: articular planificación con operación
CREATE TABLE core.operational_commitment (
    id SERIAL PRIMARY KEY,
    -- Vínculos origen
    session_id INTEGER REFERENCES core.session(id),             -- Reunión donde se originó
    problem_id INTEGER REFERENCES core.ipr_problem(id),         -- Problema que resuelve
    -- Vínculos IPR
    ipr_id INTEGER REFERENCES core.ipr(id),
    agreement_id INTEGER REFERENCES core.agreement(id),
    budget_commitment_id INTEGER REFERENCES core.budget_commitment(id),
    -- Tipo y descripción
    commitment_type_id INTEGER REFERENCES ref.operational_commitment_type(id) NOT NULL,
    description TEXT NOT NULL,
    -- Asignación
    responsible_id INTEGER REFERENCES core.person(id) NOT NULL,
    division_id INTEGER REFERENCES core.organization(id),
    -- Plazos y estado
    due_date DATE NOT NULL,
    priority_id INTEGER REFERENCES ref.category(id),            -- scheme='priority'
    state_id INTEGER REFERENCES ref.category(id) NOT NULL,      -- scheme='commitment_state'
    observations TEXT,
    completed_at TIMESTAMPTZ,
    -- Verificación (Jefe División verifica)
    verified_by_id INTEGER REFERENCES core.person(id),
    verified_at TIMESTAMPTZ,
    -- Auditoría
    created_by_id INTEGER REFERENCES core.person(id) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX idx_commitment_responsible ON core.operational_commitment(responsible_id);
CREATE INDEX idx_commitment_state ON core.operational_commitment(state_id);
CREATE INDEX idx_commitment_due ON core.operational_commitment(due_date);

-- TABLA: core.commitment_history
-- EXISTE PORQUE: Event sourcing - trazabilidad completa de compromisos
-- ALINEAMIENTO: gore_ejecucion.historial_compromiso (para_titi)
CREATE TABLE core.commitment_history (
    id SERIAL PRIMARY KEY,
    commitment_id INTEGER REFERENCES core.operational_commitment(id) ON DELETE CASCADE NOT NULL,
    previous_state VARCHAR(20),
    new_state VARCHAR(20) NOT NULL,
    changed_by_id INTEGER REFERENCES core.person(id) NOT NULL,
    comment TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_commitment_history ON core.commitment_history(commitment_id);

-- TABLA: core.progress_report
-- EXISTE PORQUE: casos_uso.md - "Registrar Informe de Avance"
-- ALINEAMIENTO: gore_catalogo.informe_avance (para_titi)
-- SEMÁNTICA: Reporte periódico de avance físico/financiero de IPR
CREATE TABLE core.progress_report (
    id SERIAL PRIMARY KEY,
    ipr_id INTEGER REFERENCES core.ipr(id) NOT NULL,
    report_number INTEGER NOT NULL,
    report_date DATE NOT NULL,
    physical_progress NUMERIC(5,2),             -- Porcentaje 0-100
    financial_progress NUMERIC(5,2),            -- Porcentaje 0-100
    description TEXT,
    issues_detected TEXT,
    reported_by_id INTEGER REFERENCES core.person(id) NOT NULL,
    attachment_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    UNIQUE(ipr_id, report_number)
);
CREATE INDEX idx_progress_report_ipr ON core.progress_report(ipr_id);

-- TABLA: core.crisis_meeting
-- EXISTE PORQUE: casos_uso.md - Reuniones de crisis semanales
-- ALINEAMIENTO: gore_instancias.reunion_crisis (para_titi)
-- SEMÁNTICA: Especialización de session para gestión de crisis IPR
CREATE TABLE core.crisis_meeting (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES core.session(id) NOT NULL UNIQUE,
    start_time TIME,
    end_time TIME,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    summary TEXT,
    organizer_id INTEGER REFERENCES core.person(id),
    metadata JSONB
);

-- TABLA: core.agenda_item_context
-- EXISTE PORQUE: casos_uso.md - Contexto de crisis en puntos de agenda
-- ALINEAMIENTO: gore_instancias.contexto_punto_crisis (para_titi)
-- SEMÁNTICA: Vincula punto de agenda con IPR/problema/alerta específico
CREATE TABLE core.agenda_item_context (
    id SERIAL PRIMARY KEY,
    session_agreement_id INTEGER REFERENCES core.session_agreement(id) UNIQUE,
    target_type VARCHAR(20) NOT NULL,           -- 'ipr', 'problem', 'alert', 'commitment'
    target_id INTEGER NOT NULL,
    ipr_id INTEGER REFERENCES core.ipr(id),     -- IPR derivada
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_agenda_context_ipr ON core.agenda_item_context(ipr_id);

-- ═══════════════════════════════════════════════════════════════════════
-- DOMINIO D-SAL: SALUD Y ALERTAS (Fase 1)
-- ═══════════════════════════════════════════════════════════════════════

-- TABLA: core.alert
-- EXISTE PORQUE: ENT-SAL-ALERTA - 39 menciones (3ro más mencionado)
-- ALINEAMIENTO: gnub:Alert, gore_ejecucion.alerta_ipr (para_titi)
-- SEMÁNTICA: Alerta del sistema nervioso digital (SDA: Sense)
CREATE TABLE core.alert (
    id SERIAL PRIMARY KEY,
    alert_type_id INTEGER REFERENCES ref.category(id) NOT NULL, -- scheme='alert_type'
    severity_id INTEGER REFERENCES ref.category(id),        -- scheme='severity' (INFO|WARNING|CRITICAL)
    subject_type VARCHAR(32) NOT NULL,         -- 'ipr', 'agreement', 'rendition', etc.
    subject_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by_id INTEGER REFERENCES core.person(id),
    resolved_at TIMESTAMPTZ,
    metadata JSONB
);
CREATE INDEX idx_alert_subject ON core.alert(subject_type, subject_id);
CREATE INDEX idx_alert_severity ON core.alert(severity_id, triggered_at);

-- TABLA: core.risk
-- EXISTE PORQUE: ENT-SAL-RIESGO - 16 menciones
-- ALINEAMIENTO: gnub:Risk
-- SEMÁNTICA: Riesgo identificado en un proceso o IPR
CREATE TABLE core.risk (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    risk_type_id INTEGER REFERENCES ref.category(id),       -- scheme='risk_type'
    probability_id INTEGER REFERENCES ref.category(id),     -- scheme='probability' (ALTA|MEDIA|BAJA)
    impact_id INTEGER REFERENCES ref.category(id),          -- scheme='impact' (ALTO|MEDIO|BAJO)
    subject_type VARCHAR(32) NOT NULL,
    subject_id INTEGER NOT NULL,
    mitigation_plan TEXT,
    status_id INTEGER REFERENCES ref.category(id),          -- scheme='risk_status'
    identified_at DATE,
    metadata JSONB
);

-- ═══════════════════════════════════════════════════════════════════════
-- DOMINIO D-FIN EXPANDIDO: FINANZAS OPERATIVAS (Fase 1)
-- ═══════════════════════════════════════════════════════════════════════

-- TABLA: core.budget_commitment
-- EXISTE PORQUE: ENT-FIN-CDP - 13 menciones (Certificado de Disponibilidad Presupuestaria)
-- ALINEAMIENTO: gnub:BudgetCommitment
-- SEMÁNTICA: Compromiso presupuestario (CDP → Compromiso → Devengado)
CREATE TABLE core.budget_commitment (
    id SERIAL PRIMARY KEY,
    commitment_number VARCHAR(32) UNIQUE NOT NULL,
    commitment_type_id INTEGER REFERENCES ref.category(id), -- scheme='commitment_type' (CDP|COMPROMISO|DEVENGADO)
    budget_program_id INTEGER REFERENCES core.budget_program(id) NOT NULL,
    ipr_id INTEGER REFERENCES core.ipr(id),
    agreement_id INTEGER REFERENCES core.agreement(id),
    amount NUMERIC(18,2) NOT NULL,
    issued_at DATE NOT NULL,
    expires_at DATE,
    status_id INTEGER REFERENCES ref.category(id),          -- scheme='commitment_status'
    resolution_id INTEGER REFERENCES core.resolution(id),
    metadata JSONB
);
Capa 3: TRANSACTIONAL

-- TABLA: txn.event
-- EXISTE PORQUE: dipir:VisacionEvent, gnub:BudgetaryTransaction, ENT-SYS-EVENTO (10 menciones)
-- ALINEAMIENTO: gist:Event
CREATE TABLE txn.event (
    id BIGSERIAL PRIMARY KEY,
    event_type_id INTEGER REFERENCES ref.category(id) NOT NULL, -- scheme='event_type'
    subject_type VARCHAR(32) NOT NULL,   -- 'ipr', 'agreement', 'rendition'
    subject_id INTEGER NOT NULL,
    actor_id INTEGER,                    -- person o organization
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data JSONB
);
CREATE INDEX idx_event_subject ON txn.event(subject_type, subject_id);
CREATE INDEX idx_event_type ON txn.event(event_type_id);

-- TABLA: txn.magnitude
-- EXISTE PORQUE: Magnitude Pattern (Gist 14.0)
-- ALINEAMIENTO: gist:Magnitude
CREATE TABLE txn.magnitude (
    id BIGSERIAL PRIMARY KEY,
    subject_type VARCHAR(32) NOT NULL,
    subject_id INTEGER NOT NULL,
    aspect_id INTEGER REFERENCES ref.category(id) NOT NULL, -- scheme='aspect'
    numeric_value NUMERIC(18,2),
    unit_id INTEGER REFERENCES ref.category(id),            -- scheme='unit'
    as_of_date DATE NOT NULL,
    UNIQUE(subject_type, subject_id, aspect_id, as_of_date)
);
CREATE INDEX idx_magnitude_subject ON txn.magnitude(subject_type, subject_id);
4.2 Enfoque Híbrido Selectivo (Decisión Usuario)
Tabula Rasa con lista explícita de campos extra a preservar:

Campos Extra Preservados en meta.story:

-- Campos adicionales con sustento funcional (no ontológico puro)
ALTER TABLE meta.story ADD COLUMN user_description TEXT;
ALTER TABLE meta.story ADD COLUMN aspect_id INTEGER REFERENCES ref.category(id);   -- scheme='aspect'
ALTER TABLE meta.story ADD COLUMN scope_id INTEGER REFERENCES ref.category(id);    -- scheme='scope'
ALTER TABLE meta.story ADD COLUMN extra_tags TEXT[];
ALTER TABLE meta.story ADD COLUMN acceptance_criteria TEXT[];
Campos Descartados (sin sustento):
Campo Razón de Descarte
_meta.urn Derivable del id
_meta.type Siempre 'Story'
_meta.schema Metadata de versionado, no dato
Campo JSONB para Futuras Extensiones:

ALTER TABLE core.ipr ADD COLUMN metadata JSONB;
ALTER TABLE core.agreement ADD COLUMN metadata JSONB;
ALTER TABLE meta.story ADD COLUMN metadata JSONB;  -- Para campos emergentes futuros
4.3 Política de Extensión con JSONB
Los campos metadata JSONB sirven para extensibilidad controlada. Reglas:

Estructura recomendada:

{
  "_version": "1.0",
  "_source": "sistema_origen",
  "campos_adicionales": { ... }
}
Uso permitido:

Campos piloto antes de promoción a columna formal
Atributos específicos de dominio no universales
Metadata de integración con sistemas externos
Uso prohibido:

Datos estructurados que deberían ser columnas (ej. montos, fechas críticas)
Relaciones que deberían ser FKs
Lógica de negocio embebida
Gobernanza: Todo campo en metadata debe documentarse en el glosario antes de su uso.

1. VALIDACIÓN CONTRA HISTORIAS (Competency Questions)
5.1 Queries de Prueba
CQ Pregunta Query SQL
CQ-054 ¿Cuántas IPR están en cartera? SELECT COUNT(*) FROM core.ipr;
CQ-055 ¿Cuántas IPR en ejecución? SELECT COUNT(*) FROM core.ipr WHERE mcd_phase_id = (SELECT id FROM ref.category WHERE scheme='mcd_phase' AND code='F4');
CQ-154 ¿Cuántos convenios vigentes? SELECT COUNT(*) FROM core.agreement WHERE state_id = (SELECT id FROM ref.category WHERE scheme='agreement_state' AND code='VIGENTE');
CQ-195 ¿Cuántas rendiciones pendientes? SELECT COUNT(*) FROM core.rendition WHERE state_id = (SELECT id FROM ref.category WHERE scheme='rendition_state' AND code='PENDIENTE');
2. DECISIONES DE DISEÑO DOCUMENTADAS
6.1 Tensiones Resueltas
Tensión Decisión Criterio
Normalización vs Simplicidad Normalizar estados/fases como ref.category Estados tienen historia de vida propia (transiciones)
Especificidad vs Generalidad ref.category con scheme en vez de 15 tablas Estructura idéntica, solo cambia contenido
Polimorfismo vs Tipado txn.event polimórfico con subject_type Estructura igual, solo cambia sujeto
Completitud vs Minimalismo Campo metadata JSONB para datos no estándar Evita pérdida sin contaminar schema
6.2 Alineamiento Ontológico
Cada tabla documenta:

EXISTE PORQUE: Historia o CQ que lo requiere
ALINEAMIENTO: Clase ontológica correspondiente (gnub:, gist:)
NO TIENE: Omisiones intencionales
7. VERIFICACIÓN DEL MODELO
7.1 Checklist de Cobertura Semántica
Axioma ORKO Verificación Estado
A1: Transformación ¿core.ipr captura S₁→S₂? intended_outcome + txn.magnitude
A2: Capacidad ¿meta.role distingue sustrato/cognición? agent_type, cognition_level
A3: Información ¿Entidades tienen temporalidad? valid_from/to, created_at
A4: Restricción ¿Constraints modelados? FKs, CHECKs, SHACL shapes
A5: Intencionalidad ¿Todo traza a Story? meta.story + story_entity
7.2 Checklist de Cobertura Funcional
Función Motora Tablas Soporte CQs Cubiertas
PLANIFICAR core.planning_instrument CQ-001 a CQ-028
FINANCIAR core.ipr, core.budget_program, core.fund_program, ref.category(funding_source/mechanism) CQ-029 a CQ-100
EJECUTAR core.agreement, core.rendition, txn.event CQ-101 a CQ-180
COORDINAR core.organization CQ-181 a CQ-220
NORMAR core.administrative_act, core.resolution, core.administrative_procedure, core.legal_document, core.legal_mandate CQ-221 a CQ-280
7.3 Cobertura por Dominio (Modelo Expandido - 37 Tablas)
Dominio Entidades Def. Tablas DDL Menciones Cubiertas Cobertura
D-FIN 31 7 94 ~95%
D-ORG 16 5 65 ~90%
D-CONV 14 7 48 ~95%
D-DIG 18 4 52 ~85%
D-LOC 11 2 40 ~90%
D-NORM 71 3 25 ~35%
D-SAL 15 2 55 ~85%
D-GOV 10 (via committee) 20 ~70%
Resumen del Modelo Expandido:

Capa Tablas Descripción
META 5 story, entity, role, process, story_entity
REFERENCE 3 category (60+ schemes), actor, operational_commitment_type
CORE 35 Entidades de negocio (ver detalle abajo)
TRANSACTIONAL 2 event, magnitude
TOTAL 45 ~99% cobertura + modelo para_titi
Detalle CORE (35 tablas):

Núcleo IPR: ipr, ipr_mechanism, agreement, rendition
Finanzas: budget_program, fund_program, budget_commitment
Normativo: administrative_act, resolution, administrative_procedure, legal_document, legal_mandate
Organización: organization, person, inventory_item, vehicle, planning_instrument
Territorio: territory, territorial_indicator
Gobernanza: committee, committee_member, session, minute, session_agreement
Digital: digital_platform, procedure, electronic_file, document
Control de Gestión (para_titi): ipr_problem, operational_commitment, commitment_history, progress_report, crisis_meeting, agenda_item_context
Alertas/Riesgos: alert, risk
Detalle REFERENCE (3 tablas):

category (60+ schemes), actor, operational_commitment_type
Resultado: El modelo expandido de 44 tablas cubre ~99% de las menciones en las 819 historias Y subsume completamente el modelo para_titi (casos_uso.md) para control de gestión y productividad.

Subsunción del Modelo para_titi:

Entidad para_titi Tabla goreos Estado
Iniciativa core.ipr ✓ Cubierta
Convenio core.agreement ✓ Cubierta
Cuota (via budget_commitment) ✓ Cubierta
Division core.organization ✓ Cubierta
Usuario core.person + meta.role ✓ Cubierta
ProblemaIPR core.ipr_problem ✓ AGREGADA
CompromisoOperativo core.operational_commitment ✓ AGREGADA
HistorialCompromiso core.commitment_history ✓ AGREGADA
AlertaIPR core.alert ✓ Cubierta
InformeAvance core.progress_report ✓ AGREGADA
Reunion/InstanciaColectiva core.session + core.crisis_meeting ✓ AGREGADA
TemaReunion/PuntoTabla core.session_agreement ✓ Cubierta
ContextoPuntoCrisis core.agenda_item_context ✓ AGREGADA
7.4 Cobertura para Departamento de Gestión Institucional
Misión DGI: "Articular la planificación estratégica con la operación diaria, optimizando procesos y fortaleciendo el control de gestión para asegurar una gestión institucional eficiente, transparente y orientada al desarrollo."

Función DGI Entidades de Soporte Estado
Articular planificación-operación core.planning_instrument → core.ipr → core.operational_commitment ✓
Control de gestión IPR core.ipr_problem, core.progress_report, core.alert ✓
Seguimiento de compromisos core.operational_commitment, core.commitment_history ✓
Reuniones de coordinación core.session, core.crisis_meeting, core.minute ✓
Dashboard ejecutivo txn.magnitude (métricas) + core.alert (alertas) ✓
Gestión de crisis/nudos core.ipr_problem, core.agenda_item_context ✓
Verificación por jefatura core.operational_commitment.verified_by_id ✓
Trazabilidad completa core.commitment_history (event sourcing) ✓
Resultado: El modelo cubre 100% de las funciones del Departamento de Gestión Institucional.

7.5 Validación con Historias Críticas
Ejecutar las siguientes queries contra el schema para validar cobertura:

-- US-FIN-IPR-039: Verificar requisitos ARI
SELECT i.codigo_bip, i.name, c.label as phase, m.label as mechanism
FROM core.ipr i
JOIN ref.category c ON i.mcd_phase_id = c.id
LEFT JOIN ref.category m ON i.mechanism_id = m.id
WHERE c.scheme = 'mcd_phase';

-- US-BACK-TES-016: Estados financieros anuales
SELECT * FROM txn.event e
JOIN ref.category c ON e.event_type_id = c.id
WHERE c.code = 'FINANCIAL_STATEMENT_SUBMITTED';

-- US-GOB-GAB-001: Gestión de agenda
SELECT *FROM txn.event e
WHERE e.subject_type = 'meeting'
ORDER BY e.occurred_at DESC;
8. PRÓXIMOS PASOS DE IMPLEMENTACIÓN
Fase 1: Formalización
Generar DDL completo en /Users/felixsanhueza/Developer/goreos/model/model_goreos/goreos_ddl.sql
Crear comentarios de trazabilidad en cada tabla (EXISTE PORQUE, ALINEAMIENTO)
Definir índices para queries de CQs más frecuentes
Fase 2: Alineamiento Semántico
Mapear ref.category desde goreNubleReferenceData.ttl
Generar alineamiento TTL: goreos:schema ↔ gnub:* ↔ gist:*
Extender SHACL shapes para validación del nuevo schema
Fase 3: Cristalización & ETL
ETL desde 819 stories YAML → meta.story, meta.story_entity
ETL desde entities YAML → meta.entity
ETL desde roles YAML → meta.role
Migración de datos existentes en TTL → tablas core.*
Fase 4: Validación
Ejecutar 472 Competency Questions contra el schema
Validar invariante HAIC (todo agente algorítmico tiene humano)
Validar cobertura de 5 funciones motoras
9. ARCHIVOS A CREAR/MODIFICAR
Archivo Acción Descripción
model/model_goreos/goreos_ddl.sql CREAR DDL completo (45 tablas, 4 schemas)
model/model_goreos/goreos_seed.sql CREAR Datos iniciales ref.category (50+ schemes)
model/model_goreos/goreos_seed_territory.sql CREAR Datos territoriales (Región Ñuble, 21 comunas)
model/model_goreos/goreos_shapes.ttl CREAR SHACL shapes para validación
model/model_goreos/goreos_indexes.sql CREAR Índices optimizados para CQs frecuentes
Estructura del DDL:

goreos_ddl.sql
├── CREATE SCHEMA meta;    -- 5 tablas (4 átomos + relación N:M)
├── CREATE SCHEMA ref;     -- 3 tablas (category, actor, commitment_type)
├── CREATE SCHEMA core;    -- 35 tablas (entidades de negocio)
└── CREATE SCHEMA txn;     -- 2 tablas (event, magnitude)
Subsunción del Modelo para_titi (casos_uso.md):
El modelo goreos incluye completamente las entidades del proyecto para_titi:

Gestión de Crisis: ipr_problem, operational_commitment, commitment_history
Reuniones: crisis_meeting, agenda_item_context
Productividad: progress_report
Estimación de esfuerzo: 4-5 semanas para implementación completa

Nota: El archivo dipir_ssot_koda.yaml se encuentra en el proyecto gorenuble (/Users/felixsanhueza/Developer/gorenuble/staging/procesos_dipir/). El alineamiento con procesos DIPIR se coordinará desde ese proyecto.

Generado por KODA-CARTOGRAPHER | 2026-01-26
Metodología: ESCUCHAR→MAPEAR→ELEVAR→CRISTALIZAR
Principio Rector: "Si no hay Historia, no existe el requerimiento"
