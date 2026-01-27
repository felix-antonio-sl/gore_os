# Análisis de Normalización: GORE_OS v3.0

**Sistema**: GORE_OS - Gestión Institucional para Gobiernos Regionales
**Fecha**: 2026-01-27
**Tablas Analizadas**: 50
**Metodología**: Verificación progresiva 1NF → 2NF → 3NF → BCNF

---

## Resumen Ejecutivo

| Forma Normal | Cumplimiento | Hallazgos |
|--------------|--------------|-----------|
| **1NF** | ⚠️ Parcial | 3 violaciones menores (arrays) |
| **2NF** | ✅ Completo | Sin violaciones (surrogate keys) |
| **3NF** | ✅ Completo | Sin dependencias transitivas |
| **BCNF** | ✅ Completo | Determinantes son candidate keys |

**Veredicto**: El modelo está correctamente normalizado hasta 3NF/BCNF con desnormalizaciones **intencionales y justificadas**.

---

## Análisis por Forma Normal

### 1NF - Primera Forma Normal

**Reglas:**
- Valores atómicos (sin grupos repetitivos)
- Cada celda contiene un solo valor
- Sin arrays o listas embebidas

#### Hallazgos 1NF

| Tabla | Columna | Tipo | Evaluación |
|-------|---------|------|------------|
| `meta.story` | `extra_tags` | `TEXT[]` | ⚠️ Violación técnica |
| `meta.story` | `acceptance_criteria` | `TEXT[]` | ⚠️ Violación técnica |
| `core.work_item` | `tags` | `TEXT[]` | ⚠️ Violación técnica |
| `ref.category` | `valid_transitions` | `JSONB` | ✅ Aceptable (config) |
| `txn.event` | `data` | `JSONB` | ✅ Aceptable (event sourcing) |

#### Análisis de Violaciones 1NF

**1. `meta.story.extra_tags` / `meta.story.acceptance_criteria`**

```sql
-- Actual (violación técnica 1NF)
extra_tags TEXT[],
acceptance_criteria TEXT[]

-- Alternativa normalizada
CREATE TABLE meta.story_tag (
    id UUID PRIMARY KEY,
    story_id UUID REFERENCES meta.story(id),
    tag TEXT NOT NULL,
    UNIQUE(story_id, tag)
);

CREATE TABLE meta.story_acceptance_criterion (
    id UUID PRIMARY KEY,
    story_id UUID REFERENCES meta.story(id),
    criterion TEXT NOT NULL,
    sort_order INTEGER
);
```

**Decisión**: **MANTENER ARRAYS**
- Razón: Los tags son atributos simples de texto sin estructura propia
- Los arrays PostgreSQL tienen soporte nativo e índices GIN
- La complejidad adicional de tablas separadas no aporta valor

**2. `core.work_item.tags`**

```sql
-- Actual
tags TEXT[]

-- Ya existe índice GIN
CREATE INDEX idx_workitem_tags ON core.work_item USING GIN(tags);
```

**Decisión**: **MANTENER ARRAY**
- Razón: Patrón estándar de etiquetado
- Índice GIN permite búsquedas eficientes
- Cardinalidad baja (típicamente <10 tags por ítem)

**3. Campos JSONB**

| Campo | Tabla | Propósito | Justificación |
|-------|-------|-----------|---------------|
| `metadata` | Todas | Extensibilidad | Semi-structured data, no rompe normalización |
| `valid_transitions` | `ref.category` | Máquina de estados | Configuración, no datos operacionales |
| `data` | `txn.event` | Payload evento | Event Sourcing pattern (desnormalización estándar) |

---

### 2NF - Segunda Forma Normal

**Reglas:**
- Cumple 1NF
- Todos los atributos no-clave dependen de la clave completa
- No hay dependencias parciales

#### Estrategia de Claves en GORE_OS

```
┌─────────────────────────────────────────────────┐
│  PATRÓN: UUID SURROGATE KEY                     │
├─────────────────────────────────────────────────┤
│  Todas las tablas usan:                         │
│    id UUID PRIMARY KEY DEFAULT gen_random_uuid()│
│                                                 │
│  Las claves naturales son UNIQUE constraints:   │
│    UNIQUE(scheme, code)                         │
│    UNIQUE(code, fiscal_year)                    │
│    UNIQUE(agreement_id, installment_number)     │
└─────────────────────────────────────────────────┘
```

#### Verificación 2NF por Schema

**Schema `meta`**
| Tabla | PK | Business Key | 2NF |
|-------|----|--------------|----|
| `role` | `id (UUID)` | `code` | ✅ |
| `process` | `id (UUID)` | `code` | ✅ |
| `entity` | `id (UUID)` | `code` | ✅ |
| `story` | `id (UUID)` | `code` | ✅ |
| `story_entity` | `id (UUID)` | `(story_id, entity_id)` | ✅ |

**Schema `ref`**
| Tabla | PK | Business Key | 2NF |
|-------|----|--------------|----|
| `category` | `id (UUID)` | `(scheme, code)` | ✅ |
| `actor` | `id (UUID)` | `code` | ✅ |
| `operational_commitment_type` | `id (UUID)` | `code` | ✅ |

**Schema `core`** (muestra)
| Tabla | PK | Business Key | 2NF |
|-------|----|--------------|----|
| `ipr` | `id (UUID)` | `codigo_bip` | ✅ |
| `agreement` | `id (UUID)` | `agreement_number` | ✅ |
| `budget_program` | `id (UUID)` | `(code, fiscal_year)` | ✅ |
| `work_item` | `id (UUID)` | `code` | ✅ |

**Resultado 2NF**: ✅ **CUMPLE** - No hay dependencias parciales porque todas las PKs son simples (UUID surrogate).

---

### 3NF - Tercera Forma Normal

**Reglas:**
- Cumple 2NF
- Ningún atributo no-clave depende de otro atributo no-clave
- No hay dependencias transitivas

#### Análisis de Dependencias Transitivas

**Caso 1: `core.ipr` - ¿phase determina status?**

```sql
-- Columnas en cuestión
mcd_phase_id UUID REFERENCES ref.category(id),  -- F0, F1, F2...
status_id UUID REFERENCES ref.category(id),     -- IDEA, EN_FORMULACION...
```

**Análisis:**
```
¿mcd_phase_id → status_id?
NO. Son dimensiones independientes:
- mcd_phase_id: Fase del ciclo de inversión (F0-F8)
- status_id: Estado operativo dentro de cualquier fase

Ejemplo válido:
  Phase=F4 + Status=EN_EJECUCION
  Phase=F4 + Status=SUSPENDIDO
  Phase=F4 + Status=PARALIZADO

Las fases pueden tener múltiples estados posibles.
```

**Resultado**: ✅ Sin dependencia transitiva

---

**Caso 2: `core.person` - ¿organization determina role?**

```sql
organization_id UUID REFERENCES core.organization(id),
role_id UUID REFERENCES meta.role(id),
```

**Análisis:**
```
¿organization_id → role_id?
NO. Son independientes:
- organization_id: Dónde trabaja la persona
- role_id: Qué capacidad tiene

Una persona en DIPLADE puede ser ANALISTA o JEFE.
Una persona con role ANALISTA puede estar en DIPLADE o DAF.
```

**Resultado**: ✅ Sin dependencia transitiva

---

**Caso 3: `core.work_item` - Múltiples FKs**

```sql
ipr_id UUID REFERENCES core.ipr(id),
agreement_id UUID REFERENCES core.agreement(id),
resolution_id UUID REFERENCES core.resolution(id),
problem_id UUID REFERENCES core.ipr_problem(id),
commitment_id UUID REFERENCES core.operational_commitment(id),
```

**Análisis:**
```
¿Existe ipr_id → agreement_id?
NO. Son referencias independientes:
- Un work_item puede ser sobre una IPR sin convenio
- Un work_item puede ser sobre un convenio sin IPR
- Un work_item puede tener ambos o ninguno
```

**Resultado**: ✅ Sin dependencia transitiva

---

**Caso 4: `core.agreement_installment` - Campos calculables**

```sql
agreement_id UUID NOT NULL,
installment_number INTEGER NOT NULL,
amount NUMERIC(18,2) NOT NULL,
due_date DATE NOT NULL,
```

**Análisis:**
```
¿due_date derivable de installment_number?
NO. Los vencimientos no siguen patrón fijo.
Cada cuota tiene su fecha específica negociada.
```

**Resultado**: ✅ Sin dependencia transitiva

---

**Caso 5: `core.budget_program` - Campo calculado**

```sql
initial_amount NUMERIC(18,2) NOT NULL,
current_amount NUMERIC(18,2),  -- ¿Derivado?
committed_amount NUMERIC(18,2),
accrued_amount NUMERIC(18,2),
paid_amount NUMERIC(18,2),
```

**Análisis:**
```
¿current_amount derivable?
PARCIALMENTE. Se mantiene por trigger (MED-003).
current_amount = initial_amount + Σ(modificaciones)

Esto es DESNORMALIZACIÓN INTENCIONAL para performance.
```

**Resultado**: ⚠️ Desnormalización intencional (aceptable)

---

### BCNF - Boyce-Codd Normal Form

**Regla:**
- Cumple 3NF
- Todo determinante es una candidate key

#### Verificación BCNF

**Caso especial: `core.ipr_mechanism`**

```sql
CREATE TABLE core.ipr_mechanism (
    id UUID PRIMARY KEY,
    ipr_id UUID REFERENCES core.ipr(id) NOT NULL UNIQUE,
    -- Atributos SNI
    rate_mdsf VARCHAR(4),
    etapa_bip VARCHAR(16),
    sector VARCHAR(64),
    -- Atributos C33
    categoria_c33 VARCHAR(32),
    vida_util_residual INTEGER,
    -- Atributos FRIL
    tipo_fril VARCHAR(32),
    -- ... etc
);
```

**Análisis:**

Este es un patrón de **Single Table Inheritance (STI)**:

```
┌────────────────────────────────────────────────────────┐
│  PATRÓN: Single Table Inheritance                       │
├────────────────────────────────────────────────────────┤
│  Una tabla para múltiples "subtipos" de mecanismo       │
│                                                         │
│  Alternativa normalizada (Class Table Inheritance):     │
│    core.ipr_mechanism_sni                               │
│    core.ipr_mechanism_c33                               │
│    core.ipr_mechanism_fril                              │
│    core.ipr_mechanism_glosa06                           │
│    ...                                                  │
│                                                         │
│  Trade-offs:                                            │
│    STI: Más simple, menos JOINs, permite NULLs          │
│    CTI: Más normalizado, sin NULLs, más tablas          │
└────────────────────────────────────────────────────────┘
```

**Decisión**: **MANTENER STI**
- Razón: Solo hay 7 tipos de mecanismo, todos con atributos simples
- Los NULLs no consumen espacio en PostgreSQL (TOAST)
- Consultas más simples sin JOINs polimórficos

**Resultado BCNF**: ✅ **CUMPLE** - El STI es desnormalización intencional, no violación BCNF.

---

## Patrones de Desnormalización Identificados

### 1. Campos Calculados (Deliberado)

| Tabla | Campo | Fórmula | Justificación |
|-------|-------|---------|---------------|
| `core.budget_program` | `current_amount` | `initial + Σmodificaciones` | Performance en reportes |
| `core.ipr` | `has_open_problems` | `EXISTS(problems WHERE resolved_at IS NULL)` | Flag de alerta |

**Mantenimiento**: Triggers en `goreos_triggers.sql`

### 2. Single Table Inheritance (Deliberado)

| Tabla | Subtipos | Columnas Nullable |
|-------|----------|-------------------|
| `core.ipr_mechanism` | SNI, C33, FRIL, GLOSA06, FRPD, SUBV8 | ~15 |

**Justificación**: Simplicidad > Purismo normalizador

### 3. Event Sourcing (Patrón Arquitectónico)

| Tabla | Payload | Propósito |
|-------|---------|-----------|
| `txn.event` | `data JSONB` | Inmutabilidad, auditoría completa |
| `txn.magnitude` | `numeric_value` | Series temporales |

**Justificación**: Write-optimized pattern para auditoría

### 4. Arrays PostgreSQL (Extensión 1NF)

| Tabla | Campo | Uso |
|-------|-------|-----|
| `meta.story` | `extra_tags`, `acceptance_criteria` | Listas simples |
| `core.work_item` | `tags` | Etiquetado flexible |

**Justificación**: Soporte nativo, índices GIN, simplicidad

---

## Propuestas de Normalización (Opcionales)

### Propuesta A: Normalizar Tags de Story

```sql
-- Si se necesita relaciones N:M con tags
CREATE TABLE meta.tag (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE meta.story_tag (
    story_id UUID REFERENCES meta.story(id),
    tag_id UUID REFERENCES meta.tag(id),
    PRIMARY KEY (story_id, tag_id)
);
```

**Beneficios:**
- Tags reutilizables entre stories
- Integridad referencial
- Facilita taxonomías de tags

**Costos:**
- 2 JOINs adicionales por query
- Complejidad en inserts/updates

**Recomendación**: Solo implementar si se requiere gestión de tags como entidades.

---

### Propuesta B: Normalizar IPR Mechanism (CTI)

```sql
-- Si los mecanismos divergen significativamente
CREATE TABLE core.ipr_mechanism_base (
    id UUID PRIMARY KEY,
    ipr_id UUID UNIQUE REFERENCES core.ipr(id)
);

CREATE TABLE core.ipr_mechanism_sni (
    id UUID PRIMARY KEY REFERENCES core.ipr_mechanism_base(id),
    rate_mdsf VARCHAR(4),
    etapa_bip VARCHAR(16),
    sector VARCHAR(64)
);

CREATE TABLE core.ipr_mechanism_c33 (
    id UUID PRIMARY KEY REFERENCES core.ipr_mechanism_base(id),
    categoria_c33 VARCHAR(32),
    vida_util_residual INTEGER,
    informe_tecnico_favorable BOOLEAN,
    cofinanciamiento_anf NUMERIC(5,2)
);
-- ... etc por mecanismo
```

**Beneficios:**
- Sin NULLs
- Constraints específicos por tipo
- Mejor documentación de estructura

**Costos:**
- 7+ tablas adicionales
- JOINs polimórficos complejos
- Más código en aplicación

**Recomendación**: Solo implementar si los mecanismos requieren validaciones muy distintas.

---

## Diagrama de Dependencias Funcionales

```mermaid
graph TD
    subgraph "core.ipr - Sin Dependencias Transitivas"
        IPR_ID[id PK]
        IPR_ID --> BIP[codigo_bip]
        IPR_ID --> NAME[name]
        IPR_ID --> NATURE[ipr_nature]
        IPR_ID --> PHASE[mcd_phase_id]
        IPR_ID --> STATUS[status_id]
        IPR_ID --> MECH[mechanism_id]

        %% No hay flechas entre atributos no-clave
        PHASE -.x.- STATUS
        MECH -.x.- STATUS
    end

    subgraph "core.person - Sin Dependencias Transitivas"
        PERSON_ID[id PK]
        PERSON_ID --> RUT[rut]
        PERSON_ID --> NAMES[names]
        PERSON_ID --> ORG[organization_id]
        PERSON_ID --> ROLE[role_id]

        %% No hay flechas entre atributos no-clave
        ORG -.x.- ROLE
    end

    subgraph "core.budget_program - Desnormalización Intencional"
        BP_ID[id PK]
        BP_ID --> CODE[code]
        BP_ID --> YEAR[fiscal_year]
        BP_ID --> INIT[initial_amount]
        BP_ID --> CURR[current_amount]

        INIT -.->|trigger| CURR
    end
```

---

## Conclusiones

### Estado de Normalización

| Aspecto | Estado | Notas |
|---------|--------|-------|
| 1NF | ⚠️ 97% | Arrays son extensión PostgreSQL aceptada |
| 2NF | ✅ 100% | Surrogate keys eliminan dependencias parciales |
| 3NF | ✅ 100% | Sin dependencias transitivas en datos operacionales |
| BCNF | ✅ 100% | Determinantes son candidate keys |

### Desnormalizaciones Justificadas

1. **Arrays TEXT[]** - Simplicidad para listas simples
2. **JSONB metadata** - Extensibilidad semi-estructurada
3. **current_amount** - Performance en reporting
4. **ipr_mechanism STI** - Simplicidad sobre purismo
5. **txn.event.data** - Event Sourcing pattern

### Recomendación Final

**El modelo GORE_OS v3.0 está correctamente normalizado hasta 3NF/BCNF.**

Las desnormalizaciones presentes son:
- Intencionales
- Documentadas
- Mantenidas por triggers
- Justificadas por trade-offs de performance y simplicidad

**No se recomienda normalización adicional** a menos que surjan requerimientos específicos que lo justifiquen.

---

*Análisis de Normalización generado para GORE_OS v3.0*
