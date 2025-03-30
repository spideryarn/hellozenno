# Architecture

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
│   │   ├── url_registry.py  # URL type registry generation
│   │   └── ...              # Other utility modules
│   └── db_models.py         # Database models
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
    │   │   │   ├── api.ts      # Type-safe API communication layer
    │   │   │   ├── generated/  # Auto-generated TypeScript files
    │   │   │   │   └── routes.ts  # Type definitions for API routes
    │   │   │   ├── components/ # Reusable Svelte components
    │   │   │   │   └── Sentence.svelte   # Sentence component
    │   │   │   │   └── Card.svelte       # Card component
    │   │   │   │   └── SourceItem.svelte # Source item component
    │   │   │   └── utils.ts    # Utility functions
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

## Flask to SvelteKit Migration

This project represents a transition from a Flask/Jinja/Svelte application to a SvelteKit frontend with a Flask API backend. The migration follows these principles:

1. **Backend/Frontend Separation**: 
   - Flask handles all API endpoints and database operations
   - SvelteKit manages all user-facing interfaces and client-side logic
   - Flask API endpoints should follow the pattern `/api/[resource]/[action]`

3. **Progressive Migration**:
   - Each Flask Jinja view is methodically replaced with a SvelteKit route
   - Components are rebuilt with Svelte's reactive paradigm

4. **Parallel Operation**:
   - During development, both the original Flask app and the new SvelteKit app run in parallel

5. **Type Safety**: uses Flask-generated TypeScript definitions for all API routes

## SvelteKit development server

The SvelteKit development server (`scripts/local/run_sveltekit.sh`):
- Is being run by the user separately, on port 5173, and generates logs in `logs/sveltekit_dev.log`
- see code in `sveltekit_hz/src`


## Flask API

The Flask development server:
- Is being run by the user separately, on port 3000, and generates logs in `logs/flask_app.log`
- It generates type definitions for routes in `sveltekit_hz/src/lib/generated/routes.ts`
- see code in `views/`

see `sveltekit_hz/docs/FLASK_API_INTEGRATION.md` for more information.

## SvelteKit State Management

The application has been migrated from using the deprecated `$app/stores` module to the newer `$app/state` module, which is built on Svelte 5's runes API. This provides finer-grained reactivity and better performance:

- `import { page } from '$app/stores'` → `import { page } from '$app/state'`
- `$page.data` → `page.data` (no $ prefix needed)

The migration was performed using the SvelteKit migration tool: `npx sv migrate app-state`

This change ensures compatibility with future SvelteKit versions, as `$app/stores` will be removed in SvelteKit 3.

