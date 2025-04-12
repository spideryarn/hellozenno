# URL Registry Documentation

881§    

## Benefits

- **Single Source of Truth**: All API routes are defined in Flask route decorators
- **Type Safety**: TypeScript definitions are auto-generated for route names and parameters
- **Refactoring Support**: Change a route in Flask and all references are updated
- **Developer Experience**: Autocomplete and validation for route names and parameters

## Architecture Overview

HelloZenno uses a hybrid architecture:
- **Flask Backend**: Provides all API endpoints (located in `views/*_api.py`)
- **SvelteKit Frontend**: Handles all user-facing interfaces (located in `frontend/src/`)

The URL Registry ensures type-safe communication between these components.

## Type Generation

When the Flask app starts in development mode, it auto-generates TypeScript definitions:
- Routes are extracted from `app.url_map`
- TypeScript enums and types are written to `frontend/src/lib/generated/routes.ts`
- The SvelteKit frontend uses these types for API communication

## SvelteKit Frontend Integration

### Basic Usage with getApiUrl and getPageUrl

```typescript
// Import the necessary types and functions
import { getApiUrl, apiFetch } from '$lib/api';
import { RouteName } from '$lib/generated/routes';
import { getPageUrl } from '$lib/navigation';

// Get an API URL with type-safe parameters
const apiUrl = getApiUrl(RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API, {
  target_language_code: 'el',
  wordform: 'γεια'
});

// Get a frontend page URL with type-safe parameters
const pageUrl = getPageUrl('wordforms', { target_language_code: 'el' });

// Or with query parameters
const searchPageUrl = getPageUrl(
  'search', 
  { target_language_code: 'el' }, 
  { query: 'hello', filter: 'all' }
);

// Or use apiFetch for a complete API request with error handling
const wordformData = await apiFetch(
  RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API, 
  { target_language_code: 'el', wordform: 'γεια' }
);
```

### In Svelte Components

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { apiFetch } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  
  export let wordform: string;
  export let target_language_code: string;
  
  let wordformData: any = null;
  let loading = true;
  let error: string | null = null;
  
  onMount(async () => {
    try {
      // Type-safe API fetch
      wordformData = await apiFetch(
        RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API,
        { target_language_code, wordform }
      );
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  });
</script>

<div>
  {#if loading}
    <p>Loading...</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else}
    <h2>{wordformData.wordform}</h2>
    <p>{wordformData.translation}</p>
  {/if}
</div>
```

### Using in Server-Side Data Loading

For SvelteKit's server-side data loading, use the same approach:

```typescript
// In +page.server.ts
import { getApiUrl } from '$lib/api';
import { RouteName } from '$lib/generated/routes';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
  const { target_language_code, wordform } = params;
  
  const url = getApiUrl(
    RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API,
    { target_language_code: target_language_code, wordform }
  );
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load wordform data: ${response.status}`);
  }
  
  return {
    wordformData: await response.json()
  };
};
```

## Flask API Development

The following sections are primarily for backend API developers working with Flask. As a frontend developer, you'll typically only need the SvelteKit integration details above.

### Accessing the Route Registry in API Functions

```python
# In your Flask API functions, use url_for() with endpoint_for()
from utils.url_registry import endpoint_for
from flask import url_for

# Best practice: Use endpoint_for with the actual API function
from views.sourcedir_api import create_sourcedir_api
url = url_for(endpoint_for(create_sourcedir_api), target_language_code='el')
```

### Testing URL Registry

You can test route resolution using the route testing page at `/sys/route-test`. This page allows you to:

1. See all available routes
2. Test route resolution with different parameters
3. Get the resolved URL for use in your code

## Adding New API Routes

When you add new routes to the Flask application:

1. The URL registry is automatically updated at application startup
2. In development, TypeScript definitions are generated automatically when Flask starts
3. After adding or modifying routes:
   - Restart the Flask server to update the registry
   - Run `FLASK_APP=api.index flask generate-routes-ts` to manually regenerate TypeScript definitions
4. For production, TypeScript routes are automatically regenerated during deployment

## In Python test code

Use the `build_url_with_query` helper from `tests/backend/utils_for_testing.py`:

```python
from tests.backend.utils_for_testing import build_url_with_query
from views.sourcedir_views import sourcedirs_list

# Build a URL with both path and query parameters
url = build_url_with_query(
    client,
    sourcedirs_list,
    query_params={"sort": "name", "filter": "active"},
    target_language_code="el"
)
```
## Naming Conventions

Routes are named using the following convention:

```
<BLUEPRINT>_<FUNCTION_NAME>
```

For example:
- `SOURCEDIR_API_CREATE_SOURCEDIR_API`
- `WORDFORM_API_GET_WORDFORM_METADATA_API`

API routes typically have names ending with `_API` to distinguish them from legacy view routes.

## Best Practices

1. **Always use getApiUrl/apiFetch instead of hardcoding URLs** for API requests
2. **Always use getPageUrl instead of hardcoding URLs** for frontend navigation
3. **Use endpoint_for() with url_for() in API code** to make it refactoring-proof
4. **Use route constants (RouteName)** in TypeScript to benefit from type checking
5. **Remember that URL parameters are automatically encoded** by the utility functions
6. **If you change a route in Flask, restart to update TypeScript definitions**

## Common Issues and Solutions

### SvelteKit URL Errors

If you get 404 errors in your SvelteKit API requests:

1. **Check browser network tab**: Look for the exact URL being requested
2. **Verify route name**: Ensure you're using the correct RouteName constant
3. **Check parameter values**: Ensure all required parameters are provided
4. **Restart Flask server**: Ensure the TypeScript definitions are up to date
5. **Test with curl**: Verify the API endpoint works directly

### Blueprint and Function Naming

The URL registry relies on correct naming of blueprints and functions:

1. **Blueprint names**: Derived from the module name (e.g., `views.sourcedir_api` → `sourcedir_api`)
2. **Endpoint format**: `blueprint_name.function_name` (e.g., `sourcedir_api.create_sourcedir_api`)
3. **Route naming**: Uppercase with underscore separators (e.g., `SOURCEDIR_API_CREATE_SOURCEDIR_API`)

## Parameter Naming Consistency

The Flask API uses `target_language_code` as the parameter name for language code, while SvelteKit routes may use `target_language_code`. When calling APIs from SvelteKit, always map the SvelteKit route parameter to `target_language_code` in API calls.