# [DRAFT] Investigation into Svelte CSS in Production Issues

## Current Issue

The Svelte components were broken in production because the CSS file could not be loaded:

1. The CSS filename includes a hash that changes with each build (e.g., `style-CSuD8m18.css`)
2. The template had a hardcoded fallback to an old CSS path (`style-DLIes3yS.css`)
3. When the manifest failed to load on production, it fell back to this hardcoded path
4. After deployment with a new CSS file but old fallback path, the CSS couldn't be found

## Root Cause Analysis

After examining the commit history, we identified that:

1. The build process generates CSS files with hash names like `style-CSuD8m18.css` in the `static/build/assets/` directory
2. The Vite manifest file (`.vite/manifest.json`) is being generated but might not be accessible in Vercel's environment
3. The manifest loading code only looks in one location and may not handle Vercel's directory structure properly
4. A fix was attempted in commit f527b68 that added a hardcoded fallback, but this breaks whenever the CSS is rebuilt

## Current Workaround

Our current temporary solution is:

1. Added a special route in Flask that serves any CSS file matching `style-*.css` from the build directory
2. Modified the template to use a consistent path (`/static/build/assets/style.css`) that doesn't depend on hash values
3. The custom route dynamically finds and serves the actual CSS file, regardless of its hash

This solution has several drawbacks:
- Bypasses Vite's asset hashing benefits for cache invalidation
- Adds performance overhead for each CSS request
- Only handles CSS files, not other assets with similar issues
- Not standard web practice

## Potential Better Solutions

We've identified several potential approaches that would be more robust:

### Option 1: Enhanced Manifest Loading

1. Modify the `load_vite_manifest()` function to:
   - Look in multiple possible locations for the manifest
   - Create a dynamic manifest as a fallback by scanning the build directory
   - Add more detailed logging for debugging

2. Update the build process to:
   - Copy the manifest to more accessible locations
   - Ensure build completes properly with the manifest intact

3. Update templates to:
   - Use the manifest-based approach without hardcoded fallbacks
   - Add better error reporting when CSS loading fails

### Option 2: Vercel Configuration Improvements

1. Investigate how Vercel handles hidden directories (like `.vite`)
2. Update Vercel config to ensure these directories are accessible
3. Add specific build steps in vercel.json to handle asset preparation

### Option 3: Simplified Asset Structure

1. Configure Vite to output assets with predictable names (no hashes)
2. Update templates to use these predictable paths directly
3. Use query string parameters for cache busting

## Next Steps

We should:

1. Consider implementing Option 1 as it provides the most robust solution while maintaining hashing benefits
2. Add better monitoring to detect CSS loading failures early
3. Run tests to verify the solution works in both development and production environments
4. Eventually investigate why Vercel's environment has issues accessing the `.vite` directory