# GORE_OS UI Interaction Patterns

> **Versión 1.0.0** | Parte del Design System
>
> Patrones de interacción estándar para resolver problemas comunes de UI/UX, inspirados en IFML y adaptados a las necesidades de GORE_OS.

---

## 1. Patrones Estructurales (Layout Patterns)

### 📄 Master-Detail (Maestro-Detalle)
**Uso:** Gestión de registros (CRUD), listados de entidades.
**Dominios:** D-BACK, D-NORM, M7-Ejecutores.

- **Vista Master:** Tabla o Lista con filtros y búsqueda. Muestra resumen de registros.
- **Vista Detail:** Panel lateral (Sheet) o página dedicada con la información completa del registro seleccionado.
- **Comportamiento:**
  - Al hacer click en fila → Abre detalle.
  - La URL debe cambiar (`/recursos/123`) para permitir compartir enlaces (Deep Linking).

### 📊 Dashboard (Cuandro de Mando)
**Uso:** Monitoreo, KPIs, Alertas.
**Dominios:** D-GESTION, D-SEG, D-OPS.

- **Grid Layout:** Tarjetas organizadas en grilla responsive.
- **Jerarquía:**
  1. **Top:** KPIs críticos (MetricCards) y Alertas activas.
  2. **Middle:** Gráficos de tendencia y desgloses.
  3. **Bottom:** Listados recientes o detallados.
- **Interactividad:** Drill-down (click en gráfico filtra los datos).

### 🧙‍♂️ Wizard (Asistente Paso a Paso)
**Uso:** Procesos secuenciales complejos, formularios largos.
**Dominios:** D-FIN (Postulaciones), D-NORM (Actos), Rendiciones.

- **Stepper:** Barra de progreso superior indicando pasos (Pasado/Presente/Futuro).
- **Validación:** No permite avanzar si el paso actual es inválido.
- **Guardado:** Auto-guardado de "Borrador" en cada cambio de paso.
- **Navegación:** Botones "Atrás" y "Siguiente" claros. "Finalizar" en el último.

---

## 2. Patrones de Navegación y Búsqueda

### 🔍 Search & Filter (Búsqueda Facetada)
**Uso:** Encontrar IPRs, Documentos, Normativas.

- **Barra Simple:** Input de texto para búsqueda difusa (Fuzzy).
- **Filtros Avanzados:** Panel colapsable con Selects múltiples y Rangos de fecha.
- **Chips de Filtro:** Los filtros activos se muestran como chips removibles bajo la barra.
- **Resultados:** Instantáneos (debounce) o tras "Buscar". Empty States amigables.

### 🌳 Hierarchical Browse (Navegación en Árbol)
**Uso:** Expedientes, ERD, Carpetas.

- **Tree View:** Estructura colapsable con indentación.
- **Breadcrumbs:** Muestra la ruta actual (`Home > D-FIN > IPR > 2024`).
- **Preview:** Al seleccionar un nodo hoja, se muestra su contenido (FileViewer).

---

## 3. Patrones de Acción y Estado

### 🚦 FSM Transition (Flujo de Estados)
**Uso:** Ciclo de vida IPR, Actos Administrativos.

- **Visualización:** `FSMStatusFlow` mostrando el estado actual y los posibles siguientes.
- **Acciones Transicionales:** Los botones de acción son las transiciones válidas (ej. "Aprobar", "Observar").
- **Bloqueo:** Acciones inválidas para el rol o estado actual están deshabilitadas o ocultas.

### 📝 Inline Editing (Edición en Línea)
**Uso:** Correcciones rápidas, datagrids editables.

- **Modo Lectura:** Texto plano.
- **Modo Edición:** Al hacer click/hover, se convierte en Input.
- **Guardado:** Check/Enter para guardar, Esc para cancelar. Optimista (feedback inmediato).

---

## 4. Patrones de Agentes IA (Agentic Patterns)

### 🤖 Contextual Assistance (Asistencia Contextual)
**Uso:** Ayuda en formularios complejos, dudas normativas.

- **Trigger:** Botón `ChatWidget` o icono de ayuda en campo específico.
- **Contexto:** El agente recibe el JSON de la entidad/formulario actual en el prompt oculto.
- **Respuesta:**
  - Explicación textual.
  - Citas a normativa (KB).
  - Sugerencia de valor (Actionable).

### 🔔 Proactive Alerting (Alertas Proactivas)
**Uso:** Detección de mora, errores, oportunidades.

- **Toast/Banner:** Aparición no intrusiva pero visible.
- **Accionable:** La alerta incluye botón "Ver Problema" o "Corregir".
- **Agrupación:** Si hay muchas alertas del mismo tipo, se agrupan ("5 IPRs en mora").

### ✨ AI Autocomplete (Generación de Contenido)
**Uso:** Redacción de resúmenes, oficios, observaciones.

- **Magic Input:** Campo de texto con botón "✨ Mejorar" o "✨ Generar".
- **Prompt:** Usuario escribe idea base ("rechazar por falta de firma").
- **Generación:** IA expande a texto formal ("Se rechaza la presente rendición debido a...").
- **Revisión:** Usuario debe aceptar o editar antes de guardar.

---

## 5. Patrones de Feedback

### 💾 Optimistic UI (Feedback Optimista)
**Uso:** Likes, cambios de estado simples.
- La UI se actualiza inmediatamente asumiendo éxito.
- Si falla la API, se revierte y muestra error (Toast).

### ⏳ Skeleton Loading (Carga Esqueleto)
**Uso:** Carga inicial de datos.
- Muestra la estructura de la página en gris pulsante.
- Reduce la percepción de tiempo de espera y evita saltos de layout (CLS).

---

*GORE_OS UI Patterns v1.0.0*
