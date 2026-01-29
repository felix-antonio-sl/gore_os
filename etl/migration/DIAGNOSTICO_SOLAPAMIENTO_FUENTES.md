# Diagnóstico de Solapamiento: FRIL, IDIS, 250

**Fecha**: 2026-01-29
**Objetivo**: Analizar duplicación entre fuentes antes de migrar a core.ipr
**Autor**: Claude Code (Opus 4.5)

---

## 1. RESUMEN EJECUTIVO

| Métrica | Valor |
|---------|-------|
| **BIPs totales únicos** | 2,007 |
| **Registros en dim_iniciativa_unificada** | 2,010 |
| **BIPs exclusivos de cartera 250** | 73 |
| **Solapamiento IDIS ↔ 250** | 437 BIPs (85.7% de 250) |
| **Inconsistencias de nombres** | ~60% en comunes |

### Conclusión Principal

**dim_iniciativa_unificada.csv está INCOMPLETA**: Faltan 73 registros de la cartera 250 que no fueron integrados.

---

## 2. ANÁLISIS DETALLADO

### 2.1 Conteo de Registros por Fuente

| Archivo | Registros | BIPs Únicos | Observaciones |
|---------|-----------|-------------|---------------|
| dim_iniciativa_unificada.csv | 2,010 | 1,934 | Fuente actual para IPRLoader |
| dim_iniciativa_idis.csv | 2,861 | 1,934 | Múltiples años por BIP |
| dim_iniciativa.csv (250) | 510 | 510 | Cartera de 250 proyectos |

### 2.2 Solapamientos Identificados

```
            dim_iniciativa_unificada
                   (1,934 BIPs)
                        ↕
              100% equivalente a
                        ↕
              dim_iniciativa_idis
                   (1,934 BIPs)

                    437 BIPs
                   ┌───┴───┐
                   │       │
                   ↓       ↓
            dim_iniciativa (250)
                 (510 BIPs)
                     │
                     ↓
              73 BIPs EXCLUSIVOS
              (NO en IDIS/Unificada)
```

### 2.3 Los 73 BIPs Exclusivos de Cartera 250

| Tipo | Cantidad | Patrón | Descripción |
|------|----------|--------|-------------|
| **BIPs nuevos 2020+** | 39 | 400XXXXX | Proyectos no sincronizados con IDIS |
| **Convenios Ad-hoc** | 34 | CVC-AD-XX | Convenios de asignación directa (no son IPRs) |

#### 39 BIPs Nuevos (400XXXXX) - DEBEN AGREGARSE A UNIFICADA:

```
40051768  CONSTRUCCION PARQUE LA RUFINA, COMUNA DE CHILLAN
40052561  CONSERVACION ESCUELA VILLA JESUS DE COELEMU
40052689  CONSERVACION SALA CUNA Y JARDIN INFANTIL LOS ENANITOS
40055244  AMPLIACION SANEAMIENTO SANITARIO MONTERRICO, CHILLAN
40059011  ADQUISICION CAMARINES Y BAÑOS MODULARES PROVINCIA DE PUNILLA
40060133  ADQUISICIÓN FLOTA VEHICULAR, REGIÓN POLICIAL DE ÑUBLE-PDI
40061141  ADQUISICIÓN AERONAVES NO TRIPULADAS RPAS
40063393  Transferencia programa de recuperación asistencia escolar
40063490  Transferencia mejorando la calidad de la educación escolar
40063943  MEJORAMIENTO COMEDOR, COCINA Y DESPENSA ESTABLECIMIENTOS
40064078  Transferencia a programa mejorando calidad de la educación
40064191  Transferencia mejoramiento de calidad de la educación
40064354  TRANSFERENCIA PARA REDUCCION LISTA DE ESPERA QUIRURGICA
40064469  ADQUISICIÓN DE EQUIPOS PARA LA FISCALIZACIÓN DE PESCA ILEGAL
40064476  CONSTRUCCIÓN ALUMBRADO PÚBLICO DIVERSOS SECTORES RURALES
40065054  SANEAMIENTO DERECHOS DE AGUA, REGION DE ÑUBLE
40065096  CONSTRUCCIÓN SEDE SOCIAL EL BOSQUE, SAN CARLOS
40065324  ADQUISICION DE MINICARGADORES PARA LA MENTENCIÓN DE ESPACIOS
40065365  TRANSFERENCIA FOMENTO Y DESARROLLO PRODUCTIVO PESCA ARTESANAL
40065537  CONSTRUCCIÓN GRADERÍAS CANCHAS DE FÚTBOL, COMUNA DE COIHUECO
40066081  MEJORAMIENTO GIMNASIO SAN GREGORIO, COMUNA DE ÑIQUÉN
40066134  AMPLIACIÓN TERCERA COMPAÑÍA DE BOMBEROS CHACAY
40066141  CONSTRUCCIÓN TORRES DE ILUMINACIÓN ESTADIO CHACAY
40066142  MEJORAMIENTO ILUMINACIÓN PÚBLICA EN DISTINTOS SECTORES
40067010  TRANSFERENCIA TELESALUD PARA ÑUBLE
40067286  TRANSFERENCIA TECNOLOGICA DE MONITOREO Y GESTION DE FUGAS
40067303  TRANSFERENCIA FORTALECIMIENTO DE LA COMPETITIVIDAD EN MIPYMES
40067306  TRANSFERENCIA BRANDING Y COMERCIALIZACIÓN DEL VALLE DEL ITATA
40067308  TRANSFERENCIA TRAZABILIDAD Y VALIDACION VINOS DEL VALLE
40067311  TRANSFERENCIA DE REDES PARA CONECTAR: CONECTIVIDAD A INTERNET
40067327  TRANSFERENCIA CLINICA TECNOLOGICA MOVIL, DIGITA ÑUBLE
40067349  TRANSFERENCIA APOYO A LA COMPETITIVIDAD DE EMPRENDIMIENTOS
40067533  ECOOLOGIC FRUIT: INICIATIVA DE TRANSFERENCIA TECNOLOGICA
40067558  TRANSFERENCIA PROMOCION DE EXPORTACIONES MULTISECTORIAL ÑUBLE
40068588  TRANSFERENCIA CONSTRUYENDO PUENTES DE APOYO PARA EL AUTISMO
40071419  MEJORAMIENTO SISTEMA DE AGUA POTABLE, COMUNA DE SAN NICOLAS
40071881  TRANSFERENCIA RENOVACION BUSES, MINIBUSES, TROLEBUSES
40074577  HABILITACION INMUEBLE COMUNITARIOS DE CUIDADOS
40075436  ADQUISICIÓN DE TERRENO EN EL MARCO DEL PEH
```

#### 34 Convenios Ad-hoc (CVC-AD-XX) - NO SON IPRs:

Estos son convenios de asignación directa del 8% FNDR (Glosa 07), no proyectos de inversión:

```
CVC-AD-01  GIRA SINFONICA ÑUBLE-BRASIL 2024
CVC-AD-02  ACERCANDO TU LICEO
CVC-AD-03  JUEGOS NACIONALES DE INVIERNO OLIMPIADAS ESPECIALES
CVC-AD-04  ENCUENTRO INTERNACIONAL DE MUJERES RURALES
CVC-AD-06  ÑUBLE FOMENTA EL DEPORTE
CVC-AD-07  JUNTOS AVANZAMOS EN LA INCLUSION
... (28 más)
```

**Recomendación**: NO migrar como IPRs. Crear tabla separada `core.convenio_asignacion_directa` o marcar con flag `is_ad_hoc`.

---

## 3. INCONSISTENCIAS DE NOMBRES

En los 437 BIPs comunes entre 250 e IDIS, hay diferencias de nomenclatura:

| Tipo de Diferencia | Frecuencia | Ejemplo |
|-------------------|------------|---------|
| Mayúsculas/minúsculas | ~80% | "MINIBUS" vs "MINI BUS" |
| Typos | ~15% | "VIILLA" vs "VILLA" |
| Nombres diferentes | ~5% | "CONSTRUCCION" vs "MEJORAMIENTO" |

### Ejemplos Críticos (similitud <50%):

| BIP | Nombre en 250 | Nombre en IDIS |
|-----|--------------|----------------|
| 40027236 | CONSERVACION VEREDAS VILLA CUARTO CENTENARIO | CONSERVACIÓN VEREDAS POBLACIÓN SIMÓN BOLIVAR Y OTROS |
| 40047896 | CONSTRUCCION CANCHA PASTO SINTETICO | MEJORAMIENTO CANCHA PASTO SINTÉTICO |

**Recomendación**: Usar nombre de IDIS como canónico, guardar nombre de 250 en `metadata.nombre_cartera_250`.

---

## 4. ACCIONES REQUERIDAS PRE-MIGRACIÓN

### 4.1 CRÍTICO - Completar dim_iniciativa_unificada

```python
# Script: etl/scripts/complete_iniciativa_unificada.py
# Agregar 39 BIPs nuevos de cartera 250
```

Campos a mapear desde dim_iniciativa.csv:
- `codigo` → `bip`
- `nombre_raw` → `nombre_iniciativa`
- Inferir `tipologia`, `etapa`, `origen` de patrones de nombre
- `fuente_principal` = '250'

### 4.2 ALTO - Separar Convenios Ad-hoc

Los 34 registros CVC-AD-XX NO deben migrarse a core.ipr:

**Opción A**: Crear tabla `core.convenio_ad_hoc`
**Opción B**: Migrar a `core.agreement` con flag `is_ad_hoc = true`

### 4.3 MEDIO - Normalizar Nombres

Para los 437 comunes:
1. Verificar que el BIP sea el mismo proyecto
2. Usar nombre canónico de IDIS
3. Guardar variantes en metadata

---

## 5. IMPACTO EN IPRLoader

### Antes de remediación:
- Registros a migrar: 2,010
- BIPs únicos: 1,934
- **Registros faltantes: 39** (BIPs nuevos de 250)

### Después de remediación:
- Registros a migrar: 2,049
- BIPs únicos: 1,973
- Registros faltantes: 0

### Convenios Ad-hoc (separados):
- Registros: 34
- Destino: core.agreement o tabla separada

---

## 6. CHECKLIST DE REMEDIACIÓN

- [ ] Ejecutar script para agregar 39 BIPs de 250 a dim_iniciativa_unificada
- [ ] Crear archivo dim_convenio_ad_hoc.csv con los 34 CVC-AD-XX
- [ ] Validar que no hay duplicados por BIP
- [ ] Normalizar nombres (IDIS como canónico)
- [ ] Agregar campo `fuente_250: bool` para tracking
- [ ] Actualizar conteo en CLAUDE.md
- [ ] Documentar decisión sobre convenios ad-hoc

---

## 7. VERIFICACIÓN POST-REMEDIACIÓN

```sql
-- Verificar conteo final de IPRs
SELECT COUNT(*) FROM core.ipr WHERE deleted_at IS NULL;
-- Esperado: ~2,049

-- Verificar no hay duplicados por código BIP
SELECT code, COUNT(*)
FROM core.ipr
WHERE deleted_at IS NULL
GROUP BY code
HAVING COUNT(*) > 1;
-- Esperado: 0 filas (o 3 filas si mantiene los 3 duplicados conocidos)
```

---

*Documento generado: 2026-01-29*
*Basado en análisis de dim_iniciativa*.csv*
