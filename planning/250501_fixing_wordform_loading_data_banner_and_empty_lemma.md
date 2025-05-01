# Fixing wordform "Loading…" banner & empty lemma pages (2025-05-01)

## Goal & context

The production site shows two closely-related problems:

*  Wordform pages sometimes stay on the blue *"Loading Wordform Data…"* banner forever.
*  Lemma pages for missing lemmas render but with empty data (all fields "-").

Root cause analysis (for wordforms) – see commit *rethrow-404*:

* `frontend/src/lib/api.ts#getWordformWithSearch()` used to **swallow 404 responses** (returning the response body instead of throwing).
* `+page.server.ts` therefore believed it had data and passed `null` to the Svelte component ⇒ `isValidData === false` forever ⇒ spinner.
* Patch: return body for 401 (auth required) **but re-throw 404** so the server loader can redirect to `/search/…`.

The lemma page uses a similar pattern (`getLemmaMetadata()`) so it still shows the blank card – we will tackle that separately.

## Principles / key decisions

*  Do not change backend behaviour; just surface HTTP codes correctly.
*  Keep API helpers responsible only for transport-level concerns; let page loaders decide UX.
*  Preserve the existing 401 logic for *auth-required-for-generation*.

## Useful references

| Ref | Why it matters | Priority |
|-----|----------------|----------|
| `frontend/src/lib/api.ts#getWordformWithSearch` | Where the bug & fix live | HIGH |
| `frontend/src/routes/…/wordform/[wordform]/+page.server.ts` | Handles 404 redirect when error is thrown | HIGH |
| `frontend/docs/SEARCH.md` | Describes intended redirect flow | MEDIUM |
| `frontend/docs/AUTH.md` | Confirms 401 handling rules | MEDIUM |
| `utils/word_utils.py#find_or_create_wordform` | Explains backend statuses | LOW |

## Actions

- [x] Patch `getWordformWithSearch()` to re-throw 404 and keep 401 special-case.
- [x] Manual curl check against production confirms 404 is now redirected.
- [ ] Run `npm run check` to ensure no TS errors.
- [ ] Commit fix to git  
  *Message:* *fix(frontend): re-throw 404 in getWordformWithSearch so wordform page redirects instead of hanging*
- [ ] Deploy after confirming staging looks good (handled separately).
- Later:  
  - [ ] Apply the same pattern to lemma loading (`getLemmaMetadata`) so empty lemma pages redirect/search.  
  - [ ] Add Playwright regression test for visiting a non-existent wordform.
