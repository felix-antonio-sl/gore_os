# GORE_OS UI Components Catalog

> **Versión 1.0.0** | Parte del Design System
>
> Catálogo de componentes visuales reutilizables, mapeados a conceptos IFML (ViewComponents) y organizados por complejidad (Atomic Design).

---

## 1. Átomos (Atomic Components)
Bloques fundamentales e indivisibles de la interfaz.

### Inputs & Controles
| Componente     | IFML Mapping     | Descripción                                 | Variantes              |
| -------------- | ---------------- | ------------------------------------------- | ---------------------- |
| `TextInput`    | `Field`          | Campo de texto básico con label y ayuda     | Text, Email, Password  |
| `NumberInput`  | `Field`          | Input numérico con controles +/- opcionales | Currency, Percentage   |
| `Select`       | `SelectionField` | Dropdown nativo o custom                    | Single, Multiple       |
| `Checkbox`     | `SelectionField` | Selección binaria                           | Default, Indeterminate |
| `ToggleSwitch` | `SelectionField` | Interruptor binario inmediato               | ON/OFF                 |
| `DatePicker`   | `Field`          | Selector de fecha/rango                     | Single, Range          |

### Acciones & Navegación
| Componente   | IFML Mapping     | Descripción                                | Variantes                         |
| ------------ | ---------------- | ------------------------------------------ | --------------------------------- |
| `Button`     | `Event`          | Disparador de eventos principal            | Primary, Secondary, Ghost, Danger |
| `IconButton` | `Event`          | Botón solo icono para acciones secundarias | Default, Tooltip                  |
| `Link`       | `NavigationFlow` | Enlace de navegación texto                 | Inline, Standalone                |
| `TabItem`    | `NavigationFlow` | Pestaña individual de navegación           | Active, Inactive                  |

### Feedback & Status
| Componente | IFML Mapping | Descripción                           | Variantes                      |
| ---------- | ------------ | ------------------------------------- | ------------------------------ |
| `Badge`    | N/A          | Etiqueta pequeña de estado o contador | Success, Warning, Error, Agent |
| `Spinner`  | N/A          | Indicador de carga circular           | Sm, Md, Lg                     |
| `Avatar`   | N/A          | Representación de usuario o entidad   | Image, Initials                |
| `Icon`     | N/A          | Representación gráfica vectorial      | 16/20/24/32px                  |

---

## 2. Moléculas (Molecules)
Agrupaciones funcionales de átomos.

### Cards & Contenedores
| Componente   | Propósito                         | Composición típica                                   |
| ------------ | --------------------------------- | ---------------------------------------------------- |
| `SimpleCard` | Contenedor básico de información  | Title + Body + Footer                                |
| `MetricCard` | KPI individual (Dashboard)        | Icono + Valor + Tendencia + MiniChart                |
| `ActionCard` | Acceso directo a una acción       | Icono + Título + Descripción + Flecha                |
| `FileCard`   | Representación de archivo adjunto | Icono Tipo + Nombre + Tamaño + Acciones (Ver/Borrar) |

### Listas & Tablas Simples
| Componente        | Propósito                   | Composición típica                  |
| ----------------- | --------------------------- | ----------------------------------- |
| `ListItem`        | Elemento de lista estándar  | Avatar + Texto Princ/Sec + Acciones |
| `DescriptionList` | Pares clave-valor (Detalle) | Label (gris) + Value (negro)        |
| `TimelineItem`    | Evento en línea de tiempo   | Punto/Icono + Fecha + Contenido     |

### Formularios & Búsqueda
| Componente    | Propósito                      | Composición típica                           |
| ------------- | ------------------------------ | -------------------------------------------- |
| `SearchBar`   | Barra de búsqueda global/local | Input + SearchIcon + ClearButton + (Filters) |
| `FilterGroup` | Conjunto de filtros            | Label + Select/Checkbox Group                |
| `FormGroup`   | Bloque lógico de formulario    | Título Sección + Inputs Relacionados         |

### Alertas Específicas
| Componente      | Propósito                      | Composición típica                           |
| --------------- | ------------------------------ | -------------------------------------------- |
| `ToastAlert`    | Notificación temporal flotante | Icono Estado + Mensaje + Cerrar              |
| `InlineAlert`   | Alerta contextual en contenido | Icono + Título + Cuerpo + (Acción)           |
| `SemaphoreCard` | Alerta de mora/estado crítico  | Barra color (Semáforo) + Días Mora + Mensaje |

---

## 3. Organismos (Organisms)
Componentes complejos que forman secciones completas de la UI.

### Gestión de Datos
| Componente    | IFML   | Descripción                                                                                                |
| ------------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| `DataTable`   | `List` | Tabla avanzada con ordenamiento, filtrado, paginación y acciones por fila/lote. **Crítico D-FIN, D-BACK**. |
| `KanbanBoard` | `List` | Tablero de columnas por estado (Drag & Drop opcional). **Crítico D-EJEC, FÉNIX**.                          |
| `TreeViewer`  | `List` | Visualizador jerárquico de carpetas o estructuras. **Crítico D-NORM, D-PLAN**.                             |

### Visualización Avanzada
| Componente      | IFML      | Descripción                                                                      |
| --------------- | --------- | -------------------------------------------------------------------------------- |
| `FSMStatusFlow` | `Details` | Barra de progreso de estados (Pasado / Presente / Futuro). **Crítico IPR Core**. |
| `MapViewer`     | `List`    | Visor GIS con control de capas, popups y leyenda. **Crítico D-TERR**.            |
| `GanttCalendar` | `List`    | Calendario / Cronograma interactivo de proyectos. **Crítico D-EJEC, D-FIN**.     |
| `RadarScore`    | `Details` | Gráfico de radar para evaluaciones multidimensionales. **Crítico Ejecutores**.   |

### Navegación Estructurada
| Componente      | IFML             | Descripción                                                          |
| --------------- | ---------------- | -------------------------------------------------------------------- |
| `WizardStepper` | `ViewContainer`  | Navegación paso a paso para formularios largos. Validación por paso. |
| `SideNav`       | `ViewContainer`  | Menú lateral principal de la aplicación.                             |
| `Breadcrumbs`   | `NavigationFlow` | Ruta de navegación jerárquica actual.                                |

---

## 4. Componentes de Agentes IA (Agentic UI)
Componentes específicos para la interacción con LLMs y automatizaciones.

| Componente          | Uso Principal          | Descripción Visual                                                                            |
| ------------------- | ---------------------- | --------------------------------------------------------------------------------------------- |
| `ChatWidget`        | Asistencia Contextual  | Botón flotante o panel lateral derecho. Historial de chat tipo mensajería.                    |
| `SuggestionPopover` | Proactividad           | Tooltip enriquecido que aparece sobre elementos (ej. Inputs) con sugerencias ("Considera X"). |
| `AgentResponseCard` | Respuesta Estructurada | Tarjeta dentro del chat o contenido mostrando respuesta del agente con citas y acciones.      |
| `NotificationBadge` | Alertas Background     | Badge en header que agrupa notificaciones de agentes (p.ej. "Vigilante completó análisis").   |
| `MagicInput`        | Autocompletar IA       | Input de texto con icono de "estrellas" que permite generar/refinar texto con IA.             |

---

## 5. Mapeo a Librerías Técnicas

Para la implementación (React), se recomienda:

- **Base UI:** [Shadcn UI](https://ui.shadcn.com/) (Radix Primitives)
- **Iconos:** [Lucide React](https://lucide.dev/guide/packages/lucide-react)
- **Gráficos:** [Recharts](https://recharts.org/) (DataViz estándar)
- **Mapas:** `react-leaflet` o `maplibre-gl-js`
- **Tablas:** `@tanstack/react-table`
- **Drag & Drop:** `@hello-pangea/dnd` (Kanban)

---

*GORE_OS UI Components v1.0.0*
