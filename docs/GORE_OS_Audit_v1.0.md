# GORE_OS Auditoría Institucional v1.0

> **Fecha**: 2026-02-27
> **Alcance**: Estado actual de GORE_OS vs Fuentes de Verdad institucionales
> **Fuentes**: 819 historias de usuario, Ontología GORE Ñuble (472 CQs), Informe Confrontación v1.0, Modelo Omega v2.6.0

---

## 1. Resumen Ejecutivo

GORE_OS cubre **~30% del dominio institucional** documentado. El sistema funciona como **data warehouse operativo** — tiene la ontología correcta (MCD phases, mechanisms, admin acts, org hierarchy) materializada en DDL + data, pero carece de la **mecánica activa** (state machines, gates, validaciones, workflows) que lo convertiría en un verdadero "sistema operativo" institucional.

### Métricas top-line

| Métrica | Valor |
|---------|-------|
| Historias de usuario totales | 819 |
| Historias con cobertura (parcial+) | ~79 (10%) |
| Dominios con implementación | 6/16 (37%) |
| Hallazgos confrontación resueltos | 9/17 (53%) |
| Hallazgos confrontación abiertos | 8/17 (47%) |
| Cobertura ontológica estimada | ~30% |
| Tablas DDL | 78 (58 lógicas + 20 particiones txn) |
| Endpoints API | 102 |
| Tests integración | 86 |
| IPRs en DB | 3,622 |
| IPRs con MCD phase | 1,973 (54%) |
| IPRs con mechanism | 3,621 (99.97%) |
| Rendiciones materializadas | 1,234 (100% en estado PENDIENTE) |
| Organizaciones activas | 3,308 (33 internas GORE) |
| Registros totales tablas clave | ~79,183 |

---

## 2. Hallazgo Central: Ontología sin Mecánica

GORE_OS tiene:
- **DDL completo**: 78 tablas, 4 schemas (meta, ref, core, txn), partitioned txn
- **Data real**: 3,622 IPRs, 537 convenios, 8,805 ipr_party, 3,596 ipr_territory, 1,234 rendiciones, 1,421 resoluciones, 12,800 documentos, 25,761 budget programs, 13,378 budget carryovers
- **Ontología materializada**: `mcd_phase` (6 codes F0-F5), `mechanism` (7 tracks SNI→FRPD), `agreement_state` (13 estados), `system_role` (13 roles), org hierarchy (3 niveles), 78 category schemes con 731 códigos
- **Eventos transaccionales**: 4,251 txn.event (7 tipos: Rendicion 8%, Aprobacion, Modificacion, Incorporacion, Creacion, Transicion, Asignacion)

GORE_OS NO tiene:
- **State machines activas**: MCD phases son data estática, no hay transiciones con gates
- **Business rules**: 0 de 11 umbrales financieros codificados, 0 de 8 glosas validadas
- **Compliance CGR**: Art. 18 Res. 30 (bloqueo transferencias) NO implementado
- **Workflows de aprobación**: Resoluciones exentas sin pipeline 7-step, CORE sin votación
- **SISREC**: Rendiciones sin ciclo transaccional (Ingreso→RTF→UCR→SIGFE) — 100% en estado PENDIENTE

---

## 3. Brechas Priorizadas

### CRÍTICAS (riesgo legal)

| ID | Brecha | Impacto | Estado |
|----|--------|---------|--------|
| H-REN-02 | Art. 18 Res. 30 CGR — bloqueo transferencias a entidades morosas | Transferencias a entidades con rendiciones pendientes violan norma CGR | **NO IMPLEMENTADO** |
| H-CON-BUG | Trigger `fn_validate_state_transition` referencia `OLD.status_id` pero columna es `state_id` | Transiciones de estado en convenios no se validan correctamente | **BUG ACTIVO** (test xfail) |

### ALTAS (funcionalidad core faltante)

| ID | Brecha | Datos existentes | Falta |
|----|--------|-----------------|-------|
| H-IPR-04 | Poly-Switch routing evaluación | 3,621 IPRs con `mechanism_id` | Lógica de routing: qué evaluador, dictamen, timeline por mecanismo |
| H-IPR-05 | Dictámenes evaluación (RS, ITF, RF, AT) | — | Tabla, workflow, validez temporal (RS 3 años) |
| H-IPR-06 | 11 umbrales financieros | — | Validaciones: 7k UTM CORE, 2.5k UTM CGR, 4.5k UTM FRIL, etc. |
| H-FIN-03 | 8 glosas presupuestarias | — | Reglas de gasto: Glosa 03, 06, 07, 12, 13 |
| H-REN-03 | Ciclo SISREC rendiciones | 1,234 rendiciones data estática (100% PENDIENTE) | Workflow: Ingreso→RTF→UCR→SIGFE |
| H-IPR-MCD | MCD phases sin workflow | 1,973 IPRs con fase (54%), 1,649 sin fase (46%) | Transiciones F0→F5 con gates y audit trail |

### MEDIAS (mejoras significativas)

| ID | Brecha | Estado |
|----|--------|--------|
| H-GOB-01 | CORE solo crisis_meetings, no sesiones ordinarias/votación | PARCIAL — tablas existen, solo módulo crisis |
| H-GOB-02 | Gobernador sin workflows específicos | Role existe, 0 users activos |
| H-FIN-01 | Clasificador presupuestario plano (solo subtítulo) | Faltan 5 niveles |
| H-DGI-TDE | Indicador TDE sin datos reales | Valor estático |
| H-IPR-ASSIGN | IPRs sin assignee ni sponsor_division | 0% completitud en ambos campos |

---

## 4. Cobertura por Dominio de Historias de Usuario

### Implementados (parcial)

| Dominio | Stories | Cobertura | Lo que funciona | Lo que falta |
|---------|---------|-----------|-----------------|--------------|
| D-GESTION (DGI) | 23 | ~78% | Cockpits, indicadores, Kanban, informes | Auditoría interna, control gestión operativo |
| D-EJEC (Ejecución) | 113 | ~27% | CRUD IPR/convenios/CDPs/compromisos/problemas | Evaluación, admisibilidad, priorización CORE, lifecycle |
| D-FIN (Finanzas) | 97 | ~15% | Presupuesto list+detail, CDPs, ejecución parcial | Clasificador 6 niveles, devengo, glosas, tesorería |
| D-GOB (Gobernanza) | 62 | ~8% | Crisis meetings, dashboard role-based | Sesiones CORE, votación, acuerdos, fiscalización |
| D-TDE (Digital) | 108 | ~7% | Auth JWT, admin usuarios, ⌘K search | ClaveÚnica, PISEE, DS7, FEA |
| D-OPS (Operaciones) | 47 | ~6% | Health endpoint, Docker infra | IAM, monitoreo, backup |

### No implementados (0%)

| Dominio | Stories | Impacto potencial |
|---------|---------|-------------------|
| D-BACK (RRHH) | 105 | Fichas funcionarios, nómina, bienestar, calificaciones |
| D-NORM (Legal) | 75 | Plantillas actos, workflow resoluciones, consulta precedentes |
| D-TERR (Territorio) | 48 | IDE regional, capas GEO, indicadores territoriales |
| D-DEV (DevOps) | 37 | CI/CD, SAST, ADR |
| D-PLAN (Planificación) | 33 | ERD, ARI, PROPIR, indicadores estratégicos |
| D-SOC (Social) | 23 | Fondos concursables, poblaciones vulnerables |
| D-SEG (Seguridad) | 18 | SINAPRED, televigilancia, alertas ciudadanas |
| D-EVOL (Evolución) | 14 | Calidad, capacitación |
| D-FENIX (Recuperación) | 11 | Desastres, respuesta |
| D-ORG (Organización) | 4 | Lifecycle organizacional |

---

## 5. Cobertura por Disciplina Ontológica

| Disciplina | Cobertura | Brecha principal |
|------------|:---------:|-----------------|
| Infraestructura Sistema | **95%** | Auth, API, DB, Docker — bien cubierto |
| Gestión Institucional (DGI) | **60%** | Faltan: auditoría interna, control gestión operativo |
| IPR (Inversión Pública) | **40%** | CRUD OK. Faltan: lifecycle F0-F5, evaluación, dictámenes |
| Convenios & Actos | **35%** | 13 estados OK. Faltan: workflow 7-step, garantías, reglas mecanismo |
| Finanzas & Presupuesto | **30%** | Ejecución parcial. Faltan: clasificador, glosas, SISREC |
| Organización & Personas | **25%** | Jerarquía OK. Faltan: RRHH, fichas, calificaciones |
| Gobernanza Regional | **15%** | Crisis meetings. Faltan: CORE votación, CDR, COSOC |
| Territorio & Geoespacial | **10%** | ipr_territory data. Faltan: IDE, GIS, indicadores |
| Normativa & Legal | **5%** | Resoluciones data (ETL). Falta: workflow, plantillas |
| Planificación | **0%** | ERD, ARI, PROPIR no implementados |
| Seguridad & Emergencias | **0%** | SINAPRED, CIES no implementados |
| Desarrollo Social | **0%** | Fondos concursables no implementados |

---

## 6. Insights del Modelo Omega v2.6.0

### 6.1 MCD: Modelo Canónico de Estados

El Omega define 6 fases con un **Poly-Switch** en F2:

```
F0 Formulación → F1 Admisibilidad → F2 Evaluación (Poly-Switch 7 tracks) → F3 Priorización → F4 Ejecución → F5 Cierre
```

**Poly-Switch F2**: Según `mechanism_id`, la IPR se deriva a:
- Track A (SNI): evaluador MDSF → dictamen RS (45-90 días)
- Track B (C33): evaluador MDSF/GORE → dictamen AD (15-30 días)
- Track C (FRIL): evaluador GORE/DIPIR → dictamen AT (30-60 días)
- Track D1 (Glosa 06): evaluador DIPRES/SES → dictamen RF (60-120 días)
- Track D2 (Transferencias): evaluador GORE Comité → dictamen ITF (30-45 días)
- Track E1 (Subvención 8%): evaluador GORE Comisión → Puntaje/Ranking (30-60 días)
- Track E2 (FRPD): evaluador ANID/CORFO → Elegibilidad (variable)

**Estado actual**: GORE_OS tiene `mechanism_id` en 3,621/3,622 IPRs pero NO tiene la lógica de routing.

### 6.2 SISREC: Ciclo de Rendiciones

El Omega define 8 actores en 2 fases:

**Fase Ejecutor**: Analista Ejecutor → Ministro de Fe → Encargado Ejecutor
**Fase GORE**: RTF/Analista Otorgante (7 días) → Jefe DAF/Encargado Otorgante → UCR (2 días) → SIGFE

**Regla Art. 18 Res. 30 CGR**: "Prohibición de entregar nuevos fondos si hay rendiciones pendientes exigibles"

**Estado actual**: 1,234 rendiciones como data estática. 100% en estado PENDIENTE. Sin workflow, sin bloqueo Art. 18.

### 6.3 Flujo Resolución Exenta

7 pasos lineales:
```
Unidad Competente → Asesoría Jurídica → Unidad Control → Jefatura División → Administrador Regional → Gobernador (FEA) → Notificación y Archivo
```

**Estado actual**: 1,421 resoluciones cargadas via ETL Phase 2C. Sin workflow de aprobación.

### 6.4 Umbrales Financieros

| Umbral | Regla | Implementado |
|--------|-------|:------------:|
| < 4.545 UTM | Exención RS (FRIL Ñuble) | No |
| > 500 UTM | Licitación pública (estudios) | No |
| > 1.000 UTM | Licitación pública (obras) | No |
| > 2.500 UTM | CGR Toma de Razón | No |
| > 7.000 UTM | Aprobación CORE obligatoria | No |
| > 15.000 UTM | Evaluación SNI/MDSF | No |
| 5% | Tope admin Glosa 06 | No |
| 5% | Tope honorarios receptor | No |
| 10% | Tope asignación directa 8% | No |
| 20% | Cofinanciamiento ANF C33 | No |
| 30% | Tope remuneraciones FRPD | No |

---

## 7. Plan Integrado — Ciclo 9: Lifecycle & Compliance

### Concepto

Activar la mecánica sobre la ontología existente. 6 waves progresivas donde cada entrega habilita la siguiente.

### Wave 0: Documentación (este documento)

### Wave 1: Cimientos (2-3 días)
- Fix trigger `fn_validate_state_transition`
- Mostrar MCD phase + mechanism en IPR UI (list + detail)
- PATCH endpoint rendiciones (workflow básico)

### Wave 2: Art. 18 + Rendiciones SISREC (3-4 días)
- Bloqueo Art. 18 en cuotas convenio
- Dashboard rendiciones DGI
- Badge "Rendiciones Pendientes" en convenio drawer

### Wave 3: IPR Lifecycle Activo (5-7 días)
- State machine F0→F5 con gates
- `ipr_phase_history` audit trail
- Admisibilidad sub-estados (F1)
- UI timeline + botón "Avanzar Fase"

### Wave 4: Actos Administrativos Workflow (5-7 días)
- Router CRUD actos + resoluciones
- 7-step approval flow (Omega)
- UI página + drawer + timeline
- Link bidireccional IPR ↔ Resolución

### Wave 5: CORE Governance (3-5 días)
- Sesiones CORE ordinarias/extraordinarias
- Votación por IPR (quorum 9/16 simple, 11/16 calificado)
- Certificado CORE post-votación
- Gate: IPR >7,000 UTM requiere acuerdo CORE

### Dependencias
```
Wave 0 → Wave 1 → Wave 2 → Wave 3 → Wave 4 (parallelizable)
                                    → Wave 5 (requiere Wave 3)
```

### Estimación: ~20-25 días

---

## 8. Datos de Base (DB snapshot 2026-02-27)

### Tablas clave

| Tabla | Registros | Nota |
|-------|----------:|------|
| core.ipr | 3,622 | 1,973 con mcd_phase (54%), 3,621 con mechanism (99.97%) |
| core.budget_program | 25,761 | Programas presupuestarios por año/división |
| core.budget_carryover | 13,378 | Arrastres inter-anuales |
| core.document | 12,800 | Via ETL Phase 2 |
| core.ipr_party | 8,805 | +2,358 via ETL Phase 6 (FORMULADOR, UNIDAD_TECNICA) |
| core.budget_commitment | 4,617 | CDPs vinculados a IPR/convenios |
| core.ipr_territory | 3,596 | +26 via ETL Phases 4+6 |
| core.organization | 3,360 | 3,308 activas (33 internas GORE), 12 org_types en uso |
| core.administrative_act | 1,421 | Via ETL Phase 2C |
| core.resolution | 1,421 | Via ETL Phase 2C |
| core.rendition | 1,234 | Via ETL Phase 2C' (coproduct IPR). 100% PENDIENTE |
| core.agreement | 537 | 476 enriquecidos via ETL Phase 3. 7/13 estados en uso |
| core.person | 121 | 110 con RUT, 8 con email (93% sin email) |
| core.operational_commitment | 11 | Compromisos operacionales (datos demo) |
| core."user" | 9 | 9 users activos, 8 roles ocupados, 5 vacíos |
| core.ipr_problem | 6 | Problemas detectados (datos demo) |
| core.alert | 5 | Alertas sistema (datos demo) |
| core.session | 2 | Sesiones crisis (datos demo) |
| core.ipr_milestone | 0 | Sin datos fuente (requiere harvest DIPIR) |
| core.progress_report | 1 | Un solo reporte de avance |
| ref.category | 731 | 78 schemes distintos |
| txn.event | 4,251 | 7 tipos (Rendicion 8%, Aprobacion, Modificacion, etc.) |

### MCD Phase Distribution

| Phase | Code | IPR Count | % |
|-------|------|----------:|--:|
| Formalización & Ejecución | F4 | 1,831 | 50.6% |
| Sin fase asignada | — | 1,649 | 45.5% |
| Evaluación Técnica | F2 | 141 | 3.9% |
| Formulación & Ingreso | F0 | 1 | 0.03% |
| Admisibilidad | F1 | 0 | 0% |
| Priorización | F3 | 0 | 0% |
| Cierre | F5 | 0 | 0% |

### Mechanism Distribution

| Mechanism | Code | IPR Count | % |
|-----------|------|----------:|--:|
| Track E1: Subvención 8% | SUBV8 | 1,648 | 45.5% |
| Track A: SNI General | SNI | 1,627 | 44.9% |
| Track D2: Transferencias | TRANSFER | 343 | 9.5% |
| Track E2: FRPD Royalty | FRPD | 3 | 0.1% |
| Sin mecanismo | — | 1 | 0.03% |
| Track B: Circular 33 | C33 | 0 | 0% |
| Track C: FRIL | FRIL | 0 | 0% |
| Track D1: Glosa 06 | GLOSA06 | 0 | 0% |

### Organization Type Distribution (activas)

| Tipo | Count | % |
|------|------:|--:|
| ORG_COMUNITARIA | 1,626 | 49.2% |
| ONG | 1,568 | 47.4% |
| MUNICIPALIDAD | 46 | 1.4% |
| SERVICIO | 23 | 0.7% |
| UNIVERSIDAD | 10 | 0.3% |
| UNIDAD | 8 | 0.2% |
| DIVISION | 8 | 0.2% |
| STAFF_UNIT | 7 | 0.2% |
| DEPARTAMENTO | 6 | 0.2% |
| ADVISORY_BODY | 3 | 0.1% |
| EMPRESA | 2 | 0.1% |
| GORE | 1 | 0.03% |

### Agreement State Distribution

| Estado | Count | % |
|--------|------:|--:|
| VIGENTE | 459 | 85.5% |
| BORRADOR | 55 | 10.2% |
| EN_REVISION_JURIDICA | 7 | 1.3% |
| FIRMADO_GORE | 6 | 1.1% |
| RESCILIADO | 6 | 1.1% |
| VENCIDO | 3 | 0.6% |
| EN_MODIFICACION | 1 | 0.2% |
| *6 estados sin uso* | 0 | — |

### System Roles (13 definidos)

| Rol | Users Activos |
|-----|:------------:|
| ADMIN_SISTEMA | 2 |
| ADMIN_REGIONAL | 1 |
| JEFE_DIVISION | 1 |
| ENCARGADO | 1 |
| JEFE_DGI | 1 |
| ESP_CONTROL_GESTION | 1 |
| ESP_PROCESOS | 1 |
| ESP_TD | 1 |
| GOBERNADOR | 0 |
| CONSEJERO_REGIONAL | 0 |
| SECRETARIO_EJECUTIVO | 0 |
| JEFE_DEPARTAMENTO | 0 |
| JEFE_UNIDAD | 0 |

### Transaction Event Distribution

| Tipo | Count | % |
|------|------:|--:|
| Rendicion 8% | 1,667 | 39.2% |
| Aprobacion | 830 | 19.5% |
| Modificacion Presupuestaria | 456 | 10.7% |
| Incorporacion | 422 | 9.9% |
| Creacion | 420 | 9.9% |
| Transicion de Estado | 240 | 5.6% |
| Asignacion | 216 | 5.1% |

### IPR Field Completeness

| Campo | Completitud |
|-------|:----------:|
| mechanism_id | 3,621/3,622 (99.97%) |
| mcd_phase_id | 1,973/3,622 (54.5%) |
| sponsor_division_id | 0/3,622 (0%) |
| assignee_id | 0/3,622 (0%) |

---

## 9. API Coverage (102 endpoints)

| Router | Prefix | Endpoints | Dominio ontológico |
|--------|--------|:---------:|-------------------|
| ipr.py | /api/ipr | 21 | IPR + partes + territorio + hitos + avances |
| admin.py | /api/admin | 9 | Usuarios + divisiones |
| dgi_data.py | /api/dgi/data | 9 | Indicadores + datos institucionales + rendiciones |
| convenios.py | /api/convenios | 8 | Convenios + cuotas + transiciones |
| reuniones.py | /api/reuniones | 8 | Reuniones crisis + temas + acuerdos |
| catalogs.py | /api/catalogs | 7 | Categorías + búsquedas catálogo |
| compromisos.py | /api/compromisos | 7 | Compromisos operacionales |
| dgi_reports.py | /api/dgi/reports | 6 | Informes institucionales |
| presupuesto.py | /api/presupuesto | 6 | Presupuesto + CDPs |
| dashboard.py | /api/dashboard | 5 | Dashboards role-aware + charts |
| problemas.py | /api/problemas | 5 | Problemas IPR |
| dgi_initiatives.py | /api/dgi/initiatives | 4 | Iniciativas Kanban |
| alertas.py | /api/alertas | 2 | Alertas sistema |
| auth.py | /api/auth | 2 | Autenticación JWT |
| dgi_cockpit.py | /api/dgi/cockpit | 1 | Panel DGI role-aware |
| search.py | /api/search | 1 | Búsqueda global |
| main.py | /api/health | 1 | Health check |

---

## 10. Referencias

- `docs/GORE_OS_Audit_Detail_v1.0.md` — Auditoría detallada (cruce exhaustivo stories × impl)
- `model/stories/` — 819 historias de usuario (502 dominios temáticos)
- `gorenuble/knowledge/ontologies/onto_gorenuble/` — Ontología institucional (472 CQs, externa)
- `gorenuble/knowledge/domains/gn/01_fundamentos/intro/omega_gore_nuble_mermaid.md` — Modelo Omega v2.6.0
- `gorenuble/staging/confrontar/Informe_Integrado_Confrontacion_GORE_OS_v1.0_vs_FdV_GORE_Nuble_2026-02-26.md` — Informe de Confrontación
- `docs/ETL_ARCHITECTURE_v1.0.md` — Arquitectura ETL (6 fases completadas)
- `model/model_goreos/sql/goreos_ddl.sql` — DDL (78 tablas, 4 schemas)
- `model/model_goreos/sql/goreos_migration_confrontacion.sql` — Migración confrontación
- `model/model_goreos/sql/goreos_migration_rendition_coproduct.sql` — Migración coproducto rendición
