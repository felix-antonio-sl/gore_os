# MANIFESTO GORE_OS

> **Sistema Operativo del Gobierno Regional de Ñuble**
> *Digitalizar, automatizar y dotar de inteligencia al GORE para acelerar el desarrollo de Ñuble.*

---

## 1. Identidad

**GORE_OS** es el sistema operativo institucional del Gobierno Regional de Ñuble. No es un software tradicional, sino un **modelo integrado de datos, procesos y capacidades** que permite al GORE funcionar de manera coherente, auditable y evolucionar orgánicamente.

### Definición Esencial

El Gobierno Regional es la administración superior de la región, concebida como territorio con características e intereses propios, que acerca decisiones de desarrollo al lugar donde se producen sus efectos.

**GORE_OS materializa esta misión** mediante:

- **Digitalización**: Transformar procesos manuales en flujos digitales trazables
- **Automatización**: Reducir tiempos de respuesta y eliminar cuellos de botella
- **Inteligencia**: Habilitar decisiones basadas en datos y alertas tempranas

### Qué Significa "Inteligencia"

Cuando hablamos de hacer a la organización "más inteligente", nos referimos a que **las personas podrán tomar mejores decisiones, apoyadas por sistemas de inteligencia artificial**. Este apoyo se materializa principalmente en:

| Modalidad                       | Descripción                                                         | Ejemplo                                                |
| ------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------ |
| **Agentes en segundo plano**    | Operan autónomamente detectando patrones, anomalías y oportunidades | Alerta de IPR con riesgo de paralización               |
| **Asistentes conversacionales** | Interactúan directamente con usuarios para consultas y análisis     | "Muéstrame las IPR de San Carlos con pagos pendientes" |

### Competencias Funcionales Integradas

GORE_OS integra competencias funcionales equivalentes a sistemas especializados, **sin utilizar ni exponer explícitamente esos términos**:

| Competencia Implícita                     | Equivalente Comercial | Alcance en GORE_OS                                    |
| ----------------------------------------- | --------------------- | ----------------------------------------------------- |
| **Gestión de Intervenciones Públicas**    | CRM                   | Ciclo de vida 360° de IPR, actores, hitos, alertas    |
| **Funcionamiento Organizacional**         | ERP                   | Divisiones, funcionarios, activos, control de gestión |
| **Inversión para el Desarrollo Regional** | Banca de Inversión    | Portafolio de fondos, priorización, ROI territorial   |

> **Principio**: Estas competencias están incorporadas dentro de la arquitectura de GORE_OS como funcionalidades nativas, no como módulos externos ni como terminología visible al usuario.

---

## 2. Génesis: El Problema que Resolvemos

Este proyecto surge como respuesta a una **crisis de gestión institucional** que expuso deficiencias estructurales:

| Problema                               | Impacto                                      | Solución GORE_OS                     |
| -------------------------------------- | -------------------------------------------- | ------------------------------------ |
| Obras terminadas sin entregar          | Inversión pública inmovilizada               | Seguimiento 360° del ciclo de vida   |
| Falta de seguimiento de ejecución      | Pérdida de control operativo                 | PMO Regional como "torre de control" |
| Pagos pendientes no identificados      | Paralizaciones de obras de alto valor social | Alertas tempranas de desviaciones    |
| Dificultad en priorización de recursos | Ineficiencia presupuestaria                  | Motor de recomendación basado en ERD |

> **La crisis reveló que el GORE carecía de un sistema nervioso digital capaz de detectar problemas antes de que se convirtieran en crisis.**

---

## 3. Ontología Estratificada del GORE_OS

GORE_OS se estructura semánticamente en torno a **tres entidades fundamentales** que articulan todo el sistema:

### 3.1 La Intervención Pública Regional (IPR)

Constituye el **núcleo del funcionamiento del GORE** y el principal medio para generar impacto en el desarrollo de Ñuble.

> Una IPR es cualquier acción de inversión o gasto público decidida y financiada por el Gobierno Regional para materializar su misión de desarrollo territorial.

**Ciclo de Vida 360°:**

| Fase               | Instrumentos           | Actores Clave          |
| ------------------ | ---------------------- | ---------------------- |
| Evaluación Ex-Ante | RS/MDSF, Admisibilidad | Analista, MDSF         |
| Priorización       | ERD, ARI, CORE         | Gobernador, Consejeros |
| Ejecución          | Convenios, UT/UF       | Ejecutor, Inspector    |
| Seguimiento        | Bitácora, Alertas, PMO | Coordinador            |
| Evaluación Ex-Post | KPIs, ROI, Cierre      | Evaluador              |

### 3.2 La Historia de Usuario

Mecanismo formal para **capturar y expresar los requerimientos del sistema**: qué debe hacer y cómo debe hacerlo.

> Toda funcionalidad, capacidad o flujo de GORE_OS debe originarse en una Historia de Usuario formal, trazable y validable.

| Componente            | Propósito                         |
| --------------------- | --------------------------------- |
| `as_a`                | Rol que necesita la funcionalidad |
| `i_want`              | Acción o capacidad requerida      |
| `so_that`             | Valor o resultado esperado        |
| `acceptance_criteria` | Condiciones de validación         |

### 3.3 El Usuario-Rol (Agente Activo)

No existe una distinción ontológica fundamental entre un "Usuario" (Humano) y un "Agente" (Máquina) al nivel más bajo. Siguiendo el primitivo **P1_Agente** de ORKO, ambos son manifestaciones del mismo concepto: un **Agente que efectúa transformaciones**.

> Un Usuario-Rol es un **Agente (P1)** instanciado en un contexto específico dentro de GORE_OS.

#### Dimensión 1: Sustrato (¿QUIÉN ejecuta?)

| Sustrato         | Descripción                            | Ejemplos en GORE_OS                  |
| ---------------- | -------------------------------------- | ------------------------------------ |
| **Humano**       | Aporta juicio, ética, responsabilidad  | Analista, Coordinador, Jefe División |
| **Algorítmico**  | Aporta escala, velocidad, consistencia | Agente de Alertas, Bot de Monitoreo  |
| **Mixto (HITL)** | Human-in-the-Loop, colaboración        | Validador con apoyo IA               |

#### Dimensión 2: Cognición (¿Qué NIVEL de decisión?)

| Nivel  | Nombre           | Descripción                           | Ejemplos                         |
| ------ | ---------------- | ------------------------------------- | -------------------------------- |
| **C0** | Ejecutar         | Determinístico, sin decisión          | RPA, Sensor, Scheduler           |
| **C1** | Decidir          | Selección entre opciones predefinidas | Motor de reglas, Clasificador ML |
| **C2** | Reflexionar      | Metacognición sobre el proceso        | Agente LLM con contexto          |
| **C3** | Meta-Reflexionar | Reflexión sobre la reflexión          | Estratega humano, Arquitecto     |

#### Invariante HAIC (Human-AI Collaboration)

> **Todo agente algorítmico (Sustrato = Algorítmico) DEBE tener un `accountable_id` humano.** La accountability moral es siempre humana e intransferible.

| Modo   | Nombre     | Descripción                                      |
| ------ | ---------- | ------------------------------------------------ |
| **M1** | Monitorear | IA observa, humano decide                        |
| **M2** | Informar   | IA sugiere, humano decide                        |
| **M3** | Habilitar  | Humano invoca, IA ejecuta supervisada            |
| **M4** | Controlar  | IA decide (reglas), humano maneja excepciones    |
| **M5** | Coproducir | Humano + IA colaboran par-a-par                  |
| **M6** | Ejecutar   | IA autónoma (acotada), humano supervisa/override |

### Principio Transversal: Cumplimiento Normativo

> **Todo el sistema opera bajo el principio del cumplimiento normativo**, respetando el marco legal y regulatorio que rige la administración pública y, en particular, a los gobiernos regionales.

| Marco                      | Alcance                | Impacto en GORE_OS            |
| -------------------------- | ---------------------- | ----------------------------- |
| LOC GORE (19.175)          | Atribuciones y límites | Define funciones motoras      |
| Ley 21.180 (TDE)           | Transformación Digital | Interoperabilidad obligatoria |
| Ley 19.886 (Compras)       | Contratación pública   | Integración MercadoPúblico    |
| Ley 20.285 (Transparencia) | Acceso a información   | Datos abiertos                |

### Mecanismos de Financiamiento

| Mecanismo         | Descripción                                          | Dominio |
| ----------------- | ---------------------------------------------------- | ------- |
| **FNDR**          | Fondo Nacional de Desarrollo Regional                | D-FIN   |
| **FRIL**          | Fondo Regional de Iniciativa Local                   | D-FIN   |
| **FRPD**          | Fondo Regional para la Productividad y el Desarrollo | D-FIN   |
| **ISAR**          | Inversiones Sectoriales de Asignación Regional       | D-FIN   |
| **Subvención 8%** | Transferencias a instituciones sin fines de lucro    | D-FIN   |

---

## 4. Las 5 Funciones Motoras

El GORE opera mediante un ciclo integrado de cinco funciones que GORE_OS debe soportar:

### 4.1 Planificar

> Traducir la misión estratégica en instrumentos técnicos vinculantes.

| Instrumento | Descripción                               | Dominio GORE_OS |
| ----------- | ----------------------------------------- | --------------- |
| ERD         | Estrategia Regional de Desarrollo         | D-PLAN          |
| PROT        | Plan Regional de Ordenamiento Territorial | D-LOC           |
| ARI         | Anteproyecto Regional de Inversiones      | D-FIN           |

### 4.2 Financiar

> Administrar y asignar recursos según la estrategia regional.

| Capacidad               | Descripción                | Dominio GORE_OS |
| ----------------------- | -------------------------- | --------------- |
| Portafolio de inversión | Gestión activa de fondos   | D-FIN           |
| Priorización            | Motor de recomendación     | D-FIN           |
| Trazabilidad            | Seguimiento de desembolsos | D-EJE           |

### 4.3 Ejecutar

> Implementar programas y viabilizar proyectos de inversión.

| Capacidad                  | Descripción              | Dominio GORE_OS |
| -------------------------- | ------------------------ | --------------- |
| Convenios de transferencia | Marco legal de ejecución | D-EJE           |
| Estados de pago            | Control de hitos         | D-EJE           |
| Bitácora de obra           | Registro de inspecciones | D-EJE           |

### 4.4 Coordinar

> Alinear servicios sectoriales, municipios y nivel central.

| Capacidad                 | Descripción                    | Dominio GORE_OS |
| ------------------------- | ------------------------------ | --------------- |
| Gabinete regional         | Coordinación de actores        | D-GOV           |
| Convenios de programación | Co-inversión con nivel central | D-GOV           |
| Servicios a municipios    | Nivelación de capacidades      | D-ORG           |

### 4.5 Normar

> Dictar normas generales para regular procedimientos regionales.

| Capacidad              | Descripción       | Dominio GORE_OS |
| ---------------------- | ----------------- | --------------- |
| Reglamentos regionales | Normas internas   | D-NORM          |
| Estándares de datos    | Interoperabilidad | D-DIG           |

---

## 5. Límites y Restricciones

### Lo que GORE_OS NO es

- ❌ No reemplaza a ClaveÚnica (Identidad delegada)
- ❌ No reemplaza a DocDigital (Comunicaciones oficiales)
- ❌ No administra pagos (Delegado a TGR/BancoEstado)
- ❌ No ejecuta obras directamente (Rol de Unidad Técnica)

### Controles Externos

| Actor  | Control                          | Impacto en GORE_OS              |
| ------ | -------------------------------- | ------------------------------- |
| MDSF   | Recomendación Satisfactoria (RS) | Prerequisito para financiar IPR |
| DIPRES | Arquitectura presupuestaria      | Estructura de programas         |
| CGR    | Toma de Razón                    | Validación legal de actos       |
| CORE   | Aprobación de inversiones        | Workflow de aprobación          |

---

## 6. Visión GORE 4.0

### El GORE como Motor Proactivo de Desarrollo

En condiciones ideales, GORE_OS evoluciona hacia un modelo **GORE 4.0** que fusiona el mandato de desarrollo con tecnologías de la Cuarta Revolución Industrial:

| Función    | Capacidad 4.0                    | Estado      |
| ---------- | -------------------------------- | ----------- |
| Planificar | Gemelo Digital del territorio    | 🔜 Futuro    |
| Financiar  | Smart contracts para desembolsos | 🔜 Futuro    |
| Ejecutar   | PMO con monitoreo IoT            | 🔜 Futuro    |
| Coordinar  | APIs de datos abiertos           | ⏳ En diseño |
| Normar     | Sandboxes regulatorios           | 🔜 Futuro    |

### Principio Rector

> **"El GORE deja de ser una entidad principalmente reactiva y se convierte en motor proactivo de desarrollo, innovación y gobernanza territorial."**
> — Visión GORE 4.0

---

## 7. Transformación Digital del Estado (TDE)

La **Transformación Digital del Estado** se integra en GORE_OS desde una doble perspectiva:

### 7.1 Obligación Normativa

La Ley 21.180 y sus normas técnicas constituyen un **roadmap obligatorio** para las instituciones públicas:

| Componente TDE     | Descripción                       | Integración GORE_OS           |
| ------------------ | --------------------------------- | ----------------------------- |
| **ClaveÚnica**     | Identidad digital ciudadana       | Autenticación federada        |
| **DocDigital**     | Gestión documental electrónica    | Comunicaciones oficiales      |
| **PISEE**          | Interoperabilidad del Estado      | Consulta de datos (Once-Only) |
| **Firma Avanzada** | Validación jurídica de documentos | Actos administrativos         |

### 7.2 Oportunidad de Liderazgo Regional

GORE_OS aprovecha estratégicamente la TDE como **plataforma para impulsar la gobernanza de la transformación digital** en los servicios públicos y municipalidades de Ñuble:

- **Rol de Coordinador**: El GORE habilita a municipios con herramientas y capacitación
- **Efecto Demostración**: GORE_OS como modelo replicable de modernización
- **Datos Regionales**: Centro de inteligencia territorial compartida

---

## 8. ORKO: Marco de Operación y Evolución

**ORKO** es el framework principal para la operación, gestión, mejoramiento continuo y evolución de GORE_OS. Proporciona la base axiomática irreducible del sistema.

> URN: `urn:knowledge:orko:*`

### Axiomas Fundamentales (A1-A5)

Verdades fundamentales no derivables que constituyen el "genoma ontológico" del sistema:

| Axioma | Nombre          | Enunciado                                                      |
| ------ | --------------- | -------------------------------------------------------------- |
| **A1** | Transformación  | Todo sistema existe para transformar estados (S₁ → S₂)         |
| **A2** | Capacidad       | Existe capacidad que efectúa la transformación (no espontánea) |
| **A3** | Información     | Existe estructura portadora de significado que coordina        |
| **A4** | Restricción     | No todo es posible; existen límites que acotan posibilidades   |
| **A5** | Intencionalidad | Transformación tiene propósito direccional (outcome deseado)   |

### Primitivos Operacionales (P1-P5)

Mínima estructura necesaria para operacionalizar los axiomas:

| Primitivo | Axioma Base | Aplicación en GORE_OS                                  |
| --------- | ----------- | ------------------------------------------------------ |
| **P1**    | A2          | Agente: Usuario-Rol con Sustrato y Cognición           |
| **P2**    | A1          | Flujo: Procesos como DAGs de transformaciones          |
| **P3**    | A3          | Información: Datos, señales, estados con lineage       |
| **P4**    | A4          | Límite: Restricciones normativas, técnicas, económicas |
| **P5**    | A5          | Propósito: OKRs, IPR como objetivo de desarrollo       |

### Invariantes del Sistema (I1-I8)

| Invariante | Nombre                 | Aplicación GORE_OS                                |
| ---------- | ---------------------- | ------------------------------------------------- |
| **I1**     | Minimalidad            | Sistema usa conjunto mínimo necesario (P1-P5)     |
| **I2**     | Ortogonalidad          | Primitivos mutuamente independientes              |
| **I3**     | Trazabilidad           | Todo artefacto tiene Lineage, Owner, Timestamp    |
| **I4**     | Clasificación          | Todo es Producción o Habilitación (contextual)    |
| **I5**     | HAIC (Primacía Humana) | Accountability humana obligatoria para IA         |
| **I6**     | Trajectory             | Capacidad algorítmica evoluciona con historial    |
| **I7**     | Emergencia             | Prácticas emergen según nivel de complejidad      |
| **I8**     | Adaptación             | Separación Genoma (rígido) vs Fenotipo (flexible) |

---

## 9. KODA: Artefactos de Conocimiento e IA

**KODA (Knowledge-Oriented Design Architecture)** es el marco específico para el trabajo con artefactos de conocimiento dentro del ecosistema GORE_OS.

> URN: `urn:knowledge:koda:*`

### Alcance KODA en GORE_OS

| Área                           | Aplicación                                    |
| ------------------------------ | --------------------------------------------- |
| **Documentación estructurada** | Todos los artefactos YAML siguen KODA/Spec    |
| **Agentes LLM**                | Diseño, desarrollo y gestión de asistentes IA |
| **Federación de conocimiento** | Catálogos URN para trazabilidad cross-repo    |
| **Validación y testing**       | Pruebas de comportamiento de agentes          |

### Agentes GORE_OS (KODA-compliant)

| Agente                | Rol                             | Estado   |
| --------------------- | ------------------------------- | -------- |
| **Arquitecto-GORE**   | Diseño ontológico y semántico   | ✅ Activo |
| **Ingeniero-GORE_OS** | Implementación y DevOps         | ✅ Activo |
| **Goreologo**         | Conocimiento institucional GORE | 🔜 Diseño |
| **PMO-Agent**         | Monitoreo de IPR y alertas      | 🔜 Diseño |

---

## Referencias

- **Documento Fuente**: `gorenuble/knowledge/domains/gn/intro/kb_gn_900_gore_ideal_koda.yml`
- **Framework ORKO**: `orko/` — Organizational Knowledge Ontology
- **Framework KODA**: `koda/` — Knowledge-Oriented Design Architecture
- **Ley Orgánica**: DFL N° 1-19.175 (LOC GORE)
- **Ley TDE**: Ley 21.180 de Transformación Digital del Estado
- **Versión**: 1.1.0
- **Fecha**: 2025-12-23

---

*Arquitecto KODA — Sistema Operativo del Gobierno Regional de Ñuble*
