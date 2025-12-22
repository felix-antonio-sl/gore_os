# D-FIN: Dominio de Financiamiento e Inversión Pública

> Parte de: [GORE_OS Vision General](../vision_general.md)  
> Capa: Núcleo (Dimensión Táctica)  
> Función GORE: FINANCIAR  

---

## Propósito

Gestión integral 360° del ciclo de vida de las inversiones públicas regionales:

1. **Captación de Oportunidades** - Identificar y priorizar necesidades
2. **Gestión de Capital** - Maximizar retorno en desarrollo regional
3. **Gestión de Ejecutores** - Administrar relaciones y capacidades
4. **Evaluación Continua** - Asegurar calidad y resultados

> Visión: El GORE opera como gestor integral del desarrollo regional: capta oportunidades, administra capital público para generar retorno, cultiva relaciones con ejecutores, y evalúa continuamente impacto.

---

## ⚠️ Restricciones Arquitectónicas

### Triángulo de Integración Presupuestaria

```text
        D-FIN (Financiamiento)
             ↕ CDP, % Ejecución
     ┌───────────────────────┐
     ↓                       ↓
D-EJEC (Ejecución Física)  D-BACK (Ejecución Presupuestaria)
     └───────EP validado────→┘
```

### Flujos Bidireccionales Pago-Rendición

| Patrón | Instrumento       | Flujo                  |
| ------ | ----------------- | ---------------------- |
| **A**  | IDI, Obras FRIL   | Ejecuta → EP → Paga    |
| **B**  | PPR, S8%, Transf. | Paga → Ejecuta → Rinde |

---

## Subdominios

| Subdominio      | Contenido                                            | Enlace                                                   |
| --------------- | ---------------------------------------------------- | -------------------------------------------------------- |
| **Core IPR**    | Taxonomía, Ciclo de vida (Fases 1-7), Procesos P1-P7 | [sub_dfin_ipr_core.md](d-fin/sub_dfin_ipr_core.md)       |
| **Mecanismos**  | Selector, Árbol de decisión, Guías KODA              | [sub_dfin_mecanismos.md](d-fin/sub_dfin_mecanismos.md)   |
| **Presupuesto** | Ciclo anual, Glosas, Cadena SIGFE                    | [sub_dfin_presupuesto.md](d-fin/sub_dfin_presupuesto.md) |
| **Rendiciones** | SISREC, Mora, Res. 30 CGR                            | [sub_dfin_rendiciones.md](d-fin/sub_dfin_rendiciones.md) |
| **Portafolio**  | Banca Inversión, PuntajeImpacto, Alertas 360°        | [sub_dfin_portafolio.md](d-fin/sub_dfin_portafolio.md)   |
| **Ejecutores**  | Calificación, Mesa de Ayuda, Inducción               | [sub_dfin_ejecutores.md](d-fin/sub_dfin_ejecutores.md)   |


---

## Glosario y Entidades Core

**(Ver detalle en subdominios)**

| Entidad Core     | Descripción                                                            | Subdominio                                   |
| :--------------- | :--------------------------------------------------------------------- | :------------------------------------------- |
| **`IPR`**        | Intervención Pública Regional (Abstracta). Padre de IDI y PPR.         | [Core IPR](d-fin/sub_dfin_ipr_core.md)       |
| **`IDI`**        | Iniciativa de Inversión (Gasto Capital). SNI, FRIL, C33.               | [Core IPR](d-fin/sub_dfin_ipr_core.md)       |
| **`PPR`**        | Programa Público Regional (Gasto Corriente). Glosa 06, Transferencias. | [Core IPR](d-fin/sub_dfin_ipr_core.md)       |
| **`Mecanismo`**  | Catálogo de financiamiento (SNI, FRIL, FRPD, etc.)                     | [Mecanismos](d-fin/sub_dfin_mecanismos.md)   |
| **`CDP`**        | Certificado Disponibilidad Presupuestaria. Inicio cadena.              | [Presupuesto](d-fin/sub_dfin_presupuesto.md) |
| **`EstadoPago`** | Rendición parcial de obras. Habilita devengo.                          | [Rendiciones](d-fin/sub_dfin_rendiciones.md) |
| **`Convenio`**   | Formalización legal GORE-Ejecutor.                                     | [Core IPR](d-fin/sub_dfin_ipr_core.md)       |

---

## Módulos Funcionales

| #   | Módulo                     | Función                                 | Subdominio  |
| --- | -------------------------- | --------------------------------------- | ----------- |
| M1  | Captación de Oportunidades | Embudo de detecting → converted         | Portafolio  |
| M2  | Capital Base               | Fuentes de financiamiento FNDR/FRPD/etc | Presupuesto |
| M3  | Portafolio IPR             | Taxonomía, ciclo de vida                | Core IPR    |
| M4  | Selector de Mecanismos     | Árbol de decisión, guías KODA           | Mecanismos  |
| M5  | Presupuesto Regional       | Ciclo anual, glosas, SIGFE              | Presupuesto |
| M6  | Rendiciones                | SISREC, mora, Res. 30                   | Rendiciones |
| M7  | Gestión de Ejecutores      | Calificación A/B/C/D                    | Ejecutores  |
| M8  | Mesa de Ayuda              | Soporte, capacitación                   | Ejecutores  |
| M9  | Portafolio Estratégico     | Banca Inversión, PuntajeImpacto         | Portafolio  |
| M10 | Alertas 360°               | SaludIPR, alertas por fase              | Portafolio  |

---

## Procesos BPMN

| Proceso | Nombre                       | Subdominio                                                                    |
| ------- | ---------------------------- | ----------------------------------------------------------------------------- |
| P0      | Selector de Vías             | [Mecanismos](d-fin/sub_dfin_mecanismos.md)                                    |
| P1      | Ingreso y Admisibilidad      | [Core IPR](d-fin/sub_dfin_ipr_core.md#p1-ingreso-pertinencia-y-admisibilidad) |
| P2      | Evaluación Técnico-Económica | [Core IPR](d-fin/sub_dfin_ipr_core.md#p2-evaluación-técnico-económica)        |
| P3      | Financiamiento               | [Core IPR](d-fin/sub_dfin_ipr_core.md#p3-obtención-de-financiamiento)         |
| P4      | Formalización                | [Core IPR](d-fin/sub_dfin_ipr_core.md#p4-formalización)                       |
| P5      | Ejecución                    | [Core IPR](d-fin/sub_dfin_ipr_core.md#p5-ejecución-y-supervisión)             |
| P6      | Modificaciones               | [Core IPR](d-fin/sub_dfin_ipr_core.md#p6-modificaciones-en-ejecución)         |
| P7      | Cierre                       | [Core IPR](d-fin/sub_dfin_ipr_core.md#p7-cierre-técnico-financiero)           |
| P8      | Asistencia Financiera        | [Ejecutores](d-fin/sub_dfin_ejecutores.md#p8-asistencia-financiera)           |

---

## Guías KODA Relacionadas

| Mecanismo  | Guía                                                                                                                              | URN                                                                  |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| IDI/SNI    | [kb_gn_024](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/ipr/kb_gn_024_guia_idi_sni_koda.yml)             | `urn:knowledge:gorenuble:gn:guia-idi-sni-sts:1.0.0`                  |
| FRIL       | [kb_gn_026](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/ipr/kb_gn_026_guia_fril_koda.yml)                | `urn:knowledge:gorenuble:gn:guia-fril-2025-sts:1.0.0`                |
| FRPD       | [kb_gn_027](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/ipr/kb_gn_027_guia_frpd_koda.yml)                | `urn:knowledge:gorenuble:gn:guia-frpd-nuble:1.0.0`                   |
| C33        | [kb_gn_029](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/ipr/kb_gn_029_guia_circ33_koda.yml)              | `urn:knowledge:gorenuble:gn:guia-circular-33-sts:1.0.0`              |
| PPR-G06    | [kb_gn_025](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/ipr/kb_gn_025_guia_programas_koda.yml)           | `urn:knowledge:gorenuble:gn:guia-programas-directos-gore:1.0.0`      |
| PPR-TRANSF | [kb_gn_001](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/ipr/kb_gn_001_transferencia_ppr_koda.yml)        | `urn:knowledge:gorenuble:gn:transferencia-ppr:1.0.0`                 |
| S8%        | [kb_gn_028](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/ipr/kb_gn_028_instructivo_subvencion_8_koda.yml) | `urn:knowledge:gorenuble:gn:instructivo-subvencion-8-2025-sts:1.0.0` |

---

## KPIs del Dominio

| Indicador                   | Meta     | Responsable |
| --------------------------- | -------- | ----------- |
| Tasa conversión IPR         | ≥25%     | DIPIR       |
| Tiempo ciclo admisibilidad  | ≤45 días | DIPIR       |
| Ejecución presupuestaria    | ≥90%     | DAF         |
| Mora rendiciones            | ≤5%      | UCR         |
| Calificación ejecutores A/B | ≥70%     | DIPIR       |
| PuntajeImpacto promedio     | ≥70      | DIPIR       |

---

## Sistemas Involucrados

| Sistema            | Fases           | Integración     |
| ------------------ | --------------- | --------------- |
| SYS-BIP-SNI        | P1, P2, P5, P7  | API consulta RS |
| SYS-SIGFE          | P3, P4, P5, P7  | DS12 - PISEE    |
| SYS-SISREC         | P7, Rendiciones | API CGR         |
| SYS-MERCADOPUBLICO | P5              | Licitaciones    |

---

## Referencias Cruzadas

| Dominio | Relación                         | Entidades                  |
| ------- | -------------------------------- | -------------------------- |
| D-PLAN  | IPR vinculadas a ERD             | ObjetivoERD, Brecha        |
| D-EJEC  | EP validado → D-BACK             | Convenio, Hito, EstadoPago |
| D-BACK  | Cadena contable, % ejecución     | CDP, Compromiso, Devengo   |
| D-GOB   | Actor (ejecutores)               | Actor, Proyecto_Seguridad  |
| D-NORM  | Convenio SSOT                    | ActoAdministrativo         |
| D-TERR  | Localización IPR                 | Ubicacion, Territorio      |
| FÉNIX   | IPR problemáticas → Intervención | Alerta, Intervencion       |

---

## Roles Asociados (SSOT: inventario_roles_v8.yml)

| Role Key                | Título                  | Unidad | Subdominio  |
| ----------------------- | ----------------------- | ------ | ----------- |
| jefe_dipir              | Jefe DIPIR              | DIPIR  | Core IPR    |
| jefe_presupuesto        | Jefe Depto. Presupuesto | DIPIR  | Presupuesto |
| jefe_inversion          | Jefe Depto. Inversión   | DIPIR  | Core IPR    |
| analista_inversion      | Analista de Inversión   | DIPIR  | Core IPR    |
| analista_presupuestario | Analista Presupuestario | DIPIR  | Presupuesto |
| analista_seguimiento    | Analista Seguimiento    | DIPIR  | Portafolio  |
| encargado_rendiciones   | Encargado Rendiciones   | DAF    | Rendiciones |
| coordinador_ucr         | Coordinador UCR         | DAF    | Rendiciones |
| entidad_ejecutora       | Entidad Ejecutora       | Ext.   | Ejecutores  |
| ejecutor_ppr            | Ejecutor PPR            | Ext.   | Ejecutores  |

> Ver inventario completo: [inventario_roles_v8.yml](inventario_roles_v8.yml)

---

## Historias de Usuario (SSOT: historias_usuarios_v2.yml)

### Capability Bundles D-FIN

| Bundle           | Descripción                           | Prioridad | Subdominio  |
| ---------------- | ------------------------------------- | --------- | ----------- |
| CAP-FIN-DASH-001 | Dashboard de Ejecución Presupuestaria | P0        | Presupuesto |
| CAP-FIN-REND-001 | Módulo de Rendiciones                 | P0        | Rendiciones |

### Distribución de Historias Atómicas

| Subdominio  | Historias | Enlace                                                   |
| ----------- | --------- | -------------------------------------------------------- |
| Presupuesto | 3         | [sub_dfin_presupuesto.md](d-fin/sub_dfin_presupuesto.md) |
| Rendiciones | 2         | [sub_dfin_rendiciones.md](d-fin/sub_dfin_rendiciones.md) |
| Ejecutores  | 2         | [sub_dfin_ejecutores.md](d-fin/sub_dfin_ejecutores.md)   |

> **Nota**: Las historias operativas (Tesorería, Compras) fueron reclasificadas a D-BACK según campo `target_domain` del SSOT.

> Ver catálogo completo: [historias_usuarios_v2.yml](historias_usuarios_v2.yml)

---

## Catálogo Completo de Historias (SSOT)

> Fuente: `historias_usuarios_v2.yml` | Filtro: `target_domain: D-FIN`  
> Total: 30 historias

| ID                 | Role                 | Descripción                                           | P   |
| ------------------ | -------------------- | ----------------------------------------------------- | --- |
| CAP-FIN-DASH-001   | Gobernador Regional  | un dashboard ejecutivo con KPIs de ejecución FNDR,... | P0  |
| CAP-FIN-REND-001   | Encargado de Rendici | alertas automáticas de rendiciones pendientes por ... | P0  |
| US-ABOG-DAF-001-01 | abogado_daf          | plantillas de bases y contratos con cláusulas actu... | P1  |
| US-ANALPRES-001-01 | analista_presupuesta | un módulo de emisión de CDP con validación automát... | P0  |
| US-ANALPRES-001-02 | analista_presupuesta | alertas de marcos presupuestarios próximos a agota... | P0  |
| US-APRES-001-01    | analista_presupuesto | un módulo de modificaciones presupuestarias...        | P0  |
| US-ATES-001-01     | analista_tesoreria   | un módulo de emisión de pagos con validación presu... | P0  |
| US-ATRANS-001-01   | analista_transferenc | un módulo de control de convenios de transferencia... | P0  |
| US-AUCR-001-01     | unidad_control_rendi | visores de documentos digitalizados con OCR...        | P0  |
| US-BOD-001-01      | encargado_bodega     | un módulo de control de stock con entradas y salid... | P1  |
| US-CGR-CONT-001-01 | contraparte_contable | acceso a reportes contables en formato estándar...    | P0  |
| US-CIU-001-02      | ciudadano            | consultar en qué se gasta el presupuesto regional...  | P1  |
| US-COM-EV-001-01   | miembro_comision_eva | acceso a ofertas y matriz de evaluación en platafo... | P0  |
| US-CONT-001-01     | analista_contable    | un módulo de conciliación bancaria automatizada...    | P0  |
| US-CONT-001-02     | contratista          | cargar documentación de estados de pago en línea...   | P1  |
| US-CORP-001-01     | director_corporacion | transferencias corrientes para gastos operativos...   | P2  |
| US-DIPIR-001-02    | jefe_dipir           | aprobar CDPs digitalmente con validación automátic... | P0  |
| US-EC33-001-01     | encargado_c33        | reporte de vida útil y depreciación de activos fin... | P2  |
| US-ECIF-001-01     | ecif                 | reportes de cumplimiento de controles financieros...  | P0  |
| US-G7-001-01       | revisor_glosa7       | un módulo de control de programación de caja con c... | P0  |
| US-INTFIN-001-01   | interventor_financie | acceso total de auditoría al ERP financiero...        | P0  |
| US-INV-001-01      | analista_inventario  | un módulo de control de activos con ubicación y re... | P1  |
| US-JCONT-001-01    | jefe_depto_contabili | un checklist de cierre mensual automatizado...        | P0  |
| US-JD-ANA-001-01   | jefe_depto_analisis  | reportes de devengo vs. gasto efectivo en tiempo r... | P0  |
| US-JPRE-001-01     | jefe_presupuesto     | bloquear imputaciones que excedan el saldo disponi... | P0  |
| US-JTES-001-01     | jefe_depto_tesoreria | un módulo de programación de pagos con proyección ... | P0  |
| US-REND-002-01     | encargado_rendicione | un workflow de revisión con estados (Recibida, En ... | P0  |
| US-RGASTO-001-01   | referente_gasto      | validación automática de clasificadores presupuest... | P0  |
| US-SUBV-001-01     | analista_subvencione | un registro de organizaciones receptoras con histo... | P1  |
| US-SUP-OBRA-001-01 | supervisor_obras     | alertas de vencimiento de boletas de garantía...      | P0  |


---

*Documento parte de GORE_OS Blueprint Integral v5.5*  
*Última actualización: 2025-12-20 | SSOT: inventario_roles_v8.yml, historias_usuarios_v2.yml*
