# Diccionario
---

## 1) Modelo relacional propuesto

### 1.1. Visión general (2 módulos)

**A. Gestión documental (RECIBIDOS, OFICIOS, MEMOS, RESOLUCIONES, CARTAS, *internos*)**
Objetivo: trazabilidad de documentos, canales, derivaciones y seguimiento.

**B. Rendiciones / subvenciones (RENDICIONES 2024, RENDICIONES FNDR Y ADNC)**
Objetivo: registro financiero-administrativo por iniciativa/código, institución, fechas y montos.

> Integración opcional: vincular una rendición a un documento del módulo documental (si se incorpora un identificador común o se agrega un “doc_id” en la hoja de rendiciones).

---

### 1.2. Esquema ER (núcleo recomendado)

#### Dimensiones (catálogos)

1. **doc_tipo_documento** (1) —— (N) **doc_documento**
2. **doc_canal** (1) —— (N) **doc_documento** (para recepción / despacho / distribución)
3. **org_division** (1) —— (N) **doc_derivacion**

#### Hechos / transacciones

4. **doc_documento** (1) —— (N) **doc_derivacion**
5. **doc_documento** (1) —— (N) **doc_evento** (seguimiento / respuesta / instrucción / hitos)

#### Rendiciones

6. **fin_programa** (1) —— (N) **fin_iniciativa**
7. **fin_institucion** (1) —— (N) **fin_rendicion**
8. **fin_iniciativa** (1) —— (N) **fin_rendicion**

#### Integración opcional

9. **doc_documento** (0..1) —— (0..N) **fin_rendicion** *(si agregan el vínculo)*

---

### 1.3. Llaves: enfoque realista con tus datos

En tus archivos hay **duplicidades en llaves “de negocio”**, por lo que el modelo debe usar **PK sustitutas**:

* En **RECIBIDOS**, `C` **no es único**: hay **30 correlativos duplicados** (p. ej. el mismo `C` usado en dos documentos distintos).
* En **OFICIOS**, `N° DCTO` casi único, pero hay al menos **1 duplicado**.
* En **RENDICIONES 2024**, `CORRELATIVO` repite (p. ej. **“s/n” aparece 7 veces**).

✅ Por eso: **PK técnica** (UUID/serial) + conservar los identificadores originales como “business keys” (con validaciones y reportes de duplicidad).

---

## 2) Diccionario de datos formal (propuesto)

A continuación va un diccionario **orientado a implementación SQL** (puede adaptarse a PostgreSQL/SQL Server/MySQL).

---

# MÓDULO A — Gestión documental

## Tabla: `doc_documento` (registro maestro)

**Propósito:** una fila por documento registrado (entrante/saliente/interno), sin perder el origen (hoja).

**PK**

* `documento_id` (UUID o BIGINT identity)

**Campos**

* `origen_hoja` (VARCHAR(40), NOT NULL)
  Valores: `RECIBIDOS`, `OFICIOS`, `MEMOS`, `RES_EXENTAS`, `RES_AFECTAS`, `CARTAS`, `OFICIOS_INTERNOS`, `MEMOS_INTERNOS`.
  Regla: controlado (catálogo interno).

* `correlativo_recibidos` (VARCHAR(20), NULL)
  **Fuente:** `RECIBIDOS.C`
  Regla: texto (no numérico). **No asumir unicidad.**

* `numero_documento` (VARCHAR(50), NULL)
  **Fuentes:** `NÚMERO DOCUMENTO` / `N° DCTO` / `NUMERO DOCUMENTO` / `NÚMERO DOCUMENTO` (internos)
  Regla: mantener ceros a la izquierda (ej. `01898`).
  Limpieza: trim; normalizar `S/N` como valor estándar.

* `folio` (VARCHAR(50), NULL)
  **Fuentes:** `FOLIO` (memos/resoluciones)
  Regla: **único por hoja** en MEMOS/RESOLUCIONES (en tus datos sí es único), pero no necesariamente global.

* `tipo_documento_id` (FK, NOT NULL)
  **Fuente:** `TIPO DE DOCUMENTO` / `TIPO DE DCTO`
  Regla: mapear variantes (ej. `RES EXE`, `RESOLUCION EXENTA` → `RESOLUCION_EXENTA`).

* `fecha_documento` (DATE, NULL)
  **Fuentes:** `FECHA DOCUMENTO`, `FECHA DCTO`, `FECHA DOCTO`
  Regla: formato final ISO.
  Validación sugerida: `fecha_recepcion >= fecha_documento` cuando aplique.

* `fecha_recepcion` (DATE, NULL)
  **Fuentes:** `FECHA RECEPCIÓN`

* `fecha_ingreso` (DATE, NULL)
  **Uso preferente:** rendiciones (si se integra) / o “ingreso a unidad”.

* `fecha_entrega` (DATE, NULL)
  **Fuentes:** `FECHA ENTREGA` / `FECHA DE ENTREGA`
  Validación sugerida: `fecha_entrega >= fecha_recepcion` cuando aplique.

* `remitente` (TEXT, NULL)
  **Fuente:** `REMITENTE`

* `destinatario` (TEXT, NULL)
  **Fuente:** `DESTINATARIO`

* `solicita` (TEXT, NULL)
  **Fuente:** `SOLICITA`
  Nota: en algunas hojas contiene iniciales/códigos (p.ej. “mel”, “vmi”), en otras nombres.

* `responsable` (TEXT, NULL)
  **Fuente:** `Responsable` (en RECIBIDOS) / `RESPONSABLE` (en MEMOS)

* `unidad_origen_raw` (TEXT, NULL)
  **Fuente:** `DE` (MEMOS) o `DIVISIÓN` (MEMOS INTERNOS)
  (Si se normaliza: FK a `org_division`)

* `dirigido_a` (TEXT, NULL)
  **Fuentes:** `PARA:` (MEMOS) / `DIRIGIDO A:` (MEMOS INTERNOS)

* `firma` (TEXT, NULL)
  **Fuentes:** `FIRMA` (varias hojas)

* `materia` (TEXT, NULL)
  **Fuente:** `MATERIA`

* `canal_recepcion_id` (FK, NULL)
  **Fuente:** `VIA RECEPCIÓN` (RECIBIDOS)

* `canal_despacho_id` (FK, NULL)
  **Fuentes:** `VÍA DESPACHO` (MEMOS), `DISTRIBUCIÓN` (OFICIOS/CARTAS)

* `canal_distribucion_id` (FK, NULL)
  **Fuente:** `VIA DISTRIBUCIÓN` (RECIBIDOS)
  Nota de calidad: en tus datos este campo mezcla canales con unidades/personas (“DIPIR”, “DAF”, “PABLO SAN MARTIN”); por eso conviene **separar canal vs destinatario interno**.

* `adjunto_descripcion` (TEXT, NULL)
  **Fuente:** `ADJUNTO` (RECIBIDOS)
  Regla: mantener literal + derivar boolean.

* `tiene_adjunto` (BOOLEAN, NOT NULL, default false)
  Derivación: `adjunto_descripcion` no nulo y distinto de `S/I` / `SIN ADJUNTO`.

* `link_documento_url` (TEXT, NULL)
  **Fuente:** `LINK AL DOCUMENTO`
  Validación: URL; idealmente drive.google.com (en tus datos casi siempre es Drive).

* `observaciones` (TEXT, NULL)
  **Fuente:** `OBSERVACIONES` / `Observación`
  Nota: en varias hojas se usa como canal (`DOC DIGITAL`, `EMAIL`) y como comentarios; recomendable separar.

**Índices sugeridos**

* `idx_doc_origen_numero`: (`origen_hoja`, `numero_documento`)
* `idx_doc_folio`: (`origen_hoja`, `folio`)
* `idx_doc_fechas`: (`fecha_recepcion`, `fecha_documento`)

---

## Tabla: `doc_tipo_documento` (catálogo)

**PK**

* `tipo_documento_id` (SMALLINT/INT)

**Campos**

* `codigo` (VARCHAR(40), UNIQUE, NOT NULL) Ej: `OFICIO`, `ORDINARIO`, `CARTA`, `MEMO`, `RESOLUCION_EXENTA`, `RESOLUCION_AFECTA`, `RENDICION`, `INVITACION`, etc.
* `nombre` (VARCHAR(100), NOT NULL)
* `activo` (BOOLEAN, NOT NULL)

**Reglas de mapeo recomendadas**

* `RES EXE`, `RESOLUCION EXENTA` → `RESOLUCION_EXENTA`
* `RES AFE`, `RESOLUCION AFECTA` → `RESOLUCION_AFECTA`
* `INVITACION`, `INVITACIÓN` → `INVITACION`
* `CORREO ELECTRONICO` → `CORREO_ELECTRONICO`

---

## Tabla: `doc_canal` (catálogo de canales)

**PK**

* `canal_id` (SMALLINT/INT)

**Campos**

* `codigo` (VARCHAR(40), UNIQUE, NOT NULL)
  Sugeridos: `EMAIL`, `DOCDIGITAL`, `PAPEL`, `POR_MANO`, `LIBRO`, `VENTANILLA_UNICA`, `CORREOS_CHILE`, `PLATAFORMA`, `WHATSAPP`, `OTRO`
* `descripcion` (VARCHAR(200), NULL)

**Normalización (reglas clave)**

* `E-MAIL`, `E MAIL`, `EMAIL.` → `EMAIL`
* `DOC DIGITAL`, `DOCDIGITAL`, `doCDIGITAL` → `DOCDIGITAL`

---

## Tabla: `org_division` (catálogo)

**PK**

* `division_id` (SMALLINT/INT)

**Campos**

* `codigo` (VARCHAR(40), UNIQUE, NOT NULL) Ej: `DIPIR`, `DAF`, `DIT`, `DIFOI`, `UCR`, `DIPLADE`, `DIDESOH`, `GABINETE`, `UNIDAD_RENDICIONES`, `JURIDICA`
* `nombre` (VARCHAR(120), NULL)

**Nota de calidad:** en `DERIVADO A: (DIVISIÓN)` aparecen combinaciones (`UCR-DIFOI`, `GABINETE - DIT`, etc.). Eso debe ir a una tabla puente.

---

## Tabla: `doc_derivacion` (puente documento–división)

**Propósito:** permitir 1 documento → N derivaciones.

**PK**

* `derivacion_id` (BIGINT)

**FK**

* `documento_id` → `doc_documento`
* `division_id` → `org_division`

**Campos**

* `rol` (VARCHAR(20), NOT NULL) valores sugeridos: `DERIVADO_A`, `COPIA`, `REVISA`
* `texto_original` (TEXT, NULL) (para preservar el valor crudo)
* `orden` (SMALLINT, NULL)

**ETL recomendado**

* Parsear `DERIVADO A: (DIVISIÓN)` por separadores: `-`, `/`, `,`, “Y”, etc.
* Conservar `texto_original` siempre.

---

## Tabla: `doc_evento` (seguimiento / workflow)

**Propósito:** normalizar el bloque final de RECIBIDOS (y permitir historial real).

**PK**

* `evento_id` (BIGINT)

**FK**

* `documento_id` → `doc_documento`
* `canal_id` → `doc_canal` (opcional)

**Campos**

* `tipo_evento` (VARCHAR(30), NOT NULL)
  Valores sugeridos: `SEGUIMIENTO`, `DERIVACION`, `RESPUESTA`, `INSTRUCCION`, `RECEPCION_INTERNA`, etc.
* `fecha_evento` (DATE, NULL)
* `actor` (TEXT, NULL) (firma/responsable)
* `respuesta_flag` (BOOLEAN, NULL)
* `instruccion` (TEXT, NULL)
* `plazo_tipo` (VARCHAR(20), NULL) valores: `FECHA`, `DIAS`, `SIN_INFO`
* `plazo_dias` (INT, NULL)
* `plazo_fecha` (DATE, NULL)
* `comentario` (TEXT, NULL)

**Nota de calidad (importante):**
En RECIBIDOS, el campo `FECHA` del seguimiento trae texto no-fecha en varios casos (ej. “EN LIBRO”, nombres), y `Plazo` mezcla `SP`, `s/i`, y números (días). Por eso esta tabla permite almacenar “lo que haya” sin romper tipos.

---

# MÓDULO B — Rendiciones / subvenciones

## Tabla: `fin_programa` (catálogo)

**PK**

* `programa_id` (SMALLINT/INT)

**Campos**

* `codigo` (VARCHAR(20), UNIQUE, NOT NULL) Ej: `SUBVENCIONES`, `FNDR`, `ADNC`, `ADCD`
* `nombre` (VARCHAR(80), NOT NULL)

---

## Tabla: `fin_institucion`

**PK**

* `institucion_id` (BIGINT)

**Campos**

* `nombre_raw` (TEXT, NOT NULL)
* `nombre_norm` (TEXT, NOT NULL) (upper/trim/espacios normalizados)

**Índice**

* `idx_institucion_nombre_norm` (`nombre_norm`)

---

## Tabla: `fin_iniciativa`

**PK**

* `iniciativa_id` (BIGINT)

**FK**

* `programa_id` → `fin_programa`

**Campos**

* `codigo_iniciativa` (VARCHAR(50), NOT NULL)  ← `CÓDIGO` (rendiciones)
* `nombre_iniciativa` (TEXT, NULL)  ← `NOMBRE DE LA INICIATIVA` (solo en RENDICIONES 2024)
* `codigo_norm` (VARCHAR(50), NOT NULL) (trim/upper)

**Índice**

* `idx_iniciativa_codigo` (`codigo_norm`)

---

## Tabla: `fin_rendicion`

**PK**

* `rendicion_id` (BIGINT)

**FK**

* `institucion_id` → `fin_institucion`
* `iniciativa_id` → `fin_iniciativa`
* *(opcional)* `documento_id` → `doc_documento`

**Campos**

* `correlativo` (VARCHAR(50), NULL) ← `CORRELATIVO`
  Regla: no es único (hay repetidos, p.ej. “s/n”).

* `tipo_documento_rendicion` (VARCHAR(30), NOT NULL) ← `TIPO DOCUMENTO`
  Normalización recomendada:

  * `REND`, `REND.` → `RENDICION`
  * `SUBS`, `SUBS.` → `SUBVENCION`
  * `REINT` → `REINTEGRO` (si corresponde)
  * otros → `OTRO`

* `fecha_docto` (DATE, NULL) ← `FECHA DCTO`

* `fecha_ingreso` (DATE, NULL) ← `FECHA INGRESO`

* `fecha_entrega` (DATE, NULL) ← `FECHA ENTREGA`

* `monto_clp` (NUMERIC(14,0), NULL)

* `monto_raw` (TEXT, NULL) ← `MONTO DE LA RENDICIÓN`

* `recepcionado_por` (TEXT, NULL)

* `firma` (TEXT, NULL)

**Notas de calidad críticas (para ETL)**

* En RENDICIONES 2024 hay muchas fechas en formato **“30-abr-24”** y placeholders como **“S/F”**, además de errores tipo **“5-11-20245”** o **“10/05//2024”**.
  Recomendación: ETL que convierta meses `ene/feb/mar/abr/may/jun/jul/ago/sep/oct/nov/dic` a números; `S/F` → NULL; y marque errores de año (5 dígitos).

* En montos hay formato mixto: `"$2,350,180.00"` y `"$1.800.000"`; se debe unificar para calcular.

---

## 3) Mapeo directo desde tus hojas actuales (ETL “de referencia”)

### RECIBIDOS → `doc_documento` + `doc_evento` + `doc_derivacion`

* `doc_documento.correlativo_recibidos` ← `C`
* `doc_documento.canal_recepcion_id` ← `VIA RECEPCIÓN` (normalizado)
* `doc_documento.numero_documento` ← `NÚMERO DOCUMENTO`
* `doc_documento.tipo_documento_id` ← `TIPO DE DOCUMENTO` (mapeo)
* `doc_documento.fecha_documento/recepcion/entrega` ← `FECHA DOCUMENTO`, `FECHA RECEPCIÓN`, `FECHA DE ENTREGA`
* `doc_documento.materia`, `remitente`, `destinatario`, `adjunto_descripcion`
* `doc_derivacion` ← `DERIVADO A: (DIVISIÓN)` (parseado)
* `doc_evento` (si existe info) ← `FECHA`, `FIRMA`, `Responsable`, `Medio derivación`, `Respuesta si/no`, `Instrucción`, `Plazo`, `Observación`

### OFICIOS / CARTAS / OFICIOS INTERNOS → `doc_documento` + `doc_derivacion`

* `numero_documento` ← `N° DCTO` o `NUMERO DOCUMENTO`
* `tipo_documento_id` ← `TIPO DE DCTO` / `TIPO DE DOCUMENTO`
* `canal_despacho_id` ← `DISTRIBUCIÓN` (normalizado)
* `link_documento_url` ← `LINK AL DOCUMENTO`
* `derivacion` ← `DERIVADO A: (DIVISIÓN)` (ojo: hoy mezcla instrucciones)

### MEMOS / MEMOS INTERNOS → `doc_documento`

* `folio` ← `FOLIO`
* `responsable` / `unidad_origen_raw` (`DE` o `DIVISIÓN`)
* `dirigido_a` ← `PARA:` o `DIRIGIDO A:`
* `canal_despacho_id` ← `VÍA DESPACHO`
* `firma_recepcion` hoy está en MEMOS como campo separado: recomendable moverlo a `doc_evento.actor` con tipo_evento `RECEPCION_INTERNA` si se usa.

### RESOLUCIONES EXENTAS / AFECTAS → `doc_documento`

* `folio` ← `FOLIO`
* `tipo_documento_id` fijo según hoja (exenta/afecta)
* `estado` (solo afectas) → mejor como `doc_evento` tipo `ESTADO` o columna específica si desean.

### RENDICIONES FNDR Y ADNC → `fin_rendicion` (normalizando “dos tablas en una”)

* Convertir a formato largo:

  * Bloque FNDR: `programa=FNDR`, `codigo=CÓDIGO`, fechas, institución
  * Bloque derecho: `programa=ADNC/ADCD`, `codigo=CÓDIGO.1`, fechas, institución
* Insertar en `fin_programa`, `fin_iniciativa`, `fin_institucion`, `fin_rendicion`

---

## 4) Reglas de calidad mínimas (muy recomendadas)

1. **IDs como texto:** `C`, `N° DCTO`, `FOLIO`, `CORRELATIVO` siempre VARCHAR (para no perder ceros).
2. **Fechas normalizadas:** todo a DATE; `S/F` → NULL; meses “abr” → 04.
3. **Canales y tipos con catálogo:** evitar variantes `E-MAIL/EMAIL/E MAIL`.
4. **Derivación separada:** no guardar “GABINETE - DIT” como un solo valor; parsear.
5. **Montos a NUMERIC:** guardar `monto_raw` y `monto_clp` calculado.
6. **Reporte de duplicados:** especialmente `RECIBIDOS.C` (30 duplicados) y `RENDICIONES.CORRELATIVO` (“s/n” repetido).
