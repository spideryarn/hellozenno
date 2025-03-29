# Hello Zenno SvelteKit Frontend

Hello Zenno is a web application for learning langauges. A modern SvelteKit frontend, designed to work with the existing Flask API backend.

## Overview

### Features

- Interactive language learning interface
- Source file management for learning materials
- Sentence and word-level translations
- Language vocabulary exploration
- Audio playback for pronunciation practice
- Responsive design for all devices

## Architecture

The Hello Zenno application uses a hybrid architecture:

```
Hello Zenno
│
├── Flask Backend (API)
│   ├── api/index.py         # Main Flask application entry point
│   ├── views/               # API endpoints and controllers
│   │   ├── languages_api.py # Language-related APIs
│   │   ├── sentence_api.py  # Sentence-related APIs
│   │   └── ...              # Other API modules
│   ├── utils/               # Shared utilities
│   │   ├── lang_utils.py    # Language processing utilities
│   │   └── ...              # Other utility modules
│   └── models/              # Database models
│
└── SvelteKit Frontend
    ├── src/
    │   ├── routes/          # SvelteKit routes and pages
    │   │   ├── languages/   # Languages listing page
    │   │   └── language/    # Language-specific pages
    │   │       ├── [language_code]/
    │   │       │   ├── sources/      # Source materials for a language
    │   │       │   └── sentence/     # Individual sentence view
    │   │       │       └── [slug]/   # Dynamic sentence route
    │   │   ├── lib/            # Shared libraries and components
    │   │   │   ├── components/ # Reusable Svelte components
    │   │   │   │   └── Sentence.svelte   # Sentence component
    │   │   │   │   └── Card.svelte       # Card component
    │   │   │   │   └── SourceItem.svelte # Source item component
    │   │   │   ├── utils.ts    # Utility functions
    │   │   │   └── api.ts      # API communication layer
    │   │   └── app.html        # SvelteKit app template
    │   └── static/             # Static assets
    │       ├── css/
    │       │   ├── base.css            # Base CSS imports
    │       │   ├── theme.css           # Theme styling
    │       │   ├── theme-variables.css # Theme variables
    │       │   ├── components.css      # Component-specific styles
    │       │   └── extern/             # External CSS libraries
    │       └── js/
    │           └── extern/             # External JS libraries
    └── ...
```

## Setup and Development

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+ with Flask backend running

### Installation

Install dependencies:

```bash
cd sveltekit_hz
npm install
```

### Development Commands

Run the development server:

```bash
# Start the SvelteKit development server
npm run dev

# Or open in a browser automatically
npm run dev -- --open
```

The SvelteKit frontend runs on port 5173 by default (see `run_sveltekit.sh`): http://localhost:5173

The Flask backend should be running separately (see `scripts/local/run_flask.sh`) on port 3000: http://localhost:3000


### Build for Production

(We haven't tried this yet)

```bash
npm run build
npm run preview  # Preview the production build locally
```

## UI and Styling

The application uses Bootstrap 5.3.2 for styling, with a custom dark theme. The styling system is organized as follows:

### CSS Structure

```
static/css/
├── base.css               # Main CSS file that imports others
├── theme-variables.css    # Theme variables (colors, fonts, etc.)
├── theme.css              # Theme-specific styling
├── components.css         # Component-specific styles
└── extern/
    └── bootstrap/
        └── bootstrap.min.css  # Bootstrap core CSS
```

### Theming

The app uses a dark theme with a color scheme defined in `theme-variables.css`:
- Background: Near-black (`#121212`)
- Main font: Near-white (`#e9e9e9`)
- Primary: Bright green (`#4CAD53`) - for highlights, buttons, active elements
- Secondary: Complementary orange (`#D97A27`) - for accents, secondary actions

### Component Library

We provide reusable Svelte components to maintain consistent styling:

- `Card.svelte`: For card-based layouts (used in language listings)
- `SourceItem.svelte`: For displaying source items
- `Sentence.svelte`: For displaying sentences with translations

### How to Use

1. Import components directly from `$lib`:

```svelte
<script>
  import { Card, SourceItem } from '$lib';
</script>
```

2. Use Bootstrap classes with our custom styling:

```svelte
<div class="card hz-language-item">
  <!-- Card content -->
</div>
```

3. Use custom CSS classes for consistent styling:
   - `.hz-language-item`: For language cards
   - `.hz-foreign-text`: For foreign language text
   - `.hz-source-item`: For source items

## Flask to SvelteKit Migration

This project represents a transition from a Flask/Jinja/Svelte application to a SvelteKit frontend with a Flask API backend. The migration follows these principles:

1. **Backend/Frontend Separation**: 
   - Flask handles all API endpoints and database operations
   - SvelteKit manages all user-facing interfaces and client-side logic

2. **API-First Approach**:
   - All data exchange happens through well-defined API endpoints
   - Flask API endpoints follow the pattern `/api/[resource]/[action]`
   - SvelteKit consumes these APIs using fetch requests

3. **Progressive Migration**:
   - Each Flask Jinja view is methodically replaced with a SvelteKit route
   - Components are rebuilt with Svelte's reactive paradigm
   - We maintain feature parity while improving UX

4. **Parallel Operation**:
   - During development, both the original Flask app and the new SvelteKit app run in parallel
   - This allows gradual migration and testing without service disruption

## API Integration

SvelteKit components communicate with the Flask backend through API calls. For example:

```typescript
// In a SvelteKit component or page
import { get_api_url } from '$lib/utils';

// Fetch languages from the API
async function fetchLanguages() {
    const response = await fetch(get_api_url('lang/languages'));
    return await response.json();
}
```

The Flask backend exposes these API endpoints in corresponding `*_api.py` files.

## Project Status and Roadmap

See [planning/250329_SvelteKit.md](../planning/250329_SvelteKit.md) for the detailed migration plan and current progress.

## Additional Documentation

- [Main Project README](../README.md) - Overview of the entire Hello Zenno project
- [Flask API Entry Point](../api/index.py) - Details of the Flask API setup
- [Database Documentation](../docs/DATABASE.md) - Database configuration information

## Contributing

1. Review the planning document to understand the current migration status
2. Follow the established patterns for component and API interactions
3. Maintain the separation between frontend and backend concerns
4. Write TypeScript types for all data structures exchanged with the API

## Environment Configuration

Create a `.env` file in the SvelteKit root directory with the following variables:

```
PUBLIC_API_BASE=http://localhost:3000/api
```

For production, this will be updated to point to the deployed API endpoint.
