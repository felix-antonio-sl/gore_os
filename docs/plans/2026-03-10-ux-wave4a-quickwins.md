# Wave 4A Quick Wins — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close 8 UX quick wins (CSS/a11y) to raise audit closure from 45% → 60%.

**Architecture:** Minimal edits — 1-5 lines per file. No new components, no new endpoints. Uses existing shadcn Tooltip (`ui/tooltip.tsx`).

**Tech Stack:** TailwindCSS v4, shadcn/ui Tooltip, React.

---

### Task 1: UX-013 + UX-016 — Login hardcoded color + email validation

**Files:**
- Modify: `web/src/app/login/page.tsx`

**Step 1: Fix hardcoded color (UX-013)**

Line 103 currently has:
```tsx
className="w-full bg-white text-[#031B5F] hover:bg-white/90 font-semibold"
```

Change to:
```tsx
className="w-full bg-white text-slate-900 hover:bg-white/90 font-semibold"
```

Note: `text-slate-900` (#0f172a) is visually close to #031B5F and uses a Tailwind token instead of a hardcoded hex.

**Step 2: Add email validation (UX-016)**

In the `handleSubmit` function, after `setError(null);` (line 18), add:
```tsx
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Ingrese un correo electrónico válido");
      setIsLoading(false);
      return;
    }
```

Wait — `setIsLoading(true)` is on line 19, after `setError(null)`. So insert the regex check AFTER line 19 (`setIsLoading(true)`):

Actually, better to add it BEFORE `setIsLoading(true)` to avoid the loading flash:

After line 18 (`setError(null);`) and BEFORE line 19 (`setIsLoading(true);`), insert:
```tsx
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Ingrese un correo electrónico válido");
      return;
    }
```

**Step 3: Build verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

**Step 4: Commit**

```bash
git add web/src/app/login/page.tsx
git commit -m "fix(ux): UX-013 replace hardcoded color + UX-016 add email validation in login"
```

---

### Task 2: UX-015 — Tooltip on cockpit TD abbreviations

**Files:**
- Modify: `web/src/components/cockpit-td.tsx`

**Step 1: Add Tooltip imports**

Add at the top after existing imports:
```tsx
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
```

**Step 2: Add full status names to the badge map**

Change the `decreeBadge` record (lines 16-20) to include the full label:
```tsx
const decreeBadge: Record<string, { label: string; fullLabel: string; className: string }> = {
  VIGENTE: { label: "VIG", fullLabel: "Vigente", className: "bg-green-100 text-green-700 border-green-300" },
  PARCIAL: { label: "PAR", fullLabel: "Parcial", className: "bg-amber-100 text-amber-700 border-amber-300" },
  PENDIENTE: { label: "PEN", fullLabel: "Pendiente", className: "bg-red-100 text-red-700 border-red-300" },
};
```

**Step 3: Wrap the Badge in a Tooltip**

Around lines 106-115, the decree badge rendering. Replace:
```tsx
                      <Badge
                        variant="outline"
                        className={cn(
                          "text-[10px] px-1.5 py-0 w-10 justify-center shrink-0 border font-bold",
                          badgeConfig.className
                        )}
                      >
                        {badgeConfig.label}
                      </Badge>
```

With:
```tsx
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Badge
                            variant="outline"
                            className={cn(
                              "text-[10px] px-1.5 py-0 w-10 justify-center shrink-0 border font-bold",
                              badgeConfig.className
                            )}
                          >
                            {badgeConfig.label}
                          </Badge>
                        </TooltipTrigger>
                        <TooltipContent>{badgeConfig.fullLabel ?? badgeConfig.label}</TooltipContent>
                      </Tooltip>
```

**Step 4: Wrap the component return in TooltipProvider**

In the return statement (line 25), wrap the outermost `<div>` with `<TooltipProvider>`:
```tsx
  return (
    <TooltipProvider>
      <div className="space-y-6">
        ...
      </div>
    </TooltipProvider>
  );
```

**Step 5: Build verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

**Step 6: Commit**

```bash
git add web/src/components/cockpit-td.tsx
git commit -m "fix(ux): UX-015 add tooltips to decree abbreviations in cockpit TD"
```

---

### Task 3: UX-025 — Alert popover keyboard accessibility

**Files:**
- Modify: `web/src/components/header.tsx`

**Step 1: Make alert items keyboard accessible**

Find the alert item divs (lines 202-217). The current div:
```tsx
                  <div
                    key={alert.id}
                    className="flex items-start gap-2 px-3 py-2 border-b last:border-0 hover:bg-muted/50"
                  >
```

Change to:
```tsx
                  <div
                    key={alert.id}
                    role="button"
                    tabIndex={0}
                    className="flex items-start gap-2 px-3 py-2 border-b last:border-0 hover:bg-muted/50 cursor-pointer focus:outline-none focus:bg-muted/50"
                    onClick={() => { setBellOpen(false); window.location.href = "/alertas"; }}
                    onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setBellOpen(false); window.location.href = "/alertas"; } }}
                  >
```

**Step 2: Build verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add web/src/components/header.tsx
git commit -m "fix(a11y): UX-025 make alert popover items keyboard accessible"
```

---

### Task 4: UX-031 — Reset password min length validation

**Files:**
- Modify: `web/src/app/(app)/admin/usuarios/page.tsx`

**Step 1: Add validation to reset password button and helper text**

Find the reset password form (lines 447-463). Change:
```tsx
                    <Button size="sm" onClick={handleResetPassword} disabled={!newPassword}>
                      Cambiar
                    </Button>
```

To:
```tsx
                    <p className="text-xs text-muted-foreground">Mínimo 8 caracteres</p>
                    <Button size="sm" onClick={handleResetPassword} disabled={!newPassword || newPassword.length < 8}>
                      Cambiar
                    </Button>
```

**Step 2: Build verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add web/src/app/(app)/admin/usuarios/page.tsx
git commit -m "fix(ux): UX-031 add min length validation to admin reset password"
```

---

### Task 5: UX-040 + UX-041 — Sparkline mobile + gray badge contrast

**Files:**
- Modify: `web/src/components/cockpit-control-gestion.tsx`

**Step 1: Hide sparklines on mobile (UX-040)**

Find the SparklineIndicator usage (line 133):
```tsx
                        <SparklineIndicator indicatorId={ind.id} days={90} />
```

Change to:
```tsx
                        <span className="hidden md:inline-block">
                          <SparklineIndicator indicatorId={ind.id} days={90} />
                        </span>
```

**Step 2: Fix gray badge contrast (UX-041)**

Find the SIN_DATOS config (line 39):
```tsx
    badgeClass: "bg-gray-100 text-gray-600 border-gray-300",
```

Change to:
```tsx
    badgeClass: "bg-gray-100 text-gray-800 border-gray-300",
```

Also fix the BAJA priority badge (line 47):
```tsx
  BAJA: "bg-gray-100 text-gray-600 border-gray-300",
```

Change to:
```tsx
  BAJA: "bg-gray-100 text-gray-800 border-gray-300",
```

**Step 3: Build verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

**Step 4: Commit**

```bash
git add web/src/components/cockpit-control-gestion.tsx
git commit -m "fix(a11y): UX-040 hide sparklines on mobile + UX-041 improve gray badge contrast"
```

---

### Task 6: UX-048 — Execution formula tooltip

**Files:**
- Modify: `web/src/app/(app)/presupuesto/page.tsx`

**Step 1: Add Tooltip imports**

Add at the top with existing imports:
```tsx
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
```

**Step 2: Wrap the ExecutionBar percentage in a Tooltip**

In the `ExecutionBar` component (lines 49-60), change:
```tsx
      <span className={`text-xs font-mono font-medium tabular-nums ${textColor}`}>{pct}%</span>
```

To:
```tsx
      <Tooltip>
        <TooltipTrigger asChild>
          <span className={`text-xs font-mono font-medium tabular-nums ${textColor} cursor-help`}>{pct}%</span>
        </TooltipTrigger>
        <TooltipContent>Ejecución = Comprometido / Vigente × 100</TooltipContent>
      </Tooltip>
```

**Step 3: Wrap the component or the page in TooltipProvider**

Wrap the return of `PresupuestoPage` in `<TooltipProvider>`:
The outermost `<div>` inside the return should be wrapped.

**Step 4: Build verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

**Step 5: Commit**

```bash
git add web/src/app/(app)/presupuesto/page.tsx
git commit -m "fix(ux): UX-048 add tooltip explaining execution formula in presupuesto"
```

---

### Task 7: Final build + restart

**Step 1: Full build**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build`

Expected: All routes compile, 0 errors.

**Step 2: Restart web container**

Run: `cd /Users/felixsanhueza/Developer/goreos && docker compose restart web`
