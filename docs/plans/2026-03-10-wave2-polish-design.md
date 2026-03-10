# Wave 2 — Polish Components Design

**Date**: 2026-03-10
**Approach**: Atomic components + progressive migration (Approach A)

## Context

Post-Wave 1 Identity, the frontend has ~15 pages with duplicated page header patterns, ~37 inconsistent empty states, and 4 delete actions without confirmation dialogs. Three shared components eliminate this duplication and improve UX safety.

## Components

### 1. PageHeader

Replaces the repeated `div > (div > h1 + p) + (div > buttons)` block.

```tsx
interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}
```

Renders: `flex items-center justify-between` wrapper, `h1 text-2xl font-bold`, optional `p text-muted-foreground text-sm mt-1`, actions slot with `flex items-center gap-2`.

**Migration targets** (~15): compromisos, convenios, presupuesto, problemas, alertas, actos, ipr, core-sessions, reuniones, cartera, admin/usuarios, admin/divisiones, admin/umbrales, admin/niveles-sni, presupuesto/ciclo.

### 2. EmptyState

Replaces ~37 inconsistent "no data" messages.

```tsx
interface EmptyStateProps {
  icon?: React.ReactNode;     // default: Inbox from lucide
  title: string;
  description?: string;
  action?: React.ReactNode;
  compact?: boolean;          // for IPR tabs — text only, no icon
}
```

Two variants:
- **Normal** (default): centered, large icon (size-10 stroke-1), medium text
- **Compact**: no icon, `text-sm text-muted-foreground` only

DataTable's inline empty state refactored to use EmptyState internally.

**Migration targets** (~20): 10 main list pages + 13 IPR tabs (partial).

### 3. ConfirmDialog

For destructive actions currently lacking confirmation.

```tsx
interface ConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  onConfirm: () => void | Promise<void>;
  variant?: "destructive" | "default";
  confirmLabel?: string;      // default: "Eliminar"
  cancelLabel?: string;       // default: "Cancelar"
  loading?: boolean;
}
```

Uses Radix AlertDialog (already in shadcn/ui). Focus trap, blocks background interaction.

**Migration targets** (~5): tab-partes, tab-territorio, tab-parentesco, tab-admisibilidad, admin/usuarios toggle.

## Impact

| Component | Files affected | Lines removed (est.) |
|-----------|:-:|:-:|
| PageHeader | ~15 | ~90 |
| EmptyState | ~20 | ~60 |
| ConfirmDialog | ~5 | ~30 + UX safety |
| **Total** | **~25 unique** | **~180** |

3 new files, ~25 files edited, ~180 duplicated lines removed.

## Non-goals

- No motion/animation (Wave 3)
- No new pages or API changes
- No DateRangePicker (deferred — no immediate need)
