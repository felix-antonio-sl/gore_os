# Bug Capturer — Design Spec

**Date**: 2026-03-22
**Status**: Approved
**Context**: Dev/testing tooling for GORE_OS. Accelerates manual testing by letting testers capture bugs inline without leaving the app. Integrates with existing `/dev` quick login and `/dev/testing` checklist.

## Components

### 1. BugReportFab (`web/src/components/bug-report-fab.tsx`)

Floating action button, fixed bottom-right (16px margin). Only renders when `goreos_dev_mode === "true"` in localStorage. Amber-500 background, bug icon. Click opens BugReportDrawer.

Mounted in `web/src/app/(app)/layout.tsx` — available on every authenticated page.

### 2. BugReportDrawer (inside bug-report-fab.tsx)

Side panel (reuses DrawerPanel component) with auto-context + 3 user inputs.

**Auto-captured (no user input):**
- `user_email` — from useAuth()
- `role_code` — from useAuth()
- `population` — from useAuth()
- `division_id` — from useAuth()
- `url` — window.location.pathname + search
- `timestamp` — ISO string
- `viewport` — `${window.innerWidth}x${window.innerHeight}`
- `active_checklist_item` — read from localStorage key (set by testing page on checkbox interaction)
- `screenshot` — base64 PNG via html2canvas (dynamic import, captures document.body)

**User inputs:**
- `title` — text input, required, placeholder "Qué salió mal..."
- `severity` — 4 toggle buttons: CRITICO (red), ALTO (amber), MEDIO (blue), BAJO (green). Default: MEDIO
- `description` — textarea, optional, placeholder "Detalles adicionales..."

**Submit flow:**
1. Capture screenshot via html2canvas (show spinner)
2. POST `/api/dev/bugs` with all fields
3. Close drawer
4. Show toast "Bug guardado"

### 3. Bugs Tab in `/dev/testing`

Add Radix Tabs to testing page: "Checklist" (default) | "Bugs ({count})".

**Bugs tab content:**
- KPI strip: 4 cards (Crítico/Alto/Medio/Bajo counts) with severity colors
- Bug list: cards with left border by severity color
  - Title (bold), severity badge
  - User email + URL + relative timestamp
  - Click to expand: description + screenshot thumbnail (if available)
- "Exportar JSON" button — downloads test-bugs.json
- Empty state when no bugs

### Backend (api/app/routers/dev.py — extend existing)

```python
_BUGS_PATH = Path(__file__).resolve().parents[3] / "docs" / "test-bugs.json"

@router.get("/bugs")
async def get_bugs():
    # ENV=development check
    # Read and return array from test-bugs.json

@router.post("/bugs")
async def create_bug(body: BugReport):
    # ENV=development check
    # Read existing array, append new bug with generated id
    # Write back to file
    # Return {id, ok: true}

@router.delete("/bugs/{bug_id}")
async def delete_bug(bug_id: str):
    # ENV=development check
    # Filter out bug by id, write back
```

BugReport schema:
```python
class BugReport(BaseModel):
    title: str
    severity: str  # CRITICO, ALTO, MEDIO, BAJO
    description: str | None = None
    user_email: str
    role_code: str
    population: str | None = None
    division_id: str | None = None
    url: str
    viewport: str | None = None
    checklist_item: str | None = None
    screenshot: str | None = None  # base64 PNG
```

### Persistence

File: `docs/test-bugs.json` — array of bug objects. Each bug gets `id` (uuid4) and `created_at` (ISO) server-side.

### Dependencies

- `html2canvas` — npm package, ~40KB gzipped. Dynamic import only when drawer opens (no impact on main bundle).

### Files

| File | Action | Lines est. |
|------|--------|:----------:|
| `web/src/components/bug-report-fab.tsx` | CREATE | ~180 |
| `web/src/app/(app)/layout.tsx` | MODIFY | +2 |
| `web/src/app/(app)/dev/testing/page.tsx` | MODIFY | +100 |
| `api/app/routers/dev.py` | MODIFY | +50 |
| `docs/test-bugs.json` | CREATE | 1 |
| `web/package.json` | MODIFY | +1 |
| **Total** | | **~330** |

### What This Does NOT Do
- No GitHub Issues integration (can be added later via export)
- No annotation on screenshots (captures as-is)
- No real-time sync between testers (file-based, single writer)
- No production usage (devMode + ENV=development gated)
