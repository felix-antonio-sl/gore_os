# D-PLAN: Dominio de Planificación Estratégica

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Habilitante (Dimensión Estratégica)  
> **Función GORE:** PLANIFICAR  

---

## Propósito

Gestionar los instrumentos de planificación regional y su conexión con la ejecución.

---

## Diagrama de Dominio

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
│   │       └── Eje Estratégico (4-6) - incluye Eje Seguridad Pública            │   │
│   │           └── Lineamiento (2-4 por eje)                                    │   │
│   │               └── Objetivo Estratégico (1-3 por lineamiento)               │   │
│   │                   └── Indicador + Meta (1-n por objetivo)                  │   │
│   │                       └── Iniciativa vinculada (IPR, Programa)             │   │
│   │                                                                             │   │
│   │   FUNCIONALIDADES                                                           │   │
│   │   • Árbol navegable de ERD                                                  │   │
│   │   • Vinculación IPR → Objetivo ERD (obligatorio, incluye Proyecto_Seguridad)│  │
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

---

## Entidades de Datos

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `ERD` | id, nombre, periodo_inicio, periodo_fin, estado | → EjeEstrategico[] |
| `EjeEstrategico` | id, erd_id, codigo, nombre, descripcion | → Lineamiento[], PoliticaRegionalSeguridad |
| `Lineamiento` | id, eje_id, codigo, nombre | → ObjetivoEstrategico[] |
| `ObjetivoEstrategico` | id, lineamiento_id, codigo, nombre, descripcion | → Indicador[], IPR[] |
| `IndicadorERD` | id, objetivo_id, nombre, formula, linea_base, meta, año_meta | → MedicionIndicador[] |
| `ARI` | id, año, estado, fecha_presentacion | → LineaARI[] |
| `LineaARI` | id, ari_id, ipr_id, prioridad, monto_solicitado, monto_asignado | → IPR |

---

## Referencias Cruzadas

| Dominio | Relación |
|---------|----------|
| **D-TERR** | ZonaPROT se define en D-TERR como parte de la IDE |
| **D-FIN** | IPR vinculadas a objetivos ERD (incluye Proyecto_Seguridad) |
| **D-EJEC** | IPR priorizadas en ARI se ejecutan vía convenios |
| **D-COORD** | Compromisos de Gobernador vinculados a objetivos ERD |
| **D-NORM** | Reglamentos regionales vinculados con ERD |
| **D-BACK** | Plan de Compras (PAC) alineado con ARI |
| **D-GESTION** | OKRs institucionales alineados con ERD |
| **D-EVOL** | Proyección de cumplimiento ERD |
| **D-SEG** | Política Regional de Seguridad → Eje Seguridad en ERD |
| **D-GINT (FÉNIX)** | Objetivos ERD sin avance >180 días activan intervención Nivel III |

---

*Documento parte de GORE_OS v4.1*
