# Framework CRV de Ingeniería de Requisitos

**v1.0** | GORE_OS | Uso interno

---

## 1. Principio Fundacional

> **El software es una cadena de compromisos verificables.**

Todo sistema existe para cumplir compromisos. Sin compromiso explícito, no hay incumplimiento posible. Sin verificación, no hay entrega válida.

```
ORIGEN  ────►  COMPROMISO  ────►  VERIFICACIÓN  ────►  ENTREGA
(¿por qué?)    (¿qué prometo?)    (¿cómo sé que cumplí?)
```

---

## 2. Las 3 Capas

### 2.1 ORIGEN — ¿Por qué?

Define el problema y la dirección. **No entra al backlog.**

| Concepto      | Definición                                 | Regla Principal                              |
| ------------- | ------------------------------------------ | -------------------------------------------- |
| **Necesidad** | Problema u oportunidad del negocio         | No es verificable, no se implementa          |
| **Objetivo**  | Resultado deseado que traduce la necesidad | Orientado a resultado, justifica compromisos |

```yaml
# Ejemplo ORIGEN
necesidad:
  id: NEC-001
  descripcion: "Los tiempos de atención en urgencia son excesivos"
  stakeholder: "División de Salud"

objetivo:
  id: OBJ-001
  necesidad_ref: NEC-001
  resultado: "Reducir en 30% el tiempo de admisión"
  indicador: "Tiempo promedio desde ingreso hasta atención"
```

---

### 2.2 COMPROMISO — ¿Qué prometo?

Define lo que el sistema debe cumplir. **Unidad fundamental del dominio.**

| Concepto        | Definición                                 | Regla Principal                                              |
| --------------- | ------------------------------------------ | ------------------------------------------------------------ |
| **Requisito**   | Declaración verificable de comportamiento  | Formato: *"Como [ACTOR], quiero [ACCIÓN], para [BENEFICIO]"* |
| **Cualidad**    | Propiedad que condiciona cómo se cumple    | Siempre medible (disponibilidad, rendimiento, etc.)          |
| **Restricción** | Límite impuesto al diseño o implementación | Reduce soluciones posibles (normativa, técnica, decisión)    |

```yaml
# Ejemplo COMPROMISO
requisito:
  id: REQ-001
  objetivo_ref: OBJ-001
  actor: "Admisionista"
  accion: "registrar paciente con datos mínimos"
  beneficio: "iniciar atención en menos de 2 minutos"
  criterios:
    - "Formulario con máximo 5 campos obligatorios"
    - "Validación en tiempo real sin recargar página"

cualidad:
  id: CUA-001
  requisito_ref: REQ-001
  tipo: "rendimiento"
  metrica: "Tiempo de respuesta < 500ms"

restriccion:
  id: RES-001
  requisito_ref: REQ-001
  tipo: "normativa"
  descripcion: "Debe cumplir Ley 21.180 (Transformación Digital)"
```

---

### 2.3 VERIFICACIÓN — ¿Cómo sé que cumplí?

Define cómo se comprueba el cumplimiento. **Cierra el ciclo.**

| Concepto       | Definición                                         | Regla Principal                              |
| -------------- | -------------------------------------------------- | -------------------------------------------- |
| **Criterio**   | Condición observable que determina cumplimiento    | Binario: cumple / no cumple                  |
| **Test**       | Procedimiento que verifica el criterio             | Automatizable cuando sea posible             |
| **Desviación** | Diferencia comprobable entre prometido y observado | Requiere requisito incumplido (no es mejora) |

```yaml
# Ejemplo VERIFICACIÓN
criterio:
  id: CRI-001
  requisito_ref: REQ-001
  condicion: "Dado un paciente nuevo, cuando se completa el formulario, entonces el registro se crea en < 2 min"
  tipo: "aceptacion"

test:
  id: TST-001
  criterio_ref: CRI-001
  tipo: "e2e"
  automatizado: true
  script: "tests/admission/test_registro_paciente.spec.ts"

desviacion:
  id: DEV-001
  requisito_ref: REQ-001
  observado: "Registro toma 4 minutos promedio"
  esperado: "< 2 minutos"
  severidad: "alta"
```

---

## 3. Trazabilidad

Toda pieza de trabajo debe poder rastrearse hacia arriba hasta un origen claro.

```
NECESIDAD
    └── OBJETIVO
            └── REQUISITO ←── CUALIDAD
                    │     ←── RESTRICCIÓN
                    │
                    └── CRITERIO
                            └── TEST
                                    └── DESVIACIÓN (si falla)
```

**Regla de oro:**
- Sin objetivo → No hay requisito válido
- Sin criterio → No hay verificación posible
- Sin requisito incumplido → No hay desviación (bug)

---

## 4. Backlog y Flujo de Trabajo

El **Backlog** es el repositorio priorizado de trabajo pendiente.

### Contiene:
- ✅ Requisitos (trabajo nuevo)
- ✅ Desviaciones (correcciones)
- ✅ Deuda técnica (mejoras estructurales)

### NO contiene:
- ❌ Necesidades (son contexto, no trabajo)
- ❌ Objetivos (son dirección, no tareas)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   ORIGEN    │────►│ COMPROMISO  │────►│VERIFICACIÓN │
│             │     │             │     │             │
│ • Necesidad │     │ • Requisito │     │ • Criterio  │
│ • Objetivo  │     │ • Cualidad  │     │ • Test      │
│             │     │ • Restricc. │     │ • Desviación│
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   │
                    ┌─────────────┐            │
                    │  BACKLOG    │◄───────────┘
                    │  (trabajo)  │
                    └─────────────┘
```

---

## 5. Antipatrones

| Antipatrón                 | Por qué es inválido                  |
| -------------------------- | ------------------------------------ |
| "Bug sin requisito"        | Sin compromiso no hay incumplimiento |
| "Requisito sin objetivo"   | No hay justificación de valor        |
| "Criterio no binario"      | No se puede verificar                |
| "Restricción inventada"    | Reduce opciones sin justificación    |
| "Deuda escondida como bug" | Confunde corrección con mejora       |

---

## 6. Plantilla YAML Completa

```yaml
# goreos_requisito.yml
_manifest:
  schema: "goreos:requirement:1.0"
  
origen:
  necesidad:
    id: "NEC-XXX"
    descripcion: ""
    stakeholder: ""
  objetivo:
    id: "OBJ-XXX"
    necesidad_ref: "NEC-XXX"
    resultado: ""
    indicador: ""

compromiso:
  requisito:
    id: "REQ-XXX"
    objetivo_ref: "OBJ-XXX"
    actor: ""
    accion: ""
    beneficio: ""
    criterios: []
  cualidades: []
  restricciones: []

verificacion:
  criterios: []
  tests: []
  desviaciones: []
```

---

## 7. Resumen Ejecutivo

| Capa             | Pregunta             | Conceptos                        | Entra al Backlog    |
| ---------------- | -------------------- | -------------------------------- | ------------------- |
| **ORIGEN**       | ¿Por qué?            | Necesidad, Objetivo              | ❌ No                |
| **COMPROMISO**   | ¿Qué prometo?        | Requisito, Cualidad, Restricción | ✅ Sí                |
| **VERIFICACIÓN** | ¿Cómo sé que cumplí? | Criterio, Test, Desviación       | ✅ Sí (desviaciones) |

**Total: 8 conceptos**, organizados en 3 capas con flujo unidireccional.

---

*Framework CRV — Compromiso, Requisito, Verificación*
