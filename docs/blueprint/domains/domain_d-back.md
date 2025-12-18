# D-BACK: Dominio de Gestión de Recursos Institucionales

> Parte de: [GORE_OS Vision General](../vision_general.md)  
> Capa: Habilitante (Soporte Operativo)  
> Función GORE: ADMINISTRAR  

---

## Glosario D-BACK

| Término           | Definición                                                                   |
| ----------------- | ---------------------------------------------------------------------------- |
| EUS               | Escala Única de Sueldos. Tabla de grados y asignaciones del sector público   |
| PAC-Compras       | Plan Anual de Compras. Programación de adquisiciones en Mercado Público      |
| PAC-Capacitación  | Plan Anual de Capacitación. Programa de formación funcionaria                |
| DNC               | Detección de Necesidades de Capacitación. Insumo para PAC-Capacitación       |
| CDP               | Certificado de Disponibilidad Presupuestaria. Ver D-FIN                      |
| OC                | Orden de Compra. Documento que formaliza adquisición                         |
| CM                | Convenio Marco. Mecanismo de compra pre-negociado en ChileCompra             |
| PPP               | Precio Promedio Ponderado. Método de valorización de inventarios             |
| FIFO              | First In, First Out. Método de valorización                                  |
| FEFO              | First Expired, First Out. Para productos perecibles                          |
| SIAPER            | Sistema de Información y Control del Personal de la Administración (CGR)     |
| PREVIRED          | Plataforma de pago de cotizaciones previsionales                             |
| TEF               | Transferencia Electrónica de Fondos. Pago bancario electrónico               |
| SIC               | Saldo Inicial de Caja. Recursos de arrastre del ejercicio anterior           |
| Deuda Flotante    | Obligaciones devengadas no pagadas al cierre del ejercicio (Ítem 34.07)      |
| Conciliación      | Proceso de cuadrar movimientos bancarios (cartola) con registros SIGFE       |
| Devengado         | Obligación contable exigible. Momento en que se reconoce el gasto            |
| Compromiso        | Obligación presupuestaria contraída formalmente (OC, contrato)               |
| Ítem 34.07        | Asignación presupuestaria para pago de deuda flotante del ejercicio anterior |
| Cartola Bancaria  | Extracto de movimientos de cuenta corriente emitido por el banco             |
| Partida Pendiente | Diferencia temporal entre registro SIGFE y movimiento bancario               |
| UCR               | Unidad Control de Rendiciones. Encargada de auditar rendiciones de terceros  |
| Compra Ágil       | Modalidad de compra competitiva para montos menores o iguales a 100 UTM      |
| Fondos Globales   | Fondos en efectivo o cta. corriente para gastos menores (caja chica) ≤3 UTM  |


---

## Propósito

Gestionar el ciclo de vida de todos los recursos institucionales del GORE: personas, bienes, servicios, infraestructura y presupuesto operativo, asegurando eficiencia, transparencia y cumplimiento normativo.

> Visión: Los recursos institucionales —humanos, materiales, financieros y tecnológicos— se gestionan como un sistema integrado que maximiza la eficiencia operativa y minimiza los riesgos de incumplimiento.

---

## Cinco Pilares del Dominio

| Pilar            | Componentes                                          |
| ---------------- | ---------------------------------------------------- |
| Personas         | Ciclo de vida funcionario, remuneraciones, bienestar |
| Abastecimiento   | Compras, contratos, proveedores                      |
| Patrimonio       | Inventarios, activo fijo, bodegas                    |
| Servicios        | Flota vehicular, mantención, infraestructura         |
| Contabilidad Op. | Caja, conciliación bancaria, contabilidad, cierre    |

---

## Módulos

### 1. Gestión de Personas (RRHH)

Ciclo de Vida:

```text
INGRESO → INDUCCIÓN → DESARROLLO → EVALUACIÓN → EGRESO
```

Subsistemas:

- Reclutamiento y selección
- Contratación y nombramiento
- Remuneraciones (EUS)
- Tiempo y asistencia
- Capacitación y desarrollo
- Bienestar funcionario
- Calificaciones

### 2. Abastecimiento y Compras

Cadena de Adquisición:

```text
PAC-Compras → REQUERIMIENTO → CDP → LICITACIÓN/CM → OC → RECEPCIÓN → PAGO
```

> Nota: CDP (Certificado de Disponibilidad Presupuestaria) se gestiona en [D-FIN](domain_d-fin.md#cadena-presupuestaria).

Mecanismos:

| Mecanismo          | Umbral        | Normativa / Plataforma        |
| ------------------ | ------------- | ----------------------------- |
| Fondos Globales    | < 3 UTM       | Res. Exenta / Caja Chica      |
| Compra Ágil        | ≤ 100 UTM     | Decreto 661 / Mercado Público |
| Convenio Marco     | Sin límite    | Mercado Público               |
| Licitación Pública | > 1.000 UTM   | Ley 19.886 / Mercado Público  |
| Licitación Privada | 100-1.000 UTM | Mercado Público               |
| Compra Directa     | < 100 UTM     | Mercado Público               |

### 3. Inventarios y Bodega

Métodos de Valorización:

| Método | Uso                                   |
| ------ | ------------------------------------- |
| PPP    | Precio Promedio Ponderado (default)   |
| FIFO   | First In, First Out                   |
| FEFO   | First Expired, First Out (perecibles) |

### 4. Activo Fijo

Criterio de Capitalización: Valor ≥ 3 UTM y vida útil > 1 año

Ciclo:

```text
ALTA → VALORIZACIÓN → DEPRECIACIÓN → MOVIMIENTOS → BAJA
```

### 5. Flota Vehicular

Restricciones D.L. 799:

- Uso solo en horario laboral
- Prohibido uso particular
- Autorización para fines de semana

### 6. Bienestar Funcionario

Prestaciones:

- Bonificaciones médicas
- Préstamos
- Subsidios por eventos
- Convenios con terceros

### 7. Contabilidad Operativa

Procesos:

| Proceso               | Descripción                                           |
| --------------------- | ----------------------------------------------------- |
| Gestión de Caja       | Saldos bancarios, programación de pagos, TEF          |
| Conciliación Bancaria | Cartolas vs SIGFE, partidas pendientes                |
| Contabilización       | Ingresos propios, gastos operativos, devengos         |
| Cierre Anual          | Corte compromisos, estados financieros, SIC           |
| Deuda Flotante        | Identificación, certificado, incorporación Ítem 34.07 |

Ciclo:

```text
REGISTRO → CONCILIACIÓN → CONTABILIZACIÓN → CIERRE → DEUDA FLOTANTE
```

> **⚠️ Triángulo de Integración Presupuestaria**:  \n> - **D-FIN** define distribución estratégica (ARI, CORE) y monitorea % ejecución como KPI de portafolio  \n> - **D-EJEC** valida técnicamente Estados de Pago (EP) y envía a D-BACK para procesamiento  \n> - **D-BACK** ejecuta la cadena contable: CDP → Compromiso → Devengo → Pago en SIGFE  \n>   \n> Este módulo gestiona las operaciones financieras internas del GORE como organización.

---

## 📋 Procesos BPMN

### Índice de Procesos

| Dominio      | ID    | Nombre                               | Líneas  |
| ------------ | ----- | ------------------------------------ | ------- |
| Compras      | D04   | Compras Públicas y Contrataciones    | 200-278 |
| Inventarios  | D05   | Gestión de Inventarios y Activo Fijo | 281-328 |
| Flota        | D06   | Gestión de Flota Vehicular           | 332-381 |
| Personas     | D07   | Gestión de Personas                  | 385-453 |
| Bienestar    | D07.B | Bienestar Funcionario                | 457-519 |
| Contabilidad | D08   | Contabilidad Operativa               | 523-629 |

### Mapa General Integrado

```mermaid
flowchart TB
    subgraph RRHH["👤 Gestión de Personas (D07)"]
        R1["Ingreso"]
        R2["Inducción"]
        R3["Remuneraciones"]
        R4["Tiempo"]
        R5["Desarrollo"]
        R6["Bienestar"]
        R7["Egreso"]
    end

    subgraph COMPRAS["🛒 Compras (D04)"]
        C1["PAC"]
        C2["Licitación"]
        C3["OC"]
        C4["Contratos"]
    end

    subgraph INVENTARIOS["📦 Inventarios (D05)"]
        I1["Bodegas"]
        I2["Activo Fijo"]
    end

    subgraph FLOTA["🚗 Flota (D06)"]
        F1["Vehículos"]
    end

    R1 --> R2 --> R3
    R3 --> R4 & R5 & R6 --> R7
    C1 --> C2 --> C3 --> C4
    C3 -.-> I1
    I1 --> I2
    C3 -.-> F1
```

---

### D04: Compras Públicas y Contrataciones

| Campo      | Valor                    |
| ---------- | ------------------------ |
| ID         | `DOM-COMPRAS`            |
| Criticidad | 🟠 Alta                   |
| Dueño      | Unidad de Abastecimiento |

#### P1: Plan Anual de Compras (PAC)

```mermaid
flowchart TD
    A["Divisiones identifican<br/>necesidades"] --> B["Unidades envían<br/>requerimientos"]
    B --> C["Abastecimiento consolida"]
    C --> D["Clasificar por:<br/>• Convenio Marco<br/>• Licitación<br/>• Compra Directa"]
    D --> E["Validación<br/>presupuestaria (DAF)"]
    E --> F["Aprobación<br/>Gobernador/a"]
    F --> G["Publicar PAC en<br/>Mercado Público"]
```

#### P2: Licitación Pública

```mermaid
flowchart LR
    A["Preparación<br/>Bases"] --> B["Publicación<br/>en MP"]
    B --> C["Consultas y<br/>Respuestas"]
    C --> D["Recepción<br/>Ofertas"]
    D --> E["Evaluación<br/>Comisión"]
    E --> F["Adjudicación"]
    F --> G["Notificación"]
```

#### Mecanismos de Compra

```mermaid
flowchart TD
    A["Necesidad de<br/>adquisición"] --> B{"Monto<br/>estimado"}
    
    B -->|"> 1.000 UTM"| C["🏛️ Licitación<br/>Pública"]
    B -->|"100-1.000 UTM"| D["📋 Licitación<br/>Privada"]
    B -->|"< 100 UTM"| E["💳 Compra<br/>Directa"]
    
    A --> F{"¿Existe<br/>Convenio Marco?"}
    F -->|"Sí"| G["🛒 Convenio<br/>Marco"]
```

#### Umbrales y Modalidades (Decreto N° 661/2024)

| Rango (UTM)    | Modalidad                   | Requisitos Mínimos                      |
| -------------- | --------------------------- | --------------------------------------- |
| < 3 UTM        | Fondos Globales Menores     | Sin OC obligatoria, boleta directa      |
| 3 - 100 UTM    | Compra Ágil                 | Mínimo 3 cotizaciones en plataforma     |
| 100 - 1000 UTM | Convenio Marco / Licitación | Bases administrativas, CDP previo       |
| > 1000 UTM     | Licitación Pública          | Comisión evaluadora, Resolución fundada |
| > 5000 UTM     | Licitación Pública          | Boleta de garantía de seriedad (≤3%)    |


#### P3: Órdenes de Compra

```mermaid
flowchart TD
    A["Adjudicación"] --> B["Generar OC"]
    B --> C["Asociar CDP"]
    C --> D["Firma jefatura"]
    D --> E["Enviar a proveedor"]
    E --> F["Proveedor acepta"]
    F --> G["Recepción bienes"]
    G --> H{"¿Conforme?"}
    H -->|"Sí"| I["Facturación → Pago"]
    H -->|"No"| J["Devolución"]
```

#### P4: Gestión de Contratos

```mermaid
flowchart TD
    A["Adjudicación<br/>formalizada"] --> B["Elaborar contrato"]
    B --> C["Revisión Jurídica"]
    C --> D["Firma proveedor"]
    D --> E["Firma GORE"]
    E --> F["Resolución aprobatoria"]
    F --> G["Registro en sistema"]
    G --> H["Monitoreo<br/>cumplimiento"]
    H --> I{"¿Término?"}
    I -->|"Vencimiento"| J["Evaluar renovación"]
    I -->|"Incumplimiento"| K["Multa/Término anticipado"]
    I -->|"Cumplimiento OK"| L["Cierre contrato"]
```

---

### D05: Gestión de Inventarios y Activo Fijo

| Campo      | Valor                |
| ---------- | -------------------- |
| ID         | `DOM-INVENTARIOS-AF` |
| Criticidad | 🟡 Media              |
| Dueño      | DAF                  |

#### Recepción de Bienes

```mermaid
flowchart TD
    A["OC aceptada"] --> B["Proveedor entrega"]
    B --> C["Bodeguero verifica:<br/>• Cantidad<br/>• Calidad<br/>• Guía"]
    C --> D{"¿Conforme?"}
    D -->|"Sí"| E["Firmar guía"]
    D -->|"No"| F["Rechazar"]
    E --> G["Ingresar en Sistema"]
    G --> H["Actualizar stock"]
```

#### Alta de Activo Fijo

```mermaid
flowchart TD
    A["Bien adquirido"] --> B{"Valor ≥ 3 UTM<br/>y vida útil > 1 año"}
    B -->|"Sí"| C["Activo Fijo"]
    B -->|"No"| D["Gasto del período"]
    C --> E["Asignar N° inventario"]
    E --> F["Plaquetear bien"]
    F --> G["Registrar en Sistema"]
    G --> H["Contabilizar SIGFE"]
```

#### Baja de Bienes

```mermaid
flowchart TD
    A["Identificar bien"] --> B{"Causal"}
    B -->|"Deterioro"| C["Informe técnico"]
    B -->|"Obsolescencia"| D["Informe funcional"]
    B -->|"Pérdida/Hurto"| E["Denuncia + Sumario"]
    B -->|"Donación"| F["Autorización"]
    C & D & E & F --> G["Resolución de baja"]
    G --> H["Baja en Sistema"]
    H --> I["Contabilizar SIGFE"]
```

---

### D06: Gestión de Flota Vehicular

| Campo      | Valor                    |
| ---------- | ------------------------ |
| ID         | `DOM-FLOTA`              |
| Criticidad | 🟡 Media                  |
| Dueño      | Jefe Servicios Generales |

#### Solicitud y Asignación

```mermaid
flowchart TD
    A["Funcionario solicita"] --> B["Ingresar solicitud:<br/>• Fecha/hora<br/>• Destino<br/>• Motivo"]
    B --> C["Jefatura autoriza"]
    C --> D["Verificar disponibilidad"]
    D --> E{"¿Disponible?"}
    E -->|"Sí"| F["Asignar vehículo"]
    E -->|"No"| G["Reprogramar"]
    F --> H["Entregar llaves y bitácora"]
```

#### Mantención Vehicular

```mermaid
flowchart LR
    subgraph PREVENTIVA["🔧 Preventiva"]
        A["Programar según km"]
        B["Ejecutar mantención"]
        C["Registrar historial"]
    end

    subgraph CORRECTIVA["⚠️ Correctiva"]
        D["Detectar falla"]
        E["Reparar"]
        F["Certificar OK"]
    end

    A --> B --> C
    D --> E --> F
```

#### Programa de Mantención

| Tipo       | Frecuencia | Acciones                  |
| ---------- | ---------- | ------------------------- |
| Básica     | 5.000 km   | Cambio aceite, filtros    |
| Intermedia | 15.000 km  | Frenos, neumáticos        |
| Mayor      | 30.000 km  | Revisión completa         |
| Documentos | Anual      | Revisión técnica, permiso |

---

### D07: Gestión de Personas

| Campo      | Valor                       |
| ---------- | --------------------------- |
| ID         | `DOM-RRHH`                  |
| Criticidad | 🟠 Alta                      |
| Dueño      | Área de Gestión de Personas |

#### P1: Ingreso y Contratación

```mermaid
flowchart LR
    A["Vacante"] --> B["Publicar<br/>llamado"]
    B --> C["Filtro<br/>curricular"]
    C --> D["Evaluación"]
    D --> E["Entrevista"]
    E --> F["Selección"]
    F --> G["Contratación"]
    G --> H["Integración con ERP RRHH (e.g. SIAPER)"]
```

#### Tipos de Contrato

| Tipo       | Descripción                        |
| ---------- | ---------------------------------- |
| Planta     | Cargo titular, carrera funcionaria |
| Contrata   | Transitorio, renovación anual      |
| Honorarios | Servicios específicos              |

#### P2: Remuneraciones

```mermaid
flowchart TD
    A["Inicio mes"] --> B["Recopilar novedades:<br/>• Licencias<br/>• Horas extra<br/>• Descuentos"]
    B --> C["Calcular bruto"]
    C --> D["Aplicar descuentos"]
    D --> E["Generar liquidación"]
    E --> F["Autorizar pago"]
    F --> G["Pagar Previred"]
    G --> H["Transferir a funcionarios"]
    H --> I["Contabilizar SIGFE"]
```

#### Ciclo Mensual de Remuneraciones

| Periodo | Actividad                                                    | Responsable               |
| ------- | ------------------------------------------------------------ | ------------------------- |
| 01 - 14 | Recopilación de novedades (Licencias, Permisos, Horas Extra) | Profesional GDP           |
| 15 - 17 | Cálculo, liquidación y registro en sistema                   | Gestora de Remuneraciones |
| 18      | Visación técnica, jurídica y de finanzas                     | GDP / Jurídica / Finanzas |
| 19      | Pago de Remuneraciones (Fecha legal)                         | Tesorería                 |
| 19 - 25 | Procesamiento de Reliquidaciones y Planilla Suplementaria    | Gestora de Remuneraciones |
| 20 - 30 | Pago de Cotizaciones Previsionales (PREVIRED)                | Tesorería                 |

> **Tope Institucional Horas Extraordinarias** (PR-DAF-0005):
> - Diurnas: Máximo 20 horas mensuales.
> - Nocturnas/Festivas: Máximo 16 horas mensuales.
> - *Excepción: Conductores institucionales y situaciones de emergencia.*

#### P3: Capacitación y Calificaciones

```mermaid
flowchart LR
    subgraph CAPACITACION["🎓 Capacitación"]
        A["DNC"] --> B["PAC-Capacitación"] --> C["Ejecutar"] --> D["Certificar"]
    end

    subgraph CALIFICACION["📊 Calificación"]
        E["Precalificación"] --> F["Junta"]
        F --> G["Listas 1-4"]
    end
```

#### P4: Egreso

```mermaid
flowchart TD
    A["Egreso"] --> B{"Causal"}
    B -->|"Renuncia"| C["Voluntario"]
    B -->|"Jubilación"| D["Retiro"]
    B -->|"Término contrata"| E["No renovación"]
    B -->|"Disciplinario"| F["Destitución"]
    C & D & E & F --> G["Cierre:<br/>• Entrega cargo<br/>• Devolución equipos<br/>• Baja sistemas"]
```

#### P5: Control de Asistencia (Absorción SIGPER)

> **Origen:** Módulo Control Asistencia SIGPER. Permite integración con reloj biométrico y gestión de teletrabajo.

```mermaid
flowchart TD
    subgraph MARCACION["⏱️ Captura Marcaciones"]
        M1["Reloj biométrico<br/>(ZK/Anviz/HikVision)"]
        M2["Marcación web<br/>Teletrabajo"]
        M3["App móvil<br/>GPS opcional"]
    end
    
    subgraph PROCESO["⚙️ Procesamiento"]
        P1["Consolidar<br/>marcaciones diarias"]
        P2["Calcular horas<br/>trabajadas"]
        P3["Identificar<br/>novedades"]
        P4["Generar tiempo<br/>excedente/faltante"]
    end
    
    subgraph RESULTADO["📊 Resultado"]
        R1["Libro asistencia<br/>mensual"]
        R2["Horas extras<br/>25%/50%"]
        R3["Atrasos/<br/>salidas anticipadas"]
        R4["Justificaciones<br/>pendientes"]
    end
    
    M1 & M2 & M3 --> P1
    P1 --> P2 --> P3 --> P4
    P4 --> R1 & R2 & R3 & R4
```

#### P6: Viáticos Nacionales y Extranjeros (Absorción SIGPER)

> **Origen:** Módulo Viáticos SIGPER. Cumple DFL 262 para viáticos nacionales.

```mermaid
flowchart LR
    subgraph SOLICITUD["📝 Solicitud"]
        S1["Funcionario<br/>ingresa cometido"]
        S2["Define destino<br/>y fechas"]
        S3["Sistema calcula<br/>monto por grado"]
    end
    
    subgraph AUTORIZACION["✅ Autorización"]
        A1["Jefatura directa<br/>autoriza"]
        A2["DAF valida<br/>disponibilidad"]
        A3["Asignar código<br/>SIGFE"]
    end
    
    subgraph PAGO["💳 Pago y Cierre"]
        P1["Tramitar<br/>resolución"]
        P2["Girar viático"]
        P3["Rendición<br/>post-comisión"]
        P4["Centralización<br/>contable"]
    end
    
    S1 --> S2 --> S3
    S3 --> A1 --> A2 --> A3
    A3 --> P1 --> P2 --> P3 --> P4
```

#### Distribución de Viáticos (DFL 262)

| Porcentaje | Condición                                                |
| ---------- | -------------------------------------------------------- |
| 100%       | Pernoctar fuera + alimentación propia                    |
| 60%        | Sin pernoctar, pero jornada completa fuera               |
| 50%        | Conglomerado urbano (mismo día, sin pernocte)            |
| 40%        | Pernoctar en alojamiento institucional                   |
| 20%        | Viaje mismo día, media jornada                           |
| 10%        | Viaje breve sin necesidad de alimentación extraordinaria |

#### P7: Desarrollo Organizacional (Absorción SIGPER)

> **Origen:** Módulo Desarrollo Organizacional SIGPER. Gestión de competencias y evaluación 360°.

```mermaid
flowchart TD
    subgraph COMPETENCIAS["🎯 Gestión de Competencias"]
        C1["Definir modelo<br/>de competencias"]
        C2["Asociar competencias<br/>a cargos"]
        C3["Evaluar nivel<br/>funcionario"]
        C4["Calcular brecha<br/>competencial"]
    end
    
    subgraph DESARROLLO["📈 Plan de Desarrollo"]
        D1["Priorizar brechas<br/>críticas"]
        D2["Vincular a<br/>PAC-Capacitación"]
        D3["Ejecutar<br/>intervenciones"]
        D4["Medir avance<br/>competencial"]
    end
    
    subgraph EVALUACION["📊 Evaluación 360°"]
        E1["Autoevaluación"]
        E2["Evaluación jefatura"]
        E3["Evaluación pares"]
        E4["Consolidar<br/>resultado"]
    end
    
    C1 --> C2 --> C3 --> C4
    C4 --> D1 --> D2 --> D3 --> D4
    C3 --> E1 & E2 & E3 --> E4
```

---

### D07.B: Bienestar Funcionario

| Campo      | Valor                 |
| ---------- | --------------------- |
| ID         | `DOM-BIENESTAR`       |
| Criticidad | 🟡 Media               |
| Dueño      | Servicio de Bienestar |

#### Afiliación y Grupo Familiar

```mermaid
flowchart TD
    A["Funcionario solicita<br/>afiliación"] --> B["Verificar requisitos"]
    B --> C["Registrar socio"]
    C --> D["Configurar descuento<br/>automático"]
    D --> E["Alta en sistema<br/>bienestar"]
    
    E --> F["Gestionar grupo<br/>familiar"]
    F --> G["Registrar cargas"]
    G --> H["Validar documentos"]
```

#### Prestaciones y Bonificaciones

```mermaid
flowchart TD
    subgraph MEDICAS["🏥 Bonificaciones Médicas"]
        M1["Socio presenta<br/>boletas/bonos"]
        M2["Verificar tope anual"]
        M3["Calcular reembolso"]
        M4["Aprobar/Rechazar"]
        M5["Pagar bonificación"]
    end
    
    subgraph PRESTAMOS["💰 Préstamos"]
        P1["Solicitar préstamo"]
        P2["Evaluar capacidad<br/>de endeudamiento"]
        P3["Aprobar préstamo"]
        P4["Desembolsar"]
        P5["Descuento cuotas<br/>en liquidación"]
    end
    
    M1 --> M2 --> M3 --> M4 --> M5
    P1 --> P2 --> P3 --> P4 --> P5
```

#### Seguridad y Salud Ocupacional

```mermaid
flowchart LR
    A["Accidente<br/>laboral"] --> B["DIAT"]
    B --> C["Derivar a<br/>Mutual"]
    C --> D["Seguimiento<br/>tratamiento"]
    D --> E["Reintegro"]
    
    F["CPHS"] --> G["Investigación"]
    G --> H["Medidas<br/>preventivas"]
```

---

### D08: Contabilidad Operativa

| Campo      | Valor           |
| ---------- | --------------- |
| ID         | `DOM-CONTAB-OP` |
| Criticidad | 🔴 Crítica       |
| Dueño      | DAF             |

#### Mapa de Procesos D08

```mermaid
flowchart TB
    subgraph TESORO["💰 Tesorería (D08)"]
        T1["P1: Gestión de Caja"]
        T2["P2: Conciliación Bancaria"]
        T3["P3: Contabilización Operativa"]
        T4["P4: Cierre Contable Anual"]
        T5["P5: Deuda Flotante"]
    end
    
    T1 --> T2
    T2 --> T3
    T3 --> T4
    T4 --> T5
```

#### P1: Gestión de Caja Institucional

```mermaid
flowchart TD
    A["Inicio día hábil"] --> B["Revisar saldos bancarios"]
    B --> C{"¿Fondos suficientes?"}
    C -->|"Sí"| D["Programar pagos del día"]
    C -->|"No"| E["Gestionar aporte fiscal<br/>con DIPRES"]
    D --> F["Ejecutar pagos (TEF)"]
    F --> G["Registrar en SIGFE"]
    G --> H["Actualizar libro de caja"]
```

#### P2: Conciliación Bancaria

```mermaid
flowchart TD
    A["Obtener cartola<br/>bancaria"] --> B["Descargar movimientos<br/>SIGFE"]
    B --> C["Comparar registros"]
    C --> D{"¿Diferencias?"}
    D -->|"No"| E["Cuadrar período"]
    D -->|"Sí"| F["Identificar<br/>partidas pendientes"]
    F --> G{"Tipo de<br/>diferencia"}
    G -->|"Timing"| H["Documentar<br/>y esperar"]
    G -->|"Error"| I["Regularizar<br/>asiento"]
    G -->|"Fraude/Anomalía"| J["Escalar a<br/>Auditoría"]
    E & H & I --> K["Firmar conciliación<br/>mensual"]
```

#### P3: Contabilización Operativa

```mermaid
flowchart TD
    subgraph INGRESOS["📥 Ingresos"]
        I1["Aporte fiscal recibido"]
        I2["Ingresos propios"]
        I3["Recuperaciones"]
    end
    
    subgraph GASTOS["📤 Gastos"]
        G1["Remuneraciones"]
        G2["Bienes y servicios"]
        G3["Transferencias"]
    end
    
    subgraph CONTAB["📊 Contabilización"]
        C1["Verificar documentación"]
        C2["Clasificar según<br/>clasificador DIPRES"]
        C3["Registrar en SIGFE"]
        C4["Generar comprobante"]
    end
    
    I1 & I2 & I3 --> C1
    G1 & G2 & G3 --> C1
    C1 --> C2 --> C3 --> C4
```

#### P4: Cierre Contable Anual

```mermaid
flowchart TD
    A["Noviembre: Alerta<br/>de cierre"] --> B["Corte de compromisos<br/>(fecha límite)"]
    B --> C["Calcular devengos<br/>pendientes"]
    C --> D["Generar deuda<br/>flotante"]
    D --> E["Ajustes contables<br/>de cierre"]
    E --> F["Balance de<br/>comprobación"]
    F --> G["Estados financieros<br/>anuales"]
    G --> H["Remitir a CGR"]
    H --> I["Generar Saldo<br/>Inicial de Caja (SIC)"]
```

#### P5: Gestión de Deuda Flotante (Subt. 34)

```mermaid
flowchart TD
    A["31 Diciembre:<br/>Cierre ejercicio"] --> B["Identificar compromisos<br/>devengados no pagados"]
    B --> C["Calcular monto<br/>total deuda flotante"]
    C --> D{"¿SIC >= <br/>Deuda flotante?"}
    D -->|"Sí"| E["Financiar 100%<br/>con SIC"]
    D -->|"No"| F["Usar SIC + solicitar<br/>mayor aporte fiscal"]
    E --> G["Tramitar Resolución<br/>GORE"]
    F --> H["Tramitar Resolución<br/>+ Decreto DIPRES"]
    G & H --> I["Crear asignación<br/>Ítem 34.07"]
    I --> J["Priorizar pagos<br/>enero/febrero"]
```

#### P6: Fondos Globales Menores (Caja Chica)

| Atributo           | Valor                  | Norma GORE            |
| ------------------ | ---------------------- | --------------------- |
| Monto Máximo Fondo | 15 UTM                 | PR-DAF-0080           |
| Límite Gasto Único | 3 UTM                  | Res. Exenta           |
| Plazo Rendición    | 10 a 15 días hábiles   | Procedimiento Interno |
| Clasificación      | ST.22 Item 12 Asig 002 | Gastos Menores        |

```mermaid
flowchart LR
    A["Solicitud<br/>Fondo"] --\u003e B["Cheque bancario/<br/>Efectivo"]
    B --\u003e C["Gasto (Boleta/<br/>Factura)"]
    C --\u003e D["Rendición a<br/>Finanzas"]
    D --\u003e E["Reposición<br/>Fondo"]
```


---

### Catálogo por Proceso (Historias de Usuario)

#### D04: Compras

| ID              | Título                 | Prioridad | Actor               |
| --------------- | ---------------------- | --------- | ------------------- |
| US-BACK-ABS-001 | Plan Anual de Compras  | Alta      | Enc. Abastecimiento |
| US-BACK-ABS-002 | Tramitar solicitudes   | Alta      | Enc. Abastecimiento |
| US-BACK-ABS-003 | Publicar licitaciones  | Crítica   | Enc. Abastecimiento |
| US-BACK-ABS-004 | Evaluar ofertas        | Crítica   | Enc. Abastecimiento |
| US-BACK-ABS-005 | Emitir Orden de Compra | Crítica   | Enc. Abastecimiento |
| US-BACK-ABS-006 | Gestionar contratos    | Alta      | Enc. Abastecimiento |

#### D05: Inventarios y Activo Fijo

| ID              | Título                      | Prioridad | Actor            |
| --------------- | --------------------------- | --------- | ---------------- |
| US-BACK-BOD-001 | Registrar ingresos a bodega | Crítica   | Enc. Bodega      |
| US-BACK-BOD-002 | Despachar solicitudes       | Crítica   | Enc. Bodega      |
| US-BACK-BOD-003 | Inventario físico           | Alta      | Enc. Bodega      |
| US-BACK-AF-001  | Alta activo fijo            | Crítica   | Enc. Activo Fijo |
| US-BACK-AF-002  | Traslado de bienes          | Alta      | Enc. Activo Fijo |
| US-BACK-AF-003  | Baja de bienes              | Alta      | Enc. Activo Fijo |
| US-BACK-AF-004  | Inventario anual AF         | Alta      | Enc. Activo Fijo |

#### D06: Flota

| ID              | Título                     | Prioridad | Actor                |
| --------------- | -------------------------- | --------- | -------------------- |
| US-BACK-FLO-001 | Órdenes trabajo mantención | Alta      | Enc. Serv. Generales |
| US-BACK-FLO-002 | Solicitudes de vehículos   | Alta      | Enc. Flota           |
| US-BACK-FLO-003 | Control km/combustible     | Alta      | Enc. Flota           |

#### D07: Personas

| ID              | Título                       | Prioridad | Actor              |
| --------------- | ---------------------------- | --------- | ------------------ |
| US-BACK-PER-001 | Visualizar ficha funcionario | Crítica   | Funcionario        |
| US-BACK-PER-003 | Solicitar feriado/permiso    | Crítica   | Funcionario        |
| US-BACK-PER-004 | Declarar licencia médica     | Crítica   | Funcionario        |
| US-BACK-PER-006 | Visualizar liquidación       | Crítica   | Funcionario        |
| US-BACK-PER-010 | Calcular liquidaciones       | Crítica   | Gestor Personas    |
| US-BACK-PER-011 | Generar planilla Previred    | Crítica   | Gestor Personas    |
| US-BACK-PER-016 | Registrar precalificación    | Crítica   | Junta Calificadora |
| US-BACK-PER-017 | Consolidar calificaciones    | Crítica   | Junta Calificadora |

#### D07: Absorción SIGPER (Gestión de Personas Extendida)

> **Origen:** Análisis Gap Analysis SIGPER vs GORE_OS (Dic 2025). Funcionalidades necesarias para evitar adquisición de solución comercial Browse.

| ID              | Título                                 | Prioridad | Actor           | Módulo SIGPER Equivalente |
| --------------- | -------------------------------------- | --------- | --------------- | ------------------------- |
| US-BACK-PER-020 | Integrar reloj biométrico              | Alta      | Admin GDP       | Control Asistencia        |
| US-BACK-PER-021 | Gestionar competencias funcionarias    | Alta      | Gestor Personas | Desarrollo Organizacional |
| US-BACK-PER-022 | Administrar planta y dotación          | Crítica   | Gestor Personas | Planta                    |
| US-BACK-PER-023 | Gestionar grupo familiar               | Alta      | Funcionario     | Personal                  |
| US-BACK-PER-024 | Tramitar nombramiento/contrato         | Crítica   | Gestor Personas | Adm. Documentos           |
| US-BACK-PER-025 | Registrar haberes y descuentos esp.    | Crítica   | Gestor Personas | Haberes y Descuentos      |
| US-BACK-PER-026 | Calcular subsidio incapacidad laboral  | Alta      | Gestor Personas | Licencias Médicas         |
| US-BACK-PER-027 | Registrar accidente del trabajo (DIAT) | Crítica   | Prof. Bienestar | Accidentes del Trabajo    |
| US-BACK-PER-028 | Gestionar cuenta corriente permisos    | Crítica   | Gestor Personas | Feriados y Permisos       |
| US-BACK-PER-029 | Administrar PAC-Capacitación           | Alta      | Enc. Capacit.   | Capacitación              |
| US-BACK-PER-030 | Tramitar viáticos nacionales/extranj.  | Crítica   | Gestor Personas | Viáticos                  |
| US-BACK-PER-031 | Calcular retroactivos de remuneración  | Alta      | Gestor Personas | Remuneraciones            |
| US-BACK-PER-032 | Registrar retención judicial           | Alta      | Gestor Personas | Retenciones Judiciales    |
| US-BACK-PER-033 | Procesar marcaciones teletrabajo       | Alta      | Funcionario     | Control Asistencia        |
| US-BACK-PER-034 | Generar centralización contable RRHH   | Crítica   | Contador        | Centralización Contable   |
| US-BACK-PER-035 | Emitir libro de remuneraciones         | Alta      | Gestor Personas | Reporte Remuneraciones    |
| US-BACK-PER-036 | Procesar operación renta anual         | Crítica   | Gestor Personas | Operación Renta           |
| US-BACK-PER-037 | Calcular finiquito e indemnizaciones   | Crítica   | Gestor Personas | Finiquito                 |
| US-BACK-PER-038 | Portal autoservicio funcionario        | Crítica   | Funcionario     | Persomático               |
| US-BACK-PER-039 | Generar carga Transparencia Activa     | Crítica   | Gestor Personas | Transparencia             |
| US-BACK-PER-040 | Gestionar asignación carga familiar    | Alta      | Gestor Personas | Asig. Carga Familiar      |
| US-BACK-PER-041 | Procesar pago cotizaciones Previred    | Crítica   | Tesorero        | Pago Cotizaciones         |
| US-BACK-PER-042 | Administrar dependencia funcional      | Alta      | Gestor Personas | Dependencia Funcional     |
| US-BACK-PER-043 | Gestionar plantillas documentos RRHH   | Media     | Gestor Personas | Plantillas                |
| US-BACK-PER-044 | Poblar datos masivos funcionarios      | Media     | Admin GDP       | Poblamiento               |
| US-BACK-PER-045 | Integrar SIAPER vía API                | Crítica   | Sistema         | Servicios Integración     |
| US-BACK-PER-046 | Consultar auditoría transacciones RRHH | Alta      | Auditor         | Auditoría                 |
| US-BACK-PER-047 | Configurar seguridad jurisdiccional    | Crítica   | Admin GDP       | Seguridad                 |

#### Bienestar (D07)

| ID               | Título                        | Prioridad | Actor           |
| ---------------- | ----------------------------- | --------- | --------------- |
| US-BACK-BIEN-008 | Coordinar con Mutual          | Crítica   | Prof. Bienestar |
| US-BACK-BIEN-003 | Gestionar bonificación médica | Alta      | Prof. Bienestar |
| US-BACK-BIEN-005 | Evaluar préstamos             | Alta      | Prof. Bienestar |

#### Bienestar: Absorción SIGPER

| ID               | Título                              | Prioridad | Actor           | Módulo SIGPER Equivalente |
| ---------------- | ----------------------------------- | --------- | --------------- | ------------------------- |
| US-BACK-BIEN-013 | Afiliar socio y grupo familiar      | Crítica   | Prof. Bienestar | Bienestar                 |
| US-BACK-BIEN-014 | Administrar topes bonificación      | Alta      | Prof. Bienestar | Bienestar                 |
| US-BACK-BIEN-015 | Gestionar convenios institucionales | Alta      | Prof. Bienestar | Bienestar                 |
| US-BACK-BIEN-016 | Registrar sala cuna/jardín infantil | Alta      | Prof. Bienestar | Personal (Sala Cuna)      |

#### Contabilidad Operativa (D08)

| ID              | Título                               | Prioridad | Actor    |
| --------------- | ------------------------------------ | --------- | -------- |
| US-BACK-TES-001 | Consultar saldos bancarios           | Crítica   | Tesorero |
| US-BACK-TES-002 | Programar pagos diarios              | Crítica   | Tesorero |
| US-BACK-TES-006 | Importar cartolas bancarias          | Crítica   | Contador |
| US-BACK-TES-007 | Conciliar movimientos SIGFE vs banco | Crítica   | Contador |
| US-BACK-TES-010 | Registrar ingresos propios           | Crítica   | Contador |
| US-BACK-TES-011 | Contabilizar gastos operativos       | Crítica   | Contador |
| US-BACK-TES-014 | Ejecutar corte de compromisos        | Crítica   | Jefe DAF |
| US-BACK-TES-015 | Calcular devengos pendientes         | Crítica   | Contador |
| US-BACK-TES-018 | Identificar deuda flotante           | Crítica   | Contador |
| US-BACK-TES-019 | Emitir certificado deuda flotante    | Crítica   | Contador |

*Ver catálogo completo en [kb_goreos_us_d-back.yml](../user-stories/kb_goreos_us_d-back.yml)*

---

## 🔗 Matriz de Trazabilidad (Historias de Usuario)

| Proceso BPMN            | Subproceso    | Historias de Usuario   |
| ----------------------- | ------------- | ---------------------- |
| D04 P1: PAC             | Consolidación | US-BACK-ABS-001        |
| D04 P2: Licitación      | Publicación   | US-BACK-ABS-003        |
| D04 P2: Licitación      | Evaluación    | US-BACK-ABS-004        |
| D04 P3: OC              | Emisión       | US-BACK-ABS-005        |
| D04 P4: Contratos       | Gestión       | US-BACK-ABS-006        |
| D05 P1: Bodegas         | Recepción     | US-BACK-BOD-001        |
| D05 P1: Bodegas         | Despacho      | US-BACK-BOD-002        |
| D05 P2: AF              | Alta          | US-BACK-AF-001         |
| D05 P2: AF              | Baja          | US-BACK-AF-003         |
| D06: Flota              | Asignación    | US-BACK-FLO-002        |
| D06: Flota              | Control       | US-BACK-FLO-003        |
| D07 P1: Ingreso         | Selección     | US-BACK-PER-015        |
| D07 P2: Remuneraciones  | Liquidación   | US-BACK-PER-010, 011   |
| D07 P2: Remuneraciones  | Tiempo        | US-BACK-PER-003, 004   |
| D07 P3: Capacitación    | Calificación  | US-BACK-PER-016, 017   |
| D07 Bienestar           | Prestaciones  | US-BACK-BIEN-001 a 012 |
| D08 P1: Caja            | Saldos/Pagos  | US-BACK-TES-001 a 005  |
| D08 P2: Conciliación    | Bancaria      | US-BACK-TES-006 a 009  |
| D08 P3: Contabilización | Devengos      | US-BACK-TES-010 a 013  |
| D08 P4: Cierre          | Anual         | US-BACK-TES-014 a 017  |
| D08 P5: Deuda Flotante  | Ítem 34.07    | US-BACK-TES-018 a 021  |

---

## Roles y Actores

| Rol                 | Descripción                      | Módulo            | US Principales   |
| ------------------- | -------------------------------- | ----------------- | ---------------- |
| Funcionario         | Empleado del GORE (autoservicio) | Personas          | PER-001 a 007    |
| Gestor Personas     | Profesional RRHH/Remuneraciones  | Personas          | PER-008 a 015    |
| Junta Calificadora  | Órgano evaluador anual           | Personas          | PER-016 a 018    |
| Enc. Abastecimiento | Jefe/Profesional Compras         | Abastecimiento    | ABS-001 a 006    |
| Enc. Bodega         | Responsable almacén/stock        | Inventarios       | BOD-001 a 003    |
| Enc. Activo Fijo    | Gestor patrimonio institucional  | Activo Fijo       | AF-001 a 004     |
| Enc. Flota          | Gestor vehículos institucionales | Flota             | FLO-001 a 003    |
| Prof. Bienestar     | Profesional Servicio Bienestar   | Bienestar         | BIEN-001 a 009   |
| Socio Bienestar     | Funcionario afiliado al servicio | Bienestar         | BIEN-010 a 012   |
| Tesorero            | Responsable pagos y caja         | Contab. Operativa | TES-001 a 005    |
| Contador            | Profesional contable DAF         | Contab. Operativa | TES-006 a 017    |
| Jefe DAF            | Director Admin. y Finanzas       | Contab. Operativa | TES-014, TES-020 |
| Enc. Capacitación   | Profesional desarrollo personas  | Competencias      | COMP-001 a 003   |

---

## Integración D-BACK ↔ D-FIN

```mermaid
flowchart TB
    subgraph D_BACK["🏛️ D-BACK: Gestión Recursos Institucionales"]
        direction TB
        OC["📄 Orden de Compra"]
        PAG["💳 Pagos TEF"]
        LIQ["📋 Liquidaciones"]
        DEV["📊 Devengos"]
        DF["⏳ Deuda Flotante"]
    end
    
    subgraph D_FIN["💰 D-FIN: Gestión Financiera"]
        direction TB
        CDP["🔒 CDP"]
        COMP["📌 Compromiso"]
        PPTO["📈 Presupuesto"]
        SIGFE["🏦 SIGFE"]
    end
    
    OC -->|"1. Requiere"| CDP
    CDP -->|"2. Genera"| COMP
    OC -->|"3. Afecta"| COMP
    COMP -->|"4. Consume"| PPTO
    
    DEV -->|"5. Registra en"| SIGFE
    PAG -->|"6. Actualiza"| SIGFE
    LIQ -->|"7. Contabiliza"| SIGFE
    
    DF -->|"8. Ítem 34.07"| PPTO
    
    style D_BACK fill:#e8f5e9,stroke:#2e7d32
    style D_FIN fill:#fff3e0,stroke:#ef6c00
```

Flujos Principales:

| #   | Flujo                          | Origen        | Destino     | Descripción                                        |
| --- | ------------------------------ | ------------- | ----------- | -------------------------------------------------- |
| 1   | CDP Requerido                  | OC            | CDP         | Toda compra requiere certificado de disponibilidad |
| 2   | Generación Compromiso          | CDP           | Compromiso  | CDP aprobado genera compromiso presupuestario      |
| 3   | Afectación Compromiso          | OC            | Compromiso  | OC emitida afecta el compromiso                    |
| 4   | Consumo Presupuesto            | Compromiso    | Presupuesto | Compromiso consume asignación                      |
| 5   | Registro Devengos              | Devengos      | SIGFE       | Obligaciones exigibles se contabilizan             |
| 6   | Actualización Pagos            | Pagos TEF     | SIGFE       | Transferencias actualizan el pagado                |
| 7   | Contabilización Remuneraciones | Liquidaciones | SIGFE       | Planilla mensual genera asientos                   |
| 8   | Deuda Flotante                 | DF            | Presupuesto | Se incorpora al presupuesto siguiente              |

---

## Entidades de Datos

### Personas

| Entidad                 | Atributos Clave                                                           | Relaciones                                   |
| ----------------------- | ------------------------------------------------------------------------- | -------------------------------------------- |
| `Funcionario`           | id, rut, nombre, cargo, grado_eus, division_id, fecha_ingreso, estado     | → ContratoLaboral, Liquidacion[], Licencia[] |
| `DeclaracionPatrimonio` | id, funcionario_id, fecha_presentacion, periodo, estado                   | → Funcionario                                |
| `ContratoLaboral`       | id, funcionario_id, tipo, fecha_inicio, fecha_termino                     | → Funcionario                                |
| `Liquidacion`           | id, funcionario_id, periodo, bruto, descuentos, liquido                   | → Funcionario                                |
| `Licencia`              | id, funcionario_id, tipo, dias, fecha_inicio, estado, subsidio_recuperado | → Funcionario                                |

### Abastecimiento

| Entidad               | Atributos Clave                                              | Relaciones              |
| --------------------- | ------------------------------------------------------------ | ----------------------- |
| `OrdenCompra`         | id, numero_mp, proveedor_id, monto, estado, fecha            | → Proveedor, ItemOC[]   |
| `Licitacion`          | id, numero_mp, tipo, estado, fecha_publicacion, fecha_cierre | → OrdenCompra           |
| `ContratoAdquisicion` | id, licitacion_id, proveedor_id, monto, vigencia             | → Licitacion, Proveedor |
| `GarantiaContrato`    | id, contrato_id, tipo, monto, vencimiento, estado custody    | → ContratoAdquisicion   |

### Inventarios

| Entidad          | Atributos Clave                                                     | Relaciones                  |
| ---------------- | ------------------------------------------------------------------- | --------------------------- |
| `ItemInventario` | id, codigo, descripcion, unidad, stock, ubicacion, valor_unitario   | → MovimientoStock[]         |
| `ActivoFijo`     | id, codigo, descripcion, valor_compra, vida_util, depreciacion_acum | → Funcionario (responsable) |
| `Vehiculo`       | id, patente, modelo, año, km_actual, estado                         | → Bitacora[], Mantencion[]  |

### Contabilidad Operativa

| Entidad                | Atributos Clave                                          | Relaciones                   |
| ---------------------- | -------------------------------------------------------- | ---------------------------- |
| `CuentaBancaria`       | id, banco, numero, tipo, saldo_actual, activa            | → MovimientoBanco[]          |
| `MovimientoBanco`      | id, cuenta_id, fecha, monto, tipo, concepto, conciliado  | → CuentaBancaria             |
| `ConciliacionBancaria` | id, cuenta_id, periodo, saldo_libro, saldo_banco, estado | → CuentaBancaria, Partidas[] |
| `DeudaFlotante`        | id, ejercicio, acreedor, monto, subtitulo, fecha_devengo | → Compromiso (D-FIN)         |
| `CierreContable`       | id, ejercicio, tipo, fecha_corte, sic_calculado, estado  | → DeudaFlotante[]            |

### Control de Asistencia (Absorción SIGPER)

| Entidad             | Atributos Clave                                                                              | Relaciones      |
| ------------------- | -------------------------------------------------------------------------------------------- | --------------- |
| `Marcacion`         | id, funcionario_id, fecha, hora, tipo (ENTRADA/SALIDA), fuente (RELOJ/WEB/MOVIL), valida     | → Funcionario   |
| `CodigoHorario`     | id, nombre, hora_entrada, hora_salida, tolerancia_min, dias_semana[], incluye_teletrabajo    | → Funcionario[] |
| `ProcesoAsistencia` | id, periodo, fecha_proceso, total_funcionarios, con_novedades, estado                        | → Marcacion[]   |
| `NovedadAsistencia` | id, funcionario_id, fecha, tipo (ATRASO/SALIDA_ANT/FALTA/EXTRA), minutos, justificada        | → Funcionario   |
| `LibroAsistencia`   | id, periodo, funcionario_id, dias_trabajados, horas_normales, horas_extra_25, horas_extra_50 | → Funcionario   |

### Viáticos (Absorción SIGPER)

| Entidad               | Atributos Clave                                                                          | Relaciones    |
| --------------------- | ---------------------------------------------------------------------------------------- | ------------- |
| `Viatico`             | id, funcionario_id, tipo (NACIONAL/EXTRANJERO), fecha_inicio, fecha_fin, destino, estado | → Funcionario |
| `DetalleViatico`      | id, viatico_id, fecha, porcentaje (100/60/50/40/20/10), monto_calculado                  | → Viatico     |
| `ConglomeradoViatico` | id, region_id, nombre, localidades[], aplica_100                                         | -             |
| `FactorPais`          | id, pais, costo_vida, vigencia_desde                                                     | -             |
| `TablaGradoViatico`   | id, grado_eus, monto_diario_nacional, monto_diario_extranjero_base                       | -             |

### Desarrollo Organizacional (Absorción SIGPER)

| Entidad                 | Atributos Clave                                                             | Relaciones                 |
| ----------------------- | --------------------------------------------------------------------------- | -------------------------- |
| `Competencia`           | id, codigo, nombre, tipo (TECNICA/TRANSVERSAL), descripcion, niveles[]      | → CompetenciaCargo[]       |
| `CompetenciaCargo`      | id, cargo_id, competencia_id, nivel_esperado                                | → Cargo, Competencia       |
| `EvaluacionCompetencia` | id, funcionario_id, competencia_id, evaluador_id, nivel_observado, fecha    | → Funcionario, Competencia |
| `BrechaCompetencial`    | id, funcionario_id, competencia_id, nivel_esperado, nivel_actual, prioridad | → Funcionario, Competencia |
| `PlanDesarrollo`        | id, funcionario_id, periodo, brechas[], acciones_formativas[], estado       | → Funcionario, PAC         |

### Grupo Familiar y Cargas (Absorción SIGPER)

| Entidad             | Atributos Clave                                                                           | Relaciones      |
| ------------------- | ----------------------------------------------------------------------------------------- | --------------- |
| `GrupoFamiliar`     | id, funcionario_id, parentesco, nombre, rut, fecha_nacimiento, es_carga, estado           | → Funcionario   |
| `AsignacionCarga`   | id, funcionario_id, tramo, monto, vigencia_desde, vigencia_hasta                          | → Funcionario   |
| `RetencionJudicial` | id, funcionario_id, beneficiario_id, monto_fijo, porcentaje, tipo_reajuste, banco, cuenta | → GrupoFamiliar |

### Haberes y Descuentos Especiales (Absorción SIGPER)

| Entidad               | Atributos Clave                                                                 | Relaciones    |
| --------------------- | ------------------------------------------------------------------------------- | ------------- |
| `HaberDescuentoEsp`   | id, codigo, nombre, tipo (HABER/DESCUENTO), formula_id, imponible, tributable   | -             |
| `AsignacionHaberDesc` | id, funcionario_id, haber_descuento_id, fecha_inicio, fecha_termino, monto_fijo | → Funcionario |
| `Bienio`              | id, funcionario_id, fecha_reconocimiento, cantidad, monto                       | → Funcionario |

---

## Sistemas Involucrados

| Sistema           | Función                           | Módulo SIGPER Equivalente |
| ----------------- | --------------------------------- | ------------------------- |
| `SYS-SIAPER`      | Control personal Estado           | Servicios Integración     |
| `SYS-PREVIRED`    | Cotizaciones previsionales        | Pago Cotizaciones         |
| `ORG-CHILECOMPRA` | Mercado Público, licitaciones, OC | -                         |
| `SYS-SIGFE`       | Contabilización                   | Centralización Contable   |
| `SYS-IMED`        | Licencias médicas electrónicas    | Licencias Médicas         |
| `SYS-SUSESO`      | Accidentes trabajo / DIAT         | Accidentes del Trabajo    |
| `SYS-SII`         | Operación renta, F1887/F1879      | Operación Renta           |
| `HW-BIOMETRICO`   | Relojes ZK/Anviz/HikVision        | Control Asistencia        |

---

## Normativa Aplicable

| Norma            | Alcance                            |
| ---------------- | ---------------------------------- |
| Ley 18.834       | Estatuto Administrativo            |
| Ley 19.886       | Compras públicas                   |
| D.S. 250         | Reglamento Ley 19.886              |
| D.L. 799         | Uso vehículos fiscales             |
| D.L. 1.263       | Ley Org. Administración Financiera |
| Res. CGR 30/2015 | Normas sobre rendición de cuentas  |
| NICSP 17, 21, 31 | Activo fijo, depreciación          |
| Ley 18.575       | Bases Administración Estado        |

---

## Referencias Cruzadas

| Dominio   | Relación                                       | Entidades Compartidas      |
| --------- | ---------------------------------------------- | -------------------------- |
| D-FIN     | % Ejecución como KPI, distribución estratégica | CDP, AsignacionPpto        |
| D-EJEC    | EP validado → Devengo → Pago                   | EstadoPago, Hito           |
| D-NORM    | Resoluciones de adjudicación, contratos        | ActoAdministrativo         |
| D-TDE     | Interoperabilidad SIGFE, Mercado Público       | IntegracionPISEE           |
| D-GOB     | Proveedores como actores                       | Actor                      |
| D-SEG     | Equipamiento CIES, vehículos seguridad         | Vehiculo, ActivoFijo       |
| D-TERR    | Geolocalización bienes fiscales, flota         | Ubicacion, CapaGeoespacial |
| D-EVOL    | Orquestación de capacidades IA sobre recursos  | Inventory                  |
| D-GESTION | Métricas back-office para scoring H_gore       | MetricaGestion             |
| FÉNIX     | Protocolo de intervención por criticidad       | Intervencion               |
| D-PLAN    | Alineación de compras con Plan Operativo       | PlanOperativo              |


---

## Indicadores de Gestión (KPIs)

| KPI                          | Meta      | Fórmula                                            | Módulo              |
| ---------------------------- | --------- | -------------------------------------------------- | ------------------- |
| % Conciliaciones al día      | 100%      | (Conciliaciones completadas / Total cuentas) × 100 | Contabilidad Op.    |
| Mora pago proveedores        | < 30 días | Promedio días desde factura hasta pago             | Contabilidad Op.    |
| Cobertura PAC                | > 90%     | (Compras ejecutadas / PAC planificado) × 100       | Abastecimiento      |
| Rotación inventario          | > 4x/año  | (Salidas anuales / Stock promedio)                 | Inventarios         |
| % Activos inventariados      | 100%      | (AF verificados / Total AF registrados) × 100      | Activo Fijo         |
| Disponibilidad flota         | > 85%     | (Vehículos operativos / Total flota) × 100         | Flota               |
| Mora rendiciones bienestar   | < 15 días | Promedio días hasta reembolso                      | Bienestar           |
| Dotación efectiva            | 95-100%   | (Dotación actual / Dotación autorizada) × 100      | Gestión de Personas |
| % Marcaciones válidas        | > 98%     | (Marcaciones OK / Total marcaciones) × 100         | Control Asistencia  |
| Brecha competencial media    | < 1 nivel | Promedio (nivel_esperado - nivel_actual)           | Desarrollo Org.     |
| Viáticos tramitados a tiempo | > 95%     | (Viáticos pagados en plazo / Total viáticos) × 100 | Viáticos            |

---

## Registro de Cambios (Changelog)

| Versión | Fecha      | Cambios                                                                                                                               |
| ------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| 6.0     | 2025-12-18 | **Absorción SIGPER.** +28 US (PER-020 a 047, BIEN-013 a 016). +3 procesos BPMN (P5-P7). +18 entidades. Cobertura 100% módulos SIGPER. |
| 5.2     | 2025-12-16 | Añadido D07.B Bienestar (+3 procesos BPMN). Tabla índice BPMN. US completas D05/D06                                                   |
| 5.1     | 2025-12-16 | Renombre módulo Tesorería → Contabilidad Operativa. +6 términos glosario                                                              |
| 5.1     | 2025-12-16 | +5 entidades datos Contab. Operativa. +8 KPIs. +13 roles documentados                                                                 |
| 5.1     | 2025-12-16 | Diagrama integración D-BACK ↔ D-FIN. Normativa ampliada (D.L. 1.263)                                                                  |
| 5.0     | 2025-12-15 | Añadido módulo Tesorería (21 US nuevas). Migración US-BACK-CONT a Tesorería                                                           |
| 4.0     | 2025-12-10 | Versión inicial consolidada. 7 módulos, 49 US                                                                                         |

---

*Documento parte de GORE_OS Blueprint Integral v5.4*  
*Última actualización: 2025-12-18*
