# Architecture

The Hello Zenno application uses a hybrid architecture, combining a SvelteKit frontend for the user interface with a Flask backend serving as a data API.

## Key Architectural Components

```
Hello Zenno/
├── backend/ (Flask API)
│   ├── api/index.py      # Main Flask application entry point
│   ├── views/            # API endpoints definitions
│   └── ...               # Models, utils, etc.
│
└── frontend/ (SvelteKit App)
    ├── svelte.config.js  # SvelteKit framework configuration
    ├── vite.config.js    # Vite build tool configuration
    ├── src/
    │   ├── app.html        # HTML shell template
    │   ├── hooks.server.js # Server-side request hooks (e.g., for auth)
    │   ├── routes/         # Application pages and API endpoints (See SITE_ORGANISATION.md)
    │   ├── lib/            # Shared modules, components, utilities
    │   │   ├── api.ts      # Type-safe API communication layer
    │   │   ├── generated/  # Auto-generated files (e.g., API types)
    │   │   ├── components/ # Reusable Svelte components
    │   │   ├── stores/     # Application state management
    │   │   └── types/      # Custom TypeScript types
    │   └── static/         # Static assets (CSS, images, fonts)
    └── ...
```

For a detailed breakdown of user-facing pages and their routes, see the [Site Organization](./SITE_ORGANISATION.md) document.

## Flask to SvelteKit Migration Rationale

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

## SvelteKit Development Environment

The SvelteKit development server (`scripts/local/run_sveltekit.sh`):
- Is typically run by the user separately (e.g., via `npm run dev` or a script).
- Uses Vite for fast Hot Module Replacement (HMR).
- Configuration is managed in `svelte.config.js` and `vite.config.js`.
- Logs are usually output to the console or configured location (e.g., `logs/frontend.log`).

## Flask API Backend Integration

The SvelteKit frontend communicates exclusively with the Flask backend via API calls.

- **API Location**: Flask runs separately (e.g., on port 3000) serving endpoints under `/api/...`. Logs are typically in `logs/backend.log`.
- **Type Safety**: The Flask backend generates TypeScript type definitions for its API routes (`frontend/src/lib/generated/routes.ts`). This ensures type-safe communication using utilities like `apiFetch` in `frontend/src/lib/api.ts`.
- **No Direct DB Access**: The frontend never accesses the database directly; all data operations go through the Flask API.

See [Flask API Integration](./BACKEND_FLASK_API_INTEGRATION.md) for more details on the API contract and communication patterns.

## Authentication

The application uses Supabase Authentication with the `@supabase/ssr` library for server-side rendering compatibility. Authentication state is initialized on the server and passed to the client, with a single client instance maintained per context.

For detailed information about the authentication implementation, see [Authentication](./AUTH.md).

## SvelteKit State Management

The application utilizes Svelte 5's runes for state management, primarily through SvelteKit's built-in `$app/state` module for page data and potentially custom stores located in `src/lib/stores/` for global or cross-component state.

The migration was performed using the SvelteKit migration tool: `npx sv migrate app-state`

This change ensures compatibility with future SvelteKit versions, as `$app/stores` will be removed in SvelteKit 3.

## Special Routing Features

### Languages Page Redirection

The `/languages` page supports a `next` query parameter for directing users to feature-specific pages after language selection:

```
/languages?next=flashcards
```

After selecting a language, users will be redirected to that language's flashcards page rather than the default sources page. This is particularly useful for marketing materials and blog posts targeting specific features.

Valid `next` parameter values include:
- `flashcards` - Language flashcards
- `lemmas` - Dictionary lemmas list
- `phrases` - Multi-word expressions
- `search` - Search interface
- `sentences` - Example sentences
- `sources` - Source texts (default)
- `wordforms` - Word forms list

Implementation details can be found in `/planning/250423_redirect_query_param_languages_page.md`.

