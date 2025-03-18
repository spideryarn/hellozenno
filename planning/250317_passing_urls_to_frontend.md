# URL Registry: Standardizing URL Management in HelloZenno

## Problem Statement

The HelloZenno application is experiencing issues with URL management during the ongoing API URL structure standardization:

1. **Inconsistent URL References**: URLs are defined in multiple places (Flask routes, Jinja templates, JavaScript files), making changes error-prone and difficult to track.

2. **Brittle URL Dependencies**: Hard-coded URLs create hidden dependencies between backend and frontend code, so changes in one place often break functionality elsewhere.

3. **Manual Updates Required**: When changing URL structures (as in the current standardization effort), developers must manually search and update each occurrence, leading to missed references and subtle bugs.

4. **Developer Friction**: The current approach creates friction in development, testing, and refactoring, as URL changes require extensive coordination across the codebase.

## Context

HelloZenno is currently undergoing API URL structure standardization as documented in `250317_API_URL_Structure_Standardization.md`. The project is moving toward domain-specific API files with standardized URL patterns like `/api/lang/<resource>/...`.

The Flask application already has good practices in place:
- Consistent use of `url_for()` in Python code and templates
- Blueprint-based organization for routes
- `full_url_for()` utility for absolute URL generation

However, JavaScript code primarily uses hard-coded URL strings, creating a maintenance burden when URL patterns change.

## Solution Options

### Option 1: Template-Injected Routes (CHOSEN)

Inject a complete route registry into the base template, making it available to all JavaScript.

#### Implementation Steps:

1. Create a central Python route registry with named constants:
   ```python
   # url_registry.py
   class Routes:
       """Central registry of view and API route templates.
       
       Format: DOMAIN_ACTION = "/path/to/{param}/endpoint"
       
       Use these constants in Flask route definitions and JavaScript URL resolution.
       """
       # Standard view routes
       HOME = "/"
       LANGUAGES = "/languages"
       WORDFORM_DETAIL = "/lang/{language_code}/wordform/{word}"
       LEMMA_DETAIL = "/lang/{language_code}/lemma/{lemma}"
       SOURCEDIR_LIST = "/lang/{language_code}/sourcedirs"
       SOURCEFILE_DETAIL = "/lang/{language_code}/sourcedir/{sourcedir_slug}/{sourcefile_slug}"
       
       # API routes
       API_SOURCEDIR_LIST = "/api/lang/sourcedir/{language_code}"
       API_SOURCEDIR_CREATE = "/api/lang/sourcedir/{language_code}"
       API_SOURCEDIR_DELETE = "/api/lang/sourcedir/{language_code}/{sourcedir_slug}/delete"
       API_SOURCEFILE_LIST = "/api/lang/sourcefile/{language_code}/{sourcedir_slug}"
       API_SOURCEFILE_DETAIL = "/api/lang/sourcefile/{language_code}/{sourcedir_slug}/{sourcefile_slug}"
       API_WORD_PREVIEW = "/api/lang/word/{language_code}/preview/{word}"
       API_SENTENCE_RANDOM = "/api/lang/sentence/{language_code}/random"
       
       # And so on for other domains...
   ```

2. Create a function to extract all routes from the registry:
   ```python
   def get_routes():
       """Extract all routes from the Routes class for template injection."""
       routes = {}
       for name, path in vars(Routes).items():
           if not name.startswith('_'):  # Skip private attributes
               routes[name] = path
       return routes
   ```

3. Modify base.jinja to inject the routes into the global JavaScript context:
   ```html
   <script>
   // Route registry - generated from url_registry.py
   window.ROUTES = {
       {% for name, path in get_routes().items() %}
       "{{ name }}": "{{ path }}",
       {% endfor %}
   };
   </script>
   ```

4. Create a JavaScript utility for resolving route templates:
   ```javascript
   // static/js/route-client.js
   /**
    * Resolve a route template with parameters.
    * 
    * @param {string} routeName - Name of the route from ROUTES
    * @param {Object} params - Parameters to substitute in the route template
    * @returns {string} Resolved URL with parameters
    * @example
    *   // Returns "/api/lang/sourcedir/el"
    *   resolveRoute('API_SOURCEDIR_LIST', {language_code: 'el'})
    */
   export function resolveRoute(routeName, params = {}) {
     if (!window.ROUTES || !window.ROUTES[routeName]) {
       console.error(`Route not found: ${routeName}`);
       return '';
     }
     
     let url = window.ROUTES[routeName];
     
     // Replace template parameters with actual values
     Object.entries(params).forEach(([key, value]) => {
       url = url.replace(`{${key}}`, encodeURIComponent(value));
     });
     
     return url;
   }
   ```

5. Update existing JavaScript to use the new utility:
   ```javascript
   // Before:
   fetch(`/api/lang/sourcedir/${window.target_language_code}`)
   
   // After:
   import { resolveRoute } from './route-client.js';
   fetch(resolveRoute('API_SOURCEDIR_LIST', {language_code: window.target_language_code}))
   ```

6. Update Flask route definitions to use the same constants:
   ```python
   from url_registry import Routes
   
   # sourcedir_api.py
   sourcedir_api_bp = Blueprint("sourcedir_api", __name__, url_prefix="/api/lang/sourcedir")
   
   @sourcedir_api_bp.route("/<target_language_code>", methods=["POST"])
   def create_sourcedir_api(target_language_code):
       # Implementation...
   ```

### Option 2: Dynamic Route Registry

Fetch routes from a dedicated API endpoint when needed.

```javascript
// route-client.js
let routeRegistry = null;

async function getRouteRegistry() {
  if (routeRegistry === null) {
    const response = await fetch('/api/routes');
    routeRegistry = await response.json();
  }
  return routeRegistry;
}

export async function resolveRoute(routeName, params) {
  const routes = await getRouteRegistry();
  let url = routes[routeName];
  // Replace template parameters
  Object.entries(params).forEach(([key, value]) => {
    url = url.replace(`{${key}}`, encodeURIComponent(value));
  });
  return url;
}
```

### Option 3: TypeScript Route Generation

Generate TypeScript constants from the Python route registry during the build process.

```python
# build_routes.py
def generate_typescript_routes():
    with open('frontend/src/lib/routes.ts', 'w') as f:
        f.write('// Auto-generated from url_registry.py\n')
        f.write('export const ROUTES = {\n')
        for name, path in vars(Routes).items():
            if not name.startswith('_'):
                f.write(f'  {name}: "{path}",\n')
        f.write('};\n')
```

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **Template-Injected Routes** | - Immediately available on page load<br>- No async loading required<br>- Simple implementation<br>- Available in all JavaScript | - Template size increases<br>- Requires server-side processing for each page<br>- No type safety |
| **Dynamic Route Registry** | - Single source of truth<br>- Can update routes without code changes<br>- Smaller initial page load | - Requires async loading<br>- Introduces potential delays<br>- Complexity of async handling |
| **TypeScript Route Generation** | - Type safety for route names<br>- Compile-time checking<br>- IDE autocompletion | - Requires build step<br>- Must regenerate when routes change<br>- More complex setup |

## Implementation Plan for Template-Injected Routes

1. **Create URL Registry Module (url_registry.py)**
   - Define Routes class with all route templates
   - Implement get_routes() helper function

2. **Modify Flask View Context Processor**
   - Add get_routes to the template context
   - Ensure it's available in all templates

3. **Update Base Template**
   - Add route registry script block to head section
   - Inject all routes as a JavaScript object

4. **Create JavaScript Utility**
   - Implement resolveRoute function
   - Add validation and error handling
   - Add to base.js or create dedicated route-client.js

5. **Migrate Existing JavaScript**
   - Update hardcoded URLs to use resolveRoute
   - Focus on key files first (sourcedir.js, sourcefile.js, etc.)

6. **Ensure Blueprint Registration Matches**
   - Verify that Flask blueprint URL prefixes match registry
   - Document any differences or special cases

7. **Testing**
   - Test resolveRoute with various parameters
   - Verify correct escaping of URL parameters
   - Check for performance impact

## Actions

1. **Delete Unused Code**
   - Remove the unused `core_api.py` file since the `/api/urls` endpoint is not being used
   - Update imports in `api/index.py` and `tests/backend/conftest.py` that reference `core_api_bp`

2. **Create Initial Route Registry**
   - Create a new file `utils/url_registry.py` with the `Routes` class
   - Include both view and API routes, organized by domain
   - Include function to extract routes for templates

3. **Register Context Processor**
   - Add a context processor in `api/index.py` to make routes available to templates:
   ```python
   @app.context_processor
   def inject_routes():
       from utils.url_registry import get_routes
       return {'get_routes': get_routes}
   ```

4. **Update Base Template**
   - Add route injection script to `templates/base.jinja` in the `<head>` section

5. **Create JavaScript Utility**
   - Create `static/js/route-client.js` with the `resolveRoute` function
   - Add appropriate JSDoc comments for developer usage

6. **Update Key JavaScript Files**
   - Modify one JavaScript file as a proof of concept (e.g., `static/js/sourcedirs.js`)
   - Test functionality to ensure routes are resolved correctly

7. **Documentation**
   - Document the approach in the codebase README
   - Add example usage to developer documentation

8. **Gradual Migration**
   - Identify files using hardcoded URLs with `GrepTool` 
   - Prioritize files with recent URL breakages for conversion
   - Convert files one at a time, testing after each change

## Potential Questions/Concerns

- **Naming Conventions**: Should route constants use `API_` prefix for API routes, or organize differently?
- **Default Parameters**: Should resolveRoute handle default parameters like current language_code?
- **Documentation**: How will these routes be documented for developers?
- **Performance**: Will the larger template size impact page load time?
- **Error Handling**: How should resolveRoute handle missing routes or parameters?