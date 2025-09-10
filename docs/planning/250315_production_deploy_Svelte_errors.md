# Fixing Svelte Component Loading in Production

## Goal Statement
Identify and fix the root cause of Svelte component loading failures in the production environment (https://hz-app-web.fly.dev), while ensuring components continue to work correctly in the development environment.

## Current Status

### Issue Description
Svelte components are not loading in production, resulting in empty UI elements where components should appear. Browser console shows the following errors:

```
TypeError: Failed to fetch dynamically imported module: https://hz-app-web.fly.dev/static/build/js/miniwordform.js
```

Similar errors appear for all component files (minilemma.js, minisentence.js, miniphrase.js, etc.)

### Environment Details
- **Development Environment**: Components load correctly using Vite's dev server on localhost
- **Production Environment**: Deployed to Fly.io using Docker, components fail to load
- **Recent Changes**: Added new MiniPhrase component (commit 87b7a3b)

### Troubleshooting Findings

1. **URL Mismatch Issue**: 
   - In production mode, `base_svelte.jinja` was looking for JS files with `-entry.js` suffix
   - Actual built files have just `.js` suffix (e.g., `minilemma.js`)

2. **Build Output Problems**:
   - Vite build generates extremely small JS files (~70 bytes)
   - Files contain only version imports: `import"./index-IHki7fMi.js";`
   - No actual component code or mounting logic is included
   - This is true for all component files, suggesting a systematic build issue

3. **Static File Serving**:
   - Files appear to be built correctly locally
   - Deploy script includes the build step
   - Network requests to component JS files are failing in production

## Analysis

### Root Cause Hypotheses

1. **Build Configuration Issue**:
   - Vite may be incorrectly bundling Svelte components
   - Export structure in entry files may not match what's expected in production
   - Component code being tree-shaken out due to configuration

2. **Static Asset Serving Issue**:
   - Files may not be correctly included in the Docker image
   - Flask static file serving configuration may be incorrect
   - Permissions or path issues in the production environment

3. **Component Architecture Problem**:
   - Dynamic import approach may not be compatible with production setup
   - Entry point structure may need modification for production builds

### Crucial Observations

1. The `-entry.js` vs `.js` suffix discrepancy is a clear issue, but doesn't explain the empty file content.
2. The fact that built files contain almost no code is highly suspicious and likely a key part of the problem.
3. Even with the URL corrected, the files would still be unusable as they lack component code.

### Investigation Update (March 15, 2025)

After thorough investigation, we've identified the root causes and implemented a solution:

1. **URL Path Mismatch**: 
   - The `base_svelte.jinja` template was incorrectly looking for files with `-entry.js` suffix
   - Actual built files have just `.js` suffix (e.g., `minilemma.js`)
   - This was fixed by updating the import URL pattern

2. **Empty Component Files**:
   - After building, component files were only ~70 bytes
   - They contained only: `import"./index-IHki7fMi.js";`
   - No actual component code or factory functions were included
   - The issue was related to how Vite optimizes code in production mode
   - Standard build is designed for applications, not component libraries

3. **Solution: Library Mode with Component Registry**:
   - Implemented Vite's "library mode" designed specifically for component libraries
   - Created a central entry point (`frontend/src/entries/index.ts`) that:
     - Imports all Svelte components
     - Exports them individually for TypeScript support
     - Creates a registry of component factory functions 
   - Updated `base_svelte.jinja` to:
     - Load the single bundle file instead of individual component files
     - Look up the appropriate component factory by name
     - Add better error handling and debugging

4. **Results**:
   - Single bundle (47KB) containing all components vs. empty individual files
   - More reliable component loading in production
   - Better aligned with industry best practices for component libraries
   - Simplified network requests (one bundle vs. many small files)
   - Added requirement: new components must be registered in `index.ts`

## Implemented Solution

We implemented **Option 3: Bundle-Based Approach** with Vite's library mode, which proved to be the most effective solution:

1. **Library Mode Configuration**:
   ```javascript
   build: {
     lib: {
       entry: resolve(__dirname, 'src/entries/index.ts'),
       name: 'HzComponents',
       formats: ['es'],
       fileName: (format) => `js/hz-components.${format}.js`
     },
     rollupOptions: {
       external: ['svelte'],
       output: {
         globals: {
           svelte: 'Svelte'
         }
       }
     }
   }
   ```

2. **Component Registry Implementation**:
   ```typescript
   // Create a component registry with factory functions
   const components = {
     minilemma: (target: HTMLElement, props: any) => new MiniLemma({ target, props }),
     minisentence: (target: HTMLElement, props: any) => new MiniSentence({ target, props }),
     // ...other components
   };
   
   export default components;
   ```

3. **Updated Template for Component Loading**:
   ```javascript
   // Load the unified component bundle
   const bundleUrl = "{{ url_for('static', filename='build/js/hz-components.es.js') }}";
   
   // Dynamic import bundle
   import(bundleUrl).then(componentsModule => {
     // Get component factory from registry
     const componentName = '{{ component_name | lower }}';
     const componentFactory = componentsModule.default[componentName];
     
     // Mount component
     const component = componentFactory(targetElement, props);
   });
   ```

## Testing Plan

Before deploying, we should be able to verify the fix locally by:

1. Running the build process: `cd frontend && npm run build`
2. Examining build output in `static/build/js/` to ensure files contain component code
3. Setting up a local production-like environment:
   - Set `FLASK_ENV=production` or `IS_PRODUCTION=true`
   - Serve the app with `gunicorn` instead of development server
   - Validate component loading in this environment

## Implementation Steps

1. **Investigation & Verification**:
   - Inspect component entry files and build output more thoroughly
   - Test with a minimal example to isolate the issue
   - Verify that the issue is reproducible in a clean environment

2. **Fix Implementation**:
   - Implement the chosen solution (likely Option 1)
   - Add comprehensive comments explaining the changes
   - Ensure development mode continues to work

3. **Testing**:
   - Test in local production-like environment
   - Verify all components load correctly
   - Test with different browsers

4. **Deployment**:
   - Deploy to production
   - Monitor component loading
   - Document the solution for future reference

## Notes & Questions

- Why is Vite generating such small files with no component code?
- Is this a known issue with Svelte + Vite in production builds?
- Do we need to configure Vite differently for SSR/production environments?
- Are other projects using similar setups encountering similar issues?

This issue requires a fundamental fix rather than workarounds or fallbacks, as it affects all components in our architecture.