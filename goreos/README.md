# GORE_OS - Base de Conocimiento KODA

**Sistema Operativo del GORE Ñuble** - Digital twin para gestión integral de inversión pública regional.

## 📊 Resumen

| Métrica            | Valor        |
| ------------------ | ------------ |
| Artefactos KODA    | 31           |
| Dominios cubiertos | 10/10 (100%) |
| Entidades de datos | 66           |
| Casos de uso       | 108          |
| Procesos BPMN      | 14           |
| Roles RBAC         | 15           |
| Integraciones      | 8            |

## 📁 Estructura de Directorios

```
goreos/
├── 00_fundacional/        # Visión, Arquitectura, Glosario
├── 01_especificaciones/   # Especificaciones funcionales (10 dominios)
├── 02_modelo_datos/       # Modelo conceptual y lógico (66 entidades)
├── 03_procesos/           # Catálogo BPMN (14 procesos)
├── 04_seguridad/          # Roles y permisos RBAC (15 roles)
├── 05_integraciones/      # APIs externas (8 integraciones)
├── 06_diseno_ui/          # Wireframes (5 diseños)
├── 07_migracion/          # Plan ETL y mapeos
├── 08_roadmap/            # Roadmap implementación (6 fases)
├── 09_testing/            # Estrategia QA
├── artifacts/             # Código generado (Prisma)
├── README.md              # Este archivo
└── kb_goreos_999_catalogo_maestro_koda.yml  # Índice central
```

## 📋 Catálogo de Artefactos

### 00_fundacional/
| ID      | Archivo                                       | Descripción                 |
| ------- | --------------------------------------------- | --------------------------- |
| GOS-000 | `kb_goreos_000_vision_estrategica_koda.yml`   | Visión, principios, roadmap |
| GOS-001 | `kb_goreos_001_arquitectura_general_koda.yml` | Arquitectura 10 dominios    |
| GOS-005 | `kb_goreos_005_glosario_goreos_koda.yml`      | Términos, acrónimos, enums  |

### 01_especificaciones/
| ID      | Archivo                                           | Dominio                 | Casos Uso |
| ------- | ------------------------------------------------- | ----------------------- | --------- |
| GOS-101 | `kb_goreos_101_especificacion_d_plan_koda.yml`    | Planificación           | 10        |
| GOS-102 | `kb_goreos_102_especificacion_d_fin_koda.yml`     | Financiamiento          | 15        |
| GOS-103 | `kb_goreos_103_especificacion_d_ejec_koda.yml`    | Ejecución               | 12        |
| GOS-104 | `kb_goreos_104_especificacion_d_coord_koda.yml`   | Coordinación            | 9         |
| GOS-105 | `kb_goreos_105_especificacion_d_norm_koda.yml`    | Normativo               | 11        |
| GOS-106 | `kb_goreos_106_especificacion_d_back_koda.yml`    | Back-Office             | 14        |
| GOS-107 | `kb_goreos_107_especificacion_d_tde_koda.yml`     | Transformación Digital  | 12        |
| GOS-108 | `kb_goreos_108_especificacion_d_terr_koda.yml`    | Territorio              | 11        |
| GOS-110 | `kb_goreos_110_especificacion_d_gestion_koda.yml` | Gestión Institucional   | 8         |
| GOS-111 | `kb_goreos_111_especificacion_d_evol_koda.yml`    | Evolución Institucional | 6         |

### 02_modelo_datos/
| ID       | Archivo                                         | Contenido                  |
| -------- | ----------------------------------------------- | -------------------------- |
| GOS-200  | `kb_goreos_200_modelo_datos_esqueleto_koda.yml` | Índice 66 entidades        |
| GOS-200a | `kb_goreos_200a_entidades_maestras_koda.yml`    | Usuario, Actor, Territorio |
| GOS-200b | `kb_goreos_200b_dominio_plan_koda.yml`          | ERD, PROT, CP              |
| GOS-200c | `kb_goreos_200c_dominio_fin_koda.yml`           | Iniciativa, Solicitud      |
| GOS-200d | `kb_goreos_200d_dominio_ejec_koda.yml`          | Convenio, Rendición        |
| GOS-200e | `kb_goreos_200e_dominio_coord_norm_koda.yml`    | Compromisos, Reglamentos   |
| GOS-200f | `kb_goreos_200f_dominio_back_tde_koda.yml`      | Documentos, Expediente     |
| GOS-200g | `kb_goreos_200g_dominio_terr_gestion_koda.yml`  | Capas, OKR, Alertas        |
| GOS-200h | `kb_goreos_200h_dominio_evol_koda.yml`          | Dataset, Agentes AI        |
| GOS-201  | `kb_goreos_201_modelo_logico_prisma_koda.yml`   | Schema Prisma              |

### 03_procesos/ a 09_testing/
| Dir                 | ID      | Contenido                 |
| ------------------- | ------- | ------------------------- |
| `03_procesos/`      | GOS-300 | 14 procesos BPMN          |
| `04_seguridad/`     | GOS-400 | 15 roles RBAC             |
| `05_integraciones/` | GOS-500 | BIP, SIGFE, SII, etc.     |
| `06_diseno_ui/`     | GOS-600 | 5 wireframes              |
| `07_migracion/`     | GOS-700 | ETL, mapeos, validaciones |
| `08_roadmap/`       | GOS-800 | 6 fases, 18-24 meses      |
| `09_testing/`       | GOS-900 | Pirámide, E2E, CI/CD      |

### Índice Central
| ID      | Archivo                                   | Descripción                             |
| ------- | ----------------------------------------- | --------------------------------------- |
| GOS-999 | `kb_goreos_999_catalogo_maestro_koda.yml` | **Catálogo maestro** - Punto de entrada |

## 🏛️ Arquitectura de Dominios

```
┌─────────────────────────────────────────────────────────────────┐
│                         GORE_OS                                 │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────────┤
│ D-PLAN  │ D-FIN   │ D-EJEC  │ D-COORD │ D-NORM  │ Funcionales │
├─────────┼─────────┼─────────┼─────────┼─────────┤             │
│ D-BACK  │ D-TDE   │ D-TERR  │         │         │ Habilitantes│
├─────────┼─────────┼─────────┴─────────┴─────────┤             │
│ D-GESTION         │ D-EVOL                      │ Estratégicos│
└───────────────────┴─────────────────────────────┴─────────────┘
```

## 🚀 Roadmap de Implementación

| Fase | Período           | Alcance                                   |
| ---- | ----------------- | ----------------------------------------- |
| 0    | Ene-Feb 2025      | Preparación, infraestructura              |
| 1    | Mar-Jun 2025      | MVP Core (IPR, Solicitudes, Convenios)    |
| 2    | Jul-Oct 2025      | Ejecución (Desembolsos, Rendiciones, PMO) |
| 3    | Nov 2025-Ene 2026 | Planificación (ERD, OKRs, H_gore)         |
| 4    | Feb-May 2026      | Evolución (Lakehouse, AI)                 |
| 5    | Jun-Ago 2026      | Consolidación                             |

## 📚 Cómo Usar

1. **Punto de entrada**: Comenzar por `kb_goreos_999_catalogo_maestro_koda.yml`
2. **Entender la visión**: Leer `kb_goreos_000_vision_estrategica_koda.yml`
3. **Explorar arquitectura**: Ver `kb_goreos_001_arquitectura_general_koda.yml`
4. **Consultar modelo de datos**: Partir de `kb_goreos_200_modelo_datos_esqueleto_koda.yml`
5. **Ver especificación de dominio**: Buscar `kb_goreos_10X_especificacion_d_*.yml`

## 🔗 Referencias

- **KODA Spec**: `urn:knowledge:koda:core:spec:1.0.0`
- **ORKO Framework**: Para metodología y playbooks
- **TDE Lineamientos**: Para compliance DS-10, DS-12, Ley 21.719

---
*Generado: 2024-12-14 | Versión: 1.0.0*
