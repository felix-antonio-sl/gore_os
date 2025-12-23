Sí — este es el **diccionario de datos del modelo unificado** (archivo `consolidado_unificado.csv` / hoja “Consolidado” del Excel). Incluye **granularidad**, **llave recomendada**, **definición de campos**, **dominios** y **reglas de calidad**.

---

## Alcance y granularidad

**Dataset:** Consolidado de 6 hojas operativas (todas excepto `Total.csv`), **excluyendo** las filas “TOTAL” internas de cada hoja.

**Grano (nivel de detalle):**
**1 fila = 1 línea de seguimiento financiero** de una iniciativa, identificada por su **Código**, y potencialmente desagregada por **Item Presupuestario** y/o **Estado/Sub-Estado**.

> En fuente **31**, un mismo Código puede aparecer varias veces (desagregación real). En **Fril**, normalmente es 1 fila por Código, salvo casos de duplicación.

**Llave técnica recomendada (no incluida como columna):**

* `Fuente + Código + (Item Presupuestario) + Estado Iniciativa + Sub-Estado Iniciativa + Hoja`

  * Nota: esto **no garantiza unicidad absoluta** en todos los casos (hay al menos un caso donde se repite la misma combinación dentro de una hoja), por lo que si necesitas unicidad estricta conviene agregar un `ID_Línea`/`Correlativo`.

---

## Diccionario de campos (16 columnas)

> Tipos según el consolidado. “Obligatorio” se refiere a filas de **detalle**.

| Campo                                             | Tipo                | Obligatorio | Descripción                                                                          | Fuente / Derivación                                                   | Reglas / Validaciones                                                                                                            | Ejemplo                |
| ------------------------------------------------- | ------------------- | ----------: | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **Fuente**                                        | texto               |          Sí | Identifica el bloque/origen presupuestario del registro.                             | Derivada del nombre de la hoja CSV de origen.                         | Dominio cerrado: `31`, `Fril`.                                                                                                   | `31`                   |
| **Categoría**                                     | texto               |          Sí | Macro-etapa operacional (según pestaña).                                             | Derivada del nombre de la hoja.                                       | Dominio cerrado: `Avan y Adj`, `Lic y Con`, `Para, Reeva y Ter`.                                                                 | `Lic y Con`            |
| **Hoja**                                          | texto               |          Sí | Nombre exacto del CSV/origen.                                                        | Origen directo.                                                       | Debe ser uno de los 6 nombres esperados.                                                                                         | `Fril Lic. y Con..csv` |
| **Comuna**                                        | texto               |          Sí | Comuna asociada a la iniciativa.                                                     | Origen directo.                                                       | Dominio observado: 22 comunas (ver lista abajo). Mayúsculas; conservar tildes/ñ.                                                 | `CHILLÁN`              |
| **Código**                                        | entero              |          Sí | Identificador numérico de la iniciativa/proyecto.                                    | Origen directo (normalizado a entero).                                | Debe ser numérico y >0. Ojo: en origen venía como número “sucio” por filas TOTAL; aquí quedó limpio.                             | `40055833`             |
| **Nombre Iniciativa**                             | texto               |          Sí | Nombre descriptivo de la iniciativa/proyecto.                                        | Origen directo.                                                       | No vacío. Recomendable estandarizar espacios múltiples.                                                                          | `CONSTRUCCIÓN ...`     |
| **Unidad Técnica**                                | texto               |          Sí | Organismo ejecutor / contraparte técnica.                                            | Origen directo.                                                       | Dominio observado: 6 valores (ver lista abajo).                                                                                  | `MUNICIPIO`            |
| **Item Presupuestario**                           | texto (nullable)    |     Depende | Ítem presupuestario asociado a la línea.                                             | Origen directo cuando existe.                                         | Nullable **solo** en `Fril Avan. y Adj..csv` (allí no viene en origen). Dominio observado: `31.02.002`…`31.02.007`, `33.03.125`. | `31.02.004`            |
| **Estado Iniciativa**                             | texto               |          Sí | Estado principal del ciclo (macroestado).                                            | Origen directo.                                                       | Dominio cerrado observado: `EJECUCIÓN`, `LICITACIÓN`, `CONVENIO`.                                                                | `EJECUCIÓN`            |
| **Sub-Estado Iniciativa**                         | texto               |          Sí | Subestado operativo dentro del estado principal.                                     | Origen directo.                                                       | Dominio cerrado observado (13 valores, ver lista abajo).                                                                         | `AVANCE`               |
| **Saldo 2026**                                    | entero              |          Sí | Saldo asociado al año 2026 (unidad monetaria según origen).                          | Parseado desde texto moneda del CSV (quitando `$`, separadores, “-”). | Debe ser ≥ 0. **Unidad**: en `Total.csv` aparece “M$” (posible *miles de pesos*); conviene confirmar convención institucional.   | `9422880`              |
| **Saldo 2027**                                    | numérico (nullable) |     Depende | Saldo asociado al año 2027.                                                          | Parseado desde origen cuando existe.                                  | En **Fril** viene nulo (no reporta 2027). En **31** debe ser ≥ 0.                                                                | `0` / `14659076`       |
| **Duplicado exacto en hoja**                      | booleano            |          Sí | Marca filas idénticas (mismos campos + saldos) repetidas dentro de la misma hoja.    | Calculado.                                                            | `TRUE` si existe al menos otro registro exactamente igual en esa hoja. Útil para depurar.                                        | `TRUE`                 |
| **Duplicado clave en hoja**                       | booleano            |          Sí | Marca duplicidad según “llave sugerida” dentro de una hoja.                          | Calculado.                                                            | `TRUE` si se repite la combinación: `Hoja+Código+Item+Estado+Subestado`.                                                         | `FALSE`                |
| **Código en múltiples categorías (misma fuente)** | booleano            |          Sí | Indica si el mismo Código aparece en más de una Categoría dentro de la misma Fuente. | Calculado.                                                            | `TRUE` si el Código aparece en ≥2 categorías (p.ej. Avan y Adj y Lic y Con) bajo la misma fuente.                                | `TRUE`                 |
| **N° líneas por código (misma fuente)**           | entero              |          Sí | Cuántas filas tiene ese Código dentro de una Fuente (medida de desagregación).       | Calculado (conteo).                                                   | Entero ≥1. Útil para saber si un código es “multi-línea”.                                                                        | `3`                    |

---

## Dominios observados (valores permitidos en este set)

### Fuente

* `31`
* `Fril`

### Categoría

* `Avan y Adj`
* `Lic y Con`
* `Para, Reeva y Ter`

### Estado Iniciativa

* `EJECUCIÓN`
* `LICITACIÓN`
* `CONVENIO`

### Sub-Estado Iniciativa (13)

* `AVANCE`
* `ADJUDICACIÓN`
* `CONTRATACIÓN`
* `PRIMERA`
* `SEGUNDA`
* `TERCERA`
* `FIRMADO`
* `SIN FIRMAR`
* `REEVALUACIÓN`
* `PARALIZACIÓN`
* `TÉRMINO ANTICIPADO CONTRATO`
* `RESCILIACIÓN CONVENIO`
* `RESCILIACIÓN CONTRATO`

### Unidad Técnica (6)

* `MUNICIPIO`
* `SERVIU`
* `DIRECCIÓN DE ARQUITECTURA`
* `CARABINEROS`
* `UBB`
* `ASOCIACION PUNILLA`

### Comuna (22)

BULNES, CHILLÁN, CHILLÁN VIEJO, COBQUECURA, COELEMU, COIHUECO, EL CARMEN, NINHUE, PEMUCO, PINTO, PORTEZUELO, PUNILLA, QUILLÓN, QUIRIHUE, RÁNQUIL, SAN CARLOS, SAN FABIÁN, SAN IGNACIO, SAN NICOLÁS, TREHUACO, YUNGAY, ÑIQUÉN.

---

## Reglas de calidad sugeridas (checks)

1. **Excluir totales**: no deben existir filas con `Código` vacío (ya excluidas en el consolidado).
2. **Integridad mínima**: `Fuente, Categoría, Hoja, Comuna, Código, Nombre Iniciativa, Unidad Técnica, Estado, Sub-Estado, Saldo 2026` no nulos.
3. **Saldos no negativos**: `Saldo 2026 ≥ 0`, `Saldo 2027 ≥ 0` cuando aplica.
4. **Control de duplicados**:

   * Si `Duplicado exacto en hoja = TRUE`: revisar si es error de carga.
   * Si `Duplicado clave en hoja = TRUE`: probablemente falta un identificador de componente/contrato/partida.
5. **Coherencia de clasificación**: si `Código en múltiples categorías = TRUE`, validar si es confirmación de “multi-etapa” real o si debería estar en una sola pestaña.

