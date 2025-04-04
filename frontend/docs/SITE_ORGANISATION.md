# Site Organization

This document outlines the organization of the Hello Zenno SvelteKit frontend, describing the main pages, their relationships, and core components.

## Page Structure

The SvelteKit application follows a file-based routing system, with routes defined in the `src/routes` directory:

```
frontend/src/routes/
├── +layout.svelte                # Main app layout
├── +page.svelte                  # Home page
├── languages/                    # Languages list 
└── language/[language_code]/     # Language-specific pages
    ├── +layout.svelte            # Layout for all language pages
    ├── lemmas/                   # Lemma listing 
    ├── lemma/[lemma]/            # Individual lemma view
    ├── phrases/                  # Phrases listing
    ├── phrase/[slug]/            # Individual phrase view
    ├── sentences/                # Sentence listing
    ├── sentence/[slug]/          # Individual sentence view 
    ├── sources/                  # Source materials for language
    ├── source/                   # Source directory navigation
    │   ├── [sourcedir_slug]/     # Source directory listing
    │   └── [sourcedir_slug]/[sourcefile_slug]/ # Individual source file
    ├── search/                   # Search landing
    │   └── [wordform]/           # Search results for word
    ├── wordforms/                # Word forms listing 
    ├── wordform/[wordform]/      # Individual word form
    └── flashcards/               # Flashcards feature
        ├── sentence/[slug]/      # Sentence flashcards
        └── random/               # Random flashcard
```

## Main Pages

### Home (`/`)
- Entry point for the application
- Links to language listing and displays migration status

### Languages List (`/languages/`)
- Lists all available languages 
- Alphabetically organized with search function
- Each language links to its dedicated page

### Language-specific Layout (`/language/[language_code]/`)
- Common layout wrapper for all language-specific pages
- Provides navigation and language context

### Sources (`/language/[language_code]/sources/`)
- Lists all source directories for language learning materials
- Each directory contains various source files (text, images, audio)

### Source Directory (`/language/[language_code]/source/[sourcedir_slug]/`)
- Lists all source files in a specific directory
- Provides source directory metadata and description

### Source File (`/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]/`)
- Displays individual source materials
- Has tabs for:
  - Text view (`/text`)
  - Words view (`/words`) 
  - Phrases view (`/phrases`)

### Lemmas (`/language/[language_code]/lemmas/`)
- Dictionary form of words (root forms)
- Contains detailed linguistic information about each lemma
- See `Lemma` model in `backend/db_models.py`

### Wordforms (`/language/[language_code]/wordforms/`)
- Different inflections and variants of lemmas
- Links to parent lemmas when available
- See `Wordform` model in `backend/db_models.py`

### Sentences (`/language/[language_code]/sentences/`)
- Example sentences in the target language
- Includes translations and audio when available
- See `Sentence` model in `backend/db_models.py`

### Phrases (`/language/[language_code]/phrases/`)
- Multi-word expressions and idioms
- Includes linguistic and cultural context
- See `Phrase` model in `backend/db_models.py`

### Search (`/language/[language_code]/search/`)
- Language-specific search interface
- Search results page at `/search/[wordform]`

### Flashcards (`/language/[language_code]/flashcards/`)
- Flashcard study feature
- Individual sentence flashcards and random options

## Reusable Components

Located in `frontend/src/lib/components/`:

| Component | Purpose |
|-----------|---------|
| `Card.svelte` | Generic card layout for items |
| `LemmaCard.svelte` | Display lemma with metadata |
| `MetadataCard.svelte` | Display creation/modification metadata |
| `NavTabs.svelte` | Tabbed navigation |
| `PhraseCard.svelte` | Display phrase with translations |
| `SearchResults.svelte` | Format search results |
| `Sentence.svelte` | Display sentence with translation and audio |
| `SentenceCard.svelte` | Compact sentence card format |
| `SourceItem.svelte` | Display source material item |
| `SourcefileLayout.svelte` | Layout for sourcefile pages |
| `WordformCard.svelte` | Display word form with metadata |

## API Integration

The frontend communicates with the Flask API using type-safe generated API routes:

- Types are generated from Flask routes in `src/lib/generated/routes.ts`
- The `getApiUrl()` and `apiFetch()` utilities in `src/lib/api.ts` handle API communication

For detailed API integration information, see [Flask API Integration](./BACKEND_FLASK_API_INTEGRATION.md).

## Related Documentation

- [Architecture](./FRONTEND_SVELTEKIT_ARCHITECTURE.md) - SvelteKit architecture details
- [Setup and Development](./SETUP.md) - Development instructions
- [UI and Styling](./STYLING.md) - Component styling information
- [Sourcefile Pages](./SOURCEFILE_PAGES.md) - Detailed structure of sourcefile pages and tabs

## URL Structure

SvelteKit automatically maps file paths to URLs:

- File: `src/routes/language/[language_code]/sources/+page.svelte`
- URL: `/language/el/sources` (where 'el' is the language code parameter)

The routing parameters (`[language_code]`, `[slug]`, etc.) are used to fetch data from the Flask API. 