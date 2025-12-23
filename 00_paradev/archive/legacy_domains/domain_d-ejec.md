# D-EJEC: Dominio de Ejecución y Seguimiento

> Parte de: [GORE_OS Vision General](../vision_general.md)  
> Capa: Núcleo (Dimensión Táctica)  
> Función GORE: EJECUTAR  

---

## Glosario D-EJEC

| Término  | Definición                                                                                                              |
| -------- | ----------------------------------------------------------------------------------------------------------------------- |
| Convenio | Acto administrativo formal que establece obligaciones entre GORE y un ejecutor. SADV (Fuente Única de Verdad) en D-NORM |
| Ejecutor | Actor habilitado para materializar proyectos. Ver D-GOB.Actor                                                           |
| PMO      | Oficina de Gestión de Proyectos (Project Management Office). Torre de control de proyectos regional                     |
| EP       | Estado de Pago. Documento que autoriza transferencia parcial o final                                                    |
| UT       | Unidad Técnica. Equipo ejecutor responsable de la obra                                                                  |
| UJ       | Unidad Jurídica. Área encargada de visación de actos administrativos                                                    |
| DIPIR    | División de Presupuesto e Inversión Regional                                                                            |
| ARI      | Anteproyecto Regional de Inversión. Priorización anual de IPR                                                           |
| IPR      | Iniciativa/Proyecto Regional. Ver D-FIN                                                                                 |
| H_org    | Panel de Salud Organizacional. Ver D-EVOL                                                                               |
| FÉNIX    | Sistema de intervención para proyectos críticos. Ver fenix.md                                                           |
| SISREC   | Sistema de Rendición de Cuentas **CGR** (Contraloría General de la República)                                           |
| FRIL     | Fondo Regional de Iniciativa Local                                                                                      |
| DAF      | División de Administración y Finanzas                                                                                   |

---

## Propósito

Gestionar la materialización de las iniciativas de inversión a través de convenios, supervisión de obras y seguimiento de compromisos, asegurando el cumplimiento de plazos, costos y alcance.

> Principio Núcleo: D-EJEC es el dominio de *ejecución operativa*. Consume definiciones formales de D-NORM (Convenio) y D-FIN (IPR), y produce información de avance para el Panel de Salud Organizacional (H_org) en D-EVOL.

---

## Módulos

### 1. Supervisión de Obras

Funcionalidades:

- Carpeta de seguimiento por IPR (visitas, informes)
- Registro de visitas a terreno con fotos geolocalizadas
- Revisión de informes de Unidad Técnica
- **Control Normativo Circular 33** (para adquisición de equipamiento y vehículos)
- Gestión de estados de pago
- Alertas de desviaciones >10%
- Validación de actas de recepción

> **⚠️ Triángulo de Integración Presupuestaria**:
> 1. D-EJEC **valida técnicamente** el Estado de Pago (EP) basado en avance físico
> 2. EP aprobado se envía a [D-BACK (Contabilidad)](domain_d-back.md#contabilidad-operativa) para Devengo → Pago
> 3. D-FIN **consume** el % de ejecución presupuestaria como indicador de SaludIPR

### 2. Gestión de Convenios

> Nota de Diseño: La entidad `Convenio` (SADV) se define en D-NORM. D-EJEC gestiona la *ejecución operativa* (hitos, pagos, riesgos).

Tipos de Convenio: (→ Ver D-NORM para definición formal)

| Tipo          | Descripción                                  | Ejemplo                       |
| ------------- | -------------------------------------------- | ----------------------------- |
| MANDATO       | GORE encarga ejecución a otro órgano         | MOP ejecuta obra vial         |
| TRANSFERENCIA | GORE transfiere recursos a ejecutor          | Municipio ejecuta multicancha |
| COLABORACIÓN  | Ejecución conjunta con aportes de ambos      | GORE+CORFO programa fomento   |
| MARCO         | Convenio paraguas para múltiples iniciativas | Marco con universidad         |
| PROGRAMACIÓN  | Convenio plurianual con Ministerio           | CP de infraestructura con MOP |

Ciclo de Vida:

```text
ELABORACIÓN → REVISIÓN JURÍDICA → FIRMA → EJECUCIÓN → LIQUIDACIÓN
```

Estados:

- BORRADOR → EN_REVISION_JURIDICA → PARA_FIRMA → VIGENTE
- PRORROGA_SOLICITADA, ADDENDUM_EN_PROCESO
- TERMINADO → LIQUIDADO
- CADUCADO

### 3. PMO Regional (Torre de Control)

Dimensiones de Monitoreo:

| Tiempo           | Costo                    | Alcance                   | Riesgo         |
| ---------------- | ------------------------ | ------------------------- | -------------- |
| % avance vs plan | Presupuesto vs ejecución | Cambios de especificación | Identificación |
| Hitos cumplidos  | Desvío %                 | EP estados                | Matriz riesgos |

Semáforo de Proyecto:

| Semáforo   | Condición                    | Acción                       |
| ---------- | ---------------------------- | ---------------------------- |
| 🟢 VERDE    | Conforme a plan (±5%)        | Monitoreo normal             |
| 🟡 AMARILLO | Desviación menor (5-15%)     | Seguimiento reforzado        |
| 🔴 ROJO     | Desviación crítica (>15%)    | Candidato FÉNIX Nivel II-III |
| ⚫ NEGRO    | Proyecto detenido/suspendido | Activación FÉNIX Nivel I-II  |

> Ver: [fenix.md](fenix.md) para detalle de niveles de intervención.

### 4. Gestión de Compromisos

Actores:

- Administrador Regional
- Jefaturas de División
- Encargados Operativos

Funcionalidades:

- Panel ejecutivo con alertas
- Creación y asignación de compromisos
- Seguimiento con semáforo de vencimiento
- **Validación de Percepción Ciudadana**: Registro de feedback social durante la obra.
- Reportes semanales automáticos

### 5. Coordinación Municipal

Funcionalidades:

- Guías por mecanismo de financiamiento
- Asistente (Wizard) de vía de financiamiento
- Verificación de elegibilidad FRIL
- Reuniones de inicio con supervisor
- Reportes de avance periódicos
- Rendición final SISREC

### 6. Relaciones Sectoriales

Funcionalidades:

- Gestión de convenios marco sectoriales
- Panel de relaciones sectoriales
- Coordinación con ministerios

---

## 📋 Procesos BPMN

### Mapa General D-EJEC

```mermaid
flowchart TB
    subgraph CONVENIOS["📋 Gestión de Convenios"]
        C1["P1: Elaboración y<br/>Firma de Convenio"]
        C2["P2: Ejecución y<br/>Estados de Pago"]
    end

    subgraph SUPERVISION["🔍 Supervisión"]
        S1["P3: Supervisión de<br/>Obra en Terreno"]
    end

    subgraph CIERRE["✅ Cierre"]
        X1["P4: Cierre y<br/>Liquidación"]
    end

    C1 --> C2
    C2 --> S1
    S1 --> C2
    C2 --> X1
```

---

### P1: Elaboración y Firma de Convenio

```mermaid
flowchart TD
    A["IPR aprobada<br/>(D-FIN)"] --> B["Elaborar borrador<br/>convenio"]
    B --> C["Revisión técnica<br/>DIPIR"]
    C --> D["Revisión jurídica<br/>UJ"]
    D --> E{"¿Observaciones?"}
    E -->|"Sí"| F["Corregir borrador"]
    F --> D
    E -->|"No"| G["V°B° jurídico"]
    G --> H["Generar decreto<br/>aprobatorio"]
    H --> I["Firma Gobernador"]
    I --> J["Firma Ejecutor"]
    J --> K["Convenio VIGENTE"]
    K --> L["Notificar a<br/>D-FIN para Compromiso"]
```

---

### P2: Ejecución y Estados de Pago

```mermaid
flowchart TD
    A["Convenio vigente"] --> B["Transferencia<br/>anticipo (si aplica)"]
    B --> C["Ejecutor inicia<br/>ejecución"]
    C --> D["UT reporta<br/>avance periódico"]
    D --> E["Supervisor revisa<br/>informe"]
    E --> F{"¿Conforme?"}
    F -->|"No"| G["Devolver con<br/>observaciones"]
    G --> D
    F -->|"Sí"| H["Aprobar informe"]
    H --> I["Generar Estado<br/>de Pago"]
    I --> J["Validación DAF & Rendición SISREC (si aplica)"]
    J --> K["Autorizar pago<br/>(D-FIN)"]
    K --> L{"¿Último EP?"}
    L -->|"No"| D
    L -->|"Sí"| M["Iniciar cierre"]
```

---

### P3: Supervisión de Obra en Terreno

```mermaid
flowchart TD
    A["Programar visita<br/>a terreno"] --> B["Realizar visita<br/>con GPS/fotos"]
    B --> C["Registrar hallazgos<br/>en sistema"]
    C --> D{"¿Desviación<br/>detectada?"}
    D -->|"No"| E["Actualizar %<br/>avance físico"]
    D -->|"Sí >10%"| F["Generar alerta<br/>automática"]
    F --> G{"¿Crítico?"}
    G -->|"Sí"| H["Activar FÉNIX<br/>Nivel I-II"]
    G -->|"No"| I["Notificar a<br/>Jefatura División"]
    I --> J["Gestionar<br/>mitigación"]
    E --> K["Actualizar<br/>PMO Regional"]
    H --> K
    J --> K
```

---

### P4: Cierre y Liquidación de Convenio

```mermaid
flowchart TD
    A["Último EP<br/>aprobado"] --> B["Solicitar acta<br/>recepción provisoria"]
    B --> C["Visita final<br/>de inspección"]
    C --> D{"¿Conforme?"}
    D -->|"No"| E["Registrar<br/>observaciones"]
    E --> F["Ejecutor corrige"]
    F --> C
    D -->|"Sí"| G["Firmar acta<br/>recepción"]
    G --> H["Liberar garantías<br/>(boletas)"]
    H --> I["Generar resolución<br/>de liquidación"]
    I --> J["Archivar expediente"]
    J --> K["Convenio LIQUIDADO"]
    K --> L["Notificar a<br/>D-FIN cierre"]
```

---

> **Umbrales sin Reevaluación MDSyF** (Glosa 01, Circular 11):
> - Incremento costo total proyecto: hasta 10%, tope 7.000 UTM
> - Adjudicación sobre monto recomendado: hasta 10%, tope 7.000 UTM
> - Si excede estos límites: requiere reevaluación MDSyF y nuevo acuerdo CORE obligatorio.

## 📝 Historias de Usuario por Módulo

### Catálogo por Módulo

#### Supervisión

| ID              | Título                    | Prioridad |
| --------------- | ------------------------- | --------- |
| US-EJEC-SUP-001 | Crear carpeta seguimiento | Crítica   |
| US-EJEC-SUP-002 | Registrar visitas terreno | Crítica   |
| US-EJEC-SUP-003 | Revisar informes UT       | Crítica   |
| US-EJEC-SUP-004 | Gestionar estados de pago | Crítica   |
| US-EJEC-SUP-005 | Alertar desviaciones      | Alta      |
| US-EJEC-SUP-006 | Validar actas recepción   | Alta      |

#### Administrador Regional

| ID             | Título                            | Prioridad |
| -------------- | --------------------------------- | --------- |
| US-EJEC-AR-001 | Panel ejecutivo AR                | Crítica   |
| US-EJEC-AR-002 | Monitor proyectos alerta crítica  | Crítica   |
| US-EJEC-AR-003 | Compromisos vencidos por división | Crítica   |
| US-EJEC-AR-004 | Crear compromiso en reunión       | Crítica   |
| US-EJEC-AR-005 | Verificar compromisos completados | Crítica   |
| US-EJEC-AR-006 | Resumen semanal Gobernador        | Crítica   |
| US-EJEC-AR-007 | Reasignar compromisos             | Alta      |
| US-EJEC-AR-008 | Reabrir compromiso devuelto       | Alta      |
| US-EJEC-AR-009 | Monitor problemas escalados       | Crítica   |

#### Jefatura División

| ID             | Título                           | Prioridad |
| -------------- | -------------------------------- | --------- |
| US-EJEC-JD-001 | Métricas división                | Crítica   |
| US-EJEC-JD-002 | Crear compromiso y asignar       | Crítica   |
| US-EJEC-JD-003 | Registrar problema IPR           | Crítica   |
| US-EJEC-JD-004 | Cerrar problema resuelto         | Alta      |
| US-EJEC-JD-005 | Filtrar compromisos por estado   | Alta      |
| US-EJEC-JD-006 | Validar compromisos completados  | Crítica   |
| US-EJEC-JD-007 | Reportes divisionales periódicos | Alta      |

#### Encargado Operativo

| ID             | Título                             | Prioridad |
| -------------- | ---------------------------------- | --------- |
| US-EJEC-EO-001 | Lista compromisos con semáforo     | Crítica   |
| US-EJEC-EO-002 | Marcar en progreso                 | Crítica   |
| US-EJEC-EO-003 | Marcar completado                  | Crítica   |
| US-EJEC-EO-004 | Registrar problema detectado       | Alta      |
| US-EJEC-EO-005 | Solicitar extensión plazo          | Alta      |
| US-EJEC-EO-006 | Ver historial del compromiso       | Media     |
| US-EJEC-EO-007 | Recibir notificaciones vencimiento | Alta      |

#### Municipal

| ID               | Título                        | Prioridad |
| ---------------- | ----------------------------- | --------- |
| US-EJEC-MUNI-001 | Consultar guías por mecanismo | Alta      |
| US-EJEC-MUNI-002 | Wizard vía financiamiento     | Crítica   |
| US-EJEC-MUNI-003 | Coordinar reunión inicio      | Alta      |
| US-EJEC-MUNI-004 | Reportar avance periódico     | Crítica   |
| US-EJEC-MUNI-005 | Verificar elegibilidad FRIL   | Alta      |
| US-EJEC-MUNI-006 | Rendición final SISREC        | Crítica   |

#### Sectorial y Comunicaciones

| ID              | Título                          | Prioridad |
| --------------- | ------------------------------- | --------- |
| US-EJEC-SEC-001 | Gestionar convenios sectoriales | Alta      |
| US-EJEC-SEC-002 | Panel de relaciones sectoriales | Alta      |
| US-EJEC-PER-001 | Cubrir hito comunicacional obra | Alta      |
| US-EJEC-PER-002 | Entrevistar beneficiarios       | Media     |

#### Ejecución (Ejecutor/Rendición)

| ID               | Título                       | Prioridad |
| ---------------- | ---------------------------- | --------- |
| US-EJEC-EJEC-001 | Ingresar transacciones       | Alta      |
| US-EJEC-EJEC-002 | Certificar autenticidad      | Crítica   |
| US-EJEC-EJEC-003 | Devolver a analista          | Alta      |
| US-EJEC-EJEC-004 | Crear informe regularización | Alta      |

---

## Entidades de Datos

### Ejecución de Convenios

| Entidad                | Atributos Clave                                                                            | Relaciones                                        |
| ---------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| `HitoConvenio`         | id, convenio_id, descripcion, fecha_compromiso, fecha_real, estado                         | → Convenio (D-NORM)                               |
| `EstadoPago`           | id, convenio_id, numero, monto, fecha_solicitud, fecha_aprobacion, estado                  | → Convenio (D-NORM)                               |
| `Riesgo`               | id, convenio_id, descripcion, probabilidad, impacto, mitigacion, estado                    | → Convenio (D-NORM)                               |
| `VisitaTerreno`        | id, convenio_id, fecha, inspector_id, hallazgos, fotografias[], ubicacion_gps, estado      | → Convenio, Funcionario, CapaGeoespacial (D-TERR) |
| `BitacoraObra`         | id, convenio_id, fecha_hora, tipo_evento, descripcion, adjuntos[]                          | → Convenio                                        |
| `ActaRecepcion`        | id, convenio_id, tipo (PARCIAL/DEFINITIVA), fecha, observaciones, conformidad, firmantes[] | → Convenio, ActoAdministrativo (D-NORM)           |
| `ModificacionConvenio` | id, convenio_id, tipo (ADDENDUM/PRORROGA/CAMBIO_MONTO), justificacion, acto_id, fecha      | → Convenio (D-NORM)                               |
| `InformeAvance`        | id, convenio_id, periodo, avance_fisico_pct, avance_financiero_pct, observaciones          | → Convenio (D-NORM)                               |
| `GarantiaConvenio`     | id, convenio_id, tipo (BOLETA/POLIZA), numero, entidad_emisora, monto, fecha_vencimiento   | → Convenio (D-NORM)                               |

### Gestión de Compromisos

| Entidad       | Atributos Clave                                                                       | Relaciones                 |
| ------------- | ------------------------------------------------------------------------------------- | -------------------------- |
| `Compromiso`  | id, descripcion, ipr_id, responsable_id, fecha_creacion, fecha_limite, estado, origen | → IPR (D-FIN), Funcionario |
| `ProblemaIPR` | id, ipr_id, tipo, descripcion, solucion_propuesta, fecha_registro, estado             | → IPR (D-FIN), Funcionario |

---

## Sistemas Involucrados

| Sistema      | Función                      | Integración             |
| ------------ | ---------------------------- | ----------------------- |
| `SYS-SISREC` | Rendición de cuentas SUBDERE | Rendiciones municipales |
| `SYS-SIGFE`  | Contabilización pagos        | Estados de pago         |
| `INT-PMO`    | Torre de control             | Panel regional          |
| `SYS-GPS`    | Geolocalización visitas      | Fotos geolocalizadas    |

---

## Normativa Aplicable

| Norma            | Alcance                      |
| ---------------- | ---------------------------- |
| Ley 19.175       | Orgánica Regional, convenios |
| D.S. 148         | Reglamento convenios GORE    |
| Ley 19.886       | Contratos públicos           |
| Res. CGR 30/2015 | Rendición de cuentas         |

---

## Referencias Cruzadas

| Dominio | Relación                                         | Entidades Compartidas        |
| ------- | ------------------------------------------------ | ---------------------------- |
| D-PLAN  | IPR priorizadas en ARI se ejecutan vía convenios | IPR, ObjetivoERD             |
| D-NORM  | Convenio (SADV del acto administrativo)          | Convenio, ActoAdministrativo |
| D-FIN   | IPR, Transferencias, Calificación Ejecutores     | IPR, CDP, Transferencia      |
| D-BACK  | EP aprobado → Devengo → Pago (cadena contable)   | EstadoPago, Devengo, Pago    |
| D-GOB   | Actor (entidad base del ejecutor)                | Actor.tipo=EJECUTOR          |
| D-TERR  | Geolocalización de obras en ejecución            | CapaGeoespacial, Ubicacion   |
| D-EVOL  | Indicadores de ejecución para H_org              | Metrica, Alerta              |
| D-SEG   | PMO para proyectos de seguridad                  | Proyecto_Seguridad           |
---

## Roles Asociados (SSOT: inventario_roles_v8.yml)

| Role Key               | Título             | Unidad     |
| ---------------------- | ------------------ | ---------- |
| jefe_dipir             | Jefe DIPIR         | DIPIR      |
| jefe_dit               | Jefe DIT           | DIT        |
| analista_inversion     | Analista Inversión | DIPIR      |
| inspector_fiscal       | Inspector Fiscal   | DIPIR      |
| inspector_tecnico_obra | ITO                | DIT        |
| ito_campo              | ITO Campo          | DIT        |
| supervisor_obras       | Supervisor Obras   | DIT        |
| unidad_tecnica         | Unidad Técnica     | Municipios |
| alcalde                | Alcalde            | Municipios |
| secpla                 | SECPLA             | Municipios |
| entidad_ejecutora      | Entidad Ejecutora  | Externos   |

---

## Capability Bundles (SSOT: historias_usuarios_v2.yml)

### CAP-EJEC-SEG-001: Seguimiento de Proyectos (P0)

> **Como** Jefe DIPIR  
> **Quiero** un semáforo de estado de la cartera de inversión con filtros por tipo  
> **Para** priorizar la gestión de proyectos críticos

| Atributo      | Valor                                                          |
| ------------- | -------------------------------------------------------------- |
| Beneficiarios | 30 roles                                                       |
| Criterios     | Estado (Formulación/Ejecución/Terminado), Semáforo, Drill-down |

### CAP-EJEC-PORTAL-001: Portal de Postulación FNDR (P1)

> **Como** Consejero Regional  
> **Quiero** un portal con historial de mis votaciones y asistencias  
> **Para** rendir cuenta a mis representados

| Atributo      | Valor                                                   |
| ------------- | ------------------------------------------------------- |
| Beneficiarios | 24 roles                                                |
| Criterios     | Historial votaciones, Registro asistencia, Certificados |

---

## Catálogo Completo de Historias (SSOT)

> Fuente: `historias_usuarios_v2.yml` | Filtro: `target_domain: D-EJEC`  
> Total: 63 historias

| ID | Role | Descripción | P |
|-----|------|-------------|---|
| CAP-EJEC-PORTAL-001 | Consejero Regional | un portal de consejeros con historial de mis votac... | P1 |
| CAP-EJEC-SEG-001 | Jefe DIPIR | un semáforo de estado de la cartera de inversión c... | P0 |
| US-ACONV-001-01 | analista_convenios | un workflow de convenios con checklist de requisit... | P0 |
| US-AEVAL-001-01 | analista_evaluacion | una ficha de evaluación con criterios estándar... | P0 |
| US-ALC-001-02 | alcalde | consultar el calendario de llamados y fondos dispo... | P0 |
| US-ALC-CHI-001-01 | Alcalde de Chillán | ver el estado de todos los proyectos de mi comuna... | P0 |
| US-ALC-CHV-001-01 | Alcalde de Chillán V | ver el estado de todos los proyectos de mi comuna... | P0 |
| US-ALC-SC-001-01 | Alcalde de San Carlo | ver el estado de todos los proyectos de mi comuna... | P0 |
| US-AMOD-001-01 | analista_modificacio | un módulo de gestión de modificaciones con histori... | P0 |
| US-ANAL-INV-001-01 | analista_inversion | un formulario digital de evaluación técnica con ca... | P0 |
| US-ANAL-INV-001-02 | analista_inversion | consultar el historial de proyectos similares eval... | P2 |
| US-ANAL-SEG-001-02 | analista_seguimiento | recibir alertas automáticas de proyectos con desvi... | P0 |
| US-ARQ-001-01 | arquitecto_revisor | visualizador de planos en formato BIM/CAD... | P1 |
| US-AS-001-01 | asistente_social | un módulo de fichas sociales con criterios de eval... | P0 |
| US-C33-001-01 | analista_c33 | un catálogo de precios referenciales de vehículos ... | P1 |
| US-CC-001-01 | camara_comercio | información de programas de apoyo empresarial del ... | P2 |
| US-COM-REC-001-01 | miembro_comision_rec | un acta de recepción electrónica con checklist de ... | P0 |
| US-COM-SECT-001-01 | comunicaciones_dipir | información actualizada de proyectos para comunica... | P2 |
| US-COMPERT-001-01 | miembro_comite_perti | acceder a la documentación de iniciativas antes de... | P0 |
| US-COMPERT-001-02 | miembro_comite_perti | votar electrónicamente durante las sesiones... | P0 |
| US-COORD-DIT-001-01 | coordinador_sectoria | una vista consolidada de proyectos por sector (via... | P1 |
| US-CORE-002-01 | consejero_regional | consultar el estado de ejecución de proyectos que ... | P1 |
| US-DIFOI-001-02 | jefe_difoi | integración con SERCOTEC, CORFO e INDAP para datos... | P1 |
| US-DIFOI-002-01 | jefe_difoi | un catálogo de proyectos FIC-R y de innovación reg... | P1 |
| US-DIPLADE-002-01 | jefe_diplade | un workflow digital para el Comité de Pertinencia ... | P1 |
| US-DIR-SOC-001-01 | dirigente_social | información de fondos concursables y consultas... | P1 |
| US-DIT-002-01 | jefe_dit | un módulo de gestión de contratos con plazos, gara... | P1 |
| US-EDU-001-01 | analista_educacion | un módulo de gestión de becas regionales... | P0 |
| US-EMP-001-01 | empresa_gremio | un calendario único de postulaciones a fondos... | P1 |
| US-EPP-001-01 | encargado_proy_prog | alertas de desviación de cronograma (Gantt)... | P1 |
| US-EVAL-001-01 | evaluador_social | un formulario de evaluación con criterios ponderad... | P0 |
| US-EVAL-001-02 | evaluador_social | consultar el historial de la organización postulan... | P1 |
| US-F8-001-01 | encargado_fondos_8 | un módulo de gestión de concursos con etapas confi... | P0 |
| US-F8-001-02 | encargado_fondos_8 | generar reportes de cobertura territorial y temáti... | P1 |
| US-FNDR8-001-01 | analista_8_tecnico | un checklist automático de admisibilidad... | P0 |
| US-FRPD-001-01 | comite_frpd | acceso a expedientes técnicos de proyectos FRPD... | P2 |
| US-GFOM-001-01 | gestor_fomento | estadísticas de formalización de empresas por comu... | P1 |
| US-IF-001-02 | inspector_fiscal | generar informes de fiscalización con plantillas e... | P1 |
| US-INDAP-001-01 | Director INDAP | información de proyectos agrícolas GORE... | P1 |
| US-INV-001-01 | investigador_univers | postular proyectos FIC totalmente en línea... | P1 |
| US-ITO-001-01 | inspector_tecnico_ob | una app móvil offline para el libro de obras digit... | P0 |
| US-ITO-001-02 | ito_obra | un checklist digital de verificación de hitos cont... | P0 |
| US-ITO-002-01 | ito_obra | un workflow de aprobación de EP con validación de ... | P0 |
| US-ITOM-001-01 | ITO Municipal | acceso restringido al sistema de inversión regiona... | P1 |
| US-ITP-001-01 | itp_programa | un módulo de inspección con checklist por programa... | P0 |
| US-MDS-001-01 | analista_inversiones | acceso al banco de proyectos BIP integrado... | P0 |
| US-ONG-001-01 | ong_regional | información de fondos concursables y consultas ciu... | P2 |
| US-ONG-001-01 | ong_fundacion | postular en línea a subvenciones del 8%... | P0 |
| US-PAT-DID-001-01 | analista_patrocinant | un módulo de patrocinio con checklist de requisito... | P0 |
| US-PAT-DIF-001-01 | analista_patrocinant | un módulo de patrocinio integrado con BIP... | P0 |
| US-PAT-DIT-001-01 | analista_patrocinant | validación técnica automática de proyectos de infr... | P0 |
| US-PES-001-01 | analista_pesca | un registro de caletas y organizaciones pesqueras ... | P1 |
| US-PPR-001-01 | analista_ppr_tecnico | un módulo de evaluación técnica específico para PP... | P1 |
| US-PREINV-001-01 | analista_preinversio | un módulo de evaluación de admisibilidad con check... | P0 |
| US-PROF-REZ-001-01 | profesional_zona_rez | acceso a expedientes de proyectos rezagados... | P0 |
| US-RTEC-001-01 | referente_tecnico | aprobar hitos técnicos en sistema... | P1 |
| US-SAG-001-01 | Director SAG | información de proyectos agrícolas financiados por... | P2 |
| US-SECPLA-001-01 | secpla | un asistente de formulación de proyectos que valid... | P1 |
| US-SECPLA-001-02 | secpla | consultar proyectos similares ejecutados en otras ... | P2 |
| US-SER-MOP-001-01 | SEREMI MOP | ver el estado de convenios de mandato MOP-GORE... | P0 |
| US-SERC-001-01 | Director SERCOTEC | información de beneficiarios GORE para evitar dupl... | P1 |
| US-SERVIU-001-01 | Director SERVIU | ver proyectos de vivienda con cofinanciamiento GOR... | P1 |
| US-SOC-001-01 | analista_social | un registro de organizaciones y beneficiarios soci... | P0 |


---

*Documento parte de GORE_OS Blueprint Integral v5.5*  
*Última actualización: 2025-12-19 | SSOT: inventario_roles_v8.yml, historias_usuarios_v2.yml*

