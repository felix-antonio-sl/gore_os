# User Stories GORE OS

> **FUENTE DE VERDAD UNIFICADA**: Este documento es una vista de alto nivel. La fuente canónica de verdad para todas las User Stories, Criterios de Aceptación y Prioridades es el **Catálogo Unificado KODA**.
>
> 📄 **Catálogo Maestro**: [`kb_goreos_200_user_stories_catalog_koda.yml`](../../goreos/01_especificaciones/kb_goreos_200_user_stories_catalog_koda.yml)

## Resumen Ejecutivo

El sistema GORE OS unifica **~1,200+** requisitos originales en un catálogo consolidado de **~115 User Stories de alto nivel** (Epic/Feature level) que cubren 9 dominios críticos.

### Dominios del Sistema

| Módulo  | Nombre | Descripción |                    User Stories                     |
| :-----: | ------ | ----------- | :-------------------------------------------------: |
| **M01** | **PRO  | IPR**       |    Inversión Pública Regional (BIP, CORE, DIPIR)    | 25 |
| **M02** | **PRO  | REN**       |        Rendiciones de Cuentas (SISREC, DAF)         | 12 |
| **M03** | **ADM  | FIN**       |       Gestión Financiera (Presupuesto, SIGFE)       | 13 |
| **M04** | **ADM  | ADQ**       |     Abastecimiento y Activos (Compras, Bodega)      | 13 |
| **M05** | **ADM  | PER**       | Gestión de Personas (Ciclo de Vida, Remuneraciones) | 14 |
| **M06** | **TEC  | TDE**       |    Transformación Digital (Expediente, Interop)     | 8  |
| **M07** | **GOB  | GOB**       |       Gobernanza (CORE, Gobernador, Gabinete)       | 7  |
| **M08** | **GOB  | SEG**       |        Seguridad Ciudadana (CIES, Proyectos)        | 4  |
| **M09** | **GOB  | JUR**       |     Jurídico y Transparencia (Actos, Litigios)      | 5  |

**Total Unificado:** ~101 User Stories Core

---

## Estructura de Identificación

Cada User Story posee un identificador único semántico que reemplaza a los antiguos IDs (`US_FIN_*`, `FE-IPR-*`, etc.).

Formato: `[MODULO]-[SUBDOMINIO]-[SECUENCIA]`

Ejemplos:
*   `IPR-ADM-001`: Inversión Pública - Admisibilidad - 001
*   `PER-REM-001`: Personas - Remuneraciones - 001
*   `SEG-OPS-001`: Seguridad - Operaciones - 001

## Trazabilidad

El catálogo KODA mantiene un índice de trazabilidad (`legacy_ids`) que permite vincular cada nueva User Story con sus requisitos originales en los documentos antiguos.

*Para consultar el detalle de Criterios de Aceptación, Actores y Beneficios, refiérase directamente al archivo YAML del catálogo.*
