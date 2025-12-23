# estructura legacy
---

## 1) Estructura global de la planilla

### 1.1 Hojas existentes y lógica de organización

La planilla está compuesta por **7 hojas**:

* **Grupo “31” (3 hojas)**

  * `31 Avan. y Adj..csv`
  * `31 Lic. y Con..csv`
  * `31 Para., Reeva. y Ter..csv`

* **Grupo “Fril” (3 hojas)**

  * `Fril Avan. y Adj..csv`
  * `Fril Lic. y Con..csv`
  * `Fril Para., Reeva. y Ter..csv`

* **Resumen (1 hoja)**

  * `Total.csv`

**Patrón estructural:**
La planilla está organizada como una **matriz Fuente × Etapa**:

* **Fuente**: `31` vs `Fril` (dos “bolsones” o líneas presupuestarias distintas; no comparten códigos entre sí).
* **Etapa/Estado agrupado por hoja** (según el nombre):

  * **Avan. y Adj.** (avance/adjudicación/contratación; en la práctica aparecen subestados como AVANCE, ADJUDICACIÓN y/o CONTRATACIÓN)
  * **Lic. y Con.** (licitación/convenio/contratación; aparecen estados LICITACIÓN/CONVENIO y subestados PRIMERA/SEGUNDA/TERCERA, FIRMADO, etc.)
  * **Para., Reeva. y Ter.** (paralización/reevaluación/término anticipado)

> En términos de diseño, estas hojas son **vistas/filtros** de un mismo universo conceptual: **“Iniciativas/Proyectos” con saldos por año**.

---

## 2) Resumen cuantitativo del conjunto

### 2.1 Volumen y totales globales (detalle, sin considerar filas de totales por hoja)

* **Filas de detalle totales (todas las hojas “operativas”)**: **167**
* **Códigos de iniciativa únicos (proyectos únicos)**: **137**
* **Saldo total 2026 (todas las fuentes)**: **$ 73,284,517**
* **Saldo total 2027 (solo fuente 31)**: **$ 20,643,831**

### 2.2 Resumen por hoja (detalle + saldos agregados)

> Importante: **cada hoja operativa incluye 1 fila final “TOTAL”** (sin comuna/código/nombre; solo trae suma(s) de saldo). Las cifras que muestro en la tabla de abajo corresponden a la suma de las filas de detalle (y coincide con la fila total de cada hoja).

| Hoja (CSV)                    | Fuente | Categoría      | Filas detalle | Códigos únicos | Total Saldo 2026 | Total Saldo 2027 |
| ----------------------------- | -----: | -------------- | ------------: | -------------: | ---------------: | ---------------: |
| Fril Avan. y Adj..csv         |   Fril | Avance/Adj     |            39 |             39 |      $ 4,983,949 |                - |
| Fril Lic. y Con..csv          |   Fril | Lic/Con        |            37 |             36 |      $ 5,582,451 |                - |
| Fril Para., Reeva. y Ter..csv |   Fril | Para/Reeva/Ter |            19 |             19 |      $ 1,467,922 |                - |
| 31 Avan. y Adj..csv           |     31 | Avance/Adj     |            48 |             26 |     $ 52,671,986 |      $ 5,984,755 |
| 31 Lic. y Con..csv            |     31 | Lic/Con        |            22 |             18 |      $ 8,208,395 |     $ 14,659,076 |
| 31 Para., Reeva. y Ter..csv   |     31 | Para/Reeva/Ter |             2 |              2 |        $ 369,814 |                - |

### 2.3 Resumen por fuente (coincide con `Total.csv`)

* **Fril**: 95 filas de detalle, 94 códigos únicos, total 2026 **$ 12,034,322**, 2027 **-**
* **31**: 72 filas de detalle, 43 códigos únicos, total 2026 **$ 61,250,195**, total 2027 **$ 20,643,831**

---

## 3) Diccionario de campos (modelo de datos)

### 3.1 Campos principales (presentes en casi todas las hojas)

Estos campos describen una **iniciativa/proyecto** y su situación:

* **Comuna** *(texto)*
  Ej.: `CHILLÁN`, `COIHUECO`, `ÑIQUÉN`

  * **Observación:** valores en mayúsculas; hay tildes/ñ en algunas comunas.

* **Código** *(numérico, pero en CSV se lee como float por presencia de NA en la fila total)*
  Ej.: `40055833`, `30119286`

  * **Rol:** identificador “central” de la iniciativa.
  * **Recomendación técnica:** manejar como **entero o string** (sin decimales) para evitar `40055833.0`.

* **Nombre Iniciativa** *(texto)*
  Nombre descriptivo del proyecto (mayúsculas, con tildes).

* **Unidad Técnica** *(texto)*
  Ej.: `MUNICIPIO`, `SERVIU`, `DIRECCIÓN DE ARQUITECTURA`, `CARABINEROS`, `UBB`, `ASOCIACION PUNILLA`.

* **Item Presupuestario** *(texto con patrón de códigos)*
  Ej. en fuente 31: `31.02.004`, `31.02.002`, etc.
  Ej. en fuente Fril: `33.03.125`

  * **No aparece en `Fril Avan. y Adj..csv`**, pero sí en las otras 2 hojas Fril.

* **Estado Iniciativa** *(texto categórico)*
  Valores detectados: `EJECUCIÓN`, `LICITACIÓN`, `CONVENIO`.

* **Sub-Estado Iniciativa** *(texto categórico)*
  Valores detectados (conjunto completo):
  `AVANCE`, `ADJUDICACIÓN`, `CONTRATACIÓN`, `PRIMERA`, `SEGUNDA`, `TERCERA`, `FIRMADO`, `SIN FIRMAR`, `REEVALUACIÓN`, `PARALIZACIÓN`, `TÉRMINO ANTICIPADO CONTRATO`, `RESCILIACIÓN CONVENIO`, `RESCILIACIÓN CONTRATO`.

* **Saldo 2026 / Saldo 2027** *(texto con formato moneda)*
  Formato típico: `"$ 9,422,880"` o `"$ -"`

  * En **Fril** solo existe **Saldo 2026** (coherente con el total 2027 “-”).
  * En **31** existen **Saldo 2026** y **Saldo 2027**.

### 3.2 Particularidades de formato (calidad)

* **Encabezados con espacios** (por ejemplo `' Comuna '`): en uso analítico conviene **normalizar** (strip) para evitar errores al programar.
* **Saldos guardados como texto**: para cálculos, se requiere parseo (quitar `$`, espacios y separadores de miles).
* **Fila total “sin etiquetas”**: todas las hojas operativas tienen una fila final con **celdas vacías en columnas clave** y solo montos en saldo(s).

---

## 4) Análisis hoja por hoja

### 4.1 `31 Avan. y Adj..csv`

**Estructura**

* **Columnas:** 9 (incluye `Item Presupuestario` y `Saldo 2027`)
* **Filas totales:** 49

  * **48 filas de detalle**
  * **1 fila final de total** (sin comuna/código/nombre)

**Contenido y distribución**

* **Estado Iniciativa:** 100% `EJECUCIÓN` (en detalle)
* **Sub-Estado Iniciativa:**

  * `AVANCE`: 47 filas
  * `CONTRATACIÓN`: 1 fila
    (No aparece `ADJUDICACIÓN` en esta hoja, aunque el nombre la menciona.)
* **Unidades técnicas:** 5 distintas (predomina `MUNICIPIO`, también `UBB`, `SERVIU`, `CARABINEROS`, `DIRECCIÓN DE ARQUITECTURA`).
* **Item Presupuestario (31.02.xxx):** aparecen varios (31.02.002, .003, .004, .005, .006, .007).

**Totales**

* **Total Saldo 2026:** `$ 52,671,986`
* **Total Saldo 2027:** `$ 5,984,755`

**Calidad y observaciones**

* **Granularidad no 1:1 por proyecto**:
  Hay **48 filas** pero solo **26 códigos únicos**. Esto indica que un mismo proyecto puede estar **desagregado en varias líneas presupuestarias** (p. ej. por `Item Presupuestario`).
* **Caso puntual de “doble línea” con misma llave compuesta**:
  El **código 40028237** aparece **dos veces con el mismo `Item Presupuestario` (31.02.002) y mismo estado/subestado**, pero con montos distintos.

  * Esto sugiere que falta un campo adicional para distinguir “componentes”/“cuotas” o que hay una fragmentación que podría consolidarse.

---

### 4.2 `31 Lic. y Con..csv`

**Estructura**

* **Columnas:** 9 (incluye `Saldo 2027`)
* **Filas totales:** 23

  * **22 detalle**
  * **1 total**

**Contenido**

* **Estado Iniciativa (detalle):**

  * `CONVENIO`: 13
  * `LICITACIÓN`: 8
  * `EJECUCIÓN`: 1 (caso “ADJUDICACIÓN” dentro de esta hoja)
* **Subestados presentes:** `FIRMADO`, `REEVALUACIÓN`, `PRIMERA`, `SIN FIRMAR`, `SEGUNDA`, `TERCERA`, `ADJUDICACIÓN`.

**Totales**

* **Saldo 2026:** `$ 8,208,395`
* **Saldo 2027:** `$ 14,659,076`

**Calidad y observaciones**

* **Desagregación por item:** 22 filas y 18 códigos únicos (hay proyectos repartidos en varios ítems).
* **Coherencia interna:** para esta hoja, la combinación `(Código, Item Presupuestario)` es **única** (no hay duplicados en esa llave), lo que facilita el modelado.
* **Heterogeneidad “de etapa” dentro de la hoja:** aparece 1 registro con `Estado = EJECUCIÓN` y `Sub-Estado = ADJUDICACIÓN`, lo que semánticamente podría convivir también con una hoja tipo “Avan/Adj” (esto no es necesariamente un error, pero sí indica que la clasificación por pestaña no es estricta al 100%).

---

### 4.3 `31 Para., Reeva. y Ter..csv`

**Estructura**

* **Columnas:** 9 (incluye `Saldo 2027`)
* **Filas totales:** 3

  * **2 detalle**
  * **1 total**

**Contenido**

* **Estado:** 100% `EJECUCIÓN`
* **Sub-Estado:** 100% `PARALIZACIÓN`
  (Aunque el nombre menciona Reevaluación y Término, en estos datos no hay esos casos en “31”.)

**Totales**

* **Saldo 2026:** `$ 369,814`
* **Saldo 2027:** `$ -` (0)

**Calidad**

* Sin faltantes en detalle; la hoja es muy pequeña y consistente.

---

### 4.4 `Fril Avan. y Adj..csv`

**Estructura**

* **Columnas:** 7

  * No incluye `Item Presupuestario`
  * No incluye `Saldo 2027` (solo 2026)
* **Filas totales:** 40

  * **39 detalle**
  * **1 total**

**Contenido**

* **Estado:** 100% `EJECUCIÓN`
* **Sub-Estado:**

  * `AVANCE`: 28
  * `ADJUDICACIÓN`: 10
  * `CONTRATACIÓN`: 1
* **Unidad Técnica:** 1 única (`MUNICIPIO`) en todos los registros.

**Totales**

* **Saldo 2026:** `$ 4,983,949`

**Calidad y observaciones**

* Estructura consistente con “Fril” (mismos campos salvo el `Item Presupuestario`).
* Si se desea unificar modelos entre hojas Fril, esta hoja podría incorporar `Item Presupuestario` como constante (en las otras hojas Fril es 33.03.125), o dejarlo nulo pero documentado.

---

### 4.5 `Fril Lic. y Con..csv`

**Estructura**

* **Columnas:** 8 (incluye `Item Presupuestario`, no incluye 2027)
* **Filas totales:** 38

  * **37 detalle**
  * **1 total**

**Contenido**

* **Estado (detalle):**

  * `LICITACIÓN`: 18
  * `CONVENIO`: 18
  * `EJECUCIÓN`: 1
* **Sub-Estado:** `PRIMERA`, `SEGUNDA`, `FIRMADO`, `REEVALUACIÓN`, `CONTRATACIÓN`, `ADJUDICACIÓN`, `RESCILIACIÓN CONVENIO`, `RESCILIACIÓN CONTRATO`.
* **Item Presupuestario:** prácticamente todo `33.03.125` (es el identificador presupuestario típico en Fril en estas hojas).

**Totales**

* **Saldo 2026:** `$ 5,582,451`

**Calidad y observaciones**

* **Duplicado exacto detectado:**
  El **código 40058376** aparece **dos veces con todos los campos iguales** (incluido el mismo monto `$ 119,533`).

  * Si este duplicado es involuntario, **infla** el total de la hoja (y por arrastre el total Fril 2026) en `$ 119,533`.
  * Recomendación: validar si son dos registros distintos (y falta un campo diferenciador) o si es un duplicado a eliminar.

---

### 4.6 `Fril Para., Reeva. y Ter..csv`

**Estructura**

* **Columnas:** 8 (incluye `Item Presupuestario`, no incluye 2027)
* **Filas totales:** 20

  * **19 detalle**
  * **1 total**

**Contenido**

* **Estado:** 100% `EJECUCIÓN`
* **Sub-Estado:**

  * `PARALIZACIÓN`: 13
  * `REEVALUACIÓN`: 5
  * `TÉRMINO ANTICIPADO CONTRATO`: 1
* **Unidad Técnica:** 1 (`MUNICIPIO`)

**Totales**

* **Saldo 2026:** `$ 1,467,922`

**Calidad**

* Hoja consistente; subestados alineados con el nombre de la pestaña.

---

### 4.7 `Total.csv`

**Rol funcional**

* Es una hoja de **resumen financiero** que consolida saldos por año para **Fril** y **31**, más un total general.

**Estructura real del CSV**

* 3 columnas: `M$`, `Unnamed: 1`, `Unnamed: 2`
* 4 filas:

  * Fila 1 (dentro del dato) actúa como “encabezado lógico”: `Ítem | 2026 | 2027`
  * Filas siguientes: `Fril`, `31`, `Total`

**Contenido**

* `Fril` 2026: `12,034,322` ; 2027: `-`
* `31` 2026: `61,250,195` ; 2027: `20,643,831`
* `Total` 2026: `73,284,517` ; 2027: `20,643,831`

**Coherencia con hojas de detalle**

* Los totales de esta hoja **coinciden exactamente** con la suma de:

  * Las 3 hojas Fril (2026)
  * Las 3 hojas 31 (2026 y 2027)

**Calidad**

* Desde el punto de vista “tabular”, no es un formato “limpio”:

  * Los encabezados quedaron como “Unnamed”
  * El “encabezado real” está en la primera fila
  * El `M$` funciona más como **unidad/etiqueta** que como nombre de columna
* Aun así, como **resumen humano** es claro.

---

## 5) Relaciones, jerarquías y claves (modelo conceptual)

### 5.1 Entidad central: Iniciativa / Proyecto

El conjunto modela una entidad principal:

**Iniciativa** (identificada por `Código`)

* Atributos: `Comuna`, `Nombre Iniciativa`, `Unidad Técnica`
* Clasificaciones:

  * `Fuente` (implícita por hoja: Fril vs 31)
  * `Item Presupuestario` (explícito en casi todas)
  * `Estado Iniciativa` y `Sub-Estado Iniciativa`

**Medidas financieras**

* `Saldo 2026` (todas)
* `Saldo 2027` (solo fuente 31)

### 5.2 Jerarquía implícita en la planilla

Se observa una jerarquía natural:

**Fuente (Fril / 31)**
→ **Grupo por etapa (Avan/Adj, Lic/Con, Para/Reeva/Ter)**
→ **Iniciativa (Código)**
→ **Línea presupuestaria / desagregación (a veces por Item Presupuestario)**
→ **Saldo por año**

### 5.3 Claves y granularidad

* En **Fril**, el modelo está cercano a “1 fila = 1 proyecto” (salvo el duplicado detectado).
* En **31**, **Código NO es clave única de fila**:

  * Un mismo código se repite en varias filas (por distintos ítems).
  * Incluso puede aparecer en **más de una hoja** (intersección entre `31 Avan...` y `31 Lic...` para 3 códigos: **40015344, 40028237, 40029660**).
  * Implicación: la “etapa por hoja” no es estrictamente exclusiva por código; puede estar **fragmentada por ítem/contrato/parte**.

**Recomendación de clave para uso analítico (fila de detalle):**

* Como mínimo: `(Fuente, Código, Item Presupuestario, Estado Iniciativa, Sub-Estado Iniciativa)`
* Y dado el caso del código 40028237 (misma combinación repetida), si se requiere unicidad absoluta, faltaría un campo adicional tipo `Componente`, `Contrato`, `Partida`, `Correlativo`, etc.

---

## 6) Coherencia y calidad de datos (evaluación crítica)

### 6.1 Fortalezas (buena calidad)

* **Completitud en filas de detalle:** no hay nulos en campos clave dentro de los registros de detalle (comuna/código/nombre/estado/subestado/saldo).
* **Dominios categóricos acotados y consistentes:** estados y subestados usan valores repetibles y coherentes con la lógica de seguimiento.
* **Formato monetario consistente:** `"$ n,nnn"` o `"$ -"` (en todas las hojas operativas).
* **Coherencia de totales:**

  * La fila total de cada hoja coincide exactamente con la suma de sus filas de detalle.
  * La hoja `Total.csv` coincide con la suma de las hojas por fuente.

### 6.2 Debilidades / riesgos

1. **Fila de total dentro de la misma tabla (sin etiqueta)**

   * Mezcla datos de distinto nivel (detalle vs agregado).
   * Riesgo alto al importar: puede romper tipado (por eso `Código` cae como float) y distorsionar análisis.

2. **Tipado inadecuado para análisis**

   * `Código` llega como float (`400xxxxx.0`) por la fila de totales.
   * `Saldo` llega como texto; requiere parseo.

3. **Inconsistencia de esquema entre hojas**

   * `Fril Avan. y Adj..csv` no tiene `Item Presupuestario` (sí existe en otras hojas Fril).
   * Fril no trae `Saldo 2027`, pero esto es consistente con el total 2027 “-”; aun así, dificulta un modelo uniforme (se resuelve agregando columna 2027 con 0/NA).

4. **Duplicado exacto en Fril Lic/Con**

   * Probable error de duplicación (código 40058376). Requiere validación.

5. **Granularidad incompleta en 31**

   * El mismo código puede aparecer en distintas hojas y múltiples filas por ítem, y en un caso con la misma combinación de campos.
   * Esto sugiere que el “registro” no está completamente identificado por los campos presentes.
