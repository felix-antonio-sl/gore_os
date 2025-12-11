# Stakeholders y Usuarios del Gemelo Digital GORE Ñuble

## Taxonomía de Usuarios (derivada de [kb_gn_000_intro_gores_nuble_koda.yml](cci:7://file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/kb_gn_000_intro_gores_nuble_koda.yml:0:0-0:0))

### Clasificación por Esfera de Relación

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ECOSISTEMA DE USUARIOS - GEMELO DIGITAL ÑUBLE            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │   ESFERA 1      │     │   ESFERA 2      │     │   ESFERA 3      │       │
│  │   NÚCLEO GORE   │     │   GOBIERNO      │     │   ECOSISTEMA    │       │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘       │
│           │                       │                       │                 │
│  ┌────────▼────────┐     ┌────────▼────────┐     ┌────────▼────────┐       │
│  │ Autoridades     │     │ Gob. Central    │     │ Ciudadanía      │       │
│  │ Funcionarios    │     │ Municipios      │     │ Empresas        │       │
│  │ Divisiones      │     │ Control         │     │ Academia        │       │
│  │ Unidades        │     │ Sectorial       │     │ Sociedad Civil  │       │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ESFERA 1: NÚCLEO GORE (Usuarios Internos Directos)

### U1.1 Gobernador Regional

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Máxima autoridad ejecutiva del GORE |
| **Perfil** | Autoridad electa, visión estratégica, toma de decisiones de alto nivel |

**Necesidades:**

- Visión 360° del estado de la región en tiempo real
- Indicadores clave de gestión y cumplimiento de metas
- Alertas tempranas de riesgos y desviaciones
- Información para rendición de cuentas política
- Simulación de escenarios para decisiones estratégicas

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-GOB-01 | Consultar dashboard ejecutivo regional | Alta |
| UC-GOB-02 | Monitorear ejecución presupuestaria en tiempo real | Alta |
| UC-GOB-03 | Simular impacto de políticas públicas | Media |
| UC-GOB-04 | Recibir alertas de situaciones críticas (emergencias, desviaciones) | Alta |
| UC-GOB-05 | Preparar presentaciones para CORE con datos actualizados | Media |
| UC-GOB-06 | Comparar indicadores comunales para priorización | Alta |
| UC-GOB-07 | Presentar DIP y actualizarla anualmente | Alta |
| UC-GOB-08 | Registrar audiencias, viajes y donativos en plataforma de lobby | Alta |
| UC-GOB-09 | Designar sujetos pasivos adicionales de lobby | Media |
| UC-GOB-10 | Firmar resoluciones con firma electrónica avanzada | Alta |
| UC-GOB-11 | Solicitar transferencia de competencias al CORE | Media |

**Journey Principal:**

```
Inicio jornada → Revisa dashboard ejecutivo → Identifica alerta de baja ejecución en comuna X 
→ Profundiza en detalle de proyectos → Convoca reunión con jefe DIPIR → Toma decisión correctiva 
→ Monitorea evolución en días siguientes
```

---

### U1.2 Consejeros Regionales (CORE)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Órgano colegiado normativo, resolutivo y fiscalizador |
| **Perfil** | 16 consejeros electos, diversos perfiles profesionales, representan circunscripciones |

**Necesidades:**

- Información para ejercer función fiscalizadora
- Datos para evaluar propuestas de inversión
- Comparativos territoriales (por provincia/comuna)
- Historial de votaciones y acuerdos
- Trazabilidad de proyectos aprobados

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CORE-01 | Consultar estado de proyectos por circunscripción | Alta |
| UC-CORE-02 | Analizar propuesta de distribución FNDR antes de votación | Alta |
| UC-CORE-03 | Fiscalizar ejecución de acuerdos previos | Alta |
| UC-CORE-04 | Comparar indicadores entre comunas de su circunscripción | Media |
| UC-CORE-05 | Revisar historial de modificaciones presupuestarias | Media |
| UC-CORE-06 | Acceder a informes de Unidad de Control | Alta |
| UC-CORE-07 | Presentar DIP individualmente y actualizarla | Alta |
| UC-CORE-08 | Registrar audiencias y donativos en plataforma de lobby | Alta |
| UC-CORE-09 | Aprobar solicitud de transferencia de competencias | Alta |
| UC-CORE-10 | Fiscalizar cumplimiento de transparencia del GORE | Media |
| UC-CORE-11 | Velar por cumplimiento de normas de probidad | Alta |
| UC-CORE-12 | Requerir cesación del Gobernador ante TRICEL (1/3 consejeros) | Baja |

**Journey Principal:**

```
Recibe convocatoria a sesión → Accede a tabla con propuestas → Consulta detalle técnico de proyecto
→ Revisa indicadores de la comuna beneficiaria → Compara con otras comunas → Solicita información adicional
→ Vota informadamente → Hace seguimiento post-aprobación
```

---

### U1.3 Administrador Regional

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Gerente operacional del GORE |
| **Perfil** | Profesional de alta dirección, coordinador de divisiones |

**Necesidades:**

- Control de gestión de todas las divisiones
- Indicadores de desempeño funcionario
- Estado de procesos administrativos
- Gestión de riesgos operacionales
- Coordinación interdivisional

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-ADM-01 | Monitorear KPIs de cada división | Alta |
| UC-ADM-02 | Gestionar agenda y compromisos del GORE | Alta |
| UC-ADM-03 | Identificar cuellos de botella en procesos | Alta |
| UC-ADM-04 | Coordinar respuesta ante emergencias | Alta |
| UC-ADM-05 | Supervisar cumplimiento de plazos legales | Media |

---

### U1.4 Jefes de División

| División | Necesidades Específicas |
|----------|------------------------|
| **DAF** | Flujo de caja, estados financieros, gestión RRHH, contratos vigentes, convenios y rendiciones |
| **DIPLADE** | Avance ERD, estado instrumentos planificación, indicadores territoriales, estudios y PROPIR |
| **DIPIR** | Cartera de proyectos, ejecución por fondo, alertas de vencimiento, coordinación presupuestaria con DAF |
| **DIFOI** | Ecosistema productivo, indicadores CTI, programas de fomento, cartera rezago, convenios CORFO/ANID/FRPD |
| **DIT** | Estado de obras, licitaciones, transporte regional, supervisión de contratos de obra |
| **DIDESOH** | Indicadores sociales, programas en ejecución, brechas por comuna, subvenciones 8% |

**Casos de Uso Transversales:**

| ID | Caso de Uso | División |
|----|-------------|----------|
| UC-DIV-01 | Generar informes de gestión divisional | Todas |
| UC-DIV-02 | Monitorear cartera de proyectos/programas | DIPIR, DIFOI, DIT, DIDESOH |
| UC-DIV-03 | Evaluar postulaciones de iniciativas | DIPIR, DIPLADE |
| UC-DIV-04 | Gestionar convenios y transferencias | DAF, DIPIR |
| UC-DIV-05 | Coordinar con servicios sectoriales | Todas |

#### U1.4.A Modelo Transversal de Gestión Interna y del Ciclo de IPR para Divisiones

```yaml
Necesidades_Transversales_Divisiones:

  Gestion_Ciclo_IPR:
    ID: MODELO-GESTION-IPR
    Concepto: "Gestionar IPR como oportunidades en pipeline con ciclo de vida completo"
    Componentes:
      Pipeline_IPR:
        etapas: [Prospección, Formulación, Admisibilidad, Evaluación, Financiamiento, Ejecución, Cierre]
        metricas: [conversion_por_etapa, dias_en_etapa, valor_pipeline, probabilidad_exito]
      Segmentacion:
        por_sector: [infraestructura, social, fomento, cultura, seguridad]
        por_mecanismo: [SNI, FRIL, FRPD, 8pct, Glosa06, C33]
        por_origen: [municipio, servicio, GORE, mixto]
        por_riesgo: [bajo, medio, alto, critico]
      Seguimiento_Relacional:
        formulador: [historial_postulaciones, tasa_exito, observaciones_frecuentes]
        ejecutor: [desempeno_rendiciones, cumplimiento_plazos, calidad_tecnica]
      Alertas_Proactivas:
        vencimientos: [plazos_legales, hitos_convenio, garantias]
        anomalias: [baja_ejecucion, desviaciones_costo, retrasos_criticos]
        oportunidades: [recursos_disponibles, ventanas_postulacion, fondos_nuevos]

  Gestion_Interna_Recursos:
    ID: MODELO-GESTION-INTERNA-GORE
    Modulos:
      RRHH:
        dotacion: [planta, contrata, honorarios, confianza]
        gestion_personas: [asistencia, permisos, licencias, feriados]
        desarrollo: [capacitacion, calificaciones, carrera_funcionaria]
        remuneraciones: [sueldos, horas_extra, viaticos, asignaciones]
      Activos_y_Recursos:
        vehiculos: [pool, asignados, mantencion, combustible]
        equipamiento: [computadores, impresoras, mobiliario, inventario]
        infraestructura: [oficinas, salas, bodegas, estacionamientos]
      Abastecimiento:
        compras: [solicitudes, licitaciones, OC, recepciones]
        proveedores: [registro, evaluacion, contratos_marco]
        bodega: [inventario, entradas, salidas, stock_critico]
      Gestion_Documental:
        correspondencia: [entrada, salida, interna]
        expedientes: [tramitacion, estados, responsables]
        archivo: [clasificacion, transferencia, eliminacion]

  Gestion_Riesgos:
    ID: MODELO-RIESGOS-DIV
    Tipos_Riesgo:
      operacional: [retrasos, sobrecostos, baja_calidad]
      legal: [incumplimiento_normas, observaciones_CGR, litigios]
      financiero: [baja_ejecucion, devolucion_fondos, deuda_flotante]
      reputacional: [proyectos_fallidos, denuncias]
      territorial: [conflictos_comunidad, problemas_terreno]
    Gestion:
      identificacion: "registro_sistematico_por_IPR_y_division"
      evaluacion: "matriz_probabilidad_impacto"
      mitigacion: "planes_de_accion_con_responsables"
      monitoreo: "semaforo_en_dashboard_divisional"
```

Tabla_resumen_por_division:

| División | Cartera IPR principal | Foco de gestión interna de recursos | Riesgos típicos |
|----------|-----------------------|------------------|-----------------|
| **DAF** | Convenios, rendiciones, pagos | RRHH, presupuesto, abastecimiento, activos | Observaciones CGR, deuda flotante, baja rendición |
| **DIPLADE** | Estudios, PROT, instrumentos planificación | Consultorías, SIG, coordinación territorial | Desactualización instrumentos, baja participación |
| **DIPIR** | Cartera completa IDI+PPR | Coordinación con DAF, seguimiento SIGFE/BIP | Proyectos estancados, RS vencidas, cierres pendientes |
| **DIFOI** | Programas fomento y CTI, rezago | Gestión convenios CORFO/ANID/FRPD | Baja ejecución, zonas rezagadas sin avance, CTI estancado |
| **DIT** | Obras viales y de infraestructura mayor | Contratos de obra, supervisión técnica | Sobrecostos, atrasos, conflictos territoriales |
| **DIDESOH** | Programas sociales y 8% | Coordinación comunal, subvenciones | Baja cobertura, duplicidades, rendiciones pendientes |

### U1.4.1 Jefaturas de Departamento DIPIR (kb_gn_019)

| Rol | Responsabilidad |
|-----|-----------------|
| **Jefatura Preinversión** | Gestión de admisibilidad y evaluación técnica de IPR (Fase 1 y 2) |
| **Jefatura Inversiones** | Seguimiento, supervisión y cierre de IPR en ejecución |

**Necesidades:**

- Vista completa de cartera IPR por estado (pipeline de gestión del ciclo de IPR)
- Asignación y reasignación de analistas
- Métricas de tiempos de tramitación por fase
- Alertas de plazos críticos (p. ej. 60 días de subsanación)
- Coordinación con MDSF y DIPRES
- Integración con disponibilidad presupuestaria (FNDR, FRPD, FRIL, 8%)

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-JDEP-01 | Asignar IPR a analista según tipología | Alta |
| UC-JDEP-02 | Monitorear tiempos de tramitación por fase | Alta |
| UC-JDEP-03 | Gestionar cola de IPR pendientes de evaluación | Alta |
| UC-JDEP-04 | Preparar cartera para envío a CORE | Alta |
| UC-JDEP-05 | Coordinar apoyos interdivisionales | Media |
| UC-JDEP-06 | Generar reportes de productividad del equipo | Media |
| UC-JDEP-07 | Orientar a postulantes sobre vía de financiamiento adecuada | Alta |
| UC-JDEP-08 | Aplicar árbol de decisión para clasificación de IPR | Alta |
| UC-JDEP-09 | Verificar elegibilidad de mecanismo según tipología y ejecutor | Alta |
| UC-JDEP-10 | Coordinar con DIPRES/SES evaluación de programas Glosa 06 | Media |

**Submódulo: Gestión Presupuestaria asociada a DIPIR (en coordinación con DAF)**

- Consultar disponibilidad por fondo antes de priorizar IPR
- Visualizar saldo comprometido vs. por comprometer por fondo/división
- Monitorear ejecución por fondo y por mecanismo (SNI, FRIL, FRPD, 8%)
- Identificar IPR con fondos comprometidos sin avance (riesgo de arrastre)
- Coordinar solicitudes de CDP y modificaciones con Jefatura Presupuesto DAF

### U1.4.2 Jefatura Departamento Presupuesto DAF (kb_gn_019)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Gestión de CDP, modificaciones presupuestarias y convenios |
| **Dependencia** | División de Administración y Finanzas (DAF) |

**Necesidades:**

- Estado de disponibilidad presupuestaria por fondo
- Cola de solicitudes de CDP pendientes
- Trazabilidad de modificaciones presupuestarias
- Control de convenios vigentes y por formalizar
- Integración operativa con SIGFE y SISREC

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-JPPT-01 | Emitir CDP verificando disponibilidad | Alta |
| UC-JPPT-02 | Tramitar modificaciones presupuestarias | Alta |
| UC-JPPT-03 | Elaborar y gestionar convenios de transferencia | Alta |
| UC-JPPT-04 | Monitorear devengo según tipo de receptor | Alta |
| UC-JPPT-05 | Programar transferencias | Alta |
| UC-JPPT-06 | Gestionar resoluciones de cierre de convenio | Media |

### U1.4.3 División GORE Patrocinante de PPR Transferidos (kb_gn_001)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Evaluar pertinencia estratégica y patrocinar PPR transferidos a entidades públicas |
| **Ubicación** | Divisiones sectoriales del GORE (fomento, social, infraestructura, etc.) |

**Necesidades:**

- Visión clara de la oferta programática regional y brechas por sector
- Herramientas para verificar alineación con ERD y planes regionales
- Información sobre programas GORE existentes para evitar duplicidades

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-DIVPAT-01 | Emitir Certificado de Pertinencia y Patrocinio GORE | Alta |
| UC-DIVPAT-02 | Evaluar alineación del PPR con ERD y planes divisionales | Alta |
| UC-DIVPAT-03 | Identificar sinergias o duplicidades con iniciativas GORE vigentes | Media |

---

### U1.5 Funcionarios Operativos GORE (EXPANDIDO kb_gn_019)

| Perfil | Ejemplos | Rol en Ciclo IPR |
|--------|----------|------------------|
| **Analista Preinversión** | Profesionales DIPIR | Revisión de admisibilidad y evaluación técnica, coordinación con MDSF |
| **Supervisor de Proyecto** | Profesionales DIPIR/Divisiones sectoriales | Seguimiento de ejecución, visitas a terreno, actualización BIP |
| **Analista Financiero** | Profesionales DAF | Monitoreo SIGFE/SISREC, revisión de rendiciones, alertas de desvíos |
| **Profesional Presupuesto** | Profesionales DAF | CDP, resoluciones, decretos y convenios de transferencia |
| **Oficina de Partes** | Administrativos | Recepción y registro de postulaciones (SGDOC) |
| **Secretario/a Ejecutivo CORE** | Profesional | Certificación de acuerdos CORE y comunicación de resultados |

#### U1.5.1 Analista de Preinversión DIPIR

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Evaluador técnico de IPR en Fase 1 y 2 |
| **Especialización** | Por tipología: infraestructura, social, fomento, estudios |

**Necesidades:**

- Bandeja de IPR asignadas con su estado
- Acceso a carpeta digital BIP y antecedentes técnicos
- Checklists de admisibilidad por mecanismo
- Comunicación estructurada con Unidad Formuladora
- Plantillas de actas e informes

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-APRE-01 | Revisar admisibilidad documental de IPR | Alta |
| UC-APRE-02 | Verificar cumplimiento de RIS y metodologías SNI | Alta |
| UC-APRE-03 | Elaborar Acta de Admisibilidad interna GORE | Alta |
| UC-APRE-04 | Comunicar observaciones a Unidad Formuladora | Alta |
| UC-APRE-05 | Registrar "Informar Postulación" en BIP | Alta |
| UC-APRE-06 | Monitorear RATE de MDSF (RS/FI/OT/AD) | Alta |
| UC-APRE-07 | Apoyar subsanación de observaciones FI/OT | Media |
| UC-APRE-08 | Actualizar estado de IPR en sistema de seguimiento | Alta |

**Journey Analista Preinversión:**

```
Recibe asignación de IPR → Descarga antecedentes de carpeta digital → Aplica checklist de admisibilidad
→ [Si admisible] Elabora acta y registra en BIP → [Si observada] Notifica a Unidad Formuladora
→ [Si inadmisible] Prepara oficio de rechazo → Formulador subsana → Re-evalúa
→ [Si RS/RF/AD] Marca como aprobado técnicamente → Informa a Jefatura para priorización
```

#### U1.5.2 Supervisor de Proyecto GORE

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Seguimiento técnico de IPR en ejecución |
| **Ubicación** | DIPIR o División sectorial patrocinante |

**Necesidades:**

- Cartera de proyectos asignados con hitos
- Calendario de visitas a terreno
- Registro estructurado de informes de avance
- Gestión de estados de pago
- Alertas de desvíos físicos vs financieros
- Integración con BIP y SIGFE

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-SUP-01 | Crear carpeta de seguimiento de proyecto | Alta |
| UC-SUP-02 | Registrar visita a terreno con evidencia | Alta |
| UC-SUP-03 | Revisar y validar informes de avance de la UT | Alta |
| UC-SUP-04 | Gestionar estados de pago | Alta |
| UC-SUP-05 | Actualizar % de avance físico en BIP | Alta |
| UC-SUP-06 | Alertar desviaciones relevantes a Jefatura | Alta |
| UC-SUP-07 | Coordinar reuniones periódicas GORE–UT | Media |
| UC-SUP-08 | Validar recepción provisoria y definitiva | Alta |

**Journey Supervisor de Proyecto:**

```
Recibe proyecto formalizado → Crea carpeta de seguimiento → Coordina reunión de inicio con UT
→ Programa visitas periódicas → Registra avances y estados de pago → Detecta desviación
→ Escala a Jefatura y Comité de Seguimiento → Gestiona modificación si aplica → Valida recepción de obras
→ Confirma cierre técnico
```

#### U1.5.3 Analista Financiero DAF

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Monitoreo financiero y gestión de rendiciones |
| **Sistemas** | SIGFE, SISREC |

**Necesidades:**

- Dashboard de ejecución financiera por IPR y por fondo
- Cola de rendiciones pendientes de revisión
- Alertas de sub-ejecución y desvíos
- Verificación de cumplimiento de reglas de devengo
- Trazabilidad de reintegros y devoluciones de garantías

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-AFIN-01 | Monitorear ejecución presupuestaria en SIGFE | Alta |
| UC-AFIN-02 | Revisar rendiciones de cuentas en SISREC | Alta |
| UC-AFIN-03 | Aprobar u observar rendición de cuentas | Alta |
| UC-AFIN-04 | Alertar sobre sub-ejecución o desvíos relevantes | Alta |
| UC-AFIN-05 | Solicitar reintegro de saldos no utilizados | Media |
| UC-AFIN-06 | Verificar reglas de devengo según tipo de receptor | Media |

#### U1.5.4 Profesional Departamento Presupuesto

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Elaboración de actos administrativos y convenios |

**Necesidades:**

- Plantillas actualizadas de resoluciones, decretos y convenios
- Flujo de visaciones internas claro
- Estado de tramitación ante DIPRES y CGR
- Registro de convenios vigentes y cerrados

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-PPPT-01 | Elaborar borrador de Resolución/Decreto | Alta |
| UC-PPPT-02 | Gestionar cadena de V°B° interno | Alta |
| UC-PPPT-03 | Elaborar borrador de Convenio de Transferencia | Alta |
| UC-PPPT-04 | Tramitar Toma de Razón ante CGR | Alta |
| UC-PPPT-05 | Elaborar Resolución de aprobación de convenio | Media |
| UC-PPPT-06 | Elaborar Resolución de cierre de convenio | Media |

#### U1.5.5 Unidad de Control de Rendiciones (U.C.R.)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Unidad especializada dentro de DAF que centraliza y ejecuta el control operativo de rendiciones |
| **Ubicación** | División de Administración y Finanzas (DAF) |

**Necesidades:**

- Base de datos centralizada de rendiciones por programa/IPR
- Integración con SISREC y SIGFE para conciliación automática
- Listas de chequeo estandarizadas por tipo de fondo
- Trazabilidad completa del expediente de rendición (ingreso, revisión, contabilización, archivo)
- Indicadores de tiempos de revisión y cuellos de botella

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-UCR-01 | Registrar rendiciones recibidas y asignarlas a RTF | Alta |
| UC-UCR-02 | Aplicar checklist formal y documental antes de contabilizar | Alta |
| UC-UCR-03 | Contabilizar rendiciones aprobadas en SIGFE | Alta |
| UC-UCR-04 | Mantener archivo físico/electrónico de expedientes de rendición | Media |
| UC-UCR-05 | Monitorear plazos internos de revisión y alertar atrasos | Media |

#### U1.5.6 Analista Otorgante SISREC (RTF)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Primera línea de revisión técnica y financiera de rendiciones en SISREC (Analista Otorgante) |
| **Sistemas** | SISREC, SIGFE (consulta), BIP |

**Necesidades:**

- Bandeja de rendiciones pendientes en SISREC por programa/IPR
- Acceso a convenios, anexos y cronogramas de ejecución
- Herramientas para revisar transacciones y adjuntos digitales con criterios técnicos y normativos
- Plantillas de observaciones y oficios de subsanación
- Visibilidad de impacto contable (cuentas, devengo, reintegros)

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-AOT-01 | Crear programas/proyectos en SISREC y registrar transferencias | Alta |
| UC-AOT-02 | Revisar rendiciones y aprobar/observar transacciones | Alta |
| UC-AOT-03 | Emitir informe técnico-financiero de rendición para DAF/UCR | Alta |
| UC-AOT-04 | Coordinar con ejecutores la regularización de observaciones | Alta |

#### U1.5.7 Encargado Otorgante SISREC (Jefatura DAF)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Jefatura que actúa como Encargado Otorgante en SISREC, firma informes de aprobación de rendiciones |
| **Ubicación** | Jefatura de División de Administración y Finanzas |

**Necesidades:**

- Vista consolidada de rendiciones en estado de aprobación
- Resumen ejecutivo de observaciones relevantes levantadas por RTF
- Trazabilidad de informes firmados con FEA y su contabilización posterior
- Alertas sobre rendiciones críticas que bloquean nuevas transferencias

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-EOT-01 | Revisar y firmar informes de aprobación de rendición en SISREC | Alta |
| UC-EOT-02 | Devolver rendiciones al ejecutor cuando las observaciones son graves o reiteradas | Alta |

---

### U1.6 Unidad de Control Interno

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Auditoría interna, fiscalización de legalidad |

**Necesidades:**

- Acceso transversal a todos los sistemas
- Trazabilidad completa de operaciones
- Alertas de desviaciones normativas
- Herramientas de auditoría analítica
- Generación de informes de hallazgos

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CTR-01 | Ejecutar auditorías con datos en tiempo real | Alta |
| UC-CTR-02 | Detectar anomalías en patrones de gasto | Alta |
| UC-CTR-03 | Verificar cumplimiento de plazos legales | Alta |
| UC-CTR-04 | Generar informes para CORE y CGR | Alta |
| UC-CTR-05 | Rastrear historial de modificaciones en registros | Media |

---

### U1.7 Roles de Cumplimiento Normativo GORE (NUEVO kb_gn_200)

#### U1.7.1 Encargado de Transparencia

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Gestión del cumplimiento de obligaciones de transparencia activa y pasiva |
| **Marco Legal** | Ley 20.285 y su reglamento |

**Necesidades:**

- Dashboard de cumplimiento de transparencia activa
- Gestión de solicitudes de acceso a información
- Alertas de plazos de respuesta (20+10 días hábiles)
- Coordinación con divisiones para obtener información solicitada
- Registro de amparos CPLT

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-ETRANSP-01 | Verificar actualización mensual de transparencia activa | Alta |
| UC-ETRANSP-02 | Gestionar solicitudes de acceso a información | Alta |
| UC-ETRANSP-03 | Coordinar respuestas con divisiones | Alta |
| UC-ETRANSP-04 | Alertar vencimientos de plazos de respuesta | Alta |
| UC-ETRANSP-05 | Preparar descargos ante amparos CPLT | Media |
| UC-ETRANSP-06 | Generar reportes de cumplimiento de transparencia | Media |

#### U1.7.2 Encargado de Registro de Lobby

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Supervisar cumplimiento de obligaciones de registro de lobby |
| **Marco Legal** | Ley 20.730 |

**Necesidades:**

- Monitoreo de registros de autoridades en leylobby.gob.cl
- Alertas de audiencias/viajes/donativos no registrados
- Coordinación con sujetos pasivos del GORE
- Preparación de informes para CGR

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-ELOB-01 | Verificar registros de audiencias de autoridades | Alta |
| UC-ELOB-02 | Alertar sobre viajes y donativos no registrados | Alta |
| UC-ELOB-03 | Coordinar con Gobernador designación de sujetos pasivos | Media |
| UC-ELOB-04 | Preparar informes de cumplimiento para CGR | Media |

#### U1.7.3 Coordinador de Transformación Digital (CTD)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Enlace con SGD para implementación de obligaciones TDE |
| **Marco Legal** | Ley 21.180 |

**Necesidades:**

- Estado de implementación de expediente electrónico
- Cumplimiento de plazos de TDE (máximo 31-12-2027)
- Coordinación con divisiones para digitalización de procesos
- Interoperabilidad con otros órganos

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CTD-01 | Monitorear avance de implementación TDE | Alta |
| UC-CTD-02 | Coordinar con SGD lineamientos técnicos | Alta |
| UC-CTD-03 | Gestionar interoperabilidad con otros órganos | Alta |
| UC-CTD-04 | Preparar informes de cumplimiento para CGR | Media |
| UC-CTD-05 | Coordinar capacitación en herramientas digitales | Media |

#### U1.7.4 Encargado de Protección de Datos (DPO)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Cumplimiento de normativa de datos personales |
| **Marco Legal** | Ley 21.719 (Protección de Datos Personales) |

**Necesidades:**

- Inventario de bases de datos con información personal
- Gestión de derechos ARCO (acceso, rectificación, cancelación, oposición)
- Evaluación de impacto en privacidad de nuevos sistemas
- Coordinación de brechas de seguridad

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-DPO-01 | Gestionar solicitudes de derechos ARCO | Alta |
| UC-DPO-02 | Evaluar impacto de privacidad en nuevos proyectos | Alta |
| UC-DPO-03 | Mantener registro de tratamiento de datos | Media |
| UC-DPO-04 | Coordinar respuesta ante brechas de seguridad | Alta |

#### U1.7.5 Oficial de Seguridad de la Información (CISO)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Gestión de políticas de seguridad y riesgos de información |
| **Marco Legal** | Ley 21.663 (Ciberseguridad), DS 7 SGD |

**Necesidades:**

- Dashboard de estado de seguridad de sistemas
- Gestión de incidentes de ciberseguridad
- Cumplimiento de estándares NIST
- Coordinación con CSIRT sectorial

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CISO-01 | Monitorear estado de seguridad de sistemas | Alta |
| UC-CISO-02 | Gestionar incidentes de ciberseguridad | Alta |
| UC-CISO-03 | Evaluar riesgos de seguridad en nuevos sistemas | Alta |
| UC-CISO-04 | Coordinar con CSIRT sectorial | Media |
| UC-CISO-05 | Verificar cumplimiento de DS 7 SGD | Media |

---

### U1.8 Comité Directivo Regional (CDR) (kb_gn_019)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Filtro de pertinencia estratégica de IPR |
| **Composición** | Jefaturas de División, Jefatura de Rezago, Administrador Regional |
| **Presidencia** | Jefatura DIPLADE |

**Necesidades:**

- Vista consolidada de postulaciones pendientes de revisión
- Información de coherencia con ERD y prioridades regionales
- Histórico de decisiones PRE-ADMISIBLE / NO PRE-ADMISIBLE
- Generación rápida de actas de sesión

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CDR-01 | Revisar cartera de postulaciones ingresadas | Alta |
| UC-CDR-02 | Evaluar coherencia con ERD y prioridades | Alta |
| UC-CDR-03 | Categorizar IPR como PRE-ADMISIBLE o NO | Alta |
| UC-CDR-04 | Generar acta de sesión con fundamentación | Alta |
| UC-CDR-05 | Consultar histórico de decisiones por IPR | Media |

**Journey CDR:**

```
DIPLADE convoca sesión → Recibe listado de postulaciones desde DIPIR → Revisa cada IPR
→ Analiza alineación con ERD y prioridades → Debaten en comité → Categoriza PRE-ADMISIBLE/NO
→ Genera acta → DIPIR prioriza para revisión técnica detallada
```

---

### U1.9 Centro Integrado de Emergencia y Seguridad (CIES Ñuble) (kb_gn_080)

| Perfil | Rol | Sistemas |
|--------|-----|----------|
| **Operador CIES** | Monitoreo continuo de cámaras y clasificación de incidentes | VMS CIES, SITIA |
| **Supervisor CIES** | Gestión de incidentes críticos y coordinación con instituciones externas | VMS CIES, SITIA |
| **Soporte Técnico CIES** | Mantenimiento preventivo/correctivo de plataforma | VMS, infraestructura TI |
| **Enlace CIES** | Puente operativo con Carabineros, PDI, Bomberos, SAMU y municipios | VMS, telefonía, radios |

**Necesidades:**

- Consola unificada de incidentes (mapa, video, fichas de contacto).
- Acceso a capas territoriales críticas (barrios prioritarios, rutas de evacuación, puntos sensibles).
- Integración fluida con SITIA (patentes, armas, evidencia).
- Registro estructurado de incidentes, tiempos de respuesta y coordinación interinstitucional.

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CIES-OP-01 | Monitorear en tiempo real cámaras CIES y detectar incidentes | Alta |
| UC-CIES-OP-02 | Clasificar incidentes por prioridad y activar protocolos | Alta |
| UC-CIES-OP-03 | Seguir trayectorias de vehículos/personas en tiempo real | Alta |
| UC-CIES-SUP-01 | Asumir gestión de incidentes críticos y coordinar con enlaces externos | Alta |
| UC-CIES-SUP-02 | Activar planes de contingencia (fallas técnicas, desastres) | Alta |
| UC-CIES-SUP-03 | Validar y escalar solicitudes de evidencia a SITIA-Evidencia | Media |
| UC-CIES-ENL-01 | Recibir alertas desde CIES y coordinar respuesta en terreno | Alta |
| UC-CIES-ENL-02 | Retroalimentar a CIES sobre resultado de la respuesta | Media |
| UC-CIES-ENL-03 | Solicitar apoyo adicional o redireccionar recursos según evolución del evento | Media |

---

### U1.10 Coordinación IDE Regional y Gestión de Información Geoespacial (kb_gn_090)

| Perfil | Rol Principal |
|--------|---------------|
| **Coordinador/a Regional IDE** | Liderar política geoespacial y articular con IDE Chile |
| **UGIT / Equipo SIG** | Operar Geonodo, modelar datos, QA/QC y publicar servicios |
| **Puntos Focales Sectoriales (Geo)** | Asegurar calidad temática y metadatos de capas sectoriales |

**Necesidades:**

- Política clara de datos territoriales y hoja de ruta institucional.
- Herramientas para modelar, validar y publicar capas alineadas a ISO/OGC.
- Mecanismos de coordinación con divisiones y servicios para priorizar datasets.
- Monitoreo de uso, calidad y licenciamiento de datos geoespaciales.

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-IDE-01 | Definir y actualizar la política de información geoespacial del GORE | Alta |
| UC-IDE-02 | Coordinar con IDE Chile la federación de catálogos (CSW) | Alta |
| UC-IDE-03 | Priorizar capas base y temáticas institucionales | Alta |
| UC-IDE-04 | Presentar avances de IDE regional a autoridades y servicios | Media |
| UC-IDE-05 | Articular iniciativas geoespaciales con otros proyectos TDE | Media |
| UC-UGIT-01 | Modelar datos y catálogo de objetos (ISO 19110) | Alta |
| UC-UGIT-02 | Crear metadatos (ISO 19115-1, Perfil Chileno/LAMPv2) | Alta |
| UC-UGIT-03 | Publicar servicios WMS/WFS/WCS y API geoespacial en Geonodo | Alta |
| UC-UGIT-04 | Implementar QA/QC y registrar calidad (ISO 19157) | Alta |
| UC-UGIT-05 | Administrar geoportal y monitorear consumo de datos | Media |
| UC-UGIT-06 | Gestionar seguridad, backup y continuidad de la plataforma | Media |
| UC-PFS-01 | Validar contenido temático y dominios de capas sectoriales | Alta |
| UC-PFS-02 | Completar y revisar metadatos de su área | Alta |
| UC-PFS-03 | Proponer nuevas capas y actualizaciones según políticas sectoriales | Media |

---

### U1.11 Comité de Transformación Digital y Gobernanza de Proyectos TIC (kb_gn_016)

| Perfil | Rol Principal |
|--------|---------------|
| **Comité de Transformación Digital** | Gobernar la TDE institucional, priorizar iniciativas TIC y monitorear el Plan de Transformación Digital (TDE) |
| **PMO TIC** | Estandarizar la gestión de proyectos y portafolios TIC, articulando con DIPRES/EVALTIC |
| **Jefes/as de Proyecto TIC** | Liderar proyectos TIC específicos, coordinando equipos internos y proveedores |

**Necesidades:**

- Vista consolidada del portafolio TIC (estado, riesgos, beneficios esperados).
- Herramientas para aplicar metodologías tradicionales, ágiles o híbridas.
- Articulación fluida con DIPRES (EVALTIC) y con la SGD en estándares de TDE.
- Registro y explotación de lecciones aprendidas de proyectos TIC.

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-COMITETD-01 | Priorizar iniciativas TIC alineadas con la ERD y la estrategia TDE | Alta |
| UC-COMITETD-02 | Monitorear avance de proyectos TIC estratégicos | Alta |
| UC-COMITETD-03 | Resolver conflictos de alcance, plazos o recursos entre proyectos | Media |
| UC-PMOTIC-01 | Mantener inventario de proyectos TIC con indicadores clave | Alta |
| UC-PMOTIC-02 | Establecer y difundir estándares de gestión de proyectos TIC | Alta |
| UC-PMOTIC-03 | Coordinar con DIPRES la presentación y seguimiento de EVALTIC | Alta |
| UC-PMOTIC-04 | Consolidar lecciones aprendidas y buenas prácticas | Media |
| UC-JPTIC-01 | Elaborar Acta de Constitución y Plan de Gestión de Proyecto TIC | Alta |
| UC-JPTIC-02 | Gestionar equipo, cronograma, presupuesto y riesgos | Alta |
| UC-JPTIC-03 | Reportar avances y gestionar cambios aprobados por el Comité TD | Alta |
| UC-JPTIC-04 | Coordinar integración con plataformas compartidas (DocDigital, ClaveÚnica, etc.) | Media |

---

## ESFERA 2: ECOSISTEMA GUBERNAMENTAL

### U2.1 Gobierno Central

| Actor | Necesidades |
|-------|-------------|
| **SUBDERE** | Monitoreo de descentralización, apoyo técnico a transferencia de competencias |
| **DIPRES** | Control financiero, visación presupuestaria, evaluación de programas |
| **MDSF** | Evaluación técnica proyectos (SNI), indicadores sociales |
| **SGD** | Cumplimiento TDE, interoperabilidad, madurez digital |
| **Ministerios** | Coordinación sectorial, convenios de programación |

**Casos de Uso:**

| ID | Caso de Uso | Actor |
|----|-------------|-------|
| UC-GOB-01 | Consultar ejecución presupuestaria regional | DIPRES |
| UC-GOB-02 | Evaluar estado de proyectos RS | MDSF |
| UC-GOB-03 | Monitorear avance transferencia de competencias | SUBDERE |
| UC-GOB-04 | Verificar cumplimiento normas TDE | SGD |

#### U2.1.1 Analista MDSF Regional (kb_gn_019)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Evaluación técnico-económica de IDI en el SNI |
| **Producto** | RATE (RS, FI, OT, AD) |

**Necesidades:**

- Acceso a postulaciones enviadas por el GORE
- Carpeta digital BIP completa y consistente
- Canal de comunicación de observaciones con GORE
- Monitoreo de plazos de evaluación y subsanación

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-MDSF-01 | Recibir postulación de IDI del GORE | Alta |
| UC-MDSF-02 | Realizar evaluación de admisibilidad (≈5 días) | Alta |
| UC-MDSF-03 | Realizar análisis técnico-económico (≈10 días) | Alta |
| UC-MDSF-04 | Emitir RATE (RS/FI/OT/AD) | Alta |
| UC-MDSF-05 | Comunicar observaciones al GORE | Media |
| UC-MDSF-06 | Verificar subsanaciones dentro del plazo (60 días) | Media |

#### U2.1.2 Analista DIPRES/SES Programas Glosa 06 (kb_gn_011)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Evaluación ex-ante de Programas Públicos Regionales (Glosa 06) |
| **Marco Legal** | Ley de Presupuestos, Oficio Circular N°22 DIPRES |

**Necesidades:**

- Formularios de Perfil y Diseño completos y consistentes
- Marco Lógico coherente con objetivos y resultados
- Antecedentes de programas previos y continuidad

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-DIPSES-01 | Recibir y revisar Formulario de Perfil de PPR | Alta |
| UC-DIPSES-02 | Evaluar Formulario de Diseño (MML) | Alta |
| UC-DIPSES-03 | Emitir Recomendación Favorable (RF) o solicitar correcciones | Alta |
| UC-DIPSES-04 | Monitorear plazos y estados de evaluación de programas | Media |

#### U2.1.3 Instituciones habilitadas FRPD (CORFO/ANID) (kb_gn_011)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Ejecución de programas y proyectos financiados con FRPD |
| **Marco Legal** | Ley 21.591 (Royalty), Glosa 13, Res. Ex. N°33 SUBCTCI |

**Necesidades:**

- Definición clara de ámbitos elegibles y líneas FRPD
- Oportunidad en transferencias desde el GORE
- Trazabilidad de metas y resultados comprometidos

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-FRPD-01 | Recibir transferencias FRPD para iniciativas seleccionadas | Alta |
| UC-FRPD-02 | Ejecutar programas/proyectos de fomento e innovación | Alta |
| UC-FRPD-03 | Rendir cuentas de uso de recursos FRPD al GORE | Alta |

#### U2.1.4 SUBDERE (Lineamientos FRIL) (kb_gn_011)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Emisión de lineamientos operativos y normativos FRIL |
| **Marco Legal** | Glosa 12 Ley de Presupuestos |

**Necesidades:**

- Información consolidada de ejecución FRIL a nivel nacional
- Coherencia de criterios de admisibilidad entre regiones
- Retroalimentación del desempeño del programa FRIL en Ñuble

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-SUBDERE-01 | Emitir y actualizar instructivos FRIL para regiones | Alta |
| UC-SUBDERE-02 | Monitorear ejecución FRIL en regiones | Media |
| UC-SUBDERE-03 | Ajustar lineamientos según desempeño y brechas detectadas | Media |

---

#### U2.1.5 Ministerio de las Culturas, las Artes y el Patrimonio (RIS Cultura/Patrimonio)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Definir políticas culturales y patrimoniales, y orientar proyectos culturales y patrimoniales que ingresan al SNI |
| **Marco Legal** | Ley 21.045 y normativa sectorial de patrimonio y cultura |

**Necesidades:**

- Información territorial sobre brechas de acceso cultural
- Cartera de proyectos culturales y patrimoniales priorizados por el GORE
- Coherencia entre proyectos FNDR y políticas/planes sectoriales de cultura y patrimonio

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CULT-01 | Revisar iniciativas culturales FNDR respecto de lineamientos sectoriales | Alta |
| UC-CULT-02 | Coordinar con GORE planes y programas culturales regionales | Media |
| UC-CULT-03 | Proveer criterios técnicos para evaluación de proyectos culturales y patrimoniales | Media |

#### U2.1.6 Consejo de Monumentos Nacionales (CMN) (RIS Patrimonio)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Autorizar intervenciones y proyectos en inmuebles protegidos (monumentos, inmuebles de conservación, zonas típicas) |
| **Marco Legal** | Ley 17.288 sobre Monumentos Nacionales |

**Necesidades:**

- Acceso temprano a antecedentes de proyectos sobre inmuebles protegidos
- Trazabilidad de solicitudes de autorización y pronunciamientos
- Coordinación con GORE y municipios para planes de puesta en valor

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CMN-01 | Recibir y revisar proyectos IPR en inmuebles patrimoniales | Alta |
| UC-CMN-02 | Emitir pronunciamientos y autorizaciones para intervenciones | Alta |
| UC-CMN-03 | Coordinar criterios técnicos con GORE y municipios | Media |

#### U2.1.7 Instituto Nacional de Deportes (IND) (RIS Deportes)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Entregar lineamientos y validación técnica para proyectos de infraestructura deportiva |
| **Marco Legal** | Ley del Deporte y normativa sectorial IND |

**Necesidades:**

- Información sobre cartera regional de proyectos deportivos FNDR
- Datos de oferta y demanda deportiva por territorio y modalidad
- Alineamiento con políticas deportivas nacionales y programas IND

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-IND-01 | Revisar y pronunciarse sobre proyectos de infraestructura deportiva | Alta |
| UC-IND-02 | Validar coherencia de proyectos con estándares y programas IND | Alta |
| UC-IND-03 | Coordinar programas deportivos complementarios a proyectos FNDR | Media |

---

### U2.2 Contraloría General de la República (EXPANDIDO kb_gn_200)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Control externo, legalidad, auditoría, juicio de cuentas |
| **Marco Legal** | DFL 1/1964 (Ley 10.336), Art. 98 CPR |

**Funciones Clave respecto al GORE:**

- Toma de razón de actos administrativos
- Fiscalización y auditoría de fondos regionales
- Emisión de dictámenes vinculantes
- Juicio de cuentas
- Fiscalización de DIP (Ley 20.880)
- Fiscalización de registros de lobby (Ley 20.730)
- Control de obligaciones TDE (Ley 21.180)

**Necesidades:**

- Acceso a rendiciones de cuentas (SISREC)
- Trazabilidad completa de actos administrativos
- Acceso a DIP de autoridades y funcionarios obligados
- Registros de lobby actualizados
- Expedientes electrónicos íntegros
- Información para dictámenes y contiendas de competencia
- Datos para auditorías de ejecución FNDR

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CGR-01 | Verificar rendiciones en SISREC | Alta |
| UC-CGR-02 | Auditar ejecución de fondos regionales | Alta |
| UC-CGR-03 | Acceder a actos administrativos para Toma de Razón | Alta |
| UC-CGR-04 | Fiscalizar oportunidad e integridad de DIP | Alta |
| UC-CGR-05 | Fiscalizar registros de lobby de autoridades GORE | Alta |
| UC-CGR-06 | Emitir dictámenes sobre consultas del GORE | Media |
| UC-CGR-07 | Resolver contiendas de competencia | Media |
| UC-CGR-08 | Instruir o asumir sumarios administrativos | Media |
| UC-CGR-09 | Verificar cumplimiento de obligaciones TDE | Media |
| UC-CGR-10 | Iniciar juicio de cuentas por rendiciones observadas | Alta |

---

### U2.3 Delegación Presidencial Regional (EXPANDIDO kb_gn_031)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Gobierno interior, orden público, coordinación de servicios desconcentrados |
| **Naturaleza** | Órgano desconcentrado del Presidente de la República |
| **Marco Legal** | DFL 1-19.175 (LOC GORE), Ley 21.730 (Ministerio Seguridad Pública) |

**Funciones respecto al GORE:**

- Colaboración en materia de seguridad y emergencias
- Formulación conjunta de necesidades de la región con el Gobernador Regional
- Coordinación de servicios públicos en la región
- Proponer ternas para nombramiento de SEREMI
- Informar al Ministerio del Interior sobre situación regional

**Necesidades:**

- Coordinación con GORE en emergencias y desastres
- Información territorial para gestión de crisis
- Datos de seguridad pública y victimización
- Acceso a diagnósticos regionales para formulación conjunta de necesidades
- Información de servicios públicos desconcentrados

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-DPR-01 | Coordinar respuesta ante emergencias con GORE | Alta |
| UC-DPR-02 | Consultar indicadores de seguridad por comuna | Media |
| UC-DPR-03 | Acceder a información para Consejo Regional de Seguridad | Media |
| UC-DPR-04 | Formular conjuntamente con Gobernador necesidades regionales | Alta |
| UC-DPR-05 | Consultar diagnósticos territoriales para propuestas de SEREMI | Media |
| UC-DPR-06 | Coordinar con GORE situaciones de extranjería regional | Baja |

### U2.3.1 Delegado Presidencial Provincial (NUEVO kb_gn_031)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Gobierno interior a nivel provincial |
| **Cantidad Ñuble** | 3 (Diguillín, Itata, Punilla) |
| **Naturaleza** | Desconcentrado del DPR |

**Necesidades:**

- Información territorial de su provincia
- Coordinación con municipios de su jurisdicción
- Datos de seguridad y emergencias provinciales

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-DPP-01 | Consultar indicadores de su provincia | Media |
| UC-DPP-02 | Coordinar con municipios en emergencias provinciales | Alta |
| UC-DPP-03 | Supervisar ejecución de programas de servicios en la provincia | Media |

---

### U2.4 Municipalidades (21 comunas)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Ejecutores de proyectos, formuladores de iniciativas, gobierno local |

**Necesidades:**

- Postular proyectos al GORE
- Hacer seguimiento de iniciativas aprobadas
- Rendir cuentas de transferencias
- Acceder a asistencia técnica
- Conocer prioridades regionales

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-MUN-01 | Postular proyectos FNDR/FRIL digitalmente | Alta |
| UC-MUN-02 | Consultar estado de proyectos postulados | Alta |
| UC-MUN-03 | Rendir cuentas de transferencias | Alta |
| UC-MUN-04 | Acceder a guías y asistencia técnica | Media |
| UC-MUN-05 | Consultar indicadores de su comuna vs región | Media |
| UC-MUN-06 | Conocer cartera de proyectos que afectan su territorio | Alta |

**Journey Principal (Alcalde/SECPLA):**

```
Identifica necesidad comunal → Consulta líneas de financiamiento disponibles → Prepara perfil de proyecto
→ Postula digitalmente → Recibe observaciones → Corrige y re-postula → Proyecto aprobado
→ Firma convenio → Ejecuta → Rinde cuentas periódicamente → Cierra proyecto
```

#### U2.4.1 Unidad Formuladora Municipal (kb_gn_019)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Formulación y postulación de IPR al GORE |
| **Actores** | SECPLA y equipos técnicos municipales |

**Necesidades:**

- Guías operativas por mecanismo de financiamiento (SNI, FRIL, 8% FNDR, FRPD, etc.)
- Estado de postulaciones en tiempo real
- Notificación temprana de observaciones y plazos de subsanación
- Canal de comunicación con analista GORE responsable

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-UF-01 | Consultar guías y requisitos por mecanismo | Alta |
| UC-UF-02 | Postular IPR digitalmente con oficio conductor | Alta |
| UC-UF-03 | Cargar antecedentes en carpeta digital BIP | Alta |
| UC-UF-04 | Recibir notificación de estado (admisible/observado) | Alta |
| UC-UF-05 | Subsanar observaciones dentro de plazo | Alta |
| UC-UF-06 | Consultar RATE y estado de evaluación en MDSF/SNI | Media |
| UC-UF-07 | Determinar vía de financiamiento adecuada usando árbol de decisión | Alta |
| UC-UF-08 | Verificar elegibilidad FRIL antes de postular | Alta |
| UC-UF-09 | Identificar si proyecto califica para Circular 33 | Media |
| UC-UF-10 | Evaluar alternativa FRPD si tiene foco productivo | Baja |

#### U2.4.2 Unidad Técnica Receptora Municipal

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Ejecución de IPR financiadas por el GORE |
| **Fase** | Post-convenio |

**Necesidades:**

- Documentación técnica aprobada (EE.TT., planos, permisos)
- Claridad en roles, plazos y hitos de control
- Proceso claro de licitación en Mercado Público
- Canal de reporte con Supervisor de Proyecto GORE
- Procedimiento estructurado de rendición de cuentas en SISREC

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-UTR-01 | Coordinar reunión de inicio con GORE | Alta |
| UC-UTR-02 | Ejecutar licitación en Mercado Público | Alta |
| UC-UTR-03 | Reportar avance periódico a Supervisor GORE | Alta |
| UC-UTR-04 | Solicitar modificación de IPR cuando se requiera | Media |
| UC-UTR-05 | Gestionar recepción provisoria y definitiva | Alta |
| UC-UTR-06 | Presentar rendición final en SISREC | Alta |
| UC-UTR-07 | Reintegrar saldos no utilizados | Media |

**Journey Unidad Técnica Receptora:**

```
Recibe convenio formalizado → Coordina reunión de inicio con GORE → Prepara bases de licitación
→ Publica en Mercado Público → Adjudica y firma contrato → Entrega de terreno / Orden de inicio
→ Ejecuta y reporta avances → [Si modificación] Solicita formalmente al GORE
→ Recepción provisoria → Período de garantía → Recepción definitiva
→ Presenta rendición final → Reintegra saldos → Cierre del proyecto
```

---

### U2.5 SEREMI (Secretarías Regionales Ministeriales)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Representantes sectoriales en la región |

**Necesidades:**

- Coordinación con GORE en materias de su sector
- Información territorial para políticas sectoriales
- Participación en convenios de programación

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-SER-01 | Consultar proyectos de su sector en la región | Media |
| UC-SER-02 | Coordinar convenios de programación | Media |
| UC-SER-03 | Acceder a diagnósticos sectoriales | Baja |

---

### U2.6 Consejo para la Transparencia (CPLT) (NUEVO kb_gn_200)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Órgano garante del derecho de acceso a información pública |
| **Marco Legal** | Ley 20.285 |

**Funciones respecto al GORE:**

- Resolver amparos por denegación de información
- Fiscalizar cumplimiento de transparencia activa
- Aplicar sanciones por incumplimiento

**Necesidades:**

- Acceso a información del GORE para resolver amparos
- Verificación de cumplimiento de obligaciones de publicación
- Antecedentes de solicitudes de acceso denegadas

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CPLT-01 | Requerir información al GORE para resolver amparo | Alta |
| UC-CPLT-02 | Verificar cumplimiento de transparencia activa | Alta |
| UC-CPLT-03 | Ordenar entrega de información denegada | Alta |
| UC-CPLT-04 | Aplicar sanciones por incumplimiento | Media |

---

### U2.7 Tribunal de Contratación Pública (NUEVO kb_gn_200)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Órgano jurisdiccional especializado en compras públicas |
| **Sede** | Santiago |
| **Marco Legal** | Ley 19.886 |

**Funciones respecto al GORE:**

- Conocer reclamaciones sobre licitaciones del GORE
- Anular adjudicaciones irregulares
- Resolver controversias con proveedores

**Necesidades:**

- Acceso a antecedentes de procesos de compra impugnados
- Expedientes de licitaciones y adjudicaciones
- Información de bases, aclaraciones y evaluaciones

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-TCP-01 | Requerir expediente de licitación impugnada | Alta |
| UC-TCP-02 | Acceder a bases, aclaraciones y actas de evaluación | Alta |
| UC-TCP-03 | Verificar cumplimiento de procedimientos de compra | Alta |

---

### U2.8 Tribunal Calificador de Elecciones (TRICEL) (NUEVO kb_gn_031)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Órgano jurisdiccional que resuelve causales de cesación del Gobernador Regional |
| **Marco Legal** | DFL 1-19.175 (LOC GORE) |

**Funciones respecto al GORE:**

- Declarar cesación del Gobernador por causales legales
- Resolver requerimientos por notable abandono de deberes o contravención a probidad
- Aplicar suspensión o inhabilidades

**Necesidades:**

- Antecedentes de requerimientos de cesación
- Información sobre actuaciones del Gobernador Regional
- Acceso a registros de acuerdos del CORE

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-TRICEL-01 | Recibir requerimiento de cesación de Gobernador | Alta |
| UC-TRICEL-02 | Acceder a antecedentes de actuaciones cuestionadas | Alta |
| UC-TRICEL-03 | Resolver causales de cesación o inhabilidad | Alta |

---

### U2.9 Dirección de Compras y Contratación Pública (ChileCompra) (NUEVO kb_gn_200)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Órgano rector del sistema de compras públicas |
| **Marco Legal** | Ley 19.886 |

**Funciones respecto al GORE:**

- Administrar plataforma de compras (Mercado Público)
- Gestionar Registro de Proveedores
- Emitir instrucciones obligatorias
- Administrar Convenios Marco

**Necesidades:**

- Información de procesos de compra del GORE
- Verificación de cumplimiento de instrucciones
- Datos de ejecución de convenios marco

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CHCP-01 | Monitorear procesos de compra del GORE | Media |
| UC-CHCP-02 | Recibir reclamos de ciudadanía sobre compras | Media |
| UC-CHCP-03 | Verificar uso de convenios marco | Baja |

---

### U2.10 Comité Interministerial de Descentralización (NUEVO kb_gn_031)

| Dimensión | Detalle |
|-----------|---------|
| **Rol** | Órgano colegiado que analiza y recomienda transferencias de competencias |
| **Presidencia** | Ministro del Interior |
| **Secretaría** | SUBDERE |
| **Marco Legal** | DFL 1-19.175 (LOC GORE) |

**Necesidades:**

- Información sobre solicitudes de transferencia del GORE
- Antecedentes de ejercicio de competencias transferidas
- Evaluaciones del Consejo de Evaluación de Competencias

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CID-01 | Recibir y analizar solicitud de transferencia del GORE | Alta |
| UC-CID-02 | Acceder a informes de comisiones de estudio | Alta |
| UC-CID-03 | Evaluar ejercicio de competencias transferidas | Media |
| UC-CID-04 | Proponer revocación de competencias temporales | Baja |

---

## ESFERA 3: ECOSISTEMA REGIONAL

### U3.1 Ciudadanía General

| Segmento | Características |
|----------|-----------------|
| **Población urbana** | ~71% en ciudades, mayor conectividad |
| **Población rural** | ~29%, menor acceso digital, mayor dispersión |
| **Adultos mayores** | 20.7% >60 años, necesidades específicas |
| **Personas con discapacidad** | 15.3%, requerimientos de accesibilidad |

**Necesidades:**

- Transparencia en uso de recursos públicos
- Acceso a información de proyectos en su territorio
- Participación ciudadana digital
- Trámites simples y accesibles
- Información de servicios disponibles

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-CIU-01 | Consultar proyectos en ejecución en su comuna | Alta |
| UC-CIU-02 | Participar en consultas ciudadanas | Media |
| UC-CIU-03 | Acceder a información de transparencia | Alta |
| UC-CIU-04 | Realizar trámites en línea con el GORE | Alta |
| UC-CIU-05 | Reportar problemas o sugerencias | Media |
| UC-CIU-06 | Conocer indicadores de su comuna | Baja |

**Journey Principal:**

```
Ciudadano escucha de proyecto en su barrio → Busca información en portal GORE → Encuentra detalles del proyecto
→ Consulta plazos y beneficios → Participa en consulta ciudadana si aplica → Monitorea avance de obra
→ Utiliza infraestructura completada
```

---

### U3.2 Organizaciones de la Sociedad Civil

| Tipo | Ejemplos |
|------|----------|
| **COSOC** | Consejo de la Sociedad Civil del GORE |
| **ONG** | Organizaciones sin fines de lucro |
| **Juntas de Vecinos** | Organizaciones territoriales |
| **Clubes deportivos** | Organizaciones funcionales |
| **Organizaciones culturales** | Agrupaciones artísticas, patrimoniales |

**Necesidades:**

- Postular a fondos (Subvenciones 8% FNDR)
- Participar en instancias consultivas
- Rendir cuentas de recursos recibidos
- Acceder a información de convocatorias

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-OSC-01 | Postular a fondos concursables | Alta |
| UC-OSC-02 | Rendir cuentas de subvenciones | Alta |
| UC-OSC-03 | Participar en consultas del COSOC | Media |
| UC-OSC-04 | Acceder a calendario de convocatorias | Media |

---

### U3.3 Sector Empresarial

| Segmento | Características |
|----------|-----------------|
| **Grandes empresas** | Agroindustria, forestal, retail |
| **PYMES** | 7,217 empresas en sector primario |
| **Emprendedores** | Nuevos negocios, innovación |
| **Cooperativas** | Asociatividad productiva |

**Necesidades:**

- Información de programas de fomento productivo
- Acceso a fondos de innovación (FRPD)
- Datos de mercado regional
- Oportunidades de proveeduría al Estado
- Información de infraestructura y conectividad

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-EMP-01 | Consultar programas de fomento disponibles | Alta |
| UC-EMP-02 | Postular a fondos de innovación | Alta |
| UC-EMP-03 | Acceder a datos económicos regionales | Media |
| UC-EMP-04 | Conocer proyectos de infraestructura planificados | Media |
| UC-EMP-05 | Participar en licitaciones públicas | Alta |

---

### U3.4 Academia e Investigación

| Actor | Ejemplos |
|-------|----------|
| **Universidades** | UBB, otras con presencia regional |
| **Centros de investigación** | CTI regional |
| **Investigadores** | Académicos, tesistas |

**Necesidades:**

- Acceso a datos abiertos regionales
- Información para investigación aplicada
- Participación en CCTID
- Colaboración en proyectos de innovación

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-ACA-01 | Acceder a datos abiertos del GORE | Alta |
| UC-ACA-02 | Consultar indicadores socioeconómicos | Alta |
| UC-ACA-03 | Colaborar en proyectos CTI | Media |
| UC-ACA-04 | Participar en instancias de planificación (ERD) | Media |

---

### U3.5 Medios de Comunicación

| Tipo | Ejemplos |
|------|----------|
| **Prensa regional** | Diarios, radios, TV local |
| **Medios digitales** | Portales de noticias |
| **Periodistas** | Cobertura de gestión pública |

**Necesidades:**

- Información de transparencia activa
- Datos para reportajes de interés público
- Acceso a vocerías y comunicados

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-MED-01 | Consultar información de transparencia | Alta |
| UC-MED-02 | Acceder a datos de ejecución presupuestaria | Alta |
| UC-MED-03 | Descargar comunicados y material de prensa | Media |

---

### U3.6 Beneficiarios de Programas Sociales

| Segmento | Características |
|----------|-----------------|
| **Población en pobreza** | 12.1% por ingresos |
| **Adultos mayores vulnerables** | Mayor índice de envejecimiento |
| **Personas con discapacidad** | 15.3% de la población |
| **Pueblos originarios** | 3.9%, principalmente Mapuche |
| **Mujeres jefas de hogar** | Brecha de género en desocupación |

**Necesidades:**

- Información de programas y beneficios disponibles
- Postulación simplificada
- Estado de postulaciones
- Notificaciones de nuevas oportunidades

**Casos de Uso:**

| ID | Caso de Uso | Prioridad |
|----|-------------|-----------|
| UC-BEN-01 | Conocer programas sociales disponibles | Alta |
| UC-BEN-02 | Postular a beneficios | Alta |
| UC-BEN-03 | Consultar estado de postulación | Alta |
| UC-BEN-04 | Recibir notificaciones de nuevos programas | Media |

---

## Matriz Resumen de Usuarios (actualizada kb_gn_019 + kb_gn_031 + kb_gn_200)

| # | Usuario | Esfera | Frecuencia Uso | Criticidad | Volumen |
|---|---------|--------|----------------|------------|---------|
| 1 | Gobernador Regional | 1 | Diaria | Crítica | 1 |
| 2 | Consejeros Regionales | 1 | Semanal | Alta | 16 |
| 3 | Administrador Regional | 1 | Diaria | Alta | 1 |
| 4 | Jefes de División | 1 | Diaria | Alta | 8 |
| 4.1 | Jefatura Preinversión DIPIR | 1 | Diaria | Alta | 1 |
| 4.2 | Jefatura Inversiones DIPIR | 1 | Diaria | Alta | 1 |
| 4.3 | Jefatura Presupuesto DAF | 1 | Diaria | Alta | 1 |
| 5 | Funcionarios GORE (general) | 1 | Diaria | Alta | ~200 |
| 5.1 | Analista Preinversión | 1 | Diaria | Crítica | ~10 |
| 5.2 | Supervisor de Proyecto | 1 | Diaria | Crítica | ~8 |
| 5.3 | Analista Financiero DAF | 1 | Diaria | Alta | ~5 |
| 5.4 | Profesional Presupuesto | 1 | Diaria | Alta | ~4 |
| 5.5 | Unidad de Control de Rendiciones (U.C.R.) | 1 | Diaria | Alta | ~5 |
| 5.6 | Analista Otorgante SISREC | 1 | Diaria | Crítica | ~10 |
| 5.7 | Encargado Otorgante SISREC | 1 | Diaria | Alta | ~3 |
| 6 | Unidad de Control Interno | 1 | Diaria | Alta | 5 |
| 7 | Comité Directivo Regional (CDR) | 1 | Semanal | Alta | ~10 |
| 7.1 | Encargado de Transparencia | 1 | Diaria | Alta | 1 |
| 7.2 | Encargado de Registro de Lobby | 1 | Semanal | Media | 1 |
| 7.3 | Coordinador TDE (CTD) | 1 | Diaria | Alta | 1 |
| 7.4 | DPO (Protección de Datos) | 1 | Semanal | Media | 1 |
| 7.5 | CISO (Seguridad Información) | 1 | Diaria | Alta | 1 |
| 8 | SUBDERE/DIPRES/MDSF (central) | 2 | Periódica | Alta | 10 |
| 8.1 | Analista MDSF Regional | 2 | Frecuente | Crítica | ~3 |
| 9 | Contraloría General de la República | 2 | Periódica | Crítica | 5 |
| 10 | Delegación Presidencial Regional | 2 | Semanal | Media | 5 |
| 10.1 | Delegados Presidenciales Provinciales | 2 | Semanal | Media | 3 |
| 11 | Municipalidades | 2 | Frecuente | Alta | 21 |
| 11.1 | Unidad Formuladora Municipal | 2 | Frecuente | Crítica | ~42 |
| 11.2 | Unidad Técnica Receptora Municipal | 2 | Frecuente | Crítica | ~42 |
| 12 | SEREMI | 2 | Periódica | Media | 20 |
| 13 | Consejo para la Transparencia (CPLT) | 2 | Ocasional | Alta | 3 |
| 14 | Tribunal de Contratación Pública | 2 | Ocasional | Media | 2 |
| 15 | Tribunal Calificador de Elecciones (TRICEL) | 2 | Excepcional | Alta | 2 |
| 16 | Dirección de Compras y Contratación Pública (ChileCompra) | 2 | Periódica | Media | 3 |
| 17 | Comité Interministerial de Descentralización | 2 | Ocasional | Media | 5 |
| 18 | DIPRES/SES (Evaluación Programas) | 2 | Periódica | Alta | 5 |
| 19 | CORFO/ANID (FRPD) | 2 | Ocasional | Media | 3 |
| 20 | SUBDERE (Lineamientos FRIL) | 2 | Ocasional | Media | 3 |
| 21 | Comisión Evaluadora FRPD | 1 | Anual | Alta | ~11 |
| 22 | División GORE Patrocinante de PPR transferidos | 1 | Frecuente | Alta | ~6 |
| 23 | Ciudadanía | 3 | Variable | Alta | ~500,000 |
| 24 | Organizaciones de la Sociedad Civil | 3 | Periódica | Media | ~1,000 |
| 25 | Empresas | 3 | Variable | Media | ~7,000 |
| 26 | Academia | 3 | Periódica | Media | ~500 |
| 27 | Medios de Comunicación | 3 | Frecuente | Media | ~50 |
| 28 | Beneficiarios de Programas Sociales | 3 | Variable | Alta | ~60,000 |
| 29 | Ministerio de las Culturas, las Artes y el Patrimonio | 2 | Periódica | Media | ~3 |
| 30 | Consejo de Monumentos Nacionales (CMN) | 2 | Ocasional | Alta | ~3 |
| 31 | Instituto Nacional de Deportes (IND) | 2 | Ocasional | Alta | ~3 |
| 32 | Operador CIES | 1 | Diaria | Crítica | ~12 |
| 33 | Supervisor CIES | 1 | Diaria | Alta | ~4 |
| 34 | Soporte Técnico CIES | 1 | Diaria | Alta | ~3 |
| 35 | Enlace CIES (Carabineros/PDI/Bomberos/SAMU) | 2 | Diaria | Crítica | ~8 |
| 36 | Coordinador/a Regional IDE | 1 | Diaria | Alta | 1 |
| 37 | UGIT / Equipo SIG institucional | 1 | Diaria | Alta | ~5 |
| 38 | Puntos Focales Sectoriales (Geo) | 1 | Semanal | Media | ~8 |
| 39 | Comité de Transformación Digital institucional | 1 | Mensual | Alta | ~8 |
| 40 | PMO TIC institucional | 1 | Diaria | Alta | ~3 |
| 41 | Jefes/as de Proyecto TIC | 1 | Diaria | Alta | ~5 |
| 42 | Secretaría de Gobierno Digital (SGD) | 2 | Periódica | Alta | ~5 |
| 43 | Proveedores TIC estratégicos del Estado (cloud/SaaS compartidos) | 2 | Periódica | Media | ~10 |

---

## Journeys Críticos para el Gemelo Digital

### Journey 1: Ciclo de Inversión Pública Regional

```
[Municipio postula] → [GORE evalúa admisibilidad] → [Evaluación técnica SNI/GORE] 
→ [Priorización Gobernador] → [Aprobación CORE] → [Formalización convenio]
→ [Ejecución y seguimiento] → [Rendición de cuentas] → [Cierre y evaluación]
```

### Journey 2: Monitoreo Territorial en Tiempo Real

```
[Sensor/fuente externa genera dato] → [Gemelo integra información] 
→ [Sistema detecta anomalía] → [Alerta a autoridad correspondiente]
→ [Autoridad toma decisión] → [Acción correctiva] → [Monitoreo de resultados]
```

### Journey 3: Participación Ciudadana

```
[Ciudadano accede al portal] → [Consulta proyectos en su comuna]
→ [Encuentra consulta ciudadana activa] → [Participa con opinión/voto]
→ [Sistema consolida resultados] → [Autoridad considera en decisión]
→ [Ciudadano ve impacto de su participación]
```

### Journey 4: Gestión de Emergencias

```
[Evento crítico detectado] → [Sistema activa alertas multicanal]
→ [Autoridades coordinan respuesta] → [Gemelo muestra recursos disponibles]
→ [Despliegue de respuesta] → [Monitoreo en tiempo real]
→ [Evaluación de daños] → [Planificación de reconstrucción]
```

### Journey 5: Subsanación de Observaciones IPR (kb_gn_019)

```
[MDSF/GORE emite OT o FI] → [Analista GORE notifica a Unidad Formuladora]
→ [Unidad Formuladora recibe observaciones detalladas] → [Prepara correcciones]
→ [Carga antecedentes corregidos en BIP] → [Plazo de subsanación: hasta 60 días hábiles]
→ [Analista GORE verifica subsanación] → [Reenvía a evaluador]
→ [Si OK → RS/RF/AD] → [Si NO → nueva iteración o rechazo]
```

### Journey 6: Gestión de Modificación de IPR en Ejecución

```
[UT detecta necesidad de cambio] → [Prepara informe técnico-financiero]
→ [Envía oficio formal al Gobernador] → [Supervisor GORE analiza pertinencia]
→ [DIPIR/DIPLADE evalúan si supera umbrales CORE/SNI] → [Si > umbral → vuelve a CORE]
→ [Depto. Presupuesto modifica presupuesto y convenio] → [Nueva tramitación de Res/Dec]
→ [Continúa ejecución con modificación aprobada]
```

### Journey 7: Cierre y Rendición Final de IPR

```
[UT finaliza ejecución física] → [Recepción provisoria de obras]
→ [Período de garantía] → [Recepción definitiva]
→ [UT elabora informe final técnico] → [Supervisor GORE valida]
→ [UT presenta rendición final en SISREC] → [Analista Financiero revisa]
→ [Si observaciones → UT subsana] → [Si OK → aprueba rendición]
→ [Se solicita reintegro de saldos cuando corresponda] → [Profesional Presupuesto elabora Res. de Cierre]
→ [Devolución de garantías] → [IPR cerrada]
```

### Journey 8: Solicitud de Acceso a Información Pública (kb_gn_200)

```
[Ciudadano presenta solicitud] → [Encargado Transparencia recibe y registra]
→ [Coordina con división competente] → [Plazo 20 días hábiles]
→ [Si información completa → entrega] → [Si reservada → deniega fundadamente]
→ [Si fuera de plazo o denegada → ciudadano puede reclamar ante CPLT]
→ [CPLT resuelve amparo] → [Si acoge → ordena entrega y puede sancionar]
```

### Journey 9: Proceso de Compra Pública (kb_gn_200)

```
[División detecta necesidad] → [DAF evalúa mecanismo: licitación/trato directo/convenio marco]
→ [Si licitación pública → elabora bases → publica en Mercado Público]
→ [Proveedores presentan ofertas] → [Comisión evalúa] → [Adjudica]
→ [Si reclamo → Tribunal Contratación Pública puede anular]
→ [Contrato vigente] → [Supervisión de ejecución] → [Pago según estados de avance]
```

### Journey 10: Transferencia de Competencias (kb_gn_031)

```
[Gobernador propone transferencia al CORE] → [CORE aprueba por mayoría absoluta]
→ [Envía solicitud al Presidente] → [Comité Interministerial analiza]
→ [Comisión de estudio emite informe] → [Comité recomienda]
→ [Presidente resuelve por decreto supremo ≤6 meses]
→ [Si aprobada → GORE asume competencia con recursos]
→ [Consejo de Evaluación monitorea ejercicio]
→ [Si temporal y deficiente → puede revocarse]
```

### Journey 11: Cumplimiento de Probidad y DIP (kb_gn_200)

```
[Autoridad asume cargo] → [Presenta DIP ante CGR en 30 días]
→ [DIP se publica en sitio web institucional]
→ [Actualización anual en marzo] → [CGR fiscaliza integridad y oportunidad]
→ [Si incumplimiento → apercibimiento → multa → eventual destitución]
→ [Si conflicto de interés detectado → deber de abstención o enajenación]
```

### Journey 12: Gestión de Expediente Electrónico TDE (kb_gn_200)

```
[Solicitud ingresa al GORE] → [Se registra en expediente electrónico]
→ [Actuaciones se incorporan cronológicamente con firma electrónica]
→ [Si documento en papel → se digitaliza e incorpora inmediatamente]
→ [Notificaciones por domicilio digital] → [Resolución con FEA del Gobernador]
→ [Expediente se archiva electrónicamente] → [Transferencia al Archivo Nacional en formato digital]
```

### Journey 13: Selección de Vía de Financiamiento (kb_gn_011)

```
[Formulador identifica necesidad] → [Clasifica: proyecto vs programa]
→ [Si proyecto] → [¿Municipio + <5000 UTM + infraestructura? → FRIL]
→ [¿Conservación/estudios/ANF especiales? → Circular 33]
→ [¿Foco productivo/innovación + entidad habilitada? → FRPD]
→ [Si ninguna anterior → SNI General]
→ [Si programa] → [¿OCSFL/comunitaria en líneas sociales/cultura/deporte? → 8% FNDR]
→ [¿GORE ejecutor directo? → Glosa 06]
→ [¿Otra entidad pública? → Transferencia Pública]
→ [¿Programa de fomento productivo/innovación? → FRPD Programático]
→ [Selecciona vía y prepara postulación según requisitos específicos]
```

### Journey 14: Postulación Municipal a FRIL (kb_gn_026)

```
[SECPLA identifica necesidad de infraestructura menor] → [Verifica elegibilidad FRIL (<4.545 UTM y tipología válida)]
→ [Prepara carpeta documental (Oficio, Ficha IDI, EETT, presupuesto, propiedad)] → [Ingresa postulación vía GESDOC/BIP]
→ [GORE revisa admisibilidad] → [Analista DIPIR evalúa técnicamente y emite RATE RS/FI/OT]
→ [Si FI/OT → municipio subsana en plazo] → [Si RS → iniciativa entra a cartera financiable]
→ [CORE aprueba financiamiento] → [Se firma convenio] → [Municipio licita, ejecuta y rinde cuentas]
```

### Journey 15: Concurso 8% Vinculación con la Comunidad (kb_gn_028)

```
[Organización comunitaria conoce convocatoria] → [Verifica requisitos (antigüedad, domicilio, rendiciones)]
→ [Prepara formularios, cartas y antecedentes] → [Postula en plataforma web del GORE]
→ [GORE revisa admisibilidad documental] → [Comisión técnica evalúa y asigna puntaje]
→ [Si supera puntaje de corte y hay presupuesto → adjudicación] → [Se firma convenio y se transfieren recursos]
→ [Organización ejecuta actividades en plazo de 8 meses] → [Rinde cuentas según instructivo y Res. 30/2015]
```

### Journey 16: Postulación y Evaluación de Iniciativas Circular 33 (kb_gn_029)

```
[Servicio/Municipio identifica necesidad de estudio/ANF/conservación/emergencia] → [Determina categoría C33 adecuada]
→ [Prepara Ficha IDI, Fichas C33 y anexos (TDR, EETT, presupuesto, certificaciones)]
→ [Ingresa antecedentes vía GESDOC con respaldo en BIP] → [GORE revisa admisibilidad]
→ [Analista aplica matriz documental C33 y evalúa técnica/económicamente] → [Emite RATE RS/AD/FI/OT]
→ [Si RS/AD → se habilita financiamiento y se tramita convenio o acto administrativo correspondiente]
→ [Ejecución de la iniciativa y seguimiento según tipo (estudio, ANF, conservación, emergencia)]
```

### Journey 17: Formulación de Proyecto Deportivo con RIS Sectorial (kb_gn_010_ris_deportes_koda.yml)

```
[Municipio identifica necesidad de infraestructura deportiva] → [Clasifica modalidad (formativo, recreativo, competitivo, alto rendimiento)]
→ [Define escala según aforo y costo] → [Aplica RIS-DEPORTES-2024 y completa planilla sector deporte]
→ [Calcula CAE Deportista y, si aplica, CAE Espectador con prorrateo de áreas mixtas]
→ [Verifica umbrales (0,075 / 0,11 / 0,12 UTM) y consistencia con políticas deportivas e IND]
→ [Prepara carpeta con antecedentes técnicos, programa arquitectónico y plan de gestión]
→ [Ingresa iniciativa al SNI a través del GORE] → [MDSF evalúa, emite RATE y se coordina con IND cuando corresponda]
```

### Journey 18: Ciclo Presupuestario Anual del GORE (kb_gn_018)

```
[DIPIR formula ARI y PROPIR con servicios y municipios] → [DAF proyecta gastos de funcionamiento y aplica clasificadores]
→ [Gobernador consolida y propone presupuesto al CORE (10 días)] → [CORE aprueba/modifica en 10 días]
→ [Gobernador envía distribución aprobada a DIPRES (5 días)] → [DIPRES emite resoluciones de presupuesto inicial (10 días)]
→ [CGR toma razón de resoluciones] → [DAF carga presupuesto en SIGFE y DIPIR concilia con BIP/PROPIR]
→ [Durante el año: ejecución mensual, modificaciones presupuesto, reportes a DIPRES/CORE/CGR]
→ [Cierre: corte de compromisos, cálculo deuda flotante, cierre SIGFE, evaluación de resultados]
```

### Journey 19: Gestión de Rendiciones de Transferencias vía SISREC (kb_gn_020)

```
[GORE transfiere recursos a ejecutor con convenio tramitado] → [Ejecutor acepta proyecto en SISREC]
→ [Analista Ejecutor registra informe de rendición mensual con respaldo digitalizado] → [Ministro de Fe verifica autenticidad y envía al Encargado Ejecutor]
→ [Encargado Ejecutor firma con FEA y envía rendición al GORE]
→ [Analista Otorgante (RTF) revisa transacciones, aprueba/observa y deriva a Encargado Otorgante]
→ [Encargado Otorgante (Jefe DAF) firma informe de aprobación total/parcial o devuelve con observaciones]
→ [UCR contabiliza en SIGFE y archiva expediente] → [Si hay montos no ejecutados/observados, se gestiona reintegro]
→ [Historial de rendiciones alimenta decisiones de nuevos financiamientos y auditorías]
```

### Journey 20: Respuesta a Incidente de Seguridad desde CIES (kb_gn_080)

```
[CIES detecta evento o recibe alerta SITIA (armas, patentes, incidentes en vía pública)] → [Operador CIES verifica y clasifica prioridad]
→ [Si prioridad alta → Supervisor CIES asume el caso y notifica a enlaces de Carabineros/PDI/Bomberos/SAMU]
→ [Se coordinan recursos en tiempo real usando Video Wall, comunicaciones directas y capas territoriales críticas]
→ [Se registra evidencia relevante en SITIA-Evidencia con cadena de custodia digital]
→ [Si se requiere → se remite evidencia al Ministerio Público u órgano competente]
```

### Journey 21: Publicación de Capa Geoespacial Institucional en Geonodo (kb_gn_090)

```
[Punto Focal Sectorial identifica necesidad de nueva capa territorial] → [Define especificación de producto (ISO 19131) y catálogo de objetos (ISO 19110)]
→ [UGIT captura o integra datos (formularios, ETL, fuentes externas)] → [Aplica QA/QC según ISO 19157]
→ [UGIT documenta metadatos en Perfil Chileno/LAMPv2 (ISO 19115-1)] → [Asesoría Jurídica define licencia (CC BY 4.0/ODbL)]
→ [UGIT publica capa en Geonodo como servicios WMS/WFS y la registra en CSW para IDE Chile]
→ [Geoportal institucional expone la capa con visor y enlaces de descarga] → [Se monitorean indicadores de uso e impacto]
```

### Journey 22: Ciclo de Inversión TIC (EVALTIC) (kb_gn_016)

```
[División identifica necesidad de proyecto TIC] → [Jefe/a de Proyecto TIC y PMO TIC clasifican iniciativa (Operación/Crecimiento/Transformación)]
→ [Se elabora formulario EVALTIC con alineamiento a TDE y política Cloud First] → [DIPRES evalúa formulación, gobernanza, riesgos y uso de plataformas compartidas]
→ [Si EVALTIC aprobado → se asigna presupuesto y se incorpora al portafolio TIC institucional]
→ [Comité de Transformación Digital prioriza y monitorea el proyecto] → [Jefe/a de Proyecto ejecuta con metodología tradicional/ágil/híbrida]
→ [Se registran avances, cambios y lecciones aprendidas] → [Cierre de proyecto y traspaso a operación con soporte permanente]
```

### Journey 23: Planificación Territorial Inteligente con Modelo GORE 4.0 (kb_gn_900)

```
[Centro de Inteligencia Territorial consolida datos territoriales, sociales, económicos y ambientales] → [Gemelo Digital integra capas ERD, PROT y otros instrumentos]
→ [Plataformas de participación ciudadana recogen aportes que son sintetizados con apoyo de IA]
→ [DIPLADE utiliza el Gemelo Digital para simular escenarios de proyectos y políticas públicas]
→ [Gobernador y CORE evalúan alternativas de inversión usando resultados de simulaciones]
→ [Se acuerdan carteras (ARI, PROPIR, convenios) alineadas con la visión de largo plazo]
→ [Ejecución y coordinación con servicios y municipios se monitorea en tiempo real desde el Gemelo Digital]
```

---

**[hecho]** Identificados 43+ tipos de usuarios, 145+ casos de uso, 23 journeys críticos.

**[inferencia]** Los nuevos roles de cumplimiento (Transparencia, Lobby, CTD, DPO, CISO), de gestión de rendiciones (UCR, Analista/Encargado Otorgante), de seguridad (CIES-SITIA), de gestión geoespacial (IDE/Geonodo) y de Transformación Digital (Comité TD, PMO TIC, Jefes de Proyecto TIC, SGD) son transversales y deben integrarse al diseño del gemelo digital desde el inicio.

**[inferencia]** Los actores externos de control y coordinación (CGR, CPLT, TCP, TRICEL, IDE Chile, SPD, organismos internacionales y proveedores TIC estratégicos) requieren interfaces de acceso específicas para fiscalización, coordinación y resolución de controversias.

**[inferencia]** El árbol de decisión de financiamiento, el catálogo de RIS sectoriales, el ciclo presupuestario, la arquitectura CIES-SITIA, los lineamientos geoespaciales (Geonodo/IDE), la guía maestra de TDE y la visión GORE 4.0 deben reflejarse en journeys interactivos para formuladores internos y externos, reduciendo errores, tiempos de tramitación y mejorando la gestión de riesgos y la calidad de las decisiones.
