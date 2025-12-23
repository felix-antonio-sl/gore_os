# Diccionario

## 0) Alcance y supuestos (desde los CSV cargados)

**Hojas/archivos y forma (filas×columnas):**

* REBAJA 5%.csv (15×10)
* MODIFICACIÓN N°1.csv (15×10)
* MODIFICACIÓN N°2.csv (41×12)
* MODIFICACIÓN N°3.csv (31×12)
* MODIFICACIÓN N°3 SIN EFECTO.csv (21×8)
* MODIFICACIÓN N°4.csv (39×11)
* MODIFICACIÓN N°5 SIC.csv (22×11)
* REBAJA FUNC. N°6 sin efecto.csv (14×11)
* MODIFICACIÓN Nº7.csv (14×10)
* MODIFICACIÓN Nº9.csv (32×14)

**Variantes estructurales observadas:**

* **Columna “marcador” (C/M)**: aparece en N°2, N°3, N°4, N°5 SIC, Rebaja Func N°6 sin efecto, Nº9.
* **Columna “OBS”**: aparece en N°2 y N°3.
* **Múltiples columnas de modificación**: **Nº9** incluye “MODIFICACIÓN N°9” y “MODIFICACIÓN N°4”.
* **Errores `#REF!`**: presentes en varias hojas (especialmente Nº9, y también N°4/N°5 SIC/Rebaja Func N°6 sin efecto, etc.).
* **Convención de signo no uniforme**: en muchas filas el valor de “MODIFICACIÓN” viene como **magnitud positiva**, pero el cambio real se ve en `PPTO_POST − PPTO_PRE` (puede ser negativo o positivo). Por eso se define un campo derivado estándar.

---

# 1) Modelo lógico recomendado (3 niveles)

1. **sheet (hoja/documento)**: metadatos del archivo/hoja y su “estado”.
2. **block (bloque)**: INGRESOS / GASTOS (cuando existan; algunas hojas solo traen un bloque implícito).
3. **line (línea presupuestaria)**: filas jerárquicas SUBT/ITEM/ASIG + montos.

> En la práctica puedes materializarlo en 2 tablas (sheet y line) y manejar block como un atributo en line.

---

# 2) Diccionario: tabla `sheet` (metadatos de hoja)

| Campo                  |          Tipo | Oblig. | Descripción                                                                                                                                       | Reglas / Observaciones                                 |
| ---------------------- | ------------: | :----: | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `sheet_id`             |        string |   Sí   | Identificador único interno (uuid o hash).                                                                                                        | Útil para trazabilidad.                                |
| `sheet_file_name`      |        string |   Sí   | Nombre del CSV (ej. “MODIFICACIÓN N°2.csv”).                                                                                                      | Fuente primaria para “estado” y “tipo”.                |
| `sheet_title`          |        string |   No   | Título capturado desde filas superiores (ej. “MODIFICACIÓN PRESUPUESTARIA N°02”).                                                                 | Puede no estar o estar inconsistente entre hojas.      |
| `program_name`         |        string |   No   | Nombre del programa (ej. “PROGRAMA DE INVERSIÓN REGIONAL”).                                                                                       | Puede venir con o sin año.                             |
| `program_year`         |           int |   No   | Año del programa si aparece (ej. 2025).                                                                                                           | Extraído desde texto (no siempre presente).            |
| `sheet_date_text`      |        string |   No   | Fecha si aparece como texto (ej. “21 de marzo de 2024”).                                                                                          | Normalizar luego a fecha si aplica.                    |
| `movement_type`        |          enum |   Sí   | Tipo de movimiento: `MODIFICACION` / `REBAJA`.                                                                                                    | Derivar por nombre de hoja (p.ej., contiene “REBAJA”). |
| `sheet_status`         |          enum |   Sí   | Estado: `VIGENTE` / `SIN_EFECTO`.                                                                                                                 | Derivar por nombre (contiene “SIN EFECTO”).            |
| `currency_unit`        |        string |   Sí   | Unidad declarada (en estos CSV: `M$`).                                                                                                            | Tratar como constante del dataset.                     |
| `mod_columns_declared` | array<string> |   Sí   | Lista de columnas de modificación declaradas en el encabezado (ej. `[“MODIFICACIÓN N°2 M$”]` o `[“MODIFICACIÓN N°9 M$”, “MODIFICACIÓN N°4 M$”]`). | En Nº9 hay 2 modificaciones en un mismo archivo.       |
| `has_block_labels`     |          bool |   Sí   | Indica si la hoja trae filas de total con “INGRESOS”/“GASTOS”.                                                                                    | Algunas hojas no las traen explícitas.                 |
| `notes_quality`        |        string |   No   | Nota libre de calidad (ej. “presenta #REF!” / “múltiples columnas de modificación”).                                                              | Útil para auditoría.                                   |

---

# 3) Diccionario: tabla `line` (líneas presupuestarias normalizadas)

## 3.1. Identificación y jerarquía

| Campo           |   Tipo | Oblig. | Descripción                                                       | Reglas / Observaciones                                                                                                                                                                      |
| --------------- | -----: | :----: | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sheet_id`      | string |   Sí   | FK a `sheet`.                                                     | Une línea con su hoja.                                                                                                                                                                      |
| `row_index_raw` |    int |   Sí   | Índice de fila en el CSV original (0-based).                      | Permite reconstruir origen.                                                                                                                                                                 |
| `block_type`    |   enum |   No   | `INGRESOS` / `GASTOS` / `NULL`.                                   | Se obtiene desde filas total “INGRESOS/GASTOS” y se “arrastra hacia abajo” hasta el siguiente bloque. Si la hoja no trae bloques, puede quedar NULL o inferirse como GASTOS según contexto. |
| `line_level`    |   enum |   Sí   | Nivel jerárquico: `TOTAL_BLOQUE`, `SUBT`, `ITEM`, `ASIG`, `OTRO`. | Derivado: si solo hay SUBT→ SUBT; si hay ITEM; si hay ASIG; si denominación es “INGRESOS/GASTOS” → TOTAL_BLOQUE.                                                                            |
| `subt_code`     | string |   No   | Código subtítulo (ej. “13”, “24”, “31”).                          | Guardar como string (puede venir vacío en filas hijas; luego fill-down).                                                                                                                    |
| `item_code`     | string |   No   | Código ítem (ej. “03”, “01”).                                     | Guardar como string para preservar ceros a la izquierda. Fill-down dentro del subtítulo.                                                                                                    |
| `asig_code`     | string |   No   | Código asignación (ej. “006”, “999”, “491”).                      | String; puede venir vacío en niveles SUBT/ITEM.                                                                                                                                             |
| `cm_flag`       |   enum |   No   | Marcador observado: `C`, `M` (u otros).                           | No está en todas las hojas. Si no existe, NULL. Importante si duplica ASIG.                                                                                                                 |
| `denominacion`  | string |   No   | Nombre/descripción (concepto).                                    | Puede venir vacío en filas de continuidad o con `#REF!` en hojas con errores.                                                                                                               |
| `obs`           | string |   No   | Observación textual (ej. “FONDO PARA LA PRODUCTIVIDAD”).          | Solo aparece en algunas hojas.                                                                                                                                                              |

## 3.2. Montos (tal como vienen + normalizados)

> Unidad: **M$** (según encabezados).
> Los valores vienen como texto con separadores “,” y a veces espacios; pueden venir negativos; pueden venir `#REF!`.

| Campo                     |    Tipo | Oblig. | Descripción                                                            | Reglas / Observaciones                                                                                                        |
| ------------------------- | ------: | :----: | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `amount_initial_raw`      |  string |   No   | “Distribución inicial M$” como texto.                                  | Puede estar vacío en algunas filas.                                                                                           |
| `amount_pre_raw`          |  string |   No   | “PPTO vigente con modificaciones anteriores M$” como texto.            | Puede estar `#REF!`.                                                                                                          |
| `amount_post_raw`         |  string |   No   | “PPTO vigente (incluye presente modificación) M$” como texto.          | Puede estar `#REF!`.                                                                                                          |
| `amount_mod_raw_map`      |  object |   No   | Mapa `{"MODIFICACIÓN N°X M$": "<texto>"}`; soporta múltiples columnas. | En Nº9 puede incluir N°9 y N°4.                                                                                               |
| `amount_initial`          | integer |   No   | `amount_initial_raw` parseado (sin comas/espacios).                    | `#REF!` → NULL.                                                                                                               |
| `amount_pre`              | integer |   No   | `amount_pre_raw` parseado.                                             | `#REF!` → NULL.                                                                                                               |
| `amount_post`             | integer |   No   | `amount_post_raw` parseado.                                            | `#REF!` → NULL.                                                                                                               |
| `amount_mod_declared_sum` | integer |   No   | Suma de todas las modificaciones declaradas (si hay varias columnas).  | Parsear cada una y sumar (NULL-safe).                                                                                         |
| `amount_mod_signed`       | integer |   No   | **Cambio real estándar** = `amount_post − amount_pre`.                 | Este es el campo recomendado para análisis, porque el “mod declarado” a veces viene como magnitud positiva aunque sea rebaja. |

## 3.3. Control de calidad por fila

| Campo             |   Tipo | Oblig. | Descripción                                                                                | Reglas / Observaciones                   |
| ----------------- | -----: | :----: | ------------------------------------------------------------------------------------------ | ---------------------------------------- |
| `has_ref_error`   |   bool |   Sí   | Indica si la fila contiene `#REF!` en algún campo crítico.                                 | `#REF!` en denominación o montos → TRUE. |
| `is_header_noise` |   bool |   Sí   | Marca filas que son rótulos/encabezados incrustados (“GOBIERNO REGIONAL…”, “SUBT.”, etc.). | Se filtran fuera del dataset analítico.  |
| `parse_warnings`  | string |   No   | Mensajes de warning (p.ej. “monto no parseable”).                                          | Para auditoría.                          |

---

# 4) Reglas de normalización (las que conviene dejar por escrito)

## 4.1. Reglas para “fill-down” jerárquico

* Si `subt_code` está vacío en una fila de detalle, **hereda** el último `subt_code` no vacío hacia arriba (hasta cambio).
* Si `item_code` está vacío en una fila de detalle, hereda el último `item_code` **dentro del mismo subtítulo**.
* `asig_code` solo debe existir en líneas `ASIG`.

## 4.2. Regla estándar de signo (clave)

* El valor de la columna “MODIFICACIÓN …” **no es confiable como signo** a nivel global.
* Campo oficial para análisis:
  **`amount_mod_signed = amount_post − amount_pre`**

  * Si da negativo → rebaja real
  * Si da positivo → aumento real
  * Si pre/post son NULL → no se puede calcular.

## 4.3. Parseo numérico (texto → entero)

* Limpieza: `strip()`, eliminar espacios internos, eliminar separadores `,`.
* Manejar negativos con `-`.
* `""` o `#REF!` → NULL.

## 4.4. Identificación de filas “ruido”

Marcar como `is_header_noise = TRUE` filas cuyo contenido corresponda a:

* Títulos (“MODIFICACIÓN PRESUPUESTARIA…”, “PROGRAMA…”)
* Rótulos institucionales (“GOBIERNO REGIONAL…”, “INVERSIÓN REGIONAL…”)
* Encabezados de tabla (“SUBT.”, “DENOMINACIONES”, etc.)
* Notas tipo “4 = (2)+(3)”

---

# 5) Catálogos mínimos (valores esperados)

## 5.1. `movement_type`

* `MODIFICACION`
* `REBAJA`

## 5.2. `sheet_status`

* `VIGENTE`
* `SIN_EFECTO`

## 5.3. `block_type`

* `INGRESOS`
* `GASTOS`
* `NULL` (si no se declara)

## 5.4. `cm_flag` (observado)

* `C`
* `M`
* `NULL` (si no existe)
