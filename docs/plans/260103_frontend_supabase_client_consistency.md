# Frontend Supabase Client Consistency

**Priority**: Medium-High (Auth Correctness)
**Effort**: Medium
**Risk**: Medium (auth changes need careful testing)
**Status**: COMPLETED (impl review: 87%, 95%, 78% -> fixes applied)

## Problem

Multiple Supabase client patterns cause confusion and potential auth/RLS issues:

1. **Server-side**: `locals.supabase` (cookie/session-aware) - CORRECT
2. **Browser client**: `+layout.ts` creates via `createBrowserClient` - CORRECT
3. **Singleton**: `$lib/supabaseClient.ts` - NOT request/session-aware on server
4. **Component access**: `($page?.data as any)?.supabase` - untyped, repeated

**Key insight**: The singleton is problematic on the server because it lacks request-specific session context (cookies). Queries run as `anon` role, bypassing user RLS policies.

### Specific Issues (Updated)

**Server routes using singleton (CRITICAL - bypasses RLS):**
- `frontend/src/routes/language/[target_language_code]/sources/+page.server.ts:5`
- `frontend/src/routes/language/[target_language_code]/generate/+page.server.ts:2`

**Client components using singleton (should use page data):**
- `frontend/src/routes/language/[target_language_code]/sources/+page.svelte:7`

**Untyped page data access:**
- `frontend/src/lib/components/LemmaContent.svelte:20`
  - `$: supabaseClient = ($page?.data as any)?.supabase ?? null;`
- `frontend/src/routes/.../learn/+page.svelte`
  - Same pattern repeated 7+ times (lines 293, 393, 440, 496, 647, 702, 859)

**Incomplete types:**
- `frontend/src/app.d.ts` - `PageData` only has `session`, missing `supabase`, `user`, `profile`, `is_admin`

## Architecture Context

The app has two correct Supabase client paths:
1. **Server**: `hooks.server.ts` creates `createServerClient` with cookies → `locals.supabase`
2. **Browser**: `+layout.ts` creates `createBrowserClient` → `$page.data.supabase`

The singleton `$lib/supabaseClient.ts` was a legacy approach that should NOT be used in:
- Any `+page.server.ts` or `+layout.server.ts` (use `locals.supabase`)
- Client components needing authenticated access (use `$page.data.supabase`)

## Implementation Steps

### Step 1: Update `app.d.ts` types
```typescript
interface PageData {
  session: Session | null
  user: User | null
  supabase: SupabaseClient<Database> | null
  profile?: any
  is_admin?: boolean | null
}
```

### Step 2: Fix server routes
Replace singleton imports with `locals.supabase`:
- `sources/+page.server.ts` 
- `generate/+page.server.ts`

### Step 3: Fix client component
Update `sources/+page.svelte` to use `data.supabase` instead of singleton import.

### Step 4: Remove `as any` casts
With proper types, update all `($page?.data as any)?.supabase` patterns to use typed access.

### Step 5: Add eslint/grep guard (optional)
Prevent future imports of `$lib/supabaseClient` in `*.server.ts` files.

## Success Criteria

- No singleton client used in server routes
- No singleton client used in client components for authenticated operations
- Typed `App.PageData` interface with all returned fields
- No `as any` casts for supabase access
- Clear documentation of which client to use where

## Files to Modify

```
frontend/src/app.d.ts
frontend/src/routes/language/[target_language_code]/sources/+page.server.ts
frontend/src/routes/language/[target_language_code]/generate/+page.server.ts
frontend/src/routes/language/[target_language_code]/sources/+page.svelte
frontend/src/lib/components/LemmaContent.svelte
frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte
```

## Client Usage Guide

| Context | Use | Import/Access |
|---------|-----|---------------|
| `+page.server.ts` / `+layout.server.ts` | `locals.supabase` | `({ locals: { supabase } })` |
| `hooks.server.ts` | `event.locals.supabase` | Created by hook |
| `.svelte` components | `$page.data.supabase` | Type-safe via `App.PageData` |
| Never in auth contexts | `$lib/supabaseClient` | Legacy, anon-only |

## Notes

Triple-review flagged additional files missed in original plan. RLS bypass in server routes is the critical security issue.
