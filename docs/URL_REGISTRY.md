# URL Registry System

The URL Registry system provides a centralized way to manage and use application routes, ensuring consistency between backend and frontend code.

## How It Works

The system automatically generates a route registry from Flask's `app.url_map` during application initialization. This registry is then:

1. Made available to Jinja templates via a context processor
2. Injected into JavaScript as a global `window.ROUTES` object
3. Used to generate TypeScript type definitions (in development)

## Using the Registry

### In Python/Flask Code

You can still use Flask's `url_for()` in Python code and templates:

```python
# In Python
url = url_for('sourcedir_api.create_sourcedir', target_language_code='el')

# In Jinja templates
{{ url_for('sourcedir_api.create_sourcedir', target_language_code='el') }}
```

For more type safety, you can use the `endpoint_for()` function to avoid hardcoding endpoint strings:

```python
from views.sourcedir_api import create_sourcedir
from utils.url_registry import endpoint_for

# Now the IDE can warn you if the function name changes
url = url_for(endpoint_for(create_sourcedir), target_language_code='el')
```

This approach makes your code more resistant to function renames and refactoring.

### In JavaScript Code

Use the `resolveRoute()` function to generate URLs:

```javascript
// Get a URL with parameters
const url = resolveRoute('SOURCEDIR_API_CREATE_SOURCEDIR', {
    target_language_code: 'el'
});

// Use in fetch
fetch(resolveRoute('SOURCEDIR_API_DELETE_SOURCEDIR', {
    target_language_code: 'el',
    sourcedir_slug: 'my-dir'
}), {
    method: 'DELETE'
});
```

### In TypeScript Code (When Using the generated TypeScript file)

TypeScript provides additional type safety with auto-completion:

```typescript
import { resolveRoute, RouteName } from '../static/js/generated/routes';

// Type-safe route resolution
const url = resolveRoute(RouteName.SOURCEDIR_API_CREATE_SOURCEDIR, {
    target_language_code: 'el'
});
```

The TypeScript enum approach provides several benefits:
- **IDE autocompletion** - You get full autocompletion of available routes
- **Type checking** - TypeScript validates that you're using a valid route name
- **Parameter type safety** - TypeScript checks that you provide the correct parameters
- **Refactoring support** - IDEs can find all references to a particular route

## Testing the Registry

Visit `/route-test` to see all available routes and test route resolution with parameters.

### Using in Python Tests

For tests, we've added utility functions in `tests/backend/utils_for_testing.py`:

```python
# Import testing utilities
from tests.backend.utils_for_testing import build_url_with_query, get_route_registry
from views.lemma_views import lemma_detail

# Simpler endpoint resolution with query parameters
def test_lemma_detail(client):
    url = build_url_with_query(
        client, 
        lemma_detail,
        query_params={'tab': 'sentences'},  # Query parameters
        target_language_code='el',          # Route parameters
        lemma='test'
    )
    response = client.get(url)
    # Assert response...

# Get the full route registry in tests
def test_with_route_registry(client):
    routes = get_route_registry(client)
    assert 'LEMMA_VIEWS_LEMMA_DETAIL' in routes
    # Use routes dictionary...
```

These utilities make testing with URLs more reliable, as they use the function objects directly rather than hardcoded strings.

## CLI Commands

Generate TypeScript route definitions with the Flask CLI command:

```bash
flask generate-routes-ts
```

This creates a TypeScript file at `static/js/generated/routes.ts`.

## Route Naming Convention

Routes are named automatically using the pattern `BLUEPRINT_VIEWFUNC`. For example:

- `sourcedir_api.create_sourcedir` becomes `SOURCEDIR_API_CREATE_SOURCEDIR`
- `wordform_views.wordform_detail` becomes `WORDFORM_VIEWS_WORDFORM_DETAIL`

## Implementation Details

- `utils/url_registry.py` - Functions to generate route registry and TypeScript definitions
- `static/js/route-client.js` - JavaScript client for resolving routes
- `static/js/generated/routes.ts` - Generated TypeScript type definitions and utilities

## Benefits

- **Single source of truth** - Routes are defined once (in Flask decorators)
- **Always up-to-date** - No manual synchronization required
- **Type safety** - TypeScript provides autocompletion and type checking
- **Consistency** - Same route naming conventions across the application
- **Refactoring safety** - Changing a route in Flask updates all references