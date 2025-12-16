# D06: Gestión de Flota Vehicular

## Metadatos del Dominio

| Campo           | Valor                                                                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID**          | `DOM-FLOTA`                                                                                                                                            |
| **Criticidad**  | 🟡 Media                                                                                                                                                |
| **Dueño**       | Jefe Servicios Generales                                                                                                                               |
| **Procesos**    | 1 (con 6 subprocesos)                                                                                                                                  |
| **Ref. Fuente** | [kb_gn_054_bpmn_c4_koda.yml](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/arquitectura/kb_gn_054_bpmn_c4_koda.yml) L.1210-1400 |

---

## Mapa General del Dominio

```mermaid
flowchart LR
    subgraph CICLO_FLOTA["🚗 Gestión de Flota"]
        S1["Registro<br/>vehículos"]
        S2["Asignación<br/>y uso"]
        S3["Bitácora<br/>de viaje"]
        S4["Combustible<br/>y kilometraje"]
        S5["Mantención<br/>vehicular"]
        S6["Siniestros y<br/>accidentes"]
    end

    S1 --> S2 --> S3 --> S4
    S4 --> S5
    S2 --> S6

    style S1 fill:#2196F3,color:#fff
    style S5 fill:#FF9800,color:#fff
    style S6 fill:#f44336,color:#fff
```

---

## P1: Gestión de Flota Vehicular

| Campo         | Valor                        |
| ------------- | ---------------------------- |
| **ID**        | `BPMN-GN-FLOTA-VEHICULAR-01` |
| **Normativa** | D.L. 799 (restricción uso)   |

### S1: Registro de Vehículos y Conductores

```mermaid
flowchart TD
    subgraph VEHICULOS["🚗 Registro de Vehículos"]
        A["Adquisición de<br/>vehículo"]
        B["Registrar en<br/>sistema interno"]
        C["Datos:<br/>• Patente<br/>• Modelo<br/>• Año<br/>• Tipo combustible"]
        D["Asignar a<br/>división/área"]
        E["Inscribir en<br/>Registro Automotor"]
    end

    subgraph CONDUCTORES["👤 Registro de Conductores"]
        F["Funcionario solicita<br/>autorización"]
        G["Verificar:<br/>• Licencia vigente<br/>• Clase apropiada<br/>• Hoja de vida"]
        H["Autorización de<br/>Jefe Servicios"]
        I["Registrar en<br/>nómina conductores"]
    end

    A --> B --> C --> D --> E
    F --> G --> H --> I

    style E fill:#2196F3,color:#fff
    style I fill:#4CAF50,color:#fff
```

### S2: Solicitud y Asignación

```mermaid
flowchart TD
    A["Funcionario solicita<br/>vehículo"] --> B["Ingresar solicitud:<br/>• Fecha/hora<br/>• Destino<br/>• Motivo<br/>• Pasajeros"]
    B --> C["Jefatura directa<br/>autoriza"]
    C --> D["Servicios Generales<br/>verifica disponibilidad"]
    D --> E{"¿Disponible?"}
    E -->|"Sí"| F["Asignar vehículo<br/>y conductor si aplica"]
    E -->|"No"| G["Buscar alternativa<br/>o reprogramar"]
    F --> H["Entregar llaves<br/>y bitácora"]

    style H fill:#4CAF50,color:#fff
```

### S3: Bitácora de Viaje

```mermaid
flowchart TD
    A["Recibir vehículo"] --> B["Registrar en bitácora:<br/>• Fecha/hora salida<br/>• Km inicial<br/>• Estado combustible"]
    B --> C["Realizar viaje"]
    C --> D["Al regresar registrar:<br/>• Fecha/hora llegada<br/>• Km final<br/>• Observaciones"]
    D --> E["Firmar bitácora"]
    E --> F["Devolver llaves<br/>a Servicios Generales"]

    style E fill:#FF9800,color:#fff
```

### S4: Gestión de Combustible

```mermaid
flowchart TD
    A["Vehículo requiere<br/>combustible"] --> B["Conductor solicita<br/>cupón/tarjeta"]
    B --> C["Servicios Generales<br/>autoriza"]
    C --> D["Cargar combustible<br/>en estación"]
    D --> E["Registrar:<br/>• Litros<br/>• Monto<br/>• Km actual"]
    E --> F["Devolver cupón<br/>con factura"]
    F --> G["Consolidar consumos<br/>mensuales"]
    G --> H["Analizar rendimiento<br/>km/litro"]

    style H fill:#9C27B0,color:#fff
```

### S5: Mantención Vehicular

```mermaid
flowchart TD
    subgraph PREVENTIVA["🔧 Mantención Preventiva"]
        A["Programar según<br/>km/tiempo"]
        B["Alertar próxima<br/>mantención"]
        C["Agendar con<br/>taller"]
        D["Ejecutar mantención"]
        E["Registrar en<br/>historial"]
    end

    subgraph CORRECTIVA["⚠️ Mantención Correctiva"]
        F["Detectar falla"]
        G["Reportar a<br/>Servicios Generales"]
        H["Evaluar:<br/>• Taller interno<br/>• Taller externo"]
        I["Reparar"]
        J["Certificar OK<br/>para uso"]
    end

    A --> B --> C --> D --> E
    F --> G --> H --> I --> J

    style E fill:#4CAF50,color:#fff
    style J fill:#FF9800,color:#fff
```

### Programa de Mantención

| Tipo           | Frecuencia | Acciones                  |
| -------------- | ---------- | ------------------------- |
| **Básica**     | 5.000 km   | Cambio aceite, filtros    |
| **Intermedia** | 15.000 km  | Frenos, neumáticos        |
| **Mayor**      | 30.000 km  | Revisión completa         |
| **Documentos** | Anual      | Revisión técnica, permiso |

### S6: Siniestros y Accidentes

```mermaid
flowchart TD
    A["Ocurre accidente"] --> B["Conductor toma<br/>medidas inmediatas"]
    B --> C["Llamar a<br/>Carabineros"]
    C --> D["Constancia<br/>policial"]
    D --> E["Reportar a<br/>Servicios Generales"]
    E --> F["Levantar acta<br/>de siniestro"]
    F --> G{"¿Daños a<br/>terceros?"}
    G -->|"Sí"| H["Activar seguro<br/>y procedimiento"]
    G -->|"No"| I["Evaluar daños<br/>propios"]
    H --> J["Seguimiento<br/>aseguradora"]
    I --> K["Cotizar<br/>reparación"]
    J & K --> L["Resolución<br/>administrativa"]
    L --> M["Determinar<br/>responsabilidades"]

    style D fill:#f44336,color:#fff
    style M fill:#9C27B0,color:#fff
```

### Información del Acta de Siniestro

| Dato         | Descripción          |
| ------------ | -------------------- |
| Fecha y hora | Del accidente        |
| Lugar        | Dirección exacta     |
| Conductor    | Funcionario a cargo  |
| Descripción  | Circunstancias       |
| Testigos     | Identificación       |
| Daños        | Propios y a terceros |
| N° Parte     | Carabineros          |

---

## Restricciones Normativas

### D.L. 799 (Uso de Vehículos Fiscales)

| Restricción            | Detalle                                 |
| ---------------------- | --------------------------------------- |
| **Fines de semana**    | Prohibido uso sin autorización especial |
| **Uso particular**     | Prohibido                               |
| **Fuera de la región** | Requiere autorización                   |
| **Horario**            | Jornada laboral (salvo excepciones)     |

> ⚠️ **Incumplimiento genera responsabilidad administrativa y patrimonial.**

---

## Métricas de Control

| Indicador                | Fórmula                        | Meta       |
| ------------------------ | ------------------------------ | ---------- |
| Rendimiento combustible  | Km / Litros                    | > 10 km/lt |
| % Mantención cumplida    | Mantenciones OK / Programadas  | > 95%      |
| Tasa de accidentabilidad | Accidentes / Vehículos         | < 5%       |
| Disponibilidad flota     | Días operativos / Días totales | > 90%      |

---

## Sistemas Involucrados

| Sistema                  | Función                 |
| ------------------------ | ----------------------- |
| `SYS-SIGAS`              | Inventario de vehículos |
| Sistema interno de flota | Bitácoras, mantenciones |

---

## Referencias Cruzadas

| Dominio Relacionado                                                                                                                           | Vínculo                            |
| --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| [D05 Inventarios y AF](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/arquitectura/bpmn/D05_inventarios_activo_fijo.md) | Vehículos como activo fijo         |
| [D04 Compras](file:///Users/felixsanhueza/Developer/gorenuble/knowledge/domains/gn/arquitectura/bpmn/D04_compras_contrataciones.md)           | Adquisición vehículos, combustible |

---

*Última actualización: 2025-12-16*
