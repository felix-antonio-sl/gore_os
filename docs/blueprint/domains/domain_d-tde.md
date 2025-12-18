# D-TDE: Dominio de Gobernanza Digital

> Parte de: [GORE_OS Vision General](../vision_general.md)
> Capa: Habilitante (Dimensión Tecnológica)  
> Función GORE: GESTIONAR (Soporte Digital)  
> División: DAF (Departamento Informática) / Unidad de Transformación Digital

---

## Glosario D-TDE

| Término                           | Sigla | Definición                                                                             |
| --------------------------------- | ----- | -------------------------------------------------------------------------------------- |
| Transformación Digital del Estado | TDE   | Proceso de cambio cultural y tecnológico para mejorar servicios públicos (Ley 21.180). |
| Plataforma Integ. Serv. Estado    | PISEE | Bus de interoperabilidad del Estado para intercambio de datos entre instituciones.     |
| Coord. Transformación Digital     | CTD   | Rol encargado de lider### Notas de Implementación de la Ley TDE en la institución.     |
| Oficial Seguridad Información     | CISO  | Responsable de la gestión de riesgos de seguridad de la información.                   |
| Delegado Protección Datos         | DPO   | Rol responsable de garantizar el cumplimiento de la Ley de Protección de Datos.        |
| Equipo Resp. Incidentes           | CSIRT | Centro de Respuesta ante Incidentes de Seguridad Informática del Gobierno.             |
| Catálogo Procedimientos           | CPAT  | Inventario oficial de trámites y procedimientos administrativos de la institución.     |
| Identidad Única Estado            | IUIe  | Código único que identifica un expediente electrónico en el Estado.                    |
| Derechos ARCO                     | ARCO  | Derechos de Acceso, Rectificación, Cancelación y Oposición sobre datos personales.     |
| Esquema Nac. Seguridad Inf.       | ENSI  | Conjunto de normas y estándares de seguridad (DS 7) basados en ISO 27001/NIST.         |

---

## Propósito

Gestionar la gobernanza digital y el cumplimiento normativo (Ley TDE, Ciberseguridad) del GORE, y liderar la articulación del ecosistema digital regional, facilitando capacidades tecnológicas y estándares comunes para municipios y servicios públicos de la región, posicionando al GORE como motor de modernización territorial.

Fundamento Legal: Ley 21.180 (TDE), Ley 21.663 (Ciberseguridad), Ley 21.719 (Datos Personales), Decreto Supremo 4/2020 (Reglamento TDE).

---

## Diagrama de Dominio

```mermaid
flowchart TB
    subgraph GOBERNANZA["🏛️ Gobernanza Digital"]
        COMITE["Comité TDE"]
        CTD["Coordinador TD"]
        CISO["Oficial Seguridad"]
        DPO["Delegado Datos"]
    end

    subgraph NORMATIVA["📜 Cumplimiento"]
        CPAT["Catálogo CPAT<br/>DS 11"]
        POLITICAS["Políticas Seguridad<br/>DS 7"]
        RAT["Registro Tratamiento<br/>LDP"]
    end

    subgraph SERVICIOS["☁️ Servicios Digitales"]
        AUTH["Autenticación<br/>ClaveÚnica"]
        DOC["Gestión Documental<br/>DocDigital"]
        NOTIF["Notificaciones<br/>Digitales"]
        FIRMA["FirmaGob"]
    end

    subgraph INFRAESTRUCTURA["🔒 Infraestructura & Ciberseguridad"]
        INTEROP["Interoperabilidad<br/>Nodo PISEE"]
        RED["Red CIES<br/>316 Nodos"]
        SOC["SOC Regional<br/>Monitoreo"]
    end

    GOBERNANZA --> NORMATIVA
    NORMATIVA --> SERVICIOS
    SERVICIOS --> INFRAESTRUCTURA
    COMITE --> CPAT
    CISO --> SOC
    CTD --> INTEROP
```

---

## Módulos

### M1: Cumplimiento TDE

| Atributo    | Descripción                                                                    |
| ----------- | ------------------------------------------------------------------------------ |
| Propósito   | Gestionar el ciclo de vida de digitalización de trámites y calidad de servicio |
| Componentes | CPAT, Medición de Satisfacción, Plan de Mejora Continua                        |

Funcionalidades:

- Gestión del Catálogo de Procedimientos (CPAT) nivel 0-5
- Dashboard de cumplimiento decretos DS 7-12
- Gate de evaluación de proyectos TIC (EvalTIC)

### M2: Servicios Digitales Habilitantes

| Atributo    | Descripción                                                             |
| ----------- | ----------------------------------------------------------------------- |
| Propósito   | Proveer capacidades transversales de identidad y gestión administrativa |
| Componentes | Broker ClaveÚnica, Integrador DocDigital, Motor Notificaciones          |

Funcionalidades:

- Autenticación centralizada (SSO) con ClaveÚnica (OIDC)
- Firma electrónica avanzada y simple (FirmaGob)
- Notificaciones electrónicas legales (DS 8) con domicilio digital

### M3: Interoperabilidad Regional

| Atributo    | Descripción                                                 |
| ----------- | ----------------------------------------------------------- |
| Propósito   | Facilitar el intercambio de datos con el ecosistema público |
| Componentes | Nodo PISEE, Gestor de Convenios, API Gateway                |

Funcionalidades:

- Consumo y publicación de servicios web SOAP/REST
- Gestión de acuerdos de intercambio de información
- Trazabilidad centralizada de transacciones de datos

### M4: Ciberseguridad & Protección de Datos

| Atributo    | Descripción                                                                 |
| ----------- | --------------------------------------------------------------------------- |
| Propósito   | Proteger la confidencialidad, integridad y disponibilidad de la información |
| Componentes | ISMS, Gestión Incidentes, Privacy Hub                                       |

Funcionalidades:

- Gestión de activos de información y análisis de riesgos
- Reporte automático de incidentes a CSIRT
- Gestión de consentimientos y solicitudes ARCO (Datos Personales)

---

### M5: Liderazgo Digital Regional (Gobernanza Expandida)

| Atributo    | Descripción                                                                         |
| ----------- | ----------------------------------------------------------------------------------- |
| Propósito   | Liderar y articular el ecosistema digital regional (Municipios, Servicios Públicos) |
| Componentes | Mesa Regional TDE, Kit Digital Municipal, CSIRT Regional (Coordinación)             |

Funcionalidades:

- Transferencia de capacidades y estándares TDE a municipios (especialmente zonas rezagadas)
- Coordinación de Mesa Regional de Transformación Digital
- Articulación de respuestas ante ciberataques a nivel regional (Red de CISO regionales)
- Compartición de activos digitales (software público regional)

### M6: Vinculación Territorial Digital

| Atributo     | Descripción                                                                    |
| ------------ | ------------------------------------------------------------------------------ |
| Propósito    | Proveer soluciones tecnológicas compartidas a los municipios (Economía Escala) |
| Beneficiario | Municipios y Servicios Públicos Locales                                        |

Funcionalidades:

- Gestión centralizada de Firmas Electrónicas Municipales (Convenio Marco)
- API Gateway Regional para interoperabilidad municipal (DIDECO, DOM, Tránsito)
- Soporte de infraestructura crítica y conectividad (Zonas Rezagadas)

---

## Procesos BPMN

### Mapa General de Procesos

```mermaid
flowchart LR
    subgraph DTDE["D-TDE: Gobernanza Digital"]
        P1["P1: Gestión Cumplimiento TDE<br/>(Interno)"]
        P2["P2: Habilitación Servicios<br/>(Interno)"]
        P3["P3: Ciberseguridad & Datos<br/>(Transversal)"]
        P4["P4: Interoperabilidad<br/>(PISEE)"]
        P5["P5: Coordinación Regional<br/>(Municipios/Servicios)"]
    end

    P1 --> P2
    P2 --> P3
    P2 --> P4
    P1 -.-> P5
    P5 -.-> P4
```

---

### P1: Gestión Cumplimiento TDE

```mermaid
flowchart TB
    subgraph P1["P1: Gestión Cumplimiento TDE"]
        P1_1["1.1 Actualización<br/>CPAT"]
        P1_2["1.2 Evaluación<br/>Proyectos TIC"]
        P1_3["1.3 Medición<br/>Brechas"]
        P1_4["1.4 Plan Mejora<br/>Continua"]
    end

    P1_1 --> P1_3 --> P1_4
    P1_2 --> P1_4

    P1_1 -.- N1["Inventario trámites<br/>Nivel digitalización"]
    P1_2 -.- N2["Gate EvalTIC<br/>Presupuesto"]
    P1_3 -.- N3["Dashboard DS 7-12<br/>Semaforización"]
    P1_4 -.- N4["Reporte anual SGD<br/>Compromisos"]
```

Actores: CTD, Comité TDE, Unidades de Negocio  
Frecuencia: Semestral (Reporte SGD) / Por proyecto

---

### P2: Habilitación Servicios Digitales

```mermaid
flowchart TB
    subgraph P2["P2: Habilitación Servicios Digitales"]
        P2_1["2.1 Solicitud<br/>Integración"]
        P2_2["2.2 Configuración<br/>Ambientes"]
        P2_3["2.3 Certificación<br/>Técnica"]
        P2_4["2.4 Pase a<br/>Producción"]
    end

    P2_1 --> P2_2 --> P2_3 --> P2_4

    P2_1 -.- N1["Requerimiento: ClaveÚnica<br/>FirmaGob o Notificación"]
    P2_2 -.- N2["Credenciales Sandbox<br/>Config API"]
    P2_3 -.- N3["Pruebas funcionales<br/>Seguridad (OIDC)"]
    P2_4 -.- N4["Switch Prod<br/>Monitoreo"]
```

Actores: Desarrolladores, Administrador TI, CTD  
Frecuencia: A demanda (nuevos sistemas)

---

### P3: Ciberseguridad & Protección Datos

```mermaid
flowchart TB
    subgraph P3["P3: Ciberseguridad & Datos"]
        P3_1["3.1 Identificar<br/>Activos/Riesgos"]
        P3_2["3.2 Proteger<br/>(Controles)"]
        P3_3["3.3 Detectar<br/>Incidente"]
        P3_4["3.4 Responder<br/>& Recuperar"]
        P3_5["3.5 Gestión<br/>Privacidad"]
    end

    P3_1 --> P3_2
    P3_3 --> P3_4
    P3_1 -.-> P3_5

    P3_1 -.- N1["Inventario Activos<br/>Clasificación CIA"]
    P3_3 -.- N2["Monitoreo SOC<br/>Alertas"]
    P3_4 -.- N3["Reporte CSIRT<br/>Continuidad BCP"]
    P3_5 -.- N4["Solicitudes ARCO<br/>Registro Tratamiento"]
```

Actores: CISO, DPO, NOC/SOC, CSIRT Nacional  
Frecuencia: Continua (Monitoreo) / Incidentes

---

### P4: Gestión Interoperabilidad

```mermaid
flowchart TB
    subgraph P4["P4: Gestión Interoperabilidad"]
        P4_1["4.1 Definición<br/>Necesidad"]
        P4_2["4.2 Acuerdo<br/>Intercambio"]
        P4_3["4.3 Habilitación<br/>Técnica"]
        P4_4["4.4 Operación<br/>& Auditoría"]
    end

    P4_1 --> P4_2 --> P4_3 --> P4_4

    P4_1 -.- N1["Datos requeridos<br/>Justificación legal"]
    P4_2 -.- N2["Convenio inst.<br/>Protocolo datos"]
    P4_3 -.- N3["Config Nodo PISEE<br/>Mapeo campos"]
    P4_4 -.- N4["Log transaccional<br/>SLA disponibilidad"]
```

Actores: CTD, Contraparte (Institución), Jurídica  
Frecuencia: A demanda

---

### P5: Articulación Ecosistema Regional

```mermaid
flowchart TB
    subgraph P5["P5: Articulación Ecosistema Regional TDE"]
        P5_1["5.1 Diagnóstico<br/>Regional"]
        P5_2["5.2 Mesa de<br/>Trabajo TDE"]
        P5_3["5.3 Transferencia<br/>Capacidades"]
        P5_4["5.4 Monitoreo<br/>Regional"]
    end

    P5_1 --> P5_2 --> P5_3 --> P5_4

    P5_1 -.- N1["Nivel madurez digital<br/>Municipios/Servicios"]
    P5_2 -.- N2["Definición de estándares<br/>Priorización de brechas"]
    P5_3 -.- N3["Kits digitales<br/>Asesoría técnica GORE"]
    P5_4 -.- N4["Índice TDE Regional<br/>Reporte avance"]
```

Actores: Gobernador, CTD GORE, Alcaldes, Jefes Servicios  
Frecuencia: Trimestral (Mesa) / Continua (Apoyo)

---

## Catálogo por Proceso

### Selección de US Clave

| ID                 | Título                             | Proceso | Prioridad |
| ------------------ | ---------------------------------- | ------- | --------- |
| US-TDE-CALIDAD-001 | Mantener Catálogo de Plataformas   | P1      | Alta      |
| US-TDE-AVANCE-001  | Dashboard avance TDE               | P1      | Alta      |
| US-TDE-AUTH-001    | Integrar ClaveÚnica OIDC           | P2      | Crítica   |
| US-TDE-NOTIF-001   | Integrar Plataforma Notificaciones | P2      | Crítica   |
| US-TDE-SEG-004     | Reportar incidentes a CSIRT        | P3      | Crítica   |
| US-TDE-DPO-001     | Gestionar Solicitudes ARCO         | P3      | Crítica   |
| US-TDE-INTEROP-001 | Habilitar Nodo PISEE               | P4      | Crítica   |
| US-TDE-REG-001     | Convocar Mesa Regional TDE         | P5      | Alta      |
| US-TDE-REG-002     | Disponibilizar Kit Digital Muni    | P5      | Alta      |
| US-TDE-VINC-001    | Gestionar Firmas Municipales       | P5      | Alta      |

> *Para el detalle completo de las 48 historias, ver catálogo YAML adjunto.*

---

## Entidades de Datos

### Cumplimiento Normativo

| Entidad      | Atributos Clave                           | Relaciones            |
| ------------ | ----------------------------------------- | --------------------- |
| `NormaTDE`   | id, codigo, nombre, fecha_vigencia        | → CumplimientoNorma[] |
| `Tramite`    | id, nombre, nivel_digitalizacion, cpat_id | → PlanDigitalizacion  |
| `Plataforma` | id, nombre, linea_base, responsable_ti    | → ActivoTI            |

### Gobernanza & Seguridad

| Entidad         | Atributos Clave                               | Relaciones              |
| --------------- | --------------------------------------------- | ----------------------- |
| `ActivoTI`      | id, nombre, clasificacion_cia, propietario    | → Riesgo[], Incidente[] |
| `Incidente`     | id, fecha, tipo, severidad, estado_csirt      | → ActivoTI[]            |
| `Riesgo`        | id, activo_id, amenaza, probabilidad, impacto | → ControlSeguridad      |
| `SolicitudARCO` | id, titular, tipo_derecho, fecha, estado      | → TratamientoDatos      |

### Interoperabilidad & Regional

| Entidad              | Atributos Clave                                          | Relaciones           |
| -------------------- | -------------------------------------------------------- | -------------------- |
| `ServicioPISEE`      | id, nombre, proveedor, endpoint, wsdl_swagger            | → AcuerdoIntercambio |
| `AcuerdoIntercambio` | id, servicio_id, institucion_origen, institucion_destino | → TransaccionPISEE[] |
| `EntidadRegional`    | id, nombre, tipo (Muni/Servicio), nivel_madurez_tde      | → MesaTDE            |

---

## Sistemas Involucrados

| Sistema            | Rol                                              | Dominio |
| ------------------ | ------------------------------------------------ | ------- |
| GORE OS            | Plataforma central de gestión                    | D-TDE   |
| Plataformas Estado | ClaveÚnica, DocDigital, FirmaGob, Notificaciones | Externo |
| PISEE              | Bus de interoperabilidad                         | Externo |
| CSIRT              | Plataforma de reporte de incidentes              | Externo |

---

## Normativa Aplicable

| Norma      | Descripción                       |
| ---------- | --------------------------------- |
| Ley 21.180 | Transformación Digital del Estado |
| Ley 21.663 | Ley Marco de Ciberseguridad       |
| Ley 21.719 | Protección de Datos Personales    |
| DS 83/2020 | Norma Técnica de Ciberseguridad   |

---

## Referencias Cruzadas

| Dominio | Relación                                               |
| ------- | ------------------------------------------------------ |
| D-NORM  | Expediente electrónico debe cumplir DS 10 del TDE      |
| FÉNIX   | Fallas críticas de ciberseguridad activan intervención |
| D-BACK  | Integración de sistemas administrativos con ClaveÚnica |
| D-SEG   | Infraestructura de red CIES gestionada bajo normas TDE |
| D-GOB   | Liderazgo político del Gobernador en Mesa Regional TDE |

---

Documento parte de GORE_OS v5.0
