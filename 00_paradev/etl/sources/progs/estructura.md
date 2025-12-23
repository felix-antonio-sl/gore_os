# Estructura legacy

---

## 1) Visión general del Google Sheet

La planilla completa funciona como un **tablero de seguimiento administrativo/financiero** con cuatro grandes “módulos”:

1. **Concurso FNDR 8% 2024 (Vinculación con la Comunidad)**

   * Es, por lejos, el componente más grande.
   * Se estructura por **fondos/typologías** (Adulto Mayor, Cultura, Deporte, etc.), con hojas “F.*” que actúan como **listados maestros** (detalle por organización/iniciativa), y hojas “auxiliares” de **resumen** y **control** (eliminadas, habilitadas fuera de plazo, inhabilitadas, sin rendir, etc.).

2. **Asignaciones Directas 2023–2024**

   * Seguimiento de ejecución/rendición de asignaciones directas, con totales y porcentajes de rendición.

3. **Programas Sociales (seguimiento) + Cartera/Programación 2026**

   * Programas con **Código BIP**, remesas, rendiciones y saldos; y una cartera 2026 con estado de avance.

4. **Otras iniciativas de inversión + Participación Ciudadana DIDESOH**

   * Iniciativas de inversión (BIP, financiamiento, estado, convenios, links) y un registro de **eventos/actas** de participación ciudadana asociadas a iniciativas BIP.

Además, hay una hoja de **apoyo territorial** (asignación de comunas a profesionales) que sirve como “tabla de referencia” transversal.

## 2) Inventario de hojas y su rol (estructura completa)

### 8%. 2019–2023

A continuación describo **la planilla a partir del único .csv disponible** en el entorno: **`Hoja 1.csv`** (asumido como **una hoja** del Google Sheet). Si existen más .csv/hojas, la estructura global (relaciones entre hojas) podría ampliarse, pero **con lo entregado** el “libro” queda compuesto por **1 hoja / 1 tabla principal**.

---

## 1) Vista general de la planilla (estructura global)

### Hojas detectadas

* **Hoja 1** (archivo: `Hoja 1.csv`)

### Tamaño y forma

* **Filas (registros):** 3.848
* **Columnas (campos):** 17
* **Cobertura temporal (campo AÑO):** 2019–2023

### Qué representa (naturaleza del dataset)

Cada fila representa una **iniciativa financiada** (proyecto/actividad) asociada a:

* un **fondo/programa** (FONDO),
* una **institución receptora** (INSTITUCIÓN + RUT),
* un **territorio** (PROVINCIA, COMUNA),
* y un **estado contable** de la transferencia (monto transferido, rendición, reintegro, saldo pendiente),
* con responsables de seguimiento (PROFESIONAL UCR, REFERENTE TÉCNICO) y eventual marca de observación (OBSERVADO).

En términos de modelo de datos, esta hoja funciona como una **tabla “hechos”** (fact table) de transferencias/rendiciones.

---

## 2) Entidades, relaciones y jerarquías implícitas

Aunque hay una sola hoja, se observan “dimensiones” implícitas (tablas de referencia que podrían separarse):

### Entidad principal (hecho)

* **Iniciativa/Transferencia** (una fila)

  * Identificador candidato: **CÓDIGO** (pero **no es estrictamente único**, ver calidad).

### Dimensiones implícitas y relaciones (muchos-a-uno)

* **Tiempo:** AÑO

  * Jerarquía: **AÑO → (conjunto de iniciativas de ese año)**
* **Programa:** FONDO

  * Jerarquía típica: **AÑO → FONDO → CÓDIGO**
* **Institución beneficiaria:** INSTITUCIÓN, RUT INSTITUCIÓN

  * Relación: una institución puede tener **múltiples iniciativas**.
* **Territorio:** PROVINCIA, COMUNA

  * Jerarquía: **PROVINCIA → COMUNA**
* **Gestión/seguimiento:** PROFESIONAL UCR, REFERENTE TÉCNICO

  * Relación: un profesional/referente puede estar asociado a muchas iniciativas.

---

## 3) Diccionario de campos (Hoja 1)

1. **N° Interno**

   * Tipo observado: numérico (aparece como decimal “.0” por importación)
   * Rol: correlativo interno / índice visible
   * Calidad: **3 valores faltantes**; no es llave confiable.

2. **AÑO**

   * Tipo: numérico (año calendario)
   * Valores: 2019–2023
   * Completitud: 100%

3. **FONDO**

   * Tipo: texto (categoría)
   * Valores típicos (normalizados): DEPORTES, SEGURIDAD, CULTURA, SOCIAL, SOCIAL COVID-19, ADULTO MAYOR, EQUIDAD DE GÉNERO, MEDIO AMBIENTE, INTERÉS REGIONAL, DEPORTISTA DESTACADO
   * Calidad: **inconsistencias por espacios** (p. ej. `"SOCIAL"`, `"SOCIAL "`, `"SOCIAL   "`; `"MEDIO AMBIENTE"` y `"MEDIO AMBIENTE "`).

4. **CÓDIGO**

   * Tipo: texto (identificador de iniciativa)
   * Calidad:

     * **32 códigos aparecen duplicados** (64 filas afectadas), casi siempre con todo igual salvo N° Interno (indica posible duplicación por consolidación/copia).
     * 1 caso con **carácter de salto de línea** (`\n`) dentro del código.
     * Variantes de formato: códigos “tipo año” (`1901D0198`, etc.) y otros como `FSDÑ 0038` / `FSDÑ0022` (espaciado no uniforme).

5. **NOMBRE DE LA INICIATIVA**

   * Tipo: texto
   * Calidad: frecuente **espaciado sobrante** (≈10% con espacios externos), mayúsculas consistentes en general.

6. **INSTITUCIÓN**

   * Tipo: texto
   * Calidad: **espacios externos** relativamente frecuentes (≈13%); nombres largos con dobles espacios en algunos casos.

7. **RUT INSTITUCIÓN**

   * Tipo: texto (RUT chileno)
   * Calidad:

     * Formatos mixtos (con puntos / sin puntos / espacios).
     * Validación de dígito verificador: **≈99,3% válidos**; **27 RUT** aparecen **inválidos** (probables errores de digitación o DV incorrecto).

8. **PROVINCIA**

   * Tipo: texto
   * Calidad:

     * Variantes por espacios: `"ITATA"` / `"ITATA "`; `"PUNILLA"` / `"PUNILLA "`; `"DIGUILLIN"` / `"DIGUILLIN "`
     * Variantes por acento: `"DIGUILLIN"` vs `"DIGUILLÍN"` (debería normalizarse a una sola forma).
     * Incluye `"REGIONAL"` (cuando no aplica provincia específica).

9. **COMUNA**

   * Tipo: texto
   * Cobertura: **24 comunas** (coherente con Región de Ñuble)
   * Calidad: muy buena; **1 fila sin comuna** (institución tipo asociación).

10. **MONTO TRANSFERIDO**

11. **RENDIDO A LA FECHA**

12. **REINTEGRADO**

13. **TOTAL ACUMULADO**

14. **SALDO PENDIENTE**

* Tipo observado: texto con formato moneda (`$`, separadores de miles, guiones).
* Coherencia contable (ver sección 5): en general **muy alta**.
* Calidad:

  * Existen **guiones** (`$ -`) usados como “0” o “sin dato” según contexto.
  * Hay **3 filas** (SEGURIDAD 2023) con rendido/total/saldo **en blanco** (NaN) y montos sin el símbolo `$` (formato inconsistente).
  * **5 filas** con MONTO TRANSFERIDO en `0` o `$ -` (requiere regla de negocio: ¿corresponde a “sin transferencia” o dato faltante?).

15. **OBSERVADO**

* Tipo: texto (SI/NO)
* Completitud: **muy baja** (**solo 120 filas con valor**, 3.728 vacías).
* Interpretación: parece un campo incorporado tarde o usado solo en ciertos periodos.

16. **PROFESIONAL UCR**

* Tipo: texto (nombre responsable)
* Calidad: viene con **espacios externos en prácticamente todos los registros** (ej. `" Victor Retamal "`).
* Completitud: 111 vacíos.

17. **REFERENTE TÉCNICO**

* Tipo: texto (nombre responsable)
* Calidad: también con **espacios externos sistemáticos**.
* Completitud: 3 vacíos (coinciden con las 3 filas incompletas de 2023 SEGURIDAD).

---

## 4) Distribución y estructura del contenido (coherencia temática)

### Distribución por año (número de iniciativas)

* 2019: 780
* 2020: 267
* 2021: 957
* 2022: 796
* 2023: 1.048

### Instituciones únicas (por RUT)

* **2.497 instituciones** para 3.848 iniciativas (≈ **1,54 iniciativas/institución** en promedio).

### Fondos más presentes (por volumen de registros)

* DEPORTES (992), CULTURA (635), SEGURIDAD (769), SOCIAL (532), etc.
  *(Ojo: antes de normalizar espacios, el conteo de “SOCIAL” y “MEDIO AMBIENTE” se fragmenta en variantes.)*

---

## 5) Coherencia contable y reglas internas verificables

En la gran mayoría de registros, se cumple la lógica:

### Regla A: **TOTAL ACUMULADO ≈ RENDIDO A LA FECHA + REINTEGRADO**

* Se observa **consistencia prácticamente total**.
* **1 anomalía puntual** detectada: diferencia de **$2** en un registro (monto/total/reintegro no calzan por 2 pesos).

### Regla B: **SALDO PENDIENTE ≈ MONTO TRANSFERIDO − TOTAL ACUMULADO**

* Cuando SALDO está informado numéricamente (no “$ -” ambiguo), la coherencia es **muy alta**.
* Existen **85 casos de saldo negativo** (TOTAL ACUMULADO supera MONTO TRANSFERIDO), generalmente por montos pequeños; el caso más extremo es **-$72.000**. Esto puede ser:

  * error de digitación,
  * ajuste/regularización posterior,
  * o un efecto contable (p. ej., rendición que excede por ítems no descontados), pero requiere definición.

### Hallazgo crítico de calidad (impacto en totales)

Hay un conjunto de filas donde:

* **TOTAL ACUMULADO = “$ -”** y **SALDO PENDIENTE = “$ -”**, pese a que **MONTO TRANSFERIDO sí tiene valor**.

En particular:

* **41 filas** (principalmente códigos `FSDÑ …` en 2023) tienen monto positivo pero saldo “$ -”.
* Esto hace que el **saldo total “reportado”** en la columna SALDO esté **subestimado**.

Magnitud del problema (agregado):

* **Monto total transferido (2019–2023):** $ 22.100.728.881
* **Total acumulado (según TOTAL ACUMULADO):** $ 10.917.151.716
* **Saldo “esperado” (monto − total):** $ 11.171.356.165
* **Saldo “reportado” (suma de SALDO PENDIENTE):** $ 6.134.520.560
* **Diferencia:** **$ 5.036.835.605** (explicada por esos saldos no informados con guión).

En simple: **la planilla es internamente coherente cuando los campos están completos**, pero **mezcla “$ -” como 0 y como “sin calcular/sin dato”**, lo que rompe análisis agregados.

---

## 6) Calidad de datos por dimensión (naturaleza, coherencia y problemas)

### Completitud (missingness)

* Muy buena en campos nucleares (AÑO, FONDO, CÓDIGO, institución, RUT, territorio, MONTO).
* Excepciones relevantes:

  * **OBSERVADO**: ~97% vacío (campo poco usable sin una regla).
  * **3 filas** con rendido/total/saldo completamente vacíos (casos puntuales 2023 SEGURIDAD).
  * **REINTEGRADO**: 59 vacíos (en muchos casos debería ser 0).

### Consistencia (formatos)

* **Espacios externos** masivos en nombres de responsables (PROFESIONAL/REFERENTE) y frecuentes en FONDO/INSTITUCIÓN/NOMBRE INICIATIVA.
* **PROVINCIA** con variantes (acentos y espacios).
* **CÓDIGO** con formatos distintos y un caso con control char (`\n`).

### Unicidad (claves)

* **CÓDIGO no es único**: 32 códigos repetidos (posible duplicación de registros).
* **N° Interno** no es llave: tiene vacíos y aparece como flotante.

### Validez

* **RUT INSTITUCIÓN:** 27 inválidos (≈0,7%). Recomendable revisar.

### A. Módulo FNDR 8% 2024 (núcleo del libro)

#### A1) Hojas maestras por fondo (detalle de iniciativas)

Estas hojas contienen el **listado base** por tipología/fondo, con datos de institución, transferencia, ejecución y rendición.

**Esquema común (campos más recurrentes):**

* **Identificación**: `CÓDIGO` (o `CODIGO`), `TIPOLOGÍA`
* **Institución**: `NOMBRE INSTITUCIÓN`, `RUT INSTITUCIÓN`, `NOMBRE REPRESENTANTE LEGAL`
* **Ubicación**: `PROVINCIA`, `COMUNA`
* **Contacto**: `CORREO`, `CORREO 2`, `TELÉFONO`
* **Transferencia/marco**: `FECHA DE TRANSFERENCIA` o `RECIBIÓ TRANSFERENCIA`, `MONTO TRANSFERIDO` (con variantes de nombre), `Nº RESOLUCIÓN QUE INCORPORA AL MARCO`
* **Ejecución/rendición**: `ESTADO EJECUCIÓN 2024` (o similar), `FECHA (DE) INGRESO A OFICINA DE PARTES`, `FECHA ENVÍO CIERRE TÉCNICO A UCR`, `FECHA CIERRE FINANCIERO UCR`, `INGRESO RENDICIÓN A TIEMPO`
* **Observaciones**: columnas tipo `DETALLE OBSERVACIÓN` / `DETALLE OBSERVACIONES`, o un campo “placeholder” (`<<<<<`)

**Hojas incluidas (con tamaño y notas estructurales):**

1. **F.ADULTO MAYOR**

* **Tipo**: tabla maestra (detalle)
* **Registros**: **234 iniciativas** (hay 1 fila adicional con código vacío)
* **Columnas**: 20
* **Notas estructurales**:

  * Arriba trae líneas tipo “INICIATIVAS POSTULADAS: 289 / INADMISIBLES: 47”.
  * Aparece un `#ERROR!` en la esquina superior (ruido del origen en Google Sheets).
  * Última columna se llama **`<<<<<`** (se usa como observación).
* **Dato clave**: `CÓDIGO` (pero hay al menos un caso con **código mal digitado**: aparece como “245” en vez de algo como `2401AM0245`).

2. **F.CULTURA**

* **Tipo**: tabla maestra (detalle)
* **Registros**: **163 iniciativas** (y 1 fila con código vacío)
* **Columnas**: 21
* **Particularidad**: incluye columna extra **`Estado UCR`** además de `DETALLE OBSERVACIÓN`.
* **Problema de clave**: existe al menos una fila donde en `CÓDIGO` aparece un **nombre de persona** (no un código).

3. **F.DEPORTE**

* **Tipo**: tabla maestra (detalle)
* **Registros**: **324 iniciativas** (más filas de ruido: 2 filas vacías y 1 fila de comentario interno).
* **Columnas**: 22
* **Particularidad**:

  * Usa `RECIBIÓ TRANSFERENCIA` en lugar de `FECHA DE TRANSFERENCIA`.
  * Incluye **2 columnas vacías extra** al final (`(blank)`).
* **Problema de clave**: hay una fila donde el `CÓDIGO` aparece como `_<` (claramente un error de digitación).

4. **F.EQUIDAD DE GÉNERO**

* **Tipo**: tabla maestra (detalle)
* **Registros**: **117 iniciativas**
* **Columnas**: 20
* **Detalle de calidad**: la columna de monto aparece como **`MONTO TRANFERIDO`** (error ortográfico en el nombre del campo).

5. **F.MEDIO AMBIENTE**

* **Tipo**: tabla maestra (detalle)
* **Registros**: **111 iniciativas**
* **Columnas**: 21
* **Particularidad**: separa observaciones en:

  * `DETALLE OBSERVACIÓN TÉCNICA`
  * `DETALLE OBSERVACIÓN FINANCIERA`

6. **F.SEGURIDAD**

* **Tipo**: tabla maestra (detalle)
* **Registros**: **549 iniciativas**
* **Columnas**: 20
* **Particularidad**:

  * La clave viene como `CODIGO` (sin tilde).
  * Monto también aparece como `MONTO TRANFERIDO`.

7. **F.SOCIAL**

* **Tipo**: tabla maestra (detalle)
* **Registros**: **182 iniciativas** (más 2 filas con código vacío)
* **Columnas**: 31
* **Particularidad fuerte**: tiene **muchas columnas extra vacías** (`(blank)…`), que no aportan datos (ruido estructural).

**Consistencia global dentro del módulo 8% (a nivel de volumen):**

* Total iniciativas en las hojas F.* = **1680**
* Total con transferencia registrada = **1613**
* Total “no transferido” (sin fecha/registro de transferencia) = **67**
  Esto calza con el resumen agregado (ver A3).

---

#### A2) Hojas “de control”/subconjuntos derivados del 8%

Estas hojas parecen extraer subconjuntos desde el universo de las F.* (o desde un consolidado paralelo) para control de cumplimiento/plazos y gestión.

8. **ELIMINADAS MARCO PRESUPUESTARIO 8% 2024**

* **Tipo**: listado de exclusión/depuración (detalle)
* **Registros**: **57**
* **Columnas**: 8
  `CÓDIGO`, `FONDO`, `NOMBRE INSTITUCIÓN`, `NOMBRE INICIATIVA`, `RUT INSTITUCIÓN`, `COMUNA`, `MONTO`, `RESOLUCIÓN`
* **Calidad**:

  * `FONDO` no está totalmente normalizado (aparece “SEGURIDAD” y “SEGURIDAD CIUDADANA” como categorías distintas).
  * Hay un caso de código mal formado: `2401AM130` (probablemente faltan ceros: `2401AM0130`).

9. **HABILITADAS FUERA DE PLAZO**

* **Tipo**: listado de excepción (detalle)
* **Registros**: **111** (pero **110 códigos únicos**: hay 1 duplicado)
* **Columnas**: 21 (muy similares a F.*)
* **Campos distintivos**: `DIA RETRASOS` (pero viene **vacío** en todos los registros)
* **Dato notable**: `INGRESO RENDICIÓN A TIEMPO` es **NO en 111/111**.
* **Calidad**:

  * Hay **duplicidad de código** (`2401SC0196` aparece dos veces).
  * `N°` tiene al menos 1 fila sin número.

10. **INHABILITADAS RENDIDAS FUERA PLAZO Y NO RENDIDAS**

* **Tipo**: listado sancionatorio/control (detalle)
* **Registros**: **527** (códigos únicos)
* **Columnas**: 20 (muy similares a F.*)
* **Dato notable**: `INGRESO RENDICIÓN A TIEMPO` es **NO en 527/527**.
* **Calidad**:

  * `DIA RETRASOS` está **casi completamente vacío** y, en algunos casos, contiene **valores que parecen fechas** (no “días” como número), lo que sugiere error de uso del campo.
  * Esta hoja contiene códigos “bien formados” que ayudan a detectar/corregir errores en F.* (por ejemplo, el caso `2401D0099` aparece aquí con datos completos, mientras en F.DEPORTE el código está corrupto como `_<`).

11. **RECURSOS ORGANIZACIONES SIN RENDIR**

* **Tipo**: listado operativo de seguimiento (detalle)
* **Registros**: **78 filas**, con **77 códigos informados** (1 fila con código vacío)
* **Columnas**: 21 (muy parecida a F.*)
* **Calidad / consistencia**:

  * Varias columnas de fechas de proceso (`FECHA DE INGRESO…`, `FECHA ENVÍO…`, `FECHA CIERRE FINANCIERO UCR`) vienen **completamente vacías** (lo que es coherente si “no han rendido”, pero limita análisis).
  * Hay casos **inconsistentes con el título**: aparece al menos un registro con `INGRESO RENDICIÓN A TIEMPO = SÍ`, lo que sugiere lista desactualizada o criterio distinto (por ejemplo “sin rendir al momento de corte”).

---

#### A3) Hojas resumen (agregación del 8%)

12. **RESUMEN FNDR 8%2024**

* **Tipo**: resumen agregado (tabla + notas)
* **Estructura**:

  * Parte superior: tabla por fondo con columnas:

    * `NO TRANSFERIDO`
    * `ORGANIZACIONES TRANSFERIDADAS`
    * `RENDIDAS`
    * `ENVIADAS A LA UCR`
    * `CON OBSERVACIONES TÉCNICAS`
    * `PENDIENTE DE REVISIÓN`
    * `NO RENDIDA`
    * `RENDICIÓN INGRESADA FUERA DE PLAZO`
  * Parte inferior: **filas con texto** (“Importante…”, “Revisar…”), mezcladas dentro del mismo rango.
* **Registros**: 7 fondos + TOTAL + 2 líneas de notas (en total **10 filas útiles** al exportar).
* **Calidad**:

  * La mezcla de **tabla + notas en el mismo bloque** rompe la estructura tabular para análisis automatizado.
  * Los nombres de fondo no están 100% normalizados (ej. “EQUIDAD DE GENERO” sin tilde).

13. **Hoja 18** (resumen “avance proceso rendición”)

* **Tipo**: resumen agregado (tabla)
* **Registros**: **8 filas** (7 fondos + TOTAL)
* **Columnas**: 7
  `TRANSFERIDAS`, `RENDIDAS`, `PENDIENTES DE RENDIR`, `CON CIERRE TECNICO`, `CON OBSERVACIONES`, `PENDIENTES DE REVISION`
* **Calidad / consistencia**:

  * Internamente es consistente (para cada fondo: `RENDIDAS = CIERRE + OBSERVACIONES + PENDIENTES REVISION`).
  * Sus cifras **no coinciden** con las de “RESUMEN FNDR 8%2024” en varias columnas (lo que sugiere **cortes temporales distintos** o **definiciones distintas** de “rendida”, “observaciones”, etc.). No hay un campo “fecha de actualización”, por lo que no se puede saber cuál es el dato vigente.

---

#### A4) Tabla de apoyo territorial

14. **DISTRIBUCIÓN TERRITORIAL**

* **Tipo**: tabla de referencia (lookup)
* **Estructura real**:

  * 2 columnas: `NOMBRE PROFESIONAL`, `COMUNA ASIGNADA`
  * Por el formato original (celdas combinadas), algunas filas vienen con profesional vacío y deben interpretarse como “mismo profesional que la fila anterior”.
* **Contenido**:

  * Permite asignar **cada comuna** a un profesional. Se observan **21 comunas únicas** (cobertura completa regional).
* **Calidad**:

  * Hay 2 filas con nombre de profesional pero comuna vacía (ruido por exportación/merge).
  * Diferencias de ortografía/acentos en comunas (ej. “CHILLAN” vs “CHILLÁN” en otras hojas) pueden dificultar cruces si no se normaliza texto.

---

### B. Módulo Asignaciones Directas 2023–2024

15. **ASIGNACIONES DIRECTAS 23-24**

* **Tipo**: tabla de seguimiento financiero (detalle + total)
* **Registros**:

  * **59 asignaciones** con `CÓDIGO` informado
  * * 1 fila **TOTAL** al final (agregada)
* **Columnas**: 19
  Incluye: `REFERENTE UCR`, `REFERENTE TÉCNICO`, `DIVISIÓN`, montos transferidos/rendidos/reintegrados, `% rendido a la fecha`, y `OBSERVACIONES`.
* **Calidad**:

  * Columna `FECHA DE LA TRANSFERENCIA` está **completamente vacía** (estructura prevista, datos no cargados).
  * Montos vienen como texto con `$`, separadores y distintos formatos.
  * La fila TOTAL no está separada como resumen (está dentro del mismo rango), lo que obliga a filtrarla si se analiza como dataset.

---

### C. Módulo Programas Sociales + Planificación 2026 (BIP)

16. **PROGRAMAS SOCIALES**

* **Tipo**: seguimiento de programas (detalle)
* **Registros**: **35** (BIP únicos)
* **Columnas**: 32
  Incluye: `CÓDIGO BIP`, comuna, unidad ejecutora, rut, **contacto (teléfono/correo)**, financiamiento, objetivo, beneficiarios H/M, remesas (1°, 2°, 3°), montos rendidos/reintegrados, saldo y `SALDO ARRASTRE 2026`.
* **Calidad**:

  * Campos de **3ª remesa** y algunos totales (`MONTO 3° REMESA`, `FECHA DE LA TRANSFERENCIA.2`, `TOTAL RENDIDO`, `MONTO REINTEGRADO`) están **mayoritariamente vacíos**, lo que sugiere que se usa principalmente 1ª/2ª remesa o que el proceso está incompleto.
  * Teléfonos y correos: datos personales de contacto (deben tratarse con cuidado).

17. **CARTERA PROGRAMAS 2026**

* **Tipo**: cartera/planificación (mixto: líneas de programa + subtotales)
* **Registros**: **16 filas** (incluye una fila de total al final)
* **Columnas**: 9
  `CÓDIGO BIP`, `PROGRAMA`, `INTITUCIÓN` (error ortográfico), `MONTO ESTIMADO`, `CONTRAPARTE`, `ACTA PERTINENCIA`, `ESTADO DE AVANCE`, `PROGRAMACIÓN REMESA 2026`, `OBSERVACIONES`.
* **Calidad**:

  * Varias filas tienen `CÓDIGO BIP` vacío (parecen **sub-líneas** o agrupaciones).
  * `OBSERVACIONES` viene vacía.
  * Incluye fila final con total en `PROGRAMACIÓN REMESA 2026`.

---

### D. Módulo Otras iniciativas de inversión + Participación Ciudadana

18. **OTRAS INICIATIVAS DE INVERSIÓN**

* **Tipo**: cartera de iniciativas (detalle)
* **Registros**: **31** (BIP únicos)
* **Columnas**: 16
  Incluye BIP, nombre proyecto/iniciativa, comuna, unidad ejecutora, rut, financiamiento, beneficiarios, año, RATE, estado, enlace, división, monto aprobado, convenio, observaciones.
* **Calidad**:

  * Mejor estructura tabular que varias otras hojas (cabecera limpia, sin notas mezcladas).
  * Algunos campos tienen valores faltantes moderados (estado/convenio).

19. **PARTICIPACIÓN CIUDADANA**

* **Tipo**: registro de eventos/actas (detalle por sesión o registro)
* **Registros**: **37 filas**, pero **17 iniciativas BIP únicas** (una iniciativa puede tener varias entradas)
* **Columnas**: 12
  `REFERENTE`, `CÓDIGO BIP`, `NOMBRE INICIATIVA`, `UNIDAD EJECUTORA`, `FECHA`, `ASISTENCIA`, `DIVISIÓN`, `LUGAR`, `ORGANIZACIÓN FIRMANTE`, `NOMBRE REPRESENTANTE LEGAL`, `OBSERVACIONES`.
* **Calidad**:

  * Es “evento-nivel” (no “proyecto-nivel”), por eso repite BIP.
  * Hay textos con saltos de línea en `NOMBRE INICIATIVA` (requiere limpieza si se exporta a sistemas).
  * Contiene datos personales (representantes legales, etc.).

---

## 3) Modelo integrado: cómo “encaja” todo como un conjunto

### 3.1 Dos universos de claves (muy importante)

* **Universo 8% FNDR (concursable 2024):**

  * Clave principal: **`CÓDIGO`** (ej. `2401SC0126`, `2401AM0247`, etc.).
  * Aparece en: **todas las F.* + Eliminadas + Habilitadas + Inhabilitadas + Recursos sin rendir**.
* **Universo inversión/programas (BIP):**

  * Clave principal: **`CÓDIGO BIP`**.
  * Aparece en: **Programas Sociales + Cartera 2026 + Otras Iniciativas + Participación Ciudadana**.

Estos universos no se mezclan directamente (salvo por atributos comunes como comuna/división).

### 3.2 Tablas “maestras” vs “derivadas”

* **Maestras (detalle base):**

  * F.* (por fondo) para 8%
  * Asignaciones Directas 23–24
  * Programas Sociales
  * Otras Iniciativas de Inversión
  * Participación Ciudadana (pero a nivel evento)
* **Derivadas / control:**

  * Eliminadas (subconjunto de “no transferidas”/fuera de marco)
  * Habilitadas fuera de plazo / Inhabilitadas (control por cumplimiento de plazos)
  * Recursos sin rendir (lista operativa de seguimiento)
* **Resumen:**

  * Hoja 18 y Resumen FNDR 8%2024

### 3.3 Rol de “Distribución Territorial”

* Es una **tabla de referencia** para asignar responsable por comuna.
* Puede apoyar cruces con:

  * F.* (tienen comuna)
  * Asignaciones Directas (tiene referente UCR, pero no siempre se puede inferir solo por comuna)
  * Programas Sociales / Otras iniciativas / Participación (tienen comuna y/o referente)

---

## 4) Naturaleza y calidad de los datos (evaluación crítica)

### 4.1 Naturaleza

* Datos **administrativos-financieros**: transferencias, montos, resoluciones, estados de ejecución y rendición.
* Datos **operativos de control**: fechas de ingreso a oficina de partes, envío a UCR, observaciones técnicas/financieras.
* Datos **personales** (PII):

  * Nombres de representantes legales, correos, teléfonos (especialmente en F.* y Programas Sociales).
  * Esto exige cuidados de confidencialidad y control de acceso.

### 4.2 Calidad estructural (formato/tabla)

Principales problemas:

* Varias hojas mezclan **títulos, KPI y cabeceras dentro del rango de datos** (F.* y algunas otras).
* Existen **filas de totales** o **notas** dentro de tablas (Asignaciones Directas, Cartera 2026, Resumen FNDR).
* Existen **columnas vacías** o “basura” (`(blank)…`, `Unnamed…`, `<<<<<`) que dificultan automatización.

Impacto: para análisis o carga a BI/BD, se requiere una etapa de **limpieza y estandarización**.

### 4.3 Calidad de claves (integridad referencial)

* `CÓDIGO` es crítico pero tiene errores puntuales:

  * códigos truncados (`245`, `_<`)
  * códigos con ceros faltantes (`2401AM130`)
  * valores no-código en la columna clave (un nombre de persona en F.CULTURA)
* En hojas derivadas (p.ej. **INHABILITADAS**) aparecen códigos “correctos” que no calzan con el maestro por estos errores, lo que rompe joins directos.

### 4.4 Tipificación (fechas, montos, teléfonos)

* **Fechas**: múltiples formatos coexistiendo:

  * `DD-MM-YYYY`, `DD.MM.YYYY`, `DD-MM-YY`, y también valores no-fecha como “Cheque”.
* **Montos**: están como texto con `$` y separadores inconsistentes (`$1.929.500`, `$2.500.000,00`, `$ 2.000.000`, `$5,000,000.00`).
* **Teléfonos**: a veces como texto, a veces como número flotante (aparece `.0`), lo que puede deformar datos.

### 4.5 Consistencia entre resúmenes y detalle

* **Hoja 18** y **RESUMEN FNDR 8%2024** reportan métricas similares pero con valores distintos en varias columnas.
* “RECURSOS ORGANIZACIONES SIN RENDIR” no siempre coincide con el estado/timeliness de las hojas F.*.
* Falta un campo explícito de **fecha de corte/actualización**, por lo que es difícil establecer cuál reporte es el “vigente”.
