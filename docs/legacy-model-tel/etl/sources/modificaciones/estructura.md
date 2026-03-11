# Estructura Legacy

## 1) Estructura global de la planilla

### 1.1. Inventario de hojas (CSV)

Las hojas detectadas (por nombre de archivo) son:

1. **REBAJA 5%.csv**
2. **MODIFICACIÓN N°1.csv**
3. **MODIFICACIÓN N°2.csv**
4. **MODIFICACIÓN N°3.csv**
5. **MODIFICACIÓN N°3 SIN EFECTO.csv**
6. **MODIFICACIÓN N°4.csv**
7. **MODIFICACIÓN N°5 SIC.csv**
8. **REBAJA FUNC. N°6 sin efecto.csv**
9. **MODIFICACIÓN Nº7.csv**
10. **MODIFICACIÓN Nº9.csv**

En términos de “estado” documental, hay **modificaciones normales**, **rebajas** y **versiones “sin efecto”** (que, por su propia etiqueta, deberían considerarse **anuladas/no vigentes** para consolidación).

---

## 2) Campos y estructura de datos (modelo común)

### 2.1. Bloques dentro de cada hoja

Las hojas vienen en dos modalidades:

* **Hojas con un solo bloque**: normalmente solo aparece un bloque tipo **GASTOS** (o un bloque sin etiqueta explícita).
* **Hojas con dos bloques**: un bloque de **INGRESOS** y otro de **GASTOS**, cada uno con su propia tabla y total.

En las hojas con etiqueta, suele aparecer una fila “total” donde `DENOMINACIONES = INGRESOS` o `DENOMINACIONES = GASTOS`.

### 2.2. Estructura de columnas (campos)

En casi todas las hojas existe un **núcleo común de campos**, aunque con variaciones:

**Campos de clasificación (identificación de línea presupuestaria)**

* `SUBT.`: código de subtítulo (nivel superior).
* `ITEM`: código de ítem (nivel intermedio).
* `ASIG.`: código de asignación (nivel más detallado).
* `DENOMINACIONES`: descripción textual del concepto (subtítulo, ítem o asignación).

**Campo adicional (según hoja)**

* Un **campo intermedio sin nombre** entre `ASIG.` y `DENOMINACIONES` que en varias hojas toma valores como:

  * `C`
  * `M`
    Este campo actúa como **marcador/etiqueta** (no hay diccionario explícito en los CSV). En la práctica, se usa en algunas asignaciones para distinguir variantes de una misma línea (por ejemplo, dos filas con mismo ASIG pero distinta marca).

**Campos de montos (unidad declarada como “M$” en el encabezado)**
Los encabezados del propio documento definen el significado de las columnas de montos. En la estructura estándar aparecen **4 columnas**:

1. `DISTRIBUCIÓN INICIAL M$`
2. `PPTO. VIGENTE CON MODIFICACIONES ANTERIORES M$`
3. `MODIFICACIÓN N°X M$` (X cambia según hoja)
4. `PPTO. VIGENTE (INCLUYE PRESENTE MODIFICACIÓN) M$`

**Campo de observaciones (solo en algunas hojas)**

* Aparece una columna de texto al final (tipo `OBS`) con valores como:

  * “Fondo de la Productividad”
  * “Ejecución desde el año 2023”
  * “FONDO PARA LA PRODUCTIVIDAD”

**Caso especial – MODIFICACIÓN Nº9**

* En esa hoja aparecen **más de 4 columnas numéricas**: además de la estructura estándar, hay:

  * Dos columnas de modificación simultáneas (ej.: “MODIFICACIÓN N°9” y “MODIFICACIÓN N°4” en el encabezado).
  * Columnas numéricas adicionales sin rótulo claro y un parámetro **“-35%”** en el encabezado superior (probable celda auxiliar para cálculos).

### 2.3. Jerarquía y “formato de reporte” (cómo se expresa el árbol SUBT→ITEM→ASIG)

La tabla no repite siempre los códigos en cada fila. Es un formato típico “estado presupuestario”:

* Filas de **nivel SUBT**: tienen `SUBT` y `DENOMINACIONES`, con `ITEM/ASIG` vacíos.
* Filas de **nivel ITEM**: tienen `ITEM` (y a veces `DENOMINACIONES`), con `SUBT` a veces vacío (se entiende por contexto).
* Filas de **nivel ASIG**: suelen tener `ASIG` y `DENOMINACIONES` (beneficiario/proyecto), y pueden venir con `SUBT/ITEM` en blanco.

Esto implica una regla importante para análisis:

* Para normalizar, hay que **“arrastrar hacia abajo” (fill‑down)** el `SUBT` y el `ITEM` vigentes a las filas de detalle, **reiniciando el ITEM cuando cambia el SUBT**.

Si no se hace, se pierden relaciones y se mezclan ítems entre subtítulos.

### 2.4. Relaciones entre hojas

La relación natural entre hojas se da por el clasificador:

* **Clave conceptual de línea** (nivel ASIG): `(SUBT, ITEM, ASIG)`

  * opcionalmente el marcador `C/M` cuando existe y cuando duplica ASIG.

Con esto se observa:

* Varias hojas modifican **las mismas ASIG** (p. ej. se repiten códigos como 476, 477, 479, 481, 483, 484, 999 en distintas hojas), lo cual sugiere una **secuencia de modificaciones sobre un mismo set de líneas**.

---

## 3) Coherencia y calidad global del conjunto

### 3.1. Coherencia aritmética (muy relevante)

En las hojas “más limpias”, se observa consistencia de la forma:

* `PPTO final` = `PPTO vigente` ± `Modificación`

Pero **no hay una convención única del signo**:

* En varias hojas, las disminuciones están expresadas con **número negativo** (ej.: `-36.000`, `-500.000`, `-350.000`, etc.), y entonces se cumple:

  * `final = vigente + modificación`
* En otras, la disminución aparece como **número positivo**, pero el presupuesto final es menor (se está usando implícitamente “resta”):

  * `final = vigente − modificación`

Esto afecta fuerte la calidad analítica porque:

* No puedes sumar la columna “Modificación” sin antes **normalizar el signo**.
* Una forma robusta de estandarizar es calcular siempre:

  * **`modificación_signed = PPTO_final − PPTO_vigente`**
    (cuando ambos existan y no estén con error).

### 3.2. Errores de fórmula exportados (`#REF!`)

Varios CSV contienen celdas `#REF!` (típico de fórmulas rotas o referencias inválidas exportadas):

* **MODIFICACIÓN Nº9.csv**: es la hoja más afectada (muchos `#REF!`, incluso en denominaciones).
* **MODIFICACIÓN N°4.csv**, **MODIFICACIÓN N°5 SIC.csv**, **MODIFICACIÓN N°3 SIN EFECTO.csv**, **REBAJA FUNC. N°6 sin efecto.csv**: también presentan `#REF!`, sobre todo en montos “vigente” y “final”, y en totales.

Impacto:

* Hay filas donde no se puede reconstruir el `PPTO vigente` o `PPTO final` desde el CSV.
* Impide validar balance (aumento vs disminución) en varios bloques.

### 3.3. Inconsistencias documentales (metadatos)

* **Desalineación del número de modificación**:

  * `MODIFICACIÓN N°1.csv`: el **título** dice “N°02”, pero el encabezado de montos dice “MODIFICACIÓN N°1”.
  * `MODIFICACIÓN N°5 SIC.csv`: el bloque de INGRESOS referencia “MODIFICACIÓN N°5”, pero el bloque de GASTOS aparece con “MODIFICACIÓN N°4”.
  * `MODIFICACIÓN Nº9.csv`: aparecen dos columnas “MODIFICACIÓN N°9” y “MODIFICACIÓN N°4”.

Esto sugiere **plantillas reutilizadas** sin corregir completamente.

* **Año / fecha**:

  * Algunas hojas indican explícitamente **AÑO 2025**.
  * Otra incluye una fecha explícita (“21 de marzo de 2024”).
  * Varias no traen año en el encabezado.

Para consolidar históricamente, falta un metadato estable en cada hoja.

### 3.4. “Ruido” por formato (filas no‑datos)

En al menos algunas hojas, dentro del rango de tabla aparecen filas de texto tipo:

* “GOBIERNO REGIONAL…”
* “DISTRIBUCIÓN INICIAL… / PPTO… / MODIFICACIÓN…”

Es decir, rótulos incrustados que, al exportar a CSV, quedan mezclados con datos.
Para analítica hay que filtrarlos explícitamente.

### 3.5. Formato de números

* Montos vienen como **texto** con separador de miles `,` y a veces espacios.
* Requiere limpieza: quitar comas/espacios y convertir a numérico.
* Hay ceros representados como `"0 "` (con espacio).

---

## 4) Descripción por hoja: contenido, estructura interna y calidad

### 4.1. REBAJA 5%.csv

**Metadatos**

* Título: “MODIFICACIÓN PRESUPUESTARIA N°05”
* Programa: “PROGRAMA DE INVERSIÓN REGIONAL AÑO 2025”
* Tipo (por nombre): **REBAJA**

**Estructura**

* 1 bloque **sin etiqueta explícita** (no hay fila “INGRESOS/GASTOS”).
* Campos: `SUBT, ITEM, ASIG, DENOMINACIONES + 4 montos`.
* Sin columna `C/M`, sin observaciones.

**Contenido**

* Subtítulos presentes:

  * `13` – “TRANSFERENCIAS PARA GASTOS DE CAPITAL”
  * `33` – “TRANSFERENCIAS DE CAPITAL”
* Ítem usado: `03` (aparece como “De otras entidades públicas” / “A otras entidades públicas”, según subtítulo)
* Asignación:

  * `999` – “Provisión Fondo para la Productividad y el Desarrollo (Sin Distribuir)”

**Coherencia y calidad**

* Aritmética consistente, pero **la rebaja se expresa con monto positivo** y el presupuesto final es menor → la “Modificación” debe interpretarse como **disminución**.
* Sin `#REF!`.
* Es una hoja pequeña y bastante “limpia”, salvo por la falta de etiqueta Ingresos/Gastos y la convención de signo.

---

### 4.2. MODIFICACIÓN N°1.csv

**Metadatos**

* El archivo se llama “N°1”, pero el **título** del documento indica “MODIFICACIÓN… N°02”.
* En el encabezado de montos aparece “MODIFICACIÓN N°1 M$”.
* Año indicado: **2025**.

**Estructura**

* 1 bloque sin “INGRESOS/GASTOS”.
* Campos: `SUBT, ITEM, ASIG, DENOMINACIONES + 4 montos`.

**Contenido**

* Subtítulos presentes:

  * `13` – “TRANSFERENCIAS PARA GASTOS DE CAPITAL”
  * `24` – “TRANSFERENCIAS CORRIENTES”
* Ítem `03`.
* Asignación detallada:

  * `006` – “Subsecretaria del Trabajo - PROEMPLEO”

**Coherencia y calidad**

* Sin `#REF!`.
* La “Modificación” aparece como **monto positivo pero aplicado como rebaja** (presupuesto final < vigente).
* **Inconsistencia fuerte en numeración** (título vs encabezado) → riesgo de asignar mal la modificación al consolidar.

---

### 4.3. MODIFICACIÓN N°2.csv

**Metadatos**

* Título: “MODIFICACIÓN PRESUPUESTARIA N°02”
* Año indicado: **2025**
* Bloque: **GASTOS** (con fila total).

**Estructura**

* 1 bloque `GASTOS`.
* Incluye columna `C/M` (etiqueta) y una columna de **OBS**.
* Total de ASIG detalladas: **19** (más niveles SUBT/ITEM).

**Contenido**

* Totales del bloque `GASTOS`: la modificación total del bloque aparece en **0** (indica reasignación interna).
* Subtítulos presentes:

  * `24` – “TRANSFERENCIAS CORRIENTES”
  * `29` – “ADQUISICIÓN DE ACTIVOS NO FINANCIEROS”
  * `33` – “TRANSFERENCIAS DE CAPITAL”
* Observaciones: aparece “FONDO PARA LA PRODUCTIVIDAD” en algunas filas (señalando líneas vinculadas a ese fondo).

**Coherencia y calidad**

* Sin `#REF!`.
* Coherencia aritmética fila a fila: el `PPTO final` coincide con `vigente ± modificación`, pero **se mezclan aumentos (suma) y rebajas (resta) con montos positivos** (el signo no es consistente).
* Requiere normalización de signo vía `final - vigente`.
* Buena riqueza de detalle (ASIG) y con notas (OBS), útil para modelar.

---

### 4.4. MODIFICACIÓN N°3.csv

**Metadatos**

* Título: “MODIFICACIÓN PRESUPUESTARIA N°03”
* Año indicado: **2025**
* Bloque: **GASTOS**
* Incluye OBS: “Fondo de la Productividad” y “Ejecución desde el año 2023”.

**Estructura**

* 1 bloque `GASTOS`.
* Incluye columna `C/M` y columna `OBS`.
* ASIG detalladas: **16**.

**Contenido**

* Totales del bloque `GASTOS`: modificación total **0** (reasignación).
* Subtítulos presentes:

  * `24` – “TRANSFERENCIAS CORRIENTES”
  * `33` – “TRANSFERENCIAS DE CAPITAL”
* Muchas ASIG están etiquetadas como “Fondo de la Productividad” (en OBS), y hay aportes a municipalidades con marca `C`.

**Coherencia y calidad**

* Sin `#REF!`.
* Aritmética consistente, pero igual que en N°2: existen filas donde la “Modificación” es positiva y se aplica como resta (rebaja), y en otras como suma (aumento).
* Es una de las hojas **más integrables** (estructura rica + sin errores de referencia).

---

### 4.5. MODIFICACIÓN N°3 SIN EFECTO.csv

**Metadatos**

* Título: “MODIFICACIÓN PRESUPUESTARIA N°003”
* Incluye fecha: **21 de marzo de 2024**
* Tag por archivo: **SIN EFECTO**
* Tiene dos bloques: **INGRESOS** y **GASTOS**.

**Estructura**

* 2 bloques (Ingresos y Gastos).
* Estructura “simple” (sin columna C/M).
* Presenta `#REF!` en montos del bloque INGRESOS.

**Contenido**

* `INGRESOS`: subtítulo `13` (“TRANSFERENCIAS PARA GASTOS DE CAPITAL”) y detalle asociado.
* `GASTOS`: `24` (“TRANSFERENCIAS CORRIENTES”), con ASIG `006` (PROEMPLEO).

**Coherencia y calidad**

* En INGRESOS hay `#REF!` en columnas clave (vigente/final), lo que impide trazabilidad completa.
* En GASTOS los montos sí se ven coherentes.
* Dado el “SIN EFECTO”, esta hoja debería tratarse como **registro histórico/anulado**, no aplicable a consolidación.

---

### 4.6. MODIFICACIÓN N°4.csv

**Metadatos**

* Título: “MODIFICACIÓN PRESUPUESTARIA N°004”
* 2 bloques: **INGRESOS** y **GASTOS**.

**Estructura**

* Incluye columna `C/M` en el bloque de GASTOS.
* Presenta `#REF!` (notablemente en totales y subtítulos de GASTOS).

**Contenido**

* `INGRESOS`:

  * `06` – “RENTAS DE LA PROPIEDAD”
  * `08` – “OTROS INGRESOS CORRIENTES”
* `GASTOS`:

  * `29` – “ADQUISICIÓN DE ACTIVOS NO FINANCIEROS”
  * `31` – “INICIATIVAS DE INVERSIÓN”
  * Muestra detalle de iniciativas/proyectos (ASIG), con marcas `M` y `C` en algunos casos.

**Coherencia y calidad**

* **Presencia de `#REF!`** en presupuesto vigente/final en varias filas y en el total del bloque de GASTOS.
* Aunque algunas filas de modificación tienen valores, falta base para calcular correctamente el saldo final en varias líneas.
* Recomendable re‑exportar valores calculados (pegado como valores) o reparar fórmulas antes de exportar.

---

### 4.7. MODIFICACIÓN N°5 SIC.csv

**Metadatos**

* Título: “MODIFICACIÓN PRESUPUESTARIA N°005”
* 2 bloques: **INGRESOS** y **GASTOS**
* Tag por archivo: **SIC** (posible versión corregida/ajustada).

**Estructura**

* Incluye columna `C/M`.
* Presenta `#REF!` en GASTOS.
* Inconsistencia: en encabezados de montos aparecen **N°5** (en INGRESOS) y **N°4** (en GASTOS).

**Contenido**

* `INGRESOS`:

  * `15` – “SALDO INICIAL DE CAJA” (con aumento)
* `GASTOS`:

  * `34` – en esta hoja se rotula como “TRANSFERENCIAS DE CAPITAL” y se muestra ítem `07`.

**Coherencia y calidad**

* La lógica global de “ingreso financia gasto” está presente (mismos montos en modificación), pero:

  * `#REF!` limita la auditabilidad del bloque GASTOS.
  * La discrepancia “Modificación N°4” dentro de una hoja N°5 es un **riesgo crítico de trazabilidad**.

---

### 4.8. REBAJA FUNC. N°6 sin efecto.csv

**Metadatos**

* Título: “MODIFICACIÓN PRESUPUESTARIA N°006”
* Tag por archivo: **REBAJA**, **SIN EFECTO**
* Bloque: `GASTOS`

**Estructura**

* 1 bloque `GASTOS`.
* Con columna `C/M`.
* Presenta `#REF!` en subtítulo `31`.

**Contenido**

* Subtítulos:

  * `13` – “TRANSFERENCIAS PARA GASTOS DE CAPITAL”
  * `31` – “INICIATIVAS DE INVERSIÓN”
* La modificación que se alcanza a ver en detalle incluye un ajuste negativo (ej.: `-350.000`) asociado a iniciativas.

**Coherencia y calidad**

* `#REF!` impide reconstrucción completa en `31`.
* Por ser “sin efecto”, debe tratarse como modificación anulada.

---

### 4.9. MODIFICACIÓN Nº7.csv

**Metadatos**

* Título: “MODIFICACIÓN PRESUPUESTARIA N°007”
* Bloque: `GASTOS`

**Estructura**

* 1 bloque `GASTOS`.
* Sin columna `C/M`.
* No hay filas ASIG detalladas (solo SUBT/ITEM).
* Sin `#REF!`.

**Contenido**

* Subtítulos:

  * `13` – “TRANSFERENCIAS PARA GASTOS DE CAPITAL”
  * `32` – “PRÉSTAMOS”
* Ítem relevante: `06` – “Anticipos a Contratistas”

**Coherencia y calidad**

* Aritmética coherente (modificación negativa explícita, ppto final disminuye).
* Poca granularidad (sin asignaciones), lo que limita trazabilidad a nivel proyecto/beneficiario.

---

### 4.10. MODIFICACIÓN Nº9.csv

**Metadatos**

* Título: “MODIFICACIÓN PRESUPUESTARIA N°09”
* Tiene parámetro visible `-35%`
* Encabezados de montos incluyen **MODIFICACIÓN N°9** y **MODIFICACIÓN N°4** (dos columnas de modificación).

**Estructura**

* 1 bloque sin etiqueta `INGRESOS/GASTOS` (el total aparece pero sin texto “GASTOS”).
* Con columna `C/M`.
* **Es la hoja con más variación estructural** (más columnas numéricas).
* **Alta presencia de `#REF!`** (incluye incluso `DENOMINACIONES` en algunas ASIG).

**Contenido**

* Subtítulos:

  * `24` – “TRANSFERENCIAS CORRIENTES”
  * `31` – “INICIATIVAS DE INVERSIÓN”
* ASIG detalladas: **17**, pero 5 de ellas tienen `DENOMINACIONES = #REF!` (se pierde el nombre del concepto).

**Coherencia y calidad**

* **Calidad baja** respecto al resto por:

  * `#REF!` masivo.
  * Doble columna de modificación (N°9 y N°4) sin explicación en datos.
  * Columnas extra sin rótulo claro (posible cálculo asociado a -35%).
* Para uso analítico, esta hoja requiere **reparación/re‑exportación** desde el Google Sheet (con fórmulas resueltas) o reconstrucción manual.
