# Enhanced Text in Hello Zenno

## Overview

Enhanced text is a key feature of Hello Zenno that transforms plain sentences into interactive language learning experiences. It identifies words in text and makes them clickable with rich hover tooltips that provide additional learning context.

## How Enhanced Text Works

The enhanced text system now uses a structured data approach (preferred) with a legacy HTML fallback:

1. Backend processing identifies recognized words in text and returns structured data with word positions.
2. The `EnhancedText.svelte` component renders the text with interactive word links.
3. Tooltips fetch word data on-demand when users hover, keeping initial page loads fast.
4. Tippy.js displays lemma, translations, etymology, and more.

## User Experience

When viewing enhanced text (e.g., in a Sourcefile text view):

- Desktop: Hover over any highlighted word to see a tooltip with word details.
- Mobile/Tablet: Tap on a word to reveal the tooltip.
- Click: Opens the wordform page in a new tab.
- Loading State: Shows "Loading..." while fetching data.
- Error Handling: Shows "Error loading word information" if something goes wrong.

## Technical Implementation

### Backend API and Data

Structured data is generated in the backend via `create_interactive_word_data()` and returned by endpoints that provide text payloads for sourcefiles and flashcards. The format is:

```json
{
  "text": "Ο σεισμός κομμάτιασε το κτίριο.",
  "recognized_words": [
    { "word": "σεισμός", "start": 2, "end": 8, "lemma": "σεισμός", "translations": ["earthquake"] }
  ]
}
```

Relevant code locations:
- `backend/utils/vocab_llm_utils.py` – `create_interactive_word_data()`
- `backend/utils/sourcefile_utils.py` – builds `recognized_words` for sourcefiles
- `backend/utils/flashcard_utils.py` – builds `recognized_words` for sentences/flashcards

### Frontend Component

The `frontend/src/lib/components/EnhancedText.svelte` component supports two modes:

#### 1. Structured Data Mode (Preferred)
```svelte
<EnhancedText 
  text="Ο σεισμός κομμάτιασε το κτίριο."
  recognizedWords=[
    {
      word: "σεισμός",
      start: 2,
      end: 8,
      lemma: "σεισμός",
      translations: ["earthquake"]
    }
  ]
  target_language_code="el"
/>
```

This is used in pages like:
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/text/+page.svelte`
- `frontend/src/routes/language/[target_language_code]/flashcards/sentence/[slug]/+page.svelte`

#### 2. HTML Mode (Legacy, deprecated)
```svelte
<EnhancedText 
  html='<p>Ο <a href="/lang/el/wordform/σεισμός" class="word-link">σεισμός</a>...</p>'
  target_language_code="el"
/>
```
Prefer the structured data mode; HTML mode is preserved for backward compatibility only.

### Tooltip Content

The tooltip displays:
- Lemma (dictionary form) as a clickable link
- Translations from the wordform
- Inflection type (if available)
- Etymology (if available)
- "View details →" link at the bottom

### Lazy Loading Behavior

1. Initial render shows just the highlighted words.
2. On hover, the tooltip appears with "Loading...".
3. The component fetches data from the word preview API: `/api/lang/word/<target_language_code>/<word>/preview`.
4. The tooltip updates with the fetched content.
5. Subsequent hovers use cached data (short-lived cache).

## Use Cases

### 1. Text Content (Sourcefile pages)
```svelte
<EnhancedText 
  text={sourcefileText}
  recognizedWords={recognizedWords}
  target_language_code="el"
/>
```

### 2. Individual Words (e.g., flashcards showing lemmas)
```svelte
{#each lemma_words as lemma}
  <EnhancedText 
    text={lemma}
    recognizedWords={[{
      word: lemma,
      start: 0,
      end: lemma.length,
      lemma: lemma,
      translations: [] // fetched on hover
    }]}
    target_language_code={language_code}
  />
{/each}
```

## Implementation Notes

- Text is normalized to NFC in backend utilities; frontend rendering assumes pre-normalized input.
- Component handles both touch and mouse interactions; links open in new tabs.
- Tooltip instances are cleaned up on unmount.

## Data Flow (Structured Mode)

1. Backend selects tokens/wordforms and calls `create_interactive_word_data(text, wordforms)`.
2. API response from text endpoints includes `recognized_words` alongside raw text.
3. Frontend pages pass `text` and `recognizedWords` to `EnhancedText.svelte`.
4. Tooltips lazy-load preview data per word on hover.

## Migration from Legacy HTML

- New code should pass structured data; avoid injecting HTML into `{@html}`.
- Keep legacy usage only where migration is not yet practical; mark such spots for cleanup.

## Troubleshooting

- If tooltips show "Loading..." forever, check the preview API route and network calls.
- If words are misaligned, verify `start`/`end` offsets and NFC normalization.
- Ensure `recognizedWords` is non-empty before initializing structured tooltips.