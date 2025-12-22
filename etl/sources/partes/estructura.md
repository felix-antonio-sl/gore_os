# Estructura legacy
---

## 1) Estructura global de la planilla (hojas, dominios y jerarquías)

### 1.1 Hojas (visión rápida)

| Hoja (CSV)                  | Filas |         Columnas | Rol principal                                      | Identificador más plausible                |
| --------------------------- | ----: | ---------------: | -------------------------------------------------- | ------------------------------------------ |
| **RECIBIDOS**               | 5.858 |               23 | Registro maestro de ingreso/recepción y derivación | `C` (correlativo interno)                  |
| **OFICIOS**                 | 1.898 | 14 (+2 espurias) | Registro de oficios (con link)                     | `N° DCTO` (pero importado como número)     |
| **MEMOS**                   | 1.236 |               14 | Registro de memos (con link)                       | `FOLIO`                                    |
| **RESOLUCIONES EXENTAS**    | 1.258 |                9 | Registro de resoluciones exentas                   | `FOLIO`                                    |
| **RESOLUCIONES AFECTAS**    |   163 |                8 | Registro de resoluciones afectas (con estado)      | `FOLIO`                                    |
| **RENDICIONES 2024**        | 2.334 |               11 | Rendiciones/subvenciones (montos y fechas)         | `CORRELATIVO` (casi único; “s/n” repetido) |
| **RENDICIONES FNDR Y ADNC** |    31 |               10 | Rendiciones, pero con dos listados “en paralelo”   | `CÓDIGO` (por cada bloque)                 |
| **MEMOS INTERNOS**          |     9 |                9 | Sub-registro de memos internos                     | `FOLIO` (no necesariamente único global)   |
| **CARTAS**                  |     5 |               11 | Registro de cartas (con link)                      | `NUMERO DOCUMENTO`                         |
| **OFICIOS INTERNOS**        |     2 |               10 | Sub-registro de oficios internos                   | `NÚMERO DOCUMENTO`                         |

> Nota estructural importante: varios CSV vienen de hojas con **celdas combinadas/filas-título**; por eso aparecen filas “vacías” al inicio o encabezados dobles. En particular, **RENDICIONES FNDR Y ADNC** es una tabla “doble” (dos listados lado a lado), lo que afecta la interpretación fila-a-fila.

### 1.2 Jerarquía / modelo conceptual (cómo “calza” todo)

**Nivel 1 (macro-registro de entrada):**

* **RECIBIDOS** parece ser el **registro maestro** de documentos entrantes: canal de recepción, datos del documento, remitente/destinatario, materia y derivación.

**Nivel 2 (registros especializados por tipo):**

* **OFICIOS**, **CARTAS**, **RESOLUCIONES (exentas/afectas)**, **MEMOS** son registros por tipo de documento, con metadatos similares y casi siempre **link a Drive**.
* **RESOLUCIONES AFECTAS** añade un componente de **workflow** (`ESTADO`).

**Nivel 3 (dominio financiero rendiciones):**

* **RENDICIONES 2024** y **RENDICIONES FNDR Y ADNC** registran rendiciones asociadas a instituciones/iniciativas, montos y fechas.
* Conceptualmente podrían relacionarse con entradas tipo “RENDICION” en **RECIBIDOS**, pero **no hay un ID compartido directo**.

---

## 2) Campos comunes y “relaciones” (más conceptuales que relacionales)

### 2.1 Campos recurrentes (patrón de metadatos)

Aparecen repetidamente:

* **Identificador**: `FOLIO`, `N° DCTO`, `NUMERO DOCUMENTO`, `C` (correlativo), `CÓDIGO` (en rendiciones).
* **Fechas**: `FECHA DCTO/DOCTO`, `FECHA RECEPCIÓN`, `FECHA ENTREGA`, `FECHA INGRESO`.
* **Actores**: `SOLICITA`, `RESPONSABLE`, `DE` (unidad/división origen), `REMITENTE`, `DESTINATARIO`, `FIRMA`, `RECEPCIONADO POR`.
* **Contenido**: `MATERIA`, `OBSERVACIONES`.
* **Trazabilidad**: `DERIVADO A: (DIVISIÓN)`, `VIA RECEPCIÓN / VÍA DESPACHO / VIA DISTRIBUCIÓN`, `ADJUNTO`, (y en RECIBIDOS) `Respuesta si/no`, `Instrucción`, `Plazo`, etc.
* **Repositorio**: `LINK AL DOCUMENTO` (Drive).

### 2.2 Relación sugerida (ideal) vs realidad actual

**Ideal (relacional):**

* `RECIBIDOS.C` debería ser **PK** y el resto de hojas tener una columna `C_RECIBIDOS` como **FK**.

**Realidad (en estos CSV):**

* Los identificadores (`FOLIO`, `N° DCTO`, etc.) son **series independientes** por hoja/tipo.
* El “número de documento” no es confiable como llave cruzada (p. ej., el mismo “610” aparece en oficios y recibidos, pero corresponde a documentos distintos).
* Por lo tanto, las “relaciones” hoy son principalmente por **tipo y proceso**, no por integridad referencial.

---

## 3) Calidad y coherencia por hoja (detallado)

### A) RECIBIDOS (5.858 × 23)

**Naturaleza:** bitácora de ingreso/recepción con derivación interna y un bloque final de seguimiento (respuesta/instrucción/plazo).

**Campos (resumen):**

* `C` (correlativo interno), `VIA RECEPCIÓN`, `NÚMERO DOCUMENTO`, `TIPO DE DOCUMENTO`
* `FECHA DOCUMENTO`, `FECHA RECEPCIÓN`, `FECHA DE ENTREGA`
* `REMITENTE`, `DESTINATARIO`, `MATERIA`
* `VIA DISTRIBUCIÓN`, `ADJUNTO`, `DERIVADO A: (DIVISIÓN)`, `RECEPCIONADO POR`
* Bloque de seguimiento: `FECHA`, `FIRMA`, `Responsable`, `Medio derivación`, `FECHA.1`, `Respuesta si/no`, `Instrucción`, `Plazo`, `Observación`

**Completitud y calidad:**

* **Muy alta** en metadatos base: `C`, tipo, fechas principales, remitente/destinatario/materia (faltantes ~0–0,2%).
* `DERIVADO A: (DIVISIÓN)` también **alto** (faltantes ~2,7%).
* **Muy baja** en seguimiento: `Responsable`, `Medio derivación`, `Respuesta si/no`, `Instrucción`, `Plazo`, `Observación` están ~**99% vacíos** (aparentan ser campos “para usar cuando aplica”, pero hoy casi no se usan).
* `VIA RECEPCIÓN` tiene **faltantes relevantes (~35,5%)** y variantes de escritura (p. ej. `DOCDIGITAL`, `DOC DIGITAL`, cambios de mayúsculas).

**Coherencia de valores (catálogos):**

* `TIPO DE DOCUMENTO` está bien poblado pero con variaciones (acentos/espacios): OFICIO, ORDINARIO, CARTA, RENDICION, INVITACION/INVITACIÓN, etc.
* `VIA RECEPCIÓN` y `VIA DISTRIBUCIÓN` muestran **variantes** (EMAIL/E-MAIL; DOC DIGITAL/DOCDIGITAL), lo que reduce consistencia para análisis.

**Anomalías detectadas (fechas):**

* Hay un puñado de **años improbables** por error de digitación (p. ej. 2044/2054) y un caso tipo `03-09-02` que cae en 2002 (muy probablemente debía ser 2024). Esto afecta reglas como “recepción ≥ documento” o “entrega ≥ recepción”.
* Se detectan algunos casos donde `FECHA DE ENTREGA < FECHA RECEPCIÓN` (pocos, pero existen), lo que sugiere errores puntuales.

**Observación técnica de exportación:**

* Varios campos (`REMITENTE`, `DESTINATARIO`, `MATERIA`) contienen **saltos de línea** dentro de las celdas, lo que es normal en Sheets pero puede complicar exportaciones/ETL si no se sanitiza.

---

### B) OFICIOS (1.898 × 14, con 2 columnas espurias casi vacías)

**Naturaleza:** registro de oficios con metadatos, canal de distribución y link a Drive.

**Campos:**

* `SOLICITA`, `N° DCTO`, `TIPO DE DCTO`
* `FECHA DCTO`, `FECHA RECEPCIÓN`, `FECHA ENTREGA`
* `REMITENTE`, `DESTINATARIO`, `MATERIA`
* `DISTRIBUCIÓN`, `DERIVADO A: (DIVISIÓN)`
* `LINK AL DOCUMENTO`
* `COL_13`, `COL_14` (prácticamente vacías; aparecen con `|` en un caso → artefacto)

**Completitud:**

* Excelente en casi todo; **link ~98,6%** presente.
* `DERIVADO A: (DIVISIÓN)` está **~89% vacío** y, cuando se llena, muchas veces no es “una división”, sino instrucciones (“se envía por correos…”, “pendiente…”). Es decir: **campo sobrecargado**.

**Coherencia/catálogos:**

* `DISTRIBUCIÓN` usa principalmente email/docdigital, pero hay **variantes** (`E-MAIL` vs `EMAIL`).
* `TIPO DE DCTO` aparece con **espacios finales** (`"OFICIO "`), lo que genera categorías duplicadas si se agrupa.

**Riesgo de calidad clave (ID numérico):**

* `N° DCTO` está importado como **float** (ej. 1898.0). Si en el Sheet original había “01898”, se pierden ceros a la izquierda. Para trazabilidad administrativa esto suele ser crítico ⇒ **debe ser texto**.

**Fechas:**

* Rango consistente en 2024, pero hay casos puntuales donde `FECHA ENTREGA < FECHA RECEPCIÓN` y también varios donde `FECHA RECEPCIÓN < FECHA DCTO` (posible definición distinta del campo o error de carga).

---

### C) MEMOS (1.236 × 14)

**Naturaleza:** registro de memorándums (o comunicaciones internas) con folio, unidad origen, destinatario, canal de despacho y link.

**Campos:**

* `FOLIO` (único), `RESPONSABLE`, `DE` (unidad/división), `PARA:`
* `FECHA DOCTO`, `FECHA ENTREGA`
* `MATERIA`, `FIRMA`
* `VÍA DESPACHO`, `OBSERVACIONES`, `FIRMA RECEPCIÓN`, `LINK AL DOCUMENTO`
* `COL_1` y `COL_14` (residuales)

  * `COL_1` aparece ocasionalmente con marcas como “MEL” o “RESERVADO” (muy poco poblado).
  * `COL_14` tiene un único valor que parece fecha adicional → probable desalineación / columna huérfana.

**Completitud:**

* `FOLIO` completo y único.
* `FECHA ENTREGA` está **~70% lleno** (cuando está lleno, el formato es consistente).
* `DE` presenta **~25% faltante** (impacta trazabilidad por unidad).
* `OBSERVACIONES` ~99% vacío y `FIRMA RECEPCIÓN` ~99,9% vacío (campos subutilizados).
* `LINK AL DOCUMENTO` ~93,5% (bueno, pero no total).

**Catálogos (VÍA DESPACHO):**

* Campo con valores heterogéneos: mezcla canales (“DOCDIGITAL”, “PAPEL”, “POR MANO”) con textos libres y hasta casos aislados muy largos (lo que sugiere **uso como comentario** además de “canal”).

**Fechas anómalas:**

* Hay **4 registros** con `FECHA DOCTO` en 2026/2027 (posibles errores de digitación de año).

---

### D) RESOLUCIONES EXENTAS (1.258 × 9)

**Naturaleza:** registro de resoluciones exentas, con solicitante, folio, fecha, materia, firma, observaciones y link.

**Campos:**

* `SOLICITA`, `FOLIO`, `FECHA DOCTO`, `MATERIA`, `FIRMA`, `OBSERVACIONES`, `LINK AL DOCUMENTO`
* `I` y `COL_9` son columnas residuales:

  * `I` contiene solo 2 notas puntuales (ej. “repetida…”) y está ~99,8% vacío.
  * `COL_9` contiene 1 link “corrida de columna” (link quedó ahí y `LINK AL DOCUMENTO` fue usado como comentario de envío).

**Completitud y coherencia:**

* Muy buena en núcleo (`FOLIO`, fecha, firma, materia).
* `OBSERVACIONES` tiene ~13% nulos y además funciona como “canal/estado de envío” con variaciones (`DOC DIGITAL`/`DOCDIGITAL`, `EMAIL`/`E-MAIL`, etc.).

---

### E) RESOLUCIONES AFECTAS (163 × 8)

**Naturaleza:** similar a exentas, pero con `ESTADO` (workflow).

**Campos:**

* `SOLICITA`, `FOLIO`, `FECHA DOCTO`, `MATERIA`, `FIRMA`, `OBSERVACIONES`, `LINK AL DOCUMENTO`, `ESTADO`

**Calidad:**

* Muy alta: casi todo completo; `ESTADO` está casi completo.
* `ESTADO` está bastante normalizado (ej. “EN TRAMITE”, “TOMADA DE RAZON”, “CON ALCANCE”, “REPRESENTADA”).
* `OBSERVACIONES` nuevamente mezcla canal/nota (faltantes ~14%).

---

### F) RENDICIONES 2024 (2.334 × 11)

**Naturaleza:** registro de rendiciones vinculadas a instituciones e iniciativas; incluye monto y fechas.

**Campos:**

* `CORRELATIVO` (mayoritariamente único, pero “s/n” se repite)
* `TIPO DOCUMENTO`, `CÓDIGO`
* `FECHA DCTO`, `FECHA INGRESO`, `FECHA ENTREGA`
* `NOMBRE INSTITUCIÓN`, `NOMBRE DE LA INICIATIVA`
* `MONTO DE LA RENDICIÓN`
* `RECEPCIONADO POR`, `FIRMA` (casi siempre vacíos)

**Calidad de datos:**

* Metadatos base muy completos (nulos bajos).
* `MONTO DE LA RENDICIÓN` tiene ~8,9% nulos y además **formatos mixtos**:

  * Estilo con separador de miles “,” y decimales “.” (p.ej. `$2,350,180.00`)
  * Estilo con separador de miles “.” (p.ej. `$1.800.000`)
  * Algunos placeholders (pocos) como “SIN MONTO” o `$ -`
* Fechas: mayoritariamente 2024, pero hay entradas en 2023/2025 y **1 caso** en 2026; además hay 1 registro 2021 (posible arrastre histórico o error). Esto sugiere que la hoja “2024” **no está estrictamente acotada** al año.

**Campos subutilizados:**

* `RECEPCIONADO POR` ~92,8% vacío y `FIRMA` ~99,9% vacío → probablemente no se usa el cierre formal en esta bitácora.

---

### G) RENDICIONES FNDR Y ADNC (31 × 10)

**Naturaleza:** dos listados distintos dentro de la misma hoja, **en paralelo**:

* Bloque “FNDR” (izquierda) con: `CÓDIGO`, fechas, institución.
* Bloque “ADNC/ADCD” (derecha) con otro set equivalente (`CÓDIGO.1`, etc.).

**Calidad estructural:**

* El bloque FNDR está **100% lleno** (31/31).
* El bloque derecho está **~19,4% lleno** (6/31). Esto confirma que **no es una tabla relacional fila-a-fila**, sino dos tablas colocadas una al lado de la otra.
  ➡️ Recomendación estructural fuerte: separar en dos hojas o normalizar a formato “largo” con columna `PROGRAMA` (FNDR/ADNC/ADCD) + columnas estándar.

---

### H) MEMOS INTERNOS (9 × 9)

**Naturaleza:** registro pequeño, muy limpio, de memos internos.

**Calidad:**

* 0% nulos (en esta muestra).
* Link 100% Drive.
* Útil como “subregistro” o muestra, pero su estructura se solapa con MEMOS; puede generar redundancia si ambos conviven sin llave.

---

### I) CARTAS (5 × 11)

**Naturaleza:** registro de cartas con metadatos y link.

**Calidad:**

* Muy completo (casi todo lleno).
* `DERIVADO A: (DIVISIÓN)` está **80% vacío** (probablemente no se usa).
* Hay **espacios finales** frecuentes en campos de texto (derivado/distribución), lo que afecta agrupaciones.

---

### J) OFICIOS INTERNOS (2 × 10)

**Naturaleza:** mini registro de oficios internos con trazabilidad completa (fechas, remitente, destinatario, materia, distribución y derivación).

**Calidad:**

* Todo completo, pero tamaño mínimo (2 filas); sirve más como plantilla/ejemplo que como dataset para análisis.

---

## 4) Diagnóstico global de coherencia y calidad (conjunto completo)

### Fortalezas

* **Cobertura alta** de metadatos esenciales en hojas grandes (especialmente RECIBIDOS y OFICIOS).
* Uso extensivo de **links a Google Drive** en varios registros (alta trazabilidad documental).
* Estructuras por tipo de documento bastante consistentes (mismos conceptos repetidos).

### Debilidades principales (impactan análisis y control)

1. **Sin integridad referencial entre hojas**
   No hay un ID común (FK) que conecte RECIBIDOS con OFICIOS/CARTAS/RESOLUCIONES/MEMOS. Las relaciones quedan “a ojo”.

2. **Campos sobrecargados y catálogos no normalizados**

   * `DERIVADO A: (DIVISIÓN)` en OFICIOS se usa muchas veces como “instrucción”.
   * `OBSERVACIONES` y `VÍA DESPACHO` mezclan canal + notas libres.
   * Variantes ortográficas (`EMAIL/E-MAIL`, `DOC DIGITAL/DOCDIGITAL`, mayúsculas, acentos) generan categorías duplicadas.

3. **Tipos incorrectos por inferencia (IDs numéricos)**

   * `C` en RECIBIDOS y `N° DCTO` en OFICIOS quedan como **float**, perdiendo potencialmente ceros a la izquierda y agregando “.0”.
   * Para gestión documental, estos campos deberían ser **texto**.

4. **Anomalías puntuales de fechas (año mal digitado)**

   * En RECIBIDOS aparecen años 2044/2054 y un caso 2002 (muy probable error).
   * En MEMOS hay 4 registros en 2026/2027.
   * Esto rompe reglas básicas de consistencia (entrega vs recepción, etc.).

5. **Estructuras “no tabulares” dentro de una hoja**

   * RENDICIONES FNDR Y ADNC contiene **dos tablas en una**, lo que es frágil para análisis automatizado.
