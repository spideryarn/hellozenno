# Frontend TypeScript `any` Reduction

**Priority**: High (Maintainability)
**Effort**: Medium-High
**Risk**: Low (type-only changes, no runtime impact)
**Scope**: Core layout/API layer and high-impact components (not exhaustive)

## Problem

40+ instances of `any` type plus `as any` casts undermine TypeScript's value.

### High-Impact Locations

1. **api.ts**
   - Line 44: `R = any` generic default
   - Lines 140, 148: `errorData: any`, `error as any`
   - Lines 414, 448: `catch (error: any)` patterns

2. **types.ts**
   - Line 94: `data: any` in `SearchResult`
   - Lines 31-33: `any[]` for synonyms, antonyms, related_words_phrases_idioms
   - Line 45: `any[]` for easily_confused_with

3. **Layout files**
   - `+layout.ts:16,19`: `data as any` casts
   - `+layout.svelte:39`: `(event: any, newSession: any)` auth callback
   - `+layout.server.ts`: Returns `profile` without type propagation

4. **app.d.ts**
   - `PageData` has `session` but missing `profile`, `is_admin`, `supabase`
   - This forces `as any` casts throughout the app

5. **Components**
   - `LemmaContent.svelte:8`: `lemma_metadata: any`
   - `DataGrid.svelte`: `rows: any[]`, generic `T = any`
   - `DropdownButton.svelte:11`: `buttonSvelteContent: any`

6. **Learn page** (actual path: `routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte`)
   - `($page?.data as any)?.supabase` repeated 9+ times
   - `audioPlayer: any` (line 60)
   - `warmingQueue: any` (line 95)
   - `summaryMeta: any` (line 105)

7. **DataGrid providers** (out of primary scope, noted for future)
   - `lib/datagrid/providers/supabase.ts`: 6 `any` usages (query builder types)
   - `lib/datagrid/utils.ts:50`: `accessor: (row: any)`

8. **Other locations** (out of primary scope, noted for future)
   - `lib/processing-queue.ts:56`: `null as any`
   - `routes/admin/users/+page.svelte:10`: `($page.data as any)?.supabase`
   - `routes/auth/profile/+page.svelte:116`: `(data as any)?.is_admin`
   - Multiple `catch (err: any)` in `+page.server.ts` files

## Approach

### Phase 1: Extend App.PageData (High Impact, Low Effort)
Add missing types to `app.d.ts`:
```typescript
interface PageData {
  session: Session | null;
  profile: UserProfile | null;  // Add profile type (define in types.ts)
  is_admin: boolean | null;     // Add admin flag (null when not authenticated)
  supabase: SupabaseClient<Database> | null;  // null on SSR, client in browser
}
```
Also create `UserProfile` interface in `frontend/src/lib/types.ts` based on backend profile response.
This eliminates most `($page.data as any)` casts once Phase 2 removes layout-layer casts.

### Phase 2: Fix Layout Data Flow
- Type auth callback in `+layout.svelte` using `AuthChangeEvent`, `Session | null`
- Remove `as any` casts in `+layout.ts`
- Ensure `+layout.server.ts` profile return type flows through

### Phase 3: Define Core Interfaces
- Create `LemmaMetadata` interface based on actual usage in `LemmaContent.svelte`
- Create `SynonymEntry`, `AntonymEntry`, `RelatedPhrase` interfaces
- Define `EasilyConfusedEntry` interface (has `lemma`, `explanation`, `example_usage_*`)

### Phase 4: API Response Typing (Gradual Migration)
**Strategy**: Keep `R = any` default temporarily, migrate call sites incrementally:
1. Create response type mappings for common endpoints
2. Add explicit type parameters at call sites: `apiFetch<..., ResponseType>(...)`
3. After majority typed, change default to `R = unknown`

This avoids breaking all 20+ call sites at once.

### Phase 5: Component Props
- Type `LemmaContent.svelte` props with new interfaces
- Make `DataGrid` properly generic: `<script lang="ts" generics="T">`
- Create typed helper for Supabase client access (or use context pattern)

### Phase 6: Learn Page Cleanup
- Replace `($page.data as any).supabase` with typed access
- Type `audioPlayer`, `warmingQueue`, `summaryMeta` variables
- Use proper event types throughout

## Verification Strategy

Before starting:
```bash
cd frontend && npm run check 2>&1 | grep -c "error"  # Baseline error count
rg "any" --glob "*.ts" --glob "*.svelte" src/ | wc -l  # Baseline any count
```

After each phase, re-run to verify no regressions and measure progress.

## Success Criteria

- **Primary scope**: 80%+ reduction in `any` usage in layout layer and core components
- No `as any` casts for `$page.data` access patterns
- Typed Supabase client access (via PageData or context)
- `npm run check` passes with no new errors

## Files to Modify (Primary Scope)

```
frontend/src/app.d.ts
frontend/src/lib/types.ts
frontend/src/lib/api.ts
frontend/src/routes/+layout.ts
frontend/src/routes/+layout.svelte
frontend/src/routes/+layout.server.ts
frontend/src/lib/components/LemmaContent.svelte
frontend/src/lib/components/DataGrid.svelte
frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte
```

## Files Noted for Future Work (Out of Primary Scope)

```
frontend/src/lib/datagrid/providers/supabase.ts
frontend/src/lib/datagrid/utils.ts
frontend/src/lib/processing-queue.ts
frontend/src/routes/admin/users/+page.svelte
frontend/src/routes/auth/profile/+page.svelte
Various +page.server.ts files (catch (err: any) patterns)
```

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Breaking API calls with `R = unknown` | High | Gradual migration (Phase 4 strategy) |
| Layout data flow changes causing runtime errors | Medium | Test auth flows after changes |
| Missing edge cases in new interfaces | Low | Base on actual usage, extend incrementally |
| Future `any` creep | Medium | Consider ESLint `@typescript-eslint/no-explicit-any` warning |

## Notes

- All 3 initial reviewers flagged this issue
- `app.d.ts` already has `Locals` properly typed; `PageData` needs extension
- Consider Svelte context for Supabase client as alternative to PageData
- `unknown` + runtime validation is preferred TypeScript pattern for API responses
