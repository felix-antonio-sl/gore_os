# Wave 2 Polish — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extract 3 shared components (PageHeader, EmptyState, ConfirmDialog) and migrate ~25 files to eliminate ~180 duplicated lines.

**Architecture:** Create atomic components in `web/src/components/`, install AlertDialog shadcn primitive, then progressively migrate main CRUD pages and IPR tabs.

**Tech Stack:** Next.js 16, React 19, shadcn/ui (Radix), TailwindCSS v4, lucide-react.

---

### Task 1: Install AlertDialog shadcn primitive

**Files:**
- Create: `web/src/components/ui/alert-dialog.tsx`

**Step 1: Install AlertDialog via shadcn CLI**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx shadcn@latest add alert-dialog`

Expected: Creates `web/src/components/ui/alert-dialog.tsx`

**Step 2: Verify file was created**

Run: `ls web/src/components/ui/alert-dialog.tsx`

Expected: File exists

**Step 3: Commit**

```bash
git add web/src/components/ui/alert-dialog.tsx
git commit -m "chore: add shadcn AlertDialog primitive"
```

---

### Task 2: Create PageHeader component

**Files:**
- Create: `web/src/components/page-header.tsx`

**Step 1: Write the component**

```tsx
import { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold">{title}</h1>
        {description && (
          <p className="text-muted-foreground text-sm mt-1">{description}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}
```

**Step 2: Build to verify no errors**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/components/page-header.tsx
git commit -m "feat(components): add PageHeader shared component"
```

---

### Task 3: Create EmptyState component

**Files:**
- Create: `web/src/components/empty-state.tsx`

**Step 1: Write the component**

```tsx
import { ReactNode } from "react";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  compact?: boolean;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  compact = false,
}: EmptyStateProps) {
  if (compact) {
    return <p className="text-sm text-muted-foreground">{title}</p>;
  }

  return (
    <div className="flex flex-col items-center gap-2 py-12 text-muted-foreground">
      {icon ?? <Inbox className="size-10 stroke-1" />}
      <p className="text-sm font-medium">{title}</p>
      {description && <p className="text-xs">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
```

**Step 2: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/components/empty-state.tsx
git commit -m "feat(components): add EmptyState shared component"
```

---

### Task 4: Create ConfirmDialog component

**Files:**
- Create: `web/src/components/confirm-dialog.tsx`

**Step 1: Write the component**

```tsx
"use client";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { buttonVariants } from "@/components/ui/button";

interface ConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  onConfirm: () => void | Promise<void>;
  variant?: "destructive" | "default";
  confirmLabel?: string;
  cancelLabel?: string;
  loading?: boolean;
}

export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  onConfirm,
  variant = "destructive",
  confirmLabel = "Eliminar",
  cancelLabel = "Cancelar",
  loading = false,
}: ConfirmDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={loading}>{cancelLabel}</AlertDialogCancel>
          <AlertDialogAction
            className={variant === "destructive" ? buttonVariants({ variant: "destructive" }) : undefined}
            onClick={(e) => {
              e.preventDefault();
              onConfirm();
            }}
            disabled={loading}
          >
            {loading ? "Procesando..." : confirmLabel}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
```

Note: `e.preventDefault()` prevents AlertDialog from auto-closing, allowing async `onConfirm` to control when dialog closes (via `onOpenChange(false)` after success).

**Step 2: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/components/confirm-dialog.tsx
git commit -m "feat(components): add ConfirmDialog shared component"
```

---

### Task 5: Migrate PageHeader — batch 1 (compromisos, convenios, presupuesto, problemas, alertas)

**Files:**
- Modify: `web/src/app/(app)/compromisos/page.tsx`
- Modify: `web/src/app/(app)/convenios/page.tsx`
- Modify: `web/src/app/(app)/presupuesto/page.tsx`
- Modify: `web/src/app/(app)/problemas/page.tsx`
- Modify: `web/src/app/(app)/alertas/page.tsx`

**Step 1: For each file, replace the header block**

In each file:
1. Add import: `import { PageHeader } from "@/components/page-header";`
2. Replace the `<div className="flex items-center justify-between">...(h1 + p + buttons)...</div>` with `<PageHeader title="..." description="..." actions={<>...buttons...</>} />`

Pattern to find and replace (identical structure in all 5 files):
```tsx
// BEFORE:
<div className="flex items-center justify-between">
  <div>
    <h1 className="text-2xl font-bold">Title</h1>
    <p className="text-muted-foreground text-sm mt-1">Description</p>
  </div>
  <div className="flex ...gap-2">
    ...buttons...
  </div>
</div>

// AFTER:
<PageHeader
  title="Title"
  description="Description"
  actions={<>...buttons...</>}
/>
```

**Step 2: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds, all 36 routes compile

**Step 3: Commit**

```bash
git add web/src/app/(app)/compromisos/page.tsx web/src/app/(app)/convenios/page.tsx web/src/app/(app)/presupuesto/page.tsx web/src/app/(app)/problemas/page.tsx web/src/app/(app)/alertas/page.tsx
git commit -m "refactor(frontend): migrate 5 CRUD pages to PageHeader component"
```

---

### Task 6: Migrate PageHeader — batch 2 (actos, ipr, core-sessions, reuniones, cartera)

**Files:**
- Modify: `web/src/app/(app)/actos/page.tsx`
- Modify: `web/src/app/(app)/ipr/page.tsx`
- Modify: `web/src/app/(app)/core-sessions/page.tsx`
- Modify: `web/src/app/(app)/reuniones/page.tsx`
- Modify: `web/src/app/(app)/cartera/page.tsx`

Same pattern as Task 5. Each file gets `import { PageHeader }` and the header block replaced.

**Step 1: Apply replacements in all 5 files**

**Step 2: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/app/(app)/actos/page.tsx web/src/app/(app)/ipr/page.tsx web/src/app/(app)/core-sessions/page.tsx web/src/app/(app)/reuniones/page.tsx web/src/app/(app)/cartera/page.tsx
git commit -m "refactor(frontend): migrate 5 more pages to PageHeader component"
```

---

### Task 7: Migrate PageHeader — batch 3 (admin pages + ciclo)

**Files:**
- Modify: `web/src/app/(app)/admin/usuarios/page.tsx`
- Modify: `web/src/app/(app)/admin/divisiones/page.tsx`
- Modify: `web/src/app/(app)/admin/umbrales/page.tsx`
- Modify: `web/src/app/(app)/admin/niveles-sni/page.tsx`
- Modify: `web/src/app/(app)/presupuesto/ciclo/page.tsx`

Same pattern. Some admin pages may have slightly different structure (e.g., no description) — PageHeader handles this via optional `description` prop.

**Step 1: Apply replacements in all 5 files**

**Step 2: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/app/(app)/admin/usuarios/page.tsx web/src/app/(app)/admin/divisiones/page.tsx web/src/app/(app)/admin/umbrales/page.tsx web/src/app/(app)/admin/niveles-sni/page.tsx web/src/app/(app)/presupuesto/ciclo/page.tsx
git commit -m "refactor(frontend): migrate admin + ciclo pages to PageHeader component"
```

---

### Task 8: Migrate EmptyState — DataTable + main list pages

**Files:**
- Modify: `web/src/components/data-table.tsx` — replace inline empty state with `<EmptyState>`
- Modify: `web/src/app/(app)/alertas/page.tsx` — replace inline empty `<p>` with `<EmptyState compact>`
- Modify: `web/src/app/(app)/mis-compromisos/page.tsx` — same
- Modify: `web/src/app/(app)/dashboard/page.tsx` — same for alerts and cockpit sections

**Step 1: In data-table.tsx, replace the empty state block**

```tsx
// BEFORE (lines 69-81):
{data.length === 0 ? (
  <TableRow>
    <TableCell colSpan={columns.length} className="py-12">
      <div className="flex flex-col items-center gap-2 text-muted-foreground">
        <Inbox className="h-10 w-10 stroke-1" />
        <p className="text-sm font-medium">Sin resultados</p>
        <p className="text-xs">Intente ajustar los filtros</p>
      </div>
    </TableCell>
  </TableRow>
)

// AFTER:
{data.length === 0 ? (
  <TableRow>
    <TableCell colSpan={columns.length} className="py-12">
      <EmptyState title="Sin resultados" description="Intente ajustar los filtros" />
    </TableCell>
  </TableRow>
)
```

Add `import { EmptyState } from "@/components/empty-state";` and remove `import { Inbox } from "lucide-react";` (if Inbox is only used there).

**Step 2: In other pages, replace standalone empty paragraphs with `<EmptyState compact>`**

**Step 3: Build to verify**

**Step 4: Commit**

```bash
git add web/src/components/data-table.tsx web/src/app/(app)/alertas/page.tsx web/src/app/(app)/mis-compromisos/page.tsx web/src/app/(app)/dashboard/page.tsx
git commit -m "refactor(frontend): migrate DataTable + 3 pages to EmptyState component"
```

---

### Task 9: Migrate EmptyState — IPR tabs

**Files:**
- Modify: `web/src/app/(app)/ipr/components/tab-convenios.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-cdps.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-resoluciones.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-territorio.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-avances.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-hitos.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-partes.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-parentesco.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-alertas.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-evaluaciones.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-admisibilidad.tsx`

**Step 1: In each tab file, replace empty state paragraphs**

Pattern (same in all tabs):
```tsx
// BEFORE:
<p className="text-sm text-muted-foreground">No hay X para este IPR.</p>

// AFTER:
<EmptyState compact title="No hay X para este IPR." />
```

Add `import { EmptyState } from "@/components/empty-state";` to each.

**Step 2: Build to verify**

**Step 3: Commit**

```bash
git add web/src/app/(app)/ipr/components/tab-*.tsx
git commit -m "refactor(frontend): migrate 11 IPR tabs to EmptyState component"
```

---

### Task 10: Migrate ConfirmDialog — IPR tabs with delete

**Files:**
- Modify: `web/src/app/(app)/ipr/components/tab-partes.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-territorio.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-parentesco.tsx`
- Modify: `web/src/app/(app)/ipr/components/tab-admisibilidad.tsx`

**Step 1: For each tab, add confirm dialog state and component**

Pattern (tab-partes.tsx example):
```tsx
// Add state:
const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
const [deleteLoading, setDeleteLoading] = useState(false);

// Change delete button onClick:
// BEFORE: onClick={() => handleDeleteParty(p.id)}
// AFTER:  onClick={() => setDeleteTarget(p.id)}

// Modify handleDeleteParty to close dialog after:
const handleDeleteParty = async () => {
  if (!deleteTarget) return;
  setDeleteLoading(true);
  try {
    await api.delete(`/api/ipr/${iprId}/partes/${deleteTarget}`);
    toast.success("Parte eliminada");
    fetchPartes();
  } catch (err) {
    toast.error(err instanceof Error ? err.message : "Error al eliminar");
  } finally {
    setDeleteLoading(false);
    setDeleteTarget(null);
  }
};

// Add at bottom of component JSX:
<ConfirmDialog
  open={deleteTarget !== null}
  onOpenChange={(open) => { if (!open) setDeleteTarget(null); }}
  title="Eliminar parte"
  description="¿Está seguro de que desea eliminar esta parte? Esta acción no se puede deshacer."
  onConfirm={handleDeleteParty}
  loading={deleteLoading}
/>
```

Repeat same pattern for tab-territorio, tab-parentesco, tab-admisibilidad with appropriate title/description.

**Step 2: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/app/(app)/ipr/components/tab-partes.tsx web/src/app/(app)/ipr/components/tab-territorio.tsx web/src/app/(app)/ipr/components/tab-parentesco.tsx web/src/app/(app)/ipr/components/tab-admisibilidad.tsx
git commit -m "feat(ux): add ConfirmDialog to 4 IPR tabs with delete actions"
```

---

### Task 11: Final verification + restart

**Step 1: Full build**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build`

Expected: All 36 routes compile, 0 errors

**Step 2: Restart web container**

Run: `cd /Users/felixsanhueza/Developer/goreos && docker compose restart web`

**Step 3: Visual smoke test**

Navigate to: `/compromisos`, `/convenios`, `/ipr`, `/admin/usuarios`, `/ipr/{id}` (check tabs).
Verify: headers render correctly, empty states show, delete triggers confirm dialog.
