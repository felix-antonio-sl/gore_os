# Diccionario
---

# 0) Convenciones del diccionario

## Tipos (canónicos)

* **string**: texto libre.
* **int**: entero.
* **decimal(18,2)**: monto (idealmente CLP sin símbolo).
* **date**: fecha (ISO `YYYY-MM-DD`).
* **bool**: `SI/NO` (o `TRUE/FALSE` tras normalización).
* **enum**: catálogo cerrado.

## Reglas transversales de limpieza (recomendadas)

* **Montos**: quitar `$`, espacios, puntos/comas de miles, y convertir a **decimal**.
* **Fechas**: normalizar a `YYYY-MM-DD`. Si el campo trae texto (“Cheque”, “Observada”), moverlo a `observacion_*`.
* **Teléfonos**: guardar como **string**, no número (evitar `.0` / notación científica).
* **Comunas**: normalizar mayúsculas, tildes (`CHILLÁN`), y eliminar dobles espacios.
* **Correos**: extraer email si viene como `Nombre <correo@dominio>`.

## Clasificación de sensibilidad (PII)

* **PII alta**: `NOMBRE REPRESENTANTE LEGAL`, `CORREO`, `CORREO 2`, `TELÉFONO`, `ORGANIZACIÓN FIRMANTE` (si identifica personas), `CONTRAPARTE` (si es persona).
* **PII media**: nombres de referentes internos (si son personas).
* **No PII**: códigos, montos, fechas, estados, comuna/provincia.

---

# 1) Modelo de datos (tablas canónicas)

## 1.1 FNDR 8% 2024 — Maestro de iniciativas (consolidado de F.*)

**Tabla canónica**: `fnrd8_iniciativa`
**Origen**: `F.SEGURIDAD`, `F.SOCIAL`, `F.ADULTO MAYOR`, `F.CULTURA`, `F.DEPORTE`, `F.EQUIDAD DE GÉNERO`, `F.MEDIO AMBIENTE`
**Grano**: 1 fila = 1 iniciativa financiada/recomendada (organización + iniciativa).
**Clave primaria**: `codigo_8pct` (string)
**Claves alternativas**: (`rut_institucion`, `nombre_iniciativa`, `comuna`) para control de duplicados.

### Campos

| Campo canónico                   | Origen (variantes de columna)                                |          Tipo | Requerido | Descripción / reglas                                                                                                |
| -------------------------------- | ------------------------------------------------------------ | ------------: | :-------: | ------------------------------------------------------------------------------------------------------------------- |
| `codigo_8pct`                    | `CÓDIGO`, `CODIGO`, `Unnamed: 0`                             |        string |    Sí     | Identificador del concurso (ej. `2401SC0126`). Validar patrón por fondo.                                            |
| `tipologia_fondo`                | `TIPOLOGÍA`, `TIPOLOGIA`                                     |          enum |    Sí     | Fondo: `SEGURIDAD`, `SOCIAL`, `ADULTO_MAYOR`, `CULTURA`, `DEPORTE`, `EQUIDAD_GENERO`, `MEDIO_AMBIENTE`. Normalizar. |
| `nombre_institucion`             | `NOMBRE INSTITUCIÓN`                                         |        string |    Sí     | Nombre organización receptora.                                                                                      |
| `rut_institucion`                | `RUT INSTITUCIÓN`                                            |        string |    Sí     | RUT con guion; normalizar puntos.                                                                                   |
| `nombre_iniciativa`              | `NOMBRE INICIATIVA`                                          |        string |    Sí     | Texto; puede venir con saltos de línea.                                                                             |
| `provincia`                      | `PROVINCIA`                                                  |        string |    No     | Texto normalizado.                                                                                                  |
| `comuna`                         | `COMUNA`                                                     |        string |    Sí     | Normalizar tildes/espacios (clave de cruce territorial).                                                            |
| `correo_1`                       | `CORREO`                                                     |        string |    No     | Extraer email “limpio”. (PII alta).                                                                                 |
| `correo_2`                       | `CORREO 2`                                                   |        string |    No     | A veces `Nombre <correo>`. Extraer email. (PII alta).                                                               |
| `telefono`                       | `TELÉFONO`                                                   |        string |    No     | Guardar como string. Puede contener múltiples números. (PII alta).                                                  |
| `representante_legal`            | `NOMBRE REPRESENTANTE LEGAL`                                 |        string |    No     | (PII alta).                                                                                                         |
| `fecha_transferencia`            | `FECHA DE TRANSFERENCIA`, `RECIBIÓ TRANSFERENCIA`            |          date |    No     | En algunas hojas el encabezado sugiere booleano, pero trae fecha. Normalizar.                                       |
| `monto_transferido`              | `MONTO TRANSFERIDO`, `MONTO TRANFERIDO`, `MONTO TRANFERIDO ` | decimal(18,2) |    No     | Convertir desde texto con `$`. Validar >= 0.                                                                        |
| `resolucion_marco`               | `Nº RESOLUCIÓN QUE INCORPORA AL MARCO`                       |        string |    No     | Puede traer múltiples resoluciones; no parsear si no es necesario.                                                  |
| `estado_ejecucion_2024`          | `ESTADO EJECUCIÓN 2024`, ` ESTADO EJECUCIÓN 2024`            |          enum |    No     | Catálogo sugerido: `EN_EJECUCION`, `EJECUTADA`, `TERMINADA`, `SIN_INFO`.                                            |
| `fecha_ingreso_of_partes`        | `FECHA (DE) INGRESO A OFICINA DE PARTES`                     |          date |    No     | Fecha ingreso rendición/antecedentes.                                                                               |
| `fecha_envio_cierre_tecnico_ucr` | `FECHA ENVÍO CIERRE TÉCNICO A UCR`                           |          date |    No     | Fecha envío a UCR (cierre técnico).                                                                                 |
| `fecha_cierre_financiero_ucr`    | `FECHA CIERRE FINANCIERO UCR`                                |          date |    No     | Muy incompleta: **no asumir 0 = no cerrado**.                                                                       |
| `rendicion_a_tiempo`             | `INGRESO RENDICIÓN A TIEMPO`                                 |          bool |    No     | Normalizar `SÍ/SI/NO`.                                                                                              |
| `detalle_observacion`            | `DETALLE OBSERVACIÓN`, `DETALLE OBSERVACIONES`, `<<<<<`      |        string |    No     | Observación técnica/administrativa (texto libre).                                                                   |
| `detalle_obs_tecnica`            | `DETALLE OBSERVACIÓN TÉCNICA`                                |        string |    No     | Solo Medio Ambiente.                                                                                                |
| `detalle_obs_financiera`         | `DETALLE OBSERVACIÓN FINANCIERA`                             |        string |    No     | Medio Ambiente; hoy suele venir vacío.                                                                              |
| `estado_ucr`                     | `Estado UCR`                                                 |          enum |    No     | Solo Cultura. Sugerido: `APROBADA`, `OBSERVADA`, `PENDIENTE`, `SIN_INFO`.                                           |

**Checks de calidad recomendados**

* `codigo_8pct` no nulo, único por fondo.
* `fecha_transferencia` nula ⇒ “no transferido” (no equivale a eliminado).
* `monto_transferido` nulo con fecha transferencia llena ⇒ inconsistencia.

---

## 1.2 FNDR 8% 2024 — Eliminadas del marco presupuestario

**Tabla**: `fnrd8_eliminada_marco`
**Origen**: `ELIMINADAS MARCO PRESUPUESTARIO 8% 2024`
**Grano**: 1 fila = 1 iniciativa eliminada/excluida.
**Clave**: `codigo_8pct`

| Campo canónico       | Origen               |    Tipo | Req.  | Reglas                                             |
| -------------------- | -------------------- | ------: | :---: | -------------------------------------------------- |
| `codigo_8pct`        | `CÓDIGO`             |  string |  Sí   | Validar formato; detectar ceros faltantes.         |
| `fondo`              | `FONDO`              |    enum |  Sí   | Normalizar (“SEGURIDAD” vs “SEGURIDAD CIUDADANA”). |
| `nombre_institucion` | `NOMBRE INSTITUCIÓN` |  string |  Sí   |                                                    |
| `nombre_iniciativa`  | `NOMBRE INICIATIVA`  |  string |  Sí   |                                                    |
| `rut_institucion`    | `RUT INSTITUCIÓN`    |  string |  Sí   |                                                    |
| `comuna`             | `COMUNA`             |  string |  Sí   |                                                    |
| `monto`              | `MONTO`              | decimal |  No   | Convertir desde texto.                             |
| `resolucion`         | `RESOLUCIÓN`         |  string |  No   |                                                    |

---

## 1.3 FNDR 8% 2024 — Habilitadas fuera de plazo

**Tabla**: `fnrd8_habilitada_fuera_plazo`
**Origen**: `HABILITADAS FUERA DE PLAZO`
**Clave**: `codigo_8pct` (ojo: puede haber duplicados)

Campos: **igual que `fnrd8_iniciativa`** + campo adicional:

| Campo               | Origen         | Tipo | Req.  | Reglas                                                                                                 |
| ------------------- | -------------- | ---: | :---: | ------------------------------------------------------------------------------------------------------ |
| `dias_retraso_decl` | `DIA RETRASOS` |  int |  No   | En origen viene vacío o mal tipado; idealmente **calcular**: `fecha_ingreso_of_partes - fecha_limite`. |

---

## 1.4 FNDR 8% 2024 — Inhabilitadas: rendidas fuera de plazo y no rendidas

**Tabla**: `fnrd8_inhabilitada`
**Origen**: `INHABILITADAS RENDIDAS FUERA PLAZO Y NO RENDIDAS`
**Clave**: `codigo_8pct`

Campos: **igual que `fnrd8_iniciativa`** + `dias_retraso_decl` (misma recomendación: calcular y no confiar ciegamente en el origen).

---

## 1.5 FNDR 8% 2024 — Recursos de organizaciones sin rendir

**Tabla**: `fnrd8_sin_rendir`
**Origen**: `RECURSOS ORGANIZACIONES SIN RENDIR`
**Clave**: `codigo_8pct` (puede haber filas con código vacío)

Campos: **igual que `fnrd8_iniciativa`**.
**Regla importante**: si `rendicion_a_tiempo = SI` pero está en esta lista, mantener y marcar como **inconsistencia de fuente** (`flag_inconsistencia_fuente = true`).

---

## 1.6 FNDR 8% 2024 — Resúmenes

Hay dos resúmenes con definiciones/cortes distintos. Conviene guardarlos como tablas separadas:

### a) `fnrd8_resumen_1` (RESUMEN FNDR 8%2024)

**Origen**: `RESUMEN FNDR 8%2024`
**Grano**: 1 fila = 1 fondo (más TOTAL)

Campos (todos int):

* `fondo`
* `no_transferido`
* `organizaciones_transferidas`
* `rendidas`
* `enviadas_ucr`
* `con_observaciones_tecnicas`
* `pendiente_revision`
* `no_rendida`
* `rendicion_fuera_plazo`

**Nota de calidad**: separar filas de “Importante/Revisar…” a otra hoja o excluirlas por regla (no son datos).

### b) `fnrd8_resumen_2` (Hoja 18)

**Origen**: `Hoja 18`
Campos (int):

* `fondo`
* `transferidas`
* `rendidas`
* `pendientes_de_rendir`
* `con_cierre_tecnico`
* `con_observaciones`
* `pendientes_de_revision`

---

## 1.7 Distribución territorial (lookup)

**Tabla**: `territorial_asignacion_comuna`
**Origen**: `DISTRIBUCIÓN TERRITORIAL`
**Grano**: 1 fila = 1 comuna asignada a 1 profesional
**Clave**: `comuna`

| Campo         | Origen               |   Tipo | Req.  | Reglas                                                             |
| ------------- | -------------------- | -----: | :---: | ------------------------------------------------------------------ |
| `profesional` | `NOMBRE PROFESIONAL` | string |  Sí   | En el CSV puede venir vacío por celdas combinadas: “forward fill”. |
| `comuna`      | `COMUNA ASIGNADA`    | string |  Sí   | Normalizar y usar como llave para cruces.                          |

---

# 2) Asignaciones Directas 23–24

**Tabla**: `asignacion_directa`
**Origen**: `ASIGNACIONES DIRECTAS 23-24`
**Grano**: 1 fila = 1 asignación (excluir fila TOTAL en procesos)

| Campo canónico          | Origen                               |    Tipo | Req.  | Reglas                                                        |
| ----------------------- | ------------------------------------ | ------: | :---: | ------------------------------------------------------------- |
| `codigo_ad`             | `CÓDIGO`                             |  string |  Sí   | Identificador AD.                                             |
| `referente_ucr`         | `REFERENTE UCR`                      |  string |  No   | Persona/rol interno (PII media).                              |
| `nombre_iniciativa`     | `NOMBRE INICIATIVA`                  |  string |  Sí   |                                                               |
| `unidad_ejecutora`      | `UNIDAD EJECUTORA`                   |  string |  Sí   |                                                               |
| `anio_inicio_ejecucion` | `AÑO INICIO EJECUCIÓN`               |     int |  No   |                                                               |
| `estado_iniciativa`     | `ESTADO DE LA INICIATIVA...`         |    enum |  No   | `EN_EJECUCION/EJECUTADA/TERMINADA`.                           |
| `referente_tecnico`     | `REFERENTE TÉCNICO`                  |  string |  No   | PII media.                                                    |
| `division`              | `DIVISIÓN`                           |  string |  No   |                                                               |
| `estado_rendicion`      | `ESTADO DE LA RENDICIÓN`             |    enum |  No   | Catálogo sugerido según uso real (APROBADA/EN REVISION/etc.). |
| `resolucion_rf`         | `NUMERO Y FECHA DE LA RESOLUCIÓN...` |  string |  No   | Texto mixto.                                                  |
| `monto_transferido`     | `MONTO TRANSFERIDO`                  | decimal |  No   | Convertir.                                                    |
| `fecha_transferencia`   | `FECHA DE LA TRANSFERENCIA`          |    date |  No   | En origen viene vacía.                                        |
| `monto_rendido`         | `MONTO RENDIDO`                      | decimal |  No   | Convertir; “$ -” ⇒ NULL o 0 según regla.                      |
| `monto_reintegrado`     | `MONTO REINTEGRADO`                  | decimal |  No   |                                                               |
| `total_rendido`         | `TOTAL RENDIDO`                      | decimal |  No   |                                                               |
| `saldo`                 | `SALDO`                              | decimal |  No   | Validar: `saldo ≈ transferido - total_rendido`.               |
| `pct_rendido`           | `% RENDIDO A LA FECHA`               | decimal |  No   | Guardar como 0–100 (convertir “95%”).                         |
| `observaciones`         | `OBSERVACIONES`                      |  string |  No   | Texto libre.                                                  |

---

# 3) Programas Sociales (BIP) + Cartera 2026

## 3.1 Programas Sociales (seguimiento de remesas)

**Tabla**: `programa_social_bip`
**Origen**: `PROGRAMAS SOCIALES`
**Clave**: `codigo_bip`

| Campo                    | Origen                         |    Tipo | Req.  | Reglas                                                       |
| ------------------------ | ------------------------------ | ------: | :---: | ------------------------------------------------------------ |
| `codigo_bip`             | `CÓDIGO BIP`                   |  string |  Sí   | Identificador BIP.                                           |
| `comuna`                 | `COMUNA`                       |  string |  No   |                                                              |
| `nombre_proyecto`        | `NOMBRE PROYECTO`              |  string |  Sí   |                                                              |
| `unidad_ejecutora`       | `UNIDAD EJECUTORA`             |  string |  No   |                                                              |
| `rut_institucion`        | `RUT INSTITUCIÓN`              |  string |  No   |                                                              |
| `contraparte_nombre`     | `PROFESIONAL CONTRAPARTE...`   |  string |  No   | PII alta si persona.                                         |
| `contraparte_telefono`   | `TELÉFONO DE CONTACTO`         |  string |  No   | PII alta.                                                    |
| `contraparte_correo`     | `CORREO ELECTRÓNICO`           |  string |  No   | PII alta.                                                    |
| `financiamiento`         | `FINANCIAMIENTO`               |    enum |  No   | Ej. `SUBTITULO_24`.                                          |
| `objetivo_programa`      | `OBJETIVO DEL PROGRAMA`        |  string |  No   |                                                              |
| `benef_hombres`          | `Nº DE BENEFICIARIOS HOMBRES`  |     int |  No   | Hay casos con texto mezclado: limpiar o mover a observación. |
| `benef_mujeres`          | `Nº DE BENEFICIARIAS MUJERES`  |     int |  No   | Cuidar separador “2.527” (miles).                            |
| `anio_inicio`            | `AÑO INICIO EJECUCIÓN`         |     int |  No   |                                                              |
| `periodo_meses`          | `PERIODO EJECUCIÓN (M)`        |     int |  No   |                                                              |
| `estado_iniciativa`      | `ESTADO DE LA INICIATIVA...`   |    enum |  No   |                                                              |
| `referente_rtf`          | `REFERENTE TÉCNICO FINANCIERO` |  string |  No   | PII media/alta.                                              |
| `resolucion_rtf`         | `NUMERO Y FECHA... RTF`        |  string |  No   | Texto mixto.                                                 |
| `division`               | `DIVISIÓN`                     |  string |  No   |                                                              |
| `monto_aprobado`         | `MONTO APROBADO`               | decimal |  No   |                                                              |
| `monto_remesa_1`         | `MONTO 1° REMESA`              | decimal |  No   |                                                              |
| `fecha_remesa_1`         | `FECHA DE LA TRANSFERENCIA`    |    date |  No   |                                                              |
| `monto_remesa_2`         | `MONTO 2° REMESA`              | decimal |  No   |                                                              |
| `fecha_remesa_2`         | `FECHA DE LA TRANSFERENCIA.1`  |    date |  No   |                                                              |
| `monto_remesa_3`         | `MONTO 3° REMESA`              | decimal |  No   |                                                              |
| `fecha_remesa_3`         | `FECHA DE LA TRANSFERENCIA.2`  |    date |  No   |                                                              |
| `monto_rendido_aprobado` | `MONTO RENDIDO (aprobado RTF)` | decimal |  No   |                                                              |
| `monto_reintegrado`      | `MONTO REINTEGRADO`            | decimal |  No   |                                                              |
| `total_rendido`          | `TOTAL RENDIDO`                | decimal |  No   |                                                              |
| `saldo`                  | `SALDO`                        | decimal |  No   | Muy incompleto; no asumir 0.                                 |
| `observaciones`          | `OBSERVACIONES`                |  string |  No   |                                                              |
| `saldo_arrastre_2026`    | `SALDO ARRASTRE 2026`          | decimal |  No   | Campo clave para continuidad.                                |

## 3.2 Cartera Programas 2026

**Tabla**: `cartera_programa_2026`
**Origen**: `CARTERA PROGRAMAS 2026`
**Clave**: `codigo_bip` (puede ser NULL en filas de agrupación)

Campos:

* `codigo_bip` (string, nullable)
* `programa` (string)
* `institucion` (string) ← viene como `INTITUCIÓN`
* `monto_estimado` (decimal)
* `contraparte` (string, PII alta si persona)
* `acta_pertinencia` (bool o enum SI/NO)
* `estado_avance` (string/enum)
* `programacion_remesa_2026` (decimal o string si es texto mixto)
* `observaciones` (string; suele venir vacío)

---

# 4) Otras iniciativas de inversión + Participación Ciudadana

## 4.1 Otras iniciativas de inversión

**Tabla**: `otra_iniciativa_inversion`
**Origen**: `OTRAS INICIATIVAS DE INVERSIÓN`
**Clave**: `codigo_bip`

Campos (principales):

* `codigo_bip` (string, requerido)
* `nombre_proyecto` (string)
* `comuna` (string)
* `unidad_ejecutora` (string)
* `rut_institucion` (string)
* `financiamiento` (string/enum)
* `beneficiarios` (int o string si viene texto)
* `anio` (int)
* `rate` (string/enum)
* `estado` (string/enum)
* `enlace` (string/url)
* `division` (string)
* `monto_aprobado` (decimal)
* `convenio` (string/enum)
* `observaciones` (string)

## 4.2 Participación ciudadana (registro de eventos)

**Tabla**: `participacion_ciudadana_evento`
**Origen**: `PARTICIPACIÓN CIUDADANA`
**Grano**: 1 fila = 1 evento/acta asociada a un BIP
**Clave**: `evento_id` (sugerido: hash o concatenación `codigo_bip+fecha+lugar`)

Campos:

* `referente` (string, PII media)
* `codigo_bip` (string, requerido)
* `nombre_iniciativa` (string)
* `unidad_ejecutora` (string)
* `fecha` (date)
* `asistencia` (string o int según contenido real)
* `division` (string)
* `lugar` (string)
* `organizacion_firmante` (string, PII posible)
* `representante_legal` (string, PII alta)
* `observaciones` (string)

---

# 5) “Crosswalk” de nombres (normalización de columnas problemáticas)

Usa estas equivalencias para consolidar:

* `RECIBIÓ TRANSFERENCIA` → `fecha_transferencia` (no es booleano)
* `MONTO TRANFERIDO` / `MONTO TRANFERIDO ` → `monto_transferido`
* `CODIGO` / `CÓDIGO` / `Unnamed: 0` → `codigo_8pct`
* `DETALLE OBSERVACIONES` / `DETALLE OBSERVACIÓN` / `<<<<<` → `detalle_observacion`
* ` ESTADO EJECUCIÓN 2024` (con espacio) → `estado_ejecucion_2024`
* `INTITUCIÓN` → `institucion`

---

# 6) Validaciones mínimas recomendadas (para control de calidad)

## FNDR 8%

* `codigo_8pct` **único** en `fnrd8_iniciativa` por fondo.
* `rut_institucion` válido (regex simple) y no vacío cuando exista institución.
* Si `fecha_transferencia` no nula ⇒ `monto_transferido` debería no ser nulo y > 0.
* Si `rendicion_a_tiempo = SI` y está en `fnrd8_inhabilitada` o `fnrd8_sin_rendir` ⇒ marcar inconsistencia.
* Campos de fecha: si contienen texto, mover a observación y dejar fecha NULL.

## BIP

* `codigo_bip` único en `programa_social_bip` y `otra_iniciativa_inversion`.
* En `participacion_ciudadana_evento`, permitir repetición de BIP (evento-nivel).

---