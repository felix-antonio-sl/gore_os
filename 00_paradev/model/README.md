# Modelo de Datos GORE_OS

**Versión:** 2.1.0  
**Entidades:** 131  
**Última actualización:** 2025-12-22

---

## Estructura del Modelo

El modelo de datos de GORE_OS sigue una **arquitectura categórica** donde cada componente tiene un propósito único y las relaciones son explícitas.

```
model/
├── atoms/              # Átomos categóricos (unidades indivisibles)
│   ├── entities/       # 131 entidades YAML
│   ├── roles/          # ~50 roles institucionales
│   ├── processes/      # ~40 procesos BPMN
│   ├── capabilities/   # ~30 capacidades
│   ├── stories/        # ~100 historias de usuario
│   └── modules/        # ~15 módulos de dominio
│
├── compositions/       # Relaciones complejas (pushouts, pullbacks)
├── profunctors/        # Relaciones avanzadas (bimodules)
├── seeds/              # Datos de configuración/catálogo
└── docs/               # Documentación ontológica
```

---

## Entidades por Dominio

### D-FIN (Finanzas) — 32 entidades

| Entidad                    | Descripción                                    |
| -------------------------- | ---------------------------------------------- |
| `ENT-FIN-IPR`              | Intervención Pública Regional (núcleo)         |
| `ENT-FIN-MECANISMO`        | Mecanismo de financiamiento (FRIL, FRPD, etc.) |
| `ENT-FIN-SERIE_FINANCIERA` | Serie temporal financiera (polimórfica)        |
| `ENT-FIN-LINEA_ARI`        | Línea del Anteproyecto Regional                |
| `ENT-FIN-ASIGNACION`       | Asignación presupuestaria                      |
| ...                        | [Ver todos](atoms/entities)                    |

### D-EJE (Ejecución) — 12 entidades

| Entidad                 | Descripción                 |
| ----------------------- | --------------------------- |
| `ENT-EJE-CONVENIO`      | Convenio de transferencia   |
| `ENT-EJE-BITACORA_OBRA` | Bitácora de inspecciones    |
| `ENT-EJE-EJECUTOR`      | Institución ejecutora       |
| ...                     | [Ver todos](atoms/entities) |

### D-ORG (Organizacional) — 15 entidades

| Entidad                | Descripción                 |
| ---------------------- | --------------------------- |
| `ENT-ORG-FUNCIONARIO`  | Funcionario del GORE        |
| `ENT-ORG-REMUNERACION` | Remuneración mensual        |
| `ENT-ORG-DIVISION`     | División del GORE           |
| ...                    | [Ver todos](atoms/entities) |

[Ver distribución completa por dominio en `docs/scope_v1.md`]

---

## Innovaciones Clave del Modelo

### 1. JSON Polimórfico para Metadatos

Las entidades usan campos JSON validados para capturar variabilidad estructural sin "ensuciar" el esquema:

**Ejemplo: `ENT-FIN-IPR.metadata_mecanismo`**

```yaml
# Validado dinámicamente según ENT-FIN-MECANISMO.schema_metadata
metadata_mecanismo: {
  "categoria_fril": "DESARROLLO_TERRITORIAL",
  "monto_solicitado": 50000000,
  "comuna_beneficiaria": "Chillán"
}
```

### 2. Serie Financiera Polimórfica

`ENT-FIN-SERIE_FINANCIERA` actúa como **funtor temporal** que captura flujos financieros de cualquier objeto:

```yaml
# Ejemplo: EJECUTADO_REAL de una IPR
- objeto_tipo: ENT-FIN-IPR
  objeto_id: <uuid>
  tipo_serie: EJECUTADO_REAL
  periodo: 2024-11
  valor: 12500000
```

### 3. Extensibilidad sin Rigidez

Campos `metadata_*` permiten absorber complejidad legacy sin romper normalización:

- `metadata_mecanismo`: Datos específicos de mecanismo IPR
- `metadata_legal`: Números de resolución, oficios
- `metadata_legacy`: Atributos "flotantes" de fuentes ETL

---

## Cobertura de Fuentes ETL

| Fuente         | Registros | Entidad Destino                       | Cobertura |
| -------------- | --------- | ------------------------------------- | --------- |
| Convenios      | ~200      | `ENT-EJE-CONVENIO`                    | ✅ 100%    |
| FRIL           | ~400      | `ENT-FIN-IPR` (FRIL)                  | ✅ 100%    |
| IDIs           | ~500      | `ENT-FIN-IPR` (IDI_SNI)               | ✅ 100%    |
| Modificaciones | ~50       | `ENT-FIN-MODIFICACION_PRESUPUESTARIA` | ✅ 100%    |
| Partes         | ~12K      | `ENT-SYS-DOCUMENTO`                   | ✅ 100%    |
| Programas      | ~1.7K     | `ENT-FIN-IPR` (SUBVENCION_8)          | ✅ 100%    |
| Funcionarios   | ~111      | `ENT-ORG-FUNCIONARIO`                 | ✅ 100%    |

Ver `etl/README.md` para detalles de mapeo.

---

## Validación y Calidad

### JSON Schemas

Cada entidad tiene un schema JSON que valida:

- Tipos de datos
- Cardinalidad (nullable, arrays)
- Referencias FK
- Constraints de negocio

### Nomenclatura

**Convención:** `ENT-{DOMINIO}-{NOMBRE}`

Ejemplos:

- `ENT-FIN-IPR` ✅
- `ENT-ORG-FUNCIONARIO` ✅
- `Funcionario` ❌ (sin prefijo)

### Categorización DDD

| Categoría       | Descripción                  | Ejemplos                                                       |
| --------------- | ---------------------------- | -------------------------------------------------------------- |
| **Master**      | Entidad maestra del dominio  | `ENT-FIN-IPR`, `ENT-ORG-FUNCIONARIO`                           |
| **Transaction** | Evento o transacción         | `ENT-FIN-MODIFICACION_PRESUPUESTARIA`, `ENT-EJE-BITACORA_OBRA` |
| **Reference**   | Datos de referencia/catálogo | `ENT-LOC-COMUNA`, `ENT-FIN-MECANISMO`                          |
| **Analytical**  | Vista analítica              | `ENT-PLAN-BRECHA_ERD`                                          |

---

## Seeds (Datos de Configuración)

Los seeds proveen datos de catálogo necesarios para el arranque del sistema:

| Archivo               | Descripción                       |
| --------------------- | --------------------------------- |
| `mecanismos-ipr.yml`  | 7 mecanismos IPR con schemas JSON |
| `comunas-nuble.yml`   | 21 comunas de la región           |
| `divisiones-gore.yml` | Organigrama del GORE              |

---

## Próximos Pasos

1. **Generación de DDL**: Script Python para generar SQL desde YAML
2. **Validación automática**: CI/CD con JSON Schema validator
3. **Documentación auto-generada**: Diagramas ERD desde el modelo
4. **API GraphQL**: Exposición del modelo vía API

---

## Cambios Recientes (v2.1.0)

### Entidades Nuevas (8)

- `ENT-EJE-BITACORA_OBRA`
- `ENT-FIN-LINEA_ARI`
- `ENT-PLAN-BRECHA_ERD`
- `ENT-LOC-IPT`
- `ENT-SAL-EQUIPO_INTERVENCION`
- `ENT-GOV-COMITE_COORDINACION`
- `ENT-DIG-SOLICITUD_TRANSPARENCIA`
- `ENT-NORM-AUDIENCIA_LOBBY`

### Extensiones

- `ENT-FIN-IPR`: +2 campos (`rate_historico`, `marco_logico`)
- `ENT-FIN-ERD`: +1 campo (`indicadores`)
- `ENT-FIN-CONVENIO_PROGRAMACION`: +1 campo (`hitos`)
- `ENT-SAL-PLAYBOOK`: +1 campo (`ejecuciones`)
- `ENT-ORG-FUNCIONARIO`: +4 campos (estamento, formación, etc.)
- `ENT-ORG-REMUNERACION`: +6 campos (bruto, horas extras JSON, etc.)

### Depreciaciones

- 55 entidades legacy marcadas como fuera de scope v1 (ver `docs/scope_v1.md`)

---

*Documento actualizado: 2025-12-22 | Arquitecto-GORE v0.1.0*
