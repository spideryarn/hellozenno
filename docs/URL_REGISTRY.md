# URL Registry Documentation

The URL Registry system provides a centralized source of truth for URL definitions in the HelloZenno application. It automatically extracts routes from Flask's `app.url_map` and makes them available to both server-side templates and client-side JavaScript.

## Implementation Status

As of March 2025, the URL Registry has been implemented in the following areas:

### Server-Side (Python)
- ✅ Core `endpoint_for` function in `utils/url_registry.py`
- ✅ Global context processor providing key view functions
- ✅ Updated view functions to use `endpoint_for` when rendering templates

### Client-Side (JavaScript)
- ✅ Client-side route resolution via `resolveRoute` function
- ✅ Updated JavaScript files to use route registry:
  - `static/js/sourcefile.js`
  - `static/js/sourcefiles.js`
  - `static/js/sentence.js`
  - `static/js/sourcedirs.js`

### Templates
- ✅ Updated key templates to use `endpoint_for`:
  - `templates/base.jinja`
  - `templates/sourcedirs.jinja`
  - `templates/sourcefiles.jinja`
  - `templates/lemmas.jinja`
  - `templates/wordforms.jinja`
  - `templates/phrases.jinja`
  - Partial template: `templates/_wordforms_list.jinja`

## Benefits

- **Single Source of Truth**: All routes are defined in one place (Flask route decorators)
- **Type Safety**: TypeScript definitions for route names and parameters
- **Refactoring Support**: Change a route in Flask and all references are updated
- **Developer Experience**: Autocomplete and validation for route names and parameters

## Server-Side (Python)

### Accessing the Route Registry in View Functions

```python
# In your Flask view functions, use url_for() with endpoint_for()
from utils.url_registry import endpoint_for
from flask import url_for

# Direct use of endpoint string (not recommended, fragile to refactoring)
url = url_for('sourcedir_views.sourcedirs_list', target_language_code='el')

# Better: Use endpoint_for with the actual view function
from views.sourcedir_views import sourcedirs_list
url = url_for(endpoint_for(sourcedirs_list), target_language_code='el')
```

### In Jinja Templates

Jinja templates use `url_for()` to generate URLs. There are several approaches to make this more robust:

#### 1. Using endpoint_for in Context Data

```jinja
{# Not recommended: Using hardcoded endpoint string (fragile to refactoring) #}
<a href="{{ url_for('sourcedir_views.sourcedirs_list', target_language_code='el') }}">View Source Directories</a>

{# Better approach: View code imports and calls endpoint_for #}
{# In your view function: #}
from utils.url_registry import endpoint_for
from views.sourcedir_views import sourcedirs_list
endpoint = endpoint_for(sourcedirs_list)
return render_template('template.jinja', sourcedirs_endpoint=endpoint)

{# Then in template.jinja: #}
<a href="{{ url_for(sourcedirs_endpoint, target_language_code='el') }}">View Source Directories</a>
```

#### 2. Using Function References with Blueprints

For view functions attached to a Blueprint, Jinja templates need both the blueprint name and the function name:

```python
# In your view function:
from views.sourcedir_views import sourcedirs_list, sourcedir_views_bp
return render_template('template.jinja',
                      view_func=sourcedirs_list,
                      blueprint=sourcedir_views_bp.name)

# In template.jinja:
<a href="{{ url_for(blueprint + '.' + view_func.__name__, target_language_code='el') }}">
  View Source Directories
</a>
```

For frequently used routes, create helper functions in your views:

```python
# In a helper file, e.g., utils/url_helpers.py
def get_sourcedirs_url(target_language_code):
    from views.sourcedir_views import sourcedirs_list
    return url_for(endpoint_for(sourcedirs_list), target_language_code=target_language_code)
    
# In your view function:
from utils.url_helpers import get_sourcedirs_url
return render_template('template.jinja', 
                       get_sourcedirs_url=get_sourcedirs_url,
                       target_language_code='el')

# Then in your template:
<a href="{{ get_sourcedirs_url(target_language_code) }}">View Source Directories</a>
```

### Using Context Processors for Common URLs

For URLs used across many templates, register a context processor:

```python
# In app initialization code (api/index.py)
@app.context_processor
def url_functions():
    from views.sourcedir_views import sourcedirs_list
    from views.lemma_views import lemmas_list
    
    def sourcedirs_url(target_language_code):
        return url_for(endpoint_for(sourcedirs_list), target_language_code=target_language_code)
        
    def lemmas_url(target_language_code):
        return url_for(endpoint_for(lemmas_list), target_language_code=target_language_code)
    
    return {
        'sourcedirs_url': sourcedirs_url,
        'lemmas_url': lemmas_url
    }

# Then in any template:
<a href="{{ sourcedirs_url(target_language_code) }}">View Source Directories</a>
<a href="{{ lemmas_url(target_language_code) }}">View Lemmas</a>
```

### In Test Code

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

## Client-Side (JavaScript)

### Basic Usage

```javascript
// Get a route with parameters
const url = resolveRoute('SOURCEDIR_API_CREATE_SOURCEDIR', {
    target_language_code: 'el'
});

// Make a fetch request to the resolved URL
fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
});
```

### With URL Parameters and Query Parameters

```javascript
// Get a route with URL parameters
const url = resolveRoute('SOURCEFILE_API_PROCESS_INDIVIDUAL', {
    target_language_code: 'el',
    sourcedir_slug: 'music',
    sourcefile_slug: 'song-01'
});

// Add query parameters
const urlWithQuery = `${url}?debug=true&verbose=1`;

// Make a fetch request
fetch(urlWithQuery, {
    method: 'POST'
});
```

## Client-Side (TypeScript/Svelte)

For TypeScript/Svelte components, use the generated TypeScript utilities for type-safe route resolution:

### First, import the route utilities:

```typescript
// Import the types and utilities
import { RouteName, resolveRoute } from '../../../static/js/generated/routes';
```

### Using the typed route resolution:

```typescript
// This provides full type-checking and auto-completion
const url = resolveRoute(RouteName.WORDFORM_API_WORD_PREVIEW, {
    target_language_code: langCode,
    word: wordform
});

// TypeScript will enforce all required parameters
fetch(url)
    .then(response => response.json())
    .then(data => {
        // Process data
    });
```

### Example in a Svelte Component:

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { RouteName, resolveRoute } from '../../../static/js/generated/routes';
  
  export let wordform: string;
  export let language_code: string;
  
  let previewData: any = null;
  let loading = false;
  let error: string | null = null;
  
  async function fetchWordPreview() {
    loading = true;
    error = null;
    
    try {
      // Type-safe route resolution
      const url = resolveRoute(RouteName.WORDFORM_API_WORD_PREVIEW, {
        target_language_code: language_code,
        word: wordform
      });
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }
      
      previewData = await response.json();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  onMount(fetchWordPreview);
</script>

<div class="word-preview">
  {#if loading}
    <p>Loading...</p>
  {:else if error}
    <p class="error">Error: {error}</p>
  {:else if previewData}
    <h4>{previewData.lemma}</h4>
    {#if previewData.translation}
      <p class="translation">Translation: {previewData.translation}</p>
    {/if}
  {/if}
</div>
```

## Testing URL Registry

You can test route resolution using the route testing page at `/route-test`. This page allows you to:

1. See all available routes
2. Test route resolution with different parameters
3. Get the resolved URL for use in your code

## Adding New Routes

When you add new routes to the Flask application:

1. The URL registry is automatically updated at application startup
2. In development, TypeScript definitions are regenerated automatically
3. For production, run `flask generate-routes-ts` to update TypeScript definitions

## Naming Conventions

Routes are named using the following convention:

```
<BLUEPRINT>_<FUNCTION_NAME>
```

For example:
- `SOURCEDIR_API_CREATE_SOURCEDIR`
- `WORDFORM_VIEWS_GET_WORDFORM_METADATA`

API routes typically have names ending with `_API` to distinguish them from view routes.

## Best Practices

1. **Always use resolveRoute instead of hardcoding URLs** in JavaScript
2. **Use endpoint_for() with url_for() in Python code** to make it refactoring-proof
3. **In Jinja templates, prefer passing view functions** from view code rather than hardcoding endpoint strings
4. **Use context processors for frequently used URLs** across templates
5. **Use route constants (not string literals)** in TypeScript to benefit from type checking
6. **Remember to encode URL parameters for special characters**
7. **If you change a route in Flask, update TypeScript definitions** with `flask generate-routes-ts`

## Common Issues and Solutions

### Jinja Template URL Errors

If you get template errors about missing endpoints:

1. **Check blueprint registration**: Ensure the blueprint is registered in `api/index.py`
2. **Check function imports**: Make sure view functions are properly imported and passed to templates
3. **Check endpoint naming**: Blueprint endpoints follow the pattern `blueprint_name.function_name`
4. **Use the endpoint_for helper**: If you're unsure about an endpoint name, use the `endpoint_for` helper

### JavaScript URL Errors

If you get 404 errors in your JavaScript requests:

1. **Check browser console**: Look for the exact URL being requested
2. **Verify route constants**: Check if the route constant exists in `window.ROUTES`
3. **Check parameter values**: Ensure all required parameters are provided and properly encoded
4. **Use the route-test page**: Test route resolution with different parameters

### Blueprint and Function Naming

The URL registry relies on correct naming of blueprints and functions:

1. **Blueprint names**: Derived from the module name (e.g., `views.sourcedir_views` → `sourcedir_views`)
2. **Endpoint format**: `blueprint_name.function_name` (e.g., `sourcedir_views.sourcedirs_list`)
3. **Route naming**: Uppercase with underscore separators (e.g., `SOURCEDIR_VIEWS_SOURCEDIRS_LIST`)