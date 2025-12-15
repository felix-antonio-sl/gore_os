# 📋 TDE Compliance — Alineamiento Normativo GORE OS

> **Sistema**: GORE OS v7.0.0 CONSOLIDATED  
> **Paradigma**: Cumplimiento normativo DS4/DS7-DS12 + Ley 21.180

---

## Resumen Ejecutivo

Este documento consolida el backlog, roadmap, gates y calendario de sprints para el **cumplimiento TDE** del GORE Ñuble, alineando:

- `data-gore/ontology` (modelo categórico)
- `gore_os/docs` (especificación funcional)
- Lineamientos TDE (KODA) asociados a DS4, DS7–DS12 y protección de datos personales

---

## 1. Fuentes Normativas (KODA)

| Decreto  | Archivo KODA                                                                         | Ámbito                   |
| -------- | ------------------------------------------------------------------------------------ | ------------------------ |
| **DS4**  | `kb_tde_lineamientos_023_reglamento_transformacion_digital_ds4_koda.yml`             | Reglamento TD            |
| **DS7**  | `kb_tde_lineamientos_018_norma_seguridad_info_ciberseguridad_koda.yml`               | Seguridad/Ciberseguridad |
| **DS8**  | `kb_tde_lineamientos_014_norma_notificaciones_koda.yml`                              | Notificaciones           |
| **DS9**  | `kb_tde_lineamientos_020_norma_autenticacion_koda.yml`                               | Autenticación            |
| **DS10** | `kb_tde_lineamientos_012_norma_documentos_expedientes_electronicos_koda.yml`         | Expedientes              |
| **DS11** | `kb_tde_lineamientos_033_norma_calidad_funcionamiento_plataformas_koda.yml`          | Calidad                  |
| **DS12** | `kb_tde_lineamientos_013_norma_interoperabilidad_koda.yml`                           | Interoperabilidad        |
| **RAT**  | `kb_tde_lineamientos_021_registro_actividades_tratamiento_datos_personales_koda.yml` | Datos Personales         |

### Plataformas Complementarias

- **ClaveÚnica**: `kb_tde_lineamientos_015_plataforma_claveunica_integracion_koda.yml`
- **Notificaciones Estado**: `kb_tde_lineamientos_016_plataforma_notificaciones_estado_koda.yml`
- **DocDigital**: `kb_tde_lineamientos_026_plataforma_docdigital_koda.yml`
- **PISEE**: `kb_tde_lineamientos_027_plataforma_pisee_interoperabilidad_koda.yml`

---

## 2. Backlog por Prioridad

### P0 — Backbone de Cumplimiento

#### DS10: Expediente Electrónico

| Ticket         | Requisito          | Historias      | Axioma        |
| -------------- | ------------------ | -------------- | ------------- |
| TDE-P0-DS10-01 | IUIe obligatorio   | AS-009, CTD-03 | `AX_DS10_001` |
| TDE-P0-DS10-02 | Índice electrónico | AS-010         | `AX_DS10_002` |
| TDE-P0-DS10-03 | Metadatos mínimos  | AS-011         | `AX_DS10_003` |

#### DS9: Autenticación

| Ticket        | Requisito               | Historias        | Axioma       |
| ------------- | ----------------------- | ---------------- | ------------ |
| TDE-P0-DS9-01 | ClaveÚnica OIDC         | tic-006..011     | `AX_DS9_001` |
| TDE-P0-DS9-02 | Custodia secretos       | tic-007          | `AX_DS9_002` |
| TDE-P0-DS9-03 | Prohibición auth propia | tic-011          | `AX_DS9_003` |
| TDE-P0-DS9-04 | Clave Tributaria PJ     | tic-010          | `AX_DS9_004` |
| TDE-P0-DS9-05 | Trazabilidad accesos    | tic-009, CISO-05 | `AX_DS9_005` |

#### DS8: Notificaciones

| Ticket        | Requisito           | Historias    | Axioma       |
| ------------- | ------------------- | ------------ | ------------ |
| TDE-P0-DS8-01 | Canal oficial + DDU | tic-012..013 | `AX_DS8_001` |
| TDE-P0-DS8-02 | Constancia + 3 días | tic-016..017 | `AX_DS8_003` |
| TDE-P0-DS8-03 | API vía PISEE       | tic-014..015 | `AX_DS8_005` |

#### DS12: Interoperabilidad

| Ticket         | Requisito             | Historias | Axioma        |
| -------------- | --------------------- | --------- | ------------- |
| TDE-P0-DS12-01 | Nodo dev/prod         | tic-019   | `AX_DS12_001` |
| TDE-P0-DS12-02 | Catálogo servicios    | tic-020   | `AX_DS12_002` |
| TDE-P0-DS12-03 | Trazabilidad central  | tic-021   | `AX_DS12_003` |
| TDE-P0-DS12-04 | Gestor acuerdos       | tic-022   | `AX_DS12_005` |
| TDE-P0-DS12-05 | Gestor autorizaciones | tic-023   | `AX_DS12_004` |

#### DS7: Seguridad

| Ticket        | Requisito          | Historias    | Axioma       |
| ------------- | ------------------ | ------------ | ------------ |
| TDE-P0-DS7-01 | Política + CISO    | tic-024..025 | `AX_DS7_001` |
| TDE-P0-DS7-02 | Clasificación CIA  | tic-026      | `AX_DS7_003` |
| TDE-P0-DS7-03 | TLS 1.2+ / cifrado | tic-027      | `AX_DS7_006` |
| TDE-P0-DS7-04 | Reporte incidentes | tic-028      | `AX_DS7_004` |

### P1 — Calidad y Privacidad

#### DS11: Calidad Plataformas

| Ticket         | Requisito            | Historias    |
| -------------- | -------------------- | ------------ |
| TDE-P1-DS11-01 | Catálogo plataformas | tic-029      |
| TDE-P1-DS11-02 | Plan anual mejora    | tic-030      |
| TDE-P1-DS11-03 | Gate EvalTIC         | tic-031..032 |

#### Privacidad (RAT)

| Ticket         | Requisito      | Historias  |
| -------------- | -------------- | ---------- |
| TDE-P1-PRIV-01 | RAT mínimo     | DPO-05     |
| TDE-P1-PRIV-02 | Versionado RAT | DPO-06     |
| TDE-P1-PRIV-03 | Anonimización  | DPO-07..08 |

---

## 3. Roadmap de Ejecución (Gates)

```
Fase 0 ─► Fase 1 ─► Fase 2 ─► Fase 3 ─► Fase 4 ─► Fase 5 ─► Fase 6 ─► Fase 7
PREP     DS10      DS9       DS7       DS12      DS8       DS11      PRIV
```

| Fase  | Objetivo           | Gates                                   |
| ----- | ------------------ | --------------------------------------- |
| **0** | Preparación        | 0.1 Base documental                     |
| **1** | DS10 Expediente    | 1.1 IUIe, 1.2 Índice, 1.3 Trazabilidad  |
| **2** | DS9 Identidad      | 2.1 ClaveÚnica, 2.2 Auditoría           |
| **3** | DS7 Seguridad      | 3.1 Gobernanza, 3.2 CIA, 3.3 Incidentes |
| **4** | DS12 Interop       | 4.1 Nodo, 4.2 Catálogo, 4.3 Acuerdos    |
| **5** | DS8 Notificaciones | 5.1 DDU, 5.2 Constancia, 5.3 Datos      |
| **6** | DS11 Calidad       | 6.1 Catálogo, 6.2 Plan, 6.3 EvalTIC     |
| **7** | Privacidad         | 7.1 RAT, 7.2 Anonimización              |

---

## 4. Calendario de Sprints (2 semanas c/u)

| Sprint | Semanas | Foco             | Gates    |
| ------ | ------- | ---------------- | -------- |
| S0     | 0-2     | Preparación      | 0.1      |
| S1     | 2-4     | DS10 IUIe        | 1.1      |
| S2     | 4-6     | DS10 Índice/Meta | 1.2, 1.3 |
| S3     | 6-8     | DS9 Auth         | 2.1, 2.2 |
| S4     | 8-10    | DS7 Seguridad    | 3.1, 3.2 |
| S5     | 10-12   | DS7/DS12         | 3.3, 4.1 |
| S6     | 12-14   | DS12 Catálogo    | 4.2, 4.3 |
| S7     | 14-16   | DS8 Notif        | 5.1, 5.2 |
| S8     | 16-18   | DS8/DS11         | 5.3, 6.1 |
| S9     | 18-20   | DS11 Plan        | 6.2, 6.3 |
| S10    | 20-22   | Privacidad       | 7.1, 7.2 |

---

## 5. Escenarios de Capacidad

### Escenario 1 — 1 Squad (Secuencial)

- **Horizonte**: 12 semanas (6 sprints) para P0 operativo
- **Riesgo**: DS8 se retrasa si DS12 Gate 4.3 demora

### Escenario 2 — 2 Squads (Paralelo)

- **Horizonte**: 8 semanas (4 sprints)
- **División**: Squad A (DS10→DS9), Squad B (DS7→DS12)

### Escenario 3 — Fast-Track (Demo)

- **Horizonte**: 6 semanas (3 sprints)
- **Riesgo**: Alta deuda técnica

---

## 6. Mapa de Implementación

### Repos Involucrados

| Repo                 | Artefactos                     |
| -------------------- | ------------------------------ |
| `gore_os/docs`       | Especificaciones, User Stories |
| `data-gore/ontology` | Entidades, Axiomas, Funtores   |
| `data-gore/scripts`  | `verify_tde_axioms.py`         |

### Trazabilidad por Decreto

| Decreto | Entidad Ontología              | Functor              |
| ------- | ------------------------------ | -------------------- |
| DS10    | `Expediente_Electronico_TDE`   | `F_Exp_GORE_TDE`     |
| DS9     | `Identidad_Digital.ClaveUnica` | `F_Auth_GORE_TDE`    |
| DS8     | `Notificacion_Electronica`     | `F_Notif_GORE_TDE`   |
| DS12    | `Interoperabilidad_Estado`     | `F_Interop_GORE_TDE` |
| DS7     | `Seguridad_TDE`                | -                    |

---

## 7. Definición de Done

Un ticket se considera **Done** cuando:

1. **Docs**: Existe especificación en `gore_os/docs` con:
   - Requisito explícito
   - Criterios de aceptación verificables
   - Dependencias (DS*/KODA)

2. **Modelo**: Existe correspondencia en ontología:
   - Entidad(es) en `L_tde_representacion.yaml`
   - Axioma(s) en `L_tde_compliance.yaml`
   - Mapeo en `F_tde_mapping.yaml`

3. **Trazabilidad**: El ticket referencia:
   - DS y/o artefacto KODA
   - Artefactos internos afectados
