# GORE_OS Auditoría Institucional v3.0

> **Fecha**: 2026-03-08
> **Alcance**: Estado actual de GORE_OS vs 4 Fuentes de Verdad institucionales
> **Fuentes**: 818 historias de usuario, 472 Competency Questions (20 dominios), 198 OWL classes, Modelo Omega v2.6.0 (reglas de negocio operativas), Auditoría v2.0 (2026-03-03)
> **Metodología**: Triangulación CQ × Stories × Ontología × Omega con scoring GREEN/YELLOW/RED

---

## 1. Resumen Ejecutivo

GORE_OS ha avanzado de **~42% a ~55% de cobertura institucional** desde la auditoría v2.0 (2026-03-03). Los 11 ciclos completados (20-25, Remediacion, UX Remediation, UX Wave 2, HΩ-14, HΩ-15, Thresholds) transformaron la plataforma de un sistema con infraestructura base a un **engine de compliance operativo**: 19 gate functions, umbrales DB-parametricos, 7 glosas codificadas, SISREC multi-rol con SLA, y ciclo presupuestario completo.

### Metricas top-line (v2.0 → v3.0)

| Metrica | v2.0 (Mar 3) | v3.0 (Mar 8) | Δ |
|---------|:-------------:|:-------------:|:-:|
| DDL tables | 81 | 90 | +9 |
| API endpoints | 121 | 138 | +17 |
| Integration tests | 210 (23 modulos) | 334 (28 modulos) | +124 |
| ref.category schemes | 95+ | 82 (verificado) | -13 (conteo corregido) |
| Gate functions (ipr.py) | 7 | 19 | +12 |
| HΩ implementados | 3/15 | 13/15 | +10 |
| Reglas Omega cubiertas | 7/81 (~10%) | ~44/81 (~54%) | +37 |
| Glosa rules | 0/8 | 7/7 definidas | +7 |
| Track thresholds | hardcoded | DB-parametricos (JSONB) | -- |
| Frontend pages | ~30 | 35 | +5 |
| DDL migrations | ~12 | 22 archivos (15 tracked) | +10 |

### Top 5 Logros desde v2.0

1. **Compliance Engine** (Ciclos 20-21): `core.financial_threshold` (10 filas), glosa engine (7/7 reglas), clasificador presupuestario 4 niveles
2. **Track Enforcement** (Ciclos 22-24): 19 gate functions en `ipr.py` -- FRIL (fraccionamiento, 5/comuna, tender 90d), SNI (proporcionalidad, vigencia RS), C33 (conservation), SUBV8 (pagare, directorio, morosos, ranking), glosa 03/06
3. **DGI Cartera IPR** (Ciclo 25): Portfolio control con health signal coalgebra (VERDE/AMARILLO/ROJO), 3 endpoints, cuotas vencidas cross-portfolio, cockpit drill-down
4. **Budget Cycle Timeline** (HΩ-15): TP-05 con 17 milestones, 5 endpoints, tracking por IPR, frontend page
5. **UX Remediation** (3 waves): Sonner toast, ARIA/a11y, responsive mobile, Art. 18 error enriquecido, CDPs endpoint+UI, bulk cuotas convenio

### Top 5 Gaps Prioritarios

1. **HΩ-02 Parentesco 8%**: Inhabilitacion por consanguinidad 3/4 grado -- no iniciado
2. **HΩ-14 SISREC ciclo completo**: 4/4 SLA estados implementados, falta formalidad CGR 8-phase
3. **3 tablas parametricas pendientes**: TP-02 (fondos 8%), TP-04 (taxonomia FRIL), TP-06 (SISREC 8-phase SLA)
4. **0 integraciones externas**: ClaveUnica, PISEE, BIP, SIGFE, CGR -- TDE <10%
5. **Clasificador presupuestario**: 4/6 niveles implementados, faltan niveles 5-6

> *† Scores CQ por dominio son de la auditoria v2.0 y pueden subestimar mejoras recientes. Un re-audit de las 472 CQs es necesario para actualizar scores individuales.*

---

## 2. CQ Coverage por Dominio (472 CQs × 20 dominios)

> **Nota v3.0**: Los scores CQ por dominio que se presentan a continuacion son de la auditoria v2.0 (2026-03-03) y pueden subestimar mejoras recientes de los Ciclos 20-25. En particular, los dominios 03 (Financiamiento), 04 (Evaluacion), 08 (Rendicion), 12 (Selector Vias), 15 (FRIL), 18 (Concurso 8%) y 20 (Umbrales) han recibido implementaciones significativas que no se reflejan en estos scores. Un re-audit completo de las 472 CQs es necesario para actualizar los scores individuales.

### 2.1 Scorecard

Criterios de evaluacion:
- **GREEN**: CQ respondible via API + UI (dato existe en DB + endpoint expone + página muestra)
- **YELLOW**: Dato existe en schema/DB pero sin API/UI dedicada para responder la CQ
- **RED**: No implementable con schema actual

**Score** = `(GREEN + 0.5 × YELLOW) / total`

| # | Dominio | CQs | GREEN | YELLOW | RED | Score |
|:-:|---------|:---:|:-----:|:------:|:---:|:-----:|
| 01 | Estructura Organizacional | 28 | 10 | 6 | 12 | **46%** |
| 02 | IPR | 32 | 14 | 8 | 10 | **56%** |
| 03 | Financiamiento | 28 | 6 | 5 | 17 | **30%** |
| 04 | Evaluación | 30 | 5 | 2 | 23 | **20%**† |
| 05 | Aprobación | 22 | 8 | 4 | 10 | **45%** |
| 06 | Convenios | 20 | 10 | 4 | 6 | **60%** |
| 07 | Ejecución | 22 | 8 | 5 | 9 | **48%** |
| 08 | Rendición | 18 | 7 | 3 | 8 | **47%**† |
| 09 | Normativo | 25 | 3 | 2 | 20 | **16%** |
| 10 | TDE | 24 | 2 | 2 | 20 | **12%** |
| 11 | Gestión Operacional IPR | 26 | 10 | 5 | 11 | **48%** |
| 12 | Selector Vías Financiamiento | 22 | 6 | 4 | 12 | **36%** |
| 13 | Guía IDI SNI | 25 | 0 | 1 | 24 | **2%** |
| 14 | PPR Ejecución Directa | 21 | 0 | 1 | 20 | **2%** |
| 15 | FRIL | 25 | 0 | 1 | 24 | **2%**† |
| 16 | FRPD | 23 | 0 | 1 | 22 | **2%** |
| 17 | Transferencia PPR | 16 | 0 | 1 | 15 | **3%** |
| 18 | Concurso 8% | 27 | 0 | 1 | 26 | **1%**† |
| 19 | Circular 33 | 26 | 0 | 1 | 25 | **2%** |
| 20 | Umbrales Transversal | 12 | 1 | 1 | 10 | **12%**† |
| | **TOTAL** | **472** | **90** | **58** | **324** | **25.2%**† |

**Score ponderado** (GREEN=1, YELLOW=0.5): **(90 + 29) / 472 = 25.2%**†

> *† 5 dominios ajustados con contexto Modelo Omega v2.6.0: Dom 04 (23→20%), Dom 08 (53→47%), Dom 15 (4→2%), Dom 18 (2→1%), Dom 20 (17→12%). El Omega reveló sub-validaciones y reglas operativas que degradan YELLOWs a RED en estos dominios. Detalle en §4.5.*

### 2.2 Detalle por Dominio

#### Dom 01: Estructura Organizacional (28 CQs → 46%)

**GREEN (10)**: CQ-001 a CQ-003 (¿Qué es GORE/División/Departamento? — `core.organization` + org_type + admin UI), CQ-009 (divisiones GORE — `GET /api/catalogs/divisions`), CQ-013 (jerarquía Div→Depto — `parent_id` endofunctor), CQ-021 (cuántas divisiones — catalog count), CQ-024/025 (comunas/provincias — `ref.territory`), CQ-014 (unidades del Gobernador — org hierarchy), CQ-028 (unidades formuladoras — org search API)

**YELLOW (6)**: CQ-006 (CORE — tablas existen pero sin UI de composición), CQ-007 (CDR — `core.committee` existe, crisis_meetings lo usa), CQ-010 (deptos DIPIR — data en org hierarchy pero sin vista dedicada), CQ-011/012 (CDR presidencia/composición — data parcial), CQ-022 (cuántos deptos DIPIR — requiere query específico)

**RED (12)**: CQ-004/005 (DIPIR/DAE como entidades con funciones detalladas), CQ-008 (Unidad Formuladora como concepto formal), CQ-015/016 (relación CORE↔aprobación formal, unidad evaluación técnica), CQ-017..020 (temporales: creación GORE, mandato, periodicidad CORE), CQ-023 (consejeros regionales — sin tabla persona↔CORE), CQ-026/027 (funcionarios count, miembros CDR count)

#### Dom 02: IPR (32 CQs → 56%)

**GREEN (14)**: CQ-029 (¿Qué es IPR? — `core.ipr` + 8 tipos), CQ-035 (código BIP — campo `codigo_bip`), CQ-038 (tipos IPR — `ipr_type` scheme 8 codes), CQ-039 (IPR↔mecanismo — `mechanism_id` FK), CQ-040/042 (formulador/ejecutor — `ipr_party` con roles), CQ-045 (división patrocinante — `sponsor_division_id`), CQ-048 (BIP↔ciclo vida — `mcd_phase_id`), CQ-049 (etapas ciclo — `mcd_phase` scheme F0-F5), CQ-054 (IPR en cartera — `GET /api/ipr` paginated), CQ-055 (IPR en ejecución — filtrable por fase), CQ-058 (IDI vs PPR — `ipr_type` classification), CQ-059 (IPR por comuna — `ipr_territory`), CQ-060 (IPR por sector)

**YELLOW (8)**: CQ-030/031 (IDI/PPR como sub-entidades formales), CQ-032/033 (Estudio Básico/Proyecto como tipos — existen como `ipr_type` codes pero sin UI diferenciada), CQ-034 (Ficha IDI), CQ-036/037 (Perfil/Diseño programa — fases sin sub-estados), CQ-046/047 (IDI↔SNI, PPR↔BIPS — sin integración externa)

**RED (10)**: CQ-041 (quién evalúa — sin routing evaluador↔IPR automatizado por track), CQ-043/044 (IPR↔ERD, IPR↔PLADECO — sin instrumentos planificación), CQ-050..053 (secuencias fases IDI/PPR detalladas, asignación BIP temporal, evaluación ex post), CQ-056/057 (aprobadas año vigente, monto total inversión — sin aggregates temporales dedicados)

#### Dom 03: Financiamiento (28 CQs → 30%)

**GREEN (6)**: CQ-061 (FNDR — concepto general cubierto por `budget_program`), CQ-082 (presupuesto total — `GET /api/presupuesto/resumen`), CQ-086 (% ejecución — dashboard chart), CQ-087 (mecanismos count — `financing_track` table, 7 tracks), CQ-064/065 (Subtítulo 24/31 — `budget_subtitle` scheme)

**YELLOW (5)**: CQ-062/063 (FRIL/FRPD como conceptos — `mechanism` scheme existe pero sin UI dedicada), CQ-066 (Subtítulo 33), CQ-083/084 (montos FRIL/FRPD — calculable desde `budget_program` con filtros)

**RED (17)**: CQ-067..070 (Glosas 06/07/12/13 como reglas — 0/8 codificadas), CQ-071 (tipo IPR↔mecanismo aplicable — sin engine automático), CQ-072..081 (relaciones normativas, calendarios, acceso fondos — sin reglas codificadas), CQ-085/088 (monto 8%, count glosas — sin datos específicos por mecanismo)

#### Dom 04: Evaluación (30 CQs → 23%)

**GREEN (5)**: CQ-107 (track evaluación por tipo — `GET /api/ipr/{id}/track-info`), CQ-113 (cuántos tracks — `financing_track` table 7 registros), CQ-089 (SNI concepto — cubierto por mechanism scheme), CQ-116 (estados RATE — `evaluator_type` scheme), CQ-104 (RATE↔estado IPR — evaluation_assignment table)

**YELLOW (4)**: CQ-090 (BIP banco — código BIP existe en IPR), CQ-091..093 (RATE/RS/RF como conceptos — `evaluator_type` scheme tiene códigos pero sin workflow completo), CQ-098 (Admisibilidad — concepto en `mcd_phase` F1)

**RED (21)**: CQ-094..097 (FI/OT/AD/IN significados detallados), CQ-099/100 (evaluación Pertinencia/Técnico-Económica — sin sub-fases), CQ-101..103 (organismos evaluadores — sin integración MDSF/DIPRES/SES), CQ-105/106 (metodologías, proporcionalidad), CQ-108..112 (plazos evaluación — 0 SLAs evaluación codificados), CQ-114/115 (niveles proporcionalidad, metodologías sectoriales), CQ-117/118 (IPR RS año, tasa aprobación — sin métricas evaluación)

#### Dom 05: Aprobación (22 CQs → 45%)

**GREEN (8)**: CQ-119 (priorización IPR — concepto MCD F3), CQ-120 (Acuerdo CORE — `core.session_vote` + `session_agreement`), CQ-121 (Resolución Exenta — `core.resolution` CRUD), CQ-123 (umbral 7.000 UTM — gate F3→F4 implementado), CQ-125 (CORE aprueba >7.000 UTM — endpoint gate), CQ-128 (CORE→Resolución — link bidireccional), CQ-139 (quórum CORE — SIMPLE=9/16, CALIFICADA=11/16), CQ-140 (sesiones CORE año — listable)

**YELLOW (4)**: CQ-122 (CDP — `budget_commitment` existe pero sin link formal aprobación), CQ-126 (Gobernador aprueba ≤7.000 — lógica implícita), CQ-127 (unidad emite CDP — DAF inferable), CQ-134 (IPR aprobadas CORE — contable desde session_vote)

**RED (10)**: CQ-124 (Toma de Razón CGR — sin integración CGR), CQ-129 (IPR requieren TR — sin umbral 2.500 UTM codificado), CQ-130 (criterios priorización CDR — sin scoring engine), CQ-131..133 (temporales: cuándo sesiona, plazo CGR, plazo CORE→Resolución), CQ-135..138 (aggregates: monto total CORE, delegaciones Gobernador, resoluciones emitidas, IPR con TR)

#### Dom 06: Convenios (20 CQs → 60%)

**GREEN (10)**: CQ-141/142 (Transferencia/Mandato — `agreement_type` 6 tipos), CQ-143/144 (Subtítulo 24/33 — schemes), CQ-146 (receptoras — `ipr_party` MANDATARIO), CQ-148 (división gestora — agreement data), CQ-154 (convenios vigentes — `GET /api/convenios`), CQ-155 (monto transferido — `agreement_installment` paid tracking), CQ-156 (entidades con convenio — contable), CQ-157 (convenios por tipo — filtrable)

**YELLOW (4)**: CQ-145 (garantía fiel cumplimiento — concepto sin campo dedicado), CQ-147 (tipo convenio↔tipo entidad — inferable), CQ-149 (convenio↔Resolución — sin FK directa), CQ-159 (monto promedio — calculable)

**RED (6)**: CQ-150 (condiciones garantía — sin reglas codificadas), CQ-151..153 (plazos: firma, primera transferencia, vigencia típica), CQ-158 (convenios con garantía — sin campo), CQ-160 (umbral 1.000 UTM garantías — no codificado)

#### Dom 07: Ejecución (22 CQs → 48%)

**GREEN (8)**: CQ-161 (seguimiento IPR — `operational_commitment` + `ipr_problem`), CQ-162 (informe avance — `progress_report` CRUD), CQ-163/164 (avance físico/financiero — progress_report fields), CQ-167 (unidad seguimiento — inferable por assignee), CQ-176 (IPR en ejecución — filtrable por `mcd_phase` F4), CQ-178 (IPR con retrasos — `ipr_milestone` deviation_days), CQ-181 (IPR terminadas — filtrable F5)

**YELLOW (5)**: CQ-166 (modificación proyecto — concepto parcial via `txn.event` MODIFICACION), CQ-168 (ejecutor↔informes — relación inferable), CQ-171 (acciones incumplimiento hitos — alerts existen), CQ-177 (% avance promedio — calculable), CQ-182 (tasa cumplimiento plazos — calculable desde milestones)

**RED (9)**: CQ-165 (ITO Inspector Técnico — sin rol formal), CQ-169 (modificaciones que requieren CORE — sin regla), CQ-170 (rol ITO — sin entity), CQ-172..175 (periodicidad informes, plazos máx FRIL/FRPD/8% — sin SLAs ejecución), CQ-179/180 (modificaciones aprobadas, ITO asignados — sin datos)

#### Dom 08: Rendición (18 CQs → 53%)

**GREEN (8)**: CQ-183 (SISREC — implementado 8-state machine), CQ-184 (rendición de cuentas — `core.rendition` CRUD), CQ-188 (entidades que rinden — rendition↔agreement), CQ-189 (unidad GORE revisa — RTF/UCR roles), CQ-191 (acciones rendiciones pendientes — Art. 18 bloqueo), CQ-195 (rendiciones pendientes — `GET /api/dgi/data/rendiciones/vencidas`), CQ-196 (monto pendiente — `amount` field), CQ-198 (aprobadas año — filtrable por estado APROBADA)

**YELLOW (3)**: CQ-185 (Res N°30 CGR — concepto referenciado pero sin entity), CQ-190 (rendición↔cierre convenio — relación inferable), CQ-197 (entidades con pendientes — calculable)

**RED (7)**: CQ-186 (reparo rendición — sin sub-estado formal de reparos), CQ-187 (cierre administrativo IPR — sin workflow cierre), CQ-192..194 (plazos: rendir post-término, subsanar reparos, periodicidad parciales — solo SLA RTF 7d y UCR 2d), CQ-199/200 (reparos emitidos, tasa aprobación — sin métricas dedicadas)

#### Dom 09: Normativo (25 CQs → 16%)

**GREEN (3)**: CQ-207 (Res N°30 CGR — referenciada en Art. 18 check), CQ-220 (leyes principales — concepto cubierto), CQ-221 (resoluciones CGR transferencias — `cgr_outcome` scheme)

**YELLOW (2)**: CQ-201 (LOC GORE — concepto general), CQ-206 (NIP — referenciadas en evaluación)

**RED (20)**: CQ-202..205 (leyes específicas como entities), CQ-208..219 (relaciones normativas, normas por domain, temporales), CQ-222..225 (aggregates normativos). Este dominio es esencialmente una **base de conocimiento legal** — GORE_OS no es un sistema de gestión normativa.

#### Dom 10: TDE (24 CQs → 12%)

**GREEN (2)**: CQ-226 (TDE concepto — cubierto por el sistema mismo), CQ-243 (trámites digitalizados — GORE_OS es el sistema digital)

**YELLOW (2)**: CQ-228 (documento electrónico — `core.document` 12,800 registros), CQ-233 (expediente electrónico — agrupable por IPR)

**RED (20)**: CQ-227/229..232 (Ley TDE, FEA, GESDOC, interoperabilidad, ClaveÚnica — sin integración), CQ-234..249 (relaciones TDE, plataformas, temporales, métricas digitalización). Este dominio requiere **integraciones con plataformas externas** del Estado chileno.

#### Dom 11: Gestión Operacional IPR (26 CQs → 48%)

**GREEN (10)**: CQ-250/251 (IPR/IDI operacional — cubierto), CQ-255 (CDR — `core.committee`), CQ-256 (CDP — `budget_commitment`), CQ-257 (SISREC — implementado), CQ-260 (CDR presidencia — committee data), CQ-262 (unidad CDP — DAF), CQ-266 (CORE↔IPR >7.000 — gate), CQ-273 (fases proceso — MCD 6 fases), CQ-274 (tracks evaluación — 7 en `financing_track`)

**YELLOW (5)**: CQ-252..254 (estados PRE-ADMISIBLE, admisibilidad, financiamiento — conceptos parciales en scheme), CQ-258 (RATE valores — `evaluator_type` scheme), CQ-275 (etapas Fase 1 — parcial)

**RED (11)**: CQ-259 (estado NV — sin codificar), CQ-261 (DIPIR↔evaluación técnica formal), CQ-263..265 (organismos Track A, Track B, divisiones CDR — sin routing detallado), CQ-267..272 (RS emisión, plazos evaluación — sin SLAs)

#### Dom 12: Selector Vías Financiamiento (22 CQs → 36%)

**GREEN (6)**: CQ-276..278 (FNDR/FRPD/SNI según selector — `financing_track` table), CQ-279 (diferencia subtítulos — scheme), CQ-295 (mecanismos count — 7), CQ-286 (tipo IPR↔vía — track-info endpoint)

**YELLOW (4)**: CQ-280/281 (RATE AD/RF — codes existen), CQ-282..285 (Glosas 06/07/12/13 — conceptos en scheme pero sin reglas)

**RED (12)**: CQ-287..291 (routing condicional por executor/monto — sin engine), CQ-292..294 (vigencia RS, plazos FRIL/FRPD), CQ-296/297 (categorías FRPD, fondos 8%)

#### Dominios 13-19: Tracks Especializados (163 CQs → ~2%)

Estos 7 dominios representan **guías operativas detalladas** para tracks de financiamiento específicos. GORE_OS tiene la infraestructura base (`financing_track`, `mechanism` scheme, evaluaciones) pero no implementa la lógica especializada de cada track.

| Dom | Nombre | CQs | GREEN | YELLOW | Score |
|:---:|--------|:---:|:-----:|:------:|:-----:|
| 13 | Guía IDI SNI | 25 | 0 | 1 | 2% |
| 14 | PPR Ejecución Directa | 21 | 0 | 1 | 2% |
| 15 | FRIL | 25 | 0 | 2 | 4% |
| 16 | FRPD | 23 | 0 | 1 | 2% |
| 17 | Transferencia PPR | 16 | 0 | 1 | 3% |
| 18 | Concurso 8% | 27 | 0 | 1 | 2% |
| 19 | Circular 33 | 26 | 0 | 1 | 2% |

Las CQs YELLOW en cada dominio corresponden a conceptos genéricos que están parcialmente cubiertos por el modelo base (ej: CQ-344 "¿Qué es el FRIL?" → `mechanism` code FRIL existe). Las CQs RED son reglas de negocio, plazos, límites y workflows específicos de cada mecanismo.

**Implicación**: Implementar estos 7 dominios requeriría un **engine de reglas parametrizable** por track, no 7 implementaciones separadas.

#### Dom 20: Umbrales Transversal (12 CQs → 17%)

**GREEN (1)**: CQ-462 (umbral 7.000 UTM CORE — gate F3→F4 implementado)

**YELLOW (2)**: CQ-461 (5.000 UTM exención RS — concepto en `financing_track` pero sin enforcement), CQ-464 (monto↔Toma Razón CGR — relación conocida pero sin codificar)

**RED (9)**: CQ-463 (1.000 UTM garantías), CQ-465/466 (5.000↔FRIL, Glosa 03 prohibiciones), CQ-467..472 (topes porcentuales: 5% admin, 5% honorarios, 10% ANF, 20% equipamiento, 30% remuneraciones, fecha UTM)

---

## 3. Story Coverage por Dominio (818 stories × 16 dominios)

### 3.1 Scorecard

Metodología de scoring:
- Mapeo `entities_mentioned` → tablas DDL existentes
- Mapeo `process_ref` → endpoints API implementados
- Score = `(entities_con_tabla / total_entities) × 0.6 + (proceso_con_endpoint ? 0.4 : 0)`

| Dominio | Stories | P0 | P1 | P2 | P3 | Coverage Est. | Δ v1.0 |
|---------|:-------:|:--:|:--:|:--:|:--:|:------------:|:------:|
| D-GESTION | 23 | 8 | 10 | 5 | 0 | **78%** | +0% |
| D-EJEC | 113 | 35 | 45 | 28 | 5 | **35%** | +8% |
| D-GOB | 62 | 18 | 25 | 15 | 4 | **22%** | +14% |
| D-FIN | 97 | 30 | 35 | 25 | 7 | **20%** | +5% |
| D-OPS | 47 | 12 | 18 | 14 | 3 | **12%** | +6% |
| D-TDE | 108 | 32 | 40 | 28 | 8 | **9%** | +2% |
| D-NORM | 75 | 20 | 30 | 20 | 5 | **5%** | +5% |
| D-ORG | 4 | 2 | 2 | 0 | 0 | **25%** | +25% |
| D-BACK | 105 | 28 | 40 | 30 | 7 | **0%** | — |
| D-TERR | 48 | 12 | 18 | 14 | 4 | **0%** | — |
| D-DEV | 37 | 8 | 15 | 10 | 4 | **0%** | — |
| D-PLAN | 33 | 10 | 12 | 8 | 3 | **0%** | — |
| D-SOC | 23 | 5 | 10 | 6 | 2 | **0%** | — |
| D-SEG | 18 | 4 | 8 | 5 | 1 | **0%** | — |
| D-EVOL | 14 | 3 | 6 | 4 | 1 | **0%** | — |
| D-FENIX | 11 | 2 | 5 | 3 | 1 | **0%** | — |
| **TOTAL** | **818** | **229** | **319** | **215** | **55** | **~16%** | +6% |

### 3.2 Detalle de progreso por dominio

#### D-EJEC: Ejecución IPR (113 → 35%, +8%)

**Nuevas coberturas desde v1.0**:
- Poly-Switch routing F2 (Track A-E2, 7 mecanismos) → ~15 stories
- Evaluaciones CRUD + TrackCard UI → ~8 stories
- IPR lifecycle gate F3→F4 con CORE approval → ~5 stories
- Actos administrativos history + timeline → ~3 stories

**Gaps restantes**: Admisibilidad sub-estados F1, evaluación ex post F5, dictámenes como workflow (RS vigencia 3 años, FI/OT subsanación), priorización con scoring engine.

#### D-GOB: Gobernanza (62 → 22%, +14%)

**Nuevas coberturas desde v1.0**:
- Sesiones CORE ordinarias/extraordinarias CRUD → ~5 stories
- Votación IPR con quórum (SIMPLE/CALIFICADA) → ~4 stories
- Gate F3→F4 (>7.000 UTM requiere CORE) → ~3 stories
- Actos administrativos 7-step state machine → ~2 stories

**Gaps restantes**: Gobernador como actor principal (firma FEA, preside, delega), CDR como órgano formal, COSOC participación ciudadana, fiscalización, descentralización.

#### D-FIN: Finanzas (97 → 20%, +5%)

**Nuevas coberturas desde v1.0**:
- SISREC multi-role workflow (8 estados) → ~4 stories
- Art. 18 CGR bloqueo transferencias → ~2 stories
- Financing tracks como tabla administrable → ~2 stories

**Gaps restantes**: Clasificador 6 niveles, 8 glosas, 11 umbrales, tesorería, devengo, conciliación SIGFE.

#### D-NORM: Normativo (75 → 5%, +5%)

**Nuevas coberturas desde v1.0**:
- Actos administrativos CRUD + 7-step state machine → ~3 stories
- Resoluciones con link IPR + CGR tracking → ~2 stories

**Gaps restantes**: Este dominio es esencialmente un **sistema de gestión documental legal** — plantillas, precedentes, consulta normativa. GORE_OS cubre los actos administrativos como instrumentos operativos pero no como base de conocimiento legal.

---

## 4. Ontology Class Coverage (198 OWL classes)

Mapeo de las 198 classes `gnub:*` contra implementación GORE_OS.

### 4.1 Scorecard por Categoría Funcional

| Categoría | OWL Classes | Con DDL Table | Con API | Con UI | Score |
|-----------|:-----------:|:------------:|:-------:|:------:|:-----:|
| Budget & Finance | 23 | 8 | 6 | 5 | **35%** |
| IPR & Investment | 18 | 12 | 10 | 9 | **67%** |
| Admin & Governance | 11 | 8 | 7 | 6 | **64%** |
| Accountability & Monitoring | 16 | 10 | 8 | 7 | **52%** |
| Organization | 6 | 5 | 3 | 2 | **56%** |
| Territory | 3 | 2 | 1 | 1 | **44%** |
| System Infrastructure | 5 | 2 | 1 | 0 | **20%** |
| GORE Functions | 4 | 0 | 0 | 0 | **0%** |
| gist:Category subclasses | 66 | 1* | 1* | 0 | **2%** |
| Properties/Aspects | 40+ | — | — | — | — |
| Other domain classes | 6 | 1 | 0 | 0 | **6%** |
| **TOTAL (excluyendo Category/Props)** | **92** | **48** | **36** | **30** | **~43%** |

*\* Las 66 subclasses de `gist:Category` estan implementadas como registros en `ref.category` (82 schemes verificados), no como tablas individuales.*

### 4.2 Mapeo Detallado — Classes con Implementación

| OWL Class | DDL Table | API Endpoint | UI Page |
|-----------|-----------|-------------|---------|
| `gnub:IPR` | `core.ipr` | `/api/ipr` (20 endpoints) | `/ipr` list+detail |
| `gnub:IPRProject` | `core.ipr` (type filter) | filtro `ipr_type` | Filtro en UI |
| `gnub:IPRPhase` | `ref.category` (mcd_phase) | `/api/ipr/{id}` | Stepper UI |
| `gnub:IPRState` | `ref.category` (mcd_phase) | `/api/ipr/{id}/transiciones` | Botones transición |
| `gnub:BudgetProgram` | `core.budget_program` | `/api/presupuesto` | `/presupuesto` |
| `gnub:BudgetaryCommitment` | `core.budget_commitment` | `/api/presupuesto/cdps-por-ipr` | Tab CDPs |
| `gnub:FundingSource` | `ref.category` (funding_source) | `/api/catalogs/categories` | Select en forms |
| `gnub:AdministrativeAct` | `core.administrative_act` | `/api/actos` | `/actos` |
| `gnub:Resolution` | `core.resolution` | `/api/actos` (auto-creates) | Tab Resoluciones |
| `gnub:GOREAgreement` | `core.agreement` | `/api/convenios` | `/convenios` |
| `gnub:AgreementState` | `ref.category` (agreement_state) | `/api/convenios/{id}/transiciones` | Badge estado |
| `gnub:Rendition` | `core.rendition` | `/api/dgi/data/rendiciones` | DGI explorer |
| `gnub:RenditionState` | `ref.category` (rendition_state) | SISREC workflow | StatusBadge |
| `gnub:Alert` | `core.alert` | `/api/alertas` | `/alertas` |
| `gnub:Indicator` | `core.dgi_indicator` | `/api/dgi/data/indicators` | DGI cockpit |
| `gnub:Division` | `core.organization` (DIVISION) | `/api/admin/divisiones` | Admin UI |
| `gnub:Department` | `core.organization` (DEPTO) | Org hierarchy | — |
| `gnub:Unit` | `core.organization` (UNIDAD) | Org hierarchy | — |
| `gnub:EvaluationTrack` | `core.financing_track` | `/api/ipr/{id}/track-info` | TrackCard |
| `gnub:FinancingMechanism` | `ref.category` (mechanism) | `/api/catalogs/categories` | IPR detail |
| `gnub:EvaluationResult` | `core.evaluation_assignment` | `/api/ipr/{id}/evaluaciones` | Tab Evaluación |
| `gnub:ExecutionReport` | `core.progress_report` | `/api/ipr/{id}/avances` | Tab Avances |
| `gnub:Province` | `ref.territory` | `/api/catalogs/territories` | Territory forms |
| `gnub:Commune` | `ref.territory` | `/api/catalogs/territories` | Territory forms |

### 4.3 Classes sin Implementación (gaps prioritarios)

| OWL Class | Impacto | Prioridad |
|-----------|---------|:---------:|
| `gnub:BudgetPartida` | 6-level classifier missing | Alta |
| `gnub:BudgetChapter` | 6-level classifier missing | Alta |
| `gnub:BudgetItem` | 6-level classifier missing | Alta |
| `gnub:BudgetAllocation` | 6-level classifier missing | Alta |
| `gnub:BudgetModification` | Modificaciones presupuestarias activas | Alta |
| `gnub:PreCommitmentEvent` | Ciclo presupuestario completo | Media |
| `gnub:AccrualEvent` | Devengo | Media |
| `gnub:PaymentEvent` | Pagos | Media |
| `gnub:LegalMandate` | Base normativa | Baja |
| `gnub:LegalDocument` | Gestión documental legal | Baja |
| `gnub:GOREFunction` | Funciones estatutarias | Baja |
| `gnub:PlanningInstrument` | ERD, ARI, PROPIR | Media |
| `gnub:SystemLog` | Audit trail completo | Media |
| `gnub:AuditLog` | Auditoría interna | Media |
| `gnub:Dataset` | Datos abiertos | Baja |

---

## 4.5 Omega Model Coverage (Reglas de Negocio Operativas)

El Modelo Omega v2.6.0 (`omega_gore_nuble_mermaid.md`, 111KB) es la fuente de verdad operativa del GORE de Ñuble. Contiene reglas de negocio exactas, umbrales con valores, SLAs, procesos paso a paso, y tablas paramétricas que las CQs y Stories no detallan. Esta sección cruza el Omega contra la implementación GORE_OS para identificar gaps operativos de alta granularidad.

### 4.5.1 Resumen de Cobertura Omega

| Categoria Omega | Reglas Totales | Implementadas | Parciales | Sin Implementar | Cobertura |
|-----------------|:--------------:|:------------:|:---------:|:---------------:|:---------:|
| Umbrales financieros | 18 | 10 | 0 | 8 | **56%** |
| Reglas de Glosa | 7 | 7 | 0 | 0 | **100%** |
| Validaciones track-especificas | 40+ | 19 | 3 | 18+ | **48%** |
| Tablas parametricas | 6 | 2 | 2 | 2 | **50%** |
| SLAs y plazos operativos | 12+ | 6 | 1 | 5+ | **50%** |
| **TOTAL** | **81+** | **~44** | **6** | **~31** | **~54%** |

**Implementadas (44)**: 10 umbrales en `core.financial_threshold`, 7 glosas en `check_glosa_rules()`, 19 gate functions en `ipr.py` (FRIL x3, SNI x2, C33, SUBV8 x4, glosa x2, evaluation x1, CORE approval, Art. 18, mechanism-aware F2→F3, track amount gates, budget cycle), SLA RTF 7d + VISADA_RTF 1d + UCR 2d + OBSERVADA 15d, `financing_track` table con `thresholds` JSONB, `budget_cycle_milestone` + `budget_cycle_tracking` (TP-05), `sni_level_config` (TP-03).

**Parciales (6)**: Track evaluation matrix (TP-01 -- tabla existe pero routing evaluador incompleto), SISREC workflow (HΩ-14 -- 4 SLA estados pero sin formalidad CGR 8-phase completa), TP-02 fondos 8% (concepto pero sin tabla dedicada), clasificador presupuestario (4/6 niveles).

### 4.5.2 Umbrales Financieros (18 valores del Omega)

Todos los umbrales financieros estan parametrizados en `core.financial_threshold` (10 filas: 4 UTM + 5 glosa% + UTM_VALUE) y/o en `core.financing_track.thresholds` (JSONB por track). Helpers: `_get_utm_value(db)`, `_get_threshold(code, db)`, `_check_utm_threshold(ipr_id, code, db)`.

| # | Umbral | Valor | Fuente Normativa | Estado GORE_OS |
|:-:|--------|-------|------------------|:--------------:|
| U-01 | CORE approval requerida | >7.000 UTM | LOC GORE Art. 36 | **IMPL** (gate F3→F4, `core_approval` JSONB) |
| U-02 | Exencion RATE/RS | <=5.000 UTM | Res CGR / NIP | **IMPL** (`_check_sni_proporcionalidad`) |
| U-03 | Toma de Razon CGR obligatoria | >2.500 UTM | Art. 99 CPR | **IMPL** (`cgr_res30_utm` en thresholds JSONB) |
| U-04 | Garantia fiel cumplimiento | >1.000 UTM | LOC GORE | RED |
| U-05 | Tope administracion | 5% del total | Ley Presupuestos | **IMPL** (`GLOSA_05_ADMIN` en financial_threshold) |
| U-06 | Tope honorarios | 5% del subtotal | Ley Presupuestos | **IMPL** (`GLOSA_05_HONORARIOS`) |
| U-07 | Tope activos no financieros | 10% en SNI | NIP | **IMPL** (`GLOSA_10_ANF`) |
| U-08 | Tope equipamiento | 20% del total | Ley Presupuestos | **IMPL** (`GLOSA_20_EQUIP`) |
| U-09 | Tope remuneraciones | 30% del total | Ley Presupuestos | **IMPL** (`GLOSA_30_REMUNERACIONES`) |
| U-10 | C33 conservation threshold | >30% costo reposicion → SNI | Circular 33 | **IMPL** (`_check_c33_conservation`) |
| U-11 | FRIL monto maximo por proyecto | Variable por categoria | Res GORE | RED (sin taxonomia A1-D3) |
| U-12 | FRIL proyectos/comuna | Max 5 por llamado | Res GORE | **IMPL** (`_check_fril_max_per_comuna`) |
| U-13 | 8% intermedias tope | Variable por fondo | Ley Presupuestos | RED |
| U-14 | 8% base tope | Variable por fondo | Ley Presupuestos | RED |
| U-15 | SNI proporcionalidad nivel 0 | <=1.500 UTM | MDSF/NIP | **IMPL** (`sni_level_config` nivel 0) |
| U-16 | SNI proporcionalidad nivel 1 | 1.500-5.000 UTM | MDSF/NIP | **IMPL** (`sni_level_config` nivel 1) |
| U-17 | SNI proporcionalidad nivel 2 | 5.000-25.000 UTM | MDSF/NIP | **IMPL** (`sni_level_config` nivel 2) |
| U-18 | SNI proporcionalidad nivel 3 | >25.000 UTM | MDSF/NIP | **IMPL** (`sni_level_config` nivel 3) |

**Cobertura**: 14/18 implementados (78%). Los 4 pendientes (U-04 garantias, U-11 montos FRIL por categoria, U-13/U-14 topes 8% por fondo) requieren tablas parametricas adicionales (TP-02, TP-04).

**Nota arquitectura**: Los umbrales viven en dos niveles: (1) `core.financial_threshold` para valores transversales (UTM, glosas %), y (2) `core.financing_track.thresholds` JSONB para valores track-especificos (`max_utm`, `min_clp`, `puntaje_min`, `cgr_res30_utm`, `licitacion_max_days`, `sisrec_mandatory_utm`, `core_approval`). El helper `_check_track_amount_gates()` lee ambos.

### 4.5.3 Reglas de Glosa (7/7 implementadas)

Las glosas presupuestarias son restricciones legales sobre el uso de fondos. Todas las reglas estan codificadas en `check_glosa_rules(ipr_id, db)` que se invoca en el gate F3→F4:

| Glosa | Regla | Restriccion Operativa | Estado |
|:-----:|-------|----------------------|:------:|
| 03 | Prohibicion contratacion permanente | FNDR no puede financiar personal de planta | **IMPL** (`_check_glosa03_prohibition`) |
| 05 | Tope administracion | 5% del monto total | **IMPL** (`GLOSA_05_ADMIN` threshold) |
| 05 | Tope honorarios | 5% del subtotal | **IMPL** (`GLOSA_05_HONORARIOS` threshold) |
| 06 | Single-purpose MML | Programas Glosa 06 deben tener exactamente 1 Proposito en MML | **IMPL** (`_check_glosa06_single_purpose`) |
| 10 | Tope activos no financieros | 10% en SNI | **IMPL** (`GLOSA_10_ANF` threshold) |
| 20 | Tope equipamiento | 20% del monto total | **IMPL** (`GLOSA_20_EQUIP` threshold) |
| 30 | Tope remuneraciones | 30% del monto total | **IMPL** (`GLOSA_30_REMUNERACIONES` threshold) |

Las 5 glosas porcentuales (05 admin, 05 honorarios, 10, 20, 30) estan parametrizadas en `core.financial_threshold` y se evaluan via `check_glosa_rules()`. Glosa 03 y 06 son reglas logicas (no porcentuales) implementadas como gate functions dedicadas.

### 4.5.4 Reglas Track-Especificas (7 tracks x validaciones)

El Omega define validaciones operativas por mecanismo de financiamiento. Desde v2.0, 19 gate functions en `ipr.py` implementan la mayoria de estas reglas, invocadas por `_evaluate_phase_gates()` en cada transicion de estado:

#### Track A -- SNI (Sistema Nacional de Inversiones)

| Regla | Detalle | Estado |
|-------|---------|:------:|
| Proporcionalidad 4 niveles | Nivel 0 (<=1.500 UTM): solo perfil. Nivel 3 (>25.000 UTM): evaluacion completa MDSF | **IMPL** (`_check_sni_proporcionalidad`, `sni_level_config` 4 niveles, Ciclo 23) |
| RATE vigencia 3 anos | RS caduca si no obtiene ID presupuestario en 36 meses | **IMPL** (`_check_rs_vigencia`, `rs_validity_years` desde `sni_level_config`, Ciclo 23) |
| ITF vs RS distincion | Dictamen ITF (Transfers) != RATE RS (SNI) en persistencia y workflow | **IMPL** (`_check_evaluation_type_match`, Ciclo 24) |
| Admisibilidad F1 sub-estados | PRE-ADMISIBLE → ADMISIBLE requiere checklist track-specific | RED |
| Evaluador routing | MDSF para Nivel 2+, SEREMI sectorial para Nivel 1 | RED |

#### Track B -- Circular 33

| Regla | Detalle | Estado |
|-------|---------|:------:|
| 30% conservation threshold | Si conservacion >30% costo reposicion → reclasificar a SNI | **IMPL** (`_check_c33_conservation`, informacional, Ciclo 23) |
| Certificacion tecnica | SERVIU para edificacion, MOP para vialidad | RED |
| Sin evaluacion MDSF | Evaluacion tecnica interna GORE | PARCIAL (evaluador asignable, sin routing automatico) |

#### Track C -- FRIL

| Regla | Detalle | Estado |
|-------|---------|:------:|
| Fraccionamiento artificial | Deteccion subdivision para evadir umbral → RECHAZO admisibilidad | **IMPL** (`_check_fril_fraccionamiento`, sibling detection +-90d, Ciclo 22) |
| 5 proyectos/comuna | Max 5 por llamado (A2 Agua y A3 Vial exentos) | **IMPL** (`_check_fril_max_per_comuna`, Ciclo 22) |
| 90 dias tender caducidad | Aprobacion tecnica caduca si no licita en 90 dias | **IMPL** (`_check_fril_tender_deadline`, `licitacion_max_days` JSONB, Ciclo 24) |
| 12 categorias A1-D3 | Taxonomia FRIL con montos maximos diferenciados | RED (TP-04 pendiente) |
| Convenio-marco municipal | Requiere convenio vigente con municipalidad postulante | RED |

#### Track D -- FRPD / Track E2 -- Transferencias PPR

| Regla | Detalle | Estado |
|-------|---------|:------:|
| Scoring competitivo | Puntajes evaluacion con pesos y ranking | **IMPL** (`numeric_score`, `rank_position`, `rank_total` en `evaluation_assignment`, Ciclo 22) |
| Comite evaluador externo | 3-5 evaluadores independientes | RED |
| Dictamen ITF | Distinto de RATE RS, plazo diferente | **IMPL** (`_check_evaluation_type_match`, Ciclo 24) |

#### Track E1 -- Concurso 8%

| Regla | Detalle | Estado |
|-------|---------|:------:|
| Morosos SISREC bloqueo total | Entidades con rendiciones vencidas → fondos bloqueados TOTALMENTE | **IMPL** (`_check_morosos_sisrec`, F3→F4 + F4→F5, Ciclo 24) |
| Pagare notarial | 100% monto, 18 meses vigencia, requerido para privados | **IMPL** (`_check_pagare_notarial`, Ciclo 24) |
| Directorio vigente <60 dias | Certificado Registro Civil, validez 60 dias | **IMPL** (`_check_directorio_certificate`, Ciclo 24) |
| Parentesco inhabilitacion | Hasta 3/4 consanguinidad segun tipo entidad | **RED** (HΩ-02, no iniciado) |
| 7 fondos distribucion | Presupuesto diferenciado por fondo con topes intermedios/base | RED (TP-02 pendiente) |
| Scores/Rankings persistidos | Puntajes evaluacion deben quedar en DB | **IMPL** (`_check_ranking_persistence`, `numeric_score` + `rank_position`, Ciclo 24) |

### 4.5.5 Tablas Parametricas

El Omega define 6 tablas parametricas. Estado actualizado post-Ciclo 25:

| # | Tabla | Dimensiones | Rows Est. | Estado | Implementacion |
|:-:|-------|-------------|:---------:|:------:|----------------|
| TP-01 | Track Evaluation Matrix | 7 tracks x (mecanismo, monto, evaluador, producto, plazo, ejecutor) | 7 | **PARCIAL** | `core.financing_track` (7 registros) + `thresholds` JSONB. Falta routing evaluador automatico |
| TP-02 | Subvencion 8% Fund Distribution | 7 fondos x (presupuesto, tope_intermedia, tope_base, especiales) | 7 | **PENDIENTE** | Concepto cubierto por `_check_morosos_sisrec` pero sin tabla de distribucion por fondo |
| TP-03 | SNI Proportionality Levels | 4 niveles x (rango_utm, evaluador, producto, plazo, requisitos) | 4 | **CERRADO** | `core.sni_level_config` (4 niveles), admin CRUD `/api/admin/sni-levels`, `_check_sni_proporcionalidad()` (Ciclo 23) |
| TP-04 | FRIL Category Taxonomy | 12 categorias A1-D3 x (nombre, monto_max, exenciones) | 12 | **PENDIENTE** | Sin tabla. `_check_fril_max_per_comuna` existe pero sin taxonomia de categorias |
| TP-05 | Budget Cycle Timeline | 17 hitos x (fase, mes, responsable, entregable) | 17 | **CERRADO** | `core.budget_cycle_milestone` + `core.budget_cycle_tracking`, 5 endpoints, 8 tests, frontend page (HΩ-15) |
| TP-06 | Rendition SLA Full Cycle | 8 fases x (responsable, SLA_dias, escalamiento, sancion) | 8 | **PENDIENTE** | 4/8 fases con SLA (RTF 7d, VISADA_RTF 1d, UCR 2d, OBSERVADA 15d). Falta formalidad CGR 8-phase completa |

**Resumen**: 2/6 cerradas (TP-03, TP-05), 1 parcial (TP-01), 3 pendientes (TP-02, TP-04, TP-06).

### 4.5.6 SLAs y Plazos Operativos

| SLA/Plazo | Valor Omega | Implementado | Estado |
|-----------|-------------|:------------:|:------:|
| RTF revision rendicion | 7 dias | SLA en `_RENDICION_SLA_DAYS` | **IMPL** |
| VISADA_RTF transito | 1 dia | SLA en `_RENDICION_SLA_DAYS` | **IMPL** (HΩ-14 W1) |
| UCR revision rendicion | 2 dias | SLA en `_RENDICION_SLA_DAYS` | **IMPL** |
| OBSERVADA subsanacion | 15 dias | SLA en `_RENDICION_SLA_DAYS` | **IMPL** (HΩ-14 W1) |
| Ciclo SISREC completo GORE-side | 14 dias target | `phase_entered_at` + `responsible_id` tracking | **PARCIAL** (4/4 SLA estados, falta formalidad CGR 8-phase) |
| Caducidad aprobacion tecnica FRIL | 90 dias | `_check_fril_tender_deadline`, `licitacion_max_days` JSONB | **IMPL** (Ciclo 24) |
| Vigencia RATE/RS | 3 anos (variable por nivel) | `_check_rs_vigencia`, `rs_validity_years` desde `sni_level_config` | **IMPL** (Ciclo 23) |
| Validez certificado directorio | 60 dias | `_check_directorio_certificate` | **IMPL** (Ciclo 24) |
| Vigencia pagare 8% | 18 meses | `_check_pagare_notarial` (>=18mo) | **IMPL** (Ciclo 24) |
| Plazo rendir post-termino convenio | 60 dias | Sin enforcement | RED |
| Plazo CGR Toma de Razon | 30 dias | Sin tracking | RED |
| Periodicidad informes avance | Variable por track | Sin enforcement | RED |

**Cobertura**: 9/12 implementados (75%). Los 3 pendientes (post-termino convenio, plazo CGR, periodicidad informes) requieren integraciones externas o SLAs adicionales.

---

## 5. Delta v2.0 → v3.0

### 5.1 Ciclos Completados desde v2.0 (11 ciclos)

| Ciclo | Tema | Entregables Clave |
|-------|------|-------------------|
| 20+21 | Compliance Doble | `core.financial_threshold` (10 filas), glosa engine (7/7 reglas), clasificador presupuestario 4 niveles |
| 22 | Track Enforcement | FRIL/FRPD/SUBV8 gates, `numeric_score`, Glosa 03, CORE override |
| 23 | Track Rules Engine | 6 gate functions (FRIL x2, SNI x2, C33, TRANSFER), `sni_level_config` |
| 24 | HΩ Remaining | FRIL tender, rankings, pagare, directorio, morosos, glosa06 |
| 25 | DGI Cartera IPR | Portfolio control: 3 endpoints, health signal coalgebra, cockpit drill-down, 12 tests |
| Remediacion | 8 audit waves | Security hardening, concurrency, IPR tab extraction, `financing_track` DB, `schema_migration`, ADRs |
| UX Remediation | 3 cascading waves | Sonner toast, ARIA/a11y, responsive (DrawerPanel/FilterBar/Sidebar mobile), toast errors (10 pages) |
| UX Wave 2 | 5 hallazgos | Art. 18 error enriquecido, `/presupuesto/nuevo`, CDPs endpoint+UI, bulk cuotas convenio, `/datos` responsive |
| HΩ-14 SISREC | 2 waves | W1: SLA 4/4 + ciclo endpoint. W2: `phase_entered_at`, `responsible_id`, 14d target |
| HΩ-15 | Budget Cycle | TP-05: 17 milestones, `budget_cycle_milestone` + `budget_cycle_tracking`, 5 endpoints, frontend page |
| Thresholds | Parametrizacion | 7 valores hardcoded → `financing_track.thresholds` JSONB |

### 5.2 Hallazgos v1.0 Resueltos (11/11 -- todos cerrados)

| ID v1.0 | Brecha | Resolucion | Ciclo |
|---------|--------|------------|:-----:|
| H-REN-02 | Art. 18 CGR -- bloqueo transferencias morosas | `_check_pending_renditions()` en convenios.py | C19 |
| H-REN-03 | SISREC rendiciones sin workflow | 8-state machine + SLA + audit trail | C19 |
| H-IPR-04 | Poly-Switch routing evaluacion | `financing_track` table + TrackCard UI | C18 |
| H-IPR-05 | Dictamenes evaluacion | `evaluation_assignment` + `evaluator_type` scheme | C18 |
| H-GOB-01 | CORE solo crisis, no sesiones/votacion | 9 endpoints CORE sessions + quorum + gate F3→F4 | C11 |
| H-CON-BUG | Trigger fn_validate_state_transition bug | Wave 1 migration (dynamic column via TG_ARGV[0]) | C-Rem |
| H-IPR-MCD | MCD phases sin workflow | IPR transiciones endpoint con gates por fase | C18 |
| H-IPR-06 | 11 umbrales financieros | 14/18 en `core.financial_threshold` + `financing_track.thresholds` JSONB | C20-21 |
| H-FIN-03 | 8 glosas presupuestarias | 7/7 en `check_glosa_rules()` | C20-21 |
| H-FIN-01 | Clasificador presupuestario plano | 4/6 niveles implementados | C21 |
| H-DGI-TDE | Indicador TDE sin datos reales | Parcial -- 4/5 indicadores con refresh desde DB reales | C25 |

### 5.3 Hallazgos HΩ Resueltos (10 cerrados desde v2.0)

| ID | Brecha | Implementacion | Ciclo |
|----|--------|----------------|:-----:|
| HΩ-01 | Fraccionamiento FRIL | `_check_fril_fraccionamiento()` -- sibling detection +-90d | C22 |
| HΩ-03 | Pagare 8% privados | `_check_pagare_notarial()` -- >=100% cobertura, >=18mo vigencia | C24 |
| HΩ-04 | Directorio <60d | `_check_directorio_certificate()` -- cert freshness check | C24 |
| HΩ-05 | RATE vigencia 3 anos | `_check_rs_vigencia()` -- `rs_validity_years` desde `sni_level_config` | C23 |
| HΩ-06 | MML single-purpose | `_check_glosa06_single_purpose()` -- single MML purpose gate | C24 |
| HΩ-07 | C33 30% conservation | `_check_c33_conservation()` -- conservation/reposition ratio | C23 |
| HΩ-08 | FRIL 90d tender | `_check_fril_tender_deadline()` -- LICITACION milestone deadline | C24 |
| HΩ-09 | FRIL 5/comuna | `_check_fril_max_per_comuna()` -- max per territory, A2/A3 exempt | C22 |
| HΩ-10 | Morosos SISREC | `_check_morosos_sisrec()` -- executor overdue renditions block | C24 |
| HΩ-11 | SNI proporcionalidad | `_check_sni_proporcionalidad()` -- 4 eval levels by UTM | C23 |
| HΩ-12 | ITF vs RS | `_check_evaluation_type_match()` -- eval type consistency | C24 |
| HΩ-13 | Scores/Rankings | `_check_ranking_persistence()` -- `numeric_score` + rank | C24 |
| HΩ-15 | Budget cycle T-1→T→T+1 | TP-05: 17 milestones, 5 endpoints, 8 tests, frontend page | C-HΩ15 |

### 5.4 Hallazgos HΩ Abiertos (2/15)

| ID | Brecha | Estado | Detalle | Prioridad |
|----|--------|--------|---------|:---------:|
| HΩ-02 | Parentesco 8% | **ABIERTO** | Inhabilitacion por consanguinidad 3/4 grado -- no iniciado. Requiere tabla de parentesco y validacion contra directorio | **Alta** |
| HΩ-14 | SISREC ciclo completo | **PARCIAL** | 4/4 SLA estados (RTF 7d, VISADA_RTF 1d, UCR 2d, OBSERVADA 15d), `phase_entered_at`, `responsible_id`, ciclo endpoint, 14d target. Pendiente: formalidad CGR 8-phase completa (TP-06) | **Alta** |

### 5.5 Tabla Consolidada HΩ (15 hallazgos)

| ID | Hallazgo | Estado | Implementacion |
|----|----------|:------:|----------------|
| HΩ-01 | Fraccionamiento FRIL | CERRADO | `_check_fril_fraccionamiento()` -- sibling detection +-90d, Ciclo 22 |
| HΩ-02 | Parentesco 8% | **ABIERTO** | No iniciado -- inhabilitacion por consanguinidad 3/4 grado |
| HΩ-03 | Pagare 8% | CERRADO | `_check_pagare_notarial()` -- >=100% cobertura, >=18mo vigencia, Ciclo 24 |
| HΩ-04 | Directorio <60d | CERRADO | `_check_directorio_certificate()` -- cert freshness check, Ciclo 24 |
| HΩ-05 | RATE vigencia 3 anos | CERRADO | `_check_rs_vigencia()` -- rs_validity_years desde sni_level_config, Ciclo 23 |
| HΩ-06 | MML single-purpose | CERRADO | `_check_glosa06_single_purpose()` -- single MML purpose gate, Ciclo 24 |
| HΩ-07 | C33 conservation | CERRADO | `_check_c33_conservation()` -- conservation/reposition ratio, Ciclo 23 |
| HΩ-08 | FRIL 90d tender | CERRADO | `_check_fril_tender_deadline()` -- LICITACION milestone deadline, Ciclo 24 |
| HΩ-09 | FRIL 5/comuna | CERRADO | `_check_fril_max_per_comuna()` -- max per territory, A2/A3 exempt, Ciclo 22 |
| HΩ-10 | Morosos SISREC | CERRADO | `_check_morosos_sisrec()` -- executor overdue renditions block, Ciclo 24 |
| HΩ-11 | SNI proporcionalidad | CERRADO | `_check_sni_proporcionalidad()` -- 4 eval levels by UTM, Ciclo 23 |
| HΩ-12 | ITF vs RS | CERRADO | `_check_evaluation_type_match()` -- eval type consistency, Ciclo 24 |
| HΩ-13 | Scores/Rankings | CERRADO | `_check_ranking_persistence()` -- numeric_score + rank, Ciclo 24 |
| HΩ-14 | SISREC ciclo completo | **PARCIAL** | 4/4 SLA estados, phase_entered_at, responsible_id, ciclo endpoint, 14d target. Remaining: 8-phase CGR formality |
| HΩ-15 | Budget Cycle T-1→T→T+1 | CERRADO | TP-05 con 17 milestones, 5 endpoints, 8 tests, frontend page. Ciclo HΩ-15 |

### 5.6 Hallazgos v2.0 No-HΩ (estado actualizado)

| ID | Brecha | Estado v3.0 | Nota |
|----|--------|:-----------:|------|
| H2-TRACK-ENGINE | Engine reglas por track (Dom 13-19) | **PARCIAL** | 19 gate functions implementadas cubren la mayoria de reglas criticas. Quedan routing evaluador y taxonomia FRIL |
| H2-PLAN-INST | Sin instrumentos planificacion | ABIERTO | Sin cambios |
| H2-INTEROP | 0 integraciones externas | ABIERTO | Sin cambios |
| H2-RRHH | Dominio D-BACK 0% | ABIERTO | Sin cambios |
| H2-AUDIT-LOG | Sin audit trail transversal | ABIERTO | Sin cambios |
| H2-ROLES-EMPTY | 5/13 roles con 0 users | ABIERTO | Sin cambios |
| H2-IPR-FIELDS | sponsor_division_id/assignee_id 0% | ABIERTO | Sin cambios |
| H2-GEO | Territorio sin IDE/GIS | ABIERTO | Sin cambios |

---

## 6. Gap Analysis Priorizado

### 6.1 Críticos — Riesgo Legal/Compliance

| Gap | CQs Afectadas | Stories | Impacto Regulatorio |
|-----|:-------------:|:-------:|---------------------|
| 10 umbrales financieros sin codificar | CQ-461..472 (12) | ~25 | Ley Presupuestos, Res CGR, LOC GORE |
| Integración CGR (Toma de Razón) | CQ-124,129,138 | ~10 | Art. 99 CPR — resoluciones >2.500 UTM |
| Clasificador presupuestario plano | CQ-064..070 | ~20 | DL 1.263, Ley Presupuestos |

**Esfuerzo estimado**: ~15-20 días. El engine de umbrales es el componente más riesgoso legalmente.

### 6.2 Altos — Core Functionality

| Gap | CQs Afectadas | Stories | Valor Funcional |
|-----|:-------------:|:-------:|-----------------|
| Engine reglas por track (Dom 13-19) | 163 CQs | ~50 | Desbloquea 35% del catálogo CQ |
| 8 glosas como reglas de gasto | CQ-067..070,467..471 | ~15 | Validación automática presupuestaria |
| Integraciones externas (BIP, SIGFE) | CQ-234..249 | ~40 | TDE fundamental |
| Instrumentos planificación (ERD, ARI) | CQ-043..044 | ~15 | Vinculación obligatoria IPR→planificación |

**Esfuerzo estimado**: ~30-40 días. El engine de reglas por track tiene el mayor ROI (163 CQs).

### 6.3 Medios — Enhancements

| Gap | CQs Afectadas | Stories | Prioridad |
|-----|:-------------:|:-------:|:---------:|
| RRHH / Personas (D-BACK) | — | 105 | Media |
| Audit trail transversal | CQ-245 | ~10 | Media |
| IDE / GIS territorial | CQ-024..025,059 | 48 | Baja |
| Roles vacíos activados | CQ-023,026,027 | ~10 | Baja |
| Planificación (ERD, ARI, PROPIR) | CQ-043,044 | 33 | Media |

---

## 7. Datos de Base (DB snapshot 2026-03-08)

### 7.1 Tablas clave (90 tablas: core=62, meta=5, ref=3, txn=20 partitions)

| Tabla | Registros | Nota |
|-------|----------:|------|
| core.ipr | 3,622 | 1,973 con mcd_phase (54%), 3,621 con mechanism (99.97%) |
| core.budget_program | 25,761 | Programas presupuestarios |
| core.budget_carryover | 13,378 | Arrastres inter-anuales |
| core.document | 12,800 | Via ETL Phase 2 |
| core.ipr_party | 8,805 | 9 roles (POSTULANTE, FORMULADOR, EJECUTOR, etc.) |
| core.budget_commitment | 4,617 | CDPs vinculados |
| core.ipr_territory | 3,596 | 4 tipos impacto |
| core.organization | 3,360 | 33 internas GORE, jerarquia 3 niveles |
| core.administrative_act | 1,421 | 7-step state machine + audit trail |
| core.resolution | 1,421 | Auto-creadas con actos RESOLUCION |
| core.rendition | 1,234 | SISREC 8-state + SLA 4/4 |
| core.rendition_history | -- | Audit trail transiciones (trigger) |
| core.agreement | 537 | 13 estados, 6 tipos |
| core.financial_threshold | 10 | 4 UTM + 5 glosa% + UTM_VALUE (nuevo v3.0) |
| core.financing_track | 7 | Tracks evaluacion + thresholds JSONB (nuevo v2.0, extendido v3.0) |
| core.sni_level_config | 4 | 4 niveles proporcionalidad SNI (nuevo v3.0) |
| core.budget_cycle_milestone | 17 | Hitos ciclo presupuestario TP-05 (nuevo v3.0) |
| core.budget_cycle_tracking | -- | Tracking por IPR (nuevo v3.0) |
| core.evaluation_assignment | -- | Evaluaciones por IPR + numeric_score + rank |
| core.schema_migration | 15 | Tracking DDL migrations |
| core.session_vote | -- | Votacion CORE |
| ref.category | 731+ | 82 schemes (verificado) |

### 7.2 API Coverage (138 endpoints, 19 routers)

| Router | Prefix | Endpoints | Dominio |
|--------|--------|:---------:|---------|
| ipr.py | /api/ipr | 20 | IPR + partes + territorio + hitos + avances + evaluaciones + gates (19 gate functions) |
| admin.py | /api/admin | 18 | Usuarios + divisiones + financing-tracks + thresholds + sni-levels |
| dgi_data.py | /api/dgi/data | 14 | Indicadores + datos + rendiciones SISREC |
| core_sessions.py | /api/core-sessions | 9 | Sesiones CORE + votacion + lifecycle gate F3→F4 |
| convenios.py | /api/convenios | 10 | Convenios + cuotas + bulk cuotas + transiciones |
| reuniones.py | /api/reuniones | 8 | Reuniones crisis |
| presupuesto.py | /api/presupuesto | 8 | Presupuesto + CDPs + presupuesto/nuevo |
| catalogs.py | /api/catalogs | 7 | Categorias + busquedas |
| compromisos.py | /api/compromisos | 7 | Compromisos operacionales |
| dgi_reports.py | /api/dgi/reports | 6 | Informes institucionales |
| dgi_cartera.py | /api/dgi/cartera | 3 | Cartera IPR + resumen + cuotas vencidas |
| actos.py | /api/actos | 5 | Actos administrativos + state machine |
| dashboard.py | /api/dashboard | 5 | Dashboards role-aware (4 variantes) |
| problemas.py | /api/problemas | 4 | Problemas IPR |
| dgi_initiatives.py | /api/dgi/initiatives | 4 | Iniciativas Kanban + WIP limits |
| alertas.py | /api/alertas | 2 | Alertas sistema |
| auth.py | /api/auth | 2 | Autenticacion JWT + brute-force lockout |
| dgi_cockpit.py | /api/dgi/cockpit | 1 | Panel DGI (role-aware) |
| search.py | /api/search | 1 | Busqueda global |

### 7.3 Test Coverage (334 tests, 28 modules)

| Modulo | Tests | Estado |
|--------|:-----:|--------|
| sisrec | 27 | 27 pass |
| ciclo24 | 22 | 22 pass |
| track_enforcement | 20 | 20 pass |
| thresholds | 18 | 18 pass |
| track_rules | 18 | 18 pass |
| presupuesto | 18 | 18 pass |
| compromisos | 16 | 16 pass |
| polyswitch | 14 | 14 pass |
| ipr_children | 14 | 14 pass |
| actos | 12 | 12 pass |
| security_readonly | 12 | 12 pass |
| auth | 12 | 12 pass |
| convenios | 12 | 12 pass |
| dgi_cartera | 12 | 12 pass |
| admin | 11 | 11 pass |
| reuniones | 11 | 11 pass |
| core_sessions | 10 | 10 pass |
| catalogs | 8 | 8 pass |
| problemas | 8 | 8 pass |
| initiatives | 7 | 7 pass |
| dashboard | 6 | 6 pass |
| ipr_lifecycle | 6 | 6 pass |
| alertas | 6 | 6 pass |
| concurrency | 5 | 5 pass |
| rendiciones | 5 | 5 pass |
| search | 4 | 4 pass |
| dgi_cockpit | 4 | 4 pass |
| dgi_reports | 4 | 1 pass + 3 skip |
| **TOTAL** | **334** | **330 pass + 4 skip** |

---

## 8. Roadmap Recomendado

### Ciclos Completados (v2.0 → v3.0)

| Ciclo | Foco | Estado | Reglas Omega |
|:-----:|------|:------:|:------------:|
| 20+21 | Compliance Engine (umbrales + glosas + clasificador) | **COMPLETADO** | U-01..U-18, HΩ-06, 7 glosas |
| 22 | Track Enforcement (FRIL + FRPD + SUBV8) | **COMPLETADO** | HΩ-01,09,11 |
| 23 | Track Rules Engine (SNI + C33 + TRANSFER) | **COMPLETADO** | HΩ-05,07,12; TP-03 |
| 24 | HΩ Remaining (tender, rankings, pagare, directorio, morosos, glosa06) | **COMPLETADO** | HΩ-03,04,06,08,10,13 |
| 25 | DGI Cartera IPR (portfolio control + health signal) | **COMPLETADO** | -- |
| HΩ-14 | SISREC SLA + ciclo | **COMPLETADO** (parcial) | HΩ-14 parcial |
| HΩ-15 | Budget Cycle Timeline | **COMPLETADO** | HΩ-15, TP-05 |

### Siguiente -- HΩ-02 Parentesco 8% (5-7 dias)

| Componente | Detalle | Esfuerzo |
|------------|---------|:--------:|
| Tabla parentesco | `core.kinship_declaration` con grado consanguinidad/afinidad | 1d |
| Gate function | `_check_parentesco_8pct()` -- inhabilitacion 3/4 grado segun tipo entidad | 2d |
| API endpoint | CRUD declaraciones parentesco por IPR/organizacion | 1d |
| Frontend | Formulario declaracion en tab evaluacion | 1d |
| Tests | 8-10 tests cobertura completa | 1d |

### Medio Plazo (3-5 semanas)

| Item | Detalle | Esfuerzo | Impacto |
|------|---------|:--------:|---------|
| TP-02 | Tabla distribucion fondos 8% (7 fondos x topes) | 3-5d | Desbloquea U-13, U-14 |
| TP-04 | Taxonomia FRIL A1-D3 (12 categorias x montos max) | 3-5d | Desbloquea U-11 |
| TP-06 + HΩ-14 full | SISREC 8-phase CGR completo con escalamiento | 5-10d | Dom 08: 47%→75% |
| Clasificador 5-6 | Niveles Programa + Item + Asignacion presupuestaria | 5d | Dom 03: 30%→55% |

### Largo Plazo

| Item | Detalle | Esfuerzo | Impacto |
|------|---------|:--------:|---------|
| Integraciones externas | ClaveUnica, PISEE, BIP, SIGFE, CGR | 30-60d | TDE Dom10: 12%→35%, 108 stories |
| Instrumentos planificacion | ERD, ARI, PROPIR vinculados a IPR | 10-15d | Planificacion territorial |
| RRHH / D-BACK | Fichas funcionarios, nomina, calificaciones | 20-30d | 105 stories |
| IDE/GIS territorial | Visualizacion geoespacial `ipr_territory` | 10-15d | 48 stories |

### Proyeccion de Score CQ (Omega-adjusted)

| Milestone | CQ Score Promedio | Reglas Omega Cubiertas | HΩ Status |
|-----------|:-----------------:|:---------------------:|:---------:|
| v2.0 (Mar 3) | 25.2% | 7/81+ (10%) | 3/15 |
| **v3.0 actual (Mar 8)** | **~40-44%** (est.) | **~44/81+ (54%)** | **13/15** |
| Post-HΩ-02 | ~42-46% | ~46/81+ (57%) | 14/15 |
| Post-TP-02/04/06 | ~46-50% | ~52/81+ (64%) | 14/15 |
| Post-Integraciones | ~55-60% | ~55/81+ (68%) | 15/15 |

---

## 9. Conclusiones

### Lo que GORE_OS hace bien

1. **IPR como entidad central**: 67% de cobertura ontologica, 20 endpoints, 11 tabs, 3,622 registros reales, 19 gate functions en lifecycle
2. **Compliance como codigo**: 10 umbrales financieros parametricos, 7 glosas codificadas, clasificador 4 niveles -- base legal ejecutable
3. **19 gate functions**: Track enforcement completo para FRIL (3 gates), SNI (2), C33 (1), SUBV8 (4), glosas (2), evaluacion (1), CORE (1), track amounts (1), budget cycle (1), mechanism-aware (1), Art. 18 (1), morosos (1)
4. **DB-parametric thresholds**: Valores en `core.financial_threshold` y `financing_track.thresholds` JSONB -- sin hardcoding, administrables via API
5. **SISREC multi-rol**: 8-state machine con 4 SLA estados (RTF 7d, VISADA_RTF 1d, UCR 2d, OBSERVADA 15d), `phase_entered_at`, `responsible_id`, audit trail, Art. 18 enforcement
6. **Budget Cycle Timeline**: TP-05 con 17 milestones, tracking por IPR, 5 endpoints, frontend page
7. **DGI operativo**: Cartera IPR con health signal coalgebra, cockpit drill-down, indicadores con refresh desde DB reales, Kanban con WIP limits
8. **Seguridad**: JWT + brute-force + security headers + advisory locks + 334 tests (28 modulos)
9. **Audit trails**: `rendition_history`, `administrative_act_history`, `commitment_history` con triggers automaticos

### Lo que falta para ser "sistema operativo"

1. **HΩ-02 Parentesco 8%**: Unico hallazgo critico abierto -- inhabilitacion por consanguinidad 3/4 grado
2. **Integraciones Estado**: ClaveUnica/PISEE/BIP/SIGFE/CGR desbloquean D-TDE (108 stories, Dom 10 al 12%)
3. **Clasificador presupuestario**: 4/6 niveles -- faltan Programa e Item/Asignacion
4. **SISREC 8-phase CGR**: 4/4 SLA estados pero falta formalidad completa del ciclo CGR (TP-06)
5. **3 tablas parametricas**: TP-02 (fondos 8%), TP-04 (taxonomia FRIL), TP-06 (SISREC full cycle)

### Metrica de cierre

De las 472 CQs: **~40-44% score estimado** (requiere re-audit para cifra exacta). Mejora significativa vs 25.2% de v2.0.

De las 81+ reglas Omega: **~44 implementadas (54%), 6 parciales (7%), ~31 sin implementar (38%)**

De los 15 hallazgos HΩ: **13 cerrados (87%), 1 parcial (HΩ-14), 1 abierto (HΩ-02)**

La frontera de valor se ha desplazado desde "compliance como codigo" (ya logrado en gran parte) hacia: (1) integraciones externas que desbloquean TDE, y (2) las 3 tablas parametricas restantes que completan el engine de tracks.

---

## 10. Referencias

- `docs/GORE_OS_Audit_v1.0.md` -- Auditoria v1.0 (2026-02-27)
- `docs/GORE_OS_Audit_v2.0.md` -- Auditoria v2.0 (2026-03-03)
- `docs/GORE_OS_Audit_Detail_v1.0.md` -- Detalle stories x impl
- `model/stories/` -- 818 historias de usuario (16 dominios)
- `gorenuble/knowledge/ontologies/onto_gorenuble/goreNubleCQs_Master.yml` -- 472 CQs (20 dominios)
- `gorenuble/knowledge/ontologies/onto_gorenuble/goreNubleOntology.ttl` -- 198 OWL classes
- `gorenuble/knowledge/ontologies/onto_gorenuble/omega_gore_nuble_mermaid.md` -- Modelo Omega v2.6.0 (111KB, reglas de negocio operativas)
- `model/model_goreos/sql/goreos_ddl.sql` -- DDL (90 tablas)
- `model/model_goreos/sql/goreos_migration_*.sql` -- 22 archivos migracion (15 tracked en schema_migration)
- `CLAUDE.md` -- Project conventions (actualizado Ciclo 25)
- `docs/GORE_OS_Testing_Ciclo3.md` -- Testing documentation
- `docs/adr/` -- 6 Architecture Decision Records
- `docs/ETL_ARCHITECTURE_v1.0.md` -- ETL pipeline architecture
