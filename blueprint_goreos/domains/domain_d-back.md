# D-BACK: Dominio de Gestión de Recursos Institucionales

> **Parte de:** [GORE_OS Vision General](../vision_general.md)  
> **Capa:** Habilitante (Soporte Operativo)  
> **Función GORE:** ADMINISTRAR  

---

## Propósito

Gestionar integralmente los recursos institucionales —financieros, humanos y materiales— que habilitan el funcionamiento del GORE, brindando al funcionario una experiencia unificada para todos los procesos de administración de recursos.

---

## Áreas Funcionales

### 1. Gestión Financiera y Tesorería

- Contabilidad patrimonial integrada con SIGFE
- Tesorería: flujo de caja, conciliaciones bancarias automáticas
- Gestión de fondos por rendir y anticipos
- Pagos electrónicos obligatorios (Art. 8 Ley Presupuestos)
- Generación de archivos bancarios para transferencias masivas
- Reportes financieros consolidados y cierre mensual/anual

### 2. Gestión de Personas (RRHH)

**Ciclo de Vida del Funcionario:**
```
SELECCIÓN → INGRESO → DESARROLLO → MOVILIDAD → EGRESO
(Concurso)   (Decreto)  (Capacitac.)  (Ascensos)  (Finiquito)
(Perfil)     (Inducción) (Desempeño)  (Traslados) (Certific.)
```

**Submódulos:**
- **Dotación:** Planta, Contrata, Honorarios, Código Trabajo
- **Remuneraciones:** Escala EUS, asignaciones, descuentos, PREVIRED
- **Tiempo y Asistencia:** Control biométrico, permisos, licencias médicas
- **Desarrollo:** DNC, Plan Capacitación, Calificaciones, Clima Laboral
- **Bienestar:** Afiliación, beneficios, préstamos, convenios

**Integraciones:** SIAPER, SIGPER, PREVIRED, I-MED (licencias electrónicas)

### 3. Abastecimiento y Patrimonio

**Compras Públicas (Ley 19.886):**
- Plan Anual de Compras (PAC): planificación, priorización, publicación
- Mecanismos: Convenio Marco, Licitación Pública/Privada, Trato Directo
- Ciclo OC: Emisión → Aceptación → Recepción Conforme → Pago
- Contratos: Formalización, administrador, estados de pago, multas
- Garantías: Seriedad oferta, fiel cumplimiento, custodia y devolución

**Inventarios y Bodegas:**
- Catálogo maestro de artículos con codificación y atributos
- Gestión multi-bodega (Central, Economato, Aseo, Mantención, EPP)
- Ingresos/Egresos: Recepción OC, despacho, préstamos, ajustes
- Valorización: PPP/FIFO, cierre mensual, cuadratura contable
- Alertas: Stock mínimo, vencimientos, artículos sin movimiento

**Activo Fijo (NICSP 17/21/31):**
- Alta: Codificación, etiquetado (código barras/QR), fotografía
- Valorización: Costo adquisición, depreciación línea recta, vida útil
- Movimientos: Traslados, préstamos, comodatos, mantención mayor
- Baja: Obsolescencia, siniestro, remate, donación
- Inventario físico anual con conciliación y responsables

**Servicios Generales y Flota:**
- Mantención infraestructura: Preventiva, correctiva, órdenes de trabajo
- Contratos externalizados: Aseo, seguridad, jardines, ascensores
- Flota vehicular: Registro, conductores, solicitud/asignación
- Bitácora de uso, control combustible, kilometraje
- Indicadores: Disponibilidad, utilización, costo por kilómetro

**Integración:** Mercado Público (OC, adjudicaciones, proveedores)

---

## Entidades de Datos

### Gestión de Personas

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Funcionario` | id, rut, nombre, cargo, division, calidad_juridica, grado, fecha_ingreso | → Contrato[], Liquidacion[], Asistencia[], Capacitacion[] |
| `Contrato` | id, funcionario_id, tipo, grado, fecha_inicio, fecha_termino, decreto | → Funcionario |
| `Liquidacion` | id, funcionario_id, periodo, sueldo_base, asignaciones[], descuentos[], liquido | → Funcionario |
| `Asistencia` | id, funcionario_id, fecha, hora_entrada, hora_salida, tipo_marca | → Funcionario |
| `PermisoLicencia` | id, funcionario_id, tipo, fecha_inicio, fecha_fin, estado | → Funcionario |
| `Capacitacion` | id, funcionario_id, curso, fecha, horas, evaluacion, costo | → Funcionario |
| `Calificacion` | id, funcionario_id, periodo, nota, lista, junta_id | → Funcionario |
| `AfiliacionBienestar` | id, funcionario_id, fecha_afiliacion, aporte_mensual, estado | → Funcionario |

### Abastecimiento y Compras

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `PlanCompras` | id, año, estado, fecha_publicacion, monto_total | → ItemPAC[] |
| `ProcesoCompra` | id, numero, tipo, monto_estimado, estado, fecha_adjudicacion | → Proveedor (D-COORD), OrdenCompra[] |
| `OrdenCompra` | id, proceso_id, numero_oc, monto, estado, fecha_emision | → ProcesoCompra, ItemOC[] |
| `ContratoCompra` | id, proceso_id, administrador_id, monto, fecha_inicio, fecha_termino | → ProcesoCompra, EstadoPago[], Garantia[] |
| `Garantia` | id, contrato_id, tipo, monto, vencimiento, estado | → ContratoCompra |

### Inventarios y Activo Fijo

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Articulo` | id, codigo, nombre, familia, unidad_medida, cuenta_contable | → MovimientoInventario[] |
| `Bodega` | id, nombre, tipo, ubicacion, encargado_id | → MovimientoInventario[] |
| `MovimientoInventario` | id, articulo_id, bodega_id, tipo, cantidad, costo_unitario, fecha | → Articulo, Bodega |
| `ActivoFijo` | id, codigo, descripcion, tipo_bien, valor_adquisicion, valor_libro, vida_util_meses | → Depreciacion[], MovimientoActivo[] |
| `Depreciacion` | id, activo_id, periodo, monto_mensual, acumulada | → ActivoFijo |

### Flota Vehicular

| Entidad | Atributos Clave | Relaciones |
|---------|-----------------|------------|
| `Vehiculo` | id, patente, marca, modelo, año, activo_fijo_id, estado, km_actual | → ActivoFijo, BitacoraVehiculo[] |
| `Conductor` | id, funcionario_id, licencia_clase, licencia_vencimiento, autorizado | → Funcionario |
| `BitacoraVehiculo` | id, vehiculo_id, conductor_id, fecha_salida, fecha_retorno, km_inicial, km_final | → Vehiculo, Conductor |
| `CargaCombustible` | id, vehiculo_id, fecha, litros, monto, km_odometro | → Vehiculo |
| `OrdenTrabajoMant` | id, vehiculo_id, tipo, descripcion, fecha, costo, proveedor_id | → Vehiculo |

---

## Notas de Diseño

- La gestión documental, expediente electrónico y actos administrativos se gestionan en **D-NORM**
- La entidad `Proveedor` se define en **D-COORD**. Todas las compras, contratos y mantenciones referencian proveedores del directorio unificado

---

## Referencias Cruzadas

| Dominio | Relación |
|---------|----------|
| **D-NORM** | Gestión documental, expediente electrónico |
| **D-COORD** | Proveedor (directorio unificado) |
| **D-TDE** | Integraciones con sistemas estatales |

---

*Documento parte de GORE_OS v3.1*
