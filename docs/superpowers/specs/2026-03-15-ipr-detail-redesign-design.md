# IPR Detail Redesign — Compact Header + Sidebar Nav

> Rediseño radical de la página de detalle IPR. De stack vertical (~460px chrome) a layout 2-panel con sticky header (~48px) + sidebar vertical de navegación.

## Problema

La página de detalle IPR apila 5 componentes (HeroCard, PhaseStepper, HistorySection, TransitionPanel, TrackCard) verticalmente antes de los 17 tabs. Resultado: ~460px de chrome antes del contenido de trabajo. La misma vista se muestra para una IPR en F0 (todo accionable) y una en F5/Cerrado (todo readonly). El usuario scrollea más de lo que trabaja.

## Solución

1. **Sticky header** (~48px): identidad compacta de la IPR (código, nombre, mecanismo, estado, fase, ejecutor, responsable, acciones)
2. **Sidebar vertical** (~200px): 17 tabs organizados en 4 grupos con labels, siempre visible sin scroll
3. **Tab "Resumen"**: absorbe PhaseStepper, TrackCard, TransitionPanel, HistorySection — el contexto completo vive en UN tab, no apilado sobre TODOS los tabs
4. **Deep link**: si URL tiene `?tab=X`, abre ese tab. Si no, abre Resumen

## Diseño detallado

### Sticky Header (`ipr-sticky-header.tsx`)

Reemplaza IprHeroCard. Una barra compacta de ~48px, sticky al top.

**Contenido (una o dos líneas responsive):**

```
← 2301ADCC010 · CINE EN TU COMUNA: 5° FESTIVAL DE CINE...   [SUBV8]  [Cerrado]  [F5]
  Ejecutor: ASOC. ÑUBLE AUDIOVISUAL   Responsable: Juan Pérez                    [⋮]
```

**Elementos:**
- Back button (ArrowLeft icon, onClick → router.back())
- Código BIP (font-mono, text-xs, muted)
- Separador "·"
- Nombre IPR (font-medium, truncate con max-w)
- Mecanismo badge (colored: SNI/FRIL/SUBV8/etc.)
- Status badge (StatusBadge component, size sm)
- Phase badge (colored: F0-F5)
- Segunda línea: Ejecutor + Responsable GORE (text-xs, muted)
- Menú acciones (⋮ dropdown): Editar nombre, Asignar Responsable, Exportar — oculto si estado terminal

**Props:**
```typescript
interface IprStickyHeaderProps {
  ipr: IprDetail;
  canEdit: boolean;
  canAssign: boolean;
  onEdit: () => void;
  onAssign: () => void;
}
```

**Responsive:** En mobile (<768px), segunda línea se oculta. Nombre se trunca más agresivamente. Menú ⋮ se mantiene.

### Sidebar Navigation (`ipr-sidebar-nav.tsx`)

Reemplaza TabsList horizontal. Columna fija de ~200px a la izquierda.

**Estructura:**
```
RESUMEN          ← item especial, siempre primero
─────────────
OPERACIÓN
  Compromisos
  Problemas
  Hitos
  Avances
  Alertas
─────────────
FINANZAS
  Presupuesto
  Convenios
  Rendiciones
  Resoluciones
─────────────
REQUISITOS
  Partes
  Territorio
  Evaluación
  Parentesco
─────────────
CICLO
  Admisibilidad
  Modificaciones
  Cierre
  Eval. Posterior
```

**Comportamiento:**
- Group labels: text-[10px] uppercase tracking-wider text-muted-foreground
- Items: text-sm, py-1.5 px-3, rounded-md
- Active item: bg-accent font-medium
- Hover: bg-muted/50
- Click: update `?tab=X` URL param (useTabParam)
- Sticky: position fixed, height calc(100vh - 48px), overflow-y auto
- Separator: border-b between groups

**Mobile (<768px):** Sidebar se oculta. Un selector `<Select>` dropdown aparece encima del contenido para cambiar de tab. O un bottom sheet con la lista.

**Props:**
```typescript
interface IprSidebarNavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}
```

### Tab Resumen (`tab-resumen.tsx`)

Nuevo tab que absorbe los componentes que hoy viven apilados sobre los tabs.

**Contenido (orden vertical):**
1. **PhaseStepper** — ciclo de vida con elapsed time
2. **TransitionPanel** — si canTransition (gate overview + selector + effects)
3. **TrackCard** — mecanismo, evaluador, dictamen, requisitos, plazos
4. **HistorySection** — historial de transiciones (colapsable)
5. **Metadata expandida** — presupuesto total, descripción, sector, fuente, fechas inicio/término

**Comportamiento:** Cada sección es un card (`rounded-xl border bg-card p-4`). Las secciones que no aplican no se renderizan (e.g., TrackCard si no hay mecanismo, TransitionPanel si no canTransition, presupuesto si es null/0).

**Props:**
```typescript
interface TabResumenProps {
  ipr: IprDetail;
  transitions: IprTransition[] | null;
  transLoading: boolean;
  trackInfo: TrackInfo | null;
  history: HistoryEntry[];
  canTransition: boolean;
  selectedTransition: string;
  onSelectTransition: (v: string) => void;
  onTransition: () => void;
  transSubmitting: boolean;
  transError: string | null;
}
```

### Page Layout (`ipr/[id]/page.tsx`)

**Reescritura del layout:**

```tsx
<div className="flex flex-col h-screen">
  {/* Sticky header — fixed top */}
  <IprStickyHeader ipr={ipr} ... />

  {/* Main area — sidebar + content */}
  <div className="flex flex-1 overflow-hidden">
    {/* Sidebar — fixed left, hidden on mobile */}
    <aside className="hidden md:block w-52 border-r overflow-y-auto shrink-0">
      <IprSidebarNav activeTab={activeTab} onTabChange={setActiveTab} />
    </aside>

    {/* Content — scrollable */}
    <main className="flex-1 overflow-y-auto p-6">
      {/* Mobile tab selector */}
      <div className="md:hidden mb-4">
        <Select value={activeTab} onValueChange={setActiveTab}>...</Select>
      </div>

      {/* Tab content */}
      {activeTab === "resumen" && <TabResumen ... />}
      {activeTab === "compromisos" && <TabCompromisos ... />}
      {activeTab === "problemas" && <TabProblemas ... />}
      {/* ... 15 more tabs ... */}
    </main>
  </div>
</div>
```

**Nota:** Ya no usa `<Tabs>` de Radix. Usa `useTabParam` + conditional rendering. La sidebar controla `activeTab` via `onTabChange` que actualiza el URL param.

### Qué se elimina

| Componente | Destino |
|-----------|---------|
| `ipr-hero-card.tsx` | ELIMINAR — reemplazado por `ipr-sticky-header.tsx` |
| TabsList horizontal | ELIMINAR — reemplazado por `ipr-sidebar-nav.tsx` |
| `<Tabs>` wrapper de Radix | ELIMINAR — reemplazado por conditional rendering + useTabParam |

### Qué se mueve

| Componente | De | A |
|-----------|------|------|
| `ipr-phase-stepper.tsx` | Pre-tab stack | Dentro de `tab-resumen.tsx` |
| `ipr-transition-panel.tsx` | Pre-tab stack | Dentro de `tab-resumen.tsx` |
| `track-card.tsx` | Pre-tab stack | Dentro de `tab-resumen.tsx` |
| `ipr-history-section.tsx` | Pre-tab stack | Dentro de `tab-resumen.tsx` |

### Qué se crea

| Componente | Responsabilidad |
|-----------|----------------|
| `ipr-sticky-header.tsx` | Header compacto con identity + badges + acciones |
| `ipr-sidebar-nav.tsx` | Navegación vertical 18 items en 5 grupos |
| `tab-resumen.tsx` | Absorbe stepper + transition + track + history + metadata |

### Archivos a crear/modificar

| Archivo | Acción |
|---------|--------|
| `ipr/components/ipr-sticky-header.tsx` | CREAR |
| `ipr/components/ipr-sidebar-nav.tsx` | CREAR |
| `ipr/components/tab-resumen.tsx` | CREAR |
| `ipr/[id]/page.tsx` | REESCRIBIR layout |
| `ipr/components/ipr-hero-card.tsx` | ELIMINAR |
| `ipr/components/ipr-constants.ts` | MODIFICAR (agregar "resumen" a TAB_GROUPS) |

### Estimación

- 3 componentes nuevos (~300 líneas total)
- 1 componente eliminado (~120 líneas)
- 1 página reescrita (~200 líneas, baja de ~440)
- Total neto: ~250 líneas nuevas, ~360 eliminadas = **−110 líneas**

## Decisiones de diseño

1. **Sticky header > HeroCard**: El header es identidad (quién soy), no detalle (qué tengo). La identidad cabe en 48px.
2. **Sidebar > tabs horizontales**: 17+ items se escanean mejor verticalmente. La sidebar está siempre visible sin scroll horizontal.
3. **Tab Resumen > stack pre-tab**: El contexto completo (stepper, track, transitions) es UNA vista, no un overhead que se paga en TODAS las vistas.
4. **Conditional rendering > Radix Tabs**: Sin wrapper Tabs, cada tab se renderiza condicionalmente. Más simple, menos indirección.
5. **Deep link respetado**: `?tab=compromisos` funciona exactamente como antes. Compatibilidad total con action-items del dashboard.
6. **Mobile**: sidebar → dropdown select. Header se adapta. Contenido full-width.
