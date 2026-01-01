# Svelte 5 Runes Migration

## Goal

Migrate all Svelte components from legacy Svelte 4 reactivity syntax to Svelte 5 Runes mode. The codebase already uses Svelte 5 (`"svelte": "^5.0.0"`) but most components still use the old patterns (`$:` reactive statements, `export let` for props).

**Current state:**
- ~90 `.svelte` files total (routes, layouts, components, stories)
- ~70+ files using legacy `export let` props
- ~110+ reactive `$:` statements across the codebase
- Only ~6 files have started using Runes (`$state`, `$derived`, `$props`)

**Target state:**
- All components use `$props()` instead of `export let`
- All reactive logic uses `$state`, `$derived`, `$effect` instead of `$:`
- No legacy reactivity patterns remain


## References

- **Svelte 5 Migration Guide**: https://svelte.dev/docs/svelte/v5-migration-guide
- **Svelte 5 Runes Documentation**: https://svelte.dev/docs/svelte/runes
- **$bindable documentation**: https://svelte.dev/docs/svelte/$bindable
- **Frontend architecture**: `frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md`
- **Project structure**: `docs/reference/PROJECT_STRUCTURE.md`
- **Type checking**: `cd frontend && npm run check`
- **Unit tests**: `cd frontend && npm run test:unit -- --run`
- **E2E tests**: `cd frontend && npm run test:e2e`


## Principles & Key Decisions

1. **Incremental migration** - Migrate one component/file at a time, ensuring tests pass after each change
2. **Start with leaf components** - Migrate simple components with no children first, then work up to routes/layouts
3. **Layouts last** - Root layouts have high blast radius; migrate them after core components are stable
4. **Preserve behaviour** - Each migration must be a pure refactor with no functional changes
5. **Use `$props<T>()` generic syntax** - Prefer `let { prop1, prop2 } = $props<{ prop1: string; prop2?: number }>()` for cleaner typing
6. **Replace `$:` explicitly** - Every `$:` must be consciously replaced:
   - Computed values used in markup/logic → `$derived()` or `$derived.by()`
   - Side effects (console.log, API calls, DOM updates) → `$effect()` with cleanup if needed
   - Simple prop mirroring → delete the mirror and use prop directly, OR keep as `$derived`
   - **Never just delete `$:`** - this can silently break reactivity
7. **Never destructure `data` once** - SvelteKit's `data` prop can update on client-side navigation. Use reactive patterns:
   - `const sourcedir = $derived(data.sourcedir)` for each property, OR
   - Keep as `data.sourcedir` in templates
8. **Handle `bind:` props** - Components that support `bind:someProp` need `$bindable()` in runes mode
9. **Test after each file** - Run `npm run check` after each component migration
10. **Run unit tests periodically** - Run `npm run test:unit -- --run` after completing each stage


## Stages & Actions

### Stage: Preparation
- [ ] Create branch `260101c_svelte5_runes_migration` for this work
- [ ] Run `cd frontend && npm run check` to establish baseline (any existing type errors?)
- [ ] Run `cd frontend && npm run test:unit -- --run` to verify tests pass
- [ ] Web search for "svelte 5 runes migration best practices 2025" to confirm approach
- [ ] Search codebase for `bind:` usages to identify components needing `$bindable()`:
  - `rg 'bind:' frontend/src --glob '*.svelte' -l`
- [ ] Fix existing "migrated" reference file (`source/[sourcedir_slug]/+page.svelte`) - it has non-reactive `data` destructuring at line 87

### Stage: Migrate lib/components (leaf components first)
- [ ] Migrate simple components without `$:` statements:
  - [ ] `LoadingSpinner.svelte` (already uses `$state`)
  - [ ] `Alert.svelte`
  - [ ] `Card.svelte`
  - [ ] `MultilingualApology.svelte`
- [ ] Run `npm run check` after each file
- [ ] Migrate components with simple `$:` → `$derived`:
  - [ ] `ContactButton.svelte` (1 `$:` statement)
  - [ ] `LemmaContent.svelte` (2 `$:` statements)
  - [ ] `Breadcrumbs.svelte`
  - [ ] `NavTabs.svelte`
  - [ ] `AudioPlayer.svelte`
- [ ] Run `npm run check`
- [ ] Migrate components with multiple `$:` statements:
  - [ ] `DataGrid.svelte` (4 `$:` statements)
  - [ ] `DataGridNavButtons.svelte`
  - [ ] `EnhancedText.svelte` (complex, 1 `$:` with side effect)
  - [ ] `LemmaDetails.svelte` (8 `$:` statements)
  - [ ] `SourcefileLayout.svelte` (4 `$:` statements)
- [ ] Run `npm run check`
- [ ] Run `npm run test:unit -- --run`

### Stage: Migrate route pages (simpler ones first)
- [ ] Migrate static/simple pages (NOT layouts yet):
  - [ ] `routes/about/+page.svelte`
  - [ ] `routes/blog/+page.svelte`
  - [ ] `routes/languages/+page.svelte` (2 `$:` statements)
- [ ] Run `npm run check`
- [ ] Migrate auth pages:
  - [ ] `routes/auth/+page.svelte`
  - [ ] `routes/auth/profile/+page.svelte`
- [ ] Run `npm run check`
- [ ] Run `npm run test:unit -- --run`

### Stage: Migrate language route pages
- [ ] Migrate list pages:
  - [ ] `routes/language/[target_language_code]/+layout.svelte`
  - [ ] `routes/language/[target_language_code]/lemmas/+page.svelte`
  - [ ] `routes/language/[target_language_code]/wordforms/+page.svelte`
  - [ ] `routes/language/[target_language_code]/phrases/+page.svelte`
  - [ ] `routes/language/[target_language_code]/sentences/+page.svelte`
  - [ ] `routes/language/[target_language_code]/sources/+page.svelte`
- [ ] Run `npm run check`
- [ ] Migrate detail pages:
  - [ ] `routes/language/[target_language_code]/lemma/[lemma]/+page.svelte` (many `$:`)
  - [ ] `routes/language/[target_language_code]/wordform/[wordform]/+page.svelte` (many `$:`)
  - [ ] `routes/language/[target_language_code]/sentence/[slug]/+page.svelte`
  - [ ] `routes/language/[target_language_code]/phrase/[slug]/+page.svelte`
- [ ] Run `npm run check`

### Stage: Migrate sourcefile components (complex)
- [ ] Migrate sourcefile route components:
  - [ ] `components/SourcefileHeader.svelte` (many `$:`, complex)
  - [ ] `components/SourcefileText.svelte` (6 `$:` statements)
  - [ ] `components/SourcefileNavButtons.svelte` (6 `$:` statements)
  - [ ] `components/SourcefileTranslation.svelte`
  - [ ] Other sourcefile components
- [ ] Run `npm run check`
- [ ] Migrate sourcefile pages:
  - [ ] `[sourcefile_slug]/learn/+page.svelte` (many `$:`, complex)
  - [ ] Other sourcefile page routes
- [ ] Run `npm run check`

### Stage: Migrate remaining files
- [ ] Migrate search and flashcard pages:
  - [ ] `routes/language/[target_language_code]/search/+page.svelte`
  - [ ] `routes/language/[target_language_code]/flashcards/+page.svelte`
- [ ] Migrate remaining components not yet covered
- [ ] Migrate Storybook stories (low priority):
  - [ ] `stories/*.svelte` files
- [ ] Run `npm run check`
- [ ] Run `npm run test:unit -- --run`

### Stage: Migrate layouts (high blast radius - do last)
- [ ] Migrate layouts after all components are stable:
  - [ ] `routes/+layout.svelte` (root layout, 8 `$:` statements)
  - [ ] `routes/language/[target_language_code]/+layout.svelte`
- [ ] Run `npm run check`
- [ ] Run `npm run test:unit -- --run`
- [ ] Run `npm run test:e2e` (layouts affect entire app)

### Stage: Validation & Cleanup
- [ ] Run full type check: `cd frontend && npm run check`
- [ ] Run linter: `cd frontend && npm run lint`
- [ ] Run full test suite: `cd frontend && npm test`
- [ ] Manually test key user flows in browser:
  - [ ] Language selection and navigation
  - [ ] Client-side navigation between pages (verify `data` reactivity works)
  - [ ] Sourcefile viewing and learning flow
  - [ ] Flashcards
  - [ ] Search functionality
  - [ ] Any `bind:` functionality still works
- [ ] Grep for any remaining legacy patterns:
  - [ ] `rg '\$:' frontend/src --glob '*.svelte'` should return 0 results
  - [ ] `rg 'export let' frontend/src --glob '*.svelte'` should return 0 results (except stories if not migrated)
- [ ] Stop & review with user

### Stage: Merge & Finish
- [ ] Create PR for review
- [ ] Merge branch to main
- [ ] Move this doc to `docs/plans/finished/`


## Appendix

### Conversion Patterns

**Props - before:**
```svelte
<script>
  export let title: string;
  export let count = 0;
</script>
```

**Props - after (preferred generic syntax):**
```svelte
<script>
  let { title, count = 0 } = $props<{ title: string; count?: number }>();
</script>
```

**Bindable props - before:**
```svelte
<script>
  export let value = '';  // used with bind:value
</script>
```

**Bindable props - after:**
```svelte
<script>
  let { value = $bindable('') } = $props<{ value?: string }>();
</script>
```

**Reactive declarations - before:**
```svelte
$: doubled = count * 2;
$: if (condition) { doSomething(); }
```

**Reactive declarations - after:**
```svelte
const doubled = $derived(count * 2);
$effect(() => { if (condition) doSomething(); });
```

**Complex derived - before:**
```svelte
$: filtered = items.filter(x => x.active).map(x => x.name);
```

**Complex derived - after:**
```svelte
const filtered = $derived.by(() => items.filter(x => x.active).map(x => x.name));
```

**SvelteKit `data` prop - WRONG (non-reactive):**
```svelte
<script>
  let { data } = $props();
  const { sourcedir, files } = data;  // BAD: won't update on client navigation
</script>
```

**SvelteKit `data` prop - CORRECT (reactive):**
```svelte
<script>
  let { data } = $props();
  const sourcedir = $derived(data.sourcedir);
  const files = $derived(data.files);
</script>
```

### Common Migration Pitfalls

1. **Don't just delete `$:`** - Every `$:` needs explicit replacement with `$derived`, `$effect`, or inline usage
2. **SvelteKit `data` updates** - The `data` prop can change on client-side navigation; destructuring it once breaks reactivity
3. **`bind:` needs `$bindable()`** - Components accepting bound props must declare them with `$bindable()`
4. **`$effect` cleanup** - Unlike `$:`, `$effect` can return a cleanup function for subscriptions/listeners

### Files Already Using Runes (reference with caveats)
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte` - **Note: has non-reactive data destructuring that needs fixing**
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileHeader.svelte` (partial)
- `frontend/src/lib/components/LoadingSpinner.svelte`
- `frontend/stories/Button.svelte`
- `frontend/stories/Header.svelte`
- `frontend/stories/Page.svelte`

### File Count Summary
- Routes/layouts: ~35 files
- lib/components: ~45 files  
- Stories: ~8 files
- Total: ~88 Svelte files requiring migration

### Review Notes (260101)
Initial plan reviewed by GPT-5.2 (high reasoning). Key feedback incorporated:
- Added explicit `$bindable()` guidance for components with `bind:` support
- Moved layout migration to end (high blast radius)
- Added unit/e2e test checkpoints throughout
- Clarified that `$:` must never be silently deleted
- Added SvelteKit `data` reactivity patterns
- Flagged existing "migrated" reference file as needing fixes before using as template
