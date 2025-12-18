# GORE_OS: Visión General

> **Versión:** 5.2 (Deep Audit Complete)  
> **Fecha:** 18 Diciembre 2025  
> **Estructura:** Blueprint Integral Unificado (12 dominios)

---

## A. FUNDAMENTOS

### 1. El Problema: Fragmentación Actual

El GORE de Ñuble opera hoy como un **sistema fragmentado**:

```text
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           ESTADO ACTUAL: FRAGMENTACIÓN                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│   │   SIGFE     │    │   BIP/SNI   │    │   SISREC    │    │  DocDigital │          │
│   │ (Finanzas)  │    │ (Proyectos) │    │(Rendiciones)│    │(Expedientes)│          │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘          │
│          │                  │                  │                  │                 │
│          ▼                  ▼                  ▼                  ▼                 │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                              EXCEL                                          │   │
│   │   • Consolidación manual          • Sin trazabilidad                        │   │
│   │   • Errores de transcripción      • Información desactualizada              │   │
│   │   • Versiones múltiples           • Sin alertas                             │   │
│   │   • Dependencia de personas       • Decisiones reactivas                    │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Síntomas específicos:**

| Área              | Síntoma                                | Impacto                               |
| ----------------- | -------------------------------------- | ------------------------------------- |
| **IPR**           | No hay visibilidad de cartera completa | Proyectos duplicados, mal priorizados |
| **Presupuesto**   | Información desfasada con SIGFE        | Subejecución ~15-20% anual            |
| **Rendiciones**   | Seguimiento manual en Excel            | Mora crónica, reparos CGR             |
| **Convenios**     | Sin alertas de vencimiento             | Caducidades, pérdida de recursos      |
| **Coordinación**  | Sin fuente única de verdad             | Actores desalineados                  |
| **Planificación** | ERD sin conexión con ejecución         | Estrategia desconectada               |

---

### 2. La Solución: GORE_OS como Plataforma Integral

**GORE_OS es la plataforma operativa integral del GORE Ñuble.**

No es un sistema de información tradicional. Es una **plataforma unificada** que opera mediante un **modelo integrado de funciones** organizadas en dimensiones estratégica, táctica y habilitante.

**Capacidades fundamentales:**

1. **Gestiona recursos institucionales**: Finanzas, personal, abastecimiento, activos, flota
2. **Gestiona actos y cumplimiento**: Procedimientos, expedientes, actos administrativos
3. **Gestiona relaciones territoriales**: Ejecutores, proveedores, ciudadanos, actores
4. **Gestiona inversión pública**: Ciclo completo IPR desde oportunidad hasta impacto
5. **Integra** sistemas externos obligatorios en vista unificada
6. **Automatiza** flujos y genera alertas predictivas
7. **Amplifica** capacidad decisional de cada funcionario

---

### 3. Principios Rectores

| Principio                     | Descripción                                              | Implicancia de Diseño                |
| ----------------------------- | -------------------------------------------------------- | ------------------------------------ |
| **Fuente Única de Verdad**    | Un dato, una fuente, muchos consumidores                 | No duplicar datos; integrar sistemas |
| **Automatización Progresiva** | Primero visibilidad, luego alertas, luego automatización | Capas incrementales de valor         |
| **Humano en el Centro**       | AI aumenta capacidad, no reemplaza juicio                | Decisiones finales siempre humanas   |
| **Cumplimiento Embebido**     | Normativa como reglas del sistema                        | Compliance by design (ver nota)      |
| **Trazabilidad Total**        | Cada acción tiene autor, fecha, razón                    | Auditoría automática                 |
| **Interoperabilidad Nativa**  | APIs primero, UI después                                 | Ecosistema abierto                   |
| **Conocimiento Estructurado** | Normativa, procesos y reglas como KB                     | Agentes consultan KB antes de actuar |
| **Agentes Especializados**    | Cada dominio tiene agentes que asisten                   | Delegación de tareas repetitivas     |

> **Nota sobre Cumplimiento:** GORE_OS distingue tres dimensiones:
>
> - **Cumplimiento Normativo General (D-NORM):** Probidad, Transparencia, Ley de Lobby, control CGR
> - **Cumplimiento Ley TDE (D-TDE):** DS 7-12, Ley 21.180, plazos cero papel, ciberseguridad
> - **Cumplimiento Embebido:** Principio transversal que integra ambos en las reglas del sistema

---

## B. MODELO CONCEPTUAL

### 4. Las 7 Funciones GORE

El GORE opera mediante un ciclo integrado de funciones organizadas en tres dimensiones:

```text
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                   MODELO DE FUNCIONES GORE: 7 FUNCIONES                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   DIMENSIÓN ESTRATÉGICA (El Rumbo)                                                   │
│   ┌───────────────────────────────────────────────────────────────────────────────┐  │
│   │  1. PLANIFICAR (D-PLAN)     │   2. GOBERNAR (D-GOB)                           │  │
│   │  ERD, PROT, ARI             │   CORE, Relaciones, Actores                     │  │
│   └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│   DIMENSIÓN TÁCTICA (El Motor de Desarrollo)                                         │
│   ┌───────────────────────────────────────────────────────────────────────────────┐  │
│   │  3. FINANCIAR (D-FIN)   │  4. EJECUTAR (D-EJEC)   │  5. COORDINAR (D-SEG)     │  │
│   │  IPR, Presupuesto       │  Convenios, PMO         │  Seguridad Pública        │  │
│   └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│   DIMENSIÓN HABILITANTE (El Soporte Operativo)                                       │
│   ┌───────────────────────────────────────────────────────────────────────────────┐  │
│   │  6. NORMAR (D-NORM)         │   7. ADMINISTRAR (D-BACK)                       │  │
│   │  Actos, Procedimientos      │   Personas, Finanzas, Bienes                    │  │
│   └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

> **Nota:** Las funciones habilitantes (NORMAR, ADMINISTRAR) no son menos importantes; son la base que permite que el motor de desarrollo funcione con certeza jurídica y recursos adecuados.

---

### 5. Arquitectura de Capas

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA GORE_OS v5.1                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CAPA DE EVOLUCIÓN                                                               │
│  └── D-EVOL: Framework ORKO, HAIC, Madurez L0-L5, Agentes IA, H_org              │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CAPA TRANSVERSAL                                                                │
│  ├── D-GESTION: OKRs, H_gore, Playbooks, UCI, Mejora Continua                    │
│  └── FÉNIX: Departamento de Gestión Institucional (Intervenciones Nivel I-IV)   │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  NÚCLEOS TÁCTICOS (Motor de Desarrollo)                                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                           │
│  │ FINANCIAR     │ │ EJECUTAR      │ │ COORDINAR     │                           │
│  │ (D-FIN)       │ │ (D-EJEC)      │ │ (D-SEG)       │                           │
│  │ IPR, Rend.    │ │ Convenios,PMO │ │ CIES, SITIA   │                           │
│  └───────────────┘ └───────────────┘ └───────────────┘                           │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CAPAS HABILITANTES (Soporte Operativo)                                          │
│  ├── D-PLAN: Planificación estratégica (ERD, PROT, ARI, CDP)                     │
│  ├── D-GOB: Gobernanza y Relacionamiento Regional (CORE, Actores, CRM)           │
│  ├── D-NORM: Gestión Jurídico-Administrativa y Cumplimiento                      │
│  ├── D-BACK: Gestión de Recursos Institucionales (RRHH, Compras, Flota)          │
│  ├── D-TDE: Gobernanza Digital y Ciberseguridad (Ley 21.180)                     │
│  └── D-TERR: Inteligencia Territorial y GIS (IDE Regional)                       │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## C. DOMINIOS GORE_OS

### 6. Mapa de Dominios (Blueprint v5.1)

| #   | Dominio                                | Código    | Capa        | Función     | Doc. Detalle                                       |
| --- | -------------------------------------- | --------- | ----------- | ----------- | -------------------------------------------------- |
| 1   | Gestión Financiera e Inversión Pública | D-FIN     | Núcleo      | FINANCIAR   | [domain_d-fin.md](domains/domain_d-fin.md)         |
| 2   | Gestión Jurídico-Administrativa        | D-NORM    | Habilitante | NORMAR      | [domain_d-norm.md](domains/domain_d-norm.md)       |
| 3   | Gestión de Recursos Institucionales    | D-BACK    | Habilitante | ADMINISTRAR | [domain_d-back.md](domains/domain_d-back.md)       |
| 4   | Planificación Estratégica              | D-PLAN    | Habilitante | PLANIFICAR  | [domain_d-plan.md](domains/domain_d-plan.md)       |
| 5   | Ejecución y Seguimiento                | D-EJEC    | Núcleo      | EJECUTAR    | [domain_d-ejec.md](domains/domain_d-ejec.md)       |
| 6   | Seguridad Pública Regional             | D-SEG     | Núcleo      | COORDINAR   | [domain_d-seg.md](domains/domain_d-seg.md)         |
| 7   | Inteligencia Territorial               | D-TERR    | Habilitante | PLANIFICAR  | [domain_d-terr.md](domains/domain_d-terr.md)       |
| 8   | Gobernanza Digital                     | D-TDE     | Habilitante | GESTIONAR   | [domain_d-tde.md](domains/domain_d-tde.md)         |
| 9   | Gobernanza y Relacionamiento Regional  | D-GOB     | Estratégica | GOBERNAR    | [domain_d-gob.md](domains/domain_d-gob.md)         |
| 10  | Gestión Institucional                  | D-GESTION | Operativa   | GESTIONAR   | [domain_d-gestion.md](domains/domain_d-gestion.md) |
| 11  | Evolución e Inteligencia               | D-EVOL    | Estratégica | EVOLUCIONAR | [domain_d-evol.md](domains/domain_d-evol.md)       |
| 12  | Departamento Gestión Institucional     | FÉNIX     | Transversal | INTERVENIR  | [domain_fenix.md](domains/domain_fenix.md)         |

---

### 7. Resumen de Módulos por Dominio

| Dominio       | Módulos Principales                                                                                                                                        |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **D-PLAN**    | ERD Digital, PROT Digital, ARI/PROPIR Digital, CDP, Inteligencia Territorial, Planificación Participativa, Asistencia Técnica Municipal                    |
| **D-FIN**     | Captación Oportunidades, Capital Base, Portafolio IPR, Selector Mecanismos (FNDR/FRPD/C33/FRIL), Presupuesto, Rendiciones, Gestión Ejecutores              |
| **D-EJEC**    | Supervisión de Obras, Gestión de Convenios, PMO Regional (Torre de Control), Gestión de Compromisos, Coordinación Municipal, Relaciones Sectoriales        |
| **D-GOB**     | Consejo Regional (CORE), Despacho Gobernador, Descentralización, Coordinación/Emergencias (GRD), Gestión Relacional (CRM/Actores), Participación Ciudadana |
| **D-NORM**    | Actos Administrativos, Procedimientos (Ley 19.880), Expediente Electrónico, Cumplimiento/Control, Convenios (SSOT), Reglamentos, Biblioteca Normativa      |
| **D-BACK**    | RRHH/Personas, Abastecimiento/Compras, Inventarios, Activo Fijo, Flota Vehicular, Bienestar Funcionario, Contabilidad Operativa                            |
| **D-TDE**     | Cumplimiento TDE (CPAT), Servicios Digitales (ClaveÚnica/FirmaGob), Interoperabilidad (PISEE), Ciberseguridad/Datos, Liderazgo Digital Regional            |
| **D-TERR**    | Inteligencia Estratégica, IDE Regional (Servicios OGC), Analítica Territorial, Gobernanza de Datos Geo, Asistencia Urbanística DOM                         |
| **D-SEG**     | CIES Ñuble (Monitoreo 24/7), Prevención del Delito, Evidencias Digitales (SITIA), Gobernanza de Seguridad, Coordinación Multi-agencia                      |
| **D-GESTION** | System Management Control (SCG), H_gore Dashboard, Operational Playbooks, Internal Control (UCI), Continuous Improvement, Institutional Coordination       |
| **D-EVOL**    | Organizational Health (H_org), System Trajectory, Knowledge Base (KB), AI Agents (HAIC), Maturity Levels L0-L5, Technical Debt                             |
| **FÉNIX**     | Interventions Levels I-IV, Diagnosis & Activation, Contingency Management, Task Force, Initiative Acceleration, Institutional Learning                     |

---

## D. INTELIGENCIA

### 8. Base de Conocimiento Institucional

GORE_OS incorpora una **base de conocimiento estructurada** que permite a los agentes y al sistema operar con contexto institucional completo.

**Categorías de Conocimiento:**

| Categoría         | Contenido                                               | Fuente        |
| ----------------- | ------------------------------------------------------- | ------------- |
| **Normativo**     | Leyes, reglamentos, circulares, oficios interpretativos | D-NORM, D-TDE |
| **Procedimental** | Flujos de trabajo, playbooks, checklists                | D-GESTION     |
| **Institucional** | Estructura orgánica, roles, responsabilidades           | D-BACK, D-GOB |
| **Histórico**     | Decisiones previas, jurisprudencia, lecciones           | D-EVOL, FÉNIX |
| **Territorial**   | Capas GIS, indicadores, brechas                         | D-TERR        |

**Políticas de Uso (D-EVOL):**

| Política      | Descripción                        | Caso de Uso           |
| ------------- | ---------------------------------- | --------------------- |
| USO_EXCLUSIVO | Solo usar artefactos especificados | Respuestas normativas |
| HÍBRIDO       | KB + conocimiento general LLM      | Consultas abiertas    |
| TIEMPO_REAL   | KB + búsqueda web                  | Datos actuales        |

---

### 9. Catálogo de Agentes Especializados

| Agente                          | Dominio        | Función Principal                                                                   | Interacción                    |
| ------------------------------- | -------------- | ----------------------------------------------------------------------------------- | ------------------------------ |
| **Analista de Ejecución**       | D-FIN          | Monitorea ejecución presupuestaria, proyecta cierre, identifica riesgos             | Alertas proactivas, dashboards |
| **Monitor de Inversiones**      | D-FIN + D-EJEC | Seguimiento de cartera IPR, alertas de estancamiento                                | Notificaciones, reportes       |
| **Verificador de Cumplimiento** | D-NORM         | Valida cumplimiento normativo en actos, procedimientos y documentos                 | Checklist automático           |
| **Asesor de Mecanismos**        | D-FIN          | Recomienda mecanismo de financiamiento apropiado según características del proyecto | Chat interactivo               |
| **Generador de Reportes**       | Transversal    | Produce informes para CORE, CGR, DIPRES en formatos requeridos                      | Generación automática          |
| **Asistente Documental**        | D-NORM         | Ayuda en redacción de actos administrativos, resoluciones, convenios                | Plantillas SFD/STS             |
| **Monitor H_gore**              | D-GESTION      | Alerta sobre desviaciones en salud operativa diaria                                 | Dashboard, escalamiento        |
| **Coordinador CIES**            | D-SEG          | Gestiona incidentes y coordinación multi-agencia                                    | Alertas tiempo real            |

**Gobernanza HAIC (Human-AI Collaboration):**

| Nivel Autonomía | Descripción                           | Ejemplo                          |
| --------------- | ------------------------------------- | -------------------------------- |
| M1              | Solo sugerencias                      | Recomendaciones de mecanismo     |
| M2              | Ejecución con aprobación              | Generación de borradores         |
| M3              | Ejecución autónoma con supervisión    | Alertas automáticas              |
| M4              | Ejecución autónoma en casos definidos | Clasificación de incidentes CIES |
| M5              | Orquestación de otros agentes         | Gestión de casos complejos       |
| M6              | Decisiones autónomas en tiempo real   | Respuesta a emergencias críticas |

---

### 10. Indicadores de Salud del Sistema

**H_gore (D-GESTION) - Tactical Health Score:**

| Dimension             | Weight | Components                        |
| --------------------- | ------ | --------------------------------- |
| Budget Execution      | 20%    | % execution, deviation vs plan    |
| IPR Portfolio         | 20%    | % progress, projects at risk      |
| Accountabilities      | 20%    | % mora, avg review days           |
| Regulatory Compliance | 15%    | UCI/CGR findings, timely sumaries |
| Agreements            | 10%    | % active OK, near expirations     |
| TDE Compliance        | 10%    | % norms met, gaps                 |
| Satisfaction          | 5%     | Internal NPS, response times      |

**H_org (D-EVOL) - Strategic Maturity Score:**

> Formula: Purpose(P5)×0.30 + Flow(P2)×0.30 + Capacity(P1)×0.20 + Information(P3)×0.10 + Governance(P4)×0.10

| Status     | H_org Range | Recommended Action                       |
| ---------- | ----------- | ---------------------------------------- |
| 🔴 Critical | < 0.50      | Survival Kit (Immediate stabilization)   |
| 🟡 Stable   | 0.50-0.70   | Minimal Kit (Consolidation 6-12 weeks)   |
| 🟢 Healthy  | > 0.70      | Advanced Kit (Transformation 3-6 months) |

---

## E. IMPLEMENTACIÓN

### 11. Integraciones Obligatorias

| Sistema         | Función                                       | Prioridad | Dominio Principal |
| --------------- | --------------------------------------------- | --------- | ----------------- |
| SIGFE           | Contabilidad gubernamental, devengado, pagado | P0        | D-FIN, D-BACK     |
| BIP/SNI         | Banco Integrado de Proyectos, RS, estados     | P0        | D-FIN             |
| SISREC          | Rendiciones de cuentas a CGR                  | P0        | D-FIN, D-EJEC     |
| Mercado Público | Órdenes de compra, contratos, proveedores     | P0        | D-BACK            |
| DocDigital      | Gestión documental, expediente electrónico    | P1        | D-NORM            |
| ClaveÚnica      | Autenticación ciudadana (OIDC)                | P1        | D-TDE             |
| SIAPER          | Registro de personal y toma de razón ante CGR | P1        | D-BACK            |
| PISEE           | Bus de interoperabilidad del Estado           | P1        | D-TDE             |
| SITIA           | Plataforma nacional de televigilancia         | P1        | D-SEG             |
| FirmaGob        | Firma electrónica avanzada                    | P1        | D-TDE, D-NORM     |

---

### 12. Dependencias Críticas entre Dominios

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DEPENDENCIAS ENTRE DOMINIOS                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  D-PLAN ──────────────────────────────────────────────────────────────────────▶  │
│    │  ERD, PROT, ARI alimentan priorización de IPR                              │
│    │  ◀───── D-SEG (Política Regional Seguridad → Eje Seguridad ERD)            │
│    │  ◀───── D-TERR (Validación PROT, indicadores territoriales)                │
│    ▼                                                                             │
│  D-FIN ◀──────────────────────────────────────────────────────────────────────▶  │
│    │  IPR, Presupuesto, Rendiciones, Rating Ejecutores                          │
│    │  ◀───── D-EJEC (Ejecución operativa de convenios)                          │
│    │  ◀───── D-GOB (Actor como Ejecutor, SSOT CRM)                              │
│    │  ◀───── D-SEG (Proyectos Seguridad heredan IPR)                            │
│    ▼                                                                             │
│  D-EJEC ◀────────────────────────────────────────────────────────────────────▶   │
│    │  Convenios, PMO, Estados de Pago, Supervisión                              │
│    │  ───▶ D-NORM (Convenio SSOT, Actos Aprobatorios)                           │
│    │  ───▶ D-TERR (Geolocalización de obras)                                    │
│    │  ───▶ FÉNIX (Proyectos en riesgo activan intervención)                     │
│    ▼                                                                             │
│  D-SEG ◀─────────────────────────────────────────────────────────────────────▶   │
│    │  Seguridad Pública Regional (CIES + División Prevención)                   │
│    │  ───▶ D-GOB (Consejo Regional Seguridad, Municipios)                       │
│    │  ───▶ D-NORM (Convenios Seguridad, Cadena Custodia)                        │
│    │  ───▶ D-TDE (Infraestructura CIES, Ciberseguridad, SITIA)                  │
│    │  ───▶ D-TERR (Georreferenciación incidentes, Mapas calor)                  │
│    ▼                                                                             │
│  D-GOB ◀─────────────────────────────────────────────────────────────────────▶   │
│    │  CORE aprueba instrumentos, presupuesto; Directorio de Actores (SSOT)      │
│    │  ───▶ D-FIN (Actor rol Ejecutor)                                           │
│    │  ───▶ D-BACK (Actor rol Proveedor)                                         │
│    ▼                                                                             │
│  D-NORM ─────────────────────────────────────────────────────────────────────▶   │
│    │  Convenio SSOT, Actos aprobatorios, Procedimientos                         │
│    │  ───▶ D-EJEC (Ejecución operativa)                                         │
│    │  ───▶ D-TDE (Expediente Electrónico DS 10)                                 │
│    ▼                                                                             │
│  D-BACK ─────────────────────────────────────────────────────────────────────▶   │
│    │  Recursos institucionales (personas, compras, flota, contabilidad)         │
│    │  ◀───── D-GOB (Proveedor desde Directorio Actores)                         │
│    │  ◀───── D-SEG (Personal CIES, Equipamiento)                                │
│    ▼                                                                             │
│  D-TERR ─────────────────────────────────────────────────────────────────────▶   │
│    │  Capas GIS, indicadores territoriales, IDE Regional                        │
│    │  ───▶ D-PLAN (Validación PROT, indicadores ERD)                            │
│    │  ───▶ D-FIN (Localización IPR)                                             │
│    │  ◀───── D-SEG (Capa incidentes, cobertura cámaras)                         │
│    ▼                                                                             │
│  D-TDE ◀─────────────────────────────────────────────────────────────────────▶   │
│    │  Cumplimiento Ley TDE (piso normativo), Servicios Digitales, Ciberseguridad│
│    │  ◀───── D-SEG (Red CIES 316 nodos, Interoperabilidad SITIA)                │
│    │  ───▶ D-NORM (Expediente Electrónico conforme DS 10)                       │
│    │  ───▶ Municipios (Liderazgo Digital Regional)                              │
│    ▼                                                                             │
│  D-GESTION ◀─────────────────────────────────────────────────────────────────▶   │
│    │  H_gore, OKRs, Playbooks, UCI, Mejora Continua                             │
│    │  ───▶ FÉNIX (H_gore < 50 activa intervención Nivel IV)                     │
│    │  ◀───── D-EVOL (H_org para madurez sistémica)                              │
│    ▼                                                                             │
│  D-EVOL ◀────────────────────────────────────────────────────────────────────▶   │
│    │  Evolución nativa (techo estratégico), Agentes IA, KB                      │
│    │  ───▶ Todos los dominios (Automatización, Analytics, Madurez L0-L5)        │
│    ▼                                                                             │
│  FÉNIX ◀─────────────────────────────────────────────────────────────────────▶   │
│       Capacidad transversal de intervención (Niveles I-IV)                      │
│       ◀───── D-GESTION (H_gore < 50), D-EJEC (IPR estancadas > 90 días)         │
│       ◀───── D-SEG (Crisis seguridad), D-FIN (Rendiciones mora > 180 días)      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 13. Niveles de Madurez (D-EVOL)

| Nivel | Nombre       | Características                                    |
| ----- | ------------ | -------------------------------------------------- |
| L0    | INICIAL      | Procesos ad-hoc, sin estandarización               |
| L1    | DIGITALIZADO | Captura digital, repositorio único, trazabilidad   |
| L2    | INTEGRADO    | Flujos automatizados, dashboards, alertas básicas  |
| L3    | AUTOMATIZADO | IA asistente, predictivo, flujos inteligentes      |
| L4    | INTELIGENTE  | IA autónoma supervisada, optimización continua     |
| L5    | AUTÓNOMO     | IA estratégica, auto-mejora, gobernanza automática |

---

### 14. Metas a 5 Años

| Indicador                              | Año 1 | Año 3 | Año 5 |
| -------------------------------------- | ----- | ----- | ----- |
| Ejecución presupuestaria               | 85%   | 92%   | 97%   |
| Mora rendiciones                       | <15%  | <5%   | <2%   |
| Convenios sin alertas de vencimiento   | 0%    | 100%  | 100%  |
| Proyectos con seguimiento automatizado | 30%   | 80%   | 100%  |
| Nivel madurez (L0-L5)                  | L1    | L3    | L4    |

---

### 15. Próximos Pasos

| Paso  | Descripción                                       | Artefacto Esperado         |
| ----- | ------------------------------------------------- | -------------------------- |
| **1** | Detallar integraciones con sistemas externos      | Documento de integraciones |
| **2** | Definir arquitectura técnica (stack, capas, APIs) | Documento de arquitectura  |
| **3** | Especificar modelo de datos unificado             | Diagrama ER consolidado    |
| **4** | Diseñar MVP (alcance Fase 1)                      | Backlog priorizado         |
| **5** | Validar con stakeholders GORE                     | Acta de validación         |

---

## F. ESTRUCTURA DE DOCUMENTACIÓN

```text
docs/blueprint/
├── vision_general.md          ← Este documento (principal)
├── governance/
│   └── marco_coexistencia_ptd_goreos.md ← Reglas TDE/PMG
└── domains/
    ├── _manifest.yml          ← Índice maestro de dominios
    ├── domain_d-plan.md       ← D-PLAN: Planificación Estratégica
    ├── domain_d-fin.md        ← D-FIN: Gestión Financiera e Inversión
    ├── domain_d-ejec.md       ← D-EJEC: Ejecución y Seguimiento
    ├── domain_d-gob.md        ← D-GOB: Gobernanza y Relacionamiento
    ├── domain_d-norm.md       ← D-NORM: Gestión Jurídico-Administrativa
    ├── domain_d-back.md       ← D-BACK: Gestión de Recursos
    ├── domain_d-tde.md        ← D-TDE: Gobernanza Digital
    ├── domain_d-terr.md       ← D-TERR: Inteligencia Territorial
    ├── domain_d-seg.md        ← D-SEG: Seguridad Pública Regional
    ├── domain_d-gestion.md    ← D-GESTION: Gestión Institucional
    ├── domain_d-evol.md       ← D-EVOL: Evolución e Inteligencia
    └── domain_fenix.md        ← FÉNIX: Departamento Gestión Institucional
```

---

*Documento generado como parte del proceso de diseño de GORE_OS.*  
*Versión: 5.2 (Consolidada y Sincronizada) | Fecha: 18 Diciembre 2025*  
*Última sincronización con dominios: 2025-12-18*
