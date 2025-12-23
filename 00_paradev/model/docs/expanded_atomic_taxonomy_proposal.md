# Ontología Estratificada GORE_OS v5.0

## Visión Fundamental

> **La Story es el pilar.** Organiza quiénes generan valor y cómo lo hacen mediante acciones que, en conjunto, determinan la Capacidad Institucional.

> **GORE_OS es el habilitador.** Permite que la acción se ejecute por un agente que ocupa un rol en una etapa o transición determinada.

---

## Arquitectura de Planos

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PLANO DE VALOR                                   │
│                  (Generación y Entrega de Valor)                        │
│                                                                         │
│    ┌─────────┐  assumes   ┌─────────┐  actor_of   ┌─────────────┐       │
│    │  AGENT  │───────────▶│  ROLE   │────────────▶│   STORY     │       │
│    │ (Quién) │            │ (Lugar) │             │   (Qué)     │       │
│    └─────────┘            └─────────┘             └──────┬──────┘       │
│                                                          │↑             │
│                                       ┌──────────────────┘└──────────┐  │
│                                       │ enables              temporal│  │
│                                       ▼                              ▼  │
│                               ┌─────────────┐              ┌─────────┐  │
│                               │ COMPETENCE  │              │ PROCESS │  │
│                               │(Acción)     │              │ (Tiempo)│  │
│                               └──────┬──────┘              └─────────┘  │
│                                      │ contributes_to                   │
│                                      ▼                                  │
│                               ┌─────────────┐                           │
│                               │ CAPABILITY  │                           │
│                               │(Valor Inst.)│                           │
│                               └─────────────┘                           │
└─────────────────────────────────────────────────────────────────────────┘
                                      ↕
                              habilitado por
                                      ↕
┌─────────────────────────────────────────────────────────────────────────┐
│                    PLANO DE IMPLEMENTACIÓN                              │
│              (Estructuración y Habilitación Técnica)                    │
│                                                                         │
│         ┌─────────────┐                    ┌─────────────┐              │
│         │   ENTITY    │                    │   MODULE    │              │
│         │  (Esquema)  │                    │  (Código)   │              │
│         └─────────────┘                    └─────────────┘              │
│                                                                         │
│         Describe la forma         Organiza cómo se habilita             │
│         de los datos              la ejecución de las stories           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Plano de Valor: Los 6 Átomos Generadores

| Átomo          | Pregunta                  | Rol en el Sistema                  |
| -------------- | ------------------------- | ---------------------------------- |
| **Agent**      | ¿Quién puede actuar?      | Sustrato ejecutor (humano/máquina) |
| **Role**       | ¿Qué lugar asume?         | Contexto de acción del agente      |
| **Story**      | ¿Qué necesita el usuario? | **Pilar**: especifica el valor     |
| **Competence** | ¿Qué acción atómica?      | Unidad mínima de ejecución         |
| **Capability** | ¿Qué valor institucional? | Límite de las competencias         |
| **Process**    | ¿Cómo fluye en el tiempo? | Visión ortogonal-temporal de Story |

### La Story como Pilar

```
Story = {
  as_a: Role,           # Quién genera valor
  i_want: Competence,   # Cómo lo genera
  so_that: Capability   # Qué valor aporta
}
```

La historia de usuario es la **base para configurar los requerimientos de GORE_OS**.

---

## Plano de Implementación: Los 2 Meta-Átomos

| Átomo      | Pregunta                          | Nivel             |
| ---------- | --------------------------------- | ----------------- |
| **Entity** | ¿Qué forma tienen los datos?      | Esquema/Ontología |
| **Module** | ¿Cómo se organiza el habilitador? | Código/Sistema    |

### Nota sobre Entity

Entity es un concepto de **segundo orden**: Agent, Role, Story, Competence, Capability y Process son *todos* entidades en el sentido de que tienen un esquema que los define. Entity describe la forma, no el valor.

### Nota sobre Module

Module describe la **organización técnica** de GORE_OS como habilitador. No genera valor directamente, sino que estructura cómo se habilita la ejecución de las historias.

---

## Impacto en la Estructura de Directorios

```
model/atoms/
├── agents/           # Plano de Valor
├── roles/            # Plano de Valor
├── stories/          # Plano de Valor (PILAR)
├── competences/      # Plano de Valor
├── capabilities/     # Plano de Valor (NUEVO)
├── processes/        # Plano de Valor
│
├── entities/         # Plano de Implementación (meta)
└── modules/          # Plano de Implementación (meta)
```

---

## Próximos Pasos Propuestos

1. **Crear directorio `agents/`:** Migrar sustrato explícito desde roles.
2. **Crear directorio `capabilities/`:** Agregar valor institucional como átomo.
3. **Actualizar Ontología:** Reflejar los dos planos en `ontologia_categorica_goreos.md`.
4. **Actualizar MANIFESTO:** Consagrar la Story como pilar.
5. **Refactorizar Diagnóstico:** Validar morfismos inter-plano.

---

## Decisión Pendiente

¿Procedo con la implementación de esta ontología estratificada?
