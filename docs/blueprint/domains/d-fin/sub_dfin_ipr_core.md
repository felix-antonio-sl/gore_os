# D-FIN Subdominio: Core IPR

> Parte de: [D-FIN](../domain_d-fin.md) | [GORE_OS Blueprint](../../vision_general.md)  
> Función: Gestión del Ciclo de Vida de Intervenciones Públicas Regionales

---

## Taxonomía IPR

```text
IPR (Intervención Pública Regional)
├── IDI (Iniciativa de Inversión)
│   ├── Gasto de capital (S.31/S.33)
│   ├── Requiere RS/AD de MDSF
│   └── Registro obligatorio en BIP
├── PPR (Programa Público Regional)
│   ├── Gasto corriente/mixto (S.24)
│   ├── Ejecución directa GORE (Glosa 06) → RF DIPRES/SES
│   └── Transferencia a entidad pública → ITF interno GORE
└── Proyecto_Seguridad
    ├── Hereda de IPR
    └── Reglas especiales: validación SPD, convenio municipal
```

---

## Fases del Ciclo de Vida

| Fase | Nombre                            | Descripción                                | Resultado                |
| ---- | --------------------------------- | ------------------------------------------ | ------------------------ |
| 1    | Ingreso/Pertinencia/Admisibilidad | Recepción, filtro CDR, revisión documental | ADMISIBLE / INADMISIBLE  |
| 2    | Evaluación Técnico-Económica      | RS/RF/ITF según track                      | RATE aprobado            |
| 3    | Financiamiento                    | CDP, Acuerdo CORE si aplica                | Recursos asegurados      |
| 4    | Gestión Presupuestaria            | Resolución, Convenio                       | Formalización            |
| 5    | Ejecución                         | Licitación, Supervisión, EP/Transferencias | Avance físico-financiero |
| 6    | Modificaciones                    | Aumento costo, Prórroga, Cambio alcance    | Convenio modificatorio   |
| 7    | Cierre                            | Recepción, Rendición, Reintegro, Garantías | IPR cerrada              |

Estados Transversales: `SUSPENDIDA`, `CANCELADA`

---

## Procesos BPMN

### P1: Ingreso, Pertinencia y Admisibilidad

```mermaid
flowchart TD
    subgraph EE["🏢 Entidad Externa"]
        A["📄 Postulación<br/>preparada"]
    end

    subgraph GORE["🏛️ GORE Ñuble"]
        B["📬 Oficina Partes:<br/>Recepcionar y registrar"]
        C["📊 DIPIR:<br/>Registrar en sistema"]
        D["👥 CDR:<br/>Evaluar pertinencia"]
        E{"¿Pre-admisible?"}
        F["✅ PRE-ADMISIBLE"]
        G["❌ NO PRE-ADMISIBLE"]
        H["🔍 Analista:<br/>Revisión documental"]
        I{"Estado<br/>admisibilidad"}
        J["✅ ADMISIBLE"]
        K["⚠️ CON OBSERVACIONES"]
        L["❌ INADMISIBLE"]
        M["📣 Notificar resultado"]
        N["📝 Subsanar (plazo)"]
    end

    A --> B --> C --> D --> E
    E -->|"Sí"| F --> H --> I
    E -->|"No"| G --> M
    I -->|"OK"| J --> M
    I -->|"Observa"| K --> M --> N --> A
    I -->|"Rechaza"| L --> M
```

| Rol                   | Responsabilidad                 |
| --------------------- | ------------------------------- |
| Oficina de Partes     | Recepcionar, registrar, derivar |
| Jefatura DIPIR        | Registrar, convocar CDR         |
| CDR                   | Evaluar pertinencia estratégica |
| Analista Preinversión | Revisión documental exhaustiva  |

### P2: Evaluación Técnico-Económica

```mermaid
flowchart TD
    A["IPR Admisible"] --> B{"Tipo de<br/>Iniciativa"}
    
    B -->|"Proyecto IDI"| C["Track A:<br/>SNI/MDSF"]
    B -->|"Programa GORE"| D["Track B:<br/>Glosa 06/DIPRES"]
    B -->|"FRIL/FRPD/C33/S8%"| E["Track C:<br/>Vías Simplificadas"]
    B -->|"Transf. Entidad Púb."| F["Track D:<br/>ITF Interno"]

    C --> C3["RATE: RS/AD/FI/OT"]
    D --> D4["RF/FI/OT"]
    E --> E3["RATE: APROBADO/FI/OT"]
    F --> F4["ITF Interno"]
```

| Código | Tipo                        | Evaluador  | Aplica a             |
| ------ | --------------------------- | ---------- | -------------------- |
| RS     | Recomendación Satisfactoria | MDSF/SNI   | IDI                  |
| AD     | Admisible                   | MDSF/SNI   | Conservación         |
| RF     | Resultado Favorable         | DIPRES/SES | PPR Glosa 06         |
| ITF    | Informe Técnico Favorable   | GORE       | PPR Transferencia    |
| FI     | Favorable con Indicaciones  | Varios     | Aprobado con ajustes |
| OT     | Objetado Técnicamente       | Cualquiera | Rechazado            |

### P3: Obtención de Financiamiento

```mermaid
flowchart TD
    A["IPR con RS/RF"] --> B{"¿Requiere<br/>Acuerdo CORE?"}
    
    B -->|"No"| C["Solicitar CDP"] --> D["DAF emite CDP"] --> E["Instrucción a<br/>Depto. Presupuesto"]
    
    B -->|"Sí"| F["Preparar carpeta<br/>CORE"] --> G["Envío formal<br/>al CORE"] --> H["Votación CORE"] --> I{"¿Aprobado?"}
    I -->|"✅"| J["Certificado<br/>Acuerdo CORE"] --> K["Solicitar creación<br/>presupuestaria"]
    I -->|"❌"| L["Rechazado"]
```

| Condición                       | ¿Requiere CORE? | Fundamento       |
| ------------------------------- | --------------- | ---------------- |
| Nueva asignación presupuestaria | ✅ Sí            | LOC GORE Art. 36 |
| Nuevo programa/proyecto         | ✅ Sí            | LOC GORE Art. 36 |
| Modificación > 5% costo total   | ✅ Sí            | Glosa 02         |
| Aumento costo ≤ 5%              | ❌ No            | Res. Gobernador  |
| Uso 3% emergencia (Glosa 14)    | ❌ No            | Glosa 14         |

### P4: Formalización

```mermaid
flowchart TD
    A["Financiamiento<br/>aprobado"] --> B{"Tipo"}
    
    B -->|"Interna"| C["Resolución GORE"]
    B -->|"Afecta Partida 31"| D["Solicitud DIPRES"]
    
    C & D --> E["Visaciones<br/>(DAF, DIPIR, Jurídica)"]
    E --> F["Firma Gobernador/a"]
    F --> G{"¿Transferencia?"}
    G -->|"Sí"| H["Convenio"] --> I["Firma GORE + Ejecutor"]
    G -->|"No"| J["Programar ejecución directa"]
```

### P4-bis: Inducción de Ejecutor

```mermaid
flowchart LR
    A["Convenio<br/>Formalizado"] --> B["Reunión Inicial"]
    B --> C["Entrega Carpeta"]
    C --> D["Cronograma Acordado"]
    D --> E["Designar Contraparte"]
    E --> F["Capacitación SISREC"]
```

### P5: Ejecución y Supervisión

> [!IMPORTANT]
> **Flujos bidireccionales según tipo de instrumento:**
> - **Patrón A (IDI/Obras):** Ejecuta → Presenta EP → Valida D-EJEC → Paga D-BACK
> - **Patrón B (PPR/Transf):** Paga anticipo → Ejecuta → Rinde SISREC → Aprueba DAF

```mermaid
flowchart TD
    subgraph INICIO["🚀 Inicio"]
        A["Chequeo documentación"]
        B["Reunión coordinación"]
        C["Carpeta seguimiento"]
    end

    subgraph LICITACION["📋 Licitación (si aplica)"]
        D["Bases y publicación MP"]
        E["Adjudicación"]
        F["Contrato"]
        G["Entrega terreno/Inicio"]
    end

    subgraph SEGUIMIENTO["📊 Seguimiento"]
        H["Visitas a terreno"]
        I["Revisión informes"]
        J["Estados de Pago / Rendiciones parciales"]
        K["Actualizar BIP"]
    end

    A --> B --> C --> D --> E --> F --> G
    G --> H --> I --> J --> K
```

### P6: Modificaciones en Ejecución

```mermaid
flowchart TD
    A["Detectar necesidad"] --> B["UT prepara informe"]
    B --> C["Oficio formal al GORE"]
    C --> D["Supervisor analiza"]
    D --> E{"¿Altera objetivo?"}
    E -->|"Sí"| F["❌ Rechazar"]
    E -->|"No"| G["Verificar umbrales"]
    G --> H{"¿Requiere CORE/SNI?"}
    H -->|"Sí"| I["Nueva aprobación"]
    H -->|"No"| J["Aprobar internamente"]
    I & J --> K["Convenio modificatorio"]
```

### P7: Cierre Técnico-Financiero

```mermaid
flowchart TD
    subgraph CIERRE_TEC["📋 Cierre Técnico"]
        A["Recepción provisoria"]
        B["Período garantía"]
        C["Recepción definitiva"]
        D["Informe final"]
    end

    subgraph CIERRE_FIN["💰 Cierre Financiero"]
        E["Rendición final SISREC"]
        F["Revisión DAF"]
        G{"¿Saldos?"}
        H["Reintegro"]
        I["Resolución cierre"]
        J["Devolución garantías"]
    end

    A --> B --> C --> D
    D --> E --> F --> G
    G -->|"Sí"| H --> I
    G -->|"No"| I
    I --> J
```

---

## Estados de Admisibilidad

| Estado                        | Descripción              | Siguiente Paso          |
| ----------------------------- | ------------------------ | ----------------------- |
| `PRE-ADMISIBLE CDR`           | Pertinencia aprobada     | Revisión documental     |
| `NO PRE-ADMISIBLE CDR`        | Pertinencia rechazada    | Archivar                |
| `ADMISIBLE`                   | Documentación completa   | Evaluación técnica (P2) |
| `ADMISIBLE CON OBSERVACIONES` | Documentación subsanable | 10 días para subsanar   |
| `INADMISIBLE`                 | Defectos no subsanables  | Rechazo formal          |

---

## Entidades de Datos

| Entidad              | Atributos Clave                                          | Relaciones                           |
| -------------------- | -------------------------------------------------------- | ------------------------------------ |
| `IPR`                | id, codigo_bip, nombre, naturaleza, mecanismo_id, estado | → Oportunidad, Mecanismo, Convenio[] |
| `Proyecto_Seguridad` | hereda IPR + tipo_prevencion, validacion_spd             | → IPR                                |
| `ActorIPR`           | id, ipr_id, actor_id, rol, fase, activo                  | → IPR, Actor                         |
| `EvaluacionIPR`      | id, ipr_id, tipo, resultado, observaciones               | → IPR                                |

---

## Referencias

- **Guía Gestión IPR:** [kb_gn_019_gestion_ipr_koda.yml](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/kb_gn_019_gestion_ipr_koda.yml)
- **Integración D-EJEC:** [domain_d-ejec.md](../domain_d-ejec.md) (Validación EP)
- **Integración D-BACK:** [domain_d-back.md](../domain_d-back.md#contabilidad-operativa) (Cadena contable)

---

*Subdominio parte de D-FIN | GORE_OS Blueprint Integral v5.5*
