# GORE_OS UI Components Catalog

> **Versión 2.0.0** | Parte del Design System
>
> Catálogo de componentes visuales reutilizables, organizados por complejidad (Atomic Design).
> **Tech Stack Compatibility:** React 18+, TailwindCSS v3.4+, Shadcn UI.

---

## 1. Stack Técnico Recomendado (Oficial)

Para garantizar la máxima compatibilidad con el stack GORE_OS (Bun + Hono + React + tRPC), se definen las siguientes librerías estándar.

| Categoría            | Librería Recomendada                | Justificación / Nota de Compatibilidad                                                                                   |
| :------------------- | :---------------------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| **Componentes Base** | **Shadcn UI**                       | Arquitectura "Copy-paste" ideal para personalización total. Basado en Radix UI (Accesible) y Tailwind.                   |
| **Iconos**           | **Lucide React**                    | Estándar de facto en el ecosistema Shadcn/Next.js modern. Ligero y treeshakable.                                         |
| **Gráficos**         | **Recharts**                        | La opción más madura para React. **Nota:** Requiere implementación cuidadosa de ARIA labels para accesibilidad completa. |
| **Mapas (GIS)**      | **MapLibre GL JS** (`react-map-gl`) | Rendimiento superior (WebGL) para "Gemelo Digital". Soporta Vector Tiles eficientemente.                                 |
| **Tablas**           | **TanStack Table v8**               | Headless, type-safe y altamente performante para grandes volúmenes de datos (D-FIN).                                     |
| **Formularios**      | **React Hook Form** + **Zod**       | Integración nativa con las validaciones del Backend (tRPC comparte esquemas Zod).                                        |

---

## 2. Átomos (Atomic Components)

### Inputs & Controles

| Componente   | Props Clave                     | Accesibilidad (A11y)                                           | Notas Stack                                       |
| :----------- | :------------------------------ | :------------------------------------------------------------- | :------------------------------------------------ |
| `TextInput`  | `label`, `error`, `placeholder` | `aria-invalid` automático si hay error. Label asociado por ID. | Wrapper sobre `shadcn/input`.                     |
| `Select`     | `options`, `value`, `onChange`  | Soporte teclado completo (Arrows, Enter, Esc).                 | Wrapper sobre `shadcn/select` (Radix).            |
| `DatePicker` | `mode` (single/range), `locale` | Navegación por teclado en calendario.                          | `shadcn/calendar` (basado en `react-day-picker`). |
| `Switch`     | `checked`, `onCheckedChange`    | Role `switch`, label clickeable.                               | `shadcn/switch`.                                  |

### Acciones & Navegación

| Componente | Props Clave                                              | Accesibilidad (A11y)                      | Notas Stack      |
| :--------- | :------------------------------------------------------- | :---------------------------------------- | :--------------- |
| `Button`   | `variant` (default, destructive, outline, ghost), `size` | Focus visible ring.                       | `shadcn/button`. |
| `Tabs`     | `defaultValue`, `orientation`                            | Role `tablist`, `tab`. Arrows move focus. | `shadcn/tabs`.   |

---

## 3. Moléculas (Molecules)

### Cards & Contenedores

| Componente   | Composición                                                                | Uso                                  |
| :----------- | :------------------------------------------------------------------------- | :----------------------------------- |
| `MetricCard` | `CardHeader` > `CardTitle` + `Icon` <br> `CardContent` > `Value` + `Trend` | Dashboard KPIs.                      |
| `Alert`      | `AlertTitle`, `AlertDescription`, `Icon`                                   | Feedback de usuario (Success/Error). |

### Formularios Avanzados

- **`Form` (Component):** Utiliza el contexto de `react-hook-form`. Gestiona automáticamente `aria-describedby` para mensajes de error.
- **Pattern:** Usar `zodResolver` para conectar con esquemas compartidos en `packages/core/src/schema`.

---

## 4. Organismos (Organisms)

### Visualización de Datos (Recharts)

> **Advertencia A11y:** Los gráficos SVG no son accesibles por defecto.
> **Regla:** Todo gráfico debe ir acompañado de una **tabla de datos accesible** (visualmente oculta o en una pestaña "Ver Datos") o descripciones detalladas con `aria-label`.

| Componente        | Implementación         | Uso                                   |
| :---------------- | :--------------------- | :------------------------------------ |
| `TrendChart`      | `LineChart` (Recharts) | Evolución presupuestaria.             |
| `DistributionPie` | `PieChart` (Recharts)  | Distribución de inversión por comuna. |

### Mapas Interactivos (MapLibre)

- **Performance:** Usar Vector Tiles (.pbf) servidos por el backend.
- **Interacción:** `Hover` para tooltips rápidos, `Click` para detalles en panel lateral.
- **A11y:** Proveer controles de zoom por teclado y alternativas textuales para la información geoespacial crítica.

**Componentes GIS Específicos:**

| Componente      | Props                         | Uso                                                                      |
| :-------------- | :---------------------------- | :----------------------------------------------------------------------- |
| `LayerSwitcher` | `layers`, `activeLayer`       | Control flotante para alternar entre capas (ej. Inversión vs Normativa). |
| `GeoFilter`     | `region`, `commune`, `bounds` | Filtros espaciales que actualizan el viewport y los datos cargados.      |
| `FeaturePopup`  | `feature`, `position`         | Tooltip rico con metadatos del objeto seleccionado en el mapa.           |

### Timelines & Procesos

Soporte para visualización temporal (`US-FIN-IPR-007`).

| Componente      | Variantes                | Uso                                                                                                                                          |
| :-------------- | :----------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| `StatusTracker` | `vertical`, `horizontal` | Muestra el estado actual en una secuencia lineal (ej. Pasos de Postulación). Diferencia visual clara entre `completed`, `current`, `future`. |
| `AuditTimeline` | `dense`                  | Lista vertical compacta de eventos históricos con timestamp y autor (Logs de auditoría).                                                     |

---

## 5. Componentes AI (Agentic UI)

Componentes específicos para interactuar con agentes (D-EVOL).

| Componente       | Props                  | Comportamiento                                                                      |
| :--------------- | :--------------------- | :---------------------------------------------------------------------------------- |
| `MagicInput`     | `onGenerate` (Promise) | Input con botón de "estrellas". Al clickear, estado `loading` y reemplazo de texto. |
| `CopilotSidebar` | `context` (JSON)       | Panel lateral persistente que mantiene el contexto de la página actual.             |

---

*GORE_OS UI Components v2.0.0*
