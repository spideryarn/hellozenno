# Tidy Frontend Logs (`logs/frontend.log`)

## Goal & Context

- **Goal:** Reduce noise and fix actionable warnings in `logs/frontend.log` to make development feedback cleaner and more focused.
- **Context:** The frontend development server logs (`logs/frontend.log`) contain numerous warnings and verbose output, making it difficult to spot important issues. This plan aims to address the agreed-upon items to improve log clarity.

## Principles & Key Decisions

- Follow `@../rules/CODING-PRINCIPLES.md`.
- Prioritize fixing warnings that affect code quality, future compatibility, and accessibility.
- **Address:**
    - Svelte deprecation warnings (`on:event` -> `onevent=`).
    - Svelte accessibility warnings (A11y: `autofocus`, clickable divs without roles/keyboard handlers).
    - Unused CSS selectors reported by `SVELTE_WARNINGS_STRICT=true`.
    - Unused component export properties (`export let`).
- **Ignore for now:**
    - Supabase auth warnings (`getSession` vs `getUser` - potentially covered in `250421_getSession_Supabase_auth_warnings.md`).
    - Node.js deprecation warning (`punycode`).
    - Verbose logging related to wordform data fetching.
    - Modifying the `SVELTE_WARNINGS_STRICT` setting in `scripts/local/run_frontend.sh`.

## Useful References

- `logs/frontend.log`: The target log file showing the warnings. (HIGH)
- `scripts/local/run_frontend.sh`: Script that runs the dev server and enables strict warnings. (LOW)
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte`: Contains many `on:event` deprecations. (HIGH)
- `frontend/src/lib/components/DescriptionFormatted.svelte`: Contains `autofocus` warning. (HIGH)
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileHeader.svelte`: Contains A11y warnings for clickable divs and unused CSS. (HIGH)
- `frontend/src/lib/components/LemmaContent.svelte`: Contains unused CSS. (MEDIUM)
- `frontend/src/lib/components/SourcefileAudio.svelte`: Contains unused export prop warning. (MEDIUM)
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/NavButtons.svelte`: Contains unused export prop warning. (MEDIUM)
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileTranslation.svelte`: Contains unused export prop warning. (MEDIUM)

## Actions

- [ ] **Stage 1: Fix Svelte Deprecations (`on:event`)**
    - [ ] Find all instances of `on:click`, `on:change`, `on:keydown` etc. directives flagged in the logs.
    - [ ] Replace them with the modern attribute syntax: `onclick=`, `onchange=`, `onkeydown=` etc.
    - [ ] Focus primarily on `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte`.
    - [ ] Check `logs/frontend.log` again to ensure these specific deprecation warnings are gone.

- [ ] **Stage 2: Fix Svelte Accessibility (A11y) Issues**
    - [x] Suppress `autofocus` warning in `frontend/src/lib/components/DescriptionFormatted.svelte`.
    - [x] Simplify progress display in `SourcefileHeader.svelte` to remove clickable div, resolving A11y warnings.
    - [ ] Check `logs/frontend.log` again to ensure these specific A11y warnings are gone.

- [ ] **Stage 3: Fix Unused CSS Selectors**
    - [ ] Identify components flagged with unused CSS selectors (e.g., `LemmaContent.svelte`, `SourcefileHeader.svelte`).
    - [ ] For each unused selector, either:
        - Remove the CSS rule if it's genuinely unused.
        - Ensure the corresponding HTML element exists and matches the selector if the CSS *should* be used.
    - [ ] Check `logs/frontend.log` again to ensure these specific unused CSS warnings are gone.

- [ ] **Stage 4: Fix Unused Export Properties (`export let`)**
    - [ ] Identify components flagged with unused `export let` properties (e.g., `SourcefileAudio.svelte`, `NavButtons.svelte`, `SourcefileTranslation.svelte`).
    - [ ] For each unused export:
        - If the property is intended only for external reference via `bind:this`, change it to `export const propertyName`.
        - If the property is truly unused (not passed in, not bound, not used internally), remove the `export let propertyName;` line.
    - [ ] Check `logs/frontend.log` again to ensure these specific unused export warnings are gone.

- [ ] **Final Review:**
    - [ ] Restart the frontend server.
    - [ ] Briefly navigate the app.
    - [ ] Check `logs/frontend.log` one last time to confirm the targeted warnings and noise have been significantly reduced.

## Appendix

N/A

