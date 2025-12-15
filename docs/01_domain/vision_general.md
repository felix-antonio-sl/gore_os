# GORE_OS: Visión General

## Parte I: Fundamentos

### 1. El Problema Fundamental

El GORE de Ñuble opera hoy como un **sistema fragmentado**:

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           ESTADO ACTUAL: FRAGMENTACIÓN                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
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
│                                      │                                              │
│                                      ▼                                              │
│                           ┌───────────────────┐                                     │
│                           │   CONSECUENCIAS   │                                     │
│                           ├───────────────────┤                                     │
│                           │ • Mora rendiciones│                                     │
│                           │ • Subejec. presup.│                                     │
│                           │ • Proyectos atras.│                                     │
│                           │ • CGR reparos     │                                     │
│                           │ • Decisiones ciegas│                                    │
│                           └───────────────────┘                                     │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Síntomas específicos:**

| Área | Síntoma | Impacto |
|------|---------|---------|
| **IPR (Intervención Pública Regional)** | No hay visibilidad de cartera completa | Proyectos duplicados, mal priorizados |
| **Presupuesto** | Información desfasada con SIGFE | Subejec. ~15-20% anual |
| **Rendiciones** | Seguimiento manual en Excel | Mora crónica, reparos CGR |
| **Convenios** | Sin alertas de vencimiento | Caducidades, pérdida de recursos |
| **Coordinación** | Sin fuente única de verdad | Actores desalineados |
| **Planificación** | ERD sin conexión con ejecución | Estrategia desconectada |

---

### 2. Propósito de GORE_OS

**GORE_OS es la plataforma operativa integral del GORE Ñuble.**

No es un sistema de información tradicional. Es una **plataforma unificada** que opera sobre cuatro núcleos:

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         GORE_OS: PLATAFORMA INTEGRAL                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│  │ GESTIÓN RECURSOS   │ │GESTIÓN JUR-ADMIN   │ │GESTIÓN RELACIONAL  │ │GESTIÓN INVERSIÓN   │
│  ├────────────────────┤ ├────────────────────┤ ├────────────────────┤ ├────────────────────┤
│  │• Finanzas/Tesorería│ │• Actos administrat.│ │• Ejecutores        │ │• Portafolio IPR    │
│  │• Personal/Dotación │ │• Procedimientos    │ │• Proveedores       │ │• Presupuesto inv.  │
│  │• Abastecimiento    │ │• Expediente electr.│ │• Ciudadanos        │ │• Convenios (ejec.) │
│  │• Activos/Inventario│ │• Cumplimiento/CGR  │ │• Actores regionales│ │• Rendiciones       │
│  │• Flota/Serv.Grales.│ │• Convenios (acto)  │ │• Historial relac.  │ │• Riesgos y alertas │
│  └─────────┬──────────┘ └─────────┬──────────┘ └─────────┬──────────┘ └─────────┬──────────┘
│            │                      │                      │                      │          │
│            └──────────────────────┴──────────────────────┴──────────────────────┘          │
│                                           │                                           │
│                            ┌──────────────▼──────────────┐                            │
│                            │    CAPA DE INTELIGENCIA     │                            │
│                            │  • Base de conocimiento     │                            │
│                            │  • Agentes especializados   │                            │
│                            │  • Alertas predictivas      │                            │
│                            │  • Simulación escenarios    │                            │
│                            │  • Trazabilidad total       │                            │
│                            │  • Cumplimiento normativo   │                            │
│                            └─────────────────────────────┘                            │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Capacidades fundamentales:**

1. **Gestiona recursos institucionales**: Finanzas, personal, abastecimiento, activos, flota
2. **Gestiona actos y cumplimiento**: Procedimientos, expedientes, actos administrativos, cumplimiento normativo
3. **Gestiona relaciones territoriales**: Ejecutores, proveedores, ciudadanos, actores regionales
4. **Gestiona inversión pública**: Ciclo completo IPR desde oportunidad hasta impacto
5. **Integra** sistemas externos obligatorios en vista unificada
6. **Automatiza** flujos y genera alertas predictivas
7. **Amplifica** capacidad decisional de cada funcionario

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           PROPÓSITO: DE REACTIVO A PREDICTIVO                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   HOY (Sin GORE_OS)                      MAÑANA (Con GORE_OS)                       │
│   ─────────────────                      ───────────────────                        │
│                                                                                      │
│   "¿Cuántas rendiciones              →   "Tienes 12 rendiciones que                │
│    están pendientes?"                     vencen en 30 días. Te sugiero             │
│                                           priorizar estas 3 primero."              │
│                                                                                      │
│   "¿Cuánto hemos ejecutado?"         →   "Ejecutas 67.3% al día 15/12.             │
│                                           Proyección: 89%. Riesgo: Programa X."    │
│                                                                                      │
│   "¿Este proyecto ya tiene RS?"      →   "Proyecto ingresado. RS estimado:         │
│                                           45 días. Requisitos pendientes: 2."       │
│                                                                                      │
│   "¿Quién tiene que firmar esto?"    →   "Flujo iniciado. Siguiente: Jefe DIPIR.   │
│                                           Alertaré si demora >3 días."              │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Principios Rectores

| Principio | Descripción | Implicancia de Diseño |
|-----------|-------------|----------------------|
| **Fuente Única de Verdad** | Un dato, una fuente, muchos consumidores | No duplicar datos; integrar sistemas |
| **Automatización Progresiva** | Primero visibilidad, luego alertas, luego automatización | Capas incrementales de valor |
| **Humano en el Centro** | AI aumenta capacidad, no reemplaza juicio | Decisiones finales siempre humanas |
| **Cumplimiento Embebido** | TDE, CGR, normativa como reglas del sistema | Compliance by design |
| **Trazabilidad Total** | Cada acción tiene autor, fecha, razón | Auditoría automática |
| **Interoperabilidad Nativa** | APIs primero, UI después | Ecosistema abierto |
| **Conocimiento Estructurado** | Normativa, procesos y reglas como base de conocimiento | Agentes consultan KB antes de actuar |
| **Agentes Especializados** | Cada dominio tiene agentes que asisten a funcionarios | Delegación de tareas repetitivas |

---

## Parte II: Arquitectura Funcional

### 4. Modelo de Funciones GORE: Motor + Soporte

El GORE opera mediante un ciclo integrado de funciones organizadas en tres dimensiones:

```
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
│   ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐          │
│   │   2. FINANCIAR    │     │    3. EJECUTAR    │     │   4. COORDINAR    │          │
│   │   (D-FIN)         │◀───▶│    (D-EJEC)       │◀───▶│   (D-COORD)       │          │
│   │   IPR, Presupuesto│     │   Convenios, Obras│     │   Actores, Mesas  │          │
│   └─────────┬─────────┘     └─────────┬─────────┘     └─────────┬─────────┘          │
│             │                         │                         │                    │
│   ══════════╪═════════════════════════╪═════════════════════════╪══════════════════  │
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

> **Nota:** Las funciones habilitantes (NORMAR, ADMINISTRAR) no son menos importantes; son la base que permite que el motor de desarrollo (FINANCIAR, EJECUTAR, COORDINAR) funcione con certeza jurídica y recursos adecuados.

---

### 5. Dominios GORE_OS (Detalle Completo)

#### 5.1 Dominio: PLANIFICACIÓN ESTRATÉGICA (D-PLAN)

**Propósito:** Gestionar los instrumentos de planificación regional y su conexión con la ejecución.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              D-PLAN: PLANIFICACIÓN                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                        MÓDULO: ERD DIGITAL                                  │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   ESTRUCTURA ERD                                                            │   │
│   │   ═══════════════════════════════════════════════                          │   │
│   │   ERD 2024-2034                                                            │   │
│   │   └── Visión Regional                                                       │   │
│   │       └── Eje Estratégico (4-6)                                            │   │
│   │           └── Lineamiento (2-4 por eje)                                    │   │
│   │               └── Objetivo Estratégico (1-3 por lineamiento)               │   │
│   │                   └── Indicador + Meta (1-n por objetivo)                  │   │
│   │                       └── Iniciativa vinculada (IPR, Programa)             │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Árbol navegable de ERD                                                  │   │
│   │   • Vinculación IPR → Objetivo ERD (obligatorio)                           │   │
│   │   • Dashboard de avance por eje/lineamiento                                │   │
│   │   • Alertas de objetivos sin iniciativas                                   │   │
│   │   • Reportes de coherencia ERD-Presupuesto                                 │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                        MÓDULO: PROT DIGITAL                                 │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   ESTRUCTURA PROT                                                           │   │
│   │   ═══════════════════════════════════════════════                          │   │
│   │   Plan Regional de Ordenamiento Territorial                                │   │
│   │   └── Macrozona (3-5)                                                       │   │
│   │       └── Zona (n por macrozona)                                           │   │
│   │           └── Uso permitido / condicionado / prohibido                     │   │
│   │               └── Condicionantes técnicas                                  │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Visor geoespacial de zonificación PROT                                 │   │
│   │   • Validador de compatibilidad IPR ↔ Zona                                 │   │
│   │   • Alertas de proyectos en zonas incompatibles                            │   │
│   │   • Consulta pública de aptitud territorial                                │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                     MÓDULO: ARI / PROPIR DIGITAL                            │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   ANTEPROYECTO REGIONAL DE INVERSIONES                                     │   │
│   │   ═══════════════════════════════════════════════                          │   │
│   │                                                                             │   │
│   │   CICLO ARI (anual, mayo-agosto)                                           │   │
│   │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐                │   │
│   │   │Solicitud│───▶│Prioriz. │───▶│Consolidar───▶│Presentar│                │   │
│   │   │Divisiones    │Técnica  │    │DIPIR    │    │CORE     │                │   │
│   │   └─────────┘    └─────────┘    └─────────┘    └─────────┘                │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Formulario de solicitud de iniciativas                                 │   │
│   │   • Scoring de priorización (multi-criterio)                               │   │
│   │   • Consolidación automática por fuente/fondo                              │   │
│   │   • Simulación de escenarios presupuestarios                               │   │
│   │   • Exportación formato DIPRES                                             │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                   MÓDULO: INTELIGENCIA TERRITORIAL                          │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   → Ver D-TERR: Observatorio Regional (indicadores, dashboards, alertas)   │   │
│   │   → Ver D-TERR: Visor Geoespacial (capas temáticas, zonificación PROT)     │   │
│   │                                                                             │   │
│   │   INTEGRACIÓN CON PLANIFICACIÓN                                            │   │
│   │   ═══════════════════════════════════════════════                          │   │
│   │   • Vinculación indicadores territoriales ↔ objetivos ERD                  │   │
│   │   • Validación automática IPR ↔ zonificación PROT                          │   │
│   │   • Alertas de brechas territoriales por eje estratégico                   │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Entidades de datos D-PLAN:**

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `ERD` | id, nombre, periodo_inicio, periodo_fin, estado | → EjeEstrategico[] |
| `EjeEstrategico` | id, erd_id, codigo, nombre, descripcion | → Lineamiento[] |
| `Lineamiento` | id, eje_id, codigo, nombre | → ObjetivoEstrategico[] |
| `ObjetivoEstrategico` | id, lineamiento_id, codigo, nombre, descripcion | → Indicador[], IPR[] |
| `IndicadorERD` | id, objetivo_id, nombre, formula, linea_base, meta, año_meta | → MedicionIndicador[] |
| `ARI` | id, año, estado, fecha_presentacion | → LineaARI[] |
| `LineaARI` | id, ari_id, ipr_id, prioridad, monto_solicitado, monto_asignado | → IPR |

**Nota:** La entidad `ZonaPROT` se define en D-TERR como parte de la Infraestructura de Datos Espaciales.

---

#### 5.2 Dominio: FINANCIAMIENTO (D-FIN)

**Propósito:** Gestión integral 360° del ciclo de vida de las inversiones públicas regionales, integrando cuatro perspectivas: **(1) Captación de Oportunidades** para identificar y priorizar necesidades de desarrollo, **(2) Gestión de Capital** para maximizar el retorno en desarrollo regional, **(3) Gestión de Ejecutores** para administrar relaciones y capacidades institucionales, y **(4) Evaluación Continua** (ex ante, ex durante, ex post) para asegurar calidad y resultados.

> **Visión:** El GORE opera como gestor integral del desarrollo regional: capta oportunidades de intervención, administra capital público (presupuesto de Hacienda) para generar retorno en desarrollo, cultiva relaciones con ejecutores, y evalúa continuamente resultados e impacto.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                D-FIN: GESTIÓN INTEGRAL DE INVERSIONES REGIONALES                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ╔═══════════════════════════════════════════════════════════════════════════════╗  │
│  ║                    MODELO DE GESTIÓN 360° IPR                                 ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                               ║  │
│  ║  CICLO COMPLETO: DESDE LA OPORTUNIDAD HASTA EL IMPACTO (10 FASES)            ║  │
│  ║  ┌─────┐ ┌────┐ ┌─────┐ ┌────┐ ┌─────┐ ┌─────┐ ┌────┐ ┌─────┐ ┌──────┐      ║  │
│  ║  │OPOR.│▶│IDEA│▶│FORM.│▶│EVAL│▶│ASIG.│▶│EJEC.│▶│REND│▶│CIERR│▶│IMPACT│      ║  │
│  ║  └──┬──┘ └──┬─┘ └──┬──┘ └──┬─┘ └──┬──┘ └──┬──┘ └──┬─┘ └──┬──┘ └──┬───┘      ║  │
│  ║     │       │      │       │      │       │       │      │       │           ║  │
│  ║  ┌──┴───────┴──┐ ┌─┴───────┴──┐ ┌─┴───────┴───┐ ┌─┴──────┴───────┴──┐       ║  │
│  ║  │  CAPTACIÓN  │ │  EX ANTE   │ │ EX DURANTE  │ │     EX POST       │       ║  │
│  ║  │ • Fuentes   │ │ • Pertinen.│ │ • Avance    │ │ • Productos       │       ║  │
│  ║  │ • Calificac.│ │ • Viabilid.│ │ • Hitos     │ │ • Outcomes        │       ║  │
│  ║  │ • Prioriz.  │ │ • Rating   │ │ • Alertas   │ │ • Impacto IDR     │       ║  │
│  ║  │ • Conversión│ │ • Riesgo   │ │ • Covenants │ │ • Rating update   │       ║  │
│  ║  └─────────────┘ └────────────┘ └─────────────┘ └───────────────────┘       ║  │
│  ║                                                                               ║  │
│  ║  CUATRO PERSPECTIVAS INTEGRADAS                                              ║  │
│  ║  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐     ║  │
│  ║  │CAPTACIÓN OPOR.│ │GESTIÓN CAPITAL│ │GESTIÓN EJECUT.│ │CICLO VIDA IPR │     ║  │
│  ║  │ • Demanda     │ │ • Capital base│ │ • Ficha 360°  │ │ • 10 fases    │     ║  │
│  ║  │ • Embudo      │ │ • Asignación  │ │ • Rating      │ │ • Estados     │     ║  │
│  ║  │ • Calificac.  │ │ • Portfolio   │ │ • Historial   │ │ • Hitos       │     ║  │
│  ║  │ • Nurturing   │ │ • IPR problem.│ │ • Capacidades │ │ • Documentos  │     ║  │
│  ║  │ • Conversión  │ │ • Retorno IDR │ │ • Alertas mora│ │ • Trazabilidad│     ║  │
│  ║  └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘     ║  │
│  ║                                                                               ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                MÓDULO: CAPTACIÓN DE OPORTUNIDADES                           │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   FUENTES DE CAPTACIÓN DE NECESIDADES DE DESARROLLO                        │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │   ┌─────────────────┬───────────────────────────────────────────────────┐  │   │
│   │   │ FUENTE          │ DESCRIPCIÓN                                       │  │   │
│   │   ├─────────────────┼───────────────────────────────────────────────────┤  │   │
│   │   │ ERD/Brechas     │ Brechas identificadas en Estrategia Regional      │  │   │
│   │   │ Diagnósticos    │ Estudios territoriales, sectoriales, comunales    │  │   │
│   │   │ Demanda ciudadan│ OIRS, cabildos, consultas públicas, cuentas públ. │  │   │
│   │   │ Compromisos     │ Compromisos de Gobernador, CORE, autoridades      │  │   │
│   │   │ Ejecutores      │ Propuestas de municipios, servicios, universidades│  │   │
│   │   │ Fondos disponib.│ Convocatorias sectoriales, cofinanciamientos      │  │   │
│   │   │ Emergencias     │ Situaciones de emergencia declarada (catástrofes) │  │   │
│   │   └─────────────────┴───────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   EMBUDO DE OPORTUNIDADES                                                  │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │                                                                             │   │
│   │   ┌─────────────────────────────────────────────────────────────────────┐  │   │
│   │   │         DETECTADA (100%)                                            │  │   │
│   │   │              ▼                                                      │  │   │
│   │   │      ┌──────────────┐                                               │  │   │
│   │   │      │  CALIFICADA  │ (Filtro: alineación ERD, viabilidad básica)   │  │   │
│   │   │      │     (60%)    │                                               │  │   │
│   │   │      └──────┬───────┘                                               │  │   │
│   │   │             ▼                                                       │  │   │
│   │   │      ┌──────────────┐                                               │  │   │
│   │   │      │  PRIORIZADA  │ (Filtro: urgencia, impacto, capacidad $)      │  │   │
│   │   │      │     (35%)    │                                               │  │   │
│   │   │      └──────┬───────┘                                               │  │   │
│   │   │             ▼                                                       │  │   │
│   │   │      ┌──────────────┐                                               │  │   │
│   │   │      │ EN NURTURING │ (Maduración: estudios, articulación)          │  │   │
│   │   │      │     (20%)    │                                               │  │   │
│   │   │      └──────┬───────┘                                               │  │   │
│   │   │             ▼                                                       │  │   │
│   │   │      ┌──────────────┐                                               │  │   │
│   │   │      │ CONVERTIDA   │ → IPR formal con código BIP                   │  │   │
│   │   │      │     (15%)    │                                               │  │   │
│   │   │      └──────────────┘                                               │  │   │
│   │   └─────────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   CALIFICACIÓN RÁPIDA DE OPORTUNIDADES                                     │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   ┌─────────────────┬───────────────────────────────────────────────────┐  │   │
│   │   │ CRITERIO        │ EVALUACIÓN                                        │  │   │
│   │   ├─────────────────┼───────────────────────────────────────────────────┤  │   │
│   │   │ Alineación ERD  │ ¿Contribuye a objetivos estratégicos regionales?  │  │   │
│   │   │ Viabilidad téc. │ ¿Es técnicamente factible? ¿Existe solución?      │  │   │
│   │   │ Ejecutor potenc.│ ¿Hay actor con capacidad de ejecución?            │  │   │
│   │   │ Disponibilidad $│ ¿Existe o existirá espacio presupuestario?        │  │   │
│   │   │ Urgencia        │ ¿Hay ventana de oportunidad o emergencia?         │  │   │
│   │   │ Impacto esperado│ ¿Beneficiarios, territorio, magnitud?             │  │   │
│   │   └─────────────────┴───────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   NURTURING DE OPORTUNIDADES                                               │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   Actividades para madurar oportunidades prometedoras:                     │   │
│   │   • Elaboración de estudios básicos o prefactibilidad                     │   │
│   │   • Articulación con ejecutores potenciales                               │   │
│   │   • Búsqueda de cofinanciamiento sectorial                                │   │
│   │   • Priorización en ARI para año siguiente                                │   │
│   │   • Gestión de compromisos de autoridades                                 │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Registro de oportunidades desde múltiples fuentes                     │   │
│   │   • Dashboard de embudo con métricas de conversión                        │   │
│   │   • Calificación asistida (checklist de criterios)                        │   │
│   │   • Alertas de oportunidades en ventana de tiempo                         │   │
│   │   • Vinculación automática con brechas ERD                                │   │
│   │   • Trazabilidad: de oportunidad a IPR ejecutada                          │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      MÓDULO: CAPITAL BASE                                   │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   FUENTES DE CAPITAL REGIONAL (Presupuesto anual de Hacienda)              │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │   ┌────────────┬──────────────────────────────────────────────────────┐    │   │
│   │   │ FUENTE     │ DESCRIPCIÓN                                          │    │   │
│   │   ├────────────┼──────────────────────────────────────────────────────┤    │   │
│   │   │ FNDR       │ Fondo Nacional Desarrollo Regional (principal)       │    │   │
│   │   │ FRPD       │ Fondo Regional Productividad y Desarrollo (Royalty)  │    │   │
│   │   │ Sectoriales│ Transferencias de ministerios (consolidables)        │    │   │
│   │   │ Propios    │ Ingresos propios, patentes, multas                   │    │   │
│   │   │ SIC        │ Saldo Inicial de Caja (arrastre)                     │    │   │
│   │   └────────────┴──────────────────────────────────────────────────────┘    │   │
│   │                                                                             │   │
│   │   CICLO PRESUPUESTARIO                                                     │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   │ MAY-JUN │ JUL-SEP │ OCT-NOV │ DIC     │ ENE-DIC (n+1)  │              │   │
│   │   │ ARI     │ Ley Ppto│ Congreso│ CORE    │ Ejecución      │              │   │
│   │   │ (marco) │ (DIPRES)│ (debate)│ aprueba │ + Modificac.   │              │   │
│   │   │─────────────────────────────────────────────────────────│              │   │
│   │   │         ESPACIO PRESUPUESTARIO = Capital - Arrastres   │              │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      MÓDULO: PORTAFOLIO IPR                                 │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   TAXONOMÍA IPR (Intervención Pública Regional)                            │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   IPR (Término paraguas)                                                    │   │
│   │   ├── IDI (Iniciativa de Inversión)                                         │   │
│   │   │   └── Gasto de capital: obras, activos (S.31, S.33)                     │   │
│   │   │       • Requiere RS/AD de MDSF (según monto/tipo)                       │   │
│   │   │       • Registro obligatorio en BIP                                     │   │
│   │   │                                                                         │   │
│   │   └── PPR (Programa Público Regional)                                       │   │
│   │       └── Gasto corriente/mixto: servicios, subvenciones (S.24)             │   │
│   │           • Requiere RF de DIPRES/SES (Glosa 06)                            │   │
│   │           • Metodología Marco Lógico                                        │   │
│   │                                                                             │   │
│   │   ROLES DE ACTORES EN EL ECOSISTEMA IPR (VISIÓN 360°)                     │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   Un mismo Actor puede asumir DIFERENTES ROLES en una IPR según la fase   │   │
│   │   del ciclo de vida. La relación Actor ↔ IPR es N:M con rol por fase.     │   │
│   │                                                                             │   │
│   │   CATÁLOGO DE ROLES                                                        │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   • POSTULANTE: Presenta la IPR formalmente al GORE                        │   │
│   │   • FORMULADOR: Elabora técnicamente la iniciativa (estudios, diseño)      │   │
│   │   • PATROCINADOR: Respalda la postulación ante el GORE                     │   │
│   │   • EVALUADOR: Realiza evaluación técnica o económica                      │   │
│   │   • APROBADOR: Toma decisión de financiamiento (CORE, Gobernador)          │   │
│   │   • UNIDAD_FINANCIERA: Transfiere recursos (generalmente GORE)             │   │
│   │   • UNIDAD_TECNICA: Licita, ejecuta, supervisa obra                        │   │
│   │   • ENTIDAD_EJECUTORA: Recibe fondos y rinde cuentas                       │   │
│   │   • CONTRAPARTE: Coordina desde el GORE con ejecutor                       │   │
│   │   • BENEFICIARIO: Población objetivo de la intervención                    │   │
│   │                                                                             │   │
│   │   MATRIZ ROL × FASE DEL CICLO DE VIDA                                      │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   │ Fase          │ Roles Activos                                │         │   │
│   │   │───────────────│──────────────────────────────────────────────│         │   │
│   │   │ IDEA          │ Postulante, Formulador                       │         │   │
│   │   │ PREFACTIBIL.  │ Formulador, Patrocinador                     │         │   │
│   │   │ DISEÑO        │ Formulador, Evaluador                        │         │   │
│   │   │ APROBACIÓN    │ Patrocinador, Evaluador, Aprobador           │         │   │
│   │   │ FINANCIAM.    │ Unidad_Financiera, Aprobador                 │         │   │
│   │   │ EJECUCIÓN     │ Unidad_Tecnica, Entidad_Ejecutora, Contrap.  │         │   │
│   │   │ RENDICIÓN     │ Entidad_Ejecutora, Contraparte               │         │   │
│   │   │ CIERRE        │ Contraparte, Evaluador (ex-post)             │         │   │
│   │   │ OPERACIÓN     │ Beneficiario, Entidad_Ejecutora (O&M)        │         │   │
│   │                                                                             │   │
│   │   EJEMPLOS DE CONFIGURACIÓN POR MECANISMO                                 │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   • FRIL: Municipio = Postulante + Formulador + Unidad_Tecnica +           │   │
│   │           Entidad_Ejecutora; GORE = Unidad_Financiera                      │   │
│   │   • PPR Transfer: Servicio Público = Postulante + Entidad_Ejecutora;       │   │
│   │                   GORE = Unidad_Financiera + Contraparte                   │   │
│   │   • Subvención 8%: ONG = Postulante + Entidad_Ejecutora;                   │   │
│   │                    GORE = Unidad_Financiera; Municipio = Patrocinador      │   │
│   │   • IDI SNI: GORE = Postulante + Formulador + Unidad_Financiera;           │   │
│   │              Empresa = Unidad_Tecnica; MDSF = Evaluador                    │   │
│   │                                                                             │   │
│   │   CICLO DE VIDA DE UNA INICIATIVA (IPR) - 9 FASES                         │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   ┌──────┐ ┌───────┐ ┌──────┐ ┌───────┐ ┌───────┐ ┌──────┐ ┌─────┐ ┌─────┐│   │
│   │   │ IDEA │▶│PREFACT│▶│DISEÑO│▶│APROB. │▶│FINANC.│▶│EJECUC│▶│REND.│▶│CIERR││   │
│   │   └──┬───┘ └───┬───┘ └──┬───┘ └───┬───┘ └───┬───┘ └──┬───┘ └──┬──┘ └──┬──┘│   │
│   │      │         │        │         │         │        │        │        │   │   │
│   │      ▼         ▼        ▼         ▼         ▼        ▼        ▼        ▼   │   │
│   │   Ficha    Estudio   Perfil/   CORE      CDP      Convenio  SISREC  Acta   │   │
│   │   idea     básico    RS       aprueba   emitido  vigente   OK      cierre │   │
│   │                                                                             │   │
│   │   → OPERACIÓN: Fase post-cierre para activos que requieren O&M             │   │
│   │                                                                             │   │
│   │   ESTADOS DE UNA IPR                                                       │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   • EN_CARTERA: Registrada, sin financiamiento                             │   │
│   │   • EN_EVALUACION: En proceso RS (MDSF)                                    │   │
│   │   • APROBADA_RS: Tiene RS, sin presupuesto                                 │   │
│   │   • PRIORIZADA_ARI: Incluida en ARI                                        │   │
│   │   • EN_PRESUPUESTO: Con recursos asignados Ley Presupuesto                 │   │
│   │   • EN_LICITACION: Proceso de contratación                                 │   │
│   │   • EN_EJECUCION: Contrato/convenio vigente                                │   │
│   │   • TERMINADA: Ejecución física 100%                                       │   │
│   │   • CERRADA: Liquidada, rendida, archivada                                 │   │
│   │   • SUSPENDIDA: Detenida temporalmente                                     │   │
│   │   • CANCELADA: Terminada sin completar                                     │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Vista Kanban de cartera por estado                                     │   │
│   │   • Filtros: división, comuna, mecanismo, estado, año                      │   │
│   │   • Ficha completa de cada IPR                                             │   │
│   │   • Timeline de hitos y cambios de estado                                  │   │
│   │   • Alertas de IPR estancadas                                              │   │
│   │   • Exportación a BIP/SNI                                                  │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                   MÓDULO: SELECTOR DE MECANISMOS                           │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   ÁRBOL DE DECISIÓN: ¿QUÉ MECANISMO DE FINANCIAMIENTO USAR?               │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   ┌─────────────────────────────────────────────────────────────────────┐  │   │
│   │   │ ¿Es inversión de capital?                                           │  │   │
│   │   ├─────────────────────────────────────────────────────────────────────┤  │   │
│   │   │ SÍ ─────────────────────────────────────────────────────────────────│  │   │
│   │   │    │                                                                │  │   │
│   │   │    ├── ¿Monto > 7.000 UTM? ──┬── SÍ → IDI (BIP, RS, CORE)          │  │   │
│   │   │    │                         └── NO → IRAL (solo GORE)              │  │   │
│   │   │    │                                                                │  │   │
│   │   │    ├── ¿Es infraestructura menor municipal? → FRIL (≤4.545 UTM Ñuble)│  │   │
│   │   │    │                                                                │  │   │
│   │   │    ├── ¿Es conservación de activo? → Circular 33 (AD)              │  │   │
│   │   │    │                                                                │  │   │
│   │   │    └── ¿Es I+D+i o productividad? → FRPD (Royalty)                 │  │   │
│   │   │                                                                     │  │   │
│   │   │ NO (PPR - Programa Público Regional) ──────────────────────────────│  │   │
│   │   │    │                                                                │  │   │
│   │   │    ├── ¿Ejecución directa GORE? → PPR Glosa 06 (RF DIPRES/SES)    │  │   │
│   │   │    │                                                                │  │   │
│   │   │    ├── ¿Transferencia a entidad pública? → PPR Transfer (exento RF)│  │   │
│   │   │    │                                                                │  │   │
│   │   │    └── ¿Actividad acotada sin fines de lucro? → Subvención 8%     │  │   │
│   │   └─────────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   CATÁLOGO DE MECANISMOS DE FINANCIAMIENTO                                 │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │                                                                             │   │
│   │   IDI (Iniciativas de Inversión - S.31/S.33)                              │   │
│   │   ┌────────┬─────────────────────┬──────────┬──────────┬──────────────┐   │   │
│   │   │ Código │ Nombre              │ Tope UTM │ Eval.    │ Ejecutor     │   │   │
│   │   ├────────┼─────────────────────┼──────────┼──────────┼──────────────┤   │   │
│   │   │ SNI    │ IDI General         │ Sin tope │ RS MDSF  │ Público      │   │   │
│   │   │ FRIL   │ Fondo Reg.Inf.Local │ 4.545    │ GORE     │ Municipios   │   │   │
│   │   │ FRPD   │ Royalty (I+D+i)     │ Variable │ Bifurc.  │ Habilitados  │   │   │
│   │   │ C33    │ Circular 33         │ Regla30% │ GORE     │ Público      │   │   │
│   │   │ IRAL   │ Inv.Reg.Asig.Local  │ 7.000    │ GORE     │ GORE         │   │   │
│   │   └────────┴─────────────────────┴──────────┴──────────┴──────────────┘   │   │
│   │                                                                             │   │
│   │   PPR (Programas Públicos Regionales - S.24)                              │   │
│   │   ┌────────┬─────────────────────┬──────────┬──────────┬──────────────┐   │   │
│   │   │ Código │ Nombre              │ Tope     │ Eval.    │ Ejecutor     │   │   │
│   │   ├────────┼─────────────────────┼──────────┼──────────┼──────────────┤   │   │
│   │   │ G06    │ PPR Glosa 06        │ Variable │ RF DIPRES│ GORE directo │   │   │
│   │   │ PPRT   │ PPR Transferencia   │ Variable │ GORE     │ Entidad púb. │   │   │
│   │   │ S8%    │ Subvención 8%       │ 8% inv.  │ GORE     │ ONG/OSC/Muni │   │   │
│   │   └────────┴─────────────────────┴──────────┴──────────┴──────────────┘   │   │
│   │                                                                             │   │
│   │   METODOLOGÍAS DE EVALUACIÓN POR MECANISMO                                │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   • IDI SNI: Evaluación Social (VAN, TIR, VAC, CAE) + BIP + RIS           │   │
│   │   • FRIL: Checklist admisibilidad + Evaluación técnica GORE               │   │
│   │   • FRPD: Comisión Regional (11 miembros) - Puntaje ≥5                    │   │
│   │   • C33: Análisis CAE + Regla 30% (conservación ≤30% → sin RS)           │   │
│   │   • PPR G06: Marco Lógico (MML) + Indicadores SMART                       │   │
│   │   • PPR Transfer: MML + ITF (Informe Técnico Favorable GORE)              │   │
│   │   • S8%: Evaluación técnica GORE por fondo temático                       │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Wizard de selección de mecanismo según naturaleza IPR                  │   │
│   │   • Validación automática de elegibilidad por mecanismo                   │   │
│   │   • Sugerencia de mecanismo óptimo según perfil iniciativa                │   │
│   │   • Comparativa de requisitos entre mecanismos                             │   │
│   │   • Generación automática de checklist documental por mecanismo           │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      MÓDULO: PRESUPUESTO REGIONAL                           │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   CICLO PRESUPUESTARIO                                                     │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   ┌──────────────────────────────────────────────────────────────────────┐ │   │
│   │   │ ENE-MAR │ ABR-JUN │ JUL-SEP │ OCT-DIC │ ENE-DIC (n+1)              │ │   │
│   │   ├─────────┼─────────┼─────────┼─────────┼────────────────────────────┤ │   │
│   │   │Ejecución│ARI      │Ley Ppto │Aprobac. │Ejecución año n+1           │ │   │
│   │   │año n    │(mayo)   │(agosto) │CORE     │                            │ │   │
│   │   │         │         │         │(dic)    │                            │ │   │
│   │   └──────────────────────────────────────────────────────────────────────┘ │   │
│   │                                                                             │   │
│   │   ESTRUCTURA PRESUPUESTARIA                                                │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   Partida 31 (Gobiernos Regionales)                                        │   │
│   │   └── Capítulo 01 (GORE Ñuble)                                             │   │
│   │       └── Programa (01: Gobierno Regional, 02: Inversión Regional)         │   │
│   │           └── Subtítulo (21: Personal, 22: Bienes, 29: Adquisición, etc.)  │   │
│   │               └── Ítem                                                      │   │
│   │                   └── Asignación                                           │   │
│   │                       └── Glosa (detalle textual)                          │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Árbol presupuestario navegable                                         │   │
│   │   • Ejecución en tiempo real (sync SIGFE)                                  │   │
│   │   • Proyección de ejecución al 31/12                                       │   │
│   │   • Alertas de subejecución por programa                                   │   │
│   │   • Gestión de modificaciones presupuestarias                              │   │
│   │   • Comparativa interanual                                                 │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                        MÓDULO: RENDICIONES                                  │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   CICLO DE RENDICIÓN                                                       │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   Transferencia         Rendición              Revisión            Cierre   │   │
│   │   ┌─────────┐          ┌─────────┐            ┌─────────┐        ┌────────┐│   │
│   │   │ Giro    │─────────▶│Ejecutor │───────────▶│ RTF     │───────▶│Aprobada││   │
│   │   │ recursos│          │ rinde   │            │ revisa  │        │        ││   │
│   │   └─────────┘          └─────────┘            └─────────┘        └────────┘│   │
│   │        │                    │                      │                  │    │   │
│   │        ▼                    ▼                      ▼                  ▼    │   │
│   │   Plazo 60 días       Documentos            Observaciones       Sin mora   │   │
│   │   para rendir         respaldatorios        o reparos                      │   │
│   │                                                                             │   │
│   │   ESTADOS DE RENDICIÓN                                                     │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   • PENDIENTE: Girado, plazo no vencido                                    │   │
│   │   • EN_MORA: Plazo vencido, no rendido                                     │   │
│   │   • EN_REVISION: Documentos ingresados, RTF revisando                      │   │
│   │   • OBSERVADA: RTF requiere subsanar                                       │   │
│   │   • APROBADA: Rendición conforme                                           │   │
│   │   • RECHAZADA: Rendición no conforme, reintegro                            │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Dashboard de rendiciones por estado                                    │   │
│   │   • Alertas de vencimiento (30, 15, 7 días)                                │   │
│   │   • Semáforo de mora por ejecutor                                          │   │
│   │   • Trazabilidad de observaciones y subsanaciones                          │   │
│   │   • Integración SISREC (envío electrónico CGR)                             │   │
│   │   • Reportes de mora para CORE                                             │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                   MÓDULO: GESTIÓN DE EJECUTORES                             │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   FICHA 360° DEL EJECUTOR                                                  │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   ┌─────────────────────────────────────────────────────────────────────┐  │   │
│   │   │ RATING DE EJECUTOR (índice de confiabilidad institucional)         │  │   │
│   │   ├─────────────────────────────────────────────────────────────────────┤  │   │
│   │   │ Dimensión               │ Peso │ Indicadores                        │  │   │
│   │   │─────────────────────────│──────│────────────────────────────────────│  │   │
│   │   │ Historial rendiciones   │ 40%  │ % a tiempo, días mora promedio     │  │   │
│   │   │ Capacidad técnica       │ 25%  │ Equipo, metodologías, experiencia  │  │   │
│   │   │ Ejecución proyectos     │ 25%  │ % avance vs plan, sobrecostos      │  │   │
│   │   │ Gobernanza              │ 10%  │ Transparencia, controles, auditoría│  │   │
│   │   └─────────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   NIVELES DE RATING                                                        │   │
│   │   • A (≥85): Ejecutor confiable - Asignación preferente                   │   │
│   │   • B (70-84): Ejecutor estándar - Monitoreo normal                       │   │
│   │   • C (55-69): Ejecutor en observación - Supervisión reforzada            │   │
│   │   • D (<55): Ejecutor crítico - Restricción nuevas asignaciones           │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Ficha completa por ejecutor (municipio, servicio, ONG, universidad)   │   │
│   │   • Historial de IPR ejecutadas con resultados                            │   │
│   │   • Mapa de capacidades institucionales                                   │   │
│   │   • Alertas de degradación de rating                                      │   │
│   │   • Evaluación previa para nuevas asignaciones                            │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                   MÓDULO: EVALUACIÓN CONTINUA                               │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   EVALUACIÓN EN TRES TIEMPOS                                               │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   EX ANTE (Pre-asignación)                                                 │   │
│   │   ┌─────────────────────────────────────────────────────────────────────┐  │   │
│   │   │ • Pertinencia estratégica (alineación ERD)                         │  │   │
│   │   │ • Viabilidad técnica (RS de MDSF / RF de DIPRES)                   │  │   │
│   │   │ • Rating del ejecutor propuesto                                     │  │   │
│   │   │ • Análisis de riesgo de ejecución                                  │  │   │
│   │   │ DECISIÓN: Aprobar / Rechazar / Condicionar                         │  │   │
│   │   └─────────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   EX DURANTE (Ejecución)                                                   │   │
│   │   ┌─────────────────────────────────────────────────────────────────────┐  │   │
│   │   │ • Avance físico vs programado (BIP)                                │  │   │
│   │   │ • Avance financiero vs programado (SIGFE)                          │  │   │
│   │   │ • Cumplimiento de hitos y covenants del convenio                   │  │   │
│   │   │ • Alertas tempranas de desvío                                      │  │   │
│   │   │ DECISIÓN: Continuar / Ajustar / Escalar                            │  │   │
│   │   └─────────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   EX POST (Cierre)                                                         │   │
│   │   ┌─────────────────────────────────────────────────────────────────────┐  │   │
│   │   │ • Productos entregados vs comprometidos                            │  │   │
│   │   │ • Outcomes alcanzados (indicadores de resultado)                   │  │   │
│   │   │ • Impacto en desarrollo regional (IDR)                             │  │   │
│   │   │ • Actualización del rating del ejecutor                            │  │   │
│   │   │ • Lecciones aprendidas                                             │  │   │
│   │   │ DECISIÓN: Cerrar / Evaluar impacto diferido                        │  │   │
│   │   └─────────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                   MÓDULO: IPR PROBLEMÁTICAS                                 │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   GESTIÓN DE INVERSIONES CON DIFICULTADES                                  │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   CLASIFICACIÓN DE IPR PROBLEMÁTICAS                                       │   │
│   │   ┌─────────────────┬───────────────────────────────────────────────────┐  │   │
│   │   │ CATEGORÍA       │ CRITERIO                                          │  │   │
│   │   ├─────────────────┼───────────────────────────────────────────────────┤  │   │
│   │   │ ESTANCADA       │ Sin avance >90 días, sin causa justificada        │  │   │
│   │   │ EN MORA         │ Rendiciones vencidas >30 días                     │  │   │
│   │   │ SOBRECOSTO      │ Incremento >10% sobre RS sin autorización         │  │   │
│   │   │ ATRASO CRÍTICO  │ Avance físico <50% del programado                 │  │   │
│   │   │ RIESGO LEGAL    │ Controversias, incumplimientos contractuales      │  │   │
│   │   └─────────────────┴───────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   PROTOCOLO DE ESCALAMIENTO                                                │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   1. Alerta automática → RTF (Referente Técnico-Financiero)               │   │
│   │   2. Gestión operativa → Jefatura División (15 días)                       │   │
│   │   3. Escalamiento → Administrador Regional (30 días)                       │   │
│   │   4. Decisión ejecutiva → Gobernador (60 días)                             │   │
│   │   5. Informe a CORE (obligatorio si >90 días o monto >1.000 UTM)          │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Dashboard de IPR problemáticas por categoría                          │   │
│   │   • Trazabilidad de acciones correctivas                                  │   │
│   │   • Simulación de impacto en ejecución presupuestaria                     │   │
│   │   • Reportes automáticos a CORE                                           │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                   MÓDULO: RETORNO EN DESARROLLO (IDR)                       │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   ÍNDICE DE DESARROLLO REGIONAL (IDR)                                      │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │   Mide el "retorno" de la inversión pública en términos de desarrollo     │   │
│   │                                                                             │   │
│   │   DIMENSIONES DEL IDR                                                      │   │
│   │   ┌─────────────────┬───────────────────────────────────────────────────┐  │   │
│   │   │ DIMENSIÓN       │ INDICADORES                                       │  │   │
│   │   ├─────────────────┼───────────────────────────────────────────────────┤  │   │
│   │   │ Económico       │ Empleo generado, PIB regional, productividad      │  │   │
│   │   │ Social          │ Pobreza, acceso servicios, calidad de vida        │  │   │
│   │   │ Territorial     │ Conectividad, equidad comunal, infraestructura    │  │   │
│   │   │ Institucional   │ Capacidades locales, gobernanza, participación    │  │   │
│   │   └─────────────────┴───────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Cálculo de IDR por IPR ejecutada (ex post)                            │   │
│   │   • Agregación por territorio, sector, mecanismo                          │   │
│   │   • Proyección de impacto para IPR en cartera                             │   │
│   │   • Benchmark con otras regiones                                          │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Categorías por Mecanismo:**

| Mecanismo | Categorías/Fondos |
|-----------|-------------------|
| **FRIL** | A-Desarrollo Territorial (A1-Integración Rural, A2-Agua, A3-Vial), B-Servicios (B1-Edificación, B2-Gestión Riesgos, B3-Seguridad), C-Desarrollo Social (C1-Inclusión, C2-Género, C3-Turismo), D-Medio Ambiente (D1-Deportes, D2-Áreas Verdes, D3-Sustentabilidad) |
| **Circular 33** | Estudios propios del giro, ANF (Activos No Financieros - 20% cofinanciamiento), Conservación de caminos (MANVU SIMP), Conservación de infraestructura (regla 30%), Emergencias (post-catástrofe) |
| **Subvención 8%** | Cultura, Social e Inclusión, Equidad de Género, Deporte, Personas Mayores, Medio Ambiente, Seguridad Ciudadana |
| **FRPD** | I+D+i, Innovación (base tecnológica, productiva, social, pública), Emprendimiento, Difusión/Transferencia tecnológica |

**Reglas Especiales por Mecanismo:**

- **FRIL**: Mínimo $100M, máximo 4.545 UTM (tope regional Ñuble; normativo 5.000 UTM); categorías A2/A3 no cuentan en límite de 5 proyectos/comuna
- **Circular 33**: Conservación ≤30% costo reposición → sin RS MDSF; ANF requiere 20% aporte propio
- **FRPD**: Bifurcación post-selección: CTCI puro (exento RF) vs Fomento (requiere RF); máx 30% en remuneraciones
- **Subvención 8%**: Plazo ejecución 8 meses; 10% puede ser asignación directa excepcional (CORE)
- **PPR Transfer**: Exento evaluación DIPRES/SES; rendición vía SISREC; máx 5% gastos personal

**Entidades de datos D-FIN:**

*Captación de Oportunidades:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Oportunidad` | id, titulo, descripcion, fuente (ERD/DIAGNOSTICO/DEMANDA/COMPROMISO/EJECUTOR/FONDO/EMERGENCIA), estado_embudo (DETECTADA/CALIFICADA/PRIORIZADA/EN_NURTURING/CONVERTIDA/DESCARTADA), fecha_captacion, comuna_id, sector, monto_estimado, urgencia, impacto_esperado | → BrechaERD, Actor, CalificacionOportunidad[], ActividadNurturing[], IPR |
| `CalificacionOportunidad` | id, oportunidad_id, criterio (ALINEACION_ERD/VIABILIDAD/EJECUTOR/DISPONIBILIDAD/URGENCIA/IMPACTO), score, observacion, fecha, evaluador_id | → Oportunidad, Funcionario |
| `ActividadNurturing` | id, oportunidad_id, tipo (ESTUDIO/ARTICULACION/COFINANC/ARI/COMPROMISO), descripcion, responsable_id, fecha_inicio, fecha_fin, estado, resultado | → Oportunidad, Funcionario |
| `BrechaERD` | id, objetivo_erd_id, descripcion, magnitud, territorio, prioridad | → ObjetivoERD, Oportunidad[] |

*Portafolio y Ciclo de Vida IPR:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `IPR` | id, codigo_bip, nombre, descripcion, naturaleza (IDI/PPR), mecanismo_id, estado, division_responsable, comuna_id, monto_total, riesgo_ejecucion, oportunidad_origen_id | → Oportunidad, Mecanismo, ObjetivoERD, Convenio[], Transferencia[], ActorIPR[], EvaluacionIPR[] |
| `ActorIPR` | id, ipr_id, actor_id, rol (enum: 10 roles), fase (enum: 10 fases), fecha_inicio, fecha_fin, activo | → IPR, Actor |
| `RatingEjecutor` | id, actor_id, periodo, score_total, score_rendiciones, score_tecnico, score_ejecucion, score_gobernanza, nivel (A/B/C/D), fecha_calculo | → Actor, HistorialRating[] |
| `HistorialRating` | id, rating_id, evento, score_anterior, score_nuevo, motivo, fecha | → RatingEjecutor |
| `EvaluacionIPR` | id, ipr_id, tipo (EX_ANTE/EX_DURANTE/EX_POST), fecha, evaluador_id, resultado, observaciones | → IPR, Funcionario |
| `IPRProblematica` | id, ipr_id, categoria (ESTANCADA/EN_MORA/SOBRECOSTO/ATRASO_CRITICO/RIESGO_LEGAL), fecha_deteccion, nivel_escalamiento, acciones_correctivas, estado | → IPR, AccionCorrectiva[] |
| `AccionCorrectiva` | id, ipr_problematica_id, descripcion, responsable_id, fecha_compromiso, fecha_cierre, estado | → IPRProblematica, Funcionario |
| `Mecanismo` | id, codigo, nombre, tope_utm, requiere_rs, naturaleza_aplicable, glosa_ref, metodologia_evaluacion | → IPR[], CategoriaMecanismo[], ReglaMecanismo[] |
| `CategoriaMecanismo` | id, mecanismo_id, codigo, nombre, descripcion, excepcion_limite | → Mecanismo |
| `ReglaMecanismo` | id, mecanismo_id, tipo (tope/plazo/cofinanc/excepcion), parametro, valor, descripcion | → Mecanismo |
| `FondoTematico` | id, mecanismo_id, nombre, monto_asignado, año, estado | → Mecanismo, IPR[] |
| `Presupuesto` | id, año, ley_numero, fecha_publicacion | → Partida[] |
| `Partida` | id, presupuesto_id, codigo, nombre | → Capitulo[] |
| `Asignacion` | id, item_id, inicial, vigente, devengado, pagado, saldo | ← Compromiso[] |
| `Transferencia` | id, convenio_id, numero, monto, fecha_giro, estado, cuenta_destino | → Convenio, Rendicion[] |
| `Rendicion` | id, transferencia_id, estado, fecha_ingreso, fecha_revision, monto_rendido | → Transferencia, DocumentoRendicion[], Observacion[] |
| `MoraRendicion` | id, rendicion_id, dias_mora, fecha_calculo, notificaciones_enviadas | → Rendicion |
| `IDR` | id, ipr_id, dimension (ECONOMICO/SOCIAL/TERRITORIAL/INSTITUCIONAL), indicador, valor_base, valor_logrado, fecha_medicion | → IPR |

---

#### 5.3 Dominio: EJECUCIÓN (D-EJEC)

**Propósito:** Gestionar la materialización de las iniciativas a través de convenios y seguimiento de obras.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               D-EJEC: EJECUCIÓN                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                         MÓDULO: CONVENIOS                                   │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   TIPOS DE CONVENIO                                                        │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   ┌─────────────────┬───────────────────────────────────────────────────┐  │   │
│   │   │ TIPO            │ DESCRIPCIÓN                                       │  │   │
│   │   ├─────────────────┼───────────────────────────────────────────────────┤  │   │
│   │   │ MANDATO         │ GORE encarga ejecución a otro órgano              │  │   │
│   │   │                 │ (ej: MOP ejecuta obra vial)                       │  │   │
│   │   ├─────────────────┼───────────────────────────────────────────────────┤  │   │
│   │   │ TRANSFERENCIA   │ GORE transfiere recursos a ejecutor               │  │   │
│   │   │                 │ (ej: Municipio ejecuta multicancha)               │  │   │
│   │   ├─────────────────┼───────────────────────────────────────────────────┤  │   │
│   │   │ COLABORACIÓN    │ Ejecución conjunta con aportes de ambos           │  │   │
│   │   │                 │ (ej: GORE+CORFO programa fomento)                 │  │   │
│   │   ├─────────────────┼───────────────────────────────────────────────────┤  │   │
│   │   │ MARCO           │ Convenio paraguas para múltiples iniciativas      │  │   │
│   │   │                 │ (ej: Marco con universidad para estudios)         │  │   │
│   │   ├─────────────────┼───────────────────────────────────────────────────┤  │   │
│   │   │ PROGRAMACIÓN    │ Convenio plurianual con Ministerio                │  │   │
│   │   │                 │ (ej: CP de infraestructura con MOP)               │  │   │
│   │   └─────────────────┴───────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   CICLO DE VIDA DEL CONVENIO                                               │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │                                                                             │   │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │   │
│   │   │ELABORA- │─▶│REVISIÓN │─▶│ FIRMA   │─▶│EJECUCIÓN│─▶│LIQUIDA- │          │   │
│   │   │CIÓN     │  │JURÍDICA │  │         │  │         │  │CIÓN     │          │   │
│   │   └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘          │   │
│   │        │            │            │            │            │               │   │
│   │        ▼            ▼            ▼            ▼            ▼               │   │
│   │   Borrador     V°B° UJ       Decreto     Transferenc.  Acta cierre        │   │
│   │   técnico                    aprueba     + monitoreo                      │   │
│   │                                                                             │   │
│   │   ESTADOS DEL CONVENIO                                                     │   │
│   │   • BORRADOR: En elaboración                                               │   │
│   │   • EN_REVISION_JURIDICA: UJ revisando                                     │   │
│   │   • PARA_FIRMA: Listo para firmar                                          │   │
│   │   • VIGENTE: Firmado, en ejecución                                         │   │
│   │   • PRORROGA_SOLICITADA: Pidió extensión plazo                             │   │
│   │   • ADDENDUM_EN_PROCESO: Modificación en trámite                           │   │
│   │   • TERMINADO: Ejecución física completa                                   │   │
│   │   • LIQUIDADO: Financieramente cerrado                                     │   │
│   │   • CADUCADO: Venció sin terminar                                          │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Catálogo de convenios con filtros                                      │   │
│   │   • Alertas de vencimiento de plazo                                        │   │
│   │   • Gestión de addendum y prórrogas                                        │   │
│   │   • Hitos de ejecución y % avance                                          │   │
│   │   • Control de garantías (boletas)                                         │   │
│   │   • Generación automática de decretos                                      │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      MÓDULO: PMO REGIONAL                                   │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   TORRE DE CONTROL DE PROYECTOS                                            │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   DIMENSIONES DE MONITOREO                                                 │   │
│   │   ┌─────────────┬─────────────┬─────────────┬─────────────┐                │   │
│   │   │   TIEMPO    │   COSTO     │   ALCANCE   │   RIESGO    │                │   │
│   │   ├─────────────┼─────────────┼─────────────┼─────────────┤                │   │
│   │   │ % avance    │ Presupuesto │ Cambios de  │ Identificac.│                │   │
│   │   │ vs plan     │ vs ejecución│ especificac.│ y mitigación│                │   │
│   │   │             │             │             │             │                │   │
│   │   │ Hitos       │ Desvío %    │ EP estados  │ Matriz      │                │   │
│   │   │ cumplidos   │             │             │ riesgos     │                │   │
│   │   └─────────────┴─────────────┴─────────────┴─────────────┘                │   │
│   │                                                                             │   │
│   │   SEMÁFORO DE PROYECTO                                                     │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   🟢 VERDE: Conforme a plan (±5%)                                          │   │
│   │   🟡 AMARILLO: Desviación menor (5-15%)                                    │   │
│   │   🔴 ROJO: Desviación crítica (>15%) o riesgo alto                         │   │
│   │   ⚫ NEGRO: Proyecto detenido/suspendido                                    │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Dashboard ejecutivo con semáforos                                      │   │
│   │   • Drill-down a detalle de proyecto                                       │   │
│   │   • Alertas proactivas de desvío                                           │   │
│   │   • Informes automáticos para Gabinete                                     │   │
│   │   • Gestión de riesgos y mitigaciones                                      │   │
│   │   • Estados de pago y avance físico                                        │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Entidades de datos D-EJEC:**

*Ejecución de Convenios (aspectos operativos):*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `HitoConvenio` | id, convenio_id, descripcion, fecha_compromiso, fecha_real, estado | → Convenio (D-NORM) |
| `EstadoPago` | id, convenio_id, numero, monto, fecha_solicitud, fecha_aprobacion, estado | → Convenio (D-NORM) |
| `Riesgo` | id, convenio_id, descripcion, probabilidad, impacto, mitigacion, estado | → Convenio (D-NORM) |

**Notas:**
- La entidad `Convenio` (SSOT) se define en D-NORM como acto administrativo formal.
- D-EJEC gestiona la *ejecución operativa* del convenio (hitos, pagos, riesgos).
- La entidad `Ejecutor` se unifica con `Actor` (D-COORD). El rol de ejecutor se representa mediante `actor_id`.
- El rating y ficha 360° del ejecutor se gestionan en D-FIN (Módulo Gestión de Ejecutores).

---

#### 5.4 Dominio: COORDINACIÓN Y GESTIÓN RELACIONAL (D-COORD)

**Propósito:** Gestionar las relaciones con actores territoriales, ejecutores, proveedores, ciudadanos y la gobernanza regional.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    D-COORD: COORDINACIÓN Y GESTIÓN RELACIONAL                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                       MÓDULO: MAPA DE ACTORES                               │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   ECOSISTEMA DE ACTORES REGIONALES                                         │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │                         ┌───────────────┐                                  │   │
│   │                         │ GOBERNADOR    │                                  │   │
│   │                         │     CORE      │                                  │   │
│   │                         └───────┬───────┘                                  │   │
│   │                                 │                                          │   │
│   │         ┌───────────────────────┼───────────────────────┐                  │   │
│   │         │                       │                       │                  │   │
│   │      ┌──┴──┐               ┌────┴────┐              ┌───┴───┐              │   │
│   │      │SEREMI│              │ GORE    │              │MUNICIPIOS            │   │
│   │      │(16) │              │Divisiones│              │  (21)  │             │   │
│   │      └──┬──┘               └────┬────┘              └───┬───┘              │   │
│   │         │                       │                       │                  │   │
│   │         ▼                       ▼                       ▼                  │   │
│   │      ┌────────┐          ┌───────────┐         ┌────────────┐             │   │
│   │      │Servicios│          │ Academia  │         │Soc. Civil  │             │   │
│   │      │Públicos │          │(UdeC,UBB) │         │Gremios,ONG │             │   │
│   │      └────────┘          └───────────┘         └────────────┘             │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Directorio de actores con contactos                                    │   │
│   │   • Historial de interacciones                                             │   │
│   │   • Convenios vigentes por actor                                           │   │
│   │   • Compromisos pendientes                                                 │   │
│   │   • Mapa georreferenciado de actores                                       │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      MÓDULO: EJECUTORES (REFERENCIA)                        │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   → Ver D-FIN: Módulo Gestión de Ejecutores (SSOT)                         │   │
│   │     Ficha 360°, Rating, Historial, Capacidades                             │   │
│   │                                                                             │   │
│   │   TIPOS DE EJECUTORES (clasificación en Actor)                             │   │
│   │   • Municipalidades (21 comunas)                                            │   │
│   │   • Servicios públicos regionales                                           │   │
│   │   • Universidades                                                           │   │
│   │   • Corporaciones y fundaciones                                             │   │
│   │   • Organizaciones comunitarias                                             │   │
│   │                                                                             │   │
│   │   INTEGRACIÓN                                                               │   │
│   │   • Actor.tipo = EJECUTOR vincula con rating en D-FIN                      │   │
│   │   • Historial relacional aquí, scoring financiero en D-FIN                 │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      MÓDULO: GESTIÓN DE PROVEEDORES                         │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Directorio de proveedores habilitados                                   │   │
│   │   • Evaluación de desempeño                                                 │   │
│   │   • Historial de compras y contratos                                        │   │
│   │   • Integración ChileProveedores                                            │   │
│   │   • Alertas de incumplimiento                                               │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      MÓDULO: PARTICIPACIÓN CIUDADANA                        │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Consultas públicas digitales                                            │   │
│   │   • Registro de audiencias                                                  │   │
│   │   • Seguimiento de solicitudes ciudadanas                                   │   │
│   │   • Integración OIRS                                                        │   │
│   │   • Cuenta pública interactiva                                              │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                   MÓDULO: GABINETE REGIONAL VIRTUAL                         │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   GESTIÓN DE GABINETE                                                      │   │
│   │   • Agenda de sesiones (ordinarias, extraordinarias)                       │   │
│   │   • Tabla de materias a tratar                                             │   │
│   │   • Actas digitales con trazabilidad                                       │   │
│   │   • Compromisos asignados con responsable y plazo                          │   │
│   │   • Seguimiento y alertas de vencimiento                                   │   │
│   │                                                                             │   │
│   │   MESAS TÉCNICAS: Seguridad, Desarrollo Económico, Infraestructura,        │   │
│   │                   Desarrollo Social, Medio Ambiente                        │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Entidades de datos D-COORD:**

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Actor` | id, tipo (municipalidad/servicio_publico/universidad/corporacion/ong/persona), rut, razon_social, contacto, comuna_id, scoring, estado | → ActorIPR[], Interaccion[], HistorialActor[] |
| `HistorialActor` | id, actor_id, evento, fecha, detalle | → Actor |
| `Proveedor` | id, rut, razon_social, rubro, evaluacion, estado_chileproveedores | → Compra[], Contrato[] |
| `SolicitudCiudadana` | id, fecha, solicitante, asunto, estado, respuesta | → Funcionario |
| `ConsultaPublica` | id, titulo, fecha_inicio, fecha_fin, participantes, resultados | → Documento |
| `CompromisoGabinete` | id, sesion_id, descripcion, responsable_id, fecha_limite, estado | → Funcionario |

**Nota:** Los roles de un `Actor` en una IPR (Postulante, Formulador, Patrocinador, Evaluador, Aprobador, Unidad_Financiera, Unidad_Tecnica, Entidad_Ejecutora, Contraparte, Beneficiario) se gestionan a través de la entidad `ActorIPR` en D-FIN, con indicación de fase del ciclo de vida.

---

#### 5.5 Dominio: GESTIÓN JURÍDICO-ADMINISTRATIVA Y CUMPLIMIENTO (D-NORM)

**Propósito:** Gestionar el ciclo completo de actos administrativos, procedimientos formales, cumplimiento normativo y control interno, asegurando la validez jurídica y trazabilidad de las actuaciones del GORE.

> **Visión:** Toda actuación formal del GORE —resoluciones, convenios, procedimientos— debe ser jurídicamente válida, trazable y verificable. Este dominio garantiza que los procesos jurídico-administrativos se ejecuten con rigor, cumpliendo plazos legales, fundamentación adecuada y control preventivo.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│            D-NORM: GESTIÓN JURÍDICO-ADMINISTRATIVA Y CUMPLIMIENTO                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ╔═══════════════════════════════════════════════════════════════════════════════╗  │
│  ║              MODELO DE GESTIÓN JURÍDICO-ADMINISTRATIVA                        ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                               ║  │
│  ║  TRES DIMENSIONES INTEGRADAS                                                  ║  │
│  ║  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐           ║  │
│  ║  │ ACTOS FORMALES    │ │ PROCEDIMIENTOS    │ │ CUMPLIMIENTO      │           ║  │
│  ║  │ • Resoluciones    │ │ • Ley 19.880      │ │ • Probidad        │           ║  │
│  ║  │ • Convenios       │ │ • Plazos legales  │ │ • Transparencia   │           ║  │
│  ║  │ • Reglamentos     │ │ • Recursos        │ │ • Control CGR     │           ║  │
│  ║  │ • Oficios         │ │ • Notificaciones  │ │ • Auditoría       │           ║  │
│  ║  └───────────────────┘ └───────────────────┘ └───────────────────┘           ║  │
│  ║                                                                               ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                    MÓDULO: ACTOS ADMINISTRATIVOS                            │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   CICLO DE VIDA DEL ACTO ADMINISTRATIVO                                    │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │   │
│   │   │BORRADOR│▶│VISACIÓN│▶│ FIRMA  │▶│TOMA    │▶│NOTIFIC.│▶│VIGENTE │       │   │
│   │   │        │ │Jurídica│ │  FEA   │ │RAZÓN   │ │        │ │        │       │   │
│   │   └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘       │   │
│   │                                    (si aplica)                             │   │
│   │                                                                             │   │
│   │   TIPOS DE ACTOS                                                           │   │
│   │   ┌─────────────────┬───────────────────────────────────────────────────┐  │   │
│   │   │ TIPO            │ CARACTERÍSTICAS                                   │  │   │
│   │   ├─────────────────┼───────────────────────────────────────────────────┤  │   │
│   │   │ Res. Exenta     │ Sin toma de razón CGR (mayoría de actos GORE)     │  │   │
│   │   │ Res. Afecta     │ Requiere toma de razón (compromiso plurianual,    │  │   │
│   │   │                 │ materias de personal, montos sobre umbral)        │  │   │
│   │   │ Decreto         │ Acto del Gobernador con efectos normativos        │  │   │
│   │   │ Oficio          │ Comunicación formal a terceros                    │  │   │
│   │   │ Acuerdo CORE    │ Decisiones colegiadas del Consejo Regional        │  │   │
│   │   │ Certificado     │ Constancia de hechos o estados                    │  │   │
│   │   └─────────────────┴───────────────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   ESTRUCTURA FORMAL (Ley 19.880)                                           │   │
│   │   ───────────────────────────────────────────────────────                  │   │
│   │   VISTOS     → Competencia y antecedentes que habilitan el acto           │   │
│   │   CONSIDERANDO → Fundamentos de hecho y de derecho (Art. 11, 41)          │   │
│   │   RESUELVO   → Decisión formal con articulado                             │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Generador asistido de actos con plantillas SFD/STS                    │   │
│   │   • Validación automática de estructura y fundamentación                  │   │
│   │   • Control de numeración correlativa por tipo                            │   │
│   │   • Flujo de firmas con FEA                                               │   │
│   │   • Envío automático a toma de razón (cuando aplica)                      │   │
│   │   • Notificación electrónica a interesados                                │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                 MÓDULO: PROCEDIMIENTOS ADMINISTRATIVOS                      │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   MARCO: LEY 19.880 (BASES PROCEDIMIENTO ADMINISTRATIVO)                   │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   ETAPAS DEL PROCEDIMIENTO                                                 │   │
│   │   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐              │   │
│   │   │ INICIACIÓN│─▶│INSTRUCCIÓN│─▶│FINALIZACIÓN─▶│IMPUGNACIÓN│              │   │
│   │   │           │  │           │  │           │  │(eventual) │              │   │
│   │   ├───────────┤  ├───────────┤  ├───────────┤  ├───────────┤              │   │
│   │   │• De oficio│  │• Pruebas  │  │• Resolución  │• Reposición│              │   │
│   │   │• A petición  │• Informes │  │• Desistim. │  │  (5 días) │              │   │
│   │   │• Denuncia │  │• Audiencia│  │• Abandono  │  │• Jerárquico│             │   │
│   │   └───────────┘  └───────────┘  └───────────┘  │  (5 días) │              │   │
│   │                                                 └───────────┘              │   │
│   │                                                                             │   │
│   │   PLAZOS LEGALES CRÍTICOS                                                  │   │
│   │   ┌────────────────────────────┬────────────────────────────────────────┐  │   │
│   │   │ PLAZO                      │ APLICACIÓN                             │  │   │
│   │   ├────────────────────────────┼────────────────────────────────────────┤  │   │
│   │   │ 5 días hábiles             │ Recurso de reposición                  │  │   │
│   │   │ 5 días hábiles             │ Recurso jerárquico                     │  │   │
│   │   │ 10 días hábiles            │ Respuesta a solicitudes ciudadanas     │  │   │
│   │   │ 30 días hábiles            │ Silencio administrativo positivo       │  │   │
│   │   │ 6 meses                    │ Plazo máximo procedimiento (prorrog.)  │  │   │
│   │   │ 2 años                     │ Invalidación de oficio                 │  │   │
│   │   └────────────────────────────┴────────────────────────────────────────┘  │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Control de plazos con alertas automáticas                             │   │
│   │   • Gestión de silencio administrativo                                    │   │
│   │   • Tramitación de recursos (reposición, jerárquico)                      │   │
│   │   • Notificaciones electrónicas con acuse                                 │   │
│   │   • Cómputo automático de días hábiles                                    │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                    MÓDULO: EXPEDIENTE ELECTRÓNICO                           │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   MARCO: LEY 21.180 (TRANSFORMACIÓN DIGITAL DEL ESTADO)                   │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   PRINCIPIOS                                                               │   │
│   │   • Expediente único por procedimiento                                    │   │
│   │   • Foliación automática y correlativa                                    │   │
│   │   • Trazabilidad completa de actuaciones                                  │   │
│   │   • Firma electrónica avanzada (FEA) para actos                           │   │
│   │   • Interoperabilidad con DocDigital                                      │   │
│   │                                                                             │   │
│   │   COMPONENTES                                                              │   │
│   │   ├─ Oficina de Partes Digital: Ingreso, distribución, seguimiento       │   │
│   │   ├─ Gestión de documentos: Clasificación, metadatos, búsqueda           │   │
│   │   ├─ Flujos de trabajo: Derivación, visación, firma                      │   │
│   │   └─ Archivo institucional: Retención, transferencia, eliminación        │   │
│   │                                                                             │   │
│   │   INTEGRACIONES: DocDigital, Cero Papel, ClaveÚnica                       │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                 MÓDULO: CUMPLIMIENTO Y CONTROL INTERNO                      │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   DIMENSIONES DE CUMPLIMIENTO                                              │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   PROBIDAD Y TRANSPARENCIA (Leyes 20.285, 20.880)                         │   │
│   │   ├─ Declaraciones de intereses y patrimonio                              │   │
│   │   ├─ Inhabilidades e incompatibilidades                                   │   │
│   │   ├─ Transparencia activa (portal institucional)                          │   │
│   │   └─ Solicitudes de acceso a información (Ley 20.285)                     │   │
│   │                                                                             │   │
│   │   LEY DE LOBBY (Ley 20.730)                                               │   │
│   │   ├─ Registro de audiencias                                               │   │
│   │   ├─ Gestiones de interés particular                                      │   │
│   │   └─ Viajes pagados por terceros                                          │   │
│   │                                                                             │   │
│   │   CONTROL PREVENTIVO CGR                                                   │   │
│   │   ├─ Toma de razón de actos afectos                                       │   │
│   │   ├─ Registro de actos exentos                                            │   │
│   │   └─ Respuesta a observaciones y reparos                                  │   │
│   │                                                                             │   │
│   │   CONTROL INTERNO                                                          │   │
│   │   ├─ Sumarios administrativos                                             │   │
│   │   ├─ Investigaciones sumarias                                             │   │
│   │   ├─ Auditoría interna                                                    │   │
│   │   └─ Plan de integridad institucional                                     │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Checklist de cumplimiento por tipo de acto                            │   │
│   │   • Alertas de vencimiento de declaraciones                               │   │
│   │   • Gestión de sumarios con plazos y etapas                               │   │
│   │   • Dashboard de estado de cumplimiento                                   │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                    MÓDULO: CONVENIOS INSTITUCIONALES                        │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   CICLO DE VIDA DEL CONVENIO                                               │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │   │
│   │   │NEGOCIAC│▶│REDACCIÓ│▶│VISACIÓN│▶│APROBAC.│▶│EJECUCIÓ│▶│TÉRMINO │       │   │
│   │   │        │ │        │ │Jurídica│ │Res.+CGR│ │        │ │        │       │   │
│   │   └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘       │   │
│   │                                                                             │   │
│   │   TIPOS DE CONVENIOS                                                       │   │
│   │   • Convenio Marco: Establece relación general                            │   │
│   │   • Convenio de Colaboración: Sin transferencia de recursos               │   │
│   │   • Convenio de Transferencia: Con recursos GORE a ejecutor               │   │
│   │   • Convenio Específico: Derivado de convenio marco                       │   │
│   │   • Convenio de Programación: Plurianual con ministerios                  │   │
│   │                                                                             │   │
│   │   ACTOS ASOCIADOS                                                          │   │
│   │   • Resolución aprobatoria del convenio                                   │   │
│   │   • Resolución de modificación                                            │   │
│   │   • Resolución de resciliación                                            │   │
│   │   • Resolución de término anticipado                                      │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Biblioteca de cláusulas tipo                                          │   │
│   │   • Control de vigencia y renovaciones                                    │   │
│   │   • Alertas de vencimiento                                                │   │
│   │   • Vinculación con rendiciones (D-FIN)                                   │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                    MÓDULO: REGLAMENTOS REGIONALES                           │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   POTESTAD REGLAMENTARIA (Art. 16 letra d LOC GORE)                        │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │   │
│   │   │INICIATIV│─▶│CONSULTA │─▶│ CORE    │─▶│TOMA     │─▶│PUBLICAC.│          │   │
│   │   │         │  │PÚBLICA  │  │aprueba  │  │RAZÓN    │  │D.Oficial│          │   │
│   │   └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘          │   │
│   │                                                                             │   │
│   │   TIPOS: Desarrollo regional, Organización interna, Instructivos          │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                     MÓDULO: BIBLIOTECA NORMATIVA                            │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   REPOSITORIO CENTRAL DE NORMATIVA APLICABLE                               │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │   CATEGORÍAS: Constitución, LOC GORE, Leyes Presupuesto, DS, Res. CGR,    │   │
│   │               Circulares DIPRES, Oficios SUBDERE, Reglamentos regionales  │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Búsqueda full-text y por metadatos                                    │   │
│   │   • Versionamiento de normas                                              │   │
│   │   • Alertas de cambios normativos                                         │   │
│   │   • Vinculación norma ↔ proceso ↔ acto                                    │   │
│   │   • Checklist de cumplimiento por tipo de operación                       │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Entidades de datos D-NORM:**

*Actos Administrativos:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `ActoAdministrativo` | id, tipo (RES_EXENTA/RES_AFECTA/DECRETO/OFICIO/ACUERDO_CORE/CERTIFICADO), numero, fecha, materia, estado_tramitacion, requiere_toma_razon, expediente_id | → ExpedienteElectronico, FirmaActo[], Notificacion[] |
| `FirmaActo` | id, acto_id, firmante_id, tipo (VISACION/FIRMA_PRINCIPAL/MINISTRO_FE), fecha, estado | → ActoAdministrativo, Funcionario |
| `Notificacion` | id, acto_id, destinatario, medio (ELECTRONICO/CARTA_CERTIFICADA/PERSONAL), fecha_envio, fecha_recepcion, estado | → ActoAdministrativo |

*Procedimientos y Expedientes:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `ExpedienteElectronico` | id, codigo, materia, fecha_inicio, estado, folio_actual, procedimiento_id | → DocumentoExpediente[], ActoAdministrativo[] |
| `DocumentoExpediente` | id, expediente_id, folio, tipo, fecha_ingreso, origen, metadata | → ExpedienteElectronico |
| `ProcedimientoAdmin` | id, tipo, iniciador, fecha_inicio, plazo_legal, fecha_vencimiento, estado, resolucion_id | → ExpedienteElectronico, ActoAdministrativo |
| `RecursoAdmin` | id, procedimiento_id, tipo (REPOSICION/JERARQUICO), fecha_interposicion, plazo_respuesta, estado, resolucion_id | → ProcedimientoAdmin, ActoAdministrativo |

*Cumplimiento y Control:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `DeclaracionInteres` | id, funcionario_id, tipo (INTERESES/PATRIMONIO), fecha, estado_verificacion, url_transparencia | → Funcionario |
| `AudienciaLobby` | id, funcionario_id, fecha, solicitante, materia, resultado | → Funcionario |
| `SumarioAdmin` | id, tipo (SUMARIO/INVESTIGACION_SUMARIA), fecha_inicio, inculpado_id, fiscal_id, estado, sancion | → Funcionario |
| `ControlCumplimiento` | id, norma_id, proceso_id, requisito, estado, fecha_verificacion, observaciones | → NormaVigente |

*Convenios:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Convenio` | id, tipo (MARCO/COLABORACION/TRANSFERENCIA/ESPECIFICO/PROGRAMACION), numero, partes[], objeto, fecha_suscripcion, vigencia_inicio, vigencia_fin, estado, acto_aprobatorio_id | → ActoAdministrativo, ModificacionConvenio[], Rendicion[] (D-FIN) |
| `ModificacionConvenio` | id, convenio_id, tipo (MODIFICACION/RESCILIACION/TERMINO), fecha, acto_id, descripcion | → Convenio, ActoAdministrativo |

*Normativa:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Reglamento` | id, numero, titulo, fecha_aprobacion, fecha_publicacion, estado | → ArticuloReglamento[], ProcesoAfectado[] |
| `NormaVigente` | id, tipo (LEY/DS/CIRCULAR/RESOLUCION_CGR/OFICIO), numero, titulo, organismo_emisor, fecha_vigencia, url | → ControlCumplimiento[], ChecklistNorma[] |
| `ChecklistNorma` | id, norma_id, tipo_operacion, requisito, obligatorio | → NormaVigente |

---

#### 5.6 Dominio: GESTIÓN DE RECURSOS INSTITUCIONALES (D-BACK)

**Propósito:** Gestionar integralmente los recursos institucionales —financieros, humanos y materiales— que habilitan el funcionamiento del GORE, brindando al funcionario una experiencia unificada para todos los procesos de administración de recursos.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    D-BACK: GESTIÓN DE RECURSOS INSTITUCIONALES                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    ÁREA: GESTIÓN FINANCIERA Y TESORERÍA                       │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │  • Contabilidad patrimonial integrada con SIGFE                               │  │
│  │  • Tesorería: flujo de caja, conciliaciones bancarias automáticas             │  │
│  │  • Gestión de fondos por rendir y anticipos                                   │  │
│  │  • Pagos electrónicos obligatorios (Art. 8 Ley Presupuestos)                  │  │
│  │  • Generación de archivos bancarios para transferencias masivas               │  │
│  │  • Reportes financieros consolidados y cierre mensual/anual                   │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    ÁREA: GESTIÓN DE PERSONAS (RRHH)                           │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                               │  │
│  │  CICLO DE VIDA DEL FUNCIONARIO                                               │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │  │
│  │  │SELECCIÓN│─▶│INGRESO  │─▶│DESARROLLO─▶│MOVILIDAD│─▶│ EGRESO  │            │  │
│  │  │Concurso │  │Decreto  │  │Capacitac.│  │Ascensos │  │Finiquito│            │  │
│  │  │Perfil   │  │Inducción│  │Desempeño │  │Traslados│  │Certific.│            │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │  │
│  │                                                                               │  │
│  │  SUBMÓDULOS:                                                                  │  │
│  │  ├─ Dotación: Planta, Contrata, Honorarios, Código Trabajo                   │  │
│  │  ├─ Remuneraciones: Escala EUS, asignaciones, descuentos, PREVIRED           │  │
│  │  ├─ Tiempo y Asistencia: Control biométrico, permisos, licencias médicas     │  │
│  │  ├─ Desarrollo: DNC, Plan Capacitación, Calificaciones, Clima Laboral        │  │
│  │  └─ Bienestar: Afiliación, beneficios, préstamos, convenios                  │  │
│  │                                                                               │  │
│  │  INTEGRACIONES: SIAPER, SIGPER, PREVIRED, I-MED (licencias electrónicas)     │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    ÁREA: ABASTECIMIENTO Y PATRIMONIO                          │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                               │  │
│  │  COMPRAS PÚBLICAS (Ley 19.886)                                               │  │
│  │  ├─ Plan Anual de Compras (PAC): planificación, priorización, publicación    │  │
│  │  ├─ Mecanismos: Convenio Marco, Licitación Pública/Privada, Trato Directo    │  │
│  │  ├─ Ciclo OC: Emisión → Aceptación → Recepción Conforme → Pago               │  │
│  │  ├─ Contratos: Formalización, administrador, estados de pago, multas         │  │
│  │  └─ Garantías: Seriedad oferta, fiel cumplimiento, custodia y devolución     │  │
│  │                                                                               │  │
│  │  INVENTARIOS Y BODEGAS                                                       │  │
│  │  ├─ Catálogo maestro de artículos con codificación y atributos               │  │
│  │  ├─ Gestión multi-bodega (Central, Economato, Aseo, Mantención, EPP)         │  │
│  │  ├─ Ingresos/Egresos: Recepción OC, despacho, préstamos, ajustes             │  │
│  │  ├─ Valorización: PPP/FIFO, cierre mensual, cuadratura contable              │  │
│  │  └─ Alertas: Stock mínimo, vencimientos, artículos sin movimiento            │  │
│  │                                                                               │  │
│  │  ACTIVO FIJO (NICSP 17/21/31)                                                │  │
│  │  ├─ Alta: Codificación, etiquetado (código barras/QR), fotografía            │  │
│  │  ├─ Valorización: Costo adquisición, depreciación línea recta, vida útil     │  │
│  │  ├─ Movimientos: Traslados, préstamos, comodatos, mantención mayor           │  │
│  │  ├─ Baja: Obsolescencia, siniestro, remate, donación                         │  │
│  │  └─ Inventario físico anual con conciliación y responsables                  │  │
│  │                                                                               │  │
│  │  SERVICIOS GENERALES Y FLOTA                                                 │  │
│  │  ├─ Mantención infraestructura: Preventiva, correctiva, órdenes de trabajo   │  │
│  │  ├─ Contratos externalizados: Aseo, seguridad, jardines, ascensores          │  │
│  │  ├─ Flota vehicular: Registro, conductores, solicitud/asignación             │  │
│  │  ├─ Bitácora de uso, control combustible, kilometraje                        │  │
│  │  └─ Indicadores: Disponibilidad, utilización, costo por kilómetro            │  │
│  │                                                                               │  │
│  │  INTEGRACIÓN: Mercado Público (OC, adjudicaciones, proveedores)              │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Nota:** La gestión documental, expediente electrónico y actos administrativos se gestionan en D-NORM (Gestión Jurídico-Administrativa y Cumplimiento).

**Entidades de datos D-BACK:**

*Gestión de Personas:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Funcionario` | id, rut, nombre, cargo, division, calidad_juridica, grado, fecha_ingreso | → Contrato[], Liquidacion[], Asistencia[], Capacitacion[], AfiliacionBienestar |
| `Contrato` | id, funcionario_id, tipo (planta/contrata/honorarios), grado, fecha_inicio, fecha_termino, decreto | → Funcionario |
| `Liquidacion` | id, funcionario_id, periodo, sueldo_base, asignaciones[], descuentos[], liquido | → Funcionario |
| `Asistencia` | id, funcionario_id, fecha, hora_entrada, hora_salida, tipo_marca | → Funcionario |
| `PermisoLicencia` | id, funcionario_id, tipo (feriado/administrativo/licencia_medica), fecha_inicio, fecha_fin, estado | → Funcionario |
| `Capacitacion` | id, funcionario_id, curso, fecha, horas, evaluacion, costo | → Funcionario |
| `Calificacion` | id, funcionario_id, periodo, nota, lista (1-4), junta_id | → Funcionario |
| `AfiliacionBienestar` | id, funcionario_id, fecha_afiliacion, aporte_mensual, estado | → Funcionario, Beneficio[], Prestamo[] |

*Abastecimiento y Compras:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `PlanCompras` | id, año, estado, fecha_publicacion, monto_total | → ItemPAC[] |
| `ProcesoCompra` | id, numero, tipo (CM/licitacion/trato_directo), monto_estimado, estado, fecha_adjudicacion | → Proveedor (D-COORD), OrdenCompra[], ContratoCompra |
| `OrdenCompra` | id, proceso_id, numero_oc, monto, estado, fecha_emision, fecha_recepcion_conforme | → ProcesoCompra, ItemOC[] |
| `ContratoCompra` | id, proceso_id, administrador_id, monto, fecha_inicio, fecha_termino | → ProcesoCompra, EstadoPago[], Multa[], Garantia[] |
| `Garantia` | id, contrato_id, tipo (seriedad/fiel_cumplimiento/correcta_ejecucion), monto, vencimiento, estado | → ContratoCompra |

*Inventarios y Activo Fijo:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Articulo` | id, codigo, nombre, familia, unidad_medida, cuenta_contable, stock_minimo, stock_maximo | → MovimientoInventario[] |
| `Bodega` | id, nombre, tipo, ubicacion, encargado_id | → MovimientoInventario[] |
| `MovimientoInventario` | id, articulo_id, bodega_id, tipo (ingreso/egreso/ajuste), cantidad, costo_unitario, fecha, oc_id | → Articulo, Bodega, OrdenCompra |
| `ActivoFijo` | id, codigo, descripcion, tipo_bien, valor_adquisicion, valor_libro, vida_util_meses, responsable_id, ubicacion_fisica | → Depreciacion[], MovimientoActivo[] |
| `Depreciacion` | id, activo_id, periodo, monto_mensual, acumulada | → ActivoFijo |
| `MovimientoActivo` | id, activo_id, tipo (alta/traslado/baja/revalorizacion), fecha, detalle, responsable_nuevo_id | → ActivoFijo |

*Flota Vehicular:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Vehiculo` | id, patente, marca, modelo, año, activo_fijo_id, estado, km_actual | → ActivoFijo, BitacoraVehiculo[], CargaCombustible[], DocumentoVehiculo[] |
| `Conductor` | id, funcionario_id, licencia_clase, licencia_vencimiento, autorizado | → Funcionario, BitacoraVehiculo[] |
| `BitacoraVehiculo` | id, vehiculo_id, conductor_id, fecha_salida, fecha_retorno, km_inicial, km_final, destino, proposito | → Vehiculo, Conductor |
| `CargaCombustible` | id, vehiculo_id, fecha, litros, monto, km_odometro, estacion | → Vehiculo |
| `OrdenTrabajoMant` | id, vehiculo_id, tipo (preventiva/correctiva), descripcion, fecha, costo, proveedor_id | → Vehiculo, Proveedor (D-COORD) |

*Gestión Documental:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Expediente` | id, numero, tipo, fecha_inicio, estado, folio_actual | → Documento[] |
| `Documento` | id, expediente_id, tipo (resolucion/decreto/oficio/memo), numero, fecha, asunto, estado, firmantes[], archivo_url | → Expediente |

**Nota:** La entidad `Proveedor` se define en D-COORD. Todas las compras, contratos y mantenciones referencian proveedores del directorio unificado.

---

#### 5.7 Dominio: GOBERNANZA DIGITAL (D-TDE)

**Propósito:** Gestionar el cumplimiento normativo de la Transformación Digital del Estado (obligación legal), y ejercer el liderazgo y gobernanza de la TDE en las instituciones públicas de la región, impulsando la evolución del aparato público regional.

> **Enfoque Dual:** La TDE es un mandato legal que el GORE debe cumplir (Ley 21.180, meta cero papel 2027). Pero más allá del cumplimiento, representa una oportunidad estratégica para que el GORE asuma la **rectoría de la transformación digital regional**, coordinando y habilitando a municipalidades, servicios públicos y organismos del territorio.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    D-TDE: TRANSFORMACIÓN DIGITAL REGIONAL                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ╔═══════════════════════════════════════════════════════════════════════════════╗  │
│  ║              CAPA 1: CUMPLIMIENTO NORMATIVO (OBLIGATORIO)                     ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                               ║  │
│  ║  MARCO LEGAL                           NORMAS TÉCNICAS (DS 7-12/2022)        ║  │
│  ║  ├─ Ley 21.180 (TDE)                   ├─ DS 7: Seguridad (NIST, MFA)        ║  │
│  ║  ├─ Ley 21.658 (SGD)                   ├─ DS 8: Notificaciones (DDU)         ║  │
│  ║  ├─ Ley 21.719 (Datos Personales)      ├─ DS 9: Autenticación (ClaveÚnica)   ║  │
│  ║  ├─ Ley 21.663 (Ciberseguridad)        ├─ DS 10: Documentos (IUIe)           ║  │
│  ║  └─ DS 4/2020 (Reglamento TDE)         ├─ DS 11: Calidad (CPAT, Coord. TD)   ║  │
│  ║                                        └─ DS 12: Interoperabilidad (PISEE)   ║  │
│  ║                                                                               ║  │
│  ║  PLAZOS CRÍTICOS                       PLATAFORMAS NACIONALES                ║  │
│  ║  ├─ 2025: CPAT actualizado             ├─ ClaveÚnica: Autenticación          ║  │
│  ║  ├─ 2026: PISEE obligatorio            ├─ DocDigital: Gestión documental     ║  │
│  ║  └─ 2027: Cero papel                   ├─ PISEE: Interoperabilidad           ║  │
│  ║                                        ├─ FirmaGob: Firma electrónica        ║  │
│  ║  ROLES INSTITUCIONALES                 └─ datos.gob.cl: Datos abiertos       ║  │
│  ║  ├─ Coordinador de TD (designado)                                            ║  │
│  ║  ├─ Comité de TD (gobernanza)                                                ║  │
│  ║  └─ Responsable Seguridad (ANCI)                                             ║  │
│  ║                                                                               ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                      │
│  ╔═══════════════════════════════════════════════════════════════════════════════╗  │
│  ║              CAPA 2: LIDERAZGO REGIONAL TDE (OPORTUNIDAD)                     ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                               ║  │
│  ║  GOBERNANZA TDE REGIONAL               GORE COMO RECTOR REGIONAL             ║  │
│  ║  ┌─────────────────────────────────────────────────────────────────────────┐ ║  │
│  ║  │                              GORE ÑUBLE                                 │ ║  │
│  ║  │                          (Rector TDE Regional)                          │ ║  │
│  ║  │                                   │                                     │ ║  │
│  ║  │      ┌────────────────────────────┼────────────────────────────┐        │ ║  │
│  ║  │      ▼                            ▼                            ▼        │ ║  │
│  ║  │ ┌──────────┐              ┌──────────────┐              ┌──────────┐    │ ║  │
│  ║  │ │MUNICIPIOS│              │SERV. PÚBLICOS│              │OTROS ORG.│    │ ║  │
│  ║  │ │21 comunas│              │SEREMIs, Dir. │              │Universid.│    │ ║  │
│  ║  │ └──────────┘              └──────────────┘              └──────────┘    │ ║  │
│  ║  └─────────────────────────────────────────────────────────────────────────┘ ║  │
│  ║                                                                               ║  │
│  ║  FUNCIONES DE RECTORÍA                 SERVICIOS COMPARTIDOS                 ║  │
│  ║  ├─ Mesa Regional TDE                  ├─ Nodo PISEE Regional                ║  │
│  ║  ├─ Diagnóstico madurez instituciones  ├─ Hub DocDigital regional            ║  │
│  ║  ├─ Plan Regional TDE (hoja de ruta)   ├─ Broker ClaveÚnica                  ║  │
│  ║  ├─ Capacitación competencias digitales├─ Lago de datos regional             ║  │
│  ║  └─ Acompañamiento técnico municipal   └─ SOC regional (ciberseguridad)      ║  │
│  ║                                                                               ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    MÓDULO: CPAT INSTITUCIONAL                                 │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │  Catálogo de Procedimientos Administrativos y Trámites (obligatorio DS 11)   │  │
│  │  ├─ Inventario trámites GORE con nivel digitalización (0-5)                  │  │
│  │  ├─ Requisitos, plazos legales, brechas identificadas                        │  │
│  │  ├─ Plan de digitalización priorizado                                        │  │
│  │  └─ Actualización semestral (mayo/noviembre) para reporte SGD                │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    MÓDULO: INTEROPERABILIDAD                                  │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │  ├─ Catálogo servicios PISEE consumidos/publicados                           │  │
│  │  ├─ Gestor de Acuerdos: Solicitudes intercambio (15 días hábiles)            │  │
│  │  ├─ Gestor de Autorizaciones: Datos sensibles                                │  │
│  │  └─ Monitoreo disponibilidad y métricas de uso                               │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    MÓDULO: CIBERSEGURIDAD                                     │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │  Marco NIST: Identificar → Proteger → Detectar → Responder → Recuperar       │  │
│  │  ├─ Política de Seguridad institucional aprobada                             │  │
│  │  ├─ Inscripción ANCI (GORE es "servicio esencial" Ley 21.663)                │  │
│  │  ├─ Responsable Institucional de Seguridad designado                         │  │
│  │  ├─ Plan continuidad operativa (BCP) y recuperación (DRP)                    │  │
│  │  └─ Gestión de incidentes con notificación CSIRT                             │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Entidades de datos D-TDE:**

*Cumplimiento Normativo:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `NormaTDE` | id, codigo (DS7-12), nombre, fecha_publicacion, plazo_cumplimiento | → CumplimientoNorma[], Requisito[] |
| `CumplimientoNorma` | id, norma_id, institucion_id, estado, fecha_evaluacion, evidencia_url | → NormaTDE, InstitucionRegional |
| `Tramite` | id, nombre, descripcion, nivel_digitalizacion (0-5), plazo_legal, brechas | → PlanDigitalizacion |
| `ServicioPISEE` | id, nombre, tipo (consumido/publicado), proveedor, estado, volumen_mensual | → AcuerdoIntercambio[] |

*Gobernanza Regional TDE:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `InstitucionRegional` | id, nombre, tipo (municipio/servicio/otro), coordinador_td, nivel_madurez_tde | → CumplimientoNorma[], DiagnosticoTDE[] |
| `MesaTDE` | id, fecha, participantes[], acuerdos[], seguimiento | → InstitucionRegional[] |
| `DiagnosticoTDE` | id, institucion_id, fecha, dimensiones[], nivel_global, brechas_criticas | → InstitucionRegional, PlanAccion |
| `PlanRegionalTDE` | id, periodo, objetivos[], hitos[], responsables[], presupuesto | → InstitucionRegional[] |

*Ciberseguridad:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `ActivoTI` | id, nombre, tipo, clasificacion, responsable_id, criticidad | → Vulnerabilidad[], IncidenteSeguridad[] |
| `IncidenteSeguridad` | id, fecha, tipo, severidad, activos_afectados[], estado, notificacion_csirt | → ActivoTI[] |
| `PlanContinuidad` | id, tipo (BCP/DRP), version, fecha_aprobacion, fecha_prueba | — |

---

#### 5.8 Dominio: INTELIGENCIA TERRITORIAL (D-TERR)

**Propósito:** Gestionar la información geoespacial regional y proveer inteligencia territorial para la toma de decisiones.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         D-TERR: INTELIGENCIA TERRITORIAL                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      MÓDULO: INFRAESTRUCTURA DE DATOS ESPACIALES            │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   CAPAS BASE                                                                │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │   • División político-administrativa (región, provincias, comunas)          │   │
│   │   • Localidades y entidades pobladas                                        │   │
│   │   • Red vial y conectividad                                                 │   │
│   │   • Hidrografía                                                             │   │
│   │   • Áreas protegidas y restricciones                                        │   │
│   │                                                                             │   │
│   │   CAPAS TEMÁTICAS                                                          │   │
│   │   • Zonificación PROT                                                       │   │
│   │   • Localización de proyectos IPR                                           │   │
│   │   • Equipamiento e infraestructura                                          │   │
│   │   • Riesgos naturales                                                       │   │
│   │   • Indicadores socioeconómicos por comuna                                  │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      MÓDULO: OBSERVATORIO REGIONAL                          │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   DIMENSIONES DE ANÁLISIS                                                  │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │   • Demográficos: Población, migración, envejecimiento                     │   │
│   │   • Económicos: PIB regional, empleo, empresas                             │   │
│   │   • Sociales: Pobreza, educación, salud                                    │   │
│   │   • Ambientales: Recursos hídricos, suelos, biodiversidad                  │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Dashboards de indicadores regionales                                   │   │
│   │   • Comparativas intercomunales                                            │   │
│   │   • Series de tiempo y tendencias                                          │   │
│   │   • Alertas de indicadores críticos                                        │   │
│   │   • Informes automáticos para CORE                                         │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      MÓDULO: VISOR GEOESPACIAL                              │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Visor web con capas activables                                          │   │
│   │   • Búsqueda por ubicación, proyecto, comuna                                │   │
│   │   • Herramientas de medición y análisis                                     │   │
│   │   • Exportación de mapas e informes                                         │   │
│   │   • Integración con IDE Chile                                               │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Entidades de datos D-TERR:**

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `CapaGeoespacial` | id, nombre, tipo, fuente, fecha_actualizacion, geometria_tipo | → Metadato |
| `IndicadorTerritorial` | id, nombre, dimension, formula, periodicidad | → MedicionIndicador[], ObjetivoERD (D-PLAN) |
| `MedicionIndicador` | id, indicador_id, comuna_id, periodo, valor | → IndicadorTerritorial, Comuna |
| `ZonaPROT` | id, codigo, nombre, macrozona_id, geometria, uso_principal | → UsoPermitido[], IPR (D-FIN) |

**Nota:** D-TERR provee la capa territorial para D-PLAN (validación PROT, indicadores ERD) y D-FIN (localización IPR).

---

#### 5.9 Dominio: GESTIÓN INSTITUCIONAL TRANSVERSAL (D-GESTION)

**Propósito:** Gestionar el desempeño institucional, la mejora continua y la operación transversal del GORE mediante metodologías de gestión por resultados.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         D-GESTION: GESTIÓN INSTITUCIONAL                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                         MÓDULO: OKRs INSTITUCIONALES                        │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   OBJECTIVES & KEY RESULTS                                                 │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   ESTRUCTURA OKR                                                           │   │
│   │   ┌───────────────────────────────────────────────────────────────────┐    │   │
│   │   │ OBJETIVO (O)                                                      │    │   │
│   │   │ └── "Mejorar la eficiencia en ejecución presupuestaria"          │    │   │
│   │   │     ├── KR1: Alcanzar 95% ejecución al 31/12                     │    │   │
│   │   │     ├── KR2: Reducir mora rendiciones a <5%                       │    │   │
│   │   │     └── KR3: Cerrar 100% convenios vencidos                       │    │   │
│   │   └───────────────────────────────────────────────────────────────────┘    │   │
│   │                                                                             │   │
│   │   CICLO OKR (Trimestral)                                                   │   │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                      │   │
│   │   │DEFINIR  │─▶│EJECUTAR │─▶│REVISAR  │─▶│CERRAR   │                      │   │
│   │   │OKRs     │  │         │  │(semanal)│  │y AJUSTAR│                      │   │
│   │   └─────────┘  └─────────┘  └─────────┘  └─────────┘                      │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Definición de OKRs por división/unidad                                 │   │
│   │   • Vinculación OKR ↔ ERD (alineamiento estratégico)                       │   │
│   │   • Tracking semanal de Key Results                                        │   │
│   │   • Alertas de OKRs en riesgo                                              │   │
│   │   • Retrospectivas trimestrales                                            │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                         MÓDULO: H_GORE (ÍNDICE DE SALUD)                    │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   ÍNDICE COMPUESTO DE SALUD INSTITUCIONAL                                  │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   DIMENSIONES H_GORE                                                       │   │
│   │   ┌─────────────────────┬──────────────────────────────────────────────┐   │   │
│   │   │ DIMENSIÓN           │ INDICADORES                                  │   │   │
│   │   ├─────────────────────┼──────────────────────────────────────────────┤   │   │
│   │   │ Ejecución Presup.   │ % ejecución, desvío vs plan, días para cierre│   │   │
│   │   │ Cartera IPR         │ % avance, proyectos en riesgo, estancados    │   │   │
│   │   │ Rendiciones         │ % mora, días promedio revisión, rechazos     │   │   │
│   │   │ Convenios           │ % vigentes OK, vencimientos próximos         │   │   │
│   │   │ Cumplimiento TDE    │ % normas cumplidas, brechas críticas         │   │   │
│   │   │ Satisfacción        │ NPS interno, tiempos respuesta               │   │   │
│   │   └─────────────────────┴──────────────────────────────────────────────┘   │   │
│   │                                                                             │   │
│   │   CÁLCULO H_GORE                                                           │   │
│   │   H_gore = Σ (peso_i × indicador_normalizado_i)                           │   │
│   │   Escala: 0-100 | Meta: ≥80 (zona verde)                                  │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Dashboard H_gore en tiempo real                                        │   │
│   │   • Drill-down por dimensión                                               │   │
│   │   • Tendencia histórica                                                    │   │
│   │   • Alertas de degradación                                                 │   │
│   │   • Benchmark con otros GOREs (cuando disponible)                          │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                         MÓDULO: PLAYBOOKS OPERATIVOS                        │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   BIBLIOTECA DE PROCEDIMIENTOS ESTANDARIZADOS                              │   │
│   │   ══════════════════════════════════════════════════════════════════════   │   │
│   │                                                                             │   │
│   │   CATEGORÍAS DE PLAYBOOKS                                                  │   │
│   │   • Operativos: Cómo ejecutar procesos recurrentes                         │   │
│   │   • De Crisis: Qué hacer ante situaciones de emergencia                    │   │
│   │   • De Onboarding: Guías para nuevos funcionarios                          │   │
│   │   • De Cierre: Procedimientos de fin de período/gestión                    │   │
│   │                                                                             │   │
│   │   ESTRUCTURA PLAYBOOK                                                      │   │
│   │   • Objetivo y alcance                                                     │   │
│   │   • Roles responsables                                                     │   │
│   │   • Pasos detallados (checklist)                                           │   │
│   │   • Decisiones y bifurcaciones                                             │   │
│   │   • Documentos/sistemas involucrados                                       │   │
│   │   • Criterios de éxito                                                     │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Catálogo de playbooks por proceso                                      │   │
│   │   • Ejecución guiada paso a paso                                           │   │
│   │   • Versionamiento y mejora continua                                       │   │
│   │   • Métricas de uso y efectividad                                          │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                         MÓDULO: MEJORA CONTINUA                             │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                             │   │
│   │   CICLO PDCA INSTITUCIONAL                                                 │   │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                      │   │
│   │   │  PLAN   │─▶│   DO    │─▶│  CHECK  │─▶│   ACT   │─┐                    │   │
│   │   └─────────┘  └─────────┘  └─────────┘  └─────────┘ │                    │   │
│   │        ▲                                              │                    │   │
│   │        └──────────────────────────────────────────────┘                    │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Registro de oportunidades de mejora                                    │   │
│   │   • Priorización y asignación de iniciativas                               │   │
│   │   • Seguimiento de implementación                                          │   │
│   │   • Medición de impacto                                                    │   │
│   │   • Lecciones aprendidas                                                   │   │
│   │                                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Entidades de datos D-GESTION:**

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `OKR` | id, periodo, tipo (institucional/division/unidad), objetivo, estado | → KeyResult[], Division |
| `KeyResult` | id, okr_id, descripcion, meta, valor_actual, confianza | → OKR, Medicion[] |
| `H_gore` | id, fecha, valor_compuesto, dimension_scores (JSON) | → HistoricoH_gore[] |
| `Playbook` | id, codigo, nombre, categoria, version, estado | → PasoPlaybook[], Ejecucion[] |
| `PasoPlaybook` | id, playbook_id, orden, descripcion, responsable_rol, checklist | → Playbook |
| `IniciativaMejora` | id, descripcion, origen, estado, responsable_id, impacto_esperado | → Funcionario |

---

#### 5.10 Dominio: EVOLUCIÓN E INTELIGENCIA (D-EVOL)

**Propósito:** Gestionar la evolución nativa del sistema operativo regional hacia niveles superiores de madurez organizacional, basándose en un framework formal de transformación que va más allá del cumplimiento normativo.

> **Evolución Nativa vs. Cumplimiento:** Mientras D-TDE asegura el piso normativo (Ley 21.180), D-EVOL representa el **techo de capacidades**. La TDE es obligatoria; la evolución nativa es estratégica. GORE_OS no solo cumple, sino que **lidera** la transformación del aparato público regional.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    D-EVOL: EVOLUCIÓN NATIVA DEL SISTEMA                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ╔═══════════════════════════════════════════════════════════════════════════════╗  │
│  ║                    FRAMEWORK DE EVOLUCIÓN ORGANIZACIONAL                      ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                               ║  │
│  ║  PRIMITIVOS FUNDAMENTALES (P1-P5)                                            ║  │
│  ║  ┌─────────────────────────────────────────────────────────────────────────┐ ║  │
│  ║  │ P1: CAPACIDAD    │ P2: FLUJO       │ P3: INFORMACIÓN                   │ ║  │
│  ║  │ Quién ejecuta    │ Cómo se         │ Qué se transforma                 │ ║  │
│  ║  │ (Humano/IA/Mixto)│ transforma      │ (entrada/salida)                  │ ║  │
│  ║  ├─────────────────────────────────────────────────────────────────────────┤ ║  │
│  ║  │ P4: LÍMITE                    │ P5: PROPÓSITO                          │ ║  │
│  ║  │ Qué restringe (normas,       │ Para qué (OKRs, outcomes)              │ ║  │
│  ║  │ recursos, plazos)            │ Alineamiento estratégico               │ ║  │
│  ║  └─────────────────────────────────────────────────────────────────────────┘ ║  │
│  ║                                                                               ║  │
│  ║  CICLO OPERACIONAL: SENSE → DECIDE → ACT                                     ║  │
│  ║  ┌──────────┐      ┌──────────┐      ┌──────────┐                           ║  │
│  ║  │  SENSE   │─────▶│  DECIDE  │─────▶│   ACT    │──┐                        ║  │
│  ║  │ Percibir │      │ Analizar │      │ Ejecutar │  │                        ║  │
│  ║  │ datos    │      │ priorizar│      │ transf.  │  │                        ║  │
│  ║  └──────────┘      └──────────┘      └──────────┘  │                        ║  │
│  ║       ▲                                            │                        ║  │
│  ║       └────────────────────────────────────────────┘ (feedback loop)        ║  │
│  ║                                                                               ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                      │
│  ╔═══════════════════════════════════════════════════════════════════════════════╗  │
│  ║                    MODELO HAIC: COLABORACIÓN HUMANO-IA                        ║  │
│  ╠═══════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                               ║  │
│  ║  NIVELES DE DELEGACIÓN (progresión gradual con evidencia)                    ║  │
│  ║  ┌─────────────────────────────────────────────────────────────────────────┐ ║  │
│  ║  │ M1 MONITOREAR │ Humano ejecuta, IA observa y aprende                    │ ║  │
│  ║  │ M2 ASISTIR    │ Humano ejecuta, IA sugiere opciones                     │ ║  │
│  ║  │ M3 HABILITAR  │ IA prepara, humano decide y ejecuta                     │ ║  │
│  ║  │ M4 CONTROLAR  │ IA ejecuta, humano aprueba cada acción                  │ ║  │
│  ║  │ M5 SUPERVISAR │ IA ejecuta, humano audita por excepción                 │ ║  │
│  ║  │ M6 EJECUTAR   │ IA autónoma, humano override disponible                 │ ║  │
│  ║  └─────────────────────────────────────────────────────────────────────────┘ ║  │
│  ║                                                                               ║  │
│  ║  INVARIANTE: ∀ Capacidad IA (nivel ≥ M2): ∃ Humano accountable              ║  │
│  ║  • Accountability humana obligatoria para decisiones algorítmicas           ║  │
│  ║  • Progresión M1→M6 solo con trajectory log y evidencia de desempeño        ║  │
│  ║  • Explainability requerida para niveles M3+                                ║  │
│  ║                                                                               ║  │
│  ╚═══════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    MÓDULO: NIVELES DE MADUREZ                                 │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │  L0 INICIAL      │ Procesos ad-hoc, sin estandarización                      │  │
│  │  L1 DIGITALIZADO │ Captura digital, repositorio único, trazabilidad          │  │
│  │  L2 INTEGRADO    │ Datos unificados, dashboards tiempo real                  │  │
│  │  L3 AUTOMATIZADO │ Alertas, validaciones, flujos automáticos                 │  │
│  │  L4 INTELIGENTE  │ Decisiones asistidas por IA (M2-M4)                       │  │
│  │  L5 AUTÓNOMO     │ Agentes IA operativos (M5-M6), optimización continua      │  │
│  │                                                                               │  │
│  │  GATE: Transformación estructural requiere H_org ≥ 70                        │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    MÓDULO: GOBIERNO DE DATOS                                  │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │  PILARES: Calidad • Seguridad (Ley 21.719) • Disponibilidad • Linaje        │  │
│  │  ├─ Catálogo de datasets con responsable (Data Steward)                      │  │
│  │  ├─ Diccionario de datos y trazabilidad de transformaciones                  │  │
│  │  ├─ Clasificación: Público / Interno / Confidencial / Sensible              │  │
│  │  └─ Calidad: Completitud, Exactitud, Actualidad, Consistencia               │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    MÓDULO: AUTOMATIZACIONES                                   │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │  TIPOS: Alertas • Validaciones • Cálculos • Notificaciones • Integraciones  │  │
│  │  ├─ Nivel cognitivo: C0 (mecánico), C1 (decisional), C2 (razonamiento)      │  │
│  │  ├─ Diseñador visual de flujos automatizados                                 │  │
│  │  ├─ Métricas: tiempo ahorrado, errores evitados, throughput                  │  │
│  │  └─ Trajectory log para progresión de autonomía                              │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    MÓDULO: AGENTES IA                                         │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │  → Ver Parte IV: Catálogo de Agentes Especializados                          │  │
│  │  ├─ Gobernanza: accountability humana, explainability, guardrails           │  │
│  │  ├─ Ciclo de vida: Deploy → Monitor → Evaluate → Promote/Demote             │  │
│  │  └─ Drift detection: Alerta si rendimiento degrada                           │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                    MÓDULO: ANALYTICS AVANZADO                                 │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │  NIVELES: Descriptivo → Diagnóstico → Predictivo → Prescriptivo             │  │
│  │  ├─ Proyección ejecución presupuestaria                                      │  │
│  │  ├─ Detección anomalías en rendiciones                                       │  │
│  │  ├─ Predicción mora por ejecutor                                             │  │
│  │  └─ Simulación de escenarios y optimización                                  │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Entidades de datos D-EVOL:**

*Framework de Evolución:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Capacidad` | id, nombre, sustrato (humano/algorítmico/mixto), nivel_cognitivo (C0-C3), rol, accountable_id | → Flujo[], Delegacion[] |
| `Flujo` | id, nombre, tipo (producción/habilitación), pasos[], nivel_cognitivo, proposito_id | → Capacidad[], Informacion[] |
| `Proposito` | id, objetivo, key_results[], owner_id, padre_id | → Flujo[], KeyResult[] |
| `Limite` | id, tipo (regulatorio/organizacional/técnico), expresion, enforcement | → Capacidad[], Flujo[] |
| `NivelMadurez` | id, proceso_id, nivel_actual (L0-L5), nivel_objetivo, fecha_evaluacion, gaps[] | → PlanEvolucion |

*Colaboración Humano-IA:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Delegacion` | id, capacidad_ia_id, humano_accountable_id, modo (M1-M6), fecha_inicio, evidencia | → Capacidad, Funcionario |
| `TrajectoryLog` | id, capacidad_id, timestamp, input, output, success, latency | → Capacidad |
| `DriftAlert` | id, capacidad_id, fecha, metrica_afectada, valor_esperado, valor_actual, severidad | → Capacidad |

*Gobierno de Datos:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Dataset` | id, nombre, descripcion, clasificacion, steward_id, frecuencia_actualizacion | → MetadatoDatos[], CertificacionCalidad[] |
| `MetadatoDatos` | id, dataset_id, campo, tipo, descripcion, sensibilidad, linaje | → Dataset |
| `Automatizacion` | id, nombre, tipo, nivel_cognitivo, trigger, estado, tiempo_ahorro | → LogEjecucion[], TrajectoryLog[] |

*Agentes IA:*

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Agente` | id, nombre, dominio, version, modo_delegacion, accountable_id, precision, estado | → InteraccionAgente[], TrajectoryLog[] |
| `InteraccionAgente` | id, agente_id, usuario_id, consulta, respuesta, rating, explicacion | → Agente, Funcionario |
| `ModeloML` | id, nombre, tipo, metricas, fecha_entrenamiento, drift_score | → Prediccion[], DriftAlert[] |

---

## Parte III: Síntesis y Roadmap

### 6. Arquitectura Consolidada

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              GORE_OS v2                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CAPA ESTRATÉGICA                                                               │
│  └── D-EVOL: Evolución Nativa (P1-P5, SDA, HAIC M1-M6, L0-L5)                   │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CAPA DE INTELIGENCIA                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │  BASE DE CONOCIMIENTO              │  AGENTES ESPECIALIZADOS               ││
│  │  ┌─────────────────────────────┐   │  ┌─────────────────────────────┐      ││
│  │  │ • Normativa vigente         │   │  │ • Analista de Ejecución     │      ││
│  │  │ • Procesos institucionales  │   │  │ • Monitor de Inversiones    │      ││
│  │  │ • Reglas de negocio         │   │  │ • Verificador de Cumplimiento│     ││
│  │  │ • Histórico de decisiones   │   │  │ • Asesor de Instrumentos    │      ││
│  │  │ • Mejores prácticas         │   │  │ • Generador de Reportes     │      ││
│  │  └─────────────────────────────┘   │  └─────────────────────────────┘      ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CAPA TRANSVERSAL                                                               │
│  └── D-GESTION: OKRs, H_gore, Playbooks, Mejora Continua                        │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  NÚCLEOS TÁCTICOS (Motor de Desarrollo)                                          │
│  ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────┐  │
│  │ FINANCIAR (D-FIN)       │ │ EJECUTAR (D-EJEC)       │ │ COORDINAR (D-COORD) │  │
│  ├─────────────────────────┤ ├─────────────────────────┤ ├─────────────────────┤  │
│  │ • Captación Oportunidades│ │ • Convenios             │ │ • Actores           │  │
│  │ • Capital Base          │ │ • PMO Regional          │ │ • Proveedores       │  │
│  │ • Portafolio IPR        │ │ • Estados de pago       │ │ • Ciudadanos        │  │
│  │ • Gestión Ejecutores    │ │ • Riesgos/Hitos         │ │ • Gabinete Regional │  │
│  │ • Evaluación Continua   │ │                         │ │                     │  │
│  │ • Retorno IDR          │ │                         │ │                     │  │
│  └─────────────────────────┘ └─────────────────────────┘ └─────────────────────┘  │
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

### 7. Integraciones Obligatorias

| Sistema | Función | Prioridad |
|---------|---------|-----------|
| **SIGFE** | Presupuesto, contabilidad | P0 |
| **BIP/SNI** | Proyectos inversión, RS | P0 |
| **SISREC** | Rendiciones CGR | P0 |
| **ClaveÚnica** | Autenticación | P0 |
| **DocDigital** | Expediente electrónico | P1 |
| **PISEE** | Interoperabilidad | P1 |
| **ChileCompra** | Adquisiciones | P2 |

---

### 8. Flujo de Datos Unificado

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         FLUJO DE DATOS GORE_OS                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  GESTIÓN DE RECURSOS ───────────────────────────────────────────────────────►   │
│  (D-BACK)                                                                        │
│  • Proporciona: datos financieros, contratos, dotación                          │
│  • Consume: alertas de ejecución, demandas de RRHH                              │
│                      │                                                           │
│                      ▼                                                           │
│  GESTIÓN DE INVERSIÓN ───────────────────────────────────────────────────────►  │
│  (D-FIN + D-EJEC)                                                               │
│  • Proporciona: compromisos presupuestarios, convenios, rendiciones             │
│  • Consume: recursos disponibles, capacidad institucional                       │
│                      │                                                           │
│                      ▼                                                           │
│  GESTIÓN RELACIONAL ─────────────────────────────────────────────────────────►  │
│  (D-COORD)                                                                       │
│  • Proporciona: ejecutores calificados, historial de desempeño                  │
│  • Consume: convenios a monitorear, alertas de mora                             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 9. Metas a 5 Años

| Indicador | Año 1 | Año 3 | Año 5 |
|-----------|-------|-------|-------|
| Procesos digitalizados | 30% | 70% | 95% |
| Automatizaciones activas | 5 | 25 | 50 |
| Agentes IA operativos | 1 | 8 | 15 |
| Índice H_gore | 60 | 80 | 90 |
| Trazabilidad total | 40% | 80% | 100% |

---

### 10. Beneficios de la Integración

| Dimensión | Sin GORE_OS | Con GORE_OS |
|-----------|-------------|-------------|
| **Visibilidad** | Fragmentada en Excel | 360° en tiempo real |
| **Trazabilidad** | Manual, incompleta | Automática, total |
| **Alertas** | Reactivas | Predictivas |
| **Decisiones** | Basadas en intuición | Basadas en datos |
| **Cumplimiento** | Verificación manual | Embebido en sistema |
| **Eficiencia** | Alta carga operativa | Automatización progresiva |

---

## Parte IV: Infraestructura de Conocimiento y Agentes

> **Nota:** Esta sección detalla la implementación de la **Capa de Inteligencia** de GORE_OS, que forma parte del dominio D-EVOL (ver sección 5.10). Aquí se especifican la Base de Conocimiento, los Agentes Especializados y su ciclo de vida.

### 11. Base de Conocimiento Institucional

GORE_OS incorpora una **base de conocimiento estructurada** que permite a los agentes y al sistema operar con contexto institucional completo.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      BASE DE CONOCIMIENTO GORE_OS                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │  CONOCIMIENTO NORMATIVO                                                     ││
│  │  • LOC GORE y reglamentos                                                   ││
│  │  • Ley de Presupuestos (vigente)                                            ││
│  │  • Circulares DIPRES y CGR                                                  ││
│  │  • Normativa TDE (decretos, guías)                                          ││
│  │  • Reglamentos regionales                                                   ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │  CONOCIMIENTO PROCEDIMENTAL                                                 ││
│  │  • Ciclo de vida de IPR (9 fases)                                           ││
│  │  • Proceso de rendiciones                                                   ││
│  │  • Selector de mecanismos de financiamiento                                 ││
│  │  • Flujos de convenios                                                      ││
│  │  • Procesos de contratación                                                 ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │  CONOCIMIENTO CONTEXTUAL                                                    ││
│  │  • Estructura organizacional GORE Ñuble                                     ││
│  │  • Mapa de actores regionales                                               ││
│  │  • Histórico de ejecución                                                   ││
│  │  • Patrones de mora por ejecutor                                            ││
│  │  • Mejores prácticas institucionales                                        ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Características de la Base de Conocimiento:**

| Característica | Descripción |
|----------------|-------------|
| **Estructurada** | Formato optimizado para consumo por agentes y búsqueda semántica |
| **Versionada** | Control de cambios con trazabilidad completa |
| **Federada** | Puede integrar conocimiento de otros repositorios institucionales |
| **Actualizable** | Ciclo de vida con curación, validación y publicación |

---

### 12. Catálogo de Agentes Especializados

Los agentes son asistentes inteligentes que operan sobre la base de conocimiento para amplificar la capacidad de los funcionarios.

| Agente | Dominio | Función Principal | Interacción |
|--------|---------|-------------------|-------------|
| **Analista de Ejecución** | D-FIN | Monitorea ejecución presupuestaria, proyecta cierre, identifica riesgos | Alertas proactivas, dashboards |
| **Monitor de Inversiones** | D-FIN + D-EJEC | Seguimiento de cartera IPR, alertas de estancamiento | Notificaciones, reportes |
| **Verificador de Cumplimiento** | D-NORM | Valida cumplimiento normativo en actos, procedimientos y documentos | Checklist automático |
| **Asesor de Mecanismos** | D-FIN | Recomienda mecanismo de financiamiento apropiado según características del proyecto | Chat interactivo |
| **Generador de Reportes** | Transversal | Produce informes para CORE, CGR, DIPRES en formatos requeridos | Generación automática |
| **Asistente Documental** | D-NORM | Ayuda en redacción de actos administrativos, resoluciones, convenios | Plantillas SFD/STS |

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         FLUJO DE AGENTES                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   FUNCIONARIO ────► SOLICITUD ────► AGENTE ────► BASE DE ────► RESPUESTA       │
│                                        │       CONOCIMIENTO                     │
│                                        │                                         │
│                                        ▼                                         │
│                                   ┌─────────┐                                    │
│                                   │ REGLAS  │                                    │
│                                   │ DE      │                                    │
│                                   │ NEGOCIO │                                    │
│                                   └─────────┘                                    │
│                                                                                  │
│   Ejemplo: "¿Qué mecanismo uso para un proyecto de $50M en agua potable?"       │
│                                                                                  │
│   → Asesor de Mecanismos consulta KB de mecanismos                              │
│   → Evalúa: monto, tipo proyecto, ejecutor, disponibilidad                      │
│   → Responde: "IDI General vía SNI con RS. Requisitos: Perfil, EIA, terreno."   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 13. Ciclo de Vida de Conocimiento y Agentes

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    CICLO DE VIDA: CONOCIMIENTO Y AGENTES                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  CONOCIMIENTO                                                                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│  │ CAPTURA  │──►│ CURACIÓN │──►│VALIDACIÓN│──►│PUBLICACIÓN──►│EVOLUCIÓN │      │
│  │          │   │          │   │          │   │          │   │          │      │
│  │ Fuentes  │   │ Estructura│  │ Revisión │   │ Catálogo │   │ Feedback │      │
│  │ oficiales│   │ semántica │  │ experta  │   │ federado │   │ uso real │      │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘      │
│                                                                                  │
│  AGENTES                                                                        │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│  │CONCEPCIÓN│──►│DESARROLLO│──►│ TESTING  │──►│DESPLIEGUE│──►│MONITOREO │      │
│  │          │   │          │   │          │   │          │   │          │      │
│  │ Necesidad│   │ KB + Reglas│ │ Casos uso│   │ Producción   │ Métricas │      │
│  │ funcional│   │ + Flujos │   │ adversar.│   │          │   │ + Ajustes│      │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 14. Gobernanza de Conocimiento

| Rol | Responsabilidad |
|-----|-----------------|
| **Curador de Dominio** | Mantiene actualizada la KB de su área (ej: DIPIR para IPR) |
| **Validador Normativo** | Revisa consistencia con normativa vigente |
| **Administrador de Agentes** | Monitorea desempeño, ajusta comportamiento |
| **Comité de Conocimiento** | Define prioridades, resuelve conflictos, aprueba publicaciones |

**Métricas de Salud:**

| Métrica | Descripción | Meta |
|---------|-------------|------|
| **Cobertura KB** | % de procesos documentados en base de conocimiento | >90% |
| **Frescura** | Tiempo promedio desde actualización normativa hasta KB | <30 días |
| **Precisión Agentes** | % de respuestas correctas validadas | >95% |
| **Adopción** | % de funcionarios que usan agentes regularmente | >70% |

---

## Parte V: Resumen y Próximos Pasos

### 15. Índice de Dominios GORE_OS

| # | Dominio | Código | Capa | Propósito | Módulos |
|---|---------|--------|------|-----------|---------|
| 5.1 | Planificación Estratégica | D-PLAN | Habilitante | Instrumentos de planificación regional | ERD, PROT, ARI, Int. Territorial (→D-TERR) |
| 5.2 | Financiamiento | D-FIN | Núcleo | Gestión integral 360° inversión pública | Captación Oportunidades, Capital Base, Portafolio IPR, Gestión Ejecutores, Evaluación Continua, IPR Problemáticas, Retorno IDR |
| 5.3 | Ejecución | D-EJEC | Núcleo | Materialización de iniciativas | Convenios, PMO Regional |
| 5.4 | Coordinación | D-COORD | Núcleo | Relaciones territoriales y gobernanza | Actores, Proveedores, Ciudadanos, Gabinete |
| 5.5 | Gestión Jurídico-Administrativa | D-NORM | Habilitante | Actos, procedimientos, cumplimiento, expedientes | Actos Administrativos, Procedimientos, Expediente Electrónico, Cumplimiento, Convenios, Reglamentos, Biblioteca |
| 5.6 | Gestión de Recursos | D-BACK | Habilitante | Recursos institucionales (función ADMINISTRAR) | Finanzas/Tesorería, RRHH, Compras, Inventarios, Activo Fijo, Flota, Servicios Generales |
| 5.7 | Gobernanza Digital | D-TDE | Habilitante | TDE Regional: modernización + ciberseguridad | CPAT, Interoperabilidad, Ciberseguridad, Gobernanza Regional, Madurez TDE |
| 5.8 | Inteligencia Territorial | D-TERR | Habilitante | Información geoespacial e indicadores | IDE, Observatorio, Visor GIS |
| 5.9 | Gestión Institucional Transversal | D-GESTION | Transversal | Desempeño y mejora continua | OKRs, H_gore, Playbooks, Mejora Continua |
| 5.10 | Evolución e Inteligencia | D-EVOL | Estratégica | Evolución nativa: framework ORKO, HAIC | Primitivos P1-P5, Ciclo SDA, HAIC M1-M6, Madurez L0-L5, Gobierno Datos, Agentes IA |

---

### 16. Dependencias Críticas

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DEPENDENCIAS PARA IMPLEMENTACIÓN                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  FASE 0: FUNDAMENTOS (prerequisitos)                                            │
│  ├── Infraestructura cloud/on-premise definida                                  │
│  ├── Modelo de autenticación (ClaveÚnica)                                       │
│  ├── Base de conocimiento inicial poblada                                       │
│  └── Equipo técnico conformado                                                  │
│                                                                                  │
│  FASE 1: NÚCLEO (MVP)                                                           │
│  ├── D-FIN: Portafolio IPR + Presupuesto básico                                 │
│  ├── D-COORD: Gestión de ejecutores                                             │
│  ├── Integración SIGFE (lectura)                                                │
│  └── Agente: Monitor de Inversiones (v1)                                        │
│                                                                                  │
│  FASE 2: EXPANSIÓN                                                              │
│  ├── D-EJEC: Convenios + Rendiciones                                            │
│  ├── D-NORM: Actos administrativos + Expediente electrónico                     │
│  ├── Integración BIP/SNI, SISREC                                                │
│  └── Agentes: Analista de Ejecución, Verificador                                │
│                                                                                  │
│  FASE 3: MADUREZ                                                                │
│  ├── D-PLAN: ERD, PROT, ARI completos                                           │
│  ├── D-TDE: Cumplimiento y CPAT                                                 │
│  ├── D-TERR: Observatorio + Visor GIS                                           │
│  └── Suite completa de agentes                                                  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### 17. Próximos Pasos

| Paso | Descripción | Artefacto Esperado |
|------|-------------|-------------------|
| **1** | Detallar integraciones con sistemas externos | Documento de integraciones |
| **2** | Definir arquitectura técnica (stack, capas, APIs) | Documento de arquitectura |
| **3** | Especificar modelo de datos unificado | Diagrama ER consolidado |
| **4** | Diseñar MVP (alcance Fase 1) | Backlog priorizado |
| **5** | Validar con stakeholders GORE | Acta de validación |

---

*Documento generado como parte del proceso de diseño de GORE_OS.*
*Versión: 3.0 | Fecha: Diciembre 2024*
*Última revisión: 15-12-2024 | Cambios: Modelo Motor+Soporte (6 funciones: PLANIFICAR, FINANCIAR, EJECUTAR, COORDINAR, NORMAR, ADMINISTRAR); D-BACK y D-NORM como capas habilitantes; D-TDE renombrado a Gobernanza Digital; coherencia semántica integral*
