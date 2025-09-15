# Flashcards for sentences

## Goal, core interaction flow

Visit `/lang/el/sentences`

Then press the "Practice with Flashcards" button

This takes you to `/lang/el/flashcards`

Press the "Start Flashcards" button (or press ENTER)

This takes you to `/lang/el/flashcards/sentence/<sentence_slug>`

### Filtering by Source

You can access flashcards filtered to specific content:

1. From a sourcefile: `/lang/el/flashcards?sourcefile=<sourcefile_slug>`
   - Shows flashcards for sentences containing lemmas from that specific file
   - Available from the sourcefile inspection page

2. From a sourcedir: `/lang/el/flashcards?sourcedir=<sourcedir_slug>`
   - Shows flashcards for sentences containing lemmas from any file in that directory
   - Combines vocabulary from all files in the directory
   - Randomly selects from qualifying sentences
   - Available from the sourcedir's files listing page

The flashcard interaction remains the same in all cases.

1) Stage 1: Audio autoplays immediately
   - Target-language sentence is hidden
   - Translation is hidden
   - All buttons are enabled and ready for interaction
   - Left button replays the audio, labelled "Play audio (←)"
   - Right button moves to Stage 2, labelled "Show sentence (→)"
   - Next moves to a new sentence (Stage 1), labelled "New sentence"

2) Stage 2: Reveals the target-language sentence
   - Left goes back to Stage 1, labelled "Play audio (←)"
   - Right goes to Stage 3, labelled "Show translation (→)"
   - Next moves to a new sentence (Stage 1), labelled "New sentence"

3) Stage 3: Reveals the translated sentence
   - Left goes back to Stage 2, labelled "Show sentence (←)"
   - Right button is disabled
   - Next moves to a new sentence (at Stage 1), labelled "New sentence"

The buttons should be really big and arranged so that it's really easy to press them on a phone.

## Keyboard shortcuts
- ENTER for "Start practice"
- LEFT arrow to proceed backwards through stages within a sentence (always plays audio)
- RIGHT arrow to proceed forward through stages within a sentence
- ENTER for "Next" (i.e. next random sentence flashcard)

## Relevant Files

- `flashcard_views.py`
- `sentence_flashcards.js`
- `sentence_flashcards.jinja`
- `tests/e2e/test_flashcard_frontend.py`
- `sentence_views.py`
- Frontend testing: `../../frontend/docs/FRONTEND_TESTING.md`

## Sourcedir Practice Notes

- Practice button will be disabled if:
  - Directory contains no sourcefiles
  - Sourcefiles have no processed vocabulary
- Error messages:
  - "Directory not found": Invalid sourcedir slug
  - "Directory contains no practice vocabulary": Valid directory but no words extracted
  - "No matching sentences found": No sentences found containing any of the sourcedir's vocabulary

## Future Enhancements
- Highlight which words in sentences come from sourcefile/sourcedir using the Tippy tooltip functionality (see `Sourcefile.jinja`)
- Show progress/stats specific to sourcefile/sourcedir words
- Prioritize sentences with multiple lemmas from sourcefile/sourcedir

## API Access for External Software

The flashcard system can be accessed programmatically through HTTP GET requests. Here are the key endpoints:

### Random Sentence Flashcard

Get a random sentence flashcard:
```
GET /lang/el/flashcards/random
```

This will redirect to a specific sentence flashcard URL.

### Specific Sentence Flashcard

Access a specific sentence by its slug:
```
GET /lang/el/flashcards/sentence/khtizoun-ena-kainourgio-spiti
```

### Filtered Random Flashcards

Get random flashcards filtered by source content:

1. By sourcefile:
```
GET /lang/el/flashcards/random?sourcefile=t3-jpg
```

2. By sourcedir:
```
GET /lang/el/flashcards/random?sourcedir=250127
```

### Response Format

The endpoints return HTML by default. To use in external software:

1. Follow redirects from the `/random` endpoints to get the final sentence URL
2. Parse the HTML response from the sentence endpoint to extract:
   - The sentence text (in target language)
   - The translation
   - The audio data URL (if available)

Note: A proper JSON API may be developed in the future. For now, external software should scrape the HTML responses.

### Cross-Origin Access (CORS)

The flashcard endpoints support cross-origin requests (CORS) from any domain. This means you can access these endpoints from JavaScript running on any website. The following endpoints are CORS-enabled:

- All `/api/*` endpoints
- All flashcard endpoints (`/lang/*/flashcards/*`)

No special headers or credentials are required for cross-origin requests.

### Example Flow

1. Get a random sentence:
```
GET /lang/el/flashcards/random
```
→ Redirects to:
```
GET /lang/el/flashcards/sentence/khtizoun-ena-kainourgio-spiti
```

2. Get a random sentence from a specific sourcefile:
```
GET /lang/el/flashcards/random?sourcefile=t3-jpg
```
→ Redirects to a sentence URL containing vocabulary from that source file

### Example Response Data

When scraping the HTML response, you can extract the following data structure:

```json
{
    "sentence": {
        "id": 123,
        "text": "Χτίζουν ένα καινούργιο σπίτι",
        "translation": "They are building a new house",
        "lemma_words": ["χτίζω", "ένας", "καινούργιος", "σπίτι"],
        "audio_url": "/lang/el/sentences/123/audio"
    },
    "metadata": {
        "target_language_code": "el",
        "language_name": "Greek",
        "sourcefile": "t3-jpg",  // only present if filtered by sourcefile
        "sourcedir": "250127"    // only present if filtered by sourcedir
    }
}
```

The data can be found in these HTML elements:
- Sentence text: `<h3 id="sentence">`
- Translation: `<p id="translation">`
- Lemma words: `<p id="lemma-words">`
- Audio URL: `<audio id="audio-player" src="...">`
- Language code: `window.target_language_code` in script
- Sentence ID: `window.current_sentence_id` in script
- Source info: `window.sourcefile` and `window.sourcedir` in script

Note: The actual response is HTML - this JSON structure represents the data that can be extracted from it.
