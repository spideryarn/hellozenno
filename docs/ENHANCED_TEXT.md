# Enhanced Text in Hello Zenno

## Overview

Enhanced text is a key feature of Hello Zenno that transforms plain sentences into interactive language learning experiences. It uses HTML formatting and augments sentences with clickable word links that provide additional learning context.

## How Enhanced Text Works

The enhanced text system processes raw text sentences through several steps:

1. **Word Recognition**: The application analyzes sentences to identify known words and their lemmas (base forms)
2. **Link Generation**: Recognized words are converted into HTML links that connect to corresponding lemma pages
3. **Formatting**: The text is formatted with proper paragraph structure, line breaks, and indentation
4. **Display**: The enhanced text is rendered as HTML in the SvelteKit frontend using Svelte's `{@html}` directive

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
3. Wraps matched words with HTML links: `<a href="/lang/{language_code}/lemma/{lemma}" class="word-link">{word}</a>`
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
 Μπορείς να μεταφέρεις τις φωτογραφίες από την <a href="/lang/el/lemma/κάρτα μνήμης" class="word-link">κάρτα μνήμης</a> στον<br>
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

1. **Interactive Learning**: Users can click on words they don't know to learn more
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
