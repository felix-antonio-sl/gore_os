# 📋 User Stories Unificadas — GORE OS

> [!CAUTION]
> ## ⚠️ ARCHIVO DEPRECATED
> Este archivo ha sido **refactorizado** y migrado a formato KODA YAML estructurado.
> 
> **Nueva ubicación:** `gore_os/specs/`
> - `_manifest.yml` (índice maestro)
> - `kb_goreos_us_d-{dominio}.yml` (9 archivos por dominio)
> 
> **Total migrado:** 322 User Stories en 9 dominios
> 
> **Para consultas use:** El catálogo KODA en `/specs/` es ahora la fuente de verdad.

---

> **Sistema Operativo Cognitivo Regional**  
> **Versión**: 6.4.0 REN-COMPLETE (LEGACY)  
> **Paradigma**: Ingeniería de Software Composicional  
> **Ontología**: `data-gore/ontology` v6.0.0

---

## Resumen Ejecutivo

| Métrica                | Cantidad |
| ---------------------- | -------- |
| **Total User Stories** | **540+** |
| **Módulos GORE OS**    | **22**   |
| **Roles/Actores**      | **86+**  |
| **Prioridad Crítica**  | 248      |
| **Prioridad Alta**     | 210      |

---

## DOMINIO NEW: SEGURIDAD Y GOBERNANZA

### M20. Seguridad Pública y Prevención del Delito

**Objetivo**: Gestionar la estrategia regional de seguridad con foco preventivo y coordinación interinstitucional.

#### Encargado Prevención (EPD)

| ID     | User Story                                                                | Prioridad |
| ------ | ------------------------------------------------------------------------- | --------- |
| EPD-01 | **Visualizar mapa de calor delictual** (integración STOP/SPD)             | Crítica   |
| EPD-02 | Gestionar cartera de proyectos preventivos (iluminación, cámaras, social) | Crítica   |
| EPD-03 | Coordinar sesiones del Consejo Regional de Seguridad Pública              | Alta      |
| EPD-04 | Emitir informes de impacto de inversiones en seguridad                    | Alta      |

#### Analista de Proyectos de Seguridad (APS)

| ID     | User Story                                                  | Prioridad |
| ------ | ----------------------------------------------------------- | --------- |
| APS-01 | Evaluar admisibilidad técnica de proyectos seguridad        | Alta      |
| APS-02 | Monitorear ejecución financiera de convenios con municipios | Alta      |
| APS-03 | Gestionar programa de asistencia a víctimas                 | Media     |

### Órganos Colegiados y Comités

**Objetivo**: Habilitar a cuerpos colegiados para ejercer sus roles consultivos y de coordinación.

#### COSOC / Comités (COL)

| ID     | User Story                                                                    | Prioridad |
| ------ | ----------------------------------------------------------------------------- | --------- |
| COL-01 | Acceder a dashboard de transparencia activa del GORE                          | Alta      |
| COL-02 | Recibir y responder consultas sobre instrumentos de planificación (ERD, PROT) | Media     |
| COL-03 | Visualizar estado de ejecución presupuestaria agregada                        | Media     |

---

### M21. GOBERNANZA DE INVERSION — Filtro Estratégico

**Objetivo**: Asegurar la pertinencia política y estratégica de la inversión antes de la evaluación técnica.

#### Comité Directivo Regional (CDR)

| ID     | User Story                                                              | Prioridad |
| ------ | ----------------------------------------------------------------------- | --------- |
| CDR-01 | **Sesión de Pertinencia** (Filtro Pre-Admisibilidad)                    | Crítica   |
| CDR-02 | **Priorización Estratégica** (Ranking de cartera para evaluación)       | Crítica   |
| CDR-03 | Visualizar cartera georreferenciada por provincia (equidad territorial) | Alta      |

#### Oficina de Partes (OP)

| ID    | User Story                                                 | Prioridad |
| ----- | ---------------------------------------------------------- | --------- |
| OP-01 | **Recepcionar Oficio Ingreso IPR** (Timbre digital/físico) | Crítica   |
| OP-02 | Derivar antecedentes a DIPIR (Ruta automática)             | Alta      |

---

## DOMINIO IV: METABOLISMO OPERACIONAL

### M1. IPR (SNI) — Gestión de Inversión Pública Regional

**Journeys:** J01, J05, J06, J13 | **FSM:** FSM-IPR (15 estados)

#### Formulador Externo (FE)

| ID         | User Story                                                                                                | Prioridad |
| ---------- | --------------------------------------------------------------------------------------------------------- | --------- |
| FE-IPR-000 | **Bolsa de Concursos Unificada:** Ver convocatorias abiertas (FRPD, 8%, FRIL) vs Ventanilla Abierta (SNI) | Crítica   |
| FE-IPR-001 | Consultar árbol de decisión financiamiento (SNI/FRIL/FRPD/8%/Glosa06)                                     | Crítica   |
| FE-IPR-002 | Ver lista de documentos obligatorios según mecanismo                                                      | Crítica   |
| FE-IPR-003 | Cargar postulación IPR con antecedentes digitalizados                                                     | Crítica   |
| FE-IPR-004 | Recibir notificación observaciones admisibilidad (plazo 60d) (DS8: ver M10 TIC)                           | Crítica   |
| FE-IPR-005 | Subsanar observaciones en línea (sin trámite presencial)                                                  | Alta      |
| FE-IPR-006 | Consultar estado en tiempo real (timeline visual)                                                         | Crítica   |
| FE-IPR-007 | Ver historial de postulaciones con tasa de éxito                                                          | Media     |
| FE-IPR-008 | Verificar elegibilidad municipal FRIL (<5000 UTM)                                                         | Crítica   |
| FE-IPR-009 | Descargar convenio de transferencia para firma FEA                                                        | Alta      |
| FE-IPR-010 | Reportar avance mensual (% físico/financiero)                                                             | Crítica   |

#### Entidad Ejecutora (EE)

| ID        | User Story                                                  | Prioridad |
| --------- | ----------------------------------------------------------- | --------- |
| EE-IPR-01 | **Ingresar rendición SISREC** (integración o carga manual)  | Crítica   |
| EE-IPR-02 | Responder observaciones a rendiciones rechazadas            | Crítica   |
| EE-IPR-03 | **Solicitar Modificación** (Plazo, Monto, Reitemización)    | Alta      |
| EE-IPR-04 | Reintegrar saldos no ejecutados (botón de pago/instrucción) | Crítica   |
| EE-IPR-05 | Registar adjudicación licitación y contrato                 | Alta      |
| EE-IPR-06 | Subir Acta Entrega Terreno / Inicio Obras                   | Crítica   |
| EE-IPR-07 | Solicitar Recepción Provisoria/Definitiva Obras             | Crítica   |

#### Analista de Preinversión (DIPIR) — Evaluación

| ID           | User Story                                                      | Prioridad |
| ------------ | --------------------------------------------------------------- | --------- |
| DIPIR-PRE-01 | **Evaluar Admisibilidad Formal** (Checklist documental)         | Crítica   |
| DIPIR-PRE-02 | **Track A (SNI):** Revisar Perfil/Prefactibilidad (MDSF)        | Crítica   |
| DIPIR-PRE-03 | **Track B (Glosa 06):** Evaluar Perfil (Pertinencia DIPRES)     | Crítica   |
| DIPIR-PRE-04 | **Track B (Glosa 06):** Evaluar Diseño (Marco Lógico detallado) | Crítica   |
| DIPIR-PRE-05 | **Track C (Simplificado):** Evaluar <5000 UTM / Conservación    | Alta      |
| DIPIR-PRE-06 | Preparar Oficio Solicitud Evaluación (MDSF/DIPRES)              | Alta      |
| DIPIR-PRE-07 | Registrar resultado evaluación externa (RS/RF/AD/OT)            | Crítica   |

#### Analista Depto. Presupuesto (DAF-PPTO) — Tramitación
>
> **Nota:** Detalle flujo administrativo financiero.
| ID            | User Story                                                     | Prioridad |
| ------------- | -------------------------------------------------------------- | --------- |
| PPTO-ADMIN-01 | Emitir CDP (Certificado Disponibilidad Presupuestaria)         | Crítica   |
| PPTO-ADMIN-02 | **Tramitar Resolución/Decreto Identificatorio** (DIPRES/CGR)   | Crítica   |
| PPTO-ADMIN-03 | Elaborar Convenio de Transferencia (Borrador)                  | Alta      |
| PPTO-ADMIN-04 | Gestionar firmas Convenio (Gore - Ejecutor)                    | Alta      |
| PPTO-ADMIN-05 | **Devengar Obligación** (Hito exigible / Tramitación completa) | Crítica   |

#### Analista de Gestión (DIPIR-GESTION)

| ID          | User Story                                                          | Prioridad |
| ----------- | ------------------------------------------------------------------- | --------- |
| AD-GEST-001 | Dashboard de cartera ejecución (fisico vs financiero)               | Crítica   |
| AD-GEST-002 | **Evaluar Solicitud Modificación** (Informe Técnico)                | Alta      |
| AD-GEST-003 | Gestionar Reevaluación (si supera 10% / cambio sustancial)          | Crítica   |
| AD-GEST-004 | Validar estado de pago (avance físico coherente)                    | Crítica   |
| AD-GEST-005 | **Visar Cierre Técnico** (Checklist recepción obras/programas)      | Crítica   |
| AD-GEST-006 | Gestionar devolución de garantías (Custodia)                        | Alta      |
| AD-IPR-002  | Bandeja de postulaciones nuevas (FIFO)                              | Crítica   |
| AD-IPR-003  | Checklist de admisibilidad dinámico según track                     | Crítica   |
| AD-IPR-004  | Registrar resultado admisibilidad y notificar UF (DS8: ver M10 TIC) | Crítica   |
| AD-IPR-005  | Enviar IPR a MDSF registrando en BIP (DS12: ver M10 TIC)            | Crítica   |
| AD-IPR-006  | Monitorear RATE con semáforo RS/FI/OT/AD                            | Crítica   |
| AD-IPR-007  | Alertas de IPR >30 días sin movimiento (HAIC: Sugerencia)           | Alta      |
| AD-IPR-008  | Registrar observaciones FI/OT con plazo legal                       | Crítica   |
| AD-IPR-009  | Generar cartera RS para sesión CORE filtrada por período            | Alta      |
| AD-IPR-010  | Generar carpeta CORE (PDF consolidado)                              | Alta      |
| AD-IPR-011  | Registrar problema/nudo (tipo, impacto, compromiso)                 | Crítica   |
| AD-IPR-012  | Semáforos de ejecución (% físico vs financiero vs tiempo)           | Crítica   |
| AD-IPR-013  | Tramitar modificaciones (determinar si requiere RS/CORE)            | Alta      |
| AD-IPR-014  | Validar cierre técnico (acta recepción, saldos)                     | Crítica   |
| AD-IPR-015  | Exportar reportes CGR/DIPRES (Excel/PDF)                            | Alta      |
| AD-IPR-016  | **Registrar código SIGFE** (`subt`/`item`/`asig`) en ficha IPR      | Crítica   |
| AD-IPR-017  | **Gestionar vigencia** de iniciativas (VIGENTE/NO VIGENTE)          | Alta      |
| AD-CONV-001 | **Tramitar envío CGR** y registrar estado toma de razón             | Crítica   |
| AD-CONV-002 | **Clasificar convenio** AFECTA/EXENTA según normativa CGR           | Alta      |
| PD-EJEC-001 | **Registrar ejecución mensual** REAL vs PROYECTADO por IPR          | Crítica   |
| PD-EJEC-002 | **Monitorear desviaciones** ejecución con semáforos y alertas       | Alta      |

#### Jefatura DIPIR (JD)

> **Nota:** Integra UC-DIPIR 15-53 (Ciclo IPR LifeCycle), 54-59 (Coordination), 60-65 (Team), 66-70 (System).
>
> * Los casos 01-14 (Presupuesto) se cubren en M2 (DAF).

| ID           | User Story                                                    | Prioridad |
| ------------ | ------------------------------------------------------------- | --------- |
| JD-DIPIR-001 | Dashboard ejecutivo: total IPR, monto, % ejecución, problemas | Crítica   |
| JD-DIPIR-002 | Distribución carga por analista con métricas tiempos          | Alta      |
| JD-DIPIR-003 | Tiempos promedio por fase con comparativo histórico           | Alta      |
| JD-DIPIR-004 | Problemas críticos escalados en lista priorizada              | Crítica   |
| JD-DIPIR-005 | Propuesta de priorización (ranking ERD/urgencia/monto)        | Crítica   |
| JD-DIPIR-006 | Informes gestión divisional con KPIs                          | Alta      |
| JD-DIPIR-007 | Información CDR con alineamiento ERD                          | Alta      |
| JD-IPR-054   | Coordinación externa (MDSF/DIPRES) para destrabe proyectos    | Alta      |
| JD-IPR-066   | Gestión de sistemas y alertas críticas                        | Crítica   |

#### Evaluador MDSF Sectorial (RIS)

> **Nota:** Aplica metodología RIS sectoriales según tipología: Cultura, Deportes, Ed.Pública, etc.

| ID     | User Story                                                                       | Prioridad |
| ------ | -------------------------------------------------------------------------------- | --------- |
| RIS-01 | **Visualizar checklist RIS** según tipología de proyecto (Deporte/Cultura/EdPub) | Crítica   |
| RIS-02 | **Validar cumplimiento RIS por etapa** (Preinversión → Diseño → Ejecución)       | Crítica   |
| RIS-03 | **Calcular y validar CAE** Deportista/Espectador según umbrales SNI              | Alta      |
| RIS-04 | **Aplicar metodología Riesgo Desastres 2024** como pre-requisito evaluación      | Alta      |
| RIS-05 | Verificar requisitos propiedad terreno (genéricos SNI + sector específico)       | Alta      |
| RIS-06 | Validar programa arquitectónico firmado por profesional responsable              | Alta      |
| RIS-07 | Verificar Plan de Contingencia para inmuebles existentes (Cultura)               | Media     |

#### Operador Tipologías IDI (BI)

> **Nota:** Gestión analítica de histórico de inversiones regionales.

| ID     | User Story                                                               | Prioridad |
| ------ | ------------------------------------------------------------------------ | --------- |
| IDI-01 | **Consultar histórico inversiones** por tipología/comuna/año             | Alta      |
| IDI-02 | **Visualizar mapa de calor inversión** (monto FNDR/BIP por territorio)   | Alta      |
| IDI-03 | Comparar proyectos similares (por código BIP o nombre) para benchmarking | Media     |
| IDI-04 | **Alertar duplicidades o reinversión** en misma infraestructura (BIP)    | Alta      |
| IDI-05 | Clasificar automáticamente tipología BIP desde nombre de iniciativa      | Media     |

---

### M22. PPR — Programas Públicos Regionales

**Objetivo**: Gestionar la oferta programática (Glosa 06) diferenciando ejecución directa de transferencias.

#### Analista DAE (PPR)

| ID         | User Story                                                                    | Prioridad |
| ---------- | ----------------------------------------------------------------------------- | --------- |
| PPR-DAE-01 | **Evaluar Track A (Transferencia):** Emitir ITF (Informe Técnico Favorable)   | Crítica   |
| PPR-DAE-02 | **Evaluar Track B (Ejecución Directa):** Revisar Matriz Marco Lógico Rigurosa | Crítica   |
| PPR-DAE-03 | Validar Declaración de No-Fraccionamiento (Unicidad de propósito)             | Alta      |
| PPR-DAE-04 | Gestionar Comité de Pertinencia (Presentación y Acta)                         | Alta      |

#### Entidad Postulante (Transferencia)

| ID         | User Story                                                 | Prioridad |
| ---------- | ---------------------------------------------------------- | --------- |
| PPR-EXT-01 | Cargar "Declaración Jurada Art. 18" (Inhabilidades)        | Crítica   |
| PPR-EXT-02 | Visualizar estado: Admisibilidad > Pertinencia > DAE > ITF | Alta      |

---

### M23. FRIL — Fondo Regional de Iniciativa Local

**Objetivo**: Administración de cartera municipal menor (infraestructura comunal).

#### Analista FRIL (DIPIR)

| ID      | User Story                                                          | Prioridad |
| ------- | ------------------------------------------------------------------- | --------- |
| FRIL-01 | **Configurar Marcos Presupuestarios** (Quota por Comuna)            | Crítica   |
| FRIL-02 | Validar proyecto contra saldo de marco comunal (bloqueo automático) | Crítica   |
| FRIL-03 | Emitir RATE FRIL (RS, FI, OT, NV)                                   | Crítica   |
| FRIL-04 | Controlar tope 2000 UTM (o máximo vigente anual)                    | Alta      |

---

### M24. FRPD — Fondo de Productividad (Fomento)

**Objetivo**: Fomento productivo alineado a ejes estratégicos (Glosa 02/06).

#### Comité FRPD

| ID          | User Story                                                                        | Prioridad |
| ----------- | --------------------------------------------------------------------------------- | --------- |
| FRPD-COM-01 | **Filtro Estratégico:** Validar alineación con Ejes (Sustentabilidad, Innovación) | Crítica   |
| FRPD-COM-02 | Ranking de competitividad regional                                                | Alta      |

#### Analista Fomento

| ID          | User Story                                             | Prioridad |
| ----------- | ------------------------------------------------------ | --------- |
| FRPD-ANA-01 | Evaluar admisibilidad de beneficiario (Empresa/Gremio) | Crítica   |
| FRPD-ANA-02 | Validar co-financiamiento pecuniario/valorado          | Alta      |

---

### M25. CONCURSO 8% — Subvenciones (FNDR)

**Objetivo**: Gestión masiva de subvenciones comunitarias (Social, Cultura, Seguridad, Deporte).

#### Analista 8% (DIDESO/DIPIR)

| ID     | User Story                                                               | Prioridad |
| ------ | ------------------------------------------------------------------------ | --------- |
| SUB-01 | **Check Automático Inhabilidades** (Cruce RUT Directiva vs Funcionarios) | Crítica   |
| SUB-02 | Evaluar Admisibilidad Estricta (Vigencia PJ, Directorio)                 | Crítica   |
| SUB-03 | Aplicar pauta de evaluación ciega (doble ciego opcional)                 | Alta      |
| SUB-04 | Generar nómina de adjudicación para CORE                                 | Crítica   |

#### Postulante Comunitario

| ID        | User Story                                               | Prioridad |
| --------- | -------------------------------------------------------- | --------- |
| SUB-US-01 | Postular a línea temática específica (wizard requisitos) | Crítica   |
| SUB-US-02 | Subir rendición simplificada (gastos menores)            | Alta      |

---

### M26. CIRCULAR 33 — Activos y Emergencia

**Objetivo**: Adquisición de activos no financieros y respuesta rápida.

#### Analista Operaciones (C33)

| ID     | User Story                                                  | Prioridad |
| ------ | ----------------------------------------------------------- | --------- |
| C33-01 | **Track Emergencia (5%):** Aprobación Fast-Track (24-48hrs) | Crítica   |
| C33-02 | Validar tipología Activo (Vehículo, Maquinaria, Equipo)     | Alta      |
| C33-03 | Controlar vida útil y plan de mantención (compromiso)       | Alta      |

---

### M2. PRESUPUESTO — Gestión Financiera

**Journeys:** J18 | **Invariantes:** INV_FIN_01, INV_FIN_02

#### Profesional DAF (PD)

| ID          | User Story                                                   | Prioridad |
| ----------- | ------------------------------------------------------------ | --------- |
| PD-PPTO-001 | Emitir CDP validando saldo en asignación                     | Crítica   |
| PD-PPTO-002 | Consultar estado afectación por IPR                          | Crítica   |
| PD-PPTO-003 | Programar pagos con reglas devengo CGR                       | Alta      |
| PD-PPTO-004 | Alertas glosas infringidas (03/04/06)                        | Crítica   |
| PD-PPTO-005 | Asistente modificaciones presupuestarias                     | Alta      |
| PD-PPTO-006 | Proyección vs programa caja (alertas >5%)                    | Alta      |
| PD-PPTO-007 | Cierre deuda flotante por programa/subtítulo                 | Crítica   |
| PD-PPTO-008 | Sincronizar SIGFE validando consistencia (DS12: ver M10 TIC) | Alta      |
| PD-PPTO-009 | Gestionar cometidos/viáticos (ciclo completo)                | Alta      |
| PD-PPTO-010 | Conciliación bancaria automática                             | Alta      |

#### Jefatura DAF (JD)

| ID         | User Story                                                                  | Prioridad |
| ---------- | --------------------------------------------------------------------------- | --------- |
| JD-DAF-001 | Dashboard ejecución mensual por subtítulo                                   | Crítica   |
| JD-DAF-002 | Monitor rendiciones vencidas (días mora, Art.18)                            | Crítica   |
| JD-DAF-003 | Aprobar informes FEA habilitando contabilización                            | Crítica   |
| JD-DAF-004 | Proyección deuda flotante e impacto siguiente año                           | Alta      |
| JD-DAF-005 | Visar resoluciones cometidos (firma masiva)                                 | Alta      |
| JD-DAF-006 | **Gestionar modificaciones presupuestarias** por tipo (MODIFICACION/REBAJA) | Alta      |
| JD-DAF-007 | **Reconciliar ejecución** REAL vs PROYECTADO mensualmente                   | Alta      |
| JD-DAF-008 | **Alertar gaps de reconciliación** datos vs maestro iniciativas             | Media     |

#### Ciclo Presupuestario — Formulación y Aprobación (kb_gn_018)

> **Nota:** User stories derivadas del KB de Gestión Presupuestaria.

| ID           | User Story                                                               | Actor      | Prioridad |
| ------------ | ------------------------------------------------------------------------ | ---------- | --------- |
| PPTO-FORM-01 | **Elaborar proyecto presupuesto inversiones** alineado con ERD           | DIPIR      | Crítica   |
| PPTO-FORM-02 | **Coordinar ARI** con servicios vía Chileindica (plazo primeros 4 meses) | DIPIR      | Crítica   |
| PPTO-FORM-03 | **Proyectar gastos funcionamiento** (Subt. 21/22) respetando glosas      | DAF        | Crítica   |
| PPTO-FORM-04 | **Verificar clasificador presupuestario** según D.854/2004               | DAF        | Alta      |
| PPTO-FORM-05 | **Crear provisiones** (FRIL, FRPD 33.03, 8% FNDR) en presupuesto inicial | DIPIR      | Alta      |
| PPTO-APR-01  | **Presentar distribución inicial al CORE** (plazo 10 días desde Ley)     | Gobernador | Crítica   |
| PPTO-APR-02  | **Tramitar envío a DIPRES** con antecedentes (plazo 5 días)              | DAF        | Crítica   |
| PPTO-APR-03  | **Monitorear Toma de Razón CGR** (15+15 días) con alertas                | DAF        | Alta      |
| PPTO-APR-04  | **Cargar presupuesto aprobado en SIGFE** post Toma de Razón              | DAF        | Crítica   |

#### Ciclo Presupuestario — Ejecución y Modificaciones (kb_gn_018)

| ID           | User Story                                                                  | Actor     | Prioridad |
| ------------ | --------------------------------------------------------------------------- | --------- | --------- |
| PPTO-EJEC-01 | **Gestionar grados de afectación** (preafectación→compromiso→devengo→pago)  | DAF       | Crítica   |
| PPTO-EJEC-02 | **Aplicar reglas devengo diferenciado** según tipo transferencia (CGR)      | DAF       | Crítica   |
| PPTO-MOD-01  | **Clasificar modificación por tipo** y determinar actos requeridos (Res/DS) | DAF/DIPIR | Alta      |
| PPTO-MOD-02  | **Validar excepciones sin CORE** (10% aumento ≤7000 UTM, Glosa 14, etc.)    | DAF       | Alta      |
| PPTO-MOD-03  | **Tramitar visación DIPRES** y seguimiento Toma de Razón CGR                | DAF       | Alta      |

#### Ciclo Presupuestario — Control y Reportes (kb_gn_018)

| ID           | User Story                                                           | Actor | Prioridad |
| ------------ | -------------------------------------------------------------------- | ----- | --------- |
| PPTO-CTRL-01 | **Generar reportes DIPRES** (ejecución, caja, dotación, Subt.31 BIP) | DAF   | Alta      |
| PPTO-CTRL-02 | **Publicar cartera proyectos FNDR** mensualmente (Glosa 16)          | DIPIR | Alta      |
| PPTO-CTRL-03 | **Monitorear KPIs Ley Presupuestos** (eficacia, eficiencia, calidad) | DIPIR | Alta      |
| PPTO-CTRL-04 | **Coordinar PROPIR trimestral** e informar al CORE                   | DIPIR | Alta      |

---

### M3. CONVENIOS — Transferencias y Rendiciones

**Journeys:** J07, JX04 | **Invariantes:** INV_FIN_03, INV_FIN_04

| Rol | ID          | User Story                                               | Prioridad |
| --- | ----------- | -------------------------------------------------------- | --------- |
| PD  | PD-CONV-001 | Generar convenios desde plantillas por tipo ejecutor     | Alta      |
| PD  | PD-CONV-002 | Lista convenios por estado (filtros)                     | Alta      |
| PD  | PD-CONV-003 | Alertas convenios por vencer (prórroga/cierre)           | Alta      |
| PD  | PD-CONV-004 | Registrar cuotas transferencia (calendario)              | Crítica   |
| PD  | PD-CONV-005 | Controlar garantías (alertas vencimiento)                | Alta      |
| RTF | RTF-001     | Crear proyectos SISREC habilitando rendiciones           | Crítica   |
| RTF | RTF-002     | Revisar rendiciones (aprobar/observar)                   | Crítica   |
| RTF | RTF-003     | Generar informe aprobación para Jefe DAF                 | Crítica   |
| RTF | RTF-004     | Coordinar regularización rendiciones (>15 días)          | Alta      |
| AOT | AOT-001     | Verificar elegibilidad ejecutor (bloqueo Art.18)         | Crítica   |
| AOT | AOT-002     | Revisar documentación rendición (facturas/boletas)       | Crítica   |
| AOT | AOT-003     | Registrar observaciones técnicas notificando ejecutor    | Alta      |
| AOT | AOT-004     | Certificar cumplimiento parcial habilitando cuota        | Crítica   |
| ESR | ESR-001     | Consolidar rendiciones programa (reporte DIPRES)         | Alta      |
| ESR | ESR-002     | Gestionar mora >90 días escalando a Jurídica             | Crítica   |
| ESR | ESR-003     | Emitir certificado cierre proyecto                       | Alta      |
| UCR | UCR-001     | Contabilizar en SIGFE (requiere FEA) (DS12: ver M10 TIC) | Crítica   |
| UCR | UCR-002     | Dashboard rendiciones pendientes (ranking mora)          | Alta      |
| UCR | UCR-003     | Alertas bloqueo Art.18 (automático)                      | Crítica   |

#### Flujo SISREC — Actores Ejecutor (kb_gn_020)

> **Nota:** User stories para actores del lado Ejecutor en SISREC.

| ID       | User Story                                                                               | Actor              | Prioridad |
| -------- | ---------------------------------------------------------------------------------------- | ------------------ | --------- |
| EJEC-001 | **Aceptar transferencia** del GORE en SISREC para iniciar flujo de rendición             | Analista Ejecutor  | Crítica   |
| EJEC-002 | **Crear informe de rendición** (mensual/regularización/sin movimiento) con plazo 15 días | Analista Ejecutor  | Crítica   |
| EJEC-003 | **Ingresar transacciones** y adjuntar documentos digitalizados                           | Analista Ejecutor  | Crítica   |
| EJEC-004 | **Certificar autenticidad** de documentos digitalizados como Ministro de Fe              | Ministro de Fe     | Crítica   |
| EJEC-005 | **Devolver a analista** si documentos son inválidos o incompletos                        | Ministro de Fe     | Alta      |
| EJEC-006 | **Firmar Informe de Rendición** con FEA y enviar al GORE                                 | Encargado Ejecutor | Crítica   |
| EJEC-007 | **Crear informe de regularización** tras devolución del GORE                             | Analista Ejecutor  | Alta      |

#### Flujo SISREC — Ampliación Actores GORE (kb_gn_020)

| ID      | User Story                                                                 | Actor                  | Prioridad |
| ------- | -------------------------------------------------------------------------- | ---------------------- | --------- |
| RTF-005 | **Registrar y enviar transferencia** al ejecutor en SISREC                 | RTF                    | Crítica   |
| RTF-006 | **Descargar Informe Aprobación** firmado y derivar a UCR                   | RTF                    | Alta      |
| UCR-004 | **Archivar expediente digital** de rendición                               | UCR                    | Alta      |
| UCR-005 | **Supervisar tiempos de revisión de RTF** con alertas SLA (7 días hábiles) | UCR                    | Alta      |
| UCI-001 | **Auditar selectivamente** procesos de transferencia y rendición           | Unidad Control Interno | Alta      |
| UCI-002 | **Informar hallazgos y recomendaciones** al Gobernador y CORE              | Unidad Control Interno | Alta      |

#### Rendiciones por Tipología de Fondos (kb_gn_020)

| ID           | User Story                                                              | Actor | Prioridad |
| ------------ | ----------------------------------------------------------------------- | ----- | --------- |
| REN-FRIL-01  | **Validar rendición FRIL** verificando exención RS y guía operativa     | RTF   | Alta      |
| REN-FRPD-01  | **Verificar cumplimiento de hitos I+D+i** en rendición FRPD             | RTF   | Alta      |
| REN-SUBV8-01 | **Verificar medios de verificación** (fotos, listas) en subvenciones 8% | RTF   | Alta      |
| REN-PROG-01  | **Controlar tope 5% gastos administración** en programas Glosa 06       | DAF   | Alta      |
| REN-S31-01   | **Gestionar rendición interna** de ejecución directa (Subt. 31)         | DAF   | Alta      |

#### Control y Responsabilidades (kb_gn_020)

| ID           | User Story                                                                     | Actor                  | Prioridad |
| ------------ | ------------------------------------------------------------------------------ | ---------------------- | --------- |
| REN-REI-01   | **Gestionar reintegro de fondos** no rendidos o mal rendidos (Art. 31 Res. 30) | DAF                    | Crítica   |
| REN-JUI-01   | **Preparar antecedentes** para Juicio de Cuentas CGR                           | Unidad Control Interno | Alta      |
| REN-TRANS-01 | **Publicar en Transparencia Activa** estado de convenios y rendiciones         | SAI                    | Alta      |

---

### M4. EJECUCIÓN — Seguimiento y Crisis

**Journeys:** J05, J06 | **FSM:** FSM-IPR (fase ejecución)

#### Supervisor (SUP)

| ID      | User Story                                     | Prioridad |
| ------- | ---------------------------------------------- | --------- |
| SUP-001 | Crear carpeta seguimiento (visitas, informes)  | Crítica   |
| SUP-002 | Registrar visitas terreno (fotos, notas, GPS)  | Crítica   |
| SUP-003 | Revisar informes UT (aprobar/observar)         | Crítica   |
| SUP-004 | Gestionar estados de pago (valida físico)      | Crítica   |
| SUP-005 | Alertar desviaciones >10% (recomendación)      | Alta      |
| SUP-006 | Validar actas recepción (autoriza último pago) | Alta      |

#### Administrador Regional (AR)

| ID     | User Story                                       | Prioridad |
| ------ | ------------------------------------------------ | --------- |
| AR-001 | Dashboard ejecutivo (alertas, compromisos)       | Crítica   |
| AR-002 | Monitor proyectos alerta crítica (problema/resp) | Crítica   |
| AR-003 | Compromisos vencidos por división (ranking)      | Crítica   |
| AR-004 | Crear compromiso en reunión (vincula IPR)        | Crítica   |
| AR-005 | Historial compromisos IPR (timeline)             | Alta      |
| AR-006 | Verificar compromisos completados (cierra/dev)   | Crítica   |
| AR-007 | Registrar problema entrevista                    | Alta      |
| AR-008 | Resumen semanal Gobernador (PDF tendencias)      | Crítica   |
| AR-009 | Ranking divisiones cumplimiento                  | Alta      |

#### Jefatura División (JD)

| ID     | User Story                                       | Prioridad |
| ------ | ------------------------------------------------ | --------- |
| JD-001 | Métricas división (IPR, problemas, compromisos)  | Crítica   |
| JD-002 | Encargados con métricas (semáforo personal)      | Alta      |
| JD-003 | Crear compromiso asignar (persona, plazo)        | Crítica   |
| JD-004 | Reasignar compromiso (notifica cambio)           | Alta      |
| JD-005 | Registrar problema IPR (tipo, solución)          | Crítica   |
| JD-006 | Cerrar problema resuelto (lección aprendida)     | Alta      |
| JD-007 | IPR compartidas (responsables interdivisionales) | Alta      |

#### Encargado Operativo (EO)

| ID     | User Story                                    | Prioridad |
| ------ | --------------------------------------------- | --------- |
| EO-001 | Lista compromisos (semáforo días restantes)   | Crítica   |
| EO-002 | Marcar "En progreso" (avance parcial)         | Crítica   |
| EO-003 | Marcar "Completado" (pasa a verificación)     | Crítica   |
| EO-004 | Alertas IPR asignadas                         | Crítica   |
| EO-005 | Registrar informe avance (notifica RTF)       | Alta      |
| EO-006 | Registrar problema detectado (vincula IPR)    | Alta      |
| EO-007 | Ver ficha completa IPR (convenios, historial) | Alta      |

---

### M5. CORE — Gobernanza Regional

**Journeys:** J10, J13

#### Consejero Regional (CR)

| ID     | User Story                                                      | Prioridad |
| ------ | --------------------------------------------------------------- | --------- |
| CR-001 | Carpeta digital sesión (notificación + docs) (DS8: ver M10 TIC) | Crítica   |
| CR-002 | Fichas resumen ejecutivo (1 página por IPR)                     | Alta      |
| CR-003 | Proyectos circunscripción (mapa territorial)                    | Alta      |
| CR-004 | Mapa inversiones (geolocalización + filtros)                    | Crítica   |
| CR-005 | Dashboard ejecución por comuna (semáforo)                       | Crítica   |
| CR-006 | Historial votaciones (resultado y acuerdo)                      | Alta      |
| CR-007 | Cumplimiento acuerdos (estado/evidencia)                        | Crítica   |
| CR-008 | Buscar IPR (código/nombre)                                      | Alta      |
| CR-009 | Portal transparencia Glosa 16 (obligación)                      | Crítica   |
| CR-010 | Exportar PDF/Excel (cualquier vista)                            | Alta      |

#### Gobernador Regional (GR) — **Gestión Estratégica (UC-GR)**
>
> **Nota:** Integra UC-GR-01 a UC-GR-37.
>
> * Estratégicas (01-05): `GR-EST-01`, `04`, `05`
> * Presupuesto/IPR (06-11): `GR-EST-02`, `03`, `06`
> * Admin/Fiscalización (12-32): `GR-EST-07` a `10`, `GR-ADM-01`, `02`
> * Operación/Dashboards (33-37): `GR-OP-01`, `02`

| ID        | User Story                                                      | Prioridad |
| --------- | --------------------------------------------------------------- | --------- |
| GR-EST-01 | Formular políticas desarrollo regional (ERD/PROT/ZUBC)          | Crítica   |
| GR-EST-02 | Proponer distribución FNDR/ISAR (presupuesto al CORE)           | Crítica   |
| GR-EST-03 | Proponer ARI y priorizar cartera IPR para CORE                  | Alta      |
| GR-EST-04 | Declarar zonas rezagadas (focalización territorial)             | Alta      |
| GR-EST-05 | Solicitar transferencia de competencias (Art. 114)              | Alta      |
| GR-EST-06 | Ejecutar planes/proyectos aprobados (seguimiento)               | Crítica   |
| GR-EST-07 | Presidir sesiones CORE (voto dirimente, tabla)                  | Crítica   |
| GR-EST-08 | Nombrar/remover directivos (Admin Regional, Jefes Div)          | Alta      |
| GR-EST-09 | Coordinar respuesta emergencias (Comité Gestión Riesgos)        | Crítica   |
| GR-EST-10 | Representar GORE ante autoridades nacionales y servicios        | Alta      |
| GR-OP-01  | Dashboard ejecutivo integrado (KPIs ERD/Compromisos/Alertas)    | Crítica   |
| GR-OP-02  | Simular impacto de políticas y comparar indicadores comunales   | Alta      |
| GR-ADM-01 | Firmar actos con FEA (Ley 21.180) y resoluciones                | Crítica   |
| GR-ADM-02 | Velar por probidad y transparencia (DIP, Lobby, Disciplinarias) | Crítica   |

#### Gabinete (GAB) — **Apoyo Político (UC-GAB)**
>
> **Nota:** Integra UC-GAB-01 a UC-GAB-20.

| ID      | User Story                                                | Prioridad |
| ------- | --------------------------------------------------------- | --------- |
| GAB-001 | Gestionar agenda GR (reuniones, giras, audiencias)        | Alta      |
| GAB-002 | Coordinar articulación política (CORE, Alcaldes, Parlam.) | Alta      |
| GAB-003 | Preparar minutas y antecedentes para toma de decisiones   | Alta      |
| GAB-004 | Seguimiento de compromisos GR (alertas vencimiento)       | Crítica   |
| GAB-005 | Gestión de crisis comunicacionales y políticas            | Crítica   |
| GAB-006 | Coordinar relación con COSOC (participación ciudadana)    | Alta      |

---

## DOMINIO V: SISTEMA NERVIOSO DIGITAL

### M6. ADMINISTRACIÓN — Sistema y Soporte

| ID     | User Story                                                                       | Prioridad |
| ------ | -------------------------------------------------------------------------------- | --------- |
| AS-001 | Crear/editar divisiones con jefe asignado                                        | Alta      |
| AS-002 | Crear usuarios (email, división, rol)                                            | Crítica   |
| AS-003 | Cambiar rol/división actualizando permisos                                       | Alta      |
| AS-004 | Desactivar usuarios manteniendo historial                                        | Alta      |
| AS-005 | Importar IPR desde Excel validando errores                                       | Alta      |
| AS-006 | Configurar reglas de alerta (disparo automático)                                 | Alta      |
| AS-007 | Ver logs actividad (filtro usuario/acción)                                       | Alta      |
| AS-008 | Estado backups con ejecución manual                                              | Alta      |
| AS-009 | **Gestionar Expediente Electrónico (DS10)** (IUIe/índice/metadatos/trazabilidad) | Crítica   |
| AS-010 | Mantener índice electrónico del expediente (DS10)                                | Crítica   |
| AS-011 | Registrar trazabilidad de acciones sobre expediente (DS10)                       | Alta      |
| AS-012 | **Registrar eventos documentales** (CERT_CORE, CREA_ASIG, APRUEBA_CONV, etc.)    | Alta      |
| AS-013 | **Registrar alineamiento ERD** (eje, lineamiento, objetivo) en ficha IPR         | Alta      |
| AS-014 | **Registrar beneficiarios esperados** para evaluación de impacto social          | Media     |

#### Comunicaciones y Prensa (UC-COM)
>
> **Nota:** Integra UC-COM-01 a UC-COM-24.

| ID      | User Story                                                | Prioridad |
| ------- | --------------------------------------------------------- | --------- |
| COM-001 | Gestionar estrategia comunicacional (web, RRSS)           | Alta      |
| COM-002 | Publicar noticias y comunicados oficiales                 | Alta      |
| COM-003 | Gestionar repositorio de material audiovisual             | Alta      |
| COM-004 | Monitoreo de medios y gestión de crisis de imagen         | Crítica   |
| COM-005 | Difusión de estado proyectos (mapa interactivo ciudadano) | Alta      |
| COM-006 | Gestión de comunicación interna (intranet/boletines)      | Alta      |

---

### M10. TIC — Infraestructura y Gobernanza Digital

**Journeys:** J12, J14, J15 | **Normas:** Ley 21.180, DS N°7-12

#### Infraestructura & Usuarios TI

| ID      | User Story                                                                                                          | Prioridad |
| ------- | ------------------------------------------------------------------------------------------------------------------- | --------- |
| tic-001 | Asignar equipamiento tecnológico con acta digital                                                                   | Alta      |
| tic-002 | Gestionar identidad digital (ClaveÚnica/SSO)                                                                        | Crítica   |
| tic-006 | Integrar ClaveÚnica (OIDC Authorization Code Flow) con `state`, token/userinfo desde backend                        | Crítica   |
| tic-007 | Gestionar credenciales ClaveÚnica por ambiente (sandbox/QA/producción) y custodia institucional                     | Alta      |
| tic-008 | Implementar cierre de sesión ClaveÚnica (logout) con URIs registradas                                               | Alta      |
| tic-009 | Registrar trazabilidad de accesos autenticados (DS9) con timestamp sincronizado a hora oficial                      | Alta      |
| tic-010 | Autenticación de personas jurídicas (Clave Tributaria o representante con ClaveÚnica)                               | Alta      |
| tic-011 | Prohibir mecanismos propios de autenticación para ciudadanía (cumplimiento DS9)                                     | Crítica   |
| tic-012 | Integrar Plataforma de Notificaciones del Estado (DS8) (vía web y/o API)                                            | Crítica   |
| tic-013 | Resolver DDU del destinatario (casilla/email/excepción/sin DDU) y aplicar canal correcto (DS8)                      | Crítica   |
| tic-014 | Enviar notificaciones vía API `/notificador/sendMessage` (DS8) **vía Nodo PISEE (DS12)** con validaciones y límites | Alta      |
| tic-015 | Consultar estado `/notificador/messageStatus/{message_data_id}` y/o webhook (DS8) **vía Nodo PISEE (DS12)**         | Alta      |
| tic-016 | Persistir constancia de notificación (`codigo_tx`, fechas, estado) y asociarla a IUIe (DS8/DS10)                    | Crítica   |
| tic-017 | Aplicar regla notificación practicada (3 días hábiles o lectura) y calcular vencimientos (DS8)                      | Alta      |
| tic-018 | Asegurar campos obligatorios DS8 (código OAE/Gestor Códigos, IUIe, CPAT)                                            | Alta      |
| tic-019 | Habilitar Nodo de Interoperabilidad PISEE (DS12) (dev/prod) y roles técnico/negocio                                 | Crítica   |
| tic-020 | Registrar/administrar servicios interoperables en Catálogo de Servicios (DS12)                                      | Alta      |
| tic-021 | Registrar trazabilidad central de transacciones interoperables (DS12) (campos mínimos)                              | Alta      |
| tic-022 | Gestionar acuerdos previos (Gestor de Acuerdos) antes de consumir servicios (DS12)                                  | Alta      |
| tic-023 | Gestionar consentimiento para datos sensibles (Gestor de Autorizaciones) (DS12)                                     | Alta      |
| tic-003 | Integrar DocDigital/FirmaGob                                                                                        | Crítica   |
| tic-004 | Alerta de ciberseguridad (CSIRT, Incidentes)                                                                        | Crítica   |
| tic-024 | Mantener Política de Seguridad de la Información (DS7) aprobada por acto administrativo                             | Crítica   |
| tic-025 | Designar y mantener Responsable de Seguridad (CISO) (DS7)                                                           | Crítica   |
| tic-026 | Clasificar activos de información según CIA (Confidencialidad/Integridad/Disponibilidad) (DS7)                      | Alta      |
| tic-027 | Reportar incidentes de seguridad a CSIRT MININT y ANCI (DS7)                                                        | Crítica   |
| tic-028 | Asegurar cifrado en tránsito (TLS 1.2+) y cifrado en reposo para datos sensibles (DS7)                              | Alta      |
| tic-029 | Mantener Catálogo de Plataformas con línea base por plataforma (DS11)                                               | Alta      |
| tic-030 | Elaborar Plan de Mejora Continua anual (diagnóstico/iniciativas/métricas/plazos) (DS11)                             | Alta      |
| tic-031 | Ejecutar Ciclo de Gestión de Calidad (Elaboración/Formulación/Implementación/Evaluación/Ajustes) (DS11)             | Alta      |
| tic-032 | Someter proyectos TIC con presupuesto a EvalTIC (gate) (DS11)                                                       | Alta      |
| tic-005 | Dashboard cumplimiento DS N°7-12                                                                                    | Alta      |

#### Gobernanza TDE (Transformación Digital) — **Integra UC-DPO/CISO/CTD**

#### Oficial de Seguridad Informática (CISO)

| ID      | User Story                                                                                     | Prioridad |
| ------- | ---------------------------------------------------------------------------------------------- | --------- |
| CISO-01 | **Gestionar Incidentes de Seguridad** (CSIRT)                                                  | Crítica   |
| CISO-02 | Configurar políticas de acceso y roles (IAM)                                                   | Crítica   |
| CISO-03 | Auditar logs de acceso a datos sensibles                                                       | Alta      |
| CISO-04 | Realizar simulaciones de Phishing y concientización                                            | Media     |
| CISO-05 | Auditar trazabilidad de accesos autenticados (DS9)                                             | Alta      |
| CISO-06 | Elaborar/actualizar Política de Seguridad de la Información (DS7) (ver `tic-024`)              | Crítica   |
| CISO-07 | Mantener inventario de activos y clasificación CIA (DS7) (ver `tic-026`)                       | Alta      |
| CISO-08 | Gestionar reporte inmediato de incidentes a CSIRT/ANCI (DS7) (ver `tic-027`)                   | Crítica   |
| CISO-09 | Verificar cumplimiento TLS 1.2+ y cifrado en reposo para datos sensibles (DS7) (ver `tic-028`) | Alta      |
| CISO-10 | Asegurar privacidad/seguridad por diseño en nuevas plataformas (DS7)                           | Alta      |

#### Delegado Protección de Datos (DPO)

| ID     | User Story                                                                              | Prioridad |
| ------ | --------------------------------------------------------------------------------------- | --------- |
| DPO-01 | **Gestionar Solicitudes ARCO** (Acceso, Rectificación, Cancelación, Oposición)          | Crítica   |
| DPO-02 | Mantener Inventario de Actividades de Tratamiento (IAT)                                 | Crítica   |
| DPO-03 | Notificar brechas de datos a la Agencia (Ley 21.719)                                    | Alta      |
| DPO-04 | Evaluar Impacto en Protección de Datos (EIPD) de nuevos proyectos                       | Alta      |
| DPO-05 | Mantener Registro de Actividades de Tratamiento (RAT) con campos mínimos (SGD)          | Crítica   |
| DPO-06 | Controlar ciclo de vida de datos personales: fuente, destinatarios y conservación (RAT) | Alta      |
| DPO-07 | Registrar versión y cambios del RAT (trazabilidad de actualizaciones)                   | Alta      |
| DPO-08 | Definir y aplicar anonimización/seudonimización antes de analítica/publicación          | Alta      |

##### DPO-05: Mantener RAT con campos mínimos (SGD)

> **Como** Delegado de Protección de Datos,  
> **Quiero** mantener un Registro de Actividades de Tratamiento (RAT) con campos mínimos exigidos por la normativa SGD,  
> **Para** cumplir con Ley 21.719 y demostrar accountability ante la Agencia de Protección de Datos.

**Campos mínimos RAT:**

* Nombre y datos de contacto del responsable
* Finalidades del tratamiento
* Descripción de categorías de interesados y datos
* Categorías de destinatarios (actuales o previstos)
* Transferencias internacionales (si aplica)
* Plazos previstos para supresión
* Descripción general de medidas de seguridad

**Criterios de Aceptación:**

* [ ] Sistema permite crear/editar registros RAT con todos los campos mínimos
* [ ] Validación impide guardar RAT incompleto
* [ ] Reporte exportable en formato interoperable (JSON/XML)

---

##### DPO-06: Controlar ciclo de vida de datos personales

> **Como** Delegado de Protección de Datos,  
> **Quiero** controlar el ciclo de vida de datos personales registrando fuente, destinatarios y plazos de conservación,  
> **Para** garantizar que los datos se eliminan al cumplir su finalidad y documentar las transferencias realizadas.

**Criterios de Aceptación:**

* [ ] Cada registro RAT incluye: `fuenteDatos` (origen), `destinatarios[]`, `plazosConservacion` (meses)
* [ ] Sistema alerta 30 días antes de vencimiento del plazo de conservación
* [ ] Log de auditoría registra transferencias a terceros con fecha/destinatario

---

##### DPO-07: Registrar versión y cambios del RAT (trazabilidad)

> **Como** Delegado de Protección de Datos,  
> **Quiero** registrar la versión y cambios del RAT con trazabilidad completa,  
> **Para** demostrar la evolución histórica del tratamiento ante auditorías o requerimientos de la Agencia.

**Criterios de Aceptación:**

* [ ] Cada modificación del RAT incrementa `version` y registra `fechaVersion`
* [ ] Sistema almacena historial de versiones con diff de cambios
* [ ] Reporte "Historial RAT" muestra línea de tiempo de modificaciones
* [ ] No se permite eliminar versiones anteriores (inmutabilidad)

---

##### DPO-08: Definir y aplicar anonimización/seudonimización

> **Como** Delegado de Protección de Datos,  
> **Quiero** definir y aplicar técnicas de anonimización o seudonimización antes de usar datos para analítica o publicación,  
> **Para** proteger la identidad de los titulares y cumplir el principio de minimización de datos.

**Técnicas soportadas:**

* **Seudonimización**: Reemplazo de identificadores por tokens reversibles (con clave)
* **Anonimización completa**: K-anonymity, generalización, supresión

**Criterios de Aceptación:**

* [ ] Campo `anonimizacion` en RAT con valores: `NINGUNA`, `SEUDONIMIZACION`, `ANONIMIZACION_COMPLETA`
* [ ] Dataset exportado para BI aplica técnica configurada en RAT
* [ ] Log registra qué técnica se aplicó, fecha y responsable
* [ ] Datos sensibles (Art. 16 Ley 21.719) requieren anonimización obligatoria para publicación

#### Coordinador Transformación Digital (CTD)

| ID     | User Story                                                                           | Prioridad |
| ------ | ------------------------------------------------------------------------------------ | --------- |
| CTD-01 | Monitorear índice de digitalización de trámites (cero papel)                         | Alta      |
| CTD-02 | Gestionar integraciones de interoperabilidad (Roadmap API)                           | Alta      |
| CTD-04 | Habilitar Nodo de Interoperabilidad PISEE (DS12) (ver `tic-019`)                     | Crítica   |
| CTD-05 | Gestionar catálogo de servicios de interoperabilidad (DS12) (ver `tic-020`)          | Alta      |
| CTD-06 | Asegurar trazabilidad central de transacciones interoperables (DS12) (ver `tic-021`) | Alta      |
| CTD-07 | Gestionar acuerdos previos para consumo de servicios (DS12) (ver `tic-022`)          | Alta      |
| CTD-08 | Gestionar autorizaciones/consentimientos datos sensibles (DS12) (ver `tic-023`)      | Alta      |
| CTD-03 | **Asegurar Expediente Electrónico (DS10)** como backbone transversal                 | Crítica   |
| CTD-09 | Mantener Catálogo de Plataformas con línea base (DS11) (ver `tic-029`)               | Alta      |
| CTD-10 | Elaborar Plan de Mejora Continua anual (DS11) (ver `tic-030`)                        | Alta      |
| CTD-11 | Ejecutar Ciclo de Gestión de Calidad (DS11) (ver `tic-031`)                          | Alta      |
| CTD-12 | Gobernar gate EvalTIC para proyectos TIC con presupuesto (DS11) (ver `tic-032`)      | Alta      |

| ID             | User Story                                                                                             | Prioridad |
| -------------- | ------------------------------------------------------------------------------------------------------ | --------- |
| CTD-01         | Avance TDE (% por componente e interoperabilidad)                                                      | Crítica   |
| CTD-03         | Expediente electrónico DS10 (IUIe/índice/metadatos/trazabilidad)                                       | Crítica   |
| CTD-02         | Interoperabilidad DS12 (Nodo/Servicios/Trazabilidad/Acuerdos/Consentimiento) (ver `tic-019`–`tic-023`) | Alta      |
| S-CTD-GORE-001 | Reporte adopción Plataforma Notificaciones (Municipios)                                                | Alta      |
| S-CTD-GORE-002 | Publicar esquema JSON interoperable (Estandarización)                                                  | Alta      |
| DPO-01         | Solicitudes ARCO (respuesta Ley 21.719)                                                                | Crítica   |
| DPO-02         | Impacto privacidad (informe riesgos)                                                                   | Alta      |
| CISO-01        | Estado seguridad (alertas, controles)                                                                  | Crítica   |
| PMOTIC-01      | Inventario proyectos TIC (estado, riesgos)                                                             | Alta      |

#### TDE: Casos de Uso Territoriales

| ID             | User Story                                                       | Actor              |
| -------------- | ---------------------------------------------------------------- | ------------------ |
| S-ALC-001      | Dashboard móvil "Fila de Espera" trámites                        | Alcalde Digital    |
| S-CTD-MUNI-001 | Conectar DIDECO con Registro Civil vía PISEE (DS12: ver M10 TIC) | Encargado TD Muni  |
| S-CTD-MUNI-002 | Habilitar Trámite Express para escalar servicios                 | Encargado TD Muni  |
| S-GOB-001      | Visualizar inversión per cápita en mapa regional                 | Gobernador Digital |

---

## DOMINIO I: ESPACIO TERRITORIAL

### M7. TERRITORIAL — Planificación y ERD

| ID           | User Story                                       | Prioridad |
| ------------ | ------------------------------------------------ | --------- |
| DIPL-001     | Brechas territoriales (brecha vs meta con mapa)  | Crítica   |
| DIPL-002     | Alineamiento IPR a ERD (score)                   | Crítica   |
| DIPL-003     | Avance metas ERD (tendencia, proyección)         | Alta      |
| DIPL-004     | Proceso ARI/PROPIR (convocar, revisar, aprobar)  | Alta      |
| GORE-AUTO-01 | Política Regional propia (instrumento normativo) | Alta      |
| GORE-AUTO-02 | Instrumentos planificación (seguimiento metas)   | Alta      |

#### Gestor Programas Públicos (GPP)

> **Nota:** Articula programas públicos vigentes con inversión regional.

| ID     | User Story                                                       | Prioridad |
| ------ | ---------------------------------------------------------------- | --------- |
| PRG-01 | **Mapear programas públicos vigentes** por beneficiario/objetivo | Alta      |
| PRG-02 | Identificar complementariedad entre programas y proyectos IDI    | Media     |
| PRG-03 | Alertar sobre ventanas de postulación a programas con plazos     | Media     |

### M8. CIES — Emergencia y Seguridad

> **Nota:** Integra UC-CIES-OP, UC-CIES-SUP, UC-CIES-ENL.

| ID          | User Story                                                | Prioridad |
| ----------- | --------------------------------------------------------- | --------- |
| CIES-OP-01  | Monitorear cámaras (detectar anomalía, activar protocolo) | Crítica   |
| CIES-OP-02  | Seguir trayectorias geoespaciales (mapa)                  | Alta      |
| CIES-SUP-01 | Gestión incidentes críticos (coordina Carabineros/PDI)    | Crítica   |
| CIES-SUP-02 | Activar contingencia (protocolos predefinidos)            | Crítica   |
| CIES-ENL-01 | Alertas y respuesta (confirmar en terreno)                | Alta      |

### M9. IDE — Infraestructura Geoespacial

> **Nota:** Integra UC-IDE (Coordinadores regionales).

| ID      | User Story                                     | Prioridad |
| ------- | ---------------------------------------------- | --------- |
| IDE-01  | Definir política geoespacial (documentada)     | Alta      |
| IDE-02  | Federar catálogos IDE Chile (CSW)              | Alta      |
| UGIT-01 | Modelar datos ISO 19110 (catálogo objetos)     | Alta      |
| UGIT-02 | Metadatos ISO 19115-1 (Perfil Chileno)         | Alta      |
| UGIT-03 | Publicar WMS/WFS/WCS (Geonodo)                 | Alta      |
| PFS-01  | Validar contenido temático (certifica calidad) | Alta      |

---

## DOMINIO III: TEJIDO NORMATIVO

### M11. CUMPLIMIENTO — Probidad y Transparencia

#### Jurídico (UC-JUR)

> **Nota:** Integra UC-JUR-01 a UC-JUR-33 (Actos 06-10, Asesoría 01-05/25-29, CGR 11-15, Litigios 16-20, Normativa 30-33).

| ID      | User Story                                               | Prioridad |
| ------- | -------------------------------------------------------- | --------- |
| JUR-001 | Gestión de actos administrativos (decretos/resoluciones) | Crítica   |
| JUR-002 | Asesoría legal y revisión de bases/convenios             | Crítica   |
| JUR-003 | Tramitación ante CGR (toma de razón)                     | Crítica   |
| JUR-004 | Gestión de litigios y defensa judicial regional          | Alta      |
| JUR-005 | Supervisar cumplimiento normativo (sumarios)             | Alta      |

#### Transparencia y Lobby (UC-TRANSP / UC-LOBBY)

| ID        | User Story                                      | Prioridad |
| --------- | ----------------------------------------------- | --------- |
| TRANSP-01 | Verificar transparencia activa mensual          | Alta      |
| TRANSP-02 | Gestionar solicitudes OIRS/SAI integradas       | Crítica   |
| TRANSP-03 | Gestión de amparos ante CPLT                    | Alta      |
| LOBBY-01  | Verificar registros audiencias y donativos      | Crítica   |
| LOBBY-02  | Coordinar nómina de sujetos pasivos             | Alta      |
| DIP-01    | Alerta vencimiento DIP (30 días antes de marzo) | Crítica   |

### M13. GOBIERNO CENTRAL — Control

| ID        | User Story                                         | Prioridad |
| --------- | -------------------------------------------------- | --------- |
| MDSF-01   | Recibir postulación IDI iniciando plazo evaluación | Crítica   |
| MDSF-02   | Emitir RATE (RS/FI/OT/AD) notificando GORE         | Crítica   |
| DIPSES-01 | Evaluar Formulario MML (RF o correcciones)         | Alta      |
| CGR-01    | Verificar rendiciones SISREC fiscalizando fondos   | Crítica   |
| CGR-02    | Fiscalizar DIP detectando incumplimientos          | Alta      |
| CPLT-01   | Requerir información amparo (plazo legal)          | Alta      |
| TCP-01    | Requerir expediente licitación                     | Alta      |

---

## M12. MUNICIPAL — Ejecución Local

> **Nota:** Integra UC-ALC y UC-CTD-MUNI.

| ID         | User Story                                                            | Prioridad |
| ---------- | --------------------------------------------------------------------- | --------- |
| UF-01      | Consultar guías por mecanismo                                         | Alta      |
| UF-02      | Wizard vía financiamiento (recomendación fundamentada)                | Crítica   |
| UF-03      | Verificar elegibilidad FRIL (<5000 UTM)                               | Crítica   |
| UTR-01     | Coordinar reunión inicio con supervisor                               | Alta      |
| UTR-02     | Reportar avance periódico (validación supervisor)                     | Crítica   |
| UTR-03     | Rendición final SISREC                                                | Crítica   |
| MUNI-TD-01 | Conectar DIDECO con Registro Civil (Interoperabilidad S-CTD-MUNI-001) | Alta      |
| MUNI-TD-02 | Habilitar Trámite Express para escalar servicios (S-CTD-MUNI-002)     | Alta      |
| S-ALC-002  | **Firma Masiva de Decretos** (FirmaGob Mobile Batch S-ALC-002)        | Crítica   |

---

## M14. SECTORIAL — Relaciones Institucionales

### Coordinación

| ID      | User Story                                 | Prioridad |
| ------- | ------------------------------------------ | --------- |
| sec-001 | Gestionar convenios sectoriales (marco)    | Alta      |
| sec-002 | Dashboard de relaciones sectoriales (mapa) | Alta      |

### Revisión RIS (Sector)

| ID          | User Story                                       | Prioridad |
| ----------- | ------------------------------------------------ | --------- |
| ris-dep-001 | IND: Evaluar proyecto deportivo (criterios CAE)  | Crítica   |
| ris-dep-002 | IND: Gestionar cartera deportiva por comuna      | Alta      |
| ris-cul-001 | MINCAP: Evaluar iniciativa cultural (política)   | Crítica   |
| ris-cul-002 | MINCAP: Gestión infraestructura cultural         | Alta      |
| ris-pat-001 | CMN: Gestionar trámite autorización (Ley 17.288) | Crítica   |
| ris-pat-002 | CMN: Alerta proyecto en zona patrimonial         | Alta      |

---

## DOMINIO II: AGENCIA INSTITUCIONAL

### M15. PERSONAS — Gestión del Talento

| Rol | ID         | User Story                                         | Prioridad   |
| --- | ---------- | -------------------------------------------------- | ----------- |
| FUN | per-001    | Visualizar ficha funcionario (hoja de vida)        | Crítica     |
| FUN | per-002    | Proceso de inducción digital (checklist)           | Alta        |
| FUN | per-003    | Solicitar feriado/permiso validando saldo          | Crítica     |
| FUN | per-004    | Declarar licencia médica (IMED/Medipass)           | Crítica     |
| FUN | per-005    | Solicitar permiso administrativo (máx 6 días/año)  | Alta        |
| FUN | per-006    | Visualizar liquidación de sueldo (PDF)             | Crítica     |
| FUN | per-007    | Solicitar certificado antigüedad/renta (FEA)       | Alta        |
|     | **FUNC-*** | *(Stories mirror: FUNC-AUS-01/02, FUNC-REM-01...)* | *Incluidas* |
| GDP | per-010    | Dashboard ausentismo por tipo y unidad             | Alta        |
| GDP | per-011    | Procesar licencias médicas (COMPIN/ISAPRE)         | Crítica     |
| GDP | per-012    | Calcular liquidaciones mensuales (EUS)             | Crítica     |
| GDP | per-013    | Generar planilla Previred                          | Crítica     |
| GDP | per-014    | Gestionar horas extraordinarias (F2)               | Alta        |
| GDP | per-015    | Gestionar cometidos funcionarios (viático)         | Alta        |
| GDP | per-016    | Registrar accidente trabajo (DIAT)                 | Crítica     |
| GDP | per-017    | Gestionar concursos públicos                       | Alta        |
| JC  | per-020    | Registrar precalificación (factores/sub)           | Crítica     |
| JC  | per-021    | Consolidar calificaciones (junta anual)            | Crítica     |
| JC  | per-022    | Notificar resultado calificación                   | Alta        |

### M16. ACTIVOS — Gestión de Recursos

#### Abastecimiento (ABS)

| ID         | User Story                                                  | Prioridad |
| ---------- | ----------------------------------------------------------- | --------- |
| ABS-COM-01 | Plan Anual de Compras (PAC) consolidado                     | Alta      |
| ABS-COM-02 | Tramitar solicitudes (verifica CDP)                         | Alta      |
| ABS-COM-03 | Publicar licitaciones (Mercado Público) (DS12: ver M10 TIC) | Crítica   |
| ABS-COM-04 | Evaluar ofertas (criterios técnico-económicos)              | Crítica   |
| ABS-COM-05 | Emitir OC (compromiso de gasto)                             | Crítica   |
| ABS-COM-06 | Gestionar contratos (hitos, garantías)                      | Alta      |

#### Contabilidad (CONT)

| ID      | User Story                                                                  | Prioridad |
| ------- | --------------------------------------------------------------------------- | --------- |
| CONT-01 | **Contabilizar devengado SISREC en SIGFE** (automático) (DS12: ver M10 TIC) | Crítica   |
| CONT-02 | Conciliar cartola bancaria con movimientos SISREC                           | Crítica   |
| CONT-03 | Emitir certificado de deuda flotante                                        | Alta      |

#### Tesorería (TES) y Activos Fijos (AF)

| ID         | User Story                                   | Prioridad |
| ---------- | -------------------------------------------- | --------- |
| ABS-BOD-01 | Registrar ingresos (aumenta stock)           | Crítica   |
| ABS-BOD-02 | Despachar solicitudes (disminuye stock, FEA) | Crítica   |
| ABS-BOD-03 | Inventario físico (ajustes diferencia)       | Alta      |
| ABS-AF-01  | Alta activo fijo (código, depreciación)      | Crítica   |
| ABS-AF-02  | Traslado bienes (cambio ubicación)           | Alta      |
| ABS-AF-03  | Baja bienes (resolución, causal)             | Alta      |
| ABS-AF-04  | Inventario anual AF                          | Alta      |

#### Servicios y Flota (FLO/MAN)

| ID         | User Story                                   | Prioridad |
| ---------- | -------------------------------------------- | --------- |
| ABS-MAN-01 | Órdenes trabajo mantención (asignar técnico) | Alta      |
| ABS-FLO-01 | Solicitudes vehículos (asignar conductor)    | Alta      |
| ABS-FLO-02 | Control km/combustible (bitácora)            | Alta      |

### M17. BIENESTAR — Calidad de Vida

#### Profesional (BIEN) y Socio (SOC)

| ID          | User Story                                         | Prioridad |
| ----------- | -------------------------------------------------- | --------- |
| BIEN-AF-01  | Registrar afiliaciones (socio con descuento)       | Alta      |
| BIEN-AF-02  | Gestionar grupo familiar (cargas)                  | Alta      |
| BIEN-BON-01 | Gestionar bonificación médica (tope anual, SIGBIE) | Alta      |
| BIEN-SUB-01 | Otorgar subsidios eventos (natalidad/pérdida)      | Media     |
| BIEN-PRE-01 | Evaluar préstamos (capacidad endeudamiento)        | Alta      |
| BIEN-PRE-02 | Descuento cuotas (automático planilla)             | Alta      |
| BIEN-CON-01 | Gestionar convenios terceros (farmacias, etc)      | Media     |
| BIEN-SSO-01 | Coordinar Mutual (accidente laboral)               | Crítica   |
| BIEN-SSO-02 | Apoyar CPHS (investigación accidentes)             | Alta      |
| SOC-BON-01  | Solicitar bonificación (adjuntar boletas)          | Alta      |
| SOC-PRE-01  | Solicitar préstamo (ver condiciones)               | Alta      |
| SOC-CTA-01  | Ver cuenta corriente bienestar (saldos)            | Alta      |

---

### M18. COMPETENCIAS — Desarrollo y Transferencia

| ID         | User Story                                              | Prioridad |
| ---------- | ------------------------------------------------------- | --------- |
| comp-001   | Plan Anual de Capacitación (PAC)                        | Alta      |
| comp-002   | Proceso de calificaciones Junta                         | Crítica   |
| comp-003   | Metas de desempeño (CDC/PMG)                            | Alta      |
| L4-COMP-01 | Monitorear estado transferencia sectorial (SUBDERE)     | Alta      |
| L4-COMP-02 | Preparar capacidades institucionales (RRHH/Presupuesto) | Alta      |
| L4-COMP-03 | Absorber competencia nueva (organigrama)                | Alta      |
| L4-COMP-04 | Evaluar brechas post-transferencia                      | Alta      |

---

### M19. EVOLUCIÓN — Gestión del Sistema

| ID         | User Story                                         | Prioridad |
| ---------- | -------------------------------------------------- | --------- |
| HO-EVO-001 | Dashboard de salud del sistema (H_org)             | Crítica   |
| HO-EVO-002 | Declarar cambio de Estado de Salud (Gate)          | Crítica   |
| HO-EVO-003 | Simular impacto de configuración (What-if)         | Alta      |
| TO-EVO-001 | Configurar trayectoria del sistema (Feature Flags) | Alta      |
| TO-EVO-002 | Ajustar umbrales de riesgo                         | Alta      |
| TO-EVO-003 | Revisar reporte de brechas de capacidad            | Alta      |
| TL-EVO-001 | Activar pilotos de autonomía (M6)                  | Alta      |
| TL-EVO-002 | Escalar configuración a nueva división             | Alta      |
| TL-EVO-003 | Crear retrospectiva de sistema                     | Alta      |
| PL-EVO-001 | Ejecutar playbook de remediación                   | Alta      |
| PL-EVO-002 | Monitor de progreso de playbooks                   | Alta      |
| CAP-EVO-01 | Aprobar cambios críticos (Gobierno)                | Crítica   |
| CAP-EVO-02 | Arbitraje de prioridades (RICE)                    | Alta      |
| EVOL-01    | Gestionar deuda técnica (inventario)               | Alta      |
| EVOL-02    | Planificar evolución schema (migraciones)          | Alta      |
| EVOL-03    | Monitorear KPIs sistema (técnicos)                 | Crítica   |

---

## DOMINIO V: MARCO LEGAL Y GOBIERNO

### M27. Gobierno Interior y Descentralización

**Objetivo**: Coordinar la acción del gobierno interior y gestionar la transferencia de competencias.

#### Delegado Presidencial Regional (DPR)

| ID      | User Story                                                                                       | Prioridad |
| ------- | ------------------------------------------------------------------------------------------------ | --------- |
| DEL-001 | **Coordinar Gabinete Regional**: Convocar a SEREMIS para alineamiento de políticas               | Alta      |
| DEL-002 | **Resolver Recursos Jerárquicos**: Decidir sobre impugnaciones a actos de Delegados Provinciales | Media     |
| DEL-004 | **Articular demanda regional**: Definir prioridades de inversión sectorial con Gobernador        | Alta      |

#### Delegado Presidencial Provincial (DPP)

| ID      | User Story                                                                 | Prioridad |
| ------- | -------------------------------------------------------------------------- | --------- |
| DEL-003 | **Gestión Orden Público**: Autorizar reuniones y coordinar con Carabineros | Alta      |

#### Gobernador Regional (Competencias)

| ID     | User Story                                                                            | Prioridad |
| ------ | ------------------------------------------------------------------------------------- | --------- |
| TC-001 | **Solicitar Transferencia**: Presentar expediente fundado al CORE para aprobación     | Alta      |
| TC-002 | **Negociar Transferencia**: Representar a la región ante Comité Interministerial      | Crítica   |
| TC-004 | **Evaluar Competencia**: Monitorear indicadores de desempeño de servicios traspasados | Alta      |

### M28. Control, Probidad y Transparencia

**Objetivo**: Asegurar el cumplimiento normativo, la probidad administrativa y el acceso a la información.

#### Contraloría General (CGR) - Externo

| ID      | User Story                                                                                           | Prioridad |
| ------- | ---------------------------------------------------------------------------------------------------- | --------- |
| PRO-002 | **Toma de Razón Digital**: Recibir actos administrativos y emitir pronunciamiento (SIAPER/SISTRADOC) | Crítica   |

#### Unidad de Control Interno (UCI)

| ID      | User Story                                                                                     | Prioridad |
| ------- | ---------------------------------------------------------------------------------------------- | --------- |
| PRO-001 | **Monitoreo DIP**: Verificar cumplimiento de declaraciones de patrimonio de funcionarios       | Alta      |
| PRO-003 | **Alerta Conflicto Interés**: Recibir notificaciones de cruces entre evaluadores y postulantes | Crítica   |
| PRO-004 | **Auditoría de Procesos**: Revisar muestreo de adjudicaciones y pagos                          | Alta      |

#### Fiscal Sumariante

| ID      | User Story                                                                    | Prioridad |
| ------- | ----------------------------------------------------------------------------- | --------- |
| PRO-004 | **Instruir Sumario**: Gestionar expediente disciplinario con reserva y plazos | Media     |

#### Encargado de Transparencia

| ID        | User Story                                                                     | Prioridad |
| --------- | ------------------------------------------------------------------------------ | --------- |
| TRANS-002 | **Gestión Solicitudes SAI**: Responder en 20 días hábiles vía portal unificado | Crítica   |
| TRANS-003 | **Gestión Amparos CPLT**: Preparar descargos ante reclamos de denegación       | Alta      |

#### Consejo para la Transparencia (CPLT) - Externo

| ID        | User Story                                                       | Prioridad |
| --------- | ---------------------------------------------------------------- | --------- |
| TRANS-003 | **Notificar Amparo**: Informar al GORE sobre reclamos admisibles | Alta      |

### M29. Gestión del Riesgo de Desastres (GRD)

**Objetivo**: Planificar y coordinar la reducción de riesgos y respuesta a emergencias.

#### Comité Regional GRD

| ID      | User Story                                                                                  | Prioridad |
| ------- | ------------------------------------------------------------------------------------------- | --------- |
| GRD-001 | **Aprobar Plan RRD**: Sancionar el Plan Regional de Reducción del Riesgo                    | Alta      |
| GRD-003 | **Vincular GRD-PROT**: Asegurar coherencia entre mapas de riesgo y ordenamiento territorial | Crítica   |

#### Director Regional SENAPRED

| ID      | User Story                                                                 | Prioridad |
| ------- | -------------------------------------------------------------------------- | --------- |
| GRD-002 | **Elaborar Plan Emergencia**: Diseñar protocolos de respuesta y evacuación | Alta      |

#### Gobernador Regional (GRD)

| ID      | User Story                                                                 | Prioridad |
| ------- | -------------------------------------------------------------------------- | --------- |
| GRD-004 | **Presidir Comité (Mitigación)**: Liderar sesiones de inversión preventiva | Alta      |

---

## DOMINIO VI: SEGURIDAD Y TERRITORIO INTELIGENTE

### M30. CIES & SITIA (Operaciones de Seguridad)

**Objetivo**: Gestionar la operación del Centro Integrado de Emergencia, vigilancia tecnológica y evidencia digital.

#### Operador CIES / Analista Videowall

| ID          | User Story                                                                                                    | Prioridad |
| ----------- | ------------------------------------------------------------------------------------------------------------- | --------- |
| CIES-OP-001 | **Gestionar Incidente**: Registrar alertas de cámaras, sensores o llamados (tipo, georreferencia)             | Crítica   |
| CIES-OP-002 | **Control PTZ**: Tomar control manual de cámara prioritaria ante incidente flagrante                          | Crítica   |
| CIES-OP-003 | **Alerta LPR/Prófugos**: Recibir notificación automática de pórticos (patente robada) o reconocimiento facial | Crítica   |
| CIES-OP-004 | **Bitácora Digital**: Registrar acciones tomadas secuencialmente (despacho móviles, cierre visual)            | Alta      |

#### Supervisor CIES

| ID           | User Story                                                                                    | Prioridad |
| ------------ | --------------------------------------------------------------------------------------------- | --------- |
| CIES-SUP-001 | **Gestión Sala Crisis**: Asignar roles y escenarios en Videowall durante emergencia mayor     | Crítica   |
| CIES-SUP-002 | **Derivación Multi-Agencia**: Despachar incidente a Carabineros/Bomberos/SAMU según protocolo | Alta      |
| CIES-SUP-003 | **Reporte Operativo**: Generar estadística de incidentes/horarios/zonas calientes             | Alta      |

#### Custodio de Evidencia (SITIA-Evidencia)

| ID            | User Story                                                                                       | Prioridad |
| ------------- | ------------------------------------------------------------------------------------------------ | --------- |
| CIES-EVID-001 | **Extracción Segura**: Generar clip de video con marca de agua y hash de integridad              | Crítica   |
| CIES-EVID-002 | **Compartir con Fiscalía**: Habilitar link seguro (Genetec Clearance) por oficio judicial        | Crítica   |
| CIES-EVID-003 | **Cadena de Custodia**: Trazar quién accedió, visualizó o descargó evidencia (Logs inalterables) | Crítica   |

### M31. Infraestructura de Datos Espaciales (IDE Regional)

**Objetivo**: Gobernar, estandarizar y publicar información territorial oficial del GORE (Geonodo).

#### Administrador Geonodo (UGIT)

| ID          | User Story                                                                            | Prioridad |
| ----------- | ------------------------------------------------------------------------------------- | --------- |
| IDE-ADM-001 | **Publicar Capa WMS/WFS**: Cargar shapefile/geopackage y exponer como servicio OGC    | Crítica   |
| IDE-ADM-002 | **Gestión Metadatos**: Completar ficha ISO 19115 mínima (título, linaje, responsable) | Crítica   |
| IDE-ADM-003 | **Federar Catálogos**: Configurar cosecha (harvesting) CSW desde nodos ministeriales  | Alta      |

#### Coordinador Regional IDE

| ID            | User Story                                                                                | Prioridad |
| ------------- | ----------------------------------------------------------------------------------------- | --------- |
| IDE-COORD-001 | **Dashboard de Calidad**: Visualizar % de capas con metadatos completos y actualizados    | Alta      |
| IDE-COORD-002 | **Gestión Usuarios**: Asignar permisos a Puntos Focales sectoriales (Edición/Publicación) | Alta      |

#### Punto Focal Sectorial

| ID           | User Story                                                                              | Prioridad |
| ------------ | --------------------------------------------------------------------------------------- | --------- |
| IDE-SECT-001 | **Actualizar Capa Temática**: Subir nueva versión de datos de su competencia (ej. APRs) | Alta      |

---

## DOMINIO VII: GESTIÓN ADMINISTRATIVA (AMPLIADO)

### M32. Gestión Administrativa y Jurídica

**Objetivo**: Asegurar la legalidad y formalidad de los actos administrativos del GORE (BPMN detallado).

#### Abogado Unidad Jurídica

| ID          | User Story                                                                                      | Prioridad |
| ----------- | ----------------------------------------------------------------------------------------------- | --------- |
| ADM-JUR-001 | **Revisión Legal**: Visar borrador de acto administrativo (check de atribuciones y presupuesto) | Crítica   |
| ADM-JUR-002 | **Observar Acto**: Devolver trámite con observaciones jurídicas para corrección                 | Alta      |

#### Centro de Gestión / Oficina de Partes

| ID           | User Story                                                                            | Prioridad |
| ------------ | ------------------------------------------------------------------------------------- | --------- |
| ADM-GEST-001 | **Numerar y Fechar**: Asignar folio único a Resolución/Decreto tras total tramitación | Crítica   |
| ADM-GEST-002 | **Distribución**: Notificar digitalmente a interesados y publicar en Transparencia    | Alta      |
| ADM-GEST-003 | **Control de Plazos**: Alerta de actos pendientes de firma > 5 días                   | Media     |

#### Ministro de Fe (Actos Admin)

| ID          | User Story                                                                     | Prioridad |
| ----------- | ------------------------------------------------------------------------------ | --------- |
| ADM-MFE-001 | **Certificar Copia Fiel**: Generar copia auténtica digital de actos originales | Alta      |

---
