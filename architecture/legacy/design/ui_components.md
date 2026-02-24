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

| Componente      | Props / States                                                               | Uso / Accesibilidad                                                                   |
| :-------------- | :--------------------------------------------------------------------------- | :------------------------------------------------------------------------------------ |
| `LayerSwitcher` | `layers: Layer[]`, `activeLayerId: string`, `onToggle: (id: string) => void` | Control flotante. **A11y:** Usar `role="menu"` y atajos numéricos para capas rápidas. |
| `GeoFilter`     | `extent: Bounds`, `filters: FilterState`, `onFilterChange`                   | Filtros espaciales. **A11y:** Anunciar cambios de resultados vía `aria-live`.         |
| `FeaturePopup`  | `data: FeatureProperties`, `onAction: (a: Action) => void`                   | Tooltip rico. **A11y:** `focus-trap` si contiene botones de acción.                   |

### Timelines & Procesos

Soporte para visualización temporal (`US-FIN-IPR-007`).

| Componente      | Props / States                                                  | Uso / Accesibilidad                                                                               |
| :-------------- | :-------------------------------------------------------------- | :------------------------------------------------------------------------------------------------ |
| `StatusTracker` | `steps: Step[]`, `currentId: string`, `orientation: 'v' \| 'h'` | Refleja flujo IFML. **A11y:** `aria-current="step"`. Indicadores visuales + textuales de estado.  |
| `AuditTimeline` | `events: Event[]`, `onExpand: (id: string) => void`             | Logs de auditoría. **A11y:** Navegación por teclado entre eventos; `aria-expanded` para detalles. |

---

## 5. Componentes AI (Agentic UI)

Componentes específicos para interactuar con agentes (D-EVOL).

| Componente       | Props                  | Comportamiento                                                                      |
| :--------------- | :--------------------- | :---------------------------------------------------------------------------------- |
| `MagicInput`     | `onGenerate` (Promise) | Input con botón de "estrellas". Al clickear, estado `loading` y reemplazo de texto. |
| `CopilotSidebar` | `context` (JSON)       | Panel lateral persistente que mantiene el contexto de la página actual.             |

---

## 6. Mapeo de Interacción y Datos (IFML)

Para formalizar el comportamiento de los componentes en flujos complejos, se definen sus roles según el estándar IFML.

### Tipos de Componentes

| Componente GORE_OS | Estereotipo IFML | Eventos Principales        | Data Binding (In/Out)          |
| :----------------- | :--------------- | :------------------------- | :----------------------------- |
| **TanStack Table** | `List`           | `SelectEvent` (onRowClick) | **Out:** `selectedRow: Object` |
| **Form (+Inputs)** | `Form`           | `SubmitEvent` (onSubmit)   | **Out:** `payload: ZodSchema`  |
| **MetricCard**     | `Details`        | `N/A`                      | **In:** `metricData: JSON`     |
| **StatusTracker**  | `ViewComponent`  | `StepSelectEvent`          | **In:** `currentStep: Number`  |
| **MapLibre**       | `ViewComponent`  | `SelectEvent` (onFeature)  | **Out:** `feature: GeoJSON`    |

### Parámetros y Flujos (Data Binding)

1.  **Navigation Flow:** Al dispararse un `Event` (ej. click en fila de tabla), los parámetros de salida (`Out`) se inyectan en el componente/contenedor destino.
2.  **Explicit Binding:** Usamos **tRPC** y **TanStack Query** para el binding de datos dinámicos, asegurando que el estado de la UI (`ViewComponent`) sea un reflejo reactivo del `DataBinding` (Base de datos).
3.  **ContextVariables:** Información persistente (ej. `userID`, `activeCommune`) se maneja vía React Context, mapeando directamente a `DataContextVariable` de IFML.

---

*GORE_OS UI Components v2.1.0 (IFML Compliant)*
