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


## SvelteKit development server

The SvelteKit development server (`scripts/local/run_sveltekit.sh`):
- Is being run by the user separately, on port 5173, and generates logs in `logs/sveltekit_dev.log`
- see code in `sveltekit_hz/src`


## Flask API

The Flask development server:
- Is being run by the user separately, on port 3000, and generates logs in `logs/flask_app.log`
- It generates a description of the API routes in `static/js/generated/routes.ts` (it's probably easiest to use grep to get the lines you want)
- see code in `views/`

see `sveltekit_hz/docs/FLASK_API_INTEGRATION.md` for more information.

