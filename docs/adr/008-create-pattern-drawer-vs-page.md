# ADR-008: Create Pattern — Drawer vs /nuevo Page

**Status**: Accepted
**Date**: 2026-03-11
**Decision**: Standardize when to use DrawerPanel vs full create page (/nuevo)

## Context

GORE_OS has two creation patterns that emerged organically:
1. **DrawerPanel** (Sheet wrapper) — slide-in panel for inline creation
2. **/nuevo page** — full-page form with navigation

During Wave B-E, 5 pages used raw `<Sheet>` instead of `<DrawerPanel>`, creating inconsistency.

## Decision

### Use DrawerPanel when:
- Entity is a **satellite** of a parent (e.g., compromisos inside IPR tab, topics inside session)
- Form has **<5 fields** and simple validation
- User should **stay on current page** after creation

### Use /nuevo page when:
- Entity is a **root object** (IPR, convenio, acto administrativo, reunión)
- Form has **>5 fields** with complex validation or catalog lookups
- User will **navigate to the new entity** after creation

### Implementation
- All drawers must use `<DrawerPanel>` component (not raw Sheet)
- DrawerPanel API: `open`, `onClose`, `title`, `children`

## Consequences
- Consistent UX across all creation flows
- Single component to maintain for drawer behavior (ScrollArea, close button, overlay)
- New features follow the criteria above to choose pattern
