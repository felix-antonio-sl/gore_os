# D09: Gestión Operativa CIES/SITIA (Seguridad Pública)

## Metadatos del Dominio

| Campo           | Valor                                                                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID**          | `DOM-CIES`                                                                                                                                             |
| **Criticidad**  | 🟠 Alta                                                                                                                                                 |
| **Dueño**       | Supervisor CIES                                                                                                                                        |
| **Procesos**    | 3                                                                                                                                                      |
| **Subprocesos** | ~8                                                                                                                                                     |
| **Ref. Fuente** | [kb_gn_054_bpmn_c4_koda.yml](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/arquitectura/kb_gn_054_bpmn_c4_koda.yml) L.4142-4306 |

---

## Mapa General del Dominio

```mermaid
flowchart LR
    subgraph CIES["🎥 Centro CIES-ÑUBLE"]
        P1["P1: Monitoreo y<br/>Detección"]
        P2["P2: Coordinación<br/>Interinstitucional"]
        P3["P3: Gestión de<br/>Evidencias"]
    end

    subgraph SITIA["🤖 Integración SITIA"]
        S1["SITIA-Patentes"]
        S2["SITIA-Armas"]
        S3["SITIA-Evidencia"]
        S4["SITIA-Unificación"]
    end

    P1 --> P2
    P1 --> P3
    P1 <--> S1 & S2 & S4
    P3 <--> S3

    style P1 fill:#2196F3,color:#fff
    style P2 fill:#FF9800,color:#fff
    style P3 fill:#9C27B0,color:#fff
```

---

## Contexto Operativo

| Aspecto          | Detalle                                 |
| ---------------- | --------------------------------------- |
| **Cobertura**    | 16 horas (08:00-00:00), proyección 24/7 |
| **Ubicación**    | Sala de monitoreo GORE Ñuble            |
| **Coordinación** | Policías, emergencias, 21 municipios    |
| **Marco legal**  | Ley 21.427, Ley 20.965, Ley 20.502      |

---

## P1: Monitoreo, Detección y Escalamiento

| Campo       | Valor                             |
| ----------- | --------------------------------- |
| **ID**      | `BPMN-GN-CIES-SITIA-MONITOREO-01` |
| **Sistema** | HikCentral VMS                    |

### Diagrama de Flujo

```mermaid
flowchart TD
    subgraph MONITOREO["🎥 Monitoreo Continuo"]
        A["Operador CIES<br/>monitorea cámaras"]
        B["Sistemas SITIA<br/>detectan automáticamente:<br/>• Patentes alertadas<br/>• Armas visibles"]
    end

    subgraph DETECCION["⚡ Detección"]
        C["Identificar evento/<br/>incidente"]
        D{"Clasificar<br/>prioridad"}
        D -->|"🔴 Alta"| E["Alarma inmediata"]
        D -->|"🟠 Media"| F["Registro y seguimiento"]
        D -->|"🟢 Baja"| G["Solo registro"]
    end

    subgraph ESCALAMIENTO["📢 Escalamiento"]
        E --> H["Supervisor CIES<br/>evalúa"]
        H --> I["Activar protocolo<br/>según tipo"]
        I --> J["Coordinar con:<br/>• Carabineros<br/>• PDI<br/>• Bomberos<br/>• SAMU"]
    end

    A --> C
    B --> C
    C --> D
    F --> H

    style E fill:#f44336,color:#fff
    style J fill:#4CAF50,color:#fff
```

### Clasificación de Incidentes

| Prioridad   | Tipo                              | Acción                   |
| ----------- | --------------------------------- | ------------------------ |
| 🔴 **Alta**  | Delito en curso, emergencia vital | Activación inmediata     |
| 🟠 **Media** | Sospecha, situación anómala       | Seguimiento y evaluación |
| 🟢 **Baja**  | Evento menor, registro            | Solo documentar          |

---

## P2: Coordinación Interinstitucional

| Campo         | Valor                                        |
| ------------- | -------------------------------------------- |
| **ID**        | `BPMN-GN-CIES-SITIA-COORD-01`                |
| **Entidades** | Carabineros, PDI, Bomberos, SAMU, Municipios |

### Diagrama de Flujo

```mermaid
flowchart TD
    A["Incidente<br/>clasificado"] --> B["Enlace CIES<br/>activa canal"]
    B --> C{"Tipo de<br/>emergencia"}
    
    C -->|"Seguridad"| D["📞 Carabineros<br/>133"]
    C -->|"Investigación"| E["📞 PDI<br/>134"]
    C -->|"Incendio"| F["📞 Bomberos<br/>132"]
    C -->|"Salud"| G["📞 SAMU<br/>131"]
    
    D & E & F & G --> H["Confirmar recepción<br/>y unidades"]
    H --> I["Seguimiento<br/>en tiempo real"]
    I --> J["Registro de<br/>respuesta"]
    J --> K["Cierre de<br/>incidente"]

    style K fill:#4CAF50,color:#fff
```

### Protocolos de Comunicación

| Canal                  | Uso                           |
| ---------------------- | ----------------------------- |
| Radio VHF              | Comunicación directa policías |
| Líneas directas        | Centrales de emergencia       |
| WhatsApp institucional | Coordinación municipal        |
| Plataforma SITIA       | Integración nacional          |

---

## P3: Gestión de Evidencias Digitales

| Campo          | Valor                               |
| -------------- | ----------------------------------- |
| **ID**         | `BPMN-GN-CIES-SITIA-EVIDENCIA-01`   |
| **Plataforma** | SITIA-Evidencia (Genetec Clearance) |

### Diagrama de Flujo

```mermaid
flowchart TD
    subgraph SOLICITUD["📋 Solicitud"]
        A["Fiscalía/Tribunal<br/>solicita evidencia"]
        B["Recepción oficio<br/>en GORE"]
        C["Verificar:<br/>• Orden judicial<br/>• Requerimiento MP"]
    end

    subgraph EXTRACCION["🎬 Extracción"]
        D["Supervisor CIES<br/>autoriza"]
        E["Localizar grabación<br/>en HikCentral"]
        F["Exportar clip<br/>seguro"]
        G["Subir a<br/>SITIA-Evidencia"]
    end

    subgraph ENTREGA["📤 Entrega"]
        H["Generar cadena<br/>de custodia"]
        I["Entrega por medio<br/>controlado"]
        J["Acta de entrega"]
        K["Registro para<br/>trazabilidad"]
    end

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J --> K

    style J fill:#4CAF50,color:#fff
```

### Cadena de Custodia Digital

| Elemento        | Verificación      |
| --------------- | ----------------- |
| Hash de archivo | Integridad        |
| Metadatos       | Fecha/hora/cámara |
| Log de accesos  | Quién manipuló    |
| Firma digital   | Autenticidad      |

---

## Capacidades SITIA

### SITIA-Patentes

```mermaid
flowchart LR
    A["Red de pórticos<br/>públicos/privados"] --> B["Lectura automática<br/>de placas"]
    B --> C["Contraste en<br/>tiempo real"]
    C --> D{"¿Encargo de<br/>búsqueda?"}
    D -->|"Sí"| E["🚨 Alerta a CIES<br/>y policías"]
    D -->|"No"| F["Registro histórico"]

    style E fill:#f44336,color:#fff
```

### SITIA-Armas

```mermaid
flowchart LR
    A["Cámaras CIES"] --> B["Modelo IA<br/>(YOLOv11)"]
    B --> C{"¿Arma<br/>detectada?"}
    C -->|"Sí"| D["🚨 Alerta automática"]
    C -->|"No"| E["Continuar monitoreo"]
    D --> F["Operador verifica"]
    F --> G["Escalar si confirma"]

    style D fill:#f44336,color:#fff
```

---

## Gestión de Privacidad y Retención

### Política de Retención

| Aspecto               | Regla                           |
| --------------------- | ------------------------------- |
| **Retención normal**  | 30 días                         |
| **Eliminación**       | Segura e irreversible           |
| **Cautela ciudadana** | Hasta 6 meses (víctima/testigo) |

### Cumplimiento Normativo

```mermaid
flowchart TD
    A["Grabación<br/>generada"] --> B["Almacenar<br/>30 días"]
    B --> C{"¿Solicitud de<br/>cautela?"}
    C -->|"Sí"| D["Extender retención<br/>hasta 6 meses"]
    C -->|"No"| E["Eliminar<br/>automáticamente"]
    D --> F["Revisar al<br/>vencimiento"]
    F --> E

    style E fill:#607D8B,color:#fff
```

> ⚠️ **Ley 19.628**: Tratamiento de datos personales debe respetar licitud, finalidad y proporcionalidad.

---

## Sostenibilidad Operativa

### Modelo de Financiamiento

| Componente         | Fuente                          |
| ------------------ | ------------------------------- |
| Personal CIES      | Presupuesto anual GORE          |
| Mantención equipos | Garantía 22 meses + presupuesto |
| Servicios SITIA    | Convenio marco con SPD          |

### Mantención

```mermaid
flowchart LR
    A["Mantención<br/>preventiva"] -->|"Trimestral"| B["Revisión equipos"]
    B --> C["Actualizaciones<br/>software"]
    C --> D["Reporte estado"]

    style D fill:#4CAF50,color:#fff
```

---

## Sistemas Involucrados

| Sistema               | Función             |
| --------------------- | ------------------- |
| `SYS-HIKCENTRAL`      | VMS gestión cámaras |
| `SYS-SITIA`           | Plataforma nacional |
| `SYS-SITIA-EVIDENCIA` | Gestión evidencias  |
| `SYS-SITIA-PATENTES`  | Lectura placas      |
| `SYS-SITIA-ARMAS`     | Detección IA        |

---

## Normativa Aplicable

| Norma          | Alcance                    |
| -------------- | -------------------------- |
| **Ley 21.427** | Sistema Nacional Seguridad |
| **Ley 20.965** | Cámaras vigilancia         |
| **Ley 20.502** | ONEMI/funcionamiento       |
| **Ley 19.628** | Protección vida privada    |
| **Ley 21.719** | Datos personales           |

---

## Referencias Cruzadas

| Dominio Relacionado                                                                                                                              | Vínculo                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| [D01 Actos Administrativos](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/arquitectura/bpmn/D01_actos_administrativos.md) | Convenios con entidades |

---

*Última actualización: 2025-12-16*
