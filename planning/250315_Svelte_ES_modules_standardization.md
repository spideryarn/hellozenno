# Svelte ES Modules Standardization

## Goal, Context

Standardize all Svelte component loading to use ES modules instead of UMD, removing inconsistencies between components and ensuring a simpler, more maintainable approach. This follows up on our recent migration away from the UMD pattern (`31d2f6cfe8003454728c55e1c3cd79d5d2795ca7`) and fixes production issues that were encountered.

We had a mix of component loading approaches:
- Some components used ES modules
- Flashcard components used UMD with global variables

The recent commit standardized our build process to only output ES modules, but we discovered production issues with 404 errors for non-existent individual component files.

## Principles, Key Decisions

- **ES Modules Only**: Use only ES modules for all components, removing UMD completely
- **Bundled Output**: Create a single bundled ES module file (`hz-components.es.js`) containing all components
- **Consistent Loading**: All components should load via the same mechanism
- **No Global Variables**: Stop exposing components via global variables
- **Simplified Templates**: Remove redundant script loading in templates
- **KISS Principle**: Keep things as simple as possible while ensuring proper functionality

## Actions

- [x] **Identify Production Issues**
  - [x] Inspect production site with browser tools to identify 404 errors
  - [x] Confirm that components still work despite the 404 errors
  - [x] Understand the loading mechanism changes from UMD to ES modules

- [x] **Fix Template Loading**
  - [x] Remove code in `base.jinja` that tries to load individual component scripts in production
  - [x] Ensure components load correctly from the bundled ES module file
  - [x] Verify that flashcard components work properly with the ES module approach

- [x] **Test and Deploy**
  - [x] Build the frontend to verify changes
  - [x] Commit changes to the repository
  - [x] Deploy to production

- [ ] **Document the Approach**
  - [ ] Update relevant documentation to reflect the standardized ES module approach
  - [ ] Explain the benefits of the unified approach
  - [ ] Add troubleshooting guidance for future developers

- [ ] **Future Improvements**
  - [ ] Consider code splitting for larger bundles if the application grows significantly
  - [ ] Optimize bundle size through tree-shaking and dead code elimination
  - [ ] Add better error reporting for component loading failures

## Appendix

### Component Loading Mechanism

In production, the following script dynamically imports the ES module bundle:

```javascript
// Dynamic import bundle
import(bundleUrl).then(componentsModule => {
  // Get component factory from registry
  const componentName = 'flashcardapp';
  const componentFactory = componentsModule.default[componentName];
  
  // Mount component
  const component = componentFactory(targetElement, props);
});
```

The bundleUrl points to `/static/build/js/hz-components.es.js`, which contains all Svelte components.

### Bundle Structure

The ES module bundle exports:
- Individual named components (MiniLemma, FlashcardApp, etc.)
- A default export with a registry of component factories indexed by lowercase component names

This approach provides flexibility while maintaining a single source of truth for all components.