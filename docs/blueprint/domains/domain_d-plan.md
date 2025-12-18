# D-PLAN: Dominio de Planificación Estratégica


> Parte de: [GORE_OS Vision General](../vision_general.md)  
> Capa: Habilitante (Dimensión Estratégica)  
> Función GORE: PLANIFICAR  
> División: DIPLADE (Planificación y Desarrollo Regional)

---

## Glosario D-PLAN

| Término                                   | Sigla   | Definición                                                                                                                                           |
| ----------------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Estrategia Regional de Desarrollo         | ERD     | Instrumento de planificación de largo plazo (10 años) que define visión, ejes y objetivos estratégicos para el desarrollo regional. Art. 16 LOC GORE |
| Plan Regional de Ordenamiento Territorial | PROT    | Instrumento vinculante que orienta el uso del territorio regional mediante macrozonificación y condicionantes. Art. 17 LOC GORE                      |
| Anteproyecto Regional de Inversiones      | ARI     | Planificación presupuestaria anual que consolida iniciativas para presentación CORE (ciclo mayo-agosto)                                              |
| Programa Regional de Inversiones          | PROPIR  | Consolidación de ARI aprobada por CORE, base para ejecución presupuestaria del año siguiente                                                         |
| Convenio de Programación                  | CDP     | Acuerdo plurianual entre GORE y ministerios sectoriales para financiamiento conjunto de inversiones                                                  |
| Eje Estratégico                           | EE      | Gran área de desarrollo regional definida en ERD (4-6 por estrategia)                                                                                |
| Lineamiento                               | LIN     | Orientación programática dentro de un eje estratégico (2-4 por eje)                                                                                  |
| Objetivo Estratégico                      | OE      | Meta medible vinculada a lineamiento con indicadores y metas anuales                                                                                 |
| Macrozona                                 | MZ      | División territorial mayor del PROT para regulación diferenciada (3-5 por región)                                                                    |
| PLADECO                                   | PLADECO | Plan de Desarrollo Comunal. Instrumento rector del desarrollo vecinal.                                                                               |
| SECPLA                                    | SECPLA  | Secretaría Comunal de Planificación. Unidad municipal técnica.                                                                                       |
| División de Planificación y Desarrollo    | DIPLADE | División del GORE responsable de diseñar y monitorear instrumentos de planificación                                                                  |

---

## Propósito

Gestionar los instrumentos de planificación regional —ERD, PROT, ARI/PROPIR y Convenios de Programación— garantizando coherencia estratégica entre visión de largo plazo, ordenamiento territorial, priorización de inversiones y ejecución presupuestaria.

Fundamento Legal: LOC GORE Art. 16-21 (funciones de planificación), Art. 17 (PROT obligatorio), Art. 75-81 (fondos regionales).

---

## Diagrama de Dominio

```mermaid
flowchart TB
    subgraph ESTRATEGICO["📊 Planificación Estratégica"]
        ERD["ERD 2024-2030<br/>Visión 10 años"]
        N250["Ñuble 250<br/>Agenda 2028"]
    end

    subgraph TERRITORIAL["🗺️ Ordenamiento"]
        PROT["PROT<br/>Vinculante"]
        PRC["Planes Reguladores<br/>Comunales"]
    end

    subgraph INVERSION["💰 Inversión Regional"]
        ARI["ARI<br/>Anual"]
        PROPIR["PROPIR<br/>Aprobado CORE"]
        CDP["Convenios<br/>Programación"]
    end

    subgraph OBSERVATORIO["📈 Observatorio"]
        IND["Indicadores<br/>Territoriales"]
        DASH["Dashboards<br/>Avance"]
    end

    ERD --> PROT
    ERD --> ARI
    N250 --> ARI
    PROT --> PRC
    ARI --> PROPIR
    PROPIR --> CDP
    IND --> DASH
    DASH --> ERD
```

---

## Módulos

### M1: ERD Digital

| Atributo   | Descripción                                                                               |
| ---------- | ----------------------------------------------------------------------------------------- |
| Propósito  | Gestionar la jerarquía completa de la ERD y vincular iniciativas a objetivos estratégicos |
| Estructura | ERD → Eje(5) → Lineamiento(15) → OE(96) → Indicador/Meta → Iniciativa                     |

Funcionalidades:

- Editor colaborativo de ERD (Objetivos, Lineamientos, Indicadores)
- Vinculación con ODS y Programas de Gobierno
- Repositorio documental de versiones ERDctos de seguridad)
- Dashboard de avance por eje estratégico con semáforos
- Alertas de objetivos sin iniciativas vinculadas (>180 días)

- Reportes de coherencia ERD ↔ Presupuesto ejecutado

### M2: PROT Digital

| Atributo   | Descripción                                                              |
| ---------- | ------------------------------------------------------------------------ |
| Propósito  | Gestionar zonificación territorial y validar compatibilidad de proyectos |
| Estructura | PROT → Macrozona(3-5) → Zona(n) → Uso(permitido/condicionado/prohibido)  |

Funcionalidades:
- Visor geoespacial de zonificación PROT integrado con D-TERR

- Validador automático de compatibilidad IPR ↔ Zona territorial

- Alertas de proyectos en zonas de uso incompatible

- Consulta pública de aptitud territorial para ciudadanos

### M3: ARI / PROPIR

| Atributo  | Descripción                                                               |
| --------- | ------------------------------------------------------------------------- |
| Propósito | Gestionar el ciclo anual de inversión regional                            |
| Ciclo     | Mayo-Agosto: solicitud → priorización → consolidación → presentación CORE |

Funcionalidades:
- Formulario digital de solicitud de iniciativas (divisiones)

- Scoring multicriterio de priorización (alineamiento ERD, impacto, factibilidad)

- Consolidación automática por fuente/fondo (FNDR, FRPD, ISAR)

- Simulación de escenarios presupuestarios

- Exportación formato DIPRES para integración nacional

### M4: Convenios de Programación

| Atributo  | Descripción                                                 |
| --------- | ----------------------------------------------------------- |
| Propósito | Gestionar acuerdos plurianuales con ministerios sectoriales |
| Tipos     | MOP, MINVU, MINSAL, CORFO, otros                            |

Funcionalidades:
- Registro de convenios con hitos y cronograma

- Seguimiento financiero (comprometido/pagado)

- Alertas de vencimiento y renovación

- Vinculación con IPR correspondientes

### M5: Observatorio Territorial

| Atributo  | Descripción                                                             |
| --------- | ----------------------------------------------------------------------- |
| Propósito | Proveer inteligencia territorial para planificación basada en evidencia |
| Fuentes   | BCN Indicadores Ñuble (800+), Ñuble250 Observatorio, CASEN, INE         |

Funcionalidades:

- Visualizador de capas territoriales (PROT, ZOIT, Pladecos)

- Análisis de solapamiento de inversiones

- Generación de reportes territoriales y proyecciones

- Vinculación indicadores ↔ objetivos ERD

- Alertas de brechas por eje estratégico

### M6: Planificación Participativa

| Atributo   | Descripción                                               |
| ---------- | --------------------------------------------------------- |
| Propósito  | Capturar y procesar insumos ciudadanos para planificación |
| Referencia | Ñuble250: 64 instancias, 2.297 participantes, 9 trazos    |

Funcionalidades:
- Registro de cabildos y consultas territoriales

- Síntesis asistida por IA de aportes ciudadanos

- Trazabilidad de propuestas ciudadanas → iniciativas

- Reportes de participación acumulada

### M7: Apoyo a Planificación Comunal

| Atributo     | Descripción                                                           |
| ------------ | --------------------------------------------------------------------- |
| Propósito    | Transferir capacidades técnicas a municipios para mejorar cartera IPR |
| Beneficiario | SECPLAN de 21 comunas de Ñuble                                        |

Funcionalidades:
- Mesa de ayuda para formulación de iniciativas (MIDESO)

- Repositorio de proyectos tipo y buenas prácticas

- Asistente de alineamiento PLADECO ↔ ERD

- Reporte de cartera comunal en proceso

---

## Procesos BPMN

### Mapa General de Procesos

```mermaid
flowchart LR
    subgraph DPLAN["D-PLAN: Planificación Estratégica"]
        P1["P1: Actualización ERD<br/>5 fases"]
        P2["P2: Ciclo ARI/PROPIR<br/>4 fases"]
        P3["P3: Validación PROT<br/>3 fases"]
        P4["P4: Gestión CDP<br/>5 fases"]
        P5["P5: Evaluación Indicadores<br/>3 fases"]
    end

    P1 --> P2
    P3 --> P2
    P5 --> P1
    P2 --> P4
    P6["P6: Asistencia<br/>Técnica Municipal"] -.-> P2
```

---

### P1: Actualización ERD

```mermaid
flowchart TB
    subgraph P1["P1: Actualización ERD"]
        P1_1["1.1 Evaluación<br/>Estado Actual"]
        P1_2["1.2 Diagnóstico<br/>Participativo"]
        P1_3["1.3 Formulación<br/>Técnica"]
        P1_4["1.4 Aprobación<br/>CORE"]
        P1_5["1.5 Publicación<br/>Vigencia"]
    end

    P1_1 --> P1_2 --> P1_3 --> P1_4 --> P1_5

    P1_1 -.- N1["Indicadores de avance<br/>Brechas identificadas"]
    P1_2 -.- N2["Cabildos territoriales<br/>Consultas sectoriales"]
    P1_3 -.- N3["Ejes, lineamientos, OE<br/>Indicadores y metas"]
    P1_4 -.- N4["Votación CORE<br/>Resolución aprobatoria"]
    P1_5 -.- N5["Diario Oficial<br/>Plataforma GORE"]
```

Actores: DIPLADE, Consejeros CORE, Ciudadanía, Servicios Públicos  
Frecuencia: Cada 10 años (actualización periódica según Art. 16 LOC)

---

### P2: Ciclo ARI/PROPIR

```mermaid
flowchart TB
    subgraph P2["P2: Ciclo ARI/PROPIR"]
        P2_1["2.1 Solicitud<br/>Iniciativas"]
        P2_2["2.2 Priorización<br/>Técnica"]
        P2_3["2.3 Consolidación<br/>DIPIR"]
        P2_4["2.4 Presentación<br/>CORE"]
    end

    P2_1 --> P2_2 --> P2_3 --> P2_4

    P2_1 -.- N1["Divisiones completan<br/>fichas de solicitud"]
    P2_2 -.- N2["Scoring multicriterio<br/>Alineamiento ERD"]
    P2_3 -.- N3["Agregación por<br/>fuente/fondo"]
    P2_4 -.- N4["Sesión CORE<br/>Septiembre"]
```

Actores: Jefes de División, DIPLADE, DIPIR, CORE  
Frecuencia: Anual (mayo-agosto-septiembre)

---

### P3: Validación PROT

```mermaid
flowchart TB
    subgraph P3["P3: Validación PROT"]
        P3_1["3.1 Solicitud<br/>Validación"]
        P3_2["3.2 Análisis<br/>Territorial"]
        P3_3["3.3 Emisión<br/>Dictamen"]
    end

    P3_1 --> P3_2 --> P3_3

    P3_1 -.- N1["Proponente remite<br/>ubicación y tipo proyecto"]
    P3_2 -.- N2["DIPLADE + D-TERR<br/>verifican zonificación"]
    P3_3 -.- N3["Compatible /<br/>Incompatible / Condicionado"]
```

Actores: Proponente (división/municipio), DIPLADE, D-TERR  
Frecuencia: Por demanda

---

### P4: Gestión CDP

```mermaid
flowchart TB
    subgraph P4["P4: Gestión Convenios de Programación"]
        P4_1["4.1 Negociación<br/>Técnica"]
        P4_2["4.2 Firma<br/>Convenio"]
        P4_3["4.3 Ejecución<br/>Hitos"]
        P4_4["4.4 Seguimiento<br/>Financiero"]
        P4_5["4.5 Cierre<br/>Rendición"]
    end

    P4_1 --> P4_2 --> P4_3 --> P4_4 --> P4_5

    P4_1 -.- N1["Definición montos<br/>y proyectos"]
    P4_2 -.- N2["Gobernador + Ministro<br/>Toma de Razón"]
    P4_3 -.- N3["Transferencias<br/>según cronograma"]
    P4_4 -.- N4["Reportes<br/>trimestrales"]
    P4_5 -.- N5["Rendición final<br/>y evaluación"]
```

Actores: GORE, Ministerio Sectorial, DIPIR, CGR  
Frecuencia: Plurianual (3-5 años por convenio)

---

### P5: Evaluación Indicadores

```mermaid
flowchart TB
    subgraph P5["P5: Evaluación Indicadores Territoriales"]
        P5_1["5.1 Recolección<br/>Datos"]
        P5_2["5.2 Análisis<br/>Brechas"]
        P5_3["5.3 Publicación<br/>Tablero"]
    end

    P5_1 --> P5_2 --> P5_3

    P5_1 -.- N1["Fuentes: INE, CASEN<br/>BCN, servicios"]
    P5_2 -.- N2["Comparación con<br/>metas ERD"]
    P5_3 -.- N3["Dashboard público<br/>Observatorio Regional"]
```

Actores: Observatorio DIPLADE, Áreas técnicas  
Frecuencia: Mensual/Trimestral

---

### P6: Asistencia Técnica Municipal

```mermaid
flowchart TD
    subgraph SOLICITUD["🆘 Solicitud Asistencia"]
        A["Municipio detecta<br/>necesidad"]
        B["Solicitud Soporte<br/>(D-PLAN)"]
    end

    subgraph ASESORIA["🛠️ Intervención"]
        C["Asignación Analista<br/>DIPLADE"]
        D{"Tipo Asesoría"}
        D -->|Formulación| E["Revisión Metodológica<br/>(MIDESO/FNDR)"]
        D -->|Estratégica| F["Alineamiento<br/>PLADECO-ERD"]
    end

    subgraph RESULTADO["✅ Resultado"]
        E --> G["Iniciativa RS<br/>(Elegible)"]
        F --> H["PLADECO Actualizado"]
    end

    A --> B --> C --> D
```

---

## Catálogo por Proceso

### US Módulo ERD Digital

| ID              | User Story                                                                                                   | Prioridad |
| --------------- | ------------------------------------------------------------------------------------------------------------ | --------- |
| US-PLAN-ERD-001 | Como Analista DIPLADE quiero navegar el árbol ERD con filtros para ubicar rápidamente objetivos estratégicos | Alta      |
| US-PLAN-ERD-002 | Como Analista DIPIR quiero vincular una IPR a un objetivo ERD para garantizar alineamiento estratégico       | Alta      |
| US-PLAN-ERD-003 | Como Jefe DIPLADE quiero visualizar un dashboard de avance por eje para monitorear cumplimiento              | Alta      |
| US-PLAN-ERD-004 | Como Sistema quiero alertar objetivos sin iniciativas >180 días para activar intervención FÉNIX              | Media     |
| US-PLAN-ERD-005 | Como Jefe DIPLADE quiero generar reportes coherencia ERD-Presupuesto para evaluar ejecución                  | Media     |
| US-PLAN-ERD-006 | Como DIPLADE quiero gestionar proceso de actualización ERD para cumplir ciclo decenal                        | Alta      |

---

### US Módulo PROT Digital

| ID               | User Story                                                                                             | Prioridad |
| ---------------- | ------------------------------------------------------------------------------------------------------ | --------- |
| US-PLAN-PROT-001 | Como Analista DIPLADE quiero visualizar zonificación PROT en visor geoespacial para evaluar territorio | Alta      |
| US-PLAN-PROT-002 | Como Analista DIPLADE quiero validar compatibilidad IPR↔Zona para prevenir conflictos territoriales    | Alta      |
| US-PLAN-PROT-003 | Como Sistema quiero alertar proyectos en zonas incompatibles para bloquear avance sin revisión         | Alta      |
| US-PLAN-PROT-004 | Como Ciudadano quiero consultar aptitud territorial de un predio para orientar inversión privada       | Media     |

---

### US Módulo ARI/PROPIR

| ID              | User Story                                                                                              | Prioridad |
| --------------- | ------------------------------------------------------------------------------------------------------- | --------- |
| US-PLAN-ARI-001 | Como Jefe de División quiero solicitar iniciativa para ARI vía formulario digital para agilizar proceso | Alta      |
| US-PLAN-ARI-002 | Como DIPLADE quiero priorizar iniciativas con scoring multicriterio para transparentar decisiones       | Alta      |
| US-PLAN-ARI-003 | Como DIPIR quiero consolidar ARI por fuente de financiamiento para presentar CORE                       | Alta      |
| US-PLAN-ARI-004 | Como Jefe DIPLADE quiero simular escenarios presupuestarios para evaluar alternativas                   | Media     |
| US-PLAN-ARI-005 | Como DIPIR quiero exportar ARI en formato DIPRES para integración con presupuesto nacional              | Alta      |

---

### US Módulo Observatorio

| ID              | User Story                                                                                    | Prioridad |
| --------------- | --------------------------------------------------------------------------------------------- | --------- |
| US-PLAN-OBS-001 | Como Analista quiero consultar indicadores territoriales por comuna para diagnóstico local    | Alta      |
| US-PLAN-OBS-002 | Como DIPLADE quiero vincular indicadores a objetivos ERD para medir avance estratégico        | Alta      |
| US-PLAN-OBS-003 | Como Sistema quiero alertar brechas por eje estratégico para priorizar intervención           | Media     |
| US-PLAN-OBS-004 | Como Observatorio quiero publicar tablero mensual de indicadores para transparencia           | Media     |
| US-PLAN-OBS-005 | Como Usuario externo quiero descargar series históricas en formato abierto para investigación | Baja      |

---

### US Módulo Participación

| ID               | User Story                                                                                              | Prioridad |
| ---------------- | ------------------------------------------------------------------------------------------------------- | --------- |
| US-PLAN-PART-001 | Como DIPLADE quiero registrar cabildo territorial con asistencia y propuestas para documentar proceso   | Alta      |
| US-PLAN-PART-002 | Como Sistema quiero sintetizar aportes ciudadanos con IA para facilitar análisis                        | Media     |
| US-PLAN-PART-003 | Como DIPLADE quiero trazar propuesta ciudadana a iniciativa para demostrar incidencia                   | Media     |
| US-PLAN-PART-004 | Como Jefe DIPLADE quiero reportar participación acumulada por territorio para evaluar representatividad | Media     |

---

### US Módulo Apoyo Comunal

| ID              | User Story                                                                                   | Prioridad |
| --------------- | -------------------------------------------------------------------------------------------- | --------- |
| US-PLAN-MUN-001 | Como SECPLA quiero solicitar asistencia técnica para formulación de proyectos RS             | Alta      |
| US-PLAN-MUN-002 | Como Analista DIPLADE quiero acceder a repositorio de PLADECOs para verificar coherencia ERD | Alta      |
| US-PLAN-MUN-003 | Como Sistema quiero recomendar "Proyectos Tipo" a municipios según sus brechas territoriales | Media     |

---

## Matriz de Trazabilidad

| Proceso                    | User Stories                | Entidades                                             |
| -------------------------- | --------------------------- | ----------------------------------------------------- |
| P1: Actualización ERD      | US-PLAN-ERD-001 a 006       | ERD, EjeEstrategico, Lineamiento, ObjetivoEstrategico |
| P2: Ciclo ARI/PROPIR       | US-PLAN-ARI-001 a 005       | ARI, LineaARI, IPR                                    |
| P3: Validación PROT        | US-PLAN-PROT-001 a 004      | ZonaPROT, IPR                                         |
| P4: Gestión CDP            | (4 US implícitas en D-EJEC) | ConvenioProgramacion, HitoCDP                         |
| P5: Evaluación Indicadores | US-PLAN-OBS-001 a 005       | IndicadorERD, MedicionIndicador                       |
| P6: Asistencia Municipal   | US-PLAN-MUN-001 a 003       | SolicitudAsistencia, PLADECO                          |

---

## Entidades de Datos

| Entidad                | Atributos Clave                                                    | Relaciones                      |
| ---------------------- | ------------------------------------------------------------------ | ------------------------------- |
| `ERD`                  | id, nombre, periodo_inicio, periodo_fin, estado                    | → EjeEstrategico[]              |
| `EjeEstrategico`       | id, erd_id, codigo, nombre, descripcion                            | → Lineamiento[]                 |
| `Lineamiento`          | id, eje_id, codigo, nombre                                         | → ObjetivoEstrategico[]         |
| `ObjetivoEstrategico`  | id, lineamiento_id, codigo, nombre, indicador, meta                | → IPR[], ActividadEstrategica[] |
| `IndicadorERD`         | id, objetivo_id, nombre, formula, linea_base, meta, año            | → MedicionIndicador[]           |
| `MedicionIndicador`    | id, indicador_id, periodo, valor_real, fuente                      |                                 |
| `ZonaPROT`             | id, macrozona, tipo_uso, condiciones_vinculantes, geometria        | → Territorio                    |
| `ARI`                  | id, año, estado, fecha_presentacion, monto_total                   | → LineaARI[]                    |
| `LineaARI`             | id, ari_id, ipr_id, prioridad, monto_solicitado, monto_asignado    | → IPR                           |
| `ConvenioProgramacion` | id, ministerio, monto_total, vigencia_inicio, vigencia_fin, estado | → HitoCDP[]                     |
| `HitoCDP`              | id, convenio_id, descripcion, fecha_comprometida, monto, estado    |                                 |
| `CabildoTerritorial`   | id, fecha, comuna, participantes, propuestas_count                 | → PropuestaCiudadana[]          |

---

## Sistemas Involucrados

| Sistema   | Rol                                        | Dominio |
| --------- | ------------------------------------------ | ------- |
| GORE OS   | Sistema central de planificación y gestión | D-PLAN  |
| IDE Ñuble | Visor geoespacial para PROT y territorios  | D-TERR  |
| SIGFE     | Integración presupuestaria nacional        | D-FIN   |
| BIP       | Banco Integrado de Proyectos (SNI)         | D-FIN   |

---

## Normativa Aplicable

| Norma                   | Artículos  | Contenido                                                               |
| ----------------------- | ---------- | ----------------------------------------------------------------------- |
| LOC GORE (DFL 1-19.175) | Art. 16    | Funciones: diseñar, elaborar, aprobar políticas, planes, programas      |
| LOC GORE                | Art. 17    | PROT obligatorio: macrozonificación, condiciones vinculantes            |
| LOC GORE                | Art. 20    | Atribuciones CORE: aprobar ERD, PROT, planes reguladores metropolitanos |
| LOC GORE                | Art. 21    | Transferencia de competencias en ordenamiento territorial               |
| LOC GORE                | Art. 75-81 | Fondos regionales: FNDR, ISAR, convenios                                |
| Ley 20.500              | -          | Participación ciudadana en gestión pública                              |

---

## Referencias Cruzadas

| Dominio   | Relación                                                          |
| --------- | ----------------------------------------------------------------- |
| D-TERR    | ZonaPROT definida en IDE; visor geoespacial compartido            |
| D-FIN     | IPR vinculadas a objetivos ERD; rendiciones de convenios          |
| D-EJEC    | Iniciativas priorizadas en ARI se ejecutan vía convenios          |
| D-COORD   | Compromisos Gobernador vinculados a objetivos ERD                 |
| D-GESTION | OKRs institucionales alineados con ejes ERD                       |
| D-EVOL    | Proyección de cumplimiento ERD; alimenta KB regional              |
| D-SEG     | Política Regional Seguridad → Eje Seguridad en ERD                |
| FÉNIX     | Objetivos ERD sin avance >180 días activan intervención Nivel III |

---

*Documento parte de GORE_OS v5.0*
