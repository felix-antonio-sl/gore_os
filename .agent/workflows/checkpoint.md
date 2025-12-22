---
description: Sincroniza el progreso del trabajo en JOURNAL.md y TASKS.md
---

Este workflow automatiza el cierre de hitos de trabajo.

1. **Analizar cambios:** Identificar qué archivos se modificaron en el turno.
2. **Actualizar JOURNAL.md:** 
   - Agregar entrada con fecha actual.
   - Listar logros, decisiones y riesgos detectados.
3. **Actualizar TASKS.md:**
   - Mover tareas de `NOW` a `DONE`.
   - Promover tareas de `NEXT` a `NOW`.
   - Limpiar el backlog si es necesario.
4. **Resumen visual:** Presentar al usuario una tarjeta con el estado actualizado.
