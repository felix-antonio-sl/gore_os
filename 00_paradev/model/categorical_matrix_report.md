# GORE_OS Categorical Cross-Reference Matrix

## 📊 Matriz de Adyacencia Categorial

Esta matriz muestra las relaciones existentes entre todos los tipos de átomos.

**Leyenda:**
- ✅ N = Relación activa con N instancias
- ↩️ N = Relación inversa activa
- ⚪ = Profunctor existe pero vacío
- ❌ = No existe profunctor

```
     | ROLE   | STOR  | PROC  | ENTI  | MODU  | CAPA  
------------------------------------------------------
ROLE | ✅ 23   | ✅ 620 | ✅ 63  | ✅ 835 | ❌     | ❌     
STOR | ↩️ 620 | ❌     | ❌     | ❌     | ❌     | ⚪ 1f  
PROC | ✅ 19   | ❌     | ✅ 9   | ✅ 17  | ❌     | ❌     
ENTI | ↩️ 835 | ❌     | ↩️ 17 | ✅ 611 | ❌     | ❌     
MODU | ❌      | ❌     | ❌     | ❌     | ❌     | ↩️ 587
CAPA | ❌      | ⚪     | ❌     | ❌     | ✅ 587 | ❌     
```

---

## 🔗 Relaciones Activas (con datos)

### ROLES → ENTITIES
- **Relaciones:** 835
- **Profunctors:** governed_by

### ROLES → STORIES
- **Relaciones:** 620
- **Profunctors:** actor_of, role-story

### ENTITIES → ENTITIES
- **Relaciones:** 611
- **Profunctors:** entity_trazado_en, entity_adquirido_por, entity_documentada_en, entity_asistido_por, entity_medido_por

### CAPABILITIES → MODULES
- **Relaciones:** 587
- **Profunctors:** contribuye

### ROLES → PROCESSES
- **Relaciones:** 63
- **Profunctors:** ejecuta

### ROLES → ROLES
- **Relaciones:** 23
- **Profunctors:** supervisa

### PROCESSES → ROLES
- **Relaciones:** 19
- **Profunctors:** process_ejecutado_por

### PROCESSES → ENTITIES
- **Relaciones:** 17
- **Profunctors:** process_manipula

### PROCESSES → PROCESSES
- **Relaciones:** 9
- **Profunctors:** process_triggers

---

## 🚨 Brechas Críticas

| Relación               | Profunctor | Prioridad | Descripción                             |
| ---------------------- | ---------- | --------- | --------------------------------------- |
| stories → capabilities | `requires` | 🟡 MEDIUM  | Capacidades necesarias para la historia |
| stories → processes    | `triggers` | 🟡 MEDIUM  | Procesos que dispara la historia        |
| modules → capabilities | `provides` | 🟡 MEDIUM  | Capacidades que provee el módulo        |
| modules → entities     | `manages`  | 🟡 MEDIUM  | Entidades que gestiona el módulo        |
| capabilities → stories | `enables`  | 🟡 MEDIUM  | Historias habilitadas por la capacidad  |

---

## 💡 Soluciones Propuestas

| Brecha                 | Profunctor | Acción                                                     | Complejidad |
| ---------------------- | ---------- | ---------------------------------------------------------- | ----------- |
| stories → capabilities | `requires` | Usar profunctor story-capability existente                 | 🟢 LOW       |
| stories → processes    | `triggers` | Analizar Stories.acceptance_criteria para inferir procesos | 🔴 HIGH      |
| modules → capabilities | `provides` | Extraer de Modules.capabilities array                      | 🟢 LOW       |
| modules → entities     | `manages`  | Inferir desde Modules.domain ↔ Entities.domain             | 🟡 MEDIUM    |
| capabilities → stories | `enables`  | Definir heurística específica                              | 🔴 HIGH      |