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

- Root layout is using the correct title format with `SITE_NAME - TAGLINE`
- Error pages already exist at both the root level and language-specific level
- Error page titles have been updated to use the standardized title format with pipe separators
- The `+layout.server.ts` file for the language section exists and fetches language data
- The language section `+layout.svelte` has been updated to set an appropriate title tag
- `config.ts` file exists with `SITE_NAME` and `TAGLINE` constants
- Trailing slash configuration is already set to 'never'
- The `get_language_name` function has been improved with proper error handling
- A language section redirect to `/sources` is implemented
- A `truncate` utility function has been added for title truncation

## Actions

- [x] **Stage 1: Setup Config & Base Title**
    - [x] Create `frontend/src/lib/config.ts` defining `export const SITE_NAME = "Hello Zenno";` and `export const TAGLINE = "AI-powered dictionary & listening practice";`.
    - [x] Update `frontend/src/routes/+layout.svelte`: Import `SITE_NAME`, `TAGLINE` from `config.ts`. Add `<svelte:head><title>{SITE_NAME} - {TAGLINE}</title></svelte:head>`.

- [x] **Stage 2: Canonical URLs (Trailing Slashes)**
    - [x] Check `frontend/svelte.config.js` for the `kit.trailingSlash` setting.
    - [x] If not present or not set to `\'never\'`, add/update the config: `kit: { adapter: adapter(), trailingSlash: \'never\' }` (ensure adapter config is preserved).
    - [x] **Correction Note:** The above step was incorrect. `trailingSlash` is a **page option**, not a global `kit` config option in `svelte.config.js`. Adding it there caused Vercel build errors (`Unexpected option config.kit.trailingSlash`). The default SvelteKit behavior is already `\'never\'`, so the incorrect line was removed from `svelte.config.js` instead of adding it elsewhere.
    - [ ] After implementation, test redirection locally by manually navigating to a URL with a trailing slash (e.g., `/languages/`) and verifying it redirects to the non-slash version.

- [x] **Stage 3: Language Section Base Title**
    - [x] Ensure `language_name` and `target_language_code` are loaded in `+layout.server.ts` (already implemented).
    - [x] Update `frontend/src/routes/language/[target_language_code]/+layout.svelte`: Import `SITE_NAME`. Use the loaded `language_name` to set title in `<svelte:head>`, e.g., `<title>{language_name} | {SITE_NAME}</title>`. This title should fully override the base title from the root layout for pages within this section.
    - [x] Improve error handling in `get_language_name` function to throw an appropriate error if language data is missing, instead of relying on fallbacks.

- [x] **Stage 4: Error Page Titles**
    - [x] Update `frontend/src/routes/+error.svelte`: Import `SITE_NAME` from config. Update title to `<title>{page.status} | {page.error?.message || 'Page Not Found'} | {SITE_NAME}</title>`.
    - [x] Update `frontend/src/routes/language/[target_language_code]/+error.svelte`: Import `SITE_NAME` from config. Update title to `<title>{page.status} | {page.error?.message || 'Error'} | {languageName || page.params.target_language_code?.toUpperCase()} | {SITE_NAME}</title>`.
    - [x] Ensure error page UI still indicates the error type/message clearly.

- [x] **Stage 5: Specific Page Titles (Core Examples)**
    - *Note: Access to `language_name` can be done via `$page.data` in child pages as it's already provided by the parent layout.*
    - [x] **Languages List:** Update `frontend/src/routes/languages/+page.svelte`: Import `SITE_NAME`. Set title `<title>Languages | {SITE_NAME}</title>`.
    - [x] **Sources List:** Update `frontend/src/routes/language/[target_language_code]/sources/+page.svelte`: Import `SITE_NAME`. Use loaded `languageName`. Set title `<title>Sources | {languageName} | {SITE_NAME}</title>`.
    - [x] **Lemmas List:** Update `frontend/src/routes/language/[target_language_code]/lemmas/+page.svelte`: Import `SITE_NAME`. Use loaded `data.language_name`. Set title `<title>Lemmas | {data.language_name} | {SITE_NAME}</title>`.
    - [x] **Lemma Detail:** Update `frontend/src/routes/language/[target_language_code]/lemma/[lemma]/+page.svelte`: Import `SITE_NAME` and `truncate`. Use loaded lemma data and language name. Set title `<title>{truncate(lemma_metadata?.lemma || lemmaParam, 30)} | Lemma | {lemmaResult?.target_language_name || target_language_code} | {SITE_NAME}</title>`.
    - [x] **Source File Detail (Text Tab):** Update `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/text/+page.svelte`: Import `SITE_NAME` and `truncate`. Use loaded `sourcefile.filename` and `language_name`. Set title `<title>{truncate(sourcefile.filename, 30)} | Text | {language_name} | {SITE_NAME}</title>`. (Similarly updated for `words`, `phrases`, `image`, `audio`, and `translation` tabs)
    - [x] **Profile Page:** Update `frontend/src/routes/auth/profile/+page.svelte`: Import `SITE_NAME`. Set title `<title>Profile | {SITE_NAME}</title>`.
    - [x] **Login Page:** Update `frontend/src/routes/auth/+page.svelte`: Import `SITE_NAME`. Set title `<title>Login / Sign Up | {SITE_NAME}</title>`.
    - [x] **Wordform Detail:** Updated `frontend/src/routes/language/[target_language_code]/wordform/[wordform]/+page.svelte`: Added title `<title>{truncate(wordform_metadata?.wordform, 30)} | Wordform | {target_language_name} | {SITE_NAME}</title>` and meta description.
    - [x] **Wordforms List:** Updated `frontend/src/routes/language/[target_language_code]/wordforms/+page.svelte`: Added title `<title>Wordforms | {language_name} | {SITE_NAME}</title>`.
    - [x] **Sentences List:** Updated `frontend/src/routes/language/[target_language_code]/sentences/+page.svelte`: Added title `<title>Sentences | {language_name} | {SITE_NAME}</title>`.
    - [x] **Sentence Detail:** Updated `frontend/src/routes/language/[target_language_code]/sentence/[slug]/+page.svelte`: Added title `<title>{truncate(sentence.text, 30)} | Sentence | {target_language_code} | {SITE_NAME}</title>` and meta description.
    - [x] **Phrases List:** Updated `frontend/src/routes/language/[target_language_code]/phrases/+page.svelte`: Added title `<title>Phrases | {language_name} | {SITE_NAME}</title>`.
    - [x] **Phrase Detail:** Updated `frontend/src/routes/language/[target_language_code]/phrase/[slug]/+page.svelte`: Added title `<title>{truncate(phrase.canonical_form, 30)} | Phrase | {language_name} | {SITE_NAME}</title>` and meta description.
    - [x] **Search Page:** Updated `frontend/src/routes/language/[target_language_code]/search/+page.svelte`: Added title `<title>\"${truncate(query, 20)}\" | Search | ${langName} | ${SITE_NAME}</title>`.
    - [x] **Flashcards:** Updated `frontend/src/routes/language/[target_language_code]/flashcards/+page.svelte`: Added title `<title>Flashcards | {language_name} | {SITE_NAME}</title>`.

- [x] **Stage 6: Redirects**
    - [x] Create or update `frontend/src/routes/language/[target_language_code]/+page.server.ts` (using `.server.ts` is appropriate for redirects).
    - [x] Inside its `load` function, add logic: `import { redirect } from '@sveltejs/kit'; export function load({ params, route }) { throw redirect(307, `/language/${params.target_language_code}/sources`); }`.
    - [ ] Test the redirect locally by navigating to `/language/[some_code]`.

- [x] **Stage 7: Meta Descriptions & Truncation**
    - [x] Define and implement a utility function (e.g., in `src/lib/utils.ts`) `truncate(text: string, maxLength: number): string`.
    - [x] Apply this function in the title generation for the Lemma detail page (and other pages as needed).
    - [x] Add meta description tag to Lemma detail page as an example: `<meta name="description" content="{generateMetaDescription(...)}">`.
    - [x] Create a helper function for consistent meta description formatting (`generateMetaDescription()`).

- [ ] **Stage 8: Review & Refine**
    - [ ] Review all major page types to ensure titles are consistent and informative.
    - [ ] Check handling of edge cases (e.g., missing data for a title).
    - [ ] Verify that errors are thrown appropriately rather than using fallbacks when required data is missing.

- [ ] **Stage 9: Future Enhancements (Optional)**
    - [ ] Add OpenGraph/Twitter meta tags for improved social media sharing.

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

## Progress Summary (Updated April 20, 2025)

Completed:
- Base title configuration is set up and working
- Trailing slash handling is properly configured
- Language section base title is implemented
- Error page titles are standardized using the proper format
- Error handling is improved in the language name fetching
- Language section redirect to sources is implemented
- Truncate utility function is added for long content in titles
- Core page titles implemented across all main sections:
  - Languages page
  - Sources list
  - Lemmas list and detail
  - Wordforms list and detail
  - Sentences list and detail
  - Phrases list and detail
  - Sourcefile detail views (text, words, phrases, image, audio, translation)
  - Search pages
  - Flashcards pages
  - Authentication pages (login/profile)
- Created `generateMetaDescription()` helper function for SEO descriptions
- Added meta description tags to:
  - Lemma detail page
  - Sourcefile text tab
  - Wordform detail page
  - Sentence detail page
  - Phrase detail page

Next Steps:
- Test all implemented features:
  - Trailing slash redirect (navigate to a URL with trailing slash and verify it redirects)
  - Language redirect (navigate to `/language/[code]` and verify it redirects to `/language/[code]/sources`)
- Check for missing titles on any edge case pages
- Complete review and refinement (Stage 8)
- Consider implementing OpenGraph tags for social sharing (optional Stage 9)