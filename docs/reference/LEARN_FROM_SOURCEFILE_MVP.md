# Learn from Sourcefile (MVP)

## Introduction

A focused learning flow for a single sourcefile: show priority words with etymologies, then practice via generated audio sentence flashcards. Sentences and audio are persisted and reused on subsequent visits for the same sourcefile.

## See also

- `frontend/docs/FRONTEND_LEARN_FROM_SOURCEFILE.md` – UI/UX overview and behavior specifics
- `docs/planning/250915a_sourcefile_learn_flow_mvp.md` – planning notes, stages, and future work
- `backend/views/learn_api.py` – summary and generation endpoints for Learn
- `backend/docs/DATABASE.md` – models relevant to lemmas, sentences, and audio
- `backend/prompt_templates/generate_sentence_flashcards.jinja` – sentence generation prompt
- `backend/prompt_templates/metadata_for_lemma.jinja` – lemma metadata prompt
- `frontend/docs/PAGE_TITLES_SEO.md` – page title conventions used in the Learn page

## Testing

End-to-end and CLI testing for the MVP flow.

- Playwright (dev server)

  1. Ensure dev servers are running (frontend :5173, backend :3000)
  2. Optionally export local test credentials (see Local Test Users):
     ```
     export PLAYWRIGHT_TEST_EMAIL=testing@hellozenno.com
     export PLAYWRIGHT_TEST_PASSWORD=hello123
     ```
  3. Run the Learn e2e test against the dev server:
     ```
     cd frontend
     npx playwright test -c playwright.dev.config.ts e2e/learn_flow.test.ts
     ```

  Code references:
  ```1:12:frontend/playwright.dev.config.ts
  import { defineConfig } from '@playwright/test';

  // Run e2e tests against an already-running dev server on :5173
  export default defineConfig({
    use: {
      baseURL: 'http://localhost:5173',
    },
    testDir: 'e2e',
  });
  ```

  ```1:32:frontend/e2e/learn_flow.test.ts
  import { test, expect } from '@playwright/test';

  async function loginIfNeeded(page) {
    const email = process.env.PLAYWRIGHT_TEST_EMAIL;
    const password = process.env.PLAYWRIGHT_TEST_PASSWORD;
    if (!email || !password) return; // allow anonymous run

    await page.goto('/auth');
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.getByRole('button', { name: /login/i }).click();
  }
```

- Manual browser smoke

  1. Open `http://localhost:5173/language/el/source/251013/1000015419-word-matching-jpg/learn`.
  2. Wait for the "Practice ready" chip or click "Start practice" when enabled.
  3. In the Practice card, click "Show sentence", then "Show translation", then "Next card".

  Notes:
  - Anonymous users only get reused sentences. If none exist yet for this sourcefile, no deck may appear until you log in.
  - Logged-in users can generate new sentences; the heading "Practice" confirms a deck is loaded.

- CLI (backend endpoints)

  Summary:
  ```bash
  python scripts/local/learn_cli.py summary el 251013 1000015419-word-matching-jpg
  ```

  Generate (anonymous returns reused-only with 401 + flag; with token performs generation):
  ```bash
  export AUTH_BEARER="<SUPABASE_JWT>"
  python scripts/local/learn_cli.py generate el 251013 1000015419-word-matching-jpg --lemmas βιβλίο,μουσική --num 3 --level A1
  ```

  Code reference:
  ```1:24:scripts/local/learn_cli.py
  #!/usr/bin/env python3
  """
  Quick CLI to exercise Learn endpoints on a running dev backend.
  """
  import argparse
  import json
  import os
  ```

## Architecture and data flow

- Frontend route: `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte`
- Entry point button on the sourcefile page:
```601:603:frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileHeader.svelte
<a href={learnUrl} class="button">
  Learn (MVP)
</a>
```
- Type-safe API routes used by the frontend:
```214:218:frontend/src/lib/generated/routes.ts
  LEARN_API_LEARN_SOURCEFILE_SUMMARY_API: "/api/lang/learn/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/summary",
  LEARN_API_LEARN_SOURCEFILE_GENERATE_API: "/api/lang/learn/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/generate",
```
- API helper used to call backend from the Learn page:
```26:33:frontend/src/lib/api.ts
export function getApiUrl<T extends RouteName>(
    routeName: T,
    params: RouteParams[T],
): string {
    const routePath = resolveRoute(routeName, params);
    return `${API_BASE_URL}${routePath}`;
}
```

### Backend endpoints

- Ranked-lemmas summary (GET):
```47:58:backend/views/learn_api.py
@learn_api_bp.route(
    "/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/summary",
    methods=["GET"],
)
@api_auth_optional
def learn_sourcefile_summary_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Return ranked lemma summaries for the given sourcefile.
    Response shape: { lemmas: [...], meta: { durations, partial?, counts? } }
    """
```

- Generate sentences + audio, persist and reuse (POST):
```167:176:backend/views/learn_api.py
@learn_api_bp.route(
    "/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/generate",
    methods=["POST"],
)
@api_auth_optional
def learn_sourcefile_generate_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Generate/persist a batch of sentences and audio for provided lemmas."""
```

Key behavior:
- Summary computes a difficulty score = (1 - guessability) + (1 - commonality) and returns top-K lemmas.
- Summary uses bulk prefetch of lemma metadata and a time budget; if exceeded, returns partial results with defaults for the remainder and sets `meta.partial=true` plus `meta.counts`.
- Generation reuses existing `Sentence` rows for the same sourcefile, then tops up via LLM; audio variants are ensured.
- Responses include durations for observability. No caching is used in this MVP.

### Frontend behavior highlights

- Page title follows the standard pattern:
```624:628:frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte
<svelte:head>
  <title>{truncate(sourcefileFilename || sourcefile_slug, 30)} | Learn | {language_name} | {SITE_NAME}</title>
  <meta name="robots" content="noindex" />
  <meta name="description" content="Priority words and generated audio flashcards" />
</svelte:head>
```

- Summary and warming flow uses the typed router and auth-aware API client:
```126:139:frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte
const js = await apiFetch({
  supabaseClient: ($page.data as any).supabase ?? null,
  routeName: RouteName.LEARN_API_LEARN_SOURCEFILE_SUMMARY_API,
  params: { target_language_code, sourcedir_slug, sourcefile_slug },
  options: { method: 'GET' },
  searchParams: { top: settingTopK },
  timeoutMs: 60000,
});
```

- Progressive improvement (authenticated): each load fills more lemma metadata within a time budget; subsequent loads return faster, more complete summaries and prepared decks.

- Practice generation and reuse:
```216:233:frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/learn/+page.svelte
const js = await apiFetch({
  supabaseClient: ($page.data as any).supabase ?? null,
  routeName: RouteName.LEARN_API_LEARN_SOURCEFILE_GENERATE_API,
  params: { target_language_code, sourcedir_slug, sourcefile_slug },
  options: {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  },
  timeoutMs: 120000,
});
```

### Configuration and defaults

- Config constants (used by the Learn page):
```26:39:frontend/src/lib/config.ts
export const SITE_NAME = "Hello Zenno";
export const TAGLINE = "AI-powered dictionary & listening practice";
export const LEARN_DEFAULT_TOP_WORDS = 10;
export const LEARN_DEFAULT_NUM_CARDS = 10;
export const LEARN_DEFAULT_CEFR: string = '';
```

- Utility helper for titles/descriptions:
```38:46:frontend/src/lib/utils.ts
export function truncate(text: string, maxLength: number = 50): string {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 1).trim() + '…';
}
```

## Limitations

- No batch/session object yet; exact replay is deferred.
- Audio variants are ensured per sentence; selection is currently first-variant simple.

## Future work

- Batch/session tracking and integration with global flashcards deck
- Server-side warming and caching strategies
- External object storage for audio at scale
- Adaptive continuation based on in-session analytics
