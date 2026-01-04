# Plan: Auth Redirect Parameter Fix

**Date:** 2026-01-04
**Status:** Draft

## Overview

Fix the auth redirect parameter mismatch where the backend reads `redirect=` but all frontend code and decorators use `next=`.

## Context

- **Relevant findings from research:**
  - 25+ locations generate `/auth?next=<url>` (frontend, decorators, tests)
  - Only 1 location reads `redirect=`: `backend/views/auth_views.py` line 40
  - `next=` is the Flask-Login and industry standard convention
  - Frontend SvelteKit auth (`/auth/+page.ts`) already correctly reads `next=`

- **Key constraints and requirements:**
  - The `auth.jinja` template passes `redirect_url` to a Svelte component as `redirectUrl` prop - this is an internal variable name, not the URL parameter, so it remains unchanged
  - E2E test at `frontend/e2e/admin_access.test.ts` expects `/auth?next=/admin`
  - Must maintain security validation via `is_safe_redirect_url()`

- **Success criteria:**
  1. Backend reads `next=` parameter instead of `redirect=`
  2. Existing E2E test passes without modification
  3. Auth redirect flow works correctly end-to-end

## Stages

### Stage 1: Update Backend Parameter

**Goal:** Change the backend to read `next=` instead of `redirect=`

**Files:** 
- `backend/views/auth_views.py`

**Steps:**
1. In `auth_page_vw()` function (line 40), change:
   ```python
   redirect_url = request.args.get("redirect", "/")
   ```
   to:
   ```python
   redirect_url = request.args.get("next", "/")
   ```

**Verification:**
- [ ] `ruff check backend/` passes
- [ ] `black --check backend/` passes
- [ ] Unit tests pass: `pytest backend/tests/`
- [ ] Manual test: Navigate to `/auth?next=/somepath` and verify redirect after login

### Stage 2: Verify Integration

**Goal:** Confirm the fix works end-to-end

**Files:** None (verification only)

**Steps:**
1. Run E2E tests to verify admin access test passes
2. Test the full auth flow manually:
   - Access a protected page while logged out
   - Verify redirect to `/auth?next=<protected_url>`
   - Log in and verify redirect to the protected URL

**Verification:**
- [ ] E2E test `admin_access.test.ts` passes (expects `/auth?next=/admin`)
- [ ] Manual auth flow works correctly

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking existing bookmarks/links using `redirect=` | Low | Very Low | The application only uses `next=`; no known external consumers use `redirect=` |
| Template variable confusion | Low | Very Low | `redirect_url` in templates is an internal variable name, not the URL parameter |

## Implementation Notes

### Stage 1 Notes
- Decisions made:
- Learnings:
- Deviations from plan:

### Stage 2 Notes
- Decisions made:
- Learnings:
- Deviations from plan:
