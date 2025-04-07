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
      url = `/language/${params.language_code}/wordforms`;
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

## Options Evaluated

### Option 1: Custom Typed Implementation

A simple enhancement to the current approach with proper TypeScript typing:

```typescript
// Define page params by type
type PageParams = {
  'languages': {};
  'wordforms': { language_code: string };
  'lemmas': { language_code: string };
  // ...other routes
};

export type PageType = keyof PageParams;

export function getPageUrl<T extends PageType>(
  page: T,
  params: PageParams[T],
  query?: Record<string, string>
): string {
  // Same implementation as before, but now params are type-checked
}
```

**Pros:**
- Simple enhancement to existing code
- Type-safe parameters
- No additional dependencies

**Cons:**
- Manual maintenance still required
- No auto-generation from file structure
- Not connected to actual routes in the filesystem

### Option 2: skRoutes

A dedicated library for SvelteKit route management:

```typescript
import { skRoutes } from 'skRoutes';
import { z } from 'zod';

export const { pageInfo, urlGenerator } = skRoutes({
  config: {
    '/[id]': {
      paramsValidation: z.object({ id: z.string() }).parse
    },
    // ...other routes
  },
  errorURL: '/error'
});

// Usage
const url = urlGenerator({ 
  address: '/[id]', 
  paramsValue: { id: 'Horse' } 
}).url;
```

**Pros:**
- Strong typing with Zod validation
- Error handling built-in
- Active maintenance
- Additional features like search params handling

**Cons:**
- Configuration-based, not auto-generated
- Manual route definition required
- More complex API

### Option 3: roullector

A route collector that generates from file structure:

```typescript
// Generated output example
import { AppRoutes, route } from '$generated/routing';

// Usage
const path = route(AppRoutes.admin.users.$id.posts.s$slug, 'user-id-123', 'slug');
// path = '/admin/users/user-id-123/posts/s-slug'
```

**Pros:**
- Auto-generates from file structure
- Simple API
- Minimal configuration

**Cons:**
- Less active maintenance
- No built-in validation
- Fewer features overall

### Option 4: vite-plugin-kit-routes (Recommended)

A Vite plugin that automatically generates route references from SvelteKit file structure:

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
<a href={route('/terms-and-conditions')}>Terms</a>

// With route parameters
<a href={route('/site/[id]', { id: 123 })}>Go to site</a>

// With query parameters
<a href={route('/site/[id]', { id: 123, limit: 3 })}>Go to site</a>
```

**Pros:**
- Zero configuration required
- Auto-generates from SvelteKit file structure
- Type-safe route parameters
- Simple API similar to our desired approach
- Part of the KitQL ecosystem (well-maintained)
- Support for both route and query parameters
- Tracks changes to route files automatically

**Cons:**
- Requires TypeScript (not a problem for us)

## Recommendation

We recommend implementing **vite-plugin-kit-routes** because:

1. It provides the most seamless auto-generation from SvelteKit file structure
2. It requires zero configuration to get started
3. The API is simple and intuitive
4. It handles both route parameters and query parameters in a type-safe way
5. It stays in sync with file changes automatically
6. It follows the same "single source of truth" principle we use for API routes

## Experimentation Strategy

Before fully committing to a new routing approach, we recommend a gradual implementation strategy:

### Recommended: Partial Implementation in Existing Project

1. Install the plugin but don't immediately update all route references:
   ```bash
   npm install -D vite-plugin-kit-routes
   ```

2. Add it to the Vite config file:
   ```javascript
   // vite.config.js
   import { sveltekit } from '@sveltejs/kit/vite'
   import { kitRoutes } from 'vite-plugin-kit-routes'

   export default {
     plugins: [
       sveltekit(),
       kitRoutes()
     ]
   }
   ```

3. Let the plugin generate the `$lib/ROUTES.ts` file when you start your dev server

4. Keep your existing `getPageUrl` function but start using the new `route` function in:
   - New components you create
   - A few existing components as a test
   - Areas undergoing active development

5. Evaluate the developer experience and any issues that arise

6. If the experience is positive, gradually migrate more components over time

This approach has several advantages:
- Minimizes risk by allowing both systems to coexist
- Provides real-world testing in your actual project
- Avoids a large refactoring effort upfront
- Allows developers to get comfortable with the new approach
- Makes it easy to revert if unexpected issues arise

### When Routes Change

When a route file is moved or renamed:
1. The plugin will automatically regenerate the `$lib/ROUTES.ts` file
2. TypeScript will show errors in components using the old route path
3. You'll need to update those references manually
4. This ensures all references are kept in sync with the actual file structure

## Implementation Plan

1. Install the plugin:
   ```bash
   npm install -D vite-plugin-kit-routes
   ```

2. Add to Vite config:
   ```javascript
   // vite.config.js
   import { sveltekit } from '@sveltejs/kit/vite'
   import { kitRoutes } from 'vite-plugin-kit-routes'

   export default {
     plugins: [
       sveltekit(),
       kitRoutes()
     ]
   }
   ```

3. Start the dev server, which will generate `$lib/ROUTES.ts`

4. Replace usages of `getPageUrl` with the new `route` function:
   ```typescript
   // Before
   const url = getPageUrl('wordforms', { language_code: 'el' });
   
   // After
   import { route } from '$lib/ROUTES';
   const url = route('/language/[language_code]/wordforms', { language_code: 'el' });
   ```

5. Update the URL Registry documentation to include information about both API routes and page routes

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
