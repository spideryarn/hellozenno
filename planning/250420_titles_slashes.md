# Page Titles, Canonical URLs, and Redirects Plan

## Goal

Implement consistent, informative page titles, enforce canonical URL structure (no trailing slashes), and add sensible redirects for the SvelteKit frontend, improving SEO and user experience.

## Context

Currently, page titles in the SvelteKit frontend are missing or inconsistent. URLs might resolve both with and without trailing slashes, potentially causing duplicate content issues. Some base routes (like `/language/[code]/`) lack a specific landing page view.

## Principles & Key Decisions

- **Title Structure:** Use a consistent format like `[Specific Content] | [Page Type] | [Language Name] | [Site Name]` for language-specific pages, and simpler structures like `[Page Name] | [Site Name]` or `[Site Name] - [Tagline]` for general pages.
- **Tagline:** Use "AI-powered dictionary & listening practice" (concise and descriptive).
- **Base Title:** Ensure a default title `[Site Name] - [Tagline]` is always present via the root layout.
- **Canonical URLs:** Enforce URLs *without* trailing slashes using SvelteKit's `trailingSlash: 'never'` setting.
- **Redirects:** Implement `/language/[target_language_code]` -> `/language/[target_language_code]/sources` as the default landing page for a language section.
- **Configuration:** Store `SITE_NAME` and `TAGLINE` in a central file (`frontend/src/lib/config.ts`) for reusability and easy updates.
- **Simplicity & Staging:** Implement changes incrementally, starting with configuration, base titles, and slash handling, then moving to specific page titles and redirects. Title truncation for long content (Sentences, Phrases) will be a later stage.
- **Error Handling:** Enforce proper error handling rather than using fallbacks for missing language data in language-specific routes.
- **Data Reuse:** Use SvelteKit's data passing mechanism to reuse data (especially language data) between layouts and pages.

## Useful References

- `frontend/docs/SITE_ORGANISATION.md` (MEDIUM): Overview of routes and page structure.
- `frontend/src/routes/+layout.svelte` (HIGH): Root layout file; needs base title and config import.
- `frontend/src/routes/language/[target_language_code]/+layout.svelte` (HIGH): Language section layout; needs language part of the title.
- `frontend/svelte.config.js` (HIGH): SvelteKit configuration file where `trailingSlash` is set.
- `frontend/src/lib/api.ts` (LOW): Example of how API data (potentially needed for titles) is fetched.
- `rules/WRITING-PLANNING-DOCS-PRINCIPLES.md`, `rules/CODING-PRINCIPLES.md` (LOW): Guiding principles for this task.

## Current State Analysis

- Error pages already exist at both the root level and language-specific level
- Error page titles exist but don't follow the proposed title structure
- The `+layout.server.ts` file for the language section exists and fetches language data
- The language section `+layout.svelte` doesn't currently set a title tag
- `config.ts` file and root layout title is already implemented
- Trailing slash configuration is already set to 'never'

## Actions

- [x] **Stage 1: Setup Config & Base Title**
    - [x] Create `frontend/src/lib/config.ts` defining `export const SITE_NAME = "Hello Zenno";` and `export const TAGLINE = "AI-powered dictionary & listening practice";`.
    - [x] Update `frontend/src/routes/+layout.svelte`: Import `SITE_NAME`, `TAGLINE` from `config.ts`. Add `<svelte:head><title>{SITE_NAME} - {TAGLINE}</title></svelte:head>`.

- [x] **Stage 2: Canonical URLs (Trailing Slashes)**
    - [x] Check `frontend/svelte.config.js` for the `kit.trailingSlash` setting.
    - [x] If not present or not set to `\'never\'`, add/update the config: `kit: { adapter: adapter(), trailingSlash: \'never\' }` (ensure adapter config is preserved).
    - [x] **Correction Note:** The above step was incorrect. `trailingSlash` is a **page option**, not a global `kit` config option in `svelte.config.js`. Adding it there caused Vercel build errors (`Unexpected option config.kit.trailingSlash`). The default SvelteKit behavior is already `\'never\'`, so the incorrect line was removed from `svelte.config.js` instead of adding it elsewhere.
    - [ ] After implementation, test redirection locally by manually navigating to a URL with a trailing slash (e.g., `/languages/`) and verifying it redirects to the non-slash version.

- [ ] **Stage 3: Language Section Base Title**
    - [x] Ensure `language_name` and `target_language_code` are loaded in `+layout.server.ts` (already implemented).
    - [ ] Update `frontend/src/routes/language/[target_language_code]/+layout.svelte`: Import `SITE_NAME`. Use the loaded `language_name` to set title in `<svelte:head>`, e.g., `<title>{language_name} | {SITE_NAME}</title>`. This title should fully override the base title from the root layout for pages within this section.
    - [ ] Improve error handling in `+layout.server.ts` to throw an appropriate error if language data is missing, instead of relying on fallbacks.

- [ ] **Stage 4: Error Page Titles**
    - [ ] Update `frontend/src/routes/+error.svelte`: Import `SITE_NAME` from config. Update title to `<title>{page.status} | {page.error?.message || 'Page Not Found'} | {SITE_NAME}</title>`.
    - [ ] Update `frontend/src/routes/language/[target_language_code]/+error.svelte`: Import `SITE_NAME` from config. Update title to `<title>{page.status} | {page.error?.message || 'Error'} | {languageName || page.params.target_language_code?.toUpperCase()} | {SITE_NAME}</title>`.
    - [ ] Ensure error page UI still indicates the error type/message clearly.

- [ ] **Stage 5: Specific Page Titles (Core Examples)**
    - *Note: Access to `language_name` can be done via `$page.data` in child pages as it's already provided by the parent layout.*
    - [ ] **Languages List:** Update `frontend/src/routes/languages/+page.svelte`: Import `SITE_NAME`. Set title `<title>Languages | {SITE_NAME}</title>`.
    - [ ] **Sources List:** Update `frontend/src/routes/language/[target_language_code]/sources/+page.svelte`: Import `SITE_NAME`. Use loaded `$page.data.language_name`. Set title `<title>Sources | {$page.data.language_name} | {SITE_NAME}</title>`.
    - [ ] **Lemmas List:** Update `frontend/src/routes/language/[target_language_code]/lemmas/+page.svelte`: Import `SITE_NAME`. Use loaded `$page.data.language_name`. Set title `<title>Lemmas | {$page.data.language_name} | {SITE_NAME}</title>`.
    - [ ] **Lemma Detail:** Update `frontend/src/routes/language/[target_language_code]/lemma/[lemma]/+page.svelte`: Import `SITE_NAME`. Use loaded lemma data and `$page.data.language_name`. Set title `<title>{lemmaData.text} | Lemma | {$page.data.language_name} | {SITE_NAME}</title>`.
    - [ ] **Source File Detail (Text Tab):** Update `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/text/+page.svelte`: Import `SITE_NAME`. Use loaded `sourcefile_name` and `$page.data.language_name`. Set title `<title>{sourcefile_name} | Text | {$page.data.language_name} | {SITE_NAME}</title>`. (Adapt similarly for `words`, `phrases` tabs etc.)
    - [ ] **Profile Page:** Update `frontend/src/routes/auth/profile/+page.svelte`: Import `SITE_NAME`. Set title `<title>Profile | {SITE_NAME}</title>`.
    - [ ] **Login Page:** Update `frontend/src/routes/auth/+page.svelte`: Import `SITE_NAME`. Set title `<title>Login / Sign Up | {SITE_NAME}</title>`.
    - [ ] *(Add more sub-tasks or adjust as we cover other key routes like sentences, phrases, wordforms, search results)*

- [ ] **Stage 6: Redirects**
    - [ ] Create or update `frontend/src/routes/language/[target_language_code]/+page.server.ts` (using `.server.ts` is appropriate for redirects).
    - [ ] Inside its `load` function, add logic: `import { redirect } from '@sveltejs/kit'; export function load({ params, route }) { if (route.id === '/language/[target_language_code]') { throw redirect(307, `/language/${params.target_language_code}/sources`); } // ... potentially other load logic ... }`.
    - [ ] Test the redirect locally by navigating to `/language/[some_code]`.

- [ ] **Stage 7: Meta Descriptions & Truncation**
    - [ ] Define and implement a utility function (e.g., in `src/lib/utils.ts`) `truncate(text: string, maxLength: number): string`.
    - [ ] Apply this function in the title generation for Sentence and Phrase detail pages within their respective `+page.svelte` files.
    - [ ] Add meta description tags to enhance SEO, especially useful for long content where titles are truncated.
    - [ ] Create a helper function for consistent meta description formatting.

- [ ] **Stage 8: Review & Refine**
    - [ ] Review all major page types to ensure titles are consistent and informative.
    - [ ] Check handling of edge cases (e.g., missing data for a title).
    - [ ] Verify that errors are thrown appropriately rather than using fallbacks when required data is missing.

- [ ] **Stage 9: Future Enhancements (Optional)**
    - [ ] Add OpenGraph/Twitter meta tags for improved social media sharing.
    - [ ] Implement structured data (JSON-LD) for rich results in search engines.
    - [ ] Consider implementing breadcrumb navigation to complement the title structure.

## Approach to Layout Loading Issues

Given the observed issues with `+layout.load.ts`, here are the proposed solutions:

1. **Continue Using +layout.server.ts:** The existing `+layout.server.ts` is already working to fetch language data. We should keep this approach since it's already implemented.

2. **Pass Data to Child Pages:** Child pages should access language data via `$page.data` as it's automatically passed down from the parent layout.

3. **Error Handling:** Instead of the current fallback to language code when language_name fetch fails, we should improve error handling to:
   - Log the error properly
   - Throw a more specific error that can be caught by the error boundary
   - Consider using SvelteKit's `error()` function: `throw error(404, 'Language not found');`

4. **Proper Typing:** Ensure all data interfaces are properly typed in `./$types.ts` files to avoid TypeScript errors.

This approach keeps changes minimal while improving the implementation quality.