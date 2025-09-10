# SvelteKit Typed URL Routing

## Current Approach

HelloZenno currently uses two separate approaches for URL management:

1. **API Routes**: Auto-generated from Flask route decorators into TypeScript definitions using `RouteParams` and `getApiUrl`
2. **Frontend Routes**: A manual switch-based implementation in `getPageUrl` that's not fully type-safe:

```typescript
export function getPageUrl(
  page: PageType,
  params: Record<string, string | undefined>,
  query?: Record<string, string>
): string {
  let url: string;
  
  // Build the appropriate URL based on the page type
  switch (page) {
    // Language pages
    case 'languages':
      url = '/languages';
      break;
    case 'wordforms':
      url = `/language/${params.target_language_code}/wordforms`;
      break;
    // ... other cases
  }
  
  // Add query string if provided
  if (query && Object.keys(query).length > 0) {
    const queryString = Object.entries(query)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&');
    url = `${url}?${queryString}`;
  }
  
  return url;
}
```

This approach has limitations:
- Not properly type-safe (no parameter validation at compile time)
- Manual maintenance required when routes change
- No direct connection to actual SvelteKit routes in the filesystem
- Potential for human error in URL construction

## Desired Outcome

We want a solution that:

1. Auto-generates route definitions from SvelteKit file structure
2. Provides type-safe parameter validation
3. Includes query parameter support
4. Requires minimal configuration
5. Follows "single source of truth" principle (similar to our API URL registry)

## Selected Solution: vite-plugin-kit-routes

After evaluating several options, we've selected **vite-plugin-kit-routes** as our solution:

```typescript
// vite.config.js
import { sveltekit } from '@sveltejs/kit/vite'
import { kitRoutes } from 'vite-plugin-kit-routes'

export default {
  plugins: [
    sveltekit(),
    kitRoutes()
  ]
}

// Usage in components
import { route } from '$lib/ROUTES'

// Simple route
<a href={route('/')}>Home</a>

// With route parameters
<a href={route('/language/[target_language_code]/wordforms', { target_language_code: 'el' })}>Greek Wordforms</a>

// With query parameters (third parameter)
<a href={route('/language/[target_language_code]/flashcards', { target_language_code: 'el' }, { sourcefile: 'myfile' })}>Flashcards</a>
```

**Key Advantages:**
- Zero configuration required
- Auto-generates from SvelteKit file structure
- Type-safe route parameters
- Simple API similar to our desired approach
- Part of the KitQL ecosystem (well-maintained)
- Support for both route and query parameters
- Tracks changes to route files automatically

## Implementation Experience

We've performed a partial implementation to evaluate the plugin's functionality:

### Installation and Setup

1. We installed the plugin in the frontend directory:
   ```bash
   cd frontend && npm install -D vite-plugin-kit-routes
   ```

2. We added it to the Vite config file (frontend/vite.config.ts):
   ```typescript
   import { sveltekit } from '@sveltejs/kit/vite';
   import { defineConfig } from 'vite';
   import { kitRoutes } from 'vite-plugin-kit-routes';

   export default defineConfig({
     plugins: [sveltekit(), kitRoutes()],
     // ... other config
   });
   ```

3. Starting the dev server generated a comprehensive `$lib/ROUTES.ts` file that includes:
   - All SvelteKit routes with typed parameters
   - Support for query parameters
   - Helper functions for route manipulation

### Test Implementation

We modified two components to test the functionality:

1. **Error Page Component**: 
   Updated `/language/[target_language_code]/+error.svelte` to use the new `route` function:

   ```svelte
   <script lang="ts">
     import { route } from '$lib/ROUTES';
     // ... other imports
   </script>

   <!-- Example of usage in links -->
   <a href={route('/')} class="btn btn-primary">Go to the homepage</a>
   <a href={route('/languages')} class="btn btn-secondary">View available languages</a>
   <a href={route('/language/[target_language_code]/sources', { target_language_code: page.params.target_language_code })} class="btn btn-info">
     Back to language page
   </a>
   ```

2. **SourcefileHeader Component**:
   Updated complex navigation links in `SourcefileHeader.svelte`:

   ```typescript
   // Generate navigation URLs using the new route function
   $: sourcedirUrl = route('/language/[target_language_code]/source/[sourcedir_slug]', {
     target_language_code,
     sourcedir_slug
   });
   
   // With query parameters (third parameter)
   $: flashcardsUrl = route('/language/[target_language_code]/flashcards', {
     target_language_code
   }, { sourcefile: sourcefile_slug });
   ```

### Observations

1. **Type Safety**: The plugin provides excellent type checking for route parameters.
2. **Developer Experience**: Excellent autocomplete support in the IDE.
3. **Generated Code Quality**: The generated ROUTES.ts file is well-structured and includes helpful documentation.
4. **Coexistence**: Both the old `getPageUrl` and new `route` functions can coexist during migration.
5. **Performance**: No noticeable impact on build or runtime performance.
6. **Query Parameters**: Well-supported with type checking.

### Minor Issues Encountered

1. There was a TypeScript error with the query parameter overload in our `SourcefileHeader.svelte` component that needs investigation:
   ```
   Expected 2 arguments, but got 3.
   ```

2. Some linting errors in the error page related to unrelated properties (`page.error.stack`).

## Implementation Plan for Full Adoption

Based on our successful test, here's our plan for full implementation:

1. **Gradual Migration**:
   - Keep the existing `getPageUrl` function during transition
   - Update components during normal development work
   - Focus on heavily modified areas first

2. **Documentation**:
   - Update internal documentation on URL handling
   - Create usage examples for developers

3. **Helper Functions**:
   - Consider creating bridge functions to ease transition
   - Add custom utility functions if needed for special cases

4. **Testing**:
   - Add specific tests for route generation
   - Ensure all routes work correctly with parameters

## Next Steps

1. **Resolve Query Parameter Type Issue**:
   - Investigate and fix TypeScript error with the third parameter in `route` function

2. **File Naming Disambiguation**:
   - Disambiguate file naming between frontend-generated `ROUTES.ts` and backend-generated `routes.ts`
   - Options include:
     - Rename backend-generated file to something like `API_ROUTES.ts` or `BACKEND_ROUTES.ts`
     - Configure vite-plugin-kit-routes to use a different output filename if possible
   - See `URL_REGISTRY.md` for context on the backend route generation

3. **Migration Strategy**:
   - Identify high-priority components for migration
   - Create a timeline for gradual adoption
   - Consider a utility function to bridge `getPageUrl` and `route` during transition

4. **Update Documentation**:
   - Complete integration with existing documentation
   - Create examples for common use cases

5. **Template Creation**:
   - Create standard templates for new components with the new routing pattern

## Benefits

1. **Type Safety**: Full TypeScript validation for route parameters
2. **Single Source of Truth**: Routes are derived directly from the file structure
3. **Developer Experience**: Autocomplete and validation for routes and parameters
4. **Maintenance**: No need to manually update route definitions
5. **Consistency**: Similar pattern to our API URL registry approach

## References

- [vite-plugin-kit-routes Documentation](https://www.kitql.dev/docs/tools/06_vite-plugin-kit-routes)
- [KitQL Ecosystem](https://www.kitql.dev/)
- [SvelteKit Routing Documentation](https://svelte.dev/docs/kit/routing)
