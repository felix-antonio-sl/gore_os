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

| Dimensión | Componentes |
|-----------|-------------|
| **Actos Formales** | Resoluciones, Convenios, Reglamentos, Oficios |
| **Procedimientos** | Ley 19.880, Plazos legales, Recursos, Notificaciones |
| **Cumplimiento** | Probidad, Transparencia, Control CGR, Auditoría |

---

## Módulos

### 1. Actos Administrativos

**Ciclo de Vida:**

```
BORRADOR → VISACIÓN Jurídica → FIRMA FEA → TOMA RAZÓN (si aplica) → NOTIFICACIÓN → VIGENTE
```

**Tipos de Actos:**

| Tipo | Características |
|------|-----------------|
| Res. Exenta | Sin toma de razón CGR (mayoría de actos GORE) |
| Res. Afecta | Requiere toma de razón (plurianual, personal, montos sobre umbral) |
| Decreto | Acto del Gobernador con efectos normativos |
| Oficio | Comunicación formal a terceros |
| Acuerdo CORE | Decisiones colegiadas del Consejo Regional |
| Certificado | Constancia de hechos o estados |

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

| Plazo | Aplicación |
|-------|------------|
| 5 días hábiles | Recurso de reposición |
| 5 días hábiles | Recurso jerárquico |
| 10 días hábiles | Respuesta a solicitudes ciudadanas |
| 30 días hábiles | Silencio administrativo positivo |
| 6 meses | Plazo máximo procedimiento (prorrogable) |
| 2 años | Invalidación de oficio |

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

---

## Entidades de Datos

### Actos Administrativos

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `ActoAdministrativo` | id, tipo, numero, fecha, materia, estado_tramitacion, requiere_toma_razon, expediente_id | → ExpedienteElectronico, FirmaActo[], Notificacion[] |
| `FirmaActo` | id, acto_id, firmante_id, tipo, fecha, estado | → ActoAdministrativo, Funcionario |
| `Notificacion` | id, acto_id, destinatario, medio, fecha_envio, fecha_recepcion, estado | → ActoAdministrativo |

### Procedimientos y Expedientes

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `ExpedienteElectronico` | id, codigo, materia, fecha_inicio, estado, folio_actual | → DocumentoExpediente[], ActoAdministrativo[] |
| `DocumentoExpediente` | id, expediente_id, folio, tipo, fecha_ingreso, origen | → ExpedienteElectronico |
| `ProcedimientoAdmin` | id, tipo, iniciador, fecha_inicio, plazo_legal, fecha_vencimiento, estado | → ExpedienteElectronico, ActoAdministrativo |
| `RecursoAdmin` | id, procedimiento_id, tipo, fecha_interposicion, plazo_respuesta, estado | → ProcedimientoAdmin |

### Cumplimiento y Control

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `DeclaracionInteres` | id, funcionario_id, tipo, fecha, estado_verificacion | → Funcionario |
| `AudienciaLobby` | id, funcionario_id, fecha, solicitante, materia, resultado | → Funcionario |
| `SumarioAdmin` | id, tipo, fecha_inicio, inculpado_id, fiscal_id, estado, sancion | → Funcionario |
| `ControlCumplimiento` | id, norma_id, proceso_id, requisito, estado, fecha_verificacion | → NormaVigente |

### Convenios

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Convenio` | id, tipo, numero, partes[], objeto, fecha_suscripcion, vigencia_inicio, vigencia_fin, estado, acto_aprobatorio_id | → ActoAdministrativo, ModificacionConvenio[], Rendicion[] (D-FIN) |
| `ModificacionConvenio` | id, convenio_id, tipo, fecha, acto_id, descripcion | → Convenio, ActoAdministrativo |

### Normativa

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Reglamento` | id, numero, titulo, fecha_aprobacion, fecha_publicacion, estado | → ArticuloReglamento[] |
| `NormaVigente` | id, tipo, numero, titulo, organismo_emisor, fecha_vigencia, url | → ControlCumplimiento[], ChecklistNorma[] |
| `ChecklistNorma` | id, norma_id, tipo_operacion, requisito, obligatorio | → NormaVigente |

---

## Referencias Cruzadas

| Dominio | Relación |
|---------|----------|
| **D-FIN** | Convenios → Rendiciones |
| **D-EJEC** | Convenio (SSOT) → Ejecución operativa |
| **D-TDE** | Expediente electrónico, interoperabilidad |

---

*Documento parte de GORE_OS v3.1*
