# Sourcefile Pages

This document describes the structure of source file pages, their components, and how to add new tabs.

## What is a Sourcefile?

A Sourcefile is a core data entity in HelloZenno representing learning content in a target language. Sourcefiles can be:

- **Text files**: Created by pasting or typing text directly
- **Image files**: Uploaded images containing text (processed with OCR)
- **Audio files**: Including YouTube audio downloads

Sourcefiles are organized into Sourcedirs (directories) and contain:
- Target language text (`text_target`)
- English translation (`text_english`)
- Associated wordforms and phrases
- Optional metadata, description, and audio

See `backend/db_models.py` for the database model definitions, particularly the `Sourcefile` model and related junction tables (`SourcefileWordform`, `SourcefilePhrase`).

## Page Structure

Sourcefile pages follow a tab-based interface pattern with routes at:
```
/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/[tab]
```

Each tab has its own route handler, with routes redirecting from the base path to `/text` by default.

The content in the text tab is displayed using "Enhanced Text" functionality which provides interactive word links - see `frontend/docs/ENHANCED_TEXT.md` for details on this implementation.

See also: `planning/250405_speeding_up_Sourcefile.md` for a discussion on refactoring, overlap, and performance.

## Components Organization

```
frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/
├── +page.server.ts        # Main route handler (redirects to /text)
├── +page.svelte           # Legacy component (redirects to tab routes)
├── components/            # Shared components for sourcefile tabs
│   ├── SourcefileHeader.svelte     # Common header with metadata
│   ├── SourcefileText.svelte       # Text tab content
│   ├── SourcefileWords.svelte      # Words tab content
│   ├── SourcefilePhrases.svelte    # Phrases tab content
│   └── SourcefileTranslation.svelte # Translation tab content
├── text/                  # Text tab route
│   └── +page.svelte       # Text view implementation
├── words/                 # Words tab route
│   └── +page.svelte       # Words list implementation
├── phrases/               # Phrases tab route
│   └── +page.svelte       # Phrases list implementation
└── translation/           # Translation tab route
    ├── +page.server.ts    # Server-side data loading
    └── +page.svelte       # Translation view implementation
```

## Shared Layout Pattern

Tabs use a common layout pattern via `SourcefileLayout.svelte` which provides:
- Consistent header with file metadata
- Tab navigation
- Breadcrumb navigation
- Navigation controls (next/previous file)

## Adding a New Tab

1. Create a component in the `components/` directory (e.g., `SourcefileNewTab.svelte`)
2. Create a new route directory with server and page files:
   ```
   mkdir translation/
   touch translation/+page.server.ts translation/+page.svelte
   ```
3. Update `SourcefileLayout.svelte` to add the new tab to navigation:
   ```svelte
   export let activeTab: 'text' | 'words' | 'phrases' | 'translation' | 'newtab';
   
   // Add to tabs array
   $: tabs = [
     // existing tabs
     {
       label: 'New Tab',
       href: `/language/${target_language_code}/source/${sourcedir_slug}/${sourcefile_slug}/newtab`,
       active: activeTab === 'newtab'
     }
   ];
   ```
4. Implement the server data loading pattern in `+page.server.ts` following existing examples

## Data Flow

1. The server component (`+page.server.ts`) loads data from the Flask API endpoints in `backend/views/sourcefile_api.py`
2. Data is passed to the page component (`+page.svelte`)
3. The page component uses `SourcefileLayout` and passes the tab-specific component
4. The tab component receives and renders data specific to its function

Each tab fetches data through a specialized endpoint like:
- `/api/lang/sourcefile/<language_code>/<sourcedir_slug>/<sourcefile_slug>/text`
- `/api/lang/sourcefile/<language_code>/<sourcedir_slug>/<sourcefile_slug>/words`
- `/api/lang/sourcefile/<language_code>/<sourcedir_slug>/<sourcefile_slug>/phrases`

The text tab integrates with the Enhanced Text system to display interactive word links with tooltips. When a user hovers over a word, a tooltip shows information about the word's lemma, translations, and other metadata.

## API Integration

Sourcefile pages interact with several backend API endpoints:
- `inspect_sourcefile_*_api()` - Get sourcefile content based on purpose (text, words, phrases)
- `process_sourcefile_api()` - Process file to extract words and phrases
- `generate_sourcefile_audio_api()` - Generate audio for the sourcefile text

See [BACKEND_FLASK_API_INTEGRATION.md](./BACKEND_FLASK_API_INTEGRATION.md) for details on API interaction.

## Sourcefile Processing Flow

When a user processes a sourcefile (by clicking the "Process this text" button), a synchronous flow is triggered that transforms raw content into learning materials:

```
[HTTP Request]
    │
    ▼
[process_sourcefile_api]
    │ "Sets processing parameters and initializes"
    │
    ▼
[process_sourcefile]
    │ "Main orchestration function that calls specialized helpers"
    │
    ├───────────────┬───────────────┬───────────────┐
    │               │               │               │
    ▼               ▼               ▼               ▼
[ensure_text_     [ensure_        [ensure_tricky_ [ensure_tricky_
 extracted]        translation]     wordforms]      phrases]
    │ "Extract      │ "Translate    │ "Extract      │ "Extract
    │  text from    │  text to      │  vocabulary   │  phrases from
    │  image/audio/ │  English"     │  words"       │  text"
    │  text file"   │               │               │
    ▼               ▼               ▼               ▼
[Database Updates]    [Database Updates]    [Database Updates]
   "Store extracted    "Store translation    "Create/update Lemma, Wordform,
    text in            in text_english       SourcefileWordform, Phrase,
    text_target field" field"               and SourcefilePhrase entries"
```

### Key Processing Stages

1. **Text Extraction**: Extracts text content from the sourcefile based on type:
   - Image files: Uses OCR to extract text
   - Audio files: Transcribes speech or uses YouTube subtitles
   - Text files: Uses content directly

2. **Translation**: Translates the extracted text to English

3. **Vocabulary Extraction**: Identifies important or difficult words in the text, creating:
   - Lemma entries (dictionary form) - partial, focusing on key fields like "translation"
   - Wordform entries (inflected forms)
   - SourcefileWordform junction entries (linking words to this sourcefile)

4. **Phrase Extraction**: Identifies idiomatic expressions and phrases, creating:
   - Phrase entries
   - SourcefilePhrase junction entries

5. **Full Lemma metadata** - fills out the rest of the lemma, e.g. etymology, easily confused with, etc

The process is designed to be idempotent - each stage checks if work is already complete before proceeding, allowing for partial or repeated processing without duplicating work.

See [SITE_ORGANISATION.md](./SITE_ORGANISATION.md) for overall site structure and [FRONTEND_SVELTEKIT_ARCHITECTURE.md](./FRONTEND_SVELTEKIT_ARCHITECTURE.md) for architecture details. 