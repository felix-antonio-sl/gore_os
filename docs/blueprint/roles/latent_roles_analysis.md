# Análisis de Roles Latentes

**Total Roles Latentes:** 142 de 398 (35.7%)

## Categorización por Unidad Organizacional

### Resumen por Tipo de Unidad
| Tipo                      | Roles Latentes |
| ------------------------- | -------------- |
| Ecosistema Externo        | 60             |
| Ejecutivo & Operaciones   | 38             |
| Mixto                     | 21             |
| Fuerza de Trabajo Digital | 13             |
| Gobernanza Estratégica    | 5              |
| Capacidades Transversales | 5              |

## Análisis Estratégico Composicional

### Priorización por Valor Potencial

> [!TIP]
> Los roles latentes representan **capacidad futura** del sistema. Activarlos mediante User Stories permite expandir la funcionalidad sin rediseñar el dominio.

#### Grupo 1: Alta Prioridad (Valor Inmediato)
| Categoría                          | Roles | Justificación                            |
| ---------------------------------- | ----- | ---------------------------------------- |
| **Bots/AI**                        | 9     | Habilitan automatización y madurez L4/L5 |
| **ITP/ITO**                        | 3     | Críticos para supervisión de ejecución   |
| **Jefaturas (DAE, DIPLADE, etc.)** | 6     | Roles de decisión sin cobertura          |

#### Grupo 2: Media Prioridad (Valor Estratégico)
| Categoría                    | Roles | Justificación               |
| ---------------------------- | ----- | --------------------------- |
| **SEREMIs**                  | 10    | Interoperabilidad sectorial |
| **Direcciones Regionales**   | 8     | Integración con servicios   |
| **Analistas especializados** | 12    | Profundización por sector   |

#### Grupo 3: Reserva (Valor Futuro)
| Categoría                             | Roles | Justificación                                   |
| ------------------------------------- | ----- | ----------------------------------------------- |
| **Ecosistema Externo (ONG, Gremios)** | 20+   | Participación ciudadana futura                  |
| **Concordancia (USR-NEW-*)**          | 21    | Creados para completitud, evaluar obsolescencia |

### Recomendaciones

1. **Sprint de Automatización**: Crear historias para los 9 Bots (GORE_OS AI), habilitando capacidades de monitoreo, clasificación y asesoría.

2. **Sprint de Supervisión**: Cubrir ITP, ITO y Jefaturas sin stories para cerrar el ciclo de ejecución de proyectos.

3. **Limpieza de Concordancia**: Evaluar los 21 roles "Mixto" creados para concordancia. Si no tienen valor funcional, marcar como `deprecated`.



---

## Detalle por Unidad

### Academia e Investigación (Ecosistema Externo)

| ID              | Título                     | Descripción                                           |
| --------------- | -------------------------- | ----------------------------------------------------- |
| `USR-EXT-CENIC` | Centro de Investigación    | Centro ANID o instituto de investigación regional.    |
| `USR-EXT-UNIV`  | Universidad (Investigador) | Académico o investigador de universidades regionales. |

### Agenda Ñuble 250 (Gabinete) (Gobernanza Estratégica)

| ID                | Título                     | Descripción                                                           |
| ----------------- | -------------------------- | --------------------------------------------------------------------- |
| `USR-GAB-250-ENC` | Encargado Agenda Ñuble 250 | Liderazgo de la cartera de proyectos patrimoniales y visión 200 años. |

### Ciudadanía (Ecosistema Externo)

| ID            | Título                     | Descripción                                                              |
| ------------- | -------------------------- | ------------------------------------------------------------------------ |
| `USR-CIU-EXT` | Usuario Externo (Genérico) | Cualquier persona natural o jurídica externa que interactúa con el GORE. |

### Comité Ciencia (CTCI) (Gobernanza Estratégica)

| ID             | Título        | Descripción                                                         |
| -------------- | ------------- | ------------------------------------------------------------------- |
| `USR-CTCI-ENC` | Encargado CTI | Gestión operativa de proyectos de Ciencia, Tecnología e Innovación. |

### Comité de Pertinencia Regional (Gobernanza Estratégica)

| ID                  | Título                                     | Descripción                                                                     |
| ------------------- | ------------------------------------------ | ------------------------------------------------------------------------------- |
| `USR-DIPL-CPER-SEC` | Secretario Ejecutivo Comité de Pertinencia | Gestión técnica de actas y certificación RS (Actúa Jefatura Presupuesto DIPIR). |

### Control Externo (Ecosistema Externo)

| ID                | Título                       | Descripción                                                                  |
| ----------------- | ---------------------------- | ---------------------------------------------------------------------------- |
| `USR-EXT-AUD-MIN` | Auditor Ministerial          | Auditoría del Ministerio del Interior y Seguridad Pública.                   |
| `USR-EXT-CAIGG`   | Auditor General de Gobierno  | Consejo de Auditoría Interna General de Gobierno (CAIGG).                    |
| `USR-EXT-CPLT`    | Consejo Transparencia (CPLT) | Órgano garante del acceso a la información y fiscalización de transparencia. |

### Cumplimiento Normativo (D-NORM) (Capacidades Transversales)

| ID                    | Título                             | Descripción                                                                      |
| --------------------- | ---------------------------------- | -------------------------------------------------------------------------------- |
| `USR-NORM-TRANSP-REF` | Referente Transparencia (por Ítem) | Funcionario designado para generar información de ítems 1-16 del Artículo 7° ... |

### D-DEV (Fuerza de Trabajo Digital)

| ID              | Título                 | Descripción                                                        |
| --------------- | ---------------------- | ------------------------------------------------------------------ |
| `USR-DEV-FRONT` | Desarrollador Frontend | Implementación de la experiencia de usuario y la interfaz gráfica. |

### D-NORM Complemento (Ecosistema Externo)

| ID              | Título            | Descripción                                                          |
| --------------- | ----------------- | -------------------------------------------------------------------- |
| `USR-NORM-ARCH` | Archivero Digital | Gestión del archivo digital institucional y preservación documental. |

### D-SEG (Ejecutivo & Operaciones)

| ID             | Título                   | Descripción                                               |
| -------------- | ------------------------ | --------------------------------------------------------- |
| `USR-SEG-ASES` | Asesor Técnico Seguridad | Asesoría experta en criminología o seguridad situacional. |

### D-TDE (Capacidades Transversales)

| ID                  | Título                             | Descripción                                                                      |
| ------------------- | ---------------------------------- | -------------------------------------------------------------------------------- |
| `USR-TDE-ADMIN-SYS` | Administrador de Sistema           | Administración funcional de aplicaciones y configuración de parámetros.          |
| `USR-TDE-CTD`       | Coordinador Transformación Digital | Líder de la implementación de Ley de Transformación Digital (Res. Ex. 2034).     |
| `USR-TDE-RESP-SIS`  | Responsable de Sistema IA          | Funcionario designado para la trazabilidad y rendición de cuentas de un Asist... |

### DAF (Ejecutivo & Operaciones)

| ID                     | Título                      | Descripción                                                                      |
| ---------------------- | --------------------------- | -------------------------------------------------------------------------------- |
| `USR-DAF-FIN-COGIR`    | Cogirador Autorizado        | Funcionario con atribución delegada para firma conjunta de cheques y transfer... |
| `USR-DAF-HON-ANAL`     | Analista GDP (Honorarios)   | analista_gdp_honorarios                                                          |
| `USR-DAF-HON-JEFE`     | Jefatura Control Jerárquico | Responsable de ejercer control, supervisar y certificar el Informe de Cumplim... |
| `USR-DAF-UCR-COOR`     | Coordinador UCR             | Jefatura operativa de la unidad de rendiciones.                                  |
| `USR-NEW-ANALISTA-COM` | Analista Compras            | analista_compras                                                                 |
| `USR-NEW-ANALISTA-VIA` | Analista Viáticos           | analista_viaticos                                                                |
| `USR-OP-ENC`           | Encargado Oficina de Partes | Supervisión del flujo documental y gestión de archivos. Dependencia DAF (Res.... |

### DIDESOH (Ejecutivo & Operaciones)

| ID                     | Título                         | Descripción                                                |
| ---------------------- | ------------------------------ | ---------------------------------------------------------- |
| `USR-DIDES-PROG-COOR`  | Coordinador Programas Sociales | Coordinación de la ejecución de programas de ayuda social. |
| `USR-DIDES-TERR`       | Analista Equidad Territorial   | analista_equidad_territorial                               |
| `USR-DIDES-TERR-SOC`   | Sociólogo Territorial          | Diagnóstico social y análisis de brechas comunales.        |
| `USR-NEW-ANALISTA-CUL` | Analista Cultura               | analista_cultura                                           |
| `USR-NEW-ANALISTA-DEP` | Analista Deporte               | analista_deporte                                           |
| `USR-NEW-ANALISTA-SAL` | Analista Salud                 | analista_salud                                             |

### DIFOI (Ejecutivo & Operaciones)

| ID                     | Título                    | Descripción                                                               |
| ---------------------- | ------------------------- | ------------------------------------------------------------------------- |
| `USR-DIFOI-CTI-PROF`   | Profesional CTI           | profesional_cti                                                           |
| `USR-DIFOI-REZ-ENC`    | Encargado Zonas de Rezago | Coordinación de programas de focalización territorial en zonas rezagadas. |
| `USR-DIFOI-URAI-EJEC`  | Ejecutivo URAI            | Gestión de atracción de inversiones y comercio exterior (URAI).           |
| `USR-NEW-ANALISTA-ENE` | Analista Energía          | analista_energia                                                          |
| `USR-NEW-ANALISTA-MED` | Analista Medio Ambiente   | analista_medio_ambiente                                                   |
| `USR-NEW-ANALISTA-TUR` | Analista Turismo          | analista_turismo                                                          |

### DIPIR (Ejecutivo & Operaciones)

| ID              | Título                              | Descripción                                                                      |
| --------------- | ----------------------------------- | -------------------------------------------------------------------------------- |
| `USR-DIPIR-COM` | Encargado Comunicaciones DIPIR      | Gestiona la difusión de instrumentos y programas de inversión regional.          |
| `USR-DIPIR-ITP` | Inspector Técnico de Programa (ITP) | Supervisión técnica de ejecución, avance y revisión de rendiciones de program... |

### DIPLADE (Ejecutivo & Operaciones)

| ID                     | Título                                                           | Descripción                                                                      |
| ---------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `USR-DIPL-CDR`         | Comité Directivo Regional (CDR)                                  | Instancia colegiada de priorización estratégica y decisiones de inversión.       |
| `USR-DIPL-DAE-JEFE`    | Jefe Depto. Análisis y Evaluación (DAE)                          | Evaluación técnica de proyectos y programas (Movido a DIPLADE en 2024).          |
| `USR-DIPL-GEN`         | Analista DIPLADE                                                 | analista_diplade                                                                 |
| `USR-DIPL-GRD`         | Comité Regional GRD                                              | Coordinación de Gestión del Riesgo de Desastres y emergencias.                   |
| `USR-DIPL-MUNI-ENC`    | Encargado Unidad de Municipalidades y Conservaciones             | Gestión técnica y asistencia a municipios para proyectos (Bajo DAE/DIPLADE).     |
| `USR-DIPL-PLAN-JEFE`   | Jefe Depto. Planificación Estratégica y Ordenamiento Territorial | Liderar PROT, ERD y planificación estratégica regional.                          |
| `USR-DIPL-PROPIR`      | Coordinador Mapa PROPIR                                          | Responsable de la difusión y actualización del Mapa de Georreferenciación de ... |
| `USR-DIPL-PROY-ENC`    | Encargado Unidad de Proyectos y Programas                        | Evaluación técnica de proyectos y programas regionales (Bajo DAE/DIPLADE).       |
| `USR-NEW-ANALISTA-CAR` | Analista Cartera                                                 | analista_cartera                                                                 |
| `USR-NEW-ANALISTA-MUN` | Analista Municipios                                              | analista_municipios                                                              |

### DIT (Ejecutivo & Operaciones)

| ID                     | Título                             | Descripción                                                     |
| ---------------------- | ---------------------------------- | --------------------------------------------------------------- |
| `USR-DIT-ANAL`         | Analista DIT                       | analista_dit                                                    |
| `USR-DIT-CON-ING`      | Ingeniero Vialidad                 | Gestión de proyectos de caminos básicos y obras viales menores. |
| `USR-DIT-INFRA-ITO`    | Inspector Técnico de Obra (ITO)    | Supervisión técnica y administrativa de obras en ejecución.     |
| `USR-DIT-ITO`          | Inspector Técnico de Obras (Campo) | Fiscalización física directa de avances y calidad de obra.      |
| `USR-NEW-ANALISTA-AGU` | Analista Agua Potable Rural        | analista_agua_potable                                           |
| `USR-NEW-ANALISTA-VIV` | Analista Vivienda                  | analista_vivienda                                               |

### Direcciones Regionales de Servicios (Ecosistema Externo)

| ID                  | Título                     | Descripción             |
| ------------------- | -------------------------- | ----------------------- |
| `USR-EXT-CNR`       | Director Regional CNR      | director_cnr            |
| `USR-EXT-DGA`       | Director Regional DGA      | director_dga            |
| `USR-EXT-DOH`       | Director Regional DOH      | director_doh            |
| `USR-EXT-JUNJI`     | Director Regional JUNJI    | director_junji          |
| `USR-EXT-SALUD-SRV` | Director Servicio de Salud | director_servicio_salud |
| `USR-EXT-SENCE`     | Director Regional SENCE    | director_sence          |
| `USR-EXT-SERNAM`    | Director Regional SernamEG | director_sernameg       |
| `USR-EXT-SII`       | Director Regional SII      | director_sii            |

### Ejecutores Sectoriales (Fomento) (Ecosistema Externo)

| ID              | Título   | Descripción                                                              |
| --------------- | -------- | ------------------------------------------------------------------------ |
| `USR-EXT-CORFO` | CORFO    | Corporación de Fomento de la Producción, innovación y desarrollo.        |
| `USR-EXT-FOSIS` | FOSIS    | Fondo de Solidaridad e Inversión Social, ejecutor de programas sociales. |
| `USR-EXT-INDAP` | INDAP    | Instituto de Desarrollo Agropecuario, fomento agrícola.                  |
| `USR-EXT-SERCO` | SERCOTEC | Servicio de Cooperación Técnica, fomento a emprendimiento.               |

### Ejecutores y Beneficiarios (Ecosistema Externo)

| ID                 | Título                       | Descripción                                                        |
| ------------------ | ---------------------------- | ------------------------------------------------------------------ |
| `USR-EJEC-ANAL`    | Analista Ejecutor            | analista_ejecutor                                                  |
| `USR-EXT-EMP`      | Empresa / Gremio             | Empresa o asociación gremial beneficiaria de programas de fomento. |
| `USR-EXT-ORG-BEN`  | Organización Beneficiaria    | Organización adjudicataria de fondos responsable de su ejecución.  |
| `USR-EXT-ORG-POST` | Organización Postulante (8%) | Junta de vecinos, club deportivo u ONG que postula a fondos.       |

### Equipo de Emergencias (ECIF) (Ecosistema Externo)

| ID              | Título           | Descripción                                                            |
| --------------- | ---------------- | ---------------------------------------------------------------------- |
| `USR-ECIF-COOR` | Coordinador ECIF | Lidera el Equipo de Coordinación Específico para Incendios Forestales. |

### FENIX (Unidad de Intervención Institucional) (Ecosistema Externo)

| ID               | Título            | Descripción                                                 |
| ---------------- | ----------------- | ----------------------------------------------------------- |
| `USR-CAL-FNX-OP` | Interventor FENIX | Ejecución de planes de estabilización en unidades críticas. |

### GORE_OS AI (Fuerza de Trabajo Digital)

| ID              | Título                               | Descripción                                                                      |
| --------------- | ------------------------------------ | -------------------------------------------------------------------------------- |
| `BOT-AUDIT`     | Fiscalizador Bot                     | Agente de auditoría contínua y detección de anomalías (Madurez 5).               |
| `BOT-CERT`      | Robot Cert-Manager                   | Bot encargado de la gestión y renovación automática de certificados digitales.   |
| `BOT-CLASIF`    | Agente Clasificador                  | IA especializada en clasificación automática de documentos y expedientes.        |
| `BOT-COMUNICON` | Comunicon (Asesor Comunicacional)    | Agente IA para redacción de comunicados, vocerosías y contenido digital.         |
| `BOT-DIGITRANS` | Digitrans (Asesor TDE)               | Agente IA asesor de cumplimiento normativo TDE (Madurez 4).                      |
| `BOT-GOREOLOGO` | Goreólogo (Experto Institucional)    | Agente IA con conocimiento profundo de la normativa, historia y cultura GORE.    |
| `BOT-IPR`       | Formuevaluador (Asesor IPR)          | Agente IA para análisis preliminar y formulación de iniciativas de inversión.    |
| `BOT-JANO`      | Jano (Asesor Jurídico y Conformidad) | IA de apoyo para redacción, revisión legal y verificación de conformidad norm... |
| `BOT-MORA`      | Mora Watcher (Monitor Plazos)        | Agente de monitoreo de plazos administrativos y alertas tempranas (Madurez 1).   |

### Gabinete (Ecosistema Externo)

| ID            | Título          | Descripción                                                            |
| ------------- | --------------- | ---------------------------------------------------------------------- |
| `USR-GAB-INT` | Encargado RR.II | Gestión de paradiplomacia, cooperación internacional y hermanamientos. |

### Gobierno Interior (Ecosistema Externo)

| ID            | Título                           | Descripción                                   |
| ------------- | -------------------------------- | --------------------------------------------- |
| `USR-EXT-DPP` | Delegado Presidencial Provincial | Representante del Presidente en la provincia. |

### Inteligencia Territorial (D-TERR) (Ecosistema Externo)

| ID              | Título      | Descripción                                         |
| --------------- | ----------- | --------------------------------------------------- |
| `USR-TERR-JEFE` | Jefe D-TERR | Liderazgo de la unidad de inteligencia territorial. |

### Oficina Digital e IA (ODIA) (Fuerza de Trabajo Digital)

| ID              | Título                 | Descripción                                                                      |
| --------------- | ---------------------- | -------------------------------------------------------------------------------- |
| `USR-ODIA-CAMP` | Miembro Equipo Campeón | Funcionario (4-6) que asume operación autónoma de plataformas IA y transferen... |
| `USR-ODIA-JEFE` | Jefe ODIA              | Lidera la unidad permanente de transformación digital e IA (Hito Mes 36 PTD).    |

### Organismos Sectoriales (Transferencia de Competencias) (Ecosistema Externo)

| ID               | Título       | Descripción                                                                      |
| ---------------- | ------------ | -------------------------------------------------------------------------------- |
| `USR-EXT-SUBTEL` | SUBTEL / MTT | Subsecretaría de Telecomunicaciones y Ministerio de Transportes, contraparte ... |

### Organismos de Emergencia (Ecosistema Externo)

| ID             | Título                                    | Descripción                                      |
| -------------- | ----------------------------------------- | ------------------------------------------------ |
| `USR-EXT-ANCI` | ANCI (Agencia Nacional de Ciberseguridad) | Agencia coordinadora de ciberseguridad nacional. |

### Participación Ciudadana (Ecosistema Externo)

| ID              | Título                               | Descripción                                                    |
| --------------- | ------------------------------------ | -------------------------------------------------------------- |
| `USR-EXT-COSOC` | COSOC / Consejo de la Sociedad Civil | Órgano participativo de representación ciudadana ante el GORE. |
| `USR-EXT-JJVV`  | Junta de Vecinos                     | Organización territorial de base comunitaria.                  |

### Poder Judicial (Ecosistema Externo)

| ID                    | Título                          | Descripción                                                       |
| --------------------- | ------------------------------- | ----------------------------------------------------------------- |
| `USR-EXT-CORTE-NUBLE` | Corte de Apelaciones de Chillán | Tribunal de alzada regional. Recursos de protección, apelaciones. |
| `USR-EXT-JUZG-LETRAS` | Juzgado de Letras               | Tribunales ordinarios civiles. Litigios civiles del GORE.         |

### Poder Legislativo (Representación Regional) (Ecosistema Externo)

| ID                  | Título               | Descripción                                                               |
| ------------------- | -------------------- | ------------------------------------------------------------------------- |
| `USR-EXT-DIP-NUBLE` | Diputado/a por Ñuble | Representante del distrito en la Cámara. Fiscalización y leyes.           |
| `USR-EXT-SEN-NUBLE` | Senador/a por Ñuble  | Representante de la región en el Senado. Legislación de interés regional. |

### Reguladores Nacionales (Ecosistema Externo)

| ID                | Título                                | Descripción                 |
| ----------------- | ------------------------------------- | --------------------------- |
| `USR-EXT-DIPRES`  | Analista Sectorial DIPRES             | analista_sectorial_dipres   |
| `USR-EXT-SUBDERE` | Analista División Gobiernos (SUBDERE) | analista_division_gobiernos |

### Roles Adicionales (Concordancia) (Mixto)

| ID                     | Título                       | Descripción                                                         |
| ---------------------- | ---------------------------- | ------------------------------------------------------------------- |
| `USR-NEW-ABOGADO-DNOR` | Abogado D-NORM               | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-ABOGADO-GENE` | Abogado General              | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-BENEFICIARIO` | Beneficiario Individual      | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-CONSULTOR-EX` | Consultor Externo            | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-CONTRAPARTE-` | Contraparte Interna          | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-CORPORACION-` | Corporación Municipal        | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-ENCARGADO-ES` | Encargado Estado Verde       | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-JEFE-DEPTO-A` | Jefe Depto. Abastecimiento   | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-JEFE-DEPTO-P` | Jefe Depto. Personal         | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-JEFE-ESTUDIO` | Jefe Estudios                | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-JEFE-PLAN`    | Jefe Depto. Planificación    | Jefatura del departamento de planificación estratégica e inversión. |
| `USR-NEW-MEDIA-COMUNI` | Medio de Comunicación        | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-MEDIO-COMUNI` | Medio de Comunicación        | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-NOTARIO`      | Notario                      | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-PRENSA-REGIO` | Prensa Regional              | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-QA-ANALISTA`  | Analista QA                  | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-SECPLA-CHILL` | SECPLA Chillán               | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-SECPLA-SAN-C` | SECPLA San Carlos            | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-UNIDAD-COORD` | Unidad Coordinación Regional | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-UNIVERSIDAD-` | Universidad Regional         | Rol agregado para concordancia con historias de usuario.            |
| `USR-NEW-UTM-GENERICA` | UTM Genérica                 | Rol agregado para concordancia con historias de usuario.            |

### Secretarías Regionales Ministeriales (SEREMI) (Ecosistema Externo)

| ID                     | Título                   | Descripción          |
| ---------------------- | ------------------------ | -------------------- |
| `USR-EXT-SEREMI-CULT`  | SEREMI Culturas          | seremi_culturas      |
| `USR-EXT-SEREMI-ECO`   | SEREMI Economía          | seremi_economia      |
| `USR-EXT-SEREMI-EDU`   | SEREMI Educación         | seremi_educacion     |
| `USR-EXT-SEREMI-HAC`   | SEREMI Hacienda          | seremi_hacienda      |
| `USR-EXT-SEREMI-MDSF`  | SEREMI Desarrollo Social | seremi_mdsf          |
| `USR-EXT-SEREMI-MEDIO` | SEREMI Medio Ambiente    | seremi_medioambiente |
| `USR-EXT-SEREMI-MUJER` | SEREMI Mujer y EG        | seremi_mujer         |
| `USR-EXT-SEREMI-SALUD` | SEREMI Salud             | seremi_salud         |
| `USR-EXT-SEREMI-TRAB`  | SEREMI Trabajo           | seremi_trabajo       |
| `USR-EXT-SEREMI-VIV`   | SEREMI MINVU             | seremi_minvu         |

### Sociedad Civil y Gremios (Ecosistema Externo)

| ID               | Título                   | Descripción                                                                  |
| ---------------- | ------------------------ | ---------------------------------------------------------------------------- |
| `USR-EXT-CCASOC` | Colegio Profesional      | Asociaciones gremiales de profesionales (Arquitectos, Ingenieros, Abogados). |
| `USR-EXT-CPC`    | CPC Regional             | Confederación de la Producción y del Comercio. Inversión privada.            |
| `USR-EXT-FEMP`   | Federación de Municipios | Asociación de municipios regionales. Coordinación intercomunal.              |
| `USR-EXT-ONG`    | ONG / Fundación          | Organización No Gubernamental o Fundación ejecutora de proyectos sociales.   |
| `USR-EXT-SINDIC` | Central Sindical         | CUT u otra central de trabajadores. Interlocución laboral.                   |
| `USR-EXT-SNA`    | SNA / SOFO               | Sociedad Nacional de Agricultura / Sociedad de Fomento Agrícola Ñuble.       |

### Subcomité de Inteligencia Artificial (Fuerza de Trabajo Digital)

| ID              | Título                  | Descripción                                                         |
| --------------- | ----------------------- | ------------------------------------------------------------------- |
| `USR-SCIA-PRES` | Presidente Subcomité IA | Lidera la supervisión ética y responsable del uso de IA en el GORE. |

### Unidad Jurídica (Gobernanza Estratégica)

| ID                 | Título                     | Descripción                                                                      |
| ------------------ | -------------------------- | -------------------------------------------------------------------------------- |
| `USR-JUR-ASES-DIV` | Abogado Asesor de División | Abogado asignado para visar y asesorar preferentemente a una División específ... |
| `USR-JUR-JEFE`     | Jefe Unidad Jurídica       | Visación legal y control de legitimidad de actos administrativos.                |

### Unidad de Calidad y Gestión Institucional (Ecosistema Externo)

| ID                  | Título                               | Descripción                                                                      |
| ------------------- | ------------------------------------ | -------------------------------------------------------------------------------- |
| `USR-CAL-CSEU-MEMB` | Miembro Comité CSEU                  | Funcionario designado para entregar lineamientos y asesoría en calidad de ser... |
| `USR-CAL-PMG-TD`    | Referente Transformación Digital PMG | Referente técnico del Sistema de Transformación Digital PMG.                     |

### Unidad de Control (Capacidades Transversales)

| ID              | Título                 | Descripción                                              |
| --------------- | ---------------------- | -------------------------------------------------------- |
| `USR-CTRL-JEFE` | Jefe Unidad de Control | Liderazgo de la fiscalización operativa y reporte a CGR. |

### Órganos Autónomos Constitucionales (Ecosistema Externo)

| ID            | Título                        | Descripción                                                           |
| ------------- | ----------------------------- | --------------------------------------------------------------------- |
| `USR-EXT-BC`  | Banco Central de Chile        | Órgano autónomo de política monetaria. Información macroeconómica.    |
| `USR-EXT-CDE` | Consejo de Defensa del Estado | Defensa judicial del patrimonio del Estado. Litigios institucionales. |
| `USR-EXT-MP`  | Ministerio Público (Fiscalía) | Fiscalía Regional. Investigación de delitos, denuncias.               |
| `USR-EXT-TC`  | Tribunal Constitucional       | Control de constitucionalidad de leyes y actos.                       |
