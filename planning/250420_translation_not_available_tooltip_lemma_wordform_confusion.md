# Planning: Tooltip Link Confusion (Lemma vs. Wordform)

## Goal, context

**Goal:** Investigate and resolve the issue where clicking the "View full details" link within the `EnhancedText.svelte` component's tooltip sometimes leads to a lemma page (`/language/.../lemma/...`) when the user might expect a wordform page (`/language/.../wordform/...`), especially when the tooltip initially shows "(translation not available)".

**Context:**
- The `EnhancedText.svelte` component renders interactive text where words are hoverable/clickable.
- Hovering (or clicking on touch devices) triggers a tooltip that attempts to fetch word preview data (lemma, translation, etc.) from the API (`/api/lang/word/{lang}/{word}/preview`).
- If the API call fails or doesn't return sufficient data (e.g., no translation), the tooltip displays fallback content like "(translation not available)".
- The tooltip contains a "View full details →" link.
- **Problem:** The clickable word *itself* correctly links to the wordform page. However, the "View full details →" link *inside the tooltip* is currently hardcoded to always link to the lemma page. In fallback/error scenarios, it uses the original word text as the lemma identifier in the URL, leading to the incorrect page type being displayed.

## Principles, key decisions

*(No specific decisions made yet)*

## Useful references

- `frontend/src/lib/components/EnhancedText.svelte`: (HIGH) The Svelte component responsible for rendering interactive text and tooltips. Contains the logic for fetching data (`fetchWordData`) and creating tooltip content (`createTooltipContent`, `createErrorContent`).
- `frontend/src/lib/types.ts -> WordPreview`: (MEDIUM) The expected structure of the data returned by the word preview API.
- `backend/views/wordform_api.py -> get_wordform_metadata_api()`: (MEDIUM) The likely Flask API endpoint that serves the `/api/lang/word/{lang}/{word}/preview` route. Understanding its behavior, especially in error/fallback cases, is important.

## Actions

- [ ] **Discuss Desired Behavior:** Decide what the "View full details →" link in the tooltip *should* do:
    - Option A: Always link to the lemma page (current behavior, but potentially confusing).
    - Option B: Link to the wordform page if the API call fails or lacks data, and lemma page otherwise.
    - Option C: Always link to the wordform page.
    - Option D: Include *both* a lemma link and a wordform link in the tooltip.
- [ ] **Implement Fix:** Based on the decision, modify the `createTooltipContent` and `createErrorContent` functions in `EnhancedText.svelte` to generate the correct link(s).
- [ ] **Test:** Verify the fix across different scenarios:
    - Successful API call with full data.
    - Successful API call with missing translation.
    - Failed API call (simulate network error or 500).
    - Words that are lemmas vs. non-lemma wordforms.
    - Test on desktop (hover) and mobile (click).

## Appendix

*(None yet)*
