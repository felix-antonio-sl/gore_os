# SSOT GORE Ñuble — Design Spec

## Contexto

La auditoría de consistencia v2.0 entre las 4 capas documentales del dominio GORE Ñuble reveló ~15 conflictos entre fuentes. Se requiere un documento SSOT que reconcilie las inconsistencias y sirva como referencia canónica.

### Fuentes y jerarquía de autoridad

| Prioridad | Fuente | Naturaleza |
|-----------|--------|------------|
| 1 (máxima) | Organigrama GORE 2026 | Acto administrativo legal |
| 2 | Ontología goreNubleBundle (12 TTL) | Modelo formal OWL/SKOS |
| 3 | Omega Mermaid v2.6.0 | Modelo de referencia descriptivo |
| 4 (mínima) | CQs Master (472 CQs) | Preguntas de competencia |

### Consumidores

- Primario: agentes KODA / pipelines RAG
- Secundario: diseño e implementación de GORE_OS (`/Users/felixsanhueza/Developer/goreos`)

## Decisiones de diseño

### Formato: KORA/MD v6.1.0

Artefactos Markdown con frontmatter YAML tripartito. Escritura telegráfica (reglas T1-T7), FS=100%, CR>1.5, sin grasa.

### Estructura: master + 9 satélites

Bundle de 10 artefactos KORA/MD con versionado independiente. El master coordina, indexa y desambigua; los satélites contienen hechos de dominio.

### Enfoque: hechos canónicos + proveniencia inline

Cada satélite documenta los hechos reconciliados como contenido principal. Secciones con conflicto incluyen `#### Proveniencia` telegráfico que documenta fuente autoritativa y qué se descartó.

### Relación con fuentes: vista reconciliada, fuentes vivas

Las fuentes originales mantienen su ciclo de vida propio. El SSOT es la capa de reconciliación — un "compiled view" que se actualiza cuando una fuente cambia. No depreca ni reemplaza las fuentes.

### Ubicación

```
knowledge/domains/gn/01_fundamentos/ssot/
```

En el monorepo `gorenuble`, junto al Omega Mermaid, señalando carácter fundacional.

## Arquitectura del bundle

```
knowledge/domains/gn/01_fundamentos/ssot/
├── ssot-master.md                 urn:gnub:kb:ssot-master
├── ssot-organica.md               urn:gnub:kb:ssot-organica
├── ssot-ipr-lifecycle.md          urn:gnub:kb:ssot-ipr-lifecycle
├── ssot-presupuesto.md            urn:gnub:kb:ssot-presupuesto
├── ssot-convenios.md              urn:gnub:kb:ssot-convenios
├── ssot-rendiciones.md            urn:gnub:kb:ssot-rendiciones
├── ssot-actos-admin.md            urn:gnub:kb:ssot-actos-admin
├── ssot-territorio.md             urn:gnub:kb:ssot-territorio
├── ssot-dgi.md                    urn:gnub:kb:ssot-dgi
└── ssot-legal.md                  urn:gnub:kb:ssot-legal
```

### Reglas del bundle

- Cada archivo es un artefacto KORA/MD v6.1.0 independiente con frontmatter propio
- Versionado independiente por satélite
- Master lleva versión de bundle (bumps al agregar/eliminar satélite)
- Jerarquía de autoridad fija: Organigrama > Ontología > Omega > CQs
- Fuentes originales mantienen su ciclo de vida propio

### Convenciones de referencia

- Inter-satélite: `[ver Rendiciones](urn:gnub:kb:ssot-rendiciones)`
- A fuente: `[fuente: ReferenceData.ttl]` en bloques de proveniencia
- A GORE_OS: `[impl: CLAUDE.md §Rule N]` cuando hay impacto en implementación

## Estructura interna: master

| Sección (`##`) | Contenido | Rol RAG |
|----------------|-----------|---------|
| Jerarquía de autoridad | 4 fuentes con peso relativo y criterio de resolución | Agente sabe cómo resolver conflictos futuros |
| Mapa de artefactos | Tabla: URN, título, fuentes primarias, versión, status | Índice para navegación y discovery |
| Glosario de reconciliación | ~15-20 términos donde las fuentes difieren | Desambiguación terminológica canónica |
| Conflictos transversales | Hallazgos que cruzan múltiples satélites | Contexto arquitectónico para agentes |
| Alineación GORE_OS | Tabla cruzada: concepto canónico → tabla/endpoint/componente | Puente knowledge base → codebase |

El master no contiene hechos de dominio — solo coordina, indexa y desambigua.

## Estructura interna: satélites

### Frontmatter

```yaml
---
_manifest:
  urn: "urn:gnub:kb:ssot-{domain}"
  provenance:
    created_by: "FS"
    created_at: "2026-03-10"
    source: "{fuentes primarias del satélite}"
version: "1.0.0"
status: draft
tags: [ssot, {domain-tags}]
lang: es
extensions:
  gnub:
    family: ssot
    bundle: "urn:gnub:kb:ssot-master"
---
```

### Patrón de secciones

```markdown
# SSOT — {Título del dominio}

## Resumen
[2-3 líneas: qué cubre, cuántas entidades canónicas]

## {Tema principal}
[Hechos canónicos — tablas para catálogos, listas para procedimientos]

#### Proveniencia
[Solo si hubo conflicto — fuente elegida, descarte, justificación]
```

### Reglas para todos los satélites

| Regla | Descripción |
|-------|-------------|
| Chunk autónomo | Cada `##` legible sin contexto externo |
| Proveniencia condicional | `#### Proveniencia` solo donde hubo conflicto |
| Tablas para catálogos | Enumeraciones siempre como tabla |
| Enlace impl | `[impl: ...]` cuando impacta GORE_OS |
| Sin duplicación | Un hecho en un solo satélite, cross-ref vía URN |
| Telegráfico | Reglas T1-T7 de KORA/MD §5.4, FS=100% |

## Mapa de reconciliaciones por satélite

| Satélite | Conflictos clave | Decisión canónica |
|----------|-----------------|-------------------|
| organica | DIT vs DIINF; DGI Depto vs StaffUnit; CDR/CTCI ausentes en organigrama | DIINF (ontología); StaffUnit (ontología); CDR/CTCI canónicos (ontología + CQs) |
| ipr-lifecycle | 6 vs 8 fases; nombres divergentes | 6 fases MCD; F6/F7 reclasificados como estados operativos |
| presupuesto | FundingSource 7 vs 8; FRPD unificado vs split | LegalData autoridad; FRPD split es detalle operativo |
| convenios | 5 vs 7 vs 13 estados | ApprovalData (7) base ontológica; 6 adicionales son refinamiento GORE_OS |
| rendiciones | RenditionState vs AccountabilityState; clases duplicadas | RenditionData canónico; AccountabilityState deprecated |
| actos-admin | 8 vs 7 etapas; sin DECRETO_ALCALDICIO | ApprovalData (8) canónico; DECRETO_ALCALDICIO como gap |
| territorio | Estable entre fuentes | OrgData.ttl canónico; tipos impacto como extensión GORE_OS |
| dgi | Coherente entre fuentes | Catálogo canónico de dimensiones × señales |
| legal | Glosas cubiertas; CQs con artículos sin ancla | LegalData canónico; mapear CQs a artículos |

## Estimación de volumen

| Categoría | Satélites | Líneas estimadas |
|-----------|-----------|-----------------|
| Master | ssot-master | 300-400 |
| Grandes | organica, ipr-lifecycle, presupuesto | 400-600 c/u |
| Medianos | convenios, rendiciones, actos-admin | 200-400 c/u |
| Pequeños | territorio, dgi, legal | 150-250 c/u |
| **Total bundle** | **10 artefactos** | **~3,000-4,500** |
