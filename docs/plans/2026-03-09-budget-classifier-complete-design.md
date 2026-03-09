# Complete Budget Classifier Level 5 (Programa) — Design

**Date**: 2026-03-09
**Status**: Approved

## Goal

Complete the budget classifier by adding `program_code_id` field to the create form and filter dropdown to the list page. All backend infrastructure already exists.

## Context

Level 5 (Programa / `budget_program_code`) has: DDL migration with FK, admin CRUD (3 endpoints), API list filter, TypeScript types. Missing: form field in `/presupuesto/nuevo`, filter dropdown in `/presupuesto/page.tsx`.

## Changes

1. **Form** (`/presupuesto/nuevo/page.tsx`): Add optional select for `program_code_id`, load options from `GET /api/admin/budget-program-codes`
2. **List** (`/presupuesto/page.tsx`): Add filter dropdown for `program_code` alongside existing filters
3. **Docs**: Update CLAUDE.md Rule 43 to "6-level complete"

No backend changes. No DDL. No seed data. No new tests.
