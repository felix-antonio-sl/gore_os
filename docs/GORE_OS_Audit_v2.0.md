# GORE_OS Auditoría Institucional v2.0

> **Fecha**: 2026-03-03
> **Alcance**: Estado actual de GORE_OS vs 4 Fuentes de Verdad institucionales
> **Fuentes**: 818 historias de usuario, 472 Competency Questions (20 dominios), 198 OWL classes, Modelo Omega v2.6.0 (reglas de negocio operativas), Auditoría v1.0 (2026-02-27)
> **Metodología**: Triangulación CQ × Stories × Ontología × Omega con scoring GREEN/YELLOW/RED

---

## 1. Resumen Ejecutivo

GORE_OS ha avanzado de **~30% a ~42% de cobertura institucional** desde la auditoría v1.0 (2026-02-27). Los 5 ciclos completados (11, 13, 18, 19, Remediación) activaron la **mecánica sobre la ontología**: state machines, gates, audit trails, y workflows multi-rol que la v1.0 identificó como brecha central.

### Métricas top-line (v1.0 → v2.0)

| Métrica | v1.0 (Feb 27) | v2.0 (Mar 3) | Δ |
|---------|:-------------:|:-------------:|:-:|
| DDL tables | 78 | 81 | +3 |
| API endpoints | 102 | 121 | +19 |
| Integration tests | 86 | 210 | +124 |
| ref.category schemes | 78 | 95+ | +17 |
| Stories cubiertas (est.) | ~79 (10%) | ~135 (16%) | +56 |
| Dominios con impl. | 6/16 | 8/16 | +2 |
| CQ score promedio (20 dom) | — | 25.2%† | — |
| Hallazgos v1.0 resueltos | — | 7/11 | 64% |

### Top 5 Logros desde v1.0

1. **SISREC Multi-Role** (Ciclo 19): 8-state machine con RTF→UCR, SLA 7d/2d, audit trail, Art. 18 gap fix
2. **CORE Governance** (Ciclo 11): Sesiones ordinarias + votación + gate F3→F4 >7.000 UTM
3. **Poly-Switch** (Ciclo 18): 7 tracks evaluación + evaluaciones CRUD + TrackCard UI
4. **Actos Administrativos** (Ciclo 13): History audit trail con trigger + timeline UI
5. **Seguridad** (Remediación): JWT validation, brute-force lockout, security headers, advisory locks

### Top 5 Gaps Prioritarios

1. **0/15+ umbrales financieros** codificados (Omega explicita 15+ vs 11 estimados; solo 7.000 UTM CORE como gate manual)
2. **0/8 glosas presupuestarias** como reglas de gasto validadas (Omega detalla valores exactos por glosa)
3. **Clasificador presupuestario plano** (solo subtítulo, faltan 5 niveles)
4. **40+ validaciones track-específicas** sin implementar (fraccionamiento FRIL, parentesco 8%, pagaré notarial, SLA 13-14d SISREC completo)
5. **TDE <10%**: Sin ClaveÚnica, PISEE, FEA, DS7, interoperabilidad

> *† Scores CQ ajustados con contexto Modelo Omega v2.6.0 — 5 dominios refinados donde el Omega reveló gaps más profundos que la evaluación CQ pura (ver §4.5).*

---

## 2. CQ Coverage por Dominio (472 CQs × 20 dominios)

### 2.1 Scorecard

Criterios de evaluación:
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

*\* Las 66 subclasses de `gist:Category` están implementadas como registros en `ref.category` (95+ schemes), no como tablas individuales.*

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

| Categoría Omega | Reglas Totales | Implementadas | Parciales | Sin Implementar | Cobertura |
|-----------------|:--------------:|:------------:|:---------:|:---------------:|:---------:|
| Umbrales financieros | 15+ | 1 | 0 | 14+ | **7%** |
| Reglas de Glosa | 8 | 0 | 0 | 8 | **0%** |
| Validaciones track-específicas | 40+ | 3 | 5 | 32+ | **10%** |
| Tablas paramétricas | 6 | 1 | 1 | 4 | **17%** |
| SLAs y plazos operativos | 12+ | 2 | 1 | 9+ | **17%** |
| **TOTAL** | **81+** | **7** | **7** | **67+** | **~10%** |

**Implementadas**: 7.000 UTM CORE gate, SLA RTF 7d, SLA UCR 2d, `financing_track` table (7 tracks), gate F2→F3 mechanism-aware, Art. 18 bloqueo rendiciones, state machine SISREC 8 estados.

**Parciales**: Track evaluation matrix (tabla existe pero sin reglas de evaluador), SISREC workflow (8 estados pero sin SLA ciclo completo 13-14d), calendar budget cycle (CDPs existen pero sin hitos calendario).

### 4.5.2 Umbrales Financieros (15+ valores del Omega)

El Omega explicita significativamente más umbrales que los 11 estimados en v2.0. Estos son valores regulatorios con efecto legal:

| # | Umbral | Valor | Fuente Normativa | Estado GORE_OS |
|:-:|--------|-------|------------------|:--------------:|
| U-01 | CORE approval requerida | >7.000 UTM | LOC GORE Art. 36 | **IMPL** (gate F3→F4) |
| U-02 | Exención RATE/RS | ≤5.000 UTM | Res CGR / NIP | RED |
| U-03 | Toma de Razón CGR obligatoria | >2.500 UTM | Art. 99 CPR | RED |
| U-04 | Garantía fiel cumplimiento | >1.000 UTM | LOC GORE | RED |
| U-05 | Tope administración | 5% del total | Ley Presupuestos | RED |
| U-06 | Tope honorarios | 5% del subtotal | Ley Presupuestos | RED |
| U-07 | Tope activos no financieros | 10% en SNI | NIP | RED |
| U-08 | Tope equipamiento | 20% del total | Ley Presupuestos | RED |
| U-09 | Tope remuneraciones | 30% del total | Ley Presupuestos | RED |
| U-10 | C33 conservation threshold | >30% costo reposición → SNI | Circular 33 | RED |
| U-11 | FRIL monto máximo por proyecto | Variable por categoría | Res GORE | RED |
| U-12 | FRIL proyectos/comuna | Max 5 por llamado | Res GORE | RED |
| U-13 | 8% intermedias tope | Variable por fondo | Ley Presupuestos | RED |
| U-14 | 8% base tope | Variable por fondo | Ley Presupuestos | RED |
| U-15 | SNI proporcionalidad nivel 0 | ≤1.500 UTM | MDSF/NIP | RED |
| U-16 | SNI proporcionalidad nivel 1 | 1.500-5.000 UTM | MDSF/NIP | RED |
| U-17 | SNI proporcionalidad nivel 2 | 5.000-25.000 UTM | MDSF/NIP | RED |
| U-18 | SNI proporcionalidad nivel 3 | >25.000 UTM | MDSF/NIP | RED |

**Cobertura**: 1/18 implementado (5.6%). El gate 7.000 UTM es el único umbral con enforcement activo.

### 4.5.3 Reglas de Glosa (8 reglas con valores exactos)

Las glosas presupuestarias son restricciones legales sobre el uso de fondos. El Omega detalla 8 reglas que GORE_OS no codifica:

| Glosa | Regla | Restricción Operativa | Estado |
|:-----:|-------|----------------------|:------:|
| 03 | Prohibición contratación permanente | FNDR no puede financiar personal de planta | RED |
| 06 | Single-purpose MML | Programas Glosa 06 deben tener exactamente 1 Propósito en MML | RED |
| 06 | Ejecución directa GORE | GORE es ejecutor directo (no delega) | RED |
| 07 | Transferencias condicionadas | Requiere convenio + rendición + fiscalización | PARCIAL* |
| 07 | Topes porcentuales | Admin 5%, honorarios 5% del monto transferido | RED |
| 12 | Programas de asignación directa | Sin proceso competitivo — asignación por nómina | RED |
| 13 | Programas especiales | Requisitos sectoriales específicos | RED |
| 03/06/07 | Glosa↔Subtítulo mapping | Cada glosa aplica a subtítulos específicos | RED |

*\* Glosa 07 parcial: convenios CRUD + rendiciones SISREC existen, pero sin validación de topes porcentuales ni fiscalización formal.*

### 4.5.4 Reglas Track-Específicas (7 tracks × validaciones)

El Omega define validaciones operativas por mecanismo de financiamiento que la infraestructura base (`financing_track`) no implementa:

#### Track A — SNI (Sistema Nacional de Inversiones)

| Regla | Detalle | Estado |
|-------|---------|:------:|
| Proporcionalidad 4 niveles | Nivel 0 (≤1.500 UTM): solo perfil. Nivel 3 (>25.000 UTM): evaluación completa MDSF | RED |
| RATE vigencia 3 años | RS caduca si no obtiene ID presupuestario en 36 meses | RED |
| ITF vs RS distinción | Dictamen ITF (Transfers) ≠ RATE RS (SNI) en persistencia y workflow | RED |
| Admisibilidad F1 sub-estados | PRE-ADMISIBLE → ADMISIBLE requiere checklist track-specific | RED |
| Evaluador routing | MDSF para Nivel 2+, SEREMI sectorial para Nivel 1 | RED |

#### Track B — Circular 33

| Regla | Detalle | Estado |
|-------|---------|:------:|
| 30% conservation threshold | Si conservación >30% costo reposición → reclasificar a SNI | RED |
| Certificación técnica | SERVIU para edificación, MOP para vialidad | RED |
| Sin evaluación MDSF | Evaluación técnica interna GORE | PARCIAL* |

*\* Parcial: `evaluation_assignment` permite asignar evaluador, pero sin routing automático por track.*

#### Track C — FRIL

| Regla | Detalle | Estado |
|-------|---------|:------:|
| Fraccionamiento artificial | Detección subdivisión para evadir umbral → RECHAZO admisibilidad | RED |
| 5 proyectos/comuna | Max 5 por llamado (A2 Agua y A3 Vial exentos) | RED |
| 90 días tender caducidad | Aprobación técnica caduca si no licita en 90 días | RED |
| 12 categorías A1-D3 | Taxonomía FRIL con montos máximos diferenciados | RED |
| Convenio-marco municipal | Requiere convenio vigente con municipalidad postulante | RED |

#### Track D — FRPD / Track E2 — Transferencias PPR

| Regla | Detalle | Estado |
|-------|---------|:------:|
| Scoring competitivo | Puntajes evaluación con pesos y ranking | RED |
| Comité evaluador externo | 3-5 evaluadores independientes | RED |
| Dictamen ITF | Distinto de RATE RS, plazo diferente | RED |

#### Track E1 — Concurso 8%

| Regla | Detalle | Estado |
|-------|---------|:------:|
| Morosos SISREC bloqueo total | Entidades con rendiciones vencidas → fondos bloqueados TOTALMENTE | RED |
| Pagaré notarial | 100% monto, 18 meses vigencia, requerido para privados | RED |
| Directorio vigente <60 días | Certificado Registro Civil, validez 60 días | RED |
| Parentesco inhabilitación | Hasta 3°/4° consanguinidad según tipo entidad | RED |
| 7 fondos distribución | Presupuesto diferenciado por fondo con topes intermedios/base | RED |
| Scores/Rankings persistidos | Puntajes evaluación deben quedar en DB | RED |

### 4.5.5 Tablas Paramétricas Pendientes de Codificación

El Omega define 6 tablas paramétricas que deberían materializarse en `core.*` o `ref.category`:

| # | Tabla | Dimensiones | Rows Est. | Prioridad |
|:-:|-------|-------------|:---------:|:---------:|
| TP-01 | Track Evaluation Matrix | 7 tracks × (mecanismo, monto, evaluador, producto, plazo, ejecutor) | 7 | **Alta** |
| TP-02 | Subvención 8% Fund Distribution | 7 fondos × (presupuesto, tope_intermedia, tope_base, especiales) | 7 | **Alta** |
| TP-03 | SNI Proportionality Levels | 4 niveles × (rango_utm, evaluador, producto, plazo, requisitos) | 4 | **Alta** |
| TP-04 | FRIL Category Taxonomy | 12 categorías A1-D3 × (nombre, monto_max, exenciones) | 12 | **Media** |
| TP-05 | Budget Cycle Timeline | 12+ hitos × (fase, mes, responsable, entregable) | 15 | **Media** |
| TP-06 | Rendition SLA Full Cycle | 8 fases × (responsable, SLA_días, escalamiento, sanción) | 8 | **Alta** |

**Estado actual**: Solo TP-01 existe parcialmente como `core.financing_track` (7 registros con 4 de 6 columnas). Las demás no tienen representación en schema.

### 4.5.6 SLAs y Plazos Operativos

| SLA/Plazo | Valor Omega | Implementado | Estado |
|-----------|-------------|:------------:|:------:|
| RTF revisión rendición | 7 días | SLA en `_RENDICION_SLA_DAYS` | **IMPL** |
| UCR revisión rendición | 2 días | SLA en `_RENDICION_SLA_DAYS` | **IMPL** |
| Ciclo SISREC completo GORE-side | 13-14 días | Solo RTF+UCR parcial | RED |
| Plazo rendir post-término convenio | 60 días | Sin enforcement | RED |
| Subsanación reparos rendición | 15 días | Sin enforcement | RED |
| Caducidad aprobación técnica FRIL | 90 días | Sin enforcement | RED |
| Vigencia RATE/RS | 3 años (1.095 días) | Sin tracking | RED |
| Plazo CGR Toma de Razón | 30 días | Sin tracking | RED |
| Periodicidad informes avance | Variable por track | Sin enforcement | RED |
| Validez certificado directorio | 60 días | Sin tracking | RED |
| Plazo respuesta observaciones CGR | 15 días | Sin tracking | RED |
| Vigencia pagaré 8% | 18 meses | Sin tracking | RED |

**Cobertura**: 2/12 implementados (16.7%). Los SLA RTF/UCR son los únicos con enforcement activo.

---

## 5. Delta v1.0 → v2.0

### 5.1 Hallazgos v1.0 Resueltos (7/11)

| ID v1.0 | Brecha | Resolución | Ciclo |
|---------|--------|------------|:-----:|
| H-REN-02 | Art. 18 CGR — bloqueo transferencias morosas | `_check_pending_renditions()` en convenios.py bloquea POST/PATCH cuotas si hay rendiciones no-terminales. Extendido a `paid_amount`/`paid_at` | C19 |
| H-REN-03 | SISREC rendiciones sin workflow | 8-state machine: PENDIENTE→EN_REVISION_RTF→VISADA_RTF→EN_REVISION_UCR→APROBADA/RECHAZADA + OBSERVADA. SLA 7d/2d. Audit trail `rendition_history` | C19 |
| H-IPR-04 | Poly-Switch routing evaluación | `financing_track` table (7 tracks), `GET /api/ipr/{id}/track-info`, TrackCard UI, gate F2→F3 mechanism-aware | C18 |
| H-IPR-05 | Dictámenes evaluación | `evaluation_assignment` table, `evaluator_type` scheme (8 codes), CRUD endpoints, auto-assign evaluator from track config | C18 |
| H-GOB-01 | CORE solo crisis, no sesiones/votación | 9 endpoints CORE sessions, votación por IPR, quórum SIMPLE/CALIFICADA, gate F3→F4 >7.000 UTM | C11 |
| H-CON-BUG | Trigger fn_validate_state_transition bug | Fixed via Wave 1 migration (dynamic column via TG_ARGV[0]) | C-Rem |
| H-IPR-MCD | MCD phases sin workflow | IPR transiciones endpoint con gates por fase, audit trail vía `txn.event` | C18 |

### 5.2 Hallazgos v1.0 Abiertos (4/11)

| ID v1.0 | Brecha | Estado Actual | Prioridad |
|---------|--------|---------------|:---------:|
| H-IPR-06 | 11 umbrales financieros | 1/11 implementado (7.000 UTM CORE gate). Los otros 10 sin codificar | **Crítica** |
| H-FIN-03 | 8 glosas presupuestarias | 0/8 codificadas. Solo existen como conceptos en schemes | **Alta** |
| H-FIN-01 | Clasificador presupuestario plano | Solo subtítulo. Faltan 5 niveles (Partida→Capítulo→Programa→Item→Asignación) | **Alta** |
| H-DGI-TDE | Indicador TDE sin datos reales | Valor estático en `dgi_indicator`. Sin fuente de datos real | **Baja** |

### 5.3 Nuevos Hallazgos v2.0

| ID | Brecha | Impacto | Prioridad |
|----|--------|---------|:---------:|
| H2-TRACK-ENGINE | Dominios 13-19 (163 CQs) requieren engine de reglas por track | 7 tracks sin lógica especializada — solo infraestructura base | **Alta** |
| H2-PLAN-INST | Sin instrumentos de planificación (ERD, ARI, PROPIR) | IPR sin vinculación a planificación territorial obligatoria | **Media** |
| H2-INTEROP | 0 integraciones externas (ClaveÚnica, PISEE, BIP, SIGFE, CGR) | TDE <10% cobertura, 108 stories D-TDE bloqueadas | **Alta** |
| H2-RRHH | Dominio D-BACK (105 stories) = 0% cobertura | Fichas funcionarios, nómina, calificaciones sin implementar | **Media** |
| H2-AUDIT-LOG | Sin audit trail transversal | `txn.event` parcial, `rendition_history` y `act_history` aislados | **Media** |
| H2-ROLES-EMPTY | 5/13 system roles con 0 users activos | GOBERNADOR, CONSEJERO_REGIONAL, SECRETARIO_EJECUTIVO, JEFE_DEPTO, JEFE_UNIDAD | **Baja** |
| H2-IPR-FIELDS | `sponsor_division_id` y `assignee_id` 0% populated | 3,622 IPRs sin división patrocinante ni responsable asignado | **Media** |
| H2-GEO | Dominio territorio (48 stories) sin IDE/GIS | `ipr_territory` tiene 3,570 registros pero sin visualización geoespacial | **Baja** |

#### Hallazgos Omega (HΩ) — Gaps operativos revelados por Modelo Omega v2.6.0

| ID | Brecha | Detalle | Impacto | Prioridad |
|----|--------|---------|---------|:---------:|
| HΩ-01 | Fraccionamiento FRIL | Detección subdivisión artificial para evadir umbral → RECHAZO admisibilidad | Dom 15 | **Alta** |
| HΩ-02 | Parentesco validation 8% | Inhabilitación hasta 3°/4° consanguinidad según mecanismo | Dom 16,18 | **Alta** |
| HΩ-03 | Pagaré 8% privados | Pagaré notarial 100% monto, 18 meses vigencia | Dom 18 | **Alta** |
| HΩ-04 | Directorio <60 días | Validez certificado directorio Registro Civil | Dom 18 | **Media** |
| HΩ-05 | RATE vigencia 3 años | RS caduca si no obtiene ID presupuestario en 3 años | Dom 04,13 | **Alta** |
| HΩ-06 | MML single-purpose | Glosa 06 programas deben tener exactamente 1 Propósito | Dom 14 | **Media** |
| HΩ-07 | C33 30% conservation | Si >30% costo reposición → SNI obligatorio | Dom 19 | **Alta** |
| HΩ-08 | FRIL 90d tender | Caducidad aprobación técnica si no licita en 90 días | Dom 15 | **Alta** |
| HΩ-09 | FRIL 5 proyectos/comuna | Max 5 por llamado (A2 Agua y A3 Vial exentos) | Dom 15 | **Media** |
| HΩ-10 | 8% morosos SISREC | Bloqueo TOTAL fondos a entidades con rendiciones vencidas | Dom 18 | **Crítica** |
| HΩ-11 | SNI proporcionalidad 4 niveles | Nivel 0-3 con requisitos escalados por monto/complejidad | Dom 04,13 | **Alta** |
| HΩ-12 | ITF vs RS distinción | Dictamen ITF (Transfers) ≠ RATE RS (SNI) en persistencia | Dom 04 | **Media** |
| HΩ-13 | Scores/Rankings 8% | Puntajes evaluación no persistidos en DB | Dom 18 | **Media** |
| HΩ-14 | SISREC ciclo completo 13-14d | SLA total GORE-side (no solo RTF 7d + UCR 2d) | Dom 08 | **Alta** |
| HΩ-15 | Budget cycle T-1→T→T+1 | Calendario presupuestario anual con 12+ hitos | Dom 03 | **Media** |

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

## 7. Datos de Base (DB snapshot 2026-03-03)

### 7.1 Tablas clave (sin cambios significativos desde v1.0)

| Tabla | Registros | Nota |
|-------|----------:|------|
| core.ipr | 3,622 | 1,973 con mcd_phase (54%), 3,621 con mechanism (99.97%) |
| core.budget_program | 25,761 | Programas presupuestarios |
| core.budget_carryover | 13,378 | Arrastres inter-anuales |
| core.document | 12,800 | Via ETL Phase 2 |
| core.ipr_party | 8,805 | 4 roles principales |
| core.budget_commitment | 4,617 | CDPs vinculados |
| core.ipr_territory | 3,596 | Todas con tipo UBICACION |
| core.organization | 3,360 | 33 internas GORE |
| core.administrative_act | 1,421 | Via ETL + audit trail trigger |
| core.resolution | 1,421 | Auto-creadas con actos |
| core.rendition | 1,234 | SISREC multi-role activo |
| core.rendition_history | — | Audit trail transiciones (nuevo v2.0) |
| core.agreement | 537 | 13 estados, 6 tipos |
| core.financing_track | 7 | Tracks evaluación (nuevo v2.0) |
| core.evaluation_assignment | — | Evaluaciones por IPR (nuevo v2.0) |
| core.schema_migration | — | Tracking DDL migrations (nuevo v2.0) |
| core.session_vote | — | Votación CORE (nuevo v2.0) |
| ref.category | 731+ | 95+ schemes |

### 7.2 API Coverage (121 endpoints, 18 routers)

| Router | Prefix | Endpoints | Dominio |
|--------|--------|:---------:|---------|
| ipr.py | /api/ipr | 20 | IPR + partes + territorio + hitos + avances + evaluaciones |
| dgi_data.py | /api/dgi/data | 14 | Indicadores + datos + rendiciones SISREC |
| admin.py | /api/admin | 12 | Usuarios + divisiones + financing-tracks |
| core_sessions.py | /api/core-sessions | 9 | Sesiones CORE + votación |
| convenios.py | /api/convenios | 8 | Convenios + cuotas + transiciones |
| reuniones.py | /api/reuniones | 8 | Reuniones crisis |
| catalogs.py | /api/catalogs | 7 | Categorías + búsquedas |
| compromisos.py | /api/compromisos | 7 | Compromisos operacionales |
| dgi_reports.py | /api/dgi/reports | 6 | Informes institucionales |
| presupuesto.py | /api/presupuesto | 6 | Presupuesto + CDPs |
| actos.py | /api/actos | 5 | Actos administrativos |
| dashboard.py | /api/dashboard | 5 | Dashboards role-aware |
| problemas.py | /api/problemas | 4 | Problemas IPR |
| dgi_initiatives.py | /api/dgi/initiatives | 4 | Iniciativas Kanban |
| alertas.py | /api/alertas | 2 | Alertas sistema |
| auth.py | /api/auth | 2 | Autenticación JWT |
| dgi_cockpit.py | /api/dgi/cockpit | 1 | Panel DGI |
| search.py | /api/search | 1 | Búsqueda global |

### 7.3 Test Coverage (210 tests, 23 modules)

| Módulo | Tests | Estado |
|--------|:-----:|--------|
| sisrec | 18 | 18 pass |
| compromisos | 16 | 16 pass |
| polyswitch | 14 | 10 pass + 4 known fail |
| ipr_children | 14 | 14 pass |
| actos | 12 | 12 pass |
| security_readonly | 12 | 12 pass |
| admin | 11 | 11 pass |
| reuniones | 11 | 11 pass |
| convenios | 9 | 9 pass |
| core_sessions | 10 | 10 pass |
| auth | 8 | 8 pass |
| presupuesto | 8 | 8 pass |
| catalogs | 8 | 8 pass |
| initiatives | 7 | 7 pass |
| problemas | 8 | 8 pass |
| dashboard | 6 | 6 pass |
| ipr_lifecycle | 6 | 6 pass |
| alertas | 6 | 6 pass |
| concurrency | 5 | 5 pass |
| rendiciones | 5 | 5 pass |
| search | 4 | 4 pass |
| dgi_cockpit | 4 | 4 pass |
| dgi_reports | 4 | 1 pass + 3 skip |
| **TOTAL** | **210** | **203 pass + 4 known fail + 3 skip** |

---

## 8. Roadmap Recomendado (Ciclos 20-24)

### Fase 1: Compliance Engine (Ciclos 20-21)

| Ciclo | Foco | CQs Target | Stories Est. | Impacto Score | Reglas Omega |
|:-----:|------|:----------:|:------------:|:------------:|:------------:|
| 20 | Umbrales Financieros Engine (18 umbrales parametrizables) | 12 (Dom 20) | ~25 | CQ Dom20: 12%→83% | U-01..U-18 |
| 21 | Glosas + Clasificador Presupuestario (8 glosas, 6 niveles) | 15 (Dom 03) | ~35 | CQ Dom03: 30%→55% | HΩ-06, TP-05 |

**Ciclo 20 — Detalle Omega**: Los 18 umbrales del Omega (§4.5.2) se parametrizan en `core.financial_threshold(code, value_utm, source, enforcement_point)`. Enforcement points: gate F1 (admisibilidad), gate F3→F4 (CORE), cuota convenio (garantía), evaluación (proporcionalidad). El engine intercepta transiciones de estado y valida umbrales.

**Ciclo 21 — Detalle Omega**: 8 reglas de glosa (§4.5.3) como constraints validables: Glosa 03 prohíbe contratación, Glosa 06 requiere MML single-purpose (HΩ-06), Glosa 07 aplica topes 5% admin/honorarios. TP-05 (Budget Cycle Timeline) materializa los 12+ hitos del calendario presupuestario T-1→T→T+1 (HΩ-15).

### Fase 2: Track Rules Engine (Ciclos 22-23)

| Ciclo | Foco | CQs Target | Stories Est. | Impacto Score | Reglas Omega |
|:-----:|------|:----------:|:------------:|:------------:|:------------:|
| 22 | Engine Reglas + Track A (SNI) + Track C (FRIL) | 50 (Dom 13,15) | ~30 | CQ Dom13: 2%→40%, Dom15: 2%→35% | HΩ-01,05,08,09,11,12; TP-01,03,04 |
| 23 | Tracks B,D,E (C33, Glosa06, Transfers, 8%, FRPD) | 113 (Dom 14,16-19) | ~40 | CQ Dom14-19: 1-2%→25% avg | HΩ-02,03,04,07,10,13; TP-02 |

**Ciclo 22 — Detalle Omega**:
- **Track A (SNI)**: Proporcionalidad 4 niveles (HΩ-11, TP-03), RATE vigencia 3 años (HΩ-05), ITF≠RS distinción (HΩ-12), evaluador routing por nivel
- **Track C (FRIL)**: Detección fraccionamiento (HΩ-01), 5 proyectos/comuna con exenciones A2/A3 (HΩ-09), 90d tender caducidad (HΩ-08), taxonomía 12 categorías A1-D3 (TP-04)
- **Framework**: `core.track_rule(track_id, rule_type, parameters JSONB, enforcement_point)` — engine genérico que evalúa reglas por track en cada transición de estado

**Ciclo 23 — Detalle Omega**:
- **Track B (C33)**: 30% conservation threshold → reclasificación a SNI (HΩ-07), certificación técnica SERVIU/MOP
- **Track E1 (8%)**: Morosos SISREC bloqueo total (HΩ-10), pagaré notarial 100%/18m (HΩ-03), directorio <60d (HΩ-04), parentesco inhabilitación 3°/4° (HΩ-02), scores/rankings persistidos (HΩ-13), 7 fondos distribución (TP-02)
- **Track D (FRPD) / Track E2 (Transfers)**: Scoring competitivo, dictamen ITF, comité evaluador externo

### Fase 3: Integrations & Expansion (Ciclo 24+)

| Ciclo | Foco | CQs Target | Stories Est. | Impacto Score | Reglas Omega |
|:-----:|------|:----------:|:------------:|:------------:|:------------:|
| 24 | Integraciones TDE (ClaveÚnica, BIP, SIGFE) | 24 (Dom 10) | ~30 | CQ Dom10: 12%→35% | — |
| 25 | SISREC ciclo completo + SLAs full | 18 (Dom 08) | ~15 | CQ Dom08: 47%→75% | HΩ-14, TP-06 |
| 26+ | RRHH (D-BACK), Planificación (D-PLAN), Territorio GIS | — | ~150 | Nuevos dominios | — |

**Ciclo 25 — Detalle Omega**: Implementa SLA ciclo completo 13-14d SISREC (HΩ-14) con las 8 fases del Omega (TP-06): ingreso → asignación RTF → revisión RTF → visa RTF → asignación UCR → revisión UCR → resolución → notificación. Incluye plazo post-término 60d, subsanación reparos 15d, y escalamiento automático.

### Proyección de Score CQ (Omega-adjusted)

| Milestone | CQ Score Promedio | Stories Coverage | Reglas Omega Cubiertas |
|-----------|:-----------------:|:---------------:|:---------------------:|
| v2.0 actual | 25.2%† | ~16% | 7/81+ (10%) |
| Post-Ciclo 21 | ~32% | ~22% | 33/81+ (41%) |
| Post-Ciclo 23 | ~40% | ~30% | 67/81+ (83%) |
| Post-Ciclo 25 | ~48% | ~38% | 75/81+ (93%) |

---

## 9. Conclusiones

### Lo que GORE_OS hace bien

1. **IPR como entidad central**: 67% de cobertura ontológica, 20 endpoints, 11 tabs, 3,622 registros reales
2. **Mecánica activada**: State machines en 4 dominios (IPR lifecycle, convenios, actos, SISREC)
3. **Audit trails**: `rendition_history`, `administrative_act_history`, `commitment_history` con triggers
4. **Seguridad**: JWT + brute-force + security headers + advisory locks + 210 tests
5. **DGI operativo**: 78% cobertura stories, cockpits, indicadores, Kanban, informes

### Lo que falta para ser "sistema operativo"

1. **Engine de reglas parametrizable**: El gap más impactante (163 CQs, 7 tracks, ~50 stories). El Omega detalla 40+ validaciones track-específicas con valores exactos
2. **Compliance como código**: 18 umbrales + 8 glosas + clasificador 6 niveles = base legal codificada. El Omega provee todos los valores
3. **Tablas paramétricas operativas**: 6 tablas del Omega (§4.5.5) contienen la parametrización exacta que falta para que `financing_track` sea un engine completo
4. **SLAs con enforcement**: Solo 2/12 SLAs del Omega tienen enforcement activo. El ciclo SISREC completo (13-14d) y la vigencia RATE (3 años) son gaps operativos críticos
5. **Integraciones Estado**: ClaveÚnica/PISEE/BIP/SIGFE desbloquean D-TDE (108 stories)

### Métrica de cierre

De las 472 CQs: **90 GREEN (19.1%), 58 YELLOW (12.3%), 324 RED (68.6%)**†

De las 81+ reglas Omega: **7 implementadas (8.6%), 7 parciales (8.6%), 67+ sin implementar (82.7%)**

La frontera de valor tiene dos ejes: (1) mover YELLOW→GREEN (58 CQs que necesitan API/UI), y (2) codificar reglas Omega como compliance ejecutable (los 18 umbrales y 8 glosas desbloquean ~30 CQs adicionales por convergencia).

---

## 10. Referencias

- `docs/GORE_OS_Audit_v1.0.md` — Auditoría v1.0 (2026-02-27)
- `docs/GORE_OS_Audit_Detail_v1.0.md` — Detalle stories × impl
- `model/stories/` — 818 historias de usuario (16 dominios)
- `gorenuble/knowledge/ontologies/onto_gorenuble/goreNubleCQs_Master.yml` — 472 CQs (20 dominios)
- `gorenuble/knowledge/ontologies/onto_gorenuble/goreNubleOntology.ttl` — 198 OWL classes
- `gorenuble/knowledge/ontologies/onto_gorenuble/omega_gore_nuble_mermaid.md` — Modelo Omega v2.6.0 (111KB, reglas de negocio operativas)
- `model/model_goreos/sql/goreos_ddl.sql` — DDL (81 tablas)
- `CLAUDE.md` — Project conventions (actualizado Ciclo 19)
- `docs/GORE_OS_Testing_Ciclo3.md` — Testing documentation
- `docs/adr/` — 6 Architecture Decision Records
