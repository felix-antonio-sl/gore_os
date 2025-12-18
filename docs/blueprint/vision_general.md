# GORE_OS: Visión General

> **Versión:** 5.0 (Consolidad)  
> **Fecha:** 16 Diciembre 2025  
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

### 4. Las 6 Funciones GORE: Motor + Soporte

El GORE opera mediante un ciclo integrado de funciones organizadas en tres dimensiones:

```text
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                   MODELO DE FUNCIONES GORE: MOTOR + SOPORTE                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   DIMENSIÓN ESTRATÉGICA (El Rumbo)                                                   │
│   ┌───────────────────────────────────────────────────────────────────────────────┐  │
│   │                          1. PLANIFICAR (D-PLAN)                               │  │
│   │                    ERD, PROT, ARI → Qué lograr y dónde                        │  │
│   └───────┬───────────────────────────────────────────────────────────────┬───────┘  │
│           │                                                               │          │
│           ▼                                                               ▼          │
│   DIMENSIÓN TÁCTICA (El Motor de Desarrollo)                                         │
│   ┌───────────────────┐     ┌───────────────────┐                                    │
│   │   2. FINANCIAR    │     │    3. EJECUTAR    │                                    │
│   │   (D-FIN)         │◀───▶│    (D-EJEC)       │                                    │
│   │   IPR, Presupuesto│     │   Convenios, Obras│                                    │
│   └─────────┬─────────┘     └─────────┬─────────┘                                    │
│             │                         │                                              │
│   ══════════╪═════════════════════════╪══════════════════════════════════════════════│
│             ▼                         ▼                         ▼                    │
│   DIMENSIÓN HABILITANTE (El Soporte Operativo)                                       │
│   ┌───────────────────────────────────────────────────────────────────────────────┐  │
│   │                          5. NORMAR (D-NORM)                                   │  │
│   │             Actos, Procedimientos, Cumplimiento → Certeza jurídica            │  │
│   ├───────────────────────────────────────────────────────────────────────────────┤  │
│   │                          6. ADMINISTRAR (D-BACK)                              │  │
│   │             Personas, Finanzas, Bienes, TIC → Recursos institucionales        │  │
│   └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│   Ref: kb_gn_900_gore_ideal_koda.yml (Motor_Cinco_Funciones + Dimensión Habilitante) │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

> **Nota:** Las funciones habilitantes (NORMAR, ADMINISTRAR) no son menos importantes; son la base que permite que el motor de desarrollo funcione con certeza jurídica y recursos adecuados.

---

### 5. Arquitectura de Capas

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA GORE_OS                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CAPA DE EVOLUCIÓN                                                              │
│  └── D-EVOL: Framework ORKO, HAIC, Madurez L0-L5, Agentes IA                   │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CAPA TRANSVERSAL                                                               │
│  └── D-GESTION: OKRs, H_gore, Playbooks, Mejora Continua                        │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  NÚCLEOS TÁCTICOS (Motor de Desarrollo)                                          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                             │
│  │ FINANCIAR     │ │ EJECUTAR      │ │ PROTEGER      │                             │
│  │ (D-FIN)       │ │ (D-EJEC)      │ │ (D-SEG)       │                             │
│  └───────────────┘ └───────────────┘ └───────────────┘                             │
│                                                                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CAPAS HABILITANTES (Soporte Operativo)                                         │
│  ├── D-PLAN: Planificación estratégica (ERD, PROT, ARI)                         │
│  ├── D-NORM: Gestión Jurídico-Administrativa (función NORMAR)                  │
│  ├── D-BACK: Gestión de Recursos (función ADMINISTRAR)                         │
│  ├── D-TDE: Gobernanza Digital y Ciberseguridad                                │
│  └── D-TERR: Inteligencia territorial y GIS                                     │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## C. DOMINIOS GORE_OS

### 6. Mapa de Dominios (Blueprint v5.0)

| #   | Dominio                    | Código    | Capa        | Función     | Estado |
| --- | -------------------------- | --------- | ----------- | ----------- | ------ |
| 1   | Gestión Financiera         | D-FIN     | Núcleo      | FINANCIAR   | ✅ 100% |
| 2   | Gestión Jurídico-Adm.      | D-NORM    | Habilitante | NORMAR      | ✅ 100% |
| 3   | Gestión de Recursos Inst.  | D-BACK    | Habilitante | ADMINISTRAR | ✅ 100% |
| 4   | Planificación Estratégica  | D-PLAN    | Habilitante | PLANIFICAR  | ✅ 100% |
| 5   | Ejecución y Seguimiento    | D-EJEC    | Núcleo      | EJECUTAR    | ✅ 100% |
| 6   | Seguridad Pública Regional | D-SEG     | Núcleo      | PROTEGER    | ✅ 100% |
| 7   | Inteligencia Territorial   | D-TERR    | Habilitante | -           | ✅ 100% |
| 8   | Gobernanza Digital         | D-TDE     | Habilitante | -           | ✅ 100% |
| 9   | Gobernanza Regional        | D-GOB     | Estratégica | GOBERNAR    | ✅ 100% |
| 10  | Gestión Institucional      | D-GESTION | Operativa   | GESTIONAR   | ✅ 100% |
| 11  | Evolución e Inteligencia   | D-EVOL    | Estratégica | EVOLUCIONAR | ✅ 100% |
| 12  | Sistema FÉNIX              | FENIX     | Transversal | INTERVENIR  | ✅ 100% |

### 7. Resumen de Módulos por Dominio

| Dominio            | Módulos Principales                                                                                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **D-PLAN**         | ERD Digital, PROT Digital, ARI/PROPIR Digital, Inteligencia Territorial                                                                                                       |
| **D-FIN**          | Captación Oportunidades, Capital Base, Portafolio IPR, Selector Mecanismos, Presupuesto, Rendiciones, Gestión Ejecutores, Evaluación Continua, IPR Problemáticas, Retorno IDR |
| **D-EJEC**         | Convenios, PMO Regional                                                                                                                                                       |
| **D-GOB**          | Gobernanza Política, Gabinete, Descentralización, **Gestión Relacional (Actores)**, Participación Ciudadana                                                                   |
| **D-NORM**         | Actos Administrativos, Procedimientos, Expediente Electrónico, Cumplimiento/Control, Convenios (SSOT), Reglamentos, Biblioteca Normativa                                      |
| **D-BACK**         | RRHH/Personas, Abastecimiento, Inventarios, Activo Fijo, Flota, Bienestar, Tesorería                                                                                          |
| **D-TDE**          | CPAT Institucional, Interoperabilidad, Ciberseguridad, Gobernanza Regional TDE                                                                                                |
| **D-TERR**         | IDE Regional, Observatorio Regional, Visor Geoespacial                                                                                                                        |
| **D-GESTION**      | OKRs Institucionales, H_gore, Playbooks Operativos, Mejora Continua                                                                                                           |
| **D-EVOL**         | Niveles Madurez, Gobierno Datos, Automatizaciones, Agentes IA, Analytics Avanzado                                                                                             |
| **D-GINT (FÉNIX)** | Intervenciones Nivel I-IV, Diagnóstico, Gestión de Contingencias, Aceleración                                                                                                 |
| **D-SEG**          | Gobernanza Seguridad, Cartera Proyectos Seguridad, Operaciones CIES, Integración SITIA                                                                                        |

---

## D. INTELIGENCIA

### 8. Base de Conocimiento Institucional

GORE_OS incorpora una **base de conocimiento estructurada** que permite a los agentes y al sistema operar con contexto institucional completo.

**Categorías de Conocimiento:**

- **Normativo:** Leyes, reglamentos, circulares, oficios interpretativos
- **Procedimental:** Flujos de trabajo, playbooks, checklists
- **Institucional:** Estructura orgánica, roles, responsabilidades
- **Histórico:** Decisiones previas, jurisprudencia administrativa, lecciones aprendidas

### 9. Catálogo de Agentes Especializados

| Agente                          | Dominio        | Función Principal                                                                   | Interacción                    |
| ------------------------------- | -------------- | ----------------------------------------------------------------------------------- | ------------------------------ |
| **Analista de Ejecución**       | D-FIN          | Monitorea ejecución presupuestaria, proyecta cierre, identifica riesgos             | Alertas proactivas, dashboards |
| **Monitor de Inversiones**      | D-FIN + D-EJEC | Seguimiento de cartera IPR, alertas de estancamiento                                | Notificaciones, reportes       |
| **Verificador de Cumplimiento** | D-NORM         | Valida cumplimiento normativo en actos, procedimientos y documentos                 | Checklist automático           |
| **Asesor de Mecanismos**        | D-FIN          | Recomienda mecanismo de financiamiento apropiado según características del proyecto | Chat interactivo               |
| **Generador de Reportes**       | Transversal    | Produce informes para CORE, CGR, DIPRES en formatos requeridos                      | Generación automática          |
| **Asistente Documental**        | D-NORM         | Ayuda en redacción de actos administrativos, resoluciones, convenios                | Plantillas SFD/STS             |

### 10. Gobernanza del Conocimiento

| Rol                 | Responsabilidad                                 |
| ------------------- | ----------------------------------------------- |
| **Knowledge Owner** | Define estructura y prioridades de la KB        |
| **Domain Expert**   | Valida contenido técnico por área               |
| **Content Curator** | Mantiene actualizado el contenido               |
| **Agent Trainer**   | Ajusta comportamiento de agentes según feedback |

---

## E. IMPLEMENTACIÓN

### 11. Integraciones Obligatorias

| Sistema         | Función                                       | Prioridad |
| --------------- | --------------------------------------------- | --------- |
| SIGFE           | Contabilidad gubernamental, devengado, pagado | P0        |
| BIP/SNI         | Banco Integrado de Proyectos, RS, estados     | P0        |
| SISREC          | Rendiciones de cuentas a CGR                  | P0        |
| Mercado Público | Órdenes de compra, contratos, proveedores     | P0        |
| DocDigital      | Gestión documental, expediente electrónico    | P1        |
| ClaveÚnica      | Autenticación ciudadana                       | P1        |
| SIAPER/SIGPER   | Gestión de personal del Estado                | P1        |

### 12. Dependencias Críticas

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DEPENDENCIAS ENTRE DOMINIOS                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  D-PLAN ──────────────────────────────────────────────────────────────────────▶ │
│    │  ERD, PROT, ARI alimentan priorización de IPR                              │
│    │  ◀───── D-SEG (Política Regional Seguridad → Eje Seguridad ERD)            │
│    ▼                                                                             │
│  D-FIN ◀──────────────────────────────────────────────────────────────────────▶ │
│    │  IPR, Presupuesto, Rendiciones, Rating Ejecutores                          │
│    │  ◀───── D-EJEC (Convenios operativos)                                      │
│    │  ◀───── D-GOB (Actor como ejecutor)                                        │
│    │  ◀───── D-SEG (Proyectos Seguridad heredan IPR con reglas especiales)      │
│    ▼                                                                             │
│  D-SEG ◀─────────────────────────────────────────────────────────────────────▶  │
│    │  Seguridad Pública Regional (División Prevención del Delito + CIES)        │
│    │  ───▶ D-GOB (Consejo Regional Seguridad, Municipios)                       │
│    │  ───▶ D-NORM (Convenios Seguridad, Cadena Custodia → Expediente)           │
│    │  ───▶ D-TDE (Infraestructura CIES, Ciberseguridad, Interop. SITIA)         │
│    │  ───▶ D-TERR (Georreferenciación incidentes, Mapas calor delictual)        │
│    │  ───▶ D-GINT (Crisis seguridad activan intervención Nivel I)               │
│    ▼                                                                             │
│  D-NORM ─────────────────────────────────────────────────────────────────────▶  │
│    │  Convenio SSOT, Actos aprobatorios                                         │
│    │  ───▶ D-EJEC (ejecución operativa del convenio)                            │
│    ▼                                                                             │
│  D-BACK ─────────────────────────────────────────────────────────────────────▶  │
│    │  Recursos institucionales (personas, finanzas, bienes)                     │
│    │  ◀───── D-GOB (Proveedor)                                                  │
│    │  ◀───── D-SEG (Personal CIES, Equipamiento, Mantenimiento)                 │
│    ▼                                                                             │
│  D-TERR ─────────────────────────────────────────────────────────────────────▶  │
│    │  Capas GIS, indicadores territoriales                                      │
│    │  ───▶ D-PLAN (validación PROT, indicadores ERD)                            │
│    │  ───▶ D-FIN (localización IPR)                                             │
│    │  ◀───── D-SEG (Capa incidentes, cobertura cámaras)                         │
│    ▼                                                                             │
│  D-TDE ◀─────────────────────────────────────────────────────────────────────── │
│    │  Cumplimiento Ley TDE (piso normativo)                                     │
│    │  ◀───── D-SEG (Red CIES 316 nodos, Interoperabilidad SITIA)                │
│    ▼                                                                             │
│  D-EVOL ◀────────────────────────────────────────────────────────────────────── │
│       Evolución nativa (techo estratégico)                                      │
│       Agentes IA operan sobre todos los dominios                                │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 13. Metas a 5 Años

| Indicador                              | Año 1 | Año 3 | Año 5 |
| -------------------------------------- | ----- | ----- | ----- |
| Ejecución presupuestaria               | 85%   | 92%   | 97%   |
| Mora rendiciones                       | <15%  | <5%   | <2%   |
| Convenios sin alertas de vencimiento   | 0%    | 100%  | 100%  |
| Proyectos con seguimiento automatizado | 30%   | 80%   | 100%  |
| Nivel madurez (L0-L5)                  | L1    | L3    | L4    |

### 14. Próximos Pasos

| Paso  | Descripción                                       | Artefacto Esperado         |
| ----- | ------------------------------------------------- | -------------------------- |
| **1** | Detallar integraciones con sistemas externos      | Documento de integraciones |
| **2** | Definir arquitectura técnica (stack, capas, APIs) | Documento de arquitectura  |
| **3** | Especificar modelo de datos unificado             | Diagrama ER consolidado    |
| **4** | Diseñar MVP (alcance Fase 1)                      | Backlog priorizado         |
| **5** | Validar con stakeholders GORE                     | Acta de validación         |

---

```text
docs/01_domain/
├── vision_general.md          ← Este documento (principal)
├── vision_general_legacy.md   ← Versión anterior completa (backup)
└── domains/
    ├── domain_d-plan.md       ← D-PLAN detallado
    ├── domain_d-fin.md        ← D-FIN detallado
    ├── domain_d-ejec.md       ← D-EJEC detallado
    ├── domain_d-norm.md       ← D-NORM detallado
    ├── domain_d-back.md       ← D-BACK detallado
    ├── domain_d-tde.md        ← D-TDE detallado
    ├── domain_d-terr.md       ← D-TERR detallado
    ├── domain_d-gestion.md    ← D-GESTION detallado
    ├── domain_d-evol.md       ← D-EVOL detallado
    ├── fenix.md               ← Dpto. Gestión Institucional (FÉNIX)
    └── domain_d-seg.md        ← D-SEG detallado (Seguridad Pública Regional)
```

---

*Documento generado como parte del proceso de diseño de GORE_OS.*
*Versión: 4.1 (Modular) | Fecha: Diciembre 2024*
*Última revisión: 15-12-2024 | Cambios: Integración D-SEG (División Prevención del Delito + CIES/SITIA)*
