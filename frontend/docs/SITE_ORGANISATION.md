# Site Organization

This document outlines the organization of the Hello Zenno SvelteKit frontend, describing the main user-facing pages, their URLs and purpose, and the core components used to build them.

For technical details on the underlying architecture, frameworks, API integration, state management, and build process, see the [Frontend Architecture](./FRONTEND_SVELTEKIT_ARCHITECTURE.md) document.

## Page Structure & Routes

The SvelteKit application follows a file-based routing system defined in the `src/routes` directory. Standard `+error.svelte` files handle errors at their respective levels.

```
frontend/src/routes/
├── +layout.svelte                # Root app layout
├── +page.svelte                  # Home page (/)
├── +error.svelte                 # Root error page
├── languages/                    # Languages list (/languages)
│   └── +page.svelte
├── language/[target_language_code]/     # Language-specific pages
│   ├── +layout.svelte            # Layout for all language pages
│   ├── +error.svelte             # Language-level error page
│   ├── lemmas/                   # Lemma listing (/language/.../lemmas)
│   ├── lemma/[lemma]/            # Individual lemma view (/language/.../lemma/...)
│   ├── phrases/                  # Phrases listing (/language/.../phrases)
│   ├── phrase/[slug]/            # Individual phrase view (/language/.../phrase/...)
│   ├── sentences/                # Sentence listing (/language/.../sentences)
│   ├── sentence/[slug]/          # Individual sentence view (/language/.../sentence/...)
│   ├── sources/                  # Source materials list (/language/.../sources)
│   ├── source/                   # Source directory/file navigation
│   │   ├── [sourcedir_slug]/     # Source directory listing (/language/.../source/...)
│   │   └── [sourcedir_slug]/[sourcefile_slug]/ # Individual source file view (+ sub-routes)
│   │       ├── +page.svelte      # Base page for source file 
│   │       ├── text/+page.svelte # Text tab
│   │       ├── words/+page.svelte # Words tab
│   │       ├── phrases/+page.svelte # Phrases tab
│   │       ├── translation/+page.svelte # Translation tab
│   │       ├── image/+page.svelte # Image tab
│   │       └── audio/+page.svelte # Audio tab
│   ├── search/                   # Search landing page (/language/.../search)
│   │   └── [wordform]/           # Search results for word (/language/.../search/...)
│   ├── wordforms/                # Word forms listing (/language/.../wordforms)
│   ├── wordform/[wordform]/      # Individual word form (/language/.../wordform/...)
│   └── flashcards/               # Flashcards feature (/language/.../flashcards)
│       ├── +page.svelte          # Flashcards landing/overview
│       ├── sentence/[slug]/      # Sentence flashcards (/language/.../flashcards/sentence/...)
│       └── random/               # Random flashcard (/language/.../flashcards/random)
├── auth/                         # Authentication pages
│   ├── +page.svelte              # Login/Signup page (/auth)
│   └── profile/                # User profile page (/auth/profile)
│       └── +page.svelte
```

## Main Pages & Sections

### Home (`/`)
- Entry point for the application.
- Links to language listing and potentially displays global status/info.

### Languages List (`/languages/`)
- Lists all available languages.
- Allows searching/filtering languages.
- Each language links to its dedicated section.

### Authentication (`/auth`, `/auth/profile`)
- Handles user login, registration, and profile management via Supabase Auth.

### Language Section (`/language/[target_language_code]/`)
- Provides a consistent layout and navigation for a specific language.
- Contains various sub-pages for exploring language content.

#### Sources (`.../sources/`, `.../source/[dir]/`, `.../source/[dir]/[file]/`)
- Browse source materials (texts, audio, images) organized in directories and files.
- The file view (`.../[file]/`) uses tabs (`/text`, `/words`, `/phrases`, etc.) to display different aspects of the source material.

#### Dictionary Views (`.../lemmas/`, `.../lemma/[lemma]`, `.../wordforms/`, `.../wordform/[wordform]`)
- Explore dictionary entries (lemmas) and their inflected forms (wordforms).
- Provide detailed linguistic information.

#### Example Content (`.../sentences/`, `.../sentence/[slug]`, `.../phrases/`, `.../phrase/[slug]`)
- View example sentences and common phrases/idioms.
- Often include translations and audio.

#### Search (`.../search/`, `.../search/[wordform]`)
- Perform searches within the specific language.
- Display results for searched terms.

#### Flashcards (`.../flashcards/`, `.../flashcards/sentence/[slug]`, `.../flashcards/random`)
- Access flashcard study modes for sentences or random selections.

## Reusable Components

Located in `frontend/src/lib/components/`, these components provide common UI elements across pages:

| Component | Purpose |
|-----------|---------|
| `Alert.svelte` | Display styled alert messages (info, warning, error). |
| `Card.svelte` | Generic card layout container. |
| `CollapsibleHeader.svelte` | A header section that can be expanded or collapsed. |
| `DescriptionFormatted.svelte` | Renders text descriptions with specific formatting. |
| `DescriptionSection.svelte` | A dedicated section for displaying descriptive text, often collapsible. |
| `EnhancedText.svelte` | Renders text with potential enhancements like popups or links. |
| `FileOperationsSection.svelte` | UI section for actions related to file management (e.g., download, upload). |
| `LemmaCard.svelte` | Displays a lemma entry in a card format. |
| `MetadataCard.svelte` | Displays creation/modification timestamps and user info. |
| `MetadataSection.svelte` | A dedicated section for displaying metadata, often collapsible. |
| `NavTabs.svelte` | Creates a tabbed navigation interface. |
| `PhraseCard.svelte` | Displays a phrase and its translation in a card format. |
| `SearchBarMini.svelte` | Provides a compact search interface used in language and sourcefile layouts. |
| `SearchResults.svelte` | Formats and displays a list of search results. |
| `Sentence.svelte` | Displays a full sentence with translation, audio controls, etc. |
| `SentenceCard.svelte` | A compact card format for displaying a sentence snippet. |
| `SourcefileAudio.svelte` | Component specifically for handling audio display/playback within source files. |
| `SourcefileImage.svelte` | Component specifically for handling image display within source files. |
| `SourcefileLayout.svelte` | Provides the common layout structure for the different source file tabs. |
| `SourceItem.svelte` | Displays an item (like a directory or file) in a source listing. |
| `WordformCard.svelte` | Displays a word form entry in a card format. |

*Note: Specific views like the source file pages (`/source/[...]/[...]/`) may also use dedicated components located within their route directory (e.g., `src/routes/.../source/.../[file]/components/`).*

## API Integration Summary

The frontend fetches all dynamic data from the Flask backend API.

- **Type Safety**: Communication is type-safe, leveraging TypeScript definitions generated by the backend.
- **Mechanism**: Uses helper functions (like `apiFetch` in `src/lib/api.ts`) to interact with the API.

For technical details on how the API integration works, including type generation and communication patterns, see the [Frontend Architecture](./FRONTEND_SVELTEKIT_ARCHITECTURE.md) document.

## Related Documentation

- [Frontend Architecture](./FRONTEND_SVELTEKIT_ARCHITECTURE.md) - Technical architecture, frameworks, build process.
- [Flask API Integration](./BACKEND_FLASK_API_INTEGRATION.md) - Details on the Flask API contract.
- [Authentication](./AUTH.md) - Detailed authentication implementation.
- [Setup and Development](./SETUP.md) - Instructions for setting up the development environment.
- [Visual Design and Styling](./VISUAL_DESIGN_STYLING.md) - Component styling conventions and theme information.
- [Sourcefile Pages](./SOURCEFILE_PAGES.md) - Detailed structure of sourcefile pages and tabs.
- [Database Models](../../backend/docs/MODELS.md) - Overview of the backend database schema.

## URL Structure

SvelteKit automatically maps file paths to URLs:

- File: `src/routes/language/[target_language_code]/sources/+page.svelte`
- URL: `/language/el/sources` (where 'el' is the language code parameter)

The routing parameters (`[target_language_code]`, `[slug]`, etc.) are used to fetch data from the Flask API. 