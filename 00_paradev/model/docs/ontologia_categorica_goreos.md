# Ontología Categórica GORE_OS v4.0

## El Sistema que Sirve al Gobierno Regional de Ñuble

**Versión:** 4.1.0 — *Categorial-Integra*  
**Estado:** Norma Superior de Construcción  
**Fecha:** 2025-12-22  
**Arquitecto:** Arquitecto-GORE (v0.1.0)

---

## 0. Propósito Fundamental

> **GORE_OS existe para que el Gobierno Regional de Ñuble funcione mejor.**

Esta ontología define **qué construimos**, **cómo se relaciona**, y **para qué sirve** en el camino hacia un sistema operativo institucional funcional.

---

## 0.1 La Story como Átomo Generador

> **Todo nace de una historia. La Story es la semilla del sistema.**

Una historia de usuario no es solo un requisito — es el **átomo primordial** del cual se extrae todo lo necesario para construir GORE_OS:

```
                         ┌─────────────────────────────────────────┐
                         │              STORY                      │
                         │   "Como [ROL] quiero [ACCIÓN]           │
                         │    para que [BENEFICIO]"                │
                         └───────────────┬─────────────────────────┘
                                         │
           ┌─────────────────────────────┼─────────────────────────────┐
           │                             │                             │
           ▼                             ▼                             ▼
    ┌─────────────┐              ┌─────────────┐              ┌─────────────┐
    │    ROLE     │              │   ENTITY    │              │  PROCESS    │
    │  (Quién)    │              │ (Qué datos) │              │   (Cómo)    │
    └─────────────┘              └─────────────┘              └─────────────┘
           │                             │                             │
           │                             │                             │
           └─────────────────────────────┼─────────────────────────────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │ CAPABILITY  │
                                  │(Qué valor)  │
                                  └──────┬──────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │   MODULE    │
                                  │(Dónde código)│
                                  └─────────────┘
```

### ¿Qué se extrae de cada Story?

| Pregunta al leer la Story                           | Se deriva      | Ejemplo                                                   |
| --------------------------------------------------- | -------------- | --------------------------------------------------------- |
| **"Como [X]..."** → ¿Quién?                         | **Role**       | "Como Analista Presupuesto" → `ROL-ANAL-PPTO`             |
| **"...quiero [Y]..."** → ¿Qué acción?               | **Process**    | "quiero gestionar firmas" → `PROC-FIRMA-CONVENIO`         |
| **"...quiero [Y]..."** → ¿Qué datos necesito?       | **Entity**     | "gestionar firmas convenio" → `ENT-CONVENIO`, `ENT-FIRMA` |
| **"...para que [Z]"** → ¿Qué valor?                 | **Capability** | "para que obtengo firmas" → `CAP-FIN-CONVENIOS`           |
| **Múltiples stories similares** → ¿Dónde agrupamos? | **Module**     | Stories de convenios → `MOD-FIN-CONVENIOS`                |

### El Flujo de Extracción

```
╔══════════════════════════════════════════════════════════════════════╗
║                    STORY: EL ÁTOMO GENERADOR                         ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  "Como ANALISTA PRESUPUESTO quiero GESTIONAR FIRMAS DE CONVENIO      ║
║   para que OBTENGO FIRMAS DE AMBAS PARTES"                           ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ① EXTRAER ACTORES (→ Role)                                          ║
║     └── "Analista Presupuesto" → ¿Existe? Si no, crear ROL           ║
║                                                                      ║
║  ② EXTRAER SUSTANTIVOS (→ Entity)                                    ║
║     └── "Convenio", "Firma", "Partes" → ¿Qué debe RECORDAR el        ║
║         sistema? Crear ENT para cada dato persistente                ║
║                                                                      ║
║  ③ EXTRAER VERBOS (→ Process)                                        ║
║     └── "Gestionar", "Firmar" → ¿Cómo FLUYE el trabajo?              ║
║         Crear PROC con estados y transiciones                        ║
║                                                                      ║
║  ④ EXTRAER BENEFICIO (→ Capability)                                  ║
║     └── "Obtener firmas" → ¿Qué VALOR entrega?                       ║
║         Agrupar stories que entregan valor similar                   ║
║                                                                      ║
║  ⑤ ORGANIZAR (→ Module)                                              ║
║     └── ¿DÓNDE vive esto en el código?                               ║
║         Agrupar entities + processes cohesivos                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 0.2 El Dominio: Contexto Organizacional

> **El Dominio NO es una carpeta — es un CONTEXTO DE SIGNIFICADO.**

### ¿Qué es un Dominio?

Un **Dominio** (D-FIN, D-TDE, D-TERR...) es una **fibra semántica** que agrupa átomos que comparten:
- El mismo **vocabulario** de negocio
- Las mismas **reglas** institucionales
- Los mismos **actores** responsables
- La misma **normativa** aplicable

```
                    GORE_OS
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌───────┐      ┌───────┐      ┌───────┐
    │ D-FIN │      │ D-TDE │      │ D-TERR│
    │       │      │       │      │       │
    │Finanzas│      │Digital│      │Territ.│
    └───┬───┘      └───┬───┘      └───┬───┘
        │              │              │
    ┌───┴───┐      ┌───┴───┐      ┌───┴───┐
    │Stories│      │Stories│      │Stories│
    │Roles  │      │Roles  │      │Roles  │
    │Entities      │Entities      │Entities
    │Processes     │Processes     │Processes
    └───────┘      └───────┘      └───────┘
```

### Los Dominios de GORE_OS

| Dominio                    | Código | Contexto                             | Ejemplos de Valor                |
| -------------------------- | ------ | ------------------------------------ | -------------------------------- |
| **Finanzas**               | D-FIN  | Presupuesto, contabilidad, tesorería | Ejecutar el presupuesto regional |
| **Transformación Digital** | D-TDE  | Firma, interoperabilidad, datos      | Cumplir normativa digital        |
| **Territorial**            | D-TERR | Georreferenciación, IDE, inversiones | Visualizar impacto territorial   |
| **Normativo**              | D-NORM | Actos administrativos, jurídica      | Garantizar legalidad             |
| **Ejecución**              | D-EJEC | Proyectos, programas, convenios      | Ejecutar inversión pública       |
| **Gobierno**               | D-GOB  | CORE, comisiones, gobernador         | Tomar decisiones regionales      |
| **BackOffice**             | D-BACK | RRHH, bienes, flota                  | Operar internamente              |
| **Desarrollo**             | D-DEV  | Código, CI/CD, arquitectura          | Construir GORE_OS                |
| **Operaciones**            | D-OPS  | Infraestructura, monitoreo           | Mantener GORE_OS                 |
| **Seguridad**              | D-SEG  | Seguridad pública, CIES              | Proteger la región               |
| **Comunicaciones**         | D-COM  | Prensa, RRSS, eventos                | Comunicar gestión                |
| **Evolución**              | D-EVOL | IA, mejora continua                  | Evolucionar el sistema           |

### Dominio como Funtor de Proyección

Categóricamente, el Dominio actúa como un **Funtor de Olvido**:

$$\pi_D: \mathcal{GORE\_OS} \to \mathcal{Domain}$$

Proyecta cada átomo a su contexto semántico, permitiendo:
- **Filtrar**: Ver solo lo relevante para un área
- **Validar**: Aplicar reglas específicas del dominio
- **Asignar**: Responsabilizar a equipos por dominio

### Relación Dominio ↔ Module

```
DOMINIO (Semántico)              MODULE (Técnico)
════════════════════             ════════════════════
D-FIN                    ───▶    MOD-FIN-PRESUPUESTO
(Contexto de Finanzas)           MOD-FIN-TESORERIA
                                 MOD-FIN-CONTABILIDAD

Un dominio puede tener múltiples modules.
Pero un module pertenece a UN dominio.
```

---

GORE_OS se construye sobre **3 dimensiones ortogonales** que garantizan que cada concepto tenga un propósito único e independiente:

```
                         TIEMPO (T)
                            ↑
                            │
                            │  Fase 3: OPERAR
                            │  ┌─────────────┐
                            │  │ Servicios   │
                            │  │ (runtime)   │
                            │  └─────────────┘
                            │
                            │  Fase 2: FABRICAR
                            │  ┌─────────────┐
                            │  │ Código      │
                            │  │ (build)     │
                            │  └─────────────┘
                            │
                            │  Fase 1: MODELAR
                            │  ┌─────────────┐
                            │  │ Átomos      │
                            │  │ (design)    │
                            │  └─────────────┘
                            │
         ESTRUCTURA (S) ────┼────────────────▶ VALOR (V)
                            │
        (Cómo se organiza)  │                (Qué beneficio entrega)
```

### 1.1 Ejes Ortogonales

| Eje            | Símbolo       | Pregunta                | Categoría                  |
| -------------- | ------------- | ----------------------- | -------------------------- |
| **Estructura** | $\mathcal{S}$ | ¿Cómo se organiza?      | Morfismos internos         |
| **Valor**      | $\mathcal{V}$ | ¿Qué beneficio entrega? | Funtores hacia usuario     |
| **Tiempo**     | $\mathcal{T}$ | ¿En qué fase estamos?   | Transformaciones naturales |

### 1.2 Invariante de Ortogonalidad

Cada átomo debe responder exactamente a **UNA** pregunta primaria:

$$\forall a \in Atom: \dim(a) \in \{S, V, T\} \text{ (dimensión dominante)}$$

---

## 2. Los 6 Átomos: Definición Categórica con Propósito

### 2.0 Tabla de Ortogonalidad

| Átomo          | Dimensión  | Pregunta Primaria             | Valor para GORE_OS             |
| -------------- | ---------- | ----------------------------- | ------------------------------ |
| **Story**      | Valor      | ¿Qué necesita el usuario?     | Define requisitos verificables |
| **Role**       | Estructura | ¿Quién puede actuar?          | Define permisos y contextos    |
| **Entity**     | Estructura | ¿Qué datos persisten?         | Define el modelo de datos      |
| **Process**    | Tiempo     | ¿Cómo fluye el trabajo?       | Define la lógica dinámica      |
| **Capability** | Valor      | ¿Qué puede lograr el sistema? | Agrupa valor entregable        |
| **Module**     | Estructura | ¿Dónde vive el código?        | Organiza la implementación     |

---

### 2.1 Story — El Requisito (Dimensión: Valor)

**Definición Categórica:**
$$Story: Hom_{\mathcal{V}}(Carencia, Beneficio)$$

Un morfismo en la categoría de Valor que transforma una necesidad en un beneficio verificable.

**Propósito en GORE_OS:**
- Captura QUÉ debe hacer el sistema
- Es la unidad mínima de valor medible
- Genera tests de aceptación

**Firma:**
```yaml
Story:
  id: US-{DOMAIN}-{NUM}
  role_id: → Role              # Morfismo: Story → Role (actor_of⁻¹)
  capability_id: → Capability  # Morfismo: Story → Capability (contributes_to)
  mentions: [→ Entity]         # Profunctor: Story ⊗ Entity → Bool
  i_want: string               # Intent (acción deseada)
  so_that: string              # Postcondición (beneficio lógico)
  acceptance_criteria: []      # Predicados de verificación
  ─────────────────────────────
  # GENERA:
  → test/acceptance/{id}.feature
```

**Diagrama:**
```
Role ──actor_of──▶ Story ──contributes_to──▶ Capability
                     │
                     ▼
               acceptance_criteria
                     │
                     ▼
                   TEST
```

---

### 2.2 Role — El Actor (Dimensión: Estructura)

**Definición Categórica:**
$$Role: Obj(\mathcal{Auth}) \text{ donde } \mathcal{Auth} \subset \mathcal{S}$$

Un objeto en la subcategoría de Autorización que define un lugar de acción.

**Propósito en GORE_OS:**
- Define QUIÉN interactúa con el sistema
- Establece permisos y contexto organizacional
- Habilita control de acceso (RBAC)

**Firma:**
```yaml
Role:
  id: ROL-{TYPE}-{NAME}
  type: [internal|external|system]
  permissions: []          # Qué puede hacer
  context: string          # Dónde actúa
  ─────────────────────────
  # GENERA:
  → src/auth/policies/{id}.json
  → src/auth/guards/{id}.guard.ts
```

**Invariante:**
$$\forall r \in Role: \exists s \in Story \mid r = s.role\_id$$
*(No existen roles sin historias)*

---

### 2.3 Entity — El Dato (Dimensión: Estructura)

**Definición Categórica:**
$$Entity: Obj(\mathcal{Schema}) \text{ con } \mathcal{Schema} \simeq \textbf{FinSet}$$

Un objeto en la categoría de esquemas que define estructura persistente.

**Propósito en GORE_OS:**
- Define QUÉ datos guarda el sistema
- Establece la estructura de base de datos
- Habilita persistencia y consultas

**Firma:**
```yaml
Entity:
  id: ENT-{DOMAIN}-{NAME}
  category: [Core|Transactional|Reference|Audit]
  attributes: []           # Campos
  relations: []            # FKs a otras entidades
  invariants: []           # Reglas de negocio
  ─────────────────────────
  # GENERA:
  → src/domain/entities/{Name}.ts
  → prisma/schema/{domain}.prisma
  → src/domain/dtos/{Name}Dto.ts
```

**Diagrama de Relaciones:**
```
Entity ◀──manipulates── Process
   │
   └──mentions──▶ Story (trazabilidad)
```

---

### 2.4 Process — El Flujo (Dimensión: Tiempo)

**Definición Categórica:**
$$Process: Coalg_F(\mathcal{State}) \text{ donde } F(S) = Action \times S$$

Una coálgebra que define comportamiento dinámico como transiciones de estado.

**Propósito en GORE_OS:**
- Define CÓMO fluye el trabajo
- Establece estados, transiciones y actores
- Habilita workflows y automatización

**Firma:**
```yaml
Process:
  id: PROC-{DOMAIN}-{NAME}
  implements: [→ Story]       # Profunctor: Process ⊗ Story → Bool
  states: []                   # Obj(States) — Estados como objetos
  transitions:                 # Morph(States) — Transiciones como morfismos
    - from: Estado_A
      to: Estado_B
      actor: → Role            # Morfismo: Transition → Role (executes⁻¹)
      guard: Predicado         # Condición de guarda
  manipulates:                 # Profunctor: Process ⊗ Entity → CRUD
    - entity: → Entity
      operations: [C|R|U|D]    # Operaciones permitidas
  ─────────────────────────────
  # GENERA:
  → src/domain/workflows/{Name}Workflow.ts
  → src/domain/machines/{Name}Machine.ts
  → bpmn/{id}.bpmn
```

**Diagrama:**
```
         ┌──guard──┐
         ▼         │
State_A ───▶ Transition ───▶ State_B
         │                    │
         └──actor: Role───────┘
```

---

### 2.5 Capability — El Valor Agregado (Dimensión: Valor)

**Definición Categórica:**
$$Capability = \coprod_{j \in J} Story_j \text{ (Colímite de Stories)}$$

Un coproducto que agrupa stories en una funcionalidad completa.

**Propósito en GORE_OS:**
- Define QUÉ PUEDE HACER el sistema (visión usuario)
- Agrupa stories relacionadas
- Es la unidad de entrega de valor

**Firma:**
```yaml
Capability:
  id: CAP-{DOMAIN}-{NAME}
  description: string      # Valor en lenguaje humano
  stories: [Story]         # Historias que agrupa
  modules: [Module]        # Dónde se implementa
  ─────────────────────────
  # GENERA:
  → Feature flag en config
  → Endpoint principal en API
  → Documentación de usuario
```

**Relación con Module:**
```
Capability (QUÉ)           Module (DÓNDE)
══════════════════         ═══════════════
"Gestionar Presupuesto" ──realizes──▶ mod-fin-presupuesto/
        │
        └── Múltiples modules pueden realizar 1 capability
```

---

### 2.6 Module — La Organización (Dimensión: Estructura)

**Definición Categórica:**
$$Module = \int_{D}(Entity \times Process) \text{ (Integral de Grothendieck)}$$

Un fibrado que organiza entities y processes en un componente cohesivo.

**Propósito en GORE_OS:**
- Define DÓNDE vive el código
- Agrupa entities y processes relacionados
- Establece dependencias y fronteras

**Firma:**
```yaml
Module:
  id: MOD-{DOMAIN}-{NAME}
  path: src/modules/{domain}/{name}/
  entities: [Entity]       # Datos que maneja
  processes: [Process]     # Flujos que ejecuta
  depends_on: [Module]     # Dependencias (DAG)
  exposes: [API]           # Interfaz pública
  ─────────────────────────
  # GENERA:
  → src/modules/{path}/index.ts
  → src/modules/{path}/module.ts
  → docker/services/{id}.dockerfile
```

**Invariante DAG:**
$$\text{depends\_on} \text{ no tiene ciclos}$$

---

## 3. Relaciones: Los Profunctores

Las relaciones N:M se modelan como **Profunctores** (bimodules) independientes:

```
Profunctor: A ⊗ B → Set
```

### 3.1 Tabla de Profunctores

Los **Profunctores** son bimodules $P: \mathcal{C}^{op} \times \mathcal{D} \to \textbf{Set}$ que modelan relaciones heterogéneas entre categorías de átomos.

| Profunctor         | Firma Categórica                                | Semántica            | Fuente de Verdad                                         |
| ------------------ | ----------------------------------------------- | -------------------- | -------------------------------------------------------- |
| **actor_of**       | $Role^{op} \otimes Story \to \mathbf{2}$        | Quién protagoniza    | `Story.role_id`                                          |
| **contributes_to** | $Story^{op} \otimes Capability \to \mathbf{2}$  | Qué aporta valor     | `Story.capability_id`                                    |
| **mentions**       | $Story^{op} \otimes Entity \to \mathbf{2}$      | Qué datos requiere   | `Story.mentions[]`                                       |
| **implements**     | $Process^{op} \otimes Story \to \mathbf{2}$     | Qué workflow realiza | `Process.implements[]`                                   |
| **manipulates**    | $Process^{op} \otimes Entity \to \textbf{CRUD}$ | Qué modifica         | `Process.manipulates[]`                                  |
| **executes**       | $Role^{op} \otimes Process \to \mathbf{2}$      | Quién activa         | **Derivado**: $\exists t \in P.transitions: t.actor = R$ |
| **realizes**       | $Module^{op} \otimes Capability \to \mathbf{2}$ | Dónde implementa     | `Capability.modules[]`                                   |
| **depends_on**     | $Module^{op} \otimes Module \to \mathbf{2}$     | DAG de construcción  | `Module.depends_on[]`                                    |
| **belongs_to**     | $Atom^{op} \otimes Domain \to \mathbf{2}$       | Contexto semántico   | `*.domain`                                               |

### 3.2 Diagrama de Relaciones Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                    GORE_OS: GRAFO ONTOLÓGICO                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                        DIMENSIÓN VALOR                          │
│                    ┌─────────────────────┐                      │
│                    │     Capability      │                      │
│                    │    (Valor Total)    │                      │
│                    └──────────▲──────────┘                      │
│                               │                                 │
│                        contributes_to                           │
│                               │                                 │
│         actor_of      ┌──────┴──────┐      mentions             │
│    ┌─────────────────▶│   Story     │◀─────────────────┐        │
│    │                  │ (Requisito) │                  │        │
│    │                  └─────────────┘                  │        │
│    │                                                   │        │
│ ───┼───────────────── DIMENSIÓN ESTRUCTURA ───────────┼─────── │
│    │                                                   │        │
│ ┌──┴────┐       executes        ┌──────────┐          │        │
│ │ Role  │──────────────────────▶│  Process │          │        │
│ │(Actor)│                       │  (Flujo) │          │        │
│ └───────┘                       └────┬─────┘          │        │
│                                      │                │        │
│                               manipulates             │        │
│                                      │                │        │
│                                      ▼                │        │
│                               ┌──────────┐            │        │
│                               │  Entity  │◀───────────┘        │
│                               │  (Dato)  │                     │
│                               └────┬─────┘                     │
│                                    │                           │
│ ───────────────────────────────────┼─────────────────────────  │
│                                    │                           │
│                        DIMENSIÓN ORGANIZACIÓN                  │
│                                    │                           │
│                                    ▼                           │
│                             ┌──────────┐        realizes       │
│                             │  Module  │─────────────────────▶ │
│                             │ (Código) │       Capability      │
│                             └────┬─────┘                       │
│                                  │                             │
│                            depends_on                          │
│                                  │                             │
│                                  ▼                             │
│                            Otros Modules                       │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Dimensión Temporal: Las Fases de Construcción

### 4.1 Las 3 Fases

```
                    TIEMPO
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
 MODELAR          FABRICAR           OPERAR
 (Diseño)         (Build)            (Run)
    │                 │                 │
    ▼                 ▼                 ▼
 Átomos YAML      Código TS         Servicios
 Schemas JSON     Tests             Containers
 Diagramas        Migrations        APIs Live
```

### 4.2 Transformaciones entre Fases (Funtores)

| Funtor                   | Dominio      | Codominio | Transforma           |
| ------------------------ | ------------ | --------- | -------------------- |
| $\mathcal{G}$ (Generate) | model/atoms/ | src/      | Átomo → Código       |
| $\mathcal{B}$ (Build)    | src/         | dist/     | Código → Artefacto   |
| $\mathcal{D}$ (Deploy)   | dist/        | runtime/  | Artefacto → Servicio |
| $\mathcal{A}$ (Audit)    | runtime/     | model/    | Servicio → Métricas  |

### 4.3 Ciclo de Vida del Átomo

```
              ┌──────────────────────────────────────┐
              │                                      │
              ▼                                      │
         ┌─────────┐    $\mathcal{G}$    ┌─────────┐ │
         │  ATOM   │ ──────────────────▶ │  CODE   │ │
         │ (.yml)  │                     │  (.ts)  │ │
         └─────────┘                     └────┬────┘ │
              ▲                               │      │
              │                    $\mathcal{B}$     │
              │                               │      │
         $\mathcal{A}$                        ▼      │
              │                          ┌─────────┐ │
              │                          │  DIST   │ │
              │                          │ (.js)   │ │
              │                          └────┬────┘ │
              │                               │      │
              │                    $\mathcal{D}$     │
              │                               │      │
              │                               ▼      │
         ┌────┴────┐                     ┌─────────┐ │
         │ METRICS │ ◀─────────────────  │ SERVICE │ │
         │ (Audit) │                     │ (Live)  │ │
         └─────────┘                     └─────────┘ │
              │                                      │
              └──────────────────────────────────────┘
                    MEJORA CONTINUA
```

---

## 5. Generación de Valor: El Propósito Final

### 5.1 Cadena de Valor

```
NECESIDAD → STORY → CAPABILITY → MODULE → CÓDIGO → SERVICIO → VALOR
    │          │         │           │        │         │        │
    └──────────┴─────────┴───────────┴────────┴─────────┴────────┘
                      TRAZABILIDAD COMPLETA
```

### 5.2 Métricas de Valor por Átomo

| Átomo      | Métrica de Valor           | Pregunta          |
| ---------- | -------------------------- | ----------------- |
| Story      | % Aceptación cumplida      | ¿Se verificó?     |
| Role       | # Usuarios activos por rol | ¿Lo usan?         |
| Entity     | # Registros / Integridad   | ¿Datos correctos? |
| Process    | Tiempo promedio ejecución  | ¿Es eficiente?    |
| Capability | Adopción de funcionalidad  | ¿Entrega valor?   |
| Module     | Cobertura de tests         | ¿Es confiable?    |

---

## 6. Invariantes Globales (Leyes Categoriales)

Los invariantes son **ecualizadores** que garantizan la conmutatividad de los diagramas ontológicos.

### GI-01: Trazabilidad Completa (Composición de Morfismos)

$$\forall s \in Story: \exists c \in Capability, m \in Module \mid s \xrightarrow{contributes} c \xrightarrow{realizes^{-1}} m$$

*Toda historia tiene un camino hacia código implementado. El diagrama conmuta.*

### GI-02: Aciclicidad (DAG como Categoría Libre)

$$\text{depends\_on}: Module \times Module \text{ es un DAG} \implies \mathcal{M} \simeq \text{Free}(G)$$

*El grafo de dependencias genera una categoría libre (sin ciclos).*

### GI-03: Cobertura de Roles (Fibración)

$$\forall s \in Story: \pi_{Role}(s) \in Obj(\mathcal{Role})$$

*El funtor de proyección $\pi_{Role}: Story \to Role$ es total (toda historia tiene actor).*

### GI-04: Cohesión de Módulos (Pullback sobre dependencias)

$$\forall m \in Module, \forall p \in m.processes: \exists e \in (m.entities \cup \bigcup_{d \in m.depends} d.entities) \mid p.manipulates(e)$$

*Todo proceso manipula entidades de su módulo o de sus dependencias (cierre transitivo).*

### GI-05: Implementación Completa (Cubrimiento)

$$\forall s \in Story: \exists p \in Process \mid s \in p.implements$$

*Toda historia tiene al menos un proceso que la implementa. El profunctor `implements` es epi.*

### GI-06: Datos Trazables (No hay entidades huérfanas)

$$\forall e \in Entity: \exists s \in Story \mid e \in s.mentions$$

*Toda entidad es mencionada por al menos una historia. El profunctor `mentions` es epi.*

### GI-07: Coherencia de Dominio (Fibración consistente)

$$\forall s \in Story, \forall e \in s.mentions: \pi_D(s) = \pi_D(e) \lor e.domain = \text{SHARED}$$

*Una historia solo menciona entidades de su mismo dominio o entidades compartidas.*

---

## 7. Comandos de Construcción (CLI goreos)

```bash
# ═══════════════════════════════════════════════════════════════
# FASE MODELAR
# ═══════════════════════════════════════════════════════════════
goreos model:validate          # Validar todos los átomos
goreos model:graph             # Generar grafo de relaciones
goreos model:health            # Reporte de salud del modelo

# ═══════════════════════════════════════════════════════════════
# FASE FABRICAR
# ═══════════════════════════════════════════════════════════════
goreos generate:all            # Generar todo el código
goreos generate:entities       # Entity → Prisma + TS
goreos generate:processes      # Process → Workflows
goreos generate:auth           # Role → RBAC
goreos generate:tests          # Story → Acceptance tests

goreos build:module <name>     # Construir módulo específico
goreos build:all               # Construir todo

# ═══════════════════════════════════════════════════════════════
# FASE OPERAR
# ═══════════════════════════════════════════════════════════════
goreos deploy:staging          # Desplegar a staging
goreos deploy:production       # Desplegar a producción

goreos audit:coverage          # Cobertura de tests
goreos audit:traceability      # Trazabilidad Story→Código
goreos audit:value             # Métricas de valor
```

---

## 8. Resumen: Cada Cosa con Sentido

| Átomo          | Es un...   | Sirve para...        | Genera... | Mide su valor con... |
| -------------- | ---------- | -------------------- | --------- | -------------------- |
| **Story**      | Requisito  | Saber QUÉ construir  | Tests     | % Aceptación         |
| **Role**       | Actor      | Saber QUIÉN usa      | Permisos  | Usuarios activos     |
| **Entity**     | Dato       | Saber QUÉ guardar    | Schema    | Integridad datos     |
| **Process**    | Flujo      | Saber CÓMO funciona  | Workflow  | Tiempo ejecución     |
| **Capability** | Valor      | Saber QUÉ entregamos | Features  | Adopción             |
| **Module**     | Componente | Saber DÓNDE va       | Código    | Cobertura tests      |

---

> **Certificación Arquitecto-GORE v0.1.0:** Esta ontología v4.0 integra rigor categórico con propósito pragmático. Cada átomo tiene un lugar en las dimensiones de Estructura, Valor y Tiempo. El objetivo es claro: **construir GORE_OS para que el Gobierno Regional de Ñuble funcione mejor**.
