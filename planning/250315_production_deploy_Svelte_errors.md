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

After initial investigation, we've confirmed several aspects of the issue:

1. **URL Path Mismatch**: 
   - The `base_svelte.jinja` template was incorrectly looking for files with `-entry.js` suffix
   - Actual built files have just `.js` suffix (e.g., `minilemma.js`)
   - This has been fixed by updating the import URL pattern

2. **Empty Component Files**:
   - After building, component files are only ~70 bytes
   - They contain only: `import"./index-IHki7fMi.js";`
   - No actual component code or factory functions are included
   - This persists even with adjusted build configurations

3. **Further Investigation Needed**:
   - Need to understand why Vite is generating minimal files
   - Research best practices for Svelte + Vite component libraries
   - Explore alternative bundling strategies

## Proposed Solutions

### Option 1: Fix Vite Build Configuration
1. Modify Vite configuration to preserve component code:
   ```javascript
   build: {
     rollupOptions: {
       output: {
         format: 'es',
         preserveModules: true,
         exports: 'named'
       }
     }
   }
   ```
2. Correct the file path in `base_svelte.jinja` to use `.js` instead of `-entry.js`
3. Add explicit component exports to ensure they survive tree-shaking

### Option 2: Custom Build Plugin
1. Create a Vite plugin that post-processes build output
2. Replace component files with complete, standalone implementations
3. Ensure each file has the necessary code to create and mount components

### Option 3: Bundle-Based Approach
1. Change architecture to use a single bundle for all components
2. Register components globally and access them by name
3. Eliminate individual dynamic imports in favor of a unified approach

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