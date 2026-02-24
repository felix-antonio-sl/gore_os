# Mapeo 
---

# 1) Mapeo (origen → destino) por hoja

## Convención de destino (modelo)

* **Dimensiones**: `dim_periodo`, `dim_clasificador_presup`, `dim_territorio`, `dim_institucion`, `dim_iniciativa`, `dim_tipo_evento`
* **Hechos**: `fact_convenio` (1 fila por registro/carga) y `fact_evento_documental` (N filas por registro, una por hito/documento)

> Regla clave: columnas “Nº …” y “FECHA …” se transforman en **filas** en `fact_evento_documental` (modelo “largo”), no quedan como columnas.

---

## 1.1 Hoja: **CONVENIOS 2023 y 2024** (24 columnas)

### A) Mapeo a dimensiones + `fact_convenio` (atributos base)

| Columna origen                            | Tabla destino             | Campo destino                                        | Transformación recomendada                                                                    |
| ----------------------------------------- | ------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `SUB`                                     | `dim_clasificador_presup` | `sub`                                                | Trim; guardar como texto o int (recomendado texto si quieres consistencia con otros orígenes) |
| `ITEM`                                    | `dim_clasificador_presup` | `item`                                               | Trim; **texto** (no int) para conservar ceros/formatos                                        |
| ` ASIG`                                   | `dim_clasificador_presup` | `asig`                                               | Trim; **texto**; `-` → NULL                                                                   |
| `CODIGO`                                  | `dim_iniciativa`          | `codigo`                                             | Trim; forzar **texto** (aunque parezca numérico)                                              |
| `NOMBRE DE LA INICIATIVA`                 | `dim_iniciativa`          | `nombre_iniciativa_raw`                              | Trim (sin cambiar contenido)                                                                  |
| `UNIDAD TECNICA `                         | `dim_institucion`         | `unidad_tecnica_raw`                                 | Trim; (opcional) normalizar mayúsculas/espacios a `unidad_tecnica_norm`                       |
| `PROVINCIA`                               | `dim_territorio`          | `provincia_raw`                                      | Trim; (opcional) catálogo a `provincia_norm`                                                  |
| `COMUNA`                                  | `dim_territorio`          | `comuna_raw`                                         | Trim; (opcional) catálogo a `comuna_norm`                                                     |
| `MONTO FNDR M$`                           | `fact_convenio`           | `monto_fndr_ms`                                      | Quitar `$`, puntos, espacios; parse a número (M$)                                             |
| `ESTADO DE CONVENIO`                      | `fact_convenio`           | `estado_convenio_raw`/`estado_convenio_norm`         | Trim; mapear a catálogo (ej. FIRMADO, NO_SE_FIRMO, etc.)                                      |
| `FECHA FIRMA DE CONVENIO `                | `fact_convenio`           | `fecha_firma_convenio`                               | Parse fecha; si no parsea → NULL y pasar texto a `observacion_estado`                         |
| `ESTADO CONVENIO EN CGR`                  | `fact_convenio`           | `estado_convenio_cgr_raw`/`estado_convenio_cgr_norm` | Trim; mapear a catálogo CGR                                                                   |
| `REFERENTE TECNICO O CONTRAPARTE TECNICA` | `fact_convenio`           | `referente_tecnico_raw`                              | Trim (no normalizar automáticamente nombres propios)                                          |

Además, al cargar:

* `dim_periodo.anio = 2023/2024` (según tu criterio de corte; o `anio = NULL` + `fuente_hoja = 'CONVENIOS 2023 y 2024'`)
* `fact_convenio.origen_hoja = 'CONVENIOS 2023 y 2024'`

### B) Mapeo a `fact_evento_documental` (eventos/hitos)

| Columnas origen                                                                   | `dim_tipo_evento.tipo_evento` | Campos destino                                    | Transformación                                                  |
| --------------------------------------------------------------------------------- | ----------------------------- | ------------------------------------------------- | --------------------------------------------------------------- |
| `Nº RES INCORPORA/ CERT CORE` + `FECHA RES INCORPORA/ CERT CORE`                  | `incorpora_cert_core`         | `numero_documento`, `fecha_documento`             | Nº como texto; fecha parse; si falla → NULL + `observacion_raw` |
| `Nº RES CREA ASIGNACIÓN` + `FECHA RES CREA  ASIGNACIÓN`                           | `crea_asignacion`             | `numero_documento`, `fecha_documento`             | idem                                                            |
| `Nº RES APRUEBA CONVENIO ` + `FECHA RES APRUEBA CONVENIO` + `TIPO DE RESOLUCIÓN ` | `aprueba_convenio`            | + `tipo_resolucion_norm`                          | tipo_resolución a catálogo {EXENTA, AFECTA}                     |
| `Nº OFICIO ENVIA CONVENIO` + `FECHA OFICIO ENVIA CONVENIO`                        | `oficio_envio_convenio`       | `numero_documento`, `fecha_documento`             | valores tipo “EN TRAMITE” → `observacion_raw`                   |
| `FECHA TOMA DE RAZON DE CGR` (+ `ESTADO CONVENIO EN CGR`)                         | `toma_razon_cgr`              | `fecha_documento` (+ `estado_cgr_norm`)           | fecha parse; estado se puede duplicar aquí para trazabilidad    |
| `Nº RES REFERENTE TECNICO`                                                        | `res_referente_tecnico`       | `numero_documento` (+ opcional `fecha_documento`) | si viene “num/fecha”, split y parse                             |

---

## 1.2 Hoja: **CONVENIOS 2025** (21 columnas)

### A) Base a dimensiones + `fact_convenio`

| Columna origen                                                                                        | Tabla destino   | Campo destino                                        | Transformación                                                                          |
| ----------------------------------------------------------------------------------------------------- | --------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `SUB`, `ITEM`, ` ASIG`, `CODIGO`, `UNIDAD TECNICA `, `NOMBRE DE LA INICIATIVA`, `PROVINCIA`, `COMUNA` | mismas dims     | mismos campos                                        | mismas reglas de trim/normalización                                                     |
| ` MONTO FNDR M$`                                                                                      | `fact_convenio` | `monto_fndr_ms`                                      | limpieza igual (nota: aquí el encabezado tiene **un espacio distinto** al de 2023–2024) |
| `ESTADO RES CREA EN CGR`                                                                              | `fact_convenio` | `estado_res_crea_cgr_raw`/`estado_res_crea_cgr_norm` | catálogo de estados (si define institucionalmente)                                      |
| `ESTADO DE CONVENIO`                                                                                  | `fact_convenio` | `estado_convenio_raw/norm`                           | catálogo                                                                                |
| `FECHA FIRMA DE CONVENIO `                                                                            | `fact_convenio` | `fecha_firma_convenio`                               | parse; textos → observación                                                             |
| `ESTADO CONVENIO EN CGR`                                                                              | `fact_convenio` | `estado_convenio_cgr_raw/norm`                       | catálogo                                                                                |
| `REFERENTE TECNICO `                                                                                  | `fact_convenio` | `referente_tecnico_raw`                              | trim                                                                                    |

### B) Eventos a `fact_evento_documental`

| Columnas origen                                                  | `dim_tipo_evento.tipo_evento` | Transformación                                                                        |
| ---------------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------- |
| `Nº RES INCORPORA/ CERT CORE` + `FECHA RES INCORPORA/ CERT CORE` | `incorpora_cert_core`         | igual a 2023–2024                                                                     |
| `Nº RES CREA ASIGNACIÓN` + `FECHA RES CREA  ASIGNACIÓN`          | `crea_asignacion`             | igual                                                                                 |
| `Nº RES  Y FECHA APRUEBA CONVENIO `                              | `aprueba_convenio`            | **split**: `numero_documento` + `fecha_documento` (separar por `/` o patrón de fecha) |
| `FECHA TOMA DE RAZON DE CGR` (+ `ESTADO CONVENIO EN CGR`)        | `toma_razon_cgr`              | igual                                                                                 |
| `Nº  Y FECHA OFICIO ENVIA CONVENIO`                              | `oficio_envio_convenio`       | split: número/fecha                                                                   |

---

## 1.3 Hoja: **MODIFICACIONES** (19 columnas)

### A) Base a dimensiones + `fact_convenio` (como “registro operacional de modificación”)

| Columna origen             | Tabla destino             | Campo destino                          | Transformación                                                          |
| -------------------------- | ------------------------- | -------------------------------------- | ----------------------------------------------------------------------- |
| `SUB`, `ITEM`, ` ASIG`     | `dim_clasificador_presup` | `sub`, `item`, `asig`                  | igual                                                                   |
| `CODIGO`                   | `dim_iniciativa`          | `codigo`                               | **forzar texto** (en este CSV suele venir numérico/float)               |
| `NOMBRE DE LA INICIATIVA`  | `dim_iniciativa`          | `nombre_iniciativa_raw`                | trim                                                                    |
| `RUT INSTITUCIÓN`          | `dim_institucion`         | `rut`                                  | trim; validación RUT (regex + DV si implementas)                        |
| `UNIDAD TECNICA `          | `dim_institucion`         | `unidad_tecnica_raw`                   | trim                                                                    |
| `COMUNA`                   | `dim_territorio`          | `comuna_raw`                           | trim; normalización “CHILLAN Y CH. VIEJO”, etc.                         |
| `TIPO DE CONVENIO`         | `fact_convenio`           | `tipo_registro` / `tipo_convenio_norm` | mapear a catálogo: `TRANSFERENCIA_BIENES`, `MODIFICACION_CONVENIO`      |
| `ESTADO DE CONVENIO`       | `fact_convenio`           | `estado_convenio_raw/norm`             | catálogo                                                                |
| `ESTADO`                   | `fact_convenio`           | `estado_operativo_raw/norm`            | **separar semántica** de “estado_convenio”; mapear a catálogo operativo |
| `FECHA FIRMA DE CONVENIO ` | `fact_convenio`           | `fecha_firma_convenio`                 | parse                                                                   |

> Aquí `dim_periodo.fuente_hoja = 'MODIFICACIONES'` (el año puede quedar NULL si no está explicitado; o derivarlo si el código/fecha lo permite).

### B) Eventos a `fact_evento_documental`

| Columnas origen                                            | `dim_tipo_evento.tipo_evento` | Transformación                                        |
| ---------------------------------------------------------- | ----------------------------- | ----------------------------------------------------- |
| `Nº RESOLUCION` + `FECHA ` + `TIPO DE RESOLUCION`          | `resolucion_modificacion`     | parse fecha; tipo resolución a catálogo EXENTA/AFECTA |
| `Nº OFICIO ENVIA CONVENIO` + `FECHA OFICIO ENVIA CONVENIO` | `oficio_envio_convenio`       | parse fecha; texto → observación                      |
| `FECHA TOMA DE RAZON DE CGR` (+ `ESTADO CONVENIO EN CGR`)  | `toma_razon_cgr`              | parse fecha; estado catálogo                          |

---

# 2) Diccionario de datos del modelo

## 2.1 `dim_periodo`

**Propósito:** identificar periodo/fuente de carga.
**Grano:** 1 fila por combinación (anio, fuente_hoja) o solo fuente_hoja si no hay año.

| Campo         | Tipo     | Nulo | Descripción                            | Reglas                                                               |
| ------------- | -------- | ---: | -------------------------------------- | -------------------------------------------------------------------- |
| `periodo_id`  | int (PK) |   no | Identificador interno                  | autoincrement                                                        |
| `anio`        | int      |   sí | Año del registro (si se puede asignar) | 2023/2024/2025 o NULL                                                |
| `fuente_hoja` | text     |   no | Nombre hoja origen                     | valores fijos: CONVENIOS 2023 y 2024, CONVENIOS 2025, MODIFICACIONES |

---

## 2.2 `dim_clasificador_presup`

**Propósito:** normalizar SUB/ITEM/ASIG.
**Grano:** 1 fila por combinación única (sub,item,asig).

| Campo       | Tipo     | Nulo | Descripción               | Reglas              |
| ----------- | -------- | ---: | ------------------------- | ------------------- |
| `clasif_id` | int (PK) |   no | Identificador interno     | autoincrement       |
| `sub`       | text     |   no | Subtítulo                 | trim                |
| `item`      | text     |   sí | Ítem (a veces multivalor) | trim; no forzar int |
| `asig`      | text     |   sí | Asignación                | trim; `-`→NULL      |

---

## 2.3 `dim_territorio`

**Propósito:** catálogo territorial con raw + normalizado.
**Grano:** 1 fila por (provincia_raw, comuna_raw) o por comuna_raw según uso.

| Campo            | Tipo     | Nulo | Descripción                   | Reglas                                |
| ---------------- | -------- | ---: | ----------------------------- | ------------------------------------- |
| `territorio_id`  | int (PK) |   no | Identificador interno         |                                       |
| `provincia_raw`  | text     |   sí | Provincia tal como viene      | trim                                  |
| `comuna_raw`     | text     |   sí | Comuna/ámbito tal como viene  | trim                                  |
| `provincia_norm` | text     |   sí | Provincia estandarizada       | catálogo (tildes/ortografía)          |
| `comuna_norm`    | text     |   sí | Comuna estandarizada          | catálogo (CHILLÁN, SAN NICOLÁS, etc.) |
| `ambito_tipo`    | text     |   sí | COMUNA / PROVINCIA / REGIONAL | derivado por reglas                   |

---

## 2.4 `dim_institucion`

**Propósito:** normalizar unidad técnica e identificar por RUT cuando exista.
**Grano:** 1 fila por (rut, unidad_tecnica_norm) o por unidad_tecnica_norm si no hay rut.

| Campo                 | Tipo     | Nulo | Descripción           | Reglas                                               |
| --------------------- | -------- | ---: | --------------------- | ---------------------------------------------------- |
| `institucion_id`      | int (PK) |   no | Identificador interno |                                                      |
| `rut`                 | text     |   sí | RUT institución       | validar formato; normalizar guion                    |
| `unidad_tecnica_raw`  | text     |   sí | Nombre como viene     | trim                                                 |
| `unidad_tecnica_norm` | text     |   sí | Nombre estandarizado  | reglas de mayúsculas/espacios; diccionario si aplica |

---

## 2.5 `dim_iniciativa`

**Propósito:** catálogo de iniciativas por código + nombre.
**Grano:** 1 fila por `codigo` (si decides forzarlo), o por (codigo,nombre_norm) si hay conflictos.

| Campo                    | Tipo     | Nulo | Descripción                 | Reglas                         |
| ------------------------ | -------- | ---: | --------------------------- | ------------------------------ |
| `iniciativa_id`          | int (PK) |   no | Identificador interno       |                                |
| `codigo`                 | text     |   sí | Identificador de iniciativa | trim; **texto siempre**        |
| `nombre_iniciativa_raw`  | text     |   sí | Nombre como viene           | trim                           |
| `nombre_iniciativa_norm` | text     |   sí | Nombre estandarizado        | opcional (normalización suave) |

> Nota práctica: dado que en 2023–2024 hay CODIGO duplicado con diferencias, es sano permitir que `codigo` **no sea único** en esta dimensión (o crear una “versión”/alias).

---

## 2.6 `dim_tipo_evento`

**Propósito:** catálogo de tipos de documento/hito.
**Grano:** 1 fila por tipo_evento.

| Campo            | Tipo     | Nulo | Descripción                      | Valores típicos                                                                                                                                             |
| ---------------- | -------- | ---: | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tipo_evento_id` | int (PK) |   no | Identificador interno            |                                                                                                                                                             |
| `familia`        | text     |   no | RESOLUCION / OFICIO / CGR / OTRO |                                                                                                                                                             |
| `tipo_evento`    | text     |   no | Código del evento                | `incorpora_cert_core`, `crea_asignacion`, `aprueba_convenio`, `oficio_envio_convenio`, `toma_razon_cgr`, `res_referente_tecnico`, `resolucion_modificacion` |
| `descripcion`    | text     |   sí | Descripción humana               |                                                                                                                                                             |

---

## 2.7 `fact_convenio`

**Propósito:** consolidar el “registro principal” por fila cargada desde cada hoja.
**Grano:** 1 fila por fila-origen (no necesariamente 1 por CODIGO).

| Campo                      | Tipo     | Nulo | Descripción                           | Reglas/Notas                                           |
| -------------------------- | -------- | ---: | ------------------------------------- | ------------------------------------------------------ |
| `convenio_id`              | int (PK) |   no | Identificador interno                 |                                                        |
| `periodo_id`               | int (FK) |   no | Relación a periodo                    |                                                        |
| `clasif_id`                | int (FK) |   sí | Relación a clasificador               |                                                        |
| `territorio_id`            | int (FK) |   sí | Relación a territorio                 |                                                        |
| `institucion_id`           | int (FK) |   sí | Relación a institución                |                                                        |
| `iniciativa_id`            | int (FK) |   sí | Relación a iniciativa                 |                                                        |
| `monto_fndr_ms`            | numeric  |   sí | Monto FNDR en M$                      | desde `MONTO FNDR M$`                                  |
| `estado_convenio_raw`      | text     |   sí | Estado como viene                     |                                                        |
| `estado_convenio_norm`     | text     |   sí | Estado normalizado                    | catálogo (FIRMADO, SIN_CONVENIO, …)                    |
| `fecha_firma_convenio`     | date     |   sí | Fecha de firma                        | parse; si no parsea → NULL                             |
| `estado_convenio_cgr_raw`  | text     |   sí | Estado CGR como viene                 |                                                        |
| `estado_convenio_cgr_norm` | text     |   sí | Estado CGR normalizado                | TOMADO_DE_RAZON, TR_CON_ALCANCES, REPRESENTADO, EN_CGR |
| `estado_res_crea_cgr_raw`  | text     |   sí | Solo 2025                             |                                                        |
| `estado_res_crea_cgr_norm` | text     |   sí | Solo 2025                             | catálogo (definir)                                     |
| `referente_tecnico_raw`    | text     |   sí | Referente/contraparte                 | ideal separar persona/unidad en otra fase              |
| `tipo_registro`            | text     |   no | CONVENIO / MODIFICACION               | derivado por origen                                    |
| `tipo_convenio_norm`       | text     |   sí | Solo MODIFICACIONES                   | TRANSFERENCIA_BIENES / MODIFICACION_CONVENIO           |
| `estado_operativo_raw`     | text     |   sí | Solo MODIFICACIONES (`ESTADO`)        |                                                        |
| `estado_operativo_norm`    | text     |   sí | Normalizado                           | catálogo operativo                                     |
| `origen_hoja`              | text     |   no | Trazabilidad                          | nombre hoja                                            |
| `fila_origen`              | int      |   sí | Nº fila (si lo capturas en ETL)       |                                                        |
| `hash_fila`                | text     |   sí | Hash para detectar duplicados exactos | recomendado                                            |

---

## 2.8 `fact_evento_documental`

**Propósito:** tabla “larga” de hitos documentales (resoluciones, oficios, CGR).
**Grano:** 1 fila por evento detectado (por convenio_id).

| Campo                  | Tipo     | Nulo | Descripción                                         | Reglas                       |
| ---------------------- | -------- | ---: | --------------------------------------------------- | ---------------------------- |
| `evento_id`            | int (PK) |   no | Identificador interno                               |                              |
| `convenio_id`          | int (FK) |   no | Registro padre                                      |                              |
| `tipo_evento_id`       | int (FK) |   no | Tipo de evento                                      |                              |
| `numero_documento`     | text     |   sí | N° resolución/oficio/etc.                           | siempre texto                |
| `fecha_documento`      | date     |   sí | Fecha del documento/hito                            | parse; inválido → NULL       |
| `tipo_resolucion_norm` | text     |   sí | EXENTA/AFECTA                                       | solo eventos de resolución   |
| `estado_cgr_norm`      | text     |   sí | Estado CGR                                          | para eventos CGR si aplica   |
| `observacion_raw`      | text     |   sí | texto no estructurado (“EN TRÁMITE”, “UT DESISTE…”) | desde celdas no parseables   |
| `columna_fuente`       | text     |   no | Columna(s) origen                                   | ej. “Nº RES CREA ASIGNACIÓN” |

---

# 3) Catálogos mínimos recomendados (para `*_norm`)

Para que el modelo “cierre” bien, define estos dominios:

* **Estado convenio (`estado_convenio_norm`)**: `FIRMADO`, `SIN_CONVENIO`, `ENCOMENDADO_DIT`, `NO_SE_FIRMO`, `RS_NO_VIGENTE`, `ENVIADO_AL_SERVICIO`, `EN_TRAMITE`, `OTRO`.
* **Estado CGR (`estado_convenio_cgr_norm` / `estado_cgr_norm`)**: `TOMADO_DE_RAZON`, `TR_CON_ALCANCES`, `REPRESENTADO`, `EN_CGR`, `OTRO`.
* **Tipo resolución (`tipo_resolucion_norm`)**: `EXENTA`, `AFECTA`.
* **Tipo convenio modificación (`tipo_convenio_norm`)**: `TRANSFERENCIA_BIENES`, `MODIFICACION_CONVENIO`.
