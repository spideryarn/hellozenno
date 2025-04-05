# Enhanced Text in Hello Zenno

## Overview

Enhanced text is a key feature of Hello Zenno that transforms plain sentences into interactive language learning experiences. It uses HTML formatting and augments sentences with hoverable & clickable word links that provide additional learning context.

## How Enhanced Text Works

The enhanced text system processes raw text sentences through several steps:

1. **Word Recognition**: The application analyzes sentences to identify known words and their forms
2. **Link Generation**: Recognized words are converted into HTML links that connect to corresponding wordform pages
3. **Formatting**: The text is formatted with proper paragraph structure, line breaks, and indentation
4. **Display**: The enhanced text is rendered as HTML in the SvelteKit frontend using Svelte's `{@html}` directive. (HANG ON maybe this should/does use the `EnhancedText.svelte` component???)


## How does it feel to the user?

Let's say I'm viewing the text of a Sourcefile, e.g.

http://localhost:5173/language/el/source/250331-odyssea-2/1000011635-jpg/text

see `frontend/src/routes/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileText.svelte`

That text should include a bunch of hyperlinks for Wordforms that exist in our database (i.e. those that are linked to the Sourcefile with the `SourcefileWordform` model - see `backend/db_models.py`)

For each hyperlink:
- I can hover with my mouse and it shows a tooltip (with Tippy.js, displaying the lemma form of the wordform, the translation of the wordform, and the etymology).
- On mobile/tablet, I can long-press to reveal this tooltip.
- If I click, it opens the Wordform in a new tab
- While we're waiting for the Flask API to return these details, the tooltip should show "Loading..."
- If there is a problem, should show "Error loading preview" - in this case, provide useful debugging information in the browser error console. (The main cause of this is related to issues with normalisation of accents/diacritics - we try to ensure everything is normalised, but it's still a bit error-prone)
- Each Wordform should be linked to a Lemma (I think!?). But the Lemma takes time to generate, and so sometimes it's incomplete (see `Lemma.is_complete` field).
  - If the Lemma is incomplete, show what we have, e.g. probably we at least have the Wordform translation, and probably even the incomplete Lemma has the `Lemma.lemma` field in the target language.
  - If the Lemma is incomplete, send a request from the client in the background to `backend/api/lemma_api.py` `get_lemma_metadata_api()`, because that will call `load_or_generate_lemma_metadata()`, which will generate the rest of the Lemma (so that if we hover again later, it'll be there).

All the API stuff lives in `backend/api/*_api.py`.


## Technical Implementation

The enhanced text is generated on the backend via the `create_interactive_word_links` function in `utils/vocab_llm_utils.py`:

```python
def create_interactive_word_links(
    text: str,
    wordforms: list[dict],
    target_language_code: str,
) -> tuple[str, set[str]]:
    """Enhance the input text by wrapping tricky wordforms with HTML links."""
    # Implementation details...
```

The function performs the following operations:

1. Normalizes text for consistent pattern matching
2. Identifies wordforms that appear in the text
3. Wraps matched words with HTML links: `<a href="/lang/{language_code}/wordform/{wordform}" class="word-link">{word}</a>`
4. Formats paragraphs with `<p>` tags and proper indentation
5. Wraps long lines at approximately 65 characters with `<br>` tags

## Example Transformation

Original text:
```
Μπορείς να μεταφέρεις τις φωτογραφίες από την κάρτα μνήμης στον υπολογιστή;
```

Enhanced text (simplified):
```html
<p>
 Μπορείς να μεταφέρεις τις φωτογραφίες από την <a href="/lang/el/wordform/κάρτα μνήμης" class="word-link">κάρτα μνήμης</a> στον<br>
 υπολογιστή;
</p>
```

## Data Flow

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
3. Rendered in the Sentence component using `{@html enhanced_sentence_text}`
4. Styled with appropriate CSS to match the original application's appearance

## Technical Considerations

- The enhanced text is pre-processed on the server to minimize client-side processing
- Proper HTML sanitization is important when using `{@html}` to prevent XSS attacks
- The CSS for links in enhanced text should be styled consistently with the application

## Future Enhancements

Possible improvements to the enhanced text feature:

1. Client-side highlighting of words based on difficulty level
2. Hoverable tooltips with quick translations
3. Color-coding words by part of speech or frequency
4. Support for multiple languages beyond Greek
5. Remembering which words a user has clicked for personalized learning
