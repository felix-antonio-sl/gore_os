# In-App Bug Capture System for Manual Testing

**Version**: 1.0 | **Status**: Implemented | **Reference**: GORE_OS (C60)

---

## Problem

Manual testing requires testers to report bugs with enough context to reproduce them. In practice:

- Testers forget to note which user/role they were logged in as
- The exact URL, query params, and viewport are lost
- Screenshots end up in Slack threads disconnected from the report
- The friction of switching to an external tool (Jira, Linear, GitHub Issues) means many bugs go unreported
- Testing progress across multiple roles/users is hard to track

## Solution

A floating action button (FAB) embedded in the application that captures bugs **in context** — the system auto-populates user, role, URL, viewport, and active test item. The tester only provides title and severity. Screenshots via clipboard paste or file upload. All data persists to JSON files on a mounted volume.

## Design Principles

1. **Zero-friction capture**: Tester writes title + severity. Everything else is automatic.
2. **Context over description**: Auto-captured metadata (user, role, URL, viewport, checklist item) is more reliable than human-written reproduction steps.
3. **No external dependencies**: No database tables, no third-party services, no API keys. JSON files on disk.
4. **Dev-only by construction**: Double-gated — frontend flag + backend environment check. Cannot leak to production.
5. **Ephemeral by design**: Test data, not business data. `cat`, `rm`, `docker cp` are the management tools.

## Architecture

```
┌─ Browser ──────────────────────────────────────────────┐
│                                                        │
│  localStorage                                          │
│  ├── {app}_dev_mode = "true"   (gate)                  │
│  ├── {app}_token = JWT         (auth context)          │
│  └── active_checklist_item     (testing context)       │
│                                                        │
│  ┌─ FAB (fixed, bottom-right, z-50) ────────────────┐  │
│  │  Visible IFF dev_mode === "true"                  │  │
│  │  Click → Drawer with form:                        │  │
│  │    [auto] user, role, URL, viewport, check item   │  │
│  │    [manual] title*, severity*, description         │  │
│  │    [optional] screenshot (paste ⌘V / file upload) │  │
│  └──────────────────────┬───────────────────────────┘  │
│                         │ POST /api/dev/bugs           │
└─────────────────────────┼──────────────────────────────┘
                          │
┌─ Backend ───────────────▼──────────────────────────────┐
│                                                        │
│  Gate: ENV ≠ "development" → 403 on ALL /dev/* routes  │
│                                                        │
│  POST /dev/bugs     → append to JSON, return UUID      │
│  GET  /dev/bugs     → read JSON array                  │
│  DELETE /dev/bugs/id → filter from JSON                │
│                                                        │
│  POST /dev/checklist → save per-user checklist state   │
│  GET  /dev/checklist → read per-user checklist state   │
│                                                        │
│  Storage: ./dev-data/ (mounted volume)                 │
│  ├── test-bugs.json                                    │
│  └── test-checklist-state.json                         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Data Model

### BugReport

```
id              UUID        auto-generated
created_at      ISO 8601    auto-generated (UTC)

title           string      required, manual
severity        enum        required, manual (CRITICO|ALTO|MEDIO|BAJO)
description     string?     optional, manual

user_email      string      auto: from auth context
role_code       string      auto: from auth context
population      string?     auto: from auth context (if app has populations)
division_id     string?     auto: from auth context (if app has org units)
url             string      auto: window.location.pathname + search
viewport        string?     auto: window.innerWidth x innerHeight
checklist_item  string?     auto: from localStorage (active test item)
screenshot      string?     manual: base64 data URL (paste or upload)
```

### ChecklistState

```json
{
  "user_a@app.cl": {
    "item_key_1": true,
    "item_key_2": false
  },
  "user_b@app.cl": {
    "item_key_1": true
  }
}
```

## Components

### C1 — FAB + Drawer (frontend)

**Behavior:**
- Renders only when `{app}_dev_mode === "true"` in localStorage
- Fixed position `bottom: 1rem, right: 1rem`, z-index 50
- Icon: bug emoji or bug icon, attention color (amber recommended)
- Click opens drawer/panel with form

**Form fields:**
- Title (text input, required)
- Severity (4 toggle buttons with color coding):
  - CRITICO: red
  - ALTO: amber
  - MEDIO: blue
  - BAJO: green
- Description (textarea, optional)
- Screenshot zone (dashed border, accepts paste + file input)
- Context summary (read-only muted box showing auto-captured fields)
- Submit button (disabled until title provided, shows loading state)

**Screenshot capture:**
- Clipboard paste: global `paste` event listener while drawer is open, filters `image/*` from `clipboardData.items`, converts via `FileReader.readAsDataURL()`
- File upload: `<input type="file" accept="image/*">`, same FileReader path
- Preview: thumbnail with delete (X) button
- Storage: complete `data:image/...;base64,...` string in JSON

**On submit:**
- POST to `/api/dev/bugs` with all fields
- Show success toast
- Close drawer
- Reset form

### C2 — SSR Wrapper (frontend, framework-dependent)

For SSR frameworks (Next.js, Nuxt, SvelteKit): a dynamic import wrapper with SSR disabled.

```
Component = dynamic(() => import("./bug-report-fab"), { ssr: false })
```

**Why:** The FAB reads localStorage on mount. Server-side rendering has no localStorage. Without the wrapper, hydration mismatch or crash.

### C3 — Backend Router

**5 endpoints, single file, ~90 lines.**

Security gate function: check environment variable, return 403 if not development. Applied to all endpoints.

**POST /dev/bugs:**
1. Load existing array from JSON (or `[]` if file missing)
2. Add `id` (UUID) and `created_at` (UTC ISO)
3. Append to array
4. Write JSON (pretty-printed, UTF-8, ensure_ascii=false)
5. Return `{ id, ok: true }`

**GET /dev/bugs:**
1. Read JSON file (or return `[]`)
2. Return array

**DELETE /dev/bugs/{id}:**
1. Load array
2. Filter out matching id
3. Write back
4. Return `{ ok: true }`

**POST /dev/checklist:**
1. Receive `{ state: { user_email: { item_key: bool } } }`
2. Write to checklist JSON
3. Return `{ ok: true }`

**GET /dev/checklist:**
1. Read checklist JSON (or `{}`)
2. Return dict

### C4 — Dev Login Page (optional but recommended)

A page at `/dev` that shows all test users as clickable cards, grouped by archetype/role type.

**On click:**
1. Call login endpoint with hardcoded test password
2. Store auth token
3. Set `{app}_dev_mode = "true"` in localStorage
4. Redirect to main page

**Key behavior:** Normal login (via `/login`) MUST clear `{app}_dev_mode` from localStorage. This prevents dev mode from persisting after a regular login flow.

### C5 — Testing Dashboard (optional)

A page at `/dev/testing` with two tabs:

**Tab 1 — Checklist:**
- Role-specific test items defined as static config
- Checkboxes that persist to `/api/dev/checklist`
- Per-user state (multiple testers work in parallel)
- Progress bar (% checked)
- On check: stores item label in localStorage as `active_checklist_item`

**Tab 2 — Bugs:**
- KPI strip: count by severity
- Expandable cards sorted by newest first
- Each card shows: title, user, URL, severity badge, relative time
- Expand reveals: description, screenshot, checklist item, role, viewport
- Delete button per bug
- Export JSON button (downloads file)

## Security Model

```
Gate 1 (frontend):  localStorage flag absent → FAB never renders
Gate 2 (backend):   ENV ≠ "development"     → 403 on all /dev/* endpoints
Gate 3 (lifecycle): Normal login             → clears dev_mode flag
```

No endpoint in `/dev/*` is reachable in production. The FAB component is physically present in the bundle but never mounts (the `useEffect` check returns early). For apps that tree-shake aggressively, the SSR wrapper with `ssr: false` ensures the component is a separate chunk only loaded client-side.

## Storage

**Format:** JSON, pretty-printed (indent 2), UTF-8 with native characters.

**Location:** A `dev-data/` directory inside the backend working directory, mapped to host via volume mount.

```yaml
# docker-compose.yml (example)
services:
  api:
    volumes:
      - ./api:/app    # dev-data/ lives inside ./api/
```

**Why JSON, not database:**
- Zero schema management — no migrations, no tables, no cleanup jobs
- Human-readable — `cat dev-data/test-bugs.json | jq .`
- Portable — `docker cp container:/app/dev-data/ .` extracts everything
- Disposable — `rm dev-data/test-bugs.json` resets the state
- No connection pool overhead for ephemeral dev data

**Tradeoffs accepted:**
- No concurrent write safety (acceptable for dev testing — low write volume)
- Screenshots as base64 inflate file size ~33% (acceptable for dev — no CDN needed)
- No indexing/search (acceptable — linear scan over dozens, not thousands)

## Checklist Item ↔ Bug Context Bridge

The key integration between testing checklist and bug capture:

```
1. Tester checks item "IPR detail shows 18 tabs"
   → localStorage: active_checklist_item = "IPR detail shows 18 tabs"

2. Tester navigates to IPR detail, sees only 16 tabs

3. Tester clicks FAB, writes "Missing 2 tabs in IPR detail"
   → Bug auto-includes: checklist_item = "IPR detail shows 18 tabs"

4. Reviewer sees the bug and knows EXACTLY what was being tested
```

This eliminates the "what were you trying to do?" back-and-forth that plagues bug reports.

## Implementation Checklist

| # | Item | Files | Effort |
|---|------|-------|--------|
| 1 | Backend router with 5 endpoints + env gate | 1 | ~90 lines |
| 2 | FAB component with drawer form + auto-context | 1 | ~230 lines |
| 3 | SSR wrapper (if using SSR framework) | 1 | ~10 lines |
| 4 | Mount in app layout | 1 edit | ~2 lines |
| 5 | Dev login page with test user cards | 1 | ~225 lines |
| 6 | Clear dev_mode flag on normal login | 1 edit | ~1 line |
| 7 | Testing dashboard with checklist + bug viewer | 1 | ~690 lines |
| 8 | Volume mount in docker-compose | 1 edit | ~1 line |
| **Total** | | **6 new + 3 edits** | **~1,250 lines** |

## Adaptation Points

When porting to another project, these are the only things that change:

| Aspect | What to adapt |
|--------|---------------|
| Auth context fields | Replace `user_email`, `role_code`, `population`, `division_id` with your app's auth shape |
| Dev mode flag name | Replace `goreos_dev_mode` with `{yourapp}_dev_mode` |
| Test users | Replace user catalog in dev login page |
| Checklist items | Define role-specific test items for your domain |
| Severity levels | Keep as-is or rename (the 4-level scale is standard) |
| Backend framework | Translate 5 endpoints to Express/Django/Rails/etc. (~30 min) |
| Styling | Adapt to your design system (the FAB is self-contained) |
