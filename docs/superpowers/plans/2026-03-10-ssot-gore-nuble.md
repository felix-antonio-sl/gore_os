# SSOT GORE Ñuble — Implementation Plan

> **⛔ OBSOLETE for this repo**: This plan targets the external `gorenuble` knowledge repository (KORA/MD artifacts), not the `gore_os` application codebase. No `knowledge/domains/gn/` directory exists in this repo. Retained for reference only.

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create 10 KORA/MD artifacts (1 master + 9 satellites) that reconcile the 4 documentary layers of GORE Ñuble into a Single Source of Truth for LLM agents and GORE_OS design.

**Architecture:** Bundle of independent KORA/MD v6.1.0 artifacts at `knowledge/domains/gn/01_fundamentos/ssot/`. Master coordinates, indexes and disambiguates. Satellites contain canonical domain facts with inline provenance where conflicts exist. Priority hierarchy: Organigrama > Ontología > Omega > CQs.

**Tech Stack:** KORA/MD v6.1.0 (Markdown + YAML frontmatter), KORA spec at `/Users/felixsanhueza/Developer/kora/specs/md-spec.md`

**Source spec:** `docs/superpowers/specs/2026-03-10-ssot-gore-nuble-design.md`

**Target repo:** `/Users/felixsanhueza/Developer/gorenuble/`

---

## File Structure

All files created at `knowledge/domains/gn/01_fundamentos/ssot/`:

| File | URN | Responsibility |
|------|-----|----------------|
| `ssot-master.md` | `urn:gnub:kb:ssot-master` | Index, authority hierarchy, glossary, conflict map, GORE_OS alignment |
| `ssot-organica.md` | `urn:gnub:kb:ssot-organica` | Canonical org structure: 6 divisions, 12 depts, 9 units, 11 staff, 3 advisory |
| `ssot-territorio.md` | `urn:gnub:kb:ssot-territorio` | 3 provinces, 21 communes, territorial hierarchy |
| `ssot-legal.md` | `urn:gnub:kb:ssot-legal` | 3 laws, 8 articles, 6 mandates, 8 glosas, budget hierarchy |
| `ssot-ipr-lifecycle.md` | `urn:gnub:kb:ssot-ipr-lifecycle` | 6 canonical phases, 28 states, 7 eval tracks, 8 financing mechanisms |
| `ssot-presupuesto.md` | `urn:gnub:kb:ssot-presupuesto` | 6-level classifier, funding sources, thresholds, budget cycle |
| `ssot-convenios.md` | `urn:gnub:kb:ssot-convenios` | 6 types, 7 canonical states, GORE_OS 13-state refinement |
| `ssot-rendiciones.md` | `urn:gnub:kb:ssot-rendiciones` | 6 canonical states, 5 SISREC roles, SLAs, 8-phase CGR |
| `ssot-actos-admin.md` | `urn:gnub:kb:ssot-actos-admin` | Act types, 8 approval stages, exemption rules, DIPIR workflow |
| `ssot-dgi.md` | `urn:gnub:kb:ssot-dgi` | 5 indicator dimensions, 3 signals, initiatives, reports |

---

## Chunk 1: Foundation (Master + Organica + Territorio)

### Task 1: Create directory and ssot-master.md

**Files:**
- Create: `knowledge/domains/gn/01_fundamentos/ssot/ssot-master.md`

- [ ] **Step 1: Create SSOT directory**

```bash
mkdir -p /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot
```

- [ ] **Step 2: Write ssot-master.md**

Write the complete file with this content:

```markdown
---
_manifest:
  urn: "urn:gnub:kb:ssot-master"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "Auditoría de consistencia v2.0 — organigrama, ontología (12 TTL), omega v2.6.0, CQs v1.0.1"
version: "1.0.0"
status: draft
tags: [ssot, gore-nuble, reconciliacion, fundamentos, indice]
lang: es
extensions:
  gnub:
    family: ssot
    bundle_version: "1.0.0"
    satellites: 9
---

# SSOT GORE Ñuble — Índice Maestro

## Resumen

Fuente de verdad reconciliada del dominio GORE Ñuble. Bundle de 10 artefactos KORA/MD (este master + 9 satélites). Reconcilia 4 capas documentales con jerarquía de autoridad fija. Consumidores: agentes KODA/RAG y diseño/implementación de GORE_OS.

## Jerarquía de autoridad

| Prioridad | Fuente | Naturaleza | Ubicación |
|-----------|--------|------------|-----------|
| 1 (máxima) | Organigrama GORE 2026 | Resolución exenta — acto administrativo legal | `staging/organigrama_gore_2026.md` |
| 2 | Ontología goreNubleBundle | Modelo formal OWL/SKOS (12 TTL) | `ontologies/onto_gorenuble/` |
| 3 | Omega Mermaid v2.6.0 | Modelo de referencia descriptivo | `domains/gn/01_fundamentos/intro/omega_gore_nuble_mermaid.md` |
| 4 (mínima) | CQs Master v1.0.1 | 472 preguntas de competencia | `ontologies/onto_gorenuble/goreNubleCQs_Master.yml` |

**Criterio de resolución**: ante conflicto entre fuentes, prevalece la de mayor prioridad. Las fuentes mantienen su ciclo de vida propio — este SSOT es una vista reconciliada, no un reemplazo.

## Mapa de artefactos

| URN | Título | Fuentes primarias | Status |
|-----|--------|-------------------|--------|
| `urn:gnub:kb:ssot-organica` | Estructura orgánica | Organigrama > OrgData.ttl > Omega | draft |
| `urn:gnub:kb:ssot-territorio` | Territorio | OrgData.ttl > Omega > CQs | draft |
| `urn:gnub:kb:ssot-legal` | Marco normativo | LegalData.ttl > Omega | draft |
| `urn:gnub:kb:ssot-ipr-lifecycle` | Ciclo de vida IPR | ReferenceData.ttl + IPRData.ttl > Omega > CQs | draft |
| `urn:gnub:kb:ssot-presupuesto` | Presupuesto | LegalData.ttl > Omega > ReferenceData.ttl | draft |
| `urn:gnub:kb:ssot-convenios` | Convenios | ApprovalData.ttl > ReferenceData.ttl > Omega | draft |
| `urn:gnub:kb:ssot-rendiciones` | Rendiciones SISREC | RenditionData.ttl > ReferenceData.ttl > Omega | draft |
| `urn:gnub:kb:ssot-actos-admin` | Actos administrativos | ApprovalData.ttl > DipirOntology.ttl > DipirRules.ttl | draft |
| `urn:gnub:kb:ssot-dgi` | DGI | Ontology.ttl > Omega > CQs | draft |

## Glosario de reconciliación

Términos donde las fuentes difieren. El valor canónico es el declarado aquí.

| Término | Canónico | Alternativas descartadas | Fuente autoritativa |
|---------|----------|--------------------------|---------------------|
| Sigla Div. Infraestructura | DIINF | DIT (GORE_OS legacy) | OrgData.ttl, Organigrama |
| Nombre Div. Infraestructura | Infraestructura y Transportes (plural) | Infraestructura y Transporte (singular, Omega) | Organigrama, OrgData.ttl |
| Clasificación DGI | StaffUnit | Departamento (Organigrama) | OrgData.ttl (mayor granularidad tipológica) |
| RS (sigla evaluación) | Recomendación Satisfactoria | Rentabilidad Social (ReferenceData.ttl) | IPRData.ttl, CQs, uso institucional |
| F0 (nombre fase) | Postulación | Formulación e Ingreso (IPRData), Formulación & Ingreso (Omega) | ReferenceData.ttl (alineado con TBox) |
| F2 (nombre fase) | Evaluación | Evaluación Técnica (IPRData, Omega) | ReferenceData.ttl |
| F3 (nombre fase) | Priorización | Aprobación Presupuestaria (IPRData), Priorización & Asignación (Omega) | ReferenceData.ttl |
| FundingSource | Concepto categorial (Category) | — | Ontology.ttl TBox |
| FinancingMechanism | Concepto de catálogo (CatalogItem) | — | Ontology.ttl TBox (distinto de FundingSource) |
| RenditionState | 6 estados (RenditionData.ttl) | AccountabilityState 5 estados (ReferenceData.ttl) | RenditionData.ttl (más granular) |
| FRPD | Fondo Regional para la Productividad y el Desarrollo | "Fondo Regional Productividad y Desarrollo" (Omega, sin "para la") | Nombre legal completo |
| FRPD mecanismo | Unificado (1 mecanismo) | Split CTCI + Fomento (IPRData.ttl) | ReferenceData.ttl (split es detalle operativo bajo mecanismo único) |
| DIDESO vs DIDECO | DIDESO | DIDECO (GORE_OS test users) | Organigrama, OrgData.ttl, Omega |

## Conflictos transversales

### Doble declaración ABox

**Diagnóstico raíz**: `ReferenceData.ttl` y los archivos de dominio (`IPRData.ttl`, `RenditionData.ttl`, `ApprovalData.ttl`) declaran instancias del mismo tipo con URIs, cardinalidades y granularidades incompatibles. Un SPARQL `SELECT ?s WHERE { ?s a gnub:IPRPhase }` retorna 14 resultados (6+8) en vez de un set canónico.

**Afecta**: fases IPR (6 vs 8), estados rendición (5 vs 6), estados convenio (5 vs 7), fuentes financiamiento (8 vs 7), mecanismos financiamiento (7 vs 8), resultados evaluación (6 vs 10).

**Resolución SSOT**: cada satélite declara el set canónico. El set más granular prevalece cuando es consistente con la jerarquía de autoridad.

### Fases IPR: 6 vs 8

6 fases canónicas (F0-F5) per ReferenceData.ttl + Omega MCD + TBox. IPRData.ttl modela 8 (F0-F7) donde F5=Ejecución, F6=Modificaciones, F7=Cierre. Resolución: F6/F7 son estados operativos dentro de F4 (Formalización) y F5 (Cierre), no fases del ciclo de vida. [ver detalle](urn:gnub:kb:ssot-ipr-lifecycle)

### Clases duplicadas en TBox

`BudgetModificationEvent` (subClass BudgetaryTransaction) y `BudgetModification` (subClass gist:Event) — mismo concepto, jerarquías incompatibles. `RenditionState` y `AccountabilityState` — definiciones virtualmente idénticas sin `owl:equivalentClass`. Pendiente: deprecar duplicados en ontología.

## Alineación GORE_OS

| Concepto canónico | Tabla/Entidad GORE_OS | Endpoint | Nota |
|-------------------|----------------------|----------|------|
| 6 divisiones | `core.organization` (org_type=DIVISION) | `GET /api/catalogs/divisions` | GORE_OS usa DIT como sigla legacy; canónico DIINF |
| 13 system roles | `meta.role` | — | 5 operativos + 4 DGI + 4 governance |
| 6 fases IPR (F0-F5) | `ref.category` scheme `ipr_phase` | — | IPRData F6/F7 no implementados |
| 7 financing tracks | `core.financing_track` | `GET /api/admin/financing-tracks` | Alineado con ReferenceData.ttl |
| 13 agreement states | `ref.category` scheme `agreement_state` | — | 7 ontológicos + 6 refinamiento GORE_OS |
| 8 rendition states | `ref.category` scheme `rendition_status` | — | 6 ontológicos + 2 refinamiento GORE_OS |
| 7 admin act steps | `core.administrative_act` FSM | `PATCH /api/actos/{id}/transition` | Ontología 8 etapas; GORE_OS 7 steps |
| 5 DGI dimensions | `ref.category` scheme `dgi_indicator_dimension` | `POST /api/dgi/data/indicators/refresh` | Solo en GORE_OS, no en Omega |
| 12 FRIL categories | `core.fril_category` | `GET /api/admin/financing-tracks` | Alineado con IPRData.ttl |
| 7 subv8 funds | `core.subv8_fund` | `GET /api/admin/financing-tracks` | Alineado con IPRData.ttl |
```

- [ ] **Step 3: Verify mechanical checks**

```bash
# Check frontmatter valid YAML
head -15 /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/ssot-master.md

# Check URN format
grep "urn:" /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/ssot-master.md

# Check heading depth (max ####)
grep "^#####" /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/ssot-master.md
# Expected: no output (no ##### headings)

# Check no truncated headings
grep '\.\.\.`\?$' /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/ssot-master.md
# Expected: no output
```

- [ ] **Step 4: Commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add knowledge/domains/gn/01_fundamentos/ssot/ssot-master.md
git commit -m "feat(ssot): add master index — SSOT GORE Ñuble bundle v1.0.0"
```

---

### Task 2: Create ssot-organica.md

**Files:**
- Create: `knowledge/domains/gn/01_fundamentos/ssot/ssot-organica.md`

**Reconciliation data** (from audit):
- G-01: CDR/CTCI en ontología pero no en organigrama → canónico por OrgData.ttl
- G-02: DGI StaffUnit (ontología) vs Departamento (organigrama) → StaffUnit prevalece (mayor granularidad)
- G-03: DIINF vs DIT, plural vs singular → DIINF, plural (organigrama + ontología)
- G-04: Auditoría Interna vs Unidad de Control → ambos existen como entidades separadas
- G-05: Corporación Regional tipo → StaffUnit (OrgData.ttl)
- E-05: Gobernador con nombre propio → referenciar por cargo

- [ ] **Step 1: Write ssot-organica.md**

Write the complete file with this content:

```markdown
---
_manifest:
  urn: "urn:gnub:kb:ssot-organica"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "Organigrama GORE 2026, goreNubleOrgData.ttl, omega_gore_nuble_mermaid.md v2.6.0"
version: "1.0.0"
status: draft
tags: [ssot, organica, divisiones, estructura-gore, jerarquia]
lang: es
extensions:
  gnub:
    family: ssot
    bundle: "urn:gnub:kb:ssot-master"
---

# SSOT — Estructura orgánica GORE Ñuble

## Resumen

Estructura orgánica canónica del Gobierno Regional de Ñuble. 6 divisiones, 12 departamentos, 9+ unidades, 11 unidades de staff, 3 cuerpos asesores. Jerarquía 3 niveles: GORE → Divisiones → Departamentos → Unidades. Reconcilia organigrama legal con ontología formal.

## Autoridad ejecutiva

| Cargo | Rol institucional |
|-------|-------------------|
| Gobernador/a Regional | Órgano ejecutivo del Gobierno Regional. Electo/a por votación popular |
| Administrador/a Regional | Colaborador/a directo/a del Gobernador/a. Gestión administrativa |
| Delegado/a Presidencial Regional | Representante del Presidente en la región. Gobierno interior (separado del GORE) |

## Divisiones (6)

| Sigla | Nombre oficial | URI ontología |
|-------|---------------|---------------|
| DIPLADE | División de Planificación y Desarrollo Regional | `_Div_DIPLADE` |
| DIPIR | División de Presupuesto e Inversión Regional | `_Div_DIPIR` |
| DIDESO | División de Desarrollo Social y Humano | `_Div_DIDESO` |
| DIFOI | División de Fomento e Industria | `_Div_DIFOI` |
| DIINF | División de Infraestructura y Transportes | `_Div_DIINF` |
| DAF | División de Administración y Finanzas | `_Div_DAF` |

#### Proveniencia

Nombre: "Infraestructura y Transportes" (plural) per organigrama y OrgData.ttl. Omega usa singular ("Transporte") — descartado. Sigla canónica: DIINF per OrgData.ttl. GORE_OS usa "DIT" como legacy — debe migrar a DIINF. [impl: CLAUDE.md test users usan DIT; pendiente alineación]

## Departamentos (12)

| Departamento | División | URI ontología |
|-------------|----------|---------------|
| Planificación Estratégica y Ordenamiento Territorial | DIPLADE | `_Dept_DIPLADE_PlanificacionEstrategica` |
| Desarrollo de Proyectos Estratégicos | DIPLADE | `_Dept_DIPLADE_ProyectosEstrategicos` |
| Zonas en Desarrollo | DIPLADE | `_Dept_DIPLADE_ZonasDesarrollo` |
| Análisis y Evaluación | DIPIR | `_Dept_DIPIR_AnalisisEvaluacion` |
| Presupuesto | DIPIR | `_Dept_DIPIR_Presupuesto` |
| Fondos Concursables y Programas Sociales | DIDESO | `_Dept_DIDESO_FondosConcursables` |
| Gestión Territorial | DIDESO | `_Dept_DIDESO_GestionTerritorial` |
| Fomento y Desarrollo Productivo | DIFOI | `_Dept_DIFOI_FomentoDesarrolloProductivo` |
| Ciencia, Tecnología e Innovación | DIFOI | `_Dept_DIFOI_CTI` |
| Infraestructura y Conectividad | DIINF | `_Dept_DIINF_InfraestructuraConectividad` |
| Ejecución y Supervisión de Proyectos de Inversión | DIINF | `_Dept_DIINF_EjecucionSupervision` |
| Gestión y Desarrollo de Personas | DAF | `_Dept_DAF_GestionPersonas` |
| Finanzas | DAF | `_Dept_DAF_Finanzas` |

## Unidades (9+)

| Unidad | Padre directo | División |
|--------|---------------|----------|
| Comité de Pertinencia y Vinculación Estratégica | DIPLADE (directo) | DIPLADE |
| Municipalidades y Conservaciones | Depto. Análisis y Evaluación | DIPIR |
| Proyectos y Programas | Depto. Análisis y Evaluación | DIPIR |
| Oficina de Partes | DAF (directo) | DAF |
| Tesorería | Depto. Finanzas | DAF |
| Contabilidad y Finanzas | Depto. Finanzas | DAF |
| Control de Rendiciones (UCR) | Depto. Finanzas | DAF |
| Adquisiciones | Depto. Finanzas | DAF |
| Operaciones (TIC) | Depto. Finanzas | DAF |
| OIRS | DGI (StaffUnit) | — |

## Unidades de staff (11)

Dependencias directas del Gobernador/a o del Administrador/a Regional. Clasificadas como `gnub:StaffUnit` en la ontología.

| Unidad | Dependencia de | URI ontología |
|--------|---------------|---------------|
| Gabinete y Participación Social | Gobernador/a | `_Staff_Gabinete` |
| Comunicaciones | Gobernador/a | `_Staff_Comunicaciones` |
| Control | Gobernador/a | `_Staff_Control` |
| Jurídica | Administrador/a Regional | `_Staff_Juridica` |
| Auditoría Interna | Administrador/a Regional | `_Staff_Auditoria` |
| DGI (Gestión Institucional) | Administrador/a Regional | `_Staff_DGI` |
| Ñuble 250 | Administrador/a Regional | `_Staff_Nuble250` |
| URAI (Asuntos Internacionales) | Administrador/a Regional | `_Staff_URAI` |
| CIES (Emergencia y Seguridad) | Órganos Especiales | `_Staff_EmergenciaSeguridad` |
| Corporación Regional de Desarrollo | Administrador/a Regional | `_Staff_Corporacion` |
| Secretaría Ejecutiva del CORE | CORE | `_Unit_CORE_SecretariaEjecutiva` |

#### Proveniencia

**DGI**: ontología clasifica como `gnub:StaffUnit`. Organigrama lo nombra "Departamento de Gestión Institucional". Prevalece StaffUnit (ontología) por mayor granularidad tipológica — `gnub:Department` y `gnub:StaffUnit` son `owl:disjointWith`, y DGI no depende jerárquicamente de ninguna división. Contiene OIRS como `gnub:Unit` hija. [impl: GORE_OS modela DGI como population="dgi" separada de operativa]

**Control vs Auditoría**: organigrama y ontología los mantienen como entidades separadas con funciones distintas — Control (fiscalización interna continua) vs Auditoría (evaluación independiente).

## Cuerpos asesores (3)

| Cuerpo | Tipo ontológico | URI |
|--------|----------------|-----|
| COSOC (Consejo de la Sociedad Civil) | AdvisoryBody | `_Advisory_COSOC` |
| Comité CTCI (Ciencia, Tecnología, Conocimiento e Innovación) | AdvisoryBody | `_Advisory_ComiteCTCI` |
| CDR (Comité Directivo Regional) | AdvisoryBody | `_Advisory_CDR` |

#### Proveniencia

CDR y Comité CTCI existen en OrgData.ttl como `gnub:AdvisoryBody` pero están ausentes del organigrama (resolución exenta). Práctica habitual en sector público chileno — cuerpos funcionales no formalizados en resolución organizacional. CQs los referencian (CQ-007, CQ-011, CQ-012, CQ-027). Canónicos por ontología.

CDR carece de composición modelada (`gist:hasMember` vacío). CQs preguntan "¿Quién preside el CDR?" — actualmente irrespondible.

## CORE (Consejo Regional)

16 Consejeros/as Regionales electos/as por votación popular. Secretaría Ejecutiva del CORE como soporte administrativo.

Quórum canónico per GORE_OS:
- Simple: 9/16
- Calificado: 11/16

[impl: CLAUDE.md §Rule 31 — CORE sessions, gate F3→F4 >7K UTM]

## Jerarquía completa

```
GORE Ñuble
├── Gobernador/a Regional
│   ├── Gabinete y Participación Social (Staff)
│   ├── Comunicaciones (Staff)
│   └── Control (Staff)
├── Administrador/a Regional
│   ├── Jurídica (Staff)
│   ├── Auditoría Interna (Staff)
│   ├── DGI (Staff) → OIRS (Unit)
│   ├── Ñuble 250 (Staff)
│   ├── URAI (Staff)
│   └── Corporación Regional (Staff)
├── CORE → Secretaría Ejecutiva (Staff)
├── DIPLADE (División)
│   ├── Depto. Planificación Estratégica y OT
│   ├── Depto. Desarrollo Proyectos Estratégicos
│   ├── Depto. Zonas en Desarrollo
│   └── Comité de Pertinencia (Unidad)
├── DIPIR (División)
│   ├── Depto. Análisis y Evaluación
│   │   ├── Unidad Municipalidades y Conservaciones
│   │   └── Unidad Proyectos y Programas
│   └── Depto. Presupuesto
├── DIDESO (División)
│   ├── Depto. Fondos Concursables y Programas Sociales
│   └── Depto. Gestión Territorial
├── DIFOI (División)
│   ├── Depto. Fomento y Desarrollo Productivo
│   └── Depto. CTI
├── DIINF (División)
│   ├── Depto. Infraestructura y Conectividad
│   └── Depto. Ejecución y Supervisión
├── DAF (División)
│   ├── Oficina de Partes (Unidad)
│   ├── Depto. Gestión y Desarrollo de Personas
│   └── Depto. Finanzas
│       ├── Tesorería (Unidad)
│       ├── Contabilidad y Finanzas (Unidad)
│       ├── UCR (Unidad)
│       ├── Adquisiciones (Unidad)
│       └── Operaciones/TIC (Unidad)
├── CIES (Staff, Órganos Especiales)
└── Cuerpos Asesores
    ├── COSOC
    ├── Comité CTCI
    └── CDR
```
```

- [ ] **Step 2: Verify mechanical checks**

```bash
head -15 /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/ssot-organica.md
grep "^#####" /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/ssot-organica.md
# Expected: no output
```

- [ ] **Step 3: Commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add knowledge/domains/gn/01_fundamentos/ssot/ssot-organica.md
git commit -m "feat(ssot): add ssot-organica — canonical org structure (6 div, 12 dept, 11 staff, 3 advisory)"
```

---

### Task 3: Create ssot-territorio.md

**Files:**
- Create: `knowledge/domains/gn/01_fundamentos/ssot/ssot-territorio.md`

- [ ] **Step 1: Write ssot-territorio.md**

```markdown
---
_manifest:
  urn: "urn:gnub:kb:ssot-territorio"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "goreNubleOrgData.ttl, omega_gore_nuble_mermaid.md v2.6.0, Ley 21.033"
version: "1.0.0"
status: draft
tags: [ssot, territorio, provincias, comunas, nuble]
lang: es
extensions:
  gnub:
    family: ssot
    bundle: "urn:gnub:kb:ssot-master"
---

# SSOT — Territorio GORE Ñuble

## Resumen

Región de Ñuble: 3 provincias, 21 comunas. Creada por Ley 21.033 (2017, vigencia 2018) por escisión de la Provincia de Ñuble desde la Región del Biobío. Superficie 13.178,5 km². Capital: Chillán. Sin conflictos entre fuentes — datos estables y consistentes.

## Ficha territorial

| Atributo | Valor | Fuente |
|----------|-------|--------|
| Creación | Ley 21.033 (promulgada 05-09-2017, vigencia 06-09-2018) | Ley 21.033 |
| Origen | Escisión Provincia de Ñuble desde Región del Biobío | Ley 21.033 |
| Superficie | 13.178,5 km² (menor región continental) | INE |
| Población | 512.289 habitantes (Censo 2017) | INE |
| Capital | Chillán | Ley 21.033 |
| Provincias | 3 | Ley 21.033 |
| Comunas | 21 | Ley 21.033 |
| Índice envejecimiento | 97,6 (vs 79,0 nacional) | CASEN |
| Ruralidad | 28,7% (vs 11,3% nacional) | INE |
| Pobreza por ingresos | 12,1% (vs 6,5% nacional) | CASEN |

## Provincias y comunas

### Provincia de Diguillín

Capital: Bulnes. 9 comunas.

Chillán, Chillán Viejo, Bulnes, El Carmen, Pemuco, Pinto, Quillón, San Ignacio, Yungay.

### Provincia de Itata

Capital: Quirihue. 7 comunas.

Cobquecura, Coelemu, Ninhue, Portezuelo, Quirihue, Ránquil, Tréguaco.

### Provincia de Punilla

Capital: San Carlos. 5 comunas.

Coihueco, Ñiquén, San Carlos, San Fabián, San Nicolás.

## Tipos de impacto territorial

Definidos en GORE_OS (`core.ipr_territory`), 4 tipos de impacto per IPR. Ontología no los modela — extensión de implementación.

[impl: `GET /api/catalogs/territories` retorna 25 entidades (3 provincias + 21 comunas + 1 región). UNIQUE constraint `uq_ipr_territory_impact`. CLAUDE.md §Rule 17]
```

- [ ] **Step 2: Commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add knowledge/domains/gn/01_fundamentos/ssot/ssot-territorio.md
git commit -m "feat(ssot): add ssot-territorio — 3 provinces, 21 communes"
```

---

## Chunk 2: Legal + IPR Lifecycle

### Task 4: Create ssot-legal.md

**Files:**
- Create: `knowledge/domains/gn/01_fundamentos/ssot/ssot-legal.md`

**Reconciliation data**:
- LegalData.ttl: 3 laws, 8 articles, 6 mandates, 6 budgetary rules
- IPRData.ttl: 8 glosas (01, 03, 06, 07, 10, 11, 12, 14)
- Omega: glosas 01, 03, 06, 07, 10/11, 12, 13, 14
- GORE_OS: 7/7 glosas implemented

- [ ] **Step 1: Write ssot-legal.md**

```markdown
---
_manifest:
  urn: "urn:gnub:kb:ssot-legal"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "goreNubleLegalData.ttl, omega_gore_nuble_mermaid.md v2.6.0, goreNubleIPRData.ttl"
version: "1.0.0"
status: draft
tags: [ssot, legal, normativo, glosas, loc-gore, presupuestos]
lang: es
extensions:
  gnub:
    family: ssot
    bundle: "urn:gnub:kb:ssot-master"
---

# SSOT — Marco normativo GORE Ñuble

## Resumen

3 cuerpos legales, 8 artículos modelados, 6 mandatos, 8+ glosas presupuestarias. Marco normativo que rige la gestión del GORE, con énfasis en LOC GORE y Ley de Presupuestos 2026 Partida 31.

## Cuerpos legales

| Documento | Descripción | URI ontología |
|-----------|-------------|---------------|
| LOC GORE (DFL 1-19.175) | Ley Orgánica Constitucional de Gobiernos Regionales, texto refundido | `_LegalDoc_LOC_GORE` |
| Ley 21.033 | Creación de la Región de Ñuble | `_LegalDoc_Ley21033` |
| Ley de Presupuestos 2026 | Partida 31 GORE — presupuesto sector público 2026 | `_LegalDoc_LeyPresupuestos2026` |

## Artículos modelados

| Artículo | Cuerpo legal | Materia |
|----------|-------------|---------|
| Art. 2 | LOC GORE | Atribuciones del Delegado Presidencial Regional |
| Art. 16 | LOC GORE | Funciones generales del Gobierno Regional |
| Art. 17 | LOC GORE | Funciones de ordenamiento territorial |
| Art. 18 | LOC GORE | Funciones de fomento productivo |
| Art. 19 | LOC GORE | Funciones de desarrollo social y cultural |
| Art. 20 | LOC GORE | Atribuciones generales del Gobierno Regional |
| Art. 21 bis | LOC GORE | Transferencia de competencias desde nivel central |
| Art. 6 | Ley Presupuestos 2026 | Umbrales para licitación pública |

## Mandatos legales

| Mandato | Deriva de | Obliga a |
|---------|-----------|----------|
| Aprobar Presupuesto Regional | Art. 16 LOC | GORE Ñuble |
| Aprobar PROT | Art. 17 LOC | GORE Ñuble |
| Fomentar Turismo Regional | Art. 18 LOC | GORE Ñuble |
| Coordinar Seguridad Pública | Art. 2 LOC | DPR Ñuble |
| Licitación pública proyectos > 1.000 UTM | Art. 6 Ley 2026 | GORE Ñuble |
| Licitación pública estudios > 500 UTM | Art. 6 Ley 2026 | GORE Ñuble |

## Glosas presupuestarias (Ley Presupuestos 2026, Partida 31)

| Glosa | Asunto | Gastos personal | Restricciones clave |
|-------|--------|-----------------|---------------------|
| 01 | Marco general FNDR | — | Reglas asignación y modificación presupuestaria |
| 03 | Prohibiciones inversión | Prohibido | NO préstamos, NO gastos personal/bienes consumo receptores, NO aportes sociedades |
| 06 | Programas públicos regionales (S24) | Permitido | Evaluación ex-ante DIPRES/SES. Admin GORE max 5%, honorarios receptor max 5% |
| 07 | Subvenciones 8% FNDR | — | Concurso público. Asignaciones directas ≤10% (Res. 72/2025 DIPRES). Inhabilita si rendiciones pendientes |
| 10/11 | Aumentos inversión | — | ≤10% costo aprobado NO requiere nueva aprobación CORE |
| 12 | FRIL | Prohibido | Transferencias a municipalidades. Exención RS < 5.000 UTM. Solo obras |
| 13 | FRPD (Royalty Minero) | — | I+D+i, instituciones habilitadas |
| 14 | Emergencias | — | 3% traspasable a Subsec. Interior + 2% uso interno GORE |

[impl: GORE_OS implementa 7/7 glosas. `check_glosa_rules()` en `ipr.py`. `_check_glosa03_prohibition()` bloquea FNDR→PERSONAL. `check_glosa07_transfer_limits()` en `presupuesto.py`. CLAUDE.md §Rules 36-38]

## Tipos de glosa

| Tipo | Descripción |
|------|-------------|
| Numérica | Limita montos/cantidades |
| Textual | Condiciones, prohibiciones, mandatos |
| Mixta | Límites numéricos + condiciones textuales |
| Estructural | Define estructura/desagregación |

## Regla cofinanciamiento C33

Circular 33: exige 20% aporte propio en Activos No Financieros. `requiresCoFinancing = true`.

[impl: `_check_c33_conservation()` gate F1→F2, informational. CLAUDE.md §Rule 38]

## Jerarquía presupuestaria

3 niveles estatutarios modelados en ontología:

Partida 31 (Gobiernos Regionales) → Capítulo 01 → Programa 19 (GORE Ñuble)

[ver clasificador completo](urn:gnub:kb:ssot-presupuesto)
```

- [ ] **Step 2: Commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add knowledge/domains/gn/01_fundamentos/ssot/ssot-legal.md
git commit -m "feat(ssot): add ssot-legal — 3 laws, 8 articles, 8 glosas"
```

---

### Task 5: Create ssot-ipr-lifecycle.md

**Files:**
- Create: `knowledge/domains/gn/01_fundamentos/ssot/ssot-ipr-lifecycle.md`

**Reconciliation data** (critical findings B-01, O-01, O-02, O-03, O-04, O-05):
- Phases: 6 canonical (ReferenceData + Omega + TBox) vs 8 (IPRData)
- Phase names: diverge across sources for F0, F2, F3
- Tracks: 4 (IPRData) vs 7 (Omega)
- Eval results: 6 (ReferenceData) vs 10 (IPRData)
- IPR types: 4 subclasses (ontology) vs 2 supertypes (Omega)

- [ ] **Step 1: Write ssot-ipr-lifecycle.md**

```markdown
---
_manifest:
  urn: "urn:gnub:kb:ssot-ipr-lifecycle"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "goreNubleReferenceData.ttl, goreNubleIPRData.ttl, goreNubleOntology.ttl, omega_gore_nuble_mermaid.md v2.6.0, goreNubleCQs_Master.yml"
version: "1.0.0"
status: draft
tags: [ssot, ipr, ciclo-vida, fases, estados, tracks, evaluacion]
lang: es
extensions:
  gnub:
    family: ssot
    bundle: "urn:gnub:kb:ssot-master"
---

# SSOT — Ciclo de vida IPR

## Resumen

Modelo canónico de estados (MCD) de la Intervención Pública Regional. 6 fases (F0-F5), 28 estados (17 universales + 9 proyecto + 2 programa), 8 mecanismos de financiamiento, 7 tracks de evaluación. IPR es polimórfica: Proyecto, Programa de Inversión, Programa Operativo, Estudio Básico.

## Fases canónicas (6)

| Fase | Nombre canónico | Descripción |
|------|----------------|-------------|
| F0 | Postulación | Formulación e ingreso de la iniciativa |
| F1 | Admisibilidad | Verificación de requisitos formales |
| F2 | Evaluación | Evaluación técnica según track |
| F3 | Priorización | Aprobación presupuestaria y asignación CORE |
| F4 | Formalización | Convenio, decreto, ejecución |
| F5 | Cierre | Rendición final y cierre administrativo |

#### Proveniencia

Canónico: ReferenceData.ttl (6 fases F0-F5), alineado con TBox (skos:definition en goreNubleOntology.ttl:622) y Omega MCD.

Descartado: IPRData.ttl modela 8 fases (F0-F7) donde F5=Ejecución, F6=Modificaciones, F7=Cierre. Resolución: F6 y F7 son estados operativos dentro de F4/F5, no fases del ciclo de vida. La ejecución y las modificaciones ocurren durante F4 (Formalización); el cierre con rendición es F5.

Nombres canónicos: ReferenceData.ttl prevalece (Postulación, Evaluación, Priorización) sobre IPRData (Formulación e Ingreso, Evaluación Técnica, Aprobación Presupuestaria) y Omega (Formulación & Ingreso, Priorización & Asignación).

## Tipos IPR (4 subclases)

| Tipo | Subtítulo | Crea activo | Superclase |
|------|-----------|-------------|------------|
| IPRProject (Proyecto) | 31/33 | Sí | IPR |
| InvestmentProgram (Programa de Inversión) | 31 ítem 03 | Sí | IPR |
| OperationalProgram (Programa Operativo) | 24 | No | IPR |
| BasicStudy (Estudio Básico) | 22 | No | IPR |

Clases `owl:disjointWith` en TBox.

#### Proveniencia

Ontología define 4 subclases. Omega muestra solo 2 supertypes (PROYECTO capital, PROGRAMA corriente). InvestmentProgram y BasicStudy sin representación en Omega — gap documental del Omega, no del modelo. Canónico: 4 subclases per ontología.

## Estados IPR (28)

### Estados universales (17)

| Seq | Estado | Fase |
|-----|--------|------|
| 1 | Pre-Admisible CDR | F1 |
| 2 | Para Revisión Técnica | F1 |
| 3 | Admisible | F1 |
| 4 | Inadmisible | F1 |
| 28 | Rechazado | F1 |
| 12 | Cartera Enviada a CORE | F3 |
| 13 | Certificado CORE OK | F3 |
| 14 | CDP Emitido | F3 |
| 15 | Decreto Tramitado | F4 |
| 16 | Convenio Formalizado | F4 |
| 17 | Tomado de Razón CGR | F4 |
| 20 | En Obra/Ejecución | F4 |
| 26 | Paralizado | F4 |
| 23 | Rendición Pendiente | F5 |
| 24 | Rendición Aprobada | F5 |
| 25 | IPR Cerrada | F5 |
| 27 | Terminado Anticipadamente | F5 |

### Estados proyecto (9)

| Seq | Estado | Fase |
|-----|--------|------|
| 5 | Enviado a MDSF | F2 |
| 6 | Recomendación Satisfactoria (RS) | F2 |
| 7 | Falta Información (FI) | F2 |
| 8 | Objetado Técnicamente (OT) | F2 |
| 11 | Admisibilidad Directa (AD) | F2 |
| 18 | En Licitación | F4 |
| 19 | Contrato Firmado | F4 |
| 21 | Recepción Provisoria | F4 |
| 22 | Recepción Definitiva | F5 |

### Estados programa (2)

| Seq | Estado | Fase |
|-----|--------|------|
| 9 | Recomendación Favorable (RF) | F2 |
| 10 | Informe Técnico Favorable (ITF) | F2 |

## Mecanismos de financiamiento (8)

| Mecanismo | Track | Fuente | Evaluador | Subtítulo |
|-----------|-------|--------|-----------|-----------|
| SNI General | A | FNDR | MDSF | S31 |
| FRIL | C | FNDR | GORE (DIPIR) | S33 |
| Circular 33 | B | — | MDSF/GORE | S31 |
| Glosa 06 (Ejecución Directa) | D1 | — | DIPRES/SES | S24 |
| Transferencia PPR | D2 | — | GORE (Comité/DAE) | S24 |
| Subvención 8% | E1 | FNDR | GORE (Comisión Evaluadora) | S24 |
| FRPD | E2 | FRPD | ANID/CORFO/GORE | S31/S33 |

#### Proveniencia

ReferenceData.ttl modela 7 mecanismos (FRPD unificado). IPRData.ttl modela 8 (FRPD split en CTCI y Fomento). Canónico: 7 mecanismos en ReferenceData (FRPD unificado). El split CTCI/Fomento es detalle operativo (líneas dentro del mecanismo), no mecanismos separados. GORE_OS `core.financing_track` tiene 7 tracks alineados.

**Nota**: la tabla usa 8 filas por claridad pero FRPD es 1 mecanismo con 2 líneas operativas.

## Tracks de evaluación (7)

| Track | Mecanismo | Evaluador | Dictamen |
|-------|-----------|-----------|----------|
| A — SNI General | SNI | MDSF | RS (Recomendación Satisfactoria) |
| B — Circular 33 | C33 | MDSF/GORE | AD (Admisibilidad) |
| C — FRIL | FRIL | GORE (DIPIR) | AT (Aprobación Técnica) |
| D1 — Glosa 06 | Glosa 06 | DIPRES/SES | RF (Recomendación Favorable) |
| D2 — Transferencias | Transfer | GORE (Comité/DAE) | ITF (Informe Técnico Favorable) |
| E1 — Subvención 8% | Subv8 | GORE (Comisión) | Puntaje/Ranking |
| E2 — FRPD | FRPD | ANID/CORFO/GORE | Elegibilidad + RS/RF |

#### Proveniencia

Omega define 7 tracks (A-E2). IPRData.ttl modela 4 tracks (RATE, Glosa06, LocalGORE, CTCI) — granularidad menor que agrupa sub-tracks del Omega bajo tracks amplios. Canónico: 7 tracks del Omega por mayor resolución operativa. Relación `skos:broader` pendiente en ontología.

## Resultados de evaluación (10)

| Código | Nombre completo | Track |
|--------|----------------|-------|
| RS | Recomendación Satisfactoria | A (SNI) |
| FI | Falta Información | A (SNI) |
| OT | Objetado Técnicamente | A (SNI) |
| AD | Admisible | B (C33), C (FRIL) |
| RF | Recomendación Favorable | D1 (G06) |
| ITF | Informe Técnico Favorable | D2 (Transfer) |
| AT | Aprobación Técnica | C (FRIL) |
| Elegible | Elegible (FRPD/FIC) | E2 (FRPD) |
| NV | No Viable | Transversal |
| Puntaje | Puntaje (concursos) | E1 (8%), E2 (FRPD) |

#### Proveniencia

ReferenceData.ttl: 6 resultados (RS, FI, OT, RF, ITF, AD). IPRData.ttl: 10 resultados (agrega AT, Elegible, NV, Puntaje). Canónico: 10 per IPRData (set más completo). RS = "Recomendación Satisfactoria" (IPRData, CQs, uso institucional), NO "Rentabilidad Social" (ReferenceData.ttl — descartado).

## Fuentes de financiamiento (FundingSource)

| Código | Nombre | URI ReferenceData | URI IPRData |
|--------|--------|-------------------|-------------|
| FNDR | Fondo Nacional de Desarrollo Regional | ✓ | ✓ |
| FRPD | Fondo Regional para la Productividad y el Desarrollo | ✓ | ✓ |
| ISAR | Inversiones Sectoriales de Asignación Regional | ✓ | ✓ |
| FIC | Fondo de Innovación para la Competitividad | ✓ | ✓ (como FIC) |
| FATC | Fondo de Apoyo a la Transferencia de Competencias | ✓ | ✓ (distinto nombre) |
| FRIL | Fondo Regional de Iniciativa Local | ✓ (solo Ref) | — |
| PROPIR | Programa Público de Inversiones Regionales | ✓ (solo Ref) | — |
| SECT | Fondos Sectoriales | ✓ (solo Ref) | — |
| FEI | Fondo de Equidad Interregional | — | ✓ (solo IPR) |
| FEIRR | Fondo de Inversión y Reconversión Regional | — | ✓ (solo IPR) |

#### Proveniencia

ReferenceData.ttl: 8 fuentes. IPRData.ttl: 7 fuentes. Sets no son superconjuntos — cada uno tiene exclusivas. Canónico: unión de ambos (10 fuentes). `FundingSource` es `gnub:Category` (concepto categorial), distinto de `FinancingMechanism` que es `gnub:CatalogItem`. GORE_OS `ref.category` scheme `funding_source` tiene 11 — incluye fuentes adicionales de implementación.

## Niveles de proporcionalidad SNI (4)

| Nivel | Umbral | Etapas |
|-------|--------|--------|
| 0 | < 5.000 UTM | Solo Ejecución (exención evaluación) |
| 1 | Baja complejidad | Perfil → Ejecución |
| 2 | Estándar | Perfil → Prefactibilidad → Ejecución |
| 3 | Alta complejidad | Idea → Perfil → Prefactibilidad → Factibilidad → Ejecución |

[impl: `core.sni_level_config` (4 niveles, admin CRUD). `_check_sni_proporcionalidad()` gate F1→F2. CLAUDE.md §Rule 38]

## Categorías FRIL (12)

| Grupo | Código | Nombre | Exención límite comunal |
|-------|--------|--------|------------------------|
| A — Desarrollo Territorial | A1 | Integración Rural | No |
| | A2 | Acceso al Agua | Sí |
| | A3 | Vial | Sí |
| B — Servicios | B1 | Edificación Pública | No |
| | B2 | Gestión Riesgos | No |
| | B3 | Seguridad | No |
| C — Desarrollo Social y Económico | C1 | Inclusión | No |
| | C2 | Género | No |
| | C3 | Turismo | No |
| D — Medio Ambiente | D1 | Deportes | No |
| | D2 | Áreas Verdes | No |
| | D3 | Sustentabilidad | No |

[impl: `core.fril_category` (12, `is_exempt_commune_limit` para A2/A3). `_check_fril_max_per_comuna()` gate F0→F1. CLAUDE.md §Rule 38]

## Fondos temáticos Subv. 8% (7)

| Fondo | Techo |
|-------|-------|
| Cultura | $5M |
| Deporte | $5M |
| Social | $5,5M |
| Seguridad Ciudadana | $8M |
| Medio Ambiente | $5M |
| Adulto Mayor | $4M |
| Género | $6,5M |

[impl: `core.subv8_fund` (7) + `core.subv8_fund_ceiling` (~22). Admin CRUD. CLAUDE.md §Rule 45]

## Estados de admisibilidad (5)

PRE-ADMISIBLE CDR, NO PRE-ADMISIBLE CDR, ADMISIBLE, ADMISIBLE CON OBSERVACIONES, INADMISIBLE.

[impl: `core.admissibility_item` + `core.admissibility_check`. Gate PRE_ADMISIBLE→ADMISIBLE. CLAUDE.md §Rule 41]
```

- [ ] **Step 2: Commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add knowledge/domains/gn/01_fundamentos/ssot/ssot-ipr-lifecycle.md
git commit -m "feat(ssot): add ssot-ipr-lifecycle — 6 phases, 28 states, 7 tracks, 10 eval results"
```

---

## Chunk 3: Presupuesto + Convenios + Rendiciones

### Task 6: Create ssot-presupuesto.md

**Files:**
- Create: `knowledge/domains/gn/01_fundamentos/ssot/ssot-presupuesto.md`

- [ ] **Step 1: Write ssot-presupuesto.md**

```markdown
---
_manifest:
  urn: "urn:gnub:kb:ssot-presupuesto"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "goreNubleLegalData.ttl, goreNubleIPRData.ttl, omega_gore_nuble_mermaid.md v2.6.0"
version: "1.0.0"
status: draft
tags: [ssot, presupuesto, clasificador, subtitulos, umbrales, ciclo]
lang: es
extensions:
  gnub:
    family: ssot
    bundle: "urn:gnub:kb:ssot-master"
---

# SSOT — Presupuesto GORE Ñuble

## Resumen

Clasificador presupuestario de 6 niveles, 6 subtítulos operativos, umbrales financieros, ciclo presupuestario. Partida 31 → Capítulo 01 → Programa 19 (GORE Ñuble). Fuente autoritativa: LegalData.ttl + Ley de Presupuestos 2026.

## Clasificador presupuestario (6 niveles)

| Nivel | Tipo | Ejemplo |
|-------|------|---------|
| 1 | Partida | 31 — Gobiernos Regionales |
| 2 | Capítulo | 01 |
| 3 | Programa | 19 — GORE Ñuble |
| 4 | Subtítulo | 31 — Iniciativas de Inversión |
| 5 | Ítem | 03 — Programas de Inversión |
| 6 | Asignación | Específica por proyecto/programa |

[impl: GORE_OS 6-level classifier completo. `budget_item`(14), `budget_allocation`(15), `program_type`(5). Admin CRUD `budget_program_code`. CLAUDE.md §Rule 37]

## Subtítulos operativos (6)

| Subtítulo | Nombre | Uso principal | División |
|-----------|--------|---------------|----------|
| 21 | Gastos en Personal | Remuneraciones planta/contrata | DAF |
| 22 | Bienes y Servicios de Consumo | Gastos operativos | DAF |
| 24 | Transferencias Corrientes | Programas G06, 8% FNDR, transferencias | DIPIR |
| 29 | Adquisición Activos No Financieros | Compra activos propios | DAF |
| 31 | Iniciativas de Inversión | Ejecución directa: proyectos propios | DIPIR |
| 33 | Transferencias de Capital | Ejecución indirecta: transferencias a municipios/FRIL | DIPIR |

#### Proveniencia

6 subtítulos consistentes entre IPRData.ttl (S21, S22, S24, S29, S31, S33) y Omega. GORE_OS `budget_subtitle` scheme tiene 8 — incluye subtítulos adicionales de implementación.

## Ejecución presupuestaria

Cadena de ejecución per programa:

Inicial → Vigente → Comprometido → Devengado → Pagado

[impl: `core.budget_program` (25.761 registros). Campos: `initial_amount`, `current_amount`, `committed_amount`, `accrued_amount`, `paid_amount`. CLAUDE.md §Rule 28]

## Umbrales financieros

| Concepto | Umbral | Fuente |
|----------|--------|--------|
| Exención RS (FRIL Ñuble) | < 4.545 UTM | Glosa 12 |
| Licitación pública (obras) | > 1.000 UTM | Art. 6 Ley 2026 |
| Licitación pública (estudios/servicios) | > 500 UTM | Art. 6 Ley 2026 |
| Toma de Razón CGR | > 2.500 UTM | Res. 7/2019 CGR |
| Aprobación CORE | > 7.000 UTM | GORE_OS parametric |
| Evaluación SNI obligatoria | > 15.000 UTM | Omega |
| Trato directo (monto ínfimo) | < 10 UTM | Omega |

#### Proveniencia

DipirRules.ttl modela exención Toma de Razón con umbral 5.000 UTM (ejemplo genérico) con operador "menor que". Omega especifica 2.500 UTM para GORE Ñuble. Canónico: 2.500 UTM per Omega (regional) + GORE_OS.

Operador: `<` (menor que) per DipirRules.ttl. Omega es inconsistente internamente (usa "<=" en tabla y "<" en árbol de decisión). Canónico: `<` per ontología.

[impl: `core.financial_threshold` (10 filas: 4 UTM + 5 glosa% + UTM_VALUE). `_get_utm_value()`, `_check_utm_threshold()`. CLAUDE.md §Rules 34-35]

## Ciclo presupuestario

| Período | Fase |
|---------|------|
| T-1 (Jul-Dic) | Formulación |
| T (Ene-Dic) | Ejecución (4 trimestres) |
| T+1 (Ene-Jun) | Rendición y auditoría |

Fases del ciclo:

Formulación → Aprobación → Ejecución → Modificaciones → Control → Cierre

[impl: `core.budget_cycle_milestone` (17 seed) + `core.budget_cycle_tracking`. 5 endpoints `/presupuesto/ciclo/*`. CLAUDE.md §Rule 43]

## Modificaciones presupuestarias

Aumentos ≤ 10% del costo aprobado NO requieren nueva aprobación CORE (Glosa 10/11).

Traspaso permitido desde cualquier Subtítulo/Ítem de inversión regional a:

- Subtítulos 24, 26, 29, 31, 33, 34.07
- Subtítulo 32.06

[ver glosas detalladas](urn:gnub:kb:ssot-legal)
```

- [ ] **Step 2: Commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add knowledge/domains/gn/01_fundamentos/ssot/ssot-presupuesto.md
git commit -m "feat(ssot): add ssot-presupuesto — 6-level classifier, thresholds, budget cycle"
```

---

### Task 7: Create ssot-convenios.md

**Files:**
- Create: `knowledge/domains/gn/01_fundamentos/ssot/ssot-convenios.md`

**Reconciliation data** (finding B-03):
- ReferenceData.ttl: 5 states
- ApprovalData.ttl: 7 states
- GORE_OS: 13 states

- [ ] **Step 1: Write ssot-convenios.md**

```markdown
---
_manifest:
  urn: "urn:gnub:kb:ssot-convenios"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "goreNubleApprovalData.ttl, goreNubleReferenceData.ttl, omega_gore_nuble_mermaid.md v2.6.0"
version: "1.0.0"
status: draft
tags: [ssot, convenios, acuerdos, estados, cuotas, transferencias]
lang: es
extensions:
  gnub:
    family: ssot
    bundle: "urn:gnub:kb:ssot-master"
---

# SSOT — Convenios GORE Ñuble

## Resumen

6 tipos de convenio, 7 estados canónicos ontológicos + 6 refinamientos GORE_OS (13 total). Cuotas e instalments inline. Art. 18: verificación de rendiciones antes de nuevas transferencias.

## Tipos de convenio (6)

| Código | Tipo |
|--------|------|
| TRANS | Convenio de Transferencia |
| MAND | Convenio Mandato |
| PROG | Convenio de Programación |
| MARCO | Convenio Marco |
| COLAB | Convenio de Colaboración |
| INTER | Convenio Interinstitucional |

Consistente entre ReferenceData.ttl y GORE_OS `agreement_type` scheme (6 valores).

## Estados de convenio

### Estados ontológicos (7)

| Seq | Estado | Descripción |
|-----|--------|-------------|
| 1 | Borrador | Elaboración inicial por división técnica |
| 2 | En Revisión Jurídica | Asesoría Jurídica verifica legalidad |
| 3 | En Revisión Financiera | DAF verifica cláusulas financieras |
| 4 | Visado Internamente | Aprobación interna completa |
| 5 | Firmado | Firma bilateral (GORE + contraparte) |
| 6 | Toma de Razón Pendiente | En trámite CGR |
| 7 | Formalizado (Tramitado) | Toma de Razón obtenida, vigente |

#### Proveniencia

ApprovalData.ttl: 7 estados secuenciados (agrega En Revisión Jurídica y En Revisión Financiera). ReferenceData.ttl: 5 estados (Draft, Reviewed, Signed, TdR, Formalized) — menos granular. Canónico: 7 per ApprovalData (mayor granularidad del flujo interno).

### Refinamientos GORE_OS (6 adicionales)

| Estado | Función |
|--------|---------|
| EN_NEGOCIACION | Entre Borrador y Revisión Jurídica — negociación con contraparte |
| FIRMADO_GORE | Firma unilateral GORE (antes de firma contraparte) |
| FIRMADO_CONTRAPARTE | Firma contraparte (antes de TdR) |
| VIGENTE | Post-formalización, durante período de vigencia |
| VENCIDO | Plazo cumplido sin renovación |
| TERMINADO | Cumplimiento total o resciliación |
| RESCILIADO | Término anticipado por acuerdo de partes |
| TDR_PENDIENTE | Alias de Toma de Razón Pendiente |

Estos estados son extensiones de implementación sin respaldo ontológico. GORE_OS total: 13 estados. [impl: `agreement_state` scheme, FSM en `convenios.py`. CLAUDE.md §Rule 5]

## Cuotas (installments)

Per convenio de transferencia. Inline CRUD en drawer.

- `POST /api/convenios/{id}/cuotas` — requiere `installment_number`, `amount`, `due_date`, `payment_status_id`
- `POST /api/convenios/{id}/cuotas/bulk` — `BulkCuotaRequest(total_amount, num_installments, start_date, frequency_months=1)`

[impl: CLAUDE.md §Rules 26-27]

## Verificación Art. 18

Antes de transferir nueva cuota: verificar que la entidad ejecutora no tenga rendiciones pendientes.

[ver rendiciones](urn:gnub:kb:ssot-rendiciones)
```

- [ ] **Step 2: Commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add knowledge/domains/gn/01_fundamentos/ssot/ssot-convenios.md
git commit -m "feat(ssot): add ssot-convenios — 6 types, 7+6 states, installments"
```

---

### Task 8: Create ssot-rendiciones.md

**Files:**
- Create: `knowledge/domains/gn/01_fundamentos/ssot/ssot-rendiciones.md`

**Reconciliation data** (findings B-02, B-08):
- RenditionData.ttl: 6 RenditionState
- ReferenceData.ttl: 5 AccountabilityState
- GORE_OS: 8 states + 8-phase CGR

- [ ] **Step 1: Write ssot-rendiciones.md**

```markdown
---
_manifest:
  urn: "urn:gnub:kb:ssot-rendiciones"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "goreNubleRenditionData.ttl, goreNubleReferenceData.ttl, omega_gore_nuble_mermaid.md v2.6.0"
version: "1.0.0"
status: draft
tags: [ssot, rendiciones, sisrec, cgr, sla, estados]
lang: es
extensions:
  gnub:
    family: ssot
    bundle: "urn:gnub:kb:ssot-master"
---

# SSOT — Rendiciones SISREC

## Resumen

Sistema de rendición de cuentas. 6 estados canónicos ontológicos, 5 roles SISREC, SLAs definidos en implementación. 8-phase CGR en GORE_OS. Flujo: Ejecutor presenta → RTF revisa → Jefe DAF visa → UCR contabiliza.

## Estados canónicos (6)

| Seq | Estado | Descripción |
|-----|--------|-------------|
| 1 | Pendiente | No presentada por entidad ejecutora |
| 2 | En Revisión | Recibida, en revisión por RTF/Analista Otorgante |
| 3 | Observada | Devuelta para subsanación |
| 4 | Aprobada Parcialmente | Aprobada con transacciones observadas |
| 5 | Aprobada Totalmente | Aprobada en totalidad, firmada con FEA |
| 6 | Contabilizada | Registrada en SIGFE, archivada por UCR/DAF |

#### Proveniencia

Canónico: RenditionData.ttl (6 estados `gnub:RenditionState`), más granular.

Descartado: ReferenceData.ttl (5 `gnub:AccountabilityState`: Pending, InReview, Observed, Approved, Rejected). Clases `RenditionState` y `AccountabilityState` duplicadas en TBox (`goreNubleOntology.ttl`) con definiciones virtualmente idénticas sin `owl:equivalentClass`. Pendiente: deprecar `AccountabilityState` en ontología.

Diferencias clave: RenditionData distingue Aprobada Parcial vs Total (la realidad CGR). ReferenceData solo tiene "Approved" genérico y agrega "Rejected" que RenditionData no incluye.

### Refinamientos GORE_OS (2 adicionales)

GORE_OS implementa 8 estados:

| Estado GORE_OS | Mapeo ontológico |
|----------------|-----------------|
| PENDIENTE | Pendiente |
| EN_REVISION_RTF | En Revisión (split fase RTF) |
| VISADA_RTF | — (estado intermedio GORE_OS) |
| EN_REVISION_UCR | — (estado intermedio GORE_OS) |
| OBSERVADA | Observada |
| APROBADA | Aprobada Totalmente |
| RECHAZADA | — (de ReferenceData, no en RenditionData) |
| Archivada | Contabilizada (vía `archived_at`) |

GORE_OS granulariza "En Revisión" en 3 fases (RTF → VISADA_RTF → UCR) y agrega RECHAZADA. La ontología no distingue estas subfases.

## Roles SISREC (5)

| Rol | Entidad | Función |
|-----|---------|---------|
| Analista Ejecutor | Ejecutora | Crea y registra transacciones en SISREC |
| Ministro de Fe | Ejecutora | Certifica autenticidad de documentos digitalizados |
| Encargado Ejecutor | Ejecutora | Representante legal, firma con FEA, envía al GORE |
| Analista Otorgante (RTF) | GORE | Referente Técnico-Financiero, revisa/aprueba/observa |
| Encargado Otorgante (Jefe DAF) | GORE | Jefatura DAF, firma Informe de Aprobación con FEA |

## SLAs

Definidos en GORE_OS (no en ontología).

| Etapa | Plazo | Responsable |
|-------|-------|-------------|
| Presentación rendición | 15 del mes siguiente | Entidad Ejecutora |
| Revisión técnica (RTF) | 7 días hábiles | Analista Otorgante |
| Devolución por observación | 1 día | Jefe DAF |
| Contabilización | 2 días | UCR/DAF |
| Resubsanación (OBSERVADA) | 15 días | Entidad Ejecutora |

Meta CGR: 14 días totales.

[impl: SLAs en `ipr.py`. `phase_entered_at` para cálculo SLA-accurate. `core.rendition_phase` (8 seed). Escalation: `core.rendition_escalation` (3 niveles: 1x, 1.5x, 2x SLA). CLAUDE.md §Rule 44]

## Normas aplicables

- Art. 18 Res. 30 CGR: no transferir nuevos fondos si rendiciones pendientes
- Art. 31 Res. 30 CGR: obligación de restitución
- Res. Ex. 1858/2023 CGR: SISREC obligatorio para Subtítulos 24 y 33
```

- [ ] **Step 2: Commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add knowledge/domains/gn/01_fundamentos/ssot/ssot-rendiciones.md
git commit -m "feat(ssot): add ssot-rendiciones — 6 canonical states, 5 SISREC roles, SLAs"
```

---

## Chunk 4: Actos Admin + DGI

### Task 9: Create ssot-actos-admin.md

**Files:**
- Create: `knowledge/domains/gn/01_fundamentos/ssot/ssot-actos-admin.md`

- [ ] **Step 1: Write ssot-actos-admin.md**

```markdown
---
_manifest:
  urn: "urn:gnub:kb:ssot-actos-admin"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "goreNubleApprovalData.ttl, goreNubleDipirOntology.ttl, goreNubleDipirRules.ttl, omega_gore_nuble_mermaid.md v2.6.0"
version: "1.0.0"
status: draft
tags: [ssot, actos-administrativos, aprobacion, visacion, toma-razon, decretos]
lang: es
extensions:
  gnub:
    family: ssot
    bundle: "urn:gnub:kb:ssot-master"
---

# SSOT — Actos administrativos

## Resumen

3 tipos de acto administrativo, 8 etapas de aprobación canónicas, reglas de exención por umbral UTM. Flujo DIPIR modelado con 3 eventos ontológicos (Visación, Aprobación, Toma de Razón).

## Tipos de acto

| Tipo | Sujeto a TdR | Subtipos |
|------|--------------|----------|
| Decreto | Sí | — |
| Resolución | Depende del monto | Exenta, Afecta |
| Oficio | No | — |

GORE_OS agrega DECRETO_ALCALDICIO — gap ontológico, no presente en ningún TTL.

[impl: `core.administrative_act`. Tipos: DECRETO, RESOLUCION, DECRETO_ALCALDICIO. CLAUDE.md §Rule 13]

#### Proveniencia

ApprovalData.ttl define 3 subtipos documentales (Resolución Exenta, Resolución Afecta, Oficio). Ontología NO modela DECRETO_ALCALDICIO. GORE_OS lo implementa para actos de municipios en convenios de mandato. Pendiente: agregar a ontología.

## Etapas de aprobación (8)

| Seq | Etapa | Actor |
|-----|-------|-------|
| 1 | Elaboración (Borrador) | Unidad competente |
| 2 | V.B. Jurídico | Asesoría Jurídica |
| 3 | V.B. Control | Unidad de Control |
| 4 | V.B. Jefatura División | Jefe/a de División |
| 5 | V.B. Administrador/a Regional | Administrador/a Regional |
| 6 | Firma Gobernador/a (FEA) | Gobernador/a Regional |
| 7 | Toma de Razón CGR | Contraloría General |
| 8 | Notificación y Archivo | Oficina de Partes |

#### Proveniencia

Canónico: ApprovalData.ttl (8 etapas secuenciadas). Omega describe 7 pasos para Resolución Exenta (sin distinguir VB Jurídico / VB Control / VB Jefatura como etapas separadas). GORE_OS implementa 7-step FSM (BORRADOR→EN_REVISION→VISADO→FIRMADO→ENVIADO_CGR→OBSERVADO/TOMADO_RAZON + ANULADO cross-cutting) — agrupa V.B. Jurídico+Control+Jefatura+Administrador en "EN_REVISION→VISADO".

### Mapeo GORE_OS

| Ontología (8 etapas) | GORE_OS (7 steps) |
|----------------------|-------------------|
| 1. Elaboración | BORRADOR |
| 2-4. VB Jurídico + Control + Jefatura | EN_REVISION |
| 5. VB Administrador | VISADO |
| 6. Firma Gobernador | FIRMADO |
| 7. Toma de Razón CGR | ENVIADO_CGR → TOMADO_RAZON / OBSERVADO |
| 8. Notificación | (post-TOMADO_RAZON, no modelado como estado) |
| — | ANULADO (cross-cutting, cualquier punto) |

## Eventos DIPIR (ontología)

3 clases de evento en `goreNubleDipirOntology.ttl`:

| Evento | Superclase | Descripción |
|--------|-----------|-------------|
| VisaciónEvent | gist:Event | Actor valida documento antes de aprobación final |
| AprobacionEvent | gist:Event | Aprobación definitiva (firma/autorización). Típicamente Gobernador/a |
| TomaRazonEvent | gist:Event | Control de legalidad CGR. Solo Resoluciones Afectas y Decretos |

Propiedades: `dipir:approvesAct` (AprobacionEvent → AdministrativeAct), `dipir:visatesAct` (VisaciónEvent → AdministrativeAct). Ambas subproperties de `gist:affects`.

## Regla de exención Toma de Razón

| Parámetro | Valor |
|-----------|-------|
| Umbral | Variable por región/año (5.000-7.000 UTM según DipirRules.ttl) |
| Operador | Menor que (<) |
| Aplica a | Resoluciones |
| Base legal | Res. 7/2019 CGR |
| Vigencia | Desde 2019-03-26 |

Para GORE Ñuble, umbral operativo: 2.500 UTM (Omega).

[impl: Track enforcement via `_check_track_amount_gates()`. `cgr_res30_utm` en JSONB de `core.financing_track`. CLAUDE.md §Rule 34]

## Operadores de comparación (ontología)

5 instancias de `ComparisonOperator` en DipirRules.ttl: `<`, `<=`, `>`, `>=`, `=`. Usados en `ExemptionRule` (subClass `gist:Specification`) para definir condiciones de exención.
```

- [ ] **Step 2: Commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add knowledge/domains/gn/01_fundamentos/ssot/ssot-actos-admin.md
git commit -m "feat(ssot): add ssot-actos-admin — 3 types, 8 approval stages, exemption rules"
```

---

### Task 10: Create ssot-dgi.md

**Files:**
- Create: `knowledge/domains/gn/01_fundamentos/ssot/ssot-dgi.md`

- [ ] **Step 1: Write ssot-dgi.md**

```markdown
---
_manifest:
  urn: "urn:gnub:kb:ssot-dgi"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "goreNubleOntology.ttl, omega_gore_nuble_mermaid.md v2.6.0, goreNubleCQs_Master.yml"
version: "1.0.0"
status: draft
tags: [ssot, dgi, indicadores, iniciativas, reportes, senales]
lang: es
extensions:
  gnub:
    family: ssot
    bundle: "urn:gnub:kb:ssot-master"
---

# SSOT — DGI (Gestión Institucional)

## Resumen

Departamento de Gestión Institucional — unidad de staff del Administrador Regional. Gestiona indicadores, iniciativas de mejora, reportes y cartera IPR con señal de salud. Dominio mayoritariamente definido en GORE_OS; la ontología y el Omega proveen solo la estructura organizacional.

## Posición orgánica

DGI es `gnub:StaffUnit` (no División ni Departamento). Depende del Administrador/a Regional. Contiene OIRS como `gnub:Unit` hija.

[ver detalle](urn:gnub:kb:ssot-organica)

## Roles DGI (4)

| Rol | system_role_id | Función |
|-----|---------------|---------|
| JEFE_DGI | 5 | Liderazgo estratégico, supervisión indicadores |
| ESP_CONTROL_GESTION | 6 | Control de gestión, indicadores, cockpit |
| ESP_PROCESOS | 7 | Procesos institucionales, BPMN, DMAIC |
| ESP_TD | 8 | Transformación Digital del Estado |

Population: `"dgi"`. Routing: sidebar DGI (7 ítems) + dashboard DGI cockpit.

[impl: CLAUDE.md §Rules 11, 23]

## Indicadores (5 dimensiones × 3 señales)

| Dimensión | Qué mide | Refresh |
|-----------|---------|---------|
| PRESUPUESTO | Ejecución presupuestaria agregada | Automático |
| CARTERA_IPR | Estado de salud del portafolio IPR | Automático |
| CONVENIOS | Cumplimiento de plazos y estados | Automático |
| TDE | Avance Transformación Digital | Estático (manual) |
| RIESGOS | Alertas y problemas activos | Automático |

Señales: VERDE (normal), AMARILLO (atención), ROJO (crítico).

`POST /api/dgi/data/indicators/refresh` — idempotente, refresca 4/5 dimensiones (TDE estático).

[impl: `ref.category` schemes: `dgi_indicator_dimension`, `dgi_signal`. CLAUDE.md §DGI Layer]

## Iniciativas de mejora

Kanban con WIP limits server-side:

| Columna | WIP máximo |
|---------|-----------|
| EN_CURSO | 5 |
| REVISION | 2 |

`POST /api/dgi/initiatives/{id}/move` → 409 si límite excedido.

Paginación opcional: con `?page=1&page_size=N` → respuesta paginada. Sin parámetros → array plano (Kanban depende de esto).

[impl: CLAUDE.md §Rule 11 — NUNCA cambiar default de paginación]

## Reportes (4 tipos × 6 secciones)

| Tipo | Frecuencia |
|------|-----------|
| FLASH | Ad-hoc |
| SEMANAL | Semanal |
| MENSUAL | Mensual |
| TEMATICO | Por tema |

6 secciones auto-populated: resumen, tabla_indicadores, alertas, avance_dgi, decisiones, prioridades.

Edición de secciones: atomic `jsonb_set` en `metadata` (no read-modify-write). Contenido auto-populated se regenera en cada GET; solo ediciones usuario persisten.

[impl: CLAUDE.md §Rule 21]

## Cartera IPR (portafolio DGI)

Vista unificada de todas las IPR con datos agregados + señal de salud:

| Señal | Significado |
|-------|------------|
| VERDE | Sin problemas |
| AMARILLO | Requiere atención |
| ROJO | Crítico |

Calculada por `_compute_health_signal()`.

3 endpoints: `GET /dgi/cartera` (paginada, post-filter), `GET /dgi/cartera/resumen`, `GET /dgi/cartera/cuotas-vencidas`.

Cockpit drill-down: `/cartera?health_signal=ROJO`.

[impl: CLAUDE.md §DGI Layer — dgi_cartera]

## Esquemas DGI en ref.category

11 schemes: `dgi_initiative_status`, `dgi_indicator_dimension`, `dgi_signal`, `dgi_report_type`, `dgi_report_status`, `dgi_bpmn_status`, `dgi_dmaic_phase`, `dgi_session_status`, `dgi_alert_status`, `dgi_decree_status`, `dgi_source_status`.

Estos schemes NO están en `goreos_seed.sql` — solo en `goreos_model`, copiados a `goreos_test` via COPY.
```

- [ ] **Step 2: Commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add knowledge/domains/gn/01_fundamentos/ssot/ssot-dgi.md
git commit -m "feat(ssot): add ssot-dgi — indicators, initiatives, reports, cartera"
```

---

## Chunk 5: Validation + Catalog Update

### Task 11: Bundle validation

- [ ] **Step 1: Verify all 10 files exist**

```bash
ls -la /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/
# Expected: 10 .md files
```

- [ ] **Step 2: Check no heading depth > ####**

```bash
grep -rn "^#####" /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/
# Expected: no output
```

- [ ] **Step 3: Check all frontmatters have required fields**

```bash
for f in /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/*.md; do
  echo "=== $(basename $f) ==="
  head -12 "$f" | grep -E "urn:|version:|status:|tags:|lang:"
  echo ""
done
```

- [ ] **Step 4: Check no truncated headings**

```bash
grep -rn '\.\.\.' /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/*.md | grep "^#"
# Expected: no output
```

- [ ] **Step 5: Check inter-satellite references resolve**

```bash
grep -roh "urn:gnub:kb:ssot-[a-z-]*" /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/*.md | sort -u
# Should list only URNs that correspond to actual files
```

- [ ] **Step 6: Line count per file (volume check)**

```bash
wc -l /Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/01_fundamentos/ssot/*.md
# Expected: total ~3000-4500 lines
```

### Task 12: Update catalog (if applicable)

- [ ] **Step 1: Check if catalog_master_gorenuble.yml exists and needs updating**

```bash
ls /Users/felixsanhueza/Developer/gorenuble/knowledge/**/catalog_master*.yml 2>/dev/null
```

- [ ] **Step 2: Add SSOT entries to catalog if it exists**

Add 10 entries (1 master + 9 satellites) to the catalog with URNs, paths and tags.

- [ ] **Step 3: Final commit**

```bash
cd /Users/felixsanhueza/Developer/gorenuble
git add -A knowledge/domains/gn/01_fundamentos/ssot/
git commit -m "feat(ssot): complete SSOT GORE Ñuble bundle v1.0.0 — 10 KORA/MD artifacts"
```
