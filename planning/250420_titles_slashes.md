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

## Useful References

- `frontend/docs/SITE_ORGANISATION.md` (MEDIUM): Overview of routes and page structure.
- `frontend/src/routes/+layout.svelte` (HIGH): Root layout file; needs base title and config import.
- `frontend/src/routes/language/[target_language_code]/+layout.svelte` (HIGH): Language section layout; needs language part of the title.
- `frontend/svelte.config.js` (HIGH): SvelteKit configuration file where `trailingSlash` is set.
- `frontend/src/lib/api.ts` (LOW): Example of how API data (potentially needed for titles) is fetched.
- `rules/WRITING-PLANNING-DOCS-PRINCIPLES.md`, `rules/CODING-PRINCIPLES.md` (LOW): Guiding principles for this task.

## Actions

- [ ] **Stage 1: Setup Config & Base Title**
    - [ ] Create `frontend/src/lib/config.ts` defining `export const SITE_NAME = "Hello Zenno";` and `export const TAGLINE = "AI-powered dictionary & listening practice";`.
    - [ ] Update `frontend/src/routes/+layout.svelte`: Import `SITE_NAME`, `TAGLINE` from `config.ts`. Add `<svelte:head><title>{SITE_NAME} - {TAGLINE}</title></svelte:head>`.

- [ ] **Stage 2: Canonical URLs (Trailing Slashes)**
    - [ ] Check `frontend/svelte.config.js` for the `kit.trailingSlash` setting.
    - [ ] If not present or not set to `'never'`, add/update the config: `kit: { adapter: adapter(), trailingSlash: 'never' }` (ensure adapter config is preserved).
    - [ ] After implementation, test redirection locally by manually navigating to a URL with a trailing slash (e.g., `/languages/`) and verifying it redirects to the non-slash version.

- [ ] **Stage 3: Language Section Base Title**
    - [ ] Ensure `language_name` and `target_language_code` are loaded in `frontend/src/routes/language/[target_language_code]/+layout.load.ts` (or similar `load` function).
    - [ ] Update `frontend/src/routes/language/[target_language_code]/+layout.svelte`: Import `SITE_NAME`. Use the loaded `language_name` (or `target_language_code` as fallback) to set title in `<svelte:head>`, e.g., `<title>{language_name} | {SITE_NAME}</title>`. This title should fully override the base title from the root layout for pages within this section.

- [ ] **Stage 4: Specific Page Titles (Core Examples)**
    - *Note: Each step requires ensuring necessary data (e.g., lemma text, filename) is loaded via a `load` function and passed to the page.* 
    - [ ] **Languages List:** Update `frontend/src/routes/languages/+page.svelte`: Import `SITE_NAME`. Set title `<title>Languages | {SITE_NAME}</title>`.
    - [ ] **Sources List:** Update `frontend/src/routes/language/[target_language_code]/sources/+page.svelte`: Import `SITE_NAME`. Use loaded `language_name`. Set title `<title>Sources | {language_name} | {SITE_NAME}</title>`.
    - [ ] **Lemmas List:** Update `frontend/src/routes/language/[target_language_code]/lemmas/+page.svelte`: Import `SITE_NAME`. Use loaded `language_name`. Set title `<title>Lemmas | {language_name} | {SITE_NAME}</title>`.
    - [ ] **Lemma Detail:** Update `frontend/src/routes/language/[target_language_code]/lemma/[lemma]/+page.svelte`: Import `SITE_NAME`. Use loaded `lemmaData` and `language_name`. Set title `<title>{lemmaData.text} | Lemma | {language_name} | {SITE_NAME}</title>`.
    - [ ] **Source File Detail (Text Tab):** Update `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/text/+page.svelte`: Import `SITE_NAME`. Use loaded `sourcefile_name`, `language_name`. Set title `<title>{sourcefile_name} | Text | {language_name} | {SITE_NAME}</title>`. (Adapt similarly for `words`, `phrases` tabs etc.)
    - [ ] **Profile Page:** Update `frontend/src/routes/auth/profile/+page.svelte`: Import `SITE_NAME`. Set title `<title>Profile | {SITE_NAME}</title>`.
    - [ ] **Login Page:** Update `frontend/src/routes/auth/+page.svelte`: Import `SITE_NAME`. Set title `<title>Login / Sign Up | {SITE_NAME}</title>`.
    - [ ] *(Add more sub-tasks or adjust as we cover other key routes like sentences, phrases, wordforms, search results)*

- [ ] **Stage 5: Redirects**
    - [ ] Create or update `frontend/src/routes/language/[target_language_code]/+page.server.ts` (using `.server.ts` is appropriate for redirects).
    - [ ] Inside its `load` function, add logic: `import { redirect } from '@sveltejs/kit'; export function load({ params, route }) { if (route.id === '/language/[target_language_code]') { throw redirect(307, `/language/${params.target_language_code}/sources`); } // ... potentially other load logic ... }`.
    - [ ] Test the redirect locally by navigating to `/language/[some_code]`.

- [ ] **Stage 6: Title Truncation (Future)**
    - [ ] Define and implement a utility function (e.g., in `src/lib/utils.ts`) `truncate(text: string, maxLength: number): string`.
    - [ ] Apply this function in the title generation for Sentence and Phrase detail pages within their respective `+page.svelte` files.

- [ ] **Stage 7: Review & Refine**
    - [ ] Review all major page types to ensure titles are consistent and informative.
    - [ ] Check handling of edge cases (e.g., missing data for a title).