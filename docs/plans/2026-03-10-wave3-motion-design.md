# Wave 3 — Motion Design (Sutil/Institucional)

**Date**: 2026-03-10
**Approach**: CSS-only with tw-animate-css (already installed), zero new dependencies

## Principles

- Fade-in only (opacity 0→1), no translate or scale
- 200-300ms duration, ease-out
- `prefers-reduced-motion: reduce` disables all animations
- Declarative Tailwind classes, no JS animation logic

## Animations

### 1. Reduced-motion base rule (globals.css)

Accessible fallback that disables all animations for users who prefer reduced motion.

### 2. PageHeader fade-in

`animate-in fade-in duration-300` on the wrapper div. Runs once on page mount.

### 3. Dashboard KPI cards — staggered fade

4-6 cards with incremental delays (0ms, 75ms, 150ms, 200ms). Uses `delay-*` utility classes plus `fill-mode-both` to hold initial opacity at 0 before animation starts.

### 4. DataTable fade-in

Subtle `animate-in fade-in duration-200` on the table container (not individual rows). Applied when data loads (transition from skeleton to content).

### 5. Login page — sequential fade

Three groups with staggered entry:
- Brand (logo + title): immediate
- Form card: 150ms delay
- Footer: 300ms delay

### 6. No-touch zones

- Sidebar navigation: persistent, no animation
- DrawerPanel/Sheet: already animated by Radix
- Skeletons: already use animate-pulse

## Impact

5 files edited, ~15 lines added, 0 new dependencies, 0 KB bundle increase.
