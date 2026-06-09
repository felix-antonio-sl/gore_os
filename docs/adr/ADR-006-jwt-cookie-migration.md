# ADR-006: JWT Cookie Migration

**Status**: DEFERRED — acknowledged as a future security improvement, but not scheduled for implementation
**Date**: 2026-03-03 (proposed) | 2026-06-09 (deferred)
**Deciders**: GORE_OS development team

## Current State (2026-06-09)

The system uses JWT tokens stored in `localStorage` (key: `goreos_token`). The `ApiClient` singleton reads the token on every request and attaches it as an `Authorization: Bearer` header. This is the pattern documented in [CLAUDE.md](../../CLAUDE.md) §Security and implemented in `web/src/lib/api.ts`.

**Why deferred**: The migration to httpOnly cookies requires CORS credentials changes, CSRF protection on all state-changing endpoints, and a dual-acceptance transition period. The SPA/JWT architecture with SecurityHeadersMiddleware provides adequate protection given the current deployment model (same-origin API + frontend behind reverse proxy). If the deployment model changes (e.g., mobile clients, third-party integrations), this ADR should be revisited.

## Context

Currently, JWT access tokens are stored in `localStorage` under the key `goreos_token`. The `ApiClient` singleton in `web/src/lib/api.ts` reads the token on every request and attaches it as an `Authorization: Bearer` header. This is a straightforward pattern but exposes the token to XSS attacks: any injected script can read `localStorage` and exfiltrate the token to steal the session.

## Threat model

An XSS vulnerability (e.g., in a third-party dependency or unsanitized user content) would allow an attacker to call `localStorage.getItem('goreos_token')`, forward it to an attacker-controlled endpoint, and impersonate the user indefinitely until the token expires (default: 60 minutes).

## Proposed decision

Migrate JWT storage from `localStorage` to an `httpOnly` cookie set by the FastAPI backend at login. `httpOnly` cookies are inaccessible to JavaScript, eliminating the XSS exfiltration vector.

## Migration plan

1. **Backend**: Add `Set-Cookie: goreos_token=<jwt>; HttpOnly; Secure; SameSite=Lax` to the `/api/auth/login` response. Continue accepting `Authorization: Bearer` header for backward compatibility during the transition period.
2. **Frontend**: Remove `localStorage.setItem('goreos_token', ...)` from `AuthProvider`. Configure `ApiClient` to send `credentials: 'include'` on all requests instead of reading localStorage.
3. **CSRF protection**: Add a `X-CSRF-Token` double-submit cookie pattern or use `SameSite=Strict` to mitigate CSRF on state-changing requests.
4. **Dual period**: Accept both cookie and Bearer header during rollout. Remove Bearer header support after all clients migrate.

## Consequences

- **XSS protection**: `httpOnly` cookies cannot be read by JavaScript, eliminating token exfiltration.
- **CSRF exposure**: Cookies are sent automatically by browsers; CSRF protection is required on all non-GET endpoints.
- **CORS changes**: `credentials: 'include'` requires the CORS `allow_credentials=True` and an explicit (non-wildcard) origin.
- **Mobile/API clients**: Token-in-header pattern still needed for non-browser clients (ETL scripts, Swagger UI testing). Dual-mode auth handles this.
