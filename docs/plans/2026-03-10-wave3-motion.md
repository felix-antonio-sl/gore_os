# Wave 3 Motion — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add subtle institutional fade-in animations to 5 key UI surfaces using existing tw-animate-css classes.

**Architecture:** CSS-only approach — add Tailwind animation utility classes (`animate-in`, `fade-in`, `duration-*`, `delay-*`, `fill-mode-both`) to existing components. No new dependencies. Accessible via `prefers-reduced-motion`.

**Tech Stack:** tw-animate-css 1.4.0 (already installed), TailwindCSS v4.

---

### Task 1: Add reduced-motion base rule

**Files:**
- Modify: `web/src/app/globals.css`

**Step 1: Add the rule inside the existing `@layer base` block**

In `web/src/app/globals.css`, find the `@layer base` block (currently contains `*`, `body`, `h1, h2` rules). Add a `@media` rule at the end:

```css
@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
  h1, h2 {
    font-family: var(--font-serif), ui-serif, serif;
  }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
}
```

**Step 2: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/app/globals.css
git commit -m "feat(a11y): add prefers-reduced-motion rule to disable animations"
```

---

### Task 2: PageHeader fade-in

**Files:**
- Modify: `web/src/components/page-header.tsx`

**Step 1: Add animation class to the wrapper div**

Change line 11 from:
```tsx
    <div className="flex items-center justify-between">
```
to:
```tsx
    <div className="flex items-center justify-between animate-in fade-in duration-300">
```

That's the only change. The `animate-in` class triggers the enter keyframe from tw-animate-css. `fade-in` sets `--tw-enter-opacity: 0` so it fades from transparent. `duration-300` sets 300ms.

**Step 2: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/components/page-header.tsx
git commit -m "feat(motion): add fade-in to PageHeader component"
```

---

### Task 3: Dashboard KPI cards staggered fade

**Files:**
- Modify: `web/src/app/(app)/dashboard/page.tsx`

**Step 1: Find the KPI grid (around line 200)**

The KPI cards are rendered in a `.map()` inside a grid div. The current code is:
```tsx
<div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
  {data?.kpis.map((kpi, i) => (
    <KpiCard
      key={i}
      ...
    />
  ))}
</div>
```

**Step 2: Wrap each KpiCard in an animated div with staggered delay**

Replace the KPI grid block (the non-loading branch, NOT the skeleton branch) with:
```tsx
<div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
  {data?.kpis.map((kpi, i) => (
    <div key={i} className={`animate-in fade-in duration-300 fill-mode-both ${
      i === 0 ? "" : i === 1 ? "delay-75" : i === 2 ? "delay-150" : "delay-200"
    }`}>
      <KpiCard
        label={kpi.label}
        value={kpi.value}
        sublabel={kpi.sublabel}
        color={kpi.color}
        onClick={DRILLDOWNS[kpi.label] ? () => router.push(DRILLDOWNS[kpi.label]) : undefined}
      />
    </div>
  ))}
</div>
```

Key details:
- `fill-mode-both` keeps opacity at 0 before the animation starts (otherwise delayed items flash visible then animate)
- Delays: 0ms, 75ms, 150ms, 200ms for cards 0-3
- Cards beyond index 3 get `delay-200` (same as last)
- Do NOT touch the skeleton/loading branch — it keeps `animate-pulse`

**Step 3: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 4: Commit**

```bash
git add web/src/app/(app)/dashboard/page.tsx
git commit -m "feat(motion): add staggered fade-in to dashboard KPI cards"
```

---

### Task 4: DataTable fade-in on data load

**Files:**
- Modify: `web/src/components/data-table.tsx`

**Step 1: Add animation to the table container**

Find the return after the loading check (line 57-58). The current code:
```tsx
  return (
    <div className="space-y-2">
```

Change to:
```tsx
  return (
    <div className="space-y-2 animate-in fade-in duration-200">
```

This makes the entire table (header + body + pagination) fade in when data loads. The skeleton (loading branch above) is unaffected.

**Step 2: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/components/data-table.tsx
git commit -m "feat(motion): add fade-in to DataTable on data load"
```

---

### Task 5: Login page sequential fade-in

**Files:**
- Modify: `web/src/app/login/page.tsx`

**Step 1: Add animation to the brand section**

Find the brand div (the one with `className="flex flex-col items-center mb-8"`). Add animation classes:

```tsx
<div className="flex flex-col items-center mb-8 animate-in fade-in duration-300 fill-mode-both">
```

**Step 2: Add animation to the login card**

Find the glass card div (the one with `className="rounded-xl bg-white/[0.07] backdrop-blur-xl ..."`). Add animation classes with delay:

```tsx
<div className="rounded-xl bg-white/[0.07] backdrop-blur-xl border border-white/[0.12] shadow-2xl p-6 animate-in fade-in duration-300 delay-150 fill-mode-both">
```

**Step 3: Add animation to the footer**

Find the footer `<p>` tag (the one with `className="relative z-10 mt-8 ..."`). Add animation classes:

```tsx
<p className="relative z-10 mt-8 text-xs text-white/40 animate-in fade-in duration-300 delay-300 fill-mode-both">
```

**Step 4: Build to verify**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build 2>&1 | tail -5`

Expected: Build succeeds

**Step 5: Commit**

```bash
git add web/src/app/login/page.tsx
git commit -m "feat(motion): add sequential fade-in to login page"
```

---

### Task 6: Final verification + restart

**Step 1: Full build**

Run: `cd /Users/felixsanhueza/Developer/goreos/web && npx next build`

Expected: All 36 routes compile, 0 errors

**Step 2: Restart web container**

Run: `cd /Users/felixsanhueza/Developer/goreos && docker compose restart web`

**Step 3: Visual smoke test**

Navigate to:
- `/login` — brand fades in, card fades in 150ms later, footer 300ms later
- `/dashboard` — KPI cards stagger in
- `/compromisos` — PageHeader fades in, table fades in when data loads
