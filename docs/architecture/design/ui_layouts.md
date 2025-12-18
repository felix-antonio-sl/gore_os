# GORE_OS UI Layouts

> **Versión 1.0.0** | Parte del Design System
>
> Plantillas de estructura de página (ViewContainers en IFML) para estandarizar la navegación y disposición del contenido en los diferentes módulos.

---

## 1. App Shell (Layout Principal)
El contenedor base para el 90% de las aplicaciones administrativas de GORE_OS.

```text
┌───────────────────────────────────────────────────────────────────────┐
│ HEADER                                                                │
│ [Logo GORE_OS]  [App Name]        [🔍 Search]      [🔔] [User Menu]   │
├──────────────┬────────────────────────────────────────────────────────┤
│ SIDE NAV     │ MAIN CONTENT AREA                                      │
│              │                                                        │
│ • Dashboard  │  [Breadcrumbs]                                         │
│ • Módulo A   │  [Page Title + Actions]                                │
│ • Módulo B   │                                                        │
│ • Config     │  ┌──────────────────────────────────────────────────┐  │
│              │  │                                                  │  │
│              │  │             Dynamic Page Content                 │  │
│              │  │                                                  │  │
│              │  └──────────────────────────────────────────────────┘  │
│              │                                                        │
├──────────────┴────────────────────────────────────────────────────────┤
│ FOOTER (Optional in Shell, usually in Main Content)                   │
└───────────────────────────────────────────────────────────────────────┘
```

- **Header:** Sticky top. Altura `64px`. Z-index alto.
- **Side Nav:** Collapsible (Icon only vs Full). Ancho `240px` / `64px`.
- **Main Content:** Scrollable area. Padding `space-6` o `space-8`.

---

## 2. Dashboard Layout
Variante del Main Content optimizada para visualización de datos.

- **Grid System:** CSS Grid responsivo.
  - Desktop: 4 columnas.
  - Tablet: 2 columnas.
  - Mobile: 1 columna.
- **Container:** `max-width: 100%` (Fluid) para aprovechar pantallas grandes.

```text
┌───────────┬───────────┬───────────┬───────────┐
│ Metric 1  │ Metric 2  │ Metric 3  │ Metric 4  │
├───────────┴───────────┴┬──────────┴───────────┤
│                        │                      │
│      Main Chart        │    Secondary Chart   │
│      (2 cols)          │    (2 cols)          │
│                        │                      │
├────────────────────────┼──────────────────────┤
│                        │                      │
│      Data Table        │     Activity Feed    │
│      (3 cols)          │     (1 col)          │
│                        │                      │
└────────────────────────┴──────────────────────┘
```

---

## 3. Split Layout (GIS / Master-Detail)
Para aplicaciones centradas en mapas (D-TERR) o exploradores de documentos (D-NORM). Maximiza el área de trabajo visual.

```text
┌──────────────────────────────────────┬────────────────────────────────┐
│ PANEL LATERAL (30%-40%)              │ PANEL PRINCIPAL (60%-70%)      │
│ Scrollable                           │ Fixed (No scroll del body)     │
│                                      │                                │
│ [Filtros]                            │                                │
│ [Resultados de Búsqueda]             │        MAP / VISUALIZER        │
│ [Detalles de Selección]              │                                │
│                                      │                                │
│                                      │                                │
│                                      │                                │
│                                      │                                │
└──────────────────────────────────────┴────────────────────────────────┘
```

- **Resizer:** Opcional, permite al usuario ajustar el ancho del panel lateral.
- **Mobile:** Se convierte en pestañas (Tabs) o Panel colapsable (Bottom Sheet) sobre el mapa.

---

## 4. Focused Layout (Enfoque Único)
Para Login, Encuestas (D-PLAN), Wizards fullscreen o páginas de Error. Sin navegación lateral ni header complejo.

```text
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                                                                       │
│                     ┌───────────────────────────┐                     │
│                     │                           │                     │
│                     │      CENTERED CARD        │                     │
│                     │      (Max-w-lg)           │                     │
│                     │                           │                     │
│                     │      [Logo]               │                     │
│                     │      [Title]              │                     │
│                     │      [Form Content]       │                     │
│                     │                           │                     │
│                     │      [Primary Action]     │                     │
│                     │                           │                     │
│                     └───────────────────────────┘                     │
│                                                                       │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

- **Fondo:** `surface-50` o patrón sutil.
- **Alineación:** Centrado vertical y horizontal.

---

## 5. Modal & Slide-over Layouts
Para sub-navegación contextual sin perder el contexto principal.

- **Modal (Dialog):** Para confirmaciones o formularios cortos. Centrado, con backdrop oscuro.
- **Slide-over (Sheet/Drawer):** Para detalles de registros (Master-Detail) o formularios largos. Desliza desde la derecha (`z-index` máximo).

---

*GORE_OS UI Layouts v1.0.0*
