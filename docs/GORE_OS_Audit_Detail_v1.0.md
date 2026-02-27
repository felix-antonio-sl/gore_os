# GORE_OS Auditoría Detallada v1.0

> **Fecha**: 2026-02-27
> **Complemento de**: `docs/GORE_OS_Audit_v1.0.md` (documento ejecutivo)
> **Metodología**: Cruce exhaustivo de 4 fuentes de verdad contra implementación actual

---

## 1. Inventario de Historias de Usuario vs Implementación

### 1.1 Resumen general

- **Total**: 819 historias en `model/stories/` distribuidas en 502 dominios temáticos
- **Con cobertura parcial+**: ~79 historias (~10%)
- **Sin cobertura**: ~740 historias (~90%)
- **Dominios con algo implementado**: 6 de 16 macro-dominios (37%)

### 1.2 Dominios temáticos principales

Las 819 historias se agrupan en 16 macro-dominios según prefijo. El inventario a continuación muestra cobertura estimada por cada uno.

#### D-EJEC: Ejecución IPR (113 stories)

| Sub-dominio | Stories | Cobertura | Detalle |
|-------------|:-------:|:---------:|---------|
| ejec_ar (Admin Regional) | 5 | ~40% | Dashboard ejecutivo, list IPR — falta lifecycle completo |
| ejec_muni (Municipal) | 5 | ~10% | Solo ipr_territory data — falta interop municipal |
| ejec_eo (Encargado Ops) | 5 | ~30% | Compromisos CRUD, mis-compromisos — falta workflow completo |
| ejec_jd (Jefe División) | 3 | ~30% | Mi-división dashboard — falta carga equipo, delegación |
| fin_ipr (Finanzas IPR) | 17 | ~20% | CDPs por IPR — falta devengo, rendiciones, conciliación |
| Otros ejec_* | ~78 | ~5% | Evaluación, admisibilidad, priorización CORE: no implementados |

**Lo implementado**: CRUD IPR (create/read/update), 9 tabs detail (compromisos, problemas, alertas, convenios, CDPs, avances, partes, territorio, hitos), list con paginación + filtros, inline satellite creation, cross-entity navigation.

**Lo que falta**: Lifecycle MCD activo (F0→F5 con gates), evaluación técnica (Poly-Switch routing), dictámenes (RS, ITF, RF, AT), admisibilidad sub-estados, priorización CORE (votación), cierre formal con validaciones.

#### D-FIN: Finanzas (97 stories)

| Sub-dominio | Stories | Cobertura | Detalle |
|-------------|:-------:|:---------:|---------|
| fin_ppto (Presupuesto) | 16 | ~25% | List+detail+create+update, resumen por división — falta clasificador 6 niveles |
| fin_ipr (Finanzas IPR) | 17 | ~20% | CDPs endpoint — falta lifecycle financiero completo |
| fin_rend (Rendiciones) | 4 | ~5% | Data estática ETL — falta SISREC workflow, Art. 18 |
| fin_sub (Subtítulos) | 5 | ~10% | budget_subtitle scheme — falta drill-down jerárquico |
| fin_ppr | 4 | 0% | No implementado |
| fin_gest (Gestión) | 3 | ~10% | Ejecución parcial |
| fin_form (Formulación) | 3 | 0% | No implementado |
| fin_frpd (FRPD) | 3 | 0% | No implementado |
| fin_c33 (Circular 33) | 3 | 0% | No implementado |
| fin_jef (Jefatura) | 3 | ~10% | Dashboard financiero parcial |
| back_tes (Tesorería) | 12 | 0% | No implementado |
| Otros fin_* | ~24 | 0% | Devengo, glosas, conciliación SIGFE |

**Lo implementado**: Budget programs list+detail+CRUD, resumen agregado por división/subtítulo, CDPs por IPR, budget commitments, carryovers (13,378 registros).

**Lo que falta**: Clasificador presupuestario 6 niveles (Partida→Capítulo→Programa→Subtítulo→Item→Asignación), 8 glosas como reglas de gasto, devengo/devengado tracking, tesorería, conciliación SIGFE, SISREC transaccional.

#### D-TDE: Transformación Digital (108 stories)

| Sub-dominio | Stories | Cobertura | Detalle |
|-------------|:-------:|:---------:|---------|
| tde_auth (Autenticación) | 6 | ~50% | JWT login, change password — falta ClaveÚnica, MFA |
| tde_admin (Administración) | 6 | ~40% | Admin usuarios + divisiones — falta audit log |
| tde_seg (Seguridad) | 11 | ~5% | Solo HTTPS infra — falta IAM, SAST, pentest |
| tde_notif (Notificaciones) | 6 | ~15% | Bell notifications — falta email, SMS, push |
| tde_interop (Interoperabilidad) | 6 | 0% | PISEE, SII, CGR: no implementados |
| tde_dpo (Datos Personales) | 5 | 0% | RGPD/Ley 19.628: no implementado |
| tde_muni (Municipal) | 3 | 0% | Portal municipal: no implementado |
| Otros tde_* | ~65 | 0% | DS7 compliance, FEA, GobDigital |

**Lo implementado**: Auth JWT con roles, admin CRUD usuarios/divisiones, global search (Cmd+K), bell notifications.

**Lo que falta**: ClaveÚnica SSO, PISEE interoperabilidad, DS7 compliance, FEA (firma electrónica avanzada), portal municipal, IAM robusto, audit trail completo.

#### D-GOB: Gobernanza (62 stories)

| Sub-dominio | Stories | Cobertura | Detalle |
|-------------|:-------:|:---------:|---------|
| gob_core (CORE) | 5 | ~10% | Tablas existen — solo crisis_meetings implementado |
| gob_gr (Gobierno Regional) | 7 | ~10% | Dashboard role-based — falta workflows gobernador |
| gob_gab (Gabinete) | 5 | 0% | No implementado |
| gob_grd (Gestión Riesgos) | 4 | 0% | No implementado |
| gob_desc (Descentralización) | 4 | 0% | No implementado |
| gob_del (Delegaciones) | 3 | 0% | No implementado |
| Otros gob_* | ~34 | 0% | CDR, COSOC, fiscalización |

**Lo implementado**: Crisis meetings module (CRUD sesiones crisis, auto-suggestions, BIP badges), dashboards role-aware (4 variantes).

**Lo que falta**: Sesiones CORE ordinarias/extraordinarias, votación IPR (quorum simple 9/16, calificado 11/16), certificados CORE, Gobernador como actor (firma, preside, aprueba), CDR, COSOC.

#### D-GESTION: Gestión Institucional DGI (23 stories)

| Sub-dominio | Stories | Cobertura | Detalle |
|-------------|:-------:|:---------:|---------|
| gest_pb (Procesos BPM) | 3 | ~60% | BPMN model tracking en DGI |
| Cockpit DGI | ~5 | ~90% | 4 cockpits role-aware |
| Indicadores | ~5 | ~80% | 5 dimensiones semáforo, refresh desde DB |
| Iniciativas | ~5 | ~85% | Kanban completo, WIP limits, CRUD |
| Informes | ~5 | ~70% | 4 tipos, 6 secciones auto-populated |

**Lo implementado**: Cockpits DGI (4 variantes por rol), indicadores semáforo (5 dimensiones, refresh real), iniciativas Kanban (WIP limits, move con 409), informes institucionales (FLASH/SEMANAL/MENSUAL/TEMATICO, 6 secciones, JSONB edits).

**Lo que falta**: Auditoría interna, control de gestión operativo, indicadores TDE con datos reales, data sources CRUD completo.

#### D-OPS: Operaciones IT (47 stories)

| Sub-dominio | Stories | Cobertura | Detalle |
|-------------|:-------:|:---------:|---------|
| ops_iam (IAM) | 5 | ~5% | Solo JWT auth básico |
| ops_mon (Monitoreo) | 4 | ~5% | Solo health endpoint |
| ops_sup (Soporte) | 4 | 0% | No implementado |
| ops_dat (Datos) | 4 | ~5% | ETL scripts existen |
| ops_bak (Backup) | 3 | 0% | No implementado |
| ops_cfg (Config) | 3 | ~10% | Docker Compose, env vars |
| ops_mig (Migraciones) | 3 | ~20% | SQL migrations manuales |
| Otros ops_* | ~21 | 0% | No implementados |

#### Dominios sin implementación (0%)

| Macro-dominio | Stories | Descripción |
|---------------|:-------:|-------------|
| D-BACK (RRHH/Backoffice) | 105 | Fichas funcionarios (`back_per` 8), tesorería (`back_tes` 12), bienestar (`back_bien` 11), activos fijos (`back_af` 3), abastecimiento (`back_abs` 3), + otros |
| D-NORM (Normativa/Legal) | 75 | Actos administrativos (`norm_acto` 8), control (`norm_ctrl` 3), transparencia, lobby, CGR, expedientes |
| D-TERR (Territorio/GIS) | 48 | IDE regional (`terr_ide` 3), planificación territorial, análisis, programas |
| D-DEV (DevOps) | 37 | CI/CD (`dev_cicd` 4), KODA (`dev_koda` 4), buenas prácticas (`dev_bp` 8), releases |
| D-PLAN (Planificación) | 33 | ERD, ARI, PROPIR, indicadores estratégicos, DIPLADE |
| D-SOC (Social) | 23 | Fondos concursables, poblaciones vulnerables, programas sociales |
| D-SEG (Seguridad/CIES) | 18 | SINAPRED (`seg_cies` 7), prevención (`seg_prev` 6), gobernanza seguridad |
| D-EVOL (Evolución) | 14 | Calidad, capacitación, mejora continua |
| D-FENIX (Recuperación) | 11 | Desastres, BCP, respuesta |
| D-ORG (Organización) | 4 | Lifecycle organizacional |

### 1.3 Historias gen_gestion_* (larga cola)

100+ historias con prefijo `gen_gestion_` representan stories específicas por unidad organizacional (ej: `gen_gestion_ucr_001`, `gen_gestion_dipir_001`). Estas historias describen las necesidades operativas de cada unidad dentro del GORE. Ninguna tiene implementación dedicada, aunque algunas se benefician del CRUD genérico existente.

---

## 2. Hallazgos de Confrontación — Estado con Evidencia

### 2.1 Resueltos (9/17 — 53%)

#### H-ORG-01: Jerarquía organizacional

**Estado**: RESUELTO

**Evidencia DB**:
- `parent_id` endofunctor en `core.organization`
- 3 niveles: GORE-NUBLE → 8 DIVISION → 6 DEPARTAMENTO → 8 UNIDAD
- 33 organizaciones internas GORE activas
- Migración: `goreos_migration_confrontacion.sql`

#### H-ORG-02: Organizaciones faltantes

**Estado**: RESUELTO

**Evidencia DB**:
- 3,308 organizaciones activas (de 3,360 totales)
- 12 de 14 org_types en uso
- +8 orgs nuevas, 16 reclasificadas, 6 soft-deleted en migración
- Distribución: 1,626 ORG_COMUNITARIA, 1,568 ONG, 46 MUNICIPALIDAD, 23 SERVICIO, etc.

#### H-ORG-05/06: Roles faltantes

**Estado**: RESUELTO

**Evidencia DB**:
- 13 system_roles definidos (antes 8)
- +5 roles: GOBERNADOR, CONSEJERO_REGIONAL, SECRETARIO_EJECUTIVO, JEFE_DEPARTAMENTO, JEFE_UNIDAD
- 9 users activos distribuidos en 8 roles
- 5 roles sin users: GOBERNADOR, CONSEJERO_REGIONAL, SECRETARIO_EJECUTIVO, JEFE_DEPARTAMENTO, JEFE_UNIDAD

#### H-CON-01: Estados convenio faltantes

**Estado**: RESUELTO

**Evidencia DB**:
- 13 agreement_states definidos (antes 10)
- +3 estados: EN_REVISION_FINANCIERA, VISADO_INTERNO, TDR_PENDIENTE
- 7/13 estados en uso (459 VIGENTE, 55 BORRADOR, 7 EN_REVISION_JURIDICA, etc.)
- 6 estados sin uso (pipeline nuevo aún no activado)

#### H-IPR-02: Mecanismos de financiamiento

**Estado**: RESUELTO

**Evidencia DB**:
- `mechanism` scheme con 7 codes
- 3,621/3,622 IPRs con mechanism_id (99.97%)
- Distribución: 1,648 SUBV8 (45.5%), 1,627 SNI (44.9%), 343 TRANSFER (9.5%), 3 FRPD
- 4 tracks sin IPRs asignadas: C33, FRIL, GLOSA06 (y 1 sin mecanismo)

#### H-IPR-03: Modelo canónico MCD F0-F5

**Estado**: RESUELTO (data estática)

**Evidencia DB**:
- `mcd_phase` scheme con 6 codes (F0-F5)
- 1,973/3,622 IPRs con mcd_phase_id (54.5%)
- Distribución: 1,831 F4 (50.6%), 141 F2, 1 F0, 0 en F1/F3/F5
- 1,649 IPRs sin fase (45.5%) — requieren clasificación
- **Nota**: Fases son datos del seed, no resultado de workflow activo

#### H-CON-03: Actos administrativos

**Estado**: RESUELTO (data estática)

**Evidencia DB**:
- `core.administrative_act`: 1,421 registros
- `core.resolution`: 1,421 registros (1:1 con admin_act)
- Cargados via ETL Phase 2C
- **Nota**: Sin workflow de aprobación, solo data

#### H-FIN-06: Modificaciones presupuestarias

**Estado**: RESUELTO

**Evidencia DB**:
- 456 `txn.event` tipo MODIFICACION (ETL Phase 5)
- 4,251 eventos totales en txn.event (7 tipos)
- Incluye: Rendicion 8% (1,667), Aprobacion (830), Modificacion (456), Incorporacion (422), Creacion (420), Transicion (240), Asignacion (216)

#### H-GOB-01: CORE

**Estado**: PARCIAL

**Evidencia**:
- Tablas DDL existen: `core.committee`, `core.session`, `core.crisis_meeting`, `core.minute`, `core.session_agreement`
- 2 sesiones en DB (datos demo)
- Solo módulo crisis_meetings implementado (8 endpoints)
- **Falta**: Sesiones CORE ordinarias/extraordinarias, votación IPR, certificados

### 2.2 Abiertos (8/17 — 47%)

#### H-REN-02: Art. 18 Res. 30 CGR — Bloqueo transferencias

**Severidad**: CRITICA

**Estado**: NO IMPLEMENTADO

**Evidencia**:
- `convenios.py` POST cuotas: NO valida rendiciones pendientes del renderer
- 1,234 rendiciones, 100% en estado PENDIENTE
- `core.rendition.renderer_id` existe (FK a organization) pero no se consulta en flujo de cuotas
- **Riesgo**: GORE puede transferir fondos a entidades morosas, violando norma CGR

**Código afectado**: `api/app/routers/convenios.py` — endpoint `POST /api/convenios/{id}/cuotas`

#### H-IPR-04: Poly-Switch routing evaluación

**Severidad**: ALTA

**Estado**: NO IMPLEMENTADO

**Evidencia**:
- `mechanism_id` existe en 3,621 IPRs pero es solo dato descriptivo
- No hay lógica que derive: "si mechanism=SNI → evaluador=MDSF, timeline=45-90 días"
- No hay tabla `evaluation_assignment` ni `evaluation_track`

#### H-IPR-05: Dictámenes evaluación

**Severidad**: ALTA

**Estado**: NO IMPLEMENTADO

**Evidencia**:
- No existe tabla para dictámenes (RS, ITF, RF, AT)
- No hay workflow de evaluación
- No hay validez temporal (ej: RS caduca a 3 años)

#### H-IPR-06: 11 umbrales financieros

**Severidad**: ALTA

**Estado**: NO IMPLEMENTADO

**Evidencia**:
- 0 de 11 umbrales codificados como reglas de negocio
- No hay tabla `financial_threshold` ni validaciones en endpoints
- Umbrales del Omega: 4.545 UTM (FRIL), 500 UTM (licitación estudios), 1.000 UTM (licitación obras), 2.500 UTM (CGR TdR), 7.000 UTM (CORE), 15.000 UTM (SNI), 5% (admin Glosa 06), 5% (honorarios), 10% (asignación directa 8%), 20% (ANF C33), 30% (remuneraciones FRPD)

#### H-FIN-03: 8 glosas presupuestarias

**Severidad**: ALTA

**Estado**: NO IMPLEMENTADO

**Evidencia**:
- No hay reglas de gasto codificadas
- Glosas del Omega: 03 (no préstamos), 06 (tope 5% admin), 07 (tope 10%), 12, 13
- `budget_item` scheme tiene 14 codes pero sin validaciones asociadas

#### H-GOB-02: Gobernador como actor

**Severidad**: MEDIA

**Estado**: NO IMPLEMENTADO (parcial)

**Evidencia**:
- Role `GOBERNADOR` existe en `meta.system_role`
- 0 users con role GOBERNADOR
- No hay workflows específicos: firma actos, preside CORE, aprueba inversiones ≤7k UTM
- No hay test user para GOBERNADOR

#### H-FIN-01: Clasificador presupuestario

**Severidad**: MEDIA

**Estado**: PARCIAL

**Evidencia**:
- Solo `budget_subtitle` scheme (8 codes) modelado
- Faltan 5 niveles: Partida → Capítulo → Programa → Subtítulo → Item → Asignación
- CSVs de modificaciones (Phase 5) contienen SUBT/ITEM/ASIG pero se almacenan flat

#### H-REN-03: Ciclo SISREC

**Severidad**: MEDIA

**Estado**: NO IMPLEMENTADO

**Evidencia**:
- 1,234 rendiciones como data estática (100% PENDIENTE)
- No hay workflow transaccional: Ingreso → Revisión RTF → Aprobación UCR → Conciliación CGR → SIGFE
- No hay endpoints para cambiar estado de rendición
- Los 8 actores del Omega (Analista Ejecutor → SIGFE) no están modelados

---

## 3. Disciplinas Ontológicas vs Schema DDL + API + UI

### 3.1 Infraestructura Sistema (95%)

| Componente ontológico | Tabla/Entidad DDL | Endpoint API | Página UI |
|-----------------------|-------------------|-------------|-----------|
| Autenticación | core."user", meta.system_role | POST /api/auth/login, /change-password | /login |
| Autorización (RBAC) | system_role (13 roles) | CurrentUser dependency | Sidebar condicional |
| Base de datos | 78 tablas, 4 schemas | SQLAlchemy async + asyncpg | — |
| API REST | — | 102 endpoints, FastAPI | — |
| Frontend SPA | — | — | Next.js 16, 25 pages |
| Containerización | docker-compose.yml | health check | — |
| Test suite | goreos_test DB | 86 tests, pytest | — |

**Brecha**: IAM robusto, audit trail, backup automatizado, monitoreo, CI/CD.

### 3.2 IPR — Inversión Pública Regional (40%)

| Componente ontológico | Tabla DDL | Endpoint API | Página UI |
|-----------------------|-----------|-------------|-----------|
| IPR entity (8 tipos) | core.ipr | GET/POST/PATCH /api/ipr | /ipr, /ipr/[id] |
| MCD phases (F0-F5) | ref.category (mcd_phase) | — (solo data) | — (no visible en UI) |
| Mechanisms (7 tracks) | ref.category (mechanism) | — (solo data) | — (no visible en UI) |
| Partes (9 roles) | core.ipr_party | GET/POST/DELETE /api/ipr/{id}/partes | Tab Partes |
| Territorio | core.ipr_territory | GET/POST/DELETE /api/ipr/{id}/territorio | Tab Territorio |
| Hitos (13 tipos) | core.ipr_milestone | GET/POST/PATCH /api/ipr/{id}/hitos | Tab Hitos |
| Avances | core.progress_report | GET/POST /api/ipr/{id}/avances | Tab Avances |
| Evaluación (Poly-Switch) | — | — | — |
| Dictámenes (RS/ITF/RF/AT) | — | — | — |
| Admisibilidad sub-estados | — | — | — |
| Priorización CORE | — | — | — |
| Lifecycle F0→F5 activo | — | — | — |

**Datos**: 3,622 IPRs, 8,805 parties, 3,596 territories, 0 milestones, 1 progress report.

### 3.3 Finanzas & Presupuesto (30%)

| Componente ontológico | Tabla DDL | Endpoint API | Página UI |
|-----------------------|-----------|-------------|-----------|
| Budget programs | core.budget_program | GET/POST/PATCH /api/presupuesto | /presupuesto |
| CDPs | core.budget_commitment | GET /api/presupuesto/cdps-por-ipr/{id} | Tab CDPs en IPR |
| Carryovers | core.budget_carryover | — (solo data) | — |
| Resumen por división | — | GET /api/presupuesto/resumen | Widget resumen |
| Clasificador 6 niveles | — | — | — |
| Glosas (8 reglas) | — | — | — |
| Devengo/devengado | — | — | — |
| Tesorería | — | — | — |
| Conciliación SIGFE | — | — | — |

**Datos**: 25,761 programs, 4,617 commitments, 13,378 carryovers.

### 3.4 Convenios & Actos Administrativos (35%)

| Componente ontológico | Tabla DDL | Endpoint API | Página UI |
|-----------------------|-----------|-------------|-----------|
| Agreements (13 estados) | core.agreement | GET/POST/PATCH /api/convenios | /convenios |
| Cuotas (installments) | core.agreement_installment | GET/POST/PATCH cuotas | Drawer inline |
| Transiciones estado | ref.category (agreement_state) | GET transiciones | Drawer actions |
| Actos administrativos | core.administrative_act | — (solo ETL data) | — |
| Resoluciones | core.resolution | — (solo ETL data) | — |
| Rendiciones | core.rendition | GET /api/dgi/data/rendiciones (read-only) | — |
| Workflow resolución 7-step | — | — | — |
| Art. 18 bloqueo | — | — | — |
| Boletas garantía | — | — | — |

**Datos**: 537 agreements, 1,421 resolutions, 1,234 renditions.

### 3.5 Gestión Institucional DGI (60%)

| Componente ontológico | Tabla DDL | Endpoint API | Página UI |
|-----------------------|-----------|-------------|-----------|
| Cockpit role-aware | — | GET /api/dgi/cockpit | /dashboard (DGI) |
| Indicadores semáforo | core.dgi_indicator | GET/POST /api/dgi/data/indicators | Panel indicadores |
| Iniciativas Kanban | core.dgi_initiative | GET/POST/PATCH/move | /dgi/iniciativas |
| Informes (4 tipos) | core.dgi_report | GET/POST/PATCH/export | /dgi/informes |
| Data sources | core.data_source_status | GET /api/dgi/data/sources | Panel fuentes |
| BPM models | core.bpmn_model | — (parcial) | — |
| Auditoría interna | — | — | — |
| Control gestión operativo | — | — | — |

### 3.6 Organización & Personas (25%)

| Componente ontológico | Tabla DDL | Endpoint API | Página UI |
|-----------------------|-----------|-------------|-----------|
| Organizaciones | core.organization (3,360) | GET /api/catalogs/organizations | ComboboxAsync |
| Jerarquía 3 niveles | parent_id endofunctor | GET /api/catalogs/divisions | Sidebar divisiones |
| Personas | core.person (121) | GET /api/dgi/data/personas | Panel DGI |
| Usuarios | core."user" (9) | GET/POST/PATCH /api/admin/usuarios | /admin/usuarios |
| Roles (13) | meta.system_role | — | Admin select |
| Ficha funcionario | — | — | — |
| RRHH (nómina, bienestar) | — | — | — |
| Calificaciones | — | — | — |
| Estamento | ref.category (estamento) | — | — (solo data) |

**Datos**: 3,308 orgs activas, 121 personas (110 con RUT, 8 con email), 9 users.

### 3.7 Gobernanza Regional (15%)

| Componente ontológico | Tabla DDL | Endpoint API | Página UI |
|-----------------------|-----------|-------------|-----------|
| Crisis meetings | core.crisis_meeting + session | 8 endpoints /api/reuniones | /reuniones |
| Committee | core.committee | — (auto-created) | — |
| Sesiones CORE | core.session (estructura) | — | — |
| Votación IPR | — | — | — |
| Certificados CORE | — | — | — |
| CDR | — | — | — |
| COSOC | — | — | — |
| Gobernador workflows | — | — | — |

### 3.8 Territorio & Geoespacial (10%)

| Componente ontológico | Tabla DDL | Endpoint API | Página UI |
|-----------------------|-----------|-------------|-----------|
| Territorios (25) | core.territory | GET /api/catalogs/territories | Tab Territorio IPR |
| IPR-Territory links | core.ipr_territory (3,596) | GET/POST/DELETE | Tab Territorio |
| IDE Regional | — | — | — |
| Capas GEO | — | — | — |
| Indicadores comunales | — | — | — |

### 3.9 Normativa & Legal (5%)

| Componente ontológico | Tabla DDL | Endpoint API |
|-----------------------|-----------|-------------|
| Resoluciones (data) | core.resolution (1,421) | — (solo ETL) |
| Actos admin (data) | core.administrative_act (1,421) | — (solo ETL) |
| Documentos (data) | core.document (12,800) | — (solo ETL) |
| Workflow resolución | — | — |
| Plantillas actos | — | — |
| Consulta precedentes | — | — |
| Transparencia | — | — |

### 3.10-3.12 Planificación, Seguridad, Social (0%)

Sin tablas DDL dedicadas, sin endpoints, sin UI. Requieren diseño desde cero.

---

## 4. Mapa de 102 Endpoints API vs Dominios Ontológicos

### Distribución por dominio

| Dominio ontológico | Endpoints | % del total |
|-------------------|:---------:|:-----------:|
| IPR (Inversión Pública) | 21 | 20.6% |
| Administración (usuarios/divisiones) | 9 | 8.8% |
| DGI Data (indicadores/fuentes) | 9 | 8.8% |
| Convenios (agreements/cuotas) | 8 | 7.8% |
| Reuniones (crisis meetings) | 8 | 7.8% |
| Catálogos (ref data) | 7 | 6.9% |
| Compromisos (work items) | 7 | 6.9% |
| Presupuesto (budget) | 6 | 5.9% |
| DGI Reports (informes) | 6 | 5.9% |
| Dashboard (visualización) | 5 | 4.9% |
| Problemas (issues) | 5 | 4.9% |
| DGI Initiatives (Kanban) | 4 | 3.9% |
| Alertas (warnings) | 2 | 2.0% |
| Auth (autenticación) | 2 | 2.0% |
| DGI Cockpit (panel) | 1 | 1.0% |
| Search (búsqueda global) | 1 | 1.0% |
| Health (infraestructura) | 1 | 1.0% |

### Endpoints por método HTTP

| Método | Count | Uso |
|--------|:-----:|-----|
| GET | 62 | Lectura (list, detail, search) |
| POST | 30 | Creación + acciones de estado |
| PATCH | 9 | Actualización parcial |
| DELETE | 1 | Eliminación (ipr_party/territory) |

### Dominios sin endpoints

- RRHH / Backoffice
- Normativa / Legal (workflow)
- Territorio / GIS
- Planificación (ERD/ARI/PROPIR)
- Social (fondos concursables)
- Seguridad / CIES
- Rendiciones (workflow — solo GET read-only)
- Actos administrativos (workflow — solo data ETL)

---

## 5. Insights del Modelo Omega v2.6.0

### 5.1 MCD Poly-Switch — Detalle de 7 tracks

El Omega define que en la fase F2 (Evaluación Técnica), el `mechanism_id` de la IPR determina:

| Track | Mechanism | Evaluador | Dictamen | Timeline | IPRs en DB |
|-------|-----------|-----------|----------|----------|:----------:|
| A | SNI General | MDSF | RS (Recomendación Satisfactoria) | 45-90 días | 1,627 |
| B | Circular 33 | MDSF/GORE | AD (Aprobación Directa) | 15-30 días | 0 |
| C | FRIL | GORE/DIPIR | AT (Aprobación Técnica) | 30-60 días | 0 |
| D1 | Glosa 06 | DIPRES/SES | RF (Resolución Favorable) | 60-120 días | 0 |
| D2 | Transferencias | GORE Comité | ITF (Informe Técnico Favorable) | 30-45 días | 343 |
| E1 | Subvención 8% | GORE Comisión | Puntaje/Ranking | 30-60 días | 1,648 |
| E2 | FRPD Royalty | ANID/CORFO | Elegibilidad | Variable | 3 |

**Observación**: 1,648 IPRs (45.5%) son Track E1 (Subvención 8%) que tiene su propio proceso interno GORE (comisión evaluadora + puntaje). 1,627 (44.9%) son Track A (SNI) que requiere evaluación externa MDSF.

### 5.2 SISREC — 8 actores, 2 fases

```
FASE EJECUTOR:
1. Analista Ejecutor → prepara rendición
2. Ministro de Fe → certifica documentos
3. Encargado Ejecutor → envía a GORE

FASE GORE:
4. RTF/Analista Otorgante → revisa (7 días hábiles)
5. Jefe DAF/Encargado Otorgante → visa
6. UCR → concilia (2 días hábiles)
7. Registro SIGFE
8. Conciliación CGR (trimestral)
```

**Estado actual**: Los 8 actores no están modelados. `core.rendition` solo tiene `renderer_id` (organizacion ejecutora) y `state_id` (100% PENDIENTE).

### 5.3 Flujo Resolución Exenta — 7 pasos

```
1. Unidad Competente → elabora borrador
2. Asesoría Jurídica → revisa legalidad
3. Unidad Control → verifica presupuesto + procedimiento
4. Jefatura División → visa técnicamente
5. Administrador Regional → visa administrativamente
6. Gobernador → firma (FEA Ley 21.180)
7. Notificación y Archivo → distribución + respaldo
```

**Estado actual**: 1,421 resoluciones en DB como datos planos. No existe `resolution_state` ni pipeline de aprobación.

### 5.4 Umbrales financieros — 11 reglas del Omega

Los umbrales están definidos en UTM (Unidad Tributaria Mensual) y porcentajes. Son reglas de negocio que deberían validarse en endpoints de creación/avance de IPR y en asignación presupuestaria.

**Ninguno está codificado** como validación en el backend actual.

### 5.5 Glosas presupuestarias — 8 reglas del Omega

| Glosa | Regla | Afecta a |
|-------|-------|----------|
| 03 | Prohibición de préstamos con fondos FNDR | budget_commitment |
| 06 | Tope 5% administración | budget_program |
| 07 | Tope 10% asignación directa | budget_commitment |
| 08 | Rendición 100% antes de nuevo desembolso | agreement_installment |
| 12 | Estudios requieren TdR aprobados | ipr (ESTUDIO type) |
| 13 | Aportes de capital solo con convenio vigente | budget_commitment |
| C33 | 20% cofinanciamiento municipal | agreement |
| FRPD | 30% tope remuneraciones | budget_program |

---

## 6. Brechas de Datos (requieren gestión humana)

| Brecha | Magnitud | Fuente necesaria |
|--------|----------|-----------------|
| Personas sin email | 113/121 (93%) | Planilla RRHH con emails institucionales |
| IPRs sin sponsor_division | 3,622/3,622 (100%) | Data harvest DIPIR |
| IPRs sin assignee | 3,622/3,622 (100%) | Data harvest DIPIR + divisiones sectoriales |
| IPRs sin MCD phase | 1,649/3,622 (46%) | Clasificación manual o reglas de inferencia |
| Convenios sin CGR outcome | ~407/537 (76%) | Harvest Jurídica |
| core.ipr_milestone | 0 registros | FRIL no tiene fechas; harvest DIPIR |
| Tracks sin IPRs (C33, FRIL, GLOSA06) | 0 IPRs en 3 tracks | Re-clasificación o data faltante |
| Agreement states sin uso (6/13) | 0 convenios | Pipeline nuevo no activado |
| Roles sin users (5/13) | 0 users | Creación de test users + producción |

---

## 7. Resumen de Capacidades del Sistema

### Lo que GORE_OS hace bien

1. **CRUD operativo completo** para 6 entidades core (IPR, convenios, presupuesto, compromisos, problemas, alertas)
2. **DGI management** con cockpits role-aware, indicadores semáforo, Kanban con WIP limits, informes auto-populated
3. **Cross-entity navigation** bidireccional (IPR ↔ satélites)
4. **Ontología materializada** en DDL (78 tablas) con data real (79K+ registros)
5. **ETL pipeline** completado (6 fases, 8 dominios CSV, idempotente)
6. **Test coverage** con 86 integration tests contra real PostgreSQL

### Lo que GORE_OS necesita

1. **Lifecycle activo**: Transiciones MCD F0→F5 con gates y audit trail
2. **Compliance CGR**: Art. 18 bloqueo transferencias, SISREC workflow
3. **Business rules**: 11 umbrales financieros, 8 glosas presupuestarias
4. **Workflows de aprobación**: Resolución exenta 7-step, CORE votación
5. **Poly-Switch routing**: Evaluación por mecanismo con dictámenes
6. **10 dominios nuevos**: RRHH, Legal, Territorio/GIS, Planificación, Social, Seguridad, DevOps, Evolución, Recuperación, Organización

---

## 8. Referencias

- `docs/GORE_OS_Audit_v1.0.md` — Documento ejecutivo de auditoría
- `model/stories/` — 819 historias de usuario (502 sub-dominios)
- `model/model_goreos/sql/goreos_ddl.sql` — DDL (78 tablas)
- `model/model_goreos/sql/goreos_seed.sql` — 78 category schemes
- `model/model_goreos/sql/goreos_migration_confrontacion.sql` — Migración confrontación
- `model/model_goreos/sql/goreos_migration_rendition_coproduct.sql` — Migración coproducto rendición
- `docs/ETL_ARCHITECTURE_v1.0.md` — Arquitectura ETL
- `docs/GORE_OS_Testing_Ciclo3.md` — Documentación de testing
- `architecture/Omega_GORE_OS_Definition_v3.0.0.md` — Especificación sistema
