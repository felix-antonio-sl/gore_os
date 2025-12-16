# D-NORM: Dominio de Gestión Jurídico-Administrativa y Cumplimiento

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Habilitante (Soporte Operativo)  
> **Función GORE:** NORMAR  

---

## Propósito

Gestionar el ciclo completo de actos administrativos, procedimientos formales, cumplimiento normativo y control interno, asegurando la validez jurídica y trazabilidad de las actuaciones del GORE.

> **Visión:** Toda actuación formal del GORE —resoluciones, convenios, procedimientos— debe ser jurídicamente válida, trazable y verificable. Este dominio garantiza que los procesos jurídico-administrativos se ejecuten con rigor, cumpliendo plazos legales, fundamentación adecuada y control preventivo.

---

## Tres Dimensiones Integradas

| Dimensión          | Componentes                                          |
| ------------------ | ---------------------------------------------------- |
| **Actos Formales** | Resoluciones, Convenios, Reglamentos, Oficios        |
| **Procedimientos** | Ley 19.880, Plazos legales, Recursos, Notificaciones |
| **Cumplimiento**   | Probidad, Transparencia, Control CGR, Auditoría      |

---

## Módulos

### 1. Actos Administrativos

**Ciclo de Vida:**

```
BORRADOR → VISACIÓN Jurídica → FIRMA FEA → TOMA RAZÓN (si aplica) → NOTIFICACIÓN → VIGENTE
```

**Tipos de Actos:**

| Tipo         | Características                                                    |
| ------------ | ------------------------------------------------------------------ |
| Res. Exenta  | Sin toma de razón CGR (mayoría de actos GORE)                      |
| Res. Afecta  | Requiere toma de razón (plurianual, personal, montos sobre umbral) |
| Decreto      | Acto del Gobernador con efectos normativos                         |
| Oficio       | Comunicación formal a terceros                                     |
| Acuerdo CORE | Decisiones colegiadas del Consejo Regional                         |
| Certificado  | Constancia de hechos o estados                                     |

**Estructura Formal (Ley 19.880):**

- **VISTOS** → Competencia y antecedentes que habilitan el acto
- **CONSIDERANDO** → Fundamentos de hecho y de derecho (Art. 11, 41)
- **RESUELVO** → Decisión formal con articulado

**Funcionalidades:**

- Generador asistido de actos con plantillas SFD/STS
- Validación automática de estructura y fundamentación
- Control de numeración correlativa por tipo
- Flujo de firmas con FEA
- Envío automático a toma de razón
- Notificación electrónica a interesados

### 2. Procedimientos Administrativos

**Marco: Ley 19.880**

**Etapas:**

```
INICIACIÓN → INSTRUCCIÓN → FINALIZACIÓN → IMPUGNACIÓN (eventual)
```

**Plazos Legales Críticos:**

| Plazo           | Aplicación                               |
| --------------- | ---------------------------------------- |
| 5 días hábiles  | Recurso de reposición                    |
| 5 días hábiles  | Recurso jerárquico                       |
| 10 días hábiles | Respuesta a solicitudes ciudadanas       |
| 30 días hábiles | Silencio administrativo positivo         |
| 6 meses         | Plazo máximo procedimiento (prorrogable) |
| 2 años          | Invalidación de oficio                   |

**Funcionalidades:**

- Control de plazos con alertas automáticas
- Gestión de silencio administrativo
- Tramitación de recursos (reposición, jerárquico)
- Notificaciones electrónicas con acuse
- Cómputo automático de días hábiles

### 3. Expediente Electrónico

**Marco: Ley 21.180 (TDE)**

**Principios:**

- Expediente único por procedimiento
- Foliación automática y correlativa
- Trazabilidad completa de actuaciones
- Firma electrónica avanzada (FEA) para actos
- Interoperabilidad con DocDigital

**Componentes:**

- Oficina de Partes Digital: Ingreso, distribución, seguimiento
- Gestión de documentos: Clasificación, metadatos, búsqueda
- Flujos de trabajo: Derivación, visación, firma
- Archivo institucional: Retención, transferencia, eliminación

**Integraciones:** DocDigital, Cero Papel, ClaveÚnica

### 4. Cumplimiento y Control Interno

**Probidad y Transparencia (Leyes 20.285, 20.880):**

- Declaraciones de intereses y patrimonio
- Inhabilidades e incompatibilidades
- Transparencia activa (portal institucional)
- Solicitudes de acceso a información

**Ley de Lobby (Ley 20.730):**

- Registro de audiencias
- Gestiones de interés particular
- Viajes pagados por terceros

**Control Preventivo CGR:**

- Toma de razón de actos afectos
- Registro de actos exentos
- Respuesta a observaciones y reparos

**Control Interno:**

- Sumarios administrativos
- Investigaciones sumarias
- Auditoría interna
- Plan de integridad institucional

### 5. Convenios Institucionales (SSOT)

**Ciclo de Vida:**

```
NEGOCIACIÓN → REDACCIÓN → VISACIÓN Jurídica → APROBACIÓN (Res.+CGR) → EJECUCIÓN → TÉRMINO
```

**Tipos:**

- Marco: Establece relación general
- Colaboración: Sin transferencia de recursos
- Transferencia: Con recursos GORE a ejecutor
- Específico: Derivado de convenio marco
- Programación: Plurianual con ministerios
- Seguridad Municipal: Operación de cámaras, mantenimiento, personal (incluye plan_comunal_ref, compromisos_operativos)

**Actos Asociados:**

- Resolución aprobatoria del convenio
- Resolución de modificación
- Resolución de resciliación
- Resolución de término anticipado

### 6. Reglamentos Regionales

**Potestad Reglamentaria (Art. 16 letra d LOC GORE)**

```
INICIATIVA → CONSULTA PÚBLICA → CORE aprueba → TOMA RAZÓN → PUBLICACIÓN D.Oficial
```

**Tipos:** Desarrollo regional, Organización interna, Instructivos

### 7. Biblioteca Normativa

**Categorías:**

- Constitución, LOC GORE, Leyes Presupuesto
- DS, Resoluciones CGR, Circulares DIPRES
- Oficios SUBDERE, Reglamentos regionales

**Funcionalidades:**

- Búsqueda full-text y por metadatos
- Versionamiento de normas
- Alertas de cambios normativos
- Vinculación norma ↔ proceso ↔ acto
- Checklist de cumplimiento por tipo de operación

### 8. Control Externo

**Objetivo:** Gestionar las relaciones y obligaciones del GORE con los órganos de control externo del Estado.

#### Órganos de Control

| Órgano                                        | Función                                             | Marco Legal               |
| --------------------------------------------- | --------------------------------------------------- | ------------------------- |
| **Contraloría General de la República (CGR)** | Control de legalidad, fiscalización, auditoría      | Ley 10.336, Art. 98 CPR   |
| **Consejo para la Transparencia (CPLT)**      | Acceso a información pública, transparencia activa  | Ley 20.285                |
| **Tribunal de Cuentas**                       | Juzgamiento de cuentas, responsabilidad funcionaria | Ley 10.336 Art. 107 y ss. |
| **Ministerio Público**                        | Persecución penal de delitos funcionarios           | CPP, Ley 19.640           |

#### Procesos de Control CGR

| Proceso               | Descripción                                | Plazo                    |
| --------------------- | ------------------------------------------ | ------------------------ |
| **Toma de Razón**     | Control preventivo de actos afectos        | 30 días (prorrogable 15) |
| **Registro**          | Inscripción de actos exentos               | 5 días                   |
| **Auditoría**         | Fiscalización de gestión y uso de recursos | Variable                 |
| **Sumario**           | Investigación de irregularidades           | 20 días (prorrogable)    |
| **Juicio de Cuentas** | Responsabilidad por rendiciones objetadas  | Variable                 |

#### Flujo de Auditorías CGR

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    CICLO DE AUDITORÍA CGR                                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  NOTIFICACIÓN ──▶ PLANIFICACIÓN ──▶ EJECUCIÓN ──▶ PREINFORME ──▶ INFORME FINAL     │
│       │                │                │              │              │             │
│       ▼                ▼                ▼              ▼              ▼             │
│  • Oficio CGR     • Designación    • Entrevistas  • Observaciones • Publicación   │
│  • Alcance          contraparte    • Revisión     • Plazo resp.   • Seguimiento   │
│  • Plazo          • Recopilación     documental   • Descargos     • Plan mejora   │
│                     antecedentes   • Terreno                                       │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### Procesos CPLT

| Proceso                                | Descripción                             | Plazo           |
| -------------------------------------- | --------------------------------------- | --------------- |
| **Solicitud Acceso Información**       | Derecho ciudadano de acceso             | 20 días hábiles |
| **Amparo**                             | Recurso ante denegación de información  | 15 días hábiles |
| **Fiscalización Transparencia Activa** | Verificación de publicación obligatoria | Anual           |

#### Entidades

```yaml
Auditoria_CGR:
  atributos:
    - id: UUID
    - oficio_inicio: String
    - fecha_notificacion: Date
    - tipo: ENUM [REGULAR, ESPECIAL, SEGUIMIENTO]
    - alcance: String
    - contraparte_gore: Ref[D-BACK.Funcionario]
    - estado: ENUM [NOTIFICADA, EN_EJECUCION, PREINFORME, DESCARGOS, FINALIZADA]
    - observaciones: Array[Observacion_CGR]
    - plan_mejora: Ref[Plan_Mejora]
  relaciones:
    - → D-GINT.Evento_FENIX  # Observaciones críticas activan intervención

Observacion_CGR:
  atributos:
    - id: UUID
    - auditoria_id: Ref[Auditoria_CGR]
    - tipo: ENUM [RECOMENDACION, OBSERVACION, REPARO]
    - descripcion: String
    - plazo_respuesta: Date
    - estado: ENUM [PENDIENTE, DESCARGADA, ACEPTADA, RECHAZADA]
    - descargo: String
    - evidencia: Array[Ref[DocumentoExpediente]]

Juicio_Cuentas:
  atributos:
    - id: UUID
    - expediente_tcp: String
    - demandado: Ref[D-BACK.Funcionario]
    - monto_reparable: Decimal
    - estado: ENUM [EN_TRAMITE, SENTENCIADO, APELADO, EJECUTORIADO]
    - sentencia: String
    - fecha_sentencia: Date

Solicitud_CPLT:
  atributos:
    - id: UUID
    - folio_cplt: String
    - solicitante: String
    - informacion_requerida: String
    - fecha_ingreso: Date
    - plazo_vencimiento: Date
    - estado: ENUM [RECIBIDA, EN_PROCESO, RESPONDIDA, AMPARO]
    - respuesta: String
    - causal_negativa: String  # Si aplica
  relaciones:
    - → ExpedienteElectronico

Plan_Mejora:
  atributos:
    - id: UUID
    - auditoria_ref: Ref[Auditoria_CGR]
    - compromisos: Array[Compromiso_Mejora]
    - fecha_comprometida: Date
    - estado: ENUM [EN_ELABORACION, APROBADO, EN_EJECUCION, VERIFICADO]

Compromiso_Mejora:
  atributos:
    - id: UUID
    - descripcion: String
    - responsable: Ref[D-BACK.Funcionario]
    - plazo: Date
    - avance_porcentaje: Integer
    - evidencia: Array[Ref[DocumentoExpediente]]
```

#### Indicadores de Control Externo

| Indicador                             | Descripción                              | Meta      |
| ------------------------------------- | ---------------------------------------- | --------- |
| **Observaciones CGR Pendientes**      | N° de observaciones sin subsanar         | 0         |
| **Tiempo Respuesta CPLT**             | Días promedio de respuesta a solicitudes | < 15 días |
| **Cumplimiento Transparencia Activa** | % de ítems publicados vs. obligatorios   | 100%      |
| **Juicios de Cuentas Activos**        | N° de juicios en tramitación             | Minimizar |

---

## Entidades de Datos

### Actos Administrativos

| Entidad              | Atributos Clave                                                                          | Relaciones                                           |
| -------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `ActoAdministrativo` | id, tipo, numero, fecha, materia, estado_tramitacion, requiere_toma_razon, expediente_id | → ExpedienteElectronico, FirmaActo[], Notificacion[] |
| `FirmaActo`          | id, acto_id, firmante_id, tipo, fecha, estado                                            | → ActoAdministrativo, Funcionario                    |
| `Notificacion`       | id, acto_id, destinatario, medio, fecha_envio, fecha_recepcion, estado                   | → ActoAdministrativo                                 |

### Procedimientos y Expedientes

| Entidad                 | Atributos Clave                                                           | Relaciones                                                           |
| ----------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `ExpedienteElectronico` | id, codigo, materia, fecha_inicio, estado, folio_actual                   | → DocumentoExpediente[], ActoAdministrativo[], Solicitud_Evidencia[] |
| `DocumentoExpediente`   | id, expediente_id, folio, tipo, fecha_ingreso, origen                     | → ExpedienteElectronico                                              |
| `ProcedimientoAdmin`    | id, tipo, iniciador, fecha_inicio, plazo_legal, fecha_vencimiento, estado | → ExpedienteElectronico, ActoAdministrativo                          |
| `RecursoAdmin`          | id, procedimiento_id, tipo, fecha_interposicion, plazo_respuesta, estado  | → ProcedimientoAdmin                                                 |

### Cumplimiento y Control

| Entidad               | Atributos Clave                                                  | Relaciones     |
| --------------------- | ---------------------------------------------------------------- | -------------- |
| `DeclaracionInteres`  | id, funcionario_id, tipo, fecha, estado_verificacion             | → Funcionario  |
| `AudienciaLobby`      | id, funcionario_id, fecha, solicitante, materia, resultado       | → Funcionario  |
| `SumarioAdmin`        | id, tipo, fecha_inicio, inculpado_id, fiscal_id, estado, sancion | → Funcionario  |
| `ControlCumplimiento` | id, norma_id, proceso_id, requisito, estado, fecha_verificacion  | → NormaVigente |

### Convenios

| Entidad                | Atributos Clave                                                                                                   | Relaciones                                                        |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `Convenio`             | id, tipo, numero, partes[], objeto, fecha_suscripcion, vigencia_inicio, vigencia_fin, estado, acto_aprobatorio_id | → ActoAdministrativo, ModificacionConvenio[], Rendicion[] (D-FIN) |
| `ModificacionConvenio` | id, convenio_id, tipo, fecha, acto_id, descripcion                                                                | → Convenio, ActoAdministrativo                                    |
| `Solicitud_Evidencia`  | id, solicitante, tipo_solicitante, oficio_ref, evidencias[], fecha_solicitud, estado                              | → ExpedienteElectronico                                           |

### Normativa

| Entidad          | Atributos Clave                                                 | Relaciones                                |
| ---------------- | --------------------------------------------------------------- | ----------------------------------------- |
| `Reglamento`     | id, numero, titulo, fecha_aprobacion, fecha_publicacion, estado | → ArticuloReglamento[]                    |
| `NormaVigente`   | id, tipo, numero, titulo, organismo_emisor, fecha_vigencia, url | → ControlCumplimiento[], ChecklistNorma[] |
| `ChecklistNorma` | id, norma_id, tipo_operacion, requisito, obligatorio            | → NormaVigente                            |

---

## Referencias Cruzadas

| Dominio            | Relación                                                                               |
| ------------------ | -------------------------------------------------------------------------------------- |
| **D-PLAN**         | Reglamentos regionales vinculados con ERD                                              |
| **D-FIN**          | Convenios → Rendiciones                                                                |
| **D-EJEC**         | Convenio (SSOT) → Ejecución operativa                                                  |
| **D-COORD**        | Actores como partes en convenios y actos administrativos                               |
| **D-BACK**         | Gestión documental, expediente electrónico                                             |
| **D-TDE**          | Expediente electrónico, interoperabilidad                                              |
| **D-GESTION**      | Indicadores de cumplimiento normativo para H_gore                                      |
| **D-SEG**          | Convenios de Seguridad Municipal, Solicitud_Evidencia → Expediente                     |
| **D-EVOL**         | Automatización de expedientes y alertas normativas                                     |
| **D-GINT (FÉNIX)** | Actos administrativos vencidos o con observaciones CGR activan intervención Nivel I-II |

---

*Documento parte de GORE_OS v4.1*
