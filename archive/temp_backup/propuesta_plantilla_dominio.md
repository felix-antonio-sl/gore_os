# Plantilla editorial única para documentos de dominio (propuesta)

## Objetivo

- **Consistencia**: todos los dominios se leen igual (misma “ruta mental”).
- **Auditabilidad**: trazabilidad clara (versionado, owners, normativa, KPIs).
- **Machine-friendly**: tablas/IDs estables para que después sea exportable a catálogos.

---

## Convenciones globales (norma editorial)

### 1) Encabezados y jerarquía

- **H1**: `# D-XXX — Nombre del Dominio`
- **H2**: secciones estándar (ver abajo).
- **H3**: submódulos/procesos dentro de una sección.
- **Regla**: no más de **H3** (evita árboles profundos).

### 2) Emojis (sí, pero controlados)

- **Regla**: *máximo 1 emoji por título H2* y siempre el mismo set (evita “ruido”).
- **Propuesta de set fijo**:
  - `🧭` Resumen
  - `🎯` Alcance
  - `🧠` Modelo Conceptual
  - `🧬` Genotipo Categorial (Modelo de Datos Formal)
  - `🗺️` Mapa del dominio
  - `🧩` Módulos / capacidades
  - `🔄` Procesos (BPMN)
  - `👥` Roles y actores
  - `🔌` Sistemas e integraciones
  - `⚖️` Normativa aplicable
  - `🧪` Historias de usuario (resumen)
  - `🔗` Matriz de trazabilidad
  - `📈` Indicadores (KPIs)
  - `🤝` Referencias cruzadas (dominios)
  - `📝` Changelog / estado editorial

### 3) Estilo de IDs y términos

- **IDs en monospace**: usar backticks para `D-XXX`, `US-...`, `SYS-...`, entidades `ExpedienteElectronico`, etc.
- **Siglas**: primera aparición expandida + sigla (`Expediente Electrónico (EE)`), luego solo sigla.
- **Regla anti-alias**: una entidad = **un nombre canónico**; alias solo en “Diccionario”.

### 4) Tablas (para que nunca se rompan)

- **Regla**: *sin saltos de línea dentro de celdas*.
- **Regla**: columnas estables por tipo de tabla (módulos, procesos, KPIs, etc.).
- **Regla**: IDs siempre en columna propia, en monospace.
- **Regla**: si una celda queda larga, mover detalle a bullets bajo la tabla (“Notas”).

### 5) Diagramas

- **Mermaid** permitido, pero con convención:
  - `flowchart LR` para mapas.
  - `flowchart TD` para decisiones.
- **BPMN**: si se referencia, exigir **índice** con links/IDs (aunque el diagrama viva fuera).

---

## Secciones estándar (orden recomendado)

- **Obligatorias**:
  1) Resumen ejecutivo  
  2) Alcance (qué cubre / qué NO cubre)
  3) Modelo Conceptual (Ontología, Definiciones)
  4) Genotipo Categorial (Objetos, Morfismos, Invariantes)
  5) Mapa del dominio (contexto + interfaces)  
  6) Módulos/capacidades  
  7) Procesos (índice BPMN)  
  8) Roles y actores  
  9) Sistemas e integraciones  
  10) Normativa aplicable  
  11) Historias de usuario (resumen + link a catálogo si existe)  
  12) Matriz de trazabilidad  
  13) Indicadores (KPIs)  
  14) Referencias cruzadas  
  15) Changelog / estado editorial + footer

- **Opcionales** (solo si aplica):
  - Riesgos y controles
  - Decisiones arquitectónicas del dominio (si no hay doc aparte)
  - Reglas de negocio clave (si no están en specs)

---

## Plantilla (copiable)

```markdown
---
domain_id: D-XXX
domain_name: "Nombre del Dominio"
blueprint_release: "5.2"
domain_version: "5.2"
status: "draft|consolidated"
last_update: "YYYY-MM-DD"
owners:
  - role: "Owner funcional"
    org_unit: "..."
  - role: "Owner técnico"
    org_unit: "..."
---

# D-XXX — Nombre del Dominio

## 🧭 1. Resumen Ejecutivo
- **Propósito**:
- **Resultado principal** (qué “entrega” el dominio):
- **Usuarios/beneficiarios**:
- **Interfaces críticas** (2-5 bullets):

## 🎯 2. Alcance
### 2.1 Qué cubre
- **Incluye**:
### 2.2 Qué NO cubre
- **Excluye** (y a qué dominio se deriva):

## 🧠 3. Modelo Conceptual (Ontología)
> Definición abstracta de los conceptos y relaciones (Genoma Humano).

### 3.1 Diccionario de Conceptos
- **Concepto A**: Definición...
- **Concepto B**: Definición...

### 3.2 Diagrama Conceptual (Mermaid Class/ERD)
Logic pura, sin detalles de implementación.

## 🧬 4. Genotipo Categorial (Modelo de Datos Formal)
> Especificación Matemática para el Desarrollo (Genoma Técnico).
> **Source of Truth** para `drizzle/schema.ts` y `xstate/machines`.

### 4.1 Objetos (Entidades) $A \in Ob(C_{dom})$
| Objeto (Entity) | Definición Formal (Tipo)  | Invariante (Regla) | Source |
| --------------- | ------------------------- | ------------------ | ------ |
| `EntityX`       | `struct { id: UUID, ...}` | `INV_01: x > 0`    | D-XXX  |

### 4.2 Morfismos (Relaciones/Procesos) $f: A \to B$
| Morfismo (Func) | Dominio $\to$ Codominio | Tipo  | Implementación      |
| --------------- | ----------------------- | ----- | ------------------- |
| `relacion_r1`   | `EntA` $\to$ `EntB`     | FK    | `drizzle.relation`  |
| `proceso_p1`    | `StateA` $\to$ `StateB` | State | `xstate.transition` |
| `calculo_c1`    | `DataA` $\to$ `DataB`   | Map   | `effect.function`   |

### 4.3 Ecuaciones y Restricciones (Paths)
- **EQ1**: `f ; g = h` (El camino f seguido de g equivale a h).
- **INV1**: Regla de negocio inmutable.

## 🗺️ 5. Mapa del Dominio

flowchart LR
  %% Contexto + entradas/salidas con otros dominios

- **Contratos** (eventos/datos mínimos intercambiados):  
  - `D-AAA` → `D-XXX`: ...
  - `D-XXX` → `D-BBB`: ...

## 🧩 4. Módulos / Capacidades

| Código | Módulo | Objetivo | Entradas | Salidas | Owner |
| ------ | ------ | -------- | -------- | ------- | ----- |
| M1     | ...    | ...      | ...      | ...     | ...   |

## 🔄 5. Procesos (Índice BPMN)

| ID Proceso | Nombre | Trigger | Output | BPMN/Link |
| ---------- | ------ | ------- | ------ | --------- |
| P1         | ...    | ...     | ...    | ...       |

## 👥 6. Roles y Actores

| Rol | Responsabilidad | Decisiones | US relacionadas |
| --- | --------------- | ---------- | --------------- |
| ... | ...             | ...        | `US-...`        |

## 🗃️ 7. Entidades de Datos

| Entidad (canónica) | Atributos clave | Relaciones   | Owner   |
| ------------------ | --------------- | ------------ | ------- |
| `EntidadX`         | ...             | → `EntidadY` | `D-XXX` |

## 🔌 8. Sistemas e Integraciones

| Código    | Sistema | Tipo (Interno/Externo) | Rol | Dominio |
| --------- | ------- | ---------------------- | --- | ------- |
| `SYS-...` | ...     | ...                    | ... | `D-XXX` |

## ⚖️ 9. Normativa Aplicable

| Norma | Artículos | Obligación | Impacto en el dominio |
| ----- | --------- | ---------- | --------------------- |
| ...   | ...       | ...        | ...                   |

## 🧪 10. Historias de Usuario (Resumen)
>
> Catálogo completo: `../user-stories/kb_goreos_us_d-xxx.yml` (si aplica)

| ID           | Título | Prioridad | Actor |
| ------------ | ------ | --------- | ----- |
| `US-XXX-...` | ...    | ...       | ...   |

## 🔗 11. Matriz de Trazabilidad

| Proceso | Fase | US       | Entidades              |
| ------- | ---- | -------- | ---------------------- |
| P1      | ...  | `US-...` | `EntidadX`, `EntidadY` |

## 📈 12. Indicadores (KPIs)

| KPI | Definición | Fórmula | Meta | Fuente |
| --- | ---------- | ------- | ---- | ------ |
| ... | ...        | ...     | ...  | ...    |

## 🤝 13. Referencias Cruzadas

| Dominio | Relación | Entidades compartidas (canónicas) |
| ------- | -------- | --------------------------------- |
| `D-AAA` | ...      | `EntidadX`                        |

## 📝 14. Changelog / Estado editorial

- **Cambios relevantes**:
- **Pendientes**:
- **Riesgos editoriales**:

---
---
*Documento parte de GORE_OS Blueprint Release v5.5 (Categorical Genotype)*  
*Última actualización: YYYY-MM-DD*

```

---

## Checklist rápido (QA editorial)
- **Versionado**: `blueprint_release` y footer alineados.
- **Tablas**: sin celdas multi-línea; pipes bien formados.
- **IDs**: `D-XXX`, `US-XXX-*`, `SYS-*` siempre en backticks y consistentes.
- **Entidades**: nombre canónico único (sin mezcla ES/EN en cruces).
- **Referencias cruzadas**: con entidad compartida explícita (no solo texto).
