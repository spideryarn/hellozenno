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

---

## Implementation Notes

### Phase 1: Extend App.PageData - COMPLETED ✓

**Date**: 2026-01-03

**Changes Made**:
1. Created `UserProfile` interface in `frontend/src/lib/types.ts`:
   - Fields: `id`, `user_id`, `target_language_code`, `admin_granted_at`, `created_at`, `updated_at`
   - Optional `email` field (added by profile_api.py from auth.users)
   - Matches backend `Profile.to_dict()` output

2. Updated `frontend/src/app.d.ts`:
   - Added import for `UserProfile` from `$lib/types`
   - Changed `profile?: any` to `profile?: UserProfile | null`
   - Kept optional marker (`?`) on `profile`, `is_admin`, `user`, `supabase` to preserve backward compatibility

**Decisions**:
- Kept `profile`, `is_admin`, `user`, `supabase` as optional (`?`) in PageData rather than required, since not all pages may have these values (e.g., some page-specific loads may not propagate them)
- `UserProfile` interface placed at top of types.ts for visibility

**Verification**:
- `npm run check` passes with 0 errors (5 warnings, all pre-existing CSS/export-related)

**Next Steps for Phase 2**:
- Remove `as any` casts in `+layout.ts` (lines 16, 19)
- Type the auth callback in `+layout.svelte` with proper Supabase types
- Ensure type flow from `+layout.server.ts` through to page components

### Phase 3: Define Core Interfaces - COMPLETED ✓

**Date**: 2026-01-03

**Changes Made**:
1. Created `ExampleUsageEntry` interface in `frontend/src/lib/types.ts`:
   - Fields: `phrase`, `translation`, `slug`
   - Replaces inline type definition in `Lemma.example_usage`

2. Created `RelatedLemmaEntry` interface:
   - Fields: `lemma`, `translations?`, `part_of_speech?`, `commonality?`, `is_complete?`
   - Used for `synonyms`, `antonyms`, `related_words_phrases_idioms` arrays
   - Based on actual usage in `LemmaCard` component

3. Created `EasilyConfusedEntry` interface:
   - Fields: `lemma`, `translations?`, `part_of_speech?`, `commonality?`, `is_complete?`, `explanation?`, `example_usage_this_target?`, `example_usage_this_source?`, `example_usage_this_slug?`, `example_usage_other_target?`, `example_usage_other_source?`, `example_usage_other_slug?`, `notes?`, `mnemonic?`
   - Based on actual usage in `LemmaContent.svelte` "Easily Confused With" section
   - Matches backend `_sanitize_easily_confused_entry` structure

4. Updated `Lemma` interface:
   - `synonyms?: RelatedLemmaEntry[]` (was `any[]`)
   - `antonyms?: RelatedLemmaEntry[]` (was `any[]`)
   - `related_words_phrases_idioms?: RelatedLemmaEntry[]` (was `any[]`)
   - `example_usage?: ExampleUsageEntry[]` (was inline type)
   - `easily_confused_with?: EasilyConfusedEntry[]` (was `any[]`)

**Decisions**:
- Named interface `RelatedLemmaEntry` (not `SynonymEntry`/`AntonymEntry` separately) since all three arrays use the same structure
- All fields except `lemma` are optional to handle partial data from API
- Based interface fields on actual component usage (`LemmaContent.svelte`, `LemmaCard.svelte`) and backend fixtures

**Verification**:
- `npm run check` passes with 0 errors (5 warnings, all pre-existing)

**Next Steps for Phase 4**:
- Create response type mappings for common API endpoints
- Add explicit type parameters at `apiFetch` call sites

### Phase 4: API Response Typing (Gradual Migration) - COMPLETED ✓

**Date**: 2026-01-03

**Changes Made**:
1. Created `ApiError` class in `frontend/src/lib/api.ts`:
   - Extends `Error` with `status: number` and `body: Record<string, unknown>`
   - Provides typed error handling for API failures
   - Exported for use in catch blocks throughout the codebase

2. Fixed error handling in `apiFetch` function:
   - Changed `errorData: any` to `errorData: Record<string, unknown>`
   - Removed `catch (e)` unused variable
   - Added type guards for extracting `description` and `message` from error response
   - Replaced `new Error(message) as any` with `new ApiError(message, status, body)`

3. Fixed `catch (error: any)` in `getWordformWithSearch`:
   - Changed to `catch (error: unknown)`
   - Added `instanceof ApiError` type guard for status checking

4. Fixed `catch (error: any)` in `getLemmaMetadata`:
   - Changed to `catch (error: unknown)`
   - Added `instanceof ApiError` type guard
   - Restructured error handling to properly narrow type before accessing `.status` and `.body`

**Decisions**:
- Created `ApiError` class instead of just an interface because `instanceof` checks work with classes
- Kept `R = any` default for `apiFetch` as per gradual migration strategy (call sites can add explicit types incrementally)
- Used `Record<string, unknown>` for error body to allow property access while maintaining type safety
- Used type guards (`typeof x === 'string'`) for extracting error message fields

**`any` Usages Fixed**:
- `errorData: any` → `errorData: Record<string, unknown>`
- `const error = new Error(message) as any` → `throw new ApiError(...)`
- `catch (error: any)` → `catch (error: unknown)` (2 instances)

**Verification**:
- `npm run check` passes with 0 errors (5 warnings, all pre-existing CSS/export-related)

**Next Steps for Phase 5**:
- Type `LemmaContent.svelte` props with new interfaces
- Make `DataGrid` properly generic
- Create typed helper for Supabase client access

### Phase 5: Component Props - COMPLETED ✓

**Date**: 2026-01-03

**Changes Made**:

1. **LemmaContent.svelte** (`frontend/src/lib/components/LemmaContent.svelte`):
   - Changed `lemma_metadata: any` to `lemma_metadata: Lemma | Partial<Lemma> | null`
   - Added import for `Lemma` type from `$lib/types`
   - Uses `Partial<Lemma>` to handle cases where incomplete data is passed from `LemmaDetails`

2. **LemmaDetails.svelte** (`frontend/src/lib/components/LemmaDetails.svelte`):
   - Changed `lemma_metadata: any | null` to `lemma_metadata: Lemma | null`
   - Changed `completeData: any | null` to `completeData: Lemma | null`
   - Changed `displayData` to be typed as `Partial<Lemma>` to handle empty object case
   - Added early return guard for `!lemmaValue` in `fetchCompleteData()` to satisfy TypeScript

3. **LemmaCard.svelte** (`frontend/src/lib/components/LemmaCard.svelte`):
   - Changed `lemma: Lemma` to `lemma: LemmaCardData`
   - Added `'property' in lemma` type guards for accessing `Lemma`-only properties (`guessability`, `etymology`, `register`) when `showDetails` is true

4. **DropdownButton.svelte** (`frontend/src/lib/components/DropdownButton.svelte`):
   - Changed `buttonSvelteContent: any` to `buttonSvelteContent: Component | null`
   - Imported `type Component` from Svelte 5
   - Created `DropdownItem` type to replace `any` in `handleItemClick(item: any)`

5. **types.ts** (`frontend/src/lib/types.ts`):
   - Created `LemmaCardData = Lemma | RelatedLemmaEntry` type alias for `LemmaCard` component
   - Added `generation_in_progress?: boolean` and `authentication_required_for_generation?: boolean` to `Lemma` interface (API response fields)

**Decisions**:
- Used `Partial<Lemma>` for `displayData` in `LemmaDetails` rather than a union type, as it better represents the "possibly incomplete Lemma data" scenario
- Created `LemmaCardData` type alias rather than modifying `RelatedLemmaEntry` to match `Lemma`, keeping types semantically meaningful
- Used `'property' in obj` pattern for type guards in template code rather than casting
- Used Svelte 5's `Component` type for `buttonSvelteContent` to properly type Svelte component constructors

**`any` Usages Fixed**:
- `lemma_metadata: any` → `Lemma | Partial<Lemma> | null` (LemmaContent.svelte)
- `lemma_metadata: any | null` → `Lemma | null` (LemmaDetails.svelte)
- `completeData: any | null` → `Lemma | null` (LemmaDetails.svelte)
- `lemma: Lemma` → `LemmaCardData` (LemmaCard.svelte - aligns with RelatedLemmaEntry usage)
- `buttonSvelteContent: any` → `Component | null` (DropdownButton.svelte)
- `handleItemClick(item: any)` → `handleItemClick(item: DropdownItem)` (DropdownButton.svelte)

**Note on DataGrid.svelte**:
DataGrid intentionally uses `any` in several places (`rows: any[]`, `ColumnDef<T = any>`) because it's designed as a generic, reusable component. Svelte 5 supports component-level generics via `<script lang="ts" generics="T">`, but full generic typing would require refactoring all consumers. This is noted for future work but out of scope for this phase.

**Verification**:
- `npm run check` passes with 0 errors (5 warnings, all pre-existing CSS/export-related)

**Next Steps for Phase 6**:
- Replace `($page.data as any).supabase` patterns in Learn page with typed access
- Type `audioPlayer`, `warmingQueue`, `summaryMeta` variables in Learn page
- Use proper event types throughout

### Phase 6: Learn Page Cleanup - COMPLETED ✓

**Date**: 2026-01-03

**Changes Made**:

1. **app.d.ts** - Added `target_language_code?: string` and `language_name?: string` to App.PageData interface to enable typed access from language layout data.

2. **types.ts** - Created new interfaces for learn page types:
   - `LearnSummaryLemma`: Lemma entry from summary API with translations, etymology, commonality, guessability, part_of_speech, is_complete
   - `LearnSummaryMeta`: Meta information from summary API (total_candidates, returned, durations, partial, counts)
   - `LearnGenerateMeta`: Meta information from generate API (reused_count, new_count, durations, timed_out, skipped_due_to_timeout)
   - `WarmingQueue`: Interface for p-queue-like task queue with `add()` and `onIdle()` methods

3. **types.ts** - Updated `Lemma` interface: changed `commonality?: number` and `guessability?: number` to allow `null` values (`commonality?: number | null`, `guessability?: number | null`) to match API responses.

4. **learn/+page.svelte** - Fixed all `any` usages:
   - `lemmas: Array<any>` → `LearnSummaryLemma[]`
   - `audioPlayer: any` → `{ play: () => void } | null` (component instance type)
   - `warmingQueue: any` → `WarmingQueue | null`
   - `preparedMeta: any` → `LearnGenerateMeta | null`
   - `summaryMeta: any` → `LearnSummaryMeta | null`
   - `($page.data as any)?.language_name` → `$page.data.language_name` (typed access)
   - All `catch (e: any)` → `catch (e: unknown)` with `const err = e as Error | null` pattern
   - `(x: any) => x.lemma` → `(x: { lemma: string }) => x.lemma`
   - `(c: any) => c.audio_data_url` → `(c) => c.audio_data_url` (type inference from preparedCards)
   - Fixed `ensureWarmingQueue` to use `as WarmingQueue` cast for fallback queue object
   - Fixed `.filter(Boolean)` → `.filter((url): url is string => url !== null)` for proper type narrowing
   - Changed `warmingQueue.add(...)` → used queue from `.then((queue) => queue.add(...))` pattern

5. **text/+page.svelte** - Fixed collateral type error: `$page.data.language_name` → `$page.data.language_name || target_language_code` for fallback.

**Decisions**:
- Used `{ play: () => void } | null` for audioPlayer since it's a Svelte component instance binding (not HTMLAudioElement)
- Created specific types for learn API meta objects rather than using generic `Record<string, unknown>`
- Cast fallback queue object `as WarmingQueue` since generic function syntax in object literals causes Svelte parser errors
- Used `e as Error | null` pattern in catch blocks for safe access to `.name` and `.message` properties
- Added `language_name` and `target_language_code` to App.PageData for typed access across language routes

**`any` Usages Fixed in Learn Page**:
- `lemmas: Array<any>` (line 31)
- `audioPlayer: any` (line 57)
- `preparedMeta: any` (line 166)
- `warmingQueue: any` (line 170)
- `summaryMeta: any` (line 185)
- `($page.data as any)?.language_name` (line 510)
- `catch (e: any)` (6 occurrences across the file)
- `(x: any) => x.lemma` (line 582)
- `(c: any) => c.audio_data_url` (line 802)

**Remaining `as any` Casts** (intentionally kept):
- `signal: summaryAbortCtrl.signal as any` (line 533) - AbortSignal type compatibility with RequestInit
- `signal: prepareAbortCtrl.signal as any` (line 792) - Same reason

These signal casts are minor type compatibility issues and don't affect runtime behavior.

**Verification**:
- `npm run check` passes with 0 errors (5 warnings, all pre-existing CSS/export-related)
