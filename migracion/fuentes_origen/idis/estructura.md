# Estructura IDIS Legacy---

## 1) Inventario de hojas y perfil cuantitativo

Resumen de estructura y “salud” (vacíos, errores típicos de exportación de fórmulas, etc.):

| Hoja          | Filas | Columnas | Filas vacías (100%) | Columnas vacías (100%) | % celdas vacías | Celdas con errores (#REF/#VALUE/...) |
| ------------- | ----: | -------: | ------------------: | ---------------------: | --------------: | -----------------------------------: |
| 192021222324  |    12 |        9 |                   0 |                      0 |            16.7 |                                    0 |
| 2022          |    51 |       17 |                   8 |                      1 |            67.1 |                                    0 |
| 2023          |    34 |       21 |                   2 |                      0 |            41.6 |                                    0 |
| 2024          |    25 |       17 |                   0 |                      0 |            41.2 |                                    0 |
| 2025          |    29 |       17 |                   0 |                      0 |            32.5 |                                    0 |
| ANALISIS      |  2794 |       78 |                 189 |                      1 |            46.6 |                                  140 |
| CONSOLIDADO   |  2477 |      151 |                 195 |                      1 |            70.8 |                                 2432 |
| DIPIR 2021    |    34 |       16 |                   2 |                      1 |            35.8 |                                    0 |
| MAESTRA DIPIR |  1267 |      228 |                  54 |                     52 |            83.3 |                                    0 |
| MASTER        |  1544 |      113 |                   0 |                     27 |            51.1 |                                 9521 |

Lectura rápida:

* **ANALISIS** es una tabla “por iniciativa” relativamente coherente (aunque con vacíos y algunos #VALUE!).
* **MAESTRA DIPIR** es una tabla “financiera por línea presupuestaria” (muy ancha y con muchas columnas vacías/ruido).
* **CONSOLIDADO** parece ser el “join” de ambas (metadatos + financiero), pero arrastra **columnas rotas** y **muchísima dispersión**.
* **MASTER** contiene gran cantidad de **errores #REF!/#VALUE!** y campos que no calzan con su encabezado (problema serio de calidad/consistencia).
* Las hojas **DIPIR 2021, 2022, 2023, 2024, 2025** y **192021222324** son **reportes agregados** tipo matriz mensual (no están normalizadas).

---

## 2) Estructura global de la planilla: entidades, claves, relaciones y jerarquías

### 2.1 Entidades implícitas (modelo conceptual)

Se distinguen dos “módulos”:

**A) Cartera/Seguimiento por iniciativa (nivel registro):**

* **Iniciativa/Proyecto**: la entidad central.

  * Identificador principal: `COD. ÚNICO` / `CODIGO ÚNICO` / `Codigo Unico`.
* **Clasificación presupuestaria** (estructura jerárquica):

  * `SUBT` → `ITEM` → `ASIG` (y el texto de línea: `NOMBRE LINEA`).
* **Identificación sectorial y territorial**:

  * `BIP` + `DV` (cuando existe), `PROVINCIA`, `COMUNA`.
* **Gestión / proceso** (flujo):
  Campos de “estado/rate/fechas” (postulación, envío a Mideso, respuesta, Core, certificado, convenio, licitación/empresa, etc.).
* **Finanzas y ejecución**:

  * Montos (iniciativa/sectorial/FNDR/final), `GASTO VIGENTE`, `ARRASTRE`, y (en algunas hojas) detalle mensual proyectado/real.

**B) Seguimiento DIPIR agregado (nivel reporte):**

* Tablas matriciales por año con filas “indicador” y columnas “mes”.
* Una tabla resumen multi-año de porcentajes acumulados por mes.

### 2.2 Claves y granularidad real (importante)

La “clave” (código único) **no es única por fila** en las hojas grandes: hay duplicados. Esto sugiere que el grano correcto suele ser:

* **Grano probable (financiero):** `CODIGO ÚNICO` + `SUBT` + `ITEM` + `ASIG` (+ `AÑO PRESUPUESTARIO` cuando aplica).
  En **MAESTRA DIPIR**, este grano se ve muy claro: cuando esos campos están completos, **la combinación es prácticamente única**.

* **Grano probable (gestión):** `COD. ÚNICO` (+ `AÑO PRESP.` / `VIGENCIA`) según el tipo de iniciativa.

### 2.3 Calidad de la clave (por hoja principal)

| Hoja          | Columna clave | Filas | Códigos únicos (no nulos) | Códigos faltantes | Duplicados | Placeholder “-” | Errores fórmula en clave | Alfanuméricos | Numérico-año |
| ------------- | ------------- | ----: | ------------------------: | ----------------: | ---------: | --------------: | -----------------------: | ------------: | -----------: |
| MASTER        | Codigo Unico  |  1544 |                      1436 |                 2 |        106 |               0 |                        9 |             0 |         1531 |
| ANALISIS      | COD. ÚNICO    |  2794 |                      2164 |               317 |        130 |               3 |                        0 |             0 |         2472 |
| CONSOLIDADO   | COD. ÚNICO    |  2477 |                      2018 |               197 |        262 |             215 |                        0 |            95 |         1963 |
| MAESTRA DIPIR | CODIGO ÚNICO  |  1267 |                      1131 |                68 |         58 |               0 |                        0 |           127 |         1014 |

Puntos críticos:

* En **CONSOLIDADO** aparecen muchos códigos con `"-"` (placeholder), y en **MAESTRA DIPIR** aparecen códigos tipo `-2023` (placeholder/año suelto). Esos valores **no sirven como llave** y deberían tratarse como nulos.
* Hay códigos **alfanuméricos** en CONSOLIDADO/MAESTRA (p.ej. `2501RC003-2025`), lo que implica que no todo sigue el patrón `NNNNNNNN-AAAA`.

### 2.4 Jerarquías que se pueden reconstruir

* **Territorio:** `PROVINCIA` → `COMUNA`.
* **Presupuesto:** `SUBT` → `ITEM` → `ASIG` → `NOMBRE LINEA`.
* **Tiempo / vigencia:** `AÑO` / `AÑO PRESP.` / `VIGENCIA` (y series mensuales cuando hay detalle).

---

## 3) Descripción por hoja: contenido, estructura y calidad

### 3.1 Hoja `ANALISIS` (ANÁLISIS.csv)

**Qué es:**
La hoja más parecida a una **“tabla maestra de iniciativas”** orientada a **gestión/flujo** y datos base (clasificación, territorio, montos y estado).

**Tamaño y estructura:** 2.794 filas × 78 columnas.
Tiene **189 filas completamente vacías** (ruido de exportación o filas separadoras).

**Campos principales (agrupados):**

* **Identificación:** `COD. ÚNICO`, `VIGENCIA`, `AÑO`, `AÑO PRESP.`, `BIP`, `DV`, `NOMBRE INICIATIVA`.
* **Clasificación:** `ETAPA`, `TIPOLOGÍA`, `ORIGEN`, `UNIDAD TÉCNICA`, `PROVINCIA`, `COMUNA`, `SUBT`, `ITEM`, `ASIG`, `NOMBRE LINEA`.
* **Montos/finanzas:** `MONTO INICIATIVA`, `MONTO SECTORIAL`, `MONTO FNDR`, `MONTO FINAL APROB.`, `GASTO VIGENTE`, `GASTO SIG. AÑOS`.
* **Beneficiarios y priorización:** `N° BENEF DIRECTOS TOTAL`, `EJE`, `LINEA PRIORITARIA`, `PRIORIZADO GOBERNADOR`.
* **Gestión / workflow:** `ESTADO ACTUAL`, `FECHA ESTADO ACTUAL`, `RATE ACTUAL`, `FECHA ULTIMO RATE`, `N° RATES EMITIDOS`, y fechas del circuito (postulación, envío Mideso, respuesta, Core, etc.).

**Calidad / coherencia:**

* **Montos:** numéricamente consistentes (parseables cuando están presentes).
* **Fechas:** mayormente consistentes, pero con **formatos mezclados** (`dd-mm-aaaa`, `dd.mm.aaaa`, `m/d/yyyy`). Se pueden parsear con un parser “mixed”, pero para análisis serio conviene **normalizar a ISO (YYYY-MM-DD)**.
* **Errores:** 140 celdas con `#VALUE!/#REF!` (principalmente en `CONTROL DE DIAS`).
* **Problema de encabezados:** hay columnas cuyo nombre incluye **saltos de línea** (p.ej. `N° MEMO PRESUPESTO\nRES. APRUEBA CONV`). Eso sugiere encabezados “compuestos” en la planilla original (celdas fusionadas o textos multilínea), lo que complica usar el CSV como diccionario limpio.

**Conclusión:**
Es la mejor base para una **tabla “iniciativas”** (dimensión) si se limpian filas vacías, se normalizan fechas y se revisa `CONTROL DE DIAS`.

---

### 3.2 Hoja `MAESTRA DIPIR` (MAESTRA DIPIR.csv)

**Qué es:**
Una **maestra financiera DIPIR** por iniciativa y **línea presupuestaria** (SUBT/ITEM/ASIG), con ejecución histórica y seguimiento mensual **proyectado vs real** para varios años (al menos 2022–2025), más arrastres.

**Tamaño y estructura:** 1.267 filas × 228 columnas.
Es extremadamente “ancha” (muchas columnas de meses/años) y por eso tiene **83% de celdas vacías**, lo cual es esperable si no todas las iniciativas tienen data en todos los años.

**Grano (muy probable):**

* Por los resultados, la combinación **`CODIGO ÚNICO + SUBT + ITEM + ASIG`** es prácticamente única cuando esos campos están completos, lo que indica una **tabla de líneas** (no solo proyectos).

**Campos principales (agrupados):**

* **Identificación/clasificación:** `CODIGO ÚNICO`, `AÑO PRESUPUESTARIO`, `UNIDAD TÉCNICA`, `ORIGEN`, `TIPOLOGIA`, `PROVINCIA`, `COMUNA`, `CODIGO BIP`, `SUBT`, `ITEM`, `ASIG`, `NOMBRE INICIATIVA`, `NOMBRE LINEA`.
* **Montos base:** `MONTO INICIATIVA`, `MONTO SECTORIAL`, `MONTO FNDR`, `MONTO FINAL APROB.`, `GASTO VIGENTE`, `GASTO SIG. AÑOS`.
* **Ejecución histórica:** `EJEC. 2019`, `EJEC. 2020`, `EJEC. 2021` + columnas mensuales asociadas.
* **Seguimiento anual detallado:** bloques repetidos de:

  * `ENERO PROYECTADO` / `ENERO REAL` … `DICIEMBRE PROYECTADO` / `DICIEMBRE REAL`
  * `TOTAL PROYECTADO <año>`, `TOTAL REAL <año>`, `DIFERENCIA`.
* **Arrastres:** `ARRASTRE 2025`, `ARRASTRE 2026`, etc.
* **Resumen adicional:** `ppto`, `saldo`, etc.

**Calidad / coherencia:**

* **Sin errores de fórmula** (#REF/#VALUE) en el CSV.
* **Mucho ruido estructural:** 52 columnas totalmente vacías y muchas columnas tipo `' .1'...' .44'` (nombres raros), lo que sugiere **columnas residuales** del sheet (separadores, cálculos, columnas ocultas, etc.) que deberían eliminarse del modelo final.
* **Formato ITEM/ASIG:** en esta hoja aparecen con **ceros a la izquierda** (ej. `03`, `01`) mientras que en otras hojas aparecen como `3`, `1`. Esto afecta joins si no se estandariza.
* **Aumento de plazo:** en `AUMENTO DE PLAZO (PARALIZACIÓN)` hay algunas entradas no numéricas (`27-8-24`, `58+88`). Son pocas, pero conviene normalizar.

**Conclusión:**
Es el insumo más sólido para el **módulo financiero** (por línea presupuestaria), pero requiere **poda de columnas basura** y estandarización de formatos.

---

### 3.3 Hoja `CONSOLIDADO` (CONSOLIDADO.csv)

**Qué es:**
Una hoja “súper ancha” que parece mezclar:

* datos base y workflow (similar a `ANALISIS`), y
* datos financieros/mensuales (similar a `MAESTRA DIPIR`).

Es decir, una tabla “consolidada” para análisis/reportería integral.

**Tamaño y estructura:** 2.477 filas × 151 columnas.
Tiene 195 filas completamente vacías (ruido).

**Relación con otras hojas:**

* Comparte **70 columnas** con `ANALISIS`.
* Comparte **70 columnas** con `MAESTRA DIPIR`.
* Tiene **81 columnas adicionales** respecto de `ANALISIS` (principalmente meses, totales, arrastres y columnas duplicadas).

**Problemas de calidad muy relevantes:**

1. **Columna `cruce` rota:** prácticamente toda llena con `#REF!` (2.217 ocurrencias).
   → Es una columna derivada por fórmula que quedó inválida al exportar.
2. **Bloques de columnas “corridas o reutilizadas”**: hay columnas cuyo contenido no coincide con el encabezado esperado. Ejemplos claros:

   * `MONTO SECTORIAL M$` contiene **textos (nombres de iniciativas)** en muchos casos, no montos.
   * `EJEC. 2019` contiene **nombres de personas** (no ejecución).
   * `EJEC. 2020` contiene **nombres de divisiones** (p.ej. DIPIR/DIPLADE), no montos.
   * `AUMENTO DE PLAZO (PARALIZACIÓN)` contiene **RUTs** en muchos registros.

   Esto suele ocurrir cuando la hoja se usa como “tablero” y se van pegando/arrastrando columnas, o cuando hay “secciones” con distinto significado en el mismo rango.
3. **Sparsidad extrema:** muchas columnas (especialmente mensuales “REAL”) están **>99% vacías**, lo que sugiere:

   * o no se está capturando ese detalle realmente,
   * o el detalle está en otra parte y quedó como estructura “plantilla”.

**Qué sí se ve consistente:**

* La parte “tipo ANALISIS” (identificación/territorio/clasificación/estado/fechas) es bastante consistente y coincide con `ANALISIS` en nombre de iniciativa (pocos desalineamientos, mayormente de redacción).
* Muchos montos/totales mensuales sí son numéricos cuando están presentes.

**Conclusión:**
Sirve como hoja de “consumo” para reportes, pero **no es una fuente confiable** sin una limpieza fuerte: remover `cruce`, identificar y/o corregir el bloque de columnas con contenido desplazado, y separar en tablas normalizadas.

---

### 3.4 Hoja `MASTER` (MASTER.csv)

**Qué es:**
Un “master” histórico/snapshot de iniciativas con muchos campos de seguimiento.

**Tamaño y estructura:** 1.544 filas × 113 columnas.

**Calidad (la más problemática):**

* **9.521 celdas con errores** (#REF!/ #VALUE!/ etc).
  Hay columnas completas que son **100% #REF!** (p.ej. `Prov Subdere`, `Fecha 1° ADM / INAD`, etc.), típicamente por fórmulas que referenciaban otras hojas/rangos.
* **27 columnas completamente vacías.**
* **Desalineación semántica de campos:**

  * `Primer Rate` está completamente vacío, mientras `Fecha Primer Rate` contiene categorías como `RS`, `FI`, `ADMISIBLE`, etc. (o sea: el contenido de Rate cayó en la columna de fecha).
  * `MONTO FNDR POSTULADO` contiene **nombres de proyectos** (no montos) en la mayoría de casos.
  * `EJEC. 2019` contiene **RUTs** (no ejecución).
  * `SUBT.` y `SUBT. - ITEM` no son numéricos (0% numérico), contienen textos (p.ej. provincia/comuna), lo que contradice el significado esperado.

**Conclusión:**
Esta hoja, en su estado exportado, es **riesgosa como fuente**. Se entiende como “hoja operativa” con muchas fórmulas; para análisis, habría que:

* convertir `#REF!/#VALUE!` a nulos y recalcular desde fuente,
* redefinir qué columnas realmente representan (varias parecen reusadas o corridas),
* o directamente priorizar `ANALISIS` + `MAESTRA DIPIR` como fuentes.

---

### 3.5 Hojas DIPIR anuales: `DIPIR 2021`, `2022`, `2023`, `2024`, `2025`

**Qué son:**
Reportes agregados mensuales por año. Se estructuran como matrices:

* columnas: meses (`ENERO` … `DICIEMBRE`)
* filas: indicadores tipo:

  * `MARCO PRESUPUESTARIO VIGENTE`
  * `EJECUTADO PROGRAMA MES` / `EJECUTADO REAL MES`
  * `% EJECUTADO PROGRAMA MES` / `% EJECUTADO REAL MES`
  * `EJECUTADO PROGRAMA ACUM` / `EJECUTADO REAL ACUM`
  * `% EJECUTADO PROGRAMA ACUM` / `% EJECUTADO REAL ACUM`
  * `DIFERENCIA` (en algunos años)

**Rasgo estructural clave:**
No son “una tabla única”, sino que suelen contener **varias secciones** en la misma hoja:

* la matriz principal (montos y %),
* una tabla “MES vs % acumulado” (histórica o proyectada),
* en 2021–2023 aparece además un bloque tipo **“Rebajas/Ajustes”** con SUBT y montos.

**Problemas de calidad/consistencia:**

* **No normalizadas:** mezclar montos y porcentajes en el mismo bloque hace que las columnas de meses tengan **tipos mezclados** (esperable en un reporte, pero no ideal para modelo de datos).
* **Filas separadoras y columnas extra**:

  * en `2022` aparecen nombres de columnas “numéricas” (`0.8160521122`, etc.), típicas de valores que quedaron en la fila usada como header al exportar.
  * en `2025` el encabezado arranca como `TOTAL 2024` aunque el archivo es 2025 → evidencia de plantilla no actualizada.
* Muchas celdas vacías, especialmente en secciones secundarias.

**Conclusión:**
Estas hojas son **buenas para lectura humana** y para explicar resultados, pero para analítica deben transformarse a algo como:
`(año, indicador, mes, valor, tipo_valor)` y separar rebajas en otra tabla.

---

### 3.6 Hoja `192021222324` (192021222324.csv)

**Qué es:**
Una tabla compacta de **porcentaje acumulado de ejecución** por mes, comparando años 2019–2025.

**Estructura:** 12 filas (ENE–DIC) × 9 columnas (`MES` + `2019`…`2025`).
Es la hoja más “limpia” del módulo DIPIR.

**Calidad:**

* Formato consistente en porcentajes.
* `2025` está incompleto (hay valores hasta `SEP` y luego nulos), lo que es coherente si el año está en curso al momento del corte.

---

## 4) Coherencia del conjunto completo: hallazgos y riesgos

### Coherencias fuertes

* Existe un **núcleo común de campos** (código único, años, BIP/DV, territorio, SUBT/ITEM/ASIG, nombre de iniciativa) que se repite en `ANALISIS`, `CONSOLIDADO`, `MAESTRA DIPIR`.
* La jerarquía **SUBT/ITEM/ASIG** está muy presente y coincide con subtítulos típicos (33, 31, 29, 24), alineable con las secciones “Rebajas” en DIPIR anuales.
* `CONSOLIDADO` coincide ampliamente con `ANALISIS` para nombres/códigos (diferencias menores de redacción o etiquetas como “(NO VIGENTE)”).

### Incoherencias / problemas de calidad (los más importantes)

1. **Errores de fórmula exportados como texto** (#REF!, #VALUE!): muy severo en `MASTER`, importante en `CONSOLIDADO` (`cruce`).
2. **Columnas cuyo contenido no calza con el encabezado** (reutilización/desplazamiento de bloques), especialmente en `MASTER` y `CONSOLIDADO`.
3. **Claves con placeholders** (`-`, `-2023`) que rompen cualquier relación entre hojas si no se limpian.
4. **Formatos heterogéneos**:

   * `ITEM/ASIG` con y sin ceros a la izquierda,
   * fechas en múltiples formatos y, en algunos casos, números tipo “serial Excel” formateados como moneda o texto.
5. **Sparsidad** excesiva en hojas anchas: muchas columnas “plantilla” nunca se usan (vacías o >90% vacías), lo que dificulta análisis y aumenta riesgo de interpretación errónea.
