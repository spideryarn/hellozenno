# Enhanced Text in Hello Zenno

THIS PAGE IS OUT OF DATE. The user experience is still the same, but we are shifting to using `create_interactive_word_data()` throughout, instead of `create_interactive_word_links()`. In other words, the backend returns structured data instead of HTML.

see `docs/planning/250412_enhanced_text_transition.md`

## Overview

Enhanced text is a key feature of Hello Zenno that transforms plain sentences into interactive language learning experiences. It identifies words in text and makes them clickable with rich hover tooltips that provide additional learning context.

## How Enhanced Text Works

The enhanced text system has evolved from HTML-based to a structured data approach:

1. **Backend Processing**: The backend identifies recognized words in text and returns structured data with word positions
2. **Frontend Rendering**: The `EnhancedText.svelte` component renders the text with interactive word links
3. **Lazy Loading**: Tooltips fetch word data on-demand when users hover, keeping initial page loads fast
4. **Rich Tooltips**: Uses Tippy.js to display lemma, translations, etymology, and more

## User Experience

When viewing enhanced text (e.g., in a Sourcefile text view):

- **Desktop**: Hover over any highlighted word to see a tooltip with word details
- **Mobile/Tablet**: Tap on a word to reveal the tooltip
- **Click**: Opens the wordform page in a new tab
- **Loading State**: Shows "Loading..." while fetching data
- **Error Handling**: Shows "Error loading word information" if something goes wrong

## Technical Implementation

### Backend API

The word preview API (`/api/lang/word/<target_language_code>/<word>/preview`) returns:

```python
{
    "lemma": str,           # Dictionary form of the word
    "translation": str,     # English translations joined with semicolons
    "etymology": str|None,  # Word origins and cognates
    "inflection_type": str|None  # Grammar information
}
```

The API handles various lookup strategies:
1. Exact match
2. Case-insensitive match
3. Normalized match (without diacritics)

### Frontend Component

The `EnhancedText.svelte` component supports two modes:

#### 1. Structured Data Mode (Preferred)
```svelte
<EnhancedText 
  text="Ο σεισμός κομμάτιασε το κτίριο."
  recognizedWords={[
    {
      word: "σεισμός",
      start: 2,
      end: 8,
      lemma: "σεισμός",
      translations: ["earthquake"]
    },
    // ... more words
  ]}
  target_language_code="el"
/>
```

#### 2. HTML Mode (Legacy)
```svelte
<EnhancedText 
  html='<p>Ο <a href="/lang/el/wordform/σεισμός" class="word-link">σεισμός</a>...</p>'
  target_language_code="el"
/>
```

### Tooltip Content

The tooltip displays:
- **Lemma** (dictionary form) as a clickable link
- **Translations** from the wordform
- **Inflection type** (e.g., "nominative singular")
- **Etymology** if available
- **"View details →"** link at the bottom

### Lazy Loading Behavior

The tooltips are truly lazy-loaded:

1. Initial render shows just the highlighted words
2. On hover, the tooltip appears with "Loading..."
3. The component fetches data from the word preview API
4. The tooltip updates with the fetched content
5. Subsequent hovers use cached data (1-minute cache)

## Use Cases

### 1. Text Content (Original Use)
Used in sourcefile text views to make entire passages interactive:
```svelte
<SourcefileText 
  text={sourcefileText}
  recognized_words={recognizedWords}
  target_language_code="el"
/>
```

### 2. Individual Words (New Use)
Can be used for individual words by treating them as single-word texts:
```svelte
<!-- In flashcards, showing lemmas with tooltips -->
{#each lemma_words as lemma}
  <EnhancedText 
    text={lemma}
    recognizedWords={[{
      word: lemma,
      start: 0,
      end: lemma.length,
      lemma: lemma,
      translations: []  // Fetched on hover
    }]}
    target_language_code={language_code}
  />
{/each}
```

This approach works because:
- Lemmas ARE wordforms (the dictionary form)
- The word preview API handles lemmas correctly
- We get consistent tooltips across the app

## Benefits

1. **Performance**: Only loads data when needed
2. **Consistency**: Same tooltip experience everywhere
3. **Flexibility**: Works for full texts or individual words
4. **Maintainability**: Single component handles all enhanced text needs
5. **Progressive Enhancement**: Falls back gracefully if data loading fails

## Implementation Notes

- Text is normalized to NFC (Unicode Normalization Form C) for consistent handling
- The component handles both touch and mouse interactions
- Tooltips are positioned intelligently to stay on screen
- All links open in new tabs with proper security attributes
- The component cleans up tooltip instances on unmount to prevent memory leaks

## How does it feel to the user?

Let's say I'm viewing the text of a Sourcefile, e.g.

http://localhost:5173/language/el/source/250331-odyssea-2/1000011635-jpg/text

see `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileText.svelte`

That text should include a bunch of hyperlinks for Wordforms that exist in our database (i.e. those that are linked to the Sourcefile with the `SourcefileWordform` model - see `backend/db_models.py`)

For each hyperlink:
- On desktop, I can hover with my mouse and it shows a tooltip (using Tippy.js, displaying the lemma form of the wordform, the translation of the wordform, and the etymology). see 
- On mobile/tablet, I can long-press to reveal this tooltip.
- If I click, it opens the Wordform in a new tab
- While we're waiting for the Flask API to return these details, the tooltip should show "Loading..."
- If there is a problem, should show "Error loading preview" - in this case, provide useful debugging information in the browser error console. (The main cause of this is related to issues with normalisation of accents/diacritics - we try to ensure everything is normalised, but it's still a bit error-prone)
- Each Wordform can be linked to a Lemma (nullable FK). But the Lemma takes time to generate, and so sometimes it's incomplete (see `Lemma.is_complete` field). If the Lemma is incomplete:
  - Show what we have in the tooltip, e.g. probably we at least have the Wordform translation, and probably even the incomplete Lemma has the `Lemma.lemma` field in the target language.
  - If the Lemma is incomplete, send a request from the client in the background to `backend/views/lemma_api.py` `get_lemma_metadata_api()`, because that will call `load_or_generate_lemma_metadata()`, which will generate the rest of the Lemma (so that if we hover again later, it'll be there).

All the API stuff lives in `backend/views/*_api.py`.

## Data Flow for a sentence

1. The `get_detailed_sentence_data` function in `sentence_utils.py` extracts tokens from sentences
2. These tokens are matched against known wordforms in the database
3. The sentence and matching wordforms are passed to `create_interactive_word_links`
4. The API response includes the enhanced text as the `enhanced_sentence_text` field
5. The SvelteKit frontend renders this HTML in the Sentence component:
   ```svelte
   <div class="target-lang-text">
     {@html enhanced_sentence_text || `<p>${sentence.text}</p>`}
   </div>
   ```

## Benefits

1. **Interactive Learning**: Users can hover or click on words they don't know to learn more
2. **Contextual Understanding**: Words are presented in the context of complete sentences
3. **Progressive Enhancement**: If enhanced text fails to load, the raw text is still displayed
4. **Formatting Consistency**: Text is consistently formatted with proper paragraph structure

## Implementation in SvelteKit

In the SvelteKit implementation, enhanced text is:

1. Fetched from the API in `+page.server.ts` files
2. Passed to the page component as a prop
3. Rendered in the Sentence component using `{@html enhanced_sentence_text}` (TODO maybe this should be `EnhancedText.svelte`)
4. Styled with appropriate CSS to match the original application's appearance

## Technical Considerations

- The enhanced text is pre-processed on the server to minimize client-side processing
- Proper HTML sanitization is important when using `{@html}` to prevent XSS attacks
- The CSS for links in enhanced text should be styled consistently with the application

## Next steps

Right now, the hovering is broken. It shows a tooltip, but it's always either "Loading..." or "Error loading preview".

This all used to work before with Jinja/vanilla JS, but we need to rewrite/fix it since moving to SvelteKit. So probably most of the Python API is right or nearly right.

Let's start by getting it to work for a single case where we know we have the full Lemma information for the Wordform, and then gradually handle more complex edgecases (e.g. loading/generating/incomplete).