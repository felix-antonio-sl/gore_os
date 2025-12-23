# Documentación del Modelo GORE_OS

Este directorio contiene la **documentación ontológica y técnica** del modelo de datos GORE_OS.

---

## Documentos Disponibles

### 📘 [ontologia_categorica_goreos.md](ontologia_categorica_goreos.md)

**La Norma Superior de Construcción**

Versión: 4.1.0 | ~36 KB | Documento fundacional

Define:

- Propósito fundamental de GORE_OS
- La **Story** como átomo generador
- Los 6 tipos de átomos (Entity, Role, Process, Capability, Story, Module)
- Sistema de **Dominios** como contextos semánticos
- Diagramas de arquitectura categórica

> *"Todo nace de una historia. La Story es la semilla del sistema."*

---

### 📊 [scope_v1.md](scope_v1.md)

**Scope de la Versión 1.0**

Define qué está **dentro** y **fuera** del alcance:

| Incluidos (11 dominios)       | Excluidos (3 dominios) |
| ----------------------------- | ---------------------- |
| D-FIN, D-EJE, D-GOV, D-LOC... | D-DEV, D-OPS, D-EVOL   |

Lista las 55 entidades legacy **depreciadas** explícitamente.

---

### 📈 [analisis_categorial_stories.md](analisis_categorial_stories.md)

**Análisis Categórico de Stories**

Métricas de cobertura del modelo por stories:

- Tasa de cobertura Role → Story
- Entidades huérfanas
- Procesos sin story asociada
- Recomendaciones de completitud

---

## Cómo Usar Esta Documentación

1. **Nuevo en GORE_OS?** → Empieza por `ontologia_categorica_goreos.md`
2. **¿Qué está en scope?** → Consulta `scope_v1.md`
3. **¿Hay gaps de cobertura?** → Revisa `analisis_categorial_stories.md`

---

## Relacionado

- 📂 [Modelo de Datos](../README.md)
- 📂 [Entidades](../atoms/entities/)
- 📂 [Seeds](../seeds/)

---

*Actualizado: 2025-12-22*
