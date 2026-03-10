# Wave 5A Quick Wins — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close 7 MEDIO/BAJO UX findings (~4.5h) to raise audit closure from 67% → 80%.

**Architecture:** All frontend-only changes. No backend modifications. No new endpoints.

**Tech Stack:** Next.js, TypeScript, shadcn/ui, TailwindCSS v4.

---

### Task 1: UX-038 — Remove redundant gauges from cockpit Jefe DGI

**Files:**
- Modify: `web/src/components/cockpit-jefe-dgi.tsx`

Remove lines 72-82 (the `{/* Gauge visual row */}` div with SemaforoGauge map). SemaforoCard grid above already displays the same information. Also remove the `SemaforoGauge` import (line 10) if it becomes unused.

### Task 2: UX-054 — Convenio vigencia multi-threshold alerts

**Files:**
- Modify: `web/src/app/(app)/convenios/page.tsx`

In the drawer detail section (around line 574), expand the `< 30` threshold to show amber warning at 60d and yellow at 90d:

```tsx
<span className={
  detail.days_to_expiry !== null && detail.days_to_expiry < 30 ? "text-red-600 font-medium" :
  detail.days_to_expiry !== null && detail.days_to_expiry < 60 ? "text-amber-600 font-medium" :
  detail.days_to_expiry !== null && detail.days_to_expiry < 90 ? "text-yellow-700" : ""
}>
```

Add an alert banner above the vigencia row when < 90d and >= 0:

```tsx
{detail.days_to_expiry !== null && detail.days_to_expiry >= 0 && detail.days_to_expiry < 90 && (
  <div className={cn(
    "px-3 py-2 rounded-md text-xs border mb-2",
    detail.days_to_expiry < 30 ? "bg-red-50 border-red-200 text-red-800" :
    detail.days_to_expiry < 60 ? "bg-amber-50 border-amber-200 text-amber-800" :
    "bg-yellow-50 border-yellow-200 text-yellow-800"
  )}>
    Vigencia vence en {detail.days_to_expiry} día{detail.days_to_expiry !== 1 ? "s" : ""}
  </div>
)}
```

### Task 3: UX-037 — Contextual empty state in Mis Compromisos

**Files:**
- Modify: `web/src/app/(app)/mis-compromisos/page.tsx`

The `EmptyState compact` ignores `description` prop (compact renders only title as plain text). Change to use normal mode with icon context:

```tsx
{filtered.length === 0 ? (
  <div className="py-4">
    <EmptyState
      title="Sin compromisos en esta categoría"
      description="Todos tus compromisos están al día."
      icon={<CheckCircle2 className="size-10 stroke-1 text-green-500" />}
    />
  </div>
) : (
```

Import `CheckCircle2` from `lucide-react`.

### Task 4: UX-021 — Password confirmation + strength indicator

**Files:**
- Modify: `web/src/components/header.tsx`

1. Add `confirm` to pwd form state: `{ current: "", next: "", confirm: "" }`
2. Add strength computation:
```tsx
const pwdStrength = pwdForm.next.length === 0 ? null :
  pwdForm.next.length < 8 ? "débil" :
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(pwdForm.next) ? "fuerte" : "media";
```
3. Add confirmation validation in handleChangePassword:
```tsx
if (pwdForm.next !== pwdForm.confirm) {
  setPwdError("Las contraseñas no coinciden");
  return;
}
```
4. Add confirmation Input field after "Nueva contraseña":
```tsx
<div className="grid gap-1.5">
  <label htmlFor="confirm-pwd" className="text-sm font-medium">Confirmar contraseña</label>
  <Input id="confirm-pwd" type="password" value={pwdForm.confirm}
    onChange={(e) => setPwdForm((f) => ({ ...f, confirm: e.target.value }))} />
</div>
```
5. Add strength indicator after new password Input:
```tsx
{pwdStrength && (
  <div className="flex items-center gap-2">
    <div className="flex gap-1 flex-1">
      <div className={cn("h-1 flex-1 rounded-full", pwdStrength === "débil" ? "bg-red-400" : "bg-green-400")} />
      <div className={cn("h-1 flex-1 rounded-full", pwdStrength === "fuerte" ? "bg-green-400" : pwdStrength === "media" ? "bg-amber-400" : "bg-gray-200")} />
      <div className={cn("h-1 flex-1 rounded-full", pwdStrength === "fuerte" ? "bg-green-400" : "bg-gray-200")} />
    </div>
    <span className={cn("text-xs", pwdStrength === "débil" ? "text-red-600" : pwdStrength === "media" ? "text-amber-600" : "text-green-600")}>
      {pwdStrength === "débil" ? "Débil" : pwdStrength === "media" ? "Media" : "Fuerte"}
    </span>
  </div>
)}
```
6. Update onOpenChange to reset confirm: `setPwdForm({ current: "", next: "", confirm: "" })`
7. Update disabled condition to include confirm: `disabled={pwdLoading || !pwdForm.current || !pwdForm.next || !pwdForm.confirm}`

### Task 5: UX-032 — Division breakdown sort in dashboard

**Files:**
- Modify: `web/src/app/(app)/dashboard/page.tsx`

1. Add sort state: `const [divSort, setDivSort] = useState<"vencidos" | "ejecucion" | "name">("vencidos");`
2. Compute sorted array before render:
```tsx
const sortedDivisions = (data?.divisions ?? []).slice().sort((a, b) => {
  if (divSort === "vencidos") return b.vencidos - a.vencidos;
  if (divSort === "ejecucion") return b.ejecucion_pct - a.ejecucion_pct;
  return a.division_name.localeCompare(b.division_name);
});
```
3. Add sort buttons in CardHeader:
```tsx
<CardHeader className="flex-row items-center justify-between">
  <CardTitle className="text-lg">Desglose por División</CardTitle>
  <div className="flex gap-1">
    {([["vencidos", "Vencidos"], ["ejecucion", "Ejecución"], ["name", "Nombre"]] as const).map(([key, label]) => (
      <Button key={key} size="sm" variant={divSort === key ? "default" : "ghost"} className="h-7 text-xs"
        onClick={() => setDivSort(key)}>{label}</Button>
    ))}
  </div>
</CardHeader>
```
4. Replace `data.divisions.map` with `sortedDivisions.map`.

### Task 6: UX-042 — "Investigar" button navigates to datos

**Files:**
- Modify: `web/src/components/cockpit-control-gestion.tsx`

Add router import if missing. Add `onClick` to the Investigar button (line 140):

```tsx
<Button size="sm" variant="outline" className="h-7 text-xs"
  onClick={() => router.push(`/datos?indicator_id=${ind.id}`)}>
  Investigar
</Button>
```

Ensure `useRouter` is imported and instantiated. Check if `router` already exists in the component.

### Task 7: UX-045 — KB stats clickeable in cockpit TD

**Files:**
- Modify: `web/src/components/cockpit-td.tsx`

Make each stat box clickable with cursor-pointer + hover effect. Add router navigation:

```tsx
<div className="rounded-lg border bg-amber-50 border-amber-200 py-3 cursor-pointer hover:shadow-md transition-shadow"
  role="button" tabIndex={0}
  onClick={() => router.push("/datos?tab=kb&status=pending")}
  onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); router.push("/datos?tab=kb&status=pending"); } }}>
```

Same pattern for Actualizados (sort=recent) and Total (no filter). Ensure `useRouter` is imported.

---

### Task 8: Build verify + commit

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build`
