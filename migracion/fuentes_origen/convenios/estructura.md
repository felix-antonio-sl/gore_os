# Estructura legay

## 1) Panorama general del Google Sheet (estructura global)

El archivo completo (Google Sheet) está compuesto por **3 hojas**, cada una exportada como .csv:

| Hoja                      | Filas | Columnas | Filas con CODIGO | CODIGO únicos | CODIGO faltantes | CODIGO repetidos* |
| ------------------------- | ----: | -------: | ---------------: | ------------: | ---------------: | ----------------: |
| **CONVENIOS 2023 y 2024** |   408 |       24 |              405 |           397 |                3 |                 8 |
| **CONVENIOS 2025**        |   106 |       21 |              106 |           106 |                0 |                 0 |
| **MODIFICACIONES**        |    30 |       19 |               29 |            22 |                1 |                 7 |

*“Repetidos” = apariciones extra sobre los únicos (p.ej. 2 filas con el mismo CODIGO generan 1 repetido).

### Rol de cada hoja dentro de la planilla

* **CONVENIOS 2023 y 2024** y **CONVENIOS 2025**: son esencialmente la **misma entidad** (registro/seguimiento de convenios por iniciativa), pero **separada por período**. Contienen identificación presupuestaria, identificación de la iniciativa, territorio, monto FNDR, y un conjunto de hitos/estados documentales (resoluciones, CGR, oficios, referente técnico).
* **MODIFICACIONES**: hoja adicional de **seguimiento documental** orientada a **convenios de transferencia de bienes** y **modificaciones de convenio**, incorporando el **RUT de la institución** y datos de **resolución** (N°/fecha/tipo) más estados asociados.

---

## 2) Modelo conceptual del conjunto (campos, relaciones y jerarquías)

### 2.1 Entidades implícitas

En términos de modelo de datos, las hojas representan (implícitamente) estas entidades:

1. **Convenio / Iniciativa (principal)**
   Representada por una fila en las hojas “CONVENIOS …”. Campos: clasificación (SUB/ITEM/ASIG), CODIGO, unidad técnica, nombre iniciativa, territorio, monto, y el “pipeline” documental (resoluciones, CGR, oficios, referente).

2. **Documentos e hitos administrativos (atributos del convenio)**
   N° y fecha de:

   * “Incorpora / Cert CORE”
   * “Crea asignación”
   * “Aprueba convenio” (y tipo de resolución, cuando existe)
   * “Oficio envía convenio”
   * “Toma de razón CGR” y estado en CGR
   * “Referente técnico” (y en 2023–2024 incluso “N° res referente técnico”)

3. **Modificación / convenio de transferencia (evento o subtipo)**
   Hoja “MODIFICACIONES” agrega:

   * **RUT INSTITUCIÓN**
   * **TIPO DE CONVENIO** (p.ej. transferencia de bienes / modificación)
   * **N° y fecha de resolución** asociada
   * Estado/etapa (campos “ESTADO DE CONVENIO” y un campo adicional “ESTADO”)

### 2.2 Jerarquías explícitas (cómo “cuelgan” los datos)

* **Jerarquía presupuestaria (muy consistente como concepto):**
  **SUB → ITEM → ASIG → CODIGO**
  donde:

  * **SUB** (numérico) agrupa grandes líneas.
  * **ITEM** y **ASIG** refinan la clasificación (aunque en los datos aparecen valores múltiples/formatos inconsistentes).
  * **CODIGO** identifica la iniciativa/convenio (pero **no siempre es estrictamente único** en 2023–2024 y **no es único** en MODIFICACIONES).

* **Jerarquía territorial:**
  **PROVINCIA → COMUNA** (solo en hojas CONVENIOS).
  En la práctica, **COMUNA** se usa a veces con valores de ámbito mayor (p.ej. “REGIONAL”, e incluso nombres de provincia).

* **Jerarquía de proceso (pipeline documental):**
  Se observan campos que, juntos, describen un flujo típico:

  1. Incorpora/Cert CORE
  2. Crea asignación
  3. Firma convenio
  4. Resolución aprueba convenio
  5. Estado en CGR + Toma de razón
  6. Oficio envía convenio
     (y en 2025 aparece además “estado res crea asignación en CGR”)

> Importante: el orden cronológico “ideal” puede variar según interpretación institucional; en los datos hay señales de que **“Oficio envía convenio” no siempre es previo** a la fecha CGR (lo que sugiere ambigüedad semántica o uso distinto del campo).

### 2.3 Relaciones entre hojas (y su “salud”)

* **Relación esperable:**
  MODIFICACIONES debería relacionarse con CONVENIOS mediante **CODIGO** (y posiblemente también **institución/RUT** cuando corresponda).
* **Lo que muestran los datos:**

  * Entre **MODIFICACIONES** y **CONVENIOS (2023–2025)** solo hay **2 CODIGO en común** (de 22 códigos únicos en MODIFICACIONES).
    Esto indica que:

    * MODIFICACIONES cubre **otro universo** (códigos de años anteriores/no incluidos), y/o
    * en MODIFICACIONES el **CODIGO se usa a otro nivel de granularidad** (programa/paquete), y/o
    * hay **faltantes / divergencias** en cómo se registran los códigos.
  * Entre **CONVENIOS 2023–2024** y **CONVENIOS 2025** hay **6 CODIGO compartidos**, lo que sugiere iniciativas que aparecen en ambos periodos o continuidad administrativa.

---

## 3) Hoja: CONVENIOS 2023 y 2024 (24 columnas)

### 3.1 Grano (qué representa una fila)

En general, **una fila = una iniciativa/convenio** (identificada por CODIGO), con su clasificación presupuestaria, territorio, monto y avance documental.
**Excepción/alerta:** hay **duplicados de CODIGO** (8 apariciones extra) y **3 filas “residuales”** sin CODIGO (solo SUB/ITEM), que rompen el grano.

### 3.2 Campos (diccionario estructurado)

**A) Identificación presupuestaria**

* **SUB** (int): código de subtítulo (4 valores distintos).
* **ITEM** (texto): normalmente 2 dígitos (03/02/01/05…), pero existen valores **multi‑item** como `03/05`, `05/07`, `03/05/06`.
* **ASIG** (texto): mezcla de códigos (muchos `125`, `300`, etc.), además de `-` y algunos multi‑valor (`002/004`, `005/006`).
* **CODIGO** (texto): identificador de iniciativa. Es **mixto**:

  * Mayoría numérica de 8 dígitos.
  * Un subconjunto alfanumérico tipo **`CVC-AD-…`** (33 registros), asociado a montos mucho menores (ver coherencia financiera más abajo).

**B) Identidad de la iniciativa**

* **UNIDAD TECNICA** (texto): institución ejecutora (municipios/servicios/universidades, etc.). Hay **variantes de escritura** (abreviaciones vs nombre completo, mayúsculas, espacios).
* **NOMBRE DE LA INICIATIVA** (texto): descripción larga, generalmente consistente.

**C) Territorio**

* **PROVINCIA** (texto): 4 valores (REGIONAL + 3 provincias). ~5% faltante.
* **COMUNA** (texto): 24 valores únicos tras normalizar espacios; aparecen valores de “ámbito” como **REGIONAL** y también **ITATA/PUNILLA** como “comuna” (lo que sugiere uso del campo para ámbito territorial, no solo comuna).

**D) Financiero**

* **MONTO FNDR M$** (texto): siempre con `$` y separadores de miles. Es 100% parseable a número (tras limpiar símbolos).

  * Hay **dos escalas** claras por tipo de CODIGO:

    * Códigos `CVC-AD`: mediana aprox. **15.000** (en la unidad del campo M$)
    * Códigos numéricos: mediana aprox. **163.016**, máximo aprox. **14.326.610**

**E) Hitos CORE / asignación / convenio**

* **Nº RES INCORPORA/ CERT CORE** + **FECHA RES INCORPORA/ CERT CORE**: muy completos (~94%). El “Nº” mezcla formatos (algunos con `/año`, otros solo número).
* **Nº RES CREA ASIGNACIÓN** (numérico, guardado como float por NaN) + **FECHA RES CREA ASIGNACIÓN**: muy completos (~98%).
* **ESTADO DE CONVENIO**: mayoritariamente **FIRMADO** (388 de 405 con CODIGO = **95,8%**). También: ENCOMENDADO DIT, NO SE FIRMO, RS NO VIGENTE, INGRESARÁ A RE.
* **FECHA FIRMA DE CONVENIO**: casi completa, pero contiene entradas no‑fecha (p.ej. `FIN FECHA`, `-`).

**F) Resolución que aprueba convenio**

* **Nº RES APRUEBA CONVENIO** + **FECHA RES APRUEBA CONVENIO**: casi completos (~99% y ~98%).
  Problemas puntuales: strings no‑fecha y errores tipográficos (ej.: `14-089-2024`).
* **TIPO DE RESOLUCIÓN**: principalmente **EXENTA** y **AFECTA**, pero también `-` y algunos nulos.

**G) Contraloría (CGR)**

* **ESTADO CONVENIO EN CGR**: **67,4% vacío**. Cuando existe, valores: TOMADO DE RAZON, T.R CON ALCANCES, REPRESENTADO, EN CGR, `-`.
* **FECHA TOMA DE RAZON DE CGR**: **68,9% vacío**. Además, aparecen valores no válidos como `036-10-2024` y `-`.

**H) Oficios**

* **Nº OFICIO ENVIA CONVENIO** + **FECHA OFICIO ENVIA CONVENIO**: **57,8% vacío**. En “Nº” aparecen casos `EN TRAMITE` y `-`.

**I) Referente técnico**

* **REFERENTE TECNICO O CONTRAPARTE TECNICA**: 91% completo, pero mezcla **personas** y **áreas** (p.ej. nombres propios vs “DIPLADE/DIT”), con inconsistencias por tildes y espacios.
* **Nº RES REFERENTE TECNICO**: 51,7% vacío; cuando existe suele venir como `número/dd.mm.aaaa` y también valores de trámite (`RES EN TRAMITE`) o `-`.

### 3.3 Calidad de datos (coherencia y problemas)

**Fortalezas**

* Montos altamente consistentes y parseables.
* La mayoría de fechas clave son parseables (con limpieza de separadores).
* Proceso “core” (incorpora, crea asignación, aprueba convenio) muy completo para 2023–2024.

**Problemas detectados**

* **Filas residuales**: 3 filas sin CODIGO (solo SUB/ITEM), claramente incompletas.
* **Duplicación**:

  * 2 duplicados exactos de fila completa.
  * 8 CODIGO con doble registro; algunos son duplicados “cosméticos” (variación de unidad), pero otros presentan **diferencias sustantivas** (distinto nombre de iniciativa y monto con el mismo CODIGO), lo que pone en duda la unicidad del identificador.
* **Fechas con errores**: valores no‑fecha o malformados (`FIN FECHA`, `14-089-2024`, `036-10-2024`, `-`).
* **Campos con valores múltiples en una celda** (ITEM y ASIG), que rompen normalización (no es una relación 1:1 sino 1:N embebida en texto).
* **Higiene de texto**: espacios finales/iniciales en nombres y campos; diferencias de tildes (ej. misma persona con y sin tilde).

---

## 4) Hoja: CONVENIOS 2025 (21 columnas)

### 4.1 Grano

Una fila representa una iniciativa/convenio 2025. En esta hoja, **CODIGO es único (106/106)**: no se observan duplicados.

### 4.2 Diferencias estructurales relevantes vs 2023–2024

* Se incorpora **ESTADO RES CREA EN CGR** (estado de la resolución de creación de asignación).
* Se **combinan campos** que en 2023–2024 estaban separados:

  * **Nº RES Y FECHA APRUEBA CONVENIO** viene en un solo campo con patrón `número/dd.mm.aaaa`.
  * **Nº Y FECHA OFICIO ENVIA CONVENIO** también combinado `número/dd.mm.aaaa`.
* No existe “TIPO DE RESOLUCIÓN” ni “Nº RES REFERENTE TÉCNICO” como en 2023–2024 (en su lugar queda solo REFERENTE TECNICO).

### 4.3 Campos (diccionario estructurado)

**A) Identificación presupuestaria**

* **SUB** (int), **ITEM** (texto), **ASIG** (numérico guardado como float):

  * **ASIG tiene 59,4% faltante** y aparece como `125.0`, `490.0`, etc (es un efecto de tipo numérico; conceptualmente son códigos enteros).
  * ITEM tiene un caso no estándar: `07, 06` (valor múltiple).

**B) Identidad de la iniciativa**

* **CODIGO** (texto): mayormente numérico, con 6 registros tipo `CVC-AD-…`.
* **UNIDAD TECNICA** y **NOMBRE DE LA INICIATIVA**: presentes, pero con heterogeneidad de escritura (mayúsculas/minúsculas, abreviaciones).

**C) Territorio**

* **PROVINCIA** y **COMUNA**: valores similares al set de años previos, pero con **inconsistencias ortográficas** más visibles: p.ej. `CHILLAN` vs `CHILLÁN`, `RANQUIL` vs `RÁNQUIL`, `SAN NICOLAS` vs `SAN NICOLÁS`, `ÑIQUEN` vs `ÑIQUÉN`.

**D) Financiero**

* **MONTO FNDR M$**: completamente parseable; se repite el patrón de dos escalas (CVC-AD muy bajo vs numéricos más altos).

**E) Hitos y estados**

* Incorpora/Cert CORE: alto (Nº ~95%, fecha ~91%).
* Crea asignación: ~66% (Nº y fecha).
* **ESTADO RES CREA EN CGR**: muy incompleto (~80% vacío).
* Convenio:

  * **ESTADO DE CONVENIO**: FIRMADO 58 (**54,7%**), SIN CONVENIO 46 (**43,4%**), `-` 2.
  * **FECHA FIRMA DE CONVENIO**: ~52% completo; contiene valores no‑fecha (p.ej. `UT DESISTE DE FIRMAR`, `REEVALUACION`).
* Aprobación convenio:

  * **Nº RES Y FECHA APRUEBA CONVENIO**: ~49% completo; cuando existe sigue patrón consistente `número/dd.mm.aaaa`.
* CGR:

  * **ESTADO CONVENIO EN CGR** ~17% completo;
  * **FECHA TOMA DE RAZON** ~14% completo; hay errores puntuales (`070-11-2025`).
* Oficio:

  * **Nº Y FECHA OFICIO ENVIA CONVENIO** ~30% completo; patrón consistente `número/dd.mm.aaaa`.
* **REFERENTE TECNICO**: ~43% completo; mezcla unidades (“INVERSIONES”, “DIDESOH”) con personas y combinaciones (“DIDESOH/NOMBRE”), lo que sugiere que aquí conviven **dos dimensiones** en un solo campo.

### 4.4 Calidad de datos (coherencia y problemas)

**Fortalezas**

* No hay duplicados de CODIGO.
* Los campos combinados Nº/fecha siguen un patrón consistente.
* Montos consistentes.

**Problemas**

* **Muchos faltantes “naturales”** (probablemente por año en curso / procesos no cerrados): CGR, oficios, resoluciones.
* **Contaminación de campos de fecha con texto** (anotaciones operativas).
* **Ortografía/acentos** en comunas y unidades técnicas no estandarizada.
* **ASIG numérico** (float) y con alto faltante: dificulta tratarlo como código.

---

## 5) Hoja: MODIFICACIONES (19 columnas)

### 5.1 Grano (clave real)

No es “1 fila = 1 CODIGO”.

* CODIGO aparece **repetido** (especialmente uno con 8 registros), lo que sugiere que aquí el grano es más bien:

  * **(CODIGO + Institución/RUT)** y/o **(CODIGO + Unidad técnica/Comuna)**

### 5.2 Campos (diccionario estructurado)

**A) Identificación presupuestaria**

* **SUB** (int), **ITEM** (texto), **ASIG** (texto):

  * ITEM presenta formatos no estándar (`2`, `3`, `05/06/07`).
  * ASIG está **80% vacío** y, cuando existe, puede ser multivalor (`001/002/004`).

* **CODIGO** (numérico guardado como float): debería tratarse como **texto/código**, ya que es identificador (y se pierde semántica si hubiera ceros o prefijos).

**B) Institución y localización**

* **RUT INSTITUCIÓN** (texto): 70% completo. Los RUT presentes siguen formato correcto (con dígito verificador consistente).
* **UNIDAD TECNICA**, **COMUNA**: descripción de entidad/territorio; COMUNA incluye valores combinados (`CHILLAN Y CH. VIEJO`) y errores/variantes (`SAN FABAN`, `SAN NICOLAS`).

**C) Tipo y estado**

* **TIPO DE CONVENIO**: 100% completo con 2 categorías:

  * “CONVENIO DE TRASNFERENCIA DE BIENES” (con error ortográfico en “TRASNFERENCIA”)
  * “MODIFICACION DE CONVENIO”
* **ESTADO DE CONVENIO**: 80% FIRMADO, 20% ENVIADO AL SERVICIO
* **FECHA FIRMA DE CONVENIO**: 80% completo

**D) Resolución asociada**

* **Nº RESOLUCION**, **FECHA**, **TIPO DE RESOLUCION**: ~80% completos.
  TIPO: EXENTA/AFECTA, con algunos faltantes.

**E) CGR y oficio**

* **ESTADO CONVENIO EN CGR**: ~87% vacío.
* **FECHA TOMA DE RAZON DE CGR**: ~93% vacío.
* **Nº OFICIO ENVIA CONVENIO** y **FECHA OFICIO ENVIA CONVENIO**: 50% completos.

**F) Campo “ESTADO” adicional**

* Existe un campo **“ESTADO”** aparte de “ESTADO DE CONVENIO” y de “ESTADO CONVENIO EN CGR”. Tiene ~43% lleno y valores como “ENVIADO AL SERVICIO”.
  Esto es una señal de **duplicidad semántica**: el “estado” está repartido en más de una columna sin definición única.

### 5.3 Calidad de datos

**Fortalezas**

* RUT con formato consistente en los valores presentes.
* Fechas que aparecen suelen ser parseables.

**Problemas**

* **CODIGO faltante** en una fila que, sin embargo, tiene información relevante (unidad, iniciativa, resolución): es un registro “huérfano” difícil de relacionar.
* **Clasificadores ITEM/ASIG con valores multivalor/no estándar**.
* **Multiplicidad de campos de estado** (riesgo de contradicción).
* Alto faltante en CGR (posiblemente por proceso no concluido o falta de actualización).

---

## 6) Coherencia inter-hojas (consistencia del diseño y del contenido)

### 6.1 Consistencia del esquema (nombres de columnas)

Hay un problema estructural transversal: **nombres de columnas con espacios iniciales/finales**, por ejemplo:

* `' ASIG'`, `'UNIDAD TECNICA '`, `'FECHA FIRMA DE CONVENIO '`
* En montos: `' MONTO FNDR M$ '` (2023–2024) vs `' MONTO FNDR M$'` (2025)

Esto impacta directamente:

* joins/relaciones entre hojas,
* automatización (PowerQuery/SQL),
* validaciones y control de calidad.

### 6.2 Campos equivalentes con estructuras distintas

Ejemplos:

* 2023–2024: **Nº RES APRUEBA CONVENIO** + **FECHA RES APRUEBA CONVENIO**
  2025: **Nº RES Y FECHA APRUEBA CONVENIO** (combinado)
* 2023–2024: **Nº OFICIO** + **FECHA OFICIO**
  2025: **Nº Y FECHA OFICIO** (combinado)

Esto reduce la comparabilidad y obliga a “desarmar” campos para análisis longitudinal.

### 6.3 Consistencia del identificador CODIGO

* En CONVENIOS 2025, CODIGO funciona como identificador único.
* En CONVENIOS 2023–2024, CODIGO **no es estrictamente único** (duplicados exactos y casos con diferencias sustantivas).
* En MODIFICACIONES, CODIGO **claramente no define grano**: se repite por institución/territorio.

---

## 7) Evaluación global de calidad (conjunto completo)

### 7.1 Fortaleza general

* La planilla captura bien el **ciclo de vida administrativo** (resoluciones, firma, CGR, oficios) y permite ver “etapas”.
* Los **montos** están muy bien formateados para visualización humana y son completamente transformables a numérico.
* Los estados principales (“FIRMADO”, “SIN CONVENIO”, etc.) dan trazabilidad.

### 7.2 Principales riesgos / degradadores de calidad

1. **No hay una clave primaria homogénea** para todo el libro:

   * CODIGO no alcanza en MODIFICACIONES y es imperfecto en 2023–2024.
2. **Inconsistencias de formato**:

   * Fechas con separadores mixtos y algunos valores inválidos o notas textuales.
   * ITEM/ASIG con multivalores en texto.
3. **Falta de estandarización de catálogos**:

   * COMUNA y UNIDAD TECNICA con variaciones (tildes, mayúsculas, abreviaturas, errores tipográficos).
   * REFERENTE TECNICO mezclando “persona” y “unidad”.
4. **Faltantes grandes** en etapas CGR/oficios:

   * Puede ser esperable (procesos abiertos), pero también puede indicar falta de actualización o definiciones difusas del campo.
