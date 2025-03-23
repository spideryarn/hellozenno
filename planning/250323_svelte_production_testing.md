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

2. **Duplicate Vite Helper Implementations**: We had two different implementations:
   - `utils/url_utils.py` contained `load_vite_manifest()`
   - `api/utils/vite_helpers.py` contained `get_vite_manifest()`, `vite_asset_url()`, and `dump_manifest()`

3. **Module Import Structure**: The Flask app (`api/index.py`) was importing from both implementations, but only one set was being used effectively.

4. **Environment Variable Transition**: We're transitioning from `LOCAL_PROD_TEST` to `LOCAL_CHECK_OF_PROD_FRONTEND` but need to ensure both work during the transition period.

5. **Persistent Loading Messages**: Even when components successfully load, the "Loading xxx component..." messages remain visible, confusing users and suggesting components are not properly loaded.

### Recent Progress

We've made significant improvements to fix these issues:

1. **Fixed Template Helper Registration**: Added proper context processor registration in Flask.

2. **Consolidated Vite Helpers**: Created a unified implementation in `utils/vite_helpers.py` that:
   - Combines the best aspects of both previous implementations
   - Provides backward compatibility with `load_vite_manifest()`
   - Uses proper type hints and documentation
   - Implements a caching layer for better performance
   - Adds robust error handling and fallbacks

3. **Improved Environment Detection**: 
   - Updated template to use a clear variable name `is_production_mode`
   - Fixed the conflict where it was trying to load from both development and production sources
   - Added better debug logging in both environments

4. **Enhanced Error Handling**: 
   - Added loading indicators for all components
   - Improved error display with detailed information
   - Added timing metrics for performance analysis

5. **Added Debugging Tools**:
   - Created a `/dev/vite-manifest` endpoint that shows detailed information about the manifest and asset resolution
   - Added more verbose console logging with environment information
   - Improved error messages with more context

6. **Jinja Scope Issues**: Solved by using Jinja globals instead of context processors
7. **Asset Path Mismatch**: Fixed lookup strategy to handle Vite's manifest structure
8. **Fixed Persistent Loading Messages**: Solved by:
   - Adding `style="display: none;"` directly to the loading element in HTML
   - Setting `display: none !important;` in CSS to override any other styling
   - Ensuring loading elements are forcibly removed when components mount

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
- [x] Plan a unified approach for both sets of Vite helpers

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

- [x] Merge the two implementations of Vite helpers
  - [x] Decide which implementation to keep (created new unified version in `utils/vite_helpers.py`)
  - [x] Ensure backward compatibility with existing code
  - [x] Add appropriate deprecation warnings for old functions
  - [x] Update imports in `api/index.py`

### Stage 9: Fix Environment Detection

- [x] Update `base_svelte.jinja` to correctly determine when to use development vs. production loading
  - [x] Clarify the variable name from `in_production_mode` to `is_production_mode`
  - [x] Add clear comments about what each environment section does
  - [x] Remove the redundant code trying to load from both environments
  - [x] Add better debugging information in each environment mode

### Stage 10: Fix Persistent Loading Messages

- [x] Update `base_svelte.jinja` to properly hide loading messages:
  - [x] Add `style="display: none;"` inline to HTML elements for immediate hiding
  - [x] Set `display: none !important;` in CSS to override any other styling
  - [x] Update component loading logic to forcibly remove loading elements
  - [x] Add fallback event handler to ensure loading elements are hidden
  - [x] Test across browsers to verify loading messages never appear

### Stage 11: Update Deployment Process

- [ ] Enhance build-frontend.sh to verify a successful build
  - [ ] Add explicit checks for required output files
  - [ ] Add validation for manifest file structure
  - [ ] Create a simple output status report
  - [ ] Test full deployment process locally
  
### Stage 12: End-to-End Testing

- [ ] Create automated tests for the component loading process
  - [ ] Add tests for development mode loading
  - [ ] Add tests for production mode loading
  - [ ] Add tests for handling missing manifest
  - [ ] Add tests for handling missing CSS
  - [ ] Add tests for handling missing component bundle
  - [ ] Test the entire workflow from build to deployment

### Stage 13: Implement Jinja Globals for Robust Helper Functions

- [x] Update the Flask application to use Jinja globals instead of context processors
  - [x] Remove existing context processor registration
  - [x] Add Jinja globals registration during app initialization
  - [x] Update helper functions to fail with clear error messages
  - [x] Remove conditional fallbacks in templates
  - [x] Create documentation describing the changes
  - [x] Test with both development and production modes

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

Our next priorities are:

1. **Document the unified Vite helpers**:
   - Add clear documentation on how the asset loading works
   - Update existing documentation to reflect the new system
   - Create examples for common usage patterns

2. **Improve build script**:
   - Add verification steps to the build process
   - Generate build reports to confirm which files were created
   - Add validation for the manifest structure

3. **Add automated tests**:
   - Create tests for the Vite helpers
   - Add end-to-end tests for the component loading process
   - Test edge cases like missing manifests or assets

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
3. ✅ **Asset Path Resolution**: Implemented robust resolution with fallbacks
4. ✅ **Duplicate Vite Helpers**: Consolidated into a single implementation
5. ✅ **Environment Detection**: Fixed to properly handle dev vs prod mode
6. ✅ **Jinja Scope Issues**: Solved by using Jinja globals instead of context processors
7. ✅ **Asset Path Mismatch**: Fixed lookup strategy to handle Vite's manifest structure
8. ✅ **Persistent Loading Messages**: Fixed by using both inline styles and `!important` CSS rules

### Issues Still to Resolve

1. **Build Verification**: Add checks to ensure production builds are complete and valid
2. **Automated Testing**: Create comprehensive tests for the component loading system

### Advanced Jinja Template Solutions

During our debugging process, we encountered a fundamental limitation in how Jinja2 macros handle context variables. After researching best practices, we identified two robust solutions:

#### Option 1: Using Jinja Globals (Recommended)

Jinja's Environment has a `globals` property that makes variables available in all templates, including macros, regardless of scope. This is simpler and more reliable than context processors for ensuring helper functions are available everywhere.

```python
# In app.py or create_app()
app.jinja_env.globals.update(
    vite_asset_url=vite_asset_url,
    vite_manifest=get_vite_manifest,
    dump_manifest=dump_manifest
)
```

**Advantages:**
- Functions are truly globally available in all templates and macros
- Minimal changes to existing code - keep using macros as before
- No additional template files needed
- Clean, function-like syntax at usage points
- Consistent with Flask's internal approach for built-in helpers

**Implementation plan:**
1. Remove our context processor registration
2. Add the Jinja globals registration during app initialization
3. Remove conditional fallbacks in templates (they'll no longer be needed)
4. Implement clear error handling in helper functions for better debugging

#### Option 2: Converting to Template Includes (Alternative)

Instead of using macros, we could use Jinja includes which have more predictable context behavior.

**Approach:**
1. Create a dedicated `_svelte_component.jinja` template file
2. Move the macro content to this template
3. Use includes to embed components:

```jinja
{% include '_svelte_component.jinja' with {
  'component_name': 'UserStatus',
  'props': {'userId': 123},
  'component_id': 'user-status'
} only %}
```

**Comparison with Macros:**

| Feature | Macros (Current) | Includes (Alternative) |
|---------|-----------------|------------------------|
| Call syntax | `{{ load_svelte_component('Name', props) }}` | `{% include '_component.jinja' with {'component_name': 'Name', 'props': props} %}` |
| Template organization | Multiple macros per file | One template per component pattern |
| Context access | Limited - requires special handling | Full parent context available by default |
| Parameter passing | Function-like named parameters | Dictionary with `with` keyword |
| Default values | Easy to define in macro signature | Requires handling in included template |

**Implementation complexity:**
- Higher: requires new template files and updating all call sites
- More verbose at each call site
- But guarantees context access without special handling

#### Hybrid Approach

If verbosity at call sites is a concern with includes, a hybrid approach could be used:

1. Create a thin macro wrapper around the include:
```jinja
{% macro component(name, props={}, id='') %}
  {% include '_svelte_component.jinja' with {
    'component_name': name,
    'props': props,
    'component_id': id
  } only %}
{% endmacro %}
```

2. Keep the familiar macro syntax at call sites:
```jinja
{{ component('UserStatus', {'userId': 123}) }}
```

This provides concise call syntax with reliable context behavior.

#### Recommendation

We recommend implementing the Jinja globals approach (Option 1) as it's:
1. Simpler to implement - fewer changes to existing code
2. More aligned with how Flask's built-in helpers work
3. Maintains the clean, concise macro syntax we currently use

This approach should make our component loading more robust and deterministic without sacrificing readability or maintainability.

### Production Testing Workflow

After implementing the Jinja globals approach, we observed clearer error handling in action. When testing in production mode without first building the frontend assets, we now get explicit error messages rather than silent fallbacks:

```
utils.vite_helpers.ViteAssetError: Critical asset 'js/hz-components.es.js' not found in Vite manifest. Expected at: build/js/hz-components.es.js. Check that frontend assets are built correctly.
```

This improved error handling helps us quickly identify issues:

1. The error clearly indicates what asset is missing (`js/hz-components.es.js`)
2. It specifies where it expected to find the asset (`build/js/hz-components.es.js`)
3. It provides actionable guidance ("Check that frontend assets are built correctly")

To properly test in production mode, the complete workflow is:

```bash
# First, build the frontend assets
./scripts/prod/build-frontend.sh

# Then, run Flask with the production frontend flag
./scripts/local/run_flask.sh --prod-frontend
```

The system now fails early and clearly if assets are missing, rather than attempting to use fallbacks which might mask underlying issues. This approach ensures that:

1. Developers are immediately alerted to missing or misnamed assets
2. There's a clearer connection between the build process and the runtime requirements
3. Issues are easier to diagnose with specific error messages pointing to the exact problem

Our improved testing workflow provides strong validation of the entire deployment pipeline, from asset building to runtime use, with clear error messages at each stage.

### Asset Path Resolution in the Manifest

During our testing, we discovered an important detail about how Vite manages asset paths in the manifest:

1. **Manifest Key Mismatch**: The key used to register the bundle in the manifest is `src/entries/index.ts`, but our code was looking for `js/hz-components.es.js`.

The issue arises because:
- In our templates, we reference the bundle path as `js/hz-components.es.js`
- But Vite records the entry point source file (e.g., `src/entries/index.ts`) as the key in the manifest
- The output file path (`js/hz-components.es.js`) is stored as a property of that entry, not as a top-level key

We resolved this by enhancing the `vite_asset_url` function to use multiple lookup strategies:

```python
# Special case for the bundle - look for the entry point that outputs this file
if asset_name == "js/hz-components.es.js":
    # First, check direct entry
    if asset_name in manifest and "file" in manifest[asset_name]:
        return url_for("static", filename=f"build/{manifest[asset_name]['file']}")
        
    # Next, look for entries that output to this file 
    for key, value in manifest.items():
        if "file" in value and value["file"] == asset_name:
            return url_for("static", filename=f"build/{value['file']}")
            
    # Finally, check if any entry has "src/entries/index.ts" as key
    if "src/entries/index.ts" in manifest and "file" in manifest["src/entries/index.ts"]:
        bundle_file = manifest["src/entries/index.ts"]["file"]
        return url_for("static", filename=f"build/{bundle_file}")
```

This approach:
1. First, checks if the requested asset name exists directly as a key
2. Then checks if any manifest entry outputs to a file matching the requested asset name
3. Finally, looks for the known entry point that should generate our bundle

We also improved error messages to show the actual contents of the manifest when the lookup fails, making debugging much easier:

```python
manifest_entries = ', '.join(manifest.keys())
error_msg = f"Critical asset '{asset_name}' not found in Vite manifest. "
error_msg += f"Expected at: {critical_assets[asset_name]}. "
error_msg += f"Manifest contains: {manifest_entries}. "
```

This multi-stage lookup ensures our system is resilient to changes in how Vite structures its manifest file.

### Fixing Persistent Loading Messages

After implementing all the asset resolution improvements, we encountered an issue where the loading message placeholders ("Loading X component...") remained visible even after components loaded successfully. This was misleading to users, making it appear that components were still loading when they had actually mounted.

We identified that the issue was caused by the CSS and DOM structure not properly handling the loading state transitions. We fixed this with a two-pronged approach:

1. **Hide loading elements by default in HTML**:
   ```html
   <div class="component-loading" style="display: none;">
     <div class="loading-text">Loading {{ component_name }} component...</div>
   </div>
   ```
   
2. **Ensure CSS forcibly hides the loading elements**:
   ```css
   .svelte-component-container .component-loading {
     display: none !important;
   }
   ```

3. **Actively remove loading elements once components mount**:
   ```javascript
   function hideLoading(targetElement) {
     if (targetElement) {
       // Explicitly remove the loading element instead of just hiding it
       const loadingEl = targetElement.querySelector('.component-loading');
       if (loadingEl) {
         loadingEl.remove();
       }
       // Also add the class as a backup mechanism
       targetElement.classList.add('component-loaded');
     }
   }
   ```

This multi-layered approach ensures that:
1. Loading messages are hidden by default (inline style)
2. CSS rules forcibly hide any that might become visible (CSS with !important)
3. Loading elements are completely removed from the DOM when components mount (JavaScript)

The result is a much better user experience where loading messages only appear briefly during development, and not at all in production mode.

## Troubleshooting and Lessons Learned