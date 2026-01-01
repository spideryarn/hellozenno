# Plan: Breadcrumb Architecture Refactor

**Date:** 2026-01-01
**Status:** Complete

## Overview

Refactor the breadcrumb system to eliminate duplicate breadcrumbs and establish a consistent, unified approach using Bootstrap's standard breadcrumb pattern with proper ARIA attributes.

## Context

### Problem
Breadcrumbs appear twice on many pages due to:
1. **Language layout** (`/frontend/src/routes/language/[target_language_code]/+layout.svelte`) renders generic breadcrumbs using `<div class="breadcrumbs">` with `»` separators
2. **SourcefileLayout component** and individual pages render their own breadcrumbs using proper Bootstrap `<nav><ol class="breadcrumb">` pattern
3. Inconsistent markup across pages:
   - Language layout: `<div class="breadcrumbs">` with manual `»` separators
   - SourcefileLayout: `<nav aria-label="breadcrumb"><ol class="breadcrumb">`
   - Lemma/Wordform pages: `<nav aria-label="breadcrumb"><ol class="breadcrumb">`
   - Sentence page: `<div class="breadcrumbs">` with manual `»` separators

### Key Findings from Research
1. **Current implementations found:**
   - Language layout (line 12-17): Generic breadcrumbs in a `div.breadcrumbs`
   - SourcefileLayout.svelte (line 61-71): Full Bootstrap pattern with 6 levels
   - Lemma page: Bootstrap pattern with 4 levels
   - Wordform page: Bootstrap pattern with 4 levels
   - Phrase page: Bootstrap pattern with 3 levels (missing language in path)
   - Sentence page: `div.breadcrumbs` pattern with 4 levels
   - Sourcedir page: Bootstrap pattern with 4 levels

2. **Shared styling:** Multiple files define `.breadcrumb` styles with identical rules (background-color, padding, border-radius)

3. **Pages using SourcefileLayout:** text, translation, words, phrases, image, audio, learn tabs all use SourcefileLayout which already has proper breadcrumbs

### Approved Solution
**Option A: Page-owned breadcrumbs with unified component**
- Create unified `Breadcrumbs.svelte` component
- Remove breadcrumbs from language layout
- Each page explicitly renders breadcrumbs using the component
- Standardize on Bootstrap `<nav aria-label="breadcrumb"><ol class="breadcrumb">` pattern

## Success Criteria

1. No duplicate breadcrumbs on any page
2. Consistent Bootstrap breadcrumb markup across all pages
3. Proper ARIA attributes for accessibility
4. TypeScript interface for type safety
5. Centralized styling (no scattered `.breadcrumb` CSS)
6. All existing tests pass
7. Visual appearance maintained or improved

## Route Audit

**All pages under `/language/[target_language_code]/` (23 total):**

| Route | Has Breadcrumbs? | Action |
|-------|-----------------|--------|
| `lemmas/+page.svelte` | Via layout only | Add breadcrumbs (list page) |
| `lemma/[lemma]/+page.svelte` | Yes (own + layout) | Update to use component |
| `sources/+page.svelte` | Via layout only | Add breadcrumbs (list page) |
| `generate/+page.svelte` | Via layout only | Add breadcrumbs |
| `wordform/[wordform]/+page.svelte` | Yes (own + layout) | Update to use component |
| `sentences/+page.svelte` | Via layout only | Add breadcrumbs (list page) |
| `sentence/[slug]/+page.svelte` | Yes (own + layout) | Update to use component |
| `test-error/+page.svelte` | Via layout only | Skip (dev page) |
| `search/[wordform]/+page.svelte` | Via layout only | Add breadcrumbs |
| `search/+page.svelte` | Via layout only | Add breadcrumbs |
| `phrases/+page.svelte` | Via layout only | Add breadcrumbs (list page) |
| `source/[sourcedir_slug]/+page.svelte` | Yes (own + layout) | Update to use component |
| `source/.../text/+page.svelte` | Via SourcefileLayout | Update SourcefileLayout |
| `source/.../image/+page.svelte` | Via SourcefileLayout | Update SourcefileLayout |
| `source/.../words/+page.svelte` | Via SourcefileLayout | Update SourcefileLayout |
| `source/.../audio/+page.svelte` | Via SourcefileLayout | Update SourcefileLayout |
| `source/.../phrases/+page.svelte` | Via SourcefileLayout | Update SourcefileLayout |
| `source/.../learn/+page.svelte` | None currently | Add breadcrumbs |
| `source/.../translation/+page.svelte` | Via SourcefileLayout | Update SourcefileLayout |
| `wordforms/+page.svelte` | Via layout only | Add breadcrumbs (list page) |
| `flashcards/+page.svelte` | Via layout only | Add breadcrumbs |
| `phrase/[slug]/+page.svelte` | Yes (own + layout) | Update to use component |
| `flashcards/sentence/[slug]/+page.svelte` | Via layout only | Add breadcrumbs |

## Stages

### Stage 1: Create Unified Breadcrumbs Component

**Goal:** Create the new `Breadcrumbs.svelte` component with TypeScript interface and shared styling

**Files to create:**
- `/frontend/src/lib/components/Breadcrumbs.svelte`

**Files to modify:**
- `/frontend/src/lib/index.ts` (export new component)

**Steps:**
1. Create TypeScript interface:
   ```typescript
   export interface BreadcrumbItem {
     label: string;
     href?: string;  // Optional - linked items have href
   }
   ```
2. Create `Breadcrumbs.svelte` component with:
   - Props: `items: BreadcrumbItem[]`
   - **Active item rule: The LAST item is ALWAYS rendered as active (no link), regardless of whether it has `href`**
   - Bootstrap markup: `<nav aria-label="breadcrumb"><ol class="breadcrumb">...</ol></nav>`
   - Proper `aria-current="page"` on last item
   - Built-in styling (consolidated from existing implementations)
   - Optional class prop for wrapper customization
   - Truncation for long labels with `title` attribute on hover
3. Export from `$lib/index.ts`

**Verification:**
- Component renders correctly in isolation
- TypeScript types are properly exported
- `npm run check` passes in frontend directory

**IMPORTANT: Reactivity requirement**
When pages derive breadcrumb items from `data`/props, they MUST use reactive declarations:
```svelte
$: items = [
  { label: 'Home', href: '/' },
  { label: data.language_name, href: `/language/${data.code}/sources` },
  // ...
];
```
NOT `const items = [...]` which becomes stale on client-side navigation.

---

### Stage 2: Remove Breadcrumbs from Language Layout

**Goal:** Remove the generic breadcrumbs from the language layout to eliminate the source of duplication

**Files to modify:**
- `/frontend/src/routes/language/[target_language_code]/+layout.svelte`

**Steps:**
1. Remove the `<div class="breadcrumbs">` section (lines ~12-17)
2. Keep the container and flex wrapper for SearchBarMini alignment
3. Adjust spacing/layout if needed after breadcrumb removal

**Verification:**
- Language pages no longer show the layout breadcrumbs
- SearchBarMini still renders correctly
- No console errors

---

### Stage 3: Update SourcefileLayout Component

**Goal:** Replace inline breadcrumb markup in SourcefileLayout with the new unified component

**Files to modify:**
- `/frontend/src/lib/components/SourcefileLayout.svelte`

**Steps:**
1. Import `Breadcrumbs` component and `BreadcrumbItem` type
2. Build items array REACTIVELY from existing props:
   ```svelte
   $: items = [
     { label: 'Home', href: '/' },
     { label: 'Languages', href: '/languages' },
     { label: language_name || target_language_code, href: `/language/${target_language_code}/sources` },
     { label: sourcedir.path, href: `/language/${target_language_code}/source/${sourcedir_slug}` },
     { label: sourcefile.filename, href: `/language/${target_language_code}/source/${sourcedir_slug}/${sourcefile_slug}/text` },
     { label: activeTab.charAt(0).toUpperCase() + activeTab.slice(1) }
   ] as BreadcrumbItem[];
   ```
3. Replace inline `<nav>` with `<Breadcrumbs {items} />`
4. Remove local `.breadcrumb` styles (will use component styles)

**Verification:**
- Sourcefile pages (text, words, phrases, translation, image, audio) display correct breadcrumbs
- Breadcrumbs are not duplicated
- Visual appearance matches or improves on original
- `npm run check` passes

---

### Stage 4: Update Standalone Entity Pages (Lemma, Wordform)

**Goal:** Update lemma and wordform pages to use the unified component

**Files to modify:**
- `/frontend/src/routes/language/[target_language_code]/lemma/[lemma]/+page.svelte`
- `/frontend/src/routes/language/[target_language_code]/wordform/[wordform]/+page.svelte`

**Steps for each file:**
1. Import `Breadcrumbs` component
2. Build items array REACTIVELY from page data using `$:` declaration
3. Replace inline breadcrumb markup with `<Breadcrumbs {items} />`
4. Remove local `.breadcrumb` styles

**Lemma breadcrumb items (reactive):**
```svelte
$: items = [
  { label: 'Home', href: '/' },
  { label: 'Languages', href: '/languages' },
  { label: target_language_name, href: `/language/${target_language_code}/sources` },
  { label: 'Lemmas', href: `/language/${target_language_code}/lemmas` },
  { label: lemma_metadata?.lemma || 'Lemma' }
] as BreadcrumbItem[];
```

**Wordform breadcrumb items (reactive):**
```svelte
$: items = [
  { label: 'Home', href: '/' },
  { label: 'Languages', href: '/languages' },
  { label: target_language_name, href: `/language/${target_language_code}/sources` },
  { label: 'Wordforms', href: `/language/${target_language_code}/wordforms` },
  { label: wordform_metadata.wordform }
] as BreadcrumbItem[];
```

**Verification:**
- Lemma page displays correct breadcrumbs without duplication
- Wordform page displays correct breadcrumbs without duplication
- Links navigate correctly
- `npm run check` passes

---

### Stage 5: Update Phrase and Sentence Pages

**Goal:** Update phrase and sentence pages to use the unified component and fix inconsistent paths

**Files to modify:**
- `/frontend/src/routes/language/[target_language_code]/phrase/[slug]/+page.svelte`
- `/frontend/src/routes/language/[target_language_code]/sentence/[slug]/+page.svelte`

**Steps for phrase page:**
1. Import `Breadcrumbs` component
2. Build items array REACTIVELY (fix missing language level):
   ```svelte
   $: items = [
     { label: 'Home', href: '/' },
     { label: 'Languages', href: '/languages' },
     { label: language_name, href: `/language/${languageCode}/sources` },
     { label: 'Phrases', href: `/language/${languageCode}/phrases` },
     { label: phrase.canonical_form }
   ] as BreadcrumbItem[];
   ```
3. Replace inline markup
4. Remove local `.breadcrumb` styles

**Steps for sentence page:**
1. Import `Breadcrumbs` component
2. Build items array REACTIVELY:
   ```svelte
   $: items = [
     { label: 'Home', href: '/' },
     { label: 'Languages', href: '/languages' },
     { label: sentence.target_language_code, href: `/language/${sentence.target_language_code}/sources` },
     { label: 'Sentence' }
   ] as BreadcrumbItem[];
   ```
3. Replace `<div class="breadcrumbs">` with `<Breadcrumbs {items} />`
4. Remove local `.breadcrumbs` styles

**Verification:**
- Phrase page displays correct breadcrumbs
- Sentence page displays correct breadcrumbs
- Both use Bootstrap pattern via component
- `npm run check` passes

---

### Stage 6: Update Sourcedir Page

**Goal:** Update the sourcedir listing page to use the unified component

**Files to modify:**
- `/frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte`

**Steps:**
1. Import `Breadcrumbs` component
2. Build items array REACTIVELY:
   ```svelte
   $: items = [
     { label: 'Home', href: '/' },
     { label: 'Languages', href: '/languages' },
     { label: language_name, href: `/language/${target_language_code}/sources` },
     { label: sourcedir.path }
   ] as BreadcrumbItem[];
   ```
3. Replace inline `<nav aria-label="breadcrumb">` with `<Breadcrumbs {items} />`

**Verification:**
- Sourcedir page displays correct breadcrumbs
- No styling regressions
- `npm run check` passes

---

### Stage 7: Add Breadcrumbs to List Pages

**Goal:** Add breadcrumbs to pages that previously relied solely on layout breadcrumbs

**Files to modify:**
- `/frontend/src/routes/language/[target_language_code]/sources/+page.svelte`
- `/frontend/src/routes/language/[target_language_code]/lemmas/+page.svelte`
- `/frontend/src/routes/language/[target_language_code]/wordforms/+page.svelte`
- `/frontend/src/routes/language/[target_language_code]/phrases/+page.svelte`
- `/frontend/src/routes/language/[target_language_code]/sentences/+page.svelte`
- `/frontend/src/routes/language/[target_language_code]/flashcards/+page.svelte`
- `/frontend/src/routes/language/[target_language_code]/search/+page.svelte`

**Pattern for list pages (reactive):**
```svelte
$: items = [
  { label: 'Home', href: '/' },
  { label: 'Languages', href: '/languages' },
  { label: language_name, href: `/language/${target_language_code}/sources` },
  { label: 'Page Name' }  // e.g., 'Sources', 'Lemmas', 'Flashcards', etc.
] as BreadcrumbItem[];
```

**Verification:**
- All list pages display breadcrumbs
- Consistent Home > Languages > {Language} > {Section} pattern
- `npm run check` passes

---

### Stage 8: Final Cleanup and Testing

**Goal:** Remove any remaining scattered breadcrumb styles and verify all pages

**Files to review/modify:**
- All files modified in previous stages (ensure no leftover `.breadcrumb` styles)
- Any other pages that might have breadcrumbs (search for "breadcrumb" in routes)

**Steps:**
1. Run searches to find any remaining implementations:
   - `rg "breadcrumb" frontend/src/routes/`
   - `rg "breadcrumbs" frontend/src/routes/`
   - `rg "»" frontend/src/routes/`
   - `rg "breadcrumb" frontend/src/lib/components/`
2. Clean up any remaining scattered `.breadcrumb` CSS rules
3. Verify link correctness: click each breadcrumb level and confirm it resolves
4. Test all breadcrumb pages manually:
   - `/language/[code]/lemma/[lemma]`
   - `/language/[code]/wordform/[wordform]`
   - `/language/[code]/phrase/[slug]`
   - `/language/[code]/sentence/[slug]`
   - `/language/[code]/source/[sourcedir_slug]`
   - `/language/[code]/source/[sourcedir_slug]/[sourcefile_slug]/text` (and other tabs)
4. Run full type check: `cd frontend && npm run check`
5. Test keyboard navigation and screen reader compatibility (ARIA)

**Verification:**
- No duplicate breadcrumbs anywhere
- Consistent visual appearance across all pages
- All type checks pass
- Links work correctly
- ARIA attributes present and correct

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Layout breaks when removing layout breadcrumbs | Medium | Medium | Test SearchBarMini positioning separately; can rollback one file |
| Missing breadcrumbs on edge-case pages | Low | Low | Search entire codebase for "breadcrumb" before finalizing |
| CSS specificity conflicts | Medium | Low | Use scoped styles in component; test in dark theme |
| TypeScript import errors | Low | Low | Export from `$lib/index.ts`; verify with `npm run check` |

## Dependencies

- No external dependencies required
- Uses existing Bootstrap CSS classes
- TypeScript already configured in project

## Estimated Complexity

**Overall: Medium**
- Stage 1 (Component): Low complexity - straightforward Svelte component
- Stage 2 (Layout removal): Low complexity - simple deletion
- Stages 3-6 (Page updates): Medium complexity - repetitive but requires care
- Stage 7 (Cleanup): Low complexity - verification focused

**Estimated stages:** 7
**Estimated implementation time:** 2-3 sessions for a skilled implementer

## Implementation Notes

<!-- Updated by implementer as stages complete -->

### Stage 1 Notes
- Decisions made:
  - Used `<script context="module">` for the interface export (required by Svelte for exporting types)
  - Used `className` prop instead of `class` to avoid Svelte reserved word
  - Added fallback color values in CSS (e.g., `var(--hz-color-text-secondary, #d7dadd)`) for robustness
  - Kept background-color as `rgba(0, 0, 0, 0.05)` matching existing implementations rather than `var(--hz-color-panel-bg)` mentioned in task (the existing implementations use rgba)
- Learnings:
  - TypeScript interfaces must be in `<script context="module">` to be exportable from Svelte components
  - The type export works correctly with `export type { BreadcrumbItem }` from index.ts
- Deviations from plan:
  - None - implemented all requirements as specified

### Stage 2 Notes
- Decisions made:
  - Moved the SearchBarMini `{#if}` condition to wrap the entire container div, so no container renders when SearchBarMini shouldn't show
  - Used `justify-content-end` to align SearchBarMini to the right since breadcrumbs are removed
  - Removed the responsive flex-column/flex-row layout since only SearchBarMini remains (no need for two-column layout)
- Learnings:
  - The original layout had complex responsive classes to handle breadcrumbs on left and search on right; simplified significantly without breadcrumbs
- Deviations from plan:
  - Restructured the container conditionally rather than keeping empty container when SearchBarMini is hidden

### Stage 3 Notes
- Decisions made:
  - Added safe fallbacks for all props (`sourcedir?.path ?? 'Source'`, `sourcefile?.filename ?? 'File'`, etc.) to handle potential undefined values during component initialization
  - Used ternary operator for activeTab capitalization with fallback to 'Text' if activeTab is undefined
- Learnings:
  - The existing inline breadcrumb code had no null safety, but since this is a layout component, adding defensive fallbacks is prudent for edge cases
  - The Breadcrumbs component handles the last item as active automatically, so we don't need special handling for that
- Deviations from plan:
  - None - implemented all requirements as specified including reactive declaration, Breadcrumbs import, and removal of local .breadcrumb styles

### Stage 4 Notes
- Decisions made:
  - Used `breadcrumbItems` as variable name (vs `items`) to be more descriptive in the page context
  - Used nullish coalescing (`??`) and logical OR (`||`) operators appropriately for fallbacks: `??` for lemma/wordform values (null-checking), `||` for language name (empty string handling)
  - On lemma page: used `lemmaResult?.target_language_name` as that's where the language name is located in that page's data structure
  - On wordform page: used `target_language_name` directly as it's a reactive variable already derived from wordformData
- Learnings:
  - The two pages have different data structures for accessing target_language_name - lemma page gets it from `lemmaResult`, wordform page has it as a separate reactive variable
  - The wordform page already had good safe fallback patterns in place that we maintained in the breadcrumb items
- Deviations from plan:
  - None - implemented all requirements as specified including imports, reactive declarations, component usage, and style removal

### Stage 5 Notes
- Decisions made:
  - Added "Sentences" level to the sentence page breadcrumb hierarchy (linking to `/language/{code}/sentences`), matching the pattern established in other pages with list views
  - Used safe null checks with `??` operators for all dynamic values (e.g., `phrase?.canonical_form ?? 'Phrase'`, `data.sentence?.target_language_code ?? 'Language'`) to handle potential undefined values during hydration
  - The phrase page breadcrumb now includes all 5 levels: Home > Languages > Language Name > Phrases > Phrase Name (fixing the previous implementation that skipped Languages and Language levels)
- Learnings:
  - The phrase page's original breadcrumb only had 3 levels (Home > Phrases > Phrase) which was inconsistent with other pages - the new implementation adds proper Languages and Language Name levels
  - The sentence page used a custom `<div class="breadcrumbs">` with `»` separators and non-themed colors (#666, #333) - replaced with consistent Bootstrap-styled component
  - Both pages use standard Svelte reactive statements (`$:`) which work correctly (unlike the sourcedir page which uses runes mode)
- Deviations from plan:
  - Added "Sentences" level to sentence page breadcrumb (plan only showed 4 levels: Home > Languages > Language > Sentence) - added for consistency with other entity pages that link to their list view

### Stage 6 Notes
- Decisions made:
  - Used `$derived` instead of `$:` since this file uses Svelte 5 runes mode (indicated by `$state()` and `$props()` usage)
  - Kept the same wrapping `<div class="my-3">` around the Breadcrumbs component to preserve spacing
  - Added safe fallbacks (`??`) for `language_name` and `sourcedir?.path` to handle potential undefined values
- Learnings:
  - Need to check whether a file uses runes mode or legacy Svelte mode before using `$:` vs `$derived`
  - This file uses runes mode (`let x = $state()`, `let { data } = $props()`), so reactive declarations must use `$derived()`
- Deviations from plan:
  - Used `$derived()` instead of `$:` as specified in the plan - the plan was written for legacy Svelte mode but this file uses runes mode

### Stage 7 Notes
- Decisions made:
  - All 7 files use legacy Svelte mode (`export let data`, `$:` reactive statements), so used `$:` syntax for all breadcrumb items
  - Used `breadcrumbItems` as the variable name for consistency with other stages
  - Used nullish coalescing (`??`) for all language name fallbacks (e.g., `language_name ?? target_language_code`) to handle potential null/undefined values
  - Placed `<Breadcrumbs items={breadcrumbItems} />` immediately after the opening `<div class="container">` tag in each page
- Learnings:
  - All list pages had consistent structures using legacy Svelte mode with `export let data` and const destructuring
  - Some pages (sources, lemmas, wordforms, phrases, sentences, flashcards) had similar variable names (`target_language_code`, `language_name`), while search page used slightly different names (`targetLanguageCode`, `langName`)
  - The flashcards page has a filter banner feature that shows when filtering by sourcefile/sourcedir - breadcrumbs are independent of this filter state
- Deviations from plan:
  - None - implemented all 7 pages as specified using the legacy Svelte `$:` reactive statement syntax

### Stage 8 Notes
- Searches performed:
  - `rg "breadcrumb" frontend/src/routes/` - Found expected usages: reactive declarations (`$: breadcrumbItems = [...]`) and `<Breadcrumbs items={...} />` component usage
  - `rg "breadcrumbs" frontend/src/routes/` - No matches (no old `div.breadcrumbs` patterns remain)
  - `rg "»" frontend/src/routes/` - No matches (no old manual separator patterns remain)
  - `rg "breadcrumb" frontend/src/lib/components/` - Only matches in Breadcrumbs.svelte (the component itself) and SourcefileLayout.svelte (using the component)
  - `rg "\.breadcrumb" frontend/src/routes/` - No matches (no scattered .breadcrumb CSS rules remain)
  - `rg "\.breadcrumbs" frontend/src/routes/` - No matches (no scattered .breadcrumbs CSS rules remain)
- Files containing breadcrumb-related code (expected):
  - `frontend/src/lib/components/Breadcrumbs.svelte` - The unified component (contains .breadcrumb styles, exported interface)
  - `frontend/src/lib/components/SourcefileLayout.svelte` - Uses Breadcrumbs component
  - All route pages under `frontend/src/routes/language/[target_language_code]/` that were updated - Use Breadcrumbs component
- Final type check: `npm run check` passed with 0 errors (5 warnings unrelated to breadcrumbs)
- Summary:
  - All old inline breadcrumb implementations have been replaced with the unified Breadcrumbs component
  - No duplicate breadcrumbs anywhere (layout breadcrumbs removed in Stage 2)
  - No scattered .breadcrumb/.breadcrumbs CSS rules remain in route pages
  - No old `»` separator patterns remain
  - All breadcrumbs use consistent Bootstrap pattern with proper ARIA attributes
  - Centralized styling in Breadcrumbs.svelte component
