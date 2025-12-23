# Fuentes ETL — Datos Legacy

Este directorio contiene las **fuentes de datos legacy** que alimentarán el modelo GORE_OS. Cada subdirectorio representa una fuente con su propia estructura y calidad de datos.

---

## Inventario de Fuentes

| Fuente             | Registros | Hojas/Archivos | Estado QA | Entidad Destino                               |
| ------------------ | --------- | -------------- | --------- | --------------------------------------------- |
| **convenios**      | ~200      | 3 CSV          | ⚠️ Media   | `ENT-EJE-CONVENIO`                            |
| **fril**           | ~400      | 6 CSV          | ✅ Alta    | `ENT-FIN-IPR` (FRIL)                          |
| **idis**           | ~500      | 7 CSV          | ❌ Baja    | `ENT-FIN-IPR` (IDI_SNI)                       |
| **modificaciones** | ~50       | 9 CSV          | ❌ Baja    | `ENT-FIN-MODIFICACION_PRESUPUESTARIA`         |
| **partes**         | ~12,000   | 10 CSV         | ⚠️ Media   | `ENT-SYS-DOCUMENTO`                           |
| **progs**          | ~1,700    | 19 CSV         | ⚠️ Media   | `ENT-FIN-IPR` (SUBVENCION_8, etc.)            |
| **funcionarios**   | ~111      | 1 CSV          | ✅ Alta    | `ENT-ORG-FUNCIONARIO`, `ENT-ORG-REMUNERACION` |

---

## Estructura por Fuente

### 1. `convenios/` — Convenios de Transferencia

**Hojas:**

- `CONVENIOS 2023 y 2024.csv`
- `CONVENIOS 2025.csv`
- `MODIFICACIONES.csv`

**Campos clave:**

- `CODIGO` (duplicados detectados)
- `NOMBRE DE LA INICIATIVA`
- `MONTO FNDR M$`
- `ESTADO DE CONVENIO`
- `Nº RES APRUEBA` → `metadata_legal`

**Problemas:**

- Códigos duplicados (~10 casos)
- Fechas en formatos mixtos
- Campo `Nº RES` a veces vacío

**Mapeo:** Ver `../model/docs/mapping_etl_goreos.md`

---

### 2. `fril/` — Fondo Regional de Iniciativa Local

**Hojas:**

- Organización: "Fuente x Etapa" (`31` vs `Fril`, `Avan. y Adj.`, `Lic. y Con.`, etc.)

**Campos clave:**

- `Código` (IDI)
- `Estado Iniciativa`, `Sub-Estado`
- `Saldo 2026` → `ENT-FIN-SERIE_FINANCIERA`

**Calidad:** ✅ **Buena**

- Completitud alta
- Dominios categóricos consistentes
- Debilidad: filas de totales incrustadas

---

### 3. `idis/` — Iniciativas de Inversión (SNI)

**Hojas:**

- `ANALISIS.csv` (más confiable)
- `MAESTRA DIPIR.csv` (datos financieros)
- `CONSOLIDADO.csv`, `MASTER.csv` (problemáticas)

**Campos clave:**

- `CODIGO BIP`
- `SUBT`, `ITEM`, `ASIG` (estructura presupuestaria)
- `GASTO VIGENTE`, `EJEC. 2021`, ... → Series Financieras

**Problemas:** ❌ **Calidad baja**

- Claves duplicadas
- Placeholders (`#REF!`, `-`, `0`)
- Columnas "corridas" (desalineación)
- Formatos heterogéneos

---

### 4. `modificaciones/` — Modificaciones Presupuestarias

**Hojas:** 9 CSV (una por modificación + consolidado)

**Campos clave:**

- `SUBT`, `ITEM`, `ASIG`, `DENOMINACIONES`
- `MODIFICACIÓN M$` (signos inconsistentes)

**Problemas:** ❌ **Calidad baja**

- Signo de modificación (Aumento/Disminución) inconsistente
- Errores `#REF!` masivos
- Falta ID global de modificación
- Bloques INGRESOS/GASTOS mezclados

---

### 5. `partes/` — Gestión Documental

**Hojas:** 10 tipos de documento

**Entidad central:** Documento (folio, fecha, remitente, materia)

**Campos clave:**

- `FOLIO` / `N° DCTO`
- `LINK AL DOCUMENTO` → `url_repositorio`
- `DERIVADO A`, `VIA RECEPCIÓN` → `metadata_legacy`

**Problemas:** ⚠️ **Calidad media**

- Sin FK entre hojas (RECIBIDOS ← OFICIOS/MEMOS)
- Fechas erróneas (2044, 2054)
- IDs numéricos (pierden ceros a la izquierda)

---

### 6. `progs/` — Programas y 8% FNDR

**Hojas:** 19 (módulos F.*, habilitadas, eliminadas, rendiciones, etc.)

**Campos clave:**

- `CÓDIGO` (tipo `2401SC0126`)
- `FONDO` (Deporte, Cultura, Seguridad, etc.)
- `MONTO TRANSFERIDO`, `RENDIDO`, `SALDO`

**Problemas:** ⚠️ **Calidad media**

- Códigos mal formados (`245`, `_<`)
- Formatos mixtos de monto
- PII (datos personales de representantes)

---

### 7. `funcionarios/` — Personal del GORE

**Archivo:** `listado_funcionarios_integrado_remediado.csv`

**Registros:** 111 funcionarios

**Campos clave:**

- Nombre completo, Cargo, Estamento
- Remuneración bruta/líquida
- Horas extras (diurnas/nocturnas/festivas)
- Asignaciones especiales

**Calidad:** ✅ **Alta**

- Completitud excelente
- Parsing requerido: nombre → apellidos

---

## Problemas Transversales

### 1. Tipos de Datos

- Montos como texto (`$ 1.000.000`)
- Fechas en formatos mixtos (`DD-MM-YYYY`, `DD/MM/YY`)
- IDs numéricos con pérdida de ceros

### 2. Valores Faltantes

- Placeholders: `$ -`, `#REF!`, `0`, `s/n`, `sin datos`
- Semántica ambigua (¿cero real o dato faltante?)

### 3. Normalización

- Espacios externos masivos
- Variantes ortográficas (`EMAIL`/`E-MAIL`)
- Acentos inconsistentes (`DIGUILLÍN`/`DIGUILLIN`)

---

## Pipeline ETL Propuesto

```
fuente.csv
    ↓
[1. Validación]
    ↓
[2. Limpieza]
    ↓
[3. Transformación]
    ↓
[4. Carga a GORE_OS]
```

### Fase 1: Validación

- Verificar tipos esperados
- Detectar valores faltantes
- Identificar duplicados

### Fase 2: Limpieza

- Normalizar espacios/acentos
- Parsear montos y fechas
- Resolver placeholders

### Fase 3: Transformación

- Mapear a entidades GORE_OS
- Generar JSON polimórfico (`metadata_*`)
- Crear registros de Series Financieras

### Fase 4: Carga

- Insertar a base de datos
- Validar integridad referencial
- Generar reporte de calidad

---

## Documentación por Fuente

Cada directorio contiene:

- `estructura.md`: Análisis detallado de la estructura
- `diccionario.md`: Diccionario de datos (si existe)
- `originales/`: Archivos CSV originales

---

## Próximos Pasos

1. Implementar scripts de limpieza en Python
2. Crear pipeline ETL automatizado (Airflow/Prefect)
3. Dashboard de calidad de datos
4. Validación post-carga

---

*Documento actualizado: 2025-12-22 | Arquitecto-GORE v0.1.0*
