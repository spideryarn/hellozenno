# Improving Svelte Components Deployment Process

## Goal, Context

Create a more robust process for testing Svelte components in production-like environments before actual deployment. Currently, Svelte components work fine in local development but often break in production due to differences in asset loading and component mounting.

The key issues are:
1. Asset path resolution not correctly handling hashed filenames
2. Lack of local testing for production builds
3. Difficulty debugging production issues
4. Inconsistent handling of the Vite manifest

We need to:
- Update our local development process to enable production-like testing
- Rename environment variables to be more explicit
- Create a step-by-step verification process for component loading
- Modify our scripts to better support this workflow

## Principles, Key Decisions

- **Break changes into small stages** - Test every piece in isolation before combining
- **Explicit environment variables** - Rename `LOCAL_PROD_TEST` to `LOCAL_CHECK_OF_PROD_FRONTEND` for clarity
- **Clear visual feedback** - Add visual indicators for component loading state and errors
- **Configuration over convention** - Use explicit configuration parameters rather than implicit defaults
- **Gradual progression** - Start with hard-coded values, test thoroughly, then make more general
- **Reuse existing scripts** - Extend `run_flask.sh` rather than creating new scripts when possible

## Current Status and Findings

We've identified several issues in our implementation:

1. **Template Helper Functions Not Registered**: The `vite_manifest` and `vite_asset_url` functions weren't being properly registered with Flask's context processor, causing "undefined" errors in templates.

2. **Duplicate Vite Helper Implementations**: We have two different implementations:
   - `utils/url_utils.py` contains `load_vite_manifest()`
   - `api/utils/vite_helpers.py` contains `get_vite_manifest()`, `vite_asset_url()`, and `dump_manifest()`

3. **Module Import Structure**: The Flask app (`api/index.py`) is importing from both implementations, but only one set is being used effectively.

4. **Environment Variable Transition**: We're transitioning from `LOCAL_PROD_TEST` to `LOCAL_CHECK_OF_PROD_FRONTEND` but need to ensure both work during the transition period.

### Recent Progress

We've implemented a successful temporary fix by:

1. **Hardcoding asset paths**: Replaced dynamic asset URL resolution with hardcoded paths in `base_svelte.jinja`:
   ```jinja
   <!-- CSS -->
   <link rel="stylesheet" href="{{ url_for('static', filename='build/assets/style.css') }}">
   
   <!-- JS -->
   const bundleUrl = "{{ url_for('static', filename='build/js/hz-components.es.js') }}";
   ```

2. **Commenting out problematic template code**: Disabled the `vite_manifest()` call in debug output which was causing template rendering errors.

3. **Testing the fix**: Successfully tested the flashcards page with our changes. The console logs confirm both components are mounting correctly:
   ```
   [SVELTE PROD] Component userstatus mounted successfully in 657.00ms
   [SVELTE PROD] Component flashcardlanding mounted successfully in 657.00ms
   ```

## Actions

### Stage 1: Update Flask Script to Support Production Testing Mode

- [x] Update `run_flask.sh` to accept command-line parameter for production testing
  - [x] Add parameter parsing for `--prod-frontend` flag
  - [x] Use the flag to set environment variable for production mode
  - [x] Update the help text to explain the new option
  - [x] Test that script can run in both modes

### Stage 2: Rename Environment Variables for Clarity

- [x] Replace `LOCAL_PROD_TEST` with `LOCAL_CHECK_OF_PROD_FRONTEND`
  - [x] Update `api/index.py` to use the new variable name
  - [x] Update `templates/base_svelte.jinja` to use the new variable name
  - [x] Remove `scripts/local/test_prod.sh` as it's now redundant with `run_flask.sh --prod-frontend`
  - [x] Test that all components still work with the new variable name

### Stage 3: Fix Vite Helper Registration

- [x] Identify the issue with vite helper function registration
- [x] Add direct context processor registration in `api/index.py`
- [x] Create a temporary workaround using hardcoded paths
- [x] Test that components load correctly with the temporary fix
- [ ] Plan a unified approach for both sets of Vite helpers

### Stage 4: Implement Step-by-Step Verification for Component Loading

- [x] Update `base_svelte.jinja` to add explicit debugging and verification
  - [x] Add a "component loading..." initial state to components
  - [x] Add timing metrics for component loading phases
  - [x] Create debug log for each loading step (manifest, CSS, component bundle, mount)
  - [x] Update error display to show more detailed information
  - [x] Test with both development and production modes

### Stage 5: Create Better Vite Manifest Handling

- [x] Update the manifest loading process with more robust verification
  - [x] Add explicit checks that manifest is loaded in production mode
  - [x] Create a fallback mechanism for when manifest isn't available
  - [x] Add detailed logging about what assets are being loaded
  - [x] Add a simple test page that shows all loaded assets from manifest
  - [x] Test with and without manifest file

### Stage 6: Hardcode Known Working Paths First for CSS Loading

- [x] Create hardcoded paths for known assets as a test
  - [x] Add hardcoded CSS path as a fallback
  - [x] Add hardcoded JS bundle path as a fallback
  - [x] Add console log showing which paths are being used (dynamic vs fallback)
  - [x] Test that components load with hardcoded paths even if manifest fails

### Stage 7: Make Manifest Loading More Robust

- [x] Create a more robust multi-stage manifest loading system
  - [x] Update `vite_helpers.py` to try multiple manifest locations
  - [x] Add validation that manifest actually contains expected keys
  - [x] Create a simple test endpoint that shows manifest content
  - [x] Add a cache to avoid repeated file system access
  - [x] Test that manifest loading works correctly in all environments

### Stage 8: Consolidate Vite Helpers

- [ ] Merge the two implementations of Vite helpers
  - [ ] Decide which implementation to keep (likely `api/utils/vite_helpers.py`)
  - [ ] Ensure backward compatibility with existing code
  - [ ] Add appropriate deprecation warnings for old functions
  - [ ] Update imports in all files

### Stage 9: Update Deployment Process

- [ ] Enhance build-frontend.sh to verify a successful build
  - [ ] Add explicit checks for required output files
  - [ ] Add validation for manifest file structure
  - [ ] Create a simple output status report
  - [ ] Test full deployment process locally
  
### Stage 10: End-to-End Testing

- [ ] Create automated tests for the component loading process
  - [ ] Add tests for development mode loading
  - [ ] Add tests for production mode loading
  - [ ] Add tests for handling missing manifest
  - [ ] Add tests for handling missing CSS
  - [ ] Add tests for handling missing component bundle
  - [ ] Test the entire workflow from build to deployment

## Process for Testing Production Builds Locally

The process for testing production builds locally is now simpler:

1. Build the frontend assets:
   ```bash
   ./scripts/prod/build-frontend.sh
   ```

2. Run Flask with the production frontend flag:
   ```bash
   ./scripts/local/run_flask.sh --prod-frontend
   ```

This gives more flexibility to:
- Build once, test multiple times
- Skip the build step if you've already built the assets
- Separate the concerns of building and running

## Next Steps

Now that we have a working temporary solution, the next steps are:

1. **Create a permanent solution for Vite helpers**:
   - Consolidate the two implementations into a single, more robust module
   - Update all templates to use the new helpers
   - Add proper error handling for edge cases

2. **Fix the environment detection**:
   - Update `base_svelte.jinja` to correctly determine when to use development vs. production loading
   - Fix the conflict where it's trying to load assets from both sources simultaneously

3. **Document the architecture**:
   - Create clear documentation on how component loading works in different environments
   - Add comments to explain the key parts of the system
   - Update existing documentation to reflect the new process

4. **Improve build script**:
   - Add verification steps to the build process
   - Generate build reports to confirm which files were created
   - Add validation for the manifest structure

## Appendix

### Current Paths in Production vs Local

**Local Development:**
- Components loaded from: `http://localhost:5173/src/entries/componentname.ts`
- Styles handled by Vite dev server
- HMR updates components automatically

**Production:**
- CSS loaded from: `/static/build/assets/style.css` (or hashed variant)
- JS bundles loaded from: `/static/build/js/hz-components.es.js`
- Components initialized from the bundle

### Issues Resolved

1. ✅ **Template Helper Registration**: Fixed by adding direct context processor registration
2. ✅ **Component Loading Display**: Added loading indicators and error handling
3. ✅ **Asset Path Resolution**: Temporarily fixed with hardcoded paths

### Issues Still to Resolve

1. **Duplicate Vite Helper Implementations**: Need to consolidate into a single solution
2. **Mixed Development/Production Mode**: Fix conflict where it's trying to load from both environments
3. **Build Verification**: Add checks to ensure production builds are complete and valid 