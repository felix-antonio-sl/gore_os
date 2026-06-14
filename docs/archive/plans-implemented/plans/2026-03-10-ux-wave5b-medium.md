# Wave 5B — Medium Functionality Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close 6 MEDIO UX findings to raise audit closure from 80% → 91%.

**Architecture:** All frontend-only. No backend changes. No new endpoints.

**Tech Stack:** Next.js, TypeScript, shadcn/ui, TailwindCSS v4.

---

### Task 1: UX-027 — Cartera table responsive columns

Hide low-priority columns on mobile. Add horizontal scroll indicator.

### Task 2: UX-033 — SemaforoCard drill-down for all dimensions

Add onClick handlers to 4 remaining dimensions.

### Task 3: UX-039 — Escalar/Playbook buttons functional

Remove disabled, add navigation to /alertas for Escalar, tooltip for Playbook.

### Task 4: UX-044 — WIP limit visual indicator + 409 handling

Show WIP capacity badge (e.g., "3/5") and handle HTTP 409 with toast.

### Task 5: UX-052 — Rendiciones vencidas card in cockpit

Add overdue renditions count + link to /rendiciones.

### Task 6: UX-055 — IPR tabs auto-refresh via refreshKey

Pass incrementing key from parent to trigger tab re-fetch after drawer closes.
