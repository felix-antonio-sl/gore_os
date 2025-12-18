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

| Subdominio       | Contenido                                            | Enlace                                                     |
| ---------------- | ---------------------------------------------------- | ---------------------------------------------------------- |
| **Core IPR**     | Taxonomía, Ciclo de vida (Fases 1-7), Procesos P1-P7 | [sub_dfin_ipr_core.md](d-fin/sub_dfin_ipr_core.md)         |
| **Mecanismos**   | Selector, Árbol de decisión, Guías KODA              | [sub_dfin_mecanismos.md](d-fin/sub_dfin_mecanismos.md)     |
| **Presupuesto**  | Ciclo anual, Glosas, Cadena SIGFE                    | [sub_dfin_presupuesto.md](d-fin/sub_dfin_presupuesto.md)   |
| **Rendiciones**  | SISREC, Mora, Res. 30 CGR                            | [sub_dfin_rendiciones.md](d-fin/sub_dfin_rendiciones.md)   |
| **Portafolio**   | Banca Inversión, PuntajeImpacto, Alertas 360°        | [sub_dfin_portafolio.md](d-fin/sub_dfin_portafolio.md)     |
| **Ejecutores**   | Calificación, Mesa de Ayuda, Inducción               | [sub_dfin_ejecutores.md](d-fin/sub_dfin_ejecutores.md)     |
| **User Stories** | Catálogo consolidado por proceso/módulo              | [sub_dfin_user_stories.md](d-fin/sub_dfin_user_stories.md) |

---

## Glosario D-FIN

| Término | Definición                                                                          |
| ------- | ----------------------------------------------------------------------------------- |
| IPR     | Intervención Pública Regional. Paragua que agrupa IDI, PPR y tipologías específicas |
| IDI     | Iniciativa de Inversión. Gasto de capital (S.31/S.33). Requiere RS/AD de MDSF       |
| PPR     | Programa Público Regional. Gasto corriente/mixto (S.24)                             |
| RS      | Recomendación Satisfactoria (MDSF/SNI)                                              |
| RF      | Resultado Favorable (DIPRES/SES)                                                    |
| ITF     | Informe Técnico Favorable. Evaluación interna GORE                                  |
| CDP     | Certificado de Disponibilidad Presupuestaria                                        |
| BIP     | Banco Integrado de Proyectos (SNI)                                                  |
| SISREC  | Sistema de Rendición Electrónica de Cuentas (CGR)                                   |
| FNDR    | Fondo Nacional de Desarrollo Regional                                               |
| FRPD    | Fondo Regional de Productividad y Desarrollo                                        |
| FRIL    | Fondo Regional de Iniciativa Local (≤5.000 UTM)                                     |
| C33     | Circular 33. Estudios, ANF, conservación, emergencias                               |
| S8%     | Subvención 8%. Financiamiento a ONG/OSC                                             |

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

*Documento parte de GORE_OS Blueprint Integral v5.5*  
*Última actualización: 2025-12-18*
